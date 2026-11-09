const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),P=require('../dist/workshop-planning.js'),D=require('../dist/workshop-design.js'),M=require('../dist/workshop-model.js'),A=require('../dist/workshop-assist.js'),data=require('../dist/planner-data.json');
(async()=>{
 const samples=[];
 for(const [output,rate,input,budget]of [['Desc_CopperIngot_C',60,'Desc_OreCopper_C',60],['Desc_IronRod_C',30,'Desc_IronIngot_C',30],['Desc_Rotor_C',4,'Desc_OreIron_C',45],['Desc_IronPlateReinforced_C',5,'Desc_OreIron_C',60],['Desc_IronPlateReinforced_C',10,'Desc_OreIron_C',120]]){
  for(const mode of ['auto','single','vertical']){
   const p=await P.build({id:'subzone-test',data,flows:{inputs:[{id:input,rate:budget}],outputs:[{id:output,rate}]},generation:D.generation({storeyMode:mode,layoutStyle:'compact'})});
   assert.equal(p.generation.layoutPolicy,'subzones-v1');assert.ok(p.zones.length);assert.ok(p.zones.every(z=>z.machines.length<=2));assert.deepEqual(M.problems(p),[]);assert.deepEqual(M.clearanceIssues(p),[]);assert.deepEqual(M.read(JSON.stringify(p)).zones,p.zones);
   for(const z of p.zones){const machines=z.machines.map(id=>p.objects.find(o=>o.id===id));assert.equal(new Set(machines.map(o=>o.recipe)).size,1);assert.equal(new Set(machines.map(o=>o.z)).size,1);assert.equal(new Set(machines.map(o=>o.y)).size,1);assert.ok(machines.every(o=>o.rotation===180));}
   assert.ok(p.links.filter(l=>l.kind==='belt').every(l=>A.route(p,l.from,l.to)));if(mode!=='vertical'){assert.equal(p.floors.length,1);assert.ok(!p.objects.some(o=>o.type==='lift'));}
   assert.deepEqual(p.flows.outputs,[{id:output,rate}]);samples.push(p);
  }
 }
 for(const shape of ['elongated','exotic']){const p=await P.build({id:'shape',data,flows:{inputs:[{id:'Desc_OreCopper_C',rate:60}],outputs:[{id:'Desc_CopperIngot_C',rate:60}]},generation:D.generation({shape})});assert.deepEqual(M.problems(p),[]);samples.push(p);}
 const source=samples[0],before=JSON.stringify(source);await assert.rejects(P.build({id:source.id,source,data,flows:source.flows,generation:D.generation({storeyMode:'single'}),dimensions:{size:32,depth:32,height:32}}),/dimensions automatiques/);assert.equal(JSON.stringify(source),before);
 const deleted=M.clone(source);deleted.objects=deleted.objects.filter(o=>o.id!==deleted.zones[0].machines[0]);deleted.links=deleted.links.filter(l=>deleted.objects.some(o=>o.id===l.from)&&deleted.objects.some(o=>o.id===l.to));assert.doesNotThrow(()=>M.read(deleted));
 const folder=process.env.SUBZONE_OUTPUT||path.resolve(__dirname,'../data');fs.mkdirSync(folder,{recursive:true});fs.writeFileSync(path.join(folder,'subzone-scenes.json'),JSON.stringify(samples));console.log('PASS: 17 modular scenes; paired recipes, same-floor bays, clearances, complete belts/power, Auto flat, explicit storeys, shape constraints, preserved metadata, edits, atomic refusal.');
})().catch(e=>{console.error(e,e.cause);process.exitCode=1;});

