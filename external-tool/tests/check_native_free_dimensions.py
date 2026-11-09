from pathlib import Path
import sys,json,subprocess,tempfile,copy,struct
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_blueprint as n,native_compact as c
from blueprint_dimensions import dimensions
script="""const M=require('./dist/workshop-model.js'),D=require('./dist/workshop-design.js'),rows=[];for(const [size,depth,height]of [[96,48,96],[48,96,128],[96,96,160]])for(const fit of ['plot','occupied'])for(const facadeForm of ['flat','warehouse','gallery','terraces']){const p={...M.fresh('free'),size,depth,height,objects:[{id:'m',type:'constructor',name:'Test',x:size/2,y:depth/2,z:73,w:8,d:10,h:6,rotation:0,recipe:'Recipe_IronPlate_C',clock:1}],floors:[{z:0,thickness:1,material:'concrete'},{z:72,thickness:1,material:'concrete'}],design:{...D.preset('warehouse',{packs:['concrete','metal','glass']}),fit,facadeForm,roofForm:'monitor'}};rows.push({project:p,parts:D.envelope(p),floor:D.floorCells(p,p.floors[1]).sort((a,b)=>a[0]-b[0]||a[1]-b[1])});}process.stdout.write(JSON.stringify(rows));"""
rows=json.loads(subprocess.run(['node','-e',script],cwd=root,encoding='utf-8',capture_output=True,check=True).stdout)
for row in rows:
 project=row['project'];assert d.envelope(project)==row['parts'],('geometry',dimensions(project),project['design']['fit'],project['design']['facadeForm'])
 assert [list(k)for k in d.floor_cells(project,project['floors'][1])]==row['floor']
 bp,info=p.build(project);assert info['experimentalXL']
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'free.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);checked=n.sbp_parse.parseBlueprint(str(path));p.verify(checked)
  assert list(struct.unpack_from('<III',path.read_bytes(),12))==[v//8 for v in dimensions(project)]
  assert checked[1][0]==[v//8 for v in dimensions(project)]
for size,depth,height in [(96,48,96),(48,96,128)]:
 project=c.proposal(dict(size=size,depth=depth,height=height,priority='architecture'));before=copy.deepcopy(project);bp,info=c.build_project(project);assert project==before;assert info['belts']==54 and info['lifts']==21
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'pairs.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);c.verify(n.sbp_parse.parseBlueprint(str(path)),project)
cube=copy.deepcopy(rows[0]['project']);cube.update(size=96,depth=96,height=96);cube['design'].update(fit='occupied',facadeForm='flat',footprint='rectangle');cube['floors']=cube['floors'][:1]
prototype=cube['objects'][0];cube['objects']=[dict(prototype,id=f'cube-{i}-{j}',x=x,y=y,z=1)for i,x in enumerate([12,36,60,84])for j,y in enumerate([12,36])]
bp,info=p.build(cube);assert info['foundations']==72
with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
 path=Path(tmp)/'cube.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);checked=n.sbp_parse.parseBlueprint(str(path));p.verify(checked);assert checked[1][0]==12
 assert struct.unpack_from('<III',path.read_bytes(),12)==(12,12,12)
cube['design']['enabled']=False;assert len(d.floor_cells(cube,cube['floors'][0]))==72,'Occupied floors remain without wall decoration'
print(f'PASS: {len(rows)} rectangular/tall JS-native architecture and floor parity scenes, independent binary XYZ roundtrips, two rectangular calibrated native networks and a 12x6 building on a 12x12 plot; no game writes')

