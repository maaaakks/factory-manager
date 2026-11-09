"""Modular workshop generation -> native graph -> binary roundtrip; no game writes."""
import copy,json,sys,tempfile,os
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_project as p,native_blueprint as n
scenes=json.loads(Path(os.environ.get('SUBZONE_SCENES',str(root/'data/subzone-scenes.json'))).read_text(encoding='utf-8'))
for scene in scenes:
 before=copy.deepcopy(scene);bp,info=p.build(scene);assert scene==before;p.verify(bp)
 original={o['id'] for o in scene['objects'] if o['type']!='lift'};edges={}
 for l in info['transportPreview']['links']:
  if l['kind']=='power':continue
  assert l.get('physicalRoute');edges.setdefault(l['from'],[]).append(l['to'])
 for l in scene['links']:
  if l['kind']=='power':continue
  seen=set();pending=[l['from']]
  while pending:
   oid=pending.pop()
   if oid in seen:continue
   seen.add(oid)
   if oid!=l['from'] and oid in original:continue
   pending.extend(edges.get(oid,[]))
  assert l['to'] in seen, l
 if scene['generation']['storeyMode']!='vertical':
  assert all(o['z']+o['h']<=8 for o in info['transportPreview']['objects'] if o['type']=='lift'),'Local crossings must stay below machine roofs'
 with tempfile.TemporaryDirectory(dir=root/'data') as tmp:
  file=Path(tmp)/'zones.sbp';n.sbp_parse.resaveBlueprint(str(file),bp);p.verify(n.sbp_parse.parseBlueprint(str(file)))
 print(scene['flows']['outputs'][0]['id'],scene['generation']['storeyMode'],info['belts'],info['lifts'],flush=True)
print('PASS: all modular networks, unchanged plans, physical continuity, low local crossings and binary roundtrip; no in-game validation.')

