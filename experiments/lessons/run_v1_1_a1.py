"""Doan Van Tai — A1, all 20 stationary certificates without action costs."""
import resource,time
from fractions import Fraction as F
from experiments.lessons.v1_1_a_common import *
from smr.stationary_v2 import stationary_two_mode_v2
from smr.stationary import stationary_two_mode,r2_keep
from smr.stationary_spectral import SpectralLaw
import numpy as np

def run():
    out=ROOT/'results/lessons/v1_1_a1';out.mkdir(parents=True,exist_ok=True)
    if (out/'certificates.csv').exists():raise SystemExit('preserve existing A1 evidence')
    write(out/'config.json',dict(author='Doan Van Tai',memory_limit_bytes=4*1024**3,seconds_per_certificate=1200,
        law_target=1e-10,posterior_target=1e-8,spectral_tail_target=1e-36,parameters=parameters(),levels=[1,2],rng_draws=0))
    sparse=[]
    for inc,s in [((-2,1),F(3,4)),((-17,7),F(99,100))]:
        start=time.monotonic();_,c=stationary_two_mode_v2(inc,s)
        sparse.append(dict(increments=inc,keep=s,wall_s=time.monotonic()-start,**c))
    write(out/'sparse_trials.json',sparse)
    rows=[]
    for index,(lam,k,eta) in enumerate(parameters(),1):
        for ref in (1,2):
            start=time.monotonic();u=2*eta;unit,A=law_for(lam,u,k,ref);ub,B=law_for(F(8),F(0),k,ref)
            values={};bounds=[]
            for name,law,quantum in [('A',A,unit),('B',B,ub)]:
                for alpha in (F(1,2),F(9,10)):
                    q=law.quantile(alpha);p,e=law.posterior(q);values[f'{name}{int(alpha*100)}']=q*quantum;bounds.append(e)
            elapsed=time.monotonic()-start;rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
            assert elapsed<=1200 and rss<=4*1024**3
            rows.append(dict(set=index,lambdaA=lam,kappa=k,eta=eta,refinement=ref,dt=F(1,120*ref),
                A_certificate_cutoff=A.plan['cutoff'],B_certificate_cutoff=B.plan['cutoff'],
                law_error_A=A.certificate['infinite_law_error_upper'],law_error_B=B.certificate['infinite_law_error_upper'],
                posterior_bound_max=max(bounds),wall_s=elapsed,peak_rss_bytes=rss,status='PASS',**values))
            write(out/f'certificate_{index:02}_{ref}.json',dict(A=A.certificate,B=B.certificate))
            print(f'A1 {index}/10 dt=1/{120*ref} PASS {elapsed:.3f}s RSS={rss/2**20:.1f}MiB',flush=True)
    csvwrite(out/'certificates.csv',rows)
    # Ten v1 comparisons requested: five references and five parameter cases.
    specs=[((-2,1),F(1,2),F(0)),((-2,1),F(3,4),F(0)),((-2,1),F(9,10),F(0)),
           ((-5,3),F(3,4),F(0)),((-2,1),*r2_keep(F(1,120),F(3,10)))]
    for lam,k in ((F(13,2),F(3,10)),(F(15,2),F(3,10)),(F(15,2),F(1)),(F(13,2),F(1)),(F(13,2),F(3))):
        _,inc=lattice((lam-6,lam+6),F(1),F(1,120));specs.append((inc,*r2_keep(F(1,120),k)))
    comparisons=[]
    for i,(inc,s,e) in enumerate(specs,1):
        start=time.monotonic();old,cert=stationary_two_mode(inc,s,e,cap_limit=300000)
        new=SpectralLaw(inc,s,e);approx=new.mass(len(old)-1)
        difference=float(np.sum(abs(approx-old),dtype=np.longdouble)/2)
        # Conservative array-evaluation allowance; posterior uses interval law.
        absolute=sum(float(abs(a)+abs(b))*float(abs(r))/(1-float(abs(r))) for r,a,b in new.terms)+sum(float(abs(z)) for z in new.zero)
        allowance=200*len(old)*float(np.finfo(np.longdouble).eps)*absolute
        bound=float(cert['infinite_law_error_upper'])+float(new.error)+allowance
        assert difference<=bound
        comparisons.append(dict(case=i,cap=len(old)-1,observed_TV=difference,v1_error=cert['infinite_law_error_upper'],
            spectral_error=str(new.error),array_evaluation_allowance=allowance,bound=bound,wall_s=time.monotonic()-start,status='PASS'))
        print(f'v1 comparison {i}/10 PASS',flush=True)
    csvwrite(out/'v1_comparisons.csv',comparisons);manifest(out)
if __name__=='__main__':run()
