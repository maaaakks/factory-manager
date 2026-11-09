"""Assembly of the actual JazzFrank modules; no source geometry is scaled."""
from pathlib import Path
from functools import lru_cache
import json,copy,contextlib,io,math
import native_blueprint as n
from native_assembly import rotate
from native_compact import piece,mul
from native_factory import q
from native_connected import prop

DATA=json.loads((Path(__file__).parent/'data/m05/manifest.json').read_text(encoding='utf8'))

def turn(v,t):
 x,y,z=v
 for _ in range(t%4):x,y=-y,x
 return [x,y,z]

def layout(p):
 from native_project import ExportError
 width=p['size'];depth=p.get('depth',width);height=p.get('height',width);nx=width//40;ny=depth//40;variant=p.get('design',{}).get('variant',1)-1
 if nx<2 or ny<2 or height<40:raise ExportError(['M05 réel : 80 × 80 m minimum, hauteur 40 m. Ses modules de 40 m gardent leurs dimensions originales.'])
 if max([0]+[o.get('z',0)+(o.get('h')or 6)for o in p['objects']])>30.6:raise ExportError(['M05 : le volume intérieur libre monte jusqu’à 30,6 m. Ce plan est trop haut pour les modules originaux ; choisissez un autre style.'])
 if nx*ny>64:raise ExportError(['M05 : 64 modules maximum par assemblage pour garder une vue fluide.'])
 ox=(width-nx*40)/2;oy=(depth-ny*40)/2;placements=[];front=[1,2,3,4,5,6][variant%6];other=[2,1,4,3,6,5][variant%6]
 for obj in p['objects']:
  if obj.get('type')in['input','output']:continue
  rotated=obj.get('rotation',0)%180;w=(obj['d']if rotated else obj['w'])/2;d=(obj['w']if rotated else obj['d'])/2
  if obj['x']-w<ox+24-.01 or obj['x']+w>width-ox-24+.01 or obj['y']-d<oy+24-.01 or obj['y']+d>depth-oy-24+.01:raise ExportError(['M05 : '+obj.get('name','Bâtiment')+' empiète sur la bande de 24 m réservée aux modules. Utilisez « Réserver la marge » pour agrandir et centrer le plan.'])
 for y in range(ny):
  for x in range(nx):
   left=x==0;right=x==nx-1;top=y==0;bottom=y==ny-1;rotation=0
   if(left or right)and(top or bottom):
    name='C'+str(1 if variant%3==0 else 2 if variant%3==1 else 1 if(left==top)else 2);rotation=(0 if right else 3)if top else(1 if right else 2)
   elif top or bottom or left or right:
    side=top or bottom;index=min(x,nx-1-x)if side else min(y,ny-1-y);name='M'+str((front if index%2 else other)if side else(other if index%2 else front));rotation=0 if top else 1 if right else 2 if bottom else 3
   else:name='IN1'
   placements.append(dict(name=name,x=ox+20+x*40,y=oy+20+y*40,z=0,turn=rotation))
 return placements

def envelope(p):
 parts=[];seen=set()
 for tile in layout(p):
  for index,source in enumerate(DATA['modules'][tile['name']]['parts']):
   if not p['design']['roof']and source['asset'].startswith('Roof_'):continue
   local=turn(source['pos'],tile['turn']);pos=[local[i]+tile[k]for i,k in enumerate(['x','y','z'])]
   basis=[math.floor(v*10000+.5)for vector in [[1,0,0],[0,1,0],[0,0,1]]for v in turn(rotate(source['quat'],vector),tile['turn'])]
   key=(source['asset'],tuple(math.floor(v*1000+.5)for v in pos),tuple(basis),source.get('length',0),str(tile['x'])+','+str(tile['y'])+','+str(index)if source['asset']=='PowerLine'else'')
   if key in seen:continue
   seen.add(key)
   parts.append(dict(name=tile['name']+' · '+source['asset'],component='module',asset=source['asset'],sourceModule=tile['name'],sourceIndex=index,origin=[tile['x'],tile['y'],tile['z']],turn=tile['turn'],x=pos[0],y=pos[1],z=pos[2],w=0,d=0,h=4 if source['asset'].startswith('Wall')else 1,rotation=tile['turn']*90,color=source['color']))
 return parts

@lru_cache(maxsize=12)
def source(name):
 path=Path(__file__).parent/'data/m05'/f'{name}.sbp'
 import hashlib
 if hashlib.sha256(path.read_bytes()).hexdigest()!=DATA['modules'][name]['sha256']:raise ValueError('Le module M05 source a changé : '+name)
 with contextlib.redirect_stdout(io.StringIO()):bp=n.sbp_parse.parseBlueprint(str(path))
 return bp,[(h,o)for h,o in zip(bp[2],bp[3])if isinstance(h,n.sav_parse.ActorHeader)]

def pose_key(path,position,rotation):
 return(path,tuple(round(v,1)for v in position),tuple(round(v,4)for vector in [[1,0,0],[0,1,0],[0,0,1]]for v in rotate(rotation,vector)))

def power_points(p,bp):
 """Expected decorative electrical ports, independently transformed from source."""
 actual={pose_key(h.typePath,h.position,h.rotation):h for h in bp[2]if isinstance(h,n.sav_parse.ActorHeader)};points={};half=[p['size']/2,p.get('depth',p['size'])/2,0]
 for tile in layout(p):
  _,actors=source(tile['name']);owners={h.instanceName:h for h,o in actors};angle=q(tile['turn']*90);offset=[tile['x'],tile['y'],tile['z']]
  def transform(pos):return [(v+offset[i]-half[i])*100 for i,v in enumerate(turn([a/100 for a in pos],tile['turn']))]
  for index,(h,o)in enumerate(actors):
   descriptor=DATA['modules'][tile['name']]['parts'][index]
   if descriptor['asset']!='PowerLine':continue
   for ref,position in zip(o[4],descriptor['wire']):
    owner,suffix=ref.pathName.rsplit('.',1);original=owners[owner];target=actual.get(pose_key(original.typePath,transform(original.position),mul(angle,original.rotation)))
    if not target:raise ValueError('Support électrique M05 absent.')
    expected=[(v+offset[i]-half[i])*100 for i,v in enumerate(turn(position,tile['turn']))];key=target.instanceName+'.'+suffix
    if key in points and math.dist(points[key],expected)>.1:raise ValueError('Port M05 incohérent dans la source.')
    points[key]=expected
 return points

def add(assembly,p,assets):
 parts=envelope(p);allowed={(tuple(t['origin']),t['sourceModule'],t['sourceIndex'])for t in parts};counts=dict(total=0,walls=0,windows=0,pillars=0,trims=0,roofs=0,beams=0,modules=len(layout(p)),source='JazzFrank · modules natifs M05',wires=0)
 half=[p['size']/2,p.get('depth',p['size'])/2,0];seen={}
 for tile in layout(p):
  bp,actors=source(tile['name']);mapping={};angle=q(tile['turn']*90);offset=[tile['x'],tile['y'],tile['z']]
  def transform(pos):return [(v+offset[i]-half[i])*100 for i,v in enumerate(turn([a/100 for a in pos],tile['turn']))]
  wires=[]
  for index,(h,o)in enumerate(actors):
   descriptor=DATA['modules'][tile['name']]['parts'][index]
   if descriptor['asset']=='PowerLine':wires.append((h,o,descriptor));continue
   rotation=mul(angle,h.rotation);position=transform(h.position)
   basis=tuple(round(v,4)for vector in [[1,0,0],[0,1,0],[0,0,1]]for v in rotate(rotation,vector));key=(h.typePath,tuple(round(v,1)for v in position),basis,descriptor.get('length',0))
   if(tuple(offset),tile['name'],index)not in allowed:
    if key in seen:mapping[h.instanceName]=seen[key]
    continue
   actor=assembly.clone(piece(bp,h.instanceName),position,rotation);mapping[h.instanceName]=actor;seen[key]=actor;counts['total']+=1
   from architecture_surfaces import group,material
   import native_project as np
   role=group(dict(component='module',asset=descriptor['asset']));color=p.get('design',{}).get('colors',{}).get(role)
   if color:np.paint(actor,color)
   replacement=material(descriptor['asset'],p.get('design',{}).get('wallMaterial'))
   if replacement!=descriptor['asset']:
    from native_factory import aset
    actor[0].typePath=assets['Build_'+replacement+'_C']['path'];aset(actor,'mBuiltWithRecipe',np.ref(assets['Recipe_'+replacement+'_C']['path']),['ObjectProperty',0])
   asset=descriptor['asset'];category='roofs'if asset.startswith('Roof')else'windows'if'Window'in asset else'beams'if asset.startswith('Beam')else'walls'if asset.startswith('Wall')else'trims';counts[category]+=1
  for h,o,descriptor in wires:
   endpoints=[]
   for ref in o[4]:
    owner,suffix=ref.pathName.rsplit('.',1)
    if owner not in mapping:break
    endpoints.append(assembly.component(mapping[owner],suffix))
   if len(endpoints)!=2:raise ValueError('M05 : extrémité électrique absente dans '+tile['name'])
   if endpoints[0][0]==endpoints[1][0]:continue
   coords=[[(v+offset[i]-half[i])*100 for i,v in enumerate(turn(pt,tile['turn']))]for pt in descriptor['wire']]
   assembly.wire(*endpoints,*coords);counts['wires']+=1;counts['total']+=1
 return counts
