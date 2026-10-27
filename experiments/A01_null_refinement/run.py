"""Doan Van Tai — A01 Part0 -> A -> B; no A04 or held-out evaluation."""
import argparse
import csv
from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess
import time
import traceback

import numpy as np

from experiments.A00_engine.cells_adapter import ROOT, GRID_PATH, load_cell, queue_law
from experiments.A00_engine.evaluate import evaluate_sides
from experiments.A00_engine.factorial_core import aggregate, Side
from experiments.A00_engine.physical import side_table
from experiments.A01_null_refinement.controls import controlled, enumerated_oracle
from experiments.A01_null_refinement.provenance import verify
from experiments.A01_null_refinement.psw import reproduce_psw
from experiments.A01_null_refinement.selection import NAMES, choose_final, pair_check, diagnostics

AUTH = dict(allow_grid=True, purpose='A01')
CONFIG = ROOT / 'experiments/A01_null_refinement/config.json'


def safe(x):
    if isinstance(x, dict):
        return {str(k): safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [safe(v) for v in x]
    if isinstance(x, (F, np.floating)):
        return str(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def write(path, obj):
    Path(path).write_text(json.dumps(safe(obj), ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def csv_write(path, rows, fields=None):
    fields = fields or list(rows[0])
    with Path(path).open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sides(c, ref):
    return tuple(side_table(c, w, ref, extended=True, **AUTH)[0] for w in 'AB')


def control_row(kind, cid, ref, r, passed, **extra):
    return dict(control=kind, cell=cid, ref=ref,
                **{g: str(r['G'][g]) for g in NAMES}, exact_identity_pass=bool(passed), **extra)


def run_part0(out, cfg):
    grid = json.loads(GRID_PATH.read_text())
    rows = []
    for cid in cfg['calibration']:
        record = next(r for r in grid['main'] if r['id'] == cid)
        for m in cfg['psw_levels']:
            r = reproduce_psw(cid, m, allow_grid=True)
            passed = [r['p_low'], r['p_high']] == record[f'p_{m}']
            rows.append(dict(cell=cid, ref=m, **r, match=passed))
            csv_write(out / 'psw_check.csv', rows, ['cell', 'ref', 'p_low', 'p_high', 'match'])
            print(f'Part0 {cid} ref={m}: match={passed}', flush=True)
            if not passed:
                raise ArithmeticError('Part0 public p_sw interval mismatch; STOP before costs')
    return len(rows)


def c4_toys():
    # Independent reference distribution, cost enumeration and strict action check.
    A = Side((F(1, 2), F(1, 2)), (F(1), F(3)), (F(1, 2), F(3, 2)),
             (F(10), F(20)), (0, 1))
    B = Side((F(1, 2), F(1, 2)), (F(-4), F(-1, 2)), (F(-2), F(-3, 4)),
             (F(7), F(9)), (0, 0))
    ref, mass = enumerated_oracle(A, B)
    r = aggregate(A, B)
    tieA = Side((F(1),), (F(1),), (F(1),), (F(10),), (0,))
    tieB = Side((F(1),), (F(-1),), (F(-1),), (F(10),), (0,))
    tie = aggregate(tieA, tieB)
    ok = r['L']['11'] == ref and r['p_sw'] == mass and tie['p_sw'] == tie['a00'] == tie['a01'] == 0
    return dict(pass_=ok, L11=str(r['L']['11']), independent_min_cost=str(ref),
                oracle_switch_mass=str(mass), strict_tie_switch_mass=str(tie['p_sw']),
                scope='independent aggregation toy; physical DP checked in L3.2, not independently proved here')


def run_partA(out, cfg):
    nulls, neg, exposure = [], [], []
    c4 = c4_toys()
    write(out / 'oracle_independent.json', c4)
    if not c4['pass_']:
        raise ArithmeticError('C4 toy oracle/tie control failed')
    for cid in cfg['calibration']:
        for m in cfg['control_levels']:
            c = load_cell(cid)
            A, B = sides(c, m)
            original = aggregate(A, B)
            # Full original ledger is exposed by debugging/controls; register honestly.
            exposure.append(dict(cell=cid, ref=m, result=original))
            for kind in ('C2', 'C3'):
                r = controlled(A, B, kind)
                preserved = (r['G']['G_M'] == original['G']['G_M_S1'] if kind == 'C2'
                             else r['G']['G_S'] == original['G']['G_S'])
                passed = r['exact_identity_pass'] and preserved
                nulls.append(control_row(kind, cid, m, r, passed,
                                         preserved_original_contrast=preserved))
            # C2' is an observed mode-visibility diagnostic, never a zero control.
            nulls.append(control_row("C2prime", cid, m, original, True,
                                     preserved_original_contrast='not_required'))
            # u=0 changes pre-decision load: construct both laws again.
            zero_c = dict(c, u=F(0), eta=F(0))
            zA, zB = sides(zero_c, m)
            zr = aggregate(zA, zB)
            zero = all(v == 0 for s in (zA, zB) for col in (s.d, s.dh) for v in col)
            passed = zero and len(set(zr['L'].values())) == 1 and all(zr['G'][g] == 0 for g in NAMES)
            # Independently check that a changed pre-Stay law was used, not cached D.
            old_unit, oldD, _, _ = queue_law(c, 'A', m)
            new_unit, newD, _, _ = queue_law(zero_c, 'A', m)
            changed = old_unit != new_unit or oldD.shape != newD.shape or not np.array_equal(oldD, newD)
            nulls.append(control_row('C1', cid, m, zr, passed and changed,
                                     preserved_original_contrast='not_required'))
            csv_write(out / 'nulls.csv', nulls)
            write(out / 'control_exposure.json', exposure)
            if not all(r['exact_identity_pass'] for r in nulls):
                raise ArithmeticError('C1/C2/C3 control failed; STOP')
            print(f'PartA {cid} ref={m}: C1,C2,C3 PASS; V={original["G"]["V"]}', flush=True)
    for cid in cfg['zero_cells'] + cfg['wd_cells']:
        for m in cfg['control_levels']:
            A, B = sides(load_cell(cid), m)
            r = evaluate_sides(A, B, refinement=m, dt=F(1, 120 * m))
            wd = cid in cfg['wd_cells']
            passed = r['G']['G_S_M1'] == 0 if wd else all(r['G'][g] == 0 for g in NAMES)
            neg.append(control_row('C6' if wd else 'C5', cid, m, r, passed,
                                   Cref=str(r['C_ref']), p_sw=str(r['p_sw']),
                                   E_pos=str(r['E_pos']), E_neg=str(r['E_neg']),
                                   subtractive_G_S_M1=str(r['L']['01'] - r['L']['11'])))
            csv_write(out / 'negative_cells.csv', neg)
            # Full precision diagnostics preserved separately; exact identities don't
            # require the artificial C1/C3 model to satisfy the original oracle definition.
            write(out / f'negative_{cid}_m{m}.json', r)
            print(f'PartA {cid} ref={m}: {"C6" if wd else "C5"} {"PASS" if passed else "FAIL"}', flush=True)
            if not passed:
                raise ArithmeticError('C5/C6 exact-zero control failed; STOP')
    return dict(null_rows=len(nulls), negative_rows=len(neg), C4='PASS',
                all_required_identities_pass=True, C2prime='observation only')


def summary_row(cid, m, r, wall):
    C = float(r['C_ref'])
    return dict(cell=cid, m=m, dt_s=str(F(1, 120 * m)), H=960 * m,
                Cref=C, Cref_low=float(r['intervals']['C_ref'][0]),
                **{g: float(r['G'][g]) for g in NAMES},
                **{'e_' + g: r['e_num'][g] for g in NAMES},
                E_delta=float(r['E_delta']), E_delta_hat=float(r['E_delta_hat']),
                a00=r['a00'], a00_nominal=r['nominal_actions']['00'], a01=r['a01'],
                e_num_max=max(r['e_num'][g] for g in NAMES),
                unresolved_mass_max=max(r['unresolved_mass'].values()),
                precision_ok=r['status'] == 'BOUNDED', status=r['status'], wall_s=wall)


def run_partB(out, cfg):
    rows, per_cell, pairs, diags = [], {}, [], []
    grid = json.loads(GRID_PATH.read_text())
    for cid in cfg['calibration']:
        levels = []
        record = next(r for r in grid['main'] if r['id'] == cid)
        for m in cfg['refinement_levels']:
            if record[f'updates_{m}'] > cfg['updates_cap_per_cell_level'] or record[f'peak_{m}'] > cfg['peak_bytes_cap']:
                raise MemoryError('preregistered A01 resource budget exceeded')
            start = time.monotonic()
            print(f'PartB START {cid} m={m}', flush=True)
            A, B = sides(load_cell(cid), m)
            r = evaluate_sides(A, B, refinement=m, dt=F(1, 120 * m))
            write(out / f'calibration_{cid}_m{m}.json', r)
            row = summary_row(cid, m, r, time.monotonic() - start)
            rows.append(row); levels.append(row)
            csv_write(out / 'refinement.csv', rows)
            print(f'PartB {cid} m={m}: {r["status"]}; max_e={row["e_num_max"]:.6g}; '
                  f'unresolved={row["unresolved_mass_max"]:.6g}; {row["wall_s"]:.1f}s', flush=True)
        per_cell[cid] = levels
        pairs.extend(dict(cell=cid, **pair_check(a, b)) for a, b in zip(levels, levels[1:]))
        diags.extend(dict(cell=cid, **r) for r in diagnostics(levels))
        csv_write(out / 'refinement_pairs.csv', pairs)
        csv_write(out / 'refinement_diagnostics.csv', diags)
    final, picks = choose_final(per_cell)
    result = dict(status='PASS' if final != 'HOLD' else 'HOLD', final_ref=final,
                  final_dt_s=str(F(1, 120 * final)) if final != 'HOLD' else None,
                  per_cell=picks, completed_levels=15,
                  reason='all finer suffix pairs pass' if final != 'HOLD' else
                  'at least one finest pair fails tolerance, sign or precision; fixed budget exhausted',
                  continuum_convergence_certified=False, A04_run=False, heldout_run=False)
    write(out / 'selection.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--allow-grid', action='store_true', required=True)
    args = parser.parse_args()
    if not args.run_id or Path(args.run_id).name != args.run_id:
        raise ValueError('run-id must be a single path component')
    receipt = verify()  # before D, result directory creation or costs
    cfg = json.loads(CONFIG.read_text())
    out = ROOT / 'results/A01' / args.run_id
    out.mkdir(parents=True, exist_ok=False)  # never overwrite failed runs
    start = time.monotonic()
    write(out / 'config.json', cfg)
    write(out / 'manifest.json', dict(author='Doan Van Tai', start_utc=datetime.now(timezone.utc).isoformat(),
          **receipt, config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
          python=platform.python_version(), platform=platform.platform(),
          libraries={p: importlib.metadata.version(p) for p in ('numpy', 'scipy', 'mpmath', 'pytest')},
          compiler=subprocess.check_output(['g++', '--version'], text=True).splitlines()[0],
          longdouble_bits=np.finfo(np.longdouble).nmant + 1, seed=None, heldout_allowed=False))
    try:
        p0 = run_part0(out, cfg)
        partA = run_partA(out, cfg)
        write(out / 'controls_status.json', dict(status='PASS', psw_checks=p0, **partA))
        selection = run_partB(out, cfg)
        write(out / 'run_status.json', dict(**selection, part0='PASS', partA='PASS', wall_s=time.monotonic() - start))
        print(json.dumps(selection, ensure_ascii=False), flush=True)
    except Exception as exc:
        write(out / 'run_status.json', dict(status='FAIL', error=repr(exc), traceback=traceback.format_exc(),
                                          wall_s=time.monotonic() - start, A04_run=False, heldout_run=False))
        raise


if __name__ == '__main__':
    main()
