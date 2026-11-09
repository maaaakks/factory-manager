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


def room(prefix,left,right,front,back,top,color='shell',glazing=True):
 for side,line in [(3,left),(1,right)]:
  for y in range(front,back,8):
   for z in range(1,top,4):wall(prefix+' · flanc',side,line,y,z,glass=glazing and z>=5,color=color)
 for side,line in [(0,front),(2,back)]:
  for x in range(left,right,8):
   for z in range(1,top,4):
    if side==0 and x in[24,32]and z<9:continue
    wall(prefix+' · façade'if side==0 else prefix+' · fond',side,line,x,z,glass=glazing and z>=5,color=color)

def finish(key,title,category,subtitle,summary,description,principles,cutaway,top=32):
 study=dict(collection=3,title=title,displayName=title.split(' · ')[0],category=category,subtitle=subtitle,summary=summary,description=description,dimensions=[64,48,top],resize={'width':{'min':64,'max':96,'step':8},'length':{'min':48,'max':80,'step':8}},parts=copy.deepcopy(parts),principles=principles,cutawayNames=cutaway,cutawayLayers=['roof','deck'],reference='Composition originale en pièces natives. Géométrie et export vérifiés hors du jeu ; matériaux et placement à valider dans Satisfactory.')
 catalog['studies'][key]=study
 family=dict(catalog['families']['lumen']);family.update(name=title,description=description,nativeStudy=key,hidden=False)
 catalog['families'][key]=family
 print(key,len(parts),'native parts')


# Flat roof assets are rotated as real native panels. Their 8 m edges retain
# their length; signatureBounds describe the rotated geometry for collisions.
def profile(points):
 return [(round(x,8),round(z,8))for x,z in points]

def shell(prefix,points,ys,glass_segments=()):
 for index,(a,b)in enumerate(zip(points,points[1:])):
  dx,dz=b[0]-a[0],b[1]-a[1];assert abs(math.hypot(dx,dz)-8)<1e-6
  angle=math.atan2(dz,dx);cx,cz=(a[0]+b[0])/2,(a[1]+b[1])/2
  for y in ys:
   asset='Roof_Window_01'if index in glass_segments else'Roof_Tar_01'
   module(prefix+' · panneau de coque',asset,cx,y,cz,0,'glass'if index in glass_segments else'shell',zone='coque',bounds=[[min(a[0],b[0])-.15,max(a[0],b[0])+.15],[y-4,y+4],[min(a[1],b[1])-.15,max(a[1],b[1])+.15]],layer='roof')
   parts[-1]['quat']=[0,-math.sin(angle/2),0,math.cos(angle/2)]
   if abs(angle)>.001:parts[-1]['repeatWidth']=False
 for y in[ys[0]-4,ys[-1]+4]:
  for dy in[-.27,0,.27]:
   for a,b in zip(points,points[1:]):
    beam(prefix+' · rive de coque',[a[0],y+dy,a[1]],[b[0],y+dy,b[1]],'shell','Beam_Painted','coque','roof')
    if abs(b[1]-a[1])>.001:parts[-1]['repeatWidth']=False

def roof_height(points,x):
 for a,b in zip(points,points[1:]):
  if a[0]-1e-7<=x<=b[0]+1e-7:return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
 raise ValueError(x)

def end_skin(prefix,points,y,back=False,entry=False):
 # Rectangular native glazing stays entirely below the polygonal roof.
 # The remaining caps are closed with contiguous native painted beam courses.
 lo,hi=points[0][0],points[-1][0]
 cuts=[lo]+[float(x)for x in range(0,65,8)if lo+1e-6<x<hi-1e-6]+[hi]
 for left,right in zip(cuts,cuts[1:]):
  samples=[roof_height(points,left),roof_height(points,right)]+[p[1]for p in points if left<p[0]<right]
  minimum,maximum=min(samples),max(samples);top=1
  if abs(right-left-8)<1e-6:
   for z in range(1,29,4):
    if z+4>minimum-.12:break
    top=z+4
    if entry and left in[24,32]and z<9:continue
    wall(prefix+' · verrière de pignon',2 if back else 0,y,left,z,glass=True)
  z=top+.15
  while z<maximum-.08:
   intervals=[]
   for a,b in zip(points,points[1:]):
    l,r=max(left,a[0]),min(right,b[0])
    if r-l<.1:continue
    za,zb=roof_height(points,l),roof_height(points,r)
    if max(za,zb)<z:continue
    if min(za,zb)<z:
     cross=a[0]+(z-a[1])*(b[0]-a[0])/(b[1]-a[1])
     if za<z:l=max(l,cross)
     else:r=min(r,cross)
    if r-l>.15:
     if intervals and l-intervals[-1][1]<.01:intervals[-1][1]=r
     else:intervals.append([l,r])
   for l,r in intervals:
    beam(prefix+' · tympan ajusté',[l,y,z],[r,y,z],'shell','Beam_Painted','pignons')
    parts[-1]['repeatWidth']=False
    if l<40 and abs(r-40)<1e-6:parts[-1]['stretchWidthEnd']=True
   z+=.28

# PRISME — two unequal crystalline volumes, with genuine pitched planar facets.
parts=[];seen=set();C.update(shell='#d9e4e8',steel='#344e6b',dark='#233d58',glass='#85b7cd',accent='#537da7',deck='#9aaeb8')
points=[(24,13)]
for angle in[45,45,0,-45,-45]:
 a=points[-1];points.append((a[0]+8*math.cos(math.radians(angle)),a[1]+8*math.sin(math.radians(angle))))
points=profile(points);shell('Prisme',points,[12,20,28,36],glass_segments=[1,2])
for side,line in[(3,points[0][0]),(1,points[-1][0])]:
 for y in[8,16,24,32]:
  for z in[1,5,9]:
   wall('Prisme · flanc du cristal',side,line,y,z,glass=z>=5)
end_skin('Prisme',points,8,entry=True);end_skin('Prisme',points,40,back=True)
for x in[24,40]:beam('Prisme · guide du seuil',[x,1,1.02],[x,8,1.02],'accent','Beam_Painted','entree')
finish('prisme','Prisme · cristal facetté','Futuriste','Des plans qui captent la lumière','Un volume facetté, des pans obliques et une faille vitrée dans la toiture.','Un volume cristallin unique enveloppe la production. Ses pans inclinés portent un vitrage oblique, avec des pignons ajustés au profil.',[['Un volume sculpté','Une seule silhouette facettée, dégagée de tout pavillon secondaire.'],['Des facettes réelles','Les panneaux natifs de 8 m sont inclinés sans être déformés.'],['Une faille vitrée','Le vitrage suit un pan oblique avant de rejoindre le sommet.'],['Des pignons ajustés','Les fenêtres restent sous la pente ; des cours de poutres ferment les pointes.']],['Prisme · verrière de pignon','Prisme · tympan ajusté'])

# CANOPÉE — a continuous vault with seven facets, unlike Sylva's stacked terraces.
parts=[];seen=set();C.update(shell='#dfd6bd',steel='#6a715e',dark='#5a6b59',glass='#a5beb1',accent='#b38d67',deck='#9ea38c')
angles=[60,40,20,0,-20,-40,-60]
span=sum(8*math.cos(math.radians(a))for a in angles);points=[(36-span/2,5)]
for angle in angles:
 a=points[-1];points.append((a[0]+8*math.cos(math.radians(angle)),a[1]+8*math.sin(math.radians(angle))))
points=profile(points);shell('Canopée',points,[12,20,28,36],glass_segments=[3])
for side,x in[(3,points[0][0]),(1,points[-1][0])]:
 for y in[8,16,24,32]:wall('Canopée · soubassement courbe',side,x,y,1,color='dark')
end_skin('Canopée',points,8,entry=True);end_skin('Canopée',points,40,back=True)
# The entrance repeats the curved profile at a much smaller height in beam ribs.
for y in[2,5.5]:
 path('Canopée · porche arrondi',[[24,y,1],[24,y,5],[26,y,7.5],[29,y,9],[35,y,9],[38,y,7.5],[40,y,5],[40,y,1]],'shell',bundle=2,zone='entree')
for x in[28,36]:roof('Canopée · ombre du porche',x,4,8.7,'dark',zone='entree',layer='deck')
for x in[24,40]:beam('Canopée · seuil minéral',[x,1,1.01],[x,8,1.01],'accent','Beam_Painted','entree')
for q in parts:
 if q['zone']=='entree':q['fixedLayout']=True
finish('canopee','Canopée · coque enveloppante','Organique','Une courbe habitée','Une voûte douce, une verrière au sommet et un porche arrondi.','Une coque continue enveloppe la halle. Sept facettes dessinent une voûte douce, soulignée par des rives épaisses et un petit porche arrondi à l’entrée.',[['Une silhouette continue','La toiture remplace les volumes superposés par une grande enveloppe.'],['Des courbes par facettes','Sept panneaux inclinés composent le profil, sans étirer les pièces natives.'],['Une lumière zénithale','La bande vitrée occupe le sommet presque horizontal de la voûte.'],['Une entrée à petite échelle','Un porche arrondi reprend le geste de la grande coque.']],['Canopée · verrière de pignon','Canopée · tympan ajusté'])

# BASTION — low opaque strata, a lateral courtyard and broad sheltered entries.
parts=[];seen=set();C.update(shell='#a99f8c',steel='#51504b',dark='#353b3a',glass='#829996',accent='#c2ab83',deck='#837c6d')
room('Bastion',24,56,16,40,13,color='dark')
parts=[q for q in parts if not(q['name']=='Bastion · façade'and q['z']<5)]
# The main roof projects 8 m forward, but stays only 17 m above the ground.
for x in[28,36,44,52]:
 for y in[12,20,28,36]:roof('Bastion · dalle en porte-à-faux',x,y,17,'shell',zone='dalles')
for side,line,us in[(0,8,[24,32,40,48]),(2,40,[24,32,40,48]),(3,24,[8,16,24,32]),(1,56,[8,16,24,32])]:
 for u in us:wall('Bastion · strate haute',side,line,u,13,color='shell')
# A ground-level through courtyard replaces the second tower of Monolithe.
for side,line in[(3,8),(1,24)]:
 for y in[8,16,24,32]:
  for z in[1,5]:
   if side==1 and y>=16:continue
   wall('Bastion · mur de cour',side,line,y,z,color='shell')
for y,top in[(8,13),(32,9)]:
 for x in[12,20]:roof('Bastion · aile basse',x,y+4,top,'shell',zone='ailes')
 for side,line in[(0,y),(2,y+8)]:
  for x in[8,16]:
   for z in range(1,top,4):
    if x==16 and z<9:continue
    wall('Bastion · retour des ailes',side,line,x,z,color='shell')
 for z in range(9,top,4):wall('Bastion · flanc de l’aile',3,8,y,z,color='shell')
# Low service block on the right, treated as an opaque horizontal volume.
for y in[20,28,36]:
 roof('Bastion · annexe basse',60,y,9,'dark',zone='annexe')
 for z in[1,5]:wall('Bastion · annexe opaque',1,63.7,y-4,z,color='shell')
for side,y in[(0,16),(2,40)]:
 for z in[1,5]:wall('Bastion · retour d’annexe',side,y,56,z,color='shell')
for x in[24,56]:
 for y in[8.2,39.8]:
  for dx in[-.27,0,.27]:beam('Bastion · appui massif',[x+dx,y,1],[x+dx,y,17],'shell','Beam_Painted','structure')
for y in[8,40]:
 for z in[13.1,17.25]:beam('Bastion · joint de strate',[24,y,z],[56,y,z],'dark','Beam_Painted','dalles')
for y in[12,28,36]:beam('Bastion · couronnement de cour',[8,y,9.2],[24,y,9.2],'accent','Beam_Painted','cour')
finish('bastion','Bastion · cour et strates','Brutaliste','L’horizon plutôt que la tour','Dalles épaisses, ailes basses et cour traversante à l’échelle du sol.','Une architecture basse ancrée dans le terrain. De grandes dalles protègent une façade reculée, tandis que deux ailes encadrent une cour traversante à gauche.',[['Une composition horizontale','La dalle principale reste basse et s’avance largement devant le vitrage.'],['Une cour traversante','Un passage au niveau du sol relie les deux ouvertures de l’aile gauche.'],['Des masses stratifiées','Les bandeaux pleins et les volumes secondaires dessinent plusieurs horizons.'],['Des ombres profondes','Le vitrage sombre se recule sous les dalles plutôt que de couvrir la façade.']],['Bastion · façade','Bastion · strate haute'])

catalog['version']=13
(root/'data/architecture-styles.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')




