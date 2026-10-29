"""Complete stationary measure: zero atom, finite feature support and zero-feature tail."""
import numpy as np
from .piecewise import LD,EPS


def build(law,K,cap):
    if type(K) is not int or K<2:raise ValueError('at least two positive-mass bins')
    c,e=law.cdf([0,cap]);start=c[0].sum();head=max(LD(0),c[1].sum()-start)
    edges=law.quantiles(start+head*np.arange(1,K,dtype=LD)/K,cap)
    lo=np.r_[1,edges+1];hi=np.r_[edges,cap];good=hi>=lo;lo,hi=lo[good],hi[good]
    a,ea=law.cdf(lo-1);b,eb=law.cdf(hi)
    targets=(a.sum(axis=1)+b.sum(axis=1))/2
    reps=np.clip(law.quantiles(targets,cap),lo,hi)
    weights=b-a;errors=ea+eb
    if np.any(weights+errors<0):raise ArithmeticError('bin weights not certified nonnegative')
    projected=np.maximum(LD(0),weights);errors+=abs(projected-weights);weights=projected
    zero,ezero=law.point([0]);tail=LD('.5')-c[1]
    indices=np.r_[0,reps,-1].astype(np.int64)
    mass=np.vstack([zero[0],weights,tail]);error=np.vstack([ezero[0],errors,e[1]])
    l1=error.sum(dtype=LD)+256*len(mass)*EPS
    if np.any(mass<0) or abs(mass.sum(dtype=LD)-1)>l1:raise ArithmeticError('complete measure mass guard failed')
    return dict(indices=indices,mass=mass,error=error,l1_error=l1,cap=cap,
                tail_probability_upper=tail.sum()+e[1].sum(),renormalized=False)
