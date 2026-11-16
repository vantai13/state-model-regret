"""Doan Van Tai — W1b controls for age-only information and s-hat estimation."""
from fractions import Fraction as F
import json
import multiprocessing
import pickle
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pytest
from scipy.linalg import expm

from experiments.explore_ctmc import ctmc
from experiments.letter.e3_agediff import evaluate_agediff, posterior_full, prepare_regime
from experiments.letter import shat


@pytest.fixture(scope='module')
def prepared():
    # A real regime in asym.json; short horizons keep the unit controls inexpensive.
    return prepare_regime('7','6','1','1/20',['1/10','2'])


def evaluate(p,tau,**kwargs):
    return evaluate_agediff(*p['parameters'][:4],p['hs'],tau,
                            c=p['parameters'][4],a=p['a'],prepared=p,**kwargs)


def test_zero_age_same_decisions_and_zero_gain_for_every_pipeline(prepared):
    levels={'negated':-prepared['s'],'perturbed':1.5*prepared['s']}
    out=evaluate(prepared,0,shat_levels=levels)
    for row in out['h']:
        assert row['G_S']==row['S']==row['G_S_hybrid']==row['G_S_ko']==0
        assert row['L00']==row['L10'] and row['L01']==row['L11']
        for twin in ('M0','M1','hybrid','hybrid_mm1','ko'):
            assert row['regret'][twin+'_new']==row['regret'][twin+'_old']
            assert row['shares'][twin+'_new']==row['shares'][twin+'_old']
        for level in row['hybrid_levels'].values():
            assert level['G_S']==0 and level['share_new']==level['share_old']
        for margin in row['margin'].values():
            assert margin['new']==margin['old'] and margin['share_new']==margin['share_old']


@pytest.mark.xfail(strict=True, reason='Brief premise fails on positive-mass exact M0 ties: tau=0 is identical, tau->0+ need not be; boundary_check.json records the counterexample')
def test_vanishing_positive_age_gain_tends_to_zero(prepared):
    out=evaluate(prepared,1e-9,disagree=False)
    for row in out['h']:
        assert abs(row['G_S'])<1e-6
        assert abs(row['G_S_hybrid'])<1e-6


def test_large_age_posterior_is_stationary_for_every_old_full_state():
    stay=ctmc.chain(F(7),F(1,2),12)
    vec=np.column_stack([stay.f,np.sin(stay.f),np.arange(stay.n)%2])
    got=posterior_full(stay,vec,1000)
    want=stay.pi@vec
    np.testing.assert_allclose(got,np.tile(want,(stay.n,1)),atol=2e-9,rtol=2e-9)


def test_full_posterior_matches_dense_exponential_and_tower():
    stay=ctmc.chain(F(7),F(1,2),12)
    rng=np.random.default_rng(71)
    vec=rng.normal(size=(stay.n,3))
    got=posterior_full(stay,vec,.4)
    np.testing.assert_allclose(got,expm(stay.Q.toarray()*.4)@vec,atol=1e-12)
    np.testing.assert_allclose(stay.pi@got,stay.pi@vec,atol=1e-12)
    # Full-state observation preserves old mode; its rows are not backlog marginals.
    assert got.shape==(stay.n,3)
    assert np.max(abs(got[0::2]-got[1::2]))>1e-3


def test_asym_regime_at_one_second_finite_and_fresh_matches_original(prepared):
    out=evaluate(prepared,1,disagree=False)
    original=ctmc.evaluate(*prepared['parameters'][:4],prepared['hs'],disagree=False)
    for row,baseline in zip(out['h'],original['h']):
        for key in ('L10','L11','Cref','M'):
            assert row[key]==baseline[key]
        assert np.isfinite([row[k] for k in ('L00','L01','L10','L11','G_S','G_M','S','M')]).all()
        assert min(row['S'],row['M'],row['G_M'])>=-1e-9
        assert row['G_SM']==pytest.approx(row['G_S']+row['M'],abs=1e-10)


def test_age_only_gain_and_hybrid_use_original_pair_sum_and_full_weights(prepared):
    out=evaluate(prepared,.3,arrays=True,disagree=False)
    arr=out['_arrays']
    for i,row in enumerate(out['h']):
        old=ctmc.pair_sum(arr['wA'],arr['dhAo'][i],arr['dAo'][i],
                          arr['wB'],arr['dhBo'][i],arr['dBo'][i],0)
        new=ctmc.pair_sum(arr['wA'],arr['dhA'][i],arr['dA'][i],
                          arr['wB'],arr['dhB'][i],arr['dB'][i],0)
        assert row['G_S']==100*(old[1]-new[1])/row['Cref']
        assert row['shares']['M0_old']==old[0]
        h=float(F(row['h']))
        ho=ctmc.pair_sum(arr['wA'],arr['dhAo'][i]+h*prepared['s'],arr['dAo'][i],
                         arr['wB'],arr['dhBo'][i],arr['dBo'][i],0)
        assert row['hybrid_levels']['true_s']['share_old']==ho[0]
        assert row['hybrid_levels']['true_s']['excess_cost_old']==pytest.approx(ho[1]-(row['Cref']-row['E_stay']),abs=1e-12)


def test_pair_sum_exact_ties_choose_stay_by_brute_force():
    wA=np.array([.2,.8]);wB=np.array([.4,.6])
    uA=np.array([-1.,0.]);uB=np.array([0.,1.])
    vA=np.array([2.,3.]);vB=np.array([5.,6.])
    mass,value,ties=ctmc.pair_sum(wA,uA,vA,wB,uB,vB,0)
    gap=uA[:,None]+uB[None,:];weights=wA[:,None]*wB[None,:]
    assert mass==pytest.approx((weights*(gap<0)).sum())
    assert value==pytest.approx((weights*(gap<0)*(vA[:,None]+vB[None,:])).sum())
    assert ties==pytest.approx((weights*(gap==0)).sum())
    assert mass==pytest.approx(.08)  # The two tie pairs contribute no Switch mass.


@pytest.mark.parametrize('tau',[-1,np.inf,np.nan])
def test_invalid_ages_refused(tau):
    ch=ctmc.chain(F(7),F(1,2),12)
    with pytest.raises(ValueError):posterior_full(ch,ch.f,tau)


def test_telemetry_sampling_and_estimators_reproduce_fixed_seed():
    args=(8.,-1.,.5,6.,.2)
    a=shat.estimate_path(*args,np.random.default_rng(20261116))
    b=shat.estimate_path(*args,np.random.default_rng(20261116))
    assert a==b and len(a['mode'])==1001
    assert a['delta']==pytest.approx(.02) and a['W']==pytest.approx(20)
    rates=8+6*(2*np.array(a['mode'])-1)
    assert a['lambda_hat']==rates.mean()
    assert a['alpha_hat']==rates.std(ddof=0)
    assert a['rho1_raw']==np.corrcoef(rates[:-1],rates[1:])[0,1]
    assert a['kappa_hat']==pytest.approx(-2*a['delta']/np.log(a['rho1_clipped']))
    assert a['switch_load_hat']==a['lambda_hat']-1


def test_namespace_rejection_is_invalid_and_falls_back_without_claiming_sign(prepared):
    levels,meta=shat.estimate_levels(prepared,0)
    assert meta['seed']==20261116 and meta['status']=='INVALID'
    assert meta['fallback']=='mm1' and meta['s_hat_mmpp'] is None and meta['sign_correct'] is None
    assert levels['mmpp_est']==levels['mm1']==prepared['s_mm1']
    assert len(meta['errors'])>0
    assert all(1+eps>0 and np.sign(levels[f'true_s_eps_{eps:+g}'])==np.sign(prepared['s']) for eps in shat.EPSILONS)
    assert levels['sign_flipped']==-prepared['s']


def test_write_once_refuses_to_replace_raw(tmp_path):
    p=tmp_path/'raw.json'
    shat.write_json_once(p,{'value':1})
    before=p.read_bytes()
    with pytest.raises(FileExistsError):shat.write_json_once(p,{'value':2})
    assert p.read_bytes()==before and json.loads(before)=={'value':1}


def test_case_inputs_define_93_unique_regimes_and_keep_each_amplitude_and_grid():
    cases=shat.load_cases()
    assert len(cases)==93 and len({c['id'] for c in cases})==93
    assert [sum(c['family']==fam for c in cases) for fam in shat.FAMILIES]==[33,33,27]
    assert all(c['hs'] and shat.saved_path(c).is_file() for c in cases)


def test_unresolved_saved_baseline_is_missing_evidence_before_computation():
    case=next(c for c in shat.load_cases() if c['id']=='Za7p5_u3-2_lA31-4_x1-3_k2')
    before=shat.saved_path(case).read_bytes()
    baseline,available=shat.read_baseline(case)
    assert not available and baseline['status']=='UNRESOLVED'
    assert 'h' not in baseline and 'a' not in baseline
    assert shat.saved_path(case).read_bytes()==before


def test_parallel_original_V_and_pickled_age_inputs_match_serial_bitwise(prepared):
    keys={(str(prepared[n].load),str(prepared[n].kappa),prepared[n].N,str(F(prepared[n].a)))
          for n in ('Ast','Asw','Bst','Bsw')}
    with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
        values=[f.result() for f in [pool.submit(shat.timed_v,(key,prepared['hs'])) for key in sorted(keys)]]
    table={key:arr for key,arr,cpu in values}
    new=prepare_regime(*prepared['parameters'][:4],prepared['hs'],v_table=table)
    for key in ('dA','dB','dhA','dhB','bA','bB'):
        np.testing.assert_array_equal(new[key],prepared[key])
    new=pickle.loads(pickle.dumps(new))
    serial=evaluate(prepared,.3,disagree=False)
    parallel=evaluate(new,.3,disagree=False)
    assert json.dumps(serial,sort_keys=True)==json.dumps(parallel,sort_keys=True)
