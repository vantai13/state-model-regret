import copy
import json
from pathlib import Path

import pytest

from experiments.R3R_09_numerics_resume.run import (
    budget_fits, load_completed, validate_config, verify_snapshot,
)
from experiments.R3R_07_confirmation.common import digest


def test_changed_threshold_cannot_enter_an_infrastructure_resume():
    parent = dict(source_sha256={'engine.py': 'abc'}, candidates=[['base', 80, 2]],
                  limits={'job_cpu_seconds': 10}, arithmetic_fraction_max='1/10')
    child = copy.deepcopy(parent)
    child['resume'] = {'interrupted_cpu_upper_seconds': 15}
    validate_config(child, parent)
    child['arithmetic_fraction_max'] = '1/5'
    with pytest.raises(ValueError, match='setting changed'):
        validate_config(child, parent)


def test_changed_estimator_source_cannot_reuse_parent_results():
    parent = dict(source_sha256={'engine.py': 'abc'}, limits={'job_cpu_seconds': 10})
    child = copy.deepcopy(parent)
    child.update(resume={'interrupted_cpu_upper_seconds': 15}, source_sha256={'engine.py': 'different'})
    with pytest.raises(ValueError, match='source changed'):
        validate_config(child, parent)


def test_parent_snapshot_rejects_corrupted_bytes(tmp_path):
    path = tmp_path / 'result.json'
    path.write_text('{}')
    manifest = {'source_sha256': {str(path): digest(path)}}
    verify_snapshot(manifest, tmp_path)
    path.write_text('{"tampered": true}')
    with pytest.raises(ValueError, match='bytes changed'):
        verify_snapshot(manifest, tmp_path)


def test_parent_snapshot_rejects_incomplete_manifest(tmp_path):
    (tmp_path / 'unlisted.json').write_text('{}')
    with pytest.raises(ValueError, match='incomplete'):
        verify_snapshot({'source_sha256': {}}, tmp_path)


def test_progress_active_job_without_receipt_is_not_reused(tmp_path):
    (tmp_path / 'progress.json').write_text(json.dumps({'active': ['MISSING'], 'completed': 999}))
    dest = tmp_path / 'base' / 'MISSING'
    dest.mkdir(parents=True)
    (dest / 'level_80_2.json').write_text('{}')
    rows, origins, bundles = load_completed({'stage_levels': {'base': [[80, 2]]}}, tmp_path)
    assert rows == [] and origins == {} and bundles == {}


def test_empty_population_payload_cannot_be_reused(tmp_path):
    dest = tmp_path / 'base' / 'A'
    dest.mkdir(parents=True)
    resources = {'exit_code': 0, 'cpu_seconds': 1}
    receipt = dict(id='A', stage='base', status='COMPLETED', payload_valid=True, resources=resources)
    result = dict(id='A', stage='base', status='COMPLETED', kind='global_calibration', levels={}, CF_generated=0)
    for name, data in [('receipt', receipt), ('resource', resources), ('result', result)]:
        (dest / (name + '.json')).write_text(json.dumps(data))
    cfg = dict(stage_levels={'base': [[80, 2]]}, cases=[dict(id='A', kind='global_calibration')])
    with pytest.raises(ValueError, match='levels are incomplete'):
        load_completed(cfg, tmp_path)


def test_interrupted_cpu_is_reserved_in_total_budget():
    cfg = dict(resume={'interrupted_cpu_upper_seconds': 15},
               limits={'job_cpu_seconds': 10, 'total_cpu_seconds': 100})
    assert budget_fits(cfg, [{'resources': {'cpu_seconds': 65}}], 0)
    assert not budget_fits(cfg, [{'resources': {'cpu_seconds': 66}}], 0)


def test_live_workers_also_reserve_their_full_ceiling():
    cfg = dict(resume={'interrupted_cpu_upper_seconds': 15},
               limits={'job_cpu_seconds': 10, 'total_cpu_seconds': 100})
    assert budget_fits(cfg, [], 3)
    assert not budget_fits(cfg, [], 4)
