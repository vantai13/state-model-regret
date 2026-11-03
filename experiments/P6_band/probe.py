"""Doan Van Tai — L6.2 Part B (DL-134): numerics probe for the SIGNED contrast G_S, off-panel.

One fixed point per numerics class (h, kappa) of the DL-133 panel: the heaviest-load panel base
of that class at c = 1/16, where H1 and H0 both predict '+' (non-discriminating). Each point is
evaluated once at the three contract levels. The summary holds readiness, d, widths, R1 deltas
and CPU only; z and G_S stay in the raw rows (sealed until L6.4). No retry, no resume.
"""
import csv
import argparse
import ctypes
import hashlib
import json
import math
import os
from fractions import Fraction as F
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time

from experiments.P6_band import select_dii as S

PANEL = 'results/phase6/window_revision03/candidates.csv'
OUT = 'results/phase6/probe'
CACHE = Path.home()/'.cache/state-model-regret/phase6/probe'
LEVELS = ((640, 4), (320, 4), (640, 2))
MAIN = LEVELS[0]
PROBE_C = F(1, 16)
EXPECTED_PROBES = ('B027C02', 'B040C02', 'B050C02')
TOL_NUM, EPS_E, ARITH_MAX = F(1, 400), F(1, 200), F(1, 4000)   # contract values (tested)
PROBE_CAP, PANEL_CAP, SAFETY = 1800, 7200, F(3, 2)
SOURCES = ('experiments/P6_band/probe.py', 'tests/test_p6_probe.py')
DECISION_COMMIT = '9f86813e'
PANEL_SHA256 = 'b614228c27ab638661379bcd983c5a4ae402007d0c05b3c42abe5b9190e73f2c'


def cpu():
    u = resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time()+u.ru_utime+u.ru_stime


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------- pure: which points, how to judge them ----------

def load_panel(root):
    if sha(Path(root)/PANEL) != PANEL_SHA256:
        raise RuntimeError('CANDIDATES_CHANGED')
    with (Path(root)/PANEL).open() as stream:
        return list(csv.DictReader(stream))


def numerics_class(r):
    return (F(r['h']), F(r['kappa']))


def heaviest(r):
    a, b, u = F(r['lambdaA']), F(r['lambdaB']), F(r['u'])
    return max(a+u, b+u)


def probe_points(scan, panel):
    """Heaviest-load D base of each class; probe row = same base at c = 1/16, must be A-type."""
    byid = {r['id']: r for r in scan}
    d_rows = [r for r in panel if r['role'] == 'D']
    out = []
    for cls in sorted({numerics_class(r) for r in d_rows}):
        members = [r for r in d_rows if numerics_class(r) == cls]
        base = max(members, key=lambda r: (heaviest(r), r['base_id']))['base_id']
        row = next(r for r in scan if r['base_id'] == base and F(r['c']) == PROBE_C)
        if not (row['group'] == 'A' and row['H1'] == row['H0'] == '+' and row['W6'] == 'True'):
            raise RuntimeError('PROBE_NOT_NONDISCRIMINATING:'+row['id'])
        if row['id'] in {r['id'] for r in panel}:
            raise RuntimeError('PROBE_IS_PANEL_MEMBER:'+row['id'])
        a, b, k, u, h = (F(byid[row['id']][n]) for n in ('lambdaA', 'lambdaB', 'kappa', 'u', 'h'))
        out.append(dict(id='P6B_'+row['id'], scan_id=row['id'], base_id=base,
                        numerics_class=[str(cls[0]), str(cls[1])],
                        parameters=[str(v) for v in (a, b, k, u/2, h, PROBE_C)]))   # engine eta = u/2
    return out


def gs_readiness(rows):
    """Contract R1 (K and dt axes) + width for G_S only. G_S MAY be negative: no sign gate."""
    reasons = [f'nonpositive_Cref:{lv}' for lv in LEVELS if F(rows[lv]['Cref']) <= 0]
    if reasons:
        return reasons
    cf, gf = F(rows[MAIN]['Cref']), F(rows[MAIN]['G_S'])
    zf = gf/cf
    for lv, axis in (((320, 4), 'K'), ((640, 2), 'dt')):
        cc, gc = F(rows[lv]['Cref']), F(rows[lv]['G_S'])
        zc = gc/cc
        if max(abs(gf-gc)/cf, abs(zf-zc)) > TOL_NUM:
            reasons.append('R1_'+axis)
        if zf*zc < 0 and abs(zf) > EPS_E and abs(zc) > EPS_E:
            reasons.append('sign_flip_'+axis)
    for lv in LEVELS:
        if F(rows[lv]['normalized_error']['G_S']) > ARITH_MAX:
            reasons.append(f'width:{lv[0]}_{lv[1]}')
    return reasons


def numerics_summary(rows):
    """Everything needed to judge readiness, but no z and no G_S (sealed)."""
    from experiments.P4_A1.checks import d_normalized
    cf, gf = F(rows[MAIN]['Cref']), F(rows[MAIN]['G_S'])
    deltas = {}
    for lv, axis in (((320, 4), 'K'), ((640, 2), 'dt')):
        cc, gc = F(rows[lv]['Cref']), F(rows[lv]['G_S'])
        deltas[axis+'_pp'] = float(100*max(abs(gf-gc)/cf, abs(gf/cf-gc/cc)))
    reasons = gs_readiness(rows)
    return dict(ready=not reasons, reasons=reasons,
                d_pp=float(100*d_normalized(rows, MAIN)[0]['G_S']),
                width_pp={f'{lv[0]}_{lv[1]}': float(100*F(rows[lv]['normalized_error']['G_S'])) for lv in LEVELS},
                R1_delta_pp=deltas,
                uncertain_action_mass={f'{lv[0]}_{lv[1]}': rows[lv].get('uncertain_action_mass') for lv in LEVELS},
                cpu_seconds={f'{lv[0]}_{lv[1]}': rows[lv]['resources']['cpu_seconds'] for lv in LEVELS})


def decide(points, results, panel):
    """Pre-declared (DL-134): drop panel bases of a class whose probe is not ready; then budget."""
    ready = {tuple(p['numerics_class']): results[p['id']]['ready'] for p in points}
    cpu3 = {tuple(p['numerics_class']): sum(results[p['id']]['cpu_seconds'].values()) for p in points}

    def cls(r):
        c = numerics_class(r)
        return (str(c[0]), str(c[1]))
    kept = [r for r in panel if r['role'] == 'A-' or ready.get(cls(r))]
    d_kept = [r for r in kept if r['role'] == 'D']
    if len(d_kept) < S.N_MIN or len({r['base_id'] for r in d_kept}) < S.BASES_MIN:
        return dict(status='STOP_NUMERICS', kept=[r['id'] for r in kept])

    def estimate(rows):
        return float(SAFETY*sum(F(cpu3.get(cls(r), max(cpu3.values()))) for r in rows))
    full = estimate(kept)
    no_twins = [r for r in kept if r['role'] != 'twin']
    if full <= PANEL_CAP:
        plan, members, est = 'ALL_MEMBERS', kept, full
    elif estimate(no_twins) <= PANEL_CAP:
        plan, members, est = 'DROP_TWINS', no_twins, estimate(no_twins)
    else:
        return dict(status='HOLD_BUDGET', estimate_full=full, estimate_no_twins=estimate(no_twins))
    status = 'PASS' if all(ready.values()) else 'PASS_REDUCED'
    worst_d = max(results[p['id']]['d_pp'] for p in points)
    u_hint = sum(abs(float(r['z_K640']))*0.85 < 100*float(EPS_E)+worst_d for r in members if r['role'] == 'D')
    return dict(status=status, plan=plan, members=[r['id'] for r in members], panel_cpu_estimate=est,
                expected_U_hint=u_hint,
                expected_U_hint_rule='|z_K640|*0.85 < 0.5 + max probe d (heuristic, descriptive only)')


# ---------- the one run ----------

def preflight(root):
    from experiments.P5_panel import run as V1
    from experiments.P6_band import window as W
    W.preflight()
    V1.git('merge-base', '--is-ancestor', DECISION_COMMIT, 'HEAD')
    V1.require('### DL-134 ' in V1.git('show', DECISION_COMMIT+':notes/02_decision_log.md').decode(),
               'DL134_REQUIRED_BEFORE_CODE')
    for source in SOURCES+('notes/phases/PHASE_6.md', PANEL, 'results/phase6/window_revision03/summary.json'):
        V1.require((root/source).read_bytes() == V1.git('show', 'HEAD:'+source), 'UNCOMMITTED:'+source)
    for source in (PANEL, 'results/phase6/window_revision03/summary.json',
                   'experiments/P6_band/predictor.py', 'experiments/P6_band/identity.py',
                   'experiments/P6_band/select_dii.py'):
        V1.require((root/source).read_bytes() == V1.git('show', 'bf582028:'+source), 'PART_A_CHANGED:'+source)
    V1.require(V1.load(root/'results/phase6/window_revision03/summary.json')['status'] == 'PASS', 'PART_A_NOT_PASSED')
    scan, panel = S.load_rows(root), load_panel(root)
    points = probe_points(scan, panel)
    V1.require(tuple(p['scan_id'] for p in points) == EXPECTED_PROBES, 'PROBE_SET_CHANGED')
    return V1, points, panel


def reservation(root, point, level, fd, path):
    from experiments.P5_panel import run as V1
    V1.require(fd is not None, 'PARENT_RESERVATION_REQUIRED')
    V1.require(tuple(level) in LEVELS and path.exists(), 'UNREGISTERED_LEVEL_OR_PATH')
    V1.require(os.fstat(fd).st_ino == path.stat().st_ino and path.stat().st_size == 0,
               'INVALID_PARENT_RESERVATION')


def launch(point, level, path, *, cpu_limit, kind='probe', worker_module='experiments.P6_band.probe'):
    """One reserved call, with Phase5 group-CPU helpers and identity BEFORE metadata."""
    from experiments.P5_panel import run as V1
    V1.require(math.isfinite(cpu_limit) and cpu_limit > 0, 'INVALID_CPU_LIMIT')
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    started, wall = cpu(), time.monotonic()
    before_children = resource.getrusage(resource.RUSAGE_CHILDREN)
    proc, row, error, status = None, {}, None, 'COMPLETED'
    with path.open('x') as target:
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            try:
                cmd = [sys.executable, '-B', '-m', worker_module, 'worker', kind, point['id'],
                       str(level[0]), str(level[1]), str(target.fileno()), str(cpu_limit)]
                proc = subprocess.Popen(cmd, cwd=V1.ROOT, stdout=stdout, stderr=stderr,
                                        pass_fds=(target.fileno(),), start_new_session=True,
                                        env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1'))
                while proc.poll() is None:
                    if cpu()-started+V1.group_cpu(proc.pid) >= cpu_limit:
                        status = 'RESOURCE_CPU'; break
                    if time.monotonic()-wall >= 3600:
                        status = 'RESOURCE_WALL'; break
                    time.sleep(.05)
                if status != 'COMPLETED':
                    os.killpg(proc.pid, signal.SIGKILL)
                code = proc.wait(); V1.reap_group(proc)
                stdout.seek(0); stderr.seek(0)
                if code and status == 'COMPLETED':
                    status = 'EXECUTION_ERROR'
                if status == 'COMPLETED':
                    row = json.loads(stdout.read())
                    V1.validate_identity(row, point, level)
                    V1.require(row['status'] == 'COMPLETED' and row['CF_computed'] is False, 'INVALID_EVALUATOR_STATUS')
                else:
                    error = stderr.read().decode(errors='replace')[-2000:]
            except BaseException as exc:
                status, row, error = 'EXECUTION_ERROR', {}, type(exc).__name__
                if proc is not None:
                    try: os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                    proc.wait(); V1.reap_group(proc)
        after_children = resource.getrusage(resource.RUSAGE_CHILDREN)
        child_cpu = (after_children.ru_utime+after_children.ru_stime
                     -before_children.ru_utime-before_children.ru_stime)
        row.update(id=point['id'], K=level[0], ref=level[1], parameters=point['parameters'], status=status,
                   resources=dict(cpu_seconds=cpu()-started, child_cpu_seconds=child_cpu,
                                  wall_seconds=time.monotonic()-wall,
                                  cpu_limit=cpu_limit, stop_error=error))
        json.dump(row, target, indent=2, allow_nan=False)
        target.write('\n'); target.flush(); os.fsync(target.fileno())
    return row


def worker(kind, mid, K, ref, fd, limit):
    from experiments.P5_panel import run as V1
    from experiments.P6_band import window as W
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, math.ceil(limit)), max(2, math.ceil(limit)+1)))
    V1.require(kind == 'probe', 'UNREGISTERED_WORKER_KIND')
    _, points, _ = preflight(V1.ROOT)
    point = next(p for p in points if p['id'] == mid)
    level = (K, ref)
    reservation(V1.ROOT, point, level, fd, V1.ROOT/OUT/mid/f'level_{K}_{ref}.json')
    # Own reserved probe keys are expected here; collision audit was done before the first call.
    V1.require(W.key(point['parameters']) not in W.forbidden_keys(), 'CF_OR_SEALED_COLLISION')
    json.dump(V1.evaluate(point, level, CACHE), sys.stdout, allow_nan=False)


def compute(root, points, panel, *, call=launch, used_cpu, out):
    from experiments.P5_panel import run as V1
    results, stop = {}, None
    for p in points:
        rows = {}
        for lv in LEVELS:
            remaining = PROBE_CAP-used_cpu()-1
            if remaining <= 0:
                stop = dict(status='RESOURCE_CPU'); break
            path = out/p['id']/f'level_{lv[0]}_{lv[1]}.json'
            row = call(p, lv, path, cpu_limit=remaining)
            problem = V1.inspect_row(row, p, lv)
            print(p['id'], lv, 'STOP' if problem else 'COMPLETED', f'{used_cpu():.0f}s', flush=True)
            if problem:
                stop = dict(status='BUG' if problem.startswith('BUG:') else row['status'],
                            id=p['id'], level=list(lv), reason=problem)
                break
            rows[lv] = row
        if stop:
            break
        results[p['id']] = numerics_summary(rows)
    decision = stop if stop else decide(points, results, panel)
    return dict(status=decision['status'], decision=decision, points=points, numerics=results)


def main():
    from experiments.P5_panel import run as V1
    from experiments.P6_band import window as W
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', nargs='?', default='probe', choices=('probe', 'worker'))
    parser.add_argument('args', nargs='*')
    parser.add_argument('--spent-cpu-seconds', type=float)
    args = parser.parse_args()
    if args.command == 'worker':
        kind, mid, K, ref, fd, limit = args.args
        return worker(kind, mid, int(K), int(ref), int(fd), float(limit))
    started = cpu()
    root, out = V1.ROOT, V1.ROOT/OUT
    _, points, panel = preflight(root)
    V1.require(args.spent_cpu_seconds is not None and math.isfinite(args.spent_cpu_seconds)
               and args.spent_cpu_seconds >= 1750 and args.spent_cpu_seconds+PROBE_CAP <= 14400,
               'PRIOR_PHASE_BUDGET_REQUIRED')
    V1.require(not out.exists() and not CACHE.exists(), 'PROBE_ALREADY_ATTEMPTED')
    blocked = W.collision_keys()
    for p in points:
        V1.require(W.key(p['parameters']) not in blocked, 'PROBE_EXPOSED:'+p['id'])
    out.mkdir(parents=True, exist_ok=False)
    V1.require(ctypes.CDLL(None).prctl(36, 1, 0, 0, 0) == 0, 'SUBREAPER_REQUIRED')
    resource.setrlimit(resource.RLIMIT_CPU, (PROBE_CAP, PROBE_CAP+1))
    try:
        summary = compute(root, points, panel, used_cpu=lambda: cpu()-started, out=out)
    except BaseException as exc:
        summary = dict(status='EXECUTION_ERROR', exception_type=type(exc).__name__,
                       points=points, numerics={}, decision=dict(status='EXECUTION_ERROR'))
    summary.update(commit=V1.git('rev-parse', 'HEAD').decode().strip(),
                   decision_commit=V1.git('rev-parse', DECISION_COMMIT).decode().strip(),
                   cpu_seconds=cpu()-started, probe_cap=PROBE_CAP,
                   prior_phase_CPU_upper=args.spent_cpu_seconds,
                   total_phase_CPU_upper=args.spent_cpu_seconds+cpu()-started,
                   source_sha256={p: sha(root/p) for p in SOURCES},
                   raw_sha256={str(p.relative_to(root)): sha(p) for p in sorted(out.glob('P6B_*/*.json'))},
                   sealed='Probe G_S/z remain unread until L6.4; audit summary only (DL-134)')
    V1.write_once(out/'summary.json', summary)
    print(json.dumps({k: summary[k] for k in ('status', 'cpu_seconds')}, indent=2))
    return 0 if summary['status'] in ('PASS', 'PASS_REDUCED') else 2


if __name__ == '__main__':
    sys.exit(main())
