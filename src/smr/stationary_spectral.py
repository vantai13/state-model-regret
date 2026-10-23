"""Doan Van Tai — spectral stationary approximation with interval residual certificate.

Roots are numerical proposals, never certificates. The infinite balance residual,
normalization and tails are bounded separately using outward interval arithmetic.
No array with one entry per tail index is required.
"""
from fractions import Fraction as F
import numpy as np
import mpmath as mp
from smr.stationary import tail_plan

DIGITS=80

def number(x):
    x=F(x); return mp.mpf(x.numerator)/x.denominator


def upper(x):
    return mp.mpf(x.b)


def lower(x):
    return mp.mpf(x.a)


class SpectralLaw:
    def __init__(self,increments,keep,keep_error=F(0)):
        mp.mp.dps=DIGITS; mp.iv.dps=DIGITS
        d,b=-increments[0],increments[1]
        self.plan=tail_plan(increments,keep,keep_error,tail_tol=1e-36)
        self.increments=increments;self.keep=F(keep);self.keep_error=F(keep_error)
        s=number(keep)
        poly=np.zeros(d+b+1);poly[0]=float(s);poly[b]=-float(2*s-1);poly[d]=-1;poly[-1]=float(s)
        f=lambda r:s*r**(d+b)-(2*s-1)*r**d-r**b+s
        derivative=lambda r:s*(d+b)*r**(d+b-1)-(2*s-1)*d*r**(d-1)-b*r**(b-1)
        roots=[]
        for z in np.roots(poly):
            if abs(z)<1-1e-9:
                r=mp.findroot(f,mp.mpc(z),df=derivative,solver='newton',tol=mp.mpf('1e-72'),maxsteps=200)
                if abs(r)<1-mp.mpf('1e-40') and all(abs(r-v)>mp.mpf('1e-40') for v in roots):roots.append(r)
        if len(roots)!=b:raise ArithmeticError(f'expected {b} stable roots, found {len(roots)}')
        v=[(1-s*r**d)*r**b/(1-s) for r in roots]
        matrix=mp.matrix(b);rhs=mp.matrix(b,1);rhs[b-1]=1
        for j in range(b):
            for i in range(b-1):matrix[i,j]=v[j]*roots[j]**(-i-1)
            matrix[b-1,j]=v[j]/(1-s)+(1+v[j])*roots[j]/(1-roots[j])
        c=mp.lu_solve(matrix,rhs)
        self.terms=[(r,cj,cj*vj) for r,cj,vj in zip(roots,c,v)]
        on=sum(cj*vj for cj,vj in zip(c,v));self.zero=(on*s/(1-s),on)
        self.certificate=self.certify()
        self.error=mp.mpf(self.certificate['infinite_law_error_upper'])

    def intervals(self):
        # Decimal strings are exact interval inputs; parameters are these rounded
        # decimal numbers. Every evaluation error is enclosed by iv arithmetic.
        def ivz(z):return mp.iv.mpc(mp.nstr(z.real,DIGITS),mp.nstr(z.imag,DIGITS))
        return [(ivz(r),ivz(a),ivz(b)) for r,a,b in self.terms],tuple(ivz(v) for v in self.zero)

    def certify(self):
        d,b=-self.increments[0],self.increments[1];terms,zero=self.intervals()
        iv=mp.iv
        s=iv.mpf(self.keep.numerator)/self.keep.denominator
        e=iv.mpf(self.keep_error.numerator)/self.keep_error.denominator
        s=iv.mpf([lower(s-e),upper(s+e)])
        def pm(q,m):return zero[m] if q==0 else sum(t[m+1]*t[0]**q for t in terms)
        residual=iv.mpf(0)
        incoming=sum(pm(q,0) for q in range(d+1))
        residual+=abs(zero[0]-s*incoming)+abs(zero[1]-(1-s)*incoming)
        for q in range(1,b+1):
            arrival_on=pm(q-b,1) if q==b else iv.mpc(0)
            residual+=abs(pm(q,0)-s*pm(q+d,0)-(1-s)*arrival_on)
            residual+=abs(pm(q,1)-(1-s)*pm(q+d,0)-s*arrival_on)
        total=zero[0]+zero[1];tail=iv.mpf(0);K=self.plan['cutoff']
        for r,a,on in terms:
            radius=abs(r)
            if upper(radius)>=1:raise ArithmeticError('uncertified decaying root')
            residual+=(abs(a-s*a*r**d-(1-s)*on*r**(-b))+
                       abs(on-(1-s)*a*r**d-s*on*r**(-b)))*radius**(b+1)/(1-radius)
            total+=(a+on)*r/(1-r)
            tail+=(abs(a)+abs(on))*radius**(K+1)/(1-radius)
        norm=abs(total-1);true_tail=iv.mpf(self.plan['tail_bound'])
        # Explicit Bellman supersolution to hit (0,off) in the capped chain.
        center=iv.mpf(self.keep.numerator)/self.keep.denominator
        B=(d+b)/(2*(1-center));C=d/(center-e);drift=iv.mpf(d-b)/2-e*B
        if lower(drift)<=0:raise ArithmeticError('return bound has no positive drift')
        T=(K+B+C)/drift
        error=(1+2*T)*(true_tail+tail+norm)+T*residual
        bound=upper(error)
        if bound>mp.mpf('1e-10'):raise ArithmeticError(f'spectral certificate fails: {bound}')
        return dict(method='spectral_interval_residual',digits=DIGITS,**self.plan,
                    approximate_tail_upper=str(upper(tail)),normalization_error_upper=str(upper(norm)),
                    residual_tv_upper=str(upper(residual)/2),return_time_upper=str(upper(T)),
                    infinite_law_error_upper=str(bound),stored_terms=len(terms),physical_buffer=False)

    def point_interval(self,q):
        if type(q) is not int or q<0:raise ValueError('nonnegative integer q')
        terms,zero=self.intervals()
        return zero if q==0 else tuple(sum(t[m+1]*t[0]**q for t in terms) for m in (0,1))

    def cdf_interval(self,q):
        if q<0:return mp.iv.mpf(0)
        terms,zero=self.intervals()
        return (zero[0]+zero[1]+sum((a+b)*r*(1-r**q)/(1-r) for r,a,b in terms)).real

    def quantile(self,alpha):
        alpha=number(alpha);lo=-1;hi=self.plan['cutoff']
        while hi-lo>1:
            mid=(lo+hi)//2
            if upper(self.cdf_interval(mid))<alpha:lo=mid
            else:hi=mid
        if upper(self.cdf_interval(hi-1))+self.error>=alpha or lower(self.cdf_interval(hi))-self.error<alpha:
            raise ArithmeticError('quantile not uniquely certified')
        return hi

    def posterior(self,q):
        a,b=self.point_interval(q);p=(a+b).real;low=lower(p)-self.error
        if low<=0:raise ArithmeticError('conditioning event not certified')
        ratio=b.real/p;error=2*self.error/low+upper(ratio)-lower(ratio)+mp.mpf('4e-16')
        if error>mp.mpf('1e-8'):raise ArithmeticError('posterior certificate fails')
        return float((upper(ratio)+lower(ratio))/2),float(error)

    def mass(self,N):
        # Reference comparisons only. This array conversion has its own roundoff
        # bound; the certificate describes the interval spectral law.
        q=np.arange(1,N+1,dtype=np.longdouble);out=np.zeros((N+1,2),dtype=np.longdouble)
        out[0]=[np.longdouble(str(mp.re(z))) for z in self.zero]
        for r,a,b in self.terms:
            root=np.clongdouble(str(r.real))+1j*np.clongdouble(str(r.imag))
            power=np.cumprod(np.full(N,root,dtype=np.clongdouble))
            for m,v in enumerate((a,b)):
                c=np.clongdouble(str(v.real))+1j*np.clongdouble(str(v.imag))
                out[1:,m]+=(c*power).real
        return out
