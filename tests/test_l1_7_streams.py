"""Doan Van Tai — Tests L1.7 — "cùng seed" so với primitive stream, máy dò CRN (đẳng thức 2), rò tương lai.

Seed: DEMO_ROOT (sổ seed, dòng "lesson-demo", chỉ để dạy). Test kiểm TÍNH CHẤT, không chép cứng số ngẫu nhiên.
"""
from fractions import Fraction as F
import numpy as np
import pytest
from experiments.lessons.l1_3_expected_cost import CANON, expected_cost, oracle
from experiments.lessons.l1_7_streams import (
    DEMO_ROOT, PATH, ROLE, background_B, future_rng, identity2_residual,
    mk_action, mode_path, naive_two_actions, path_costs, predictor_rng,
    primitive_two_actions, stream,
)

TH6 = dict(CANON, H=6)
TH3 = dict(CANON, H=3)
XB = (2, 2, "off")
N = 2000


def same_key_seed(i):
    """Seed mà cách ngây thơ dùng: CÙNG khóa với stream future của path B ở episode i."""
    return np.random.SeedSequence(DEMO_ROOT, spawn_key=(ROLE["future"], i, PATH["B"]))


# ---------- Part B của bài lý thuyết: cuộn băng tự đặt (golden, không ngẫu nhiên) ----------

def test_tape_example_from_part1():
    tape = [0.31, 0.72, 0.05, 0.88, 0.46, 0.63]
    b_st = background_B(XB, TH6, tape[0:5])
    b_sw = background_B(XB, TH6, tape[1:6])                 # Switch rút trước một số
    assert mode_path("off", tape[0:5], F(1, 2), F(1, 2)) == ["off", "off", "on", "on", "off", "off"]
    assert mode_path("off", tape[1:6], F(1, 2), F(1, 2)) == ["off", "on", "on", "off", "off", "on"]
    naive = path_costs(XB, TH6, b_st, b_sw)
    assert (naive["Stay"][0], naive["Switch"][0]) == (19, 41)
    assert identity2_residual(naive) == 22 - 7                # đẳng thức 2 gãy
    for bB, (st, sw) in ((b_st, (19, 26)), (b_sw, (21, 41))):
        crn = path_costs(XB, TH6, bB, bB)
        assert (crn["Stay"][0], crn["Switch"][0]) == (st, sw)
        assert identity2_residual(crn) == 0


# ---------- "cùng seed" so với primitive ----------

def test_naive_differs_only_because_of_the_extra_draw():
    differ = 0
    for i in range(N):
        prim, _ = primitive_two_actions(DEMO_ROOT, i, XB, TH6, 1)
        st0, sw0 = naive_two_actions(same_key_seed(i), XB, TH6, 0)
        st1, sw1 = naive_two_actions(same_key_seed(i), XB, TH6, 1)
        assert st0 == sw0 == st1 == prim                     # đối chứng: không rút thêm thì trùng
        differ += sw1 != st1
    assert differ / N > 0.9                                  # rút thêm MỘT số: gần như luôn lệch


@pytest.mark.parametrize("extra", [0, 1, 7])
def test_primitive_gives_identical_futures_whatever_the_branch_draws(extra):
    for i in range(N):
        st, sw = primitive_two_actions(DEMO_ROOT, i, XB, TH6, extra)
        assert st == sw == primitive_two_actions(DEMO_ROOT, i, XB, TH6, 0)[0]


def test_draws_on_other_streams_do_not_move_B():
    for i in range(200):
        before = future_rng(DEMO_ROOT, i, "B").random(5)
        future_rng(DEMO_ROOT, i, "A").random(50)             # path A bỗng có traffic ngẫu nhiên
        predictor_rng(DEMO_ROOT, i).random(16)               # M_16 lấy mẫu
        assert np.array_equal(before, future_rng(DEMO_ROOT, i, "B").random(5))
    shared = np.random.default_rng(same_key_seed(0))         # đối chứng: MỘT generator cho cả A và B
    shared.random(5)                                         # A rút trước
    assert not np.array_equal(shared.random(5), future_rng(DEMO_ROOT, 0, "B").random(5))


def test_episode_replay_and_order_independence():
    nested = (np.random.SeedSequence(DEMO_ROOT, spawn_key=(ROLE["future"],))
              .spawn(38)[37].spawn(2)[PATH["B"]])
    assert np.array_equal(np.random.default_rng(nested).random(5),
                          future_rng(DEMO_ROOT, 37, "B").random(5))
    forward = [future_rng(DEMO_ROOT, i, "B").random(5) for i in range(20)]
    backward = [future_rng(DEMO_ROOT, i, "B").random(5) for i in reversed(range(20))][::-1]
    assert all(np.array_equal(a, b) for a, b in zip(forward, backward))


def test_stream_key_refuses_labels():
    with pytest.raises(TypeError):
        stream(DEMO_ROOT, "future", 0, "Switch")
    with pytest.raises(KeyError):
        stream(DEMO_ROOT, "cell_00", 0)


# ---------- Máy dò CRN và phương sai ----------

def test_identity2_detector_zero_under_crn_nonzero_under_naive():
    broken = 0
    for i in range(N):
        assert identity2_residual(path_costs(XB, TH6, *primitive_two_actions(DEMO_ROOT, i, XB, TH6, 1))) == 0
        broken += identity2_residual(path_costs(XB, TH6, *naive_two_actions(same_key_seed(i), XB, TH6, 1))) != 0
    assert broken / N > 0.9


def test_naive_is_unbiased_but_noisier():
    exact = float(expected_cost(XB, "Switch", TH6) - expected_cost(XB, "Stay", TH6))   # 145/16
    d = {"prim": [], "naive": []}
    for i in range(N):
        for name, pair in (("prim", primitive_two_actions(DEMO_ROOT, i, XB, TH6, 1)),
                           ("naive", naive_two_actions(same_key_seed(i), XB, TH6, 1))):
            c = path_costs(XB, TH6, *pair)
            d[name].append(c["Switch"][0] - c["Stay"][0])
    for v in d.values():
        v = np.array(v, float)
        assert abs(v.mean() - exact) <= 3 * v.std(ddof=1) / np.sqrt(N)   # cả hai không lệch
    var_prim, var_naive = (np.var(d[k], ddof=1) for k in ("prim", "naive"))
    assert abs(var_prim - 117.4961) / 117.4961 < 0.15        # khớp phương sai CRN chính xác (Part 1, A5)
    assert var_naive > 2 * var_prim                          # mất ghép cặp: ồn hơn nhiều


def test_sampler_matches_exact_J_on_asymmetric_chain():
    # p ≠ s: sai quy ước "u < P(giữ)" sẽ đổi phân phối. Với p = s = ½ thì không lộ.
    th = dict(CANON, H=4, p_onon=F(3, 4), p_offoff=F(1, 2))
    for x in [(2, 2, "on"), (2, 0, "off")]:
        for a in ("Stay", "Switch"):
            c = np.array([path_costs(x, th, *primitive_two_actions(DEMO_ROOT, i, x, th, 0))[a][0]
                          for i in range(N)], float)
            assert abs(c.mean() - float(expected_cost(x, a, th))) <= 3 * c.std(ddof=1) / np.sqrt(N), (x, a)


# ---------- Rò tương lai ----------

def _measured_costs(x, th, n):
    """Mỗi episode: evaluator rút MỘT tương lai từ stream future rồi chấm ba ô."""
    a_star = oracle(x, th)[0]
    out = {"oracle": [], "leak": [], "honest": []}
    for i in range(n):
        w = background_B(x, th, future_rng(DEMO_ROOT, i, "B").random(th["H"] - 1))
        C = {a: v[0] for a, v in path_costs(x, th, w, w).items()}
        out["oracle"].append(C[a_star])
        out["leak"].append(C[mk_action(x, th, future_rng(DEMO_ROOT, i, "B"), 1)])   # cùng khóa với future
        out["honest"].append(C[mk_action(x, th, predictor_rng(DEMO_ROOT, i), 1)])
    return {k: np.array(v, float) for k, v in out.items()}


def test_leaky_mk_beats_the_oracle_honest_mk_does_not():
    m = _measured_costs(XB, TH3, N)              # chính xác: oracle 31/4, rò 13/2, đúng luật 65/8
    assert np.all(m["leak"] <= m["oracle"])      # rò: không bao giờ thua oracle, ở MỌI episode
    gap = m["oracle"] - m["leak"]
    assert gap.mean() > 3 * gap.std(ddof=1) / np.sqrt(N)
    excess = m["honest"] - m["oracle"]
    assert excess.mean() >= -3 * excess.std(ddof=1) / np.sqrt(N)
    assert np.any(excess < 0)                    # nhưng TỪNG episode vẫn có thể "thắng" vì nhiễu


def test_canonical_example_is_blind_to_the_leak():
    for x in [(2, 2, "on"), (2, 2, "off"), (2, 0, "on"), (2, 0, "off")]:
        m = _measured_costs(x, CANON, 300)
        assert np.array_equal(m["leak"], m["oracle"]), x
