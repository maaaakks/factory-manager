'use strict';
(function(root){
 const nodeMode=typeof module!=='undefined'&&module.exports,M=nodeMode?require('./workshop-model.js'):root.WorkshopModel,A=nodeMode?require('./workshop-assist.js'):root.WorkshopAssist,F=nodeMode?require('./flow-core.js'):root.FactoryFlowCore;
 const machineTypes=new Set(['smelter','constructor','assembler']);
 function build(project,data,options={}){
  if(!data)throw new Error('Catalogue en cours de chargement.');
  if(project.nativeProfile)throw new Error('Ce module possède déjà son réseau natif calibré. Conservez ses raccordements.');
  const next=M.clone(project),inputs=next.objects.filter(o=>o.io?.side==='input'),outputs=next.objects.filter(o=>o.io?.side==='output');
  if(!inputs.length||!outputs.length)throw new Error('Placez au moins une Entrée et une Sortie, puis indiquez leurs ressources.');
  if([...inputs,...outputs].some(o=>!o.io.item)||inputs.some(o=>!Number.isFinite(o.io.rate)||o.io.rate<=0))throw new Error('Indiquez la ressource de chaque repère et le débit disponible de chaque entrée.');
  const machines=next.objects.filter(o=>machineTypes.has(o.type)),required=new Set(),visiting=new Set(),recipeChoices=new Map(),autoRecipes=[];
  const recipes=Object.entries(data.recipes),label=id=>data.names[id]||id;
  function discover(item){
   if(inputs.some(o=>o.io.item===item))return;
   if(visiting.has(item))throw new Error('Cycle de transformation : '+label(item)+'.');
   if(required.has(item))return;
   visiting.add(item);
   let producers=machines.filter(o=>data.recipes[o.recipe]?.outputs.some(r=>r.id===item));
   if(!producers.length){
    const choices=recipes.filter(([id,r])=>r.outputs.some(row=>row.id===item)&&machines.some(o=>!o.recipe&&o.type===r.type));
    if(choices.length!==1)throw new Error(choices.length?'Plusieurs recettes possibles pour '+label(item)+' : choisissez la recette sur la machine.':'Étape manquante pour '+label(item)+' : ajoutez une machine avec sa recette.');
    const [id,r]=choices[0],o=machines.find(o=>!o.recipe&&o.type===r.type);o.recipe=id;producers=[o];autoRecipes.push(o.id);
   }
   for(const o of producers){const r=data.recipes[o.recipe];if(r.type!==o.type)throw new Error('Recette incompatible : '+o.name);if(!recipeChoices.has(o.type))recipeChoices.set(o.type,new Set());recipeChoices.get(o.type).add(o.recipe);for(const row of r.inputs)discover(row.id);}
   visiting.delete(item);required.add(item);
  }
  for(const o of outputs)discover(o.io.item);
  // Unassigned machines can join a parallel bank only when its recipe is unambiguous.
  for(const o of machines)if(!o.recipe&&recipeChoices.get(o.type)?.size===1){o.recipe=[...recipeChoices.get(o.type)][0];autoRecipes.push(o.id);}
  const used=new Set(),groups=new Map(),walked=new Set();
  function group(item){if(!groups.has(item))groups.set(item,{item,sources:[],targets:[]});return groups.get(item);}
  function need(item,target){
   const g=group(item);if(!g.targets.some(o=>o.id===target.id))g.targets.push(target);
   const entries=inputs.filter(o=>o.io.item===item),providers=entries.length?entries:machines.filter(o=>data.recipes[o.recipe]?.outputs.some(r=>r.id===item));
   if(!providers.length)throw new Error('Aucun fournisseur pour '+label(item)+'.');
   for(const o of providers){if(!g.sources.some(x=>x.id===o.id))g.sources.push(o);if(machineTypes.has(o.type)){used.add(o.id);if(walked.has(o.id))continue;walked.add(o.id);for(const row of data.recipes[o.recipe].inputs)need(row.id,o);}}
  }
  for(const o of outputs)need(o.io.item,o);
  if(machines.some(o=>used.has(o.id)&&data.recipes[o.recipe].outputs.length!==1))throw new Error('Les recettes à plusieurs sorties nécessitent un routage explicite.');
  // Rebuild transport atomically, retaining electricity. Old generated junctions are replaceable.
  const oldGenerated=new Set(next.objects.filter(o=>/^network-(splitter|merger)-/.test(o.id)).map(o=>o.id));
  next.objects=next.objects.filter(o=>!oldGenerated.has(o.id));next.links=next.links.filter(l=>l.kind==='power'&&!oldGenerated.has(l.from)&&!oldGenerated.has(l.to));
  let serial=0,checks=0;const taken=new Set(next.objects.map(o=>o.id)),junctions=[],routeCache=new Map(),started=Date.now(),router=options.route||A.route;
  const routes=(p,from,to)=>{if(++checks>3000||Date.now()-started>1500)throw new Error('Réseau trop complexe à router rapidement. Libérez un couloir autour des machines puis réessayez.');const key=next.objects.length+'|'+from+'|'+to;if(!routeCache.has(key))routeCache.set(key,router(p,from,to,[]));return routeCache.get(key);};
  const newId=type=>{let id;do{id='network-'+type+'-'+(++serial);}while(taken.has(id));taken.add(id);return id;};
  function wire(a,b,item){if((a.z||0)!==(b.z||0))throw new Error(label(item)+' : un élévateur est nécessaire entre les étages.');if(!routes(next,a.id,b.id,[]))throw new Error('Passage bloqué : '+a.name+' → '+b.name+'. Écartez ou tournez les machines.');next.links.push({kind:'belt',from:a.id,to:b.id,item,capacity:options.capacity||780});}
  function junction(type,ends,item){
   const z=ends[0].z||0;if(ends.some(o=>(o.z||0)!==z))throw new Error(label(item)+' : raccordement entre étages à prévoir.');
   const cx=ends.reduce((s,o)=>s+o.x,0)/ends.length,cy=ends.reduce((s,o)=>s+o.y,0)/ends.length,candidates=[];
   for(let x=2;x<=next.size-2;x+=2)for(let y=2;y<=M.depth(next)-2;y+=2)candidates.push({x,y,cost:Math.hypot(x-cx,y-cy)});
   candidates.sort((a,b)=>a.cost-b.cost);
   const id=newId(type);for(const pos of candidates)for(const rotation of [0,90,180,270]){const o={id,type,name:(type==='splitter'?'Répartiteur · ':'Fusion · ')+label(item),x:pos.x,y:pos.y,z,w:3,d:3,h:2,rotation,recipe:null,clock:1};if(M.candidate(next,o))continue;next.objects.push(o);const valid=ends.every((end,i)=>routes(next,type==='merger'&&i<ends.length-1||type==='splitter'&&i===0?end.id:o.id,type==='merger'&&i<ends.length-1||type==='splitter'&&i===0?o.id:end.id,[]));if(valid){junctions.push(o.id);return o;}next.objects.pop();}
   throw new Error('Pas de place pour '+(type==='splitter'?'répartir ':'fusionner ')+label(item)+'. Réservez un passage de 3 m et l’accès aux ports.');
  }
  for(const g of groups.values()){
   let source=g.sources[0];
   for(let i=1;i<g.sources.length;i++){const merger=junction('merger',[source,g.sources[i],g.targets[0]],g.item);wire(source,merger,g.item);wire(g.sources[i],merger,g.item);source=merger;}
   for(let i=0;i<g.targets.length-1;i++){const splitter=junction('splitter',[source,g.targets[i],g.targets[i+1]],g.item);wire(source,splitter,g.item);wire(splitter,g.targets[i],g.item);source=splitter;}
   wire(source,g.targets[g.targets.length-1],g.item);
  }
  if(next.objects.length+(next.buffer?.length||0)>300)throw new Error('Le réseau dépasse la limite de 300 objets.');
  for(const l of next.links)if(l.kind==='belt'&&!routes(next,l.from,l.to,[]))throw new Error('Un raccord bloque un passage déjà prévu. Libérez davantage d’espace pour le réseau.');
  for(const o of machines)if(autoRecipes.includes(o.id)&&o.name===M.TYPES[o.type].name)o.name=(M.TYPES[o.type].name+' · '+data.recipes[o.recipe].name).slice(0,80);
  const report=F.analyze(next,data,{linkAvailable:l=>!!routes(next,l.from,l.to,[])});
  if(!report.converged)throw new Error('Calcul de charge incomplet : simplifiez le réseau.');
  if(!options.capacity)for(const l of next.links)if(l.kind==='belt'){const rate=report.links.get(l)?.actual||0;l.capacity=[60,120,270,480,780].find(c=>c>=rate-1e-6)||780;}
  return {project:M.read(next),machines:used.size,junctions:junctions.length,autoRecipes: autoRecipes.length,unused:machines.filter(o=>!used.has(o.id)).length,report:F.analyze(next,data,{linkAvailable:l=>!!routes(next,l.from,l.to,[])})};
 }
 function removeTransport(project){const next=M.clone(project),lifts=new Set(next.objects.filter(o=>o.type==='lift').map(o=>o.id));next.objects=next.objects.filter(o=>!lifts.has(o.id));next.links=next.links.filter(l=>l.kind==='power'&&!lifts.has(l.from)&&!lifts.has(l.to));return M.read(next);}
 const api={build,removeTransport};if(nodeMode)module.exports=api;else root.WorkshopNetwork=api;
})(typeof globalThis!=='undefined'?globalThis:this);
