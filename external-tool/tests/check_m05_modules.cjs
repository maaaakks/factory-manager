const assert=require('node:assert/strict'),D=require('../dist/workshop-design.js'),M=require('../dist/workshop-model.js'),G=D.M05;
assert.equal(Object.keys(D.GROUPS)[0],'m05');assert.equal(Object.keys(D.PRESETS)[0],'m05-kit');assert.equal(Object.keys(G.library.modules).length,12);
const base={...M.fresh('m05'),size:120,depth:120,height:48,objects:[],design:D.preset('m05',{packs:['concrete','metal','glass']})};
for(let variant=1;variant<=6;variant++){
 const p={...base,design:D.preset('m05',base.design,variant)},tiles=G.layout(p),parts=D.envelope(p);assert.equal(tiles.length,9);assert.equal(tiles.filter(t=>/^C/.test(t.name)).length,4);assert.equal(tiles.filter(t=>/^M/.test(t.name)).length,4);assert.equal(tiles.filter(t=>/^IN/.test(t.name)).length,1);
 assert.ok(new Set(tiles.filter(t=>/^M/.test(t.name)).map(t=>t.name)).size===2,'Front and sides use coherent complementary facades');
 assert.deepEqual(parts,D.envelope(p));assert.ok(parts.length>2000);let faces=0;
 for(const part of parts){for(const face of G.geometry(part)){assert.ok(face.coords.length>=3);for(const point of face.coords)assert.ok(point.every(Number.isFinite));faces++;}}
 assert.ok(faces>10000);assert.equal(D.openings(p),0);assert.deepEqual(M.read(p).design,p.design);
}
for(const [size,depth]of [[80,80],[120,80],[160,120],[136,96]]){
 const p={...base,size,depth};assert.equal(G.layout(p).length,Math.floor(size/40)*Math.floor(depth/40));assert.ok(D.floorCells(p,{z:0}).every(([x,y])=>x*8>=24&&y*8>=24));
}
assert.throws(()=>D.envelope({...base,size:48}),/80/);assert.throws(()=>D.envelope({...base,objects:[{z:25,h:9}]}),/30/);
assert.throws(()=>D.envelope({...base,objects:[{type:'smelter',name:'Trop près du bord',x:12,y:60,z:1,h:9,w:6,d:9,rotation:0}]}),/bande de 24/);
const small={...M.fresh('small'),objects:[{id:'c',type:'constructor',name:'Constructeur',x:16,y:16,z:0,w:8,d:10,h:6,rotation:0}],design:base.design},before=JSON.stringify(small),grown=D.prepareM05(small);assert.equal(grown.size,80);assert.equal(grown.depth,80);assert.equal(grown.objects[0].x,40);assert.equal(grown.objects[0].y,40);assert.equal(JSON.stringify(small),before);assert.ok(D.envelope(grown).length>1500);
console.log('PASS: 12 measured sources; six symmetric C/M/IN compositions, geometry, sizing, floor margins, deterministic variants, format errors and reversible fitting.');

