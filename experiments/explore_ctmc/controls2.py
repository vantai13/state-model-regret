"""Doan Van Tai — controls of SPEC_v2 §6 for ctmc-v2 [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.controls2 --attempt 02            # (a) (b) (c) (d-truth) (f) (g)
  python -m experiments.explore_ctmc.controls2 --attempt 02 --only a b # subset
  python -m experiments.explore_ctmc.controls2 --bitid OUT.json        # (e) zero-fit JSON for a host comparison

Finite-h truth is computed only at a_s = 0 (control (a)) and at the two CONTROL_REGIMES; both are excluded from every
case list and card. Results: results/explore_ctmc/controls_l73/attempt<NN>/.
"""
import argparse
from fractions import Fraction as F
import json
import math
from pathlib import Path
import socket
import time

import numpy as np

from experiments.explore_ctmc import ctmc, ctmc2, mc2
from experiments.explore_ctmc.design import rational

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc/controls_l73'
A_REGIMES = [(F(7), F(15, 2), F(1), F(1, 5)), (F(13, 2), F(8), F(1, 2), F(1)), (F(8), F(7), F(1), F(2))]
A_HS = [F(1, 2), F(3), F(20)]
PCT, SHARE, REL = 1e-6, 1e-9, 1e-9


def _worst(store, key, value, limit):
    v = abs(float(value))
    rec = store.setdefault(key, dict(max=0.0, limit=limit))
    rec['max'] = max(rec['max'], v)


def ctrl_a():
    """a_s = 0 against ctmc-v1 (kappa = T_f): zero fit, D22 zero fit, truth and D22 truth."""
    worst, per = {}, []
    for lamA, lamB, u, k in A_REGIMES:
        z1 = ctmc.evaluate_d22_m0(lamA, lamB, u, k, A_HS)
        z2 = ctmc2.evaluate_d22_m0(lamA, lamB, u, k, 10 * k, F(6), F(0), A_HS, relax=False)
        for key in ('z_inf', 'z_inf_ko', 'z_F_inf', 'z_V_inf', 'M0_regret_new_pred', 'M0_regret_old_pred'):
            _worst(worst, f'zf_{key}', z1[key] - z2[key], PCT)
        _worst(worst, 'zf_T_int_rel', (z1['T_int_max'] - z2['T_int_max']) / z1['T_int_max'], REL)
        for r1, r2 in zip(z1['h'], z2['h']):
            for key in ('F_new', 'F_old', 'F_cb'):
                tie = max(r1.get('tie_new', 0), r1.get('tie_old', 0), r1.get('tie_cb', 0))
                _worst(worst, f'zf_{key}_minus_tie', max(0.0, abs(r1[key] - r2[key]) - tie), SHARE)
            if 'z_pred_first_order' in r1:
                _worst(worst, 'zf_z_pred1', r1['z_pred_first_order'] - r2['z_pred_first_order'], PCT)
        t1 = ctmc.evaluate_d22(lamA, lamB, u, k, A_HS)
        t2 = ctmc2.evaluate_d22(lamA, lamB, u, k, 10 * k, F(6), F(0), A_HS)
        for r1, r2 in zip(t1['h'], t2['h']):
            for key in ('G_S', 'G_M', 'G_SM', 'Gamma', 'S', 'M', 'G_S_hybrid', 'G_S_ko'):
                _worst(worst, f'truth_{key}', r1[key] - r2[key], PCT)
            for key in ('L00', 'L01', 'L10', 'L11'):
                _worst(worst, 'truth_L_rel', (r1[key] - r2[key]) / r1[key], REL)
            for t in r2['regret']:
                _worst(worst, 'truth_regret', r1['regret'][t] - r2['regret'][t], PCT)
            tie = max(r1['tie_mass'].values())
            for t in r2['shares']:
                _worst(worst, 'truth_share_minus_tie', max(0.0, abs(r1['shares'][t] - r2['shares'][t]) - tie), SHARE)
            for key in ('F', 'V', 'F1', 'V1'):
                _worst(worst, f'truth_d22_{key}', r1['d22'][key] - r2['d22'][key], PCT)
        per.append(dict(regime=[str(x) for x in (lamA, lamB, u, k)], N=z2['N']))
    ok = all(v['max'] <= v['limit'] for v in worst.values())
    return dict(PASS=ok, worst=worst, regimes=per)


B_CHAINS = [(F(8), F(1, 5), F(2), F(4), F(2)), (F(15, 2), F(1), F(100), F(3), F(3)),
            (F(17, 2), F(1, 5), F(20), *ctmc2.amplitudes(F(1, 20))), (F(7), F(1), F(10), F(3), F(3)),
            # attempt03: chains with an MPM mode (sigma_f = -1, sigma_s = +1, a_s > mu - load)
            (F(9), F(1, 5), F(20), F(4), F(2)), (F(17, 2), F(1), F(10), F(3), F(3)), (F(9), F(1, 5), F(2), F(4), F(2))]


def _grid(Tf, t_end, hs, step):
    """attempt03: fine steps where the fast exponential varies (the attempt02 reference had ~1e-6 trapezoid error in C
    near t = 0 for T_f = 1/5), the attempt02 step elsewhere."""
    fine = np.linspace(0, min(10 * float(Tf), t_end), 200001)
    rest = np.arange(10 * float(Tf), t_end, step)
    return np.unique(np.concatenate([fine, rest, [h for h in hs if h != math.inf], [t_end]]))


def ctrl_b(nmax=80, step=2.5e-4):
    """M0 closed form against a numerical reflected rollout (cumulative trapezoid of d, numerical running min)."""
    res, n_mpm = [], 0
    for load, Tf, Ts, af, as_ in B_CHAINS:
        hs = [float(Tf) / 2, float(Tf), float(Ts), 10 * float(Ts), math.inf]
        got, T = ctmc2.m0_vhat(load, Tf, Ts, af, as_, nmax, hs, return_T=True)
        L = float(load) - ctmc2.MU
        sf, ss = ctmc2.sigmas()
        for m in range(4):
            sh = ctmc2.mode_shape(load, Tf, Ts, af, as_, m)
            n_mpm += sh['shape'] == 'MPM'
            idx = np.arange(nmax + 1) * 4 + m
            t_end = max(10 * float(Ts), float(T[idx].max())) * 1.05 + 1
            if sh['shape'] == 'MPM':
                t_end = max(t_end, 2 * sh['t2'] + 10 * float(Ts))
            grid = _grid(Tf, t_end, hs, step)
            d = L + sf[m] * float(af) * np.exp(-2 * grid / float(Tf)) + ss[m] * float(as_) * np.exp(-2 * grid / float(Ts))
            C = np.concatenate([[0.0], np.cumsum(0.5 * (d[1:] + d[:-1]) * np.diff(grid))])
            Mrun = np.minimum.accumulate(C)
            for n in range(nmax + 1):
                q = C + np.maximum(n, -Mrun)
                cum = np.concatenate([[0.0], np.cumsum(0.5 * (q[1:] + q[:-1]) * np.diff(grid))])
                if q[-1] > 1e-9:
                    raise ArithmeticError('numerical rollout not drained at t_end')
                for j, h in enumerate(hs):
                    want = float(cum[-1] if h == math.inf else cum[np.searchsorted(grid, h)])
                    g = float(got[j][4 * n + m])
                    rel = abs(g - want) / max(abs(want), 1.0)
                    res.append(dict(chain=[str(x) for x in (load, Tf, Ts, af, as_)], m=m, shape=sh['shape'], n=n,
                                    h=str(h), closed=g, numeric=want, rel=rel))
    worst = max(r['rel'] for r in res)
    mpm = [r for r in res if r['shape'] == 'MPM']
    return dict(PASS=worst <= 1e-6, worst_rel=worst, worst_rel_MPM=max((r['rel'] for r in mpm), default=None),
                n_checks=len(res), n_checks_MPM=len(mpm), n_mode_chains_MPM=n_mpm,
                worst_cases=sorted(res, key=lambda r: -r['rel'])[:5])


def control_hs(regime, mults=(F(3, 10), F(1), F(3), F(10))):
    lamA, lamB, u, Tf, Ts, af, as_ = regime
    z = ctmc2.evaluate_m0(lamA, lamB, u, Tf, Ts, af, as_, [F(1)], relax=False)
    return [rational(float(m) * z['T_int_max']) for m in mults], z['T_int_max']


def ctrl_c(episodes):
    out = {}
    for j, (name, reg) in enumerate(ctmc2.CONTROL_REGIMES.items()):
        hs, T = control_hs(reg, (F(2),))
        r = mc2.end_to_end(reg, hs[0], episodes, seed=20261104 + j)
        out[name] = dict(r, T_int_max=T)
    return dict(PASS=all(v['PASS'] for v in out.values()), regimes=out)


def ctrl_d_truth():
    reg = ctmc2.CONTROL_REGIMES['C2b']
    hs, T = control_hs(reg, (F(1), F(5)))
    a = ctmc2.evaluate(*reg, hs, disagree=False)
    b = ctmc2.evaluate(*reg, hs, disagree=False, N_scale=2)
    worst = 0.0
    for r1, r2 in zip(a['h'], b['h']):
        for key in ('G_S', 'G_M', 'G_SM', 'Gamma', 'S', 'M'):
            worst = max(worst, abs(r1[key] - r2[key]))
    return dict(PASS=worst <= 0.01, worst_pp=worst, N=a['N'], N2=b['N'], hs=[str(h) for h in hs])


def ctrl_d_zf():
    """SPEC_v2 §6 (d), zero-fit part: N -> 2N at the heaviest case of the case lists (no D22 at 2N)."""
    cases = [c for st in ('asym', 'mid', 'sobol', 'xs')
             for c in json.loads((ROOT / f'results/explore_ctmc/cases_l73/{st}.json').read_text())]
    c = max(cases, key=lambda c: (max(c['N'].values()), c['id']))
    p = [F(x) for x in c['parameters']]
    a = ctmc2.evaluate_m0(*p[:7], c['hs'], c=p[7], relax=False)
    b = ctmc2.evaluate_m0(*p[:7], c['hs'], c=p[7], relax=False, N_scale=2)
    worst = abs(a['z_inf'] - b['z_inf'])
    for r1, r2 in zip(a['h'][:-1], b['h'][:-1]):
        worst = max(worst, abs(r1['z_pred_first_order'] - r2['z_pred_first_order']))
    worst = max(worst, abs(a['z_inf_ko'] - b['z_inf_ko']))
    return dict(PASS=worst <= 0.01, worst_pp=worst, case=c['id'], N=a['N'], N2=b['N'],
                T_int_rel_change=abs(a['T_int_max'] - b['T_int_max']) / a['T_int_max'])


def ctrl_f():
    rows = []
    for name, reg in ctmc2.CONTROL_REGIMES.items():
        hs, T = control_hs(reg)
        out = ctmc2.evaluate(*reg, hs, disagree=False)
        for r in out['h']:
            rows.append(dict(regime=name, h=r['h'], S=r['S'], M=r['M'], G_M=r['G_M'], G_S=r['G_S'], Gamma=r['Gamma']))
    worst = min(min(r['S'], r['M'], r['G_M']) for r in rows)
    return dict(PASS=worst >= -1e-9, min_of_S_M_GM=worst, rows=rows)


def ctrl_g():
    res = dict(V_two_routes=[], pi_vs_geometric=[], mentor_table=[])
    for name, reg in ctmc2.CONTROL_REGIMES.items():
        lamA, lamB, u, Tf, Ts, af, as_ = reg
        N = ctmc2.choose_N(lamA + u, Tf, Ts, af, as_)
        ch = ctmc2.Chain(lamA + u, Tf, Ts, af, as_, N)
        for h in (0.5, 5.0, 20 * ch.T_int):
            a, b = ch.V([h], reg)[0], ch.V_aug(h, reg)
            res['V_two_routes'].append(dict(regime=name, h=h, rel=float(np.abs(a - b).max() / np.abs(b).max())))
        mg = ctmc2.matrix_geometric(lamA + u, Tf, Ts, af, as_)
        lev = np.array([mg['pi0'] @ np.linalg.matrix_power(mg['R'], n) for n in range(min(N + 1, 400))]).sum(axis=1)
        tr = ch.pi.reshape(-1, 4).sum(axis=1)[:lev.size]
        res['pi_vs_geometric'].append(dict(regime=name, N=N, max_abs=float(np.abs(tr - lev).max()),
                                           mean_trunc=ch.r, mean_inf=mg['mean']))
    for f in (F(0), F(1, 20), F(1, 5), F(1, 2)):
        af, as_ = ctmc2.amplitudes(f)
        N = ctmc2.choose_N(F(17, 2), F(1, 2), F(50), af, as_)
        ch = ctmc2.chain(F(17, 2), F(1, 2), F(50), af, as_, N)
        rel = ch.T_relax()
        res['mentor_table'].append(dict(f=str(f), a_f=str(af), a_s=str(as_), N=N, mean_backlog=ch.r, T_int=ch.T_int,
                                        T_relax=rel['T_relax'], T_relax_over_T_int=rel['T_relax'] / ch.T_int,
                                        T_int_approx_3d=ctmc2.tint_approx(F(17, 2), F(1, 2), F(50), af, as_)))
    ok = (all(r['rel'] <= 1e-8 for r in res['V_two_routes'])
          and all(r['max_abs'] <= 1e-10 for r in res['pi_vs_geometric']))
    return dict(PASS=ok, blocking=False, **res)


def bitid(path):
    out = {}
    for name, reg in ctmc2.CONTROL_REGIMES.items():
        out[name] = ctmc2.evaluate_m0(*reg, [F(1), F(10)], relax=True)
    Path(path).write_text(json.dumps(out, indent=0, default=float) + '\n')
    print('wrote', path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--attempt', default='02')
    p.add_argument('--only', nargs='*', default=None)
    p.add_argument('--episodes', type=int, default=200000)
    p.add_argument('--bitid', default=None)
    a = p.parse_args()
    if a.bitid:
        bitid(a.bitid)
        return
    dest = OUT / f'attempt{a.attempt}'
    dest.mkdir(parents=True, exist_ok=True)
    todo = dict(a=ctrl_a, b=ctrl_b, c=lambda: ctrl_c(a.episodes), d_truth=ctrl_d_truth, d_zf=ctrl_d_zf, f=ctrl_f, g=ctrl_g)
    for name, fn in todo.items():
        if a.only and name not in a.only:
            continue
        path = dest / f'{name}.json'
        if path.exists():
            raise SystemExit(f'{path} exists (write-once)')
        t0 = time.process_time()
        rep = fn()
        rep.update(cpu_seconds=time.process_time() - t0, host=socket.gethostname())
        path.write_text(json.dumps(rep, indent=1, default=float) + '\n')
        print(name, 'PASS' if rep['PASS'] else 'FAIL', f"{rep['cpu_seconds']:.1f}s", flush=True)


if __name__ == '__main__':
    main()
