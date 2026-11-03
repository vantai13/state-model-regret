"""Doan Van Tai — L6.2 A parameter-only window, not a truth experiment."""
import argparse
import csv
import ctypes
from fractions import Fraction as F
import hashlib
import itertools
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
from experiments.P6_band import predictor as P
from experiments.P6_band import identity as I
from experiments.P5_panel import run as V1
from experiments.explore_mech.scan import key, forbidden_keys

ROOT = V1.ROOT
OUT = ROOT/'results/phase6/window_revision02'
PREVIOUS = ROOT/'results/phase6/window_revision01'
CACHE = Path.home()/'.cache/state-model-regret/phase6/window'
SOURCES = ('experiments/P6_band/__init__.py', 'experiments/P6_band/predictor.py',
           'experiments/P6_band/identity.py', 'experiments/P6_band/window.py', 'tests/test_p6_predictor.py')
HISTORY = tuple('results/phase6/window/'+n for n in ('scan.csv','summary.json','diagnostic_B017.json'))+(
    'results/phase6/window_attempt01_failed/summary.json',
    'results/phase6/window_revision01/scan.csv','results/phase6/window_revision01/summary.json')
IDENTITY_BASES = ('B001','B002','B006','B011','B016','B017','B042')
CAP = 1800
RHO, PMIN, ZMIN, MEAN_TOL = F(1,4), F(30), F(1), .005  # old tau: descriptive only (DL-131)
COSTS = tuple(map(F, ('0','1/32','1/16','1/8','3/16','1/4','3/8','1/2','3/4','1',
                     '5/4','3/2','7/4','2','5/2','3','7/2','4','5','6')))
K, REF, NMIN = 320, 4, 10


def cpu():
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time()+usage.ru_utime+usage.ru_stime


def bases():
    for a,k,h,u,x in itertools.product(map(F,('7','15/2')), map(F,('1/10','1/5')),
            map(F,('8','16')), map(F,('1','3/2')),
            map(F,('-2/3','-1/2','-1/3','-1/4','1/6','1/4','1/3'))):
        b = a+x*u
        if min(a,b)>=F(13,2) and max(a+u,b+u)<10 and h/k*abs(b-a)>=PMIN:
            yield a,b,k,u,h


def parameters(base, c):
    a,b,k,u,h = base
    return [str(v) for v in (a,b,k,u/2,h,F(c))]  # engine eta = u/2


def collision_keys():
    """Only design fields are consumed; never convert any outcome column."""
    blocked = set(forbidden_keys())
    inv = V1.load(ROOT/'results/lessons/l3r_7/lean_close/collision_inventory_v3.json')
    for r in inv['records']:
        blocked.add(tuple(str(F(v)) for v in r['key'].split('|')))
    for path in sorted((ROOT/'results/explore_mech/cases').glob('*.json')):
        for case in V1.load(path):
            blocked.add(key(case['parameters']))
    for path in sorted((ROOT/'results/explore_p4').glob('*/metrics.csv')):
        with path.open() as stream:
            for row in csv.DictReader(stream):
                blocked.add(tuple(str(F(row[n])) for n in ('lamA','lamB','u','kappa','h'))+('0',))
    for path in (ROOT/'results/phase6/probe').glob('**/*.json'):
        r = V1.load(path)
        if isinstance(r,dict) and 'parameters' in r:
            blocked.add(key(r['parameters']))
    return blocked


def flags(base, c, pred, zero, lower, upper, blocked):
    valid = pred['status']=='PREDICTED'
    a,b,k,u,h = base
    group = 'NONE'
    if valid:
        if (b<a and c>0 and pred['truth_switch'] and pred['H1']=='+' and pred['H0']=='-'):
            group = 'Di'
        elif (0<(b-a)/u<P.THETA0-P.THETA1*u and c>0 and not pred['truth_switch']
              and pred['H1']=='-' and pred['H0']=='+'):
            group = 'Dii'
        elif pred['H1']==pred['H0']:
            group = 'A'
    out = dict(group=group, W1=min(a,b)>=F(13,2) and max(a+u,b+u)<10 and a!=b
               and h<=16 and F(1,10)<=k<=F(3,10), W2=h/k*abs(b-a)>=PMIN,
               W3=valid and (group!='Di' or pred['c_over_stake']<=float(RHO)),
               W4=valid and abs(pred['z_H1'])>=float(ZMIN), W5=group!='NONE',
               W6=key(parameters(base,c)) not in blocked,
               W7=valid and all(q['status']=='PREDICTED' and q['H1']==pred['H1'] for q in (lower,upper)),
               W8=zero['status']=='PREDICTED' and zero['H1']==zero['H0'])
    out['must'] = all(out[f'W{i}'] for i in range(1,7))
    out['all'] = out['must'] and out['W7'] and out['W8']
    return out


def capped(rows, count):
    """Stable round-robin: one cost/base, then a second. No optimization on truth."""
    groups = {}
    for r in rows:
        groups.setdefault(r['base_id'],[]).append(r)
    ordered = [groups[k] for k in sorted(groups)]
    out = [g[i] for i in (0,1) for g in ordered if len(g)>i]
    return out[:count]


def witness(rows):
    d1 = [r for r in rows if r['all'] and r['group']=='Di']
    d2 = [r for r in rows if r['all'] and r['group']=='Dii']
    selected = []
    for n1 in (7,8,9):
        one,two = capped(d1,n1),capped(d2,NMIN-n1)
        cand = one+two
        counts = {b:sum(r['base_id']==b for r in cand) for b in {r['base_id'] for r in cand}}
        if len(one)==n1 and len(cand)==NMIN and len(counts)>=5 and max(counts.values())<=2:
            selected=cand; break
    controls=[]
    for sign in ('+','-'):
        pool=[r for r in rows if r['all'] and r['group']=='A' and r['H1']==sign]
        if pool:controls.append(pool[0])
    return dict(D=[r['id'] for r in selected], A=[r['id'] for r in controls],
                D_bases=len({r['base_id'] for r in selected}),
                Di=sum(r['group']=='Di' for r in selected), W9_met=bool(selected),
                controls_both_signs=len(controls)==2)


def preflight():
    V1.check_frozen()
    from experiments.P4_A1.config import verify_run
    from experiments.P4_03_map_audit.common import verify_prereg
    for name in V1.RUNS: verify_run(name)
    verify_prereg()
    for source in SOURCES:
        V1.require((ROOT/source).read_bytes()==V1.git('show','HEAD:'+source), 'UNCOMMITTED:'+source)
    V1.require(not V1.git('status','--porcelain','--untracked-files=no').strip(), 'TRACKED_TREE_DIRTY')
    V1.require('### DL-132 ' in (ROOT/'notes/02_decision_log.md').read_text(), 'REVISION_REQUIRED')
    for path in HISTORY:
        V1.require((ROOT/path).read_bytes()==V1.git('show','bf972c9c:'+path),'HISTORY_CHANGED:'+path)


def load_identity_samples():
    """Reuse c-independent certificates only while all shared code is unchanged."""
    saved = V1.load(PREVIOUS/'summary.json')
    V1.require(saved['ref']==REF and saved['identity_base_ids']==list(IDENTITY_BASES),'IDENTITY_SCOPE_CHANGED')
    changed=V1.git('diff','--name-only','bf972c9c','--','src','experiments').decode().splitlines()
    V1.require(set(changed)<={'experiments/P6_band/window.py','experiments/P6_band/select_dii.py'},'IDENTITY_DEPENDENCY_CHANGED')
    for path in ('experiments/P6_band/identity.py','experiments/P6_band/predictor.py'):
        V1.require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==saved['source_sha256'][path],
                   'IDENTITY_SOURCE_CHANGED:'+path)
    samples={bid:saved['identities'][bid] for bid in IDENTITY_BASES}
    V1.require(all(r['passed'] and abs(r['drift'])<=r['bound'] for r in samples.values()),'INVALID_REUSED_IDENTITY')
    return samples


def load_previous_rows():
    with (PREVIOUS/'scan.csv').open() as stream:rows=list(csv.DictReader(stream))
    V1.require(len(rows)==510 and len({r['id'] for r in rows})==510,'PREVIOUS_SCAN_INCOMPLETE')
    return rows


def replay_invariant(rows, previous):
    """Compare the CSV representation of EVERY old field, not a float tolerance."""
    current={r['id']:r for r in rows};mismatches=[]
    for old in previous:
        new=current.get(old['id'],{})
        fields=[k for k,v in old.items() if k not in new or ('' if new[k] is None else str(new[k]))!=v]
        if fields:mismatches.append(dict(id=old['id'],fields=fields))
    return dict(passed=not mismatches,rows_compared=len(previous),mismatches=mismatches)


def candidate_status(counts, w):
    if w['W9_met'] and w['controls_both_signs']:
        return 'READY_FOR_FINAL_CHECKS'
    return 'STOP_INSUFFICIENT_WINDOW'


def validate_witness(rows, w, cache, identities, *, builder, identity_checker):
    """Veto the fixed 320 witness; never replace failed points to rescue it."""
    chosen = set(w['D']+w['A'])
    selected = [r for r in rows if r['id'] in chosen]
    checked = []
    for bid in sorted({r['base_id'] for r in selected}):
        members = [r for r in selected if r['base_id']==bid]
        r = members[0]
        base = tuple(F(r[k]) for k in ('lambdaA','lambdaB','kappa','u','h'))
        if bid not in identities:
            identities[bid] = identity_checker(*base,cache,ref=REF)
        if not identities[bid]['passed']:
            return dict(status='BLOCKED_EXACT_IDENTITY',base_id=bid,**identities[bid]),checked
        sd = builder(*base,cache,ref=REF,K=640)
        for r in members:
            pred = P.predict(sd,F(r['c']))
            stable = (pred['status']=='PREDICTED' and pred['H1']==r['H1']
                      and abs(pred['z_H1'])>=float(ZMIN) and abs(r['z_H1'])>=float(ZMIN))
            r.update(K_stable=stable,H1_K640=pred.get('H1'),z_H1_K640=pred.get('z_H1'))
            checked.append(dict(id=r['id'],K_stable=stable,H1_K320=r['H1'],
                                z_H1_K320=r['z_H1'],prediction_K640=pred))
    return None,checked


def write_csv(path, rows, mode='w'):
    with Path(path).open(mode,newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=list(rows[0]))
        if mode!='a':writer.writeheader()
        writer.writerows(rows);stream.flush();os.fsync(stream.fileno())


def compute(out=OUT, *, builder=P.build_sides, identity_checker=I.exact_identity,
            identity_samples=None, previous_rows=None):
    """Worker emits only design predictions; guard forbids true cost construction."""
    blocked=collision_keys(); cache=P.StationaryCache(ROOT,CACHE)
    rows=[]; timings=[]; diagnostic_failure=None; identities=dict(identity_samples or {}); refined=[]
    replay=dict(passed=None,rows_compared=0,mismatches=[])
    def deny(*a,**kw):raise RuntimeError('FINITE_H_TRUTH_FORBIDDEN')
    with patch.object(P.profiles,'get',deny),patch.object(P.P,'idle',deny):
        for index,base in enumerate(bases(),1):
            started=cpu()
            sd=builder(*base,cache,ref=REF,K=K)
            diag=P.distribution_checks(sd)
            bid=f'B{index:03d}'
            if bid in IDENTITY_BASES:
                if bid not in identities:identities[bid]=identity_checker(*base,cache,ref=REF)
                if not identities[bid]['passed']:
                    diagnostic_failure=dict(status='BLOCKED_EXACT_IDENTITY',base_id=bid,**identities[bid])
            timings.append(dict(base_id=f'B{index:03d}',cpu_seconds=cpu()-started))
            if diagnostic_failure:
                break
            predictions={}
            def prediction(c):
                if c not in predictions:predictions[c]=P.predict(sd,c)
                return predictions[c]
            zero=prediction(F(0))
            for j,c in enumerate(COSTS):
                p=prediction(c)
                row=dict(id=f'B{index:03d}C{j:02d}',base_id=f'B{index:03d}',
                         lambdaA=str(base[0]),lambdaB=str(base[1]),kappa=str(base[2]),
                         u=str(base[3]),eta=str(base[3]/2),h=str(base[4]),c=str(c))
                row.update(p)
                row.update(diag)
                low,high=prediction(3*c/4),prediction(5*c/4)
                row.update(flags(base,c,p,zero,low,high,blocked))
                row.update(H1_c0=zero.get('H1','UNRESOLVED'),z_H1_c0=zero.get('z_H1'),
                           H1_3c_4=low.get('H1','UNRESOLVED'),H1_5c_4=high.get('H1','UNRESOLVED'))
                row.update(identity_checked=False,identity_passed=None,identity_drift=None,
                           identity_bound=None,K_stable=None,H1_K640=None,z_H1_K640=None)
                rows.append(row)
            # Small buffered design CSV; keep completed bases even if a later one is killed.
            path=Path(out)/'scan.csv'
            mode='x' if index==1 else 'a'
            write_csv(path,rows[-len(COSTS):],mode)
            print(f'B{index:03d}/{len(list(bases()))} PARAMETER_ONLY CPU={cpu():.3f}s',file=sys.stderr,flush=True)
        counts={}
        for mode in ('must','all'):
            counts[mode]={g:sum(r[mode] and r['group']==g for r in rows) for g in ('Di','Dii','A')}
        w=witness(rows)
        for r in rows:
            # Preserve the old scan-stage fields. Final checks belong in summary.
            if r['base_id'] in IDENTITY_BASES and r['base_id'] in identities:
                ident=identities[r['base_id']]
                r.update(identity_checked=True,identity_passed=ident['passed'],
                         identity_drift=ident['drift'],identity_bound=ident['bound'])
        status='BLOCKED_EXACT_IDENTITY' if diagnostic_failure else candidate_status(counts,w)
        if previous_rows is not None and not diagnostic_failure:
            replay=replay_invariant(rows,previous_rows)
            if not replay['passed']:status='BLOCKED_REPLAY_INVARIANT'
        if status=='READY_FOR_FINAL_CHECKS':
            # Do not overwrite old CSV metadata when a new witness gains checks.
            diagnostic_failure,refined=validate_witness([dict(r) for r in rows],w,cache,identities,
                                                      builder=builder,identity_checker=identity_checker)
            status=('BLOCKED_EXACT_IDENTITY' if diagnostic_failure else
                    'PASS' if all(r['K_stable'] for r in refined) else 'HOLD_K_STABILITY')
        if rows:write_csv(Path(out)/'scan.csv',rows)
    return dict(status=status,counts=counts,witness=w,bases_completed=len(rows)//len(COSTS),
                bases_built=len(timings),rows=len(rows),identity_scope='stratified-plus-final',
                identity_base_ids=list(IDENTITY_BASES),identities=identities,K640_checks=refined,
                reused_identity_base_ids=sorted(identity_samples or {}),replay_invariant=replay,
                csv_scope='Scan-stage predictions; final identity and K640 checks are in summary',
                diagnostic_failure=diagnostic_failure,base_timings=timings,
                max_mean_drift=max((r['mean_drift'] for r in rows),default=None),
                stationary_sources=[dict(load=str(k[0]),kappa=str(k[1]),ref=k[2],path=v[2],key=v[3])
                                    for k,v in cache.used.items()])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spent-cpu-seconds',type=float,default=0.)
    parser.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    if args.worker:
        result=compute(identity_samples=load_identity_samples(),previous_rows=load_previous_rows())
        print(json.dumps(result,allow_nan=False));return 0
    preflight()
    V1.require(860<=args.spent_cpu_seconds<CAP-2, 'PART_A_PRIOR_BUDGET_REQUIRED_OR_EXHAUSTED')
    V1.require(not OUT.exists(),'WINDOW_ALREADY_ATTEMPTED')
    OUT.mkdir(parents=True)
    V1.require(ctypes.CDLL(None).prctl(36,1,0,0,0)==0,'SUBREAPER_REQUIRED')
    with tempfile.TemporaryFile() as stream:
        proc=subprocess.Popen([sys.executable,'-B','-m',__package__+'.window','--worker'],
                              cwd=ROOT,stdout=stream,start_new_session=True)
        stop=None
        while proc.poll() is None:
            if args.spent_cpu_seconds+cpu()+V1.group_cpu(proc.pid)>=CAP-1:
                stop='RESOURCE_CPU';break
            time.sleep(.1)
        if stop:
            os.killpg(proc.pid,signal.SIGKILL)
        code=proc.wait();V1.reap_group(proc);stream.seek(0)
        if stop or code:
            result=dict(status=stop or 'EXECUTION_FAILURE',worker_exit=code)
        else:
            result=json.loads(stream.read())
    measured=cpu()
    result.update(commit=V1.git('rev-parse','HEAD').decode().strip(),K=K,ref=REF,
                  cpu_seconds=measured,prior_compute_CPU_upper_seconds=args.spent_cpu_seconds,
                  total_Part_A_CPU_upper_seconds=measured+args.spent_cpu_seconds,cap_CPU_seconds=CAP,
                  rho=str(RHO),P_min=str(PMIN),z_min_pct=str(ZMIN),legacy_mean_tolerance_descriptive=MEAN_TOL,
                  costs=list(map(str,COSTS)),base_count=len(list(bases())),finite_h_truth_calls=0,
                  source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
                  historical_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in HISTORY})
    V1.write_once(OUT/'summary.json',result)
    print(json.dumps({k:result[k] for k in ('status','total_Part_A_CPU_upper_seconds')},indent=2))
    return 0 if result['status']=='PASS' else 2


if __name__=='__main__':
    raise SystemExit(main())
