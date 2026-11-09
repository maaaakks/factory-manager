const assert=require('node:assert/strict'),fs=require('node:fs');
const D=require('../dist/workshop-design'),M=require('../dist/workshop-model');
const base=JSON.parse(fs.readFileSync(__dirname+'/fixtures/architecture-finishes.json','utf8'));
const packs=['concrete','metal','glass'],rows=[];
assert.deepEqual(Object.entries(D.PRESETS).filter(([id,f])=>!f.hidden&&id!=='m05').map(([id])=>id),['m05-kit','classics','atlas']);
for(const variant of [1,2,3,4,999])for(const [size,depth,height]of [[32,32,48],[48,40,64],[80,64,64]]){
 const p={...base,size,depth,height,objects:base.objects.map(o=>({...o,x:size/2,y:depth/2,z:size===32?1:17})),floors:[{...base.floors[0],profile:'solid'}],design:D.preset('signature',{packs},variant)};
 if(size!==32)p.floors.push({...base.floors[0],z:16});
 const before=JSON.stringify(p),parts=D.envelope(p);assert.equal(JSON.stringify(p),before);assert.deepEqual(parts,D.envelope(p));
 assert.ok(parts.some(q=>q.name==='Signature · Tableau de baie'));
 assert.ok(parts.some(q=>q.name==='Signature · Rive de toiture'));
 assert.equal(D.openings(p),0,'No missing wall panels');
 for(const q of parts){const b=M.bounds(q);assert.ok(b.minX>=-.001&&b.minY>=-.001&&b.maxX<=size+.001&&b.maxY<=depth+.001&&q.z>=-.001&&q.z+q.h<=height+.001,q.name);}
 assert.deepEqual(M.read(p).design,p.design);
 rows.push({project:p,parts,upperCells:D.floorCells(p,{z:11,thickness:1}).sort((a,b)=>a[0]-b[0]||a[1]-b[1])});
}
const a=rows.find(r=>r.project.size===80&&r.project.design.variant===1),b=rows.find(r=>r.project.size===80&&r.project.design.variant===2);
assert.notDeepEqual(a.parts.map(q=>[q.x,q.y,q.z,q.asset]),b.parts.map(q=>[q.x,q.y,q.z,q.asset]));
for(const k of D.PRESETS.classics.variants){const p={...base,design:D.preset(k,{packs},2)};assert.deepEqual(M.read(p).design,p.design,'Legacy projects preserved');}
assert.ok(D.presetAvailable('classics',['concrete']));assert.ok(!D.presetAvailable('signature',['concrete']));
const blocked={...a.project,objects:[{...a.project.objects[0],x:40,y:4,z:17,w:80,d:8,h:6}]};
assert.ok(D.facadeBands(blocked).filter(b=>b.bottom>=16).every(b=>b.cells.has('5,0')),'No recess through occupied cells');
fs.writeFileSync(require('node:path').join(__dirname,'../data/signature-test-scenes.json'),JSON.stringify(rows));
console.log('PASS: 15 signature scenes, three silhouettes, deterministic variants, native bounds, complete panels, persistence, locks, occupied-cell guard and legacy loading.');
