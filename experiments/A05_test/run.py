"""Doan Van Tai — A05-T: open the ten declared held-out cells exactly once, grade by frozen rules.

AI (Claude) viết theo ủy quyền trực tiếp của tác giả (L3.7, DL-059); không là
bằng chứng tác giả tự viết. The CLI has no option for cells, dt, margin, metric
or model: all come from the frozen A05-F records. Order: frozen chain ->
committed decision -> exact IDs -> empty output -> manifest -> public p_sw check
-> engine -> validity/invariants -> frozen scorer -> pre-declared diagnostics.
"""
import argparse
from datetime import datetime, timedelta, timezone
from fractions import Fraction as F
import importlib.metadata
import json
import multiprocessing
from pathlib import Path
import platform
import time
import traceback

import numpy as np

from experiments.A00_engine.cells_adapter import ROOT, GRID_PATH, load_cell, queue_law
from experiments.A00_engine.evaluate import evaluate_sides
from experiments.A00_engine.guard import guard
from experiments.A00_engine.physical import side_table
from experiments.A01_null_refinement.psw import _component
from experiments.A01_null_refinement.run import write, csv_write
from experiments.A04_discovery.validity import physical_checks, row as validity_row, pair
from experiments.A05_freeze.provenance import CONFIG, PREDICTIONS, DISCRIMINATION, read, verify_frozen
from experiments.A05_freeze.score_test import score, safe
from experiments.A05_test.gate import (OPEN, SEALED, OUTPUT_BASE, check_ids, require_committed_decision,
                                       require_fresh_output, sha)
from experiments.A05_test.invariants import extra_checks, diagnostics
from smr.gap_screen import probability_interval

REFS = (1, 2)
UPDATES_CAP, PEAK_CAP = 200000000000, 1073741824  # A04-registered per cell-level budget
VALIDITY_CFG = dict(zero_cells=[], wd_cells=[])   # held-out cells are candidates, not controls
AUTH = dict(allow_grid=True, allow_heldout=True, purpose='A05-T')


def psw_interval(cid, ref):
    """Design-screen p_sw sign interval (same convention as A01 Part0), A05-T guard."""
    if cid not in OPEN:
        raise PermissionError('p_sw check outside the opening list')
    guard(cid, **AUTH)
    c = load_cell(cid)
    parts = {w: queue_law(c, w, ref) for w in 'AB'}
    for extended in (False, True):
        a, pa, ea, da, za = _component(c, 'A', ref, parts['A'], extended)
        b, pb, eb, db, zb = _component(c, 'B', ref, parts['B'], extended)
        r = probability_interval(a, b, pa, pb, ea, eb, da + db, za, zb)
        if r['unresolved_mass'] <= .01:
            return [r['p_low'], r['p_high']]
    raise ArithmeticError('p_sw unresolved mass exceeds .01')


def psw_check(records, out):
    rows = []
    for cid in OPEN:
        for m in REFS:
            got = psw_interval(cid, m)
            match = got == records[cid][f'p_{m}']
            rows.append(dict(cell=cid, ref=m, p_low=got[0], p_high=got[1], match=match))
            csv_write(out / 'psw_check.csv', rows)
            print(f'[PSW] {cid} ref={m} match={match}', flush=True)
            if not match:
                raise ArithmeticError('public p_sw interval mismatch; STOP before costs')
    return rows


def level_task(spec):
    cid, ref = spec
    if cid not in OPEN or ref not in REFS:
        raise PermissionError('engine call outside the frozen opening list')
    started = time.monotonic()
    c = load_cell(cid)
    tables, details = [], []
    for which in 'AB':
        t, d = side_table(c, which, ref, extended=True, **AUTH)
        tables.append(t); details.append(d)
    r = evaluate_sides(*tables, refinement=ref, dt=F(1, 120 * ref))
    return cid, ref, r, physical_checks(tables, details), c, time.monotonic() - started


def preflight():
    """Everything that must hold before a held-out D or cost exists."""
    frozen = verify_frozen()
    decision = require_committed_decision(frozen)
    disc = read(ROOT / DISCRIMINATION)
    check_ids(disc['outcome_open_ids'])
    records = {r['id']: r for r in read(GRID_PATH)['heldout']}
    check_ids([cid for cid in OPEN if cid in records])
    for cid in OPEN:
        for m in REFS:
            if records[cid][f'updates_{m}'] > UPDATES_CAP or records[cid][f'peak_{m}'] > PEAK_CAP:
                raise MemoryError('registered per cell-level budget exceeded')
    base = ROOT / OUTPUT_BASE
    require_fresh_output(base)
    return frozen, decision, disc, records, base


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args(argv)
    if not 1 <= args.workers <= 6:
        raise ValueError('workers must be 1..6')
    frozen, decision, disc, records, base = preflight()
    run_id = datetime.now(timezone(timedelta(hours=7))).strftime('%Y%m%d') + '_01'
    out = base / run_id
    out.mkdir(parents=True, exist_ok=False)
    (out / 'raw').mkdir()
    start = time.monotonic()
    write(out / 'manifest.json', dict(
        responsible='Doan Van Tai', provenance='AI (Claude) theo ủy quyền trực tiếp của tác giả, DL-059',
        start_utc=datetime.now(timezone.utc).isoformat(), A05_F=frozen, decision=decision,
        open_ids=list(OPEN), sealed_ids=list(SEALED), refinements=list(REFS), scoring_dt_s='1/240',
        check_dt_s='1/120', python=platform.python_version(), platform=platform.platform(),
        libraries={p: importlib.metadata.version(p) for p in ('numpy', 'scipy', 'mpmath')},
        longdouble_bits=np.finfo(np.longdouble).nmant + 1, seed=None, sampling_CI=False,
        workers=args.workers, heldout_evaluated=True, one_shot=True))
    try:
        psw_rows = psw_check(records, out)
        tasks = [(cid, m) for cid in OPEN for m in REFS]
        results, checks = {}, []
        with multiprocessing.get_context('fork').Pool(args.workers) as pool:
            for cid, m, r, phys, cell, wall in pool.imap_unordered(level_task, tasks, chunksize=1):
                extra = extra_checks(cid, m, r, records[cid], cell)
                results[cid, m] = r
                write(out / 'raw' / f'{cid}_m{m}.json', dict(engine=r, physical_validity=phys,
                                                             extra_invariants=extra, wall_s=wall))
                v = validity_row(cid, m, r, phys, VALIDITY_CFG)
                v.update(extra)
                v['hard_pass'] = bool(v['hard_pass'] and all(extra.values()))
                checks.append(v)
                csv_write(out / 'validity_partial.csv', checks)
                print(f'[VALIDITY] {cid} ref={m} hard={v["hard_pass"]} status={r["status"]} '
                      f'completed={len(checks)}/{len(tasks)}', flush=True)
        pairs = {cid: pair(results[cid, 1], results[cid, 2]) for cid in OPEN}
        checks.sort(key=lambda x: (x['cell'], x['refinement']))
        for v in checks:
            v.update({k: x for k, x in pairs[v['cell']].items() if k not in ('F_pair_change', 'V_pair_change')})
        csv_write(out / 'validity.csv', checks)
        write(out / 'grading_input.json', {level: {cid: results[cid, m] for cid in OPEN}
                                          for level, m in (('coarse', 1), ('fine', 2))})
        hard_failed = [f'{v["cell"]}/m{v["refinement"]}' for v in checks if not v['hard_pass']]
        status = dict(validity='FAIL' if hard_failed else 'PASS', completed_levels=len(checks),
                      psw_checks=len(psw_rows), hard_failures=hard_failed,
                      hold_levels=[f'{v["cell"]}/m{v["refinement"]}' for v in checks if v['status'] != 'BOUNDED'],
                      dt_pair_not_stands=[cid for cid in OPEN if pairs[cid]['pair_flag']],
                      max_e_over_Cref_lower=max(v['max_e_over_Cref_lower'] for v in checks
                                                if v['max_e_over_Cref_lower'] != ''),
                      max_unresolved_mass=max(v['unresolved_' + k] for v in checks for k in ('oracle', 'M0', 'D22')))
        write(out / 'validity_status.json', status)
        if hard_failed:
            raise ArithmeticError('tier-1 validity failed; preserve outputs, no scoring')
        if verify_frozen() != frozen:
            raise PermissionError('A05-F freeze changed during the run')
        data = read(out / 'grading_input.json')
        grades = score(data, read(ROOT / PREDICTIONS)['predictions'], disc, read(ROOT / CONFIG))
        write(out / 'verdict.json', safe(dict(provenance=frozen, decision=decision, grades=grades)))
        eligible = {name: g.get('available_ids') for name, g in grades['PC4'].items()}
        write(out / 'diagnostics.json', safe(diagnostics(data, read(ROOT / PREDICTIONS)['predictions'],
                                                         disc, records, eligible)))
        summary = dict(status='SCORED', **status, primary_PC4=grades['primary_verdict'],
                       PC4={k: v['verdict'] for k, v in grades['PC4'].items()},
                       K5_heldout=grades['K5']['heldout_K']['verdict'],
                       K5_full_rule=grades['K5']['full_rule_verdict'], C1=grades['C1']['heldout']['verdict'],
                       end_utc=datetime.now(timezone.utc).isoformat(), wall_s=time.monotonic() - start,
                       sealed_untouched=list(SEALED))
        write(out / 'run_status.json', summary)
        print('[A05-T] ' + json.dumps(safe(summary), ensure_ascii=False), flush=True)
    except Exception as exc:
        write(out / 'failure.json', dict(status='FAIL', error=repr(exc), traceback=traceback.format_exc(),
                                         wall_s=time.monotonic() - start))
        raise
    finally:
        files = sorted(p for p in out.rglob('*') if p.is_file() and p.name != 'output_hashes.json')
        write(out / 'output_hashes.json', {str(p.relative_to(out)): sha(p) for p in files})


if __name__ == '__main__':
    main()
