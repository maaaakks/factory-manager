"""Native test 03: two floors and a 12m conveyor lift in an open edge shaft."""
import json,math
import native_blueprint as n
from native_assembly import Assembly,rotate,check_graph
from native_connected import prop,add

NAME='FT_TEST_03_PlaquesEtages'
DESCRIPTION='Factory Tools - TEST 03 : fonderie en bas, constructeur de plaques en haut, deux convoyeurs Mk.1 et un elevateur Mk.1 de 12 m en gaine ouverte. 12 fondations, 2 poteaux, 3 cables. 30 minerai/min -> 20 plaques/min, 8 MW. Brancher le poteau du bas.'


def build():
    base=n.decode(json.loads((n.ROOT/'data'/'native-test-template.json').read_text(encoding='utf-8')))
    extra=n.decode(json.loads((n.ROOT/'data'/'native-connected-template.json').read_text(encoding='utf-8')))
    vertical=n.decode(json.loads((n.ROOT/'data'/'native-vertical-template.json').read_text(encoding='utf-8')))
    a=Assembly(extra);ports=extra['ports']
    smelter=a.clone(base['machine'],[0.0,0.0,100.0]);constructor=a.clone(extra['constructor'],[0.0,0.0,1300.0],[0.0,0.0,1.0,0.0])
    pole_low=a.clone(extra['pole'],[-600.0,1200.0,100.0]);pole_high=a.clone(extra['pole'],[-600.0,600.0,1300.0])
    floor={'headers':[base['foundation']['header']],'objects':[base['foundation']['object']]}
    for x in [-400.0,400.0]:
        for y in [-1200.0,-400.0,400.0,1200.0]:a.clone(floor,[x,y,50.0])
        for y in [-400.0,400.0]:a.clone(floor,[x,y,1250.0])
    half=math.sqrt(.5);lift=a.clone(vertical['lift'],[0.0,1200.0,200.0],[0.0,0.0,-half,half])
    top=prop(lift[1],'mTopTransform')
    for item in top[0]:
        if item[0]=='Translation':item[1]=[0.0,0.0,1200.0]
        elif item[0]=='Rotation':item[1]=[0.0,0.0,0.0,1.0]
    a.belt(a.port(smelter,ports['smelterOutput']),a.port(lift,[0.0,0.0,0.0]),a.component(smelter,'Output2'),a.component(lift,'ConveyorAny0'))
    a.belt(a.port(lift,[0.0,0.0,1200.0]),a.port(constructor,ports['constructorInput']),a.component(lift,'ConveyorAny1'),a.component(constructor,'Input0'))
    power=[(pole_low,'PowerConnection',ports['polePower'],smelter,'PowerConnection',ports['smelterPower']),(pole_low,'PowerConnection',ports['polePower'],pole_high,'PowerConnection',ports['polePower']),(pole_high,'PowerConnection',ports['polePower'],constructor,'PowerInput',ports['constructorPower'])]
    for source,ss,sp,target,ts,tp in power:a.wire(a.component(source,ss),a.component(target,ts),a.port(source,sp),a.port(target,tp))
    costs={'Desc_Cement_C':62,'Desc_IronRod_C':7,'Desc_Wire_C':14,'Desc_IronPlateReinforced_C':2,'Desc_Cable_C':11,'Desc_IronPlate_C':22}
    ingredients=[[costs[ref.pathName.rsplit('.',1)[-1]],ref] for _,ref in extra['ingredients']]
    bp=a.finish(base['versions'],ingredients);verify(bp);return bp


def verify(bp):
    by=check_graph(bp);actors=[(h,o) for h,o in zip(bp[2],bp[3]) if isinstance(h,n.sav_parse.ActorHeader)]
    def of_type(kind):return [(h,o) for h,o in actors if kind+'.' in h.typePath]
    counts={'Build_Foundation_8x1_01':12,'Build_SmelterMk1':1,'Build_ConstructorMk1':1,'Build_ConveyorBeltMk1':2,'Build_ConveyorLiftMk1':1,'Build_PowerPoleMk1':2,'Build_PowerLine':3}
    if len(actors)!=sum(counts.values()) or any(len(of_type(k))!=v for k,v in counts.items()):raise ValueError('Bâtiments du test 03 incorrects.')
    smelter=of_type('Build_SmelterMk1')[0];constructor=of_type('Build_ConstructorMk1')[0];lift=of_type('Build_ConveyorLiftMk1')[0];belts=of_type('Build_ConveyorBeltMk1');poles=sorted(of_type('Build_PowerPoleMk1'),key=lambda p:p[0].position[2]);low,high=poles
    def point(actor,offset):return add(actor[0].position,rotate(actor[0].rotation,offset))
    def component(actor,suffix):return actor[0].instanceName+'.'+suffix
    for actor,recipe in [(smelter,'Recipe_IngotIron_C'),(constructor,'Recipe_IronPlate_C')]:
        r=prop(actor[1],'mCurrentRecipe')
        if not r or r.pathName.rsplit('.',1)[-1]!=recipe:raise ValueError('Recette incorrecte.')
    if smelter[0].position[2]!=100 or constructor[0].position[2]!=1300:raise ValueError('Les machines doivent reposer sur leurs étages respectifs.')
    if constructor[0].rotation!=[0.0,0.0,1.0,0.0]:raise ValueError('Orientation du constructeur incorrecte.')
    top=dict(prop(lift[1],'mTopTransform')[0]);translation=top['Translation']
    if math.dist(translation,[0,0,1200])>.01 or math.dist(top['Rotation'],[0,0,0,1])>.001:raise ValueError('Hauteur ou sortie de l’élévateur incorrecte.')
    # Both lift ends were measured at its origin / top transform in a native belt-connected lift.
    start_lift=point(lift,[0,0,0]);end_lift=point(lift,translation)
    points={component(smelter,'Output2'):point(smelter,[0,200,100]),component(lift,'ConveyorAny0'):start_lift,component(lift,'ConveyorAny1'):end_lift,component(constructor,'Input0'):point(constructor,[0,-300,100])}
    segments=[]
    for h,obj in belts:
        ends=[]
        for idx,p in enumerate(prop(obj,'mSplineData')):
            name=component((h,obj),'ConveyorAny'+str(idx));r=dict(by[name][1][0]).get('mConnectedComponent')
            if not r or r.pathName not in points:raise ValueError('Convoyeur raccordé au mauvais port.')
            location=add(h.position,rotate(h.rotation,dict(p[0])['Location']))
            if math.dist(location,points[r.pathName])>.01:raise ValueError('Convoyeur détaché du port natif.')
            ends.append(r.pathName)
        if len(ends)!=2:raise ValueError('Le convoyeur doit avoir deux extrémités.')
        segments.append(tuple(ends))
    wanted={(component(smelter,'Output2'),component(lift,'ConveyorAny0')),(component(lift,'ConveyorAny1'),component(constructor,'Input0'))}
    if set(segments)!=wanted:raise ValueError('Sens du transport vertical incorrect.')
    # The lift needs upward transport, with incoming +Y / outgoing -Y for these two straight belts.
    incoming=rotate(lift[0].rotation,[-1,0,0]);outgoing=rotate(lift[0].rotation,[1,0,0])
    if math.dist(incoming,[0,1,0])>.001 or math.dist(outgoing,[0,-1,0])>.001:raise ValueError('Orientation de l’élévateur incorrecte.')
    foundations=of_type('Build_Foundation_8x1_01');upper=[h for h,_ in foundations if h.position[2]>1000]
    if len(upper)!=4 or len(foundations)!=12:raise ValueError('Planchers incomplets.')
    for f in upper:
        if f.position[2]!=1250:raise ValueError('Épaisseur/altitude du plancher incorrecte.')
        if abs(f.position[0]-start_lift[0])<500 and abs(f.position[1]-start_lift[1])<500:raise ValueError('La gaine doit rester ouverte sans traverser le plancher.')
    if smelter[0].position[2]+900>min(f.position[2]-50 for f in upper):raise ValueError('Dégagement au-dessus de la fonderie insuffisant.')
    power_points={component(low,'PowerConnection'):point(low,[0,0,700]),component(high,'PowerConnection'):point(high,[0,0,700]),component(smelter,'PowerConnection'):point(smelter,[220,-310,480]),component(constructor,'PowerInput'):point(constructor,[210,-470,687.1653620805591])}
    power_edges=[]
    for h,obj in of_type('Build_PowerLine'):
        if not obj[4] or len(obj[4])!=2:raise ValueError('Câble sans bornes.')
        ends=tuple(r.pathName for r in obj[4]);power_edges.append(ends)
        cached=[v for k,v in prop(obj,'mWireInstances')[0][0] if k=='CachedRelativeLocations'];locations=[v for k,v in prop(obj,'mWireInstances')[0][0] if k=='Locations']
        if len(cached)!=2 or len(locations)!=2:raise ValueError('Géométrie de câble incomplète.')
        for idx,name in enumerate(ends):
            if name not in power_points:raise ValueError('Borne électrique inattendue.')
            if math.dist(add(h.position,rotate(h.rotation,cached[idx])),power_points[name])>.01 or math.dist(locations[idx],power_points[name])>.01:raise ValueError('Câble détaché de sa borne électrique.')
            refs=dict(by[name][1][0]).get('mWires',[])
            if h.instanceName not in [r.pathName for r in refs]:raise ValueError('Câble absent de sa borne.')
        if abs(prop(obj,'mCachedLength')-math.dist(locations[0],locations[1]))>.01:raise ValueError('Longueur de câble incohérente.')
        # Reject a cable crossing a solid upper slab; the inter-floor cable passes outside its edge.
        a,b=locations
        if abs(a[2]-b[2])>1e-8:
            for f in upper:
                for z in [f.position[2]-50,f.position[2],f.position[2]+50]:
                    t=(z-a[2])/(b[2]-a[2])
                    if 0<t<1:
                        p=[a[i]+t*(b[i]-a[i]) for i in range(3)]
                        if abs(p[0]-f.position[0])<400 and abs(p[1]-f.position[1])<400:raise ValueError('Câble traversant le plancher.')
    expected_power={(component(low,'PowerConnection'),component(smelter,'PowerConnection')),(component(low,'PowerConnection'),component(high,'PowerConnection')),(component(high,'PowerConnection'),component(constructor,'PowerInput'))}
    if set(power_edges)!=expected_power:raise ValueError('Réseau électrique incomplet.')
    return {'actors':len(actors),'components':len(bp[2])-len(actors),'designer':4,'inputRate':30,'rate':20,'powerMW':8,'belts':2,'lifts':1,'liftHeightM':12,'floors':2,'foundations':12,'poles':2,'wires':3,'shaft':'open-edge'}
