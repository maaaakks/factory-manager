from pathlib import Path
import json,copy,sys,subprocess,math,tempfile
root=Path(__file__).resolve().parents[1];base=root/'data';sys.path.insert(0,str(root))
import native_project as p,native_design as d,native_blueprint as n
original=json.loads((root/'dist/atlas-example.json').read_text(encoding='utf-8'))
projects=[]
for family in['atlas','lumen']:
 for width in[64,72,80,88,96]:
  for length in[48,56,64,72,80]:
   q=copy.deepcopy(original);q['size']=width;q['depth']=length;q['design'].update(family=family,nativeStudy=family);projects.append(q)
script="const D=require('./dist/workshop-design');const ps="+json.dumps(projects)+";process.stdout.write(JSON.stringify(ps.map(p=>D.envelope(p))));"
js=json.loads(subprocess.run(['node'],input=script,cwd=root,capture_output=True,encoding='utf-8',check=True).stdout)

for q,other in zip(projects,js):
 before=copy.deepcopy(q);parts=d.envelope(q);assert q==before;assert len(parts)==len(other)
 for a,b in zip(parts,other):
  assert a.keys()==b.keys()
  for k,v in a.items():
   if isinstance(v,(float,int)):assert abs(v-b[k])<1e-7,(k,v,b[k])
   elif k in['start','end']:assert all(abs(x-y)<1e-7 for x,y in zip(v,b[k]))
   else:assert v==b[k],k
 assert all(math.dist(a['start'],a['end'])<=16.00001 for a in parts if 'start'in a)
 if q['design']['family']=='atlas':assert sum(a['asset']=='CatwalkStairs'for a in parts)==6
 else:assert sum(a['name']=='Lumen · pavillon vitré'for a in parts)==10
 if (q['size'],q['depth'])in[(64,48),(64,80),(80,64),(96,48),(96,80)]:
  bp,info=p.build(q);assert q==before
  with tempfile.TemporaryDirectory(dir=base)as tmp:
   dest=Path(tmp)/'test.sbp';n.sbp_parse.resaveBlueprint(str(dest),bp);p.verify(n.sbp_parse.parseBlueprint(str(dest)))
  print(f'PASS native {q["design"]["family"]} {q["size"]}x{q["depth"]}: {len(parts)} pieces, binary re-read.',flush=True)
print('PASS: all 50 width/length combinations have JS/Python parity and bounded native beams; 10 native exports re-read.')


