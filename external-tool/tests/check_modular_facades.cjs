const assert=require('node:assert/strict'),D=require('../dist/workshop-design.js'),M=require('../dist/workshop-model.js');
const base={...M.fresh('relief'),size:48,objects:[{id:'m',type:'constructor',name:'Test',x:24,y:24,z:22,w:8,d:10,h:6,rotation:0}],floors:[{z:0,thickness:1,material:'concrete'}],design:D.preset('warehouse',{packs:['concrete','metal','glass']})};
const before=JSON.stringify(base),forms=[];
for(const facadeForm of ['warehouse','gallery','terraces'])for(const roofForm of ['flat','monitor','sawtooth']){
 const p={...base,design:{...base.design,facadeForm,roofForm}},bands=D.facadeBands(p),parts=D.envelope(p);
 assert.ok(new Set(bands.map(b=>[...b.cells].join(';'))).size>1,'Relief changes actual occupied cells by height');
 assert.ok(parts.some(q=>q.name==='Terrasse de retrait'),'Setbacks have caps');
 if(facadeForm!=='terraces')assert.ok(parts.some(q=>q.name==='Sous-face du volume saillant'),'Projecting bays have closed undersides');
 if(roofForm==='monitor')assert.ok(parts.some(q=>q.name==='Lanterneau · vitrage vertical'));
 if(roofForm==='sawtooth')assert.ok(parts.some(q=>q.component==='gable'),'Pitched roof ends are closed');
 assert.equal(D.openings(p),0,'Completed volume has no unintended facade holes');
 const columns=parts.filter(q=>q.name==='Angle · montant unique');assert.ok(columns.length>4,'Recessed corners own columns too');
 for(const q of parts){const b=M.bounds(q);assert.ok(b.minX>=-.001&&b.minY>=-.001&&b.maxX<=p.size+.001&&b.maxY<=p.size+.001);if(q.start)assert.ok(Math.hypot(...q.start.map((v,i)=>v-q.end[i]))<=16.000001,'Native beam length cap');}
 for(let i=0;i<columns.length;i++)for(let j=i+1;j<columns.length;j++){const a=columns[i],b=columns[j];if(Math.abs(a.x-b.x)<.001&&Math.abs(a.y-b.y)<.001)assert.ok(Math.min(a.end[2],b.end[2])-Math.max(a.start[2],b.start[2])<.001,'No duplicate corner posts');}
 assert.ok(!parts.some(q=>q.component==='corner'),'No overlapping legacy pillar stack');
 assert.ok(!parts.some(q=>q.name==='Corniche · raccord arrêté'),'No coplanar corner cornice over the beam cladding');
 if(roofForm==='flat')forms.push(JSON.stringify(parts));
}
assert.equal(new Set(forms).size,3,'Three facade compositions change geometry');
const occupied={...base,objects:[{...base.objects[0],x:24,y:4,z:8,w:8,d:6,h:8}]};
assert.ok(D.facadeBands(occupied).filter(b=>b.bottom>=8&&b.bottom<16).every(b=>b.cells.has('2,0')&&b.cells.has('3,0')),'Do not recess occupied bays');
const belt={...base,links:[{kind:'belt',physicalRoute:[{x:0,y:4,z:14},{x:48,y:4,z:14}]}]};
assert.ok(D.facadeBands(belt).find(b=>b.bottom===12).cells.has('1,0'),'Protect physical conveyor routes');
assert.equal(JSON.stringify(base),before);assert.throws(()=>D.settings({facadeForm:'unknown'}),/invalide/);
console.log('PASS: nine tall modular facades, three distinct relief grammars, owned convex/concave corners, capped terraces and soffits, closed roof ends, legal beams, no production mutation and obstacle protection');
