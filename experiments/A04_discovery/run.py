"""Doan Van Tai — 92 declared cell-levels, validity-only console before grading."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import importlib.metadata
import json
import multiprocessing
from pathlib import Path
import platform
import time
import traceback

import numpy as np

from smr.thresholds import verdict
from experiments.A00_engine.cells_adapter import ROOT, GRID_PATH, load_cell
from experiments.A00_engine.physical import side_table
from experiments.A00_engine.evaluate import evaluate_sides
from experiments.A00_engine.factorial_core import _cut_sum
from experiments.A01_null_refinement.run import write, csv_write
from experiments.A03_card.grading import CONTRASTS
from experiments.A04_discovery.provenance import BASE, read, sha, verify
from experiments.A04_discovery.validity import physical_checks, row as validity_row, pair


def point_label(gain, C, eps_R):
    if eps_R > .005:
        return verdict(gain, C, eps_E=.005, eps_R=eps_R)
    # D23 sensitivity at coincident epsilon_R=epsilon_E: closed equivalence first.
    if C == 0:
        return 'excluded_zero_reference'
    q = gain / C
    if abs(q) <= .005:
        return 'equivalent_point'
    return 'practical_positive' if q >= eps_R else 'practical_negative'


def r04_diagnostic(A, B, details, r):
    ld = np.longdouble
    khat = sum(sum(p * (j - (w1 - w0)) for p, j, w1, w0 in
                  zip(s.p, s.jst, d['W1']['St'], d['W0']['St'])) for s, d in zip((A, B), details))
    _, chosen_model_gap = _cut_sum(A.dh, A.dh, A.p, B.dh, B.dh, B.p)
    old_hat = khat + r['nominal_actions']['00'] * r['E_delta_hat']
    new_hat = khat + chosen_model_gap
    pred_gain = old_hat - new_hat
    old_error, new_error = r['L']['00'] - old_hat, r['L']['10'] - new_hat
    return dict(predicted_gain=pred_gain, delta_old=old_error, delta_new=new_error,
                identity_residual=ld(r['G']['G_S']) - (pred_gain + old_error - new_error),
                oracle_costs_used=True, eligible_A05_feature=False)


def level_task(spec):
    cid, ref = spec
    started = time.monotonic()
    c = load_cell(cid)
    tables, details = [], []
    for which in 'AB':
        t, d = side_table(c, which, ref, extended=True, allow_grid=True, purpose='A04')
        tables.append(t); details.append(d)
    r = evaluate_sides(*tables, refinement=ref, dt=F(1, 120 * ref))
    physical = physical_checks(tables, details)
    diagnostic = r04_diagnostic(*tables, details, r)
    return cid, ref, r, physical, diagnostic, time.monotonic() - started


def flatten(record, ref, r, physical, diagnostic, paired, wall):
    C = float(r['C_ref'])
    anchors = record.get('anchors', [])
    output = dict(cell=record['id'], role=record.get('role', 'structural_probe'),
                  group=record.get('group', 'controls_probes'), slice=record.get('slice', ''),
                  kappa=record['kappa'], alphaA=record.get('alphaA', ''), alphaB=record.get('alphaB', ''),
                  eta=record['eta'], h_s=record['h'],
                  lambdaA=record.get('lambdaA', str(sum(map(F, record['ratesA'])) / 2) if 'ratesA' in record else ''),
                  psi=record.get('psi', ''), yA=record['yA'], yB=record['yB'],
                  targets='|'.join(str(a['target']) for a in anchors),
                  floor=any(a['bracketing'] == 'floor' for a in anchors),
                  dk1_label=record[f'label_{ref}'], refinement=ref, dt_s=r['dt_s'],
                  H=record['H_coarse'] * ref, status=r['status'], numeric_budget_met=r['numeric_budget_met'],
                  **paired, C_ref=str(r['C_ref']), R00=str(r['R']['00']),
                  a00=r['a00'], a01=r['a01'], a00_nominal=r['nominal_actions']['00'],
                  a01_nominal=r['nominal_actions']['01'], wall_s=wall)
    for name, v in r['L'].items():
        output['L' + name] = str(v)
    for name in ('E_delta', 'E_delta_hat', 'bias', 'E_pos', 'E_neg', 'E_abs_e_M', 'E_abs_I_delta', 'p_sw'):
        output[name] = str(r[name])
    output['abs_E_delta'] = str(abs(r['E_delta']))
    output['abs_bias'] = str(abs(r['bias']))
    gs = r['G']['G_S']
    output['G_S_sign'] = 'positive' if gs > 0 else 'negative' if gs < 0 else 'zero'
    for g, value in r['G'].items():
        output[g] = str(value)
        output[g + '_pct_Cref'] = 100 * float(value) / C if C > 0 else ''
        for threshold, suffix in ((.005, '005'), (.01, '010'), (.02, '020')):
            output[f'{g}_verdict_{suffix}'] = point_label(float(value), C, threshold)
    for name, value in r['e_num'].items():
        output['e_' + name] = value
    for name, endpoints in r['intervals'].items():
        output[name + '_low'], output[name + '_high'] = endpoints
    for name, values in r['quantile_intervals'].items():
        for level, endpoints in values.items():
            label = 'q' + str(int(F(level) * 100))
            output[name + '_' + label] = str(r['quantiles_' + name][level])
            output[name + '_' + label + '_low'], output[name + '_' + label + '_high'] = endpoints
    for name, value in r['unresolved_mass'].items():
        output['unresolved_' + name] = value
    for name, value in diagnostic.items():
        output['R04_' + name] = str(value)
    output.update(physical)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--allow-grid', action='store_true', required=True)
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args()
    receipt = verify()  # before any D/cost, no bypass CLI
    cfg = read(ROOT / (BASE + 'config.json'))
    if not args.run_id or Path(args.run_id).name != args.run_id or not 1 <= args.workers <= cfg['max_workers']:
        raise ValueError('invalid run ID or worker count')
    grid = read(GRID_PATH)
    records = {r['id']: r for k in ('main', 'controls', 'probes') for r in grid[k]}
    ids = cfg['controls'] + cfg['main_ids']
    tasks = [(cid, m) for cid in ids for m in cfg['pair_refinements']]
    for cid, m in tasks:
        if (records[cid][f'updates_{m}'] > cfg['updates_cap_per_cell_level'] or
                records[cid][f'peak_{m}'] > cfg['peak_bytes_cap']):
            raise MemoryError('registered per-cell budget exceeded')
    out = ROOT / 'results/A04' / args.run_id
    out.mkdir(parents=True, exist_ok=False)
    (out / 'raw').mkdir()
    write(out / 'config.json', cfg)
    write(out / 'manifest.json', dict(responsible='Doan Van Tai', **receipt,
          start_utc=datetime.now(timezone.utc).isoformat(), python=platform.python_version(),
          platform=platform.platform(), libraries={p: importlib.metadata.version(p) for p in ('numpy', 'scipy', 'mpmath')},
          longdouble_bits=np.finfo(np.longdouble).nmant + 1, seed=None, sampling_CI=False,
          workers=args.workers, requested_levels=92, heldout_evaluated=False))
    start = time.monotonic()
    results, checks = {}, []
    try:
        with multiprocessing.get_context('fork').Pool(args.workers) as pool:
            for cid, m, r, phys, diag, wall in pool.imap_unordered(level_task, tasks, chunksize=1):
                results[cid, m] = (r, phys, diag, wall)
                write(out / 'raw' / f'{cid}_m{m}.json', dict(engine=r, physical_validity=phys, R04=diag, wall_s=wall))
                v = validity_row(cid, m, r, phys, cfg)
                checks.append(v)
                csv_write(out / 'validity_partial.csv', checks)
                print(f'[VALIDITY] {cid} ref={m} hard={v["hard_pass"]} status={r["status"]} '
                      f'completed={len(checks)}/92', flush=True)
        pairs = {cid: pair(results[cid, 1][0], results[cid, 2][0]) for cid in ids}
        rows = []
        for cid in cfg['main_ids'] + cfg['controls']:
            for m in cfg['pair_refinements']:
                r, phys, diag, wall = results[cid, m]
                rows.append(flatten(records[cid], m, r, phys, diag, pairs[cid], wall))
        csv_write(out / 'cells.csv', rows)
        checks.sort(key=lambda x: (x['cell'], x['refinement']))
        for v in checks:
            v.update({k: x for k, x in pairs[v['cell']].items() if k not in ('F_pair_change', 'V_pair_change')})
        csv_write(out / 'validity.csv', checks)
        write(out / 'grading_input.json', {level: {cid: results[cid, m][0] for cid in cfg['main_ids']}
                                          for level, m in (('coarse', 1), ('fine', 2))})
        hard_failed = [f'{v["cell"]}/m{v["refinement"]}' for v in checks if not v['hard_pass']]
        holds = [f'{v["cell"]}/m{v["refinement"]}' for v in checks if v['status'] != 'BOUNDED']
        flagged = [cid for cid in ids if pairs[cid]['pair_flag']]
        status = dict(status='FAIL' if hard_failed else 'PASS_WITH_HOLD' if holds else 'PASS',
                      completed_levels=len(checks), main_cells=38, controls_probes=8,
                      hard_failures=hard_failed, hold_levels=holds, dt_flagged_cells=flagged,
                      max_e_over_Cref_lower=max(v['max_e_over_Cref_lower'] for v in checks if v['max_e_over_Cref_lower'] != ''),
                      max_unresolved_mass=max(v['unresolved_' + name] for v in checks for name in ('oracle', 'M0', 'D22')),
                      max_pair_change_upper_ratio=max(v['max_change_upper_over_Cref_fine'] for v in checks
                                                      if v['max_change_upper_over_Cref_fine'] != ''),
                      end_utc=datetime.now(timezone.utc).isoformat(), wall_s=time.monotonic()-start,
                      heldout_evaluated=False, contrasts_displayed=False, card_scored=False)
        write(out / 'validity_status.json', status)
        write(out / 'run_status.json', status)
        files = sorted(p for p in out.rglob('*') if p.is_file())
        write(out / 'output_hashes.json', {str(p.relative_to(out)): sha(p) for p in files})
        print('[VALIDITY] ' + json.dumps(status, ensure_ascii=False), flush=True)
        if hard_failed:
            raise ArithmeticError('hard validity failed; preserve outputs, no scoring/discovery')
    except Exception as exc:
        write(out / 'failure.json', dict(status='FAIL', error=repr(exc), traceback=traceback.format_exc(),
              completed_levels=len(results), wall_s=time.monotonic()-start, heldout_evaluated=False))
        raise


if __name__ == '__main__':
    main()
