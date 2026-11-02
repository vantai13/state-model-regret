"""Doan Van Tai — L5.1 runner, implemented with AI assistance under delegation.

The L4.9 plan, engine and scorers stay frozen. Strict no-retry: an attempted
panel directory is never resumed, even when its last row was not saved.
Anchor and panel share the same guarded subprocess/evaluation/write path.
"""
import argparse
import ctypes
import hashlib
import json
import math
import os
import re
import resource
import signal
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as F
from pathlib import Path

os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')

from experiments.P4_03_map_audit.common import ROOT, canonical, git, require

PROTOCOL = ROOT / 'experiments/P4_09_stationary/protocol.json'
LOCK = ROOT / 'notes/design/analysis_plan_v1.lock.json'
PREDICTIONS = ROOT / 'results/lessons/l4_9_v2/future_predictions.jsonl'
OUT = ROOT / 'results/phase5'
CACHE = Path.home() / '.cache/state-model-regret/phase5'
BASE = '271819f90e4ddfe9b75f0a5c95b4b295ad27ba05'
SOURCES = ('experiments/P5_panel/__init__.py', 'experiments/P5_panel/run.py', 'tests/test_p5_panel.py')
LEVELS = ((640, 4), (320, 4), (640, 2))
MAIN, THRESHOLD = LEVELS[0], F(1, 200)
BUDGET, CALL_CPU_CAP, CALL_WALL_CAP = 28800, 1800, 3600
RESERVE = 1.0  # stop conservatively before exhausting CPU; not a metric tolerance
RUNS = ('L43_A1_SV', 'L44_A3', 'SUB_BOX')
ANCHORS = {
    'P43_0379': ('results/lessons/l4_3/a1_sv/native/P43_0379', 'DOES_NOT_MEET'),
    'P44_025': ('results/lessons/l4_4/a3/native/P44_025', 'MEETS'),
}
FIELDS = ('losses', 'cost_error', 'Cref', 'G_S', 'G_M', 'G_SM', 'Gamma', 'G_S_M1', 'G_M_S1', 'normalized_error')


def load(path):
    return json.loads(Path(path).read_text())


def write_once(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(obj, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def check_frozen():
    require(LOCK.read_bytes() == git('show', BASE + ':notes/design/analysis_plan_v1.lock.json'), 'LOCK_CHANGED')
    for name, digest in load(LOCK)['files'].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'FROZEN_FILE_CHANGED: ' + name)
    proto = load(PROTOCOL)
    panel, levels = proto['future_panel'], tuple(map(tuple, proto['future_levels']))
    require([p['id'] for p in panel] == [f'P5_{i:02d}' for i in range(1, 13)], 'PANEL_ORDER')
    require(levels == LEVELS and proto['future_CPU_budget_seconds'] == BUDGET, 'LEVELS_OR_BUDGET')
    from experiments.P4_09_stationary.discovery import forbidden
    blocked = forbidden()
    require(all(canonical(p['parameters']) not in blocked for p in panel), 'CF_OR_SEALED_COLLISION')
    return panel, levels


def gate_record():
    path = ROOT / 'notes/02_decision_log.md'
    require(path.read_bytes() == git('show', 'HEAD:notes/02_decision_log.md'), 'UNCOMMITTED_GATE')
    matches = re.findall(r'<!-- P5_GATE4\s+(.*?)\s*-->', path.read_text(), re.S)
    require(len(matches) == 1, 'GATE4_DECLARATION_REQUIRED')
    gate = json.loads(matches[0])
    require(gate['status'] == 'GO' and gate['policy'] == 'STRICT_NO_RETRY', 'GATE4_NOT_GO')
    require((gate['call_cpu_cap'], gate['call_wall_cap']) == (CALL_CPU_CAP, CALL_WALL_CAP), 'CAP_CHANGED')
    commit = gate['runner_commit']
    git('merge-base', '--is-ancestor', commit, 'HEAD')
    for source in SOURCES:
        require((ROOT / source).read_bytes() == git('show', commit + ':' + source), 'RUNNER_CHANGED: ' + source)
    report_path = 'results/phase5/gate4_anchor/report.json'
    report = load(ROOT / report_path)
    require((ROOT / report_path).read_bytes() == git('show', 'HEAD:' + report_path), 'UNCOMMITTED_ANCHOR')
    require(report['status'] == 'PASS' and report['runner_commit'] == commit, 'ANCHOR_NOT_VALID_FOR_RUNNER')
    raw = ROOT / 'results/phase5/gate4_anchor/P43_0379_level_640_4.json'
    require(hashlib.sha256(raw.read_bytes()).hexdigest() == report['replay_sha256'], 'ANCHOR_ROW_CHANGED')
    return gate


def preflight(*, panel_run=False):
    panel, levels = check_frozen()
    from experiments.P4_A1.config import verify_run
    from experiments.P4_03_map_audit.common import verify_prereg
    for name in RUNS:
        verify_run(name)
    verify_prereg()
    for name in SOURCES:
        require((ROOT / name).read_bytes() == git('show', 'HEAD:' + name), 'UNCOMMITTED_RUNNER: ' + name)
    require(not git('status', '--porcelain', '--untracked-files=no').strip(), 'TRACKED_TREE_DIRTY')
    if panel_run:
        gate_record()
    return dict(panel=panel, levels=levels, commit=git('rev-parse', 'HEAD').decode().strip())


def saved_levels(cid):
    return {lv: load(ROOT / ANCHORS[cid][0] / f'level_{lv[0]}_{lv[1]}.json') for lv in LEVELS}


def row_path(out, pid, level):
    return Path(out) / 'panel' / pid / f'level_{level[0]}_{level[1]}.json'


def evaluate(point, level, cache):
    """The only native call; caller owns status/parameters and checks returned identity."""
    from experiments.R3R_14_lean_close import engine
    engine.configure()
    row = engine.evaluate_level(point['id'], point['parameters'], *level, cache)
    require((row['id'], row['K'], row['ref']) == (point['id'], *level), 'ENGINE_ROW_IDENTITY')
    require(row['CF_computed'] is False, 'UNEXPECTED_CF')
    return dict(row, status='COMPLETED', parameters=point['parameters'])


def worker(pid, level, kind, cpu_limit, reservation=None):
    require(0 < cpu_limit <= CALL_CPU_CAP, 'INVALID_CPU_CAP')
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, math.ceil(cpu_limit)), max(2, math.ceil(cpu_limit) + 1)))
    ctx = preflight(panel_run=kind == 'panel')  # all guards BEFORE importing the evaluator
    if kind == 'anchor':
        require(pid == 'P43_0379' and level == MAIN, 'UNREGISTERED_ANCHOR')
        point = dict(id=pid, parameters=saved_levels(pid)[MAIN]['parameters'])
    else:
        require(kind == 'panel' and level in LEVELS, 'UNREGISTERED_CALL')
        point = next(p for p in ctx['panel'] if p['id'] == pid)
    from experiments.P4_09_stationary.discovery import forbidden
    require(canonical(point['parameters']) not in forbidden(), 'CF_OR_SEALED_COLLISION')
    expected = (OUT / 'gate4_anchor/P43_0379_level_640_4.json') if kind == 'anchor' else row_path(OUT, pid, level)
    require(reservation is not None and expected.exists(), 'PARENT_RESERVATION_REQUIRED')
    require(os.fstat(reservation).st_ino == expected.stat().st_ino and expected.stat().st_size == 0,
            'INVALID_PARENT_RESERVATION')
    json.dump(evaluate(point, level, CACHE / kind), sys.stdout, allow_nan=False)
    sys.stdout.flush()


def group_cpu(pgid):
    total = 0.0
    for folder in Path('/proc').iterdir():
        if not folder.name.isdigit():
            continue
        try:
            fields = (folder / 'stat').read_text().rsplit(')', 1)[1].split()
            if int(fields[2]) == pgid:
                total += sum(int(fields[i]) for i in (11, 12, 13, 14)) / os.sysconf('SC_CLK_TCK')
        except (OSError, ValueError, IndexError):
            pass
    return total


def launch(point, level, path, *, cpu_limit, kind='panel', wall_limit=CALL_WALL_CAP):
    """Reserve output BEFORE the call; an unsaved outcome cannot silently be retried.

    Parent measures all child/descendant CPU, monitors the whole process group,
    and writes one completed/error record. No scientific values reach the terminal.
    """
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start, self_start = time.monotonic(), time.process_time()
    preflight(panel_run=kind == 'panel')
    # Reap orphaned compiler/worker children too, including when the worker is killed.
    require(ctypes.CDLL(None).prctl(36, 1, 0, 0, 0) == 0, 'SUBREAPER_REQUIRED')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    proc, error, status = None, None, 'COMPLETED'
    with path.open('x') as target, tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            spent = resource.getrusage(resource.RUSAGE_CHILDREN)
            guard_cpu = spent.ru_utime + spent.ru_stime - before.ru_utime - before.ru_stime
            require(guard_cpu + time.process_time() - self_start < cpu_limit, 'CPU_LIMIT_IN_PREFLIGHT')
            proc = subprocess.Popen([sys.executable, '-m', 'experiments.P5_panel.run', 'worker', point['id'],
                                     str(level[0]), str(level[1]), kind, str(cpu_limit), str(target.fileno())],
                                    cwd=ROOT, env=env, stdout=stdout, stderr=stderr, start_new_session=True,
                                    pass_fds=(target.fileno(),))
            while proc.poll() is None:
                # Include this launch's guards, completed descendants, active group and controller.
                done = resource.getrusage(resource.RUSAGE_CHILDREN)
                completed_cpu = done.ru_utime + done.ru_stime - before.ru_utime - before.ru_stime
                if completed_cpu + group_cpu(proc.pid) + time.process_time() - self_start >= cpu_limit:
                    status = 'RESOURCE_CPU'; break
                if time.monotonic() - start >= wall_limit:
                    status = 'RESOURCE_WALL'; break
                time.sleep(.05)
            if status != 'COMPLETED':
                os.killpg(proc.pid, signal.SIGKILL)
            code = proc.wait()
            reap_group(proc)
            if code != 0:
                status = status if status != 'COMPLETED' else 'EXECUTION_ERROR'
            stdout.seek(0); stderr.seek(0)
            if status == 'COMPLETED':
                row = json.loads(stdout.read())
                validate_identity(row, point, level)
            else:
                row = {}
                error = stderr.read().decode(errors='replace')[-3000:]
        except BaseException as exc:
            status, error, row = 'EXECUTION_ERROR', f'{type(exc).__name__}: {exc}', {}
            if proc is not None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
                reap_group(proc)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        child_cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
        row.update(id=point['id'], K=level[0], ref=level[1], parameters=point['parameters'], status=status,
                   resources=dict(child_cpu_seconds=child_cpu, wall_seconds=time.monotonic() - start,
                                  cpu_limit=cpu_limit, stop_error=error))
        json.dump(row, target, indent=2, allow_nan=False)
        target.write('\n'); target.flush(); os.fsync(target.fileno())
    return row


def reap_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    while True:
        try:
            os.waitpid(-proc.pid, 0)
        except ChildProcessError:
            break


def validate_identity(row, point, level):
    require((row['id'], row['K'], row['ref']) == (point['id'], *level), 'ROW_IDENTITY')
    require(row['parameters'] == point['parameters'], 'ROW_PARAMETERS')


def bug_reasons(row):
    from experiments.P4_A1.checks import algebra_violations, same_route_violations
    try:
        out = algebra_violations(row) + same_route_violations(row['losses'], row['cost_error'])
        L = {k: F(row['losses'][k]) for k in ('00', '01', '10', '11')}
        expected = dict(G_S=L['00']-L['10'], G_M=L['00']-L['01'], G_SM=L['00']-L['11'],
                        Gamma=L['10']+L['01']-L['00']-L['11'], G_S_M1=L['01']-L['11'], G_M_S1=L['10']-L['11'])
        for key, value in expected.items():
            if abs(F(row[key])-value) / F(row['Cref']) > F(1, 10**11):
                out.append('COST_DEFINITION:' + key)
        if F(row['Cref']) != L['11']:
            out.append('CREF_NOT_L11')
        return out
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as exc:
        return ['MALFORMED_ROW:' + type(exc).__name__]


def label(rows):
    from experiments.P4_A1.checks import row_readiness, d_normalized
    require(not any(bug_reasons(r) for r in rows.values()), 'BUG_IN_LABEL_INPUT')
    reasons = row_readiness(rows, MAIN)
    fine = rows[MAIN]
    z = F(fine['G_S_M1']) / F(fine['Cref'])
    d = d_normalized(rows, MAIN)[0]['G_S_M1']
    name = 'UNRESOLVED' if reasons or abs(z-THRESHOLD) <= d else ('MEETS' if z <= THRESHOLD else 'DOES_NOT_MEET')
    return dict(label=name, z=str(z), d=str(d), ready=not reasons, readiness_reasons=reasons,
                S_abs=fine['G_S_M1'], Cref=fine['Cref'],
                M_pct_by_level=[str(100*F(rows[lv]['G_M_S1'])/F(rows[lv]['Cref'])) for lv in LEVELS])


def score(points, panel):
    from experiments.P4_09_stationary.score import state_verdict, model_verdict
    labels = [points[p['id']]['label'] for p in panel if p['id'] in points]
    preds = {r['id']: r for r in map(json.loads, PREDICTIONS.read_text().splitlines())}
    done = len(points) == len(panel)
    truth = [[float(F(points[p['id']]['M_pct_by_level'][i])) for p in panel] for i in range(3)] if done else []
    others = [points[p['id']]['label'] for p in panel if p['id'] in points and p['id'] != 'P5_08']
    return dict(H_L1=state_verdict(labels), H_L2_exploratory=model_verdict(
        [preds[p['id']]['GM_pred_pctC'] for p in panel], [preds[p['id']]['NN_pred_pctC'] for p in panel],
        truth, all_ready=done and all(v['ready'] for v in points.values())),
        P5_08_label=points.get('P5_08', {}).get('label', 'NOT_RUN'),
        without_P5_08_descriptive={k: others.count(k) for k in ('MEETS', 'DOES_NOT_MEET', 'UNRESOLVED')},
        labels_by_id={p['id']: points.get(p['id'], {}).get('label', 'NOT_RUN') for p in panel})


def inspect_row(row, point, lv):
    validate_identity(row, point, lv)
    if row['status'] != 'COMPLETED':
        return 'EXECUTION:' + row['status']
    bugs = bug_reasons(row)
    return 'BUG:' + ','.join(bugs) if bugs else None


def run_panel(panel=None, levels=None, *, call=None, out=None, budget=BUDGET, controller_clock=time.process_time):
    out = Path(out or OUT)
    require(not (out / 'summary.json').exists(), 'ALREADY_SCORED')
    production = call is None
    ctx = preflight(panel_run=True) if production else dict(commit='FAKE_ENGINE')
    if panel is None:
        panel, levels = ctx['panel'], ctx['levels']
    require(tuple(levels) == LEVELS and len(panel) == 12, 'FIXED_PANEL_REQUIRED')
    if production:
        require(not (CACHE / 'panel').exists(), 'PANEL_CACHE_ALREADY_EXISTS')
    (out / 'panel').mkdir(parents=True, exist_ok=False)  # also blocks interrupted, unsaved attempts
    start = controller_clock()
    calls, points, stop, child_cpu, terminal_failure = [], {}, None, 0.0, None
    def used_cpu():
        if production:
            usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            return time.process_time() + usage.ru_utime + usage.ru_stime
        return child_cpu + controller_clock() - start
    call = call or launch
    for point in panel:
        rows = {}
        for lv in levels:
            used = used_cpu()
            remaining = budget - used - RESERVE
            if remaining <= 0:
                stop = 'BUDGET'; break
            path = row_path(out, point['id'], lv)
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            before_wall = time.monotonic()
            try:
                row = call(point, lv, path, cpu_limit=min(CALL_CPU_CAP, remaining), kind='panel')
                child_cpu += row['resources']['child_cpu_seconds']
                calls.append(dict(id=point['id'], level=list(lv), status=row['status'], **row['resources']))
            except BaseException as exc:
                # No retry, including caller failure after an outcome was computed.
                stop = 'EXECUTION:' + type(exc).__name__
                after = resource.getrusage(resource.RUSAGE_CHILDREN)
                consumed = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
                child_cpu += consumed
                terminal_failure = dict(id=point['id'], level=list(lv), status='EXECUTION_ERROR',
                                        child_cpu_seconds=consumed, wall_seconds=time.monotonic()-before_wall,
                                        cpu_limit=min(CALL_CPU_CAP, remaining), stop_error=f'{type(exc).__name__}: {exc}')
                calls.append(terminal_failure)
                if not path.exists():
                    write_once(path, dict(id=point['id'], K=lv[0], ref=lv[1], parameters=point['parameters'],
                                         status='EXECUTION_ERROR', error=str(exc)))
            else:
                try:
                    stop = inspect_row(row, point, lv)
                except (KeyError, ValueError, RuntimeError, TypeError) as exc:
                    stop = 'BUG:ROW_SCHEMA:' + str(exc)
            print(point['id'], lv, 'STOP' if stop else 'COMPLETED', f'{used_cpu():.3f}s', flush=True)
            if stop:
                break
            rows[lv] = row
        if stop:
            break
        try:
            points[point['id']] = label(rows)
        except (KeyError, ValueError, TypeError, ArithmeticError) as exc:
            stop = 'BUG:LABEL_SCHEMA:' + str(exc)
            break
        if sum(v['label'] == 'UNRESOLVED' for v in points.values()) == 2:
            stop = 'SECOND_U'; break
    scored = score(points, panel)
    result = dict(commit=ctx['commit'], stop_reason=stop, cpu_seconds=used_cpu(),
                  budget_CPU_seconds=budget, calls=calls, points=points, terminal_failure=terminal_failure, **scored)
    write_once(out / 'summary.json', result)
    return result


def rescore(out=None):
    """Read rows only: never starts/resumes calls and never rewrites artifacts."""
    out = Path(out or OUT)
    panel, levels = check_frozen()
    saved, points, calls, stop, missing = load(out / 'summary.json'), {}, [], None, False
    if saved['commit'] != 'FAKE_ENGINE':
        for name in SOURCES:
            require((ROOT / name).read_bytes() == git('show', saved['commit'] + ':' + name), 'RESCORE_RUNNER_CHANGED')
    for point in panel:
        rows = {}
        for lv in levels:
            path = row_path(out, point['id'], lv)
            failure = saved.get('terminal_failure')
            if failure and (failure['id'], failure['level']) == (point['id'], list(lv)):
                require(path.exists() and saved['stop_reason'].startswith('EXECUTION:'), 'INVALID_FAILURE_RECEIPT')
                calls.append(failure)
                stop = saved['stop_reason']
                break
            if not path.exists():
                missing = True; break
            row = load(path)
            if 'resources' in row:
                calls.append(dict(id=point['id'], level=list(lv), status=row['status'], **row['resources']))
            try:
                stop = inspect_row(row, point, lv)
            except (KeyError, ValueError, RuntimeError, TypeError) as exc:
                stop = 'BUG:ROW_SCHEMA:' + str(exc)
            if stop:
                break
            rows[lv] = row
        if stop or missing:
            break
        try:
            points[point['id']] = label(rows)
        except (KeyError, ValueError, TypeError, ArithmeticError) as exc:
            stop = 'BUG:LABEL_SCHEMA:' + str(exc)
            break
        if sum(v['label'] == 'UNRESOLVED' for v in points.values()) == 2:
            stop = 'SECOND_U'; break
    if missing:
        require(saved['stop_reason'] == 'BUDGET' and saved['budget_CPU_seconds']-saved['cpu_seconds'] <= RESERVE,
                'UNEXPLAINED_MISSING_ROW')
        stop = 'BUDGET'
    now = dict(stop_reason=stop, calls=calls, points=points, **score(points, panel))
    expected_paths = {row_path(out, c['id'], c['level']) for c in calls}
    return (set((out / 'panel').glob('*/level_*_*.json')) == expected_paths
            and all(saved[k] == v for k, v in now.items())
            and sum(c['child_cpu_seconds'] for c in calls) <= saved['cpu_seconds'] <= saved['budget_CPU_seconds'])


def anchor():
    ctx = preflight()
    out = OUT / 'gate4_anchor'
    require(not out.exists(), 'ANCHOR_ALREADY_ATTEMPTED')
    require(not (CACHE / 'anchor').exists(), 'ANCHOR_CACHE_ALREADY_EXISTS')
    out.mkdir(parents=True)
    old = saved_levels('P43_0379')[MAIN]
    point = dict(id='P43_0379', parameters=old['parameters'])
    target = out / 'P43_0379_level_640_4.json'
    new = launch(point, MAIN, target, cpu_limit=CALL_CPU_CAP, kind='anchor')
    report = dict(runner_commit=ctx['commit'], replay=point['id'], replay_cpu=new['resources']['child_cpu_seconds'],
                  replay_status=new['status'], field_mismatch=[], replay_bugs=[], labels={},
                  cache=str(CACHE / 'anchor'), panel_true_calls=0,
                  replay_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    if new['status'] == 'COMPLETED':
        report['field_mismatch'] = [k for k in FIELDS if new[k] != old[k]]
        report['replay_bugs'] = bug_reasons(new)
    for cid, (_, expected) in ANCHORS.items():
        got = label(saved_levels(cid))
        report['labels'][cid] = dict(expected=expected, got=got['label'], z_pct=float(100*F(got['z'])), d_pp=float(100*F(got['d'])))
    report['status'] = 'PASS' if (new['status'] == 'COMPLETED' and not report['field_mismatch'] and
                                not report['replay_bugs'] and all(v['expected'] == v['got'] for v in report['labels'].values())) else 'FAIL'
    write_once(out / 'report.json', report)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cmd', choices=('panel', 'rescore', 'anchor', 'worker'))
    parser.add_argument('rest', nargs='*')
    args = parser.parse_args(argv)
    if args.cmd == 'worker':
        require(len(args.rest) == 6, 'WORKER_REQUIRES_PARENT_RESERVATION')
        return worker(args.rest[0], (int(args.rest[1]), int(args.rest[2])), args.rest[3], float(args.rest[4]), int(args.rest[5]))
    require(not args.rest, 'NO_CONFIG_OVERRIDES')
    if args.cmd == 'anchor':
        return anchor()
    if args.cmd == 'rescore':
        same = rescore()
        print('RESCORE_MATCH' if same else 'RESCORE_MISMATCH')
        return 0 if same else 1
    result = run_panel()
    print('SCORED_ONCE', result['stop_reason'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
