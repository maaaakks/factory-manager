"""Both routing modes must produce valid native blueprints."""
import sys,json,tempfile
from pathlib import Path
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root))
import native_manifold as m,native_project as p,native_blueprint as n
D=json.loads((root/'dist/planner-data.json').read_text(encoding='utf8'))
for enabled in [False,True]:
 for kind,rid in [('smelter','Recipe_IngotIron_C'),('constructor','Recipe_IronRod_C'),('assembler','Recipe_IronPlateReinforced_C')]:
  for count in [1,4]:
   recipe=D['recipes'][rid];flow=lambda k:[dict(id=q['id'],rate=q['amount']*60/recipe['seconds']*count) for q in recipe[k]]
   project=m.proposal(dict(inputs=flow('inputs'),outputs=flow('outputs'),options=dict(layoutPolicy='simple-patterns-v1',logisticsFloor=enabled)))
   assert [f['z'] for f in project['floors']]==([0,5] if enabled else [0])
   assert all(o['z']==(6 if enabled else 1) for o in project['objects'] if o.get('recipe'))
   blueprint,info=p.build(project);p.verify(blueprint)
   with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
    target=Path(directory)/'pattern.sbp';n.sbp_parse.resaveBlueprint(str(target),blueprint);p.verify(n.sbp_parse.parseBlueprint(str(target)))
   print('PASS',enabled,kind,count,flush=True)

for enabled in [False,True]:
 project=m.proposal(dict(inputs=[dict(id='Desc_OreIron_C',rate=120)],outputs=[dict(id='Desc_IronPlate_C',rate=80)],options=dict(layoutPolicy='simple-patterns-v1',logisticsFloor=enabled)))
 p.build(project)
 print('PASS chain',enabled,flush=True)

