"""Prospective finite-panel verdicts. Does not compute or load any outcomes."""
from fractions import Fraction as F
import numpy as np
from scipy.stats import spearmanr


def state_verdict(labels, *, planned=12):
    if len(labels)!=planned or any(x not in ('MEETS','DOES_NOT_MEET','UNRESOLVED') for x in labels):
        return dict(verdict='INCONCLUSIVE',reason='INCOMPLETE_OR_INVALID_PANEL')
    m,f,u=(labels.count(x) for x in ('MEETS','DOES_NOT_MEET','UNRESOLVED'))
    lower,upper=F(m,planned),F(m+u,planned)
    verdict='INCONCLUSIVE'
    if F(u,planned)<=F(1,10):
        if lower>=F(9,10):verdict='PASS'
        elif upper<F(9,10):verdict='FAIL'
    return dict(verdict=verdict,meets=m,fails=f,unresolved=u,rate_low=float(lower),rate_high=float(upper))


def model_metrics(prediction,nearest,truth):
    p,n,y=map(lambda x:np.asarray(x,dtype=float),(prediction,nearest,truth))
    if not (len(p)==len(n)==len(y)) or len(y)<3 or not all(np.isfinite(x).all() for x in (p,n,y)):
        raise ValueError('finite aligned panel required')
    med,base=float(np.median(abs(p-y))),float(np.median(abs(n-y)))
    rho=float(spearmanr(p,y).statistic) if np.ptp(p)>1e-12 and np.ptp(y)>1e-12 else None
    return dict(Spearman=rho,stationary_MedAE_pp=med,NN_MedAE_pp=base,
                relative_improvement=None if base==0 else 1-med/base,
                passes=bool(rho is not None and rho>=.7 and base>0 and med<=.7*base))


def model_verdict(prediction,nearest,truth_by_level, *, all_ready,planned=12):
    if (not all_ready or len(prediction)!=planned or len(nearest)!=planned or len(truth_by_level)!=3
            or any(len(y)!=planned for y in truth_by_level)):
        return dict(verdict='INCONCLUSIVE',reason='NEED_COMPLETE_READY_PANEL_AND_THREE_LEVELS')
    metrics=[model_metrics(prediction,nearest,y) for y in truth_by_level]
    passed=[m['passes'] for m in metrics]
    return dict(verdict='PASS' if all(passed) else 'FAIL' if not any(passed) else 'INCONCLUSIVE',
                metrics_by_level=metrics,reason='FIXED_PREDICTIONS_THREE_LEVEL_SENSITIVITY')
