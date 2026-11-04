"""Doan Van Tai — L7.3 Part 2 Stage 0 case lists for ctmc-v2 [EXPLORATION ONLY; AI (Claude) theo ủy quyền].
Stationary quantities only (N, T_int); no V, no gaps.

  python -m experiments.explore_ctmc.design_l73      # -> results/explore_ctmc/cases_l73/{asym,mid,sobol,xs}.json

Grid of timescale combos: f in {1/20, 1/5, 1/2} x T_f in {1/5, 1} x T_s/T_f in {10, 100}; peak a_f + a_s = 6.
  asym   families (u, lamA, x) x 13 horizons h/T_int in {0.3, 1, 2, 3, 4.5, 5.5, 6.5, 8, 10, 12.5, 15, 25, 40}
  mid    horizon between the scales: h = 10 T_f = T_s / 10 (only T_s/T_f = 100), Sobol (u, lamA, lamB), 30 per combo
  sobol  Sobol over (u, lamA, lamB, combo, log h/T_int in [0.3, 40]), 30 per combo
  xs     x grids for x* (sign change of z_inf), h = 10 T_int, no D22
Every case has N <= 3000 on both paths (D22 range) and total load <= 9; CONTROL_REGIMES are excluded; drops are counted.
"""
from fractions import Fraction as F
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import qmc

from experiments.explore_ctmc import ctmc2
from experiments.explore_ctmc.design import rational

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc/cases_l73'
LOAD_MAX = F(9)
NMAX = 3000
FS = (F(1, 20), F(1, 5), F(1, 2))
TFS = (F(1, 5), F(1))
RATIOS = (10, 100)
H_MULTS = [F(3, 10), F(1), F(2), F(3), F(9, 2), F(11, 2), F(13, 2), F(8), F(10), F(25, 2), F(15), F(25), F(40)]
FAMILIES = [(F(1), F(7), [F(-1), F(-1, 2), F(1, 4), F(1, 2), F(1)]), (F(1, 2), F(8), [F(-2), F(-1), F(1, 2)]),
            (F(2), F(13, 2), [F(-1, 4), F(1, 4)])]


def combos():
    out = []
    for f in FS:
        af, as_ = ctmc2.amplitudes(f)
        for Tf in TFS:
            for r in RATIOS:
                tag = f"f{f.denominator if f.numerator == 1 else f}_Tf{str(Tf).replace('/', '-')}_r{r}"
                out.append(dict(tag=tag, f=f, Tf=Tf, Ts=Tf * r, af=af, as_=as_, ratio=r))
    return out


_N = {}


def nlevel(load, cb):
    key = (load, cb['tag'])
    if key not in _N:
        _N[key] = ctmc2.choose_N(load, cb['Tf'], cb['Ts'], cb['af'], cb['as_'])
    return _N[key]


def regime_info(lamA, lamB, u, cb):
    """(T_int_max, NA, NB) or None if outside the Stage 0 range (load cap, N cap)."""
    if max(lamA, lamB) + u > LOAD_MAX or min(lamA, lamB) < ctmc2.PEAK:
        return None
    NA, NB = nlevel(lamA + u, cb), nlevel(lamB + u, cb)
    if max(NA, NB) > NMAX:
        return None
    T = max(ctmc2.chain(l, cb['Tf'], cb['Ts'], cb['af'], cb['as_'], N).T_int
            for l, N in ((lamA + u, NA), (lamA, NA), (lamB, NB), (lamB + u, NB)))
    return T, NA, NB


def key(lamA, lamB, u, cb):
    return ctmc2.regime_key(lamA, lamB, u, cb['Tf'], cb['Ts'], cb['af'], cb['as_'])


def is_control(lamA, lamB, u, cb):
    return key(lamA, lamB, u, cb) in ctmc2.CONTROL_REGIMES.values()


def mk(cid, lamA, lamB, u, cb, hs, T, NA, NB, tags, d22=True):
    hs = sorted(set(F(h) for h in hs))
    return dict(id=cid, namespace=ctmc2.NAMESPACE,
                parameters=[str(x) for x in (lamA, lamB, u, cb['Tf'], cb['Ts'], cb['af'], cb['as_'], 0)],
                hs=[str(h) for h in hs], f=str(cb['f']), f_actual=ctmc2.f_of(cb['af'], cb['as_']), T_int_max=T,
                N=dict(A=NA, B=NB), d22=d22, tags=dict(tags, combo=cb['tag'], ratio=cb['ratio']))


def asym(drops):
    out = []
    for cb in combos():
        for u, lamA, xs in FAMILIES:
            for x in xs:
                lamB = lamA + x * u
                if is_control(lamA, lamB, u, cb):
                    drops['control'] += 1
                    continue
                info = regime_info(lamA, lamB, u, cb)
                if info is None:
                    drops['range'] += 1
                    continue
                T, NA, NB = info
                hs = [rational(float(m) * T) for m in H_MULTS]
                cid = f"A2_{cb['tag']}_u{u}_lA{lamA}_x{x}".replace('/', '-')
                out.append(mk(cid, lamA, lamB, u, cb, hs, T, NA, NB, dict(x=str(x), u=str(u), lamA=str(lamA))))
    return out


def lattice_regime(pu, pa, pb):
    u = F(1, 4) * (1 + int(pu * 12))                       # u in {1/4, ..., 3}
    steps = int((LOAD_MAX - u - ctmc2.PEAK) * 4)
    if steps < 0:
        return None
    lamA = ctmc2.PEAK + F(int(pa * (steps + 1)), 4)
    lamB = ctmc2.PEAK + F(int(pb * (steps + 1)), 4)
    return u, lamA, lamB


def sobol_set(drops, per=30, seed=20261111):
    pts = qmc.Sobol(5, scramble=True, seed=seed).random(8192)
    cbs = combos()
    out, count = [], {cb['tag']: 0 for cb in cbs}
    for j, (pu, pa, pb, pc, ph) in enumerate(pts):
        cb = cbs[min(int(pc * len(cbs)), len(cbs) - 1)]
        if count[cb['tag']] >= per:
            continue
        r = lattice_regime(pu, pa, pb)
        if r is None or r[1] == r[2]:
            continue
        u, lamA, lamB = r
        if is_control(lamA, lamB, u, cb):
            drops['control'] += 1
            continue
        info = regime_info(lamA, lamB, u, cb)
        if info is None:
            drops['range'] += 1
            continue
        T, NA, NB = info
        h = rational(T * math.exp(math.log(0.3) + ph * (math.log(40) - math.log(0.3))))
        out.append(mk(f"S2_{cb['tag']}_{j:04d}", lamA, lamB, u, cb, [h], T, NA, NB, dict(sobol=j)))
        count[cb['tag']] += 1
        if all(v >= per for v in count.values()):
            break
    drops['sobol_short'] = {k: per - v for k, v in count.items() if v < per}
    return out


def mid_set(drops, per=30, seed=20261112):
    pts = qmc.Sobol(3, scramble=True, seed=seed).random(4096)
    out = []
    for cb in [c for c in combos() if c['ratio'] == 100]:
        h = 10 * cb['Tf']
        n = 0
        for j, (pu, pa, pb) in enumerate(pts):
            r = lattice_regime(pu, pa, pb)
            if r is None or r[1] == r[2]:
                continue
            u, lamA, lamB = r
            if is_control(lamA, lamB, u, cb):
                drops['control'] += 1
                continue
            info = regime_info(lamA, lamB, u, cb)
            if info is None:
                continue
            T, NA, NB = info
            out.append(mk(f"M2_{cb['tag']}_{j:04d}", lamA, lamB, u, cb, [h], T, NA, NB,
                          dict(sobol=j, h_Tf=str(h / cb['Tf']), h_Ts=str(h / cb['Ts']))))
            n += 1
            if n >= per:
                break
        if n < per:
            drops.setdefault('mid_short', {})[cb['tag']] = per - n
    return out


def xs_set(drops):
    out = []
    grids = [(F(1), F(7), F(1, 10)), (F(1, 2), F(8), F(1, 4))]
    for cb in combos():
        for u, lamA, step in grids:
            x = (ctmc2.PEAK - lamA) / u
            while lamA + x * u + u <= LOAD_MAX:
                lamB = lamA + x * u
                if x != 0 and not is_control(lamA, lamB, u, cb):
                    info = regime_info(lamA, lamB, u, cb)
                    if info is None:
                        drops['range'] += 1
                    else:
                        T, NA, NB = info
                        cid = f"X2_{cb['tag']}_u{u}_lA{lamA}_x{x}".replace('/', '-')
                        out.append(mk(cid, lamA, lamB, u, cb, [rational(10 * T)], T, NA, NB,
                                      dict(x=str(x), u=str(u), lamA=str(lamA)), d22=False))
                x += step
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    drops = dict(control=0, range=0)
    sets = dict(asym=asym(drops), mid=mid_set(drops), sobol=sobol_set(drops), xs=xs_set(drops))
    keys = set()
    for name, cases in sets.items():
        for c in cases:
            k = tuple(c['parameters'][:7])
            if tuple(F(x) for x in k) in ctmc2.CONTROL_REGIMES.values():
                raise SystemExit(f'control regime leaked into {name}: {c["id"]}')
            keys.add(k)
    for name, cases in sets.items():
        path = OUT / f'{name}.json'
        if path.exists():
            raise SystemExit(f'{path} exists (write-once)')
        path.write_text(json.dumps(cases, indent=0) + '\n')
        print(name, len(cases), 'cases', 'horizons', sum(len(c['hs']) for c in cases))
    (OUT / 'design_report.json').write_text(json.dumps(dict(drops=drops, n_unique_regimes=len(keys),
                                                            load_max=str(LOAD_MAX), N_max=NMAX,
                                                            combos=[{k: str(v) for k, v in c.items()} for c in combos()]),
                                                       indent=1) + '\n')
    print('drops', drops, 'unique regimes', len(keys))


if __name__ == '__main__':
    main()
