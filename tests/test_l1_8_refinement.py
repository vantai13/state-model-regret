"""Doan Van Tai — B1 scaling, finite reference, refinement diagnostics and controls."""
from fractions import Fraction as F
import math
import numpy as np
import pytest

from experiments.lessons.l1_3_expected_cost import expected_cost, generate_episodes
from experiments.lessons.l1_6_belief import cost_with_current_backlog, factorial_end_to_end, m0_cost
from experiments.lessons.l1_8_refinement import (
    CONTRASTS, episode_distribution, pair_check, params_at, solve_level, triplet_diagnostic,
)


def test_scaling_keeps_world_and_observation_unchanged():
    for m in (1,2,4,8,16,32,64,128):
        p=params_at(m)
        assert p['dt']*p['H']==2 and p['dt']*p['tau']==1 and p['y']==(2,0)
        assert p['cA']/p['dt']==p['cB']/p['dt']==3
        assert p['u']/p['dt']==2 and p['rate_on']/p['dt']==5
        assert float(p['lam']**m)==pytest.approx(.25,rel=1e-12)


@pytest.mark.parametrize('m',[1,2,4])
def test_aggregated_dp_matches_old_independent_finite_path_reference(m):
    solved=solve_level(m)
    p=solved['params']
    th={k:p[k] for k in ('cA','cB','u','bA','rate_on','rate_off','H')}
    th.update(p_onon=F(float(p['p_onon'])),p_offoff=F(float(p['p_offoff'])))
    D=generate_episodes((2,0),m,th,F(1,2))
    L,_,belief=factorial_end_to_end([(-m,(2,0))],th,F(1,2),D)
    assert D==belief
    assert len(D)==solved['summary']['support_states']
    for x,prob in D.items():
        qi,mode=int(x[1]*m),int(x[2]=='on')
        assert solved['D'][qi,mode]==pytest.approx(float(prob),abs=1e-14)
        for ai,a in enumerate(('Stay','Switch')):
            assert solved['J'][qi,mode,ai]==pytest.approx(float(expected_cost(x,a,th)*p['dt']),abs=1e-12)
            assert solved['M'][qi,mode,ai]==pytest.approx(float(m0_cost(x,a,th)*p['dt']),abs=1e-12)
    for c,val in L.items():
        assert solved['summary']['L'+c]==pytest.approx(float(val*p['dt']),abs=1e-12)
    for model in ('M0','M1'):
        val=cost_with_current_backlog(D,th,model)*p['dt']
        assert solved['summary']['L_current_'+model]==pytest.approx(float(val),abs=1e-12)


def test_coarse_golden_is_rational_not_rounded_table():
    s=solve_level(1)['summary']
    assert s['Lstar']==float(F(409,64))
    assert s['G_S']==float(F(119,128))
    assert s['G_M']==s['Gamma']==s['R11']==0
    assert s['freshness']==float(F(35,128)) and s['mode_visibility']==float(F(21,32))


def test_zero_managed_traffic_is_a_negative_control():
    for m in (1,2,8,32):
        s=solve_level(m,managed_rate=0)['summary']
        assert all(s[k]==0 for k in CONTRASTS)
        assert s['freshness']==s['mode_visibility']==0


def test_original_and_proposed_reporting_rules_on_known_linear_error():
    levels=[]
    for m in (1,2,4,8):
        levels.append(dict(m=m,**{k:1+1/m for k in CONTRASTS}))
    diagnostic=triplet_diagnostic(*levels[:3],'G_S')
    assert diagnostic['rho_conv']==.5
    assert diagnostic['richardson_from_last']==1
    checks=pair_check(levels[0],levels[1],C_ref=100,tolerance_fraction=.005)
    assert all(r['passed'] for r in checks)
    # Coarse true error1 exceeds .5 tolerance; finer error.5 passes.
    assert levels[0]['G_S']-1==1 and levels[1]['G_S']-1==.5


def test_sign_rule_ignores_small_flips_but_rejects_large_flips():
    a=dict(m=1,**{k:.001 for k in CONTRASTS})
    b=dict(m=2,**{k:-.001 for k in CONTRASTS})
    assert all(r['passed'] for r in pair_check(a,b,C_ref=1))
    b['Gamma']=-.02
    r=next(r for r in pair_check(a,b,C_ref=1) if r['metric']=='Gamma')
    assert r['sign_violation'] and not r['passed']


def test_flat_zero_and_non_asymptotic_sequences_do_not_certify_an_order():
    def level(m,g): return dict(m=m,G_S=g)
    flat=triplet_diagnostic(level(1,0),level(2,0),level(4,0),'G_S')
    assert flat['rho_conv'] is None and flat['flat_three']
    other=triplet_diagnostic(level(1,.8),level(2,.6),level(4,.58),'G_S')
    assert other['rho_conv']==pytest.approx(.1)
    assert not math.isclose(other['rho_conv'],.5)


def test_invalid_refinement_inputs():
    for m in (0,-1,True,1.5):
        with pytest.raises(ValueError): params_at(m)
    for lam in (0,1,-1):
        with pytest.raises(ValueError): params_at(1,lam_coarse=lam)
    with pytest.raises(ValueError): pair_check({}, {},0)


def test_precision_audit_preserves_decisions_on_refined_levels():
    for m in (8,32,128):
        normal=solve_level(m)
        extended=solve_level(m,dtype=np.longdouble)
        support=normal['D']>0
        assert np.max(np.abs(normal['J']-extended['J']))<1e-10
        for cell in ('00','10','01','11'):
            assert np.array_equal(normal['actions'][cell][support],extended['actions'][cell][support])
            assert normal['near_ties'][cell]['alerted_states']==0
        for model in ('M0','M1'):
            assert np.array_equal(normal['current_actions'][model],extended['current_actions'][model])
            assert normal['near_ties']['current_'+model]['alerted_states']==0


def test_fixed_model_state_split_is_distinct_from_source_hybrid():
    s=solve_level(16)['summary']
    assert s['freshness']+s['mode_visibility']==pytest.approx(s['G_S'],abs=1e-12)
    assert s['freshness_M1']+s['mode_visibility_M1']==pytest.approx(s['G_S|M1'],abs=1e-12)
    assert s['hybrid_freshness']+s['hybrid_mode']==pytest.approx(s['G_S'],abs=1e-12)
    assert s['hybrid_freshness']!=pytest.approx(s['freshness'],abs=1e-3)
    # The source's .288/.051 row is the mixed-model path, not the fixed-M0 path.
    assert s['hybrid_freshness']==pytest.approx(.288,abs=.0005)
    assert s['hybrid_mode']==pytest.approx(.051,abs=.0005)


def test_independent_forward_scoring_matches_backward_expectations():
    from experiments.lessons.l1_8_forward_reference import check_level
    for m in (4,16,64,128):
        result=check_level(solve_level(m))
        assert result['D_max_abs_error']<1e-12
        assert result['max_aggregate_cost_error']<1e-10
