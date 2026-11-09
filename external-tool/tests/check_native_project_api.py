import http.client,json,sys,tempfile,threading
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_blueprint as n,server
from check_native_project import project

with tempfile.TemporaryDirectory(dir=n.ROOT/'data') as tmp,patch.object(n,'blueprint_root',return_value=Path(tmp)):
 httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
 thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start()
 def request(body,header=True):
  conn=http.client.HTTPConnection('127.0.0.1',httpd.server_port,timeout=15);headers={'Content-Type':'application/json'}
  if header:headers['X-Factory-Tools']='local-viewer'
  conn.request('POST','/api/blueprints/project',json.dumps(body),headers);res=conn.getresponse();data=json.loads(res.read());conn.close();return res.status,data
 try:
  status,data=request({'session':'SANDBOX','project':project()});assert status==200,data
  assert all(Path(f['path']).parent==Path(tmp)/'SANDBOX' for f in data['files'])
  b=project();b['links'][0]['kind']='planned';status,data=request({'session':'SANDBOX','project':b});assert status==422 and data['issues']
  assert request({'session':'SANDBOX','project':project()},False)[0]==403
  assert request({'session':'../escape','project':project()})[0]==422
  assert request({'project':None})[0]==422
  print('PASS: real HTTP project endpoint, request header, structured validation errors, session containment; all writes isolated to temporary directory')
 finally:httpd.shutdown();httpd.server_close();thread.join(timeout=2)
