const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(process.argv[2]),D=require(path.join(root,'dist/workshop-design')),C=require(path.join(root,'dist/design-campus')),M=require(path.join(root,'dist/workshop-model')),G=require(path.join(root,'dist/m05-modules'));
const source=require(path.join(root,'data/cuivriere-source.json')),rows=[],snapshot=JSON.stringify(D.CATALOG.studies.cuivriere);
for(let width=104;width<=136;width+=8)for(let depth=88;depth<=120;depth+=8){
 const project=C.project('cuivriere',width,depth),parts=D.envelope(project);
 M.read(JSON.stringify(project));assert.equal(project.objects.length,0);assert.equal(project.links.length,0);
 for(const q of parts){assert(q.nativeShell||q.emissiveSign);assert(Math.abs(Math.hypot(...q.quat)-1)<1e-6);assert(G.geometry(q).length>0,q.asset);}
 const leds=parts.filter(q=>q.emissiveSign);assert.equal(leds.length,6);for(const q of leds){assert(Math.abs(q.y-(80.18+depth-88))<1e-6);assert(q.x===1.2||q.x===6.8);}
 rows.push({project,parts});
}
assert.equal(rows[0].parts.length,source.length+6);assert.equal(rows[0].parts.filter(q=>q.emissiveSign).length,6);
const roofGlass=rows[0].parts.filter(q=>q.asset==='FoundationGlass_01');assert.equal(roofGlass.length,34);for(const q of roofGlass){const panes=G.geometry(q).filter(f=>f.glass);assert.equal(panes.length,1);assert.notEqual(panes[0].color,q.color,'Glass must not inherit the copper frame color');}
for(const q of rows[0].parts.filter(q=>q.asset.includes('Tris')))assert.equal(G.geometry(q).length,5,'Cladding must occlude coplanar glazing from both sides');
source.forEach((q,i)=>{const p=rows[0].parts[i];assert.equal(p.asset,q.asset);p.quat.forEach((v,j)=>assert(Math.abs(v-q.quat[j])<1e-9));assert.equal(p.paintFinish,q.finish);for(let j=0;j<3;j++)assert(Math.abs(p[['x','y','z'][j]]-q.pos[j]-(j===2?6:0))<1e-6);});
assert.equal(JSON.stringify(D.CATALOG.studies.cuivriere),snapshot);
for(const [width,depth]of[[96,88],[104,80],[144,88],[104,128],[108,88]])assert.throws(()=>D.envelope(C.project('cuivriere',width,depth)));
fs.writeFileSync(process.argv[3],JSON.stringify(rows));console.log('PASS: 25 dimensions, source poses and finishes, visible geometry, immutable source, invalid dimensions refused');

