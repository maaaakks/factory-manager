"""Run with Python; optionally pass --save path/to/world.sav for read-only integration."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import adapter
import server


def check():
    assert adapter.category('Build_Wall_8x4_C') == 'wall'
    assert adapter.category('Build_ConveyorAttachmentWallHole_C') != 'wall'
    assert adapter.category('Build_Foundation_8x4_C') == 'foundation'
    original = adapter.CATALOG
    item = {'id': 'Copper', 'name': 'Cuivre', 'amount': 1, 'solid': True}
    adapter.CATALOG = {'recipes': {'Recipe_Test_C': {
        'inputs': [item], 'outputs': [item], 'seconds': 2,
        'producedIn': ['Smelter']}}, 'machines': {'Smelter': 1}}
    try:
        p = {'mCurrentRecipe': SimpleNamespace(pathName='Recipe_Test_C')}
        rate = adapter.rate_model('Smelter', p)
        assert rate['outputs'][0]['rate'] == 30 and rate['assumedClock']
        rate = adapter.rate_model('Smelter', {**p, 'mCurrentPotential': 2, 'mCurrentProductionBoost': 1.5})
        assert rate['inputs'][0]['rate'] == 60 and rate['outputs'][0]['rate'] == 90
        assert not adapter.rate_model('WrongMachine', p)['supported']
        adapter.CATALOG['recipes']['Recipe_Test_C']['inputs'] = [{**item, 'solid': False}]
        assert not adapter.rate_model('Smelter', p)['supported']
    finally:
        adapter.CATALOG = original

    original_file = server.FACTORY_FILE
    try:
        with tempfile.TemporaryDirectory() as temp:
            server.FACTORY_FILE = Path(temp) / 'factories.json'
            key = 'a' * 64
            payload = {'worldKey': key, 'factory': {'id': 'test', 'name': 'Cuivre',
                'members': ['machine-1'], 'rect': {'minX': 0, 'maxX': 10, 'minY': 0, 'maxY': 10},
                'source': 'automatic'}}
            server.store_factory(payload)
            payload['factory']['name'] = 'Cuivre renommé'
            payload['factory']['source'] = 'walls'
            server.store_factory(payload)
            db = server.factory_database()
            assert len(db['worlds'][key]) == 1
            assert db['worlds'][key][0]['name'] == 'Cuivre renommé'
            assert db['worlds'][key][0]['source'] == 'walls'
            for bad in ('../bad', None, ''):
                try:
                    server.store_factory({**payload, 'worldKey': bad})
                except ValueError:
                    pass
                else:
                    raise AssertionError('Invalid world accepted')
            assert 'b' * 64 not in db['worlds']
    finally:
        server.FACTORY_FILE = original_file
    print('PASS: architecture categories, theoretical rates, unsupported recipes, isolated persistence and rename')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--save', type=Path)
    args = ap.parse_args()
    check()
    if args.save:
        before = hashlib.sha256(args.save.read_bytes()).digest()
        world = adapter.extract(args.save)
        assert len({b['id'] for b in world['buildings']}) == len(world['buildings'])
        assert before == hashlib.sha256(args.save.read_bytes()).digest()
        print(json.dumps({'counts': world['counts'], 'quality': world['quality'],
                          'sourceUnchanged': True}, ensure_ascii=True))
