"""Doan Van Tai — lean L3R.7 closure rules (DL-095) on synthetic rows; no engine call."""
from fractions import Fraction as F

import pytest

from experiments.R3R_14_lean_close import checks, engine

CONTRASTS = ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1')


def row(Cref='10', **g):
    base = dict(Cref=Cref, G_S='0.5', G_M='0.2', G_SM='0.6', Gamma='-0.1', G_S_M1='0.4', G_M_S1='0.1',
                GM_identity_gap='0', Sbar='2', normalized_error={k: '1e-6' for k in CONTRASTS})
    base.update(g)
    return base


def test_round_rates_ties_to_even_and_u_from_eta():
    out = engine.round_rates(['7123/1000', '6543/1000', '1/10', '617/1000', '8', '0'], '1/10')
    assert out == ['71/10', '13/2', '1/10', '3/5', '8', '0']           # u = 1.234 -> 1.2, eta = 0.6
    assert engine.snap(F('7.15'), F(1, 10)) == F('7.2') and engine.snap(F('7.25'), F(1, 10)) == F('7.2')


def test_consistency_uses_contract_tolerance_not_arithmetic_bound():
    assert checks.consistency(row(G_SM='-0.001')) == []                  # -0.01 % of Cref: inside 1/400
    assert checks.consistency(row(G_SM='-0.1')) == ['negative_nonnegative_contrast:G_SM']
    assert checks.consistency(row(GM_identity_gap='0.05')) == ['model_gain_flip_identity']
    assert checks.consistency(row(G_S='2.01')) == []                    # 0.1 % of Cref above stakes: inside
    assert checks.consistency(row(G_S='2.1')) == ['state_gain_exceeds_stakes']    # 1 % of Cref above


def test_zero_control_must_be_exact():
    zero = row(**{k: '0' for k in CONTRASTS}, zero_action_certificate=True)
    assert checks.consistency(zero) == []
    assert checks.consistency(dict(zero, G_M='1e-30')) == ['zero_control_not_exact']


def test_level_ready_checks_both_neighbours_and_arithmetic():
    lv = {(160, 4): row(), (80, 4): row(), (160, 2): row()}
    assert checks.level_ready(lv, (160, 4)) == (True, [])
    worse = dict(lv)
    worse[(160, 2)] = row(G_M='0.5')                                     # 3 % of Cref apart on the dt axis
    ok, why = checks.level_ready(worse, (160, 4))
    assert ok is False and why[0].startswith('R1_dt')
    wide = dict(lv)
    wide[(80, 4)] = row(normalized_error={k: '0.001' for k in CONTRASTS})
    assert checks.level_ready(wide, (160, 4))[1] == ['arithmetic_width:(80, 4)']
    assert checks.level_ready({(160, 4): row()}, (160, 4))[0] is None


def test_select_level_skips_failing_candidate_and_waits_for_missing():
    good = {(80, 2): row(), (40, 2): row(), (80, 1): row(G_M='0.5')}       # fails R1 at (80, 2)
    level, _ = checks.select_level({'a': good}, [[80, 2], [160, 2]])
    assert level is None                                                  # (160, 2) not computed yet
    good.update({(160, 2): row(), (160, 1): row()})
    level, report = checks.select_level({'a': good}, [[80, 2], [160, 2]])
    assert level == (160, 2) and report[0]['failing']


def test_representation_rule():
    fine, near = row(G_M='0.2'), row(G_M='0.21')
    assert checks.representation(fine, near)['ok']
    far = row(G_M='0.3')                                                  # 1 % of Cref apart
    assert not checks.representation(fine, far)['ok']
    inside_band = checks.representation(row(G_M='0.12'), row(G_M='0.099'))   # 1.2 % is within 0.25 % of 1 %
    assert inside_band['criterion_flips'] == []
    flip = checks.representation(row(G_M='0.13'), row(G_M='0.099'))          # 1.3 % vs 0.99 %: a real flip
    assert flip['criterion_flips'] == ['G_M']


def test_write_once(tmp_path):
    engine.write_once(tmp_path / 'x.json', dict(a=1))
    with pytest.raises(FileExistsError):
        engine.write_once(tmp_path / 'x.json', dict(a=2))
