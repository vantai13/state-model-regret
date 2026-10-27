"""Doan Van Tai — metadata-only v1.2 adapter; D rebuild stays in smr.cells.

Experimental pending T05 ownership. load_cell never computes priors or D.
"""
import json
from fractions import Fraction as F
from pathlib import Path

from smr.cells import queue_D

ROOT = Path(__file__).resolve().parents[2]
GRID_PATH = ROOT / 'notes/design/grid_v1_2.json'


def load_cell(cid, grid_path=GRID_PATH):
    grid = json.loads(Path(grid_path).read_text())
    for section in ('main', 'heldout', 'controls', 'probes'):
        record = next((r for r in grid[section] if r['id'] == cid), None)
        if record is not None:
            break
    else:
        raise KeyError(cid)
    c = {'id': cid, 'role': record.get('role', 'structural_probe'),
         'origin': 'contract-v1.2', 'kappa': F(record['kappa']), 'eta': F(record['eta']),
         'u': F(record.get('u', 2 * F(record['eta']))), 'age': F(1),
         'yA': F(record['yA']), 'yB': F(record['yB']),
         'h': F(record['h']), 'H_coarse': int(record['H_coarse'])}
    c['ratesA'] = (tuple(map(F, record['ratesA'])) if 'ratesA' in record
                   else (F(record['lambdaA']) - 6, F(record['lambdaA']) + 6))
    c['ratesB'] = (F(2), F(14))
    c['lambdaA'] = sum(c['ratesA']) / 2
    if c['u'] != 2 * c['eta'] or c['h'] != F(c['H_coarse'], 120):
        raise ValueError('inconsistent frozen metadata')
    return c


def queue_law(cell, which, ref):
    """D-only API; callers must record exposure. No action values computed."""
    if which not in ('A', 'B') or type(ref) is not int or ref < 1:
        raise ValueError('queue A/B and positive integer refinement required')
    if F(cell['age']) != 1:
        raise ValueError('inherited queue_D supports age=1 s only')
    return queue_D(cell, which, ref)
