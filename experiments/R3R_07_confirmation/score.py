"""Join registered rows to numerical bundles and the unchanged frozen scorer.

This module consumes results, never runs an engine. Missing coarse checks remain
UNRESOLVED. R3 orchestration and arithmetic certificates belong to the audited
v1.3.1 adapter; a caller cannot replace them with an unqualified 'ready' flag.
"""
from collections import Counter
from fractions import Fraction as F

from experiments.R3R_05_contract.rules import compare_levels
from experiments.R3R_06_cards import verdict as V
from .common import ORDER


def label_result(criterion, result):
    fine = result['main']
    cf = F(fine['Cref'])
    if cf < 0:
        raise ValueError('negative reference cost')
    if cf == 0:
        return 'UNDEFINED'
    metric = 'G_M' if criterion == 'effect' else 'G_S'
    if not all(result.get(k) is not None for k in ('coarse_K','coarse_dt')):
        return 'UNRESOLVED'
    checks = [compare_levels(fine,result[k]) for k in ('coarse_K','coarse_dt')]
    ready = all(c['ready'] for c in checks) and result.get('arithmetic_pass') is True
    d = max(c['deltas'][metric] for c in checks if c['deltas'] is not None) if all(c['deltas'] for c in checks) else F(0)
    # Arithmetic enclosures are separate from empirical refinement. Either can
    # make a threshold unresolved; neither is silently treated as an exact tie.
    d=max(d,F(fine.get('normalized_error',{}).get(metric,0)))
    # Exact threshold certificates, if any, must be validated by the audited adapter.
    return V.regime_label(criterion,F(fine[metric])/cf,d,r1_ready=ready,certified_exact=False)


def score_batch(rows, results, *, validity_reasons=()):
    ids = [row['regime']['id'] for row in rows]
    if len(ids)!=len(set(ids)) or set(results)!=set(ids):
        raise ValueError('score only the complete registered batch, without duplicate/extra/missing IDs')
    counts = {region: Counter() for region in ORDER}
    labels = {}
    for row in rows:
        origin, rid = row['origin_region'], row['regime']['id']
        if origin not in counts:
            raise ValueError('unknown origin region')
        criterion = 'effect' if origin.startswith('MV') else 'harm'
        label = label_result(criterion,results[rid])
        labels[rid] = label
        counts[origin][label] += 1
    return dict(labels=labels,counts={k:dict(v) for k,v in counts.items()},
                cards={name:V.primary_verdict(counts[plus],counts[minus],validity_reasons=validity_reasons)
                       for name,plus,minus in (('Hyp-MV','MV+A','MV-ii'),('Hyp-SH','SH+A','SH-ii'))},
                boundary_role='descriptive only; never rescues a primary')


def require_zero_control(values):
    from experiments.R3R_05_contract.rules import CONTRASTS
    if set(values) != set(CONTRASTS) or any(F(value)!=0 for value in values.values()):
        raise ValueError('CONTROL_NONZERO_OR_INCOMPLETE: stop; no epsilon')


def require_identical_models(values):
    if any(F(values[key])!=0 for key in ('G_M','G_M_S1')):
        raise ValueError('IDENTICAL_MODELS_NONZERO: stop; no epsilon')
