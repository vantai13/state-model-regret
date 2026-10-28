"""Doan Van Tai — verify saved L3R.2 artifacts and pre-audit T07; no engine run."""
import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.A05_freeze.provenance import verify_frozen
from experiments.lessons.audit_l3_8 import check_links

OUT = ROOT / 'results/lessons/l3r_2'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def main():
    (OUT / 'verification.json').write_text(json.dumps({'status': 'RUNNING', 'responsible': 'Doan Van Tai'}) + '\n')
    spec = read(ROOT / 'experiments/lessons/l3r_2_spec.json')
    manifest = read(OUT / 'toys/manifest.json')
    for rel, expected in spec['source_sha256'].items():
        assert sha(ROOT / rel) == expected, rel
    for rel, expected in manifest['source_sha256'].items():
        assert sha(ROOT / rel) == expected, rel
        committed = subprocess.check_output(['git', '-C', str(ROOT), 'show', manifest['code_commit'] + ':' + rel])
        assert hashlib.sha256(committed).hexdigest() == expected
    assert git('log', '--format=%H', '-1', '--', 'notes/theory/T07_population_estimand.md') == manifest['code_commit']
    assert manifest['status'] == 'PASS' and manifest['baseline_checks'] == 16
    assert manifest['distinct_random_laws'] == 500 and manifest['random_identity_violations'] == 0
    assert manifest['pilot_engine_called'] is manifest['CF_outcomes'] is manifest['R09_R10_outcomes'] is False
    tests = {}
    for filename, expected_n in [('toy_tests.xml', 16), ('full_suite.xml', 439)]:
        suites = ET.parse(OUT / filename).getroot().findall('testsuite')
        assert sum(int(s.attrib['tests']) for s in suites) == expected_n
        assert all(int(s.attrib[k]) == 0 for s in suites for k in ('errors', 'failures', 'skipped'))
        tests[filename] = {'tests': expected_n, 'seconds': sum(float(s.attrib['time']) for s in suites)}
    baseline, mutants = read(OUT / 'toys/baseline.json'), read(OUT / 'toys/mutants.json')
    assert len(baseline) == 16 and all(r['status'] == 'PASS' for r in baseline)
    assert len(mutants) == 5 and all(r['status'] == 'KILLED' and r['caught_by'] for r in mutants)
    metrics = read(OUT / 'toys/metrics.json')
    rows = {r['toy']: r for r in metrics['examples']}
    def value(toy, group, key):
        return F(rows[toy][group][key]['fraction'])
    assert value('three_snapshots', 'contrasts', 'GM') == F(6, 25)
    assert value('harm_compensating_errors', 'contrasts', 'GS') == F(-1, 2)
    assert value('substitutes_error_minus4', 'contrasts', 'Gamma') == F(-1, 2)
    for name, f, v in [('D22_mode_only', 0, F(-1, 2)), ('D22_backlog_only', F(-1, 2), 0),
                       ('D22_cancellation', F(-1, 2), F(1, 2))]:
        assert (value(name, 'contrasts', 'F'), value(name, 'contrasts', 'V')) == (f, v)
    assert value('age_short', 'cells', '11') == value('age_long', 'cells', '11') == 9
    assert F(metrics['ratio_of_expectations']['fraction']) == F(1, 100)
    assert F(metrics['expectation_of_ratios']['fraction']) == F(1, 20)
    t07 = (ROOT / 'notes/theory/T07_population_estimand.md').read_text()
    assert len(re.findall(r'^\| S\d\d \|', t07, re.M)) == 18
    assert 'Understanding/ownership OPEN' in t07
    assert not git('diff', 'bf3915e', '--', 'notes/01_definitions_v1_2.md',
                   'notes/01_definitions_v1_3_draft.md', 'notes/01_claim_boundary_v1_2.md',
                   'experiments/A05_freeze', 'results/A05_test', 'results/R3R_01_recount')
    pilot = git('rev-parse', 'explore-v13-pilot^{}')
    assert pilot == 'a7435e9a3cb0d1625479c942041ec6748444014a'
    assert git('rev-parse', 'explore/v13-population') == pilot
    assert subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor', pilot, 'HEAD'], capture_output=True).returncode == 1
    assert not git('ls-files', '--', '*.zip', 'experiments/explore_v13', 'results/explore_v13')
    # Preserve original supplied Phase3R body, including CRLF, independently of new local addenda.
    marker = '# PHASE 3R — Reformulation v1.3:'.encode()
    oldplan = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'bf3915e:notes/phases/PHASE_3R.md'])
    newplan = (ROOT / 'notes/phases/PHASE_3R.md').read_bytes()
    assert oldplan[oldplan.index(marker):] == newplan[newplan.index(marker):]
    paths = ['README.md', 'notes/03_experiment_index.md', 'notes/phases/PHASE_3R.md',
             'notes/theory/T07_population_estimand.md', 'results/lessons/l3r_2/report.md']
    links = check_links(paths)
    completion = read(ROOT / 'notes/phases/L3R_2_completion.json')
    assert completion['Understanding'] == 'OPEN' and completion['phase4_execution'] == 'HOLD'
    assert completion['status'] == 'L3R_2_TECHNICAL_COMPLETE'
    frozen = verify_frozen()
    outputs = sorted(p for p in (OUT / 'toys').iterdir() if p.is_file())
    result = {'responsible': 'Doan Van Tai', 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS', 'scope': 'saved finite exact toys; no pilot-engine audit',
              'T07_commit': manifest['code_commit'], 'source_hashes_verified': len(manifest['source_sha256']),
              'tests': tests, 'mutants_killed': 5, 'distinct_random_laws': 500,
              'random_identity_violations': 0, 'sanity_rows': 18, 'local_links_checked': links,
              'legacy_freeze': frozen, 'pilot_unmerged': True, 'contracts_and_old_outcomes_unchanged': True,
              'outputs_sha256': {str(p.relative_to(ROOT)): sha(p) for p in outputs},
              'Understanding': 'OPEN', 'phase4_execution': 'HOLD', 'G_level': 'G1'}
    (OUT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
