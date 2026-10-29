"""Exact decimal inputs checked against an independent160-digit product path."""
from fractions import Fraction as F
import mpmath as mp
import pytest
from smr.stationary_spectral import SpectralLaw,lower,upper
from experiments.R3R_08_population_numerics.dyadic import products
from experiments.R3R_08_population_numerics.native_law import NativeLaw


@pytest.mark.parametrize('count',[1,3,17,65])
def test_exact_integer_enclosure_contains_independent_products(count):
    mp.mp.dps=160;mp.iv.dps=80
    roots=[mp.mpc(mp.mpf(j+1)/(count+2),mp.mpf(j%3-1)/7) for j in range(count)]
    boxes=products(roots)
    declared=[mp.mpc(mp.nstr(r.real,80),mp.nstr(r.imag,80)) for r in roots]
    for j,box in enumerate(boxes):
        truth=mp.fprod(declared[j]-r for k,r in enumerate(declared) if k!=j)
        assert lower(box.real)<=truth.real<=upper(box.real)
        assert lower(box.imag)<=truth.imag<=upper(box.imag)


def test_native_products_reject_duplicate_roots():
    with pytest.raises(ArithmeticError,match='distinct roots'):products([mp.mpc('.5'),mp.mpc('.5')])


@pytest.mark.parametrize('inc,p',[((-2,1),F(3,4)),((-5,3),F(3,4)),((-7,4),F(9,10))])
def test_native_law_accepted_by_original_certificate_and_quantiles(inc,p):
    law=NativeLaw(inc,p);reference=SpectralLaw(inc,p)
    old=SpectralLaw.certify(law)
    assert mp.mpf(old['infinite_law_error_upper'])<mp.mpf('1e-10')
    for a in (F(1,2),F(9,10)):assert law.quantile(a)==reference.quantile(a)
    r,a,b=law.terms[0];law.terms[0]=(r*mp.mpf('.99'),a,b)
    with pytest.raises(ArithmeticError,match='root proposals changed'):law.certify()
