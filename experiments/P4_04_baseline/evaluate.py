"""Capture actual arrays in one frozen evaluation, then add margin outputs.

Each worker is an independent process; the temporary side wrapper only retains
its unchanged return value and is restored before returning or on exceptions.
"""
from fractions import Fraction as F
import time

import numpy as np

from .margin import pair_loss_margin, significant_bits, LD, EPS, number
from .common import RHOS, require


def add_baselines(row, sides, h):
    from experiments.R3R_08_population_numerics.population import pair_loss
    require(len(sides) == 2, 'side capture did not return A/B')
    A,B=sides
    base=number(h)*(A['mean']+B['mean'])
    ebase=abs(number(h))*(A['mean_error']+B['mean_error'])+128*EPS*(abs(base)+1)
    require(base>=0, 'negative Stay scale')
    outputs=[]
    for rho in RHOS:
        r=number(F(rho));theta=r*base
        etheta=r*ebase+(64*EPS*(abs(theta)+1) if r else LD(0))
        costs={};errors={};ambiguity={}
        for key,kind in (('00','old'),('10','current')):
            arrays=(A[kind],B[kind])
            gap,err,amb=pair_loss_margin(*arrays,theta=theta,theta_error=etheta)
            loss=base+gap
            error=ebase+err+64*EPS*(abs(base)+abs(gap)+1)
            require(loss+error >= LD(row['losses']['11'])-LD(row['cost_error']['11']), 'margin beats oracle outside arithmetic error')
            if r==0:
                original=pair_loss(*arrays,model='mean')
                for x,y in zip((gap,err),original[:2]):
                    require(significant_bits(x)==significant_bits(y), 'theta0 pair_loss bit mismatch')
                require(amb==original[2], 'theta0 ambiguity mismatch')
                require(significant_bits(loss)==significant_bits(LD(row['losses'][key])), 'theta0 cell bit mismatch')
                require(significant_bits(error)==significant_bits(LD(row['cost_error'][key])), 'theta0 error bit mismatch')
                require(amb==row['uncertain_action_mass'][key], 'theta0 cell ambiguity mismatch')
            costs[key]=loss;errors[key]=error;ambiguity[key]=amb
        gs=costs['00']-costs['10'];delta=costs['10']-LD(row['losses']['10'])
        gm=LD(row['G_M']);gm_error=LD(row['contrast_error']['G_M'])
        recovery=(LD(row['losses']['00'])-costs['00'])/gm if gm>0 else None
        outputs.append(dict(rho=rho,theta=str(theta),theta_error=str(etheta),
                            L00=str(costs['00']),L10=str(costs['10']),
                            error00=str(errors['00']),error10=str(errors['10']),
                            GS_theta=str(gs),GS_theta_error=str(errors['00']+errors['10']),
                            deltaL10=str(delta),deltaL10_error=str(errors['10']+LD(row['cost_error']['10'])),
                            R_M=None if recovery is None else str(recovery),
                            R_M_denominator_certified=bool(gm>gm_error),
                            R_M_undefined=bool(gm<=0),uncertain_action_mass=ambiguity))
    # Very large margin checks Stay on the same actual arrays. It is not tuned.
    for kind in ('old','current'):
        theta=max(abs(A[kind]['h']))+max(abs(B[kind]['h']))+LD(1)
        gap,_,_=pair_loss_margin(A[kind],B[kind],theta=theta)
        require(gap==0 and base+gap==base, 'large margin did not equal Stay')
    if row['zero_action_certificate']:
        require(all(LD(v)==base for v in row['losses'].values()), 'u0 original cells differ')
        require(all(LD(b[k])==base for b in outputs for k in ('L00','L10')), 'u0 baseline cells differ')
    row.update(Stay=str(base),Stay_error=str(ebase),baseline=outputs,
               baseline_sanity_pass=True,baseline_sanity=dict(theta0_bits=True,large_margin_stay=True,
                   oracle_bound=True,zero_action_real=bool(row['zero_action_certificate'])))
    return row


def evaluate_level(case, level, cache):
    from experiments.R3R_14_lean_close import engine
    from experiments.R3R_08_population_numerics import population
    engine.configure()
    sides=[];original=population.side
    def capture(*args,**kwargs):
        result=original(*args,**kwargs);sides.append(result);return result
    begin_cpu=engine.cpu_seconds();begin=time.monotonic()
    population.side=capture
    try:
        row=engine.evaluate_level(case['id'],case['parameters'],*level,cache)
    finally:
        population.side=original
    try:
        row=add_baselines(row,sides,F(case['parameters'][4]))
    except Exception as exc:
        # Keep the actual frozen-native row even when a new sanity check fails.
        row.update(baseline_sanity_pass=False,error=f'{type(exc).__name__}: {exc}')
    row['native_only_cpu_seconds']=row['call_cpu_seconds']
    row['call_cpu_seconds']=engine.cpu_seconds()-begin_cpu
    row['call_wall_seconds']=time.monotonic()-begin
    row['baseline_added_cpu_seconds']=row['call_cpu_seconds']-row['native_only_cpu_seconds']
    return row
