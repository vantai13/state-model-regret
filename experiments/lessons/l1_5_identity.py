"""Doan Van Tai — L1.5 F5 regret identity and prediction interaction diagnostic.

F5 and direct regret deliberately take different computational paths. I_delta
checks use the same belief for cells 00 and 01. A zero mean is necessary under
the declared posterior/aggregation assumptions, not a certificate of calibration.
Units match J: packet·slot in the canonical example. No H0/H1 fitting is done here.
"""
from experiments.lessons.l1_4_factorial import choose


def regret_identity(delta, delta_hat):
    """F5 with ties Stay; do not call choose, so a bug there can be detected."""
    wrong_sign = abs(delta) if delta_hat*delta < 0 else 0
    tie_loss = max(0, -delta) if delta_hat == 0 else 0
    return wrong_sign+tie_loss


def direct_regret(J_stay, J_switch, delta_hat):
    """Choose from the predicted gap using L1.4, then score with true J."""
    costs = {"Stay": J_stay, "Switch": J_switch}
    return costs[choose(delta_hat)]-min(J_stay, J_switch)


def i_delta(d00, d10, d01, d11):
    """F6: prediction-level interaction; cell ordering is (state, model)."""
    return d11-d10-d01+d00


def belief_average(belief, values):
    """Sum b(x)*v(x) for a supplied normalized belief and compatible values."""
    return sum(belief[x]*values[x] for x in belief)


def i_delta_per_state(belief, delta, delta_hat_m0):
    """Cell11=delta(x), cell10=M0(x), cell01=E_b delta, cell00=E_b M0."""
    d01 = belief_average(belief, delta)
    d00 = belief_average(belief, delta_hat_m0)
    return {x: i_delta(d00, delta_hat_m0[x], d01, delta[x]) for x in belief}
