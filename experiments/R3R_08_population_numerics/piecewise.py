"""Integer-lattice Bellman approximation with explicit uniform cost enclosures."""
import ctypes as C
from fractions import Fraction as F
import hashlib
from functools import lru_cache
from pathlib import Path
import subprocess
import tempfile
import numpy as np

LD=np.longdouble
EPS=np.finfo(LD).eps


def number(value):
    f=F(value);return LD(f.numerator)/LD(f.denominator)


def probability(keep,error=F(0)):
    p=number(keep);represented=F(*p.as_integer_ratio())
    e=number(abs(represented-F(keep))+F(error))+8*EPS
    return np.array([p],dtype=LD),np.array([np.nextafter(e,LD('inf'))],dtype=LD)


@lru_cache(None)
def library():
    source=Path(__file__).with_name('native')/'piecewise.cpp'
    target=Path(tempfile.gettempdir())/('smr-piecewise-'+hashlib.sha256(source.read_bytes()).hexdigest()[:24]+'.so')
    if not target.exists():
        subprocess.run(['g++','-O3','-std=c++17','-shared','-fPIC','-ffp-contract=off',str(source),'-o',str(target)],check=True)
    lib=C.CDLL(str(target));P=C.c_void_p;I=C.c_int64;N=C.c_size_t
    lib.pw_idle.argtypes=[C.c_int,I,I,P,P,P,N];lib.pw_idle.restype=P
    lib.pw_create.argtypes=[N,P,P,N,P,P,P];lib.pw_create.restype=P
    lib.pw_age.argtypes=[P,C.c_int,I,I,P,P,P,N];lib.pw_age.restype=P
    lib.pw_size.argtypes=[P,C.c_int];lib.pw_size.restype=N
    lib.pw_copy.argtypes=[P,C.c_int,P,P];lib.pw_copy.restype=None
    lib.pw_meta.argtypes=[P,P,P];lib.pw_meta.restype=None
    lib.pw_free.argtypes=[P];lib.pw_free.restype=None
    lib.pw_error.restype=C.c_char_p
    return lib


def unpack(handle):
    lib=library()
    if not handle:raise ArithmeticError(lib.pw_error().decode())
    try:
        modes=[]
        for m in (0,1):
            n=lib.pw_size(handle,m);x=np.empty(n,dtype=np.int64);y=np.empty(n,dtype=LD)
            lib.pw_copy(handle,m,x.ctypes.data,y.ctypes.data);modes.append((x,y))
        error=np.zeros(1,dtype=LD);peak=np.zeros(1,dtype=np.uint64)
        lib.pw_meta(handle,error.ctypes.data,peak.ctypes.data)
        return dict(modes=modes,error=error[0],peak_knots=int(peak[0]))
    finally:lib.pw_free(handle)


def idle(H,increments,keep,keep_error=F(0),*,error_budget_raw=LD('1e-6'),max_knots=2_000_000):
    if type(H) is not int or H<1 or H>100_000:raise ValueError('invalid horizon')
    if any(type(a) is not int for a in increments):raise TypeError('integer lattice increments required')
    p,pe=probability(keep,keep_error);tol=np.array([LD(error_budget_raw)/H],dtype=LD)
    return unpack(library().pw_idle(H,*increments,p.ctypes.data,pe.ctypes.data,tol.ctypes.data,max_knots))


def evaluate(profile,q,mode):
    x,y=profile['modes'][mode];q=np.asarray(q,dtype=np.int64)
    indices=np.clip(np.searchsorted(x,q,side='right')-1,0,len(x)-2)
    t=(q-x[indices]).astype(LD)/(x[indices+1]-x[indices]).astype(LD)
    result=y[indices]+t*(y[indices+1]-y[indices])
    return np.where(q>=x[-1],LD(0),np.where(q<=0,y[0],result))


def combine(left,right,subtract=False):
    modes=[];bound=LD(0)
    for m in (0,1):
        x=np.union1d(left['modes'][m][0],right['modes'][m][0])
        a,b=evaluate(left,x,m),evaluate(right,x,m)
        y=a-b if subtract else a+b
        bound=max(bound,LD(128)*EPS*(max(np.max(abs(a)),np.max(abs(b)))+1))
        modes.append((x,np.asarray(y,dtype=LD)))
    return dict(modes=modes,error=left['error']+right['error']+bound,
                peak_knots=max(left['peak_knots'],right['peak_knots']))


def age(profile,steps,increments,keep,keep_error=F(0),*,error_budget_raw=LD('1e-6'),max_knots=2_000_000):
    lib=library();arrays=[np.ascontiguousarray(v) for mode in profile['modes'] for v in mode]
    x0,y0,x1,y1=arrays;e=np.array([profile['error']],dtype=LD)
    initial=lib.pw_create(len(x0),x0.ctypes.data,y0.ctypes.data,len(x1),x1.ctypes.data,y1.ctypes.data,e.ctypes.data)
    if not initial:raise ArithmeticError(lib.pw_error().decode())
    try:
        p,pe=probability(keep,keep_error);tol=np.array([LD(error_budget_raw)/max(1,steps)],dtype=LD)
        return unpack(lib.pw_age(initial,steps,*increments,p.ctypes.data,pe.ctypes.data,tol.ctypes.data,max_knots))
    finally:lib.pw_free(initial)


def mean_idle(H,increments,keep,keep_error=F(0)):
    p,pe=probability(keep,keep_error);r=2*p[0]-1
    powers=np.r_[LD(1),np.cumprod(np.full(max(0,H-1),r,dtype=LD))]
    mean=LD(sum(increments))/2;amp=LD(increments[1]-increments[0])/2
    modes=[];error=LD(0)
    for m in (0,1):
        cumulative=np.cumsum(mean+(2*m-1)*amp*powers,dtype=LD)
        maxima=np.maximum.accumulate(np.maximum(LD(0),-cumulative))
        magnitude=LD(H)*(abs(mean)+abs(amp)+1)
        terr=8*LD(H)**2*abs(amp)*pe[0]+128*LD(H)*EPS*magnitude
        x=np.unique(np.r_[0,np.floor(maxima).astype(np.int64),np.ceil(maxima).astype(np.int64),int(np.ceil(maxima[-1]+terr))+1])
        prefix=np.r_[LD(0),np.cumsum(maxima,dtype=LD)]
        i=np.searchsorted(maxima,x,side='right')
        y=(prefix[-1]-prefix[i])-(H-i).astype(LD)*x.astype(LD)
        y[-1]=0
        modes.append((x,np.asarray(y,dtype=LD)))
        error=max(error,H*terr+256*LD(H)*EPS*(LD(H)*magnitude+1))
    return dict(modes=modes,error=error,peak_knots=max(len(x) for x,y in modes))
