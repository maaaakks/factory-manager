const assert=require('node:assert/strict'),P=require('../dist/factory-preview.js'),G=require('../dist/preview-gpu.js'),D=require('../dist/workshop-design.js'),M=require('../dist/workshop-model.js');
for(const level of ['good','warning','critical','unknown'])assert.equal(P.diagnosticTint({category:'machine'},{level}),null,'Diagnostics must preserve building colors');
assert.equal(P.diagnosticTint({category:'conveyor'},{level:'good'}),'#8ca6b2');assert.equal(P.diagnosticTint({category:'conveyor'},{level:'warning'}),'#f2ac52');assert.equal(P.diagnosticTint({category:'conveyor'},{level:'critical'}),'#ec6464');
const face={coords:[[10000,10000,0],[10008,10000,0],[10008,10008,0],[10000,10008,0]]},line={coords:[[10000,10000,0],[10008,10000,0]]};
const clean=G.prepareGeometry([face,{coords:[...face.coords].reverse()}],[line,{coords:[...line.coords].reverse()}]);assert.equal(clean.faces.length,1);assert.equal(clean.lines.length,1);assert.deepEqual(clean.depthFrame.slice(0,3),[10004,10004,0]);assert.ok(clean.depthFrame[3]<6);assert.deepEqual(G.prepareGeometry([],[]).depthFrame,[0,0,0,1]);
const p={...M.fresh('entry'),size:32,floors:[{z:0,thickness:1,material:'concrete'}],design:D.settings({enabled:true,entrance:'front'})};
const entryParts=q=>D.envelope(q).filter(p=>p.name.startsWith('Entrée piétonne'));
assert.equal(entryParts(p).length,3);assert.equal(D.openings(p),0,'Intentional entry is not a collision gap');
assert.equal(entryParts({...p,design:{...p.design,entrance:'none'}}).length,0);
const obstacle={id:'blocked',type:'constructor',x:16,y:3,z:1,w:32,d:5,h:7,rotation:0};assert.equal(entryParts({...p,objects:[obstacle]}).length,0,'Do not open an entrance into a machine');
const belt={kind:'belt',from:'x',to:'y',physicalRoute:[{x:0,y:2,z:2},{x:32,y:2,z:2}]};assert.equal(entryParts({...p,links:[belt]}).length,0,'A belt crossing the approach blocks the entrance');
assert.equal(entryParts({...p,links:[{...belt,physicalRoute:belt.physicalRoute.map(q=>({...q,z:10}))}]}).length,3,'An overhead belt with sufficient clearance is allowed');
for(const key of Object.keys(D.PRESETS).filter(id=>id!=='m05'&&!D.PRESETS[id].nativeStudy)){const d=D.preset(key,{packs:['concrete','metal','glass']});assert.equal(d.enabled,true);assert.equal(d.roof,true);assert.equal(d.entrance,'auto');assert.equal(d.footprint,D.PRESETS[key].footprints?.[0]||D.PRESETS[key].footprint);assert.ok(entryParts({...p,design:d}).length);}
assert.throws(()=>D.preset('campus',{packs:['concrete']}),/débloqué/);
const decorated=D.envelope({...p,design:{...p.design,wallDecoration:'lattice'}}),wall=decorated.find(o=>o.component==='wall'&&o.rotation===0&&o.z===8);
// Wall, band and beams occupy distinct outward planes; lattice diagonals are offset.
const bare={...p,objects:[{id:'high',type:'constructor',x:16,y:16,z:4,w:8,d:8,h:6,rotation:0}],design:{...p.design,wallDecoration:'lattice',entrance:'none'}};
const parts=D.envelope(bare),diagonal=parts.find(o=>o.name==='Contreventement diagonal'&&o.start[1]<1),cross=parts.find(o=>o.name==='Croix de contreventement'&&o.start[1]<1);
assert.ok(Math.abs(diagonal.start[1]-cross.start[1])>=.0999);assert.ok(parts.some(o=>o.component==='wall'&&o.y===.9));
console.log('PASS: neutral buildings and healthy belts, warning colors, duplicate face/edge removal, local depth range, access blocked by machines/belts, overhead clearance and coherent presets');



