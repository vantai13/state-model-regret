# Exploration (post-hoc on the seen EV-A2 panel): decoupled-epoch approximation with exact epoch cost.
# J_m ~ sum_b P_m(b) E_{x~pi_b}[ V_{a_m(x)}(Delta, x) ] / Delta, P_m(b) from the two-state action chain.
import csv, json, sys
from fractions import Fraction as F
import numpy as np
from experiments.explore_ctmc import ctmc as C
from experiments.ext_validity import closed_loop as CL
cases = json.load(open('results/ext_validity/ev_a2/cases.json'))
T = {(r['id'], r['which']): r for r in csv.DictReader(open('results/ext_validity/ev_a2/truth.csv'))}
def approx(case, D, hp):
    chains = CL._chains(case, hp)
    ar = CL._m0(case, hp, chains)
    (Ast, Bst), (Asw, Bsw) = chains
    V = [[ch.V([D])[0] for ch in pair] for pair in chains]     # V[action][path]
    out = {}
    for name, stale in (('new', False), ('old', True)):
        q, cost = [], []
        for b, (cA, cB) in enumerate(chains):
            if stale:
                pA, pB = cA.pi.reshape(-1, 2).sum(1), cB.pi.reshape(-1, 2).sum(1)
                # value of each action given y under chain b: E_b[V_a(x)|y]
                vSt = (C.posterior_mean(cA, V[0][0]), C.posterior_mean(cB, V[0][1]))
                vSw = (C.posterior_mean(cA, V[1][0]), C.posterior_mean(cB, V[1][1]))
                m, val, _ = C.pair_sum(pA, ar['dhAo'][0], vSw[0] - vSt[0], pB, ar['dhBo'][0], vSw[1] - vSt[1], 0)
                base = float(pA @ vSt[0] + pB @ vSt[1])
            else:
                m, val, _ = C.pair_sum(cA.pi, ar['dhA'][0], V[1][0] - V[0][0], cB.pi, ar['dhB'][0], V[1][1] - V[0][1], 0)
                base = float(cA.pi @ V[0][0] + cB.pi @ V[0][1])
            q.append(m); cost.append(base + val)
        P1 = q[0] / (1 - q[1] + q[0]); Pb = [1 - P1, P1]
        out[name] = sum(Pb[b] * cost[b] for b in (0, 1)) / float(D)
    return out['old'] - out['new']
hit_old = hit_new = 0
for c in cases:
    signs = []
    for which in ('lo', 'hi'):
        D = F(c[f'Delta_{which}']); g = approx(c, D, F(c['h_p'])); t = float(T[(c['id'], which)]['G_S_CL_abs'])
        signs.append(((g > 0) == (t > 0), g, t))
    ok = all(s[0] for s in signs)
    hit_new += ok
    print(c['id'], '%.2f' % c['Delta_star_over_T'], 'lo approx %.3f truth %.3f | hi approx %.3f truth %.3f' % (signs[0][1], signs[0][2], signs[1][1], signs[1][2]), 'OK' if ok else 'x')
print('decoupled-exact-epoch both-sign agreement:', hit_new, '/', len(cases))
