"""Doan Van Tai — independent balance/closed form and roundoff counterexamples."""
from fractions import Fraction as F
import numpy as np
import mpmath as mp
import pytest
from smr.stationary_spectral import SpectralLaw,lower,upper
from smr.stationary_v2 import positive_sum
from smr.stationary import r2_keep

@pytest.mark.parametrize('s',[F(1,2),F(3,4),F(9,10)])
def test_spectral_against_closed_form(s):
    law=SpectralLaw((-2,1),s);s=mp.mpf(s.numerator)/s.denominator
    r=(-(1-s)+mp.sqrt((1-s)**2+4*s*s))/(2*s);b=r*(1+r)
    a=1/(b/(1-s)+(1+b)*r/(1-r))
    for q in (0,1,2,7,90):
        points=law.point_interval(q)
        for mode in (0,1):
            expected=a*b*(s/(1-s) if mode==0 else 1) if q==0 else a*r**q*(b if mode else 1)
            assert lower(points[mode].real)-law.error<=expected<=upper(points[mode].real)+law.error
    assert law.quantile(F(1,2))<=law.quantile(F(9,10))


def test_boundary_residual_certificate_rejects_bad_coefficients():
    law=SpectralLaw((-5,3),F(3,4));r,a,b=law.terms[0];law.terms[0]=(r,a*mp.mpf('1.01'),b)
    with pytest.raises(ArithmeticError):law.certify()


def test_rounding_guard_covers_actual_lost_positive_summand():
    eps=np.finfo(np.longdouble).eps
    total,bound=positive_sum([np.longdouble(1),eps/4])
    actual=F(1)+F(str(eps/4))-F(str(total))
    assert actual>0
    assert F(str(bound))>=actual


def test_large_spectral_law_does_not_allocate_tail_domain():
    law=SpectralLaw((-67,53),*r2_keep(F(1,240),F(1)))
    assert law.plan['cutoff']>1_000_000 and len(law.terms)==53
    q=law.quantile(F(9,10));p,error=law.posterior(q)
    assert 0<p<1 and error<1e-8 and law.error<mp.mpf('1e-10')
