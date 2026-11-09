"""Procedural 8 m bays with real M05 glazing, steel members and source fans."""
import math
from m05_architecture import DATA,source
from native_compact import piece
def profile(seed,side):
 front=((seed-1)//3)%4;secondary=(front+1)%4
 return (seed-1)%3 if side==front else seed%3 if seed%2==0 and side==secondary else -1

def recess(x,y,z,h,top,b,seed):
 x0,x1,y0,y1=b;front=((seed-1)//3)%4
 for side in range(4):
  motif=profile(seed,side);edge=[y==y0,x==x1,y==y1,x==x0][side];u=y if side%2 else x;lo=y0 if side%2 else x0;hi=y1 if side%2 else x1;mid=math.floor((lo+hi)/2)
  if motif<0 or not edge or hi-lo<2 or z<4 or z+h>top-4:continue
  if motif==0 and u==mid and z>=8:return True
  if motif==1 and lo<u<hi and u!=mid and z>=8:return True
  if motif==2 and u==mid and math.floor(z/4)%4 not in[0,3]:return True
 return seed%2==0 and x1-x0>=3 and y1-y0>=3 and z>=top-8 and z+h<=top-4 and((front<2 and x==x1 and y==y0)or(front>=2 and x==x0 and y==y1))

def window_at(start,side,z,top,size,seed):
 bay=math.floor(start/8);n=size/8;motif=profile(seed,side);center=abs(bay-(n-1)/2)<1;corner=bay==0 or bay==n-1
 if corner:return z>=4 and z<top-4
 if motif==0:return z==4 or z>=top-8
 if motif==1:return center and z>=4 or z>=top-4
 if motif==2:return math.floor(z/4)%3!=0
 return z==4 or z>=top-4
def decorate(parts,p,paths=None):
 columns=[q for q in parts if q['name']=='Angle · montant unique'];result=[]
 for q in parts:
  if q['name']=='Angle · bardage ajusté':
   a=list(q['start']);b=list(q['end']);axis=0 if abs(b[0]-a[0])>.01 else 1
   for v in[a,b]:
    if any(math.hypot(v[0]-c['x'],v[1]-c['y'])<.6 for c in columns):v[axis]+=(1 if b[axis]>a[axis]else-1)*(-.25 if v is a else .25)
   for dz in[-.32,0,.32]:
    start=[a[0],a[1],a[2]+dz];end=[b[0],b[1],b[2]+dz];lo=[min(v,end[i])-.15 for i,v in enumerate(start)];hi=[max(v,end[i])+.15 for i,v in enumerate(start)];result.append(dict(q,asset='Beam_Painted',start=start,end=end,x=(start[0]+end[0])/2,y=(start[1]+end[1])/2,z=lo[2],w=hi[0]-lo[0],d=hi[1]-lo[1],h=hi[2]-lo[2],panelUnits=(q.get('panelUnits')or 0)/3))
  else:result.append(dict(q,asset='Wall_Window_Thin_8x4_02')if q['component']=='window'and q['h']==4 else dict(q,asset='Beam_H')if q['component']=='beam'else q)
 for q in parts:
  side=q['rotation']/90;seed=p['design'].get('seed',1);motif=profile(seed,side)
  if motif<0 or q['component']!='wall'or q['h']!=4 or q['z']<4 or q['z']%8!=0:continue
  module=['M3','M4','M6'][motif];index=next((i for i,p in enumerate(DATA['modules'][module]['parts'])if p['asset']=='LargeFan'),-1)
  if index<0:continue
  a=math.radians(q['rotation']-90);clamp=lambda v,n:round(max(.6,min(n-.6,v)),9)
  result.append(dict(name=module+' · Ventilation',component='module',asset='LargeFan',sourceModule=module,sourceIndex=index,origin=[0,0,0],turn=0,quat=[0,0,round(math.sin(a/2),9),round(math.cos(a/2),9)],x=clamp(q['x']+math.cos(a)*.35,p['size']),y=clamp(q['y']+math.sin(a)*.35,p.get('depth',p['size'])),z=q['z']+2,w=0,d=0,h=0,rotation=q['rotation']-90,color='#ef922b'))
 from m05_facade import apply
 from m05_roof import apply as roof_details
 return roof_details(apply(result,p,paths or []),p,paths or [])
def add_piece(assembly,part,project,assets=None):
 if part.get('nativeShell'):
  import native_project as p,re
  from native_factory import aset
  asset=part['asset'];recipe=part['nativeRecipe']
  if not re.match(r'^(Wall_|Roof_|Foundation|Pillar|Fence_|Catwalk|QuarterPipe)',asset) or 'Build_'+asset+'_C' not in assets or recipe not in assets:raise p.ExportError(['Pièce architecturale importée inconnue.'])
  actor=assembly.clone(p.load('native-design-template.json')['piece'],[(part['x']-project['size']/2)*100,(part['y']-project.get('depth',project['size'])/2)*100,part['z']*100],part['quat'])
  actor[0].typePath=assets['Build_'+asset+'_C']['path'];aset(actor,'mBuiltWithRecipe',p.ref(assets[recipe]['path']),['ObjectProperty',0]);p.paint(actor,part['color'])
  finish=part.get('paintFinish','')
  if finish:
   allowed='/Game/FactoryGame/Buildable/-Shared/Customization/PaintFinishes/Metals/'
   if finish not in [allowed+'PaintFinishDesc_'+m+'.PaintFinishDesc_'+m+'_C' for m in ['Copper','Caterium']]:raise p.ExportError(['Finition métallique importée inconnue.'])
   customization=dict(actor[1][2])['mCustomizationData'];override=dict(customization[0])['OverrideColorData'];override[0].append(['PaintFinish',p.ref(finish)]);override[1].append(['PaintFinish','ObjectProperty',0]);customization[0][0][1]=p.ref(finish)
  return actor
 if part['asset']in['Foundation_ConcretePolished_8x1','Stair_PolishedConcrete_8x2','Stair_PolishedConcrete_8x1']:
  import native_project as p
  from native_factory import aset
  actor=assembly.clone(p.load('native-design-template.json')['piece'],[(part['x']-project['size']/2)*100,(part['y']-project.get('depth',project['size'])/2)*100,part['z']*100],part['quat'])
  actor[0].typePath=assets['Build_'+part['asset']+'_C']['path'];aset(actor,'mBuiltWithRecipe',p.ref(assets['Recipe_'+part['asset']+'_C']['path']),['ObjectProperty',0]);p.paint(actor,part['color']);return actor
 if part.get('emissiveSign'):
  from native_signs import add
  return add(assembly,part,project,assets)
 bp,actors=source(part['sourceModule']);h,o=actors[part['sourceIndex']]
 actor=assembly.clone(piece(bp,h.instanceName),[(part['x']-project['size']/2)*100,(part['y']-project.get('depth',project['size'])/2)*100,part['z']*100],part['quat'])
 import native_project as p
 from native_factory import aset
 if assets and part['asset']!=DATA['modules'][part['sourceModule']]['parts'][part['sourceIndex']]['asset']:
  actor[0].typePath=assets['Build_'+part['asset']+'_C']['path'];aset(actor,'mBuiltWithRecipe',p.ref(assets['Recipe_'+part['asset']+'_C']['path']),['ObjectProperty',0])
 if part.get('lightIntensity')is not None:
  aset(actor,'mLightControlData',[[['ColorSlotIndex',0],['Intensity',part['lightIntensity']/5],['IsTimeOfDayAware',False]],[['ColorSlotIndex','IntProperty',0],['Intensity','FloatProperty',0],['IsTimeOfDayAware','BoolProperty',0]]],['StructProperty',0,'LightSourceControlData',None,0])
 p.paint(actor,part['color'])
 return actor

