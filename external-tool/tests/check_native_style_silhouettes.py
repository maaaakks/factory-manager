from pathlib import Path
import json,subprocess,sys,tempfile,copy
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_project as p,native_blueprint as n,native_design as d
script="""const M=require('./dist/workshop-model.js'),A=require('./dist/workshop-assist.js'),D=require('./dist/workshop-design.js'),data=require('./dist/planner-data.json');const flows={inputs:[{id:'Desc_OreCopper_C',rate:60}],outputs:[{id:'Desc_CopperIngot_C',rate:60}]},generation=D.generation({priority:'architecture',envelopeStyle:'campus',storeyMode:'single',layoutStyle:'compact'}),r=A.calculate(flows,data,{size:40,physical:true,generation}),p={...M.fresh('single-storey'),name:'Single-storey test',size:40,objects:[...r.objects,...r.logistics],links:r.links,flows,floors:r.floors,structure:r.structure,generation,design:D.preset('campus',{packs:['concrete','metal','glass']})};process.stdout.write(JSON.stringify(M.read(p)));"""
project=json.loads(subprocess.run(['node','-e',script],cwd=root,encoding='utf-8',capture_output=True,check=True).stdout);before=copy.deepcopy(project)
bp,info=p.build(project);assert project==before;assert info['powerMW']==8;assert info['belts']>=6;assert info['lifts']>0
assert info['architecture']['windows']>0
js="const D=require('./dist/workshop-design.js');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>process.stdout.write(JSON.stringify(D.envelope(JSON.parse(s)))));"
preview=info['transportPreview'];actual=json.loads(subprocess.run(['node','-e',js],input=json.dumps(preview),cwd=root,encoding='utf-8',capture_output=True,check=True).stdout)
expected=d.envelope(preview)
assert actual==expected;assert len(actual)==info['architecture']['total']
with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
 path=Path(tmp)/'copper.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);p.verify(n.sbp_parse.parseBlueprint(str(path)))
print('PASS: architecture-first single-storey 60 copper ore -> 60 ingots, real native ports, separate input/output rails, overhead lifts, JS/native exported envelope parity, binary roundtrip and source preservation')


