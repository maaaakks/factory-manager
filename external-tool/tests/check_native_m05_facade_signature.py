from pathlib import Path
import json,sys,tempfile,copy
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_blueprint as n,native_compact as c
rows=json.loads((root.parents[1]/'outputs/facade61-scenes.json').read_text(encoding='utf8'));built=0
for row in rows:
 scene=row['project'];before=copy.deepcopy(scene);assert d.envelope(scene)==row['parts'],(scene['size'],scene['design']['seed'],scene['design']['entrance'])
 if row.get('geometryOnly'):continue
 bp,info=p.build(scene);built+=1;assert scene==before
 if scene.get('nativeProfile'):c.verify(bp,scene);assert info['belts']==54 and info['lifts']==21
 else:p.verify(bp)
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'facade.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);parsed=n.sbp_parse.parseBlueprint(str(path))
  if scene.get('nativeProfile'):c.verify(parsed,scene)
  else:p.verify(parsed)
print(f'PASS: {len(rows)} exact JS/Python facade scenes, {built} native builds and binary roundtrips, source garage/glass/roof actors, native H beams, independent painting, functional 4x4 transport unchanged. No game writes.')
