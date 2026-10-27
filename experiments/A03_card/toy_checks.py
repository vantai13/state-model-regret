"""Doan Van Tai — exposed lesson toy checks; no named grid evaluations.

state_row adapted from supplied L3.3 Part2 §7.5.
"""
"""Toy checks cho L3.3 — KHÔNG gọi engine trên ô M, R, N, P nào.

Scientific purpose: kiểm xem một cơ chế viết bằng lời có đúng dấu trên hệ tí hon.
Output: Δ, Δ̂, e_M, j theo từng state toy. Invariant: W^M0 <= W^M1 (j >= 0).
"""
from fractions import Fraction as F
from smr.idle_gap import weighted_idle as W1, mean_weighted_idle as W0
import random

from experiments.A00_engine.factorial_core import Side, aggregate

def state_row(qA, mA, RA, PA, qB, mB, RB, PB, c, u, H):
    side = {}
    for name, q, m, R, P, u_st, u_sw in (('A', qA, mA, RA, PA, u, 0), ('B', qB, mB, RB, PB, 0, u)):
        w1 = {'St': W1(q, m, R, u_st, c, H, P), 'Sw': W1(q, m, R, u_sw, c, H, P)}
        w0 = {'St': W0(q, m, R, u_st, c, H, P), 'Sw': W0(q, m, R, u_sw, c, H, P)}
        j = {a: w1[a] - w0[a] for a in w1}
        assert min(j.values()) >= 0, 'Jensen bị vi phạm: bug'
        side[name] = dict(d=w1['Sw'] - w1['St'], dh=w0['Sw'] - w0['St'], j=j)
    d, dh = side['A']['d'] + side['B']['d'], side['A']['dh'] + side['B']['dh']
    return dict(Delta=d, Delta_hat=dh, e_M=dh - d, jA=side['A']['j'], jB=side['B']['j'],
                oracle='Sw' if d < 0 else 'St', S1M0='Sw' if dh < 0 else 'St')


def E8():
    half = (F(1, 2), F(1, 2))
    A = Side(half, (F(0), F(1, 2)), (F(0), F(5, 4)), (F(0), F(0)), (1, 4))
    B = Side(half, (F(-3, 2), F(-3)), (F(-1, 2), F(-3, 2)), (F(0), F(0)), (0, 0))
    return A, B


def persistence_rows():
    rows = []
    for s in (F(1, 2), F(3, 4), F(9, 10), F(1)):
        P = {'off': {'off': s, 'on': 1 - s}, 'on': {'on': s, 'off': 1 - s}}
        for mode in ('off', 'on'):
            row = state_row(0, 'x', {'x': F(5, 2)}, {'x': {'x': 1}},
                            0, mode, {'off': F(1), 'on': F(6)}, P, 3, 2, 3)
            rows.append(dict(toy='B_bursty', keep=s, mode=mode, **row))
            mirror = state_row(0, mode, {'off': F(1), 'on': F(6)}, P,
                               0, 'x', {'x': F(5, 2)}, {'x': {'x': 1}}, 3, 2, 3)
            rows.append(dict(toy='A_bursty_AI_conjecture', keep=s, mode=mode, **mirror))
    return rows


def check_ledger_bound(cases=4000, seed=20261031):
    """Reference uses direct pair enumeration; never uses core cut helpers."""
    rng = random.Random(seed)
    def side(which):
        n = rng.randint(1, 5)
        weights = [rng.randint(1, 5) for _ in range(n)]
        sign = 1 if which == 'A' else -1
        def v():
            return sign * F(rng.randint(0, 12), rng.choice((1, 2, 4)))
        return Side(tuple(F(w, sum(weights)) for w in weights), tuple(v() for _ in weights),
                    tuple(v() for _ in weights), tuple(F(30) for _ in weights), tuple(range(n)))
    violations, mismatches, minimum_slack = 0, 0, None
    for _ in range(cases):
        A, B = side('A'), side('B')
        result = aggregate(A, B)
        direct = sum(pa * pb * abs(ha + hb - da - db)
                     for pa, da, ha in zip(A.p, A.d, A.dh)
                     for pb, db, hb in zip(B.p, B.d, B.dh))
        mismatches += result['E_abs_e_M'] != direct
        slack = direct - result['G']['G_M_S1']
        violations += slack < 0
        minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)
    return dict(cases=cases, seed=seed, violations=violations, independent_abs_error_mismatches=mismatches,
                minimum_slack=str(minimum_slack))
