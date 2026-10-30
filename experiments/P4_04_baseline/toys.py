"""Exact supplied L4.4 teaching fixtures; no queue model or author forecast."""
from fractions import Fraction as F

from experiments.P4_02_reading.toys import TOYS, cells


def expected_cost(weights, true_gaps, forecasts, theta, base=10):
    w, d, forecast = (tuple(map(F, x)) for x in (weights, true_gaps, forecasts))
    theta = F(theta)
    if len(w) != len(d) or len(w) != len(forecast) or not w or min(w) < 0 or sum(w) != 1:
        raise ValueError('aligned finite probability distribution required')
    if theta < 0:
        raise ValueError('nonnegative margin required')
    return F(base) + sum(p * gap for p, gap, pred in zip(w, d, forecast) if pred < -theta)


def two_state(name, theta):
    d, dh = TOYS[name]
    ref = cells(d, dh)
    old = expected_cost((F(1, 2),) * 2, d, (sum(dh) / 2,) * 2, theta)
    current = expected_cost((F(1, 2),) * 2, d, dh, theta)
    recovery = (ref['L00'] - old) / ref['GM'] if ref['GM'] > 0 else None
    return dict(L00_theta=old, L10_theta=current, GS_theta=old-current,
                deltaL10=current-ref['L10'], R_M=recovery)


def goldens():
    weights = (F(1, 3),) * 3
    d = (F(2), F(-3), F(-3, 5))
    forecast = (F(-1, 2), F(-4), F(-4, 5))
    three = {str(theta): expected_cost(weights, d, forecast, theta) for theta in (0, 1, 5)}
    correct_model = expected_cost(weights, d, d, 0)
    changed_forecast = (F(-3), *forecast[1:])
    changed = expected_cost(weights, d, changed_forecast, 1)
    return dict(three_snapshots=three, L01=correct_model,
                recovery_theta1=(three['0']-three['1'])/(three['0']-correct_model),
                changed_y1_theta1=changed,
                changed_y1_recovery=(three['0']-changed)/(three['0']-correct_model),
                two_states=[dict(toy=name, theta=str(theta), **two_state(name, theta))
                            for name, values in [('T-AB',(0,F(3,2),F(7,2))),
                                                 ("T-C'",(0,F(3,2),F(7,2))),
                                                 ('T-A',(0,F(3,2)))] for theta in values])
