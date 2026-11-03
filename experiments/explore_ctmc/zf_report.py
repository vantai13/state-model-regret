"""Doan Van Tai — L7.2 Part 1B report: zero-fit numbers at the held-out amplitudes [EXPLORATION ONLY;
AI (Claude) theo ủy quyền]. No truth column exists anywhere in these files.

  python -m experiments.explore_ctmc.zf_report   # -> results/explore_ctmc/l72/{ZEROFIT_a3.csv, ZEROFIT_a7p5.csv,
                                                 #    ZEROFIT_a6_xs.csv, compare_amplitudes.json}
"""
from fractions import Fraction as F
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
DEST = OUT / 'l72'


def rows(stage, folder='m0_l72'):
    recs = []
    for f in sorted((OUT / folder / stage).glob('*.json')):
        d = json.loads(f.read_text())
        if d['status'] != 'COMPLETED':
            recs.append(dict(stage=stage, id=d['id'], status=d['status'], error=d.get('error')))
            continue
        lamA, lamB, u, kappa, c = (float(F(x)) for x in d['parameters'])
        for r in d['h'][:-1]:
            h = float(F(r['h']))
            rec = dict(stage=stage, id=d['id'], status='COMPLETED', a=d.get('a', 6), lamA=lamA, lamB=lamB, u=u, kappa=kappa,
                       x=d['x'], delta=d['delta'], load_max=max(lamA, lamB) + u, h=r['h'], h_Tint=h / d['T_int_max'],
                       h_kappa=r['h_kappa'], T_int_max=d['T_int_max'], N_A=d['N']['A'], N_B=d['N']['B'], s=d['s'],
                       r_min=d['r_min'], z_inf=d['z_inf'], z_pred1=r['z_pred_first_order'], z_inf_ko=d['z_inf_ko'],
                       F_old=d['h'][-1]['F_old'], F_new=d['h'][-1]['F_new'], M0_regret_new_pred=d['M0_regret_new_pred'],
                       dep_M0_new=d['dep_inf']['M0_new'], dep_ko_new=d['dep_inf']['ko_new'])
            if 'z_F_inf' in d:
                rec.update(z_F_inf=d['z_F_inf'], z_V_inf=d['z_V_inf'], F_cb=d['F_cb'],
                           backlog_share=d['z_F_inf'] / d['z_inf'] if d['z_inf'] else np.nan)
            recs.append(rec)
    return pd.DataFrame(recs)


def x_star(df):
    """Upper edge of the help band: first sign change of z_inf from + to - for x > 0, linear interpolation."""
    out = []
    for (u, lamA, kappa), g in df.groupby(['u', 'lamA', 'kappa']):
        g = g.sort_values('x')
        pos = g[g.x > 0]
        xs, zs = pos.x.values, pos.z_inf.values
        edge = None
        for i in range(1, len(xs)):
            if zs[i - 1] > 0 >= zs[i]:
                edge = float(xs[i - 1] + (xs[i] - xs[i - 1]) * zs[i - 1] / (zs[i - 1] - zs[i]))
                break
        out.append(dict(u=u, lamA=lamA, kappa=kappa, x_star=edge, z_at_first_x=float(zs[0]) if len(zs) else None,
                        n=len(g)))
    return out


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    summary = {}
    for tag in ('a3', 'a7p5'):
        df = pd.concat([rows(f'zf_{tag}_asym'), rows(f'zf_{tag}_sobol'), rows(f'zf_{tag}_xs')], ignore_index=True)
        df.to_csv(DEST / f'ZEROFIT_{tag}.csv', index=False)
        ok = df[df.status == 'COMPLETED']
        one = ok.drop_duplicates(['stage', 'id'])
        sob = one[one.stage == f'zf_{tag}_sobol']
        harm = sob[sob.z_inf < -0.5]
        summary[tag] = dict(rows=len(df), not_completed=int((df.status != 'COMPLETED').sum()),
                            T_int_quantiles=sob.T_int_max.quantile([.1, .5, .9]).round(2).tolist(),
                            N_max_quantiles=sob[['N_A', 'N_B']].max(axis=1).quantile([.5, .9, 1]).tolist(),
                            frac_harm_z_inf=float((sob.z_inf < -0.5).mean()), frac_help_z_inf=float((sob.z_inf > 0.5).mean()),
                            backlog_share_harm=harm.backlog_share.quantile([.1, .5, .9]).round(3).tolist()
                            if 'backlog_share' in harm else None,
                            z_inf_ko_over_z_inf_harm=(harm.z_inf_ko / harm.z_inf).quantile([.1, .5, .9]).round(3).tolist(),
                            dep_M0_new_median=float(sob.dep_M0_new.median()), dep_ko_new_median=float(sob.dep_ko_new.median()),
                            x_star=x_star(one[one.stage == f'zf_{tag}_xs']))
    from experiments.explore_ctmc.design import est_cpu
    for tag in ('a3', 'a7p5'):
        cost = {}
        for st in ('asym', 'sobol'):
            cases = json.loads((OUT / 'cases' / f'zf_{tag}_{st}.json').read_text())
            est = []
            for c in cases:
                f = OUT / 'm0_l72' / f'zf_{tag}_{st}' / f"{c['id']}.json"
                if not f.exists():
                    continue
                d = json.loads(f.read_text())
                if d['status'] != 'COMPLETED':
                    continue
                est.append(est_cpu(d['N']['A'], d['N']['B'], F(c['parameters'][3]), max(F(h) for h in c['hs'])))
            est = np.array(est)
            cost[st] = dict(n=int(est.size), est_CPU_h=float(est.sum() / 3600) if est.size else None,
                            est_CPU_h_if_case_cap_900s=float(est[est <= 900].sum() / 3600) if est.size else None,
                            n_over_900s=int((est > 900).sum()), max_case_s=float(est.max()) if est.size else None)
        summary[tag]['truth_cost_estimate'] = cost
    a6 = rows('zf_a6_xs')
    a6.to_csv(DEST / 'ZEROFIT_a6_xs.csv', index=False)
    summary['a6'] = dict(x_star=x_star(a6[a6.status == 'COMPLETED'].drop_duplicates(['stage', 'id'])))
    d22 = pd.read_csv(OUT / 'PREDICTIONS_d22_numbers.csv').drop_duplicates(['stage', 'id'])
    h6 = d22[d22.z_inf < -0.5]
    summary['a6']['backlog_share_harm'] = (h6.z_F_inf / h6.z_inf).quantile([.1, .5, .9]).round(3).tolist()
    m0w = [json.loads(f.read_text()) for f in (OUT / 'm0' / 'asym').glob('*.json')]
    summary['a6']['T_int_quantiles_asym'] = np.quantile([d['T_int_max'] for d in m0w], [.1, .5, .9]).round(2).tolist()
    (DEST / 'compare_amplitudes.json').write_text(json.dumps(summary, indent=1, default=float) + '\n')
    for tag, s in summary.items():
        print(tag, {k: v for k, v in s.items() if k != 'x_star'})
        print('   x*:', [(r['u'], r['lamA'], r['kappa'], None if r['x_star'] is None else round(r['x_star'], 3)) for r in s['x_star']])


if __name__ == '__main__':
    main()
