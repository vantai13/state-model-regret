"""Pure A1 checks (no engine import). Two failure kinds are never mixed:

BUG        An inequality that is EXACT on one discretized grid failed: theta=0 bit identity,
           same-route decision bounds (L00>=L01, L10>=L11, margin cells too), large-theta == Stay,
           zero action. Arithmetic error is the right budget here. -> stop the schedule.
NOT_READY  A numerical-readiness rule of the frozen confirmation failed at one point: contract R1 on
           both axes, arithmetic width <= 1/4000, lean consistency within TOL_NUM (DL-095), or the
           same refinement rule on baseline outputs. -> keep the point, it enters downstream as
           UNRESOLVED; stop only when the per-support count can no longer meet the prereg cap.

Cross-route differences (L00-L11, L01-L11) compare two different quadratures (old snapshot grid +
posterior vs current-state grid); their mismatch is not inside the row's arithmetic error
(row field `quadrature_error`). They are reported, and judged only by the frozen lean rule.
"""
from fractions import Fraction as F

from experiments.R3R_05_contract.rules import TOL_NUM, compare_levels
from experiments.R3R_14_lean_close.checks import level_ready, ARITH_MAX
from experiments.P4_03_map_audit.common import point_class, pct, METRICS

SAME_ROUTE = (('00', '01'), ('10', '11'))     # (higher, lower) computed on ONE quadrature
CROSS_ROUTE = (('00', '11'), ('01', '11'))    # two quadratures: report only
BASELINE_FIELDS = dict(L00='error00', L10='error10', GS_theta='GS_theta_error', deltaL10='deltaL10_error')
PILOT_TOL_PP = F(1, 4)


def algebra_violations(row):
    """Keep S11 bookkeeping checks separate from cross-quadrature inequalities."""
    c = F(row['Cref'])
    if c <= 0:
        return ['nonpositive_Cref']
    g = {name: F(row[name]) / c for name in METRICS}
    tol = F(1, 10**11)  # original 1e-9 percentage-point algebra tolerance
    out = []
    if abs(g['Gamma'] - (g['G_S_M1'] - g['G_S'])) > tol:
        out.append('S11_state_identity')
    if abs(g['Gamma'] - (g['G_M_S1'] - g['G_M'])) > tol:
        out.append('S11_model_identity')
    return out


def same_route_violations(losses, errors, label='cell'):
    """Decision-rule bound on one grid: any rule >= the true-model rule on the same nodes."""
    out = []
    for hi, lo in SAME_ROUTE:
        if F(losses[hi]) + F(errors[hi]) < F(losses[lo]) - F(errors[lo]):
            out.append(f'{label}:same_route:{hi}<{lo}')
    return out


def margin_violations(row, baseline):
    """Margin cells vs the true-model cell of the SAME route: L00^theta>=L01, L10^theta>=L11."""
    L, E = row['losses'], row['cost_error']
    out = []
    for cell, err, ref in (('L00', 'error00', '01'), ('L10', 'error10', '11')):
        if F(baseline[cell]) + F(baseline[err]) < F(L[ref]) - F(E[ref]):
            out.append(f'rho={baseline["rho"]}:same_route:{cell}<{ref}')
    return out


def cross_route_report(row):
    c = F(row['Cref'])
    return {f'{hi}-{lo}': str((F(row['losses'][hi]) - F(row['losses'][lo])) / c) for hi, lo in CROSS_ROUTE}


def row_readiness(levels, main):
    """Frozen confirmation acceptance (frame_v2 lean rule): R1 both axes + width + lean consistency."""
    ready, reasons = level_ready(levels, tuple(main))
    if ready is None:
        return ['missing_levels'] + reasons
    return list(reasons)


def neighbours(main):
    K, ref = main
    return [(K // 2, ref), (K, ref // 2)]


def baseline_readiness(levels, main, rhos):
    """Same refinement/width rule as L4.4 compare_bundle, applied to margin outputs at every rho."""
    main = tuple(main); reasons = []; refinement = []
    fine_row = levels[main]; cf = F(fine_row['Cref'])
    for lv in [main, *neighbours(main)]:
        row = levels[lv]
        for b in row['baseline']:
            if max(F(b[e]) / F(row['Cref']) for e in BASELINE_FIELDS.values()) > ARITH_MAX:
                reasons.append(f'baseline_arithmetic:{lv}:{b["rho"]}')
    for i, rho in enumerate(rhos):
        fine = fine_row['baseline'][i]; ds = {}
        if fine['rho'] != rho:
            raise ValueError('rho grid order changed')
        for field in BASELINE_FIELDS:
            gf = F(fine[field]); diffs = []
            for lv in neighbours(main):
                coarse = levels[lv]; cc = F(coarse['Cref']); gc = F(coarse['baseline'][i][field])
                diffs.append(max(abs(gf - gc) / cf, abs(gf / cf - gc / cc)))
            ds[field] = float(max(diffs))
            if max(diffs) > TOL_NUM:
                reasons.append(f'baseline_R1:{rho}:{field}')
        refinement.append(dict(rho=rho, normalized_difference=ds))
    return reasons, refinement


def d_normalized(levels, main):
    """R6 distance per metric (ratio of Cref): max refinement delta and arithmetic width (as L4.3/score.py)."""
    main = tuple(main); fine = levels[main]
    r1 = [compare_levels(fine, levels[lv]) for lv in neighbours(main)]
    out = {}
    for m in METRICS:
        deltas = [c['deltas'][m] for c in r1 if c['deltas'] is not None]
        out[m] = max(deltas + [F(fine['normalized_error'][m])])
    return out, r1


def audit_compare(alias, levels, main):
    """Port of L4.3 compare() with the ONE intended change: no raw-validity / 1e-9 cross-route gate.
    Readiness is judged elsewhere by row_readiness (lean). Labels, d and R6 logic are unchanged."""
    main = tuple(main); row = levels[main]
    d_ratio, r1 = d_normalized(levels, main)
    z = {m: pct(row, m) for m in METRICS}
    d = {m: 100 * d_ratio[m] for m in METRICS}
    shift = {m: z[m] - F(alias['pilot_pctC'][m]) for m in METRICS}
    keys = ('G_S', 'G_M', 'G_SM', 'Gamma')
    native_class = point_class([z[m] for m in keys])
    from itertools import product
    candidates = {point_class(v) for v in product(*[(z[m] - d[m], z[m] + d[m]) for m in keys])}
    boundaries = ((abs(z['G_S'] + 1), d['G_S']), (abs(z['G_S'] - 1), d['G_S']),
                  (abs(z['G_M'] - 1), d['G_M']), (abs(z['G_SM'] - 1), d['G_SM']),
                  (abs(z['Gamma'] - z['G_S']), d['Gamma'] + d['G_S']),
                  (abs(z['Gamma'] - z['G_M']), d['Gamma'] + d['G_M']))
    relevant = {'C': (0,), 'A': (0, 1, 2), 'AB': (0, 1, 2), 'B': (0, 1, 2), 'J': tuple(range(6)), 'D': tuple(range(6))}
    if native_class == 'D' and z['G_SM'] < 1:
        relevant['D'] = (0, 1, 2, 3)
    ambiguous = len(candidates) != 1 or any(boundaries[i][0] <= boundaries[i][1] for i in relevant[native_class])
    flags = ['PILOT_NATIVE:' + m for m in ('G_S', 'G_M', 'Gamma', 'G_S_M1', 'G_M_S1') if abs(shift[m]) > PILOT_TOL_PP]
    return dict(id=alias['id'], pilot_class=alias['pilot_class'], native_class=native_class,
                native_class_R6='UNRESOLVED' if ambiguous else native_class,
                class_flipped=native_class != alias['pilot_class'],
                z_pctC={m: float(v) for m, v in z.items()}, d_pp={m: float(v) for m, v in d.items()},
                shift_pp={m: float(v) for m, v in shift.items()}, pilot_flags=flags,
                r1=[dict(ready=bool(c['ready']), cref_delta=float(c['cref_delta'])) for c in r1])


def manifest_row(case, levels, main, readiness_reasons):
    """Row format required by experiments/P4_05_candidates/screen.native_label (DISCOVERY_NATIVE)."""
    main = tuple(main); row = levels[main]
    d_ratio, r1 = d_normalized(levels, main)
    arithmetic = not any(r.startswith(('arithmetic_width', 'negative_', 'model_gain', 'state_gain', 'interaction'))
                         for r in readiness_reasons)
    return dict(id=case['id'], key=list(case['key']), Cref=row['Cref'], G_S=row['G_S'], Gamma=row['Gamma'],
                G_M=row['G_M'], d_normalized={m: str(v) for m, v in d_ratio.items()},
                r1_ready=all(c['ready'] for c in r1) and not readiness_reasons,
                arithmetic_ready=arithmetic,
                certified_exact=False, CF_computed=False, source_kind='DISCOVERY_NATIVE')


def classify(bug_reasons, readiness_reasons):
    if bug_reasons:
        return 'BUG'
    return 'NOT_READY' if readiness_reasons else 'PASS'


def stop_decision(results, planned_by_support, caps):
    """BUG/execution -> stop now. NOT_READY or pilot flags -> stop only when the count already
    exceeds cap * planned N of that support (the cap can no longer be met). Planned N, not completed
    N, is the denominator so one early NOT_READY cannot stop a run by itself."""
    reasons = []
    for r in results:
        if r['status'] in ('BUG', 'HOLD_EXECUTION', 'HOLD_RESOURCE_TIMEOUT', 'HOLD_GUARD'):
            reasons.append(f'{r["native_id"]}:{r["status"]}')
    for support, n in planned_by_support.items():
        mine = [r for r in results if support in r.get('supports', [])]
        nr = sum(r['status'] == 'NOT_READY' for r in mine)
        if nr > F(caps['max_not_ready_fraction']) * n:
            reasons.append(f'{support}:NOT_READY {nr}/{n} > {caps["max_not_ready_fraction"]}')
        flagged = sum(bool(r.get('pilot_flags')) for r in mine)
        if 'max_pilot_flag_fraction' in caps and flagged > F(caps['max_pilot_flag_fraction']) * n:
            reasons.append(f'{support}:PILOT_NATIVE {flagged}/{n} > {caps["max_pilot_flag_fraction"]}')
    return reasons
