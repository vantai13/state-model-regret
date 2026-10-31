"""Doan Van Tai — replay saved discovery scores and compare mean profiles; no new truth."""
import csv
from fractions import Fraction as F
import json
from unittest.mock import patch

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

from experiments.P4_07_clipping.check_clipping import cached_side, current_measure
from experiments.R3R_08_population_numerics import quadrature
from .discovery import ROOT, OUT, references, write_json
from .predictor import StationaryCache, mean_side, action_mismatch, predict, nearest


def main():
    rows=list(csv.DictReader((OUT/'predictions.csv').open()))
    summary=json.loads((OUT/'summary.json').read_text())
    training,_,_=references()
    saved=list(csv.DictReader((OUT/'nn_training.csv').open()))
    assert [(r['key'],r['GM_S1_pctC']) for r in training]==[(r['key'],float(r['GM_S1_pctC'])) for r in saved]
    y,p,n=(np.array([float(r[k]) for r in rows]) for k in ('GM_true_pctC','GM_pred_pctC','NN_pred_pctC'))
    for r in rows:
        reference=nearest(r['key'],training,leave_out=True)
        assert reference['key']==r['NN_key'] and reference['GM_S1_pctC']==float(r['NN_pred_pctC'])
    scores=dict(Spearman=float(spearmanr(p,y).statistic),stationary_MedAE_pp=float(np.median(abs(p-y))),
                NN_MedAE_pp=float(np.median(abs(n-y))))
    assert all(v==summary['metrics'][k] for k,v in scores.items())
    assert len(rows)==86 and summary['new_heldout_outcomes']==0
    verification=dict(status='PASS',scores=scores,NN_references_replayed=len(rows),training_replayed=len(saved))
    base=ROOT/'results/lessons/l4_9_v2'
    write_json(base/'saved_score_verification.json',verification)

    # Native caches are read ONLY here to validate old discovery mean profiles.
    # The predictor itself never calls profiles.get or loads native finite-h costs.
    allrows={r['id']:r for r in csv.DictReader((ROOT/'results/lessons/l4_6_v2/analysis/rows.csv').open()) if r['engine']=='native'}
    cache=StationaryCache(ROOT,base/'native_cache')
    checks=[]
    for cid in ('P44_002','P44_005','P44_014','SUB_0000'):
        path=ROOT/allrows[cid]['source'];raw=json.loads(path.read_text())
        case=dict(raw=raw,cache=path.parents[2]/'native_cache')
        native=[];maxgap=0.;sameflags=True
        for which in ('A','B'):
            side=cached_side(case,which);old=side['costs'];factor=old['factor']
            cap=max((int(old['profiles'][name]['modes'][m][0][-1])+factor-1)//factor for name in ('d','dh') for m in (0,1))
            grid=quadrature.build(side['law'],raw['K'],cap)
            with patch.object(quadrature,'build',return_value=grid):
                rebuilt=mean_side(side['lam'],side['pre'],side['post'],F(raw['parameters'][2]),side['h'],side['ref'],raw['K'],side['unit'],side['law'])
            original=current_measure(side,raw['K'])
            maxgap=max(maxgap,float(np.max(abs(original['h']-rebuilt['h']))))
            sameflags=sameflags and np.array_equal(original['zero_h'],rebuilt['zero']) and np.array_equal(original['sat_h'],rebuilt['sat'])
            native.append(dict(h=original['h'],eh=original['eh'],zero=original['zero_h'],sat=original['sat_h'],w=original['w']))
        pred=predict(raw['parameters'],cache,ref=raw['ref'],K=320)
        pm=action_mismatch(*native,pred['s'])['P_mis']
        assert maxgap==0 and sameflags
        checks.append(dict(id=cid,max_mean_gap_difference=maxgap,zero_saturation_flags_equal=bool(sameflags),
                           pmis_native_grid=pm,pmis_predictor_grid=pred['P_mis'],pmis_abs_difference=abs(pm-pred['P_mis'])))
    write_json(base/'mean_only_validation.json',dict(status='PASS',checks=checks,
        note='Pointwise mean-only profiles match existing native dh bitwise on four discovery grids; no tuning or replacement of primary86score. M1 cached fields only in this validation, not predictor inputs.'))

    fig,axes=plt.subplots(1,2,figsize=(9,4),sharex=True,sharey=True,layout='constrained')
    limits=[min(0,float(min(y.min(),p.min(),n.min()))),float(max(y.max(),p.max(),n.max()))*1.04]
    flagged=np.array([r['arithmetic_pass_original']!='True' for r in rows])
    for ax,values,title in zip(axes,(p,n),('Stationary predictor','1-NN (physical-key leave-one-out)')):
        ax.scatter(y[~flagged],values[~flagged],s=21,alpha=.8,label='Original raw flag absent')
        ax.scatter(y[flagged],values[flagged],s=27,marker='x',color='#d55e00',label='Original raw flag retained')
        ax.plot(limits,limits,color='#555555',lw=1);ax.set(xlim=limits,ylim=limits,title=title,xlabel='Saved native model value (% Cref)')
        ax.grid(alpha=.18)
    axes[0].set_ylabel('Prediction (% Cref)');axes[0].legend(fontsize=7)
    fig.suptitle('Discovery only: 86 fixed points; no fitted parameters')
    for ext in ('png','pdf'):fig.savefig(base/('discovery_predictions.'+ext),dpi=180)
    plt.close(fig)
    print(json.dumps(verification))


if __name__=='__main__':main()
