"""Doan Van Tai — exact E0 bookkeeping under one observation and b=D."""
from fractions import Fraction as F


def statistics(rows):
    """Rows=(prob,J_stay,J_switch,M0_stay,M0_switch), rational inputs only."""
    rows=list(rows)
    if not rows or any(len(r)!=5 for r in rows): raise ValueError('nonempty five-field rows required')
    if any(not isinstance(v,(int,F)) for r in rows for v in r): raise ValueError('rational reference inputs required')
    if any(r[0]<0 for r in rows) or sum(r[0] for r in rows)!=1: raise ValueError('normalized nonnegative D required')
    Js=[sum(r[0]*r[i] for r in rows) for i in (1,2)]
    Ms=[sum(r[0]*r[i] for r in rows) for i in (3,4)]
    gap=Js[1]-Js[0]; model_gap=Ms[1]-Ms[0]
    a00,a01=int(model_gap<0),int(gap<0)
    oracle=sum(p*min(st,sw) for p,st,sw,_,_ in rows)
    positive=sum(p*max(0,sw-st) for p,st,sw,_,_ in rows)
    negative=sum(p*max(0,st-sw) for p,st,sw,_,_ in rows)
    GM=Js[a00]-Js[a01]; state_gain=Js[a01]-oracle
    assert GM==abs(gap)*(a00!=a01)
    assert GM<=abs(model_gap-gap)
    assert state_gain==min(positive,negative)
    return dict(E_delta=gap,E_model_delta=model_gap,model_bias=model_gap-gap,
                E_positive=positive,E_negative=negative,a00=a00,a01=a01,
                L00=Js[a00],L01=Js[a01],L11=oracle,G_M=GM,G_S_given_M1=state_gain)
