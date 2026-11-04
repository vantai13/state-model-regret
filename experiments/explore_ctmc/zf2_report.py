"""Doan Van Tai — L7.3 Part 2 Stage 0 report: zero-fit numbers of ctmc-v2 [EXPLORATION ONLY; AI (Claude) theo ủy quyền].
No truth column exists anywhere in these files.

  python -m experiments.explore_ctmc.zf2_report    # -> results/explore_ctmc/l73/{ZEROFIT_2s.csv, zerofit_summary.json}
"""
from fractions import Fraction as F
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
SRC = OUT / 'm0_l73'
DEST = OUT / 'l73'
STAGES = ('asym', 'mid', 'sobol', 'xs')
BINS = [0, 1, 4, 7, 15, 40.0001]


def rows(stage):
    recs = []
    for f in sorted((SRC / stage).glob('*.json')):
        d = json.loads(f.read_text())
        base = dict(stage=stage, id=d['id'], status=d['status'], combo=d.get('tags', {}).get('combo'))
        if d['status'] != 'COMPLETED':
            recs.append(dict(base, error=d.get('error')))
            continue
        lamA, lamB, u, Tf, Ts, af, as_, c = (float(F(x)) for x in d['parameters'])
        ch = d['chains']
        Tr = max(v['T_relax'] for v in ch.values())
        Tap = max(v['T_int_approx_3d'] for v in ch.values())
        inf = d['h'][-1]
        ko = {r['h']: r['z_pred_first_order_ko'] for r in d['h_ko']}
        for r in d['h'][:-1]:
            h = float(F(r['h']))
            rec = dict(base, f=d['f'], f_nominal=d.get('f_nominal'), Tf=Tf, Ts=Ts, ratio=Ts / Tf, a_f=af, a_s=as_,
                       lamA=lamA, lamB=lamB, u=u, x=d['x'], delta=d['delta'], load_max=max(lamA, lamB) + u, h=r['h'],
                       h_Tint=r['h_Tint'], h_Tf=r['h_Tf'], h_Ts=r['h_Ts'], T_int_max=d['T_int_max'],
                       T_relax_max=Tr, T_relax_over_T_int=Tr / d['T_int_max'], T_int_approx_3d_max=Tap,
                       approx_over_exact=Tap / d['T_int_max'], N_A=d['N']['A'], N_B=d['N']['B'], s=d['s'],
                       r_min=d['r_min'], z_inf=d['z_inf'], z_pred1=r['z_pred_first_order'], z_inf_ko=d['z_inf_ko'],
                       z_pred1_ko=ko.get(r['h']), F_old_inf=inf['F_old'], F_new_inf=inf['F_new'],
                       dep_M0_new=d['dep_inf']['M0_new'], dep_M0_old=d['dep_inf']['M0_old'],
                       M0_regret_new_pred=d['M0_regret_new_pred'], M0_regret_old_pred=d['M0_regret_old_pred'],
                       est_truth_cpu=d['est_truth_cpu'], cpu_zf=d['cpu'])
            if 'z_F_inf' in d:
                rec.update(F_cb_inf=inf['F_cb'], z_F_inf=d['z_F_inf'], z_V_inf=d['z_V_inf'],
                           backlog_share=d['z_F_inf'] / d['z_inf'] if d['z_inf'] else np.nan,
                           dep_M0_cb=d['dep_inf'].get('M0_cb'), d22_dropped_mass=d.get('d22_dropped_mass'))
            recs.append(rec)
    return pd.DataFrame(recs)


def q(s, qs=(.1, .5, .9)):
    s = pd.Series(s).dropna()
    return [round(float(v), 4) for v in s.quantile(list(qs))] if len(s) else None


def x_star(df):
    out = []
    for (combo, u, lamA), g in df.groupby(['combo', 'u', 'lamA']):
        g = g.sort_values('x')
        pos = g[g.x > 0]
        xs, zs = pos.x.values, pos.z_inf.values
        edge = None
        for i in range(1, len(xs)):
            if zs[i - 1] > 0 >= zs[i]:
                edge = float(xs[i - 1] + (xs[i] - xs[i - 1]) * zs[i - 1] / (zs[i - 1] - zs[i]))
                break
        out.append(dict(combo=combo, u=u, lamA=lamA, x_star=edge, z_first_pos=float(zs[0]) if len(zs) else None,
                        n=len(g)))
    return out


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    df = pd.concat([rows(s) for s in STAGES], ignore_index=True)
    df.to_csv(DEST / 'ZEROFIT_2s.csv', index=False)
    ok = df[df.status == 'COMPLETED']
    one = ok.drop_duplicates(['stage', 'id'])
    summ = dict(rows=len(df), cases={s: int((df.drop_duplicates(['stage', 'id']).stage == s).sum()) for s in STAGES},
                not_completed=df[df.status != 'COMPLETED'][['stage', 'id', 'status', 'error']].to_dict('records'))
    stat = {}
    for combo, g in one.groupby('combo'):
        stat[combo] = dict(n=len(g), T_int=q(g.T_int_max), T_relax_over_T_int=q(g.T_relax_over_T_int),
                           approx3d_over_exact=q(g.approx_over_exact), N_max=int(g[['N_A', 'N_B']].max(axis=1).max()))
    summ['stationary_by_combo'] = stat
    summ['stationary_all'] = dict(T_relax_over_T_int=q(one.T_relax_over_T_int, (.05, .5, .95)),
                                  approx3d_over_exact=q(one.approx_over_exact, (.05, .5, .95)))
    sign = {}
    for (f, ratio), g in one[one.stage.isin(['asym', 'sobol', 'mid'])].groupby(['f_nominal', 'ratio']):
        sign[f'f={f}_ratio={int(ratio)}'] = dict(n=len(g), frac_harm=float((g.z_inf < -0.5).mean()),
                                                 frac_help=float((g.z_inf > 0.5).mean()), z_inf=q(g.z_inf),
                                                 backlog_share_harm=q(g[g.z_inf < -0.5].backlog_share)
                                                 if 'backlog_share' in g else None,
                                                 ko_over_z_harm=q((g.z_inf_ko / g.z_inf)[g.z_inf < -0.5]))
    summ['z_inf_by_f_ratio'] = sign
    asym = ok[ok.stage == 'asym'].copy()
    asym['bin'] = pd.cut(asym.h_Tint, BINS, right=True)
    summ['asym_bins'] = {str(b): dict(n=len(g), z_pred1=q(g.z_pred1), abs_z_pred1_minus_z_inf=q((g.z_pred1 - g.z_inf).abs()))
                         for b, g in asym.groupby('bin', observed=True)}
    mid = ok[ok.stage == 'mid']
    summ['mid'] = {combo: dict(n=len(g), h_Tint=q(g.h_Tint), z_pred1=q(g.z_pred1), z_inf=q(g.z_inf),
                               dep_M0_new=q(g.dep_M0_new), dep_M0_old=q(g.dep_M0_old))
                   for combo, g in mid.groupby('combo')}
    summ['x_star'] = x_star(one[one.stage == 'xs'])
    cost = {}
    for s in ('asym', 'mid', 'sobol'):
        g = one[one.stage == s]
        cost[s] = dict(n=len(g), est_CPU_h=float(g.est_truth_cpu.sum() / 3600), n_over_900s=int((g.est_truth_cpu > 900).sum()),
                       max_case_s=float(g.est_truth_cpu.max()) if len(g) else None)
    summ['truth_cost_estimate'] = cost
    summ['zero_fit_cpu_h'] = float(one.cpu_zf.sum() / 3600)
    (DEST / 'zerofit_summary.json').write_text(json.dumps(summ, indent=1, default=float) + '\n')
    print(json.dumps({k: v for k, v in summ.items() if k not in ('x_star', 'stationary_by_combo')}, indent=1, default=float)[:6000])


if __name__ == '__main__':
    main()
