"""Full factory networks: no omitted links, unchanged layout, native roundtrip."""
import copy,json,sys,tempfile,math
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_project as p,native_blueprint as n,native_transport as t

boxes={'source':([-1550,-1550,100],[-1450,-1450,300]),'target':([1450,1450,100],[1550,1550,300]),'first':([-500,-2000,0],[-300,500,500]),'second':([500,-500,0],[700,2000,500])}
spans=p.route([-1500,-1500,200],[1500,1500,200],[1,0,0],[1,0,0],boxes,'source','target',(4000,4000,4000),{})
assert len(spans)>7,'Serpentine requires several turns rather than a single corridor'
assert all(not(lo[0]-35<pt[0]<hi[0]+35 and lo[1]-35<pt[1]<hi[1]+35)for name,(lo,hi)in boxes.items()if name in ['first','second']for pt in p.samples(spans))
print('PASS: multi-turn native spline through staggered obstacles',flush=True)

for file in sorted((root/'tests/fixtures/native-routing').glob('*.json')):
 scene=json.loads(file.read_text(encoding='utf8'));before=copy.deepcopy(scene);bp,info=p.build(scene);assert scene==before;p.verify(bp)
 prepared=t.prepare(scene);original={o['id']for o in prepared['objects']if o['type']!='lift'};edges={}
 for edge in info['transportPreview']['links']:
  if edge['kind']=='power':continue
  assert edge.get('physicalRoute');edges.setdefault(edge['from'],[]).append(edge['to'])
 for edge in prepared['links']:
  if edge['kind']=='power':continue
  seen=set();pending=[edge['from']]
  while pending:
   node=pending.pop()
   if node in seen:continue
   seen.add(node)
   if node!=edge['from'] and node in original:continue
   pending.extend(edges.get(node,[]))
  assert edge['to'] in seen,'Logical link was omitted or routed through another machine'
 if scene.get('design',{}).get('family')=='m05':
  assert info['architecture']['modules']>=6
  mx=(scene['size']%40)/2+24;my=(scene.get('depth',scene['size'])%40)/2+24
  assert all(mx<=pt['x']<=scene['size']-mx and my<=pt['y']<=scene.get('depth',scene['size'])-my and pt['z']<30.6 for edge in info['transportPreview']['links']if edge['kind']!='power'for pt in edge['physicalRoute'])
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  dest=Path(tmp)/'network.sbp';n.sbp_parse.resaveBlueprint(str(dest),bp);p.verify(n.sbp_parse.parseBlueprint(str(dest)))
 # Neither a caller nor the preview UI can corrupt the verified export cache.
 expected=copy.deepcopy(info);bp[1][0]=999;info['warnings'].append('mutated')
 cached_bp,cached_info=p.build(scene);assert cached_info==expected and cached_bp[1][0]!=999;p.verify(cached_bp)
 assert not expected['inGameValidated']
 print(file.name,'PASS',expected['belts'],'belts',expected['lifts'],'lifts; complete graph, preserved layout, binary roundtrip and isolated cache',flush=True)
