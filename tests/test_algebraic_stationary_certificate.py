"""Exact rational state-balance enumeration and independent true-law checks."""
from fractions import Fraction as F
import mpmath as mp
import pytest

from smr.stationary_spectral import SpectralLaw,lower,upper
from experiments.R3R_07_fast_stationary.algebraic_certificate import AlgebraicCertificateLaw


def exact_gauss(A,rhs):
    a=[list(row)+[value] for row,value in zip(A,rhs)];n=len(a)
    for k in range(n):
        pivot=next(i for i in range(k,n) if a[i][k]);a[k],a[pivot]=a[pivot],a[k]
        p=a[k][k];a[k]=[x/p for x in a[k]]
        for i in range(n):
            if i!=k:
                factor=a[i][k];a[i]=[x-factor*y for x,y in zip(a[i],a[k])]
    return [row[-1] for row in a]


@pytest.mark.parametrize('d,b,s',[(2,1,F(3,4)),(5,3,F(9,10)),(7,4,F(1,2))])
def test_residual_identity_by_exact_enumeration(d,b,s):
    roots=[F(i+1,b+2) for i in range(b)]
    v=[(1-s*r**d)*r**b/(1-s) for r in roots]
    A=[[vj*r**(-i-1) for r,vj in zip(roots,v)] for i in range(b-1)]
    A.append([vj/(1-s)+(1+vj)*r/(1-r) for r,vj in zip(roots,v)])
    c=exact_gauss(A,[F(0)]*(b-1)+[F(1)])
    on=sum(cj*vj for cj,vj in zip(c,v));zero=(on*s/(1-s),on)
    def mass(q,m):return zero[m] if q==0 else sum(cj*(vj if m else 1)*r**q for r,cj,vj in zip(roots,c,v))
    total=sum(zero)+sum(cj*(1+vj)*r/(1-r) for r,cj,vj in zip(roots,c,v))
    assert total==1
    for q in range(1,d+b+5):
        from_on=mass(q-b,1) if q>=b else F(0)
        off=mass(q,0)-s*mass(q+d,0)-(1-s)*from_on
        on=mass(q,1)-(1-s)*mass(q+d,0)-s*from_on
        predicted=-sum(cj*(s*r**(d+b)-(2*s-1)*r**d-r**b+s)*r**q for cj,r in zip(c,roots))/(1-s)
        assert off==0 and on==predicted
    direct=sum(mass(q,0) for q in range(d+1))
    geometric=zero[0]+sum(cj*r*(1-r**d)/(1-r) for cj,r in zip(c,roots))
    assert direct==geometric


@pytest.mark.parametrize('s',[F(1,2),F(3,4),F(9,10)])
def test_certificate_covers_actual_closed_form_error(s):
    law=AlgebraicCertificateLaw((-2,1),s)
    def encode(x):
        z=mp.mpc(x)
        return mp.nstr(z.real,80),mp.nstr(z.imag,80)
    declared=[tuple(encode(x) for x in term) for term in law.terms]
    zero=[encode(x) for x in law.zero]
    with mp.workdps(150):
        p=mp.mpf(s.numerator)/s.denominator
        r=(-(1-p)+mp.sqrt((1-p)**2+4*p*p))/(2*p);v=r*(1+r)
        a=1/(v/(1-p)+(1+v)*r/(1-r))
        error=mp.mpf(0)
        terms=[tuple(mp.mpc(*x) for x in t) for t in declared]
        N=5000
        for q in range(N):
            for m in (0,1):
                proposed=mp.mpc(*zero[m]) if q==0 else sum(t[m+1]*t[0]**q for t in terms)
                expected=a*v*(p/(1-p) if m==0 else 1) if q==0 else a*r**q*(v if m else 1)
                error+=abs(proposed-expected)
        # Independent upper bound on the complete TV error, including both tails.
        true_tail=abs(a)*(1+abs(v))*abs(r)**N/(1-abs(r))
        proposed_tail=sum((abs(t[1])+abs(t[2]))*abs(t[0])**N/(1-abs(t[0])) for t in terms)
        assert (error+true_tail+proposed_tail)/2<mp.mpf(law.certificate['infinite_law_error_upper'])
    assert law.error<mp.mpf('1e-10')
    assert float(law.posterior(0)[1])<1e-8


def test_independent_original_certificate_also_accepts_same_proposal():
    law=AlgebraicCertificateLaw((-5,3),F(3,4))
    old=SpectralLaw.certify(law)
    assert mp.mpf(old['infinite_law_error_upper'])<mp.mpf('1e-10')
    reference=SpectralLaw((-5,3),F(3,4))
    for alpha in (F(1,2),F(9,10)):assert law.quantile(alpha)==reference.quantile(alpha)


def test_moderate_case_matches_reference_and_original_certificate():
    from smr.stationary import r2_keep
    keep,error=r2_keep(F(1,120),F(1,10))
    law=AlgebraicCertificateLaw((-77,43),keep,error)
    reference=SpectralLaw((-77,43),keep,error)
    assert mp.mpf(SpectralLaw.certify(law)['infinite_law_error_upper'])<mp.mpf('1e-10')
    for alpha in (F(1,2),F(9,10)):assert law.quantile(alpha)==reference.quantile(alpha)


def test_certificate_rejects_coefficient_and_root_corruption():
    for part in ('coefficient','root'):
        law=AlgebraicCertificateLaw((-5,3),F(3,4))
        r,a,b=law.terms[0]
        law.terms[0]=(r,a*mp.mpf('1.01'),b) if part=='coefficient' else (r*mp.mpf('.99'),a,b)
        with pytest.raises(ArithmeticError):law.certify()
