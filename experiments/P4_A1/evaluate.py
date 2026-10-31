"""One frozen-engine evaluation per (case, level), plus margin/Stay outputs with A1 sanity.

The physical numbers come from the unchanged native engine (R3R_14 engine.evaluate_level). The
side() arrays are captured from that SAME call, so margin cells and the engine's own cells share
nodes, weights and summation order. Failed checks are RECORDED (row['a1_bug_reasons']), never
raised: the frozen row is always kept. Formulas for loss/error are byte-for-byte those of L4.4.
"""
from fractions import Fraction as F

from experiments.P4_04_baseline.margin import pair_loss_margin, significant_bits, LD, EPS, number
from .checks import same_route_violations, margin_violations, cross_route_report, algebra_violations


def margin_cells(A, B, base, ebase, rho):
    r = number(F(rho)); theta = r * base
    etheta = r * ebase + (64 * EPS * (abs(theta) + 1) if r else LD(0))
    cells = {}
    for key, kind in (('00', 'old'), ('10', 'current')):
        gap, err, amb = pair_loss_margin(A[kind], B[kind], theta=theta, theta_error=etheta)
        cells[key] = (base + gap, ebase + err + 64 * EPS * (abs(base) + abs(gap) + 1), amb, gap, err)
    return theta, etheta, cells


def add_baselines_a1(row, sides, h, rhos):
    from experiments.R3R_08_population_numerics.population import pair_loss
    bugs = []
    if len(sides) != 2:
        row.update(a1_bug_reasons=['side_capture_failed'], baseline=[]); return row
    A, B = sides
    base = number(h) * (A['mean'] + B['mean'])
    ebase = abs(number(h)) * (A['mean_error'] + B['mean_error']) + 128 * EPS * (abs(base) + 1)
    if base < 0:
        bugs.append('negative_stay_scale')
    # (1) theta = 0 must reproduce the engine bit-for-bit (strongest margin.py bug detector) -- FIRST.
    _, _, zero = margin_cells(A, B, base, ebase, '0')
    for key, kind in (('00', 'old'), ('10', 'current')):
        loss, error, amb, gap, err = zero[key]
        original = pair_loss(A[kind], B[kind], model='mean')
        if significant_bits(gap) != significant_bits(original[0]) or significant_bits(err) != significant_bits(original[1]):
            bugs.append(f'theta0_pair_loss_bits:{key}')
        if amb != original[2] or amb != row['uncertain_action_mass'][key]:
            bugs.append(f'theta0_ambiguity:{key}')
        if significant_bits(loss) != significant_bits(LD(row['losses'][key])):
            bugs.append(f'theta0_cell_bits:{key}')
        if significant_bits(error) != significant_bits(LD(row['cost_error'][key])):
            bugs.append(f'theta0_error_bits:{key}')
    # (2) engine's own cells: same-route bounds are exact on the grid (cross-route only reported).
    bugs += same_route_violations(row['losses'], row['cost_error'], label='engine')
    bugs += algebra_violations(row)
    # (3) every rho: margin cell vs the true-model cell of the same route.
    outputs = []
    for rho in rhos:
        theta, etheta, cells = margin_cells(A, B, base, ebase, rho)
        l00, e00, a00, _, _ = cells['00']; l10, e10, a10, _, _ = cells['10']
        gm = LD(row['G_M']); gm_error = LD(row['contrast_error']['G_M'])
        recovery = (LD(row['losses']['00']) - l00) / gm if gm > 0 else None
        b = dict(rho=rho, theta=str(theta), theta_error=str(etheta), L00=str(l00), L10=str(l10),
                 error00=str(e00), error10=str(e10), GS_theta=str(l00 - l10), GS_theta_error=str(e00 + e10),
                 deltaL00=str(l00 - LD(row['losses']['00'])), deltaL00_error=str(e00 + LD(row['cost_error']['00'])),
                 deltaL10=str(l10 - LD(row['losses']['10'])), deltaL10_error=str(e10 + LD(row['cost_error']['10'])),
                 R_M=None if recovery is None else str(recovery), R_M_denominator_certified=bool(gm > gm_error),
                 R_M_undefined=bool(gm <= 0), uncertain_action_mass={'00': a00, '10': a10})
        bugs += margin_violations(row, b)
        outputs.append(b)
    # (4) very large margin == Stay on the same arrays; (5) exact zero action.
    for kind in ('old', 'current'):
        theta = max(abs(A[kind]['h'])) + max(abs(B[kind]['h'])) + LD(1)
        gap, _, _ = pair_loss_margin(A[kind], B[kind], theta=theta)
        if not (gap == 0 and base + gap == base):
            bugs.append(f'large_margin_not_stay:{kind}')
    if row.get('zero_action_certificate'):
        if not all(LD(v) == base for v in row['losses'].values()):
            bugs.append('u0_cells_differ')
        if not all(LD(b[k]) == base for b in outputs for k in ('L00', 'L10')):
            bugs.append('u0_baseline_differs')
    row.update(Stay=str(base), Stay_error=str(ebase), baseline=outputs, a1_bug_reasons=bugs,
               cross_route_report=cross_route_report(row), raw_flags_report_only=dict(
                   arithmetic_pass=row.get('arithmetic_pass'), validity_errors=row.get('validity_errors')))
    return row


def evaluate_level(case, level, cache, rhos):
    from experiments.R3R_14_lean_close import engine
    from experiments.R3R_08_population_numerics import population
    engine.configure()
    sides = []; original = population.side

    def capture(*args, **kwargs):
        result = original(*args, **kwargs); sides.append(result); return result
    begin = engine.cpu_seconds()
    population.side = capture
    try:
        row = engine.evaluate_level(case['id'], case['parameters'], *level, cache)
    finally:
        population.side = original
    try:
        row = add_baselines_a1(row, sides, F(case['parameters'][4]), rhos)
    except Exception as exc:                      # keep the frozen row; an exception is a BUG
        row.update(a1_bug_reasons=[f'baseline_exception:{type(exc).__name__}: {exc}'], baseline=[])
    row['native_only_cpu_seconds'] = row['call_cpu_seconds']
    row['call_cpu_seconds'] = engine.cpu_seconds() - begin
    return row
