"""Doan Van Tai — fit only 38 A04 cells; twenty-slice LOSO, identical budgets."""
from datetime import datetime,timezone
from fractions import Fraction as F
import importlib.metadata
import platform
import time
import traceback

import numpy as np

from experiments.A05_freeze.features import load_design,tensor,CANDIDATES
from experiments.A05_freeze.ledger import contrasts
from experiments.A05_freeze.model import fit_model,predict_model
from experiments.A05_freeze.provenance import ROOT,CONFIG,FITDIR,read,write,sha,verify_prereg


def training_summaries(records,data):
    y=[]
    for record in records:
        cid=record['id'];r=data[cid]
        if not cid.startswith('M') or r['dt_s']!='1/240' or r['refinement']!=2 or r['status']!='BOUNDED':
            raise PermissionError('fit can only consume A04 fine-level main records')
        C,ed,edh,en=map(F,(r['C_ref'],r['E_delta'],r['E_delta_hat'],r['E_neg']))
        t10=F(r['G']['G_M_S1'])-en
        if C<=0:raise ValueError('positive training reference required')
        y.append([float(v/C) for v in (ed,edh,en,t10)])
    return np.asarray(y)


def loso(records,y,model,candidate,cfg):
    X=tensor(records,model,candidate)
    slices=sorted({r['slice'] for r in records})
    if len(slices)!=20:raise ValueError('exactly twenty design slices required')
    rows=[]
    for name in slices:
        test=np.asarray([r['slice']==name for r in records]);train=~test
        theta=fit_model(X[train],y[train],cfg)
        predictions=predict_model(X[test],theta,cfg)
        mse=float(np.mean((predictions-y[test])**2))
        rows.append(dict(slice=name,train_cells=int(sum(train)),test_ids=[r['id'] for r,t in zip(records,test) if t],
                 summary_MSE=mse,summary_MAE=float(np.mean(abs(predictions-y[test]))),
                 contrast_MAE=float(np.mean(abs(contrasts(predictions)-contrasts(y[test])))),
                 chosen_start=theta['chosen_start'],optimizer_starts=theta['starts']))
        print(f'LOSO {model}/{candidate}/{name}: summary_MSE={mse:.8g}',flush=True)
    # Equal slice weights: singleton floor slices each receive one fold weight.
    return dict(candidate=candidate,mean_slice_MSE=float(np.mean([r['summary_MSE'] for r in rows])),folds=rows)


def main():
    receipt=verify_prereg()
    cfg=read(ROOT/CONFIG)
    out=ROOT/FITDIR;out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    records=load_design('main')
    ids=[r['id'] for r in records]
    if ids!=[f'M{i:02}' for i in range(1,39)]:raise PermissionError('wrong fit cells')
    path=ROOT/cfg['fit_outcome_inputs']
    y=training_summaries(records,read(path)['fine'])
    write(out/'fit_input.json',dict(design_main=records,summaries=y.tolist(),A04_input_sha256=sha(path)))
    write(out/'manifest.json',dict(responsible='Doan Van Tai',start_utc=datetime.now(timezone.utc).isoformat(),
          **receipt,python=platform.python_version(),libraries={k:importlib.metadata.version(k) for k in ('numpy','scipy')},
          seed=None,fit_ids=ids,heldout_features_read=False,heldout_D_or_outcomes=False))
    all_cv={};models={}
    try:
        for model in ('H0','H1'):
            candidates=list(CANDIDATES[model])
            if len(candidates)!=cfg['candidates_per_model']:raise ValueError('unequal candidate budget')
            cv=[loso(records,y,model,c,cfg) for c in candidates]
            all_cv[model]=cv
            write(out/'loso.json',all_cv)
            selected=min(range(len(cv)),key=lambda i:(cv[i]['mean_slice_MSE'],i))
            candidate=candidates[selected]
            theta=fit_model(tensor(records,model,candidate),y,cfg)
            models[model]=dict(candidate=candidate,LOSO_summary_MSE=cv[selected]['mean_slice_MSE'],**theta)
            print(f'SELECTED {model}/{candidate}; k={theta["k"]}; LOSO={cv[selected]["mean_slice_MSE"]:.8g}',flush=True)
        result=dict(responsible='Doan Van Tai',**receipt,fit_ids=ids,fit_slices=20,models=models,
                    all_candidate_LOSO={m:{c['candidate']:c['mean_slice_MSE'] for c in cs} for m,cs in all_cv.items()},
                    selection_rule='minimum equal-slice mean squared normalized-summary error; ties by declared candidate order',
                    wall_s=time.monotonic()-started,end_utc=datetime.now(timezone.utc).isoformat(),
                    heldout_features_computed=False,heldout_outcomes_computed=False)
        write(out/'theta.json',result)
        write(out/'fit_status.json',dict(status='PASS',models=2,LOSO_folds=80,full_fits=2,solver_starts=164,
                                       wall_s=result['wall_s'],heldout_inputs=False))
    except Exception as exc:
        write(out/'fit_status.json',dict(status='FAIL',error=repr(exc),traceback=traceback.format_exc(),
                                       wall_s=time.monotonic()-started,heldout_inputs=False))
        raise


if __name__=='__main__':main()
