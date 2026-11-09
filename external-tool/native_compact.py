"""Calibrated pair modules, physical workshop scene and native scene exporter.

The first supported chain is 120 iron -> 10 reinforced plates. No world is read
or written here. Pair internals retain their measured native head transforms.
"""
import copy,json,math
from blueprint_dimensions import dimensions,header_dimensions,experimental
from functools import lru_cache
import native_blueprint as n
from native_assembly import Assembly,rotate,check_graph
from native_connected import prop
from native_factory import q,aset

PROFILE='iron-plates-pairs-v1'
def mul(a,b):
 x,y,z,w=a;X,Y,Z,W=b
 return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
def inv(a):return [-a[0],-a[1],-a[2],a[3]]
def local(actor,world):return rotate(inv(actor[0].rotation),[world[i]-actor[0].position[i] for i in range(3)])
def piece(bp,owner):
 names={h.instanceName for h in bp[2] if h.instanceName==owner or getattr(h,'parentActorName',None)==owner}
 rows=[(copy.deepcopy(h),copy.deepcopy(o)) for h,o in zip(bp[2],bp[3]) if h.instanceName in names]
 for h,o in rows:
  ps,ts=(o[2],o[3]) if isinstance(h,n.sav_parse.ActorHeader) else (o[0],o[1])
  for i in range(len(ps)-1,-1,-1):
   key,value=ps[i]
   if key in ['mConnectedComponent','mWires','mBlueprintProxy','mCircuitID','mHasPower','mIsProducing','mManufacturingProgress'] or any(r.levelName=='Persistent_Level' and r.pathName not in names and not r.pathName.endswith('BuildableSubsystem') for r in n.references(value)):
    ps.pop(i);ts.pop(i)
  def empty(v):
   if isinstance(v,list):
    if len(v)==2 and v[0]=='NumItems':v[1]=0
    if len(v)==2 and v[0]=='Item' and isinstance(v[1],list):v[1][0]=''
    for x in v:empty(x)
  empty(ps)
 return {'headers':[h for h,o in rows],'objects':[o for h,o in rows]}

@lru_cache(maxsize=8)
def canonical(pitch=0,clearance=0):
 rise1=(max(10.8,pitch)+clearance-10.8)*100;rise2=rise1+(max(8,pitch)+clearance-8)*100
 import native_project as p
 sources=n.decode(json.loads((n.ROOT/'data/compact-native-sources.json').read_text(encoding='utf-8')))
 base=p.load('native-test-template.json');extra=p.load('native-connected-template.json');pieces=p.load('native-factory-template.json');vertical=p.load('native-vertical-template.json')['lift']
 a=Assembly(extra);groups={};powerpoints={};labels={};modules=[]
 def record(actor,group,label):groups[actor[0].instanceName]=group;labels[actor[0].instanceName]={'splitter':'Répartiteur','merger':'Fusionneur','lift':'Élévateur natif','wallPole':'Raccord mural'}.get(label,label);return actor
 def node(kind,x,y,z,angle=0,label=None):return record(a.clone(pieces[kind],[x,y,z],q(angle)),'interconnect',label or kind)
 def end(actor,suffix,offset=None):
  if offset is None:offset=next(v for side in p.PORTS[kindof(actor)].values() for key,v,d in side if key==suffix)
  return a.component(actor,suffix),a.port(actor,offset)
 def belt(src,dst,points=None):
  points=points or [src[1],dst[1]];spans=p.spline(points)
  if not spans:raise ValueError('Courbe compacte impossible : '+str(points))
  return p.native_belt(a,spans,src[0],dst[0],2,json.loads((n.ROOT/'data/native-assets.json').read_text(encoding='utf-8')))
 def pair(kind,x,z,angle,recipe,clock,group,flip_merge=False):
  bp=sources[kind]['blueprint'];by={h.instanceName:(h,o) for h,o in zip(bp[2],bp[3])};actors=[(h,o) for h,o in zip(bp[2],bp[3]) if isinstance(h,n.sav_parse.ActorHeader)]
  center=next(h.position for h,o in actors if 'AttachmentSplitter.' in h.typePath);origin=[center[0],center[1],0];rotation=q(angle);mapping={}
  transform=lambda pos:[v+w for v,w in zip([x,0,z],rotate(rotation,[pos[i]-origin[i] for i in range(3)]))]
  merge_name=next(h.instanceName for h,o in actors if 'AttachmentMerger.' in h.typePath)
  for h,o in actors:
   if 'PowerLine.' in h.typePath:continue
   clone=a.clone(piece(bp,h.instanceName),transform(h.position),mul(rotation,h.rotation));record(clone,group,kindof(clone));mapping[h.instanceName]=clone
   if kindof(clone) in ['smelter','constructor']:
    aset(clone,'mCurrentRecipe',p.ref(json.loads((n.ROOT/'data/native-assets.json').read_text(encoding='utf-8'))[recipe]['path']),['ObjectProperty',0])
    for key in ['mCurrentPotential','mPendingPotential']:aset(clone,key,clock,['FloatProperty',0])
  if flip_merge:mapping[merge_name][0].rotation=mul(q(180),mapping[merge_name][0].rotation)
  def component(owner,suffix):return a.component(mapping[owner],{'Input2':'Input3','Input3':'Input2'}.get(suffix,suffix) if flip_merge and owner==merge_name else suffix)
  for h,o in actors:
   if 'PowerLine.' in h.typePath:
    cached=[v for k,v in prop(o,'mWireInstances')[0][0] if k=='CachedRelativeLocations'];positions=[transform([h.position[i]+rotate(h.rotation,v)[i] for i in range(3)]) for v in cached]
    ends=[]
    for ref,pos in zip(o[4],positions):
     owner,suffix=ref.pathName.rsplit('.',1);target=mapping[owner];ends.append(a.component(target,suffix));powerpoints[target[0].instanceName]=pos
    a.wire(*ends,*positions)
   else:
    for ref in o[1]:
     ch,co=by[ref.pathName];other=dict(co[0]).get('mConnectedComponent')
     if other:
      owner,suffix=other.pathName.rsplit('.',1)
      if owner in mapping:a.connect(component(h.instanceName,ref.pathName.rsplit('.',1)[-1]),component(owner,suffix))
  splitter=next(v for v in mapping.values() if kindof(v)=='splitter');merger=next(v for v in mapping.values() if kindof(v)=='merger');wall=next(v for v in mapping.values() if kindof(v)=='wallPole')
  modules.append({'id':group,'source':kind,'recipe':recipe,'clock':clock,'input':splitter[0].instanceName,'output':merger[0].instanceName})
  return splitter,merger,wall
 def lift(x,y,low,high,entry,exit,label):
  # A native lift receives along local -X and emits along top-local +X.
  actor=record(a.clone(vertical,[x,y,low],q(entry+180)),'interconnect',label)
  aset(actor,'mTopTransform',[[['Rotation',q(exit-entry-180)],['Translation',[0.,0.,high-low]]],[['Rotation','StructProperty',0,'Quat',None,0],['Translation','StructProperty',0,'Vector',None,0]]],['StructProperty',0,'Transform',None,0])
  actor[0].typePath=actor[0].typePath.replace('Mk1','Mk2');prop(actor[1],'mBuiltWithRecipe').pathName=prop(actor[1],'mBuiltWithRecipe').pathName.replace('Mk1','Mk2')
  return end(actor,'ConveyorAny0',[0,0,0]),end(actor,'ConveyorAny1',[0,0,high-low])
 sm=[pair('smelter',x,100,0,'Recipe_IngotIron_C',1,'smelter-'+str(i)) for i,x in enumerate([-1100,-500])]
 rods=pair('constructor',700,100,0,'Recipe_IronRod_C',1,'rods')
 plates=[pair('constructor',x,(1180+rise1),180,'Recipe_IronPlate_C',.75,'plates-'+str(i)) for i,x in enumerate([-400,-1200])]
 screws=[pair('constructor',x,(1180+rise1),180,'Recipe_Screw_C',.75,'screws-'+str(i),True) for i,x in enumerate([1200,400])]
 belt(end(sm[0][0],'Output1'),end(sm[1][0],'Input1'))
 belt(end(sm[0][1],'Output1'),end(sm[1][1],'Input1'))
 ingots=node('splitter',-100,0,1000,label='Répartition des lingots · 90 / 30')
 belt(end(sm[1][1],'Output1'),end(ingots,'Input1'))
 lo,hi=lift(200,0,1000,(1280+rise1),0,180,'Lingots → plaques')
 belt(end(ingots,'Output1'),lo);belt(hi,end(plates[0][0],'Input1'))
 belt(end(plates[0][0],'Output1'),end(plates[1][0],'Input1'))
 lo,hi=lift(-100,-300,1000,200,-90,90,'Lingots → tiges · descente')
 belt(end(ingots,'Output3'),lo)
 dst=end(rods[0],'Input1');belt(hi,dst,[hi[1],[-100,0,200],dst[1]])
 # Rod output rises in the empty central aisle, then feeds the screw pair bus.
 lo,hi=lift(1500,0,700,(1280+rise1),0,180,'Tiges → vis')
 belt(end(rods[1],'Output1'),lo)
 belt(hi,end(screws[0][0],'Input1'))
 belt(end(screws[0][0],'Output1'),end(screws[1][0],'Input1'))
 belt(end(plates[0][1],'Output1'),end(plates[1][1],'Input1'))
 belt(end(screws[1][1],'Output1'),end(screws[0][1],'Input1'))
 # Independent assembly buses, separated vertically by three metres.
 ps=node('splitter',0,-1200,(2080+rise2),90,'Plaques → assemblage')
 ss=node('splitter',-500,-1200,(2380+rise2),90,'Vis → assemblage · bus haut')
 for group,x,high,target in [(plates,-1500,(2080+rise2),ps),(screws,1500,(2380+rise2),ss)]:
  lo,hi=lift(x,0,(1780+rise1),high,180 if x<0 else 0,-90,'Collecte → assemblage')
  belt(end(group[1 if x<0 else 0][1],'Output1'),lo);dst=end(target,'Input1')
  belt(hi,dst,[hi[1],[x,-1500,high],[target[0].position[0],-1500,high],dst[1]])
 assemblers=[]
 for i,x in enumerate([-700,700]):
  machine=node('assembler',x,-300,(1980+rise2),label='Plaques renforcées · 5/min');assemblers.append(machine)
  plate_port='Input0' if i==0 else 'Input1';screw_port='Input1' if i==0 else 'Input0';plate_x=x+200 if i==0 else x-200;screw_x=x-200 if i==0 else x+200
  belt(end(ps,'Output2' if i==0 else 'Output3'),end(machine,plate_port),[end(ps,'Output2' if i==0 else 'Output3')[1],[plate_x,-1200,(2080+rise2)],end(machine,plate_port)[1]])
  lo,hi=lift(screw_x,-1200,(2380+rise2),(2080+rise2),180 if i==0 else 0,90,'Vis → assembleuse · descente')
  src=end(ss,'Output2' if i==0 else 'Output3')
  belt(src,lo);belt(hi,end(machine,screw_port))
 final=node('merger',0,400,(2080+rise2),90,'Plaques renforcées · 10/min')
 for i,machine in enumerate(assemblers):
  src=end(machine,'Output0');dst=end(final,'Input2' if i==0 else 'Input3');belt(src,dst,[src[1],[machine[0].position[0],400,(2080+rise2)],dst[1]])
 storage=node('storage',0,1050,(1980+rise2),label='Coffre · plaques renforcées');belt(end(final,'Output1'),end(storage,'Input0'))
 walls=[v[2] for v in sm]+[rods[2]]+[v[2] for v in plates]+[v[2] for v in screws]
 for i,machine in enumerate(assemblers):
  pole=record(a.clone(extra['pole'],[-1400 if i==0 else 1400,700,(1980+rise2)]),'assembly-power','Poteau assembleuse')
  powerpoints[pole[0].instanceName]=a.port(pole,[0,0,700]);powerpoints[machine[0].instanceName]=a.port(machine,[175,-60,1030]);walls.append(pole)
  a.wire(a.component(pole,'PowerConnection'),a.component(machine,'PowerInput'),powerpoints[pole[0].instanceName],powerpoints[machine[0].instanceName])
 for left,right in zip(walls,walls[1:]):a.wire(a.component(left,'PowerConnection'),a.component(right,'PowerConnection'),powerpoints[left[0].instanceName],powerpoints[right[0].instanceName])
 bp=a.finish(base['versions'],[]);check_graph(bp)
 return bp,groups,labels,modules,sources

def kindof(actor):
 path=actor[0].typePath
 for needle,kind in [('SmelterMk1.','smelter'),('ConstructorMk1.','constructor'),('AssemblerMk1.','assembler'),('AttachmentSplitter.','splitter'),('AttachmentMerger.','merger'),('StorageContainerMk1.','storage'),('ConveyorLift','lift'),('PowerPoleWall.','wallPole'),('PowerPoleMk1.','pole'),('ConveyorBelt','belt'),('PowerLine.','power')]:
  if needle in path:return kind
 raise ValueError('Type compact inconnu : '+path)

def endpoints(bp):
 import native_project as p
 by=check_graph(bp);points={}
 for h,o in zip(bp[2],bp[3]):
  if not isinstance(h,n.sav_parse.ActorHeader):continue
  actor=(h,o);kind=kindof(actor)
  if kind in p.PORTS:
   for side in p.PORTS[kind].values():
    for key,v,d in side:points[h.instanceName+'.'+key]=[x+y for x,y in zip(h.position,rotate(h.rotation,v))]
  if kind=='belt':
   for i,row in [(0,prop(o,'mSplineData')[0]),(1,prop(o,'mSplineData')[-1])]:points[h.instanceName+'.ConveyorAny'+str(i)]=[x+y for x,y in zip(h.position,rotate(h.rotation,dict(row[0])['Location']))]
  if kind=='power':
   locs=[v for k,v in prop(o,'mWireInstances')[0][0] if k=='Locations']
   for ref,loc in zip(o[4],locs):points[ref.pathName]=loc
 # Native snapped lift heads are calibrated against their known source pair.
 for h,o in zip(bp[2],bp[3]):
  if isinstance(h,n.sav_parse.ActorHeader) and kindof((h,o))=='lift':
   top=dict(prop(o,'mTopTransform')[0])['Translation']
   for i,offset in [(0,[0,0,0]),(1,top)]:
    name=h.instanceName+'.ConveyorAny'+str(i);other=dict(by[name][1][0]).get('mConnectedComponent')
    points[name]=points.get(other.pathName) if other and other.pathName in points else [x+y for x,y in zip(h.position,rotate(h.rotation,offset))]
 return points

@lru_cache(maxsize=8)
def atlas(pitch=0,clearance=0,profile=PROFILE):
 flat=profile=='iron-plates-blocks-flat-v1'
 if flat:
  import native_blocks
  bp,groups,labels,modules,sources=native_blocks.canonical(clearance)
 else:bp,groups,labels,modules,sources=canonical(pitch,clearance)
 base_size=40+8*clearance if flat else 32
 points=endpoints(bp);prototypes=[];owner_to_id={};by=check_graph(bp)
 objects=[]
 dims={'smelter':(5,10,8.5),'constructor':(8,10,6),'assembler':(9,17,10.75),'storage':(5,11,4),'splitter':(2,2,1.2),'merger':(2,2,1.2),'lift':(1,1,1),'wallPole':(.6,.6,.6),'pole':(1,1,7)}
 for h,o in zip(bp[2],bp[3]):
  if not isinstance(h,n.sav_parse.ActorHeader):continue
  actor=(h,o);kind=kindof(actor)
  if kind in ['belt','power']:continue
  i=len(prototypes);oid='compact-'+str(i);owner_to_id[h.instanceName]=oid;w,d,height=dims[kind];z=h.position[2]/100
  yaw=math.degrees(math.atan2(2*(h.rotation[3]*h.rotation[2]+h.rotation[0]*h.rotation[1]),1-2*(h.rotation[1]**2+h.rotation[2]**2)));uirot=round((yaw-(-90 if kind in ['splitter','merger'] else 180))/90)*90%360
  if kind in ['splitter','merger']:z-=1
  if kind=='lift':
   top=[x+y for x,y in zip(h.position,rotate(h.rotation,dict(prop(o,'mTopTransform')[0])['Translation']))];z=min(h.position[2],top[2])/100;height=abs(top[2]-h.position[2])/100+.5
  r=prop(o,'mCurrentRecipe');recipe=r.pathName.rsplit('.',1)[-1] if r else None
  z=round(z,5)
  obj={'id':oid,'type':kind,'name':labels[h.instanceName],'x':round(h.position[0]/100+base_size/2,5),'y':round(h.position[1]/100+base_size/2,5),'z':z,'w':w,'d':d,'h':round(height,5),'rotation':uirot,'clock':prop(o,'mCurrentPotential',1),'recipe':recipe,'native':{'prototype':i,'module':groups[h.instanceName]}}
  if recipe:obj['name']={'Recipe_IngotIron_C':'Lingots de fer','Recipe_IronRod_C':'Tiges de fer','Recipe_IronPlate_C':'Plaques de fer · 75 %','Recipe_Screw_C':'Vis · 75 %','Recipe_IronPlateReinforced_C':'Plaques renforcées · 5/min'}[recipe]
  ports={key.rsplit('.',1)[-1]:local(actor,value) for key,value in points.items() if key.startswith(h.instanceName+'.')}
  obj['native'].update({'rotation':uirot,'quaternion':h.rotation,'originZ':h.position[2]/100-z,'ports':{key:[v/100 for v in value] for key,value in ports.items()}})
  if kind=='assembler':obj['native']['inputItems']={'Input0':'Desc_IronPlate_C' if flat or h.position[0]<0 else 'Desc_IronScrew_C','Input1':'Desc_IronScrew_C' if flat or h.position[0]<0 else 'Desc_IronPlate_C'}
  objects.append(obj);prototypes.append({'piece':piece(bp,h.instanceName),'object':obj,'actor':actor,'ports':ports})
 links=[]
 for h,o in zip(bp[2],bp[3]):
  if not isinstance(h,n.sav_parse.ActorHeader):continue
  kind=kindof((h,o))
  if kind=='belt':
   refs=[dict(by[h.instanceName+'.ConveyorAny'+str(i)][1][0])['mConnectedComponent'].pathName for i in [0,1]];source,sp=refs[0].rsplit('.',1);target,tp=refs[1].rsplit('.',1)
   if kindof(by[source])=='belt':continue
   actor=by[source];segments=[(h,o)];visited={h.instanceName}
   while kindof(by[target])=='belt':
    if target in visited:raise ValueError('Boucle de convoyeurs sans machine.')
    visited.add(target);bh,bo=by[target];segments.append((bh,bo));peer=dict(by[target+'.ConveyorAny1'][1][0])['mConnectedComponent'].pathName;target,tp=peer.rsplit('.',1)
   spans=[]
   for bh,bo in segments:
    rows=[dict(row[0]) for row in prop(bo,'mSplineData')]
    for x,y in zip(rows,rows[1:]):
     world=lambda v:[a+b for a,b in zip(bh.position,rotate(bh.rotation,v))]
     spans.append([[v/100 for v in local(actor,world(x['Location']))],[v/100 for v in local(actor,world(y['Location']))],[v/100 for v in rotate(inv(actor[0].rotation),rotate(bh.rotation,x['LeaveTangent']))],[v/100 for v in rotate(inv(actor[0].rotation),rotate(bh.rotation,y['ArriveTangent']))]])
   links.append({'kind':'belt','from':owner_to_id[source],'to':owner_to_id[target],'capacity':120,'native':{'fromPort':sp,'toPort':tp,'spans':spans}})
  elif kind=='power':
   left,right=[r.pathName.rsplit('.',1)[0] for r in o[4]];links.append({'kind':'power','from':owner_to_id[left],'to':owner_to_id[right]})
 # Directly attached machine/lift connections remain native snaps, not missing belts.
 for obj,proto in zip(objects,prototypes):
  h,o=proto['actor']
  for ref in o[1]:
   component=by[ref.pathName];other=dict(component[1][0]).get('mConnectedComponent')
   if other:
    owner,suffix=other.pathName.rsplit('.',1);own_suffix=ref.pathName.rsplit('.',1)[-1]
    if owner in owner_to_id and (own_suffix.startswith('Output') or(obj['type']=='lift' and own_suffix=='ConveyorAny1')):
     links.append({'kind':'belt','from':obj['id'],'to':owner_to_id[owner],'capacity':120,'native':{'fromPort':own_suffix,'toPort':suffix,'snap':True}})
 project={'schemaVersion':2,'kind':'factory-tools-paper-blueprint','id':'compact-iron-plates','name':'Plaques renforcées · paires compactes','size':32,'objects':objects,'buffer':[],'links':links,'flows':{'inputs':[{'id':'Desc_OreIron_C','rate':120}],'outputs':[{'id':'Desc_IronPlateReinforced_C','rate':10}]},'nativeProfile':PROFILE,'powerStyle':'per-module','structure':{'gap':4,'pitch':12,'thickness':1,'material':'concrete','color':'#536454'},'floors':[{'z':z,'thickness':1,'material':'concrete','color':'#536454','shaft':2,'profile':profile} for z,profile in [(0,'solid'),(max(10.8,pitch)+clearance,'frame'),(max(10.8,pitch)+max(8,pitch)+clearance*2,'frame')]],'layoutInfo':{'name':'Paires calibrées · 3 niveaux · cadres ajourés','sources':{k:v['sha256'] for k,v in sources.items()},'machineCount':16,'inputRate':120,'outputRate':10}}
 project['layoutInfo']['input']={'objectId':owner_to_id[modules[0]['input']],'port':'Input1','rate':120,'label':'120 minerais/min'}
 project['layoutInfo']['output']={'objectId':owner_to_id[next(h.instanceName for h,o in zip(bp[2],bp[3]) if isinstance(h,n.sav_parse.ActorHeader) and 'StorageContainerMk1.' in h.typePath)],'rate':10,'label':'10 plaques renforcées/min'}
 if flat:
  project.update(size=base_size,nativeProfile=profile)
  project['floors']=project['floors'][:1]
  project['flows']['inputs'][0]['rate']=60;project['flows']['outputs'][0]['rate']=5
  project['layoutInfo'].update(name='Blocs natifs · collecte haute · un étage',machineCount=8,inputRate=60,outputRate=5,modules=[{k:v for k,v in m.items() if k in ['id','source','recipe','clock','machineCount']} for m in modules])
  project['layoutInfo']['input'].update(rate=60,label='60 minerais/min')
  project['layoutInfo']['output'].update(rate=5,label='5 plaques renforcées/min')
 balance(project)
 return project,prototypes

def balance(project):
 flows=project.get('flows',{'inputs':[{'rate':120}],'outputs':[{'rate':10}]})
 try:input_rate=flows['inputs'][0]['rate'];output_rate=flows['outputs'][0]['rate']
 except (KeyError,TypeError,IndexError) as exc:raise ValueError('Interfaces du module absentes.') from exc
 if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or v<=0 for v in [input_rate,output_rate]) or (project.get('nativeProfile')!='clean-manifold-v1'and abs(input_rate-12*output_rate)>1e-6):raise ValueError('Débits des interfaces du module incohérents.')
 """Solve transport conservation from recipes and explicit input/output ports."""
 catalog=json.loads((n.ROOT/'dist/planner-data.json').read_text(encoding='utf-8'));objects={o['id']:o for o in project['objects']};links=[l for l in project['links'] if l['kind']=='belt'];known={};equations=[]
 for oid,o in objects.items():
  incoming=[i for i,l in enumerate(links) if l['to']==oid];outgoing=[i for i,l in enumerate(links) if l['from']==oid]
  if o['recipe']:
   r=catalog['recipes'][o['recipe']]
   for j,item in enumerate(r['inputs']):
    suffix=next(key for key,value in o['native']['inputItems'].items() if value==item['id']) if o['type']=='assembler' else 'Input0';edges=[i for i in incoming if links[i]['native']['toPort']==suffix]
    if len(edges)!=1:raise ValueError('Entrée machine absente ou dupliquée.')
    known[edges[0]]=item['amount']*60/r['seconds']*o['clock'];links[edges[0]]['item']=item['id']
   if len(outgoing)!=1:raise ValueError('Sortie machine absente ou dupliquée.')
   known[outgoing[0]]=r['outputs'][0]['amount']*60/r['seconds']*o['clock'];links[outgoing[0]]['item']=r['outputs'][0]['id']
  elif incoming or outgoing:
   equations.append((incoming,outgoing,(o['io']['rate']*(1 if o['io']['side']=='input'else -1))if project.get('nativeProfile')=='clean-manifold-v1'and o.get('io')else (input_rate if not incoming else -output_rate if o['type']=='storage'or (not outgoing and oid==project.get('layoutInfo',{}).get('output',{}).get('objectId')) else 0)))
 for _ in range(len(links)+1):
  changed=False
  for ins,outs,supply in equations:
   ids=ins+outs;unknown=[i for i in ids if i not in known];value=supply+sum(known.get(i,0) for i in ins)-sum(known.get(i,0) for i in outs)
   if not unknown and abs(value)>1e-5:raise ValueError('Débits non équilibrés dans le module.')
   if len(unknown)==1:known[unknown[0]]=value if unknown[0] in outs else -value;changed=True
   items={links[i].get('item') for i in ids}-{None}
   if len(items)>1:raise ValueError('Mélange de ressources dans le réseau.')
   if items:
    for i in ids:
     if 'item' not in links[i]:links[i]['item']=next(iter(items));changed=True
  if not changed:break
 if len(known)!=len(links):raise ValueError('Débit physique indéterminé.')
 for i,l in enumerate(links):
  if known[i]<=0 or known[i]>l['capacity']+1e-6:raise ValueError('Débit invalide ou capacité insuffisante.')
  l['rate']=round(known[i],8)

def calibrated_options(project):return project.get('nativeSettings',project.get('generation',{}))

def parameters(project):
 options=calibrated_options(project)
 pitch=options.get('pitch','minimum');style=options.get('layoutStyle','compact')
 if pitch not in ['minimum',8,10,12,16] or style not in ['compact','balanced','spacious']:raise ValueError('Options de génération invalides.')
 return (0 if pitch=='minimum' else pitch),({'compact':0,'balanced':1,'spacious':2}[style])

def proposal(options=None):
 options=options or {};pitch,clearance=parameters({'generation':options})
 flat=options.get('storeyMode')=='single'
 if flat and options.get('inputItem','Desc_OreIron_C')!='Desc_OreIron_C':raise ValueError('Les blocs sur un étage demandent une entrée de minerai de fer.')
 profile='iron-plates-blocks-flat-v1' if flat else PROFILE
 result=copy.deepcopy(atlas(pitch,clearance,profile)[0]);base_size=result['size'];size=options.get('size',base_size);depth=options.get('depth',size);height=options.get('height',size);dimensions(dict(size=size,depth=depth,height=height))
 if min(size,depth)<base_size or options.get('floorProfile','factory') not in ['frame','factory','solid'] or options.get('beltPolicy','fixed') not in ['fixed','auto']:raise ValueError('Options de génération invalides.')
 if options.get('priority')=='architecture'and (options.get('reserveCladding')or options.get('layoutStyle','compact')!='compact')and min(size,depth)<({0:48,1:48,2:64}[clearance] if flat else 40):raise ValueError('La chaîne calibrée occupe 32 m. Pour réserver les marges de façade, choisissez au moins 5 × 5, ou Production d’abord en 4 × 4.')
 result['size']=size;result.update({k:v for k,v in [('depth',depth),('height',height)]if v!=size});result['generation']={'layoutStyle':options.get('layoutStyle','compact'),'pitch':options.get('pitch','minimum'),'floorProfile':options.get('floorProfile','factory'),'beltPolicy':options.get('beltPolicy','fixed')}
 # The calibrated module occupies 32 m. A larger designer reserves the spare
 # space around it for walls and decoration instead of anchoring it to an edge.
 margin=(size-base_size)/2;margin_y=(depth-base_size)/2
 for obj in result['objects']:obj['x']+=margin;obj['y']+=margin_y
 result['layoutInfo']['edgeMargin']=margin
 result['generation'].update(priority='architecture'if options.get('reserveCladding')else'production'if options.get('layoutStyle','compact')=='compact'else options.get('priority','production'),envelopeStyle=options.get('envelopeStyle','classics'))
 if flat:result['generation'].update(storeyMode='single',maxStoreys=1)
 result['nativeSettings']=copy.deepcopy(result['generation'])
 rate=options.get('outputRate',5 if flat else 10)
 if not isinstance(rate,(int,float)) or isinstance(rate,bool) or not .2<=rate<=(5 if flat else 10):raise ValueError('Ces modules prennent en charge de 0,2 à '+str(5 if flat else 10)+' plaques renforcées/min.')
 factor=rate/(5 if flat else 10)
 for obj in result['objects']:
  if obj['type'] in ['smelter','constructor','assembler']:obj['clock']*=factor
 for link in result['links']:
  if link.get('rate'):link['rate']*=factor
 result['flows']={'inputs':[{'id':'Desc_OreIron_C','rate':rate*12}],'outputs':[{'id':'Desc_IronPlateReinforced_C','rate':rate}]}
 result['layoutInfo'].update(inputRate=rate*12,outputRate=rate)
 result['layoutInfo']['input'].update(rate=rate*12,label=f'{rate*12:g} minerais/min')
 result['layoutInfo']['output'].update(rate=rate,label=f'{rate:g} plaques renforcées/min')
 result['structure']['pitch']=options.get('pitch','minimum');result['structure']['clearance']=clearance
 result['layoutInfo']['name']={'compact':'Super compact','balanced':'Équilibré','spacious':'Aéré'}[result['generation']['layoutStyle']]+' · paires calibrées'
 for floor in result['floors']:
  floor['profile']=options.get('floorProfile','factory');floor['holes']=[]
 if result['generation']['beltPolicy']=='auto':
  for link in result['links']:
   if link['kind']=='belt':link['capacity']=next(c for c in [60,120,270,480,780] if c>=link['rate']-1e-6)
 if max(o['z']+o['h'] for o in result['objects'])>height:raise ValueError('Cette hauteur dépasse le volume '+str(size//8)+'×'+str(size//8)+'. Choisissez un format supérieur ou réduisez la hauteur entre étages.')
 if options.get('inputItem')=='Desc_IronIngot_C':
  # Bypass the smelting pair modules when ingots are supplied externally.
  removed={o['id']for o in result['objects']if o['native']['module'].startswith('smelter-')}
  result['objects']=[o for o in result['objects']if o['id'] not in removed]
  result['links']=[l for l in result['links']if l['from'] not in removed and l['to'] not in removed]
  entry=next(o for o in result['objects']if o['name']=='Répartition des lingots · 90 / 30')
  result['flows']['inputs'][0]['id']='Desc_IronIngot_C'
  result['layoutInfo']['input'].update(objectId=entry['id'],port='Input1',label=f'{rate*12:g} lingots/min')
  result['layoutInfo']['machineCount']=sum(o['type'] in ['smelter','constructor','assembler']for o in result['objects'])
  # Removing a pair may split the power backbone. Join the remaining wall
  # connectors without exceeding their four native cable slots.
  poles=[o['id']for o in result['objects']if o['type']=='wallPole'];parent={o['id']:o['id']for o in result['objects']};degree={k:0 for k in parent}
  def find(k):
   while parent[k]!=k:k=parent[k]
   return k
  for l in result['links']:
   if l['kind']=='power':parent[find(l['from'])]=find(l['to']);degree[l['from']]+=1;degree[l['to']]+=1
  for left in poles:
   for right in poles:
    if find(left)!=find(right) and degree[left]<4 and degree[right]<4:
     result['links'].append({'kind':'power','from':left,'to':right});parent[find(left)]=find(right);degree[left]+=1;degree[right]+=1
  balance(result)
 ids={o['id']for o in result['objects']if o['type']=='storage'}
 incoming=next((l for l in result['links']if l['kind']=='belt'and l['to']in ids),None)
 if incoming and result.get('layoutInfo',{}).get('output'):result['layoutInfo']['output'].update(objectId=incoming['from'],port=incoming.get('native',{}).get('fromPort','Output1'))
 for o in result['objects']:
  if incoming and o['id']==incoming['from']:o['name']='Sortie usine'
 result['objects']=[o for o in result['objects']if o['id']not in ids];result['links']=[l for l in result['links']if l['from']not in ids and l['to']not in ids]
 return result

def project_atlas(project):
 if project.get('nativeProfile')=='clean-manifold-v1':
  from native_manifold import atlas as clean_atlas
  return clean_atlas(json.dumps(project['manifoldSpec'],sort_keys=True))
 return atlas(*parameters(project),project.get('nativeProfile',PROFILE))

def build_project(project):
 import native_project as p
 import native_design
 if project.get('schemaVersion')!=2 or project.get('kind')!='factory-tools-paper-blueprint' or not isinstance(project.get('id'),str) or not p.re.fullmatch(r'[A-Za-z0-9_-]{1,80}',project['id']) or not isinstance(project.get('name'),str) or not 1<=len(project['name'].strip())<=80:raise p.ExportError(['Identité du projet compact invalide.'])
 if project.get('nativeProfile')=='clean-manifold-v1':
  from native_manifold import validate as validate_manifold
  validate_manifold(project)
 expected,prototypes=project_atlas(project);objects=project.get('objects',[]);links=project.get('links',[])
 if any(l.get('waypoints') for l in links):raise p.ExportError(['Le tracé manuel à points de passage est schématique ; son export natif n’est pas encore calibré.'])
 dimensions(project)
 if not isinstance(objects,list) or not 1<=len(objects)<=1000 or not isinstance(links,list) or len(links)>5000 or len({o.get('id') for o in objects})!=len(objects):raise p.ExportError(['Projet compact invalide.'])
 if not isinstance(project.get('floors'),list) or not project['floors'] or len(project['floors'])>64:raise p.ExportError(['Planchers du module absents.'])
 for f in project['floors']:
  if not p.finite(f.get('z')) or f['z']<0 or f['z']+1.4>dimensions(project)[2] or f.get('thickness')!=1 or f.get('profile') not in ['solid','frame','factory']:raise p.ExportError(['Structure compacte invalide.'])
 for f in project['floors']:
  holes=f.get('holes',[])
  if not isinstance(holes,list) or len(holes)>project['size']*project.get('depth',project['size'])//64 or any(not isinstance(cell,list) or len(cell)!=2 or any(not isinstance(v,int) or isinstance(v,bool) or not 0<=v<dimensions(project)[i]//8 for i,v in enumerate(cell)) for cell in holes):raise p.ExportError(['Trémies de plancher invalides.'])
 appearance=project.get('appearance')
 if appearance is not None and (not isinstance(appearance,dict) or not isinstance(appearance.get('enabled'),bool) or not isinstance(appearance.get('color'),str) or not p.re.fullmatch('#[0-9a-fA-F]{6}',appearance['color'])):raise p.ExportError(['Couleur du module invalide.'])
 a=Assembly(p.load('native-connected-template.json'));actors={};metadata={};used=set();assets=json.loads((n.ROOT/'data/native-assets.json').read_text(encoding='utf-8'));catalog=json.loads((n.ROOT/'data/game_catalog.json').read_text(encoding='utf-8'))['recipes']
 for o in objects:
  index=o.get('native',{}).get('prototype')
  if not isinstance(index,int) or isinstance(index,bool) or not 0<=index<len(prototypes):raise p.ExportError(['Composant non calibré : recalculer le plan compact après ajout de bâtiments.'])
  proto=prototypes[index];original=proto['object']
  if not all(p.finite(o.get(k)) for k in ['x','y','z','rotation','clock','w','d','h']) or o['rotation'] not in [0,90,180,270] or not .01<=o['clock']<=1:raise p.ExportError(['Position ou cadence invalide.'])
  w,d=(o['d'],o['w']) if o['rotation']%180 else (o['w'],o['d'])
  if o['x']-w/2<-.001 or o['y']-d/2<-.001 or o['x']+w/2>project['size']+.001 or o['y']+d/2>dimensions(project)[1]+.001 or o['z']<0 or o['z']+o['h']>dimensions(project)[2]+.001:raise p.ExportError([o['name']+' dépasse le volume du blueprint.'])
  if o['type'] in p.MACHINES and not any(abs(o['z']-(f['z']+1))<.001 for f in project['floors']):raise p.ExportError([o['name']+' : plancher absent sous la machine.'])
  delta=q(o['rotation']-original['rotation']);position=[proto['actor'][0].position[i]+100*(o[k]-original[k])-(dimensions(project)[i]-dimensions(expected)[i])*50*(i<2) for i,k in enumerate(['x','y','z'])]
  if o['type']!=original['type'] or any(abs(o[k]-original[k])>1e-6 for k in ['w','d','h']):raise p.ExportError(['Dimensions du module calibré modifiées. Recalculez le plan.'])
  rotation=mul(delta,proto['actor'][0].rotation)
  if o['type']=='wallPole'and o.get('native',{}).get('wallMounted'):
   rotation=o['native']['quaternion']
   if len(rotation)!=4 or any(not p.finite(v)for v in rotation)or abs(sum(v*v for v in rotation)-1)>1e-5:raise p.ExportError(['Orientation du raccord mural invalide.'])
  actor=a.clone(proto['piece'],position,rotation);actors[o['id']]=actor;metadata[o['id']]=proto
  if o['type']=='lift' and calibrated_options(project).get('beltPolicy')=='auto':
   rate=max((l.get('rate',0) for l in links if l.get('kind')=='belt' and o['id'] in [l.get('from'),l.get('to')]),default=0);tier=next(i+1 for i,c in enumerate([60,120,270,480,780]) if c>=rate-1e-6)
   actor[0].typePath=p.re.sub(r'Mk[1-6]',f'Mk{tier}',actor[0].typePath);built=prop(actor[1],'mBuiltWithRecipe')
   if built:built.pathName=p.re.sub(r'Mk[1-6]',f'Mk{tier}',built.pathName)
  if o['type'] in p.MACHINES:p.recipe(actor,o,a,assets,catalog)
  color=p.design_color(project,'machines' if o['type'] in p.MACHINES else 'power' if o['type'] in ['pole','wallPole'] else 'logistics')
  if color:p.paint(actor,color)
 def point(oid,port):
  if port not in metadata[oid]['ports']:raise ValueError('Port natif inconnu.')
  return a.port(actors[oid],metadata[oid]['ports'][port])
 def once(oid,port):
  if (oid,port) in used:raise ValueError('Port natif déjà occupé.')
  used.add((oid,port));return a.component(actors[oid],port)
 physical=[]
 for l in links:
  source,target=l['from'],l['to']
  if source not in actors or target not in actors:raise p.ExportError(['Connexion vers un bâtiment absent.'])
  if l['kind']=='power':
   so='PowerInput' if objects_by_id(objects,source)['type'] in ['constructor','assembler'] else 'PowerConnection';to='PowerInput' if objects_by_id(objects,target)['type'] in ['constructor','assembler'] else 'PowerConnection'
   a.wire(a.component(actors[source],so),a.component(actors[target],to),point(source,so),point(target,to));continue
  native=l.get('native',{});sp,tp=native.get('fromPort'),native.get('toPort')
  try:
   start,end=point(source,sp),point(target,tp)
   if l.get('rate',0)>l.get('capacity',120):raise ValueError('Capacité insuffisante.')
   if native.get('snap'):
    if math.dist(start,end)>.1:raise ValueError('Raccord direct détaché : déplacez le module complet ou recalculez.')
    a.connect(once(source,sp),once(target,tp));continue
   spans=[]
   if not isinstance(native.get('spans'),list) or not 1<=len(native['spans'])<=20:raise ValueError('Tracé physique absent ou trop long.')
   for row in native.get('spans',[]):
    if len(row)!=4 or any(len(v)!=3 or any(not p.finite(x) for x in v) for v in row):raise ValueError('Tracé physique invalide.')
    spans.append(tuple(a.port(actors[source],[x*100 for x in v]) if i<2 else rotate(actors[source][0].rotation,[x*100 for x in v]) for i,v in enumerate(row)))
   if not spans or math.dist(spans[0][0],start)>.1 or math.dist(spans[-1][1],end)>.1:raise ValueError('Trajet détaché : déplacez le module complet ou recalculez le plan.')
   if any(math.dist(left[1],right[0])>.1 for left,right in zip(spans,spans[1:])) or any(abs(row[0][2]-row[1][2])>.2 or abs(row[2][2])>.01 or abs(row[3][2])>.01 for row in spans):raise ValueError('Tracé interrompu ou pente non calibrée : utilisez les élévateurs du module.')
   p.native_belt(a,spans,once(source,sp),once(target,tp),[60,120,270,480,780,1200].index(l.get('capacity',120))+1,assets);physical.append((l,p.samples(spans)))
  except (ValueError,KeyError,TypeError) as exc:raise p.ExportError([str(exc)]) from exc
 balanced=copy.deepcopy(project)
 for o in balanced['objects']:o['native']['inputItems']=metadata[o['id']]['object']['native'].get('inputItems',{})
 try:balance(balanced)
 except ValueError as exc:raise p.ExportError(['Débits du module modifiés : '+str(exc)+' Recalculez le plan.']) from exc
 for before,after in zip([l for l in links if l['kind']=='belt'],[l for l in balanced['links'] if l['kind']=='belt']):
  if before.get('item')!=after.get('item') or not p.finite(before.get('rate')) or abs(before['rate']-after['rate'])>1e-5:raise p.ExportError(['Débit déclaré différent du débit des recettes. Recalculez le plan.'])
 for oid,actor in actors.items():
  if metadata[oid]['object']['type']=='lift':
   tier=int(p.re.search(r'ConveyorLiftMk(\d)',actor[0].typePath).group(1));capacity=[60,120,270,480,780,1200][tier-1]
   if any(l['kind']=='belt' and oid in [l['from'],l['to']] and l['rate']>capacity+.001 for l in links):raise p.ExportError(['Capacité réelle de l’élévateur insuffisante.'])
 check_geometry(project,actors,metadata,physical)
 add_floors(a,project,assets)
 if project.get('appearance',{}).get('enabled') or project.get('design',{}).get('colors'):
  for h,o in zip(a.headers,a.objects):
   if isinstance(h,n.sav_parse.ActorHeader) and ('ConveyorBelt' in h.typePath or 'PowerLine' in h.typePath):
    color=p.design_color(project,'power' if 'PowerLine' in h.typePath else 'logistics')
    if color:p.paint((h,o),color)
 architecture=native_design.add(a,project,assets)
 bp=a.finish(p.load('native-test-template.json')['versions'],p.costs(a,assets));bp[1][0]=header_dimensions(project);verify(bp,project)
 mw=sum(float(assets[p.MACHINES[o['type']][0]].get('mPowerConsumption','0'))*o['clock']**1.321928 for o in objects if o['type'] in p.MACHINES)
 return bp,{'objects':len(objects),'architecture':architecture,'foundations':sum(len(native_design.floor_cells(project,f)) for f in project['floors'] if f['profile']=='solid'),'factoryFloors':sum(len(native_design.floor_cells(project,f))for f in project['floors']if f['profile']=='factory'),'frames':sum(len(native_design.floor_cells(project,f)) for f in project['floors'] if f['profile']=='frame'),'belts':sum(l['kind']=='belt' and not l.get('native',{}).get('snap') for l in links),'lifts':sum(o['type']=='lift' for o in objects),'wires':sum(l['kind']=='power' for l in links)+architecture.get('lightWires',0),'size':project['size'],'dimensions':dict(zip(['width','depth','height'],dimensions(project))),'experimentalXL':experimental(project),'powerMW':round(mw+architecture.get('lightingMW',0),2),'warnings':(['Format libre XL expérimental : placement dans le jeu à valider.']if experimental(project)else[])+['Fonctionnement et dégagements en jeu à vérifier.'],'inGameValidated':False,'profile':project.get('nativeProfile',PROFILE)}

def objects_by_id(objects,oid):return next(o for o in objects if o['id']==oid)

def add_floors(a,project,assets):
 from native_design import floor_cells,add_floor
 for f in project.get('floors',[]):
  for ix,iy in floor_cells(project,f):add_floor(a,project,f,ix*8+4,iy*8+4,assets)


def floor_hole(project,floor,point):
 return [int((point[0]+project['size']*50)//800),int((point[1]+dimensions(project)[1]*50)//800)] in floor.get('holes',[])

def check_geometry(project,actors,metadata,physical):
 import native_project as p
 shapes={'smelter':[(0,0,0,500,1000,450),(0,145,450,500,710,400)],'constructor':[(0,0,0,800,1000,600)],'assembler':[(0,-50,0,900,1700,300),(0,75,300,900,550,500)],'storage':[(0,0,0,500,1100,400)]}
 bodies=[(oid,actor,shapes[metadata[oid]['object']['type']]) for oid,actor in actors.items() if metadata[oid]['object']['type'] in shapes]
 for oid,actor in actors.items():
  kind=metadata[oid]['object']['type'];lo=actor[0].position[2];hi=lo
  if kind=='lift':
   dz=rotate(actor[0].rotation,dict(prop(actor[1],'mTopTransform')[0])['Translation'])[2];lo,hi=sorted([lo,lo+dz])
  elif kind in p.MACHINES:hi=lo+metadata[oid]['object']['h']*100
  for f in project['floors']:
   if kind!='lift' and f['profile']!='frame' and not floor_hole(project,f,actor[0].position) and lo<(f['z']+1)*100-.1 and hi>f['z']*100+.1:raise p.ExportError(['Un élévateur ou une machine traverse une dalle pleine. Ce module utilise des cadres ajourés aux étages.'])
 def inside(actor,shape,point):
  x,y,z=local(actor,point)
  return any(abs(x-cx)<w/2-1 and abs(y-cy)<d/2-1 and zz+1<z<zz+h-1 for cx,cy,zz,w,d,h in shape)
 # Hard bodies, not a full-height box around antennae and empty frontal areas.
 for i,(oid,actor,shape) in enumerate(bodies):
  for other,target,tshape in bodies[i+1:]:
   for cx,cy,zz,w,d,h in shape:
    for sx in [-.49,0,.49]:
     for sy in [-.49,0,.49]:
      for sz in [.01,.5,.99]:
       point=[v+b for v,b in zip(actor[0].position,rotate(actor[0].rotation,[cx+w*sx,cy+d*sy,zz+h*sz]))]
       if inside(target,tshape,point):raise p.ExportError(['Corps de machines en collision. Déplacez le module ou recalculez.'])
 points_by_cell={};limit=project['size']*50;limit_y=dimensions(project)[1]*50;ceiling=dimensions(project)[2]*100
 for index,(link,points) in enumerate(physical):
  source,target=link['from'],link['to'];source_group=metadata[source]['object']['native']['module'];target_group=metadata[target]['object']['native']['module'];internal=source_group==target_group and source_group!='interconnect'
  for pt in points:
   if abs(pt[0])>limit+.1 or abs(pt[1])>limit_y+.1 or not -.1<=pt[2]<=ceiling+.1:raise p.ExportError(['Convoyeur hors du volume du blueprint.'])
   if not internal:
    for oid,actor,shape in bodies:
     if oid not in [source,target] and inside(actor,shape,pt):raise p.ExportError(['Un convoyeur traverse le corps d’une machine. Recalculez le plan.'])
   for floor in project['floors']:
    if floor['profile']=='solid' and not floor_hole(project,floor,pt) and floor['z']*100+.1<pt[2]<(floor['z']+1)*100-.1:raise p.ExportError(['Convoyeur traversant une dalle pleine : conserver les cadres ajourés ou créer une traversée native.'])
   for oid,actor in actors.items():
    if metadata[oid]['object']['type']!='lift' or oid in [source,target]:continue
    top=[x+y for x,y in zip(actor[0].position,rotate(actor[0].rotation,dict(prop(actor[1],'mTopTransform')[0])['Translation']))];lo,hi=sorted([actor[0].position[2],top[2]])
    if lo+30<pt[2]<hi-30 and math.hypot(pt[0]-top[0],pt[1]-top[1])<55:raise p.ExportError(['Un convoyeur croise la colonne d’un élévateur.'])
   cell=tuple(math.floor(v/50) for v in pt)
   for dx in [-1,0,1]:
    for dy in [-1,0,1]:
     for dz in [-1,0,1]:
      for previous,qpt in points_by_cell.get((cell[0]+dx,cell[1]+dy,cell[2]+dz),[]):
       if previous!=index and math.dist(pt,qpt)<49:raise p.ExportError(['Deux convoyeurs se croisent à la même hauteur. Recalculez le plan.'])
   points_by_cell.setdefault(cell,[]).append((index,pt))

def verify(bp,project):
 import native_project as p
 by=check_graph(bp);_,prototypes=project_atlas(project);actors=[(h,o) for h,o in zip(bp[2],bp[3]) if isinstance(h,n.sav_parse.ActorHeader)];points={};directions={}
 if len(actors)<len(project['objects']):raise ValueError('Scène native incomplète.')
 for obj,actor in zip(project['objects'],actors):
  proto=prototypes[obj['native']['prototype']]
  expected_path=proto['actor'][0].typePath
  if obj['type']=='lift' and calibrated_options(project).get('beltPolicy')=='auto':
   rate=max((l.get('rate',0) for l in project['links'] if l.get('kind')=='belt' and obj['id'] in [l.get('from'),l.get('to')]),default=0);tier=next(i+1 for i,c in enumerate([60,120,270,480,780]) if c>=rate-1e-6);expected_path=p.re.sub(r'Mk[1-6]',f'Mk{tier}',expected_path)
  if actor[0].typePath!=expected_path:raise ValueError('Type natif incorrect.')
  for suffix,offset in proto['ports'].items():points[actor[0].instanceName+'.'+suffix]=[x+y for x,y in zip(actor[0].position,rotate(actor[0].rotation,offset))]
  if obj['type'] in p.PORTS:
   for side in p.PORTS[obj['type']].values():
    for suffix,offset,direction in side:directions[actor[0].instanceName+'.'+suffix]=rotate(actor[0].rotation,direction)
  elif obj['type']=='lift':
   top=dict(prop(actor[1],'mTopTransform')[0]);directions[actor[0].instanceName+'.ConveyorAny0']=rotate(actor[0].rotation,[-1,0,0]);directions[actor[0].instanceName+'.ConveyorAny1']=rotate(mul(actor[0].rotation,top['Rotation']),[1,0,0])
 if project.get('design',{}).get('living')or project.get('nativeProfile')=='clean-manifold-v1':
  from living_lighting import points as lighting_points
  points.update(lighting_points(project,bp))
 if project.get('design',{}).get('enabled')and project['design'].get('family')=='m05':
  from m05_architecture import power_points
  points.update(power_points(project,bp))
 for h,o in actors:
  if not all(p.finite(v) for v in h.position+h.rotation):raise ValueError('Transformation native invalide.')
  if 'ConveyorBelt' in h.typePath:
   for idx,row in [(0,prop(o,'mSplineData')[0]),(1,prop(o,'mSplineData')[-1])]:
    points[h.instanceName+'.ConveyorAny'+str(idx)]=[x+y for x,y in zip(h.position,rotate(h.rotation,dict(row[0])['Location']))]
    tangent=rotate(h.rotation,dict(row[0])['LeaveTangent' if idx==0 else 'ArriveTangent']);length=math.sqrt(sum(v*v for v in tangent))
    if length<1e-6:raise ValueError('Tangente native vide.')
    directions[h.instanceName+'.ConveyorAny'+str(idx)]=[v/length for v in tangent]
  if 'PowerLine.' in h.typePath:
   locations=[v for k,v in prop(o,'mWireInstances')[0][0] if k=='Locations']
   for ref,loc in zip(o[4],locations):
    if math.dist(points[ref.pathName],loc)>.1 or h.instanceName not in [r.pathName for r in dict(by[ref.pathName][1][0]).get('mWires',[])]:raise ValueError('Câble natif détaché.')
  if 'PowerPole' in h.typePath:
   components=[co for ch,co in by.values()if isinstance(ch,n.sav_parse.ComponentHeader)and ch.parentActorName==h.instanceName and '.PowerConnection'in ch.instanceName]
   for component in components:
    if len(dict(component[0]).get('mWires',[]))>4:raise ValueError('Trop de câbles sur un raccord Mk.1.')
 for h,o in zip(bp[2],bp[3]):
  if isinstance(h,n.sav_parse.ComponentHeader):
   ref=dict(o[0]).get('mConnectedComponent')
   if ref and (h.instanceName not in points or ref.pathName not in points or math.dist(points[h.instanceName],points[ref.pathName])>.1):raise ValueError('Extrémité native non raccordée.')
   if ref and h.instanceName in directions and ref.pathName in directions and sum(a*b for a,b in zip(directions[h.instanceName],directions[ref.pathName]))<.99:raise ValueError('Sens ou orientation de tête native incorrect : '+h.instanceName)
 return by

