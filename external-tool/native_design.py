"""Native architecture made from component-free lightweight game buildings.

Coordinates match WorkshopDesign.envelope. Walls use a bottom origin and local
Y width; flat roofs and small pillars use a centre origin (installed game Docs).
No world references, arbitrary actor classes, scaling or in-game save writes.
"""
import math,json,re
from blueprint_dimensions import dimensions
from pathlib import Path
CATALOG=json.loads((Path(__file__).parent/'data/architecture-styles.json').read_text(encoding='utf-8'))
PALETTES=CATALOG['palettes']
import native_blueprint as n
from architecture_patterns import roof_composition,footprint,opening_groups,entrance,access_paths
from native_factory import q,aset

STYLES={
 'concrete':dict(packs=['concrete'],wall='#a0a49e',trim='#656e69',windowEvery=3),
 'ficsit':dict(packs=['concrete','metal'],wall='#48545a',trim='#e9a043',windowEvery=4),
 'glass':dict(packs=['metal','glass'],wall='#607e89',trim='#b1bfc3',windowEvery=1),
}

def settings(value):
 import native_project as p
 d=dict(fit='plot',facadeForm='warehouse'if value.get('family')=='warehouse'else'flat',enabled=False,style='concrete',family='custom',variant=1,palette='default',pattern='classic',structure='none',entryTreatment='frame',seed=1,roofSeed=1,roofForm='auto',roofLayout='auto',wallDecoration='frames',footprint='rectangle',entrance='auto',roof=True,roofStyle='tar',detail='bands',windowEvery=0,cornerWidth=.5,packs=['concrete'],colors={},wallMaterial='original')
 if not isinstance(value,dict):raise p.ExportError(['Style architectural invalide.'])
 d.update(value)
 from architecture_surfaces import CATEGORIES
 if d['wallMaterial']not in['original','concrete','ficsit']or not isinstance(d['colors'],dict)or any(k not in CATEGORIES or not isinstance(v,str)or not re.fullmatch('#[0-9a-fA-F]{6}',v)for k,v in d['colors'].items()):raise p.ExportError(['Peinture ou matière architecturale invalide.'])
 if (d['fit']not in['plot','occupied']or d['facadeForm']not in ['flat','warehouse','gallery','terraces','signature']or d['family']not in ['custom',*CATALOG['families']]or type(d['variant'])is not int or not 1<=d['variant']<=999 or d['palette']not in PALETTES or d['pattern']not in ['classic','paired','ribbon','alternating','upper','full']or d['structure']not in ['none','grid','columns']or d['entryTreatment']not in ['frame','porch','double']or d['entrance'] not in ['auto','none','front','right','back','left'] or d['roofLayout'] not in ['auto','central','pair','quartet','triple','band','ring'] or d['wallDecoration'] not in ['none','frames','braces','lattice'] or d['footprint'] not in ['rectangle','stepped','l','u','cross'] or type(d['enabled'])is not bool or d['style'] not in STYLES or type(d['seed'])is not int or not 1<=d['seed']<=999 or type(d['roof'])is not bool or type(d['roofSeed'])is not int or not 1<=d['roofSeed']<=999 or d['roofForm'] not in ['auto','flat','ridges','monitor','sawtooth'] or d['roofStyle'] not in ['tar','ficsit','glass','skylights'] or d['detail'] not in ['none','bands'] or type(d['windowEvery'])is not int or d['windowEvery'] not in [0,1,2,3,4,99] or type(d['cornerWidth'])not in [int,float] or d['cornerWidth'] not in [0,.3,.5,1,2] or not isinstance(d['packs'],list) or any(x not in ['concrete','metal','glass'] for x in d['packs'])):raise p.ExportError(['Style architectural invalide.'])
 if d['enabled'] and not all(x in d['packs'] for x in STYLES[d['style']]['packs']):raise p.ExportError(['Ce style utilise un pack non débloqué.'])
 from authored_living import validate
 validate(d)
 if 'studyFitted'in d and type(d['studyFitted'])is not bool:raise p.ExportError(['Adaptation de création invalide.'])
 if 'studyFloors'in d:
  rows=d['studyFloors']
  if not isinstance(rows,list)or len(rows)>64 or any(not isinstance(r,dict)or type(r.get('z'))not in[int,float]or not math.isfinite(r['z'])or not isinstance(r.get('cells'),list)or len(r['cells'])>144 or any(not isinstance(c,list)or len(c)!=2 or any(type(v)is not int or not 0<=v<12 for v in c)for c in r['cells'])for r in rows):raise p.ExportError(['Planchers de création invalides.'])
 return d

def window_at(d,style,start,side,z,top,h,size):
 if h!=4 or d['windowEvery']==99 or z==0 and not(d['family']!='custom'and top<=12 and d['style']!='concrete'):return False
 if d['family']=='signature'and not d['windowEvery']:
  from signature_design import window_at
  return window_at(start,side,z,top,size,d['seed'])
 if d['family']=='m05-kit'and not d['windowEvery']:
  from m05_kit import window_at
  return window_at(start,side,z,top,size,d['seed'])
 if d['family']=='warehouse'and d['facadeForm']!='flat'and not d['windowEvery']:
  bay=math.floor(start/8);n=size//8
  return z>=top-4 or z>=8 and z<top-8 and bay in[1,n-2]
 if d['windowEvery']or d['pattern']=='classic':return(start/8+side+d['seed'])%(d['windowEvery']or style['windowEvery'])==0
 bay=math.floor(start/8);distance=min(bay,size/8-1-bay);row=math.floor(z/4)
 if d['pattern']=='paired':return(distance+math.floor((d['seed']-1)/2))%3!=2
 if d['pattern']=='ribbon':return row%3==min(1+d['seed']%2,max(1,math.floor((top-4)/4)))
 if d['pattern']=='alternating':return(distance+row+d['seed'])%2==0
 if d['pattern']=='upper':return z+h>=top-4
 return d['pattern']=='full'


def envelope(project,geometry=None):
 from architecture_surfaces import apply
 parts=raw_envelope(project,geometry)
 if geometry is None and project.get('design',{}).get('family')=='m05-kit':
  from m05_kit import decorate
  parts=decorate(parts,project,access_paths(project))
 if geometry is None and project.get('design',{}).get('family')=='signature':
  from signature_design import decorate
  design=settings(project['design']);parts=decorate(parts,project,access_paths(project),dict(STYLES[design['style']],**PALETTES[design['palette']]))
 from manifold_interior import parts as clean_parts
 return apply(parts,settings(project.get('design',{})))+clean_parts(project)

def raw_envelope(project,geometry=None):
 import native_project as p
 d=settings(project.get('design',{}))
 if not d['enabled']:return []
 if CATALOG['families'].get(d['family'],{}).get('nativeStudy'):
  from authored_study import envelope
  return envelope(project,d,CATALOG)
 if d['family']=='m05':
  from m05_architecture import envelope as m05_envelope
  return m05_envelope(project)
 if geometry is None and d['facadeForm']!='flat':
  from modular_architecture import envelope as modular_envelope
  return modular_envelope(project,d)
 style=dict(STYLES[d['style']],**PALETTES[d['palette']]);size,depth,height=dimensions(project);top=geometry['top']if geometry else math.ceil(max([8]+[o.get('z',0)+(o.get('h')or 6)for o in project['objects']]));bottom=geometry['bottom']if geometry else 0;sloped=d['roofForm']in['ridges','sawtooth']and top+2.3<=height or d['roofForm']=='auto' and d['roofSeed']%2==0 and top+2.3<=height;rise=2 if sloped else 0;monitor=d['roofForm']=='monitor'and top+4.5<=height;parts=[];missing=[];cells=geometry['cells']if geometry else footprint(project,d);composition=roof_composition(size,d['roofSeed'],d['roofLayout'],cells,depth);glazed=set(composition['cells']);roof_mid=(min(x for x,y in cells)+max(x for x,y in cells))/2
 def high_roof(ix):return ix in[math.floor(roof_mid),math.ceil(roof_mid)]
 if top>height or d['roof'] and top+max(.5,rise+.3)>height:raise p.ExportError(['La façade ou le toit dépasse la hauteur du blueprint. Choisissez un format supérieur.'])
 wall='Wall_Concrete_8x4' if d['style']=='concrete' else 'Wall_8x4_01'
 glass='Wall_Window_8x4_05'if d['family']=='warehouse'else'Wall_Concrete_8x4_Window_02' if d['style']=='concrete' else 'Wall_Window_Thin_8x4_01' if d['style']=='glass' else 'Wall_Window_8x4_01'
 shapes=[]
 for o in project['objects']:
  rows={'smelter':[(0,0,5,10,4.5),(1.45,4.5,5,7.1,4)],'constructor':[(0,0,8,10,6)],'assembler':[(-.5,0,9,17,3),(.75,3,9,5.5,5),(0,8,.2,.2,2.75)]}.get(o['type'])if o.get('native')else None
  if rows:
   a=math.radians(o['rotation']+180)
   shapes.extend(dict(o,x=o['x']-math.sin(a)*cy,y=o['y']+math.cos(a)*cy,z=o['z']+z,w=w,d=depth,h=h)for cy,z,w,depth,h in rows)
  else:shapes.append(o)
 def overlaps(x,y,z,w,depth,h,rotation):
  ww,dd=(depth,w)if rotation%180 else(w,depth)
  for o in shapes:
   ow,od=(o['d'],o['w'])if o['rotation']%180 else(o['w'],o['d'])
   if min(x+ww/2,o['x']+ow/2)-max(x-ww/2,o['x']-ow/2)>.001 and min(y+dd/2,o['y']+od/2)-max(y-dd/2,o['y']-od/2)>.001 and min(z+h,o.get('z',0)+(o.get('h')or 6))-max(z,o.get('z',0))>.001:return True
  return False
 def box(name,x,y,z,w,depth,h,rotation,color,component,asset,**extra):
  if overlaps(x,y,z,w,depth,h,rotation):return False
  parts.append(dict(name=name,x=x,y=y,z=z,w=w,d=depth,h=h,rotation=rotation,color=color,component=component,asset=asset,**extra));return True
 def beam(name,a,b):
  length=math.dist(a,b)
  if length<1:return
  if length>16:
   count=math.ceil(length/16)
   def at(i):return [a[j]+(b[j]-a[j])*i/count for j in range(3)]
   for i in range(count):beam(name,at(i),at(i+1))
   return
  minimum=[min(a[i],b[i])-.5 for i in range(3)];maximum=[max(a[i],b[i])+.5 for i in range(3)]
  if min(minimum)<-.001 or maximum[0]>size+.001 or maximum[1]>depth+.001 or maximum[2]>height+.001 or overlaps((minimum[0]+maximum[0])/2,(minimum[1]+maximum[1])/2,minimum[2],maximum[0]-minimum[0],maximum[1]-minimum[1],maximum[2]-minimum[2],0):return
  parts.append(dict(name=name,x=(a[0]+b[0])/2,y=(a[1]+b[1])/2,z=minimum[2],w=maximum[0]-minimum[0],d=maximum[1]-minimum[1],h=maximum[2]-minimum[2],rotation=0,color=style['trim'],component='beam',asset='Beam_Painted',start=a,end=b))
 def facade(side,line,u,z):return [line,u,z]if side%2 else[u,line,z]
 decorated=d['structure']!='none' or d['wallDecoration']!='none' or d['detail']=='bands' or d['cornerWidth']>0;inset=.9
 def decor_line(side,line,depth=.6):return line+(depth-inset if side in[0,3]else inset-depth)
 edges=[]
 for ix,iy in cells:
  for dx,dy,side in [(0,-1,0),(1,0,1),(0,1,2),(-1,0,3)]:
   if(ix+dx,iy+dy)not in cells:edges.append(dict(side=side,start=(iy if side%2 else ix)*8,line=iy*8+inset if side==0 else(ix+1)*8-inset if side==1 else(iy+1)*8-inset if side==2 else ix*8+inset))
 edges.sort(key=lambda e:(e['side'],e['line'],e['start']))
 entry=entrance(project,edges,overlaps)
 rows=[];z=bottom
 while z<top:
  h=4 if top-z>=4 else 1;rows.append((z,h));z+=h
 for edge in edges:
  side,start,line=edge['side'],edge['start'],edge['line'];span=depth if side%2 else size
  for z,h in rows:
   if entry and side==entry['side']and line==entry['line']and start==entry['start']and z<8:continue
   center=start+4;x,y,_=facade(side,line,center,z);rot=side*90;window=window_at(dict(d,facadeForm=geometry['facadeForm'])if geometry and geometry.get('facadeForm')else d,style,start,side,z,geometry['globalTop']if geometry else top,h,span)
   if not box('Fenêtre'if window else'Mur plein',x,y,z,8,.5,h,rot,style.get('window','#7aabb9')if window else style['wall'],'window'if window else'wall',glass if window else('Wall_Concrete_8x1'if d['style']=='concrete'else'Wall_Orange_8x1')if h==1 else wall):missing.append(dict(side=side,line=line,u=start,z=z,h=h))
   if d['detail']=='bands' and z+h==(geometry['globalTop']if geometry else top):
    offset=.3-inset;xx=x+(-offset if side==1 else offset if side==3 else 0);yy=y+(offset if side==0 else -offset if side==2 else 0)
    box('Bandeau décoratif',xx,yy,z+h-1,8,.5,1,rot,style['trim'],'trim','Wall_Concrete_8x1'if d['style']=='concrete'else'Wall_Orange_8x1')
   if d['wallDecoration']in['braces','lattice']and h==4 and not window and(d['wallDecoration']=='lattice'or(start//8+side+d['seed'])%2==0):
    beamline=decor_line(side,line);flip=(start//8+math.floor(z/4)+side+d['seed'])%2==0;a=facade(side,beamline,start+.5,z+h-.5 if flip else z+.5);b=facade(side,beamline,start+7.5,z+.5 if flip else z+h-.5)
    beam('Contreventement diagonal',a,b)
    if d['wallDecoration']=='lattice':beam('Croix de contreventement',facade(side,decor_line(side,line,.7),start+.5,z+.5 if flip else z+h-.5),facade(side,decor_line(side,line,.7),start+7.5,z+h-.5 if flip else z+.5))
 if d['structure']!='none':
  for edge in edges:
   side,start,line=edge['side'],edge['start'],edge['line'];l=decor_line(side,line);last=not any(e['side']==side and e['line']==line and e['start']==start+8 for e in edges);posts=[max(.5,start)]+([min((depth if side%2 else size)-.5,start+8)]if last else[])
   for u in posts:beam('Trame modulaire · montant',facade(side,l,u,bottom+.5),facade(side,l,u,top-.5))
   if d['structure']=='grid':
    for z in range(max(4,bottom),top,4):
     if entry and side==entry['side']and line==entry['line']and start==entry['start']and z<8:continue
     rail=decor_line(side,line,.8);beam('Trame modulaire · traverse',facade(side,rail,start+.5,z-.5),facade(side,rail,start+7.5,z-.5))
 if d['wallDecoration']!='none':
  for gap in opening_groups(missing):
   side,start,end,gap_bottom,cap=gap['side'],gap['start'],gap['end'],gap['bottom'],gap['top'];line=decor_line(side,gap['line'],.75 if d['structure']!='none'else .6)
   a=facade(side,line,start+.5,gap_bottom+.5);b=facade(side,line,end-.5,gap_bottom+.5);c=facade(side,line,end-.5,cap-.5);e=facade(side,line,start+.5,cap-.5)
   beam('Baie industrielle · jambage',facade(side,line,start+.5,gap_bottom+1),facade(side,line,start+.5,cap-1));beam('Baie industrielle · jambage',facade(side,line,end-.5,gap_bottom+1),facade(side,line,end-.5,cap-1));beam('Baie industrielle · linteau',e,c);beam('Baie industrielle · traverse basse',a,b)
 if entry and bottom==0:
  side,start,line,base=entry['side'],entry['start'],decor_line(entry['side'],entry['line'],.7 if d['structure']!='none'else .6),entry['base']
  beam('Entrée piétonne · jambage',facade(side,line,start+.5,base+.5),facade(side,line,start+.5,6.5));beam('Entrée piétonne · jambage',facade(side,line,start+7.5,base+.5),facade(side,line,start+7.5,6.5));beam('Entrée piétonne · linteau',facade(side,line,start+.5,7.5),facade(side,line,start+7.5,7.5))
  if d['entryTreatment']!='frame':
   back=decor_line(side,entry['line'],3)
   if d['entryTreatment']=='double':
    for u in [start+.5,start+7.5]:beam('Portique · montant intérieur',facade(side,back,u,base+.5),facade(side,back,u,6.5))
   beam('Portique · traverse intérieure',facade(side,back,start+.5,7.5),facade(side,back,start+7.5,7.5))
   for u in [start+.5,start+2.5,start+5.5,start+7.5]if d['entryTreatment']=='porch'else[start+.5,start+7.5]:beam('Portique · brise-soleil',facade(side,line,u,7.3),facade(side,back,u,7.3))
 if d['cornerWidth']:
  for x in [1,size-1]:
   for y in [1,depth-1]:
    if (0 if x<2 else size//8-1,0 if y<2 else depth//8-1)not in cells:continue
    for z in range(bottom,top-3,4):box('Pilier de coin',x,y,z,2,2,4,0,style['trim'],'corner','Pillar_Small_Concrete' if d['style']=='concrete' else 'Pillar_Small_Metal')
 if d['roof']:
  for x in range(4,size,8):
   for y in range(4,depth,8):
    ix=(x-4)//8;iy=(y-4)//8
    if(ix,iy)not in cells:continue
    skylight=d['roofStyle']=='glass' or d['roofStyle']=='skylights' and f'{ix},{iy}'in glazed
    rotation=(0 if d['roofForm']=='sawtooth'or ix%2 else 180)if sloped else 0
    raised=monitor and high_roof(ix);roof_z=top+(4 if raised else 0)
    stem='Roof_Window' if skylight else 'Roof_Orange' if d['roofStyle']=='ficsit' else 'Roof_Tar'
    box('Verrière à ossature' if skylight else 'Toiture',x,y,roof_z+(.15 if sloped else 0),8,8,2 if sloped else .5,rotation,'#91bbc7'if skylight else style['trim']if d['roofStyle']=='ficsit'else'#656e69','roof',stem+('_03' if sloped else '_01'),**({'slope':'roof'} if sloped else {}))
    if raised:
     for dx,dy,side in [(0,-1,0),(1,0,1),(0,1,2),(-1,0,3)]:
      nx,ny=ix+dx,iy+dy;high=(nx,ny)in cells and high_roof(nx)
      if high:continue
      line=y-3.75 if side==0 else x+3.75 if side==1 else y+3.75 if side==2 else x-3.75;wx,wy,_=facade(side,line,y if side%2 else x,top)
      box('Lanterneau · vitrage vertical',wx,wy,top,8,.5,4,side*90,style.get('window','#91bbc7'),'window',glass)
    if sloped:
     for dy,yy in [(-1,y-3.75),(1,y+3.75)]:
      if(ix,iy+dy)not in cells:box('Pignon incliné',x,yy,top,8,.5,2,180 if rotation==0 else 0,style['wall'],'gable','Wall_Orange_Tris_8x2',slope='gable')
     if d['roofForm']=='sawtooth'or(ix-1,iy)not in cells and rotation==0 or(ix+1,iy)not in cells and rotation==180:
      for z in range(top,top+2):box('Rive de toit',x-3.75 if rotation==0 else x+3.75,y,z,8,.5,1,90,style['wall'],'gable','Wall_Orange_8x1')
 from modular_architecture import join_corners
 return join_corners(parts,edges,inset,bottom,top,dict(style,cornerColor=style['trim']if d['cornerWidth']else style['wall']),overlaps)

def add(assembly,project,assets):
 import native_project as p
 if project.get('design',{}).get('enabled')and project['design'].get('family')=='m05':
  from m05_architecture import add as add_m05
  return add_m05(assembly,project,assets)
 parts=envelope(project);counts=dict(total=len(parts),walls=0,windows=0,pillars=0,trims=0,roofs=0,beams=0)
 if not parts:return counts
 piece=p.load('native-design-template.json')['piece'];half=project['size']/2;half_y=project.get('depth',project['size'])/2
 placed_lighting=[]
 for part in parts:
  if part['component']=='module':
   from m05_kit import add_piece
   actor=add_piece(assembly,part,project,assets)
   if part.get('livingCircuit')is not None:placed_lighting.append((part,actor))
   counts['trims']+=1;continue
  cls='Build_'+part['asset']+'_C';recipe='Recipe_'+part['asset']+'_C'
  if cls not in assets or recipe not in assets:raise p.ExportError(['Pièce architecturale native inconnue.'])
  if part['component']=='beam':
   a,b=part['start'],part['end'];direction=[b[i]-a[i]for i in range(3)];length=math.sqrt(sum(v*v for v in direction));dx,dy,dz=[v/length for v in direction]
   # Native beam length runs from its origin along local +X.
   quat=[0.,-dz,dy,1+dx]if dx>-.999999 else[0.,0.,1.,0.];norm=math.sqrt(sum(v*v for v in quat));quat=[v/norm for v in quat]
   actor=assembly.clone(p.load('native-beam-template.json')['piece'],[(a[0]-half)*100,(a[1]-half_y)*100,a[2]*100],quat)
   actor[0].typePath=assets[cls]['path'];aset(actor,'mLength',length*100,['FloatProperty',0]);aset(actor,'mBuiltWithRecipe',p.ref(assets[recipe]['path']),['ObjectProperty',0]);p.paint(actor,part['color']);counts['beams']+=1;continue
  z=part['z']+(part['h']/2 if part['component'] in ['roof','corner'] else 0)
  angle=part['rotation']+(-90 if part['component'] in ['wall','window','trim','gable'] else 0)
  actor=assembly.clone(piece,[(part['x']-half)*100,(part['y']-half_y)*100,z*100],q(angle))
  actor[0].typePath=assets[cls]['path'];actor[0].instanceName=actor[0].instanceName.replace('Build_Foundation_8x1_01_C',cls)
  aset(actor,'mBuiltWithRecipe',p.ref(assets[recipe]['path']),['ObjectProperty',0]);p.paint(actor,part['color'])
  counts[dict(wall='walls',gable='walls',window='windows',corner='pillars',trim='trims',roof='roofs')[part['component']]]+=1
 if placed_lighting:
  from living_lighting import connect
  info=connect(assembly,project,placed_lighting,assets);counts.update(info);counts['total']+=info['lightWires']
 return counts

def floor_stem(material,thickness):
 import native_project as p
 prefixes={'steel':'','concrete':'Concrete_','asphalt':'Asphalt_','polished':'ConcretePolished_','metal':'Metal_'}
 if material not in prefixes or thickness not in [1,2] or material in ['polished','metal'] and thickness!=1:raise p.ExportError(['Béton ciré et tôle antidérapante : fondations natives de 1 m uniquement.'])
 return 'Foundation_'+prefixes[material]+'8x'+str(thickness)+('_01' if material=='steel' else '')




def floor_cells(project,floor):
 if project.get('design',{}).get('enabled')and CATALOG['families'].get(project['design'].get('family'),{}).get('nativeStudy')and project['design'].get('studyFitted'):return {tuple(c)for r in settings(project['design']).get('studyFloors',[])if r['z']==floor['z']for c in r['cells']}
 width=project['size'];depth=project.get('depth',width)
 if project.get('design',{}).get('enabled')and project['design'].get('family')=='m05':
  ox=(width-width//40*40)/2;oy=(depth-depth//40*40)/2
  cells={(x,y)for x in range(width//8)for y in range(depth//8)if x*8>=ox+24 and x*8+8<=width-ox-24 and y*8>=oy+24 and y*8+8<=depth-oy-24}
 else:
  cells={(x,y)for x in range(width//8)for y in range(depth//8)}
  if project.get('generation',{}).get('shape')=='exotic'or project.get('design',{}).get('fit')=='occupied'or project.get('design',{}).get('enabled')and floor['z']>0:
   d=settings(project['design'])
   if d['facadeForm']=='flat':cells&=footprint(project,d)
   else:
    from modular_architecture import facade_bands
    band=next((b for b in facade_bands(project,d)if b['bottom']<=floor['z']+floor.get('thickness',1)<b['top']),None)
    cells&=band['cells']if band else footprint(project,d)
 if project.get('design',{}).get('enabled'):
  top=floor['z']+floor['thickness'];surfaces=[]
  for q in envelope(project):
   if q['asset']not in['Roof_Tar_01','Roof_Orange_01','Roof_Window_01']:continue
   b=q.get('signatureBounds')or([[q['x']-4,q['x']+4],[q['y']-4,q['y']+4],[q['z'],q['z']+q['h']]]if q['component']=='roof'else None)
   if b and abs(b[2][1]-top)<.8:surfaces.append(b)
  cells={c for c in cells if not any(min(b[0][1],c[0]*8+8)-max(b[0][0],c[0]*8)>7 and min(b[1][1],c[1]*8+8)-max(b[1][0],c[1]*8)>7 for b in surfaces)}
 return sorted(cells)

def add_floor(assembly,project,floor,x,y,assets):
 import native_project as p
 pos=[(x-project['size']/2)*100,(y-project.get('depth',project['size'])/2)*100,0]
 profile=floor.get('profile','solid')
 if profile=='frame':
  pos[2]=(floor['z']+1.4)*100;actor=assembly.clone(p.load('native-frame-template.json'),pos,q(0))
 else:
  factory=profile=='factory';stem='Roof_Tar_01'if factory else floor_stem(floor['material'],floor['thickness']);pos[2]=(floor['z']+floor['thickness']-.09 if factory else floor['z']+floor['thickness']/2)*100
  actor=assembly.clone(p.load('native-design-template.json')['piece'],pos,q(0));actor[0].typePath=assets['Build_'+stem+'_C']['path'];aset(actor,'mBuiltWithRecipe',p.ref(assets['Recipe_'+stem+'_C']['path']),['ObjectProperty',0])
 from authored_living import floor_color
 color=floor_color(project,floor,x,y,p.design_color(project,'floors')or floor.get('color'))
 if color:p.paint(actor,color)
 return profile
