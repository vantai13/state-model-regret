"""Independent dense solve / closed-form / certificate checks, synthetic laws only."""
from fractions import Fraction as F
import mpmath as mp
import pytest

from experiments.R3R_07_fast_stationary.law import barycentric_coefficients,BarycentricLaw
from smr.stationary_spectral import SpectralLaw,lower,upper
from smr.stationary import r2_keep


def test_coefficients_against_independent_dense_system():
    mp.mp.dps=80
    for roots in ([mp.mpf('0.2')],list(map(mp.mpc,('.2','.4','.7'))),
                  [mp.mpc('.3','.2'),mp.mpc('.3','-.2'),mp.mpc('.8')]):
        b=len(roots);s=mp.mpf('.8');v=[(1-s*r**5)*r**b/(1-s) for r in roots]
        matrix=mp.matrix(b);rhs=mp.matrix(b,1);rhs[b-1]=1
        for j in range(b):
            for i in range(b-1):matrix[i,j]=v[j]*roots[j]**(-i-1)
            matrix[b-1,j]=v[j]/(1-s)+(1+v[j])*roots[j]/(1-roots[j])
        expected=mp.lu_solve(matrix,rhs)
        actual=barycentric_coefficients(roots,v,s)
        assert max(abs(a-b) for a,b in zip(actual,expected))<mp.mpf('1e-65')


@pytest.mark.parametrize('increments,kappa,ref',[
    ((-2,1),F(1,10),1),((-5,3),F(3,10),1),((-7,5),F(1,10),1),
    ((-77,43),F(1,10),1),((-7,5),F(3),2),
])
def test_law_matches_unchanged_reference_and_passes_certificate(increments,kappa,ref):
    keep,error=r2_keep(F(1,120*ref),kappa)
    reference=SpectralLaw(increments,keep,error)
    candidate=BarycentricLaw(increments,keep,error)
    assert candidate.error<mp.mpf('1e-10')
    def center(z):
        return mp.mpc((lower(z.real)+upper(z.real))/2,(lower(z.imag)+upper(z.imag))/2)
    for q in (0,1,3,10,100):
        for a,b in zip(reference.point_interval(q),candidate.point_interval(q)):
            assert abs(center(a)-center(b))<mp.mpf('1e-50')
    for alpha in (F(1,2),F(9,10)):
        assert candidate.quantile(alpha)==reference.quantile(alpha)
    assert candidate.posterior(0)[1]<1e-8


def test_closed_form_and_no_dense_LU_dependency(monkeypatch):
    def forbidden(*a,**k):raise AssertionError('dense LU must not be used')
    monkeypatch.setattr(mp,'lu_solve',forbidden)
    s=F(3,4);law=BarycentricLaw((-2,1),s)
    p=mp.mpf(3)/4
    r=(-(1-p)+mp.sqrt((1-p)**2+4*p*p))/(2*p)
    v=r*(1+r);a=1/(v/(1-p)+(1+v)*r/(1-r))
    for q in (1,2,10,90):
        for m,value in enumerate(law.point_interval(q)):
            expected=a*r**q*(v if m else 1)
            assert lower(value.real)-law.error<=expected<=upper(value.real)+law.error


def test_unchanged_certificate_rejects_corrupt_coefficients():
    law=BarycentricLaw((-5,3),F(3,4))
    r,a,b=law.terms[0];law.terms[0]=(r,a*mp.mpf('1.01'),b)
    with pytest.raises(ArithmeticError):law.certify()
