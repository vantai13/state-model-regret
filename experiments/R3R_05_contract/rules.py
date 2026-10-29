"""Doan Van Tai — exact contract arithmetic, diagnostic numerical rules, no engine."""
from fractions import Fraction as F

EPS_R, EPS_E, TOL_NUM, U_MAX = F(1,100), F(1,200), F(1,400), F(1,10)
CONTRASTS = ('G_S','G_M','G_SM','Gamma','G_S_M1','G_M_S1')


def relative(value, denominator):
    d = F(denominator)
    if d < 0: raise ValueError('nonnegative cost/stakes denominator required')
    return None if d == 0 else F(value)/d


def ratio_of_expectations(weights, gains, costs):
    if not (len(weights)==len(gains)==len(costs)) or not weights: raise ValueError('aligned nonempty population required')
    p = list(map(F,weights))
    if min(p)<0 or sum(p)!=1: raise ValueError('normalized nonnegative population required')
    if any(F(c)<0 for c in costs): raise ValueError('negative oracle cost')
    return relative(sum(w*F(g) for w,g in zip(p,gains)),sum(w*F(c) for w,c in zip(p,costs)))


def conditional_weights(weights, keep):
    p=list(map(F,weights))
    if len(p)!=len(keep) or not p or min(p)<0 or sum(p)!=1:raise ValueError('valid population/mask required')
    mass=sum(w for w,k in zip(p,keep) if k)
    if mass==0:raise ValueError('zero-probability conditioning event')
    return [w/mass if k else F(0) for w,k in zip(p,keep)]


def compare_levels(fine, coarse):
    """R1 requires cost-scale AND normalized-ratio stability, for all six contrasts.

    These differences are diagnostics, never certified error bars.
    """
    cf,cc=F(fine['Cref']),F(coarse['Cref'])
    if min(cf,cc)<=0:return dict(ready=False,reason='UNDEFINED_DENOMINATOR',deltas=None)
    delta={}
    flips=[]
    for name in CONTRASTS:
        gf,gc=F(fine[name]),F(coarse[name]);zf,zc=gf/cf,gc/cc
        delta[name]=max(abs(gf-gc)/cf,abs(zf-zc))
        if zf*zc<0 and abs(zf)>EPS_E and abs(zc)>EPS_E:flips.append(name)
    cref_delta=abs(cf-cc)/cf
    return dict(ready=max(delta.values())<=TOL_NUM and cref_delta<=TOL_NUM and not flips,
                reason='REFINEMENT_DIAGNOSTIC_ONLY',deltas=delta,cref_delta=cref_delta,sign_flips=flips)


def classify_threshold(value, measured_difference, *, kind='effect', remaining_steps=0, certified_exact=False):
    """R6 near-threshold ambiguity is criterion-specific, including harm/equivalence.

    Caller must also pass all R1/R2 checks before treating this as a usable label.
    An empirical difference of zero is not an estimand error certificate.
    """
    if value is None:return 'UNDEFINED'
    if kind not in ('effect','harm','equivalence'):raise ValueError('unknown criterion')
    if remaining_steps<0 or not isinstance(remaining_steps,int):raise ValueError('finite nonnegative step budget required')
    z,d=F(value),F(measured_difference)
    if d<0:raise ValueError('nonnegative measured difference required')
    threshold=EPS_E if kind=='equivalence' else EPS_R
    transformed=abs(z) if kind=='equivalence' else (-z if kind=='harm' else z)
    if not certified_exact and abs(transformed-threshold)<=d:
        return 'ESCALATE' if remaining_steps else 'UNRESOLVED'
    meets=transformed<=threshold if kind=='equivalence' else transformed>=threshold
    return 'MEETS' if meets else 'DOES_NOT_MEET'


def escalation_levels(K, ref):
    """Exactly two shared escalation steps: first 2K, then double ref."""
    if any(isinstance(v,bool) or not isinstance(v,int) or v<2 or v%2 for v in (K,ref)):
        raise ValueError('even K/ref >=2 required for both coarse-axis checks')
    return [(K,ref),(2*K,ref),(2*K,2*ref)]


def unresolved_bounds(meets, does_not_meet, unresolved):
    counts=(meets,does_not_meet,unresolved)
    if any(isinstance(v,bool) or not isinstance(v,int) or v<0 for v in counts):raise ValueError('nonnegative integer counts')
    n=sum(counts)
    if n==0:return dict(status='INCONCLUSIVE',rate_low=None,rate_high=None,unresolved_rate=None)
    rate=F(unresolved,n)
    return dict(status='INCONCLUSIVE' if rate>U_MAX else 'APPLY_PREREG_TO_BOTH_EXTREMES',
                rate_low=F(meets,n),rate_high=F(meets+unresolved,n),unresolved_rate=rate)


def numerical_coverage(K, ref):
    """Separate K and dt coarse neighbors prevent cancellation in a joint step."""
    escalation_levels(K,ref)
    return dict(main=(K,ref),coarse_K=(K//2,ref),coarse_dt=(K,ref//2))
