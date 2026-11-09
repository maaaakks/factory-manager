const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]),D=require(path.join(root,'dist/workshop-design')),L=require(path.join(root,'dist/creation-living')),F=require(path.join(root,'dist/creation-fitting')),M=require(path.join(root,'dist/workshop-model'));
const source=require(path.join(root,'tests/fixtures/living-calibrated.json')),motor=require(path.join(root,'tests/fixtures/living-two-storeys.json')),original=JSON.stringify(source),rows=[];
function verify(p,fitted){
 assert.equal(JSON.stringify(source),original);assert.deepEqual(p.objects.filter(o=>o.type!=='wallPole'),fitted.objects.filter(o=>o.type!=='wallPole'));assert.deepEqual(p.links,fitted.links);assert.deepEqual(p.flows,fitted.flows);
 assert.deepEqual(M.problems(p),[]);assert.equal(p.design.living.revision,2);assert.deepEqual(M.read(p).design.living,p.design.living);
 const parts=D.envelope(p),living=p.design.living;
 assert.ok(!living.accessParts.some(q=>q.livingFloorMark||/guide piéton|poste d’inspection/.test(q.name)));
 assert.equal(p.design.studyFloors[0].cells.length,p.size*(p.depth??p.size)/64);assert.ok(p.floors.every(f=>f.profile==='solid'&&f.material==='concrete'));
 for(const q of living.fixtures){
  const wall=parts.find(w=>q.mount.wall.every((v,i)=>v===[w.x,w.y,w.z,w.rotation][i]));assert.ok(wall,'Every light fixture has a real wall');
  assert.ok(!parts.some(w=>!(w.asset===q.asset&&w.x===q.x&&w.y===q.y&&w.z===q.z)&&w!==wall&&L.hit(L.box(q),L.box(w))),'Hardware clears structure and other fixtures');
 }
 for(const o of p.objects.filter(o=>o.type==='wallPole')){assert.ok(o.native.wallMounted);const walls=parts.filter(q=>q.component==='wall'&&o.z>=q.z&&o.z<=q.z+q.h);assert.ok(walls.some(w=>{const b=L.box(w),a=b[0][1]-b[0][0]<b[1][1]-b[1][0]?0:1,v=a?o.y:o.x;return Math.min(Math.abs(v-b[a][0]),Math.abs(v-b[a][1]))<.026;}),'Power mounting plate flush to wall');}
 assert.ok(living.levels.every(l=>l.missing.length===0));
 rows.push({project:p,parts,floors:p.floors.map(f=>D.floorCells(p,f)),colors:p.floors.flatMap(f=>D.floorCells(p,f).map(([x,y])=>[f.z,x,y,L.floorColor(p,f,x*8+4,y*8+4,'#000000')]))});
}
for(const family of Object.keys(D.PRESETS).filter(k=>D.PRESETS[k].nativeStudy&&!D.CATALOG.studies[D.PRESETS[k].nativeStudy]?.designFirst)){const fitted=F.fit(source,family,['concrete','metal','glass']),p=L.plan(fitted);verify(p,fitted);assert.equal(p.design.living.levels[0].stations.length,8);const old=structuredClone(p);delete old.design.living.revision;assert.equal(L.matches(old),false);assert.equal(M.read(old).design.living,undefined);}
for(const family of ['atlas','sylva']){const fitted=F.fit(motor,family,['concrete','metal','glass']),p=L.plan(fitted);verify(p,fitted);assert.equal(p.design.living.levels.reduce((n,l)=>n+l.stations.length,0),9);}
fs.writeFileSync(path.join(out,'living-tests.json'),JSON.stringify(rows));
(async()=>{const spacious=require(path.join(root,'tests/fixtures/living-spacious.json'));let request;global.fetch=async(url,body)=>{request=JSON.parse(body.body);return{ok:true,json:async()=>({project:structuredClone(spacious)})}};
 for(const family of ['atlas','sylva']){const p=await F.reflow(source,family,['concrete','metal','glass'],null);assert.equal(request.options.layoutStyle,'spacious');assert.equal(p.design.living.levels[0].stations.length,8);assert.deepEqual(M.problems(p),[]);fs.writeFileSync(path.join(out,family+'-spacious.json'),JSON.stringify(p));}
 console.log('PASS: 8 styles + 2 storeys: full solid floor, no beam markings, flush wall power mounts, clear lights, machine/network preservation; native aired reflow exercised.');
})().catch(e=>{console.error(e);process.exitCode=1});
