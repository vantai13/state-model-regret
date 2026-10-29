"""Independent dense companion roots on small sparse polynomials; no queue outcomes."""
import numpy as np
import pytest

from experiments.R3R_07_fast_stationary.root_proposal import stable_root_proposals


@pytest.mark.parametrize('d,b,s',[(2,1,.75),(5,3,.92),(7,5,.9),(17,11,.5),(17,11,.99),
                                (67,53,.995),(77,43,.923240862),(100,1,.75)])
def test_proposals_match_independent_dense_roots(d,b,s):
    coefficients=np.zeros(d+b+1)
    coefficients[0]=coefficients[-1]=s;coefficients[b]=-(2*s-1);coefficients[d]=-1
    expected=np.roots(coefficients);expected=expected[np.abs(expected)<1-1e-9]
    actual=stable_root_proposals(d,b,s)
    assert len(expected)==len(actual)==b
    for r in actual:assert np.min(np.abs(expected-r))<1e-8


def test_bad_parameters_rejected():
    with pytest.raises(ValueError):stable_root_proposals(2,2,.9)
