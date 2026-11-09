"""Build the offline English pack from UI strings and official game names."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build(docs=None):
 game=ROOT/'data/locales/game-en.json'
 if docs:
  sys.path.insert(0,str(ROOT))
  from build_catalog import read_json
  english={c['ClassName']:c.get('mDisplayName')for group in read_json(docs/'en-US.json')for c in group['Classes']}
  names=json.loads((ROOT/'data/game_catalog.json').read_text(encoding='utf8'))['names']
  pairs={fr:english[key]for key,fr in names.items()if fr and english.get(key)and fr!=english[key]}
  game.write_text(json.dumps(pairs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 pairs=json.loads(game.read_text(encoding='utf8'))
 for line in (ROOT/'data/locales/ui-en.tsv').read_text(encoding='utf8').splitlines():
  if not line or line.startswith('#'):continue
  fr,en=line.split('\t',1)
  if not fr.strip()or not en.strip():raise ValueError('Empty translation')
  pairs[fr]=en
 (ROOT/'dist/locales').mkdir(exist_ok=True)
 (ROOT/'dist/locales/en.json').write_text(json.dumps(pairs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(f'Built {len(pairs)} translation entries.')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--docs',type=Path);args=parser.parse_args();build(args.docs)
