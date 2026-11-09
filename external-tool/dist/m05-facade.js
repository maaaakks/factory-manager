'use strict';
(function(root){
 const node=typeof module!=='undefined'&&module.exports,C=node?require('./m05-facade-library.js'):root.M05FacadeLibrary;
 const round=v=>Math.round(v*1e9)/1e9,turn=([x,y,z],n)=>n===0?[x,y,z]:n===1?[-y,x,z]:n===2?[-x,-y,z]:[y,-x,z];
 const overlap=(a,b)=>a.every((r,i)=>Math.min(r[1],b[i][1])-Math.max(r[0],b[i][0])>.01);
 const box=pts=>[0,1,2].map(i=>[Math.min(...pts.map(p=>p[i])),Math.max(...pts.map(p=>p[i]))]);
 function bounds(q){if(q.signatureBounds)return q.signatureBounds;if(q.start)return box([q.start,q.end]).map(r=>[r[0]-.3,r[1]+.3]);let w=q.w||0,d=q.d||0;if(q.rotation%180)[w,d]=[d,w];return[[q.x-w/2,q.x+w/2],[q.y-d/2,q.y+d/2],[q.z,q.z+(q.h||0)]];}
 function apply(parts,p,paths=[],slot=0,wrap=false){
  const seed=(p.design.seed||1)+slot,side={front:0,right:1,back:2,left:3}[p.design.entrance]??0,n=[2,3,0,1][side],normal=turn([0,1,0],n),width=p.size,depth=p.depth??width,height=p.height??width;
  const panels=parts.filter(q=>['wall','window'].includes(q.component)&&q.h===4&&q.rotation===side*90&&!q.name.startsWith('Lanterneau'));
  if(!panels.length)return parts;
  const distance=q=>q.x*normal[0]+q.y*normal[1],line=Math.max(...panels.map(distance)),face=panels.filter(q=>Math.abs(distance(q)-line)<.05),us=[...new Set(face.map(q=>side%2?q.y:q.x))].sort((a,b)=>a-b),mid=(us[0]+us.at(-1))/2;
  const obstacles=p.objects.map(o=>{let w=o.w,d=o.d;if(o.rotation%180)[w,d]=[d,w];return[[o.x-w/2-.15,o.x+w/2+.15],[o.y-d/2-.15,o.y+d/2+.15],[o.z||0,(o.z||0)+(o.h||6)+.15]];});
  for(const pts of paths)for(let i=1;i<pts.length;i++)obstacles.push(box([pts[i-1],pts[i]]).map(r=>[r[0]-.75,r[1]+.75]));
  for(const q of parts)if(q.name.startsWith('Entrée piétonne'))obstacles.push(bounds(q));
  for(const q of parts)if(q.signatureRegion||q.signatureBounds)obstacles.push(q.signatureRegion||q.signatureBounds);
  const free=b=>b.every((r,i)=>r[0]>=(i===2?-1e-7:.009)&&r[1]<=[width,depth,height][i]-.009)&&!obstacles.some(o=>overlap(b,o));
  const wallTop=Math.max(...panels.map(q=>q.z+q.h)),levels=[...new Set((p.floors||[]).map(f=>round(f.z+(f.thickness||1))))].sort((a,b)=>a-b);if(!levels.length)levels.push(0);
  const order=[(seed-1)%3,...[0,1,2].filter(i=>i!==(seed-1)%3)];
  const modes=wrap?['inset','projection']:['projection','inset'];
  for(const mode of modes){
   if(mode==='crown'&&(!p.design.roof||slot))continue;
   for(const index of order)for(const motif of[C.motifs[index],C.motifs[index+3]].filter(Boolean)){const lo=motif.bounds[0][0],hi=motif.bounds[0][1],span=hi-lo;
    const target=mid+(slot===1?-24:slot===2?24:0),centers=[...(span>12?us.slice(0,-1).map((u,i)=>(u+us[i+1])/2):us)].filter(u=>!slot||Math.abs(u-target)<=8).sort((a,b)=>Math.abs(a-target)-Math.abs(b-target)||a-b);
    const bases=levels.filter(z=>z+motif.bounds[2][1]<=wallTop+.75);
    for(const u of centers)for(const base of bases){
     const offset=mode==='projection'?.35:-8.45,anchor=side%2?[normal[0]*(line+offset),u,base]:[u,normal[1]*(line+offset),base];
     const point=a=>turn(a,n).map((v,i)=>round(v+anchor[i]));
     const transform=b=>box([0,1].flatMap(i=>[0,1].flatMap(j=>[0,1].map(k=>point([b[0][i],b[1][j],b[2][k]])))));
     const region=transform(motif.bounds);if(!free(region))continue;
     const passage=motif.id==='portique'?transform([[-7,7],[-.5,8.2],[.05,7.1]]):null;
     const result=[],added=[];let units=0;
     // Replace complete panels inside the new volume. Preserve crossing members
     // and the pedestrian entrance; never trim native fixed-size walls.
     for(const q of parts){const b=bounds(q),inside=b.every((r,i)=>r[0]>=region[i][0]-1.5&&r[1]<=region[i][1]+1.5),replace=(inside&&!q.name.startsWith('Entrée')&&(mode==='crown'||q.component!=='roof'))||passage&&overlap(b,passage);
      if(replace)units+=q.coverageUnits||q.panelUnits||(['wall','window'].includes(q.component)?1:0);else result.push(q);
     }
     const angle=n*Math.PI/2,s=round(Math.sin(angle/2)),c=round(Math.cos(angle/2));
     for(const source of motif.pieces){
      if(!p.design.roof&&source.asset?.startsWith('Roof_')||mode==='crown'&&source.platform)continue;
      const b=transform(source.bounds),name='Signature M05 · '+motif.label;
      if(source.beam){const start=point(source.start),end=point(source.end);added.push({name,component:'beam',asset:'Beam_H',start,end,x:(start[0]+end[0])/2,y:(start[1]+end[1])/2,z:b[2][0],w:b[0][1]-b[0][0],d:b[1][1]-b[1][0],h:b[2][1]-b[2][0],rotation:0,color:source.color,signatureBounds:b,...(source.platform?{platform:true}:{})});}
      else{const [x,y,z,w]=source.quat,quat=[c*x-s*y,c*y+s*x,c*z+s*w,c*w-s*z].map(round),pos=point(source.pos);added.push({name,component:'module',asset:source.asset,sourceModule:source.sourceModule,sourceIndex:source.sourceIndex,origin:[0,0,0],turn:0,quat,x:pos[0],y:pos[1],z:pos[2],w:0,d:0,h:0,rotation:n*90,color:source.color,signatureBounds:b,...(source.platform?{platform:true}:{})});}
     }
     if(!added.length)continue;
     if(units)(added.find(q=>q.z<wallTop)||added[0]).coverageUnits=units;
     added[0].facadeSignature={id:motif.id,label:motif.label,placement:mode,side,supportZ:base,wallTop};added[0].signatureRegion=region;return [...result,...added];
    }
   }
  }
  // If there is no free volume, a shallow steel portal still gives the front
  // a distinct silhouette without stealing production or increasing the plot.
  if(slot)return parts;
  const accents=[],chosen=face.filter(q=>q.z>=4).sort((a,b)=>Math.abs((side%2?a.y:a.x)-mid)-Math.abs((side%2?b.y:b.x)-mid)||b.z-a.z).slice(0,2);
  for(const q of chosen){const u=side%2?q.y:q.x,at=(t,z)=>side%2?[normal[0]*(line+.5),u+t,z]:[u+t,normal[1]*(line+.5),z];
   for(const sign of[-1,1]){const start=at(sign*2.8,q.z+.7),end=at(0,q.z+3.2),b=box([start,end]).map(r=>[r[0]-.22,r[1]+.22]);if(!free(b))continue;accents.push({name:'Signature M05 · Charpente compacte',component:'beam',asset:'Beam_Painted',start,end,x:(start[0]+end[0])/2,y:(start[1]+end[1])/2,z:b[2][0],w:b[0][1]-b[0][0],d:b[1][1]-b[1][0],h:b[2][1]-b[2][0],rotation:0,color:'#354145',signatureBounds:b});}
  }
  if(accents.length){accents[0].facadeSignature={id:'charpente',label:'Charpente compacte',placement:'relief',side};return [...parts.filter(q=>q.asset!=='LargeFan'||!chosen.some(c=>Math.abs(c.x-q.x)<1&&Math.abs(c.y-q.y)<1&&Math.abs(c.z+2-q.z)<.1)),...accents];}
  return parts;
 }
 function compose(parts,p,paths=[]){
  let result=apply(parts,p,paths);const faces=['front','right','back','left'],primary=faces.indexOf(p.design.entrance),first=primary<0?0:primary;
  const span=first%2?p.depth??p.size:p.size;
  if(span>=64&&result.some(q=>q.signatureRegion)){result=apply(result,p,paths,1);result=apply(result,p,paths,2);}
  // Compose each remaining face independently. Insets have priority, and no
  // secondary tower steals the main facade's silhouette or enlarges the plot.
  for(let offset=1;offset<4;offset++){const side=(first+offset)%4,view={...p,design:{...p.design,entrance:faces[side],seed:((p.design.seed||1)+offset-1)%999+1}};result=apply(result,view,paths,0,true);}
  return result;
 }
 const api={apply:compose,bounds};if(node)module.exports=api;else root.M05Facade=api;
})(typeof globalThis!=='undefined'?globalThis:this);
