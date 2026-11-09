const assert=require('node:assert/strict');
const {zoneVisible,wallRoom,inputReport,beltCapacity}=require('../dist/factory-metrics.js');
const {dimensions,project}=require('../dist/factory-preview.js');
assert.equal(zoneVisible(.2,200,200),false);
assert.equal(zoneVisible(1,80,40),true);
assert.equal(zoneVisible(1,10,10),false);
const machine=(id,x,y,z=0)=>({id,category:'machine',recipe:'r',position:[x,y,z]});
const walls=[];
for(const x of [-4,4])for(const y of [-8,8])walls.push({category:'wall',type:'Build_Wall_8x4_01_C',yaw:Math.PI/2,position:[x,y,0]});
for(const y of [-4,4])for(const x of [-8,8])walls.push({category:'wall',type:'Build_Wall_8x4_01_C',yaw:0,position:[x,y,0]});
const seed=machine('a',0,0),second=machine('b',4,0),outside=machine('outside',30,0);
let room=wallRoom(seed,[...walls,seed,second,outside]);
assert.ok(room);
assert.deepEqual(room.machineIds,['a','b']);
assert.equal(room.contains(outside.position),false);
assert.equal(room.contains([200,0,0]),false);
assert.equal(wallRoom(seed,[...walls.slice(1),seed,second]),null,'An opening must not become a closed factory');
assert.equal(wallRoom(seed,[...walls.map(w=>({...w,position:[...w.position.slice(0,2),30]})),seed,second]),null);
const upperWalls=walls.map(w=>({...w,position:[...w.position.slice(0,2),12]}));
assert.equal(wallRoom(seed,[...upperWalls,seed,second]),null);
assert.ok(wallRoom(seed,[...upperWalls,seed,second],true)?.projectedWalls);
assert.deepEqual(dimensions({type:'Build_Wall_8x4_01_C',category:'wall'}),[.3,8,4]);
assert.ok(project([10,20,4],Math.PI/3).every(Number.isFinite));
assert.equal(beltCapacity('Build_ConveyorLiftMk2_C'),120);
assert.equal(beltCapacity('Build_ModdedBelt_C'),null);
const item={id:'ore',name:'Ore',demand:120};
const buildings=[{id:'miner',category:'machine',extraction:{purity:null}},
 {id:'belt',category:'conveyor',type:'Build_ConveyorBeltMk1_C',passThrough:true},
 {id:'splitter',category:'junction',passThrough:true},
 {id:'a',category:'machine',rateModel:{supported:true,inputs:[{id:'ore'}]}},
 {id:'b',category:'machine',rateModel:{supported:true,inputs:[{id:'ore'}]}}];
buildings.forEach(b=>b.ports=[]);const ports=[];
function link(from,to){const a={id:'out'+ports.length,owner:from,direction:'out',state:'connected',peerOwner:to},b={id:'in'+ports.length,owner:to,direction:'in',state:'connected',peerOwner:from};a.peer=b.id;b.peer=a.id;ports.push(a,b);buildings.find(b=>b.id===from).ports.push(a.id);buildings.find(b=>b.id===to).ports.push(b.id);}
link('miner','belt');link('belt','splitter');link('splitter','a');link('splitter','b');
let report=inputReport(item,buildings.slice(3),buildings,ports);
assert.equal(report.miners,1);
assert.equal(report.capacity,60,'One shared Mk.1 must not count twice after splitting');
assert.equal(report.extractionKnown,false);
buildings[1].type='Build_ConveyorBeltMk2_C';
assert.equal(inputReport(item,buildings.slice(3),buildings,ports).capacity,120);
buildings[3].rateModel.inputs.push({id:'coal'});
assert.equal(inputReport(item,buildings.slice(3),buildings,ports).ambiguous,true);
console.log('PASS: zoom threshold, closed/open/floor-separated walls, schematic projection, shared-belt input capacity, miner identity and ingredient uncertainty');
