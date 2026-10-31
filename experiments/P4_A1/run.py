"""A1 runner: control -> benchmark -> budget -> full, config-driven by runs/<RUN_ID>/prereg.json.

python -m experiments.P4_A1.run control   --run RUN_ID
python -m experiments.P4_A1.run benchmark --run RUN_ID
python -m experiments.P4_A1.run budget    --run RUN_ID   (then COMMIT budget.json before full)
python -m experiments.P4_A1.run full      --run RUN_ID

Stop policy (checks.stop_decision): BUG / execution / guard -> stop scheduling at once.
NOT_READY and pilot flags -> continue, stop only when the per-support cap can no longer be met.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import os
from pathlib import Path
import resource
import subprocess
import time

from experiments.P4_03_map_audit.common import ROOT, sha, git, require, write_once
from .config import RUNS, load, verify_run, guard_case
from .checks import (row_readiness, baseline_readiness, audit_compare, classify, stop_decision,
                     cross_route_report, neighbours)


def out_dir(cfg):
    path = ROOT / cfg['output']
    path.mkdir(parents=True, exist_ok=True)
    ignore = path / '.gitignore'
    if not ignore.exists():
        ignore.write_text('native_cache/\n')
    return path


def fingerprint(run_id):
    return sha(ROOT / RUNS / run_id / 'prereg.json')


def budget_receipt(cfg):
    path = Path(cfg['output']) / 'budget.json'
    require((ROOT / path).exists(), 'full run needs budget receipt')
    require(git('show', 'HEAD:' + str(path)) == (ROOT / path).read_bytes(), 'commit budget.json before full')
    receipt = load(path)
    require(receipt['status'] == 'AUTHORIZED_BY_PREREG_RULE', 'budget not authorized')
    return receipt


def case_of(cfg, cid):
    if cid == cfg['control']['id']:
        return cfg['control'], True
    return next(c for c in cfg['cases'] if c['id'] == cid), False


def validate_saved_row(row, case, lv, fp):
    require(row.get('a1_prereg_sha256') == fp and row.get('id') == case['id'] and
            row.get('parameters') == case['parameters'] and
            (row.get('K'), row.get('ref')) == lv and row.get('CF_computed') is False,
            'stale or foreign resumed row (receipt/identity/level/CF flag)')


def case_record(cfg, case, control, rows, fp):
    main = tuple(cfg['levels'][0]); cid = case['id']
    cpu = sum(r.get('call_cpu_seconds', 0) for r in rows.values())
    bugs = sorted({b for r in rows.values() for b in r.get('a1_bug_reasons', [])})
    failed = [r for r in rows.values() if r['status'] != 'COMPLETED']
    if failed:
        record = dict(status='HOLD_EXECUTION', reasons=[r.get('error', r['status']) for r in failed])
    elif bugs:
        record = dict(status='BUG', bug_reasons=bugs)
    elif control:
        ok = rows[main].get('zero_action_certificate') is True
        record = dict(status='PASS' if ok else 'BUG', bug_reasons=[] if ok else ['u0_certificate_missing'])
    else:
        native_reasons = row_readiness(rows, main)
        base_reasons, refinement = baseline_readiness(rows, main, cfg['rho'])
        readiness = native_reasons + base_reasons
        audits = [audit_compare(a, rows, main) for a in cfg.get('aliases', []) if a['native_id'] == cid] \
            if cfg.get('audit_pilot') else []
        record = dict(status=classify([], readiness), bug_reasons=[], readiness_reasons=readiness,
                      native_readiness_reasons=native_reasons, baseline_readiness_reasons=base_reasons,
                      baseline_refinement=refinement,
                      pilot_flags=sorted({f for a in audits for f in a['pilot_flags']}), audit=audits,
                      cross_route_main=cross_route_report(rows[main]),
                      raw_flags_report_only={f'{lv[0]}_{lv[1]}': r['raw_flags_report_only'] for lv, r in rows.items()})
    record.update(native_id=cid, supports=case.get('supports', []), cpu_seconds=cpu, a1_prereg_sha256=fp)
    return record


def verify_saved_comparison(run_id, cfg, case, control, folder, saved):
    fp = fingerprint(run_id)
    require(saved.get('a1_prereg_sha256') == fp and saved.get('native_id') == case['id'],
            'comparison from another prereg/case')
    rows = {}
    main = tuple(cfg['levels'][0])
    for lv in ([main] if control else [main, *neighbours(main)]):
        path = folder / f'level_{lv[0]}_{lv[1]}.json'
        if not path.exists():
            break
        row = load(path.relative_to(ROOT)); validate_saved_row(row, case, lv, fp); rows[lv] = row
        if row['status'] != 'COMPLETED' or row.get('a1_bug_reasons'):
            break
    require(rows and case_record(cfg, case, control, rows, fp) == saved, 'cached comparison changed or rows incomplete')
    return saved


def worker(run_id, cid):
    cfg = verify_run(run_id)
    case, control = case_of(cfg, cid)
    guard_case(case, cfg, control=control)
    out = out_dir(cfg)
    for stage in ('benchmark', 'full'):
        if (out / f'{stage}_summary.json').exists():
            require(load((out / f'{stage}_summary.json').relative_to(ROOT))['status'] == 'PASS',
                    'previous stage HOLD: no new physical calls')
    if not control:
        require(load((out / 'control_summary.json').relative_to(ROOT))['status'] == 'PASS', 'control not passed')
        if cid not in cfg['benchmark_ids']:
            budget_receipt(cfg)
    lim = cfg['resources']
    resource.setrlimit(resource.RLIMIT_CPU, (lim['case_cpu_seconds'], lim['case_cpu_seconds'] + 5))
    resource.setrlimit(resource.RLIMIT_AS, (lim['address_space_bytes'], lim['address_space_bytes']))
    from .evaluate import evaluate_level            # every guard above runs BEFORE the engine import
    main = tuple(cfg['levels'][0])
    requested = [main] if control else [main, *neighbours(main)]
    folder = out / ('controls' if control else 'native') / cid
    folder.mkdir(parents=True, exist_ok=True)
    fp = fingerprint(run_id); rows = {}
    for lv in requested:
        path = folder / f'level_{lv[0]}_{lv[1]}.json'
        if path.exists():
            row = load(path.relative_to(ROOT))
            validate_saved_row(row, case, lv, fp)
        else:
            begin_cpu = time.process_time()
            try:
                row = evaluate_level(case, lv, out / 'native_cache', cfg['rho'])
                row['status'] = 'COMPLETED'
            except Exception as exc:
                row = dict(id=cid, K=lv[0], ref=lv[1], status='HOLD_EXECUTION', error=f'{type(exc).__name__}: {exc}',
                           call_cpu_seconds=time.process_time()-begin_cpu)
            row.update(parameters=case['parameters'], a1_prereg_sha256=fp, CF_computed=False)
            write_once(path, row)
        rows[lv] = row
        if row['status'] != 'COMPLETED' or row.get('a1_bug_reasons'):
            break  # no further physical call after a confirmed BUG/execution error
    record = case_record(cfg, case, control, rows, fp)
    target = folder / 'comparison.json'
    if target.exists():
        require(load(target.relative_to(ROOT)) == record, 'comparison changed on resume')
    else:
        write_once(target, record)
    print(cid, record['status'], record.get('bug_reasons') or record.get('readiness_reasons') or '', flush=True)
    return 0 if record['status'] in ('PASS', 'NOT_READY') else 1


def launch(run_id, cfg, cid):
    case, control = case_of(cfg, cid)
    guard_case(case, cfg, control=control)
    folder = ROOT / cfg['output'] / ('controls' if control else 'native') / cid
    target = folder / 'comparison.json'
    if target.exists():
        saved = load(target.relative_to(ROOT))
        return verify_saved_comparison(run_id, cfg, case, control, folder, saved)
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    cmd = [str(ROOT / '.venv/bin/python'), '-m', 'experiments.P4_A1.run', 'worker', '--run', run_id, '--case', cid]
    try:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True,
                              timeout=cfg['resources']['case_wall_seconds'])
        log = proc.stdout + proc.stderr
        failure = dict(native_id=cid, supports=case.get('supports', []), status='HOLD_EXECUTION',
                       exit_code=proc.returncode, error=proc.stderr[-4000:])
    except subprocess.TimeoutExpired as exc:
        log = str(exc); failure = dict(native_id=cid, supports=case.get('supports', []), status='HOLD_RESOURCE_TIMEOUT')
    folder.mkdir(parents=True, exist_ok=True)
    attempts = list(folder.glob('worker_*.log'))
    with (folder / f'worker_{len(attempts) + 1:02d}.log').open('x') as stream:
        stream.write(log)
    if not target.exists():
        failure['a1_prereg_sha256'] = fingerprint(run_id)
        write_once(target, failure)
    return load(target.relative_to(ROOT))


def planned_by_support(cfg, ids):
    counts = {}
    for c in cfg['cases']:
        for s in c['supports']:
            counts[s] = counts.get(s, 0) + 1
    return counts


def control(run_id, cfg):
    target = out_dir(cfg) / 'control_summary.json'
    if not target.exists():
        write_once(target, launch(run_id, cfg, cfg['control']['id']))
    result = load(target.relative_to(ROOT)); print(result, flush=True)
    return result['status'] != 'PASS'


def run_stage(run_id, cfg, stage):
    out = out_dir(cfg)
    require(load((out / 'control_summary.json').relative_to(ROOT))['status'] == 'PASS', 'control HOLD')
    if stage == 'full':
        budget_receipt(cfg)
    target = out / f'{stage}_summary.json'
    if target.exists():
        result = load(target.relative_to(ROOT)); print(result['status'], flush=True)
        return result['status'] != 'PASS'
    ids = cfg['benchmark_ids'] if stage == 'benchmark' else [c['id'] for c in cfg['cases']]
    planned = planned_by_support(cfg, ids)
    begin = time.monotonic(); results = []; reasons = []
    workers = 1 if stage == 'benchmark' else cfg['resources']['workers']
    pending_ids = iter(ids)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        active = {}

        def schedule():
            cid = next(pending_ids, None)
            if cid is not None:
                active[pool.submit(launch, run_id, cfg, cid)] = cid
        for _ in range(workers):
            schedule()
        while active:
            done, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in done:
                cid = active.pop(future)
                try:
                    result = future.result()
                except Exception as exc:
                    case, _ = case_of(cfg, cid)
                    result = dict(native_id=cid, supports=case['supports'], status='HOLD_GUARD',
                                  error=f'{type(exc).__name__}: {exc}')
                results.append(result)
                print(stage, cid, result['status'], round(result.get('cpu_seconds', 0), 2), flush=True)
            reasons = stop_decision(results, planned, cfg['caps'])
            if sum(r.get('cpu_seconds', 0) for r in results) > cfg['resources']['cpu_cap_hours'] * 3600:
                reasons.append('cpu_cap')
            if not reasons:
                while len(active) < workers:
                    before = len(active); schedule()
                    if len(active) == before:
                        break
    ok = not reasons and len(results) == len(ids)
    summary = dict(stage=stage, status='PASS' if ok else 'HOLD', planned=len(ids), completed=len(results),
                   counts={s: sum(r['status'] == s for r in results) for s in {r['status'] for r in results}},
                   stop_reasons=reasons, cpu_seconds=sum(r.get('cpu_seconds', 0) for r in results),
                   wall_seconds=time.monotonic() - begin, results=results, a1_prereg_sha256=fingerprint(run_id))
    write_once(target, summary)
    print({k: summary[k] for k in ('stage', 'status', 'planned', 'completed', 'counts', 'stop_reasons')}, flush=True)
    return not ok


def budget(run_id, cfg):
    out = out_dir(cfg)
    bench = load((out / 'benchmark_summary.json').relative_to(ROOT))
    require(bench['status'] == 'PASS', 'benchmark HOLD: no budget')
    by_id = {r['native_id']: r for r in bench['results']}
    estimate = {}
    for support, n in planned_by_support(cfg, None).items():
        measured = [by_id[c['id']]['cpu_seconds'] for c in cfg['cases'] if c['id'] in by_id and support in c['supports']]
        require(measured, 'every support needs a benchmark case: ' + support)
        estimate[support] = dict(max_bundle_cpu_seconds=max(measured), N=n, conservative_cpu_seconds=1.5 * max(measured) * n)
    total = sum(e['conservative_cpu_seconds'] for e in estimate.values()) + \
        load((out / 'control_summary.json').relative_to(ROOT))['cpu_seconds']
    cap = cfg['resources']['cpu_cap_hours']
    receipt = dict(status='AUTHORIZED_BY_PREREG_RULE' if total <= cap * 3600 else 'HOLD_BUDGET',
                   rule='1.5 * max benchmark bundle CPU per support * N(support) + control',
                   supports=estimate, estimated_cpu_hours=total / 3600, cap_cpu_hours=cap,
                   a1_prereg_sha256=fingerprint(run_id))
    write_once(out / 'budget.json', receipt)
    print(receipt, flush=True)
    return receipt['status'] != 'AUTHORIZED_BY_PREREG_RULE'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('step', choices=['control', 'benchmark', 'budget', 'full', 'worker'])
    p.add_argument('--run', required=True); p.add_argument('--case')
    a = p.parse_args()
    if a.step == 'worker':
        return worker(a.run, a.case)
    cfg = verify_run(a.run)
    if a.step == 'control':
        return control(a.run, cfg)
    if a.step == 'budget':
        return budget(a.run, cfg)
    return run_stage(a.run, cfg, a.step)


if __name__ == '__main__':
    raise SystemExit(main())
