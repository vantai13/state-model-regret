"""Doan Van Tai — descriptive read-outs of ctmc-v1 runs (Stage E discovery tables) [EXPLORATION ONLY;
AI (Claude) theo ủy quyền]. Nothing here is a scored prediction.

  python -m experiments.explore_ctmc.analyze STAGE [STAGE ...]   # -> results/explore_ctmc/analysis_<first>.json
"""
from fractions import Fraction as F
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
TWINS = ('M0_new', 'M0_old', 'margin_new', 'margin_old', 'static', 'const', 'hybrid_new', 'hybrid_old', 'M1_old')


def rows(stages):
    recs, bad = [], []
    for stage in stages:
        for f in sorted((OUT / 'runs' / stage).glob('*.json')):
            d = json.loads(f.read_text())
            if d['status'] != 'COMPLETED':
                bad.append((stage, d['id'], d['status']))
                continue
            lamA, lamB, u, kappa, c = (float(F(x)) for x in d['parameters'])
            for r in d['h']:
                rec = dict(stage=stage, id=d['id'], lamA=lamA, lamB=lamB, u=u, kappa=kappa, c=c, delta=lamB - lamA,
                           x=d['x'], h=float(F(r['h'])), h_kappa=r['h_kappa'], h_Tint=r['h_Tint'],
                           P=r['h_kappa'] * abs(lamB - lamA), s=d['s'], r_min=d['r_min'], z_inf=d['asymptotic']['z_inf'],
                           S=r['S'], M=r['M'], G_S=r['G_S'], G_M=r['G_M'], Gamma=r['Gamma'], G_S_hybrid=r['G_S_hybrid'],
                           z_pred1_inf=r['z_pred_first_order_inf_decisions'], cpu=d['cpu'], host=d['host'],
                           load_max=max(lamA, lamB) + u)
                rec.update({f'reg_{t}': r['regret'][t] for t in TWINS})
                recs.append(rec)
    return pd.DataFrame(recs), bad


def best_threshold(values, labels):
    best = (0.0, None)
    for t in np.unique(np.quantile(values, np.linspace(0.01, 0.99, 197))):
        acc = max(((values < t) == labels).mean(), ((values >= t) == labels).mean())
        if acc > best[0]:
            best = (float(acc), float(t))
    return best


def x_class(x):
    if x == 0:
        return 'x=0'
    if x < 0:
        return 'x<0'
    return '0<x<=0.25' if x <= 0.25 else ('0.25<x<=0.5' if x <= 0.5 else 'x>0.5')


def main():
    stages = sys.argv[1:]
    d, bad = rows(stages)
    d['xc'] = d.x.map(x_class)
    d['S_gt_M_flag'] = d.S > d.M
    d['hT_bin'] = pd.cut(d.h_Tint, [0, 0.1, 0.3, 1, 3, 10, 1e9], labels=['<0.1', '0.1-0.3', '0.3-1', '1-3', '3-10', '>=10'])
    out = dict(stages=stages, n_rows=len(d), unresolved=bad, cpu_hours=float(d.drop_duplicates('id').cpu.sum() / 3600))
    rel = d[(d.S + d.M) >= 0.5]
    y = (rel.S > rel.M).values
    hs = (rel.h * abs(rel.s) / rel.r_min).values
    out['collapse_S_gt_M'] = dict(n=len(rel), base_rate=float(y.mean()) if len(y) else None,
                                  **{k: best_threshold(v, y) for k, v in (('h_kappa', rel.h_kappa.values), ('P', rel.P.values),
                                                                          ('h_Tint', rel.h_Tint.values), ('h_s_over_rmin', hs))})
    reg = d[[f'reg_{t}' for t in TWINS]]
    d['best_twin'] = reg.idxmin(axis=1).str[4:]
    d['static_enough'] = d.reg_static <= 0.5
    state_twins = d[[f'reg_{t}' for t in ('M0_new', 'margin_new', 'hybrid_new')]].min(axis=1)
    d['state_helps_vs_static'] = state_twins < d.reg_static - 0.5
    d['needs_M1'] = d[[f'reg_{t}' for t in TWINS if t != 'M1_old']].min(axis=1) > 0.5
    g = d.groupby(['hT_bin', 'xc'], observed=True)
    twin_map = g.agg(n=('id', 'size'), best=('best_twin', lambda v: v.value_counts().idxmax()),
                     best_share=('best_twin', lambda v: float(v.value_counts(normalize=True).iloc[0])),
                     static_enough=('static_enough', 'mean'), state_helps=('state_helps_vs_static', 'mean'),
                     needs_M1=('needs_M1', 'mean'), med_reg_M0_new=('reg_M0_new', 'median'),
                     med_reg_static=('reg_static', 'median'), med_reg_hybrid_new=('reg_hybrid_new', 'median'))
    out['twin_map'] = twin_map.round(3).reset_index().astype(str).to_dict('records')
    harm = d[(d.G_S < -0.5)]
    out['hybrid'] = harm.groupby(['hT_bin'], observed=True).agg(n=('id', 'size'), med_GS=('G_S', 'median'),
                                                                med_GS_hyb=('G_S_hybrid', 'median'),
                                                                hyb_ok=('G_S_hybrid', lambda v: float((v >= -0.1).mean()))) \
        .round(3).reset_index().astype(str).to_dict('records')
    zz = d[abs(d.z_inf) >= 0.5]
    out['z_convergence'] = zz.assign(rel=abs(zz.G_S - zz.z_inf) / abs(zz.z_inf), sign=np.sign(zz.G_S) == np.sign(zz.z_inf)) \
        .groupby('hT_bin', observed=True).agg(n=('id', 'size'), med_rel_err=('rel', 'median'), sign_agree=('sign', 'mean')) \
        .round(3).reset_index().astype(str).to_dict('records')
    out['classes'] = d.groupby(['hT_bin', 'xc'], observed=True).agg(
        n=('id', 'size'), GS_neg=('G_S', lambda v: float((v < -0.1).mean())), GS_pos=('G_S', lambda v: float((v > 0.1).mean())),
        S_gt_M=('S_gt_M_flag', 'mean')).reset_index().astype(str).to_dict('records')
    (OUT / f'analysis_{stages[0]}.json').write_text(json.dumps(out, indent=1, default=str) + '\n')
    pd.set_option('display.width', 200)
    print(json.dumps({k: out[k] for k in ('stages', 'n_rows', 'cpu_hours', 'collapse_S_gt_M')}, indent=0, default=str))
    print(twin_map.round(3).to_string())
    print(pd.DataFrame(out['hybrid']).to_string())
    print(pd.DataFrame(out['z_convergence']).to_string())


if __name__ == '__main__':
    main()
