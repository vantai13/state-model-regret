"""Doan Van Tai — ctmc-v1: exact evaluator for the two-path MMPP/M/1 plant (L7.1) [EXPLORATION ONLY;
AI (Claude) theo ủy quyền]. Spec: experiments/explore_ctmc/SPEC.md.

Per path the state is (n, m), index 2n + m, n = 0..N packets in system, m = 0 low / 1 high background mode.
Arrivals Poisson at load + sigma_m * a (sigma = -1, +1), exponential service mu when n > 0, mode flips at rate
1/kappa each way, arrivals blocked at N. Everything below is exact up to floating point and the truncation N:
no Monte Carlo. The amplitude a = 6 is fixed; any other amplitude is held out for the author (L7.2) and refused,
except a = 0 for the stationary-law control V2.
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

from fractions import Fraction as F
import math

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import expm_multiply, splu

MU = 10
A = 6
TAU = 1
RHOS = (F(0), F(1, 200), F(1, 100), F(1, 50), F(1, 20))
TAIL = 1e-13
DENSE_PAIRS = 5e7          # largest |X_A| * |X_B| for which disagreement shares are computed (dense, chunked)


def _amplitude(a, allow_zero):
    if a == A or (allow_zero and a == 0):
        return float(a)
    raise ValueError(f'amplitude a={a} is held out (a/mu != 0.6); only the author opens it in L7.2')


def generator(load, kappa, N, a=A, mu=MU):
    a = _amplitude(a, allow_zero=True)
    n = np.repeat(np.arange(N + 1), 2)
    m = np.tile([0, 1], N + 1)
    i = np.arange(2 * (N + 1))
    lam = float(load) + np.where(m == 1, a, -a)
    up, down = n < N, n > 0
    rows = np.concatenate([i[up], i[down], i])
    cols = np.concatenate([i[up] + 2, i[down] - 2, i + 1 - 2 * m])
    vals = np.concatenate([lam[up], np.full(down.sum(), float(mu)), np.full(i.size, 1 / float(kappa))])
    keep = vals > 0
    Q = sp.csr_matrix((vals[keep], (rows[keep], cols[keep])), shape=(i.size, i.size))
    return (Q - sp.diags(np.asarray(Q.sum(axis=1)).ravel())).tocsr()


class Chain:
    """One path under one constant load: stationary law, Poisson-equation bias g, T_int and exact V(h)."""

    def __init__(self, load, kappa, N, a=A, mu=MU):
        self.load, self.kappa, self.N, self.a = F(load), F(kappa), int(N), a
        if not self.load < mu:
            raise ValueError('unstable load')
        self.Q = generator(load, kappa, N, a, mu)
        self.n = self.Q.shape[0]
        self.f = np.repeat(np.arange(N + 1), 2).astype(float)
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

    def V(self, hs):
        """V(h, x) = E[int_0^h n dt | x] = h r + g - e^{Qh} g for each h (any order); rows follow hs."""
        hs = [float(h) for h in hs]
        out = np.empty((len(hs), self.n))
        w, t = self.g.copy(), 0.0
        for k in sorted(range(len(hs)), key=lambda j: hs[j]):
            if hs[k] > t:
                w = expm_multiply(self.Q * (hs[k] - t), w)
                t = hs[k]
            out[k] = hs[k] * self.r + self.g - w
        return out

    def V_aug(self, h):
        """Second route for V4: exponential of the generator augmented with the cost column."""
        Qa = sp.bmat([[self.Q, sp.csr_matrix(self.f[:, None])], [None, sp.csr_matrix((1, 1))]]).tocsr()
        e = np.zeros(self.n + 1)
        e[-1] = 1.0
        return expm_multiply(Qa * float(h), e)[:-1]


_CHAINS = {}


def chain(load, kappa, N):
    key = (F(load), F(kappa), int(N))
    if key not in _CHAINS:
        if len(_CHAINS) > 24:
            _CHAINS.clear()
        _CHAINS[key] = Chain(*key)
    return _CHAINS[key]


def matrix_geometric(load, kappa, a=A, mu=MU):
    """Infinite-buffer stationary law pi_n = pi_0 R^n (level-independent QBD; logarithmic reduction)."""
    a = _amplitude(a, allow_zero=True)
    q, l0, l1 = 1 / float(kappa), float(load) - a, float(load) + a
    I = np.eye(2)
    A0, A2 = np.diag([l0, l1]), mu * I
    A1 = np.array([[-(l0 + mu + q), q], [q, -(l1 + mu + q)]])
    B1 = A1 + mu * I
    inv = np.linalg.inv(-A1)
    H, L = inv @ A0, inv @ A2
    G, T = L.copy(), H.copy()
    for _ in range(100):
        U = H @ L + L @ H
        M = np.linalg.inv(I - U)
        H, L = M @ H @ H, M @ L @ L
        G, T = G + T @ L, T @ H
        if np.abs(T).max() < 1e-30:
            break
    if not np.abs(1 - G.sum(axis=1)).max() <= 1e-12:
        raise ArithmeticError('logarithmic reduction did not converge')
    R = A0 @ np.linalg.inv(-(A1 + A0 @ G))
    pi0 = np.linalg.svd((B1 + R @ A2).T)[2][-1]
    S = np.linalg.inv(I - R)
    pi0 = pi0 / (pi0 @ S @ np.ones(2))

    def tail(N):
        return float(pi0 @ np.linalg.matrix_power(R, int(N)) @ S @ np.ones(2))
    return dict(R=R, pi0=pi0, tail=tail, mean=float(pi0 @ R @ S @ S @ np.ones(2)))


def choose_N(load, kappa, tol=TAIL):
    tail = matrix_geometric(load, kappa)['tail']
    lo, hi = 0, 1
    while tail(hi) > tol:
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if tail(mid) > tol else (lo, mid)
    return max(40, math.ceil(1.2 * hi))


_LN2_HI, _LN2_LO, _INV_LN2 = 6.93147180369123816490e-01, 1.90821492927058770002e-10, 1.44269504088896338700e+00


def _taylor_expm1(r):
    p = np.ones_like(r)
    for n in range(25, 1, -1):
        p = 1.0 + (r * p) / n
    return r * p


def det_expm1(y):
    """expm1 for y <= 0 from correctly rounded +, *, / only, so every machine gives the same bits (numpy's array
    exp/expm1 pick CPU-specific SIMD kernels that differ in the last ulp between the local AMD and the GCP Xeon)."""
    y = np.asarray(y, dtype=float)
    out = np.empty_like(y)
    small = y > -0.35
    out[small] = _taylor_expm1(y[small])
    yb = y[~small]
    n = np.rint(yb * _INV_LN2)
    r = (yb - n * _LN2_HI) - n * _LN2_LO
    out[~small] = np.ldexp(1.0 + _taylor_expm1(r), n.astype(np.int64)) - 1.0
    return out


def m0_vhat(load, kappa, N, hs, a=A, mu=MU, return_T=False):
    """Mean-rollout cost per state (rows follow hs; h may be inf). Expected arrivals conditional on the current
    mode, deterministic drain: q(t) = max(0, n + C(t)), exact because the drift is monotone decreasing in t."""
    a = _amplitude(a, allow_zero=True)
    L, k = float(load) - mu, float(kappa)
    if L >= 0:
        raise ValueError('mean rollout needs load < mu')
    n = np.repeat(np.arange(N + 1), 2).astype(float)
    sig = np.tile([-1.0, 1.0], N + 1)

    def phi(t):
        return n + L * t + sig * a * (k / 2) * (-det_expm1(-2 * t / k))
    rising = (sig > 0) & (L + a > 0)
    tp = np.where(rising, (k / 2) * math.log(a / -L) if L + a > 0 else 0.0, 0.0)
    lo = tp.copy()
    hi = (n + np.where(sig > 0, a * k / 2, 0.0)) / -L
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        pos = phi(mid) > 0
        lo, hi = np.where(pos, mid, lo), np.where(pos, hi, mid)
    T = hi
    T[(n == 0) & ~rising] = 0.0

    def integral(t):
        return n * t + L * t * t / 2 + sig * a * (k / 2) * (t + (k / 2) * det_expm1(-2 * t / k))
    out = np.empty((len(hs), n.size))
    for j, h in enumerate(hs):
        t = np.minimum(float(h), T)
        v = integral(t)
        v[t == 0] = 0.0
        out[j] = np.maximum(v, 0.0)
    return (out, T) if return_T else out


def m0_gap(lam, u, kappa, N, hs, side):
    """Mean-rollout gap Switch - Stay of one path, shifted by +u h^2/2 (side 'A', where Switch removes u) or by
    -u h^2/2 (side 'B', where Switch adds u). The two shifts cancel exactly in the network gap, so decisions are
    unchanged; but at a state whose queue stays positive on [0, h] under the lighter load the rollout is linear in
    the load and the shifted gap is exactly 0. Both paths saturated therefore give an exact tie (Stay), the
    certified-tie rule of the contract, instead of a sign left to rounding. At h = inf there is no shift."""
    light, T = m0_vhat(lam, kappa, N, hs, return_T=True)
    heavy = m0_vhat(lam + u, kappa, N, hs)
    out = np.empty_like(light)
    for j, h in enumerate(hs):
        h = float(h)
        diff = (light[j] - heavy[j]) if side == 'A' else (heavy[j] - light[j])
        if h == math.inf:
            out[j] = diff
            continue
        c0 = float(u) * h * h / 2
        out[j] = diff + c0 if side == 'A' else diff - c0
        out[j][T >= h] = 0.0
    return out


def posterior_mean(stay, vec, tau=TAU):
    """E[v(X) | Y = y] for the old backlog y (no mode): push the stationary law at y through e^{Q tau}."""
    vec = np.asarray(vec, dtype=float)
    one = vec.ndim == 1
    vec = vec[:, None] if one else vec
    push = expm_multiply(stay.Q * float(tau), vec).reshape(-1, 2, vec.shape[1])
    pi = stay.pi.reshape(-1, 2)
    p = pi.sum(axis=1)
    out = (pi[:, :, None] * push).sum(axis=1) / np.where(p > 0, p, 1)[:, None]
    return out[:, 0] if one else out


def pair_sum(wA, uA, vA, wB, uB, vB, c, tol=0.0):
    """Exact sum over all pairs: mass and value of {uA + uB + c < 0} (Switch), value weight vA + vB + c, and the
    near-tie mass |uA + uB + c| <= tol. Sorting path B once; strict inequality so exact ties choose Stay."""
    c = float(c)
    order = np.argsort(uB, kind='stable')
    us = uB[order]
    W = np.concatenate([[0.0], np.cumsum(wB[order])])
    WV = np.concatenate([[0.0], np.cumsum((wB * vB)[order])])
    k = np.searchsorted(us, -c - uA, side='left')
    mass = float(wA @ W[k])
    value = float(wA @ ((vA + c) * W[k] + WV[k]))
    lo = np.searchsorted(us, -c - uA - tol, side='left')
    hi = np.searchsorted(us, -c - uA + tol, side='right')
    return mass, value, float(wA @ (W[hi] - W[lo]))


def dense_disagree(wA, uA1, uA2, wB, uB1, uB2, c):
    """Mass where two pair decisions differ (chunked dense; only used when |A|*|B| <= DENSE_PAIRS)."""
    c, out, step = float(c), 0.0, max(1, int(2e6 // max(1, wB.size)))
    for s in range(0, wA.size, step):
        sl = slice(s, s + step)
        d1 = uA1[sl, None] + uB1[None, :] + c < 0
        d2 = uA2[sl, None] + uB2[None, :] + c < 0
        out += float(wA[sl] @ ((d1 != d2) @ wB))
    return out


def mm1_mean(load, mu=MU):
    rho = float(load) / mu
    return rho / (1 - rho)


def evaluate(lamA, lamB, u, kappa, hs, c=0, a=A, control=False, N_scale=1, disagree=True, arrays=False, allow_csw=False):
    """All four cells, twins and asymptotic read-outs for one regime at each horizon in hs."""
    _amplitude(a, allow_zero=False)
    lamA, lamB, u, kappa, c = (F(x) for x in (lamA, lamB, u, kappa, c))
    hs = [F(h) for h in hs]
    if not (min(lamA, lamB) >= A and max(lamA, lamB) + u < MU and kappa > 0 and c >= 0 and min(hs) > 0):
        raise ValueError('outside the ctmc-v1 domain')
    if not control and not (F(1, 4) <= u <= 3 and (c == 0 or allow_csw)):
        raise ValueError('outside the ctmc-v1 scientific domain (u in [1/4, 3], c_sw = 0 unless Stage F)')
    NA, NB = (int(N_scale) * choose_N(lam + u, kappa) for lam in (lamA, lamB))
    Ast, Asw = chain(lamA + u, kappa, NA), chain(lamA, kappa, NA)
    Bst, Bsw = chain(lamB, kappa, NB), chain(lamB + u, kappa, NB)
    H = len(hs)
    hf = [float(h) for h in hs]

    def gaps(st, sw, sign):
        Vst = st.V(hs)
        Vsw = Vst if sw is st else sw.V(hs)
        d = sign * (Vsw - Vst)
        lam = min(st.load, sw.load)
        dh = m0_gap(lam, abs(sw.load - st.load), kappa, st.N, hf + [math.inf], 'A' if sign > 0 else 'B')
        b = sign * (sw.g - st.g)
        return d, dh, b
    # path A: Switch removes u (sign +1: d_A = V[lamA] - V[lamA+u]); path B: Switch adds u
    dA, dhA, bA = gaps(Ast, Asw, +1)
    dB, dhB, bB = gaps(Bsw, Bst, -1)          # Bsw - Bst written as -(Bst - Bsw)
    stayA, stayB = Ast, Bst

    def old(stay, d, dh, b):
        cols = np.column_stack([d.T, dh.T, b])
        post = posterior_mean(stay, cols)
        return post[:, :H].T, post[:, H:2 * H + 1].T, post[:, -1]
    dAo, dhAo, bAo = old(stayA, dA, dhA, bA)
    dBo, dhBo, bBo = old(stayB, dB, dhB, bB)
    wA, wB = stayA.pi, stayB.pi
    pA, pB = stayA.pi.reshape(-1, 2).sum(axis=1), stayB.pi.reshape(-1, 2).sum(axis=1)

    r_stay, r_switch = Ast.r + Bst.r, Asw.r + Bsw.r
    s = r_switch - r_stay
    r_min = min(r_stay, r_switch)
    s_mm1 = mm1_mean(lamA) + mm1_mean(lamB + u) - mm1_mean(lamA + u) - mm1_mean(lamB)
    cf = float(c)
    new = lambda uA, vA, uB, vB, tol=0.0: pair_sum(wA, uA, vA, wB, uB, vB, cf, tol)
    olds = lambda uA, vA, uB, vB, tol=0.0: pair_sum(pA, uA, vA, pB, uB, vB, cf, tol)

    # infinite-horizon mean-rollout read-outs (zero fit: M0 and stationary quantities only)
    F_new = new(dhA[H], bA, dhB[H], bB)
    F_old = olds(dhAo[H], bAo, dhBo[H], bBo)
    z_inf = 100 * s * (F_old[0] - F_new[0]) / r_min
    a_inf = s < 0
    Eb = float(wA @ bA + wB @ bB) + cf
    asym = dict(F_new=F_new[0], F_old=F_old[0], z_inf=z_inf, a_inf_switch=bool(a_inf),
                B=F_old[1] - F_new[1], beta_C=Eb if a_inf else 0.0,
                M0_regret_new_pred=100 * abs(s) * ((1 - F_new[0]) if a_inf else F_new[0]) / r_min,
                M0_regret_old_pred=100 * abs(s) * ((1 - F_old[0]) if a_inf else F_old[0]) / r_min,
                tie_mass_new=new(dhA[H], bA, dhB[H], bB, 1e-12)[2], tie_mass_old=olds(dhAo[H], bAo, dhBo[H], bBo, 1e-12)[2])

    rows = []
    for k, h in enumerate(hf):
        scale = h * r_stay
        tol = 1e-12 * (scale + 1)
        c11, c10 = new(dA[k], dA[k], dB[k], dB[k], tol), new(dhA[k], dA[k], dhB[k], dB[k], tol)
        c01, c00 = olds(dAo[k], dAo[k], dBo[k], dBo[k], tol), olds(dhAo[k], dAo[k], dhBo[k], dBo[k], tol)
        G00, G01, G10, G11 = c00[1], c01[1], c10[1], c11[1]
        Cref = scale + G11
        pct = lambda x: 100 * x / Cref
        EdA, EdB = float(wA @ dA[k]), float(wB @ dB[k])
        Ed = EdA + EdB + cf
        twins = dict(M1_new=G11, M1_old=G01, M0_new=G10, M0_old=G00,
                     static=Ed if h * s + cf < 0 else 0.0, const=min(0.0, Ed))
        shares = dict(M1_new=c11[0], M1_old=c01[0], M0_new=c10[0], M0_old=c00[0],
                      static=float(h * s + cf < 0), const=float(Ed < 0))
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
            hn = new(dhA[k] + h * sv, dA[k], dhB[k], dB[k])
            ho = olds(dhAo[k] + h * sv, dAo[k], dhBo[k], dBo[k])
            twins[f'{name}_new'], twins[f'{name}_old'] = hn[1], ho[1]
            shares[f'{name}_new'], shares[f'{name}_old'] = hn[0], ho[0]
        row = dict(h=str(hs[k]), h_kappa=float(hs[k] / kappa), h_Tint=h / max(Ast.T_int, Bst.T_int, Asw.T_int, Bsw.T_int),
                   L00=scale + G00, L01=scale + G01, L10=scale + G10, L11=Cref, Cref=Cref, E_stay=scale, E_gap=Ed,
                   G_S=pct(G00 - G10), G_M=pct(G00 - G01), G_SM=pct(G00 - G11), Gamma=pct(G10 + G01 - G00 - G11),
                   S=pct(G01 - G11), M=pct(G10 - G11),
                   regret={t: pct(v - G11) for t, v in twins.items()}, shares=shares,
                   margin=margin, margin_best=dict(new=best_new, old=best_old),
                   G_S_hybrid=pct(twins['hybrid_old'] - twins['hybrid_new']),
                   G_S_hybrid_mm1=pct(twins['hybrid_mm1_old'] - twins['hybrid_mm1_new']),
                   z_pred_first_order_inf_decisions=100 * (h * s * (asym['F_old'] - asym['F_new']) + asym['B']) / (h * r_min + asym['beta_C']),
                   tie_mass=dict(c11=c11[2], c10=c10[2], c01=c01[2], c00=c00[2]))
        if disagree and wA.size * wB.size <= DENSE_PAIRS:
            row['disagree_new'] = {t: dense_disagree(wA, uA, dA[k], wB, uB, dB[k], cf) for t, (uA, uB) in
                                   dict(M0=(dhA[k], dhB[k]), hybrid=(dhA[k] + h * s, dhB[k])).items()}
            row['disagree_old'] = {t: dense_disagree(pA, uA, dAo[k], pB, uB, dBo[k], cf) for t, (uA, uB) in
                                   dict(M0=(dhAo[k], dhBo[k]), hybrid=(dhAo[k] + h * s, dhBo[k])).items()}
        rows.append(row)
    chains = {name: dict(load=str(ch.load), N=ch.N, r=ch.r, T_int=ch.T_int, var=ch.var, residual=ch.residual)
              for name, ch in dict(A_stay=Ast, A_switch=Asw, B_stay=Bst, B_switch=Bsw).items()}
    out = dict(namespace='ctmc-v1', parameters=[str(x) for x in (lamA, lamB, u, kappa, c)], a=A, mu=MU, tau=TAU,
               N=dict(A=NA, B=NB), r_stay=r_stay, r_switch=r_switch, s=s, r_min=r_min, s_mm1=s_mm1,
               x=float((lamB - lamA) / u) if u else None, delta=float(lamB - lamA), chains=chains,
               asymptotic=asym, h=rows)
    if arrays:      # decision inputs for the Monte Carlo control V3 (not written to result files)
        out['_arrays'] = dict(dA=dA, dhA=dhA[:H], dAo=dAo, dhAo=dhAo[:H], dB=dB, dhB=dhB[:H], dBo=dBo,
                              dhBo=dhBo[:H], NA=NA, NB=NB)
    return out


def evaluate_m0(lamA, lamB, u, kappa, hs, c=0, allow_csw=False):
    """Pre-registration read-outs that never touch the finite-h truth (no V, no true gap): stationary laws, r, s,
    T_int, bias g, and the mean-rollout decisions on old and new state at each h and at h = inf. Used to write
    zero-fit predictions before any truth is computed (L7.1 §4)."""
    lamA, lamB, u, kappa, c = (F(x) for x in (lamA, lamB, u, kappa, c))
    hs = [F(h) for h in hs]
    if not (min(lamA, lamB) >= A and max(lamA, lamB) + u < MU and F(1, 4) <= u <= 3 and kappa > 0
            and c >= 0 and (c == 0 or allow_csw)):
        raise ValueError('outside the ctmc-v1 scientific domain')
    NA, NB = (choose_N(lam + u, kappa) for lam in (lamA, lamB))
    Ast, Asw = chain(lamA + u, kappa, NA), chain(lamA, kappa, NA)
    Bst, Bsw = chain(lamB, kappa, NB), chain(lamB + u, kappa, NB)
    hf = [float(h) for h in hs] + [math.inf]
    dhA = m0_gap(lamA, u, kappa, NA, hf, 'A')
    dhB = m0_gap(lamB, u, kappa, NB, hf, 'B')
    bA, bB = Asw.g - Ast.g, Bsw.g - Bst.g
    postA = posterior_mean(Ast, np.column_stack([dhA.T, bA]))
    postB = posterior_mean(Bst, np.column_stack([dhB.T, bB]))
    wA, wB = Ast.pi, Bst.pi
    pA, pB = Ast.pi.reshape(-1, 2).sum(axis=1), Bst.pi.reshape(-1, 2).sum(axis=1)
    r_stay, r_switch = Ast.r + Bst.r, Asw.r + Bsw.r
    s, r_min = r_switch - r_stay, min(r_stay, r_switch)
    a_inf = s < 0
    cf = float(c)
    Eb = float(wA @ bA + wB @ bB) + cf
    per_h = []
    for k, h in enumerate(hf):
        new = pair_sum(wA, dhA[k], bA, wB, dhB[k], bB, cf, 1e-12)
        old = pair_sum(pA, postA[:, k], postA[:, -1], pB, postB[:, k], postB[:, -1], cf, 1e-12)
        row = dict(h='inf' if h == math.inf else str(hs[k]), F_new=new[0], F_old=old[0], tie_new=new[2], tie_old=old[2],
                   B=old[1] - new[1])
        if h != math.inf:
            row.update(h_kappa=float(hs[k] / kappa), z_pred_first_order=100 * (h * s * (old[0] - new[0]) + old[1] - new[1])
                       / (h * r_min + (Eb if a_inf else 0.0)))
        per_h.append(row)
    inf = per_h[-1]
    T = {n: ch.T_int for n, ch in dict(A_stay=Ast, A_switch=Asw, B_stay=Bst, B_switch=Bsw).items()}
    return dict(namespace='ctmc-v1', kind='M0_and_stationary_only', parameters=[str(x) for x in (lamA, lamB, u, kappa, c)],
                N=dict(A=NA, B=NB), r_stay=r_stay, r_switch=r_switch, s=s, r_min=r_min, x=float((lamB - lamA) / u),
                delta=float(lamB - lamA), T_int=T, T_int_max=max(T.values()), beta_C=Eb if a_inf else 0.0,
                z_inf=100 * s * (inf['F_old'] - inf['F_new']) / r_min, a_inf_switch=bool(a_inf),
                M0_regret_new_pred=100 * abs(s) * ((1 - inf['F_new']) if a_inf else inf['F_new']) / r_min,
                M0_regret_old_pred=100 * abs(s) * ((1 - inf['F_old']) if a_inf else inf['F_old']) / r_min, h=per_h)
