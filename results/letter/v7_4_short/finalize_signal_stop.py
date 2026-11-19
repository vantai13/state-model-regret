"""Doan Van Tai — freeze the CARD's automatic negative-signal stop.

This is preparation metadata, not a pilot run or a completed-pilot lock.
The frozen runner's success-only create_lock() is deliberately not called.
No simulator, cost gather, evaluation or reference calculation occurs here.
"""
import json
from pathlib import Path

from experiments.letter import v7_4_short as V


def main():
    out = V.OUT
    signal = V.C.read_json(out/'signal.json')
    if signal['signal_gate']['verdict'] != 'NOT_ENOUGH_SIGNAL':
        raise ValueError('automatic signal stop requires NOT_ENOUGH_SIGNAL')
    if V.C.read_json(out/'input_fingerprints.json') != V.input_fingerprint():
        raise ValueError('source/input drift since step 0')
    if any((out/p).exists() for p in ('pilot.json', 'predictions.json', 'lock.json', 'truth')):
        raise FileExistsError('stop finalization refuses existing final artifacts')
    planned = V.C.read_json(out/'pilot_selection_proposal.json')
    selection = dict(planned, status='NOT_RUN_SIGNAL_STOP',
        execution_note='Planned records only. CARD stop rule applies; no pilot outcomes computed.')
    V.C.write_json(out/'pilot/selection.json', selection)
    pilot = dict(owner='Doan Van Tai', stage='pilot', status='NOT_RUN_SIGNAL_STOP',
        decision='NOT_RUN_SIGNAL_STOP', seed=V.PILOT_SEED, records=[],
        planned_records=planned['records'], planned_N=V.N, planned_K=V.K,
        planned_R_dec=V.R_DEC, planned_R_eval=V.R_EVAL,
        CPU_s_records=0., CPU_s_command=None, projected_CPU_s=None, projected_CPU_hours=None,
        outcomes_computed=False, automatic_stop=True, author_override_received=False,
        reason='CARD: Nếu không đạt: dừng, ghi NOT_ENOUGH_SIGNAL, không chạy truth. Brief still lists a timing pilot; no pilot was run across this conflict.',
        selection_sha256=V.C.sha256(out/'pilot/selection.json'))
    V.C.write_json(out/'pilot.json', pilot)
    pred = V.predictions()
    pred.update(preparation_status='STOPPED_NOT_ENOUGH_SIGNAL', pilot_status=pilot['status'],
        pilot_outcomes_computed=False, planned_pilot_records=pilot['planned_records'],
        projected_truth_CPU_hours=None, truth_authorized=False,
        stop_note='CARD automatic stop, not a completed pilot. No author reply or overridden criterion is assumed.')
    pred['implementation_choices'].append(
        'Automatic negative-signal stop takes precedence over running the brief timing pilot; pilot fields above describe a plan only. No timing projection is claimed.')
    V.C.write_json(out/'predictions.json', pred)
    paths = V.preparation_paths()
    for p in paths.values():
        if not Path(p).is_file():
            raise FileNotFoundError(p)
    evidence = [out/name for name in ('diagnosis.json', 'diagnosis.md', 'diagnose_saved_signal.py',
        'signal_verification.json', 'verify_preparation.py', 'pilot_selection_proposal.json',
        'finalize_signal_stop.py')]
    lock = dict(owner='Doan Van Tai', schema='v7-4-short-lock-v1',
        preparation_status='STOPPED_NOT_ENOUGH_SIGNAL', pilot_status=pilot['status'],
        sha256={name: V.C.sha256(p) for name, p in sorted(paths.items())},
        evidence_sha256={V.rel(p): V.C.sha256(p) for p in evidence},
        truth_prerequisites=['lock byte-identical to HEAD commit', 'all file hashes match',
                             'SIGNAL_OK', 'one-shot output absent'],
        note='STOP lock only: 87 decisions records, zero pilot records, zero truth. Committing this lock does not authorize truth; SIGNAL_OK is false.')
    V.C.write_json(out/'lock.json', lock)
    print(json.dumps(dict(status=lock['preparation_status'], pilot_status=pilot['status'],
        core_files_hashed=len(lock['sha256']), evidence_files_hashed=len(lock['evidence_sha256']),
        lock_sha256=V.C.sha256(out/'lock.json'), truth_run=False), sort_keys=True))


if __name__ == '__main__':
    main()
