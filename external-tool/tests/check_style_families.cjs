const assert=require('node:assert/strict'),fs=require('node:fs'),D=require('../dist/workshop-design.js'),M=require('../dist/workshop-model.js');
assert.deepEqual(D.CATALOG,JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'../data/architecture-styles.json'),'utf8')),'Browser and native style catalogs match');
const base={...M.fresh('families'),size:48,objects:[{id:'machine',type:'constructor',name:'Test',x:24,y:24,z:1,w:8,d:10,h:6,rotation:0}],structure:{gap:4,pitch:'minimum',thickness:1,material:'concrete',color:'#536454'},floors:[{z:0,thickness:1,material:'concrete',color:'#536454',shaft:2}]},packs=['concrete','metal','glass'];
const before=JSON.stringify(base);let count=0;
for(const [id,family]of Object.entries(D.PRESETS).filter(([id,f])=>id!=='m05'&&!f.nativeStudy)){
 assert.ok(D.GROUPS[family.group]);const shapes=new Set();
 for(const size of [32,40,48])for(const variant of [1,2,3,6]){
  const p={...base,size,objects:base.objects.map(o=>({...o,x:size/2,y:size/2})),design:D.preset(id,{packs},variant)},a=D.envelope(p);
  assert.deepEqual(a,D.envelope(p));assert.equal(p.design.family,id);assert.equal(p.design.variant,variant);assert.ok(a.some(o=>o.component==='roof'));assert.ok(a.some(o=>o.component==='window'),'Every family offers glazing in a short factory');
  if(id==='warehouse'){assert.ok(a.some(o=>o.name==='Trame modulaire · montant'));assert.ok(a.some(o=>o.name==='Trame modulaire · traverse'));}
  if(id==='compact')assert.ok(!a.some(o=>o.name.startsWith('Trame modulaire')));
  for(const part of a){const b=M.bounds(part);assert.ok(b.minX>=-.001&&b.minY>=-.001&&b.maxX<=size+.001&&b.maxY<=size+.001);assert.ok(part.z>=0&&part.z+part.h<=size);}
  assert.deepEqual(M.read(p).design,p.design);if(size===48)shapes.add(JSON.stringify(a));count++;
 }
 assert.ok(shapes.size>=3,`${id}: variations change geometry or palette, not just metadata`);
 const d=D.preset(id,{packs,colors:{machines:'#111111'}});d.entrance='left';d.roof=false;const varied=D.vary(d);
 assert.equal(varied.family,id);assert.equal(varied.variant,2);assert.equal(varied.entrance,'left');assert.equal(varied.roof,false);assert.deepEqual(varied.colors,d.colors);assert.equal(D.vary({...d,variant:999}).variant,1);
}
assert.equal(JSON.stringify(base),before);assert.throws(()=>D.vary({}),/famille/);assert.throws(()=>D.settings({palette:'constructor'}),/invalide/);assert.throws(()=>D.settings({family:'unknown'}),/invalide/);assert.throws(()=>D.preset('warehouse',{packs:['concrete']}),/débloqué/);
console.log(`PASS: ${count} style scenes, ${Object.keys(D.PRESETS).filter(id=>id!=='m05'&&!D.PRESETS[id].nativeStudy).length} categorized families, native bounds, short-factory glazing, deterministic geometry variants, catalog parity, JSON persistence, pack locks and no production mutation`);

