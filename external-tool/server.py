"""Loopback-only factory planner. World saves are read-only; isolated native test exports are explicit."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs
import argparse
import hashlib
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import threading
import webbrowser
import re
import math
import time
import save_cache
import native_blueprint

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'dist'
MAX_UPLOAD = 64 * 1024 * 1024
PARSE_LOCK = threading.Lock()
FACTORY_LOCK = threading.Lock()
FACTORY_FILE = ROOT/'data'/'factories.json'


def factory_database():
    if not FACTORY_FILE.exists():return {'schemaVersion':1,'worlds':{}}
    data=json.loads(FACTORY_FILE.read_text(encoding='utf-8'))
    if data.get('schemaVersion')!=1:raise ValueError('Version du fichier de périmètres non prise en charge.')
    return data


def validate_world(key):
    if not isinstance(key,str) or not re.fullmatch(r'[a-f0-9]{64}',key):raise ValueError('Identité de sauvegarde invalide.')
    return key


def store_factory(payload):
    key=validate_world(payload.get('worldKey'))
    record=payload.get('factory',{})
    identifier=record.get('id');name=record.get('name');members=record.get('members');rect=record.get('rect',{})
    if not isinstance(identifier,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',identifier):raise ValueError('Identifiant de périmètre invalide.')
    if not isinstance(name,str) or not name.strip() or len(name)>80:raise ValueError('Donnez un nom de 1 à 80 caractères.')
    if not isinstance(members,list) or not 1<=len(members)<=30000 or any(not isinstance(m,str) or len(m)>1024 for m in members):raise ValueError('Liste de bâtiments invalide.')
    if any(not isinstance(rect.get(k),(int,float)) or not math.isfinite(rect[k]) for k in ('minX','maxX','minY','maxY')) or rect['minX']>=rect['maxX'] or rect['minY']>=rect['maxY']:raise ValueError('Rectangle invalide.')
    clean={'id':identifier,'name':name.strip(),'members':list(dict.fromkeys(members)),'rect':{k:rect[k] for k in ('minX','maxX','minY','maxY')},'source':record.get('source') if record.get('source') in ('manual','automatic','density','walls') else 'manual','updatedAt':int(time.time())}
    with FACTORY_LOCK:
        db=factory_database();records=db['worlds'].setdefault(key,[])
        records[:]=[r for r in records if r['id']!=identifier]
        if len(records)>=200:raise ValueError('Limite de 200 usines pour cette partie.')
        records.append(clean)
        FACTORY_FILE.parent.mkdir(exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix='factories-',suffix='.tmp',dir=FACTORY_FILE.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as handle:json.dump(db,handle,ensure_ascii=True);handle.flush();os.fsync(handle.fileno())
            os.replace(tmp,FACTORY_FILE)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    return {'factory':clean}


def list_saves():
    base = Path(os.environ.get('LOCALAPPDATA', '')) / 'FactoryGame' / 'Saved' / 'SaveGames'
    files = list(base.glob('*/*.sav')) if base.is_dir() else []
    files += list(base.glob('*.sav')) if base.is_dir() else []
    # Steam dedicated-server metadata also uses .sav; it is not a world save.
    files = [p for p in files if p.name.lower() != 'servermanager_v2.sav']
    return {hashlib.sha256(str(p).encode()).hexdigest()[:20]: p for p in sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)}


def parse_save(path, label, content_key=None):
    key = save_cache.fingerprint(ROOT,path,content_key)
    cached = save_cache.read(ROOT,key)
    if cached is not None:
        cached["save"]["name"] = label
        return cached
    completed = subprocess.run([sys.executable, str(ROOT / 'adapter.py'), str(path)], capture_output=True, text=True, encoding='utf-8', timeout=120, cwd=ROOT)
    try:
        data = json.loads(completed.stdout)
    except (ValueError, TypeError):
        raise ValueError('Le parseur ne peut pas lire ce fichier. Format incompatible ou fichier incomplet.')
    if completed.returncode or 'error' in data:
        raise ValueError(data.get('error', 'Échec de lecture.'))
    data['save']['name'] = label
    data['cache'] = {'hit':False,'version':save_cache.FORMAT}
    try:save_cache.write(ROOT,key,data)
    except OSError:pass
    return data


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(130)

    def reply(self, code, content, mime='application/json; charset=utf-8'):
        if isinstance(content, (dict, list)):
            content = json.dumps(content, ensure_ascii=True).encode()
        elif isinstance(content, str):
            content = content.encode()
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(content)

    def valid_host(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

    def do_GET(self):
        if not self.valid_host():
            return self.reply(403, {'error': 'Hôte refusé.'})
        path = urlparse(self.path).path
        if path == '/api/blueprints':
            try:return self.reply(200,native_blueprint.info())
            except (OSError,ValueError,KeyError) as exc:return self.reply(422,{'error':str(exc)[:300]})
        if path == '/api/saves':
            analysis_version = save_cache.parser_version(ROOT)
            return self.reply(200, [{'id': key, 'name': p.name, 'size': p.stat().st_size, 'stamp':str(p.stat().st_size)+':'+str(p.stat().st_mtime_ns), 'analysis':analysis_version} for key, p in list_saves().items()])
        if path == '/api/factories':
            try:
                key=validate_world(parse_qs(urlparse(self.path).query).get('worldKey',[''])[0])
                with FACTORY_LOCK:data=factory_database()['worlds'].get(key,[])
                return self.reply(200,{'factories':data})
            except (ValueError,OSError) as exc:return self.reply(422,{'error':str(exc)})
        routes = {'/i18n.js':'i18n.js','/locales/en.json':'locales/en.json','/calculateur': 'calculator.html', '/calculator.js': 'calculator.js', '/calculator.css': 'calculator.css', '/navigation.js': 'navigation.js', '/navigation.css': 'navigation.css', '/workshop-patterns.js':'workshop-patterns.js','/workshop-assist.js': 'workshop-assist.js', '/planner-data.json': 'planner-data.json', '/': 'index.html', '/atelier': 'workshop.html', '/design': 'workshop.html', '/workshop-design.js':'workshop-design.js', '/preview-picking.js':'preview-picking.js','/preview-gpu.js':'preview-gpu.js', '/transport-geometry.js':'transport-geometry.js', '/flow-core.js':'flow-core.js','/workshop-network.js':'workshop-network.js', '/resource-icons.svg':'resource-icons.svg', '/workshop.css': 'workshop.css', '/workshop.js': 'workshop.js', '/workshop-model.js': 'workshop-model.js', '/explorer-cache.js':'explorer-cache.js', '/app.js': 'app.js', '/factory-metrics.js': 'factory-metrics.js', '/factory-preview.js': 'factory-preview.js', '/style.css': 'style.css', '/assets/world-map.jpg': 'assets/world-map.jpg'}
        routes.update({'/m05-facade-library.js':'m05-facade-library.js','/m05-facade.js':'m05-facade.js','/m05-roof.js':'m05-roof.js','/m05-roof-forms.js':'m05-roof-forms.js'})
        routes.update({'/design-campus.js':'design-campus.js'})
        routes.update({'/signature-design.js':'signature-design.js','/creation-fitting.js':'creation-fitting.js','/creation-living.js':'creation-living.js'})
        routes.update({'/architecture-surfaces.js':'architecture-surfaces.js','/m05-kit.js':'m05-kit.js'})
        routes.update({'/patterns.html':'patterns.html','/patterns.js':'patterns.js','/patterns.css':'patterns.css','/compact-patterns.json':'compact-patterns.json','/architecture-catalog.js':'architecture-catalog.js','/workshop-intents.js':'workshop-intents.js','/workshop-planning.js':'workshop-planning.js','/workshop-planner-worker.js':'workshop-planner-worker.js','/m05-library.js':'m05-library.js','/m05-modules.js':'m05-modules.js'})
        routes.update({'/atlas':'atlas.html','/atlas.css':'atlas.css','/atlas.js':'atlas.js','/atlas-example.json':'atlas-example.json','/atlas-scene.json':'atlas-scene.json'})
        routes.update({'/creations':'creations.html','/creations.css':'creations.css','/creations.js':'creations.js','/creation':'atlas.html'})
        if path not in routes:
            return self.reply(404, {'error': 'Introuvable.'})
        file = PUBLIC / routes[path]
        self.reply(200, file.read_bytes(), (mimetypes.guess_type(file.name)[0] or 'application/octet-stream') + '; charset=utf-8')

    def do_POST(self):
        origin = self.headers.get('Origin')
        allowed = (f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}')
        if not self.valid_host() or (origin and origin not in allowed) or self.headers.get('X-Factory-Tools') != 'local-viewer':
            return self.reply(403, {'error': 'Requête locale requise.'})
        path = urlparse(self.path).path
        if path == '/api/workshop/manifold':
            import native_manifold,native_project
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=16384:return self.reply(413,{'error':'Objectifs trop volumineux.'})
                payload=json.loads(self.rfile.read(size));project=native_manifold.proposal(payload);_,verified=native_project.build(project)
                return self.reply(200,{'project':project,'verified':verified})
            except (ValueError,OSError,TypeError,AttributeError,KeyError)as exc:return self.reply(422,{'error':'Pattern de production impossible : '+str(exc)[:350]})
        if path == '/api/workshop/compact':
            import native_compact
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=8192:return self.reply(413,{'error':'Objectifs trop volumineux.'})
                payload=json.loads(self.rfile.read(size))
                inputs=payload.get('inputs',[]);outputs=payload.get('outputs',[])
                if len(inputs)!=1 or len(outputs)!=1 or inputs[0].get('id') not in ['Desc_OreIron_C','Desc_IronIngot_C'] or outputs[0].get('id')!='Desc_IronPlateReinforced_C':raise ValueError('Modules disponibles : fer vers plaques renforcées.')
                rate=outputs[0].get('rate')
                if not isinstance(rate,(int,float)) or isinstance(rate,bool) or not .2<=rate<=10 or abs(inputs[0].get('rate',0)-12*rate)>1e-6:raise ValueError('Débits incompatibles avec les modules : 12 minerais par plaque renforcée, maximum 10/min.')
                options={**(payload.get('options') or {}),'outputRate':rate,'inputItem':inputs[0]['id']}
                project=native_compact.proposal(options);_,verified=native_compact.build_project(project)
                return self.reply(200,{'project':project,'verified':verified})
            except (ValueError,OSError,TypeError,AttributeError,KeyError) as exc:return self.reply(422,{'error':'Module compact impossible : '+str(exc)[:300]})
        if path == '/api/workshop/repair':
            import native_transport,native_project
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=1024*1024:return self.reply(413,{'error':'Projet trop volumineux.'})
                payload=json.loads(self.rfile.read(size))
                project,verified=native_transport.repair(payload.get('project'))
                return self.reply(200,{'project':project,'verified':verified})
            except native_project.ExportError as exc:return self.reply(422,{'error':str(exc),'issues':exc.issues,'repairAvailable':native_transport.can_repair(payload.get('project'))})
            except (ValueError,OSError,TypeError,AttributeError,KeyError) as exc:return self.reply(422,{'error':'Conversion impossible : '+str(exc)[:300]})
        if path == '/api/blueprints/preview':
            import native_project,native_transport
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=1024*1024:return self.reply(413,{'error':'Projet trop volumineux.'})
                payload=json.loads(self.rfile.read(size))
                _,verified=native_project.build(payload.get('project'))
                return self.reply(200,{'verified':verified})
            except native_project.ExportError as exc:return self.reply(422,{'error':str(exc),'issues':exc.issues,'repairAvailable':native_transport.can_repair(payload.get('project'))})
            except (ValueError,OSError,TypeError,AttributeError,KeyError,native_project.n.sav_parse.ParseError) as exc:return self.reply(422,{'error':'Préparation impossible : '+str(exc)[:300]})
        if path == '/api/blueprints/project':
            import native_project,native_transport
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=1024*1024:return self.reply(413,{'error':'Projet trop volumineux (1 Mo maximum).'})
                payload=json.loads(self.rfile.read(size))
                if not isinstance(payload,dict):return self.reply(422,{'error':'Projet invalide.'})
                return self.reply(200,native_project.save(payload.get('project'),payload.get('session')))
            except native_project.ExportError as exc:return self.reply(422,{'error':str(exc),'issues':exc.issues,'repairAvailable':native_transport.can_repair(payload.get('project'))})
            except (ValueError,OSError,TypeError,AttributeError,KeyError,native_project.n.sav_parse.ParseError) as exc:return self.reply(422,{'error':'Export impossible : '+str(exc)[:300]})
        if path == '/api/blueprints/test':
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=4096:return self.reply(413,{'error':'Requête trop volumineuse.'})
                payload=json.loads(self.rfile.read(size))
                return self.reply(200,native_blueprint.save_test(payload.get('session'),module=payload.get('module','smelter')))
            except (ValueError,OSError,TypeError,AttributeError,KeyError) as exc:return self.reply(422,{'error':str(exc)[:300]})
        if path == '/api/factories':
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=4*1024*1024:return self.reply(413,{'error':'Périmètre trop volumineux.'})
                return self.reply(200,store_factory(json.loads(self.rfile.read(size))))
            except (ValueError,OSError,TypeError,AttributeError) as exc:return self.reply(422,{'error':str(exc)[:300]})
        if path not in ('/api/load', '/api/upload'):
            return self.reply(404, {'error': 'Introuvable.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size <= 0 or size > MAX_UPLOAD or (path == '/api/load' and size > 4096):
                return self.reply(413, {'error': 'Fichier vide ou trop volumineux (maximum 64 Mo).'} )
            if not PARSE_LOCK.acquire(blocking=False):
                return self.reply(409, {'error': 'Une lecture est déjà en cours.'})
            try:
                body = self.rfile.read(size)
                if len(body) != size:
                    raise ValueError('Transfert incomplet.')
                if path == '/api/load':
                    key = json.loads(body).get('id')
                    source = list_saves().get(key)
                    if source is None:
                        raise ValueError('Sauvegarde introuvable. Actualise la liste.')
                    data = parse_save(source, source.name)
                else:
                    label = unquote(self.headers.get('X-File-Name', 'import.sav')).replace('\\', '/').rsplit('/', 1)[-1][:160]
                    if not label.lower().endswith('.sav'):
                        raise ValueError('Choisis un fichier .sav.')
                    with tempfile.TemporaryDirectory(prefix='factory-tools-') as tmp:
                        source = Path(tmp) / 'upload.sav'
                        source.write_bytes(body)
                        data = parse_save(source, label, hashlib.sha256(body).hexdigest())
                self.reply(200, data)
            finally:
                PARSE_LOCK.release()
        except subprocess.TimeoutExpired:
            self.reply(422, {'error': 'Lecture interrompue après 120 s. Essaie une sauvegarde plus petite.'})
        except (ValueError, OSError) as exc:
            self.reply(422, {'error': str(exc)[:400]})


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--port', type=int, default=8765)
    args.add_argument('--open', action='store_true')
    config = args.parse_args()
    try:
        server = ThreadingHTTPServer(('127.0.0.1', config.port), Handler)
    except OSError:
        sys.exit('Port occupé. Ferme l’ancienne fenêtre ou utilise --port 8766.')
    server.daemon_threads = True
    server.timeout = 120
    print(f'Factory Manager : http://127.0.0.1:{config.port} — Ctrl+C pour arrêter.', flush=True)
    if config.open:
        webbrowser.open(f'http://127.0.0.1:{config.port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
