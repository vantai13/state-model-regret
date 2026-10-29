"""Doan Van Tai — L3R.6 region rules on design coordinates only (no outcomes).

A rule only receives a DesignView: the six contract identity fields plus
deterministic derived coordinates. Any other key, e.g. G_M_pctC, raises KeyError.
"""
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction as F
import json

from experiments.R3R_05_contract.schema import IDENTITY, MU, AGE, exact, canonical

DERIVED = ('rhoA', 'rhoB', 'rhoA_post', 'rhoB_post', 'phi', 'h_over_tau')
COORDS = IDENTITY + DERIVED


class DesignView(Mapping):
    """Read-only exact design coordinates of one regime."""

    def __init__(self, reg):
        lA, lB, u, kappa, h, c_sw = canonical(reg)
        self._v = dict(zip(IDENTITY, (lA, lB, u, kappa, h, c_sw)))
        self._v.update(rhoA=(lA + u)/MU, rhoB=lB/MU, rhoA_post=lA/MU, rhoB_post=(lB + u)/MU,
                       phi=u/(MU - lB), h_over_tau=h/AGE)

    def __getitem__(self, key):
        if key not in self._v:
            raise KeyError(f'region rules may only read design coordinates, not {key!r}')
        return self._v[key]

    def __iter__(self): return iter(self._v)
    def __len__(self): return len(self._v)
    def key(self): return tuple(self._v[k] for k in IDENTITY)


@dataclass(frozen=True)
class Box:
    """Closed box on design coordinates; every bound is an exact rational."""
    rule_id: str
    bounds: tuple          # ((coord, lo, hi), ...)
    role: str = ''         # e.g. MV_plus, MV_minus, SH_plus, Gamma, BND
    note: str = ''

    def __post_init__(self):
        seen = set()
        for c, lo, hi in self.bounds:
            if c not in COORDS: raise ValueError(f'unknown design coordinate {c!r}')
            if c in seen: raise ValueError(f'duplicate coordinate {c!r}')
            if exact(lo) > exact(hi): raise ValueError(f'empty interval for {c}')
            seen.add(c)

    def __call__(self, design):
        return all(exact(lo) <= design[c] <= exact(hi) for c, lo, hi in self.bounds)

    def active(self, fixed=('c_sw',)):
        """Coordinates restricted to a proper sub-range (not a fixed-scope pin)."""
        return [c for c, lo, hi in self.bounds if c not in fixed]

    def text(self):
        parts = [f'{c}={lo}' if exact(lo) == exact(hi) else f'{c}∈[{lo};{hi}]' for c, lo, hi in self.bounds]
        return f'{self.rule_id}: ' + ', '.join(parts)

    def as_json(self):
        return dict(rule_id=self.rule_id, role=self.role, note=self.note,
                    bounds=[dict(coord=c, lo=str(exact(lo)), hi=str(exact(hi))) for c, lo, hi in self.bounds])


EMPTY = Box('EMPTY', (('lambdaA', '6', '6'), ('lambdaB', '7', '7'), ('u', '0', '0')), note='test rule: no valid regime')


def in_region(rule, design):
    if not isinstance(design, DesignView):
        raise TypeError('region rules receive a DesignView, never an outcome row')
    return bool(rule(design))


def v12_cells(grid_path='notes/design/grid_v1_2.json'):
    """Parameter-only v1.2 cells (lambdaB=8 by D4, c_sw=0); no p_sw/outcome fields used."""
    grid = json.load(open(grid_path))
    out = []
    for role in ('main', 'heldout'):
        for c in grid[role]:
            reg = dict(lambdaA=c['lambdaA'], lambdaB='8', u=c['u'], kappa=c['kappa'], h=c['h'], c_sw='0')
            out.append((c['id'], DesignView(reg)))
    return out


def sealed_and_exposed(rule, grid_path='notes/design/grid_v1_2.json'):
    """Which v1.2 cells (incl. sealed R09/R10) fall inside a rule, by parameters only."""
    hits = [cid for cid, d in v12_cells(grid_path) if in_region(rule, d)]
    return dict(v12_cells_inside=hits, sealed_inside=[c for c in hits if c in ('R09', 'R10')])
