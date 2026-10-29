"""Doan Van Tai — pure design-parameter mappings for L3R.4.

Continuous Markov-fluid formulas are screening references, not exact slotted
queue results or empirical network measurements. No engine or file access here.
"""
import math


def _positive(name, value, *, zero=False):
    value = float(value)
    if not math.isfinite(value) or value < 0 or (value == 0 and not zero):
        raise ValueError(f'{name} must be finite and {"nonnegative" if zero else "positive"}')
    return value


def window_cv(lam, amplitude, mode_time_s, window_s):
    """Stationary CV of mean input rate over a fixed physical window (CTMC)."""
    lam = _positive('lambda', lam)
    a = _positive('amplitude', amplitude, zero=True)
    T, w = _positive('T', mode_time_s), _positive('window', window_s)
    z = 2 * w / T
    if z < 1e-3:
        f = 1 - z / 3 + z * z / 12 - z ** 3 / 60 + z ** 4 / 360 - z ** 5 / 2520
    else:
        f = 2 * (1 + math.expm1(-z) / z) / z
    return a / lam * math.sqrt(f)


def fluid_queue(lam, amplitude, capacity, mode_time_s):
    """Stationary infinite-buffer CTMC fluid queue; virtual time-average delay."""
    lam, c = _positive('lambda', lam), _positive('capacity', capacity)
    a, T = _positive('amplitude', amplitude, zero=True), _positive('T', mode_time_s)
    if lam - a < 0:
        raise ValueError('negative background rate')
    g = c - lam
    if g <= 0:
        raise ValueError('stationary queue requires mean rate below capacity')
    if g >= a:
        return dict(status='ALWAYS_EMPTY', p_busy=0., atom_zero=1., theta_per_packet=None,
                    mean_backlog_packets=0., virtual_delay_time_mean_s=0.)
    p = a / (a + g)
    theta = 2 * g / (T * (a * a - g * g))
    return dict(status='STABLE_MODULATED', p_busy=p, atom_zero=1 - p, theta_per_packet=theta,
                mean_backlog_packets=p / theta, virtual_delay_time_mean_s=p / theta / c)


def delay_exceedance(law, capacity, delay_s):
    """Infinite-buffer stationary tail proxy; never a finite-buffer drop fraction."""
    threshold = _positive('delay threshold', delay_s, zero=True)
    if law['p_busy'] == 0: return 0.
    return law['p_busy'] * math.exp(-law['theta_per_packet'] * capacity * threshold)


def mode_diagnostics(kappa, *, ref=1):
    k = _positive('kappa', kappa)
    if not isinstance(ref, int) or ref < 1: raise ValueError('positive integer ref')
    n = 120 * ref
    flip = -math.expm1(-2 / (n * k)) / 2
    return dict(ctmc_expected_events_in_age=1 / k,
                slotted_expected_boundary_flips_in_age=n * flip,
                mode_correlation_over_age=math.exp(-2 / k))


def implied(lamA, lamB, u, kappa, h_over_tau, *, tau_anchor_s=1., amplitude=6.,
            capacity=10., windows_s=(.001, .01, .1, 1.), buffer_time_s=None,
            actuation_s=None, c_sw_model=0., base_tau_s=1., ref=1):
    """h_over_tau is dimensionless; one physical tau anchor maps the entire row.

    Cost scaling reference: physical capacity/base capacity times time_scale^2.
    c_sw/(capacity*base_tau^2) is a design-only ratio; no Cbar normalization.
    """
    lamA, lamB = _positive('lambdaA', lamA), _positive('lambdaB', lamB)
    u, a = _positive('u', u, zero=True), _positive('amplitude', amplitude, zero=True)
    c, tau, k = _positive('capacity', capacity), _positive('tau', tau_anchor_s), _positive('kappa', kappa)
    hr, basetau = _positive('h/tau', h_over_tau), _positive('base tau', base_tau_s)
    csw = _positive('c_sw', c_sw_model, zero=True)
    if min(lamA, lamB) < a or max(lamA + u, lamB + u) >= c:
        raise ValueError('nonnegative, stable pre/post two-mode family required')
    T = k * tau
    out = dict(rho_A_pre=(lamA + u) / c, rho_A_post=lamA / c,
               rho_B_pre=lamB / c, rho_B_post=(lamB + u) / c,
               amplitude_over_capacity=a / c, phi=u / (c - lamB), eta_label_pilot=u / 2,
               kappa=k, h_over_tau=hr, tau_anchor_s=tau, T_mode_s=T, h_physical_s=hr * tau,
               c_sw_over_capacity_tau2=csw / (c * basetau ** 2),
               **mode_diagnostics(k, ref=ref),
               stationary_reference='continuous Markov fluid; not exact slotted or measured network')
    for label, lam in [('A_pre', lamA + u), ('A_post', lamA), ('B_pre', lamB), ('B_post', lamB + u)]:
        law = fluid_queue(lam, a, c, T)
        values = dict(peak_over_capacity=(lam + a) / c, trough_over_capacity=(lam - a) / c,
                      **law, CV_windows={str(w): window_cv(lam, a, T, w) for w in windows_s})
        if buffer_time_s is not None:
            values['infinite_queue_delay_exceedance_proxy'] = delay_exceedance(law, c, buffer_time_s)
        if label.endswith('post'):
            values['scope'] = 'stationary post-load proxy, not actual transient queue over h'
        out[label] = values
    out['actuation_mode_correlation'] = None if actuation_s is None else math.exp(-2 * _positive('actuation', actuation_s, zero=True) / T)
    out['mode_oracle_structural_flag'] = True
    return out


def endpoint_path(initial_q, rates, managed, capacity, dt):
    """Teaching recurrence only; used to prove homogeneity, no action selection."""
    q = _positive('initial backlog', initial_q, zero=True)
    c, delta = _positive('capacity', capacity), _positive('dt', dt)
    backlog = []
    for rate in rates:
        q = max(0., q + (rate + managed - c) * delta)
        backlog.append(q)
    return backlog
