"""Doan Van Tai — compact sparse proposal and explicit longdouble roundoff bounds."""
from fractions import Fraction as F
import numpy as np
from scipy.sparse import csc_matrix,eye
from scipy.sparse.linalg import splu
from smr.stationary import tail_plan,StationaryBudgetError

LD=np.longdouble

def gamma(n):
    u=LD(np.finfo(LD).eps)/2
    if n*u>=1:raise ArithmeticError('roundoff budget exhausted')
    return np.nextafter(n*u/(1-n*u),LD(np.inf))

def positive_sum(values):
    a=np.asarray(values,dtype=LD)
    if np.any(a<0):raise ValueError('nonnegative values required')
    total=np.sum(a,dtype=LD)
    return total,gamma(len(a))*total/(1-gamma(len(a)))

def stationary_two_mode_v2(increments,keep,keep_error=F(0),memory_limit=4*1024**3):
    plan=tail_plan(increments,keep,keep_error);K=plan['cutoff'];n=2*(K+1)
    predicted=n*(2*max(map(abs,increments))+8)*24+n*160
    if predicted>memory_limit:raise StationaryBudgetError(f'LU allocation estimate {predicted} exceeds {memory_limit}')
    q=np.arange(K+1,dtype=np.int64);rr=[];cc=[];data=[];s=float(keep)
    for m,a in enumerate(increments):
        i=2*q+m;jq=np.minimum(K,np.maximum(0,q+a))
        for mode in (0,1):
            j=2*jq+mode;mask=(i>0)&(j>0)
            rr.append(j[mask]-1);cc.append(i[mask]-1);data.append(np.full(mask.sum(),s if m==mode else 1-s))
    A=eye(n-1,format='csc')-csc_matrix((np.concatenate(data),(np.concatenate(rr),np.concatenate(cc))),shape=(n-1,n-1))
    lu=splu(A,permc_spec='NATURAL');rhs=np.zeros(n-1);rhs[0]=1-s
    z=np.r_[LD(1),lu.solve(rhs).astype(LD)];norm,norm_err=positive_sum(np.abs(z))
    if np.any(z<0):raise ArithmeticError('negative sparse occupation')
    mass=(z/norm).reshape(K+1,2)
    prob=LD(str(keep.numerator))/LD(str(keep.denominator));prob_error=LD(float(keep_error))+4*np.finfo(LD).eps
    incoming=np.zeros_like(mass)
    for m,a in enumerate(increments):
        target=np.minimum(K,np.maximum(0,q+a))
        for mode in (0,1):np.add.at(incoming[:,mode],target,mass[:,m]*(prob if m==mode else 1-prob))
    fan=2*max(map(abs,increments))+4
    residual=np.sum(abs(incoming-mass),dtype=LD)/2+gamma(fan)*np.sum(abs(incoming))+2*prob_error
    normalization=norm_err/norm+gamma(3)
    d,b=-increments[0],increments[1];B=(d+b)/(2*(1-prob));C=d/(prob-prob_error)
    T=(K+B+C)/((d-b)/2-prob_error*B)
    error=(1+2*T)*LD(plan['tail_bound'])+2*T*(residual+normalization)+normalization
    cert=dict(**plan,method='sparse_longdouble',longdouble_eps=str(np.finfo(LD).eps),
              rounding_bound=str(gamma(fan)+normalization),residual_tv_upper=str(residual),
              infinite_law_error_upper=str(error),estimated_bytes=predicted,
              status='PASS' if error<=LD('1e-10') else 'HOLD_PRECISION_BOUND')
    return mass,cert
