"""Doan Van Tai — exact toy comparisons and strict probability signs."""
from fractions import Fraction as F
import numpy as np
from smr.gap_screen import backward,probability_interval
from smr.idle_gap import weighted_idle


def test_native_weighted_idle_matches_fraction_for_all_small_states():
    for H in (1,2,5,12):
        for inc in ((-2,1),(-5,3),(-1,-1)):
            for extended in (False,True):
                out,error,_=backward(np.arange(15),inc,H,F(3,4),extended=extended)
                for q in range(15):
                    for m in (0,1):
                        rates={0:5+inc[0],1:5+inc[1]};P={m:{n:F(3,4) if n==m else F(1,4) for n in (0,1)} for m in (0,1)}
                        exact=weighted_idle(F(q),m,rates,F(0),F(5),H,P)
                        assert abs(F(str(out[q,m]))-exact)<=F(str(error))
                assert np.all(out[H*max(0,-inc[0],-inc[1]):]==0)


def test_sort_screen_matches_brute_force_with_ties():
    A=np.array([0,1,2,4]);B=np.array([-4,-2,-1,0]);p=np.full(4,.25)
    r=probability_interval(A,B,p,p,0,0)
    exact=sum(F(1,16) for a in A for b in B if a+b<0)
    assert r['p_low']<=float(exact)<=r['p_high']
    assert r['unresolved_mass']==0
    unresolved=probability_interval([1],[-1],[1],[1],.01,.01)
    assert unresolved['unresolved_mass']==1


def test_golden_gap_and_queue_signs():
    # Canonical H2,c3,u2,A background1,B OFF0/ON5; both actions use unit1.
    q=np.array([0,2]);ast,_,_=backward(q,(-0,-0),2,F(1,2))
    asw,_,_=backward(q,(-2,-2),2,F(1,2))
    bst,_,_=backward(q,(-3,2),2,F(1,2));bsw,_,_=backward(q,(-1,4),2,F(1,2))
    WA=asw-ast;WB=bsw-bst
    assert np.all(WA>=0) and np.all(WB<=0)
    assert [WA[1,0]+WB[j,m] for j,m in ((1,1),(1,0),(0,1),(0,0))]==[2,-1.5,1.5,-3]


def test_zero_capacity_loss_is_exact_zero_and_large_toy_fits_budget():
    out,_,seconds=backward(np.array([10000,10001]),(-3,2),300,F(3,4))
    assert np.all(out==0) and seconds<1200


def test_two_markov_queues_against_joint_exact_paths():
    from itertools import product
    from tests.test_dominance_v1_1 import _paths,_prob,_cost
    for H in (1,2,3):
        p=dict(H=H,cA=F(3),cB=F(3),u=F(1),ratesA={'off':F(0),'on':F(4)},ratesB={'off':F(1),'on':F(5)},keepA=F(3,4),keepB=F(1,2))
        qa=np.arange(4);ast,_,_=backward(qa,(-2,2),H,F(3,4));asw,_,_=backward(qa,(-3,1),H,F(3,4))
        bst,_,_=backward(qa,(-2,2),H,F(1,2));bsw,_,_=backward(qa,(-1,3),H,F(1,2))
        for a,b,ma,mb in product(range(4),range(4),range(2),range(2)):
            x=(F(a),('off','on')[ma],F(b),('off','on')[mb])
            exact=sum(_prob(pa,p['keepA'])*_prob(pb,p['keepB'])*(_cost(x,pa,pb,p,'Switch')-_cost(x,pa,pb,p,'Stay'))
                      for pa,pb in product(_paths(x[1],H),_paths(x[3],H)))
            assert (asw-ast)[a,ma]+(bsw-bst)[b,mb]==float(exact)


def test_large_synthetic_benchmark():
    out,error,seconds=backward(np.arange(100,1600),(-19,11),1000,F(3,4))
    assert np.all(out>=0) and error>0 and seconds<1200
