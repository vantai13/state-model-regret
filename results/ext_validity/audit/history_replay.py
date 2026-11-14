"""Doan Van Tai — in-memory default-tau regression vs historically locked source.
No panel rerun, no project file changes; scientific toy outputs only.
"""
import json
import subprocess
import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from experiments.ext_validity import packet as current


def main():
    reports=[]
    for commit,cls in [('0abbd7f7','mmpp2'),('44b0284d','trace_cox')]:
        source=subprocess.check_output(['git','show',commit+':experiments/ext_validity/packet.py'],cwd=ROOT)
        ns={'__name__':'audit_historical_packet','__file__':str(ROOT/'experiments/ext_validity/packet.py')}
        exec(compile(source,commit+'/packet.py','exec'),ns)
        params=dict(kappa=.5) if cls=='mmpp2' else dict(series='results/ext_validity/ev_d2/series_c1.npz',bin=.01,key='s0')
        case=dict(id='audit_default_tau',cls=cls,params=params,lamA=6.,lamB=6.5,u=.25,
                  seed=773,warmup=1000.,train_T=500.,sample_dt=.2,h_mult=[3],n_inst=80,batches=4,spacing_mult=3)
        tr_old,tr_new=ns['train'](case),current.train(case)
        def clean(d): return {k:v for k,v in d.items() if k not in ('CPU','wall')}
        same_train=clean(tr_old)==clean(tr_new)
        # Frozen identity estimator makes this a kernel control independent of
        # training quality of the tiny, deliberately short training trajectory.
        tr=dict(s_train=.25,T_int=1.,nowcast={p:dict(beta=[0.,1.,0.],gamma=[0.,1.,0.]) for p in ('A','B')})
        old,new=ns['simulate'](case,3.,tr),current.simulate(case,3.,tr)
        same_test=clean(old)==clean(new)
        reports.append(dict(commit=commit,cls=cls,default_tau_train_bitwise=same_train,
                            default_tau_test_bitwise=same_test))
        assert same_train and same_test
    out=Path(__file__).resolve().parent
    (out/'history_replay.json').write_text(json.dumps(reports,indent=2)+'\n')
    print(json.dumps(reports,indent=2))


if __name__=='__main__': main()
