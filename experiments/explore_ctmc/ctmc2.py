"""Doan Van Tai — ctmc-v2: two-timescale evaluator for the two-path MMPP/M/1 plant (L7.3 Part 2, Stage 0)
[EXPLORATION ONLY; AI (Claude) theo ủy quyền]. Spec: experiments/explore_ctmc/SPEC_v2.md.

Per path the state is (n, m), index 4n + m, m = 1[sigma_f = +1] + 2 * 1[sigma_s = +1]. Arrivals are Poisson at
load + sigma_f * a_f + sigma_s * a_s, service mu when n > 0, the fast modulator flips at rate 1/T_f and the slow one at
1/T_s, independently; arrivals are blocked at N. With a_s = 0 the slow modulator is irrelevant and the chain lumps to
ctmc-v1 with kappa = T_f (control (a)). Finite-horizon truth is refused outside the controls until the author's card
is locked (locks_l73.json).
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigs, expm_multiply, splu

from experiments.explore_ctmc import ctmc
from experiments.explore_ctmc.ctmc import MU, TAU, RHOS, TAIL, DENSE_PAIRS, det_expm1, pair_sum, dense_disagree, mm1_mean

NAMESPACE = 'ctmc-v2'
M = 4
PEAK = F(6)
ROOT = Path(__file__).resolve().parents[2]
LOCKS_L73 = ROOT / 'results/explore_ctmc/locks_l73.json'
# Regimes on which finite-h truth is allowed for the controls of SPEC_v2 §6; excluded from every case list and card.
CONTROL_REGIMES = {'C2a': (F(7), F(15, 2), F(1), F(1, 5), F(2), F(4), F(2)),
                   'C2b': (F(13, 2), F(7), F(3, 2), F(1), F(10), F(3), F(3))}


def amplitudes(f):
    """(a_f, a_s) with a_f + a_s = 6 and a_s^2 / (a_f^2 + a_s^2) = f (exact for 1/2 and 1/5, 4 decimals otherwise)."""
    f = F(f)
    exact = {F(1, 2): (F(3), F(3)), F(1, 5): (F(4), F(2)), F(0): (F(6), F(0))}
    if f in exact:
        return exact[f]
    r = math.sqrt(float(f) / (1 - float(f)))
    a_s = F(f'{6 * r / (1 + r):.4f}')
    return PEAK - a_s, a_s


def f_of(a_f, a_s):
    return float(F(a_s) ** 2 / (F(a_f) ** 2 + F(a_s) ** 2)) if (a_f or a_s) else 0.0


def l73_unlocked():
    if not LOCKS_L73.exists():
        return False
    locks = json.loads(LOCKS_L73.read_text())
    card = LOCKS_L73.parent / locks.get('card', '')
    return card.is_file() and hashlib.sha256(card.read_bytes()).hexdigest() == locks.get('card_sha256')


def regime_key(lamA, lamB, u, Tf, Ts, af, as_):
    return tuple(F(x) for x in (lamA, lamB, u, Tf, Ts, af, as_))


def truth_allowed(lamA, lamB, u, Tf, Ts, af, as_):
    if F(as_) == 0 or regime_key(lamA, lamB, u, Tf, Ts, af, as_) in CONTROL_REGIMES.values() or l73_unlocked():
        return
    raise PermissionError('ctmc-v2 finite-horizon truth is refused until the author locks the L7.3 card (locks_l73.json)')


def sigmas():
    m = np.arange(M)
    return np.where(m & 1, 1.0, -1.0), np.where(m & 2, 1.0, -1.0)


def mode_generator(Tf, Ts):
    q = np.zeros((M, M))
    for m in range(M):
        q[m, m ^ 1] += 1 / float(Tf)
        q[m, m ^ 2] += 1 / float(Ts)
    return q - np.diag(q.sum(axis=1))


def rates(load, af, as_):
    sf, ss = sigmas()
    lam = float(load) + sf * float(af) + ss * float(as_)
    if lam.min() < -1e-12:
        raise ValueError('negative arrival rate: load must be >= a_f + a_s')
    return np.maximum(lam, 0.0)


def generator(load, Tf, Ts, af, as_, N, mu=MU):
    lam = rates(load, af, as_)
    n = np.repeat(np.arange(N + 1), M)
    m = np.tile(np.arange(M), N + 1)
    i = np.arange(M * (N + 1))
    up, down = n < N, n > 0
    rows = np.concatenate([i[up], i[down], i, i])
    cols = np.concatenate([i[up] + M, i[down] - M, i ^ 1, i ^ 2])
    vals = np.concatenate([lam[m[up]], np.full(down.sum(), float(mu)), np.full(i.size, 1 / float(Tf)),
                           np.full(i.size, 1 / float(Ts))])
    keep = vals > 0
    Q = sp.csr_matrix((vals[keep], (rows[keep], cols[keep])), shape=(i.size, i.size))
    return (Q - sp.diags(np.asarray(Q.sum(axis=1)).ravel())).tocsr()


class Chain:
    """One path under one constant load: stationary law, Poisson-equation bias g, T_int, T_relax and exact V(h)."""

    def __init__(self, load, Tf, Ts, af, as_, N, mu=MU):
        self.load, self.Tf, self.Ts, self.af, self.as_, self.N = F(load), F(Tf), F(Ts), F(af), F(as_), int(N)
        if not self.load < mu:
            raise ValueError('unstable load')
        self.Q = generator(load, Tf, Ts, af, as_, N, mu)
        self.n = self.Q.shape[0]
        self.f = np.repeat(np.arange(N + 1), M).astype(float)
        QT = self.Q.T.tocsc()
        x = splu(QT[1:, 1:].tocsc()).solve(-QT[1:, 0].toarray().ravel())
        pi = np.concatenate([[1.0], x])
        self.pi = pi / pi.sum()
        self.r = float(self.pi @ self.f)
        b = -(self.f - self.r)
        g = np.concatenate([[0.0], splu(self.Q[1:, 1:].tocsc()).solve(b[1:])])
        self.g = g - self.pi @ g
        self.var = float(self.pi @ (self.f - self.r) ** 2)
        self.T_int = float(self.pi @ ((self.f - self.r) * self.g)) / self.var if self.var > 0 else 0.0
        self.residual = float(np.abs(self.pi @ self.Q).max())
        self._relax = None

    def key(self):
        return (self.Tf, self.Ts, self.af, self.as_)

    def T_relax(self):
        """1/|Re lambda_2| of the truncated generator (shift-invert Arnoldi around -1e-9; 0 is dropped)."""
        if self._relax is None:
            vals = eigs(self.Q.tocsc(), k=6, sigma=-1e-9, which='LM', return_eigenvectors=False, tol=1e-10,
                        v0=np.ones(self.n))
            nz = vals[np.abs(vals) > 1e-8]
            lam2 = nz[np.argmax(nz.real)]
            self._relax = dict(T_relax=float(1 / abs(lam2.real)), lambda2=[float(lam2.real), float(lam2.imag)])
        return self._relax

    def V(self, hs, regime):
        truth_allowed(*regime)
        hs = [float(h) for h in hs]
        out = np.empty((len(hs), self.n))
        w, t = self.g.copy(), 0.0
        for k in sorted(range(len(hs)), key=lambda j: hs[j]):
            if hs[k] > t:
                w = expm_multiply(self.Q * (hs[k] - t), w)
                t = hs[k]
            out[k] = hs[k] * self.r + self.g - w
        return out

    def V_aug(self, h, regime):
        truth_allowed(*regime)
        Qa = sp.bmat([[self.Q, sp.csr_matrix(self.f[:, None])], [None, sp.csr_matrix((1, 1))]]).tocsr()
        e = np.zeros(self.n + 1)
        e[-1] = 1.0
        return expm_multiply(Qa * float(h), e)[:-1]


_CHAINS = {}


def chain(load, Tf, Ts, af, as_, N):
    key = (F(load), F(Tf), F(Ts), F(af), F(as_), int(N))
    if key not in _CHAINS:
        if len(_CHAINS) > 24:
            _CHAINS.clear()
        _CHAINS[key] = Chain(*key)
    return _CHAINS[key]


def matrix_geometric(load, Tf, Ts, af, as_, mu=MU):
    """Infinite-buffer stationary law pi_n = pi_0 R^n of the 4-phase level-independent QBD (logarithmic reduction)."""
    lam = rates(load, af, as_)
    Qm = mode_generator(Tf, Ts)
    I = np.eye(M)
    A0, A2 = np.diag(lam), mu * I
    A1 = Qm - np.diag(lam) - mu * I
    B1 = A1 + mu * I
    inv = np.linalg.inv(-A1)
    H, L = inv @ A0, inv @ A2
    G, T = L.copy(), H.copy()
    for _ in range(200):
        U = H @ L + L @ H
        Mi = np.linalg.inv(I - U)
        H, L = Mi @ H @ H, Mi @ L @ L
        G, T = G + T @ L, T @ H
        if np.abs(T).max() < 1e-30:
            break
    if not np.abs(1 - G.sum(axis=1)).max() <= 1e-10:
        raise ArithmeticError('logarithmic reduction did not converge')
    R = A0 @ np.linalg.inv(-(A1 + A0 @ G))
    pi0 = np.linalg.svd((B1 + R @ A2).T)[2][-1]
    S = np.linalg.inv(I - R)
    pi0 = pi0 / (pi0 @ S @ np.ones(M))

    def tail(N):
        return float(pi0 @ np.linalg.matrix_power(R, int(N)) @ S @ np.ones(M))
    return dict(R=R, pi0=pi0, tail=tail, mean=float(pi0 @ R @ S @ S @ np.ones(M)))


def choose_N(load, Tf, Ts, af, as_, tol=TAIL):
    tail = matrix_geometric(load, Tf, Ts, af, as_)['tail']
    lo, hi = 0, 1
    while tail(hi) > tol:
        lo, hi = hi, 2 * hi
        if hi > 1 << 20:
            raise ValueError('truncation level beyond 2^20')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if tail(mid) > tol else (lo, mid)
    return max(40, math.ceil(1.2 * hi))


# ---------------------------------------------------------------- M0: deterministic mean rollout with reflection
def _C(t, L, sf, af, Tf, ss, as_, Ts):
    t = np.asarray(t, dtype=float)
    return (L * t + sf * af * (Tf / 2) * (-det_expm1(-2 * t / Tf))
            + ss * as_ * (Ts / 2) * (-det_expm1(-2 * t / Ts)))


def _I(t, L, sf, af, Tf, ss, as_, Ts):
    t = np.asarray(t, dtype=float)
    return (L * t * t / 2 + sf * af * (Tf / 2) * (t + (Tf / 2) * det_expm1(-2 * t / Tf))
            + ss * as_ * (Ts / 2) * (t + (Ts / 2) * det_expm1(-2 * t / Ts)))


def _d(t, L, sf, af, Tf, ss, as_, Ts):
    t = np.asarray(t, dtype=float)
    return L + sf * af * (1 + det_expm1(-2 * t / Tf)) + ss * as_ * (1 + det_expm1(-2 * t / Ts))


def _bisect(fun, lo, hi, it=200):
    """Root of a function that is >= 0 at lo and < 0 at hi (vectorised over arrays lo, hi)."""
    lo, hi = np.array(lo, dtype=float), np.array(hi, dtype=float)
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        pos = fun(mid) >= 0
        lo, hi = np.where(pos, mid, lo), np.where(pos, hi, mid)
    return hi


def mode_shape(load, Tf, Ts, af, as_, m, mu=MU):
    """Sign pattern of the drift d(t) for mode m: 'D' (-), 'PM' (+, -) with t2, or 'MPM' (-, +, -) with t1 < t2."""
    sf_all, ss_all = sigmas()
    sf, ss = sf_all[m], ss_all[m]
    L = float(load) - mu
    p = (L, sf, float(af), float(Tf), ss, float(as_), float(Ts))
    d = lambda t: float(_d(np.array([t]), *p)[0])
    tot = float(af) + float(as_)
    t_big = (max(float(Tf), float(Ts)) / 2) * math.log(2 * tot / -L) + 1.0 if tot > -L else 1.0
    # turning point of d (exists only when the two modulators have opposite signs and both amplitudes are positive)
    tstar = None
    if sf * ss < 0 and float(af) > 0 and float(as_) > 0:
        num = (float(af) / float(Tf)) / (float(as_) / float(Ts))
        if num > 1:
            tstar = math.log(num) / (2 * (1 / float(Tf) - 1 / float(Ts)))
    pts = [0.0] + ([tstar] if tstar and tstar < t_big else []) + [t_big]
    roots = []
    for a, b in zip(pts[:-1], pts[1:]):
        da, db = d(a), d(b)
        if (da >= 0) != (db >= 0):
            sgn = 1.0 if da >= 0 else -1.0
            roots.append(float(_bisect(lambda t: sgn * _d(t, *p), np.array([a]), np.array([b]))[0]))
    d0 = d(0.0)
    if d0 < 0 and not roots:
        return dict(shape='D', p=p)
    if d0 >= 0 and len(roots) == 1:
        return dict(shape='PM', p=p, t2=roots[0])
    if d0 < 0 and len(roots) == 2:
        t1, t2 = roots
        return dict(shape='MPM', p=p, t1=t1, t2=t2, C1=float(_C(np.array([t1]), *p)[0]),
                    C2=float(_C(np.array([t2]), *p)[0]))
    raise ArithmeticError(f'unexpected drift sign pattern d0={d0}, roots={roots}')


def m0_vhat(load, Tf, Ts, af, as_, N, hs, mu=MU, return_T=False):
    """Mean-rollout cost per state (rows follow hs; h may be inf) and the first time T the queue reaches 0 under this
    load (T >= h means the queue stays positive on [0, h], used for the exact-tie rule)."""
    if not float(load) < mu:
        raise ValueError('mean rollout needs load < mu')
    nS = M * (N + 1)
    out = np.empty((len(hs), nS))
    T_all = np.empty(nS)
    nvec = np.arange(N + 1, dtype=float)
    sf_all, ss_all = sigmas()
    for m in range(M):
        sh = mode_shape(load, Tf, Ts, af, as_, m, mu)
        p = sh['p']
        L = p[0]
        pos = float(af) * float(Tf) / 2 * (sf_all[m] > 0) + float(as_) * float(Ts) / 2 * (ss_all[m] > 0)
        C = lambda t: _C(t, *p)
        I = lambda t: _I(t, *p)
        idx = np.arange(N + 1) * M + m
        if sh['shape'] in ('D', 'PM'):
            lo = np.full(N + 1, sh.get('t2', 0.0))
            hi = np.maximum((nvec + pos) / -L, lo) + 1.0
            T = _bisect(lambda t: nvec + C(t), lo, hi)
            if sh['shape'] == 'D':
                T[nvec == 0] = 0.0
            for j, h in enumerate(hs):
                t = np.minimum(float(h), T)
                v = nvec * t + I(t)
                v[t == 0] = 0.0
                out[j, idx] = np.maximum(v, 0.0)
            T_all[idx] = T
        else:
            t1, t2, C1 = sh['t1'], sh['t2'], sh['C1']
            hi_n = np.maximum((nvec + pos) / -L, t2) + 1.0
            Tn = _bisect(lambda t: nvec + C(t), np.full(N + 1, t2), hi_n)           # n >= -C1: one zero after t2
            Ta = _bisect(lambda t: nvec + C(t), np.zeros(N + 1), np.full(N + 1, t1))  # n < -C1: zero before t1
            Ta[nvec == 0] = 0.0
            t3 = float(_bisect(lambda t: C(t) - C1, np.array([t2]), np.array([max((-C1 + pos) / -L, t2) + 1.0]))[0])
            low = nvec < -C1
            T = np.where(low, Ta, Tn)
            for j, h in enumerate(hs):
                h = float(h)
                ta = np.minimum(h, T)
                v = nvec * ta + I(ta)
                v[ta == 0] = 0.0
                if h > t1:
                    tb = min(h, t3)
                    extra = float(I(np.array([tb]))[0] - I(np.array([t1]))[0] - C1 * (tb - t1))
                    v = v + np.where(low, max(extra, 0.0), 0.0)
                out[j, idx] = np.maximum(v, 0.0)
            T_all[idx] = T
    return (out, T_all) if return_T else out


def m0_gap(lam, u, Tf, Ts, af, as_, N, hs, side):
    """Mean-rollout gap Switch - Stay of one path with the ctmc-v1 exact-tie shift (SPEC_v2 §2)."""
    light, T = m0_vhat(lam, Tf, Ts, af, as_, N, hs, return_T=True)
    heavy = m0_vhat(lam + u, Tf, Ts, af, as_, N, hs)
    out = np.empty_like(light)
    for j, h in enumerate(hs):
        h = float(h)
        diff = (light[j] - heavy[j]) if side == 'A' else (heavy[j] - light[j])
        if h == math.inf:
            out[j] = diff
            continue
        c0 = float(u) * h * h / 2
        out[j] = diff + c0 if side == 'A' else diff - c0
        out[j][saturated(T, h, af, as_)] = 0.0
    return out


SAT_TOL = 1e-12


def saturated(T, h, af, as_, mu=MU):
    """Exact-tie set of SPEC_v2 §2: the light-load queue stays positive on [0, h] (T >= h), or it reaches 0 so close
    to h that the gap can differ from the linear value -/+ u h^2/2 by at most max|d| (h - T)^2 <= SAT_TOL (1 + h), the
    near-tie tolerance of pair_sum. Without the second clause, states whose zero time coincides with h to ~1e-9
    (integer n, rational load, e^{-2h/T} tiny) get a sign decided by rounding (control (a) attempt01)."""
    dmax = float(mu) + float(af) + float(as_)
    gapT = np.maximum(h - T, 0.0)
    return (T >= h) | (dmax * gapT * gapT <= SAT_TOL * (1 + h))


def posterior_mean(stay, vec, tau=TAU):
    """E[v(X) | Y = y] for the old backlog y (both modes unknown): push the stationary law at y through e^{Q tau}."""
    vec = np.asarray(vec, dtype=float)
    one = vec.ndim == 1
    vec = vec[:, None] if one else vec
    push = expm_multiply(stay.Q * float(tau), vec).reshape(-1, M, vec.shape[1])
    pi = stay.pi.reshape(-1, M)
    p = pi.sum(axis=1)
    out = (pi[:, :, None] * push).sum(axis=1) / np.where(p > 0, p, 1)[:, None]
    return out[:, 0] if one else out


def tint_v1_ratio(load, kappa):
    """T_int / kappa of the one-scale ctmc-v1 chain (a = 6) at the same load: stationary, used for the §3d formula."""
    N = ctmc.choose_N(load, kappa)
    return ctmc.chain(load, kappa, N).T_int / float(kappa)


def tint_approx(load, Tf, Ts, af, as_):
    f = f_of(af, as_)
    return (1 - f) * tint_v1_ratio(load, Tf) * float(Tf) + f * tint_v1_ratio(load, Ts) * float(Ts)


def _check_domain(lamA, lamB, u, Tf, Ts, af, as_, c, control=False):
    peak = af + as_
    if not (min(lamA, lamB) >= peak and max(lamA, lamB) + u < MU and 0 < Tf < Ts and af >= 0 and as_ >= 0 and c >= 0):
        raise ValueError('outside the ctmc-v2 domain')
    if not control and not (F(1, 4) <= u <= 3 and c == 0):
        raise ValueError('outside the ctmc-v2 scientific domain (u in [1/4, 3], c = 0)')


def _chains(lamA, lamB, u, Tf, Ts, af, as_, N_scale=1):
    NA, NB = (int(N_scale) * choose_N(lam + u, Tf, Ts, af, as_) for lam in (lamA, lamB))
    Ast, Asw = chain(lamA + u, Tf, Ts, af, as_, NA), chain(lamA, Tf, Ts, af, as_, NA)
    Bst, Bsw = chain(lamB, Tf, Ts, af, as_, NB), chain(lamB + u, Tf, Ts, af, as_, NB)
    return NA, NB, Ast, Asw, Bst, Bsw


def _chain_info(Ast, Asw, Bst, Bsw, relax=True):
    out = {}
    for name, ch in dict(A_stay=Ast, A_switch=Asw, B_stay=Bst, B_switch=Bsw).items():
        d = dict(load=str(ch.load), N=ch.N, r=ch.r, T_int=ch.T_int, var=ch.var, residual=ch.residual)
        if relax:
            d.update(ch.T_relax())
            d['T_int_approx_3d'] = tint_approx(ch.load, ch.Tf, ch.Ts, ch.af, ch.as_)
        out[name] = d
    return out


def evaluate(lamA, lamB, u, Tf, Ts, af, as_, hs, c=0, control=False, N_scale=1, disagree=True, arrays=False,
             relax=False):
    """All four cells, twins and asymptotic read-outs for one ctmc-v2 regime at each horizon in hs (truth)."""
    lamA, lamB, u, Tf, Ts, af, as_, c = (F(x) for x in (lamA, lamB, u, Tf, Ts, af, as_, c))
    regime = (lamA, lamB, u, Tf, Ts, af, as_)
    truth_allowed(*regime)
    hs = [F(h) for h in hs]
    _check_domain(lamA, lamB, u, Tf, Ts, af, as_, c, control)
    if min(hs) <= 0:
        raise ValueError('h must be positive')
    NA, NB, Ast, Asw, Bst, Bsw = _chains(lamA, lamB, u, Tf, Ts, af, as_, N_scale)
    H = len(hs)
    hf = [float(h) for h in hs]

    def gaps(st, sw, sign):
        Vst = st.V(hs, regime)
        Vsw = sw.V(hs, regime)
        d = sign * (Vsw - Vst)
        lam = min(st.load, sw.load)
        dh = m0_gap(lam, abs(sw.load - st.load), Tf, Ts, af, as_, st.N, hf + [math.inf], 'A' if sign > 0 else 'B')
        b = sign * (sw.g - st.g)
        return d, dh, b
    dA, dhA, bA = gaps(Ast, Asw, +1)
    dB, dhB, bB = gaps(Bsw, Bst, -1)

    def old(stay, d, dh, b):
        post = posterior_mean(stay, np.column_stack([d.T, dh.T, b]))
        return post[:, :H].T, post[:, H:2 * H + 1].T, post[:, -1]
    dAo, dhAo, bAo = old(Ast, dA, dhA, bA)
    dBo, dhBo, bBo = old(Bst, dB, dhB, bB)
    wA, wB = Ast.pi, Bst.pi
    pA, pB = Ast.pi.reshape(-1, M).sum(axis=1), Bst.pi.reshape(-1, M).sum(axis=1)
    r_stay, r_switch = Ast.r + Bst.r, Asw.r + Bsw.r
    s = r_switch - r_stay
    r_min = min(r_stay, r_switch)
    s_mm1 = mm1_mean(lamA) + mm1_mean(lamB + u) - mm1_mean(lamA + u) - mm1_mean(lamB)
    cf = float(c)
    new = lambda uA, vA, uB, vB, tol=0.0: pair_sum(wA, uA, vA, wB, uB, vB, cf, tol)
    olds = lambda uA, vA, uB, vB, tol=0.0: pair_sum(pA, uA, vA, pB, uB, vB, cf, tol)
    F_new = new(dhA[H], bA, dhB[H], bB)
    F_old = olds(dhAo[H], bAo, dhBo[H], bBo)
    a_inf = s < 0
    Eb = float(wA @ bA + wB @ bB) + cf
    asym = dict(F_new=F_new[0], F_old=F_old[0], z_inf=100 * s * (F_old[0] - F_new[0]) / r_min, a_inf_switch=bool(a_inf),
                B=F_old[1] - F_new[1], beta_C=Eb if a_inf else 0.0,
                tie_mass_new=new(dhA[H], bA, dhB[H], bB, 1e-12)[2], tie_mass_old=olds(dhAo[H], bAo, dhBo[H], bBo, 1e-12)[2])
    Kn, Ko = new(bA, bA, bB, bB), olds(bAo, bAo, bBo, bBo)
    asym.update(F_new_ko=Kn[0], F_old_ko=Ko[0], z_inf_ko=100 * s * (Ko[0] - Kn[0]) / r_min, B_ko=Ko[1] - Kn[1])
    T_int_max = max(Ast.T_int, Bst.T_int, Asw.T_int, Bsw.T_int)
    rows = []
    for k, h in enumerate(hf):
        scale = h * r_stay
        tol = 1e-12 * (scale + 1)
        c11, c10 = new(dA[k], dA[k], dB[k], dB[k], tol), new(dhA[k], dA[k], dhB[k], dB[k], tol)
        c01, c00 = olds(dAo[k], dAo[k], dBo[k], dBo[k], tol), olds(dhAo[k], dAo[k], dhBo[k], dBo[k], tol)
        G00, G01, G10, G11 = c00[1], c01[1], c10[1], c11[1]
        Cref = scale + G11
        pct = lambda x: 100 * x / Cref
        Ed = float(wA @ dA[k]) + float(wB @ dB[k]) + cf
        twins = dict(M1_new=G11, M1_old=G01, M0_new=G10, M0_old=G00, static=Ed if h * s + cf < 0 else 0.0,
                     const=min(0.0, Ed))
        shares = dict(M1_new=c11[0], M1_old=c01[0], M0_new=c10[0], M0_old=c00[0], static=float(h * s + cf < 0),
                      const=float(Ed < 0))
        margin = {}
        for rho in RHOS:
            sh = float(rho) * scale
            mn, mo = new(dhA[k] + sh, dA[k], dhB[k], dB[k]), olds(dhAo[k] + sh, dAo[k], dhBo[k], dBo[k])
            margin[str(rho)] = dict(new=pct(mn[1] - G11), old=pct(mo[1] - G11), share_new=mn[0], share_old=mo[0])
        best_new = min(margin, key=lambda r: (margin[r]['new'], F(r)))
        best_old = min(margin, key=lambda r: (margin[r]['old'], F(r)))
        twins['margin_new'] = G11 + margin[best_new]['new'] * Cref / 100
        twins['margin_old'] = G11 + margin[best_old]['old'] * Cref / 100
        for name, sv in (('hybrid', s), ('hybrid_mm1', s_mm1)):
            hn, ho = new(dhA[k] + h * sv, dA[k], dhB[k], dB[k]), olds(dhAo[k] + h * sv, dAo[k], dhBo[k], dBo[k])
            twins[f'{name}_new'], twins[f'{name}_old'] = hn[1], ho[1]
            shares[f'{name}_new'], shares[f'{name}_old'] = hn[0], ho[0]
        kn, ko = new(dA[k] - h * s, dA[k], dB[k], dB[k]), olds(dAo[k] - h * s, dAo[k], dBo[k], dBo[k])
        twins['ko_new'], twins['ko_old'] = kn[1], ko[1]
        shares['ko_new'], shares['ko_old'] = kn[0], ko[0]
        row = dict(h=str(hs[k]), h_Tf=float(hs[k] / Tf), h_Ts=float(hs[k] / Ts), h_Tint=h / T_int_max,
                   L00=scale + G00, L01=scale + G01, L10=scale + G10, L11=Cref, Cref=Cref, E_stay=scale, E_gap=Ed,
                   G_S=pct(G00 - G10), G_M=pct(G00 - G01), G_SM=pct(G00 - G11), Gamma=pct(G10 + G01 - G00 - G11),
                   S=pct(G01 - G11), M=pct(G10 - G11), regret={t: pct(v - G11) for t, v in twins.items()},
                   shares=shares, margin=margin, margin_best=dict(new=best_new, old=best_old),
                   G_S_hybrid=pct(twins['hybrid_old'] - twins['hybrid_new']),
                   G_S_ko=pct(twins['ko_old'] - twins['ko_new']),
                   z_pred_first_order_inf_decisions=100 * (h * s * (asym['F_old'] - asym['F_new']) + asym['B'])
                   / (h * r_min + asym['beta_C']),
                   z_pred_first_order_ko=100 * (h * s * (asym['F_old_ko'] - asym['F_new_ko']) + asym['B_ko'])
                   / (h * r_min + asym['beta_C']),
                   tie_mass=dict(c11=c11[2], c10=c10[2], c01=c01[2], c00=c00[2]))
        row['dep_static'] = {t: (v if shares['static'] == 0 else 1 - v) for t, v in shares.items()
                             if t not in ('static', 'const')}
        if disagree and wA.size * wB.size <= DENSE_PAIRS:
            row['disagree_new'] = dict(M0=dense_disagree(wA, dhA[k], dA[k], wB, dhB[k], dB[k], cf))
            row['disagree_old'] = dict(M0=dense_disagree(pA, dhAo[k], dAo[k], pB, dhBo[k], dBo[k], cf))
        rows.append(row)
    out = dict(namespace=NAMESPACE, parameters=[str(x) for x in (lamA, lamB, u, Tf, Ts, af, as_, c)], f=f_of(af, as_),
               mu=MU, tau=TAU, N=dict(A=NA, B=NB), r_stay=r_stay, r_switch=r_switch, s=s, r_min=r_min, s_mm1=s_mm1,
               x=float((lamB - lamA) / u), delta=float(lamB - lamA), T_int_max=T_int_max,
               chains=_chain_info(Ast, Asw, Bst, Bsw, relax), asymptotic=asym, h=rows)
    if arrays:
        out['_arrays'] = dict(dA=dA, dhA=dhA, dAo=dAo, dhAo=dhAo, dB=dB, dhB=dhB, dBo=dBo, dhBo=dhBo, NA=NA, NB=NB)
    return out


def evaluate_m0(lamA, lamB, u, Tf, Ts, af, as_, hs, c=0, N_scale=1, relax=True):
    """Zero-fit read-outs that never touch finite-h truth: stationary laws, r, s, T_int, T_relax, bias g, the
    mean-rollout decisions on old and new state at each h and at h = inf, KO at h = inf, first-order z."""
    lamA, lamB, u, Tf, Ts, af, as_, c = (F(x) for x in (lamA, lamB, u, Tf, Ts, af, as_, c))
    hs = [F(h) for h in hs]
    _check_domain(lamA, lamB, u, Tf, Ts, af, as_, c)
    NA, NB, Ast, Asw, Bst, Bsw = _chains(lamA, lamB, u, Tf, Ts, af, as_, N_scale)
    hf = [float(h) for h in hs] + [math.inf]
    dhA = m0_gap(lamA, u, Tf, Ts, af, as_, NA, hf, 'A')
    dhB = m0_gap(lamB, u, Tf, Ts, af, as_, NB, hf, 'B')
    bA, bB = Asw.g - Ast.g, Bsw.g - Bst.g
    postA = posterior_mean(Ast, np.column_stack([dhA.T, bA]))
    postB = posterior_mean(Bst, np.column_stack([dhB.T, bB]))
    wA, wB = Ast.pi, Bst.pi
    pA, pB = Ast.pi.reshape(-1, M).sum(axis=1), Bst.pi.reshape(-1, M).sum(axis=1)
    r_stay, r_switch = Ast.r + Bst.r, Asw.r + Bsw.r
    s, r_min = r_switch - r_stay, min(r_stay, r_switch)
    a_inf = s < 0
    cf = float(c)
    Eb = float(wA @ bA + wB @ bB) + cf
    T_int_max = max(ch.T_int for ch in (Ast, Asw, Bst, Bsw))
    per_h = []
    for k, h in enumerate(hf):
        new = pair_sum(wA, dhA[k], bA, wB, dhB[k], bB, cf, 1e-12)
        old = pair_sum(pA, postA[:, k], postA[:, -1], pB, postB[:, k], postB[:, -1], cf, 1e-12)
        row = dict(h='inf' if h == math.inf else str(hs[k]), F_new=new[0], F_old=old[0], tie_new=new[2],
                   tie_old=old[2], B=old[1] - new[1])
        if h != math.inf:
            row.update(h_Tf=float(hs[k] / Tf), h_Ts=float(hs[k] / Ts), h_Tint=h / T_int_max,
                       z_pred_first_order=100 * (h * s * (old[0] - new[0]) + old[1] - new[1])
                       / (h * r_min + (Eb if a_inf else 0.0)))
        per_h.append(row)
    inf = per_h[-1]
    Kn = pair_sum(wA, bA, bA, wB, bB, bB, cf, 1e-12)
    Ko = pair_sum(pA, postA[:, -1], postA[:, -1], pB, postB[:, -1], postB[:, -1], cf, 1e-12)
    ko = dict(F_new_ko=Kn[0], F_old_ko=Ko[0], B_ko=Ko[1] - Kn[1], z_inf_ko=100 * s * (Ko[0] - Kn[0]) / r_min,
              tie_new_ko=Kn[2], tie_old_ko=Ko[2])
    stat = 1.0 if a_inf else 0.0
    ko['dep_inf'] = dict(M0_new=abs(inf['F_new'] - stat), M0_old=abs(inf['F_old'] - stat), ko_new=abs(Kn[0] - stat),
                         ko_old=abs(Ko[0] - stat))
    ko['h_ko'] = [dict(h=str(hs[k]), z_pred_first_order_ko=100 * (h * s * (Ko[0] - Kn[0]) + Ko[1] - Kn[1])
                       / (h * r_min + (Eb if a_inf else 0.0))) for k, h in enumerate(hf[:-1])]
    return dict(**ko, namespace=NAMESPACE, kind='M0_and_stationary_only',
                parameters=[str(x) for x in (lamA, lamB, u, Tf, Ts, af, as_, c)], f=f_of(af, as_), N=dict(A=NA, B=NB),
                r_stay=r_stay, r_switch=r_switch, s=s, r_min=r_min, x=float((lamB - lamA) / u),
                delta=float(lamB - lamA), chains=_chain_info(Ast, Asw, Bst, Bsw, relax), T_int_max=T_int_max,
                beta_C=Eb if a_inf else 0.0, z_inf=100 * s * (inf['F_old'] - inf['F_new']) / r_min,
                a_inf_switch=bool(a_inf),
                M0_regret_new_pred=100 * abs(s) * ((1 - inf['F_new']) if a_inf else inf['F_new']) / r_min,
                M0_regret_old_pred=100 * abs(s) * ((1 - inf['F_old']) if a_inf else inf['F_old']) / r_min, h=per_h)


# ---------------------------------------------------------------- D22: fresh backlog without either mode
D22_NMAX = 3000
D22_PRUNE = 1e-20
D22_CHUNK = 256
D22_CACHE = Path(os.environ.get('SMR_D22_CACHE_V2', Path.home() / '.cache/smr_ctmc_d22_v2'))


def joint_old_current(stay, tau=TAU):
    """J[y, n, m] = P(Y = y, X = (n, m)) under P1 (Y = backlog at t0 - tau, modes summed out). Disk-cached."""
    key = f'{stay.load}_{stay.Tf}_{stay.Ts}_{stay.af}_{stay.as_}_{stay.N}_{F(tau)}_{D22_CHUNK}'.replace('/', '-')
    path = D22_CACHE / f'{key}.npy'
    if path.exists():
        return np.load(path)
    N, n = stay.N, stay.n
    QT = (stay.Q.T * float(tau)).tocsr()
    out = np.empty((n, N + 1))
    rows = np.arange(n)
    for s0 in range(0, N + 1, D22_CHUNK):
        ys = np.arange(s0, min(N + 1, s0 + D22_CHUNK))
        B = np.zeros((n, ys.size))
        sel = (rows // M >= ys[0]) & (rows // M <= ys[-1])
        B[rows[sel], rows[sel] // M - ys[0]] = stay.pi[sel]
        out[:, ys] = expm_multiply(QT, B)
    J = out.T.reshape(N + 1, N + 1, M)
    D22_CACHE.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f'.{os.getpid()}.tmp.npy')
    np.save(tmp, J)
    os.replace(tmp, path)
    return J


def cond_on_backlog(J, v):
    w = J.sum(axis=2)
    num = (J * np.asarray(v, dtype=float).reshape(J.shape[1], M)[None, :, :]).sum(axis=2)
    return w, np.divide(num, w, out=np.zeros_like(num), where=w > 0)


def _flat(J, keep, v):
    return cond_on_backlog(J, v)[1][keep]


def evaluate_d22_m0(lamA, lamB, u, Tf, Ts, af, as_, hs, c=0, relax=True):
    """Zero-fit D22 read-outs: M0 Switch share on (Y, Q) at each h and h = inf, and the split of z_inf into a
    backlog part z_F_inf (old -> backlog-only) and a mode part z_V_inf (backlog-only -> full state)."""
    base = evaluate_m0(lamA, lamB, u, Tf, Ts, af, as_, hs, c=c, relax=relax)
    NA, NB = base['N']['A'], base['N']['B']
    if max(NA, NB) > D22_NMAX:
        raise ValueError(f'D22 range is N <= {D22_NMAX} per path (N = {NA}, {NB})')
    lamA, lamB, u, Tf, Ts, af, as_, c = (F(x) for x in (lamA, lamB, u, Tf, Ts, af, as_, c))
    Ast, Bst = chain(lamA + u, Tf, Ts, af, as_, NA), chain(lamB, Tf, Ts, af, as_, NB)
    Asw, Bsw = chain(lamA, Tf, Ts, af, as_, NA), chain(lamB + u, Tf, Ts, af, as_, NB)
    JA, JB = joint_old_current(Ast), joint_old_current(Bst)
    wA, wB = JA.sum(axis=2), JB.sum(axis=2)
    kA, kB = wA > D22_PRUNE, wB > D22_PRUNE
    wa, wb = wA[kA], wB[kB]
    hf = [float(F(h)) for h in hs] + [math.inf]
    dhA = m0_gap(lamA, u, Tf, Ts, af, as_, NA, hf, 'A')
    dhB = m0_gap(lamB, u, Tf, Ts, af, as_, NB, hf, 'B')
    one = lambda x: np.ones(x.size)
    for k, row in enumerate(base['h']):
        g = pair_sum(wa, _flat(JA, kA, dhA[k]), one(wa), wb, _flat(JB, kB, dhB[k]), one(wb), float(c), 1e-12)
        row['F_cb'], row['tie_cb'] = g[0], g[2]
    bAf, bBf = _flat(JA, kA, Asw.g - Ast.g), _flat(JB, kB, Bsw.g - Bst.g)
    Kcb = pair_sum(wa, bAf, bAf, wb, bBf, bBf, float(c), 1e-12)
    inf = base['h'][-1]
    base['z_F_inf'] = 100 * base['s'] * (inf['F_old'] - inf['F_cb']) / base['r_min']
    base['z_V_inf'] = 100 * base['s'] * (inf['F_cb'] - inf['F_new']) / base['r_min']
    stat = 1.0 if base['s'] < 0 else 0.0
    base['dep_inf'].update(M0_cb=abs(inf['F_cb'] - stat), ko_cb=abs(Kcb[0] - stat))
    base['F_cb_ko'] = Kcb[0]
    base['d22_dropped_mass'] = float(wA[~kA].sum() + wB[~kB].sum())
    base['kind'] = 'D22_M0_and_stationary_only'
    return base


def evaluate_d22(lamA, lamB, u, Tf, Ts, af, as_, hs, c=0, control=False, relax=False):
    """D22 truth (backlog-only decisions with M0 and with the true model); F, V, F1, V1 as in ctmc-v1."""
    out = evaluate(lamA, lamB, u, Tf, Ts, af, as_, hs, c, control=control, disagree=False, arrays=True, relax=relax)
    arr = out.pop('_arrays')
    NA, NB = arr['NA'], arr['NB']
    if max(NA, NB) > D22_NMAX:
        raise ValueError(f'D22 range is N <= {D22_NMAX} per path (N = {NA}, {NB})')
    lamA, lamB, u, Tf, Ts, af, as_, c = (F(x) for x in (lamA, lamB, u, Tf, Ts, af, as_, c))
    Ast, Bst = chain(lamA + u, Tf, Ts, af, as_, NA), chain(lamB, Tf, Ts, af, as_, NB)
    JA, JB = joint_old_current(Ast), joint_old_current(Bst)
    wA, wB = JA.sum(axis=2), JB.sum(axis=2)
    kA, kB = wA > D22_PRUNE, wB > D22_PRUNE
    wa, wb = wA[kA], wB[kB]
    cf = float(c)
    for k, row in enumerate(out['h']):
        scale, Cref = row['E_stay'], row['Cref']
        pct = lambda x: 100 * x / Cref
        tol = 1e-12 * (scale + 1)
        vA, vB = _flat(JA, kA, arr['dA'][k]), _flat(JB, kB, arr['dB'][k])
        gA, gB = _flat(JA, kA, arr['dhA'][k]), _flat(JB, kB, arr['dhB'][k])
        cb0 = pair_sum(wa, gA, vA, wb, gB, vB, cf, tol)
        cb1 = pair_sum(wa, vA, vA, wb, vB, vB, cf, tol)
        G = {cell: row[f'L{cell}'] - scale for cell in ('00', '01', '10', '11')}
        row['d22'] = dict(F=pct(G['00'] - cb0[1]), V=pct(cb0[1] - G['10']), F1=pct(G['01'] - cb1[1]),
                          V1=pct(cb1[1] - G['11']), share_cb0=cb0[0], share_cb1=cb1[0], tie_cb0=cb0[2], tie_cb1=cb1[2])
    out['d22_dropped_mass'] = float(wA[~kA].sum() + wB[~kB].sum())
    return out
