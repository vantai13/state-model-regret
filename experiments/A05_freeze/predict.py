"""Doan Van Tai — held-out level0–2 feature/prediction freeze after theta commit."""
from datetime import datetime,timezone
from fractions import Fraction as F

from experiments.A05_freeze.features import load_design,tensor,values,group
from experiments.A05_freeze.ledger import contrasts,CONTRASTS
from experiments.A05_freeze.model import predict_model
from experiments.A05_freeze.provenance import ROOT,CONFIG,THETA,PREDICTIONS,DISCRIMINATION,FEATURES,read,write,verify_theta


def discrimination(predictions,cfg):
    result={}
    primary=cfg['primary_metric']
    for name,ids in cfg['test_groups'].items():
        def D(metrics):
            return sum(abs(F(predictions[c]['H0']['contrasts'][g])-F(predictions[c]['H1']['contrasts'][g]))
                       for c in ids for g in metrics)/(len(ids)*len(metrics))
        value=D(primary)
        result[name]=dict(ids=ids,n_cells=len(ids),metric=primary,equal_weight=True,
              D=str(value),D_fraction_Cref=float(value),D_percentage_points_Cref=100*float(value),
              margin=cfg['margin'],comparison_open=value>=F(cfg['margin']),
              decision='OPEN_COMPARISON' if value>=F(cfg['margin']) else 'DO_NOT_OPEN_COMPARISON',
              diagnostics_only_D_by_contrast={g:float(D([g])) for g in CONTRASTS})
    # Declare all twelve; consume outcomes only for active comparisons or frozen rules.
    needed=set(cfg['K5_test_ids']+cfg['C1_test_ids'])
    for r in result.values():
        if r['comparison_open']:needed.update(r['ids'])
    return dict(groups=result,primary_group='interpolation',
          interpretation='D>=m is necessary discrimination, not a power guarantee or an outcome verdict',
          outcome_open_ids=sorted(needed),registered_universe=[f'R{i:02}' for i in range(1,13)],
          outcomes_not_needed=[f'R{i:02}' for i in range(1,13) if f'R{i:02}' not in needed],
          group_mixing_allowed=False,heldout_truth_used=False)


def main():
    receipt=verify_theta()  # must precede the held-out design read
    for path in (PREDICTIONS,DISCRIMINATION,FEATURES):
        if (ROOT/path).exists():raise FileExistsError('predictions already exist; never replace the frozen view')
    cfg=read(ROOT/CONFIG);theta=read(ROOT/THETA)
    records=load_design('heldout',allow_heldout=True)
    if [r['id'] for r in records]!=[f'R{i:02}' for i in range(1,13)]:raise PermissionError('wrong test universe')
    for name,ids in cfg['test_groups'].items():
        if [r['id'] for r in records if group(r)==name]!=ids:raise PermissionError('coordinate grouping changed')
    predictions={r['id']:{} for r in records}
    for model in ('H0','H1'):
        candidate=theta['models'][model]['candidate']
        s=predict_model(tensor(records,model,candidate),theta['models'][model],cfg)
        gains=contrasts(s)
        for r,summary,g in zip(records,s,gains):
            predictions[r['id']][model]=dict(summaries_normalized=[str(float(x)) for x in summary],
                            contrasts={k:str(float(v)) for k,v in zip(CONTRASTS,g)})
    features=dict(responsible='Doan Van Tai',**receipt,maximum_tier=2,heldout_D_computed=False,
                  created_utc=datetime.now(timezone.utc).isoformat(),
                  design_whitelist=records,feature_values={r['id']:values(r) for r in records},
                  forbidden_inputs=['p_sw','cost','gap','Cref','bias outcomes','headroom','posterior D moments'])
    disc=discrimination(predictions,cfg)
    write(ROOT/FEATURES,features)
    write(ROOT/PREDICTIONS,dict(responsible='Doan Van Tai',**receipt,
          created_utc=datetime.now(timezone.utc).isoformat(),predictions=predictions,
          units='fractions of Cref predicted directly; true target Cref never read',
          heldout_truth_computed=False,heldout_D_computed=False))
    write(ROOT/DISCRIMINATION,disc)
    for name,r in disc['groups'].items():
        print(name,'D=',r['D_percentage_points_Cref'],'percentage points Cref;',r['decision'],flush=True)
    print('Planned outcome IDs:',','.join(disc['outcome_open_ids']),'; no outcomes computed.',flush=True)


if __name__=='__main__':main()
