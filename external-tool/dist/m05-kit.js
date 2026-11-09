'use strict';
(function(root){
 const F=typeof module!=='undefined'&&module.exports?require('./m05-facade.js'):root.M05Facade;
 const L=typeof module!=='undefined'&&module.exports?require('./m05-library.js'):root.M05Library;
 // The grammar selects accents, rather than wrapping all four sides in the
 // same complete 40 m module. Native asset dimensions are never scaled.
 function profile(seed,side){const front=Math.floor((seed-1)/3)%4,secondary=(front+1)%4;return side===front?(seed-1)%3:seed%2===0&&side===secondary?seed%3:-1;}
 function recess(x,y,z,h,top,b,seed){
  const [x0,x1,y0,y1]=b,front=Math.floor((seed-1)/3)%4;
  for(let side=0;side<4;side++){
   const motif=profile(seed,side),edge=[y===y0,x===x1,y===y1,x===x0][side],u=side%2?y:x,lo=side%2?y0:x0,hi=side%2?y1:x1,mid=Math.floor((lo+hi)/2);
   if(motif<0||!edge||hi-lo<2||z<4||z+h>top-4)continue;
   // M3: a single inset bay. M4: glass tower with recessed shoulders.
   // M6: two tiers of recessed galleries. Occupancy is checked by the caller.
   if(motif===0&&u===mid&&z>=8)return true;
   if(motif===1&&u>lo&&u<hi&&u!==mid&&z>=8)return true;
   if(motif===2&&u===mid&&Math.floor(z/4)%4!==0&&Math.floor(z/4)%4!==3)return true;
  }
  // A clipped upper corner gives the C2 tiered silhouette where it is free.
  return seed%2===0&&x1-x0>=3&&y1-y0>=3&&z>=top-8&&z+h<=top-4&&((front<2&&x===x1&&y===y0)||(front>=2&&x===x0&&y===y1));
 }
 function windowAt(start,side,z,top,size,seed){
  const bay=Math.floor(start/8),n=size/8,motif=profile(seed,side),center=Math.abs(bay-(n-1)/2)<1,corner=bay===0||bay===n-1;
  if(corner)return z>=4&&z<top-4; // C1/C2 glazing wraps the corner piers.
  if(motif===0)return z===4||z>=top-8;
  if(motif===1)return center&&z>=4||z>=top-4;
  if(motif===2)return Math.floor(z/4)%3!==0;
  return z===4||z>=top-4;
 }
 function decorate(parts,p,paths=[]){
  const columns=parts.filter(q=>q.name==='Angle · montant unique');
  const result=parts.flatMap(q=>{
   if(q.name==='Angle · bardage ajusté'){
    const a=[...q.start],b=[...q.end],axis=Math.abs(b[0]-a[0])>.01?0:1;
    for(const v of[a,b])if(columns.some(c=>Math.hypot(v[0]-c.x,v[1]-c.y)<.6))v[axis]+=(b[axis]>a[axis]?1:-1)*(v===a?-.25:.25);
    return[-.32,0,.32].map(dz=>{const start=[a[0],a[1],a[2]+dz],end=[b[0],b[1],b[2]+dz],lo=start.map((v,i)=>Math.min(v,end[i])-.15),hi=start.map((v,i)=>Math.max(v,end[i])+.15);return{...q,asset:'Beam_Painted',start,end,x:(start[0]+end[0])/2,y:(start[1]+end[1])/2,z:lo[2],w:hi[0]-lo[0],d:hi[1]-lo[1],h:hi[2]-lo[2],panelUnits:(q.panelUnits||0)/3};});
   }
   return[q.component==='window'&&q.h===4?{...q,asset:'Wall_Window_Thin_8x4_02'}:q.component==='beam'?{...q,asset:'Beam_H'}:q];
  });
  for(const q of parts){
   const side=q.rotation/90,u=side%2?q.y:q.x,seed=p.design.seed||1,motif=profile(seed,side);
   if(motif<0||q.component!=='wall'||q.h!==4||q.z<4||q.z%8!==0)continue;
   const sourceModule=['M3','M4','M6'][motif],index=L.modules[sourceModule].parts.findIndex(p=>p.asset==='LargeFan');
   if(index<0)continue;
   const a=(q.rotation-90)*Math.PI/180,round=v=>Math.round(v*1e9)/1e9,clamp=(v,n)=>round(Math.max(.6,Math.min(n-.6,v)));
   result.push({name:sourceModule+' · Ventilation',component:'module',asset:'LargeFan',sourceModule,sourceIndex:index,origin:[0,0,0],turn:0,quat:[0,0,round(Math.sin(a/2)),round(Math.cos(a/2))],x:clamp(q.x+Math.cos(a)*.35,p.size),y:clamp(q.y+Math.sin(a)*.35,p.depth??p.size),z:q.z+2,w:0,d:0,h:0,rotation:q.rotation-90,color:'#ef922b'});
  }return (typeof module!=='undefined'&&module.exports?require('./m05-roof.js'):root.M05Roof).apply(F.apply(result,p,paths),p,paths);
 }
 const api={decorate,profile,recess,windowAt};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.M05Kit=api;
})(typeof globalThis!=='undefined'?globalThis:this);
