"""Reproduce lesson design tables with frozen exact functions. No discovery I/O."""
import csv
from fractions import Fraction as F
from pathlib import Path

from experiments.R3R_06_cards import stats,verdict
from experiments.R3R_07_confirmation import power
from experiments.P4_03_map_audit.common import ROOT,sha,write_once
from .identity_checks import fixtures


OUT=Path('results/lessons/l4_5/design')


def minimum_p(*,two_regions,r_plus=F(0),r_minus=F(0)):
    """Exact-rational bracket of width < 1e-7 for planning power >= 1/2."""
    lo,hi=F(0),F(1)
    for _ in range(24):
        mid=(lo+hi)/2
        value=(power.robust_pass_power(60,mid,F(1,5),r_plus,r_minus) if two_regions
               else power.robust_region_power(60,mid,r_plus,plus=True))
        if value>=F(1,2):hi=mid
        else:lo=mid
    return dict(lower=str(lo),upper=str(hi),lower_float=float(lo),upper_float=float(hi),
                width=float(hi-lo),r_plus=str(r_plus),r_minus=str(r_minus),p_minus='1/5' if two_regions else None)


def plain(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [plain(v) for v in x]
    return x


def main():
    destination=ROOT/OUT
    if destination.exists():raise FileExistsError('design outputs already exist')
    no_u=[]
    for p in (F(3,5),F(13,20),F(7,10),F(3,4),F(4,5)):
        two=power.pass_power(60,p,F(1,5));one=verdict.plus_power(60,p)
        if power.robust_pass_power(60,p,F(1,5),0,0)!=two:raise RuntimeError('r0 two-region mismatch')
        if power.robust_region_power(60,p,0,plus=True)!=one:raise RuntimeError('r0 one-region mismatch')
        no_u.append(dict(p_plus=float(p),two_region_power=float(two),one_region_power=float(one)))
    unresolved=[dict(p_cond=float(p),r=float(r),one_region_power=float(power.robust_region_power(60,p,r,plus=True)))
                for p in (F(7,10),F(3,4),F(4,5)) for r in (F(0),F(1,20),F(1,10))]
    r5=[dict(r=float(r),probability_R5_fails=float(power.r5_failure(60,r))) for r in (F(1,20),F(2,25))]
    thresholds={f'{design}_r{r}':minimum_p(two_regions=design=='SV',r_plus=r,r_minus=r)
                for design in ('SV','SUB') for r in (F(0),F(1,20))}
    support=stats.k_support(60,F(1,2),F(1,40));reject=stats.k_reject(60,F(1,2),F(1,40))
    if (support,reject)!=(39,21):raise RuntimeError('n60 cutoffs changed')
    expected_two=(.256,.558,.836,.968,.996);expected_one=(.257,.559,.838,.970,.998)
    checks=[abs(row['two_region_power']-a)<.0006 and abs(row['one_region_power']-b)<.0006
            for row,a,b in zip(no_u,expected_two,expected_one)]
    expected_u=(.838,.645,.331,.970,.867,.500,.998,.955,.586)
    checks += [abs(row['one_region_power']-e)<.0006 for row,e in zip(unresolved,expected_u)]
    if not all(checks):raise RuntimeError('lesson table mismatch')
    destination.mkdir(parents=True)
    for name,rows in [('power_no_unresolved.csv',no_u),('power_with_unresolved.csv',unresolved),('R5_failure.csv',r5)]:
        with (destination/name).open('x',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    write_once(destination/'identity_fixtures.json',plain(fixtures()))
    summary=dict(responsible='Doan Van Tai',type='HYPOTHETICAL_EXACT_DESIGN_NOT_DISCOVERY',
                 n=60,alpha='1/40',pi0='1/2',plus_support_min=39,minus_reject_max=21,
                 table_rows_matched=len(checks),all_table_rows_match=True,min_p_for_half_power=thresholds,
                 R5=r5,real_boxes_evaluated=0,engine_calls=0,CF_outcomes=0,
                 assumptions=['i.i.d. categorical/binomial draws for each hypothetical region',
                              'p is conditional MEETS among resolved; r is unresolved probability',
                              'UNDEFINED=0','two-region product assumes independent region samples',
                              'frozen docstring additionally states U independent of latent label; this run does not verify that in native data'],
                 source_sha256={p:sha(ROOT/p) for p in ['experiments/R3R_07_confirmation/power.py','experiments/R3R_06_cards/verdict.py','experiments/R3R_06_cards/stats.py']})
    write_once(destination/'summary.json',summary)
    write_once(destination/'manifest.json',dict(script_sha256=sha(__file__),outputs_sha256={p.name:sha(p) for p in destination.iterdir()}))
    print({k:summary[k] for k in ('plus_support_min','minus_reject_max','table_rows_matched','engine_calls','real_boxes_evaluated')},flush=True)
    print('minimum p planning brackets:',thresholds,flush=True)


if __name__=='__main__':main()
