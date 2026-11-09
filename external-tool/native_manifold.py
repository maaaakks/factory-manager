"""Airy native manifolds, built from individual machines, never paired blocks."""
import copy,json,math
from functools import lru_cache
import native_blueprint as n
from native_factory import q,aset
from native_assembly import Assembly,rotate,check_graph
from native_connected import prop
PROFILE='clean-manifold-v1'

def demand(flows):
 data=json.loads((n.ROOT/'dist/planner-data.json').read_text(encoding='utf-8'));recipes={**data.get('productionRecipes',{}),**data['recipes']};defaults=data.get('productionDefaults',data.get('defaultRecipes'));raw={r['id']:r['rate']for r in flows['inputs']};work={};needraw={}
 def need(item,rate,trail=()):
  if item in raw:
   needraw[item]=needraw.get(item,0)+rate;return
  if item in trail or item not in defaults:raise ValueError('Entrée ou recette manquante : '+item)
  recipe={**recipes[defaults[item]],'id':defaults[item]}
  if recipe['type']not in ['smelter','constructor','assembler']or len(recipe['outputs'])!=1:raise ValueError('Ce manifold nécessite une machine solide prise en charge.')
  cycles=rate/recipe['outputs'][0]['amount'];work[recipe['id']]=work.get(recipe['id'],0)+cycles
  for row in recipe['inputs']:need(row['id'],cycles*row['amount'],(*trail,item))
 for row in flows['outputs']:need(row['id'],row['rate'])
 if any(abs(needraw.get(k,0)-v)>1e-5 for k,v in raw.items()):raise ValueError('Les entrées doivent correspondre aux besoins des recettes.')
 # Dependency order makes columns read left to right.
 order=[]
 def visit(rid):
  if rid in order:return
  for row in recipes[rid]['inputs']:
   if row['id']not in raw:visit(defaults[row['id']])
  order.append(rid)
 for rid in list(work):visit(rid)
 return [({**recipes[rid],'id':rid},work[rid]*recipes[rid]['seconds']/60)for rid in order]

@lru_cache(maxsize=16)
def atlas(spec_json):
 import native_compact as c,native_project as p,native_transport as t
 spec=json.loads(spec_json);flat=spec.get('simplePatterns') and spec.get('logisticsFloor') is False;flows=spec['flows'];groupspec=demand(flows);rows=max(math.ceil(v-1e-7)for r,v in groupspec);count=sum(math.ceil(v-1e-7)for r,v in groupspec)
 if count>64:raise ValueError('Ce premier manifold accepte au maximum 64 machines.')
 paired=not spec.get('simplePatterns') and len(groupspec)==2 and len(groupspec[1][0]['inputs'])==1 and groupspec[0][0]['outputs'][0]['id']==groupspec[1][0]['inputs'][0]['id']and all(math.ceil(v-1e-7)==rows for r,v in groupspec)
 columns=len(groupspec)if paired else min(3,len(groupspec));bands=math.ceil(len(groupspec)/columns);band=max(32,math.ceil((rows*(18 if flat else 13)+6)/8)*8);depth=max(40,math.ceil((rows*8.5+6)/8)*8)if paired else max(40,bands*band);centers=[];last_half=0
 for col in range(columns):
  half=max({'smelter':5,'constructor':5,'assembler':8.5}[groupspec[i][0]['type']]for i in range(col,len(groupspec),columns));centers.append((20 if flat else 16) if not centers else centers[-1]+last_half+(14 if flat else 5)+half);last_half=half
 width=max(40,math.ceil((centers[-1]+last_half+(8 if flat else 2))/8)*8)
 extra=p.load('native-connected-template.json');pieces=p.load('native-factory-template.json');pieces.update(smelter=p.load('native-test-template.json')['machine'],constructor=extra['constructor']);assets=json.loads((n.ROOT/'data/native-assets.json').read_text(encoding='utf-8'));a=Assembly(extra)
 objects=[];prototypes=[];actors={};links=[];ports={};occupied={};boxes={};resources={};allmachines=[]
 def node(kind,x,y,z,angle=0,recipe=None,clock=1,label=None):
  oid='mf-'+str(len(objects));actor=a.clone(pieces[kind],[(x-width/2)*100,(y-depth/2)*100,z*100],q(angle));actors[oid]=actor
  if recipe:p.recipe(actor,dict(type=kind,recipe=recipe,clock=clock),a,assets,json.loads((n.ROOT/'data/game_catalog.json').read_text(encoding='utf-8'))['recipes'])
  w,d,h={'smelter':(5,10,8.5),'constructor':(8,10,6),'assembler':(9,17,10.75),'splitter':(2,2,1.8),'merger':(2,2,1.8)}[kind];ui=round((angle-(-90 if kind in ['splitter','merger']else 180))/90)*90%360;zz=z-1 if kind in ['splitter','merger']else z
  o=dict(id=oid,type=kind,name=label or kind,x=x,y=y,z=zz,w=w,d=d,h=h,rotation=ui,clock=clock,recipe=recipe,native=dict(prototype=len(objects),module='interconnect',rotation=ui,quaternion=q(angle),originZ=z-zz,ports={}))
  objects.append(o);prototypes.append(dict(piece=None,object=copy.deepcopy(o),actor=actor,ports={}))
  for side in p.PORTS.get(kind,{}).values():
   for suffix,offset,direction in side:ports[oid,suffix]=(offset,rotate(q(angle),direction));o['native']['ports'][suffix]=[v/100 for v in offset]
  boxes[oid]=p.aabb(actor,w*100,d*100,h*100)
  if kind in ['splitter','merger']:boxes[oid]=([actor[0].position[0]-100,actor[0].position[1]-100,z*100-100],[actor[0].position[0]+100,actor[0].position[1]+100,z*100+90])
  if recipe:allmachines.append(oid)
  return oid
 def end(oid,suffix):return a.component(actors[oid],suffix),a.port(actors[oid],ports[oid,suffix][0])
 def belt(src,dst,item,rate,straight=False,forced=None):
  sc,start=end(*src);tc,finish=end(*dst);tier=next(i+1 for i,v in enumerate([60,120,270,480,780,1200])if v>=rate-1e-6)
  if math.dist(start,finish)<.1:a.connect(sc,tc);links.append(dict(kind='belt',**{'from':src[0],'to':dst[0]},item=item,rate=rate,capacity=[60,120,270,480,780,1200][tier-1],native=dict(fromPort=src[1],toPort=dst[1],snap=True)));return
  direction=ports[src][1];arrival=ports[dst][1]
  if forced is not None:spans=forced
  elif straight:
   delta=[finish[i]-start[i]for i in range(3)];spans=[(start,finish,delta,delta)]
  else:
   try:spans=p.route(start,finish,direction,arrival,boxes,src[0],dst[0],(width*100,depth*100,3200),occupied)
   except ValueError as exc:
    scene={'size':width,'depth':depth,'height':32,'floors':[{'z':0}] if flat else [{'z':0},{'z':5}],'nativeProfile':PROFILE}
    try:chains,risers=t.bridge(start,finish,direction,arrival,boxes,src[0],dst[0],(width*100,depth*100,3200),occupied,scene)
    except ValueError:raise ValueError(str(exc)+' '+str((src,dst)))from exc
    ids=[lift(pos[0]/100+width/2,pos[1]/100+depth/2,pos[2]/100,z/100,entry,exit)for pos,z,entry,exit,column in risers]
    points=[src]+[(oid,suffix)for oid in ids for suffix in ['ConveyorAny0','ConveyorAny1']]+[dst]
    for i,sp in enumerate(chains):belt(points[2*i],points[2*i+1],item,rate,forced=sp)
    return
  p.native_belt(a,spans,sc,tc,tier,assets)
  for pt in p.samples(spans):occupied.setdefault(tuple(math.floor(v/50)for v in pt),[]).append(pt)
  actor=actors[src[0]];local=lambda v:[v/100 for v in c.local(actor,v)];vec=lambda v:[v/100 for v in rotate(c.inv(actor[0].rotation),v)]
  links.append(dict(kind='belt',**{'from':src[0],'to':dst[0]},item=item,rate=rate,capacity=[60,120,270,480,780,1200][tier-1],native=dict(fromPort=src[1],toPort=dst[1],spans=[[local(s),local(e),vec(u),vec(v)]for s,e,u,v in spans])))
 def lift(x,y,start,finish,entry=0,exit=0):
  oid='mf-'+str(len(objects));actor=t.lift(a,[(x-width/2)*100,(y-depth/2)*100,start*100],finish*100,entry,exit,2,assets);actors[oid]=actor;z=min(start,finish);h=abs(finish-start)+.5
  o=dict(id=oid,type='lift',name='Traversée vers le vide technique',x=x,y=y,z=z,w=1,d=1,h=h,rotation=0,clock=1,recipe=None,native=dict(prototype=len(objects),module='interconnect',rotation=0,quaternion=actor[0].rotation,originZ=start-z,ports={'ConveyorAny0':[0,0,0],'ConveyorAny1':[0,0,finish-start]}));objects.append(o);prototypes.append(dict(piece=None,object=copy.deepcopy(o),actor=actor,ports={}))
  ports[oid,'ConveyorAny0']=([0,0,0],[math.cos(math.radians(entry)),math.sin(math.radians(entry)),0]);ports[oid,'ConveyorAny1']=([0,0,(finish-start)*100],[math.cos(math.radians(exit)),math.sin(math.radians(exit)),0]);boxes[oid]=([actor[0].position[0]-55,actor[0].position[1]-55,z*100],[actor[0].position[0]+55,actor[0].position[1]+55,max(start,finish)*100]);return oid
 # Individual machine rows. Two simple columns occupy 40 x 40m and leave the
 # entire left 8m strip for a glazed control room, without a storage container.
 if paired:
  machine_rows=[]
  for col,(recipe,equivalents)in enumerate(groupspec):
   stage=[]
   for i in range(rows):
    x=16+15*col;y=5+8.5*i;clock=min(1,equivalents-i);stage.append(node(recipe['type'],x,y,6,270,recipe['id'],clock,recipe['name']))
   machine_rows.append(stage)
  splitters=[node('splitter',9,5+8.5*i,2,90,label='Manifold entrée · minerai')for i in range(rows)]
  mergers=[node('merger',38.5,5+8.5*i,2,90,label='Manifold sortie · production')for i in range(rows)]
  for i,(sm,con)in enumerate(zip(*machine_rows)):
   y=5+8.5*i;ore=lift(10,y,2,7);down=lift(22,y,7,2);up=lift(24,y,2,7);out=lift(37.5,y,7,2)
   r0,v0=groupspec[0];r1,v1=groupspec[1];c0=objects[int(sm[3:])]['clock'];c1=objects[int(con[3:])]['clock'];ir=r0['inputs'][0]['amount']*60/r0['seconds']*c0;mid=r0['outputs'][0]['amount']*60/r0['seconds']*c0;need=r1['inputs'][0]['amount']*60/r1['seconds']*c1;rate=r1['outputs'][0]['amount']*60/r1['seconds']*c1
   if abs(mid-need)>1e-5:raise ValueError('Ce pattern demande des lignes fonderie/constructeur équilibrées.')
   belt((splitters[i],'Output3'),(ore,'ConveyorAny0'),r0['inputs'][0]['id'],ir,True);belt((ore,'ConveyorAny1'),(sm,'Input0'),r0['inputs'][0]['id'],ir,True)
   belt((sm,'Output2'),(down,'ConveyorAny0'),r0['outputs'][0]['id'],mid,True);belt((down,'ConveyorAny1'),(up,'ConveyorAny0'),r0['outputs'][0]['id'],mid,True);belt((up,'ConveyorAny1'),(con,'Input0'),r0['outputs'][0]['id'],mid,True)
   belt((con,'Output0'),(out,'ConveyorAny0'),r1['outputs'][0]['id'],rate,True);belt((out,'ConveyorAny1'),(mergers[i],'Input2'),r1['outputs'][0]['id'],rate,True)
   if i+1<rows:
    remaining=sum(r0['inputs'][0]['amount']*60/r0['seconds']*objects[int(v[3:])]['clock']for v in machine_rows[0][i+1:]);made=sum(r1['outputs'][0]['amount']*60/r1['seconds']*objects[int(v[3:])]['clock']for v in machine_rows[1][:i+1])
    belt((splitters[i],'Output1'),(splitters[i+1],'Input1'),r0['inputs'][0]['id'],remaining,True);belt((mergers[i],'Output1'),(mergers[i+1],'Input1'),r1['outputs'][0]['id'],made,True)
 else:
  inputs={};outputs={};edges=[]
  def pending(a,b,item,rate,straight=False):edges.append((a,b,item,rate,straight))
  for col,(recipe,equivalents)in enumerate(groupspec):
   for i in range(math.ceil(equivalents-1e-7)):
    x=centers[col%columns];y=8+(18 if flat else 13)*i+(col//columns)*band;clock=min(1,equivalents-i);kind=recipe['type'];machine=node(kind,x,y,1 if flat else 6,270,recipe['id'],clock,recipe['name']);half={'smelter':5,'constructor':5,'assembler':8.5}[kind]
    if kind=='assembler':objects[int(machine[3:])]['native']['inputItems']={f'Input{j}':row['id']for j,row in enumerate(recipe['inputs'])}
    for j,row in enumerate(recipe['inputs']):
     yy=y+(-2 if j==0 else 2)if kind=='assembler'else y;rate=row['amount']*60/recipe['seconds']*clock
     if flat:
      junction=node('splitter',x-half-4-3*j,yy,2+2*j,90,label='Manifold entrée · '+row['id']);inputs.setdefault(row['id'],[]).append((junction,rate))
      if j:
       head=lift(x-half-1.5,yy,4,2,0,0);pending((junction,'Output3'),(head,'ConveyorAny0'),row['id'],rate);pending((head,'ConveyorAny1'),(machine,'Input'+str(j)),row['id'],rate,True)
      else:pending((junction,'Output3'),(machine,'Input'+str(j)),row['id'],rate)
      continue
     rail_z=3 if spec.get('simplePatterns') and j==1 else 2;head=lift(x-half-1.5,yy,rail_z,7,180,0);junction=node('splitter',x-2-(4*j if spec.get('simplePatterns') else 0),y-2+4*j,rail_z,90,label='Manifold entrée · '+row['id']);inputs.setdefault(row['id'],[]).append((junction,rate))
     pending((junction,'Output2'),(head,'ConveyorAny0'),row['id'],rate);pending((head,'ConveyorAny1'),(machine,'Input'+str(j)),row['id'],rate,True)
    row=recipe['outputs'][0];rate=row['amount']*60/recipe['seconds']*clock
    if flat:
     junction=node('merger',x+half+4,y,2,90,label='Manifold sortie · '+row['id']);outputs.setdefault(row['id'],[]).append((junction,rate));pending((machine,'Output2'if kind=='smelter'else'Output0'),(junction,'Input2'),row['id'],rate);continue
    head=lift(x+half+1.5,y,7,2,0,180);junction=node('merger',x+2,y,2,90,label='Manifold sortie · '+row['id']);outputs.setdefault(row['id'],[]).append((junction,rate))
    pending((machine,'Output2'if kind=='smelter'else'Output0'),(head,'ConveyorAny0'),row['id'],rate,True);pending((head,'ConveyorAny1'),(junction,'Input2'),row['id'],rate)
  # All recipe inputs form one scalable sequential manifold per resource.
  # Output mergers accumulate in the same order, wholly in the service void.
  for item,consumers in inputs.items():
   for i,((left,_),(right,_))in enumerate(zip(consumers,consumers[1:])):pending((left,'Output1'),(right,'Input1'),item,sum(v for _,v in consumers[i+1:]))
  for item,producers in outputs.items():
   for i,((left,_),(right,_))in enumerate(zip(producers,producers[1:])):pending((left,'Output1'),(right,'Input1'),item,sum(v for _,v in producers[:i+1]))
   if item in inputs:pending((producers[-1][0],'Output1'),(inputs[item][0][0],'Input1'),item,sum(v for _,v in inputs[item]))
  for row in flows['inputs']:
   oid=inputs[row['id']][0][0];objects[int(oid[3:])]['io']=dict(side='input',item=row['id'],rate=row['rate'])
  for row in flows['outputs']:
   oid=(inputs[row['id']][-1][0]if row['id']in inputs else outputs[row['id']][-1][0]);objects[int(oid[3:])]['io']=dict(side='output',item=row['id'],rate=row['rate'])
  splitters=[inputs[flows['inputs'][0]['id']][0][0]];mergers=[outputs[flows['outputs'][0]['id']][-1][0]]
  for args in sorted(edges,key=lambda row:not row[4]):belt(*args)
 # Ceiling terminals use a measured wall connector, rotated down, directly
 # above each real native power port. No diagonal wire across the control room.
 from native_blocks import sources
 source=sources()['smelter2']['blueprint'];sh=next(h for h in source[2]if isinstance(h,n.sav_parse.ActorHeader)and 'PowerPoleWall.'in h.typePath);template=c.piece(source,sh.instanceName);previous=None;ceiling=max(16.5,max(o['z']+p.MACHINES[o['type']][5][2]/100+.9 for o in objects if o.get('recipe')))
 for machine in allmachines:
  actor=actors[machine];kind=objects[int(machine[3:])]['type'];suffix,offset=p.MACHINES[kind][4:];where=a.port(actor,offset);pos=[where[0],where[1],ceiling*100];oid='mf-'+str(len(objects));socket=a.clone(template,pos,[0,math.sqrt(.5),0,math.sqrt(.5)]);actors[oid]=socket
  off=[80,0,0];point=a.port(socket,off);o=dict(id=oid,type='wallPole',name='Électricité au plafond',x=pos[0]/100+width/2,y=pos[1]/100+depth/2,z=ceiling,w=.6,d=.6,h=.6,rotation=0,clock=1,recipe=None,native=dict(prototype=len(objects),module='manifold-electric',rotation=0,quaternion=socket[0].rotation,originZ=0,ports={'PowerConnection':[.8,0,0]},ceilingMounted=True,wallMounted=True));objects.append(o);prototypes.append(dict(piece=None,object=copy.deepcopy(o),actor=socket,ports={}))
  a.wire(a.component(socket,'PowerConnection'),a.component(actor,suffix),point,where);links.append(dict(kind='power',**{'from':oid,'to':machine}));objects[int(machine[3:])]['native']['ports'][suffix]=[v/100 for v in offset]
  if previous:
   poid,pa,pp=previous;a.wire(a.component(pa,'PowerConnection'),a.component(socket,'PowerConnection'),pp,point);links.append(dict(kind='power',**{'from':poid,'to':oid}))
  previous=oid,socket,point
 bp=a.finish(p.load('native-test-template.json')['versions'],p.costs(a,assets));bp[1][0]=[width//8,depth//8,4]
 for i,(o,proto)in enumerate(zip(objects,prototypes)):
  proto['piece']=c.piece(bp,proto['actor'][0].instanceName);proto['ports']={k:[v*100 for v in xyz]for k,xyz in o['native']['ports'].items()};proto['object']=copy.deepcopy(o)
 project=dict(schemaVersion=2,kind='factory-tools-paper-blueprint',id='clean-manifold',name='Atelier aéré · 4 fonderies + 4 constructeurs',size=width,depth=depth,height=32,objects=objects,links=links,buffer=[],flows=flows,nativeProfile=PROFILE,manifoldSpec=spec,powerStyle='per-module',nativeSettings={'pitch':'minimum','beltPolicy':'auto'},generation={'layoutStyle':spec.get('density','spacious'),'layoutPolicy':'clean-manifold-v1','storeyMode':'single','shape':'rectangle','floorProfile':'solid','reserveCladding':False},structure=dict(gap=4,pitch=12,thickness=1,material='polished',color='#aeb7b7'),floors=[dict(z=z,thickness=1,profile='solid',material='polished',color='#aeb7b7',shaft=2,role=role)for z,role in ([(0,'production')] if flat else [(0,'technical'),(5,'production')])],layoutInfo=dict(name='Manifolds · vide technique caché de 4 m',machineCount=count,controlWidth=8,technicalClearance=4,**{'input':dict(objectId=splitters[0],port='Input1',rate=flows['inputs'][0]['rate'],label='Entrée minerai'),'output':dict(objectId=mergers[-1],port='Output1',rate=flows['outputs'][0]['rate'],label='Sortie usine')}))
 if spec.get('simplePatterns'):
  project['name']='Patterns de production';project['layoutInfo']['input']['label']='Entrée ressource';project['layoutInfo'].update(name='Rangées simples · Logistics floor de 4 m',controlWidth=0,patterns=[dict(type=recipe['type'],recipe=recipe['id'],count=math.ceil(equivalents-1e-7))for recipe,equivalents in groupspec])
 if flat:
  project['generation']['logisticsFloor']=False;project['layoutInfo'].update(name='Rangées simples · réseaux au sol',technicalClearance=0)
 from manifold_interior import parts
 from manifold_interior import entry_parts
 project['manifoldInterior']={'version':1,'parts':parts(project),'baseParts':parts(project),'entryParts':[] if spec.get('simplePatterns') else entry_parts()}
 c.balance(project);return project,prototypes

def proposal(payload):
 flows={k:payload[k]for k in ['inputs','outputs']};options=payload.get('options',{});spec=dict(flows=flows,density=options.get('layoutStyle','spacious'));
 if options.get('layoutPolicy')=='simple-patterns-v1':
  if any(row['rate']>1200+1e-6 for side in ['inputs','outputs']for row in flows[side]):raise ValueError('Le manifold dépasse 1 200 unités/min ; réduisez le débit ou le nombre de machines.')
  spec['simplePatterns']=True
  if 'logisticsFloor' in options:
   if not isinstance(options['logisticsFloor'],bool):raise ValueError('Option logistics floor invalide.')
   spec['logisticsFloor']=options['logisticsFloor']
 project=copy.deepcopy(atlas(json.dumps(spec,sort_keys=True))[0]);add_light_feeds(project);return project

def add_light_feeds(p):
 p['objects']=[o for o in p['objects']if not o['id'].startswith('mf-light-')];p['links']=[l for l in p['links']if not l['from'].startswith('mf-light-')and not l['to'].startswith('mf-light-')]
 from manifold_interior import parts
 sockets=[o for o in p['objects']if o.get('native',{}).get('ceilingMounted')];proto=sockets[0];previous=sockets[-1]['id']
 for i,q0 in enumerate(q for q in parts(p)if q['asset']=='PowerPoleWall'):
  v=rotate(q0['quat'],[.8,0,0]);o=copy.deepcopy(proto);o.update(id='mf-light-'+str(i),x=q0['x']+v[0],y=q0['y']+v[1]);o['native']['lightingFeed']=True;p['objects'].append(o);p['links'].append(dict(kind='power',**{'from':previous,'to':o['id']}));previous=o['id']

def validate(p):
 from native_project import ExportError
 from manifold_interior import parts
 def close(a,b):
  if isinstance(a,(int,float))and not isinstance(a,bool):return isinstance(b,(int,float))and abs(a-b)<1e-6
  if isinstance(a,dict):return isinstance(b,dict)and a.keys()==b.keys()and all(close(v,b[k])for k,v in a.items())
  if isinstance(a,list):return isinstance(b,list)and len(a)==len(b)and all(close(x,y)for x,y in zip(a,b))
  return a==b
 if not close(p.get('manifoldInterior',{}).get('parts'),parts(p)):raise ExportError(['Aménagement aéré modifié : régénérez le layout avant l’export.'])
 canonical=atlas(json.dumps(p['manifoldSpec'],sort_keys=True))[0]
 if not close(p.get('manifoldInterior',{}).get('baseParts'),canonical['manifoldInterior']['baseParts']):raise ExportError(['Gabarit intérieur modifié.'])
 if not close(p['flows'],p['manifoldSpec']['flows']):raise ExportError(['Objectifs modifiés : régénérez le manifold.'])
 expected=[0] if p['manifoldSpec'].get('simplePatterns') and p['manifoldSpec'].get('logisticsFloor') is False else [0,5]
 if sorted(f['z']for f in p.get('floors',[]))!=expected or any(f['thickness']!=1 or f['material']!='polished'for f in p['floors']):raise ExportError(['Le vide technique doit conserver ses 4 m libres et ses dalles en béton ciré.'])
 if p.get('manifoldPlacement')and (p['manifoldPlacement']['x']!=8 or p['manifoldPlacement']['y']!=16):raise ExportError(['Accueil et contrôle désalignés. Réappliquez la création.'])

