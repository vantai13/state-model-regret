"""Doan Van Tai — controls for V7-3; synthetic/train-only inputs."""
from datetime import date, datetime, timedelta

import numpy as np
import pytest

from experiments.ext_validity import ev_te as T
from experiments.letter import e4_geant as E
from experiments.letter import v7_3_data as D
from experiments.letter import v7_3_sim as S
from experiments.letter import v7_3_run as R


def triangle():
    nodes=['a','b','c']
    links=[dict(id=f'{u}{v}:{x}>{y}',source=x,target=y,capacity=1)
           for u,v in [('a','b'),('a','c'),('b','c')] for x,y in [(u,v),(v,u)]]
    links.sort(key=lambda e:(e['source'],e['target']))
    return dict(nodes=nodes,links=links,demands=[dict(id='ac',source='a',target='c',value=1),
                                              dict(id='bc',source='b',target='c',value=1)])


def test_sparse_parser_round_trip():
    net=triangle();values=np.array([1.234567891234567,0.]);present=np.array([True,False])
    encoded=D.format_tm(values,present,net,datetime(2005,5,5))
    got,mask=D.parse_tm(encoded,net)
    np.testing.assert_array_equal(got,values)
    np.testing.assert_array_equal(mask,present)
    assert D.format_tm(got,mask,net,datetime(2005,5,5))==encoded


@pytest.mark.parametrize('bad',['nan','-1','inf'])
def test_parser_rejects_invalid_values(bad):
    encoded=D.format_tm([1,0],[True,False],triangle(),datetime(2005,5,5))
    with pytest.raises(ValueError):
        D.parse_tm(encoded.replace(') 1 1 UNLIMITED',f') 1 {bad} UNLIMITED'),triangle())


def test_parser_rejects_duplicate_and_empty():
    text=D.format_tm([1,0],[True,False],triangle(),datetime(2005,5,5))
    with pytest.raises(ValueError,match='duplicate'):
        D.parse_tm(text.replace('DEMANDS (','DEMANDS (\nac ( a c ) 1 1 UNLIMITED'),triangle())
    with pytest.raises(ValueError,match='empty'):
        D.parse_tm(D.format_tm([0,0],[False,False],triangle(),datetime(2005,5,5)),triangle())


def test_calendar_split_is_42_dates_not_42_retained_nights():
    days=[date(2005,5,4)+timedelta(days=i) for i in range(50)]
    complete=set(days)-{days[0],days[20]}
    train,test,cutoff=D.split_calendar(days,complete,set(days))
    assert len(train)==40 and len(test)==8 and cutoff=='2005-06-15'
    assert train[-1]=='2005-06-14' and test[0]=='2005-06-15'


def test_consolidation_connectivity_and_preserves_unaffected_route():
    net=triangle();config,inc=D.consolidate(net,np.array([2.,3.]),20.)
    assert config['removed']==['ab']
    assert config['stay_routes']==config['switch_routes']
    assert len(config['history'])==3
    assert sum(x['status']=='KEEP_BRIDGE' for x in config['history'])==2
    D.routes_and_incidence(net,config['removed'])
    np.testing.assert_array_equal(inc[0],inc[1])


def test_only_flows_crossing_removed_links_are_rerouted():
    net=triangle();routes,inc=D.routes_and_incidence(net)
    newer,newinc=D.routes_and_incidence(net,['ac'],routes)
    assert newer[0]==('a','b','c') and newer[1]==routes[1]
    assert np.all(newinc[[i for i,e in enumerate(net['links']) if e['id'].startswith('ac:')]]==0)


def test_consolidation_stops_before_utilization_over_point_eight():
    net=triangle()
    net['demands'].append(dict(id='ab',source='a',target='b',value=1.))
    values=np.array([2.,3.,1.5])
    config,inc=D.consolidate(net,values,4.)
    assert max((inc[1]@values)/4)<=.8
    assert config['stop_link'] is not None
    assert config['history'][-1]['max_train_mean_utilization']>.8


def test_capacity_is_train_daytime_peak_divided_by_point_nine():
    _,inc=D.routes_and_incidence(triangle())
    daytime=np.array([[2,3],[4,1],[1,8]])
    cap=D.capacity_rule(daytime,inc)
    assert cap==pytest.approx(8/.9)
    assert (daytime@inc.T).max()/cap==pytest.approx(.9)


def test_one_slot_adapter_is_bitwise_ev_te_without_shortcuts():
    inc=np.array([[[1.,.5],[0.,1.]],[[.5,1.],[1.,0.]]])
    demand=np.array([[7.,4.]])
    m=np.array([[1.,-1.],[-1.,1.]])
    q=np.array([[0.,3.],[2.,0.]])
    mod=T.Model(inc*demand[0],np.array([8.,5.]),np.ones(2),.3,[],[])
    expected,fm,fq=T.futures(mod,m,q,.05,[10,30],90381)
    got,gm,gq,_=S.variable(inc,demand,[8.,5.],m,q,90381,lengths=[30],hs=[10,30],shortcut=False,reduce=False)
    np.testing.assert_array_equal(got,expected)
    np.testing.assert_array_equal(gm,fm)
    np.testing.assert_array_equal(gq[:,0],fq)


def test_constant_slots_equal_single_ev_te_call_bitwise():
    inc=np.array([[[1.]],[[.8]]]);m=np.array([[1.],[-1.]]);q=np.array([[1.],[2.]])
    one=S.variable(inc,[[9.]],[8.],m,q,98,lengths=[40],hs=[10,40],shortcut=False,reduce=False)
    two=S.variable(inc,[[9.],[9.]],[8.],m,q,98,lengths=[13,27],hs=[10,40],shortcut=False,reduce=False)
    for x,y in zip(one[:3],two[:3]):
        np.testing.assert_array_equal(x,y)


def test_toy_night_known_switch_answer_and_exact_crn_identity():
    # Stay: load 12 > cap 10, Q(t)=2t, cost(2)=4. Switch: load 6, cost=0.
    inc=np.array([[[2.]],[[1.]]]);m=np.ones((3,1));q=np.zeros((3,1))
    v,_,_,b=S.variable(inc,[[6.]],[10.],m,q,19,lengths=[40],hs=[20,40],beta=0.,trace=True)
    np.testing.assert_allclose(v[:,0],[ [1.,4.] ]*3,rtol=1e-14)
    np.testing.assert_array_equal(v[:,1],0.)
    d,ties=E.pick(v);assert (d==1).all() and not ties.any()
    np.testing.assert_array_equal(E.costs_for_decisions(v,d),E.costs_for_decisions(v,d.copy()))
    identical=np.repeat(inc[:1],2,axis=0)
    costs=S.variable(identical,[[6.]],[10.],m,q,123,lengths=[40],hs=[20,40])[0]
    np.testing.assert_array_equal(costs[:,0],costs[:,1])


def test_certified_shortcut_and_reduction_do_not_drop_initial_queue():
    inc=np.ones((2,1,1));m=np.ones((4,1));q=np.zeros((4,1))
    zero=S.variable(inc,[[1.],[2.]],[10.],m,q,50,lengths=[10,10],trace=True)
    assert not zero[0].any() and not zero[2].any() and not zero[3].any()
    q[:]=3
    got=S.variable(inc,[[1.]],[10.],m,q,50,lengths=[20],beta=0.)
    assert np.allclose(got[0],.5) and not got[2].any()


def test_shortcut_endpoint_law_and_independence():
    n=12000;inc=np.ones((1,1,2));m=np.ones((n,2));q=np.zeros((n,1))
    _,fm,_,_=S.variable(inc,[[.1,.1]],[10.],m,q,52,lengths=[10])
    expected=-np.expm1(-1)/2
    np.testing.assert_allclose((fm==-1).mean(axis=0),expected,atol=.015)
    assert abs(np.corrcoef(fm.T)[0,1])<.035


@pytest.mark.parametrize('q0,weight,mode',[(3.,8.,-1.),(.1,9.,1.),(0.,10.5,-1.)])
def test_mean_endpoint_and_cost_match_explicit_discrete_fluid(q0,weight,mode):
    inc=np.ones((1,1,1));m=np.array([[mode]]);q=np.array([[q0]])
    expected,acc=q.copy(),np.zeros((1,1));steps=70
    for k in range(steps):
        load=weight*(1+.3*mode*np.exp(-2*.05*k))
        expected,cost=T.fluid_step(expected,load,10.,.05);acc+=cost
    mod=T.Model(inc*weight,np.array([10.]),np.ones(1),.3,[],[])
    got=S.mean_endpoint(mod,m,q,.05,steps)
    np.testing.assert_allclose(got[:,0],expected,rtol=1e-12,atol=1e-12)
    costs=S.mean_rollout(inc,np.array([[weight]]),10.,m,q,hs=[steps],slot_seconds=steps*.05)
    np.testing.assert_allclose(costs[:,0,0],acc[:,0],rtol=1e-12,atol=1e-12)


def test_mean_path_carries_queue_between_slots():
    inc=np.ones((1,1,1));m=np.array([[-1.]]);q=np.array([[2.]])
    means=np.array([[12.],[4.],[11.]])
    expected,acc=q.copy(),np.zeros((1,1))
    for k in range(60):
        load=means[k//20,0]*(1+.3*m*np.exp(-2*.05*k))
        expected,cost=T.fluid_step(expected,load,10.,.05);acc+=cost
    got=S.mean_rollout(inc,means,10.,m,q,hs=[60],slot_seconds=1.)
    np.testing.assert_allclose(got[:,0,0],acc[:,0],rtol=1e-12,atol=1e-12)


def test_zero_variance_tint_is_undefined_not_infinite_h_over_tint():
    ti,censored,error=T.estimate_tint(np.zeros(200),.05)
    assert ti is None and censored and 'zero-variance' in error


def test_reduced_kernel_multiple_instances_uses_contiguous_output_buffers():
    inc=np.ones((2,2,4));m=np.ones((3,4));q=np.zeros((3,2))
    got=S.variable(inc,[[4.,3.,2.,1.]],[9.,8.],m,q,80,lengths=[20])
    assert got[0].shape==(3,2,1) and np.isfinite(got[0]).all()


def test_end_to_end_toy_and_no_test_date_engine_calls(monkeypatch):
    train=dict(dates=np.array(['2005-05-05']),days=np.full((1,96,1),6.),warm=np.zeros((1,8,1)))
    config=dict(incidence=np.array([[[2.]],[[1.]]]),capacity=np.array([10.]),profiles=np.full((2,24,1),6.))
    raw,meta=R.compute_night(train,config,'2005-05-05',-1.,n=1,k=2,r_dec=2,r_eval=3,seed=898)
    assert raw['decisions'].shape==(1,3,2,2,4)
    assert (raw['reference_decision']==1).all()
    np.testing.assert_array_equal(raw['G_S'],0.)
    assert meta['reference_evaluation_streams_distinct']
    monkeypatch.setattr(S,'variable',lambda *a,**k:pytest.fail('test engine called'))
    monkeypatch.setattr(S,'warm_instances',lambda *a,**k:pytest.fail('test warmup called'))
    with pytest.raises(ValueError,match='forbids test-night'):
        R.compute_night(train,config,'2005-06-15',-1.)
