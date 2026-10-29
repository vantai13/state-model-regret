"""Doan Van Tai — saved-evidence integrity for L3R.3; no new plant outcomes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from experiments.A05_freeze.provenance import verify_frozen
from experiments.lessons.audit_l3_8 import check_links

OUT = ROOT / 'results/lessons/l3r_3'
PILOT = 'a7435e9a3cb0d1625479c942041ec6748444014a'


def read(path): return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def git(*args): return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def main():
    (OUT / 'verification.json').write_text(json.dumps({'status': 'RUNNING', 'responsible': 'Doan Van Tai'}) + '\n')
    s, completion = read(OUT / 'summary.json'), read(ROOT / 'notes/phases/L3R_3_completion.json')
    assert s['audit_verdict'] == completion['audit_verdict'] == 'HOLD'
    assert s['technical_evidence'] == 'PASS_WITH_LIMITATIONS'
    assert completion['Understanding'] == 'OPEN' and completion['phase4_execution'] == 'HOLD'
    assert s['engine_bug_requiring_pilot_v2'] == 'NOT_CONFIRMED_IN_AUDITED_SCOPE' and s['pilot_v2_rerun'] is False
    assert git('rev-parse', 'explore-v13-pilot^{}') == git('rev-parse', 'explore/v13-population') == PILOT
    assert subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor', PILOT, 'HEAD'], capture_output=True).returncode == 1
    for copy, source in [('pilot_population.py', 'experiments/explore_v13/population.py'), ('pilot_tests_original.py', 'tests/test_explore_v13.py')]:
        raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', PILOT + ':' + source])
        assert raw == (ROOT / 'experiments/R3R_02_audit' / copy).read_bytes()
    assert not git('diff', PILOT, '--', 'src/smr', 'experiments/A00_engine', 'experiments/V13_step1/regime.py')
    assert not git('diff', '0c0ce27', '--', 'notes/01_definitions_v1_2.md', 'notes/01_definitions_v1_3_draft.md',
                   'experiments/A05_freeze', 'results/A05_test', 'papers/data/catalog.json', 'papers/paper_comparison.xlsx')
    for before, after in [('6499d7f', '4dffbcc'), ('4c4908f', '5a26db7')]:
        assert subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor', before, after], capture_output=True).returncode == 0
    assert read(OUT / 'engine_run01/controller.json')['prereg_commit'] == '6499d7f'
    assert read(OUT / 'mc_run01/final_controller.json')['selection_commit'] == '4c4908f'
    t07_original = subprocess.check_output(['git', '-C', str(ROOT), 'show', '315d203:notes/theory/T07_population_estimand.md'])
    assert (ROOT / 'notes/theory/T07_population_estimand.md').read_bytes().startswith(t07_original)
    marker = '# PHASE 3R — Reformulation v1.3:'.encode()
    original = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'bf3915e:notes/phases/PHASE_3R.md'])
    current = (ROOT / 'notes/phases/PHASE_3R.md').read_bytes()
    assert original[original.index(marker):] == current[current.index(marker):]
    for filename, n in [('full_suite.xml', 467), ('pilot_original_tests.xml', 19)]:
        suites = ET.parse(OUT / filename).getroot().findall('testsuite')
        assert sum(int(v.attrib['tests']) for v in suites) == n
        assert all(int(v.attrib[k]) == 0 for v in suites for k in ('failures', 'errors', 'skipped'))
    mutants = read(OUT / 'mutants.json')
    assert all(r['status'] == 'PASS' for r in mutants['baseline'])
    assert len(mutants['mutants']) == 12 and all(r['status'] == 'KILLED' and r['caught_by'] for r in mutants['mutants'])
    assert sum(r.get('mechanism') == 'MATH_INVARIANT_REJECTION' for r in mutants['mutants']) == 1
    assert (OUT / 'T1_failure_before_fix.json').exists() and (OUT / 'audit_unit_tests.xml').exists()
    provenance = read(ROOT / 'experiments/R3R_02_audit/independent_mc_provenance.json')
    assert provenance['engine_source_tests_pilot_or_outcomes_consulted'] is False
    assert provenance['additional_project_sources_read'] == []
    for path, expected in provenance['implementation_files_sha256'].items():
        assert sha(ROOT / path) == expected, path
    p = read(ROOT / 'experiments/R3R_02_audit/prereg.json')
    for rid in p['audit_regimes']:
        engine = read(OUT / f'engine_run01/{rid}/audit.json')
        assert engine['status'] == 'PASS'
        assert all(v['status'] == 'PASS' for v in engine['posterior_prior'].values())
        assert engine['snapshot_v12']['status'] == 'PASS'
        mc = read(OUT / f'mc_run01/{rid}/final.json')
        assert all(v['status'] == 'PASS' for v in mc['C3']['nodes'][-1]['checks'].values())
        assert mc['C3']['nodes'][-1]['SE_target_met']
    assert read(OUT / 'mc_run01/X2065/final.json')['status'] == 'UNRESOLVED'
    assert read(OUT / 'mc_run01/X2065/precision_extension.json')['status'] == 'PASS'
    assert read(OUT / 'mc_run01/X1008/C2_arithmetic_resolution.json')['status'] == 'PASS'
    repro = read(OUT / 'repro_run01/comparison_final.json')
    assert repro['status'] == 'PASS' and len(repro['jobs']) == 19
    assert all(v['all_pairs_exact'] and not v['scalar_mismatches'] for v in repro['jobs'])
    assert next(v for v in repro['jobs'] if v['id'] == 'X2065')['added_metadata_verified_against_spec'] == {'c_sw': 0.}
    # Independently recompute the saved sample means and SD/SE, including failed retry0.
    moment_files = sorted((OUT / 'mc_run01').glob('*/*moments.npz'))
    moment_samples = 0
    for path in moment_files:
        with np.load(path) as data:
            values = data['per_episode']
            mean, sd = values.mean(axis=0), values.std(axis=0, ddof=1)
            assert np.allclose(mean, data['mean'], rtol=1e-12, atol=1e-12)
            assert np.allclose(sd, data['sd'], rtol=1e-12, atol=1e-12)
            assert np.allclose(sd / np.sqrt(len(values)), data['se'], rtol=1e-12, atol=1e-12)
            moment_samples += len(values)
    assert len(moment_files) == 18
    used = read(OUT / 'used_seeds.json')
    assert all(318300000 <= row['seed'] <= 318399999 for row in used['records'])
    historical_search = subprocess.run(['git', '-C', str(ROOT), 'grep', '-n', 'evaluate_sides', PILOT, '--',
                                      'experiments/explore_v13', 'tests/test_explore_v13.py'], capture_output=True, text=True)
    assert historical_search.returncode == 1 and historical_search.stdout == ''
    frozen = verify_frozen()
    links = check_links(['README.md', 'notes/03_experiment_index.md', 'notes/phases/PHASE_3R.md',
                         'notes/phases/PHASE_3R_discovery_record.md', 'notes/theory/T07_population_estimand.md',
                         'notes/verification/l3r_3/code_map.md', 'results/lessons/l3r_3/report.md'])
    outputs = sorted(v for v in OUT.rglob('*') if v.is_file() and v.name not in
                     ('engine_cache.pkl', 'verification.json', 'artifact_index.json', 'audit.log'))
    index = {str(v.relative_to(ROOT)): sha(v) for v in outputs}
    (OUT / 'artifact_index.json').write_text(json.dumps(index, indent=2) + '\n')
    result = dict(responsible='Doan Van Tai', checked_utc=datetime.now(timezone.utc).isoformat(),
                  status='PASS', scope='saved-evidence integrity; scientific audit verdict remains HOLD',
                  checked_head=git('rev-parse', 'HEAD'), audit_verdict='HOLD', Understanding='OPEN', phase4_execution='HOLD',
                  full_tests=467, original_pilot_tests=19, mutants=12, local_links=links,
                  moment_files_recomputed=len(moment_files), C3_saved_samples_checked=moment_samples,
                  artifact_hashes=len(index), artifact_index_sha256=sha(OUT / 'artifact_index.json'),
                  original_pilot_bytes_preserved=True, legacy_freeze=frozen,
                  N7_original_implementation_search='NO_MATCH; new 8 comparisons recorded separately',
                  verifier_source_sha256=sha(Path(__file__)), report_source_sha256=sha(ROOT / 'experiments/lessons/report_l3r_3.py'))
    (OUT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
