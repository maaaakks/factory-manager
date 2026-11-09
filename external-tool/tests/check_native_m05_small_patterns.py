from pathlib import Path
import json,sys,hashlib,tempfile
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_design as d,native_project as p,native_blueprint as n,native_compact as c
manifest=json.loads((root/'data/m05/manifest.json').read_text(encoding='utf8'))
assert set(manifest['modules'])=={'C1','C2','M1','M2','M3','M4','M5','M6','IN1','IN2','IC1','IC2'}
catalog=[]
for name,entry in manifest['modules'].items():
 path=root/f'data/m05/{name}.sbp';sha=hashlib.sha256(path.read_bytes()).hexdigest();assert sha==entry['sha256'],name
 bp=n.sbp_parse.parseBlueprint(str(path));actors=[h for h in bp[2]if isinstance(h,n.sav_parse.ActorHeader)];assert len(actors)==entry['actors']
 catalog.append(dict(module=name,url='https://satisfactoryblueprints.com/blueprint/'+entry['id'],file=path.name,actors=len(actors),sha256=sha))
(root.parents[1]/'outputs/jazzfrank60-catalog.json').write_text(json.dumps(dict(author=manifest['author'],url=manifest['url'],modules=catalog),indent=2),encoding='utf8')
rows=json.loads((root.parents[1]/'outputs/patterns60-scenes.json').read_text(encoding='utf8'))
for row in rows:
 scene=row['project'];actual=d.envelope(scene);assert actual==row['parts'],(scene['size'],scene['design']['seed'])
 bp,info=p.build(scene);p.verify(bp)
 with tempfile.TemporaryDirectory(dir=root/'data')as tmp:
  path=Path(tmp)/'pattern.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);p.verify(n.sbp_parse.parseBlueprint(str(path)))
scene=json.loads((root.parents[1]/'outputs/compact60-4x4.factory-blueprint.json').read_text(encoding='utf8'));bp,info=p.build(scene);c.verify(bp,scene);assert info['belts']==54 and info['lifts']==21
scene=json.loads((root.parents[1]/'outputs/compact60-copper.factory-blueprint.json').read_text(encoding='utf8'));bp,info=p.build(scene);p.verify(bp);assert info['belts']>0 and info['lifts']>0
print('PASS: all 12 JazzFrank source hashes and native actor counts, 18 small native facades and exact JS/Python parity, binary roundtrips, compact 4x4 transport unchanged. No game writes.')
