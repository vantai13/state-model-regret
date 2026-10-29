from experiments.R3R_07_confirmation.score import label_result
from experiments.R3R_05_contract.rules import CONTRASTS


def bundle(gain,error):
    level=dict(Cref='1',**{k:gain for k in CONTRASTS},normalized_error={'G_M':error})
    return dict(main=level,coarse_K=level,coarse_dt=level,arithmetic_pass=True)


def test_arithmetic_interval_crossing_boundary_stays_unresolved():
    assert label_result('effect',bundle('0.01001','0.00002'))=='UNRESOLVED'


def test_effect_farther_than_arithmetic_error_can_be_scored():
    assert label_result('effect',bundle('0.02','0.00002'))=='MEETS'
