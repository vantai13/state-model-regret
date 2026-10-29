"""Vector spectral evaluation with forward error bounds and a separate moment bound.

The 80-digit infinite-law certificate remains authoritative. Integer powers use
explicit multiplications, not an unqualified complex libm power. No dense PMF,
finite physical buffer, tail renormalization or fluid-law substitution is used.
"""
from fractions import Fraction as F
import numpy as np
import mpmath as mp
from smr.stationary_spectral import upper,lower
from .piecewise import LD,EPS,number

INF=LD('inf');TINY=np.sqrt(np.nextafter(LD(0),LD(1)))


def up(x):return np.nextafter(np.asarray(x,dtype=LD)*(1+32*EPS)+TINY,INF)


def norm(z):return up(np.sqrt(z.real*z.real+z.imag*z.imag))


def multiply(a,ea,b,eb):
    na,nb=norm(a),norm(b);v=a*b
    error=up(na*eb+nb*ea+ea*eb+32*EPS*na*nb)
    return v,error


def represented(x):
    a,b=LD(x).as_integer_ratio();return mp.iv.mpf(a)/b


def convert(value):
    real=(lower(value.real)+upper(value.real))/2;imag=(lower(value.imag)+upper(value.imag))/2
    a,b=LD(str(real)),LD(str(imag));center=np.clongdouble(a)+np.clongdouble(1j)*b
    exact=mp.iv.mpc(represented(a),represented(b))
    radius=np.nextafter(LD(str(upper(abs(value-exact)))),INF)
    return center,radius


class FastLaw:
    def __init__(self,law):
        self._cdf_cache={}
        self._posterior_fallback_cache={}
        self.law=law;self.error=LD(str(2*law.error));self.terms,zero=law.intervals()
        self.r,self.er=map(np.array,zip(*(convert(t[0]) for t in self.terms)))
        self.c=[];self.ec=[];self.h=[];self.eh=[]
        for m in (0,1):
            c,ec=zip(*(convert(t[m+1]) for t in self.terms))
            h,eh=zip(*(convert(t[m+1]*t[0]/(1-t[0])) for t in self.terms))
            self.c.append(np.asarray(c,dtype=np.clongdouble));self.ec.append(np.asarray(ec,dtype=LD))
            self.h.append(np.asarray(h,dtype=np.clongdouble));self.eh.append(np.asarray(eh,dtype=LD))
        self.zero=[convert(v) for v in zero]
        self.r=np.asarray(self.r,dtype=np.clongdouble);self.er=np.asarray(self.er,dtype=LD)
        self.mean,self.mean_error=self._moment()

    def _moment(self):
        iv=mp.iv;K=self.law.plan['cutoff'];theta=iv.mpf(self.law.plan['theta']);pref=iv.mpf(self.law.plan['prefactor_upper'])
        exact=sum((a+b)*r/(1-r)**2 for r,a,b in self.terms)
        target_tail=iv.mpf(0)
        for r,a,b in self.terms:
            rho=abs(r)
            target_tail+=(abs(a)+abs(b))*rho**(K+1)*((K+1)/(1-rho)+rho/(1-rho)**2)
        true_tail=pref*iv.exp(-theta*K)*(K+1+1/(1-iv.exp(-theta)))
        # TV alone never bounds an unbounded moment: bound the finite part and
        # both complete moment tails independently before conversion.
        radius=2*K*iv.mpf(str(self.law.error))+true_tail+target_tail
        interval=exact.real+iv.mpf([-upper(radius),upper(radius)])
        center=LD(str((lower(interval)+upper(interval))/2))
        error=np.nextafter(LD(str(upper(abs(interval-represented(center))))),INF)
        return center,error

    def powers(self,indices):
        indices=np.asarray(indices,dtype=np.int64)
        if np.any(indices<0):raise ValueError('nonnegative powers only')
        q=indices.copy();shape=(len(q),len(self.r))
        result=np.ones(shape,dtype=np.clongdouble);error=np.zeros(shape,dtype=LD)
        base=np.broadcast_to(self.r,shape).copy();eb=np.broadcast_to(self.er,shape).copy()
        while np.any(q):
            active=(q&1).astype(bool)
            if np.any(active):result[active],error[active]=multiply(result[active],error[active],base[active],eb[active])
            q//=2
            if np.any(q):base,eb=multiply(base,eb,base,eb)
        return result,error

    def sum_terms(self,powers,power_errors,coefficients,coefficient_errors):
        values,error=multiply(powers,power_errors,coefficients,coefficient_errors)
        sums=values.real.sum(axis=1,dtype=LD)
        bound=up(error.sum(axis=1,dtype=LD)+64*len(self.r)*EPS*norm(values).sum(axis=1,dtype=LD))+self.error
        return sums,bound

    def cdf(self,indices):
        indices=np.atleast_1d(indices).astype(np.int64)
        missing=np.array([q for q in np.unique(indices) if int(q) not in self._cdf_cache],dtype=np.int64)
        if len(missing):
            values,errors=self._cdf_uncached(missing)
            self._cdf_cache.update({int(q):(v,e) for q,v,e in zip(missing,values,errors)})
        return (np.array([self._cdf_cache[int(q)][0] for q in indices],dtype=LD).reshape(-1,2),
                np.array([self._cdf_cache[int(q)][1] for q in indices],dtype=LD).reshape(-1,2))

    def _cdf_uncached(self,indices):
        indices=np.atleast_1d(indices).astype(np.int64);values=np.zeros((len(indices),2),dtype=LD);errors=np.zeros_like(values)
        for start in range(0,len(indices),16):
            stop=min(len(indices),start+16);q=indices[start:stop];power,ep=self.powers(np.maximum(0,q))
            for m in (0,1):
                tail,e=self.sum_terms(power,ep,self.h[m],self.eh[m]);center=LD('.5')-tail
                if np.any((center+e<0)|(center-e>LD('.5'))):raise ArithmeticError('CDF certificate violates probability bounds')
                projected=np.clip(center,LD(0),LD('.5'))
                values[start:stop,m]=np.where(q<0,LD(0),projected)
                errors[start:stop,m]=np.where(q<0,LD(0),up(e+abs(projected-center)+8*EPS))
        return values,errors

    def point(self,indices):
        indices=np.atleast_1d(indices).astype(np.int64);values=np.zeros((len(indices),2),dtype=LD);errors=np.zeros_like(values)
        for start in range(0,len(indices),16):
            stop=min(len(indices),start+16);q=indices[start:stop];power,ep=self.powers(q)
            for m in (0,1):
                val,e=self.sum_terms(power,ep,self.c[m],self.ec[m]);z,ez=self.zero[m]
                val=np.where(q==0,z.real,val);e=np.where(q==0,ez+self.error,e)
                if np.any(val+e<0):raise ArithmeticError('point certificate violates nonnegativity')
                projected=np.maximum(LD(0),val)
                values[start:stop,m]=projected;errors[start:stop,m]=up(e+abs(projected-val))
        return values,errors

    def posterior(self,indices):
        indices=np.atleast_1d(indices).astype(np.int64)
        p,e=self.point(indices);total=p.sum(axis=1);et=e.sum(axis=1)
        positive=total>et;center=np.zeros(len(indices),dtype=LD)
        error=np.full(len(indices),INF,dtype=LD)
        center[positive]=p[positive,1]/total[positive]
        low=np.maximum(LD(0),(p[positive,1]-e[positive,1])/(total[positive]+et[positive]))
        high=np.minimum(LD(1),(p[positive,1]+e[positive,1])/(total[positive]-et[positive]))
        error[positive]=up(np.maximum(center[positive]-low,high-center[positive])+32*EPS)
        # A large forward error in binary evaluation need not mean that the
        # conditioning event or posterior is uncertifiable. Use the original
        # 80-digit interval evaluator and its unchanged 1e-8 acceptance test.
        for i in np.flatnonzero(error>LD('1e-8')):
            q=int(indices[i])
            if q not in self._posterior_fallback_cache:
                value,bound=self.law.posterior(q)
                self._posterior_fallback_cache[q]=(LD(value),up(LD(bound)+32*EPS))
            center[i],error[i]=self._posterior_fallback_cache[q]
        if np.any(error>LD('1e-8')):raise ArithmeticError('fast posterior error exceeds1e-8')
        return center,error

    def quantiles(self,alphas,cap):
        targets=np.asarray(alphas,dtype=LD);lo=np.full(len(targets),-1,dtype=np.int64);hi=np.full(len(targets),int(cap),dtype=np.int64)
        for _ in range(64):
            if np.all(hi-lo<=1):break
            mid=(lo+hi)//2;c,e=self.cdf(mid);v=c.sum(axis=1)
            lower=v-e.sum(axis=1);upper_=v+e.sum(axis=1)
            active=hi-lo>1
            ambiguous=active&(lower<targets)&(upper_>=targets)
            if np.any(ambiguous):
                # A quadrature edge is a deterministic numerical choice, not a
                # claim that an ambiguous true quantile was uniquely certified.
                # Bin weights are later enclosed from CDF at the chosen edges.
                hi[ambiguous]=mid[ambiguous];active&=~ambiguous
            below=active&(v<targets);lo[below]=mid[below];hi[active&~below]=mid[active&~below]
        return hi
