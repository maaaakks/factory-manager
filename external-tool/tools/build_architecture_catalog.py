"""Regenerate the browser catalog from the shared architectural source of truth."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
catalog=json.loads((root/'data/architecture-styles.json').read_text(encoding='utf-8'))
for key,family in catalog['families'].items():
 assert family['group']in catalog['groups'],key
 assert family['style']in ['concrete','ficsit','glass'],key
 assert family['structure']in ['none','grid','columns'],key
 assert family['patterns']and set(family['patterns'])<=set(['classic','paired','ribbon','alternating','upper','full']),key
 assert family['layouts']and set(family['layouts'])<=set(['auto','central','pair','quartet','triple','band','ring']),key
 assert family['palettes']and all(p in catalog['palettes']for p in family['palettes']),key
 assert family['entryTreatments']and set(family['entryTreatments'])<=set(['frame','porch','double']),key
code="'use strict';\n// Generated from data/architecture-styles.json.\n(function(root){const catalog="+json.dumps(catalog,ensure_ascii=False)+";if(typeof module!=='undefined'&&module.exports)module.exports=catalog;else root.ArchitectureCatalog=catalog;})(typeof globalThis!=='undefined'?globalThis:this);\n"
(root/'dist/architecture-catalog.js').write_text(code,encoding='utf-8')
print(f"Built {len(catalog['families'])} architectural families in {len(catalog['groups'])} categories.")
