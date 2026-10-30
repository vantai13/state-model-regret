"""Doan Van Tai — lean-closure decision rules as pure functions (DL-095). AI (Claude) theo ủy quyền.

R1 is the locked contract rule (experiments/R3R_05_contract/rules.compare_levels), unchanged. The only
change against the native05 selection rule is the consistency ("validity") check: identity/bound
violations are judged against the contract numerical tolerance TOL_NUM = 1/400 of Cref instead of the
interval arithmetic error, because R1 already accepts refinement differences up to that size. The
arithmetic-width check (max normalized arithmetic error <= 1/4000) is kept exactly as in native05.
"""
from fractions import Fraction as F

from experiments.R3R_05_contract.rules import CONTRASTS, EPS_R, TOL_NUM, compare_levels

ARITH_MAX = F(1, 4000)


def normalized(row, name):
    return F(row[name]) / F(row['Cref'])


def consistency(row):
    """Tolerance-based identity checks on one evaluated row; returns a list of violations."""
    C = F(row['Cref'])
    out = []
    if C <= 0:
        return ['nonpositive_Cref']
    if row.get('zero_action_certificate'):
        return [] if all(F(row[k]) == 0 for k in CONTRASTS) else ['zero_control_not_exact']
    for key in ('G_M', 'G_SM', 'G_S_M1', 'G_M_S1'):
        if F(row[key]) / C < -TOL_NUM:
            out.append('negative_nonnegative_contrast:' + key)
    if abs(F(row['GM_identity_gap'])) / C > TOL_NUM:
        out.append('model_gain_flip_identity')
    S = F(row['Sbar'])
    if (abs(F(row['G_S'])) - S) / C > TOL_NUM:
        out.append('state_gain_exceeds_stakes')
    if (abs(F(row['Gamma'])) - S) / C > TOL_NUM:
        out.append('interaction_exceeds_stakes')
    return out


def arithmetic_ok(row):
    return max(F(v) for v in row['normalized_error'].values()) <= ARITH_MAX


def level_ready(levels, main):
    """Contract R1/R2 at main=(K, ref): both coarse-axis neighbours, plus arithmetic and consistency on
    all three rows. levels maps (K, ref) -> row. Returns (ready, reasons)."""
    K, ref = main
    needed = [main, (K // 2, ref), (K, ref // 2)]
    missing = [lv for lv in needed if lv not in levels]
    if missing:
        return None, [f'missing_level:{lv}' for lv in missing]
    reasons = []
    for neighbour, axis in ((needed[1], 'K'), (needed[2], 'dt')):
        cmp = compare_levels(levels[main], levels[neighbour])
        if not cmp['ready']:
            reasons.append(f'R1_{axis}:cref={float(cmp["cref_delta"]):.5f},max={float(max(cmp["deltas"].values())):.5f},flips={cmp["sign_flips"]}')
    for lv in needed:
        if not arithmetic_ok(levels[lv]):
            reasons.append(f'arithmetic_width:{lv}')
        reasons += [f'{v}:{lv}' for v in consistency(levels[lv])]
    return not reasons, reasons


def select_level(case_levels, candidates):
    """First candidate (in registered order) where every case is ready; None if none is."""
    report = []
    for main in candidates:
        status = {cid: level_ready(lv, tuple(main)) for cid, lv in case_levels.items()}
        missing = [cid for cid, (ok, _) in status.items() if ok is None]
        failing = {cid: why for cid, (ok, why) in status.items() if ok is False}
        report.append(dict(level=list(main), cases=len(status), missing=missing, failing=failing))
        if failing:
            continue                     # one failing case rejects the candidate; go to the next one
        if missing:
            return None, report          # must compute before this candidate can be judged
        return tuple(main), report
    return None, report


def meets(value, criterion):
    """Criterion classification against the card threshold (effect: >= +1/100; harm: <= -1/100)."""
    return value >= EPS_R if criterion == 'effect' else value <= -EPS_R


def representation(fine, coarse):
    """Normalized six-contrast difference between a 1/1000-rate regime and its r-rounded version at the
    same (K, ref), plus criterion agreement for the two scored metrics (MV: G_M effect, SH: G_S harm).
    A criterion disagreement only counts if the fine value is farther than TOL_NUM from the threshold."""
    delta = max(abs(normalized(fine, k) - normalized(coarse, k)) for k in CONTRASTS)
    flips = []
    for key, criterion, boundary in (('G_M', 'effect', EPS_R), ('G_S', 'harm', -EPS_R)):
        f, c = normalized(fine, key), normalized(coarse, key)
        if meets(f, criterion) != meets(c, criterion) and abs(f - boundary) > TOL_NUM:
            flips.append(key)
    return dict(max_normalized_delta=delta, criterion_flips=flips, ok=delta <= TOL_NUM and not flips)
