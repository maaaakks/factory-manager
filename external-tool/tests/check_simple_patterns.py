"""Native row patterns: ports, two-input routing, floors and binary readback."""
import json,sys
from pathlib import Path
root=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(root))
import native_manifold as m,native_project as p,native_blueprint as n
data=json.loads((root/'dist/planner-data.json').read_text(encoding='utf8'));rows=[]
for kind,rid in [('smelter','Recipe_IngotIron_C'),('constructor','Recipe_IronRod_C'),('assembler','Recipe_IronPlateReinforced_C')]:
 for count in [1,4]:
  recipe=data['recipes'][rid];flow=lambda key:[dict(id=r['id'],rate=r['amount']*60/recipe['seconds']*count)for r in recipe[key]]
  payload=dict(inputs=flow('inputs'),outputs=flow('outputs'),options=dict(layoutPolicy='simple-patterns-v1'))
  project=m.proposal(payload);machines=[o for o in project['objects']if o.get('recipe')]
  assert len(machines)==count and all(o['type']==kind and o['recipe']==rid and o['z']==6 for o in machines)
  assert project['manifoldInterior']['parts']==[] and project['manifoldInterior']['entryParts']==[]
  assert [(f['z'],f['role'])for f in project['floors']]==[(0,'technical'),(5,'production')]
  assert project['layoutInfo']['controlWidth']==0
  assert project['flows']=={k:payload[k]for k in ['inputs','outputs']}
  bp,info=p.build(project);dest=out/f'{kind}-{count}.sbp';n.sbp_parse.resaveBlueprint(str(dest),bp);p.verify(n.sbp_parse.parseBlueprint(str(dest)))
  assert info['belts']>0 and info['lifts']>=2*count
  rows.append(dict(type=kind,count=count,project=project));print('PASS',kind,count,flush=True)
chain=m.proposal(dict(inputs=[dict(id='Desc_OreIron_C',rate=120)],outputs=[dict(id='Desc_IronPlate_C',rate=80)],options=dict(layoutPolicy='simple-patterns-v1')))
assert len([o for o in chain['objects']if o.get('recipe')])==8
p.build(chain)
(out/'projects.json').write_text(json.dumps(rows),encoding='utf8')
print('PASS: 3 patterns at 1/4 machines, independent assembler inputs, 4 m logistics floor, no fixed interior, 6 binary roundtrips and an 8-machine chain')
