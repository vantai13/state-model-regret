"""Exact binomial/multinomial design calculations; assumptions are not observations."""
from fractions import Fraction as F
from math import comb

from experiments.R3R_06_cards import stats
from experiments.R3R_06_cards.verdict import PRIMARY_ALPHA, PRIMARY_PI0


def probability(n, lo, hi, p):
    p = F(p)
    return sum((F(comb(n, k)) * p**k * (1-p)**(n-k) for k in range(lo, hi+1)), F(0))


def pass_power(n, p_plus, p_minus):
    support = stats.k_support(n, PRIMARY_PI0, PRIMARY_ALPHA)
    reject = stats.k_reject(n, PRIMARY_PI0, PRIMARY_ALPHA)
    return probability(n, support, n, p_plus) * probability(n, 0, reject, p_minus)


def r5_failure(n, r):
    return probability(n, n//10 + 1, n, r)


def robust_region_power(n, p, r, *, plus):
    """p = conditional MEETS rate given resolved; U independent of latent label.

    Exact sum with R5 and the least favorable R4 endpoint, not a product assuming
    R5 is independent of success counts. UNDEFINED probability is assumed zero.
    """
    p, r = F(p), F(r)
    hi = stats.k_support(n, PRIMARY_PI0, PRIMARY_ALPHA)
    low = stats.k_reject(n, PRIMARY_PI0, PRIMARY_ALPHA)
    ans = F(0)
    for u in range(n//10 + 1):
        pu = F(comb(n, u))*r**u*(1-r)**(n-u)
        lo_k, hi_k = (hi, n-u) if plus else (0, min(n-u, low-u))
        ans += pu * probability(n-u, lo_k, hi_k, p)
    return ans


def robust_pass_power(n, p_plus, p_minus, r_plus, r_minus):
    return robust_region_power(n, p_plus, r_plus, plus=True) * robust_region_power(n, p_minus, r_minus, plus=False)


def select_allocation(budget_cpu_hours, p95_bundle_seconds, fixed_seconds, *, numerics_closed):
    """Pure rule evaluator. Production must additionally verify the numerics receipt.

    p95 is CPU seconds for one complete main/coarse-K/coarse-dt bundle. Fixed cost
    includes both-level anchors, zero controls and registered identical-model tests.
    """
    if not numerics_closed:
        raise ValueError('numerics v1.3.1 not closed')
    B, t, fixed = map(F, (budget_cpu_hours, p95_bundle_seconds, fixed_seconds))
    if B <= 0 or t <= 0 or fixed < 0:
        raise ValueError('positive budget/timing and nonnegative fixed costs required')
    def cost(n, bnd):
        return F(13, 10) * ((4*n+2*bnd)*t+fixed)
    chosen = next((n for n in (60, 40, 30) if cost(n, 0) <= 3600*B), None)
    if chosen is None:
        return dict(status='HOLD_BUDGET', n=None, bnd=None)
    bnd = 15 if cost(chosen, 15) <= 3600*B else 0
    return dict(status='RULE_EVALUATED_NOT_PREREG', n=chosen, bnd=bnd,
                planned_cpu_hours=str(cost(chosen, bnd)/3600))


def tables():
    grid = [dict(n=n, p_plus=str(pp), p_minus=str(pm), pass_probability=float(pass_power(n, pp, pm)))
            for n in (30, 40, 60) for pp in (F(3,5), F(7,10), F(4,5))
            for pm in (F(1,10), F(1,5), F(3,10), F(2,5))]
    r5 = [dict(n=n, r=str(r), inconclusive_one_region=float(r5_failure(n, r)))
          for n in (30,40,60) for r in (F(3,100),F(5,100),F(8,100),F(12,100))]
    joint = [dict(n=n, p_plus='7/10', p_minus='1/5', r_plus=str(r), r_minus=str(r),
                  exact_R4_R5_pass=float(robust_pass_power(n, F(7,10), F(1,5), r, r)),
                  heuristic_R5_only=float(pass_power(n,F(7,10),F(1,5))*(1-r5_failure(n,r))**2))
             for n in (30,40,60) for r in (F(0),F(3,100),F(5,100),F(8,100))]
    return dict(scope='hypothetical design probabilities, not CF predictions; UNDEFINED=0',
                power=grid, R5=r5, R4_R5=joint)
