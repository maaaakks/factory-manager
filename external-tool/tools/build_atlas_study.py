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

# HALLE: a tall working room with a recessed central glazed wall and two piers.
# Only two dark stone-like piers carry infill; most of the front stays open.
for u in[24,48]:
 for z in range(1,25,4):wall('Halle · pile latérale',0,8.8,u,z,glass=z>=17,color='dark')
for u in[32,40]:
 for z in range(9,25,4):wall('Atrium · vitrage en retrait',0,12,u,z,glass=True,zone='atrium')
 # Upper glazing return to the face plane, built as narrow native beam courses.
for x in[32,48]:
 for i in range(54):
  z=9.15+i*.3
  beam('Atrium · tableau profond',[x,8.9,z],[x,11.8,z],'shell','Beam_Painted','atrium')
for side,line in[(3,24.5),(1,55.5)]:
 for u in[8,16,24,32]:
  for z in range(1,25,4):
   if side==3 and(z<13 or(u==16 and z==13)):continue # Open gallery and real upper doorway.
   wall('Halle · flanc',side,line,u,z,glass=z>=17 or(side==3 and u==16),color='dark'if z<9 else'shell')
for u in[24,32,40,48]:
 for z in range(1,25,4):wall('Halle · fond',2,39.5,u,z,glass=z>=17,color='dark'if z<9 else'shell')

# Roof hierarchy: two low wings and a single high glazed lantern, no full-grid skylight.
for x in[28,36,44,52]:
 for y in[12,20,28,36]:
  if x in[36,44]:roof('Halle · couverture',x,y,29,glass=True,zone='lanterneau')
  else:box('Halle · pan incliné',x,y,25,8,8,2,180 if x==28 else 0,'dark','roof','Roof_Tar_03','halle','roof');parts[-1]['slope']='roof'
for x in[28,52]:
 for y in[8,40]:box('Halle · fermeture du pignon',x,y,25,8,.22,2,180 if x==28 else 0,'dark','gable','Wall_Orange_Tris_8x2','halle','roof')
for x in[32,48]:
 for y in[8,16,24,32]:wall('Lanterneau · jour latéral',3 if x==32 else 1,x,y,25,glass=True,zone='lanterneau')
for y,side in[(8,0),(40,2)]:
 for x in[32,40]:wall('Lanterneau · fermeture vitrée',side,y,x,25,glass=True,zone='lanterneau')

# Two deeply separated load-bearing front frames, with visible angled shoulders.
for y,color,bundle in[(6.5,'shell',2),(10,'steel',0)]:
 path('Portique · épaules facettées',[[25,y,1],[25,y,19],[30,y,25.2],[50,y,25.2],[55,y,19],[55,y,1]],color,bundle=bundle)
for x in[25,55]:
 for z in[5,13,19]:beam('Portique · entretoise',[x,6.2,z],[x,10.3,z],'steel')
for x in[24.5,55.6]:
 for y in[17,29,38]:beam('Halle · poteau porteur',[x,y,1],[x,y,25.1],'steel')
for y in[17,29,38]:
 beam('Halle · traverse de charpente',[25,y,24],[55,y,24],'steel')
 for x in[32.2,47.8]:beam('Lanterneau · appui de charpente',[x,y,24],[x,y,29],'steel',layer='roof')
 for x in[25,51]:beam('Halle · console',[x,y,21],[x+4,y,24],'steel')

# An open, low left gallery: the upper deck is also the viewing terrace.
for x in[12,20]:
 for y in[20,28,36]:
  if(x,y)==(12,20):continue # real 8 m opening above the stair, filled locally below
  roof('Galerie · terrasse accessible',x,y,12.9,zone='galerie',layer='deck')
for x in[8.5,23.5]:
 for y in[16.5,24.5,39.5]:
  beam('Galerie · poteau',[x,y,1],[x,y,12.9],'shell')
for y in[16.5,39.5]:beam('Galerie · poutre de rive',[8.5,y,12.5],[23.5,y,12.5],'steel')
for u in[16,24,32]:
 for z in[1,5,9]:wall('Galerie · paroi ajourée',3,8.6,u,z,glass=z>=5,zone='galerie')
# Three actual 4 x 4 m native stairs, 4 m rise each, continuous from 1 to 13 m.
for i in range(3):
 y=8+i*4;z=1+i*4
 module('Galerie · escalier vers la terrasse','CatwalkStairs',12,y,z,90,bounds=[[10,14],[y-2,y+2],[z-.2,z+5.1]])
for x,y,z in[(12,20,13),(16,20,13),(16,32,13),(12,36,13)]:
 module('Galerie · palier','CatwalkCross',x,y,z,0,bounds=[[x-2,x+2],[y-2,y+2],[z-.15,z]])
for y in[18,22,26,30,34,38]:module('Terrasse · garde-corps extérieur','Railing_01',8.2,y,13,0,bounds=[[8.1,8.3],[y-2,y+2],[13,14]])
for x in[10,14,18,22]:module('Terrasse · garde-corps avant','Railing_01',x,16.2,13,90,bounds=[[x-2,x+2],[16.1,16.3],[13,14]])
for y in[18,22]:module('Terrasse · protection de la trémie','Railing_01',16.1,y,13,0,bounds=[[16,16.2],[y-2,y+2],[13,14]])
module('Galerie · porte vers la halle','Wall_Door_8x4_03',24.2,20,13,0,'shell',bounds=[[24.1,24.3],[16,24],[13,17]])
roof('Halle · belvédère intérieur',28,20,12.9,zone='galerie',layer='deck')
for y in[18,22]:module('Belvédère · garde-corps','Railing_01',31.8,y,13,0,bounds=[[31.7,31.9],[y-2,y+2],[13,14]])
for x in[26,30]:
 for y in[16.2,23.8]:module('Belvédère · garde-corps','Railing_01',x,y,13,90,bounds=[[x-2,x+2],[y-.1,y+.1],[13,14]])

# A clearly separate right service spine with a raised plant tower.
for side,line in[(1,63.4),(3,56.5)]:
 for y in[16,24,32]:
  for z in range(1,17,4):wall('Bande technique · bardage',side,line,y,z,color='steel',zone='technique')
for side,y in[(0,16.5),(2,39.5)]:
 for z in range(1,17,4):wall('Bande technique · pignon',side,y,56,z,color='steel',zone='technique')
for y in[20,28,36]:roof('Bande technique · couverture',60,y,17,zone='technique')
for y in[20,28]:
 # Wall-normal +X, set upward by a -90 degree local Y rotation.
 module('Bande technique · extracteur','LargeVent',60,y,17.4,0,'accent','technique',[[58.4,61.6],[y-1.6,y+1.6],[17.1,18.1]])
 parts[-1]['quat']=[0,-.707106781,0,.707106781]
for z in range(17,29,4):
 for side,line,start in[(0,32.5,56),(2,39.5,56),(1,63.4,32),(3,56.5,32)]:wall('Tour technique · couronnement',side,line,start,z,color='dark',zone='tour')
roof('Tour technique · chapeau',60,36,29,zone='tour')
for z in[19,23,27]:module('Tour technique · ventilation','LargeFan',63.55,36,z,0,'accent','tour',[[63.3,63.8],[34.5,37.5],[z-1.5,z+1.5]])
for z in[17.4,28.5]:beam('Tour technique · liseré',[56.7,32.1,z],[63.1,32.1,z],'accent','Beam_Painted','tour')

# Forecourt: an entrance canopy on canted supports and a protected pedestrian lane.
for x in[12,20]:roof('Accueil · auvent bas',x,4,9,'shell',zone='accueil')
for x in[9,22.5]:
 path('Accueil · appui oblique',[[x,8,1],[x,8,5.2],[x,4,8.5]],'shell',bundle=1,zone='accueil')
for x in[12,20]:beam('Accueil · porte-à-faux',[x,9,8.4],[x,.5,8.4],'steel',zone='accueil')
for x in[36,44]:roof('Atrium · marquise en retrait',x,8,8.8,'dark',zone='atrium')
beam('Accueil · filet de rive',[8.5,.5,9.25],[23.5,.5,9.25],'accent','Beam_Painted','accueil')
# Three-dimensional native beam markings, not a painted emissive mock-up.
for y in range(2,16,2):beam('Parvis · guide piéton',[25.6,y,.99],[25.6,y+1,.99],'accent','Beam_Painted','parvis')
for x in range(28,52,4):beam('Parvis · seuil',[x,3,.99],[x+2,3,.99],'shell','Beam_Painted','parvis')

# Roof edge thickness and controlled louvers, not an even decorative grid.
for y in[8,40]:
 for x0,x1,z0,z1 in[(24.5,31.5,25.4,27.2),(32.5,47.5,29.4,29.4),(48.5,55.5,27.2,25.4)]:beam('Halle · rive épaisse',[x0,y,z0],[x1,y,z1],'shell','Beam_Painted','halle','roof')
for y in[22,26,30,34]:
 for z in[4.5,5,5.5,6]:beam('Bande technique · persienne',[63.65,y-1.5,z],[63.65,y+1.5,z],'accent','Beam_Painted','technique')
for y in[12,24,36]:
 module('Halle · projecteur de paroi','FloodlightWall',54.9,y,21,180,'light','eclairage',[[54.6,55.2],[y-.5,y+.5],[21,21.5]])

study=dict(title='Halle Atlas · étude 01',dimensions=[64,48,32],description='Halle haute, atrium en retrait, galerie basse et terrasse desservie par un escalier. Composition fixe de 64 × 48 m.',parts=parts,productionRegion=[[26,54],[14,38],[1,24]],reference='Composition originale. Quelques pièces natives isolées utilisent les gabarits M05 de JazzFrank déjà documentés dans le projet, sans réutiliser son assemblage.')
study.update(resize={'width':{'min':64,'max':96,'step':8},'length':{'min':48,'max':80,'step':8}},category='Industriel')
catalog.setdefault('studies',{})['atlas']=study
catalog['families']['signature']['hidden']=True
catalog['groups']['signature']='Chapitre II · Architectures composées'
atlas=dict(catalog['families']['signature']);atlas.update(name='Halle Atlas · étude 01',description=study['description'],hidden=False,nativeStudy='atlas',facadeForm='flat',roofForm='flat',roofStyle='tar',detail='none',structure='none',wallDecoration='none',fit='plot',palettes=['signature-chalk'])
catalog['families']['atlas']=atlas;catalog['version']=max(11,catalog.get('version',0))
(root/'data/architecture-styles.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Atlas authored: {len(parts)} native parts; {len(set(p["zone"]for p in parts))} functional/design zones.')

