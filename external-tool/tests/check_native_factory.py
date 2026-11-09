import copy,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_blueprint as n
from native_factory import build,verify,prop,aset,q

with tempfile.TemporaryDirectory(dir=n.ROOT/'data') as tmp:
    receipt=n.save_test('SANDBOX',tmp,module='reinforced')
    assert receipt['verified']['inputPerMinute']==120 and receipt['verified']['outputPerMinute']==10
    assert receipt['verified']['powerMW']==78
    assert receipt['verified']['footprintMeters']==[32,32]
    assert receipt['inGameValidated'] is False
    for f in receipt['files']:assert Path(f['path']).is_file()
    first=n.sbp_parse.parseBlueprint(receipt['files'][0]['path'])
    assert verify(first)['floors']==[1,10.5,20]
    print('Native binary roundtrip:',receipt['verified'])

def find(bp,text):return next((h,o) for h,o in zip(bp[2],bp[3]) if isinstance(h,n.sav_parse.ActorHeader) and text+'.' in h.typePath)
def rejects(mutate,reason):
    b=copy.deepcopy(first);mutate(b)
    try:verify(b)
    except (ValueError,KeyError):return
    raise AssertionError('Accepted invalid '+reason)
rejects(lambda b:setattr(find(b,'Build_ConstructorMk1')[0],'position',[900,-1000,700]),'floor height')
rejects(lambda b:setattr(find(b,'Build_AssemblerMk1')[0],'position',[1500,0,2000]),'footprint')
rejects(lambda b:setattr(find(b,'Build_ConveyorLiftMk2')[0],'rotation',q(90)),'lift direction')
rejects(lambda b:prop(find(b,'Build_FoundationPassthrough_Lift')[1],'mBottomSnappedConnection').__setattr__('pathName','missing'),'floor hole')
rejects(lambda b:prop(find(b,'Build_ConveyorBeltMk2')[1],'mSplineData')[0][0][0][1].__setitem__(0,100),'detached belt endpoint')
rejects(lambda b:prop(find(b,'Build_AssemblerMk1')[1],'mCurrentRecipe').__setattr__('pathName','wrong.Recipe_Rotor_C'),'recipe')
rejects(lambda b:dict(prop(find(b,'Build_AssemblerMk1')[1],'mCustomizationData')[0])['OverrideColorData'][0][0][1].__setitem__(0,1),'black appearance')

# Recompute item balances using the installed game's catalog, independently of labels.
catalog=json.loads((n.ROOT/'data'/'game_catalog.json').read_text(encoding='utf-8'))
net={};machines=0
for h,o in zip(first[2],first[3]):
    if not isinstance(h,n.sav_parse.ActorHeader):continue
    r=prop(o,'mCurrentRecipe')
    if not r:continue
    recipe=catalog['recipes'][r.pathName.rsplit('.',1)[-1]];machines+=1
    for direction,sign in [('inputs',-1),('outputs',1)]:
        for item in recipe[direction]:net[item['id']]=net.get(item['id'],0)+sign*item['amount']*60/recipe['seconds']
assert machines==14
assert {k:round(v,6) for k,v in net.items() if abs(v)>1e-6}=={'Desc_OreIron_C':-120.,'Desc_IronPlateReinforced_C':10.}
print('PASS: recipe balance 120 ore -> 10 reinforced/min; native graph, belt endpoints and directions, real floor holes, no machine/floor overlap, 32m cube, black customization, bounded power poles, deliberate corruption rejection')
