"""Doan Van Tai — score PREDICTIONS_d22.md exactly as locked [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.check_d22    # -> results/explore_ctmc/score_d22.json
"""
from fractions import Fraction as F
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
STAGES = ('d22_bridge', 'd22_xslice', 'd22_pslice', 'd22_asym', 'd22_wide', 'd22_wide_rest')


def verdict(ok, n):
    return 'INCONCLUSIVE' if n == 0 else ('PASS' if ok else 'FAIL')


def frac(mask):
    return float(np.mean(mask)) if len(mask) else float('nan')


def load():
    recs, bad = [], []
    for stage in STAGES:
        for f in sorted((OUT / 'runs_d22' / stage).glob('*.json')):
            d = json.loads(f.read_text())
            if d['status'] != 'COMPLETED':
                bad.append((stage, d['id'], d['status']))
                continue
            kappa = float(F(d['parameters'][3]))
            for r in d['h']:
                dd = r['d22']
                recs.append(dict(stage=stage, id=d['id'], h=r['h'], h_Tint=r['h_Tint'], kappa=kappa, x=d['x'],
                                 G_S=r['G_S'], S=r['S'], F=dd['F'], V=dd['V'], F1=dd['F1'], V1=dd['V1'],
                                 regret_cb0=dd['regret_cb0'], regret_static=r['regret']['static'],
                                 dropped=dd['dropped_mass'], flags=len(r.get('flags', []))))
    return pd.DataFrame(recs), bad


def main():
    d, bad = load()
    frozen = pd.read_csv(OUT / 'PREDICTIONS_d22_numbers.csv', dtype={'h': str})
    d = d.merge(frozen[['stage', 'id', 'h', 'z_inf', 'z_F_inf', 'z_V_inf']], on=['stage', 'id', 'h'], how='left')
    out = {}
    ident = np.maximum(abs(d.F + d.V - d.G_S), abs(d.F1 + d.V1 - d.S))
    ok = (ident <= 1e-9).all() and (d[['F1', 'V1']].min(axis=1) >= -1e-9).all() and (d.dropped <= 1e-12).all()
    out['D-T1'] = dict(label='toán', n=len(d), max_identity_err=float(ident.max()), min_F1V1=float(d[['F1', 'V1']].min().min()),
                       max_dropped=float(d.dropped.max()), verdict=verdict(ok, len(d)))
    m = d[d.h_Tint >= 10]
    hit = (abs(m.F - m.z_F_inf) <= 0.1 + 0.1 * abs(m.z_F_inf)) & (abs(m.V - m.z_V_inf) <= 0.1 + 0.1 * abs(m.z_V_inf))
    out['D-T2'] = dict(label='toán + onset', n=len(m), value=frac(hit), threshold=0.9, verdict=verdict(frac(hit) >= 0.9, len(m)))
    harm = d[d.G_S < -0.5]
    hit = harm.F < -0.1
    out['D-R1'] = dict(label='rủi ro', n=len(harm), value=frac(hit), threshold=0.8, verdict=verdict(frac(hit) >= 0.8, len(harm)))
    m = harm[(harm.h_Tint >= 3) & (abs(harm.z_inf) >= 0.5)]
    hit = abs(m.F / m.G_S - m.z_F_inf / m.z_inf) <= 0.1
    out['D-R2'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.8, verdict=verdict(frac(hit) >= 0.8, len(m)))
    m = harm[harm.h_Tint < 1]
    hit = m.F < 0
    out['D-R3'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.7, verdict=verdict(frac(hit) >= 0.7, len(m)))
    m = d[d.S >= 0.5]
    hit = m.F1 >= m.V1
    out['D-R4'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.7, verdict=verdict(frac(hit) >= 0.7, len(m)),
                       by_kappa={str(k): round(float(v), 3) for k, v in
                                 hit.groupby(pd.cut(m.kappa, [0, .05, .2, 1, 5, 21]), observed=True).mean().items()})
    m = d[d.h_Tint >= 3]
    hit = m.regret_static <= m.regret_cb0
    out['D-R5'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.9, verdict=verdict(frac(hit) >= 0.9, len(m)))
    risky = [k for k, v in out.items() if v['label'] == 'rủi ro']
    summary = dict(risky_pass=sum(out[k]['verdict'] == 'PASS' for k in risky),
                   risky_fail=sum(out[k]['verdict'] == 'FAIL' for k in risky),
                   risky_inconclusive=sum(out[k]['verdict'] == 'INCONCLUSIVE' for k in risky), risky_total=len(risky))
    desc = d.assign(hT=pd.cut(d.h_Tint, [0, 0.3, 1, 3, 10, 1e9]), harm=d.G_S < -0.5).groupby(['hT', 'harm'], observed=True) \
        .agg(n=('id', 'size'), med_G_S=('G_S', 'median'), med_F=('F', 'median'), med_V=('V', 'median'),
             med_S=('S', 'median'), med_F1=('F1', 'median'), med_V1=('V1', 'median')).round(4).reset_index().astype(str) \
        .to_dict('records')
    result = dict(predictions=out, summary=summary, unresolved=bad, missing_frozen=int(d.z_F_inf.isna().sum()),
                  descriptive=desc, n_rows=len(d))
    (OUT / 'score_d22.json').write_text(json.dumps(result, indent=1, default=str) + '\n')
    for k, v in out.items():
        print(f"{k:5s} {v['label']:13s} n={v['n']:5d} {v['verdict']:12s}",
              {kk: vv for kk, vv in v.items() if kk in ('value', 'threshold', 'by_kappa', 'max_identity_err')})
    print('risky:', summary, 'unresolved:', len(bad), 'missing frozen:', result['missing_frozen'])
    print(pd.DataFrame(desc).to_string())


if __name__ == '__main__':
    main()
