'use strict';
(function(root){
 const node=typeof module!=='undefined'&&module.exports;
 const library=node?require('./m05-library'):root.M05Library;
 const clone=v=>JSON.parse(JSON.stringify(v));
 const palettes={compact:{floor:'#7d8588',lane:'#bbced0',pad:'#458b94',frame:'#263039',light:'#d7eff2'},atlas:{floor:'#333f43',lane:'#bdb9a8',pad:'#c7924f',frame:'#293c43',light:'#f0d8a8'},sylva:{floor:'#626e62',lane:'#d6d1b9',pad:'#a7be9a',frame:'#526c5b',light:'#eee4be'},lumen:{floor:'#53656b',lane:'#dce5e4',pad:'#70bfcb',frame:'#43646d',light:'#d7eff2'},prisme:{floor:'#475663',lane:'#dbe0ed',pad:'#93b5d4',frame:'#3d546c',light:'#dfebf5'},canopee:{floor:'#6a7165',lane:'#d8d5bd',pad:'#aab58b',frame:'#66765b',light:'#f1e4bb'},bastion:{floor:'#5e5d58',lane:'#b9b5a4',pad:'#aa8360',frame:'#4c4d48',light:'#e8d5b0'},monolithe:{floor:'#535754',lane:'#c3bdae',pad:'#a68d69',frame:'#454c49',light:'#e9dec6'},aster:{floor:'#4e5d64',lane:'#c9d4d5',pad:'#c99752',frame:'#3d4f58',light:'#e2e9e0'}};
 function box(q){if(q.beamRadius&&q.start){const a=q.start,b=q.end,l=Math.hypot(...a.map((v,i)=>b[i]-v)),[dx,dy,dz]=a.map((v,i)=>(b[i]-v)/l),raw=dx>-.999999?[0,-dz,dy,1+dx]:[0,0,1,0],norm=Math.hypot(...raw),quat=raw.map(v=>v/norm),u=rotate(quat,[0,q.beamRadius,0]),v=rotate(quat,[0,0,q.beamRadius]);return a.map((n,i)=>[Math.min(n,b[i])-Math.abs(u[i])-Math.abs(v[i]),Math.max(n,b[i])+Math.abs(u[i])+Math.abs(v[i])]);} if(q.type==='wallPole'&&q.native?.ceilingMounted)return[[q.x-.3,q.x+.3],[q.y-.3,q.y+.3],[q.z-.8,q.z+.02]];if(q.type==='wallPole'&&q.native?.wallMounted){const r=q.rotation*Math.PI/180,n=[Math.round(Math.cos(r)),Math.round(Math.sin(r))],b=[[q.x-.3,q.x+.3],[q.y-.3,q.y+.3],[q.z,q.z+.6]],a=n[0]?0:1,v=a?q.y:q.x;b[a]=n[a]>0?[v,v+.6]:[v-.6,v];return b;}if(q.signatureBounds)return q.signatureBounds;const w=q.rotation%180?q.d:q.w,d=q.rotation%180?q.w:q.d;return[[q.x-w/2,q.x+w/2],[q.y-d/2,q.y+d/2],[q.z||0,(q.z||0)+(q.h||0)]];}
 const hit=(a,b)=>a.every((r,i)=>Math.min(r[1],b[i][1])-Math.max(r[0],b[i][0])>.04);
 function transform(source,p){
  const family=p.design?.family;if(p.design?.studyHeightMode!=='auto'||!['atlas','sylva'].includes(family))return source;
  const top=Math.max(9,p.design?.studyHeightTop||0,...p.objects.filter(o=>!['port','pole','wallPole','lift'].includes(o.type)).map(o=>(o.z||0)+(o.h||6))),base=family==='atlas'?25:17,target=Math.max(17,1+Math.ceil((top+2.5-1)/4)*4),delta=target-base,pivot=family==='atlas'?13:9,out=[];
  const zmap=z=>z<=pivot?z:delta<0?Math.max(pivot,z+delta):z+delta;
  const push=q=>{if(!q.start){out.push(q);return;}const a=q.start,b=q.end,length=Math.hypot(...a.map((v,i)=>v-b[i]));if(length<.01)return;const n=Math.ceil(length/16);for(let i=0;i<n;i++){const r=clone(q);r.start=a.map((v,j)=>v+(b[j]-v)*i/n);r.end=a.map((v,j)=>v+(b[j]-v)*(i+1)/n);const rad=r.asset==='Beam_H'?.3:.15;r.x=(r.start[0]+r.end[0])/2;r.y=(r.start[1]+r.end[1])/2;r.z=Math.min(r.start[2],r.end[2])-rad;r.w=Math.abs(r.start[0]-r.end[0])+rad*2;r.d=Math.abs(r.start[1]-r.end[1])+rad*2;r.h=Math.abs(r.start[2]-r.end[2])+rad*2;out.push(r);}};
  for(const original of source){let q=clone(original);const fixed=q.zone==='circulation'||q.zone==='galerie'||q.zone==='accueil'||q.zone==='parvis'||family==='sylva'&&q.zone==='terrasses'||/escalier|palier|garde-corps|trémie|porte vers/.test(q.name);if(!fixed){
    if(delta<0){if(['wall','window'].includes(q.component)&&q.z>=pivot&&q.z<pivot-delta)continue;if(q.start&&q.start[2]>=pivot&&q.start[2]<pivot-delta&&q.end[2]>=pivot&&q.end[2]<pivot-delta)continue;}
    if(delta>0&&['wall','window'].includes(q.component)&&q.z===pivot)for(let dz=0;dz<delta;dz+=4)push({...clone(q),z:pivot+dz});
    if(q.start){q.start[2]=zmap(q.start[2]);q.end[2]=zmap(q.end[2]);}else{const old=q.z;q.z=zmap(q.z);if(q.signatureBounds)q.signatureBounds[2]=q.signatureBounds[2].map(z=>z+q.z-old);}
   }
   if(family==='atlas'&&q.name==='Halle · flanc'&&q.x===24.5&&q.y===20&&q.z===13)continue;
   if(family==='sylva'&&(/pavillon supérieur/.test(q.name)&&q.z===target+4))continue;
   if(family==='sylva'&&(/toiture du pavillon|couronnement/.test(q.name))){if(q.start){q.start[2]-=4;q.end[2]-=4;}else q.z-=4;}
   push(q);
  }
  return out;
 }
 function modulePart(asset,name,x,y,z,rotation,color,group){let sourceModule,sourceIndex;for(const [key,m]of Object.entries(library.modules)){const i=m.parts.findIndex(q=>q.asset===asset);if(i>=0){sourceModule=key;sourceIndex=i;break;}}if(sourceModule===undefined&&['Foundation_ConcretePolished_8x1','Stair_PolishedConcrete_8x2'].includes(asset)){for(const[key,m]of Object.entries(library.modules)){const i=m.parts.findIndex(q=>q.asset==='Foundation_Concrete_8x4');if(i>=0){sourceModule=key;sourceIndex=i;break;}}}if(sourceModule===undefined)throw new Error('Pièce intérieure indisponible : '+asset);const a=(rotation+(asset.startsWith('Stair_')?180:0))*Math.PI/360;return{name,asset,component:'module',sourceModule,sourceIndex,origin:[0,0,0],turn:0,quat:[0,0,Math.sin(a),Math.cos(a)],x,y,z,w:0,d:0,h:0,rotation,color,zone:'interieur',studyLayer:'interior',livingCircuit:group,signatureBounds:[[x-.55,x+.55],[y-.55,y+.55],[z,z+.7]]};}
 function access(p,levels,palette){
  const parts=[],openings=[];if(levels.length<2)return{parts,openings};let z=levels[0].z,y=8;
  const platform=(x,y,z)=>{const q=modulePart('CatwalkCross','Intérieur · palier de circulation',x,y,z,0,palette.frame);delete q.livingCircuit;q.signatureBounds=[[x-2,x+2],[y-2,y+2],[z-.18,z]];parts.push(q);};
  platform(4,6,z);
  for(const level of levels.slice(1)){
   let rise=level.z-z;if(rise<0||!Number.isInteger(rise))throw new Error('Les niveaux de circulation doivent être espacés d’un nombre entier de mètres.');
   while(rise>=2){const step=rise>=4?4:2,asset=step===4?'CatwalkStairs':'CatwalkRamp',q=modulePart(asset,'Intérieur · escalier entre étages',4,y+2,z,90,palette.frame);delete q.livingCircuit;q.signatureBounds=[[2,6],[y,y+4],[z-.18,z+step+1.1]];q.walkStart=[4,y,z];q.walkEnd=[4,y+4,z+step];parts.push(q);y+=4;z+=step;rise-=step;}
   if(rise){for(let i=0;i<4;i++){const yy=y+.15+i*.3,zz=z+.1+i*.25;parts.push({name:'Intérieur · marche de raccord de 1 m',asset:'Beam_Painted',component:'beam',start:[2,yy,zz],end:[6,yy,zz],x:4,y:yy,z:zz-.15,w:4.3,d:.3,h:.3,rotation:0,color:palette.frame,zone:'interieur',studyLayer:'interior'});}y+=1.2;z+=1;}
   if(y+4>(p.depth??p.size))throw new Error('L’escalier entre étages nécessite davantage de longueur. Agrandissez la création.');
   platform(4,y+2,z);const end=level.paths[0];if(!end)throw new Error('Aucun palier intérieur accessible au niveau '+z+' m.');
   // Turn sideways before returning along the stair core: no deck above its flights.
   const points=[[4,y+2,z],[8,y+2,z],[8,end[1],z],[end[0],end[1],z]];
   for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i],length=Math.hypot(b[0]-a[0],b[1]-a[1]);if(length<.1)continue;const dx=(b[0]-a[0])/length,dy=(b[1]-a[1])/length;
    for(let t=2;t<length+1.99;t+=4){const q=modulePart('CatwalkStraight','Intérieur · passerelle d’inspection',a[0]+dx*Math.min(t,length),a[1]+dy*Math.min(t,length),z,dy?90:0,palette.frame);delete q.livingCircuit;q.signatureBounds=[[q.x-2,q.x+2],[q.y-2,q.y+2],[z-.18,z]];parts.push(q);}
   }
   // A real doorway replaces a complete native side-wall panel at the bridge.
   const line=p.design.family==='atlas'?24.5:24,wallY=8+Math.floor((end[1]-8)/8)*8+4;openings.push([[line-.8,line+.8],[end[1]-2,end[1]+2],[z,z+3]]);
   const door=modulePart('Wall_Door_8x4_03','Intérieur · porte du palier',line,wallY,z,0,palette.frame);delete door.livingCircuit;door.signatureBounds=[[line-.15,line+.15],[wallY-4,wallY+4],[z+3,z+4]];parts.push(door);
   y+=4;
  }
  return{parts,openings};
 }
 // Floor paint is carried by native foundations. Beams are never decals.
 function cleanParts(parts,p){
  if(!p.design?.living)return parts;
  const top=Math.min(...p.floors.map(f=>f.z+f.thickness));
  return parts.filter(q=>!q.livingFloorMark&&q.asset!=='FloodlightWall'&&!(q.studyLayer==='deck'&&box(q)[2][0]>=0&&box(q)[2][1]<=top+.8));
 }
 function continuousFloor(p,parts){
  const base=Math.min(...p.floors.map(f=>f.z));
  if(p.design.studyFitted){let row=p.design.studyFloors.find(r=>r.z===base);if(row){row.cells=[];for(let x=0;x<p.size/8;x++)for(let y=0;y<(p.depth??p.size)/8;y++)row.cells.push([x,y]);}}
  for(const f of p.floors){f.profile='solid';f.material=p.design.family==='compact'?'polished':'concrete';if(p.design.family==='compact')f.thickness=1;}
 }
 // Only opaque, complete native wall panels can carry electrical hardware.
 function wallMounts(parts,p,z){
  const machines=p.objects.filter(o=>o.recipe),cx=machines.length?machines.reduce((n,o)=>n+o.x,0)/machines.length:p.size/2,cy=machines.length?machines.reduce((n,o)=>n+o.y,0)/machines.length:(p.depth??p.size)/2;
  return parts.filter(q=>q.component==='wall'&&q.rotation%90===0&&q.h===4&&q.w===8&&!/Door|Tris/.test(q.asset)&&q.z<=z&&q.z+q.h>=z).map(q=>{
   const b=box(q),axis=b[0][1]-b[0][0]<b[1][1]-b[1][0]?0:1,side=(axis===0?cx-q.x:cy-q.y)>=0?1:-1,normal=axis===0?[side,0]:[0,side],position=[q.x,q.y];
   position[axis]=b[axis][side>0?1:0]+side*.025;
   return{wall:q,normal,axis,position,rotation:axis===0?(side>0?0:180):(side>0?90:270)};
  });
 }
 function mountedPart(asset,name,m,z,color,group){
  const q=modulePart(asset,name,...m.position,z,m.rotation,color,group),a=m.axis,b=1-a,r=asset==='FloodlightWall'?1.25:.3,depth=asset==='FloodlightWall'?1.8:.6;
  q.signatureBounds=[[q.x-r,q.x+r],[q.y-r,q.y+r],[z-(asset==='FloodlightWall'?1.15:0),z+.7]];
  q.signatureBounds[a]=m.normal[a]>0?[m.position[a]+.01,m.position[a]+depth]:[m.position[a]-depth,m.position[a]-.01];
  q.mount={wall:[m.wall.x,m.wall.y,m.wall.z,m.wall.rotation],normal:m.normal};return q;
 }
 function remountPower(p,parts){
  const mounted=[];
  for(const o of p.objects.filter(o=>o.type==='wallPole'&&o.native)){
   const choices=parts.filter(q=>q.component==='wall'&&q.h===4&&q.w===8&&!/Door|Tris/.test(q.asset)).flatMap(q=>{const z=Math.max(q.z+.7,Math.min(q.z+q.h-.8,o.z));return wallMounts([q],p,z).map(m=>({m,z,d:Math.hypot(o.x-m.position[0],o.y-m.position[1],o.z-z)}));}).sort((a,b)=>a.d-b.d);
   const candidate=({m,z})=>{return box({type:'wallPole',native:{wallMounted:true},rotation:m.rotation,x:m.position[0],y:m.position[1],z});};
   const choice=choices.find(c=>!parts.some(q=>q!==c.m.wall&&hit(candidate(c),box(q)))&&!mounted.some(b=>hit(candidate(c),b))&&!p.objects.some(other=>other!==o&&!['port','pole','wallPole'].includes(other.type)&&hit(candidate(c),box(other))));
   if(!choice)throw new Error('Aucun mur dégagé pour fixer '+o.name+'.');
   const {m,z}=choice;[o.x,o.y]=m.position;o.z=z;
   const a=m.rotation*Math.PI/360;o.rotation=m.rotation;o.native.rotation=m.rotation;o.native.quaternion=[0,0,Math.sin(a),Math.cos(a)];o.native.wallMounted=true;mounted.push(candidate(choice));
  }
 }
 function snapshot(p){return{size:p.size,depth:p.depth??p.size,floors:(p.floors||[]).map(f=>[f.z,f.thickness]),machines:p.objects.filter(o=>o.recipe).map(o=>[o.id,o.x,o.y,o.z||0,o.rotation]).sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0)};}
 function matches(p){const old=p.design?.living?.snapshot;if(!old)return true;if(p.design.living.revision!==2||p.design.family==='compact'&&p.design.living.compactRevision!==4)return false;const now=snapshot(p);return old.size===now.size&&old.depth===now.depth&&JSON.stringify(old.floors)===JSON.stringify(now.floors)&&JSON.stringify(old.machines)===JSON.stringify(now.machines);}
 function terraces(source,p){
  if(p.design?.family!=='sylva')return source;
  const y=(p.depth??p.size)-12,palette=palettes.sylva;
  const result=source.filter(q=>!(q.name==='Sylva · gradin paysager'&&q.x===20&&q.y===y&&q.z===13)&&!(q.name==='Sylva · terrasse haute'&&q.x===28&&q.y===y&&q.z===17)&&!(['wall','window'].includes(q.component)&&q.y===y&&((q.x===16&&q.z===9)||(q.x===24&&q.z===13))));
  for(const [x,z]of[[16,9],[24,13]]){const q=modulePart('CatwalkStairs','Sylva · escalier entre terrasses',x,y,z,0,palette.frame);delete q.livingCircuit;q.fixedLayout=true;q.walkStart=[x-2,y,z];q.walkEnd=[x+2,y,z+4];q.signatureBounds=[[x-2,x+2],[y-2,y+2],[z-.18,z+5.1]];result.push(q);}
  for(const[x,yy,z,asset,rotation]of[[20,y,13,'CatwalkCross',0],[20,y-4,13,'CatwalkStraight',90],[28,y,17,'CatwalkCross',0],[32,y,17,'CatwalkStraight',0]]){const q=modulePart(asset,'Sylva · palier panoramique',x,yy,z,rotation,palette.frame);delete q.livingCircuit;q.signatureBounds=[[x-2,x+2],[yy-2,yy+2],[z-.18,z]];q.fixedLayout=true;result.push(q);}
  for(const[x,z]of[[20,13],[28,17]])for(const yy of[y-2,y+2]){const q=modulePart('Railing_01','Sylva · protection de palier',x,yy,z,90,palette.frame);delete q.livingCircuit;q.signatureBounds=[[x-2,x+2],[yy-.1,yy+.1],[z,z+1]];q.fixedLayout=true;result.push(q);}
  return result;
 }
 function restorePower(p){
  const old=p.design?.living?.powerOriginal;if(!old)return;
  const generated=new Set(p.design.living.powerGenerated||[]),present=new Set(p.objects.filter(o=>!generated.has(o.id)).map(o=>o.id));
  p.objects=p.objects.filter(o=>!generated.has(o.id));for(const o of old.objects)if(!present.has(o.id))p.objects.push(clone(o));
  const ids=new Set(p.objects.map(o=>o.id));p.links=p.links.filter(l=>l.kind!=='power').concat(clone(old.links).filter(l=>ids.has(l.from)&&ids.has(l.to)));
 }
 function rotate(q,v){const [x,y,z,w]=q,[a,b,c]=v,tx=2*(y*c-z*b),ty=2*(z*a-x*c),tz=2*(x*b-y*a);return[a+w*tx+y*tz-z*ty,b+w*ty+z*tx-x*tz,c+w*tz+x*ty-y*tx];}
 function powerPoint(o){
  const off=o.native?.ports?.PowerInput||o.native?.ports?.PowerConnection;if(!off)return[o.x,o.y,(o.z||0)+(o.h||4)];
  const v=rotate(o.native.quaternion,off),a=(o.rotation-o.native.rotation)*Math.PI/180;
  return[o.x+v[0]*Math.cos(a)-v[1]*Math.sin(a),o.y+v[0]*Math.sin(a)+v[1]*Math.cos(a),o.z+(o.native.originZ||0)+v[2]];
 }
 function compactPower(p){
  if(!p.nativeProfile)return null;
  const poles=p.objects.filter(o=>o.type==='wallPole'),prototype=poles[0];if(!prototype)throw new Error('Compact : aucun raccord électrique natif disponible.');
  const original={objects:clone(poles),links:clone(p.links.filter(l=>l.kind==='power'))},generated=[],carriers=[];
  p.objects=p.objects.filter(o=>o.type!=='wallPole');p.links=p.links.filter(l=>l.kind!=='power');
  const machines=p.objects.filter(o=>o.recipe),trunkX=Math.round((Math.min(...machines.map(o=>o.x))+Math.max(...machines.map(o=>o.x)))/2),hubs=new Map(),height=16.5;
  const node=(id,x,y)=>{const o={...clone(prototype),id,name:'Distribution électrique au plafond',x,y,z:height,rotation:0};o.native={...o.native,module:'compact-electric',wallMounted:true,ceilingMounted:true,rotation:0,quaternion:[0,Math.SQRT1_2,0,Math.SQRT1_2]};p.objects.push(o);generated.push(id);return o;};
  const wire=(a,b)=>{if(a!==b)p.links.push({kind:'power',from:a.id,to:b.id});};
  for(const m of machines){
   const off=m.native?.ports?.[m.type==='smelter'?'PowerConnection':'PowerInput'];if(!off)throw new Error('Port électrique natif absent : '+m.name);
   const a=(m.rotation-m.native.rotation)*Math.PI/180,raw=rotate(m.native.quaternion,off),v=[raw[0]*Math.cos(a)-raw[1]*Math.sin(a),raw[0]*Math.sin(a)+raw[1]*Math.cos(a)],x=m.x+v[0],y=m.y+v[1],yy=Math.round(y*100)/100;
   const terminal=node('cp-drop-'+m.id,x,y);wire(terminal,m);
   let hub=hubs.get(yy);if(!hub){hub=Math.abs(x-trunkX)<.65?terminal:node('cp-bus-'+String(yy).replace('.','_'),trunkX,yy);hubs.set(yy,hub);}wire(hub,terminal);
   carriers.push([[hub.x,hub.y,16.65],[terminal.x,terminal.y,16.65]]);
  }
  const ordered=[...hubs.values()].sort((a,b)=>a.y-b.y);for(let i=1;i<ordered.length;i++){wire(ordered[i-1],ordered[i]);carriers.push([[ordered[i-1].x,ordered[i-1].y,16.65],[ordered[i].x,ordered[i].y,16.65]]);}
  return{original,generated,carriers,trunkX,hubIds:ordered.map(o=>o.id)};
 }
 function compactLightingFeeds(p,power,fixtures){
  if(!power)return;
  const prototype=p.objects.find(o=>o.native?.ceilingMounted),hubs=power.hubIds.map(id=>p.objects.find(o=>o.id===id)),originalHubs=new Set(power.hubIds),branches=[];
  const add=(id,x,y)=>{const o={...clone(prototype),id,x,y};p.objects.push(o);power.generated.push(id);return o;};
  for(const [i,q]of fixtures.filter(q=>q.asset==='PowerPoleWall').entries()){
   const offset=rotate(q.quat,[.8,0,0]),x=q.x+offset[0],y=q.y+offset[1],feed=add('cp-light-'+i,x,y);let yy=y;while(hubs.some(o=>Math.abs(o.y-yy)<.65))yy+=y>(p.depth??p.size)/2?-.8:.8;const hub=add('cp-light-hub-'+i,power.trunkX,yy);hubs.push(hub);
   p.links.push({kind:'power',from:hub.id,to:feed.id});branches.push([[hub.x,hub.y,16.65],[feed.x,feed.y,16.65]]);
  }
  p.links=p.links.filter(l=>!(l.kind==='power'&&originalHubs.has(l.from)&&originalHubs.has(l.to)));
  power.carriers=power.carriers.filter(([a,b])=>Math.abs(a[0]-power.trunkX)>.01||Math.abs(b[0]-power.trunkX)>.01).concat(branches);
  hubs.sort((a,b)=>a.y-b.y);for(let i=1;i<hubs.length;i++){p.links.push({kind:'power',from:hubs[i-1].id,to:hubs[i].id});power.carriers.push([[hubs[i-1].x,hubs[i-1].y,16.65],[hubs[i].x,hubs[i].y,16.65]]);}
 }

 function compactInterior(p,parts,levels,fixtures,palette,power){
  const D=node?require('./workshop-design'):root.WorkshopDesign,out=[],end=(p.depth??p.size)-8;
  const volumes=[[[8.05,16.7],[16,end],[1.05,7.6]],[[16,24.5],[16,24],[1.05,5.5]],[[9.2,20.5],[9.2,20.5],[1.05,7.6]]];
  const paths=D.accessPaths(p),spans=[];for(const pts of paths)for(let i=1;i<pts.length;i++)spans.push(pts[i-1].map((v,j)=>[Math.min(v,pts[i][j])-.4,Math.max(v,pts[i][j])+.4]));
  if(volumes.some(b=>p.objects.some(o=>!['wallPole','port'].includes(o.type)&&hit(box(o),b))||spans.some(a=>hit(a,b))))throw new Error('Compact : réservez l’accueil surélevé et son escalier avant les machines.');
  const module=(asset,name,x,y,z,r,b,color)=>{const q=modulePart(asset,name,x,y,z,r,color);delete q.livingCircuit;q.signatureBounds=b;q.compactAssembly='inspection-gallery';if(asset==='Roof_Tar_01')q.interiorCeiling=true;out.push(q);return q;};
  const beam=(name,a,b,color,assembly)=>{const len=Math.hypot(...a.map((v,i)=>v-b[i])),n=Math.ceil(len/16);if(len<.05)return;for(let i=0;i<n;i++){const s=a.map((v,j)=>v+(b[j]-v)*i/n),e=a.map((v,j)=>v+(b[j]-v)*(i+1)/n);const q={name,asset:'Beam_Painted',component:'beam',start:s,end:e,x:(s[0]+e[0])/2,y:(s[1]+e[1])/2,z:Math.min(s[2],e[2])-.5,w:Math.abs(e[0]-s[0])+1,d:Math.abs(e[1]-s[1])+1,h:Math.abs(e[2]-s[2])+1,beamRadius:.5,rotation:0,color,zone:'interieur',studyLayer:'interior',compactAssembly:assembly};q.signatureBounds=box(q);out.push(q);}};
  // A diagonal welcome landing joins the straight control gallery. Its raised
  // surface has a 5 cm step at the joint, never a coincident second top face.
  const c=12+2*Math.SQRT2,r=4*Math.SQRT2;
  for(const z of[1.55,2.55])module('Foundation_ConcretePolished_8x1','Accueil · palier diagonal',c,c,z,45,[[c-r,c+r],[c-r,c+r],[z-.5,z+.5]],'#abb7b8');
  const outside=module('Stair_PolishedConcrete_8x2','Accueil · escalier extérieur',12-2*Math.SQRT2,12-2*Math.SQRT2,2.05,45,[[12-6*Math.SQRT2,c],[12-6*Math.SQRT2,c],[1.05,3.05]],'#abb7b8');outside.walkStart=[12-4*Math.SQRT2,12-4*Math.SQRT2,1.05];outside.walkEnd=[12,12,3.05];
  for(let y=20;y<end;y+=8){
   for(const z of[1.5,2.5])module('Foundation_ConcretePolished_8x1','Contrôle · socle continu en béton ciré',12,y,z,0,[[8,16],[y-4,y+4],[z-.5,z+.5]],z===2.5?'#abb7b8':'#263039');
   if(y===20){out.push({name:'Contrôle · porte centrale vers l’escalier',asset:'Wall_Door_8x4_01',component:'wall',x:16.15,y,z:3,w:8,d:.22,h:4,rotation:90,color:palette.frame,zone:'interieur',studyLayer:'interior',compactAssembly:'inspection-gallery'});}
   else {out.push({name:'Contrôle · vitrage continu sans bordure',asset:'Wall_Window_Thin_8x4_01',component:'window',x:16.15,y,z:3.3,w:8,d:.12,h:4,rotation:90,color:'#a8d7df',zone:'interieur',studyLayer:'interior',signatureBounds:[[16.09,16.21],[y-4,y+4],[3.3,7.3]],compactAssembly:'inspection-gallery'});beam('Contrôle · soubassement du vitrage',[16.15,y-4,2.8],[16.15,y+4,2.8],palette.frame,'inspection-gallery');}
   module('Roof_Tar_01','Contrôle · couverture continue',12,y,7.5,0,[[8,16],[y-4,y+4],[7.41,7.59]],'#263039');
  }
  const stairs=module('Stair_PolishedConcrete_8x2','Contrôle · escalier vers la production',20,20,2,180,[[16,24],[16,24],[1,3]],'#abb7b8');stairs.walkStart=[24,20,1];stairs.walkEnd=[16,20,3];
  // Structural support is deliberately mounted into its own overhead carrier.
  for(const[a,b]of power?.carriers||[])beam('Technique · support de distribution au plafond',a,b,'#263039','ceiling-electric');
  // A recessed outline belongs to a machine group. Leave a wide inspection gate
  // in the front edge; the other three sides form a joined painted perimeter.
  const groups=new Map();for(const o of p.objects.filter(o=>o.recipe)){const key=o.native?.module||o.recipe;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(o);}
  for(const [key,objects]of groups){const bb=objects.map(box),x0=Math.min(...bb.map(b=>b[0][0]))-1.1,x1=Math.max(...bb.map(b=>b[0][1]))+1.1,y0=Math.min(...bb.map(b=>b[1][0]))-1.1,y1=Math.max(...bb.map(b=>b[1][1]))+1.1,mid=(x0+x1)/2,before=out.length;
   const edges=[[[x0,y0,.7],[mid-2,y0,.7]],[[mid+2,y0,.7],[x1,y0,.7]],[[x1,y0+.5,.7],[x1,y1-.5,.7]],[[x1,y1,.7],[x0,y1,.7]],[[x0,y1-.5,.7],[x0,y0+.5,.7]]];for(const[a,b]of edges)if(Math.hypot(a[0]-b[0],a[1]-b[1])>=1)beam('Production · délimitation peinte',a,b,'#e6a343','machine-zones');
   const generated=out.slice(before);if(generated.some(q=>p.objects.some(o=>hit(box(q),box(o)))||spans.some(b=>hit(box(q),b))||volumes.some(b=>hit(box(q),b))))out.splice(before);else for(const q of generated)q.machineZone=key;
  }
  return out;
 }

 function validateCompact(p,parts){
  if(p.design?.family!=='compact'||!p.design.living)return;
  const v=p.design.living,n=((p.depth??p.size)-32)/8,items=v.accessParts.filter(q=>q.compactAssembly==='inspection-gallery'),fail=()=>{throw new Error('Intérieur Compact incohérent : réappliquez la création.');};
  const count=a=>items.filter(q=>q.asset===a),near=(a,b)=>Math.abs(a-b)<1e-5,has=(asset,x,y,z)=>items.some(q=>q.asset===asset&&near(q.x,x)&&near(q.y,y)&&near(q.z,z));
  if(v.compactRevision!==4||count('Foundation_ConcretePolished_8x1').length!==2*n+4||count('Wall_Window_Thin_8x4_01').length!==n||count('Roof_Tar_01').length!==n+1||count('Stair_PolishedConcrete_8x2').length!==2||count('Wall_Door_8x4_01').length!==1)fail();
  if(v.accessParts.some(q=>!['inspection-gallery','ceiling-electric','machine-zones'].includes(q.compactAssembly)))fail();
  for(let y=20;y<(p.depth??p.size)-8;y+=8)if(!has('Foundation_ConcretePolished_8x1',12,y,1.5)||!has('Foundation_ConcretePolished_8x1',12,y,2.5)||!has('Roof_Tar_01',12,y,7.5)||(y>20&&!has('Wall_Window_Thin_8x4_01',16.15,y,3.3)))fail();
  if(!has('Wall_Door_8x4_01',16.15,20,3)||!has('Stair_PolishedConcrete_8x2',20,20,2))fail();
  const exterior=parts.filter(q=>q.component==='wall'&&q.asset.includes('Door')&&q.zone!=='interieur');if(exterior.length!==1||exterior[0].asset!=='Wall_Door_8x4_01'||!near(exterior[0].x,12)||!near(exterior[0].y,12)||!near(exterior[0].z,3.05))fail();
  if(p.objects.some(o=>o.type==='storage'))fail();
  const cornice=parts.filter(q=>q.name.includes('Corniche unique'));for(let i=0;i<cornice.length;i++)for(let j=i+1;j<cornice.length;j++)if(box(cornice[i]).every((r,k)=>Math.min(r[1],box(cornice[j])[k][1])-Math.max(r[0],box(cornice[j])[k][0])>1e-6))fail();
  for(const passage of[[[11.3,12.7],[11.3,12.7],[3.15,5.85]],[[15.4,16.9],[19.3,20.7],[3.1,5.8]]])if(parts.some(q=>q.component==='beam'&&hit(box(q),passage)))fail();
  for(const stair of count('Stair_PolishedConcrete_8x2'))if(!stair.walkStart||!stair.walkEnd||rotate(stair.quat,[-1,0,0]).reduce((v,n,i)=>v+n*(stair.walkEnd[i]-stair.walkStart[i])/8,0)<.999||!near(stair.walkEnd[2]-stair.walkStart[2],2)||!near(Math.hypot(stair.walkEnd[0]-stair.walkStart[0],stair.walkEnd[1]-stair.walkStart[1]),8))fail();
  if(p.nativeProfile){const sockets=p.objects.filter(o=>o.native?.ceilingMounted),ids=new Set(sockets.map(o=>o.id));if(!sockets.length||sockets.some(o=>!near(o.z,16.5)))fail();for(const m of p.objects.filter(o=>o.recipe)){const links=p.links.filter(l=>l.kind==='power'&&(l.from===m.id||l.to===m.id));if(links.length!==1||!ids.has(links[0].from===m.id?links[0].to:links[0].from))fail();}}
 }

 function plan(project){
  const D=node?require('./workshop-design'):root.WorkshopDesign,M=node?require('./workshop-model'):root.WorkshopModel,p=M.clone(project),family=p.design?.family;
  if(!D.PRESETS[family]?.nativeStudy)throw new Error('Choisissez une création composée.');
  restorePower(p);const oldLiving=p.design.living,attachmentOrigins={};for(const o of p.objects.filter(o=>o.type==='wallPole'))attachmentOrigins[o.id]=clone(oldLiving?.attachmentOrigins?.[o.id]||{x:o.x,y:o.y,z:o.z,rotation:o.rotation,native:o.native});
  delete p.design.living;const power=family==='compact'?compactPower(p):null;let parts=D.envelope(family==='compact'?{...p,objects:p.objects.filter(o=>o.type!=='wallPole')}:p);continuousFloor(p,parts);if(!power)remountPower(p,parts);parts=parts.filter(q=>q.asset!=='FloodlightWall'&&!(q.studyLayer==='deck'&&box(q)[2][0]>=0&&box(q)[2][1]<=1.8));const solid=parts.filter(q=>q.component!=='module'||q.signatureBounds).map(box),paths=D.accessPaths(p),roofs=parts.filter(q=>q.studyLayer==='roof'||q.studyLayer==='deck').map(box),palette=palettes[family]||palettes.atlas,levels=[],fixtures=[];
  for(const f of p.floors||[]){const z=f.z+f.thickness;
   const choices=family==='compact'?wallMounts(parts,p,14).map(m=>({...m,lampZ:14})):[...wallMounts(parts,p,z+6).map(m=>({...m,lampZ:z+6})),...wallMounts(parts,p,z+3.9).map(m=>({...m,lampZ:z+3.9})),...wallMounts(parts,p,z+3.1).map(m=>({...m,lampZ:z+3.1}))],selected=[];
   for(const mount of choices){
    if(selected.some(m=>Math.hypot(m.position[0]-mount.position[0],m.position[1]-mount.position[1])<12))continue;
    const socketMount=wallMounts(parts,p,mount.lampZ-2.1).find(m=>Math.hypot(m.position[0]-mount.position[0],m.position[1]-mount.position[1])<.01);if(!socketMount)continue;const group='living-'+z+'-'+selected.length,lamp=mountedPart('FloodlightWall','Intérieur · projecteur mural',mount,mount.lampZ,palette.light,group),support=mountedPart('PowerPoleWall','Intérieur · raccord fixé au mur',socketMount,mount.lampZ-2.1,palette.frame,group);
    if(family==='compact'){lamp.lightIntensity=100;const a=mount.axis;lamp.signatureBounds[a]=mount.normal[a]>0?[mount.position[a]+.01,mount.position[a]+6.5]:[mount.position[a]-6.5,mount.position[a]-.01];}
    const blocked=q=>parts.some(part=>part!==mount.wall&&part!==socketMount.wall&&hit(box(q),box(part)))||p.objects.some(o=>hit(box(q),box(o)));
    if(blocked(lamp)||blocked(support))continue;
    fixtures.push(support,lamp);selected.push(mount);if(selected.length>=(family==='compact'?8:4))break;
   }
   if(!selected.length)throw new Error('Aucun emplacement mural dégagé pour les projecteurs au niveau '+z+' m.');
   const cells=D.floorCells(p,f),allowed=new Set(cells.map(c=>c.join(','))),obstacles=p.objects.filter(o=>!['port','pole','wallPole'].includes(o.type)).map(o=>{const b=M.bounds(o);return[[b.minX,b.maxX],[b.minY,b.maxY],[o.z||0,(o.z||0)+(o.h||6)]];}).concat(solid,fixtures.map(box)),network=[];
   for(const pts of paths)for(let i=1;i<pts.length;i++)network.push(pts[i-1].map((v,j)=>[Math.min(v,pts[i][j])-.3,Math.max(v,pts[i][j])+.3]));
   const nodes=new Map();for(let x=1;x<p.size;x+=2)for(let y=1;y<M.depth(p);y+=2){if(family==='compact'&&(x<10||y<10||x>p.size-10||y>M.depth(p)-10||x+y<27||x<17&&y>=20))continue;if(!allowed.has(Math.floor(x/8)+','+Math.floor(y/8)))continue;const volume=[[x-1.2,x+1.2],[y-1.2,y+1.2],[z+.12,z+2.7]];if(obstacles.some(b=>hit(volume,b))||network.some(b=>hit(volume,b)))continue;nodes.set(x+','+y,[x,y]);}
   const neighbors=k=>{const[x,y]=nodes.get(k);return[[x-2,y],[x+2,y],[x,y-2],[x,y+2]].map(c=>c.join(',')).filter(k=>nodes.has(k));};
   const unseen=new Set(nodes.keys());let component=[],componentScore=-1;while(unseen.size){const queue=[unseen.values().next().value];unseen.delete(queue[0]);for(let i=0;i<queue.length;i++)for(const k of neighbors(queue[i]))if(unseen.delete(k))queue.push(k);const score=p.objects.filter(o=>o.recipe&&Math.abs((o.z||0)-z)<.2).filter(o=>{const b=M.bounds(o);return queue.some(k=>{const[x,y]=nodes.get(k);return Math.hypot(Math.max(b.minX-x,0,x-b.maxX),Math.max(b.minY-y,0,y-b.maxY))<=4;});}).length;if(score>componentScore||score===componentScore&&queue.length>component.length){component=queue;componentScore=score;}}
   if(!component.length){levels.push({z,paths:[],stations:[],missing:p.objects.filter(o=>o.recipe&&Math.abs(o.z-z)<.2).map(o=>o.name)});continue;}
   component.sort((a,b)=>family==='compact'?Math.hypot(nodes.get(a)[0]-25,nodes.get(a)[1]-19)-Math.hypot(nodes.get(b)[0]-25,nodes.get(b)[1]-19):nodes.get(a)[1]-nodes.get(b)[1]||nodes.get(a)[0]-nodes.get(b)[0]);const rootKey=component[0],prev=new Map([[rootKey,null]]),queue=[rootKey];for(let i=0;i<queue.length;i++)for(const k of neighbors(queue[i]))if(!prev.has(k)){prev.set(k,queue[i]);queue.push(k);}
   const route=new Set([rootKey]),stations=[],missing=[];
   for(const o of p.objects.filter(o=>o.recipe&&Math.abs((o.z||0)-z)<.2)){const b=M.bounds(o),choices=component.map(k=>{const[x,y]=nodes.get(k),dx=Math.max(b.minX-x,0,x-b.maxX),dy=Math.max(b.minY-y,0,y-b.maxY);return{k,d:Math.hypot(dx,dy)};}).filter(v=>v.d<=4).sort((a,b)=>a.d-b.d);if(!choices.length){missing.push(o.name);continue;}let k=choices[0].k;stations.push({id:o.id,name:o.name,point:[...nodes.get(k),z]});while(k!==null){route.add(k);k=prev.get(k);}}
   if(family==='compact')for(const target of[[25,19]]){
    const keys=component.slice().sort((a,b)=>Math.hypot(nodes.get(a)[0]-target[0],nodes.get(a)[1]-target[1])-Math.hypot(nodes.get(b)[0]-target[0],nodes.get(b)[1]-target[1]));let k=keys[0];
    if(!k||Math.hypot(nodes.get(k)[0]-target[0],nodes.get(k)[1]-target[1])>3)throw new Error('Compact : l’escalier doit rejoindre la circulation intérieure.');
    while(k!==null){route.add(k);k=prev.get(k);}
   }
   const routePoints=[...route].map(k=>[...nodes.get(k),z]);levels.push({z,paths:routePoints,stations,missing});
  }
  if(['atlas','sylva'].includes(family)&&levels.length>1&&p.design.studyFloors){if(p.objects.some(o=>o.recipe&&(o.z||0)>levels[0].z+.2&&M.bounds(o).minX<8))throw new Error('La cage d’escalier nécessite une bande libre de 8 m à gauche.');for(const row of p.design.studyFloors)if(row.z>0)row.cells=row.cells.filter(c=>c[0]>0);}
  const circulation=['atlas','sylva'].includes(family)?access(p,levels,palette):{parts:[],openings:[]};
  if(family==='compact'){
   if(levels.some(l=>l.missing.length))throw new Error('Compact : certaines machines ne disposent pas d’un passage d’inspection. Réorganisez la production.');
   if(levels.length!==1||levels[0].z!==1)throw new Error('Compact : un niveau de production au sol uniquement.');
   compactLightingFeeds(p,power,fixtures);circulation.parts=compactInterior(p,parts,levels,fixtures,palette,power);
  }
  const attachmentAnchors={};for(const o of p.objects.filter(o=>o.type==='wallPole'))attachmentAnchors[o.id]={x:o.x,y:o.y,z:o.z,rotation:o.rotation};
  p.design.living={version:1,revision:2,snapshot:snapshot(p),palette,levels,fixtures,accessParts:circulation.parts,openings:circulation.openings,attachmentOrigins,attachmentAnchors,...(family==='compact'?{compactRevision:4,powerOriginal:power?.original,powerGenerated:power?.generated}:{} )};D.envelope(p);return p;
 }
 function floorColor(p,f,x,y,fallback){if((node?require('./architecture-catalog'):root.ArchitectureCatalog).studies[p.design?.family]?.designFirst&&!p.design?.living)return (node?require('./design-campus'):root.DesignCampus).floorColor(p,f,x,y,fallback);const v=p.design?.living;if(!v)return fallback;const level=v.levels.find(l=>Math.abs(l.z-f.z-f.thickness)<.05);if(!level)return fallback;const within=q=>q[0]>=x-4&&q[0]<x+4&&q[1]>=y-4&&q[1]<y+4;return level.stations.some(s=>within(s.point))?v.palette.pad:level.paths.some(within)?v.palette.lane:v.palette.floor;}
 function power(p){if(p.nativeProfile==='clean-manifold-v1')return p.manifoldInterior.parts.filter(q=>q.asset==='FloodlightWall').length*6;if(!p.design?.enabled||!p.design?.living)return 0;const D=node?require('./workshop-design'):root.WorkshopDesign;return D.envelope(p).filter(q=>q.asset==='FloodlightWall').length*(D.CATALOG.livingLighting?.FloodlightWall?.powerMW||0);}
 const api={powerPoint,validateCompact,restorePower,cleanParts,wallMounts,terraces,snapshot,matches,power,palettes,transform,plan,floorColor,box,hit};if(node)module.exports=api;else root.CreationLiving=api;
})(typeof globalThis!=='undefined'?globalThis:this);
