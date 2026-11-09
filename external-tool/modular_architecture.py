"""Facade relief and owned corner junctions. Mirrors WorkshopDesign exactly."""
import math
from blueprint_dimensions import dimensions
from architecture_patterns import footprint,access_paths,roof_composition

def join_corners(parts,edges,inset,bottom,top,style,overlaps):
 vertices={};corners=[]
 for e in edges:
  for end in [0,1]:
   raw=e['line']+(-inset if e['side']in[0,3]else inset);u=e['start']+end*8;x,y=(raw,u)if e['side']%2 else(u,raw)
   vertices.setdefault((round(x,4),round(y,4)),[]).append((e,end))
 for v in vertices.values():
  h=next((e for e,end in v if e['side']%2==0),None);w=next((e for e,end in v if e['side']%2==1),None)
  if h is None or w is None:continue
  c=dict(x=w['line'],y=h['line']);corners.append(c)
  for e,end in v:e['hi'if end else'lo']=(c['y']if e['side']%2 else c['x'])+(-.55 if end else .55)
 result=[]
 def emit(name,a,b,color,extra=None):
  length=math.dist(a,b)
  if length<.05:return
  count=math.ceil(length/16)
  for i in range(count):
   def at(t):return [a[j]+(b[j]-a[j])*t for j in range(3)]
   start=at(i/count);end=at((i+1)/count);vertical=start[0]==end[0]and start[1]==end[1];lo=[min(start[j],end[j])-(0 if vertical and j==2 else .5)for j in range(3)];hi=[max(start[j],end[j])+(0 if vertical and j==2 else .5)for j in range(3)]
   if overlaps((start[0]+end[0])/2,(start[1]+end[1])/2,lo[2],hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2],0):continue
   result.append(dict(name=name,x=(start[0]+end[0])/2,y=(start[1]+end[1])/2,z=lo[2],w=hi[0]-lo[0],d=hi[1]-lo[1],h=hi[2]-lo[2],rotation=0,color=color,component='beam',asset='Beam_Painted',start=start,end=end,**(extra or {} if i==0 else {})))
 for part in parts:
  if part['component']=='corner':continue
  edge=next((e for e in edges if e['side']==part['rotation']/90 and abs((part['y']if e['side']%2 else part['x'])-(e['start']+4))<.01 and abs((part['x']if e['side']%2 else part['y'])-e['line'])<.7),None)
  if edge is not None and part['component']in['wall','trim']and('lo'in edge or'hi'in edge):
   if part['component']=='trim':continue
   lo=edge.get('lo',edge['start']);hi=edge.get('hi',edge['start']+8);line=edge['line']+(-.3 if edge['side']in[0,3]else .3)if part['component']=='trim'else edge['line']
   for z in range(part['z'],part['z']+part['h']):
    a,b=([line,lo,z+.5],[line,hi,z+.5])if edge['side']%2 else([lo,line,z+.5],[hi,line,z+.5])
    emit('Angle · bardage ajusté',a,b,part['color'],dict(panelUnits=1/part['h']))
  elif part['component']=='beam'and part['start'][2]==part['end'][2]and(part['start'][0]==part['end'][0]or part['start'][1]==part['end'][1]):
   axis=1 if part['start'][0]==part['end'][0]else 0;fixed=1-axis;lo=min(part['start'][axis],part['end'][axis]);hi=max(part['start'][axis],part['end'][axis])
   for c in corners:
    v=c['y']if axis else c['x'];t=c['y']if fixed else c['x']
    if abs(part['start'][fixed]-t)>=1.05 or lo>=v+1.05 or hi<=v-1.05:continue
    if lo>=v-1.05:lo=v+1.05
    elif hi<=v+1.05:hi=v-1.05
    else:hi=lo
   if hi-lo>=1:
    a=list(part['start']);b=list(part['end']);a[axis]=lo;b[axis]=hi;emit(part['name'],a,b,part['color'])
  elif part['component']=='beam':
   if any(min(part['start'][0],part['end'][0])<c['x']+1.05 and max(part['start'][0],part['end'][0])>c['x']-1.05 and min(part['start'][1],part['end'][1])<c['y']+1.05 and max(part['start'][1],part['end'][1])>c['y']-1.05 for c in corners):continue
   result.append(part)
  else:result.append(part)
 for c in corners:
  if not overlaps(c['x'],c['y'],bottom,1,1,top-bottom,0):emit('Angle · montant unique',[c['x'],c['y'],bottom],[c['x'],c['y'],top],style.get('cornerColor',style['trim']))
 return result

def facade_bands(p,d):
 raw=math.ceil(max([8]+[o.get('z',0)+(o.get('h')or 6)for o in p['objects']]));top=min(p.get('height',p['size'])-1 if d['roof']else p.get('height',p['size']),math.ceil(raw/4)*4);base=footprint(p,d);n=p['size']//8;ny=p.get('depth',p['size'])//8;paths=access_paths(p);bands=[];z=0;min_x=min(x for x,y in base);max_x=max(x for x,y in base);min_y=min(y for x,y in base);max_y=max(y for x,y in base)
 if raw>top:
  import native_project as np
  raise np.ExportError(['La façade ou le toit dépasse la hauteur du blueprint. Choisissez un format supérieur.'])
 while z<top:
  h=4 if top-z>=4 else 1;cells=set(base)
  if d['facadeForm']!='flat':
   for x,y in sorted(base):
    middle=z>=8 and z+h<=top-4;central=min_x<x<max_x;rear=y==max_y;front=y==min_y
    tower=z<top*.6 and abs(x-(min_x+max_x)/2)<1
    target=middle and central and not tower and(front or rear)if d['facadeForm']=='warehouse'else middle and((front or rear)and min(x-min_x,max_x-x)%2!=0 or(x==min_x or x==max_x)and min(y-min_y,max_y-y)%2!=0)if d['facadeForm']=='gallery'else z>=max(8,math.ceil(top*.55/4)*4)and(x==min_x or y==min_y or x==max_x or y==max_y)
    if d['family']=='signature':
     from signature_design import recess
     target=recess(x,y,z,h,top,[min_x,max_x,min_y,max_y],d['seed'])
    if d['family']=='m05-kit':
     from m05_kit import recess
     target=recess(x,y,z,h,top,[min_x,max_x,min_y,max_y],d['seed'])
    if not target:continue
    occupied=False
    for o in p['objects']:
     w,depth=(o['d'],o['w'])if o['rotation']%180 else(o['w'],o['d']);w=w/2+1;depth=depth/2+1
     if o.get('z',0)<z+h+.5 and o.get('z',0)+(o.get('h')or 6)>z-.5 and o['x']+w>x*8 and o['x']-w<(x+1)*8 and o['y']+depth>y*8 and o['y']-depth<(y+1)*8:occupied=True;break
    crossed=any(max(a[2],b[2])>z-.5 and min(a[2],b[2])<z+h+.5 and max(a[0],b[0])>x*8-1 and min(a[0],b[0])<(x+1)*8+1 and max(a[1],b[1])>y*8-1 and min(a[1],b[1])<(y+1)*8+1 for pts in paths for i,b in enumerate(pts)for a in[pts[max(0,i-1)]])
    if not occupied and not crossed:cells.remove((x,y))
  if not cells:cells=set(base)
  bands.append(dict(bottom=z,top=z+h,cells=cells,globalTop=top,facadeForm=d['facadeForm']));z+=h
 return bands

def envelope(p,d):
 import native_design as nd
 style=dict(nd.STYLES[d['style']],**nd.PALETTES[d['palette']]);bands=facade_bands(p,d);plain=dict(p,design=dict(d,facadeForm='flat',roof=False));parts=[]
 for band in bands:parts.extend(nd.envelope(plain,band))
 glazed=set(roof_composition(p['size'],d['roofSeed'],d['roofLayout'],depth=p.get('depth',p['size']))['cells'])
 for i,band in enumerate(bands):
  for ix,iy in sorted(band['cells']):
   last=i==len(bands)-1;above=bands[i+1]['cells']if not last else None
   if last or above is not None and(ix,iy)in above:continue
   light=last and(d['roofStyle']=='glass'or d['roofStyle']=='skylights'and f'{ix},{iy}'in glazed);stem='Roof_Window'if light else'Roof_Orange'if d['roofStyle']=='ficsit'else'Roof_Tar';slope=last and d['roofForm']in['ridges','sawtooth']and band['top']+2.3<=p.get('height',p['size'])
   parts.append(dict(name='Toiture'if last else'Terrasse de retrait',x=ix*8+4,y=iy*8+4,z=band['top']+.05,w=8,d=8,h=2 if slope else .5,rotation=180 if slope and d['roofForm']=='ridges'and ix%2==0 else 0,color='#91bbc7'if light else'#656e69',component='roof',asset=stem+('_03'if slope else'_01'),**(dict(slope='roof')if slope else{})))
 for i in range(1,len(bands)):
  for ix,iy in sorted(bands[i]['cells']):
   if(ix,iy)not in bands[i-1]['cells']:parts.append(dict(name='Sous-face du volume saillant',x=ix*8+4,y=iy*8+4,z=bands[i]['bottom']-.55,w=8,d=8,h=.5,rotation=0,color=style['wall'],component='roof',asset='Roof_Tar_01'))
 if d['roof']:
  last=bands[-1];cap=dict(p,design=dict(d,facadeForm='flat'))
  parts.extend(q for q in nd.envelope(cap,dict(bottom=last['top'],top=last['top'],globalTop=last['top'],cells=last['cells']))if q['component']in['roof','gable']or q['name']=='Lanterneau · vitrage vertical')
 columns={};result=[]
 for part in parts:
  if part['name']not in['Angle · montant unique','Trame modulaire · montant']:result.append(part);continue
  columns.setdefault((part['name'],part['x'],part['y']),[]).append(part)
 for group in columns.values():
  group.sort(key=lambda a:a['z']);current=None
  for part in group:
   if current is not None and part['z']<=current['z']+current['h']+.01:current['end']=part['end'];current['h']=part['z']+part['h']-current['z']
   else:current=dict(part);result.append(current)
 final=[]
 for part in result:
  if 'start'not in part or math.dist(part['start'],part['end'])<=16:final.append(part);continue
  count=math.ceil(math.dist(part['start'],part['end'])/16)
  for i in range(count):
   start=[part['start'][j]+(part['end'][j]-part['start'][j])*i/count for j in range(3)];end=[part['start'][j]+(part['end'][j]-part['start'][j])*(i+1)/count for j in range(3)]
   final.append(dict(part,start=start,end=end,z=start[2],h=end[2]-start[2]))
 return final
