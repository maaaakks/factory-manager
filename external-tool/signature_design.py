"""Authored signature compositions; mirrors dist/signature-design.js."""
import math

def recess(x,y,z,h,top,b,seed):
 x0,x1,y0,y1=b;n=x1-x0+1;m=y1-y0+1;k=(seed-1)%3
 if n<3 or m<3:return False
 upper=z>=max(4,top-8)
 if k==0:return upper and((y==y0 and x>=x0+math.ceil(n*.6))or(x==x1 and y==y1))
 if k==1:return y==y0 and x==x0+math.floor(n/3)or upper and x==x1 and y>=y0+math.ceil(m*.65)
 return upper and((x==x0 and y==y0)or(x==x1 and y==y1))

def window_at(start,side,z,top,size,seed):
 bay=math.floor(start/8);n=size/8;k=(seed-1)%3
 if z==0:return False
 if k==0:return(z==4 or z>=top-4)and(side%2==0 or bay%3!=0)
 if k==1:return z>=4 and(abs(bay-n*.65)<1 or z>=top-4)
 return z>=top-4 or bay%3==1

def decorate(parts,p,paths,style):
 width=p['size'];depth=p.get('depth',width);height=p.get('height',width);mode=(p['design']['seed']-1)%3
 def bounds(q):
  w,d=(q['d'],q['w'])if q['rotation']%180 else(q['w'],q['d'])
  return[[q['x']-w/2,q['x']+w/2],[q['y']-d/2,q['y']+d/2],[q['z'],q['z']+q['h']]]
 obstacles=[bounds(dict(q,z=q.get('z')or 0,h=q.get('h')or 6))for q in p['objects']]
 for points in paths:
  for i in range(1,len(points)):obstacles.append([[min(points[i-1][j],points[i][j])-.75,max(points[i-1][j],points[i][j])+.75]for j in range(3)])
 for q in parts:
  if q['name'].startswith('Entrée piétonne'):obstacles.append(bounds(q))
 def overlap(a,b):return all(min(r[1],b[i][1])-max(r[0],b[i][0])>.01 for i,r in enumerate(a))
 def free(b):return all(r[0]>=-.001 and r[1]<=[width,depth,height][i]+.001 for i,r in enumerate(b))and not any(overlap(b,o)for o in obstacles)
 result=[]
 for q in parts:
  color=(style['window']if'Window'in q['asset']else style['trim'])if q['component']=='roof'else(style['trim']if q['z']<4 else style['wall'])if q['component']=='wall'else style['trim']if q['component']=='beam'and not q.get('panelUnits')else q['color']
  if q['name']=='Angle · bardage ajusté':
   for dz in[-.32,0,.32]:
    start=[v+(dz if i==2 else 0)for i,v in enumerate(q['start'])];end=[v+(dz if i==2 else 0)for i,v in enumerate(q['end'])];lo=[min(v,end[i])-.15 for i,v in enumerate(start)];hi=[max(v,end[i])+.15 for i,v in enumerate(start)]
    result.append(dict(q,start=start,end=end,x=(start[0]+end[0])/2,y=(start[1]+end[1])/2,z=lo[2],w=hi[0]-lo[0],d=hi[1]-lo[1],h=hi[2]-lo[2],color=style['trim']if q['z']<4 else style['wall'],panelUnits=(q.get('panelUnits')or 0)/3))
  else:result.append(dict(q,color=color,**({'asset':'Wall_Window_Thin_8x4_02'}if q['component']=='window'else{})))
 def beam(name,a,b,color=None):
  length=math.dist(a,b)
  if length<.1:return
  count=math.ceil(length/16)
  for i in range(count):
   def at(t):return[v+(b[j]-v)*t for j,v in enumerate(a)]
   start=at(i/count);end=at((i+1)/count);lo=[min(v,end[j])-.15 for j,v in enumerate(start)];hi=[max(v,end[j])+.15 for j,v in enumerate(start)];box=[[v,hi[j]]for j,v in enumerate(lo)]
   if not free(box):continue
   result.append(dict(name='Signature · '+name,x=(start[0]+end[0])/2,y=(start[1]+end[1])/2,z=lo[2],w=hi[0]-lo[0],d=hi[1]-lo[1],h=hi[2]-lo[2],rotation=0,color=color or style['trim'],component='beam',asset='Beam_Painted',start=start,end=end))
 front=[q for q in parts if q['component']in['wall','window']and q['rotation']==0];line=min(q['y']for q in front)if front else 0;face=[q for q in front if abs(q['y']-line)<.01]
 if face:
  for lo in[.8,8.8,max(.8,width-24.8)]:
   hi=min(lo+22.4,width-.8);top=max(q['z']+q['h']for q in face)
   if hi-lo>=14 and top>=8:
    floor=next((f for f in p.get('floors',[])if f['z']==0),{});bottom=(floor.get('thickness')or 1)+.3;y=line-.65;z=top-.5;cut=min(4,(hi-lo)/5,top/3);points=[[lo,y,bottom],[lo,y,z-cut],[lo+cut,y,z],[hi-cut,y,z],[hi,y,z-cut],[hi,y,bottom]]
    fits=all(free([[min(v,b[j])-.15,max(v,b[j])+.15]for j,v in enumerate(points[i])])for i,b in enumerate(points[1:]))
    if fits:
     for i in range(1,len(points)):beam('Portique facetté',points[i-1],points[i],style['accent']if mode==2 else style['trim'])
     break
 def point(q,u,z,offset):
  side=q['rotation']//90;sign=[-1,1,1,-1][side]
  return[q['x']+sign*offset,q['y']+u,z]if side%2 else[q['x']+u,q['y']+sign*offset,z]
 for q in parts:
  if q['component']=='window'and q['h']==4 and not q['name'].startswith('Lanterneau'):
   beam('Appui de baie',point(q,-3.7,q['z']+.2,.35),point(q,3.7,q['z']+.2,.35))
   beam('Linteau de baie',point(q,-3.7,q['z']+3.8,.35),point(q,3.7,q['z']+3.8,.35))
   for u in[-3.7,3.7]:beam('Tableau de baie',point(q,u,q['z']+.2,.35),point(q,u,q['z']+3.8,.35))
   bay=math.floor((q['y']if q['rotation']%180 else q['x'])/8)
   if(q['rotation']/90+bay)%3==0:beam('Lame verticale',point(q,-2.5,q['z']+.25,.65),point(q,-2.5,q['z']+3.75,.65),style['accent'])
 serviced=set()
 for q in parts:
  if q['component']!='wall'or q['h']!=4 or q['z']<4 or q['rotation']in serviced:continue
  serviced.add(q['rotation'])
  for i in range(5):beam('Persienne technique',point(q,-2.7,q['z']+.8+i*.55,.6),point(q,2.7,q['z']+.8+i*.55,.6))
  if mode==2:beam('Contreventement ponctuel',point(q,-3.5,q['z']+.4,.7),point(q,3.5,q['z']+3.6,.7),style['accent'])
 if p['design']['roof']:
  roofs=[q for q in parts if q['component']=='roof'and not q['name'].startswith('Sous-face')]
  for q in roofs:
   for dx,dy in[[0,-1],[1,0],[0,1],[-1,0]]:
    if any(abs(r['x']-q['x']-dx*8)<.01 and abs(r['y']-q['y']-dy*8)<.01 and abs(r['z']-q['z'])<.1 for r in roofs):continue
    z=q['z']+.7
    if dx:beam('Rive de toiture',[q['x']+dx*3.7,q['y']-3.7,z],[q['x']+dx*3.7,q['y']+3.7,z])
    else:beam('Rive de toiture',[q['x']-3.7,q['y']+dy*3.7,z],[q['x']+3.7,q['y']+dy*3.7,z])
 for q in parts:
  if q['name']=='Entrée piétonne · linteau':beam('Repère entrée',[v+(.4 if i==2 else 0)for i,v in enumerate(q['start'])],[v+(.4 if i==2 else 0)for i,v in enumerate(q['end'])],style['accent'])
 return result
