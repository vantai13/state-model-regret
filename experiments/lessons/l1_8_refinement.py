"""Doan Van Tai — L1.8B finite-law refinement by state aggregation.

The teaching cell has deterministic A and Markov-modulated B. B backlog is stored
as integer multiples of 1/m packet; probabilities and costs use the selected
floating dtype. No sampling. M1 is exact in finite-law summation, not arithmetic.
"""
import math
import time
from fractions import Fraction as F

import numpy as np

from experiments.lessons.l1_4_factorial import contrasts

CELLS=('00','10','01','11')
CONTRASTS=('G_S','G_M','G_SM','Gamma','G_S|M1','G_M|S1')


def params_at(m,lam_coarse=.25,managed_rate=2,dtype=np.float64):
    if type(m) is not int or m<1 or type(managed_rate) is not int or managed_rate<0:
        raise ValueError('m positive integer; managed_rate nonnegative integer')
    if not 0<lam_coarse<1:
        raise ValueError('physical symmetric embedding requires 0<lambda_coarse<1')
    dt=F(1,m)
    # dtype-native log/exp is important for the independent precision comparison.
    lam=np.exp(np.log(dtype(lam_coarse))/dtype(m))
    return dict(m=m,dt=dt,cA=F(3,m),cB=F(3,m),u=F(managed_rate,m),bA=F(1,m),
                rate_on=F(5,m),rate_off=F(0),p_onon=(1+lam)/2,p_offoff=(1+lam)/2,
                lam=lam,H=2*m,tau=m,y=(2,0),managed_rate=managed_rate,dtype=dtype,
                T_mode= -2/math.log(lam_coarse),lam_coarse=lam_coarse)


def _prehistory(p):
    """D12 law from the declared initialization; modes refer to START of each slot."""
    m,dtype=p['m'],p['dtype']
    keep=p['p_onon']
    mass=np.zeros((2*m+1,2),dtype=dtype)
    mass[0,:]=dtype(.5)
    active=0
    for _ in range(p['tau']):
        next_mass=np.zeros_like(mass)
        for mode,increment in ((0,-3),(1,2)):
            qnext=np.maximum(0,np.arange(active+1)+increment)
            weights=mass[:active+1,mode]
            # add.at handles several off-mode backlogs clipping to zero.
            np.add.at(next_mass[:,mode],qnext,weights*keep)
            np.add.at(next_mass[:,1-mode],qnext,weights*(1-keep))
        mass=next_mass
        active+=2
    return mass


def episode_distribution(p):
    """Evaluator-only D; do not pass it to the S0 decision interface."""
    return _prehistory(p)


def belief_from_observation(p):
    """S0 receives y/law via p; no evaluator realization/distribution parameter."""
    return _prehistory(p)


def _A_cost(p,action):
    m=p['m']
    u=p['managed_rate']
    # The A state at t0 is generated from y under prehistory Stay.
    qa=max(0,2*m+p['tau']*(1+u-3))
    total=0
    delta=1+(u if action=='Stay' else 0)-3
    for _ in range(p['H']):
        qa=max(0,qa+delta)
        total+=qa
    return p['dtype'](total)/p['dtype'](m*m)


def exact_cost_table(p,action):
    """Backward DP for every qB in D and both current modes; current mode fixed.

    Domain shrinks at each backward step, so no artificial upper truncation of q.
    V_h(q,mode)=q_next/m^2+E[V_(h-1)(q_next,mode_next)].
    """
    if action not in ('Stay','Switch'):
        raise ValueError('invalid action')
    m,H,dtype=p['m'],p['H'],p['dtype']
    u=p['managed_rate'] if action=='Switch' else 0
    increments=(u-3,u+2)
    grow=max(0,*increments)
    start_max=2*m
    values=np.zeros((start_max+H*grow+1,2),dtype=dtype)
    keep=p['p_onon']
    scale=dtype(m*m)
    for h in range(1,H+1):
        limit=start_max+(H-h)*grow
        grid=np.arange(limit+1)
        result=np.empty((limit+1,2),dtype=dtype)
        for mode,increment in enumerate(increments):
            qnext=np.maximum(0,grid+increment)
            result[:,mode]=qnext/scale+keep*values[qnext,mode]+(1-keep)*values[qnext,1-mode]
        values=result
    return values+_A_cost(p,action)


def mean_cost_table(p,action):
    if action not in ('Stay','Switch'):
        raise ValueError('invalid action')
    m,H,dtype=p['m'],p['H'],p['dtype']
    q=np.repeat(np.arange(2*m+1,dtype=dtype)[:,None],2,axis=1)
    prob_on=np.array([0,1],dtype=dtype)
    total=np.zeros_like(q)
    keep=p['p_onon']
    u=p['managed_rate'] if action=='Switch' else 0
    for _ in range(H):
        q=np.maximum(0,q+5*prob_on+u-3)
        total+=q
        prob_on=prob_on*keep+(1-prob_on)*(1-keep)
    return total/dtype(m*m)+_A_cost(p,action)


def solve_level(m,lam_coarse=.25,managed_rate=2,dtype=np.float64):
    started=time.perf_counter()
    p=params_at(m,lam_coarse,managed_rate,dtype)
    D=episode_distribution(p)
    b=belief_from_observation(p)  # one shared belief, outside per-state decision loop
    assert np.array_equal(D,b)
    J=np.stack([exact_cost_table(p,a) for a in ('Stay','Switch')],axis=-1)
    M=np.stack([mean_cost_table(p,a) for a in ('Stay','Switch')],axis=-1)
    # Arrays index (qB units, mode, action); 0 Stay,1 Switch. Strict ties Stay.
    d10=M[:,:,1]-M[:,:,0]
    d11=J[:,:,1]-J[:,:,0]
    pred0=np.sum(b[:,:,None]*M,axis=(0,1))
    pred1=np.sum(b[:,:,None]*J,axis=(0,1))
    d00=pred0[1]-pred0[0]
    d01=pred1[1]-pred1[0]
    a00,a01=int(d00<0),int(d01<0)
    a10=(d10<0).astype(int)
    a11=(d11<0).astype(int)
    ell={'00':J[:,:,a00],'01':J[:,:,a01],
         '10':np.take_along_axis(J,a10[:,:,None],axis=2)[:,:,0],
         '11':np.take_along_axis(J,a11[:,:,None],axis=2)[:,:,0]}
    L={c:np.sum(D*ell[c]) for c in CELLS}
    star=np.sum(D*np.min(J,axis=2))
    gains=contrasts(*(L[c] for c in CELLS))
    current={}
    current_actions={}
    current_deltas={}
    qmass=np.sum(D,axis=1)
    posterior_q=np.divide(D,qmass[:,None],out=np.zeros_like(D),where=qmass[:,None]>0)
    for name,predictions in (('M0',M),('M1',J)):
        pred_q=np.sum(posterior_q[:,:,None]*predictions,axis=1)
        current_deltas[name]=pred_q[:,1]-pred_q[:,0]
        aq=(current_deltas[name]<0).astype(int)
        current_actions[name]=aq
        selected=np.take_along_axis(J,aq[:,None,None].repeat(2,axis=1),axis=2)[:,:,0]
        current[name]=np.sum(D*selected)
    I=d11-d10-d01+d00
    meanI=np.sum(D*I)
    support=D>0
    deltas={'00':np.full_like(D,d00),'10':d10,'01':np.full_like(D,d01),'11':d11}
    actions={'00':np.full(D.shape,a00),'10':a10,'01':np.full(D.shape,a01),'11':a11}
    cost_scale=max(1,float(np.max(np.abs(J))))
    alert=64*np.finfo(dtype).eps*p['H']*cost_scale
    diagnostics={}
    for c,d in deltas.items():
        vals=d[support]
        diagnostics[c]=dict(min_abs=float(np.min(np.abs(vals))),exact_zero_states=int(np.sum(vals==0)),
                            alerted_states=int(np.sum((np.abs(vals)<alert)&(vals!=0))),
                            alerted_mass=float(np.sum(D[(np.abs(d)<alert)&(d!=0)])))
    for model,d in current_deltas.items():
        vals=d[qmass>0]
        diagnostics['current_'+model]=dict(min_abs=float(np.min(np.abs(vals))),
            exact_zero_states=int(np.sum(vals==0)),alerted_states=int(np.sum((np.abs(vals)<alert)&(vals!=0))),
            alerted_mass=float(np.sum(qmass[(np.abs(d)<alert)&(d!=0)])))
    summary=dict(m=m,dt=float(p['dt']),H=p['H'],tau=p['tau'],p_stay=float(p['p_onon']),
                 support_states=int(np.sum(support)),mass=float(np.sum(D)),Lstar=float(star),
                 **{f'L{c}':float(L[c]) for c in CELLS},**{k:float(v) for k,v in gains.items()},
                 R11=float(L['11']-star),mean_I_delta=float(meanI),
                 L_current_M0=float(current['M0']),L_current_M1=float(current['M1']),
                 freshness=float(L['00']-current['M0']),mode_visibility=float(current['M0']-L['10']),
                 freshness_M1=float(L['01']-current['M1']),mode_visibility_M1=float(current['M1']-L['11']),
                 hybrid_freshness=float(L['00']-current['M1']),hybrid_mode=float(current['M1']-L['10']),
                 numerical_alert=float(alert),wall_seconds=time.perf_counter()-started,
                 max_B_backlog_grid_units=2*m+p['H']*(p['managed_rate']+2),
                 dtype=np.dtype(dtype).name)
    summary['mode_share']=summary['mode_visibility']/summary['G_S'] if summary['G_S']!=0 else None
    summary['hybrid_mode_share']=summary['hybrid_mode']/summary['G_S'] if summary['G_S']!=0 else None
    tol=1e-10
    assert abs(summary['mass']-1)<tol and summary['R11']==0
    assert summary['G_M']>=-tol and abs(summary['mean_I_delta'])<tol
    assert abs(summary['freshness']+summary['mode_visibility']-summary['G_S'])<tol
    return dict(summary=summary,params=p,D=D,J=J,M=M,deltas=deltas,actions=actions,
                current_actions=current_actions,current_deltas=current_deltas,near_ties=diagnostics)


def pair_check(coarse,fine,C_ref,tolerance_fraction=.01):
    if C_ref<=0 or tolerance_fraction<=0:
        raise ValueError('C_ref and tolerance must be positive')
    limit=C_ref*tolerance_fraction
    rows=[]
    for metric in CONTRASTS:
        a,b=coarse[metric],fine[metric]
        flip=a*b<0 and max(abs(a),abs(b))>limit
        rows.append(dict(coarse_m=coarse['m'],fine_m=fine['m'],metric=metric,
                         coarse=a,fine=b,abs_change=abs(b-a),change_over_Cref=abs(b-a)/C_ref,
                         tolerance_fraction=tolerance_fraction,sign_violation=flip,
                         passed=abs(b-a)<=limit and not flip))
    return rows


def triplet_diagnostic(a,b,c,metric):
    d1=a[metric]-b[metric]
    d2=b[metric]-c[metric]
    return dict(coarse_m=a['m'],middle_m=b['m'],fine_m=c['m'],metric=metric,
                first_difference=d1,second_difference=d2,rho_conv=None if d1==0 else d2/d1,
                richardson_from_first=2*b[metric]-a[metric],
                richardson_from_last=2*c[metric]-b[metric],
                flat_three=d1==0 and d2==0)
