"""Doan Van Tai — Phase 5 v1.1: ONE declared design revision after the v1 panel stopped SECOND_U.

What changes (notes/design/phase5_v1_1_amendment.md): numerical acceptance is applied to the
contrast each hypothesis uses (H-L1: G_S|M1, H-L2: G_M|S1) with the SAME tolerances as contract
R1 / numerics v1.3.1 (1/400 refinement, 1/4000 width). Everything else is the frozen v1 runner:
estimand, threshold, levels, order, BUG checks, stop rules, strict no-retry. Panel = the 10 points
v1 never ran (P5_03..P5_12), N = 10. v1 files stay byte-identical; this module only imports them.
"""
import argparse, ctypes, hashlib, json, math, os, re, resource, signal, subprocess, sys, tempfile, time
from fractions import Fraction as F
from pathlib import Path

os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')

from experiments.P4_03_map_audit.common import ROOT, canonical, git, require
from experiments.P5_panel import run as V1                     # frozen v1 runner, never edited

OUT = ROOT / 'results/phase5_v1_1'
CACHE = Path.home() / '.cache/state-model-regret/phase5_v1_1'
AMENDMENT = 'notes/design/phase5_v1_1_amendment.md'
V1_RUNNER = '3331d16350b6b1a9f3fdf892b965e48ea442fc80'         # DL-124 runner commit
V1_DATA = '5a2f0bafc788c95e0c4171ed6d95a6bc49cc43c3'
SOURCES = ('experiments/P5_v11/__init__.py', 'experiments/P5_v11/run.py', 'tests/test_p5_v11.py')
PANEL_IDS = tuple(f'P5_{i:02d}' for i in range(3, 13))          # never run in v1
SEEN = ('P5_01', 'P5_02')                                       # v1 outcomes: reported, never counted
CREF_DELTA_GATES = False                                        # author choice, DL-126
LEVELS, MAIN, THRESHOLD = V1.LEVELS, V1.MAIN, V1.THRESHOLD
load, write_once, bug_reasons = V1.load, V1.write_once, V1.bug_reasons


# ---------- 1. the one rule that changes: acceptance scoped to the hypothesis contrast ----------
def scoped_readiness(rows, contrast):
    """Contract R1 + numerics acceptance, same tolerances, applied to ONE contrast (+ its normalisation)."""
    from experiments.R3R_05_contract.rules import TOL_NUM, EPS_E
    from experiments.R3R_14_lean_close.checks import ARITH_MAX
    bad = [f'nonpositive_Cref:{lv}' for lv in LEVELS if F(rows[lv]['Cref']) <= 0]
    if bad:
        return bad
    fine = rows[MAIN]
    cf = F(fine['Cref'])
    reasons = []
    for lv, axis in (((320, 4), 'K'), ((640, 2), 'dt')):
        cc = F(rows[lv]['Cref'])
        if cc <= 0:
            reasons.append(f'nonpositive_Cref:{lv}'); continue
        gf, gc = F(fine[contrast]), F(rows[lv][contrast])
        zf, zc = gf / cf, gc / cc
        if max(abs(gf - gc) / cf, abs(zf - zc)) > TOL_NUM:
            reasons.append(f'R1_{axis}:{contrast}')
        if zf * zc < 0 and abs(zf) > EPS_E and abs(zc) > EPS_E:
            reasons.append(f'R1_{axis}:sign_flip:{contrast}')
        if CREF_DELTA_GATES and abs(cf - cc) / cf > TOL_NUM:
            reasons.append(f'R1_{axis}:Cref')
    for lv in LEVELS:
        if F(rows[lv]['normalized_error'][contrast]) > ARITH_MAX:
            reasons.append(f'arithmetic_width:{lv}:{contrast}')
        if F(rows[lv][contrast]) / F(rows[lv]['Cref']) < -TOL_NUM:
            reasons.append(f'negative_contrast:{lv}:{contrast}')
    return reasons


def label(rows):
    from experiments.P4_A1.checks import row_readiness, d_normalized
    require(not any(bug_reasons(r) for r in rows.values()), 'BUG_IN_LABEL_INPUT')   # BUG stays whole-row
    fine = rows[MAIN]
    z = F(fine['G_S_M1']) / F(fine['Cref'])
    d = d_normalized(rows, MAIN)[0]['G_S_M1']                                         # R6 unchanged
    reasons = scoped_readiness(rows, 'G_S_M1')
    name = 'UNRESOLVED' if reasons or abs(z - THRESHOLD) <= d else ('MEETS' if z <= THRESHOLD else 'DOES_NOT_MEET')
    strict = row_readiness(rows, MAIN)                                                # v1 rule: report only
    hl2 = scoped_readiness(rows, 'G_M_S1')
    return dict(label=name, z=str(z), d=str(d), ready=not reasons, readiness_reasons=reasons,
                strict_v1_label=V1.label(rows)['label'],
                strict_v1_reasons=strict, ready_HL2=not hl2, readiness_reasons_HL2=hl2,
                S_abs=fine['G_S_M1'], Cref=fine['Cref'],
                M_pct_by_level=[str(100 * F(rows[lv]['G_M_S1']) / F(rows[lv]['Cref'])) for lv in LEVELS])


def score(points, panel):
    from experiments.P4_09_stationary.score import state_verdict, model_verdict
    n = len(panel)
    labels = [points[p['id']]['label'] for p in panel if p['id'] in points]
    preds = {r['id']: r for r in map(json.loads, V1.PREDICTIONS.read_text().splitlines())}
    done = len(points) == n
    truth = [[float(F(points[p['id']]['M_pct_by_level'][i])) for p in panel] for i in range(3)] if done else []
    others = [points[p['id']]['label'] for p in panel if p['id'] in points and p['id'] != 'P5_08']
    strict = [points[p['id']]['strict_v1_label'] for p in panel if p['id'] in points]
    seen = {pid: label({lv: load(V1.row_path(V1.OUT, pid, lv)) for lv in LEVELS})['label'] for pid in SEEN}
    return dict(H_L1_v11=state_verdict(labels, planned=n),
                H_L2_v11_exploratory=model_verdict(
                    [preds[p['id']]['GM_pred_pctC'] for p in panel], [preds[p['id']]['NN_pred_pctC'] for p in panel],
                    truth, all_ready=done and all(v['ready_HL2'] for v in points.values()), planned=n),
                P5_08_label=points.get('P5_08', {}).get('label', 'NOT_RUN'),
                without_P5_08_descriptive={k: others.count(k) for k in ('MEETS', 'DOES_NOT_MEET', 'UNRESOLVED')},
                strict_v1_rule_sensitivity={k: strict.count(k) for k in ('MEETS', 'DOES_NOT_MEET', 'UNRESOLVED')},
                seen_points_v11_rule_descriptive=seen,
                labels_by_id={p['id']: points.get(p['id'], {}).get('label', 'NOT_RUN') for p in panel})


# ---------- 2. guards: v1 frozen + closed, amendment committed, gate declared ----------
def panel10():
    panel, _ = V1.check_frozen()
    out = [p for p in panel if p['id'] in PANEL_IDS]
    require([p['id'] for p in out] == list(PANEL_IDS), 'V11_PANEL_ORDER')
    return out


def v1_closed():
    for path in git('ls-tree', '-r', '--name-only', V1_DATA, 'results/phase5').decode().splitlines():
        require((ROOT / path).read_bytes() == git('show', V1_DATA + ':' + path), 'V1_DATA_CHANGED: ' + path)
    s = load(V1.OUT / 'summary.json')
    require((V1.OUT / 'summary.json').read_bytes() == git('show', 'HEAD:results/phase5/summary.json'), 'V1_SUMMARY_UNCOMMITTED')
    require(s['stop_reason'] == 'SECOND_U' and s['H_L1']['verdict'] == 'INCONCLUSIVE', 'V1_NOT_CLOSED_AS_EXPECTED')
    require(all(s['labels_by_id'][pid] == 'NOT_RUN' for pid in PANEL_IDS), 'V11_POINT_ALREADY_RUN_IN_V1')
    require(V1.rescore(), 'V1_RESCORE_MISMATCH')
    for name in V1.SOURCES:
        require((ROOT / name).read_bytes() == git('show', V1_RUNNER + ':' + name), 'V1_RUNNER_CHANGED: ' + name)


def gate_record():
    path = ROOT / 'notes/02_decision_log.md'
    require(path.read_bytes() == git('show', 'HEAD:notes/02_decision_log.md'), 'UNCOMMITTED_GATE')
    found = re.findall(r'<!-- P5_GATE_V11\s+(.*?)\s*-->', path.read_text(), re.S)
    require(len(found) == 1, 'V11_GATE_DECLARATION_REQUIRED')
    gate = json.loads(found[0])
    require(gate['status'] == 'GO' and gate['policy'] == 'STRICT_NO_RETRY', 'V11_GATE_NOT_GO')
    require(gate['cref_delta_gates'] == CREF_DELTA_GATES, 'CREF_CHOICE_MISMATCH')
    require(gate['amendment_sha256'] == hashlib.sha256((ROOT / AMENDMENT).read_bytes()).hexdigest(), 'AMENDMENT_CHANGED')
    commit = gate['runner_commit']
    git('merge-base', '--is-ancestor', commit, 'HEAD')
    for source in SOURCES:
        require((ROOT / source).read_bytes() == git('show', commit + ':' + source), 'V11_RUNNER_CHANGED: ' + source)
    rp = 'results/phase5_v1_1/gate_anchor/report.json'
    report = load(ROOT / rp)
    require((ROOT / rp).read_bytes() == git('show', 'HEAD:' + rp), 'UNCOMMITTED_ANCHOR')
    require(report['status'] == 'PASS' and report['runner_commit'] == commit, 'ANCHOR_NOT_VALID_FOR_RUNNER')
    raw = ROOT / 'results/phase5_v1_1/gate_anchor/P43_0379_level_640_4.json'
    require(hashlib.sha256(raw.read_bytes()).hexdigest() == report['replay_sha256'], 'ANCHOR_ROW_CHANGED')
    require((ROOT / AMENDMENT).read_bytes() == git('show', commit + ':' + AMENDMENT), 'AMENDMENT_NOT_IN_RUNNER_COMMIT')
    return gate


def preflight(*, panel_run=False):
    V1.check_frozen()
    from experiments.P4_A1.config import verify_run
    from experiments.P4_03_map_audit.common import verify_prereg
    for name in V1.RUNS:
        verify_run(name)
    verify_prereg()
    for name in (*SOURCES, AMENDMENT):
        require((ROOT / name).read_bytes() == git('show', 'HEAD:' + name), 'UNCOMMITTED: ' + name)
    v1_closed()
    require(not git('status', '--porcelain', '--untracked-files=no').strip(), 'TRACKED_TREE_DIRTY')
    if panel_run:
        gate_record()
    return dict(panel=panel10(), commit=git('rev-parse', 'HEAD').decode().strip())


# ---------- 3. physical calls: same evaluate() as v1, own output/cache/reservation ----------
def row_path(out, pid, level):
    return Path(out) / 'panel' / pid / f'level_{level[0]}_{level[1]}.json'


def worker(pid, level, kind, cpu_limit, reservation):
    require(0 < cpu_limit <= V1.CALL_CPU_CAP, 'INVALID_CPU_CAP')
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, math.ceil(cpu_limit)), max(2, math.ceil(cpu_limit) + 1)))
    ctx = preflight(panel_run=kind == 'panel')                   # all guards BEFORE the evaluator import
    if kind == 'anchor':
        require(pid == 'P43_0379' and level == MAIN, 'UNREGISTERED_ANCHOR')
        point = dict(id=pid, parameters=V1.saved_levels(pid)[MAIN]['parameters'])
        expected = OUT / 'gate_anchor/P43_0379_level_640_4.json'
    else:
        require(kind == 'panel' and level in LEVELS, 'UNREGISTERED_CALL')
        point = next(p for p in ctx['panel'] if p['id'] == pid)
        expected = row_path(OUT, pid, level)
    from experiments.P4_09_stationary.discovery import forbidden
    require(canonical(point['parameters']) not in forbidden(), 'CF_OR_SEALED_COLLISION')
    require(expected.exists() and os.fstat(reservation).st_ino == expected.stat().st_ino
            and expected.stat().st_size == 0, 'INVALID_PARENT_RESERVATION')
    json.dump(V1.evaluate(point, level, CACHE / kind), sys.stdout, allow_nan=False)
    sys.stdout.flush()


def launch(point, level, path, *, cpu_limit, kind='panel', wall_limit=V1.CALL_WALL_CAP):
    """v1 launch, unchanged except the guard set and the worker module (v1 bytes must not change)."""
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start, self_start = time.monotonic(), time.process_time()
    preflight(panel_run=kind == 'panel')
    require(ctypes.CDLL(None).prctl(36, 1, 0, 0, 0) == 0, 'SUBREAPER_REQUIRED')
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    proc, error, status = None, None, 'COMPLETED'
    with path.open('x') as target, tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            spent = resource.getrusage(resource.RUSAGE_CHILDREN)
            guard_cpu = spent.ru_utime + spent.ru_stime - before.ru_utime - before.ru_stime
            require(guard_cpu + time.process_time() - self_start < cpu_limit, 'CPU_LIMIT_IN_PREFLIGHT')
            proc = subprocess.Popen([sys.executable, '-m', 'experiments.P5_v11.run', 'worker', point['id'],
                                     str(level[0]), str(level[1]), kind, str(cpu_limit), str(target.fileno())],
                                    cwd=ROOT, env=dict(os.environ), stdout=stdout, stderr=stderr,
                                    start_new_session=True, pass_fds=(target.fileno(),))
            while proc.poll() is None:
                done = resource.getrusage(resource.RUSAGE_CHILDREN)
                completed = done.ru_utime + done.ru_stime - before.ru_utime - before.ru_stime
                if completed + V1.group_cpu(proc.pid) + time.process_time() - self_start >= cpu_limit:
                    status = 'RESOURCE_CPU'; break
                if time.monotonic() - start >= wall_limit:
                    status = 'RESOURCE_WALL'; break
                time.sleep(.05)
            if status != 'COMPLETED':
                os.killpg(proc.pid, signal.SIGKILL)
            code = proc.wait(); V1.reap_group(proc)
            if code != 0 and status == 'COMPLETED':
                status = 'EXECUTION_ERROR'
            stdout.seek(0); stderr.seek(0)
            if status == 'COMPLETED':
                row = json.loads(stdout.read()); V1.validate_identity(row, point, level)
            else:
                row, error = {}, stderr.read().decode(errors='replace')[-3000:]
        except BaseException as exc:
            status, error, row = 'EXECUTION_ERROR', f'{type(exc).__name__}: {exc}', {}
            if proc is not None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait(); V1.reap_group(proc)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        row.update(id=point['id'], K=level[0], ref=level[1], parameters=point['parameters'], status=status,
                   resources=dict(child_cpu_seconds=after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                                  wall_seconds=time.monotonic() - start, cpu_limit=cpu_limit, stop_error=error))
        json.dump(row, target, indent=2, allow_nan=False)
        target.write('\n'); target.flush(); os.fsync(target.fileno())
    return row


# ---------- 4. the one run (same loop and stop rules as v1) ----------
def remaining_budget():
    return V1.BUDGET - load(V1.OUT / 'summary.json')['cpu_seconds']      # one Phase 5 budget, not a new one


def run_panel(panel=None, *, call=None, out=None, budget=None, controller_clock=time.process_time):
    out = Path(out or OUT)
    require(not (out / 'summary.json').exists(), 'ALREADY_SCORED')
    production = call is None
    ctx = preflight(panel_run=True) if production else dict(commit='FAKE_ENGINE', panel=panel)
    panel = panel or ctx['panel']
    require([p['id'] for p in panel] == list(PANEL_IDS), 'FIXED_V11_PANEL_REQUIRED')
    budget = budget if budget is not None else remaining_budget()
    if production:
        require(panel == ctx['panel'] and budget == remaining_budget(), 'V11_CONFIG_OVERRIDE')
        require(not (CACHE / 'panel').exists(), 'PANEL_CACHE_ALREADY_EXISTS')
    (out / 'panel').mkdir(parents=True, exist_ok=False)                 # strict: no resume, ever
    start = controller_clock()
    calls, points, stop, child_cpu, terminal_failure = [], {}, None, 0.0, None

    def used_cpu():
        if production:
            u = resource.getrusage(resource.RUSAGE_CHILDREN)
            return time.process_time() + u.ru_utime + u.ru_stime
        return child_cpu + controller_clock() - start
    call = call or launch
    for point in panel:
        rows = {}
        for lv in LEVELS:
            remaining = budget - used_cpu() - V1.RESERVE
            if remaining <= 0:
                stop = 'BUDGET'; break
            path = row_path(out, point['id'], lv)
            before, before_wall = resource.getrusage(resource.RUSAGE_CHILDREN), time.monotonic()
            try:
                row = call(point, lv, path, cpu_limit=min(V1.CALL_CPU_CAP, remaining), kind='panel')
                child_cpu += row['resources']['child_cpu_seconds']
                calls.append(dict(id=point['id'], level=list(lv), status=row['status'], **row['resources']))
            except BaseException as exc:                                # no retry, ever
                after = resource.getrusage(resource.RUSAGE_CHILDREN)
                consumed = max(0.0, after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime)
                child_cpu += consumed
                stop = 'EXECUTION:' + type(exc).__name__
                terminal_failure = dict(id=point['id'], level=list(lv), status='EXECUTION_ERROR', child_cpu_seconds=consumed,
                                        wall_seconds=time.monotonic() - before_wall, cpu_limit=min(V1.CALL_CPU_CAP, remaining),
                                        stop_error=f'{type(exc).__name__}: {exc}')
                calls.append(terminal_failure)
                if not path.exists():
                    write_once(path, dict(id=point['id'], K=lv[0], ref=lv[1], parameters=point['parameters'],
                                          status='EXECUTION_ERROR', error=str(exc)))
            else:
                try:
                    stop = V1.inspect_row(row, point, lv)
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
        except (KeyError, ValueError, TypeError, RuntimeError, ArithmeticError) as exc:
            stop = 'BUG:LABEL_SCHEMA:' + str(exc); break
        if sum(v['label'] == 'UNRESOLVED' for v in points.values()) == 2:
            stop = 'SECOND_U'; break
    result = dict(commit=ctx['commit'], amendment=AMENDMENT, cref_delta_gates=CREF_DELTA_GATES, stop_reason=stop,
                  cpu_seconds=used_cpu(), budget_CPU_seconds=budget, calls=calls, points=points,
                  terminal_failure=terminal_failure, **score(points, panel))
    write_once(out / 'summary.json', result)
    return result


def rescore(out=None):
    """Replay raw calls/order/stops/resources and labels, read-only; no engine."""
    out = Path(out or OUT)
    saved, panel = load(out / 'summary.json'), panel10()
    if saved['commit'] != 'FAKE_ENGINE':
        v1_closed()
        for name in SOURCES:
            require((ROOT / name).read_bytes() == git('show', saved['commit'] + ':' + name), 'RESCORE_RUNNER_CHANGED')
        require((ROOT / AMENDMENT).read_bytes() == git('show', saved['commit'] + ':' + AMENDMENT), 'RESCORE_AMENDMENT_CHANGED')
        if saved['budget_CPU_seconds'] != remaining_budget():
            return False
    if saved['amendment'] != AMENDMENT or saved['cref_delta_gates'] != CREF_DELTA_GATES:
        return False
    points, calls, stop, missing = {}, [], None, False
    failure = saved.get('terminal_failure')
    for point in panel:
        rows = {}
        for lv in LEVELS:
            path = row_path(out, point['id'], lv)
            if failure and (failure['id'], failure['level']) == (point['id'], list(lv)):
                if not path.exists() or not saved['stop_reason'].startswith('EXECUTION:'):
                    return False
                calls.append(failure)
                stop = saved['stop_reason']
                break
            if not path.exists():
                missing = True
                break
            row = load(path)
            if 'resources' not in row:
                return False
            calls.append(dict(id=point['id'], level=list(lv), status=row['status'], **row['resources']))
            try:
                stop = V1.inspect_row(row, point, lv)
            except (KeyError, ValueError, RuntimeError, TypeError) as exc:
                stop = 'BUG:ROW_SCHEMA:' + str(exc)
            if stop:
                break
            rows[lv] = row
        if stop or missing:
            break
        try:
            points[point['id']] = label(rows)
        except (KeyError, ValueError, TypeError, RuntimeError, ArithmeticError) as exc:
            stop = 'BUG:LABEL_SCHEMA:' + str(exc)
            break
        if sum(v['label'] == 'UNRESOLVED' for v in points.values()) == 2:
            stop = 'SECOND_U'
            break
    if missing:
        if saved['stop_reason'] != 'BUDGET' or saved['budget_CPU_seconds'] - saved['cpu_seconds'] > V1.RESERVE:
            return False
        stop = 'BUDGET'
    if failure and (not calls or calls[-1] != failure):
        return False
    now = dict(stop_reason=stop, calls=calls, points=points, **score(points, panel))
    files = set((out / 'panel').glob('*/level_*_*.json'))
    expected = {row_path(out, c['id'], c['level']) for c in calls}
    valid_resources = all(all(math.isfinite(c[k]) and c[k] >= 0 for k in ('child_cpu_seconds', 'wall_seconds'))
                          and 0 < c['cpu_limit'] <= V1.CALL_CPU_CAP for c in calls)
    return (files == expected and valid_resources and all(saved[k] == v for k, v in now.items())
            and sum(c['child_cpu_seconds'] for c in calls) <= saved['cpu_seconds'] <= saved['budget_CPU_seconds'])


# ---------- 5. positive control for the v1.1 runner ----------
def anchor():
    ctx = preflight()
    out = OUT / 'gate_anchor'
    require(not out.exists() and not (CACHE / 'anchor').exists(), 'ANCHOR_ALREADY_ATTEMPTED')
    out.mkdir(parents=True)
    old = V1.saved_levels('P43_0379')[MAIN]
    target = out / 'P43_0379_level_640_4.json'
    new = launch(dict(id='P43_0379', parameters=old['parameters']), MAIN, target, cpu_limit=V1.CALL_CPU_CAP, kind='anchor')
    report = dict(runner_commit=ctx['commit'], replay_status=new['status'],
                  replay_cpu=new['resources']['child_cpu_seconds'], field_mismatch=[], replay_bugs=[], labels={},
                  replay_sha256=hashlib.sha256(target.read_bytes()).hexdigest(), panel_true_calls=0)
    if new['status'] == 'COMPLETED':
        report['field_mismatch'] = [k for k in V1.FIELDS if new[k] != old[k]]
        report['replay_bugs'] = bug_reasons(new)
    cases = {cid: (V1.saved_levels(cid), exp) for cid, (_, exp) in V1.ANCHORS.items()}
    for pid in SEEN:                                   # the two v1 points: U under v1, must be MEETS here
        cases[pid] = ({lv: load(V1.row_path(V1.OUT, pid, lv)) for lv in LEVELS}, 'MEETS')
    for cid, (rows, expected) in cases.items():
        got = label(rows)
        report['labels'][cid] = dict(expected=expected, got=got['label'], strict_v1=got['strict_v1_label'],
                                     z_pct=float(100 * F(got['z'])), d_pp=float(100 * F(got['d'])))
    report['status'] = 'PASS' if (new['status'] == 'COMPLETED' and not report['field_mismatch'] and not report['replay_bugs']
                                  and all(v['expected'] == v['got'] for v in report['labels'].values())) else 'FAIL'
    write_once(out / 'report.json', report)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('cmd', choices=('panel', 'rescore', 'anchor', 'worker'))
    ap.add_argument('rest', nargs='*')
    a = ap.parse_args(argv)
    if a.cmd == 'worker':
        require(len(a.rest) == 6, 'WORKER_REQUIRES_PARENT_RESERVATION')
        return worker(a.rest[0], (int(a.rest[1]), int(a.rest[2])), a.rest[3], float(a.rest[4]), int(a.rest[5]))
    require(not a.rest, 'NO_CONFIG_OVERRIDES')
    if a.cmd == 'anchor':
        return anchor()
    if a.cmd == 'rescore':
        same = rescore()
        print('RESCORE_MATCH' if same else 'RESCORE_MISMATCH')
        return 0 if same else 1
    print('SCORED_ONCE', run_panel()['stop_reason'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
