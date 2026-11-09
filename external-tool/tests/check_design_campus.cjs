const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(process.argv[2]),base=path.resolve(process.argv[3]),D=require(path.join(root,'dist/workshop-design')),C=require(path.join(root,'dist/design-campus')),M=require(path.join(root,'dist/workshop-model')),rows=[];
function check(p){
 const before=JSON.stringify(p),parts=D.envelope(p);assert.equal(JSON.stringify(p),before);assert.deepEqual(M.problems(p),[]);assert.deepEqual(M.read(p).floors,p.floors.map(f=>({...f,holes:[]})));assert.equal(p.objects.length,0);assert.equal(p.links.length,0);assert.equal(p.nativeProfile,undefined);
 for(const q of parts.filter(q=>q.emissiveSign)){assert.equal(q.asset,'StandaloneWidgetSign_Portrait');assert.equal(q.emission,3);assert.ok(Math.abs(Math.hypot(...q.quat)-1)<1e-8);}
 if(p.design.family==='noyau'){
  const a=C.assembly(D.CATALOG.studies.noyau,p),levels=p.design.campusLevels;assert.equal(p.floors.length,levels+1);assert.ok(a.rooms>=4);assert.equal(parts.filter(q=>q.asset==='CatwalkStairs').length,4*levels);
  for(const q of parts.filter(q=>q.asset==='CatwalkStairs'))assert.equal(q.walkEnd[2]-q.walkStart[2],4);
  const ids=new Set();for(const q of parts){const key=[q.asset,q.x,q.y,q.z,q.asset.startsWith('Wall_')?q.rotation%180:q.rotation].join('|');assert.ok(!ids.has(key),'No duplicated native wall faces');ids.add(key);}
  for(const inst of a.instances.filter(i=>i.purpose==='assembler'))assert.equal(inst.prefab,'room_long','An assembler needs a 16 x 32 m room, not a 16 m cell');
  for(const level of Array.from({length:levels},(_,i)=>i)){const rooms=parts.filter(q=>q.campusLevel===level&&q.campusRole.startsWith('room'));assert.ok(rooms.length);assert.ok(rooms.some(q=>q.color===D.CATALOG.studies.noyau.grammar.palettes[level].wall));}
 }
 rows.push({project:p,parts,floors:p.floors.map(f=>D.floorCells(p,f))});return parts;
}
for(const w of [64,96])for(const d of [48,64,80])for(const n of [1,2,3])check(C.project('noyau',w,d,n));
for(const w of [64,80,96])for(const d of [48,64,80])check(C.project('aurore',w,d));
assert.throws(()=>D.envelope(C.project('noyau',72,48)),/Noyau/);
fs.writeFileSync(path.join(base,'parity.json'),JSON.stringify(rows));
for(const [family,w,d,n]of [['noyau',64,48,3],['aurore',64,48,1]])fs.writeFileSync(path.join(base,family+'.json'),JSON.stringify(C.project(family,w,d,n)));
console.log('PASS: 18 Noyau assemblies and 9 Aurore sizes; empty production; real floors, no duplicate walls, native stair rises, separate circulation and correctly sized assembly rooms.');
