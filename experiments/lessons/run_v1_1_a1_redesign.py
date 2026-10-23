"""Doan Van Tai — prior-only certificates for the one preregistered redesign."""
from experiments.lessons.v1_1_a_common import *
import argparse,time,resource


def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if (out/'certificates.csv').exists():raise SystemExit('preserve certificates; select fresh --output-dir')
    rows=[]
    write(out/'config.json',dict(author='Doan Van Tai',preregistration='19d03cc',levels=['7','7.2','8.1'],center='7.2',redesign_count=1,
        law_target=1e-10,posterior_target=1e-8,memory_limit=4*1024**3,seconds=1200,no_J=True))
    params=[(a,k,F(1,2)) for a in (F(7),F(36,5),F(81,10)) for k in (F(3,10),F(1),F(3))]+[(F(36,5),F(1),F(9,10))]
    for i,(a,k,eta) in enumerate(params,1):
        for ref in (1,2):
            start=time.monotonic();u,A=law_for(a,2*eta,k,ref);ub,B=law_for(F(8),F(0),k,ref);errors=[];values={}
            for name,law,unit in [('A',A,u),('B',B,ub)]:
                for alpha in (F(1,2),F(9,10)):
                    q=law.quantile(alpha);_,e=law.posterior(q);errors.append(e);values[f'{name}{int(alpha*100)}']=q*unit
            rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;elapsed=time.monotonic()-start
            assert rss<4*1024**3 and elapsed<1200
            rows.append(dict(set=i,lambdaA=a,kappa=k,eta=eta,refinement=ref,law_error_A=str(A.error),law_error_B=str(B.error),
                posterior_bound=max(errors),wall_s=elapsed,peak_rss_bytes=rss,status='PASS',**values))
            write(out/f'certificate_{i:02}_{ref}.json',dict(A=A.certificate,B=B.certificate))
            print(i,ref,'PASS',flush=True)
    csvwrite(out/'certificates.csv',rows);manifest(out)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=ROOT/'results/lessons/v1_1_a1_redesign');run(p.parse_args().output_dir)
