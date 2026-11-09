import copy,json,sys,tempfile,os
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_workcells as w,native_compact as c,native_project as p,native_blueprint as n
scenes=json.loads(Path(os.environ.get('WORKCELL_SCENES',str(root/'data/workcells-scenes.json'))).read_text(encoding='utf-8'))
for project in scenes:
 before=copy.deepcopy(project);bp,info=p.build(project);assert project==before
 assert info['lifts']==11 and info['belts']==20 and info['wires']==11
 assert len([o for o in project['objects']if o.get('recipe')])==8
 assert all(o['z']==1 for o in project['objects']if o.get('recipe'))
 # Topology is the contract: central raw distribution, elevated local collection,
 # return to the central manifold, then only processed components at assembly.
 objects={o['id']:o for o in project['objects']}
 for group in ['smelting','plates','rods','screws']:
  local=[o for o in objects.values()if o.get('native',{}).get('module')==group]
  split=next(o for o in local if o['type']=='splitter');merge=next(o for o in local if o['type']=='merger')
  assert abs(split['x']-project['size']/2+8)<.01 and abs(split['x']-merge['x'])<.01
  assert abs(split['y']-merge['y'])<.01 and merge['z']>split['z']
 assembler=next(o for o in objects.values()if o['type']=='assembler')
 assert {l.get('item')for l in project['links']if l['kind']=='belt'and l['to']==assembler['id']}=={'Desc_IronPlate_C','Desc_IronScrew_C'}
 for o in objects.values():
  if o['type']=='constructor':assert o['native']['module']in ['plates','rods','screws']
 reference=n.sbp_parse.parseBlueprint(str(root/'data/workcell-iron-reference.sbp'))
 measured=sorted((round(h.position[0]/100,4),round(h.position[1]/100,4))for h in reference[2]if isinstance(h,n.sav_parse.ActorHeader)and any(kind in h.typePath for kind in ['SmelterMk1.','ConstructorMk1.','AssemblerMk1.']))
 actual=sorted((round(o['x']-project['size']/2,4),round(o['y']-project.get('depth',project['size'])/2,4))for o in objects.values()if o.get('recipe'))
 assert measured==actual,'Reference layout was replaced by generic packing'
 c.balance(copy.deepcopy(project));c.verify(bp,project)
 with tempfile.TemporaryDirectory(dir=Path(os.environ.get('WORKCELL_TMP',str(root/'data'))))as temp:
  out=Path(temp)/'cells.sbp';n.sbp_parse.resaveBlueprint(str(out),bp);c.verify(n.sbp_parse.parseBlueprint(str(out)),project)
 print('PASS:',project['size'],'m ground-floor cells, flows, native ports, collision checks, power, binary roundtrip',flush=True)
for rate in [1,2.5,5]:
 project=w.proposal({'outputRate':rate});bp,info=p.build(project);assert project['flows']['inputs'][0]['rate']==12*rate;c.verify(bp,project)
ingots=w.proposal({'inputItem':'Desc_IronIngot_C'});bp,info=p.build(ingots);c.verify(bp,ingots);assert sum(o.get('recipe') is not None for o in ingots['objects'])==6
bad=copy.deepcopy(scenes[0]);next(o for o in bad['objects']if o['type']=='constructor')['x']+=1
try:p.build(bad);raise AssertionError('Detached calibrated module accepted')
except p.ExportError:pass
print('PASS: scaled rates, detached modules refused; no game writes.')
