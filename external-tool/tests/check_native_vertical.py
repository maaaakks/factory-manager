import copy,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_blueprint as n
from native_vertical import build,verify
from native_connected import prop
with tempfile.TemporaryDirectory(dir=n.ROOT/'data') as tmp:
 result=n.save_test('SANDBOX',tmp,module='vertical')
 assert result['verified']=={'actors':22,'components':24,'designer':4,'inputRate':30,'rate':20,'powerMW':8,'belts':2,'lifts':1,'liftHeightM':12,'floors':2,'foundations':12,'poles':2,'wires':3,'shaft':'open-edge'}
 print(result['name'],'native roundtrip:',result['verified']['actors'],'actors')
bp=build();bad=copy.deepcopy(bp)
lift=next((h,o) for h,o in zip(bad[2],bad[3]) if isinstance(h,n.sav_parse.ActorHeader) and 'ConveyorLiftMk1.' in h.typePath)
for item in prop(lift[1],'mTopTransform')[0]:
 if item[0]=='Translation':item[1][2]-=100
try:verify(bad);raise AssertionError('Wrong lift height accepted')
except ValueError as e:assert 'Hauteur' in str(e)
bad=copy.deepcopy(bp);floor=next(h for h in bad[2] if isinstance(h,n.sav_parse.ActorHeader) and 'Foundation' in h.typePath and h.position[2]>1000);floor.position=[0,1200,1250]
try:verify(bad);raise AssertionError('Shaft blocked by slab accepted')
except ValueError as e:assert 'gaine' in str(e)
bad=copy.deepcopy(bp);machine=next(h for h in bad[2] if isinstance(h,n.sav_parse.ActorHeader) and 'ConstructorMk1.' in h.typePath);machine.rotation=[0,0,0,1]
try:verify(bad);raise AssertionError('Wrong constructor orientation accepted')
except ValueError as e:assert 'Orientation' in str(e)
bad=copy.deepcopy(bp);lift=next(h for h in bad[2] if isinstance(h,n.sav_parse.ActorHeader) and 'ConveyorLiftMk1.' in h.typePath);lift.rotation=[0,0,0,1]
try:verify(bad);raise AssertionError('Wrong lift orientation accepted')
except ValueError as e:assert 'Orientation' in str(e)
assert n.info(Path('.'))['defaultModule'] in ('vertical','reinforced')
print('PASS: two native floors, lift height and direction, reciprocal conveyor flow, electrical network, open shaft and geometric failure cases')
