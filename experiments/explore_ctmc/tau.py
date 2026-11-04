"""Doan Van Tai — L7.5: telemetry age tau as the only new axis of ctmc-v1 (a = 6) [EXPLORATION ONLY; AI (Claude) theo
ủy quyền]. Spec: experiments/explore_ctmc/SPEC_tau.md.

ctmc.py is not modified. `at_tau(tau)` temporarily rebinds the three names through which the old observation Y enters
ctmc-v1 (ctmc.TAU, ctmc.posterior_mean, ctmc.joint_old_current) to versions with the requested tau, and restores them
on exit. Every other computation (V, the M0 rollout, pair sums, D22 conditioning) is the unchanged v1 code, so at
tau = 1 the numbers are the v1 numbers bit for bit on one machine.

Truth guard: inside at_tau with tau != 1, Chain.V and Chain.V_aug raise PermissionError unless the regime is one of
CONTROL_REGIMES_L75 or results/explore_ctmc/locks_l75.json holds the sha256 of the card on disk.
"""
from contextlib import contextmanager
from fractions import Fraction as F
from functools import partial
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from experiments.explore_ctmc import ctmc

ROOT = Path(__file__).resolve().parents[2]
LOCKS_L75 = ROOT / 'results/explore_ctmc/locks_l75.json'
TAU_REF = F(1)
TAU_GRID = (F(3, 1000), F(1, 100), F(3, 100), F(1, 10), F(3, 10), F(1), F(3), F(10))   # tau / T_int
H_GRID = (F(3, 10), F(1), F(3), F(7), F(15), F(30))                                     # h / T_int
XS_TAU = (F(1, 100), F(1, 10), F(1))                                                     # tau / T_int on the x slice
# (lamA, lamB, u, kappa): truth at tau != 1 is allowed here for controls; excluded from every L7.5 case list
CONTROL_REGIMES_L75 = {'CT1': (F(7), F(13, 2), F(1), F(3, 10)), 'CT2': (F(7), F(29, 4), F(1), F(3, 10))}

_ORIG = dict(TAU=ctmc.TAU, posterior_mean=ctmc.posterior_mean, joint_old_current=ctmc.joint_old_current,
             V=ctmc.Chain.V, V_aug=ctmc.Chain.V_aug)


def l75_unlocked():
    """True when locks_l75.json lists the card and its sha256 still matches the card on disk."""
    if not LOCKS_L75.exists():
        return False
    locks = json.loads(LOCKS_L75.read_text())
    card = LOCKS_L75.parent / locks.get('card', '')
    return card.is_file() and hashlib.sha256(card.read_bytes()).hexdigest() == locks.get('card_sha256')


def is_control(regime):
    return regime is not None and tuple(F(x) for x in regime[:4]) in set(CONTROL_REGIMES_L75.values())


def truth_allowed(tau, regime=None):
    return F(tau) == TAU_REF or is_control(regime) or l75_unlocked()


@contextmanager
def at_tau(tau, regime=None, vmemo=None):
    """Run ctmc-v1 code with the old observation taken tau before t0. `regime` = (lamA, lamB, u, kappa) only matters
    for the truth guard. `vmemo` (a dict) memoizes Chain.V across several tau of one regime; V does not depend on tau."""
    tau = F(tau)
    if tau <= 0:
        raise ValueError('tau must be positive')
    allowed = truth_allowed(tau, regime)
    joints = {}

    def joint(stay, tau_=None):
        if tau_ is not None and F(tau_) != tau:
            raise ValueError('joint_old_current called with a different tau inside at_tau')
        key = (stay.load, stay.kappa, stay.N, F(stay.a))
        if key not in joints:          # same arithmetic as the v1 disk cache stores, but never written to disk
            joints[key] = ctmc._joint_old_current(stay, tau)
        return joints[key]

    def guarded(name):
        f = _ORIG[name]

        def g(self, *args, **kw):
            if not allowed:
                raise PermissionError(f'truth at tau={tau} is refused until locks_l75.json holds the card hash '
                                      '(controls CONTROL_REGIMES_L75 excepted)')
            if name == 'V' and vmemo is not None:
                key = (self.load, self.kappa, self.N, F(self.a), tuple(float(h) for h in args[0]))
                if key not in vmemo:
                    vmemo[key] = f(self, *args, **kw)
                return vmemo[key].copy()
            return f(self, *args, **kw)
        return g
    ctmc.TAU = tau
    ctmc.posterior_mean = partial(_ORIG['posterior_mean'], tau=tau)
    ctmc.joint_old_current = joint
    ctmc.Chain.V, ctmc.Chain.V_aug = guarded('V'), guarded('V_aug')
    try:
        yield
    finally:
        ctmc.TAU = _ORIG['TAU']
        ctmc.posterior_mean = _ORIG['posterior_mean']
        ctmc.joint_old_current = _ORIG['joint_old_current']
        ctmc.Chain.V, ctmc.Chain.V_aug = _ORIG['V'], _ORIG['V_aug']


def restored():
    """Control (d): every rebound name is back to the v1 object."""
    return (ctmc.TAU == _ORIG['TAU'] and ctmc.posterior_mean is _ORIG['posterior_mean']
            and ctmc.joint_old_current is _ORIG['joint_old_current'] and ctmc.Chain.V is _ORIG['V']
            and ctmc.Chain.V_aug is _ORIG['V_aug'])


# ---------------------------------------------------------------- zero fit (no truth)
def evaluate_m0(lamA, lamB, u, kappa, hs, tau, d22=False):
    """ctmc.evaluate_m0 (or evaluate_d22_m0) at telemetry age tau. Never calls V."""
    with at_tau(tau):
        out = (ctmc.evaluate_d22_m0 if d22 else ctmc.evaluate_m0)(lamA, lamB, u, kappa, hs)
    out['tau'] = str(F(tau))
    return out


# ---------------------------------------------------------------- truth (guarded)
def evaluate(lamA, lamB, u, kappa, hs, tau, d22=False, vmemo=None, **kw):
    regime = (lamA, lamB, u, kappa)
    with at_tau(tau, regime, vmemo):
        out = (ctmc.evaluate_d22 if d22 else ctmc.evaluate)(lamA, lamB, u, kappa, hs, **kw)
    out['tau'] = str(F(tau))
    return out


def tint_max(lamA, lamB, u, kappa):
    NA, NB = (ctmc.choose_N(lam + u, kappa) for lam in (lamA, lamB))
    T = {n: ctmc.chain(l, kappa, N).T_int for n, (l, N) in
         dict(A_stay=(lamA + u, NA), A_switch=(lamA, NA), B_stay=(lamB, NB), B_switch=(lamB + u, NB)).items()}
    return max(T.values()), T, NA, NB


def tau_grid_map(case, stage):
    """{tau string: grid multiple} for one case-list entry, exactly as design_l75 built it (tau = rational(m * T_int)).
    A grid tau that rounds to 1 s is a grid point (TB0001: 0.3 T_int = 1 s); the extra reference tau = 1 s is not."""
    from experiments.explore_ctmc.design import rational
    grid = XS_TAU if stage == 'xs' else TAU_GRID
    return {str(rational(m * case['T_int_max'])): float(m) for m in grid}


def q_norm(lamA, lamB, u, kappa):
    """Largest row rate of the Stay generators (sets the cost of e^{Q tau} pushes)."""
    return 2 * (float(max(lamA + u, lamB)) + ctmc.A + ctmc.MU + 1 / float(kappa))


def stationary_posterior_decision(lamA, lamB, u, kappa, h=math.inf):
    """Control (f): the M0 decision when Y carries no information (posterior = stationary law): one Switch share."""
    lamA, lamB, u, kappa = (F(x) for x in (lamA, lamB, u, kappa))
    NA, NB = (ctmc.choose_N(lam + u, kappa) for lam in (lamA, lamB))
    Ast, Bst = ctmc.chain(lamA + u, kappa, NA), ctmc.chain(lamB, kappa, NB)
    dhA = ctmc.m0_gap(lamA, u, kappa, NA, [h], 'A')[0]
    dhB = ctmc.m0_gap(lamB, u, kappa, NB, [h], 'B')[0]
    return float(Ast.pi @ dhA + Bst.pi @ dhB < 0)
