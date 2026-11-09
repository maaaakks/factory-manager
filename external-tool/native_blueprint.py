"""Small native .sbp test exporter, using the bundled GPL-3.0 GreyHak parser.

This intentionally exports a fixed isolated test module, not arbitrary workshop plans.
"""
from pathlib import Path
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
import threading
import time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'/'sat_sav_parse'))
import sav_parse
import sbp_parse

NAME='FT_TEST_01_Fonderie'
LOCK=threading.Lock()
DESCRIPTION='Factory Tools - TEST 01 : 2 fondations de 1 m et 1 fonderie. Lingots de fer, 100 %. Brancher le courant manuellement. Aucun convoyeur.'


def blueprint_root():
    return Path(os.environ['LOCALAPPDATA'])/'FactoryGame'/'Saved'/'SaveGames'/'blueprints'


def destination(session,base=None):
    root=(Path(base) if base is not None else blueprint_root()).resolve()
    if not isinstance(session,str) or not re.fullmatch(r'[^<>:"/\\|?*\x00-\x1f]{1,80}',session) or session in ('.','..') or session!=session.strip() or session.endswith('.'):
        raise ValueError('Nom de session invalide.')
    path=(root/session).resolve()
    if path.parent!=root:raise ValueError('Destination hors du dossier des blueprints.')
    if not path.is_dir() and session!='SANDBOX':raise ValueError('Session introuvable : choisissez un dossier existant ou SANDBOX.')
    return path


def info(base=None):
    root=Path(base) if base is not None else blueprint_root()
    sessions=sorted([p.name for p in root.iterdir() if p.is_dir() and p.resolve().parent==root.resolve()]) if root.exists() else []
    if 'SANDBOX' not in sessions:sessions.append('SANDBOX')
    return {'sessions':sessions,'defaultSession':'SANDBOX','root':str(root),'name':NAME,'module':'2 fondations de 1 m + 1 fonderie · lingots de fer · 100 %','defaultModule':'reinforced','modules':[{'id':'reinforced','name':'FT_TEST_04_PlaquesRenforcees','label':'04 · Plaques renforcées · 4×4','description':'120 minerais de fer/min → 10 plaques renforcées/min vers un coffre · 78 MW. Emprise 4×4, trois étages espacés de 9,5 m, sols béton, machines noires, six traversées de sol et convoyeurs Mk.2.'},{'id':'smelter','name':NAME,'label':'01 · Fonderie seule','description':'2 fondations + 1 fonderie, sans câble ni convoyeur.'},{'id':'plates','name':'FT_TEST_02_PlaquesFer','label':'02 · Chaîne de plaques de fer','description':'8 fondations + fonderie → convoyeur Mk.1 → constructeur, poteau et 2 câbles. 30 minerai/min → 20 plaques/min · 8 MW.'},{'id':'vertical','name':'FT_TEST_03_PlaquesEtages','label':'03 · Plaques sur deux étages','description':'Fonderie en bas, constructeur en haut, élévateur Mk.1 de 12 m en gaine ouverte, 12 fondations, 2 poteaux et 3 câbles. 30 minerai/min → 20 plaques/min · 8 MW.'}]}


def decode(value):
    if isinstance(value,list):return [decode(v) for v in value]
    if isinstance(value,dict):
        if '__type__' in value:
            classes={'ActorHeader':sav_parse.ActorHeader,'ComponentHeader':sav_parse.ComponentHeader,'ObjectReference':sav_parse.ObjectReference}
            obj=classes[value['__type__']]()
            for k,v in value.items():
                if k!='__type__':setattr(obj,k,decode(v))
            return obj
        return {k:decode(v) for k,v in value.items()}
    return value


def references(value):
    if isinstance(value,sav_parse.ObjectReference):yield value
    elif isinstance(value,(list,tuple)):
        for item in value:yield from references(item)


def build_test():
    template=decode(json.loads((ROOT/'data'/'native-test-template.json').read_text(encoding='utf-8')))
    headers=copy.deepcopy(template['machine']['headers']);objects=copy.deepcopy(template['machine']['objects'])
    original=headers[0].instanceName
    # Local actor/component IDs are fresh on each export, preserving class conventions.
    serial=int.from_bytes(os.urandom(4),'little')
    new='Persistent_Level:PersistentLevel.Build_SmelterMk1_C_'+str(serial)
    for header in headers:
        header.instanceName=header.instanceName.replace(original,new)
        if isinstance(header,sav_parse.ComponentHeader):header.parentActorName=new
    for ref in references(objects):ref.pathName=ref.pathName.replace(original,new)
    headers[0].position=[0.0,0.0,100.0];headers[0].rotation=[0.0,0.0,0.0,1.0]
    for idx,y in enumerate([-400.0,400.0]):
        header=copy.deepcopy(template['foundation']['header']);obj=copy.deepcopy(template['foundation']['object'])
        header.instanceName='Persistent_Level:PersistentLevel.Build_Foundation_8x1_01_C_'+str((serial+idx+1)%2**32)
        header.position=[0.0,y,50.0];header.rotation=[0.0,0.0,0.0,1.0]
        headers.append(header);objects.append(obj)
    recipes=[]
    for header,obj in zip(headers,objects):
        if isinstance(header,sav_parse.ActorHeader):
            recipe=next(value for key,value in obj[2] if key=='mBuiltWithRecipe')
            if recipe.pathName not in [r.pathName for r in recipes]:recipes.append(copy.deepcopy(recipe))
    result=[template['versions'],[4,template['ingredients'],recipes],headers,objects]
    verify(result)
    return result


def verify(blueprint,module="smelter"):
    if module=="reinforced":
        import native_factory
        return native_factory.verify(blueprint)
    if module=="vertical":
        import native_vertical
        return native_vertical.verify(blueprint)
    if module=="plates":
        import native_connected
        return native_connected.verify(blueprint)
    if isinstance(blueprint,str):raise ValueError('Blueprint illisible : '+blueprint)
    versions,summary,headers,objects=blueprint
    if len(headers)!=len(objects) or summary[0]!=4:raise ValueError('Structure du blueprint invalide.')
    actors=[h for h in headers if isinstance(h,sav_parse.ActorHeader)]
    if len(actors)!=3 or sum('Build_SmelterMk1.' in h.typePath for h in actors)!=1 or sum('Build_Foundation_8x1_01.' in h.typePath for h in actors)!=2:raise ValueError('Le module doit contenir deux fondations et une fonderie.')
    names={h.instanceName for h in headers}
    if len(names)!=len(headers):raise ValueError('Identifiants natifs dupliqués.')
    for h in headers:
        if isinstance(h,sav_parse.ComponentHeader) and h.parentActorName not in names:raise ValueError('Composant orphelin.')
    for ref in references(objects):
        if ref.levelName=='Persistent_Level' and ref.pathName not in names and ref.pathName!='Persistent_Level:PersistentLevel.BuildableSubsystem':raise ValueError('Référence externe inattendue : '+ref.pathName)
    for h,obj in zip(headers,objects):
        if isinstance(h,sav_parse.ActorHeader):
            for ref in obj[1]:
                if ref.pathName not in names:raise ValueError('Composant natif manquant.')
        elif h.className.endswith('FGPowerConnectionComponent'):
            for key,value in obj[0]:
                if key=='mWires' and value:raise ValueError('Le module de test doit être déconnecté.')
    return {'actors':len(actors),'components':len(headers)-len(actors),'designer':4,'recipe':'Lingot de fer','rate':30,'powerMW':4}


def save_test(session,base=None,module='smelter'):
    if module not in ('smelter','plates','vertical','reinforced'):raise ValueError('Module natif inconnu.')
    if module=='reinforced':
        import native_factory
        name,description,builder=native_factory.NAME,native_factory.DESCRIPTION,native_factory.build
    elif module=='vertical':
        import native_vertical
        name,description=native_vertical.NAME,native_vertical.DESCRIPTION
        builder=native_vertical.build
    elif module=='plates':
        import native_connected
        name,description= native_connected.NAME,native_connected.DESCRIPTION
        builder=native_connected.build
    else:name,description,builder=NAME,DESCRIPTION,build_test
    target=destination(session,base)
    with LOCK:
        target.mkdir(parents=True,exist_ok=True)
        bp=builder()
        with tempfile.TemporaryDirectory(prefix='factory-tools-native-',dir=ROOT/'data') as tmp:
            tmp=Path(tmp);sbp=tmp/(name+'.sbp');cfg=tmp/(name+'.sbpcfg')
            sbp_parse.resaveBlueprint(str(sbp),bp)
            checked=sbp_parse.parseBlueprint(str(sbp));details=verify(checked,module)
            config=(4,description,4,[0.107023,0.434154,0.558341,1.0],'None','None',[],None,None)
            sbp_parse.resaveBlueprintConfig(str(cfg),config)
            if sbp_parse.parseBlueprintConfig(str(cfg))[1]!=description:raise ValueError('Configuration native illisible.')
            files=[];backups=[]
            # Back up the old test pair before replacing our own fixed test files.
            for source in (sbp,cfg):
                dest=target/source.name
                if dest.is_symlink():raise ValueError('Lien symbolique refusé pour le fichier de test.')
                if dest.exists():
                    backup_dir=ROOT/'data'/'native-backups';backup_dir.mkdir(parents=True,exist_ok=True)
                    backup=backup_dir/(str(time.time_ns())+'-'+dest.name);backup.write_bytes(dest.read_bytes());backups.append(str(backup))
            for source in (sbp,cfg):
                dest=target/source.name
                fd,temp=tempfile.mkstemp(prefix='ft-native-',suffix='.tmp',dir=target)
                try:
                    with os.fdopen(fd,'wb') as out:out.write(source.read_bytes());out.flush();os.fsync(out.fileno())
                    os.replace(temp,dest)
                finally:
                    if os.path.exists(temp):os.unlink(temp)
                files.append({'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
        return {'name':name,'module':module,'session':session,'directory':str(target),'files':files,'backups':backups,'verified':details,'inGameValidated':False}

