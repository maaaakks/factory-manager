from pathlib import Path
import sys,json,tempfile
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_blueprint as n
rows=json.loads((root.parents[1]/'outputs/support63-scenes.json').read_text(encoding='utf8'))
for row in rows:
 scene=row['project'];assert d.envelope(scene)==row['parts'],(scene['size'],scene['design']['seed'])
 bp,info=p.build(scene);p.verify(bp)
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'support.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);p.verify(n.sbp_parse.parseBlueprint(str(path)))
print('PASS: 18 one-floor compositions, exact JS/Python parity and native SBP roundtrips. No game writes.')
