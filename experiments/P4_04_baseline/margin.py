"""Same physical gaps as frozen population.py; margin changes decisions only.

Doan Van Tai — AI implementation under authorization. No plant calls at import.
"""
from fractions import Fraction as F
import sys

import numpy as np

from experiments.R3R_08_population_numerics.piecewise import LD, EPS, number


def significant_bits(value):
    """Ignore ABI padding of the x86 80-bit long double stored in 16 bytes."""
    value = LD(value)
    if not np.isfinite(value):
        raise ValueError('finite value required for bit comparison')
    raw = np.asarray(value, dtype=LD).tobytes()
    if np.finfo(LD).nmant == 63 and np.dtype(LD).itemsize in (12, 16):
        return raw[:10] if sys.byteorder == 'little' else raw[-10:]
    return raw


def pair_loss_margin(A, B, cost=F(0), *, model='mean', theta=LD(0), theta_error=LD(0)):
    """Switch iff forecast < -theta; theta never enters the physical cost.

    At theta=theta_error=0 this retains the exact operation order of pair_loss,
    including certified ties and its error/ambiguity calculations. At positive
    margin the ambiguity interval also covers the estimated Stay scale.
    """
    theta, theta_error = LD(theta), LD(theta_error)
    if not np.isfinite(theta) or not np.isfinite(theta_error) or min(theta, theta_error) < 0:
        raise ValueError('finite nonnegative margin and margin error required')
    d = A['d'][:, None] + B['d'][None, :] + number(cost)
    ed = A['ed'][:, None] + B['ed'][None, :] + 64 * EPS * (abs(d) + 1)
    if model == 'true':
        h = d; eh = ed
    elif model == 'mean':
        h = A['h'][:, None] + B['h'][None, :] + number(cost)
        eh = A['eh'][:, None] + B['eh'][None, :] + 64 * EPS * (abs(h) + 1)
        certified = ((A['zero_h'][:, None] & B['zero_h'][None, :]) |
                     (A['sat_h'][:, None] & B['sat_h'][None, :]))
        h = np.where(certified, number(cost), h)
        eh = np.where(certified, LD(0), eh)
    else:
        raise ValueError('unknown action model')
    weights = A['w'][:, None] * B['w'][None, :]
    if theta == 0 and theta_error == 0:
        s = h; es = eh
    else:
        s = h + theta
        es = eh + theta_error + 64 * EPS * (abs(h) + abs(theta) + abs(s) + 1)
    switch = s < 0
    ambiguous = (s - es < 0) & (s + es >= 0)
    contribution = np.where(switch, d, LD(0))
    loss = (weights * contribution).sum(dtype=LD)
    error = (weights * np.where(ambiguous, abs(d) + ed,
                               np.where(switch, ed, LD(0)))).sum(dtype=LD)
    maxcost = max(LD(1), np.max(abs(d) + ed))
    error += (A['w_error'] + B['w_error'] + A['w_error'] * B['w_error']) * maxcost
    error += 1024 * weights.size * EPS * maxcost
    return loss, error, float(weights[ambiguous].sum(dtype=LD))
