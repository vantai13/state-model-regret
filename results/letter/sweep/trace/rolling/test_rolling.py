"""Doan Van Tai — hand calculations, causal windows and output guards for S1-C rolling."""
import csv
import json
import math
from pathlib import Path

import numpy as np
import pytest

import analyze_rolling as R


def test_mm1_hand_calculation_and_relabeling():
    case = dict(mu=[10., 10.], u=1.)
    slope, flag = R.mm1_slope([2., 4.], case)
    assert slope == pytest.approx(13 / 84)
    assert flag is False
    assert R.mm1_slope([4., 2.], case)[0] == pytest.approx(-13 / 84)
    assert R.mm1_slope([2., 4.], dict(case, u=0.)) == (0., False)


def test_spawn_workers_work_without_forkserver_socket():
    with R.ProcessPoolExecutor(max_workers=2, mp_context=R.mp.get_context('spawn')) as pool:
        values = list(pool.map(R.mm1_cost, [2., 4.], [10., 10.]))
    assert values == pytest.approx([1 / 4, 2 / 3])


@pytest.mark.parametrize('rates,expected', [([8., 1.], -math.inf), ([1., 8.], math.inf)])
def test_one_unstable_action_is_flagged(rates, expected):
    assert R.mm1_slope(rates, dict(mu=[10., 10.], u=3.)) == (expected, True)


@pytest.mark.parametrize('rates,expected', [([9., 8.], -math.inf), ([8., 9.], math.inf), ([9., 9.], 0.)])
def test_two_unstable_actions_have_no_finite_slope(rates, expected):
    assert R.mm1_slope(rates, dict(mu=[10., 10.], u=4.)) == (expected, True)


@pytest.mark.parametrize('e,W,expected', [(20., 60., (0., 20.)), (100., 60., (40., 100.)),
                                        (100., 300., (0., 100.)), (100., None, (0., 100.))])
def test_windows_end_at_cutoff(e, W, expected):
    assert R.window_bounds(e, W) == expected
    assert R.window_bounds(e, W)[1] == e


def test_invalid_window_is_rejected():
    for e, W in ((0., 60.), (-1., None), (1., 0.), (math.inf, 60.)):
        with pytest.raises(ValueError):
            R.window_bounds(e, W)


def test_occupation_clips_departures_after_cutoff():
    a = np.array([0., 1., 6., 8.])
    run = (a, np.array([2., 6., 7., 9.]))
    # [1,5]: first packet contributes 1, the unfinished second contributes 4.
    assert R.S.occupation(run, 1., 5.) == 5.
    changed_future = (np.array([0., 1., 60., 80.]), np.array([2., 50., 70., 90.]))
    assert R.S.occupation(changed_future, 1., 5.) == 5.


def test_sim_and_mm1_ignore_future_tape_and_services():
    case = dict(mu=[10., 11.], u=1.)
    bg = [np.array([0., 1., 4., 6., 9.]), np.array([.5, 2., 5., 7.])]
    tape = R.S.Tape(bg, [np.full(len(a), .2) for a in bg],
                    np.array([1.2, 4.2, 8.2]), np.array([.4, .4, .4]), 10.)
    runs = [R.S.history(tape, case, a) for a in (0, 1)]
    estimate = R.estimate_window(tape, runs, case, 1., 5.)
    # Arrival at start is excluded; arrival exactly at e is included.
    assert estimate['bg0_count'] == 1 and estimate['bg1_count'] == 2
    truncated = R.S.Tape([a[a <= 5.] for a in bg],
                         [u[a <= 5.] for a, u in zip(bg, tape.bg_unit)],
                         tape.flow[tape.flow <= 5.], tape.flow_unit[tape.flow <= 5.], 5.)
    truncated_runs = [R.S.history(truncated, case, a) for a in (0, 1)]
    assert R.estimate_window(truncated, truncated_runs, case, 1., 5.) == estimate
    changed = R.S.Tape([np.r_[a[a <= 5.], 9.9] for a in bg],
                       [np.r_[u[a <= 5.], 1e6] for a, u in zip(bg, tape.bg_unit)],
                       np.r_[tape.flow[tape.flow <= 5.], 9.99], np.array([.4, .4, 1e6]), 10.)
    assert R.estimate_window(changed, [R.S.history(changed, case, a) for a in (0, 1)],
                             case, 1., 5.) == estimate
    with pytest.raises(ValueError):
        R.estimate_window(tape, runs, case, 1., 11.)


def test_group_uses_largest_available_h_uniform_tau0():
    rows = [dict(h_mult=1., h_s=2., tau_s=0., cost_stay=1., cost_switch=11.),
            dict(h_mult=2., h_s=4., tau_s=0., cost_stay=9., cost_switch=1.),
            dict(h_mult=2., h_s=4., tau_s=0., cost_stay=5., cost_switch=1.),
            dict(h_mult=2., h_s=4., tau_s=60., cost_stay=1., cost_switch=1000.)]
    result = R.case_group(rows, dict(s_hat=1.))
    assert result['group'] == 'FLIP' and result['group_n'] == 2
    assert result['s_test_case'] == -1.5 and result['group_h_mult'] == 2.


@pytest.mark.parametrize('name', ['json', 'csv'])
def test_writers_never_overwrite(tmp_path, name):
    path = tmp_path / name
    if name == 'json':
        R.write_json(path, dict(answer=42))
        write = lambda: R.write_json(path, dict(answer=0))
    else:
        R.write_csv(path, [dict(answer=42)])
        write = lambda: R.write_csv(path, [dict(answer=0)])
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        write()
    assert path.read_bytes() == before


def test_existing_output_blocks_compute(tmp_path, monkeypatch):
    (tmp_path / 'rows_rolling.csv').write_text('keep')
    monkeypatch.setattr(R, 'HERE', tmp_path)
    monkeypatch.setattr(R.S, 'verify_plan', lambda *args: pytest.fail('compute must not start'))
    with pytest.raises(FileExistsError):
        R.main()


def test_run_case_checks_every_saved_backlog_and_reuses_full_seed(tmp_path, monkeypatch):
    case = dict(id='toy', trace='ditl_20230412', lam=[2., 3.], mu=[10., 11.], u=1.)
    trace = dict(counts=[np.ones(200), np.ones(200)], dt=.1, cut=100,
                 train_means=[1., 1.], train_s=10., test_s=10., duration_s=20.)
    plan = dict(cases=[case], full_seed=311121, train_fraction=.5)
    plan_path = tmp_path / 'plan.json'
    plan_path.write_text(json.dumps(plan))
    folder = tmp_path / 'toy'
    folder.mkdir()
    (folder / 'training.json').write_text(json.dumps(dict(s_hat=1.)))
    tape = R.S.make_tape(trace, case, False, 1311121)
    runs = R.S.history(tape, case, 0)
    rows = []
    for i, t in enumerate([5., 6., 7., 8.]):
        q = [int(R.P.backlog(r, t)) for r in runs]
        rows.append(dict(point=i, t_test_s=t, tau_s=0., h_s=1., h_mult=1.,
                         fluid_gap=-.1, cost_stay=2., cost_switch=1., C_ref=1.,
                         action_M0=1, action_static=0, action_hybrid=0, disagreement=False,
                         trace=case['trace'], qA=q[0], qB=q[1], alarm=False, block=0,
                         regret_M0=0., regret_static=1., regret_hybrid=1.))
    path = folder / 'decisions.csv'
    R.write_csv(path, rows)
    monkeypatch.setattr(R, 'PLAN', plan_path)
    monkeypatch.setattr(R, 'FULL', tmp_path)
    monkeypatch.setattr(R.S, 'load_trace', lambda *args: trace)
    result = R.run_case('toy')
    assert result['audit']['checked_rows'] == 4
    assert result['audit']['test_seed'] == 1311121
    assert len(result['rows']) == 4
    for r in result['rows']:
        assert r['e_s'] == r['t_test_s'] - r['tau_s']
        for tag in R.TAGS:
            a = int(r[f'shat_{tag}'] < 0)
            assert r[f'regret_static_{tag}'] == (2., 1.)[a] - 1.
    # Tamper with a row the draft's every-37th-row sample would miss.
    path.unlink()
    rows[1]['qA'] += 1
    R.write_csv(path, rows)
    with pytest.raises(RuntimeError, match='does not match saved backlog'):
        R.run_case('toy')
