"""Doan Van Tai — in-memory mutations on five-row fake data; no pilot access."""
import importlib.util
import json
from pathlib import Path
import types


def main():
    root = Path(__file__).resolve().parents[2]
    path = root / 'tests/test_r3r_01_recount.py'
    spec = importlib.util.spec_from_file_location('recount_fake_tests', path)
    tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tests)
    original = tests.R
    source = (Path(__file__).with_name('recount.py')).read_text()
    cases = [
        ('harm_boundary_excluded', "r['G_S_pctC'] <= -1", "r['G_S_pctC'] < -1", 'test_summary_row_known_answers'),
        ('model_value_boundary_excluded', "r['G_M_pctC'] >= 1", "r['G_M_pctC'] > 1", 'test_summary_row_known_answers'),
        ('wrong_transfer_rate', 'u = 2 * eta', 'u = eta', 'test_eta_meaning_splits_when_lambdaB_not_8'),
    ]
    results = []
    for name, before, after, check in cases:
        assert before in source
        mutant = types.ModuleType('recount_mutant_' + name)
        exec(compile(source.replace(before, after), str(path), 'exec'), mutant.__dict__)
        tests.R = mutant
        try:
            getattr(tests, check)()
        except AssertionError:
            results.append(dict(mutant=name, status='KILLED', test=check))
        else:
            results.append(dict(mutant=name, status='SURVIVED', test=check))
        finally:
            tests.R = original
    print(json.dumps(results, indent=2))
    if any(r['status'] != 'KILLED' for r in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
