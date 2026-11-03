"""Doan Van Tai — score PREDICTIONS_csw.md exactly as locked [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.check_csw    # -> results/explore_ctmc/score_csw.json
"""
from fractions import Fraction as F
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'


def verdict(ok, n):
    return 'INCONCLUSIVE' if n == 0 else ('PASS' if ok else 'FAIL')


def frac(mask):
    return float(np.mean(mask)) if len(mask) else float('nan')


def main():
    recs, bad = [], []
    for f in sorted((OUT / 'runs' / 'csw').glob('*.json')):
        d = json.loads(f.read_text())
        if d['status'] != 'COMPLETED':
            bad.append(d['id'])
            continue
        for r in d['h']:
            recs.append(dict(id=d['id'], base=d['id'].rsplit('_', 1)[0], arm=d['id'].rsplit('_', 1)[1], h=r['h'],
                             h_Tint=r['h_Tint'], z=r['G_S'], G_S_hybrid=r['G_S_hybrid'], z_inf_run=d['asymptotic']['z_inf']))
    d = pd.DataFrame(recs)
    frozen = pd.read_csv(OUT / 'PREDICTIONS_csw_numbers.csv', dtype={'h': str})
    d = d.merge(frozen[['id', 'h', 'z_inf', 'z_pred_first_order']], on=['id', 'h'], how='left')
    out = {}
    last = d.loc[d.groupby('id').h_Tint.idxmax()]
    ok = abs(last.z - last.z_inf) <= 0.1 + 0.1 * abs(last.z_inf)
    out['F-T1'] = dict(label='toán', n=len(last), value=frac(ok), verdict=verdict(ok.all(), len(last)))
    m = d[d.h_Tint >= 3]
    hit = abs(m.z - m.z_pred_first_order) <= 0.1
    out['F-R1'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.9, verdict=verdict(frac(hit) >= 0.9, len(m)))
    c = d[d.arm == 'c']
    out['F-R2'] = dict(label='rủi ro', n=len(c), value=frac(c.z >= -0.25), threshold=0.9, min_z=float(c.z.min()),
                       verdict=verdict(frac(c.z >= -0.25) >= 0.9, len(c)))
    m = c[c.h_Tint < 3]
    out['F-R3'] = dict(label='rủi ro', n=len(m), value=frac(m.z > 0), threshold=0.7, verdict=verdict(frac(m.z > 0) >= 0.7, len(m)))
    pair = c.merge(d[d.arm == 'c0'][['base', 'h', 'z']], on=['base', 'h'], suffixes=('', '_0'))
    m = pair[pair.h_Tint >= 3]
    out['F-R4'] = dict(label='toán + onset', n=len(m), value=frac(m.z < m.z_0), threshold=0.9,
                       verdict=verdict(frac(m.z < m.z_0) >= 0.9, len(m)))
    m = d[d.z < -0.1]
    out['F-R5'] = dict(label='rủi ro', n=len(m), value=frac(m.G_S_hybrid >= -0.1), threshold=0.95,
                       verdict=verdict(frac(m.G_S_hybrid >= -0.1) >= 0.95, len(m)))
    risky = [k for k, v in out.items() if v['label'] == 'rủi ro']
    summary = dict(risky_pass=sum(out[k]['verdict'] == 'PASS' for k in risky),
                   risky_fail=sum(out[k]['verdict'] == 'FAIL' for k in risky),
                   risky_inconclusive=sum(out[k]['verdict'] == 'INCONCLUSIVE' for k in risky), risky_total=len(risky))
    table = d[['id', 'h', 'h_Tint', 'z', 'z_pred_first_order', 'z_inf', 'G_S_hybrid']].round(5).to_dict('records')
    result = dict(predictions=out, summary=summary, unresolved=bad,
                  consistency=float((d.z_inf - d.z_inf_run).abs().max()), table=table)
    (OUT / 'score_csw.json').write_text(json.dumps(result, indent=1, default=str) + '\n')
    for k, v in out.items():
        print(f"{k:5s} {v['label']:13s} n={v['n']:3d} {v['verdict']:12s}",
              {kk: vv for kk, vv in v.items() if kk in ('value', 'threshold', 'min_z')})
    print('risky:', summary, 'consistency z_inf:', result['consistency'])


if __name__ == '__main__':
    main()
