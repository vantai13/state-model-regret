"""Doan Van Tai — independent saved-artifact replay; never calls any simulator.

Does not import v7_3_run (the scorer) or v7_3_sim. Checks training quantities,
pilot regret/G_S/CRN, train-only envelopes and tracked-source preservation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

from experiments.letter import v7_3_data as D


def first_zero_tint(series,dt):
    z=series-series.mean()
    if not np.any(z):
        return None,True
    n=len(z)
    c=np.fft.irfft(np.abs(np.fft.rfft(z,n=2*n))**2)[:n//4]
    c=c/np.arange(n,n-len(c),-1)
    r=c/c[0]
    zeros=np.where(r<=0)[0]
    k=int(zeros[0]) if len(zeros) else len(r)-1
    area=sum((r[:-1][:k-1]+r[1:k])/2)*dt
    area+=.5*r[k-1]*dt*(r[k-1]/(r[k-1]-r[k]) if len(zeros) else 1)
    return float(area),not bool(len(zeros))


def verify(out=D.OUT, result_name='verification.json'):
    if Path(result_name).name!=result_name:
        raise ValueError('verification result must stay in V7-3 output directory')
    manifest=json.loads((out/'data_manifest.json').read_text())
    summary=json.loads((out/'train/summary.json').read_text())
    pilot=json.loads((out/'pilot/summary.json').read_text())
    tr,cf=D.load_training(out=out)
    dates=tr['dates'].tolist()
    assert dates==manifest['train_dates']
    assert not set(dates)&set(manifest['test_dates'])
    cap=float(cf['capacity'].item());inc=cf['incidence'];checks=0
    daytime_peak=np.max(np.einsum('nsd,ed->nse',tr['days'][:,24:88],inc[0],optimize=True))
    assert np.isclose(daytime_peak/cap,.9,rtol=0,atol=1e-15);checks+=1
    # These three certificates use train only and explain the observed ties.
    warm_max=float((1.3*np.einsum('nsd,ed->nse',tr['warm'],inc[0],optimize=True)/cap).max())
    stay_max=float((1.3*np.einsum('nsd,ed->nse',tr['days'][:,:24],inc[0],optimize=True)/cap).max())
    profile_max=float((1.3*np.einsum('ksd,aed->ksae',cf['profiles'],inc,optimize=True)/cap).max())
    assert warm_max<1 and stay_max<1 and profile_max<1;checks+=3
    s_values=[];mc_variances=[];tis=[[],[]];slope=[];night_cpu=[]
    for date in dates:
        meta=json.loads((out/f'train/raw/{date}.json').read_text())
        j=dates.index(date)
        with np.load(out/f'train/raw/{date}.npz',allow_pickle=False) as f:
            rates=f['costs'][:,:,-1]/21600
            np.testing.assert_array_equal(rates,f['rates']);checks+=1
            assert len(rates)==200 and meta['N']==200
            assert not f['fresh_queues'].any() and not f['M0'].any()
            delta=rates[:,1]-rates[:,0]
            s=float(delta.mean());s_values.append(s)
            mc_variances.append(float(delta.var(ddof=1)/len(delta)))
            np.testing.assert_allclose(s,meta['s_hat_Mbit'],rtol=0,atol=1e-15);checks+=1
            for a in range(2):
                ti,censored=first_zero_tint(f['backlog_first_instance'][:,a],.05)
                saved=meta['T_int'][a]
                assert censored==saved['censored']
                if ti is None:
                    assert saved['T_int_s'] is None and saved['h6_over_T_int'] is None
                else:
                    np.testing.assert_allclose(ti,saved['T_int_s'],rtol=1e-12,atol=1e-12)
                    np.testing.assert_allclose(21600/ti,saved['h6_over_T_int'],rtol=1e-12)
                    tis[a].append(dict(date=date,T_int_s=ti,h6_over_T_int=21600/ti))
                checks+=1
        assert np.all(np.array(meta['M0_tie_share_fresh'])==1)
        assert np.all(np.array(meta['M0_tie_share_stale'])==1);checks+=2
        x=(np.arange(24)+.5)*.25;y=tr['days'][j,:24].sum(axis=1)
        fitted=float(np.dot(x-x.mean(),y-y.mean())/np.dot(x-x.mean(),x-x.mean()))
        np.testing.assert_allclose(fitted,meta['total_demand_slope_Mbps_per_hour'],atol=1e-10,rtol=1e-12)
        slope.append(fitted);checks+=1
        night_cpu.append(meta['timings']['true_train_night']['CPU_s'])
    s_hat=float(np.mean(s_values))
    np.testing.assert_allclose(s_hat,summary['s_hat_Mbit'],rtol=0,atol=1e-15);checks+=1
    sign=np.sign(s_hat)
    assert int(sum(np.sign(s_values)==sign))==summary['sign_stability_numerator'];checks+=1
    for date in pilot['pilot_dates']:
        assert date in dates and date not in manifest['test_dates'];checks+=1
        meta=json.loads((out/f'pilot/{date}.json').read_text())
        with np.load(out/f'pilot/{date}.npz',allow_pickle=False) as f:
            v=f['paired_evaluation'].mean(axis=1)
            np.testing.assert_array_equal(v,f['V'])
            ref=f['reference_decision_rollouts'].mean(axis=1).argmin(axis=1)
            np.testing.assert_array_equal(ref,f['reference_decision'])
            cref=np.take_along_axis(v,ref[:,None,:],axis=1)[:,0,:]
            np.testing.assert_array_equal(cref,f['C_ref'])
            decisions=f['decisions'];costs=np.empty(decisions.shape,dtype=float)
            for index in np.ndindex(decisions.shape):
                i,p,s,t,h=index
                costs[index]=v[i,decisions[index],h]
            np.testing.assert_array_equal(costs,f['costs'])
            np.testing.assert_array_equal(costs-cref[:,None,None,None,:],f['regret'])
            np.testing.assert_array_equal(costs[:,:,1]-costs[:,:,0],f['G_S'])
            assert not cref.any() and not f['G_S'].any()
            assert (decisions==0).all() and (f['tie_flags'][:,0]).all()
            # Identical selected decisions use exactly the same paired values.
            assert np.array_equal(costs[:,0],costs[:,1]) and np.array_equal(costs[:,0],costs[:,2])
            checks+=9
    assert np.isclose(sum(pilot['CPU_s_by_component'].values()),pilot['projected_CPU_s'],rtol=1e-15);checks+=1
    assert np.isclose(pilot['projected_CPU_s']/20,pilot['ideal_wall_s_20_workers'],rtol=1e-15);checks+=1
    baseline=json.loads((out/'initial_tracked_sha256.json').read_text())
    changed=[path for path,digest in baseline.items()
             if not Path(path).is_file() or hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest]
    assert not changed,changed
    checks+=len(baseline)
    protocol=json.loads((out/'PHASE_A_PROTOCOL.json').read_text())
    current_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    subprocess.run(['git','merge-base','--is-ancestor',protocol['brief_commit'],current_head],check=True)
    committed_brief=subprocess.check_output(['git','show','HEAD:notes/ops/codex/V7_3_phaseA_brief.md'])
    assert hashlib.sha256(committed_brief).hexdigest()==protocol['brief_sha256']
    assert hashlib.sha256(Path('notes/ops/codex/V7_3_phaseA_brief.md').read_bytes()).hexdigest()==protocol['brief_sha256'];checks+=2
    paths=[*Path('experiments/letter').glob('v7_3_*.py'),*Path('tests').glob('test_letter_v7_3*.py')]
    result=dict(owner='Doan Van Tai',status='PASS',checks=checks,training_only=True,
                test_nights_simulated=0,tracked_files_modified=changed,
                starting_HEAD=protocol['brief_commit'],current_HEAD=current_head,
                HEAD_unchanged=current_head==protocol['brief_commit'],
                original_tracked_bytes_unchanged=True,committed_brief_unchanged=True,
                no_simulator_calls=True,train_nights=len(dates),train_instances=200*len(dates),
                s_hat_Mbit=s_hat,s_hat_conditional_MC_SE_Mbit=float(np.sqrt(sum(mc_variances))/len(dates)),
                envelope_max_utilization=dict(warmup_Stay=warm_max,train_night_Stay=stay_max,M0_profile_both_actions=profile_max),
                T_int_defined= [len(t) for t in tis],T_int_details=tis,
                T_int_resolution_warning='dt=0.05s; estimates near one step are unresolved as continuous-time correlation scales',
                sign_counts=summary['sign_counts'],pilot_dates=pilot['pilot_dates'],
                source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                imported_source_sha256={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ['experiments/ext_validity/ev_te.py','experiments/letter/e4_geant.py']})
    with (out/result_name).open('x') as f:
        json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='verification.json')
    verify(result_name=parser.parse_args().output)
