"""Verified inputs and write-once artifacts, separate from engine execution."""
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.R3R_06_cards import verify_cards

ORDER = ('MV+A', 'MV-ii', 'MV-BND', 'SH+A', 'SH-ii', 'SH-BND')
TEST_ROOT = 318700001
TEST_RANGE = range(318700000, 318710000)
NUMERICS_TAG = 'contract-v1.3.1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    return sha(Path(path).read_bytes())


def git(*args):
    return subprocess.check_output(['git', *args], stderr=subprocess.PIPE)


def verified_card():
    result = verify_cards.verify()
    if result['status'] != 'PASS':
        raise ValueError('card receipt FAIL: ' + '; '.join(result['errors']))
    text = Path(verify_cards.FROZEN[0]).read_text()
    return json.loads(text.split('<!-- L3R6_CARDS\n', 1)[1].split('\n-->', 1)[0])


def write_once(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        stream.write(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def check_committed(path):
    path = Path(path)
    if path.is_absolute():
        path = path.relative_to(Path.cwd())
    if git('show', f'HEAD:{path}') != path.read_bytes():
        raise ValueError(f'input must match its committed HEAD blob: {path}')


def tool_hashes():
    paths=sorted(str(p) for p in Path('experiments/R3R_07_confirmation').glob('*.py'))
    paths+=['experiments/R3R_06_cards/verify_cards.py']
    return {path:digest(path) for path in paths}


def verify_tool_hashes(expected):
    if expected!=tool_hashes():
        raise ValueError('complete confirmation-tool manifest mismatch')
    for path in expected:
        check_committed(path)


def environment():
    import platform
    import numpy as np
    import scipy
    return dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                bit_generator='PCG64', platform=platform.platform())
