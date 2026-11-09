"""Deterministic architectural compositions shared with WorkshopDesign rules."""
def roof_composition(size,seed,layout='auto',available=None,depth=None):
 if depth is not None and depth!=size:
  nx=size//8;ny=depth//8;n=min(nx,ny);base=roof_composition(n*8,seed,layout);cells=set()
  for k in base['cells']:
   x,y=map(int,k.split(','));cells.add(f'{int(x*(nx-1)/max(1,n-1)+.5)},{int(y*(ny-1)/max(1,n-1)+.5)}')
  if base['kind']=='band':cells={f'{x},{y}'for x in range((nx-1)//2,(nx//2)+1)for y in range(ny)}
  return dict(base,cells=sorted(cells))
 n=size//8;names=['central','pair','quartet','triple','band','ring'];kind=names[(seed-1)%6] if layout=='auto' else layout
 large=((seed-1)//6)%2==1;turn=((seed-1)//12)%2==1;cells=set()
 def put(x,y):
  if turn:x,y=y,x
  if 0<=x<n and 0<=y<n:cells.add(f'{x},{y}')
 def rect(x,y,w,h):
  for i in range(x,x+w):
   for j in range(y,y+h):put(i,j)
 span=min(n-2,(3 if large else 1)if n%2 else(4 if large else 2));lo=(n-span)//2;mid=[n//2]if n%2 else[n//2-1,n//2]
 if kind=='central':rect(lo,lo,span,span)
 if kind=='pair':
  for x in [0,n-1]:rect(x,lo,1,span)
 if kind=='quartet':
  w=2 if large and n>=6 else 1
  for x in [0,n-w]:
   for y in [0,n-w]:rect(x,y,w,w)
 if kind=='triple':
  if n>=5:
   for x in [0,*mid,n-1]:rect(x,lo,1,span)
  else:
   for x in mid:put(x,0)
   put(0,n-1);put(n-1,n-1)
 if kind=='band':rect(lo,0,span,n)
 if kind=='ring':
  w=n-2 if n>=5 else n;a=(n-w)//2
  for x in range(a,a+w):
   for y in range(a,a+w):
    if x in [a,a+w-1]or y in [a,a+w-1]:put(x,y)
 labels=dict(central='Puits central',pair='Deux verrières symétriques',quartet='Quatre puits symétriques',triple='Trois puits alignés'if n>=5 else'Trois puits en triangle',band='Verrière longitudinale',ring='Couronne vitrée')
 if available is not None and any(tuple(map(int,k.split(',')))not in available for k in cells):return roof_composition(size,seed,'central')
 return dict(kind=kind,label=labels[kind],cells=sorted(cells),large=large,turn=turn)

def footprint(project,design):
 if project.get('generation',{}).get('shape')=='exotic':design=dict(design,footprint='l',fit='plot')
 import math
 from blueprint_dimensions import dimensions
 width,depth,height=dimensions(project);nx=width//8;ny=depth//8;cells={(x,y)for x in range(nx)for y in range(ny)};paths=access_paths(project)
 if design.get('fit')=='occupied'and project['objects']:
  used=set()
  def mark(x0,y0,x1,y1):
   for x in range(max(0,math.floor((x0-4)/8)),min(nx-1,math.floor((x1+4-1e-7)/8))+1):
    for y in range(max(0,math.floor((y0-4)/8)),min(ny-1,math.floor((y1+4-1e-7)/8))+1):used.add((x,y))
  for o in project['objects']:
   w,d=(o['d'],o['w'])if o['rotation']%180 else(o['w'],o['d']);mark(o['x']-w/2,o['y']-d/2,o['x']+w/2,o['y']+d/2)
  for pts in paths:
   for i,b in enumerate(pts):
    a=pts[max(0,i-1)];mark(min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1]))
  outside=set();queue=[]
  for k in sorted(cells):
   x,y=k
   if(x==0 or y==0 or x==nx-1 or y==ny-1)and k not in used:outside.add(k);queue.append(k)
  for x,y in queue:
   for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
    k=(x+dx,y+dy)
    if 0<=k[0]<nx and 0<=k[1]<ny and k not in used and k not in outside:outside.add(k);queue.append(k)
  cells-=outside
 offset_x=min(x for x,y in cells)if design.get('fit')=='occupied'else 0;offset_y=min(y for x,y in cells)if design.get('fit')=='occupied'else 0
 if design.get('fit')=='occupied':nx=max(x for x,y in cells)-offset_x+1;ny=max(y for x,y in cells)-offset_y+1
 kind=design['footprint'];turn=0 if kind=='stepped'or project.get('generation',{}).get('shape')=='exotic'else((design['variant']-1)//3)%4
 def cut(x,y):
  if nx<3 or ny<3:return False
  if kind=='stepped':return x in[0,nx-1]and y in[0,ny-1]
  if kind=='l':return x>=math.ceil(nx/2)and y<math.ceil(ny/2)
  if kind=='u':return nx//3<=x<nx-nx//3 and y<max(1,ny//3)
  if kind=='cross':return(x<nx//3 or x>=nx-nx//3)and(y<ny//3 or y>=ny-ny//3)
  return False
 for xx in range(nx):
  for yy in range(ny):
   if not cut(xx,yy):continue
   x,y=xx,yy
   if nx==ny:
    for _ in range(turn):x,y=nx-1-y,x
   else:
    if turn in[1,2]:x=nx-1-x
    if turn in[2,3]:y=ny-1-y
   x+=offset_x;y+=offset_y
   occupied=False
   for o in project['objects']:
    w,d=(o['d'],o['w'])if o.get('rotation',0)%180 else(o['w'],o['d']);w=w/2+1;d=d/2+1
    if o['x']+w>x*8 and o['x']-w<(x+1)*8 and o['y']+d>y*8 and o['y']-d<(y+1)*8:occupied=True;break
   crossed=any(max(pts[max(0,i-1)][0],b[0])>x*8-1 and min(pts[max(0,i-1)][0],b[0])<(x+1)*8+1 and max(pts[max(0,i-1)][1],b[1])>y*8-1 and min(pts[max(0,i-1)][1],b[1])<(y+1)*8+1 for pts in paths for i,b in enumerate(pts))
   if not occupied and not crossed:cells.discard((x,y))
 return cells


def opening_groups(panels):
 seen=set();groups=[]
 for i in range(len(panels)):
  if i in seen:continue
  q=[i];g=[];seen.add(i)
  for k in q:
   a=panels[k];g.append(a)
   for j,b in enumerate(panels):
    if j in seen:continue
    horizontal=(abs(a['u']+8-b['u'])<.01 or abs(b['u']+8-a['u'])<.01)and min(a['z']+a['h'],b['z']+b['h'])>max(a['z'],b['z'])
    vertical=a['u']==b['u']and(abs(a['z']+a['h']-b['z'])<.01 or abs(b['z']+b['h']-a['z'])<.01)
    if a['side']==b['side']and a['line']==b['line']and(horizontal or vertical):seen.add(j);q.append(j)
  groups.append(dict(side=g[0]['side'],line=g[0]['line'],start=min(a['u']for a in g),end=max(a['u']+8 for a in g),bottom=min(a['z']for a in g),top=max(a['z']+a['h']for a in g)))
 return groups


def access_paths(p):
 import math
 from native_assembly import rotate
 paths=[];objects={o['id']:o for o in p['objects']}
 for link in p.get('links',[]):
  if link['kind']=='power':continue
  if link.get('physicalRoute'):
   paths.append([[q['x'],q['y'],q['z']]for q in link['physicalRoute']]);continue
  o=objects.get(link['from'])
  if link.get('native')and o and o.get('native'):
   native=o['native'];angle=math.radians(o['rotation']-native['rotation']);c=math.cos(angle);s=math.sin(angle)
   def point(v):
    r=rotate(native['quaternion'],v);return[o['x']+c*r[0]-s*r[1],o['y']+s*r[0]+c*r[1],o['z']+native['originZ']+r[2]]
   pts=[]
   for a,b,ta,tb in link['native'].get('spans',[]):
    for i in range(25):
     t=i/24;pts.append(point([(2*t**3-3*t*t+1)*a[j]+(t**3-2*t*t+t)*ta[j]+(-2*t**3+3*t*t)*b[j]+(t**3-t*t)*tb[j]for j in range(3)]))
   if link['native'].get('snap')and link['native']['fromPort']in native['ports']:pts.append(point(native['ports'][link['native']['fromPort']]))
   if pts:paths.append(pts)
  elif link['kind']in['belt','planned']:
   b=objects.get(link['to'])
   if o and b:paths.append([[o['x'],o['y'],o.get('z',0)],*[[q['x'],q['y'],q.get('z',0)]for q in link.get('waypoints',[])],[b['x'],b['y'],b.get('z',0)]])
 return paths

def entrance(p,edges,overlaps):
 mode=p.get('design',{}).get('entrance','auto')
 if mode=='none':return None
 floor=next((f for f in p.get('floors',[])if f['z']==0),None)
 if not floor or floor.get('holes'):return None
 base=floor.get('thickness',1);paths=access_paths(p)
 candidates=[dict(e,score=e['side']*1000+abs(e['start']+4-(p.get('depth',p['size'])if e['side']%2 else p['size'])/2))for e in edges if mode=='auto'or e['side']==['front','right','back','left'].index(mode)]
 for e in sorted(candidates,key=lambda e:e['score']):
  horizontal=e['side']%2==0;sign=1 if e['side']in[0,3]else-1;x=e['start']+4 if horizontal else e['line']+sign*2;y=e['line']+sign*2 if horizontal else e['start']+4;w,depth=(8,4)if horizontal else(4,8)
  if overlaps(x,y,base,w,depth,8-base,0):continue
  low=[x-w/2-.5,y-depth/2-.5,base-.2];high=[x+w/2+.5,y+depth/2+.5,8.2]
  blocked=False
  for pts in paths:
   for i,b in enumerate(pts):
    a=pts[max(0,i-1)]
    if all(max(a[j],b[j])>=low[j]and min(a[j],b[j])<=high[j]for j in range(3)):blocked=True;break
   if blocked:break
  if not blocked:return dict(e,base=base)
 return None
