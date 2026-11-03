"""Doan Van Tai — L6.2 Part C / L6.3 (DL-135): frozen D(ii) panel, signed-G_S labels, one run.

Subcommands
  freeze   build results/phase6/predictions.jsonl from DL-133 candidates + DL-134 probe plan
           (parameter-only; written once, committed before any panel call)
  anchor   positive control: replay one probe call through THIS runner (fields must match, values
           are never printed) and label two stored anchors of opposite G_S sign
  run      the one panel run (needs the DL-135 Gate D-entry marker)
  rescore  recompute every label and verdict from the raw rows; must match summary.json
Rules (DL-134): labels on G_S only, no sign gate; verdict 0.8 N / 0.1 N; A- must be '-';
stop on BUG, execution/resource failure, budget, A- failure. No retry, no resume.
"""
import argparse
import ctypes
import hashlib
import json
import math
import os
import resource
import re
import signal
import subprocess
import sys
import time
from fractions import Fraction as F
from pathlib import Path

from experiments.P6_band import probe as B
from experiments.P6_band import select_dii as S

PREDICTIONS = 'results/phase6/predictions.jsonl'
PLAN = 'notes/design/analysis_plan_v2.md'
PANEL_OUT = 'results/phase6/panel'
SUMMARY = 'results/phase6/summary.json'
ANCHOR_OUT = 'results/phase6/gate_anchor'
CACHE = Path.home()/'.cache/state-model-regret/phase6'
LEVELS, MAIN, EPS_E = B.LEVELS, B.MAIN, B.EPS_E
PANEL_BUDGET, PHASE_CAP = 7200, 14400
CALL_CPU_CAP, CALL_WALL_CAP, RESERVE = 1800, 3600, 1.0
GATE_MARKER = 'P6_GATE_D_ENTRY'
ANCHOR_PROBE = 'P6B_B027C02'
SOURCES = ('experiments/P6_band/run.py', 'tests/test_p6_run.py')


# ---------- 1. freeze: members, order, predictions (no truth) ----------

def ordered(members):
    """A- first (sanity), then per base in ID order: twin, then D (pairs finish together)."""
    first = [m for m in members if m['role'] == 'A-']
    rest = sorted((m for m in members if m['role'] != 'A-'),
                  key=lambda m: (m['base_id'], 0 if m['role'] == 'twin' else 1))
    return first+rest


def build_predictions(candidates, scan, kept):
    byid = {r['id']: r for r in scan}
    out = []
    for r in candidates:
        if r['id'] not in kept:
            continue
        s = byid[r['id']]
        a, b, k, u, h, c = (F(s[n]) for n in ('lambdaA', 'lambdaB', 'kappa', 'u', 'h', 'c'))
        out.append(dict(id='P6_'+r['id'], scan_id=r['id'], role=r['role'], base_id=r['base_id'],
                        parameters=[str(v) for v in (a, b, k, u/2, h, c)],      # engine eta = u/2
                        H1=r['H1_K640'], H0=s['H0'], z_H1_K640=float(r['z_K640']),
                        z_H1_K320=float(r['z_K320']), c_over_Cref_pct=float(r['c_over_Cref_pct'])))
    return ordered(out)


def load_predictions(root):
    return [json.loads(line) for line in (Path(root)/PREDICTIONS).read_text().splitlines()]


# ---------- 2. labels and verdict (pure) ----------

def label(rows, eps=EPS_E):
    from experiments.P4_A1.checks import d_normalized
    reasons = B.gs_readiness(rows)
    fine = rows[MAIN]
    cref = F(fine['Cref'])
    z = F(fine['G_S'])/cref
    d = d_normalized(rows, MAIN)[0]['G_S']
    name = 'U' if reasons else '+' if z >= eps+d else '-' if z <= -eps-d else 'U'
    return dict(label=name, z_pct=float(100*z), d_pp=float(100*d), ready=not reasons, reasons=reasons,
                G_S_abs=float(abs(F(fine['G_S']))), G_S_signed=float(F(fine['G_S'])), Cref=float(cref),
                S_pct=float(100*F(fine['G_S_M1'])/cref), M_pct=float(100*F(fine['G_M_S1'])/cref),
                Gamma_pct=float(100*F(fine['Gamma'])/cref))


def verdict(labels):
    n = len(labels)
    if not n:
        return 'INCONCLUSIVE'
    if not set(labels) <= {'+', '-', 'U'}:
        raise ValueError('INVALID_LABEL')
    need, ucap = math.ceil(F(8, 10)*n), math.floor(F(1, 10)*n)
    neg, pos, u = labels.count('-'), labels.count('+'), labels.count('U')
    if u > ucap:
        return 'INCONCLUSIVE'
    if neg >= need:
        return 'H1_SUPPORTED'
    if pos >= need:
        return 'H0_SUPPORTED'
    return 'MIXED'


def score(points, members, stop, rows_by_id=None):
    """Everything here is a function of labels; rows_by_id only for the eps=1% sensitivity."""
    role = {m['id']: m['role'] for m in members}
    d_ids = [m['id'] for m in members if m['role'] == 'D']
    complete = (stop is None and bool(d_ids) and all(m['id'] in points for m in members)
                and len([m for m in members if m['role']=='A-']) == 1
                and all(points[m['id']]['label']=='-' for m in members if m['role']=='A-'))
    d_labels = [points[i]['label'] for i in d_ids if i in points]
    out = dict(N_D=len(d_ids), D_counts={k: d_labels.count(k) for k in '+-U'},
               verdict=verdict(d_labels) if complete else 'INCOMPLETE',
               A_minus={i: p['label'] for i, p in points.items() if role[i] == 'A-'})
    twins = {m['base_id']: m['id'] for m in members if m['role'] == 'twin'}
    if twins:
        pairs = [m['base_id'] for m in members if m['role'] == 'D' and m['id'] in points
                 and twins.get(m['base_id']) in points
                 and points[twins[m['base_id']]]['label'] == '+' and points[m['id']]['label'] == '-']
        out.update(twin_counts={k: [points[t]['label'] for t in twins.values() if t in points].count(k) for k in '+-U'},
                   intervention_pairs=pairs,
                   intervention_wording_allowed=complete and out['verdict']=='H1_SUPPORTED'
                       and len(pairs) >= math.ceil(F(8, 10)*len(d_ids)))
    if complete and rows_by_id is not None:
        out['verdict_eps_1pct_descriptive'] = verdict([label(rows_by_id[i], F(1, 100))['label'] for i in d_ids])
    return out


# ---------- 3. one call = one subprocess, write-once ----------

def children_cpu():
    u = resource.getrusage(resource.RUSAGE_CHILDREN)
    return u.ru_utime+u.ru_stime


def launch(member, level, path, *, cpu_limit, kind='panel'):
    return B.launch(member, level, path, cpu_limit=cpu_limit, kind=kind,
                    worker_module='experiments.P6_band.run')


def worker(kind, member_id, K, ref, fd, limit):
    from experiments.P5_panel import run as V1
    from experiments.P4_03_map_audit.common import canonical
    from experiments.P4_09_stationary.discovery import forbidden
    root = V1.ROOT
    resource.setrlimit(resource.RLIMIT_CPU, (max(1,math.ceil(limit)),max(2,math.ceil(limit)+1)))
    V1.require(kind in ('anchor','panel'), 'UNREGISTERED_WORKER_KIND')
    preflight(root, gate=kind=='panel', worker=True)
    if kind == 'anchor':
        points = V1.load(root/B.OUT/'summary.json')['points']
        member = next(p for p in points if p['id'] == member_id == ANCHOR_PROBE)
    else:
        member = next(m for m in load_predictions(root) if m['id'] == member_id)
    expected = (root/ANCHOR_OUT/f'{member_id}_level_{K}_{ref}.json' if kind=='anchor'
                else root/PANEL_OUT/member_id/f'level_{K}_{ref}.json')
    B.reservation(root,member,(K,ref),fd,expected)
    V1.require(kind!='anchor' or (K,ref)==MAIN, 'ANCHOR_LEVEL_NOT_REGISTERED')
    V1.require(canonical(member['parameters']) not in forbidden(), 'CF_OR_SEALED_COLLISION')
    json.dump(V1.evaluate(dict(id=member['id'], parameters=member['parameters']), (K, ref),
                          CACHE/kind), sys.stdout, allow_nan=False)


# ---------- 4. the one run ----------

def run_panel(members, *, call, out, budget, used_cpu):
    from experiments.P5_panel import run as V1
    calls, points, stop, rows_by_id = [], {}, None, {}
    for m in members:
        rows = {}
        for lv in LEVELS:
            remaining = budget-used_cpu()-RESERVE
            if remaining <= 0:
                stop = 'BUDGET'
                break
            try:
                row = call(m, lv, Path(out)/m['id']/f'level_{lv[0]}_{lv[1]}.json',
                           cpu_limit=min(CALL_CPU_CAP, remaining))
            except BaseException as exc:
                stop = 'EXECUTION_INTERRUPTED' if isinstance(exc,KeyboardInterrupt) else 'EXECUTION:CALL_EXCEPTION:'+type(exc).__name__
                break
            calls.append(dict(id=m['id'], level=list(lv), status=row['status'], **row['resources']))
            try:
                stop = V1.inspect_row(row, m, lv)                     # EXECUTION:... or BUG:... or None
            except (KeyError, ValueError, RuntimeError, TypeError) as exc:
                stop = 'BUG:ROW_SCHEMA:'+str(exc)
            print(m['id'], lv, 'STOP' if stop else 'COMPLETED', f'{used_cpu():.0f}s', flush=True)
            if stop:
                break
            rows[lv] = row
        if stop:
            break
        try:points[m['id']] = label(rows)
        except (KeyError,ValueError,TypeError,ZeroDivisionError):
            stop='BUG:LABEL_SCHEMA';break
        rows_by_id[m['id']] = rows
        if m['role'] == 'A-' and points[m['id']]['label'] != '-':
            stop = 'A_MINUS_FAILED'
            break
    return calls, points, stop, rows_by_id


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gate_record(root):
    from experiments.P5_panel import run as V1
    text=(root/'notes/02_decision_log.md').read_text()
    V1.require((root/'notes/02_decision_log.md').read_bytes()==V1.git('show','HEAD:notes/02_decision_log.md'),
               'UNCOMMITTED_GATE')
    matches=re.findall(r'<!-- P6_GATE_D_ENTRY\s+(.*?)\s*-->',text,re.S)
    V1.require(len(matches)==1 and '### DL-135 ' in text, 'GATE_D_ENTRY_REQUIRED')
    record=json.loads(matches[0])
    V1.require(record['status']=='GO' and record['policy']=='STRICT_NO_RETRY', 'GATE_NOT_GO')
    V1.require((record['panel_budget'],record['phase_cap'],record['call_cpu_cap'],record['call_wall_cap'])
               ==(PANEL_BUDGET,PHASE_CAP,CALL_CPU_CAP,CALL_WALL_CAP),'GATE_BUDGET_CHANGED')
    V1.git('merge-base','--is-ancestor',record['runner_commit'],'HEAD')
    required=set(SOURCES+B.SOURCES+(PREDICTIONS,PLAN,B.OUT+'/summary.json',
                                    ANCHOR_OUT+'/report.json','notes/phases/PHASE_6.md',
                                    'experiments/P6_band/window.py'))
    V1.require(set(record['files'])==required,'INCOMPLETE_FREEZE_FILES')
    for path,digest in record['files'].items():
        V1.require(sha(root/path)==digest,'FROZEN_SHA_MISMATCH:'+path)
    for path in SOURCES+B.SOURCES+(PREDICTIONS,PLAN,'experiments/P6_band/window.py'):
        V1.require((root/path).read_bytes()==V1.git('show',record['runner_commit']+':'+path),
                   'FROZEN_RUNNER_CHANGED:'+path)
    report=V1.load(root/ANCHOR_OUT/'report.json')
    V1.require(report['runner_commit']==record['runner_commit'] and report['status']=='PASS'
               and report['predictions_sha256']==sha(root/PREDICTIONS)
               and report['plan_sha256']==sha(root/PLAN),'ANCHOR_NOT_BOUND_TO_FREEZE')
    V1.require(sha(root/ANCHOR_OUT/f'{ANCHOR_PROBE}_level_640_4.json')==report['replay_sha256'],
               'ANCHOR_RAW_CHANGED')
    V1.require(record['prior_phase_CPU_upper']>=V1.load(root/B.OUT/'summary.json')['total_phase_CPU_upper'],
               'PRIOR_PHASE_BUDGET_RESET')
    return record


def preflight(root, *, gate, worker=False):
    from experiments.P5_panel import run as V1
    B.preflight(root)
    for source in SOURCES+(PREDICTIONS, PLAN):
        V1.require((root/source).read_bytes() == V1.git('show', 'HEAD:'+source), 'UNCOMMITTED:'+source)
    V1.require(not V1.git('status', '--porcelain', '--untracked-files=no').strip(), 'TRACKED_TREE_DIRTY')
    probe=V1.load(root/B.OUT/'summary.json')
    V1.require(probe['status'] in ('PASS','PASS_REDUCED'),'PROBE_NOT_PASSED')
    for path,digest in probe['source_sha256'].items():
        V1.require(sha(root/path)==digest,'PROBE_SOURCE_CHANGED:'+path)
    expected=build_predictions(B.load_panel(root),S.load_rows(root),set(probe['decision']['members']))
    V1.require(load_predictions(root)==expected,'PREDICTIONS_NOT_MECHANICAL_PROBE_PLAN')
    if gate:
        gate_record(root)
        if not worker:
            V1.require(not (root/SUMMARY).exists() and not (root/PANEL_OUT).exists()
                       and not (CACHE/'panel').exists(), 'PANEL_ALREADY_ATTEMPTED')
    return V1


def cmd_freeze(root):
    from experiments.P5_panel import run as V1
    V1.require(not (root/PREDICTIONS).exists(), 'PREDICTIONS_ALREADY_FROZEN')
    probe = V1.load(root/B.OUT/'summary.json')
    V1.require(probe['status'] in ('PASS', 'PASS_REDUCED'), 'PROBE_NOT_PASSED')
    members = build_predictions(B.load_panel(root), S.load_rows(root), set(probe['decision']['members']))
    with (root/PREDICTIONS).open('x') as stream:
        for m in members:
            stream.write(json.dumps(m, sort_keys=True)+'\n')
    print(len(members), 'members frozen; sha256', sha(root/PREDICTIONS))


def cmd_anchor(root):
    V1 = preflight(root, gate=False)
    out = root/ANCHOR_OUT
    V1.require(not out.exists() and not (CACHE/'anchor').exists(), 'ANCHOR_ALREADY_ATTEMPTED')
    out.mkdir(parents=True,exist_ok=False)
    V1.require(ctypes.CDLL(None).prctl(36,1,0,0,0)==0,'SUBREAPER_REQUIRED')
    probe_path=root/B.OUT/ANCHOR_PROBE/'level_640_4.json'
    V1.require(sha(probe_path)==V1.load(root/B.OUT/'summary.json')['raw_sha256'][str(probe_path.relative_to(root))],
               'SEALED_PROBE_CHANGED')
    old = V1.load(probe_path)
    member = dict(id=ANCHOR_PROBE, parameters=old['parameters'])
    new = launch(member, MAIN, out/f'{ANCHOR_PROBE}_level_640_4.json', cpu_limit=CALL_CPU_CAP, kind='anchor')
    report = dict(runner_commit=V1.git('rev-parse', 'HEAD').decode().strip(), replay_status=new['status'],
                  field_mismatch=[k for k in (*V1.FIELDS,'parameters','K','ref','id','CF_computed') if new.get(k) != old.get(k)],
                  replay_bugs=V1.bug_reasons(new) if new['status'] == 'COMPLETED' else ['NOT_COMPLETED'],
                  replay_cpu=new['resources']['cpu_seconds'], labels={}, panel_calls=0,
                  predictions_sha256=sha(root/PREDICTIONS),plan_sha256=sha(root/PLAN),
                  probe_row_sha256=sha(root/B.OUT/ANCHOR_PROBE/'level_640_4.json'),
                  replay_sha256=sha(out/f'{ANCHOR_PROBE}_level_640_4.json'))
    for cid, expected in (('P43_0021', '-'), ('P43_0018', '+')):
        rows = {lv: V1.load(root/f'results/lessons/l4_3/a1_sv/native/{cid}/level_{lv[0]}_{lv[1]}.json') for lv in LEVELS}
        report['labels'][cid] = dict(expected=expected, got=label(rows)['label'])
    report['status'] = 'PASS' if (new['status'] == 'COMPLETED' and not report['field_mismatch']
                                  and not report['replay_bugs']
                                  and all(v['expected'] == v['got'] for v in report['labels'].values())) else 'FAIL'
    V1.write_once(out/'report.json', report)
    print(json.dumps({k: report[k] for k in ('status', 'field_mismatch', 'labels')}, indent=2))
    return 0 if report['status'] == 'PASS' else 1


def cmd_run(root, spent):
    V1 = preflight(root, gate=True)
    record=gate_record(root)
    V1.require(spent is not None and math.isfinite(spent) and spent==record['prior_phase_CPU_upper']
               and spent+PANEL_BUDGET <= PHASE_CAP, 'PHASE_BUDGET_EXCEEDED_OR_RESET')
    members = load_predictions(root)
    (root/PANEL_OUT).mkdir(parents=True,exist_ok=False)
    V1.require(ctypes.CDLL(None).prctl(36,1,0,0,0)==0,'SUBREAPER_REQUIRED')
    start = B.cpu()
    calls, points, stop, rows_by_id = run_panel(
        members, call=launch, out=root/PANEL_OUT, budget=PANEL_BUDGET,
        used_cpu=lambda: B.cpu()-start)
    result = dict(commit=V1.git('rev-parse', 'HEAD').decode().strip(), predictions_sha256=sha(root/PREDICTIONS),
                  plan_sha256=sha(root/PLAN), stop_reason=stop, calls=calls, points=points,
                  cpu_seconds=round(B.cpu()-start, 1),
                  budget_CPU_seconds=PANEL_BUDGET, prior_phase_CPU_upper=spent,
                  **score(points, members, stop, rows_by_id))
    V1.write_once(root/SUMMARY, result)
    print(json.dumps({k: result[k] for k in ('stop_reason', 'verdict', 'cpu_seconds')}, indent=2))
    return 0


def cmd_rescore(root):
    from experiments.P5_panel import run as V1
    if root == V1.ROOT:
        gate_record(root)
    saved = V1.load(root/SUMMARY)
    members = load_predictions(root)
    points, rows_by_id, calls, stop = {}, {}, [], None
    for m in members:
        rows={}
        for lv in LEVELS:
            path=root/PANEL_OUT/m['id']/f'level_{lv[0]}_{lv[1]}.json'
            if not path.exists() or not path.stat().st_size:
                stop='BUDGET' if saved['stop_reason']=='BUDGET' and saved.get('cpu_seconds',0)>=PANEL_BUDGET-RESERVE else 'EXECUTION_INTERRUPTED'
                break
            row=V1.load(path)
            calls.append(dict(id=m['id'],level=list(lv),status=row['status'],**row['resources']))
            try:stop=V1.inspect_row(row,m,lv)
            except (KeyError,ValueError,RuntimeError,TypeError):stop='BUG:ROW_SCHEMA'
            if stop:break
            rows[lv]=row
        if stop:break
        rows_by_id[m['id']]=rows
        try:points[m['id']]=label(rows)
        except (KeyError,ValueError,TypeError,ZeroDivisionError):
            stop='BUG:LABEL_SCHEMA';break
        if m['role']=='A-' and points[m['id']]['label']!='-':
            stop='A_MINUS_FAILED';break
    again = score(points, members, stop, rows_by_id)
    ok = (stop==saved['stop_reason'] and points == saved['points']
          and all(saved[k] == v for k, v in again.items())
          and ('calls' not in saved or calls==saved['calls']))
    print('RESCORE', 'MATCH' if ok else 'MISMATCH')
    return 0 if ok else 1


def main(argv=None):
    from experiments.P5_panel import run as V1
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('freeze', 'anchor', 'run', 'rescore', 'worker'))
    p.add_argument('args', nargs='*')
    p.add_argument('--spent-cpu-seconds', type=float)
    a = p.parse_args(argv)
    root = V1.ROOT
    if a.command == 'worker':
        kind, mid, K, ref, fd, limit = a.args
        return worker(kind, mid, int(K), int(ref), int(fd), float(limit))
    return dict(freeze=lambda: cmd_freeze(root), anchor=lambda: cmd_anchor(root),
                run=lambda: cmd_run(root, a.spent_cpu_seconds), rescore=lambda: cmd_rescore(root))[a.command]()


if __name__ == '__main__':
    sys.exit(main())
