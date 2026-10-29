"""The fast arithmetic guard can escalate precision, never relax its threshold."""
from fractions import Fraction as F
import numpy as np
import pytest
from smr.stationary_spectral import SpectralLaw
from experiments.R3R_08_population_numerics.fast_law import FastLaw


def test_forward_error_uses_original_interval_reference_and_caches(monkeypatch):
    law=SpectralLaw((-2,1),F(3,4));fast=FastLaw(law)
    point=fast.point;reference=law.posterior;calls=[]
    def uncertain(q):
        p,e=point(q)
        return p,e+np.longdouble('1e-4')
    def counted(q):
        calls.append(q)
        return reference(q)
    monkeypatch.setattr(fast,'point',uncertain)
    monkeypatch.setattr(law,'posterior',counted)
    for _ in range(2):
        values,errors=fast.posterior([0,3,7])
        assert np.all(errors<=np.longdouble('1e-8'))
        for q,value,error in zip([0,3,7],values,errors):
            expected,expected_error=reference(q)
            assert abs(value-expected)<=error
            assert error>=expected_error
    assert calls==[0,3,7]


def test_uncertified_high_precision_conditioning_still_fails(monkeypatch):
    law=SpectralLaw((-2,1),F(3,4));fast=FastLaw(law);point=fast.point
    monkeypatch.setattr(fast,'point',lambda q:(point(q)[0],point(q)[1]+1))
    def refuse(q):raise ArithmeticError('conditioning event not certified')
    monkeypatch.setattr(law,'posterior',refuse)
    with pytest.raises(ArithmeticError,match='conditioning event not certified'):
        fast.posterior([7])
