"""Extract a small local read-only catalogue from the user's installed game docs."""
import argparse, hashlib, json, re
from pathlib import Path

def read_json(path):
    raw=path.read_bytes()
    return json.loads(raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'))

def build(docs, build_id):
    source=docs/'en-US.json'; english=read_json(source)
    french=read_json(docs/'fr.json') if (docs/'fr.json').exists() else english
    classes={c['ClassName']:c for group in english for c in group['Classes']}
    names={c['ClassName']:c['mDisplayName'] for group in french for c in group['Classes'] if c.get('mDisplayName')}
    def entries(text):
        # ItemClass contains a full BlueprintGeneratedClass reference; keep its leaf ID.
        pairs=re.findall(r'ItemClass=.*?\.([A-Za-z0-9_]+)\x27\"\s*,Amount=([0-9.]+)',text)
        return [{'id':key,'name':names.get(key,key),'amount':float(amount),'solid':classes.get(key,{}).get('mForm')=='RF_SOLID'} for key,amount in pairs]
    recipes={}
    for key,c in classes.items():
        if not key.startswith('Recipe_') or not c.get('mProduct'):continue
        inputs,outputs=entries(c.get('mIngredients','')),entries(c.get('mProduct',''))
        if not outputs or (c.get('mIngredients') not in ('','()') and not inputs):continue
        recipes[key]={'name':names.get(key,c.get('mDisplayName',key)),'seconds':float(c.get('mManufactoringDuration',0)), 'inputs':inputs,'outputs':outputs,'producedIn':re.findall(r'\.([A-Za-z0-9_]+)\"',c.get('mProducedIn',''))}
    machines={key:float(c['mManufacturingSpeed']) for key,c in classes.items() if c.get('mManufacturingSpeed')}
    extractors={key:60*float(c['mItemsPerCycle'])/float(c['mExtractCycleTime']) for key,c in classes.items() if key.startswith('Build_MinerMk') and float(c.get('mExtractCycleTime',0))>0}
    return {'build':build_id,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'names':names,'recipes':recipes,'machines':machines,'extractors':extractors}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--docs',type=Path,required=True);ap.add_argument('--build',type=int,required=True);args=ap.parse_args()
    target=Path(__file__).parent/'data'/'game_catalog.json';target.parent.mkdir(exist_ok=True)
    result=build(args.docs,args.build);target.write_text(json.dumps(result,ensure_ascii=True),encoding='utf-8')
    print(f"Catalogue local : {len(result['recipes'])} recettes, build {args.build}.")
