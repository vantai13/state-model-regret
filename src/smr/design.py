"""Doan Van Tai — L1.8C design diagnostics; no action values or contrasts.

The stationary prior is for a reflected discrete queue with increments -2/+1
and a symmetric mode transition. It is NOT a fluid stationary approximation.
"""
import math
from fractions import Fraction as F
from itertools import product

import numpy as np


def can_idle(q0, arrivals, capacity):
    if q0 < 0 or capacity < 0:
        raise ValueError('nonnegative queue and capacity required')
    q = q0
    for a in arrivals:
        if a < 0:
            raise ValueError('negative arrivals')
        if q + a < capacity:
            return True
        q = max(0, q + a - capacity)
    return False


def stationary_parameters(keep):
    """Closed-form normalized infinite stationary law; q is an integer index.

    pi(q,off)=A*r**q, pi(q,on)=A*r*(1+r)*r**q for q>=1.
    At q=0: pi(0,off)=A*s*r*(1+r)/(1-s), pi(0,on)=A*r*(1+r).
    r solves s*r*r+(1-s)*r-s=0. No finite-tail renormalization.
    """
    if not math.isfinite(keep) or not .5 <= keep < 1:
        raise ValueError('irreducible symmetric R2 requires .5 <= keep < 1')
    r = 2*keep / (math.hypot(1-keep, 2*keep) + 1-keep)
    b = r*(1+r)
    A = 1 / (b/(1-keep) + (1+b)*r/(1-r))
    return r, A


def stationary_mass(q, mode, keep):
    if type(q) is not int or q < 0 or mode not in (0, 1):
        raise ValueError('q nonnegative integer; mode 0=off,1=on')
    r, A = stationary_parameters(keep)
    b = r*(1+r)
    if q == 0:
        return A*b*(keep/(1-keep) if mode == 0 else 1)
    return A*r**q*(b if mode == 1 else 1)


def conditional_on(q, keep):
    if type(q) is not int or q < 0:
        raise ValueError('observation must belong to the stationary queue lattice')
    r, _ = stationary_parameters(keep)
    b = r*(1+r)
    return 1-keep if q == 0 else b/(1+b)


def stationary_total(keep):
    r, A = stationary_parameters(keep)
    return sum(stationary_mass(0, mode, keep) for mode in (0, 1)) + A*(1+r+r*r)*r/(1-r)


def design_cells():
    """Proposed physical profile; adoption state is recorded in the manifest."""
    cells = []
    for i, (z, kappa, eta) in enumerate(product((F(1,3), F(1), F(3), F(10)),
                                               (F(3,10), F(1), F(3)),
                                               (F(1,2), F(9,10))), 1):
        cells.append(dict(id=f'M{i:02}', role='main', z=z, kappa=kappa, eta=eta,
                          yA=2*z, yB=2*z, age=F(1), horizon=z/(1-eta)))
    for i, (kappa, eta, horizon) in enumerate(((F(3,10), F(1,2), F(1,2)),
                                              (F(3), F(9,10), F(1))), 1):
        cells.append(dict(id=f'N{i:02}', role='negative_control', z=F(50), kappa=kappa,
                          eta=eta, yA=F(100), yB=F(100), age=F(1), horizon=horizon))
    for i, (z, kappa) in enumerate(((F(1), F(3,10)), (F(3), F(3))), 1):
        cells.append(dict(id=f'S{i:02}', role='stress', z=z, kappa=kappa, eta=F(3,2),
                          yA=2*z, yB=2*z, age=F(1), horizon=z))
    return cells


def reserved_coordinates():
    # Coordinates only. Do not build D, costs, or diagnostics on the reserve.
    return [dict(z=z, kappa=k, eta=e,
                 role='extrapolation' if z == 30 else 'held_out')
            for z, k, e in product((F(3,5), F(2), F(5), F(30)),
                                    (F(3,5), F(2)), (F(1,2), F(9,10)))]


def episode_law(cell, refinement=1):
    """Finite propagation from a stationary conditional prior under pre-Stay.

    Returns qA (packets), qB quantum, mass[qB_index, current_mode], dt, keep.
    Evaluator and observation-only estimator call this law separately.
    """
    if type(refinement) is not int or refinement < 1:
        raise ValueError('positive integer refinement required')
    dt = F(1, 120*refinement)
    tau = cell['age']/dt
    initial = cell['yB']/(4*dt)
    if tau.denominator != 1 or initial.denominator != 1:
        raise ValueError('age and observation must lie on the declared lattice')
    keep = (1+math.exp(-2*float(dt/cell['kappa'])))/2
    prior = conditional_on(int(initial), keep)
    size = int(initial)+int(tau)+1
    mass = np.zeros((size, 2))
    mass[int(initial)] = (1-prior, prior)
    for _ in range(int(tau)):
        following = np.zeros_like(mass)
        for mode, increment in ((0, -2), (1, 1)):
            indices = np.maximum(0, np.arange(size)+increment)
            active = np.flatnonzero(mass[:, mode])
            for next_mode, chance in ((mode, keep), (1-mode, 1-keep)):
                np.add.at(following[:, next_mode], indices[active], mass[active, mode]*chance)
        mass = following
    qa = max(F(0), cell['yA'] + (F(5)+2*cell['eta']-10)*cell['age'])
    return qa, 4*dt, mass, dt, keep


def diagnostic(cell, refinement=1, time_scale=F(1), rate_scale=F(1)):
    """Only conservation mass, timescale ratios, and analytic budget estimates."""
    qa, quantum, mass, dt, keep = episode_law(cell, refinement)
    H = cell['horizon']/dt
    if H.denominator != 1:
        raise ValueError('horizon must be aligned, never silently rounded')
    H = int(H)
    u = 2*cell['eta']
    # rates*dt and backlogs both scale by rate_scale*time_scale.
    scale = rate_scale*time_scale
    no_idle = 0.0
    for q, mode in zip(*np.nonzero(mass)):
        idle = False
        for switch in (False, True):
            a = (5+(0 if switch else u))*dt*scale
            b0 = ((14 if mode else 2)+(u if switch else 0))*dt*scale
            bmin = (2+(u if switch else 0))*dt*scale
            # Constant minimum path: strict last-slot test is equivalent to rollout.
            def constant_tail_idle(start, first, tail):
                c = 10*dt*scale
                if start+first < c:
                    return True
                after = max(0, start+first-c)
                return H > 1 and tail < c and after+(H-1)*(tail-c) < 0
            idle |= constant_tail_idle(qa*scale, a, a)
            idle |= constant_tail_idle(F(int(q))*quantum*scale, b0, bmin)
        if not idle:
            no_idle += mass[q, mode]
    # Dense rational-lattice upper bound, including prehistory and BOTH actions.
    increments = [(rate + managed-10)*dt for managed in (F(0),u) for rate in (F(2), F(14))]
    denominator = math.lcm(*(v.denominator for v in increments), quantum.denominator)
    numerators = [int(v*denominator) for v in increments] + [int(quantum*denominator)]
    lattice = F(math.gcd(*numerators), denominator)
    maxq = F(len(mass)-1)*quantum
    max_growth = max(F(0), *increments)
    max_domain = int((maxq + H*max_growth)/lattice)+1
    updates = 4*H*max_domain  # conservative, two actions x two modes
    return dict(cell=cell['id'], role=cell['role'], states=int(np.count_nonzero(mass)),
                total_mass=float(mass.sum()), stationary_total=stationary_total(keep),
                prior_on=conditional_on(int(cell['yB']/quantum), keep),
                s_bt=no_idle, dt_s=float(dt*time_scale), H=H,
                z=float(cell['z']), kappa=float(cell['kappa']), eta=float(cell['eta']),
                horizon_s=float(cell['horizon']*time_scale), dt_over_Tmode=float(dt/cell['kappa']),
                dt_over_drain_pre=float(dt/cell['z']),
                h_over_drain_post=None if cell['eta'] >= 1 else float(cell['horizon']*(1-cell['eta'])/cell['z']),
                max_dense_states=max_domain*2, upper_scalar_updates=updates,
                estimated_peak_bytes=max_domain*2*8*3,
                budget_kind='conservative operation/memory estimate; not measured runtime')
