const assert=require('node:assert/strict'),fs=require('node:fs');
const path=require('node:path'),root=path.resolve(__dirname,'..'),P=require(root+'/dist/workshop-planning.js'),D=require(root+'/dist/workshop-design.js'),data=require(root+'/dist/planner-data.json');
async function compact(body){const r=await fetch((process.env.FACTORY_TEST_URL||'http://127.0.0.1:8765')+'/api/workshop/compact',{method:'POST',headers:{'Content-Type':'application/json','X-Factory-Tools':'local-viewer'},body:JSON.stringify(body)}),v=await r.json();if(!r.ok)throw new Error(v.error);return v.project;}
(async()=>{
 const records=[];let good,request;
 for(const input of ['Desc_OreIron_C','Desc_IronIngot_C'])for(const storeyMode of ['single','auto']){
  request={id:'bas-regression',data,flows:{inputs:[{id:input,rate:60}],outputs:[{id:'Desc_IronPlateReinforced_C',rate:5}]},generation:D.generation({layoutStyle:'compact',storeyMode,shape:'rectangle'})};
  const p=await P.build(request,{compact});assert.equal(p.nativeProfile,'iron-plates-workcells-v1');assert.equal(p.floors.length,1);assert.equal(new Set(p.objects.filter(o=>o.recipe).map(o=>o.z)).size,1);assert.equal(p.size,40);good=p;records.push({input,storeyMode,profile:p.nativeProfile,floors:p.floors.length,machines:p.objects.filter(o=>o.recipe).length});
 }
 request.generation.storeyMode='single';await assert.rejects(P.build(request,{compact:async()=>({...good,nativeProfile:'iron-plates-pairs-v1'})}),/ancien module/);
 await assert.rejects(P.build(request,{compact:async()=>({...good,objects:good.objects.map((o,i)=>i===0?{...o,z:17}:o)})}),/choix Bas/);
 const noPolicy=await compact({...request.flows,options:{size:40,depth:40,height:40,layoutStyle:'compact',storeyMode:'single'}});assert.equal(noPolicy.floors.length,1);assert.equal(noPolicy.nativeProfile,'iron-plates-workcells-v1');
 await assert.rejects(compact({inputs:[{id:'Desc_OreIron_C',rate:120}],outputs:[{id:'Desc_IronPlateReinforced_C',rate:10}],options:{size:40,depth:40,height:40,storeyMode:'single'}}),/choix Bas/);
 if(process.env.FACTORY_TEST_REPORT)fs.writeFileSync(process.env.FACTORY_TEST_REPORT,JSON.stringify(records,null,2));console.log('PASS: real HTTP + planning, 4 compact recipes, Bas/Auto at 5x5 and one production floor; stale legacy replies and multi-floor replies rejected; server Bas enforced even without layoutPolicy.');
})().catch(e=>{console.error(e,e.cause);process.exitCode=1;});
