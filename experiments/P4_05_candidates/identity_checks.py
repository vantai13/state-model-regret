"""Exact finite teaching counterexamples; no plant, region or outcome data."""
from fractions import Fraction as F


def cells(gaps,forecasts,base=10):
    d,dh=tuple(map(F,gaps)),tuple(map(F,forecasts))
    if not d or len(d)!=len(dh):raise ValueError('aligned finite states required')
    p=F(1,len(d));base=F(base)
    mean=lambda xs:sum(xs,F(0))*p
    actions=dict(a00=[mean(dh)<0]*len(d),a01=[mean(d)<0]*len(d),
                 a10=[x<0 for x in dh],a11=[x<0 for x in d])
    L={k[1:]:base+mean([gap*action for gap,action in zip(d,aa)]) for k,aa in actions.items()}
    gs=L['00']-L['10'];gm=L['00']-L['01'];gamma=L['10']+L['01']-L['00']-L['11']
    return dict(losses=L,GS=gs,GM=gm,Gamma=gamma,GS_M1=L['01']-L['11'],
                GM_S1=L['10']-L['11'],Cref=L['11'],unit='arbitrary_teaching_cost')


def fixtures():
    return dict(
        SV_and_MV_both_hold=cells((1,1),(-3,1)),
        AB_without_SUB=cells((-4,2,4,6),(1,1,1,-10)),
        identity_lower_bound='Gamma >= -min(GS,GM)',
        SUB_implication='Gamma/Cref <= -1/100 implies GS/Cref >=1/100 and GM/Cref>=1/100',
        kappa_note='Identity has no kappa argument; a kappa flip requires a physical prediction, not algebra alone')
