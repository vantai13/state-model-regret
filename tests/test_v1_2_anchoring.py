"""Doan Van Tai — unit tests for the v1.2 anchoring rule (synthetic ladders, no plant)."""
from fractions import Fraction as F

import pytest

from smr.anchoring import anchor, in_band


def ladder(values, start=F(6), step=F(1, 4), width=0.0):
    return [{'lambdaA': str(start + i * step), 'p_low_1': p - width, 'p_high_1': p + width,
             'p_low_2': p - width, 'p_high_2': p + width} for i, p in enumerate(values)]


def test_closest_point_and_bracketing():
    a = anchor(ladder([.05, .2, .35, .6, .9]), .3)
    assert a['lambdaA'] == F(13, 2) and a['accepted'] and a['bracketing'] == 'bracketed'
    assert not a['at_ladder_floor'] and abs(a['deviation'] - .05) < 1e-12


def test_tie_goes_to_smaller_lambda():
    a = anchor(ladder([.2, .4]), .3)
    assert a['lambdaA'] == F(6)


def test_window_rejects_far_points():
    a = anchor(ladder([0., .0, .9, 1.]), .3)
    assert not a['accepted'] and a['bracketing'] == 'bracketed'


def test_floor_is_reported_but_accepted_inside_window():
    a = anchor(ladder([.33, .5, .8]), .3)
    assert a['accepted'] and a['bracketing'] == 'floor' and a['at_ladder_floor']


def test_ceiling_and_unordered_input():
    rows = ladder([.1, .2, .5])[::-1]
    a = anchor(rows, .7)
    assert a['lambdaA'] == F(13, 2) and a['bracketing'] == 'ceiling' and a['at_ladder_ceiling']
    assert not a['accepted']


def test_every_level_must_be_inside_window():
    rows = ladder([.3])
    rows[0]['p_high_2'] = .5
    assert not anchor(rows, .3)['accepted']


def test_in_band_uses_interval_ends():
    row = ladder([.5], width=.45)[0]
    assert not in_band(row)
    assert in_band(ladder([.5], width=.3)[0])


def test_empty_ladder_rejected():
    with pytest.raises(ValueError):
        anchor([], .3)
