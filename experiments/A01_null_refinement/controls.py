"""Doan Van Tai — changed-information/model controls, true scoring unchanged.

C3's pipeline 11 is deliberately NOT the D15 true oracle. Its benchmark is
reported separately; no claim that its original R11 is zero is made.
"""
from experiments.A00_engine.factorial_core import _cut_sum


def controlled(A, B, kind):
    if kind not in ('C2', 'C3'):
        raise ValueError(kind)
    E = lambda s, col: sum(p * v for p, v in zip(s.p, col))
    K = E(A, A.jst) + E(B, B.jst)
    Ed = E(A, A.d) + E(B, B.d)
    Eh = E(A, A.dh) + E(B, B.dh)
    L = {}
    for state in (0, 1):
        for model in (0, 1):
            keyA, keyB = (A.dh, B.dh) if model == 0 or kind == 'C3' else (A.d, B.d)
            if state == 1 or kind == 'C2':
                _, gain = _cut_sum(keyA, A.d, A.p, keyB, B.d, B.p)
            else:
                gap = Eh if model == 0 or kind == 'C3' else Ed
                gain = Ed * int(gap < 0)
            L[str(state) + str(model)] = K + gain
    # Group the factorial differences to retain equality when policies coincide.
    G = dict(G_S=L['00'] - L['10'], G_M=L['00'] - L['01'],
             G_SM=L['00'] - L['11'], G_S_M1=L['01'] - L['11'],
             G_M_S1=L['10'] - L['11'],
             Gamma=(L['10'] - L['00']) + (L['01'] - L['11']))
    if kind == 'C2':
        ok = G['G_S'] == G['G_S_M1'] == G['Gamma'] == 0 and G['G_M'] == G['G_M_S1']
    else:
        ok = G['G_M'] == G['G_M_S1'] == G['Gamma'] == 0
    return dict(L=L, G=G, exact_identity_pass=ok)


def enumerated_oracle(A, B):
    """Independent Cartesian toy checker: no cuts or aggregate imports/calls."""
    cost = A.p[0] * 0
    switch_mass = cost
    for pa, da, ja in zip(A.p, A.d, A.jst):
        for pb, db, jb in zip(B.p, B.d, B.jst):
            st, sw = ja + jb, ja + jb + da + db
            cost += pa * pb * min(st, sw)
            switch_mass += pa * pb * int(sw < st)
    return cost, switch_mass
