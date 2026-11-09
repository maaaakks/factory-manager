"""Ground-floor workcells based on the user's 5x5 layout. No game writes."""
import copy,json,math,hashlib
from functools import lru_cache
import native_blueprint as n
from native_assembly import Assembly,rotate,check_graph
from native_connected import prop
from native_factory import q,aset
PROFILE='iron-plates-workcells-v1'

@lru_cache(maxsize=2)
def canonical(shape="rectangle"):
 import native_compact as c,native_project as p
 long=shape=='elongated'
 source=n.sbp_parse.parseBlueprint(str(n.ROOT/'data/workcell-iron-reference.sbp'));by=check_graph(source)
 extra=p.load('native-connected-template.json');assets=json.loads((n.ROOT/'data/native-assets.json').read_text(encoding='utf-8'));a=Assembly(extra);mapping={};groups={};labels={}
 actors=[(h,o)for h,o in zip(source[2],source[3])if isinstance(h,n.sav_parse.ActorHeader)]
 templates=p.load('native-factory-template.json');templates.update(smelter=p.load('native-test-template.json')['machine'],constructor=extra['constructor'],lift=p.load('native-vertical-template.json')['lift'])
 old_sources=n.decode(json.loads((n.ROOT/'data/compact-native-sources.json').read_text(encoding='utf-8')));old_bp=old_sources['smelter']['blueprint'];wall=next(h for h in old_bp[2]if isinstance(h,n.sav_parse.ActorHeader)and 'PowerPoleWall.'in h.typePath);templates['wallPole']=c.piece(old_bp,wall.instanceName)
 # The illustrative source still uses rods in every constructor and includes an
 # unprocessed-input bypass into the assembler. Keep the cells, repair the flows.
 removed=set()
 old_plate_lift=next(h.instanceName for h,o in actors if 'ConveyorLift'in h.typePath and abs(h.position[0]-1100)<1 and abs(h.position[1]+200)<1)
 if long:removed.add(old_plate_lift)
 for h,o in actors:
  if 'ConveyorBelt' in h.typePath:
   peers=[dict(by[h.instanceName+'.ConveyorAny'+str(i)][1][0]).get('mConnectedComponent')for i in [0,1]]
   if any(r and ('ConveyorBelt' in r.pathName or long and r.pathName.rsplit('.',1)[0]==old_plate_lift) for r in peers):removed.add(h.instanceName)
 def cell(h):
  y=h.position[1]/100
  return 'smelting'if y<-15 else 'plates'if y<-5 else 'rods'if y<4 else 'screws'
 recipes={'smelting':('Recipe_IngotIron_C',1),'plates':('Recipe_IronPlate_C',.75),'rods':('Recipe_IronRod_C',1),'screws':('Recipe_Screw_C',.75),'assembly':('Recipe_IronPlateReinforced_C',1)}
 def record(actor,group,label):groups[actor[0].instanceName]=group;labels[actor[0].instanceName]=label;return actor
 for h,o in actors:
  if h.instanceName in removed or 'PowerLine' in h.typePath or 'ConveyorPole.' in h.typePath:continue
  kind=c.kindof((h,o));group='assembly'if kind=='assembler'else cell(h)
  if kind=='lift' and abs(h.position[0]-1100)<1:group='interconnect'
  if kind=='belt':
   data=[dict(row[0])for row in prop(o,'mSplineData')]
   world=lambda v:[h.position[j]+rotate(h.rotation,v)[j]+(100 if j==2 else 0)for j in range(3)]
   spans=[(world(x['Location']),world(y['Location']),rotate(h.rotation,x['LeaveTangent']),rotate(h.rotation,y['ArriveTangent']))for x,y in zip(data,data[1:])]
   actor=p.native_belt(a,spans,None,None,1,assets)
  else:
   actor=a.clone(templates[kind],([-800,2200,100] if long and kind=='assembler' else [h.position[0],h.position[1],h.position[2]+100]),(q(0)if long and kind=='assembler'else h.rotation))
   if kind=='lift':
    top=dict(prop(o,'mTopTransform')[0]);aset(actor,'mTopTransform',[[['Rotation',top['Rotation']],['Translation',top['Translation']]],[['Rotation','StructProperty',0,'Quat',None,0],['Translation','StructProperty',0,'Vector',None,0]]],['StructProperty',0,'Transform',None,0])
  mapping[h.instanceName]=actor;record(actor,group,{'splitter':'Distribution locale','merger':'Collecte locale','lift':'Élévateur de cellule','wallPole':'Raccord électrique'}.get(kind,kind))
  if kind in p.MACHINES:
   recipe,clock=recipes[group];aset(actor,'mCurrentRecipe',p.ref(assets[recipe]['path']),['ObjectProperty',0])
   for key in ['mCurrentPotential','mPendingPotential']:aset(actor,key,clock,['FloatProperty',0])
 for h,o in actors:
  if h.instanceName not in mapping:continue
  for ref in o[1]:
   peer=dict(by[ref.pathName][1][0]).get('mConnectedComponent')
   if peer:
    owner,suffix=peer.pathName.rsplit('.',1)
    if owner in mapping:a.connect(a.component(mapping[h.instanceName],ref.pathName.rsplit('.',1)[-1]),a.component(mapping[owner],suffix))
 def find(kind,group):return next(actor for actor in mapping.values()if c.kindof(actor)==kind and groups[actor[0].instanceName]==group)
 def end(actor,suffix,offset=None):
  if offset is None:offset=next(v for side in p.PORTS[c.kindof(actor)].values()for key,v,d in side if key==suffix)
  return a.component(actor,suffix),a.port(actor,offset)
 def belt(src,dst,points):
  spans=p.spline(points)
  if not spans:raise ValueError('Courbe de cellule impossible.')
  return p.native_belt(a,spans,src[0],dst[0],1,assets)
 def descent(x,y,entry,exit,label):
  lift=record(a.clone(p.load('native-vertical-template.json')['lift'],[x,y,700],q(entry+180)),'interconnect',label)
  aset(lift,'mTopTransform',[[['Rotation',q(exit-entry-180)],['Translation',[0.,0.,-500.]]],[['Rotation','StructProperty',0,'Quat',None,0],['Translation','StructProperty',0,'Vector',None,0]]],['StructProperty',0,'Transform',None,0])
  return end(lift,'ConveyorAny0',[0,0,0]),end(lift,'ConveyorAny1',[0,0,-500])
 screws=find('merger','screws');assembler=find('assembler','assembly');start=end(screws,'Output1')
 if long:
  top,bottom=descent(-1000,1400,180,90,'Vis vers assemblage')
  belt(start,top,[start[1],[-800,1400,700],top[1]])
  belt(bottom,end(assembler,'Input1'),[bottom[1],end(assembler,'Input1')[1]])
  top,bottom=descent(-600,1400,180,90,'Plaques vers assemblage')
  start=end(find('merger','plates'),'Output1')
  belt(start,top,[start[1],[-800,-400,700],[600,-400,700],[600,1400,700],top[1]])
  belt(bottom,end(assembler,'Input0'),[bottom[1],end(assembler,'Input0')[1]])
 else:
  top,bottom=descent(1500,-100,0,-90,'Vis vers assemblage')
  belt(start,top,[start[1],[-800,1300,700],[600,1300,700],[600,-100,700],top[1]])
  belt(bottom,end(assembler,'Input1'),[bottom[1],end(assembler,'Input1')[1]])
 # Rebuild a small electrical chain, with at most four wires per wall connector.
 poles=[find('wallPole',group)for group in ['smelting','plates','rods','screws']]
 def power(actor):
  kind=c.kindof(actor)
  if kind=='wallPole':return a.component(actor,'PowerConnection'),a.port(actor,[0,0,0])
  suffix,offset=p.MACHINES[kind][4:];return a.component(actor,suffix),a.port(actor,offset)
 for group,pole in zip(['smelting','plates','rods','screws'],poles):
  for machine in [actor for actor in mapping.values()if c.kindof(actor)in p.MACHINES and groups[actor[0].instanceName]==group]:
   x,xp=power(pole);y,yp=power(machine);a.wire(x,y,xp,yp)
 for left,right in zip(poles,poles[1:]):
  x,xp=power(left);y,yp=power(right);a.wire(x,y,xp,yp)
 x,xp=power(poles[-1]);y,yp=power(assembler);a.wire(x,y,xp,yp)
 if long:
  for h in a.headers:
   if isinstance(h,n.sav_parse.ActorHeader):h.position[0]+=400;h.position[1]-=600
  for h,o in zip(a.headers,a.objects):
   if isinstance(h,n.sav_parse.ActorHeader)and 'PowerLine.'in h.typePath:
    for key,value in prop(o,'mWireInstances')[0][0]:
     if key=='Locations':value[0]+=400;value[1]-=600
 bp=a.finish(p.load('native-test-template.json')['versions'],[]);bp[1][0]=5;check_graph(bp)
 modules=[{'input':find('splitter','smelting')[0].instanceName}]
 return bp,groups,labels,modules,{'reference':{'sha256':hashlib.sha256((n.ROOT/'data/workcell-iron-reference.sbp').read_bytes()).hexdigest()}}

def proposal(options=None):
 import native_compact as c
 options=options or {};shape=options.get('shape','rectangle');result=copy.deepcopy(c.atlas(0,0,PROFILE,shape)[0]);size=options.get('size',32 if shape=='elongated'else 40);depth=options.get('depth',64 if shape=='elongated'else size);height=options.get('height',40)
 from blueprint_dimensions import dimensions
 dimensions(dict(size=size,depth=depth,height=height))
 if shape not in ['rectangle','elongated']:raise ValueError('Choisissez Rectangle ou Allongé. La forme Découpé est retirée.')
 min_width,min_depth=(32,64)if shape=='elongated'else(40,40)
 if size<min_width or depth<min_depth:raise ValueError(f'Ces cellules demandent au moins {min_width//8} × {min_depth//8} fondations pour cette forme.')
 if options.get('storeyMode')=='vertical':raise ValueError('Le mode Haut est temporairement indisponible. Choisissez Bas ou Auto.')
 rate=options.get('outputRate',5)
 if not isinstance(rate,(int,float))or isinstance(rate,bool)or not math.isfinite(rate)or not .2<=rate<=5:raise ValueError('Cellules 5×5 : de 0,2 à 5 plaques renforcées/min.')
 for obj in result['objects']:
  obj['x']+=(size-40)/2;obj['y']+=(depth-40)/2
  if obj['type']in ['smelter','constructor','assembler']:obj['clock']*=rate/5
 for key,v in [('size',size),('depth',depth),('height',height)]:result[key]=v
 result['flows']={'inputs':[{'id':'Desc_OreIron_C','rate':rate*12}],'outputs':[{'id':'Desc_IronPlateReinforced_C','rate':rate}]}
 result['generation']={**options,'layoutPolicy':'workcells-5x5-v1','storeyMode':'single','routed':True,'beltPolicy':'auto'};result['nativeSettings']=copy.deepcopy(result['generation'])
 for side,item,flow in [('input','Desc_OreIron_C',rate*12),('output','Desc_IronPlateReinforced_C',rate)]:
  info=result['layoutInfo'][side];info['rate']=flow;info['label']=f'{flow:g}/min';next(o for o in result['objects']if o['id']==info['objectId'])['io']={'side':side,'item':item,'rate':flow}
 if options.get('inputItem')=='Desc_IronIngot_C':
  removed={o['id']for o in result['objects']if o['native']['module']=='smelting' or o['type']=='lift' and abs(o['x']-(size/2-(4 if shape=='elongated'else 8)))<.01 and abs(o['y']-(depth/2-(19 if shape=='elongated'else 13)))<.01}
  result['objects']=[o for o in result['objects']if o['id']not in removed]
  result['links']=[l for l in result['links']if l['from']not in removed and l['to']not in removed]
  entry=next(o for o in result['objects']if o['type']=='splitter'and o['native']['module']=='plates')
  result['layoutInfo']['input'].update(objectId=entry['id'],port='Input1')
  entry['io']={'side':'input','item':'Desc_IronIngot_C','rate':rate*12}
  result['flows']['inputs'][0]['id']='Desc_IronIngot_C'
  result['layoutInfo']['machineCount']=6
 result['layoutInfo'].update(inputRate=rate*12,outputRate=rate,name='Cellules en ligne · 4×8 · un niveau'if shape=='elongated'else 'Cellules face à face · 5×5 · un niveau')
 c.balance(result)
 for l in result['links']:
  if l['kind']=='belt':l['capacity']=60
 return result

