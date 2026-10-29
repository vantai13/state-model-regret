"""Same spectral equations and unchanged interval certificate; eliminate dense LU.

Numerical proposals are still rejected by the original infinite-law certificate.
No queue-grid coarsening, model change or altered tolerance. Candidate only.
"""
from fractions import Fraction as F
import mpmath as mp
import numpy as np

from smr.stationary import tail_plan
from smr.stationary_spectral import SpectralLaw as ReferenceLaw,number,DIGITS


def barycentric_coefficients(roots,v,s):
    """Null vector of the first b-1 Vandermonde equations, then normalize.

    w_j=1/P'(r_j) has sum(w_j*r_j**k)=0 for k=0..b-2. Hence
    c_j proportional to r_j**(b-1)/(v_j*P'(r_j)), followed by the *same*
    normalization row as ReferenceLaw. O(b²) operations, O(b) storage.
    """
    b=len(roots)
    if b==0 or len(v)!=b:raise ValueError('nonempty aligned roots/v required')
    derivatives=[mp.mpc(1) for _ in roots]
    for i in range(b):
        for j in range(i):
            difference=roots[i]-roots[j]
            if not difference:raise ArithmeticError('distinct roots required')
            derivatives[i]*=difference
            derivatives[j]*=-difference
    raw=[r**(b-1)/(vj*dj) for r,vj,dj in zip(roots,v,derivatives)]
    normalizer=mp.fsum(cj*(vj/(1-s)+(1+vj)*r/(1-r)) for cj,r,vj in zip(raw,roots,v))
    if not normalizer:raise ArithmeticError('normalization row is singular')
    return [cj/normalizer for cj in raw]


class BarycentricLaw(ReferenceLaw):
    """Drop only the dense coefficient solve; keep root proposals/certificate."""
    def __init__(self,increments,keep,keep_error=F(0)):
        mp.mp.dps=DIGITS;mp.iv.dps=DIGITS
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
        c=barycentric_coefficients(roots,v,s)
        self.terms=[(r,cj,cj*vj) for r,cj,vj in zip(roots,c,v)]
        on=mp.fsum(cj*vj for cj,vj in zip(c,v));self.zero=(on*s/(1-s),on)
        self.certificate=self.certify()
        self.error=mp.mpf(self.certificate['infinite_law_error_upper'])
