const assert=require('node:assert/strict'),D=require('../dist/workshop-design.js'),M=require('../dist/workshop-model.js');
const base={...M.fresh('design-test'),size:32,objects:[{id:'a',type:'constructor',name:'Test',x:12,y:12,z:0,w:8,d:10,h:6,rotation:0}]};
base.design=D.settings({enabled:true,packs:['concrete','metal'],style:'ficsit',colors:{machines:'#252a2d'}});
const original=JSON.stringify(base),parts=D.envelope(base);assert.ok(parts.length>0);assert.equal(JSON.stringify(base),original);
assert.deepEqual(D.envelope(base),parts,'Deterministic generation');assert.ok(parts.some(p=>p.name==='Angle · montant unique'));
for(const p of parts){const bounds=M.bounds(p);assert.ok(bounds.minX>=-1e-7&&bounds.maxX<=32+1e-7&&bounds.minY>=-1e-7&&bounds.maxY<=32+1e-7);assert.ok(p.z>=0&&p.z+p.h<=32);}
assert.equal(D.color(base,base.objects[0]),'#252a2d');assert.deepEqual(M.read(base).design,base.design);assert.equal(D.available('glass',['concrete']),false);
assert.throws(()=>D.envelope({...base,design:{...base.design,style:'glass'}}),/débloqué/);
assert.deepEqual(D.envelope({...base,design:{...base.design,enabled:false}}),[]);
const full=D.envelope({...base,design:{...base.design,windowEvery:99}});assert.ok(full.filter(x=>x.name==='Mur plein').length>parts.filter(x=>x.name==='Mur plein').length);
assert.throws(()=>M.read({...base,generation:{pitch:3}}),/Options/);assert.throws(()=>D.settings({seed:Infinity}),/invalide/);assert.throws(()=>D.settings({colors:{machines:'red'}}),/invalide/);
console.log('PASS: deterministic style volumes, bounds, palette persistence, locked packs, wall variants and invalid imports');
const compact={...base,nativeProfile:'iron-plates-pairs-v1',floors:[{z:0,thickness:1,material:'concrete',profile:'solid'},{z:10,thickness:1,material:'concrete',profile:'frame'}],objects:[...base.objects,{id:'lift',type:'lift',x:8,y:8,z:3,h:10,w:1.2,d:1.2,rotation:0}]};
const slabs=D.floors(compact,'polished','solid');assert.equal(slabs[0].material,'polished');assert.equal(slabs[1].profile,'solid');assert.deepEqual(slabs[1].holes,[[0,0],[0,1],[1,0],[1,1]],'Reserve every tile intersecting the lift footprint');
assert.deepEqual(D.floors({...compact,floors:slabs},'asphalt','frame')[1].holes,[],'Restore open frames without stale slab holes');
assert.throws(()=>D.floors({...compact,floors:[{thickness:2}]},'polished','solid'),/1 m/);
for(const roofStyle of ['tar','ficsit','glass','skylights']){const scene={...base,design:D.settings({enabled:true,roof:true,roofStyle,packs:['concrete','metal','glass']})};assert.equal(D.envelope(scene).filter(x=>x.component==='roof').length,16);assert.ok(D.envelope(scene).every(x=>typeof x.asset==='string'));}
assert.throws(()=>D.envelope({...base,objects:[{...base.objects[0],h:32}],design:D.settings({enabled:true,roof:true})}),/dépasse/);
console.log('PASS: native roof variants, supported floor materials, reversible frame/slab conversion, lift openings and height overflow');
