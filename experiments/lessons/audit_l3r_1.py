"""Doan Van Tai — audit L3R.1 saved outputs/order; never rerun the recount/engine."""
import csv
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.A05_freeze.provenance import verify_frozen
from experiments.lessons.audit_l3_8 import check_links

OUT = ROOT / 'results/lessons/l3r_1'
RUN = ROOT / 'results/R3R_01_recount/20261028_01'
PILOT = 'a7435e9a3cb0d1625479c942041ec6748444014a'


def read(path):
    return json.loads(path.read_text())


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def main():
    p = read(ROOT / 'experiments/R3R_01_recount/prereg.json')
    m = read(RUN / 'manifest.json')
    r = read(RUN / 'recount.json')
    assert p['responsible'] == m['responsible'] == 'Doan Van Tai'
    assert git('rev-parse', 'explore-v13-pilot^{}') == git('rev-parse', 'explore/v13-population') == PILOT
    assert git('cat-file', '-t', 'explore-v13-pilot') == 'tag'
    assert subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor', PILOT, 'main'], capture_output=True).returncode == 1
    assert not git('ls-files', '--', 'experiments/explore_v13', 'results/explore_v13', 'tests/test_explore_v13.py')
    assert m['declaration_commit'] == git('log', '-1', '--format=%H', '--', 'experiments/R3R_01_recount/prereg.json')
    assert m['pilot_commit'] == r['commit'] == PILOT
    assert 'R3R1_RECOUNT_DECLARED' in git('show', m['declaration_commit'] + ':notes/00_exposure_register.md')
    assert '### DL-064 ' in git('show', m['declaration_commit'] + ':notes/02_decision_log.md')
    declared = datetime.fromisoformat(git('show', '-s', '--format=%cI', m['declaration_commit']))
    tagged = datetime.fromisoformat(git('for-each-ref', '--format=%(taggerdate:iso-strict)', 'refs/tags/explore-v13-pilot'))
    artifact_time = datetime.fromisoformat(m['artifact_last_write_utc'])
    assert max(declared, tagged) < artifact_time
    for path, expected in p['source_sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    assert hashlib.sha256((ROOT / 'experiments/R3R_01_recount/prereg.json').read_bytes()).hexdigest() == m['prereg_sha256']
    for path, blob in r['blobs'].items():
        assert git('rev-parse', PILOT + ':' + path) == blob
    hashes = read(RUN / 'output_hashes.json')
    for name, h in hashes.items():
        assert hashlib.sha256((RUN / name).read_bytes()).hexdigest() == h
    assert not r['problems']
    assert sum(v['match'] for t in r['table'].values() for v in t.values()) == 30
    assert [r['table'][s]['GS_harm']['raw'] for s in ['stage1', 'stage2', 'stage3']] == [6, 73, 1]
    assert r['duplicates']['n_distinct'] == 210 and len(r['duplicates']['groups']) == 6
    assert all(v['max_spread_all_columns'] == 0 for v in r['duplicates']['groups'])
    assert r['text_claims'][0]['raw'] == '80/216' and r['text_claims'][2]['raw'].startswith('78/210')
    assert r['part1_distinct']['n'] == 162 and r['part1_distinct']['harm_total'] == 77
    assert len(r['overlap_v12']['hits']) == 45
    assert len({c for h in r['overlap_v12']['hits'] for c in h['v12_cells']}) == 23
    assert all(z['pilot_same_kappa'] == z['pilot_same_h'] == z['pilot_same_kappa_and_h'] == 0 for z in r['overlap_v12']['sealed'])
    assert all(v['n_pairs'] == 9 and not v['missing'] for v in r['robustness'].values())
    with (RUN / 'discovery_regimes.csv').open() as f:
        reader = csv.DictReader(f)
        assert set(reader.fieldnames) == {'id', 'stage', 'lambdaA', 'lambdaB', 'kappa', 'eta', 'h', 'c_sw', 'ref', 'K', 'u'}
        rows = list(reader)
    assert len(rows) == 234 and len({row['id'] for row in rows}) == 234
    tests = {}
    for name, n in [('recount_tests.xml', 13), ('full_suite.xml', 423)]:
        suite = ET.parse(OUT / name).getroot()[0].attrib
        assert int(suite['tests']) == n and all(int(suite[k]) == 0 for k in ['errors', 'failures', 'skipped'])
        tests[name] = suite
    mutants = read(OUT / 'mutants.json')
    assert len(mutants) == 3 and all(v['status'] == 'KILLED' for v in mutants)
    assert m['recount_exit_code'] == 0 and m['local_recount_invocations'] == 1
    assert m['zip_preview_matches_after_Rev_normalization'] is True
    assert m['pasted_preview_matches_ignoring_final_newline'] is True
    assert m['controller_recovered_without_recount'] is True
    assert m['engine_rerun'] is m['new_regimes'] is m['confirmation_outcomes'] is False
    assert not (ROOT / 'results/explore_v13/stage3/L3R1_part2_bundle.zip').exists()
    ledger = (ROOT / 'notes/lessons/L3R.1_evidence_ledger.md').read_text()
    assert len(re.findall(r'^\| (?:[1-9]|1[0-4]) \|', ledger, re.M)) == 14
    record = (ROOT / 'notes/phases/PHASE_3R_discovery_record.md').read_text()
    assert all(f'| E{i} |' in record for i in range(1, 8))
    assert '<RUN>' not in record and '[TÁC GIẢ' not in record
    marker = '# PHASE 3R — Reformulation v1.3:'.encode()
    original_plan = subprocess.check_output(['git', '-C', str(ROOT), 'show', m['declaration_commit'] + ':notes/phases/PHASE_3R.md'])
    current_plan = (ROOT / 'notes/phases/PHASE_3R.md').read_bytes()
    assert original_plan[original_plan.index(marker):] == current_plan[current_plan.index(marker):]
    paths = ['README.md', 'notes/03_experiment_index.md', 'notes/phases/PHASE_3R.md',
             'notes/phases/PHASE_3R_discovery_record.md', 'notes/lessons/L3R.1_evidence_ledger.md',
             'results/lessons/l3r_1/report.md']
    links = check_links(paths)
    frozen = verify_frozen()
    payload = dict(responsible='Doan Van Tai', checked_utc=datetime.now(timezone.utc).isoformat(),
                   status='PASS', scope='saved-data verification, not engine validation or hypothesis confirmation',
                   declaration_commit=m['declaration_commit'], pilot_commit=PILOT,
                   annotated_pilot_tag_correct=True, pilot_branch_not_merged=True,
                   tag_and_declaration_precede_recount=True, tag_before_declaration_commit=True,
                   input_blobs_checked=len(r['blobs']), output_hashes_checked=len(hashes),
                   source_hashes_checked=len(p['source_sha256']), local_links_checked=links,
                   tests=tests, mutants_killed=3, stage_summary_cells_matched=30,
                   main_IDs=216, distinct_main_configurations=210, duplicate_pairs=6,
                   excluded_regime_parameter_rows=234, v12_overlap_IDs=45, v12_overlap_cells=23,
                   no_overlap_design_assertion_satisfied=False,
                   preview_matches_except_Rev=True, pasted_only_missing_final_newline=True,
                   original_plan_body_preserved=True,
                   zip_deleted=True, zip_tracked=False, local_recount_invocations=1,
                   protected_v12_freeze=frozen['freeze_commit'], engine_rerun=False,
                   confirmation_outcomes=False, Understanding='OPEN', phase4_execution='HOLD',
                   next_lesson='L3R.2', deviations=m['deviations'])
    (OUT / 'verification.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    completion = {k: payload[k] for k in ['responsible', 'checked_utc', 'status', 'pilot_commit',
                  'declaration_commit', 'zip_deleted', 'engine_rerun', 'confirmation_outcomes',
                  'Understanding', 'phase4_execution', 'next_lesson']}
    completion.update(status='L3R_1_TECHNICAL_COMPLETE', report='results/lessons/l3r_1/report.md',
                      discovery_record='notes/phases/PHASE_3R_discovery_record.md',
                      P0_V10='OPEN', L8='OPEN', V9='WAIVED_BY_AUTHOR',
                      engine_audit='NOT_RUN', realism='NOT_RUN', G_level='G1')
    (ROOT / 'notes/phases/L3R_1_completion.json').write_text(json.dumps(completion, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: payload[k] for k in ['status', 'local_links_checked', 'input_blobs_checked',
                          'output_hashes_checked', 'stage_summary_cells_matched', 'main_IDs',
                          'distinct_main_configurations', 'v12_overlap_IDs', 'zip_deleted', 'engine_rerun',
                          'Understanding', 'phase4_execution']}, indent=2))


if __name__ == '__main__':
    main()
