"""Lengthen authored studies through repeatable 8 m rear bays, without scaling assets."""
import copy,math,re
def repeat_bays(source,width_extra,depth_extra,bays):
 result=copy.deepcopy(source)
 for axis,extra,key in [('x',width_extra,'width'),('y',depth_extra,'length')]:
  pivot=bays[key]['pivot'];start=bays[key]['from'];out=[]
  for source in result:
   q=copy.deepcopy(source)
   if q[axis]>=pivot:q[axis]+=extra
   out.append(q)
   if start<=source[axis]<pivot:
    for delta in range(8,extra+1,8):
     q=copy.deepcopy(source);q[axis]+=delta;out.append(q)
  result=out
 return result

def expand(source,extra):
 if not extra:return copy.deepcopy(source)
 result=[]
 def move(q,dy):
  q['y']+=dy
  if 'start'in q:q['start'][1]+=dy;q['end'][1]+=dy
  if 'signatureBounds'in q:q['signatureBounds'][1]=[y+dy for y in q['signatureBounds'][1]]
  return q
 def push(q):
  if 'start'not in q:result.append(q);return
  a,b=q['start'],q['end'];n=math.ceil(math.dist(a,b)/16)
  for i in range(n):
   r=copy.deepcopy(q);r['start']=[v+(b[j]-v)*i/n for j,v in enumerate(a)];r['end']=[v+(b[j]-v)*(i+1)/n for j,v in enumerate(a)];rad=.3 if r['asset']=='Beam_H'else .15
   r.update(x=(r['start'][0]+r['end'][0])/2,y=(r['start'][1]+r['end'][1])/2,z=min(r['start'][2],r['end'][2])-rad,w=abs(r['start'][0]-r['end'][0])+rad*2,d=abs(r['start'][1]-r['end'][1])+rad*2,h=abs(r['start'][2]-r['end'][2])+rad*2);result.append(r)
 for original in source:
  q=copy.deepcopy(original)
  if (re.search('escalier|palier|protection de la trémie|Lumen · pavillon|Lumen · retour de coque|Lumen · rive flottante|Lumen · porche|Lumen · seuil|Lumen · appui',q['name'])or(q['name']=='Lumen · annexe lisse'and q['rotation']==0)or q.get('fixedLayout')):push(q);continue
  if 'start'in q and min(q['start'][1],q['end'][1])<32<max(q['start'][1],q['end'][1]):
   for p in[q['start'],q['end']]:
    if p[1]>=32:p[1]+=extra
   push(q);continue
  if q['y']>=32:push(move(q,extra))
  else:
   push(q)
   if q['y']>=24:
    for d in range(8,extra+1,8):push(move(copy.deepcopy(original),d))
 terrace=next((q for q in source if q['name']=='Galerie · terrasse accessible'and q['x']==12 and q['y']==36),None)
 if terrace:
  for d in range(0,extra,8):push(move(copy.deepcopy(terrace),d))
 return result

def widen(source,extra):
 if not extra:return source
 result=[]
 def move(q,dx):
  q['x']+=dx
  if 'start'in q:q['start'][0]+=dx;q['end'][0]+=dx
  if 'signatureBounds'in q:q['signatureBounds'][0]=[x+dx for x in q['signatureBounds'][0]]
  return q
 def push(q):
  if 'start'not in q:result.append(q);return
  a,b=q['start'],q['end'];n=math.ceil(math.dist(a,b)/16)
  for i in range(n):
   r=copy.deepcopy(q);r['start']=[v+(b[j]-v)*i/n for j,v in enumerate(a)];r['end']=[v+(b[j]-v)*(i+1)/n for j,v in enumerate(a)];rad=.3 if r['asset']=='Beam_H'else .15
   r.update(x=(r['start'][0]+r['end'][0])/2,y=(r['start'][1]+r['end'][1])/2,z=min(r['start'][2],r['end'][2])-rad,w=abs(r['start'][0]-r['end'][0])+rad*2,d=abs(r['start'][1]-r['end'][1])+rad*2,h=abs(r['start'][2]-r['end'][2])+rad*2);result.append(r)
 for original in source:
  q=copy.deepcopy(original)
  if q.get('fixedLayout'):push(q);continue
  if 'start'in q and min(q['start'][0],q['end'][0])<40 and(max(q['start'][0],q['end'][0])>40 or(q.get('stretchWidthEnd')and abs(max(q['start'][0],q['end'][0])-40)<1e-6)):
   for p in[q['start'],q['end']]:
    if p[0]>=40-1e-6:p[0]+=extra
   push(q);continue
  if q['x']>=40:push(move(q,extra))
  else:
   push(q)
   parallel=abs(q['start'][0]-q['end'][0])<1e-6 if 'start'in q else q['component']in['wall','window','trim']and q['rotation']%180!=0
   if q['x']>=32 and not parallel and q.get('repeatWidth')is not False:
    for dx in range(8,extra+1,8):push(move(copy.deepcopy(original),dx))
 return result
