from pathlib import Path
import json,sys,subprocess,tempfile,copy,hashlib
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_project as p,native_blueprint as n,native_design as d,native_compact as c,m05_architecture as m
script="""const D=require('./dist/workshop-design.js'),M=require('./dist/workshop-model.js');const rows=[];for(const variant of [1,3,5,6]){const p={...M.fresh('m05'),size:120,depth:80,height:48,objects:[],design:D.preset('m05',{packs:['concrete','metal','glass']},variant)};rows.push({p,layout:D.M05.layout(p),parts:D.envelope(p),floors:D.floorCells(p,{z:0})});}process.stdout.write(JSON.stringify(rows));"""
rows=json.loads(subprocess.run(['node','-e',script],cwd=root,capture_output=True,encoding='utf8',check=True).stdout)
for row in rows:
 assert m.layout(row['p'])==row['layout'];assert d.envelope(row['p'])==row['parts'];assert [list(x)for x in d.floor_cells(row['p'],{'z':0})]==row['floors']
for name,entry in m.DATA['modules'].items():assert hashlib.sha256((root/'data/m05'/f'{name}.sbp').read_bytes()).hexdigest()==entry['sha256']
for variant in [1,2,3,4,5,6]:
 scene=c.proposal(dict(size=120,depth=120,height=48,beltPolicy='auto'));before=copy.deepcopy(scene);scene['design']=rows[0]['p']['design'].copy();scene['design']['variant']=variant
 bp,info=c.build_project(scene);c.verify(bp,scene);assert info['architecture']['modules']==9;assert info['architecture']['wires']>200
 for key in ['objects','links','floors','flows']:assert scene[key]==before[key],key
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'m05.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);c.verify(n.sbp_parse.parseBlueprint(str(path)),scene)
 if variant==5:
  (root.parents[1]/'outputs/m05-56-production.factory-blueprint.json').write_text(json.dumps(scene,ensure_ascii=False),encoding='utf8')
  # A detached decorative wire must fail independently of the production network.
  broken=copy.deepcopy(bp);wire=next(o for h,o in reversed(list(zip(broken[2],broken[3])))if isinstance(h,n.sav_parse.ActorHeader)and 'PowerLine.'in h.typePath)
  from native_connected import prop
  next(value for key,value in prop(wire,'mWireInstances')[0][0]if key=='Locations')[0]+=100
  try:c.verify(broken,scene)
  except ValueError as error:assert 'détaché'in str(error)
  else:raise AssertionError('Detached source wire accepted')
 print('Native composition',variant,info['architecture'],'production:',info['belts'],'belts,',info['lifts'],'lifts')
print('PASS: JS/Python source poses, floors, hashes, native production preservation, real decorative wires and binary roundtrips. No game save writes.')
