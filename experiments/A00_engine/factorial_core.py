"""Doan Van Tai — L3.2 experimental engine, not promoted to src.

Core adapted from supplied Part4 §8.1; additions: validation, diagnostics,
independent mathematical checks. No grid outcomes authorized here.
"""
"""Tầng sổ sách của engine exact (L3.2): ghép hai bảng một phía thành bốn L.

Scientific purpose: tính L00, L01, L10, L11, L_cb0 (D22) và sáu contrast D19
    từ hai bảng tách được, KHÔNG dựng tích D_A x D_B.
Used by: evaluate_cell (A01, A04, A05-T); test golden Phase 1, E2, E7.
Metric: packet·s. Bản này dùng Fraction (chính xác) cho toy và golden.
"""
from bisect import bisect_left
from dataclasses import dataclass
from fractions import Fraction as F
from numbers import Rational
import math

import numpy as np


@dataclass(frozen=True)
class Side:
    """Bảng một phía. Mỗi dòng là một state x_l = (q_l, m_l) của queue l."""
    p: tuple      # D_l(x_l)
    d: tuple      # δ_l: thành phần gap thật (M1)
    dh: tuple     # δ̂_l: thành phần gap theo M0
    jst: tuple    # J_l(Stay; x_l) thật
    group: tuple  # mã backlog q_l, dùng cho D22 (giấu mode)

    bounds: dict | None = None

    def check(self, which):
        if which not in ('A', 'B'):
            raise ValueError('which must be A or B')
        n = len(self.p)
        if not all(len(v) == n for v in (self.d, self.dh, self.jst, self.group)):
            raise ValueError('cột lệch độ dài')
        exact = all(isinstance(x, Rational) for x in self.p)
        total = sum(self.p)
        if not all(math.isfinite(x) for col in (self.p, self.d, self.dh, self.jst) for x in col):
            raise ValueError('finite inputs required')
        if any(x <= 0 for x in self.p) or (total != 1 if exact else abs(total - 1) > 1e-12):
            raise ValueError('D_l phải dương trên support và cộng bằng 1')
        sign = (lambda v: v >= 0) if which == 'A' else (lambda v: v <= 0)
        if not all(sign(v) for v in self.d + self.dh):
            raise ValueError(f'vi phạm dấu δ_{which} (Part 2 §7.3)')


def _cut_sum(A_key, A_val, A_p, B_key, B_val, B_p):
    """Σ_a p_a Σ_{b: keyA+keyB<0} p_b (valA+valB), và khối lượng tương ứng.

    Sắp B theo KEY (cái dùng để quyết định), cộng dồn VAL (cái dùng để chấm).
    Bất đẳng thức chặt: hòa thì Stay (D16).
    """
    order = sorted(range(len(B_key)), key=lambda i: B_key[i])
    keys = [B_key[i] for i in order]
    zero = B_p[0] * 0
    cum_p, cum_pv = [zero], [zero]
    for i in order:
        cum_p.append(cum_p[-1] + B_p[i])
        cum_pv.append(cum_pv[-1] + B_p[i] * B_val[i])
    mass = value = zero
    for ka, va, pa in zip(A_key, A_val, A_p):
        k = bisect_left(keys, -ka)              # số phần tử < -ka
        mass += pa * cum_p[k]
        value += pa * (va * cum_p[k] + cum_pv[k])
    return mass, value


def _by_backlog(s):
    """Gộp mode trong cùng backlog: posterior D(m|q), trung bình δ và δ̂ (D22, D10)."""
    acc = {}
    for p, d, dh, g in zip(s.p, s.d, s.dh, s.group):
        zero = s.p[0] * 0
        P, Sd, Sdh = acc.get(g, (zero, zero, zero))
        acc[g] = (P + p, Sd + p * d, Sdh + p * dh)
    P = tuple(v[0] for v in acc.values())
    return P, tuple(v[1] / v[0] for v in acc.values()), tuple(v[2] / v[0] for v in acc.values())


def aggregate(A, B):
    A.check('A'); B.check('B')
    E = lambda s, col: sum(p * v for p, v in zip(s.p, col))
    K = E(A, A.jst) + E(B, B.jst)                  # E_D J(Stay): không cần ghép
    Ed, Edh = E(A, A.d) + E(B, B.d), E(A, A.dh) + E(B, B.dh)
    a00, a01 = int(Edh < 0), int(Ed < 0)           # S0: MỘT action cho cả ô (T01)
    p_sw, neg = _cut_sum(A.d, A.d, A.p, B.d, B.d, B.p)     # E[Δ·1(Δ<0)] = -EΔ⁻
    # Direct positive-part cut: an empty sum stays exactly zero on WD cells.
    # Subtracting E_delta - negative_part would lose that structural guarantee.
    _, minus_pos = _cut_sum(tuple(-v for v in A.d), tuple(-v for v in A.d), A.p,
                            tuple(-v for v in B.d), tuple(-v for v in B.d), B.p)
    pos = -minus_pos
    _, sw10 = _cut_sum(A.dh, A.d, A.p, B.dh, B.d, B.p)     # quyết theo δ̂, chấm bằng δ
    PA, dA, dhA = _by_backlog(A); PB, dB, dhB = _by_backlog(B)
    _, swcb = _cut_sum(dhA, dA, PA, dhB, dB, PB)           # D22: biết q, giấu mode
    L = {'00': K + a00 * Ed, '01': K + a01 * Ed, '10': K + sw10, '11': K + neg, 'cb0': K + swcb}
    G = dict(G_S=L['00'] - L['10'], G_M=L['00'] - L['01'], G_SM=L['00'] - L['11'],
             Gamma=L['10'] + L['01'] - L['00'] - L['11'],
             G_S_M1=min(pos, -neg), G_M_S1=L['10'] - L['11'],
             F=L['00'] - L['cb0'], V=L['cb0'] - L['10'])
    result = dict(L=L, G=G, a00=a00, a01=a01, E_delta=Ed, E_delta_hat=Edh, bias=Edh - Ed,
                  E_pos=pos, E_neg=-neg, p_sw=p_sw, C_ref=L['11'])
    result['R'] = {k: value - L['11'] for k, value in L.items()}
    eA = tuple(h - d - (Edh - Ed) for h, d in zip(A.dh, A.d))
    eB = tuple(h - d for h, d in zip(B.dh, B.d))
    modelA = tuple(h - d for h, d in zip(A.dh, A.d))
    _, model_negative = _cut_sum(modelA, modelA, A.p, eB, eB, B.p)
    result['E_abs_e_M'] = E(A, modelA) + E(B, eB) - 2 * model_negative
    _, negative = _cut_sum(eA, eA, A.p, eB, eB, B.p)
    result['E_abs_I_delta'] = E(A, eA) + E(B, eB) - 2 * negative
    levels = (F(1, 2), F(9, 10), F(99, 100))
    result['quantiles_abs_delta'] = {str(t): _abs_quantile(A.d, A.p, B.d, B.p, t) for t in levels}
    result['quantiles_abs_I_delta'] = {str(t): _abs_quantile(eA, A.p, eB, B.p, t) for t in levels}
    exact = all(isinstance(v, Rational) for v in (*A.p, *B.p, *A.d, *B.d, *A.dh, *B.dh))
    if exact:
        if not all(L['11'] <= L[k] for k in ('00', '01', '10', 'cb0')):
            raise ArithmeticError('oracle is not the minimum')
        if L['01'] - L['11'] != min(result['E_pos'], result['E_neg']):
            raise ArithmeticError('independent T01 positive/negative-parts check failed')
        if not 0 <= G['G_M'] <= abs(result['bias']):
            raise ArithmeticError('T01 bias bound failed')
        if not 0 <= G['G_M_S1'] <= result['E_abs_e_M']:
            raise ArithmeticError('statewise model-error bound failed')
    return result


def _abs_quantile(a, pa, b, pb, target):
    """Weighted quantile of |a+b| using CDF cuts and attainable successors.

    No Cartesian array. For rational inputs the returned support value is exact.
    Float quantiles describe nominal tables; bounds live in precision.py.
    """
    from bisect import bisect_right
    order = sorted(range(len(b)), key=lambda i: b[i])
    keys = [b[i] for i in order]
    cp = [pb[0] * 0]
    for i in order:
        cp.append(cp[-1] + pb[i])
    def cdf(t):
        return sum(p * (cp[bisect_right(keys, t - x)] - cp[bisect_left(keys, -t - x)])
                   for x, p in zip(a, pa))
    def successor(t):
        candidates = []
        for x in a:
            if t < 0:
                k = bisect_left(keys, -x)
                for j in (k - 1, k):
                    if 0 <= j < len(keys):
                        candidates.append(abs(x + keys[j]))
            else:
                k = bisect_right(keys, t - x)
                if k < len(keys):
                    candidates.append(abs(x + keys[k]))
                k = bisect_left(keys, -t - x) - 1
                if k >= 0:
                    candidates.append(abs(x + keys[k]))
        return min(candidates) if candidates else None
    total = sum(pa) * sum(pb)
    target = ((np.longdouble(target.numerator) / target.denominator) * total
              if isinstance(total, np.floating) and isinstance(target, F) else target * total)
    lo = a[0] * 0 - 1
    hi = max(abs(min(a) + min(b)), abs(max(a) + max(b)))
    for _ in range(4096):
        candidate = successor(lo)
        if candidate is None:
            return hi
        if cdf(candidate) >= target:
            return candidate
        mid = (max(0, lo) + hi) / 2
        if mid == lo or mid == hi:
            return hi
        if cdf(mid) >= target:
            hi = mid
        else:
            lo = mid
    raise ArithmeticError('quantile did not separate; report an interval instead')
