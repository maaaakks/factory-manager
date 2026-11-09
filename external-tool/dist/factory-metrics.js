'use strict';
// Pure calculations shared by the UI and Node checks; no game simulation.
(function(root){
 function wallAxis(yaw){return ((yaw*180/Math.PI+90)%180+180)%180;}
 function wallEnds(b){const dx=-Math.sin(b.yaw)*4,dy=Math.cos(b.yaw)*4;return [[b.position[0]-dx,b.position[1]-dy],[b.position[0]+dx,b.position[1]+dy]];}
 function balance(buildings){
  const items=new Map();let calculated=0,unsupported=0,assumed=0;
  for(const b of buildings){if(!b.recipe)continue;const m=b.rateModel;if(!m?.supported){unsupported++;continue;}calculated++;if(m.assumedClock||m.assumedBoost)assumed++;
   for(const [field,entries]of [['production',m.outputs],['demand',m.inputs]])for(const item of entries){if(!items.has(item.id))items.set(item.id,{id:item.id,name:item.name,production:0,demand:0});items.get(item.id)[field]+=item.rate;}
  }
  // A surplus may leave the factory: it is not evidence of lost production.
  const intermediate=[...items.values()].filter(i=>i.production>0&&i.demand>0).map(i=>({...i,ratio:Math.min(1,i.production/i.demand)})).sort((a,b)=>a.ratio-b.ratio);
  return {calculated,unsupported,assumed,intermediate,score:!unsupported&&intermediate.length?100*intermediate.reduce((sum,i)=>sum+i.ratio,0)/intermediate.length:null};
 }
 function density(buildings,radius=28,minPoints=4){
  const machines=buildings.filter(b=>b.category==='machine'&&b.recipe).sort((a,b)=>a.id.localeCompare(b.id));
  const cells=new Map(),cell=b=>[Math.floor(b.position[0]/radius),Math.floor(b.position[1]/radius),Math.floor(2*b.position[2]/radius)];
  machines.forEach((b,i)=>{const key=cell(b).join(',');if(!cells.has(key))cells.set(key,[]);cells.get(key).push(i);});
  const neighbours=machines.map(a=>{const [x,y,z]=cell(a),near=[];for(let dx=-1;dx<=1;dx++)for(let dy=-1;dy<=1;dy++)for(let dz=-1;dz<=1;dz++)for(const i of cells.get([x+dx,y+dy,z+dz].join(','))||[]){const b=machines[i];if(Math.hypot(a.position[0]-b.position[0],a.position[1]-b.position[1],2*(a.position[2]-b.position[2]))<=radius)near.push(i);}return near;});
  const assigned=new Map(),visited=new Set(),groups=[];
  for(let i=0;i<machines.length;i++){
   if(visited.has(i))continue;visited.add(i);if(neighbours[i].length<minPoints)continue;
   const group=[],index=groups.length,queue=[i],queued=new Set(queue);
   for(let n=0;n<queue.length;n++){const j=queue[n];if(!assigned.has(j)){assigned.set(j,index);group.push(machines[j]);}else if(assigned.get(j)!==index)continue;
    if(!visited.has(j)){visited.add(j);}else if(j!==i)continue;
    if(neighbours[j].length>=minPoints)for(const k of neighbours[j])if(!queued.has(k)){queued.add(k);queue.push(k);}
   }
   groups.push(group);
  }
  return groups.map(group=>{const xs=group.map(b=>b.position[0]),ys=group.map(b=>b.position[1]),zs=group.map(b=>b.position[2]);return {machineIds:group.map(b=>b.id),rect:{minX:Math.min(...xs)-10,maxX:Math.max(...xs)+10,minY:Math.min(...ys)-10,maxY:Math.max(...ys)+10},minZ:Math.min(...zs)-8,maxZ:Math.max(...zs)+8};}).sort((a,b)=>a.rect.minX-b.rect.minX||a.rect.minY-b.rect.minY);
 }
 function flowReport(members,allBuildings,allPorts){
  const byId=new Map(allBuildings.map(b=>[b.id,b])),ports=new Map(allPorts.map(p=>[p.id,p])),inside=new Set(members.map(b=>b.id)),items=new Map();
  let unsupported=0,assumed=0;
  for(const b of members){if(!b.recipe)continue;if(!b.rateModel?.supported){unsupported++;continue;}if(b.rateModel.assumedClock||b.rateModel.assumedBoost)assumed++;
   for(const [field,entries]of [['producers',b.rateModel.outputs],['consumers',b.rateModel.inputs]])for(const item of entries){if(!items.has(item.id))items.set(item.id,{id:item.id,name:item.name,producers:[],consumers:[]});items.get(item.id)[field].push({building:b.id,rate:item.rate});}}
  function destinations(id){const queue=[],seen=new Set(),terminals=new Set();let partial=false;
   for(const pid of byId.get(id)?.ports||[]){const p=ports.get(pid);if(!p?.direction)partial=true;if(p?.direction==='out'&&p.state==='connected')queue.push(p.peerOwner);}
   for(let n=0;n<queue.length&&seen.size<2000;n++){const next=queue[n];if(seen.has(next))continue;seen.add(next);const b=byId.get(next);if(!b){partial=true;continue;}
    if(b.category==='storage'||b.category==='machine'){terminals.add(next);continue;}
    if(!b.passThrough){partial=true;continue;}for(const pid of b.ports){const p=ports.get(pid);if(!p?.direction)partial=true;if(p?.direction==='out'&&p.state==='connected')queue.push(p.peerOwner);}}
   if(seen.size>=2000)partial=true;return {terminals,partial};
  }
  const routes=new Map();for(const item of items.values())for(const p of item.producers)if(!routes.has(p.building))routes.set(p.building,destinations(p.building));
  const result=[];
  for(const item of items.values()){
   const production=item.producers.reduce((s,p)=>s+p.rate,0),demand=item.consumers.reduce((s,c)=>s+c.rate,0),graph=new Map(),storageEdges=[],demandEdges=[];
   function edge(a,b,capacity){if(!graph.has(a))graph.set(a,[]);if(!graph.has(b))graph.set(b,[]);const f={to:b,cap:capacity,flow:0},r={to:a,cap:0,flow:0};f.reverse=r;r.reverse=f;graph.get(a).push(f);graph.get(b).push(r);return f;}
   for(const p of item.producers){edge('source','p:'+p.building,p.rate);const route=routes.get(p.building);for(const c of item.consumers)if(route.terminals.has(c.building))edge('p:'+p.building,'c:'+c.building,production);}
   for(const c of item.consumers)demandEdges.push(edge('c:'+c.building,'sink',c.rate));
   function maxflow(){let added=0;while(true){const prev=new Map([['source',null]]),queue=['source'];for(let n=0;n<queue.length&&!prev.has('sink');n++)for(const e of graph.get(queue[n])||[])if(e.cap-e.flow>1e-7&&!prev.has(e.to)){prev.set(e.to,{from:queue[n],edge:e});queue.push(e.to);}if(!prev.has('sink'))break;
    let amount=Infinity;for(let id='sink';id!=='source';){const p=prev.get(id);amount=Math.min(amount,p.edge.cap-p.edge.flow);id=p.from;}for(let id='sink';id!=='source';){const p=prev.get(id);p.edge.flow+=amount;p.edge.reverse.flow-=amount;id=p.from;}added+=amount;}return added;}
   maxflow();
   const storages=new Set();for(const p of item.producers)for(const id of routes.get(p.building).terminals)if(byId.get(id)?.category==='storage'){storages.add(id);edge('p:'+p.building,'s:'+id,production);}
   for(const id of storages)storageEdges.push(edge('s:'+id,'sink',production));maxflow();
   const consumed=demandEdges.reduce((s,e)=>s+e.flow,0),stored=storageEdges.reduce((s,e)=>s+e.flow,0),partial=item.producers.some(p=>routes.get(p.building).partial);
   result.push({id:item.id,name:item.name,production,demand,consumed,stored,unassigned:Math.max(0,production-consumed-stored),storageIds:[...storages],partial,
    coverage:demand>0&&production>0?Math.min(100,100*consumed/demand):null,
    use:production>0?Math.min(100,100*(consumed+stored)/production):null,
    kind:production===0?'input':demand>0?'intermediate':'product'});
  }
  return {items:result,unsupported,assumed};
 }
 function zoneVisible(zoom,w,h){return zoom>=.75&&Math.max(w,h)>=48;}
 function wallRoom(seed,buildings,projectAbove=false){
  const step=2,span=100,minX=Math.floor((seed.position[0]-span)/step)*step,minY=Math.floor((seed.position[1]-span)/step)*step,size=100;
  const walls=buildings.filter(b=>b.category==='wall'&&!/Tris|Corner|Door/i.test(b.type)&&Math.abs(b.position[0]-seed.position[0])<span&&Math.abs(b.position[1]-seed.position[1])<span&&(Math.abs(b.position[2]-seed.position[2])<=4||(projectAbove&&b.position[2]>=seed.position[2]&&b.position[2]-seed.position[2]<=24)));
  if(walls.length<4)return null;const blocked=new Set(),key=(x,y)=>y*size+x;
  for(const b of walls){const [a,c]=wallEnds(b);for(let i=0;i<=32;i++){const x=Math.floor((a[0]+(c[0]-a[0])*i/32-minX)/step),y=Math.floor((a[1]+(c[1]-a[1])*i/32-minY)/step);if(x>=0&&y>=0&&x<size&&y<size)blocked.add(key(x,y));}}
  const sx=Math.floor((seed.position[0]-minX)/step),sy=Math.floor((seed.position[1]-minY)/step);if(blocked.has(key(sx,sy)))return null;
  const cells=new Set([key(sx,sy)]),queue=[[sx,sy]];
  for(let n=0;n<queue.length;n++){const [x,y]=queue[n];if(x===0||y===0||x===size-1||y===size-1)return null;for(const [dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]]){const nx=x+dx,ny=y+dy,k=key(nx,ny);if(!blocked.has(k)&&!cells.has(k)){cells.add(k);queue.push([nx,ny]);}}}
  if(cells.size<9)return null;
  const contains=p=>{const x=Math.floor((p[0]-minX)/step),y=Math.floor((p[1]-minY)/step);return x>=0&&y>=0&&x<size&&y<size&&Math.abs(p[2]-seed.position[2])<=8&&cells.has(key(x,y));};
  const machines=buildings.filter(b=>b.category==='machine'&&b.recipe&&contains(b.position));if(machines.length<2)return null;
  const outline=[];for(const [x,y]of queue){const wx=minX+x*step,wy=minY+y*step;for(const [dx,dy,a,b]of [[-1,0,[wx,wy],[wx,wy+step]],[1,0,[wx+step,wy],[wx+step,wy+step]],[0,-1,[wx,wy],[wx+step,wy]],[0,1,[wx,wy+step],[wx+step,wy+step]]])if(!cells.has(key(x+dx,y+dy)))outline.push([a,b]);}
  const xs=queue.map(p=>minX+p[0]*step),ys=queue.map(p=>minY+p[1]*step);
  return {machineIds:machines.map(b=>b.id),rect:{minX:Math.min(...xs),maxX:Math.max(...xs)+step,minY:Math.min(...ys),maxY:Math.max(...ys)+step},minZ:seed.position[2]-8,maxZ:seed.position[2]+(projectAbove?24:8),wallGuided:true,projectedWalls:projectAbove,outline,contains};
 }
 function beltCapacity(type){const m=/^Build_Conveyor(?:Belt|Lift)Mk([1-6])_C$/.exec(type||'');return m?[0,60,120,270,480,780,1200][Number(m[1])]:null;}
 function extractionCapacity(b){const e=b?.extraction;return e&&Number.isFinite(e.normalRate)&&Number.isFinite(e.purity)&&e.purity>0&&Number.isFinite(e.clock)?e.normalRate*e.purity*e.clock:null;}
 function residualReachable(graph){const seen=new Set(['source']),q=['source'];for(let n=0;n<q.length;n++)for(const e of graph.get(q[n])||[])if(e.cap-e.flow>1e-6&&!seen.has(e.to)){seen.add(e.to);q.push(e.to);}return seen;}
 function inputReport(item,members,allBuildings,allPorts){
  const byId=new Map(allBuildings.map(b=>[b.id,b])),ports=new Map(allPorts.map(p=>[p.id,p])),inside=new Set(members.map(b=>b.id));
  const targets=members.filter(b=>b.rateModel?.supported&&b.rateModel.inputs.some(i=>i.id===item.id)),seen=new Set(),queue=targets.map(b=>b.id),sources=new Map();let partial=false;
  const ambiguous=targets.some(b=>b.rateModel.inputs.length>1);if(ambiguous)partial=true;
  for(let n=0;n<queue.length&&seen.size<3000;n++){const id=queue[n];if(seen.has(id))continue;seen.add(id);const b=byId.get(id);if(!b){partial=true;continue;}
   if(!targets.some(t=>t.id===id)&&!b.passThrough){if(!ambiguous||b.rateModel?.outputs?.some(i=>i.id===item.id))sources.set(id,b);continue;}
   for(const pid of b.ports||[]){const p=ports.get(pid);if(!p?.direction||p?.state==='unresolved')partial=true;if(p?.direction==='in'&&p.state==='connected')queue.push(p.peerOwner);}}
  if(seen.size>=3000)partial=true;
  // Node capacities preserve shared-belt bottlenecks across multiple branches.
  const graph=new Map();function edge(a,b,cap){if(!graph.has(a))graph.set(a,[]);if(!graph.has(b))graph.set(b,[]);const f={to:b,cap,flow:0},r={to:a,cap:0,flow:0};f.rev=r;r.rev=f;graph.get(a).push(f);graph.get(b).push(r);}
  for(const id of seen){const b=byId.get(id);if(!b)continue;let cap=beltCapacity(b.type);if(b.category==='conveyor'&&cap===null){partial=true;cap=0;}edge(id+':in',id+':out',cap??1e7);
   if(sources.has(id))edge('source',id+':in',extractionCapacity(b)??1e7);
   if(targets.some(t=>t.id===id))edge(id+':out','sink',1e7);
   else for(const pid of b.ports||[]){const p=ports.get(pid);if(p?.direction==='out'&&p.state==='connected'&&seen.has(p.peerOwner))edge(id+':out',p.peerOwner+':in',1e7);}}
  let capacity=0;while(true){const prev=new Map([['source',null]]),q=['source'];for(let n=0;n<q.length&&!prev.has('sink');n++)for(const e of graph.get(q[n])||[])if(e.cap-e.flow>.00001&&!prev.has(e.to)){prev.set(e.to,{from:q[n],e});q.push(e.to);}if(!prev.has('sink'))break;let amount=Infinity;for(let id='sink';id!=='source';){const p=prev.get(id);amount=Math.min(amount,p.e.cap-p.e.flow);id=p.from;}for(let id='sink';id!=='source';){const p=prev.get(id);p.e.flow+=amount;p.e.rev.flow-=amount;id=p.from;}capacity+=amount;}
  const miners=[...sources.values()].filter(b=>b.extraction),known=miners.length>0&&sources.size===miners.length&&miners.every(b=>extractionCapacity(b)!==null),potential=known?miners.reduce((s,b)=>s+extractionCapacity(b),0):null,reachable=residualReachable(graph);
  const need=targets.reduce((s,b)=>s+b.rateModel.inputs.filter(i=>i.id===item.id).reduce((s,i)=>s+i.rate,0),0);
  const critical=need>capacity+1e-5&&!partial?[...seen].filter(id=>byId.get(id)?.category==='conveyor'&&reachable.has(id+':in')&&!reachable.has(id+':out')):[];
  const shared=miners.some(b=>(b.ports||[]).some(pid=>{const p=ports.get(pid);return p?.direction==='out'&&p.state==='connected'&&!seen.has(p.peerOwner);}))||[...seen].some(id=>byId.get(id)?.passThrough&&(byId.get(id).ports||[]).some(pid=>{const p=ports.get(pid);return p?.direction==='out'&&p.state==='connected'&&!seen.has(p.peerOwner);}));
  return {sources:[...sources.values()].map(b=>({id:b.id,name:b.name,type:b.type})),pathIds:[...seen],miners:miners.length,capacity:capacity>=1e7?null:capacity,potential,shared,critical,partial,ambiguous,extractionKnown:known,outside:sources.size>0};
 }
 // Per-resource physical network. Shared belts have one capacity across branches.
 // Stops at the first machine/chest, never traverses storage into another factory.
 function transportReport(item,members,allBuildings,allPorts,options={}){
  const byId=new Map(allBuildings.map(b=>[b.id,b])),ports=new Map(allPorts.map(p=>[p.id,p])),graph=new Map(),seen=new Set(),belts=[],storages=new Set(),storageEdges=[],consumerEdges=[];
  const inside=new Set(members.map(b=>b.id)),boundary=new Map(),boundaryEdges=[];
  const producers=members.filter(b=>b.rateModel?.supported&&b.rateModel.outputs.some(i=>i.id===item.id)),sourceIds=new Set(producers.map(b=>b.id));let partial=false;
  const consumers=new Map(members.filter(b=>b.rateModel?.supported).map(b=>[b.id,b.rateModel.inputs.filter(i=>i.id===item.id).reduce((n,i)=>n+i.rate,0)]));
  function edge(a,b,cap){if(!graph.has(a))graph.set(a,[]);if(!graph.has(b))graph.set(b,[]);const f={to:b,cap,flow:0},r={to:a,cap:0,flow:0};f.rev=r;r.rev=f;graph.get(a).push(f);graph.get(b).push(r);return f;}
  const queue=producers.map(b=>b.id);
  for(let n=0;n<queue.length&&seen.size<3000;n++){
   const id=queue[n];if(seen.has(id))continue;seen.add(id);const b=byId.get(id);if(!b){partial=true;continue;}
   let cap=1e8;if(b.category==='conveyor'){cap=beltCapacity(b.type);if(cap===null){partial=true;cap=0;}belts.push({id,name:b.name||b.type,capacity:cap});}
   const physicalEdge=edge(id+':in',id+':out',options.unbounded?1e8:cap);if(b.category==='conveyor')belts[belts.length-1].edge=physicalEdge;
   if(!sourceIds.has(id)){
    if(b.category==='storage'){storages.add(id);continue;}
    if(b.category==='machine'){if(consumers.get(id)>0)consumerEdges.push({id,demand:consumers.get(id),edge:edge(id+':out','sink',consumers.get(id))});continue;}
    if(!b.passThrough){partial=true;continue;}
   }
   if(sourceIds.has(id)&&b.rateModel.outputs.length>1)partial=true;
   // A directed open belt whose outgoing end is beyond the rectangle is also an export.
   if(options.boundary&&b.category==='conveyor'&&options.rect&&b.points?.length>1&&(b.ports||[]).some(pid=>{const p=ports.get(pid);return p?.direction==='out'&&p.state==='open';})){
    const r=options.rect,outside=p=>p[0]<r.minX||p[0]>r.maxX||p[1]<r.minY||p[1]>r.maxY,upstream=(b.ports||[]).map(pid=>ports.get(pid)).find(p=>p?.direction==='in'&&p.state==='connected'),origin=byId.get(upstream?.peerOwner)?.position;
    const ends=[b.points[0],b.points.at(-1)];let end=null;
    if(origin){const dist=p=>Math.hypot(...p.map((v,i)=>v-origin[i]));end=dist(ends[0])<dist(ends[1])?ends[1]:ends[0];}
    if(end&&outside(end)&&b.points.some(p=>!outside(p))){boundary.set(id,{id,name:b.name||b.type,kind:'open-belt'});boundaryEdges.push(edge(id+':out','export:'+id,1e8));continue;}
   }
   for(const pid of b.ports||[]){const p=ports.get(pid);if(!p?.direction||p.state==='unresolved'){partial=true;continue;}if(p.direction==='out'&&p.state==='connected'){const peer=ports.get(p.peer);if(!peer||peer.peerOwner!==id||peer.direction!=='in'){partial=true;continue;}
    const target=byId.get(p.peerOwner);
    if(options.boundary&&!inside.has(p.peerOwner)&&target){
     if(!boundary.has(target.id)){let cap=target.category==='conveyor'?beltCapacity(target.type):1e8;if(cap===null){partial=true;cap=0;}boundary.set(target.id,{id:target.id,name:target.name||target.type,kind:target.category==='storage'?'external-storage':'boundary',capacity:cap});boundaryEdges.push(edge('export-in:'+target.id,'export:'+target.id,options.unbounded?1e8:cap));}
     edge(id+':out','export-in:'+target.id,1e8);continue;
    }
    edge(id+':out',p.peerOwner+':in',1e8);queue.push(p.peerOwner);}}
  }
  if(seen.size>=3000)partial=true;
  for(const p of producers)edge('source',p.id+':in',p.rateModel.outputs.filter(i=>i.id===item.id).reduce((n,i)=>n+i.rate,0));
  function flow(){let total=0;while(true){const prev=new Map([['source',null]]),q=['source'];for(let n=0;n<q.length&&!prev.has('sink');n++)for(const e of graph.get(q[n])||[])if(e.cap-e.flow>1e-7&&!prev.has(e.to)){prev.set(e.to,{from:q[n],e});q.push(e.to);}if(!prev.has('sink'))return total;let amount=Infinity;for(let id='sink';id!=='source';){const p=prev.get(id);amount=Math.min(amount,p.e.cap-p.e.flow);id=p.from;}for(let id='sink';id!=='source';){const p=prev.get(id);p.e.flow+=amount;p.e.rev.flow-=amount;id=p.from;}total+=amount;}}
  const internal=flow(),internalCut=residualReachable(graph);for(const id of storages)storageEdges.push(edge(id+':out','sink',1e8));for(const id of boundary.keys())edge('export:'+id,'sink',1e8);flow();const toStorage=storageEdges.reduce((n,e)=>n+e.flow,0),toBoundary=boundaryEdges.reduce((n,e)=>n+e.flow,0),delivered=internal+toStorage+toBoundary,outputCut=residualReachable(graph);
  const internalCritical=belts.filter(b=>internalCut.has(b.id+':in')&&!internalCut.has(b.id+':out')).map(b=>b.id),outputCritical=belts.filter(b=>outputCut.has(b.id+':in')&&!outputCut.has(b.id+':out')).map(b=>b.id);
  for(const [i,b]of [...boundary.values()].entries())if(outputCut.has('export-in:'+b.id)&&!outputCut.has('export:'+b.id))outputCritical.push(b.id);
  for(const belt of belts){belt.estimated=belt.edge.flow;belt.saturated=belt.capacity>0&&belt.estimated+1e-5>=belt.capacity;delete belt.edge;}
  return {delivered,toStorage,toBoundary,exported:toStorage+toBoundary,exits:[...boundary.values()],internal,consumers:consumerEdges.map(c=>({id:c.id,demand:c.demand,served:c.edge.flow})),belts,internalCritical,outputCritical,storageIds:[...storages],partial,limited:!partial&&(belts.some(b=>b.saturated)||boundaryEdges.some(e=>e.cap<1e8&&e.flow+1e-5>=e.cap))&&delivered+1e-5<item.production};
 }
 // Compare with the SAME demand and destinations but unlimited conveyors.
 // A full manifold branch is healthy when lifting its capacity serves no extra demand.
 function usefulInputDemand(members,allBuildings,allPorts,options={}){
  // Back-propagate unused outputs into upstream recipe needs. This is a capacity
  // estimate, not measured running time. Never reduce on incomplete connections.
  let scaled=members,settled=false;
  for(let iteration=0;iteration<16;iteration++){
   const replacements=new Map(scaled.map(b=>[b.id,b])),world=allBuildings.map(b=>replacements.get(b.id)||b),report=flowReport(scaled,world,allPorts),ratios=new Map();
   for(const item of report.items.filter(i=>i.production>0)){const t=transportReport(item,scaled,world,allPorts,options);if(!t.partial)ratios.set(item.id,Math.min(1,t.delivered/item.production));}
   let change=0;
   scaled=scaled.map(b=>{if(!b.rateModel?.supported||!b.rateModel.outputs.length)return b;const ratio=Math.min(1,...b.rateModel.outputs.map(i=>ratios.get(i.id)??1));if(ratio>.999999)return b;change=Math.max(change,...b.rateModel.outputs.map(i=>i.rate*(1-ratio)));return {...b,rateModel:{...b.rateModel,inputs:b.rateModel.inputs.map(i=>({...i,rate:i.rate*ratio})),outputs:b.rateModel.outputs.map(i=>({...i,rate:i.rate*ratio}))}};});
   if(change<.001){settled=true;break;}
  }
  const demands=new Map();for(const b of scaled)if(b.rateModel?.supported)for(const i of b.rateModel.inputs)demands.set(i.id,(demands.get(i.id)||0)+i.rate);
  return {demands,settled};
 }
 function diagnostics(members,allBuildings,allPorts,options={}){
  const report=flowReport(members,allBuildings,allPorts),states=new Map(),resources=[],context=new Set(members.map(b=>b.id)),byId=new Map(allBuildings.map(b=>[b.id,b]));
  const mark=(id,ratio,reason)=>{const level=ratio>=.999?'good':ratio>=.8?'warning':'critical',old=states.get(id);if(!old||ratio<old.ratio)states.set(id,{ratio,level,reason});};
  for(const item of report.items){
   if(item.production>0){const actual=transportReport(item,members,allBuildings,allPorts,options),base=transportReport(item,members,allBuildings,allPorts,{...options,unbounded:true});
    const internalLoss=base.internal-actual.internal,outputLoss=base.delivered-actual.delivered,expected=Math.max(base.internal,base.delivered),ratio=expected>0?Math.max(0,1-Math.max(internalLoss,outputLoss)/expected):null;
    resources.push({item,actual,expected,ratio});
    if(!actual.partial&&ratio!==null){for(const b of actual.belts)mark(b.id,1,'Capacité suffisante pour les besoins identifiés');
     for(const c of actual.consumers)mark(c.id,Math.min(1,c.served/c.demand),'Alimentation acheminable · '+item.name);
     if(actual.delivered+.01>=item.production)for(const b of members.filter(b=>b.rateModel?.outputs?.some(i=>i.id===item.id)))mark(b.id,1,'Production acheminable · '+item.name);
     const critical=new Set([...(internalLoss>.01?actual.internalCritical:[]),...(outputLoss>.01?actual.outputCritical:[])]);
     for(const id of critical)mark(id,ratio,'Capacité convoyeur limitante · '+item.name);
    }
   }
   if(item.demand>0){const supply=inputReport(item,members,allBuildings,allPorts);for(const id of supply.pathIds)context.add(id);
    if(item.production===0&&!supply.partial&&supply.capacity!==null){const ratio=Math.min(1,supply.capacity/item.demand);for(const id of supply.pathIds)if(byId.get(id)?.passThrough)mark(id,1,'Capacité suffisante pour les besoins identifiés');for(const id of supply.critical)mark(id,ratio,'Alimentation insuffisante · '+item.name);
     for(const b of members.filter(b=>b.rateModel?.inputs?.some(i=>i.id===item.id)))mark(b.id,ratio,'Alimentation acheminable · '+item.name);
     if(supply.extractionKnown&&!supply.shared)for(const source of supply.sources)mark(source.id,Math.min(1,supply.potential/item.demand),'Potentiel d’extraction pour les besoins identifiés');
    }
   }
  }
  return {states,resources,context,usefulInputs:usefulInputDemand(members,allBuildings,allPorts,options)};
 }
 const api={wallAxis,wallEnds,balance,density,flowReport,zoneVisible,wallRoom,beltCapacity,inputReport,transportReport,extractionCapacity,diagnostics,usefulInputDemand};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FactoryMetrics=api;
})(typeof globalThis!=='undefined'?globalThis:this);
