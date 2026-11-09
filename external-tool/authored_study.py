"""Interpret an authored, fixed-size native composition from the shared catalog."""
import copy
from authored_layout import expand,widen,repeat_bays

def envelope(project,d,catalog):
 if project.get('nativeProfile')=='clean-manifold-v1':
  probe=copy.deepcopy(project);probe.pop('nativeProfile');probe['design'].pop('living',None);probe['design']['studyFitted']=False;probe.update(objects=[],links=[],floors=[dict(z=0,thickness=1)]);return envelope(probe,probe['design'],catalog)
 from native_project import ExportError
 from architecture_patterns import access_paths
 spec=catalog['studies'][catalog['families'][d['family']]['nativeStudy']];width,depth,height=spec['dimensions']
 extra=project.get('depth',project['size'])-depth;width_extra=project['size']-width
 if width_extra<0 or width_extra>(48 if spec.get("workshopCompatible")else 32) or width_extra%8!=0 or extra<0 or extra>(48 if spec.get("workshopCompatible")else 32) or extra%8!=0 or project.get('height',project['size'])<height:raise ExportError(['Étude architecturale : largeur 64 à 96 m, longueur 48 à 80 m par travées de 8 m, hauteur de 32 m minimum. Ouvrez la maquette fournie.'])
 if not d.get('studyFitted')and(len(project.get('floors',[]))!=1 or project['floors'][0]['z']!=0 or project['floors'][0]['thickness']!=1):raise ExportError(['Étude architecturale : le plan de production utilise un sol de 1 m au niveau zéro. Les terrasses appartiennent à la composition.'])
 from authored_living import transform,terraces,assert_fresh,clean_parts
 assert_fresh(project)
 from design_campus import parts as campus_parts
 parts=clean_parts(terraces(transform(campus_parts(spec,project)if spec.get('grammar')else repeat_bays(spec['parts'],width_extra,extra,spec['repeatBay'])if spec.get('repeatBay')else widen(expand(spec['parts'],extra),width_extra),project),project),project)+copy.deepcopy(d.get('living',{}).get('fixtures',[]))+copy.deepcopy(d.get('living',{}).get('accessParts',[]))
 if any((q.get('signatureBounds')or[[0,0],[0,0],[q['z'],q['z']+q['h']]])[2][1]>project.get('height',project['size'])+.05 for q in parts):raise ExportError(['La création adaptée dépasse la hauteur du terrain. Augmentez la hauteur.'])
 if d.get('living'):
  parts=[dict(q,livingCircuit='living-existing')if q['asset']=='FloodlightWall'and not q.get('livingCircuit')else q for q in parts]
 def bounds(q):
  if q.get('beamRadius'):
   from compact_rules import beam_bounds
   return beam_bounds(q)
  if q.get('type')=='wallPole'and q.get('native',{}).get('ceilingMounted'):return[[q['x']-.3,q['x']+.3],[q['y']-.3,q['y']+.3],[q['z']-.8,q['z']+.02]]
  if q.get('type')=='wallPole'and q.get('native',{}).get('wallMounted'):
   import math
   r=math.radians(q['rotation']);v=[round(math.cos(r)),round(math.sin(r))];a=0 if v[0]else 1;pos=[q['x'],q['y']];b=[[pos[0]-.3,pos[0]+.3],[pos[1]-.3,pos[1]+.3],[q['z'],q['z']+.6]];b[a]=[pos[a],pos[a]+.6]if v[a]>0 else[pos[a]-.6,pos[a]];return b
  if q.get('signatureBounds'):return q['signatureBounds']
  w,depth=(q['d'],q['w'])if q.get('rotation',0)%180 else(q['w'],q['d'])
  return[[q['x']-w/2,q['x']+w/2],[q['y']-depth/2,q['y']+depth/2],[q['z'],q['z']+q['h']]]
 def overlap(a,b):return all(min(r[1],b[i][1])-max(r[0],b[i][0])>.05 for i,r in enumerate(a))
 parts=[q for q in parts if q['component']not in['wall','window']or not any(overlap(bounds(q),b)for b in d.get('living',{}).get('openings',[]))]
 from compact_rules import validate as validate_compact
 validate_compact(project,parts)
 for o in project['objects']:
  if o['type']in['input','output','entry','exit','port']:continue
  box=bounds(dict(o,z=o.get('z')or 0,h=o.get('h')or 6))
  for q in parts:
   if q['component']=='module'and not q.get('signatureBounds'):continue
   if o.get('native',{}).get('ceilingMounted')and q.get('compactAssembly')=='ceiling-electric':continue
   if overlap(box,bounds(q)):raise ExportError(['Étude architecturale : '+o['name']+' rencontre '+q['name']+'. Cette composition fixe ne déplace pas les machines.'])
 for points in access_paths(project):
  for i in range(1,len(points)):
   box=[[min(v,points[i][j])-.25,max(v,points[i][j])+.25]for j,v in enumerate(points[i-1])]
   for q in parts:
    if q['component']=='module'and not q.get('signatureBounds'):continue
    if overlap(box,bounds(q)):raise ExportError(['Étude architecturale : un trajet logistique rencontre '+q['name']+'.'])
 if d.get('studyFitted'):
  for f in project.get('floors',[]):
   for x,y in next((r['cells']for r in d.get('studyFloors',[])if r['z']==f['z']),[]):
    if x*8>=project['size']or y*8>=project.get('depth',project['size']):raise ExportError(['Plancher hors de la création.'])
    box=[[x*8,x*8+8],[y*8,y*8+8],[f['z'],f['z']+f['thickness']]]
    for q in parts:
     if f['z']==0 and q['component']=='beam'and bounds(q)[2][0]<1<bounds(q)[2][1]:continue
     if q['asset']in['CatwalkCross','CatwalkStraight','CatwalkStairs','CatwalkRamp']and abs(q['z']-f['z']-f['thickness'])<.2:continue
     if q['component']=='module'and not q.get('signatureBounds'):continue
     if overlap(box,bounds(q)):raise ExportError(['Un plancher rencontre '+q['name']+'. Réappliquez la création.'])
 return[q for q in parts if d['roof']or q.get('studyLayer')!='roof']
