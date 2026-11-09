'use strict';
(function(root){
 const node=typeof module!=='undefined'&&module.exports,C=node?require('./m05-roof-forms'):root.M05RoofForms,L=node?require('./m05-library'):root.M05Library;
 const round=v=>Math.round(v*1e9)/1e9,turn=([x,y,z],n)=>n===0?[x,y,z]:[-y,x,z],box=pts=>[0,1,2].map(i=>[Math.min(...pts.map(p=>p[i])),Math.max(...pts.map(p=>p[i]))]),overlap=(a,b)=>a.every((r,i)=>Math.min(r[1],b[i][1])-Math.max(r[0],b[i][0])>.01);
 function apply(parts,p,paths=[]){
  if(!p.design.roof)return parts;
  const width=p.size,depth=p.depth??width,height=p.height??width,seed=p.design.roofSeed||1,obstacles=[];
  for(const o of p.objects){let w=o.w,d=o.d;if(o.rotation%180)[w,d]=[d,w];obstacles.push([[o.x-w/2-.15,o.x+w/2+.15],[o.y-d/2-.15,o.y+d/2+.15],[o.z||0,(o.z||0)+(o.h||6)+.15]]);}
  for(const pts of paths)for(let i=1;i<pts.length;i++)obstacles.push(box([pts[i-1],pts[i]]).map(r=>[r[0]-.75,r[1]+.75]));
  for(const q of parts)if(q.signatureRegion||q.signatureBounds)obstacles.push(q.signatureRegion||q.signatureBounds);
  const free=b=>b.every((r,i)=>r[0]>=.009&&r[1]<=[width,depth,height][i]-.009)&&!obstacles.some(o=>overlap(b,o));
  const roofs=parts.filter(q=>q.component==='roof'&&['Toiture','Verrière à ossature'].includes(q.name)&&q.w===8&&q.d===8&&q.asset.endsWith('_01')),rank=q=>(q.x-width/2)**2+(q.y-depth/2)**2;
  const ordered=[...roofs].sort((a,b)=>rank(a)-rank(b)||a.x-b.x||a.y-b.y),form=C.forms[(seed-1)%C.forms.length];
  // Extend the central composition over contiguous bays, using real roof cells.
  const candidates=[];
  for(const n of[Math.floor((seed-1)/C.forms.length)%2,1-Math.floor((seed-1)/C.forms.length)%2])for(const q of ordered){
   const partner=form.width===8?q:roofs.find(r=>Math.abs(r.x-q.x-(n?0:8))<.01&&Math.abs(r.y-q.y-(n?8:0))<.01&&Math.abs(r.z+r.h-q.z-q.h)<.01);if(!partner)continue;
   const support=q.z+q.h,anchor=[(q.x+partner.x)/2,(q.y+partner.y)/2,support],point=a=>turn(a,n).map((v,i)=>round(v+anchor[i])),transform=b=>box([0,1].flatMap(i=>[0,1].flatMap(j=>[0,1].map(k=>point([b[0][i],b[1][j],b[2][k]]))))),region=transform(form.bounds);
   if(!free(region))continue;
   candidates.push({n,q,partner,support,anchor,region});
  }
  const groups=candidates.map(a=>{
   const axis=a.n?0:1,other=1-axis;
   const row=candidates.filter(b=>b.n===a.n&&Math.abs(b.support-a.support)<.01&&Math.abs(b.anchor[other]-a.anchor[other])<.01&&b.anchor[axis]>=a.anchor[axis]-.01&&b.anchor[axis]<=a.anchor[axis]+8*(Math.min(form.id==='monitor'?3:6,Math.max(2,Math.floor(([width,depth][axis]-16)/8)))-1)+.01).sort((b,c)=>b.anchor[axis]-c.anchor[axis]);
   const run=[];for(const b of row){if(run.length&&Math.abs(b.anchor[axis]-run[run.length-1].anchor[axis]-8)>.01)break;run.push(b);}return run;
  }).sort((a,b)=>b.length-a.length||rank({x:a.reduce((s,q)=>s+q.anchor[0],0)/a.length,y:a.reduce((s,q)=>s+q.anchor[1],0)/a.length})-rank({x:b.reduce((s,q)=>s+q.anchor[0],0)/b.length,y:b.reduce((s,q)=>s+q.anchor[1],0)/b.length}));
  if(groups.length){
   const chosen=[groups[0]],first=groups[0][0],axis=first.n?0:1,other=1-axis;
   for(const group of groups){if(chosen.length>=(form.id==='monitor'?2:3))break;if(group.length!==groups[0].length||group[0].n!==first.n||Math.abs(group[0].anchor[axis]-first.anchor[axis])>.01)continue;if(chosen.every(g=>Math.abs(g[0].anchor[other]-group[0].anchor[other])>=form.width+7.99))chosen.push(group);}
   const selected=chosen.flat(),tiles=new Set(),details=[],seen=new Set();
   for(const {n,q,partner,support,anchor,region} of selected){
   tiles.add(q);tiles.add(partner);
   const point=a=>turn(a,n).map((v,i)=>round(v+anchor[i])),transform=b=>box([0,1].flatMap(i=>[0,1].flatMap(j=>[0,1].map(k=>point([b[0][i],b[1][j],b[2][k]])))));
   const added=[],s=round(Math.sin(n*Math.PI/4)),c=round(Math.cos(n*Math.PI/4));
   for(const source of form.pieces){const b=transform(source.bounds),name='M05 · '+form.label;
    if(source.beam){const start=point(source.start),end=point(source.end);added.push({name,component:'beam',asset:'Beam_Painted',start,end,x:(start[0]+end[0])/2,y:(start[1]+end[1])/2,z:b[2][0],w:b[0][1]-b[0][0],d:b[1][1]-b[1][0],h:b[2][1]-b[2][0],rotation:0,color:source.color,signatureBounds:b,roofDetail:form.id});}
    else{const[x,y,z,w]=source.quat,pos=point(source.pos),quat=[c*x-s*y,c*y+s*x,c*z+s*w,c*w-s*z].map(round);added.push({name,component:'module',asset:source.asset,sourceModule:source.sourceModule,sourceIndex:source.sourceIndex,origin:[0,0,0],turn:0,quat,x:pos[0],y:pos[1],z:pos[2],w:0,d:0,h:0,rotation:n*90,color:source.color,signatureBounds:b,roofDetail:form.id});}
   }
   added[0].roofComposition={id:form.id,label:form.label,supportZ:support,bounds:region};
   for(const part of added){const key=JSON.stringify([part.asset,part.start,part.end,part.x,part.y,part.z,part.quat]);if(!seen.has(key)){seen.add(key);details.push(part);}}
   }
   return [...parts.map(r=>tiles.has(r)?{...r,asset:'Roof_Window_01',color:'#91b9c0'}:r),...details];
  }
  // With insufficient headroom, retain skylights and at most one small vent.
  const index=L.modules.M3.parts.findIndex(q=>q.asset==='LargeVent'),source=L.modules.M3.parts[index];
  for(const q of ordered.filter(q=>q.asset==='Roof_Tar_01')){const z=q.z+q.h+.02,b=[[q.x-1.3,q.x+1.3],[q.y-1.3,q.y+1.3],[z,z+.35]];if(!free(b))continue;return[...parts,{name:'M05 · Ventilation discrète',component:'module',asset:'LargeVent',sourceModule:'M3',sourceIndex:index,origin:[0,0,0],turn:0,quat:source.quat,x:q.x,y:q.y,z,w:0,d:0,h:0,rotation:0,color:'#354145',signatureBounds:b,roofDetail:'vent'}];}
  return parts;
 }
 const api={apply};if(node)module.exports=api;else root.M05Roof=api;
})(typeof globalThis!=='undefined'?globalThis:this);
