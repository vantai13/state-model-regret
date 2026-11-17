"""Independent replay checks using hand-built arithmetic fixtures only."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from experiments.letter import trunc_n2_rescore as rescore


def fixture(root, delta=0., cost_delta=0.):
    hashes = {}
    for i in range(27):
        rid = f'R{i:02}'
        raw = dict(case={'id': rid}, levels={}, evaluations=[dict(
            age_label='seconds_1', N={'A': 40}, chains={},
            h=[dict(h='1', G_S=0., Cref=100.)])])
        two = copy.deepcopy(raw)
        two['evaluations'][0]['N']['A'] = 80
        two['evaluations'][0]['h'][0].update(G_S=delta, Cref=100.+cost_delta)
        pair = {}
        for folder, value, key in (('one', raw, 'baseline_sha256'), ('two', two, 'candidate_sha256')):
            path = root / folder / 'raw' / (rid + '.json')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value))
            pair[key] = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes[rid] = pair
    relative = abs((100.+cost_delta)-100.)/100.
    pct_good, rel_good = abs(delta) <= 1e-6, relative <= 1e-9
    group = lambda n, m, a, fs, good: dict(count=n, max_difference=m,
        max_absolute_difference=a, fields=fs, passed=good)
    result = dict(thresholds=rescore.THRESHOLDS, compared_regimes=27,
        comparison=dict(baseline='one', candidate='two', same_platform=True,
                        candidate_n_scale=2, input_sha256=hashes),
        groups=dict(
            percentage_pp=group(27, abs(delta), abs(delta), ['[].h[].G_S'], pct_good),
            relative=group(54, relative, abs((100.+cost_delta)-100.),
                           ['[].h[].Cref', '[].h[].h'], rel_good),
            discrete=group(54, 0., 0., ['[].age_label', '[].chains'], True)),
        violations=([{'group':'percentage_pp'}]*27 if not pct_good else [])
                   + ([{'group':'relative'}]*27 if not rel_good else []),
        status='PASS' if pct_good and rel_good else 'FAIL',
        missing_regimes=[], extra_regimes=[], missing_fields=[], extra_fields=[])
    path = root / 'comparison.json'
    path.write_text(json.dumps(result))
    return path


@pytest.mark.parametrize('delta,cost_delta,status', [(5e-7, 0., 'PASS'), (2e-6, 0., 'FAIL'), (0., 1e-5, 'FAIL')])
def test_independent_known_arithmetic_and_locked_verdicts(tmp_path, delta, cost_delta, status):
    path = fixture(tmp_path, delta, cost_delta)
    result = rescore.replay(tmp_path, path)
    assert result['matched'] and result['status'] == status
    assert result['groups']['percentage_pp']['count'] == 27


def test_independent_replay_detects_input_tampering(tmp_path):
    path = fixture(tmp_path)
    (tmp_path / 'two/raw/R00.json').write_text('{}')
    with pytest.raises(AssertionError):
        rescore.replay(tmp_path, path)


def test_serialized_parameters_are_exact_discrete_metadata():
    assert rescore.category((0, 'parameters', 0), '17/2') == 'discrete'
    assert rescore.category((0, 'h', 0, 'h'), '17/2') == 'relative'
