"""Toy decision-geometry checks for the review (NOT the repo plant, NOT grid cells).

Purpose: verify the numbers quoted in the review about how the 2x2 contrasts of the
single-observation design behave as pure functions of (margin mu, posterior spread sigma,
M0 bias), and how averaging over an observation population changes them.

Model: given an observation y, the true gap Delta ~ N(mu, sigma^2) under the posterior D.
M0 predicts Delta_hat = Delta + b (constant bias) or Delta_hat = k * Delta (exaggeration).
Binary decision: Switch iff gap < -c (c = switching threshold, 0 by default); ties -> Stay.
S0 decides from the posterior mean of the (predicted) gap; S1 decides per state.
"""
import numpy as np
from scipy.stats import norm


def trunc_mean_part(mu, sigma, a, c):
    """E[Delta * 1(a <= Delta < c)] for Delta ~ N(mu, sigma^2)."""
    al, be = (a - mu) / sigma, (c - mu) / sigma
    return mu * (norm.cdf(be) - norm.cdf(al)) + sigma * (norm.pdf(al) - norm.pdf(be))


def prob(mu, sigma, a, c):
    al, be = (a - mu) / sigma, (c - mu) / sigma
    return norm.cdf(be) - norm.cdf(al)


def contrasts_const_bias(mu, sigma, b, c=0.0):
    """Six-contrast core for one observation, constant bias b, threshold c (Switch iff gap < -c).
    Costs measured relative to always-Stay: cost(Switch) - cost(Stay) = Delta + c."""
    # true per-state optimal: Switch iff Delta + c < 0
    # S1M0 switches iff Delta + b + c < 0
    # regret of S1M0 vs oracle = E[|Delta + c| * 1(decisions differ)]
    lo, hi = sorted([-c, -c - b])
    # states between the two thresholds are decided differently
    # |Delta + c| on that band
    part = trunc_mean_part(mu, sigma, lo, hi) + c * prob(mu, sigma, lo, hi)
    G_M_S1 = abs(part)  # sign of Delta + c is constant on the band
    a01 = (mu + c) < 0
    a00 = (mu + b + c) < 0
    G_M = abs(mu + c) * (a00 != a01)
    return dict(G_M=G_M, G_M_S1=G_M_S1, Gamma=G_M_S1 - G_M, flip=a00 != a01)


def contrasts_scale(mu, sigma, k, c=0.0, n=200001):
    """M0 predicts k * Delta (same-sign exaggeration when k > 1); threshold c."""
    x = np.linspace(mu - 9 * sigma, mu + 9 * sigma, n)
    w = norm.pdf(x, mu, sigma); w /= w.sum()
    true_sw = (x + c) < 0
    m0_sw = (k * x + c) < 0
    G_M_S1 = float(np.sum(w * np.abs(x + c) * (true_sw != m0_sw)))
    a01 = (mu + c) < 0
    a00 = (k * mu + c) < 0
    G_M = abs(mu + c) * (a00 != a01)
    return dict(G_M=G_M, G_M_S1=G_M_S1, Gamma=G_M_S1 - G_M)


def population(mu0, s_mu, sigma_post, b, c=0.0, n=4001):
    """Average one-observation contrasts over posterior means mu(y) ~ N(mu0, s_mu^2)."""
    m = np.linspace(mu0 - 8 * s_mu, mu0 + 8 * s_mu, n)
    w = norm.pdf(m, mu0, s_mu); w /= w.sum()
    acc = dict(G_M=0.0, G_M_S1=0.0, Gamma=0.0, p_flip=0.0)
    for mi, wi in zip(m, w):
        r = contrasts_const_bias(mi, sigma_post, b, c)
        acc['G_M'] += wi * r['G_M']; acc['G_M_S1'] += wi * r['G_M_S1']
        acc['Gamma'] += wi * r['Gamma']; acc['p_flip'] += wi * r['flip']
    return acc


if __name__ == '__main__':
    print('A. single observation, Gaussian, constant bias (mu = +0.5, sigma = 1 -> p_sw = Phi(-0.5) = %.3f)' % norm.cdf(-0.5))
    for b in [-0.2, -0.45, -0.55, -0.6, -1.0, -3.0, +0.6]:
        r = contrasts_const_bias(0.5, 1.0, b)
        print(f'   b={b:+.2f}  flip={r["flip"]!s:5}  G_M={r["G_M"]:.4f}  G_M|S1={r["G_M_S1"]:.4f}  Gamma={r["Gamma"]:+.4f}')

    print('\nB. exaggeration Delta_hat = k*Delta (k=2), mu=+0.5, sigma=1')
    for c in [0.0, 0.5, 1.0]:
        r = contrasts_scale(0.5, 1.0, 2.0, c)
        print(f'   c_sw={c:.1f}  G_M={r["G_M"]:.4f}  G_M|S1={r["G_M_S1"]:.4f}  Gamma={r["Gamma"]:+.4f}')

    print('\nC. knife-edge vs population: G_M as bias grows (single obs mu=0.5, sigma=1) vs population')
    print('   population: mu(y) ~ N(0.5, 0.8^2), sigma_post = 0.6 (total sd = 1.0)')
    for b in [-0.2, -0.4, -0.49, -0.51, -0.6, -0.8, -1.2]:
        s = contrasts_const_bias(0.5, 1.0, b)
        p = population(0.5, 0.8, 0.6, b)
        print(f'   b={b:+.2f}  single: G_M={s["G_M"]:.3f} Gamma={s["Gamma"]:+.3f}   population: G_M={p["G_M"]:.3f} Gamma={p["Gamma"]:+.3f} P(flip)={p["p_flip"]:.3f}')

    print('\nD. population Gamma sign vs informativeness of the observation (b = -0.3, total sd 1.0, mu0 = 0.5)')
    for r_inf in [0.05, 0.3, 0.6, 0.9, 0.98]:
        s_mu = np.sqrt(r_inf); sp = np.sqrt(1 - r_inf)
        p = population(0.5, s_mu, sp, -0.3)
        print(f'   share of Var(Delta) explained by y = {r_inf:.2f}:  G_M={p["G_M"]:.4f}  G_M|S1={p["G_M_S1"]:.4f}  Gamma={p["Gamma"]:+.4f}')
