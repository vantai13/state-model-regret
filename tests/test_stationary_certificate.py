"""Doan Van Tai — infinite-law certificate checked against closed form."""
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
import numpy as np
import pytest
from smr.stationary import (StationaryBudgetError,quantile,r2_keep,
                            stationary_two_mode,tail_plan,quantile_interval,conditional_mode_interval)


@pytest.mark.parametrize('keep',[F(1,2),F(3,4),F(9,10)])
def test_infinite_law_against_high_precision_closed_form(keep):
    mass,cert=stationary_two_mode((-2,1),keep,cap_limit=3000)
    with localcontext() as c:
        c.prec=70
        s=D(keep.numerator)/D(keep.denominator)
        r=(-(1-s)+((1-s)**2+4*s*s).sqrt())/(2*s)
        b=r*(1+r); A=1/(b/(1-s)+(1+b)*r/(1-r))
        error=D(0)
        for q in range(len(mass)):
            for m in (0,1):
                exact=(A*b*(s/(1-s) if m==0 else 1) if q==0 else A*r**q*(b if m else 1))
                error+=abs(D.from_float(float(mass[q,m]))-exact)
        tail=A*(1+b)*r**len(mass)/(1-r)
        actual=(error+tail)/2
        assert actual<=D(cert['infinite_law_error_upper'])
    assert np.sum(mass)==pytest.approx(1,abs=1e-14)
    assert D(cert['tail_bound'])<=D('1e-20')
    assert quantile(mass,.5)<=quantile(mass,.9)
    err=float(cert['infinite_law_error_upper'])
    lo,hi=quantile_interval(mass,.9,err)
    assert lo==hi==quantile(mass,.9)
    posterior,bound=conditional_mode_interval(mass,lo,err)
    assert sum(posterior)==pytest.approx(1) and bound<1e-10


def test_generic_increments_stationarity_and_budget_failures():
    mass,cert=stationary_two_mode((-5,3),F(3,4),cap_limit=5000)
    incoming=np.zeros_like(mass)
    for q in range(len(mass)):
        for m,a in enumerate((-5,3)):
            j=min(len(mass)-1,max(0,q+a))
            incoming[j,m]+=mass[q,m]*.75
            incoming[j,1-m]+=mass[q,m]*.25
    assert np.max(np.abs(incoming-mass))<1e-14
    assert D(cert['infinite_law_error_upper'])<D('1e-10')
    with pytest.raises(StationaryBudgetError):
        stationary_two_mode((-2,1),F(99,100),cap_limit=10)
    with pytest.raises(ValueError): tail_plan((-2,2),F(3,4))
    with pytest.raises(ValueError): tail_plan((-6,2),F(3,4))


def test_R2_probability_interval_is_used_in_certificate():
    s,error=r2_keep(F(1,120),F(3,10))
    assert F(1,2)<s<1 and 0<error<F(1,10**50)
    mass,cert=stationary_two_mode((-2,1),s,error,cap_limit=12000)
    assert D(cert['infinite_law_error_upper'])<D('1e-10')
    assert mass.shape[1]==2
