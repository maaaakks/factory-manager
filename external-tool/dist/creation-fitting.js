'use strict';
(function(root){

 function restoreAttachments(p){
  const v=p.design?.living;for(const o of p.objects){const a=v?.attachmentAnchors?.[o.id],s=v?.attachmentOrigins?.[o.id];if(a&&s&&['x','y','z','rotation'].every(k=>Math.abs(o[k]-a[k])<1e-6)){Object.assign(o,JSON.parse(JSON.stringify(s)));}}
 }
 function detach(source){
  const node=typeof module!=='undefined'&&module.exports,M=node?require('./workshop-model'):root.WorkshopModel,D=node?require('./workshop-design'):root.WorkshopDesign,p=M.clone(source);(node?require('./creation-living'):root.CreationLiving).restorePower(p);restoreAttachments(p);
  p.design={...D.settings(p.design),enabled:false};for(const k of ['living','studyFloors','studyFitted'])delete p.design[k];
  // Ground slab belongs to the creation. Keep upper production supports intact.
  p.floors=(p.floors||[]).filter(f=>f.z>0);if(p.generation)p.generation.reserveCladding=false;
  return p;
 }
 function removeStorage(p){const ids=new Set(p.objects.filter(o=>o.type==='storage').map(o=>o.id));if(!ids.size)return;const incoming=p.links.find(l=>ids.has(l.to)&&l.kind==='belt');if(incoming&&p.layoutInfo?.output)p.layoutInfo.output={...p.layoutInfo.output,objectId:incoming.from,port:incoming.native?.fromPort||'Output1'};for(const o of p.objects)if(o.id===incoming?.from)o.name='Sortie usine';p.objects=p.objects.filter(o=>!ids.has(o.id));p.links=p.links.filter(l=>!ids.has(l.from)&&!ids.has(l.to));}
 function fitCompact(source,packs){
  const node=typeof module!=='undefined'&&module.exports,D=node?require('./workshop-design'):root.WorkshopDesign,M=node?require('./workshop-model'):root.WorkshopModel,C=node?require('./design-campus'):root.DesignCampus;
  const clean=M.clone(source);clean.design=clean.design||{};(node?require('./creation-living'):root.CreationLiving).restorePower(clean);restoreAttachments(clean);delete clean.design.living;delete clean.design.studyFitted;delete clean.design.studyFloors;
  if(!clean.objects.length){const next=C.project('compact');next.id=source.id;next.name=source.name;next.buffer=M.clone(source.buffer||[]);next.design.packs=packs;next.design.ledColor=source.design?.ledColor||next.design.ledColor;return next;}
  removeStorage(clean);restoreAttachments(clean);const production=clean.objects.filter(o=>o.type!=='wallPole'),boxes=production.map(M.bounds),paths=D.accessPaths(clean).flat();
  const minX=Math.min(...boxes.map(b=>b.minX),...paths.map(v=>v[0])),maxX=Math.max(...boxes.map(b=>b.maxX),...paths.map(v=>v[0])),minY=Math.min(...boxes.map(b=>b.minY),...paths.map(v=>v[1])),maxY=Math.max(...boxes.map(b=>b.maxY),...paths.map(v=>v[1]));
  if((clean.floors||[]).some(f=>f.z>0))throw new Error('Compact accueille actuellement un seul niveau de production. Les étages sont conservés : choisissez une autre création.');
  const top=Math.max(...clean.objects.filter(o=>!['wallPole','port','input','output','entry','exit'].includes(o.type)).map(o=>(o.z||0)+(o.h||6)),...paths.map(v=>v[2]||0));
  if(top>16.5)throw new Error('Compact : cette production dépasse les 16 m disponibles sous toiture. Réorganisez-la sur un niveau. Le projet est conservé.');
  for(const size of[48,64,80,96]){
   if(maxX-minX>size-20||maxY-minY>size-20)continue;
   const moves=[];for(let dx=Math.ceil((10-minX)/8)*8;dx<=size-10-maxX;dx+=8)for(let dy=Math.ceil((10-minY)/8)*8;dy<=size-10-maxY;dy+=8)moves.push([dx,dy]);
   moves.sort((a,b)=>Math.abs((minX+maxX)/2+a[0]-size/2)+Math.abs((minY+maxY)/2+a[1]-size/2)-Math.abs((minX+maxX)/2+b[0]-size/2)-Math.abs((minY+maxY)/2+b[1]-size/2));
   for(const[dx,dy]of moves){
    if(boxes.some(b=>b.minX+dx+b.minY+dy<27)||paths.some(v=>v[0]+dx+v[1]+dy<27))continue;
    const next=M.translatePlan(clean,dx,dy),shell=C.project('compact',size,size);next.size=size;next.depth=size;next.height=Math.max(32,M.height(clean));next.design={...shell.design,packs,ledColor:source.design?.ledColor||shell.design.ledColor};
    next.floors=M.clone(clean.floors?.length?clean.floors:shell.floors).map(f=>({...f,profile:'solid',material:'polished',thickness:1,color:'#7d8588'}));next.design.studyFloors=next.floors.map(f=>({z:f.z,cells:[] }));
    for(const row of next.design.studyFloors)for(let x=0;x<size/8;x++)for(let y=0;y<size/8;y++)row.cells.push([x,y]);
    try{const L=node?require('./creation-living'):root.CreationLiving,ready=L.plan(next);M.read(ready);if(!M.problems(ready).length)return ready;}catch{}
   }
  }
  throw new Error('Compact : cette implantation ne tient pas dans un carré de 96 m avec les dégagements intérieurs. Réorganisez la production sur un niveau. Le projet est conservé.');
 }
 function apply(source,family,packs){const node=typeof module!=='undefined'&&module.exports,L=node?require('./creation-living'):root.CreationLiving;const next=fit(source,family,packs);return next.nativeProfile==='clean-manifold-v1'?next:next.objects.length&&!next.design?.living?L.plan(next):next;}

 function fitManifold(source,family,packs){
  const node=typeof module!=='undefined'&&module.exports,M=node?require('./workshop-model'):root.WorkshopModel,D=node?require('./workshop-design'):root.WorkshopDesign,C=node?require('./design-campus'):root.DesignCampus,L=node?require('./creation-living'):root.CreationLiving;
  if(family!=='compact')throw new Error('Ce premier aménagement avec contrôle surélevé est prêt pour la création Compact. Le layout aéré reste disponible sans habillage.');
  const clean=M.clone(source),old=clean.manifoldPlacement||{x:0,y:0,width:clean.size,depth:M.depth(clean)},width=old.width,depth=old.depth,size=[64,80,96].find(n=>n>=width+24&&n>=depth+24&&n>=(source.manifoldSite?.size||0));
  if(!size)throw new Error('Le manifold conserve ses dégagements : cette création doit être plus grande pour le recevoir.');
  const next=M.translatePlan(clean,8-old.x,16-old.y),shell=C.project('compact',size,size);next.size=next.depth=size;next.height=Math.max(32,M.height(clean));next.manifoldPlacement={x:8,y:16,width,depth};next.design={...shell.design,packs,ledColor:source.design?.ledColor||shell.design.ledColor,studyFitted:true};delete next.design.living;
  next.floors=[{z:0,thickness:1,material:'polished',color:'#aeb7b7',shaft:2,profile:'solid',role:'technical'},{z:5,thickness:1,material:'polished',color:'#aeb7b7',shaft:2,profile:'solid',role:'production'}];next.design.studyFloors=next.floors.map(f=>({z:f.z,cells:[]}));
  for(let x=0;x<size/8;x++)for(let y=0;y<size/8;y++)next.design.studyFloors[0].cells.push([x,y]);
  for(let x=1;x<1+width/8;x++)for(let y=2;y<2+depth/8;y++)if(x!==1||y>=5)next.design.studyFloors[1].cells.push([x,y]);
  // The original façade and its real wall lighting are preserved. The service
  // room is placed behind the entrance and does not touch the outer glazing.
  const baseParts=(clean.manifoldInterior.baseParts||clean.manifoldInterior.parts).map(q=>{const r=M.clone(q);if(!clean.manifoldInterior.baseParts&&(old.x||old.y)){r.x-=old.x;r.y-=old.y;for(const k of ['start','end','walkStart','walkEnd'])if(r[k]){r[k][0]-=old.x;r[k][1]-=old.y;}}return r;});
  let lighting=M.clone(source.manifoldSite?.lighting||source.manifoldExteriorLighting||[]);
  if(!lighting.length){const proto=baseParts.filter(q=>q.livingCircuit),walls=D.envelope(shell),mounts=L.wallMounts(walls,next,14),selected=[];for(const m of mounts){if(selected.some(a=>Math.hypot(a.position[0]-m.position[0],a.position[1]-m.position[1])<12))continue;const lower=L.wallMounts(walls,next,11.9).find(a=>Math.hypot(a.position[0]-m.position[0],a.position[1]-m.position[1])<.01);if(!lower)continue;for(const [asset,z,mount]of[['PowerPoleWall',11.9,lower],['FloodlightWall',14,m]]){const q=M.clone(proto.find(q=>q.asset===asset)),a=m.rotation*Math.PI/360;Object.assign(q,{x:mount.position[0],y:mount.position[1],z,rotation:m.rotation,quat:[0,0,Math.sin(a),Math.cos(a)],livingCircuit:'clean-exterior-'+selected.length});lighting.push(q);}selected.push(m);if(selected.length===8)break;}}
  next.manifoldExteriorLighting=lighting;let parts=[];
  for(const q0 of baseParts){const q=M.clone(q0);if(q.livingCircuit||q.name.startsWith('Lumière ·')||q.name==='Machines · plafond technique')continue;if(q.x===4&&q.asset==='Foundation_ConcretePolished_8x1'&&q.y<=20)continue;if(q.x===8.2&&q.y<=20)continue;if(q.x===4&&Math.abs(q.y-.15)<.01)continue;q.x+=8;q.y+=16;for(const k of ['walkStart','walkEnd','start','end'])if(q[k]){q[k][0]+=8;q[k][1]+=16;}parts.push(q);}
  parts.push(...M.clone(lighting),...M.clone(clean.manifoldInterior.entryParts));next.manifoldInterior={...clean.manifoldInterior,parts};
  next.objects=next.objects.filter(o=>!o.id.startsWith('mf-light-')&&!o.native?.lightingFeed);const ids=new Set(next.objects.map(o=>o.id));next.links=next.links.filter(l=>ids.has(l.from)&&ids.has(l.to));const sockets=next.objects.filter(o=>o.native?.ceilingMounted),prototype=sockets[0];let previous=sockets.at(-1).id;
  for(const[i,q]of lighting.filter(q=>q.asset==='PowerPoleWall').entries()){const a=q.rotation*Math.PI/180,o={...M.clone(prototype),id:'mf-light-'+i,x:q.x+.8*Math.cos(a),y:q.y+.8*Math.sin(a)};o.native.lightingFeed=true;next.objects.push(o);next.links.push({kind:'power',from:previous,to:o.id});previous=o.id;}
  M.read(next);D.envelope(next);return next;
 }

 function fit(source,family,packs){
  if(source.nativeProfile==='clean-manifold-v1')return fitManifold(source,family,packs);
  if(family==='compact')return fitCompact(source,packs);
  const D=typeof module!=='undefined'&&module.exports?require('./workshop-design'):root.WorkshopDesign,M=typeof module!=='undefined'&&module.exports?require('./workshop-model'):root.WorkshopModel;
  if(!D.PRESETS[family]?.nativeStudy)throw new Error('Création inconnue.');
  const clean=M.clone(source);clean.design=clean.design||{};(typeof module!=='undefined'&&module.exports?require('./creation-living'):root.CreationLiving).restorePower(clean);delete clean.design.living;delete clean.design.studyFloors;delete clean.design.studyFitted;
  const design=D.preset(family,{...clean.design,studyHeightMode:['atlas','sylva'].includes(family)?'auto':clean.design.studyHeightMode,packs}),boxes=clean.objects.map(M.bounds);
  if(!boxes.length)throw new Error('Ajoutez la production avant d’appliquer une création.');
  const paths=D.accessPaths(clean),points=paths.flat(),minX=Math.min(...boxes.map(b=>b.minX),...points.map(p=>p[0])),maxX=Math.max(...boxes.map(b=>b.maxX),...points.map(p=>p[0])),minY=Math.min(...boxes.map(b=>b.minY),...points.map(p=>p[1])),maxY=Math.max(...boxes.map(b=>b.maxY),...points.map(p=>p[1]));
  // Keep the production assembly rigid. Native spans/ports stay local to their machines.
  const formats=[];for(let w=64;w<=96;w+=8)for(let d=48;d<=80;d+=8)if(w>=maxX-minX+8&&d>=maxY-minY+8)formats.push([w,d]);formats.sort((a,b)=>a[0]*a[1]-b[0]*b[1]||a[0]-b[0]);
  const baseFloors=(clean.floors||[]).map(f=>({z:f.z,cells:D.floorCells({...clean,design:{...clean.design,enabled:false,fit:'occupied',facadeForm:'flat'}},f)}));
  const bounds=q=>q.signatureBounds||[[q.x-(q.rotation%180?q.d:q.w)/2,q.x+(q.rotation%180?q.d:q.w)/2],[q.y-(q.rotation%180?q.w:q.d)/2,q.y+(q.rotation%180?q.w:q.d)/2],[q.z,q.z+q.h]],overlap=(a,b)=>a.every((r,i)=>Math.min(r[1],b[i][1])-Math.max(r[0],b[i][0])>.05);
  for(const [size,depth]of formats){
   const shell={...clean,size,depth,height:Math.max(32,M.height(clean),8*Math.ceil((Math.max(0,...clean.objects.map(o=>(o.z||0)+(o.h||6)))+16)/8)),objects:[],links:[],floors:[{z:0,thickness:1}],design:{...design,studyHeightTop:Math.max(0,...clean.objects.map(o=>(o.z||0)+(o.h||6)))}},parts=D.envelope(shell),solid=parts.filter(q=>q.component!=='module'||q.signatureBounds).map(bounds),roofs=parts.filter(q=>q.studyLayer==='roof').map(bounds);
   const moves=[];for(let dx=Math.ceil((4-minX)/8)*8;dx<=size-4-maxX;dx+=8)for(let dy=Math.ceil((4-minY)/8)*8;dy<=depth-4-maxY;dy+=8)moves.push([dx,dy]);moves.sort((a,b)=>Math.abs(a[0])+Math.abs(a[1])-Math.abs(b[0])-Math.abs(b[1]));
   for(const [dx,dy]of moves){
    const next=M.translatePlan(clean,dx,dy);Object.assign(next,{size,depth,height:shell.height});next.design={...design,studyFitted:true,fit:'occupied',studyFloors:[]};
    // A machine must be below the actual roof, including the low wings and slopes.
    if(next.objects.some(o=>!['port','pole','wallPole'].includes(o.type)&&!roofs.some(b=>o.x>=b[0][0]&&o.x<=b[0][1]&&o.y>=b[1][0]&&o.y<=b[1][1]&&(o.z||0)+(o.h||6)<=b[2][1]+.05)))continue;
    try{D.envelope(next);}catch{continue;}
    let supported=true;
    for(const f of next.floors||[]){
     const cells=baseFloors.find(row=>row.z===f.z).cells.map(([x,y])=>[x+dx/8,y+dy/8]).filter(([x,y])=>x>=0&&y>=0&&x<size/8&&y<depth/8&&!solid.some(b=>overlap([[x*8,x*8+8],[y*8,y*8+8],[f.z,f.z+f.thickness]],b)));
     const keys=new Set(cells.map(c=>c.join(',')));
     for(const o of next.objects.filter(o=>Math.abs((o.z||0)-f.z-f.thickness)<.1&&o.type!=='lift')){const b=M.bounds(o);for(let x=Math.floor((b.minX+.01)/8);x<=Math.floor((b.maxX-.01)/8);x++)for(let y=Math.floor((b.minY+.01)/8);y<=Math.floor((b.maxY-.01)/8);y++)if(!keys.has(x+','+y))supported=false;}
     next.design.studyFloors.push({z:f.z,cells});
    }
    if(!supported)continue;
    try{D.envelope(next);M.read(next);if(M.problems(next).length)continue;return next;}catch{}
   }
  }
  throw new Error('Cette production ne tient pas sous les volumes de '+D.PRESETS[family].name+' (jusqu’à 96 × 80 m). Réduisez l’emprise ou les étages, ou choisissez une création plus haute. Le projet est conservé.');
 }
 async function reflow(source,family,packs,data,storeys='single'){
  const node=typeof module!=='undefined'&&module.exports,D=node?require('./workshop-design'):root.WorkshopDesign,M=node?require('./workshop-model'):root.WorkshopModel,P=node?require('./workshop-planning'):root.WorkshopPlanning;
  
  const totals=p=>{const result={};for(const o of p.objects)if(o.recipe)result[o.recipe]=(result[o.recipe]||0)+(o.clock??1);return result;},before=totals(source);
  if(source.nativeProfile){
   if((source.nativeProfile!=='iron-plates-blocks-flat-v1'&&!(family==='compact'&&source.nativeProfile==='iron-plates-pairs-v1'))||storeys!=='single')throw new Error('Cette réorganisation conserve les blocs natifs sur un seul niveau. Choisissez 1 étage.');
   const body={...source.flows,options:{layoutStyle:'spacious',pitch:'minimum',floorProfile:'solid',beltPolicy:source.nativeSettings?.beltPolicy||'fixed',storeyMode:'single',size:64,depth:64,height:32,priority:'architecture',reserveCladding:true}};
   const response=await fetch('/api/workshop/compact',{method:'POST',headers:{'Content-Type':'application/json','X-Factory-Tools':'local-viewer'},body:JSON.stringify(body)}),result=await response.json();
   if(!response.ok)throw new Error(result.error||'Réorganisation des blocs impossible.');
   const next=result.project,after=totals(next);
   if(Object.keys(before).length!==Object.keys(after).length||Object.entries(before).some(([r,c])=>Math.abs(c-(after[r]??-1))>1e-6))throw new Error('Cette chaîne personnalisée ne peut pas être réorganisée sans changer ses recettes ou cadences.');
   next.id=source.id;next.name=source.name;next.buffer=M.clone(source.buffer||[]);if(source.appearance)next.appearance=M.clone(source.appearance);
   const fitted=fit(next,family,packs);return (node?require('./creation-living'):root.CreationLiving).plan(fitted);
  }
  const clean=M.clone(source);clean.design={...D.settings(clean.design),enabled:false};delete clean.design.studyFitted;delete clean.design.living;delete clean.design.studyFloors;
  for(const [size,depth]of [[48,48],[48,64],[56,64],[64,64]]){
   let next;try{next=await P.build({data,flows:source.flows,source:clean,id:source.id,structure:source.structure,reserved:[[[24,28],[4,depth-4]]],dimensions:{size,depth,height:Math.max(32,M.height(source))},generation:{...source.generation,layoutStyle:'spacious',storeyMode:storeys==='single'?'single':'limited',maxStoreys:storeys==='single'?1:Number(storeys),reserveCladding:false,floorProfile:'solid',shape:'rectangle',priority:'production'}});}catch{continue;}
   const after=totals(next);if(Object.keys(before).length!==Object.keys(after).length||Object.entries(before).some(([recipe,clock])=>Math.abs(clock-(after[recipe]??-1))>1e-6))continue;
   try{return (node?require('./creation-living'):root.CreationLiving).plan(fit(next,family,packs));}catch{}
  }
  throw new Error('Aucune implantation compatible trouvée pour cette création avec les mêmes recettes et débits. Le projet est conservé.');
 }
 const api={fit,reflow,apply,fitCompact,detach};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.CreationFitting=api;
})(typeof globalThis!=='undefined'?globalThis:this);
