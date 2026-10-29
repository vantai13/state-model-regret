"""High-precision reference checks, including the unbounded first moment."""
from fractions import Fraction as F
import mpmath as mp
import numpy as np
import pytest
from smr.stationary_spectral import SpectralLaw,upper,lower
from experiments.R3R_08_population_numerics.fast_law import FastLaw


def exact_float(x):
    a,b=np.longdouble(x).as_integer_ratio()
    return mp.mpf(a)/b


@pytest.mark.parametrize('inc,p',[((-2,1),F(3,4)),((-5,3),F(3,4)),((-7,4),F(9,10))])
def test_fast_cdf_point_and_posterior_enclose_interval_reference(inc,p):
    law=SpectralLaw(inc,p);fast=FastLaw(law);qs=np.array([0,1,3,7,19],dtype=np.int64)
    c,e=fast.cdf(qs);mass,em=fast.point(qs);posterior,ep=fast.posterior(qs)
    for j,q in enumerate(qs):
        exact=law.point_interval(int(q))
        totals=[sum(law.point_interval(i)[m] for i in range(int(q)+1)) for m in (0,1)]
        for m in (0,1):
            mid=(lower(exact[m].real)+upper(exact[m].real))/2
            cmid=(lower(totals[m].real)+upper(totals[m].real))/2
            assert abs(exact_float(mass[j,m])-mid)<=exact_float(em[j,m])
            assert abs(exact_float(c[j,m])-cmid)<=exact_float(e[j,m])
        reference=law.posterior(int(q))[0]
        assert abs(posterior[j]-reference)<=ep[j]+np.longdouble('4e-16')


@pytest.mark.parametrize('p',[F(1,2),F(3,4),F(9,10)])
def test_first_moment_includes_conversion_and_both_infinite_tails(p):
    law=SpectralLaw((-2,1),p);fast=FastLaw(law)
    with mp.workdps(150):
        s=mp.mpf(p.numerator)/p.denominator
        r=(-(1-s)+mp.sqrt((1-s)**2+4*s*s))/(2*s);v=r*(1+r)
        a=1/(v/(1-s)+(1+v)*r/(1-r));truth=a*(1+v)*r/(1-r)**2
        assert abs(exact_float(fast.mean)-truth)<=exact_float(fast.mean_error)


def test_quantile_edges_are_ordered_and_cdf_weights_preserve_all_mass():
    fast=FastLaw(SpectralLaw((-5,3),F(3,4)))
    edges=fast.quantiles(np.array([.1,.3,.5,.7,.9],dtype=np.longdouble),fast.law.plan['cutoff'])
    assert np.all(np.diff(edges)>=0)
    c,e=fast.cdf(np.r_[-1,edges,fast.law.plan['cutoff']])
    weights=np.diff(c,axis=0);tail=np.longdouble('.5')-c[-1]
    assert np.max(abs(weights.sum(axis=0)+tail-np.longdouble('.5')))<np.longdouble('1e-15')
