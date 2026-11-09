"""Expose solid recipes compatible with the workshop's calibrated machines."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def build():
 source=json.loads((root/'data/game_catalog.json').read_text(encoding='utf8'))
 old=json.loads((root/'dist/planner-data.json').read_text(encoding='utf8'))
 machines={'Build_SmelterMk1_C':'smelter','Build_ConstructorMk1_C':'constructor','Build_AssemblerMk1_C':'assembler'}
 recipes={}
 for key,row in source['recipes'].items():
  kind=next((machines[m]for m in row['producedIn']if m in machines),None)
  if not kind or len(row['outputs'])!=1 or not row['inputs']or row['seconds']<=0 or not all(i['solid']for i in row['inputs']+row['outputs']):continue
  recipes[key]={'type':kind,**row,'alternate':'alternate'in key.lower()or'alternative'in row['name'].lower()}
 preferred={'Recipe_IronPlate_C','Recipe_IronRod_C','Recipe_IngotIron_C','Recipe_Cable_C','Recipe_Wire_C','Recipe_IngotCopper_C','Recipe_Screw_C','Recipe_CopperSheet_C','Recipe_IronPlateReinforced_C','Recipe_Rotor_C','Recipe_Biomass_Leaves_C','Recipe_PowerCrystalShard_1_C','Recipe_Rubber_C'}
 products={r['outputs'][0]['id']for r in recipes.values()}
 defaults={item:min((key for key,r in recipes.items()if r['outputs'][0]['id']==item),key=lambda key:(key not in preferred,recipes[key]['alternate'],key))for item in sorted(products)}
 names={i['id']:i['name']for r in recipes.values()for i in r['inputs']+r['outputs']}
 result={'build':source['build'],'sourceSha256':source['sourceSha256'],'names':names,'recipes':recipes,'defaultRecipes':defaults,'power':old['power'],'powerSource':old['powerSource']}
 # Recipe calculation is independent of calibrated workshop placement.
 kinds={**machines,'Build_FoundryMk1_C':'foundry','Build_ManufacturerMk1_C':'manufacturer','Build_OilRefinery_C':'refinery','Build_Packager_C':'packager','Build_Blender_C':'blender','Build_HadronCollider_C':'accelerator','Build_Converter_C':'converter','Build_QuantumEncoder_C':'encoder'}
 labels={'smelter':'Fonderie','constructor':'Constructeur','assembler':'Assembleuse','foundry':'Forge','manufacturer':'Façonneuse','refinery':'Raffinerie','packager':'Conditionneur','blender':'Mélangeur','accelerator':'Accélérateur de particules','converter':'Convertisseur','encoder':'Encodeur quantique'}
 production={};units={}
 for key,row in source['recipes'].items():
  kind=next((kinds[m]for m in row['producedIn']if m in kinds),None)
  if not kind or not row['outputs']or row['seconds']<=0:continue
  r={'type':kind,**row,'alternate':'alternate'in key.lower()or'alternative'in row['name'].lower()}
  for side in ['inputs','outputs']:
   r[side]=[{**i,'amount':i['amount']/(1 if i['solid']else 1000)}for i in row[side]]
   for i in r[side]:names[i['id']]=i['name'];units[i['id']]='item'if i['solid']else'm³'
  production[key]=r
 raw={i for i in names if i.startswith('Desc_Ore')}|{'Desc_Stone_C','Desc_Coal_C','Desc_Sulfur_C','Desc_RawQuartz_C','Desc_LiquidOil_C','Desc_Water_C','Desc_NitrogenGas_C','Desc_SAM_C'}
 all_products={i['id']for r in production.values()for i in r['outputs']}-raw
 standard={}
 for item in sorted(all_products):
  candidates=[k for k,r in production.items()if any(i['id']==item for i in r['outputs'])]
  standard[item]=min(candidates,key=lambda k:('unpackage'in k.lower(),production[k]['alternate'],production[k]['outputs'][0]['id']!=item,k not in preferred,'residual'in k.lower(),k))
 assets=json.loads((root/'data/native-assets.json').read_text(encoding='utf8'))
 for asset,kind in kinds.items():
  mw=float(assets[asset].get('mPowerConsumption','0'));result['power'][kind]={'mw':mw,'exponent':1.321928,'variable':mw==0}
 result.update(productionRecipes=production,productionDefaults=standard,rawResources=sorted(raw),itemUnits=units,machineNames=labels)
 (root/'dist/planner-data.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf8')
 return result
if __name__=='__main__':
 data=build();print(f"Planner catalog: {len(data['recipes'])} recipes, {len(data['defaultRecipes'])} products, {len(data['names'])} resources.")
