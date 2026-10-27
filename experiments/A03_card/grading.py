"""Doan Van Tai — preregistered three-valued grading on supplied intervals.

No engine/cell/D import. Arithmetic is exact on supplied decimal endpoints;
numeric enclosure validity remains the engine's responsibility. Not a CI test.
"""
from dataclasses import dataclass
from fractions import Fraction as F

STANDS = 'STANDS'
FAILS = 'DOES_NOT_STAND'
UNKNOWN = 'UNRESOLVED'
EXCLUDED = 'EXCLUDED_ZERO_REFERENCE'
CONTRASTS = ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1')


def fraction(x):
    if isinstance(x, bool):
        raise ValueError('boolean is not a numeric endpoint')
    return x if isinstance(x, F) else F(str(x))


@dataclass(frozen=True)
class Interval:
    lo: F
    hi: F

    def __post_init__(self):
        object.__setattr__(self, 'lo', fraction(self.lo))
        object.__setattr__(self, 'hi', fraction(self.hi))
        if self.lo > self.hi:
            raise ValueError('reversed interval')

    def __sub__(self, other):
        return Interval(self.lo - other.hi, self.hi - other.lo)


def ratio(numerator, denominator):
    if denominator.lo <= 0:
        raise ZeroDivisionError('positive denominator lower bound required')
    corners = [a / b for a in (numerator.lo, numerator.hi) for b in (denominator.lo, denominator.hi)]
    return Interval(min(corners), max(corners))


def judge(interval, relation, threshold):
    t = fraction(threshold)
    if relation == '<=':
        return STANDS if interval.hi <= t else FAILS if interval.lo > t else UNKNOWN
    if relation == '>=':
        return STANDS if interval.lo >= t else FAILS if interval.hi < t else UNKNOWN
    if relation == '<':
        return STANDS if interval.hi < t else FAILS if interval.lo >= t else UNKNOWN
    if relation == '>':
        return STANDS if interval.lo > t else FAILS if interval.hi <= t else UNKNOWN
    raise ValueError('unsupported relation')


def combine(verdicts, quantifier='all'):
    states = list(verdicts)
    if quantifier not in ('all', 'any'):
        raise ValueError('quantifier must be all/any')
    if not states:
        return UNKNOWN  # never claim support from an empty eligible domain
    if any(v not in (STANDS, FAILS, UNKNOWN, EXCLUDED) for v in states):
        raise ValueError('unknown verdict')
    if quantifier == 'all':
        return FAILS if FAILS in states else STANDS if all(v == STANDS for v in states) else UNKNOWN
    return STANDS if STANDS in states else FAILS if all(v == FAILS for v in states) else UNKNOWN


def get(row, key):
    return Interval(*row['intervals'][key])


def validate_reference(row):
    if get(row, 'C_ref') != get(row, 'L11'):
        raise ValueError('C_ref must be L11 from this same row/refinement')
    context = row['reference_context']
    if context['refinement'] != row['refinement'] or fraction(context['dt_s']) != fraction(row['dt_s']):
        raise ValueError('mixed-refinement reference context')
    if get(row, 'C_ref').hi < 0:
        raise ValueError('negative absolute reference cost')


def numerical_hold(row):
    bands = row.get('unresolved_mass', {})
    if (row.get('status') != 'BOUNDED' or row.get('numeric_budget_met') is not True or
            not {'oracle', 'M0', 'D22'} <= set(bands)):
        return True
    return any(fraction(v) > F(1, 100) for v in bands.values())


def refinement(coarse, fine):
    """D1/D24 at adjacent levels, using this pair's fine-level Cref.

    PASS means the interval bounds certify the rule; FAIL or unresolved bounds
    both make the prediction inconclusive at this discretization.
    """
    validate_reference(coarse)
    validate_reference(fine)
    if fine['refinement'] != 2 * coarse['refinement'] or fraction(coarse['dt_s']) != 2 * fraction(fine['dt_s']):
        raise ValueError('refinement pair must be adjacent with dt ratio two')
    if numerical_hold(coarse) or numerical_hold(fine):
        return UNKNOWN
    C = get(fine, 'C_ref')
    results = []
    for metric in CONTRASTS:
        delta = get(fine, metric) - get(coarse, metric)
        low_abs = 0 if delta.lo <= 0 <= delta.hi else min(abs(delta.lo), abs(delta.hi))
        high_abs = max(abs(delta.lo), abs(delta.hi))
        if high_abs <= F(1, 400) * C.lo:
            state = STANDS
        elif low_abs > F(1, 400) * C.hi:
            state = FAILS
        else:
            state = UNKNOWN
        if C.lo > 0 and get(coarse, 'C_ref').lo > 0:
            c = ratio(get(coarse, metric), get(coarse, 'C_ref'))
            f = ratio(get(fine, metric), C)
            eps = F(1, 200)
            certain_flip = ((c.lo > eps and f.hi < -eps) or (f.lo > eps and c.hi < -eps))
            possible_flip = ((c.hi > eps and f.lo < -eps) or (f.hi > eps and c.lo < -eps))
            if certain_flip:
                state = FAILS
            elif possible_flip and state == STANDS:
                state = UNKNOWN
        results.append(state)
    return combine(results)


def point_claim(which, row):
    """Grade one row at its own dt, after numerical/convergence eligibility."""
    C = get(row, 'C_ref')
    if which in ('P2', 'P3', 'P5_K', 'P5_Q'):
        if C.lo == C.hi == 0:
            return EXCLUDED
        if C.lo <= 0:
            return UNKNOWN
    if which == 'P2':
        # Cancel L00 before propagating uncertainty (GS-GM = L01-L10).
        return judge(ratio(get(row, 'L01') - get(row, 'L10'), C), '>=', F(1, 100))
    if which == 'P3':
        return judge(ratio(get(row, 'Gamma'), C), '>', F(1, 200))
    if which == 'P5_K':
        return judge(ratio(get(row, 'G_M'), C), '<=', F(1, 200))
    if which == 'P5_Q':
        return judge(ratio(get(row, 'G_M'), C), '>=', F(1, 100))
    if which == 'P6':
        return combine([judge(get(row, 'V'), '>', 0), judge(get(row, 'V') - get(row, 'F'), '>', 0)])
    raise KeyError(which)


def grade_cell(which, fine, coarse=None):
    validate_reference(fine)
    if which in ('P2', 'P3', 'P5_K', 'P5_Q') and get(fine, 'C_ref') == Interval(0, 0):
        return dict(verdict=EXCLUDED, reason='excluded_Cref_zero', sensitive_to_dt=None)
    if coarse is None:
        return dict(verdict=UNKNOWN, reason='missing_adjacent_dt_check', sensitive_to_dt=None)
    quality = refinement(coarse, fine)
    if numerical_hold(fine) or quality != STANDS:
        return dict(verdict=UNKNOWN, reason='numeric_hold_or_dt_not_certified', sensitive_to_dt=None)
    final = point_claim(which, fine)
    previous = point_claim(which, coarse)
    return dict(verdict=final, reason='excluded_Cref_zero' if final == EXCLUDED else 'graded_at_final_dt',
                sensitive_to_dt=(final != previous))


def carry_rule(main_verdict):
    """Locked before A04: carry all rules whose main part is not refuted."""
    if main_verdict not in (STANDS, FAILS, UNKNOWN, EXCLUDED):
        raise ValueError('unknown verdict')
    return main_verdict != FAILS
