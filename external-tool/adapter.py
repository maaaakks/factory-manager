"""Read-only saved-world adapter. Original code: MIT; uses GreyHak's GPL-3.0 parser."""
from pathlib import Path
import collections
import contextlib
import io
import json
import math
import re
import sys
import hashlib

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor' / 'sat_sav_parse'))
import sav_parse as parser
from sav_data.resourcePurity import RESOURCE_PURITY

parser.PROGRESS_BAR_ENABLE_DECOMPRESS = False
parser.PROGRESS_BAR_ENABLE_PARSE = False

try:
    CATALOG = json.loads((ROOT/'data'/'game_catalog.json').read_text(encoding='utf-8'))
except (OSError, ValueError):
    CATALOG = {'names':{}, 'recipes':{}, 'machines':{}, 'build':None}


def rate_model(type_name, p):
    key=ref(p.get('mCurrentRecipe')).rsplit('.',1)[-1]
    recipe=CATALOG['recipes'].get(key)
    if not recipe:return None
    reason=None
    if type_name not in recipe['producedIn']:reason='Machine non validée pour cette recette'
    speed=CATALOG['machines'].get(type_name)
    if not speed or recipe['seconds']<=0:reason='Durée ou vitesse de fabrication inconnue'
    if not all(item['solid'] for item in recipe['inputs']+recipe['outputs']):reason='Recette avec fluide non prise en charge'
    clock=p.get('mCurrentPotential',1.0);boost=p.get('mCurrentProductionBoost',1.0)
    if not isinstance(clock,(int,float)) or not math.isfinite(clock) or clock<=0:reason='Cadence inconnue'
    if not isinstance(boost,(int,float)) or not math.isfinite(boost) or boost<=0:reason='Multiplicateur de production inconnu'
    result={'recipeId':key,'inputs':recipe['inputs'],'outputs':recipe['outputs'],'supported':reason is None,'reason':reason,'assumedClock':'mCurrentPotential' not in p,'assumedBoost':'mCurrentProductionBoost' not in p}
    if reason is None:
        cycles=60/recipe['seconds']*speed*clock
        result['inputs']=[{**item,'rate':item['amount']*cycles} for item in recipe['inputs']]
        result['outputs']=[{**item,'rate':item['amount']*cycles*boost} for item in recipe['outputs']]
    return result


def props(obj):
    return dict(getattr(obj, 'properties', []))


def ref(value):
    return getattr(value, 'pathName', '')


def recipe_label(path):
    # UI labels only. No recipe quantities/rates are inferred from these names.
    labels = {
        'Recipe_Biofuel_C': 'Biocarburant',
        'Recipe_Biomass_Leaves_C': 'Biomasse (feuilles)',
        'Recipe_Biomass_Wood_C': 'Biomasse (bois)',
        'Recipe_Concrete_C': 'Béton',
        'Recipe_CopperSheet_C': 'Tôles de cuivre',
        'Recipe_Wire_C': 'Fil électrique',
        'Recipe_Cable_C': 'Câble',
        'Recipe_Screw_C': 'Vis',
        'Recipe_IngotCopper_C': 'Lingot de cuivre',
        'Recipe_IngotIron_C': 'Lingot de fer',
        'Recipe_IronPlate_C': 'Plaque de fer',
        'Recipe_IronRod_C': 'Tige de fer',
        'Recipe_IronPlateReinforced_C': 'Plaque de fer renforcée',
    }
    key = path.rsplit('.', 1)[-1]
    if key in labels:
        return labels[key]
    return parser.pathNameToReadableName(path).split(' (/')[0].removeprefix('Recipe, ')


def category(type_name):
    if 'ConveyorBelt' in type_name or 'ConveyorLift' in type_name:
        return 'conveyor'
    if any(x in type_name for x in ('ConveyorAttachmentSplitter', 'ConveyorAttachmentMerger')):
        return 'junction'
    if 'StorageContainer' in type_name or 'IndustrialTank' in type_name:
        return 'storage'
    # Functional wall/floor attachments are not architectural walls/foundations.
    if not any(x in type_name for x in ('Conveyor', 'Pipeline', 'Pipe', 'Power', 'Railroad', 'HyperTube')):
        if any(x in type_name for x in ('Sign', 'Light', 'Floodlight', 'Fence', 'Railing', 'Ladder', 'RoadBarrier', 'Statue')):
            return 'decoration'
        if any(x in type_name for x in ('Wall', 'Window', 'Door')):
            return 'wall'
        if 'Roof' in type_name:
            return 'roof'
        if any(x in type_name for x in ('Foundation', 'Ramp')):
            return 'foundation'
        if 'Roof' in type_name:
            return 'roof'
        if any(x in type_name for x in ('Sign', 'Light', 'Fence', 'Railing', 'Ladder', 'RoadBarrier', 'Statue', 'Frame')):
            return 'decoration'
    if any(x in type_name for x in ('Constructor', 'Assembler', 'Manufacturer', 'Smelter', 'Foundry', 'Refinery', 'Blender', 'Miner', 'Generator', 'Packager', 'Accelerator', 'Converter', 'OilPump', 'WaterPump')):
        return 'machine'
    if any(x in type_name for x in ('Beam', 'Pillar', 'Walkway', 'Stair', 'Catwalk')):
        return 'structure'
    return 'other'


def world_point(local, h):
    # Quaternion rotation: v' = v + 2*w*(q.xyz cross v) + 2*(q.xyz cross(q.xyz cross v)).
    v = [float(local[i]) * h.scale[i] for i in range(3)]
    x, y, z, w = h.rotation
    uv = [y*v[2]-z*v[1], z*v[0]-x*v[2], x*v[1]-y*v[0]]
    uuv = [y*uv[2]-z*uv[1], z*uv[0]-x*uv[2], x*uv[1]-y*uv[0]]
    return [(h.position[i] + v[i] + 2*(w*uv[i] + uuv[i])) / 100 for i in range(3)]


def geometry(h, p):
    spline = p.get('mSplineData')
    if spline:
        points = [dict(entry[0]) for entry in spline]
        result = []
        for a, b in zip(points, points[1:]):
            if not all(k in a and k in b for k in ('Location', 'ArriveTangent', 'LeaveTangent')):
                continue
            for i in range(13):
                t = i/12
                h00, h10, h01, h11 = 2*t**3-3*t*t+1, t**3-2*t*t+t, -2*t**3+3*t*t, t**3-t*t
                v = [h00*a['Location'][j]+h10*a['LeaveTangent'][j]+h01*b['Location'][j]+h11*b['ArriveTangent'][j] for j in range(3)]
                result.append(world_point(v, h))
        if result:
            return result, 'saved-spline'
    top = p.get('mTopTransform')
    if top:
        trans = dict(top[0]).get('Translation')
        if trans:
            return [world_point([0, 0, 0], h), world_point(trans, h)], 'saved-lift-endpoints'
    return [], 'origin-only'


def extraction_model(type_name, p, node_properties=None, position=None):
    if not type_name.startswith('Build_MinerMk'):
        return None
    node = ref(p.get('mExtractableResource')) or None
    defaults = RESOURCE_PURITY.get(node)
    override = (node_properties or {}).get(node, {}).get('mPurityOverride')
    purity = None
    source = None
    if isinstance(override, (list, tuple)) and len(override) > 1:
        purity = {'RP_Impure': .5, 'RP_Normal': 1, 'RP_Pure': 2}.get(override[1])
        source = 'saved-override' if purity is not None else None
    elif defaults and position is not None and math.dist(position, defaults[2]) < 3000:
        purity = {'IMPURE': .5, 'NORMAL': 1, 'PURE': 2}.get(defaults[1].name)
        source = 'world-reference' if purity is not None else None
    return {'resourceNode': node, 'normalRate': CATALOG.get('extractors', {}).get(type_name),
            'clock': p.get('mCurrentPotential', 1.0), 'assumedClock': 'mCurrentPotential' not in p,
            'purity': purity, 'puritySource': source,
            'resource': (ref((node_properties or {}).get(node, {}).get('mResourceClassOverride')) or '').rsplit('.', 1)[-1] or (defaults[0] if defaults else None)}


def extract(filename):
    with contextlib.redirect_stdout(io.StringIO()):
        save = parser.readFullSaveFile(str(filename))
    pairs = [(h, o) for level in save.levels for h, o in zip(level.actorAndComponentObjectHeaders, level.objects)]
    node_properties = {h.instanceName: props(o) for h, o in pairs if isinstance(h, parser.ActorHeader) and 'ResourceNode' in h.typePath}
    buildings = {}
    for h, o in pairs:
        if not isinstance(h, parser.ActorHeader) or '/Build_' not in h.typePath:
            continue
        p = props(o)
        type_name = h.typePath.rsplit('.', 1)[-1]
        cat = category(type_name)
        points, geom_source = geometry(h, p)
        qx, qy, qz, qw = h.rotation
        yaw = math.atan2(2*(qw*qz+qx*qy), 1-2*(qy*qy+qz*qz))
        buildings[h.instanceName] = {
            'id': h.instanceName, 'name': CATALOG.get('names',{}).get(type_name,CATALOG.get('names',{}).get(type_name.replace('Build_','Recipe_',1),parser.pathNameToReadableName(h.typePath))),
            'type': type_name, 'category': cat, 'position': [v/100 for v in h.position],
            'yaw': yaw, 'rotation':list(h.rotation), 'scale':list(h.scale), 'points': points, 'geometrySource': geom_source,
            'recipe': recipe_label(ref(p['mCurrentRecipe'])) if ref(p.get('mCurrentRecipe')) else None,
            'savedClock': p.get('mCurrentPotential'), 'ports': [],
            'rateModel': rate_model(type_name,p), 'recordSource':'actor',
            'extraction': extraction_model(type_name, p, node_properties, h.position),
            'passThrough': bool(re.fullmatch(r'Build_Conveyor(?:Belt|Lift)Mk\d+_C', type_name) or type_name in ('Build_ConveyorAttachmentSplitter_C', 'Build_ConveyorAttachmentMerger_C')),
        }
    # Architectural pieces are mostly packed instances, with no ordinary actor header.
    lightweight_count=0
    occurrences=collections.Counter()
    for h,o in pairs:
        if not isinstance(h,parser.ActorHeader) or h.typePath!='/Script/FactoryGame.FGLightweightBuildableSubsystem':continue
        for type_path, instances in o.actorSpecificInfo[1:]:
            type_name=type_path.rsplit('.',1)[-1]
            for instance in instances:
                rotation,position=instance[:2]
                fingerprint=json.dumps([type_path,position,rotation],separators=(',',':'))
                digest=hashlib.sha256(fingerprint.encode()).hexdigest()[:32]
                occurrence=occurrences[digest];occurrences[digest]+=1
                identifier=f'lightweight:{digest}:{occurrence}'
                qx,qy,qz,qw=rotation
                buildings[identifier]={'id':identifier,'name':CATALOG['names'].get(type_name,parser.pathNameToReadableName(type_path)),'type':type_name,'category':category(type_name),'position':[v/100 for v in position],'yaw':math.atan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz)),'rotation':list(rotation),'scale':[1,1,1],'points':[],'geometrySource':'lightweight-transform','recipe':None,'savedClock':None,'ports':[],'passThrough':False,'recordSource':'lightweight','rateModel':None}
                lightweight_count+=1
    ports = {}
    for h, o in pairs:
        if not isinstance(h, parser.ComponentHeader) or h.className != '/Script/FactoryGame.FGFactoryConnectionComponent' or h.parentActorName not in buildings:
            continue
        name = h.instanceName.rsplit('.', 1)[-1]
        # Explicit naming rules only; ConveyorAny0/1 do not imply a direction.
        direction = 'in' if re.fullmatch(r'Input\d*', name) else 'out' if re.fullmatch(r'Output\d*', name) else None
        ports[h.instanceName] = {'id': h.instanceName, 'owner': h.parentActorName, 'name': name, 'peer': ref(props(o).get('mConnectedComponent')) or None, 'direction': direction, 'directionSource': 'component-name' if direction else None}
        buildings[h.parentActorName]['ports'].append(h.instanceName)

    # Direction constraints: a physical link flips direction, as does a two-port belt.
    adjacency = collections.defaultdict(set)
    for pid, port in ports.items():
        peer = ports.get(port['peer'])
        if peer and peer['peer'] == pid:
            adjacency[pid].add(peer['id'])
            adjacency[peer['id']].add(pid)
    for b in buildings.values():
        if b['category'] == 'conveyor' and b['passThrough'] and len(b['ports']) == 2:
            a, c = b['ports']
            adjacency[a].add(c)
            adjacency[c].add(a)
    visited = set()
    conflicts = 0
    for seed in ports:
        if seed in visited:
            continue
        parity, queue, inconsistent = {seed: 0}, collections.deque([seed]), False
        while queue:
            a = queue.popleft()
            for b in adjacency[a]:
                expected = 1-parity[a]
                if b in parity and parity[b] != expected:
                    inconsistent = True
                elif b not in parity:
                    parity[b] = expected
                    queue.append(b)
        visited.update(parity)
        anchors = {(0 if ports[p]['direction'] == 'in' else 1) ^ bit for p, bit in parity.items() if ports[p]['direction']}
        inconsistent = inconsistent or len(anchors) > 1
        if inconsistent:
            conflicts += 1
            for p in parity:
                ports[p]['direction'] = None
                ports[p]['directionSource'] = 'conflict'
        elif anchors:
            base = next(iter(anchors))
            for p, bit in parity.items():
                if not ports[p]['direction']:
                    ports[p]['direction'] = 'in' if (base ^ bit) == 0 else 'out'
                    ports[p]['directionSource'] = 'connection-inference'
    for port in ports.values():
        peer = ports.get(port['peer'])
        port['peerOwner'] = peer['owner'] if peer else None
        port['state'] = 'open' if port['peer'] is None else 'connected' if peer and peer['peer'] == port['id'] else 'unresolved'
    info = save.saveFileInfo
    return {
        'schemaVersion': 2,
        'worldKey':hashlib.sha256(json.dumps([info.mapName,info.sessionName,getattr(info,'saveIdentifier','')]).encode()).hexdigest(),
        'catalogBuild':CATALOG['build'],
        'save': {'name': Path(filename).name, 'session': info.sessionName, 'saveVersion': info.saveVersion, 'build': info.buildVersion, 'savedAt': info.saveDatetime.isoformat(), 'playSeconds': info.playDurationInSeconds, 'modded': bool(info.isModdedSave)},
        'buildings': list(buildings.values()), 'ports': list(ports.values()),
        'counts': dict(collections.Counter(b['category'] for b in buildings.values())),
        'quality': {'unresolvedPorts': sum(p['state']=='unresolved' for p in ports.values()), 'unknownDirections': sum(p['direction'] is None for p in ports.values()), 'directionConflicts': conflicts,'lightweightBuildings':lightweight_count},
    }


if __name__ == '__main__':
    try:
        result = extract(sys.argv[1])
        print(json.dumps(result, ensure_ascii=True, allow_nan=False, separators=(',', ':')))
    except Exception as exc:
        print(json.dumps({'error': f'{type(exc).__name__}: {exc}'}))
        sys.exit(1)

