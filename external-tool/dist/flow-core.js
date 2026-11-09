'use strict';
// Shared, read-only transport/recipe contract for planner and explorer adapters.
// Rates are theoretical bounds, never live production measurements.
(function(root){
 const machines=new Set(['smelter','constructor','assembler']);
 function interfaceFor(o){return o.io||null;}
 function assignRecipe(project,ids,recipe,data){const chosen=new Set(ids),next=JSON.parse(JSON.stringify(project)),r=data.recipes[recipe];for(const o of next.objects)if(chosen.has(o.id)){if(!machines.has(o.type)||r&&r.type!==o.type||recipe&&!r)throw new Error('Recette incompatible avec la sélection.');o.recipe=recipe||null;if(r)o.name=r.name;}return next;}
 function solve(constraints,c){
  const n=c.length,m=constraints.length,width=n+m+1,table=constraints.map((row,i)=>{const a=new Float64Array(width);for(const [k,v]of Object.entries(row.row))a[Number(k)]=v;a[n+i]=1;a[width-1]=row.limit;return a;}),cost=new Float64Array(width),basis=Array.from({length:m},(_,i)=>n+i),start=typeof performance!=='undefined'?performance.now():Date.now();
  c.forEach((value,i)=>cost[i]=-value);let complete=false;
  for(let step=0;step<2000;step++){
   if(step%20===0&&(typeof performance!=='undefined'?performance.now():Date.now())-start>180)break;
   let column=-1;for(let i=0;i<width-1;i++)if(cost[i]<-1e-8){column=i;break;}if(column<0){complete=true;break;}
   let row=-1,ratio=Infinity;for(let i=0;i<m;i++)if(table[i][column]>1e-8){const r=table[i][width-1]/table[i][column];if(r<ratio-1e-8||Math.abs(r-ratio)<1e-8&&(row<0||basis[i]<basis[row])){row=i;ratio=r;}}if(row<0)break;
   const pivot=table[row],value=pivot[column];for(let j=0;j<width;j++)pivot[j]/=value;
   for(let i=0;i<m;i++){if(i===row)continue;const a=table[i],factor=a[column];if(Math.abs(factor)<1e-12)continue;for(let j=0;j<width;j++)a[j]-=factor*pivot[j];}
   const factor=cost[column];for(let j=0;j<width;j++)cost[j]-=factor*pivot[j];basis[row]=column;
  }
  const values=new Float64Array(n);for(let i=0;i<m;i++)if(basis[i]<n)values[basis[i]]=Math.max(0,table[i][width-1]);return {values,complete};
 }
 function analyze(p,data,options={}){
  const objects=p.objects||[],links=(p.links||[]).filter(l=>l.kind!=='power'),byId=new Map(objects.map(o=>[o.id,o])),issues=[],interfaces=new Map();
  for(const o of objects)if(o.io)interfaces.set(o.id,{...o.io});
  if(p.nativeProfile&&p.layoutInfo){const input=p.layoutInfo.input,output=p.layoutInfo.output;if(input&&!interfaces.has(input.objectId))interfaces.set(input.objectId,{side:'input',item:p.flows.inputs[0]?.id,rate:input.rate});if(output&&!interfaces.has(output.objectId))interfaces.set(output.objectId,{side:'output',item:p.flows.outputs[0]?.id,rate:output.rate});}
  const recipe=o=>data?.recipes?.[o?.recipe],rows=(o,side)=>recipe(o)?.[side]||[],nominal=(o,row)=>row.amount*60/recipe(o).seconds*(o.clock??1);
  const itemSets=new Map(links.map(l=>[l,new Set(l.item?[l.item]:[])]));
  const itemsAt=(o,side)=>{const io=interfaces.get(o.id);if(io?.item)return new Set([io.item]);if(recipe(o))return new Set(rows(o,side).map(i=>i.id));const connected=links.filter(l=>side==='outputs'?l.to===o.id:l.from===o.id),found=new Set();for(const l of connected)for(const id of itemSets.get(l))found.add(id);return found;};
  for(let step=0;step<objects.length+1;step++){let changed=false;for(const l of links){if(itemSets.get(l).size)continue;const a=byId.get(l.from),b=byId.get(l.to);if(!a||!b)continue;const source=itemsAt(a,'outputs'),target=itemsAt(b,'inputs'),possible=source.size&&target.size?new Set([...source].filter(x=>target.has(x))):source.size?source:target;if(possible.size===1){itemSets.set(l,possible);changed=true;}}if(!changed)break;}
  const valid=[];
  for(const l of links){if(options.linkAvailable&&!options.linkAvailable(l)){issues.push('Trajet introuvable ou interrompu.');continue;}const a=byId.get(l.from),b=byId.get(l.to),set=itemSets.get(l);if(!a||!b||set.size!==1){issues.push('Ressource inconnue ou ambiguë sur une liaison.');continue;}const item=[...set][0],ar=recipe(a),br=recipe(b),ai=interfaces.get(a.id),bi=interfaces.get(b.id);if(ai?.side==='output'||bi?.side==='input'||ar&&!ar.outputs.some(i=>i.id===item)||br&&!br.inputs.some(i=>i.id===item)||ai?.item&&ai.item!==item||bi?.item&&bi.item!==item){issues.push('Ressource ou sens incompatible sur une liaison.');continue;}valid.push({link:l,item});}
  // Steady-state material conservation, including recipe ratios. All-zero is
  // feasible, so a primal simplex can start from slack variables without Phase I.
  const producers=objects.filter(recipe),n=valid.length+producers.length,variables=new Map(producers.map((o,i)=>[o.id,valid.length+i])),constraints=[],objective=new Float64Array(n);
  const incoming=(id,item)=>valid.flatMap((v,i)=>v.link.to===id&&v.item===item?[i]:[]),outgoing=(id,item)=>valid.flatMap((v,i)=>v.link.from===id&&v.item===item?[i]:[]);
  const bound=(row,limit)=>constraints.push({row,limit});
  const equal=row=>{bound(row,0);bound(Object.fromEntries(Object.entries(row).map(([k,v])=>[k,-v])),0);};
  for(const [i,v]of valid.entries())bound({[i]:v.link.capacity??p.beltCapacity??120},1);
  // Convert capacity rows to coefficient 1, for stable pivot scales.
  for(let i=0;i<valid.length;i++){constraints[i].limit=constraints[i].row[i];constraints[i].row[i]=1;}
  for(const o of objects){const io=interfaces.get(o.id),r=recipe(o),items=new Set(valid.filter(v=>v.link.from===o.id||v.link.to===o.id).map(v=>v.item));
   if(r){const index=variables.get(o.id);bound({[index]:1},1);for(const side of ['inputs','outputs'])for(const item of r[side]){const ids=side==='inputs'?incoming(o.id,item.id):outgoing(o.id,item.id),row=Object.fromEntries(ids.map(i=>[i,1]));row[index]=-nominal(o,item);equal(row);}continue;}
   for(const item of items){const ins=incoming(o.id,item),outs=outgoing(o.id,item),row={};for(const i of ins)row[i]=(row[i]||0)+1;for(const i of outs)row[i]=(row[i]||0)-1;
    if(io?.side==='input'){
     if(io.rate===null||io.rate===undefined)issues.push('Une entrée a un débit inconnu.');
     bound(Object.fromEntries(outs.map(i=>[i,1])),io.item===item?io.rate??0:0);for(const i of ins)bound({[i]:1},0);
    }else if(io?.side==='output'||o.type==='storage'){
     for(const i of outs)bound({[i]:1},0);if(io?.rate)bound(Object.fromEntries(ins.map(i=>[i,1])),io.rate);
     for(const i of ins)objective[i]+=io?.rate?1/io.rate:1e-4;
    }else equal(row);
   }
  }
  const solved=solve(constraints,objective),fractions=new Map(producers.map(o=>[o.id,solved.values[variables.get(o.id)]])),lastFlows=new Map(valid.map((v,i)=>[v.link,solved.values[i]])),lastSupply=new Map(),lastDeliveries=new Map(),converged=solved.complete;
  for(const [id,io]of interfaces){if(io.side==='input')lastSupply.set(id,valid.reduce((sum,v,i)=>sum+(v.link.from===id?solved.values[i]:0),0));else lastDeliveries.set(id+'|'+io.item,valid.reduce((sum,v,i)=>sum+(v.link.to===id&&v.item===io.item?solved.values[i]:0),0));}
  if(!converged)issues.push('Analyse partielle : limite de calcul atteinte.');
  const linkReports=new Map();for(const {link,item}of valid){const a=byId.get(link.from),b=byId.get(link.to),r=recipe(b),io=interfaces.get(b.id),source=interfaces.get(a.id),output=rows(a,'outputs').find(i=>i.id===item),offer=source?.rate??(output?nominal(a,output):null),capacity=link.capacity??p.beltCapacity??120,incoming=valid.filter(x=>x.item===item&&x.link.to===b.id).length;const wanted=link.rate??(io?.rate??(r?nominal(b,r.inputs.find(i=>i.id===item)):offer)),requested=wanted===null?null:wanted/(link.rate?1:Math.max(1,incoming)),demand=requested===null?offer:offer===null?requested:Math.min(offer,requested),actual=lastFlows.get(link)||0;linkReports.set(link,{item,capacity,actual,demand,load:100*actual/capacity,efficiency:demand?Math.min(100,100*actual/demand):null,state:demand&&demand>capacity+1e-7&&(offer??actual)>=capacity-1e-7?'blocked':actual>=capacity*.9?'busy':'ok'});}
  const endpointReports=new Map();for(const [id,io]of interfaces){const actual=io.side==='input'?lastSupply.get(id)||0:lastDeliveries.get(id+'|'+io.item)||0;endpointReports.set(id,{...io,actual,efficiency:io.side==='output'&&io.rate?Math.min(100,100*actual/io.rate):null});}
  return {links:linkReports,endpoints:endpointReports,machines:fractions,issues:[...new Set(issues)],converged,theoretical:true};
 }
 const api={analyze,assignRecipe,interfaceFor};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FactoryFlowCore=api;
})(typeof globalThis!=='undefined'?globalThis:this);
