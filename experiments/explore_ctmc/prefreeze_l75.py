"""Doan Van Tai — L7.5 zero-fit quantities frozen before the tau card is locked (mentor review 04/11/2026)
[EXPLORATION ONLY; AI (Claude) theo ủy quyền]. No truth: never calls V.

  python -m experiments.explore_ctmc.prefreeze_l75   # -> l75/PRIOR_BIT.csv, l75/L75_4_ELIGIBILITY.csv, l75/M0_GAP_PARTS.json

1. Prior bit (mentor §2). For each SO ∪ OLD regime: F_stat = M0 decision on the stationary posterior at h = inf (one action
   for every state; tau.stationary_posterior_decision), a_LR = 1 if s < 0 (Switch better in the long run) else 0,
   prior_correct = (F_stat == a_LR). Also F_new at h = inf and z_inf at tau = 10 T_int, from the frozen zero fit, and the
   identity check sign(z_inf(10 T_int)) == sign(s (F_stat - F_new)) (an identity, not evidence).
2. L75-4 eligibility (mentor §3b). For each x-slice series (family, tau): x_edge from z_pred1 (first + -> - over x > 0),
   band height = max z_pred1 over 0 < x < x_edge, slope = finite difference of z_pred1 at the two points bracketing the
   edge, eligible iff height >= 0.5 pp and 0.1 / |slope| <= 0.01.
3. M0 gap parts (mentor §2 question, prompt item 8): at h = inf, pi_Stay-average of the M0 gap of path A and of path B
   (ctmc.m0_gap; side A: Switch removes u from A; side B: Switch adds u to B) and their sum, for TN0003, TB0007, TP0079.
"""
from fractions import Fraction as F
import json
import math
from pathlib import Path
import socket

import numpy as np
import pandas as pd

from experiments.explore_ctmc import check_l75 as C, ctmc, tau as T5

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
L75 = OUT / 'l75'


def prior_bit():
    rows = []
    for st in ('sobol', 'old'):
        for c in json.loads((OUT / 'cases_l75' / f'{st}.json').read_text()):
            lamA, lamB, u, kappa = (F(x) for x in c['parameters'][:4])
            gm = T5.tau_grid_map(c, st)
            t10 = next(t for t, m in gm.items() if m == 10.0)
            d = json.loads((OUT / 'm0_l75' / st / f"{c['id']}__t{t10.replace('/', '-')}.json").read_text())
            inf = d['h'][-1]
            F_stat = T5.stationary_posterior_decision(lamA, lamB, u, kappa)
            a_lr = 1.0 if d['s'] < 0 else 0.0
            ident = np.sign(d['z_inf']) == np.sign(d['s'] * (F_stat - inf['F_new']))
            rows.append(dict(stage=st, id=c['id'], x=c['x'], s=d['s'], F_new=inf['F_new'], F_old_10T=inf['F_old'],
                             F_stat=F_stat, a_LR=a_lr, prior_correct=bool(F_stat == a_lr), z_inf_10T=d['z_inf'],
                             sign_identity=bool(ident)))
    return pd.DataFrame(rows)


def eligibility(z):
    xs = z[(z.stage == 'xs') & (z.status == 'COMPLETED') & (z.h != 'inf')].copy()
    gmap = {}
    for c in json.loads((OUT / 'cases_l75' / 'xs.json').read_text()):
        gmap.update({(c['id'], t): m for t, m in T5.tau_grid_map(c, 'xs').items()})
    xs['tau_mult'] = [gmap[(i, t)] for i, t in zip(xs.id, xs.tau)]
    rows = []
    for (fam, tm), g in xs.groupby(['family', 'tau_mult']):
        g = g[g.x > 0].sort_values('x')
        x, y = g.x.values, g.z_pred1.values
        edge = C.x_edge(x, y)
        row = dict(family=fam, tau_mult=tm, x_edge_zf=edge, n_points=len(g))
        if edge is not None:
            i = next(k for k in range(1, len(x)) if y[k - 1] > 0 >= y[k])
            height = float(y[x < edge].max())
            slope = float((y[i] - y[i - 1]) / (x[i] - x[i - 1]))
            row.update(height=height, slope=slope, dx_per_0p1=0.1 / abs(slope),
                       eligible=bool(height >= 0.5 and 0.1 / abs(slope) <= 0.01))
        else:
            row.update(height=None, slope=None, dx_per_0p1=None, eligible=False)
        rows.append(row)
    return pd.DataFrame(rows)


def gap_parts(ids=('TN0003', 'TB0007', 'TP0079')):
    cases = {c['id']: c for c in json.loads((OUT / 'cases_l75' / 'sobol.json').read_text())}
    out = {}
    for rid in ids:
        lamA, lamB, u, kappa = (F(x) for x in cases[rid]['parameters'][:4])
        NA, NB = (ctmc.choose_N(lam + u, kappa) for lam in (lamA, lamB))
        Ast, Bst = ctmc.chain(lamA + u, kappa, NA), ctmc.chain(lamB, kappa, NB)
        Asw, Bsw = ctmc.chain(lamA, kappa, NA), ctmc.chain(lamB + u, kappa, NB)
        gA = float(Ast.pi @ ctmc.m0_gap(lamA, u, kappa, NA, [math.inf], 'A')[0])
        gB = float(Bst.pi @ ctmc.m0_gap(lamB, u, kappa, NB, [math.inf], 'B')[0])
        out[rid] = dict(parameters=[str(v) for v in (lamA, lamB, u, kappa)], x=cases[rid]['x'],
                        gap_A=gA, gap_B=gB, gap_sum=gA + gB, M0_blind_switch=bool(gA + gB < 0),
                        s=(Asw.r + Bsw.r) - (Ast.r + Bst.r), mean_backlog_stay=dict(A=Ast.r, B=Bst.r),
                        note='pi_Stay-average of the M0 drain-cost gap (Switch - Stay) at h = inf; < 0 favours Switch')
    return out


def main():
    z = pd.read_csv(L75 / 'ZEROFIT_tau.csv', dtype={'h': str, 'tau': str})
    pb = prior_bit()
    pb.to_csv(L75 / 'PRIOR_BIT.csv', index=False)
    el = eligibility(z)
    el.to_csv(L75 / 'L75_4_ELIGIBILITY.csv', index=False)
    gp = gap_parts()
    (L75 / 'M0_GAP_PARTS.json').write_text(json.dumps(dict(host=socket.gethostname(), regimes=gp), indent=1) + '\n')
    wrong = pb[~pb.prior_correct]
    print('host', socket.gethostname())
    print('prior correct / wrong:', int(pb.prior_correct.sum()), '/', int((~pb.prior_correct).sum()),
          '| sign identity', int(pb.sign_identity.sum()), '/', len(pb))
    print('prior wrong: all s > 0', bool((wrong.s > 0).all()), 'all F_stat = 1', bool((wrong.F_stat == 1).all()),
          'x range', wrong.x.min(), wrong.x.max())
    print('eligible L75-4 series:', int(el.eligible.sum()))
    print(el.to_string())
    print(json.dumps(gp, indent=1))


if __name__ == '__main__':
    main()
