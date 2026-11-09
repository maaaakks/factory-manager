"""Export the actual workshop project. Unsupported/unsafe geometry fails closed."""
from blueprint_dimensions import dimensions,volume_cm,header_dimensions,experimental
import copy,hashlib,heapq,json,math,os,re,tempfile,time,unicodedata
import threading
from collections import OrderedDict
from pathlib import Path
import native_blueprint as n
from native_assembly import Assembly,rotate,check_graph
from native_connected import prop
from native_factory import q,aset

MACHINES={'smelter':('Build_SmelterMk1_C',5,10,8.5,'PowerConnection',[220,-310,480]),'constructor':('Build_ConstructorMk1_C',8,10,6,'PowerInput',[210,-470,687.165]),'assembler':('Build_AssemblerMk1_C',9,17,10.75,'PowerInput',[175,-60,1030])}
TYPES=set(MACHINES)|{'storage','pole','splitter','merger','port','lift'}
PORTS={'smelter':{'in':[('Input0',[0,-300,100],[0,1,0])],'out':[('Output2',[0,200,100],[0,1,0])]},'constructor':{'in':[('Input0',[0,-300,100],[0,1,0])],'out':[('Output0',[0,300,100],[0,1,0])]},'assembler':{'in':[('Input0',[200,-600,100],[0,1,0]),('Input1',[-200,-600,100],[0,1,0])],'out':[('Output0',[0,500,100],[0,1,0])]},'storage':{'in':[('Input0',[0,-400,100],[0,1,0])],'out':[('Output1',[0,400,100],[0,1,0])]},'splitter':{'in':[('Input1',[-100,0,0],[1,0,0])],'out':[('Output1',[100,0,0],[1,0,0]),('Output2',[0,100,0],[0,1,0]),('Output3',[0,-100,0],[0,-1,0])]},'merger':{'in':[('Input1',[-100,0,0],[1,0,0]),('Input2',[0,100,0],[0,-1,0]),('Input3',[0,-100,0],[0,1,0])],'out':[('Output1',[100,0,0],[1,0,0])]}}

class ExportError(ValueError):
    def __init__(self,issues):self.issues=issues;super().__init__('Export impossible : '+issues[0])
def finite(value):return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
def load(name):return n.decode(json.loads((n.ROOT/'data'/name).read_text(encoding='utf-8')))
def ref(path):return n.sav_parse.ObjectReference('',path)
def validate(p):
    issues=[]
    if not isinstance(p,dict) or p.get('kind')!='factory-tools-paper-blueprint' or p.get('schemaVersion') not in [1,2] or not p.get('size'):raise ExportError(['Format de projet Atelier invalide.'])
    if not isinstance(p.get('id'),str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',p['id']) or not isinstance(p.get('name'),str) or not 1<=len(p['name'].strip())<=80:raise ExportError(['Nom ou identifiant du projet invalide.'])
    try:dimensions(p)
    except ValueError as error:raise ExportError([str(error)])
    objects=p.get('objects');links=p.get('links',[]);floors=p.get('floors',[])
    if not isinstance(objects,list) or not 1<=len(objects)<=1000 or not isinstance(links,list) or len(links)>5000 or not isinstance(floors,list) or len(floors)>64:raise ExportError(['Projet vide ou trop volumineux.'])
    ids=set()
    for o in objects:
        if not isinstance(o,dict) or not isinstance(o.get('id'),str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',o['id']) or o['id'] in ids:raise ExportError(['Identifiant de bâtiment invalide ou dupliqué.'])
        ids.add(o['id'])
        if o.get('type') not in TYPES or not isinstance(o.get('name'),str) or not 1<=len(o['name'])<=80 or not all(finite(o.get(k,0)) for k in ['x','y','z','rotation','clock']) or o.get('rotation') not in [0,90,180,270]:raise ExportError(['Valeurs de bâtiment invalides.'])
        if not .01<=o.get('clock',1)<=1:issues.append(o['name']+' : l’horloge native doit être comprise entre 1 et 100 %.')
        if o['type']=='lift' and not any(l.get('via')==o['id'] for l in links):issues.append(o.get('name','Élévateur')+' : reliez une entrée et une sortie pour définir les extrémités de cet élévateur.')
        if o['type'] in MACHINES and not o.get('recipe'):issues.append(o.get('name',o['type'])+' : choisissez une recette avant l’export.')
    for l in links:
        if not isinstance(l,dict) or l.get('kind') not in ['belt','power','planned'] or l.get('from') not in ids or l.get('to') not in ids or l['from']==l['to']:raise ExportError(['Liaison invalide.'])
        if l.get('waypoints'):issues.append('Trajet avec points de passage : aperçu schématique, export natif de ce tracé manuel non calibré. Retirez les points de passage pour utiliser le routage natif.');
        if l['kind']=='planned':issues.append('Liaison logique '+l['from']+' → '+l['to']+' : à remplacer par un convoyeur explicite. Le réseau pointillé ne décrit pas des raccords physiques.')
        if 'rate' in l and (not finite(l['rate']) or not 0<l['rate']<=100000):raise ExportError(['Débit de liaison invalide.'])
        if l.get('capacity',p.get('beltCapacity',120)) not in [60,120,270,480,780,1200]:raise ExportError(['Capacité de convoyeur invalide.'])
    for f in floors:
        if not isinstance(f,dict) or not finite(f.get('z')) or f.get('thickness') not in [1,2] or f.get('material') not in ['concrete','steel','asphalt','polished','metal'] or f['z']<0 or f['z']+f['thickness']>dimensions(p)[2]:issues.append('Plancher invalide : épaisseur native de 1 ou 2 m et matière béton, métal ou asphalte attendues.')
    if not issues:
        ordered=sorted(floors,key=lambda f:f['z'])
        if any(a['z']+a['thickness']>b['z']+.0001 for a,b in zip(ordered,ordered[1:])):issues.append('Les planchers se chevauchent.')
    appearance=p.get('appearance')
    if appearance is not None and (not isinstance(appearance,dict) or not isinstance(appearance.get('enabled'),bool) or not isinstance(appearance.get('color'),str) or not re.fullmatch('#[0-9a-fA-F]{6}',appearance['color'])):issues.append('Couleur globale invalide.')
    if issues:raise ExportError(list(dict.fromkeys(issues))[:20])
    return {o['id']:o for o in objects}

def paint(a,hexcolor):
    rgb=[int(hexcolor[i:i+2],16)/255 for i in [1,3,5]];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]+[1.]
    colors=[[k,list(linear)] for k in ['PrimaryColor','SecondaryColor']]
    aset(a,'mColorSlot',['None',255],['ByteProperty',0])
    aset(a,'mCustomizationData',[[['SwatchDesc',ref('/Game/FactoryGame/Buildable/-Shared/Customization/Swatches/SwatchDesc_Custom.SwatchDesc_Custom_C')],['OverrideColorData',[colors,[[k,'StructProperty',0,'LinearColor',None,0] for k,v in colors]]]],[['SwatchDesc','ObjectProperty',0],['OverrideColorData','StructProperty',0,'FactoryCustomizationColorSlot',None,0]]],['StructProperty',0,'FactoryCustomizationData',None,0])

def recipe(a,o,assembly,assets,catalog):
    key=o['recipe'];r=catalog.get(key);machine=MACHINES[o['type']][0]
    if not r or machine not in r['producedIn'] or key not in assets or any(not i['solid'] for i in r['inputs']+r['outputs']) or len(r['inputs'])>len(PORTS[o['type']]['in']) or len(r['outputs'])!=1:raise ExportError([o['name']+' : recette incompatible avec les ports solides de cette machine.'])
    aset(a,'mCurrentRecipe',ref(assets[key]['path']),['ObjectProperty',0])
    for suffix,rows in [('InputInventory',r['inputs']),('OutputInventory',r['outputs'])]:
        _,component=assembly.component(a,suffix);p,t=component
        current=dict(p);stack=copy.deepcopy(current['mInventoryStacks'][0]);stacks=[]
        for item in rows:
            s=copy.deepcopy(stack)
            for entry in s[0]:
                if entry[0]=='Item':entry[1]=['',1]
                if entry[0]=='NumItems':entry[1]=0
            stacks.append(s)
        for entry in p:
            if entry[0]=='mInventoryStacks':entry[1]=stacks
            elif entry[0]=='mArbitrarySlotSizes':entry[1]=[0]*len(rows)
            elif entry[0]=='mAllowedItemDescriptors':entry[1]=[ref(assets[i['id']]['path']) for i in rows]
    clock=o.get('clock',1)
    for key in ['mCurrentPotential','mPendingPotential']:aset(a,key,clock,['FloatProperty',0])

def aabb(actor,w,d,h):
    head=actor[0];corners=[rotate(head.rotation,[x*w/2,y*d/2,0]) for x in [-1,1] for y in [-1,1]]
    return ([head.position[j]+min(v[j] for v in corners) for j in [0,1]]+[head.position[2]],[head.position[j]+max(v[j] for v in corners) for j in [0,1]]+[head.position[2]+h])

def spline(points,radius=200):
    """Convert a cardinal polyline to line/quarter-circle native Hermite spans."""
    clean=[]
    for p in points:
        if not clean or math.dist(clean[-1],p)>.01:clean.append(p)
    i=1
    while i+1<len(clean):
        a,b,c=clean[i-1:i+2];v=[b[j]-a[j] for j in range(3)];w=[c[j]-b[j] for j in range(3)];cross=v[0]*w[1]-v[1]*w[0]
        if abs(cross)<.01:
            if sum(v[j]*w[j] for j in [0,1])<=0:return None
            clean.pop(i)
        else:i+=1
    if len(clean)<2:return None
    dirs=[];lengths=[]
    for a,b in zip(clean,clean[1:]):
        d=[b[j]-a[j] for j in range(3)];length=math.dist(a,b)
        if sum(abs(v)>.01 for v in d[:2])!=1 or abs(d[2])>.01:return None
        dirs.append([v/length for v in d]);lengths.append(length)
    for i,length in enumerate(lengths):
        if length+1e-4<radius*((i>0)+(i<len(lengths)-1)):return None
    # Each segment is (start,end,start derivative,end derivative).
    spans=[];cursor=clean[0]
    for i in range(1,len(clean)-1):
        corner=clean[i];before=dirs[i-1];after=dirs[i]
        entry=[corner[j]-before[j]*radius for j in range(3)];exit=[corner[j]+after[j]*radius for j in range(3)];length=math.dist(cursor,entry)
        if length>.01:spans.append((cursor,entry,[v*length for v in before],[v*length for v in before]))
        tangent=4*(math.sqrt(2)-1)*radius
        spans.append((entry,exit,[v*tangent for v in before],[v*tangent for v in after]));cursor=exit
    length=math.dist(cursor,clean[-1])
    if length>.01:spans.append((cursor,clean[-1],[v*length for v in dirs[-1]],[v*length for v in dirs[-1]]))
    return spans

def samples(spans):
    result=[]
    for a,b,ta,tb in spans:
        steps=max(24,math.ceil((math.dist(a,b)+math.dist(ta,tb))/25))
        for i in range(steps+1):
            t=i/steps;result.append([(2*t**3-3*t*t+1)*a[j]+(t**3-2*t*t+t)*ta[j]+(-2*t**3+3*t*t)*b[j]+(t**3-t*t)*tb[j] for j in range(3)])
    return result

def route(start,end,forward,arrival,boxes,source,target,size,occupied,radius=200):
    bounds=volume_cm(size)
    if abs(start[2]-end[2])>.1:raise ValueError('Convoyeur entre niveaux : un élévateur natif est nécessaire.')
    def stub(point,direction,box):
        lo,hi=box;distance=radius+25.
        for i in [0,1]:
            if abs(direction[i])>.5:distance=max(distance,(hi[i]-point[i] if direction[i]>0 else point[i]-lo[i])+radius+25)
        return [point[i]+direction[i]*distance for i in range(3)]
    s=stub(start,forward,boxes[source]);e=stub(end,[-v for v in arrival],boxes[target]);candidates=[[start,end],[start,s,e,end],[start,s,[e[0],s[1],s[2]],e,end],[start,s,[s[0],e[1],s[2]],e,end]]
    for coord in range(-int(bounds[0]/2)+200,int(bounds[0]/2)-199,200):candidates.append([start,s,[coord,s[1],s[2]],[coord,e[1],s[2]],e,end])
    for coord in range(-int(bounds[1]/2)+200,int(bounds[1]/2)-199,200):candidates.append([start,s,[s[0],coord,s[2]],[e[0],coord,s[2]],e,end])
    obstacles={}
    for oid,(lo,hi) in boxes.items():
        for x in range(math.floor((lo[0]-35)/200),math.floor((hi[0]+35)/200)+1):
            for y in range(math.floor((lo[1]-35)/200),math.floor((hi[1]+35)/200)+1):obstacles.setdefault((x,y),[]).append((oid,lo,hi))
    def routes():
        yield from candidates
        if radius==100:
            from native_route_search import search
            path=search(s,e,boxes,occupied,bounds,forward,arrival)
            if path:yield [start,*path,end]
    for path in routes():
        spans=spline(path,radius)
        if not spans:continue
        first=spans[0][2];last=spans[-1][3]
        if sum(first[j]*forward[j] for j in [0,1])<.99*math.hypot(*first[:2]) or sum(last[j]*arrival[j] for j in [0,1])<.99*math.hypot(*last[:2]):continue
        pts=samples(spans);bad=False
        for pt in pts:
            if any(abs(pt[j])>bounds[j]/2-25 for j in [0,1])or not -.01<=pt[2]<=bounds[2]+.01:bad=True;break
            for oid,lo,hi in obstacles.get((math.floor(pt[0]/200),math.floor(pt[1]/200)),[]):
                if not lo[2]-.05<=pt[2]<=hi[2]+.05:continue
                if all(lo[j]-35<pt[j]<hi[j]+35 for j in [0,1]):
                    # The game's ports lie inside its clearance box. Only their straight access tunnels are exempt.
                    anchor,direction=(start,forward) if oid==source else (end,arrival) if oid==target else (None,None)
                    if anchor is not None:
                        lateral=abs((pt[0]-anchor[0])*direction[1]-(pt[1]-anchor[1])*direction[0])
                        longitudinal=sum((pt[j]-anchor[j])*direction[j] for j in [0,1])
                        if lateral<30 and (longitudinal>=-.01 if oid==source else longitudinal<=.01):continue
                    bad=True;break
            if bad:break
            bx,by,bz=[math.floor(v/50) for v in pt]
            if any(abs(pt[2]-old[2])<50 and math.hypot(pt[0]-old[0],pt[1]-old[1])<50 for dx in [-1,0,1] for dy in [-1,0,1] for dz in [-1,0,1] for old in occupied.get((bx+dx,by+dy,bz+dz),[])):bad=True;break
        if not bad:return spans
    if radius>100:return route(start,end,forward,arrival,boxes,source,target,size,occupied,100)
    raise ValueError('Le routeur n’a pas trouvé de passage libre aux ports natifs. Revoir l’espace et l’orientation des machines.')

def native_belt(a,spans,source,target,tier,assets):
    actor=a.belt(spans[0][0],spans[-1][1],source,target);head,obj=actor;head.typePath=assets['Build_ConveyorBeltMk'+str(tier)+'_C']['path'];aset(actor,'mBuiltWithRecipe',ref(assets['Recipe_ConveyorBeltMk'+str(tier)+'_C']['path']),['ObjectProperty',0])
    template=copy.deepcopy(prop(obj,'mSplineData')[0]);rows=[]
    for i in range(len(spans)+1):
        pos=spans[i][0] if i<len(spans) else spans[-1][1];tin=spans[i-1][3] if i else spans[0][2];tout=spans[i][2] if i<len(spans) else spans[-1][3];row=copy.deepcopy(template)
        for entry in row[0]:
            if entry[0]=='Location':entry[1]=[pos[j]-head.position[j] for j in range(3)]
            if entry[0]=='ArriveTangent':entry[1]=tin
            if entry[0]=='LeaveTangent':entry[1]=tout
        rows.append(row)
    aset(actor,'mSplineData',rows,next(t[1:] for t in obj[3] if t[0]=='mSplineData'));return actor

def design_color(project,category):
    colors=project.get('design',{}).get('colors',{})
    color=colors.get(category)
    if color is not None and (not isinstance(color,str) or not re.fullmatch('#[0-9a-fA-F]{6}',color)):raise ExportError(['Palette de couleurs invalide.'])
    return color or (project.get('appearance',{}).get('color') if project.get('appearance',{}).get('enabled') else None)

_verified_cache=OrderedDict()
_verified_lock=threading.RLock()

def build(project):
    # Preview and export must reuse exactly the same verified physical routes.
    # Cache successes only; every project change invalidates the complete key.
    try:key=hashlib.sha256(json.dumps(project,sort_keys=True,allow_nan=False,separators=(',',':')).encode()).hexdigest()
    except (ValueError,TypeError):return _build(project)
    with _verified_lock:
        if key in _verified_cache:
            _verified_cache.move_to_end(key)
            return copy.deepcopy(_verified_cache[key])
        result=_route_build(project)
        _verified_cache[key]=copy.deepcopy(result)
        while len(_verified_cache)>2:_verified_cache.popitem(last=False)
        return result

def _route_build(project):
    service=isinstance(project,dict) and isinstance(project.get('objects'),list) and sum(o.get('type') in MACHINES for o in project['objects'] if isinstance(o,dict))>=4
    try:return _build(project,service=service)
    except ExportError as error:
        if not any('voie logistique' in issue or 'routeur' in issue for issue in error.issues):raise
        return _build(project,service=not service)

def _build(project,service=False):
    import native_design
    if isinstance(project,dict)and not project.get('objects')and project.get('design',{}).get('enabled')and native_design.CATALOG['studies'].get(project.get('design',{}).get('family'),{}).get('designFirst'):
        from native_architecture import build as build_architecture
        return build_architecture(project)
    if isinstance(project,dict) and project.get('nativeProfile') in ['iron-plates-pairs-v1','iron-plates-blocks-flat-v1','clean-manifold-v1']:
        import native_compact
        return native_compact.build_project(project)
    import native_transport as transport
    project=transport.prepare(project)
    objects=validate(project);assets=json.loads((n.ROOT/'data'/'native-assets.json').read_text(encoding='utf-8'));catalog=json.loads((n.ROOT/'data'/'game_catalog.json').read_text(encoding='utf-8'))['recipes']
    base=load('native-test-template.json');extra=load('native-connected-template.json');pieces=load('native-factory-template.json');pieces.update({'smelter':base['machine'],'constructor':extra['constructor'],'pole':extra['pole']})
    a=Assembly(extra);actors={};boxes={};size,depth,height=[v*100 for v in dimensions(project)];volume=(size,depth,height);issues=[];used=set();occupied={};physical={};powerMW=0
    def color(actor,category='logistics'):
        value=design_color(project,category)
        if value:paint(actor,value)
    for oid,o in objects.items():
        if o['type'] in ['port','lift']:continue
        pos=[o['x']*100-size/2,o['y']*100-depth/2,o.get('z',0)*100]
        if o['type'] in ['splitter','merger']:pos[2]+=100
        angle=o['rotation']+(-90 if o['type'] in ['splitter','merger'] else 180)
        actor=a.clone(pieces[o['type']],pos,q(angle));actors[oid]=actor;color(actor,'machines' if o['type'] in MACHINES else 'power' if o['type']=='pole' else 'logistics')
        if o['type'] in MACHINES:
            recipe(actor,o,a,assets,catalog);_,w,d,h,_,_=MACHINES[o['type']];powerMW+=float(assets[MACHINES[o['type']][0]].get('mPowerConsumption','0'))*o.get('clock',1)**1.321928
        else:w,d,h={'storage':(5,11,4),'pole':(1,1,7),'splitter':(2,2,1.8),'merger':(2,2,1.8)}[o['type']]
        box=aabb(actor,w*100,d*100,h*100)
        if o['type'] in ['splitter','merger']:box[0][2]=pos[2]-90;box[1][2]=pos[2]+90
        boxes[oid]=box;lo,hi=box
        surfaces=[f['z']+f['thickness'] for f in project.get('floors',[])] or [0]
        if not any(abs(o.get('z',0)-z)<.0001 for z in surfaces):issues.append(o['name']+' : ajouter un plancher sous ce niveau ou poser le bâtiment à sa surface.')
        if lo[0]<-size/2-.01 or lo[1]<-depth/2-.01 or hi[0]>size/2+.01 or hi[1]>depth/2+.01 or lo[2]<-.01 or hi[2]>height+.01:issues.append(o['name']+' dépasse le volume réel du blueprint.')
    if not actors:raise ExportError(['Le plan ne contient aucun bâtiment physique à exporter.'])
    for i,oid in enumerate(boxes):
        lo,hi=boxes[oid]
        for other in list(boxes)[i+1:]:
            a0,a1=boxes[other]
            if all(min(hi[j],a1[j])-max(lo[j],a0[j])>.01 for j in range(3)):issues.append(objects[oid]['name']+' chevauche '+objects[other]['name']+' avec les dimensions du jeu.')
        for floor in project.get('floors',[]):
            if objects[oid]['type']!='lift' and lo[2]<100*(floor['z']+floor['thickness'])-.01 and hi[2]>floor['z']*100+.01:issues.append(objects[oid]['name']+' traverse un plancher : augmenter la hauteur entre étages.')
    if issues:raise ExportError(issues[:20])
    def resource(oid,trail=None):
        trail=set() if trail is None else trail
        if oid in trail:return set()
        trail.add(oid);o=objects[oid]
        if o.get('io',{}).get('item'):return {o['io']['item']}
        if o.get('recipe'):return {i['id'] for i in catalog[o['recipe']]['outputs']}
        out=set()
        for l in project.get('links',[]):
            if l['kind']=='belt' and l['to']==oid:out|=resource(l['from'],trail)
        return out
    def ports(oid,side,link):
        o=objects[oid];out=list(PORTS.get(o['type'],{}).get(side,[]))
        if o['type']=='port':
            io=o.get('io',{}).get('side');expected='out' if io=='input' else 'in' if io=='output' else side
            if side!=expected:return []
            out=[('Boundary'+str(i),[0,0,100],v)for i,v in enumerate([[1,0,0],[0,1,0],[-1,0,0],[0,-1,0]])]
        if side=='in' and o['type']=='assembler':
            r=catalog[o['recipe']];items={link['item']} if link.get('item') else resource(link['from']);matches=[i for i,row in enumerate(r['inputs']) if row['id'] in items]
            if len(matches)!=1:raise ValueError('Ressource ambiguë pour l’entrée de '+o['name']+'. Reliez un producteur identifiable.')
            out=[out[matches[0]]]
        return [p for p in out if (oid,p[0]) not in used]
    wires=set();lift_count=0;lift_columns=[];belt_count=0;preview_links=[];preview_objects=[copy.deepcopy(o)for o in objects.values()if o['type']!='lift']
    for o in preview_objects:
        if o['type'] in MACHINES:o['w'],o['d'],o['h']=MACHINES[o['type']][1:4]
        elif o['type'] in ['splitter','merger']:o.update(w=2,d=2,h=1.8,z=o.get('z',0)+.1)
        elif o['type']=='storage':o.update(w=5,d=11,h=4)
        elif o['type']=='pole':o.update(w=1,d=1,h=7)
    def add_riser(pos,z,entry,exit,tier,column):
        nonlocal lift_count
        actor=transport.lift(a,pos,z,entry,exit,tier,assets);color(actor);lift_count+=1;lift_columns.append(column);boxes['@lift'+str(lift_count)]=column
        oid='export-riser-'+str(lift_count)
        preview_objects.append(dict(id=oid,type='lift',name='Élévateur natif Mk.'+str(tier),x=(pos[0]+size/2)/100,y=(pos[1]+depth/2)/100,z=min(pos[2],z)/100-.25,h=abs(z-pos[2])/100+.5,w=1.2,d=1.2,rotation=0,recipe=None,clock=1,exported=True))
        return actor,oid
    def record_belt(spans,start,end,source_id,target_id,tier,link):
        native_belt(a,spans,start,end,tier,assets)
        preview_links.append(dict(kind='belt',**{'from':source_id,'to':target_id},item=link.get('item'),rate=link.get('rate',0),capacity=link.get('capacity',project.get('beltCapacity',120)),physicalRoute=[dict(x=(v[0]+size/2)/100,y=(v[1]+depth/2)/100,z=v[2]/100)for v in samples(spans)]))
    virtual_boxes={oid:([o['x']*100-size/2-20,o['y']*100-depth/2-20,o.get('z',0)*100],[o['x']*100-size/2+20,o['y']*100-depth/2+20,o.get('z',0)*100+200])for oid,o in objects.items()if o['type']=='port'}
    boxes.update(virtual_boxes)
    if project.get('generation',{}).get('shape')=='exotic':
        cut_x=math.ceil(project['size']/16)*800;cut_y=math.ceil(project.get('depth',project['size'])/16)*800
        boxes['@courtyard']=([cut_x-size/2,-depth/2,0],[size/2,cut_y-depth/2,height])
    if project.get('design',{}).get('enabled') and project.get('design',{}).get('family')=='m05':
        mx=(size%4000)/2+2400;my=(depth%4000)/2+2400
        boxes.update({'@m05-west':([-size/2,-depth/2,0],[-size/2+mx,depth/2,height]),'@m05-east':([size/2-mx,-depth/2,0],[size/2,depth/2,height]),'@m05-north':([-size/2,-depth/2,0],[size/2,-depth/2+my,height]),'@m05-south':([-size/2,depth/2-my,0],[size/2,depth/2,height])})
    access={};head_access={};port_sides={};pending={}
    if service:
        for oid,o in objects.items():
            if oid not in actors:continue
            for side in ['in','out']:
                pending[(oid,side)]=sum(l['kind']!='power' and l['to' if side=='in' else 'from']==oid for l in project.get('links',[]))
                if not pending[(oid,side)]:continue
                for suffix,offset,direction in PORTS.get(o['type'],{}).get(side,[]):
                    port_sides[(oid,suffix)]=side
                    actor=actors[oid][0];point=[x+y for x,y in zip(actor.position,rotate(actor.rotation,offset))];direction=rotate(actor.rotation,direction)
                    if side=='in':direction=[-v for v in direction]
                    lo,hi=boxes[oid];distance=125.
                    for j in [0,1]:
                        if abs(direction[j])>.5:distance=max(distance,(hi[j]-point[j] if direction[j]>0 else point[j]-lo[j])+75)
                    end=[point[j]+direction[j]*distance for j in range(3)]
                    access[(oid,suffix)]=([min(point[j],end[j])-40 for j in range(3)],[max(point[j],end[j])+40 for j in range(3)])
                    ceiling=min([height]+[f['z']*100-25 for f in project.get('floors',[]) if f['z']*100>point[2]])
                    for distance in range(125,1001,25):
                        xy=[point[j]+direction[j]*distance for j in [0,1]]
                        column=([xy[0]-65,xy[1]-65,point[2]-25],[xy[0]+65,xy[1]+65,ceiling])
                        if any(all(min(column[1][j],hi[j])-max(column[0][j],lo[j])>1 for j in range(3))for lo,hi in boxes.values()):continue
                        head_access[(oid,suffix)]=column;break
    def routing_boxes(source,sn,target,tn):
        def inactive(key):
            oid,suffix=key;side=port_sides[key];remaining=pending[(oid,side)]
            if not remaining or key in used or key in [(source,sn),(target,tn)]:return False
            # On the last connection of a junction, alternative unused ports
            # no longer need access columns of their own.
            return not(remaining==1 and (oid==source and side=='out' or oid==target and side=='in'))
        return {**boxes,**{'@access:'+oid+':'+suffix:box for (oid,suffix),box in access.items() if inactive((oid,suffix))},**{'@head:'+oid+':'+suffix:box for (oid,suffix),box in head_access.items() if inactive((oid,suffix))}}
    for link in project.get('links',[]):
        source,target=link['from'],link['to'];so,to=objects[source],objects[target]
        try:
            if any(oid not in actors and objects[oid]['type']!='port' for oid in [source,target]):raise ValueError('Extrémité physique absente.')
            if link['kind']=='power':
                key=tuple(sorted([source,target]))
                if key in wires:raise ValueError('Câble dupliqué.')
                def power(oid):
                    o=objects[oid];kind=o['type']
                    if kind=='pole':suffix,offset='PowerConnection',[0,0,700]
                    elif kind in MACHINES:suffix,offset=MACHINES[kind][4:]
                    else:raise ValueError('Ce bâtiment ne possède pas de raccord électrique.')
                    c=a.component(actors[oid],suffix);refs=dict(c[1][0]).get('mWires',[])
                    limit=4 if kind=='pole' else 1
                    if len(refs)>=limit:raise ValueError(o['name']+' : limite de raccords électriques atteinte.')
                    return c,a.port(actors[oid],offset)
                s,sp=power(source);t,tp=power(target)
                if math.dist(sp,tp)>10000:raise ValueError('Câble de plus de 100 m.')
                a.wire(s,t,sp,tp);wires.add(key);continue
            capacity=link.get('capacity',project.get('beltCapacity',120))
            if link.get('rate',0)>capacity:raise ValueError('Débit demandé supérieur à la capacité du convoyeur.')
            choices=[];last_error='Ports déjà occupés ou inexistants.'
            for sn,sv,sd in ports(source,'out',link):
                for tn,tv,td in ports(target,'in',link):
                    def pose(oid,offset,direction):
                        o=objects[oid];rotation=actors[oid][0].rotation if oid in actors else q(o['rotation']+180);pos=actors[oid][0].position if oid in actors else [o['x']*100-size/2,o['y']*100-depth/2,o.get('z',0)*100]
                        return [x+y for x,y in zip(pos,rotate(rotation,offset))],rotate(rotation,direction)
                    start,forward=pose(source,sv,sd);end,arrival=pose(target,tv,td)
                    try:
                        if service and (so['type'] in MACHINES or to['type'] in MACHINES):raise ValueError('Voie supérieure réservée aux machines.')
                        if abs(start[2]-end[2])>.1:
                            via=objects.get(link.get('via'))
                            if not via or via['type']!='lift':raise ValueError('Le trajet entre étages doit préciser un élévateur.')
                            path=transport.crossing(start,end,forward,arrival,routing_boxes(source,sn,target,tn),source,target,volume,occupied,via);spans=[*path[0],*path[1]]
                        else:path=None;spans=route(start,end,forward,arrival,routing_boxes(source,sn,target,tn),source,target,volume,occupied)
                        pts=samples(spans);choices.append((sum(math.dist(x,y) for x,y in zip(pts,pts[1:])),sn,tn,spans,path,end[2]))
                    except ValueError as exc:last_error=str(exc)
            if not choices:
                for sn,sv,sd in ports(source,'out',link):
                    for tn,tv,td in ports(target,'in',link):
                        start,forward=pose(source,sv,sd);end,arrival=pose(target,tv,td)
                        if abs(start[2]-end[2])>.1 and not link.get('via'):continue
                        try:
                            belts,risers=transport.bridge(start,end,forward,arrival,routing_boxes(source,sn,target,tn),source,target,volume,occupied,project)
                            spans=[span for belt in belts for span in belt];pts=samples(spans)
                            choices.append((sum(math.dist(x,y)for x,y in zip(pts,pts[1:])),sn,tn,spans,{'belts':belts,'risers':risers},end[2]));break
                        except ValueError as exc:last_error=str(exc)
                    if choices:break
            if not choices:raise ValueError(last_error)
            _,sn,tn,spans,path,end_z=min(choices,key=lambda c:c[0]);tier=[60,120,270,480,780,1200].index(capacity)+1
            sc=a.component(actors[source],sn) if source in actors else None;tc=a.component(actors[target],tn) if target in actors else None
            if isinstance(path,dict):
                chain=[sc];chain_ids=[source]
                for pos,z,entry,exit,column in path['risers']:
                    riser,oid=add_riser(pos,z,entry,exit,tier,column);chain_ids.extend([oid,oid])
                    chain.extend([a.component(riser,'ConveyorAny0'),a.component(riser,'ConveyorAny1')])
                chain.append(tc);chain_ids.append(target)
                for i,belt in enumerate(path['belts']):record_belt(belt,chain[2*i],chain[2*i+1],chain_ids[2*i],chain_ids[2*i+1],tier,link);belt_count+=1
            elif path:
                first,second,pos,entry,exit,column=path
                riser,oid=add_riser(pos,end_z,entry,exit,tier,column)
                record_belt(first,sc,a.component(riser,'ConveyorAny0'),source,oid,tier,link);record_belt(second,a.component(riser,'ConveyorAny1'),tc,oid,target,tier,link);belt_count+=2
            else:record_belt(spans,sc,tc,source,target,tier,link);belt_count+=1
            used.update([(source,sn),(target,tn)])
            if service:
                for key in [(source,'out'),(target,'in')]:
                    if key in pending:pending[key]-=1
            for pt in samples(spans):occupied.setdefault(tuple(math.floor(v/50) for v in pt),[]).append(pt)
            physical[(source,target)]=spans
        except ValueError as exc:issues.append(so['name']+' → '+to['name']+' : '+str(exc))
    if issues:raise ExportError(issues[:20])
    for h,o in zip(a.headers,a.objects):
        if isinstance(h,n.sav_parse.ActorHeader) and ('ConveyorBelt' in h.typePath or 'PowerLine' in h.typePath):color((h,o),'power' if 'PowerLine' in h.typePath else 'logistics')
    foundation_count=0;frame_count=0
    architectural_project={**project,'objects':preview_objects,'links':preview_links+[copy.deepcopy(l)for l in project.get('links',[])if l['kind']=='power'],'floors':transport.floor_holes(project,lift_columns)}
    for floor in architectural_project['floors']:
        allowed_floor=set(native_design.floor_cells(architectural_project,floor))
        material=floor['material'];thick=floor['thickness'];stem=native_design.floor_stem(material,thick)
        cls='Build_'+stem+'_C';r='Recipe_'+stem+'_C'
        if cls not in assets or r not in assets:raise ExportError(['Matière de fondation non prise en charge.'])
        for x in range(400,int(size),800):
            for y in range(400,int(depth),800):
                if (x//800,y//800)not in allowed_floor:continue
                profile=native_design.add_floor(a,architectural_project,floor,x/100,y/100,assets)
                if profile=='frame':frame_count+=1
                elif profile=='solid':foundation_count+=1

    architecture=native_design.add(a,architectural_project,assets)
    bp=a.finish(base['versions'],costs(a,assets));bp[1][0]=header_dimensions(project);verify(bp)
    warnings=[]
    if project.get('buffer'):warnings.append(str(len(project['buffer']))+' objets du tampon restent hors du blueprint.')
    if any(o['type']=='port' for o in objects.values()):warnings.append('Entrées/sorties : extrémités libres de convoyeurs à raccorder en jeu.')
    missing=[o['name'] for oid,o in objects.items() if o['type'] in MACHINES and not any(oid in pair for pair in wires)]
    if missing:warnings.append(str(len(missing))+' machines sans câble : branchement manuel nécessaire en jeu.')
    if experimental(project):warnings.append('Format libre XL expérimental : placement dans le jeu à valider. Réédition dans un designer vanilla non garantie.')
    return bp,{'objects':len(actors)+lift_count,'architecture':architecture,'foundations':foundation_count,'frames':frame_count,'factoryFloors':sum(len(native_design.floor_cells(architectural_project,f))for f in architectural_project['floors']if f.get('profile')=='factory'),'transportPreview':{**project,'objects':preview_objects,'links':preview_links+[copy.deepcopy(l)for l in project.get('links',[])if l['kind']=='power'],'floors':transport.floor_holes(project,lift_columns)},'belts':belt_count,'lifts':lift_count,'liftHoles':transport.floor_holes(project,lift_columns),'wires':len(wires)+architecture.get('lightWires',0),'size':project['size'],'dimensions':dict(zip(['width','depth','height'],dimensions(project))),'experimentalXL':experimental(project),'powerMW':round(powerMW+architecture.get('lightingMW',0),2),'warnings':warnings,'inGameValidated':False}

def costs(a,assets):
    totals={}
    for h,o in zip(a.headers,a.objects):
        if not isinstance(h,n.sav_parse.ActorHeader):continue
        key=prop(o,'mBuiltWithRecipe').pathName.rsplit('.',1)[-1];factor=1
        if 'ConveyorBelt' in h.typePath:
            rows=[dict(p[0]) for p in prop(o,'mSplineData')];spans=[(x['Location'],y['Location'],x['LeaveTangent'],y['ArriveTangent']) for x,y in zip(rows,rows[1:])];pts=samples(spans);factor=max(1,math.ceil((sum(math.dist(x,y) for x,y in zip(pts,pts[1:]))-.01)/200))
        if 'ConveyorLift' in h.typePath:factor=max(1,math.ceil(abs(dict(prop(o,'mTopTransform')[0])['Translation'][2])/200))
        if 'PowerLine.' in h.typePath:factor=max(1,math.ceil((prop(o,'mCachedLength')-.01)/2500))
        for path,amount in re.findall(r'ItemClass=.*?(/Game/[^\"\']+).*?Amount=(\d+)',assets[key]['mIngredients']):totals[path]=totals.get(path,0)+int(amount)*factor
    return [[amount,ref(path)] for path,amount in sorted(totals.items())]

def verify(bp):
    by=check_graph(bp)
    def endpoint(name):
        owner,suffix=name.rsplit('.',1);h,o=by[owner]
        if 'ConveyorBelt' in h.typePath:offset=dict(prop(o,'mSplineData')[0 if suffix=='ConveyorAny0' else -1][0])['Location']
        elif 'ConveyorLift' in h.typePath:offset=[0,0,0] if suffix=='ConveyorAny0' else dict(prop(o,'mTopTransform')[0])['Translation']
        else:
            kind=next((kind for kind,needle in [('smelter','SmelterMk1.'),('constructor','ConstructorMk1.'),('assembler','AssemblerMk1.'),('splitter','AttachmentSplitter.'),('merger','AttachmentMerger.'),('storage','StorageContainerMk1.')] if needle in h.typePath),None)
            offset=next(v for side in PORTS[kind].values() for key,v,direction in side if key==suffix)
        return [a+b for a,b in zip(h.position,rotate(h.rotation,offset))]
    for h,o in zip(bp[2],bp[3]):
        if isinstance(h,n.sav_parse.ComponentHeader):
            target=dict(o[0]).get('mConnectedComponent')
            if target and math.dist(endpoint(h.instanceName),endpoint(target.pathName))>.1:raise ValueError('Extrémité native non raccordée.')
            continue
        if not all(finite(v) for v in h.position+h.rotation):raise ValueError('Transform natif invalide.')
        if 'PowerLine.' in h.typePath:
            for r in o[4]:
                if not any(v.pathName==h.instanceName for v in dict(by[r.pathName][1][0]).get('mWires',[])):raise ValueError('Câble non réciproque.')
    return by

def output_icon(project):
    from sav_data.data import ICON_NAMES_TO_IDS
    names={'Desc_IronIngot_C':'Iron Ingot','Desc_CopperIngot_C':'Copper Ingot','Desc_IronPlate_C':'Iron Plate','Desc_IronRod_C':'Iron Rod','Desc_OreIron_C':'Iron Ore','Desc_OreCopper_C':'Copper Ore','Desc_Wire_C':'Wire','Desc_Cable_C':'Cable','Desc_IronScrew_C':'Screw','Desc_CopperSheet_C':'Copper Sheet','Desc_IronPlateReinforced_C':'Reinforced Iron Plate'}
    outputs=project.get('flows',{}).get('outputs',[])
    primary=max(outputs,key=lambda row:row.get('rate') or 0,default={})
    return ICON_NAMES_TO_IDS.get(names.get(primary.get('id')),4)

def save(project,session,base=None):
    bp,details=build(project);target=n.destination(session,base)
    slug=unicodedata.normalize('NFKD',project['name']).encode('ascii','ignore').decode();slug=re.sub('[^A-Za-z0-9_-]+','_',slug).strip('_')[:45] or 'Blueprint'
    name='FT_'+slug+'_'+hashlib.sha256(project['id'].encode()).hexdigest()[:10];tag='Factory Tools | projet '+project['id']+' | '
    description=tag+project['name']+' | '+str(details['objects'])+' objets | '+str(details['powerMW'])+' MW. Export du projet Atelier. Validation en jeu a effectuer.'
    if details.get('profile')=='iron-plates-pairs-v1':description+=' Entree 120 minerais/min : repartiteur gauche au RDC, face X negatif. Sortie : coffre en haut. Alimenter un raccord mural ou poteau. Attendre le remplissage des manifolds. Planchers selon le projet.'
    if details.get('architecture',{}).get('total'):description+=' Habillage natif : '+str(details['architecture']['total'])+' pieces.'
    with n.LOCK:
        target.mkdir(parents=True,exist_ok=True)
        old=target/(name+'.sbpcfg')
        owned=False
        if old.is_file() and not old.is_symlink():
            try:owned=n.sbp_parse.parseBlueprintConfig(str(old))[1].startswith(tag)
            except (n.sav_parse.ParseError,ValueError,TypeError,IndexError):owned=False
        for suffix in ['.sbp','.sbpcfg']:
            dest=target/(name+suffix)
            if dest.is_symlink():raise ValueError('Lien symbolique refusé.')
            if dest.exists() and not owned:raise ValueError('Un blueprint extérieur à ce projet porte ce nom ; il ne sera pas remplacé.')
        with tempfile.TemporaryDirectory(dir=n.ROOT/'data') as tmp:
            pair=[Path(tmp)/(name+s) for s in ['.sbp','.sbpcfg']];n.sbp_parse.resaveBlueprint(str(pair[0]),bp)
            if project.get('nativeProfile') in ['iron-plates-pairs-v1','iron-plates-blocks-flat-v1','clean-manifold-v1']:
                import native_compact
                native_compact.verify(n.sbp_parse.parseBlueprint(str(pair[0])),project)
            else:verify(n.sbp_parse.parseBlueprint(str(pair[0])))
            icon=output_icon(project)
            n.sbp_parse.resaveBlueprintConfig(str(pair[1]),(4,description,icon,[.12,.3,.2,1.],'None','None',[],None,None))
            if n.sbp_parse.parseBlueprintConfig(str(pair[1]))[2]!=icon:raise ValueError('Icône de sortie native illisible.')
            if n.sbp_parse.parseBlueprintConfig(str(pair[1]))[1]!=description:raise ValueError('Configuration native illisible.')
            files=[]
            for source in pair:
                dest=target/source.name
                if dest.exists():
                    backup=n.ROOT/'data'/'native-backups';backup.mkdir(exist_ok=True);(backup/(str(time.time_ns())+'-'+source.name)).write_bytes(dest.read_bytes())
                fd,temp=tempfile.mkstemp(prefix='ft-project-',suffix='.tmp',dir=target)
                try:
                    with os.fdopen(fd,'wb') as f:f.write(source.read_bytes());f.flush();os.fsync(f.fileno())
                    os.replace(temp,dest)
                finally:
                    if os.path.exists(temp):os.unlink(temp)
                files.append({'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    return {'name':name,'directory':str(target),'session':session,'files':files,'verified':details,'inGameValidated':False}


