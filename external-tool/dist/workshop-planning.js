'use strict';
(function(root){
 const node=typeof module!=='undefined'&&module.exports,M=node?require('./workshop-model.js'):root.WorkshopModel,A=node?require('./workshop-assist.js'):root.WorkshopAssist,D=node?require('./workshop-design.js'):root.WorkshopDesign;
 function estimate(flows,data,g){const work=A.demand(flows,data).work,recipes=A.demand(flows,data).byOutput;let area=0,count=0;const gap={compact:2,balanced:4,spacious:8}[g.layoutStyle];for(const[id,cycles]of work){const r=recipes.get(id),n=Math.ceil(cycles*r.seconds/60-1e-8),t=M.TYPES[r.type];area+=n*(t.w+gap+3)*(t.d+gap+5);count+=n;}return{area,count};}
 function candidates(flows,data,g,fixed){
  if(fixed)return[{size:fixed.size,depth:fixed.depth??fixed.size,height:fixed.height??fixed.size}];
  const {area,count}=estimate(flows,data,g),floors=g.storeyMode==='single'?1:g.storeyMode==='vertical'?Math.min(g.maxStoreys,Math.max(2,Math.ceil(count/4))):Math.min(3,Math.max(1,Math.ceil(count/7))),ratio=g.shape==='elongated'?2:1,extra=g.shape==='exotic'?1.5:1;
  const height=Math.max(compactCase(flows,g)?48:32,Math.ceil((floors*14+4)/8)*8),side=Math.max(g.shape==='exotic'?64:g.layoutStyle==='compact'?32:40,Math.ceil(Math.sqrt(area*extra/floors/ratio)/8)*8),rows=[];
  if(g.shape==='rectangle'&&(g.layoutStyle==='compact'||compactCase(flows,g)))for(const size of[32,40,48,56,64])rows.push({size,depth:size,height});
  for(let i=0;i<4;i++){const depth=Math.min(256,side+i*8),size=Math.min(512,depth*ratio);rows.push({size,depth,height});}return rows;
 }
 function compactCase(flows,g){return g.layoutStyle==='compact'&&g.shape==='rectangle'&&(g.storeyMode==='single'?flows.outputs[0]?.rate<=5:g.maxStoreys>=3)&&flows.inputs.length===1&&flows.inputs[0].id==='Desc_OreIron_C'&&flows.outputs.length===1&&flows.outputs[0].id==='Desc_IronPlateReinforced_C'&&flows.outputs[0].rate>=.2&&flows.outputs[0].rate<=10&&Math.abs(flows.inputs[0].rate-12*flows.outputs[0].rate)<1e-6;}
 function describe(p){const n=p.floors?.filter(f=>f.role!=='technical').length||1,top=Math.max(0,...p.objects.map(o=>(o.z||0)+(o.h||6))),width=p.size,depth=M.depth(p);return`${width/8} × ${depth/8} fondations · ${width} × ${depth} m · ${n} étage${n>1?'s':''}${p.floors?.some(f=>f.role==='technical')?' · Logistics floor de 4 m':''}`;}
 async function build(request,{compact,manifold,progress=()=>{}}={}){
  const {data}=request,flows=A.resolveFlexible(request.flows,data),source=request.source,g=D.generation(request.generation),design=source?D.settings(source.design):g.priority==='architecture'?D.preset(g.envelopeStyle,{packs:['concrete','metal','glass']}):D.settings({enabled:false,packs:['concrete','metal','glass']});
  if(design.enabled&&design.family==='compact'){g.storeyMode='single';g.maxStoreys=1;g.shape='rectangle';}
  const unavailable=A.layoutLimit(flows,data);if(unavailable)throw new Error(unavailable);
  if(design.enabled&&design.family==='m05'&&g.shape==='exotic')throw new Error('Le M05 utilise encore une trame rectangulaire. Choisissez Rectangle ou Allongé, ou un autre style pour une forme découpée.');
  if(manifold){g.storeyMode='single';g.maxStoreys=1;g.shape='rectangle';}g.routingMargin=true;
  g.priority=g.reserveCladding?'architecture':'production';if(design.enabled&&design.family==='m05')g.maxStoreys=Math.min(g.maxStoreys,3);
  const fixed=request.dimensions||(g.sizing==='fixed'?(g.plot||(source?{size:source.size,depth:M.depth(source),height:M.height(source)}:null)):null);if(g.sizing==='fixed'&&!fixed)throw new Error('Choisissez un terrain pour le format imposé.');g.sizing=fixed?'fixed':'auto';if(fixed)g.plot=M.clone(fixed);else delete g.plot;
  const volumes=candidates(flows,data,g,fixed);if(!fixed&&source&&g.reserveCladding)volumes.push({size:source.size,depth:M.depth(source),height:Math.max(M.height(source),volumes[0].height)});if(!fixed)volumes.sort((a,b)=>a.size*a.depth-b.size*b.depth||a.height-b.height);let last;
  for(let i=0;i<volumes.length;i++){
   const volume=volumes[i];progress({attempt:i+1,total:volumes.length,label:`Recherche · ${volume.size/8} × ${volume.depth/8} fondations`});
   try{
    let next;
    if(manifold){next=await manifold({...flows,options:{...g,...volume,layoutPolicy:'simple-patterns-v1'}});}
    else {const settings={gap:4,pitch:g.pitch,thickness:1,material:'concrete',color:'#536454',...request.structure,pitch:g.pitch},result=A.calculate(flows,data,{...volume,physical:true,reserved:request.reserved,generation:{...g,floorProfile:'frame'},structure:settings});next={...M.fresh(request.id||'generated'),...volume,objects:[...result.objects,...result.logistics],links:result.links,floors:result.floors,structure:result.structure,generation:{...g,routed:true},flows:M.clone(flows)};next=A.addPoles(next,source?.powerStyle==='shared'?'shared':'per-machine');}
    next.id=request.id||next.id;next.name=source?.name||request.name||'Mon usine';next.buffer=M.clone(source?.buffer||[]);if(source?.appearance)next.appearance=M.clone(source.appearance);next.generation={...g,routed:true};
    if(next.nativeProfile==='clean-manifold-v1'&&source?.design?.enabled)next.manifoldSite={size:source.size,depth:M.depth(source),lighting:M.clone(source.design?.living?.fixtures||source.manifoldExteriorLighting||[])};
    next.design=design.enabled?D.settings({...design,fit:g.reserveCladding||g.shape==='exotic'?'plot':'occupied',footprint:g.shape==='exotic'?'l':'rectangle'}):D.settings({...design,...(g.reserveCladding?{fit:'plot'}:{}),footprint:g.shape==='exotic'?'l':'rectangle'});
    if(design.enabled&&design.family==='m05')next=D.prepareM05(next);
    if(source?.structure?.material)next.structure.material=source.structure.material;next.floors=D.floors(next,next.nativeProfile==='clean-manifold-v1'?'polished':next.structure.material,next.nativeProfile==='clean-manifold-v1'?'solid':g.floorProfile);
    if(next.nativeSettings)next.nativeSettings={...next.nativeSettings,...g};
    const ids=new Map(next.objects.map((o,i)=>[o.id,globalThis.crypto?.randomUUID?.()||'generated-'+Date.now()+'-'+i]));for(const o of next.objects)o.id=ids.get(o.id);for(const l of next.links){l.from=ids.get(l.from);l.to=ids.get(l.to);if(l.via)l.via=ids.get(l.via);}for(const side of ['input','output'])if(next.layoutInfo?.[side]?.objectId)next.layoutInfo[side].objectId=ids.get(next.layoutInfo[side].objectId);
    if(design.enabled&&D.PRESETS[design.family]?.nativeStudy){const spec=D.CATALOG.studies[D.PRESETS[design.family].nativeStudy];if(!spec.designFirst||spec.workshopCompatible)next=(node?require('./creation-fitting'):root.CreationFitting).apply(next,design.family,design.packs);}
    D.envelope(next);
    if(fixed&&(next.size!==fixed.size||M.depth(next)!==(fixed.depth??fixed.size)))throw new Error('Le style dépasse le terrain imposé.');
    if(g.reserveCladding){const probe={...next,design:D.settings({...next.design,enabled:true,fit:'plot'})},margin=3;
     const crowded=next.objects.some(o=>{const b=M.bounds(o);return b.minX<margin||b.minY<margin||b.maxX>next.size-margin||b.maxY>M.depth(next)-margin;});
     const crossed=D.accessPaths(next).some(pts=>pts.some(v=>v[0]<margin||v[1]<margin||v[0]>next.size-margin||v[1]>M.depth(next)-margin));
     if(crowded||crossed||D.openings(probe)>0)throw new Error('La réserve d’habillage ne permet pas encore des façades complètes.');
    }
    M.read(next);return next;
   }catch(error){last=error;if(fixed)break;}
  }
  const error=new Error(fixed?(g.reserveCladding?'Le terrain imposé ne permet pas cette implantation avec des façades complètes. Choisissez Auto, un terrain plus grand ou décochez la réserve d’habillage.':'Impossible de raccorder cette usine dans le terrain choisi. Repassez en dimensions automatiques.'):'Cette combinaison ne permet pas un réseau complet. Essayez Auto pour les étages ou Rectangle. Le plan actuel est conservé.');error.cause=last;throw error;
 }
 const api={estimate,candidates,compactCase,describe,build};if(node)module.exports=api;else root.WorkshopPlanning=api;
})(typeof globalThis!=='undefined'?globalThis:this);

