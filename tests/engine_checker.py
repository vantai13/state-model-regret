"""Doan Van Tai — independent checker; supplied L3.2 Part4 §8.2.

No import from the engine/core or shared aggregation helpers.
"""
"""Checker độc lập: liệt kê mọi cặp (x_A, x_B). KHÔNG import factorial_core."""
from fractions import Fraction as F
from itertools import product


def brute(A, B):
    rows = []
    for (pa, da, ha, ja, ga), (pb, db, hb, jb, gb) in product(
            zip(A.p, A.d, A.dh, A.jst, A.group), zip(B.p, B.d, B.dh, B.jst, B.group)):
        rows.append(dict(p=pa * pb, st=ja + jb, sw=ja + jb + da + db, dh=ha + hb, gA=ga, gB=gb))
    Ed = sum(r['p'] * (r['sw'] - r['st']) for r in rows)
    Edh = sum(r['p'] * r['dh'] for r in rows)
    pick = lambda r, switch: r['sw'] if switch else r['st']
    L00 = sum(r['p'] * pick(r, Edh < 0) for r in rows)
    L01 = sum(r['p'] * pick(r, Ed < 0) for r in rows)
    L10 = sum(r['p'] * pick(r, r['dh'] < 0) for r in rows)
    L11 = sum(r['p'] * min(r['st'], r['sw']) for r in rows)
    groups = {}
    for r in rows:                                   # D22 theo định nghĩa: posterior trên nhóm (qA,qB)
        g = groups.setdefault((r['gA'], r['gB']), [])
        g.append(r)
    Lcb = F(0)
    for g in groups.values():
        P = sum(r['p'] for r in g)
        switch = sum(r['p'] * r['dh'] for r in g) / P < 0
        Lcb += sum(r['p'] * pick(r, switch) for r in g)
    return dict(L={'00': L00, '01': L01, '10': L10, '11': L11, 'cb0': Lcb},
                p_sw=sum(r['p'] for r in rows if r['sw'] < r['st']), rows=rows)
