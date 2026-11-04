"""Doan Van Tai — L7.5 Stage 0 controls (a)-(e) of SPEC_tau §5 [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.controls_tau a|b|c|d|e [--episodes N]   # -> results/explore_ctmc/controls_l75/<x>.json

Criteria were written in SPEC_tau.md before any run. The v1 reference numbers (m0/asym, l72/ZEROFIT_a6_xs.csv) were
computed on the local machine; L7.5 numbers on dt4n-research-01, so (a) allows last-bit differences (relative 1e-12)
and requires identical decisions, as control (a) of L7.3.
"""
import argparse
from fractions import Fraction as F
import json
import math
from pathlib import Path
import socket
import time

import numpy as np

from experiments.explore_ctmc import ctmc, tau as T5
from experiments.explore_ctmc.design import rational

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
DEST = OUT / 'controls_l75'
REL = 1e-12


def rel(a, b):
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


def ctrl_a():
    """tau = 1 reproduces the v1 zero fit: the 10 old regimes (m0/asym) and the 269 x-slice regimes (ZEROFIT_a6_xs)."""
    import pandas as pd
    rows, worst = [], 0.0
    for c in json.loads((OUT / 'cases_l75/old.json').read_text()):
        new = json.loads((OUT / 'm0_l75/old' / f"{c['id']}__t1.json").read_text())
        ref = json.loads((OUT / 'm0/asym' / f"{c['id']}.json").read_text())
        rh = {r['h']: r for r in ref['h']}
        common = [r for r in new['h'] if r['h'] in rh]
        d = [rel(new['z_inf'], ref['z_inf'])]
        share = [abs(new['h'][-1]['F_old'] - ref['h'][-1]['F_old']), abs(new['h'][-1]['F_new'] - ref['h'][-1]['F_new'])]
        for r in common:
            if r['h'] != 'inf':
                d.append(rel(r['z_pred_first_order'], rh[r['h']]['z_pred_first_order']))
            share += [abs(r['F_old'] - rh[r['h']]['F_old']), abs(r['F_new'] - rh[r['h']]['F_new'])]
        worst = max(worst, max(d))
        rows.append(dict(id=c['id'], common_h=[r['h'] for r in common], max_rel=max(d), max_share_diff=max(share)))
    xs_ref = pd.read_csv(OUT / 'l72/ZEROFIT_a6_xs.csv', dtype={'h': str}).set_index('id')
    xs_rows = []
    for c in json.loads((OUT / 'cases_l75/xs.json').read_text()):
        p = [F(x) for x in c['parameters'][:4]]
        new = T5.evaluate_m0(*p, c['hs'], 1)
        r = xs_ref.loc[c['id']]
        d = max(rel(new['z_inf'], r.z_inf), rel(new['h'][0]['z_pred_first_order'], r.z_pred1))
        # the L7.2 CSV stores F_old, F_new at h = inf (zf_report: d['h'][-1]); attempt01 compared h[0] by mistake
        sh = max(abs(new['h'][-1]['F_old'] - r.F_old), abs(new['h'][-1]['F_new'] - r.F_new))
        xs_rows.append(dict(id=c['id'], max_rel=d, max_share_diff=sh))
    allr = rows + xs_rows
    ok = all(r['max_rel'] <= REL for r in allr) and all(r['max_share_diff'] <= 1e-12 for r in allr)
    return dict(criterion=f'relative <= {REL} on z_inf and z_pred1, decision shares equal (<= 1e-12)', PASS=ok,
                old=rows, xs_max_rel=max(r['max_rel'] for r in xs_rows),
                xs_max_share_diff=max(r['max_share_diff'] for r in xs_rows), n_xs=len(xs_rows),
                n_fail=sum(not (r['max_rel'] <= REL and r['max_share_diff'] <= 1e-12) for r in allr))


def ctrl_b():
    """Posterior through expm_multiply vs dense scipy.linalg.expm, both Stay chains of both controls, 4 tau."""
    import scipy.linalg
    out = []
    for name, (lamA, lamB, u, kappa) in T5.CONTROL_REGIMES_L75.items():
        for side, load in (('A', lamA + u), ('B', lamB)):
            N = ctmc.choose_N((lamA if side == 'A' else lamB) + u, kappa)      # NA, NB as in ctmc.evaluate
            st = ctmc.chain(load, kappa, N)
            v = np.random.default_rng(1).standard_normal((st.n, 4))
            for t in (F(1, 100), F(1, 3), F(3), F(30)):
                with T5.at_tau(t):
                    got = ctmc.posterior_mean(st, v)
                P = scipy.linalg.expm(st.Q.toarray() * float(t))
                pi = st.pi.reshape(-1, 2)
                want = (pi[:, :, None] * (P @ v).reshape(-1, 2, 4)).sum(axis=1) / pi.sum(axis=1)[:, None]
                out.append(dict(control=name, side=side, N=N, tau=str(t), err=float(np.abs(got - want).max() / np.abs(v).max())))
    return dict(criterion='max abs error / max|v| <= 1e-10', PASS=all(r['err'] <= 1e-10 for r in out), rows=out)


def ctrl_c(episodes):
    """Monte Carlo end to end with CRN (mc.end_to_end, with D22) at both controls, tau/T_int in {1/10, 3}, h = 3 T_int."""
    from experiments.explore_ctmc import mc
    out = []
    for k, (name, reg) in enumerate(T5.CONTROL_REGIMES_L75.items()):
        Tm = T5.tint_max(*reg)[0]
        h = rational(3 * Tm)
        for j, m in enumerate((F(1, 10), F(3))):
            t = rational(m * Tm)
            t0 = time.process_time()
            with T5.at_tau(t, reg):
                r = mc.end_to_end(*reg, h, episodes, seed=20261105 + 10 * k + j, d22=True)
            Cref = r['exact']['h'][0]['Cref']
            res, unres = {}, {}
            for key, v in r['checks'].items():
                if v['se'] > 0:
                    res[key] = v['z']
                else:                       # no disagreement sampled: MC cannot resolve (amended 04/11, SPEC_tau §5)
                    unres[key] = dict(exact=v['exact'], exact_over_Cref=abs(v['exact']) / Cref, mc=v['mc'])
            ok = all(abs(z) <= 3.5 for z in res.values()) and all(u['exact_over_Cref'] <= 1e-4 for u in unres.values())
            out.append(dict(control=name, tau=str(t), h=str(h), episodes=episodes, PASS=ok,
                            max_abs_z=max(abs(z) for z in res.values()), z=res, unresolved_by_mc=unres,
                            cpu=time.process_time() - t0, tau_in_exact=r['exact']['tau']))
    return dict(criterion='|z| <= 3.5 where se > 0; where se = 0 (MC saw no disagreement) |exact| <= 1e-4 Cref, '
                          'reported as not resolved by MC (amended after a 2,000-episode smoke run, before the run)',
                PASS=all(r['PASS'] for r in out), rows=out)


def ctrl_d():
    """Isolation: names restored after every context; tau = 1 truth after a tau != 1 truth gives the same bits."""
    reg = T5.CONTROL_REGIMES_L75['CT1']
    hs = [F(2), F(8)]
    def dump(d):                                    # the wrapper records tau as a string ('1'), v1 as the int 1
        d = dict(d)
        d.pop('tau')
        return json.dumps(d, default=str)
    first = dump(T5.evaluate(*reg, hs, 1, disagree=False))
    T5.evaluate(*reg, hs, F(7, 3), disagree=False)
    with T5.at_tau(F(1, 5)):
        ctmc.evaluate_m0(*reg, hs)
    again = dump(T5.evaluate(*reg, hs, 1, disagree=False))
    v1 = dump(ctmc.evaluate(*reg, hs, disagree=False))
    return dict(criterion='restored() and identical JSON', restored=T5.restored(), same_after=first == again,
                same_as_v1=first == v1, PASS=T5.restored() and first == again == v1)


def ctrl_e():
    """D22 at tau != 1: marginal of J and the tower check reported by ctmc.evaluate_d22, both controls, two tau."""
    out = []
    for name, reg in T5.CONTROL_REGIMES_L75.items():
        Tm = T5.tint_max(*reg)[0]
        for m in (F(1, 100), F(3)):
            t = rational(m * Tm)
            r = T5.evaluate(*reg, [rational(3 * Tm)], t, d22=True)
            out.append(dict(control=name, tau=str(t), **r['d22_checks']))
    return dict(criterion='marginal_err and tower_err <= 1e-10',
                PASS=all(r['marginal_err'] <= 1e-10 and r['tower_err'] <= 1e-10 for r in out), rows=out)


MENTOR = {   # the mentor's tau table (L7.4/L7.5 message, 04/11): z_inf in % C_ref at absolute tau (s), as printed
    'A_u1-2_lA9_x-1_k1-2': ['-0.38', '-0.67', '-1.22', '-2.37', '-4.05', '-5.92', '-6.54', '-6.57'],
    'A_u1_lA7_x1_k1-2': ['-0.73', '-1.91', '-3.06', '-6.52', '-10.2', '-14.3', '-15.9', '-16.0'],
    'A_u1_lA7_x1-4_k1-2': ['-0.06', '-0.06', '-0.05', '-0.03', '0.77', '2.29', '2.80', '2.80']}
MENTOR_TAU = ['1/100', '1/10', '3/10', '1', '3', '10', '30', '100']


def ctrl_m():
    """Report only: recompute the mentor's table on this host; a cell matches when it rounds to the printed digits."""
    rows = []
    for rid, vals in MENTOR.items():
        ref = json.loads((OUT / 'm0/asym' / f'{rid}.json').read_text())
        p = [F(x) for x in ref['parameters'][:4]]
        for t, v in zip(MENTOR_TAU, vals):
            z = T5.evaluate_m0(*p, [], F(t))['z_inf']
            dec = len(v.split('.')[1])
            rows.append(dict(id=rid, tau=t, mentor=v, ours=z, match=abs(z - float(v)) <= 0.5 * 10 ** -dec + 1e-12))
    return dict(criterion='report only', PASS=True, matches=sum(r['match'] for r in rows), cells=len(rows), rows=rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('which', choices=list('abcdem'))
    ap.add_argument('--episodes', type=int, default=200_000)
    a = ap.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    t0 = time.process_time()
    res = dict(a=ctrl_a, b=ctrl_b, d=ctrl_d, e=ctrl_e, m=ctrl_m)[a.which]() if a.which != 'c' else ctrl_c(a.episodes)
    res.update(control=a.which, host=socket.gethostname(), cpu=time.process_time() - t0,
               note='AI (Claude) theo ủy quyền; criteria fixed in SPEC_tau.md §5 before the run')
    (DEST / f'{a.which}.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    print(a.which, 'PASS' if res['PASS'] else 'FAIL', f"{res['cpu']:.0f} CPU-s")


if __name__ == '__main__':
    main()
