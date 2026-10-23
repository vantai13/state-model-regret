"""Doan Van Tai — factorized strict-sign screening; no cost/margin persistence."""
import ctypes,hashlib,subprocess,tempfile,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np


def library():
    source=Path(__file__).with_name('native')/'idle_backward.cpp'
    name=hashlib.sha256(source.read_bytes()).hexdigest()[:20]
    target=Path(tempfile.gettempdir())/f'smr-idle-{name}.so'
    if not target.exists():subprocess.run(['g++','-O3','-std=c++17','-shared','-fPIC','-ffp-contract=off',str(source),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target))
    for fn in (lib.idle64,lib.idle80):
        fn.argtypes=[ctypes.c_int]*3+[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p];fn.restype=None
    return lib


def backward(indices,increments,H,keep,keep_error=F(0),extended=False):
    if H<1 or H>1_000_000 or min(indices)<0:raise ValueError('invalid horizon/indices')
    dtype=np.longdouble if extended else np.float64
    a,b=increments;N=H*max(0,-a,-b)
    if 4*(N+1)*np.dtype(dtype).itemsize>4*1024**3:raise MemoryError('DP exceeds4GiB')
    indices=np.ascontiguousarray(indices,dtype=np.int64);out=np.zeros((len(indices),2),dtype=dtype)
    p=np.array([dtype(str(keep.numerator))/dtype(str(keep.denominator))],dtype=dtype)
    fn=library().idle80 if extended else library().idle64
    start=time.monotonic();fn(H,a,b,p.ctypes.data,len(indices),indices.ctypes.data,out.ctypes.data)
    elapsed=time.monotonic()-start
    if elapsed>1200:raise TimeoutError('DP exceeds1200s per action')
    eps=np.finfo(dtype).eps;nu=8*H*eps/2;gamma=nu/(1-nu)
    p_error=float(abs(F(str(p[0]))-keep)+keep_error)+2*float(eps)
    maximum=H*(H+1)/2*max(0,-a,-b)
    error=gamma*maximum/(1-gamma)+2*H*p_error*maximum
    return out,error,elapsed


def probability_interval(A,B,pA,pB,errorA,errorB,D_error=0.,zeroA=None,zeroB=None):
    A=np.asarray(A,dtype=np.longdouble).ravel();B=np.asarray(B,dtype=np.longdouble).ravel()
    pa=np.asarray(pA,dtype=np.longdouble).ravel();pb=np.asarray(pB,dtype=np.longdouble).ravel()
    if len(A)!=len(pa) or len(B)!=len(pb):raise ValueError('shape mismatch')
    # Numerical signs are intersected with proved WA>=0 and WB<=0 bounds.
    alo=np.maximum(0,A-errorA);ahi=np.maximum(0,A+errorA)
    blo=np.minimum(0,B-errorB);bhi=np.minimum(0,B+errorB)
    if zeroA is not None:alo[zeroA]=ahi[zeroA]=0
    if zeroB is not None:blo[zeroB]=bhi[zeroB]=0
    def less_mass(values,threshold,side):
        order=np.argsort(values);cumulative=np.r_[np.longdouble(0),np.cumsum(pb[order],dtype=np.longdouble)]
        idx=np.searchsorted(values[order],threshold,side=side)
        return np.sum(pa*cumulative[idx],dtype=np.longdouble)
    switch=less_mass(bhi,-ahi,'left')
    # A+B >=0 is certainly Stay, including exact structural ties.
    possible=less_mass(blo,-alo,'left')
    numerical=max(0,float(possible-switch));rounding=16*(len(A)+len(B))*float(np.finfo(np.longdouble).eps)
    return dict(p_low=max(0.,float(switch)-D_error-rounding),p_high=min(1.,float(possible)+D_error+rounding),
                unresolved_mass=numerical,D_error=D_error,aggregation_rounding_bound=rounding)
