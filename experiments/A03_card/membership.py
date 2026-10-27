"""Doan Van Tai — whitelist design coordinates only; no priors/D/action values.

Actual p_sw and lambdaA are deliberately never projected or used in predicates.
Targets come from declared anchors; they are not measured switch probabilities.
"""
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID_PATH = ROOT / 'notes/design/grid_v1_2.json'


def coordinates(path=GRID_PATH):
    raw = json.loads(Path(path).read_text())
    rows = []
    for section in ('main', 'heldout'):
        for r in raw[section]:
            rows.append(dict(id=r['id'], section=section,
                             **{k: F(r[k]) for k in ('kappa', 'alphaA', 'alphaB', 'eta', 'h')},
                             targets=tuple(F(str(a['target'])) for a in r['anchors']),
                             candidate=(r['label_1'] == r['label_2'] == 'candidate')))
    return rows


def matches(r, name):
    high = (r['candidate'] and r['alphaA'] == r['alphaB'] == F(9, 10) and
            r['h'] == 8 and r['eta'] in (F(1, 2), F(3, 4)))
    if name == 'K5_list':
        return r['id'] in ('M19', 'M20', 'M21', 'M22')
    if name == 'K5_k3':
        return high and r['kappa'] == 3
    if name == 'K5_kge2':
        return high and r['kappa'] >= 2 and any(t in (F(3, 10), F(7, 10)) for t in r['targets'])
    if name == 'P2_optional':
        return (r['candidate'] and r['kappa'] == 1 and r['alphaA'] == F(9, 10) and
                r['alphaB'] == F(1, 2) and r['h'] == 8 and F(1, 2) <= r['eta'] <= F(3, 4))
    if name == 'P3_optional':
        return high and r['kappa'] >= 2 and F(3, 10) in r['targets']
    raise KeyError(name)


def all_memberships(path=GRID_PATH):
    rows = coordinates(path)
    return {name: {section: [r['id'] for r in rows if r['section'] == section and matches(r, name)]
                   for section in ('main', 'heldout')}
            for name in ('K5_list', 'K5_k3', 'K5_kge2', 'P2_optional', 'P3_optional')}
