"""Doan Van Tai — finite-horizon backward values with reachable domains."""
import math


def value_backward(managed, H, capacity, rates, P, q_values, dt):
    """Per-slot amounts; returns {(q,mode): expected cumulative occupancy}.

    Build only finite-horizon reachable domains. No assumption that a finite
    backlog grid is closed under positive arrivals, and no artificial cap.
    """
    if type(H) is not int or H < 0 or capacity < 0 or managed < 0 or dt <= 0:
        raise ValueError('invalid horizon, amount, or dt')
    modes = tuple(rates)
    if not modes or set(P) != set(modes) or any(r < 0 for r in rates.values()):
        raise ValueError('invalid rates/transition modes')
    for mode in modes:
        if set(P[mode]) != set(modes) or any(not math.isfinite(float(v)) or v < 0 for v in P[mode].values()):
            raise ValueError('invalid transition row')
        if not math.isclose(float(sum(P[mode].values())), 1, rel_tol=0, abs_tol=1e-14):
            raise ValueError('transition row must sum to one')
    start = {(q, m) for q in q_values for m in modes}
    if any(q < 0 for q, _ in start):
        raise ValueError('negative initial backlog')
    domains = [start]
    for _ in range(H):
        domains.append({(max(0,q+rates[m]+managed-capacity), n)
                        for q,m in domains[-1] for n in modes if P[m][n] > 0})
    values = {state: 0 for state in domains[-1]}
    for domain in reversed(domains[:-1]):
        previous = {}
        for q, m in domain:
            q2 = max(0,q+rates[m]+managed-capacity)
            previous[q,m] = dt*q2 + sum(prob*values[q2,n]
                                       for n,prob in P[m].items() if prob > 0)
        values = previous
    return values
