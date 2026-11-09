from pathlib import Path
import sys, math, json, tempfile
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import native_blocks as b, native_compact as c, native_project as p, native_blueprint as n
from native_assembly import Assembly, check_graph

# Every 2x/3x source is a rigid unit, including belts, lift heads and wires.
for key,count in [('smelter2',2),('smelter3',3),('constructor2',2),('constructor3',3)]:
    bp,owners,origin=b.block(key)
    for angle in [0,90,180,270]:
        a=Assembly(p.load('native-connected-template.json'))
        clones,_=b.instantiate(a,bp,owners,origin,[0,0,100],angle,'Recipe_IngotIron_C' if key.startswith('smelter') else 'Recipe_IronPlate_C',.75)
        scene=a.finish(bp[0],[]);by=check_graph(scene);points=c.endpoints(scene)
        assert sum(c.kindof(actor) in p.MACHINES for actor in clones.values())==count
        for h,o in zip(scene[2],scene[3]):
            if isinstance(h,n.sav_parse.ComponentHeader):
                peer=dict(o[0]).get('mConnectedComponent')
                if peer:assert math.dist(points[h.instanceName],points[peer.pathName])<.1
        with tempfile.TemporaryDirectory(dir=root/'data') as tmp:
            path=Path(tmp)/'block.sbp';n.sbp_parse.resaveBlueprint(str(path),scene);check_graph(n.sbp_parse.parseBlueprint(str(path)))

for style,size,reserve in [('compact',40,False),('compact',48,True),('balanced',48,False),('balanced',48,True),('spacious',56,False),('spacious',64,True)]:
    for rate in [.2,5]:
        project=c.proposal(dict(layoutStyle=style,size=size,height=48,storeyMode='single',outputRate=rate,beltPolicy='auto',reserveCladding=reserve,priority='architecture' if reserve else 'production'))
        assert len(project['floors'])==1 and sum(o['type'] in p.MACHINES for o in project['objects'])==8
        assert sum(o['type']=='lift' for o in project['objects'])==13
        assert project['flows']['inputs'][0]['rate']==12*rate
        bp,info=p.build(project);c.verify(bp,project)
        assert info['belts']==(23 if style=='compact' else 26) and info['wires']==11
        assert all(l.get('capacity')==60 for l in project['links'] if l['kind']=='belt')
        with tempfile.TemporaryDirectory(dir=root/'data') as tmp:
            path=Path(tmp)/'chain.sbp';n.sbp_parse.resaveBlueprint(str(path),bp);c.verify(n.sbp_parse.parseBlueprint(str(path)),project)
        if rate==5:(root.parents[1]/'outputs'/f'blocks69-native-{style}-{size}.factory-blueprint.json').write_text(json.dumps(project),encoding='utf8')

# Detached endpoints and changed declared flows fail closed.
project=c.proposal(dict(size=40,height=32,storeyMode='single',outputRate=5,beltPolicy='auto'))
next(o for o in project['objects'] if o['type']=='smelter')['x']+=1
try:c.build_project(project)
except ValueError:pass
else:raise AssertionError('Detached module accepted')
print('PASS: 2x/3x rigid blocks, four rotations, native endpoints, 16 block roundtrips; twelve full single-floor exports across all density styles and roundtrips; detached edit rejected. No game writes.')
