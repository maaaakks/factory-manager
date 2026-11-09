import sys,json,copy,math
from pathlib import Path
stage=Path(sys.argv[1]);live=Path(sys.argv[2]);base=Path(sys.argv[3]);sys.path.insert(0,str(stage));sys.path.append(str(live))
import native_project as p,native_compact as c,native_design as d,native_blueprint as n
from authored_living import floor_color
rows=json.loads((base/'living-tests.json').read_text(encoding='utf-8'))
def equal(a,b):
 if type(a)in[int,float]:assert abs(a-b)<1e-7,(a,b)
 elif isinstance(a,list):
  assert len(a)==len(b),(len(a),len(b))
  for x,y in zip(a,b):equal(x,y)
 elif isinstance(a,dict):
  assert a.keys()==b.keys()
  for k in a:equal(a[k],b[k])
 else:assert a==b,(a,b)
for row in rows:
 project=row['project'];before=copy.deepcopy(project);equal(d.envelope(project),row['parts']);assert project==before
 for f,cells in zip(project['floors'],row['floors']):assert sorted(d.floor_cells(project,f))==sorted(map(tuple,cells))
 for z,x,y,color in row['colors']:
  floor=next(f for f in project['floors']if f['z']==z);assert floor_color(project,floor,x*8+4,y*8+4,'#000000')==color
 for q in row['parts']:
  if q['component']=='beam':assert math.dist(q['start'],q['end'])<=16.00001
print('PASS: JS/Python shell, stairs, circulation, fixtures, floor cells and native colour parity for 10 scenes.',flush=True)
for family in['atlas','sylva']:
 project=next(r['project']for r in rows if r['project']['design']['family']==family and len(r['project']['floors'])==1);before=copy.deepcopy(project);bp,info=p.build(project);assert project==before
 assert info['belts']==23 and info['lifts']==13;lights=sum(q['asset']=='FloodlightWall'for q in d.envelope(project));supports=sum(q.get('livingCircuit')is not None and q['asset']=='PowerPoleWall'for q in d.envelope(project));assert info['architecture']['lights']==lights and info['architecture']['lightingFeed'];assert info['architecture']['lightWires']==lights+supports
 file=base/(family+'-verified.sbp');n.sbp_parse.resaveBlueprint(str(file),bp);read=n.sbp_parse.parseBlueprint(str(file));c.verify(read,project)
 actors=[h for h in read[2]if isinstance(h,n.sav_parse.ActorHeader)];stairs=[h for h in actors if 'CatwalkStairs.'in h.typePath];assert len(stairs)==(3 if family=='atlas'else 4)
 for a,b in zip(sorted(stairs,key=lambda h:h.position[2]),sorted(stairs,key=lambda h:h.position[2])[1:]):assert abs(b.position[2]-a.position[2]-400)<.01
 print('PASS native',family,': measured power-port endpoints, reciprocal circuit, 23 belts/13 lifts retained, correctly spaced stairs and binary re-read.',flush=True)
