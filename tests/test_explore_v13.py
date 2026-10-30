"""Doan Van Tai — population pilot ledger against brute-force enumeration (synthetic tables only)."""
import itertools

import numpy as np
import pytest

from experiments.explore_v13 import population as P

LD = np.longdouble


def tables(rng, n=7):
    A = dict(d=rng.uniform(0, 3, n).astype(LD), dh=rng.uniform(0, 4, n).astype(LD), j=rng.uniform(5, 9, n).astype(LD))
    B = dict(d=-rng.uniform(0, 3, n).astype(LD), dh=-rng.uniform(0, 4, n).astype(LD), j=rng.uniform(5, 9, n).astype(LD))
    for T in (A, B):
        w = rng.dirichlet(np.ones(n)) * (rng.random(n) < .7)
        w[0] += 1e-3
        T['w'] = [(w / w.sum()).astype(LD)]
    return A, B


def brute(A, B, c):
    wa, wb = A['w'][0], B['w'][0]
    J = float((wa * A['j']).sum() + (wb * B['j']).sum())
    ED = float((wa * A['d']).sum() + (wb * B['d']).sum()) + c
    EDh = float((wa * A['dh']).sum() + (wb * B['dh']).sum()) + c
    T10 = T11 = wrong = 0.0
    for i, k in itertools.product(range(len(wa)), range(len(wb))):
        w = float(wa[i] * wb[k])
        if w == 0:
            continue
        delta = float(A['d'][i] + B['d'][k]) + c
        hat = float(A['dh'][i] + B['dh'][k]) + c
        T10 += w * delta * (hat < 0)
        T11 += w * delta * (delta < 0)
        wrong += w * ((delta < 0) != (hat < 0))
    return {'00': J + (EDh < 0) * ED, '01': J + (ED < 0) * ED, '10': J + T10, '11': J + T11}, wrong


@pytest.mark.parametrize('seed,c', [(s, c) for s in range(6) for c in (0, 0.5, 2.0)])
def test_pair_values_match_enumeration_with_switch_cost(seed, c):
    A, B = tables(np.random.default_rng(seed))
    v = P.pair_values(A, B, 0, 0, c)
    L, wrong = brute(A, B, c)
    for k in L:
        assert float(v['L'][k]) == pytest.approx(L[k], abs=1e-12)
    assert float(v['wrong']) == pytest.approx(wrong, abs=1e-12)
    G = P.contrasts(v['L'])
    assert float(G['Gamma']) == pytest.approx(float(G['G_M_S1'] - G['G_M']), abs=1e-12)


def test_regime_family_bounds():
    with pytest.raises(ValueError):
        P.make_regime(5, 8, 1, '1/2', 8, 'Xbad')      # negative OFF rate
    with pytest.raises(ValueError):
        P.make_regime(9, 8, 1, '1/2', 8, 'Xbad')      # unstable A under Stay
    assert P.make_regime(7, 8, 1, '1/2', 8, 'Xok')['H_coarse'] == 960


# --- age / amplitude extension (regime-map exploration) ---
import csv
from fractions import Fraction as F
from pathlib import Path

from smr import cells as SC

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('which', ['A', 'B'])
def test_local_queue_D_is_bitwise_smr_at_age_one(which):
    cell = P.make_regime('13/2', '7', '3/10', '3/4', 2, 'Xage')
    unit, reps, _, _ = P.observation_bins(cell, which, 1, 8)
    for idx in reps:
        c = dict(cell, **{'y' + which: idx * unit})
        u1, m1, s1, e1 = P.queue_D(c, which, 1)
        u0, m0, s0, e0 = SC.queue_D(c, which, 1)
        assert u1 == u0 and e1 == e0
        assert np.array_equal(m1, m0) and np.array_equal(s1, s0)


def test_evaluate_reproduces_saved_map1_row_exactly():
    row = next(r for r in csv.DictReader(open(ROOT / 'results/explore_v13/map1/regimes.csv')) if r['id'] == 'XM1051')
    out, _ = P.evaluate(('XM1051', '13/2', '7', '3/10', '3/4', '2', 1, 40, '0', '1', '6'))
    for k in ('Cbar', 'Sbar', 'G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1', 'P_flip'):
        assert out[k] == float(row[k]), k


def test_age_and_amplitude_bounds():
    with pytest.raises(ValueError):
        P.make_regime(7, 8, 1, '1/2', 8, 'Xbad', age=F(1, 240))   # not on the coarse dt grid
    with pytest.raises(ValueError):
        P.make_regime(7, 7, 1, '1/2', 8, 'Xbad', amp=3)            # B never overloaded: point-mass law
    assert P.make_regime(7, 8, 1, '1/2', 8, 'Xok', age=4, amp=4)['ratesA'] == (3, 11)


def test_mode_posterior_forgets_the_observation_with_age():
    gaps = []
    for age in (F(1, 4), 1, 4):
        cell = P.make_regime('13/2', '7', '3/10', '3/4', 2, 'Xage', age=age)
        unit, reps, _, _ = P.observation_bins(cell, 'A', 1, 8)
        _, mass, _, _ = P.queue_D(dict(cell, yA=reps[-1] * unit), 'A', 1)
        gaps.append(abs(float(mass[:, 1].sum()) - .5))
    assert gaps[0] > gaps[1] > gaps[2]
