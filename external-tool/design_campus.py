"""Instantiate shared, native-size architectural room prefabs, without scaling."""
import copy
def assembly(spec,p):
 key=f"{p['size']}x{p.get('depth',p['size'])}x{p['design'].get('campusLevels',3)}"
 if key not in spec['grammar']['assemblies']:
  from native_project import ExportError
  raise ExportError(['Noyau : largeurs 64 ou 96 m, longueurs 48 / 64 / 80 m et 1 à 3 niveaux.'])
 return spec['grammar']['assemblies'][key]
def parts(spec,p):
 a=assembly(spec,p);out=[];seen=set()
 for inst in a['instances']:
  for source in spec['grammar']['prefabs'][inst['prefab']]:
   q=copy.deepcopy(source)
   for i,k in enumerate(['x','y','z']):q[k]+=inst['at'][i]
   q.update(name=inst['prefix']+' · '+q['name'],color=q['color']if spec.get('floorPalette')else spec['grammar']['palettes'][max(0,spec['interiorStyles'].index(p['design'].get('interiorStyle','creuset')))if spec.get('interiorStyles')else inst['phase']][q.get('colorSlot','wall')],campusLevel=inst['level'],campusRole=inst['prefab'])
   if q.get('ledPanel'):
    import re
    color=p['design'].get('ledColor',spec.get('ledColor'))
    if not isinstance(color,str)or not re.fullmatch('#[0-9a-fA-F]{6}',color):raise ValueError('Couleur LED invalide.')
    q['color']=color
   if 'signatureBounds'in q:q['signatureBounds']=[[v+inst['at'][i]for v in r]for i,r in enumerate(q['signatureBounds'])]
   for k in ['walkStart','walkEnd']:
    if k in q:q[k]=[v+inst['at'][i]for i,v in enumerate(q[k])]
   key=(q['asset'],*[round(q[k],5)for k in ['x','y','z']],q['rotation']%180 if q['asset'].startswith('Wall_')else q['rotation'])+(tuple(q['quat'])if spec.get('squareModule')and q.get('quat')else())
   if key not in seen:seen.add(key);out.append(q)
 return out


def floor_color(p,f,x,y,fallback):
 import native_design
 spec=native_design.CATALOG['studies'].get(p.get('design',{}).get('family'),{})
 if not spec.get('designFirst'):return fallback
 if spec.get('floorPalette'):
  pal=spec['floorPalette'];cx=p['size']/2;plan=spec['floorPlan'];lane=abs(x-cx)<8 if plan in['creuset','atelier']else(abs(x-cx)>8 or y<16 or y>p.get('depth',48)-20)if plan=='horizon'else False
  return pal['lane']if lane else pal['floor']
 color=fallback
 if p['design']['family']=='noyau'and f['z']>0:color=spec['grammar']['palettes'][max(0,spec['interiorStyles'].index(p['design'].get('interiorStyle','creuset')))]['floor']
 if p['design']['family']=='noyau'and f['z']>0 and abs(x-p['size']/2)<8.1:
  import native_design
  phase=max(0,min(2,spec['interiorStyles'].index(p['design'].get('interiorStyle','creuset'))));color=native_design.CATALOG['studies']['noyau']['grammar']['palettes'][phase]['frame']
 if not color:return fallback
 factor=.94 if(int(x//8)+int(y//8))%2 else 1
 return '#'+''.join(format(int(int(color[i:i+2],16)*factor+.5),'02x')for i in[1,3,5])
