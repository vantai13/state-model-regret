"""Doan Van Tai — L7.2 Part 1 case sets [EXPLORATION ONLY; AI (Claude) theo ủy quyền]. Stationary quantities only.

  python -m experiments.explore_ctmc.design_l72

A (a = 6, truth after the KO predictions are locked):
  ko_asym   the 33 asym regimes x 7 horizons of L7.1 (truth of G_S already seen; KO is new)
  ko_slice  ~200 NEW regimes: Sobol over (u, lamA, lamB, log kappa in [0.02, 5], log h/T_int in [0.3, 30]),
            stratified into x < 0, 0 < x < 1/4, x > 1/4 (about 67 each); N <= 3000; no tuple used before.
B (zero fit only, held-out amplitudes a = 3 and a = 15/2; a = 6 x-slices for comparison):
  zf_a{3,7p5}_asym    asym-like families x kappa in {1/20, 1/2, 2} x 7 horizons
  zf_a{3,7p5}_sobol   ~600 Sobol regimes, one horizon each (h/T_int log-uniform in [0.03, 30])
  zf_a{3,6,7p5}_xs    x grids (step 1/20) for x* = sign change of z_inf, kappa in {1/5, 1}
"""
from fractions import Fraction as F
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import qmc

from experiments.explore_ctmc import ctmc
from experiments.explore_ctmc.design import est_cpu, rational

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc/cases'


def tint_N(lamA, lamB, u, kappa, a):
    NA, NB = (ctmc.choose_N(l + u, kappa, a=a) for l in (lamA, lamB))
    T = max(ctmc.chain(l, kappa, N, a).T_int for l, N in ((lamA + u, NA), (lamA, NA), (lamB, NB), (lamB + u, NB)))
    return T, NA, NB


def mk(cid, lamA, lamB, u, kappa, hs, a, tags, T):
    hs = sorted(set(F(h) for h in hs))
    return dict(id=cid, parameters=[str(x) for x in (lamA, lamB, u, kappa, 0)], hs=[str(h) for h in hs], a=str(a),
                long=any(h / kappa > 160 or float(h) / T >= 10 for h in hs), T_int_max=T, tags=tags)


def used_keys():
    keys = set()
    for f in OUT.glob('*.json'):
        for c in json.loads(f.read_text()):
            if 'parameters' in c and c.get('a', '6') == '6':
                keys.add(tuple(str(F(x)) for x in c['parameters'][:4]))
    return keys


def lam_lo(a):
    return max(F(6), F(a))


def sobol_regime(p, a):
    """Map a point of [0,1)^5 to (u, lamA, lamB, kappa, h/T_int) on the 1/4 load lattice of the amplitude's domain."""
    pu, pa, pb, pk, ph = p
    lo = lam_lo(a)
    umax = min(F(3), F(10) - lo - F(1, 4))
    nu = int(umax * 4)
    if nu < 1:
        return None
    u = F(1, 4) * (1 + int(pu * nu))
    steps = int((F(10) - u - lo) * 4)
    if steps < 1:
        return None
    lamA, lamB = lo + F(int(pa * steps), 4), lo + F(int(pb * steps), 4)
    kappa = rational(math.exp(math.log(0.02) + pk * (math.log(5) - math.log(0.02))))
    return u, lamA, lamB, kappa, ph


def ko_slice(n_per=67, seed=20261107):
    used = used_keys() | {k[:4] for k in ctmc_forbidden()}
    pts = qmc.Sobol(5, scramble=True, seed=seed).random(4096)
    bins = {'x<0': [], '0<x<1/4': [], 'x>1/4': []}
    for j, p in enumerate(pts):
        r = sobol_regime(p, 6)
        if r is None:
            continue
        u, lamA, lamB, kappa, ph = r
        x = (lamB - lamA) / u
        b = 'x<0' if x < 0 else ('0<x<1/4' if 0 < x < F(1, 4) else ('x>1/4' if x > F(1, 4) else None))
        if b is None or len(bins[b]) >= n_per or (str(lamA), str(lamB), str(u), str(kappa)) in used:
            continue
        T, NA, NB = tint_N(lamA, lamB, u, kappa, 6)
        h = rational(T * math.exp(math.log(0.3) + ph * (math.log(30) - math.log(0.3))))
        if max(NA, NB) > ctmc.D22_NMAX or est_cpu(NA, NB, kappa, h) > 600:
            continue
        bins[b].append(mk(f'K{j:04d}', lamA, lamB, u, kappa, [h], 6, dict(x_class=b, sobol=j), T))
        if all(len(v) >= n_per for v in bins.values()):
            break
    return [c for v in bins.values() for c in v]


def ctmc_forbidden():
    from experiments.explore_ctmc.scan import fluid_forbidden
    return fluid_forbidden()


def ko_asym():
    out = []
    for c in json.loads((OUT / 'asym.json').read_text()):
        out.append(dict(c, a='6'))
    return out


FAMILIES = {F(3): [(F(1), F(7), [F(-1), F(-1, 2), F(1, 4), F(1, 2), F(1)]), (F(1, 2), F(9), [F(-2), F(-1), F(1, 2)]),
                   (F(2), F(13, 2), [F(-1, 4), F(1, 4), F(1, 2)])],
            F(15, 2): [(F(1, 2), F(17, 2), [F(-2), F(-1), F(1, 2)]), (F(1), F(8), [F(-1, 2), F(1, 4), F(1, 2)]),
                       (F(3, 2), F(31, 4), [F(-1, 6), F(1, 6), F(1, 3)])]}
TAG = {F(3): 'a3', F(15, 2): 'a7p5', F(6): 'a6'}


def zf_asym(a):
    out = []
    for u, lamA, xs in FAMILIES[a]:
        for x in xs:
            lamB = lamA + x * u
            for kappa in (F(1, 20), F(1, 2), F(2)):
                T, NA, NB = tint_N(lamA, lamB, u, kappa, a)
                hs = [rational(m * T) for m in (F(1, 3), 1, 3, 10, 30)] + [160 * kappa, 1000 * kappa]
                out.append(mk(f'Z{TAG[a]}_u{u}_lA{lamA}_x{x}_k{kappa}'.replace('/', '-'), lamA, lamB, u, kappa, hs, a,
                              dict(x=str(x), u=str(u), lamA=str(lamA)), T))
    return out


def zf_sobol(a, n=600, seed=20261108):
    pts = qmc.Sobol(5, scramble=True, seed=seed).random(1024)
    out = []
    for j, p in enumerate(pts):
        r = sobol_regime(p, a)
        if r is None:
            continue
        u, lamA, lamB, kappa, ph = r
        T, NA, NB = tint_N(lamA, lamB, u, kappa, a)
        h = rational(T * math.exp(math.log(0.03) + ph * (math.log(30) - math.log(0.03))))
        out.append(mk(f'S{TAG[a]}_{j:04d}', lamA, lamB, u, kappa, [h], a, dict(sobol=j), T))
        if len(out) >= n:
            break
    return out


def zf_xs(a):
    """x grids for x*: for each family (u, lamA) and kappa, x from the domain's lowest to highest value, step 1/20."""
    fam = {F(3): [(F(1), F(7)), (F(2), F(13, 2)), (F(1, 2), F(8))], F(6): [(F(1), F(7)), (F(2), F(13, 2)), (F(1, 2), F(8))],
           F(15, 2): [(F(1, 2), F(17, 2)), (F(1), F(8)), (F(3, 2), F(31, 4))]}[a]
    lo = lam_lo(a)
    out = []
    for u, lamA in fam:
        for kappa in (F(1, 5), F(1)):
            x = F(-20, 20)
            while x <= 2:
                lamB = lamA + x * u
                if lamB >= lo and lamB + u < 10 and x != 0:
                    T, NA, NB = tint_N(lamA, lamB, u, kappa, a)
                    out.append(mk(f'X{TAG[a]}_u{u}_lA{lamA}_k{kappa}_x{x}'.replace('/', '-'), lamA, lamB, u, kappa,
                                  [rational(10 * T)], a, dict(x=str(x), u=str(u), lamA=str(lamA)), T) | dict(d22=False))
                x += F(1, 20)
    return out


def main():
    sets = dict(ko_asym=ko_asym(), ko_slice=ko_slice())
    for a in (F(3), F(15, 2)):
        sets[f'zf_{TAG[a]}_asym'] = zf_asym(a)
        sets[f'zf_{TAG[a]}_sobol'] = zf_sobol(a)
    for a in (F(3), F(6), F(15, 2)):
        sets[f'zf_{TAG[a]}_xs'] = zf_xs(a)
    for name, cases in sets.items():
        path = OUT / f'{name}.json'
        if path.exists():
            raise SystemExit(f'{path} exists (write-once)')
        path.write_text(json.dumps(cases, indent=0) + '\n')
        print(name, len(cases), 'cases', 'long', sum(c['long'] for c in cases))


if __name__ == '__main__':
    main()
