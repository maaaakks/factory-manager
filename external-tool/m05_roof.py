"""Complete supported roof compositions, exact mirror of m05-roof.js."""
import json,math
from pathlib import Path
from m05_architecture import DATA
from m05_facade import overlap,box
FORMS=json.loads((Path(__file__).parent/'data/m05-roof-forms.json').read_text(encoding='utf8'))['forms']
def apply(parts,p,paths):
 if not p['design']['roof']:return parts
 width=p['size'];depth=p.get('depth',width);height=p.get('height',width);seed=p['design'].get('roofSeed',1);obstacles=[]
 for o in p['objects']:
  w,d=o['w'],o['d']
  if o['rotation']%180:w,d=d,w
  obstacles.append([[o['x']-w/2-.15,o['x']+w/2+.15],[o['y']-d/2-.15,o['y']+d/2+.15],[o.get('z',0),o.get('z',0)+(o.get('h')or 6)+.15]])
 for pts in paths:
  for i in range(1,len(pts)):obstacles.append([[r[0]-.75,r[1]+.75]for r in box([pts[i-1],pts[i]])])
 obstacles.extend(q.get('signatureRegion',q.get('signatureBounds'))for q in parts if 'signatureRegion'in q or 'signatureBounds'in q)
 def free(b):return all(r[0]>=.009 and r[1]<=[width,depth,height][i]-.009 for i,r in enumerate(b))and not any(overlap(b,o)for o in obstacles)
 roofs=[q for q in parts if q['component']=='roof'and q['name']in['Toiture','Verrière à ossature']and q['w']==8 and q['d']==8 and q['asset'].endswith('_01')];ordered=sorted(roofs,key=lambda q:((q['x']-width/2)**2+(q['y']-depth/2)**2,q['x'],q['y']));form=FORMS[(seed-1)%len(FORMS)];candidates=[]
 for n in([(seed-1)//len(FORMS)%2,1-(seed-1)//len(FORMS)%2]):
  for q in ordered:
   partner=q if form['width']==8 else next((r for r in roofs if abs(r['x']-q['x']-(0 if n else 8))<.01 and abs(r['y']-q['y']-(8 if n else 0))<.01 and abs(r['z']+r['h']-q['z']-q['h'])<.01),None)
   if partner is None:continue
   support=q['z']+q['h'];anchor=[(q['x']+partner['x'])/2,(q['y']+partner['y'])/2,support]
   def point(a):
    x,y,z=a;v=[x,y,z]if n==0 else[-y,x,z];return[round(v[i]+anchor[i],9)for i in range(3)]
   def transform(b):return box([point([b[0][i],b[1][j],b[2][k]])for i in[0,1]for j in[0,1]for k in[0,1]])
   region=transform(form['bounds'])
   if not free(region):continue
   candidates.append(dict(n=n,q=q,partner=partner,support=support,anchor=anchor,region=region))
 groups=[]
 for a in candidates:
  axis=0 if a['n']else 1;other=1-axis
  row=sorted([b for b in candidates if b['n']==a['n']and abs(b['support']-a['support'])<.01 and abs(b['anchor'][other]-a['anchor'][other])<.01 and b['anchor'][axis]>=a['anchor'][axis]-.01 and b['anchor'][axis]<=a['anchor'][axis]+8*(min(3 if form['id']=='monitor'else 6,max(2,math.floor(([width,depth][axis]-16)/8)))-1)+.01],key=lambda b:b['anchor'][axis]);run=[]
  for b in row:
   if run and abs(b['anchor'][axis]-run[-1]['anchor'][axis]-8)>.01:break
   run.append(b)
  groups.append(run)
 groups.sort(key=lambda a:(-len(a),(sum(q['anchor'][0]for q in a)/len(a)-width/2)**2+(sum(q['anchor'][1]for q in a)/len(a)-depth/2)**2))
 if groups:
  chosen=[groups[0]];first=groups[0][0];axis=0 if first['n']else 1;other=1-axis
  for group in groups:
   if len(chosen)>=(2 if form['id']=='monitor'else 3):break
   if len(group)!=len(groups[0])or group[0]['n']!=first['n']or abs(group[0]['anchor'][axis]-first['anchor'][axis])>.01:continue
   if all(abs(g[0]['anchor'][other]-group[0]['anchor'][other])>=form['width']+7.99 for g in chosen):chosen.append(group)
  selected=[c for g in chosen for c in g];tiles=set();details=[];seen=set()
  for candidate in selected:
   n=candidate['n'];q=candidate['q'];partner=candidate['partner'];support=candidate['support'];anchor=candidate['anchor'];region=candidate['region'];tiles.update([id(q),id(partner)])
   def point(a):
    x,y,z=a;v=[x,y,z]if n==0 else[-y,x,z];return[round(v[i]+anchor[i],9)for i in range(3)]
   def transform(b):return box([point([b[0][i],b[1][j],b[2][k]])for i in[0,1]for j in[0,1]for k in[0,1]])
   added=[];s=round(math.sin(n*math.pi/4),9);c=round(math.cos(n*math.pi/4),9)
   for source in form['pieces']:
    b=transform(source['bounds']);name='M05 · '+form['label']
    if source.get('beam'):
     start=point(source['start']);end=point(source['end']);added.append(dict(name=name,component='beam',asset='Beam_Painted',start=start,end=end,x=(start[0]+end[0])/2,y=(start[1]+end[1])/2,z=b[2][0],w=b[0][1]-b[0][0],d=b[1][1]-b[1][0],h=b[2][1]-b[2][0],rotation=0,color=source['color'],signatureBounds=b,roofDetail=form['id']))
    else:
     x,y,z,w=source['quat'];pos=point(source['pos']);quat=[round(v,9)for v in[c*x-s*y,c*y+s*x,c*z+s*w,c*w-s*z]];added.append(dict(name=name,component='module',asset=source['asset'],sourceModule=source['sourceModule'],sourceIndex=source['sourceIndex'],origin=[0,0,0],turn=0,quat=quat,x=pos[0],y=pos[1],z=pos[2],w=0,d=0,h=0,rotation=n*90,color=source['color'],signatureBounds=b,roofDetail=form['id']))
   added[0]['roofComposition']=dict(id=form['id'],label=form['label'],supportZ=support,bounds=region)
   for part in added:
    key=json.dumps([part['asset'],part.get('start'),part.get('end'),part['x'],part['y'],part['z'],part.get('quat')])
    if key not in seen:seen.add(key);details.append(part)
  return[dict(r,asset='Roof_Window_01',color='#91b9c0')if id(r)in tiles else r for r in parts]+details
 index=next(i for i,q in enumerate(DATA['modules']['M3']['parts'])if q['asset']=='LargeVent');source=DATA['modules']['M3']['parts'][index]
 for q in[q for q in ordered if q['asset']=='Roof_Tar_01']:
  z=q['z']+q['h']+.02;b=[[q['x']-1.3,q['x']+1.3],[q['y']-1.3,q['y']+1.3],[z,z+.35]]
  if free(b):return list(parts)+[dict(name='M05 · Ventilation discrète',component='module',asset='LargeVent',sourceModule='M3',sourceIndex=index,origin=[0,0,0],turn=0,quat=source['quat'],x=q['x'],y=q['y'],z=z,w=0,d=0,h=0,rotation=0,color='#354145',signatureBounds=b,roofDetail='vent')]
 return parts
