"""Exact R1 diagnostics and conservative arithmetic boundary checks."""
from fractions import Fraction as F
from experiments.R3R_05_contract.rules import compare_levels,CONTRASTS,TOL_NUM,EPS_R


def check(bundle,K,ref):
    keys=[f'{K}:{ref}',f'{K//2}:{ref}',f'{K}:{ref//2}']
    if any(k not in bundle for k in keys):return dict(ready=False,reason='missing_levels')
    fine=bundle[keys[0]];coarse=[bundle[k] for k in keys[1:]]
    comparisons=[compare_levels(fine,c) for c in coarse]
    arithmetic=all(row['arithmetic_pass'] and not row['validity_errors'] for row in [fine,*coarse])
    for comparison,c in zip(comparisons,coarse):
        if comparison['deltas']:
            for metric,delta in comparison['deltas'].items():
                arithmetic &= delta+F(fine.get('normalized_error',{}).get(metric,0))+F(c.get('normalized_error',{}).get(metric,0))<=TOL_NUM
            error=(F(fine.get('cost_error',{}).get('11',0))+F(c.get('cost_error',{}).get('11',0)))/F(fine['Cref'])
            arithmetic &= comparison['cref_delta']+error<=TOL_NUM
    return dict(ready=all(c['ready'] for c in comparisons) and arithmetic,
                refinement_ready=all(c['ready'] for c in comparisons),arithmetic_ready=arithmetic,
                checks=[{k:{a:str(b) for a,b in v.items()} if isinstance(v,dict) else str(v) if isinstance(v,F) else v for k,v in row.items()} for row in comparisons],
                max_delta=str(max((v for c in comparisons if c['deltas'] for v in c['deltas'].values()),default=F(0))),
                Cref_delta=str(max(c.get('cref_delta',F(1)) for c in comparisons)))


def planning_seconds(levels,K,ref):
    rows=[levels[f'{k}:{r}'] for k,r in ((K,ref),(K//2,ref),(K,ref//2))]
    seen={};created=0.
    for row in rows:
        for side in row['source_components'].values():
            for name in ('law','profile'):
                key=(name,side[name+'_key']);seen[key]=max(seen.get(key,0),side[name+'_cold_cpu_seconds'])
                created+=side[name+'_created_cpu_seconds']
    observed=sum(row['cpu_seconds'] for row in rows)
    return dict(actual_estimator_cpu_seconds=observed,
                cold_component_cpu_charge=sum(seen.values()),created_component_cpu_seconds=created,
                cold_bundle_planning_seconds=max(observed,observed-created+sum(seen.values())),
                scope='component-adjusted calibration timing, not a population p95 guarantee')
