const assert=require('node:assert/strict'),A=require('../dist/workshop-assist'),d=require('../dist/planner-data.json');
const need=(id,rate=1,inputs=[])=>A.demand({inputs,outputs:[{id,rate}]},d),close=(a,b)=>assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);
for(const item of Object.keys(d.productionDefaults)){
 const result=need(item);for(const [id,rate]of result.requirements){assert.ok(!Object.hasOwn(d.productionDefaults,id),`Intermediate remained as input: ${id}`);assert.ok(Number.isFinite(rate)&&rate>0);}
}
const supercomputer=need('Desc_ComputerSuper_C');assert.deepEqual([...supercomputer.requirements.keys()].sort(),['Desc_OreCopper_C','Desc_OreGold_C','Desc_LiquidOil_C'].sort());close(supercomputer.requirements.get('Desc_OreCopper_C'),158);close(supercomputer.requirements.get('Desc_OreGold_C'),124.8);close(supercomputer.requirements.get('Desc_LiquidOil_C'),252);assert.ok([...supercomputer.work].some(([id])=>supercomputer.byOutput.get(id).type==='manufacturer'));
const cooling=need('Desc_CoolingSystem_C');for(const item of ['Desc_OreBauxite_C','Desc_Water_C','Desc_NitrogenGas_C','Desc_LiquidOil_C','Desc_Coal_C'])assert.ok(cooling.requirements.has(item));close(cooling.requirements.get('Desc_Water_C'),20);close(cooling.requirements.get('Desc_NitrogenGas_C'),25);close(cooling.surplus.find(r=>r.id==='Desc_Water_C').rate,5);
const plastic=need('Desc_Plastic_C');close(plastic.requirements.get('Desc_LiquidOil_C'),1.5);close(plastic.surplus.find(r=>r.id==='Desc_HeavyOilResidue_C').rate,.5);assert.equal(d.itemUnits.Desc_LiquidOil_C,'m³');
const motor=need('Desc_Motor_C');close(motor.requirements.get('Desc_OreIron_C'),31.5);close(motor.requirements.get('Desc_Coal_C'),9);assert.ok(!motor.requirements.has('Desc_SteelIngot_C'));
const imported=need('Desc_ComputerSuper_C',1,[{id:'Desc_Computer_C',rate:4}]);close(imported.requirements.get('Desc_Computer_C'),4);assert.ok(!imported.work.has('Desc_Computer_C'));
assert.match(A.layoutLimit({inputs:[],outputs:[{id:'Desc_ComputerSuper_C',rate:1}]},d),/Façonneuse.*Raffinerie|Raffinerie.*Façonneuse/);assert.equal(A.layoutLimit({inputs:[],outputs:[{id:'Desc_IronPlateReinforced_C',rate:5}]},d),null);
const old=need('Desc_IronPlateReinforced_C',5);assert.deepEqual([...old.requirements],[['Desc_OreIron_C',60]]);
console.log(`PASS: ${Object.keys(d.productionDefaults).length} complete recipe trees; supercomputers, cooling systems, steel, raw fluids in m³, co-products, explicit imports and calibrated layout limits.`);
