"""Golden and failure-mode checks; full enumeration runs via the lesson CLI."""
from fractions import Fraction as F

import pytest

from experiments.lessons.l2_2_voi_mapping import invariants, toy_table
from experiments.lessons.l2_3_p11 import p11_toy, value_of_disclosure


def test_v1_from_queue_and_nonmonotone_state_repair():
    t = toy_table([2, 3], [1, 6], [0, 1])
    assert t["J"]["hi"] == {"St": F(3), "Sw": F(5, 2)}
    assert t["J0"]["hi"] == {"St": F(2), "Sw": F(5, 2)}
    assert t["L"] == {"00": F(5, 4), "10": F(3, 2), "01": F(5, 4), "11": F(5, 4)}
    assert t["con"]["GS"] == F(-1, 4)
    assert t["RP"] - t["WS"] == F(1, 8)
    assert all(invariants(t).values())


def test_v2_separates_global_EV_from_belief_averaged_M0():
    t = toy_table([0, 5], [0, 2], [3, 6])
    assert t["con"]["GM"] == F(1, 4)
    assert t["EEV"] - t["RP"] == t["con"]["GMgS1"] == 0
    changed = toy_table([0, 5], [0, 2], [3, 6], mean_state=True)
    assert changed["L"]["00"] != t["L"]["00"]


def test_wrong_belief_extra_loss_is_true_law_decision_loss():
    t = toy_table([0, 5], [0, 2], [3, 6], belief_hi=F(3, 4))
    assert t["con"]["GSgM1"] == F(1, 2)
    assert t["EVPPI"] == F(1, 4)
    assert t["L"]["01"] - t["RP"] == F(1, 4)
    assert not invariants(t)["I1"]


def test_independent_VSS_catches_ignored_mode_while_reused_policy_does_not():
    t = toy_table([2, 3], [1, 6], [0, 1], m0_ignores_mode=True)
    assert not invariants(t)["I2"]
    assert t["con"]["GMgS1"] == t["EVSS_taut"]


def test_tie_switch_is_equivalent_control_for_VOI():
    args = ([0, 1], [0, 1], [0, 1])
    assert all(invariants(toy_table(*args, tie="Sw")).values())
    assert toy_table(*args)["con"]["GSgM1"] == toy_table(*args, tie="Sw")["con"]["GSgM1"]


def test_global_EV_may_exceed_WS_without_violating_Jensen_to_RP():
    t = toy_table([1, 2], [0, 1], [1, 3])
    assert t["EV"] == F(1, 4) > t["WS"] == F(1, 8)
    assert t["EV"] <= t["RP"]


def test_point_prior_zero_VOI_does_not_imply_zero_true_loss():
    wrong = p11_toy([(F(0), F(1))])
    right = p11_toy([(F(1), F(1))])
    assert wrong["EVPI_delta"] == right["EVPI_delta"] == 0
    assert wrong["true_regret"] == F(1, 2)
    assert right["true_regret"] == 0


def test_correlated_signal_uses_conditional_distribution():
    J = {"hi": {"St": F(2), "Sw": F(3, 2)}, "lo": {"St": F(7, 2), "Sw": F(9, 2)}}
    weights = {"hi": F(1, 2), "lo": F(1, 2)}
    assert value_of_disclosure(J, weights, {"hi": 0, "lo": 1})["value"] == F(1, 4)
    assert value_of_disclosure(J, weights, {"hi": 0, "lo": 0})["value"] == 0


def test_invalid_prior_is_rejected():
    with pytest.raises(ValueError):
        p11_toy([(F(0), F(3, 4))])
