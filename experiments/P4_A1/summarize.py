"""Write-once descriptive summary after a full PASS: rho* by the frozen rule, readings, manifests.

rho* is selected ONLY on READY (status PASS) points of the support named in the prereg, with the
author-adopted target controller, using the unchanged L4.4 helpers (select_rho / describe / reading).
NOT_READY points are counted and listed, never silently dropped. For SV supports this also writes the
DISCOVERY_NATIVE row tables and manifest that experiments/P4_05_candidates/screen.py expects.
"""
import argparse
import csv
from fractions import Fraction as F
from statistics import median

from experiments.P4_03_map_audit.common import ROOT, sha, require, write_once
from experiments.P4_04_baseline.analysis import select_rho, describe, reading
from .config import RUNS, load, verify_run
from .checks import manifest_row, neighbours
from .run import verify_saved_comparison


def reading_sv(descs, rule):
    gs = [F(d['GS_theta_pctC_exact']) for d in descs]
    d00 = [F(d['deltaL00']) for d in descs]
    narrow = median(gs) < F(rule['median_GS_theta_pctC_below']) and median(d00) < 0
    return dict(region='SV', median_GS_theta_pctC=float(median(gs)), median_deltaL00=float(median(d00)),
                controller_improved=median(d00) < 0, descriptive_narrow=narrow,
                statement=rule['statement_if_narrow'] if narrow else rule['statement_otherwise'])


def table(path, rows):
    if rows:
        with path.open('x', newline='') as stream:
            w = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
            w.writeheader(); w.writerows(rows)


def main():
    p = argparse.ArgumentParser(); p.add_argument('--run', required=True); a = p.parse_args()
    cfg = verify_run(a.run); out = ROOT / cfg['output']
    full = load((out / 'full_summary.json').relative_to(ROOT))
    require(full['status'] == 'PASS', 'full stage HOLD: no selection, no manifest')
    dest = out / 'summary'
    require(not dest.exists(), 'summary exists; never overwrite')
    main_lv = tuple(cfg['levels'][0])
    records, rows = {}, {}
    for c in cfg['cases']:
        folder = out / 'native' / c['id']
        records[c['id']] = load((folder / 'comparison.json').relative_to(ROOT))
        verify_saved_comparison(a.run, cfg, c, False, folder, records[c['id']])
        rows[c['id']] = {lv: load((folder / f'level_{lv[0]}_{lv[1]}.json').relative_to(ROOT))
                         for lv in [main_lv, *neighbours(main_lv)]}
    summary = dict(run_id=a.run, responsible='Doan Van Tai', supports={}, CF_outcomes=0, G_level='G1',
                   card_v2_verdict_unchanged=True, prereg_sha256=sha(ROOT / RUNS / a.run / 'prereg.json'))
    freeze, ledger, described, manifests = {}, [], [], {}
    for name, spec in cfg['supports'].items():
        members = [c for c in cfg['cases'] if name in c['supports']]
        ready = [c for c in members if records[c['id']]['status'] == 'PASS']
        not_ready = [c['id'] for c in members if records[c['id']]['status'] == 'NOT_READY']
        info = dict(N=len(members), N_ready=len(ready), not_ready=not_ready)
        if spec.get('target'):
            main_rows = [rows[c['id']][main_lv] for c in ready]
            rho, scores = select_rho(main_rows, spec['target'])
            ds = [dict(support=name, **describe(r, rho, spec['target']),
                       deltaL00=next(b for b in r['baseline'] if F(b['rho']) == F(rho))['deltaL00']) for r in main_rows]
            described += ds
            info.update(rho_star=rho, target=spec['target'], scores_float={k: float(v) for k, v in scores.items()},
                        reading=reading_sv(ds, cfg['reading']['SV']) if spec.get('reading') == 'SV'
                        else reading(spec['reading'], ds))
            freeze[name] = dict(rho_star=rho, target=spec['target'], N_ready=len(ready), N_not_ready=len(not_ready))
        if spec.get('manifest_role'):
            mrows = [manifest_row(c, rows[c['id']], main_lv, records[c['id']].get('readiness_reasons', [])) for c in members]
            path = dest / f'native_rows_{name}.json'
            manifests[spec['manifest_role']] = (path, mrows)
        summary['supports'][name] = info
        for c in members:
            r = records[c['id']]
            ledger.append(dict(id=c['id'], support=name, status=r['status'], reasons='|'.join(r.get('readiness_reasons', [])),
                               pilot_flags='|'.join(r.get('pilot_flags', [])),
                               raw_validity_main=str(r['raw_flags_report_only'][f'{main_lv[0]}_{main_lv[1]}']['validity_errors'])))
    dest.mkdir(parents=True)
    write_once(dest / 'summary.json', summary)
    table(dest / 'case_ledger.csv', ledger)
    table(dest / 'selected_baseline.csv', described)
    if freeze:
        write_once(ROOT / RUNS / a.run / 'rho_freeze.json', dict(
            responsible='Doan Van Tai', status='FROZEN_BY_PREDECLARED_SELECTION_RULE', run_id=a.run,
            supports=freeze, prereg_sha256=summary['prereg_sha256'], not_CF_verdict=True))
    if manifests:
        import json
        hashes = {}
        for role, (path, mrows) in manifests.items():
            write_once(path, mrows); hashes[str(path.relative_to(ROOT))] = sha(path)
        write_once(dest / 'native_manifest.json', dict(
            source_kind='DISCOVERY_NATIVE_BUNDLE_V1', run_id=a.run,
            rows={role: str(path.relative_to(ROOT)) for role, (path, _) in manifests.items()},
            source_sha256=hashes, note='NOT_READY points appear with r1_ready/arithmetic_ready False -> UNRESOLVED'))
    print({k: (v['N'], v['N_ready'], v.get('rho_star'), (v.get('reading') or {}).get('descriptive_narrow'))
           for k, v in summary['supports'].items()}, flush=True)


if __name__ == '__main__':
    main()
