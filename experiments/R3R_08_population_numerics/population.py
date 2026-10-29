"""Same P1 four-cell estimand; direct stationary S1 and exact stay-cost moment.

Only numerical representations change. K-refinement remains a diagnostic (R7),
separate from kernel/roundoff/moment enclosures. No CF generation at import/run.
"""
from fractions import Fraction as F
import math
from pathlib import Path
import time
import numpy as np
from .piecewise import LD,EPS,number
from . import law_cache,profiles,quadrature

CONTRASTS=('G_S','G_M','G_SM','Gamma','G_S_M1','G_M_S1')


def contrasts(L):
    gs=L['00']-L['10'];gm=L['00']-L['01'];gsm=L['00']-L['11']
    return dict(G_S=gs,G_M=gm,G_SM=gsm,Gamma=gsm-gs-gm,G_S_M1=L['01']-L['11'],G_M_S1=L['10']-L['11'])


def side(lam,pre,post,kappa,h,ref,K,cache,progress):
    unit,law,law_key=law_cache.get(lam,pre,kappa,ref,Path(cache)/'stationary',progress)
    budget=min(F(1,10000),F(h)**2/F(10_000_000))
    costs=profiles.get(lam,pre,post,kappa,h,ref,unit,Path(cache)/'profiles',cost_budget=budget,progress=progress)
    factor=costs['factor']
    cap=lambda names:max((int(costs['profiles'][name]['modes'][m][0][-1])+factor-1)//factor for name in names for m in (0,1))
    state=quadrature.build(law,K,cap(('d','dh')))
    observation=quadrature.build(law,K,cap(('old_d','old_h')))
    n=len(state['indices']);state_rows={key:np.empty((n,2),dtype=LD) for key in ('d','h','ed','eh')}
    state_zero=np.zeros((n,2),dtype=bool);state_sat=np.zeros((n,2),dtype=bool)
    for m in (0,1):
        d,ed,zd,_=profiles.values(costs,'d',state['indices'],m)
        hh,eh,zh,sat=profiles.values(costs,'dh',state['indices'],m)
        state_rows['d'][:,m]=d;state_rows['ed'][:,m]=ed;state_rows['h'][:,m]=hh;state_rows['eh'][:,m]=eh
        state_zero[:,m]=zh;state_sat[:,m]=sat
    current=dict(**{k:v.ravel() for k,v in state_rows.items()},w=state['mass'].ravel(),
                 w_error=state['l1_error'],zero_h=state_zero.ravel(),sat_h=state_sat.ravel())
    q=observation['indices'];valid=q>=0;prior=np.zeros(len(q),dtype=LD);ep=np.zeros(len(q),dtype=LD)
    prior[valid],ep[valid]=law.posterior(q[valid])
    old=dict(w=observation['mass'].sum(axis=1,dtype=LD),w_error=observation['l1_error'])
    for name,key,ekey in [('old_d','d','ed'),('old_h','h','eh')]:
        off,eo,zo,_=profiles.values(costs,name,q,0);on,en,zn,_=profiles.values(costs,name,q,1)
        value=(1-prior)*off+prior*on
        error=eo+en+ep*(abs(on-off)+eo+en)+128*EPS*(abs(off)+abs(on)+1)
        zero=zo&zn;value[zero]=0;error[zero]=0
        old[key]=value;old[ekey]=error
        if key=='h':old['zero_h']=zero
    old['sat_h']=np.zeros(len(q),dtype=bool)
    return dict(current=current,old=old,mean=law.mean*number(unit),
                mean_error=law.mean_error*abs(number(unit))+32*EPS*(abs(law.mean*number(unit))+1),
                law_key=law_key,profile_key=costs['key'],
                law_cold_cpu_seconds=law.cold_cpu_seconds,law_created_cpu_seconds=law.last_creation_cpu_seconds,
                profile_cold_cpu_seconds=costs['cold_cpu_seconds'],profile_created_cpu_seconds=costs['created_cpu_seconds'],
                law_error=str(law.law.error),posterior_error_max=float(max(ep)),
                kernel_error_max=float(max(costs['profiles'][k]['error'] for k in costs['profiles'])*LD(costs['scale'])),
                state_weight_l1_error=str(state['l1_error']),observation_weight_l1_error=str(observation['l1_error']),
                complete_tail_atom=True,renormalized=False)


def pair_loss(A,B,cost=F(0),*,model='true'):
    d=A['d'][:,None]+B['d'][None,:]+number(cost)
    ed=A['ed'][:,None]+B['ed'][None,:]+64*EPS*(abs(d)+1)
    if model=='true':h=d;eh=ed
    elif model=='mean':
        h=A['h'][:,None]+B['h'][None,:]+number(cost)
        eh=A['eh'][:,None]+B['eh'][None,:]+64*EPS*(abs(h)+1)
    else:raise ValueError('unknown action model')
    if model=='mean':
        certified=(A['zero_h'][:,None]&B['zero_h'][None,:])|(A['sat_h'][:,None]&B['sat_h'][None,:])
        h=np.where(certified,number(cost),h);eh=np.where(certified,LD(0),eh)
    weights=A['w'][:,None]*B['w'][None,:]
    switch=h<0;ambiguous=(h-eh<0)&(h+eh>=0)
    contribution=np.where(switch,d,LD(0))
    loss=(weights*contribution).sum(dtype=LD)
    error=(weights*np.where(ambiguous,abs(d)+ed,np.where(switch,ed,LD(0)))).sum(dtype=LD)
    maxcost=max(LD(1),np.max(abs(d)+ed))
    error+=(A['w_error']+B['w_error']+A['w_error']*B['w_error'])*maxcost
    error+=1024*weights.size*EPS*maxcost
    return loss,error,float(weights[ambiguous].sum(dtype=LD))


def evaluate(spec,cache,progress=lambda *a,**k:None,*,identical_models=False):
    rid,lamA,lamB,kappa,eta,h,ref,K,*rest=spec
    lamA,lamB,kappa,eta,h=map(F,(lamA,lamB,kappa,eta,h));u=2*eta;c=F(rest[0]) if rest else F(0)
    if min(lamA,lamB)<6 or max(lamA+u,lamB+u)>=10:raise ValueError('outside fixed stable nonnegative plant')
    begin=time.monotonic();progress('population_started',id=rid,K=K,ref=ref)
    A=side(lamA,u,F(0),kappa,h,ref,K,cache,progress)
    B=side(lamB,F(0),u,kappa,h,ref,K,cache,progress)
    # P1 and Stay preserve each pre-decision stationary queue. Thus E[JStay]
    # is exactly h*E[QA+QB]; it needs a moment certificate, not a TV shortcut.
    base=number(h)*(A['mean']+B['mean'])
    ebase=abs(number(h))*(A['mean_error']+B['mean_error'])+128*EPS*(abs(base)+1)
    losses={};errors={};ambiguity={}
    for key,kind,model in [('00','old','mean'),('01','old','true'),('10','current','mean'),('11','current','true')]:
        action_model='mean' if identical_models else model
        gap,error,uncertain=pair_loss(A[kind],B[kind],c,model=action_model)
        losses[key]=base+gap;errors[key]=ebase+error+64*EPS*(abs(base)+abs(gap)+1);ambiguity[key]=uncertain
    G=contrasts(losses)
    eG=dict(G_S=errors['00']+errors['10'],G_M=errors['00']+errors['01'],G_SM=errors['00']+errors['11'],
            Gamma=errors['00']+errors['01']+errors['10']+errors['11'],G_S_M1=errors['01']+errors['11'],G_M_S1=errors['10']+errors['11'])
    if u==0 and c==0:
        # Equal managed loads give identical actions for every state and future.
        # This is a structural certificate, not epsilon clipping.
        G={name:LD(0) for name in CONTRASTS};eG={name:LD(0) for name in CONTRASTS}
    Cref=losses['11'];ec=errors['11']
    if Cref<=ec:raise ArithmeticError('positive Cref not certified')
    normalized_errors={name:(eG[name]+abs(G[name]/Cref)*ec)/(Cref-ec)+256*EPS for name in CONTRASTS}
    validity=[]
    currentA,currentB=A['current'],B['current']
    ED=(currentA['w']*currentA['d']).sum(dtype=LD)+(currentB['w']*currentB['d']).sum(dtype=LD)+number(c)
    stakes=ED-2*(losses['11']-base)
    stake_error=errors['11']*2+sum((s['w']*s['ed']).sum(dtype=LD)+s['w_error']*max(LD(1),np.max(abs(s['d']))) for s in (currentA,currentB))+512*EPS*(abs(ED)+abs(base)+1)
    oldA,oldB=A['old'],B['old'];gap=oldA['d'][:,None]+oldB['d'][None,:]+number(c)
    forecast=oldA['h'][:,None]+oldB['h'][None,:]+number(c)
    flip=((forecast<0)!=(gap<0));old_weights=oldA['w'][:,None]*oldB['w'][None,:]
    flip_stakes=(old_weights*abs(gap)*flip).sum(dtype=LD)
    identity_gap=G['G_M']-flip_stakes
    for key in ('G_M','G_SM','G_S_M1','G_M_S1'):
        if not identical_models and G[key]+eG[key]<0:validity.append('negative_nonnegative_contrast:'+key)
    if not identical_models and abs(identity_gap)>eG['G_M']+512*EPS*(abs(base)+abs(flip_stakes)+1):validity.append('model_gain_flip_identity')
    if not identical_models and abs(G['G_S'])-eG['G_S']>stakes+stake_error:validity.append('state_gain_exceeds_stakes')
    if not identical_models and abs(G['Gamma'])-eG['Gamma']>stakes+stake_error:validity.append('interaction_exceeds_stakes')
    row=dict(id=rid,Cref=str(Cref),**{k:str(v) for k,v in G.items()},K=K,ref=ref,dt=str(F(1,120*ref)),
             losses={k:str(v) for k,v in losses.items()},cost_error={k:str(v) for k,v in errors.items()},
             contrast_error={k:str(v) for k,v in eG.items()},normalized_error={k:str(v) for k,v in normalized_errors.items()},
             arithmetic_pass=max(normalized_errors.values())<=LD('0.00025') and not validity,
             validity_errors=validity,uncertain_action_mass=ambiguity,
             Sbar=str(stakes),Sbar_error=str(stake_error),GM_identity_gap=str(identity_gap),
             P_flip=str((old_weights*flip).sum(dtype=LD)),
             S1_route='direct_stationary_state',stay_cost_route='exact_stationary_first_moment',
             quadrature_error='R1 paired refinement diagnostic only; not a certified total error interval',
             zero_action_certificate=u==0 and c==0,identical_models_test=identical_models,
             stationary_error_max=max(float(A['law_error']),float(B['law_error'])),
             posterior_error_max=max(A['posterior_error_max'],B['posterior_error_max']),
             kernel_error_max=max(A['kernel_error_max'],B['kernel_error_max']),
             source_components={key:{k:v for k,v in value.items() if k not in ('current','old','mean','mean_error')} for key,value in [('A',A),('B',B)]},
             CF_computed=False,wall_seconds=time.monotonic()-begin)
    progress('population_completed',id=rid,K=K,ref=ref,arithmetic_pass=row['arithmetic_pass'])
    return row
