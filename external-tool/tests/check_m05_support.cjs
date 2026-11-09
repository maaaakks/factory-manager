const assert=require('node:assert/strict'),fs=require('node:fs'),D=require('../dist/workshop-design'),M=require('../dist/workshop-model'),G=require('../dist/m05-modules');
const rows=[];
for(const size of[32,40,48])for(const seed of[1,2,3,4,5,6]){
 const p={...M.fresh('support63'),size,depth:size,height:48,name:'M05 · Appuis '+size/8+'×'+size/8+' · '+seed,objects:[{id:'m',type:'constructor',name:'Constructeur',x:size/2,y:size/2,z:1,w:8,d:10,h:6,rotation:0,clock:1,recipe:'Recipe_IronPlate_C'}],links:[],floors:[{z:0,thickness:1,material:'concrete',color:'#536454',shaft:2}],structure:{gap:4,pitch:'minimum',thickness:1,material:'concrete',color:'#536454'},design:{...D.preset('m05-kit',{packs:['concrete','metal','glass']},seed),fit:'plot',roofForm:'flat',entrance:'auto'}};
 const before=JSON.stringify(p),parts=D.envelope(p);assert.equal(before,JSON.stringify(p));
 for(const q of parts.filter(q=>q.facadeSignature)){
  assert.notEqual(q.facadeSignature.placement,'crown');
  if(q.signatureRegion){assert.ok(q.signatureRegion[2][1]<=q.facadeSignature.wallTop+.75);assert.ok([0,1].includes(q.facadeSignature.supportZ));}
 }
 // One-floor factories cannot acquire the 12 m facade fragments from the old
 // fallback. The only roof furnishings are explicitly supported roof details.
 assert.ok(parts.filter(q=>q.signatureBounds&&!q.roofDetail).every(q=>q.signatureBounds[2][1]<=8.75));
 const courses=parts.filter(q=>q.name==='Angle · bardage ajusté');assert.ok(courses.length);assert.ok(courses.every(q=>q.asset==='Beam_Painted'));
 for(const q of parts.filter(q=>q.roofDetail==='Pied de ventilation')){const roof=parts.find(r=>r.component==='roof'&&r.name==='Toiture'&&Math.abs(r.x-q.start[0])<4&&Math.abs(r.y-q.start[1])<4&&Math.abs(r.z+r.h-q.start[2])<1e-6);assert.ok(roof,'Vent guard foot reaches its roof');}
 for(const q of parts.filter(q=>q.roofDetail==='Corniche arrondie'&&q.start[0]===q.end[0]&&q.start[1]===q.end[1]))assert.ok(parts.some(r=>r.component==='roof'&&r.name==='Toiture'&&Math.abs(r.z+r.h-q.start[2])<1e-6),'Cornice post reaches the roof');
 M.read(JSON.stringify(p));rows.push({project:p,parts});
}
fs.writeFileSync('../../outputs/support63-scenes.json',JSON.stringify(rows));fs.writeFileSync('../../outputs/support63-small.factory-blueprint.json',JSON.stringify(rows[1].project));
console.log('PASS: 18 one-floor layouts, no facade crowns or floating tall modules, low native bays, floor anchoring, roof feet and real painted corner courses.');
