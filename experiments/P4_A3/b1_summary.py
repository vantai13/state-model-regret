"""Final baseline sensitivity check, simplified at the user's request.

Keep all 90 cases. At each of three fixed levels apply the unchanged DL-104
selection/reading helpers. Same rho and same narrow decision => STABLE, else
UNRESOLVED. No engine calls and no follow-up numerical escalation.
"""
import argparse
import csv
from fractions import Fraction as F
import json
import math
from pathlib import Path

from experiments.P4_03_map_audit.common import ROOT, sha, require, write_once
from experiments.P4_04_baseline.analysis import select_rho, describe, reading
from experiments.P4_A1.config import RUNS, load, verify_run
from experiments.P4_A1.run import validate_saved_row, verify_saved_comparison
from experiments.P4_A2.guards import reproduction

RUN_ID = 'L44_A3'
LEVELS = ((640, 4), (320, 4), (640, 2))
RHOS = ['0', '1/200', '1/100', '1/50', '1/20']
A1_NATIVE = Path('results/lessons/l4_4/a1/native')


def fingerprint():
    return sha(ROOT / RUNS / RUN_ID / 'prereg.json')


def validate_protocol(cfg):
    old = load(RUNS / 'L44_A1/prereg.json')
    require(cfg['run_id'] == RUN_ID and cfg['cases'] == old['cases'], 'must keep the same 90 cases')
    require(len(cfg['cases']) == 90 and len({tuple(c['key']) for c in cfg['cases']}) == 90, '90 unique keys required')
    require(cfg['levels'] == [list(lv) for lv in LEVELS] and cfg['rho'] == RHOS, 'fixed levels/rho required')
    require(cfg['supports'] == old['supports'] and cfg['benchmark_ids'] == old['benchmark_ids'], 'support/reference changed')
    require(F(cfg['caps']['max_not_ready_fraction']) == 1, 'B1 keeps all NOT_READY points')


def level_reading(rows, target, support):
    rho, scores = select_rho(rows, target)
    return dict(rho_star=rho, scores_exact={r: str(s) for r, s in scores.items()},
                reading=reading(support, [describe(row, rho, target) for row in rows]))


def verdict(per_level):
    require(set(per_level) == {f'{k}_{r}' for k, r in LEVELS}, 'all three levels required')
    if len({v['rho_star'] for v in per_level.values()}) != 1:
        return 'UNRESOLVED_RHO_DEPENDS_ON_NUMERICS'
    if len({v['reading']['descriptive_narrow'] for v in per_level.values()}) != 1:
        return 'UNRESOLVED_READING_DEPENDS_ON_NUMERICS'
    return 'STABLE'


def replay(cfg):
    """One fixed reference subset: all four benchmark cases, 12 saved rows."""
    validate_protocol(cfg)
    results = []
    for cid in cfg['benchmark_ids']:
        case = next(c for c in cfg['cases'] if c['id'] == cid)
        for lv in LEVELS:
            name = f'level_{lv[0]}_{lv[1]}.json'
            path = ROOT / cfg['output'] / 'native' / cid / name
            require(path.exists(), 'missing reference row: ' + str(path))
            new = load(path)
            validate_saved_row(new, case, lv, fingerprint())
            require(new['status'] == 'COMPLETED' and not new['a1_bug_reasons'], 'reference row failed')
            result = reproduction(load(A1_NATIVE / cid / name), new)
            require(result['reparsed_significant_bits_equal'], 'REPRODUCTION_MISMATCH: ' + cid + '/' + name)
            results.append(dict(id=cid, level=list(lv), equal=True))
    require(len(results) == 12, '12 reference rows required; zero is not PASS')
    return dict(status='PASS', rows_compared=12, rows_equal=12,
                prereg_sha256=fingerprint(), rows=results)


def load_results(cfg):
    validate_protocol(cfg)
    out = ROOT / cfg['output']
    full = load(out / 'full_summary.json')
    ids = {c['id'] for c in cfg['cases']}
    require(full['status'] == 'PASS' and full['completed'] == 90 and
            len(full['results']) == 90 and {r['native_id'] for r in full['results']} == ids and
            full['a1_prereg_sha256'] == fingerprint(), 'full 90-case run not complete: no selection')
    sample = load(out / 'replay.json')
    require(sample == replay(cfg), 'reference replay receipt changed')
    rows, records = {}, {}
    for case in cfg['cases']:
        folder = out / 'native' / case['id']
        records[case['id']] = verify_saved_comparison(RUN_ID, cfg, case, False, folder, load(folder / 'comparison.json'))
        require(records[case['id']]['status'] in ('PASS', 'NOT_READY'), 'BUG/execution failure: no reading')
        rows[case['id']] = {}
        for lv in LEVELS:
            row = load(folder / f'level_{lv[0]}_{lv[1]}.json')
            require(row['status'] == 'COMPLETED' and row['dt'] == str(F(1, 120*lv[1])) and
                    [b['rho'] for b in row['baseline']] == RHOS, 'incomplete or wrong numerical level')
            rows[case['id']][lv] = row
    return rows, records


def summarize():
    cfg = verify_run(RUN_ID)
    out = ROOT / cfg['output']; dest = out / 'summary'
    require(not dest.exists(), 'summary already exists: never overwrite or use the A1 subset summarizer')
    rows, records = load_results(cfg)
    control = load(out / 'control_summary.json')
    require(control['status'] == 'PASS', 'control not PASS')
    summary = dict(run_id=RUN_ID, responsible='Doan Van Tai', status='COMPLETED',
                   branch='B1_CLAIM_LEVEL_ROBUSTNESS', prereg_sha256=fingerprint(),
                   replay_rows_equal=12, CF_outcomes=0, G_level='G1', supports={},
                   cpu_seconds_including_control=math.fsum([control['cpu_seconds'], *[
                       row['call_cpu_seconds'] for case in rows.values() for row in case.values()]]),
                   limitation='Stability only across the three fixed levels; not per-point convergence or an error certificate',
                   stop='Final numerical sensitivity check. No A4 or extra level to obtain STABLE.')
    csv_rows, frozen = [], {}
    for name, spec in cfg['supports'].items():
        members = [c for c in cfg['cases'] if name in c['supports']]
        per = {f'{k}_{r}': level_reading([rows[c['id']][(k,r)] for c in members], spec['target'], spec['reading'])
               for k,r in LEVELS}
        status = verdict(per)
        nr = [c['id'] for c in members if records[c['id']]['status'] == 'NOT_READY']
        rho = per['640_4']['rho_star'] if status == 'STABLE' else None
        summary['supports'][name] = dict(N=len(members), N_ready=len(members)-len(nr), not_ready=nr,
                                        target=spec['target'], verdict=status, rho_star=rho, per_level=per)
        frozen[name] = dict(status=status, rho_star=rho, target=spec['target'], N=len(members))
        for lv, result in per.items():
            rd = result['reading']
            csv_rows.append(dict(support=name, N=len(members), N_not_ready=len(nr), level=lv,
                rho_star=result['rho_star'], narrow=rd['descriptive_narrow'], verdict=status,
                median_R_M=rd.get('median_recovery'), median_abs_GS_theta_pctC=rd.get('median_abs_GS_theta_pctC'),
                median_deltaL10_packet_s=rd.get('median_deltaL10'), claim_readiness=rd.get('claim_readiness'),
                undefined_R_M=rd.get('undefined')))
    dest.mkdir()
    write_once(dest / 'b1_summary.json', summary)
    with (dest / 'level_summary.csv').open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(csv_rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(csv_rows)
    write_once(ROOT / RUNS / RUN_ID / 'rho_freeze.json', dict(run_id=RUN_ID,
               status='FROZEN_BY_PREDECLARED_B1_RULE', supports=frozen, prereg_sha256=fingerprint(), not_CF_verdict=True))
    for name, result in summary['supports'].items():
        print(name, result['verdict'], {lv:(v['rho_star'],v['reading']['descriptive_narrow']) for lv,v in result['per_level'].items()})
    return 0


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('step', choices=['replay', 'summarize'])
    args = parser.parse_args()
    if args.step == 'summarize':
        return summarize()
    cfg = verify_run(RUN_ID); result = replay(cfg)
    write_once(ROOT / cfg['output'] / 'replay.json', result)
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
