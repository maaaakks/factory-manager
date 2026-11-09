from pathlib import Path
import json,sys,copy,tempfile
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_blueprint as n,native_compact as c
rows=json.loads((root.parents[1]/'outputs/kit59-scenes.json').read_text(encoding='utf8'))
for row in rows:
 scene=row['project'];before=copy.deepcopy(scene);actual=d.envelope(scene);assert actual==row['parts'],scene['design']['family'];bp,info=p.build(scene);p.verify(bp);assert scene==before
 if scene['design']['family']=='m05':assert any('Wall_Concrete_8x4.'in h.typePath for h in bp[2]if isinstance(h,n.sav_parse.ActorHeader))
 if scene['design']['family']=='m05-kit':
  fans=[h for h in bp[2]if isinstance(h,n.sav_parse.ActorHeader)and 'LargeFan' in h.typePath];assert len(fans)==sum(q['asset']=='LargeFan'for q in actual)
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'kit.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);p.verify(n.sbp_parse.parseBlueprint(str(path)))
print('PASS: nine kits and painted original M05; exact JS/native parts, source fans, real material classes, source preservation and binary roundtrips')
scene=json.loads((root.parents[1]/'outputs/reflow59-4x4-3.factory-blueprint.json').read_text(encoding='utf8'));bp,info=p.build(scene);c.verify(bp,scene);assert info['belts']==54 and info['lifts']==21
assert scene['size']==32 and scene.get('depth',scene['size'])==32 and len(scene['floors'])==3 and scene['flows']['outputs'][0]['rate']==5
with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
 path=Path(tmp)/'reflow.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);c.verify(n.sbp_parse.parseBlueprint(str(path)),scene)
print('PASS: 4x4 three-storey 60 iron -> 5 reinforced plates; 54 belts, 21 lifts, native verification and binary roundtrip. No game writes.')

