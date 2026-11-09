from pathlib import Path
import json,subprocess,sys,tempfile,copy
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_blueprint as n,native_compact as c
script="""const D=require('./dist/workshop-design.js');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const base=JSON.parse(s),rows=[];for(const family of Object.keys(D.PRESETS).filter(id=>id!=='m05'&&!D.PRESETS[id].nativeStudy))for(const variant of [1,3,6]){const p={...base,design:D.preset(family,{packs:['concrete','metal','glass']},variant)};rows.push({project:p,parts:D.envelope(p),upperCells:D.floorCells(p,{z:11,thickness:1}).sort((a,b)=>a[0]-b[0]||a[1]-b[1])});}process.stdout.write(JSON.stringify(rows));});"""
base=dict(schemaVersion=2,kind='factory-tools-paper-blueprint',id='family-test',name='Family test',size=48,objects=[dict(id='test',type='constructor',name='Test',x=24,y=24,z=1,w=8,d=10,h=6,rotation=0,recipe='Recipe_IronPlate_C',clock=1)],links=[],buffer=[],floors=[dict(z=0,thickness=1,material='concrete')],flows=dict(inputs=[],outputs=[]))
rows=json.loads(subprocess.run(['node','-e',script],input=json.dumps(base),cwd=root,capture_output=True,encoding='utf-8',check=True).stdout)
for row in rows:
 project=row['project'];parts=d.envelope(project);assert parts==row['parts'],('Native parity',project['design']['family'],project['design']['variant'])
 assert [list(cell)for cell in d.floor_cells(project,{'z':11,'thickness':1})]==row['upperCells'],'JS/native floor mask'
 # Every family and all three entrance treatments pass a binary roundtrip.
 bp,info=p.build(project)
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'style.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);p.verify(n.sbp_parse.parseBlueprint(str(path)))
for variant in [1,3,6]:
 scene=c.proposal(dict(size=48,beltPolicy='auto'));before=copy.deepcopy(scene)
 scene['design']=next(row['project']['design']for row in rows if row['project']['design']['family']=='warehouse'and row['project']['design']['variant']==variant)
 bp,info=c.build_project(scene)
 assert info['frames']==sum(len(d.floor_cells(scene,f))for f in scene['floors']if f['profile']=='frame')
 for key in ['objects','links','floors','flows']:assert scene[key]==before[key],key
 assert info['architecture']['beams']>50;assert any(part['name']=='Entrée piétonne · linteau'for part in d.envelope(scene))
print(f'PASS: {len(rows)} family/variant JS-native parity scenes and binary roundtrips; three warehouse variants on calibrated 120 ore -> 10 reinforced plates preserve production and native transport')

try:c.proposal(dict(size=32,priority='architecture',layoutStyle='balanced'))
except ValueError as error:assert '5 × 5'in str(error)
else:raise AssertionError('Architecture-first calibrated modules must reserve a margin')
scene=c.proposal(dict(size=40,priority='architecture'));assert scene['layoutInfo']['edgeMargin']==4
print('PASS: architecture-first calibrated core reserves 4 m; no game writes')
