"""Doan Van Tai — L7.5 case lists (write-once) for the telemetry-age sweep [EXPLORATION ONLY; AI (Claude) theo ủy
quyền]. Only stationary quantities (T_int, N) are used here; no truth, no zero-fit outcome.

  python -m experiments.explore_ctmc.design_l75      # -> results/explore_ctmc/cases_l75/{sobol,old,xs}.json + design_report.json

sobol: NEW regimes (not any a = 6 tuple of results/explore_ctmc/cases/*.json, not a control), three x strata
       x < 0, 0 < x <= 0.35 (help band and its edge), x >= 0.4; 27 accepted per stratum, scrambled Sobol over
       (u, lamA, x, log kappa), kappa in [1/20, 2]. Each regime: tau/T_int in TAU_GRID plus tau = 1 s,
       h/T_int in H_GRID.
old:   10 L7.1 asym regimes (truth at tau = 1 already seen in L7.1) to link the numbers: the three regimes of the
       mentor's tau table plus seven spanning x and kappa. Same tau and h grids.
xs:    the 276 regimes of zf_a6_xs (L7.2), h = 10 T_int as there, tau/T_int in XS_TAU.
A unit is (regime, tau). Regimes whose largest unit truth estimate exceeds CAP/2 are dropped and counted.
"""
from fractions import Fraction as F
import glob
import json
import math
from pathlib import Path

from scipy.stats import qmc

from experiments.explore_ctmc import ctmc, tau as T5
from experiments.explore_ctmc.design import rational

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc/cases_l75'
SEED = 20261105
N_PER = 27
CAP = 900.0
D22_BUDGET = 60.0          # CPU-s per (regime, tau) for the D22 joint J; measured 04/11 (SPEC_tau §5)
STRATA = dict(neg=(F(-3, 2), F(-1, 10)), band=(F(1, 50), F(7, 20)), pos=(F(2, 5), F(3, 2)))
OLD_IDS = ['A_u1-2_lA9_x-1_k1-2', 'A_u1_lA7_x1_k1-2', 'A_u1_lA7_x1-4_k1-2', 'A_u1_lA7_x-1_k1-20',
           'A_u1_lA7_x-1-2_k1-2', 'A_u1_lA7_x1-2_k1-2', 'A_u1_lA7_x1-4_k1-20', 'A_u2_lA13-2_x-1-4_k1-2',
           'A_u2_lA13-2_x1-4_k1-20', 'A_u1-2_lA9_x-2_k1-20']


def seen_tuples():
    out = set()
    for f in glob.glob(str(ROOT / 'results/explore_ctmc/cases/*.json')):
        d = json.loads(Path(f).read_text())
        if isinstance(d, list) and d and isinstance(d[0], dict):
            out |= {tuple(F(x) for x in c['parameters'][:4]) for c in d if F(str(c.get('a', 6))) == 6}
    return out


def est_units(lamA, lamB, u, kappa, NA, NB, T, taus, hs):
    """Rough CPU-s per (regime, tau) unit: v1 evaluate at h_max (design.est_cpu) + the e^{Q tau} pushes of the 2H+2
    old-state columns (1.2e-7 per N*column*tau*norm, timed 04/11) + the D22 joint when it is inside D22_BUDGET."""
    norm = T5.q_norm(lamA, lamB, u, kappa)
    hmax = max(float(h) for h in hs)
    base = 1.5e-6 * (NA + NB) * 2 * hmax * norm / 52
    out = []
    for t in taus:
        post = 1.2e-7 * (NA + NB) * (2 * len(hs) + 2) * float(t) * norm
        d22 = 1.1e-8 * (NA * NA + NB * NB) * float(t) * norm
        use = max(NA, NB) <= ctmc.D22_NMAX and d22 <= D22_BUDGET
        out.append(dict(tau=str(t), est_truth=base + post + (d22 if use else 0.0), est_d22=d22, d22=use))
    return out


def regime_case(cid, lamA, lamB, u, kappa, tags, tau_mult=T5.TAU_GRID, h_mult=T5.H_GRID, add_ref=True, hs=None):
    Tm, Tch, NA, NB = T5.tint_max(lamA, lamB, u, kappa)
    hs = sorted(set(rational(m * Tm) for m in h_mult)) if hs is None else [F(h) for h in hs]
    taus = sorted(set([rational(m * Tm) for m in tau_mult] + ([T5.TAU_REF] if add_ref else [])))
    units = est_units(lamA, lamB, u, kappa, NA, NB, Tm, taus, hs)
    return dict(id=cid, parameters=[str(x) for x in (lamA, lamB, u, kappa, 0)], hs=[str(h) for h in hs],
                taus=[str(t) for t in taus], T_int_max=Tm, T_int=Tch, N=dict(A=NA, B=NB),
                x=float((lamB - lamA) / u), units=units, tags=tags)


def sobol(seen):
    out, report = [], {}
    for k, (name, (lo, hi)) in enumerate(STRATA.items()):
        pts = qmc.Sobol(4, scramble=True, seed=SEED + k).random(1024)
        acc, drop = [], dict(domain=0, seen=0, cost=0)
        for j, (pu, pa, px, pk) in enumerate(pts):
            if len(acc) >= N_PER:
                break
            u = F(1, 4) * (1 + int(pu * 12))
            room = F(10) - u - 6
            steps = int(room * 4)
            if steps < 1:
                drop['domain'] += 1
                continue
            lamA = 6 + F(int(pa * steps), 4)
            x = F(round(float(lo + (hi - lo) * F(px)) * 100), 100)
            lamB = lamA + x * u
            if not (lamB >= 6 and lamB + u < 10 and x != 0):
                drop['domain'] += 1
                continue
            kappa = rational(math.exp(math.log(1 / 20) + pk * (math.log(2) - math.log(1 / 20))))
            key = (lamA, lamB, u, kappa)
            if key in seen or T5.is_control(key):
                drop['seen'] += 1
                continue
            c = regime_case(f'T{name[0].upper()}{j:04d}', lamA, lamB, u, kappa, dict(stratum=name, sobol=j))
            if max(un['est_truth'] for un in c['units']) > CAP / 2:
                drop['cost'] += 1
                continue
            seen.add(key)
            acc.append(c)
        out += acc
        report[name] = dict(accepted=len(acc), dropped=drop, x_range=[str(lo), str(hi)])
    return out, report


def old():
    src = {Path(f).stem: json.loads(Path(f).read_text()) for f in glob.glob(str(ROOT / 'results/explore_ctmc/m0/asym/*.json'))}
    out = []
    for rid in OLD_IDS:
        lamA, lamB, u, kappa = (F(x) for x in src[rid]['parameters'][:4])
        out.append(regime_case(rid, lamA, lamB, u, kappa, dict(source='L7.1 asym')))
    return out


def xs():
    out, dropped = [], []
    for c in json.loads((ROOT / 'results/explore_ctmc/cases/zf_a6_xs.json').read_text()):
        lamA, lamB, u, kappa = (F(x) for x in c['parameters'][:4])
        case = regime_case(c['id'], lamA, lamB, u, kappa, dict(c['tags'], source='zf_a6_xs (L7.2)'),
                           tau_mult=T5.XS_TAU, add_ref=False, hs=c['hs'])
        if max(un['est_truth'] for un in case['units']) > CAP / 2:      # 04/11: 7 regimes at the domain top, x >= 0.7
            dropped.append(dict(id=c['id'], N=case['N'], T_int_max=case['T_int_max'], x=case['x']))
            continue
        out.append(case)
    return out, dropped


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    seen = seen_tuples()
    n_seen = len(seen)
    sets = {}
    sets['sobol'], strata = sobol(seen)
    sets['old'] = old()
    sets['xs'], xs_dropped = xs()
    for name, cases in sets.items():
        path = OUT / f'{name}.json'
        if path.exists():
            raise SystemExit(f'{path} exists (write-once)')
    for name, cases in sets.items():
        (OUT / f'{name}.json').write_text(json.dumps(cases, indent=0) + '\n')
    rep = dict(seed=SEED, n_per_stratum=N_PER, cap=CAP, d22_budget=D22_BUDGET, seen_tuples=n_seen, strata=strata,
               counts={k: dict(regimes=len(v), units=sum(len(c['taus']) for c in v),
                               d22_units=sum(un['d22'] for c in v for un in c['units']),
                               est_truth_cpu_h=sum(un['est_truth'] for c in v for un in c['units']) / 3600,
                               max_unit=max(un['est_truth'] for c in v for un in c['units'])) for k, v in sets.items()},
               x_class={k: dict(neg=sum(c['x'] < 0 for c in v), band=sum(0 < c['x'] <= 0.35 for c in v),
                                pos=sum(c['x'] > 0.35 for c in v)) for k, v in sets.items()},
               xs_dropped_by_cost=xs_dropped,
               controls={k: [str(x) for x in v] for k, v in T5.CONTROL_REGIMES_L75.items()},
               note='AI (Claude) theo ủy quyền; stationary quantities only, no truth, no zero-fit outcomes.')
    (OUT / 'design_report.json').write_text(json.dumps(rep, indent=1, default=str) + '\n')
    print(json.dumps(rep, indent=1, default=str))


if __name__ == '__main__':
    main()
