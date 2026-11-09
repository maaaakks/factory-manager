"""Local parsed-save cache. Fingerprints include source changes and parser version."""
from pathlib import Path
import gzip, hashlib, json, os

FORMAT = 'parsed-world-v3'

def parser_version(root):
    root = Path(root)
    digest = hashlib.sha256(FORMAT.encode())
    for relative in ['adapter.py', 'data/game_catalog.json', 'vendor/sat_sav_parse/sav_parse.py']:
        source = root / relative
        digest.update(source.read_bytes())
    return digest.hexdigest()

def fingerprint(root, path, content_key=None):
    path = Path(path)
    digest = hashlib.sha256(parser_version(root).encode())
    if content_key:
        digest.update(content_key.encode())
    else:
        stat = path.stat()
        digest.update(str(path.resolve()).encode())
        digest.update(f'{stat.st_size}:{stat.st_mtime_ns}'.encode())
    return digest.hexdigest()

def read(root, key):
    path = Path(root) / 'data' / 'save-cache' / (key + '.json.gz')
    try:
        with gzip.open(path, 'rt', encoding='utf-8') as stream:
            value = json.load(stream)
        if not isinstance(value.get('buildings'), list) or not isinstance(value.get('ports'), list):
            return None
        os.utime(path, None)
        value['cache'] = {'hit': True, 'version': FORMAT}
        return value
    except (OSError, ValueError, EOFError, TypeError, AttributeError):
        return None

def write(root, key, data):
    directory = Path(root) / 'data' / 'save-cache'
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (key + '.json.gz')
    temporary = directory / (key + '.tmp')
    try:
        with gzip.open(temporary, 'wt', encoding='utf-8', compresslevel=1) as stream:
            json.dump(data, stream, ensure_ascii=False, separators=(',', ':'))
        temporary.replace(path)
        # Bound disk use to five snapshots and 150 MB; game saves are never touched.
        size = 0
        for index, entry in enumerate(sorted(directory.glob('*.json.gz'), key=lambda p:p.stat().st_mtime, reverse=True)):
            size += entry.stat().st_size
            if index >= 5 or size > 150 * 1024 * 1024:
                entry.unlink(missing_ok=True)
    finally:
        temporary.unlink(missing_ok=True)
