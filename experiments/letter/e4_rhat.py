"""Doan Van Tai — E4 action-rate estimates; no simulation or work on import.

Rates are total mean backlog (Mb), except level iii, which is dimensionless
and is deliberately unavailable to the hybrid magnitude correction.
"""
import numpy as np


def action_statistics(model):
    w = np.asarray(model.weights, dtype=float)
    cap = np.asarray(model.capacity, dtype=float)
    kap = np.asarray(model.kappa, dtype=float)
    if (w.ndim != 3 or cap.shape != (w.shape[1],) or kap.shape != (w.shape[2],)
            or not np.isfinite(w).all() or not np.isfinite(cap).all()
            or not np.isfinite(kap).all() or np.any(w < 0)
            or np.any(cap <= 0) or np.any(kap <= 0)
            or not np.isfinite(model.beta) or model.beta < 0):
        raise ValueError('invalid model statistics')
    mean = w.sum(axis=2)
    variances = (model.beta * w)**2
    variance = variances.sum(axis=2)
    integrated = (variances / (2 * kap)).sum(axis=2)
    correlation = np.divide(integrated, variance, out=np.zeros_like(mean), where=variance > 0)
    return mean, variance, correlation, integrated


def gaussian_rates(model):
    """Level ii: sigma^2 T/(C-mean); kappa is a SWITCHING rate.

    The integrated covariance is sum_j (beta*w_j)^2/(2*kappa_j).
    Zero-variance links contribute zero. Unstable links are flagged; None,
    rather than a finite rate or JSON infinity, denotes an invalid action.
    """
    mean, variance, correlation, integrated = action_statistics(model)
    slack = np.asarray(model.capacity) - mean
    stable = slack > 0
    backlog = np.divide(integrated, slack, out=np.zeros_like(mean), where=stable)
    values = [float(row.sum()) if ok.all() else None for row, ok in zip(backlog, stable)]
    return dict(values=values, units='Mb', link_mean=mean.tolist(),
                link_variance=variance.tolist(), link_T=correlation.tolist(),
                link_backlog=[[float(x) if ok else None for x, ok in zip(row, oks)]
                              for row, oks in zip(backlog, stable)],
                unstable_links=[np.flatnonzero(~ok).tolist() for ok in stable])


def ordering_rates(model):
    """Level iii: dimensionless ordering only; never a hybrid magnitude."""
    mean, _, _, _ = action_statistics(model)
    rho = mean / np.asarray(model.capacity)
    stable = rho < 1
    load_score = np.divide(rho, 1-rho, out=np.zeros_like(rho), where=stable)
    return dict(values=[float(row.sum()) if ok.all() else None
                        for row, ok in zip(load_score, stable)],
                units='dimensionless; tie-break/ordering only', rho=rho.tolist(),
                unstable_links=[np.flatnonzero(~ok).tolist() for ok in stable])


def rate_levels(model, training):
    base = np.array([r['mean'] for r in training['r_a']], dtype=float)
    if base.shape != (len(model.weights),) or not np.isfinite(base).all() or np.any(base < 0):
        raise ValueError('invalid training action rates')
    gaussian, ordering = gaussian_rates(model), ordering_rates(model)
    if any(x is None for x in gaussian['values'] + ordering['values']):
        raise ValueError('nonstationary action in E4 rate estimates')
    levels = dict(i=base, ii=np.array(gaussian['values']), iii=np.array(ordering['values']))
    for label, epsilon in (('noise_m50', -.5), ('noise_m25', -.25),
                           ('noise_p25', .25), ('noise_p50', .5)):
        levels[label] = base[0] + (base-base[0])*(1+epsilon)
    levels['reversed'] = base.max()+base.min()-base
    return levels, dict(ii=gaussian, iii=ordering)


def ordering_comparison(reference, candidate):
    """Exact best-action and weak-order comparisons, including exact ties."""
    ref, other = np.asarray(reference), np.asarray(candidate)
    if ref.ndim != 1 or ref.shape != other.shape:
        raise ValueError('action vectors must match')
    ref_order = np.sign(ref[:, None]-ref[None, :])
    other_order = np.sign(other[:, None]-other[None, :])
    pairs = np.triu_indices(len(ref), 1)
    return dict(reference_best=int(ref.argmin()), candidate_best=int(other.argmin()),
                best_action_agrees=bool(ref.argmin() == other.argmin()),
                best_set_agrees=bool(np.array_equal(ref == ref.min(), other == other.min())),
                full_order_agrees=bool(np.array_equal(ref_order, other_order)),
                pairwise_agreement=float((ref_order[pairs] == other_order[pairs]).mean())
                if len(pairs[0]) else 1.)
