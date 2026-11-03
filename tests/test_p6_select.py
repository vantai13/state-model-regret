"""Doan Van Tai — fixed selection and readiness vetoes with synthetic numerics."""
from contextlib import nullcontext
import csv
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from experiments.P6_band import select_dii as S

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ['B004C07', 'B005C06', 'B010C02', 'B013C07', 'B014C06', 'B015C06', 'B019C12',
            'B020C11', 'B027C12', 'B034C05', 'B039C14', 'B040C12', 'B050C19']


def row(rid, z, c, group='Dii', all='True', **kwargs):
    result = dict(id=rid, base_id=rid[:4], group=group, all=all, z_H1=str(z), c=c,
                  H1='-', H0='+', truth_switch='False', F_new='.3', F_old='.2',
                  **{f'W{i}': 'True' for i in range(1, 9)})
    result.update(kwargs)
    return result


def test_real_scan_gives_declared_13_points():
    chosen = S.select_dii(S.load_rows(ROOT))
    assert [r['id'] for r in chosen] == EXPECTED
    S.check_rows(chosen)
    twins, control = S.twins_and_control(S.load_rows(ROOT), chosen)
    assert [r['id'] for r in twins] == [r[:4]+'C00' for r in EXPECTED]
    assert control['id'] == 'B001C00'


def test_peak_abs_z_and_exact_cost_tie():
    rows = [row('B001C01', -1.2, '1/8'), row('B001C02', -2., '1/4'),
            row('B001C03', -2., '1/2'), row('B001C04', -1.5, '1')]
    assert [r['id'] for r in S.select_dii(rows)] == ['B001C02']


def test_ineligible_rows_are_ignored():
    rows = [row('B001C01', -5, '1/8', all='False'), row('B002C01', -5, '1/8', group='Di'),
            row('B003C01', -1.1, '1/8')]
    assert [r['id'] for r in S.select_dii(rows)] == ['B003C01']


def test_inconsistent_cdf_or_flags_rejected():
    for change in ({'F_new': '.1'}, {'W8': 'False'}, {'z_H1': 'nan'}):
        with pytest.raises(RuntimeError, match='DII_ROW_INCONSISTENT'):
            S.check_rows([row('B001C01', -1.5, '1/8', **change)])


def test_twin_must_be_agreed_plus_and_unexposed():
    chosen = [row('B001C03', -2, '1/4')]
    for change in ({'H0': '-'}, {'W6': 'False'}):
        bad = row('B001C00', 3, '0', group='A', H1='+', H0='+')
        bad.update(change)
        with pytest.raises(RuntimeError, match='TWIN_NOT_CLEAN'):
            S.twins_and_control([bad], chosen)


def checks(n, *, twin=True, control=True):
    rows = [dict(role='D', base_id=f'B{i:03d}', K_stable=True) for i in range(n)]
    rows += [dict(role='twin', base_id=f'B{i:03d}', K_stable=twin) for i in range(n)]
    rows += [dict(role='A-', base_id='B999', K_stable=control)]
    identities = {r['base_id']: dict(passed=True, drift=0., bound=1e-4) for r in rows}
    return rows, identities


@pytest.mark.parametrize('n,twin,control,expected', [
    (10, True, True, 'PASS'), (9, True, True, 'HOLD_K_STABILITY'),
    (13, False, True, 'HOLD_K_STABILITY'), (13, True, False, 'HOLD_K_STABILITY')])
def test_status_thresholds_and_pair_veto(n, twin, control, expected):
    rows, identities = checks(n, twin=twin, control=control)
    assert S.window_status(rows, identities) == expected


def test_missing_control_or_duplicate_bases_cannot_pass():
    rows, identities = checks(13)
    assert S.window_status([r for r in rows if r['role'] != 'A-'], identities) == 'HOLD_K_STABILITY'
    rows[0]['base_id'] = rows[1]['base_id']
    assert S.window_status(rows, identities) == 'HOLD_K_STABILITY'


def test_missing_or_invalid_identity_blocks():
    rows, identities = checks(13)
    for broken in ({}, {k: v for k, v in identities.items() if k != 'B000'},
                   dict(identities, B000=dict(passed=False, drift=.1, bound=1e-4)),
                   dict(identities, B000=dict(passed=True, drift=.1, bound=1e-4))):
        assert S.window_status(rows, broken) == 'BLOCKED_EXACT_IDENTITY'


@pytest.mark.parametrize('pred,need_z,expected', [
    (dict(status='PREDICTED', H1='-', z_H1=-1), True, True),
    (dict(status='PREDICTED', H1='-', z_H1=-.99), True, False),
    (dict(status='PREDICTED', H1='+', z_H1=2), True, False),
    (dict(status='PREDICTED', H1='-', z_H1=float('-inf')), True, False),
    (dict(status='PREDICTED', H1='-', z_H1=float('nan')), True, False),
    (dict(status='UNRESOLVED'), True, False),
    (dict(status='PREDICTED', H1='-', z_H1=-.1), False, True)])
def test_k_stability_sign_margin_and_nonfinite(pred, need_z, expected):
    assert S.k_stable(dict(H1='-', z_H1='-1.2'), pred, need_z=need_z) == expected


def fake_deps(*, failed_base=None, weak_base=None):
    seen = []

    def builder(*args, ref, K):
        seen.append((args[:5], K))
        return args[:5]

    chosen = S.select_dii(S.load_rows(ROOT))
    params = {r['base_id']: tuple(S.F(r[k]) for k in ('lambdaA', 'lambdaB', 'kappa', 'u', 'h'))
              for r in chosen}

    def identity(*args, ref):
        return dict(passed=args[:5] != params.get(failed_base), drift=0., bound=1e-4)

    def predict(sd, c):
        sign = '+' if c == 0 and sd[1] > sd[0] else '-'
        magnitude = .9 if c > 0 and sd == params.get(weak_base) else 1.5
        return dict(status='PREDICTED', H1=sign, z_H1=magnitude if sign == '+' else -magnitude)

    return SimpleNamespace(cache=None, builder=builder, identity=identity, predict=predict,
                           guard=nullcontext, seen=seen)


def test_fake_run_only_fixed_bases_and_no_replacement():
    deps = fake_deps(weak_base='B013')
    result = S.run(ROOT, deps)
    assert result['status'] == 'PASS' and len(result['usable_D']) == 12
    assert result['chosen'] == EXPECTED and result['control'] == 'B001C00'
    assert 'B013C07' not in result['usable_D'] and len(result['checks']) == 27
    assert len(deps.seen) == 14 and all(K == 640 for base, K in deps.seen)


def test_failed_identity_stops_before_its_builder():
    deps = fake_deps(failed_base='B004')
    result = S.run(ROOT, deps)
    assert result['status'] == 'BLOCKED_EXACT_IDENTITY' and result['blocked_base'] == 'B004'
    assert len(deps.seen) == 1  # B001 only, before the first D base.


def test_attempt_reserved_and_partial_rows_survive_error(tmp_path):
    out = tmp_path/'attempt'
    deps = fake_deps()
    original = deps.builder

    def broken(*args, **kwargs):
        if deps.seen:
            raise RuntimeError('SYNTHETIC_FAILURE')
        return original(*args, **kwargs)

    deps.builder = broken
    result = S.execute(ROOT, out, lambda root: deps, dict(prior_CPU_upper_seconds=1200))
    assert result['status'] == 'EXECUTION_FAILURE' and len(result['checks']) == 1
    assert json.loads((out/'summary.json').read_text())['error'] == 'RuntimeError: SYNTHETIC_FAILURE'
    assert len(list(csv.DictReader((out/'candidates.csv').open()))) == 1
    with pytest.raises(FileExistsError):
        S.execute(ROOT, out, lambda root: pytest.fail('attempt rerun'), dict(prior_CPU_upper_seconds=1200))


def test_real_guard_blocks_both_truth_entrypoints(tmp_path, monkeypatch):
    from experiments.P6_band import predictor as P
    monkeypatch.setattr(P, 'StationaryCache', lambda *args: None)
    deps = S.real_deps(tmp_path)
    original_get, original_idle = P.profiles.get, P.P.idle
    with deps.guard():
        for fn in (P.profiles.get, P.P.idle):
            with pytest.raises(RuntimeError, match='FINITE_H_TRUTH_FORBIDDEN'):
                fn()
    assert P.profiles.get is original_get and P.P.idle is original_idle


def test_changed_source_csv_rejected(tmp_path):
    path = tmp_path/S.SOURCE
    path.parent.mkdir(parents=True)
    path.write_text('synthetic changed input\n')
    with pytest.raises(RuntimeError, match='SOURCE_SCAN_CHANGED'):
        S.load_rows(tmp_path)


def test_nonfinite_predictions_are_retained_as_vetoes_in_strict_json(tmp_path):
    deps = fake_deps()
    original = deps.predict

    def nonfinite(sd, c):
        pred = original(sd, c)
        if c > 0:
            pred['z_H1'] = float('nan')
        return pred

    deps.predict = nonfinite
    result = S.execute(ROOT, tmp_path/'invalid', lambda root: deps, dict(prior_CPU_upper_seconds=1200))
    assert result['status'] == 'HOLD_K_STABILITY' and result['usable_D'] == []
    saved = json.loads((tmp_path/'invalid/summary.json').read_text())
    assert all(r['z_K640'] is None and not r['K_stable'] for r in saved['checks'] if r['role'] == 'D')


def test_legacy_certificate_guard_allows_selector_but_rejects_numeric_changes(monkeypatch):
    from experiments.P6_band import window as W
    original = W.V1.git
    changed = ['experiments/P6_band/window.py', 'experiments/P6_band/select_dii.py']

    def git(*args):
        return ('\n'.join(changed)+'\n').encode() if args[0] == 'diff' else original(*args)

    monkeypatch.setattr(W.V1, 'git', git)
    assert len(W.load_identity_samples()) == 7
    changed.append('src/smr/stationary.py')
    with pytest.raises(RuntimeError, match='IDENTITY_DEPENDENCY_CHANGED'):
        W.load_identity_samples()
