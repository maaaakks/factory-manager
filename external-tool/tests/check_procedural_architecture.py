from pathlib import Path
import sys,json,subprocess,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_design as d,native_project as p,native_blueprint as n
root=Path(__file__).resolve().parents[1]
base=dict(schemaVersion=2,kind='factory-tools-paper-blueprint',id='roof-test',name='Roof test',size=32,objects=[dict(id='smelt',type='smelter',name='Fonderie',x=16,y=16,z=1,w=6,d=9,h=9,rotation=0,recipe='Recipe_IngotIron_C',clock=1)],links=[],buffer=[],floors=[dict(z=0,thickness=1,material='concrete')],flows=dict(inputs=[],outputs=[]))
scenes=[]
for size in [32,40,48]:
 for seed in [1,2,3,4]:
  scene=copy.deepcopy(base);scene['size']=size;scene['design']=dict(enabled=True,style='glass',packs=['concrete','metal','glass'],roof=True,roofSeed=seed,roofStyle='skylights',roofForm='auto');scenes.append(scene)
js="const D=require('./dist/workshop-design.js');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>process.stdout.write(JSON.stringify(JSON.parse(s).map(p=>D.envelope(p)))));"
expected=json.loads(subprocess.run(['node','-e',js],input=json.dumps(scenes),text=True,encoding="utf-8",cwd=root,check=True,capture_output=True).stdout)
assets=json.loads((root/'data/native-assets.json').read_text())
for scene,parts in zip(scenes,expected):
 assert d.envelope(scene)==parts,('Preview/native envelope parity',next(((a,b)for a,b in zip(d.envelope(scene),parts)if a!=b),('length',len(d.envelope(scene)),len(parts))))
 for part in parts:
  assert 'Build_'+part['asset']+'_C' in assets and 'Recipe_'+part['asset']+'_C' in assets
  assert 0<=part['z'] and part['z']+part['h']<=scene['size']
for form in ['flat','ridges']:
 scene=copy.deepcopy(scenes[1]);scene['design']['roofForm']=form
 bp,details=p.build(scene);assert details['architecture']['roofs']==16
 assert details['architecture']['walls']>0
 # Serialize/parse in a disposable local directory, never the game's Blueprint folder.
 import tempfile
 with tempfile.TemporaryDirectory(dir=root/"data")as temp:
  out=Path(temp)/'architecture.sbp';n.sbp_parse.resaveBlueprint(str(out),bp);roundtrip=n.sbp_parse.parseBlueprint(str(out));p.verify(roundtrip)
print('PASS: 12 preview/native envelope parity cases, native assets, flat/sloped architecture binary export and roundtrip')
