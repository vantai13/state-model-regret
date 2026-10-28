"""Doan Van Tai — A05-T one-shot gates, independent rescoring and diagnostics on synthetic data only.

No test calls the engine on a grid cell; engine entry points are monkeypatched to fail.
"""
from fractions import Fraction as F
import json
from pathlib import Path

import pytest

from experiments.A05_freeze.predict import discrimination
from experiments.A05_freeze.score_test import score
from experiments.A05_test import gate, invariants, rescore, run
from tests.test_a05_freeze import cfg, predictions, synthetic_outcomes
from tests.test_card_grading import row
from tests.test_engine_guard import isolated_repo, commit, git  # noqa: F401  (fixture)

OPEN = list(gate.OPEN)


def test_opening_list_is_exact_and_sealed_cells_never_reach_engine(monkeypatch):
    gate.check_ids(OPEN)
    for bad in (OPEN + ['R09'], OPEN[:-1], ['R10'] + OPEN[1:], list(reversed(OPEN))):
        with pytest.raises(PermissionError):
            gate.check_ids(bad)
    monkeypatch.setattr(run, 'side_table', lambda *a, **k: pytest.fail('engine called for a sealed cell'))
    monkeypatch.setattr(run, 'load_cell', lambda *a, **k: pytest.fail('cell loaded for a sealed cell'))
    for spec in (('R09', 2), ('R10', 1), ('M01', 2), ('R01', 4)):
        with pytest.raises(PermissionError):
            run.level_task(spec)
    with pytest.raises(PermissionError):
        run.psw_interval('R09', 2)
    frozen = json.loads(Path('experiments/A05_freeze/discrimination.json').read_text())
    assert frozen['outcome_open_ids'] == OPEN and frozen['outcomes_not_needed'] == ['R09', 'R10']


def test_existing_output_refused_and_empty_base_allowed(tmp_path):
    base = tmp_path / 'A05_test'
    gate.require_fresh_output(base)
    base.mkdir()
    gate.require_fresh_output(base)
    (base / '20261028_01').mkdir()
    with pytest.raises(PermissionError, match='one-shot'):
        gate.require_fresh_output(base)


def test_cli_has_no_scientific_overrides(monkeypatch):
    monkeypatch.setattr(run, 'preflight', lambda: pytest.fail('preflight reached with a forbidden option'))
    for option in (['--margin', '0'], ['--ids', 'R09'], ['--dt', '1/480'], ['--metric', 'G_SM'],
                   ['--run-id', 'again'], ['--allow-sealed']):
        with pytest.raises(SystemExit):
            run.main(option)


def test_frozen_chain_checked_before_any_read(monkeypatch):
    def denied():
        raise PermissionError('synthetic freeze mismatch')
    monkeypatch.setattr(run, 'verify_frozen', denied)
    monkeypatch.setattr(run, 'read', lambda p: pytest.fail('input read before freeze check'))
    monkeypatch.setattr(run, 'require_committed_decision', lambda f: pytest.fail('decision read first'))
    with pytest.raises(PermissionError, match='freeze mismatch'):
        run.main([])


def test_missing_decision_stops_before_discrimination_or_grid(monkeypatch):
    monkeypatch.setattr(run, 'verify_frozen', lambda: {'freeze_commit': 'synthetic'})
    def denied(frozen):
        raise PermissionError('synthetic: no committed DL')
    monkeypatch.setattr(run, 'require_committed_decision', denied)
    monkeypatch.setattr(run, 'read', lambda p: pytest.fail('read before decision gate'))
    with pytest.raises(PermissionError, match='no committed DL'):
        run.main([])


def _fixture_repo(repo, *, dl=True, exposure=True, same_commit=True, open_ids=None, marker=True):
    """Synthetic repo: frozen commit, then A05-T sources, then decision+DL+exposure."""
    (repo / 'experiments/A05_freeze').mkdir(parents=True)
    (repo / 'notes').mkdir()
    (repo / 'experiments/A05_freeze/discrimination.json').write_text(json.dumps(
        {'outcome_open_ids': OPEN, 'outcomes_not_needed': ['R09', 'R10']}))
    (repo / gate.DECISION_LOG).write_text('# synthetic log\n')
    (repo / gate.EXPOSURE).write_text('# synthetic exposure\n')
    commit(repo, 'synthetic freeze')
    freeze = git(repo, 'rev-parse', 'HEAD')
    (repo / gate.BASE).mkdir(parents=True)
    (repo / gate.BASE / 'run.py').write_text('# synthetic runner\n')
    commit(repo, 'synthetic sources')
    frozen = dict(freeze_commit=freeze, predictions_sha256='p' * 64, discrimination_sha256='d' * 64)
    decision = dict(status='IRREVERSIBLE_A05_T_DECISION', open_ids=open_ids or OPEN, sealed_ids=['R09', 'R10'],
                    scoring_dt_s='1/240', check_dt_s='1/120', freeze_commit=freeze,
                    predictions_sha256=frozen['predictions_sha256'],
                    discrimination_sha256=frozen['discrimination_sha256'],
                    source_sha256=gate.sources(repo), decided_at='synthetic', provenance='synthetic')
    if dl:
        heading = gate.DL_MARKER if marker else '### DL-999'
        (repo / gate.DECISION_LOG).write_text('# synthetic log\n\n' + heading + ' — synthetic\n')
    if not same_commit:
        commit(repo, 'DL alone')
    if exposure:
        (repo / gate.EXPOSURE).write_text('# synthetic exposure\n' + gate.EXPOSURE_MARKER + '\n')
    (repo / gate.DECISION).write_text(json.dumps(decision))
    commit(repo, 'synthetic decision')
    return frozen


def test_decision_gate_accepts_complete_record(isolated_repo):
    frozen = _fixture_repo(isolated_repo)
    result = gate.require_committed_decision(frozen, repo=isolated_repo)
    assert result['decision_commit'] == git(isolated_repo, 'rev-parse', 'HEAD')
    (isolated_repo / gate.BASE / 'run.py').write_text('# changed after decision\n')
    with pytest.raises(PermissionError, match='clean committed tree'):
        gate.require_committed_decision(frozen, repo=isolated_repo)


@pytest.mark.parametrize('kwargs,reason', [
    (dict(dl=False), 'share one commit'), (dict(exposure=False), 'share one commit'),
    (dict(same_commit=False), 'share one commit'), (dict(marker=False), 'lacks the committed'),
    (dict(open_ids=OPEN + ['R09']), 'open_ids differs')])
def test_decision_gate_rejects_incomplete_records(isolated_repo, kwargs, reason):
    frozen = _fixture_repo(isolated_repo, **kwargs)
    with pytest.raises(PermissionError, match=reason):
        gate.require_committed_decision(frozen, repo=isolated_repo)


def test_decision_gate_rejects_changed_source_after_registration(isolated_repo):
    frozen = _fixture_repo(isolated_repo)
    (isolated_repo / gate.BASE / 'extra.py').write_text('# unregistered helper\n')
    commit(isolated_repo, 'unregistered source')
    with pytest.raises(PermissionError, match='source differs'):
        gate.require_committed_decision(frozen, repo=isolated_repo)


def _set(row_, key, lo, hi=None):
    row_['intervals'][key] = [lo, lo if hi is None else hi]


def _truth(cids, value, C=100, radius=0):
    """Synthetic outcomes: GS=GM=Gamma ratio `value` (fraction of Cref) on both levels."""
    data = {'fine': {}, 'coarse': {}}
    for cid in cids:
        for name, ref in (('fine', 2), ('coarse', 1)):
            g = F(value) * C
            r = row(ref, GS=g, GM=g, Gamma=g, C=C)
            r['dt_s'] = str(F(1, 120 * ref)); r['reference_context']['dt_s'] = r['dt_s']
            r['intervals']['R00'] = [1, 1]
            if radius:
                for k in ('G_S', 'G_M', 'Gamma'):
                    _set(r, k, g - F(radius) * C, g + F(radius) * C)
            data[name][cid] = r
    return data


@pytest.mark.parametrize('value,radius,expected', [
    ('.02', 0, 'SUPPORT'),              # truth equals H1
    ('0', 0, 'FALSIFY'),                # truth equals H0
    ('.0105', 0, 'WEAKEN'),             # d = .001
    ('.01125', '.00005', 'INCONCLUSIVE'),  # d interval straddles the margin
    ('.01', '.0005', 'INCONCLUSIVE'),   # truth radius above m/10: cells unavailable
])
def test_independent_rescore_matches_frozen_scorer(value, radius, expected):
    p = predictions()                    # H0=0, H1=.02 for every contrast
    d = discrimination(p, cfg())
    data = _truth(d['outcome_open_ids'], value, radius=radius)
    frozen = json.loads(json.dumps(score(data, p, d, cfg()), default=str))
    mine = rescore.rescore(data, p, d)
    assert mine['PC4']['interpolation']['verdict'] == expected
    assert rescore.agree(mine, frozen) == []


def test_independent_rescore_detects_disagreement_and_unauthorized_cells():
    p = predictions(); d = discrimination(p, cfg())
    data = _truth(d['outcome_open_ids'], '.02')
    frozen = json.loads(json.dumps(score(data, p, d, cfg()), default=str))
    frozen['PC4']['interpolation']['verdict'] = 'FALSIFY'
    assert rescore.agree(rescore.rescore(data, p, d), frozen)
    real = json.loads(Path('experiments/A05_freeze/discrimination.json').read_text())
    with pytest.raises(PermissionError):
        rescore.rescore(_truth(['R09'], '.02'), p, real)


def test_equivalence_branches_and_headroom_label_match():
    p = predictions(); d = discrimination(p, cfg())
    data = synthetic_outcomes(d['outcome_open_ids'])
    data['fine']['R06']['intervals']['G_M'] = [1, 1]   # GM/Cref=.01 > .005: counterexample
    data['coarse']['R06']['intervals']['G_M'] = [1, 1]
    frozen = json.loads(json.dumps(score(data, p, d, cfg()), default=str))
    mine = rescore.rescore(data, p, d)
    assert mine['C1']['verdict'] == 'DOES_NOT_STAND' and mine['K5']['verdict'] == 'STANDS'
    assert rescore.agree(mine, frozen) == []


def test_extra_invariants_catch_corrupted_rows():
    record = dict(id='R01', kappa='3/5', eta='1/2', h='8', yA='1', yB='1', H_coarse=960)
    cell = dict(id='R01', kappa=F(3, 5), eta=F(1, 2), h=F(8), yA=F(1), yB=F(1), H_coarse=960)
    r = row(2, GS=1, GM=0, Gamma=1, C=100)
    r['dt_s'] = '1/240'; r['reference_context']['dt_s'] = '1/240'
    for k in ('R00', 'R01', 'R10'):
        r['intervals'][k] = [0, 1]
    assert all(invariants.extra_checks('R01', 2, r, record, cell).values())
    bad = json.loads(json.dumps(r)); bad['intervals']['R01'] = [-2, -1]
    assert not invariants.extra_checks('R01', 2, bad, record, cell)['regrets_not_below_zero']
    bad = json.loads(json.dumps(r)); bad['intervals']['G_S_M1'] = [5, 5]
    assert not invariants.extra_checks('R01', 2, bad, record, cell)['GS_plus_Gamma_meets_GS_M1']
    assert not invariants.extra_checks('R02', 2, r, record, cell)['cell_id_match']
    assert not invariants.extra_checks('R01', 1, r, record, cell)['dt_match']


def test_diagnostic_position_saturation_and_level_shape_on_toy():
    p0, p1 = F('1.08'), F('.43')
    assert invariants.position(F('.10'), F('.10'), p0, p1) == 'beyond_H1_side'
    assert invariants.contribution(F('.10'), F('.10'), p0, p1) == (F('.65'), F('.65'))
    assert invariants.contribution(F('.43'), F('.43'), p0, p1) == (F('.65'), F('.65'))
    assert invariants.position(F('.70'), F('.80'), p0, p1) == 'between_predictions'
    # H0 = H1 + 1 everywhere, truth = H1: pure level difference, identical shape.
    entries = [dict(contrast='Gamma', _p0=a + 1, _p1=a, _lo=a, _hi=a) for a in (F(1), F(3), F(2))]
    ls = invariants.group_level_shape(entries)['Gamma']
    assert ls['level_gap_abs_mean_difference'] == 1 and ls['D_contrast'] == 1
    assert ls['shape_only_MAE_H0'] == ls['shape_only_MAE_H1'] == 0


def test_psw_check_stops_on_any_mismatch(tmp_path, monkeypatch):
    records = {cid: {'p_1': [.3, .31], 'p_2': [.3, .31]} for cid in OPEN}
    monkeypatch.setattr(run, 'psw_interval', lambda cid, m: [.3, .31])
    assert len(run.psw_check(records, tmp_path)) == 20
    monkeypatch.setattr(run, 'psw_interval', lambda cid, m: [.3, .3100000001] if cid == 'R05' else [.3, .31])
    with pytest.raises(ArithmeticError, match='STOP before costs'):
        run.psw_check(records, tmp_path)
