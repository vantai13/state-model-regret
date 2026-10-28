"""Shared Gaussian threshold ledger and feasible four-summary identity map.

Doan Van Tai. All quantities are normalized by the cell's Cref during fitting.
No queue, grid, D, cost engine or outcome-file access in this module.
"""
import numpy as np
from scipy.special import ndtr

SUMMARY_NAMES = ('E_delta', 'E_delta_hat', 'E_neg', 'T10')
CONTRASTS = ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1')


def feasible(values):
    """Two-stage range projection, shared by both models; not Euclidean projection."""
    s = np.asarray(values, dtype=float).copy()
    if s.shape[-1] != 4 or not np.isfinite(s).all():
        raise ValueError('four finite summaries required')
    s[..., 2] = np.maximum(s[..., 2], np.maximum(0, -s[..., 0]))
    s[..., 3] = np.clip(s[..., 3], -s[..., 2], s[..., 0] + s[..., 2])
    return s


def contrasts(values):
    """Strict negative gap selects Switch, exactly zero selects Stay (T01)."""
    s = feasible(values)
    mu, mh, en, t10 = np.moveaxis(s, -1, 0)
    a00, a01 = mh < 0, mu < 0
    l00, l01, l10, l11 = a00 * mu, a01 * mu, t10, -en
    return np.stack((l00-l10, abs(mu)*(a00 != a01), l00-l11,
                     l10+l01-l00-l11, l01-l11, l10-l11), axis=-1)


def gaussian(mu, sigma, bias, tau, rho=0.):
    """Four summaries of jointly normal Delta and model error; degeneracies explicit."""
    mu, sigma, bias, tau, rho = np.broadcast_arrays(*map(lambda x: np.asarray(x, dtype=float),
                                                       (mu, sigma, bias, tau, rho)))
    if (not all(np.isfinite(x).all() for x in (mu, sigma, bias, tau, rho)) or
            np.any(sigma < 0) or np.any(tau < 0) or np.any(abs(rho) > 1)):
        raise ValueError('finite values, nonnegative scales and |rho|<=1 required')
    mh = mu + bias
    phi = lambda z: np.exp(-.5*z*z) / np.sqrt(2*np.pi)
    safe_sigma = np.where(sigma > 0, sigma, 1.)
    z = mu / safe_sigma
    en = np.where(sigma > 0, sigma*phi(z)-mu*ndtr(-z), np.maximum(0., -mu))
    variance = np.maximum(0., sigma*sigma + tau*tau + 2*rho*sigma*tau)
    sd = np.sqrt(variance)
    safe_sd = np.where(sd > 0, sd, 1.)
    cov = sigma*sigma + rho*sigma*tau
    t10 = np.where(sd > 0, mu*ndtr(-mh/safe_sd)-cov/safe_sd*phi(mh/safe_sd), mu*(mh < 0))
    return feasible(np.stack((mu, mh, en, t10), axis=-1))
