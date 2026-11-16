"""Doan Van Tai — independent W2 MMPP/M/1 stationary-mean solver.

The sparse generator/solve accepts continuous amplitudes.  The old CTMC's
truncation selector is reused only where its amplitude namespace permits it.
No change to, or monkey patch of, the CTMC implementation is made.
"""
from dataclasses import asdict, dataclass
import math

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve


@dataclass(frozen=True)
class StationaryMean:
    r: float
    N: int
    tail: float
    residual: float
    min_probability: float
    truncation: str

    def record(self):
        return asdict(self)


def _validate(load, kappa, alpha, mu):
    if not all(math.isfinite(v) for v in (load, kappa, alpha, mu)):
        raise ValueError('MMPP parameters must be finite')
    if not (0 <= alpha <= load < mu and kappa > 0 and mu > 0):
        raise ValueError('need 0 <= alpha <= load < mu and kappa > 0')


def generator(load, kappa, N, alpha, mu=10.):
    load, kappa, alpha, mu = map(float, (load, kappa, alpha, mu))
    _validate(load, kappa, alpha, mu)
    if int(N) != N or N < 1:
        raise ValueError('N must be a positive integer')
    states = np.arange(2 * (int(N) + 1))
    levels, modes = states // 2, states % 2
    birth = load + alpha * (2 * modes - 1)
    up, down = levels < N, levels > 0
    row = np.r_[states[up], states[down], states]
    col = np.r_[states[up] + 2, states[down] - 2, states ^ 1]
    rate = np.r_[birth[up], np.full(down.sum(), mu),
                 np.full(states.size, 1 / kappa)]
    Q = sparse.csr_matrix((rate, (row, col)), shape=(states.size, states.size))
    return Q - sparse.diags(np.asarray(Q.sum(axis=1)).ravel())


def _geometric_tail(load, kappa, alpha, mu):
    """Two-phase QBD logarithmic reduction; same tail convention as choose_N.

    tail(N) bounds P(backlog >= N) in the infinite chain, rather than relying
    on the (artificially blocked) last-level mass in the finite generator.
    """
    if alpha == 0:
        rho = load / mu
        return lambda N: rho ** int(N)
    I = np.eye(2)
    arrivals = np.diag([load - alpha, load + alpha])
    services = mu * I
    q = 1 / kappa
    middle = np.array([[-(load-alpha+mu+q), q],
                       [q, -(load+alpha+mu+q)]])
    inverse = np.linalg.inv(-middle)
    H, L = inverse @ arrivals, inverse @ services
    G, T = L.copy(), H.copy()
    for _ in range(200):
        inverse = np.linalg.inv(I - H @ L - L @ H)
        H, L = inverse @ H @ H, inverse @ L @ L
        G, T = G + T @ L, T @ H
        if np.abs(T).max() < 1e-30:
            break
    if np.abs(G.sum(axis=1) - 1).max() > 1e-10:
        raise ArithmeticError('QBD reduction did not converge')
    R = arrivals @ np.linalg.inv(-(middle + arrivals @ G))
    pi0 = np.linalg.svd((middle + services + R @ services).T)[2][-1]
    S = np.linalg.inv(I - R)
    pi0 /= pi0 @ S @ np.ones(2)

    def tail(N):
        value = float(pi0 @ np.linalg.matrix_power(R, int(N)) @ S @ np.ones(2))
        if not math.isfinite(value) or value < -1e-12:
            raise ArithmeticError('invalid QBD tail')
        return max(0., value)
    return tail


def choose_N(load, kappa, alpha, mu=10., tol=1e-13):
    load, kappa, alpha, mu = map(float, (load, kappa, alpha, mu))
    _validate(load, kappa, alpha, mu)
    if not 0 < tol < 1:
        raise ValueError('tail tolerance must be in (0,1)')
    tail = _geometric_tail(load, kappa, alpha, mu)
    # Reuse the existing selector where it is defined, but certify the tail
    # with the continuous-amplitude calculation above in either case.
    if mu == 10. and alpha in (0., 3., 6., 7.5):
        from experiments.explore_ctmc import ctmc
        N = ctmc.choose_N(load, kappa, tol=tol, a=alpha)
        if tail(N) <= tol:
            return N, tail(N), 'ctmc.choose_N + independent QBD tail'
    lo, hi = 0, 1
    while tail(hi) > tol:
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if tail(mid) > tol:
            lo = mid
        else:
            hi = mid
    N = max(40, math.ceil(1.2 * hi))
    return N, tail(N), 'continuous-amplitude QBD tail'


def stationary_mean(load, kappa, alpha, mu=10., N=None, tol=1e-13):
    """Return the truncated sparse stationary mean and truncation diagnostics.

    An explicit N is useful for exact like-for-like validation.  Its measured
    infinite-chain tail is still reported; automatic N always meets tol.
    """
    load, kappa, alpha, mu = map(float, (load, kappa, alpha, mu))
    _validate(load, kappa, alpha, mu)
    if N is None:
        N, tail, method = choose_N(load, kappa, alpha, mu, tol)
    else:
        if int(N) != N or N < 1:
            raise ValueError('N must be a positive integer')
        N = int(N)
        tail, method = _geometric_tail(load, kappa, alpha, mu)(N), 'explicit N'
    Q = generator(load, kappa, N, alpha, mu)
    # Fix pi[0] = 1 before normalization.  This uses a separate sparse solve
    # and independently assembled generator, not Chain.r or Chain.pi.
    QT = Q.T.tocsc()
    rest = spsolve(QT[1:, 1:], -QT[1:, 0].toarray().ravel())
    pi = np.r_[1., rest]
    pi /= pi.sum()
    residual = float(np.max(np.abs(pi @ Q)))
    if not np.isfinite(pi).all() or pi.min() < -1e-12 or residual > 1e-9:
        raise ArithmeticError('invalid sparse stationary solution')
    r = float(pi @ np.repeat(np.arange(N + 1), 2))
    return StationaryMean(r, N, tail, residual, float(pi.min()), method)
