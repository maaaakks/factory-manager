"""Native-sized 4 m wall courses: adapt the shell without scaling any actor."""
import copy,math,re
def transform(source,p):
 d=p.get('design',{});family=d.get('family')
 if d.get('studyHeightMode')!='auto'or family not in['atlas','sylva']:return source
 top=max([9,d.get('studyHeightTop',0)]+[o.get('z',0)+(o.get('h')or 6)for o in p['objects']if o['type']not in['port','pole','wallPole','lift']]);base=25 if family=='atlas'else 17;target=max(17,1+math.ceil((top+2.5-1)/4)*4);delta=target-base;pivot=13 if family=='atlas'else 9;out=[]
 def zmap(z):return z if z<=pivot else max(pivot,z+delta)if delta<0 else z+delta
 def push(q):
  if 'start'not in q:out.append(q);return
  a,b=q['start'],q['end'];length=math.dist(a,b)
  if length<.01:return
  n=math.ceil(length/16)
  for i in range(n):
   r=copy.deepcopy(q);r['start']=[v+(b[j]-v)*i/n for j,v in enumerate(a)];r['end']=[v+(b[j]-v)*(i+1)/n for j,v in enumerate(a)];rad=.3 if r['asset']=='Beam_H'else .15
   r.update(x=(r['start'][0]+r['end'][0])/2,y=(r['start'][1]+r['end'][1])/2,z=min(r['start'][2],r['end'][2])-rad,w=abs(r['start'][0]-r['end'][0])+rad*2,d=abs(r['start'][1]-r['end'][1])+rad*2,h=abs(r['start'][2]-r['end'][2])+rad*2);out.append(r)
 for original in source:
  q=copy.deepcopy(original);fixed=q.get('zone')in['circulation','galerie','accueil','parvis']or family=='sylva'and q.get('zone')=='terrasses'or re.search('escalier|palier|garde-corps|trémie|porte vers',q['name'])
  if not fixed:
   if delta<0:
    if q['component']in['wall','window']and pivot<=q['z']<pivot-delta:continue
    if 'start'in q and pivot<=q['start'][2]<pivot-delta and pivot<=q['end'][2]<pivot-delta:continue
   if delta>0 and q['component']in['wall','window']and q['z']==pivot:
    for dz in range(0,delta,4):r=copy.deepcopy(q);r['z']=pivot+dz;push(r)
   if 'start'in q:q['start'][2]=zmap(q['start'][2]);q['end'][2]=zmap(q['end'][2])
   else:
    old=q['z'];q['z']=zmap(q['z'])
    if q.get('signatureBounds'):q['signatureBounds'][2]=[z+q['z']-old for z in q['signatureBounds'][2]]
  if family=='atlas'and q['name']=='Halle · flanc'and q['x']==24.5 and q['y']==20 and q['z']==13:continue
  if family=='sylva'and 'pavillon supérieur'in q['name']and q['z']==target+4:continue
  if family=='sylva'and re.search('toiture du pavillon|couronnement',q['name']):
   if 'start'in q:q['start'][2]-=4;q['end'][2]-=4
   else:q['z']-=4
  push(q)
 return out

def floor_color(p,f,x,y,fallback):
 if __import__('native_design').CATALOG['studies'].get(p.get('design',{}).get('family'),{}).get('designFirst')and not p.get('design',{}).get('living'):
  from design_campus import floor_color as campus_color
  return campus_color(p,f,x,y,fallback)
 v=p.get('design',{}).get('living')
 if not v:return fallback
 level=next((l for l in v['levels']if abs(l['z']-f['z']-f['thickness'])<.05),None)
 if not level:return fallback
 def within(q):return x-4<=q[0]<x+4 and y-4<=q[1]<y+4
 return v['palette']['pad']if any(within(s['point'])for s in level['stations'])else v['palette']['lane']if any(map(within,level['paths']))else v['palette']['floor']

def validate(d):
 from native_project import ExportError
 def bad():raise ExportError(['Aménagement intérieur invalide.'])
 if 'studyHeightMode'in d and d['studyHeightMode']not in['auto','reference']:bad()
 if 'living'not in d:return
 v=d['living']
 def vector(q):return isinstance(q,list)and len(q)==3 and all(type(n)in[int,float]and math.isfinite(n)and 0<=n<=512 for n in q)
 if not isinstance(v,dict)or v.get('version')!=1 or not isinstance(v.get('palette'),dict)or any(not isinstance(v['palette'].get(k),str)or not re.fullmatch('#[a-fA-F0-9]{6}',v['palette'][k])for k in['floor','lane','pad','frame','light']):bad()
 if not isinstance(v.get('levels'),list)or len(v['levels'])>64 or not isinstance(v.get('fixtures'),list)or len(v['fixtures'])>128:bad()
 for l in v['levels']:
  if not isinstance(l,dict)or type(l.get('z'))not in[int,float]or not math.isfinite(l['z'])or not isinstance(l.get('paths'),list)or len(l['paths'])>4000 or any(not vector(q)for q in l['paths'])or not isinstance(l.get('stations'),list)or any(not isinstance(s,dict)or not isinstance(s.get('name'),str)or not vector(s.get('point'))for s in l['stations'])or not isinstance(l.get('missing'),list):bad()
 for q in v['fixtures']:
  if not isinstance(q,dict)or q.get('component')!='module'or q.get('asset')not in['FloodlightWall','PowerPoleWall']or not vector([q.get('x'),q.get('y'),q.get('z')])or any(not isinstance(q.get(k),str)for k in['sourceModule','name','livingCircuit'])or type(q.get('sourceIndex'))is not int or not isinstance(q.get('quat'),list)or len(q['quat'])!=4 or any(type(n)not in[int,float]or not math.isfinite(n)for n in q['quat'])or abs(sum(n*n for n in q['quat'])-1)>1e-5 or not isinstance(q.get('color'),str)or not re.fullmatch('#[a-fA-F0-9]{6}',q['color']):bad()

 if 'accessParts'in v:
  if not isinstance(v['accessParts'],list)or len(v['accessParts'])>1200 or any(not isinstance(q,dict)or q.get('asset')not in['CatwalkStairs','CatwalkRamp','CatwalkCross','CatwalkStraight','Wall_Door_8x4_03','Beam_Painted','Wall_Window_Thin_8x4_02','Railing_01','Wall_Window_Thin_8x4_01','Foundation_ConcretePolished_8x1','Stair_PolishedConcrete_8x2','Wall_Door_8x4_01','Roof_Tar_01']or q.get('component')not in['module','beam','window','wall']or any(type(q.get(k))not in[int,float]or not math.isfinite(q[k])for k in['x','y','z'])for q in v['accessParts']):bad()
 if 'openings'in v and(not isinstance(v['openings'],list)or len(v['openings'])>64 or any(not isinstance(b,list)or len(b)!=3 or any(not isinstance(a,list)or len(a)!=2 or any(type(n)not in[int,float]or not math.isfinite(n)for n in a)for a in b)for b in v['openings'])):bad()

def assert_fresh(p):
 v=p.get('design',{}).get('living',{});old=v.get('snapshot')
 if v and v.get('revision')!=2:
  from native_project import ExportError
  raise ExportError(['Ancien intérieur : réappliquez la création pour actualiser son aménagement.'])
 if p.get('design',{}).get('family')=='compact'and v and v.get('compactRevision')!=4:
  from native_project import ExportError
  raise ExportError(['Réappliquez Compact pour remplacer l’ancien intérieur.'])
 if old is None:return
 current=dict(size=p['size'],depth=p.get('depth',p['size']),floors=[[f['z'],f['thickness']]for f in p.get('floors',[])],machines=sorted([[o['id'],o['x'],o['y'],o.get('z',0),o['rotation']]for o in p['objects']if o.get('recipe')]))
 if old!=current:
  from native_project import ExportError
  raise ExportError(['Implantation modifiée : réappliquez la création pour actualiser son aménagement avant l’export.'])

def terraces(source_parts,p):
 if p.get('design',{}).get('family')!='sylva':return source_parts
 from m05_architecture import DATA
 y=p.get('depth',p['size'])-12;color='#526c5b'
 def module(asset,name,x,yy,z,rotation,bounds):
  for key,m in DATA['modules'].items():
   index=next((i for i,q in enumerate(m['parts'])if q['asset']==asset),None)
   if index is not None:break
  a=math.radians(rotation)/2
  return dict(name=name,asset=asset,component='module',sourceModule=key,sourceIndex=index,origin=[0,0,0],turn=0,quat=[0,0,math.sin(a),math.cos(a)],x=x,y=yy,z=z,w=0,d=0,h=0,rotation=rotation,color=color,zone='interieur',studyLayer='interior',signatureBounds=bounds,fixedLayout=True)
 result=[q for q in source_parts if not(q['name']=='Sylva · gradin paysager'and q['x']==20 and q['y']==y and q['z']==13)and not(q['name']=='Sylva · terrasse haute'and q['x']==28 and q['y']==y and q['z']==17)and not(q['component']in['wall','window']and q['y']==y and(q['x']==16 and q['z']==9 or q['x']==24 and q['z']==13))]
 for x,z in[(16,9),(24,13)]:
  q=module('CatwalkStairs','Sylva · escalier entre terrasses',x,y,z,0,[[x-2,x+2],[y-2,y+2],[z-.18,z+5.1]]);q.update(walkStart=[x-2,y,z],walkEnd=[x+2,y,z+4]);result.append(q)
 for x,yy,z,asset,rotation in[(20,y,13,'CatwalkCross',0),(20,y-4,13,'CatwalkStraight',90),(28,y,17,'CatwalkCross',0),(32,y,17,'CatwalkStraight',0)]:result.append(module(asset,'Sylva · palier panoramique',x,yy,z,rotation,[[x-2,x+2],[yy-2,yy+2],[z-.18,z]]))
 for x,z in[(20,13),(28,17)]:
  for yy in[y-2,y+2]:result.append(module('Railing_01','Sylva · protection de palier',x,yy,z,90,[[x-2,x+2],[yy-.1,yy+.1],[z,z+1]]))
 return result


def clean_parts(parts,p):
 if not p.get('design',{}).get('living'):return parts
 top=min(f['z']+f['thickness']for f in p['floors'])
 def bounds(q):return q.get('signatureBounds')or[[0,0],[0,0],[q['z'],q['z']+q['h']]]
 return[q for q in parts if not q.get('livingFloorMark')and q['asset']!='FloodlightWall'and not(q.get('studyLayer')=='deck'and bounds(q)[2][0]>=0 and bounds(q)[2][1]<=top+.8)]
