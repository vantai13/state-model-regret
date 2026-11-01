"""Doan Van Tai — case lists for the mechanism-regime exploration [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

ref:   6 fixed regimes to check that every machine computes bit-identical rows.
sobol: scrambled Sobol (seed 20261101) over u, the free load share of A and B, log kappa/tau and log h/tau:
       u in [1/4, 3] (step 1/20), lam = 6 + s (4 - u) .98 (step 1/50), kappa/tau in [.02, 20] (3 significant
       digits), h/tau in [.1, 32] (multiple of 1/120 so H = h/dt is an integer at every ref); keep the first
       N points with h/kappa <= 160. Coordinates are read later as rho = (lamA + lamB)/2mu, d = (lamB - lamA)/mu.

  python -m experiments.explore_mech.design ref|sobol [N]
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


def sobol(n):
    from scipy.stats import qmc
    draws = qmc.Sobol(d=5, scramble=True, seed=20261101).random(1 << 15)
    bad, cases, seen = forbidden_keys(), [], set()
    for x0, sa, sb, xk, xh in draws:
        u = max(F(1, 4), snap(F(1, 4) + F(x0) * F(11, 4), F(1, 20)))
        lamA = snap(6 + F(sa) * (4 - u) * F(49, 50), F(1, 50))
        lamB = snap(6 + F(sb) * (4 - u) * F(49, 50), F(1, 50))
        kappa = sig(10 ** (math.log10(.02) + xk * 3))
        h = max(F(1, 120), snap(F(10 ** (-1 + xh * math.log10(320))), F(1, 120)))
        params = [str(lamA), str(lamB), str(kappa), str(u / 2), str(h), '0']
        if not admissible(params) or key(params) in bad or key(params) in seen:
            continue
        seen.add(key(params))
        cases.append(dict(id=f'B{len(cases):05d}', parameters=params))
        if len(cases) == n:
            return cases
    raise SystemExit(f'only {len(cases)} admissible points')


def main():
    stage = sys.argv[1]
    cases = ([dict(id=f'REF{i}', parameters=p) for i, p in enumerate(REF)] if stage == 'ref'
             else sobol(int(sys.argv[2]) if len(sys.argv) > 2 else 8192))
    path = OUT / 'cases' / f'{stage}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f'{path} exists; case lists are write-once')
    path.write_text(json.dumps(cases, indent=0) + '\n')
    print(f'{stage}: {len(cases)} cases -> {path}')


if __name__ == '__main__':
    main()
