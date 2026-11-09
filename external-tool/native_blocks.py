"""Reusable native blocks and the first calibrated single-storey composition.

All transforms are rigid: splines, lift heads, connections and power follow the
block. Local user blueprints are bundled offline, never read at runtime.
"""
import copy, json, math
from functools import lru_cache
import native_blueprint as n
from native_assembly import Assembly, rotate, check_graph
from native_connected import prop
from native_factory import q, aset

PROFILE = 'iron-plates-blocks-flat-v1'

@lru_cache(maxsize=1)
def sources():
    def decode(value):
        if isinstance(value, dict) and '__bytes__' in value: return bytes.fromhex(value['__bytes__'])
        if isinstance(value, dict): return {k:decode(v) for k,v in value.items()}
        if isinstance(value, list): return [decode(v) for v in value]
        return value
    return n.decode(decode(json.loads((n.ROOT/'data/native-block-sources.json').read_text(encoding='utf8'))))

def instantiate(assembly, bp, owners, origin, position, angle=0, recipe=None, clock=1):
    """Clone a complete connected block, returning old-owner -> new-actor.

    External ports stay free. Never reconnect a block by guessed coordinates.
    """
    import native_compact as c
    import native_project as p
    by=check_graph(bp); rotation=q(angle); mapping={}; powerpoints={}
    transform=lambda v:[a+b for a,b in zip(position,rotate(rotation,[v[i]-origin[i] for i in range(3)]))]
    for h,o in zip(bp[2],bp[3]):
        if not isinstance(h,n.sav_parse.ActorHeader) or h.instanceName not in owners or 'PowerLine.' in h.typePath: continue
        template=c.piece(bp,h.instanceName)
        if bp[0][1]>=60:
            # The recent reference uses a newer property encoding. Rebuild its
            # geometry on our supported native templates, not mixed-version data.
            kind=c.kindof((h,o))
            if kind in ['smelter','constructor','wallPole']:
                source=sources()['smelter2' if kind=='smelter' else 'constructor2']['blueprint']
                owner=next(sh.instanceName for sh,so in zip(source[2],source[3]) if isinstance(sh,n.sav_parse.ActorHeader) and c.kindof((sh,so))==kind)
                template=c.piece(source,owner)
            else:
                template=copy.deepcopy(p.load('native-vertical-template.json')['lift'] if kind=='lift' else p.load('native-connected-template.json')['belt'] if kind=='belt' else p.load('native-factory-template.json')[kind])
            original=template['objects'][0]
            for key in ['mSplineData','mTopTransform','mIsReversed']:
                value=prop(o,key)
                metadata=next((t for (k,v),t in zip(original[2],original[3]) if k==key),None)
                if key=='mTopTransform' and value is not None:
                    top=dict(value[0]);value=[[['Rotation',top['Rotation']],['Translation',top['Translation']]],[['Rotation','StructProperty',0,'Quat',None,0],['Translation','StructProperty',0,'Vector',None,0]]]
                if key=='mSplineData' and value is not None:
                    value=[[copy.deepcopy(row[0]),[[k,'StructProperty',0,'Vector',None,0] for k,v in row[0]]] for row in value]
                if value is not None and metadata is not None:aset((template['headers'][0],original),key,copy.deepcopy(value),copy.deepcopy(metadata[1:]))
        actor=assembly.clone(template,transform(h.position),c.mul(rotation,h.rotation));mapping[h.instanceName]=actor
        if recipe and any(t in h.typePath for t in ['SmelterMk1.','ConstructorMk1.','AssemblerMk1.']):
            assets=json.loads((n.ROOT/'data/native-assets.json').read_text(encoding='utf8'))
            aset(actor,'mCurrentRecipe',p.ref(assets[recipe]['path']),['ObjectProperty',0])
            for key in ['mCurrentPotential','mPendingPotential']:aset(actor,key,clock,['FloatProperty',0])
    for h,o in zip(bp[2],bp[3]):
        if not isinstance(h,n.sav_parse.ActorHeader) or h.instanceName not in owners: continue
        if 'PowerLine.' in h.typePath:
            refs=[r.pathName.rsplit('.',1) for r in o[4]]
            if not all(owner in mapping for owner,suffix in refs): continue
            cached=[v for k,v in prop(o,'mWireInstances')[0][0] if k=='CachedRelativeLocations']
            positions=[transform([h.position[i]+rotate(h.rotation,v)[i] for i in range(3)]) for v in cached]
            ends=[assembly.component(mapping[owner],suffix) for owner,suffix in refs]
            assembly.wire(*ends,*positions)
            for (owner,suffix),pos in zip(refs,positions):powerpoints[mapping[owner][0].instanceName]=pos
        else:
            for ref in o[1]:
                other=dict(by[ref.pathName][1][0]).get('mConnectedComponent')
                if other:
                    owner,suffix=other.pathName.rsplit('.',1)
                    if owner in mapping:assembly.connect(assembly.component(mapping[h.instanceName],ref.pathName.rsplit('.',1)[-1]),assembly.component(mapping[owner],suffix))
    return mapping,powerpoints

def block(key):
    """The 2x/3x sources expose their full native internals as one unit."""
    bp=sources()[key]['blueprint']
    owners={h.instanceName for h in bp[2] if isinstance(h,n.sav_parse.ActorHeader)}
    origin=next(h.position for h in bp[2] if isinstance(h,n.sav_parse.ActorHeader) and 'AttachmentSplitter.' in h.typePath)
    return bp,owners,[origin[0],origin[1],0]

@lru_cache(maxsize=3)
def canonical(clearance=0):
    if clearance:return spaced(clearance)
    import native_compact as c
    import native_project as p
    bp=sources()['reference']['blueprint'];by=check_graph(bp)
    base=p.load('native-test-template.json');extra=p.load('native-connected-template.json');a=Assembly(extra)
    actors=[(h,o) for h,o in zip(bp[2],bp[3]) if isinstance(h,n.sav_parse.ActorHeader)]
    groups={};labels={};mapping={};powerpoints={};modules=[]
    rows=[(-1700,'smelter-0','Recipe_IngotIron_C',1),(-800,'plates','Recipe_IronPlate_C',.75),(0,'rods','Recipe_IronRod_C',1),(900,'screws','Recipe_Screw_C',.75)]
    owner_group={}
    for h,o in actors:
        try:kind=c.kindof((h,o))
        except ValueError:continue
        group='interconnect'
        if kind not in ['belt','power','assembler']:
            row=next((r for r in rows if abs(h.position[1]-r[0])<1),None)
            if row:group=row[1]
        owner_group[h.instanceName]=group
    # Belts/wires belong to a block only when both endpoints belong to it.
    for h,o in actors:
        if h.instanceName not in owner_group:continue
        kind=c.kindof((h,o))
        if kind=='belt':refs=[dict(by[h.instanceName+'.ConveyorAny'+str(i)][1][0]).get('mConnectedComponent') for i in [0,1]]
        elif kind=='power':refs=o[4]
        else:continue
        peers=[owner_group.get(r.pathName.rsplit('.',1)[0]) for r in refs if r]
        if len(peers)==2 and peers[0]==peers[1]:owner_group[h.instanceName]=peers[0]
    for y,group,recipe,clock in rows:
        owners={owner for owner,g in owner_group.items() if g==group}
        cloned,points=instantiate(a,bp,owners,[-800,y,0],[-800,y,100],recipe=recipe,clock=clock)
        mapping.update(cloned);powerpoints.update(points)
        for actor in cloned.values():groups[actor[0].instanceName]=group;labels[actor[0].instanceName]=c.kindof(actor)
        splitter=next(v for v in cloned.values() if c.kindof(v)=='splitter');merger=next(v for v in cloned.values() if c.kindof(v)=='merger')
        modules.append(dict(id=group,source='reference-block',recipe=recipe,clock=clock,input=splitter[0].instanceName,output=merger[0].instanceName,machineCount=sum(c.kindof(v) in p.MACHINES for v in cloned.values())))
    # The reference's screw feed was a placeholder taken from the input bus.
    # Remove that entire belt chain; collect screws from the upper merger.
    wrong=next(h for h,o in actors if 'AttachmentSplitter.' in h.typePath and abs(h.position[1]-900)<1)
    peer=dict(by[wrong.instanceName+'.Output1'][1][0]).get('mConnectedComponent');removed=set()
    while peer:
        owner=peer.pathName.rsplit('.',1)[0]
        if 'ConveyorBelt' not in by[owner][0].typePath:break
        removed.add(owner);peer=dict(by[owner+'.ConveyorAny1'][1][0]).get('mConnectedComponent')
    owners={owner for owner,g in owner_group.items() if g=='interconnect' and owner not in removed}
    cloned,points=instantiate(a,bp,owners,[0,0,0],[0,0,100]);mapping.update(cloned);powerpoints.update(points)
    for actor in cloned.values():groups[actor[0].instanceName]='interconnect';labels[actor[0].instanceName]=c.kindof(actor)
    # Join the compiled module boundaries using their original exact components.
    for h,o in actors:
        if h.instanceName not in mapping:continue
        for ref in o[1]:
            other=dict(by[ref.pathName][1][0]).get('mConnectedComponent')
            if other:
                owner,suffix=other.pathName.rsplit('.',1)
                if owner in mapping:a.connect(a.component(mapping[h.instanceName],ref.pathName.rsplit('.',1)[-1]),a.component(mapping[owner],suffix))
    machine=next(v for v in mapping.values() if c.kindof(v)=='assembler')
    assets=json.loads((n.ROOT/'data/native-assets.json').read_text(encoding='utf8'))
    aset(machine,'mCurrentRecipe',p.ref(assets['Recipe_IronPlateReinforced_C']['path']),['ObjectProperty',0])
    for key in ['mCurrentPotential','mPendingPotential']:aset(machine,key,1,['FloatProperty',0])
    def record(actor,label):groups[actor[0].instanceName]='interconnect';labels[actor[0].instanceName]=label;return actor
    def end(actor,suffix,offset=None):
        if offset is None:offset=next(v for side in p.PORTS[c.kindof(actor)].values() for key,v,d in side if key==suffix)
        return a.component(actor,suffix),a.port(actor,offset)
    def belt(src,dst,points=None):return p.native_belt(a,p.spline(points or [src[1],dst[1]]),src[0],dst[0],1,assets)
    def lift(x,y,low,high,entry,exit):
        actor=record(a.clone(p.load('native-vertical-template.json')['lift'],[x,y,low],q(entry+180)),'Élévateur · sortie')
        aset(actor,'mTopTransform',[[['Rotation',q(exit-entry-180)],['Translation',[0.,0.,high-low]]],[['Rotation','StructProperty',0,'Quat',None,0],['Translation','StructProperty',0,'Vector',None,0]]],['StructProperty',0,'Transform',None,0])
        return end(actor,'ConveyorAny0',[0,0,0]),end(actor,'ConveyorAny1',[0,0,high-low])
    screws=next(v for v in mapping.values() if groups[v[0].instanceName]=='screws' and c.kindof(v)=='merger')
    entry,exit=lift(1500,-200,700,200,-90,-90)
    src=end(screws,'Output1');belt(src,entry,[src[1],[-800,1500,700],[1500,1500,700],entry[1]]);belt(exit,end(machine,'Input1'))
    storage=record(a.clone(p.load('native-factory-template.json')['storage'],[1300,900,100],q(0)),'Coffre · plaques renforcées')
    lo,hi=lift(1850,-1900,200,1300,0,90);src=end(machine,'Output0');belt(src,lo,[src[1],[1300,-1900,200],lo[1]])
    down,out=lift(1300,200,1300,200,90,90);belt(hi,down,[hi[1],[1850,-300,1300],[1300,-300,1300],down[1]]);belt(out,end(storage,'Input0'))
    walls=[next(v for v in mapping.values() if groups[v[0].instanceName]==group and c.kindof(v)=='wallPole') for y,group,r,k in rows]
    for left,right in zip(walls,walls[1:]):a.wire(a.component(left,'PowerConnection'),a.component(right,'PowerConnection'),powerpoints[left[0].instanceName],powerpoints[right[0].instanceName])
    mp=a.port(machine,p.MACHINES['assembler'][5]);a.wire(a.component(walls[-1],'PowerConnection'),a.component(machine,'PowerInput'),powerpoints[walls[-1][0].instanceName],mp)
    result=a.finish(base['versions'],[]);check_graph(result)
    return result,groups,labels,modules,sources()

@lru_cache(maxsize=2)
def spaced(clearance):
    """Move rigid blocks apart, then construct their external buses explicitly."""
    import native_compact as c
    import native_project as p
    bp,original_groups,original_labels,original_modules,library=canonical(0)
    by=check_graph(bp);a=Assembly(p.load('native-connected-template.json'));assets=json.loads((n.ROOT/'data/native-assets.json').read_text(encoding='utf8'))
    rows=['smelter-0','plates','rods','screws'];shifts={group:i*200*clearance for i,group in enumerate(rows)}
    mapping={};groups={};labels={};powerpoints={};modules=[]
    for group in rows:
        owners={owner for owner,g in original_groups.items() if g==group}
        for h,o in zip(bp[2],bp[3]):
            if not isinstance(h,n.sav_parse.ActorHeader):continue
            kind=c.kindof((h,o))
            if kind=='belt':refs=[dict(by[h.instanceName+'.ConveyorAny'+str(i)][1][0]).get('mConnectedComponent') for i in [0,1]]
            elif kind=='power':refs=o[4]
            else:continue
            if len(refs)==2 and all(r and r.pathName.rsplit('.',1)[0] in owners for r in refs):owners.add(h.instanceName)
        cloned,points=instantiate(a,bp,owners,[0,0,0],[0,shifts[group],0]);mapping.update(cloned);powerpoints.update(points)
        for actor in cloned.values():groups[actor[0].instanceName]=group;labels[actor[0].instanceName]=c.kindof(actor)
        module=next(m for m in original_modules if m['id']==group);modules.append({**module,'input':cloned[module['input']][0].instanceName,'output':cloned[module['output']][0].instanceName})
    def record(actor,label):groups[actor[0].instanceName]='interconnect';labels[actor[0].instanceName]=label;return actor
    def device(group,kind):return next(v for v in mapping.values() if groups[v[0].instanceName]==group and c.kindof(v)==kind)
    def end(actor,suffix,offset=None):
        if offset is None:offset=next(v for side in p.PORTS[c.kindof(actor)].values() for key,v,d in side if key==suffix)
        return a.component(actor,suffix),a.port(actor,offset)
    def belt(src,dst,points=None):return p.native_belt(a,p.spline(points or [src[1],dst[1]]),src[0],dst[0],1,assets)
    def lift(x,y,low,high,entry,exit,label):
        actor=record(a.clone(p.load('native-vertical-template.json')['lift'],[x,y,low],q(entry+180)),label)
        aset(actor,'mTopTransform',[[['Rotation',q(exit-entry-180)],['Translation',[0.,0.,high-low]]],[['Rotation','StructProperty',0,'Quat',None,0],['Translation','StructProperty',0,'Vector',None,0]]],['StructProperty',0,'Transform',None,0])
        return end(actor,'ConveyorAny0',[0,0,0]),end(actor,'ConveyorAny1',[0,0,high-low])
    yp,yr,ys=[shifts[g] for g in ['plates','rods','screws']]
    assembler_original=next(h for h,o in zip(bp[2],bp[3]) if isinstance(h,n.sav_parse.ActorHeader) and c.kindof((h,o))=='assembler')
    machine=record(a.clone(c.piece(bp,assembler_original.instanceName),[1300,-1100+yp,100],assembler_original.rotation),'Plaques renforcées · 5/min')
    lo,hi=lift(-800,-1300+yp/2,1000,200,90,90,'Lingots · descente')
    belt(end(device('smelter-0','merger'),'Output1'),lo);belt(hi,end(device('plates','splitter'),'Input1'))
    belt(end(device('plates','splitter'),'Output1'),end(device('rods','splitter'),'Input1'))
    lo,hi=lift(-800,400+(yr+ys)/2,700,200,90,90,'Barres · descente')
    belt(end(device('rods','merger'),'Output1'),lo);belt(hi,end(device('screws','splitter'),'Input1'))
    lo,hi=lift(1100,-200+yp,700,200,0,-90,'Plaques · assemblage')
    src=end(device('plates','merger'),'Output1');belt(src,lo,[src[1],[-800,-200+yp,700],lo[1]]);belt(hi,end(machine,'Input0'))
    lo,hi=lift(1500,-200+yp,700,200,-90,-90,'Vis · assemblage')
    src=end(device('screws','merger'),'Output1');belt(src,lo,[src[1],[-800,1500+ys,700],[1500,1500+ys,700],lo[1]]);belt(hi,end(machine,'Input1'))
    storage=record(a.clone(p.load('native-factory-template.json')['storage'],[1300,900+ys,100],q(0)),'Coffre · plaques renforcées')
    lo,hi=lift(1850,-1900+yp,200,1300,0,90,'Sortie · montée');src=end(machine,'Output0');belt(src,lo,[src[1],[1300,-1900+yp,200],lo[1]])
    down,out=lift(1300,200+ys,1300,200,90,90,'Sortie · coffre');belt(hi,down,[hi[1],[1850,-300+yp,1300],[1300,-300+yp,1300],down[1]]);belt(out,end(storage,'Input0'))
    walls=[device(group,'wallPole') for group in rows]
    for left,right in zip(walls,walls[1:]):a.wire(a.component(left,'PowerConnection'),a.component(right,'PowerConnection'),powerpoints[left[0].instanceName],powerpoints[right[0].instanceName])
    a.wire(a.component(walls[-1],'PowerConnection'),a.component(machine,'PowerInput'),powerpoints[walls[-1][0].instanceName],a.port(machine,p.MACHINES['assembler'][5]))
    result=a.finish(p.load('native-test-template.json')['versions'],[]);check_graph(result)
    return result,groups,labels,modules,library

