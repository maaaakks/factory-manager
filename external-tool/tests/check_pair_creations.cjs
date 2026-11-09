const assert=require('node:assert/strict'),D=require('../dist/workshop-design'),original=require('../dist/atlas-example.json');
const counts={};for(const spec of Object.values(D.CATALOG.studies))counts[spec.category]=(counts[spec.category]||0)+1;
assert.deepEqual(counts,{Industriel:2,Futuriste:2,Organique:2,Brutaliste:2});
const round=v=>typeof v==='number'?Math.round(v*1e7)/1e7:Array.isArray(v)?v.map(round):v;
const fixed=parts=>parts.filter(q=>q.fixedLayout).map(q=>[q.name,q.asset,round(q.start||[q.x,q.y,q.z]),round(q.end||q.quat||[])]);
for(const family of['prisme','canopee','bastion']){
 const base=structuredClone(original);base.design.family=family;const baseline=D.envelope(base);
 for(const size of[64,72,80,88,96])for(const depth of[48,56,64,72,80]){
  const p=structuredClone(base);p.size=size;p.depth=depth;const before=JSON.stringify(p),parts=D.envelope(p);
  assert.equal(JSON.stringify(p),before);assert.deepEqual(fixed(parts),fixed(baseline));
  for(const q of parts){if(q.start)assert.ok(Math.hypot(...q.start.map((v,i)=>v-q.end[i]))<=16.00001);if(q.quat)assert.ok(Math.abs(q.quat.reduce((s,v)=>s+v*v,0)-1)<1e-7);}
 }
}
console.log('PASS: eight studies, two per category; 75 new sizes, immutable projects, fixed sculpted annexes/porch, native beam lengths and unit panel quaternions.');
