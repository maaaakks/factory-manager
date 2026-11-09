"""Export an explicitly autonomous architectural study with no production actors."""
import json,copy
def build(project):
 import native_project as p,native_design as d,native_blueprint as n
 from native_assembly import Assembly
 from blueprint_dimensions import header_dimensions,dimensions,experimental
 if project.get('objects')!=[]or project.get('links')!=[]:raise p.ExportError(['Cette maquette autonome ne contient pas de production.'])
 family=project.get('design',{}).get('family');spec=d.CATALOG['studies'].get(family,{})
 if not spec.get('designFirst'):raise p.ExportError(['Étude autonome inconnue.'])
 # Reuse the ordinary schema validation without exporting a dummy actor.
 probe=copy.deepcopy(project);probe['objects']=[dict(id='schema-check',name='Validation',type='port',x=4,y=4,z=1,w=2,d=2,h=1,rotation=0,clock=1)];p.validate(probe)
 d.settings(project['design']);d.envelope(project)
 if any(f.get('profile')!='solid'or f.get('thickness')!=1 for f in project['floors']):raise p.ExportError(['Cette étude utilise des fondations natives de 1 m ; conservez le profil plein.'])
 assets=json.loads((n.ROOT/'data/native-assets.json').read_text(encoding='utf-8'));a=Assembly(p.load('native-connected-template.json'))
 for floor in project['floors']:
  for x,y in d.floor_cells(project,floor):d.add_floor(a,project,floor,x*8+4,y*8+4,assets)
 architecture=d.add(a,project,assets);bp=a.finish(p.load('native-test-template.json')['versions'],p.costs(a,assets));bp[1][0]=header_dimensions(project);p.verify(bp)
 signs=sum(q.get('emissiveSign',False)for q in d.envelope(project))
 return bp,dict(objects=0,architecture={**architecture,'signPanels':signs},foundations=sum(len(d.floor_cells(project,f))for f in project['floors']),frames=0,factoryFloors=0,belts=0,lifts=0,wires=0,size=project['size'],dimensions=dict(zip(['width','depth','height'],dimensions(project))),experimentalXL=experimental(project),powerMW=0,warnings=['Maquette architecturale autonome : salles et gaines réservées, sans machines ni convoyeurs.','Émission des signes, matériaux et parcours à confirmer dans Satisfactory.'],inGameValidated=False)
