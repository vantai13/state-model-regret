"""Experimental algebraic evaluation of the original residual/return-time bound.

The target coefficients are interval evaluations of the exact Vandermonde null
vector. Boundary equations then hold by identity; the remaining positive-state
residual is bounded by the sparse root polynomial. Stored-coefficient error is
added in L1. Same infinite queue, precision and 1e-10 acceptance threshold.
Candidate only; independent exact-balance and closed-form tests are required.
"""
import mpmath as mp

from smr.stationary_spectral import lower,upper
from .law import BarycentricLaw


def algebraic_certificate(law,progress=None):
    d,b=-law.increments[0],law.increments[1]
    terms,zero_stored=law.intervals();iv=mp.iv
    center=iv.mpf(law.keep.numerator)/law.keep.denominator
    e=iv.mpf(law.keep_error.numerator)/law.keep_error.denominator
    s=iv.mpf([lower(center-e),upper(center+e)])
    roots=[t[0] for t in terms]
    radii=[abs(r) for r in roots]
    if any(upper(r)>=1 for r in radii):raise ArithmeticError('uncertified decaying root')
    derivative=[iv.mpc(1) for _ in roots]
    for i in range(b):
        for j in range(i):
            delta=roots[i]-roots[j]
            if lower(abs(delta))<=0:raise ArithmeticError('distinct roots not certified')
            derivative[i]*=delta;derivative[j]*=-delta
        if progress and (i%128==0 or i==b-1):progress('interval_products',rows=i+1,total=b)
    v=[(1-s*r**d)*r**b/(1-s) for r in roots]
    raw=[r**(b-1)/(vj*dj) for r,vj,dj in zip(roots,v,derivative)]
    normalizer=sum(cj*(vj/(1-s)+(1+vj)*r/(1-r)) for cj,r,vj in zip(raw,roots,v))
    if lower(abs(normalizer))<=0:raise ArithmeticError('normalizer not certified nonzero')
    c=[x/normalizer for x in raw]
    on=sum(cj*vj for cj,vj in zip(c,v));zero_target=(on*s/(1-s),on)
    incoming=zero_target[0]+sum(cj*r*(1-r**d)/(1-r) for cj,r in zip(c,roots))
    residual0=abs(zero_target[0]-s*incoming)+abs(zero_target[1]-(1-s)*incoming)
    positive=iv.mpf(0);tail=iv.mpf(0);difference=sum(abs(a-z) for a,z in zip(zero_stored,zero_target))
    K=law.plan['cutoff']
    for (r,a_stored,b_stored),rho,cj,vj in zip(terms,radii,c,v):
        polynomial=s*r**(d+b)-(2*s-1)*r**d-r**b+s
        positive+=abs(cj*polynomial)*rho/((1-s)*(1-rho))
        tail+=(abs(cj)+abs(cj*vj))*rho**(K+1)/(1-rho)
        difference+=(abs(a_stored-cj)+abs(b_stored-cj*vj))*rho/(1-rho)
    # Identical return-time supersolution and true-tail plan as ReferenceLaw.
    B=(d+b)/(2*(1-center));C=d/(center-e);drift=iv.mpf(d-b)/2-e*B
    if lower(drift)<=0:raise ArithmeticError('return bound has no positive drift')
    T=(K+B+C)/drift
    true_tail=iv.mpf(law.plan['tail_bound']);residual=residual0+positive
    error=(1+2*T)*(true_tail+tail)+T*residual+difference
    bound=upper(error)
    if bound>mp.mpf('1e-10'):raise ArithmeticError(f'algebraic spectral certificate fails: {bound}')
    return dict(method='barycentric_algebraic_interval_residual',digits=80,**law.plan,
                approximate_tail_upper=str(upper(tail)),normalization='exact target identity; stored error separately enclosed',
                stored_coefficient_l1_error_upper=str(upper(difference)),
                boundary_zero_residual_l1_upper=str(upper(residual0)),positive_residual_l1_upper=str(upper(positive)),
                residual_tv_upper=str(upper(residual)/2),return_time_upper=str(upper(T)),
                infinite_law_error_upper=str(bound),stored_terms=len(terms),physical_buffer=False)


class AlgebraicCertificateLaw(BarycentricLaw):
    def certify(self):return algebraic_certificate(self)
