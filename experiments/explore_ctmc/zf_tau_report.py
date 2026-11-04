"""Doan Van Tai — L7.5 Stage 0 zero-fit report [EXPLORATION ONLY; AI (Claude) theo ủy quyền]. Reads m0_l75 only;
no truth exists at tau != 1.

  python -m experiments.explore_ctmc.zf_tau_report   # -> results/explore_ctmc/l75/{ZEROFIT_tau.csv, zerofit_summary.json}

Sign convention (as v1): z = G_S in % C_ref, G_S = L00 - L10 (old-state loss minus fresh-state loss of the M0 twin).
z < 0: replacing the old observation by the fresh state HARMS the twin. "Harm" below means z < -0.5.
"""
from fractions import Fraction as F
import json
import math
from pathlib import Path
import socket

import numpy as np
import pandas as pd

from experiments.explore_ctmc import tau as T5

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
SRC = OUT / 'm0_l75'
DEST = OUT / 'l75'
TAU_BINS = [(0, 0.005), (0.005, 0.02), (0.02, 0.05), (0.05, 0.2), (0.2, 0.5), (0.5, 2), (2, 5), (5, 20)]
H_BINS = [(0.2, 0.5), (0.5, 2), (2, 5), (5, 10), (10, 20), (20, 40)]


def load():
    recs = []
    for stage in ('sobol', 'old', 'xs'):
        cases = {c['id']: c for c in json.loads((OUT / 'cases_l75' / f'{stage}.json').read_text())}
        for f in sorted((SRC / stage).glob('*.json')):
            d = json.loads(f.read_text())
            c = cases[d['id']]
            lamA, lamB, u, kappa = (F(x) for x in c['parameters'][:4])
            base = dict(stage=stage, id=d['id'], status=d['status'], host=d.get('host'), cpu=d.get('cpu'),
                        lamA=float(lamA), lamB=float(lamB), u=float(u), kappa=float(kappa), x=c['x'],
                        delta=float(lamB - lamA), T_int_max=c['T_int_max'], tau=d['tau'], tau_s=float(F(d['tau'])),
                        tau_Tint=float(F(d['tau'])) / c['T_int_max'], is_ref_tau=F(d['tau']) == 1,
                        d22=d.get('d22_unit'), family=f"u{c['parameters'][2]}_lA{c['parameters'][0]}_k{c['parameters'][3]}",
                        stratum=c['tags'].get('stratum', 'old' if stage == 'old' else 'xs'))
            if d['status'] != 'COMPLETED':
                recs.append(dict(base, h='inf'))
                continue
            base.update(z_inf=d['z_inf'], z_inf_ko=d['z_inf_ko'], s=d['s'], r_min=d['r_min'], a_inf_switch=d['a_inf_switch'],
                        z_F_inf=d.get('z_F_inf'), z_V_inf=d.get('z_V_inf'))
            for r in d['h']:
                recs.append(dict(base, h=r['h'], h_Tint=(math.inf if r['h'] == 'inf' else float(F(r['h'])) / c['T_int_max']),
                                 F_new=r['F_new'], F_old=r['F_old'], B=r['B'], F_cb=r.get('F_cb'),
                                 z_pred1=r.get('z_pred_first_order')))
    return pd.DataFrame(recs)


def q(s):
    s = pd.Series(s).dropna()
    return dict(n=int(len(s)), q10=float(s.quantile(.1)), median=float(s.median()), q90=float(s.quantile(.9))) if len(s) else dict(n=0)


def tau_index(df):
    """Position of each unit's tau on its regime's grid (0..7) from the exact case-list map (tau.tau_grid_map); the
    extra reference tau = 1 s is marked -1 (a grid tau that rounds to 1 s, TB0001, keeps its grid index)."""
    out = {}
    for st in ('sobol', 'old', 'xs'):
        grid = T5.XS_TAU if st == 'xs' else T5.TAU_GRID
        for c in json.loads((OUT / 'cases_l75' / f'{st}.json').read_text()):
            gm = T5.tau_grid_map(c, st)
            for t in c['taus']:
                out[(st, c['id'], float(F(t)))] = [float(m) for m in grid].index(gm[t]) if t in gm else -1
    return out


def monotone(df):
    """Per regime (sobol, old): z_inf over the 8 grid tau sorted by tau. Strictly: every step <= +1e-9 (non-increasing)
    or every step >= -1e-9 (non-decreasing)."""
    rows = []
    idx = tau_index(df)
    sel = df[(df.h == 'inf') & df.stage.isin(['sobol', 'old'])]
    sel = sel[[idx[(s, i, t)] >= 0 for s, i, t in zip(sel.stage, sel.id, sel.tau_s)]]
    for (st, rid), g in sel.groupby(['stage', 'id']):
        g = g.sort_values('tau_s')
        z = g.z_inf.values
        dz = np.diff(z)
        rows.append(dict(stage=st, id=rid, x=g.x.iloc[0], stratum=g.stratum.iloc[0], n=len(z),
                         dec=bool((dz <= 1e-9).all()), inc=bool((dz >= -1e-9).all()),
                         sign_changes=int((np.diff(np.sign(np.where(np.abs(z) < 1e-12, 0, z))) != 0).sum()),
                         z_first=float(z[0]), z_last=float(z[-1]), harm_last=bool(z[-1] < -0.5),
                         mono_abs_on_harm=bool(z[-1] < -0.5 and (dz <= 1e-9).all())))
    return pd.DataFrame(rows)


def x_star(df):
    """x*(tau) per x-slice family: first + -> - sign change of z for x > 0 (rule of zf_report.x_star), from z_inf and
    from z_pred1 at h = 10 T_int."""
    out = []
    xs = df[(df.stage == 'xs') & (df.status == 'COMPLETED')]
    idx = tau_index(df)
    for col in ('z_inf', 'z_pred1'):
        sub = xs[xs.h == 'inf'] if col == 'z_inf' else xs[xs.h != 'inf']
        sub = sub.assign(k=[idx[(s, i, t)] for s, i, t in zip(sub.stage, sub.id, sub.tau_s)])
        for (fam, k), g in sub.groupby(['family', 'k']):
            g = g[g.x > 0].sort_values('x')
            xv, zv = g.x.values, g[col].values
            edge = None
            for i in range(1, len(xv)):
                if zv[i - 1] > 0 >= zv[i]:
                    edge = float(xv[i - 1] + (xv[i] - xv[i - 1]) * zv[i - 1] / (zv[i - 1] - zv[i]))
                    break
            out.append(dict(source=col, family=fam, tau_Tint=str(T5.XS_TAU[k]), x_star=edge,
                            z_first_pos=float(zv[0]) if len(zv) else None, help_points=int((zv > 0.5).sum()), n=len(g)))
    return out


def n_estimates(df):
    """Predicted rows by tau bin x h bin (sobol + old, grid tau), from z_pred1 at finite h: all rows and predicted harm
    (z_pred1 < -0.5). Zero-fit predictions only; a guide for the author's n_min, not a result."""
    idx = tau_index(df)
    fin = df[df.stage.isin(['sobol', 'old']) & (df.h != 'inf') & (df.status == 'COMPLETED')]
    fin = fin[[idx[(s, i, t)] >= 0 for s, i, t in zip(fin.stage, fin.id, fin.tau_s)]]
    tab = {}
    for tl, th in TAU_BINS:
        for hl, hh in H_BINS:
            g = fin[(fin.tau_Tint > tl) & (fin.tau_Tint <= th) & (fin.h_Tint > hl) & (fin.h_Tint <= hh)]
            tab[f'tau({tl};{th}] h({hl};{hh}]'] = dict(rows=int(len(g)), harm_pred=int((g.z_pred1 < -0.5).sum()),
                                                       help_pred=int((g.z_pred1 > 0.5).sum()), regimes=int(g.id.nunique()))
    long = fin[fin.h_Tint >= 7]
    harm_reg = long.groupby('id').z_pred1.min()
    dose = dict(rows_h_ge_7=int(len(long)), regimes_h_ge_7=int(long.id.nunique()),
                regimes_with_some_harm_pred=int((harm_reg < -0.5).sum()))
    return tab, dose


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    df = load()
    df.to_csv(DEST / 'ZEROFIT_tau.csv', index=False)
    inf = df[(df.h == 'inf') & (df.status == 'COMPLETED')]
    units = df.drop_duplicates(['stage', 'id', 'tau'])
    idx = tau_index(df)
    inf = inf.assign(k=[idx[(s, i, t)] for s, i, t in zip(inf.stage, inf.id, inf.tau_s)])
    main_set = inf[inf.stage.isin(['sobol', 'old'])]
    summ = dict(note='AI (Claude) theo ủy quyền; zero fit only (no truth at tau != 1). z = G_S in % C_ref; z < 0 harm.',
                hosts=sorted(df.host.dropna().unique()), report_host=socket.gethostname(),
                units={st: g.status.value_counts().to_dict() for st, g in units.groupby('stage')},
                cpu_h=float(units.cpu.fillna(0).sum() / 3600))
    summ['z_inf_by_tau'] = {str(T5.TAU_GRID[k]): dict(all=q(g.z_inf), **{s: q(gs.z_inf) for s, gs in g.groupby('stratum')})
                            for k, g in main_set[main_set.k >= 0].groupby('k')}
    summ['z_inf_ref_tau_1s'] = q(main_set[main_set.k < 0].z_inf)
    mono = monotone(df)
    summ['monotone'] = dict(regimes=len(mono), non_increasing=int(mono.dec.sum()), non_decreasing=int(mono.inc.sum()),
                            neither=int((~mono.dec & ~mono.inc).sum()),
                            by_stratum={s: dict(n=len(g), non_increasing=int(g.dec.sum()), non_decreasing=int(g.inc.sum()),
                                                with_sign_change=int((g.sign_changes > 0).sum()))
                                        for s, g in mono.groupby('stratum')},
                            harm_at_largest_tau=int(mono.harm_last.sum()),
                            harm_at_largest_tau_and_non_increasing=int(mono.mono_abs_on_harm.sum()))
    mono.to_csv(DEST / 'monotone_tau.csv', index=False)
    d22 = main_set[main_set.z_F_inf.notna() & (main_set.z_inf < -0.5)]
    summ['d22_backlog_share_on_harm'] = {str(T5.TAU_GRID[k]): q(g.z_F_inf / g.z_inf) for k, g in d22[d22.k >= 0].groupby('k')}
    summ['d22_coverage'] = dict(units_with_d22=int(main_set.z_F_inf.notna().sum()), units=int(len(main_set)))
    summ['ko_by_tau'] = {str(T5.TAU_GRID[k]): q(g.z_inf_ko) for k, g in main_set[main_set.k >= 0].groupby('k')}
    summ['x_star'] = x_star(df)
    summ['n_estimates'], summ['dose_response_pool'] = n_estimates(df)
    # control (f): at the largest tau the old observation carries almost no information; compare with the decision
    # on the stationary posterior (one action for every Y). Report only.
    big = main_set[main_set.k == 7]
    fdev = []
    for _, r in big.iterrows():
        stat = T5.stationary_posterior_decision(F(r.lamA), F(r.lamB), F(r.u), F(r.kappa))
        old_share = df[(df.stage == r.stage) & (df.id == r.id) & (df.tau == r.tau) & (df.h == 'inf')].F_old.iloc[0]
        fdev.append(abs(old_share - stat))
    summ['control_f_largest_tau'] = dict(criterion='report only', abs_F_old_minus_stationary_decision=q(fdev),
                                         share_below_1e_3=float(np.mean(np.array(fdev) < 1e-3)) if fdev else None)
    (DEST / 'zerofit_summary.json').write_text(json.dumps(summ, indent=1, default=float) + '\n')
    print(json.dumps({k: summ[k] for k in ('hosts', 'units', 'cpu_h', 'monotone', 'dose_response_pool')}, indent=1, default=float))


if __name__ == '__main__':
    main()
