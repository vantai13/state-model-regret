"""Doan Van Tai — deterministic verification fixtures, not candidate grid."""
import math
from fractions import Fraction as F
from smr.exact import value_backward


def conservation_cases(count=300):
    for i in range(count):
        dt=F(1,(120,96,80,60,48)[i%5]); H=12
        sa=(1+math.exp(-2*float(dt)/(0.3+(i%3))))/2
        sb=(1+math.exp(-2*float(dt)/(0.5+(i%7))))/2
        P=lambda s:{m:{n:s if m==n else 1-s for n in (0,1)} for m in (0,1)}
        plant=dict(cA=10*dt,cB=10*dt,u=dt,H=H,dt=dt,
                   ratesA={0:F(1,2)*dt,1:F(25,2)*dt},ratesB={0:2*dt,1:14*dt},PA=P(sa),PB=P(sb))
        yield (F(100+i,3),i%2,F(200+i%17,7),(i//2)%2),plant


def subtract_truth(state,plant):
    costs=[]
    for switch in (False,True):
        cost=0.
        for q,m,rates,c,P,isB in ((state[0],state[1],plant['ratesA'],plant['cA'],plant['PA'],False),
                                  (state[2],state[3],plant['ratesB'],plant['cB'],plant['PB'],True)):
            extra=plant['u'] if switch==isB else 0
            cost+=float(value_backward(extra,plant['H'],c,rates,P,[q],plant['dt'])[q,m])
        costs.append(cost)
    return costs[1]-costs[0]


def subtract_mean(state,plant):
    costs=[]
    for switch in (False,True):
        total=0.
        for q,m,rates,c,P,isB in ((state[0],state[1],plant['ratesA'],plant['cA'],plant['PA'],False),
                                  (state[2],state[3],plant['ratesB'],plant['cB'],plant['PB'],True)):
            q=float(q); pm={n:float(n==m) for n in rates}
            extra=float(plant['u']) if switch==isB else 0.
            for _ in range(plant['H']):
                a=sum(pm[n]*float(rates[n]) for n in rates)+extra
                q=max(0.,q+a-float(c)); total+=float(plant['dt'])*q
                pm={n:sum(pm[k]*P[k][n] for k in rates) for n in rates}
        costs.append(total)
    return costs[1]-costs[0]
