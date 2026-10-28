"""Doan Van Tai — audit saved A05-T data only; never import/call the engine.

This review is after exposure. It neither changes the frozen scorer nor creates
new test evidence. Recompute ratios, losses and dt checks using exact fractions.
Run from the repository: .venv/bin/python results/reviews/l3_7_20261028/audit_saved_run.py
"""
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RUN = ROOT / 'results/A05_test/20261028_01'
OPEN = [f'R{i:02}' for i in (*range(1, 9), 11, 12)]
METRICS = ['G_S', 'G_M', 'Gamma']
SIX = METRICS + ['G_SM', 'G_S_M1', 'G_M_S1']


def read(path):
    return json.loads(path.read_text())


def q(x):
    return F(str(x))


def band(row, key):
    lo, hi = map(q, row['intervals'][key])
    assert lo <= hi
    return lo, hi


def ratio(row, key):
    c = band(row, 'C_ref')
    assert c[0] > 0
    corners = [n / d for n in band(row, key) for d in c]
    return min(corners), max(corners)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def serialize(x):
    if isinstance(x, F):
        return str(x)
    raise TypeError(type(x).__name__)


def main():
    data = read(RUN / 'grading_input.json')
    grades = read(RUN / 'verdict.json')['grades']
    manifest = read(RUN / 'manifest.json')
    config = read(ROOT / 'experiments/A05_freeze/config.json')
    predictions_file = read(ROOT / 'experiments/A05_freeze/predictions_heldout.json')
    predictions = predictions_file['predictions']
    decision = read(ROOT / 'experiments/A05_test/decision.json')
    status = read(RUN / 'run_status.json')
    checks = {}
    hashes = read(RUN / 'output_hashes.json')
    assert all(sha(RUN / name) == digest for name, digest in hashes.items())
    checks['output_sha256'] = {'matched': len(hashes), 'failed': 0}
    assert sha(RUN / 'console.log') == read(ROOT / 'results/lessons/l3_7/verification.json')['console_log_sha256']
    checks['console_sha256'] = 'PASS'
    sources = {**predictions_file['source_sha256'], **decision['source_sha256']}
    assert all(sha(ROOT / name) == digest for name, digest in sources.items())
    assert sha(ROOT / 'experiments/A05_freeze/predictions_heldout.json') == decision['predictions_sha256']
    assert sha(ROOT / 'experiments/A05_freeze/discrimination.json') == decision['discrimination_sha256']
    checks['frozen_and_runner_source_sha256'] = {'matched': len(sources), 'failed': 0}
    checks['prediction_and_discrimination_sha256'] = 'PASS'

    assert manifest['open_ids'] == decision['open_ids'] == OPEN
    assert sorted(p.name for p in (RUN / 'raw').glob('*.json')) == sorted(f'{cid}_m{ref}.json' for cid in OPEN for ref in (1, 2))
    assert set(data['fine']) == set(data['coarse']) == set(OPEN)
    pairs = []
    for cid in OPEN:
        for level, ref in [('coarse', 1), ('fine', 2)]:
            row = data[level][cid]
            assert row == read(RUN / f'raw/{cid}_m{ref}.json')['engine']
            assert row['status'] == 'BOUNDED' and row['numeric_budget_met'] is True
            assert row['refinement'] == ref and q(row['dt_s']) == F(1, 120 * ref)
            assert band(row, 'C_ref') == band(row, 'L11')
            assert row['reference_context'] == {'refinement': ref, 'dt_s': f'1/{120*ref}'}
            assert set(row['unresolved_mass']) == {'oracle', 'M0', 'D22'}
            assert max(map(q, row['unresolved_mass'].values())) <= F(1, 100)
            assert max(map(q, row['e_num'].values())) / band(row, 'C_ref')[0] <= F(1, 400)
        coarse, fine = data['coarse'][cid], data['fine'][cid]
        largest = F(0)
        for metric in SIX:
            a, b = band(coarse, metric), band(fine, metric)
            largest = max(largest, abs(b[0] - a[1]), abs(b[1] - a[0]))
            assert max(abs(b[0] - a[1]), abs(b[1] - a[0])) <= F(1, 400) * band(fine, 'C_ref')[0]
            a, b = ratio(coarse, metric), ratio(fine, metric)
            assert not ((a[1] > F(1, 200) and b[0] < -F(1, 200)) or (b[1] > F(1, 200) and a[0] < -F(1, 200)))
        assert all((ratio(fine, g)[1] - ratio(fine, g)[0]) / 2 <= q(config['truth_radius_cap_for_comparison']) for g in METRICS)
        pairs.append(float(largest / band(fine, 'C_ref')[0]))
    checks['raw_equals_grading_input_levels'] = 20
    checks['registered_ids_dt_reference_numeric_gates'] = 'PASS'
    checks['adjacent_dt_pairs_passed'] = len(pairs)
    checks['max_pair_change_fraction_Cref'] = max(pairs)
    with (RUN / 'psw_check.csv').open() as f:
        public_psw = list(csv.DictReader(f))
    assert {(r['cell'], int(r['ref'])) for r in public_psw} == {(c, ref) for c in OPEN for ref in (1, 2)}
    assert all(r['match'] == 'True' for r in public_psw)
    checks['recorded_public_psw_bitwise_matches'] = len(public_psw)

    # Independent exact scalar MAE and paired difference on saved truth intervals.
    groups = {}
    cells = []
    for name in ['interpolation', 'extrapolation']:
        ids = config['test_groups'][name]
        losses = [[], []]
        differences = []
        for cid in ids:
            local = []
            for metric in METRICS:
                y = ratio(data['fine'][cid], metric)
                p = [q(predictions[cid][model]['contrasts'][metric]) for model in ['H0', 'H1']]
                for model in (0, 1):
                    a, b = [abs(p[model] - yy) for yy in y]
                    losses[model].append((F(0) if y[0] <= p[model] <= y[1] else min(a, b), max(a, b)))
                # Difference is monotone between its two prediction kinks.
                values = [abs(p[0] - yy) - abs(p[1] - yy) for yy in y]
                differences.append((min(values), max(values)))
                local.append(sum(values) / 2)
            row = data['fine'][cid]
            cells.append({'cell': cid, 'group': name,
                          **{f'L{k}_packet_s': row['L'][k] for k in ['00', '01', '10', '11']},
                          **{f'{g}_percent_Cref': float(q(row['G'][g]) / q(row['C_ref']) * 100) for g in METRICS},
                          'GM_lower_percent_Cref': float(ratio(row, 'G_M')[0] * 100),
                          'GM_upper_percent_Cref': float(ratio(row, 'G_M')[1] * 100),
                          'd_contribution_to_group_pp': float(sum(local) / (3 * len(ids)) * 100)})
        n = len(differences)
        d = tuple(sum(v[k] for v in differences) / n for k in (0, 1))
        mae = [tuple(sum(v[k] for v in loss) / n for k in (0, 1)) for loss in losses]
        margin = q(config['margin'])
        verdict = 'SUPPORT' if d[0] >= margin else 'FALSIFY' if d[1] <= 0 else 'WEAKEN' if 0 < d[0] and d[1] < margin else 'INCONCLUSIVE'
        recorded = grades['PC4'][name]
        assert d == tuple(map(q, recorded['d_interval']))
        assert all(mae[i] == tuple(map(q, recorded[f'MAE{i}'])) for i in (0, 1))
        assert verdict == recorded['verdict'] and recorded['available_ids'] == ids
        groups[name] = {'cells': len(ids), 'scalar_entries': n, 'verdict': verdict, 'd_exact': d,
                        'd_pp': [float(x * 100) for x in d],
                        'MAE0_pp': [float(x * 100) for x in mae[0]],
                        'MAE1_pp': [float(x * 100) for x in mae[1]]}
    checks['independent_MAE0_MAE1_paired_d_and_verdict'] = 'PASS'

    rule_states = {}
    for name, ids in [('K5', config['K5_test_ids']), ('C1', config['C1_test_ids'])]:
        states = {}
        branch = grades[name]['heldout_K' if name == 'K5' else 'heldout']
        for cid in ids:
            lo, hi = ratio(data['fine'][cid], 'G_M')
            state = 'STANDS' if hi <= F(1, 200) else 'DOES_NOT_STAND' if lo > F(1, 200) else 'UNRESOLVED'
            assert state == branch['cells'][cid]['verdict']
            headroom = state == 'STANDS' and ratio(data['fine'][cid], 'R00')[1] < F(1, 200)
            label = 'STANDS_HEADROOM_LIMITED' if headroom else 'STANDS_NOT_CERTIFIED_BY_HEADROOM' if state == 'STANDS' else 'NOT_STANDING_OR_UNRESOLVED'
            assert label == branch['cells'][cid]['headroom_label']
            states[cid] = {'verdict': state, 'headroom_label': label,
                           'GM_percent_Cref_interval': [float(lo * 100), float(hi * 100)]}
        state = 'DOES_NOT_STAND' if any(v['verdict'] == 'DOES_NOT_STAND' for v in states.values()) else 'STANDS' if all(v['verdict'] == 'STANDS' for v in states.values()) else 'UNRESOLVED'
        assert state == branch['verdict']
        rule_states[name] = {'verdict': state, 'cells': states}
    checks['independent_K5_C1_and_headroom_labels'] = 'PASS'
    assert grades['PC4']['weak_interpolation']['verdict'] == 'DO_NOT_OPEN'
    assert grades['PC4']['weak_interpolation']['truth_used'] is False
    checks['sealed_outcomes_absent_in_audited_run'] = ['R09', 'R10']

    stages = [decision['freeze_commit'], decision['runner_commit'], manifest['decision']['decision_commit'], 'e719157c2f55a5cff2163bb73ef09a31a3483f7e', 'ec022d1de4aebc5761d10df558d06b186c963547']
    for earlier, later in zip(stages, stages[1:]):
        subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor', earlier, later], check=True)
    chronology = [{'commit': x, 'committed_at': git('show', '-s', '--format=%cI', x)} for x in stages]
    assert datetime.fromisoformat(chronology[2]['committed_at']) < datetime.fromisoformat(manifest['start_utc']) < datetime.fromisoformat(status['end_utc']) < datetime.fromisoformat(chronology[3]['committed_at'])
    untouched = ['experiments/A00_engine', 'experiments/A01_null_refinement', 'experiments/A04_discovery', 'notes/phases/PHASE_3_prediction_card.md']
    assert not git('diff', '--name-only', decision['engine_card_A01_A04_unchanged_since'], 'HEAD', '--', *untouched)
    checks['freeze_runner_decision_run_output_chronology'] = 'PASS'
    checks['engine_card_A01_A04_unchanged'] = 'PASS'

    tests = ET.parse(OUT / 'targeted_tests.xml').getroot()[0].attrib
    assert tests['tests'] == '43' and all(tests[k] == '0' for k in ['errors', 'failures', 'skipped'])
    results = {'responsible': 'Doan Van Tai', 'review_provenance': 'AI-assisted review requested by author; not human supervisor review',
               'audited_HEAD': git('rev-parse', 'HEAD'), 'review_utc': datetime.now(timezone.utc).isoformat(),
               'original_run': str(RUN.relative_to(ROOT)), 'engine_rerun': False, 'checks': checks,
               'tests': tests, 'run_wall_s': status['wall_s'], 'chronology': chronology,
               'margin_pp': float(q(config['margin']) * 100), 'PC4': groups, 'rules': rule_states,
               'scope_limit': 'Saved files, committed history and targeted tests only; not proof of actions outside repo or unconditional engine validity.'}
    (OUT / 'audit.json').write_text(json.dumps(results, indent=2, default=serialize) + '\n')
    with (OUT / 'cells.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(cells[0]))
        writer.writeheader(); writer.writerows(cells)
    print(json.dumps({'checks': checks, 'PC4': {k: {x: v[x] for x in ['verdict', 'd_pp', 'MAE0_pp', 'MAE1_pp']} for k, v in groups.items()}, 'K5': rule_states['K5']['verdict'], 'C1': rule_states['C1']['verdict']}, indent=2))


if __name__ == '__main__':
    main()
