from pathlib import Path
import sys,json,copy,math,subprocess,tempfile
root=Path(__file__).resolve().parents[1];base=root/'data';sys.path.insert(0,str(root))
import native_project as p,native_design as d,native_blueprint as n
example=json.loads((root/'dist/atlas-example.json').read_text(encoding='utf-8'));projects=[]
for family in['prisme','canopee','bastion']:
 for width in[64,72,80,88,96]:
  for depth in[48,56,64,72,80]:
   q=copy.deepcopy(example);q['size']=width;q['depth']=depth;q['id']=f'{family}-{width}x{depth}';q['name']=family.title()+f' {width} × {depth} m';q['design'].update(family=family,nativeStudy=family);projects.append(q)
script="const D=require('./dist/workshop-design');process.stdout.write(JSON.stringify(("+json.dumps(projects)+").map(p=>D.envelope(p))));"
result=subprocess.run(['node'],input=script,cwd=root,capture_output=True,encoding='utf-8',check=True);js=json.loads(result.stdout)

for q,other in zip(projects,js):
 before=copy.deepcopy(q);parts=d.envelope(q);assert q==before;assert len(parts)==len(other)
 for a,b in zip(parts,other):
  assert a.keys()==b.keys()
  for k,v in a.items():
   if isinstance(v,(float,int)):assert abs(v-b[k])<1e-7,(k,v,b[k])
   elif k in['start','end']:assert all(abs(x-y)<1e-7 for x,y in zip(v,b[k]))
   else:assert v==b[k],k
 assert all(math.dist(a['start'],a['end'])<=16.00001 for a in parts if 'start'in a)
 assert all(abs(sum(v*v for v in a['quat'])-1)<1e-7 for a in parts if 'quat'in a)
 # Side slopes must stay unique across width variants; only the flat crown grows.
 baseline=d.envelope(dict(q,size=64))
 assert sum(a.get('repeatWidth')is False and a['component']=='module'for a in parts)==sum(a.get('repeatWidth')is False and a['component']=='module'for a in baseline)
 if(q['size'],q['depth'])in[(64,48),(64,80),(80,64),(96,48),(96,80)]:
  bp,info=p.build(q);assert q==before
  with tempfile.TemporaryDirectory(dir=base)as tmp:
   dest=Path(tmp)/'proof.sbp';n.sbp_parse.resaveBlueprint(str(dest),bp);p.verify(n.sbp_parse.parseBlueprint(str(dest)))
  print(f'PASS native {q["id"]}: {len(parts)} pieces; binary re-read.',flush=True)
print('PASS 75 new sizes: JS/Python parity, native beam limits, normalized panel rotations and preserved side facets; 15 native exports re-read.')

