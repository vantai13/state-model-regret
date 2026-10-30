"""Read-only verification of L4.3 receipts; never calls a physical engine."""
import argparse
import csv
import json
from pathlib import Path
import struct

from .common import (ROOT, HERE, OUT, LEVELS, sha, git, require, write_once,
                     validate_row, compare, canonical, forbid_cf, cf_keys)
from .resource_resume import NEWOUT, verify_extension


def load(path):
    return json.loads((ROOT / path).read_text())


def verify():
    verify_extension()  # Includes initial prereg, transitive source and failure hashes.
    sealed = load(HERE / 'sealed_scope.json')
    require(git('show', 'HEAD:' + str(HERE / 'sealed_scope.json')) ==
            (ROOT / HERE / 'sealed_scope.json').read_bytes(), 'uncommitted sealed scope')
    for path, digest in sealed['source_sha256'].items():
        require(sha(ROOT / path) == digest, 'sealed source changed: ' + path)
    keys = {tuple(r['coordinates']) for r in sealed['sealed']}
    plan = load(HERE / 'cases.json')
    cases = {c['id']: c for c in plan['cases']}
    require(len(cases) == 666 and len(plan['aliases']) == 684, 'scope ledger changed')

    part_a = load(NEWOUT / 'partA/summary.json')
    specs = load(HERE / 'bit_specs.json')['rows']
    rows = {r['id']: r for r in part_a['results']}
    fields = 0
    require(part_a['status'] == 'PASS' and len(rows) == 14, 'PartA incomplete')
    for path, digest in part_a['row_receipts_sha256'].items():
        require(sha(ROOT / path) == digest, 'PartA receipt changed: ' + path)
    for spec in specs:
        row = rows[spec['id']]
        require(row['status'] == 'PASS' and row['expected'] == spec['expected'], 'PartA identity')
        for metric, expected in spec['expected'].items():
            require(struct.pack('!d', float(row['actual'][metric])) ==
                    struct.pack('!d', float(expected)), 'PartA bit mismatch')
            fields += 1
    require(fields == 126, 'PartA field count')
    require(len(part_a['recount']) == 10 and all(part_a['recount'].values()), 'recount failed')

    forbidden = cf_keys()
    benchmark = load(NEWOUT / 'benchmark_summary.json')
    require(benchmark['status'] == 'HOLD' and benchmark['completed'] == 3 and
            benchmark['planned'] == 4 and benchmark['stopped_without_scheduling_more'], 'stop rule mismatch')
    observed = []
    failed_r1 = []
    count = 0
    for saved in benchmark['results']:
        cid = saved['native_id']
        case = cases[cid]
        require(canonical(case['parameters']) == tuple(case['key']), 'canonical case key')
        require(tuple(case['key']) not in keys, 'sealed physical coordinate was run')
        forbid_cf(case['parameters'], forbidden)
        folder = NEWOUT / 'native' / cid
        native = {}
        for level in LEVELS:
            row = load(folder / f'level_{level[0]}_{level[1]}.json')
            require(row['audit_prereg_sha256'] == sha(ROOT / HERE / 'prereg.json'), 'stale native receipt')
            validate_row(row, case, level)
            native[level] = row
            count += 1
        aliases = [a for a in plan['aliases'] if a['native_id'] == cid]
        recalculated = [compare(a, case, native) for a in aliases]
        stored = load(folder / 'comparison.json')
        require(stored == saved and stored['aliases'] == recalculated, 'comparison changed')
        for alias in recalculated:
            for axis, result in zip(('K', 'dt'), alias['r1']):
                if not result['ready']:
                    failed_r1.append(dict(id=alias['id'], axis=axis, **result))
        observed.append(cid)
    require(set(observed) == {'P43_0379', 'P43_0114', 'P43_0000'} and count == 9, 'native scope changed')
    require(len(list((ROOT / NEWOUT / 'native').glob('*/level_*.json'))) == 9, 'unexpected extra native levels')
    require(len(failed_r1) == 1 and failed_r1[0]['id'] == 'XM2X000' and
            failed_r1[0]['axis'] == 'dt', 'R1 diagnosis changed')
    require(not (ROOT / NEWOUT / 'budget.json').exists() and
            not (ROOT / NEWOUT / 'full_summary.json').exists(), 'full run after HOLD')

    manifest = load(OUT / 'report_data/manifest.json')
    require(sha(ROOT / HERE / 'report_final.py') == manifest['script_sha256'], 'report script changed')
    for name, digest in manifest['outputs_sha256'].items():
        require(sha(ROOT / OUT / 'report_data' / name) == digest, 'report output changed: ' + name)
    with (ROOT / OUT / 'report_data/audit_points.csv').open(newline='') as stream:
        points = list(csv.DictReader(stream))
    bad = next(p for p in points if p['id'] == 'XM2X000')
    require(bad['native_class_for_use'] == 'UNRESOLVED_VALIDITY', 'R1 failure has usable class')
    require(all(p['eligible_for_L45'] == 'False' for p in points), 'L4.5 used HOLD output')
    ledger = load(OUT / 'execution_ledger/summary.json')
    require(ledger['distinct_status_counts'] == dict(PASS=2, HOLD=1, SEALED_BLOCKED=1,
            NOT_RUN_AUDIT_HOLD=662), 'case status ledger')
    require(ledger['alias_status_counts'] == dict(PASS=2, HOLD=1, SEALED_BLOCKED=1,
            NOT_RUN_AUDIT_HOLD=680), 'alias status ledger')
    for name, expected in [('cases.csv', 666), ('aliases.csv', 684)]:
        with (ROOT / OUT / 'execution_ledger' / name).open(newline='') as stream:
            require(len(list(csv.DictReader(stream))) == expected, 'ledger missing rows')

    cache = load(OUT / 'cache_manifest.json')
    total_bytes = 0
    for name, receipt in cache['files'].items():
        path = ROOT / cache['cache_root'] / name
        require(sha(path) == receipt['sha256'] and path.stat().st_size == receipt['bytes'], 'cache changed')
        total_bytes += path.stat().st_size
    require(len(cache['files']) == 48 and total_bytes == 31051632, 'cache count/size')
    log = (ROOT / OUT / 'full_tests_after_sealed_guard.log').read_text()
    require('779 passed in 100.17s' in log, 'full test receipt not found')
    artifact_path = ROOT / OUT / 'artifact_manifest.json'
    artifact_count = None
    if artifact_path.exists():
        artifact = json.loads(artifact_path.read_text())
        for path, receipt in artifact['files'].items():
            require(sha(ROOT / path) == receipt['sha256'], 'artifact changed: ' + path)
        artifact_count = len(artifact['files'])
    return dict(responsible='Doan Van Tai', verification_status='PASS', audit_status='HOLD',
                scope='read-only receipt/hash/bit/identity/R1 checks; no physical calls',
                prereg_and_amendment_hashes='PASS', sealed_guard_hashes='PASS',
                preserved_original_failure='PASS', partA_rows=14, partA_exact_fields=fields,
                pilot_recount='PASS', native_cases=observed, native_level_rows=count,
                raw_arithmetic_validity_CF_guards='9/9 PASS', failed_R1=failed_r1,
                sealed_or_CF_native_cases=0, full_run='NOT_RUN', MC='NOT_RUN',
                latest_full_tests=dict(passed=779, seconds=100.17),
                cache_files=48, cache_bytes=total_bytes, report_hashes='PASS',
                ledger='666 cases / 684 aliases preserved',
                artifact_manifest_files_checked=artifact_count)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    args = parser.parse_args()
    result = verify()
    if args.output:
        write_once(ROOT / args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
