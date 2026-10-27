"""Doan Van Tai — L1.8B golden chain, through the shared new aggregation path."""
import numpy as np
import pytest

from experiments.A00_engine.toy_refinement import solve_toy_level
from experiments.lessons.l1_8_refinement import solve_level


@pytest.mark.parametrize('ref', [1, 2, 4, 8, 16, 32, 64, 128])
def test_L18B_golden_chain(ref):
    new = solve_toy_level(ref)
    old = solve_level(ref, dtype=np.longdouble)['summary']
    for c in ('00', '01', '10', '11'):
        assert new['L'][c] == pytest.approx(old['L' + c], abs=1e-11)
        lo, hi = new['intervals']['L' + c]
        assert lo <= old['L' + c] <= hi
    assert new['G']['G_S'] == pytest.approx(old['G_S'], abs=1e-11)
    assert new['G']['Gamma'] == pytest.approx(old['Gamma'], abs=1e-11)
    assert new['G']['F'] == pytest.approx(old['freshness'], abs=1e-11)
    assert new['G']['V'] == pytest.approx(old['mode_visibility'], abs=1e-11)
