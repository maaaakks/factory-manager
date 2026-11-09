from pathlib import Path
import sys,json,tempfile,copy
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_blueprint as n
rows=json.loads((root/'data/signature-test-scenes.json').read_text(encoding='utf-8'))
for row in rows:
 project=row['project'];before=copy.deepcopy(project);parts=d.envelope(project)
 if parts!=row['parts']:
  for i,(a,b)in enumerate(zip(parts,row['parts'])):
   if a!=b:print(i,a,b);break
  raise AssertionError(('Native parity',project['size'],project['design']['variant']))
 assert project==before
 assert [list(c)for c in d.floor_cells(project,{'z':11,'thickness':1})]==row['upperCells']
 bp,info=p.build(project)
 with tempfile.TemporaryDirectory(dir=Path(__file__).parent)as tmp:
  path=Path(tmp)/'signature.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);p.verify(n.sbp_parse.parseBlueprint(str(path)))
print(f'PASS: {len(rows)} signature preview/export parity scenes, floor masks, no mutation and native binary roundtrips. No game writes.')
