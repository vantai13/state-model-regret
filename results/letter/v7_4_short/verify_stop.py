"""Doan Van Tai — independent stopped-artifact audit and read-only truth guards."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from unittest.mock import patch

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    lock = read(OUT/'lock.json')
    data = Path(os.environ.get('SMR_SNDLIB', '~/papers/data/sndlib')).expanduser()
    external = {'sndlib:archive': data/'directed-geant-uhlig-15min-over-4months-ALL-native.tgz',
                'sndlib:topology': data/'sndlib-networks-native/geant.txt',
                'sndlib:train_cache': data/'v7_3_train.npz'}
    for field in ('sha256', 'evidence_sha256'):
        for name, digest in lock[field].items():
            assert sha(external[name] if name in external else ROOT/name) == digest, name
    assert lock['preparation_status'] == 'STOPPED_NOT_ENOUGH_SIGNAL'
    pilot, pred, signal = (read(OUT/name) for name in ('pilot.json', 'predictions.json', 'signal.json'))
    assert pilot['status'] == pred['pilot_status'] == 'NOT_RUN_SIGNAL_STOP'
    assert pilot['records'] == [] and pilot['CPU_s_records'] == 0.
    assert pilot['projected_CPU_hours'] is None and pred['projected_truth_CPU_hours'] is None
    assert not pilot['outcomes_computed'] and not pred['truth_authorized'] and not pred['truth_run']
    assert pred['H_P1_verdict'] == 'NOT_RUN'
    assert signal['signal_gate']['verdict'] == 'NOT_ENOUGH_SIGNAL'
    assert signal['signal_gate']['primary_disagreements'] == 0
    card = (OUT/'CARD_V7_4.md').read_text()
    assert pred['H_P1_reading_rule_verbatim'] == card[card.index('**H-P1 (chính'):card.index('## Dự báo')].strip()
    assert pred['expected_records_all'] == 87 and pred['expected_records_primary'] == 58
    assert pred['expected_side_instances_all'] == 55680 and pred['expected_side_instances_primary'] == 37120
    assert len(list((OUT/'decision_records').glob('*.npz'))) == 87
    assert not (OUT/'pilot/records').exists() and not (OUT/'truth').exists()
    assert read(OUT/'signal_verification.json')['status'] == 'PASS'
    subprocess.run(['git', 'diff', '--exit-code'], cwd=ROOT, check=True, capture_output=True)
    # Test only the read-only preflight guard, never the truth runner.
    from experiments.letter import v7_4_short as V
    try:
        V.verify_committed_lock()
    except ValueError as error:
        assert 'not been committed' in str(error)
        actual_guard = str(error)
    else:
        raise AssertionError('uncommitted lock was accepted')
    with patch.object(V.subprocess, 'check_output', return_value=(OUT/'lock.json').read_bytes()):
        try:
            V.verify_committed_lock()
        except ValueError as error:
            assert 'NOT_ENOUGH_SIGNAL' in str(error)
            simulated_commit_guard = str(error)
        else:
            raise AssertionError('negative signal was accepted')
    result = dict(owner='Doan Van Tai', status='PASS',
        core_hashes_checked=len(lock['sha256']), evidence_hashes_checked=len(lock['evidence_sha256']),
        independent_signal_audit='PASS 87 records / 3480 count rows',
        prediction_H_P1_verbatim=True, stopped_pilot_metadata_valid=True,
        actual_uncommitted_guard=actual_guard, simulated_commit_negative_signal_guard=simulated_commit_guard,
        no_simulation_or_gather_calls=True, pilot_rollouts=0, truth_rollouts=0,
        tracked_files_unchanged=True, lock_sha256=sha(OUT/'lock.json'), audit_source_sha256=sha(__file__))
    with (OUT/'verification.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
