import sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_blueprint as n
with tempfile.TemporaryDirectory(dir=n.ROOT/'data') as tmp:
 root=Path(tmp);r=n.save_test('SANDBOX',root);print(r)
 assert r['verified']['actors']==3 and r['inGameValidated'] is False
 assert all(Path(f['path']).is_file() for f in r['files'])
 for session in ['../outside','..','C:\\escape','unknown','SANDBOX/../jojo','SANDBOX.']:
  try:n.destination(session,root);raise AssertionError(session)
  except ValueError:pass
 p=n.build_test();p[3][1][0].append(['mWires',[n.sav_parse.ObjectReference('Persistent_Level','missing')]])
 try:n.verify(p);raise AssertionError('dangling reference accepted')
 except ValueError:pass
print('PASS: native .sbp/.sbpcfg reread, minimal actors, references, empty connections, directory containment, unsupported target rejection')

