"""Doan Van Tai — wrapper, comparison schema and saved W1b path checks."""
import copy
from fractions import Fraction as F
import json

import pytest

from experiments.explore_ctmc import ctmc
from experiments.letter import e3_agediff, shat, trunc_n2 as trunc


def test_choose_n_doubles_attribute_and_import_binding_and_restores(monkeypatch):
    original = ctmc.choose_N
    monkeypatch.setattr(e3_agediff, 'imported_choose_N', original, raising=False)
    monkeypatch.setattr(shat, 'choose_N', original, raising=False)
    args = (F(9), F(1, 20))
    expected = original(*args, a=F(15, 2))
    with trunc.scaled_choose_n(2):
        assert ctmc.choose_N(*args, a=F(15, 2)) == 2 * expected
        assert e3_agediff.ctmc.choose_N is ctmc.choose_N
        assert e3_agediff.imported_choose_N(*args, a=F(15, 2)) == 2 * expected
        assert shat.choose_N(*args, a=F(15, 2)) == 2 * expected
    assert ctmc.choose_N is original
    assert e3_agediff.imported_choose_N is original
    assert shat.choose_N is original
    with pytest.raises(RuntimeError), trunc.scaled_choose_n(2):
        raise RuntimeError('restore on failure too')
    assert ctmc.choose_N is original and shat.choose_N is original
    with trunc.scaled_choose_n(1):
        assert ctmc.choose_N(*args, a=F(15, 2)) == expected


@pytest.mark.parametrize('scale', [0, 3])
def test_unsupported_n_scale_refused(scale):
    with pytest.raises(ValueError), trunc.scaled_choose_n(scale):
        pass


def synthetic():
    return [dict(age_label='seconds_1', tau=1.0, cpu_seconds=5.0, N={'A': 10},
                 chains={'A_stay': {'N': 10, 'r': 2.0, 'T_int': 4.0}},
                 asymptotic={'z_inf': 2.0, 'B': 3.0, 'a_inf_switch': True},
                 count=3, h=[dict(h='1/2', G_S=1.0, Cref=100.0,
                     regret={'M0_new': 2.0, 'static': 3.0},
                     margin={'0': {'new': 2.0, 'old': 1.0, 'share_new': .5}},
                     margin_best={'new': '0'}, shares={'M0_new': .5, 'static': 1.0},
                     tie_mass={'c11': .125}, tie_flag=False,
                     hybrid_levels={'mmpp_est': {'s_hat': 2.0, 'regret_new': 3.0,
                         'regret_old': 4.0, 'G_S': 1.0, 'excess_cost_new': 3.0}},
                     z_pred_first_order_ko=2.0, flags=[])])]


def test_compare_field_groups_argmax_and_operational_exclusions():
    old, new = synthetic(), synthetic()
    new[0]['h'][0]['G_S'] += 5e-7
    new[0]['h'][0]['Cref'] += 5e-8
    new[0]['cpu_seconds'] = 999.0
    new[0]['N']['A'] = 20
    new[0]['chains']['A_stay']['N'] = 20
    result = trunc.compare_evaluations(old, new, 'R')
    assert result['passed']
    pct = result['groups']['percentage_pp']
    assert pct['max_difference'] == pytest.approx(5e-7)
    assert pct['argmax'] == dict(regime='R', age='seconds_1', h='1/2',
                               field='[].h[].G_S', baseline=1., candidate=1. + 5e-7)
    assert result['groups']['relative']['max_difference'] == pytest.approx(5e-10, rel=1e-6)
    assert result['groups']['discrete']['max_difference'] == 0
    assert '[].h[].regret.static' in pct['fields']
    assert '[].h[].hybrid_levels.mmpp_est.regret_new' in pct['fields']
    assert '[].h[].z_pred_first_order_ko' in pct['fields']
    assert '[].h[].tie_mass.c11' in result['groups']['relative']['fields']
    assert '[].h[].tie_flag' in result['groups']['discrete']['fields']
    assert '[].N.A' in result['excluded_fields']
    assert '[].chains.A_stay.T_int' in result['groups']['relative']['fields']


@pytest.mark.parametrize('group,change', [
    ('percentage_pp', lambda e: e['h'][0].update(G_S=1.000002)),
    ('relative', lambda e: e['h'][0].update(Cref=100.000001)),
    ('discrete', lambda e: e.update(count=4)),
    ('discrete', lambda e: e['h'][0].update(tie_flag=True)),
    ('discrete', lambda e: e['h'][0]['margin_best'].update(new='1/100')),
    ('discrete', lambda e: e['h'][0]['shares'].update(static=0.0)),
])
def test_compare_rejects_each_threshold_or_discrete_change(group, change):
    old, new = synthetic(), synthetic()
    change(new[0])
    result = trunc.compare_evaluations(old, new)
    assert not result['passed']
    assert not result['groups'][group]['passed']
    assert any(v['group'] == group for v in result['violations'])


def test_missing_and_extra_fields_and_empty_structures_are_not_ignored():
    old, new = synthetic(), synthetic()
    del new[0]['h'][0]['Cref']
    new[0]['h'][0]['extra_decision'] = True
    new[0]['h'][0]['flags'] = ['negative']
    result = trunc.compare_evaluations(old, new)
    assert not result['passed']
    assert '[].h[].Cref' in [f['field'] for f in result['missing_fields']]
    assert '[].h[].extra_decision' in [f['field'] for f in result['extra_fields']]
    assert '[].h[].flags' in [f['field'] for f in result['missing_fields']]


def test_unknown_numeric_field_is_an_error_not_silently_ignored():
    old = synthetic()
    old[0]['unclassified_numeric'] = 1.0
    with pytest.raises(ValueError, match='unclassified numeric'):
        trunc.compare_evaluations(old, copy.deepcopy(old))


def test_zero_reference_has_no_tolerance_floor_and_json_stays_finite():
    old, new = synthetic(), synthetic()
    old[0]['h'][0]['E_gap'] = 0.0
    new[0]['h'][0]['E_gap'] = 1e-30
    result = trunc.compare_evaluations(old, new)
    assert not result['passed']
    assert result['groups']['relative']['max_difference'] == 'infinity'
    json.dumps(result, allow_nan=False)
    new[0]['h'][0]['E_gap'] = 0.0
    assert trunc.compare_evaluations(old, new)['passed']


def test_population_saved_input_order_and_chain_n_guard():
    records = trunc.load_population()
    assert len(records) == 27 and records[0]['raw']['id'] == trunc.HEAVIEST
    assert records[-1]['raw']['id'] == trunc.LIGHTEST
    for record in records:
        assert all(e['age_label'] == label for e, label in
                   zip(record['raw']['evaluations'], trunc.AGE_LABELS))
        trunc.chain_keys(record, 2)
    saved = records[-1]['raw']
    doubled = copy.deepcopy(saved['evaluations'])
    for ev in doubled:
        ev['N'] = {s: 2*n for s, n in ev['N'].items()}
        for chain in ev['chains'].values():
            chain['N'] *= 2
    trunc.guard_n(doubled, saved, 2)
    doubled[3]['chains']['B_switch']['N'] -= 1
    with pytest.raises(AssertionError, match='N guard'):
        trunc.guard_n(doubled, saved, 2)


def test_age_job_uses_saved_age_levels_horizons_and_disagree_false(monkeypatch):
    record = trunc.load_population()[-1]['raw']
    case, old = record['case'], record['evaluations'][3]
    captured = {}

    def evaluate(*args, **kwargs):
        captured.update(args=args, kwargs=kwargs)
        return {}

    monkeypatch.setattr(shat, 'evaluate_agediff', evaluate)
    value, _ = trunc.execute_job('age', ({'T_int': case['T_int_max']}, case,
                             old['age_label'], old['tau'], record['levels']), 2)
    assert captured['args'][4] == case['hs']
    assert captured['args'][5] == old['tau']
    assert captured['kwargs']['shat_levels'] == record['levels']
    assert captured['kwargs']['disagree'] is False
    assert value['age_label'] == old['age_label']


def test_v_job_preserves_rational_horizons_in_serial_input_type(monkeypatch):
    captured = {}

    def timed(job):
        key, horizons = job
        captured['horizons'] = horizons
        return key, 'values', 0.0

    monkeypatch.setattr(shat, 'timed_v', timed)
    key = ('9', '1/20', 398, '15/2')
    value, _ = trunc.execute_job('V', (key, ['183/25', '8']), 1)
    assert captured['horizons'] == [F(183, 25), F(8)]
    assert all(isinstance(h, F) for h in captured['horizons'])
    assert value == (key, 'values')


def test_write_once_refuses_existing_content(tmp_path):
    path = tmp_path / 'raw.json'
    trunc.write_once(path, {'first': True})
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        trunc.write_once(path, {'first': False})
    assert path.read_bytes() == before


def test_incomplete_full_comparison_cannot_pass():
    report = trunc.compare_evaluations(synthetic(), synthetic())
    result = trunc.combine_reports([report], ['R1', 'R2'], ['R2'], [])
    assert result['status'] == 'INCOMPLETE'
    assert result['compared_regimes'] == 1 and result['missing_regimes'] == ['R2']


def test_compare_exports_json_markdown_and_refuses_overwrite(tmp_path, monkeypatch):
    old, new = synthetic(), synthetic()
    new[0]['N']['A'] = 20
    new[0]['chains']['A_stay']['N'] = 20
    case, levels = {'id': 'synthetic'}, {'true_s': 2.0}
    saved = dict(id='synthetic', case=case, levels=levels, evaluations=old)
    candidate = dict(id='synthetic', case=case, levels=levels, n_scale=2,
                     saved_w1b_sha256='synthetic-sha', evaluations=new)
    monkeypatch.setattr(trunc, 'load_population', lambda: [dict(raw=saved, sha256='synthetic-sha')])
    trunc.write_once(tmp_path / 'raw/synthetic.json', candidate)
    result = trunc.compare(tmp_path)
    assert result['status'] == 'PASS'
    assert json.loads((tmp_path / 'compare.json').read_text()) == result
    markdown = (tmp_path / 'compare.md').read_text()
    assert 'percentage_pp' in markdown and '[].h[].regret.static' in markdown
    assert result['thresholds'] == {'percentage_pp': 1e-6, 'relative': 1e-9, 'discrete': 0}
    before = (tmp_path / 'compare.json').read_bytes()
    with pytest.raises(FileExistsError):
        trunc.compare(tmp_path)
    assert (tmp_path / 'compare.json').read_bytes() == before


def test_all_saved_numeric_fields_have_explicit_comparison_classes():
    for record in trunc.load_population():
        result = trunc.compare_evaluations(record['raw']['evaluations'],
                                           record['raw']['evaluations'])
        assert result['passed']
        assert all(group['count'] for group in result['groups'].values())


def test_historical_local_n1_code_path_reproduces_saved_w1b(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('saved levels must be used; do not call estimate_levels')

    monkeypatch.setattr(shat, 'estimate_levels', forbidden)
    directory = trunc.pilot_directory(1, trunc.LIGHTEST)
    check_path = directory / 'code_path_check.json'
    # This is the committed phase-1 local fixture, not a new VM execution.
    # The real VM-vs-local failure is retained in DEVIATION_01, never relaxed.
    assert check_path.exists(), 'sync the historical phase-1 fixture; do not rerun truth in tests'
    start = json.loads((directory / 'run_start.json').read_text())
    historical = dict(start['source_sha256'])
    assert historical.pop('experiments/letter/trunc_n2.py') == '76ec92e894c02986c15ddb56c63d97921a8cba6e3b1c1ecb8d173ad2ec1eea32'
    assert historical == {name: value for name, value in trunc.source_hashes().items()
                          if name != 'experiments/letter/trunc_n2.py'}
    saved = next(r for r in trunc.load_population() if r['raw']['id'] == trunc.LIGHTEST)
    raw = json.loads((directory / 'raw' / (trunc.LIGHTEST + '.json')).read_text())
    assert raw['saved_w1b_sha256'] == saved['sha256']
    check = trunc.reproduction_check(saved['raw'], raw)
    assert check['passed'], check
    assert check['max_relative_difference'] <= 1e-12
    assert check['numeric_leaves'] > 5000
    assert raw['n_guard'] == 'PASS'
    print('1N_MAX_RELATIVE_DIFFERENCE', check['max_relative_difference'])


def synthetic_record(scale):
    ev = synthetic()
    ev[0]['N']['A'] *= scale
    ev[0]['chains']['A_stay']['N'] *= scale
    return dict(id='synthetic', case={'id': 'synthetic'}, levels={'true_s': 2.0},
                evaluations=ev, n_scale=scale, saved_w1b_sha256='synthetic-sha')


def test_same_platform_baseline_and_separate_output_roots(tmp_path, monkeypatch):
    saved, one, two = (synthetic_record(scale) for scale in (1, 1, 2))
    # Shared platform offset must disappear from the primary comparison.
    one['evaluations'][0]['h'][0]['Cref'] += 1e-5
    two['evaluations'][0]['h'][0]['Cref'] += 1e-5
    two['evaluations'][0]['h'][0]['G_S'] += 5e-7
    monkeypatch.setattr(trunc, 'load_population', lambda: [dict(raw=saved, sha256='synthetic-sha')])
    trunc.write_once(tmp_path / 'one/raw/synthetic.json', one)
    trunc.write_once(tmp_path / 'two/raw/synthetic.json', two)
    result = trunc.compare(tmp_path / 'score', tmp_path / 'one', tmp_path / 'two')
    assert result['status'] == 'PASS'
    assert result['groups']['relative']['max_difference'] == 0
    assert result['groups']['percentage_pp']['max_difference'] == pytest.approx(5e-7)
    assert result['comparison']['same_platform']
    assert result['comparison']['input_sha256']['synthetic']['baseline_sha256'] == trunc.sha256(tmp_path / 'one/raw/synthetic.json')
    platform = trunc.compare(tmp_path / 'platform', candidate=tmp_path / 'one', candidate_scale=1)
    assert platform['status'] == 'FAIL'
    assert platform['groups']['relative']['max_absolute_difference'] == pytest.approx(1e-5)


@pytest.mark.parametrize('damage', ['missing_baseline', 'wrong_scale', 'wrong_sha', 'wrong_N'])
def test_same_platform_comparison_rejects_invalid_baseline(tmp_path, monkeypatch, damage):
    saved, one, two = (synthetic_record(scale) for scale in (1, 1, 2))
    monkeypatch.setattr(trunc, 'load_population', lambda: [dict(raw=saved, sha256='synthetic-sha')])
    if damage == 'wrong_scale':
        one['n_scale'] = 2
    elif damage == 'wrong_sha':
        one['saved_w1b_sha256'] = 'changed'
    elif damage == 'wrong_N':
        one['evaluations'][0]['N']['A'] += 1
    if damage != 'missing_baseline':
        trunc.write_once(tmp_path / 'one/raw/synthetic.json', one)
    trunc.write_once(tmp_path / 'two/raw/synthetic.json', two)
    with pytest.raises((ValueError, AssertionError)):
        trunc.compare(tmp_path / 'score', tmp_path / 'one', tmp_path / 'two')
    assert not (tmp_path / 'score/compare.json').exists()


def test_cli_routes_distinct_run_and_compare_roots(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(trunc, 'load_population', lambda: 'population')
    monkeypatch.setattr(trunc, 'run_population', lambda *args: calls.append(args))
    assert trunc.main(['run', '--n-scale', '1', '--workers', '12', '--out', str(tmp_path / 'one')]) == 0
    assert calls.pop() == ('population', 1, 12, tmp_path / 'one')
    monkeypatch.setattr(trunc, 'compare', lambda *args: calls.append(args) or {'status': 'PASS'})
    assert trunc.main(['compare', '--out', str(tmp_path / 'score'), '--baseline', str(tmp_path / 'one'),
                       '--candidate', str(tmp_path / 'two')]) == 0
    assert calls.pop() == (tmp_path / 'score', tmp_path / 'one', tmp_path / 'two', 2)
