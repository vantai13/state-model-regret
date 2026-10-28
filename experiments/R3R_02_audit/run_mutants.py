"""Doan Van Tai — execute focused tests on source-level mutants; no source overwrite."""
import importlib.util
import inspect
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import pytest
from experiments.R3R_02_audit import bridge as B
from experiments.R3R_02_audit import pilot_population as P
from experiments.A00_engine import physical


def execute(tests):
    result = []
    for name in sorted(k for k in vars(tests) if k.startswith('test_')):
        with pytest.MonkeyPatch.context() as mp:
            try:
                f = getattr(tests, name)
                f(mp) if inspect.signature(f).parameters else f()
            except AssertionError:
                result.append({'test': name, 'status': 'FAIL_ASSERTION'})
            else:
                result.append({'test': name, 'status': 'PASS'})
    return result


def changed_function(function, before, after):
    text = inspect.getsource(function)
    assert text.count(before) == 1, (function.__name__, before)
    ns = dict(function.__globals__)
    exec(compile(text.replace(before, after), function.__code__.co_filename, 'exec'), ns)
    return ns[function.__name__]


def main():
    path = ROOT / 'tests/test_r3r_engine_audit.py'
    sp = importlib.util.spec_from_file_location('r3r_focused_tests', path)
    tests = importlib.util.module_from_spec(sp); sp.loader.exec_module(tests)
    baseline = execute(tests)
    assert all(r['status'] == 'PASS' for r in baseline)
    original_side, original_gold = physical.side_from_law, B.golden_population
    cases = [
        ('S0_leaks_state', P, 'pair_values', 'J + a00 * ED', 'J + T10'),
        ('swap_L00_L10', P, 'pair_values', "'10': J + T10", "'10': J + a00 * ED"),
        ('mean_state_rollout_D10', physical, 'side_from_law',
         'q0 = np.repeat(qs.astype(dtype)[:, None], 2, axis=1) * _number(unit, dtype)',
         'q0 = np.full((len(qs),2), _number(unit,dtype)*np.sum(np.arange(len(mass))*mass.sum(axis=1)), dtype=dtype)'),
        ('old_mode_independent_of_y', P, 'queue_D', 'prior,bound=law.posterior(index)', 'prior,bound=.5,0.'),
        ('no_age_propagation', P, 'queue_D', 'for _ in range(tau):', 'for _ in range(0):'),
        ('drop_zero_atom', P, 'observation_bins', 'reps, weights = [0], [pmf[0]]', 'reps, weights = [], []'),
        ('unnormalized_y_weights', P, 'observation_bins', 'w / w.sum()', 'w'),
        ('tie_switch', P, 'pair_values', 'bool(EDh < 0), bool(ED < 0)', 'bool(EDh <= 0), bool(ED <= 0)'),
        ('union_weight_row_permutation', P, 'side_rows', 'full[rows_q, rows_m]', 'np.roll(full[rows_q, rows_m],1)'),
        ('Cbar_other_dt', P, 'evaluate', "C = Lbar['11']", "C = Lbar['11'] * 1.01"),
        ('D22_mode_leak', B, 'golden_population', "L['cb0'] = cb", "L['cb0'] = L['10']"),
        ('state_cost_corruption', physical, 'side_from_law', 'J[action] = linear + W1[action]',
         'J[action] = (linear + W1[action])*1.01'),
    ]
    records = []
    for name, obj, attr, before, after in cases:
        try:
            with pytest.MonkeyPatch.context() as mp:
                mutant = changed_function(getattr(obj, attr), before, after)
                mp.setattr(obj, attr, mutant)
                if obj is physical:
                    mp.setattr(P, 'side_from_law', mutant)
                observed = execute(tests)
            caught = [r['test'] for r in observed if r['status'] == 'FAIL_ASSERTION']
            records.append({'mutant': name, 'status': 'KILLED' if caught else 'SURVIVED', 'caught_by': caught})
        except Exception as error:
            # Run errors are not counted as a killed scientific mutant.
            records.append({'mutant': name, 'status': 'EXECUTION_ERROR', 'error': repr(error)})
    out = ROOT / 'results/lessons/l3r_3/mutants.json'
    out.write_text(json.dumps({'baseline': baseline, 'mutants': records}, indent=2) + '\n')
    print(json.dumps(records, indent=2))
    if any(r['status'] != 'KILLED' for r in records):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
