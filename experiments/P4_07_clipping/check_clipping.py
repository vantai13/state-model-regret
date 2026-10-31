"""Doan Van Tai — AI-assisted clipping checks; production source stays frozen.

Read-only cached native profiles. No population.evaluate, CF or SUB runner calls.
Run: python -m experiments.P4_07_clipping.check_clipping --out NEW_DIR
"""
import argparse
from collections import defaultdict
import csv
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
import resource
import signal
import time

import numpy as np

from experiments.P4_03_map_audit.common import ROOT, cf_keys, canonical
from experiments.R3R_08_population_numerics import piecewise as P

PROTOCOL = ROOT/'notes/lessons/L4.7_v2_protocol.json'


def cpu():
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time()+children.ru_utime+children.ru_stime


def require(ok, message):
    if not ok:
        raise ValueError(message)


def threshold(H, increments, mode):
    """Strict-reflection threshold when all transitions have positive mass.

    The first slot uses the known initial mode. Future slots may take the
    smallest increment. Works in physical packets or integer-lattice units.
    """
    require(type(H) is int and H > 0 and mode in (0,1), 'bad H/mode')
    first = F(increments[mode])
    return -min(F(0), first, first+(H-1)*min(map(F, increments)))


def exact_reference(H, increments, keep, q0, mode):
    """Finite-state rational Bellman reference, independent of native kernel."""
    keep, q0 = F(keep), F(q0)
    require(0 < keep < 1 and H > 0, 'invalid reference law')
    inc = tuple(map(F, increments))
    @lru_cache(None)
    def cost(t, q, m):
        if not t:
            return F(0)
        new_q = max(F(0), q+inc[m])
        return new_q+keep*cost(t-1,new_q,m)+(1-keep)*cost(t-1,new_q,1-m)
    return cost(H,q0,mode)


def rational_mean(H, increments, keep, q0, mode):
    """Forward reflected path, not an idle-profile implementation."""
    lo, hi = map(F, increments)
    q, total, r = F(q0), F(0), 2*F(keep)-1
    for k in range(H):
        increment = (lo+hi)/2+(2*mode-1)*(hi-lo)/2*r**k
        q = max(F(0), q+increment)
        total += q
    return total


def enumerate_example():
    """Reproduce supplied H10, 512-path example using the declared slot law."""
    dt, H, kappa = F(1,20), 10, F(3,10)
    p = (1+math.exp(-2*float(dt/kappa)))/2
    out = []
    for q0 in (5,1):
        for mode in (0,1):
            value = mass = 0.0
            for flips in itertools.product((0,1), repeat=H-1):
                q, m, weight, cost = float(q0), mode, 1., 0.
                for k in range(H):
                    if k:
                        flip = flips[k-1]
                        weight *= (1-p) if flip else p
                        m = 1-m if flip else m
                    q = max(0., q+(-7 if m==0 else 5)*float(dt))
                    cost += q*float(dt)
                mass += weight
                value += weight*cost
            q, mean = float(q0), 0.
            for k in range(H):
                q = max(0., q+(-1+(2*mode-1)*6*(2*p-1)**k)*float(dt))
                mean += q*float(dt)
            require(abs(mass-1) < 1e-12, 'enumeration mass !=1')
            outside = F(q0) >= threshold(H, (F(-7)*dt,F(5)*dt), mode)
            require(value+1e-12 >= mean, 'finite-path Jensen violation')
            require(not outside or abs(value-mean) < 1e-12, 'finite-path P-clip violation')
            out.append(dict(q0=q0,mode=mode,paths=2**(H-1),probability_mass=mass,
                            M1=value,M0=mean,M1_minus_M0=value-mean,outside=outside,
                            units='packet*s; dt=1/20, H=10, fixed initial mode'))
    return out


def load_inputs():
    protocol = json.loads(PROTOCOL.read_text())
    source = ROOT/protocol['input_csv']
    require(hashlib.sha256(source.read_bytes()).hexdigest()==protocol['input_csv_sha256'], 'L4.6 CSV changed')
    rows = {r['id']:r for r in csv.DictReader(source.open()) if r['engine']=='native'}
    cases = {}
    forbidden = cf_keys()
    for cid in set(protocol['part_B_ids']+protocol['part_C_ids']):
        r = rows[cid]
        path = ROOT/r['source']
        require(hashlib.sha256(path.read_bytes()).hexdigest()==r['source_sha256'], 'native row changed')
        raw = json.loads(path.read_text())
        require(raw['CF_computed'] is False and raw['status']=='COMPLETED', 'not a completed discovery row')
        require(canonical(raw['parameters']) not in forbidden, 'CF collision')
        cases[cid] = dict(meta=r,raw=raw,cache=path.parents[2]/'native_cache')
    return protocol, cases


def cached_side(case, which):
    """Use the exact saved profile/law keys, refusing any cache miss."""
    from experiments.R3R_08_population_numerics import law_cache, profiles
    raw, cache = case['raw'], case['cache']
    a,b,kappa,eta,h,_ = map(F,raw['parameters'])
    lam,pre,post = (a,2*eta,F(0)) if which=='A' else (b,F(0),2*eta)
    expected = raw['source_components'][which]
    for rel in (f'stationary/{expected["law_key"]}.json', f'stationary/{expected["law_key"]}.sha256',
                f'profiles/{expected["profile_key"]}.json', f'profiles/{expected["profile_key"]}.npz'):
        require((cache/rel).exists(), 'cache missing; refuse recomputation: '+str(cache/rel))
    unit,law,key = law_cache.get(lam,pre,kappa,raw['ref'],cache/'stationary')
    require(key==expected['law_key'] and law.last_creation_cpu_seconds==0, 'wrong/new stationary cache')
    costs = profiles.get(lam,pre,post,kappa,h,raw['ref'],unit,cache/'profiles',
                         cost_budget=min(F(1,10000),h*h/F(10_000_000)))
    require(costs['key']==expected['profile_key'] and costs['created_cpu_seconds']==0, 'wrong/new cost profile')
    return dict(unit=unit,law=law,costs=costs,lam=lam,pre=pre,post=post,h=h,ref=raw['ref'])


def state_checks(cid, case):
    """48 planned state rows overall; true/mean cost checked per action."""
    from experiments.R3R_08_population_numerics import profiles
    rows = []
    for which in ('A','B'):
        side = cached_side(case,which)
        unit,costs = side['unit'],side['costs']
        H,dt = costs['H'],F(costs['dt'])
        incs = (tuple(costs['increments_st']),tuple(costs['increments_sw']))
        scale = P.LD(costs['scale'])
        # Mean idle profiles are fast and do not construct new physical kernels.
        keep = side['law'].law.keep
        ke = side['law'].law.keep_error
        means = [P.mean_idle(H,inc,keep,ke) for inc in incs]
        bound = max(threshold(H,inc,0) for inc in incs)*F(costs['quantum'])
        for multiplier in (F(3,2),F(2),F(1,4),F(0)):
            requested = multiplier*bound
            idx = math.ceil(requested/unit)
            actual = idx*unit
            q_lattice = np.array([idx*costs['factor']],dtype=np.int64)
            for mode in (0,1):
                d,ed,*_ = profiles.values(costs,'d',[idx],mode)
                dh,eh,*_ = profiles.values(costs,'dh',[idx],mode)
                outside = all(actual >= threshold(H,inc,mode)*F(costs['quantum']) for inc in incs)
                difference,error = abs(d[0]-dh[0]),ed[0]+eh[0]
                require(not outside or difference<=error, 'native P-clip mismatch outside Clip')
                st = P.evaluate(costs['profiles']['Wst'],q_lattice,mode)[0]
                delta = P.evaluate(costs['profiles']['d'],q_lattice,mode)[0]
                true_idle = (st,st+delta)
                true_errors = (costs['profiles']['Wst']['error'],
                               costs['profiles']['Wst']['error']+costs['profiles']['d']['error'])
                action_results = {}
                for name,inc,mean,true_value,true_error in zip(('Stay','Switch'),incs,means,true_idle,true_errors):
                    mvalue = P.evaluate(mean,q_lattice,mode)[0]
                    jensen_gap = (true_value-mvalue)*scale
                    allowance = (true_error+mean['error']+256*P.EPS*(abs(true_value)+abs(mvalue)+1))*abs(scale)
                    require(jensen_gap >= -allowance, 'native Jensen mismatch')
                    # Add the same conditional linear term to both idle costs.
                    p,_ = P.probability(keep,ke)
                    r = 2*p[0]-1
                    powers = np.r_[P.LD(1),np.cumprod(np.full(H-1,r,dtype=P.LD))]
                    increments = P.LD(sum(inc))/2+(2*mode-1)*P.LD(inc[1]-inc[0])/2*powers
                    linear = P.number(dt)*(H*P.number(actual)+P.number(F(costs['quantum']))*
                                             (np.arange(H,0,-1,dtype=P.LD)*increments).sum(dtype=P.LD))
                    action_results[name] = dict(M1=float(linear+true_value*scale),M0=float(linear+mvalue*scale),
                                                M1_minus_M0=float(jensen_gap),error=float(allowance))
                rows.append(dict(id=cid,path=which,mode=mode,q_requested=str(requested),q_actual=str(actual),
                                 unit=str(unit),index=idx,ref=case['raw']['ref'],H=H,dt=str(dt),
                                 outside_exact_Clip=outside,d=float(d[0]),dh=float(dh[0]),
                                 abs_d_minus_dh=float(difference),reported_error=float(error),
                                 actions=action_results,arithmetic_pass_original=case['raw']['arithmetic_pass']))
    return rows


def current_measure(side, K):
    from experiments.R3R_08_population_numerics import quadrature,profiles
    costs,unit,law = side['costs'],side['unit'],side['law']
    factor = costs['factor']
    cap = max((int(costs['profiles'][name]['modes'][m][0][-1])+factor-1)//factor
              for name in ('d','dh') for m in (0,1))
    grid = quadrature.build(law,K,cap)
    thresholds = [max(threshold(costs['H'],inc,m) for inc in
                      (costs['increments_st'],costs['increments_sw']))*F(costs['quantum']) for m in (0,1)]
    require(all((cap+1)*unit >= t for t in thresholds), 'tail sentinel could contain clipping states')
    # Strict q<t on integer stationary lattice: last included index=ceil(t/unit)-1.
    cutoffs = [math.ceil(t/unit)-1 for t in thresholds]
    clip = np.column_stack([(grid['indices']>=0)&(grid['indices']<=cutoff) for cutoff in cutoffs])
    cdf,ecdf = law.cdf(cutoffs)
    pc = sum(cdf[m,m] for m in (0,1))
    epc = sum(ecdf[m,m] for m in (0,1))
    data = {key:[] for key in ('d','h','ed','eh','zero_h','sat_h')}
    for m in (0,1):
        d,ed,_,_ = profiles.values(costs,'d',grid['indices'],m)
        h,eh,zero,sat = profiles.values(costs,'dh',grid['indices'],m)
        for key,value in zip(data,(d,h,ed,eh,zero,sat)):
            data[key].append(value)
    data = {k:np.column_stack(v).ravel() for k,v in data.items()}
    data.update(w=grid['mass'].ravel(),w_error=grid['l1_error'],clip=clip.ravel(),
                P_clip=pc,P_clip_error=epc,tail_mass=grid['mass'][-1].sum())
    return data


def diagnostic(cid, case):
    from experiments.R3R_08_population_numerics.population import pair_loss
    raw = case['raw']
    A,B = (current_measure(cached_side(case,w),raw['K']) for w in ('A','B'))
    c = P.number(F(raw['parameters'][-1]))
    d = A['d'][:,None]+B['d'][None,:]+c
    h = A['h'][:,None]+B['h'][None,:]+c
    certified = (A['zero_h'][:,None]&B['zero_h'][None,:])|(A['sat_h'][:,None]&B['sat_h'][None,:])
    h = np.where(certified,c,h)
    weight = A['w'][:,None]*B['w'][None,:]
    clip = A['clip'][:,None]|B['clip'][None,:]
    sigma = (weight*abs(d)).sum(dtype=P.LD)
    sclip = (weight*abs(d)*clip).sum(dtype=P.LD)
    gain = (weight*abs(d)*((h<0)!=(d<0))).sum(dtype=P.LD)
    scale = P.number(raw['Cref'])
    native_gain = P.number(raw['G_M_S1'])
    delta_pp = 100*abs(gain-native_gain)/scale
    mean_cost,_,_ = pair_loss(A,B,F(raw['parameters'][-1]),model='mean')
    true_cost,_,_ = pair_loss(A,B,F(raw['parameters'][-1]),model='true')
    require(abs(gain-(mean_cost-true_cost)) <= 1e-12*(1+abs(gain)), 'regret vs pair_loss mismatch')
    require(delta_pp<=1e-9,'saved native gain does not replay on current quadrature')
    allowance = 2048*P.EPS*(1+sigma+gain)
    require(gain<=sclip+allowance,'G_M|S1 exceeds S_clip on the same quadrature')
    require(sclip<=sigma+allowance,'S_clip exceeds total stakes')
    p = 1-(1-A['P_clip'])*(1-B['P_clip'])
    ep = A['P_clip_error']+B['P_clip_error']+A['P_clip_error']*B['P_clip_error']+1024*P.EPS
    return dict(id=cid,old_class=case['meta']['old_class'],cohort=case['meta']['cohort'],
                parameters=raw['parameters'],K=raw['K'],ref=raw['ref'],dt=raw['dt'],
                P_clip=float(p),P_clip_error=float(ep),P_clip_quadrature=float((weight*clip).sum(dtype=P.LD)),
                S_clip=float(sclip),sigma=float(sigma),S_clip_over_sigma=float(sclip/sigma) if sigma>0 else None,
                S_clip_pctC=float(100*sclip/scale),GM_S1_pctC=float(100*native_gain/scale),
                abs_Gamma_pctC=float(100*abs(P.number(raw['Gamma']))/scale),
                GM_S1_direct=float(gain),replay_difference_pp=float(delta_pp),
                bound_slack=float(sclip-gain),bound_pass=True,
                arithmetic_pass_original=raw['arithmetic_pass'],validity_errors_original=raw['validity_errors'],
                source=case['meta']['source'],source_sha256=case['meta']['source_sha256'],
                interpretation='P_clip uses certified marginal CDF; S_clip/sigma uses native quadrature, not a certified total interval')


def associations(rows, range_floor):
    from scipy.stats import spearmanr
    out = {}
    for predictor in ('P_clip','S_clip_over_sigma'):
        x = [r[predictor] for r in rows]
        for target in ('GM_S1_pctC','abs_Gamma_pctC'):
            y = [r[target] for r in rows]
            meaningful = (len(x)>=3 and all(v is not None for v in x)
                          and max(x)-min(x)>range_floor and max(y)-min(y)>range_floor)
            out[predictor+'__'+target] = dict(n=len(rows),rho=float(spearmanr(x,y).statistic) if meaningful else None,
                                               status='DESCRIPTIVE_ONLY' if meaningful else 'DEGENERATE_RANGE',
                                               p_value_reported=False)
    return out


def write_json(path, doc):
    path.write_text(json.dumps(doc,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def plot(rows, path):
    if not rows:
        return
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes = plt.subplots(2,2,figsize=(10,8),layout='constrained')
    for i,x in enumerate(('P_clip','S_clip_over_sigma')):
        for j,y in enumerate(('GM_S1_pctC','abs_Gamma_pctC')):
            for label,color in (('A','#0072B2'),('AB','#009E73'),('C','#D55E00')):
                rr = [r for r in rows if r['old_class']==label]
                axes[i,j].scatter([r[x] for r in rr],[r[y] for r in rr],c=color,label=label,s=24,alpha=.7)
            axes[i,j].set(xlabel=x,ylabel=y+' (% Cref)')
            axes[i,j].grid(alpha=.2)
    axes[0,0].legend()
    fig.suptitle(f'L4.7 exposed discovery n={len(rows)}; S_clip uses true Delta; no causal/held-out inference')
    for ext in ('png','pdf'):
        fig.savefig(path.with_suffix('.'+ext),dpi=160)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args(argv)
    require(not args.out.exists(),'use a new output directory')
    from experiments.P4_A1.config import verify_run
    for name in ('L43_A1_SV','L44_A3','SUB_BOX'):
        verify_run(name)
    protocol,cases = load_inputs()
    from experiments.R3R_14_lean_close.engine import configure
    configure()
    args.out.mkdir(parents=True)
    begin,wall = cpu(),time.monotonic()
    example = enumerate_example()
    write_json(args.out/'enumeration.json',example)
    states = []
    for cid in protocol['part_B_ids']:
        states.extend(state_checks(cid,cases[cid]))
    write_json(args.out/'state_checks.json',states)
    optional_start,optional_wall = cpu(),time.monotonic()
    rows,status = [],'COMPLETE'
    class Timebox(Exception):
        pass
    def alarm(signum,frame):
        raise Timebox('PartC wall cap reached')
    previous = signal.signal(signal.SIGALRM,alarm)
    signal.setitimer(signal.ITIMER_REAL,protocol['part_C_cap']['wall_seconds'])
    try:
        with (args.out/'diagnostics.jsonl').open('w') as stream:
            for cid in protocol['part_C_ids']:
                if cpu()-optional_start>=protocol['part_C_cap']['cpu_seconds']:
                    status='CPU_TIMEBOX_REACHED';break
                started = cpu()
                row = diagnostic(cid,cases[cid])
                row['diagnostic_cpu_seconds'] = cpu()-started
                rows.append(row)
                stream.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n');stream.flush()
                print(f'PartC {len(rows)}/{len(protocol["part_C_ids"])} {cid} CPU={row["diagnostic_cpu_seconds"]:.3f}s',flush=True)
    except Timebox:
        status='WALL_TIMEBOX_REACHED'
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        signal.signal(signal.SIGALRM,previous)
    if rows:
        with (args.out/'diagnostics.csv').open('w',newline='') as stream:
            flat=[{k:v for k,v in r.items() if k not in ('parameters','validity_errors_original')} for r in rows]
            writer=csv.DictWriter(stream,fieldnames=list(flat[0]),lineterminator='\n');writer.writeheader();writer.writerows(flat)
    outside = [r for r in states if r['outside_exact_Clip']]
    summary = dict(responsible='Doan Van Tai',date='2026-10-31',part_A='AI_ASSISTED_PROOF; author understanding OPEN',
                   part_B=dict(status='PASS',states=len(states),outside=len(outside),inside=len(states)-len(outside),
                               max_outside_abs_d_minus_dh=max(r['abs_d_minus_dh'] for r in outside),
                               max_inside_abs_d_minus_dh=max(r['abs_d_minus_dh'] for r in states if not r['outside_exact_Clip']),
                               jensen_action_checks=2*len(states),
                               gap_error_signs=sorted({int(np.sign(r['d']-r['dh'])) for r in states})),
                   part_C=dict(status=status,planned=len(protocol['part_C_ids']),completed=len(rows),
                               cpu_seconds=cpu()-optional_start,wall_seconds=time.monotonic()-optional_wall,
                               all_bounds_pass=all(r['bound_pass'] for r in rows),
                               max_saved_gain_replay_error_pp=max((r['replay_difference_pp'] for r in rows),default=None),
                               P_clip_range=[min(r['P_clip'] for r in rows),max(r['P_clip'] for r in rows)] if rows else None,
                               S_clip_over_sigma_range=[min(r['S_clip_over_sigma'] for r in rows),max(r['S_clip_over_sigma'] for r in rows)] if rows else None,
                               correlations=associations(rows,protocol['rank_degeneracy_range'])),
                   diagnostics_cpu_seconds_before_summary_plot=cpu()-begin,
                   diagnostics_wall_seconds_before_summary_plot=time.monotonic()-wall,
                   new_whole_regime_evaluations=0,new_CF_outcomes=0,new_sealed_outcomes=0,
                   new_physical_profiles=0,SUB_resumed=False,native_D22='DEFERRED',
                   protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest())
    write_json(args.out/'summary.json',summary)
    plot(rows,args.out/'predictors')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
