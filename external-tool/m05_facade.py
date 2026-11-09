"""Native-size front compositions; deterministic mirror of m05-facade.js."""
import json,math
from pathlib import Path
DATA=json.loads((Path(__file__).parent/'data/m05-facade-library.json').read_text(encoding='utf8'))
def turn(v,n):
 x,y,z=v
 return [x,y,z]if n==0 else[-y,x,z]if n==1 else[-x,-y,z]if n==2 else[y,-x,z]
def box(points):return [[min(p[i]for p in points),max(p[i]for p in points)]for i in range(3)]
def overlap(a,b):return all(min(r[1],b[i][1])-max(r[0],b[i][0])>.01 for i,r in enumerate(a))
def bounds(q):
 if 'signatureBounds'in q:return q['signatureBounds']
 if 'start'in q:return [[r[0]-.3,r[1]+.3]for r in box([q['start'],q['end']])]
 w,d=q.get('w',0),q.get('d',0)
 if q['rotation']%180:w,d=d,w
 return[[q['x']-w/2,q['x']+w/2],[q['y']-d/2,q['y']+d/2],[q['z'],q['z']+q.get('h',0)]]
def apply_one(parts,p,paths,slot=0,wrap=False):
 seed=p['design'].get('seed',1)+slot;side=dict(front=0,right=1,back=2,left=3).get(p['design'].get('entrance'),0);n=[2,3,0,1][side];normal=turn([0,1,0],n);width=p['size'];depth=p.get('depth',width);height=p.get('height',width)
 panels=[q for q in parts if q['component']in['wall','window']and q['h']==4 and q['rotation']==side*90 and not q['name'].startswith('Lanterneau')]
 if not panels:return parts
 distance=lambda q:q['x']*normal[0]+q['y']*normal[1]
 line=max(map(distance,panels));face=[q for q in panels if abs(distance(q)-line)<.05];us=sorted({q['y']if side%2 else q['x']for q in face});mid=(us[0]+us[-1])/2;obstacles=[]
 for o in p['objects']:
  w,d=o['w'],o['d']
  if o['rotation']%180:w,d=d,w
  obstacles.append([[o['x']-w/2-.15,o['x']+w/2+.15],[o['y']-d/2-.15,o['y']+d/2+.15],[o.get('z',0),o.get('z',0)+(o.get('h')or 6)+.15]])
 for pts in paths:
  for i in range(1,len(pts)):obstacles.append([[r[0]-.75,r[1]+.75]for r in box([pts[i-1],pts[i]])])
 obstacles.extend(bounds(q)for q in parts if q['name'].startswith('Entrée piétonne'))
 obstacles.extend(q.get('signatureRegion',q.get('signatureBounds'))for q in parts if 'signatureRegion'in q or 'signatureBounds'in q)
 def free(b):return all(r[0]>=(-1e-7 if i==2 else .009)and r[1]<=[width,depth,height][i]-.009 for i,r in enumerate(b))and not any(overlap(b,o)for o in obstacles)
 wall_top=max(q['z']+q['h']for q in panels);levels=sorted({z for f in p.get('floors',[])for z in[round(f['z']+(f.get('thickness')or 1),9)]})or[0];order=[(seed-1)%3]+[i for i in[0,1,2]if i!=(seed-1)%3]
 modes=['inset','projection']if wrap else['projection','inset']
 for mode in modes:
  if mode=='crown'and(not p['design']['roof']or slot):continue
  for index in order:
   for motif in[DATA['motifs'][index],DATA['motifs'][index+3]]:
    lo,hi=motif['bounds'][0];span=hi-lo;target=mid+(-24 if slot==1 else 24 if slot==2 else 0);centers=[(u+us[i+1])/2 for i,u in enumerate(us[:-1])]if span>12 else list(us);centers=[u for u in centers if not slot or abs(u-target)<=8];centers.sort(key=lambda u:(abs(u-target),u))
    bases=[z for z in levels if z+motif['bounds'][2][1]<=wall_top+.75]
    for u in centers:
     for base in bases:
      offset=.35 if mode=='projection'else-8.45;anchor=[normal[0]*(line+offset),u,base]if side%2 else[u,normal[1]*(line+offset),base]
      def point(a):return [round(v+anchor[i],9)for i,v in enumerate(turn(a,n))]
      def transform(b):return box([point([b[0][i],b[1][j],b[2][k]])for i in[0,1]for j in[0,1]for k in[0,1]])
      region=transform(motif['bounds'])
      if not free(region):continue
      passage=transform([[-7,7],[-.5,8.2],[.05,7.1]])if motif['id']=='portique'else None
      result=[];added=[];units=0
      for q in parts:
       b=bounds(q);inside=all(r[0]>=region[i][0]-1.5 and r[1]<=region[i][1]+1.5 for i,r in enumerate(b));replace=(inside and not q['name'].startswith('Entrée')and(mode=='crown'or q['component']!='roof'))or(passage is not None and overlap(b,passage))
       if replace:units+=q.get('coverageUnits')or q.get('panelUnits')or(1 if q['component']in['wall','window']else 0)
       else:result.append(q)
      angle=n*math.pi/2;s=round(math.sin(angle/2),9);c=round(math.cos(angle/2),9)
      for source in motif['pieces']:
       if not p['design']['roof']and source.get('asset','').startswith('Roof_')or mode=='crown'and source.get('platform'):continue
       b=transform(source['bounds']);name='Signature M05 · '+motif['label']
       if source.get('beam'):
        start=point(source['start']);end=point(source['end']);added.append(dict(name=name,component='beam',asset='Beam_H',start=start,end=end,x=(start[0]+end[0])/2,y=(start[1]+end[1])/2,z=b[2][0],w=b[0][1]-b[0][0],d=b[1][1]-b[1][0],h=b[2][1]-b[2][0],rotation=0,color=source['color'],signatureBounds=b))
       else:
        x,y,z,w=source['quat'];quat=[round(v,9)for v in[c*x-s*y,c*y+s*x,c*z+s*w,c*w-s*z]];pos=point(source['pos']);added.append(dict(name=name,component='module',asset=source['asset'],sourceModule=source['sourceModule'],sourceIndex=source['sourceIndex'],origin=[0,0,0],turn=0,quat=quat,x=pos[0],y=pos[1],z=pos[2],w=0,d=0,h=0,rotation=n*90,color=source['color'],signatureBounds=b,**({'platform':True}if source.get('platform')else{})))
      if not added:continue
      if units:next((q for q in added if q['z']<wall_top),added[0])['coverageUnits']=units
      added[0]['facadeSignature']=dict(id=motif['id'],label=motif['label'],placement=mode,side=side,supportZ=base,wallTop=wall_top);added[0]['signatureRegion']=region
      return result+added
 if slot:return parts
 accents=[];chosen=sorted([q for q in face if q['z']>=4],key=lambda q:(abs((q['y']if side%2 else q['x'])-mid),-q['z']))[:2]
 for q in chosen:
  u=q['y']if side%2 else q['x']
  def at(t,z):return[normal[0]*(line+.5),u+t,z]if side%2 else[u+t,normal[1]*(line+.5),z]
  for sign in[-1,1]:
   start=at(sign*2.8,q['z']+.7);end=at(0,q['z']+3.2);b=[[r[0]-.22,r[1]+.22]for r in box([start,end])]
   if not free(b):continue
   accents.append(dict(name='Signature M05 · Charpente compacte',component='beam',asset='Beam_Painted',start=start,end=end,x=(start[0]+end[0])/2,y=(start[1]+end[1])/2,z=b[2][0],w=b[0][1]-b[0][0],d=b[1][1]-b[1][0],h=b[2][1]-b[2][0],rotation=0,color='#354145',signatureBounds=b))
 if accents:
  accents[0]['facadeSignature']=dict(id='charpente',label='Charpente compacte',placement='relief',side=side)
  return[q for q in parts if q['asset']!='LargeFan'or not any(abs(a['x']-q['x'])<1 and abs(a['y']-q['y'])<1 and abs(a['z']+2-q['z'])<.1 for a in chosen)]+accents
 return parts
def apply(parts,p,paths):
 result=apply_one(parts,p,paths);faces=['front','right','back','left'];first=faces.index(p['design'].get('entrance'))if p['design'].get('entrance')in faces else 0;span=p.get('depth',p['size'])if first%2 else p['size']
 if span>=64 and any('signatureRegion'in q for q in result):result=apply_one(result,p,paths,1);result=apply_one(result,p,paths,2)
 for offset in range(1,4):
  side=(first+offset)%4;view=dict(p,design=dict(p['design'],entrance=faces[side],seed=((p['design'].get('seed',1)+offset-1)%999)+1));result=apply_one(result,view,paths,0,True)
 return result
