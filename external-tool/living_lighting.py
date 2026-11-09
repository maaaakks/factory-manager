"""Wire native light fixtures using power-port offsets measured in source SBPs."""
import math
from functools import lru_cache
from native_assembly import rotate
from native_compact import inv
from m05_architecture import source,DATA,pose_key

@lru_cache(maxsize=64)
def measured_port(module,index):
 bp,actors=source(module);h,_=actors[index]
 for (wh,wo),descriptor in zip(actors,DATA['modules'][module]['parts']):
  if descriptor['asset']!='PowerLine':continue
  for ref,position in zip(wo[4],descriptor['wire']):
   if ref.pathName.rsplit('.',1)[0]==h.instanceName:
    return ref.pathName.rsplit('.',1)[1],rotate(inv(h.rotation),[position[j]*100-h.position[j]for j in range(3)])
 raise ValueError('Aucun raccord électrique mesuré pour '+DATA['modules'][module]['parts'][index]['asset'])

def expected(part,project):
 suffix,offset=measured_port(part['sourceModule'],part['sourceIndex']);pos=[(part['x']-project['size']/2)*100,(part['y']-project.get('depth',project['size'])/2)*100,part['z']*100]
 return suffix,[pos[j]+v for j,v in enumerate(rotate(part['quat'],offset))]

def points(project,bp):
 if not project.get('design',{}).get('living')and project.get('nativeProfile')!='clean-manifold-v1':return {}
 import native_design,native_blueprint as n
 actual={pose_key(h.typePath,h.position,h.rotation):h for h in bp[2]if isinstance(h,n.sav_parse.ActorHeader)};result={}
 for q in native_design.envelope(project):
  if q.get('livingCircuit')is None or q['asset']not in['PowerPoleWall','FloodlightWall']:continue
  _,actors=source(q['sourceModule']);original=actors[q['sourceIndex']][0];position=[(q['x']-project['size']/2)*100,(q['y']-project.get('depth',project['size'])/2)*100,q['z']*100]
  target=actual.get(pose_key(original.typePath,position,q['quat']))
  if not target:raise ValueError('Élément d’éclairage absent du SBP.')
  suffix,where=expected(q,project);result[target.instanceName+'.'+suffix]=where
 return result

def connect(assembly,project,placed,assets):
 from native_connected import prop
 supports=[];lamps=[]
 for q,actor in placed:
  if q.get('livingCircuit')is None:continue
  suffix,where=expected(q,project);entry=(assembly.component(actor,suffix),where)
  (supports if q['asset']=='PowerPoleWall'else lamps).append(entry)
 if not lamps:return dict(lightWires=0,lights=0,lightingMW=0,lightingFeed=False)
 if not supports:raise ValueError('Le circuit d’éclairage nécessite un raccord mural.')
 # Copy existing connection locations before adding the independent fixture circuit.
 available={}
 for h,o in zip(assembly.headers,assembly.objects):
  if 'PowerLine.'not in getattr(h,'typePath',''):continue
  locations=[v for k,v in prop(o,'mWireInstances')[0][0]if k=='Locations']
  for r,pos in zip(o[4],locations):
   owner=r.pathName.rsplit('.',1)[0];header=next(v for v in assembly.headers if v.instanceName==owner)
   if 'PowerPole'not in header.typePath:continue
   component=assembly.component((header,None),r.pathName.rsplit('.',1)[1]);wires=dict(component[1][0]).get('mWires',[])
   if len(wires)<4:available[r.pathName]=(component,pos)
 if project.get('nativeProfile')=='clean-manifold-v1'or(project.get('design',{}).get('family')=='compact'and project['design']['living'].get('compactRevision')>=2):
  count=0
  for support in supports:
   choices=[v for v in available.values()if len(dict(v[0][1][0]).get('mWires',[]))<4]
   if not choices:raise ValueError('Alimentation de la galerie absente.')
   peer=min(choices,key=lambda v:math.dist(v[1],support[1]))
   if math.dist(peer[1],support[1])>1000:raise ValueError('Alimentation locale du projecteur trop éloignée.')
   assembly.wire(peer[0],support[0],peer[1],support[1]);count+=1
  for lamp in lamps:
   support=min(supports,key=lambda v:math.dist(v[1],lamp[1]));assembly.wire(support[0],lamp[0],support[1],lamp[1]);count+=1
  return dict(lightWires=count,lights=len(lamps),lightingMW=__import__('native_design').CATALOG['livingLighting']['FloodlightWall']['powerMW']*len(lamps),lightingFeed=True)
 supports.sort(key=lambda v:(v[1][2],v[1][0],v[1][1]))
 count=0
 for left,right in zip(supports,supports[1:]):
  if math.dist(left[1],right[1])>10000:raise ValueError('Circuit d’éclairage : raccords distants de plus de 100 m.')
  assembly.wire(left[0],right[0],left[1],right[1]);count+=1
 feed=False
 if available:
  peer=min(available.values(),key=lambda v:math.dist(v[1],supports[0][1]))
  if math.dist(peer[1],supports[0][1])<=10000:assembly.wire(peer[0],supports[0][0],peer[1],supports[0][1]);count+=1;feed=True
 for lamp in lamps:
  choices=[v for v in supports if len(dict(v[0][1][0]).get('mWires',[]))<4]
  if not choices:raise ValueError('Circuit d’éclairage : raccord saturé.')
  support=min(choices,key=lambda v:math.dist(v[1],lamp[1]));assembly.wire(support[0],lamp[0],support[1],lamp[1]);count+=1
 return dict(lightWires=count,lights=len(lamps),lightingMW=__import__('native_design').CATALOG['livingLighting']['FloodlightWall']['powerMW']*len(lamps),lightingFeed=feed)
