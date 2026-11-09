const assert=require('node:assert/strict'),fs=require('node:fs'),D=require('../dist/workshop-design'),M=require('../dist/workshop-model'),G=require('../dist/m05-modules'),R=require('../dist/m05-roof');
const base=JSON.parse(fs.readFileSync('../../outputs/facade61-scenes.json','utf8'))[36].project,tests=[];
for(const seed of[1,2,3,4]){
 const p=M.clone(base);p.design.roofSeed=seed;p.design.roofForm='flat';p.design.roofLayout='central';const before=JSON.stringify(p),parts=D.envelope(p),details=parts.filter(q=>q.roofDetail),composition=details.find(q=>q.roofComposition)?.roofComposition;
 assert.equal(JSON.stringify(p),before);assert.equal(composition?.id,['lantern','ridge','sheds','monitor'][seed-1]);assert.ok(details.length>=10);assert.equal(details.filter(q=>q.asset==='LargeVent').length,0);assert.equal(details.filter(q=>q.roofDetail==='Corniche arrondie').length,0);
 assert.ok(details.some(q=>q.start&&Math.abs(q.start[2]-composition.supportZ)<1e-7),'Posts reach actual roof surface');
 for(const q of details){assert.ok(q.signatureBounds.every((r,i)=>r[0]>0&&r[1]<[p.size,p.depth,p.height][i]));const geometry=q.component==='module'?G.geometry(q):G.beamGeometry(q);for(const f of geometry)for(const point of f.coords)assert.ok(point.every((v,i)=>v>=q.signatureBounds[i][0]-1e-6&&v<=q.signatureBounds[i][1]+1e-6));}
 assert.deepEqual(D.envelope(p),parts);tests.push({project:p,parts});
 const off=M.clone(p);off.design.roof=false;assert.equal(D.envelope(off).filter(q=>q.roofDetail).length,0);tests.push({project:off,parts:D.envelope(off)});
 fs.writeFileSync('../../outputs/roof65-'+composition.id+'.factory-blueprint.json',JSON.stringify(p));
}
const p=M.clone(base),raw=tests[0].parts.filter(q=>!q.roofDetail);p.height=32.5;assert.equal(R.apply(raw,p).filter(q=>q.roofDetail).length,0);
fs.writeFileSync('../../outputs/envelope62-scenes.json',JSON.stringify(tests));
console.log('PASS: four complete roof forms, actual supports, native mesh bounds, no repeated rings, deterministic variants, roof toggle and safe refusal with no headroom.');
