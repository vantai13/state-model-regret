"""Doan Van Tai — run the ctmc-v1 controls of SPEC.md and record them [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

  python -m experiments.explore_ctmc.controls            # V1 V2 V3 V4 V8 V9 V10 V11 -> results/explore_ctmc/controls/
  python -m experiments.explore_ctmc.controls --v7 A B   # compare two hosts' v7 files bit for bit
  python -m experiments.explore_ctmc.controls --v5 STAGE ID [ID ...]   # N -> 2N at heavy corners (Stage D)

V3 regimes are excluded from every scored set (their IDs are written into controls/v3_ids.json). R1 is also the
light timing probe whose outputs were printed before the predictions were written (exposure, see SUMMARY.md).
"""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import socket
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from experiments.explore_ctmc import ctmc, mc

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc/controls'
V3_REGIMES = {'V3_R1': ('7', '15/2', '3/2', '1/2', '4'), 'V3_R2': ('15/2', '13/2', '1', '1/5', '3'),
              'V3_R3': ('13/2', '7', '1', '1', '6')}
EXPOSED_TIMING = {'T1': ('7', '15/2', '3/2', '1/2', ['4']), 'T2': ('27/4', '13/2', '3', '20', ['32']),
                  'T3': ('7', '13/2', '5/2', '2', ['80', '320', '2000'])}


def v1():
    out = ctmc.evaluate(F(7), F(15, 2), F(0), F(1, 2), [F(3), F(40)], control=True)
    ok = all(r['L00'] == r['L01'] == r['L10'] == r['L11'] and
             all(r[k] == 0.0 for k in ('G_S', 'G_M', 'G_SM', 'Gamma', 'S', 'M')) for r in out['h'])
    return dict(PASS=ok, rows=[{k: r[k] for k in ('h', 'L00', 'L11', 'G_S', 'S', 'M')} for r in out['h']])


def v2():
    res = []
    for load, kappa, N in ((F(8), F(1, 2), 300), (F(19, 2), F(2), 1500)):
        ch = ctmc.Chain(load, kappa, N, a=0)
        rho = float(load) / ctmc.MU
        geo = (1 - rho) * rho ** np.arange(N + 1) / (1 - rho ** (N + 1))
        err = float(np.abs(ch.pi.reshape(-1, 2).sum(axis=1) - geo).max())
        mean_err = abs(ch.r - float((geo * np.arange(N + 1)).sum()))
        res.append(dict(load=str(load), kappa=str(kappa), N=N, max_abs_err=err, mean_err=mean_err,
                        PASS=err <= 1e-12 and mean_err <= 1e-9))
    return dict(PASS=all(r['PASS'] for r in res), cases=res)


def v4():
    res = []
    for load, kappa in ((F(17, 2), F(1, 2)), (F(19, 2), F(2)), (F(7), F(1, 50))):
        ch = ctmc.Chain(load, kappa, ctmc.choose_N(load, kappa))
        for h in (0.5, 5.0, 20 * ch.T_int):
            a, b = ch.V([h])[0], ch.V_aug(h)
            rel = float(np.abs(a - b).max() / np.abs(b).max())
            res.append(dict(load=str(load), kappa=str(kappa), N=ch.N, h=h, rel=rel, PASS=rel <= 1e-8))
    return dict(PASS=all(r['PASS'] for r in res), cases=res)


def v9():
    res = []
    for load, kappa, n, sigma in [(F(17, 2), F(1, 2), 0, 1), (F(17, 2), F(1, 2), 7, 1), (F(7), F(2), 3, -1),
                                  (F(31, 4), F(1, 50), 12, 1), (F(9), F(5), 0, 1), (F(39, 4), F(20), 40, 1)]:
        for h in (0.3, 4.0, 60.0):
            got = float(ctmc.m0_vhat(load, kappa, 60, [h])[0][2 * n + (sigma > 0)])

            def rhs(t, y):
                rate = float(load) + sigma * ctmc.A * np.exp(-2 * t / float(kappa)) - ctmc.MU
                return [rate if y[0] > 0 or rate > 0 else 0.0, max(y[0], 0.0)]
            sol = solve_ivp(rhs, (0, h), [n, 0.0], rtol=1e-11, atol=1e-12, max_step=0.005)
            want = float(sol.y[1, -1])
            rel = abs(got - want) / max(abs(want), 1e-9)
            res.append(dict(load=str(load), kappa=str(kappa), n=n, sigma=sigma, h=h, got=got, ode=want, rel=rel,
                            PASS=rel <= 1e-7 or abs(got - want) <= 1e-9))
    return dict(PASS=all(r['PASS'] for r in res), cases=res)


def v10():
    res = []
    for load, kappa, N in ((F(15, 2), F(1, 2), 60), (F(17, 2), F(1, 5), 120)):
        ch = ctmc.Chain(load, kappa, N)
        vec = np.random.default_rng(1).normal(size=(ch.n, 3))
        got = ctmc.posterior_mean(ch, vec)
        P = expm(ch.Q.toarray())
        pi = ch.pi.reshape(-1, 2)
        want = (pi[:, :, None] * (P @ vec).reshape(-1, 2, 3)).sum(axis=1) / pi.sum(axis=1)[:, None]
        rel = float(np.abs(got - want).max() / np.abs(want).max())
        res.append(dict(load=str(load), kappa=str(kappa), N=N, rel=rel, PASS=rel <= 1e-10))
    return dict(PASS=all(r['PASS'] for r in res), cases=res)


def v11():
    res = []
    for lamA, lamB, u, kappa in (('7', '15/2', '1', '1/2'), ('15/2', '7', '1', '1/2'), ('6', '33/4', '3/2', '5'),
                                 ('9', '27/4', '3/4', '1/50')):
        out = ctmc.evaluate(F(lamA), F(lamB), F(u), F(kappa), [F(1)], disagree=False)
        res.append(dict(params=[lamA, lamB, u, kappa], s=out['s'], PASS=(out['s'] < 0) == (F(lamB) < F(lamA))))
    return dict(PASS=all(r['PASS'] for r in res), cases=res, note='V11 also runs on every scanned row')


def v8():
    res = []
    for state in ((0, 0), (6, 1), (20, 1)):
        mean, se, exact = mc.gillespie_V(F(15, 2), F(1, 2), 200, state, 3.0, 100000, seed=11)
        res.append(dict(state=state, mc=mean, se=se, exact=exact, z=(mean - exact) / se, PASS=abs(mean - exact) <= 3.5 * se))
    return dict(PASS=all(r['PASS'] for r in res), cases=res)


def v3(episodes):
    res = {}
    for k, (lamA, lamB, u, kappa, h) in V3_REGIMES.items():
        r = mc.end_to_end(F(lamA), F(lamB), F(u), F(kappa), F(h), episodes, seed=20261103 + len(res))
        exact = r.pop('exact')
        res[k] = dict(r, exact_row=exact['h'][0], exact_asymptotic=exact['asymptotic'])
    return dict(PASS=all(r['PASS'] for r in res.values()), regimes=res)


def v5(stage, ids):
    """N -> 2N on the heaviest scored cases: every normalized contrast and regret changes by <= 0.01 pp."""
    cases = {c['id']: c for c in json.loads((ROOT / 'results/explore_ctmc/cases' / f'{stage}.json').read_text())}
    res = []
    for cid in ids:
        c = cases[cid]
        args = [F(x) for x in c['parameters'][:4]]
        one = ctmc.evaluate(*args, c['hs'], disagree=False)
        two = ctmc.evaluate(*args, c['hs'], disagree=False, N_scale=2)
        worst = 0.0
        for r1, r2 in zip(one['h'], two['h']):
            keys = ['G_S', 'G_M', 'G_SM', 'Gamma', 'S', 'M', 'G_S_hybrid']
            worst = max([worst] + [abs(r1[k] - r2[k]) for k in keys] + [abs(r1['regret'][t] - r2['regret'][t]) for t in r1['regret']])
        res.append(dict(stage=stage, id=cid, N=one['N'], N2=two['N'], max_change_pp=worst, PASS=worst <= 0.01))
    return dict(PASS=all(r['PASS'] for r in res), cases=res)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--episodes', type=int, default=100000)
    p.add_argument('--v7', nargs=2)
    p.add_argument('--v5', nargs='+')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.v5:
        r = v5(a.v5[0], a.v5[1:])
        (OUT / f"v5_{a.v5[0]}_{'_'.join(a.v5[1:])}_{socket.gethostname()}.json").write_text(json.dumps(r, indent=1, default=float) + '\n')
        print('V5', 'PASS' if r['PASS'] else 'FAIL', [(c['id'], c['max_change_pp']) for c in r['cases']])
        return
    if a.v7:
        x, y = (json.loads(Path(f).read_text()) for f in a.v7)
        same = json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True)
        print('V7', 'PASS bit-identical' if same else 'FAIL', a.v7)
        return
    host = socket.gethostname()
    report, t0 = {}, time.process_time()
    for name, fn in (('V1', v1), ('V2', v2), ('V4', v4), ('V8', v8), ('V9', v9), ('V10', v10), ('V11', v11),
                     ('V3', lambda: v3(a.episodes))):
        t = time.process_time()
        report[name] = fn()
        report[name]['cpu_seconds'] = time.process_time() - t
        print(name, 'PASS' if report[name]['PASS'] else 'FAIL', f"{report[name]['cpu_seconds']:.1f}s", flush=True)
    report['all_MUST_PASS'] = all(report[k]['PASS'] for k in ('V1', 'V2', 'V3', 'V4'))
    report['cpu_seconds'] = time.process_time() - t0
    report['host'] = host
    (OUT / f'controls_{host}.json').write_text(json.dumps(report, indent=1, default=float) + '\n')
    v7 = {k: dict(exact=v['exact_row'], checks=v['checks']) for k, v in report['V3']['regimes'].items()}
    (OUT / f'v7_{host}.json').write_text(json.dumps(v7, sort_keys=True, default=float) + '\n')
    (OUT / 'v3_ids.json').write_text(json.dumps(dict(V3=V3_REGIMES, exposed_timing_probes=EXPOSED_TIMING), indent=1) + '\n')
    print('all MUST', report['all_MUST_PASS'], f"cpu {report['cpu_seconds']:.0f}s")


if __name__ == '__main__':
    main()
