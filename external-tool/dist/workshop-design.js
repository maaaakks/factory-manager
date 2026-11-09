'use strict';
(function(root){
 const STYLES={
  concrete:{name:'Atelier béton',description:'Socle massif, angles renforcés et fenêtres espacées.',packs:['concrete'],wall:'#a0a49e',trim:'#656e69',windowEvery:3},
  ficsit:{name:'Industriel FICSIT',description:'Bardage sombre, cadres orange et bandeaux réguliers.',packs:['concrete','metal'],wall:'#48545a',trim:'#e9a043',windowEvery:4},
  glass:{name:'Verrière',description:'Travées vitrées et ossature métallique apparente.',packs:['metal','glass'],wall:'#607e89',trim:'#b1bfc3',windowEvery:1}
 };
 const CATALOG=typeof module!=='undefined'&&module.exports?require('./architecture-catalog.js'):root.ArchitectureCatalog;
 const M05=typeof module!=='undefined'&&module.exports?require('./m05-modules.js'):root.M05Modules;
 const Surfaces=typeof module!=='undefined'&&module.exports?require('./architecture-surfaces.js'):root.ArchitectureSurfaces,Kit=typeof module!=='undefined'&&module.exports?require('./m05-kit.js'):root.M05Kit;
 const Signature=typeof module!=='undefined'&&module.exports?require('./signature-design.js'):root.SignatureDesign;
 const PRESETS=CATALOG.families,PALETTES=CATALOG.palettes,GROUPS=CATALOG.groups;
 function presetAvailable(id,packs){const p=PRESETS[id];return !!p&&(id==='classics'?p.variants.some(k=>presetAvailable(k,packs)):available(p.style,packs));}
 function preset(id,value={},variant=1){
  const p=PRESETS[id];if(!p)throw new Error('Design inconnu.');const current=settings(value);
  if(!Number.isInteger(variant)||variant<1||variant>999)throw new Error('Variation invalide.');
  if(id==='classics'){const choices=p.variants.filter(k=>presetAvailable(k,current.packs));if(!choices.length)throw new Error('Ce design utilise un pack non débloqué.');const source=preset(choices[(variant-1)%choices.length],current,1+Math.floor((variant-1)/choices.length)%90);return settings({...source,family:id,variant,seed:variant,roofSeed:variant});}
  if(!presetAvailable(id,current.packs))throw new Error('Ce design utilise un pack non débloqué.');
  if(!Number.isInteger(variant)||variant<1||variant>999)throw new Error('Variation invalide.');
  const {name,description,group,patterns,layouts,palettes,entryTreatments,footprints,roofForms,facadeForms,hidden,variants,...options}=p,n=variant-1;
  return settings({...current,...options,enabled:true,roof:true,footprint:footprints?.[n%footprints.length]||p.footprint,roofForm:roofForms?.[n%roofForms.length]||p.roofForm,facadeForm:facadeForms?.[n%facadeForms.length]||p.facadeForm||'flat',family:id,variant,seed:variant,roofSeed:variant,windowEvery:0,pattern:patterns[n%patterns.length],roofLayout:layouts[n%layouts.length],palette:palettes[Math.floor(n/3)%palettes.length],entryTreatment:entryTreatments[Math.floor(n/2)%entryTreatments.length],entrance:'auto',cornerWidth:['compact','signature'].includes(id)?0:.5,...(id==='signature'?{palette:['signature-chalk','signature-slate','signature-oxide'][n%3],colors:current.family==='signature'?current.colors:Object.fromEntries(Object.entries(current.colors).filter(([k])=>!['walls','frames','windows','roofs'].includes(k)))}:{})});
 }
 function vary(value){const d=settings(value);if(d.family==='custom')throw new Error('Choisissez une famille de style avant de créer une variation.');if(PRESETS[d.family]?.nativeStudy)throw new Error('Cette étude possède une composition fixe.');return {...preset(d.family,d,d.variant%(d.family==='signature'?3:999)+1),entrance:d.entrance,roof:d.roof};}
 function windowAt(d,style,start,side,z,top,h,size){
  if(h!==4||d.windowEvery===99||z===0&&!(d.family!=='custom'&&top<=12&&d.style!=='concrete'))return false;
  if(d.family==='signature'&&!d.windowEvery)return Signature.windowAt(start,side,z,top,size,d.seed);
  if(d.family==='m05-kit'&&!d.windowEvery)return Kit.windowAt(start,side,z,top,size,d.seed);
  if(d.family==='warehouse'&&d.facadeForm!=='flat'&&!d.windowEvery){const bay=Math.floor(start/8),n=size/8;return z>=top-4||(z>=8&&z<top-8&&[1,n-2].includes(bay));}
  if(d.windowEvery||d.pattern==='classic')return(start/8+side+d.seed)%(d.windowEvery||style.windowEvery)===0;
  const bay=Math.floor(start/8),distance=Math.min(bay,size/8-1-bay),row=Math.floor(z/4);
  if(d.pattern==='paired')return(distance+Math.floor((d.seed-1)/2))%3!==2;
  if(d.pattern==='ribbon')return row%3===Math.min(1+d.seed%2,Math.max(1,Math.floor((top-4)/4)));
  if(d.pattern==='alternating')return(distance+row+d.seed)%2===0;
  if(d.pattern==='upper')return z+h>=top-4;
  return d.pattern==='full';
 }
 const DEFAULTS={shape:'rectangle',sizing:'auto',layoutStyle:'compact',pitch:'minimum',floorProfile:'factory',beltPolicy:'auto',priority:'production',envelopeStyle:'classics'};
 function generation(value={}){const v={...DEFAULTS,storeyMode:'auto',maxStoreys:3,...value};if(!['rectangle','elongated','exotic'].includes(v.shape)||!['auto','fixed'].includes(v.sizing)||!['production','architecture'].includes(v.priority)||!Object.hasOwn(PRESETS,v.envelopeStyle)||!['auto','vertical','single','limited'].includes(v.storeyMode)||!Number.isInteger(v.maxStoreys)||v.maxStoreys<1||v.maxStoreys>64)throw new Error('Préférence d’étages invalide.');v.reserveCladding=value.reserveCladding??(v.layoutStyle==='spacious'||v.priority==='architecture'&&v.layoutStyle!=='compact');if(typeof v.reserveCladding!=='boolean'||v.plot!==undefined&&(!Number.isInteger(v.plot.size)||v.plot.size<8||v.plot.size>512||v.plot.size%8||!Number.isInteger(v.plot.depth??v.plot.size)||(v.plot.depth??v.plot.size)<8||(v.plot.depth??v.plot.size)>512||(v.plot.depth??v.plot.size)%8))throw new Error('Terrain ou réserve pour l’habillage invalide.');if(!['compact','balanced','spacious'].includes(v.layoutStyle)||!['minimum',8,10,12,16].includes(v.pitch)||!['frame','factory','solid'].includes(v.floorProfile)||!['auto','fixed'].includes(v.beltPolicy))throw new Error('Options de génération invalides.');return v;}
 function settings(value={}){const v={fit:'plot',facadeForm:value.family==='warehouse'?'warehouse':'flat',enabled:false,style:'concrete',family:'custom',variant:1,palette:'default',pattern:'classic',structure:'none',entryTreatment:'frame',seed:1,roofSeed:1,roofForm:'auto',roofLayout:'auto',wallDecoration:'frames',footprint:'rectangle',entrance:'auto',roof:true,roofStyle:'tar',detail:'bands',windowEvery:0,cornerWidth:.5,packs:['concrete'],colors:{},wallMaterial:'original',...value};if(!['plot','occupied'].includes(v.fit)||!['flat','warehouse','gallery','terraces','signature'].includes(v.facadeForm)||!(v.family==='custom'||Object.hasOwn(PRESETS,v.family))||!Number.isInteger(v.variant)||v.variant<1||v.variant>999||!Object.hasOwn(PALETTES,v.palette)||!['classic','paired','ribbon','alternating','upper','full'].includes(v.pattern)||!['none','grid','columns'].includes(v.structure)||!['frame','porch','double'].includes(v.entryTreatment)||!['auto','none','front','right','back','left'].includes(v.entrance)||!['auto','central','pair','quartet','triple','band','ring'].includes(v.roofLayout)||!['none','frames','braces','lattice'].includes(v.wallDecoration)||!['rectangle','stepped','l','u','cross'].includes(v.footprint)||typeof v.enabled!=='boolean'||!STYLES[v.style]||!Number.isInteger(v.seed)||v.seed<1||v.seed>999||typeof v.roof!=='boolean'||!Number.isInteger(v.roofSeed)||v.roofSeed<1||v.roofSeed>999||!['auto','flat','ridges','monitor','sawtooth'].includes(v.roofForm)||![0,1,2,3,4,99].includes(v.windowEvery)||![0,.3,.5,1,2].includes(v.cornerWidth)||!['tar','ficsit','glass','skylights'].includes(v.roofStyle)||!['none','bands'].includes(v.detail)||!Array.isArray(v.packs)||v.packs.some(x=>!['concrete','metal','glass'].includes(x))||!v.colors||typeof v.colors!=='object'||Object.entries(v.colors).some(([k,c])=>!Surfaces.categories.includes(k)||!/^#[0-9a-f]{6}$/i.test(c))||!['original','concrete','ficsit'].includes(v.wallMaterial)||(v.source!==undefined&&(!v.source||typeof v.source.name!=='string'||v.source.name.length>160||!Array.isArray(v.source.walls)||v.source.walls.length>100||v.source.walls.some(w=>!w||typeof w.type!=='string'||w.type.length>500||!Number.isInteger(w.count)||w.count<1))))throw new Error('Style architectural invalide.');validateStudyPlacement(v);validateLiving(v);return JSON.parse(JSON.stringify(v));}
 function validateStudyPlacement(d){
  if(d.studyFitted!==undefined&&typeof d.studyFitted!=='boolean')throw new Error('Adaptation de création invalide.');
  if(d.studyFloors!==undefined&&(!Array.isArray(d.studyFloors)||d.studyFloors.length>64||d.studyFloors.some(r=>!r||!Number.isFinite(r.z)||!Array.isArray(r.cells)||r.cells.length>144||r.cells.some(c=>!Array.isArray(c)||c.length!==2||c.some(v=>!Number.isInteger(v)||v<0||v>=12)))))throw new Error('Planchers de création invalides.');
 }
 function validateLiving(d){
 if(d.studyHeightMode!==undefined&&!['auto','reference'].includes(d.studyHeightMode))throw new Error('Hauteur de création invalide.');
 if(d.living?.accessParts){if(!Array.isArray(d.living.accessParts)||d.living.accessParts.length>1200||d.living.accessParts.some(q=>!q||!['CatwalkStairs','CatwalkRamp','CatwalkCross','CatwalkStraight','Wall_Door_8x4_03','Beam_Painted','Wall_Window_Thin_8x4_02','Railing_01','Wall_Window_Thin_8x4_01','Foundation_ConcretePolished_8x1','Stair_PolishedConcrete_8x2','Wall_Door_8x4_01','Roof_Tar_01'].includes(q.asset)||!['module','beam','window','wall'].includes(q.component)||!Number.isFinite(q.x)||!Number.isFinite(q.y)||!Number.isFinite(q.z)))throw new Error('Circulation intérieure invalide.');}if(d.living?.openings&&(!Array.isArray(d.living.openings)||d.living.openings.length>64||d.living.openings.some(b=>!Array.isArray(b)||b.length!==3||b.some(a=>!Array.isArray(a)||a.length!==2||a.some(n=>!Number.isFinite(n))))))throw new Error('Portes de circulation invalides.');
 if(d.living===undefined)return;const v=d.living,vector=q=>Array.isArray(q)&&q.length===3&&q.every(n=>Number.isFinite(n)&&n>=0&&n<=512);
 if(!v||v.version!==1||!v.palette||['floor','lane','pad','frame','light'].some(k=>!/^#[a-f0-9]{6}$/i.test(v.palette[k]))||!Array.isArray(v.levels)||v.levels.length>64||v.levels.some(l=>!Number.isFinite(l.z)||!Array.isArray(l.paths)||l.paths.length>4000||l.paths.some(q=>!vector(q))||!Array.isArray(l.stations)||l.stations.some(s=>!s||typeof s.name!=='string'||!vector(s.point))||!Array.isArray(l.missing))||!Array.isArray(v.fixtures)||v.fixtures.length>128||v.fixtures.some(q=>!q||q.component!=='module'||!['FloodlightWall','PowerPoleWall'].includes(q.asset)||!vector([q.x,q.y,q.z])||!['sourceModule','name','livingCircuit'].every(k=>typeof q[k]==='string')||!Number.isInteger(q.sourceIndex)||!Array.isArray(q.quat)||q.quat.length!==4||q.quat.some(n=>!Number.isFinite(n))||Math.abs(q.quat.reduce((s,n)=>s+n*n,0)-1)>1e-5||!/^#[a-f0-9]{6}$/i.test(q.color)))throw new Error('Aménagement intérieur invalide.');
 }
 function prepareM05(p){
  const M=typeof module!=='undefined'&&module.exports?require('./workshop-model.js'):root.WorkshopModel;let next=M.clone(p);const boxes=next.objects.map(M.bounds),span=axis=>boxes.length?Math.max(...boxes.map(b=>b['max'+axis]))-Math.min(...boxes.map(b=>b['min'+axis])):0;const size=Math.max(next.size,80,Math.ceil((span('X')+60)/40)*40),depth=Math.max(M.depth(next),80,Math.ceil((span('Y')+60)/40)*40);next=M.resize(next,{size,depth,height:Math.max(48,M.height(next))});next=M.centerPlan(next);next.design={...next.design,fit:'plot'};if(next.generation)next.generation={...next.generation,shape:'rectangle'};if(next.nativeSettings)next.nativeSettings={...next.nativeSettings,shape:'rectangle'};return next;
 }
 function reserveArchitecture(p){
  if(p.design?.family==='m05')return prepareM05(p);
  const M=typeof module!=='undefined'&&module.exports?require('./workshop-model.js'):root.WorkshopModel;
  let next=M.centerPlan(p);for(;;){if(openings(next)===0)return next;if(M.freeFormat(next)){const w=Math.min(512,next.size+8),d=Math.min(512,M.depth(next)+8);if(w===next.size&&d===M.depth(next))throw new Error('La limite technique de 512 m est atteinte. Dégagez les façades.');next=M.resize(next,{size:w,depth:d,height:M.height(next)});}else{const size=M.FORMATS.find(s=>s>next.size);if(!size)throw new Error('L’habillage manque encore de place en 6 × 6. Réduisez la chaîne ou passez en dimensions libres.');next=M.resize(next,size);}}
 }
 function architectureStyle(value={}){const d=settings(value);return {...STYLES[d.style],...PALETTES[d.palette]};}
 function available(style,packs){return STYLES[style].packs.every(p=>packs.includes(p));}
 function category(o){return ['smelter','constructor','assembler'].includes(o.type)?'machines':['pole','wallPole'].includes(o.type)?'power':'logistics';}
 function color(p,o){return p.design?.colors?.[category(o)]||(p.appearance?.enabled?p.appearance.color:null);}
 // Roof glazing is composed in groups, never sampled independently per tile.
 function roofComposition(size,seed,layout='auto',available=null,depth=size){
  if(depth!==size){const nx=size/8,ny=depth/8,n=Math.min(nx,ny),base=roofComposition(n*8,seed,layout),cells=new Set();for(const k of base.cells){const [x,y]=k.split(',').map(Number);cells.add(Math.round(x*(nx-1)/Math.max(1,n-1))+','+Math.round(y*(ny-1)/Math.max(1,n-1)));}if(base.kind==='band'){cells.clear();const a=Math.floor((nx-1)/2),b=Math.ceil((nx-1)/2);for(let y=0;y<ny;y++)for(let x=a;x<=b;x++)cells.add(x+','+y);}return {...base,cells:[...cells].sort()};}
  const n=size/8,names=['central','pair','quartet','triple','band','ring'],kind=layout==='auto'?names[(seed-1)%names.length]:layout,large=Math.floor((seed-1)/6)%2===1,turn=Math.floor((seed-1)/12)%2===1,cells=new Set(),put=(x,y)=>{if(turn)[x,y]=[y,x];if(x>=0&&y>=0&&x<n&&y<n)cells.add(x+','+y);},rect=(x,y,w,h)=>{for(let i=x;i<x+w;i++)for(let j=y;j<y+h;j++)put(i,j);},span=Math.min(n-2,n%2?(large?3:1):(large?4:2)),lo=(n-span)/2,mid=n%2?[Math.floor(n/2)]:[n/2-1,n/2];
  if(kind==='central')rect(lo,lo,span,span);
  if(kind==='pair')for(const x of [0,n-1])rect(x,lo,1,span);
  if(kind==='quartet'){const w=large&&n>=6?2:1;for(const x of [0,n-w])for(const y of [0,n-w])rect(x,y,w,w);}
  if(kind==='triple'){if(n>=5){for(const x of [0,...mid,n-1])rect(x,lo,1,span);}else{for(const x of mid)put(x,0);put(0,n-1);put(n-1,n-1);}}
  if(kind==='band')rect(lo,0,span,n);
  if(kind==='ring'){const w=n>=5?n-2:n;const a=(n-w)/2;for(let x=a;x<a+w;x++)for(let y=a;y<a+w;y++)if(x===a||y===a||x===a+w-1||y===a+w-1)put(x,y);}
  if(available&&[...cells].some(k=>!available.has(k)))return roofComposition(size,seed,'central');
  return {kind,label:{central:'Puits central',pair:'Deux verrières symétriques',quartet:'Quatre puits symétriques',triple:n>=5?'Trois puits alignés':'Trois puits en triangle',band:'Verrière longitudinale',ring:'Couronne vitrée'}[kind],cells:[...cells].sort(),large,turn};
 }
 function footprint(p,d=settings(p.design)){
  if(p.generation?.shape==='exotic')d={...d,footprint:'l',fit:'plot'};
  let nx=p.size/8,ny=(p.depth??p.size)/8;const cells=new Set();for(let x=0;x<nx;x++)for(let y=0;y<ny;y++)cells.add(x+','+y);
  const paths=accessPaths(p);
  if(d.fit==='occupied'&&p.objects.length){
   const used=new Set(),mark=(x0,y0,x1,y1)=>{for(let x=Math.max(0,Math.floor((x0-4)/8));x<=Math.min(nx-1,Math.floor((x1+4-1e-7)/8));x++)for(let y=Math.max(0,Math.floor((y0-4)/8));y<=Math.min(ny-1,Math.floor((y1+4-1e-7)/8));y++)used.add(x+','+y);};
   for(const o of p.objects){const r=o.rotation%180,w=r?o.d:o.w,depth=r?o.w:o.d;mark(o.x-w/2,o.y-depth/2,o.x+w/2,o.y+depth/2);}
   for(const pts of paths)for(let i=0;i<pts.length;i++){const a=pts[Math.max(0,i-1)],b=pts[i];mark(Math.min(a[0],b[0]),Math.min(a[1],b[1]),Math.max(a[0],b[0]),Math.max(a[1],b[1]));}
   // Fill enclosed courtyards, while retaining genuine external recesses.
   const outside=new Set(),queue=[];for(const k of cells){const [x,y]=k.split(',').map(Number);if((x===0||y===0||x===nx-1||y===ny-1)&&!used.has(k)){outside.add(k);queue.push([x,y]);}}
   for(let i=0;i<queue.length;i++){const [x,y]=queue[i];for(const [dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]]){const xx=x+dx,yy=y+dy,k=xx+','+yy;if(xx>=0&&yy>=0&&xx<nx&&yy<ny&&!used.has(k)&&!outside.has(k)){outside.add(k);queue.push([xx,yy]);}}}
   for(const k of [...cells])if(outside.has(k))cells.delete(k);
  }
  const xs=[...cells].map(k=>Number(k.split(',')[0])),ys=[...cells].map(k=>Number(k.split(',')[1])),offsetX=d.fit==='occupied'?Math.min(...xs):0,offsetY=d.fit==='occupied'?Math.min(...ys):0;if(d.fit==='occupied'){nx=Math.max(...xs)-offsetX+1;ny=Math.max(...ys)-offsetY+1;}
  const turn=d.footprint==='stepped'||p.generation?.shape==='exotic'?0:Math.floor((d.variant-1)/3)%4;
  const rotate=(x,y)=>{if(nx===ny){for(let i=0;i<turn;i++)[x,y]=[nx-1-y,x];}else{if(turn===1||turn===2)x=nx-1-x;if(turn===2||turn===3)y=ny-1-y;}return[x+offsetX,y+offsetY];};
  const cut=(x,y)=>nx<3||ny<3?false:d.footprint==='stepped'?(x===0||x===nx-1)&&(y===0||y===ny-1):d.footprint==='l'?x>=Math.ceil(nx/2)&&y<Math.ceil(ny/2):d.footprint==='u'?x>=Math.floor(nx/3)&&x<nx-Math.floor(nx/3)&&y<Math.max(1,Math.floor(ny/3)):d.footprint==='cross'?(x<Math.floor(nx/3)||x>=nx-Math.floor(nx/3))&&(y<Math.floor(ny/3)||y>=ny-Math.floor(ny/3)):false;
  for(let xx=0;xx<nx;xx++)for(let yy=0;yy<ny;yy++){if(!cut(xx,yy))continue;const [x,y]=rotate(xx,yy),occupied=p.objects.some(o=>{const rotated=(o.rotation||0)%180,w=(rotated?o.d:o.w)/2+1,depth=(rotated?o.w:o.d)/2+1;return o.x+w>x*8&&o.x-w<(x+1)*8&&o.y+depth>y*8&&o.y-depth<(y+1)*8;});
   const crossed=paths.some(pts=>pts.some((b,i)=>{const a=pts[Math.max(0,i-1)];return Math.max(a[0],b[0])>x*8-1&&Math.min(a[0],b[0])<(x+1)*8+1&&Math.max(a[1],b[1])>y*8-1&&Math.min(a[1],b[1])<(y+1)*8+1;}));
   if(!occupied&&!crossed)cells.delete(x+','+y);
  }return cells;
 }

 function openingGroups(panels){
  const seen=new Set(),groups=[];
  for(let i=0;i<panels.length;i++){
   if(seen.has(i))continue;const q=[i],g=[];seen.add(i);
   for(let k=0;k<q.length;k++){
    const a=panels[q[k]];g.push(a);
    for(let j=0;j<panels.length;j++){
     if(seen.has(j))continue;const b=panels[j];
     const horizontal=(Math.abs(a.u+8-b.u)<.01||Math.abs(b.u+8-a.u)<.01)&&Math.min(a.z+a.h,b.z+b.h)>Math.max(a.z,b.z);
     const vertical=a.u===b.u&&(Math.abs(a.z+a.h-b.z)<.01||Math.abs(b.z+b.h-a.z)<.01);
     if(a.side===b.side&&a.line===b.line&&(horizontal||vertical)){seen.add(j);q.push(j);}
    }
   }
   groups.push({side:g[0].side,line:g[0].line,start:Math.min(...g.map(a=>a.u)),end:Math.max(...g.map(a=>a.u+8)),bottom:Math.min(...g.map(a=>a.z)),top:Math.max(...g.map(a=>a.z+a.h))});
  }
  return groups;
 }
 // Access is separate from material input/output: a clear 8 x 4 x 7 m bay.
 function accessPaths(p){
  const paths=[];
  for(const link of p.links||[]){
   if(link.kind==='power')continue;
   if(link.physicalRoute){paths.push(link.physicalRoute.map(q=>[q.x,q.y,q.z]));continue;}
   const o=p.objects.find(o=>o.id===link.from);
   if(link.native&&o?.native){
    const [x,y,z,w]=o.native.quaternion,angle=(o.rotation-o.native.rotation)*Math.PI/180,c=Math.cos(angle),s=Math.sin(angle),point=v=>{const [a,b,d]=v,r=[(1-2*y*y-2*z*z)*a+(2*x*y-2*z*w)*b+(2*x*z+2*y*w)*d,(2*x*y+2*z*w)*a+(1-2*x*x-2*z*z)*b+(2*y*z-2*x*w)*d,(2*x*z-2*y*w)*a+(2*y*z+2*x*w)*b+(1-2*x*x-2*y*y)*d];return[o.x+c*r[0]-s*r[1],o.y+s*r[0]+c*r[1],o.z+o.native.originZ+r[2]];},pts=[];
    for(const [a,b,ta,tb]of link.native.spans||[])for(let i=0;i<=24;i++){const t=i/24;pts.push(point(a.map((v,j)=>(2*t**3-3*t*t+1)*v+(t**3-2*t*t+t)*ta[j]+(-2*t**3+3*t*t)*b[j]+(t**3-t*t)*tb[j])));}
    if(link.native.snap&&o.native.ports[link.native.fromPort])pts.push(point(o.native.ports[link.native.fromPort]));
    if(pts.length)paths.push(pts);
   }else if(link.kind==='belt'||link.kind==='planned'){
    // An unspecified physical route cannot establish a safe access through its bounding region.
    const b=p.objects.find(o=>o.id===link.to);if(o&&b)paths.push([[o.x,o.y,o.z||0],...(link.waypoints||[]).map(q=>[q.x,q.y,q.z||0]),[b.x,b.y,b.z||0]]);
   }
  }return paths;
 }
 function entrance(p,edges,overlaps){
  const mode=p.design?.entrance??'auto';if(mode==='none')return null;
  const floor=p.floors?.find(f=>f.z===0);if(!floor||floor.holes?.length)return null;
  const base=floor.thickness||1,paths=accessPaths(p),candidates=edges.filter(e=>mode==='auto'||e.side===['front','right','back','left'].indexOf(mode)).map(e=>({...e,score:e.side*1000+Math.abs(e.start+4-(e.side%2?(p.depth??p.size):p.size)/2)})).sort((a,b)=>a.score-b.score);
  for(const e of candidates){
   const horizontal=e.side%2===0,sign=e.side===0||e.side===3?1:-1,x=horizontal?e.start+4:e.line+sign*2,y=horizontal?e.line+sign*2:e.start+4,w=horizontal?8:4,depth=horizontal?4:8;
   if(overlaps(x,y,base,w,depth,8-base,0))continue;
   const low=[x-w/2-.5,y-depth/2-.5,base-.2],high=[x+w/2+.5,y+depth/2+.5,8.2];
   const blocked=paths.some(pts=>pts.some((b,i)=>{const a=pts[Math.max(0,i-1)];return a.every((v,j)=>Math.max(v,b[j])>=low[j]&&Math.min(v,b[j])<=high[j]);}));
   if(!blocked)return {...e,base};
  }return null;
 }
 // A corner owns one column. Fixed-width native walls never get fictitiously
 // shortened: their end bays use variable-length native painted beam courses.
 function joinCorners(parts,edges,inset,bottom,top,style,overlaps){
  const vertices=new Map(),corners=[],key=(x,y)=>x.toFixed(4)+','+y.toFixed(4);
  for(const e of edges)for(const end of [0,1]){const raw=e.line+([0,3].includes(e.side)?-inset:inset),u=e.start+end*8,[x,y]=e.side%2?[raw,u]:[u,raw],k=key(x,y);if(!vertices.has(k))vertices.set(k,[]);vertices.get(k).push({e,end});}
  for(const v of vertices.values()){const h=v.find(q=>q.e.side%2===0),w=v.find(q=>q.e.side%2===1);if(!h||!w)continue;const c={x:w.e.line,y:h.e.line};corners.push(c);for(const q of v){const u=q.e.side%2?c.y:c.x;q.e[q.end?'hi':'lo']=u+(q.end?-.55:.55);}}
  const result=[],emit=(name,a,b,color,extra={})=>{const length=Math.hypot(...a.map((v,i)=>v-b[i]));if(length<.05)return;const n=Math.ceil(length/16);for(let i=0;i<n;i++){const at=t=>a.map((v,j)=>v+(b[j]-v)*t),start=at(i/n),end=at((i+1)/n),vertical=start[0]===end[0]&&start[1]===end[1],lo=start.map((v,j)=>Math.min(v,end[j])-(vertical&&j===2?0:.5)),hi=start.map((v,j)=>Math.max(v,end[j])+(vertical&&j===2?0:.5));if(overlaps((start[0]+end[0])/2,(start[1]+end[1])/2,lo[2],hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2],0))continue;result.push({name,x:(start[0]+end[0])/2,y:(start[1]+end[1])/2,z:lo[2],w:hi[0]-lo[0],d:hi[1]-lo[1],h:hi[2]-lo[2],rotation:0,color,component:'beam',asset:'Beam_Painted',start,end,...(i===0?extra:{})});}};
  for(const part of parts){
   if(part.component==='corner')continue;
   const edge=edges.find(e=>e.side===part.rotation/90&&Math.abs((e.side%2?part.y:part.x)-(e.start+4))<.01&&Math.abs((e.side%2?part.x:part.y)-e.line)<.7);
   if(edge&&['wall','trim'].includes(part.component)&&(edge.lo!==undefined||edge.hi!==undefined)){
    if(part.component==='trim')continue; // Colour the last course; never stack two coplanar caps.
    const lo=edge.lo??edge.start,hi=edge.hi??edge.start+8,line=part.component==='trim'?edge.line+([0,3].includes(edge.side)?-.3:.3):edge.line;
    for(let z=part.z;z<part.z+part.h-.01;z++)emit('Angle · bardage ajusté',edge.side%2?[line,lo,z+.5]:[lo,line,z+.5],edge.side%2?[line,hi,z+.5]:[hi,line,z+.5],part.color,{panelUnits:1/part.h});
   }else if(part.component==='beam'&&part.start[2]===part.end[2]&&(part.start[0]===part.end[0]||part.start[1]===part.end[1])){
    const axis=part.start[0]===part.end[0]?1:0,fixed=1-axis;let lo=Math.min(part.start[axis],part.end[axis]),hi=Math.max(part.start[axis],part.end[axis]);
    for(const c of corners){const v=axis?c.y:c.x,t=fixed?c.y:c.x;if(Math.abs(part.start[fixed]-t)>=1.05||lo>=v+1.05||hi<=v-1.05)continue;if(lo>=v-1.05)lo=v+1.05;else if(hi<=v+1.05)hi=v-1.05;else hi=lo;}
    if(hi-lo>=1){const a=[...part.start],b=[...part.end];a[axis]=lo;b[axis]=hi;emit(part.name,a,b,part.color);}
   }else if(part.component==='beam'){
    // Keep a clearance from the corner column, including diagonals and rails.
    if(corners.some(c=>Math.min(part.start[0],part.end[0])<c.x+1.05&&Math.max(part.start[0],part.end[0])>c.x-1.05&&Math.min(part.start[1],part.end[1])<c.y+1.05&&Math.max(part.start[1],part.end[1])>c.y-1.05))continue;
    result.push(part);
   }else result.push(part);
  }
  for(const c of corners)if(!overlaps(c.x,c.y,bottom,1,1,top-bottom,0))emit('Angle · montant unique',[c.x,c.y,bottom],[c.x,c.y,top],style.cornerColor||style.trim);
  return result;
 }
 function facadeBands(p,d=settings(p.design)){
  const raw=Math.ceil(Math.max(8,...p.objects.map(o=>(o.z||0)+(o.h||6)))),top=Math.min(d.roof?(p.height??p.size)-1:(p.height??p.size),Math.ceil(raw/4)*4),base=footprint(p,d),n=p.size/8,ny=(p.depth??p.size)/8,paths=accessPaths(p),bands=[],xs=[...base].map(k=>Number(k.split(',')[0])),ys=[...base].map(k=>Number(k.split(',')[1])),minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
  if(raw>top)throw new Error('La façade ou le toit dépasse la hauteur du blueprint. Choisissez un format supérieur.');
  for(let z=0;z<top;){const h=top-z>=4?4:1,cells=new Set(base);
   if(d.facadeForm!=='flat')for(const k of base){const [x,y]=k.split(',').map(Number),middle=z>=8&&z+h<=top-4,central=x>minX&&x<maxX,rear=y===maxY,front=y===minY;
    const tower=z<top*.6&&Math.abs(x-(minX+maxX)/2)<1;
    const target=d.facadeForm==='warehouse'?middle&&central&&!tower&&(front||rear):d.facadeForm==='gallery'?middle&&((front||rear)&&Math.min(x-minX,maxX-x)%2!==0||(x===minX||x===maxX)&&Math.min(y-minY,maxY-y)%2!==0):z>=Math.max(8,Math.ceil(top*.55/4)*4)&&(x===minX||y===minY||x===maxX||y===maxY);
    const selected=d.family==='signature'?Signature.recess(x,y,z,h,top,[minX,maxX,minY,maxY],d.seed):d.family==='m05-kit'?Kit.recess(x,y,z,h,top,[minX,maxX,minY,maxY],d.seed):target;
    if(!selected)continue;
    const occupied=p.objects.some(o=>{const r=o.rotation%180,w=(r?o.d:o.w)/2+1,depth=(r?o.w:o.d)/2+1;return (o.z||0)<z+h+.5&&(o.z||0)+(o.h||6)>z-.5&&o.x+w>x*8&&o.x-w<(x+1)*8&&o.y+depth>y*8&&o.y-depth<(y+1)*8;});
    const crossed=paths.some(pts=>pts.some((b,i)=>{const a=pts[Math.max(0,i-1)];return Math.max(a[2],b[2])>z-.5&&Math.min(a[2],b[2])<z+h+.5&&Math.max(a[0],b[0])>x*8-1&&Math.min(a[0],b[0])<(x+1)*8+1&&Math.max(a[1],b[1])>y*8-1&&Math.min(a[1],b[1])<(y+1)*8+1;}));
    if(!occupied&&!crossed)cells.delete(k);
   }
   if(!cells.size)for(const k of base)cells.add(k);
   bands.push({bottom:z,top:z+h,cells,globalTop:top,facadeForm:d.facadeForm});z+=h;
  }return bands;
 }
 function modularEnvelope(p,d){
  const style=architectureStyle(d),bands=facadeBands(p,d),plain={...p,design:{...d,facadeForm:'flat',roof:false}},parts=[];
  for(const band of bands)parts.push(...envelope(plain,band));
  const composition=roofComposition(p.size,d.roofSeed,d.roofLayout,null,p.depth??p.size),glazed=new Set(composition.cells);
  // Horizontal caps close every setback and the underside of a projecting bay.
  for(let i=0;i<bands.length;i++)for(const k of bands[i].cells){const [ix,iy]=k.split(',').map(Number),last=i===bands.length-1,above=bands[i+1]?.cells;
   if(last||above?.has(k))continue;
   const light=last&&(d.roofStyle==='glass'||d.roofStyle==='skylights'&&glazed.has(k)),stem=light?'Roof_Window':d.roofStyle==='ficsit'?'Roof_Orange':'Roof_Tar',slope=last&&['ridges','sawtooth'].includes(d.roofForm)&&bands[i].top+2.3<=(p.height??p.size);
   parts.push({name:last?'Toiture':'Terrasse de retrait',x:ix*8+4,y:iy*8+4,z:bands[i].top+.05,w:8,d:8,h:slope?2:.5,rotation:slope&&d.roofForm==='ridges'&&ix%2===0?180:0,color:light?'#91bbc7':'#656e69',component:'roof',asset:stem+(slope?'_03':'_01'),...(slope?{slope:'roof'}:{})});
  }
  for(let i=1;i<bands.length;i++)for(const k of bands[i].cells)if(!bands[i-1].cells.has(k)){const [ix,iy]=k.split(',').map(Number);parts.push({name:'Sous-face du volume saillant',x:ix*8+4,y:iy*8+4,z:bands[i].bottom-.55,w:8,d:8,h:.5,rotation:0,color:style.wall,component:'roof',asset:'Roof_Tar_01'});}
  if(d.roof){const last=bands.at(-1),cap={...p,design:{...d,facadeForm:'flat'}};parts.push(...envelope(cap,{bottom:last.top,top:last.top,globalTop:last.top,cells:last.cells}).filter(q=>['roof','gable'].includes(q.component)||q.name==='Lanterneau · vitrage vertical'));}
  // Merge vertical courses at shared levels; avoid stacked caps and visible gaps.
  const columns=new Map(),result=[];
  for(const part of parts){if(!['Angle · montant unique','Trame modulaire · montant'].includes(part.name)){result.push(part);continue;}const k=part.name+','+part.x+','+part.y;if(!columns.has(k))columns.set(k,[]);columns.get(k).push(part);}
  for(const group of columns.values()){group.sort((a,b)=>a.z-b.z);let current=null;for(const part of group){if(current&&part.z<=current.z+current.h+.01){current.end=part.end;current.h=part.z+part.h-current.z;}else{current={...part};result.push(current);}}}
  return result.flatMap(part=>{if(!part.start)return[part];const length=Math.hypot(...part.start.map((v,i)=>v-part.end[i]));if(length<=16)return[part];const count=Math.ceil(length/16);return Array.from({length:count},(_,i)=>{const start=part.start.map((v,j)=>v+(part.end[j]-v)*i/count),end=part.start.map((v,j)=>v+(part.end[j]-v)*(i+1)/count);return {...part,start,end,z:start[2],h:end[2]-start[2]};});});
 }

 // Native component plan. The server mirrors these deterministic rules and checks parity in tests.
 function envelope(p,geometry){let parts=rawEnvelope(p,geometry);if(!geometry&&p.design?.family==='m05-kit')parts=Kit.decorate(parts,p,accessPaths(p));if(!geometry&&p.design?.family==='signature')parts=Signature.decorate(parts,p,accessPaths(p),architectureStyle(p.design));return Surfaces.apply(parts,settings(p.design)).concat(p.nativeProfile==='clean-manifold-v1'?p.manifoldInterior?.parts||[]:[]);}
 function expandStudy(source,extra){
  if(!extra)return JSON.parse(JSON.stringify(source));
  const result=[],fixed=q=>/escalier|palier|protection de la trémie|Lumen · pavillon|Lumen · retour de coque|Lumen · rive flottante|Lumen · porche|Lumen · seuil|Lumen · appui/.test(q.name)||(q.name==='Lumen · annexe lisse'&&q.rotation===0),clone=q=>JSON.parse(JSON.stringify(q));
  const move=(q,dy)=>{q.y+=dy;if(q.start){q.start[1]+=dy;q.end[1]+=dy;}if(q.signatureBounds){q.signatureBounds[1]=q.signatureBounds[1].map(y=>y+dy);}return q;};
  const push=q=>{if(q.start){const a=q.start,b=q.end,n=Math.ceil(Math.hypot(...a.map((v,i)=>v-b[i]))/16);for(let i=0;i<n;i++){const r=clone(q);r.start=a.map((v,j)=>v+(b[j]-v)*i/n);r.end=a.map((v,j)=>v+(b[j]-v)*(i+1)/n);const rad=r.asset==='Beam_H'?.3:.15;r.x=(r.start[0]+r.end[0])/2;r.y=(r.start[1]+r.end[1])/2;r.z=Math.min(r.start[2],r.end[2])-rad;r.w=Math.abs(r.start[0]-r.end[0])+rad*2;r.d=Math.abs(r.start[1]-r.end[1])+rad*2;r.h=Math.abs(r.start[2]-r.end[2])+rad*2;result.push(r);}}else result.push(q);};
  for(const original of source){let q=clone(original);if(fixed(q)||q.fixedLayout){push(q);continue;}
   if(q.start){const lo=Math.min(q.start[1],q.end[1]),hi=Math.max(q.start[1],q.end[1]);if(lo<32&&hi>32){for(const p of[q.start,q.end])if(p[1]>=32)p[1]+=extra;push(q);continue;}}
   if(q.y>=32)push(move(q,extra));else{push(q);if(q.y>=24)for(let d=8;d<=extra;d+=8)push(move(clone(original),d));}
  }
  const terrace=source.find(q=>q.name==='Galerie · terrasse accessible'&&q.x===12&&q.y===36);if(terrace)for(let d=0;d<extra;d+=8)push(move(clone(terrace),d));
  return result;
 }
 function widenStudy(source,extra){
  if(!extra)return source;
  const result=[],clone=q=>JSON.parse(JSON.stringify(q));
  const move=(q,dx)=>{q.x+=dx;if(q.start){q.start[0]+=dx;q.end[0]+=dx;}if(q.signatureBounds)q.signatureBounds[0]=q.signatureBounds[0].map(x=>x+dx);return q;};
  const push=q=>{if(!q.start){result.push(q);return;}const a=q.start,b=q.end,n=Math.ceil(Math.hypot(...a.map((v,i)=>v-b[i]))/16);for(let i=0;i<n;i++){const r=clone(q);r.start=a.map((v,j)=>v+(b[j]-v)*i/n);r.end=a.map((v,j)=>v+(b[j]-v)*(i+1)/n);const rad=r.asset==='Beam_H'?.3:.15;r.x=(r.start[0]+r.end[0])/2;r.y=(r.start[1]+r.end[1])/2;r.z=Math.min(r.start[2],r.end[2])-rad;r.w=Math.abs(r.start[0]-r.end[0])+rad*2;r.d=Math.abs(r.start[1]-r.end[1])+rad*2;r.h=Math.abs(r.start[2]-r.end[2])+rad*2;result.push(r);}};
  for(const original of source){const q=clone(original);if(q.fixedLayout){push(q);continue;}if(q.start&&Math.min(q.start[0],q.end[0])<40&&(Math.max(q.start[0],q.end[0])>40||(q.stretchWidthEnd&&Math.abs(Math.max(q.start[0],q.end[0])-40)<1e-6))){for(const p of[q.start,q.end])if(p[0]>=40-1e-6)p[0]+=extra;push(q);continue;}
   if(q.x>=40)push(move(q,extra));else{push(q);const parallel=q.start?Math.abs(q.start[0]-q.end[0])<1e-6:['wall','window','trim'].includes(q.component)&&q.rotation%180!==0;if(q.x>=32&&!parallel&&q.repeatWidth!==false)for(let dx=8;dx<=extra;dx+=8)push(move(clone(original),dx));}
  }
  return result;
 }
 function repeatBays(source,widthExtra,depthExtra,bays){
  let result=JSON.parse(JSON.stringify(source));
  for(const [axis,extra,key]of[['x',widthExtra,'width'],['y',depthExtra,'length']]){
   const {pivot,from}=bays[key],out=[];
   for(const source of result){const q={...source};if(q[axis]>=pivot)q[axis]+=extra;out.push(q);if(source[axis]>=from&&source[axis]<pivot)for(let delta=8;delta<=extra;delta+=8)out.push({...source,[axis]:source[axis]+delta});}result=out;
  }return result;
 }
 function authoredStudy(p){
  if(p.nativeProfile==='clean-manifold-v1'){const probe=JSON.parse(JSON.stringify(p));delete probe.nativeProfile;delete probe.design.living;probe.design.studyFitted=false;probe.objects=[];probe.links=[];probe.floors=[{z:0,thickness:1}];return authoredStudy(probe);}
  const spec=CATALOG.studies[PRESETS[p.design.family].nativeStudy],dims=spec.dimensions;
  const widthExtra=p.size-dims[0],extra=(p.depth??p.size)-dims[1];if(widthExtra<0||widthExtra>(spec.workshopCompatible?48:32)||widthExtra%8!==0||extra<0||extra>(spec.workshopCompatible?48:32)||extra%8!==0||(p.height??p.size)<dims[2])throw new Error('Étude architecturale : largeur 64 à 96 m, longueur 48 à 80 m par travées de 8 m, hauteur de 32 m minimum. Ouvrez la maquette fournie.');
  if(!p.design.studyFitted&&(p.floors?.length!==1||p.floors[0].z!==0||p.floors[0].thickness!==1))throw new Error('Étude architecturale : le plan de production utilise un sol de 1 m au niveau zéro. Les terrasses appartiennent à la composition.');
  const Living=typeof module!=='undefined'&&module.exports?require('./creation-living'):root.CreationLiving,parts=Living.cleanParts(Living.terraces(Living.transform((spec.grammar?(typeof module!=='undefined'&&module.exports?require('./design-campus'):root.DesignCampus).parts(spec,p):spec.repeatBay?repeatBays(spec.parts,widthExtra,extra,spec.repeatBay):widenStudy(expandStudy(spec.parts,extra),widthExtra)),p),p),p).map(q=>p.design.living&&q.asset==='FloodlightWall'?{...q,livingCircuit:'living-existing'}:q).filter(q=>!['wall','window'].includes(q.component)||!(p.design.living?.openings||[]).some(b=>Living.hit(Living.box(q),b))).concat(p.design.living?.fixtures||[],p.design.living?.accessParts||[]),bounds=q=>{if(q.beamRadius)return Living.box(q);if(q.type==='wallPole'&&q.native?.wallMounted)return Living.box(q);if(q.signatureBounds)return q.signatureBounds;let w=q.w,d=q.d;if(q.rotation%180)[w,d]=[d,w];return [[q.x-w/2,q.x+w/2],[q.y-d/2,q.y+d/2],[q.z,q.z+q.h]];},overlap=(a,b)=>a.every((r,i)=>Math.min(r[1],b[i][1])-Math.max(r[0],b[i][0])>.05);
  Living.validateCompact(p,parts);
  if(!Living.matches(p))throw new Error('Implantation modifiée : réappliquez la création pour actualiser son aménagement avant l’export.');
  if(parts.some(q=>(q.signatureBounds?.[2]?.[1]??q.z+q.h)>(p.height??p.size)+.05))throw new Error('La création adaptée dépasse la hauteur du terrain. Augmentez la hauteur.');
  for(const o of p.objects){if(['input','output','entry','exit','port'].includes(o.type))continue;const b=bounds({...o,z:o.z||0,h:o.h||6});for(const q of parts){if(q.component==='module'&&!q.signatureBounds)continue;if(o.native?.ceilingMounted&&q.compactAssembly==='ceiling-electric')continue;if(overlap(b,bounds(q)))throw new Error('Étude architecturale : '+o.name+' rencontre '+q.name+'. Cette composition fixe ne déplace pas les machines.');}}
  for(const points of accessPaths(p))for(let i=1;i<points.length;i++){const b=points[i-1].map((v,j)=>[Math.min(v,points[i][j])-.25,Math.max(v,points[i][j])+.25]);for(const q of parts){if(q.component==='module'&&!q.signatureBounds)continue;if(overlap(b,bounds(q)))throw new Error('Étude architecturale : un trajet logistique rencontre '+q.name+'.');}}
  if(p.design.studyFitted)for(const f of p.floors||[])for(const [x,y]of p.design.studyFloors?.find(row=>row.z===f.z)?.cells||[]){if(x*8>=p.size||y*8>=(p.depth??p.size))throw new Error('Plancher hors de la création.');const b=[[x*8,x*8+8],[y*8,y*8+8],[f.z,f.z+f.thickness]];for(const q of parts){if(f.z===0&&q.component==='beam'&&bounds(q)[2][0]<1&&bounds(q)[2][1]>1)continue;if(['CatwalkCross','CatwalkStraight','CatwalkStairs','CatwalkRamp'].includes(q.asset)&&Math.abs(q.z-f.z-f.thickness)<.2)continue;if(q.component==='module'&&!q.signatureBounds)continue;if(overlap(b,bounds(q)))throw new Error('Un plancher rencontre '+q.name+'. Réappliquez la création.');}}
  return parts.filter(q=>p.design.roof||q.studyLayer!=='roof');
 }
 function rawEnvelope(p,geometry=null){
  if(!p.design?.enabled)return [];
  const d=settings(p.design);if(PRESETS[d.family]?.nativeStudy){if(!available(d.style,d.packs))throw new Error('Ce style utilise un pack non débloqué.');return authoredStudy(p);}if(d.family==='m05'){if(!available(d.style,d.packs))throw new Error('Ce style utilise un pack non débloqué.');return M05.envelope(p);}if(!geometry&&d.facadeForm!=='flat')return modularEnvelope(p,d);const style={...STYLES[d.style],...PALETTES[d.palette]};if(!available(d.style,d.packs))throw new Error('Ce style utilise un pack non débloqué.');
  const size=p.size,depth=p.depth??size,height=p.height??size,top=geometry?.top??Math.ceil(Math.max(8,...p.objects.map(o=>(o.z||0)+(o.h||6)))),bottom=geometry?.bottom||0,sloped=(d.roofForm==='ridges'||d.roofForm==='sawtooth')&&top+2.3<=height||d.roofForm==='auto'&&d.roofSeed%2===0&&top+2.3<=height,rise=sloped?2:0,monitor=d.roofForm==='monitor'&&top+4.5<=height,parts=[],missing=[],cells=geometry?.cells||footprint(p,d),composition=roofComposition(size,d.roofSeed,d.roofLayout,cells,depth),glazed=new Set(composition.cells),roofXs=[...cells].map(k=>Number(k.split(',')[0])),roofMid=(Math.min(...roofXs)+Math.max(...roofXs))/2,highRoof=ix=>ix===Math.floor(roofMid)||ix===Math.ceil(roofMid);
  if(top>height||(d.roof&&top+Math.max(.5,rise+.3)>height))throw new Error('La façade ou le toit dépasse la hauteur du blueprint. Choisissez un format supérieur.');
  const wall=d.style==='concrete'?'Wall_Concrete_8x4':'Wall_8x4_01',glass=d.family==='warehouse'?'Wall_Window_8x4_05':d.style==='concrete'?'Wall_Concrete_8x4_Window_02':d.style==='glass'?'Wall_Window_Thin_8x4_01':'Wall_Window_8x4_01';
  const shapes=p.objects.flatMap(o=>{const a=(o.rotation+180)*Math.PI/180,rows=o.native?({smelter:[[0,0,5,10,4.5],[1.45,4.5,5,7.1,4]],constructor:[[0,0,8,10,6]],assembler:[[-.5,0,9,17,3],[.75,3,9,5.5,5],[0,8,.2,.2,2.75]]}[o.type]):null;return rows?rows.map(([cy,z,w,d,h])=>({...o,x:o.x-Math.sin(a)*cy,y:o.y+Math.cos(a)*cy,z:o.z+z,w,d,h})):o;});
  const overlaps=(x,y,z,w,depth,h,rotation)=>{if(rotation%180)[w,depth]=[depth,w];return shapes.some(o=>{let ow=o.w,od=o.d;if(o.rotation%180)[ow,od]=[od,ow];return Math.min(x+w/2,o.x+ow/2)-Math.max(x-w/2,o.x-ow/2)>.001&&Math.min(y+depth/2,o.y+od/2)-Math.max(y-depth/2,o.y-od/2)>.001&&Math.min(z+h,(o.z||0)+(o.h||6))-Math.max(z,o.z||0)>.001;});};
  const box=(name,x,y,z,w,depth,h,rotation,color,component,asset,extra={})=>{if(overlaps(x,y,z,w,depth,h,rotation))return false;parts.push({name,x,y,z,w,d:depth,h,rotation,color,component,asset,...extra});return true;};
  const beam=(name,a,b)=>{const length=Math.hypot(...a.map((v,i)=>v-b[i]));if(length<1)return;if(length>16){const count=Math.ceil(length/16),at=i=>a.map((v,j)=>v+(b[j]-v)*i/count);for(let i=0;i<count;i++)beam(name,at(i),at(i+1));return;}const min=a.map((v,i)=>Math.min(v,b[i])-.5),max=a.map((v,i)=>Math.max(v,b[i])+.5);if(min[0]<-.001||min[1]<-.001||min[2]<-.001||max[0]>size+.001||max[1]>depth+.001||max[2]>height+.001||overlaps((min[0]+max[0])/2,(min[1]+max[1])/2,min[2],max[0]-min[0],max[1]-min[1],max[2]-min[2],0))return;parts.push({name,x:(a[0]+b[0])/2,y:(a[1]+b[1])/2,z:min[2],w:max[0]-min[0],d:max[1]-min[1],h:max[2]-min[2],rotation:0,color:style.trim,component:'beam',asset:'Beam_Painted',start:a,end:b});};
  const facade=(side,line,u,z)=>side%2?[line,u,z]:[u,line,z];
  // Separate outward surfaces: pillar 0, band .05, beam .10, wall .65 m.
  const decorated=d.structure!=='none'||d.wallDecoration!=='none'||d.detail==='bands'||d.cornerWidth>0,inset=.9,decorLine=(side,line,depth=.6)=>line+(side===0||side===3?depth-inset:inset-depth);
  const edges=[];for(const key of cells){const [ix,iy]=key.split(',').map(Number);for(const [dx,dy,side]of [[0,-1,0],[1,0,1],[0,1,2],[-1,0,3]])if(!cells.has((ix+dx)+','+(iy+dy)))edges.push({side,start:(side%2?iy:ix)*8,line:side===0?iy*8+inset:side===1?(ix+1)*8-inset:side===2?(iy+1)*8-inset:ix*8+inset});}edges.sort((a,b)=>a.side-b.side||a.line-b.line||a.start-b.start);
  const entry=entrance(p,edges,overlaps);
  for(const edge of edges)for(let z=bottom;z<top;z+=top-z>=4?4:1){
   const {side,start,line}=edge,span=side%2?depth:size,center=start+4,[x,y]=facade(side,line,center,z),rot=[0,90,180,270][side];
   if(entry&&edge.side===entry.side&&edge.line===entry.line&&edge.start===entry.start&&z<8)continue;
   const h=top-z>=4?4:1,window=windowAt(geometry?.facadeForm?{...d,facadeForm:geometry.facadeForm}:d,style,start,side,z,geometry?.globalTop??top,h,span);
   if(!box(window?'Fenêtre':'Mur plein',x,y,z,8,.5,h,rot,window?(style.window||'#7aabb9'):style.wall,window?'window':'wall',window?glass:h===1?d.style==='concrete'?'Wall_Concrete_8x1':'Wall_Orange_8x1':wall))missing.push({side,line,u:start,z,h});
   if(d.detail==='bands'&&z+h===(geometry?.globalTop??top)){const offset=.3-inset,xx=x+(side===1?-offset:side===3?offset:0),yy=y+(side===0?offset:side===2?-offset:0);box('Bandeau décoratif',xx,yy,z+h-1,8,.5,1,rot,style.trim,'trim',d.style==='concrete'?'Wall_Concrete_8x1':'Wall_Orange_8x1');}
   if(['braces','lattice'].includes(d.wallDecoration)&&h===4&&!window&&(d.wallDecoration==='lattice'||(start/8+side+d.seed)%2===0)){const beamline=decorLine(side,line),flip=(start/8+Math.floor(z/4)+side+d.seed)%2===0,a=facade(side,beamline,start+.5,flip?z+h-.5:z+.5),b=facade(side,beamline,start+7.5,flip?z+.5:z+h-.5);beam('Contreventement diagonal',a,b);if(d.wallDecoration==='lattice')beam('Croix de contreventement',facade(side,decorLine(side,line,.7),start+.5,flip?z+.5:z+h-.5),facade(side,decorLine(side,line,.7),start+7.5,flip?z+h-.5:z+.5));}
  }
  if(d.structure!=='none')for(const edge of edges){
   const {side,start,line}=edge,l=decorLine(side,line),last=!edges.some(e=>e.side===side&&e.line===line&&e.start===start+8),posts=[Math.max(.5,start),...(last?[Math.min((side%2?depth:size)-.5,start+8)]:[])];
   for(const u of posts)beam('Trame modulaire · montant',facade(side,l,u,bottom+.5),facade(side,l,u,top-.5));
   if(d.structure==='grid')for(let z=Math.max(4,bottom);z<top;z+=4){if(entry&&side===entry.side&&line===entry.line&&start===entry.start&&z<8)continue;const rail=decorLine(side,line,.8);beam('Trame modulaire · traverse',facade(side,rail,start+.5,z-.5),facade(side,rail,start+7.5,z-.5));}
  }
  if(d.wallDecoration!=='none')for(const gap of openingGroups(missing)){
   const {side,start,end,bottom,top}=gap,line=decorLine(side,gap.line,d.structure!=='none'?.75:.6),a=facade(side,line,start+.5,bottom+.5),b=facade(side,line,end-.5,bottom+.5),c=facade(side,line,end-.5,top-.5),e=facade(side,line,start+.5,top-.5);
   beam('Baie industrielle · jambage',facade(side,line,start+.5,bottom+1),facade(side,line,start+.5,top-1));beam('Baie industrielle · jambage',facade(side,line,end-.5,bottom+1),facade(side,line,end-.5,top-1));beam('Baie industrielle · linteau',e,c);beam('Baie industrielle · traverse basse',a,b);
  }
  if(entry&&bottom===0){const {side,start,line,base}=entry,l=decorLine(side,line,d.structure!=='none'?.7:.6);beam('Entrée piétonne · jambage',facade(side,l,start+.5,base+.5),facade(side,l,start+.5,6.5));beam('Entrée piétonne · jambage',facade(side,l,start+7.5,base+.5),facade(side,l,start+7.5,6.5));beam('Entrée piétonne · linteau',facade(side,l,start+.5,7.5),facade(side,l,start+7.5,7.5));
   if(d.entryTreatment!=='frame'){
    const back=decorLine(side,line,3);
    if(d.entryTreatment==='double')for(const u of [start+.5,start+7.5])beam('Portique · montant intérieur',facade(side,back,u,base+.5),facade(side,back,u,6.5));
    beam('Portique · traverse intérieure',facade(side,back,start+.5,7.5),facade(side,back,start+7.5,7.5));
    for(const u of d.entryTreatment==='porch'?[start+.5,start+2.5,start+5.5,start+7.5]:[start+.5,start+7.5])beam('Portique · brise-soleil',facade(side,l,u,7.3),facade(side,back,u,7.3));
   }
  }
  if(d.cornerWidth)for(const x of [1,size-1])for(const y of [1,depth-1])if(cells.has((x<2?0:size/8-1)+','+(y<2?0:depth/8-1)))for(let z=bottom;z+4<=top;z+=4)box('Pilier de coin',x,y,z,2,2,4,0,style.trim,'corner',d.style==='concrete'?'Pillar_Small_Concrete':'Pillar_Small_Metal');
  if(d.roof)for(let x=4;x<size;x+=8)for(let y=4;y<depth;y+=8){
   const ix=(x-4)/8,iy=(y-4)/8;if(!cells.has(ix+','+iy))continue;const skylight=d.roofStyle==='glass'||d.roofStyle==='skylights'&&glazed.has(ix+','+iy),rotation=sloped?(d.roofForm==='sawtooth'?0:ix%2?0:180):0,raised=monitor&&highRoof(ix),roofZ=top+(raised?4:0);
   const stem=skylight?'Roof_Window':d.roofStyle==='ficsit'?'Roof_Orange':'Roof_Tar';
   box(skylight?'Verrière à ossature':'Toiture',x,y,roofZ+(sloped?.15:0),8,8,sloped?2:.5,rotation,skylight?'#91bbc7':d.roofStyle==='ficsit'?style.trim:'#656e69','roof',stem+(sloped?'_03':'_01'),sloped?{slope:'roof'}:{});
   if(raised)for(const [dx,dy,side]of [[0,-1,0],[1,0,1],[0,1,2],[-1,0,3]]){
    const nx=ix+dx,ny=iy+dy,high=cells.has(nx+','+ny)&&highRoof(nx);if(high)continue;
    const line=side===0?y-3.75:side===1?x+3.75:side===2?y+3.75:x-3.75,[wx,wy]=facade(side,line,side%2?y:x,top);
    box('Lanterneau · vitrage vertical',wx,wy,top,8,.5,4,side*90,style.window||'#91bbc7','window',glass);
   }
   if(sloped)for(const [dy,yy]of [[-1,y-3.75],[1,y+3.75]])if(!cells.has(ix+','+(iy+dy)))box('Pignon incliné',x,yy,top,8,.5,2,rotation===0?180:0,style.wall,'gable','Wall_Orange_Tris_8x2',{slope:'gable'});
   if(sloped&&(d.roofForm==='sawtooth'||!cells.has((ix-1)+','+iy)&&rotation===0||!cells.has((ix+1)+','+iy)&&rotation===180))for(let z=top;z<top+2;z++)box('Rive de toit',rotation===0?x-3.75:x+3.75,y,z,8,.5,1,90,style.wall,'gable','Wall_Orange_8x1');
  }
  return joinCorners(parts,edges,inset,bottom,top,{...style,cornerColor:d.cornerWidth?style.trim:style.wall},overlaps);
 }
 function floorCells(p,f){
  if(p.design?.enabled&&PRESETS[p.design.family]?.nativeStudy&&p.design.studyFitted)return (p.design.studyFloors?.find(row=>row.z===f.z)?.cells||[]).map(c=>[...c]);
  let cells=new Set();const width=p.size,depth=p.depth??width;
  if(p.design?.enabled&&p.design.family==='m05'){const ox=(width-Math.floor(width/40)*40)/2,oy=(depth-Math.floor(depth/40)*40)/2;for(let x=0;x<width/8;x++)for(let y=0;y<depth/8;y++)if(x*8>=ox+24&&x*8+8<=width-ox-24&&y*8>=oy+24&&y*8+8<=depth-oy-24)cells.add(x+','+y);}
  else{for(let x=0;x<width/8;x++)for(let y=0;y<depth/8;y++)cells.add(x+','+y);if(p.generation?.shape==='exotic'||p.design?.fit==='occupied'||p.design?.enabled&&f.z>0){const allowed=settings(p.design).facadeForm==='flat'?footprint(p):(facadeBands(p).find(b=>b.bottom<=f.z+(f.thickness||1)&&b.top>f.z+(f.thickness||1))?.cells||footprint(p));cells=new Set([...cells].filter(k=>allowed.has(k)));}}
  // A terrace already supplies its own deck. Never put a second floor below it.
  if(p.design?.enabled){const top=f.z+f.thickness,surfaces=envelope(p).filter(q=>q.asset==='Roof_Tar_01'||q.asset==='Roof_Orange_01'||q.asset==='Roof_Window_01').map(q=>q.signatureBounds||(q.component==='roof'?[[q.x-4,q.x+4],[q.y-4,q.y+4],[q.z,q.z+q.h]]:null)).filter(b=>b&&Math.abs(b[2][1]-top)<.8);for(const k of cells){const [x,y]=k.split(',').map(Number);if(surfaces.some(b=>Math.min(b[0][1],x*8+8)-Math.max(b[0][0],x*8)>7&&Math.min(b[1][1],y*8+8)-Math.max(b[1][0],y*8)>7))cells.delete(k);}}
  return [...cells].map(k=>k.split(',').map(Number));
 }
 function floors(p,material,profile){if(!['concrete','steel','asphalt','polished','metal'].includes(material)||!['solid','frame','factory'].includes(profile))throw new Error('Sol invalide.');if(profile==='solid'&&['polished','metal'].includes(material)&&p.floors.some(f=>f.thickness!==1))throw new Error('Le béton ciré et la tôle utilisent des dalles natives de 1 m.');return p.floors.map(f=>({...f,material,profile,holes:[]}));}

 function openings(p){
  if(!p.design?.enabled||p.design.family==='m05'||PRESETS[p.design.family]?.nativeStudy)return 0;const d=settings(p.design),parts=envelope(p),bands=d.facadeForm==='flat'?[{cells:footprint(p),bottom:0,top:Math.ceil(Math.max(8,...p.objects.map(o=>(o.z||0)+(o.h||6))))}]:facadeBands(p,d);let expected=0;
  for(const b of bands){const height=b.top-b.bottom,rows=Math.floor(height/4)+height%4;for(const k of b.cells){const [x,y]=k.split(',').map(Number);for(const [dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]])if(!b.cells.has((x+dx)+','+(y+dy)))expected+=rows;}}
  const top=bands.at(-1).top,actual=parts.filter(p=>p.z<top).reduce((n,p)=>n+(p.coverageUnits||p.panelUnits||(['wall','window'].includes(p.component)?1:0)),0),entry=parts.some(p=>p.name==='Entrée piétonne · linteau')?2:0;
  return Math.max(0,Math.ceil(expected-actual-entry-1e-7));
 }

 const api={prepareM05,M05,facadeBands,floorCells,reserveArchitecture,architectureStyle,CATALOG,GROUPS,PALETTES,PRESETS,preset,presetAvailable,vary,windowAt,accessPaths,entrance,STYLES,DEFAULTS,generation,settings,available,category,color,envelope,openings,floors,roofComposition,footprint,openingGroups};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.WorkshopDesign=api;
})(typeof globalThis!=='undefined'?globalThis:this);




