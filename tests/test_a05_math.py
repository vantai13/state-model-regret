"""Doan Van Tai — meaningful Gaussian and paired-score tests; no held-out I/O."""
from fractions import Fraction as F

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import ndtr

from experiments.A05_freeze.ledger import gaussian, contrasts, feasible, CONTRASTS
from experiments.A05_freeze.scoring import distance, paired_difference, compare


@pytest.mark.parametrize('pars',[(.5,1.,0.,2.,0.),(-.2,.8,.4,.7,.35)])
def test_gaussian_matches_independent_quadrature(pars):
    mu,sd,b,tau,rho=pars
    s=gaussian(*pars)
    normal=lambda z: np.exp(-z*z/2)/np.sqrt(2*np.pi)
    en=quad(lambda z: -(mu+sd*z)*normal(z),-np.inf,-mu/sd,epsabs=1e-11)[0]
    # Integrate true gap times conditional probability of model selecting Switch.
    t=quad(lambda z: (mu+sd*z)*ndtr(-(mu+sd*z+b+rho*tau*z)/(tau*np.sqrt(1-rho*rho)))*normal(z),
           -np.inf,np.inf,epsabs=1e-11)[0]
    np.testing.assert_allclose(s,[mu,mu+b,en,t],atol=2e-11,rtol=2e-11)


def test_gaussian_without_queue_or_correlation_reproduces_harm_and_interaction():
    table=np.array([contrasts(gaussian(.5,1.,0.,tau,0.)) for tau in (0.,.5,1.,2.)])
    assert np.all(table[:,1]==0)
    assert np.all(np.diff(table[:,3])>0)
    assert table[-1,0]<0 and table[-1,5]>table[-1,2]
    assert abs(table[0,3])<1e-14


def test_degenerate_gaussian_strict_tie_and_feasible_projection():
    np.testing.assert_array_equal(gaussian(1,0,-1,0,0),[1,0,0,0])
    np.testing.assert_array_equal(gaussian(-1,0,1,0,0),[-1,0,1,0])
    c=contrasts(gaussian(-1,0,1,0,0))
    assert c[1]==1 and c[2]==1 and c[4]==0
    np.testing.assert_array_equal(feasible([-2,1,-1,99]),[-2,1,2,0])
    with pytest.raises(ValueError):gaussian(0,-1,0,1)


def test_paired_interval_uses_endpoints_but_individual_loss_needs_internal_kink():
    assert distance(1,(0,2))==(0,1)
    assert paired_difference(0,2,(F(1,2),F(3,2)))==(-1,1)
    assert paired_difference(0,2,(0,2))==(-2,2)


@pytest.mark.parametrize('truth,state',[(F(0),'FALSIFY'),(F(1,2),'WEAKEN'),(F(1),'SUPPORT')])
def test_decision_boundaries_are_closed_where_specified(truth,state):
    # d = |0-y|-|1-y|; y=.5 gives exact zero, so use predictions 0/2 instead.
    ys={'FALSIFY':F(1),'WEAKEN':F(9,8),'SUPPORT':F(3,2)}
    out=compare([(ys[state],ys[state])],[0],[2],margin=1)
    assert out['verdict']==state


def test_boundary_crossing_discrimination_and_missing_budget():
    assert compare([(0,2)],[0],[2],margin=1)['verdict']=='INCONCLUSIVE'
    assert compare([(0,2)],[0],[F(1,10)],margin=1)['verdict']=='DO_NOT_OPEN'
    assert compare([None],[0],[2],margin=1)['verdict']=='INCONCLUSIVE'


def test_reverse_triangle_bound_and_interval_enclosures_randomized():
    rng=np.random.default_rng(136)
    for _ in range(300):
        a,b,lo=rng.normal(size=3);hi=lo+abs(rng.normal())
        low,high=paired_difference(a,b,(lo,hi))
        for y in np.linspace(lo,hi,7):
            d=abs(a-y)-abs(b-y)
            assert float(low)-1e-14 <= d <= float(high)+1e-14
            assert abs(d)<=abs(a-b)+1e-14
