import http.client,json,sys,tempfile,threading,copy
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_blueprint as n,native_project as p,native_transport as t,server
from check_generic_lifts import scene

legacy=scene();legacy['links'][0]['kind']='planned'
legacy['flows']=dict(inputs=[dict(id='Desc_IronIngot_C',rate=120)],outputs=[dict(id='Desc_IronPlateReinforced_C',rate=10)])
legacy['objects'][0]['recipe']='Recipe_IronRod_C' # flows drive a new, reviewed implantation, not a mutation of this draft.
with tempfile.TemporaryDirectory(dir=n.ROOT/'data')as temporary,patch.object(n,'blueprint_root',side_effect=AssertionError('preview attempted game-folder access')):
 httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start()
 def request(path,body,authorized=True):
  conn=http.client.HTTPConnection('127.0.0.1',httpd.server_port,timeout=20);headers={'Content-Type':'application/json'}
  if authorized:headers['X-Factory-Tools']='local-viewer'
  conn.request('POST',path,json.dumps(body),headers);r=conn.getresponse();data=json.loads(r.read());conn.close();return r.status,data
 try:
  status,data=request('/api/blueprints/preview',dict(project=scene()));assert status==200 and data['verified']['lifts']==1
  assert request('/api/blueprints/preview',dict(project=scene()),False)[0]==403
  assert request('/api/blueprints/preview',dict(project=None))[0]==422
  original=copy.deepcopy(legacy);status,data=request('/api/workshop/repair',dict(project=legacy));assert status==200,data
  fixed=data['project'];assert legacy==original and fixed['id']==legacy['id'] and fixed['size']==32 and fixed['flows']==legacy['flows']
  assert not any(o['type']=='smelter' for o in fixed['objects']);assert data['verified']['belts']==43 and data['verified']['lifts']==17
  assert len(list(Path(temporary).iterdir()))==0
  saved=p.save(fixed,'SANDBOX',temporary);assert saved['verified']['lifts']==17
  assert request('/api/workshop/repair',dict(project=scene()))[0]==422
  print('PASS: generic preview HTTP, auth, no game access, ingot/reinforced repair in 4x4, exact flow/identity preservation and native file roundtrip in temporary directory')
 finally:httpd.shutdown();httpd.server_close()
