"""Doan Van Tai — stationary-only engine diagnostic, no action/decision costs."""
import argparse
from fractions import Fraction as F
import json
import math
from pathlib import Path

import mpmath as mp
from smr.cells import law_for
from experiments.R3R_04_realism.implied import fluid_queue,delay_exceedance
from experiments.R3R_04_realism.run_screen import verify_freeze,designs,write_csv


def main():
    p=argparse.ArgumentParser();p.add_argument('--freeze',required=True);args=p.parse_args()
    commit,spec,_=verify_freeze(args.freeze)
    chosen=spec['stationary_check'];rows={r['id']:r for r in designs(spec)};results=[]
    for rid in chosen['ids']:
        row=rows[rid];T=F(row['kappa']);threshold=chosen['delay_threshold_over_T']*T
        for which in chosen['queues']:
            lam=F(row['lambdaA'] if which=='A_pre' else row['lambdaB'])
            u=F(row['u']) if which=='A_pre' else F(0)
            reference=fluid_queue(float(lam+u),6,10,float(T))
            for ref in chosen['refs']:
                unit,law=law_for(lam,u,T,ref)
                atom=float(mp.re(sum(law.zero)))
                mean=float(mp.re(sum((a+b)*r/(1-r)**2 for r,a,b in law.terms)))*float(unit)/10
                cutoff=math.floor(threshold*10/unit)
                tail=float(mp.re(sum((a+b)*r**(cutoff+1)/(1-r) for r,a,b in law.terms)))
                ct=delay_exceedance(reference,10,float(threshold))
                results.append(dict(id=rid,queue=which,ref=ref,base_tau_s=1,T_s=float(T),
                                    atom_slotted=atom,atom_fluid=reference['atom_zero'],
                                    abs_atom_delta=abs(atom-reference['atom_zero']),
                                    mean_virtual_delay_slotted_s=mean,mean_virtual_delay_fluid_s=reference['virtual_delay_time_mean_s'],
                                    abs_mean_delta_s=abs(mean-reference['virtual_delay_time_mean_s']),
                                    tail_slotted=tail,tail_fluid=ct,abs_tail_delta=abs(tail-ct),
                                    tail_threshold_s=float(threshold),law_TV_error_upper=str(law.error),
                                    mean_is_unbounded_moment_estimate=True))
    out=Path('results/lessons/l3r_4/stationary');write_csv(out/'comparisons.csv',results)
    summary=dict(owner=spec['owner'],freeze_commit=commit,rows=len(results),ids=chosen['ids'],
                 scope='stationary only; continuous approximation is not exact slotted law; mean lacks certified moment bound',
                 no_J_gap_decision_regret_or_contrast_computed=True,
                 max_abs_atom_delta=max(r['abs_atom_delta'] for r in results),
                 max_abs_mean_delta_s=max(r['abs_mean_delta_s'] for r in results),
                 max_abs_tail_delta=max(r['abs_tail_delta'] for r in results))
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
