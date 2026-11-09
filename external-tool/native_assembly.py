"""Native actor assembly helpers for fixed integration test modules."""
import copy,math,os
import native_blueprint as n
from native_connected import prop,set_component,add

def rotate(q,v):
    x,y,z,w=q;a,b,c=v
    return [(1-2*y*y-2*z*z)*a+(2*x*y-2*z*w)*b+(2*x*z+2*y*w)*c,(2*x*y+2*z*w)*a+(1-2*x*x-2*z*z)*b+(2*y*z-2*x*w)*c,(2*x*z-2*y*w)*a+(2*y*z+2*x*w)*b+(1-2*x*x-2*y*y)*c]

class Assembly:
    def __init__(self,extra):
        self.extra=extra;self.headers=[];self.objects=[];self.serial=int.from_bytes(os.urandom(4),'little')
    def clone(self,piece,position,rotation=None):
        hs=copy.deepcopy(piece['headers']);obs=copy.deepcopy(piece['objects']);old=hs[0].instanceName
        self.serial=(self.serial+1)%2**32;new=old.rsplit('_',1)[0]+'_'+str(self.serial)
        for h in hs:
            h.instanceName=h.instanceName.replace(old,new)
            if isinstance(h,n.sav_parse.ComponentHeader):h.parentActorName=new
        for ref in n.references(obs):ref.pathName=ref.pathName.replace(old,new)
        hs[0].position=list(position);hs[0].rotation=list(rotation or [0.0,0.0,0.0,1.0]);self.headers.extend(hs);self.objects.extend(obs)
        return hs[0],obs[0]
    def component(self,actor,suffix):
        name=actor[0].instanceName+'.'+suffix;i=next(i for i,h in enumerate(self.headers) if h.instanceName==name)
        return name,self.objects[i]
    @staticmethod
    def ref(name):return n.sav_parse.ObjectReference('Persistent_Level',name)
    def connect(self,a,b):
        set_component(a[1],'mConnectedComponent',self.ref(b[0]),['ObjectProperty',0]);set_component(b[1],'mConnectedComponent',self.ref(a[0]),['ObjectProperty',0])
    def port(self,actor,offset):return add(actor[0].position,rotate(actor[0].rotation,offset))
    def belt(self,start,end,source,target):
        actor=self.clone(self.extra['belt'],start);delta=[end[i]-start[i] for i in range(3)];length=math.dist(start,end);direction=[v/length for v in delta]
        for idx,point in enumerate(prop(actor[1],'mSplineData')):
            for entry in point[0]:
                if entry[0]=='Location':entry[1]=[0.0,0.0,0.0] if idx==0 else delta
                elif entry[0]=='ArriveTangent':entry[1]=direction if idx==0 else [v*length/2 for v in direction]
                elif entry[0]=='LeaveTangent':entry[1]=[v*length/2 for v in direction] if idx==0 else direction
        for suffix,peer in [('ConveyorAny0',source),('ConveyorAny1',target)]:
            component=self.component(actor,suffix)
            if peer:self.connect(component,peer)
            else:
                component[1][0][:]=[row for row in component[1][0] if row[0]!='mConnectedComponent']
                component[1][1][:]=[row for row in component[1][1] if row[0]!='mConnectedComponent']
        return actor
    def wire(self,source,target,source_pos,target_pos):
        actor=self.clone(self.extra['wire'],source_pos);actor[1][4]=[self.ref(source[0]),self.ref(target[0])]
        for c in [source,target]:
            refs=next((v for k,v in c[1][0] if k=='mWires'),[])
            set_component(c[1],'mWires',refs+[self.ref(actor[0].instanceName)],['ArrayProperty',0,'ObjectProperty',0])
        relative=[target_pos[i]-source_pos[i] for i in range(3)];locations=iter([source_pos,target_pos]);cached=iter([[0.0,0.0,0.0],relative])
        for entry in prop(actor[1],'mWireInstances')[0][0]:
            if entry[0]=='Locations':entry[1]=next(locations)
            elif entry[0]=='CachedRelativeLocations':entry[1]=next(cached)
        for p in actor[1][2]:
            if p[0]=='mCachedLength':p[1]=math.dist(source_pos,target_pos)
        return actor
    def finish(self,versions,ingredients):
        recipes=[]
        for h,o in zip(self.headers,self.objects):
            if isinstance(h,n.sav_parse.ActorHeader):
                r=prop(o,'mBuiltWithRecipe')
                if r.pathName not in [a.pathName for a in recipes]:recipes.append(copy.deepcopy(r))
        return [copy.deepcopy(versions),[4,copy.deepcopy(ingredients),recipes],self.headers,self.objects]


def check_graph(bp):
    if isinstance(bp,str):raise ValueError('Blueprint illisible : '+bp)
    if len(bp[2])!=len(bp[3]) or not ((type(bp[1][0])is int and 1<=bp[1][0]<=64)or(isinstance(bp[1][0],(list,tuple))and len(bp[1][0])==3 and all(type(v)is int and 1<=v<=64 for v in bp[1][0]))):raise ValueError('Structure native invalide.')
    by={h.instanceName:(h,o) for h,o in zip(bp[2],bp[3])};names=set(by)
    if len(names)!=len(bp[2]):raise ValueError('Identifiants natifs dupliqués.')
    for h,o in zip(bp[2],bp[3]):
        if isinstance(h,n.sav_parse.ComponentHeader):
            if h.parentActorName not in names:raise ValueError('Composant orphelin.')
            r=dict(o[0]).get('mConnectedComponent')
            if r:
                if r.pathName not in names:raise ValueError('Port absent.')
                back=dict(by[r.pathName][1][0]).get('mConnectedComponent')
                if not back or back.pathName!=h.instanceName:raise ValueError('Raccord non réciproque.')
        else:
            for ref in o[1]:
                if ref.pathName not in names:raise ValueError('Composant absent de son acteur.')
    for ref in n.references(bp[3]):
        if ref.levelName=='Persistent_Level' and ref.pathName not in names and ref.pathName!='Persistent_Level:PersistentLevel.BuildableSubsystem':raise ValueError('Référence externe inattendue.')
    return by
