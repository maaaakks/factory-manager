"""A single authored architectural study. No legacy facade generator is used."""
from pathlib import Path
import json,math,copy
root=Path(__file__).resolve().parents[1]
catalog=json.loads((root/'data/architecture-styles.json').read_text(encoding='utf-8'))
library=json.loads((root/'data/m05/manifest.json').read_text(encoding='utf-8'))['modules']
parts=[];seen=set()
C={'shell':'#d6d0bb','steel':'#293c43','dark':'#394d54','glass':'#80b6bd','accent':'#ca8d46','deck':'#69716b','light':'#e4eed9'}
def add(q):
 key=json.dumps([q['asset'],q.get('start'),q.get('end'),q['x'],q['y'],q['z'],q['rotation']],sort_keys=True)
 if key not in seen:seen.add(key);parts.append(q)
def box(name,x,y,z,w,d,h,rot,color,component,asset,zone,layer='shell'):
 add(dict(name=name,x=x,y=y,z=z,w=w,d=d,h=h,rotation=rot,color=C.get(color,color),component=component,asset=asset,zone=zone,studyLayer=layer))
def beam(name,a,b,color='steel',asset='Beam_H',zone='structure',layer='shell'):
 length=math.dist(a,b);count=math.ceil(length/16)
 for i in range(count):
  start=[round(a[j]+(b[j]-a[j])*i/count,6)for j in range(3)];end=[round(a[j]+(b[j]-a[j])*(i+1)/count,6)for j in range(3)];radius=.3 if asset=='Beam_H'else .15
  lo=[min(start[j],end[j])-radius for j in range(3)];hi=[max(start[j],end[j])+radius for j in range(3)]
  add(dict(name=name,x=(start[0]+end[0])/2,y=(start[1]+end[1])/2,z=lo[2],w=hi[0]-lo[0],d=hi[1]-lo[1],h=hi[2]-lo[2],rotation=0,color=C.get(color,color),component='beam',asset=asset,start=start,end=end,zone=zone,studyLayer=layer))
def module(name,asset,x,y,z,rot=0,color='steel',zone='circulation',bounds=None,layer='shell'):
 for source,m in library.items():
  match=next((i for i,q in enumerate(m['parts'])if q['asset']==asset),None)
  if match is not None:break
 else:raise ValueError(asset)
 a=math.radians(rot)/2
 q=dict(name=name,asset=asset,component='module',sourceModule=source,sourceIndex=match,origin=[0,0,0],turn=0,quat=[0,0,round(math.sin(a),9),round(math.cos(a),9)],x=x,y=y,z=z,w=0,d=0,h=0,rotation=rot,color=C.get(color,color),zone=zone,studyLayer=layer)
 if bounds:q['signatureBounds']=bounds
 add(q)
def wall(name,side,line,start,z,h=4,glass=False,color='shell',zone='halle'):
 x,y=(line,start+4)if side%2 else(start+4,line)
 box(name,x,y,z,8,.22,h,side*90,'glass'if glass else color,'window'if glass else'wall','Wall_Window_Thin_8x4_02'if glass else'Wall_8x4_01'if h==4 else'Wall_Orange_8x1',zone)
def roof(name,x,y,z,color='dark',glass=False,zone='halle',layer='roof'):
 box(name,x,y,z,8,8,.18,0,'glass'if glass else color,'roof','Roof_Window_01'if glass else'Roof_Tar_01',zone,layer)
def path(name,points,color='shell',zone='structure',bundle=0):
 for shift in(range(-bundle,bundle+1)if bundle else[0]):
  for a,b in zip(points,points[1:]):beam(name,[(v+shift*.27 if j==1 else v)for j,v in enumerate(a)],[(v+shift*.27 if j==1 else v)for j,v in enumerate(b)],color,'Beam_Painted',zone)


# LUMEN: continuous ivory hulls, horizontal glazing and a recessed entrance.
C.update(shell='#e8eee9',steel='#34445c',dark='#27374d',glass='#82cbd6',accent='#8de6e4',deck='#adb9bc')
# Main clear-span room. No exposed lattice, ventilation tower or industrial braces.
for side,line in [(3,24),(1,56)]:
 for u in [8,16,24,32]:
  for z in range(1,17,4):wall('Lumen · peau continue',side,line,u,z,glass=5<=z<=9,color='shell')
for side,line in [(0,8),(2,40)]:
 for u in [24,32,40,48]:
  for z in range(1,17,4):
   if side==0 and u==32 and z<9:continue
   wall('Lumen · bandeau panoramique'if 5<=z<=9 else'Lumen · coque',side,line,u,z,glass=5<=z<=9)
for x in [28,36,44,52]:
 for y in [12,20,28,36]:roof('Lumen · toit intégré',x,y,17,'shell',glass=x==44,zone='coque')
# Solid chamfered perimeter ribs: closely bundled painted beams make wide ribbons.
# Kept in the boundary planes so the actual production floor stays clear.
for y in [7.4,40.6]:
 for offset in [-.54,-.27,0,.27,.54]:
  path('Lumen · ruban de coque',[[24,y+offset,1],[24,y+offset,12],[29,y+offset,17.8],[51,y+offset,17.8],[56,y+offset,12],[56,y+offset,1]],'shell',zone='coque')
for x in[24,56]:
 for z in[4.7,13.4]:beam('Lumen · joint horizontal',[x,8,z],[x,40,z],'accent','Beam_Painted','joint')
# A broad upper visor projects ahead of the glazing, with stepped solid edges.
for x in[28,36,44,52]:
 roof('Lumen · visière en porte-à-faux',x,4,17,'shell',zone='coque')
for y in[.3,40.6]:
 for dz in[0,.27,.54,.81]:
  beam('Lumen · lèvre de coque',[24,y,17.1+dz],[56,y,17.1+dz],'shell','Beam_Painted','coque','roof')
for x in[24,56]:
 for dx in[-.27,0,.27]:
  path('Lumen · aile longitudinale',[[x+dx,.3,17.3],[x+dx,9,18.2],[x+dx,31,18.2],[x+dx,40.6,17.3]],'shell',zone='coque')
# Low asymmetric entrance pavilion. Its roof turns into an inhabited terrace.
for x in[12,20]:
 for y in[12,20]:roof('Lumen · pavillon bas',x,y,9,'shell',zone='pavillon',layer='deck')
for side,line,us in[(3,8,[8,16]),(0,8,[8,16]),(2,24,[8,16])]:
 for u in us:
  for z in[1,5]:
   if side==0 and u==16:continue
   wall('Lumen · pavillon vitré',side,line,u,z,glass=True,zone='pavillon')
for x in[8,24]:
 for y in[8,24]:beam('Lumen · retour de coque',[x,y,1],[x,y,9],'shell','Beam_Painted','pavillon')
for y in[8,24]:
 for dz in[0,.27,.54]:beam('Lumen · rive flottante',[8,y,9+dz],[24,y,9+dz],'shell','Beam_Painted','pavillon')
# Recessed ground entrance: a clear walk into the hall through the opening x32..40.
for x in[28,36,44]:roof('Lumen · porche en retrait',x,4,8.8,'shell',zone='entree',layer='deck')
for x in[32,40]:beam('Lumen · seuil lumineux',[x,1,1.02],[x,12,1.02],'accent','Beam_Painted','entree')
for x in[28,44]:beam('Lumen · appui du porche',[x,1,1],[x,1,8.8],'shell','Beam_Painted','entree')
# Rear service volume is low and enclosed; no external fans or chimney.
for y in[28,36]:
 roof('Lumen · annexe intégrée',60,y,13,'shell',zone='annexe')
 for z in[1,5,9]:wall('Lumen · annexe lisse',1,64,y-4,z,color='shell',zone='annexe')
for side,y in[(0,24),(2,40)]:
 for z in[1,5,9]:wall('Lumen · annexe lisse',side,y,56,z,color='shell',zone='annexe')
study=dict(title='Lumen · pavillon futuriste',dimensions=[64,48,32],description='Coque claire à pans coupés, bandeau panoramique et pavillon asymétrique. Étude futuriste, sans structure industrielle exposée.',parts=parts,productionRegion=[[26,54],[14,38],[1,24]],reference='Composition originale en pièces natives. Matériaux et lumière à valider en jeu.')
study.update(resize={'width':{'min':64,'max':96,'step':8},'length':{'min':48,'max':80,'step':8}},category='Futuriste')
catalog.setdefault('studies',{})['lumen']=study
family=dict(catalog['families']['atlas']);family.update(name=study['title'],description=study['description'],nativeStudy='lumen')
catalog['families']['lumen']=family
catalog['families']['atlas']['name']='Atlas · halle industrielle'
catalog['version']=max(11,catalog.get('version',0))
(root/'data/architecture-styles.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Lumen:',len(parts),'native parts')
