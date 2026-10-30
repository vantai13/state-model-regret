from fractions import Fraction as F
from types import SimpleNamespace

import mpmath as mp
import numpy as np
import pytest

from experiments.R3R_10_interval_evaluation.evaluator import (
    NativePosteriorFastLaw, interval, point_boxes, posteriors,
)
from smr.stationary_spectral import SpectralLaw, lower, upper


def exact_complex_mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def exact_complex_power(a, q):
    out = (F(1), F(0))
    for _ in range(q):
        out = exact_complex_mul(out, a)
    return out


def assert_encloses(box, value):
    re, im, rad, exp = int(box[0]), int(box[1]), int(box[2]), int(box[3])
    scale = F(2)**exp
    assert (re-rad)*scale <= value[0] <= (re+rad)*scale
    assert (im-rad)*scale <= value[1] <= (im+rad)*scale


def test_complex_cancellation_point_sums_enclose_exact_fraction_arithmetic():
    mp.mp.dps = mp.iv.dps = 80
    roots = [(F(2,5), F(3,10)), (F(2,5), F(-3,10))]
    off = [(F(-7), F(2)), (F(-7), F(-2))]
    on = [(F(3), F(-5)), (F(3), F(5))]
    ivz = lambda z: mp.mpc(str(z[0].numerator/z[0].denominator), str(z[1].numerator/z[1].denominator))
    terms = [(ivz(r), ivz(a), ivz(b)) for r, a, b in zip(roots, off, on)]
    qs = [1, 5, 31]
    boxes = point_boxes(terms, (mp.mpc(0), mp.mpc(0)), qs)
    for q, point in zip(qs, boxes):
        for mode, coefficients in enumerate((off, on)):
            products = [exact_complex_mul(c, exact_complex_power(r, q)) for c, r in zip(coefficients, roots)]
            assert_encloses(point[mode], tuple(sum(p[j] for p in products) for j in (0, 1)))


def test_zero_atom_is_not_replaced_by_the_spectral_positive_index_formula():
    terms = [(mp.mpc('.5'), mp.mpc('.1'), mp.mpc('.2'))]
    point = point_boxes(terms, (mp.mpc('.3'), mp.mpc('.4')), [0])[0]
    assert_encloses(point[0], (F(3,10), F(0)))
    assert_encloses(point[1], (F(2,5), F(0)))


def test_native_posterior_matches_independent_original_interval_reference():
    law = SpectralLaw((-3, 2), F(3,4))
    qs = [0, 1, 7, 31, 100]
    values, errors = posteriors(law, qs)
    for q, v, e in zip(qs, values, errors):
        reference, reference_error = law.posterior(q)
        assert abs(v-np.longdouble(reference)) <= e + reference_error
        assert e <= np.longdouble('1e-8')


def test_native_conditioning_event_still_must_be_certified():
    law = SimpleNamespace(terms=[(mp.mpc('.5'), mp.mpc('.1'), mp.mpc('.2'))],
                          zero=(mp.mpc(0), mp.mpc(0)), error=mp.mpf('1e-5'))
    with pytest.raises(ArithmeticError, match='conditioning event'):
        posteriors(law, [0])


def test_positive_conditioning_mass_does_not_relax_the_posterior_threshold():
    law = SimpleNamespace(terms=[(mp.mpc('.5'), mp.mpc('.1'), mp.mpc('.2'))],
                          zero=(mp.mpc('.1'), mp.mpc('.2')), error=mp.mpf('1e-5'))
    with pytest.raises(ArithmeticError, match='posterior certificate'):
        posteriors(law, [0])


@pytest.mark.parametrize('q', [-1, 1.5, True, 2**40+1])
def test_invalid_power_cannot_be_silently_truncated_or_overflow_the_native_loop(q):
    with pytest.raises(ValueError):
        point_boxes([(mp.mpc('.5'), mp.mpc('.1'), mp.mpc('.2'))],
                    (mp.mpc('.1'), mp.mpc('.2')), [q])


def test_large_power_underflow_is_enclosed_without_dense_state_arrays():
    boxes = point_boxes([(mp.mpc('.01'), mp.mpc(1), mp.mpc(2)),
                         (mp.mpc('.9'), mp.mpc(1), mp.mpc(2))],
                        (mp.mpc(0), mp.mpc(0)), [1000])[0]
    assert_encloses(boxes[0], (F(1,100)**1000+F(9,10)**1000, F(0)))


def test_fallback_candidate_keeps_binary_checks_and_reuses_its_cache(monkeypatch):
    law = SpectralLaw((-2,1), F(3,4))
    fast = NativePosteriorFastLaw(law)
    point = fast.point
    monkeypatch.setattr(fast, 'point', lambda q: (point(q)[0], point(q)[1]+np.longdouble('1e-4')))
    a, ea = fast.posterior([0, 3, 7])
    b, eb = fast.posterior([0, 3, 7])
    assert np.array_equal(a, b) and np.array_equal(ea, eb)
    assert set(fast._posterior_fallback_cache) == {0,3,7}
    assert np.all(ea <= np.longdouble('1e-8'))


def test_certified_binary_path_does_not_call_the_expensive_fallback(monkeypatch):
    import experiments.R3R_10_interval_evaluation.evaluator as module
    law = SpectralLaw((-2,1), F(3,4))
    fast = NativePosteriorFastLaw(law)
    def forbidden(*args):
        raise AssertionError('binary-certified point must keep the fast path')
    monkeypatch.setattr(module, 'posteriors', forbidden)
    values, errors = fast.posterior([0,3,7])
    assert np.all(errors <= np.longdouble('1e-8'))
    assert fast._posterior_fallback_cache == {}
