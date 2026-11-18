"""Doan Van Tai — deterministic V7-3 card scoring, from saved raw only."""
import argparse
from collections import Counter
import csv
from datetime import datetime
from pathlib import Path

import numpy as np

from experiments.letter import v7_3_day as A
from experiments.letter import v7_3_test_common as C

PIPES = ('M0', 'Hybrid', 'Stationary', 'M0_random_tie', 'M0_switch_tie', 'Hybrid_S')


def fraction_test(numerator, denominator, threshold, minimum=1, forecast=False):
    verdict = ('NOT_EVALUABLE' if denominator < minimum else
               ('HELD' if forecast else 'PASS') if numerator/denominator >= threshold else
               ('NOT_HELD' if forecast else 'FAIL'))
    return dict(numerator=int(numerator), denominator=int(denominator),
                fraction=float(numerator/denominator) if denominator else None,
                threshold=threshold, minimum=minimum, verdict=verdict)


def _same(actual, expected, name):
    if not np.array_equal(actual, expected):
        raise ValueError('raw identity mismatch: '+name)


def case_rows(raw, meta, params):
    """Instance-paired SE; cost ratios use the mean reference, never mean ratios."""
    for key,value in raw.items():
        if np.issubdtype(value.dtype,np.number) and not np.isfinite(value).all():
            raise ValueError('nonfinite raw array: '+key)
    stratum = 'S' if bool((raw['input_utilization']<1).all()) else 'O'
    if stratum!=meta['stratum']:
        raise ValueError('stratum differs from raw input utilization')
    v = raw['paired_evaluation'].mean(axis=1)
    ref_values = raw['reference_decision_rollouts'].mean(axis=1)
    reference = ref_values.argmin(axis=1)
    n, _, nh = v.shape
    hs, taus = raw['h_seconds'], raw['tau_seconds']
    _same(hs, np.array(params['hours'])*3600, 'horizons')
    _same(taus, params['tau_seconds'], 'ages')
    _same(raw['V'], v, 'V')
    _same(raw['reference_decision'], reference, 'reference_decision')
    _same(raw['reference_tie_flags'], ref_values[:,0]==ref_values[:,1], 'reference_ties')
    cref = v[np.arange(n)[:,None],reference,np.arange(nh)]
    _same(raw['C_ref'], cref, 'C_ref')
    m0 = np.stack([raw['M0_predicted_fresh'], *np.moveaxis(raw['M0_predicted_stale'],1,0)],axis=1)
    # axes: instance, unique side (fresh/stale300/stale900), action, h.
    decisions = [m0.argmin(axis=2)]
    corrected = m0.copy()
    corrected[:,:,1] += params['s_hat_pooled_Mbit'][meta['regime']]*hs
    decisions += [corrected.argmin(axis=2),
                  np.full((n,3,nh), int(params['s_hat_pooled_Mbit'][meta['regime']]<0))]
    tied = [m0[:,:,0]==m0[:,:,1], corrected[:,:,0]==corrected[:,:,1],
            np.full((n,3,nh),params['s_hat_pooled_Mbit'][meta['regime']]==0)]
    selected, switch = [], []
    for p in range(3):
        d = decisions[p]
        expected = np.stack([np.repeat(d[:,:1],2,axis=1),d[:,1:]],axis=1)
        flags = np.stack([np.repeat(tied[p][:,:1],2,axis=1),tied[p][:,1:]],axis=1)
        _same(raw['decisions'][:,p], expected, PIPES[p]+' decisions')
        _same(raw['tie_flags'][:,p], flags, PIPES[p]+' ties')
        cost = v[np.arange(n)[:,None,None],d,np.arange(nh)]
        selected.append(cost)
        switch.append(d.astype(float))
        stored = np.stack([np.repeat(cost[:,:1],2,axis=1),cost[:,1:]],axis=1)
        _same(raw['costs'][:,p],stored,PIPES[p]+' costs')
        _same(raw['regret'][:,p],stored-cref[:,None,None,:],PIPES[p]+' regret')
        _same(raw['G_S'][:,p],stored[:,1]-stored[:,0],PIPES[p]+' G_S')
    expected_random = np.where(tied[0],v.mean(axis=1)[:,None,:],selected[0])
    selected.append(expected_random)
    switch.append(np.where(tied[0],.5,decisions[0]))
    tied.append(tied[0])
    d_switch = np.where(tied[0],1,decisions[0])
    selected.append(v[np.arange(n)[:,None,None],d_switch,np.arange(nh)])
    switch.append(d_switch.astype(float))
    tied.append(tied[0])
    stable_cost = m0.copy()
    stable_cost[:,:,1] += params['s_hat_S_Mbit_sensitivity'][meta['regime']]*hs
    ds = stable_cost.argmin(axis=2)
    selected.append(v[np.arange(n)[:,None,None],ds,np.arange(nh)])
    switch.append(ds.astype(float))
    tied.append(stable_cost[:,:,0]==stable_cost[:,:,1])
    tint = [A.resolution(raw['backlog_trace'][:,a],params['dt_s']) for a in range(2)]
    rows = []
    for ti,tau in enumerate(taus):
        for hi,h in enumerate(hs):
            cr = float(cref[:,hi].mean())
            evaluable = bool(cr/h >= params['evaluable_threshold_Mbit'])
            row = dict(regime=meta['regime'],date=meta['date'],stratum=meta['stratum'],
                       tau_s=int(tau),h_hours=int(h/3600),N=n,evaluable=evaluable,
                       C_ref_Mbit_s=cr,C_ref_Mbit=cr/h,
                       C_ref_ms=1000*cr/h/params['capacity_Mbps'],
                       reference_tie_share=float(raw['reference_tie_flags'][:,hi].mean()))
            for a,action in enumerate(('Stay','Switch')):
                detail = tint[a]
                row['T_int_'+action+'_s'] = detail['T_int_s']
                row['T_int_'+action+'_censored'] = detail['censored']
                row['T_int_'+action+'_status'] = detail['status']
                row['h_over_T_int_'+action] = (float(h/detail['T_int_s'])
                    if detail['T_int_s'] is not None and detail['T_int_s']>0 else None)
            for p,name in enumerate(PIPES):
                pair = selected[p][:,[0,ti+1],hi]
                l = pair.mean(axis=0)
                excess = l-cr
                gs = float((pair[:,1]-pair[:,0]).mean())
                se = float((pair[:,1]-pair[:,0]).std(ddof=1)/np.sqrt(n)) if n>1 else None
                for side,suffix in enumerate(('fresh','stale')):
                    prefix = name+'_'+suffix
                    row[prefix+'_L_Mbit_s'] = float(l[side])
                    row[prefix+'_L_Mbit'] = float(l[side]/h)
                    row[prefix+'_L_ms'] = float(1000*l[side]/h/params['capacity_Mbps'])
                    row[prefix+'_R_Mbit_s'] = float(excess[side])
                    row[prefix+'_R_Mbit'] = float(excess[side]/h)
                    row[prefix+'_R_ms'] = float(1000*excess[side]/h/params['capacity_Mbps'])
                    row[prefix+'_R_pct'] = float(100*excess[side]/cr) if evaluable else None
                    si = 0 if side==0 else ti+1
                    row[prefix+'_F_switch'] = float(switch[p][:,si,hi].mean())
                    row[prefix+'_tie_share'] = float(tied[p][:,si,hi].mean())
                both = float(max(excess))
                for field,value in (('both_R',both),('G_S',gs),('se_G_S',se)):
                    row[name+'_'+field+'_Mbit_s'] = value
                    row[name+'_'+field+'_Mbit'] = value/h if value is not None else None
                    row[name+'_'+field+'_ms'] = (1000*value/h/params['capacity_Mbps']
                                               if value is not None else None)
                    row[name+'_'+field+'_pct'] = (100*value/cr
                        if evaluable and value is not None else None)
            for side,si in (('fresh',0),('stale',ti+1)):
                row['Hybrid_Stationary_'+side+'_agree_n'] = int(
                    (decisions[1][:,si,hi]==decisions[2][:,si,hi]).sum())
            df = row['M0_stale_F_switch']-row['M0_fresh_F_switch']
            prediction = int(np.sign(params['s_hat_pooled_Mbit'][meta['regime']]*df))
            resolved = bool(df!=0 and row['M0_se_G_S_Mbit_s'] is not None and
                            abs(row['M0_G_S_Mbit_s'])>2*row['M0_se_G_S_Mbit_s'])
            agree = bool(prediction==int(np.sign(row['M0_G_S_Mbit_s'])))
            population = (meta['regime'] in params['confirmatory_regimes'] and
                          meta['stratum']=='S' and row['h_hours'] in params['test_horizons_hours'])
            row.update(H1_predicted_sign=prediction,H1_resolved=resolved,H1_agrees=agree,
                       confirmatory_population=population)
            outside = 'OUTSIDE_POPULATION' if not population else 'NON_EVALUABLE' if not evaluable else None
            row['H1_clause'] = outside or ('F_EQUAL' if df==0 else 'GS_WITHIN_2SE' if not resolved else
                                           'RESOLVED_AGREE' if agree else 'RESOLVED_DISAGREE')
            row['H2_clause'] = outside or ('REGRET_LE_0.5' if row['Hybrid_both_R_pct']<=.5 else 'REGRET_GT_0.5')
            row['H3_clause'] = outside or ('M0_LE_0.5' if row['M0_both_R_pct']<=.5 else
                'HYBRID_LOWER' if row['Hybrid_both_R_pct']<row['M0_both_R_pct'] else 'HYBRID_NOT_LOWER')
            if not evaluable:
                # Card: non-evaluable costs are reported in Mbit only.
                for key in row:
                    if key.endswith('_ms'):
                        row[key] = None
            rows.append(row)
    return rows


def hypothesis(rows, name, params):
    eligible = [r for r in rows if r['confirmatory_population'] and r['evaluable']]
    if name=='H1':
        population = [r for r in eligible if r['H1_resolved']]
        numerator = sum(r['H1_agrees'] for r in population)
    elif name=='H2':
        population = eligible
        numerator = sum(r['Hybrid_both_R_pct']<=.5 for r in population)
    else:
        population = [r for r in eligible if r['M0_both_R_pct']>.5]
        numerator = sum(r['Hybrid_both_R_pct']<r['M0_both_R_pct'] for r in population)
    test = params['tests'][name]
    result = fraction_test(numerator,len(population),test['pass_share'],test['min_cases'])
    result.update(population_cases=len(eligible),clauses=dict(sorted(Counter(r[name+'_clause'] for r in rows).items())),
                  deciding_clause='minimum_cases' if len(population)<test['min_cases'] else 'pass_share')
    return result


def describe(rows):
    eligible = [r for r in rows if r['evaluable']]
    excluded = [r for r in rows if not r['evaluable']]
    def median(key):
        values = [r[key] for r in eligible if r[key] is not None]
        return float(np.median(values)) if values else None
    result = dict(cases=len(rows),evaluable=sum(r['evaluable'] for r in rows),
                  non_evaluable=sum(not r['evaluable'] for r in rows),pipelines={},
                  cost_summary_population='evaluable cases; non-evaluable physical values reported separately',
                  non_evaluable_Mbit={})
    for p in PIPES:
        values = {field:median(p+'_'+field) for field in
                  ('both_R_pct','both_R_Mbit','both_R_ms','G_S_pct','G_S_Mbit','G_S_ms')}
        harm = [r for r in eligible if r[p+'_G_S_Mbit_s']<0]
        values['harm_cases'] = len(harm)
        values['harm_share'] = len(harm)/len(eligible) if eligible else None
        values['harm_size_median'] = {
            unit:float(np.median([-r[p+'_G_S_'+unit] for r in harm if r[p+'_G_S_'+unit] is not None]))
            if any(r[p+'_G_S_'+unit] is not None for r in harm) else None for unit in ('pct','Mbit','ms')}
        values['tie_share_fresh'] = float(np.median([r[p+'_fresh_tie_share'] for r in rows])) if rows else None
        values['tie_share_stale'] = float(np.median([r[p+'_stale_tie_share'] for r in rows])) if rows else None
        result['pipelines'][p] = values
        result['non_evaluable_Mbit'][p] = dict(
            both_R_median_Mbit=float(np.median([r[p+'_both_R_Mbit'] for r in excluded])) if excluded else None,
            G_S_median_Mbit=float(np.median([r[p+'_G_S_Mbit'] for r in excluded])) if excluded else None,
            harm_cases=sum(r[p+'_G_S_Mbit']<0 for r in excluded))
    return result


def summarize(rows, inputs, params):
    rows = sorted(rows,key=lambda r:(r['regime'],r['date'],r['tau_s'],r['h_hours']))
    records = inputs['records']
    strata = {s:dict(records=sum(r['stratum']==s for r in records),
                     cases=sum(r['stratum']==s for r in rows),
                     evaluable=sum(r['stratum']==s and r['evaluable'] for r in rows)) for s in ('S','O')}
    tests = {}
    for name in ('H1','H2','H3'):
        tests[name] = hypothesis(rows,name,params)
        tests[name]['by_horizon'] = {str(h):hypothesis([r for r in rows if r['h_hours']==h],name,params)
                                     for h in params['test_horizons_hours']}
    stable = [r for r in rows if r['regime'] in params['confirmatory_regimes'] and r['stratum']=='S']
    s6 = [r for r in stable if r['h_hours']==6 and r['evaluable']]
    stable_dates = [d for d in inputs['dates'] if all(
        r['stratum']=='S' for r in records if r['date']==d)]
    f1 = fraction_test(len(stable_dates),len(inputs['dates']),.6,forecast=True)
    f1['definition'] = 'weekday S for every declared regime; per-regime counts also reported'
    f1['by_regime'] = {g:fraction_test(sum(r['regime']==g and r['stratum']=='S' for r in records),
                         sum(r['regime']==g for r in records),.6,forecast=True) for g in params['regimes']}
    f2 = fraction_test(sum(r['M0_G_S_Mbit_s']<0 and r['H1_resolved'] for r in s6),len(s6),.6,forecast=True)
    def median_forecast(pop,key,threshold,lower):
        values = [r[key] for r in pop if r[key] is not None]
        value = float(np.median(values)) if values else None
        return dict(value=value,denominator=len(values),threshold=threshold,
                    verdict='NOT_EVALUABLE' if value is None else 'HELD' if
                    (value>=threshold if lower else value<=threshold) else 'NOT_HELD')
    f3 = median_forecast(s6,'M0_both_R_pct',5,True)
    f3['physical_medians'] = describe(s6)['pipelines']['M0']
    agreement = [r for r in rows if r['h_hours']>=2]
    ag_n = sum(r['Hybrid_Stationary_stale_agree_n']+
               (r['Hybrid_Stationary_fresh_agree_n'] if r['tau_s']==params['tau_seconds'][0] else 0)
               for r in agreement)
    ag_d = sum(r['N']*(2 if r['tau_s']==params['tau_seconds'][0] else 1) for r in agreement)
    f4 = fraction_test(ag_n,ag_d,.99,forecast=True)
    f4['population'] = 'all regimes/strata, h>=2h, unique fresh/stale300/stale900 decisions'
    f4['by_horizon'] = {}
    for h in params['test_horizons_hours']:
        group = [r for r in agreement if r['h_hours']==h]
        num = sum(r['Hybrid_Stationary_stale_agree_n']+
                  (r['Hybrid_Stationary_fresh_agree_n'] if r['tau_s']==params['tau_seconds'][0] else 0)
                  for r in group)
        den = sum(r['N']*(2 if r['tau_s']==params['tau_seconds'][0] else 1) for r in group)
        f4['by_horizon'][str(h)] = fraction_test(num,den,.99,forecast=True)
    overload = [r for r in rows if r['stratum']=='O' and r['evaluable']]
    f5_by_pipeline = {p:fraction_test(sum(r[p+'_both_R_pct']<=.5 for r in overload),
                          len(overload),.8,forecast=True) for p in PIPES[:3]}
    f5 = dict(by_pipeline=f5_by_pipeline,
              verdict='NOT_EVALUABLE' if not overload else 'HELD' if all(
                  x['verdict']=='HELD' for x in f5_by_pipeline.values()) else 'NOT_HELD',
              deciding_clause='each_pipeline_share',
              joint_numerator=sum(all(r[p+'_both_R_pct']<=.5 for p in PIPES[:3]) for r in overload),
              denominator=len(overload))
    f5['by_horizon'] = {str(h):{p:fraction_test(
        sum(r[p+'_both_R_pct']<=.5 for r in overload if r['h_hours']==h),
        sum(r['h_hours']==h for r in overload),.8,forecast=True) for p in PIPES[:3]}
        for h in params['hours']}
    control6 = [dict(r,abs_GS_pct=abs(r['M0_G_S_pct'])) for r in rows
                if r['regime'] in params['control_regimes'] and r['stratum']=='S' and
                r['h_hours']==6 and r['evaluable']]
    f6 = median_forecast(control6,'abs_GS_pct',.5,False)
    f6['physical_medians'] = {unit:float(np.median([abs(r['M0_G_S_'+unit]) for r in control6]))
                             if control6 else None for unit in ('Mbit','ms')}
    # F7 has no horizon restriction in the card: all horizons, and also split below.
    fresh_unique = [r for r in stable if r['tau_s']==params['tau_seconds'][0]]
    share = float(np.mean([r['M0_fresh_tie_share'] for r in fresh_unique])) if fresh_unique else None
    negative = [r for r in stable if r['M0_G_S_Mbit_s']<0]
    retention = fraction_test(sum(r['M0_random_tie_G_S_Mbit_s']<0 for r in negative),len(negative),.5,forecast=True)
    f7 = dict(fresh_tie_share=share,fresh_record_horizons=len(fresh_unique),
              tie_threshold=.5,random_tie_harm_retention=retention,
              verdict='NOT_EVALUABLE' if share is None or not negative else
                      'HELD' if share>=.5 and retention['verdict']=='HELD' else 'NOT_HELD',
              by_horizon={str(h):dict(
                  fresh_tie_share=float(np.mean([r['M0_fresh_tie_share'] for r in fresh_unique if r['h_hours']==h]))
                    if any(r['h_hours']==h for r in fresh_unique) else None,
                  retention=fraction_test(sum(r['M0_random_tie_G_S_Mbit_s']<0 for r in negative if r['h_hours']==h),
                    sum(r['h_hours']==h for r in negative),.5,forecast=True)) for h in params['hours']})
    descriptions = {g+'_'+s:describe([r for r in rows if r['regime']==g and r['stratum']==s])
                    for g in params['regimes'] for s in ('S','O')}
    # Save all tie shares by side (means, fresh counted only once per record/h).
    ties = {p:{side:float(np.mean([r[p+'_'+side+'_tie_share'] for r in rows
                      if side=='stale' or r['tau_s']==params['tau_seconds'][0]])) if rows else None
               for side in ('fresh','stale')} for p in PIPES}
    return dict(schema='v7-3-score-v1',owner='Doan Van Tai',cases=len(rows),
        usable_weekdays=len(inputs['dates']),exclusions=inputs['exclusions'],strata=strata,
        evaluable_cases=sum(r['evaluable'] for r in rows),
        non_evaluable_cases=sum(not r['evaluable'] for r in rows),tests=tests,
        forecasts=dict(F1=f1,F2=f2,F3=f3,F4=f4,F5=f5,F6=f6,F7=f7),
        descriptions=descriptions,confirmatory_h6=describe(s6),tie_shares=ties,
        sensitivity=dict(tie_variants=['M0_random_tie','M0_switch_tie'],
                         stable_training_rate='Hybrid_S',h1=describe([r for r in rows if r['h_hours']==1]),
                         overload=describe([r for r in rows if r['stratum']=='O']),
                         DAY3_stable=describe([r for r in rows if r['regime']=='DAY3' and r['stratum']=='S']),
                         T_int='per-action first-zero training estimator; censoring and h/T_int in cases.csv'),
        denominator_note='cases share days/instances; counts are denominators, not independent trials',
        physical_units=dict(cost='Mbit*s',rate='Mbit',service_delay='ms',capacity_Mbps=params['capacity_Mbps']),
        non_evaluable_reporting='percentages/ms null; Mbit physical metrics retained')


def read_records(out, inputs, params):
    run = C.read_json(out/'run_summary.json')
    if run['status']!='COMPLETE':
        raise ValueError('INCOMPLETE one-shot run cannot receive confirmatory verdicts')
    manifest = C.read_json(C.ROOT/C.BASE/'data_manifest.json')
    scheduled = sorted(d for d in manifest['test_dates'] if datetime.fromisoformat(d).weekday()<5)
    excluded = [r['date'] for r in inputs['exclusions']]
    if (inputs['requested_dates']!=scheduled or inputs['dates']!=sorted(set(inputs['dates'])) or
        len(excluded)!=len(set(excluded)) or set(inputs['dates']) & set(excluded) or
        set(inputs['dates']) | set(excluded) != set(scheduled)):
        raise ValueError('input calendar differs from locked manifest/exclusions')
    expected = {(r['regime'],r['date']) for r in inputs['records']}
    if (expected != {(g,d) for g in params['regimes'] for d in inputs['dates']} or
        len(inputs['records'])!=len(expected)):
        raise ValueError('input population differs from locked regimes/calendar')
    actual = {(r['regime'],r['date']) for r in run['records']}
    if actual!=expected or len(run['records'])!=len(expected):
        raise ValueError('missing or duplicate records')
    stems = {f'{g}_{d}' for g,d in expected}
    if {p.stem for p in (out/'records').glob('*.npz')}!=stems or {p.stem for p in (out/'records').glob('*.json')}!=stems:
        raise ValueError('unexpected or missing raw files')
    rows = []
    for label in sorted(inputs['records'],key=lambda r:(r['regime'],r['date'])):
        path = out/'records'/f'{label["regime"]}_{label["date"]}.npz'
        meta = C.read_json(path.with_suffix('.json'))
        if C.sha256(path)!=meta['npz_sha256'] or any(meta[k]!=label[k] for k in label):
            raise ValueError('record integrity/stratum mismatch')
        with np.load(path,allow_pickle=False) as f:
            raw = {k:f[k] for k in f.files}
        if (raw['V'].shape!=(params['N_test'],2,4) or
            raw['paired_evaluation'].shape!=(params['N_test'],params['R_eval'],2,4) or
            raw['reference_decision_rollouts'].shape!=(params['N_test'],params['R_dec'],2,4)):
            raise ValueError('record sample counts differ from card')
        rows.extend(case_rows(raw,meta,params))
    return rows


def score(out=C.OUT):
    verified = C.verify_lock(out)  # Before opening raw or inputs.
    out = Path(out)
    params = C.read_json(C.ROOT/C.PARAMS)
    inputs = C.read_json(out/'inputs.json')
    if inputs['lock_sha256']!=verified.digest:
        raise ValueError('inputs were generated under a different lock')
    rows = read_records(out,inputs,params)
    rows.sort(key=lambda r:(r['regime'],r['date'],r['tau_s'],r['h_hours']))
    summary = summarize(rows,inputs,params)
    def write_csv(path):
        with path.open('x',newline='') as f:
            writer = csv.DictWriter(f,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    C.atomic_write(out/'score/cases.csv',write_csv)
    C.write_json(out/'score/summary.json',summary)
    return summary


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    score()
