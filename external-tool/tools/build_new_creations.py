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
 if asset=='CatwalkStairs':
  q['fixedLayout']=True;q['walkStart']=[round(x-2*math.cos(math.radians(rot)),6),round(y-2*math.sin(math.radians(rot)),6),z];q['walkEnd']=[round(x+2*math.cos(math.radians(rot)),6),round(y+2*math.sin(math.radians(rot)),6),z+4]
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
 study=dict(collection=2,title=title,displayName=title.split(' · ')[0],category=category,subtitle=subtitle,summary=summary,description=description,dimensions=[64,48,top],resize={'width':{'min':64,'max':96,'step':8},'length':{'min':48,'max':80,'step':8}},parts=copy.deepcopy(parts),principles=principles,cutawayNames=cutaway,cutawayLayers=['roof','deck'],reference='Composition originale en pièces natives. Géométrie et export vérifiés hors du jeu ; matériaux et placement à valider dans Satisfactory.')
 catalog['studies'][key]=study
 family=dict(catalog['families']['lumen']);family.update(name=title,description=description,nativeStudy=key,hidden=False)
 catalog['families'][key]=family
 print(key,len(parts),'native parts')

# SYLVA — stepped landscape rather than a single upright front.
parts=[];seen=set();C.update(shell='#e3dfcb',steel='#566d61',dark='#68856c',accent='#bda56e',glass='#a4c8b4',deck='#7e997b')
room('Sylva',24,56,8,40,17)
for q in parts:
 if q['z']==13 and q['component']=='window':q.update(component='wall',asset='Wall_8x4_01',color=C['shell'])
for x in[28,36,44,52]:
 for y in[12,20,28,36]:
  if x in[28,36]and y in[20,28]:continue
  roof('Sylva · terrasse haute',x,y,17,'dark',zone='terrasses',layer='deck')
# Upper pavilion emerges from the terrace, offset to the left.
for side,line,us in[(3,24,[16,24]),(1,40,[16,24]),(0,16,[24,32]),(2,32,[24,32])]:
 for u in us:
  for z in[17,21]:wall('Sylva · pavillon supérieur',side,line,u,z,glass=True)
for x in[28,36]:
 for y in[20,28]:roof('Sylva · toiture du pavillon',x,y,25,'shell',zone='couronne')
# Two garden-like terraces descend to the left, their contours broken into steps.
for x,ys,height in[(20,[12,20,28,36],13),(12,[20,28,36],9)]:
 for y in ys:
  if True:roof('Sylva · gradin paysager',x,y,height,'dark',zone='terrasses',layer='deck')
  for z in range(1,height,4):wall('Sylva · soubassement',3,x-4,y-4,z,glass=5<=z<height-4,color='shell')
 for side,y in[(0,ys[0]-4),(2,40)]:
  for z in range(1,height,4):wall('Sylva · retour de gradin',side,y,x-4,z,glass=5<=z<height-4)
# Two native flights reach the lower terrace through a real roof opening.
for i in range(2):
 y=4+i*4;z=1+i*4
 module('Sylva · escalier de terrasse','CatwalkStairs',12,y,z,90,'shell',bounds=[[10,14],[y-2,y+2],[z-.2,z+5.1]])
for y in[12,16]:module('Sylva · palier de terrasse','CatwalkCross',12,y,9,0,'shell',bounds=[[10,14],[y-2,y+2],[8.85,9]])
for y in[22,26,30,34,38]:module('Sylva · garde-corps','Railing_01',8.2,y,9,0,'shell',bounds=[[8.1,8.3],[y-2,y+2],[9,10]])
# Thick, pale terrace edges and restrained planting troughs. No fake vegetation.
for x,z,y0 in[(8,9,16),(16,13,8),(56,17,8)]:
 for dx in[0,.27,.54]:beam('Sylva · rive de terrasse',[x+dx,y0,z+.25],[x+dx,40,z+.25],'shell','Beam_Painted','terrasses')
 for y in range(y0+4,40,8):
  inward=-1 if x==56 else 1
  for zz in[z+.3,z+.6,z+.9]:
   for offset in[.8,2]:beam('Sylva · jardinière vide',[x+inward*offset,y-2,zz],[x+inward*offset,y+2,zz],'steel','Beam_Painted','terrasses')
   for yy in[y-2,y+2]:beam('Sylva · jardinière vide',[x+inward*.8,yy,zz],[x+inward*2,yy,zz],'steel','Beam_Painted','terrasses')
  for yy in[y-1.5,y-.5,y+.5,y+1.5]:beam('Sylva · fond de jardinière',[x+inward*.8,yy,z+.15],[x+inward*2,yy,z+.15],'steel','Beam_Painted','terrasses')
for y in[8,40]:
 for z in[17.2,17.5]:beam('Sylva · lisière du plateau',[24,y,z],[56,y,z],'shell','Beam_Painted','terrasses')
for y in[16,32]:beam('Sylva · couronnement',[24,y,25.3],[40,y,25.3],'shell','Beam_Painted','couronne','roof')
for x in[28,36]:roof('Sylva · seuil abrité',x,4,8.8,'shell',zone='entree',layer='deck')
for x in[24,40]:beam('Sylva · appui du seuil',[x,1,1],[x,1,8.8],'shell','Beam_Painted','entree')
finish('sylva','Sylva · terrasses habitées','Organique','Un paysage en gradins','Terrasses décalées, teintes sauge et pavillon vitré en retrait.','Une architecture de paysage : les volumes descendent en gradins autour d’un pavillon haut, avec des rives claires et une palette sauge.',[['Une silhouette étagée','Trois niveaux de terrasses remplacent la façade verticale unique.'],['Un pavillon décentré','Le petit volume supérieur laisse lire un grand plateau autour de lui.'],['Des limites épaisses','Les rives claires soulignent les changements de niveau.'],['Une palette de paysage','Sauge et pierre claire ; les jardinières sont vides, sans végétation simulée.']],['Sylva · façade','Sylva · pavillon supérieur','Sylva · retour de gradin'])

# MONOLITHE — a recessed void between two opaque, massive pylons.
parts=[];seen=set();C.update(shell='#bdb7a7',steel='#4f5151',dark='#363f43',accent='#b68a58',glass='#7f9da7',deck='#a29e91')
room('Monolithe',24,56,12,40,21,color='dark')
# Side pylons are full 8 m deep volumes, not cosmetic columns.
for left,right in[(16,24),(56,64)]:
 for side,line in[(3,left+.25),(1,right-.25)]:
  for y in[8,16,24,32]:
   for z in range(1,29,4):wall('Monolithe · massif porteur',side,line,y,z,color='shell')
 for side,line in[(0,8),(2,40)]:
  for z in range(1,29,4):wall('Monolithe · tête de massif',side,line,left,z,color='shell')
 for y in[12,20,28,36]:roof('Monolithe · sommet des massifs',(left+right)/2,y,29,'shell',zone='massifs')
# A high opaque lintel spans the central opening and returns across the roof.
for side,y in[(0,8),(2,40)]:
 for x in[24,32,40,48]:
  for z in[21,25]:wall('Monolithe · linteau monumental',side,y,x,z,color='shell')
for x in[28,36,44,52]:
 for y in[12,20,28,36]:roof('Monolithe · dalle de couronnement',x,y,29,'shell',zone='couronnement')
for y in[12,28,38]:beam('Monolithe · poutre de franchissement',[24,y,24],[56,y,24],'dark','Beam_H','structure','roof')
# Deep entry reveal and a low bronze lintel establish human scale inside the void.
for x in[24.3,55.7]:
 for z in[5,9,13,17]:beam('Monolithe · embrasure',[x,8,z],[x,11.7,z],'dark','Beam_Painted','entree')
for x in[28,36,44,52]:roof('Monolithe · seuil bas',x,4,5,'dark',zone='entree',layer='deck')
for x in[24,56]:beam('Monolithe · appui du seuil',[x,.5,1],[x,.5,5],'dark','Beam_Painted','entree')
for dz in[0,.27]:beam('Monolithe · filet de bronze',[24,.5,5.2+dz],[56,.5,5.2+dz],'accent','Beam_Painted','entree')
finish('monolithe','Monolithe · porte monumentale','Brutaliste','Le plein encadre le vide','Deux massifs opaques, un couronnement haut et une entrée profondément reculée.','Une porte monumentale en pierre grise : deux massifs pleins encadrent un vide central, tandis qu’un seuil bas donne une échelle plus intime à l’entrée.',[['Des masses pleines','Deux volumes porteurs de 8 m de largeur donnent le poids visuel.'],['Un vide profond','Le vitrage se recule de quatre mètres derrière la façade monumentale.'],['Deux échelles','Le grand linteau haut surplombe un auvent d’entrée bas.'],['Un détail rare','Un seul filet bronze accompagne le seuil sombre.']],['Monolithe · façade','Monolithe · linteau monumental'])

# ASTER — a long glazed fuselage beneath sloping, swept wings.
parts=[];seen=set();C.update(shell='#e0e6e4',steel='#526d83',dark='#415f76',accent='#ce8c70',glass='#94b7c8',deck='#869aa8')
room('Aster',24,56,8,40,13)
# The central spine is glazed; wings descend in real native 2 m pitched panels.
for x in[36,44]:
 for y in[12,20,28,36]:roof('Aster · épine vitrée',x,y,17,'shell',glass=True,zone='epine')
for side,x in[(3,32),(1,48)]:
 for y in[8,16,24,32]:wall('Aster · jour de l’épine',side,x,y,13,glass=True)
for y,side in[(8,0),(40,2)]:
 for x in[32,40]:wall('Aster · nez de l’épine',side,y,x,13,glass=True)
for x,z,rot in[(12,9,180),(20,11,180),(28,13,180),(52,13,0),(60,11,0)]:
 for y in[12,20,28,36]:
  box('Aster · aile inclinée',x,y,z,8,8,2,rot,'shell','roof','Roof_Tar_03','ailes','roof');parts[-1]['slope']='roof'
 for side,y in[(0,8),(2,40)]:box('Aster · fermeture triangulaire',x,y,z,8,.22,2,rot,'shell','gable','Wall_Orange_Tris_8x2','ailes','roof')
# Swept edges and diagonal supports read as a vehicle-like shell, not a factory frame.
for y in[7.5,40.5]:
 for dy in[-.27,0,.27]:path('Aster · bord d’attaque',[[8,y+dy,9.3],[16,y+dy,11.3],[24,y+dy,13.3],[32,y+dy,15.3],[32,y+dy,17.4],[48,y+dy,17.4],[48,y+dy,15.3],[56,y+dy,13.3],[64,y+dy,11.3]],'shell',zone='ailes')
for y in[16,32]:
 for dy in[-.27,0,.27]:
  beam('Aster · appui en flèche',[10,y+dy,1],[24,y+dy,12.8],'shell','Beam_Painted','ailes')
  beam('Aster · appui en flèche',[62,y+dy,1],[56,y+dy,12.8],'shell','Beam_Painted','ailes')
for y in[12,36]:
 for x in[8.4,63.6]:beam('Aster · pied d’aile',[x,y,1],[x,y,9 if x<32 else 11],'dark','Beam_Painted','ailes')
# Low nose canopy, with a single copper-colored seam rather than luminous stripes.
for x in[28,36,44,52]:roof('Aster · nez en porte-à-faux',x,4,9,'dark',zone='nez',layer='deck')
for x in[24,56]:beam('Aster · béquille du nez',[x,.5,1],[x,3,8.8],'shell','Beam_Painted','nez')
beam('Aster · joint de nez',[24,.5,9.3],[56,.5,9.3],'accent','Beam_Painted','nez')
finish('aster','Aster · ailes en flèche','Industriel','Une coque déployée','Ailes inclinées, épine vitrée haute et appuis en diagonale.','Une architecture inspirée d’un appareil posé au sol : des ailes en pente encadrent une épine vitrée, avec un nez bas et des appuis inclinés.',[['Une toiture déployée','Les pans descendent vers les extrémités au lieu de former un couvercle plat.'],['Une épine centrale','Un bandeau vitré haut éclaire la longueur du volume.'],['Des appuis en diagonale','Les soutiens suivent la direction des ailes et dégagent le vitrage.'],['Un nez plus bas','L’entrée possède sa propre avancée et un joint cuivré discret.']],['Aster · façade','Aster · nez de l’épine','Aster · jour de l’épine'])

catalog['version']=12
(root/'data/architecture-styles.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
