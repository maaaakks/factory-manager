const assert=require('node:assert/strict'),fs=require('node:fs'),P=require('../dist/workshop-planning'),D=require('../dist/workshop-design'),M=require('../dist/workshop-model'),data=require('../dist/planner-data');
(async()=>{
 const flows={inputs:[{id:'Desc_OreIron_C',rate:60}],outputs:[{id:'Desc_IronPlateReinforced_C',rate:5}]},source={...M.fresh('regression65'),size:56,name:'Plaques renforcées · 60 → 5',flows,design:D.preset('m05-kit',{packs:['concrete','metal','glass']})},before=JSON.stringify(source);
 for(const reserveCladding of[false,true]){
  const project=await P.build({source,flows,data,generation:D.generation({layoutStyle:'compact',storeyMode:'single',reserveCladding})});assert.equal(project.size,reserveCladding?48:40);assert.equal(project.floors.length,1);assert.equal(project.generation.storeyMode,'single');assert.equal(JSON.stringify(source),before);assert.equal(project.objects.filter(o=>o.recipe).length,8);
  if(reserveCladding)assert.equal(D.openings(project),0);assert.ok(project.links.some(l=>l.kind==='belt'));assert.deepEqual(project.flows.inputs,flows.inputs);assert.deepEqual(project.flows.outputs,flows.outputs);M.read(project);
  fs.writeFileSync('../../outputs/iron65-'+reserveCladding+'.factory-blueprint.json',JSON.stringify(project));
 }
 const previous=JSON.parse(fs.readFileSync('../../outputs/terrain64-native.factory-blueprint.json','utf8'));previous.size=56;previous.generation.sizing='auto';delete previous.generation.plot;
 const candidates=P.candidates(flows,data,D.generation({layoutStyle:'compact',reserveCladding:true}));assert.ok(candidates.some(q=>q.size===40)&&candidates.some(q=>q.size===48));
 console.log('PASS: 60 iron -> 5 reinforced plates, exactly one production floor, 5x5 compact, 6x6 with complete cladding, shrinking from 7x7, unchanged flows and atomic source.');
})().catch(e=>{console.error(e);process.exitCode=1;});
