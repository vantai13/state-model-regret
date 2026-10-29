"""Doan Van Tai — L3R.6 read-only integrity audit; writes only results/lessons/l3r_6/verification.json."""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = '2f4195769488be1fb6067b4e30d272c68d8205cb'       # L3R.5 completion, before L3R.6
OUT = Path('results/lessons/l3r_6/verification.json')
DOCS = ('README.md', 'notes/phases/PHASE_3R_hypothesis_cards.md', 'notes/phases/PHASE_3R_forking_paths.md',
        'notes/01_claim_boundary_v1_3.md', 'notes/lessons/L3R.6_identity_prior_filter.md',
        'results/lessons/l3r_6/report.md', 'notes/03_experiment_index.md', 'notes/00_progress_log.md')
PROTECTED = ('results/lessons/l3r_5', 'results/lessons/l3r_4', 'results/lessons/l3r_3', 'results/R3R_01_recount',
             'experiments/R3R_05_contract', 'notes/01_definitions_v1_3.md', 'notes/00_research_brief_v1_3.md',
             'notes/01_definitions_v1_2.md', 'notes/phases/PHASE_3_prediction_card.md', 'notes/theory/T07_population_estimand.md')


def run(*a): return subprocess.run(a, capture_output=True, text=True)


def links(path):
    bad = []
    for target in re.findall(r'\]\(([^)#\s]+)(?:#[^)]*)?\)', Path(path).read_text()):
        if target.startswith(('http://', 'https://', 'mailto:')): continue
        if not (Path(path).parent / target).resolve().exists(): bad.append(target)
    return bad


def main():
    r = {}
    r['contract_freeze'] = json.loads(run(sys.executable, '-m', 'experiments.R3R_05_contract.freeze').stdout)['status']
    r['card_receipt'] = json.loads(run(sys.executable, '-m', 'experiments.R3R_06_cards.verify_cards').stdout)['status']
    old = subprocess.run(['git', 'show', f'{BASE}:notes/phases/PHASE_3R.md'], capture_output=True, check=True).stdout
    r['phase3r_body_preserved'] = Path('notes/phases/PHASE_3R.md').read_bytes().endswith(old)
    r['protected_unchanged'] = {p: run('git', 'diff', '--quiet', BASE, '--', p).returncode == 0 for p in PROTECTED}
    r['broken_links'] = {d: links(d) for d in DOCS if links(d)}
    comp = json.loads(Path('notes/phases/L3R_6_completion.json').read_text())
    rec = json.loads(Path('notes/phases/PHASE_3R_hypothesis_cards.lock.json').read_text())
    r['completion_matches_receipt'] = (comp['card_commit'] == rec['card_commit'] and
                                       comp['card_sha256'] == rec['sha256']['notes/phases/PHASE_3R_hypothesis_cards.md'])
    r['no_cf_artifacts'] = not any(Path(p).exists() for p in ('experiments/CF_v13', 'results/CF_v13'))
    ok = (r['contract_freeze'] == 'PASS' and r['card_receipt'] == 'PASS' and r['phase3r_body_preserved']
          and all(r['protected_unchanged'].values()) and not r['broken_links'] and r['completion_matches_receipt']
          and r['no_cf_artifacts'])
    res = dict(owner='Doan Van Tai', checked_utc=datetime.now(timezone.utc).isoformat(), status='PASS' if ok else 'FAIL',
               base=BASE, head=run('git', 'rev-parse', 'HEAD').stdout.strip(), **r,
               note='integrity only; does not certify hypotheses, numerics, realism or author understanding')
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps(res, indent=1, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
