from pathlib import Path
import json,sys,tempfile
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_project as p,native_blueprint as n,native_design as d
paths=[root.parents[1]/'outputs'/f'simple57-{shape}-{storeys}.json'for shape in ['rectangle','elongated','exotic']for storeys in ['single','vertical']]
for path in paths:
 project=json.loads(path.read_text(encoding='utf8'));bp,info=p.build(project);p.verify(bp)
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  dest=Path(tmp)/'simple.sbp';n.sbp_parse.resaveBlueprint(str(dest),bp);p.verify(n.sbp_parse.parseBlueprint(str(dest)))
 assert info['belts']>0 and info['wires']==3 and info['powerMW']==8
 if project['generation']['shape']=='exotic':
  cx=(project['size']+15)//16*8;cy=(project.get('depth',project['size'])+15)//16*8
  assert all(pt['x']<cx+.001 or pt['y']>=cy-.001 for link in info['transportPreview']['links']for pt in link.get('physicalRoute',[]))
  assert len(d.floor_cells(project,project['floors'][0]))<project['size']*project.get('depth',project['size'])//64
 print(path.name,'PASS:',info['belts'],'belts,',info['lifts'],'lifts,',info['wires'],'wires; binary ports and floor mask checked')
print('PASS: six native layouts; horizontal and vertical transport, electrical connections, L courtyard routing and binary roundtrips. No game writes.')
