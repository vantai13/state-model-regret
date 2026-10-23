"""Doan Van Tai — N1 gap via idle identity, rational queue coordinates.

Fraction transition inputs give exact finite-law arithmetic. Float transition
inputs give finite precision expectations, not an exact physical R2 law.
"""
import math
from collections import defaultdict
from fractions import Fraction as F
from numbers import Rational

from smr.dominance import classify_state


def _sum(values):
    values=list(values)
    return sum(values,F(0)) if all(isinstance(v,Rational) for v in values) else math.fsum(values)


def _validate(q,mode,rates,extra,capacity,H,P,dt):
    if type(H) is not int or H<1 or mode not in rates or set(P)!=set(rates):
        raise ValueError('invalid horizon or modes')
    if not all(isinstance(v,Rational) and v>=0 for v in [q,extra,capacity,*rates.values()]):
        raise ValueError('amounts/backlogs must be nonnegative int/Fraction')
    if not isinstance(dt,Rational) or dt<=0: raise ValueError('positive rational dt required')
    for row in P.values():
        if set(row)!=set(rates) or not all(math.isfinite(v) and v>=0 for v in row.values()):
            raise ValueError('invalid transition probabilities')
        if not math.isclose(float(sum(row.values())),1,abs_tol=1e-14,rel_tol=0):
            raise ValueError('transition rows must sum to one')


def weighted_idle(q,mode,rates,extra,capacity,H,P,dt=F(1)):
    """E[dt sum_(k=0..H-1)(H-k)*idle_k], without computing occupancy costs."""
    _validate(q,mode,rates,extra,capacity,H,P,dt)
    mass={(F(q),mode):F(1)}; terms=[]
    for k in range(H):
        following=defaultdict(list)
        terms.append((H-k)*_sum(p*max(F(0),capacity-q-rates[m]-extra) for (q,m),p in mass.items()))
        for (q,m),p in mass.items():
            end=max(F(0),q+rates[m]+extra-capacity)
            for n,chance in P[m].items():
                if chance>0: following[end,n].append(p*chance)
        mass={state:_sum(parts) for state,parts in following.items()}
    return dt*_sum(terms)


def mean_weighted_idle(q,mode,rates,extra,capacity,H,P,dt=F(1)):
    """Mean-path idle with rationalized input P; not exact transcendental R2."""
    _validate(q,mode,rates,extra,capacity,H,P,dt)
    rational={m:{n:F(v) for n,v in row.items()} for m,row in P.items()}
    if any(sum(row.values())!=1 for row in rational.values()):
        raise ValueError('rationalized transition rows must sum exactly to one')
    pm={m:F(m==mode) for m in rates}; q=F(q); total=F(0)
    for k in range(H):
        arrival=sum(pm[m]*rates[m] for m in rates)+extra
        idle=max(F(0),capacity-q-arrival)
        total+=(H-k)*idle
        q=max(F(0),q+arrival-capacity)
        pm={n:sum(pm[m]*rational[m][n] for m in rates) for n in rates}
    return dt*total


def gap_from_idle(state,plant,model='M1'):
    """Plant slots/amounts; state=(qA,mA,qB,mB). Certificates assert, never clamp."""
    if model not in ('M0','M1'): raise ValueError('model must be M0 or M1')
    function=weighted_idle if model=='M1' else mean_weighted_idle
    qa,ma,qb,mb=state; u,H,dt=plant['u'],plant['H'],plant.get('dt',F(1))
    values=[]
    for q,m,rates,c,P,isB in ((qa,ma,plant['ratesA'],plant['cA'],plant['PA'],False),
                              (qb,mb,plant['ratesB'],plant['cB'],plant['PB'],True)):
        stay=function(q,m,rates,u if not isB else 0,c,H,P,dt)
        switch=function(q,m,rates,u if isB else 0,c,H,P,dt)
        values.extend((switch,-stay))
    gap=_sum(values)
    flags=classify_state(*state,plant)
    if flags['label']=='conservation' and gap!=0:
        raise ArithmeticError('conservation certificate violated')
    if (flags['SD1'] or flags['SD2']) and gap<0:
        raise ArithmeticError('SD sign certificate violated')
    if (flags['WD1'] or flags['WD2']) and gap>0:
        raise ArithmeticError('WD sign certificate violated')
    return gap


def resolve_sign(gap,error_bound=None,exact_zero=False):
    """Return final strict action only if the supplied interval resolves it.

    error_bound must be justified by the caller; this API does not invent an
    error estimate. A numerical band cannot change a small negative true gap.
    """
    if not math.isfinite(gap): raise ValueError('finite gap required')
    if exact_zero:
        if gap!=0: raise ArithmeticError('claimed exact zero is not zero')
        return dict(resolved=True,action='Stay',reason='exact_zero_certificate')
    if error_bound is None:
        if not isinstance(gap,Rational): raise ValueError('float gap requires an error bound')
        error_bound=F(0)
    if not math.isfinite(error_bound) or error_bound<0: raise ValueError('nonnegative finite error bound')
    low,high=gap-error_bound,gap+error_bound
    if low>=0: return dict(resolved=True,action='Stay',reason='nonnegative_interval')
    if high<0: return dict(resolved=True,action='Switch',reason='negative_interval')
    return dict(resolved=False,action=None,reason='precision_escalation_required')


def precision_summary(entries,C_ref,relative=1e-9,alarm=.01):
    """entries=(gap,probability,certified_zero); report-only band after Cref allowed."""
    if not all(math.isfinite(v) for v in (C_ref,relative,alarm)) or C_ref<0 or relative<0 or not 0<=alarm<=1:
        raise ValueError('invalid numeric policy')
    certified=uncertain=total=0.
    for gap,prob,zero in entries:
        if not math.isfinite(gap) or not math.isfinite(prob) or prob<0: raise ValueError('invalid entry')
        total+=prob
        if zero:
            if gap!=0: raise ArithmeticError('false exact-zero certificate')
            certified+=prob
        elif abs(gap)<=relative*C_ref: uncertain+=prob
    if not math.isclose(total,1,abs_tol=1e-12,rel_tol=0): raise ValueError('probabilities must sum to one')
    return dict(certified_tie_mass=certified,uncertified_band_mass=uncertain,
                escalation_required=uncertain>alarm,band=relative*C_ref)
