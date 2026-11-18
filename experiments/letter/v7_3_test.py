"""Doan Van Tai — locked one-shot V7-3 test runner; importing does no work.

The record body is the unchanged compute_night engine sequence. Only its date
and regime gate, saved prediction arrays and independent trace stream are new.
Train-only validation explicitly bypasses test access and uses the pilot seed.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta
import multiprocessing as mp
from pathlib import Path
import platform
import resource
import signal
import socket
import tarfile
import time
import traceback

import numpy as np

from experiments.ext_validity import ev_te as T
from experiments.letter import e4_geant as E
from experiments.letter import v7_3_data as D
from experiments.letter import v7_3_day as A
from experiments.letter import v7_3_run as R
from experiments.letter import v7_3_sim as S
from experiments.letter import v7_3_test_common as C

OUT = C.OUT


def checked_token(verified):
    if not isinstance(verified, C.VerifiedLock) or C.sha256(verified.path) != verified.digest:
        raise ValueError('verified lock required before test access')


def load_days(dates, config, *, verified=None, training_only=False, root=None,
              manifest=None):
    """Parse only requested dates and their phase-A 22:00 warmups.

    Even a midday window retains phase A's complete 96-slot day and previous
    22:00--23:45 eligibility. Duplicate/corrupt slots exclude the whole date.
    No test payload can be read through the explicit train validation path.
    """
    if not training_only:
        checked_token(verified)
    root = T.data_root() if root is None else Path(root)
    manifest = C.read_json(D.OUT/'data_manifest.json') if manifest is None else manifest
    dates = [str(x) for x in dates]
    allowed = set(manifest['train_dates'] if training_only else manifest['test_dates'])
    if (len(set(dates)) != len(dates) or any(d not in allowed or
            datetime.fromisoformat(d).weekday() >= 5 for d in dates)):
        raise ValueError('date gate: retained weekdays of the authorized split only')
    dates.sort()
    wanted = set()
    for date in dates:
        start = datetime.fromisoformat(date)
        wanted.update(start+timedelta(minutes=15*i) for i in range(-8, 96))
    records, errors = {}, {}
    net = D.topology(root)
    with tarfile.open(root/D.TM_NAME) as tar:
        for member in tar:
            if not member.isfile() or not member.name.endswith('.txt'):
                continue
            when = D.stamp(member.name)
            if when not in wanted:
                continue
            if when in records:
                records[when] = None
                errors[when] = 'duplicate timestamp'
                continue
            try:
                with tar.extractfile(member) as f:
                    text = f.read().decode('utf-8')
                meta = D.re.search(r'time\s*=\s*(\d{8}-\d{4})', text)
                if not meta or D.stamp(meta[1]) != when:
                    raise ValueError('filename/META time mismatch')
                records[when] = D.parse_tm(text, net)[0]
            except (ValueError, UnicodeError) as exc:
                records[when], errors[when] = None, str(exc)
    accepted, windows, warms, exclusions = [], [], [], []
    slot = config['start_slot']
    if slot not in range(73):
        raise ValueError('six-hour within-day window required')
    for date in dates:
        start = datetime.fromisoformat(date)
        times = [start+timedelta(minutes=15*i) for i in range(-8,96)]
        bad = [t for t in times if records.get(t) is None]
        if bad:
            exclusions.append(dict(date=date, reason='incomplete day' if any(t>=start for t in bad)
                                   else 'incomplete 22:00 warmup',
                                   invalid_slots=[dict(timestamp=t.isoformat(),
                                     error=errors.get(t,'missing')) for t in bad]))
            continue
        values = np.stack([records[t] for t in times])
        accepted.append(date)
        windows.append(values[8+slot:8+slot+24])
        warms.append(values[slot:slot+8])
    d = len(net['demands'])
    return dict(dates=np.array(accepted, dtype='U10'),
                days=np.stack(windows) if windows else np.empty((0,24,d)),
                warm=np.stack(warms) if warms else np.empty((0,8,d))), exclusions


def strata(demand, incidence, capacity):
    load = np.einsum('sd,aed->sae', np.asarray(demand), incidence, optimize=True)
    maximum = (load/float(np.asarray(capacity).item())).max(axis=(0,2))
    return dict(max_utilization_by_action=maximum.tolist(),
                stratum='S' if bool((maximum<1).all()) else 'O')


def require_day(training, config, date, regime, training_only, verified):
    if not training_only:
        checked_token(verified)
        manifest = C.read_json(D.OUT/'data_manifest.json')
        if date not in manifest['test_dates']:
            raise ValueError('date gate: not a retained test date')
    elif date not in config['train_dates']:
        raise ValueError('date gate: train validation forbids test dates')
    if regime not in [r['id'] for r in config['regimes']]:
        raise ValueError('unknown daytime regime')
    if datetime.fromisoformat(date).weekday()>=5:
        raise ValueError('weekday required')
    indices = np.flatnonzero(training['dates']==date)
    if len(indices)!=1:
        raise ValueError('date must occur exactly once in supplied arrays')
    return int(indices[0])


def compute_record(training, arrays, config, date, regime, s_hat, *, n=32, k=64,
                   r_dec=64, r_eval=128, seed=7312001, training_only=False,
                   verified=None):
    cpu_start, wall_start = time.process_time(), time.perf_counter()
    j = require_day(training, config, date, regime, training_only, verified)
    ids = [x['id'] for x in config['regimes']]
    config = dict(incidence=arrays['incidence'][ids.index(regime)],
                  capacity=arrays['capacity'], profiles=arrays['profiles'])
    seed_base = seed
    seed = T.seed_for(seed, 'V7-3-A2|' + regime)
    timings={};root=T.seed_for(seed,'V7-3|'+date)
    inc,cap=config['incidence'],float(np.asarray(config['capacity']).item())
    hs=np.rint(S.HOURS*3600/S.DT).astype(int)
    fresh,stale=R.timer(timings,'warmup',lambda:S.warm_instances(inc,training['warm'][j],cap,n,T.seed_for(root,'warm')))
    weekend=int(datetime.fromisoformat(date).weekday()>=5)
    m0=R.timer(timings,'M0_fresh',lambda:S.mean_rollout(inc,config['profiles'][weekend],cap,*fresh))
    names=['M0','Hybrid','Stationary']
    decisions=np.empty((n,3,2,2,4),dtype=np.int16)
    ties=np.zeros_like(decisions,dtype=bool)
    def twins(costs):
        plain=E.pick(costs)
        hybrid=E.pick(E.hybrid_costs(costs,[0.,s_hat],S.HOURS*3600))
        stationary=np.full((n,4),int(s_hat<0),dtype=np.int16)
        return np.stack([plain[0],hybrid[0],stationary],axis=1),np.stack([plain[1],hybrid[1],np.full((n,4),s_hat==0)],axis=1)
    fresh_d,fresh_t=R.timer(timings,'choices_fresh',lambda:twins(m0))
    decisions[:,:,0]=fresh_d[:,:,None,:];ties[:,:,0]=fresh_t[:,:,None,:]
    m0_stale = []
    for t,tau in enumerate(S.TAU_SECONDS):
        pm,pq=R.timer(timings,f'posterior_{int(tau)}',lambda tau=tau:S.forward_posterior(
            inc,training['warm'][j,-1],cap,stale[tau],tau,k,T.seed_for(root,f'posterior-{tau}')))
        old=R.timer(timings,f'M0_stale_{int(tau)}',lambda:S.mean_rollout(
            inc,config['profiles'][weekend],cap,pm,pq).reshape(n,k,2,4).mean(axis=1))
        m0_stale.append(old)
        decisions[:,:,1,t],ties[:,:,1,t]=R.timer(timings,f'choices_stale_{int(tau)}',lambda:twins(old))
    def rollout(rollouts,purpose):
        m,q=(np.repeat(x,rollouts,axis=0) for x in fresh)
        costs=S.variable(inc,training['days'][j,:24],cap,m,q,T.seed_for(root,purpose),hs=hs)[0]
        return costs.reshape(n,rollouts,2,4)
    dec_values=R.timer(timings,'reference_decision',lambda:rollout(r_dec,'reference-decision'))
    evaluation=R.timer(timings,'paired_evaluation',lambda:rollout(r_eval,'evaluation'))
    def metrics():
        v=evaluation.mean(axis=1)
        reference,ref_tie=E.pick(dec_values.mean(axis=1))
        cref=E.costs_for_decisions(v,reference)
        selected=E.costs_for_decisions(v,decisions)
        regret=selected-cref[:,None,None,None,:]
        gs=selected[:,:,1]-selected[:,:,0]
        return v,reference,ref_tie,cref,selected,regret,gs
    v,reference,ref_tie,cref,selected,regret,gs=R.timer(timings,'metrics_gather',metrics)
    # Exact gather identity is required, not a confidence-interval assertion.
    if not np.array_equal(E.costs_for_decisions(v,reference),cref):
        raise AssertionError('CRN gather identity failed')
    tint_seed = T.seed_for(seed_base, 'tint|' + regime + '|' + date)
    trace = R.timer(timings, 'descriptive_trace', lambda: S.variable(
        inc, training['days'][j,:24], cap, fresh[0][:1], fresh[1][:1],
        tint_seed, hs=hs, trace=True)[3])
    tint = R.timer(timings, 'descriptive_T_int', lambda: [
        A.resolution(trace[:, a], S.DT) for a in range(2)])
    arrays=dict(M0_predicted_fresh=m0, M0_predicted_stale=np.stack(m0_stale, axis=1),
                backlog_trace=trace, tint_seed=np.array(tint_seed, dtype=np.uint64),
                fresh_modes=fresh[0], fresh_queues=fresh[1], V=v,reference_decision=reference,C_ref=cref,decisions=decisions,tie_flags=ties,
                reference_tie_flags=ref_tie,paired_evaluation=evaluation,reference_decision_rollouts=dec_values,
                costs=selected,regret=regret,G_S=gs,pipelines=np.array(names),
                h_seconds=S.HOURS*3600,tau_seconds=np.array(S.TAU_SECONDS))
    metadata=dict(owner='Doan Van Tai',date=date,training_only=training_only,pilot=training_only,N=n,K=k,R_dec=r_dec,R_eval=r_eval,
                  seed=seed,dt_s=S.DT,timings=timings,units=dict(cost='Mbit*s',rate='Mbit'),
                  C_ref_mean_Mbit_s=cref.mean(axis=0).tolist(),
                  regret_mean_Mbit_s=regret.mean(axis=0).tolist(),G_S_mean_Mbit_s=gs.mean(axis=0).tolist(),
                  percentages_defined=(cref.mean(axis=0)>0).tolist(),
                  reference_evaluation_streams_distinct=T.seed_for(root,'reference-decision')!=T.seed_for(root,'evaluation'),
                  peak_memory_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
                  axes=dict(decisions=['instance','pipeline','side:fresh,stale','tau','h'],V=['instance','action','h']))
    metadata.update(regime=regime, seed_base=seed_base, T_int=tint,
                    tint_seed=tint_seed, status='COMPLETE',
                    CPU_s=time.process_time()-cpu_start,
                    wall_s=time.perf_counter()-wall_start)
    return arrays,metadata

_WORKER = None


def _initialize(training, arrays, config, params, out, verified, labels):
    global _WORKER
    checked_token(verified)
    _WORKER = (training, arrays, config, params, Path(out), verified, labels)


def write_record(training, arrays, config, params, out, regime, date, label, *,
                 verified=None, training_only=False):
    """Run and publish one record; train validation uses this same worker body."""
    cpu_start,wall_start = time.process_time(),time.perf_counter()
    out = Path(out)
    # Save the pre-truth input calculation too, for raw-only strata rescoring.
    j = require_day(training,config,date,regime,training_only,verified)
    r = [x['id'] for x in config['regimes']].index(regime)
    utilization = np.einsum('sd,aed->sae',training['days'][j],
                           arrays['incidence'][r],optimize=True)/float(np.asarray(arrays['capacity']).item())
    raw, meta = compute_record(training, arrays, config, date, regime,
        params['s_hat_pooled_Mbit'][regime], n=params['N_test'], k=params['K'],
        r_dec=params['R_dec'], r_eval=params['R_eval'], seed=params['test_seed'],
        verified=verified, training_only=training_only)
    raw['input_utilization'] = utilization
    meta.update(label)
    stem = out/'records'/f'{regime}_{date}'
    R.timer(meta['timings'],'write_raw_npz',lambda: C.atomic_write(
        stem.with_suffix('.npz'),lambda p: E.write_npz(p,raw)))
    meta['npz_sha256'] = C.sha256(stem.with_suffix('.npz'))
    meta['CPU_s'] = time.process_time()-cpu_start
    meta['wall_s'] = time.perf_counter()-wall_start
    C.write_json(stem.with_suffix('.json'),meta)
    return dict(regime=regime,date=date,CPU_s=meta['CPU_s'],wall_s=meta['wall_s'],
                peak_memory_MiB=meta['peak_memory_MiB'],npz_sha256=meta['npz_sha256'])


def _record(task):
    training, arrays, config, params, out, verified, labels = _WORKER
    regime, date = task
    return write_record(training, arrays, config, params, out, regime, date,
                        labels[regime,date], verified=verified)


def prepare_inputs(params, out, *, verified=None, training_only=False, dates=None):
    """Shared pre-pool steps; the validation bypass accepts train dates only."""
    if not training_only:
        checked_token(verified)
    out = Path(out)
    config = C.read_json(C.ROOT/params['training_dir']/'configuration.json')
    with np.load(C.ROOT/params['training_dir']/'configuration.npz',allow_pickle=False) as f:
        arrays = {k:f[k] for k in f.files}
    manifest = C.read_json(D.OUT/'data_manifest.json')
    if dates is None:
        dates = A.weekday_dates(manifest['train_dates'] if training_only else manifest['test_dates'])
    training, exclusions = load_days(dates,config,verified=verified,
                                     training_only=training_only,manifest=manifest)
    tasks, labels, inputs = [], {}, []
    for r, regime in enumerate(params['regimes']):
        for j,date in enumerate(training['dates'].tolist()):
            label = strata(training['days'][j],arrays['incidence'][r],arrays['capacity'])
            labels[regime,date] = label
            inputs.append(dict(regime=regime,date=date,**label))
            tasks.append((regime,date))
    # All input-only strata are durably published before even worker startup.
    payload = dict(requested_dates=dates,dates=training['dates'].tolist(),
                   exclusions=exclusions,phase_A_exclusions_metadata=manifest['dropped_nights'],
                   records=inputs,lock_sha256=verified.digest if verified is not None else None)
    if training_only:
        payload['training_only'] = True
    C.write_json(out/'inputs.json',payload)
    return training, arrays, config, tasks, labels


def _interrupt(signum, frame):
    raise KeyboardInterrupt('interrupted by signal '+str(signum))


def run(workers=30, out=OUT):
    verified = C.verify_lock(out)  # Before training data, test loader or engine.
    out = Path(out)
    if workers<1:
        raise ValueError('positive worker count required')
    if ((out/'records').exists() and any((out/'records').iterdir())) or any(
            (out/name).exists() for name in ('run_started.json','inputs.json','run_summary.json')):
        raise FileExistsError('one-shot run already attempted; no retry or resume')
    started = time.perf_counter()
    C.write_json(out/'run_started.json',dict(owner='Doan Van Tai', host=socket.gethostname(),
                 lock_sha256=verified.digest,workers=workers))
    summary = dict(status='INCOMPLETE',owner='Doan Van Tai', records=[],workers=workers,
                   host=socket.gethostname(),python=platform.python_version(),numpy=np.__version__,
                   lock_sha256=verified.digest)
    pool = None
    old_term = signal.signal(signal.SIGTERM,_interrupt)
    try:
        params = C.read_json(C.ROOT/C.PARAMS)
        training,arrays,config,tasks,labels = prepare_inputs(params,out,verified=verified)
        summary['expected_records'] = len(tasks)
        if not tasks:
            raise ValueError('no complete eligible test weekdays')
        pool = ProcessPoolExecutor(workers,mp_context=mp.get_context('spawn'),initializer=_initialize,
            initargs=(training,arrays,config,params,out,verified,labels))
        futures = [pool.submit(_record,task) for task in tasks]
        for future in as_completed(futures):
            record = future.result()
            summary['records'].append(record)
            print(E.json_bytes(record).decode().strip(),flush=True)
        pool.shutdown(wait=True)
        pool = None
        summary['status'] = 'COMPLETE'
    except BaseException:
        summary['error'] = traceback.format_exc()
        if pool is not None:
            # Stop on Python exceptions AND BrokenProcessPool/native worker loss.
            processes = list((getattr(pool,'_processes',None) or {}).values())
            for process in processes:
                if process.is_alive():
                    process.terminate()
            pool.shutdown(wait=True,cancel_futures=True)
        raise
    finally:
        signal.signal(signal.SIGTERM,old_term)
        summary['records'].sort(key=lambda r:(r['regime'],r['date']))
        summary['wall_s'] = time.perf_counter()-started
        summary['CPU_s_records'] = sum(r['CPU_s'] for r in summary['records'])
        summary['peak_worker_memory_MiB'] = max(
            [r['peak_memory_MiB'] for r in summary['records']], default=None)
        summary['parent_peak_memory_MiB'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        summary['children_CPU_s'] = sum(getattr(resource.getrusage(resource.RUSAGE_CHILDREN),x)
                                        for x in ('ru_utime','ru_stime'))
        summary['peak_child_memory_MiB'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024
        C.write_json(out/'run_summary.json',summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['lock','verify-lock','run'])
    parser.add_argument('--workers',type=int,default=30)
    args = parser.parse_args()
    if args.command=='lock':
        C.create_lock()
    elif args.command=='verify-lock':
        C.verify_lock()
        print('LOCK MATCH')
    else:
        run(args.workers)


if __name__=='__main__':
    main()
