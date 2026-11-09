import sys,json,tempfile,os
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_blueprint as n,native_transport as t
rows=json.loads(Path(os.environ.get('FACTORY_FINISHES_REPORT',str(root/'data/finishes-test-scenes.json'))).read_text(encoding='utf8'))
for i,row in enumerate(rows):
 scene=row['project'];assert d.envelope(scene)==row['parts'],('envelope parity',i)
 assert [d.floor_cells(scene,f)for f in scene['floors']]==[[tuple(c)for c in f]for f in row['floors']],('floor parity',i)
 assert all(not f['holes']for f in t.floor_holes(scene,[[[-100,-100,0],[100,100,4000]]]))
 if scene['size']==40 and scene['design']['seed']==2:
  bp,info=p.build(scene);p.verify(bp);profile=scene['floors'][0]['profile'];headers=[h for h in bp[2]if hasattr(h,'typePath')]
  if profile=='factory':assert info['factoryFloors']>0 and not info['foundations']and any('Roof_Tar_01.'in h.typePath for h in headers)
  if profile=='frame':assert info['frames']>0 and not info['foundations']
  with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
   path=Path(tmp)/'finishes.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);p.verify(n.sbp_parse.parseBlueprint(str(path)))
print('PASS: 18 JS/Python envelope and floor parity checks; factory/frame/foundation exports and native binary roundtrips. No game writes.')

import native_compact as c
for profile in ['frame','factory','solid']:
 scene=c.proposal({'floorProfile':profile});bp,info=p.build(scene);c.verify(bp,scene);assert(info['belts'],info['lifts'],info['wires'])==(54,21,24);assert all(not f.get('holes')for f in scene['floors']);assert all(f['profile']==profile for f in scene['floors'])
print('PASS: compact factory/frame/foundation decks retain all 54 belts, 21 lifts and 24 wires, with no floor holes.')
