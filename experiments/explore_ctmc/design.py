"""Doan Van Tai — case sets for L7.1 [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.design            # writes results/explore_ctmc/cases/{bridge,xslice,pslice,asym}.json

bridge: 1,200 sobol4 tuples (seed 20261103, fixed before any CTMC truth), paired with the fluid rows.
xslice: x grids at large P (u = 1, lamA = 7; u = 2, lamA = 13/2), kappa in {1/5, 1}, h/kappa in {50, 150}.
pslice: P grids at x in {-1/2, 1/4, 1} (u = 1, lamA = 7), kappa in {1/5, 1}, h/kappa from 1 to 160.
asym:  33 regimes x horizon series h/T_int in {1/3, 1, 3, 10, 30} plus h/kappa in {160, 1000}.
Every case records whether it is 'long' (h/kappa > 160 or h/T_int >= 10): long cases need the asymptote lock.
Only stationary quantities (T_int) are used here; no truth.
"""
from fractions import Fraction as F
import json
import math
from pathlib import Path

import numpy as np

from experiments.explore_ctmc import ctmc

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc/cases'
SOBOL = ROOT / 'results/explore_mech/cases/sobol4.json'
SEED = 20261103


def tint_max(lamA, lamB, u, kappa):
    NA, NB = (ctmc.choose_N(lam + u, kappa) for lam in (lamA, lamB))
    return max(ctmc.chain(l, kappa, N).T_int for l, N in ((lamA + u, NA), (lamA, NA), (lamB, NB), (lamB + u, NB)))


def rational(x, digits=3):
    return F(f'{float(x):.{digits}g}')


def case(cid, lamA, lamB, u, kappa, hs, tags, T=None):
    T = tint_max(lamA, lamB, u, kappa) if T is None else T
    hs = sorted(set(F(h) for h in hs))
    long = any(h / kappa > 160 or float(h) / T >= 10 for h in hs)
    return dict(id=cid, parameters=[str(x) for x in (lamA, lamB, u, kappa, 0)], hs=[str(h) for h in hs],
                long=long, T_int_max=T, tags=tags)


def bridge():
    rows = json.loads(SOBOL.read_text())
    pick = np.random.default_rng(SEED).choice(len(rows), 1200, replace=False)
    out = []
    for j in sorted(pick):
        r = rows[j]
        lamA, lamB, kappa, eta, h, c = (F(x) for x in r['parameters'])
        out.append(case(f"B{r['id']}", lamA, lamB, 2 * eta, kappa, [h], dict(sobol4=r['id'])))
    return out


def xslice():
    out = []
    grids = {(F(1), F(7)): [F(x) for x in ('-1', '-1/2', '-1/4', '0', '1/10', '1/5', '3/10', '2/5', '1/2', '3/5',
                                             '7/10', '4/5', '1', '3/2', '19/10')],
             (F(2), F(13, 2)): [F(x) for x in ('-1/4', '0', '1/10', '1/5', '3/10', '2/5', '1/2', '3/5', '7/10')]}
    for (u, lamA), xs in grids.items():
        for kappa in (F(1, 5), F(1)):
            for hk in (50, 150):
                for x in xs:
                    lamB = lamA + x * u
                    out.append(case(f'X_u{u}_k{kappa}_hk{hk}_x{x}'.replace('/', '-'), lamA, lamB, u, kappa,
                                    [hk * kappa], dict(x=str(x), u=str(u), h_kappa=hk)))
    return out


def pslice():
    out = []
    for x in (F(-1, 2), F(1, 4), F(1)):
        for kappa in (F(1, 5), F(1)):
            for hk in (1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 160):
                lamB = F(7) + x
                out.append(case(f'P_x{x}_k{kappa}_hk{hk}'.replace('/', '-'), F(7), lamB, F(1), kappa, [hk * kappa],
                                dict(x=str(x), h_kappa=hk, P=float(hk * abs(x)))))
    return out


def asym():
    out = []
    families = [(F(1), F(7), [F(-1), F(-1, 2), F(1, 4), F(1, 2), F(1)]),
                (F(1, 2), F(9), [F(-2), F(-1), F(1, 2)]),
                (F(2), F(13, 2), [F(-1, 4), F(1, 4), F(1, 2)])]
    for u, lamA, xs in families:
        for x in xs:
            lamB = lamA + x * u
            for kappa in (F(1, 20), F(1, 2), F(2)):
                T = tint_max(lamA, lamB, u, kappa)
                hs = [rational(m * T) for m in (F(1, 3), 1, 3, 10, 30)] + [160 * kappa, 1000 * kappa]
                out.append(case(f'A_u{u}_lA{lamA}_x{x}_k{kappa}'.replace('/', '-'), lamA, lamB, u, kappa, hs,
                                dict(x=str(x), u=str(u), lamA=str(lamA)), T))
    return out


def est_cpu(NA, NB, kappa, h):
    """Rough CPU-s for one case, calibrated on the timing probe T3 (30 CPU-s for N = 3298 + 1635, h = 2000, kappa = 2)."""
    norm = 2 * (9.75 + 6 + 10 + 1 / float(kappa))
    return 1.5e-6 * (NA + NB) * 2 * float(h) * norm / 52


def wide(n=2048, seed=20261104, cap=900.0):
    """Stage E: scrambled Sobol over (u, free load of A, free load of B, log kappa in [0.02, 5], log h/T_int in
    [0.03, 30]); loads on the 1/4 lattice, h rounded to 3 significant digits. Cases whose estimated CPU exceeds cap
    are dropped and counted (the heavy corner: total load near 10 with kappa near 5)."""
    from scipy.stats import qmc
    pts = qmc.Sobol(5, scramble=True, seed=seed).random(n)
    out, dropped = [], 0
    for j, (pu, pa, pb, pk, ph) in enumerate(pts):
        u = F(1, 4) * (1 + int(pu * 12))
        room = F(10) - u - 6                       # max(lamA, lamB) + u < 10 with lam >= 6
        steps = int(room * 4)
        if steps < 1:
            continue
        lamA = 6 + F(int(pa * steps), 4)
        lamB = 6 + F(int(pb * steps), 4)
        kappa = rational(math.exp(math.log(0.02) + pk * (math.log(5) - math.log(0.02))))
        NA, NB = (ctmc.choose_N(lam + u, kappa) for lam in (lamA, lamB))
        T = max(ctmc.chain(l, kappa, N).T_int for l, N in ((lamA + u, NA), (lamA, NA), (lamB, NB), (lamB + u, NB)))
        h = rational(T * math.exp(math.log(0.03) + ph * (math.log(30) - math.log(0.03))))
        if est_cpu(NA, NB, kappa, h) > cap:
            dropped += 1
            continue
        out.append(case(f'W{j:04d}', lamA, lamB, u, kappa, [h], dict(sobol=j), T))
    return out, dropped


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    import sys
    names = sys.argv[1:] or ['bridge', 'xslice', 'pslice', 'asym']
    for name in names:
        cases = globals()[name]()
        if isinstance(cases, tuple):
            cases, dropped = cases
            print(name, 'dropped by CPU cap:', dropped)
        (OUT / f'{name}.json').write_text(json.dumps(cases, indent=0) + '\n')
        print(name, len(cases), 'cases,', sum(c['long'] for c in cases), 'long')


if __name__ == '__main__':
    main()
