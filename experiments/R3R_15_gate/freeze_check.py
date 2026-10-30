"""Doan Van Tai — L3R.8 freeze check: hashes, commit ancestry, CF list, exposure inside card regions.

AI (Claude) theo ủy quyền ("làm những cái bạn có thể tự làm"). Reads files and git only; no engine, no CF outcome.
Writes results/lessons/l3r_8/freeze_check.json (write-once).

  python -m experiments.R3R_15_gate.freeze_check
"""
from collections import Counter
from fractions import Fraction as F
import csv
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path('results/lessons/l3r_8/freeze_check.json')
LOCKS = {'contract_v1_3': 'notes/phases/contract_v1_3.lock.json', 'cards_v1': 'notes/phases/PHASE_3R_hypothesis_cards.lock.json',
         'cards_v2': 'notes/phases/PHASE_3R_hypothesis_cards_v2.lock.json', 'numerics_lean': 'notes/phases/numerics_v1_3_1_lean.lock.json'}
CF = 'results/lessons/l3r_7/lean_close/cf_generation/attempt01/regimes_cf.json'


def git(*a, check=True):
    return subprocess.run(['git', *a], capture_output=True, text=True, check=check).stdout.strip()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ancestor(a, b):
    return subprocess.run(['git', 'merge-base', '--is-ancestor', a, b]).returncode == 0


def lock_status(path):
    rec = json.loads(Path(path).read_text())
    files = rec.get('source_sha256') or rec.get('sha256') or {}
    bad = [p for p, h in files.items() if not Path(p).exists() or sha(p) != h]
    return dict(files=len(files), mismatched=bad, ok=not bad)


def main():
    report = dict(owner='Doan Van Tai', scope='read-only freeze check before Gate 3R; no engine, no CF outcome',
                  head=git('rev-parse', 'HEAD'))
    report['locks'] = {k: lock_status(v) for k, v in LOCKS.items()}
    pre = json.loads(Path('experiments/R3R_14_lean_close/cf_prereg.json').read_text())
    report['cf_prereg_artifacts'] = {k: dict(path=v['path'], ok=sha(v['path']) == v['sha256'], sha256=v['sha256'])
                                     for k, v in pre['artifacts'].items()}
    commits = {name: git('log', '-1', '--format=%H', '--', path) for name, path in (
        ('cards_v1', 'notes/phases/PHASE_3R_hypothesis_cards.md'), ('cards_v2', 'notes/phases/PHASE_3R_hypothesis_cards_v2.md'),
        ('numerics_spec', 'notes/design/numerics_v1_3_1_lean.json'), ('seed', 'results/lessons/l3r_7/lean_close/seed_allocation.json'),
        ('cf_prereg', 'experiments/R3R_14_lean_close/cf_prereg.json'), ('cf_list', CF))}
    order = ['cards_v1', 'cards_v2', 'numerics_spec', 'seed', 'cf_prereg', 'cf_list']
    report['commits'] = commits
    report['ancestry_in_order'] = all(ancestor(commits[a], commits[b]) and commits[a] != commits[b]
                                      for a, b in zip(order, order[1:]))
    report['tags'] = {t: git('rev-list', '-n1', t, check=False) for t in
                      ('contract-v1.3', 'numerics-v1.3.1-lean', 'explore-v13-pilot', 'explore-v13-regime-map')}
    envelope, labels = '6bef959', '1164500'
    report['realism_envelope_before_labels'] = ancestor(envelope, labels) and envelope != labels
    cf = json.loads(Path(CF).read_text())
    report['cf_list'] = dict(sha256=sha(CF), rows=len(cf['rows']), per_region=dict(Counter(r['origin_region'] for r in cf['rows'])),
                             attempts=sorted(p.name for p in Path(CF).parents[1].iterdir() if p.is_dir()), outcome_files=0)
    # exposure: parameter keys seen before the draw that fall inside each card-v2 region
    from experiments.R3R_07_confirmation.sampler import inside
    from experiments.R3R_14_lean_close.cards_v2 import load
    card = load()
    inv = json.loads(Path('results/lessons/l3r_7/lean_close/collision_inventory_v3.json').read_text())
    exposure = {name: Counter() for name in card['regions']}
    seen_keys = {name: set() for name in card['regions']}
    for rec in inv['records']:
        if rec['namespace'] != 'v1.3_fixed_plant':
            continue
        for name, region in card['regions'].items():
            if inside(rec['coordinates'], region) and rec['key'] not in seen_keys[name]:
                seen_keys[name].add(rec['key'])
                exposure[name][rec['source'].split('/')[0]] += 1
    report['exposure_inside_regions'] = {k: dict(v, distinct_keys=len(seen_keys[k])) for k, v in exposure.items()}
    rows = list(csv.DictReader(open('results/lessons/l3r_7/preparation/power.csv')))
    report['power_n60'] = [r for r in rows if r['n'] == '60' and r['p_plus'] in ('3/5', '7/10') and r['p_minus'] in ('1/5', '1/10')]
    report['all_ok'] = all(v['ok'] for v in report['locks'].values()) and all(v['ok'] for v in report['cf_prereg_artifacts'].values()) \
        and report['ancestry_in_order'] and report['cf_list']['rows'] == 270
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('x') as f:
        f.write(json.dumps(report, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps(report, indent=1, ensure_ascii=False)[:6000])


if __name__ == '__main__':
    main()
