"""Doan Van Tai — physical identity, exact collision keys and frame separation."""
from fractions import Fraction as F
import pytest
from experiments.R3R_05_contract.schema import canonical,derived,exact,from_pilot,validate,frame_errors,freshness,slot_count


def toy(**kw):
    return dict(id='synthetic-schema-test',contract_id='contract-v1.3',lambdaA='7',lambdaB='8',u='1',
                kappa='3/10',h='8',c_sw='0',role='discovery',**kw)


def change(**kw):
    r=toy();r.update(kw);return r


def test_scientific_identity_keeps_cost_and_excludes_K_ref_role_label():
    x=toy()
    assert canonical(x)==canonical(change(id='other',role='calibration',numerics={'K':80,'ref':2}))
    assert canonical(x)!=canonical(change(c_sw='1'))
    assert canonical(x)==canonical(change(kappa='0.3',lambdaA='14/2'))


@pytest.mark.parametrize('bad',[0.3,True,'nan','inf','1/0','1 / 2','+1',''])
def test_inexact_or_invalid_tokens_rejected(bad):
    with pytest.raises(ValueError):exact(bad)


@pytest.mark.parametrize('kw',[{'lambdaB':'10'},{'lambdaA':'5'},{'u':'3'}, {'u':'0'},
                             {'kappa':'0'},{'h':'0'},{'c_sw':'-1'},{'contract_id':'other'},
                             {'G_M_pctC':'3'},{'eta':'1/2'},{'numerics':{'K':2.5,'ref':1}}])
def test_invalid_regimes_are_rejected(kw):
    with pytest.raises(ValueError):validate(change(**kw))


def test_zero_action_control_is_valid_but_not_primary():
    x=change(u='0',role='control');validate(x)
    with pytest.raises(ValueError):validate(x,primary=True)


def test_finite_horizon_post_overload_is_not_stationary_pre_validity():
    x=change(lambdaA='6',lambdaB='9',u='3/2')
    validate(x,primary=True)
    assert derived(x)['rhoB_post']==F(21,20)
    assert frame_errors(x,{'rhoB_post':('0','19/20')})==['rhoB_post']


def test_switching_cost_scenario_is_valid_but_not_primary():
    validate(change(c_sw='1'))
    with pytest.raises(ValueError):validate(change(c_sw='1'),primary=True)


def test_pilot_adapter_preserves_ninth_cost_field_and_eta_meaning():
    p=['toy','7','6','3/10','3/4','8','1','40','1']
    r=from_pilot(p)
    assert r['c_sw']=='1' and r['u']=='3/2'
    assert derived(r)['phi']==F(3,8) and r['provenance']['eta_pilot']=='3/4'
    assert from_pilot(p[:8])['c_sw']=='0'
    assert derived(from_pilot(['toy','7','8','3/10','3/4','8','1','40']))['phi']==F(3,4)


def test_pilot_adapter_rejects_fractional_numerical_metadata():
    with pytest.raises(ValueError):from_pilot(['toy','7','8','3/10','1/2','8','1','81/2'])


def test_freshness_detects_exact_collision_despite_different_id_and_numerics():
    seen=[toy()]
    x=freshness(change(id='synthetic-other',numerics={'K':80,'ref':2}),seen)
    assert not x['fresh'] and x['min_design_Linf']==0
    close=freshness(change(lambdaA='7000001/1000000'),seen)
    assert close['fresh'] and close['min_design_Linf']==F(1,10000000)


def test_horizon_lattice_is_not_physical_validity_or_silent_rounding():
    assert slot_count(toy(),2)==1920
    r=change(h='1/7');validate(r)
    with pytest.raises(ValueError,match='no silent'):slot_count(r,2)
