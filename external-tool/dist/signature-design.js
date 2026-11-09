'use strict';
(function(root){
 // A small authored grammar: one silhouette, material hierarchy and detail
 // budget per composition. Occupied cells are retained by facadeBands.
 const labels=['Horizon','Faille','Ossature'];
 function recess(x,y,z,h,top,b,seed){
  const [x0,x1,y0,y1]=b,n=x1-x0+1,m=y1-y0+1,k=(seed-1)%3;
  if(n<3||m<3)return false;
  const upper=z>=Math.max(4,top-8);
  if(k===0)return upper&&((y===y0&&x>=x0+Math.ceil(n*.6))||(x===x1&&y===y1));
  if(k===1)return y===y0&&x===x0+Math.floor(n/3)||upper&&x===x1&&y>=y0+Math.ceil(m*.65);
  return upper&&((x===x0&&y===y0)||(x===x1&&y===y1));
 }
 function windowAt(start,side,z,top,size,seed){
  const bay=Math.floor(start/8),n=size/8,k=(seed-1)%3;
  if(z===0)return false;
  if(k===0)return(z===4||z>=top-4)&&(side%2===0||bay%3!==0);
  if(k===1)return z>=4&&(Math.abs(bay-n*.65)<1||z>=top-4);
  return z>=top-4||bay%3===1;
 }
 function decorate(parts,p,paths,style){
  const width=p.size,depth=p.depth??width,height=p.height??width,mode=(p.design.seed-1)%3;
  const bounds=q=>{let w=q.w,d=q.d;if(q.rotation%180)[w,d]=[d,w];return[[q.x-w/2,q.x+w/2],[q.y-d/2,q.y+d/2],[q.z,q.z+q.h]];};
  const obstacles=p.objects.map(q=>bounds({...q,z:q.z||0,h:q.h||6}));
  for(const points of paths)for(let i=1;i<points.length;i++)obstacles.push([0,1,2].map(j=>[Math.min(points[i-1][j],points[i][j])-.75,Math.max(points[i-1][j],points[i][j])+.75]));
  for(const q of parts)if(q.name.startsWith('Entrée piétonne'))obstacles.push(bounds(q));
  const overlap=(a,b)=>a.every((r,i)=>Math.min(r[1],b[i][1])-Math.max(r[0],b[i][0])>.01);
  const free=b=>b.every((r,i)=>r[0]>=-.001&&r[1]<=[width,depth,height][i]+.001)&&!obstacles.some(o=>overlap(b,o));
  const result=parts.flatMap(q=>{
   const color=q.component==='roof'?(/Window/.test(q.asset)?style.window:style.trim):q.component==='wall'?q.z<4?style.trim:style.wall:q.component==='beam'&&!q.panelUnits?style.trim:q.color;
   if(q.name==='Angle · bardage ajusté')return[-.32,0,.32].map(dz=>{const start=q.start.map((v,i)=>v+(i===2?dz:0)),end=q.end.map((v,i)=>v+(i===2?dz:0)),lo=start.map((v,i)=>Math.min(v,end[i])-.15),hi=start.map((v,i)=>Math.max(v,end[i])+.15);return{...q,start,end,x:(start[0]+end[0])/2,y:(start[1]+end[1])/2,z:lo[2],w:hi[0]-lo[0],d:hi[1]-lo[1],h:hi[2]-lo[2],color:q.z<4?style.trim:style.wall,panelUnits:(q.panelUnits||0)/3};});
   return[{...q,color,...(q.component==='window'?{asset:'Wall_Window_Thin_8x4_02'}:{})}];
  });
  function beam(name,a,b,color=style.trim){
   const length=Math.hypot(...a.map((v,i)=>b[i]-v));if(length<.1)return;
   const count=Math.ceil(length/16);
   for(let i=0;i<count;i++){
    const at=t=>a.map((v,j)=>v+(b[j]-v)*t),start=at(i/count),end=at((i+1)/count),lo=start.map((v,j)=>Math.min(v,end[j])-.15),hi=start.map((v,j)=>Math.max(v,end[j])+.15),box=lo.map((v,j)=>[v,hi[j]]);
    if(!free(box))continue;
    result.push({name:'Signature · '+name,x:(start[0]+end[0])/2,y:(start[1]+end[1])/2,z:lo[2],w:hi[0]-lo[0],d:hi[1]-lo[1],h:hi[2]-lo[2],rotation:0,color,component:'beam',asset:'Beam_Painted',start,end});
   }
  }
  // One faceted portal supplies the long angled line. Both ends meet the
  // ground; the complete feature is omitted if any segment is obstructed.
  const front=parts.filter(q=>['wall','window'].includes(q.component)&&q.rotation===0),line=front.length?Math.min(...front.map(q=>q.y)):0,face=front.filter(q=>Math.abs(q.y-line)<.01);
  if(face.length){
   for(const lo of[.8,8.8,Math.max(.8,width-24.8)]){const hi=Math.min(lo+22.4,width-.8),top=Math.max(...face.map(q=>q.z+q.h));
   if(hi-lo>=14&&top>=8){
    const bottom=(p.floors?.find(f=>f.z===0)?.thickness||1)+.3,y=line-.65,z=top-.5,cut=Math.min(4,(hi-lo)/5,top/3),points=[[lo,y,bottom],[lo,y,z-cut],[lo+cut,y,z],[hi-cut,y,z],[hi,y,z-cut],[hi,y,bottom]];
    const fits=points.slice(1).every((b,i)=>free(points[i].map((v,j)=>[Math.min(v,b[j])-.15,Math.max(v,b[j])+.15])));
    if(fits){for(let i=1;i<points.length;i++)beam('Portique facetté',points[i-1],points[i],mode===2?style.accent:style.trim);break;}
   }
   }
  }
  const point=(q,u,z,offset)=>{const side=q.rotation/90,sign=[-1,1,1,-1][side];return side%2?[q.x+sign*offset,q.y+u,z]:[q.x+u,q.y+sign*offset,z];};
  // Two separate depth planes: reveal at 0.35 m, selected fins at 0.65 m.
  for(const q of parts){
   if(q.component==='window'&&q.h===4&&!q.name.startsWith('Lanterneau')){
    beam('Appui de baie',point(q,-3.7,q.z+.2,.35),point(q,3.7,q.z+.2,.35));
    beam('Linteau de baie',point(q,-3.7,q.z+3.8,.35),point(q,3.7,q.z+3.8,.35));
    for(const u of[-3.7,3.7])beam('Tableau de baie',point(q,u,q.z+.2,.35),point(q,u,q.z+3.8,.35));
    const bay=Math.floor((q.rotation%180?q.y:q.x)/8);
    if((q.rotation/90+bay)%3===0)beam('Lame verticale',point(q,-2.5,q.z+.25,.65),point(q,-2.5,q.z+3.75,.65),style.accent);
   }
  }
  // One louvred service panel per side, rather than ornament on every tile.
  const serviced=new Set();
  for(const q of parts){
   if(q.component!=='wall'||q.h!==4||q.z<4||serviced.has(q.rotation))continue;
   serviced.add(q.rotation);
   for(let i=0;i<5;i++)beam('Persienne technique',point(q,-2.7,q.z+.8+i*.55,.6),point(q,2.7,q.z+.8+i*.55,.6));
   if(mode===2)beam('Contreventement ponctuel',point(q,-3.5,q.z+.4,.7),point(q,3.5,q.z+3.6,.7),style.accent);
  }
  // Roof edges follow each real setback, including low terraces.
  if(p.design.roof){
   const roofs=parts.filter(q=>q.component==='roof'&&!q.name.startsWith('Sous-face'));
   for(const q of roofs)for(const [dx,dy]of[[0,-1],[1,0],[0,1],[-1,0]]){
    if(roofs.some(r=>Math.abs(r.x-q.x-dx*8)<.01&&Math.abs(r.y-q.y-dy*8)<.01&&Math.abs(r.z-q.z)<.1))continue;
    const z=q.z+.7;
    if(dx)beam('Rive de toiture',[q.x+dx*3.7,q.y-3.7,z],[q.x+dx*3.7,q.y+3.7,z]);
    else beam('Rive de toiture',[q.x-3.7,q.y+dy*3.7,z],[q.x+3.7,q.y+dy*3.7,z]);
   }
  }
  // A restrained accent marks the existing safe entrance; it is solid paint.
  for(const q of parts)if(q.name==='Entrée piétonne · linteau')beam('Repère entrée',q.start.map((v,i)=>v+(i===2?.4:0)),q.end.map((v,i)=>v+(i===2?.4:0)),style.accent);
  return result;
 }
 const api={labels,recess,windowAt,decorate};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.SignatureDesign=api;
})(typeof globalThis!=='undefined'?globalThis:this);
