"""Doan Van Tai — check the v1.2 D rebuild against preserved design code.

Only main-cell construction and calibration/control D are evaluated here.
No costs, predictions or held-out D are computed.
"""
import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import pytest

from smr.cells import make_cell, queue_D
from experiments.explore.reformulate_grid import make_cell as original_make_cell
from experiments.lessons.run_v1_1_a2 import queue_D as original_queue_D

ROOT = Path(__file__).resolve().parents[1]
GRID = json.loads((ROOT / 'notes/design/grid_v1_2.json').read_text())


def main_cell(record, constructor=make_cell):
    s = {k: F(record[k]) for k in ('kappa', 'eta', 'alphaA', 'alphaB')}
    s.update(slice=record['slice'], horizon=record['horizon'])
    return constructor(s, F(record['lambdaA']))


def calibration_or_control(cid):
    if cid.startswith('M'):
        return main_cell(next(c for c in GRID['main'] if c['id'] == cid))
    old = json.loads((ROOT / 'notes/design/grid_v1_1_redesign_candidate.json').read_text())
    c = dict(next(c for c in old['cells'] if c['id'] == cid))
    for k in ('lambdaA', 'kappa', 'eta', 'u', 'yA', 'yB', 'h', 'age'):
        c[k] = F(c[k])
    for k in ('ratesA', 'ratesB'):
        c[k] = tuple(map(F, c[k]))
    return c


def test_all_main_cells_preserve_original_constructor_and_frozen_observations():
    for record in GRID['main']:
        c = main_cell(record)
        assert c == main_cell(record, original_make_cell), record['id']
        assert all(c[k] == F(record[k]) for k in ('yA', 'yB', 'h'))
        assert c['H_coarse'] == record['H_coarse']
        assert c['ratesA'] == (F(record['lambdaA']) - 6, F(record['lambdaA']) + 6)


@pytest.mark.parametrize('cid', ['M01', 'M09', 'M22', 'N01'])
@pytest.mark.parametrize('which', ['A', 'B'])
@pytest.mark.parametrize('ref', [1, 2, 4])
def test_factorized_D_matches_original(cid, which, ref):
    c = calibration_or_control(cid)
    unit, mass, support, error = queue_D(c, which, ref)
    old_unit, old_mass, old_support, old_error = original_queue_D(c, which, ref)
    assert unit == old_unit and error == old_error
    np.testing.assert_array_equal(mass, old_mass)
    np.testing.assert_array_equal(support, old_support)
    assert abs(mass.sum(dtype=np.longdouble) - 1) < 1e-12
    assert error <= 1e-8


def test_draining_control_keeps_zero_backlog_and_both_modes():
    # Independent analytic invariant: arrivals 4 + managed 1 < capacity 10.
    unit, mass, support, _ = queue_D(calibration_or_control('N01'), 'A', 1)
    assert unit > 0 and mass.shape == (1, 2)
    np.testing.assert_array_equal(mass, np.array([[.5, .5]], dtype=np.longdouble))
    assert support.all()
