"""Execute only committed, allowlisted calibration; never draw or open CF."""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys

from experiments.R3R_07_confirmation.common import check_committed,digest,git,verified_card,write_once
from experiments.R3R_05_contract.freeze import verify_lock
from .budget import bounded_call

PILOT='a7435e9a3cb0d1625479c942041ec6748444014a'


def verify_prereg(path):
    check_committed(path)
    config=json.loads(Path(path).read_text())
    if config['status']!='PREREGISTERED_CALIBRATION_ONLY':raise ValueError('not a calibration prereg')
    verify_lock();verified_card()
    for p,h in config['source_sha256'].items():
        check_committed(p)
        if digest(p)!=h:raise ValueError('source changed after prereg: '+p)
    if config['pilot_commit']!=PILOT or git('rev-list','-n1','explore-v13-pilot').decode().strip()!=PILOT:
        raise ValueError('pilot source mismatch')
    return config


def compare_anchor(job,result,out):
    """Exact parsed numeric columns and binary floating arrays; not equal NPZ container bytes."""
    import numpy as np
    stage=job['stage'];rid=job['id'];row=result['row']
    base=f'{PILOT}:results/explore_v13/{stage}'
    csv_raw=git('show',base+'/regimes.csv');npz_raw=git('show',base+'/pairs.npz')
    old=next(r for r in csv.DictReader(io.StringIO(csv_raw.decode())) if r['id']==rid)
    bad={}
    for key,value in row.items():
        if key=='wall_s':continue
        if key not in old:
            if key!='c_sw' or float(value)!=float(job['spec'][8]):bad[key]='missing archived scalar'
        elif key=='id':
            if value!=old[key]:bad[key]=[value,old[key]]
        elif not (float(value)==float(old[key]) or np.isnan(float(value)) and np.isnan(float(old[key]))):
            bad[key]=[value,old[key]]
    new=np.load(Path(out)/'pairs.npz')['pairs'];archive=np.load(io.BytesIO(npz_raw))
    mask=archive['rid']==rid
    cols=('rid','ia','ib','w','ED','EDh','EdA','EdB','EhA','EhB','flip','reverse','blind','m_rel')
    mismatch=[]
    for i,key in enumerate(cols):
        if key=='rid':same=np.array_equal(new[:,i],archive[key][mask])
        else:
            a,b=new[:,i].astype(float),archive[key][mask].astype(float)
            same=a.shape==b.shape and np.array_equal(a.view(np.uint64),b.view(np.uint64))
        if not same:mismatch.append(key)
    return dict(status='PASS' if not bad and not mismatch else 'FAIL',scalar_mismatches=bad,
                pair_column_mismatches=mismatch,pairs=len(new),numeric_pair_columns_bitwise=not mismatch,
                archive_csv_sha256=__import__('hashlib').sha256(csv_raw).hexdigest(),
                archive_npz_sha256=__import__('hashlib').sha256(npz_raw).hexdigest())


def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--prereg',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(argv);cfg=verify_prereg(a.prereg)
    out=a.out;out.mkdir(parents=True,exist_ok=False)
    env=dict(os.environ,**cfg['worker_environment']);records=[]
    write_once(out/'attempt.json',dict(prereg_sha256=digest(a.prereg),source_commit=git('rev-parse','HEAD').decode().strip(),CF_runs=0))
    for job in cfg['legacy_jobs']+cfg['stationary_jobs']:
        if sum(r['resources']['cpu_seconds'] for r in records)>=cfg['limits']['total_cpu_seconds']:
            records.append(dict(id=job['id'],status='NOT_RUN_TOTAL_BUDGET'));break
        dest=out/job['id']
        resources=bounded_call([sys.executable,'-m','experiments.R3R_07_numerics.worker','--prereg',str(a.prereg),'--job',job['id'],'--out',str(dest)],
                               dest,wall_seconds=cfg['limits']['job_wall_seconds'],cpu_seconds=cfg['limits']['job_cpu_seconds'],
                               rss_bytes=cfg['limits']['rss_bytes'],env=env)
        file=dest/'result.json';data=json.loads(file.read_text()) if file.exists() else None
        rec=dict(id=job['id'],kind=job['kind'],resources=resources,
                 status='COMPLETED' if data and data['status']=='COMPLETED' and resources['exit_code']==0 else 'UNRESOLVED')
        if rec['status']=='COMPLETED' and job['kind']=='legacy_anchor':
            rec['legacy_comparison']=compare_anchor(job,data,dest)
            if rec['legacy_comparison']['status']!='PASS':rec['status']='FAIL_ANCHOR'
        if data:
            rec['worker_peak_rss_bytes']=data['peak_rss_bytes']
            if job['kind']=='stationary_only' and data['status']=='COMPLETED':
                rec.update(degree=data['degree'],law_error_upper=data['law_error_upper'])
        records.append(rec);write_once(out/(job['id']+'_receipt.json'),rec)
        print(json.dumps(dict(id=job['id'],status=rec['status'],wall_seconds=resources['wall_seconds'],stop_reason=resources['stop_reason'])),flush=True)
    feasible=all(r['status']=='COMPLETED' for r in records) and len(records)==len(cfg['legacy_jobs'])+len(cfg['stationary_jobs'])
    # Stage 0 is a necessary gate. The conditional global schedule is deliberately
    # not opened if rate-resolution feasibility or an anchor fails.
    summary=dict(owner='Doan Van Tai',status='STAGE0_PASS_REQUIRES_GLOBAL_AUDIT' if feasible else 'HOLD_NUMERICS_FEASIBILITY',
                 records=records,global_calibration='PENDING_SEPARATE_FULL_AUDIT' if feasible else 'NOT_RUN_PREREGISTERED_STOP',
                 conditional_global_jobs=len(cfg['conditional_global_jobs']),stage0_cpu_seconds=sum(r.get('resources',{}).get('cpu_seconds',0) for r in records),
                 CF_generated=0,confirmation_root=None,n=None,contract_v1_3_1_created=False,Phase4='HOLD')
    write_once(out/'summary.json',summary)
    return 0


if __name__=='__main__':raise SystemExit(main())
