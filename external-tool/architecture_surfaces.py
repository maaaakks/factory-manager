"""Matching preview/export material and paint overrides; glass is independent."""
import re
CATEGORIES=['machines','logistics','power','floors','walls','frames','windows','roofs']
def group(part):
 a=part.get('asset','');c=part['component']
 return 'walls'if part.get('panelUnits')else'floors'if a.startswith('Foundation')else'power'if'PowerPole'in a else'windows'if c=='window'or'Window'in a else'roofs'if c=='roof'or a.startswith('Roof_')else'frames'if c=='beam'or a.startswith('Beam_')or c=='corner'else'walls'if c in['wall','gable']or a.startswith('Wall_')else'frames'
def material(asset,choice):
 m=re.fullmatch(r'Wall_(?:Concrete_|Orange_)?8x([124])(?:_01)?',asset)
 if not m or not choice or choice=='original':return asset
 return 'Wall_Concrete_8x'+m[1]if choice=='concrete'else'Wall_8x4_01'if m[1]=='4'else'Wall_Orange_8x'+m[1]
def apply(parts,design):return [dict(p,asset=material(p['asset'],design.get('wallMaterial')),color=design.get('colors',{}).get(group(p),p['color']))for p in parts]
