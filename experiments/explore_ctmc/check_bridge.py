"""Doan Van Tai — score PREDICTIONS_bridge.md exactly as locked [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.check_bridge    # -> results/explore_ctmc/score_bridge.json
"""
from fractions import Fraction as F
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
FLUID = ROOT / 'results/explore_mech/sobol4/metrics.csv'


def load(stage):
    recs, bad = [], []
    for f in sorted((OUT / 'runs' / stage).glob('*.json')):
        d = json.loads(f.read_text())
        if d['status'] != 'COMPLETED':
            bad.append(d['id'])
            continue
        lamA, lamB, u, kappa, c = (F(x) for x in d['parameters'])
        for r in d['h']:
            recs.append(dict(stage=stage, id=d['id'], sobol4=d['tags'].get('sobol4'), lamA=float(lamA), lamB=float(lamB),
                             u=float(u), kappa=float(kappa), delta=float(lamB - lamA), x=d['x'], h=float(F(r['h'])),
                             h_kappa=r['h_kappa'], h_Tint=r['h_Tint'], P=r['h_kappa'] * abs(float(lamB - lamA)),
                             S=r['S'], M=r['M'], G_S=r['G_S'], G_M=r['G_M'], G_SM=r['G_SM'], Gamma=r['Gamma'],
                             z_inf=d['asymptotic']['z_inf'], s=d['s'], r_min=d['r_min'],
                             share_truth_new=r['shares']['M1_new'], static_share=r['shares']['static'],
                             tags=d['tags']))
    return pd.DataFrame(recs), bad


def best_threshold(values, labels):
    best = (0.0, None)
    for t in np.unique(np.quantile(values, np.linspace(0.01, 0.99, 197))):
        acc = max(((values < t) == labels).mean(), ((values >= t) == labels).mean())
        if acc > best[0]:
            best = (float(acc), float(t))
    return best


def verdict(ok, n):
    return 'INCONCLUSIVE' if n == 0 else ('PASS' if ok else 'FAIL')


def frac(mask):
    return float(mask.mean()) if len(mask) else float('nan')


def main():
    stages = {s: load(s) for s in ('bridge', 'xslice', 'pslice')}
    unresolved = {s: v[1] for s, v in stages.items()}
    B, X, P = (stages[s][0] for s in ('bridge', 'xslice', 'pslice'))
    allr = pd.concat([B, X, P], ignore_index=True)
    fl = pd.read_csv(FLUID).set_index('id')
    Bf = B.join(fl[['arith', 'S', 'M', 'G_S', 'Gamma']].add_suffix('_f'), on='sobol4')
    Bf = Bf[Bf.arith_f == True]
    out = {}

    id_err = np.maximum.reduce([abs(allr.G_SM - allr.G_S - allr.M), abs(allr.G_SM - allr.G_M - allr.S),
                                abs(allr.Gamma - allr.S + allr.G_S)])
    neg = allr[['S', 'M', 'G_M']].min(axis=1)
    out['BR-G1'] = dict(label='toán', n=len(allr), max_identity_err=float(id_err.max()), min_SMGM=float(neg.min()),
                        verdict=verdict((id_err <= 1e-9).all() and (neg >= -1e-9).all(), len(allr)))
    zero, nz = allr[allr.delta == 0], allr[allr.delta != 0]
    ok = ((zero.s == 0) & (zero.static_share == 0)).all() and ((nz.s < 0) == (nz.lamB < nz.lamA)).all()
    out['BR-G2'] = dict(label='toán', n=len(allr), verdict=verdict(ok, len(allr)))

    m = Bf[abs(Bf.G_S_f) >= 0.5]
    agree = np.sign(m.G_S) == np.sign(m.G_S_f)
    out['BR-R1'] = dict(label='rủi ro', n=len(m), value=frac(agree), threshold=0.75, verdict=verdict(frac(agree) >= 0.75, len(m)),
                        by_kappa={str(k): round(float(v), 3) for k, v in agree.groupby(pd.cut(m.kappa, [0, .05, .2, 1, 5, 21]), observed=True).mean().items()})
    m = Bf[((Bf.S + Bf.M) >= 0.5) & ((Bf.S_f + Bf.M_f) >= 0.5)]
    agree = (m.S > m.M) == (m.S_f > m.M_f)
    out['BR-R2'] = dict(label='rủi ro', n=len(m), value=frac(agree), threshold=0.8, verdict=verdict(frac(agree) >= 0.8, len(m)))

    m = B[(B.S + B.M) >= 0.5]
    y = (m.S > m.M).values
    accs = {name: best_threshold(m[col].values, y) for name, col in (('P', 'P'), ('h_kappa', 'h_kappa'),
                                                                       ('h_Tint', 'h_Tint'))}
    hs = (m.h * abs(m.s) / m.r_min).values
    accs['h_s_over_rmin'] = best_threshold(hs, y)
    ok = accs['P'][0] >= 0.85 and accs['P'][0] >= accs['h_kappa'][0] + 0.03 and 5 <= (accs['P'][1] or 0) <= 30
    out['BR-R3'] = dict(label='rủi ro', n=len(m), base_rate=float(y.mean()) if len(y) else None,
                        accuracy={k: dict(acc=v[0], threshold=v[1]) for k, v in accs.items()}, verdict=verdict(ok, len(m)))

    big = allr[(allr.P >= 30) & ((allr.S + allr.M) >= 0.5)]
    for key, mask, col, thr, op in (('BR-R4a', big.x < 0, 'G_S', 0.9, 'lt'), ('BR-R4b', big.x > 0.5, 'G_S', 0.9, 'lt'),
                                    ('BR-R4c', (big.x > 0) & (big.x <= 0.5), 'Gamma', 0.4, 'gamma')):
        s = big[mask]
        hit = (s.G_S < -0.1) if op == 'lt' else (s.Gamma < 0)
        out[key] = dict(label='rủi ro', n=len(s), value=frac(hit), threshold=thr, verdict=verdict(frac(hit) >= thr, len(s)))

    xs = X[X.h_kappa.round(6) == 150]
    series = {}
    for (u, k), g in xs.groupby(['u', 'kappa']):
        helped = g[g.G_S > 0.1]
        series[f'u{u}_k{k}'] = float(helped.x.max()) if len(helped) else None
    ok = all(v is None or v <= 0.35 for v in series.values())
    out['BR-R5'] = dict(label='rủi ro', n=len(series), largest_x_with_GS_gt_0_1=series, threshold=0.35,
                        verdict=verdict(ok, len(series)))

    m = B[B.delta == 0]
    out['BR-R6'] = dict(label='rủi ro', n=len(m), value=frac(m.M <= 0.3), threshold=0.95,
                        verdict=verdict(frac(m.M <= 0.3) >= 0.95, len(m)))
    m = Bf[Bf.kappa <= 0.05]
    med_c, med_f = float((m.S + m.M).median()), float((m.S_f + m.M_f).median())
    out['BR-R7'] = dict(label='rủi ro', n=len(m), median_ctmc=med_c, median_fluid=med_f, verdict=verdict(med_c < med_f, len(m)))

    XP = pd.concat([X, P], ignore_index=True)
    m = XP[(XP.h_Tint >= 3) & (abs(XP.delta) >= 0.5)]
    hit = np.where(m.delta < 0, m.share_truth_new >= 0.9, m.share_truth_new <= 0.1)
    out['BR-R8'] = dict(label='rủi ro', n=len(m), value=frac(pd.Series(hit)), threshold=0.9,
                        verdict=verdict(frac(pd.Series(hit)) >= 0.9, len(m)))
    m = XP[(XP.h_Tint >= 3) & (abs(XP.z_inf) >= 0.25)]
    hit = np.sign(m.G_S) == np.sign(m.z_inf)
    out['BR-T1'] = dict(label='toán + onset rủi ro', n=len(m), value=frac(hit), threshold=0.9,
                        verdict=verdict(frac(hit) >= 0.9, len(m)))

    desc = {}
    for name, g in (('bridge', B), ('xslice', X), ('pslice', P)):
        desc[name] = dict(n=len(g), kappa_strata=g.groupby(pd.cut(g.kappa, [0, .05, .2, 1, 5, 21]), observed=True)
                          .agg(n=('S', 'size'), S_med=('S', 'median'), M_med=('M', 'median'), GS_neg=('G_S', lambda v: float((v < -0.1).mean())))
                          .round(4).reset_index().astype(str).to_dict('records'))
    risky = [k for k, v in out.items() if v['label'] == 'rủi ro']
    summary = dict(risky_pass=sum(out[k]['verdict'] == 'PASS' for k in risky),
                   risky_fail=sum(out[k]['verdict'] == 'FAIL' for k in risky),
                   risky_inconclusive=sum(out[k]['verdict'] == 'INCONCLUSIVE' for k in risky), risky_total=len(risky))
    result = dict(predictions=out, summary=summary, unresolved=unresolved, descriptive=desc)
    (OUT / 'score_bridge.json').write_text(json.dumps(result, indent=1, default=str) + '\n')
    for k, v in out.items():
        print(f"{k:7s} {v['label']:20s} n={v['n']:5d} {v['verdict']:12s}",
              {kk: vv for kk, vv in v.items() if kk in ('value', 'threshold', 'median_ctmc', 'median_fluid', 'largest_x_with_GS_gt_0_1')})
    print('risky:', summary, 'unresolved:', {k: len(v) for k, v in unresolved.items()})


if __name__ == '__main__':
    main()
