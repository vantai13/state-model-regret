"""Doan Van Tai — native weighted-idle DP and vectorized conditional mean path.

Shared Side interface with Fraction toy adapter. No grid calls at import time.
Numeric bounds are conservative and conditional on the kernel/input bounds;
dt convergence remains A01. A deterministic zero certificate is never a clamp.
"""
import math
from fractions import Fraction as F

import numpy as np

from smr.gap_screen import backward
from smr.stationary import r2_keep
from experiments.A00_engine.factorial_core import Side
from experiments.A00_engine.cells_adapter import queue_law
from experiments.A00_engine.guard import guard


def _number(x, dtype):
    f = F(x)
    return dtype(str(f.numerator)) / dtype(str(f.denominator))


def side_from_law(unit, mass, *, rates, u_stay, u_switch, capacity, H, dt,
                  keep, keep_error=F(0), D_error=0., extended=True):
    """Rates are packet/s; mass[q_index, current_mode]; unit is packets.

    This low-level physical interface accepts explicit synthetic laws. Callers
    of named grid cells must use side_table/evaluate_cell and their guard.
    """
    if type(H) is not int or H < 1 or dt <= 0 or unit <= 0:
        raise ValueError('positive horizon, dt and queue unit required')
    if len(rates) != 2 or min(*rates, u_stay, u_switch, capacity) < 0:
        raise ValueError('nonnegative two-mode plant required')
    if not 0 <= keep <= 1 or keep_error < 0 or D_error < 0:
        raise ValueError('invalid probability bounds')
    mass = np.asarray(mass, dtype=np.longdouble)
    if mass.ndim != 2 or mass.shape[1] != 2 or np.any(mass < 0) or not np.all(np.isfinite(mass)):
        raise ValueError('law must have two finite nonnegative mode columns')
    if abs(mass.sum(dtype=np.longdouble) - 1) > 1e-12:
        raise ValueError('law must sum to one')
    dtype = np.longdouble if extended else np.float64
    eps = np.finfo(dtype).eps
    amounts = [(r + u - capacity) * dt for r in rates for u in (u_stay, u_switch)] + [unit]
    denominator = math.lcm(*(F(x).denominator for x in amounts))
    quantum = F(math.gcd(*(int(x * denominator) for x in amounts)), denominator)
    support_q, modes = np.nonzero(mass)
    qs = np.unique(support_q)
    factor = unit / quantum
    if factor.denominator != 1:
        raise ValueError('law and action lattices must align')
    indices = qs.astype(np.int64) * int(factor)
    p = _number(keep, dtype)
    # |p_float - p_true| includes supplied R2 approximation error.
    pe = abs(F(str(p)) - keep) + keep_error + F(str(2 * eps))
    dtf, scale = _number(dt, dtype), _number(quantum * dt, dtype)
    q0 = np.repeat(qs.astype(dtype)[:, None], 2, axis=1) * _number(unit, dtype)
    weights = H - np.arange(H, dtype=dtype)
    mean = _number(sum(rates) / 2, dtype)
    amplitude = _number((rates[1] - rates[0]) / 2, dtype)
    r = 2 * p - 1
    mu = mean + np.power(r, np.arange(H, dtype=dtype))[:, None] * np.array([-amplitude, amplitude], dtype=dtype)
    W1, W0, J, errs, mean_errs, busy = {}, {}, {}, {}, {}, {}
    net_by_action = {}
    qbound = np.max(abs(q0)) + H * max(_number(abs(x), dtype) for x in amounts)
    gamma = (64 * H * eps) / (1 - 64 * H * eps)
    if 64 * H * eps >= .01:
        raise ArithmeticError('mean-path roundoff bound invalid')
    arrival_error = 2 * abs(amplitude) * np.arange(H, dtype=dtype) * _number(pe, dtype) * dtf
    merror = dtf * (np.sum(weights * arrival_error) + gamma * H * (qbound + 1))
    for action, managed in (('St', u_stay), ('Sw', u_switch)):
        increments = tuple(int((rate + managed - capacity) * dt / quantum) for rate in rates)
        net_by_action[action] = increments
        raw, error, _ = backward(indices, increments, H, keep, keep_error, extended)
        W1[action] = raw * scale
        errs[action] = error * abs(scale) + 8 * eps * abs(scale) * max(dtype(1), np.max(abs(raw)))
        q, total = q0.copy(), np.zeros_like(q0)
        linear_q, minimum_linear = q0.copy(), np.full_like(q0, np.inf)
        managed_f = _number(managed, dtype)
        for k in range(H):
            net = (mu[k] + managed_f - _number(capacity, dtype)) * dtf
            linear_q += net
            minimum_linear = np.minimum(minimum_linear, linear_q)
            # Compute idle from pre-update q. The lesson pseudocode reversed these.
            idle = np.maximum(0, -q - net)
            total += (H - k) * idle
            q = np.maximum(0, q + net)
        W0[action] = dtf * total
        q_error = np.sum(arrival_error) + gamma * H * (qbound + 1)
        busy[action] = minimum_linear > q_error
        mean_errs[action] = merror
        linear = dtf * (H * q0 + np.sum(weights[:, None] *
                         (mu + managed_f - _number(capacity, dtype)) * dtf, axis=0))
        J[action] = linear + W1[action]
        if np.any(W0[action] - W1[action] > merror + errs[action]):
            raise ArithmeticError('Jensen bound violated')
    d = W1['Sw'] - W1['St']
    dh = W0['Sw'] - W0['St']
    # Saturation is another symbolic identity, not an epsilon/clamp: if both
    # actions empty the queue at every endpoint, their idle difference is the
    # same closed-form triangular managed-load term on either queue. Computing
    # two idle totals independently can otherwise turn an exact A+B tie into a
    # small negative gap and a macroscopic wrong-action cost (A01 N01).
    max_managed = max(u_stay, u_switch)
    first = tuple(int((rate + max_managed - capacity) * dt / quantum) for rate in rates)
    full_idle = np.column_stack([(indices + a <= 0) & (max(rates) + max_managed <= capacity)
                                 for a in first])
    # For nonnegative R2 correlation, conditional mean approaches the stationary
    # mean monotonically; otherwise max(rates) is a valid conservative envelope.
    envelope = tuple(max(rate, sum(rates) / 2) if keep >= F(1, 2) else max(rates) for rate in rates)
    mean_idle = np.column_stack([(indices + a <= 0) & (upper + max_managed <= capacity)
                                 for a, upper in zip(first, envelope)])
    saturation = (u_stay - u_switch) * dt * dt * H * (H + 1) / 2
    d[full_idle] = _number(saturation, dtype)
    dh[mean_idle] = _number(saturation, dtype)
    mean_zero = busy['St'] & busy['Sw']
    dh[mean_zero] = 0  # proved no idle in either conditional mean path
    minimum_action = 'Sw' if u_switch < u_stay else 'St'
    inc = net_by_action[minimum_action]
    zero = np.column_stack([(indices + a >= 0) & (indices + a + (H - 1) * min(0, *inc) >= 0)
                            for a in inc])
    if u_stay == u_switch:
        zero[:] = True  # identical actions are another exact certificate
    mean_zero |= zero
    if np.any(d[zero] != 0) or np.any(dh[zero] != 0):
        raise ArithmeticError('conservation certificate violated: exact zero required')
    row_lookup = {int(q): i for i, q in enumerate(qs)}
    rows = np.array([row_lookup[int(q)] for q in support_q])
    select = rows, modes
    d_error = errs['St'] + errs['Sw'] + 8 * eps * max(dtype(1), np.max(abs(d)))
    dh_error = 2 * merror + 8 * eps * max(dtype(1), np.max(abs(dh)))
    j_error = errs['St'] + merror + gamma * max(dtype(1), np.max(abs(J['St'])), qbound * H * dtf)
    bounds = dict(d=d_error, dh=dh_error, jst=j_error,
                  D_l1=2 * D_error + float(abs(mass.sum(dtype=np.longdouble) - 1)),
                  zero=tuple(bool(x) for x in zero[select]),
                  zero_dh=tuple(bool(x) for x in mean_zero[select]),
                  saturated_d=tuple(bool(x) for x in full_idle[select]),
                  saturated_dh=tuple(bool(x) for x in mean_idle[select]),
                  saturation=saturation)
    table = Side(tuple(mass[support_q, modes]), tuple(d[select]), tuple(dh[select]),
                 tuple(J['St'][select]), tuple(F(int(q)) * unit for q in support_q), bounds)
    table.check('A' if u_switch <= u_stay else 'B')
    detail = dict(W1={k: tuple(v[select]) for k, v in W1.items()},
                  W0={k: tuple(v[select]) for k, v in W0.items()},
                  Jsw=tuple(J['Sw'][select]), true_idle_error={k: float(v) for k, v in errs.items()},
                  mean_idle_error=float(merror), unit=quantum)
    return table, detail


def side_table(cell, which, ref, *, extended=True, **authorization):
    receipt = guard(cell['id'], **authorization)
    unit, mass, support, error = queue_law(cell, which, ref)
    dt = F(1, 120 * ref)
    keep, ke = r2_keep(dt, cell['kappa'])
    table, detail = side_from_law(unit, mass, rates=cell['rates' + which],
                                  u_stay=cell['u'] if which == 'A' else F(0),
                                  u_switch=cell['u'] if which == 'B' else F(0), capacity=F(10),
                                  H=cell['H_coarse'] * ref, dt=dt, keep=keep, keep_error=ke,
                                  D_error=error, extended=extended)
    detail.update(provenance=receipt, refinement=ref)
    return table, detail
