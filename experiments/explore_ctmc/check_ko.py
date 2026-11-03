"""Doan Van Tai — score PREDICTIONS_ko.md exactly as locked; freeze its zero-fit numbers [EXPLORATION ONLY;
AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.check_ko freeze   # -> results/explore_ctmc/PREDICTIONS_ko_numbers.csv (M0-only rows)
  python -m experiments.explore_ctmc.check_ko          # -> results/explore_ctmc/score_ko.json
"""
from fractions import Fraction as F
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
STAGES = ('ko_asym', 'ko_slice')
BINS = [0.3, 1, 2, 4, 7, 15, 40]


def verdict(ok, n):
    return 'INCONCLUSIVE' if n == 0 else ('PASS' if ok else 'FAIL')


def frac(mask):
    return float(np.mean(mask)) if len(mask) else float('nan')


def freeze():
    rows = []
    for stage in STAGES:
        for c in json.loads((OUT / 'cases' / f'{stage}.json').read_text()):
            d = json.loads((OUT / 'm0' / stage / f"{c['id']}.json").read_text())
            if d['status'] != 'COMPLETED':
                raise SystemExit(f'missing M0-only row {stage} {c["id"]}')
            for r, k in zip(d['h'][:-1], d['h_ko']):
                assert r['h'] == k['h']
                rows.append(dict(stage=stage, id=d['id'], h=r['h'], h_Tint=float(F(r['h'])) / d['T_int_max'],
                                 z_inf=d['z_inf'], z_inf_ko=d['z_inf_ko'], z_pred1_ko=k['z_pred_first_order_ko'],
                                 dep_inf_ko_new=d['dep_inf']['ko_new'], dep_inf_M0_new=d['dep_inf']['M0_new']))
    pd.DataFrame(rows).to_csv(OUT / 'PREDICTIONS_ko_numbers.csv', index=False)
    print(len(rows), 'rows frozen')


def load():
    recs, bad = [], []
    for stage in STAGES:
        for f in sorted((OUT / 'runs_ko' / stage).glob('*.json')):
            d = json.loads(f.read_text())
            if d['status'] != 'COMPLETED':
                bad.append((stage, d['id'], d['status']))
                continue
            for r in d['h']:
                cb = r.get('dep_static_cb', {})
                recs.append(dict(stage=stage, id=d['id'], h=r['h'], h_Tint=r['h_Tint'], x=d['x'], G_S=r['G_S'], S=r['S'],
                                 G_S_ko=r['G_S_ko'], G_S_hyb=r['G_S_hybrid'], dep_ko_new=r['dep_static']['ko_new'],
                                 dep_ko_old=r['dep_static']['ko_old'], dep_M0_new=r['dep_static']['M0_new'],
                                 dep_M0_old=r['dep_static']['M0_old'], dep_hyb_new=r['dep_static']['hybrid_new'],
                                 dep_M1_new=r['dep_static']['M1_new'], dep_ko_cb=cb.get('ko_cb'), dep_M0_cb=cb.get('M0_cb'),
                                 dep_M1_cb=cb.get('M1_cb'), dep_hyb_cb=cb.get('hybrid_cb'), flags=len(r.get('flags', []))))
    return pd.DataFrame(recs), bad


def main():
    if sys.argv[1:] == ['freeze']:
        return freeze()
    d, bad = load()
    frozen = pd.read_csv(OUT / 'PREDICTIONS_ko_numbers.csv', dtype={'h': str})
    d = d.merge(frozen[['stage', 'id', 'h', 'z_inf_ko', 'z_pred1_ko']], on=['stage', 'id', 'h'], how='left')
    out = {}
    m = d[d.h_Tint >= 15]
    ok = abs(m.G_S_ko - m.z_inf_ko) <= 0.1 + 0.1 * abs(m.z_inf_ko)
    out['KO-T1'] = dict(label='toán', n=len(m), value=frac(ok), verdict=verdict(ok.all(), len(m)))
    harm = d[d.G_S < -0.5]
    hit = abs(harm.G_S_ko) < 0.5 * abs(harm.G_S)
    out['KO-R1'] = dict(label='rủi ro', n=len(harm), value=frac(hit), threshold=0.8, verdict=verdict(frac(hit) >= 0.8, len(harm)))
    out['KO-R2'] = dict(label='rủi ro', n=len(d), value=frac(d.G_S_ko >= -0.25), threshold=0.9,
                        min=float(d.G_S_ko.min()), verdict=verdict(frac(d.G_S_ko >= -0.25) >= 0.9, len(d)))
    m = d[d.h_Tint <= 1]
    out['KO-R3'] = dict(label='rủi ro', n=len(m), value=frac(m.G_S_ko >= -0.1), threshold=0.9,
                        verdict=verdict(frac(m.G_S_ko >= -0.1) >= 0.9, len(m)))
    for key, (lo, hi), thr in (('KO-R4a', (2, 4), 0.5), ('KO-R4b', (4, 7), 0.9), ('KO-R4c', (7, 15), 0.9),
                               ('KO-R4d', (15, 40), 0.95)):
        m = d[(d.h_Tint > lo) & (d.h_Tint <= hi)]
        hit = abs(m.G_S_ko - m.z_pred1_ko) <= 0.1
        out[key] = dict(label='onset', n=len(m), value=frac(hit), threshold=thr, verdict=verdict(frac(hit) >= thr, len(m)))
    m = d[d.h_Tint >= 4]
    out['KO-R5'] = dict(label='rủi ro', n=len(m), value=frac(m.dep_ko_new >= 0.5), threshold=0.9,
                        verdict=verdict(frac(m.dep_ko_new >= 0.5) >= 0.9, len(m)))
    m = d[(d.h_Tint >= 7) & (abs(d.z_inf_ko) >= 0.25)]
    hit = np.sign(m.G_S_ko) == np.sign(m.z_inf_ko)
    out['KO-R6'] = dict(label='rủi ro', n=len(m), value=frac(hit), threshold=0.9, verdict=verdict(frac(hit) >= 0.9, len(m)))
    risky = [k for k, v in out.items() if v['label'] in ('rủi ro', 'onset')]
    summary = dict(risky_pass=sum(out[k]['verdict'] == 'PASS' for k in risky),
                   risky_fail=sum(out[k]['verdict'] == 'FAIL' for k in risky),
                   risky_inconclusive=sum(out[k]['verdict'] == 'INCONCLUSIVE' for k in risky), risky_total=len(risky))
    d['xc'] = np.where(d.x < 0, 'x<0', np.where(d.x < 0.25, '0<x<1/4', 'x>=1/4'))
    d['hT'] = pd.cut(d.h_Tint, BINS)
    table = d.groupby(['xc', 'hT'], observed=True).agg(
        n=('id', 'size'), G_S_M0=('G_S', 'median'), G_S_hybrid=('G_S_hyb', 'median'), G_S_KO=('G_S_ko', 'median'),
        G_S_M1=('S', 'median'), dep_M0=('dep_M0_new', 'median'), dep_KO=('dep_ko_new', 'median'),
        dep_hybrid=('dep_hyb_new', 'median'), dep_M1=('dep_M1_new', 'median')).round(4)
    dep_harm = d[d.G_S < -0.5][['dep_M1_new', 'dep_M0_new', 'dep_hyb_new', 'dep_ko_new', 'dep_M0_old', 'dep_ko_old',
                                'dep_M0_cb', 'dep_ko_cb', 'dep_M1_cb', 'dep_hyb_cb']].median().round(4).to_dict()
    result = dict(predictions=out, summary=summary, unresolved=bad, missing_frozen=int(d.z_pred1_ko.isna().sum()),
                  table_2x2=table.reset_index().astype(str).to_dict('records'), dep_median_harm_rows=dep_harm, n_rows=len(d))
    (OUT / 'score_ko.json').write_text(json.dumps(result, indent=1, default=str) + '\n')
    for k, v in out.items():
        print(f"{k:7s} {v['label']:7s} n={v['n']:4d} {v['verdict']:12s}", {kk: vv for kk, vv in v.items() if kk in ('value', 'threshold', 'min')})
    print('risky+onset:', summary, 'unresolved:', len(bad), 'missing frozen:', result['missing_frozen'])
    pd.set_option('display.width', 220)
    print(table.to_string())
    print('state dependence (median, harm rows):', dep_harm)


if __name__ == '__main__':
    main()
