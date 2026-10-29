"""Experimental double-precision proposals for the sparse four-term polynomial.

These are proposals ONLY: the existing 80-digit refinement, required stable-root
count and unchanged interval residual certificate remain mandatory downstream.
No random seeds, no coarser queue lattice, no change to the stationary equations.
"""
import numpy as np


def stable_root_proposals(d,b,s,*,iterations=160):
    if not (isinstance(d,int) and isinstance(b,int) and d>b>0 and .5<=s<1):
        raise ValueError('d>b>0, .5<=keep<1 required')
    n=d+b;found=[]
    for radial in (1.,2.,.5,4.):
        for offset in (0.,.25,-.25):
            angles=2*np.pi*(np.arange(b)+offset)/b
            z=np.exp(radial*np.log(s)/b+1j*angles)
            for _ in range(iterations):
                zn,zd,zb=z**n,z**d,z**b
                f=s*zn-(2*s-1)*zd-zb+s
                df=(s*n*zn-(2*s-1)*d*zd-b*zb)/z
                step=np.divide(f,df,out=np.zeros_like(z),where=np.abs(df)>1e-280)
                length=np.abs(step)
                step*=np.minimum(1.,(.75/b)/np.maximum(length,1e-300))
                z-=step
                radius=np.abs(z)
                z*=np.minimum(1.,(1+2/n)/np.maximum(radius,1e-300))
                if np.max(np.abs(step))<2e-13:break
            residual=np.abs(s*z**n-(2*s-1)*z**d-z**b+s)
            good=(np.abs(z)<1-1e-9)&(residual<1e-9)&np.isfinite(z)
            found.extend(z[good])
            if found:
                ordered=sorted(found,key=lambda r:(np.angle(r),abs(r)))
                unique=[]
                for r in ordered:
                    if not unique or abs(r-unique[-1])>1e-7:
                        unique.append(r)
                if len(unique)>1 and abs(unique[0]-unique[-1])<=1e-7:unique.pop()
                found=unique
                if len(found)==b:return np.asarray(found)
    if len(found)!=b:
        raise ArithmeticError(f'proposal search found {len(found)} distinct stable candidates, expected {b}')
    return np.asarray(found)
