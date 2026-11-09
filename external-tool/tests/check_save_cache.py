from pathlib import Path
import sys,tempfile,json
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server,save_cache

def check():
 original=server.ROOT
 with tempfile.TemporaryDirectory() as temporary:
  root=Path(temporary);server.ROOT=root
  for relative in ['adapter.py','data/game_catalog.json','vendor/sat_sav_parse/sav_parse.py']:
   path=root/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('version-one')
  source=root/'test.sav';source.write_bytes(b'world-one')
  response={'buildings':[{'id':'one'}],'ports':[],'save':{'name':'old'}}
  with patch.object(server.subprocess,'run',return_value=SimpleNamespace(stdout=json.dumps(response),returncode=0)) as parse:
   first=server.parse_save(source,'test.sav');assert not first['cache']['hit'];assert parse.call_count==1
   second=server.parse_save(source,'renamed.sav');assert second['cache']['hit'] and second['save']['name']=='renamed.sav';assert parse.call_count==1
   source.write_bytes(b'world-two-longer');assert not server.parse_save(source,'test.sav')['cache']['hit'];assert parse.call_count==2
   (root/'adapter.py').write_text('version-two');assert not server.parse_save(source,'test.sav')['cache']['hit'];assert parse.call_count==3
   upload_a=root/'a.sav';upload_b=root/'b.sav';upload_a.write_bytes(b'uploaded');upload_b.write_bytes(b'uploaded')
   server.parse_save(upload_a,'a.sav','content-hash');assert server.parse_save(upload_b,'b.sav','content-hash')['cache']['hit'];assert parse.call_count==4
   key=save_cache.fingerprint(root,source);(root/'data/save-cache'/f'{key}.json.gz').write_bytes(b'corrupt')
   assert not server.parse_save(source,'test.sav')['cache']['hit'];assert parse.call_count==5
  for i in range(8):save_cache.write(root,f'{i:064x}',response)
  assert len(list((root/'data/save-cache').glob('*.json.gz')))==5
  assert source.read_bytes()==b'world-two-longer'
 server.ROOT=original
 print('PASS: disk cache hits, source/parser invalidation, upload content keys, corrupt cache recovery, eviction and untouched source')

if __name__=='__main__':check()
