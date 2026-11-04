"""Doan Van Tai — Stage F design: a one-time switching cost c_sw > 0 in ctmc-v1 (the CTMC analogue of the Phase 6
D(ii) arm) [EXPLORATION ONLY; AI (Claude) theo ủy quyền].

The mean rollout is horizon-blind, so c changes M0's decisions on an O(1) scale at every horizon, while the truth's
stake h*s + c is dominated by h*s. The zero-fit limit is therefore h-invariant:
    z_inf(c) = 100 * s * (F_old(c) - F_new(c)) / r_min,   F = M0 Switch share at h = inf with the cost c included.
This module only uses M0 and stationary quantities (no V, no true gap), so it may run before the Stage F
predictions are locked.

  python -m experiments.explore_ctmc.stage_f design    # -> results/explore_ctmc/cases/csw.json + stage_f_design.json
"""
from fractions import Fraction as F
import json
import math
from pathlib import Path
import sys

import numpy as np

from experiments.explore_ctmc import ctmc
from experiments.explore_ctmc.design import case, rational

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/explore_ctmc'
BASES = [(F(7), F(71, 10), F(1), F(1, 5)), (F(7), F(71, 10), F(1), F(1)), (F(13, 2), F(33, 5), F(2), F(1, 5)),
         (F(13, 2), F(33, 5), F(2), F(1)), (F(13, 2), F(67, 10), F(2), F(1, 5)), (F(13, 2), F(33, 5), F(2), F(1, 2))]
C_GRID = [F(k, 8) for k in range(1, 49)]          # 1/8 .. 6 packet-seconds


def m0_inf(lamA, lamB, u, kappa, c_values):
    """M0 Switch shares on old/new state at h = inf for each c, and s, r_min, T_int; no truth."""
    NA, NB = (ctmc.choose_N(lam + u, kappa) for lam in (lamA, lamB))
    Ast, Asw = ctmc.chain(lamA + u, kappa, NA), ctmc.chain(lamA, kappa, NA)
    Bst, Bsw = ctmc.chain(lamB, kappa, NB), ctmc.chain(lamB + u, kappa, NB)
    dhA = ctmc.m0_gap(lamA, u, kappa, NA, [math.inf], 'A')[0]
    dhB = ctmc.m0_gap(lamB, u, kappa, NB, [math.inf], 'B')[0]
    oA, oB = ctmc.posterior_mean(Ast, dhA), ctmc.posterior_mean(Bst, dhB)
    wA, wB = Ast.pi, Bst.pi
    pA, pB = Ast.pi.reshape(-1, 2).sum(axis=1), Bst.pi.reshape(-1, 2).sum(axis=1)
    s = (Asw.r + Bsw.r) - (Ast.r + Bst.r)
    r_min = min(Ast.r + Bst.r, Asw.r + Bsw.r)
    one = lambda n: np.ones(n)
    rows = []
    for c in c_values:
        Fn = ctmc.pair_sum(wA, dhA, one(wA.size), wB, dhB, one(wB.size), float(c))[0]
        Fo = ctmc.pair_sum(pA, oA, one(pA.size), pB, oB, one(pB.size), float(c))[0]
        rows.append(dict(c=str(c), F_new=Fn, F_old=Fo, z_inf=100 * s * (Fo - Fn) / r_min))
    T = max(ch.T_int for ch in (Ast, Asw, Bst, Bsw))
    return dict(s=s, r_min=r_min, T_int_max=T, rows=rows)


def design():
    cases, record = [], []
    for lamA, lamB, u, kappa in BASES:
        info = m0_inf(lamA, lamB, u, kappa, [F(0)] + C_GRID)
        base_z = info['rows'][0]['z_inf']
        best = min(info['rows'][1:], key=lambda r: (r['z_inf'], F(r['c'])))     # most negative z_inf(c); tie -> smaller c
        c = F(best['c'])
        T = info['T_int_max']
        hs = [rational(m * T) for m in (F(1, 3), 1, 3, 10, 30)] + [80 * kappa, 160 * kappa]
        tag = f"F_lA{lamA}_lB{lamB}_u{u}_k{kappa}".replace('/', '-')
        for cc, suffix in ((c, 'c'), (F(0), 'c0')):
            cs = case(f'{tag}_{suffix}', lamA, lamB, u, kappa, hs, dict(x=str((lamB - lamA) / u), c=str(cc)), T)
            cs['parameters'][4] = str(cc)
            cs['csw'] = True
            cases.append(cs)
        record.append(dict(base=[str(x) for x in (lamA, lamB, u, kappa)], x=float((lamB - lamA) / u), s=info['s'],
                           r_min=info['r_min'], T_int_max=T, z_inf_c0=base_z, c_star=str(c), z_inf_c_star=best['z_inf'],
                           F_old=best['F_old'], F_new=best['F_new'], scan=info['rows']))
    (OUT / 'cases' / 'csw.json').write_text(json.dumps(cases, indent=0) + '\n')
    (OUT / 'stage_f_design.json').write_text(json.dumps(record, indent=1) + '\n')
    for r in record:
        print(r['base'], 'x %.2f' % r['x'], 'z_inf(0) %.3f' % r['z_inf_c0'], 'c* %s' % r['c_star'],
              'z_inf(c*) %.3f' % r['z_inf_c_star'], 'Tint %.1f' % r['T_int_max'])
    print(len(cases), 'cases')


if __name__ == '__main__' and sys.argv[1:] == ['design']:
    design()
