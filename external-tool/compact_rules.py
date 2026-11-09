"""Native-sized Compact landing, circulation and electrical invariants."""
import math

def beam_bounds(q):
 a,b=q['start'],q['end'];l=math.dist(a,b);dx,dy,dz=[(b[i]-a[i])/l for i in range(3)];v=[0,-dz,dy,1+dx]if dx>-.999999 else[0,0,1,0];norm=math.sqrt(sum(n*n for n in v));x,y,z,w=[n/norm for n in v];r=q['beamRadius']
 u=[(2*x*y-2*z*w)*r,(1-2*x*x-2*z*z)*r,(2*y*z+2*x*w)*r];v=[(2*x*z+2*y*w)*r,(2*y*z-2*x*w)*r,(1-2*x*x-2*y*y)*r]
 return [[min(a[i],b[i])-abs(u[i])-abs(v[i]),max(a[i],b[i])+abs(u[i])+abs(v[i])]for i in range(3)]

def validate(p,parts):
 if p.get('design',{}).get('family')!='compact' or not p['design'].get('living'):return
 from native_project import ExportError
 v=p['design']['living'];items=[q for q in v['accessParts']if q.get('compactAssembly')=='inspection-gallery'];n=(p.get('depth',p['size'])-32)//8
 def fail():raise ExportError(['Intérieur Compact incohérent : réappliquez la création.'])
 if v.get('compactRevision')!=4:fail()
 for asset,count in [('Foundation_ConcretePolished_8x1',2*n+4),('Wall_Window_Thin_8x4_01',n),('Roof_Tar_01',n+1),('Stair_PolishedConcrete_8x2',2),('Wall_Door_8x4_01',1)]:
  if sum(q['asset']==asset for q in items)!=count:fail()
 if any(q.get('compactAssembly')not in ['inspection-gallery','ceiling-electric','machine-zones']for q in v['accessParts']):fail()
 def near(a,b):return abs(a-b)<1e-5
 def has(asset,x,y,z):return any(q['asset']==asset and near(q['x'],x)and near(q['y'],y)and near(q['z'],z)for q in items)
 for y in range(20,p.get('depth',p['size'])-8,8):
  if not all(has(asset,x,y,z)for asset,x,z in [('Foundation_ConcretePolished_8x1',12,1.5),('Foundation_ConcretePolished_8x1',12,2.5),('Roof_Tar_01',12,7.5)]):fail()
  if y>20 and not has('Wall_Window_Thin_8x4_01',16.15,y,3.3):fail()
 if not has('Stair_PolishedConcrete_8x2',20,20,2)or not has('Wall_Door_8x4_01',16.15,20,3):fail()
 exterior=[q for q in parts if q['component']=='wall'and 'Door'in q['asset']and q.get('zone')!='interieur']
 if len(exterior)!=1 or exterior[0]['asset']!='Wall_Door_8x4_01'or not all(near(exterior[0][k],v)for k,v in [('x',12),('y',12),('z',3.05)]):fail()
 if any(o['type']=='storage'for o in p['objects']):fail()
 def bounds(q):return beam_bounds(q)if q.get('beamRadius')else q.get('signatureBounds')or[[q['x']-q['w']/2,q['x']+q['w']/2],[q['y']-q['d']/2,q['y']+q['d']/2],[q['z'],q['z']+q['h']]]
 def overlap(a,b,t=.04):return all(min(r[1],b[i][1])-max(r[0],b[i][0])>t for i,r in enumerate(a))
 cornice=[q for q in parts if 'Corniche unique'in q['name']]
 for i,q in enumerate(cornice):
  if any(overlap(bounds(q),bounds(r),1e-6)for r in cornice[i+1:]):fail()
 for passage in [[[11.3,12.7],[11.3,12.7],[3.15,5.85]],[[15.4,16.9],[19.3,20.7],[3.1,5.8]]]:
  if any(q['component']=='beam'and overlap(bounds(q),passage)for q in parts):fail()
 for stair in [q for q in items if q['asset']=='Stair_PolishedConcrete_8x2']:
  a,b=stair.get('walkStart'),stair.get('walkEnd')
  from native_assembly import rotate
  if not a or not b or sum(v*(b[i]-a[i])/8 for i,v in enumerate(rotate(stair['quat'],[-1,0,0])))<.999 or not near(b[2]-a[2],2)or not near(math.dist(a[:2],b[:2]),8):fail()
 if p.get('nativeProfile'):
  sockets=[o for o in p['objects']if o.get('native',{}).get('ceilingMounted')];ids={o['id']for o in sockets}
  if not sockets or any(not near(o['z'],16.5)for o in sockets):fail()
  for m in [o for o in p['objects']if o.get('recipe')]:
   links=[l for l in p['links']if l['kind']=='power'and m['id']in[l['from'],l['to']]]
   if len(links)!=1 or (links[0]['to']if links[0]['from']==m['id']else links[0]['from'])not in ids:fail()
