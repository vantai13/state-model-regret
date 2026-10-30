"""Prepare concrete validation jobs only after the independent global audit passes."""
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

from experiments.R3R_07_confirmation.common import digest, write_once


def require_ready(audit):
    if (audit.get('status') != 'PASS_RECORD_INTEGRITY_NUMERICS_READY_FOR_CLOSURE'
            or not audit.get('selected_levels') or audit.get('unresolved') != 0
            or audit.get('base_global_bundles_complete') != 114
            or audit.get('legacy_pass') != 3 or audit.get('marginals_pass') != 6):
        raise ValueError('complete verified numerical selection required before validation')
    return audit['selected_levels']


def cpu_limit(measured):
    if not math.isfinite(measured) or measured <= 0 or measured >= 3600:
        raise ValueError('positive measured timing required')
    return min(3600, max(60, math.ceil(2*measured+30)))


def main():
    root = Path('results/lessons/l3r_7/full_numerics/native05')
    audit_path = root/'report/verification.json'
    audit = json.loads(audit_path.read_text())
    K, ref = require_ready(audit)
    parent_path = Path('experiments/R3R_11_native_population/prereg.json')
    parent = json.loads(parent_path.read_text())
    design_path = root/'fixed_validation_design_v2.json'
    design = json.loads(design_path.read_text())
    level_path = Path(parent['output'])/'levels.json'
    levels = json.loads(level_path.read_text())
    cases = {j['id']:j for j in parent['cases']}
    for job in parent['legacy_jobs']:
        if job['id'] not in cases:
            cases[job['id']] = dict(id=job['id'], parameters=job['spec'][1:6]+job['spec'][8:9])
    requested = []
    for rid in ('ZERO_MV', 'ZERO_SH'):
        requested.append(('zero', rid, K, ref))
    for rid in ('X2065', 'X1008', 'X1009'):
        requested.append(('anchor', rid, K, ref))
    for case in design['identical_model_timing_cases']:
        requested.append(('identical', case['id'], K, ref))
    for values in design['dry_run_B_discovery_cases'].values():
        for case in values:
            for k, r in ((K,ref),(K//2,ref),(K,ref//2)):
                requested.append(('discovery', case['id'], k, r))
    known = [float(row['cpu_seconds']) for rows in levels.values() for row in rows.values()]
    jobs = []
    for role, rid, k, r in requested:
        previous = levels.get(rid, {}).get(f'{k}:{r}')
        measured = float(previous['cpu_seconds']) if previous else max(known)
        if previous is None and role == 'anchor':
            # The additional anchor has small integer-lattice parameters; use
            # the measured worst registered call, rather than inventing timing.
            measured = max(known)
        limit = cpu_limit(measured)
        jobs.append(dict(id=f'{role}_{rid}_{k}_{r}', role=role, source_id=rid,
            parameters=cases[rid]['parameters'], K=k, ref=r, measured_reference_cpu_seconds=measured,
            cpu_seconds=limit, wall_seconds=min(4800, max(180, 2*limit+120))))
    cfg = copy.deepcopy(parent)
    cfg.update(id='R3R_NUMERICS_SELECTED_VALIDATION', decision='DL-093',
        declared_at=datetime.now(timezone.utc).isoformat(), output='results/R3R_selected_validation/20261030_01',
        calibration_audit=dict(path=str(audit_path),sha256=digest(audit_path)),
        calibration_levels=dict(path=str(level_path),sha256=digest(level_path)),
        selected_levels=[K,ref], validation_jobs=jobs,
        carried_cpu_reserve_seconds=parent['carried_cpu_reserve_seconds']+audit['cpu_seconds'])
    # Exact count is measured from pytest collection before deployment.
    collected = subprocess.check_output([sys.executable,'-m','pytest','--collect-only','-q'],text=True)
    cfg['full_tests_required'] = int(re.search(r'(\d+) tests collected',collected).group(1))
    sources = [*Path('experiments/R3R_12_validation').glob('*.py'),
               Path('tests/test_selected_validation_guards.py'), parent_path,
               audit_path, level_path, design_path]
    for path in sources:
        cfg['source_sha256'][str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    write_once('experiments/R3R_12_validation/prereg.json', cfg)
    print(json.dumps(dict(jobs=len(jobs),selected_levels=[K,ref],
        carried_cpu_reserve_seconds=cfg['carried_cpu_reserve_seconds'],CF_generated=0),indent=2))


if __name__ == '__main__':
    main()
