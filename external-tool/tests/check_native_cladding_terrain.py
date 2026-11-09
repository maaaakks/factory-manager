from pathlib import Path
import sys,json,tempfile
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_compact as c,native_blueprint as n
for name in['terrain64-copper.factory-blueprint.json','terrain64-native.factory-blueprint.json']:
 scene=json.loads((root.parents[1]/'outputs'/name).read_text(encoding='utf8'));bp,info=p.build(scene)
 if scene.get('nativeProfile'):c.verify(bp,scene);assert info['belts']==54 and info['lifts']==21
 else:p.verify(bp)
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'terrain.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);parsed=n.sbp_parse.parseBlueprint(str(path));c.verify(parsed,scene)if scene.get('nativeProfile')else p.verify(parsed)
print('PASS: airy 6x6 copper and protected native compact chain build and roundtrip. No game writes.')
