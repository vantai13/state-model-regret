"""Doan Van Tai — independent forward mass propagation for L1.8B costs.

Does not import backward DP, mean-rollout or action-selection functions. Accepts
fixed actions for scoring only. Rebuilds the episode law from its initialization.
"""
import numpy as np


def propagate_B(initial, slots, p_keep, managed_B, m):
    mass=initial.copy()
    accumulated=0.
    for _ in range(slots):
        increments=(managed_B-3,managed_B+2)
        grow=max(0,*increments)
        next_mass=np.zeros((mass.shape[0]+grow,2))
        grid=np.arange(mass.shape[0])
        for mode,increment in enumerate(increments):
            end=np.maximum(0,grid+increment)
            accumulated+=float(np.dot(mass[:,mode],end))/(m*m)
            for next_mode,conditional in ((mode,p_keep),(1-mode,1-p_keep)):
                next_mass[:,next_mode]+=np.bincount(end,weights=mass[:,mode]*conditional,
                                                   minlength=next_mass.shape[0])
        mass=next_mass
    return mass,accumulated


def check_level(solved):
    p=solved['params']
    m,H,tau=p['m'],p['H'],p['tau']
    keep=float(p['p_onon'])
    initial=np.array([[.5,.5]])
    D,_=propagate_B(initial,tau,keep,0,m)
    assert D.shape==solved['D'].shape
    D_error=float(np.max(np.abs(D-solved['D'])))
    qa0=max(0,2*m+(p['managed_rate']-2)*tau)
    def score(action_indices):
        cost=0.
        for a in (0,1):
            starting=np.where(action_indices==a,D,0.)
            mass=float(starting.sum())
            _,B_cost=propagate_B(starting,H,keep,p['managed_rate'] if a else 0,m)
            q=qa0
            A_sum=0
            for _ in range(H):
                q=max(0,q+(1+(0 if a else p['managed_rate'])-3))
                A_sum+=q
            cost+=B_cost+mass*A_sum/(m*m)
        return cost
    fields={}
    for c in ('00','10','01','11'):
        fields['L'+c+'_forward']=score(solved['actions'][c])
    for model in ('M0','M1'):
        a=solved['current_actions'][model][:,None].repeat(2,axis=1)
        fields['L_current_'+model+'_forward']=score(a)
    errors=[abs(fields['L'+c+'_forward']-solved['summary']['L'+c]) for c in ('00','10','01','11')]
    errors += [abs(fields['L_current_'+model+'_forward']-solved['summary']['L_current_'+model]) for model in ('M0','M1')]
    return dict(m=m,D_max_abs_error=D_error,max_aggregate_cost_error=max(errors),**fields)
