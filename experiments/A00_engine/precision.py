"""Doan Van Tai — numerical enclosures, separate from dt convergence and CI.

Enclosures are conditional on the supplied per-state and L1 probability bounds.
Sorting changes no numeric values; prefix sums use long double with an explicit
conservative operation-count allowance. No probability product table is built.
"""
import numpy as np
from numbers import Rational

from experiments.A00_engine.factorial_core import Side, _abs_quantile, _by_backlog

LD = np.longdouble
EPS = np.finfo(LD).eps


def array(x):
    def convert(v):
        return LD(str(v.numerator)) / LD(str(v.denominator)) if isinstance(v, Rational) else LD(v)
    if np.isscalar(x) or isinstance(x, Rational):
        return np.asarray(convert(x), dtype=LD)
    return np.asarray([convert(v) for v in x], dtype=LD)


def arithmetic(A, B, scale=1):
    n = 256 * (len(A.p) + len(B.p) + 16)
    if n * EPS >= .01:
        raise ArithmeticError('aggregation roundoff budget invalid')
    return LD(n * EPS / (1 - n * EPS)) * max(LD(1), LD(scale))


def radii(s, key):
    value = (s.bounds or {}).get(key, 0)
    result = np.broadcast_to(array(value), (len(s.p),))
    if np.any(result < 0) or not np.all(np.isfinite(result)):
        raise ValueError('nonnegative finite radii required')
    result = result + 2 * EPS * abs(array(getattr(s, key)))
    if key in ('d', 'dh'):
        zero = np.asarray((s.bounds or {}).get('zero_' + key, (s.bounds or {}).get('zero', [False] * len(s.p))), dtype=bool)
        if np.any(array(getattr(s, key))[zero] != 0):
            raise ArithmeticError('invalid zero certificate')
        result[zero] = 0
    return result


def key_interval(s, key, which):
    values, error = array(getattr(s, key)), radii(s, key)
    lo = np.nextafter(values - error, -np.inf)
    hi = np.nextafter(values + error, np.inf)
    if which == 'A':
        lo, hi = np.maximum(0, lo), np.maximum(0, hi)
    else:
        lo, hi = np.minimum(0, lo), np.minimum(0, hi)
    zero = np.asarray((s.bounds or {}).get('zero_' + key, (s.bounds or {}).get('zero', [False] * len(values))), dtype=bool)
    if np.any(values[zero] != 0):
        raise ArithmeticError('false structural zero certificate')
    lo[zero] = hi[zero] = 0
    return lo, hi


def _cut(ka, va, pa, kb, vb, pb):
    order = np.argsort(kb, kind='stable')
    cp = np.r_[LD(0), np.cumsum(pb[order], dtype=LD)]
    cv = np.r_[LD(0), np.cumsum(pb[order] * vb[order], dtype=LD)]
    index = np.searchsorted(kb[order], -ka, side='left')
    return (np.sum(pa * cp[index], dtype=LD),
            np.sum(pa * (va * cp[index] + cv[index]), dtype=LD))


def bounded_cut(A, B, key='dh'):
    alo, ahi = key_interval(A, key, 'A')
    blo, bhi = key_interval(B, key, 'B')
    pa, pb, da, db = map(array, (A.p, B.p, A.d, B.d))
    nominal_mass, value = _cut(array(getattr(A, key)), da, pa, array(getattr(B, key)), db, pb)
    certain, _ = _cut(ahi, da, pa, bhi, db, pb)
    possible, _ = _cut(alo, da, pa, blo, db, pb)
    _, abs_certain = _cut(ahi, abs(da), pa, bhi, abs(db), pb)
    _, abs_possible = _cut(alo, abs(da), pa, blo, abs(db), pb)
    # Paired saturation certificates are exact symbolic ties. Their common
    # managed-load cap cancels algebraically, even though individual rounded
    # caps have error intervals. Such pairs choose Stay, not unresolved.
    ba, bb = A.bounds or {}, B.bounds or {}
    ca, cb = ba.get('saturation'), bb.get('saturation')
    if ca is not None and cb is not None and ca != 0 and ca + cb == 0:
        sa = np.asarray(ba.get('saturated_' + key, [False] * len(pa)))
        sb = np.asarray(bb.get('saturated_' + key, [False] * len(pb)))
        if np.any(sa) and np.any(sb):
            if not (np.all(abs(array(getattr(A, key))[sa] - array(ca)) <= radii(A, key)[sa]) and
                    np.all(abs(array(getattr(B, key))[sb] - array(cb)) <= radii(B, key)[sb])):
                raise ArithmeticError('invalid paired saturation certificate')
            possible -= sum(pa[sa]) * sum(pb[sb])
            abs_possible -= sum(pa[sa] * abs(da[sa])) * sum(pb[sb]) + sum(pb[sb] * abs(db[sb])) * sum(pa[sa])
    scale = max(abs(da), default=0) + max(abs(db), default=0)
    rounding = arithmetic(A, B, scale)
    # The nonnegative clamp enlarges an error bound; it never changes a gap/action.
    return dict(value=value, nominal_mass=nominal_mass,
                certain_mass=certain, possible_mass=possible,
                unresolved_mass=max(LD(0), possible - certain),
                impact=max(LD(0), abs_possible - abs_certain) + rounding,
                arithmetic_bound=rounding)


def cut_with_bound(A_key, A_val, A_p, B_key, B_val, B_p, e_key):
    """Lesson §10 diagnostic kernel; no assumption about component signs.

    e_key bounds the sum of the two key errors. Unlike the supplied snippet,
    the return includes an arithmetic allowance (fourth value).
    """
    ak, av, ap, bk, bv, bp = map(array, (A_key, A_val, A_p, B_key, B_val, B_p))
    _, value = _cut(ak, av, ap, bk, bv, bp)
    certain, ca = _cut(ak + e_key, abs(av), ap, bk, abs(bv), bp)
    possible, aa = _cut(ak - e_key, abs(av), ap, bk, abs(bv), bp)
    rnd = 256 * (len(ak) + len(bk) + 16) * EPS * max(LD(1), max(abs(av)) + max(abs(bv)))
    return value, max(LD(0), possible - certain), max(LD(0), aa - ca), rnd


def group_side(s):
    p, d, dh = _by_backlog(s)
    grouped = {}
    for i, g in enumerate(s.group):
        grouped.setdefault(g, []).append(i)
    errors = {k: [] for k in ('d', 'dh')}
    de = LD((s.bounds or {}).get('D_l1', 0))
    probabilities = array(s.p)
    for k in errors:
        values, r = array(getattr(s, k)), radii(s, k)
        maximum = max(abs(values) + r)
        for indices in grouped.values():
            P = sum(probabilities[i] for i in indices)
            if P <= de:
                bound = 2 * maximum
            else:
                bound = sum(probabilities[i] * r[i] for i in indices) / P + 2 * de * maximum / (P - de)
            errors[k].append(bound + 64 * len(indices) * EPS * max(LD(1), maximum))
    zero = [all((s.bounds or {}).get('zero', [False] * len(s.p))[i] for i in ix)
            for ix in grouped.values()]
    zero_dh = [all((s.bounds or {}).get('zero_dh', (s.bounds or {}).get('zero', [False] * len(s.p)))[i] for i in ix)
               for ix in grouped.values()]
    return Side(p, d, dh, (LD(0),) * len(p), tuple(grouped),
                dict(**errors, zero=zero, zero_dh=zero_dh, D_l1=de))


def enclose(A, B, nominal):
    """Return per-quantity bounds; unresolved M0 actions are never final labels."""
    dp = [LD((s.bounds or {}).get('D_l1', 0)) for s in (A, B)]
    if any(not np.isfinite(e) or not 0 <= e <= 2 for e in dp):
        raise ValueError('invalid L1 probability bound')
    dprob = sum(dp) + dp[0] * dp[1]
    def mean_error(key):
        if key in ('d', 'dh') and all(all((s.bounds or {}).get('zero_' + key, (s.bounds or {}).get('zero', [False] * len(s.p)))) for s in (A, B)):
            return LD(0)  # expectation of certified zeros is exactly zero
        return sum(np.sum(array(s.p) * radii(s, key), dtype=LD) +
                   LD((s.bounds or {}).get('D_l1', 0)) * max(abs(array(getattr(s, key))) + radii(s, key))
                   for s in (A, B)) + arithmetic(A, B, sum(max(abs(array(getattr(s, key)))) for s in (A, B)))
    ek, ed, eh = (mean_error(k) for k in ('jst', 'd', 'dh'))
    oracle, model = bounded_cut(A, B, 'd'), bounded_cut(A, B, 'dh')
    groupedA, groupedB = group_side(A), group_side(B)
    cb = bounded_cut(groupedA, groupedB, 'dh')
    def cut_value_error(a, b):
        ra, rb = radii(a, 'd'), radii(b, 'd')
        pa, pb = array(a.p), array(b.p)
        value_bound = max(abs(array(a.d)) + ra) + max(abs(array(b.d)) + rb)
        return (sum(pa * ra) * sum(pb) + sum(pb * rb) * sum(pa) +
                dprob * value_bound + arithmetic(a, b, value_bound))
    ec = cut_value_error(A, B)
    ecb = cut_value_error(groupedA, groupedB)
    K = sum(np.sum(array(s.p) * array(s.jst), dtype=LD) for s in (A, B))
    eg = LD(nominal['E_delta'])
    eg_hat = LD(nominal['E_delta_hat'])
    if eg_hat - eh >= 0:
        actions = [0]
    elif eg_hat + eh < 0:
        actions = [1]
    else:
        actions = [0, 1]
    alternatives = [(K - ek + a * (eg - ed), K + ek + a * (eg + ed)) for a in actions]
    Lerr = {'00': max(abs(LD(nominal['L']['00']) - x) for interval in alternatives for x in interval),
            '01': ek + ed, '11': ek + ec,
            '10': ek + ec + model['impact'], 'cb0': ek + ecb + cb['impact']}
    pairs = {'G_S': ('00', '10'), 'G_M': ('00', '01'), 'G_SM': ('00', '11'),
             'G_S_M1': ('01', '11'), 'G_M_S1': ('10', '11'), 'F': ('00', 'cb0'), 'V': ('cb0', '10')}
    errors = {f'L{k}': v for k, v in Lerr.items()}
    errors.update({f'R{k}': (LD(0) if k == '11' else v + Lerr['11']) for k, v in Lerr.items()})
    errors.update({k: Lerr[i] + Lerr[j] for k, (i, j) in pairs.items()})
    errors['Gamma'] = sum(Lerr[k] for k in ('00', '01', '10', '11'))
    maxI = sum(max(abs(array(s.dh) - array(s.d))) for s in (A, B)) + abs(LD(nominal['bias']))
    errors.update(E_delta=ed, E_delta_hat=eh, bias=ed + eh, E_pos=ed + ec, E_neg=ec,
                  C_ref=Lerr['11'], E_abs_I_delta=2 * (ed + eh) + dprob * maxI,
                  E_abs_e_M=ed + eh + dprob * sum(max(abs(array(s.dh) - array(s.d))) for s in (A, B)))
    p_low = max(LD(0), oracle['certain_mass'] - dprob - arithmetic(A, B))
    p_high = min(LD(1), oracle['possible_mass'] + dprob + arithmetic(A, B))
    errors['p_sw'] = max(LD(nominal['p_sw']) - p_low, p_high - LD(nominal['p_sw']))
    intervals = {}
    for name, e in errors.items():
        center = (nominal['L'][name[1:]] if name.startswith('L') else
                  nominal['R'][name[1:]] if name.startswith('R') else nominal.get(name, nominal['G'].get(name)))
        if center is None:
            raise KeyError(name)
        center = LD(center)
        intervals[name] = [np.nextafter(float(center - e), -np.inf), np.nextafter(float(center + e), np.inf)]
    intervals['p_sw'] = [max(0., float(p_low)), min(1., float(p_high))]
    intervals['R11'] = [0., 0.]
    quantile_intervals = {}
    for name, va, vb, shift in (
            ('abs_delta', A.d, B.d, max(radii(A, 'd')) + max(radii(B, 'd'))),
            ('abs_I_delta', tuple(h - d - nominal['bias'] for h, d in zip(A.dh, A.d)),
             tuple(h - d for h, d in zip(B.dh, B.d)),
             sum(max(radii(s, 'dh') + radii(s, 'd')) for s in (A, B)) + ed + eh)):
        quantile_intervals[name] = {}
        va, vb = tuple(array(va)), tuple(array(vb))
        pa, pb = tuple(array(A.p)), tuple(array(B.p))
        for label in nominal['quantiles_' + name]:
            numerator, denominator = label.split('/')
            level = LD(numerator) / LD(denominator)
            cdf_error = dprob + arithmetic(A, B)
            pl, ph = max(LD(0), level - cdf_error), min(LD(1), level + cdf_error)
            low = LD(0) if pl <= 0 else LD(_abs_quantile(va, pa, vb, pb, pl))
            high = (max(abs(min(va) + min(vb)), abs(max(va) + max(vb))) if ph >= 1
                    else _abs_quantile(va, pa, vb, pb, ph))
            quantile_intervals[name][label] = [max(0., np.nextafter(float(low - shift), -np.inf)),
                                               np.nextafter(float(high + shift), np.inf)]
    uncertain = {'oracle': float(oracle['unresolved_mass']), 'M0': float(model['unresolved_mass']),
                 'D22': float(cb['unresolved_mass'])}
    return dict(e_num={k: float(v) for k, v in errors.items()}, intervals=intervals,
                unresolved_mass=uncertain,
                unresolved_impact={'M0': float(model['impact']), 'D22': float(cb['impact'])},
                L00_alternatives=[[float(x) for x in r] for r in alternatives],
                a00=actions[0] if len(actions) == 1 else None,
                a01=0 if eg - ed >= 0 else 1 if eg + ed < 0 else None,
                aggregation_error=float(arithmetic(A, B)), probability_L1_bound=float(dprob),
                quantile_intervals=quantile_intervals,
                bound_scope='slot-model numeric enclosure conditional on input bounds; not CI or dt error')
