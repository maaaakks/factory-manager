const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=process.argv[2],out=process.argv[3],D=require(path.join(root,'dist/workshop-design')),M=require(path.join(root,'dist/workshop-model')),F=require(path.join(root,'dist/creation-fitting')),P=require(path.join(root,'dist/workshop-planning')),data=require(path.join(root,'dist/planner-data.json')),example=require(path.join(root,'dist/atlas-example.json'));
const totals=p=>{const r={};for(const o of p.objects)if(o.recipe)r[o.recipe]=(r[o.recipe]||0)+o.clock;return r;};
(async()=>{
 const motor=await P.build({data,flows:{inputs:[{id:'Desc_SteelIngot_C',rate:2.25}],outputs:[{id:'Desc_Motor_C',rate:.25}]},generation:{layoutStyle:'balanced'}}),baseline=JSON.stringify(motor),rows=[];
 for(const id of Object.keys(D.PRESETS).filter(id=>D.PRESETS[id].nativeStudy)){
  const initial=JSON.stringify(example),fitted=F.fit(example,id,['concrete','metal','glass']);assert.equal(JSON.stringify(example),initial);
  const dx=fitted.objects[0].x-example.objects[0].x,dy=fitted.objects[0].y-example.objects[0].y;
  for(let i=0;i<example.objects.length;i++)assert.deepEqual(fitted.objects[i],{...example.objects[i],x:example.objects[i].x+dx,y:example.objects[i].y+dy});
  assert.deepEqual(fitted.links.map(l=>l.native),example.links.map(l=>l.native));assert.deepEqual(fitted.flows,example.flows);assert.deepEqual(M.problems(fitted),[]);
  const q=await F.reflow(motor,id,['concrete','metal','glass'],data);assert.equal(JSON.stringify(motor),baseline);assert.equal(q.floors.length,1);assert.deepEqual(q.flows,motor.flows);assert.deepEqual(totals(q),totals(motor));assert.deepEqual(q.buffer,motor.buffer);assert.equal(q.id,motor.id);assert.deepEqual(M.problems(q),[]);assert.equal(M.read(q).design.studyFitted,true);
  for(const p of [fitted,q])rows.push({project:p,parts:D.envelope(p),floors:p.floors.map(f=>D.floorCells(p,f).sort((a,b)=>a[0]-b[0]||a[1]-b[1]))});
 }
 const impossible=M.clone(example);impossible.objects[0].h=200;assert.throws(()=>F.fit(impossible,'lumen',['concrete','metal','glass']),/ne tient pas/);assert.equal(impossible.objects[0].h,200);
 assert.throws(()=>F.fit(example,'lumen',['concrete']),/débloqué/);
 await assert.rejects(()=>F.reflow({...motor,nativeProfile:'iron-plates-pairs-v1'},'lumen',['concrete','metal','glass'],data),/calibré/);
 const bad=M.clone(rows[0].project);bad.design.studyFloors=[{z:0,cells:[[99,0]]}];assert.throws(()=>D.settings(bad.design),/invalides/);
 const colliding=M.clone(rows[0].project);const wall=D.envelope(colliding).find(q=>q.component==='wall');colliding.objects[0].x=wall.x;colliding.objects[0].y=wall.y;colliding.objects[0].z=wall.z;assert.throws(()=>D.envelope(colliding),/rencontre/);
 fs.writeFileSync(out,JSON.stringify(rows));console.log('PASS: 8 rigid fits + 8 motor reflows; source immutable, recipes/rates retained, native spans retained, valid floors, atomic refusal and locked packs.');
})().catch(e=>{console.error(e);process.exit(1)});
