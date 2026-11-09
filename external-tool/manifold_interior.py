"""A connected control room and concealed one-wall service void."""
import math,copy

def parts(p):
 if p.get('nativeProfile')!='clean-manifold-v1' or p.get('manifoldSpec',{}).get('simplePatterns'):return []
 from m05_architecture import DATA
 out=[];w=p['size'];d=p.get('depth',w);ceiling=max(o['z']for o in p['objects']if o.get('native',{}).get('ceilingMounted'))
 def wall(asset,name,x,y,z,r=0,h=4,layer='interior'):
  q=dict(name=name,asset=asset,component='window'if 'Window'in asset else'wall',x=x,y=y,z=z,w=8,d=.22,h=h,rotation=r,color='#263039'if 'Window'not in asset else'#99c7d3',zone='interieur',studyLayer=layer);out.append(q);return q
 def module(asset,name,x,y,z,r=0,color='#aeb7b7'):
  find=asset if any(any(q['asset']==asset for q in m['parts'])for m in DATA['modules'].values())else'Foundation_Concrete_8x4'
  key=next(k for k,m in DATA['modules'].items()if any(q['asset']==find for q in m['parts']));i=next(i for i,q in enumerate(DATA['modules'][key]['parts'])if q['asset']==find)
  a=math.radians(r)/2;q=dict(name=name,asset=asset,component='module',sourceModule=key,sourceIndex=i,origin=[0,0,0],turn=0,quat=[0,0,math.sin(a),math.cos(a)],x=x,y=y,z=z,w=0,d=0,h=0,rotation=r,color=color,zone='interieur',studyLayer='interior');out.append(q);return q
 # The service void is genuinely enclosed; belts disappear below the slab.
 for x in range(4,w,8):
  for y in [.15,d-.15]:wall('Wall_Concrete_8x4','Technique · paroi opaque de 4 m',x,y,1,0,layer='technical')
 for y in range(4,d,8):
  for x in [.15,w-.15]:wall('Wall_Concrete_8x4','Technique · paroi opaque de 4 m',x,y,1,90,layer='technical')
  wall('Wall_Concrete_8x4','Contrôle · soubassement plein',8.2,y,6,90)
  if y==d-4:wall('Wall_Gate_8x4_01','Contrôle · passage large vers la descente',8.2,y,10,90)
  else:wall('Wall_Window_Thin_8x4_01','Contrôle · baie continue sans bordure',8.2,y,10.25,90)
  module('Foundation_ConcretePolished_8x1','Contrôle · estrade continue',4,y,9.5)
  module('Roof_Tar_01','Contrôle · plafond isolant',4,y,14.5,color='#263039')['interiorCeiling']=True
 # Native catwalk stairs rise along +X; the high end joins the control room.
 stairs=module('CatwalkStairs','Contrôle · descente vers les machines',10,d-4,6,180,'#697c80');stairs.update(walkStart=[12,d-4,6],walkEnd=[8,d-4,10])
 module('CatwalkCross','Contrôle · palier d’inspection',14,d-4,6,color='#697c80')
 # Long LED strips match the native sign and downward orientation in the user's
 # EXEMPLE_DESIGN_CLEAN, with no dependence on that file at runtime.
 for x in [4,20,36]:
  for y in range(4,d,4):
   q=module('StandaloneWidgetSign_SmallVeryWide','Technique · bande LED sous dalle',x,y,4.85,color='#ddf7f4');q.update(emissiveSign=True,emission=2,nativeSignQuaternion=[-.5,.5,-.5,.5],quat=[-.5,.5,-.5,.5],studyLayer='technical')
 # An actual ceiling supports the electrical terminals and hides in cutaway.
 for x in range(12,w,8):
  for y in range(4,d,8):module('Roof_Tar_01','Machines · plafond technique',x,y,17.3,color='#263039')['interiorCeiling']=True
 # Real floodlights retain the working native circuit used by Compact.
 locations=[(w-.15,5+8.5*i,180)for i in range(4)]+[(31,.15,90),(31,d-.15,270)]
 for i,(x,y,r)in enumerate(locations):
  for zz,asset,hh in[(6,'Wall_8x4_01',4),(10,'Wall_8x4_01',4),(14,'Wall_Orange_8x1',1),(15,'Wall_Orange_8x1',1),(16,'Wall_Orange_8x1',1)]:
   if r==180:wall(asset,'Lumière · cassette de fixation',w-.02,y,zz,90,hh)
   else:wall(asset,'Lumière · cassette de fixation',x,y,zz,0,hh)
  for asset,z in [('PowerPoleWall',11.9),('FloodlightWall',14)]:
   q=module(asset,'Machines · projecteur alimenté'if asset=='FloodlightWall'else'Machines · raccord du projecteur',x,y,z,r,'#d7eff2');q['livingCircuit']='clean-light-'+str(i)
   if asset=='FloodlightWall':q['lightIntensity']=100
 if p.get('manifoldPlacement'):
  place=p['manifoldPlacement'];base=copy.deepcopy(p);base.pop('manifoldPlacement');base.update(size=place['width'],depth=place['depth']);base['objects']=[dict(o,x=o['x']-place['x'],y=o['y']-place['y'])for o in p['objects']];source=parts(base);out=[]
  for q in source:
   if q.get('livingCircuit')or q['name'].startswith('Lumière ·')or q['name']=='Machines · plafond technique':continue
   if q['x']==4 and q['asset']=='Foundation_ConcretePolished_8x1'and q['y']<=20:continue
   if q['x']==8.2 and q['y']<=20:continue
   if q['x']==4 and abs(q['y']-.15)<.01:continue
   q=copy.deepcopy(q);q['x']+=place['x'];q['y']+=place['y']
   for k in ['walkStart','walkEnd','start','end']:
    if k in q:q[k][0]+=place['x'];q[k][1]+=place['y']
   out.append(q)
  out.extend(copy.deepcopy(p.get('manifoldExteriorLighting',[])))
  out.extend(entry_parts())
 return out

def entry_parts():
 from m05_architecture import DATA
 out=[]
 def module(asset,name,x,y,z,r=0):
  source=asset if any(any(q['asset']==asset for q in m['parts'])for m in DATA['modules'].values())else'Foundation_Concrete_8x4';key=next(k for k,m in DATA['modules'].items()if any(q['asset']==source for q in m['parts']));i=next(i for i,q in enumerate(DATA['modules'][key]['parts'])if q['asset']==source);a=math.radians(r+(180 if asset.startswith('Stair_')else 0))/2
  q=dict(asset=asset,name=name,component='module',sourceModule=key,sourceIndex=i,origin=[0,0,0],turn=0,quat=[0,0,math.sin(a),math.cos(a)],x=x,y=y,z=z,w=0,d=0,h=0,rotation=r,color='#aeb7b7',zone='interieur',studyLayer='interior');out.append(q);return q
 c=12+2*math.sqrt(2)
 for z in [1.55,2.55]:module('Foundation_ConcretePolished_8x1','Accueil · palier diagonal',c,c,z,45)
 for z in [1.5,2.5]:module('Foundation_ConcretePolished_8x1','Accueil · accès à la montée',12,20,z)
 module('Stair_PolishedConcrete_8x2','Accueil · escalier extérieur corrigé',12-2*math.sqrt(2),12-2*math.sqrt(2),2.05,45)
 module('CatwalkStairs','Contrôle · première volée de 4 m',12,22,3,90).update(walkStart=[12,20,3],walkEnd=[12,24,7])
 module('CatwalkRamp','Contrôle · raccord de 2 m',12,26,7,90).update(walkStart=[12,24,7],walkEnd=[12,28,9])
 module('Stair_PolishedConcrete_8x1','Contrôle · raccord final de 1 m',12,32,9.5,90).update(walkStart=[12,28,9],walkEnd=[12,36,10])
 module('CatwalkCross','Contrôle · palier d’arrivée',12,38,10)
 out.append(dict(name='Accueil · porte intérieure de la montée',asset='Wall_Door_8x4_01',component='wall',x=12,y=16.15,z=3,w=8,d=.22,h=4,rotation=0,color='#263039',zone='interieur',studyLayer='interior'))
 return out
