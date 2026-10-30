"""Doan Van Tai — fail-closed prereg, source and collision guards (AI theo ủy quyền)."""
from fractions import Fraction as F
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path('experiments/P4_03_map_audit')
OUT=Path('results/lessons/l4_3')
CF=Path('results/lessons/l3r_7/lean_close/cf_generation/attempt01/regimes_cf.json')
COORDS=('lambdaA','lambdaB','u','kappa','h','c_sw')
METRICS=('G_S','G_M','G_SM','Gamma','G_S_M1','G_M_S1')
LEVELS=((640,4),(320,4),(640,2))
TOL_PP=F(1,4)


def require(ok,message):
    if not ok: raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args])


def write_once(path,obj):
    """Exclusive create; never overwrite another writer, including resume metadata."""
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    blob=(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    temporary=path.with_name(path.name+f'.{os.getpid()}.tmp')
    with temporary.open('xb') as f:
        f.write(blob); f.flush(); os.fsync(f.fileno())
    try:
        os.link(temporary,path)
    finally:
        temporary.unlink()


def canonical(parameters):
    a,b,k,e,h,c=map(F,parameters)
    return tuple(map(str,(a,b,2*e,k,h,c)))


def cf_keys(path=None):
    doc=json.loads(Path(path or ROOT/CF).read_text())
    return {tuple(str(F(r['regime'][k])) for k in COORDS) for r in doc['rows']}


def forbid_cf(parameters,forbidden):
    require(canonical(parameters) not in forbidden,'CF_COLLISION: refuse before engine import')


def verify_prereg():
    config=json.loads((ROOT/HERE/'prereg.json').read_text())
    require(config['status']=='FROZEN_BEFORE_PHYSICAL_CALLS','prereg not frozen')
    for name,h in config['source_sha256'].items():
        require(sha(ROOT/name)==h,'source hash mismatch: '+name)
    # Every prereg/runner/source must be committed with the frozen bytes.
    for name in [str(HERE/'prereg.json'),str(HERE/'prereg.md'),*config['source_sha256']]:
        require(git('show','HEAD:'+name)==(ROOT/name).read_bytes(),'uncommitted prereg/source: '+name)
    for manifest in ('experiments/R3R_14_lean_close/prereg.json','experiments/R3R_11_native_population/prereg.json'):
        doc=json.loads((ROOT/manifest).read_text())
        for name,h in doc['source_sha256'].items():
            require(sha(ROOT/name)==h,'native transitive source changed: '+name)
    from experiments.P4_01_recount.verify_artifacts import verify
    require(verify()['status']=='PASS','frozen/L4.1 integrity failure')
    return config


def pct(row,metric):
    c=F(row['Cref']); require(c>0,'nonpositive Cref')
    return 100*F(row[metric])/c


def point_class(values):
    gs,gm,gsm,g=values
    if gs<=-1:return 'C'
    if gs>=1:return 'AB' if gm>=1 else 'A'
    if gm>=1:return 'B'
    if gsm>=1 and g>=max(gs,gm):return 'J'
    return 'D'


def validate_row(row,case,level):
    require(row.get('id')==case['id'] and (row.get('K'),row.get('ref'))==tuple(level),'wrong row ID/level')
    require(row.get('parameters')==case['parameters'],'wrong row parameters')
    require(row.get('status')=='COMPLETED','native row incomplete')
    require(row.get('CF_computed') is False,'CF_computed must be literal False')
    require(row.get('arithmetic_pass') is True,'raw arithmetic_pass is not True')
    require(row.get('validity_errors')==[],'raw validity_errors not empty')
    from experiments.R3R_14_lean_close import checks
    require(checks.arithmetic_ok(row) and not checks.consistency(row),'lean adapter arithmetic/consistency failed')
    z={m:pct(row,m) for m in METRICS}
    tol=F(1,10**9)  # algebra roundoff diagnostic pp, not a convergence bound
    require(abs(z['Gamma']-(z['G_S_M1']-z['G_S']))<=tol,'S11 state identity violated')
    require(abs(z['Gamma']-(z['G_M_S1']-z['G_M']))<=tol,'S11 model identity violated')
    require(all(z[m]>=-tol for m in ('G_M','G_SM','G_S_M1','G_M_S1')),'S07/S08 violated')
    require(z['Gamma']>=-min(z['G_S'],z['G_M'])-tol,'Gamma lower bound violated')


def compare(alias,case,rows):
    """Use actual contract R1, including Cref, six contrasts and sign flips."""
    from experiments.R3R_05_contract.rules import compare_levels
    failures=[]
    for lv in LEVELS:
        try:validate_row(rows[lv],case,lv)
        except (KeyError,ValueError,RuntimeError) as exc:failures.append(f'{lv}:{exc}')
    if any(lv not in rows or rows[lv].get('status')!='COMPLETED' for lv in LEVELS):
        return dict(id=alias['id'],native_id=case['id'],status='HOLD',reasons=failures or ['missing levels'])
    try:
        require(all(F(rows[lv]['Cref'])>0 for lv in LEVELS),'nonpositive Cref')
    except (KeyError,ValueError,RuntimeError) as exc:
        return dict(id=alias['id'],native_id=case['id'],status='HOLD',reasons=failures+[str(exc)])
    main=rows[LEVELS[0]]
    z={m:pct(main,m) for m in METRICS}
    r1=[compare_levels(main,rows[lv]) for lv in LEVELS[1:]]
    if not all(c['ready'] for c in r1):failures.append('R1')
    # d includes raw cost-scale and ratio differences, as well as arithmetic width.
    d={m:100*max([c['deltas'][m] for c in r1]+[F(main['normalized_error'][m])]) for m in METRICS}
    shift={m:z[m]-F(alias['pilot_pctC'][m]) for m in METRICS}
    checked=('G_S','G_M','Gamma','G_S_M1','G_M_S1')  # supplied pilot/native tolerance table
    failures += ['PILOT_NATIVE:'+m for m in checked if abs(shift[m])>TOL_PP]
    keys=('G_S','G_M','G_SM','Gamma')
    native_class=point_class([z[m] for m in keys])
    candidates={point_class(v) for v in itertools.product(*[(z[m]-d[m],z[m]+d[m]) for m in keys])}
    # Equality remains unresolved absent an exact certificate, even if measured d=0.
    boundaries=((abs(z['G_S']+1),d['G_S']),(abs(z['G_S']-1),d['G_S']),
                (abs(z['G_M']-1),d['G_M']),(abs(z['G_SM']-1),d['G_SM']),
                (abs(z['Gamma']-z['G_S']),d['Gamma']+d['G_S']),
                (abs(z['Gamma']-z['G_M']),d['Gamma']+d['G_M']))
    # Only tests relevant to the selected class can make that class ambiguous.
    relevant={'C':(0,), 'A':(0,1,2),'AB':(0,1,2),'B':(0,1,2),'J':tuple(range(6)),'D':tuple(range(6))}
    if native_class=='D' and z['G_SM']<1:relevant['D']=(0,1,2,3)
    ambiguous=len(candidates)!=1 or any(boundaries[i][0]<=boundaries[i][1] for i in relevant[native_class])
    return dict(id=alias['id'],native_id=case['id'],zones=alias['zones'],pilot_class=alias['pilot_class'],
                native_class=native_class,native_class_R6='UNRESOLVED' if ambiguous else native_class,
                class_flipped=native_class!=alias['pilot_class'],
                z_pctC={m:float(v) for m,v in z.items()},d_pp={m:float(v) for m,v in d.items()},
                shift_pp={m:float(v) for m,v in shift.items()},
                unresolved_A_GS=abs(z['G_S']-1)<=d['G_S'],
                unresolved_AB_Gamma=abs(z['Gamma']+1)<=d['Gamma'],
                r1=[dict(ready=bool(c['ready']),cref_delta=float(c['cref_delta']),
                         max_delta_pp=float(100*max(c['deltas'].values())),sign_flips=c['sign_flips']) for c in r1],
                status='HOLD' if failures else 'PASS',reasons=failures)
