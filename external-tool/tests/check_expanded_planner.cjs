const assert=require('node:assert/strict'),data=require('../dist/planner-data.json'),catalog=require('../data/game_catalog.json'),A=require('../dist/workshop-assist'),Flow=require('../dist/flow-core');
assert.equal(Object.keys(data.recipes).length,120);assert.equal(Object.keys(data.defaultRecipes).length,75);
for(const [id,r]of Object.entries(data.recipes)){
 const source=catalog.recipes[id];for(const key of ['seconds','inputs','outputs','producedIn'])assert.deepEqual(r[key],source[key]);
 assert.ok(r.inputs.every(i=>i.solid)&&r.outputs.every(i=>i.solid));assert.ok(r.inputs.length<=(r.type==='assembler'?2:1));
 const next=Flow.assignRecipe({objects:[{id:'machine',type:r.type}]},['machine'],id,data);assert.equal(next.objects[0].recipe,id);
}
for(const [item,recipe]of Object.entries(data.defaultRecipes)){
 assert.equal(data.recipes[recipe].outputs[0].id,item);
 const outputs=[{id:item,rate:1}],d=A.demand({inputs:[],outputs},data),inputs=[...d.requirements].map(([id,rate])=>({id,rate}));
 assert.ok(inputs.length&&inputs.every(i=>Number.isFinite(i.rate)&&i.rate>0));
 if(data.rawResources?.includes(item)){assert.deepEqual(inputs,outputs);continue;}const inverse=A.resolveObjectives('input',inputs,outputs,data);assert.ok(Math.abs(inverse.outputs[0].rate-1)<1e-7);
}
assert.equal(data.defaultRecipes.Desc_IronPlateReinforced_C,'Recipe_IronPlateReinforced_C');
assert.deepEqual([...A.demand({inputs:[],outputs:[{id:'Desc_IronPlateReinforced_C',rate:5}]},data).requirements],[['Desc_OreIron_C',60]]);
for(const recipe of ['Recipe_Concrete_C','Recipe_ModularFrame_C','Recipe_Motor_C','Recipe_CircuitBoard_C','Recipe_SpaceElevatorPart_1_C']){
 const id=data.recipes[recipe].outputs[0].id,flows={inputs:[],outputs:[{id,rate:.1}]};if(A.layoutLimit(flows,data)){assert.throws(()=>A.calculate(flows,data,{size:80}),/chaîne complète nécessite/);}else{const result=A.calculate(flows,data,{size:80});assert.ok(result.objects.some(o=>o.recipe===recipe));assert.ok(result.required.length);}
}
console.log('PASS: 120 catalog-exact solid recipes, 75 products, standard defaults, inverse flow calculations, new chains and unchanged 60 ore → 5 reinforced plates.');
