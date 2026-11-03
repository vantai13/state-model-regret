"""Doan Van Tai — DL-133: fixed D(ii) selection and parameter-only checks.

One cost per base from the saved K320 predictions; no replacement after K640.
Identity/K640 readiness does not validate A1/A2 or finite-horizon truth.
"""
from contextlib import ExitStack
import argparse
import csv
from fractions import Fraction as F
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import sys
import time
from types import SimpleNamespace

SOURCE = 'results/phase6/window_revision02/scan.csv'
SOURCE_SHA256 = 'caa11725f4c2ab9be6fd9a2f1ddfecbcc67e7f61627f24fb4ffebacd09033e64'
OUT = 'results/phase6/window_revision03'
CACHE = Path.home()/'.cache/state-model-regret/phase6/window'
DECISION_COMMIT = 'd7308d01'
ZMIN, N_MIN, BASES_MIN, K_CHECK, REF = 1.0, 10, 5, 640, 4
PHASE_CPU_CAP = 14400
SOURCES = ('experiments/P6_band/select_dii.py', 'tests/test_p6_select.py')
FIELDS = ('role', 'id', 'base_id', 'lambdaA', 'lambdaB', 'kappa', 'u', 'h', 'c',
          'x', 'P', 'c_over_Cref_pct', 'H1_K320', 'z_K320', 'H1_K640', 'z_K640',
          'K_stable', 'identity_passed', 'identity_drift', 'identity_bound')


def cpu():
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time()+children.ru_utime+children.ru_stime


def load_rows(root):
    path = Path(root)/SOURCE
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise RuntimeError('SOURCE_SCAN_CHANGED')
    with path.open() as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 1020 or len({r['id'] for r in rows}) != 1020:
        raise RuntimeError('SOURCE_SCAN_INCOMPLETE')
    return rows


def select_dii(rows):
    """Largest saved |z| per eligible base, ties to the smaller exact cost."""
    best = {}
    for row in rows:
        if row['group'] != 'Dii' or row['all'] != 'True':
            continue
        rank = (abs(float(row['z_H1'])), -F(row['c']))
        if row['base_id'] not in best or rank > best[row['base_id']][0]:
            best[row['base_id']] = (rank, row)
    return [best[bid][1] for bid in sorted(best)]


def check_rows(chosen):
    for row in chosen:
        ok = (row['truth_switch'] == 'False' and row['H1'] == '-'
              and row['H0'] == '+' and F(row['c']) > 0
              and float(row['F_new']) > float(row['F_old'])
              and math.isfinite(float(row['z_H1'])) and float(row['z_H1']) <= -ZMIN
              and all(row[f'W{i}'] == 'True' for i in range(1, 9)))
        if not ok:
            raise RuntimeError('DII_ROW_INCONSISTENT:'+row['id'])


def twins_and_control(rows, chosen):
    byid = {row['id']: row for row in rows}
    twins = []
    for row in chosen:
        twin = byid[row['base_id']+'C00']
        if not (F(twin['c']) == 0 and twin['H1'] == twin['H0'] == '+'
                and twin['W6'] == 'True'):
            raise RuntimeError('TWIN_NOT_CLEAN:'+twin['id'])
        twins.append(twin)
    control = byid.get('B001C00')
    if not control or not (control['group'] == 'A' and control['all'] == 'True'
                          and control['H1'] == control['H0'] == '-'
                          and F(control['c']) == 0):
        raise RuntimeError('NEGATIVE_CONTROL_NOT_CLEAN')
    return twins, control


def k_stable(row, pred, *, need_z):
    try:
        old, new = float(row['z_H1']), float(pred['z_H1'])
    except (KeyError, TypeError, ValueError):
        return False
    ok = (pred.get('status') == 'PREDICTED' and pred.get('H1') == row['H1']
          and math.isfinite(old) and math.isfinite(new)
          and ((new > 0 and row['H1'] == '+') or (new < 0 and row['H1'] == '-')))
    return bool(ok and (not need_z or min(abs(old), abs(new)) >= ZMIN))


def identity_passed(record):
    try:
        drift, bound = float(record['drift']), float(record['bound'])
        return bool(record['passed'] and math.isfinite(drift) and math.isfinite(bound)
                    and bound >= 0 and abs(drift) <= bound)
    except (KeyError, TypeError, ValueError):
        return False


def finite_report(value):
    """Keep invalid estimates reportable in strict JSON, never eligible for PASS."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: finite_report(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_report(v) for v in value]
    return value


def window_status(checks, identities):
    required = {row['base_id'] for row in checks}
    if not identities or not required <= identities.keys() or not all(
            identity_passed(record) for record in identities.values()):
        return 'BLOCKED_EXACT_IDENTITY'
    groups = {role: [row for row in checks if row['role'] == role]
              for role in ('D', 'twin', 'A-')}
    # Missing controls and duplicate D/twins must never yield a vacuous PASS.
    if (len(groups['A-']) != 1 or not groups['A-'][0]['K_stable']
            or any(len({r['base_id'] for r in groups[role]}) != len(groups[role])
                   for role in ('D', 'twin'))):
        return 'HOLD_K_STABILITY'
    twins = {row['base_id']: row['K_stable'] for row in groups['twin']}
    usable = [row for row in groups['D'] if row['K_stable'] and twins.get(row['base_id'])]
    return ('PASS' if len(usable) >= N_MIN
            and len({row['base_id'] for row in usable}) >= BASES_MIN else 'HOLD_K_STABILITY')


def real_deps(root):
    from unittest.mock import patch
    from experiments.P6_band import predictor as P, identity as I

    def deny(*args, **kwargs):
        raise RuntimeError('FINITE_H_TRUTH_FORBIDDEN')

    def guard():
        stack = ExitStack()
        stack.enter_context(patch.object(P.profiles, 'get', deny))
        stack.enter_context(patch.object(P.P, 'idle', deny))
        return stack

    return SimpleNamespace(cache=P.StationaryCache(root, CACHE), builder=P.build_sides,
                           identity=I.exact_identity, predict=P.predict, guard=guard)


def run(root, deps, *, result=None, on_check=None, on_base=None):
    rows = load_rows(root)
    chosen = select_dii(rows)
    check_rows(chosen)
    twins, control = twins_and_control(rows, chosen)
    members = [(r, 'D') for r in chosen]+[(r, 'twin') for r in twins]+[(control, 'A-')]
    if result is None:
        result = {}
    result.update(status='RUNNING', checks=[], identities={}, chosen=[r['id'] for r in chosen],
                  twins=[r['id'] for r in twins], control=control['id'], finite_h_truth_calls=0)
    with deps.guard():
        for bid in sorted({r['base_id'] for r, _ in members}):
            own = [(r, role) for r, role in members if r['base_id'] == bid]
            row = own[0][0]
            base = tuple(F(row[k]) for k in ('lambdaA', 'lambdaB', 'kappa', 'u', 'h'))
            ident = deps.identity(*base, deps.cache, ref=REF)
            result['identities'][bid] = finite_report(ident)
            if not identity_passed(ident):
                result.update(status='BLOCKED_EXACT_IDENTITY', blocked_base=bid)
                return result
            sides = deps.builder(*base, deps.cache, ref=REF, K=K_CHECK)
            for row, role in own:
                pred = deps.predict(sides, F(row['c']))
                check = dict(role=role, id=row['id'], base_id=bid,
                             **{k: row[k] for k in ('lambdaA', 'lambdaB', 'kappa', 'u', 'h', 'c', 'x', 'P')},
                             c_over_Cref_pct=100*float(F(row['c']))/float(row['Cref_H1']),
                             H1_K320=row['H1'], z_K320=float(row['z_H1']),
                             H1_K640=pred.get('H1'), z_K640=finite_report(pred.get('z_H1')),
                             K_stable=k_stable(row, pred, need_z=role != 'twin'),
                             identity_passed=True, identity_drift=float(ident['drift']),
                             identity_bound=float(ident['bound']))
                result['checks'].append(check)
                if on_check:
                    on_check(check)
            del sides
            if on_base:
                on_base(bid)
    result['status'] = window_status(result['checks'], result['identities'])
    result['usable_D'] = [row['id'] for row in result['checks'] if row['role'] == 'D'
                          and row['K_stable'] and next(t['K_stable'] for t in result['checks']
                            if t['role'] == 'twin' and t['base_id'] == row['base_id'])]
    return result


def execute(root, out, deps_factory, metadata):
    """Reserve the attempt before numerical work; preserve completed rows on error."""
    from experiments.P5_panel import run as V1
    started = cpu()
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    result = dict(metadata, status='EXECUTION_FAILURE', checks=[], identities={}, finite_h_truth_calls=0)
    with (out/'candidates.csv').open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        stream.flush()

        def emit(row):
            writer.writerow(row)
            stream.flush()
            os.fsync(stream.fileno())

        try:
            run(root, deps_factory(root), result=result, on_check=emit,
                on_base=lambda bid: print(f'{bid} CHECK_COMPLETE CPU={cpu()-started:.1f}s',
                                           file=sys.stderr, flush=True))
        except Exception as exc:
            result.update(status='RESOURCE_CPU' if isinstance(exc, TimeoutError) else 'EXECUTION_FAILURE',
                          error=f'{type(exc).__name__}: {exc}')
    measured = cpu()-started
    result.update(cpu_seconds=round(measured, 1), cpu_seconds_measured=measured,
                  total_Phase6_CPU_upper_seconds=metadata['prior_CPU_upper_seconds']+measured)
    if result['total_Phase6_CPU_upper_seconds'] > PHASE_CPU_CAP:
        result['readiness_before_resource_check'] = result['status']
        result['status'] = 'RESOURCE_CPU'
    V1.write_once(out/'summary.json', result)
    return result


def main():
    from experiments.P6_band import window as W
    from experiments.P5_panel import run as V1
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spent-cpu-seconds', type=float, required=True)
    args = parser.parse_args()
    V1.require(math.isfinite(args.spent_cpu_seconds)
               and 1200 <= args.spent_cpu_seconds < PHASE_CPU_CAP-2, 'PRIOR_PHASE_BUDGET_REQUIRED')
    W.preflight()
    V1.git('merge-base', '--is-ancestor', DECISION_COMMIT, 'HEAD')
    V1.require('### DL-133 ' in V1.git('show', DECISION_COMMIT+':notes/02_decision_log.md').decode(),
               'DL133_NOT_COMMITTED_BEFORE_CODE')
    for path in SOURCES:
        V1.require((V1.ROOT/path).read_bytes() == V1.git('show', 'HEAD:'+path), 'UNCOMMITTED:'+path)
    rows = load_rows(V1.ROOT)
    chosen = select_dii(rows)
    twins, control = twins_and_control(rows, chosen)
    blocked = W.collision_keys()
    for row in chosen+twins+[control]:
        physical = tuple(str(F(row[k])) for k in ('lambdaA', 'lambdaB', 'u', 'kappa', 'h', 'c'))
        V1.require(physical not in blocked, 'COLLISION:'+row['id'])
    previous = V1.load(V1.ROOT/'results/phase6/window_revision02/summary.json')
    legacy_window = 'experiments/P6_band/window.py'
    original = V1.git('show', '34ed25d0:'+legacy_window)
    expected = original.replace(b"set(changed)<={'experiments/P6_band/window.py'}",
                                b"set(changed)<={'experiments/P6_band/window.py','experiments/P6_band/select_dii.py'}")
    V1.require((V1.ROOT/legacy_window).read_bytes() == expected, 'WINDOW_COMPATIBILITY_CHANGE_ONLY')
    files = {**{p: h for p, h in previous['source_sha256'].items() if p != legacy_window},
             **previous['historical_sha256']}
    for path, digest in files.items():
        V1.require(hashlib.sha256((V1.ROOT/path).read_bytes()).hexdigest() == digest,
                   'HISTORICAL_SOURCE_CHANGED:'+path)
    metadata = dict(commit=V1.git('rev-parse', 'HEAD').decode().strip(),
                    decision_commit=V1.git('rev-parse', DECISION_COMMIT).decode().strip(),
                    source=SOURCE, source_sha256=SOURCE_SHA256, K_check=K_CHECK, ref=REF,
                    z_min_pct=ZMIN, N_min=N_MIN, bases_min=BASES_MIN,
                    prior_CPU_upper_seconds=args.spent_cpu_seconds,
                    Phase6_CPU_cap_seconds=PHASE_CPU_CAP, Part_A_CPU_kill_cap=None,
                    collision_union_keys=len(blocked), planned_member_keys=len(chosen)*2+1,
                    source_sha256_files={p: hashlib.sha256((V1.ROOT/p).read_bytes()).hexdigest()
                                         for p in (*SOURCES, legacy_window)},
                    legacy_window_compatibility=dict(original_sha256=hashlib.sha256(original).hexdigest(),
                        current_sha256=hashlib.sha256(expected).hexdigest(), change='allow independent select_dii.py only'),
                    historical_sha256=files)
    # D6 removes the old Part A kill cap, while retaining the total Phase 6 cap.
    def exhausted(signum, frame):
        raise TimeoutError('PHASE6_CPU_CAP')
    signal.signal(signal.SIGXCPU, exhausted)
    current = time.process_time()
    remaining = PHASE_CPU_CAP-args.spent_cpu_seconds-2
    resource.setrlimit(resource.RLIMIT_CPU, (math.floor(current+remaining), math.ceil(current+remaining)+1))
    result = execute(V1.ROOT, V1.ROOT/OUT, real_deps, metadata)
    print(json.dumps({k: result[k] for k in ('status', 'cpu_seconds')}, indent=2))
    return 0 if result['status'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
