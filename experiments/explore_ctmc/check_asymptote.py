"""Doan Van Tai — score PREDICTIONS_asymptote.md exactly as locked [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.check_asymptote    # -> results/explore_ctmc/score_asymptote.json
"""
from fractions import Fraction as F
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'


def load(stage):
    recs, bad = [], []
    for f in sorted((OUT / 'runs' / stage).glob('*.json')):
        d = json.loads(f.read_text())
        if d['status'] != 'COMPLETED':
            bad.append(d['id'])
            continue
        lamA, lamB = (float(F(x)) for x in d['parameters'][:2])
        for r in d['h']:
            recs.append(dict(stage=stage, id=d['id'], h=r['h'], h_kappa=r['h_kappa'], h_Tint=r['h_Tint'],
                             delta=lamB - lamA, P=r['h_kappa'] * abs(lamB - lamA), z=r['G_S'], S=r['S'], M=r['M'],
                             G_S_hybrid=r['G_S_hybrid'], regret_static=r['regret']['static'],
                             regret_M0_new=r['regret']['M0_new'], z_inf_run=d['asymptotic']['z_inf'],
                             M_pred_run=d['asymptotic']['M0_regret_new_pred']))
    return pd.DataFrame(recs), bad


def verdict(ok, n):
    return 'INCONCLUSIVE' if n == 0 else ('PASS' if ok else 'FAIL')


def frac(mask):
    return float(np.mean(mask)) if len(mask) else float('nan')


def main():
    A, badA = load('asym')
    X, badX = load('xslice')
    P, badP = load('pslice')
    frozen = pd.read_csv(OUT / 'PREDICTIONS_asymptote_numbers.csv', dtype={'h': str})
    A = A.merge(frozen[['id', 'h', 'z_inf', 'z_pred_first_order', 'M_pred_new']], on=['id', 'h'], how='left')
    consistency = dict(z_inf=float((A.z_inf - A.z_inf_run).abs().max()), M_pred=float((A.M_pred_new - A.M_pred_run).abs().max()),
                       missing_frozen=int(A.z_pred_first_order.isna().sum()))
    out = {}
    last = A.loc[A.groupby('id').h_Tint.idxmax()]
    ok = (abs(last.z - last.z_inf) <= 0.1 + 0.1 * abs(last.z_inf))
    out['AS-T1'] = dict(label='toán', n=len(last), value=frac(ok), verdict=verdict(ok.all(), len(last)),
                        worst=last.assign(err=abs(last.z - last.z_inf))[['id', 'h', 'z', 'z_inf', 'err']]
                        .sort_values('err').tail(3).to_dict('records'))
    m = A[A.h_Tint >= 3]
    hit = abs(m.z - m.z_pred_first_order) <= 0.1
    out['AS-R1a'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.9, verdict=verdict(frac(hit) >= 0.9, len(m)))
    m = A[(A.h_Tint >= 1) & (A.h_Tint < 3)]
    hit = abs(m.z - m.z_pred_first_order) <= 0.1 + 0.1 * abs(m.z)
    out['AS-R1b'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.7, verdict=verdict(frac(hit) >= 0.7, len(m)))
    m = A[A.h_Tint >= 10]
    out['AS-T2'] = dict(label='toán', n=len(m), value=frac(m.S <= 0.5), threshold=0.9, verdict=verdict(frac(m.S <= 0.5) >= 0.9, len(m)))
    out['AS-T3'] = dict(label='toán', n=len(m), value=frac(m.regret_static <= 0.5), threshold=0.9,
                        verdict=verdict(frac(m.regret_static <= 0.5) >= 0.9, len(m)))
    m = A[(A.h_Tint >= 10) & (A.M_pred_new >= 1)]
    hit = abs(m.M - m.M_pred_new) <= 0.15 * m.M_pred_new
    out['AS-R2a'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.9, verdict=verdict(frac(hit) >= 0.9, len(m)))
    hit = m.M < m.M_pred_new
    out['AS-R2b'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.8, verdict=verdict(frac(hit) >= 0.8, len(m)))
    allr = pd.concat([A, X, P], ignore_index=True)
    m = allr[(allr.z < -0.5) & (allr.P >= 10)]
    hit = m.G_S_hybrid >= -0.1
    out['AS-R3'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.9, verdict=verdict(frac(hit) >= 0.9, len(m)),
                        by_stage=m.assign(hit=hit).groupby('stage').hit.agg(['size', 'mean']).round(3).to_dict())
    m = A[abs(A.z_inf) >= 0.5]
    rel = abs(m.z - m.z_inf) / abs(m.z_inf)
    rT, rK = spearmanr(rel, m.h_Tint)[0], spearmanr(rel, m.h_kappa)[0]
    out['AS-R4'] = dict(label='rủi ro', n=len(m), spearman_h_Tint=float(rT), spearman_h_kappa=float(rK),
                        verdict=verdict(rT <= rK - 0.1, len(m)))
    per = []
    for rid, g in A[A.delta != 0].groupby('id'):
        late = g[g.h_Tint >= 3]
        early = g.loc[[(g.h_Tint - 1 / 3).abs().idxmin()]]
        per.append(dict(id=rid, late_static_wins=bool((late.regret_static < late.regret_M0_new).all()) if len(late) else None,
                        early_M0_wins=bool((early.regret_M0_new < early.regret_static).all())))
    per = pd.DataFrame(per)
    late = per.late_static_wins.dropna()
    out['AS-R5a'] = dict(label='rủi ro', n=len(late), value=frac(late.astype(bool)), threshold=0.9,
                         verdict=verdict(frac(late.astype(bool)) >= 0.9, len(late)))
    out['AS-R5b'] = dict(label='rủi ro', n=len(per), value=frac(per.early_M0_wins), threshold=0.5,
                         verdict=verdict(frac(per.early_M0_wins) >= 0.5, len(per)))
    risky = [k for k, v in out.items() if v['label'] == 'rủi ro']
    summary = dict(risky_pass=sum(out[k]['verdict'] == 'PASS' for k in risky),
                   risky_fail=sum(out[k]['verdict'] == 'FAIL' for k in risky),
                   risky_inconclusive=sum(out[k]['verdict'] == 'INCONCLUSIVE' for k in risky), risky_total=len(risky))
    table = A[['id', 'h', 'h_Tint', 'h_kappa', 'z', 'z_pred_first_order', 'z_inf', 'S', 'M', 'M_pred_new', 'regret_static',
               'regret_M0_new', 'G_S_hybrid']].round(5).to_dict('records')
    result = dict(predictions=out, summary=summary, consistency=consistency,
                  unresolved=dict(asym=badA, xslice=badX, pslice=badP), table=table)
    (OUT / 'score_asymptote.json').write_text(json.dumps(result, indent=1, default=str) + '\n')
    for k, v in out.items():
        print(f"{k:7s} {v['label']:8s} n={v['n']:4d} {v['verdict']:12s}",
              {kk: vv for kk, vv in v.items() if kk in ('value', 'threshold', 'spearman_h_Tint', 'spearman_h_kappa')})
    print('risky:', summary, 'consistency:', consistency)


if __name__ == '__main__':
    main()
