from pathlib import Path
import sys
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import adapter

node='Persistent_Level:PersistentLevel.BP_ResourceNode511'
reference=adapter.RESOURCE_PURITY[node]
p={'mExtractableResource':SimpleNamespace(pathName=node),'mCurrentPotential':1.5}
model=adapter.extraction_model('Build_MinerMk2_C',p,{},reference[2])
assert model['purity']==1 and model['puritySource']=='world-reference'
assert model['normalRate']==120 and model['clock']==1.5
model=adapter.extraction_model('Build_MinerMk2_C',p,{node:{'mPurityOverride':['EResourcePurity','RP_Pure']}},reference[2])
assert model['purity']==2 and model['puritySource']=='saved-override'
assert adapter.extraction_model('Build_MinerMk2_C',p,{},[1e8,1e8,1e8])['purity'] is None
assert adapter.extraction_model('Build_MinerMk2_C',{}, {},[0,0,0])['purity'] is None
assert adapter.extraction_model('Build_ConstructorMk1_C',p) is None
assert adapter.extraction_model('Build_MinerMk2_C',p,{node:{'mPurityOverride':['EResourcePurity','RP_Unknown']}},reference[2])['purity'] is None
print('PASS: spatially matched node purity, saved override priority, unknown nodes and extraction cadence')
