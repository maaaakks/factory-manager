from pathlib import Path
import sys,json,subprocess,tempfile,copy,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_design as d,native_project as p,native_blueprint as n,native_compact as c
from native_assembly import rotate
from native_connected import prop
root=Path(__file__).resolve().parents[1]
base=dict(schemaVersion=2,kind='factory-tools-paper-blueprint',id='patterns',name='Patterns',size=48,objects=[dict(id='machine',type='constructor',name='Test',x=24,y=24,z=1,w=8,d=10,h=6,rotation=0,recipe='Recipe_IronPlate_C',clock=1)],links=[],buffer=[],floors=[dict(z=0,thickness=1,material='concrete')],flows=dict(inputs=[],outputs=[]))
scenes=[]
for size in [32,40,48]:
 for layout in ['auto','central','pair','quartet','triple','band','ring']:
  for contour in ['rectangle','stepped']:
   s=copy.deepcopy(base);s['size']=size;s['objects'][0].update(x=size/2,y=size/2);s['design']=dict(enabled=True,style='ficsit',packs=['concrete','metal','glass'],roof=True,roofSeed=14,roofLayout=layout,roofStyle='skylights',roofForm='auto',wallDecoration='lattice',footprint=contour);scenes.append(s)
gap=copy.deepcopy(base);gap['size']=32;gap['objects'][0].update(x=4,y=10,z=8);gap['floors'].append(dict(z=7,thickness=1,material='concrete'));gap['design']=dict(enabled=True,wallDecoration='frames');scenes.append(gap)
for height in [2,10]:
 s=copy.deepcopy(base);s['design']=dict(enabled=True,entrance='front');s['links']=[dict(kind='belt',**{'from':'outside','to':'inside'},physicalRoute=[dict(x=0,y=2,z=height),dict(x=48,y=2,z=height)])];scenes.append(s)
script="const D=require('./dist/workshop-design.js');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>process.stdout.write(JSON.stringify(JSON.parse(s).map(p=>D.envelope(p)))));"
expected=json.loads(subprocess.run(['node','-e',script],input=json.dumps(scenes),encoding='utf-8',cwd=root,capture_output=True,check=True).stdout)
for scene,parts in zip(scenes,expected):assert d.envelope(scene)==parts,('Preview/native parity',scene['size'],scene['design'])
for scene in [scenes[0],scenes[1],gap]:
 bp,details=p.build(scene);beams=[(h,o)for h,o in zip(bp[2],bp[3])if isinstance(h,n.sav_parse.ActorHeader)and'/Build_Beam'in h.typePath]
 assert len(beams)>0 and details['architecture']['beams']==len(beams)
 parts=[part for part in d.envelope(scene)if part['component']=='beam']
 for(h,o),part in zip(beams,parts):
  endpoint=[a+b for a,b in zip(h.position,rotate(h.rotation,[prop(o,'mLength'),0,0]))];wanted=[(part['end'][0]-scene['size']/2)*100,(part['end'][1]-scene['size']/2)*100,part['end'][2]*100]
  assert math.dist(endpoint,wanted)<.00001,'Beam native orientation/length mismatches preview'
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'beams.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);p.verify(n.sbp_parse.parseBlueprint(str(path)))
for size in [40,48]:
 scene=c.proposal(dict(size=size,beltPolicy='auto'));margin=(size-32)/2
 assert scene['layoutInfo']['edgeMargin']==margin
 assert min(o['x']-o['w']/2 for o in scene['objects'])>=margin-.01
 scene['design']=dict(enabled=True,style='concrete',packs=['concrete','metal','glass'],roof=True,roofStyle='skylights',roofLayout='central',wallDecoration='braces')
 bp,details=c.build_project(scene);assert details['architecture']['beams']>0
print(f'PASS: {len(scenes)} JS/native architecture parity cases, native beam endpoints/length/rotation, binary roundtrips, 5x5/6x6 centered compact export')

