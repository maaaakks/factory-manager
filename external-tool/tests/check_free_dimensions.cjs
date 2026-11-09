const assert=require('node:assert/strict'),M=require('../dist/workshop-model.js'),D=require('../dist/workshop-design.js'),A=require('../dist/workshop-assist.js'),data=require('../dist/planner-data.json');
const object={id:'m',type:'constructor',name:'Machine',x:24,y:24,z:1,w:8,d:10,h:6,rotation:0,recipe:'Recipe_IronPlate_C',clock:1},packs=['concrete','metal','glass'];
const square={...M.fresh('bounds'),size:32,objects:[{...object,x:16,y:16}]},before=JSON.stringify(square),wide=M.resize(square,{size:96,depth:48,height:128});
assert.deepEqual(M.dimensions(wide),{width:96,depth:48,height:128});assert.equal(wide.objects[0].x,48);assert.equal(wide.objects[0].y,24);assert.equal(JSON.stringify(square),before);assert.deepEqual(M.read(JSON.stringify(wide)),wide);
assert.ok(M.candidate({...wide,objects:[]},{...object,x:80,y:24,z:90})===null);assert.match(M.candidate(wide,{...object,y:47}),/dépasse/);assert.match(M.candidate(wide,{...object,z:124}),/dépasse/);
assert.throws(()=>M.resize(wide,{size:96,depth:8,height:128}),/débordent/);assert.throws(()=>M.resize(wide,{size:95,depth:48,height:128}),/multiples/);
let scenes=0;
for(const [size,depth,height]of [[96,48,96],[48,96,128],[96,96,160],[32,80,128]])for(const fit of ['plot','occupied'])for(const facadeForm of ['flat','warehouse','gallery','terraces']){
 const p={...M.fresh('rect'),size,depth,height,objects:[{...object,x:size/2,y:depth/2,z:73}],design:{...D.preset('warehouse',{packs}),fit,facadeForm,roofForm:'monitor'}};
 const parts=D.envelope(p);assert.ok(parts.length);for(const q of parts){const b=M.bounds(q);assert.ok(b.minX>=-.001&&b.minY>=-.001&&b.maxX<=size+.001&&b.maxY<=depth+.001);assert.ok(q.z>=0&&q.z+q.h<=height+.001);}
 assert.equal(D.openings(p),0);assert.deepEqual(M.read(p).design,p.design);scenes++;
}
const p={...M.fresh('unused'),size:96,depth:96,height:96,objects:[object],design:{...D.preset('warehouse',{packs}),fit:'occupied'}};
assert.ok(D.floorCells({...p,design:{...p.design,enabled:false}},{z:0,thickness:1}).length<144,'Occupied footprint also applies without facade decoration');assert.ok(D.floorCells(p,{z:0,thickness:1}).length<144,'Unused plot is not filled with foundations');assert.ok(D.footprint(p).size<144,'Cladding follows the used footprint');
const rectangle={...p,objects:[12,36,60,84].flatMap((x,i)=>[12,36].map((y,j)=>({...object,id:'cell-'+i+'-'+j,x,y}))),design:{...p.design,footprint:'rectangle'}};assert.equal(D.footprint(rectangle).size,72,'A 12 by 12 plot holds an exact 12 by 6 building');assert.equal(Math.max(...[...D.footprint(rectangle)].map(k=>Number(k.split(',')[1]))),5);
const flows={inputs:[{id:'Desc_OreCopper_C',rate:60}],outputs:[{id:'Desc_CopperIngot_C',rate:60}]};
for(const volume of [{size:96,depth:48,height:96},{size:48,depth:96,height:128}]){const result=A.calculate(flows,data,{...volume,physical:true,generation:{priority:'architecture',storeyMode:'single'}});assert.equal(M.problems({...volume,objects:[...result.objects,...result.logistics],links:result.links}).length,0);}
console.log(`PASS: ${scenes} rectangular/tall design scenes, independent XYZ bounds, atomic resizing, JSON migration, occupied cladding/floors and rectangular calculator routing`);
