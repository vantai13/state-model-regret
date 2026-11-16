"""Doan Van Tai — W1b finite-record s-hat estimators and local experiment runner.

Run after sourcing .venv/bin/activate and experiments/explore_ctmc/env.sh:
    python3 -m experiments.letter.shat run --workers 8
    python3 -m experiments.letter.shat analyze
No existing result is overwritten, and the original CTMC namespace is respected.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
import hashlib
import json
import math
import multiprocessing
from pathlib import Path
import time
import traceback

import numpy as np

from experiments.explore_ctmc import ctmc
from experiments.letter.e3_agediff import evaluate_agediff, prepare_regime

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/letter/w1b'
FAMILIES = ('asym', 'zf_a3_asym', 'zf_a7p5_asym')
EPSILONS = (-.5, -.25, -.1, .1, .25, .5)
NUM_TOL = 1e-9  # arithmetic equality in percentage points; not a scientific effect threshold


def write_json_once(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Serialize before exclusive creation, so a serialization error cannot leave a partial file.
    payload = json.dumps(obj, indent=2, allow_nan=False) + '\n'
    with path.open('x') as f:
        f.write(payload)


def load_cases():
    cases = []
    for family in FAMILIES:
        for case in json.loads((ROOT / 'results/explore_ctmc/cases' / (family+'.json')).read_text()):
            cases.append(dict(case, family=family, regime_index=len(cases)))
    return cases


def estimate_path(load_stay, managed_shift, kappa, amplitude, T_int, rng):
    """Exact sampled two-state mode process, including both endpoints 0 and W.

    load_stay is the telemetry arrival mean; managed_shift is Switch minus Stay.
    The same estimated exogenous process is used for the two action loads.
    """
    delta = float(T_int)/10
    count = 1000  # W/delta = (100*T_int)/(T_int/10)
    mode = np.empty(count+1, dtype=np.int8)
    mode[0] = rng.integers(0, 2)
    p_flip = -math.expm1(-2*delta/float(kappa))/2
    flips = rng.random(count) < p_flip
    mode[1:] = np.bitwise_xor.accumulate(np.r_[mode[0], flips.astype(np.int8)])[1:]
    rates = float(load_stay) + float(amplitude)*(2*mode.astype(float)-1)
    mean, sd = float(rates.mean()), float(rates.std(ddof=0))
    raw_rho = float(np.corrcoef(rates[:-1], rates[1:])[0,1]) if sd > 0 else None
    if raw_rho is not None and not math.isfinite(raw_rho):
        raw_rho = None
    rho = float(np.clip(raw_rho, np.nextafter(0.,1.), np.nextafter(1.,0.))) if raw_rho is not None and math.isfinite(raw_rho) else None
    khat = -2*delta/math.log(rho) if rho is not None else None
    return dict(W=100*float(T_int), delta=delta, n_samples=count+1, mode=mode.tolist(),
                lambda_hat=mean, alpha_hat=sd, rho1_raw=raw_rho, rho1_clipped=rho,
                kappa_hat=khat, stay_load_hat=mean, switch_load_hat=mean+float(managed_shift))


def estimate_levels(p, regime_index):
    """Estimate once per regime, then keep estimates fixed at every age and h."""
    lamA, lamB, u, kappa, _ = p['parameters']
    seed = 20261116 + int(regime_index)
    rng = np.random.default_rng(seed)
    telemetry = dict(A=estimate_path(lamA+u,-u,kappa,p['a'],p['T_int'],rng),
                     B=estimate_path(lamB,u,kappa,p['a'],p['T_int'],rng))
    errors, records = [], {}
    means = {}
    for side, N in (('A',p['NA']),('B',p['NB'])):
        est = telemetry[side]
        for action in ('stay','switch'):
            name, load = side+'_'+action, est[action+'_load_hat']
            try:
                if est['kappa_hat'] is None or est['kappa_hat'] <= 0:
                    raise ValueError('undefined or nonpositive kappa estimate')
                if load < est['alpha_hat'] or load < 0 or load >= ctmc.MU:
                    raise ValueError('estimated load/amplitude outside nonnegative stable model domain')
                ch = ctmc.chain(load, est['kappa_hat'], N, est['alpha_hat'])
                if not (np.isfinite(ch.pi).all() and np.min(ch.pi) >= -1e-12
                        and math.isfinite(ch.r) and ch.residual <= 1e-9):
                    raise ArithmeticError('invalid estimated chain stationary law')
                means[name] = ch.r
                records[name] = dict(status='VALID',load=load,N=N,r=ch.r,residual=ch.residual)
            except (ValueError, ArithmeticError, RuntimeError) as exc:
                errors.append(dict(chain=name,kind=type(exc).__name__,message=str(exc)))
                records[name] = dict(status='INVALID',load=load,N=N,error=str(exc))
    valid = not errors
    s_est = means['A_switch']+means['B_switch']-means['A_stay']-means['B_stay'] if valid else None
    levels = dict(true_s=p['s'], mmpp_est=s_est if valid else p['s_mm1'], mm1=p['s_mm1'])
    levels.update({f'true_s_eps_{eps:+g}':p['s']*(1+eps) for eps in EPSILONS})
    levels['sign_flipped'] = -p['s']
    meta = dict(seed=seed,status='VALID' if valid else 'INVALID',fallback=None if valid else 'mm1',
                s_hat_mmpp=s_est,effective_s_hat=levels['mmpp_est'], telemetry=telemetry,
                chains=records, errors=errors,
                sign_correct=None if not valid else bool(np.sign(s_est)==np.sign(p['s'])),
                effective_sign_correct=bool(np.sign(levels['mmpp_est'])==np.sign(p['s'])))
    return levels, meta


def saved_path(case):
    return ROOT / 'results/explore_ctmc' / ('runs' if case['family']=='asym' else 'runs_l72') / case['family'] / (case['id']+'.json')


def case_work(case):
    """A deterministic stiffness/state/horizon proxy used only to choose the pilot."""
    la,lb,u,k,_ = (F(x) for x in case['parameters'])
    a = F(case.get('a',ctmc.A))
    na,nb = (ctmc.choose_N(l+u,k,a=a) for l in (la,lb))
    return (na+nb+2)*(max(float(F(h)) for h in case['hs'])+4.4*case['T_int_max']+1)*(30+2/float(k))


def read_baseline(case):
    """Preflight the existing baseline; UNRESOLVED is missing evidence, not zero."""
    baseline = json.loads(saved_path(case).read_text())
    if baseline['parameters'] != [str(F(v)) for v in case['parameters']]:
        raise ValueError('saved baseline parameters do not match case')
    available = baseline.get('status') == 'COMPLETED' and isinstance(baseline.get('h'), list)
    if available and F(baseline['a']) != F(case.get('a',ctmc.A)):
        raise ValueError('saved baseline amplitude does not match case')
    if not available and baseline.get('status') != 'UNRESOLVED':
        raise ValueError('unexpected missing baseline status')
    if available:
        missing = set(map(lambda h:str(F(h)),case['hs']))-{str(F(r['h'])) for r in baseline['h']}
        if missing:
            raise ValueError('baseline lacks horizons: '+str(missing))
    return baseline, available


def timed_v(job):
    """Unchanged Chain.V in an independent worker, with its own CPU measurement."""
    key, hs = job
    t0 = time.process_time()
    load,kappa,N,a = key
    values = ctmc.chain(F(load),F(kappa),N,F(a)).V(hs)
    return key, values, time.process_time()-t0


def timed_age(p, case, label, tau, levels):
    t0 = time.process_time()
    la,lb,u,k,c = case['parameters']
    out = evaluate_agediff(la,lb,u,k,case['hs'],tau,c=c,a=F(case.get('a',ctmc.A)),
                           prepared=p,shat_levels=levels,disagree=False)
    out.update(age_label=label,tau_Tint=tau/p['T_int'],cpu_seconds=time.process_time()-t0)
    return out


def run_one(case, parallel_pool=None):
    target = OUT / 'raw' / (case['id']+'.json')
    if target.exists():
        raise FileExistsError(target)
    t0, w0 = time.process_time(), time.monotonic()
    baseline, baseline_available = read_baseline(case)
    la,lb,u,k,c = case['parameters']
    a = F(case.get('a',ctmc.A))
    child_cpu = 0.
    v_components = []
    v_table = None
    if parallel_pool is not None:
        na,nb = (ctmc.choose_N(F(load)+F(u),F(k),a=a) for load in (la,lb))
        keys = {(str(F(load)),str(F(k)),N,str(a)) for load,N in
                ((F(la)+F(u),na),(F(la),na),(F(lb),nb),(F(lb)+F(u),nb))}
        print('V_JOBS '+json.dumps([list(key) for key in sorted(keys)]),flush=True)
        futures = [parallel_pool.submit(timed_v,(key,case['hs'])) for key in sorted(keys)]
        v_table = {}
        for future in as_completed(futures):
            key,values,cpu = future.result()
            v_table[key] = values
            child_cpu += cpu
            v_components.append(dict(key=list(key),cpu_seconds=cpu))
            print('V_DONE '+json.dumps(v_components[-1]),flush=True)
    p = prepare_regime(la,lb,u,k,case['hs'],c=c,a=a,v_table=v_table)
    prepared_cpu = time.process_time()-t0+child_cpu
    levels, estimates = estimate_levels(p,case['regime_index'])
    ages = [('seconds_1',1.)]+[(f'Tint_{v:g}',v*p['T_int']) for v in (.1,.3,1.,3.)]
    if parallel_pool is None:
        evaluations = [timed_age(p,case,label,tau,levels) for label,tau in ages]
    else:
        futures = [parallel_pool.submit(timed_age,p,case,label,tau,levels) for label,tau in ages]
        by_label = {}
        for future in as_completed(futures):
            ev = future.result()
            by_label[ev['age_label']] = ev
            child_cpu += ev['cpu_seconds']
            print('AGE_DONE '+json.dumps(dict(id=case['id'],age=ev['age_label'],cpu_seconds=ev['cpu_seconds'])),flush=True)
        evaluations = [by_label[label] for label,_ in ages]
    max_diff = 0. if baseline_available else None
    if baseline_available:
        old_h = {str(F(row['h'])):row for row in baseline['h']}
        for row in evaluations[0]['h']:
            old = old_h[row['h']]
            for key in ('L10','L11','Cref'):
                max_diff = max(max_diff,abs(row[key]-old[key]))
                if not math.isclose(row[key],old[key],rel_tol=1e-10,abs_tol=1e-9):
                    raise ArithmeticError('fresh side differs from saved confounded baseline')
    out = dict(owner='Doan Van Tai',id=case['id'],family=case['family'],regime_index=case['regime_index'],
               status='COMPLETED',case=case,T_int=p['T_int'],s=p['s'],s_mm1=p['s_mm1'],
               estimates=estimates,levels=levels,evaluations=evaluations,
               baseline_available=baseline_available,baseline_status=baseline.get('status'),
               baseline_error=baseline.get('error'),
               saved_baseline=str(saved_path(case).relative_to(ROOT)),max_fresh_baseline_abs_diff=max_diff,
               baseline_sha256=hashlib.sha256(saved_path(case).read_bytes()).hexdigest(),
               prepare_cpu_seconds=prepared_cpu,cpu_seconds=time.process_time()-t0+child_cpu,
               cpu_components_V=v_components,parallel_inside_regime=parallel_pool is not None,
               wall_seconds=time.monotonic()-w0)
    write_json_once(target,out)
    return dict(id=case['id'],family=case['family'],cpu_seconds=out['cpu_seconds'],
                wall_seconds=out['wall_seconds'],estimator_status=estimates['status'])


def recover(workers):
    """Finish only missing raw, after an I/O interruption, without rerunning successes."""
    if workers != 8:
        raise ValueError('eight local workers required')
    cases = load_cases()
    pilot = json.loads((OUT/'pilot.json').read_text())
    selected = [c for c in cases if pilot['decision']=='all_on_disk' or c['family']=='asym']
    missing = [c for c in selected if not (OUT/'raw'/(c['id']+'.json')).exists()]
    if len(missing)!=1 or missing[0]['id']!='Za7p5_u3-2_lA31-4_x1-3_k2':
        raise ValueError('I/O recovery is restricted to the one interrupted raw case')
    baseline,available = read_baseline(missing[0])
    if available:
        raise ValueError('recovery reason no longer matches original unresolved baseline')
    write_json_once(OUT/'io_recovery_plan.json',dict(owner='Doan Van Tai',case=missing[0],
                    reason='Preflight baseline is UNRESOLVED; omit only its P7/P8 comparison, still compute all E3/E2 outputs.',
                    scheduling='same unchanged Chain.V in four independent tasks, then same direct age evaluations in five independent tasks; max_workers=8, fork',
                    scientific_changes=[],retry_reason='I/O repair before any result from this case was saved or interpreted; 92 successful raws never rerun or overwritten',
                    baseline_status=baseline['status'],baseline_error=baseline['error'],
                    previous_interrupted_cpu='unknown; report separately from measured successful CPU',
                    source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('experiments/letter/e3_agediff.py','experiments/letter/shat.py','tests/test_letter_w1b.py')}))
    w0=time.monotonic()
    with ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('fork')) as pool:
        result=run_one(missing[0],parallel_pool=pool)
    print('RECOVERED '+json.dumps(result),flush=True)
    raws=[json.loads((OUT/'raw'/(c['id']+'.json')).read_text()) for c in selected]
    interruption=json.loads((OUT/'interruption.json').read_text())
    write_json_once(OUT/'run_receipt.json',dict(status='COMPLETED',selected_ids=[c['id'] for c in selected],
                    cpu_seconds=sum(r['cpu_seconds'] for r in raws),
                    cpu_note='Measured successful evaluations only; interrupted case CPU unknown and excluded, not zero.',
                    wall_seconds=time.time()-(OUT/'run_plan.json').stat().st_mtime,
                    wall_note='Elapsed from immutable initial run_plan timestamp, including interruption and I/O repair.',
                    recovery_wall_seconds=time.monotonic()-w0,receipts=[dict(id=r['id'],family=r['family'],cpu_seconds=r['cpu_seconds'],wall_seconds=r['wall_seconds']) for r in raws],
                    failures=[],historical_interruption='interruption.json',interrupted_case_cpu_seconds=None))


def run(workers):
    if workers != 8:
        raise ValueError('brief specifies eight local workers')
    cases = load_cases()
    for case in cases:
        read_baseline(case)
    # One median-work representative per family; no outcomes used in the selection.
    pilot, proxies = [], {}
    for fam in FAMILIES:
        ordered = sorted((c for c in cases if c['family']==fam),key=case_work)
        proxies.update({c['id']:case_work(c) for c in ordered})
        pilot.append(ordered[len(ordered)//2])
    plan = dict(owner='Doan Van Tai',n_regimes_in_brief=99,n_regimes_on_disk=len(cases),
                family_counts={f:sum(c['family']==f for c in cases) for f in FAMILIES},
                pilot_ids=[c['id'] for c in pilot],workers=workers,projection_cap_wall_hours=3,
                pilot_projection='sum(family CPU/proxy from its pilot * family proxy sum) / 8',
                seed='20261116 + zero-based concatenated case index',
                numeric_equality_tolerance_pp=NUM_TOL,
                interpretation=dict(P7='tau=Tint; h/Tint>=7; saved confounded G_S<-.1; fraction age-only G_S<-.1 >= .6',
                    P8='tau=1 s; literal median ratio on all matching rows with nonzero confounded G_S < 1; harm subsets also reported',
                    P9='each of i and all six iv separately: both telemetry regrets <=.1 percent for >=.95 of rows h/Tint>=4',
                    P10='VALID estimates only: sign agreement per regime >=.95, and both regrets equal i within 1e-9 pp on sign-correct rows; INVALID fallback reported separately',
                    P11='finite-panel numerical reading: all sign-flip |G_S|<=1e-9 pp; report raw excess cost/(h*abs(s)) by h/Tint without inventing a tolerance for approx; asymptotic statement separate',
                    P12='true-s level i at h/Tint<1: exists a new or old regret exceeding its M0 counterpart by >1e-9 pp'),
                ambiguity='P10 matches and P11 approx have no scientific tolerances on the card; arithmetic equality is conservative, ratios are descriptive; P11 absolute excess cost is distinct from percent regret',
                pilot_proxies=proxies)
    plan_path = OUT/'run_plan.json'
    if plan_path.exists():
        if json.loads(plan_path.read_text()) != plan:
            raise ValueError('existing run plan differs; will not overwrite it')
    else:
        write_json_once(plan_path,plan)
    wall0, all_receipts = time.monotonic(), []
    # Python 3.14's default forkserver needs a Unix listener, unavailable in the
    # restricted local sandbox. fork uses the same numeric workers via pipes.
    with ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('fork')) as pool:
        futures = {pool.submit(run_one,c):c for c in pilot}
        for future in as_completed(futures):
            receipt = future.result()
            all_receipts.append(receipt)
            print('PILOT '+json.dumps(receipt),flush=True)
        ratios = {r['family']:r['cpu_seconds']/proxies[r['id']] for r in all_receipts}
        projected_cpu = sum(ratios[c['family']]*proxies[c['id']] for c in cases)
        asym_only = projected_cpu/(workers*3600)>3
        selected = [c for c in cases if not asym_only or c['family']=='asym']
        projection = dict(projected_cpu_seconds=projected_cpu,projected_wall_hours_8_workers=projected_cpu/(workers*3600),
                          decision='asym_only' if asym_only else 'all_on_disk',
                          selected_regimes=len(selected),pilot_wall_seconds=time.monotonic()-wall0,
                          note='Out-of-scope pilot rows remain saved, and are excluded from primary analysis if asym_only.')
        write_json_once(OUT/'pilot.json',dict(**projection,receipts=all_receipts.copy()))
        print('PROJECTION '+json.dumps(projection),flush=True)
        pilot_ids={c['id'] for c in pilot}
        futures={pool.submit(run_one,c):c for c in selected if c['id'] not in pilot_ids}
        failures=[]
        for future in as_completed(futures):
            try:
                receipt=future.result();all_receipts.append(receipt)
                print('DONE '+json.dumps(receipt),flush=True)
            except Exception as exc:
                failure=dict(id=futures[future]['id'],error=str(exc),traceback=traceback.format_exc())
                failures.append(failure);print('FAILED '+json.dumps(failure),flush=True)
        write_json_once(OUT/'run_receipt.json',dict(status='FAILED' if failures else 'COMPLETED',
                        cpu_seconds=sum(r['cpu_seconds'] for r in all_receipts),
                        wall_seconds=time.monotonic()-wall0,receipts=all_receipts,failures=failures,
                        selected_ids=[c['id'] for c in selected]))
    if failures:
        raise RuntimeError('Some regimes failed; raw successes preserved, no automatic retry')


def analyze():
    """Read completed write-once raw files; export tables and mechanical scores."""
    import pandas as pd
    receipt=json.loads((OUT/'run_receipt.json').read_text())
    if receipt['status']!='COMPLETED':
        raise RuntimeError('Cannot score an incomplete experiment')
    selected=set(receipt['selected_ids'])
    raw_files=sorted((OUT/'raw').glob('*.json'))
    write_json_once(OUT/'raw_manifest.json',dict(sha256={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in raw_files}))
    flat,regimes=[],[]
    flags=[]
    max_fresh=0.
    for path in raw_files:
        raw=json.loads(path.read_text())
        if raw['id'] not in selected:
            continue
        meta=raw['estimates']
        regimes.append(dict(id=raw['id'],family=raw['family'],s=raw['s'],status=meta['status'],
                            sign_correct=meta['sign_correct'],effective_sign_correct=meta['effective_sign_correct'],
                            errors=meta['errors']))
        if raw['max_fresh_baseline_abs_diff'] is not None:
            max_fresh=max(max_fresh,raw['max_fresh_baseline_abs_diff'])
        baseline=json.loads((ROOT/raw['saved_baseline']).read_text())
        if hashlib.sha256((ROOT/raw['saved_baseline']).read_bytes()).hexdigest()!=raw['baseline_sha256']:
            raise ValueError('saved baseline changed since run')
        baseline_h={str(F(r['h'])):r for r in baseline.get('h',[])}
        for ev in raw['evaluations']:
            for r in ev['h']:
                if r['flags']:flags.append(dict(id=raw['id'],age=ev['age_label'],h=r['h'],flags=r['flags']))
                bin_name=('<1' if r['h_Tint']<1 else '1–<4' if r['h_Tint']<4 else '4–<7' if r['h_Tint']<7 else '>=7')
                for level,v in r['hybrid_levels'].items():
                    hs=abs(raw['s'])*float(F(r['h']))
                    flat.append(dict(family=raw['family'],id=raw['id'],seed=meta['seed'],age_label=ev['age_label'],
                                     tau=ev['tau'],tau_Tint=ev['tau_Tint'],a=ev['a'],T_int=raw['T_int'],
                                     h=r['h'],h_Tint=r['h_Tint'],h_bin=bin_name,level=level,s_true=raw['s'],s_hat=v['s_hat'],
                                     estimator_status=meta['status'],is_fallback=level=='mmpp_est' and meta['status']=='INVALID',
                                     baseline_available=r['h'] in baseline_h,
                                     Cref=r['Cref'],G_S_M0_age=r['G_S'],G_S_M0_confounded=baseline_h.get(r['h'],{}).get('G_S'),
                                     M0_new=r['regret']['M0_new'],M0_old=r['regret']['M0_old'],
                                     regret_new=v['regret_new'],regret_old=v['regret_old'],G_S_hybrid=v['G_S'],
                                     share_new=v['share_new'],share_old=v['share_old'],
                                     excess_cost_new=v['excess_cost_new'],excess_cost_old=v['excess_cost_old'],
                                     cost_over_h_abs_s_new=v['excess_cost_new']/hs if hs else None,
                                     cost_over_h_abs_s_old=v['excess_cost_old']/hs if hs else None))
    if len(regimes)!=len(selected):
        raise ValueError('selected raw regime set is incomplete')
    df=pd.DataFrame(flat)
    if not np.isfinite(df[['Cref','regret_new','regret_old','G_S_hybrid','share_new','share_old']].values).all():
        raise ArithmeticError('nonfinite scored outputs')
    if flags:raise ArithmeticError('control inequalities violated: '+str(flags))
    if min(df.regret_new.min(),df.regret_old.min()) < -NUM_TOL:
        raise ArithmeticError('negative regret beyond numeric tolerance')
    e3=df[df.level=='true_s'].copy()
    p7rows=e3[(e3.age_label=='Tint_1')&(e3.h_Tint>=7)&(e3.G_S_M0_confounded<-.1)]
    p7=[]
    for family,sub in [('ALL',p7rows)]+[(f,p7rows[p7rows.family==f]) for f in FAMILIES if f in set(df.family)]:
        n=len(sub);hits=int((sub.G_S_M0_age<-.1).sum())
        p7.append(dict(family=family,eligible=n,age_harm=hits,fraction=hits/n if n else None,
                       confounded_median=float(sub.G_S_M0_confounded.median()) if n else None,
                       age_median=float(sub.G_S_M0_age.median()) if n else None))
    p8base=e3[(e3.age_label=='seconds_1')&e3.baseline_available]
    p8=[]
    for label,sub in [('all_nonzero',p8base[p8base.G_S_M0_confounded!=0]),
                       ('confounded_negative',p8base[p8base.G_S_M0_confounded<0]),
                       ('confounded_below_minus_0.1',p8base[p8base.G_S_M0_confounded<-.1])]:
        ratios=sub.G_S_M0_age/sub.G_S_M0_confounded
        p8.append(dict(population=label,n=len(sub),median_ratio=float(ratios.median()) if len(sub) else None,
                       confounded_median=float(sub.G_S_M0_confounded.median()) if len(sub) else None,
                       age_median=float(sub.G_S_M0_age.median()) if len(sub) else None))
    p9=[]
    for level,sub in df[(df.h_Tint>=4)&(df.level.str.startswith('true_s'))].groupby('level',sort=False):
        both=(sub.regret_new<=.1)&(sub.regret_old<=.1)
        p9.append(dict(level=level,n=len(sub),both_pass=int(both.sum()),fraction=float(both.mean()),
                       new_pass=int((sub.regret_new<=.1).sum()),old_pass=int((sub.regret_old<=.1).sum()),
                       max_new=float(sub.regret_new.max()),max_old=float(sub.regret_old.max())))
    valid=[r for r in regimes if r['status']=='VALID']
    correct_ids={r['id'] for r in valid if r['sign_correct']}
    est=df[(df.level=='mmpp_est')&df.id.isin(correct_ids)]
    truth=df[df.level=='true_s'].set_index(['id','age_label','h'])
    match_diffs=[]
    for r in est.itertuples():
        tr=truth.loc[(r.id,r.age_label,r.h)]
        match_diffs.append(max(abs(r.regret_new-tr.regret_new),abs(r.regret_old-tr.regret_old)))
    p10=dict(valid_regimes=len(valid),invalid_regimes=len(regimes)-len(valid),
             correct_sign=sum(r['sign_correct'] for r in valid),
             sign_fraction=sum(r['sign_correct'] for r in valid)/len(valid) if valid else None,
             sign_correct_rows=len(match_diffs),equal_regret_rows=sum(d<=NUM_TOL for d in match_diffs),
             max_regret_difference_pp=max(match_diffs) if match_diffs else None,
             fallback_sign_correct=sum(r['effective_sign_correct'] for r in regimes if r['status']=='INVALID'))
    p11=[]
    flipped=df[df.level=='sign_flipped']
    bins=['<1','1–<4','4–<7','>=7']
    for name in bins:
        sub=flipped[flipped.h_bin==name]
        p11.append(dict(h_Tint=name,n=len(sub),max_abs_GS=float(sub.G_S_hybrid.abs().max()),
                        median_regret_new=float(sub.regret_new.median()),median_regret_old=float(sub.regret_old.median()),
                        median_cost_ratio_new=float(sub.cost_over_h_abs_s_new.median()),
                        median_cost_ratio_old=float(sub.cost_over_h_abs_s_old.median())))
    p12=[]
    for level,sub in df[df.h_Tint<1].groupby('level',sort=False):
        new=(sub.regret_new-sub.M0_new)>NUM_TOL;old=(sub.regret_old-sub.M0_old)>NUM_TOL
        p12.append(dict(level=level,n=len(sub),new_worse=int(new.sum()),old_worse=int(old.sum()),
                        either_worse=int((new|old).sum()),
                        max_new_increase_pp=float((sub.regret_new-sub.M0_new).max()),
                        max_old_increase_pp=float((sub.regret_old-sub.M0_old).max())))
    by_bin=[]
    for level,sub0 in df.groupby('level',sort=False):
        for name in bins:
            sub=sub0[sub0.h_bin==name]
            by_bin.append(dict(level=level,h_Tint=name,n=len(sub),
                               median_new=float(sub.regret_new.median()),median_old=float(sub.regret_old.median()),
                               p95_new=float(sub.regret_new.quantile(.95)),p95_old=float(sub.regret_old.quantile(.95)),
                               max_abs_GS=float(sub.G_S_hybrid.abs().max()),
                               median_share_new=float(sub.share_new.median()),median_share_old=float(sub.share_old.median())))
    p12true=next(r for r in p12 if r['level']=='true_s')
    verdict=dict(P7='HELD' if p7[0]['fraction'] is not None and p7[0]['fraction']>=.6 else 'NOT_HELD',
                 P8='HELD' if p8[0]['median_ratio'] is not None and p8[0]['median_ratio']<1 else 'NOT_HELD',
                 P9='HELD' if len(p9)==7 and all(r['fraction']>=.95 for r in p9) else 'NOT_HELD',
                 P10=('NOT_EVALUABLE' if not valid else 'HELD' if p10['sign_fraction']>=.95 and all(d<=NUM_TOL for d in match_diffs) else 'NOT_HELD'),
                 P11='HELD_NUMERICAL_GS' if bool((flipped.G_S_hybrid.abs()<=NUM_TOL).all()) else 'NOT_HELD_FINITE_PANEL',
                 P12='HELD' if p12true['either_worse']>0 else 'NOT_HELD')
    # Exports are exclusive. Raw hashes are recorded before producing any summary.
    def csv(name,table):
        with (OUT/name).open('x') as f:table.to_csv(f,index=False)
    csv('summary.csv',df)
    for name,records in [('p7.csv',p7),('p8.csv',p8),('p9.csv',p9),('p11.csv',p11),
                          ('p12.csv',p12),('hybrid_by_bin.csv',by_bin)]:
        csv(name,pd.DataFrame(records))
    score=dict(verdict=verdict,regimes=len(regimes),rows_e3=len(e3),rows_hybrid=len(df),
               raw_regimes=len(raw_files),p7=p7,p8=p8,p9=p9,p10=p10,p11=p11,p12=p12,
               matched_baseline_regimes=int(e3[e3.baseline_available].id.nunique()),
               missing_baseline_ids=sorted(set(e3[~e3.baseline_available].id)),
               max_fresh_baseline_abs_diff=max_fresh,validity_flags=flags,
               invalid_details=regimes,minimum_regret_pp=float(min(df.regret_new.min(),df.regret_old.min())))
    write_json_once(OUT/'analysis.json',score)
    pilot=json.loads((OUT/'pilot.json').read_text())
    def table(records):
        d=pd.DataFrame(records)
        def fmt(v):
            if v is None or (isinstance(v,float) and not math.isfinite(v)):return 'N/A'
            return f'{v:.6g}' if isinstance(v,(float,np.floating)) else str(v)
        return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in r)+' |' for r in d.itertuples(index=False,name=None))
    invalid=len(regimes)-len(valid)
    sections=[table([dict(prediction=k,outcome=v) for k,v in verdict.items()]),
              table([dict(owner='Doan Van Tai',regimes=len(regimes),raw_regimes=len(raw_files),E3_rows=len(e3),
                          hybrid_rows=len(df),CPU_s=receipt['cpu_seconds'],wall_s=receipt['wall_seconds'],
                          pilot_projected_wall_h=pilot['projected_wall_hours_8_workers'],scope=pilot['decision'])]),
              table(p7),table(p8),table(p9),table([p10]),table(by_bin),table(p11),table(p12)]
    paragraph=(f'Đây là exploration CTMC cắt hữu hạn với μ=10, a theo từng case, seed 20261116 + index, '
               f'5 ages và h grid giữ nguyên; ba file chứa 93 regimes, không phải 99. '
               f'Mọi regret/G_S trong bảng là % C_ref; cost ratio là excess cost/(h|s|), CPU là tổng process time. '
               f'Các bin dùng h/T_int thật, không làm tròn; P9 yêu cầu cả fresh và stale đạt riêng ở từng mức i/iv. '
               f'P8 dùng tỷ số literal khi baseline khác 0 và kèm hai harm subsets; P7 ghép saved baseline τ=1 s với age-only τ=T_int. '
               f'P7/P8 chỉ trên {score["matched_baseline_regimes"]} regimes có baseline: case cuối có baseline UNRESOLVED vì CPU cap cũ, không điền 0 hoặc chạy lại baseline. '
               f'Estimator ii INVALID ở {invalid}/{len(regimes)} regimes; các dòng mmpp_est khi INVALID dùng iii và không chứng minh P10. '
               f'API gốc từ chối α̂ ngoài namespace cố định; chi tiết lỗi domain/API nằm trong raw và analysis.json. '
               f'P10 “matches” và P11 “≈” thiếu tolerance: phép so bằng số dùng 1e−9 pp; P11 NOT_HELD_FINITE_PANEL chỉ bác cách đọc đồng nhất ở mọi h, '
               f'không bác giới hạn h→∞ (s≠0, finite state: −s làm cả hai chọn action sai, G_S→0, excess cost/(h|s|)→1). '
               f'Tại τ=0 mọi pipeline trùng nhau; control τ→0⁺ không đạt trên exact M0 ties, lưu boundary_check.json, không thêm epsilon. '
               f'Fresh so với baseline sai khác tuyệt đối tối đa {max_fresh:.6g}; không có validity flags. '
               f'Pilot và raw được lưu trước diễn giải; không commit theo brief. Run khởi đầu dừng trước computation vì forkserver bị sandbox chặn, '
               f'run_fork.log dùng fork/pipes. Sau 92 raw, đã dừng case cuối trước lỗi đọc baseline thiếu; recovery chỉ tính case chưa có raw, '
               f'dùng cùng Chain.V/age calls trong các tasks độc lập, không đổi numerical evaluator. CPU báo ở bảng là các evaluations hoàn tất; '
               f'CPU phần bị dừng không có số đo và không được coi là 0. interruption.json, io_recovery_plan.json và recovery.log giữ lịch sử. '
               f'Đây là mô tả panel hữu hạn, không population CI hoặc novelty claim.')
    with (OUT/'README.md').open('x') as f:f.write('\n\n'.join(sections+[paragraph])+'\n')
    print(json.dumps(dict(verdict=verdict,regimes=len(regimes),rows=len(df),p10=p10,cpu_seconds=receipt['cpu_seconds']),indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('run','recover','analyze'))
    parser.add_argument('--workers',type=int,default=8)
    args=parser.parse_args()
    if args.action=='run':
        run(args.workers)
    elif args.action=='recover':
        recover(args.workers)
    else:
        analyze()


if __name__=='__main__':
    main()
