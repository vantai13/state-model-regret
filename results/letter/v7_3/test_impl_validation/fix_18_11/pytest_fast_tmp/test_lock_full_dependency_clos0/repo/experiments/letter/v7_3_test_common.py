"""Doan Van Tai — V7-3 file integrity and exclusive, atomic output helpers.

No traffic matrices are parsed and no simulator is called on import or locking.
The archive's canonical fingerprint hashes opaque member bytes only.
"""
import ast
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tarfile
import uuid

ROOT = Path(__file__).resolve().parents[2]
BASE = Path('results/letter/v7_3')
PARAMS = BASE / 'card_v7_3_params.json'
BRIEF = Path('notes/ops/codex/V7_3_test_brief.md')
OUT = ROOT / BASE / 'test_congested'
ARCHIVE = 'directed-geant-uhlig-15min-over-4months-ALL-native.tgz'


def read_json(path):
    return json.loads(Path(path).read_text())


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def atomic_write(path, writer):
    """Publish only a finished file; link() refuses to replace any existing file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('.' + path.name + '.' + uuid.uuid4().hex)
    try:
        writer(temporary)
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path, value):
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    atomic_write(path, lambda p: p.write_text(payload))


def data_root():
    return Path(os.environ.get('SMR_SNDLIB', '~/papers/data/sndlib')).expanduser()


def source_paths(root=ROOT):
    """AST closure of repository imports, including package __init__ sources."""
    pending = [Path('experiments/letter') / (name + '.py') for name in
               ('v7_3_test', 'v7_3_score', 'v7_3_rescore', 'v7_3_cong')]
    found = set()
    while pending:
        rel = pending.pop()
        if rel in found or not (root / rel).is_file():
            continue
        found.add(rel)
        for parent in rel.parents:
            init = parent / '__init__.py'
            if (root / init).is_file() and init not in found:
                pending.append(init)
        tree = ast.parse((root / rel).read_text())
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.Import):
                modules = [x.name for x in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.level:
                    package = list(rel.with_suffix('').parts[:-node.level])
                    base = '.'.join(package + node.module.split('.'))
                else:
                    base = node.module
                modules = [base] + [base + '.' + x.name for x in node.names]
            for module in modules:
                path = Path(*module.split('.'))
                for candidate in (path.with_suffix('.py'), path / '__init__.py'):
                    if (root / candidate).is_file() and candidate not in found:
                        pending.append(candidate)
    return sorted(found)


def input_paths(root=ROOT, sndlib=None):
    sndlib = data_root() if sndlib is None else Path(sndlib)
    params = read_json(root / PARAMS)
    train = Path(params['training_dir'])
    paths = {str(p): root / p for p in source_paths(root)}
    for p in (Path(params['card']), PARAMS, BRIEF, BASE / 'data_manifest.json',
              train / 'configuration.json', train / 'configuration.npz',
              train / 'protocol.json', train / 'summary.json',
              Path('experiments/letter/v7_3_test_gcp.sh')):
        paths[str(p)] = root / p
    paths.update({'sndlib:archive': sndlib / ARCHIVE,
                  'sndlib:topology': sndlib / 'sndlib-networks-native/geant.txt',
                  'sndlib:train_cache': sndlib / 'v7_3_train.npz'})
    return paths


def canonical_members(archive):
    hashes = []
    with tarfile.open(archive) as tar:
        for member in tar:
            if member.isfile() and member.name.endswith('.txt'):
                with tar.extractfile(member) as f:
                    hashes.append((member.name, hashlib.sha256(f.read()).hexdigest()))
    return hashlib.sha256(''.join(f'{n}\t{h}\n' for n, h in sorted(hashes)).encode()).hexdigest()


def fingerprint(root=ROOT, sndlib=None):
    paths = input_paths(root, sndlib)
    hashes = {name: sha256(path) for name, path in sorted(paths.items())}
    manifest = read_json(root / BASE / 'data_manifest.json')
    for logical, field in (('sndlib:archive', 'sha256'),
                           ('sndlib:topology', 'topology_sha256'),
                           ('sndlib:train_cache', 'train_cache_sha256')):
        if hashes[logical] != manifest[field]:
            raise ValueError('manifest fingerprint mismatch: ' + logical)
    canonical = canonical_members(paths['sndlib:archive'])
    if canonical != manifest['canonical_member_sha256']:
        raise ValueError('canonical SNDlib member fingerprint mismatch')
    return dict(schema='v7-3-test-lock-v1', owner='Doan Van Tai',
                sha256=hashes, canonical_member_sha256=canonical)


@dataclass(frozen=True)
class VerifiedLock:
    path: str
    digest: str


def create_lock(out=OUT, *, root=ROOT, sndlib=None):
    path = Path(out) / 'lock.json'
    if path.exists():
        raise FileExistsError(path)
    value = fingerprint(root, sndlib)
    write_json(path, value)
    return value


def verify_lock(out=OUT, *, root=ROOT, sndlib=None):
    path = Path(out) / 'lock.json'
    locked = read_json(path)
    current = fingerprint(root, sndlib)
    if locked != current:
        before, after = locked.get('sha256', {}), current['sha256']
        names = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        raise ValueError('lock mismatch: ' + ', '.join(names or ['schema/canonical fingerprint']))
    return VerifiedLock(str(path.resolve()), sha256(path))
