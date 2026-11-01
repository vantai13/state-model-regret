"""Doan Van Tai — case lists for the mechanism-regime exploration [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

ref:   6 fixed regimes to check that every machine computes bit-identical rows.
sobol: (stopped after 103 rows: rate denominators of 50 make the backlog lattice ~12x finer and each row 4-7x
       slower than a 1/4 lattice) scrambled Sobol (seed 20261101) over u, the free load share of A and B, log kappa/tau and log h/tau:
       u in [1/4, 3] (step 1/20), lam = 6 + s (4 - u) .98 (step 1/50), kappa/tau in [.02, 20] (3 significant
       digits), h/tau in [.1, 32] (multiple of 1/120 so H = h/dt is an integer at every ref); keep the first
       N points with h/kappa <= 160.
sobol4: same Sobol stream, but lam and u on a 1/4 lattice and kappa/tau on a 10-per-decade log grid (3
       significant digits), so stationary laws and native lattices are shared; h/tau stays log-continuous.
       Coordinates are read later as rho = (lamA + lamB)/2mu, d = (lamB - lamA)/mu.

  python -m experiments.explore_mech.design ref|sobol|sobol4 [N]
"""
from fractions import Fraction as F
import json
import math
import sys

from experiments.explore_mech.scan import OUT, admissible, forbidden_keys, key

REF = [['7', '8', '1', '3/4', '8', '0'], ['6', '7', '10', '1/4', '32', '0'], ['13/2', '7', '1/5', '3/4', '1/2', '0'],
       ['8', '9', '1', '1/4', '8', '0'], ['6', '6', '1/10', '1/2', '2', '0'], ['7', '13/2', '3', '1/2', '16', '0']]


def sig(x, digits=3):
    e = digits - 1 - math.floor(math.log10(x))
    return F(round(x * 10 ** e), 10 ** e) if e >= 0 else F(round(x / 10 ** -e) * 10 ** -e)


def snap(x, step):
    return round(F(x) / step) * step


def sobol(n, rate_step=None, kappa_grid=False, prefix='B'):
    from scipy.stats import qmc
    draws = qmc.Sobol(d=5, scramble=True, seed=20261101).random(1 << 16)
    bad, cases, seen = forbidden_keys(), [], set()
    for x0, sa, sb, xk, xh in draws:
        ur, lr = (rate_step, rate_step) if rate_step else (F(1, 20), F(1, 50))
        u = max(F(1, 4), snap(F(1, 4) + F(x0) * F(11, 4), ur))
        lamA = snap(6 + F(sa) * (4 - u) * F(49, 50), lr)
        lamB = snap(6 + F(sb) * (4 - u) * F(49, 50), lr)
        kappa = sig(10 ** (math.log10(.02) + (round(xk * 30) / 30 if kappa_grid else xk) * 3))
        h = max(F(1, 120), snap(F(10 ** (-1 + xh * math.log10(320))), F(1, 120)))
        params = [str(lamA), str(lamB), str(kappa), str(u / 2), str(h), '0']
        if not admissible(params) or key(params) in bad or key(params) in seen:
            continue
        seen.add(key(params))
        cases.append(dict(id=f'{prefix}{len(cases):05d}', parameters=params))
        if len(cases) == n:
            return cases
    raise SystemExit(f'only {len(cases)} admissible points')


def grid(prefix, rows):
    """rows of (lamA, lamB, u, kappa, h); drops inadmissible/forbidden/duplicate points, reports how many."""
    bad, cases, seen, dropped = forbidden_keys(), [], set(), 0
    for lamA, lamB, u, kappa, h in rows:
        params = [str(F(lamA)), str(F(lamB)), str(F(kappa)), str(F(u) / 2), str(F(h)), '0']
        if not admissible(params) or key(params) in bad or key(params) in seen:
            dropped += 1
            continue
        seen.add(key(params))
        cases.append(dict(id=f'{prefix}{len(cases):04d}', parameters=params))
    print(f'{prefix}: {len(cases)} kept, {dropped} dropped')
    return cases


def ratios(n, lo=1, hi=160):
    return [10 ** (math.log10(lo) + i * math.log10(hi / lo) / (n - 1)) for i in range(n)]


# hslice (designed after sobol4 showed a class pattern ordered by x = (lamB - lamA)/u at large h/kappa):
#   lamA 13/2, u 3/2, lamB 6..8 (x = -1/3..1), kappa .1 and .2, 16 log-spaced h/kappa in [1, 160].
# xslice: lamA + lamB = 27/2 fixed, u in {1, 2}, lamB on a 1/16 lattice (x step 1/16 or 1/32), kappa .1,
#   h/kappa in {50, 150}: locates the mean-model action boundary in x.
SLICES = {
    'hslice': lambda: grid('H', [(F(13, 2), lamB, F(3, 2), kappa, max(F(1, 120), snap(F(kappa) * F(r), F(1, 120))))
                                 for lamB in (6, F(25, 4), F(13, 2), F(27, 4), 7, F(29, 4), F(15, 2), 8)
                                 for kappa in (F(1, 10), F(1, 5)) for r in ratios(16)]),
    'xslice': lambda: grid('X', [(F(27, 2) - lamB, lamB, u, F(1, 10), F(r, 10))
                                 for u in (1, 2) for r in (50, 150)
                                 for lamB in (F(6 * 16 + j, 16) for j in range(0, 25))]),
    # pslice (designed after sobol4 suggested the R transition is ordered by P = (h/kappa)|delta|, not h/kappa):
    #   lamA + lamB = 14, delta in {0, +-1/2, +-1, +-2}, u in {3/4, 3/2}, kappa in {.05, .2, .8},
    #   P in {2, ..., 128} (delta = 0: h/kappa = P); h snapped to 1/120 and capped at 32 like sobol4.
    'pslice': lambda: grid('P', [(7 - F(dl, 2), 7 + F(dl, 2), u, kappa, h)
                                 for dl in (0, F(1, 2), -F(1, 2), 1, -1, 2, -2) for u in (F(3, 4), F(3, 2))
                                 for kappa in (F(1, 20), F(1, 5), F(4, 5)) for p in (2, 4, 8, 16, 32, 64, 128)
                                 for h in [max(F(1, 120), snap(kappa * p / (abs(dl) or 1), F(1, 120)))] if h <= 32]),
    # xstar (designed after xslice/hslice/pslice were scored): where does the mean model's old-state action flip
    #   in x, across mean load lamA + lamB in {25/2, 27/2, 29/2} and u in {1/2, ..., 5/2}? delta = x u on a 1/16
    #   grid for u <= 1 and a 1/8 grid for u >= 3/2, 0 < x <= 3/4; kappa .1 (h 5) and .5 (h 25), h/kappa = 50.
    'xstar': lambda: grid('S', [((s - dl) / 2, (s + dl) / 2, u, kappa, 50 * kappa)
                                for s in (F(25, 2), F(27, 2), F(29, 2)) for kappa in (F(1, 10), F(1, 2))
                                for u in (F(1, 2), F(1), F(3, 2), F(2), F(5, 2))
                                for step in [F(1, 16) if u <= 1 else F(1, 8)]
                                for dl in (step * k for k in range(1, 100)) if dl / u <= F(3, 4)]),
}


def main():
    stage = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8192
    cases = ([dict(id=f'REF{i}', parameters=p) for i, p in enumerate(REF)] if stage == 'ref'
             else SLICES[stage]() if stage in SLICES
             else sobol(n) if stage == 'sobol' else sobol(n, F(1, 4), True, 'Q'))
    path = OUT / 'cases' / f'{stage}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f'{path} exists; case lists are write-once')
    path.write_text(json.dumps(cases, indent=0) + '\n')
    print(f'{stage}: {len(cases)} cases -> {path}')


if __name__ == '__main__':
    main()
