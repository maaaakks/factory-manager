const assert=require('node:assert/strict'),fs=require('node:fs'),D=require('../dist/workshop-design');
const original=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'../dist/atlas-example.json'),'utf8'));
for(const family of ['atlas','lumen'])for(const width of [64,72,80,88,96])for(const depth of [48,56,64,72,80]){
 const p=structuredClone(original);p.design.family=family;p.size=width;p.depth=depth;const before=JSON.stringify(p),parts=D.envelope(p);
 assert.equal(JSON.stringify(p),before);assert.ok(parts.length>=D.CATALOG.studies[family].parts.length);
 for(const q of parts)if(q.start)assert.ok(Math.hypot(...q.start.map((v,i)=>v-q.end[i]))<=16.00001);
 if(family==='lumen')assert.equal(parts.filter(q=>q.name==='Lumen · pavillon vitré').length,D.CATALOG.studies.lumen.parts.filter(q=>q.name==='Lumen · pavillon vitré').length);
 if(family==='atlas')assert.equal(parts.filter(q=>q.asset==='CatwalkStairs').length,3);
 const bad=structuredClone(p);bad.objects[0].x=56+width-64;bad.objects[0].y=20;assert.throws(()=>D.envelope(bad),/rencontre/);
}
for(const depth of [40,49,88])assert.throws(()=>D.envelope({...original,depth}),/longueur/);
for(const size of [56,65,104])assert.throws(()=>D.envelope({...original,size}),/largeur/);
console.log('PASS: fifty authored width/length combinations, immutable projects, native beam limits, fixed stairs, collision refusals and invalid-size refusals.');
