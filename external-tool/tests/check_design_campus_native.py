from pathlib import Path
import sys,json,math
S=Path(sys.argv[1]);B=Path(sys.argv[2]);R=Path(sys.argv[3])if len(sys.argv)>3 else S;sys.path.insert(0,str(S));sys.path.append(str(R))
import native_project as p,native_design as d,native_blueprint as n
from native_connected import prop
def equal(a,b):
 if isinstance(a,(int,float))and not isinstance(a,bool):assert isinstance(b,(int,float))and abs(a-b)<1e-7,(a,b)
 elif isinstance(a,list):
  assert len(a)==len(b),(len(a),len(b))
  for x,y in zip(a,b):equal(x,y)
 elif isinstance(a,dict):
  assert a.keys()==b.keys(),(a.keys(),b.keys())
  for k in a:equal(a[k],b[k])
 else:assert a==b,(a,b)
for row in json.loads((B/'parity.json').read_text(encoding='utf-8')):
 equal(d.envelope(row['project']),row['parts'])
 for floor,cells in zip(row['project']['floors'],row['floors']):assert sorted(d.floor_cells(row['project'],floor))==sorted(map(tuple,cells))
print('PASS Python/JS parity: 27 architectural configurations and all slab openings.',flush=True)
for family in ['aurore','noyau']:
 project=json.loads((B/(family+'.json')).read_text(encoding='utf-8'));bp,info=p.build(project)
 dest=B/(family+'-test.sbp');n.sbp_parse.resaveBlueprint(str(dest),bp);r=n.sbp_parse.parseBlueprint(str(dest));p.verify(r)
 signs=[(h,o)for h,o in zip(r[2],r[3])if isinstance(h,n.sav_parse.ActorHeader)and 'StandaloneWidgetSign'in h.typePath]
 assert len(signs)==info['architecture']['signPanels'] and len(signs)>0
 for h,o in signs:
  assert prop(o,'mEmissive')==3 and prop(o,'mBackgroundColor')is not None
  assert prop(o,'mSoftActivePrefabLayout')is not None
 assert info['objects']==0 and info['belts']==0 and info['lifts']==0
 print('PASS native',family,info['foundations'],'foundations',len(signs),'native emissive signs;',info['architecture']['total'],'architectural parts; binary re-read.',flush=True)
