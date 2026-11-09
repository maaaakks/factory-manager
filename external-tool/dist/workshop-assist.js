'use strict';
(function(root){
 const M=typeof module!=='undefined'&&module.exports?require('./workshop-model.js'):root.WorkshopModel;
 function shapeAllows(project,x,y){return project.generation?.shape!=='exotic'||x<Math.ceil(M.extent(project)/16)*8||y>=Math.ceil(M.depth(project)/16)*8;}
 function shapeBox(project,o){const b=M.bounds(o);if(o.recipe&&(project.reserved||[]).some(r=>b.minX<r[0][1]&&b.maxX>r[0][0]&&b.minY<r[1][1]&&b.maxY>r[1][0]))return false;return [[b.minX,b.minY],[b.maxX-.001,b.minY],[b.maxX-.001,b.maxY-.001],[b.minX,b.maxY-.001]].every(([x,y])=>shapeAllows(project,x,y));}
 function port(o,output){const a=o.rotation*Math.PI/180,dy=(output?-1:1)*o.d/2;return {x:o.x-Math.sin(a)*dy,y:o.y+Math.cos(a)*dy,z:o.z||0};}
 // Schematic routing on a one-metre grid, avoiding envelopes on this floor.
 function route(project,from,to,waypoints=undefined){waypoints=waypoints??project.links?.find(l=>l.kind==='belt'&&l.from===from&&l.to===to)?.waypoints??[];const a=project.objects.find(o=>o.id===from),b=project.objects.find(o=>o.id===to);if(!a||!b||a===b||a.type==='pole'||b.type==='pole')return null;if((a.z||0)!==(b.z||0)){
  const link=project.links?.find(l=>l.kind==='belt'&&l.from===from&&l.to===to),shaft=link?.via&&project.objects.find(o=>o.id===link.via&&o.type==='lift');if(!shaft)return null;
  const head=z=>({...shaft,type:'port',z,h:1,w:1.5,d:1.5}),temp=z=>({...project,objects:project.objects.filter(o=>o.id!==shaft.id).concat(head(z)),links:[]});
  const lower=route(temp(a.z),from,shaft.id,[]),upper=route(temp(b.z),shaft.id,to,[]);if(!lower||!upper)return null;
  return [...lower.map(p=>({...p,z:a.z})),{x:shaft.x,y:shaft.y,z:a.z},{x:shaft.x,y:shaft.y,z:b.z},...upper.map(p=>({...p,z:b.z}))];
 }
  const start=port(a,true),end=port(b,false),key=(x,y)=>x+','+y;
  const outside=(o,p,out)=>{const angle=o.rotation*Math.PI/180,sign=out?-1:1;return {x:Math.round(p.x-Math.sin(angle)*sign*(project.generation?.routed?1:1.5)),y:Math.round(p.y+Math.cos(angle)*sign*(project.generation?.routed?1:1.5))};};
  const s=outside(a,start,true),e=outside(b,end,false),blocked=(x,y)=>!shapeAllows(project,x,y)||x<((project.generation?.priority==='architecture'||project.generation?.routingMargin)?4:0)||y<((project.generation?.priority==='architecture'||project.generation?.routingMargin)?4:0)||x>M.extent(project)-((project.generation?.priority==='architecture'||project.generation?.routingMargin)?4:0)||y>M.depth(project)-((project.generation?.priority==='architecture'||project.generation?.routingMargin)?4:0)||project.objects.some(o=>{if(!M.vertical(a,o))return false;const r=M.bounds(o);return x>r.minX-.3&&x<r.maxX+.3&&y>r.minY-.3&&y<r.maxY+.3;});
  if(blocked(s.x,s.y)||blocked(e.x,e.y))return null;
  if(!Array.isArray(waypoints)||waypoints.length>32)return null;
  const stops=[s,...waypoints.map(q=>({x:Math.round(q.x),y:Math.round(q.y)})),e],points=[];
  if(stops.some(p=>blocked(p.x,p.y)))return null;
  for(let leg=1;leg<stops.length;leg++){
   const start=stops[leg-1],end=stops[leg],queue=[start],previous=new Map([[key(start.x,start.y),null]]);let found=false;
   for(let i=0;i<queue.length;i++){const p=queue[i];if(p.x===end.x&&p.y===end.y){found=true;break;}for(const [dx,dy]of [[0,1],[1,0],[0,-1],[-1,0]]){const n={x:p.x+dx,y:p.y+dy},k=key(n.x,n.y);if(!previous.has(k)&&!blocked(n.x,n.y)){previous.set(k,p);queue.push(n);}}}
   if(!found)return null;const part=[];for(let p=end;p;p=previous.get(key(p.x,p.y)))part.push(p);part.reverse();points.push(...(leg>1?part.slice(1):part));
  }
  return [start,...points,end];
 }
 function parseCalculator(text){if(text.length>100000)throw new Error('Import trop volumineux.');let raw=text.trim();if(/^https?:/i.test(raw)){const u=new URL(raw);if(u.hostname!=='satisfactory-calculator.com')throw new Error('Lien Satisfactory Calculator attendu.');const marker='/index/json/',i=u.pathname.indexOf(marker);if(i<0)throw new Error('Copiez un lien de partage contenant /index/json/.');raw=decodeURIComponent(u.pathname.slice(i+marker.length));}const p=JSON.parse(raw);if(!p||typeof p!=='object'||Array.isArray(p))throw new Error('Objectifs JSON invalides.');
  if(Array.isArray(p.altRecipes)&&p.altRecipes.length===0)delete p.altRecipes;const allowed=new Set(['input','view','maxBeltSpeed','maxPipeSpeed','oreExtraction','powerShards']);for(const k of Object.keys(p))if(!/^Desc_[A-Za-z0-9_]+_C$/.test(k)&&!allowed.has(k))throw new Error('Option non prise en charge : '+k+'. Utilisez des recettes standard.');
  function rows(data){if(!data||typeof data!=='object'||Array.isArray(data))throw new Error('Débits invalides');return Object.entries(data).map(([id,v])=>{const rate=Number(v);if(!/^Desc_[A-Za-z0-9_]+_C$/.test(id)||!Number.isFinite(rate)||rate<=0||rate>100000)throw new Error('Débit invalide : '+id);return {id,rate};});}
  return {inputs:rows(p.input||{}),outputs:rows(Object.fromEntries(Object.entries(p).filter(([k])=>k.startsWith('Desc_'))))};
 }
 function demand(flows,data){
  const available=new Set(flows.inputs.map(r=>r.id)),requirements=new Map(),work=new Map(),catalog=data.productionRecipes?{...data.productionRecipes,...data.recipes}:data.recipes,defaults=data.productionDefaults||data.defaultRecipes,byOutput=defaults?new Map(Object.entries(defaults).map(([item,id])=>[item,catalog[id]])):new Map(Object.values(catalog).map(r=>[r.outputs[0].id,r]));
  function need(id,rate,trail=[]){if(!data.names[id])throw new Error('Ressource non prise en charge : '+id);if(available.has(id)||!byOutput.has(id)){requirements.set(id,(requirements.get(id)||0)+rate);return;}if(trail.includes(id))throw new Error('Cycle de recettes : '+[...trail,id].map(i=>data.names[i]).join(' → '));const r=byOutput.get(id),output=r.outputs.find(i=>i.id===id),cycles=rate/output.amount;work.set(id,(work.get(id)||0)+cycles);for(const item of r.inputs)need(item.id,item.amount*cycles,[...trail,id]);}
  if(!flows.outputs.length)throw new Error('Ajoutez une sortie cible.');for(const r of flows.outputs)need(r.id,r.rate);
  const balance=new Map(requirements);for(const [item,cycles]of work){const r=byOutput.get(item);for(const i of r.inputs)balance.set(i.id,(balance.get(i.id)||0)-i.amount*cycles);for(const o of r.outputs)balance.set(o.id,(balance.get(o.id)||0)+o.amount*cycles);}for(const o of flows.outputs)balance.set(o.id,(balance.get(o.id)||0)-o.rate);
  const surplus=[...balance].filter(([,rate])=>rate>1e-7).map(([id,rate])=>({id,rate}));return {requirements,work,byOutput,surplus};
 }
 function layoutLimit(flows,data){const d=demand(flows,data),missing=new Set();for(const [item]of d.work){const r=d.byOutput.get(item);if(!['smelter','constructor','assembler'].includes(r.type)||r.inputs.concat(r.outputs).some(i=>!i.solid))missing.add(data.machineNames?.[r.type]||r.type);}return missing.size?'Cette chaîne complète nécessite : '+[...missing].join(', ')+'. Le calcul des recettes est disponible ; ces machines et les fluides ne sont pas encore pris en charge pour le placement dans l’atelier.':null;}

 function resolveObjectives(mode,inputs,outputs,data){
  if(!['output','input','both'].includes(mode))throw new Error('Mode de calcul inconnu.');
  for(const rows of [inputs,outputs])if(!Array.isArray(rows)||new Set(rows.map(r=>r.id)).size!==rows.length||rows.some(r=>!data.names[r.id]||!Number.isFinite(r.rate)||r.rate<=0||r.rate>100000))throw new Error('Choisissez des ressources distinctes et des débits positifs.');
  if(!outputs.length)throw new Error('Précisez au moins une sortie.');
  if(inputs.some(i=>outputs.some(o=>o.id===i.id)))throw new Error('Une ressource ne peut pas être à la fois entrée et sortie cible.');
  if(mode==='output')return {outputs:M.clone(outputs),scale:1,limited:[],unused:[]};
  if(!inputs.length)throw new Error('Ajoutez au moins une entrée disponible.');
  const {requirements}=demand({inputs,outputs},data);
  const missing=[...requirements.keys()].filter(id=>!inputs.some(i=>i.id===id));
  if(missing.length)throw new Error('Indiquez aussi la disponibilité de : '+missing.map(id=>data.names[id]).join(', ')+'.');
  if(inputs.some(i=>!requirements.has(i.id)))throw new Error('Une entrée ne participe pas aux sorties choisies. Retirez-la ou ajoutez une sortie correspondante.');
  const maximum=Math.min(...inputs.map(i=>i.rate/requirements.get(i.id))),scale=mode==='both'?Math.min(1,maximum):maximum;
  const resolved=outputs.map(o=>({...o,rate:o.rate*scale}));
  if(resolved.some(o=>o.rate>100000))throw new Error('Le résultat dépasse la limite de ce prototype.');
  return {outputs:resolved,scale,limited:inputs.filter(i=>Math.abs(i.rate-requirements.get(i.id)*scale)<1e-6).map(i=>i.id),unused:inputs.map(i=>({id:i.id,rate:Math.max(0,i.rate-requirements.get(i.id)*scale)})).filter(i=>i.rate>1e-6)};
 }
 function power(project,data){let mw=0,unknown=0;for(const o of project.objects){if(!['smelter','constructor','assembler'].includes(o.type))continue;const power=data?.power?.[o.type];if(!power){unknown++;continue;}mw+=power.mw*Math.pow(o.clock??1,power.exponent);}return {mw,unknown};}
 const BELTS=[60,120,270,480,780,1200];
 function beltDiagnostic(project,link,data){
  const capacity=link.capacity??project.beltCapacity??120;
  let rate=link.rate,item=link.item;
  // Infer only a direct, unbranched machine-to-machine link with one matching item.
  if(!Number.isFinite(rate)&&link.kind==='belt'&&data){const from=project.objects.find(o=>o.id===link.from),to=project.objects.find(o=>o.id===link.to),a=data.recipes[from?.recipe],b=data.recipes[to?.recipe];const outgoing=project.links.filter(l=>l.kind!=='power'&&l.from===link.from),incoming=project.links.filter(l=>l.kind!=='power'&&l.to===link.to);const matches=a&&b?a.outputs.filter(i=>b.inputs.some(j=>j.id===i.id)):[];if(matches.length===1&&outgoing.length===1&&incoming.length===1){item=matches[0].id;rate=matches[0].amount*60/a.seconds*(from.clock??1);}}
  const known=Number.isFinite(rate)&&rate>0,state=!known?'unknown':rate>capacity+1e-7?'blocked':rate>=capacity*.9?'busy':'ok';
  const served=known?Math.min(rate,capacity):null,efficiency=known?100*served/rate:null;
  const color={unknown:'#99a5af',blocked:'#ef786c',busy:'#e8b85c',ok:'#7fd5a0'}[state];
  return {capacity,rate,item,state,color,served,efficiency,label:!known?'Débit inconnu':(data?.names[item]||item||'Ressource')+' · '+Number(rate.toFixed(2))+' / '+capacity+'/min · '+(state==='blocked'?'goulot : '+Math.round(efficiency)+' % du débit passe':state==='busy'?'proche de la capacité':'capacité suffisante')};
 }
 function calculateLegacy(flows,data,volume={}){if(flows.inputs.some(i=>flows.outputs.some(o=>o.id===i.id)))throw new Error('Choisissez une sortie différente des entrées : aucune transformation à calculer pour cette ressource.');const size=M.extent(volume),depth=M.depth(volume),height=M.height(volume),{requirements,work,byOutput}=demand(flows,data);
  const objects=[];let count=0;for(const [id,cycles]of work){const r=byOutput.get(id),machines=cycles*r.seconds/60;if(machines>100)throw new Error('Objectif trop grand pour ce prototype.');for(let i=0;i<Math.ceil(machines-1e-8);i++){const t=M.TYPES[r.type];objects.push({id:'calc-'+count++,type:r.type,name:r.name,w:t.w,d:t.d,x:0,y:0,z:0,h:r.type==='assembler'?10.75:r.type==='smelter'?8.5:8.5,rotation:0,recipe:Object.keys(data.recipes).find(k=>data.recipes[k]===r),clock:Math.min(1,machines-i)});}}
  if(!objects.length)throw new Error('Aucune machine de production : choisissez une sortie fabriquée à partir des entrées.');
  if(objects.length>100)throw new Error('Limite de 100 machines pour le placement assisté.');
  const settings={gap:4,pitch:8,thickness:1,material:'concrete',color:'#536454',...(volume.structure||{})};if(settings.pitch==='minimum')settings.pitch=10;
  if(!M.validStructure(settings)||!Number.isFinite(settings.gap)||settings.gap<4||settings.gap>8||![8,10,12,16].includes(settings.pitch)||!Number.isFinite(settings.thickness)||settings.thickness<.5||settings.thickness>2||settings.pitch<settings.thickness+7)throw new Error('Structure invalide : prévoyez au moins 7 m au-dessus du plancher, et un couloir de 4 à 8 m.');
  settings.pitch=[8,10,12,16].find(p=>p>=settings.pitch&&p>=Math.max(...objects.map(o=>o.h))+settings.thickness);
  // Place producers before consumers. A consumer never starts below its upstream machines.
  const stages=new Map();function stage(id){if(stages.has(id))return stages.get(id);const recipe=byOutput.get(id),value=1+Math.max(-1,...recipe.inputs.filter(i=>work.has(i.id)).map(i=>stage(i.id)));stages.set(id,value);return value;}
  const stageOf=o=>stage(data.recipes[o.recipe].outputs[0].id);
  let best=null;for(let mask=0;mask<8;mask++){const placed=[];let failed=false;const order=objects.slice().sort((a,b)=>stageOf(a)-stageOf(b)||b.w*b.d-a.w*a.d||a.id.localeCompare(b.id));for(const source of order){let fit=null;const o={...source,rotation:(mask&(source.type==='smelter'?1:source.type==='constructor'?2:4))?90:0},w=o.rotation?o.d:o.w,d=o.rotation?o.w:o.d;for(let base=Math.max(0,...placed.filter(p=>data.recipes[source.recipe].inputs.some(i=>data.recipes[p.recipe].outputs.some(out=>out.id===i.id))).map(p=>p.z-settings.thickness));base+settings.thickness+o.h<=height&&!fit;base+=settings.pitch){const here=placed.filter(p=>p.z===base+settings.thickness),xs=[8,...here.map(p=>M.bounds(p).maxX+settings.gap)],ys=[2,...here.map(p=>M.bounds(p).maxY+settings.gap)];for(const y of [...new Set(ys)].sort((a,b)=>a-b)){for(const x of [...new Set(xs)].sort((a,b)=>a-b)){const candidate={...o,x:x+w/2,y:y+d/2,z:base+settings.thickness};if(x+w>size-2+1e-7||y+d>depth-2+1e-7)continue;const envelope=M.bounds(candidate);const clash=here.some(p=>{const r=M.bounds(p);return envelope.minX<r.maxX+settings.gap-1e-7&&envelope.maxX>r.minX-settings.gap+1e-7&&envelope.minY<r.maxY+settings.gap-1e-7&&envelope.maxY>r.minY-settings.gap+1e-7;});if(!clash){fit=candidate;break;}}if(fit)break;}}if(!fit){failed=true;break;}placed.push(fit);}if(failed)continue;const levels=[...new Set(placed.map(o=>o.z-settings.thickness))],score=levels.length*100000+placed.reduce((sum,o)=>sum+M.bounds(o).maxY,0);if(!best||score<best.score)best={placed,levels,score};}
  if(!best)throw new Error('Le format sélectionné ne contient pas la chaîne avec les couloirs de '+settings.gap+' m, les virages et les planchers. Augmentez le format ou réduisez les débits.');
  const placed=best.placed,floors=best.levels.sort((a,b)=>a-b).map(z=>({z,thickness:settings.thickness,material:settings.material,color:settings.color,shaft:2}));
  const network=planNetwork(placed,flows,data,{size,depth,height,floors,structure:settings});
  return {objects:placed,floors,structure:settings,...network,required:[...requirements].map(([id,rate])=>({id,rate})),shortages:[...requirements].filter(([id,rate])=>{const row=flows.inputs.find(r=>r.id===id);return row&&row.rate<rate-1e-7;}).map(([id,rate])=>({id,rate}))};
 }
 function planNetwork(machines,flows,data,volume){if(!volume.floors.length||volume.floors.some(f=>!Number.isFinite(f.z)||!Number.isFinite(f.thickness)))throw new Error('Aucun étage valide pour placer la logistique.');const project={...volume,objects:M.clone(machines)},links=[],logistics=[],sources=new Map(),targets=new Map();let serial=0;
  const add=(map,id,node,rate)=>{if(!map.has(id))map.set(id,[]);map.get(id).push({node,rate});};
  for(const o of machines){const r=data.recipes[o.recipe],factor=60/r.seconds*o.clock;for(const i of r.outputs)add(sources,i.id,o,i.amount*factor);for(const i of r.inputs)add(targets,i.id,o,i.amount*factor);}
  function node(type,name,preferred){const t=M.TYPES[type],levels=volume.floors.map(f=>f.z+f.thickness).sort((a,b)=>Math.abs(a-preferred)-Math.abs(b-preferred)||a-b);for(const z of levels)for(let y=2;y<=M.depth(volume)-2;y+=4){const o={id:'net-'+serial++,type,name:name.slice(0,80),x:4.5,y,z,h:2,w:type==='port'?2:3,d:type==='port'?2:3,rotation:0,recipe:null,clock:1};if(shapeBox(project,o)&&!M.candidate(project,o)){project.objects.push(o);logistics.push(o);return o;}}const base=Math.max(...volume.floors.map(f=>f.z))+volume.structure.pitch;if(base+volume.structure.thickness+6<=M.height(volume)){volume.floors.push({...volume.floors[0],z:base});return node(type,name,preferred);}throw new Error('Le format sélectionné ne contient pas toute la logistique. Augmentez le format ou réduisez les débits.');}
  function link(from,to,item,rate){links.push({kind:'planned',from:from.id,to:to.id,item,rate});}
  for(const output of flows.outputs){const preferred=sources.get(output.id)?.[0]?.node.z||volume.structure.thickness;add(targets,output.id,node('port','Sortie · '+data.names[output.id],preferred),output.rate);}
  for(const [item,destinations]of targets){let origins=sources.get(item)||[];if(!origins.length){const rate=destinations.reduce((sum,d)=>sum+d.rate,0);origins=[{node:node('port','Entrée · '+data.names[item],destinations[0].node.z),rate}];}
   const queue=origins.slice();while(queue.length>1){const group=queue.splice(0,3),junction=node('merger','Fusion · '+data.names[item],group[0].node.z),rate=group.reduce((sum,g)=>sum+g.rate,0);for(const g of group)link(g.node,junction,item,g.rate);queue.push({node:junction,rate});}
   function distribute(source,dests){if(dests.length===1){link(source,dests[0].node,item,dests[0].rate);return;}const junction=node('splitter','Répartition · '+data.names[item],source.z),rate=dests.reduce((sum,d)=>sum+d.rate,0);link(source,junction,item,rate);if(dests.length<=3){for(const d of dests)link(junction,d.node,item,d.rate);}else{const step=Math.ceil(dests.length/3);for(let i=0;i<dests.length;i+=step)distribute(junction,dests.slice(i,i+step));}}
   distribute(queue[0].node,destinations);
  }
  let shaft=0;for(const item of new Set(links.map(l=>l.item))){const crossings=links.filter(l=>l.item===item&&project.objects.find(o=>o.id===l.from).z!==project.objects.find(o=>o.id===l.to).z);if(!crossings.length)continue;const zs=crossings.flatMap(l=>[project.objects.find(o=>o.id===l.from).z,project.objects.find(o=>o.id===l.to).z]),bottom=Math.min(...zs),top=Math.max(...zs);const lift={id:'shaft-'+shaft,type:'lift',name:'Gaine réservée · '+data.names[item],x:1,y:2+shaft*5,z:bottom,h:top-bottom+2,w:2,d:2,rotation:0,recipe:null,clock:1};shaft++;if(M.candidate(project,lift))throw new Error('Pas assez de place pour les gaines verticales.');project.objects.push(lift);logistics.push(lift);for(const l of crossings)l.via=lift.id;}
  if(project.objects.length>300)throw new Error('La chaîne dépasse la limite de 300 objets, logistique comprise.');const errors=M.problems(project);if(errors.length)throw new Error(errors[0].text);return {logistics,links};
 }
 // Reusable two-machine bays. A recipe stays in its own row and service aisles
 // separate rows; only an explicit vertical request assigns recipes to storeys.
 function calculateZones(flows,data,volume){
  volume={...volume,generation:{...volume.generation,routed:true}};
  const {requirements,work,byOutput}=demand(flows,data),settings={gap:4,pitch:'minimum',thickness:1,material:'concrete',color:'#536454',...volume.structure},g=volume.generation||{},size=M.extent(volume),depth=M.depth(volume),height=M.height(volume);
  const stages=new Map();function stage(id){if(stages.has(id))return stages.get(id);const r=byOutput.get(id),n=1+Math.max(-1,...r.inputs.filter(i=>work.has(i.id)).map(i=>stage(i.id)));stages.set(id,n);return n;}
  const rows=[...work].sort((a,b)=>stage(a[0])-stage(b[0])||a[0].localeCompare(b[0])),objects=[],zones=[],floors=[],gap=g.layoutStyle==='spacious'?8:4,pitch=settings.pitch==='minimum'?16:Math.max(16,settings.pitch);const originY=g.shape==='exotic'?Math.ceil(depth/16)*8+12:12;let y=originY,x=12,z=settings.thickness,serial=0,previousStage=-1,usedDepth=0;
  for(const [item,cycles]of rows){const r=byOutput.get(item),count=cycles*r.seconds/60,t=M.TYPES[r.type],h=r.type==='assembler'?10.75:r.type==='smelter'?8.5:6,recipe=Object.keys(data.recipes).find(k=>data.recipes[k]===r),bayWidth=2*t.w+gap+8,rowDepth=t.d+16;
   if(count>100||objects.length+Math.ceil(count-1e-8)>100)throw new Error('Plus de 100 machines : réduisez le débit.');
   const level=g.storeyMode==='vertical'?Math.min(stage(item),Math.max(0,(g.maxStoreys||3)-1)):0;
   if(level*pitch+settings.thickness!==z){z=level*pitch+settings.thickness;y=originY;x=12;usedDepth=0;}
   else if(previousStage!==-1&&stage(item)!==previousStage){y+=usedDepth+8;x=12;usedDepth=0;}
   previousStage=stage(item);usedDepth=Math.max(usedDepth,rowDepth);
   for(let i=0;i<Math.ceil(count-1e-8);i+=2){
    if(x+bayWidth>size-12){x=12;y+=usedDepth+8;usedDepth=rowDepth;}
    if(y+rowDepth>depth-8){if(g.storeyMode==='single'||g.storeyMode==='auto'||z+pitch>=height||floors.length>=(g.maxStoreys||3))throw new Error('Terrain trop petit pour les sous-zones et leurs allées.');z+=pitch;y=originY;x=12;}
    if(z+h>height||x+bayWidth>size-12)throw new Error('Sous-zone hors du volume disponible.');
    if(!floors.some(f=>f.z===z-settings.thickness))floors.push({z:z-settings.thickness,thickness:settings.thickness,material:settings.material,color:settings.color,shaft:2,profile:g.floorProfile||'factory'});
    const zone='zone-'+zones.length,members=[];
    for(let j=i;j<Math.min(i+2,Math.ceil(count-1e-8));j++){const o={id:'calc-'+serial++,type:r.type,name:r.name,w:t.w,d:t.d,h,x:x+4+t.w/2+(j-i)*(t.w+gap),y:y+12+t.d/2,z,rotation:180,recipe,clock:Math.min(1,count-j),zone};if(!shapeBox(volume,o))throw new Error('Sous-zone dans la cour réservée.');objects.push(o);members.push(o.id);}
    zones.push({id:zone,name:r.name,recipe,machines:members});x+=bayWidth+8;
   }
  }
  if(!objects.length)throw new Error('Aucune transformation à calculer.');
  const network=planNetworkPhysical(objects,flows,data,{...volume,floors,structure:settings});
  return {objects,floors,structure:settings,...network,zones,required:[...requirements].map(([id,rate])=>({id,rate})),shortages:[...requirements].filter(([id,rate])=>flows.inputs.some(r=>r.id===id&&r.rate<rate-1e-7)).map(([id,rate])=>({id,rate}))};
 }
 function calculate(flows,data,volume={}){const unavailable=layoutLimit(flows,data);if(unavailable)throw new Error(unavailable);
  if(!volume.physical)return calculateLegacy(flows,data,volume);
  if(flows.inputs.some(i=>flows.outputs.some(o=>o.id===i.id)))throw new Error('Choisissez une sortie différente des entrées.');
  const size=M.extent(volume),depth=M.depth(volume),height=M.height(volume),{requirements,work,byOutput}=demand(flows,data),objects=[];let serial=0;
  for(const [id,cycles]of work){const r=byOutput.get(id),count=cycles*r.seconds/60;if(count>100)throw new Error('Plus de 100 machines : réduisez le débit.');for(let i=0;i<Math.ceil(count-1e-8);i++){const t={...M.TYPES[r.type],...({smelter:{w:5,d:10},assembler:{w:9,d:17}}[r.type]||{})};objects.push({id:'calc-'+serial++,type:r.type,name:r.name,w:t.w,d:t.d,x:0,y:0,z:0,h:r.type==='assembler'?10.75:r.type==='smelter'?8.5:6,rotation:0,recipe:Object.keys(data.recipes).find(k=>data.recipes[k]===r),clock:Math.min(1,count-i)});}}
  if(!objects.length||objects.length>100)throw new Error('Choisissez une chaîne entre 1 et 100 machines.');
  const settings={gap:4,pitch:'minimum',thickness:1,material:'concrete',color:'#536454',...(volume.structure||{})};if(!M.validStructure(settings))throw new Error('Structure du plan invalide.');
  const g={...(volume.generation||{}),...(volume.physical?{routed:true}:{})},policy=g.storeyMode||'auto',limit=policy==='single'?1:policy==='auto'?Math.min(64,Math.floor(height/8)):Math.min(64,g.maxStoreys||3),spacing=g.layoutStyle==='spacious'?8:g.layoutStyle==='compact'?2:4;
  const stages=new Map();function stage(id){if(stages.has(id))return stages.get(id);const r=byOutput.get(id),n=1+Math.max(-1,...r.inputs.filter(i=>work.has(i.id)).map(i=>stage(i.id)));stages.set(id,n);return n;}
  const stageOf=o=>stage(data.recipes[o.recipe].outputs[0].id),maxStage=Math.max(...objects.map(stageOf));
  const counts=Array.from({length:limit},(_,i)=>i+1);if(policy==='vertical')counts.reverse();let lastReason='';
  for(const count of counts){
   // Minimum pitch follows the machines on each storey instead of imposing the assembler height everywhere.
   const bases=[0];for(let i=1;i<count;i++)bases.push(bases[i-1]+(settings.pitch==='minimum'?(g.routingMargin?Math.ceil(Math.max(...objects.map(o=>o.h))+settings.thickness+3):policy==='vertical'?Math.ceil(Math.max(...objects.map(o=>o.h))+settings.thickness):(i===1?10:8)):Number(settings.pitch)));
   if(bases[count-1]+settings.thickness+Math.min(...objects.map(o=>o.h))>height)continue;
   for(let mask=0;mask<32;mask++){
    const placed=[],order=objects.slice().sort((a,b)=>(mask&16?0:stageOf(a)-stageOf(b))||(mask&8?a.w*a.d-b.w*b.d:b.w*b.d-a.w*a.d));let failed=false;
    for(const source of order){let fit=null;const preferred=policy==='vertical'?Math.min(count-1,Math.floor(placed.length*count/order.length)):0;
     const indices=Array.from({length:count},(_,i)=>i).sort((a,b)=>Math.abs(a-preferred)-Math.abs(b-preferred));
     for(const li of indices){const base=bases[li],top=bases[li+1]??height;if(base+settings.thickness+source.h>top+1e-7)continue;
      for(const rotation of [(mask&(source.type==='smelter'?1:source.type==='constructor'?2:4))?90:0,(mask&(source.type==='smelter'?1:source.type==='constructor'?2:4))?0:90]){
       const w=rotation?source.d:source.w,d=rotation?source.w:source.d,here=placed.filter(p=>p.z===base+settings.thickness),xs=[(g.priority==='architecture'||g.routingMargin)?(g.layoutStyle==='compact'?8:12):8,...here.map(p=>M.bounds(p).maxX+spacing),...(volume.reserved||[]).map(r=>r[0][1]+2)],ys=[(g.priority==='architecture'||g.routingMargin)?6:2,...here.map(p=>M.bounds(p).maxY+spacing)];
       for(const y of [...new Set(ys)].sort((a,b)=>a-b)){for(const x of [...new Set(xs)].sort((a,b)=>a-b)){if(x+w>size-((g.priority==='architecture'||g.routingMargin)?4:2)||y+d>depth-((g.priority==='architecture'||g.routingMargin)?4:2))continue;const candidate={...source,rotation,x:x+w/2,y:y+d/2,z:base+settings.thickness},box=M.bounds(candidate);if(!shapeBox({...volume,generation:g},candidate))continue;if(here.some(p=>{const r=M.bounds(p);return box.minX<r.maxX+spacing-1e-7&&box.maxX>r.minX-spacing+1e-7&&box.minY<r.maxY+spacing-1e-7&&box.maxY>r.minY-spacing+1e-7;}))continue;fit=candidate;break;}if(fit)break;}if(fit)break;
      }if(fit)break;
     }if(!fit){failed=true;break;}placed.push(fit);
    }
    if(failed)continue;
    const floors=bases.filter(z=>placed.some(o=>o.z===z+settings.thickness)).map(z=>({z,thickness:settings.thickness,material:settings.material,color:settings.color,shaft:2,profile:g.floorProfile||'factory'}));
    try{const network=planNetworkPhysical(placed,flows,data,{size,depth,height,floors,structure:settings,generation:g,physical:volume.physical});return {objects:placed,floors,structure:settings,...network,required:[...requirements].map(([id,rate])=>({id,rate})),shortages:[...requirements].filter(([id,rate])=>flows.inputs.some(r=>r.id===id&&r.rate<rate-1e-7)).map(([id,rate])=>({id,rate}))};}catch(error){lastReason=error.message;}
   }
  }
  throw new Error(`Le placement automatique n’a pas trouvé de réseau complet pour ${objects.length} machines dans ${size/8} × ${depth/8}, sur ${limit} étage(s) maximum avec ce style. Essayez Auto, un étage supplémentaire ou un format supérieur.${lastReason?' '+lastReason:''}`);
 }
 function planNetworkPhysical(machines,flows,data,volume){if(!volume.floors.length||volume.floors.some(f=>!Number.isFinite(f.z)||!Number.isFinite(f.thickness)))throw new Error('Aucun étage valide pour placer la logistique.');const project={...volume,objects:M.clone(machines)},links=[],logistics=[],sources=new Map(),targets=new Map();let serial=0;
  const add=(map,id,node,rate)=>{if(!map.has(id))map.set(id,[]);map.get(id).push({node,rate});};
  for(const o of machines){const r=data.recipes[o.recipe],factor=60/r.seconds*o.clock;for(const i of r.outputs)add(sources,i.id,o,i.amount*factor);for(const i of r.inputs)add(targets,i.id,o,i.amount*factor);}
  function node(type,name,preferred){const t=type==='storage'?{...M.TYPES.storage,d:11}:M.TYPES[type],levels=volume.floors.map(f=>f.z+f.thickness).sort((a,b)=>Math.abs(a-preferred)-Math.abs(b-preferred)||a-b);for(const z of levels)for(const railX of volume.generation?.layoutStyle==='compact'?[...(type==='storage'?[volume.size-(volume.generation?.priority==='architecture'?10:6.5),9]:[volume.generation?.priority==='architecture'?6.5:3.5,volume.size-(volume.generation?.priority==='architecture'?6.5:3.5)]),...Array.from({length:Math.ceil(volume.size/4)},(_,i)=>4.5+i*4)]:(volume.generation?.routingMargin||volume.generation?.priority==='architecture')?(type==='storage'?[volume.size-10]:[6.5,volume.size-6.5]):[null])for(let y=(volume.generation?.priority==='architecture'||volume.generation?.routingMargin)?8:2;y<=M.depth(volume)-((volume.generation?.priority==='architecture'||volume.generation?.routingMargin)?6:2);y+=(volume.generation?.priority==='architecture'||volume.generation?.routingMargin)?6:4){const o={id:'net-'+serial++,type,name:name.slice(0,80),x:railX??((volume.generation?.priority==='architecture'||volume.generation?.routingMargin)?(type==='storage'?volume.size-10:6.5):type==='storage'?6.5:3.5),y,z,h:type==='storage'?4:2,w:t.w,d:t.d,rotation:volume.physical?90:0,recipe:null,clock:1};if(volume.physical){if(type==='storage')o.rotation=o.x>volume.size/2?90:270;else o.rotation=o.x>volume.size/2?270:90;}const border=volume.generation?.priority==='architecture'||volume.generation?.routingMargin?4:0,ends=type==='storage'?[false]:type==='port'?[true]:[false,true],accessible=ends.every(output=>{const at=port(o,output),angle=o.rotation*Math.PI/180,sign=output?-1:1,x=at.x-Math.sin(angle)*sign,y=at.y+Math.cos(angle)*sign;return x>=border&&y>=border&&x<=volume.size-border&&y<=M.depth(volume)-border&&!project.objects.some(v=>{if(!M.vertical(o,v))return false;const b=M.bounds(v);return x>b.minX-.3&&x<b.maxX+.3&&y>b.minY-.3&&y<b.maxY+.3;});});const bounds=M.bounds(o),inside=volume.generation?.priority!=='architecture'||bounds.minX>=4&&bounds.minY>=4&&bounds.maxX<=volume.size-4&&bounds.maxY<=M.depth(volume)-4;if(inside&&accessible&&shapeBox(project,o)&&!M.candidate(project,o)){project.objects.push(o);logistics.push(o);return o;}}const base=Math.max(...volume.floors.map(f=>f.z))+(volume.structure.pitch==='minimum'?12:volume.structure.pitch);if(!volume.physical&&base+volume.structure.thickness+6<=M.height(volume)){volume.floors.push({...volume.floors[0],z:base});return node(type,name,preferred);}throw new Error('Le format sélectionné ne contient pas toute la logistique. Augmentez le format ou réduisez les débits.');}
  function link(from,to,item,rate){links.push({kind:'planned',from:from.id,to:to.id,item,rate});}
  for(const output of flows.outputs){const preferred=sources.get(output.id)?.[0]?.node.z||volume.structure.thickness;const o=node('storage','Sortie · '+data.names[output.id],preferred);o.io={side:'output',item:output.id,rate:output.rate};add(targets,output.id,o,output.rate);}
  for(const [item,destinations]of targets){let origins=sources.get(item)||[];if(!origins.length){const rate=destinations.reduce((sum,d)=>sum+d.rate,0);const o=node('port','Entrée · '+data.names[item],destinations[0].node.z);o.io={side:'input',item,rate};origins=[{node:o,rate}];}
   const queue=origins.slice();while(queue.length>1){const group=queue.splice(0,3),junction=node('merger','Fusion · '+data.names[item],group[0].node.z),rate=group.reduce((sum,g)=>sum+g.rate,0);for(const g of group)link(g.node,junction,item,g.rate);queue.push({node:junction,rate});}
   function distribute(source,dests){if(dests.length===1){link(source,dests[0].node,item,dests[0].rate);return;}const junction=node('splitter','Répartition · '+data.names[item],source.z),rate=dests.reduce((sum,d)=>sum+d.rate,0);link(source,junction,item,rate);if(dests.length<=3){for(const d of dests)link(junction,d.node,item,d.rate);}else{const step=Math.ceil(dests.length/3);for(let i=0;i<dests.length;i+=step)distribute(junction,dests.slice(i,i+step));}}
   distribute(queue[0].node,destinations);
  }
  let shaft=0;
  if(volume.physical){for(const l of links){const from=project.objects.find(o=>o.id===l.from),to=project.objects.find(o=>o.id===l.to);l.kind='belt';l.capacity=[60,120,270,480,780].find(c=>c>=l.rate-1e-6)||780;
   if(from.z===to.z)continue;let lift=null;const bottom=Math.min(from.z,to.z),top=Math.max(from.z,to.z);
   for(let y=(volume.generation?.priority==='architecture'||volume.generation?.routingMargin)?8:4;y<=M.depth(volume)-2;y+=4){const o={id:'shaft-'+shaft,type:'lift',name:'Élévateur · '+data.names[l.item],x:(volume.generation?.priority==='architecture'||volume.generation?.routingMargin)?5.5:1.5,y,z:bottom,h:top-bottom+2,w:1,d:1,rotation:90,recipe:null,clock:1};if(shapeBox(project,o)&&!M.candidate(project,o)){lift=o;break;}}
   if(!lift)throw new Error('Aucune place libre pour un élévateur de '+data.names[l.item]+'.');shaft++;project.objects.push(lift);logistics.push(lift);l.via=lift.id;
  }
  project.links=links;
  for(const link of links)if(!route(project,link.from,link.to))throw new Error('Passage convoyeur bloqué : '+project.objects.find(o=>o.id===link.from).name+' → '+project.objects.find(o=>o.id===link.to).name+'.');
  }else{
  let shaft=0;for(const item of new Set(links.map(l=>l.item))){const crossings=links.filter(l=>l.item===item&&project.objects.find(o=>o.id===l.from).z!==project.objects.find(o=>o.id===l.to).z);if(!crossings.length)continue;const zs=crossings.flatMap(l=>[project.objects.find(o=>o.id===l.from).z,project.objects.find(o=>o.id===l.to).z]),bottom=Math.min(...zs),top=Math.max(...zs);const lift={id:'shaft-'+shaft,type:'lift',name:'Gaine réservée · '+data.names[item],x:1,y:2+shaft*5,z:bottom,h:top-bottom+2,w:2,d:2,rotation:0,recipe:null,clock:1};shaft++;if(M.candidate(project,lift))throw new Error('Pas assez de place pour les gaines verticales.');project.objects.push(lift);logistics.push(lift);for(const l of crossings)l.via=lift.id;}
  }
  if(project.objects.length>300)throw new Error('La chaîne dépasse la limite de 300 objets, logistique comprise.');const errors=M.problems(project);if(errors.length)throw new Error(errors[0].text);return {logistics,links};
 }
 function addPoles(project,style=project.powerStyle||'per-machine'){
  if(!['per-machine','shared'].includes(style))throw new Error('Style électrique inconnu.');
  const next=M.clone(project),machines=next.objects.filter(o=>['smelter','constructor','assembler'].includes(o.type)),oldLinks=next.links.filter(l=>l.kind==='power'),links=next.links.filter(l=>l.kind!=='power'),usage=new Map(),limit=style==='per-machine'?1:2;let serial=0;
  next.powerStyle=style;
  function position(machine,id){
   const angle=machine.rotation*Math.PI/180;
   for(let margin=1;margin<=4;margin+=.5)for(const [right,rear]of [[1,1],[-1,1],[1,-1],[-1,-1]]){
    const x=right*(machine.w/2+margin),y=rear*(machine.d/2-1),candidate={id,type:'pole',name:('Électricité · '+machine.name).slice(0,80),x:machine.x+Math.cos(angle)*x-Math.sin(angle)*y,y:machine.y+Math.sin(angle)*x+Math.cos(angle)*y,z:machine.z||0,h:7,w:1,d:1,rotation:machine.rotation,recipe:null,clock:1};
    if(shapeBox(next,candidate)&&!M.candidate(next,candidate))return candidate;
   }
   throw new Error('Pas de place pour un poteau au coin de '+machine.name+'. Libérez un coin de la machine.');
  }
  for(const machine of machines){
   const previous=oldLinks.find(l=>l.to===machine.id&&next.objects.some(o=>o.id===l.from&&o.type==='pole'))?.from;
   const available=o=>o.type==='pole'&&(o.z||0)===(machine.z||0)&&Math.hypot(o.x-machine.x,o.y-machine.y)<=12&&(usage.get(o.id)||0)<limit;
   let pole=next.objects.find(o=>o.id===previous&&available(o))||next.objects.find(available);
   if(!pole){let id;do{id='pole-'+Date.now()+'-'+serial++;}while(next.objects.some(o=>o.id===id));pole=position(machine,id);next.objects.push(pole);}
   else if(style==='per-machine'&&(pole.name==='Poteau proposé'||pole.name.startsWith('Électricité · '))){const placed=position(machine,pole.id);Object.assign(pole,placed);}
   usage.set(pole.id,(usage.get(pole.id)||0)+1);links.push({kind:'power',from:pole.id,to:machine.id});
  }
  // A tidy chain on each floor, followed by a single transition to the next floor.
  const poles=next.objects.filter(o=>o.type==='pole'),levels=[...new Set(poles.map(o=>o.z||0))].sort((a,b)=>a-b);let previous=null;
  for(const z of levels){const remaining=poles.filter(o=>(o.z||0)===z);while(remaining.length){remaining.sort((a,b)=>previous?(Math.hypot(a.x-previous.x,a.y-previous.y)-Math.hypot(b.x-previous.x,b.y-previous.y)||a.y-b.y||a.x-b.x):(a.y-b.y||a.x-b.x));const pole=remaining.shift();if(previous)links.push({kind:'power',from:previous.id,to:pole.id});previous=pole;}}
  next.links=links;if(next.objects.length>300)throw new Error('Limite de 300 objets atteinte.');return next;
 }
 // Fixed outputs are satisfied first; automatic outputs share remaining inputs equally.
 // This only solves rates. Packing must remain an explicit user action.
 function resolveFlexible(flows,data){
  const {inputs,outputs}=flows;
  for(const rows of [inputs,outputs])if(!Array.isArray(rows)||new Set(rows.map(r=>r.id)).size!==rows.length||rows.some(r=>!data.names[r.id]||(r.rate!==null&&(!Number.isFinite(r.rate)||r.rate<=0||r.rate>100000))))throw new Error('Ressource ou débit invalide.');
  if(!outputs.length)throw new Error('Ajoutez au moins une sortie.');
  if(inputs.some(i=>outputs.some(o=>o.id===i.id)))throw new Error('Une ressource ne peut pas être à la fois entrée et sortie.');
  const fixed=outputs.filter(o=>o.rate!==null),automatic=outputs.filter(o=>o.rate===null),budgets=inputs.filter(i=>i.rate!==null);
  if(!inputs.length&&automatic.length){const targets=outputs.map(o=>{if(o.rate!==null)return {...o};const r=(data.productionRecipes||data.recipes)[(data.productionDefaults||data.defaultRecipes)?.[o.id]]||Object.values(data.recipes).find(r=>r.outputs[0].id===o.id);if(!r)throw new Error('Indiquez un débit de sortie pour '+data.names[o.id]+'.');return {...o,rate:60*r.outputs.find(i=>i.id===o.id).amount/r.seconds};});return resolveFlexible({...flows,inputs:[],outputs:targets},data);}
  const fixedNeed=fixed.length?demand({inputs,outputs:fixed},data).requirements:new Map();
  // Equal resource shares use the inverse cost of each output, after fixed targets.
  // Normalize multiple resources by their remaining budgets; the limiting input wins.
  const weights=new Map(automatic.map(o=>[o.id,1]));
  if(flows.resourceWeighted&&budgets.length)for(const o of automatic){
   const need=demand({inputs,outputs:[{...o,rate:1}]},data).requirements;
   const cost=budgets.reduce((sum,i)=>sum+(need.get(i.id)||0)/Math.max(1e-9,i.rate-(fixedNeed.get(i.id)||0)),0);
   if(cost>0)weights.set(o.id,1/cost);
  }
  const unitNeed=automatic.length?demand({inputs,outputs:automatic.map(o=>({...o,rate:weights.get(o.id)}))},data).requirements:new Map();
  for(const i of budgets){if(!fixedNeed.has(i.id)&&!unitNeed.has(i.id))throw new Error(data.names[i.id]+' ne participe pas aux sorties choisies.');if(i.rate<(fixedNeed.get(i.id)||0)-1e-7)throw new Error('Entrée insuffisante : '+data.names[i.id]+'. Réduisez la sortie fixée ou laissez son débit vide.');}
  let scale=0;
  if(automatic.length){const constraints=budgets.filter(i=>unitNeed.has(i.id));if(!constraints.length)throw new Error('Renseignez un débit d’entrée pour calculer une sortie automatique.');scale=Math.min(...constraints.map(i=>(i.rate-(fixedNeed.get(i.id)||0))/unitNeed.get(i.id)));if(scale<=1e-7)throw new Error('Aucune entrée restante pour les sorties automatiques.');}
  const resolvedOutputs=outputs.map(o=>({...o,rate:o.rate===null?scale*weights.get(o.id):o.rate}));
  const required=demand({inputs,outputs:resolvedOutputs},data).requirements;
  const resolvedInputs=[...required].map(([id,rate])=>({id,rate}));
  if([...resolvedInputs,...resolvedOutputs].some(r=>!Number.isFinite(r.rate)||r.rate>100000))throw new Error('Le résultat dépasse 100 000/min.');
  const unused=budgets.map(i=>({id:i.id,rate:i.rate-(required.get(i.id)||0)})).filter(i=>i.rate>1e-7);
  return {inputs:resolvedInputs,outputs:resolvedOutputs,unused,...(flows.resourceWeighted?{resourceWeighted:true}:{})};
 }
 const physicalCache=new WeakMap();
 function physicalPath(project,link){
  if(!link.native)return null;if(!physicalCache.has(project))physicalCache.set(project,new WeakMap());const cache=physicalCache.get(project);if(cache.has(link))return cache.get(link);
  const o=project.objects.find(o=>o.id===link.from);if(!o?.native)return null;
  function rotate(q,v){const [x,y,z,w]=q,[a,b,c]=v;return [(1-2*y*y-2*z*z)*a+(2*x*y-2*z*w)*b+(2*x*z+2*y*w)*c,(2*x*y+2*z*w)*a+(1-2*x*x-2*z*z)*b+(2*y*z-2*x*w)*c,(2*x*z-2*y*w)*a+(2*y*z+2*x*w)*b+(1-2*x*x-2*y*y)*c];}
  const angle=(o.rotation-o.native.rotation)*Math.PI/180,c=Math.cos(angle),s=Math.sin(angle);
  const point=v=>{const r=rotate(o.native.quaternion,v);return {x:o.x+c*r[0]-s*r[1],y:o.y+s*r[0]+c*r[1],z:o.z+o.native.originZ+r[2]};};
  const points=[];
  if(link.native.snap){const p=o.native.ports[link.native.fromPort];if(p)points.push(point(p));}
  else for(const [a,b,ta,tb]of link.native.spans||[])for(let i=0;i<=24;i++){const t=i/24;points.push(point(a.map((v,j)=>(2*t**3-3*t*t+1)*v+(t**3-2*t*t+t)*ta[j]+(-2*t**3+3*t*t)*b[j]+(t**3-t*t)*tb[j])));}
  cache.set(link,points);return points;
 }
 const api={physicalPath,layoutLimit,demand,resolveObjectives,resolveFlexible,power,BELTS,beltDiagnostic,port,route,parseCalculator,calculate,addPoles};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.WorkshopAssist=api;
})(typeof globalThis!=='undefined'?globalThis:this);





