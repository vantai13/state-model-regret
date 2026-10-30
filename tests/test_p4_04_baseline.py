"""Sanity against the actual frozen pair_loss and exact supplied toys."""
from fractions import Fraction as F
import struct

import numpy as np
import pytest

from experiments.P4_04_baseline.margin import pair_loss_margin, significant_bits
from experiments.P4_04_baseline.toys import goldens, two_state
from experiments.R3R_08_population_numerics.population import pair_loss
from experiments.R3R_08_population_numerics.piecewise import LD


def side(rng, size):
    w = rng.random(size).astype(LD)
    w /= w.sum(dtype=LD)
    return dict(d=rng.normal(size=size).astype(LD), h=rng.normal(size=size).astype(LD),
                ed=np.full(size, LD('1e-15')), eh=np.full(size, LD('1e-15')),
                w=w, w_error=LD('1e-17'), zero_h=np.zeros(size, dtype=bool),
                sat_h=np.zeros(size, dtype=bool))


def test_200_synthetic_trials_actual_frozen_pair_loss():
    rng = np.random.default_rng(44004)
    for trial in range(200):
        A, B = side(rng, 1+trial % 7), side(rng, 1+(trial*3) % 9)
        # Exercise certificates, including ties, rather than random signs alone.
        if trial % 3 == 0:
            A['zero_h'][0] = B['zero_h'][0] = True
        if trial % 5 == 0:
            A['sat_h'][-1] = B['sat_h'][-1] = True
        for model in ('true', 'mean'):
            expected = pair_loss(A, B, model=model)
            actual = pair_loss_margin(A, B, model=model)
            assert significant_bits(actual[0]) == significant_bits(expected[0])
            assert significant_bits(actual[1]) == significant_bits(expected[1])
            assert struct.pack('!d',actual[2]) == struct.pack('!d',expected[2])
        huge = max(abs(A['h']))+max(abs(B['h']))+LD(1)
        assert pair_loss_margin(A, B, theta=huge)[0] == 0
        theta = LD(str((trial % 11) / 10))
        loss, err, _ = pair_loss_margin(A, B, theta=theta)
        oracle, oracle_err, _ = pair_loss(A, B, model='true')
        assert loss+err >= oracle-oracle_err


def test_exact_goldens_all_supplied_rows():
    g = goldens()
    assert g['three_snapshots'] == {'0':F(142,15), '1':F(9), '5':F(10)}
    assert g['L01'] == F(44,5) and g['recovery_theta1'] == F(7,10)
    assert g['changed_y1_theta1'] == F(29,3) and g['changed_y1_recovery'] == F(-3,10)
    expected = {
        ('T-AB','0'):(11,F(21,2),F(1,2),0),
        ('T-AB','3/2'):(10,F(21,2),F(-1,2),1),
        ('T-AB','7/2'):(10,10,0,1),
        ("T-C'",'0'):(10,F(21,2),F(-1,2),None),
        ("T-C'",'3/2'):(10,F(21,2),F(-1,2),None),
        ("T-C'",'7/2'):(10,10,0,None),
        ('T-A','0'):(10,F(19,2),F(1,2),None),
        ('T-A','3/2'):(10,10,0,None),
    }
    for row in g['two_states']:
        assert tuple(row[k] for k in ('L00_theta','L10_theta','GS_theta','R_M')) == expected[(row['toy'],row['theta'])]


def test_margin_can_remove_genuine_state_value_by_worsening_current_controller():
    row = two_state('T-A',F(3,2))
    assert row['GS_theta'] == 0 and row['deltaL10'] == F(1,2)


def test_margin_changes_action_only_not_cost():
    z=np.zeros(1,dtype=LD); cert=np.zeros(1,dtype=bool)
    A=dict(d=np.array([-3],dtype=LD), h=np.array([-4],dtype=LD),ed=z,eh=z,
           w=np.ones(1,dtype=LD),w_error=LD(0),zero_h=cert,sat_h=cert)
    B=dict(A,d=z,h=z)
    assert pair_loss_margin(A,B,theta=LD(1))[0] == -3
    assert pair_loss_margin(A,B,theta=LD(4))[0] == 0  # strict tie stays


def test_margin_scale_uncertainty_covers_boundary():
    z=np.zeros(1,dtype=LD); cert=np.zeros(1,dtype=bool)
    A=dict(d=np.array([2],dtype=LD),h=np.array([-1],dtype=LD),ed=z,eh=z,
           w=np.ones(1,dtype=LD),w_error=LD(0),zero_h=cert,sat_h=cert)
    B=dict(A,d=z,h=z)
    exact=pair_loss_margin(A,B,theta=LD('0.9'))
    uncertain=pair_loss_margin(A,B,theta=LD('0.9'),theta_error=LD('0.2'))
    assert exact[0] == uncertain[0] == 2
    assert exact[2] == 0 and uncertain[2] == 1 and uncertain[1] >= 2


def test_zero_action_arrays_and_unknown_model():
    rng=np.random.default_rng(44005);A=side(rng,3);B=side(rng,4)
    for s in (A,B):
        s['d'][:]=0;s['h'][:]=0;s['zero_h'][:]=True
    for theta in (0,LD('0.5'),100):
        assert pair_loss_margin(A,B,theta=theta)[0] == 0
    with pytest.raises(ValueError,match='unknown action model'):
        pair_loss_margin(A,B,model='bad')


@pytest.mark.parametrize('theta,error',[(-1,0),(0,-1),(float('nan'),0),(0,float('inf'))])
def test_invalid_margin_rejected(theta,error):
    with pytest.raises(ValueError,match='finite nonnegative'):
        pair_loss_margin({}, {}, theta=theta,theta_error=error)


def test_guard_rejects_cf_and_sealed_before_discovery_lookup():
    from experiments.P4_04_baseline.common import guard_case,cf_keys,canonical,load,SEALED
    key=next(iter(cf_keys()))
    a,b,u,k,h,c=map(F,key)
    case=dict(parameters=list(map(str,(a,b,k,u/2,h,c))),key=list(key))
    with pytest.raises(RuntimeError,match='CF_COLLISION'):guard_case(case)
    key=load(SEALED)['sealed'][1]['coordinates']
    a,b,u,k,h,c=map(F,key)
    case=dict(parameters=list(map(str,(a,b,k,u/2,h,c))),key=list(key))
    assert canonical(case['parameters'])==tuple(key)
    with pytest.raises(RuntimeError,match='SEALED_R09_R10'):guard_case(case)


def test_exact_scope_all_classes_and_normalized_age():
    from experiments.P4_04_baseline.common import plan,guard_case
    p=plan()
    assert len(p['cases'])==90 and len(p['aliases'])==90
    assert sum('MV+A' in c['regions'] for c in p['cases'])==18
    assert sum('SH+A' in c['regions'] for c in p['cases'])==72
    for c in p['cases']:guard_case(c)
    assert {a['pilot_class'] for a in p['aliases'] if 'MV+A' in a['regions']}=={'B','C'}
    assert {a['pilot_class'] for a in p['aliases'] if 'SH+A' in a['regions']}=={'A','C','D'}


def test_missing_prereg_refuses_physical_run(monkeypatch,tmp_path):
    from experiments.P4_04_baseline import common
    monkeypatch.setattr(common,'ROOT',tmp_path)
    with pytest.raises(RuntimeError,match='BASELINE_PREREG_NOT_FROZEN'):common.verify_prereg()


def test_select_rho_controller_specific_exact_tie_and_zero_option():
    from experiments.P4_04_baseline.analysis import select_rho
    from experiments.P4_04_baseline.common import RHOS
    row=dict(losses={'11':'8'},Cref='8',baseline=[dict(rho=r,L00='10',L10='9') for r in RHOS])
    assert select_rho([row],'00')[0]=='0'
    row['baseline'][1]['L00']='9';row['baseline'][3]['L10']='8'
    assert select_rho([row],'00')[0]=='1/200'
    assert select_rho([row],'10')[0]=='1/50'


@pytest.mark.parametrize('delta,narrow',[(1,False),(0,False),(-1,True)])
def test_reading_requires_strictly_improved_current_controller(delta,narrow):
    from experiments.P4_04_baseline.analysis import reading
    result=reading('SH+A',[dict(GS_theta_pctC=.1,deltaL10=delta)])
    assert result['descriptive_narrow'] is narrow


def test_reading_boundaries_and_undefined_recovery():
    from experiments.P4_04_baseline.analysis import reading
    assert not reading('SH+A',[dict(GS_theta_pctC=.5,deltaL10=-1)])['descriptive_narrow']
    assert reading('MV+A',[dict(R_M=.5,R_M_denominator_certified=True)])['descriptive_narrow']
    result=reading('MV+A',[dict(R_M=None,R_M_denominator_certified=False)])
    assert result['undefined']==1 and not result['descriptive_narrow']
