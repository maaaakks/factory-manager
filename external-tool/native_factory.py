"""Fixed test 04: a 32m square, three-storey reinforced plate factory.

Native templates come from local blueprints; no world save is modified.
"""
import copy,json,math,re
import native_blueprint as n
from native_assembly import Assembly,rotate,check_graph
from native_connected import prop,set_component

NAME='FT_TEST_04_PlaquesRenforcees'
DESCRIPTION='Factory Tools TEST 04 - 4x4, 3 etages beton, machines noires. 120 minerai de fer/min -> 10 plaques renforcees/min dans un coffre. 78 MW. Convoyeurs Mk.2, passages de fondation natifs. Sols a 1 / 10.5 / 20 m. Brancher le poteau du RDC et alimenter le repartiteur central cote sud (Y negatif). Attendre le remplissage des manifolds.'
Z=[100.,1050.,2000.]
OFF={'Input0':[0,-300,100],'Output0':[0,300,100],
     'Input1':[-100,0,0],'Output1':[100,0,0],'Input2':[0,100,0],'Input3':[0,-100,0],'Output2':[0,100,0],'Output3':[0,-100,0]}

def q(deg):return [0.,0.,math.sin(math.radians(deg)/2),math.cos(math.radians(deg)/2)]
def aset(actor,key,value,kind):
    p,t=actor[1][2:4]
    for i,(k,v) in enumerate(p):
        if k==key:p[i][1]=value;t[i]=[key,*kind];return
    p.append([key,value]);t.append([key,*kind])

def black(actor):
    color=[['PrimaryColor',[0.,0.,0.,1.]],['SecondaryColor',[0.,0.,0.,1.]]]
    types=[[k,'StructProperty',0,'LinearColor',None,0] for k,v in color]
    sw=n.sav_parse.ObjectReference('','/Game/FactoryGame/Buildable/-Shared/Customization/Swatches/SwatchDesc_Custom.SwatchDesc_Custom_C')
    aset(actor,'mColorSlot',['None',255],['ByteProperty',0])
    aset(actor,'mCustomizationData',[[['SwatchDesc',sw],['OverrideColorData',[color,types]]],[['SwatchDesc','ObjectProperty',0],['OverrideColorData','StructProperty',0,'FactoryCustomizationColorSlot',None,0]]],['StructProperty',0,'FactoryCustomizationData',None,0])

class Factory(Assembly):
    def __init__(self,extra,pieces):
        super().__init__(extra);self.pieces=pieces;self.links=[];self.nodes=[];self.production=[];self.lifts=[];self.holes=[];self.splines=[]
    def node(self,kind,x,y,z,angle=0):
        a=self.clone(self.pieces[kind],[x,y,z],q(angle));self.nodes.append((kind,a));return a
    def machine(self,kind,x,y,z,angle=0):
        a=self.node(kind,x,y,z,angle);black(a);self.production.append((kind,a));return a
    def end(self,actor,suffix,offset=None):
        return (self.component(actor,suffix),self.port(actor,offset or OFF[suffix]))
    def belt(self,src,dst,flow=0):
        start,end=src[1],dst[1]
        if math.dist(start,end)<1: self.connect(src[0],dst[0]);return
        a=super().belt(start,end,src[0],dst[0])
        a[0].typePath=a[0].typePath.replace('Mk1','Mk2');r=prop(a[1],'mBuiltWithRecipe');r.pathName=r.pathName.replace('Mk1','Mk2')
        self.links.append((src[0][0],dst[0][0],flow));self.splines.append(a)
        return a
    def curve(self,src,dst,first,last,flow=0):
        """Horizontal 90-degree turn, 2m radius, exact native Hermite arc."""
        s,e=src[1],dst[1];d=[e[i]-s[i] for i in range(3)]
        if abs(first[0]*last[0]+first[1]*last[1])>.1:
            return self.belt(src,dst,flow)
        u=sum(d[i]*first[i] for i in range(2));v=sum(d[i]*last[i] for i in range(2));radius=200.
        if min(u,v)<radius-.01:raise ValueError('Virage trop court : '+str((s,e,u,v)))
        corner=[s[i]+first[i]*u for i in range(2)];arcstart=[corner[i]-first[i]*radius for i in range(2)];arcend=[corner[i]+last[i]*radius for i in range(2)]
        total=u+v-2*radius+radius*math.pi/2;pts=[list(s)];dist=[0.]
        if u-radius>.01:pts.append([*arcstart,0]);dist.append(u-radius)
        if math.dist(pts[-1][:2],arcstart)>.01:raise ValueError('Arc incorrect')
        arcindex=len(pts)-1;pts.append([*arcend,0]);dist.append(u-radius+radius*math.pi/2)
        if v-radius>.01:pts.append(list(e));dist.append(total)
        for p,l in zip(pts,dist):p[2]=s[2]+(e[2]-s[2])*l/total
        if abs(e[2]-s[2])/total>math.tan(math.radians(35))+.001:raise ValueError('Pente convoyeur >35 degres')
        a=self.belt(src,dst,flow);template=copy.deepcopy(prop(a[1],'mSplineData')[0]);data=[]
        for i,p in enumerate(pts):
            row=copy.deepcopy(template);direction=first if i<=arcindex else last
            before=math.dist(pts[i-1],p) if i else 1.;after=math.dist(p,pts[i+1]) if i+1<len(pts) else 1.
            tin=before if i else 1.;tout=after if i+1<len(pts) else 1.
            if i==arcindex:tout=radius*4*(math.sqrt(2)-1)
            if i==arcindex+1:tin=radius*4*(math.sqrt(2)-1)
            for entry in row[0]:
                if entry[0]=='Location':entry[1]=[p[j]-s[j] for j in range(3)]
                elif entry[0]=='ArriveTangent':entry[1]=[direction[0]*tin,direction[1]*tin,(e[2]-s[2])*tin/total]
                elif entry[0]=='LeaveTangent':entry[1]=[direction[0]*tout,direction[1]*tout,(e[2]-s[2])*tout/total]
            data.append(row)
        aset(a,'mSplineData',data,next(t[1:] for t in a[1][3] if t[0]=='mSplineData'))
        return a
    def riser(self,x,y,low,high,lower_angle,upper_angle,end_height=100):
        """Two lifts joined through a real floor hole, not a belt clipping a slab."""
        plane=high-50.;hole=self.node('hole',x,y,plane)
        lower=self.node('lift',x,y,low+100,lower_angle);upper=self.node('lift',x,y,plane,upper_angle)
        for actor,height in [(lower,plane-low-100),(upper,high+end_height-plane)]:
            actor[0].typePath=actor[0].typePath.replace('Mk1','Mk2');prop(actor[1],'mBuiltWithRecipe').pathName=prop(actor[1],'mBuiltWithRecipe').pathName.replace('Mk1','Mk2')
            aset(actor,'mTopTransform',[[['Rotation',q(0)],['Translation',[0.,0.,height]]],[['Rotation','StructProperty',0,'Quat',None,0],['Translation','StructProperty',0,'Vector',None,0]]],['StructProperty',0,'Transform',None,0])
        empty=n.sav_parse.ObjectReference('','')
        aset(lower,'mOutputMeshDisplayMode',['EFGBuildableConveyorLiftMeshDisplayMode','EFGBuildableConveyorLiftMeshDisplayMode::MDM_Empty'],['EnumProperty',0])
        aset(lower,'mIsBeltUsingInputRotation',1,['BoolProperty',0])
        aset(upper,'mInputMeshDisplayMode',['EFGBuildableConveyorLiftMeshDisplayMode','EFGBuildableConveyorLiftMeshDisplayMode::MDM_Empty'],['EnumProperty',0])
        aset(lower,'mSnappedPassthroughs',[empty,self.ref(hole[0].instanceName)],['ArrayProperty',0,'ObjectProperty',0])
        aset(upper,'mSnappedPassthroughs',[self.ref(hole[0].instanceName),copy.deepcopy(empty)],['ArrayProperty',0,'ObjectProperty',0])
        self.connect(self.component(lower,'ConveyorAny1'),self.component(upper,'ConveyorAny0'))
        aset(hole,'mBottomSnappedConnection',self.ref(lower[0].instanceName+'.ConveyorAny1'),['ObjectProperty',0])
        aset(hole,'mTopSnappedConnection',self.ref(upper[0].instanceName+'.ConveyorAny0'),['ObjectProperty',0])
        self.lifts.extend([lower,upper]);self.holes.append(hole)
        return self.end(lower,'ConveyorAny0',[0,0,0]),self.end(upper,'ConveyorAny1',[0,0,high+end_height-plane])

def build():
    load=lambda f:n.decode(json.loads((n.ROOT/'data'/f).read_text(encoding='utf-8')))
    base=load('native-test-template.json');extra=load('native-connected-template.json');p=load('native-factory-template.json');p.update({'smelter':base['machine'],'plates':extra['constructor'],'pole':extra['pole'],'lift':load('native-vertical-template.json')['lift']})
    a=Factory(extra,p);P=extra['ports']
    for z in Z:
        for x in [-1200,-400,400,1200]:
            for y in [-1200,-400,400,1200]:a.node('concrete',x,y,z-50)
    sm=[a.machine('smelter',-900,y,Z[0],90) for y in [-1000,0,1000]]
    sm.append(a.machine('smelter',900,-1000,Z[0],-90))
    rods=[a.machine('rods',900,y,Z[0],90) for y in [0,1000]]
    plates=[a.machine('plates',-900,y,Z[1],-90) for y in [-1000,0,1000]]
    screws=[a.machine('screws',900,y,Z[1],90) for y in [-1000,0,1000]]
    assemblers=[a.machine('assembler',x,-300,Z[2]) for x in [-700,700]]
    storage=a.node('storage',0,1050,Z[2]);black(storage)
    # Ore manifold: the front Input1 is the single external 120/min interface.
    ore=[a.node('splitter',0,y,Z[0]+100,90) for y in [-1000,0,1000]]
    for i in range(2):a.belt(a.end(ore[i],'Output1'),a.end(ore[i+1],'Input1'),60 if i==0 else 30)
    for i in range(3):a.belt(a.end(ore[i],'Output2'),a.end(sm[i],'Input0',P['smelterInput']),30)
    a.belt(a.end(ore[0],'Output3'),a.end(sm[3],'Input0',P['smelterInput']),30)
    # Three independent 30/min ingot columns, through the first concrete floor.
    for i,y in enumerate([-1000,0,1000]):
        lo,hi=a.riser(-1500,y,Z[0],Z[1],0,0)
        a.belt(a.end(sm[i],'Output2',P['smelterOutput']),lo,30);a.belt(hi,a.end(plates[i],'Input0'),30)
    # Fourth smelter feeds the two rod constructors along the outside lane.
    rs=[a.node('splitter',1400,y,Z[0]+100,90) for y in [0,1000]]
    a.curve(a.end(sm[3],'Output2',P['smelterOutput']),a.end(rs[0],'Input1'),[1,0],[0,1],30)
    a.belt(a.end(rs[0],'Output1'),a.end(rs[1],'Input1'),15)
    for r,s in zip(rods,rs):a.belt(a.end(s,'Output2'),a.end(r,'Input0'),15)
    rm=[a.node('merger',200,y,Z[0]+100,90) for y in [0,1000]]
    for r,m in zip(rods,rm):a.belt(a.end(r,'Output0'),a.end(m,'Input3'),15)
    a.belt(a.end(rm[0],'Output1'),a.end(rm[1],'Input1'),15)
    # Rod bus turns into the right-hand input lane on the constructor floor.
    lo,hi=a.riser(1400,1400,Z[0],Z[1],180,-90)
    a.curve(a.end(rm[1],'Output1'),lo,[0,1],[1,0],30)
    ss=[a.node('splitter',1400,y,Z[1]+100,-90) for y in [1000,0,-1000]]
    a.belt(hi,a.end(ss[0],'Input1'),30)
    for i in range(2):a.belt(a.end(ss[i],'Output1'),a.end(ss[i+1],'Input1'),20-i*10)
    for s,c in zip(ss,reversed(screws)):a.belt(a.end(s,'Output3'),a.end(c,'Input0'),10)
    # Central independent plate/screw manifolds, then real holes into assembly.
    inputs=[]
    for machines,x,rate,side,extraheight in [(plates,-200,20,'Input3',100),(screws,200,40,'Input2',380)]:
        merges=[a.node('merger',x,y,Z[1]+100,-90) for y in [-1000,0,1000]]
        for c,m in zip(machines,merges):a.belt(a.end(c,'Output0'),a.end(m,side),rate)
        for i in [2,1]:a.belt(a.end(merges[i],'Output1'),a.end(merges[i-1],'Input1'),rate*(3-i))
        lo,hi=a.riser(x,-1400,Z[1],Z[2],90,0 if rate==20 else 180,extraheight)
        a.belt(a.end(merges[0],'Output1'),lo,3*rate)
        splitter=a.node('splitter',0,-1100,Z[2]+extraheight,90)
        a.curve(hi,a.end(splitter,'Input1'),[1 if rate==20 else -1,0],[0,1],3*rate);inputs.append(splitter)
    for j,assembler in enumerate(assemblers):
        for i,splitter in enumerate(inputs):
            suffix='Output2' if j==0 else 'Output3';port='Input0' if i==0 else 'Input1';offset=[200 if i==0 else -200,-600,100]
            a.curve(a.end(splitter,suffix),a.end(assembler,port,offset),[-1 if j==0 else 1,0],[0,1],30 if i==0 else 60)
    # Finished plates merge into an ordinary, empty Mk.1 storage container.
    final=a.node('merger',0,400,Z[2]+100,90)
    for j,c in enumerate(assemblers):
        a.curve(a.end(c,'Output0',[0,500,100]),a.end(final,'Input2' if j==0 else 'Input3'),[0,1],[1 if j==0 else -1,0],5)
    a.belt(a.end(final,'Output1'),a.end(storage,'Input0',[0,-400,100]),10)
    # Mk.1 poles: at most two machines + two backbone cables per pole.
    poles=[]
    groups=[a.production[i:i+2] for i in range(0,len(a.production),2)]
    spots=[(300,-700,Z[0]),(300,300,Z[0]),(300,1300,Z[0]),(0,-700,Z[1]),(0,300,Z[1]),(0,1300,Z[1]),(-1400,500,Z[2])]
    for group,(x,y,z) in zip(groups,spots):
        pole=a.node('pole',x,y,z);poles.append(pole)
        for kind,c in group:
            suffix='PowerConnection' if kind=='smelter' else 'PowerInput'
            offset=P['smelterPower'] if kind=='smelter' else ([175,-60,1030] if kind=='assembler' else P['constructorPower'])
            a.wire(a.component(pole,'PowerConnection'),a.component(c,suffix),a.port(pole,P['polePower']),a.port(c,offset))
    for left,right in zip(poles,poles[1:]):a.wire(a.component(left,'PowerConnection'),a.component(right,'PowerConnection'),a.port(left,P['polePower']),a.port(right,P['polePower']))
    bp=a.finish(base['versions'],ingredients(a));verify(bp);return bp

def ingredients(a):
    """Recipe-based native costs, including variable belt/lift/wire lengths."""
    catalog=json.loads((n.ROOT/'data'/'native-build-costs.json').read_text(encoding='utf-8'));cost={};refs={}
    for h,o in zip(a.headers,a.objects):
        if not isinstance(h,n.sav_parse.ActorHeader):continue
        recipe=prop(o,'mBuiltWithRecipe').pathName.rsplit('.',1)[-1];factor=1
        if 'ConveyorBelt' in h.typePath:
            points=prop(o,'mSplineData');length=0.
            for p0,p1 in zip(points,points[1:]):
                v0=dict(p0[0]);v1=dict(p1[0]);prev=v0['Location']
                for i in range(1,101):
                    t=i/100;pt=[(2*t**3-3*t*t+1)*v0['Location'][j]+(t**3-2*t*t+t)*v0['LeaveTangent'][j]+(-2*t**3+3*t*t)*v1['Location'][j]+(t**3-t*t)*v1['ArriveTangent'][j] for j in range(3)];length+=math.dist(prev,pt);prev=pt
            factor=math.ceil((length-.01)/200)
        elif 'ConveyorLift' in h.typePath:factor=math.ceil((abs(dict(prop(o,'mTopTransform')[0])['Translation'][2])-.01)/200)
        elif 'PowerLine.' in h.typePath:factor=math.ceil((prop(o,'mCachedLength')-.01)/2500)
        for quantity,path in catalog[recipe]:cost[path]=cost.get(path,0)+quantity*factor
    return [[v,n.sav_parse.ObjectReference('',k)] for k,v in sorted(cost.items())]

def verify(bp):
    by=check_graph(bp);actors=[(h,o) for h,o in zip(bp[2],bp[3]) if isinstance(h,n.sav_parse.ActorHeader)]
    count=lambda text:sum(text+'.' in h.typePath for h,o in actors)
    for kind,number in [('Build_SmelterMk1',4),('Build_ConstructorMk1',8),('Build_AssemblerMk1',2),('Build_StorageContainerMk1',1),('Build_Foundation_Concrete_8x1',48),('Build_FoundationPassthrough_Lift',6),('Build_ConveyorLiftMk2',12)]:
        if count(kind)!=number:raise ValueError('Nombre incorrect : '+kind)
    recipes={}
    for h,o in actors:
        r=prop(o,'mCurrentRecipe')
        if r:recipes[r.pathName.rsplit('.',1)[-1]]=recipes.get(r.pathName.rsplit('.',1)[-1],0)+1
        if any(abs(v)>1600.01 for v in h.position[:2]):raise ValueError('Origine hors du 4x4')
        if 'Foundation_Concrete' in h.typePath and (abs(h.position[0])+400>1600 or abs(h.position[1])+400>1600):raise ValueError('Fondation hors du plan')
        if 'Passthrough' in h.typePath:
            for key in ['mBottomSnappedConnection','mTopSnappedConnection']:
                ref=prop(o,key);owner=by[ref.pathName.rsplit('.',1)[0]];snapped=prop(owner[1],'mSnappedPassthroughs')
                if not any(v.pathName==h.instanceName for v in snapped):raise ValueError('Traversée non réciproque')
        if r or 'StorageContainerMk1.' in h.typePath:
            custom=dict(prop(o,'mCustomizationData')[0]);colors=dict(custom['OverrideColorData'][0])
            if colors['PrimaryColor']!=[0.,0.,0.,1.] or colors['SecondaryColor']!=[0.,0.,0.,1.]:raise ValueError('Personnalisation noire absente')
    if recipes!={'Recipe_IngotIron_C':4,'Recipe_IronRod_C':2,'Recipe_IronPlate_C':3,'Recipe_Screw_C':3,'Recipe_IronPlateReinforced_C':2}:raise ValueError('Bilan de recettes incorrect : '+str(recipes))
    verify_connections(bp,by)
    power={};powered=[]
    for h,o in actors:
        if prop(o,'mCurrentRecipe'):powered.append(h.instanceName)
        if 'PowerLine.' in h.typePath:
            source,target=[r.pathName.rsplit('.',1)[0] for r in o[4]]
            power.setdefault(source,set()).add(target);power.setdefault(target,set()).add(source)
            for ref in o[4]:
                wires=dict(by[ref.pathName][1][0]).get('mWires',[])
                if not any(r.pathName==h.instanceName for r in wires):raise ValueError('Câble électrique non réciproque')
    seen=set();pending=[powered[0]]
    while pending:
        current=pending.pop()
        if current in seen:continue
        seen.add(current);pending.extend(power.get(current,[]))
    if not set(powered)<=seen:raise ValueError('Réseau électrique interrompu')
    for h,o in zip(bp[2],bp[3]):
        if isinstance(h,n.sav_parse.ComponentHeader) and h.instanceName.endswith('.PowerConnection') and 'PowerPoleMk1' in h.parentActorName:
            if len(dict(o[0]).get('mWires',[]))>4:raise ValueError('Poteau saturé')
    return {'actors':len(actors),'components':len(bp[2])-len(actors),'inputPerMinute':120,'outputPerMinute':10,'powerMW':78,'floors':[1,10.5,20],'footprintMeters':[32,32],'inGameValidated':False}

def verify_connections(bp,by):
    def endpoint(name):
        owner,suffix=name.rsplit('.',1);h,o=by[owner];kind=h.typePath
        if 'ConveyorBelt' in kind:
            offset=dict(prop(o,'mSplineData')[0 if suffix=='ConveyorAny0' else -1][0])['Location']
        elif 'ConveyorLift' in kind:offset=[0,0,0] if suffix=='ConveyorAny0' else dict(prop(o,'mTopTransform')[0])['Translation']
        elif 'Smelter' in kind:offset=[0,-300,100] if suffix=='Input0' else [0,200,100]
        elif 'Constructor' in kind:offset=OFF[suffix]
        elif 'Assembler' in kind:offset={'Input0':[200,-600,100],'Input1':[-200,-600,100],'Output0':[0,500,100]}[suffix]
        elif 'StorageContainer' in kind:offset=[0,-400 if suffix=='Input0' else 400,100]
        else:offset=OFF[suffix]
        return [a+b for a,b in zip(h.position,rotate(h.rotation,offset))]
    for h,o in zip(bp[2],bp[3]):
        if not isinstance(h,n.sav_parse.ComponentHeader):continue
        r=dict(o[0]).get('mConnectedComponent')
        if r and math.dist(endpoint(h.instanceName),endpoint(r.pathName))>1:raise ValueError('Extrémité convoyeur décalée : '+h.instanceName)
    # Production bounds include the constructor's aerial/power mast and assembler antenna.
    boxes=[]
    for h,o in zip(bp[2],bp[3]):
        if not isinstance(h,n.sav_parse.ActorHeader):continue
        kind=h.typePath
        dims=([250,500,850] if 'SmelterMk1.' in kind else [400,500,850] if 'ConstructorMk1.' in kind else [450,850,1075] if 'AssemblerMk1.' in kind else None)
        if not dims:continue
        corners=[rotate(h.rotation,[x*dims[0],y*dims[1],0]) for x in [-1,1] for y in [-1,1]]
        lo=[h.position[j]+min(v[j] for v in corners) for j in [0,1]]+[h.position[2]]
        hi=[h.position[j]+max(v[j] for v in corners) for j in [0,1]]+[h.position[2]+dims[2]]
        if lo[2]<-.01 or lo[0]<-1600-.01 or lo[1]<-1600-.01 or hi[0]>1600+.01 or hi[1]>1600+.01 or hi[2]>3200+.01:raise ValueError('Machine hors du volume 32 m')
        for z in Z:
            if lo[2]<z-100-.01 and hi[2]>z-100+.01:raise ValueError('Machine traversant le plafond')
        for otherlo,otherhi in boxes:
            if all(min(hi[j],otherhi[j])-max(lo[j],otherlo[j])>.01 for j in range(3)):raise ValueError('Machines qui se chevauchent')
        boxes.append((lo,hi))
    # Follow physical connections from each output to the next production stage.
    def outputs(h):
        if 'ConveyorBelt' in h.typePath or 'ConveyorLift' in h.typePath:return ['ConveyorAny1']
        if 'AttachmentSplitter' in h.typePath:return ['Output1','Output2','Output3']
        if 'AttachmentMerger' in h.typePath:return ['Output1']
        return []
    def downstream(component,visited=None):
        visited=set() if visited is None else visited
        if component in visited:return set()
        visited.add(component);c=by.get(component)
        r=dict(c[1][0]).get('mConnectedComponent') if c else None
        if not r:return set()
        h,o=by[r.pathName.rsplit('.',1)[0]];recipe=prop(o,'mCurrentRecipe')
        if recipe:return {recipe.pathName.rsplit('.',1)[-1]}
        if 'StorageContainerMk1.' in h.typePath:return {'STORAGE'}
        result=set()
        for suffix in outputs(h):result|=downstream(h.instanceName+'.'+suffix,visited)
        return result
    expected={'Recipe_IngotIron_C':{'Recipe_IronRod_C','Recipe_IronPlate_C'},'Recipe_IronRod_C':{'Recipe_Screw_C'},'Recipe_IronPlate_C':{'Recipe_IronPlateReinforced_C'},'Recipe_Screw_C':{'Recipe_IronPlateReinforced_C'},'Recipe_IronPlateReinforced_C':{'STORAGE'}}
    for h,o in zip(bp[2],bp[3]):
        if not isinstance(h,n.sav_parse.ActorHeader):continue
        recipe=prop(o,'mCurrentRecipe')
        if not recipe:continue
        required=['Input0','Input1'] if 'Assembler' in h.typePath else ['Input0']
        for suffix in required:
            if not dict(by[h.instanceName+'.'+suffix][1][0]).get('mConnectedComponent'):raise ValueError('Entrée machine non connectée')
        key=recipe.pathName.rsplit('.',1)[-1];out='Output2' if 'Smelter' in h.typePath else 'Output0'
        dest=downstream(h.instanceName+'.'+out)
        if not dest or not dest<=expected[key]:raise ValueError('Chaîne physique interrompue ou mauvaise destination : '+key)
    for h,o in zip(bp[2],bp[3]):
        if not isinstance(h,n.sav_parse.ActorHeader) or 'ConveyorBelt' not in h.typePath:continue
        for i in [0,1]:
            c=by[h.instanceName+'.ConveyorAny'+str(i)];ref=dict(c[1][0]).get('mConnectedComponent')
            if not ref:raise ValueError('Convoyeur non raccordé')
            owner,suffix=ref.pathName.rsplit('.',1);th,to=by[owner];kind=th.typePath
            if 'ConveyorLift' in kind:
                local=[-1,0,0] if suffix=='ConveyorAny0' else [1,0,0]
                if suffix=='ConveyorAny1':local=rotate(dict(prop(to,'mTopTransform')[0])['Rotation'],local)
            elif 'AttachmentSplitter' in kind:local={'Input1':[1,0,0],'Output1':[1,0,0],'Output2':[0,1,0],'Output3':[0,-1,0]}[suffix]
            elif 'AttachmentMerger' in kind:local={'Input1':[1,0,0],'Input2':[0,-1,0],'Input3':[0,1,0],'Output1':[1,0,0]}[suffix]
            else:local=[0,1,0]
            expected_direction=rotate(th.rotation,local);spline=dict(prop(o,'mSplineData')[0 if i==0 else -1][0]);tangent=rotate(h.rotation,spline['LeaveTangent' if i==0 else 'ArriveTangent']);length=math.hypot(*tangent[:2])
            if length<.001 or sum(tangent[j]*expected_direction[j] for j in [0,1])/length<.99:raise ValueError('Convoyeur entrant ou sortant dans le mauvais sens')


