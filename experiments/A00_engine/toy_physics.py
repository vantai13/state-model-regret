"""Doan Van Tai — supplied L3.2 Part4 §8.3, adapted imports.

Fraction reference adapter for synthetic plants only.
"""
"""Tầng vật lý cho plant TOY, chỉ dùng hàm tham chiếu Fraction đã có trong repo.

Scientific purpose: dựng bảng Side từ một plant nhỏ để engine tái lập golden Phase 1.
Không dùng cho ô lưới (ô lưới đi qua cells.py + kernel native).
"""
from fractions import Fraction as F
from smr.exact import value_backward
from smr.idle_gap import weighted_idle, mean_weighted_idle
from experiments.A00_engine.factorial_core import Side


def toy_side(states, rates, P, c, u_stay, u_switch, H, dt=F(1)):
    """states: list of (prob, q, mode). Trả Side và (J_Sw thật) để kiểm chéo."""
    cols = dict(p=[], d=[], dh=[], jst=[], group=[]); jsw = []
    for p, q, m in states:
        w1 = {a: weighted_idle(q, m, rates, x, c, H, P, dt) for a, x in (('St', u_stay), ('Sw', u_switch))}
        w0 = {a: mean_weighted_idle(q, m, rates, x, c, H, P, dt) for a, x in (('St', u_stay), ('Sw', u_switch))}
        if not all(w0[a] <= w1[a] for a in w1):
            raise AssertionError('Jensen: W^M0 <= W^M1 bị vi phạm')
        cols['p'].append(F(p)); cols['d'].append(w1['Sw'] - w1['St']); cols['dh'].append(w0['Sw'] - w0['St'])
        cols['jst'].append(value_backward(u_stay, H, c, rates, P, [q], dt)[q, m]); cols['group'].append(q)
        jsw.append(value_backward(u_switch, H, c, rates, P, [q], dt)[q, m])
    return Side(**{k: tuple(v) for k, v in cols.items()}), tuple(jsw)
