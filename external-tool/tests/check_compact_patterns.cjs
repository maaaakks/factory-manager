const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const M=require('../dist/workshop-model.js'),A=require('../dist/workshop-assist.js');
const patterns=JSON.parse(fs.readFileSync(path.join(__dirname,'../dist/compact-patterns.json'),'utf8'));
const sm=patterns.find(p=>p.id==='smelter'),co=patterns.find(p=>p.id==='constructor'),ro=patterns.find(p=>p.id==='rotors');
assert.equal(sm.metrics.machineCount,2);assert.equal(co.metrics.machineCount,2);assert.deepEqual(ro.metrics.pairCounts,{smelter:2,constructor:7});assert.equal(ro.metrics.machineCount,22);assert.equal(ro.metrics.downwardLifts,8);
assert.equal(sm.pairs[0].centers,14);assert.equal(co.pairs[0].centers,12);assert.equal(sm.pairs[0].feedZ,1);assert.equal(sm.pairs[0].outputZ,9);assert.equal(co.pairs[0].outputZ,6);
assert.equal(Math.min(...co.shortBelts.map(b=>b.length)),2);
const direct=ro.shortBelts.filter(b=>b.between.length===2&&b.between.every(n=>n.includes('Attachment')));assert.equal(Math.min(...direct.map(b=>b.length)),3);
assert.ok(ro.tightCurves[0].sampledHorizontalRadius>1.20&&ro.tightCurves[0].sampledHorizontalRadius<1.22);
// Dedicated electrical design: one pole per machine; corner follows rotation.
const p=M.fresh('dedicated');p.objects=[{id:'machine',type:'constructor',name:'Constructeur',x:20,y:20,z:0,w:8,d:10,h:6,rotation:90,recipe:'Recipe_IronPlate_C',clock:1}];
const powered=A.addPoles(p),pole=powered.objects.find(o=>o.type==='pole');assert.equal(pole.x,16);assert.equal(pole.y,25);assert.equal(pole.h,7);assert.equal(powered.powerStyle,'per-machine');assert.equal(M.read(powered).powerStyle,'per-machine');
const repeat=A.addPoles(powered);assert.equal(repeat.objects.length,powered.objects.length);assert.equal(repeat.objects.find(o=>o.type==='pole').id,pole.id);
const group=M.fresh('group');group.objects=[[10,10],[22,10],[16,21]].map(([x,y],i)=>({...p.objects[0],id:'m'+i,x,y,rotation:0}));
const dedicated=A.addPoles(group),shared=A.addPoles(group,'shared');assert.equal(dedicated.objects.filter(o=>o.type==='pole').length,3);assert.equal(shared.objects.filter(o=>o.type==='pole').length,2);
for(const plan of [dedicated,shared])for(const pole of plan.objects.filter(o=>o.type==='pole'))assert.ok(plan.links.filter(l=>l.kind==='power'&&(l.from===pole.id||l.to===pole.id)).length<=4);
const bad=M.clone(powered);bad.powerStyle='invalid';assert.throws(()=>M.read(bad));
console.log('PASS: measured pair topology, 2m/3m native spans, tight native curves, downward lifts; dedicated rotated poles, shared option, JSON persistence and cable limits');
