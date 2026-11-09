import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import native_design as d,native_project as p,native_blueprint as n
proof=Path(sys.argv[2]);rows=json.loads(proof.read_text(encoding='utf8'))
for row in rows:assert d.envelope(row['project'])==row['parts']
for i in [0,12,24]:
 bp,info=p.build(rows[i]['project']);dest=proof.parent/f'cuivriere-{i}.sbp'
 n.sbp_parse.resaveBlueprint(str(dest),bp);parsed=n.sbp_parse.parseBlueprint(str(dest));p.verify(parsed)
 assert len(parsed[2])==len(rows[i]['parts'])
 assert info['belts']==info['lifts']==info['wires']==0
 assert info['architecture']['signPanels']==6
 assert all(h.scale==[1.,1.,1.]for h in parsed[2])
print('PASS: JS/Python parity for 25 formats; 3 native binary roundtrips; unit scales and no production networks')
