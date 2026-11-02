"""Phase 6 — H1/H0 predictor: parameter-only, M0-only, zero fit (Doan Van Tai, AI-assisted).

Forbidden here (DL-129): profiles.get, P.idle, population.evaluate/side, any finite-h M1 cost.
Allowed: stationary laws (mean queue, posterior), mean_idle profiles, the true aging kernel r2_keep.
"""
from fractions import Fraction as F
import os
os.environ.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
import numpy as np
from experiments.R3R_08_population_numerics import profiles, quadrature
from experiments.R3R_08_population_numerics import piecewise as P
from experiments.P4_09_stationary.predictor import StationaryCache, mean_side
from smr.stationary import r2_keep

THETA0, THETA1 = F(27, 50), F(7, 100)              # DL-129: theta(u) = 27/50 - 7/100*u


def h0_sign(x, u):
    """H0a: '+' iff 0 < x < theta(u); boundaries count as outside."""
    x, u = F(x), F(u)
    return '+' if 0 < x < THETA0 - THETA1*u else '-'


def stale_mean_side(lam, pre, post, kappa, h, ref, K, unit, law):
    """S0 + M0: forecast E[M0 gap(X_now) | old observation q], averaged over the hidden mode."""
    dt = F(1, 120*ref); H = h/dt
    if H.denominator != 1:
        raise ValueError('horizon not on slotted grid')
    H = int(H)
    amounts = [(lam+s*6+load-10)*dt for s in (-1, 1) for load in (pre, post)]
    quantum = profiles.quantum([*amounts, unit]); factor = unit/quantum
    if factor.denominator != 1:
        raise ValueError('unaligned mean action lattice')
    st, sw = [tuple(int((lam+s*6+load-10)*dt/quantum) for s in (-1, 1)) for load in (pre, post)]
    keep, ke = r2_keep(dt, kappa)
    dh = P.combine(P.mean_idle(H, sw, keep, ke), P.mean_idle(H, st, keep, ke), subtract=True)
    if pre == post:
        dh['modes'] = [(np.array([0, 1], dtype=np.int64), np.zeros(2, dtype=P.LD)) for _ in (0, 1)]
        dh['error'] = P.LD(0)
    scale = P.number(quantum*dt)
    budget = min(F(1, 10000), F(h)**2/F(10_000_000))          # same aging budget as profiles.get
    old_h = P.age(dh, 120*ref, st, keep, ke, error_budget_raw=P.number(budget)/scale)
    data = dict(profiles={'old_h': old_h}, factor=int(factor), scale=scale, identical_actions=pre == post)
    cap = max((int(x[-1])+int(factor)-1)//int(factor) for x, y in old_h['modes'])
    obs = quadrature.build(law, K, cap)
    q = obs['indices']; valid = q >= 0
    prior = np.zeros(len(q), dtype=P.LD); ep = np.zeros(len(q), dtype=P.LD)
    prior[valid], ep[valid] = law.posterior(q[valid])         # P(mode = 1 | old queue q)
    off, eo, zo, _ = profiles.values(data, 'old_h', q, 0)
    on, en, zn, _ = profiles.values(data, 'old_h', q, 1)
    value = (1-prior)*off + prior*on                          # average forecast, not forecast-at-mean
    zero = zo & zn; value[zero] = 0
    error = eo+en+ep*(abs(on-off)+eo+en)+128*P.EPS*(abs(off)+abs(on)+1)
    error[zero] = 0
    return dict(h=value, eh=error, zero=zero, sat=np.zeros(len(q), dtype=bool),
                w=obs['mass'].sum(axis=1, dtype=P.LD), w_error=obs['l1_error'])


def switch_share(A, B, c):
    """Mass where M0 + one-time cost c says Switch; certified rule copied from population.pair_loss."""
    c = F(c)
    if c < 0:
        raise ValueError('negative switching cost')
    total = P.LD(0)
    for start in range(0, len(A['w']), 512):
        sl = slice(start, start+512)
        gap = A['h'][sl, None] + B['h'][None, :] + P.number(c)
        cert = ((A['zero'][sl, None] & B['zero'][None, :])
                | (A['sat'][sl, None] & B['sat'][None, :]))
        gap = np.where(cert, P.number(c), gap)
        total += (A['w'][sl, None]*B['w'][None, :]*(gap < 0)).sum(dtype=P.LD)
    return float(total)


def build_sides(a, b, kappa, u, h, cache, *, ref=4, K=320):
    """Everything that does not depend on c. Computed once per (a, b, kappa, u, h)."""
    a, b, kappa, u, h = map(F, (a, b, kappa, u, h))
    if min(a, b) < 6 or max(a+u, b+u) >= 10 or u <= 0 or a == b or kappa <= 0 or h <= 0:
        raise ValueError('outside stable asymmetric two-path plant')
    law = {load: cache.get(load, kappa, ref)[:2] for load in (a+u, b, a, b+u)}
    mean = {load: float(lw.mean*P.number(unit)) for load, (unit, lw) in law.items()}
    errors = {load: float(abs(P.number(unit))*lw.mean_error) for load, (unit, lw) in law.items()}
    return dict(a=a, b=b, kappa=kappa, u=u, h=h, x=(b-a)/u,
                r_stay=mean[a+u]+mean[b], r_switch=mean[a]+mean[b+u],
                s_error=errors[a+u]+errors[b]+errors[a]+errors[b+u],
                fresh=(mean_side(a, u, F(0), kappa, h, ref, K, *law[a+u]),
                       mean_side(b, F(0), u, kappa, h, ref, K, *law[b])),
                stale=(stale_mean_side(a, u, F(0), kappa, h, ref, K, *law[a+u]),
                       stale_mean_side(b, F(0), u, kappa, h, ref, K, *law[b])))


def predict(sd, c):
    """H1 sign and approximate size of G_S/C_ref (%) at one-time cost c; H0 sign."""
    c = F(c); h = float(sd['h'])
    if c < 0:
        raise ValueError('negative switching cost')
    s = sd['r_switch'] - sd['r_stay']
    stake = h*s + float(c)                                   # A1: truth acts by sign(h*s + c)
    error = h*sd.get('s_error', 0.)
    if stake == 0 or abs(stake) <= error:
        return dict(status='STATIONARY_STAKE_UNRESOLVED')
    truth_switch = stake < 0
    F_new, F_old = switch_share(*sd['fresh'], c), switch_share(*sd['stale'], c)
    mis_new = 1-F_new if truth_switch else F_new
    mis_old = 1-F_old if truth_switch else F_old
    cref = min(h*sd['r_stay'], h*sd['r_switch'] + float(c))   # A2: |Delta_c| ~ |h*s + c| for every state
    if cref <= 0:
        return dict(status='NONPOSITIVE_STATIONARY_NORMALIZER')
    z = 100*abs(stake)*(mis_old - mis_new)/cref
    return dict(status='PREDICTED', x=float(sd['x']), c=str(c), P=float(sd['h']/sd['kappa']*abs(sd['b']-sd['a'])),
                s=s, s_error=sd.get('s_error', 0.), stake=stake, stake_error=error,
                Cref_H1=cref, c_over_stake=float(c)/abs(h*s) if s else None, truth_switch=bool(truth_switch),
                F_new=F_new, F_old=F_old, z_H1=z, H1=('+' if z > 0 else '-' if z < 0 else '0'),
                H0=h0_sign(sd['x'], sd['u']))


def distribution_checks(sd):
    """Numerical mean/variance diagnostics; not an exact-law certificate."""
    def moments(sides):
        means = [(v['w']*v['h']).sum(dtype=P.LD) for v in sides]
        variance = sum((v['w']*(v['h']-mean)**2).sum(dtype=P.LD)
                       for v, mean in zip(sides, means))
        return float(sum(means)), float(variance)
    fresh, stale = moments(sd['fresh']), moments(sd['stale'])
    return dict(mean_new=fresh[0], mean_old=stale[0], mean_drift=abs(fresh[0]-stale[0]),
                variance_new=fresh[1], variance_old=stale[1])
