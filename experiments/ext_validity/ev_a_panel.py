"""Doan Van Tai — EV-A panel, zero-fit predictions and scoring for the closed-loop test [AI (Claude) theo ủy quyền
14/11/2026]. The evaluator is closed_loop.py (Codex). Panel: fresh, seed 20261161, neg/band/pos 20 each, N <= 600,
T_int_max >= 4 s (so Delta = T/2 > tau).

    python -m experiments.ext_validity.ev_a_panel design
    python -m experiments.ext_validity.ev_a_panel predict --workers N    # zero fit only
    python -m experiments.ext_validity.ev_a_panel score --run DIR
"""
import argparse
import csv
import json
import math
import multiprocessing
import statistics as st
from fractions import Fraction as F
from pathlib import Path

from experiments.ext_validity import closed_loop as CL

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/ext_validity/ev_a'
CASES, GRID, PRED = OUT / 'cases.json', OUT / 'grid.json', OUT / 'predictions.csv'
SEED = 20261161
COUNTS = dict(neg=20, band=20, pos=20)
GRIDV = [['1/2', '1/2'], ['1', '1'], ['3', '3'], ['10', '10'], ['1/2', '10'], ['1', '10'], ['3', '10']]


def design():
    from scipy.stats import qmc
    from experiments.explore_ctmc import design_l75 as L75, tau as T5
    from experiments.explore_ctmc.design import rational
    from experiments.explore_ctmc.csw_harm import seen_all
    if CASES.exists():
        raise FileExistsError(CASES)
    seen = seen_all()
    for p in ('results/explore_ctmc/csw_harm/cases_csw_harm.json', 'results/ext_validity/ev_b/cases.json',
              'results/ext_validity/ev_b_rep/cases.json'):
        f = Path('/home/vantai/state-model-regret') / p
        seen |= {tuple(F(x) for x in c['parameters'][:4]) for c in json.loads(f.read_text())}
    out = []
    for k, name in enumerate(COUNTS):
        lo, hi = L75.STRATA[name]
        acc = []
        for pu, pa, px, pk in qmc.Sobol(4, scramble=True, seed=SEED + k).random(4096):
            if len(acc) >= COUNTS[name]:
                break
            u = F(1, 4) * (1 + int(pu * 12))
            steps = int((F(10) - u - 6) * 4)
            if steps < 1:
                continue
            lamA = 6 + F(int(pa * steps), 4)
            x = F(round(float(lo + (hi - lo) * F(px)) * 100), 100)
            lamB = lamA + x * u
            kappa = rational(math.exp(math.log(1 / 20) + pk * (math.log(2) - math.log(1 / 20))))
            key = (lamA, lamB, u, kappa)
            if not (lamB >= 6 and lamB + u < 10 and x != 0) or key in seen or T5.is_control(key):
                continue
            Tm, _, NA, NB = T5.tint_max(lamA, lamB, u, kappa)
            if max(NA, NB) > 600 or Tm < 4:
                continue
            seen.add(key)
            acc.append(dict(id=f'A{name[0].upper()}{len(acc):02d}', stratum=name, x=float(x), T_int_max=Tm,
                            parameters=[str(v) for v in key], N=dict(A=NA, B=NB)))
        out += acc
    OUT.mkdir(parents=True, exist_ok=True)
    CASES.write_text(json.dumps(out, indent=1) + '\n')
    GRID.write_text(json.dumps(GRIDV) + '\n')
    print({n: sum(c['stratum'] == n for c in out) for n in COUNTS})


def _jobs(case):
    from experiments.explore_ctmc.design import rational
    return [(rational(float(F(dm)) * case['T_int_max']), rational(float(F(hm)) * case['T_int_max']), dm, hm)
            for dm, hm in GRIDV]


def _pred(case):
    rows = []
    for D, hp, dm, hm in _jobs(case):
        z1, zi = CL.zero_fit_first_order(case, D, hp), CL.zero_fit(case, hp)
        rows.append(dict(id=case['id'], stratum=case['stratum'], Delta=str(D), h_p=str(hp), dm=dm, hm=hm,
                         G_S_CL_pred1=z1['G_S_CL_pred1'], G_S_CL_pred_inf=zi['G_S_CL_pred'],
                         p_old=z1['old']['p'], p_new=z1['new']['p']))
    return rows


def predict(workers):
    if PRED.exists():
        raise FileExistsError(PRED)
    with multiprocessing.get_context('fork').Pool(workers) as p:
        rows = [r for rs in p.map(_pred, json.loads(CASES.read_text())) for r in rs]
    with PRED.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()} for r in rows)
    print(len(rows), 'prediction rows')


def table(run):
    P = {(r['id'], r['Delta'], r['h_p']): r for r in csv.DictReader(PRED.open())}
    out = []
    for f in sorted(Path(run).glob('*.json')):
        j = json.loads(f.read_text())
        if j.get('status') != 'COMPLETED':
            out.append(dict(id=j['id'], status=j.get('status')))
            continue
        p = P[(j['id'], j['Delta'], j['h_p'])]
        J = {k: v['J'] for k, v in j['cells'].items()}
        sc = 100 / J['11']
        out.append(dict(id=j['id'], status='COMPLETED', stratum=p['stratum'], dm=p['dm'], hm=p['hm'],
                        G_S_CL=sc * (J['00'] - J['10']), pred1=sc * float(p['G_S_CL_pred1']),
                        pred_inf=sc * float(p['G_S_CL_pred_inf']), G_M_CL=sc * (J['00'] - J['01']),
                        Gamma_CL=sc * (J['10'] + J['01'] - J['00'] - J['11']),
                        static_regret=sc * (j['J_static'] - J['11']), one_shot_G_S=j['one_shot']['G_S'],
                        p00=j['cells']['00']['p'], p10=j['cells']['10']['p'], p11=j['cells']['11']['p']))
    return out


def score(run):
    T = table(run)
    ok = [r for r in T if r['status'] == 'COMPLETED']
    n_all = len(json.loads(CASES.read_text())) * len(GRIDV)
    tol = lambda r: max(0.1, 0.05 * abs(r['pred1']))
    long = [r for r in ok if F(r['dm']) >= 3]
    A1 = sum(abs(r['G_S_CL'] - r['pred1']) <= tol(r) for r in long) / len(long)
    d10 = [r for r in ok if r['dm'] == '10' and abs(r['pred1']) >= 0.25]
    A2 = sum((r['G_S_CL'] > 0) == (r['pred1'] > 0) for r in d10) / len(d10) if d10 else None
    diag10 = [r for r in ok if r['dm'] == '10' and r['hm'] == '10']
    harm_os = [r for r in diag10 if r['one_shot_G_S'] <= -0.25]
    res = dict(completed=len(ok), of=n_all,
               A1=dict(n=len(long), share=A1, threshold=0.9,
                       verdict='INCONCLUSIVE' if len(ok) < 0.9 * n_all else ('PASS' if A1 >= 0.9 else 'FAIL')),
               A2=dict(n=len(d10), share=A2, threshold=0.9,
                       verdict='NOT_EVALUABLE' if len(d10) < 5 else ('PASS' if A2 >= 0.9 else 'FAIL')),
               descriptive=dict(
                   open_loop_harm_rows=len(harm_os), closed_loop_harm_kept=sum(r['G_S_CL'] <= -0.25 for r in harm_os),
                   by_grid={f"{dm}|{hm}": dict(n=len(g), median_G_S_CL=st.median(r['G_S_CL'] for r in g),
                                               harm=sum(r['G_S_CL'] <= -0.25 for r in g), help=sum(r['G_S_CL'] >= 0.25 for r in g),
                                               within_tol_pred1=sum(abs(r['G_S_CL'] - r['pred1']) <= tol(r) for r in g) / len(g))
                            for dm, hm in GRIDV for g in [[r for r in ok if r['dm'] == dm and r['hm'] == hm]] if g}))
    (OUT / 'score.json').write_text(json.dumps(res, indent=1) + '\n')
    with (OUT / 'table.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(ok[0]))
        w.writeheader()
        w.writerows(ok)
    print(json.dumps({k: v for k, v in res.items() if k != 'descriptive'}, indent=1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['design', 'predict', 'score'])
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--run')
    a = ap.parse_args()
    design() if a.cmd == 'design' else predict(a.workers) if a.cmd == 'predict' else score(a.run)
