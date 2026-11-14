"""Doan Van Tai — small synthetic controls, not new study outcomes.
Only production kernels (never scorers) are imported. Writes only beside script.
"""
import itertools
import json
import sys
from pathlib import Path
from fractions import Fraction as F

import numpy as np
from scipy.linalg import expm

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from experiments.ext_validity import closed_loop as CL, packet as P, trace_cox as TC

OUT=Path(__file__).resolve().parent


def closed_loop_timing():
    # Separate, explicit flattened Kronecker transition; tiny truncation test only.
    original=CL.C.choose_N
    CL.C.choose_N=lambda *a,**kw: 4
    try:
        case=dict(id='audit_toy',parameters=['7','15/2','1','1/2'])
        chains=CL._chains(case,F(2))
        e=CL._Epoch(chains,F(2))
        n=e.initial.size
        mask=np.indices(e.initial.shape).sum(0)%3==0
        K=np.zeros((2*n,2*n))
        q=[np.kron(a.Q.toarray(),np.eye(b.n))+np.kron(np.eye(a.n),b.Q.toarray()) for a,b in chains]
        push=[]
        # old action b for tau, then selected new action a for Delta-tau.
        for b in (0,1):
            for a in (0,1):
                select=(mask if a else ~mask).ravel()
                block=np.diag(select)@expm(q[b])@expm(q[a])
                K[b*n:(b+1)*n,a*n:(a+1)*n]=block
                law=np.zeros((2,*e.initial.shape));law[b]=e.initial
                expected=(law[b]*(mask if a else ~mask)).ravel()@expm(q[b])@expm(q[a])
                direct=e.push(e.push(law[b]*(mask if a else ~mask),b,1.),a,1.).ravel()
                push.append(float(np.max(abs(expected-direct))))
        rec,law=e.stationary(mask,True,2000)
        flat=law.ravel()
        # Observation-epoch accounting: first tau at b, then Delta-tau at a.
        # Production charges the full Delta from actuation to actuation; equal
        # only in stationary long-run expectation (boundary terms telescope).
        physical=0.
        for b in (0,1):
            v_b=sum(ch.V([F(1)])[0][:,None] if j==0 else ch.V([F(1)])[0][None,:]
                    for j,ch in enumerate(chains[b]))
            physical+=float((law[b]*v_b).sum())
            for a in (0,1):
                phi=e.push(law[b]*(mask if a else ~mask),b,1.)
                v_a=sum(ch.V([F(1)])[0][:,None] if j==0 else ch.V([F(1)])[0][None,:]
                        for j,ch in enumerate(chains[a]))
                physical+=float((phi*v_a).sum())
        out=dict(status=rec['status'],kronecker_push_max_abs=max(push),
                 stationary_mass_error=float(abs(flat.sum()-1)),
                 independent_transition_residual=float(np.abs(flat@K-flat).sum()),
                 production_J=rec['J'],explicit_observation_epoch_J=physical/2,
                 cost_abs_diff=abs(rec['J']-physical/2))
        assert max(push)<1e-13 and out['independent_transition_residual']<1e-10 and out['cost_abs_diff']<1e-10
        return out
    finally:
        CL.C.choose_N=original


def stationary_plugin_counterexample():
    # Symmetric two-state CTMC, flip rate 1, T_int=1/2; phi(x)=x.
    # True switch-minus-stay instantaneous gap = 2X-1.
    # A deliberately wrong policy: bounded negative G is allowed by T12.
    tau=1.
    Q=np.array([[-1.,1.],[1.,-1.]])
    pi=np.array([.5,.5]); action=np.array([0.,1.]); gap=np.array([-1.,1.])
    rows=[]
    for h in (15.,150.):
        b=.5*gap*(1-np.exp(-2*h))
        # Joint law of old state y and current x.
        joint=pi[:,None]*expm(Q*tau)
        g=float(np.sum(joint*(action[:,None]-action[None,:])*b[None,:]))
        exact=-(1-np.exp(-2*tau))*(1-np.exp(-2*h))/4
        assert abs(g-exact)<1e-14
        rows.append(dict(h=h,h_Tint=h/.5,tau=tau,G=g,pct_denominator_h=100*g/h,
                         D1_style_no_SE=(100*g/h>=-.25)))
    # Separate proof gap: E[D|Z_t] alone is not enough to multiply by an old
    # action unless Z_t is sufficient for future costs conditional on history.
    # iid Bernoulli Z_j, D=sum_{k=0}^{h-1}(2 Z_{k-1}-1), h=3.
    actual=claimed=0.
    for z in itertools.product((0,1),repeat=4): # Z_-1,Z_0,Z_1,Z_2
        diff=z[0]-z[1]
        D=sum(2*z[k]-1 for k in range(3))
        b=2*z[1]-1  # E[D|Z_0], exactly, h>=2
        actual+=diff*D/16
        claimed+=diff*b/16
    assert actual==0 and claimed==-.5
    return dict(mixing_plugin_negative_but_bounded=rows,
                conditioning_gap=dict(actual_G=actual,T12_rhs_without_history_sufficiency=claimed,
                                      note='The equality fails for insufficient Z, not a refutation of the Markov theorem.'))


def crn_and_lindley():
    # Scalar event-by-event reference and zero-effect controls.
    rng=np.random.default_rng(78142)
    maxerr=0.
    for _ in range(100):
        h=2.;n=int(rng.integers(0,10));q=int(rng.integers(0,5))
        arrivals=np.sort(rng.uniform(0,h,n)); services=rng.exponential(.1,n)
        initial=rng.exponential(.1,q)
        clock=0.;ref=0.
        for sv in initial:
            clock+=sv;ref+=min(clock,h)
        for t,sv in zip(arrivals,services):
            clock=max(clock,t)+sv;ref+=max(0.,min(clock,h)-t)
        got=P.lindley_cost(np.array([q]),arrivals[None,:],services[None,:],initial[None,:],h)[0]
        maxerr=max(maxerr,abs(got-ref))
    c=dict(id='crn',cls='mmpp2',lamA=7.,lamB=7.5,u=0.,params=dict(kappa=.5))
    bg,both=P.long_run_crn(c,30.,np.random.default_rng(12))
    long_identical=all(np.array_equal(both[0][j][v],both[1][j][v]) for j in (0,1) for v in (0,1))
    costs=P.futures(np.array([[2,3],[0,1]]),np.array([1.,2.]),bg,c,3.,np.random.default_rng(16))
    assert maxerr<1e-13 and long_identical and np.array_equal(costs[:,0],costs[:,1])
    return dict(scalar_lindley_100_max_abs=maxerr,zero_u_long_run_CRN_bitwise=long_identical,
                zero_u_future_CRN_bitwise=bool(np.array_equal(costs[:,0],costs[:,1])))


def periodic_phase():
    # Use a tiny new artificial trace, never a new physical study coordinate.
    f=OUT/'toy_periodic.npz'
    np.savez(f,s0=np.array([0,1,3,4]))
    p=dict(series=str(f),bin=.05)
    phase_log=[]
    orig=TC.arrivals
    def traced(lam,params,T,rng):
        probe=np.random.default_rng();probe.bit_generator.state=rng.bit_generator.state
        phase_log.append(float(probe.uniform(0,.2)))
        return orig(lam,params,T,rng)
    TC.arrivals=traced
    try:
        c=dict(id='phase',cls='trace_cox',lamA=7.,lamB=7.5,u=1.,params=p)
        for T in (20.,21.):
            P.long_run(c,0,T,np.random.default_rng(123))
    finally:
        TC.arrivals=orig
    # For a unit-period square-wave intensity, its exact autocovariance at kL
    # equals its variance at all integer k. There is no finite mixing time.
    x=np.r_[np.zeros(50),np.full(50,2.)];x-=x.mean()
    cyc=[float(x@np.roll(x,k)/len(x)) for k in (0,100,200,1000)]
    assert phase_log[0]==phase_log[2] and phase_log[1]!=phase_log[3]
    return dict(phases_T20=phase_log[:2],phases_T21=phase_log[2:],
                same_seed_different_duration_changes_path_B_phase=True,
                periodic_intensity_covariance_at_integer_periods=cyc,
                relative_phase_constant_over_all_cycles=True,
                square_wave_joint_intensity_product=dict(
                    phase_aligned_time_mean=2.,half_period_offset_time_mean=0.,
                    independent_uniform_phases_ensemble_mean=1.))


def tau_validation():
    c=dict(id='tau_validation',cls='mmpp2',lamA=7.,lamB=7.5,u=1.,params=dict(kappa=.5))
    accepted=[]
    for tau in (-1.,float('nan'),50000.):
        try:
            P.validate(dict(c,tau=tau,train_T=20000.))
            accepted.append(str(tau))
        except Exception:
            pass
    return dict(invalid_tau_values_accepted=accepted,current_scored_cases_affected=False)


def alarm_population():
    # Birth/death chain 0<->1<->2 at unit rates. Uniform stationary law.
    # Occupancy conditional on q>=1 differs from the first upward crossing of 1.
    occupancy=np.array([0.,.5,.5])
    crossing=np.array([0.,1.,0.])
    outcome=np.array([0.,-1.,3.])
    return dict(stationary_threshold_occupancy=occupancy.tolist(),
                upward_crossing_entry_population=crossing.tolist(),
                toy_signed_outcome_occupancy=float(occupancy@outcome),
                toy_signed_outcome_crossing=float(crossing@outcome),
                note='Synthetic population distinction; not an alternative EV-B score.')


def completion_gate():
    # Source ev_a_panel.py: A2 omits the card-wide 90% completion override.
    # A synthetic already-aggregated example, never a current panel score.
    completed,total,qualified,sign_correct=80,100,10,10
    implementation='NOT_EVALUABLE' if qualified<5 else ('PASS' if sign_correct/qualified>=.9 else 'FAIL')
    card='INCONCLUSIVE' if completed<.9*total else implementation
    return dict(completed=completed,total=total,A2_implementation=implementation,A2_card=card,
                current_panel_affected=False)


def main():
    out=dict(closed_loop=closed_loop_timing(),T12=stationary_plugin_counterexample(),
             packet=crn_and_lindley(),trace=periodic_phase(),validation=tau_validation(),
             alarm=alarm_population(),completion_gate=completion_gate())
    (OUT/'repro_checks.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':
    main()
