"""Doan Van Tai — check before displaying contrasts; flags never remove cells."""
from fractions import Fraction as F
import numpy as np

from experiments.A03_card.grading import CONTRASTS, STANDS, refinement, get


def physical_checks(tables, details):
    signs = all(all(v >= 0 for v in s.d + s.dh) if side == 'A' else
                all(v <= 0 for v in s.d + s.dh) for side, s in zip('AB', tables))
    worst = np.longdouble(0)
    passed = True
    for detail in details:
        for a in ('St', 'Sw'):
            excess = max((np.longdouble(x) - np.longdouble(y) for x, y in
                          zip(detail['W0'][a], detail['W1'][a])), default=np.longdouble(0))
            bound = detail['mean_idle_error'] + detail['true_idle_error'][a]
            worst = max(worst, excess)
            passed &= excess <= bound
    return dict(component_signs_pass=bool(signs), jensen_within_bounds=bool(passed),
                jensen_max_nominal_excess=str(worst))


def ledger_checks(r):
    ld = np.longdouble
    L, G, e = r['L'], r['G'], r['e_num']
    def difference_ok(a, b, allowance):
        return abs(ld(a) - ld(b)) <= ld(allowance)
    nonnegative = all(ld(G[g]) >= -ld(e[g]) for g in ('G_M', 'G_SM', 'G_S_M1', 'G_M_S1'))
    oracle = all(ld(L['11']) <= ld(L[k]) + ld(e['L11']) + ld(e['L' + k]) for k in ('00', '01', '10', 'cb0'))
    model_bound = ld(G['G_M_S1']) <= ld(r['E_abs_e_M']) + ld(e['G_M_S1']) + ld(e['E_abs_e_M'])
    bias_bound = ld(G['G_M']) <= abs(ld(r['bias'])) + ld(e['G_M']) + ld(e['bias'])
    ids = (
        difference_ok(G['Gamma'], ld(G['G_M_S1']) - ld(G['G_M']), e['Gamma'] + e['G_M_S1'] + e['G_M']),
        difference_ok(G['Gamma'], ld(G['G_S_M1']) - ld(G['G_S']), e['Gamma'] + e['G_S_M1'] + e['G_S']),
        difference_ok(G['G_S'], ld(G['F']) + ld(G['V']), e['G_S'] + e['F'] + e['V']),
        difference_ok(G['G_S_M1'], min(ld(r['E_pos']), ld(r['E_neg'])), e['G_S_M1'] + e['E_pos'] + e['E_neg']),
        difference_ok(G['G_M'], abs(ld(r['E_delta'])) * (r['nominal_actions']['00'] != r['nominal_actions']['01']), e['G_M'] + e['E_delta']),
    )
    return dict(oracle_within_bounds=bool(oracle), nonnegative_within_bounds=bool(nonnegative),
                model_error_bound_pass=bool(model_bound), bias_bound_pass=bool(bias_bound),
                identities_pass=bool(all(ids)), R11_exact_zero=(ld(r['R']['11']) == 0))


def row(cid, ref, r, physical, cfg):
    checks = {**ledger_checks(r), **physical}
    zero = cid not in cfg['zero_cells'] or all(np.longdouble(r['G'][g]) == 0 for g in CONTRASTS)
    wd = cid not in cfg['wd_cells'] or np.longdouble(r['G']['G_S_M1']) == 0
    hard = all(v for k, v in checks.items() if k != 'jensen_max_nominal_excess') and zero and wd
    cl = float(r['intervals']['C_ref'][0])
    return dict(cell=cid, refinement=ref, status=r['status'], **checks,
                zero_control_pass=bool(zero), wd_control_pass=bool(wd), hard_pass=bool(hard),
                max_e_over_Cref_lower=max(r['e_num'][g] for g in r['G']) / cl if cl > 0 else '',
                unresolved_oracle=r['unresolved_mass']['oracle'], unresolved_M0=r['unresolved_mass']['M0'],
                unresolved_D22=r['unresolved_mass']['D22'], numeric_budget_met=r['numeric_budget_met'])


def pair(coarse, fine):
    state = refinement(coarse, fine)
    C = get(fine, 'C_ref')
    changes = {g: get(fine, g) - get(coarse, g) for g in CONTRASTS}
    maximum = max(max(abs(d.lo), abs(d.hi)) for d in changes.values())
    return dict(pair_verdict=state, pair_flag=state != STANDS,
                max_change_upper_over_Cref_fine=float(maximum / C.lo) if C.lo > 0 else '',
                F_pair_change=float(F(str(fine['G']['F'])) - F(str(coarse['G']['F']))),
                V_pair_change=float(F(str(fine['G']['V'])) - F(str(coarse['G']['V']))))
