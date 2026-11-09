import copy,json,math,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_compact as c,native_project as p,native_blueprint as n
from native_connected import prop
project=c.proposal();before=copy.deepcopy(project);bp,stats=p.build(project)
assert project==before
assert stats['objects']==65 and stats['belts']==54 and stats['lifts']==21 and stats['wires']==24 and stats['powerMW']==75.88
assert stats['foundations']==16 and stats['frames']==32
assert len([o for o in project['objects'] if o['type'] in p.MACHINES])==16
assert len([o for o in project['objects'] if o['type']=='smelter'])==4
assert len([o for o in project['objects'] if o['recipe']=='Recipe_IronPlate_C' and o['clock']==.75])==4
assert len([o for o in project['objects'] if o['recipe']=='Recipe_Screw_C' and o['clock']==.75])==4
assert all(l['kind']!='planned' for l in project['links'])
assert all(l.get('native') for l in project['links'] if l['kind']=='belt')
assert len([o for o in project['objects'] if o['type']=='storage'])==1
assert [f['z'] for f in project['floors']]==[0,10.8,18.8]
assert [f['profile'] for f in project['floors']]==['solid','frame','frame']
assert sorted(set(l['rate'] for l in project['links'] if l.get('item')=='Desc_IronPlateReinforced_C'))==[5,10]
c.verify(bp,project)
bad=copy.deepcopy(bp)
lift=next((h,o) for h,o in zip(bad[2],bad[3]) if isinstance(h,n.sav_parse.ActorHeader) and 'ConveyorLift' in h.typePath)
for row in prop(lift[1],'mTopTransform')[0]:
 if row[0]=='Rotation':row[1]=c.mul(c.q(180),row[1])
try:c.verify(bad,project);raise AssertionError('Reversed head accepted')
except ValueError:pass
with tempfile.TemporaryDirectory(dir=n.ROOT/'data') as tmp:
 receipt=p.save(project,'SANDBOX',tmp);c.verify(n.sbp_parse.parseBlueprint(receipt['files'][0]['path']),project)
 assert receipt['verified']['profile']==c.PROFILE
 for file in receipt['files']:assert Path(file['path']).is_file()
 # Real current-plan edits: changed name/color, translated full module scene.
 changed=copy.deepcopy(project);changed['name']='Renommé';changed['appearance']={'enabled':True,'color':'#000000'};p.save(changed,'SANDBOX',tmp)
 changed=copy.deepcopy(project);changed['size']=40
 for o in changed['objects']:o['x']+=4;o['y']+=4
 p.build(changed)
 for number,change in enumerate([lambda x:x['objects'][0].update(x=x['objects'][0]['x']+.5),lambda x:x['objects'][0].update(clock=.5),lambda x:x['objects'][0].update(x=-1),lambda x:x['objects'][0]['native'].update(prototype=999),lambda x:x['links'][0].update(rate=1000),lambda x:x['floors'][1].update(profile='solid'),lambda x:x['objects'][0].update(x=float('nan'))]):
  broken=copy.deepcopy(project);change(broken)
  try:p.build(broken);raise AssertionError('Invalid compact scene accepted '+str(number))
  except (p.ExportError,ValueError):pass
print('PASS: native pair reuse, 16 machines, 120 iron -> 10 reinforced plates in storage, balanced ports/rates, 54 belts + 21 lifts + 24 wires, 75.88 MW, hard-body and belt-crossing checks, binary roundtrip, current project color/name/translation, malformed/stale geometry/solid floors rejected; no game-folder writes')
