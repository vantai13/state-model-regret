"""80-digit spectral proposals with linear-time duplicate checks and dyadic products."""
from fractions import Fraction as F
import mpmath as mp
from smr.stationary import tail_plan
from smr.stationary_spectral import SpectralLaw,number,lower,upper
from experiments.R3R_07_fast_stationary.root_proposal import stable_root_proposals
from .dyadic import products
from .native_certificate import native_certificate


class NativeLaw(SpectralLaw):
    def __init__(self,increments,keep,keep_error=F(0),progress=lambda *a,**k:None):
        mp.mp.dps=80;mp.iv.dps=80
        d,b=-increments[0],increments[1];s=number(keep)
        self.increments=increments;self.keep=F(keep);self.keep_error=F(keep_error)
        self.plan=tail_plan(increments,keep,keep_error,tail_tol=1e-36)
        polynomial=lambda r:s*r**(d+b)-(2*s-1)*r**d-r**b+s
        derivative=lambda r:s*(d+b)*r**(d+b-1)-(2*s-1)*d*r**(d-1)-b*r**(b-1)
        roots=[];buckets={};tolerance=mp.mpf('1e-40')
        for z in stable_root_proposals(d,b,float(s)):
            r=mp.findroot(polynomial,mp.mpc(z),df=derivative,solver='newton',tol=mp.mpf('1e-72'),maxsteps=200)
            if abs(r)>=1-tolerance:continue
            ix,iy=int(mp.floor(r.real/tolerance)),int(mp.floor(r.imag/tolerance))
            if any(abs(r-v)<=tolerance for dx in (-1,0,1) for dy in (-1,0,1) for v in buckets.get((ix+dx,iy+dy),())):continue
            roots.append(r);buckets.setdefault((ix,iy),[]).append(r)
        if len(roots)!=b:raise ArithmeticError(f'expected{b} stable roots; got{len(roots)}')
        progress('native_roots_refined',roots=b)
        self._derivatives=products(roots)
        self._derivative_roots=tuple((mp.nstr(r.real,80),mp.nstr(r.imag,80)) for r in roots)
        progress('native_derivative_products_completed',roots=b)
        v=[(1-s*r**d)*r**b/(1-s) for r in roots]
        center=lambda z:mp.mpc((lower(z.real)+upper(z.real))/2,(lower(z.imag)+upper(z.imag))/2)
        raw=[r**(b-1)/(vj*center(dp)) for r,vj,dp in zip(roots,v,self._derivatives)]
        norm=sum(c*(vj/(1-s)+(1+vj)*r/(1-r)) for c,r,vj in zip(raw,roots,v))
        c=[x/norm for x in raw];self.terms=[(r,cj,cj*vj) for r,cj,vj in zip(roots,c,v)]
        on=sum(cj*vj for cj,vj in zip(c,v));self.zero=(on*s/(1-s),on)
        self.certificate=self.certify();self.error=mp.mpf(self.certificate['infinite_law_error_upper'])

    def certify(self):return native_certificate(self)
