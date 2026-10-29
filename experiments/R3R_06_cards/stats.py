"""Doan Van Tai — L3R.6 exact one-sided Clopper–Pearson decisions and power.

Decisions use exact rational binomial tails, not floating Beta quantiles:
lower CP bound L(k) > p0  <=>  P_p0(X >= k) < alpha, and
upper CP bound U(k) < p0  <=>  P_p0(X <= k) < alpha,
because P_p(X >= k) = I_p(k, n-k+1) increases in p. Floats are for display only.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import comb


def _check(n, k):
    if isinstance(n, bool) or isinstance(k, bool) or not isinstance(n, int) or not isinstance(k, int):
        raise ValueError('integer counts required')
    if n < 0 or not 0 <= k <= n:
        raise ValueError('need 0 <= k <= n')


@lru_cache(maxsize=None)
def upper_tail(n, k, p):
    """P(X >= k), X ~ Bin(n, p), exact for rational p."""
    _check(n, k); p = F(p)
    return sum(comb(n, j) * p**j * (1 - p)**(n - j) for j in range(k, n + 1))


@lru_cache(maxsize=None)
def lower_tail(n, k, p):
    """P(X <= k), X ~ Bin(n, p), exact for rational p."""
    _check(n, k); p = F(p)
    return sum(comb(n, j) * p**j * (1 - p)**(n - j) for j in range(0, k + 1))


def lower_bound_exceeds(n, k, p0, alpha):
    """One-sided (1-alpha) CP lower bound strictly above p0."""
    return n > 0 and upper_tail(n, k, F(p0)) < F(alpha)


def upper_bound_below(n, k, p0, alpha):
    """One-sided (1-alpha) CP upper bound strictly below p0."""
    return n > 0 and lower_tail(n, k, F(p0)) < F(alpha)


def k_support(n, p0, alpha):
    """Smallest k whose lower bound exceeds p0; None if impossible at this n."""
    return next((k for k in range(n + 1) if lower_bound_exceeds(n, k, p0, alpha)), None)


def k_reject(n, p0, alpha):
    """Largest k whose upper bound is below p0; None if impossible at this n."""
    return next((k for k in range(n, -1, -1) if upper_bound_below(n, k, p0, alpha)), None)


def cp_bounds(n, k, alpha):
    """Display-only floating one-sided CP bounds (lower, upper)."""
    from scipy.stats import beta
    a = float(alpha)
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
    return lo, hi


def prob_at_least(n, k, p):
    """P(X >= k) under a true rate p; k None means the event is impossible."""
    return F(0) if k is None else upper_tail(n, k, F(p))


def prob_at_most(n, k, p):
    return F(0) if k is None else lower_tail(n, k, F(p))
