"""Doan Van Tai — supplied nine golden/cross-check tests, adapted imports.

Expected outputs recorded before implementation; random seed 20261027.
"""
import random
from fractions import Fraction as F
from experiments.A00_engine.factorial_core import Side, aggregate
from experiments.A00_engine.toy_physics import toy_side
from tests.engine_checker import brute
from smr.single_observation import statistics
from tests import golden_phase1 as g

h = F(1, 2)
def side(p, d, dh, jst=None, group=None):
    n = len(p); return Side(tuple(map(F, p)), tuple(map(F, d)), tuple(map(F, dh)),
                            tuple(map(F, jst or [0] * n)), tuple(group or range(n)))

def canonical():
    """Ví dụ chuẩn Phase 1: H=2, c=3, u=2, A nền 1, B on/off 5/0, keep 1/2, D đều trên 4 state."""
    keep = {'on': {'on': h, 'off': h}, 'off': {'on': h, 'off': h}}
    A, jswA = toy_side([(1, 2, 'x')], {'x': 1}, {'x': {'x': 1}}, 3, 2, 0, 2)
    B, jswB = toy_side([(F(1, 4), q, m) for q in (2, 0) for m in ('on', 'off')],
                       {'on': 5, 'off': 0}, keep, 3, 0, 2, 2)
    return A, B, jswA, jswB

E7 = (side([h, h], [1, 3], ['1/2', '3/2'], group=[1, 4]),
      side([h, h], [-4, '-1/2'], [-2, '-3/4'], group=[0, 0]))

def test_idle_identity_cross_check():          # loại 3: hai đường tính độc lập
    A, B, jswA, jswB = canonical()
    for i, (jb, sb) in enumerate(zip(B.jst, jswB)):
        assert (jswA[0] + sb) - (A.jst[0] + jb) == A.d[0] + B.d[i]

def test_canonical_golden_from_physics():       # golden Phase 1, dựng lại từ vật lý
    r = aggregate(*canonical()[:2])
    assert r['L'] == {**{k: v for k, v in g.FACTORIAL_MEANS.items()}, 'cb0': r['L']['cb0']}
    G = r['G']
    assert (G['G_S'], G['G_M'], G['Gamma'], G['G_S_M1'], G['G_M_S1']) == (F(9, 8), F(1, 4), F(-1, 4), F(7, 8), 0)
    assert (G['F'], G['V']) == (F(3, 8), F(3, 4))  # L1.6: freshness + mode visibility

def test_E7_golden():
    r = aggregate(*E7)                          # jst = 0 nên K = 0
    assert [r['L'][k] for k in ('00', '01', '10', '11', 'cb0')] == [F(-1, 4), F(-1, 4), F(-7, 8), -1, F(-5, 8)]
    assert (r['G']['F'], r['G']['V'], r['p_sw']) == (F(3, 8), F(1, 4), h)

def test_tie_goes_to_stay():                    # E4: một state có Δ = 0
    r = aggregate(side([h, h], [1, 3], [1, 3]), side([h, h], [-4, -1], [-4, -1]))
    assert r['p_sw'] == h

def test_cell_level_tie_goes_to_stay():         # E_D δ̂ = 0 đúng bằng 0, nhưng E_D Δ = -1
    r = aggregate(side([1], [1], [1]), side([1], [-2], [-1]))
    assert (r['a00'], r['L']['00']) == (0, 0)

def test_D10_mean_of_rollouts():                 # belief q_B ∈ {0,4}: E δ̂ = -1/4 (rollout từ q=2 sẽ cho +1/4)
    B, _ = toy_side([(h, 0, 'x'), (h, 4, 'x')], {'x': 2}, {'x': {'x': 1}}, 3, 0, 2, 1)
    r = aggregate(side([1], ['1/4'], ['1/4']), B)
    assert (r['E_delta_hat'], r['a00']) == (F(-1, 4), 1)

def test_T01_checker_agrees():                  # checker độc lập của repo, cấp ô
    A, B = canonical()[:2]; b = brute(A, B)
    rows = [(r['p'], r['st'], r['sw'], 0, r['dh']) for r in b['rows']]   # M0: chỉ hiệu số có nghĩa
    s, r = statistics(rows), aggregate(A, B)
    assert (s['L00'] - s['L01'], s['G_S_given_M1']) == (r['G']['G_M'], r['G']['G_S_M1'])

def test_metamorphic_S0_sees_only_mean():       # đổi chỗ δ̂ giữa hai state cùng xác suất
    A, B = E7; r1 = aggregate(A, B)
    B2 = Side(B.p, B.d, B.dh[::-1], B.jst, B.group); r2 = aggregate(A, B2)
    assert r1['L']['00'] == r2['L']['00'] and r1['L']['10'] != r2['L']['10']

def _random_side(rng, which, n):
    w = [rng.randint(1, 4) for _ in range(n)]; p = [F(x, sum(w)) for x in w]
    s = 1 if which == 'A' else -1
    v = lambda: s * F(rng.randint(0, 8), rng.choice([1, 2, 4]))
    return Side(tuple(p), tuple(v() for _ in p), tuple(v() for _ in p),
                tuple(F(rng.randint(0, 20)) for _ in p), tuple(rng.randint(0, 2) for _ in p))

def test_brute_force_random():                  # loại 3: dạng tách = liệt kê, 300 ô ngẫu nhiên
    rng = random.Random(20261027)
    for _ in range(300):
        A, B = _random_side(rng, 'A', rng.randint(1, 5)), _random_side(rng, 'B', rng.randint(1, 5))
        r, b = aggregate(A, B), brute(A, B)
        assert r['L'] == b['L'] and r['p_sw'] == b['p_sw']
        assert r['L']['11'] <= min(r['L'][k] for k in ('00', '01', '10', 'cb0'))   # loại 2
        assert r['G']['G_S_M1'] == min(r['E_pos'], r['E_neg'])                       # T01 (c)
        assert r['G']['G_M'] <= abs(r['bias'])                                       # T01 (b)
