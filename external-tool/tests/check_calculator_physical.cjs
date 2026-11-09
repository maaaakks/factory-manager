const assert=require('node:assert/strict'),M=require('../dist/workshop-model.js'),A=require('../dist/workshop-assist.js'),F=require('../dist/flow-core.js'),data=require('../dist/planner-data.json');
const flows={inputs:[{id:'Desc_OreIron_C',rate:30}],outputs:[{id:'Desc_IronPlate_C',rate:20}]};
for(const storeyMode of ['single','vertical']){
 const generation={layoutStyle:'compact',storeyMode,maxStoreys:2,routed:true},r=A.calculate(flows,data,{size:32,physical:true,generation});
 const p=M.read({...M.fresh('physical-'+storeyMode),size:32,objects:[...r.objects,...r.logistics],links:r.links,floors:r.floors,structure:r.structure,flows,generation});
 assert.equal(p.floors.length,storeyMode==='single'?1:2);assert.equal(M.problems(p).length,0);assert.ok(p.links.every(l=>l.kind==='belt'));assert.ok(p.objects.some(o=>M.visible(p,o,p.floors.at(-1).z)),'Minimum height keeps the last storey visible');
 const entry=p.objects.find(o=>o.io?.side==='input'),output=p.objects.find(o=>o.io?.side==='output');assert.equal(entry.io.item,'Desc_OreIron_C');assert.equal(output.type,'storage');
 for(const link of p.links){const path=A.route(p,link.from,link.to);assert.ok(path?.length);assert.ok(path.every(pt=>pt.x>=0&&pt.x<=32&&pt.y>=0&&pt.y<=32));if(link.via)assert.ok(new Set(path.map(pt=>pt.z)).size>1,'Vertical conveyor has a continuous 3D route');}
 const report=F.analyze(p,data,{linkAvailable:l=>!!A.route(p,l.from,l.to)});assert.equal(report.endpoints.get(output.id).actual,20);assert.equal(report.endpoints.get(output.id).efficiency,100);
 assert.deepEqual(M.read(JSON.stringify(p)),p);
}
const reinforced={inputs:[{id:'Desc_OreIron_C',rate:60}],outputs:[{id:'Desc_IronPlateReinforced_C',rate:5}]};
const one=A.calculate(reinforced,data,{size:48,physical:true,generation:{layoutStyle:'compact',storeyMode:'single',maxStoreys:1,routed:true}});
assert.equal(one.floors.length,1);assert.ok(one.links.every(l=>l.kind==='belt'));
assert.throws(()=>A.calculate(reinforced,data,{size:32,physical:true,generation:{layoutStyle:'compact',storeyMode:'single',maxStoreys:1}}),/8 machines.*1 étage/);
console.log('PASS: one/two-storey preferences, explicit interfaces and storage, complete belt paths, continuous lift routes, material flow and persistence');
