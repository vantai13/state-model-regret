"""Independent regression for interval wrapping and unchanged queue bounds."""
from fractions import Fraction as F
import mpmath as mp
import pytest

from smr.stationary_spectral import SpectralLaw,lower,upper
from experiments.R3R_07_fast_stationary.balanced_certificate import BalancedProduct,BalancedCertificateLaw


def test_balanced_product_preserves_factors_and_avoids_wrapping():
    old=mp.iv.dps;mp.iv.dps=80
    try:
        one=mp.iv.mpf(1);e=mp.iv.mpf('1e-70')
        factor=mp.iv.mpc(one+mp.iv.mpf([-upper(e),upper(e)]),one+mp.iv.mpf([-upper(e),upper(e)]))
        product=BalancedProduct();left=mp.iv.mpc(1)
        for _ in range(1024):product.add(factor);left*=factor
        # Exact center (1+i)^1024 = 2^512; no queue implementation is used.
        exact=mp.mpf(2)**512;balanced=product.value()
        assert lower(balanced.real)<=exact<=upper(balanced.real)
        assert lower(balanced.imag)<=0<=upper(balanced.imag)
        assert upper(abs(balanced-mp.iv.mpc(mp.iv.mpf(2)**512)))<exact*mp.mpf('1e-60')
        assert lower(abs(left))==0
    finally:mp.iv.dps=old


@pytest.mark.parametrize('count',[0,1,2,3,7,16,31])
def test_all_factors_including_unbalanced_final_levels(count):
    product=BalancedProduct();expected=1
    for i in range(count):product.add(mp.iv.mpc(i+1));expected*=i+1
    result=product.value()
    with mp.workdps(150):
        assert lower(result.real)<=expected<=upper(result.real)
    assert lower(result.imag)==upper(result.imag)==0


@pytest.mark.parametrize('s',[F(1,2),F(3,4),F(9,10)])
def test_balanced_certificate_matches_reference_and_rejects_corruption(s):
    law=BalancedCertificateLaw((-5,3),s)
    old=SpectralLaw.certify(law)
    assert mp.mpf(old['infinite_law_error_upper'])<mp.mpf('1e-10')
    reference=SpectralLaw((-5,3),s)
    for a in (F(1,2),F(9,10)):assert law.quantile(a)==reference.quantile(a)
    r,a,b=law.terms[0];law.terms[0]=(r,a*mp.mpf('1.01'),b)
    with pytest.raises(ArithmeticError):law.certify()


def test_balanced_certificate_actual_closed_form_error(monkeypatch):
    # Reuse the independent 150-digit true-law/complete-tail calculation.
    import tests.test_algebraic_stationary_certificate as reference
    monkeypatch.setattr(reference,'AlgebraicCertificateLaw',BalancedCertificateLaw)
    reference.test_certificate_covers_actual_closed_form_error(F(3,4))
