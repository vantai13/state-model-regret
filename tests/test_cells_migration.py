"""Doan Van Tai — Part4 §11: metadata and planned D-only migration, no J."""
import json
from fractions import Fraction as F

import numpy as np
import pytest

from experiments.A00_engine.cells_adapter import GRID_PATH, load_cell, queue_law
from experiments.lessons.run_v1_1_a2 import queue_D


def test_adapter_three_schemas_metadata_only():
    g = json.loads(GRID_PATH.read_text())
    for section in ('main', 'heldout', 'controls', 'probes'):
        for row in g[section]:
            c = load_cell(row['id'])
            assert (c['yA'], c['yB'], c['h']) == tuple(F(row[k]) for k in ('yA', 'yB', 'h'))
            assert c['role'] and c['age'] == 1
            assert c['ratesA'] == (tuple(map(F, row['ratesA'])) if 'ratesA' in row else
                                    (F(row['lambdaA']) - 6, F(row['lambdaA']) + 6))
    assert load_cell('N01')['ratesA'] == (4, 4)
    assert load_cell('N01')['u'] == 1 and load_cell('S01')['u'] == 3
    with pytest.raises(KeyError):
        load_cell('no-such-cell')


@pytest.mark.parametrize('cid', ['M01', 'M09', 'M22', 'N01', 'N02', 'N03', 'N04', 'W01'])
@pytest.mark.parametrize('which', ['A', 'B'])
@pytest.mark.parametrize('ref', [1, 2])
def test_D_only_migration(cid, which, ref):
    c = load_cell(cid)
    new, old = queue_law(c, which, ref), queue_D(c, which, ref)
    assert new[0] == old[0] and new[3] == old[3]
    np.testing.assert_array_equal(new[1], old[1])
    np.testing.assert_array_equal(new[2], old[2])


def test_prior_is_recomputed_at_refinement(monkeypatch):
    import smr.cells as source
    calls = []
    law = source.law_for
    def record(*args):
        calls.append(args[-1])
        return law(*args)
    monkeypatch.setattr(source, 'law_for', record)
    c = load_cell('M01')
    y = c['yB']
    first = queue_law(c, 'B', 1)
    second = queue_law(c, 'B', 2)
    assert calls == [1, 2] and c['yB'] == y
    assert first[0] == 2 * second[0]
