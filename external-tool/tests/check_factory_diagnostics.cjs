const assert=require('node:assert/strict');
const M=require('../dist/factory-metrics.js'),P=require('../dist/factory-preview.js');
function network(production=120,demand=60,storage=false,mk=1){
 const bs=[{id:'p',category:'machine',recipe:'ingot',rateModel:{supported:true,inputs:[],outputs:[{id:'ingot',name:'Lingot',rate:production}]}},
 {id:'belt',category:'conveyor',type:`Build_ConveyorBeltMk${mk}_C`,passThrough:true},
 {id:'c',category:storage?'storage':'machine',recipe:storage?null:'plate',rateModel:{supported:true,inputs:[{id:'ingot',rate:demand}],outputs:[]}}];
 const ports=[];bs.forEach(b=>b.ports=[]);
 function link(a,b){const out={id:'out'+ports.length,owner:a,peerOwner:b,direction:'out',state:'connected'},input={id:'in'+ports.length,owner:b,peerOwner:a,direction:'in',state:'connected'};out.peer=input.id;input.peer=out.id;ports.push(out,input);bs.find(b=>b.id===a).ports.push(out.id);bs.find(a=>a.id===b).ports.push(input.id);}
 link('p','belt');link('belt','c');return {bs,ports};
}
let {bs,ports}=network();let d=M.diagnostics(bs,bs,ports);
assert.equal(d.states.get('belt').level,'good','A saturated Mk1 manifold meeting 60/min demand is not a bottleneck');
({bs,ports}=network(120,120));d=M.diagnostics(bs,bs,ports);
assert.equal(d.states.get('belt').level,'critical');assert.equal(d.resources[0].ratio,.5);
({bs,ports}=network(70,70));d=M.diagnostics(bs,bs,ports);assert.equal(d.states.get('belt').level,'warning');
({bs,ports}=network(120,120,true));d=M.diagnostics(bs,bs,ports);assert.equal(d.states.get('belt').level,'critical','A capacity limit on a final chest path is detected');
({bs,ports}=network(120,60,false,2));d=M.diagnostics(bs,bs,ports);assert.equal(d.states.get('belt').level,'good','Surplus without a destination does not prove a belt bottleneck');
({bs,ports}=network(120,120,true,2));d=M.diagnostics(bs.slice(0,1),bs,ports,{boundary:true});assert.equal(d.resources[0].actual.exported,120);
bs[1].type='Build_ConveyorBeltMk1_C';d=M.diagnostics(bs.slice(0,1),bs,ports,{boundary:true});assert.equal(d.states.get('belt').level,'critical','Outside boundary belt capacity is colored');
// Extraction capacity and context include a miner outside the factory perimeter.
({bs,ports}=network(360,330,false,3));bs[0].extraction={normalRate:120,purity:1,clock:3};bs[0].rateModel=null;bs[0].recipe=null;
let input=M.inputReport({id:'ingot'},[bs[2]],bs,ports);
assert.equal(input.potential,360);assert.equal(input.capacity,270);assert.ok(input.pathIds.includes('p'));assert.deepEqual(input.critical,['belt']);
assert.equal(M.extractionCapacity({extraction:{normalRate:120,purity:null,clock:1}}),null,'Unknown purity is not normal purity');
bs[0].extraction.purity=null;input=M.inputReport({id:'ingot'},[bs[2]],bs,ports);assert.equal(input.potential,null);
({bs,ports}=network(360,330,false,5));bs[0].rateModel.inputs=[{id:'ore',rate:360}];
let useful=M.usefulInputDemand(bs,bs,ports);assert.equal(useful.settled,true);assert.ok(Math.abs(useful.demands.get('ore')-330)<1e-6,'360 nominal smelter input becomes 330 useful input when only 330 ingots are used downstream');
({bs,ports}=network(360,330,true,5));bs[0].rateModel.inputs=[{id:'ore',rate:360}];useful=M.usefulInputDemand(bs,bs,ports);assert.equal(useful.demands.get('ore'),360,'Chest exports count as useful production, not unused ore');
assert.deepEqual(P.dimensions({type:'Build_MinerMk2_C',category:'machine'}),[6,14,18]);
const ramp={type:'Build_Ramp_8x2_01_C',category:'foundation',position:[0,0,0],yaw:0};let v=P.vertices(ramp);
assert.equal(v[4][2],1);assert.equal(v[5][2],-1);assert.equal(v[0][2],-1,'Ramp pivot is vertically centred');
v=P.vertices({...ramp,type:'Build_InvertedRamp_Concrete_8x2_C'});assert.equal(v[4][2],1);assert.equal(v[5][2],1);assert.equal(v[0][2],1);assert.equal(v[1][2],-1,'Inverted ramp has flat top and descending underside');
v=P.vertices({...ramp,scale:[-1,1,1],rotation:[0,0,Math.SQRT1_2,Math.SQRT1_2]});assert.ok(Math.abs(v[4][1]-4)<1e-8,'Native mirrored scale and quaternion preserved');
console.log('PASS: genuine bottlenecks, manifold backpressure, exports, unknown purity, connected miners and centred native ramps');
