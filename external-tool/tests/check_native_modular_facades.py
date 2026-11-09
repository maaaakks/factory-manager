from pathlib import Path
import sys,json,subprocess,tempfile,math
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_blueprint as n
script="""const M=require('./dist/workshop-model.js'),D=require('./dist/workshop-design.js'),base={...M.fresh('modular-test'),size:48,objects:[{id:'m',type:'constructor',name:'Test',x:24,y:24,z:22,w:8,d:10,h:6,rotation:0,recipe:'Recipe_IronPlate_C',clock:1}],floors:[{z:0,thickness:1,material:'concrete'},{z:21,thickness:1,material:'concrete'}]},rows=[];for(const facadeForm of ['warehouse','gallery','terraces'])for(const roofForm of ['flat','monitor','sawtooth']){const p={...base,design:{...D.preset('warehouse',{packs:['concrete','metal','glass']}),facadeForm,roofForm}};rows.push({project:p,parts:D.envelope(p)});}process.stdout.write(JSON.stringify(rows));"""
rows=json.loads(subprocess.run(['node','-e',script],cwd=root,encoding='utf-8',capture_output=True,check=True).stdout)
for row in rows:
 project=row['project'];parts=d.envelope(project);assert parts==row['parts'],(project['design']['facadeForm'],project['design']['roofForm'])
 assert all(math.dist(q['start'],q['end'])<=16.000001 for q in parts if 'start'in q)
 bp,info=p.build(project)
 assert info['architecture']['total']==len(parts)
 assert any(h.typePath.endswith('Build_Wall_Window_8x4_05_C')for h in bp[2]if isinstance(h,n.sav_parse.ActorHeader)),'Use the M05 native window asset'
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'modular.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);p.verify(n.sbp_parse.parseBlueprint(str(path)))
print('PASS: nine tall JS/native modular geometry parity scenes and binary roundtrips, M05 window asset, legal beam lengths; no game writes')
