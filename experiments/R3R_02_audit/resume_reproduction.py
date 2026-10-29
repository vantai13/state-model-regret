"""Doan Van Tai — finish missing jobs in a declared fresh clone/venv reproduction.

Preserves the interrupted comparison ledger and previously completed job files.
Only known discovery robustness records and X2065 are read from the pilot tag.
"""
import concurrent.futures
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def main():
    out = ROOT / 'results/lessons/l3r_3/repro_run01'
    if (out / 'comparison_final.json').exists(): raise ValueError('preserve final reproduction')
    config = json.loads((ROOT / 'results/lessons/l3r_3/repro_environment.json').read_text())
    repo, interpreter, base = Path(config['repo']), config['interpreter'], Path(config['base'])
    assert subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip() == 'a7435e9a3cb0d1625479c942041ec6748444014a'
    assert not subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'], text=True).strip()
    env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(repo / 'src'), str(repo))), TMPDIR=str(base / 'native_tmp'))
    worker = ROOT / 'experiments/R3R_02_audit/reproduction_worker.py'
    original = json.loads((out / 'comparison.json').read_text())
    previous = {r['id']: r for r in original['jobs']}
    rawcsv, rawpairs, jobs = {}, {}, []
    for stage in ('robustK', 'robustdt', 'stage2'):
        raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'explore-v13-pilot:results/explore_v13/{stage}/regimes.csv'])
        rawcsv[stage] = {r['id']: r for r in csv.DictReader(io.StringIO(raw.decode()))}
        raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'explore-v13-pilot:results/explore_v13/{stage}/pairs.npz'])
        arr = np.load(io.BytesIO(raw)); rawpairs[stage] = {k: arr[k] for k in arr.files}
        if stage != 'stage2':
            specs = json.loads(subprocess.check_output(['git', '-C', str(ROOT), 'show', f'explore-v13-pilot:results/explore_v13/{stage}/specs.json']))
            jobs.extend((stage, s) for s in specs)
    r = json.loads((ROOT / 'experiments/R3R_02_audit/regimes.json').read_text())['audit_regimes'][0]
    jobs.append(('stage2', [r['id'], r['lambdaA'], r['lambdaB'], r['kappa'], r['eta'], r['h'], 1, 40, r['c_sw']]))
    cols = ('rid', 'ia', 'ib', 'w', 'ED', 'EDh', 'EdA', 'EdB', 'EhA', 'EhB', 'flip', 'reverse', 'blind', 'm_rel')
    def run(job):
        stage, spec = job; rid = spec[0]
        if rid in previous:
            assert previous[rid]['status'] == 'PASS'
            return dict(previous[rid], resumed=False, preserved_completed_job=True)
        path = base / (rid + '_spec.json'); path.write_text(json.dumps(spec))
        dest = out / rid
        start = time.monotonic()
        with (out / (rid + '_resume.log')).open('w') as log:
            result = subprocess.run([interpreter, str(worker), str(path), str(dest)], cwd=repo, env=env, stdout=log, stderr=subprocess.STDOUT)
        row = dict(id=rid, stage=stage, exit_code=result.returncode, wall_s=time.monotonic() - start, resumed=True)
        if result.returncode: return dict(row, status='FAIL')
        actual = json.loads(dest.with_suffix('.json').read_text()); expected = rawcsv[stage][rid]
        bad = {}
        for k, v in actual.items():
            if k == 'wall_s': continue
            ok = str(v) == expected[k] if k == 'id' else float(v) == float(expected[k]) or np.isnan(float(v)) and np.isnan(float(expected[k]))
            if not ok: bad[k] = [v, expected[k]]
        new = np.load(dest.with_suffix('.npz'))['pairs']; old = rawpairs[stage]; select = old['rid'] == rid
        badpairs = [k for i, k in enumerate(cols) if not (np.array_equal(new[:, i], old[k][select]) if k == 'rid'
                    else np.array_equal(new[:, i].astype(float), old[k][select].astype(float), equal_nan=True))]
        return dict(row, scalar_columns=len(actual) - 1, scalar_mismatches=bad, pairs=len(new),
                    pair_columns_mismatch=badpairs, all_pairs_exact=not badpairs, status='PASS' if not bad and not badpairs else 'FAIL')
    ledger = dict(original, status='RUNNING', jobs=[], interrupted_ledger_preserved=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for record in pool.map(run, jobs):
            ledger['jobs'].append(record)
            (out / 'comparison_resume.json').write_text(json.dumps(ledger, indent=2) + '\n')
            print(json.dumps(record), flush=True)
    ledger['status'] = 'PASS' if len(ledger['jobs']) == 19 and all(r['status'] == 'PASS' for r in ledger['jobs']) else 'FAIL'
    (out / 'comparison_final.json').write_text(json.dumps(ledger, indent=2) + '\n')
    print(ledger['status'], flush=True)


if __name__ == '__main__':
    main()
