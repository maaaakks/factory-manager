'use strict';
(function(root){
 const library=typeof module!=='undefined'&&module.exports?require('./m05-library.js'):root.M05Library;
 const rotate=(q,[a,b,c])=>{const[x,y,z,w]=q;return[(1-2*y*y-2*z*z)*a+(2*x*y-2*z*w)*b+(2*x*z+2*y*w)*c,(2*x*y+2*z*w)*a+(1-2*x*x-2*z*z)*b+(2*y*z-2*x*w)*c,(2*x*z-2*y*w)*a+(2*y*z+2*x*w)*b+(1-2*x*x-2*y*y)*c];};
 const turn=([x,y,z],n)=>{for(let i=0;i<((n%4)+4)%4;i++)[x,y]=[-y,x];return[x,y,z];};
 function layout(p){
  const width=p.size,depth=p.depth??width,height=p.height??width,nx=Math.floor(width/40),ny=Math.floor(depth/40),variant=(p.design?.variant||1)-1;
  if(nx<2||ny<2||height<40)throw new Error('M05 réel : 80 × 80 m minimum, hauteur 40 m. Ses modules de 40 m gardent leurs dimensions originales.');
  if(Math.max(0,...p.objects.map(o=>(o.z||0)+(o.h||6)))>30.6)throw new Error('M05 : le volume intérieur libre monte jusqu’à 30,6 m. Ce plan est trop haut pour les modules originaux ; choisissez un autre style.');
  if(nx*ny>64)throw new Error('M05 : 64 modules maximum par assemblage pour garder une vue fluide.');
  const ox=(width-nx*40)/2,oy=(depth-ny*40)/2,placements=[];
  const clashes=p.objects.filter(o=>{if(['input','output'].includes(o.type))return false;const r=(o.rotation||0)%180,w=(r?o.d:o.w)/2,d=(r?o.w:o.d)/2;return o.x-w<ox+24-.01||o.x+w>width-ox-24+.01||o.y-d<oy+24-.01||o.y+d>depth-oy-24+.01;});
  if(clashes.length)throw new Error('M05 : '+clashes.slice(0,2).map(o=>o.name).join(', ')+' empiète sur la bande de 24 m réservée aux modules. Utilisez « Réserver la marge » pour agrandir et centrer le plan.');
  const front=[1,2,3,4,5,6][variant%6],other=[2,1,4,3,6,5][variant%6];
  for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
   const left=x===0,right=x===nx-1,top=y===0,bottom=y===ny-1;let name,rotation=0;
   if((left||right)&&(top||bottom)){name='C'+(variant%3===0?1:variant%3===1?2:((x===0)===(y===0)?1:2));rotation=top?(right?0:3):(right?1:2);}
   else if(top||bottom||left||right){const side=top||bottom,index=side?Math.min(x,nx-1-x):Math.min(y,ny-1-y);name='M'+(side?(index%2?front:other):(index%2?other:front));rotation=top?0:right?1:bottom?2:3;}
   else name='IN1';
   placements.push({name,x:ox+20+x*40,y:oy+20+y*40,z:0,turn:rotation});
  }
  return placements;
 }
 function envelope(p){
  const parts=[],seen=new Set();
  for(const tile of layout(p))library.modules[tile.name].parts.forEach((source,index)=>{
   if(!p.design.roof&&source.asset.startsWith('Roof_'))return;
   const local=turn(source.pos,tile.turn),pos=[local[0]+tile.x,local[1]+tile.y,local[2]+tile.z];
   // Neighbour tiles sometimes share a seam actor. Keep one exact pose only.
   const basis=[[1,0,0],[0,1,0],[0,0,1]].flatMap(v=>turn(rotate(source.quat,v),tile.turn)).map(v=>Math.round(v*10000));
   const key=source.asset+'|'+pos.map(v=>Math.round(v*1000))+'|'+basis+'|'+(source.length||0)+(source.asset==='PowerLine'?'|'+tile.x+','+tile.y+','+index:'');if(seen.has(key))return;seen.add(key);
   parts.push({name:tile.name+' · '+source.asset,component:'module',asset:source.asset,sourceModule:tile.name,sourceIndex:index,origin:[tile.x,tile.y,tile.z],turn:tile.turn,x:pos[0],y:pos[1],z:pos[2],w:0,d:0,h:source.asset.startsWith('Wall')?4:1,rotation:tile.turn*90,color:source.color});
  });return parts;
 }
 function geometry(part){
  const source=library.modules[part.sourceModule].parts[part.sourceIndex],asset=part.asset,faces=[];
  const point=v=>{const a=part.quat?rotate(part.quat,v):turn(rotate(source.quat,v),part.turn);return[a[0]+part.x,a[1]+part.y,a[2]+part.z];};
  const poly=(points,color=part.color||source.color,glass=false)=>faces.push({coords:points.map(point),color,glass});
  const cube=(x,y,z,w,d,h,color=part.color||source.color)=>{const v=[];for(const zz of [z,z+h])for(const[xx,yy]of [[x-w/2,y-d/2],[x+w/2,y-d/2],[x+w/2,y+d/2],[x-w/2,y+d/2]])v.push([xx,yy,zz]);for(const f of [[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]])poly(f.map(i=>v[i]),color);};
  const rod=(a,b,width=.1,color='#303a3d')=>{const dx=b[0]-a[0],dy=b[1]-a[1],dz=b[2]-a[2],len=Math.hypot(dx,dy,dz);if(!len)return;const n=Math.hypot(dx,dy),u=n>1e-8?[-dy/n*width/2,dx/n*width/2,0]:[width/2,0,0],v=[(dy*u[2]-dz*u[1])/len,(dz*u[0]-dx*u[2])/len,(dx*u[1]-dy*u[0])/len],c=[];for(const p of [a,b])for(const [i,j]of [[-1,-1],[1,-1],[1,1],[-1,1]])c.push(p.map((q,k)=>q+i*u[k]+j*v[k]));for(const f of [[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])poly(f.map(i=>c[i]),color);};
  const glass=(points,diagonal=false)=>{const frame=part.nativeShell&&part.paintFinish?part.color:'#303a3d';poly(points,part.nativeShell?'#b3d1cc':part.color||'#8bb9c4',true);for(let i=0;i<points.length;i++)rod(points[i],points[(i+1)%points.length],part.asset==='FoundationGlass_01'?.24:.13,frame);if(diagonal){rod(points[0],points[2],.075,frame);rod(points[1],points[3],.075,frame);}};
  if(asset==='StandaloneWidgetSign_SmallVeryWide'){cube(0,0,-.5,4,.12,1,part.color||'#ddf7f4');return faces;}
  if(asset.startsWith('StandaloneWidgetSign')){cube(0,0,-1.5,.14,2,3,part.color||'#b7f5fa');return faces;}
  if(asset==='PowerLine'){return [];}
  if(asset==='BigGarageDoor_16x8'){cube(0,-7.5,0,.6,1,8);cube(0,7.5,0,.6,1,8);cube(0,0,7.2,.6,14,.8);cube(.05,0,0,.12,14,7.1,'#53646a');return faces;}
  if(asset.startsWith('Beam_')){
   if(source.length){const L=part.beamLength??source.length;if(asset==='Beam_H'){cube(L/2,0,-.26,L,.55,.09);cube(L/2,0,.17,L,.55,.09);cube(L/2,0,-.17,L,.085,.34);}else {const r=part.beamRadius??.15;cube(L/2,0,-r,L,r*2,r*2);}}
   else cube(0,0,-.3,.8,.8,.6);return faces;
  }
  if(asset==='Wall_Gate_8x4_01'){cube(0,-3,0,.22,2,4);cube(0,3,0,.22,2,4);cube(0,0,3,.22,4,1);return faces;}
  if(asset==='Wall_Door_8x4_01'){cube(0,-2.5,0,.22,3,4);cube(0,2.5,0,.22,3,4);cube(0,0,3,.22,2,1);return faces;}
  if(asset.startsWith('Stair_PolishedConcrete_8x')){const rise=asset.endsWith('8x1')?1:2;for(let i=0;i<16;i++)cube(4-(i+.5)*.5,0,-rise/2,.5,8,(i+1)*rise/16);return faces;}
  if(asset==='Wall_Door_8x4_03'){cube(0,-3,0,.22,2,4);cube(0,3,0,.22,2,4);cube(0,0,3,.22,4,1);return faces;}
  if(asset==='FoundationGlass_01'){glass([[-4,-4,.5],[4,-4,.5],[4,4,.5],[-4,4,.5]]);return faces;}
  if(asset.startsWith('Pillar')){const w=asset.includes('Small')?1:2;cube(0,0,-2,w,w,4);return faces;}
  if(asset==='Fence_01'){for(const y of[-4,4])rod([0,y,0],[0,y,1],.1);rod([0,-4,1],[0,4,1],.12);rod([0,-4,.5],[0,4,.5],.08);return faces;}
  if(asset.startsWith('Foundation')){const h=asset.includes('8x1')?1:asset.includes('8x2')?2:4;cube(0,0,-h/2,8,8,h);return faces;}
  if(asset.startsWith('Wall_')){
   const h=asset.includes('8x8')?8:asset.includes('8x1')?1:asset.includes('8x2')?2:4;
   if(asset.includes('Window')){
    const pts=[[-.02,-4,0],[-.02,4,0],[-.02,4,h],[-.02,-4,h]];glass(pts,asset.includes('Thin'));
    if(asset.includes('_05')){rod([-.03,0,0],[-.03,0,h],.13);rod([-.03,-4,h/2],[-.03,4,h/2],.13);}return faces;
   }
   if(asset.includes('Tris')){const flip=asset.includes('Flip'),p=[[0,-4,flip?h:0],[0,4,0],[0,flip?4:-4,h]];if(part.nativeShell){const front=p.map(v=>[.12,v[1],v[2]]),back=p.map(v=>[-.12,v[1],v[2]]);poly(front);poly(back.slice().reverse());for(let i=0;i<3;i++)poly([front[i],front[(i+1)%3],back[(i+1)%3],back[i]]);}else poly(p);return faces;}
   if(asset.includes('Corner')||asset.includes('Angular')){poly([[0,-4,0],[4,0,0],[4,0,h],[0,-4,h]]);return faces;}
   if(asset.includes('Door')||asset.includes('Gate')){cube(0,-2.75,0,.22,2.5,h);cube(0,2.75,0,.22,2.5,h);cube(0,0,h-.7,.22,3,.7);return faces;}
   if(asset.includes('Conveyor')){cube(0,-3,0,.22,2,h);cube(0,3,0,.22,2,h);cube(0,0,0,.22,4,1);cube(0,0,h-1,.22,4,1);return faces;}
   cube(0,0,0,.22,8,h);return faces;
  }
  if(asset.startsWith('Roof_')){
   const slope=asset.endsWith('_04')?4:asset.endsWith('_03')?2:asset.endsWith('_02')?1:0;
   const z=(x,y)=>-(asset.includes('InCorner')?Math.min(x,y):asset.includes('OutCorner')?Math.max(x,y):x)*slope/8;
   const pts=[[-4,-4,z(-4,-4)],[4,-4,z(4,-4)],[4,4,z(4,4)],[-4,4,z(-4,4)]];
   if(asset.includes('Window')){glass(pts);rod([0,-4,0],[0,4,0],.12);rod([-4,0,slope/2],[4,0,-slope/2],.12);}
   else {poly(pts,part.color||'#333c3b');for(let i=0;i<4;i++)rod(pts[i],pts[(i+1)%4],.18,'#424b48');}
   return faces;
  }
  if(asset.includes('Catwalk')){const rise=asset.includes('Stairs')?4:asset.includes('Ramp')?2:0;if(rise){for(let i=0;i<16;i++)cube(-2+(i+.5)*.25,0,i*rise/16,.25,4,.12,part.color||'#72766c');for(const y of[-1.85,1.85]){rod([-2,y,1],[2,y,rise+1],.09);for(const x of[-2,0,2])rod([x,y,(x+2)*rise/4],[x,y,(x+2)*rise/4+1],.07);}}else{cube(0,0,-.15,4,4,.15,part.color||'#59605a');if(asset==='CatwalkStraight')for(const y of[-1.85,1.85]){rod([-2,y,1],[2,y,1],.09);for(const x of[-2,2])rod([x,y,0],[x,y,1],.07);}}return faces;}
  if(asset.includes('Railing')){rod([0,-2,.95],[0,2,.95],.08,'#c29b51');rod([0,-2,.45],[0,2,.45],.06);for(const y of [-1.95,1.95])rod([0,y,0],[0,y,1],.08);return faces;}
  if(asset==='Ladder'){const h=(source.segments||4)*2;for(const y of [-.35,.35])rod([0,y,0],[0,y,h],.08);for(let z=.2;z<h;z+=.4)rod([0,-.35,z],[0,.35,z],.05);return faces;}
  if(asset.includes('LargeFan')||asset.includes('LargeVent')){
   // Native fan/vent faces lie in local YZ, normal +X. Saved quaternions
   // mount fans on walls and turn the roof vents upwards.
   const radius=asset.includes('Fan')?1.45:1.15,n=16,disk=([u,v,w])=>[w,u,v];
   poly(Array.from({length:n},(_,i)=>disk([Math.cos(i*2*Math.PI/n)*radius,Math.sin(i*2*Math.PI/n)*radius,.12])),'#1d292b');
   for(let i=0;i<n;i++){const a=i*2*Math.PI/n,b=(i+1)*2*Math.PI/n;rod(disk([Math.cos(a)*radius,Math.sin(a)*radius,.18]),disk([Math.cos(b)*radius,Math.sin(b)*radius,.18]),.18,'#e4a351');}
   for(let i=0;i<5;i++){const a=i*2*Math.PI/5;poly([[0,0,.2],[Math.cos(a)*radius*.8,Math.sin(a)*radius*.8,.2],[Math.cos(a+.6)*radius*.5,Math.sin(a+.6)*radius*.5,.2]].map(disk),'#8b9690');}return faces;
  }
  if(asset.includes('Floodlight')){cube(0,0,0,1,.4,.5,'#e1dab1');return faces;}
  if(asset.includes('PowerPole')){cube(0,0,0,.25,.4,.25,'#777c76');return faces;}
  if(asset.includes('QuarterPipe')){poly([[0,-4,0],[0,4,0],[4,4,4],[4,-4,4]],'#a6a99d');return faces;}
  if(asset.includes('PipelineSupport')){cube(0,0,0,.5,.5,.5,'#414b4b');return faces;}
  return faces;
 }
 function beamGeometry(part){const [dx,dy,dz]=part.end.map((v,i)=>v-part.start[i]),length=Math.hypot(dx,dy,dz);if(length<1e-8)return[];const x=dx/length,y=dy/length,z=dz/length,q=x>-.999999?[0,-z,y,1+x]:[0,0,1,0],norm=Math.hypot(...q),quat=q.map(v=>v/norm),index=library.modules.M2.parts.findIndex(p=>p.asset==='Beam_H'&&p.length);return geometry({...part,component:'module',sourceModule:'M2',sourceIndex:index,beamLength:length,quat,x:part.start[0],y:part.start[1],z:part.start[2]});}
 function report(p){const tiles=layout(p),counts={};for(const t of tiles)counts[t.name]=(counts[t.name]||0)+1;return Object.entries(counts).map(([id,n])=>n+' × '+id).join(' · ');}
 const api={library,layout,envelope,geometry,beamGeometry,report,rotate,turn};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.M05Modules=api;
})(typeof globalThis!=='undefined'?globalThis:this);
