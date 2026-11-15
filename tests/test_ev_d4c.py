"""Doan Van Tai — fast, synthetic EV-D4c checks; no panel or VM execution."""
import builtins
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np
import pytest

from experiments.ext_validity import ev_d4c_panel as D
from experiments.ext_validity import packet as P


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, allow_nan=False))


@pytest.fixture
def out(tmp_path, monkeypatch):
    monkeypatch.setattr(D, 'OUT', tmp_path)
    return tmp_path


def case(arm='C', regime=0, r=.8):
    name = f'{arm}N{regime:02d}'
    return dict(arm=arm, regime=name, r=r, tau=123.45, id=f'{name}_r{round(r * 10):02d}', seed=15000 + regime,
                h_mult=[10, 30], cls='trace_cox', stratum='neg')


def prediction_file(out, rows):
    with (out / 'predictions.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'h_mult', 'twin', 'pred_abs'])
        writer.writeheader()
        writer.writerows(rows)


def test_design_probe_amended_ids_and_determinism(out, monkeypatch):
    D.main(['design-probe'])
    data = (out / 'probe_cases.json').read_bytes()
    probes = json.loads(data)
    assert len(probes) == 60
    for arm in D.ARMS:
        group = [c for c in probes if c['arm'] == arm]
        assert [sum(c['stratum'] == s for c in group) for s in D.D4.STRATA] == [8, 4, 8]
        assert [c['seed'] for c in group] == list(range(17000 if arm == 'H' else 15000, 17020 if arm == 'H' else 15020))
        for c in group:
            load = max(c['lamA'], c['lamB']) + c['u']
            assert (7.75 < load <= 9.75) if arm == 'H' else (load <= 7.75)
            assert min(c['lamA'], c['lamB']) >= 6
            lo, hi, _ = D.D4.STRATA[c['stratum']]
            assert lo - .005 <= (c['lamB'] - c['lamA']) / c['u'] <= hi + .005
            assert c['tau'] == 1. and c['n_inst'] == 10000 and c['train_T'] == 100000.
            assert c['h_mult'] == [10, 30] and c['spacing_mult'] == 3 and c['batches'] == 40
    for c, l in zip(probes[:20], probes[20:40]):
        assert c['regime'][1:] == l['regime'][1:]
        cc, ll = copy.deepcopy(c), copy.deepcopy(l)
        for row in (cc, ll):
            for key in ('arm', 'regime', 'id'):
                row.pop(key)
            row['params'].pop('series')
        assert cc == ll
        assert c['params']['series'] == D.SER_C and l['params']['series'] == D.SER_L
    with pytest.raises(FileExistsError):
        D.design_probe()
    other = out / 'second'
    monkeypatch.setattr(D, 'OUT', other)
    D.design_probe()
    assert (other / 'probe_cases.json').read_bytes() == data


def test_unfillable_stratum_raises(monkeypatch):
    monkeypatch.setattr(D.D4, 'STRATA', dict(neg=(-1.5, -.1, 5000)))
    with pytest.raises(RuntimeError, match='only'):
        list(D._regimes(20270115, 7.75))


def fake_probes(out, bad=None, ti=8.04):
    D.design_probe()
    probes = json.loads((out / 'probe_cases.json').read_text())
    for i, c in enumerate(probes):
        put(D._train_path(c, probe=True), dict(T_int=ti if bad != 'zero' or i else 0.,
                                              T_int_censored=bad == 'censored' and i == 0))
    return probes


@pytest.mark.parametrize('bad', [None, 'censored', 'zero'])
def test_design_rounding_exclusions_and_packet_ids(out, bad):
    probes = fake_probes(out, bad)
    D.main(['design'])
    cases = json.loads((out / 'cases_all.json').read_text())
    excluded = json.loads((out / 'design_excluded.json').read_text())['excluded']
    assert len(cases) == (480 if bad is None else 472)
    assert len(excluded) == int(bad is not None)
    for c in cases:
        assert c['tau'] == round(c['r'] * 8.04, 2)
        assert c['id'] == f"{c['regime']}_r{round(c['r'] * 10):02d}"
        assert '.' not in c['id']
    assert {c['id'].split('_r')[1] for c in cases} == {'01', '03', '05', '08', '10', '12', '25', '50'}
    if bad:
        assert excluded[0]['regime'] == probes[0]['regime']
        assert all(c['regime'] != probes[0]['regime'] for c in cases)
    # Exercise the real packet validator on all r ids, including tau < 1 s.
    for c in cases[:8]:
        P.validate(c)
    with pytest.raises(FileExistsError):
        D.design()


def test_design_rejects_sub_bin_tau_without_outputs(out):
    fake_probes(out, ti=.01)
    with pytest.raises(ValueError, match='tau .* < 0.01'):
        D.design()
    assert not (out / 'cases_all.json').exists()
    assert not (out / 'design_excluded.json').exists()


def selection_inputs(out, counts):
    cases = [case(arm, i, r) for arm, n in zip(D.ARMS, counts) for i in range(n) for r in D.R]
    put(out / 'cases_all.json', cases)
    put(out / 'design_excluded.json', dict(excluded=[]))
    for c in cases:
        put(D._train_path(c), dict(T_int=10., T_int_censored=False))
    return cases


def test_selection_pairing_and_h_independence(out):
    cases = selection_inputs(out, (11, 11, 10))
    put(D._train_path(cases[0]), dict(T_int=240.01, T_int_censored=False))
    D.select()
    kept = json.loads((out / 'cases.json').read_text())
    arms = json.loads((out / 'selection.json').read_text())['arms']
    assert {arm: a['kept_regimes'] for arm, a in arms.items()} == dict(C=10, L=10, H=10)
    assert all(a['arm_status'] == 'OK' for a in arms.values())
    assert not any(c['regime'] in ('CN00', 'LN00') for c in kept)
    assert any(c['regime'] == 'HN00' for c in kept)
    assert 'paired CN00' in arms['L']['excluded'][0]['reasons'][0]
    assert len(kept) == 240
    with pytest.raises(FileExistsError):
        D.select()


def test_selection_design_exclusion_propagates_and_stop(out):
    cases = selection_inputs(out, (10, 10, 10))
    put(out / 'cases_all.json', [c for c in cases if c['regime'] != 'CN00'])
    put(out / 'design_excluded.json', dict(excluded=[dict(arm='C', regime='CN00', reason='probe T_int censored')]))
    D.select()
    arms = json.loads((out / 'selection.json').read_text())['arms']
    assert arms['C']['kept_regimes'] == arms['L']['kept_regimes'] == 9
    assert arms['C']['arm_status'] == arms['L']['arm_status'] == 'STOP'
    assert {c['arm'] for c in json.loads((out / 'cases.json').read_text())} == {'H'}
    assert arms['H']['arm_status'] == 'OK'


def test_selection_all_stop_exits_nonzero(out):
    selection_inputs(out, (9, 9, 9))
    with pytest.raises(SystemExit, match='all three arms'):
        D.select()
    assert json.loads((out / 'cases.json').read_text()) == []
    assert all(a['arm_status'] == 'STOP' for a in json.loads((out / 'selection.json').read_text())['arms'].values())


def training(c, ti=10.):
    return dict(case_sha256=P.signature(c), T_int=ti, T_int_censored=False, s_train=.01, mean_stay=2.,
                nowcast={'A': dict(beta=[1., c['r'], 0.])},
                shares={str(m): dict(F_old_fluid_nowcast=.3, F_new=.1, F_old_ratefluid_nowcast=.4, F_new_rate=.1)
                        for m in (10, 30)})


def test_predict_reuses_d4_and_describe_cannot_read_test(out, monkeypatch):
    cases = [case(arm, i, r) for arm in D.ARMS for i in range(2) for r in D.R]
    put(out / 'cases.json', cases)
    for c in cases:
        put(D._train_path(c), training(c, ti=10. + int(c['regime'][-2:])))
    old = D.D4.OUT, D.D4.CASES, D.D4.PRED
    D.predict()
    assert (D.D4.OUT, D.D4.CASES, D.D4.PRED) == old
    with (out / 'predictions.csv').open() as f:
        preds = list(csv.DictReader(f))
    assert len(preds) == len(cases) * 4
    assert float(preds[0]['pred_abs']) == pytest.approx(10 * 10 * .01 * .2)
    (out / 'test').mkdir()
    (out / 'test' / 'forbidden.json').write_text('NEVER READ')
    originals = builtins.open, Path.open, Path.read_text

    def guard(path):
        assert 'test' not in Path(path).relative_to(out).parts, 'describe read test data'

    def safe_open(path, *args, **kwargs):
        guard(path)
        return originals[0](path, *args, **kwargs)

    def safe_path_open(path, *args, **kwargs):
        guard(path)
        return originals[1](path, *args, **kwargs)

    def safe_read(path, *args, **kwargs):
        guard(path)
        return originals[2](path, *args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(builtins, 'open', safe_open)
        m.setattr(Path, 'open', safe_path_open)
        m.setattr(Path, 'read_text', safe_read)
        D.describe()
    seen = json.loads((out / 'seen_before_lock.json').read_text())['arms']
    for arm in D.ARMS:
        assert seen[arm]['kept_regimes'] == 2
        assert seen[arm]['T_int'] == dict(min=10., median=10.5, max=11., over='main_train_cases')
        assert seen[arm]['by_r']['0.8']['median_beta1_A'] == .8
        assert seen[arm]['by_r']['0.8']['median_F_old_minus_F_new_h30'] == pytest.approx(.2)
        assert [seen[arm]['by_group'][g]['n_filter_rows_h30'] for g in D.GROUPS] == [12, 12, 8]
    for writer in (D.predict, D.describe):
        with pytest.raises(FileExistsError):
            writer()


def scoring_inputs(out, l_share=.6, h_share=.6, c_band=.65, c_ratio=.4, n=10):
    """20 rows/group: C low 16/20; C band 13/20, median ratio .4.

    E10/E30=.4. Plug-in equal absolute effects have growth zero although their
    percentage effects differ. C D6 passes exactly .9, H falls below .9.
    Nowcast level signs all fail independently of the increment signs.
    """
    cases, predictions = [], []
    for arm in D.ARMS:
        for group_index, r in enumerate((.1, .8, 2.5)):
            share = .8 if group_index == 0 else (c_band if arm == 'C' else (l_share if arm == 'L' else h_share))
            good = round(share * 2 * n)
            for i in range(n):
                c = case(arm, group_index * n + i, r)
                cases.append(c)
                raw = {m: dict(E_stay=dict(mean=4. if m == 10 else 10.), twins={}) for m in (10, 30)}
                for j, (twin, _, _) in enumerate(D.D4.NOWCAST):
                    ok = 2 * i + j < good
                    ratio = c_ratio if arm == 'C' and group_index == 1 else 1.
                    delta = .03125 * (ratio if ok else -1.)
                    noisy = arm == 'C' and group_index == 1 and ok
                    for m in (10, 30):
                        # Dyadic baseline/increment make the ratio=.5 boundary exact.
                        g = -.125 if m == 10 else -.125 + delta
                        raw[m]['twins'][twin] = dict(G_S=g, se=.01 if noisy else .001,
                                                     pct_E_stay=100 * g / raw[m]['E_stay']['mean'], se_pct=.01)
                        predictions.append(dict(id=c['id'], h_mult=m, twin=twin, pred_abs=.015625 if m == 10 else .046875))
                for j, twin in enumerate(D.D4.PLUGIN):
                    index = 2 * (group_index * n + i) + j
                    fail = index < (6 if arm == 'C' else (7 if arm == 'H' else 0))
                    for m in (10, 30):
                        g = .1 if m == 30 and fail else .02
                        raw[m]['twins'][twin] = dict(G_S=g, se=.0004,
                                                     pct_E_stay=100 * g / raw[m]['E_stay']['mean'], se_pct=.01)
                for m in (10, 30):
                    put(out / 'test' / f"{c['id']}_s{c['seed']}_h{m}.json", raw[m])
    put(out / 'cases.json', cases)
    prediction_file(out, predictions)
    return cases


@pytest.mark.parametrize('l,h,expected', [(.8, .6, 'LOOPING'), (.6, .8, 'LOAD'),
                                          (.6, .6, 'TRACE_OR_OTHER'), (.7, .8, 'UNRESOLVED')])
def test_score_h3_branches_and_hand_computed_statistics(out, l, h, expected):
    scoring_inputs(out, l, h)
    D.main(['score'])
    score = json.loads((out / 'score.json').read_text())
    assert score['H1']['verdict'] == score['H2']['verdict'] == 'PASS'
    assert score['H3']['verdict'] == expected
    c = score['arms']['C']
    assert (c['completed'], c['of'], c['inconclusive']) == (60, 60, False)
    assert c['groups']['low']['inc_share'] == .8
    band = c['groups']['band']
    assert band['n'] == 20 and band['n_regimes'] == 10
    assert band['inc_share'] == .65 and band['level_share'] == 0.
    assert band['median_inc_ratio'] == pytest.approx(.4)
    assert band['n_noise'] == 7 and band['inc_share_noise'] == 0.
    assert c['by_r']['0.8'] == band
    assert c['by_r']['1.0']['status'] == 'NOT_EVALUABLE'
    assert score['D6-C']['share'] == .9 and score['D6-C']['verdict'] == 'PASS'
    assert score['D6-L']['share'] == 1. and score['D6-L']['exploratory']
    assert score['D6-H']['share'] == pytest.approx(53 / 60) and score['D6-H']['verdict'] == 'FAIL'
    assert not score['D6-C']['exploratory']
    with (out / 'score_rows.csv').open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 180 and tuple(rows[0]) == D.ROW_FIELDS
    assert float(rows[0]['pred30']) == .46875 and float(rows[0]['tau']) == 123.45
    assert float(rows[0]['G30_abs']) - float(rows[0]['G10_abs']) == pytest.approx(.03125)
    with pytest.raises(FileExistsError):
        D.score()


@pytest.mark.parametrize('share,ratio', [(.7, .4), (.65, .5)])
def test_h2_requires_both_conditions(out, share, ratio):
    scoring_inputs(out, l_share=.8, c_band=share, c_ratio=ratio)
    D.score()
    result = json.loads((out / 'score.json').read_text())
    assert result['H2']['verdict'] == 'FAIL'
    assert result['H3']['verdict'] == 'UNRESOLVED'


def test_score_not_evaluable(out):
    scoring_inputs(out, n=4)
    D.score()
    result = json.loads((out / 'score.json').read_text())
    assert result['arms']['C']['groups']['low']['n'] == 8
    assert result['H1']['verdict'] == result['H2']['verdict'] == 'NOT_EVALUABLE'
    assert result['H3']['verdict'] == 'UNRESOLVED'


@pytest.mark.parametrize('missing,inconclusive', [(6, False), (7, True)])
def test_score_completion_threshold(out, missing, inconclusive):
    scoring_inputs(out)
    for path in sorted((out / 'test').glob('C*.json'))[:missing]:
        path.unlink()
    D.score()
    result = json.loads((out / 'score.json').read_text())
    assert result['arms']['C']['inconclusive'] is inconclusive
    assert result['arms']['C']['completed'] == 60 - missing
    if inconclusive:
        assert result['H1']['verdict'] == result['H2']['verdict'] == result['D6-C']['verdict'] == 'INCONCLUSIVE'
        assert result['H3']['verdict'] == 'UNRESOLVED'


def test_score_stopped_arm_and_missing_needed_h_group(out):
    cases = scoring_inputs(out)
    put(out / 'cases.json', [c for c in cases if c['arm'] != 'H'])
    put(out / 'selection.json', dict(arms=dict(H=dict(arm_status='STOP'))))
    D.score()
    result = json.loads((out / 'score.json').read_text())
    assert result['arms']['H']['arm_status'] == result['D6-H']['verdict'] == 'STOP'
    assert result['H3']['verdict'] == 'UNRESOLVED'
    assert D._h3('PASS', 'WORKS', 'STOP') == 'LOOPING'  # H = any in the card.
    assert D._h3('PASS', 'FAILS', 'NOT_EVALUABLE') == 'UNRESOLVED'
    assert D._h3('PASS', 'FAILS', 'INCONCLUSIVE') == 'UNRESOLVED'


def test_score_filter_ties_noise_and_zero_increment(out):
    cases = scoring_inputs(out)
    c = cases[0]
    predictions = D._predictions()
    # Exact binary numbers: .25 pp is retained, a zero sign stays a zero,
    # equality at the secondary noise threshold is excluded.
    for twin, _, _ in D.D4.NOWCAST:
        predictions[c['id'], 10, twin] = .125
        predictions[c['id'], 30, twin] = .25
        predictions[cases[1]['id'], 30, twin] = .0249  # Below .25 pp: excluded.
    prediction_file(out, [dict(id=i, h_mult=m, twin=t, pred_abs=p) for (i, m, t), p in predictions.items()])
    for m, gs in ((10, -.25), (30, 0.)):
        path = out / 'test' / f"{c['id']}_s{c['seed']}_h{m}.json"
        raw = json.loads(path.read_text())
        raw['E_stay']['mean'] = 100. if m == 30 else 4.
        for twin, _, _ in D.D4.NOWCAST:
            raw['twins'][twin].update(G_S=gs, pct_E_stay=100 * gs / raw['E_stay']['mean'], se=.0625)
        put(path, raw)
    D.score()
    with (out / 'score_rows.csv').open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 178
    row = rows[0]
    assert float(row['pred30']) == .25 and row['inc_ok'] == 'True'
    assert row['level_ok'] == 'False' and row['noise_ok'] == 'False'
    assert float(row['inc_ratio']) == 2.


def test_zero_predicted_increment_has_no_ratio(out):
    scoring_inputs(out)
    predictions = D._predictions()
    for (i, m, twin), p in list(predictions.items()):
        if i.startswith('C') and i.endswith('_r08') and m == 10:
            predictions[i, m, twin] = predictions[i, 30, twin]
    prediction_file(out, [dict(id=i, h_mult=m, twin=t, pred_abs=p) for (i, m, t), p in predictions.items()])
    D.score()
    result = json.loads((out / 'score.json').read_text())
    band = result['arms']['C']['groups']['band']
    assert band['n'] == 20 and band['n_inc_ratio'] == 0
    assert band['median_inc_ratio'] is None and result['H2']['verdict'] == 'NOT_EVALUABLE'
    with (out / 'score_rows.csv').open() as f:
        assert all(row['inc_ratio'] == '' for row in csv.DictReader(f) if row['arm'] == 'C' and row['r'] == '0.8')


def test_d6_uses_sum_of_standard_errors_and_inclusive_threshold(out):
    cases = scoring_inputs(out)
    c = cases[3]  # Both plug-in rows originally pass.
    for m in (10, 30):
        path = out / 'test' / f"{c['id']}_s{c['seed']}_h{m}.json"
        raw = json.loads(path.read_text())
        raw['E_stay']['mean'] = 4. if m == 10 else 8.
        for twin in raw['twins'].values():
            twin['pct_E_stay'] = 100 * twin['G_S'] / raw['E_stay']['mean']
        # e=.5, growth=.75-.5*.5=.5, 2*(se30+e*se10)=.5.
        raw['twins']['fluid'].update(pct_E_stay=.5 if m == 10 else .75,
                                     G_S=.02 if m == 10 else .06,
                                     se_pct=.25 if m == 10 else .125)
        put(path, raw)
    D.score()
    d6 = json.loads((out / 'score.json').read_text())['D6-C']
    assert d6['n'] == 60 and d6['share'] == .9 and d6['verdict'] == 'PASS'


def test_verify_lock_success_byte_change_and_missing(out, monkeypatch, capsys):
    monkeypatch.setattr(D, 'ROOT', out)
    frozen = out / 'frozen.txt'
    frozen.write_bytes(b'abc')
    put(out / 'lock.json', dict(created='fixture', sha256={'frozen.txt': hashlib.sha256(b'abc').hexdigest()}))
    D.main(['verify-lock'])
    assert 'LOCK_PASS 1' in capsys.readouterr().out
    frozen.write_bytes(b'abd')
    with pytest.raises(SystemExit) as exc:
        D.verify_lock()
    assert exc.value.code == 1 and 'mismatch' in capsys.readouterr().out
    frozen.unlink()
    with pytest.raises(SystemExit) as exc:
        D.verify_lock()
    assert exc.value.code == 1


def test_manifest_exclusive_and_exact_hashes(out):
    put(out / 'test' / 'a.json', {'value': 1})
    put(out / 'test' / 'b.json', {'value': 2})
    D.manifest()
    manifest = json.loads((out / 'raw_manifest.json').read_text())
    assert manifest['n'] == 2
    assert manifest['sha256'] == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (out / 'test').glob('*.json')}
    with pytest.raises(FileExistsError):
        D.manifest()


def test_run_reuses_resumable_sorted_tasks_and_checks_signature(out, monkeypatch):
    cases = [case('C', 0), case('H', 1)]
    put(out / 'cases.json', cases)
    for c, ti in zip(cases, (10., 30.)):
        put(D._train_path(c), training(c, ti))
    existing = out / 'test' / f"{cases[0]['id']}_s{cases[0]['seed']}_h10.json"
    put(existing, {'existing': True})
    observed = []

    class Pool:
        def __init__(self, **kwargs):
            assert kwargs['max_workers'] == 2

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def map(self, fn, tasks):
            assert fn is P.job
            observed.extend(tasks)
            return []

    monkeypatch.setattr('concurrent.futures.ProcessPoolExecutor', Pool)
    before = D.D4B.OUT, D.D4B.CASES, D.D4B.PRED
    D.run(2)
    assert (D.D4B.OUT, D.D4B.CASES, D.D4B.PRED) == before
    assert [t[3] * t[2]['T_int'] for t in observed] == [900., 300., 300.]
    assert all(t[0] == 'test' and t[1] in cases and not t[-1] for t in observed)
    assert all(t[4] != existing for t in observed)
    put(D._train_path(cases[1]), dict(training(cases[1]), case_sha256='bad'))
    with pytest.raises(AssertionError):
        D.run(2)
    assert (D.D4B.OUT, D.D4B.CASES, D.D4B.PRED) == before


def test_tau_below_one_real_trace_smoke(monkeypatch):
    c = dict(id='evd4c_tau08_smoke', cls='trace_cox', lamA=6.5, lamB=6.25, u=.5,
             params=dict(series=D.SER_L, key='s0', path_keys=['s0', 's1'], bin=.01),
             seed=15000, n_inst=16, spacing_mult=3, train_T=200., sample_dt=.2,
             h_mult=[10, 30], batches=4, tau=.8)
    P.validate(c)
    sampled = []
    backlog = P.backlog

    def record_backlog(run, ts):
        sampled.append(float(ts[0]))
        return backlog(run, ts)

    monkeypatch.setattr(P, 'backlog', record_backlog)
    start = time.perf_counter()
    tr = P.train(c)
    assert sampled[0] - sampled[2] == pytest.approx(.8, abs=1e-12)
    sampled.clear()
    raw = P.simulate(c, 10 * tr['T_int'], tr)
    assert sampled[0] - sampled[2] == pytest.approx(.8, abs=1e-12)
    json.dumps([tr, raw], allow_nan=False)
    assert raw['tau'] == .8 and raw['seed'] == 1015000 and len(raw['twins']) == 8
    assert raw['E_stay']['mean'] > 0 and tr['T_int'] > 0
    assert raw['spacing'] == max(P.TAU, 3 * tr['T_int'])
    print('\ntau08 smoke:', json.dumps(dict(T_int=tr['T_int'], train_CPU=tr['CPU'], simulate_CPU=raw['CPU'],
                                           wall=time.perf_counter() - start, E_stay=raw['E_stay'])))


@pytest.mark.parametrize('stage,mode', [('train', ''), ('train', 'train_fail'), ('test', ''),
                                       ('test', 'lock_fail'), ('test', 'retry'), ('test', 'run_fail'),
                                       ('test', 'score_fail')])
def test_pipeline_stages_with_fake_commands(tmp_path, stage, mode):
    """Only stubs execute; no real shutdown, train, test, timeout or VM access."""
    repo, calls, log = tmp_path / 'smr', tmp_path / 'calls', tmp_path / 'pipeline.log'
    (repo / '.venv/bin').mkdir(parents=True)
    (repo / 'experiments/explore_ctmc').mkdir(parents=True)
    (repo / '.venv/bin/activate').write_text(':\n')
    (repo / 'experiments/explore_ctmc/env.sh').write_text(':\n')
    fake_python = repo / '.venv/bin/python'
    fake_python.write_text('''#!/bin/bash
echo "python $*" >> "$EV_D4C_CALLS"
case "$EV_D4C_FAIL_MODE:$*" in
  train_fail:*cases_all.json*|lock_fail:*verify-lock*|run_fail:*" run "*|score_fail:*" score") exit 9 ;;
  retry:*" run 32"|retry:*" run 16") exit 9 ;;
esac
''')
    fake_python.chmod(0o755)
    bin_path = tmp_path / 'bin'
    bin_path.mkdir()
    for command, body in dict(timeout='shift\nexec "$@"', sync='exit 0', sudo='exit 0').items():
        stub = bin_path / command
        stub.write_text(f'#!/bin/bash\necho "{command} $*" >> "$EV_D4C_CALLS"\n{body}\n')
        stub.chmod(0o755)
    # Substitute only the VM locations in a temp copy; leave HOME and source intact.
    source = (D.ROOT / 'experiments/ext_validity/ev_d4c_pipeline.sh').read_text()
    source = source.replace('L=~/ev_d4c.log', f'L="{log}"').replace('cd ~/smr', f'cd "{repo}"')
    script = tmp_path / 'pipeline.sh'
    script.write_text(source)
    env = dict(os.environ, PATH=str(bin_path) + os.pathsep + os.environ['PATH'],
               EV_D4C_CALLS=str(calls), EV_D4C_FAIL_MODE=mode, WORKERS='32')
    proc = subprocess.run(['bash', str(script), stage], env=env, capture_output=True, text=True, timeout=5)
    lines, logged = calls.read_text().splitlines(), log.read_text()
    commands = [line for line in lines if line.startswith('python ')]
    assert proc.returncode == (0 if mode in ('', 'retry') else 9 if mode != 'run_fail' else 1)
    assert 'STAGE_START' in logged
    if stage == 'train':
        assert not any('poweroff' in line for line in lines)
        assert '--out results/ext_validity/ev_d4c/train_probe --workers 32' in commands[0]
        if mode:
            assert 'FAILED step=main_train' in logged and 'TRAIN_DONE' not in logged
            assert len(commands) == 3
        else:
            assert [c.split()[-1] for c in commands[3:]] == ['select', 'predict', 'describe']
            assert 'TRAIN_DONE' in logged
    else:
        assert commands[0].endswith('verify-lock')
        assert lines[-2:] == ['sync ', 'sudo -n poweroff']
        if mode == 'lock_fail':
            assert len(commands) == 1 and 'PIPELINE_DONE' not in logged
        elif mode == 'run_fail':
            assert [c.split()[-1] for c in commands[1:]] == ['32', '16', '8']
            assert 'PIPELINE_DONE' not in logged
        else:
            assert commands[-2].endswith('manifest') and commands[-1].endswith('score')
            if mode == 'retry':
                assert [c.split()[-1] for c in commands[1:-2]] == ['32', '16', '8']
            assert ('PIPELINE_DONE' in logged) == (mode != 'score_fail')
