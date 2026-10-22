"""Doan Van Tai — four core tests supplied in L1.8 Part A."""
import math
import pytest
from experiments.lessons.l1_8_slots import T_mode_from_lambda, p_stay, persistence_R2, to_slots


def test_semigroup():
    lam,lam_half = persistence_R2(.012,.1),persistence_R2(.006,.1)
    p = p_stay(lam_half)
    assert math.isclose(p*p+(1-p)**2,p_stay(lam))


def test_correlation_invariant():
    for dt in (.012,.006,.003):
        n,_ = to_slots(.204,dt)
        assert math.isclose(persistence_R2(dt,.1)**n,math.exp(-4.08))


def test_anchor_b():
    assert to_slots(.2,.012)[0]==17 and to_slots(.6,.012)[0]==50
    assert math.isclose(1-p_stay(persistence_R2(.012,.1)),.1067,abs_tol=1e-4)


def test_canonical_not_physical():
    with pytest.raises(ValueError):
        T_mode_from_lambda(0.,1.)
