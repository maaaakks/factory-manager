const assert=require('node:assert/strict'),fs=require('node:fs'),D=require('../dist/workshop-design'),M=require('../dist/workshop-model'),G=require('../dist/m05-modules'),F=require('../dist/m05-facade');
const rows=[],overlap=(a,b)=>a.every((r,i)=>Math.min(r[1],b[i][1])-Math.max(r[0],b[i][0])>.01);
for(const size of[32,40,48])for(const seed of[1,2,3])for(const side of['front','right','back','left']){
 const project={...M.fresh('signature61'),size,depth:size,height:48,name:'Façade M05 '+size/8+'×'+size/8,objects:[{id:'machine',type:'constructor',name:'Constructeur',x:size/2,y:size/2,z:25,w:8,d:10,h:6,rotation:0,clock:1,recipe:'Recipe_IronPlate_C'}],links:[],structure:{gap:4,pitch:'minimum',thickness:1,material:'concrete',color:'#536454'},floors:[0,24].map(z=>({z,thickness:1,material:'concrete',color:'#536454',shaft:2})),design:{...D.preset('m05-kit',{packs:['concrete','metal','glass']},seed),fit:'plot',entrance:side,colors:{walls:'#cb792d',frames:'#354145',windows:'#80b4c7'}}};
 const before=JSON.stringify(project),parts=D.envelope(project),signature=parts.find(q=>q.facadeSignature),features=parts.filter(q=>q.signatureBounds);
 assert.equal(JSON.stringify(project),before);assert.equal(signature.facadeSignature.id,['verriere','portique','galeries'][seed-1]);assert.ok(features.length>=13);assert.equal(D.openings(project),0);M.read(JSON.stringify(project));
 const obstacle=M.bounds(project.objects[0]),b=[[obstacle.minX,obstacle.maxX],[obstacle.minY,obstacle.maxY],[obstacle.minZ,obstacle.maxZ]];
 for(const q of features){assert.ok(q.signatureBounds.every((r,i)=>r[0]>=0&&r[1]<=[size,size,48][i]));assert.ok(!overlap(q.signatureBounds,b));
  const faces=q.component==='module'?G.geometry(q):G.beamGeometry(q);assert.ok(faces.length);
  for(const f of faces)for(const p of f.coords)assert.ok(p.every((v,i)=>v>=q.signatureBounds[i][0]-1e-6&&v<=q.signatureBounds[i][1]+1e-6),'Mesh fits reserved native bounds');
  if(q.start)assert.ok(Math.hypot(...q.start.map((v,i)=>v-q.end[i]))<=16);
 }
 if(seed===2)assert.ok(features.some(q=>q.asset==='BigGarageDoor_16x8'));
 if(seed===3)assert.ok(features.some(q=>q.asset==='Roof_Window_04'));
 rows.push({project,parts});
}
const large=M.clone(rows[0].project);large.size=80;large.depth=80;large.height=64;large.objects[0].x=40;large.objects[0].y=40;large.name='M05 · Façades et toiture 10×10';const parts=D.envelope(large);assert.ok(parts.filter(q=>q.facadeSignature).length>=4);assert.equal(new Set(parts.filter(q=>q.facadeSignature).map(q=>q.facadeSignature.side)).size,4);const regions=parts.filter(q=>q.signatureRegion).map(q=>q.signatureRegion);for(let i=0;i<regions.length;i++)for(let j=i+1;j<regions.length;j++)assert.ok(!overlap(regions[i],regions[j]));rows.push({project:large,parts});
const tight=M.clone(rows[0].project);tight.height=32;tight.floors=[tight.floors[0]];Object.assign(tight.objects[0],{x:16,y:16,z:1,w:28,d:28,h:22});tight.design.entrance='none';const skin=D.envelope(tight),relief=skin.find(q=>q.facadeSignature);assert.equal(relief.facadeSignature.id,'charpente');assert.ok(skin.filter(q=>q.signatureBounds&&!q.roofDetail).every(q=>q.asset==='Beam_Painted'));
rows.push({project:tight,parts:skin,geometryOnly:true});
const compact=JSON.parse(fs.readFileSync('../../outputs/compact60-4x4.factory-blueprint.json','utf8'));for(const seed of[1,2,3]){const project=M.clone(compact);project.name='M05 · Production 4×4 · '+seed;project.design=D.preset('m05-kit',{packs:['concrete','metal','glass']},seed);const before=JSON.stringify(project),parts=D.envelope(project);assert.ok(parts.some(q=>q.facadeSignature));assert.equal(project.size,32);assert.equal(JSON.stringify(project),before);rows.push({project,parts});}
fs.writeFileSync('../../outputs/facade61-scenes.json',JSON.stringify(rows));fs.writeFileSync('../../outputs/facade61-compact-demo.factory-blueprint.json',JSON.stringify(rows.at(-2).project));fs.writeFileSync('../../outputs/facade61-large-demo.factory-blueprint.json',JSON.stringify(large));
console.log('PASS: 36 native-size front compositions, four orientations, occupied volumes protected, independent glazing paint, native mesh bounds, legal H beams, three large-front accents, shallow fallback and unchanged functional 4x4 chain.');

