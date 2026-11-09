const assert=require('node:assert/strict'),D=require('../dist/workshop-design.js'),M=require('../dist/workshop-model.js'),A=require('../dist/workshop-assist.js'),P=require('../dist/factory-preview.js'),data=require('../dist/planner-data.json');
for(const category of ['wall','roof','decoration','structure'])assert.equal(P.layerOf({category}),'habillage');for(const category of ['machine','foundation','conveyor'])assert.equal(P.layerOf({category}),category);
const empty={...M.fresh('shapes'),size:48,objects:[],floors:[{z:0,thickness:1,material:'concrete'}]};
for(const [shape,count]of [['rectangle',36],['stepped',32],['l',27],['u',32],['cross',20]]){
 const p={...empty,design:D.settings({enabled:true,footprint:shape})};assert.equal(D.footprint(p).size,count);assert.equal(D.floorCells(p,p.floors[0]).length,36);assert.equal(D.floorCells(p,{z:10}).length,count);
}
const l={...empty,design:D.settings({enabled:true,footprint:'l'})},occupied={...l,objects:[{id:'ob',type:'constructor',x:40,y:5,z:1,w:8,d:8,h:6,rotation:0}]};assert.ok(D.footprint(occupied).has('5,0'));
const belt={kind:'belt',from:'x',to:'y',physicalRoute:[{x:38,y:3,z:2},{x:46,y:3,z:2}]};assert.ok(D.footprint({...l,links:[belt]}).has('5,0'));
const glass={...empty,design:D.preset('campus',{packs:['concrete','metal','glass']})},parts=D.envelope(glass);assert.ok(parts.some(o=>o.component==='window'&&o.z===0),'Short contemporary factory has glazing at ground level');assert.ok(parts.some(o=>o.name.startsWith('Lanterneau')));assert.ok(parts.some(o=>o.component==='roof'&&o.z===12));
const saw=D.envelope({...empty,design:{...glass.design,roofForm:'sawtooth'}});assert.ok(saw.filter(o=>o.component==='roof').every(o=>o.rotation===0));assert.ok(saw.some(o=>o.name==='Rive de toit'));
const frame={...empty,size:32,design:D.settings({enabled:true,entrance:'none',footprint:'rectangle'}),objects:[{id:'a',name:'A',type:'constructor',x:4,y:16,z:1,w:8,d:10,h:6,rotation:0},{id:'b',name:'B',type:'constructor',x:28,y:16,z:1,w:8,d:10,h:6,rotation:0}]},before=JSON.stringify(frame);assert.ok(D.openings(frame)>0);const room=D.reserveArchitecture(frame);assert.equal(room.size,40);assert.equal(D.openings(room),0);assert.equal(room.objects[1].x-room.objects[0].x,24);assert.equal(JSON.stringify(frame),before);
const full={...frame,size:48,objects:frame.objects.map((o,i)=>({...o,x:i?44:4,y:24}))},saved=JSON.stringify(full);assert.throws(()=>D.reserveArchitecture(full),/6 × 6/);assert.equal(JSON.stringify(full),saved);
const flows={inputs:[{id:'Desc_OreCopper_C',rate:60}],outputs:[{id:'Desc_CopperIngot_C',rate:60}]},generation=D.generation({priority:'architecture',storeyMode:'single'}),r=A.calculate(flows,data,{size:40,physical:true,generation});
for(const o of [...r.objects,...r.logistics]){const b=M.bounds(o);assert.ok(b.minX>=4&&b.minY>=4&&b.maxX<=36&&b.maxY<=36);}
assert.throws(()=>D.generation({priority:'guess'}),/invalide/);
console.log('PASS: unified cladding, L/U/cross contours, protected machines/belts, matching floor masks, single-storey glazing, monitor/sawtooth roofs, atomic margin reservation and architecture-first single-storey copper chain');
