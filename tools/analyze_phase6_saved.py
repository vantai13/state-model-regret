"""Doan Van Tai — post-hoc diagnosis from immutable Phase6 rows and saved caches.

Never evaluates a regime or constructs future-cost profiles. Cache-only replay
uses the existing response surfaces at the already-run (640,4) resolution.
"""
import argparse
from contextlib import ExitStack
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import statistics
from unittest.mock import patch

import numpy as np

from experiments.P6_band import run as R
from experiments.P6_band import probe as B
from experiments.R3R_08_population_numerics import law_cache, profiles, quadrature, population
from experiments.R3R_08_population_numerics import piecewise as P
from experiments.R3R_10_interval_evaluation.evaluator import NativePosteriorFastLaw
from experiments.R3R_08_population_numerics.native_law import NativeLaw
from smr.cells import lattice

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path.home()/'.cache/state-model-regret/phase6/panel'
OUT = ROOT/'results/phase6/analysis_l6_4'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def u_category(label, ready):
    return 'NOT_READY' if not ready else 'READY_DEADBAND' if label == 'U' else 'LABELLED'


def signed_components(alpha, old, new, predicted_z, predictor_cref, actual_cref):
    """An exact arithmetic decomposition of the represented contributions."""
    gs = old['loss']-new['loss']
    constant = alpha*(old['share']-new['share'])
    pred_abs = predicted_z*predictor_cref/100
    return dict(constant_stake_native_pp=100*constant/actual_cref,
                weighted_gap_correction_pp=100*(gs-constant)/actual_cref,
                action_representation_correction_pp=100*(constant-pred_abs)/actual_cref,
                normalizer_correction_pp=100*pred_abs/actual_cref-predicted_z)


class SavedCache:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.laws = {}
        self.provenance = {}

    def remember(self, path):
        self.provenance[str(path)] = sha(path)

    def side(self, row, which):
        a,b,k,e,h,c = map(F,row['parameters']);u=2*e;ref=row['ref'];K=row['K']
        lam,pre,post = (a,u,F(0)) if which=='A' else (b,F(0),u)
        unit,increments = lattice((lam-6,lam+6),pre,F(1,120*ref))
        component=row['source_components'][which]
        key=component['law_key'];path=self.directory/'stationary'/(key+'.json')
        if key not in self.laws:
            data=json.loads(path.read_text());self.remember(path)
            assert sha(path)==path.with_suffix('.sha256').read_text().strip()
            assert data['source_fingerprint']==law_cache.fingerprint()
            assert list(increments)==data['increments']
            assert F(data['parameters'][0])+F(data['parameters'][1])==lam+pre
            native=law_cache.restore(data,data['parameters'],data['source_fingerprint'])
            self.laws[key]=NativePosteriorFastLaw(native)
        law=self.laws[key]
        key=component['profile_key'];meta=self.directory/'profiles'/(key+'.json')
        data_path=meta.with_suffix('.npz');record=json.loads(meta.read_text())
        self.remember(meta);self.remember(data_path)
        assert sha(data_path)==record['sha256']
        sources=(profiles.__file__,P.__file__,str(Path(P.__file__).with_name('native')/'piecewise.cpp'),
                 str(ROOT/'src/smr/stationary.py'))
        fingerprint=hashlib.sha256(''.join(sha(p) for p in sources).encode()).hexdigest()
        assert record['source']==fingerprint
        budget=min(F(1,10000),h*h/F(10_000_000))
        assert record['parameters']==[str(v) for v in (lam,pre,post,k,h,unit,budget)]+[ref]
        assert hashlib.sha256(json.dumps([record['parameters'],record['source']]).encode()).hexdigest()==key
        with np.load(data_path,allow_pickle=False) as arrays:
            saved={name:dict(modes=[(arrays[name+f'_x{m}'].copy(),arrays[name+f'_y{m}'].copy())
                                    for m in (0,1)],error=P.LD(item['error']))
                   for name,item in record['profiles'].items()}
        data=dict(record,profiles=saved)
        def cap(names):
            return max((int(saved[n]['modes'][m][0][-1])+record['factor']-1)//record['factor']
                       for n in names for m in (0,1))
        state=quadrature.build(law,K,cap(('d','dh')))
        old_grid=quadrature.build(law,K,cap(('old_d','old_h')))
        current={}
        for name,field in (('d','d'),('dh','h')):
            result=[profiles.values(data,name,state['indices'],m) for m in (0,1)]
            current[field]=np.column_stack([v[0] for v in result]).ravel()
            if field=='h':
                current['zero']=np.column_stack([v[2] for v in result]).ravel()
                current['sat']=np.column_stack([v[3] for v in result]).ravel()
        current['w']=state['mass'].ravel()
        q=old_grid['indices'];valid=q>=0;prior=np.zeros(len(q),dtype=P.LD)
        prior[valid]=law.posterior(q[valid])[0]
        old=dict(w=old_grid['mass'].sum(axis=1,dtype=P.LD),sat=np.zeros(len(q),dtype=bool))
        for name,field in (('old_d','d'),('old_h','h')):
            off,_,zo,_=profiles.values(data,name,q,0);on,_,zn,_=profiles.values(data,name,q,1)
            zero=zo&zn;value=(1-prior)*off+prior*on;value[zero]=0
            old[field]=value
            if field=='h':old['zero']=zero
        return dict(current=current,old=old,mean=law.mean*P.number(unit))


def aggregate(A, Bside, cost):
    """Statistics of already-stored response values, not an evaluator call."""
    totals={k:P.LD(0) for k in ('share','loss','oracle_share','oracle_loss','mean_gap','abs_gap')}
    for start in range(0,len(A['w']),128):
        sl=slice(start,start+128)
        w=A['w'][sl,None]*Bside['w'][None,:]
        d=A['d'][sl,None]+Bside['d'][None,:]+P.number(cost)
        h=A['h'][sl,None]+Bside['h'][None,:]+P.number(cost)
        cert=((A['zero'][sl,None]&Bside['zero'][None,:])|
              (A['sat'][sl,None]&Bside['sat'][None,:]))
        h=np.where(cert,P.number(cost),h);switch=h<0
        for key,value in (('share',switch),('loss',np.where(switch,d,0)),
                          ('oracle_share',d<0),('oracle_loss',np.minimum(d,0)),
                          ('mean_gap',d),('abs_gap',abs(d))):
            totals[key]+=(w*value).sum(dtype=P.LD)
    return {k:float(v) for k,v in totals.items()}


def diagnostics(root=ROOT, cache_dir=CACHE):
    root=Path(root);R.gate_record(root)
    saved=json.loads((root/R.SUMMARY).read_text());members=R.load_predictions(root)
    scan={r['id']:r for r in csv.DictReader((root/B.S.SOURCE).open())}
    cache=SavedCache(cache_dir);rows_out=[]
    def forbidden(*args,**kwargs):raise AssertionError('NEW_EVALUATION_FORBIDDEN')
    with ExitStack() as stack:
        for obj,name in ((population,'evaluate'),(population,'side'),(population,'pair_loss'),
                         (profiles,'get'),(law_cache,'get'),(P,'idle'),(P,'mean_idle'),(P,'age')):
            stack.enter_context(patch.object(obj,name,forbidden))
        stack.enter_context(patch.object(NativeLaw,'__init__',forbidden))
        for m in members:
            levels={lv:json.loads((root/R.PANEL_OUT/m['id']/f'level_{lv[0]}_{lv[1]}.json').read_text())
                    for lv in R.LEVELS}
            raw=levels[R.MAIN];point=saved['points'][m['id']];old=scan[m['scan_id']]
            A,Bside=cache.side(raw,'A'),cache.side(raw,'B')
            c=F(raw['parameters'][-1]);h=F(raw['parameters'][4])
            current=aggregate(A['current'],Bside['current'],c)
            aged=aggregate(A['old'],Bside['old'],c)
            base=float(P.number(h)*(A['mean']+Bside['mean']))
            reconstructed={'00':base+aged['loss'],'10':base+current['loss'],
                           '01':base+aged['oracle_loss'],'11':base+current['oracle_loss']}
            replay_error=max(abs(reconstructed[k]-float(F(raw['losses'][k]))) for k in reconstructed)
            assert replay_error<=1e-10*max(1,abs(base)),(m['id'],replay_error)
            cf=float(F(raw['Cref']));gs=float(F(raw['G_S']));alpha=float(old['stake'])
            pieces=signed_components(alpha,aged,current,m['z_H1_K640'],float(old['Cref_H1']),cf)
            residual=point['z_pct']-m['z_H1_K640']-sum(pieces[k] for k in (
                'weighted_gap_correction_pp','action_representation_correction_pp','normalizer_correction_pp'))
            assert abs(residual)<1e-9,(m['id'],residual)
            deltas={axis:float(100*max(abs(F(raw['G_S'])-F(levels[lv]['G_S']))/F(raw['Cref']),
                        abs(F(raw['G_S'])/F(raw['Cref'])-F(levels[lv]['G_S'])/F(levels[lv]['Cref']))))
                    for lv,axis in (((320,4),'K'),((640,2),'dt'))}
            result=dict(id=m['id'],scan_id=m['scan_id'],role=m['role'],base_id=m['base_id'],
                h=m['parameters'][4],kappa=m['parameters'][2],c=m['parameters'][5],
                label=point['label'],ready=point['ready'],category=u_category(point['label'],point['ready']),
                reasons=';'.join(point['reasons']),predicted_z_pct=m['z_H1_K640'],actual_z_pct=point['z_pct'],
                d_pp=point['d_pp'],R1_K_pp=deltas['K'],R1_dt_pp=deltas['dt'],
                **{f'width_{lv[0]}_{lv[1]}_pp':float(100*F(levels[lv]['normalized_error']['G_S'])) for lv in R.LEVELS},
                **{f'z_{lv[0]}_{lv[1]}_pct':float(100*F(levels[lv]['G_S'])/F(levels[lv]['Cref'])) for lv in R.LEVELS},
                G_S=gs,Cref=cf,Cref_H1=float(old['Cref_H1']),stationary_stake=alpha,
                actual_mean_gap=current['mean_gap'],oracle_switch_share=current['oracle_share'],
                oracle_gain_vs_stay=-current['oracle_loss'],native_stay_cost=base,
                old_M0_switch_share=aged['share'],new_M0_switch_share=current['share'],
                old_weighted_switch_cost=aged['loss'],new_weighted_switch_cost=current['loss'],
                replay_max_loss_error=replay_error,decomposition_residual_pp=residual,**pieces)
            rows_out.append(result)
            print(m['scan_id'],'SAVED_CACHE_POSTPROCESS_OK',flush=True)
    D=[r for r in rows_out if r['role']=='D'];twins=[r for r in rows_out if r['role']=='twin']
    ratio=[abs(r['actual_z_pct']/r['predicted_z_pct']) for r in D]
    summary=dict(analysis='POST_HOC_SAVED_DATA_ONLY',primary_verdict=saved['verdict'],
        D_counts=saved['D_counts'],D_ready=sum(r['ready'] for r in D),D_U_not_ready=sum(
            r['label']=='U' and not r['ready'] for r in D),D_U_ready_deadband=sum(
            r['label']=='U' and r['ready'] for r in D),D_positive_ids=[r['scan_id'] for r in D if r['label']=='+'],
        D_main_raw_positive_count=sum(r['actual_z_pct']>0 for r in D),
        twin_not_ready_ids=[r['scan_id'] for r in twins if not r['ready']],
        abs_truth_prediction_ratio_mean=statistics.mean(ratio),abs_truth_prediction_ratio_median=statistics.median(ratio),
        max_D_R1_pp=max(max(r['R1_K_pp'],r['R1_dt_pp']) for r in D),
        max_D_width_pp=max(r[f'width_{lv[0]}_{lv[1]}_pp'] for r in D for lv in R.LEVELS),
        max_replay_loss_error=max(r['replay_max_loss_error'] for r in rows_out),
        max_decomposition_residual_pp=max(abs(r['decomposition_residual_pp']) for r in rows_out),
        cache_files_sha256=cache.provenance,new_evaluator_calls=0,new_profiles_built=0,
        input_sha256={str(p.relative_to(root)):sha(p) for p in [root/R.SUMMARY,root/R.PREDICTIONS,
            root/B.S.SOURCE,*sorted((root/R.PANEL_OUT).glob('*/*.json'))]},
        limitations=['Same frozen cached profiles, not independent validation or new experiment',
                     'Measured refinement differences do not exclude common numerical bias',
                     'No H1/H0 conclusion from a five-point subset; primary verdict unchanged'])
    for p,digest in cache.provenance.items():assert sha(p)==digest,'CACHE_CHANGED_DURING_READ'
    return rows_out,summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=OUT)
    args=parser.parse_args();assert not args.out.exists(),'ANALYSIS_OUTPUT_EXISTS'
    rows,summary=diagnostics()
    args.out.mkdir(parents=True,exist_ok=False)
    with (args.out/'members.csv').open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary['analyzer_sha256']=sha(__file__)
    with (args.out/'summary.json').open('x') as stream:
        json.dump(summary,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({k:summary[k] for k in ('primary_verdict','D_U_not_ready','D_U_ready_deadband',
          'D_positive_ids','max_replay_loss_error','new_evaluator_calls','new_profiles_built')},indent=2))


if __name__=='__main__':main()
