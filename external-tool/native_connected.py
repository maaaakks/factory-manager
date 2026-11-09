"""Fixed native test 02: iron smelting, belt transport and plate construction."""
import copy
import json
import math
import os
from pathlib import Path
import native_blueprint as n

NAME='FT_TEST_02_PlaquesFer'
DESCRIPTION='Factory Tools - TEST 02 : 8 fondations, fonderie -> convoyeur Mk.1 -> constructeur de plaques de fer. 30 minerai/min -> 20 plaques/min. 8 MW. Brancher le poteau au reseau et alimenter la fonderie. Sortie a recuperer dans le constructeur.'


def prop(obj,key,default=None):
    return next((v for k,v in obj[2] if k==key),default)


def set_component(obj,key,value,kind):
    for p in obj[0]:
        if p[0]==key:p[1]=value;return
    obj[0].append([key,value]);obj[1].append([key,*kind])


def add(a,b):return [a[i]+b[i] for i in range(3)]


def build():
    base=n.decode(json.loads((n.ROOT/'data'/'native-test-template.json').read_text(encoding='utf-8')))
    extra=n.decode(json.loads((n.ROOT/'data'/'native-connected-template.json').read_text(encoding='utf-8')))
    headers=[];objects=[];serial=int.from_bytes(os.urandom(4),'little')
    def clone(piece,position):
        nonlocal serial
        hs=copy.deepcopy(piece['headers']);obs=copy.deepcopy(piece['objects']);original=hs[0].instanceName
        serial=(serial+1)%2**32;new=original.rsplit('_',1)[0]+'_'+str(serial)
        for h in hs:
            h.instanceName=h.instanceName.replace(original,new)
            if isinstance(h,n.sav_parse.ComponentHeader):h.parentActorName=new
        for r in n.references(obs):r.pathName=r.pathName.replace(original,new)
        hs[0].position=list(position);hs[0].rotation=[0.0,0.0,0.0,1.0]
        headers.extend(hs);objects.extend(obs)
        return hs[0],obs[0]
    machine=clone(base['machine'],[0.0,-800.0,100.0]);constructor=clone(extra['constructor'],[0.0,800.0,100.0]);pole=clone(extra['pole'],[-600.0,0.0,100.0])
    for x in [-400.0,400.0]:
        for y in [-1200.0,-400.0,400.0,1200.0]:clone({'headers':[base['foundation']['header']],'objects':[base['foundation']['object']]},[x,y,50.0])
    ports=extra['ports'];start=add(machine[0].position,ports['smelterOutput']);end=add(constructor[0].position,ports['constructorInput']);delta=[end[i]-start[i] for i in range(3)];length=math.dist(start,end);direction=[v/length for v in delta]
    belt=clone(extra['belt'],start);spline=prop(belt[1],'mSplineData')
    for idx,p in enumerate(spline):
        for entry in p[0]:
            if entry[0]=='Location':entry[1]=[0.0,0.0,0.0] if idx==0 else delta
            elif entry[0]=='ArriveTangent':entry[1]=direction if idx==0 else [v*length/2 for v in direction]
            elif entry[0]=='LeaveTangent':entry[1]=[v*length/2 for v in direction] if idx==0 else direction
    def component(actor,suffix):
        name=actor[0].instanceName+'.'+suffix
        idx=next(i for i,h in enumerate(headers) if h.instanceName==name)
        return name,objects[idx]
    def ref(path):return n.sav_parse.ObjectReference('Persistent_Level',path)
    def connect(a,b):
        set_component(a[1],'mConnectedComponent',ref(b[0]),['ObjectProperty',0]);set_component(b[1],'mConnectedComponent',ref(a[0]),['ObjectProperty',0])
    connect(component(machine,'Output2'),component(belt,'ConveyorAny0'));connect(component(belt,'ConveyorAny1'),component(constructor,'Input0'))
    pole_port=add(pole[0].position,ports['polePower']);pole_component=component(pole,'PowerConnection');pole_wires=[]
    for actor,suffix,offset in [(machine,'PowerConnection',ports['smelterPower']),(constructor,'PowerInput',ports['constructorPower'])]:
        target=add(actor[0].position,offset);wire=clone(extra['wire'],pole_port);wire_name=wire[0].instanceName;target_component=component(actor,suffix)
        wire[1][4]=[ref(pole_component[0]),ref(target_component[0])]
        pole_wires.append(ref(wire_name));set_component(target_component[1],'mWires',[ref(wire_name)],['ArrayProperty',0,'ObjectProperty',0])
        instances=prop(wire[1],'mWireInstances');values=instances[0][0];relative=[target[i]-pole_port[i] for i in range(3)];locations=iter([pole_port,target]);cached=iter([[0.0,0.0,0.0],relative])
        for entry in values:
            if entry[0]=='Locations':entry[1]=next(locations)
            elif entry[0]=='CachedRelativeLocations':entry[1]=next(cached)
        for p in wire[1][2]:
            if p[0]=='mCachedLength':p[1]=math.dist(pole_port,target)
    set_component(pole_component[1],'mWires',pole_wires,['ArrayProperty',0,'ObjectProperty',0])
    recipes=[]
    for h,obj in zip(headers,objects):
        if isinstance(h,n.sav_parse.ActorHeader):
            recipe=prop(obj,'mBuiltWithRecipe')
            if recipe.pathName not in [r.pathName for r in recipes]:recipes.append(copy.deepcopy(recipe))
    bp=[base['versions'],[4,extra['ingredients'],recipes],headers,objects];verify(bp);return bp


def verify(bp):
    if isinstance(bp,str):raise ValueError('Blueprint illisible : '+bp)
    versions,summary,headers,objects=bp
    if len(headers)!=len(objects) or summary[0]!=4:raise ValueError('Structure du module connecté invalide.')
    names={h.instanceName for h in headers}
    if len(names)!=len(headers):raise ValueError('Identifiants natifs dupliqués.')
    by={h.instanceName:(h,o) for h,o in zip(headers,objects)};actors=[(h,o) for h,o in zip(headers,objects) if isinstance(h,n.sav_parse.ActorHeader)]
    def of_type(kind):return [(h,o) for h,o in actors if kind+'.' in h.typePath]
    expected={'Build_Foundation_8x1_01':8,'Build_SmelterMk1':1,'Build_ConstructorMk1':1,'Build_ConveyorBeltMk1':1,'Build_PowerPoleMk1':1,'Build_PowerLine':2}
    if len(actors)!=sum(expected.values()) or any(len(of_type(k))!=count for k,count in expected.items()):raise ValueError('Bâtiments inattendus dans le test 02.')
    for h in headers:
        if isinstance(h,n.sav_parse.ComponentHeader) and h.parentActorName not in names:raise ValueError('Composant orphelin.')
    for r in n.references(objects):
        if r.levelName=='Persistent_Level' and r.pathName not in names and r.pathName!='Persistent_Level:PersistentLevel.BuildableSubsystem':raise ValueError('Référence native manquante : '+r.pathName)
    for h,obj in actors:
        for r in obj[1]:
            if r.pathName not in names:raise ValueError('Composant absent de son acteur.')
    machine=of_type('Build_SmelterMk1')[0];constructor=of_type('Build_ConstructorMk1')[0];belt=of_type('Build_ConveyorBeltMk1')[0];pole=of_type('Build_PowerPoleMk1')[0]
    for actor,recipe in [(machine,'Recipe_IngotIron_C'),(constructor,'Recipe_IronPlate_C')]:
        if prop(actor[1],'mCurrentRecipe').pathName.rsplit('.',1)[-1]!=recipe:raise ValueError('Recette incorrecte.')
    def conn(actor,suffix):return actor[0].instanceName+'.'+suffix
    expected_edges=[(conn(machine,'Output2'),conn(belt,'ConveyorAny0')),(conn(belt,'ConveyorAny1'),conn(constructor,'Input0'))]
    for a,b in expected_edges:
        for source,target in [(a,b),(b,a)]:
            r=dict(by[source][1][0]).get('mConnectedComponent')
            if not r or r.pathName!=target:raise ValueError('Raccord convoyeur non réciproque.')
    for component in [conn(machine,'Input0'),conn(constructor,'Output0')]:
        if 'mConnectedComponent' in dict(by[component][1][0]):raise ValueError('Entrée et sortie externes doivent rester libres.')
    # Check straight spline ends against measured native connection offsets (cm).
    start=add(machine[0].position,[0.0,200.0,100.0]);end=add(constructor[0].position,[0.0,-300.0,100.0]);spline=prop(belt[1],'mSplineData')
    if len(spline)!=2 or belt[0].rotation!=[0.0,0.0,0.0,1.0]:raise ValueError('Spline de test inattendue.')
    for point,target in zip(spline,[start,end]):
        location=add(belt[0].position,dict(point[0])['Location'])
        if math.dist(location,target)>.01:raise ValueError('Extrémité du convoyeur hors du port natif.')
    power_positions={conn(pole,'PowerConnection'):add(pole[0].position,[0.0,0.0,700.0]),conn(machine,'PowerConnection'):add(machine[0].position,[220.0,-310.0,480.0]),conn(constructor,'PowerInput'):add(constructor[0].position,[210.0,-470.0,687.1653620805591])}
    wires=of_type('Build_PowerLine');expected_power={conn(machine,'PowerConnection'),conn(constructor,'PowerInput')};seen=set()
    for h,obj in wires:
        if len(obj[4])!=2 or obj[4][0].pathName!=conn(pole,'PowerConnection') or obj[4][1].pathName not in expected_power:raise ValueError('Câble électrique mal raccordé.')
        seen.add(obj[4][1].pathName)
        for r in obj[4]:
            wire_refs=dict(by[r.pathName][1][0]).get('mWires',[])
            if h.instanceName not in [v.pathName for v in wire_refs]:raise ValueError('Câble absent de son composant électrique.')
        if not 0<prop(obj,'mCachedLength')<10000:raise ValueError('Longueur de câble invalide.')
        values=prop(obj,'mWireInstances')[0][0];cached=[v for k,v in values if k=='CachedRelativeLocations'];locations=[v for k,v in values if k=='Locations']
        if h.rotation!=[0.0,0.0,0.0,1.0] or len(cached)!=2 or len(locations)!=2:raise ValueError('Géométrie de câble inattendue.')
        for idx,r in enumerate(obj[4]):
            expected=power_positions[r.pathName]
            if math.dist(add(h.position,cached[idx]),expected)>.01 or math.dist(locations[idx],expected)>.01:raise ValueError('Extrémité du câble hors de la borne électrique.')
        if abs(prop(obj,'mCachedLength')-math.dist(locations[0],locations[1]))>.01:raise ValueError('Cache de longueur du câble incohérent.')
    if seen!=expected_power:raise ValueError('Une machine n’est pas alimentée par le poteau.')
    pole_wire_refs=dict(by[conn(pole,'PowerConnection')][1][0])['mWires']
    if len(pole_wire_refs)!=2:raise ValueError('Le poteau doit garder deux prises libres.')
    return {'actors':len(actors),'components':len(headers)-len(actors),'designer':4,'recipe':'Minerai de fer → lingots → plaques de fer','inputRate':30,'rate':20,'powerMW':8,'belts':1,'wires':2,'foundations':8}
