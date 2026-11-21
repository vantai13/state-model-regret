#!/usr/bin/env python3
"""Doan Van Tai — Sweep S0: post hoc re-analysis of SAVED letter data (Claude, 21/11/2026).

Question: where the hybrid (fluid gap + h*s_hat) departs from the stationary rule
1{s_hat<0}, does it win/lose through the instantaneous state, ties, workload or the
metric, and which regime features predict the paired benefit
    Delta = regret(stationary) - regret(hybrid)   [points of % C_ref; >0 = hybrid better]?

Rules: reads only saved files (no simulation, no CTMC solve, no rollout); writes only to
results/letter/sweep/s0/. Everything here is POST HOC and EXPLORATORY.
Independence: CTMC cells of one regime (all h, tau, sides) are not independent; GEANT
instances share a regime/seed and the two seeds share regime parameters; X4b instances
share a day. CIs below are across regimes (CTMC, GEANT) or are instance SEs (X4b).

Run:  .venv/bin/python -B results/letter/sweep/s0/analyze_s0.py
"""
from fractions import Fraction as F
import glob
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
L = ROOT / 'results/letter'
OUT = Path(__file__).resolve().parent
THR = 0.05      # points of % C_ref: better/worse threshold from the brief
MU_W1B = 10.0   # ctmc.MU of the homogeneous CTMC (experiments/explore_ctmc/ctmc.py)


def ci95(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 2:
        return (float(x.mean()) if n else np.nan, np.nan, np.nan)
    m, se = x.mean(), x.std(ddof=1) / math.sqrt(n)
    q = stats.t.ppf(.975, n - 1)
    return float(m), float(m - q * se), float(m + q * se)


def summarize(df, keys, unit='regime'):
    """One row per group: mean Delta with 95% CI across units, counts beyond +-THR."""
    rows = []
    for k, g in df.groupby(keys, sort=True):
        k = k if isinstance(k, tuple) else (k,)
        m, lo, hi = ci95(g['delta'])
        row = dict(zip(keys, k))
        row.update(n_units=len(g), unit=unit, mean_delta=m, ci_lo=lo, ci_hi=hi,
                   median_delta=float(g['delta'].median()),
                   n_better=int((g['delta'] > THR).sum()), n_worse=int((g['delta'] < -THR).sum()),
                   max_delta=float(g['delta'].max()), min_delta=float(g['delta'].min()),
                   mean_disagree=float(g['disagree'].mean()) if 'disagree' in g else np.nan)
        rows.append(row)
    return pd.DataFrame(rows)


def spearman_table(df, keys, features, source):
    rows = []
    for k, g in df.groupby(keys, sort=True):
        k = k if isinstance(k, tuple) else (k,)
        for f in features:
            sub = g[[f, 'delta']].replace([np.inf, -np.inf], np.nan).dropna()
            if len(sub) < 8 or sub[f].nunique() < 2 or sub['delta'].nunique() < 2:
                continue
            r, p = stats.spearmanr(sub[f], sub['delta'])
            rows.append(dict(source=source, **dict(zip(keys, k)), feature=f, n=len(sub),
                             spearman_rho=float(r), p_value=float(p)))
    return rows


def snap(x, grid, rel=.05):
    for g in grid:
        if abs(x - g) <= rel * g:
            return g
    return np.nan


# ---------------------------------------------------------------- W1b (homogeneous CTMC)
def load_w1b():
    rows = []
    for f in sorted(glob.glob(str(L / 'w1b/raw/*.json'))):
        r = json.loads(Path(f).read_text())
        la, lb, u, k, c = (float(F(x)) for x in r['case']['parameters'])
        s_mm1 = r['levels']['mm1']
        fresh_seen = {}
        for ev in r['evaluations']:
            a, s, rmin, Tint = ev['a'], ev['s'], ev['r_min'], r['T_int']
            stat_true = 1 if s < 0 else 0     # c = 0 in all W1b regimes (checked below)
            util = dict(A_stay=(la + u) / MU_W1B, B_stay=lb / MU_W1B,
                        A_switch=la / MU_W1B, B_switch=(lb + u) / MU_W1B)
            for row in ev['h']:
                h = float(F(row['h']))
                Cref, Est, Eg = row['Cref'], row['E_stay'], row['E_gap']
                G11 = Cref - Est
                base = dict(regime=r['id'], family=r['family'], age=ev['age_label'], tau=ev['tau'],
                            tau_Tint=ev['tau_Tint'], h=h, h_Tint=row['h_Tint'], T_int=Tint,
                            kappa=k, u=u, lamA=la, lamB=lb, a=a, a_over_mu=a / MU_W1B, s=s,
                            abs_s_over_rmin=abs(s) / rmin, kappa_over_Tint=k / Tint,
                            h_over_kappa=h / k, Cref=Cref)
                for level, sv in (('true_s', s), ('mm1', s_mm1)):
                    st = 1 if h * sv + c < 0 else 0
                    reg_stat = 100 * ((Eg if st else 0.) - G11) / Cref
                    if level == 'true_s':
                        # identity check against the saved static twin
                        assert abs(reg_stat - row['regret']['static']) < 1e-7, (r['id'], h)
                    hl = row['hybrid_levels'][level]
                    path = ('A_switch', 'B_switch') if st else ('A_stay', 'B_stay')
                    managed = 'B_switch' if st else 'A_stay'
                    feats = dict(level=level, s_hat=sv, sign_correct=bool(np.sign(sv) == np.sign(s)),
                                 static_action=st, rho_max_static=max(util[p] for p in path),
                                 rho_managed_static=util[managed],
                                 rho_other_static=util[[p for p in path if p != managed][0]],
                                 high_mode_overload_static=int(any(
                                     (util[p] * MU_W1B + a) > MU_W1B for p in path)),
                                 abs_shat_over_rmin=abs(sv) / rmin)
                    for side, key, tie in (('fresh', 'new', row['tie_mass']['c10']),
                                           ('stale', 'old', row['tie_mass']['c00'])):
                        share = hl['share_' + key]
                        if side == 'fresh':
                            seen = fresh_seen.setdefault((level, row['h']), (hl['regret_new'], share))
                            assert abs(seen[0] - hl['regret_new']) < 1e-12 and abs(seen[1] - share) < 1e-12
                            if ev['age_label'] != 'seconds_1':
                                continue   # fresh side is identical at every age (asserted above)
                        rows.append(dict(base, **feats, side=side,
                                         reg_static=reg_stat, reg_hybrid=hl['regret_' + key],
                                         delta=reg_stat - hl['regret_' + key],
                                         disagree=share if st == 0 else 1 - share,
                                         m0_tie_mass=tie))
        assert c == 0
    df = pd.DataFrame(rows)
    df['h_grid'] = [snap(x, (1 / 3, 1, 3, 10, 30)) for x in df['h_Tint']]
    # one row per regime and grid point: keep the saved h closest to the grid value
    df['snap_err'] = (df['h_Tint'] / df['h_grid'] - 1).abs()
    keep = df[df.h_grid.notna()].sort_values('snap_err').drop_duplicates(
        ['regime', 'level', 'side', 'age', 'h_grid'])
    df['on_grid'] = df.index.isin(keep.index)
    return df


# ---------------------------------------------------------------- X-CTMC grids
def load_xctmc(name):
    pred = json.loads((L / name / 'predictions.json').read_text())
    exposed = set(pred['pilot_exposed_regimes'])
    rows = []
    for f in sorted(glob.glob(str(L / name / 'raw/*.json'))):
        r = json.loads(Path(f).read_text())
        g = r['regime']
        if g['id'] in exposed or r['status'] != 'COMPLETED':
            continue
        A, B, u = g['A'], g['B'], g['u']
        util = dict(A_stay=(A['load'] + u) / A['mu'], B_stay=B['load'] / B['mu'],
                    A_switch=A['load'] / A['mu'], B_switch=(B['load'] + u) / B['mu'])
        hi = dict(A_stay=A['load'] + u + A['alpha'] > A['mu'], B_stay=B['load'] + B['alpha'] > B['mu'],
                  A_switch=A['load'] + A['alpha'] > A['mu'], B_switch=B['load'] + u + B['alpha'] > B['mu'])
        idx = {(x['rule'], round(x['h_T_int'], 6), round(x['tau_T_int'], 6)): x for x in r['rows']}
        # r_min proxy: C_ref/h at h = 100 T_int (C_ref/h -> min(r_stay, r_switch) as h grows)
        rmin = idx[('M0', 100, 1)]['C_ref'] / idx[('M0', 100, 1)]['h']
        s, sh, Tint = r['s'], r['s_hat'], r['T_int']
        for (rule, hT, tT), S in idx.items():
            if rule != 'Stationary_hat' or S['status'] != 'COMPLETED':
                continue
            st = 1 if sh < 0 else 0
            assert S['p_new'] in (0., 1.) and S['p_new'] == st
            path = ('A_switch', 'B_switch') if st else ('A_stay', 'B_stay')
            managed = 'B_switch' if st else 'A_stay'
            other = [p for p in path if p != managed][0]
            base = dict(grid=name, regime=g['id'], stratum=g['stratum'], h_Tint=hT, tau_Tint=tT,
                        h=S['h'], T_int=Tint, s=s, s_hat=sh, sign_correct=bool(np.sign(s) == np.sign(sh)),
                        static_action=st, abs_s_over_rmin=abs(s) / rmin, abs_shat_over_rmin=abs(sh) / rmin,
                        rmin_proxy=rmin, rho_max_static=max(util[p] for p in path),
                        rho_managed_static=util[managed], rho_other_static=util[other],
                        rho_max_other_action=max(util[p] for p in (('A_stay', 'B_stay') if st else ('A_switch', 'B_switch'))),
                        high_mode_overload_static=int(any(hi[p] for p in path)),
                        kappa_managed_static_over_Tint=(B if st else A)['kappa'] / Tint,
                        kappa_min_over_Tint=min(A['kappa'], B['kappa']) / Tint,
                        alpha_ratio_managed_static=(B if st else A)['alpha'] / max((B if st else A)['load'], 1e-12),
                        alpha_over_mu_managed_static=(B if st else A)['alpha'] / (B if st else A)['mu'],
                        mu_ratio=max(A['mu'], B['mu']) / min(A['mu'], B['mu']),
                        u_over_mu_managed=u / (B if st else A)['mu'], C_ref=S['C_ref'])
            for rule_h in ('Hybrid_hat', 'Hybrid_true'):
                H = idx[(rule_h, hT, tT)]
                M0 = idx[('M0', hT, tT)]
                if H['status'] != 'COMPLETED':
                    continue
                for side in ('fresh', 'stale'):
                    p = H['p_new'] if side == 'fresh' else H['p_old']
                    rows.append(dict(base, hybrid=rule_h, side=side,
                                     reg_static=S['regret_%s_pct_C_ref' % side],
                                     reg_hybrid=H['regret_%s_pct_C_ref' % side],
                                     delta=S['regret_%s_pct_C_ref' % side] - H['regret_%s_pct_C_ref' % side],
                                     disagree=abs(p - st),
                                     m0_tie_share=M0['tie_share_%s' % side],
                                     m0_disagree_static=abs((M0['p_new'] if side == 'fresh' else M0['p_old']) - st)))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- GEANT synthetic E4 / E4b
SCALES = {'Hybrid-noise_m50': .5, 'Hybrid-noise_m25': .75, 'Hybrid-i': 1.,
          'Hybrid-noise_p25': 1.25, 'Hybrid-noise_p50': 1.5}


def load_geant():
    tr = json.loads((L / 'e4/training_checks.json').read_text())
    regs = tr['regimes'] if isinstance(tr['regimes'], list) else list(tr['regimes'].values())
    rhat = {x['regime']: np.asarray(x['rhat']['i'], dtype=float) for x in regs}
    tie_train = {x['regime']: x['fresh_tie_share'] for x in regs}
    spec = {x['id']: x for x in json.loads((ROOT / 'results/ext_validity/ev_te/regimes.json').read_text())}
    cells, inst = [], []
    for seed_dir in ('e4', 'e4b'):
        for reg in sorted(rhat):
            fs = sorted(glob.glob(str(L / seed_dir / 'raw' / f'{reg}_chunk*.npz')))
            Z = [np.load(f) for f in fs]
            meta = json.loads(Path(fs[0]).with_suffix('.json').read_text())
            V = np.concatenate([z['V'] for z in Z])
            D = np.concatenate([z['decisions'] for z in Z])
            T = np.concatenate([z['tie_flags'] for z in Z])
            pipes = list(Z[0]['pipelines'])
            hm, tm = Z[0]['h_mult'], Z[0]['tau_mult']
            n, ix = len(V), np.arange(len(V))
            astar = int(np.argmin(rhat[reg]))            # stationary rule (i): lowest training rate
            # check: M0-tie-i at M0 ties equals the stationary action
            ti = D[:, pipes.index('M0-tie-i')][T[:, pipes.index('M0')]]
            assert (ti == astar).all(), reg
            r = rhat[reg]
            sp = spec[reg]
            util = json.loads(sp['max_action_mean_utilization']) if isinstance(sp['max_action_mean_utilization'], str) else sp['max_action_mean_utilization']
            feats = dict(seed=seed_dir, regime=reg, set=sp['set'], rho_peak=float(sp['rho']),
                         beta=float(sp['beta']), slow=int(sp['slow']), static_action=astar,
                         r_stay=r[0], r_switch=r[1], abs_s_over_rmin=abs(r[1] - r[0]) / r.min(),
                         util_static=float(util[astar]), util_other=float(util[1 - astar]),
                         T_int=meta['T_int'], train_fresh_tie=tie_train[reg])
            m1 = D[:, pipes.index('M1_new'), 0, 0, :]
            for side, tlist in (('fresh', [0]), ('stale', [0, 1, 2])):
                si = 0 if side == 'fresh' else 1
                for t in tlist:
                    for k in range(len(hm)):
                        cref = V[ix, m1[:, k], k].mean()
                        d = D[:, pipes.index('Hybrid-i'), si, t, k]
                        gain = V[:, astar, k] - V[ix, d, k]          # per instance, Mb*s; >0 hybrid better
                        dis = d != astar
                        m0d = D[:, pipes.index('M0'), si, t, k]
                        m0tie = T[:, pipes.index('M0'), si, t, k]
                        strict_opp = (m0d != astar) & ~m0tie
                        scale_dis = {sc: D[:, pipes.index(p), si, t, k] != astar for p, sc in SCALES.items()}
                        gpos = gain[dis & (gain > 0)]
                        gneg = gain[dis & (gain < 0)]
                        top5 = np.sort(gpos)[::-1][:5].sum() / gpos.sum() if gpos.sum() > 0 else np.nan
                        row = dict(feats, side=side, tau_mult=float(tm[t]) if side == 'stale' else 0.,
                                   h_mult=int(hm[k]), N=n, C_ref=cref,
                                   delta=100 * gain.mean() / cref,
                                   delta_se=100 * gain.std(ddof=1) / math.sqrt(n) / cref,
                                   delta_abs_per_decision=gain.mean(),
                                   disagree=dis.mean(), n_disagree=int(dis.sum()),
                                   m0_tie_share=m0tie.mean(),
                                   m0_tie_at_disagree=int((dis & m0tie).sum()),
                                   m0_strict_opposite=int(strict_opp.sum()),
                                   dis_beyond_x1_25=int((dis & scale_dis[1.25]).sum()),
                                   dis_beyond_x1_5=int((dis & scale_dis[1.5]).sum()),
                                   dis_beyond_x0_75=int(scale_dis[.75].sum()),
                                   dis_beyond_x0_5=int(scale_dis[.5].sum()),
                                   n_right=int((dis & (gain > 0)).sum()), n_wrong=int((dis & (gain < 0)).sum()),
                                   n_equal=int((dis & (gain == 0)).sum()),
                                   gain_right_sum=float(gpos.sum()), loss_wrong_sum=float(-gneg.sum()),
                                   top5_share_of_right_gain=top5,
                                   m1_agrees_with_hybrid_at_dis=int((dis & (m1[:, k] == d)).sum()))
                        cells.append(row)
                        for i in np.flatnonzero(dis):
                            inst.append(dict(seed=seed_dir, regime=reg, side=side, tau_mult=row['tau_mult'],
                                             h_mult=int(hm[k]), instance=i, gain=gain[i],
                                             gain_pct=100 * gain[i] / cref,
                                             V_static=V[i, astar, k], V_hybrid=V[i, d[i], k],
                                             V_static_over_mean=V[i, astar, k] / V[:, astar, k].mean(),
                                             m1_choice=int(m1[i, k]), hybrid_choice=int(d[i]),
                                             ratio_bracket=('>1.5' if scale_dis[1.5][i] else
                                                            '(1.25,1.5]' if scale_dis[1.25][i] else '(1,1.25]')))
    return pd.DataFrame(cells), pd.DataFrame(inst)


# ---------------------------------------------------------------- X4b real GEANT matrices
def load_x4b():
    conf = {r['id']: r for r in json.loads((L / 'x4b/configuration.json').read_text())['regimes']}
    cells, inst = [], []
    for f in sorted(glob.glob(str(L / 'x4b/truth/records/*.npz'))):
        z = np.load(f)
        meta = json.loads(Path(f).with_suffix('.json').read_text())
        reg, date = meta['regime'], meta['date']
        sh = float(z['s_hat_Mbit'][0])
        st = int(sh < 0)
        pb = conf[reg]['path_bottleneck_indices_after']
        bott = (json.loads(pb) if isinstance(pb, str) else pb)[st]
        hs = z['h_seconds']
        dec, tie, V = z['decisions'], z['tie_flags'], z['V']
        n = dec.shape[0]
        for si, side in enumerate(z['sides']):
            if si == 0:
                gap = z['M0_predicted_fresh'][:, 1, :] - z['M0_predicted_fresh'][:, 0, :]
            else:
                gap = z['M0_predicted_stale'][:, si - 1, 1, :] - z['M0_predicted_stale'][:, si - 1, 0, :]
            for k, h in enumerate(hs):
                cref = z['C_ref'][:, k].mean()
                cref = cref if cref > 0 else np.nan   # empty-network cells: percentage undefined
                assert (dec[:, 2, si, k] == st).all()
                gain = -z['paired_Hybrid_minus_Stationary'][:, si, k]   # >0 hybrid better
                dis = dec[:, 1, si, k] != st
                ratio = np.abs(gap[:, k]) / (h * abs(sh))
                strict_opp = (dec[:, 0, si, k] != st) & ~tie[:, 0, si, k]
                cells.append(dict(regime=reg, date=date, side=side, h_s=int(h), evaluable=bool(z['evaluable'][k]),
                                  N=n, C_ref=cref, delta=100 * gain.mean() / cref,
                                  delta_se=100 * gain.std(ddof=1) / math.sqrt(n) / cref,
                                  delta_abs=gain.mean(), disagree=dis.mean(), n_disagree=int(dis.sum()),
                                  m0_tie_share=tie[:, 0, si, k].mean(),
                                  m0_tie_at_disagree=int((dis & tie[:, 0, si, k]).sum()),
                                  m0_strict_opposite=int(strict_opp.sum()),
                                  median_ratio_strict_opposite=float(np.median(ratio[strict_opp])) if strict_opp.any() else np.nan,
                                  n_right=int((dis & (gain > 0)).sum()), n_wrong=int((dis & (gain < 0)).sum()),
                                  n_equal=int((dis & (gain == 0)).sum()),
                                  ref_agrees_hybrid_at_dis=int((dis & (z['reference_decision'][:, k] == dec[:, 1, si, k])).sum()),
                                  static_action=st, s_hat=sh))
                for i in np.flatnonzero(dis):
                    inst.append(dict(regime=reg, date=date, side=side, h_s=int(h), instance=i, gain=gain[i],
                                     gain_pct=100 * gain[i] / cref, fluid_gap=gap[i, k], h_abs_shat=h * abs(sh),
                                     ratio=ratio[i], m0_tie=bool(tie[i, 0, si, k]),
                                     ref_choice=int(z['reference_decision'][i, k]), hybrid_choice=int(dec[i, 1, si, k]),
                                     static_path_bottleneck_backlog_Mbit=float(z['fresh_queues'][i, bott]),
                                     util_static_path=float(z['path_utilization'][i, si, st]),
                                     util_other_path=float(z['path_utilization'][i, si, 1 - st])))
    return pd.DataFrame(cells), pd.DataFrame(inst)


# ---------------------------------------------------------------- X5c (decisions only, no truth)
def load_x5c():
    rows = []
    for arm in ('arm_A', 'arm_B'):
        for f in sorted(glob.glob(str(L / 'x5c_alarm' / arm / 'step0/test/*.npz'))):
            z = np.load(f)
            meta = json.loads(Path(f).with_suffix('.json').read_text())
            if 'decisions' not in z.files:   # ALARM_RARE record: no decisions were made
                continue
            dec, tie = z['decisions'], z['tie_flags']
            if dec.shape[0] == 0:
                continue
            sh = float(z['s_hat_Mbit'][0])
            st = int(sh < 0)
            for si, side in enumerate(z['sides']):
                gap = (z['M0_predicted_fresh'][:, 1] - z['M0_predicted_fresh'][:, 0] if si == 0 else
                       z['M0_predicted_stale'][:, si - 1, 1] - z['M0_predicted_stale'][:, si - 1, 0])
                for k, h in enumerate(z['h_seconds']):
                    dis = dec[:, 1, si, k] != st
                    opp = (dec[:, 0, si, k] != st) & ~tie[:, 0, si, k]
                    ratio = np.abs(gap[:, k]) / (h * abs(sh))
                    rows.append(dict(arm=arm, regime=meta['regime'], date=meta['date'], side=side, h_s=int(h),
                                     N=dec.shape[0], n_disagree=int(dis.sum()),
                                     m0_tie=int(tie[:, 0, si, k].sum()), m0_strict_opposite=int(opp.sum()),
                                     m0_tie_at_disagree=int((dis & tie[:, 0, si, k]).sum()),
                                     max_ratio_strict_opposite=float(ratio[opp].max()) if opp.any() else np.nan,
                                     median_ratio_strict_opposite=float(np.median(ratio[opp])) if opp.any() else np.nan))
    return pd.DataFrame(rows)


NEAR_EMPTY = ('G1_r80_b3_s1', 'G2_r80_b3_s1', 'G3_r80_b3_s1')   # training r_Stay < 1 Mb


def counts(df, keys):
    return df.groupby(keys, as_index=False).agg(
        n=('delta', 'size'), mean=('delta', 'mean'), median=('delta', 'median'),
        n_ge_0_10=('delta', lambda v: int((v >= .1).sum())), n_better=('delta', lambda v: int((v > THR).sum())),
        n_worse=('delta', lambda v: int((v < -THR).sum())), min=('delta', 'min'))


def derived(wg, xh, gsel, gi, x4c, x4i, x5, gc):
    """Numbers quoted in REPORT_S0.md; every one recomputed here from the saved-data tables."""
    gate = [counts(wg, ['level', 'side', 'h_grid']).assign(source='W1b'),
            counts(xh[xh.tau_Tint == 1], ['side', 'h_Tint']).assign(source='XCTMC_both_grids_hat_tau1'),
            counts(xh[(xh.tau_Tint == 1) & (xh.abs_s_over_rmin < .1)], ['side', 'h_Tint']).assign(source='XCTMC_abs_s_rmin_lt_0.1'),
            counts(gsel[~gsel.regime.isin(NEAR_EMPTY)], ['side', 'h_mult']).assign(source='GEANT_17x2_minus_near_empty'),
            counts(gsel, ['side', 'h_mult']).assign(source='GEANT_17x2_all'),
            counts(x4c[x4c.evaluable], ['side', 'h_s']).assign(source='X4b_evaluable_records')]
    pd.concat(gate, ignore_index=True).to_csv(OUT / 'gate_counts.csv', index=False)
    mm = wg[wg.level == 'mm1'].assign(shat_ratio=lambda d: d.s_hat / d.s)
    gi1 = gi[(gi.side == 'fresh') | (gi.tau_mult == 1.)]
    dis_reg = gsel[gsel.n_disagree > 0].groupby('regime').static_action.first()
    x4d = x4c[x4c.n_disagree > 0]
    key = dict(
        note='post hoc, exploratory; cells of one regime/day are not independent',
        w1b=dict(regimes=int(wg.regime.nunique()), mm1_sign_correct_all=bool(mm.sign_correct.all()),
                 mm1_worse_rows=int((mm.delta < -THR).sum()),
                 mm1_worse_shat_ratio_max=float(mm[mm.delta < -THR].shat_ratio.max()),
                 mm1_min_delta_when_shat_ratio_ge_0_5=float(mm[mm.shat_ratio >= .5].delta.min()),
                 true_s_min_delta=float(wg[wg.level == 'true_s'].delta.min())),
        xctmc=dict(regimes=int((xh.grid + xh.regime).nunique()),
                   sign_wrong_regimes=int((xh[~xh.sign_correct].grid + xh[~xh.sign_correct].regime).nunique()),
                   min_delta_tau1=float(xh[xh.tau_Tint == 1].delta.min())),
        geant=dict(regimes_with_any_disagreement=int(len(dis_reg)),
                   static_action_of_those=sorted(set(int(v) for v in dis_reg)),
                   m0_tie_at_disagreement=int(gsel.m0_tie_at_disagree.sum()),
                   all_tau_cells=int(len(gc)), all_tau_disagreements=int(gc.n_disagree.sum()),
                   all_tau_disagreements_at_m0_tie=int(gc.m0_tie_at_disagree.sum()),
                   fresh=dict(dis=int(gsel[gsel.side == 'fresh'].n_disagree.sum()),
                              right=int(gsel[gsel.side == 'fresh'].n_right.sum()),
                              wrong=int(gsel[gsel.side == 'fresh'].n_wrong.sum()),
                              m1_agrees=int(gsel[gsel.side == 'fresh'].m1_agrees_with_hybrid_at_dis.sum()),
                              ratio_gt_1_5=int((gi1[gi1.side == 'fresh'].ratio_bracket == '>1.5').sum()),
                              V_static_over_mean_median=float(gi1[gi1.side == 'fresh'].V_static_over_mean.median())),
                   stale_tau1=dict(dis=int(gsel[gsel.side == 'stale'].n_disagree.sum()),
                                   right=int(gsel[gsel.side == 'stale'].n_right.sum()),
                                   wrong=int(gsel[gsel.side == 'stale'].n_wrong.sum()),
                                   gain_sum=float(gsel[gsel.side == 'stale'].gain_right_sum.sum()),
                                   loss_sum=float(gsel[gsel.side == 'stale'].loss_wrong_sum.sum()),
                                   ratio_gt_1_5=int((gi1[gi1.side == 'stale'].ratio_bracket == '>1.5').sum())),
                   top5_share_median=gsel[gsel.n_disagree >= 10].groupby('side').top5_share_of_right_gain.median().to_dict()),
        x4b=dict(records=int(x4c[['regime', 'date']].drop_duplicates().shape[0]),
                 disagreement_cells=int(len(x4d)), days=sorted(set(x4d.regime + ' ' + x4d.date)),
                 instances=int(len(x4i)), right=int((x4i.gain > 0).sum()), m0_tie=int(x4i.m0_tie.sum()),
                 ref_agrees=int((x4i.ref_choice == x4i.hybrid_choice).sum()),
                 ratio_min=float(x4i.ratio.min()), ratio_median=float(x4i.ratio.median()), ratio_max=float(x4i.ratio.max()),
                 backlog_static_bottleneck_median_Mbit=float(x4i.static_path_bottleneck_backlog_Mbit.median()),
                 delta_by_h=x4d[x4d.side == 'fresh'].set_index('h_s')[['delta', 'delta_se']].to_dict('index')),
        x5c=dict(disagreement_records=sorted(set(x5[x5.n_disagree > 0].arm + ' ' + x5[x5.n_disagree > 0].regime + ' ' + x5[x5.n_disagree > 0].date)),
                 totals=x5.groupby('arm')[['N', 'n_disagree', 'm0_tie_at_disagree']].sum().to_dict('index')))
    (OUT / 'key_numbers.json').write_text(json.dumps(key, indent=1, default=float) + '\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    spear = []
    # ---- W1b
    w = load_w1b()
    w.to_csv(OUT / 'w1b_pairs.csv', index=False)
    wg = w[w['on_grid'] & w['age'].isin(['seconds_1', 'Tint_1'])]
    wg = wg[(wg.side == 'fresh') | (wg.age == 'Tint_1')]
    s_w = summarize(wg, ['level', 'side', 'h_grid'])
    s_w.insert(0, 'source', 'W1b_CTMC_homog')
    wf = ['abs_s_over_rmin', 'kappa_over_Tint', 'T_int', 'a_over_mu', 'rho_max_static',
          'rho_managed_static', 'rho_other_static', 'm0_tie_mass', 'u', 'high_mode_overload_static',
          'static_action', 'disagree']
    spear += spearman_table(wg[wg.level == 'true_s'], ['side', 'h_grid'], wf, 'W1b_true_s')
    # group tables (true s, h grid, fresh + stale tau=T_int)
    grp = []
    for feat, bins in (('abs_s_over_rmin', [0, .1, .3, 1, np.inf]), ('kappa_over_Tint', [0, .01, .05, .2, np.inf]),
                       ('rho_max_static', [0, .8, .9, .95, 1.01]), ('a_over_mu', [0, .45, .65, 1])):
        t = wg[wg.level == 'true_s'].copy()
        t['bin'] = pd.cut(t[feat], bins, right=False).astype(str)
        g = summarize(t, ['side', 'h_grid', 'bin'])
        g.insert(0, 'feature', feat)
        grp.append(g)
    pd.concat(grp).to_csv(OUT / 'w1b_groups.csv', index=False)

    # ---- X-CTMC
    xs = pd.concat([load_xctmc('x_ctmc'), load_xctmc('x_ctmc_c')], ignore_index=True)
    xs.to_csv(OUT / 'xctmc_pairs.csv', index=False)
    xh = xs[(xs.hybrid == 'Hybrid_hat') & ((xs.side == 'fresh') & (xs.tau_Tint == 1) | (xs.side == 'stale'))]
    s_x = summarize(xh, ['grid', 'side', 'tau_Tint', 'h_Tint'])
    s_x.insert(0, 'source', 'XCTMC_heterog')
    xf = ['abs_s_over_rmin', 'abs_shat_over_rmin', 'kappa_managed_static_over_Tint', 'kappa_min_over_Tint',
          'T_int', 'rho_max_static', 'rho_managed_static', 'rho_other_static', 'rho_max_other_action',
          'alpha_ratio_managed_static', 'alpha_over_mu_managed_static', 'high_mode_overload_static',
          'm0_tie_share', 'mu_ratio', 'u_over_mu_managed', 'static_action', 'disagree']
    xx = xh[xh.tau_Tint == 1].copy()
    xx['grid_all'] = 'both_grids'
    spear += spearman_table(xx, ['grid_all', 'side', 'h_Tint'], xf, 'XCTMC_hat_tau1')
    grp = []
    for feat, bins in (('abs_s_over_rmin', [0, .1, .3, 1, np.inf]), ('rho_max_static', [0, .7, .8, .9, 1.01]),
                       ('kappa_managed_static_over_Tint', [0, .1, .3, 1, np.inf]),
                       ('high_mode_overload_static', [-.5, .5, 1.5]), ('m0_tie_share', [-.01, .05, .3, .7, 1.01])):
        t = xx.copy()
        t['bin'] = pd.cut(t[feat], bins, right=False).astype(str)
        g = summarize(t, ['side', 'h_Tint', 'bin'])
        g.insert(0, 'feature', feat)
        grp.append(g)
    pd.concat(grp).to_csv(OUT / 'xctmc_groups.csv', index=False)

    # ---- GEANT synthetic
    gc, gi = load_geant()
    gc.to_csv(OUT / 'geant_cells.csv', index=False)
    gi.to_csv(OUT / 'geant_disagreement_instances.csv', index=False)
    gsel = gc[(gc.side == 'fresh') | (gc.tau_mult == 1.)]
    s_g = summarize(gsel, ['seed', 'side', 'h_mult'], unit='regime')
    s_g.insert(0, 'source', 'GEANT_synth')
    gm = gsel.groupby(['regime', 'side', 'h_mult'], as_index=False).agg(
        delta=('delta', 'mean'), disagree=('disagree', 'mean'), abs_s_over_rmin=('abs_s_over_rmin', 'first'),
        rho_peak=('rho_peak', 'first'), beta=('beta', 'first'), slow=('slow', 'first'),
        util_static=('util_static', 'first'), util_other=('util_other', 'first'), T_int=('T_int', 'first'),
        m0_tie_share=('m0_tie_share', 'mean'), C_ref=('C_ref', 'mean'), static_action=('static_action', 'first'))
    s_gm = summarize(gm, ['side', 'h_mult'], unit='regime (2-seed mean)')
    s_gm.insert(0, 'source', 'GEANT_synth_seedmean')
    gf = ['abs_s_over_rmin', 'rho_peak', 'beta', 'slow', 'util_static', 'util_other', 'T_int', 'm0_tie_share',
          'static_action', 'disagree']
    spear += spearman_table(gm, ['side', 'h_mult'], gf, 'GEANT_seedmean')
    # mechanism decomposition pooled
    agg = gsel.groupby(['side', 'h_mult'], as_index=False)[[
        'N', 'n_disagree', 'm0_tie_at_disagree', 'm0_strict_opposite', 'dis_beyond_x1_25', 'dis_beyond_x1_5',
        'n_right', 'n_wrong', 'n_equal', 'gain_right_sum', 'loss_wrong_sum', 'm1_agrees_with_hybrid_at_dis']].sum()
    agg.to_csv(OUT / 'geant_mechanism.csv', index=False)

    # ---- X4b
    x4c, x4i = load_x4b()
    x4c.to_csv(OUT / 'x4b_cells.csv', index=False)
    x4i.to_csv(OUT / 'x4b_disagreement_instances.csv', index=False)
    # ---- X5c
    x5 = load_x5c()
    x5.to_csv(OUT / 'x5c_cells.csv', index=False)
    x5s = x5.groupby(['arm', 'side', 'h_s'], as_index=False)[['N', 'n_disagree', 'm0_tie', 'm0_strict_opposite']].sum()
    x5s.to_csv(OUT / 'x5c_summary.csv', index=False)

    pd.concat([s_w, s_x, s_g, s_gm], ignore_index=True).to_csv(OUT / 'summary_by_h.csv', index=False)
    pd.DataFrame(spear).to_csv(OUT / 'feature_spearman.csv', index=False)
    derived(wg, xh, gsel, gi, x4c, x4i, x5, gc)
    print('wrote', sorted(p.name for p in OUT.iterdir()))


if __name__ == '__main__':
    main()
