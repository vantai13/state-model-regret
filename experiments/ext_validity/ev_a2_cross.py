"""Doan Van Tai — EV-A2: zero-fit sign-reversal threshold Delta* of the closed loop, confirmation on a fresh panel
[AI (Claude) theo ủy quyền 14/11/2026]. With the lookahead fixed at h_p = 10 T_int, the first-order closed-loop law
gives G_S_CL(Delta) = a + b / Delta, hence Delta* = -b / a when a < 0 < b (harm at long periods, help at short ones).
Test: G_S_CL > 0 at Delta*/2 and G_S_CL < 0 at 2 Delta*.

    python -m experiments.ext_validity.ev_a2_cross design|predict|truth|score [--workers N]
"""
import csv
import json
import math
import multiprocessing
import sys
from fractions import Fraction as F
from pathlib import Path

from experiments.ext_validity import closed_loop as CL

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/ext_validity/ev_a2'
CASES, PRED, TRUTH = OUT / 'cases.json', OUT / 'predictions.csv', OUT / 'truth.csv'
SEED = 20261181
HP_MULT = 10
N_TARGET = 30
MIN_A = 0.005          # |a| / r_min: predicted harm at 2 Delta* is a/2 >= 0.25% of r_min


def _rat(x):
    from experiments.explore_ctmc.design import rational
    return rational(x)


def ab(case):
    """a, b of G_S_CL(Delta) = a + b/Delta from the zero-fit first-order law (no truth); exact two-point solve."""
    hp = _rat(HP_MULT * case['T_int_max'])
    g1 = CL.zero_fit_first_order(case, F(1), hp)['G_S_CL_pred1']
    g2 = CL.zero_fit_first_order(case, F(2), hp)['G_S_CL_pred1']
    b = 2 * (g1 - g2)
    return g1 - b, b, hp


def design():
    from scipy.stats import qmc
    from experiments.explore_ctmc import design_l75 as L75, tau as T5, ctmc as C
    from experiments.explore_ctmc.csw_harm import seen_all
    if CASES.exists():
        raise FileExistsError(CASES)
    seen = seen_all()
    for p in ('results/explore_ctmc/csw_harm/cases_csw_harm.json', 'results/ext_validity/ev_b/cases.json',
              'results/ext_validity/ev_b_rep/cases.json', 'results/ext_validity/ev_a/cases.json'):
        seen |= {tuple(F(x) for x in c['parameters'][:4]) for c in json.loads((ROOT / p).read_text())}
    out, report = [], dict(scanned=0, ineligible=0)
    gens = [iter(qmc.Sobol(4, scramble=True, seed=SEED + k).random(4096)) for k in range(2)]
    names = ['neg', 'pos']
    k = 0
    while len(out) < N_TARGET and report['scanned'] < 4000:
        name = names[k % 2]
        pu, pa, px, pk = next(gens[k % 2])
        k += 1
        lo, hi = L75.STRATA[name]
        u = F(1, 4) * (1 + int(pu * 12))
        steps = int((F(10) - u - 6) * 4)
        if steps < 1:
            continue
        lamA = 6 + F(int(pa * steps), 4)
        x = F(round(float(lo + (hi - lo) * F(px)) * 100), 100)
        lamB = lamA + x * u
        kappa = _rat(math.exp(math.log(1 / 20) + pk * (math.log(2) - math.log(1 / 20))))
        key = (lamA, lamB, u, kappa)
        if not (lamB >= 6 and lamB + u < 10 and x != 0) or key in seen or T5.is_control(key):
            continue
        Tm, _, NA, NB = T5.tint_max(lamA, lamB, u, kappa)
        if max(NA, NB) > 600 or Tm < 4:
            continue
        seen.add(key)
        report['scanned'] += 1
        case = dict(id=f'X{name[0].upper()}{len(out):02d}', stratum=name, x=float(x), T_int_max=Tm,
                    parameters=[str(v) for v in key])
        a, b, hp = ab(case)
        r_min = min(sum(C.chain(l, kappa, n).r for l, n in ((lamA + u, NA), (lamB, NB))),
                    sum(C.chain(l, kappa, n).r for l, n in ((lamA, NA), (lamB + u, NB))))
        if not (a < 0 < b and -a / r_min >= MIN_A):
            report['ineligible'] += 1
            continue
        dstar = -b / a
        lo_d, hi_d = dstar / 2, 2 * dstar
        if lo_d <= 1.5 or hi_d > 30 * Tm:
            report['ineligible'] += 1
            continue
        case.update(a=a, b=b, r_min=r_min, Delta_star=dstar, Delta_star_over_T=dstar / Tm, h_p=str(hp),
                    Delta_lo=str(_rat(lo_d)), Delta_hi=str(_rat(hi_d)))
        out.append(case)
    OUT.mkdir(parents=True, exist_ok=True)
    CASES.write_text(json.dumps(out, indent=1) + '\n')
    (OUT / 'design_report.json').write_text(json.dumps(dict(report, accepted=len(out), seed=SEED), indent=1) + '\n')
    print(report, 'accepted', len(out))


def _pred(case):
    rows = []
    for which in ('lo', 'hi'):
        D = F(case[f'Delta_{which}'])
        z = CL.zero_fit_first_order(case, D, F(case['h_p']))
        rows.append(dict(id=case['id'], which=which, Delta=str(D), Delta_over_T=float(D) / case['T_int_max'],
                         pred_abs=z['G_S_CL_pred1'], pred_sign=1 if z['G_S_CL_pred1'] > 0 else -1, r_min=case['r_min']))
    return rows


def _truth(case):
    rows = []
    for which in ('lo', 'hi'):
        D = F(case[f'Delta_{which}'])
        o = CL.closed_loop(case, D, F(case['h_p']))
        J = {k: v['J'] for k, v in o['cells'].items()}
        rows.append(dict(id=case['id'], which=which, Delta=str(D), status=o['status'], G_S_CL_abs=J['00'] - J['10'],
                         G_S_CL_pct=100 * (J['00'] - J['10']) / J['11'], J11=J['11'], cpu=o['cpu']))
    return rows


def _write(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()} for r in rows)


def run(fn, path, workers):
    if path.exists():
        raise FileExistsError(path)
    with multiprocessing.get_context('fork').Pool(workers) as p:
        _write(path, [r for rs in p.map(fn, json.loads(CASES.read_text())) for r in rs])


def score():
    P = {(r['id'], r['which']): r for r in csv.DictReader(PRED.open())}
    T = {(r['id'], r['which']): r for r in csv.DictReader(TRUTH.open())}
    ids = sorted({k[0] for k in P})
    ok = [i for i in ids if all(T[(i, w)]['status'] == 'COMPLETED' for w in ('lo', 'hi'))]
    both = [i for i in ok if float(T[(i, 'lo')]['G_S_CL_abs']) > 0 and float(T[(i, 'hi')]['G_S_CL_abs']) < 0]
    lo_ok = sum(float(T[(i, 'lo')]['G_S_CL_abs']) > 0 for i in ok)
    hi_ok = sum(float(T[(i, 'hi')]['G_S_CL_abs']) < 0 for i in ok)
    share = len(both) / len(ok) if ok else None
    res = dict(n=len(ok), of=len(ids), Z1=dict(both_signs=len(both), share=share, threshold=0.75,
               verdict='NOT_EVALUABLE' if len(ok) < 10 else ('PASS' if share >= 0.75 else 'FAIL')),
               lo_help=lo_ok, hi_harm=hi_ok,
               rel_err_hi=[abs(float(T[(i, 'hi')]['G_S_CL_abs']) - float(P[(i, 'hi')]['pred_abs'])) / abs(float(P[(i, 'hi')]['pred_abs'])) for i in ok])
    (OUT / 'score.json').write_text(json.dumps(res, indent=1) + '\n')
    print(json.dumps({k: v for k, v in res.items() if k != 'rel_err_hi'}, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1]
    w = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 8
    if cmd == 'design':
        design()
    elif cmd == 'predict':
        run(_pred, PRED, w)
    elif cmd == 'truth':
        if not (OUT / 'lock.json').exists():
            raise RuntimeError('not locked')
        run(_truth, TRUTH, w)
    else:
        score()
