"""Doan Van Tai — EV-TE post-lock score writer (serialization only).

Provenance: written by Claude (orchestrator, author delegation 16/11/2026) after the locked
`ev_te.score` failed at its last step. The locked function computed every number and wrote
`score_cells.csv`, then `json.dump` raised `TypeError: Object of type int64 is not JSON
serializable` while writing `score.json`: the pass counts are sums of numpy booleans.

This wrapper does not change `ev_te.py` (locked, sha256 checked below) and does not change any
computation. It replaces only the module-level `write_json` by a copy whose encoder converts
numpy scalars (`np.bool_`, `np.integer`, `np.floating`) to the equal Python value with `.item()`,
then calls the locked `ev_te.score()` unchanged (which runs `verify_lock` first).
Precedent: L7.5 `score_l75_post.py` (DL-140). The failed attempt is kept byte-for-byte in
`results/ext_validity/ev_te/score_attempt01_failed/`.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from experiments.ext_validity import ev_te

LOCKED_SHA256 = '4eb87842c1397ebdcb5fa1efc4ea3fe5711821d093cead435fe7f57693ec084f'


def _numpy_scalar(o):
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False, default=_numpy_scalar)
        f.write('\n')


def main():
    sha = hashlib.sha256(Path(ev_te.__file__).read_bytes()).hexdigest()
    if sha != LOCKED_SHA256:
        raise SystemExit(f'ev_te.py changed: {sha}')
    ev_te.write_json = write_json
    ev_te.score()
    print('SCORE_WRITTEN', flush=True)


if __name__ == '__main__':
    main()
