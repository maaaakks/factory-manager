const assert=require('node:assert/strict'),fs=require('node:fs'),D=require('../dist/workshop-design'),M=require('../dist/workshop-model'),F=require('../dist/m05-facade');
const template=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'fixtures/architecture-finishes.json'),'utf8')),rows=[];
assert.equal(D.generation().floorProfile,'factory');
let garages=0,terraces=0;
for(const size of [40,80])for(const seed of [1,2,3])for(const profile of ['frame','factory','solid']){
 const p=M.clone(template);p.size=size;p.depth=size;p.height=64;p.objects[0].x=size/2;p.objects[0].y=size/2;p.design.seed=seed;p.design.roofSeed=3;p.design.family='m05-kit';p.design.facadeForm='warehouse';p.floors=[0,12,24].map(z=>({z,thickness:1,material:'concrete',color:'#536454',shaft:2,profile,holes:[[1,1]]}));p.generation=D.generation({floorProfile:profile});
 const before=JSON.stringify(p),parts=D.envelope(p),floors=p.floors.map(f=>D.floorCells(p,f));assert.equal(JSON.stringify(p),before);assert.deepEqual(D.envelope(p),parts);assert.deepEqual(D.floors(p,'concrete',profile).map(f=>f.holes),[[],[],[]]);assert.ok(floors[0].some(c=>c[0]===1&&c[1]===1),'No automatic shaft reservations');
 for(const q of parts.filter(q=>q.asset==='BigGarageDoor_16x8')){
  garages++;const signature=parts.find(r=>r.facadeSignature?.id==='portique'&&r.signatureRegion&&[q.x,q.y,q.z+.1].every((v,i)=>v>=r.signatureRegion[i][0]&&v<=r.signatureRegion[i][1]));const region=signature?.signatureRegion;assert.ok(region,'Garage retains its full facade feature');
  const side=signature.facadeSignature.side,axis=side%2?1:0,normal=1-axis,cx=q[axis===0?'x':'y'],base=signature.facadeSignature.supportZ;
  const passage=[[0,0],[0,0],[base+.1,base+7.1]];passage[axis]=[cx-6.9,cx+6.9];passage[normal]=region[normal];
  const overlaps=b=>b.every((r,i)=>Math.min(r[1],passage[i][1])-Math.max(r[0],passage[i][0])>.05);
  for(const r of parts.filter(r=>r!==q&&r.asset!=='BigGarageDoor_16x8'))assert.ok(!overlaps(F.bounds(r)),`Garage passage obstructed by ${r.name}`);
 }
 for(const q of parts.filter(q=>q.platform||q.name==='Terrasse de retrait')){
  terraces++;const b=F.bounds(q);for(let i=0;i<p.floors.length;i++){const f=p.floors[i];if(Math.abs(b[2][1]-(f.z+f.thickness))>=.8)continue;for(const [x,y]of floors[i])assert.ok(!(Math.min(b[0][1],x*8+8)-Math.max(b[0][0],x*8)>7&&Math.min(b[1][1],y*8+8)-Math.max(b[1][0],y*8)>7),'Duplicate floor under terrace');}
 }
 M.read(p);rows.push({project:p,parts,floors});
}
assert.ok(garages>0&&terraces>0);fs.writeFileSync(process.env.FACTORY_FINISHES_REPORT||require('node:path').join(__dirname,'../data/finishes-test-scenes.json'),JSON.stringify(rows));console.log(`PASS: ${rows.length} finish scenes, ${garages} preserved garages, ${terraces} terraces, three floor profiles and no reserved holes.`);
