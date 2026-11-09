from pathlib import Path
import sys,json,subprocess,copy,tempfile
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_project as p,native_design as d,native_blueprint as n
project=json.loads((root/'dist/atlas-example.json').read_text(encoding='utf-8'));before=copy.deepcopy(project)
script="const fs=require('node:fs'),D=require('./dist/workshop-design');const p=JSON.parse(fs.readFileSync('./dist/atlas-example.json','utf8'));process.stdout.write(JSON.stringify(D.envelope(p)));"
js=json.loads(subprocess.run(['node','-e',script],cwd=root,capture_output=True,encoding='utf-8',check=True).stdout)
assert d.envelope(project)==js
bp,info=p.build(project);assert project==before;assert info['belts']==8 and info['lifts']==2 and info['wires']==3;assert info['architecture']['total']==len(js);assert info['powerMW']==8
with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
 path=Path(tmp)/'Atlas.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);by=p.verify(n.sbp_parse.parseBlueprint(str(path)))
 actors=[h for h in bp[2]if isinstance(h,n.sav_parse.ActorHeader)]
 assert sum('CatwalkStairs.'in h.typePath for h in actors)==3
 assert sum('FloodlightWall.'in h.typePath for h in actors)==3
 assert sum('PowerLine.'in h.typePath for h in actors)==3
 assert all(abs(sum(v*v for v in h.rotation)-1)<1e-5 for h in actors)
preview=info['transportPreview'];assert d.envelope(preview)==js
bad=copy.deepcopy(project);bad['objects'][0].update(x=12,y=8)
try:d.envelope(bad)
except p.ExportError:pass
else:raise AssertionError('A stair collision must refuse the fixed composition')
print(f'PASS: Atlas JS/Python parity before and after native routing; binary roundtrip, {len(js)} architectural actors, three native stairs, 8 belts, 2 lifts, 3 reciprocal power wires and no game writes.')
