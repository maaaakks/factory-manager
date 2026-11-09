import json,sys,tempfile,copy,os
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root));import native_project as p,native_compact as c,native_blueprint as n
rows=json.loads(Path(os.environ.get('FACTORY_SHAPE_SCENES',str(root/'data/layout-shape-scenes.json'))).read_text())
for scene in rows:
 before=copy.deepcopy(scene);bp,info=p.build(scene);assert scene==before
 with tempfile.TemporaryDirectory(dir=os.environ.get('FACTORY_SHAPE_TMP',str(root/'data')))as tmp:
  file=Path(tmp)/'layout.sbp';n.sbp_parse.resaveBlueprint(str(file),bp);c.verify(n.sbp_parse.parseBlueprint(str(file)),scene)
 assert info['lifts']in [8,11]
 c.balance(copy.deepcopy(scene));print(scene['generation']['shape'],scene['generation']['storeyMode'],info['belts'],info['lifts'],'PASS',flush=True)
print('PASS: 8 native graphs, physical ports/directions, collision checks, flow conservation, binary roundtrip; no game writes.')
