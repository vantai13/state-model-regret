"""Doan Van Tai — T1/T4/T5/T7 and focused structural/conditional regression checks."""
from fractions import Fraction as F
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from experiments.R3R_02_audit import bridge as B
from experiments.R3R_02_audit import pilot_population as P
from experiments.A00_engine import physical


def golden():
    path = Path(__file__).with_name('test_population_toys.py')
    s = importlib.util.spec_from_file_location('population_golden_reference', path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def test_T1_actual_pilot_on_exact_toys_and_random_joint_laws():
    G = golden()
    plants = [G.two_state_part1(F(4, 5)), G.two_state_part1(F(3, 5)), G.harm_toy(-2),
              G.harm_toy(-4), G.harm_toy(F(1, 2))]
    rng = G.random.Random(20261028)
    plants.extend(G.random_plant(rng) for _ in range(500))
    for plant in plants:
        observed = B.golden_population(plant)
        expected = G.cells(plant)
        for key in ('00', '01', '10', '11'):
            assert abs(float(observed[key]) - float(expected[key])) <= 1e-12


def test_D22_exact_fresh_and_mode_paths():
    G = golden()
    for q, f, v in [({'x1': 5, 'x2': 5}, 0, -.5), ({'x1': 8, 'x2': 2}, -.5, 0)]:
        L = B.golden_population(G.harm_toy(-2) | {'q': q})
        assert float(L['00'] - L['cb0']) == f
        assert float(L['cb0'] - L['10']) == v


def test_rational_tie_adapter_regression_preserves_original_problem():
    # The original naive adapter rounded 2/7,3/7,2/7 before taking a sign.
    # Integer-count homogeneity preserves exact mean-hat=0 and hence Stay.
    plant = dict(p={'y': F(1)}, D={'y': {1: F(2, 7), 2: F(3, 7), 3: F(2, 7)}},
                 J={1: F(10), 2: F(10), 3: F(6)},
                 Delta={1: F(3), 2: F(-1), 3: F(0)},
                 Dhat={1: F(2), 2: F(-4), 3: F(4)})
    assert B.golden_population(plant)['00'] == F(62, 7)


def test_T7_engine_ties_stay_in_both_rows():
    A = dict(d=np.array([1.], dtype=P.LD), dh=np.array([0.], dtype=P.LD),
             j=np.array([5.], dtype=P.LD), w=[np.array([1.], dtype=P.LD)])
    Z = dict(d=np.array([0.], dtype=P.LD), dh=np.array([0.], dtype=P.LD),
             j=np.array([0.], dtype=P.LD), w=[np.array([1.], dtype=P.LD)])
    result = P.pair_values(A, Z, 0, 0)
    assert not result['a00'] and not result['a01']
    assert result['L']['10'] == result['L']['00'] == 5


def test_observation_atom_and_normalization(monkeypatch):
    class Law:
        plan = {'cutoff': 3}
        def mass(self, n):
            return np.array([[.25, 0], [.5, 0], [.24995, 0], [.00005, 0]], dtype=P.LD)
    monkeypatch.setattr(P, 'law_for', lambda *a: (F(1), Law()))
    cell = dict(ratesA=(F(2), F(14)), u=F(1), kappa=F(1))
    _, reps, weights, tail = P.observation_bins(cell, 'A', 1, 4)
    assert reps[0] == 0
    assert abs(weights[0] - .25 / .99995) < 1e-12
    assert abs(sum(weights) - 1) < 1e-12 and tail > 0


def test_union_weight_rows_match_nonzero_order(monkeypatch):
    mass = [np.array([[.75, 0], [0, .25]], dtype=P.LD),
            np.array([[.2, 0], [0, .8]], dtype=P.LD)]
    monkeypatch.setattr(P, 'queue_D', lambda cell, *args: (F(1), mass[int(cell['yA'])], None, 0.))
    def fake_table(unit, law, **kwargs):
        q, m = np.nonzero(law)
        return SimpleNamespace(d=q + 1, dh=q * 2 + 1, jst=q * 5 + 10), {}
    monkeypatch.setattr(P, 'side_from_law', fake_table)
    cell = dict(ratesA=(F(2), F(14)), u=F(1), kappa=F(1), H_coarse=1)
    result = P.side_rows(cell, 'A', 1, [0, 1], F(1))
    assert np.array_equal(result['w'][0], mass[0][np.nonzero(sum(mass))])
    assert np.array_equal(result['w'][1], mass[1][np.nonzero(sum(mass))])


def test_conditional_mode_age_matches_closed_R2_formula():
    # Additional C2 analytic diagnostic: this sees no-age even without MC.
    cell = B.cell_for(B.spec('X1001'))
    _, post, _, _ = P.queue_D(dict(cell, yB=F(0)), 'B', 1)
    keep, _ = P.r2_keep(F(1, 120), cell['kappa'])
    p = float(keep)
    initial_on_at_empty = 1 - p
    expected = .5 + (initial_on_at_empty - .5) * (2 * p - 1) ** 120
    assert abs(float(post[:, 1].sum()) - expected) <= 1e-12


def example_physical():
    mass = np.zeros((9, 2), dtype=P.LD)
    mass[0, 0] = mass[8, 0] = .5
    return physical.side_from_law(F(1), mass, rates=(F(2), F(14)), u_stay=F(1),
                                  u_switch=F(0), capacity=F(10), H=1, dt=F(1), keep=F(3, 4))[0]


def test_D10_average_cost_is_not_cost_at_mean_backlog():
    t = example_physical()
    # Endpoints: q0 ->0, q8->1 under Stay; expected cost .5, idle-gap mean .5.
    assert float(sum(p * h for p, h in zip(t.p, t.dh))) == .5
    assert float(sum(p * j for p, j in zip(t.p, t.jst))) == .5


def test_T5_far_states_have_exact_zero_idle_gaps():
    mass = np.zeros((201, 2), dtype=P.LD); mass[200] = (.5, .5)
    t, _ = physical.side_from_law(F(1), mass, rates=(F(2), F(14)), u_stay=F(1),
                                 u_switch=F(0), capacity=F(10), H=2, dt=F(1), keep=F(3, 4))
    assert all(d == 0 for d in t.d) and all(h == 0 for h in t.dh)


def test_T4_zero_action_is_exactly_zero():
    out, _ = P.evaluate(['TOY-u0', '6', '8', '3/10', '0', '2', 1, 4, '0'])
    assert all(out[k] == 0 for k in B.GKEYS)
    assert out['P_flip'] == 0


def test_Cbar_comes_from_same_population_loss_call(monkeypatch):
    z = np.array([P.LD(0)]); one = np.array([P.LD(1)])
    table = dict(d=z, dh=z, j=np.array([P.LD(3)]), w=[one])
    monkeypatch.setattr(P, 'observation_bins', lambda *args: (F(1), [0], one, 0.))
    monkeypatch.setattr(P, 'side_rows', lambda *args: table)
    out, _ = P.evaluate(['TOY-Cbar', '6', '8', '3/10', '0', '2', 1, 4, '0'])
    assert out['Cbar'] == 6 and out['G_SM'] == 0


def test_new_integration_rejects_nonprobability_weights():
    z = np.array([P.LD(0)]); one = np.array([P.LD(1)])
    T = dict(d=z, dh=z, j=one, w=[one])
    with pytest.raises(ValueError, match='normalized'):
        B.population_from_tables(T, T, [.99], [1.])
