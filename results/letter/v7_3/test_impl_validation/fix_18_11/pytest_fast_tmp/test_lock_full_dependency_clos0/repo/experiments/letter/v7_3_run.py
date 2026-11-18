"""Doan Van Tai — V7-3 Phase A training and two-TRAIN-night timing pilot only.

No test command is implemented. A date outside the validated train cache is
rejected before any simulator call. Phase B needs Claude's future card.
"""
import argparse
from datetime import datetime
import json
import platform
import resource
import time

import numpy as np

from experiments.ext_validity import ev_te as T
from experiments.letter import e4_geant as E
from experiments.letter import v7_3_data as D
from experiments.letter import v7_3_sim as S

OUT=D.OUT
TRAIN_SEED,PILOT_SEED=730001,7370001


def require_train(training,date):
    indices=np.flatnonzero(training['dates']==date)
    if len(indices)!=1:
        raise ValueError('Phase A forbids test-night simulation: date must be retained train')
    return int(indices[0])


def timer(timings,name,fn):
    cpu,wall=time.process_time(),time.perf_counter()
    result=fn()
    timings[name]=dict(CPU_s=time.process_time()-cpu,wall_s=time.perf_counter()-wall)
    return result


def ratio(numerator,denominator):
    return None if denominator is None or denominator<=0 else float(numerator/denominator)


def train(out=OUT,n=200):
    if n!=200:
        raise ValueError('brief fixes N=200 training instances per night')
    T.new(out/'train/summary.json')
    training,config=D.load_training(out=out)
    inc,cap=config['incidence'],float(config['capacity'].item())
    # Precompile before scientific timers. Record build separately.
    build_cpu=time.process_time();build_wall=time.perf_counter();S.native();T.native()
    build=dict(CPU_s=time.process_time()-build_cpu,wall_s=time.perf_counter()-build_wall)
    records=[]
    for date in training['dates']:
        j=require_train(training,date);timings={}
        root=T.seed_for(TRAIN_SEED,'V7-3|'+date)
        (fresh,stale)=timer(timings,'warmup',lambda:S.warm_instances(inc,training['warm'][j],cap,n,T.seed_for(root,'warm')))
        hs=np.rint(S.HOURS*3600/S.DT).astype(int)
        costs,_,_,trace=timer(timings,'true_train_night',lambda:S.variable(
            inc,training['days'][j,:24],cap,*fresh,T.seed_for(root,'rate-rollout'),hs=hs,trace=True))
        rates=costs[:,:,-1]/(6*3600)
        weekend=int(datetime.fromisoformat(date).weekday()>=5)
        m0=timer(timings,'M0_fresh',lambda:S.mean_rollout(inc,config['profiles'][weekend],cap,*fresh))
        _,tie=E.pick(m0)
        stale_ties=[]
        for tau in S.TAU_SECONDS:
            pm,pq=timer(timings,f'posterior_{int(tau)}',lambda tau=tau:S.forward_posterior(
                inc,training['warm'][j,-1],cap,stale[tau],tau,64,T.seed_for(root,f'posterior-{tau}')))
            old=timer(timings,f'M0_stale_{int(tau)}',lambda:S.mean_rollout(
                inc,config['profiles'][weekend],cap,pm,pq).reshape(n,64,2,4).mean(axis=1))
            stale_ties.append(E.pick(old)[1].mean(axis=0).tolist())
        tis=[]
        for action in range(2):
            ti,censored,error=T.estimate_tint(trace[:,action],S.DT)
            tis.append(dict(T_int_s=ti,censored=censored,error=error,h6_over_T_int=ratio(21600,ti),
                            P_backlog_positive=float((trace[:,action]>0).mean()),
                            max_backlog_Mbit=float(trace[:,action].max())))
        demand_total=training['days'][j,:24].sum(axis=1)
        slope=float(np.polyfit((np.arange(24)+.5)*.25,demand_total,1)[0])
        s_hat=float((rates[:,1]-rates[:,0]).mean())
        record=dict(date=date,training_only=True,N=n,K=64,seed=int(root),
                    mean_backlog_rates_Mbit=rates.mean(axis=0).tolist(),s_hat_Mbit=s_hat,
                    T_int=tis,T_int_trace_instance=0,
                    T_int_interpretation='first independently seeded instance per night, 6h nonstationary record; no concatenation across nights',
                    M0_tie_share_fresh=tie.mean(axis=0).tolist(),M0_tie_share_stale=stale_ties,
                    total_demand_slope_Mbps_per_hour=slope,
                    demand_first_Mbps=float(demand_total[0]),demand_last_Mbps=float(demand_total[-1]),
                    timings=timings)
        E.write_npz(out/f'train/raw/{date}.npz',dict(costs=costs,rates=rates,backlog_first_instance=trace,
                     fresh_modes=fresh[0],fresh_queues=fresh[1],M0=m0,seed=np.array(root,dtype=np.uint64)))
        E.write_json(out/f'train/raw/{date}.json',record)
        records.append(record)
        print(json.dumps(dict(date=date,s_hat=s_hat,T_int=[x['T_int_s'] for x in tis],CPU_s=sum(t['CPU_s'] for t in timings.values()))),flush=True)
    per_night=np.array([r['s_hat_Mbit'] for r in records]);s_hat=float(per_night.mean())
    signs=np.sign(per_night);sign=float(np.sign(s_hat))
    means=np.mean([r['mean_backlog_rates_Mbit'] for r in records],axis=0)
    summary=dict(owner='Doan Van Tai',training_only=True,N=n,K=64,train_nights=len(records),
                 s_hat_Mbit=s_hat,mean_backlog_rates_Mbit=means.tolist(),
                 gap_definition='Switch-minus-Stay backlog cost rate; positive favors Stay',
                 sign_counts=dict(positive=int((signs>0).sum()),zero=int((signs==0).sum()),negative=int((signs<0).sum())),
                 sign_stability_fraction=float((signs==sign).mean()),
                 sign_stability_numerator=int((signs==sign).sum()),sign_stability_denominator=len(records),
                 M0_tie_share_fresh=np.mean([r['M0_tie_share_fresh'] for r in records],axis=0).tolist(),
                 M0_tie_share_stale=np.mean([r['M0_tie_share_stale'] for r in records],axis=0).tolist(),
                 T_int_sampling='one full 0.05s backlog trace (instance 0) per train night per configuration; rates/ties use all 200 instances',
                 T_int_by_night=[dict(date=r['date'],actions=r['T_int']) for r in records],
                 timing_build=build,
                 total_measured_component_CPU_s=sum(sum(t['CPU_s'] for t in r['timings'].values()) for r in records),
                 nonstationarity_slope_quantiles_Mbps_per_hour=np.quantile([r['total_demand_slope_Mbps_per_hour'] for r in records],[0,.25,.5,.75,1]).tolist(),
                 seed=TRAIN_SEED,dt_s=S.DT,beta=S.BETA,fast_flip_rate_per_s=1.,
                 warnings=['T_int is descriptive for nonstationary nights. Zero variance means undefined.',
                           'Nightwise sign counts have denominator nights, not independent population trials.',
                           'No test-night outcomes computed.'])
    E.write_json(out/'train/summary.json',summary)
    T.write_csv(out/'train/night_statistics.csv',[
        dict(date=r['date'],s_hat_Mbit=r['s_hat_Mbit'],T_int_Stay_s=r['T_int'][0]['T_int_s'],
             T_int_Switch_s=r['T_int'][1]['T_int_s'],h6_over_T_int_Stay=r['T_int'][0]['h6_over_T_int'],
             h6_over_T_int_Switch=r['T_int'][1]['h6_over_T_int'],
             slope_Mbps_per_hour=r['total_demand_slope_Mbps_per_hour'],
             CPU_s=sum(x['CPU_s'] for x in r['timings'].values())) for r in records])
    return summary


def compute_night(training,config,date,s_hat,*,n=2,k=4,r_dec=4,r_eval=8,seed=PILOT_SEED):
    j=require_train(training,date)  # Must precede every engine/timer call.
    timings={};root=T.seed_for(seed,'V7-3|'+date)
    inc,cap=config['incidence'],float(config['capacity'].item())
    hs=np.rint(S.HOURS*3600/S.DT).astype(int)
    fresh,stale=timer(timings,'warmup',lambda:S.warm_instances(inc,training['warm'][j],cap,n,T.seed_for(root,'warm')))
    weekend=int(datetime.fromisoformat(date).weekday()>=5)
    m0=timer(timings,'M0_fresh',lambda:S.mean_rollout(inc,config['profiles'][weekend],cap,*fresh))
    names=['M0','Hybrid','Stationary']
    decisions=np.empty((n,3,2,2,4),dtype=np.int16)
    ties=np.zeros_like(decisions,dtype=bool)
    def twins(costs):
        plain=E.pick(costs)
        hybrid=E.pick(E.hybrid_costs(costs,[0.,s_hat],S.HOURS*3600))
        stationary=np.full((n,4),int(s_hat<0),dtype=np.int16)
        return np.stack([plain[0],hybrid[0],stationary],axis=1),np.stack([plain[1],hybrid[1],np.full((n,4),s_hat==0)],axis=1)
    fresh_d,fresh_t=timer(timings,'choices_fresh',lambda:twins(m0))
    decisions[:,:,0]=fresh_d[:,:,None,:];ties[:,:,0]=fresh_t[:,:,None,:]
    for t,tau in enumerate(S.TAU_SECONDS):
        pm,pq=timer(timings,f'posterior_{int(tau)}',lambda tau=tau:S.forward_posterior(
            inc,training['warm'][j,-1],cap,stale[tau],tau,k,T.seed_for(root,f'posterior-{tau}')))
        old=timer(timings,f'M0_stale_{int(tau)}',lambda:S.mean_rollout(
            inc,config['profiles'][weekend],cap,pm,pq).reshape(n,k,2,4).mean(axis=1))
        decisions[:,:,1,t],ties[:,:,1,t]=timer(timings,f'choices_stale_{int(tau)}',lambda:twins(old))
    def rollout(rollouts,purpose):
        m,q=(np.repeat(x,rollouts,axis=0) for x in fresh)
        costs=S.variable(inc,training['days'][j,:24],cap,m,q,T.seed_for(root,purpose),hs=hs)[0]
        return costs.reshape(n,rollouts,2,4)
    dec_values=timer(timings,'reference_decision',lambda:rollout(r_dec,'reference-decision'))
    evaluation=timer(timings,'paired_evaluation',lambda:rollout(r_eval,'evaluation'))
    def metrics():
        v=evaluation.mean(axis=1)
        reference,ref_tie=E.pick(dec_values.mean(axis=1))
        cref=E.costs_for_decisions(v,reference)
        selected=E.costs_for_decisions(v,decisions)
        regret=selected-cref[:,None,None,None,:]
        gs=selected[:,:,1]-selected[:,:,0]
        return v,reference,ref_tie,cref,selected,regret,gs
    v,reference,ref_tie,cref,selected,regret,gs=timer(timings,'metrics_gather',metrics)
    # Exact gather identity is required, not a confidence-interval assertion.
    if not np.array_equal(E.costs_for_decisions(v,reference),cref):
        raise AssertionError('CRN gather identity failed')
    arrays=dict(V=v,reference_decision=reference,C_ref=cref,decisions=decisions,tie_flags=ties,
                reference_tie_flags=ref_tie,paired_evaluation=evaluation,reference_decision_rollouts=dec_values,
                costs=selected,regret=regret,G_S=gs,pipelines=np.array(names),
                h_seconds=S.HOURS*3600,tau_seconds=np.array(S.TAU_SECONDS))
    metadata=dict(owner='Doan Van Tai',date=date,training_only=True,pilot=True,N=n,K=k,R_dec=r_dec,R_eval=r_eval,
                  seed=seed,dt_s=S.DT,timings=timings,units=dict(cost='Mbit*s',rate='Mbit'),
                  C_ref_mean_Mbit_s=cref.mean(axis=0).tolist(),
                  regret_mean_Mbit_s=regret.mean(axis=0).tolist(),G_S_mean_Mbit_s=gs.mean(axis=0).tolist(),
                  percentages_defined=(cref.mean(axis=0)>0).tolist(),
                  reference_evaluation_streams_distinct=T.seed_for(root,'reference-decision')!=T.seed_for(root,'evaluation'),
                  peak_memory_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
                  axes=dict(decisions=['instance','pipeline','side:fresh,stale','tau','h'],V=['instance','action','h']))
    return arrays,metadata


def pilot(out=OUT):
    T.new(out/'pilot/summary.json')
    training,config=D.load_training(out=out)
    summary=T.read_json(out/'train/summary.json')
    dates=training['dates'].tolist()
    weekdays=[d for d in dates if datetime.fromisoformat(d).weekday()<5]
    weekends=[d for d in dates if datetime.fromisoformat(d).weekday()>=5]
    chosen=[weekdays[0],weekends[0]] if weekdays and weekends else dates[:2]
    records=[]
    for date in chosen:
        arrays,meta=compute_night(training,config,date,summary['s_hat_Mbit'])
        timer(meta['timings'],'write_raw_npz',lambda:E.write_npz(out/f'pilot/{date}.npz',arrays))
        E.write_json(out/f'pilot/{date}.json',meta)
        records.append(meta)
        print(json.dumps(dict(date=date,CPU_s=sum(x['CPU_s'] for x in meta['timings'].values()),timings=meta['timings'])),flush=True)
    nt=len(T.read_json(out/'data_manifest.json')['test_dates'])
    scale=dict(warmup=100.,M0_fresh=100.,posterior_300=1600.,posterior_900=1600.,
               M0_stale_300=1600.,M0_stale_900=1600.,reference_decision=1600.,paired_evaluation=1600.)
    scale.update(choices_fresh=100.,choices_stale_300=100.,choices_stale_900=100.,
                 metrics_gather=1600.,write_raw_npz=1600.)
    components={name:float(np.mean([r['timings'][name]['CPU_s'] for r in records]))*factor*nt for name,factor in scale.items()}
    projected=sum(components.values())
    # Stress proxy uses the heaviest measured full-size train night, without
    # opening any test TM outcomes or load/intensity summaries.
    train_metas=[T.read_json(out/f'train/raw/{d}.json') for d in dates]
    heaviest=max(train_metas,key=lambda r:r['timings']['true_train_night']['CPU_s'])
    train_rollout=heaviest['timings']['true_train_night']['CPU_s']
    stress=(projected-components['reference_decision']-components['paired_evaluation']
            +nt*(64+128)*train_rollout)
    result=dict(owner='Doan Van Tai',training_only=True,pilot_dates=chosen,pilot_N=2,pilot_K=4,
                pilot_R_dec=4,pilot_R_eval=8,full=dict(N=200,K=64,R_dec=64,R_eval=128,test_nights=nt,workers=20,target='n2-standard-32'),
                CPU_s_by_component=components,projected_CPU_s=projected,projected_CPU_hours=projected/3600,
                ideal_wall_s_20_workers=projected/20,ideal_wall_hours_20_workers=projected/72000,
                stress_train_night=heaviest['date'],stress_full_train_rollout_CPU_s=train_rollout,
                stress_projected_CPU_s=stress,stress_ideal_wall_hours_20_workers=stress/72000,
                projection='linear in N for fresh/warmup, N*K for stale, N*R for reference/evaluation; average of two train pilot nights',
                stress_proxy='replace rollout components by max measured train N200 rollout cost times R_dec+R_eval per night; includes trace overhead',
                hardware=dict(machine=platform.machine(),platform=platform.platform(),python=platform.python_version(),
                              processor=next((line.split(':',1)[1].strip() for line in open('/proc/cpuinfo') if line.startswith('model name')),platform.processor())),
                limitations=['Local CPU-seconds, not measured n2-standard-32 seconds; ideal division by 20 assumes independent workers and no contention.',
                             'No test load intensity opened; workload can differ. Stress proxy is not an upper bound.',
                             'No cloud VM, SSH, test card or test outcomes in this phase.'])
    E.write_json(out/'pilot/summary.json',result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['train','pilot'])
    a=p.parse_args()
    (train if a.command=='train' else pilot)()
