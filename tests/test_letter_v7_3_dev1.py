"""Doan Van Tai — deviation population, independent archive and integrity checks."""
import ast
import copy
import csv
from datetime import datetime, timedelta
import io
import json
from pathlib import Path
import tarfile

import numpy as np
import pytest

from experiments.letter import v7_3_cong as Cong
from experiments.letter import v7_3_data as Data
from experiments.letter import v7_3_day as Day
from experiments.letter import v7_3_rescore_dev1 as Independent
from experiments.letter import v7_3_score_dev1 as Scoring
from experiments.letter import v7_3_test as Loader
from experiments.letter import v7_3_test_common as C


@pytest.fixture(scope='module', autouse=True)
def locked_files_untouched():
    root = C.ROOT
    lock_path = C.OUT/'lock.json'
    locked = C.read_json(lock_path)
    before = {root/name: digest for name, digest in locked['sha256'].items()
              if not name.startswith('sndlib:')}
    before[lock_path] = C.sha256(lock_path)
    assert all(C.sha256(path) == digest for path, digest in before.items())
    yield
    assert all(C.sha256(path) == digest for path, digest in before.items())


@pytest.mark.parametrize('function', [Scoring.exclusion_from_maxima, Independent.exclusion_from_maxima])
def test_strict_threshold_and_open_interval(function):
    dates = ['2005-06-15', '2005-06-16', '2005-06-23', '2005-06-27']
    peaks = [850., 1000., 1230., 19640.]
    for threshold in np.linspace(np.nextafter(1.23, np.inf), np.nextafter(19.64, -np.inf), 101):
        result = function(dates, peaks, 1000., threshold=threshold)
        assert [r['date'] for r in result['excluded_days']] == ['2005-06-27']
    result = function(dates, peaks, 1000.)
    assert result['threshold_ratio'] == 2.
    assert result['excluded_days'][0]['ratio'] == 19.64
    assert result['top_5_test_ratios'][1]['ratio'] == 1.23
    boundary = function(['below', 'equal', 'above'],
                        [np.nextafter(2000., 0.), 2000., np.nextafter(2000., np.inf)], 1000.)
    assert [r['date'] for r in boundary['excluded_days']] == ['above']


@pytest.mark.parametrize('function', [Scoring.exclusion_from_maxima, Independent.exclusion_from_maxima])
@pytest.mark.parametrize('peaks,train,threshold', [
    ([1.], 0., 2.), ([1.], float('nan'), 2.), ([1.], 1., 0.),
    ([1.], 1., float('inf')), ([float('nan')], 1., 2.), ([-1.], 1., 2.), ([], 1., 2.)])
def test_invalid_exclusion_inputs_refused(function, peaks, train, threshold):
    with pytest.raises(ValueError, match='invalid demand'):
        function(['day'], peaks, train, threshold=threshold)


def analytic_raw(params):
    """Known constant action gap: M0 fresh ties; stale and Hybrid choose Switch."""
    n = params['N_test']
    hs = np.asarray(params['hours'])*3600
    v = np.empty((n, 2, 4))
    v[:, 0] = 100*hs
    v[:, 1] = 80*hs
    decisions = np.ones((n, 3, 2, 2, 4), dtype=np.int16)
    decisions[:, 0, 0] = 0
    flags = np.zeros_like(decisions, dtype=bool)
    flags[:, 0, 0] = True
    costs = np.where(decisions == 0, 100*hs, 80*hs)
    cref = np.full((n, 4), 80*hs)
    old = np.ones((n, 2, 2, 4))
    old[:, :, 1] = 0
    return dict(V=v, paired_evaluation=np.repeat(v[:, None], params['R_eval'], axis=1),
        reference_decision_rollouts=np.repeat(v[:, None], params['R_dec'], axis=1),
        C_ref=cref, reference_decision=np.ones((n, 4), dtype=np.int16),
        reference_tie_flags=np.zeros((n, 4), dtype=bool),
        decisions=decisions, tie_flags=flags, costs=costs,
        regret=costs-cref[:, None, None, None, :], G_S=costs[:, :, 1]-costs[:, :, 0],
        M0_predicted_fresh=np.ones((n, 2, 4)), M0_predicted_stale=old,
        h_seconds=hs, tau_seconds=np.asarray(params['tau_seconds']),
        backlog_trace=np.zeros((16, 2)), input_utilization=np.full((24, 2, 1), .5))


@pytest.fixture
def amended_fixture(tmp_path, monkeypatch):
    params = dict(C.read_json(C.ROOT/C.PARAMS), N_test=4, R_dec=2, R_eval=2)
    root = tmp_path/'repo'
    sndlib = tmp_path/'sndlib'
    out = root/'out'
    sndlib.mkdir()
    train, safe, anomaly = '2005-05-05', '2005-06-15', '2005-06-27'
    config = dict(start_slot=0, train_dates=[train])
    network = dict(nodes=['a', 'b'], demands=[dict(id='ab', source='a', target='b')])
    # Every day is complete, including the prior two hours, as required by phase A.
    with tarfile.open(sndlib/Data.TM_NAME, 'w:gz') as archive:
        for date, peak in ((train, 100.), (safe, 123.), (anomaly, 1964.)):
            start = datetime.fromisoformat(date)
            for slot in range(-8, 96):
                when = start+timedelta(minutes=15*slot)
                payload = Data.format_tm([peak], [True], network, when).encode()
                member = tarfile.TarInfo(f'tm-{when:%Y%m%d-%H%M}.txt')
                member.size = len(payload)
                archive.addfile(member, io.BytesIO(payload))
    C.write_json(root/C.PARAMS, params)
    C.write_json(root/C.BASE/'data_manifest.json', dict(train_dates=[train], test_dates=[safe, anomaly]))
    C.write_json(root/params['training_dir']/'configuration.json', config)
    lock_path = out/'lock.json'
    C.write_json(lock_path, dict(synthetic=True))
    verified = C.VerifiedLock(str(lock_path), C.sha256(lock_path))
    monkeypatch.setattr(C, 'ROOT', root)
    monkeypatch.setattr(C, 'verify_lock', lambda *args, **kwargs: verified)
    monkeypatch.setattr(C, 'data_root', lambda: sndlib)
    monkeypatch.setattr(Data, 'topology', lambda *args: network)
    monkeypatch.setattr(Cong, 'OUT', root/params['training_dir'])

    def cached_training(path):
        assert path == Cong.OUT
        return dict(days=np.full((1, 24, 1), 100.)), {}, config

    monkeypatch.setattr(Day, 'load', cached_training)
    labels, receipts = [], []
    raw = analytic_raw(params)
    for g in params['regimes']:
        for date in (safe, anomaly):
            label = dict(regime=g, date=date, stratum='S' if date == safe else 'O',
                         max_utilization_by_action=[.5, .5] if date == safe else [2., 2.])
            labels.append(label)
            if date == anomaly:
                continue
            path = out/'records'/f'{g}_{date}.npz'
            path.parent.mkdir(parents=True, exist_ok=True)
            np.savez(path, **raw)
            digest = C.sha256(path)
            C.write_json(path.with_suffix('.json'), dict(label, status='COMPLETE', npz_sha256=digest))
            receipts.append(dict(regime=g, date=date, npz_sha256=digest))
    inputs = dict(dates=[safe, anomaly], requested_dates=[safe, anomaly], records=labels,
                  exclusions=[], lock_sha256=verified.digest)
    run = dict(status='INCOMPLETE', expected_records=len(labels), records=receipts,
               lock_sha256=verified.digest)
    C.write_json(out/'inputs.json', inputs)
    C.write_json(out/'run_summary.json', run)
    return out, inputs, run, params, verified


def test_archive_and_loader_exclusions_match_independently(amended_fixture):
    out, inputs, run, params, verified = amended_fixture
    original = copy.deepcopy(inputs)
    scored = Scoring.recompute_exclusion(inputs, verified)
    filtered = Scoring.amend_inputs(inputs, run, params, scored)
    other_inputs, independent = Independent.independent_inputs(inputs, run, params)
    assert scored == independent
    assert filtered == other_inputs
    assert inputs == original
    assert filtered['dates'] == ['2005-06-15']
    assert len(filtered['records']) == 3
    assert scored['train_maximum_Mbps'] == 100.
    assert scored['excluded_days'][0]['ratio'] == 19.64


@pytest.mark.parametrize('change', ['missing', 'extra', 'duplicate', 'wrong_regime', 'input_omission'])
def test_refuse_different_completed_set(amended_fixture, change):
    out, inputs, run, params, verified = amended_fixture
    if change == 'missing':
        run['records'].pop()
    elif change == 'extra':
        run['records'].append(dict(regime='DAY1', date='2005-06-27'))
    elif change == 'duplicate':
        run['records'][-1] = run['records'][0]
    elif change == 'wrong_regime':
        run['records'][0]['regime'] = 'OTHER'
    else:
        inputs['records'].pop()
    deviation = Scoring.recompute_exclusion(inputs, verified)
    with pytest.raises(ValueError, match='population|completed set'):
        Scoring.amend_inputs(inputs, run, params, deviation)
    with pytest.raises(ValueError, match='population|completed set'):
        Independent.independent_inputs(inputs, run, params)


def test_wrappers_verify_lock_before_reading_any_inputs(tmp_path, monkeypatch):
    calls = []

    def failed_lock(*args, **kwargs):
        calls.append('lock')
        raise ValueError('lock mismatch')

    def forbidden(*args, **kwargs):
        pytest.fail('input read before verified lock')

    monkeypatch.setattr(C, 'verify_lock', failed_lock)
    monkeypatch.setattr(C, 'read_json', forbidden)
    monkeypatch.setattr(Day, 'load', forbidden)
    monkeypatch.setattr(Loader, 'load_days', forbidden)
    for wrapper in (Scoring.score, Independent.rescore):
        with pytest.raises(ValueError, match='lock mismatch'):
            wrapper(tmp_path)
    assert calls == ['lock', 'lock']
    assert list(tmp_path.iterdir()) == []


def test_independent_imports_and_lock_closure():
    tree = ast.parse(Path(Independent.__file__).read_text())
    banned = {'v7_3_score', 'v7_3_score_dev1', 'v7_3_test'}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(not banned.intersection(alias.name.split('.')) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert not banned.intersection((node.module or '').split('.'))
            assert all(alias.name not in banned for alias in node.names)
    closure = C.source_paths()
    assert Path('experiments/letter/v7_3_score_dev1.py') not in closure
    assert Path('experiments/letter/v7_3_rescore_dev1.py') not in closure


def test_analytic_roundtrip_no_overwrite_or_original_input_changes(amended_fixture):
    out, inputs, run, params, verified = amended_fixture
    before = {p: C.sha256(p) for p in out.rglob('*') if p.is_file()}
    summary = Scoring.score(out)
    assert summary['analysis'] == 'AMENDED_ANALYSIS_DEVIATION_01'
    assert summary['original_run_status'] == 'INCOMPLETE'
    assert summary['completed_records'] == 3 and summary['cases'] == 24
    assert summary['F1_original_population']['fraction'] == .5
    assert summary['forecasts']['F1']['fraction'] == 1.
    result = Independent.rescore(out)
    assert result['status'] == 'MATCH' and result['mismatches'] == []
    assert result['cases_recomputed'] == 24
    with (out/'score_dev1/cases.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    assert float(rows[0]['M0_G_S_Mbit']) == -20.
    assert float(rows[0]['Hybrid_both_R_Mbit']) == 0.
    for wrapper in (Scoring.score, Independent.rescore):
        with pytest.raises(FileExistsError):
            wrapper(out)
    assert all(C.sha256(p) == digest for p, digest in before.items())


def test_non_evaluable_numpy_counts_serialize_without_metric_changes(amended_fixture):
    out, inputs, run, params, verified = amended_fixture
    params['evaluable_threshold_Mbit'] = 1.e9
    (C.ROOT/C.PARAMS).write_text(json.dumps(params))
    summary = Scoring.score(out)
    assert summary['evaluable_cases'] == 0 and summary['non_evaluable_cases'] == 24
    saved = C.read_json(out/'score_dev1/summary.json')
    assert saved['descriptions']['DAY1_S']['non_evaluable_Mbit']['M0']['harm_cases'] == 8
    assert saved['descriptions']['DAY1_S']['non_evaluable_Mbit']['Hybrid']['harm_cases'] == 0
    assert Independent.rescore(out)['status'] == 'MATCH'


@pytest.mark.parametrize('corrupt_partial', [False, True])
def test_json_failure_recovery_requires_identical_preserved_csv(amended_fixture, monkeypatch, corrupt_partial):
    out, inputs, run, params, verified = amended_fixture
    original_write = C.write_json

    def fail_summary(path, value):
        if Path(path).name == 'summary.json':
            raise TypeError('synthetic JSON I/O failure')
        original_write(path, value)

    monkeypatch.setattr(C, 'write_json', fail_summary)
    with pytest.raises(TypeError, match='synthetic JSON'):
        Scoring.score(out)
    csv_path = out/'score_dev1/cases.csv'
    before = csv_path.read_bytes()
    monkeypatch.setattr(C, 'write_json', original_write)
    if corrupt_partial:
        csv_path.write_bytes(before+b'corruption')
        with pytest.raises(ValueError, match='not byte-identical'):
            Scoring.score(out)
        assert csv_path.read_bytes() == before+b'corruption'
        assert not (out/'score_dev1/summary.json').exists()
    else:
        Scoring.score(out)
        assert csv_path.read_bytes() == before
        assert Independent.rescore(out)['status'] == 'MATCH'


@pytest.mark.parametrize('tamper', ['verdict', 'case', 'exclusion', 'receipt_hash', 'stratum', 'extra_file'])
def test_tamper_is_detected(amended_fixture, tamper):
    out, inputs, run, params, verified = amended_fixture
    Scoring.score(out)
    if tamper == 'case':
        path = out/'score_dev1/cases.csv'
        path.write_text(path.read_text().replace('-20.0,', '-999.0,', 1))
    elif tamper == 'extra_file':
        (out/'records/OTHER_2005-06-15.npz').write_bytes(b'unexpected')
    else:
        path = out/('score_dev1/summary.json' if tamper == 'verdict' else
                    'score_dev1/deviation.json' if tamper == 'exclusion' else
                    'run_summary.json' if tamper == 'receipt_hash' else
                    'records/DAY1_2005-06-15.json')
        value = C.read_json(path)
        if tamper == 'verdict':
            value['tests']['H1']['verdict'] = 'FAIL'
        elif tamper == 'exclusion':
            value['excluded_days'][0]['ratio'] += .1
        elif tamper == 'receipt_hash':
            value['records'][0]['npz_sha256'] = 'bad'
        else:
            value['stratum'] = 'O'
        path.write_text(json.dumps(value))
    result = Independent.rescore(out)
    assert result['status'] == 'MISMATCH' and result['mismatches']
    if tamper in ('receipt_hash', 'stratum', 'extra_file'):
        with pytest.raises(ValueError, match='integrity|raw files'):
            filtered = Scoring.amend_inputs(inputs, C.read_json(out/'run_summary.json'), params,
                                            Scoring.recompute_exclusion(inputs, verified))
            Scoring.read_completed_records(out, filtered, C.read_json(out/'run_summary.json'), params)
