"""Doan Van Tai — L4.9 discovery exploration only; no held-out M1 calls."""
import argparse
from collections import Counter,defaultdict
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import resource
import signal
import time

import numpy as np
from scipy.stats import spearmanr

from experiments.P4_01_recount import recount_map as R
from experiments.P4_03_map_audit.common import canonical,cf_keys
from .predictor import StationaryCache,predict,nearest

ROOT=R.ROOT
PROTOCOL=ROOT/'experiments/P4_09_stationary/protocol.json'
OUT=ROOT/'results/lessons/l4_9_v2/discovery'


def cpu():
    c=resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time()+c.ru_utime+c.ru_stime


def write_json(path,doc):
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def forbidden():
    seal=json.loads((ROOT/'experiments/P4_03_map_audit/sealed_scope.json').read_text())
    return set(cf_keys())|{tuple(r['coordinates']) for r in seal['sealed']}


def references():
    """Exclude sealed keys BEFORE numeric outcome parsing; native preferred."""
    blocked=forbidden();by={};skipped=Counter()
    source=ROOT/'results/P4_01_recount/20261030_01/recounted_regimes.csv'
    for raw in csv.DictReader(source.open()):
        if F(raw['amp'])!=6:continue
        age=F(raw['age'])
        key=tuple(map(str,(F(raw['lambdaA']),F(raw['lambdaB']),2*F(raw['eta']),F(raw['kappa'])/age,F(raw['h'])/age,F(0))))
        if key in blocked:skipped['pilot_sealed_or_CF']+=1;continue
        ks='|'.join(key);priority=(1 if age==1 else 2,raw['id'])
        item=dict(key=ks,id=raw['id'],source_kind='pilot',GM_S1_pctC=float(raw['G_M_S1_pctC']),
                  GS_M1_pctC=float(raw['G_S_M1_pctC']),arithmetic_pass_original='',priority=priority)
        if ks not in by or priority<by[ks]['priority']:by[ks]=item
    natives=[]
    for r in csv.DictReader((ROOT/'results/lessons/l4_6_v2/analysis/rows.csv').open()):
        if r['engine']!='native':continue
        if tuple(r['key'].split('|')) in blocked:raise ValueError('sealed/CF native reference')
        item=dict(key=r['key'],id=r['id'],source_kind='native',GM_S1_pctC=float(r['G_M_S1_pctC']),
                  GS_M1_pctC=float(r['G_S_M1_pctC']),arithmetic_pass_original=r['arithmetic_pass'],
                  priority=(0,r['id']),source=r['source'],ref=int(r['ref']))
        by[r['key']]=item;natives.append(item)
    training=[{k:v for k,v in r.items() if k!='priority'} for r in sorted(by.values(),key=lambda r:r['key'])]
    return training,natives,dict(skipped)


def exposure_audit(protocol,training):
    inv=json.loads((ROOT/'results/lessons/l3r_7/lean_close/collision_inventory_v3.json').read_text())
    keys={r['key'] for r in inv['records'] if r['namespace']=='v1.3_fixed_plant'}|{r['key'] for r in training}
    for c in json.loads((ROOT/'experiments/R3R_11_native_population/prereg.json').read_text())['cases']:
        keys.add('|'.join(canonical(c['parameters'])))
    blocked=forbidden()
    panel=[]
    for c in protocol['future_panel']:
        key=canonical(c['parameters']);ratio=F(c['parameters'][4])/F(c['parameters'][2])
        if '|'.join(key) in keys or key in blocked or ratio<=160:raise ValueError('future panel collision/non-extrapolation')
        panel.append(dict(id=c['id'],key=list(key),h_over_kappa=str(ratio),fresh_coordinate=True))
    # Calibration is explicitly disjoint; h32 here is new exposure, not old discovery.
    new=protocol['timing'][-1];key=canonical(new['parameters'])
    if key in blocked or any(key==tuple(r['key']) for r in panel) or F(new['parameters'][4])/F(new['parameters'][2])>160:
        raise ValueError('timing case overlaps held-out ratio/key')
    return dict(max_registered_ratio=str(max(F(k.split('|')[4])/F(k.split('|')[3]) for k in keys)),
                registered_keys=len(keys),future_panel=panel,timing_h32_new_coordinate='|'.join(key) not in keys,
                CF_or_sealed_outcomes_read=False)


def metrics(rows):
    scored=[r for r in rows if r.get('status')=='PREDICTED']
    if not scored:return dict(n=0)
    y=np.array([r['GM_true_pctC'] for r in scored]);p=np.array([r['GM_pred_pctC'] for r in scored]);n=np.array([r['NN_pred_pctC'] for r in scored])
    rho=float(spearmanr(p,y).statistic) if np.ptp(p)>1e-12 and np.ptp(y)>1e-12 else None
    mp=float(np.median(abs(p-y)));mn=float(np.median(abs(n-y)))
    return dict(n=len(scored),Spearman=rho,stationary_MedAE_pp=mp,NN_MedAE_pp=mn,
                relative_MedAE_improvement=None if mn==0 else 1-mp/mn,
                passes_prospective_numeric_thresholds=bool(rho is not None and rho>=.7 and mn>0 and mp<=.7*mn))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,default=OUT)
    args=parser.parse_args(argv)
    if args.out.exists():raise FileExistsError('use new discovery output path')
    protocol=json.loads(PROTOCOL.read_text())
    from experiments.P4_A1.config import verify_run
    for name in ('L43_A1_SV','L44_A3','SUB_BOX'):verify_run(name)
    training,natives,skipped=references();audit=exposure_audit(protocol,training)
    selected={r['id']:r for r in natives}
    args.out.mkdir(parents=True)
    write_json(args.out/'exposure_audit.json',audit)
    with (args.out/'nn_training.csv').open('w',newline='') as f:
        fields=sorted({k for r in training for k in r});w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(training)
    cache=StationaryCache(ROOT,ROOT/'results/lessons/l4_9_v2/native_cache')
    begin,wall=cpu(),time.monotonic();rows=[];status='COMPLETE'
    class Timebox(Exception):pass
    def alarm(*_):raise Timebox()
    previous=signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,protocol['limits']['predictor_wall_seconds'])
    try:
        with (args.out/'predictions.jsonl').open('w') as f:
            for cid in protocol['discovery_ids']:
                if cpu()-begin>protocol['limits']['predictor_CPU_seconds']:status='CPU_TIMEBOX_REACHED';break
                row=selected[cid];a,b,u,k,h,c=row['key'].split('|');parameters=[a,b,k,str(F(u)/2),h,c]
                started=cpu();pred=predict(parameters,cache,ref=row['ref'],K=protocol['predictor']['K'])
                nn=nearest(row['key'],training,leave_out=True)
                pred.update(id=cid,key=row['key'],h_over_kappa=float(F(h)/F(k)),GM_true_pctC=row['GM_S1_pctC'],
                            GS_M1_pctC=row['GS_M1_pctC'],NN_pred_pctC=nn['GM_S1_pctC'],NN_key=nn['key'],
                            NN_source_kind=nn['source_kind'],arithmetic_pass_original=row['arithmetic_pass_original'],
                            cpu_seconds=cpu()-started)
                rows.append(pred);f.write(json.dumps(pred,ensure_ascii=False,allow_nan=False)+'\n');f.flush()
                if len(rows)%10==0:print(f'discovery {len(rows)}/{len(protocol["discovery_ids"])} CPU={cpu()-begin:.2f}s',flush=True)
    except Timebox:status='WALL_TIMEBOX_REACHED'
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
    summary=dict(status=status,planned=len(protocol['discovery_ids']),completed=len(rows),metrics=metrics(rows),
                 sensitivity_no_original_raw_flags=metrics([r for r in rows if r['arithmetic_pass_original']=='True']),
                 training_rows=len(training),training_sources=dict(Counter(r['source_kind'] for r in training)),
                 excluded=skipped,CPU_seconds=cpu()-begin,wall_seconds=time.monotonic()-wall,
                 hstar='NOT_IMPLEMENTED_INVALID_UNIFORM_BOUND',fitted_parameters=0,new_heldout_outcomes=0,
                 future_cases=audit['future_panel'],uncertainty='Discovery point estimates; no predictive claim/CI/Phase5 verdict',
                 protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest())
    write_json(args.out/'summary.json',summary)
    if rows:
        flat=[{k:v for k,v in r.items() if k!='stationary_sources'} for r in rows]
        with (args.out/'predictions.csv').open('w',newline='') as f:
            fields=sorted({k for r in flat for k in r});w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(flat)
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
