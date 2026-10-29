"""Finite enumeration and old physical code independently check new aggregation."""
from fractions import Fraction as F
import numpy as np
from experiments.R3R_08_population_numerics import population as P,profiles,law_cache


def row(d,h,w,*,sat=False):
    return dict(d=np.array(d,dtype=np.longdouble),h=np.array(h,dtype=np.longdouble),
                w=np.array(w,dtype=np.longdouble),ed=np.zeros(len(d),dtype=np.longdouble),
                eh=np.zeros(len(d),dtype=np.longdouble),w_error=np.longdouble(0),
                zero_h=np.zeros(len(d),dtype=bool),sat_h=np.full(len(d),sat,dtype=bool))


def test_pair_costs_match_exact_factorized_state_enumeration():
    da=[F(0),F(1,2),F(2)];db=[F(-3),F(-1,3)]
    ha=[F(0),F(1),F(3)];hb=[F(-2),F(-1)]
    wa=[F(1,4),F(1,2),F(1,4)];wb=[F(2,3),F(1,3)]
    cv=lambda xs:[str(x.numerator/x.denominator) for x in xs]
    A=row(cv(da),cv(ha),cv(wa));B=row(cv(db),cv(hb),cv(wb))
    for model in ('true','mean'):
        exact=sum(a*b*(x+y) for a,x,h in zip(wa,da,ha) for b,y,k in zip(wb,db,hb) if (x+y<0 if model=='true' else h+k<0))
        loss,error,_=P.pair_loss(A,B,model=model)
        assert abs(loss-np.longdouble(exact.numerator)/exact.denominator)<=error+np.longdouble('1e-15')


def test_exact_mean_saturation_tie_is_not_decided_by_roundoff():
    A=row([3],[1+1e-7],[1],sat=True);B=row([-4],[-1-2e-7],[1],sat=True)
    loss,_,_=P.pair_loss(A,B,model='mean');assert loss==0
    A['sat_h'][:]=False;B['sat_h'][:]=False
    loss,_,_=P.pair_loss(A,B,model='mean');assert loss==-1


def test_stale_expected_gap_agrees_with_original_forward_posterior(tmp_path):
    from smr.cells import queue_D
    from smr.stationary import r2_keep
    from experiments.A00_engine.physical import side_from_law
    unit,law,_=law_cache.get(F(7),F(1),F(1,10),1,tmp_path/'law')
    side=profiles.get(F(7),F(1),F(0),F(1,10),F(1,40),1,unit,tmp_path/'profiles',cost_budget=F(1,10**9))
    for index in (0,2,7):
        cell=dict(ratesA=(F(1),F(13)),u=F(1),kappa=F(1,10),yA=index*unit)
        gotunit,mass,support,error=queue_D(cell,'A',1)
        keep,ke=r2_keep(F(1,120),F(1,10))
        table,_=side_from_law(unit,mass,rates=cell['ratesA'],u_stay=F(1),u_switch=F(0),capacity=F(10),H=3,dt=F(1,120),keep=keep,keep_error=ke)
        prior,ep=law.posterior([index])
        for name,truth in [('old_d',sum(p*v for p,v in zip(table.p,table.d))),('old_h',sum(p*v for p,v in zip(table.p,table.dh)))]:
            a,ea,_,_=profiles.values(side,name,np.array([index]),0);b,eb,_,_=profiles.values(side,name,np.array([index]),1)
            estimate=(1-prior[0])*a[0]+prior[0]*b[0]
            assert abs(estimate-truth)<=ea[0]+eb[0]+ep[0]*abs(a[0]-b[0])+np.longdouble('1e-11')


def test_zero_action_population_preserves_all_six_exact_zeros(tmp_path):
    result=P.evaluate(['TOY_ZERO','8','8','1/10','0','1/40',1,16,'0'],tmp_path)
    assert result['zero_action_certificate'] is True
    assert all(F(result[k])==0 for k in P.CONTRASTS)
    assert result['S1_route']=='direct_stationary_state'
    assert result['source_components']['A']['renormalized'] is False


def test_identical_model_policies_preserve_exact_model_gains(tmp_path):
    result=P.evaluate(['TOY_IDENTICAL','7','8','1/10','1/2','1/40',1,16,'0'],tmp_path,identical_models=True)
    assert F(result['G_M'])==F(result['G_M_S1'])==0
