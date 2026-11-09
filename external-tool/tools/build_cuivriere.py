"""Import the Copper architecture read-only, keeping native poses and finishes."""
from pathlib import Path
import json,math,sys,copy
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'data/cuivriere-source.json').read_text())
parts=[]
for r in rows:
 a=r['asset'];x,y,z=r['pos'];z+=6
 color='#794c3c' if 'Copper' in r['finish'] else '#777b6b' if a.startswith('Roof') else '#97aca8' if 'Window' in a or 'Glass' in a else '#747c75'
 if 'Caterium' in r['finish']:color='#a99b66'
 parts.append(dict(name=a,asset=a,component='module',sourceModule='C1',sourceIndex=0,nativeShell=True,nativeRecipe=r['recipePath'].rsplit('.',1)[-1],paintFinish=r['finish'],x=round(x,7),y=round(y,7),z=round(z,7),w=0,d=0,h=0,rotation=round(math.degrees(2*math.atan2(r['quat'][2],r['quat'][3])),7)%360,quat=r['quat'],color=color,studyLayer='roof' if a.startswith('Roof') or a=='FoundationGlass_01' else 'interior' if a.startswith(('Catwalk','Fence','Pillar','QuarterPipe')) else 'shell'))
# Warm luminous native sign panels frame the recessed 8 m entrance, on the saved wall at Y=80 m.
for x in [1.2,6.8]:
 for z in [10.,13.,16.]:
  parts.append(dict(name='Cuivrière · LED entrée',asset='StandaloneWidgetSign_Portrait',component='module',sourceModule='C1',sourceIndex=0,x=x,y=80.18,z=z,w=2,d=.14,h=3,rotation=180,quat=[0,0,math.sin(math.pi/4),math.cos(math.pi/4)],nativeSignQuaternion=[0,0,math.sin(math.pi/4),math.cos(math.pi/4)],color='#ffc778',studyLayer='shell',emissiveSign=True,emission=2))
catalog=json.loads((root/'data/architecture-styles.json').read_text(encoding='utf8'))
catalog['studies']['cuivriere']=dict(title='Cuivrière · halle de cuivre',displayName='Cuivrière',collection=4,category='Industriel',creationKind='exterior',designFirst=True,sourceArchitecture=True,dimensions=[104,88,32],resize={'width':{'min':104,'max':136,'step':8},'length':{'min':88,'max':120,'step':8}},repeatBay={'width':{'pivot':56,'from':48},'length':{'pivot':48,'from':40}},parts=parts,subtitle='Cuivre patiné / vitrages géométriques',summary='La halle Copper de kouyère : façades triangulaires, toiture plate et circulations conservées.',description='Architecture extraite du bâtiment Copper de kouyère_autosave_0. Le format original de 104 × 88 m conserve les pièces et leurs orientations, les vitrages, les circulations et les finitions métalliques. Les extensions ajoutent des travées centrales de 8 m, sans étirer les pièces. Machines et réseaux de production non inclus.',principles=[['La façade d’origine','Panneaux de cuivre et grands vitrages croisés, avec les motifs triangulaires de la sauvegarde.'],['Des pièces conservées','Les orientations et dimensions natives restent celles du bâtiment Copper.'],['Des travées extensibles','Largeur de 104 à 136 m et longueur de 88 à 120 m, par pas de 8 m.'],['Une enveloppe disponible','Planchers, passerelles et escaliers conservés ; production à implanter dans l’atelier.']],reference='Source locale : kouyère_autosave_0.sav, bâtiment Copper. Extraction architecturale sans modification de la sauvegarde.',source={'save':'kouyère_autosave_0.sav','factory':'Copper','pieceCount':len(rows),'addedLED':6,'origin':[-2676,-596,-6]},cutawayLayers=['roof'])
family=copy.deepcopy(catalog['families']['lumen']);family.update(name='Cuivrière · halle de cuivre',nativeStudy='cuivriere',description=catalog['studies']['cuivriere']['summary'],style='ficsit')
catalog['families']['cuivriere']=family
catalog['version']=max(catalog['version'],13)
(root/'data/architecture-styles.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Imported',len(parts),'native architecture pieces')

assets=json.loads((root/'data/native-assets.json').read_text(encoding='utf8'))
for r in rows:
 assets.setdefault('Build_'+r['asset']+'_C',{'path':r['typePath']})
 assert r['recipePath'].rsplit('.',1)[-1] in assets,r['recipePath']
(root/'data/native-assets.json').write_text(json.dumps(assets,ensure_ascii=False),encoding='utf8')
