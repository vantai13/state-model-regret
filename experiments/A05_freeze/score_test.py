"""Doan Van Tai — future A05-T scorer; verifies frozen prediction SHA before input.

This module never calls an engine. Actual outcomes may be supplied only by the
separate A05-T runner after its one-time irreversible-decision record.
"""
import argparse
from fractions import Fraction as F
from pathlib import Path

from experiments.A03_card.grading import (grade_cell,combine,get,ratio,refinement,numerical_hold,STANDS,UNKNOWN)
from experiments.A05_freeze.scoring import compare
from experiments.A05_freeze.provenance import (ROOT,CONFIG,PREDICTIONS,DISCRIMINATION,read,verify_frozen)


def safe(value):
    if isinstance(value,F):return str(value)
    if isinstance(value,dict):return {k:safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [safe(v) for v in value]
    return value


def relative_bands(row,metrics):
    C=get(row,'C_ref')
    if C.lo<=0:raise ValueError('nonpositive reference')
    return [ratio(get(row,g),C) for g in metrics]


def score_group(ids,data,predictions,cfg,group_name,declared_D):
    if F(declared_D)<F(cfg['margin']):
        return dict(verdict='DO_NOT_OPEN',D=declared_D,ids=ids,truth_used=False)
    metrics=cfg['primary_metric']
    available=[];missing=[]
    for cid in ids:
        fine,coarse=data.get('fine',{}).get(cid),data.get('coarse',{}).get(cid)
        reason=None
        if fine is None or coarse is None:
            reason='missing_cell_or_pair'
        elif fine['dt_s']!='1/240' or coarse['dt_s']!='1/120':
            reason='wrong_final_dt'
        elif numerical_hold(fine) or refinement(coarse,fine)!=STANDS:
            reason='numeric_or_dt_hold'
        elif get(fine,'C_ref').lo<=0:
            reason='nonpositive_reference'
        else:
            bands=relative_bands(fine,metrics)
            if max((b.hi-b.lo)/2 for b in bands)>F(cfg['truth_radius_cap_for_comparison']):
                reason='truth_radius_too_large_for_margin'
        if reason:
            missing.append(dict(cell=cid,reason=reason))
        else:
            available.append((cid,bands))
    cap=cfg['primary_max_unavailable_cells'] if group_name=='interpolation' else cfg['secondary_max_unavailable_cells']
    if len(missing)>cap or not available:
        return dict(verdict='INCONCLUSIVE',reason='unavailable_cell_budget',D=declared_D,
                    registered_cells=len(ids),available_cells=len(available),unavailable=missing)
    p0=[];p1=[];truth=[]
    for cid,bands in available:
        for metric,band in zip(metrics,bands):
            p0.append(predictions[cid]['H0']['contrasts'][metric])
            p1.append(predictions[cid]['H1']['contrasts'][metric])
            truth.append((band.lo,band.hi))
    result=compare(truth,p0,p1,margin=cfg['margin'])
    if result['verdict']=='DO_NOT_OPEN':
        result['verdict']='INCONCLUSIVE';result['reason']='remaining_cells_D_below_margin'
    return dict(**result,registered_D=declared_D,registered_cells=len(ids),available_cells=len(available),
                available_ids=[c for c,_ in available],unavailable=missing,
                interpretation='MAE on the preregistered eligible subset; no inference for unavailable cells')


def equivalence(ids,data,cfg):
    cells={}
    for cid in ids:
        fine=data.get('fine',{}).get(cid);coarse=data.get('coarse',{}).get(cid)
        if fine is None or coarse is None:
            cells[cid]=dict(verdict=UNKNOWN,reason='missing_cell_or_pair',headroom_label='NOT_RESOLVED')
            continue
        if fine['dt_s']!='1/240' or coarse['dt_s']!='1/120':
            raise ValueError('frozen equivalence must use registered final dt')
        cell=grade_cell('P5_K',fine,coarse)
        C=get(fine,'C_ref')
        headroom=ratio(get(fine,'R00'),C) if C.lo>0 else None
        label=('STANDS_HEADROOM_LIMITED' if cell['verdict']==STANDS and headroom and headroom.hi<F(1,200)
               else 'STANDS_NOT_CERTIFIED_BY_HEADROOM' if cell['verdict']==STANDS else 'NOT_STANDING_OR_UNRESOLVED')
        cells[cid]=dict(**cell,headroom_label=label,
                        R00_ratio_upper=str(headroom.hi) if headroom else None)
    return dict(verdict=combine([r['verdict'] for r in cells.values()]),cells=cells)


def score(data,predictions,disc,cfg):
    allowed=set(disc['outcome_open_ids'])
    if any(set(data.get(k,{}))-allowed for k in ('fine','coarse')):
        raise PermissionError('outcomes contain a cell not authorized by the frozen opening rule')
    comparisons={name:score_group(info['ids'],data,predictions,cfg,name,info['D']) for name,info in disc['groups'].items()}
    K=equivalence(cfg['K5_test_ids'],data,cfg)
    C1=equivalence(cfg['C1_test_ids'],data,cfg)
    # Fixed A04 K and Q were both STANDS. No new Q witnesses are permitted.
    return dict(PC4=comparisons,primary_verdict=comparisons['interpolation']['verdict'],
                mixed_results_rule='primary interpolation verdict; weak interpolation and extrapolation reported separately',
                K5=dict(locked_before_A04=True,locked_rule_count=1,heldout_K=K,
                        full_rule_verdict=combine([STANDS,STANDS,K['verdict']]),
                        Q_scope='M01-M04 only; frozen witnesses M01,M03'),
                C1=dict(locked_after_A04=True,heldout=C1,threshold='1/200',base_rate='36/38',
                        heuristic_four_equivalence=str(F(36,38)**4)),combined_success_rate=None)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    args=parser.parse_args()
    receipt=verify_frozen()  # before loading any true outcome file
    data=read(args.input)
    result=score(data,read(ROOT/PREDICTIONS)['predictions'],read(ROOT/DISCRIMINATION),read(ROOT/CONFIG))
    import json
    print(json.dumps(safe(dict(provenance=receipt,grades=result)),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
