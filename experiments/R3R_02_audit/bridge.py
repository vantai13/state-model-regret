"""Instrument pilot without changing its computations; expose explicit test interfaces.

Doan Van Tai. Physical cost core stays in A00_engine. The untouched pilot snapshot
is the comparison implementation; no named held-out cell is constructed here.
"""
from fractions import Fraction as F
import json
import math
from pathlib import Path

import numpy as np

from smr.cells import law_for, queue_D
from smr.stationary import r2_keep
from experiments.A00_engine.physical import side_from_law
from . import pilot_population as P

LD = np.longdouble
ROOT = Path(__file__).resolve().parents[2]
GKEYS = ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1')


def specs():
    data = json.loads((ROOT / 'experiments/R3R_02_audit/regimes.json').read_text())
    return {r['id']: r for r in data['audit_regimes']}


def spec(rid, ref=1, K=40):
    r = specs()[rid]
    return [rid, r['lambdaA'], r['lambdaB'], r['kappa'], r['eta'], r['h'], int(ref), int(K), r['c_sw']]


def cell_for(s):
    return P.make_regime(*s[1:6], s[0])


def population_from_tables(A, B, wa, wb, c=0, pair=P.pair_values):
    """Finite-node integration layer accepting explicit input, independently testable."""
    if len(wa) != len(A['w']) or len(wb) != len(B['w']):
        raise ValueError('observation weights and conditional tables differ')
    for w in (wa, wb):
        if np.any(np.asarray(w) < 0) or abs(sum(w) - 1) > 1e-12:
            raise ValueError('normalized nonnegative observation law required')
    L = dict.fromkeys(('00', '01', '10', '11'), LD(0))
    for ia, pa in enumerate(wa):
        for ib, pb in enumerate(wb):
            v = pair(A, B, ia, ib, c)
            for k in L:
                L[k] += LD(pa) * LD(pb) * v['L'][k]
    return L


def golden_population(plant):
    """All toy states on A, zero B; preserve exact input ties by integer scaling.

    A zero B with c=0 makes pair_values homogeneous of degree one in A weights
    and A costs. Scale rational probabilities/costs to integer counts first,
    then divide the returned cost by both scales. This avoids changing a toy
    with exact rational tie into a different rounded-input toy. Production
    physical code/pilot estimates are unaffected by this adapter correction.
    """
    xs, ys = list(plant['J']), list(plant['p'])
    cost_scale = math.lcm(*(F(plant[c][x]).denominator for c in ('J', 'Delta', 'Dhat') for x in xs))
    col = lambda v: np.array([LD(int(F(v[x]) * cost_scale)) for x in xs])
    B = dict(d=np.array([LD(0)]), dh=np.array([LD(0)]), j=np.array([LD(0)]), w=[np.array([LD(1)])])
    L = dict.fromkeys(('00', '01', '10', '11'), F(0))
    for y in ys:
        scale = math.lcm(*(F(plant['D'][y].get(x, 0)).denominator for x in xs))
        A = {'d': col(plant['Delta']), 'dh': col(plant['Dhat']), 'j': col(plant['J']),
             'w': [np.array([LD(int(F(plant['D'][y].get(x, 0)) * scale)) for x in xs])]}
        result = P.pair_values(A, B, 0, 0)['L']
        for key in L:
            integer = int(result[key])
            if result[key] != integer:
                raise ArithmeticError('integer-count toy exceeds exact arithmetic range')
            L[key] += F(plant['p'][y]) * F(integer, scale * cost_scale)
    if 'q' in plant:
        cb = F(0)
        for y in ys:
            for q in set(plant['q'].values()):
                weights = {x: F(plant['D'][y].get(x, 0)) for x in xs if plant['q'][x] == q}
                action = sum(w * plant['Dhat'][x] for x, w in weights.items()) < 0
                cb += F(plant['p'][y]) * sum(w * (plant['J'][x] + action * plant['Delta'][x]) for x, w in weights.items())
        L['cb0'] = cb
    return L


def instrument(s):
    cell = cell_for(s)
    result = {'cell': cell, 'spec': s}
    for which in ('A', 'B'):
        unit, reps, weights, tail = P.observation_bins(cell, which, int(s[6]), int(s[7]))
        side = P.side_rows(cell, which, int(s[6]), reps, unit)
        posts = [queue_D(dict(cell, **{'y' + which: idx * unit}), which, int(s[6]))[1] for idx in reps]
        n = max(len(m) for m in posts)
        union = np.zeros((n, 2), dtype=LD)
        for mass in posts:
            union[:len(mass)] += mass
        qi, mi = np.nonzero(union)
        assert len(qi) == len(side['d'])
        result[which] = dict(unit=unit, reps=reps, weights=weights, tail=tail,
                             side=side, qi=qi, mi=mi, posts=posts)
    return result


def direct_stationary_tables(cell, which, ref, cutoff_probability=1e-12):
    """Retained stationary mass and *same* physical state costs; not a new state law."""
    rates = cell['rates' + which]
    pre = cell['u'] if which == 'A' else F(0)
    unit, law = law_for(sum(rates) / 2, pre, cell['kappa'], ref)
    cap = law.quantile(F(str(1 - cutoff_probability)))
    mass = law.mass(cap)
    removed = max(0., float(1 - mass.sum()))
    mass /= mass.sum()
    keep, ke = r2_keep(F(1, 120 * ref), cell['kappa'])
    table, _ = side_from_law(unit, mass, rates=rates, u_stay=pre,
                            u_switch=cell['u'] if which == 'B' else F(0), capacity=F(10),
                            H=cell['H_coarse'] * ref, dt=F(1, 120 * ref), keep=keep, keep_error=ke)
    A = {'d': np.asarray(table.d, dtype=LD), 'dh': np.asarray(table.dh, dtype=LD),
         'j': np.asarray(table.jst, dtype=LD), 'w': [np.asarray(table.p, dtype=LD)]}
    return A, dict(removed=removed, unit=str(unit), cutoff=cap)


class BlackBoxSide:
    """Engine action/cost queries at arbitrary physical lattice q, not only y nodes.

    Full idle-gap table up to a deterministic no-idle threshold; beyond threshold
    idle gaps are symbolically zero and JStay follows the exactly busy linear path.
    Backward age expectations avoid a separate queue_D call for every MC episode.
    """
    def __init__(self, cell, which, ref):
        self.cell, self.which, self.ref = cell, which, ref
        rates = cell['rates' + which]
        pre = cell['u'] if which == 'A' else F(0)
        self.unit, self.law = law_for(sum(rates) / 2, pre, cell['kappa'], ref)
        self.dt, self.H = F(1, 120 * ref), cell['H_coarse'] * ref
        self.keep, ke = r2_keep(self.dt, cell['kappa'])
        self.pre, self.post = pre, cell['u'] if which == 'B' else F(0)
        # Both actions cannot hit empty at q greater than maximum possible drain*h.
        drain = max(F(0), F(10) - min(rates) - min(self.pre, self.post))
        self.cap = int(np.ceil(float(drain * cell['h'] / self.unit))) + 2
        mass = np.full((self.cap + 1, 2), LD(1) / (2 * (self.cap + 1)), dtype=LD)
        t, self.detail = side_from_law(self.unit, mass, rates=rates, u_stay=self.pre,
                                     u_switch=self.post, capacity=F(10), H=self.H,
                                     dt=self.dt, keep=self.keep, keep_error=ke)
        self.d = np.asarray(t.d, dtype=LD).reshape(-1, 2)
        self.dh = np.asarray(t.dh, dtype=LD).reshape(-1, 2)
        self.j = np.asarray(t.jst, dtype=LD).reshape(-1, 2)
        self.inc = tuple(int((r + pre - 10) * self.dt / self.unit) for r in rates)
        age_steps = 120 * ref
        n = self.cap + 1 + age_steps * max(0, -min(self.inc))
        def age_values(v):
            vals = np.zeros((n, 2), dtype=LD)
            vals[:len(v)] = v
            p = LD(self.keep.numerator) / self.keep.denominator
            ix = np.arange(n)
            for _ in range(age_steps):
                after = np.zeros_like(vals)
                for m, inc in enumerate(self.inc):
                    qn = np.maximum(0, ix + inc)
                    good = qn < n
                    after[good, m] = p * vals[qn[good], m] + (1 - p) * vals[qn[good], 1 - m]
                vals = after
            return vals
        self.old_d, self.old_dh = age_values(self.d), age_values(self.dh)
        mass_prior = self.law.mass(n - 1)
        denom = mass_prior.sum(axis=1)
        self.old_mode = mass_prior / np.where(denom > 0, denom, 1)[:, None]
        self.g = (self.old_d * self.old_mode).sum(axis=1)
        self.gh = (self.old_dh * self.old_mode).sum(axis=1)

    def _indices(self, q):
        scaled = np.asarray(q, dtype=float) / float(self.unit)
        idx = np.rint(scaled).astype(np.int64)
        if np.any(np.abs(scaled - idx) > 1e-6):
            raise ValueError('query not on specified stationary lattice')
        return idx

    def gap(self, q, mode):
        idx, mode = self._indices(q), np.asarray(mode, dtype=int)
        shape = idx.shape
        d, dh = np.zeros(shape, dtype=LD), np.zeros(shape, dtype=LD)
        good = idx <= self.cap
        d[good], dh[good] = self.d[idx[good], mode[good]], self.dh[idx[good], mode[good]]
        return d, dh

    def old_gap(self, q):
        idx = self._indices(q)
        d, dh = np.zeros(idx.shape, dtype=LD), np.zeros(idx.shape, dtype=LD)
        good = idx < len(self.g)
        d[good], dh[good] = self.g[idx[good]], self.gh[idx[good]]
        return d, dh

    def cost(self, q, mode):
        idx, mode = self._indices(q), np.asarray(mode, dtype=int)
        # Busy cost exact mean-rate sum at far states, no cost-table clipping.
        k = np.arange(self.H, dtype=LD)
        r = LD(2) * LD(self.keep.numerator) / self.keep.denominator - 1
        mu = LD(float(sum(self.cell['rates' + self.which]) / 2))
        net_sum = (self.H - k) * (mu + float(self.pre) - 10)
        common = LD(float(self.dt)) ** 2 * net_sum.sum()
        modeterm = LD(float(self.dt)) ** 2 * ((self.H - k) * 6 * np.power(r, k)).sum()
        j = self.H * LD(float(self.dt)) * np.asarray(q, dtype=LD) + common + (2 * mode - 1) * modeterm
        good = idx <= self.cap
        j[good] = self.j[idx[good], mode[good]]
        d, _ = self.gap(q, mode)
        linear = LD(float((self.post - self.pre) * self.dt * self.dt * self.H * (self.H + 1) / 2))
        return j, j + d + linear


class BlackBox:
    def __init__(self, s):
        self.spec, self.cell = s, cell_for(s)
        self.A, self.B = BlackBoxSide(self.cell, 'A', int(s[6])), BlackBoxSide(self.cell, 'B', int(s[6]))
        self.c = LD(float(F(s[8])))

    def actions(self, y, x):
        ga, ha = self.A.old_gap(y[:, 0]); gb, hb = self.B.old_gap(y[:, 1])
        da, dha = self.A.gap(x[:, 0], x[:, 1]); db, dhb = self.B.gap(x[:, 2], x[:, 3])
        return np.column_stack((ha + hb + self.c < 0, ga + gb + self.c < 0,
                                dha + dhb + self.c < 0, da + db + self.c < 0))

    def costs(self, x):
        ja, sa = self.A.cost(x[:, 0], x[:, 1]); jb, sb = self.B.cost(x[:, 2], x[:, 3])
        return np.column_stack((ja + jb, sa + sb + self.c))
