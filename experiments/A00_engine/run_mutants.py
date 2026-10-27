"""Doan Van Tai — run eleven deliberate faults in an isolated temporary copy.

Never edits the working engine. A mutant is killed only by failed assertions or
explicit mathematical checks in test calls, not collection/import errors.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/lessons/l3_2/mutants'
CORE = 'experiments/A00_engine/factorial_core.py'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ledger_tests = ['tests/test_engine_core.py', 'tests/test_engine_extended.py']
    cut = '_cut_sum(A.dh, A.d, A.p, B.dh, B.d, B.p)'
    specs = [
        ('M1', CORE, '    G = dict(G_S=', "    L['01'], L['10'] = L['10'], L['01']\n    G = dict(G_S=", ledger_tests),
        ('M3', CORE, "L = {'00': K + a00 * Ed", "L = {'00': K + sw10", ledger_tests),
        ('M5a', CORE, 'k = bisect_left(keys, -ka)', "k = __import__('bisect').bisect_right(keys, -ka)", ledger_tests),
        ('M5b', CORE, 'a00, a01 = int(Edh < 0), int(Ed < 0)', 'a00, a01 = int(Edh <= 0), int(Ed < 0)', ledger_tests),
        ('M8', CORE, 'PA, dA, dhA = _by_backlog(A); PB, dB, dhB = _by_backlog(B)',
         'PA, dA, dhA = A.p, A.d, A.dh; PB, dB, dhB = B.p, B.d, B.dh', ledger_tests),
        ('M9', CORE, cut, '_cut_sum(A.d, A.d, A.p, B.d, B.d, B.p)', ledger_tests),
        ('M10', CORE, cut, '_cut_sum(A.dh, A.dh, A.p, B.dh, B.dh, B.p)', ledger_tests),
        ('M2', 'experiments/A00_engine/toy_physics.py',
         'w0 = {a: mean_weighted_idle(q, m, rates, x, c, H, P, dt)',
         'w0 = {a: mean_weighted_idle(sum(F(p0)*q0 for p0,q0,m0 in states)/sum(F(p0) for p0,q0,m0 in states), m, rates, x, c, H, P, dt)',
         ['tests/test_engine_core.py::test_D10_mean_of_rollouts']),
        ('M4', 'experiments/A00_engine/physical.py', "    d = W1['Sw'] - W1['St']",
         "    d = (J['Sw'] - J['St']) - _number((u_switch-u_stay)*dt*dt*H*(H+1)/2, dtype)",
         ['tests/test_engine_physics.py::test_float_conservation_is_exact_at_large_backlog']),
        ('M6', 'src/smr/cells.py', "law_for(sum(rates)/2,u,cell['kappa'],ref)",
         "law_for(sum(rates)/2,u,cell['kappa'],1)",
         ['tests/test_cells_migration.py::test_prior_is_recomputed_at_refinement']),
        ('M7', 'experiments/A00_engine/evaluate.py', '    result = aggregate(A, B)',
         "    result = aggregate(A, B)\n    global _cached_reference\n    if '_cached_reference' not in globals():\n        _cached_reference = result['C_ref']\n    result['C_ref'] = _cached_reference",
         ['tests/test_engine_physics.py::test_native_canonical_and_context_reference']),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix='smr-l32-mutants-') as directory:
        temp = Path(directory)
        for folder in ('src', 'experiments', 'tests'):
            shutil.copytree(ROOT / folder, temp / folder, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (temp / 'notes/design').mkdir(parents=True)
        for name in ('grid_v1_2.json', 'grid_v1_1_redesign_candidate.json'):
            shutil.copy2(ROOT / 'notes/design' / name, temp / 'notes/design' / name)
        shutil.copy2(ROOT / 'pyproject.toml', temp / 'pyproject.toml')
        for folder in ('tests', 'experiments', 'experiments/A00_engine'):
            (temp / folder / '__init__.py').touch()
        env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(temp / 'src'), str(temp))))
        for mid, path, old, new, selection in specs:
            target = temp / path
            original = target.read_text()
            if old not in original:
                raise AssertionError(f'{mid}: mutation location missing')
            target.write_text(original.replace(old, new, 1))
            for cache in list(temp.rglob('__pycache__')):
                shutil.rmtree(cache)
            xml = OUT / f'{mid}.xml'
            command = [sys.executable, '-m', 'pytest', '-q', '--import-mode=importlib',
                       f'--junitxml={xml}', *selection]
            run = subprocess.run(command, cwd=temp, env=env, capture_output=True, text=True)
            (OUT / f'{mid}.log').write_text(run.stdout + run.stderr)
            target.write_text(original)
            cases = list(ET.parse(xml).getroot().iter('testcase')) if xml.exists() else []
            failed = [c.attrib['name'] for c in cases if c.find('failure') is not None]
            errors = [c.attrib['name'] for c in cases if c.find('error') is not None]
            killed = run.returncode == 1 and bool(failed) and not errors
            result = dict(mutant=mid, source=path, status='KILLED' if killed else 'FAIL',
                          failed_tests=failed, collection_or_setup_errors=errors,
                          returncode=run.returncode, selected_tests=selection,
                          equivalent_in_fraction=(mid == 'M4'))
            results.append(result)
            print(mid, result['status'], len(failed), flush=True)
    (OUT / 'summary.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    if not all(r['status'] == 'KILLED' for r in results):
        raise SystemExit('mutant survived or infrastructure failed; see logs')


if __name__ == '__main__':
    main()
