from pathlib import Path
import sys,json,tempfile
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_blueprint as n
rows=json.loads((root.parents[1]/'outputs/envelope62-scenes.json').read_text(encoding='utf8'))
for row in rows:
 scene=row['project'];assert d.envelope(scene)==row['parts']
 bp,info=p.build(scene);p.verify(bp)
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'wrap.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);p.verify(n.sbp_parse.parseBlueprint(str(path)))
print('PASS: eight roof forms/toggles, exact JS/Python parity, native builds and binary roundtrips. No game writes.')
