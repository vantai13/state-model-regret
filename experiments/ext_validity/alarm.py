"""Doan Van Tai — EV-B: decisions triggered by an alarm on the stale backlog (THREATS K5), exact on ctmc-v1
[EXTERNAL VALIDITY; AI (Claude) theo ủy quyền 14/11/2026].

The one-shot pipelines of the contract are unchanged; only the population changes: the decision is taken only when the
old backlog of the Stay path A is at or above its stationary q90 (alarm probability ~10%). Path B is unconditioned.
Everything is exact: the alarm weights of path A are pi_A * 1[n >= y*] pushed through e^{Q tau}.

    python -m experiments.ext_validity.alarm design     # fresh panel (write-once)
    python -m experiments.ext_validity.alarm predict    # zero-fit law under the alarm (M0 + stationary only)
    python -m experiments.ext_validity.alarm truth --workers N
    python -m experiments.ext_validity.alarm score
"""
import argparse
import csv
import json
import math
import multiprocessing
import statistics as st
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import expm_multiply

from experiments.explore_ctmc import ctmc as C

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/ext_validity/ev_b'
CASES, PRED, TRUTH = OUT / 'cases.json', OUT / 'predictions.csv', OUT / 'truth.csv'
SEED = 20261151
COUNTS = dict(neg=10, band=10, pos=10)
H_MULT = (F(1), F(3), F(10))
Q_ALARM = 0.90
N_MAX = 2500


def design():
    from scipy.stats import qmc
    from experiments.explore_ctmc import design_l75 as L75, tau as T5
    from experiments.explore_ctmc.design import rational
    from experiments.explore_ctmc.csw_harm import seen_all
    if CASES.exists():
        raise FileExistsError(CASES)
    seen = seen_all() | {tuple(F(x) for x in c['parameters'][:4])
                         for c in json.loads((ROOT / 'results/explore_ctmc/csw_harm/cases_csw_harm.json').read_text())}
    out = []
    for k, name in enumerate(COUNTS):
        lo, hi = L75.STRATA[name]
        acc = []
        for pu, pa, px, pk in qmc.Sobol(4, scramble=True, seed=SEED + k).random(2048):
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
            if max(NA, NB) > N_MAX:
                continue
            seen.add(key)
            acc.append(dict(id=f'B{name[0].upper()}{len(acc):02d}', stratum=name, x=float(x), T_int_max=Tm,
                            parameters=[str(v) for v in key], hs=[str(rational(m * Tm)) for m in H_MULT]))
        out += acc
    OUT.mkdir(parents=True, exist_ok=True)
    CASES.write_text(json.dumps(out, indent=1) + '\n')
    print(len(out), 'cases')


def _setup(case):
    lamA, lamB, u, kappa = (F(x) for x in case['parameters'])
    NA, NB = (C.choose_N(lam + u, kappa) for lam in (lamA, lamB))
    Ast, Asw = C.chain(lamA + u, kappa, NA), C.chain(lamA, kappa, NA)
    Bst, Bsw = C.chain(lamB, kappa, NB), C.chain(lamB + u, kappa, NB)
    pA = Ast.pi.reshape(-1, 2).sum(axis=1)
    tail = np.cumsum(pA[::-1])[::-1]                       # P(n >= y)
    ystar = int(np.argmax(tail <= 1 - Q_ALARM))            # smallest y with P(n >= y) <= 0.10
    mask = (np.repeat(np.arange(NA + 1), 2) >= ystar).astype(float)
    Palarm = float(Ast.pi @ mask)
    wA = expm_multiply(Ast.Q.T * float(C.TAU), Ast.pi * mask) / Palarm     # law of x_A at t0 given the alarm
    pAal = np.where(np.arange(NA + 1) >= ystar, pA, 0.0) / Palarm          # law of the old backlog given the alarm
    return dict(lamA=lamA, lamB=lamB, u=u, kappa=kappa, NA=NA, NB=NB, Ast=Ast, Asw=Asw, Bst=Bst, Bsw=Bsw,
                ystar=ystar, Palarm=Palarm, wA=wA, pAal=pAal, wB=Bst.pi, pB=Bst.pi.reshape(-1, 2).sum(axis=1))


def predict_one(case):
    """Zero-fit first-order law (as ctmc.evaluate_m0) with the alarm weights on path A; no V, no true gap."""
    S = _setup(case)
    hs = [F(h) for h in case['hs']]
    hf = [float(h) for h in hs]
    dhA = C.m0_gap(S['lamA'], S['u'], S['kappa'], S['NA'], hf, 'A')
    dhB = C.m0_gap(S['lamB'], S['u'], S['kappa'], S['NB'], hf, 'B')
    bA, bB = S['Asw'].g - S['Ast'].g, S['Bsw'].g - S['Bst'].g
    postA = C.posterior_mean(S['Ast'], np.column_stack([dhA.T, bA]))
    postB = C.posterior_mean(S['Bst'], np.column_stack([dhB.T, bB]))
    s = (S['Asw'].r + S['Bsw'].r) - (S['Ast'].r + S['Bst'].r)
    rows = []
    for k, (h, hm) in enumerate(zip(hf, H_MULT)):
        new = C.pair_sum(S['wA'], dhA[k], bA, S['wB'], dhB[k], bB, 0.0, 1e-12)
        old = C.pair_sum(S['pAal'], postA[:, k], postA[:, -1], S['pB'], postB[:, k], postB[:, -1], 0.0, 1e-12)
        rows.append(dict(id=case['id'], stratum=case['stratum'], h=case['hs'][k], h_mult=str(hm), ystar=S['ystar'],
                         P_alarm=S['Palarm'], G_S_pred_abs=h * s * (old[0] - new[0]) + old[1] - new[1],
                         F_old=old[0], F_new=new[0], s=s))
    return rows


def truth_one(case):
    """Exact one-shot cells under the alarm population (same decision maps as the contract)."""
    S = _setup(case)
    hs = [F(h) for h in case['hs']]
    ev = C.evaluate(S['lamA'], S['lamB'], S['u'], S['kappa'], hs, disagree=False, arrays=True)
    ar = ev.pop('_arrays')
    VA, VB = S['Ast'].V(hs), S['Bst'].V(hs)
    rows = []
    for k, (h, hm) in enumerate(zip(hs, H_MULT)):
        tol = 1e-12 * (float(h) * 20 + 1)
        dA, dhA, dAo, dhAo = ar['dA'][k], ar['dhA'][k], ar['dAo'][k], ar['dhAo'][k]
        dB, dhB, dBo, dhBo = ar['dB'][k], ar['dhB'][k], ar['dBo'][k], ar['dhBo'][k]
        fresh = lambda kA, kB: C.pair_sum(S['wA'], kA, dA, S['wB'], kB, dB, 0.0, tol)[1]
        stale = lambda kA, kB: C.pair_sum(S['pAal'], kA, dAo, S['pB'], kB, dBo, 0.0, tol)[1]
        G11, G10, G01, G00 = fresh(dA, dB), fresh(dhA, dhB), stale(dAo, dBo), stale(dhAo, dhBo)
        Estay = float(S['wA'] @ VA[k] + S['wB'] @ VB[k])
        Cref = Estay + G11
        pct = lambda v: 100 * v / Cref
        er = ev['h'][k]
        rows.append(dict(id=case['id'], stratum=case['stratum'], h=case['hs'][k], h_mult=str(hm), Cref=Cref,
                         G_S_abs=G00 - G10, G_S=pct(G00 - G10), G_M=pct(G00 - G01), Gamma=pct(G10 + G01 - G00 - G11),
                         G_S_uncond=er['G_S'], hybrid_uncond=er['G_S_hybrid']))
    return rows


def _write(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()} for r in rows)


def _pool(fn, workers):
    cases = json.loads(CASES.read_text())
    with multiprocessing.get_context('fork').Pool(workers) as pool:
        return [r for rs in pool.map(fn, cases) for r in rs]


def score():
    P = {(r['id'], r['h_mult']): r for r in csv.DictReader(PRED.open())}
    T = list(csv.DictReader(TRUTH.open()))
    rec = []
    for t in T:
        p = P[(t['id'], t['h_mult'])]
        Cref = float(t['Cref'])
        rec.append(dict(id=t['id'], stratum=t['stratum'], hm=float(F(t['h_mult'])), G_S=float(t['G_S']),
                        pred=100 * float(p['G_S_pred_abs']) / Cref, G_S_uncond=float(t['G_S_uncond'])))
    long = [r for r in rec if r['hm'] == 10]
    tol = lambda r: max(0.1, 0.05 * abs(r['pred']))
    B1 = sum(abs(r['G_S'] - r['pred']) <= tol(r) for r in long) / len(long)
    sig = [r for r in long if abs(r['pred']) >= 0.25]
    B2 = sum((r['G_S'] > 0) == (r['pred'] > 0) for r in sig) / len(sig) if sig else None
    harm_u = [r for r in long if r['G_S_uncond'] <= -0.25]
    out = dict(
        B1=dict(n=len(long), share=B1, threshold=0.9, verdict='PASS' if B1 >= 0.9 else 'FAIL'),
        B2=dict(n=len(sig), sign_agree=B2, threshold=0.9,
                verdict='NOT_EVALUABLE' if len(sig) < 5 else ('PASS' if B2 >= 0.9 else 'FAIL')),
        descriptive=dict(
            harm_rows_uncond=len(harm_u),
            harm_kept_under_alarm=sum(r['G_S'] <= -0.25 for r in harm_u),
            median_G_S_alarm_vs_uncond=[st.median(r['G_S'] for r in harm_u), st.median(r['G_S_uncond'] for r in harm_u)]
            if harm_u else None,
            h3_within_tol=sum(abs(r['G_S'] - r['pred']) <= tol(r) for r in rec if r['hm'] == 3) / max(1, sum(r['hm'] == 3 for r in rec))))
    (OUT / 'score.json').write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['design', 'predict', 'truth', 'score'])
    ap.add_argument('--workers', type=int, default=6)
    a = ap.parse_args()
    if a.cmd == 'design':
        design()
    elif a.cmd == 'predict':
        if PRED.exists():
            raise FileExistsError(PRED)
        _write(PRED, _pool(predict_one, a.workers))
    elif a.cmd == 'truth':
        if TRUTH.exists():
            raise FileExistsError(TRUTH)
        if not (OUT / 'lock.json').exists():
            raise RuntimeError('predictions are not locked')
        _write(TRUTH, _pool(truth_one, a.workers))
    else:
        score()


if __name__ == '__main__':
    main()
