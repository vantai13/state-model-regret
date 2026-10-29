"""Doan Van Tai — L3R.6 per-regime labels, region states and verdict maps.

Pure functions on hypothetical counts/values: no engine, no CF, no outcome data.
Labels apply after the L3R.7 escalation budget is spent (R2/R3); R1 readiness and
the R6 refinement difference are inputs, never certified error bounds.
"""
from fractions import Fraction as F
from itertools import product

from experiments.R3R_05_contract.rules import EPS_R, EPS_E, U_MAX
from experiments.R3R_06_cards import stats

LABELS = ('MEETS', 'FAILS', 'UNRESOLVED', 'UNDEFINED')
CRITERIA = {                       # boundary, relation that MEETS
    'effect': (EPS_R, '>='),       # Hyp-MV: G_M/Cref >= +1%
    'harm': (-EPS_R, '<='),        # Hyp-SH: G_S/Cref <= -1%
    'noninferiority': (-EPS_E, '>='),  # Hyp-Gamma: Gamma/Cref >= -0.5%
}
PRIMARY_ALPHA, PRIMARY_PI0 = F(1, 40), F(1, 2)
RANK = {'PASS': 3, 'WEAKEN': 2, 'INCONCLUSIVE': 1}      # FALSIFY handled separately


def regime_label(criterion, value, measured_difference, *, r1_ready=True, certified_exact=False):
    """value is the normalized estimate (G/Cref); None means Cref=0 (UNDEFINED)."""
    if value is None: return 'UNDEFINED'
    boundary, rel = CRITERIA[criterion]
    z, d = F(value), F(measured_difference)
    if d < 0: raise ValueError('nonnegative measured refinement difference required')
    if not r1_ready: return 'UNRESOLVED'
    if not certified_exact and abs(z - boundary) <= d: return 'UNRESOLVED'
    meets = z >= boundary if rel == '>=' else z <= boundary
    return 'MEETS' if meets else 'FAILS'


def condition_label(value, threshold, measured_difference, *, strict, certified_exact=False):
    """Pre-declared eligibility condition on an outcome (Gamma card only).
    Near-boundary values are AMBIGUOUS: not scored, reported separately."""
    if value is None: return 'UNDEFINED'
    z, t, d = F(value), F(threshold), F(measured_difference)
    if d < 0: raise ValueError('nonnegative measured refinement difference required')
    if not certified_exact and abs(z - t) <= d: return 'AMBIGUOUS'
    return 'ELIGIBLE' if (z > t if strict else z >= t) else 'EXCLUDED'


def all_conditions(labels):
    """Conjunction: any EXCLUDED/UNDEFINED excludes; else any AMBIGUOUS is ambiguous."""
    if any(x in ('EXCLUDED', 'UNDEFINED') for x in labels): return 'EXCLUDED'
    return 'AMBIGUOUS' if 'AMBIGUOUS' in labels else 'ELIGIBLE'


def _n(c): return c.get('MEETS', 0) + c.get('FAILS', 0) + c.get('UNRESOLVED', 0)


def r5(counts):
    """u_max=.10 per scored region; UNDEFINED is excluded from N, UNRESOLVED is not."""
    n = _n(counts)
    if n == 0: return 'N0'
    if F(counts.get('UNRESOLVED', 0), n) > U_MAX: return 'UMAX'
    return None


def plus_state(n, k, p0=PRIMARY_PI0, alpha=PRIMARY_ALPHA):
    if stats.lower_bound_exceeds(n, k, p0, alpha): return 'S'
    if stats.upper_bound_below(n, k, p0, alpha): return 'R'
    return 'U_hi' if F(k, n) > p0 else 'U_lo'


def minus_state(n, k, p0=PRIMARY_PI0, alpha=PRIMARY_ALPHA):
    if stats.upper_bound_below(n, k, p0, alpha): return 'N'
    if stats.lower_bound_exceeds(n, k, p0, alpha): return 'Y'
    return 'U'


PRIMARY_TABLE = {
    ('S', 'N'): ('PASS', None), ('S', 'U'): ('WEAKEN', 'W2'), ('S', 'Y'): ('WEAKEN', 'W1'),
    ('U_hi', 'N'): ('WEAKEN', 'W3'), ('U_hi', 'U'): ('WEAKEN', 'W3'), ('U_hi', 'Y'): ('WEAKEN', 'W1'),
    ('U_lo', 'N'): ('INCONCLUSIVE', 'PRECISION'), ('U_lo', 'U'): ('INCONCLUSIVE', 'PRECISION'),
    ('U_lo', 'Y'): ('INCONCLUSIVE', 'PRECISION'),
    ('R', 'N'): ('FALSIFY', None), ('R', 'U'): ('FALSIFY', None), ('R', 'Y'): ('FALSIFY', None),
}


def primary_map(n_plus, k_plus, n_minus, k_minus, p0=PRIMARY_PI0, alpha=PRIMARY_ALPHA):
    return PRIMARY_TABLE[(plus_state(n_plus, k_plus, p0, alpha), minus_state(n_minus, k_minus, p0, alpha))]


def combine(results):
    """R4: identical verdict class across extremes is kept; otherwise downgrade.
    FALSIFY mixed with anything becomes INCONCLUSIVE (never WEAKEN)."""
    classes = {v for v, _ in results}
    if len(classes) == 1:
        v = classes.pop()
        return v, sorted({c for _, c in results if c}), False
    if 'FALSIFY' in classes:
        return 'INCONCLUSIVE', ['R4_FALSIFY_NOT_ROBUST'], True
    v = min(classes, key=RANK.get)
    return v, sorted({c for w, c in results if c and w == v} | {'R4_DOWNGRADE'}), True


def _extreme_counts(c, unresolved_as):
    m, f, u = c.get('MEETS', 0), c.get('FAILS', 0), c.get('UNRESOLVED', 0)
    return m + f + u, m + (u if unresolved_as == 'MEETS' else 0)


def primary_verdict(plus, minus, *, validity_reasons=(), p0=PRIMARY_PI0, alpha=PRIMARY_ALPHA):
    """plus/minus: label counts. Returns verdict, reason codes and R4 audit trail."""
    if validity_reasons:
        return dict(verdict='INCONCLUSIVE', codes=['VALIDITY:' + r for r in validity_reasons], r4=None)
    for name, c in (('plus', plus), ('minus', minus)):
        bad = r5(c)
        if bad: return dict(verdict='INCONCLUSIVE', codes=[f'VALIDITY:R5_{bad}_{name}'], r4=None)
    corners = {}
    for up, um in product(('MEETS', 'FAILS'), repeat=2):
        corners[(up, um)] = primary_map(*_extreme_counts(plus, up), *_extreme_counts(minus, um), p0, alpha)
    v, codes, downgraded = combine(list(corners.values()))
    uniform = combine([corners[('MEETS', 'MEETS')], corners[('FAILS', 'FAILS')]])
    return dict(verdict=v, codes=codes, r4=dict(downgraded=downgraded,
                corners={f'{a}/{b}': list(r) for (a, b), r in corners.items()},
                lesson_two_uniform=list(uniform[:2])))


def gamma_map(n, k, *, pi0, alpha, n_min):
    if n < n_min: return 'INCONCLUSIVE', 'N_MIN'
    if stats.lower_bound_exceeds(n, k, pi0, alpha): return 'PASS', None
    if stats.upper_bound_below(n, k, pi0, alpha): return 'FALSIFY', 'SUBSTITUTION'
    if F(k, n) >= F(pi0): return 'WEAKEN', 'POINT_ONLY'
    return 'INCONCLUSIVE', 'PRECISION'


def gamma_verdict(counts, *, pi0, alpha, n_min, validity_reasons=()):
    """counts over ELIGIBLE regimes only; exclusions are reported, never scored."""
    if validity_reasons:
        return dict(verdict='INCONCLUSIVE', codes=['VALIDITY:' + r for r in validity_reasons], r4=None)
    bad = r5(counts)
    if bad: return dict(verdict='INCONCLUSIVE', codes=[f'VALIDITY:R5_{bad}'], r4=None)
    ext = {u: gamma_map(*_extreme_counts(counts, u), pi0=pi0, alpha=alpha, n_min=n_min) for u in ('MEETS', 'FAILS')}
    v, codes, downgraded = combine(list(ext.values()))
    return dict(verdict=v, codes=codes, r4=dict(downgraded=downgraded, extremes={k: list(r) for k, r in ext.items()}))


def plus_power(n, p, p0=PRIMARY_PI0, alpha=PRIMARY_ALPHA):
    return stats.prob_at_least(n, stats.k_support(n, p0, alpha), p)


def minus_power(n, p, p0=PRIMARY_PI0, alpha=PRIMARY_ALPHA):
    return stats.prob_at_most(n, stats.k_reject(n, p0, alpha), p)


def primary_pass_power(n_plus, p_plus, n_minus, p_minus, p0=PRIMARY_PI0, alpha=PRIMARY_ALPHA):
    """Independent draws in the two regions; no unresolved regimes assumed."""
    return plus_power(n_plus, p_plus, p0, alpha) * minus_power(n_minus, p_minus, p0, alpha)


def gamma_pass_power(n, p, *, pi0, alpha):
    return stats.prob_at_least(n, stats.k_support(n, pi0, alpha), p)
