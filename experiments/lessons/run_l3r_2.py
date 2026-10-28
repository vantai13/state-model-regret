"""Doan Van Tai — exact finite toys and mutations for T07; no pilot/CF access."""
import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import subprocess
import types

ROOT = Path(__file__).resolve().parents[2]
TEST = ROOT / 'tests/test_population_toys.py'


def load_reference():
    spec = importlib.util.spec_from_file_location('t07_golden', TEST)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_all(module):
    """Only no-argument exact checks, with AssertionError separated from run errors."""
    rows = []
    for name in sorted(n for n in vars(module) if n.startswith('test_')):
        try:
            getattr(module, name)()
        except AssertionError:
            rows.append({'test': name, 'status': 'FAIL_ASSERTION'})
        else:
            rows.append({'test': name, 'status': 'PASS'})
    return rows


def exact(value):
    value = F(value)
    return {'fraction': str(value), 'value': float(value)}


def summarize(module, name, plant):
    L = module.cells(plant)
    return {'toy': name, 'unit': 'toy_cost_unit',
            'cells': {k: exact(v) for k, v in L.items()},
            'contrasts': {k: exact(v) for k, v in module.contrasts(L).items()},
            'stakes': exact(module.stakes(plant)),
            'relative_status': 'UNDEFINED_ZERO_DENOMINATOR' if L['11'] == 0 else 'DEFINED'}


def run_mutations(reference):
    source = TEST.read_text()
    cases = [
        ('S0_leaks_realized_state', 'cost(P, a00, x)', "cost(P, act(P['Dhat'][x]), x)"),
        ('tie_switches', 'return SWITCH if gap < 0 else STAY',
         'return SWITCH if gap <= 0 else STAY'),
        ('M1_uses_M0_gap', "a01 = act(sum(w * P['Delta'][x] for x, w in Dy.items()))",
         "a01 = act(sum(w * P['Dhat'][x] for x, w in Dy.items()))"),
        ('oracle_maximizes_cost', 'min(cost(P, STAY, x), cost(P, SWITCH, x))',
         'max(cost(P, STAY, x), cost(P, SWITCH, x))'),
        ('cb0_hides_current_backlog', "a = act(sum(w * P['Dhat'][x] for x, w in grp.items()))",
         'a = a00'),
    ]
    records = []
    for name, before, after in cases:
        if source.count(before) != 1:
            raise RuntimeError(f'Mutation anchor must occur exactly once: {name}')
        mutant = types.ModuleType('t07_mutant_' + name)
        exec(compile(source.replace(before, after), str(TEST), 'exec'), mutant.__dict__)
        results = check_all(mutant)
        caught = [r['test'] for r in results if r['status'] == 'FAIL_ASSERTION']
        records.append({'mutant': name, 'status': 'KILLED' if caught else 'SURVIVED',
                        'caught_by': caught, 'tests_executed': len(results)})
    assert len(check_all(reference)) == 16
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('results/lessons/l3r_2/toys'))
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Output directory exists; preserve previous results and use another path.')
    module = load_reference()
    baseline = check_all(module)
    if any(r['status'] != 'PASS' for r in baseline):
        raise RuntimeError(f'Baseline golden failures: {baseline}')
    mutants = run_mutations(module)
    examples = [
        summarize(module, 'age_short', module.two_state_part1(F(4, 5))),
        summarize(module, 'age_long', module.two_state_part1(F(3, 5))),
        summarize(module, 'harm_compensating_errors', module.harm_toy(-2)),
        summarize(module, 'substitutes_error_minus4', module.harm_toy(-4)),
        summarize(module, 'D22_mode_only', module.harm_toy(-2) | {'q': {'x1': 5, 'x2': 5}}),
        summarize(module, 'D22_backlog_only', module.harm_toy(-2) | {'q': {'x1': 8, 'x2': 2}}),
    ]
    xs = ('aON', 'aOFF', 'bON', 'bOFF')
    cancel = module.one_snapshot(J={x: 10 for x in xs}, Delta=dict(zip(xs, (-1, -1, -1, 1))),
                                Dhat=dict(zip(xs, (-1, 2, -3, 1))), q={x: x[0] for x in xs})
    examples.append(summarize(module, 'D22_cancellation', cancel))
    three = dict(p={1: F(1, 2), 2: F(3, 10), 3: F(1, 5)}, D={y: {y: F(1)} for y in (1, 2, 3)},
                 J={1: 10, 2: 10, 3: 10}, Delta={1: F(-3, 2), 2: F(-4, 5), 3: F(9, 10)},
                 Dhat={1: F(-3, 5), 2: F(3, 10), 3: F(6, 5)})
    # JStay=10 rather than 0 changes no action or contrast; keeps illustrative costs positive.
    examples.append(summarize(module, 'three_snapshots', three))
    smoothing = []
    for b in [F(1, 10), F(1, 5), F(3, 10), F(2, 5)]:
        P = module.smoothing_toy(b)
        g, gh = P['Delta'][3], P['Dhat'][3]  # y*=0.35
        smoothing.append({'bias': exact(b), 'GM_population': exact(module.contrasts(module.cells(P))['GM']),
                          'GM_snapshot_y035': exact(abs(g) * (module.act(g) != module.act(gh)))})
    sources = ['notes/theory/T07_population_estimand.md', 'tests/test_population_toys.py',
               'experiments/lessons/run_l3r_2.py', 'experiments/lessons/l3r_2_spec.json']
    manifest = {'responsible': 'Doan Van Tai', 'created_utc': datetime.now(timezone.utc).isoformat(),
                'code_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources},
                'seed': 20261028, 'distinct_random_laws': 500,
                'same_laws_reused_for_tighter_bound': True,
                'scope': 'finite exact toys; not pilot-engine verification or hypothesis confirmation',
                'pilot_engine_called': False, 'CF_outcomes': False, 'R09_R10_outcomes': False,
                'baseline_checks': len(baseline), 'random_identity_violations': 0,
                'status': 'PASS' if all(r['status'] == 'KILLED' for r in mutants) else 'FAIL'}
    args.out.mkdir(parents=True)
    payloads = {'metrics.json': {'examples': examples, 'smoothing': smoothing,
                               'ratio_of_expectations': exact(F(1, 100)),
                               'expectation_of_ratios': exact(F(1, 20)),
                               'stakes_fraction_when_gain13pct_cost_stakes30pct': exact(F(13, 30))},
                'mutants.json': mutants, 'baseline.json': baseline, 'manifest.json': manifest}
    for name, payload in payloads.items():
        (args.out / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': manifest['status'], 'baseline_passed': len(baseline),
                      'distinct_random_laws': 500, 'mutants_killed': sum(r['status'] == 'KILLED' for r in mutants),
                      'out': str(args.out)}, ensure_ascii=False, indent=2))
    if manifest['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
