"""Doan Van Tai — independent raw-only V7-3 recomputation and comparison.

Does not import the runner or scorer. Only file-integrity helpers and the
pre-existing training T_int estimator are shared; decisions, costs, case
metrics, populations and verdicts are recomputed here independently.
"""
from collections import Counter
import csv
from datetime import datetime
import math
from pathlib import Path

import numpy as np

from experiments.letter import v7_3_day as Day
from experiments.letter import v7_3_test_common as C

NAMES = ('M0','Hybrid','Stationary','M0_random_tie','M0_switch_tie','Hybrid_S')


def recompute(raw, label, p):
    for name,array in raw.items():
        if np.issubdtype(array.dtype,np.number) and not np.all(np.isfinite(array)):
            raise ValueError('nonfinite raw array: '+name)
    peaks = np.max(raw['input_utilization'],axis=(0,2))
    recomputed_stratum = 'S' if max(peaks)<1 else 'O'
    if recomputed_stratum!=label['stratum']:
        raise ValueError('stratum differs from raw input utilization')
    value = np.mean(raw['paired_evaluation'],axis=1)
    oracle_choice = np.argmin(np.mean(raw['reference_decision_rollouts'],axis=1),axis=1)
    count = len(value)
    horizons = np.asarray(p['hours'])*3600
    reference = np.empty((count,4))
    for i in range(count):
        for j in range(4):
            reference[i,j] = value[i,oracle_choice[i,j],j]
    # Explicit per-side minimization, separate from the scorer's vector gathers.
    predictions = [raw['M0_predicted_fresh']]+[raw['M0_predicted_stale'][:,t] for t in range(2)]
    actions, ties, evaluated = {}, {}, {}
    for name in NAMES:
        actions[name] = np.empty((count,3,4))
        ties[name] = np.zeros((count,3,4),dtype=bool)
        evaluated[name] = np.empty((count,3,4))
        for side in range(3):
            forecast = predictions[side].copy()
            if name in ('Hybrid','Hybrid_S'):
                rate = p['s_hat_pooled_Mbit'] if name=='Hybrid' else p['s_hat_S_Mbit_sensitivity']
                forecast[:,1,:] = forecast[:,1,:] + rate[label['regime']]*horizons
            for i in range(count):
                for j in range(4):
                    is_tie = bool(forecast[i,0,j]==forecast[i,1,j])
                    switch = float(forecast[i,1,j]<forecast[i,0,j])
                    if name=='Stationary':
                        is_tie = p['s_hat_pooled_Mbit'][label['regime']]==0
                        switch = float(p['s_hat_pooled_Mbit'][label['regime']]<0)
                    elif name=='M0_random_tie' and is_tie:
                        switch = .5
                    elif name=='M0_switch_tie' and is_tie:
                        switch = 1.
                    actions[name][i,side,j] = switch
                    ties[name][i,side,j] = is_tie
                    evaluated[name][i,side,j] = ((value[i,0,j]+value[i,1,j])/2
                        if switch==.5 else value[i,int(switch),j])
    # Saved convenience arrays are checked, not taken as independent truth.
    expected = {'V':value,'C_ref':reference,'reference_decision':oracle_choice,
                'reference_tie_flags':(raw['reference_decision_rollouts'].mean(axis=1)[:,0]==
                                       raw['reference_decision_rollouts'].mean(axis=1)[:,1]),
                'h_seconds':horizons,'tau_seconds':np.asarray(p['tau_seconds'])}
    for key,computed in expected.items():
        if not np.array_equal(raw[key],computed):
            raise ValueError('raw identity mismatch: '+key)
    for pi,name in enumerate(NAMES[:3]):
        for side in range(2):
            for t in range(2):
                si = 0 if side==0 else t+1
                for key,computed in (('decisions',actions[name][:,si]),('tie_flags',ties[name][:,si]),
                        ('costs',evaluated[name][:,si]),('regret',evaluated[name][:,si]-reference)):
                    if not np.array_equal(raw[key][:,pi,side,t],computed):
                        raise ValueError('raw identity mismatch: '+key)
                if not np.array_equal(raw['G_S'][:,pi,t],evaluated[name][:,t+1]-evaluated[name][:,0]):
                    raise ValueError('raw identity mismatch: G_S')
    tint = [Day.resolution(raw['backlog_trace'][:,a],p['dt_s']) for a in range(2)]
    rows = []
    for t,tau in enumerate(p['tau_seconds']):
        for j,h in enumerate(horizons):
            ref = float(np.mean(reference[:,j]))
            usable = bool(ref/h>=p['evaluable_threshold_Mbit'])
            row = dict(regime=label['regime'],date=label['date'],stratum=label['stratum'],
                       tau_s=tau,h_hours=int(h/3600),N=count,evaluable=usable,
                       C_ref_Mbit_s=ref,C_ref_Mbit=ref/h,C_ref_ms=ref/h/p['capacity_Mbps']*1000,
                       reference_tie_share=float(raw['reference_tie_flags'][:,j].mean()))
            for a,name in enumerate(('Stay','Switch')):
                ti = tint[a]['T_int_s']
                row['T_int_'+name+'_s'] = ti
                row['T_int_'+name+'_censored'] = tint[a]['censored']
                row['T_int_'+name+'_status'] = tint[a]['status']
                row['h_over_T_int_'+name] = float(h/ti) if ti is not None and ti>0 else None
            for name in NAMES:
                excess = []
                for side,si in (('fresh',0),('stale',t+1)):
                    mean = float(evaluated[name][:,si,j].mean())
                    delta = mean-ref
                    excess.append(delta)
                    pre = name+'_'+side
                    row[pre+'_L_Mbit_s'] = mean
                    row[pre+'_L_Mbit'] = mean/h
                    row[pre+'_L_ms'] = mean/h/p['capacity_Mbps']*1000
                    row[pre+'_R_Mbit_s'] = delta
                    row[pre+'_R_Mbit'] = delta/h
                    row[pre+'_R_ms'] = delta/h/p['capacity_Mbps']*1000
                    row[pre+'_R_pct'] = delta/ref*100 if usable else None
                    row[pre+'_F_switch'] = float(actions[name][:,si,j].mean())
                    row[pre+'_tie_share'] = float(ties[name][:,si,j].mean())
                differences = evaluated[name][:,t+1,j]-evaluated[name][:,0,j]
                g = float(differences.mean())
                se = float(np.std(differences,ddof=1)/np.sqrt(count)) if count>1 else None
                for field,amount in (('both_R',max(excess)),('G_S',g),('se_G_S',se)):
                    row[name+'_'+field+'_Mbit_s'] = amount
                    row[name+'_'+field+'_Mbit'] = amount/h if amount is not None else None
                    row[name+'_'+field+'_ms'] = amount/h/p['capacity_Mbps']*1000 if amount is not None else None
                    row[name+'_'+field+'_pct'] = amount/ref*100 if usable and amount is not None else None
            for side,si in (('fresh',0),('stale',t+1)):
                row['Hybrid_Stationary_'+side+'_agree_n'] = int(np.count_nonzero(
                    actions['Hybrid'][:,si,j]==actions['Stationary'][:,si,j]))
            difference = row['M0_stale_F_switch']-row['M0_fresh_F_switch']
            predicted = int(np.sign(p['s_hat_pooled_Mbit'][label['regime']]*difference))
            resolved = bool(difference!=0 and row['M0_se_G_S_Mbit_s'] is not None and
                            abs(row['M0_G_S_Mbit_s'])>2*row['M0_se_G_S_Mbit_s'])
            agrees = predicted==int(np.sign(row['M0_G_S_Mbit_s']))
            population = label['regime'] in p['confirmatory_regimes'] and label['stratum']=='S' and int(h/3600) in p['test_horizons_hours']
            row.update(H1_predicted_sign=predicted,H1_resolved=resolved,H1_agrees=agrees,
                       confirmatory_population=population)
            outside = 'OUTSIDE_POPULATION' if not population else 'NON_EVALUABLE' if not usable else None
            row['H1_clause'] = outside or ('F_EQUAL' if difference==0 else 'GS_WITHIN_2SE' if not resolved else
                                           'RESOLVED_AGREE' if agrees else 'RESOLVED_DISAGREE')
            row['H2_clause'] = outside or ('REGRET_LE_0.5' if row['Hybrid_both_R_pct']<=.5 else 'REGRET_GT_0.5')
            row['H3_clause'] = outside or ('M0_LE_0.5' if row['M0_both_R_pct']<=.5 else
                'HYBRID_LOWER' if row['Hybrid_both_R_pct']<row['M0_both_R_pct'] else 'HYBRID_NOT_LOWER')
            if not usable:
                row = {key:None if key.endswith('_ms') else val for key,val in row.items()}
            rows.append(row)
    return rows


def ratio_verdict(n,d,cut,minimum=1,forecast=False):
    if d<minimum:
        label = 'NOT_EVALUABLE'
    elif n/d<cut:
        label = 'NOT_HELD' if forecast else 'FAIL'
    else:
        label = 'HELD' if forecast else 'PASS'
    return dict(numerator=int(n),denominator=int(d),fraction=float(n/d) if d else None,
                threshold=cut,minimum=minimum,verdict=label)


def trial(rows,which,p):
    eligible = [r for r in rows if r['confirmatory_population'] and r['evaluable']]
    if which=='H1':
        selected = [r for r in eligible if r['H1_resolved']]
        hits = sum(r['H1_agrees'] for r in selected)
    elif which=='H2':
        selected = eligible
        hits = len([r for r in selected if r['Hybrid_both_R_pct']<=.5])
    else:
        selected = [r for r in eligible if r['M0_both_R_pct']>.5]
        hits = len([r for r in selected if r['Hybrid_both_R_pct']<r['M0_both_R_pct']])
    rule = p['tests'][which]
    answer = ratio_verdict(hits,len(selected),rule['pass_share'],rule['min_cases'])
    answer['population_cases'] = len(eligible)
    answer['clauses'] = dict(sorted(Counter(r[which+'_clause'] for r in rows).items()))
    answer['deciding_clause'] = 'minimum_cases' if len(selected)<rule['min_cases'] else 'pass_share'
    return answer


def med(values):
    values = [x for x in values if x is not None]
    return float(np.median(values)) if values else None


def describe_again(rows):
    eligible = [r for r in rows if r['evaluable']]
    excluded = [r for r in rows if not r['evaluable']]
    answer = dict(cases=len(rows),evaluable=sum(r['evaluable'] for r in rows),
                  non_evaluable=sum(not r['evaluable'] for r in rows),pipelines={},
                  cost_summary_population='evaluable cases; non-evaluable physical values reported separately',
                  non_evaluable_Mbit={})
    for name in NAMES:
        metrics = {}
        for field in ('both_R_pct','both_R_Mbit','both_R_ms','G_S_pct','G_S_Mbit','G_S_ms'):
            metrics[field] = med([r[name+'_'+field] for r in eligible])
        harm = [r for r in eligible if r[name+'_G_S_Mbit_s']<0]
        metrics.update(harm_cases=len(harm),harm_share=len(harm)/len(eligible) if eligible else None,
            harm_size_median={u:med([-r[name+'_G_S_'+u] for r in harm if r[name+'_G_S_'+u] is not None])
                              for u in ('pct','Mbit','ms')},
            tie_share_fresh=med([r[name+'_fresh_tie_share'] for r in rows]),
            tie_share_stale=med([r[name+'_stale_tie_share'] for r in rows]))
        answer['pipelines'][name] = metrics
        answer['non_evaluable_Mbit'][name] = dict(
            both_R_median_Mbit=med([r[name+'_both_R_Mbit'] for r in excluded]),
            G_S_median_Mbit=med([r[name+'_G_S_Mbit'] for r in excluded]),
            harm_cases=sum(r[name+'_G_S_Mbit']<0 for r in excluded))
    return answer


def median_rule(rows,key,cut,lower):
    values = [r[key] for r in rows if r[key] is not None]
    value = med(values)
    passed = value is not None and (value>=cut if lower else value<=cut)
    return dict(value=value,denominator=len(values),threshold=cut,
                verdict='NOT_EVALUABLE' if value is None else 'HELD' if passed else 'NOT_HELD')


def rebuild_summary(rows,inputs,p):
    rows = sorted(rows,key=lambda r:(r['regime'],r['date'],r['tau_s'],r['h_hours']))
    record_labels = inputs['records']
    strata = {}
    for s in ('S','O'):
        cells = [r for r in rows if r['stratum']==s]
        strata[s] = dict(records=sum(r['stratum']==s for r in record_labels),cases=len(cells),
                          evaluable=sum(r['evaluable'] for r in cells))
    tests = {}
    for which in ('H1','H2','H3'):
        tests[which] = trial(rows,which,p)
        tests[which]['by_horizon'] = {str(h):trial([r for r in rows if r['h_hours']==h],which,p)
                                       for h in p['test_horizons_hours']}
    stable = [r for r in rows if r['regime'] in p['confirmatory_regimes'] and r['stratum']=='S']
    s6 = [r for r in stable if r['h_hours']==6 and r['evaluable']]
    all_s = sum(all(x['stratum']=='S' for x in record_labels if x['date']==d) for d in inputs['dates'])
    f1 = ratio_verdict(all_s,len(inputs['dates']),.6,forecast=True)
    f1['definition'] = 'weekday S for every declared regime; per-regime counts also reported'
    f1['by_regime'] = {}
    for g in p['regimes']:
        group = [r for r in record_labels if r['regime']==g]
        f1['by_regime'][g] = ratio_verdict(sum(r['stratum']=='S' for r in group),len(group),.6,forecast=True)
    f2 = ratio_verdict(sum(r['M0_G_S_Mbit_s']<0 and r['H1_resolved'] for r in s6),len(s6),.6,forecast=True)
    f3 = median_rule(s6,'M0_both_R_pct',5,True)
    f3['physical_medians'] = describe_again(s6)['pipelines']['M0']
    numerator = denominator = 0
    for r in rows:
        if r['h_hours']<2:
            continue
        numerator += r['Hybrid_Stationary_stale_agree_n']
        denominator += r['N']
        if r['tau_s']==p['tau_seconds'][0]:
            numerator += r['Hybrid_Stationary_fresh_agree_n']
            denominator += r['N']
    f4 = ratio_verdict(numerator,denominator,.99,forecast=True)
    f4['population'] = 'all regimes/strata, h>=2h, unique fresh/stale300/stale900 decisions'
    f4['by_horizon'] = {}
    for h in p['test_horizons_hours']:
        n_h = d_h = 0
        for r in rows:
            if r['h_hours']!=h:
                continue
            n_h += r['Hybrid_Stationary_stale_agree_n']
            d_h += r['N']
            if r['tau_s']==p['tau_seconds'][0]:
                n_h += r['Hybrid_Stationary_fresh_agree_n']
                d_h += r['N']
        f4['by_horizon'][str(h)] = ratio_verdict(n_h,d_h,.99,forecast=True)
    overload = [r for r in rows if r['stratum']=='O' and r['evaluable']]
    individual = {name:ratio_verdict(sum(r[name+'_both_R_pct']<=.5 for r in overload),
                                           len(overload),.8,forecast=True) for name in NAMES[:3]}
    f5 = dict(by_pipeline=individual,
              verdict='NOT_EVALUABLE' if not overload else 'HELD' if all(
                  entry['verdict']=='HELD' for entry in individual.values()) else 'NOT_HELD',
              deciding_clause='each_pipeline_share',
              joint_numerator=sum(all(r[name+'_both_R_pct']<=.5 for name in NAMES[:3]) for r in overload),
              denominator=len(overload))
    f5['by_horizon'] = {}
    for h in p['hours']:
        same_h = [r for r in overload if r['h_hours']==h]
        f5['by_horizon'][str(h)] = {name:ratio_verdict(
            sum(r[name+'_both_R_pct']<=.5 for r in same_h),len(same_h),.8,forecast=True)
            for name in NAMES[:3]}
    control = [dict(r,abs_GS_pct=abs(r['M0_G_S_pct'])) for r in rows if r['regime'] in p['control_regimes']
                and r['stratum']=='S' and r['h_hours']==6 and r['evaluable']]
    f6 = median_rule(control,'abs_GS_pct',.5,False)
    f6['physical_medians'] = {u:med([abs(r['M0_G_S_'+u]) for r in control]) for u in ('Mbit','ms')}
    unique = [r for r in stable if r['tau_s']==p['tau_seconds'][0]]
    share = float(np.mean([r['M0_fresh_tie_share'] for r in unique])) if unique else None
    harm = [r for r in stable if r['M0_G_S_Mbit_s']<0]
    retention = ratio_verdict(sum(r['M0_random_tie_G_S_Mbit_s']<0 for r in harm),len(harm),.5,forecast=True)
    f7 = dict(fresh_tie_share=share,fresh_record_horizons=len(unique),tie_threshold=.5,
              random_tie_harm_retention=retention,
              verdict='NOT_EVALUABLE' if share is None or not harm else
                      'HELD' if share>=.5 and retention['verdict']=='HELD' else 'NOT_HELD',by_horizon={})
    for h in p['hours']:
        uu = [r for r in unique if r['h_hours']==h]
        hh = [r for r in harm if r['h_hours']==h]
        f7['by_horizon'][str(h)] = dict(fresh_tie_share=float(np.mean([r['M0_fresh_tie_share'] for r in uu])) if uu else None,
            retention=ratio_verdict(sum(r['M0_random_tie_G_S_Mbit_s']<0 for r in hh),len(hh),.5,forecast=True))
    tie_shares = {}
    for name in NAMES:
        tie_shares[name] = {}
        for side in ('fresh','stale'):
            group = [r[name+'_'+side+'_tie_share'] for r in rows if side=='stale' or r['tau_s']==p['tau_seconds'][0]]
            tie_shares[name][side] = float(np.mean(group)) if group else None
    return dict(schema='v7-3-score-v1',owner='Doan Van Tai',cases=len(rows),usable_weekdays=len(inputs['dates']),
        exclusions=inputs['exclusions'],strata=strata,evaluable_cases=sum(r['evaluable'] for r in rows),
        non_evaluable_cases=sum(not r['evaluable'] for r in rows),tests=tests,
        forecasts=dict(F1=f1,F2=f2,F3=f3,F4=f4,F5=f5,F6=f6,F7=f7),
        descriptions={g+'_'+s:describe_again([r for r in rows if r['regime']==g and r['stratum']==s])
                       for g in p['regimes'] for s in ('S','O')},
        confirmatory_h6=describe_again(s6),tie_shares=tie_shares,
        sensitivity=dict(tie_variants=['M0_random_tie','M0_switch_tie'],stable_training_rate='Hybrid_S',
            h1=describe_again([r for r in rows if r['h_hours']==1]),
            overload=describe_again([r for r in rows if r['stratum']=='O']),
            DAY3_stable=describe_again([r for r in rows if r['regime']=='DAY3' and r['stratum']=='S']),
            T_int='per-action first-zero training estimator; censoring and h/T_int in cases.csv'),
        denominator_note='cases share days/instances; counts are denominators, not independent trials',
        physical_units=dict(cost='Mbit*s',rate='Mbit',service_delay='ms',capacity_Mbps=p['capacity_Mbps']),
        non_evaluable_reporting='percentages/ms null; Mbit physical metrics retained')


def compare(expected, actual, path='', mismatches=None):
    mismatches = [] if mismatches is None else mismatches
    if isinstance(expected,dict) and isinstance(actual,dict):
        if expected.keys()!=actual.keys():
            mismatches.append(path+': fields differ')
        for key in expected.keys() & actual.keys():
            compare(expected[key],actual[key],path+'/'+str(key),mismatches)
    elif isinstance(expected,list) and isinstance(actual,list):
        if len(expected)!=len(actual):
            mismatches.append(path+': lengths differ')
        for i,(x,y) in enumerate(zip(expected,actual)):
            compare(x,y,path+'/'+str(i),mismatches)
    elif isinstance(expected,bool) or isinstance(actual,bool):
        if type(expected)!=type(actual) or expected!=actual:
            mismatches.append(path+': boolean mismatch')
    elif isinstance(expected,(int,float)) and isinstance(actual,(int,float)):
        if not math.isclose(expected,actual,rel_tol=1e-12,abs_tol=0.):
            mismatches.append(path+': numeric mismatch '+repr(expected)+' != '+repr(actual))
    elif expected!=actual:
        mismatches.append(path+': value mismatch '+repr(expected)+' != '+repr(actual))
    return mismatches


def read_cell(value,prototype):
    if prototype is None:
        return None if value=='' else value
    if isinstance(prototype,bool):
        return {'True':True,'False':False}.get(value,value)
    if isinstance(prototype,(int,float)):
        try:
            return float(value)
        except ValueError:
            return value
    return value


def rescore(out=C.OUT):
    verified = C.verify_lock(out)
    out = Path(out)
    p = C.read_json(C.ROOT/C.PARAMS)
    inputs = C.read_json(out/'inputs.json')
    run = C.read_json(out/'run_summary.json')
    mismatches, rows = [], []
    try:
        if inputs['lock_sha256']!=verified.digest or run['status']!='COMPLETE':
            raise ValueError('different lock or incomplete run')
        manifest = C.read_json(C.ROOT/C.BASE/'data_manifest.json')
        planned = sorted(d for d in manifest['test_dates'] if datetime.fromisoformat(d).weekday()<5)
        removed = [r['date'] for r in inputs['exclusions']]
        if (inputs['requested_dates']!=planned or inputs['dates']!=sorted(set(inputs['dates'])) or
            len(removed)!=len(set(removed)) or any(d in removed for d in inputs['dates']) or
            set(removed+inputs['dates'])!=set(planned)):
            raise ValueError('input calendar differs from locked manifest/exclusions')
        required = {(g,d) for g in p['regimes'] for d in inputs['dates']}
        if (required!={(r['regime'],r['date']) for r in inputs['records']} or
            len(inputs['records'])!=len(required) or
            required!={(r['regime'],r['date']) for r in run['records']} or len(run['records'])!=len(required)):
            raise ValueError('incomplete/duplicate raw population')
        stems = {f'{g}_{d}' for g,d in required}
        for suffix in ('npz','json'):
            if {f.stem for f in (out/'records').glob('*.'+suffix)}!=stems:
                raise ValueError('unexpected/missing raw files')
        for label in inputs['records']:
            path = out/'records'/f'{label["regime"]}_{label["date"]}.npz'
            meta = C.read_json(path.with_suffix('.json'))
            if C.sha256(path)!=meta['npz_sha256'] or any(meta[k]!=label[k] for k in label):
                raise ValueError('raw record hash/label mismatch')
            with np.load(path,allow_pickle=False) as f:
                raw = {k:f[k] for k in f.files}
            if (raw['V'].shape!=(p['N_test'],2,4) or
                raw['paired_evaluation'].shape!=(p['N_test'],p['R_eval'],2,4) or
                raw['reference_decision_rollouts'].shape!=(p['N_test'],p['R_dec'],2,4)):
                raise ValueError('sample-count mismatch')
            rows.extend(recompute(raw,label,p))
        rows.sort(key=lambda r:(r['regime'],r['date'],r['tau_s'],r['h_hours']))
        compare(rebuild_summary(rows,inputs,p),C.read_json(out/'score/summary.json'),'summary',mismatches)
        with (out/'score/cases.csv').open(newline='') as f:
            saved = list(csv.DictReader(f))
        if len(saved)!=len(rows):
            mismatches.append('cases: row count differs')
        for i,(row,stored) in enumerate(zip(rows,saved)):
            converted = {k:read_cell(v,row.get(k)) for k,v in stored.items()}
            compare(row,converted,'cases/'+str(i),mismatches)
    except (ValueError,KeyError,IndexError,OSError) as exc:
        mismatches.append(str(exc))
    result = dict(status='MATCH' if not mismatches else 'MISMATCH',mismatches=sorted(mismatches),
                  cases_recomputed=len(rows),relative_tolerance=1e-12,absolute_tolerance=0.,
                  lock_sha256=verified.digest)
    C.write_json(out/'rescore.json',result)
    return result


if __name__=='__main__':
    result = rescore()
    print(result['status'])
    raise SystemExit(0 if result['status']=='MATCH' else 1)
