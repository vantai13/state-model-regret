"""Doan Van Tai — v1.3 step-1 [DISCOVERY] on the 38 already-exposed main cells, ref 2.

AI (Claude) viết theo ủy quyền trực tiếp của tác giả (DL-062). The frozen engine guard only
knows the purposes A01/A04/A05-T and is part of the A01 receipt, so it is not edited: this
runner reuses the 'A04' access level, which admits main cells only (held-out stays blocked).
The manifest labels the study V13-STEP1-DISCOVERY. One run; a rerun needs a new DL.
"""
import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
import multiprocessing
from pathlib import Path
import platform
import subprocess
import time
import traceback

import numpy as np

from experiments.A00_engine.cells_adapter import ROOT, load_cell
from experiments.A00_engine.physical import side_table
from experiments.A01_null_refinement.run import write, csv_write
from experiments.A03_card.provenance import _tracked_clean
from experiments.V13_step1 import regime as R

A04_CSV = 'results/A04/20261027_01/main_final.csv'
PREDICTIONS = 'experiments/V13_step1/predictions.md'
DECISION_LOG, EXPOSURE = 'notes/02_decision_log.md', 'notes/00_exposure_register.md'
DL_MARKER, EXPOSURE_MARKER = '### DL-062', 'V13_STEP1_DISCOVERY_DECLARED'
OUT_BASE = 'results/V13_step1'
REF = 2
MAIN = tuple(f'M{i:02}' for i in range(1, 39))


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def preflight(repo=ROOT):
    if _git(repo, 'status', '--porcelain'):
        raise PermissionError('run only from a clean committed tree')
    commit, _ = _tracked_clean(PREDICTIONS, repo)
    touched = set(_git(repo, 'diff-tree', '--no-commit-id', '--name-only', '-r', commit).splitlines())
    if not {PREDICTIONS, DECISION_LOG, EXPOSURE} <= touched:
        raise PermissionError('predictions, DL and exposure entry must share one commit')
    for path, marker in ((DECISION_LOG, DL_MARKER), (EXPOSURE, EXPOSURE_MARKER)):
        _, body = _tracked_clean(path, repo)
        if marker.encode() not in body:
            raise PermissionError(f'{path} lacks the committed step-1 marker')
    base = Path(repo) / OUT_BASE
    if base.exists() and any(base.iterdir()):
        raise PermissionError('step 1 already ran; a rerun needs a new DL')
    return commit


def cell_task(spec):
    cid, stakes = spec
    if cid not in MAIN:
        raise PermissionError('step 1 is restricted to the 38 main cells')
    started = time.monotonic()
    c = load_cell(cid)
    A, _ = side_table(c, 'A', REF, extended=True, allow_grid=True, purpose='A04')
    B, _ = side_table(c, 'B', REF, extended=True, allow_grid=True, purpose='A04')
    fa, fb = R.fluid_idle(A, 'A'), R.fluid_idle(B, 'B')
    pA, pB = R.col(A.p), R.col(B.p)
    out = dict(cell=cid, n_A=len(A.p), n_B=len(B.p), I_A=fa['I'], I_B=fb['I'],
               A_all_zero=fa['all_zero'], B_all_zero=fb['all_zero'],
               A_unresolved=fa['unresolved_mass'], B_unresolved=fb['unresolved_mass'],
               J_A=R.true_idle(A, 'A'), J_B=R.true_idle(B, 'B'),
               E_dh_A=float((pA * R.col(A.dh)).sum()), E_dh_B=float((pB * R.col(B.dh)).sum()),
               E_d_A=float((pA * R.col(A.d)).sum()), E_d_B=float((pB * R.col(B.d)).sum()),
               G_M_S1_recomputed=R.gm_s1(A, B))
    eps = R.EPS_PRIMARY * stakes
    out['lens_boundary'], out['window_mass'] = R.boundary_lens(A, B, eps)
    for factor in R.EPS_SENSITIVITY:
        out[f'lens_boundary_{factor}'], _ = R.boundary_lens(A, B, factor * stakes)
    out['wall_s'] = time.monotonic() - started
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args(argv)
    if not 1 <= args.workers <= 6:
        raise ValueError('workers must be 1..6')
    predictions_commit = preflight()
    rows = {r['cell']: r for r in csv.DictReader(open(ROOT / A04_CSV))}
    if sorted(rows) != sorted(MAIN) or any(rows[c]['refinement'] != str(REF) for c in MAIN):
        raise ValueError('A04 table must hold the 38 main cells at ref 2')
    run_id = datetime.now(timezone(timedelta(hours=7))).strftime('%Y%m%d') + '_01'
    out = ROOT / OUT_BASE / run_id
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    write(out / 'manifest.json', dict(
        responsible='Doan Van Tai', study='V13-STEP1-DISCOVERY', label='DISCOVERY',
        provenance='AI (Claude) theo ủy quyền trực tiếp của tác giả, DL-062',
        predictions_commit=predictions_commit, code_commit=_git(ROOT, 'rev-parse', 'HEAD'),
        guard_access_level_reused='A04 (main cells only; held-out blocked)', cells=list(MAIN), refinement=REF,
        dt_s='1/240', inputs=[A04_CSV], heldout_used=False, R_cells_used=False, seed=None,
        python=platform.python_version(), longdouble_bits=np.finfo(np.longdouble).nmant + 1,
        start_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers))
    try:
        specs = [(c, float(rows[c]['E_pos']) + float(rows[c]['E_neg'])) for c in MAIN]
        results = {}
        with multiprocessing.get_context('fork').Pool(args.workers) as pool:
            for r in pool.imap_unordered(cell_task, specs, chunksize=1):
                results[r['cell']] = r
                print(f"[STEP1] {r['cell']} n_A={r['n_A']} n_B={r['n_B']} done={len(results)}/38", flush=True)
        cells, mismatched = [], []
        for cid in MAIN:
            r, a = results[cid], rows[cid]
            stakes = float(a['E_pos']) + float(a['E_neg'])
            gm, err, C = float(a['G_M_S1']), float(a['e_G_M_S1']), float(a['C_ref'])
            if abs(r['G_M_S1_recomputed'] - gm) > 2 * err + 1e-12 * C:
                mismatched.append(cid)
            label = R.side_label(r['I_A'], r['I_B'])
            target = a['targets']
            cells.append(dict(r, target=target, E_delta=float(a['E_delta']), E_delta_hat=float(a['E_delta_hat']),
                              bias=float(a['bias']), stakes=stakes, C_ref=C, G_M_S1=gm,
                              observed_regime=R.observed_regime(float(a['E_delta']), float(a['E_delta_hat'])),
                              side_label=label, predicted_reversal=R.predicted_reversal(target, label),
                              lens_mean=R.mean_bias_lens(float(a['E_delta']), stakes, float(a['bias']))))
        csv_write(out / 'cells.csv', cells)
        if mismatched:
            write(out / 'run_status.json', dict(status='FAIL_VALIDITY', mismatched=mismatched))
            raise ArithmeticError('recomputed G_M|S1 differs from A04; no scoring')
        summary = R.score(cells)
        status = dict(status='SCORED', validity='PASS', cells=len(cells),
                      max_unresolved_fluid_mass=max(max(c['A_unresolved'], c['B_unresolved']) for c in cells),
                      **{k: v['verdict'] for k, v in summary.items() if k.startswith('P_')},
                      wall_s=time.monotonic() - start, end_utc=datetime.now(timezone.utc).isoformat())
        write(out / 'summary.json', summary)
        write(out / 'run_status.json', status)
        print('[STEP1] ' + json.dumps(status, ensure_ascii=False), flush=True)
    except Exception as exc:
        write(out / 'failure.json', dict(status='FAIL', error=repr(exc), traceback=traceback.format_exc()))
        raise
    finally:
        files = sorted(p for p in out.rglob('*') if p.is_file() and p.name != 'output_hashes.json')
        write(out / 'output_hashes.json', {str(p.relative_to(out)): _sha(p) for p in files})


if __name__ == '__main__':
    main()
