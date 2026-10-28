# Người phụ trách: Doan Van Tai. Golden reference theo ba phần lesson được cung cấp.
# Chỉ toy hữu hạn; không import/call engine pilot. cb0 vắng khi chưa khai báo q.
"""Golden toy cho T07 (L3R.2). Mọi đáp án là phân số và tính tay được."""
from fractions import Fraction as F
import random

STAY, SWITCH = 0, 1


def act(gap):                                   # D16: chỉ Switch khi gap < 0; hòa -> Stay
    return SWITCH if gap < 0 else STAY


def cost(P, a, x):                              # J(a;x) = J(Stay;x) + 1[a=Switch]·Δ(x)
    return P['J'][x] + (P['Delta'][x] if a == SWITCH else 0)


def cells(P):
    """P: p[y], D[y][x], J[x]=J(Stay;x), Delta[x] (đúng), Dhat[x] (M0 theo state); q[x] tùy chọn (D22)."""
    L = dict.fromkeys(('00', '01', '10', '11'), F(0))
    if 'q' in P:
        L['cb0'] = F(0)
    for y, py in P['p'].items():
        Dy = P['D'][y]
        a00 = act(sum(w * P['Dhat'][x] for x, w in Dy.items()))    # S0: MỘT action cho cả y
        a01 = act(sum(w * P['Delta'][x] for x, w in Dy.items()))
        for x, w in Dy.items():
            L['00'] += py * w * cost(P, a00, x)
            L['01'] += py * w * cost(P, a01, x)
            L['10'] += py * w * cost(P, act(P['Dhat'][x]), x)        # S1: theo từng state
            L['11'] += py * w * min(cost(P, STAY, x), cost(P, SWITCH, x))
        for q in sorted({P['q'][x] for x in Dy}) if 'q' in P else ():  # D22: thêm backlog hiện tại, giấu mode
            grp = {x: w for x, w in Dy.items() if P['q'][x] == q}
            a = act(sum(w * P['Dhat'][x] for x, w in grp.items()))
            L['cb0'] += py * sum(w * cost(P, a, x) for x, w in grp.items())
    return L


def contrasts(L):
    G = dict(GS=L['00'] - L['10'], GM=L['00'] - L['01'], GSM=L['00'] - L['11'],
             GS_M1=L['01'] - L['11'], GM_S1=L['10'] - L['11'])
    if 'cb0' in L:
        G.update(F=L['00'] - L['cb0'], V=L['cb0'] - L['10'])
    G['Gamma'] = G['GSM'] - G['GS'] - G['GM']
    return G


def prior(P):                                    # Σ_y p(y) D(x|y)
    out = {}
    for y, py in P['p'].items():
        for x, w in P['D'][y].items():
            out[x] = out.get(x, 0) + py * w
    return out


def stakes(P):                                   # σ̄ = E|Δ|
    return sum(w * abs(P['Delta'][x]) for x, w in prior(P).items())


def one_snapshot(**kw):                          # ảnh cũ không phân biệt được state nào
    xs = list(kw['J'])
    return dict(p={'y': F(1)}, D={'y': {x: F(1, len(xs)) for x in xs}}, **kw)


# ------------------------------------------------------------------ Part 1
def test_three_snapshots_GM():
    P = dict(p={1: F(1, 2), 2: F(3, 10), 3: F(1, 5)}, D={y: {y: F(1)} for y in (1, 2, 3)},
             J={1: 0, 2: 0, 3: 0}, Delta={1: F(-3, 2), 2: F(-4, 5), 3: F(9, 10)},
             Dhat={1: F(-3, 5), 2: F(3, 10), 3: F(6, 5)})
    assert contrasts(cells(P))['GM'] == F(6, 25)                      # 0,3 × 0,8


def two_state_part1(a):
    return dict(p={'cao': F(1, 2), 'thap': F(1, 2)},
                D={'cao': {'x1': a, 'x2': 1 - a}, 'thap': {'x1': 1 - a, 'x2': a}},
                J={'x1': 12, 'x2': 8}, Delta={'x1': -2, 'x2': 1}, Dhat={'x1': -1, 'x2': F(-1, 2)})


def test_total_expectation_S1_cells_ignore_age():
    short, long_ = cells(two_state_part1(F(4, 5))), cells(two_state_part1(F(3, 5)))
    assert prior(two_state_part1(F(4, 5))) == prior(two_state_part1(F(3, 5))) == {'x1': F(1, 2), 'x2': F(1, 2)}
    assert (short['01'], long_['01']) == (F(93, 10), F(19, 2))       # hàng S0 đổi theo tuổi ảnh
    assert short['10'] == long_['10'] == F(19, 2) and short['11'] == long_['11'] == 9


# ------------------------------------------------------------------ Part 2
def harm_toy(dhat_x1):
    return one_snapshot(J={'x1': 10, 'x2': 10}, Delta={'x1': 1, 'x2': 1}, Dhat={'x1': dhat_x1, 'x2': 3})


def test_compensating_errors():
    G = contrasts(cells(harm_toy(-2)))
    assert (G['GS'], G['GM'], G['GSM'], G['Gamma'], G['GS_M1'], G['GM_S1']) == \
        (F(-1, 2), 0, 0, F(1, 2), 0, F(1, 2))
    assert stakes(harm_toy(-2)) == 1


def test_sign_of_GS_and_Gamma_flip_with_error_size():
    assert contrasts(cells(harm_toy(F(1, 2))))['GS'] == 0
    G = contrasts(cells(harm_toy(-4)))
    assert (G['GS'], G['Gamma']) == (F(1, 2), F(-1, 2))               # substitutes


def test_tie_goes_to_stay():
    L = cells(one_snapshot(J={'x': 10}, Delta={'x': 1}, Dhat={'x': 0}))
    assert L['10'] == 10                                              # Δ̂ = 0 -> Stay


# ------------------------------------------------------------------ Part 3 (D22)
def test_D22_same_GS_different_story():
    mode = harm_toy(-2) | {'q': {'x1': 5, 'x2': 5}}                   # hai state chỉ khác mode
    fresh = harm_toy(-2) | {'q': {'x1': 8, 'x2': 2}}                  # hai state chỉ khác backlog
    Gm, Gf = contrasts(cells(mode)), contrasts(cells(fresh))
    assert Gm['GS'] == Gf['GS'] == F(-1, 2)
    assert (Gm['F'], Gm['V']) == (0, F(-1, 2))                        # hại do THẤY MODE
    assert (Gf['F'], Gf['V']) == (F(-1, 2), 0)                        # hại do BACKLOG MỚI


def test_D22_parts_can_cancel():
    xs = ('aON', 'aOFF', 'bON', 'bOFF')
    P = one_snapshot(J={x: 10 for x in xs}, Delta=dict(zip(xs, (-1, -1, -1, 1))),
                     Dhat=dict(zip(xs, (-1, 2, -3, 1)))) | {'q': {x: x[0] for x in xs}}
    G = contrasts(cells(P))
    assert (G['GS'], G['F'], G['V']) == (0, F(-1, 2), F(1, 2))


# ------------------------------------------------------------------ identity 1–5 trên plant ngẫu nhiên
def random_plant(rng, ny=3, nx=4):
    joint = {(y, x): F(rng.randint(0, 3)) for y in range(ny) for x in range(nx)}
    for y in range(ny):                                               # mỗi y có khối lượng dương
        if not any(joint[y, x] for x in range(nx)):
            joint[y, 0] = F(1)
    tot = sum(joint.values())
    p = {y: sum(joint[y, x] for x in range(nx)) / tot for y in range(ny)}
    D = {y: {x: joint[y, x] / tot / p[y] for x in range(nx) if joint[y, x]} for y in range(ny)}
    return dict(p=p, D=D, J={x: F(rng.randint(5, 15)) for x in range(nx)},
                Delta={x: F(rng.randint(-3, 3)) for x in range(nx)},
                Dhat={x: F(rng.randint(-4, 4)) for x in range(nx)}, q={x: x // 2 for x in range(nx)},
                pi={x: sum(joint[y, x] for y in range(ny)) / tot for x in range(nx)})


def test_identities_on_random_plants():
    rng = random.Random(20261028)
    for _ in range(500):
        P = random_plant(rng)
        L, s = cells(P), stakes(P)
        G = contrasts(L)
        pi = {x: w for x, w in P['pi'].items() if w}
        assert prior(P) == pi                                                          # Σ p D = π
        assert L['10'] == sum(w * cost(P, act(P['Dhat'][x]), x) for x, w in pi.items())
        assert L['11'] == sum(w * min(cost(P, 0, x), cost(P, 1, x)) for x, w in pi.items())
        for k in ('GSM', 'GS_M1', 'GM_S1', 'GM'):                                      # (1), (2), (5)
            assert 0 <= G[k] <= s
        assert G['Gamma'] == G['GS_M1'] - G['GS'] == G['GM_S1'] - G['GM']              # (3)
        if G['GS'] < 0:                                                                # (4)
            assert G['Gamma'] >= -G['GS'] and G['GM_S1'] >= -G['GS'] + G['GM']
        assert abs(G['GS']) <= s and -s <= G['Gamma'] <= 2 * s                        # (5)
        assert G['F'] + G['V'] == G['GS']                                              # D22
        gm = gs1 = 0                                                                   # T01 theo từng y
        for y, py in P['p'].items():
            Dy = P['D'][y]
            g = sum(w * P['Delta'][x] for x, w in Dy.items())
            h = sum(w * P['Dhat'][x] for x, w in Dy.items())
            gm += py * abs(g) * (act(g) != act(h))
            pos = sum(w * max(P['Delta'][x], 0) for x, w in Dy.items())
            neg = sum(w * max(-P['Delta'][x], 0) for x, w in Dy.items())
            gs1 += py * min(pos, neg)
        assert G['GM'] == gm and G['GS_M1'] == gs1


# Bổ sung để kiểm các giới hạn của lời giải thích, không đổi đáp án 8 test nguồn.
def smoothing_toy(bias):
    ys = range(10)
    return dict(p={y: F(1, 10) for y in ys},
                D={y: {y: F(1)} for y in ys}, J={y: F(10) for y in ys},
                Delta={y: F(2 * y + 1, 20) - F(1, 2) for y in ys},
                Dhat={y: F(2 * y + 1, 20) - F(1, 2) + bias for y in ys})


def test_population_bias_table_and_finite_support_jump():
    for bias, expected in [(F(1, 10), F(1, 200)), (F(1, 5), F(1, 50)),
                           (F(3, 10), F(9, 200)), (F(2, 5), F(2, 25))]:
        assert contrasts(cells(smoothing_toy(bias)))['GM'] == expected == bias ** 2 / 2
    # Y hữu hạn vẫn có bước nhảy tại tie; không suy ra tính trơn tổng quát.
    before = contrasts(cells(smoothing_toy(F(49, 1000))))['GM']
    at_tie = contrasts(cells(smoothing_toy(F(1, 20))))['GM']
    assert (before, at_tie) == (0, F(1, 200))


def test_ratio_of_expectations_is_not_expectation_of_ratios():
    p, gain, cref = (F(1, 2), F(1, 2)), (F(1), F(0)), (F(10), F(90))
    ratio_of_means = sum(w * g for w, g in zip(p, gain)) / sum(w * c for w, c in zip(p, cref))
    mean_of_ratios = sum(w * g / c for w, g, c in zip(p, gain, cref))
    assert (ratio_of_means, mean_of_ratios) == (F(1, 100), F(1, 20))
    assert F(13, 100) / F(30, 100) == F(13, 30)


def test_same_marginal_keeps_S1_cref_and_stakes_fixed():
    reference = two_state_part1(F(4, 5))
    L0, s0 = cells(reference), stakes(reference)
    for a in (F(0), F(1, 2), F(3, 5), F(1)):
        P = two_state_part1(a)
        L = cells(P)
        assert prior(P) == prior(reference)
        assert (L['10'], L['11'], stakes(P)) == (L0['10'], L0['11'], s0)
    assert s0 == F(3, 2)


def test_selected_population_changes_marginal_and_S1():
    P = two_state_part1(F(4, 5))
    selected = P | {'p': {'cao': F(1)}}
    assert prior(selected) == {'x1': F(4, 5), 'x2': F(1, 5)}
    assert (cells(selected)['10'], cells(selected)['11']) == (F(49, 5), F(48, 5))
    assert cells(selected)['11'] != cells(P)['11']


def test_positive_Gamma_does_not_imply_state_harm():
    P = one_snapshot(J={'x1': 10, 'x2': 10}, Delta={'x1': -1, 'x2': 1},
                     Dhat={'x1': 1, 'x2': 1})
    G = contrasts(cells(P))
    assert (G['GS'], G['Gamma']) == (0, F(1, 2))


def test_zero_stakes_zero_contrasts_and_optional_D22():
    P = one_snapshot(J={'x1': 0, 'x2': 0}, Delta={'x1': 0, 'x2': 0},
                     Dhat={'x1': -1, 'x2': 2})
    L = cells(P)
    assert stakes(P) == 0 and L['11'] == 0
    assert 'cb0' not in L and 'F' not in contrasts(L) and 'V' not in contrasts(L)
    assert all(v == 0 for v in contrasts(L).values())
    # 0/0 không định nghĩa; không trả 0%, không dùng epsilon cứu mẫu số.


def test_exact_tie_rule_for_snapshot_and_current_backlog():
    P = one_snapshot(J={'x1': 10, 'x2': 10}, Delta={'x1': 1, 'x2': 1},
                     Dhat={'x1': -1, 'x2': 1}, q={'x1': 2, 'x2': 2})
    L = cells(P)
    assert (L['00'], L['01'], L['cb0']) == (10, 10, 10)
    assert L['10'] == F(21, 2)


def test_tighter_Gamma_bound_from_shared_belief():
    rng = random.Random(20261028)
    for _ in range(500):
        P = random_plant(rng)
        G, s = contrasts(cells(P)), stakes(P)
        assert -s <= G['Gamma'] <= s
