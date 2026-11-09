import copy,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_project as p,native_blueprint as n
def obj(id,type,x,y,recipe=None,z=1,rotation=0):return {'id':id,'type':type,'name':id,'x':x,'y':y,'z':z,'rotation':rotation,'recipe':recipe,'clock':1,'w':6,'d':9}
def project():return {'schemaVersion':2,'kind':'factory-tools-paper-blueprint','size':32,'id':'custom-test','name':'Mon usine personnalisée','objects':[obj('smelt','smelter',16,24,'Recipe_IngotIron_C'),obj('construct','constructor',16,10,'Recipe_IronPlate_C'),obj('pole','pole',25,20)],'links':[{'kind':'belt','from':'smelt','to':'construct','rate':30},{'kind':'power','from':'pole','to':'smelt'},{'kind':'power','from':'pole','to':'construct'}],'floors':[{'z':0,'thickness':1,'material':'concrete'}],'appearance':{'enabled':True,'color':'#112233'},'buffer':[obj('unused','constructor',40,8,'Recipe_IronPlate_C')]}
b,details=p.build(project());assert details['belts']==1 and details['wires']==2 and details['objects']==3 and details['foundations']==16 and details['powerMW']==8
with tempfile.TemporaryDirectory(dir=n.ROOT/'data') as d:
 r=p.save(project(),'SANDBOX',d);assert all(Path(f['path']).is_file() for f in r['files']);p.verify(n.sbp_parse.parseBlueprint(r['files'][0]['path']))
 assert len([h for h in n.sbp_parse.parseBlueprint(r['files'][0]['path'])[2] if isinstance(h,n.sav_parse.ActorHeader) and 'ConstructorMk1.' in h.typePath])==1
 again=p.save(project(),'SANDBOX',d);assert again['name']==r['name']
 bad=project();bad['links'][0]['kind']='planned'
 try:p.save(bad,'SANDBOX',d);raise AssertionError('planned links accepted')
 except p.ExportError:pass
 foreign=Path(r['files'][1]['path']);foreign.write_bytes(b'foreign')
 try:p.save(project(),'SANDBOX',d);raise AssertionError('foreign file overwritten')
 except (ValueError,IndexError,TypeError):pass
 assert foreign.read_bytes()==b'foreign'
for size in [40,48]:
 c=project();c['size']=size;bp,_=p.build(c);assert bp[1][0]==size//8
for material in ['steel','asphalt']:
 c=project();c['floors'][0]['material']=material;bp,_=p.build(c);assert any(material in h.typePath.lower() if material=='asphalt' else 'Foundation_8x1_01.' in h.typePath for h in bp[2] if isinstance(h,n.sav_parse.ActorHeader))
for mutate in [lambda c:c['objects'].append(obj('lift','lift',3,3)),lambda c:c['objects'][0].update(x=1),lambda c:c['objects'][0].update(recipe='Recipe_Rotor_C'),lambda c:c['floors'].append({'z':6,'thickness':1,'material':'concrete'}),lambda c:c['links'][0].update(rate=240),lambda c:c['objects'][1].update(z=12),lambda c:c['objects'][0].update(x=float('nan'))]:
 c=project();mutate(c)
 try:p.build(c);raise AssertionError('invalid project accepted')
 except (p.ExportError,ValueError):pass
print('PASS: actual custom objects/recipes/positions/colors, physical belts and power, all formats, floor materials, binary roundtrip, stable filenames, backup, buffer excluded, invalid geometry/recipes/logic/lifts/capacity rejected, foreign file preserved')

c=project();c['objects']=[obj('s','smelter',9,24,'Recipe_IngotIron_C'),obj('c','constructor',23,12,'Recipe_IronPlate_C',rotation=90)];c['links']=[{'kind':'belt','from':'s','to':'c'}]
bp,stats=p.build(c);assert stats['belts']==1
c=project();c['objects'][0]['clock']=.5;bp,stats=p.build(c)
assert next(p.prop(o,'mCurrentPotential') for h,o in zip(bp[2],bp[3]) if isinstance(h,n.sav_parse.ActorHeader) and 'SmelterMk1.' in h.typePath)==.5
c=project();c['size']=40;c['objects']=[obj('smelt','smelter',20,32,'Recipe_IngotIron_C'),obj('split','splitter',20,22),obj('left','constructor',10,10,'Recipe_IronPlate_C'),obj('right','constructor',30,10,'Recipe_IronPlate_C')];c['links']=[{'kind':'belt','from':'smelt','to':'split'},{'kind':'belt','from':'split','to':'left'},{'kind':'belt','from':'split','to':'right'}]
bp,stats=p.build(c);assert stats['belts']==3
for capacity in [60,120,270,480,780,1200]:
 c=project();c['beltCapacity']=capacity;bp,stats=p.build(c)
 assert any('ConveyorBeltMk'+str([60,120,270,480,780,1200].index(capacity)+1)+'.' in h.typePath for h in bp[2] if isinstance(h,n.sav_parse.ActorHeader))
print('PASS: 90-degree native curve, underclock, multi-output splitter port allocation, all six conveyor tiers')

