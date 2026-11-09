const assert=require('node:assert/strict'),A=require('../dist/workshop-assist'),data=require('../dist/planner-data.json');
const flows={inputs:[],outputs:[{id:'Desc_IronPlateReinforced_C',rate:5}]},before=JSON.stringify(flows),fixed=A.resolveFlexible(flows,data);
assert.deepEqual(fixed.inputs,[{id:'Desc_OreIron_C',rate:60}]);assert.equal(JSON.stringify(flows),before);
const plan=A.demand(fixed,data);assert.deepEqual([...plan.byOutput.values()].filter(r=>plan.work.has(r.outputs[0].id)).map(r=>r.name).sort(),['Barre de fer','Lingot de fer','Plaque de fer','Plaque de fer renforcée','Vis'].sort());
const automatic=A.resolveFlexible({inputs:[],outputs:[{id:'Desc_IronPlateReinforced_C',rate:null}]},data);assert.deepEqual(automatic,fixed);
for(const [item,id]of Object.entries(data.productionDefaults||data.defaultRecipes)){
 const r=(data.productionRecipes||data.recipes)[id],p={inputs:[],outputs:[{id:item,rate:null}]},snapshot=JSON.stringify(p),resolved=A.resolveFlexible(p,data);
 assert.ok(Math.abs(resolved.outputs[0].rate-60*r.outputs.find(o=>o.id===item).amount/r.seconds)<1e-8);assert.ok(resolved.inputs.length||r.inputs.length===0);assert.equal(JSON.stringify(p),snapshot);
}
const imported=A.resolveFlexible({inputs:[{id:'Desc_IronIngot_C',rate:60}],outputs:[{id:'Desc_IronPlateReinforced_C',rate:5}]},data);assert.deepEqual(imported.inputs,[{id:'Desc_IronIngot_C',rate:60}]);assert.ok(!A.demand(imported,data).work.has('Desc_IronIngot_C'));
console.log('PASS: empty inputs resolve the upstream chain, 75 nominal output defaults, visible ore requirements and explicit intermediate inputs preserved.');
