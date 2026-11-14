"""Doan Van Tai — post-hoc descriptive audit, no confirmatory claims or reruns."""
import csv
import json
import statistics as S
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent


def read(p): return json.loads((ROOT/p).read_text())


def main():
    with (OUT/'recomputed_rows.csv').open() as f:
        rows=list(csv.DictReader(f))
    data=[]
    for r in rows:
        if r['experiment'] not in ('ev_d','ev_d2','ev_d3','ev_d3b'):
            continue
        d={k:(float(v) if k in ('G','se','pred','tau','T_int','tau_T','s_train','h','E_stay',
                                'mean_stay','Fdiff_test','Fdiff_train','beta_A','beta_B') and v else v)
           for k,v in r.items()}
        d['h_mult']=int(d['h_mult'])
        data.append(d)
    summaries=[]
    for exp in ('ev_d','ev_d2','ev_d3','ev_d3b'):
        a=[r for r in data if r['experiment']==exp and r['h_mult']==30]
        for tau in sorted({r['tau'] for r in a}):
            for twin in ('fluid','ratefluid','fluid_nowcast','ratefluid_nowcast','ratefluid_nowcast_hybrid_train'):
                b=[r for r in a if r['tau']==tau and r['twin']==twin]
                summaries.append(dict(experiment=exp,tau=tau,twin=twin,n=len(b),
                    median_Tint=S.median(r['T_int'] for r in b),median_tau_T=S.median(r['tau_T'] for r in b),
                    median_G=S.median(r['G'] for r in b),min_G=min(r['G'] for r in b),max_G=max(r['G'] for r in b),
                    harm_point=sum(r['G']<=-.25 for r in b),
                    harm_exceeds_2se=sum(r['G']< -max(.25,2*r['se']) for r in b)))
    diagnostics=[]
    for r in data:
        if not r['pred'] or r['twin'] not in ('fluid_nowcast','ratefluid_nowcast'):
            continue
        # Test action shares only: uses test information, deliberately post-hoc.
        # This is diagnostic accounting, not a competing preregistered predictor.
        ptest=100*r['h']*r['s_train']*r['Fdiff_test']/r['E_stay']
        d=dict(experiment=r['experiment'],id=r['id'],twin=r['twin'],tau=r['tau'],h_mult=r['h_mult'],
               G=r['G'],pred_locked=r['pred'],pred_test_share=ptest,
               error_locked=abs(r['G']-r['pred']),error_test_share=abs(r['G']-ptest),
               share_shift=abs(r['Fdiff_test']-r['Fdiff_train']),
               pred_dimensionless_train=100*r['s_train']/r['mean_stay']*r['Fdiff_train'],
               tau_T=r['tau_T'],se=r['se'])
        diagnostics.append(d)
    diag_groups=[]
    for exp in ('ev_d','ev_d2','ev_d3','ev_d3b'):
        for m in (10,30):
            a=[r for r in diagnostics if r['experiment']==exp and r['h_mult']==m]
            sig=[r for r in a if abs(r['pred_locked'])>=.25]
            diag_groups.append(dict(experiment=exp,h_mult=m,n=len(a),significant_n=len(sig),
               median_abs_error_locked=S.median(r['error_locked'] for r in a),
               median_abs_error_test_share=S.median(r['error_test_share'] for r in a),
               closer_using_test_shares=sum(r['error_test_share']<r['error_locked'] for r in a),
               original_tolerance_hits_locked=sum(r['error_locked']<=max(.15,.3*abs(r['pred_locked']))+2*r['se'] for r in a),
               original_tolerance_hits_test_share=sum(r['error_test_share']<=max(.15,.3*abs(r['pred_locked']))+2*r['se'] for r in a),
               relative_error_den_pred_median=S.median(r['error_locked']/abs(r['pred_locked']) for r in sig) if sig else None,
               relative_error_den_pred_max=max((r['error_locked']/abs(r['pred_locked']) for r in sig),default=None),
               share_shift_vs_abs_error_spearman=float(spearmanr([r['share_shift'] for r in a],[r['error_locked'] for r in a]).statistic)))
    pairs=[]
    for exp in ('ev_d3','ev_d3b'):
        for twin in ('fluid_nowcast','ratefluid_nowcast','fluid','ratefluid','ratefluid_nowcast_hybrid_train'):
            a={r['id'].rsplit('_tau',1)[0]:r for r in data if r['experiment']==exp and r['tau']==30 and r['twin']==twin and r['h_mult']==30}
            b={r['id'].rsplit('_tau',1)[0]:r for r in data if r['experiment']==exp and r['tau']==300 and r['twin']==twin and r['h_mult']==30}
            delta=[b[k]['G']-v['G'] for k,v in a.items()]
            pairs.append(dict(experiment=exp,twin=twin,n=len(delta),more_negative=sum(v<0 for v in delta),
                              median_delta=S.median(delta),min_delta=min(delta),max_delta=max(delta)))
    slope=[]
    for r in read('results/ext_validity/ev_d3/diag_s_long.json'):
        h=[d for d in data if d['experiment']=='ev_d3' and d['id']==r['id'] and d['twin']=='ratefluid_nowcast_hybrid_train']
        slope.append(dict(r,relative_error=abs(r['s_train']-r['s_long'])/abs(r['s_long']),
                          diagnostic_z=(r['s_train']-r['s_long'])/r['s_long_se'],
                          hybrid_h10=h[0]['G'] if h[0]['h_mult']==10 else h[1]['G'],
                          hybrid_h30=h[0]['G'] if h[0]['h_mult']==30 else h[1]['G']))
    features=[]
    for exp in ('ev_d','ev_d3','ev_d3b'):
        a=[r for r in data if r['experiment']==exp and r['h_mult']==30
           and r['twin']=='fluid_nowcast' and abs(r['pred'])>=.25]
        rel=[abs(r['G']-r['pred'])/abs(r['pred']) for r in a]
        absolute=[abs(r['G']-r['pred']) for r in a]
        fdict=dict(tau_T=[r['tau_T'] for r in a],
                   abs_s_over_mean=[abs(r['s_train'])/r['mean_stay'] for r in a],
                   max_load=[(max(float(r['lamA']),float(r['lamB']))+float(r['u']))/10 for r in a],
                   share_shift=[abs(r['Fdiff_test']-r['Fdiff_train']) for r in a],
                   beta_A=[r['beta_A'] for r in a])
        for k,f in fdict.items():
            features.append(dict(experiment=exp,n=len(a),feature=k,
                                 spearman_relative_error=float(spearmanr(f,rel).statistic),
                                 spearman_absolute_error=float(spearmanr(f,absolute).statistic)))
    hybrid_features=[]
    for exp in ('ev_d3','ev_d3b'):
        a=[r for r in data if r['experiment']==exp and r['h_mult']==30 and r['tau']==300
           and r['twin']=='ratefluid_nowcast_hybrid_train']
        for failure in (False,True):
            b=[r for r in a if (r['G'] < -max(.1,2*r['se']))==failure]
            hybrid_features.append(dict(experiment=exp,D4_row_failure=failure,n=len(b),
               median_abs_s_over_mean=S.median(abs(r['s_train'])/r['mean_stay'] for r in b),
               median_abs_s=S.median(abs(r['s_train']) for r in b)))
    # Direct source-series evidence; no web or raw packet download.
    traces=[]
    for exp,name in [('ev_d2','20250311'),('ev_d3b','20260414')]:
        p=ROOT/f'results/ext_validity/{exp}/series_{name}.bin'
        c=np.fromfile(p,dtype='<i4').reshape(-1,3)
        meta=read(f'results/ext_validity/{exp}/series_{name}.json')
        x=c[:,1].astype(float)
        z=x-x.mean()
        # Circular ACF is exact for the periodically repeated intensity.
        circ=np.fft.irfft(abs(np.fft.rfft(z))**2,n=len(z))/np.dot(z,z)
        minute=x[:15*6000].reshape(15,6000).mean(1)/x.mean()
        bin1=x[:len(x)//100*100].reshape(-1,100).sum(1)
        archive_path=ROOT/('results/ext_validity/ev_d2/series_c1.npz' if exp=='ev_d2' else 'results/ext_validity/ev_d3b/series_20260414.npz')
        with np.load(archive_path) as archive:
            equality=all(np.array_equal(archive[key],c[:,i]) for i,key in enumerate(('all','s0','s1')))
        traces.append(dict(trace=name,bins=len(c),period_seconds=len(c)*.01,packets=int(c[:,0].sum()),
                           metadata_packets=meta['packets'],binary_npz_exact=equality,
                           parse_error_pct=100*meta['parse_errors']/meta['packets'],
                           cov_10ms=float(x.std()/x.mean()),cov_1s=float(bin1.std()/bin1.mean()),
                           minute_ratio_min=float(minute.min()),minute_ratio_max=float(minute.max()),
                           circular_acf_at_period=1.,circular_acf_300s=float(circ[30000]),
                           s0_packets=int(x.sum()),selected_packet_fraction=float(x.sum()/c[:,0].sum())))
    a=[r for r in rows if r['experiment']=='ev_a']
    a_groups=[]
    for dm,hm in sorted({(r['dm'],r['hm']) for r in a}):
        for strat in ('neg','band','pos'):
            b=[r for r in a if r['dm']==dm and r['hm']==hm and r['stratum']==strat]
            a_groups.append(dict(dm=dm,hm=hm,stratum=strat,n=len(b),median_G=S.median(float(r['G']) for r in b),
                                 sign_match=sum((float(r['G'])>0)==(float(r['pred'])>0) for r in b)))
    e=[]
    for r in csv.DictReader((ROOT/'results/ext_validity/ev_e_twin_classes.csv').open()):
        if r['h_mult']=='10': e.append(r)
    e_groups=[]
    for strata in ('all','negpos'):
        b=[r for r in e if strata=='all' or r['stratum']!='band']
        for t in ('M0','margin','hybrid','hybrid_mm1','ko','static'):
            e_groups.append(dict(strata=strata,twin=t,n=len(b),harm=sum(float(r['G_S_'+t])<=-.25 for r in b),
                                 median_regret=S.median(float(r['regret_new_'+t]) for r in b),
                                 max_regret=max(float(r['regret_new_'+t]) for r in b)))
    result=dict(post_hoc=True,units='G and errors in percentage points of E_stay; closed loop in % J11',
                dose_response=summaries,paired_age=pairs,prediction_diagnostics=diag_groups,slope_diagnostic=slope,
                trace_facts=traces,closed_loop_groups=a_groups,EV_E=e_groups,
                exploratory_feature_correlations=features,hybrid_features=hybrid_features)
    (OUT/'exploratory.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    with (OUT/'prediction_diagnostics.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(diagnostics[0]));w.writeheader();w.writerows(diagnostics)
    print(json.dumps(dict(paired_age=pairs,prediction_diagnostics=diag_groups,trace_facts=traces),indent=2))


if __name__=='__main__': main()
