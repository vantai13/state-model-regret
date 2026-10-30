"""Independent rescore of the complete registered numerical schedule, no engine."""
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np

from experiments.R3R_07_confirmation.common import digest, git, write_once
from experiments.R3R_08_population_numerics.checks import check, planning_seconds
from experiments.R3R_05_contract.freeze import verify_lock
from experiments.R3R_06_cards.verify_cards import verify
from experiments.R3R_09_numerics_resume.run import validate_config, verify_snapshot


def main():
    prereg = Path('experiments/R3R_09_numerics_resume/prereg.json')
    cfg = json.loads(prereg.read_text())
    folder = Path('results/lessons/l3r_7/full_numerics/recovery04')
    raw = Path(cfg['output'])
    summary = json.loads((raw / 'summary.json').read_text())
    attempt = json.loads((raw / 'attempt.json').read_text())
    assert attempt['prereg_sha256'] == digest(prereg)
    assert git('show', f"{attempt['source_commit']}:{prereg}") == prereg.read_bytes()
    for path, wanted in cfg['source_sha256'].items():
        assert hashlib.sha256(git('show', f"{attempt['source_commit']}:{path}")).hexdigest() == wanted, path
        assert digest(path) == wanted, path
    parent = json.loads(Path(cfg['resume']['parent_prereg']).read_text())
    validate_config(cfg, parent)
    verify_snapshot(json.loads(Path(cfg['resume']['snapshot_manifest']).read_text()), cfg['resume']['parent_output'])
    export = json.loads((folder / 'export_verification.json').read_text())
    assert export['status'] == 'PASS'
    for path, wanted in export['source_sha256'].items():
        assert digest(path) == wanted, path
    suites = list(ET.parse('results/lessons/l3r_7/full_numerics/attempt04/full_suite.xml').getroot().iter('testsuite'))
    assert sum(int(s.get('tests', 0)) for s in suites) == cfg['full_tests_required']
    assert not any(int(s.get(k, 0)) for s in suites for k in ('failures', 'errors', 'skipped'))
    contract = verify_lock()
    card = verify()
    assert card['status'] == 'PASS'
    levels = {}
    rows, gains, seen = [], [], set()
    for receipt in summary['receipts']:
        key = receipt['stage'] + ':' + receipt['id']
        assert key not in seen
        seen.add(key)
        dest = Path(summary['receipt_origins'][key])
        assert dest.is_relative_to(raw) or dest.is_relative_to(Path(cfg['resume']['parent_output']))
        assert json.loads((dest / 'receipt.json').read_text()) == receipt
        resource = json.loads((dest / 'resource.json').read_text())
        assert resource == receipt['resources']
        data = json.loads((dest / 'result.json').read_text())
        if receipt['status'] == 'COMPLETED':
            assert resource['exit_code'] == 0 and receipt['payload_valid']
            assert data['status'] == 'COMPLETED' and data['CF_generated'] == 0
            if receipt['stage'] != 'marginal':
                assert data['kind'] == 'global_calibration'
                assert set(data['levels']) == {f'{k}:{r}' for k, r in cfg['stage_levels'][receipt['stage']]}
                levels.setdefault(receipt['id'], {}).update(data['levels'])
                for level, row in data['levels'].items():
                    assert json.loads((dest / ('level_' + level.replace(':', '_') + '.json')).read_text()) == row
                    entry = dict(id=receipt['id'], stage=receipt['stage'], K=row['K'], ref=row['ref'],
                        Cref_packet_seconds=row['Cref'], arithmetic_pass=row['arithmetic_pass'],
                        validity_errors=';'.join(row['validity_errors']))
                    for cell, value in row['losses'].items():
                        entry['L' + cell + '_packet_seconds'] = value
                    for metric in ('G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1'):
                        entry[metric + '_percent_Cref'] = 100 * float(F(row[metric]) / F(row['Cref']))
                    entry['maximum_arithmetic_error_percent_Cref'] = 100 * max(float(x) for x in row['normalized_error'].values())
                    gains.append(entry)
            elif data['kind'] == 'legacy_anchor':
                assert data['comparison']['status'] == 'PASS'
        rows.append(dict(id=receipt['id'], stage=receipt['stage'], status=receipt['status'],
            reused=not dest.is_relative_to(raw), cpu_seconds=resource['cpu_seconds'],
            wall_seconds=resource['wall_seconds'], peak_rss_MiB=resource['sampled_peak_rss_bytes']/1024**2,
            origin=str(dest)))
    assert levels == json.loads((raw / 'levels.json').read_text())
    coverage = []
    for stage, K, ref in cfg['candidates']:
        checks = {j['id']: check(levels.get(j['id'], {}), K, ref) for j in cfg['cases']}
        coverage.append(dict(stage=stage, K=K, ref=ref, checks=checks,
            ready=sum(x['ready'] for x in checks.values()), total=len(checks),
            scope='fixed calibration coverage, not estimated population prevalence'))
    first = next(([c['K'], c['ref']] for c in coverage if c['ready'] == c['total']), None)
    assert first == summary['selected_levels']
    timing = None
    if first:
        recomputed = {j['id']: planning_seconds(levels[j['id']], *first) for j in cfg['cases']}
        assert {r['id']: {k: v for k, v in r.items() if k != 'id'} for r in summary['timing']} == recomputed
        groups = {name: [recomputed[j['id']]['cold_bundle_planning_seconds'] for j in cfg['cases']
            if (j.get('role') == 'rational_rate_timing_accuracy') == (name == 'rational_rates')]
            for name in ('rational_rates', 'corners_audit_controls')}
        timing = {name: dict(n=len(values), p95_cpu_seconds=float(np.quantile(values, .95, method='higher')))
            for name, values in groups.items()}
        timing['planning_p95_cpu_seconds'] = max(v['p95_cpu_seconds'] for v in timing.values())
    assert summary['CF_generated'] == 0 and summary['n'] is summary['confirmation_root'] is None
    out = folder / 'report'
    out.mkdir(exist_ok=False)
    for name, data in [('metrics', rows), ('gains_calibration_only', gains)]:
        if data:
            with (out / (name + '.csv')).open('x', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(data[0]))
                writer.writeheader()
                writer.writerows(data)
    result = dict(owner='Doan Van Tai', status='PASS_INDEPENDENT_RECORD_AND_SELECTION_AUDIT',
        numerical_status=summary['status'], selected_levels=first,
        registered_cases=len(cfg['cases']), source_commit=attempt['source_commit'], source_files=len(cfg['source_sha256']),
        exported_files=export['files'], reused=sum(r['reused'] for r in rows),
        new_receipts=sum(not r['reused'] for r in rows), unresolved=sum(r['status'] != 'COMPLETED' for r in rows),
        recorded_receipt_cpu_seconds=sum(r['cpu_seconds'] for r in rows),
        new_recorded_receipt_cpu_seconds=sum(r['cpu_seconds'] for r in rows if not r['reused']),
        interrupted_parent_cpu_seconds='UNKNOWN; 3605 seconds reserved for planning, not measured',
        peak_sampled_RSS_MiB=max(r['peak_rss_MiB'] for r in rows),
        full_tests=cfg['full_tests_required'], contract_files=len(contract['source_sha256']), card_files=card['files'],
        candidates=[{k: c[k] for k in ('stage', 'K', 'ref', 'ready', 'total')} for c in coverage],
        timing=timing, CF_generated=0, n=None, confirmation_root=None, Phase4='HOLD')
    write_once(out / 'verification.json', result)
    write_once(out / 'coverage.json', coverage)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
