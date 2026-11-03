"""Doan Van Tai — distinguish uncertainty causes and weighted gap diagnostics."""
import pytest
from tools.analyze_phase6_saved import u_category,signed_components


@pytest.mark.parametrize('label,ready,expected',[
    ('U',False,'NOT_READY'),('U',True,'READY_DEADBAND'),('-',True,'LABELLED'),('+',True,'LABELLED')])
def test_uncertainty_categories(label,ready,expected):
    assert u_category(label,ready)==expected


def test_weighted_gap_can_reverse_sign_with_fewer_old_switches():
    # Old switches less, but pays a higher true gap on the states where it switches.
    old=dict(share=.1,loss=.3);new=dict(share=.2,loss=.1)
    components=signed_components(10.,old,new,-10.,10.,10.)
    assert components['constant_stake_native_pp']==pytest.approx(-10.)
    assert components['weighted_gap_correction_pp']==pytest.approx(12.)
    assert sum(components[k] for k in ('weighted_gap_correction_pp',
        'action_representation_correction_pp','normalizer_correction_pp'))==pytest.approx(12.)


def test_normalizer_and_action_representation_are_not_weighting_error():
    old=dict(share=.2,loss=2.);new=dict(share=.3,loss=3.)
    c=signed_components(10.,old,new,-5.,10.,20.)
    assert c['weighted_gap_correction_pp']==pytest.approx(0.)
    assert c['action_representation_correction_pp']==pytest.approx(-2.5)
    assert c['normalizer_correction_pp']==pytest.approx(2.5)
    assert -5.+sum(c[k] for k in ('weighted_gap_correction_pp',
        'action_representation_correction_pp','normalizer_correction_pp'))==pytest.approx(-5.)
