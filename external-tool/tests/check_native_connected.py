from pathlib import Path
import sys,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_blueprint as n
with tempfile.TemporaryDirectory(dir=n.ROOT/'data') as tmp:
 result=n.save_test('SANDBOX',tmp,module='plates');print(result['name'],result['verified']['actors'], 'actors,',result['verified']['components'],'components')
 assert result['verified']=={'actors':14,'components':19,'designer':4,'recipe':'Minerai de fer → lingots → plaques de fer','inputRate':30,'rate':20,'powerMW':8,'belts':1,'wires':2,'foundations':8}
print('PASS: connected native chain, recipes, belt endpoint geometry, reciprocal connections, power topology and binary roundtrip')


import copy
from native_connected import build,verify,prop
bp=build();bad=copy.deepcopy(bp)
belt=next((h,o) for h,o in zip(bad[2],bad[3]) if isinstance(h,n.sav_parse.ActorHeader) and 'ConveyorBeltMk1.' in h.typePath)
prop(belt[1],'mSplineData')[1][0][0][1][1]+=100
try:verify(bad);raise AssertionError('detached belt geometry accepted')
except ValueError as e:assert 'convoyeur' in str(e)
bad=copy.deepcopy(bp);wire=next((h,o) for h,o in zip(bad[2],bad[3]) if isinstance(h,n.sav_parse.ActorHeader) and 'PowerLine.' in h.typePath)
for entry in prop(wire[1],'mWireInstances')[0][0]:
 if entry[0]=='CachedRelativeLocations':entry[1][2]+=100;break
try:verify(bad);raise AssertionError('detached wire geometry accepted')
except ValueError as e:assert 'borne' in str(e)
bad=copy.deepcopy(bp);c=next((h,o) for h,o in zip(bad[2],bad[3]) if isinstance(h,n.sav_parse.ComponentHeader) and h.instanceName.endswith('.Input0') and 'Constructor' in h.instanceName)
c[1][0]=[];c[1][1]=[]
try:verify(bad);raise AssertionError('non reciprocal belt accepted')
except ValueError as e:assert 'réciproque' in str(e)
try:n.save_test('SANDBOX',module='../bad');raise AssertionError('arbitrary module accepted')
except ValueError:pass
print('PASS: detached belt, incorrect cable endpoints, broken reciprocal connections and unknown modules rejected')
