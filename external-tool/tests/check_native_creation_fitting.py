import sys,json,copy
from pathlib import Path
sys.path.insert(0,sys.argv[1]);import native_design as d,native_project as p,native_blueprint as n
rows=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
def close(a,b):
 if isinstance(a,(int,float))and not isinstance(a,bool):assert abs(a-b)<1e-7,(a,b)
 elif isinstance(a,list):
  assert len(a)==len(b)
  for x,y in zip(a,b):close(x,y)
 elif isinstance(a,dict):
  assert a.keys()==b.keys()
  for k in a:close(a[k],b[k])
 else:assert a==b,(a,b)
for row in rows:
 project=row['project'];before=copy.deepcopy(project);close(d.envelope(project),row['parts']);assert project==before
 for f,cells in zip(project['floors'],row['floors']):assert sorted(d.floor_cells(project,f))==[tuple(c)for c in cells]
bad=copy.deepcopy(rows[0]['project']);bad['design']['studyFloors']=[dict(z=0,cells=[[99,0]])]
try:d.settings(bad['design']);raise AssertionError('invalid cells accepted')
except p.ExportError:pass
print('PASS: JS/Python geometry and floor parity for 16 fitted projects; malformed floors rejected.')
# Native binary smoke test uses only local output files, never a game directory.
project=rows[0]['project'];bp,info=p.build(project);dest=Path(sys.argv[2]).parent/'fitted-proof.sbp';n.sbp_parse.resaveBlueprint(str(dest),bp);p.verify(n.sbp_parse.parseBlueprint(str(dest)))
print('PASS: fitted native blueprint built and binary re-read.')
