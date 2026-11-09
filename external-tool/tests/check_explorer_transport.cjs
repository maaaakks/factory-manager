const assert=require('node:assert/strict');
const {transportReport}=require('../dist/factory-metrics.js');
const {vertices}=require('../dist/factory-preview.js');
const rate=(id,n)=>({id,name:id,rate:n});
const buildings=[{id:'p',category:'machine',rateModel:{supported:true,outputs:[rate('plate',120)],inputs:[]}},
 {id:'belt',category:'conveyor',type:'Build_ConveyorBeltMk1_C',passThrough:true},
 {id:'split',category:'junction',passThrough:true},
 {id:'a',category:'storage'},{id:'b',category:'storage'},
 {id:'after',category:'conveyor',type:'Build_ConveyorBeltMk5_C',passThrough:true}];
const ports=[];buildings.forEach(b=>b.ports=[]);
function link(from,to){const a={id:'o'+ports.length,owner:from,peerOwner:to,direction:'out',state:'connected'},b={id:'i'+ports.length,owner:to,peerOwner:from,direction:'in',state:'connected'};a.peer=b.id;b.peer=a.id;ports.push(a,b);buildings.find(b=>b.id===from).ports.push(a.id);buildings.find(b=>b.id===to).ports.push(b.id);}
link('p','belt');link('belt','split');link('split','a');link('split','b');link('a','after');
const item={id:'plate',production:120};
let report=transportReport(item,buildings.slice(0,1),buildings,ports);
assert.equal(report.toStorage,60);assert.equal(report.limited,true);assert.equal(report.belts.length,1,'Stop at first chest');assert.equal(report.partial,false);
buildings[1].type='Build_ConveyorBeltMk2_C';
report=transportReport(item,buildings.slice(0,1),buildings,ports);assert.equal(report.toStorage,120);assert.equal(report.limited,false);
ports.find(p=>p.owner==='belt'&&p.direction==='in').direction=null;
assert.equal(transportReport(item,buildings.slice(0,1),buildings,ports).partial,true);
const slope={category:'wall',type:'Build_Wall_Slope_8x4_C',position:[0,0,0],yaw:0};
const v=vertices(slope);assert.equal(v[4][2],0);assert.equal(v[6][2],4);assert.ok(v.flat().every(Number.isFinite));
const turned=vertices({...slope,rotation:[0,0,Math.SQRT1_2,Math.SQRT1_2]});assert.ok(Math.abs(turned[0][0]-4)<1e-8,'Native quaternion is used');
console.log('PASS: shared conveyor bottleneck, first chest boundary, reciprocal ports, sloped walls and native rotations');
