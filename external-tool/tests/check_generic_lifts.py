from pathlib import Path
import copy,sys,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_project as p,native_blueprint as n,native_transport as t

def scene(down=False,capacity=120):
 objects=[dict(id='smelt',name='Fonderie',type='smelter',x=16,y=24,z=13 if down else 1,w=6,d=9,h=8.5,rotation=0,recipe='Recipe_IngotIron_C',clock=1),dict(id='construct',name='Constructeur',type='constructor',x=16,y=10,z=1 if down else 13,w=8,d=10,h=6,rotation=0,recipe='Recipe_IronPlate_C',clock=1),dict(id='shaft',name='Elévateur',type='lift',x=5,y=16,z=1,h=14,w=1,d=1,rotation=0)]
 return dict(schemaVersion=2,kind='factory-tools-paper-blueprint',id='generic-lift',name='Generic lift',size=32,objects=objects,links=[dict(kind='belt',**{'from':'smelt','to':'construct'},via='shaft',item='Desc_IronIngot_C',rate=30,capacity=capacity)],floors=[dict(z=0,thickness=1,material='concrete'),dict(z=12,thickness=1,material='concrete')])

if __name__=='__main__':
 for down in [False,True]:
  v=scene(down);original=copy.deepcopy(v);bp,stats=p.build(v);assert v==original
  assert stats['lifts']==1 and stats['belts']==2
  assert sum('ConveyorLift' in h.typePath for h in bp[2] if isinstance(h,n.sav_parse.ActorHeader))==1
  p.verify(bp)
  with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'data')as temp:
   out=Path(temp)/'lift.sbp';n.sbp_parse.resaveBlueprint(str(out),bp);p.verify(n.sbp_parse.parseBlueprint(str(out)))
 print('PASS: generic native lift ascent/descent, two physical belts, reciprocal ports, floor holes, roundtrip and source non-mutation')
 for capacity in [60,120,270,480,780,1200]:
  bp,stats=p.build(scene(capacity=capacity));tier=[60,120,270,480,780,1200].index(capacity)+1
  assert any(f'ConveyorLiftMk{tier}.' in h.typePath for h in bp[2] if isinstance(h,n.sav_parse.ActorHeader))
  assert stats['liftHoles'][1]['holes'] and not stats['liftHoles'][0]['holes']
  assert all(l['physicalRoute'] for l in stats['transportPreview']['links'])
 legacy=scene();legacy['links'][0]['kind']='planned';assert p.build(legacy)[1]['lifts']==1
 explicit=scene();explicit['links']=[dict(kind='belt',**{'from':'smelt','to':'shaft'},item='Desc_IronIngot_C',rate=30),dict(kind='belt',**{'from':'shaft','to':'construct'},item='Desc_IronIngot_C',rate=30)]
 assert p.build(explicit)[1]['lifts']==1
 ports=scene();ports['objects'] += [dict(id='entry',type='port',name='Entrée',x=16,y=31,z=1,rotation=0,io=dict(side='input',item='Desc_OreIron_C',rate=30)),dict(id='exit',type='port',name='Sortie',x=16,y=2,z=13,rotation=0,io=dict(side='output',item='Desc_IronPlate_C',rate=20))]
 ports['links'] += [dict(kind='belt',**{'from':'entry','to':'smelt'},rate=30),dict(kind='belt',**{'from':'construct','to':'exit'},rate=20)]
 bp,stats=p.build(ports);assert stats['belts']==4;p.verify(bp)
 frame=scene();frame['floors'][1]['profile']='frame';assert p.build(frame)[1]['frames']>0
 bad=scene();bad['links']=[]
 try:p.build(bad);raise AssertionError('orphan lift accepted')
 except p.ExportError:pass
 bad=scene();bad['links'][0]['rate']=121
 try:p.build(bad);raise AssertionError('insufficient rank accepted')
 except p.ExportError:pass
 boxes={'source':([-250,600,100],[250,1400,600]),'target':([-250,-1400,100],[250,-600,600]),'obstacle':([-1600,-100,100],[1600,100,600])}
 belts,risers=t.bridge([0,900,200],[0,-900,200],[0,-1,0],[0,-1,0],boxes,'source','target',3200,{},dict(size=32,floors=[dict(z=0)]))
 assert len(belts)==3 and len(risers)==2
 assert all(not(-1600<pt[0]<1600 and -100<pt[1]<100 and 100<pt[2]<600)for span in belts for pt in p.samples(span))
 print('PASS: ranks 1–6, planned and explicit lifts, free input/output belt ends, open frames, orphan/capacity rejection and overhead obstacle avoidance')
