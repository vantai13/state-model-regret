"""Doan Van Tai — S1-C exploratory trace sweep (AI-assisted implementation).

Local: design, reference, pilot. The explicit run command is for Claude on GCP.
Chronological, nonperiodic Cox replay of existing MAWI count series; this is
not replay of the original packets. All writers refuse existing destinations.
Units: seconds, model packets, packets/s, packet-seconds. No run on import.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
from dataclasses import dataclass
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import platform
import time

import numpy as np
from scipy.stats import t as student_t

from experiments.ext_validity import packet as P

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/letter/sweep/trace'
H_MULT = (0.3, 0.5, 1., 2., 3., 5., 10.)
TAUS = (0., 1., 10., 30., 60., 120., 300.)
TRACES = {
    'ditl_20230412': 'results/ext_validity/ev_d4/series_ditl4h_mod10.npz',
    'mawi_20250311': 'results/ext_validity/ev_d3/series_20250311.npz',
    'mawi_20260414': 'results/ext_validity/ev_d3b/series_20260414.npz',
}
BRIEF = Path('/home/vantai/state-model-regret-papers/letter_smr/briefs/sweep/BRIEF_S1C_TRACE.md')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')


def write_csv(path, rows):
    if not rows:
        raise ValueError('cannot infer schema for empty CSV')
    with Path(path).open('x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def output_path(path):
    path = Path(path).resolve()
    if not path.is_relative_to(OUT.resolve()):
        raise ValueError('outputs must be inside results/letter/sweep/trace')
    if path.exists():
        raise FileExistsError(path)
    return path


def load_trace(path, fraction=0.5):
    """Only the chronological train prefix determines normalization.

    Drop the final bin conservatively (it can be incomplete). Neither source
    is time-compressed, looped, independently phase-shifted, or renormalized
    on test. The two keys stay aligned in absolute time.
    """
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z['metadata'].item()))
        x = [np.asarray(z[k], dtype=float)[:-1] for k in ('s0', 's1')]
    dt = float(meta['bin'])
    n = len(x[0])
    if (len(x[1]) != n or n < 40 or not 0 < fraction < 1 or not dt > 0
            or any(not np.isfinite(a).all() or np.any(a < 0) for a in x)):
        raise ValueError('invalid aligned trace, bin or train fraction')
    cut = int(n * fraction)
    means = [float(a[:cut].mean()) for a in x]
    if min(means) <= 0:
        raise ValueError('zero train intensity')
    return dict(counts=x, dt=dt, cut=cut, train_means=means, metadata=meta,
                train_s=cut*dt, test_s=(n-cut)*dt, duration_s=n*dt)


def trace_inventory():
    result = []
    # The two 15-min DITL extracts are inventory only, not independent days.
    extras = {'ditl_1000_subset': 'results/ext_validity/ev_d4/diag_loop15/series_202304121000.npz',
              'ditl_1200_subset': 'results/ext_validity/ev_d4/diag_loop15/series_202304121200.npz',
              'ditl_mod250_old': 'results/ext_validity/ev_d4/attempt1_mod250/series_ditl4h.npz',
              'mawi_c1_duplicate': 'results/ext_validity/ev_d2/series_c1.npz',
              'mawi_c25_compressed': 'results/ext_validity/ev_d2/series_c25.npz'}
    for name, rel in (TRACES | extras).items():
        path = ROOT / rel
        if not path.exists():
            result.append(dict(id=name, path=rel, status='MISSING_LOCAL'))
            continue
        trace = load_trace(path)
        result.append(dict(id=name, path=rel, status='AVAILABLE', sha256=sha(path),
            bytes=path.stat().st_size, bin_s=trace['dt'], duration_s=trace['duration_s'],
            train_s=trace['train_s'], test_s=trace['test_s'],
            used_in_grid=name in TRACES, metadata=trace['metadata']))
    return result


def cox_segment(counts, dt, lo, hi, train_mean, lam, rng):
    """One finite chronological segment; times relative to lo*dt."""
    if not 0 <= lo < hi <= len(counts) or min(dt, train_mean) <= 0 or lam < 0:
        raise ValueError('invalid nonperiodic segment')
    multiplicities = rng.poisson(lam * counts[lo:hi] / train_mean * dt)
    indices = np.repeat(np.arange(hi-lo), multiplicities)
    return np.sort((indices + rng.random(len(indices))) * dt)


@dataclass
class Tape:
    bg: list
    bg_unit: list
    flow: np.ndarray
    flow_unit: np.ndarray
    duration: float


def make_tape(trace, case, train, seed):
    rng = np.random.default_rng(seed)
    lo, hi = (0, trace['cut']) if train else (trace['cut'], len(trace['counts'][0]))
    bg = [cox_segment(a, trace['dt'], lo, hi, m, lam, rng)
          for a, m, lam in zip(trace['counts'], trace['train_means'], case['lam'])]
    duration = (hi-lo)*trace['dt']
    # Keep the source, standardized services and managed arrivals in a tape.
    # Both actions, all horizons, ages and populations reuse these draws.
    flow = P.poisson(case['u'], duration, rng)
    return Tape(bg, [rng.exponential(1., len(a)) for a in bg], flow,
                rng.exponential(1., len(flow)), duration)


def history(tape, case, action):
    runs = []
    for j, mu in enumerate(case['mu']):
        at, unit = tape.bg[j], tape.bg_unit[j]
        if j == action:
            at, unit = np.r_[at, tape.flow], np.r_[unit, tape.flow_unit]
            order = np.argsort(at, kind='stable')
            at, unit = at[order], unit[order]
        service = unit / mu
        runs.append((at, P.departures(at, service), service))
    return runs


def occupation(run, start, stop):
    return float(np.maximum(0., np.minimum(run[1], stop)-np.maximum(run[0], start)).sum())


def train_model(trace, case, seed):
    """Finite-prefix time-average slope, not an asserted stationary truth."""
    cpu = time.process_time()
    tape = make_tape(trace, case, True, seed)
    both = [history(tape, case, a) for a in (0, 1)]
    burn = .1*tape.duration
    means = [sum(occupation(r, burn, tape.duration) for r in runs)/(tape.duration-burn)
             for runs in both]
    dt = .2
    ts = np.arange(burn, tape.duration, dt)
    q = np.column_stack([P.backlog(r, ts) for r in both[0]])
    try:
        tint, censored = P.tint(q.sum(axis=1), dt)
    except ValueError:
        tint, censored = None, True
    s_hat = means[1]-means[0]
    static = int(s_hat < 0)
    return dict(s_hat=s_hat, mean_stay=means[0], mean_switch=means[1],
        T_int=tint, T_int_censored=censored, train_seed=seed, burn_s=burn,
        train_s=tape.duration, sample_dt_s=dt, train_means=trace['train_means'],
        static_action=static, alarm_threshold_packets=max(1., float(np.quantile(q[:, static], .9))),
        alarm_definition='stale backlog on static-selected path >= max(1, train q90)',
        CPU_s=time.process_time()-cpu)


def fluid_gap(q, lam, mu, u, h):
    """Switch minus stay; analytically cancel the +/- u*h*h/2 terms.

    This is the EV-D fluid model extended to unequal service capacities.
    Exact saturated ties stay exactly zero, without a decision epsilon.
    """
    q = np.asarray(q, dtype=float)
    if q.shape[-1] != 2 or np.any(q < 0) or h < 0:
        raise ValueError('invalid backlog or horizon')
    parts = []
    for j in (0, 1):
        def correction(load):
            slack = mu[j]-load
            return slack/2*np.maximum(h-q[..., j]/slack, 0.)**2 if slack > 0 else np.zeros(q.shape[:-1])
        v = correction(lam[j])-correction(lam[j]+u)
        if lam[j]+u < mu[j]:
            v = np.where(q[..., j] == 0, u*h*h/2, v)
        parts.append(v)
    return parts[0]-parts[1]


def pending_services(run, t):
    """Actual unfinished services under the common action-0 history."""
    first = int(np.searchsorted(run[1], t, side='right'))
    end = int(np.searchsorted(run[0], t, side='right'))
    pending = run[2][first:end].copy()
    if len(pending):
        pending[0] = run[1][first]-t
    return pending


def path_cost(initial, at, services, h):
    initial_departures = np.cumsum(initial)
    work = float(initial_departures[-1]) if len(initial_departures) else 0.
    dep = P.departures(at, services, work) if len(at) else np.empty(0)
    return float(np.minimum(initial_departures, h).sum() + (np.minimum(dep, h)-at).sum())


def replay_costs(tape, runs, case, t, h):
    """Clairvoyant two-action oracle on the SAME finite realized tape.

    This oracle is a realized-path lower bound; it is not a conditional
    expected-cost oracle. No queue reset, redraw or resampling across h.
    """
    if t < 0 or h < 0 or t+h > tape.duration+1e-9:
        raise ValueError('future outside test trace; periodic replay forbidden')
    f0, f1 = np.searchsorted(tape.flow, [t, t+h], side='right')
    flow, flow_unit = tape.flow[f0:f1]-t, tape.flow_unit[f0:f1]
    costs = np.zeros(2)
    for j in (0, 1):
        initial = pending_services(runs[j], t)
        i0, i1 = np.searchsorted(tape.bg[j], [t, t+h], side='right')
        bg, bg_unit = tape.bg[j][i0:i1]-t, tape.bg_unit[j][i0:i1]
        for action in (0, 1):
            at, unit = (np.r_[bg, flow], np.r_[bg_unit, flow_unit]) if action == j else (bg, bg_unit)
            order = np.argsort(at, kind='stable')
            costs[action] += path_cost(initial, at[order], unit[order]/case['mu'][j], h)
    return costs


def decision_times(duration, tint, n, max_tau):
    # All h share a fixed candidate grid. Long h lose only unavailable tails;
    # per-h candidate counts are saved, never silently replaced with zero.
    start = max(10., 2*tint)+max_tau
    stop = duration-min(H_MULT)*tint
    return np.linspace(start, stop, n) if stop >= start else np.empty(0)


def simulate_case(case, plan, stage, dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=False)
    wall, cpu = time.perf_counter(), time.process_time()
    trace = load_trace(ROOT / TRACES[case['trace']], plan['train_fraction'])
    # Seed depends only on day and stage. Capacity and load comparisons are
    # paired where draws permit it; policy comparisons are always exactly CRN.
    seed = plan['pilot_seed'] if stage == 'pilot' else plan['full_seed']
    seed += list(TRACES).index(case['trace'])*100
    training = train_model(trace, case, seed)
    write_json(dest/'training.json', training)  # before any test tape is built
    n = plan['pilot_points'] if stage == 'pilot' else plan['full_points']
    result = dict(case=case, stage=stage, status='NOT_EVALUABLE', training=training,
                  candidate_points=n, rows=0, test_seed=seed+1000000, support=[])
    rows = []
    if training['T_int'] is not None and not training['T_int_censored'] and training['T_int'] > 0:
        ti = training['T_int']
        ts = decision_times(trace['test_s'], ti, n, max(plan['taus_s']))
        if len(ts):
            tape = make_tape(trace, case, False, seed+1000000)
            runs = history(tape, case, 0)
            for m in plan['h_mult']:
                h = m*ti
                use = ts[ts+h <= tape.duration+1e-9]
                result['support'].append(dict(h_mult=m, h_s=h, n_candidates=len(use),
                    status='AVAILABLE' if len(use) else 'INSUFFICIENT_TEST_DURATION'))
                for index, t in enumerate(use):
                    costs = replay_costs(tape, runs, case, float(t), h)
                    cref, oracle = float(min(costs)), int(costs[1] < costs[0])
                    for tau in plan['taus_s']:
                        q = np.array([P.backlog(r, t-tau).item() for r in runs])
                        gap = float(fluid_gap(q, case['lam'], case['mu'], case['u'], h))
                        hybrid_gap = gap+h*training['s_hat']
                        a0, ah, ast = int(gap < 0), int(hybrid_gap < 0), training['static_action']
                        r0, rh, rs = [float(costs[a]-cref) for a in (a0, ah, ast)]
                        delta = rs-rh
                        rows.append(dict(case_id=case['id'], trace=case['trace'], point=index,
                            t_test_s=float(t), t_trace_s=float(t+trace['train_s']),
                            block=int(t/(tape.duration/8)), h_mult=m, h_s=h, tau_s=tau,
                            alarm=bool(q[ast] >= training['alarm_threshold_packets']),
                            qA=int(q[0]), qB=int(q[1]), fluid_gap=gap, hybrid_gap=hybrid_gap,
                            action_M0=a0, action_static=ast, action_hybrid=ah, action_oracle=oracle,
                            cost_stay=float(costs[0]), cost_switch=float(costs[1]), C_ref=cref,
                            regret_M0=r0, regret_static=rs, regret_hybrid=rh,
                            delta_static_minus_hybrid=delta, disagreement=ast != ah, M0_tie=gap == 0.,
                            delta_pct_Cref=100*delta/cref if cref > 0 else None))
            result['status'] = 'COMPLETE' if rows else 'NOT_EVALUABLE'
        else:
            result['reason'] = 'test segment shorter than warmup + max age + minimum horizon'
    else:
        result['reason'] = 'train T_int unresolved or censored; no fallback timescale'
    if not result['support']:
        result['support'] = [dict(h_mult=m, h_s=None, n_candidates=0, status='NOT_EVALUABLE')
                             for m in plan['h_mult']]
    if rows:
        write_csv(dest/'decisions.csv', rows)
    result.update(rows=len(rows), CPU_s=time.process_time()-cpu, wall_s=time.perf_counter()-wall)
    write_json(dest/'receipt.json', result)
    return result


def mean_or_none(values):
    return float(np.mean(values)) if len(values) else None


def cluster_ci(rows, value='delta_static_minus_hybrid', cluster='block'):
    """Student interval across contiguous-block means, never across instants.

    Blocks can remain dependent and futures overlap. This descriptive interval
    is not an independent-day/population CI. Day intervals are separate below.
    """
    groups = {}
    for row in rows:
        groups.setdefault(row[cluster], []).append(row[value])
    means = [float(np.mean(v)) for v in groups.values()]
    if len(means) < 2:
        return dict(n_clusters=len(means), mean=mean_or_none(means), low=None, high=None)
    center = float(np.mean(means))
    half = float(student_t.ppf(.975, len(means)-1)*np.std(means, ddof=1)/np.sqrt(len(means)))
    return dict(n_clusters=len(means), mean=center, low=center-half, high=center+half)


def summarize(receipts, out, plan):
    from collections import defaultdict
    grouped = defaultdict(list)
    for r in receipts:
        p = Path(out)/r['case']['id']/'decisions.csv'
        if not p.exists():
            continue
        with p.open(newline='') as f:
            for raw in csv.DictReader(f):
                row = dict(raw)
                for k in ('delta_static_minus_hybrid', 'regret_M0', 'regret_static', 'regret_hybrid', 'C_ref'):
                    row[k] = float(row[k])
                for k in ('alarm', 'disagreement', 'M0_tie'):
                    row[k] = row[k] == 'True'
                row['block'] = int(row['block'])
                for population in ('uniform', 'alarm'):
                    if population == 'uniform' or row['alarm']:
                        grouped[(row['case_id'], float(row['h_mult']), float(row['tau_s']), population)].append(row)
    table, by_day = [], defaultdict(list)
    for receipt in receipts:
        case = receipt['case']
        for support in receipt['support']:
            m = support['h_mult']
            for tau in plan['taus_s']:
                for population in ('uniform', 'alarm'):
                    rows = grouped[case['id'], m, tau, population]
                    dis = [r for r in rows if r['disagreement']]
                    cref = mean_or_none([r['C_ref'] for r in rows])
                    delta = mean_or_none([r['delta_static_minus_hybrid'] for r in rows])
                    ci = cluster_ci(rows)
                    row = dict(case_id=case['id'], trace=case['trace'], scale=case['scale'],
                        muA=case['mu'][0], muB=case['mu'][1], h_mult=m, tau_s=tau, population=population,
                        status='AVAILABLE' if rows else ('NO_ALARMS' if support['n_candidates'] else 'NOT_EVALUABLE'),
                        n=len(rows), n_uniform=support['n_candidates'], n_disagreement=len(dis),
                        disagreement_share=len(dis)/len(rows) if rows else None,
                        M0_tie_count=sum(r['M0_tie'] for r in rows),
                        M0_tie_share=mean_or_none([r['M0_tie'] for r in rows]),
                        mean_Cref=cref, mean_regret_M0=mean_or_none([r['regret_M0'] for r in rows]),
                        mean_regret_static=mean_or_none([r['regret_static'] for r in rows]),
                        mean_regret_hybrid=mean_or_none([r['regret_hybrid'] for r in rows]),
                        mean_delta=delta, delta_pct_ratio_of_means=100*delta/cref if cref and cref > 0 else None,
                        q90_regret_static=float(np.quantile([r['regret_static'] for r in rows], .9)) if rows else None,
                        q90_regret_hybrid=float(np.quantile([r['regret_hybrid'] for r in rows], .9)) if rows else None,
                        mean_delta_when_disagree=mean_or_none([r['delta_static_minus_hybrid'] for r in dis]),
                        mean_static_regret_when_disagree=mean_or_none([r['regret_static'] for r in dis]),
                        mean_hybrid_regret_when_disagree=mean_or_none([r['regret_hybrid'] for r in dis]),
                        block_mean_delta=ci['mean'], block_ci_low=ci['low'], block_ci_high=ci['high'],
                        n_blocks=ci['n_clusters'])
                    table.append(row)
                    if delta is not None:
                        by_day[(m, tau, population)].append(dict(day=case['trace'], delta_static_minus_hybrid=delta))
    write_csv(Path(out)/'summary.csv', table)
    day_rows = []
    for (m, tau, pop), records in sorted(by_day.items()):
        ci = cluster_ci(records, cluster='day')
        day_rows.append(dict(h_mult=m, tau_s=tau, population=pop,
            unit='packet*s; equal-weight within available regime cells then equal-weight days',
            n_days=ci['n_clusters'], mean_delta=ci['mean'], ci_low=ci['low'], ci_high=ci['high']))
    if day_rows:
        write_csv(Path(out)/'day_summary.csv', day_rows)
    return table


def source_hashes():
    names = ['experiments/letter/sweep_trace.py', 'experiments/letter/sweep_trace_gcp.sh',
             'tests/test_sweep_trace.py', 'experiments/ext_validity/packet.py',
             'experiments/ext_validity/trace_cox.py', 'experiments/explore_ctmc/env.sh']
    return {n: sha(ROOT/n) for n in names}


def design(out):
    out = output_path(out)
    out.mkdir(parents=True)
    inventory = trace_inventory()
    if any(r['status'] != 'AVAILABLE' for r in inventory if r['id'] in TRACES):
        raise FileNotFoundError('required existing trace missing; no download attempted')
    cases = []
    for name in TRACES:
        for scale in (.8, 1., 1.2):
            for k, mu in enumerate(((10., 10.), (9.5, 10.5), (10.5, 9.5))):
                cases.append(dict(id=f'{name}_s{round(scale*100)}_c{k}', trace=name,
                    scale=scale, lam=[6.5*scale, 6.8*scale], mu=list(mu), u=1.))
    plan = dict(owner='Doan Van Tai', stage='EXPLORATORY', schema='S1-C-v1',
        train_fraction=.5, h_mult=list(H_MULT), taus_s=list(TAUS), full_points=128, pilot_points=24,
        pilot_seed=211121, full_seed=311121, cases=cases,
        pilot_case='ditl_20230412_s120_c1', source_sha256=source_hashes(),
        trace_sha256={r['path']: r['sha256'] for r in inventory if r.get('used_in_grid')},
        forecast_before_pilot='No pass/fail test; unknown benefit and disagreement. Long h may approach static.',
        reading_rule='Report every supported h/age/population; positive paired delta favors hybrid; no selection gate.',
        paper_rule='Discovery only; confirmation on new data needs a separate author-approved card.',
        inference='Descriptive block-t and day-t intervals; dependence/overlap and n_days<=3 limit inference.')
    write_json(out/'inventory.json', inventory)
    write_json(out/'plan.json', plan)
    with (out/'BRIEF_S1C_TRACE.md').open('x') as f:
        f.write(BRIEF.read_text())
    return plan


def verify_plan(path):
    plan = json.loads(Path(path).read_text())
    for name, expected in (plan['source_sha256'] | plan['trace_sha256']).items():
        if sha(ROOT/name) != expected:
            raise ValueError('changed input: '+name)
    if plan['schema'] != 'S1-C-v1' or plan['h_mult'] != list(H_MULT) or plan['taus_s'] != list(TAUS):
        raise ValueError('unexpected plan schema/horizons/ages')
    return plan


def _worker(args):
    return simulate_case(*args)


def runtime_projection(total_cpu, training_cpu, n_rows, plan):
    if not n_rows:
        return dict(status='NOT_ESTIMABLE', CPU_hours=None, ideal_wall_hours_15_workers=None,
                    reason='No future replay measured; train-only CPU cannot project full sweep.')
    replay_cpu = max(0., total_cpu-training_cpu)
    projection = len(plan['cases'])*(training_cpu + replay_cpu*plan['full_points']/plan['pilot_points'])
    return dict(status='LINEAR_SCENARIO', full_cases=len(plan['cases']), full_points=plan['full_points'],
        CPU_hours=projection/3600, ideal_wall_hours_15_workers=projection/3600/15,
        stress_3x_CPU_hours=3*projection/3600,
        pilot_train_CPU_s=training_cpu, pilot_other_CPU_s=replay_cpu,
        limitation='Linear scenario from one case; no bound/CI/GCP measurement; includes no download or transfer.')


def execute(plan_path, out, stage, workers):
    if workers < 1:
        raise ValueError('workers must be positive')
    plan = verify_plan(plan_path)
    out = output_path(out)
    out.mkdir(parents=True)
    selected = [c for c in plan['cases'] if c['id'] == plan['pilot_case']] if stage == 'pilot' else plan['cases']
    wall = time.perf_counter()
    write_json(out/'started.json', dict(owner='Doan Van Tai', stage=stage, workers=workers,
        plan_sha256=sha(plan_path), source_sha256=plan['source_sha256'], case_ids=[c['id'] for c in selected]))
    tasks = [(c, plan, stage, str(out/c['id'])) for c in selected]
    if workers == 1:
        receipts = [_worker(t) for t in tasks]
    else:
        with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context('spawn')) as pool:
            receipts = list(pool.map(_worker, tasks))
    # Save raw checksums BEFORE reading the decision rows for summaries.
    write_json(out/'raw_manifest.json', {str(p.relative_to(out)): sha(p)
               for p in sorted(out.rglob('*')) if p.is_file()})
    table = summarize(receipts, out, plan)
    total_cpu = sum(r['CPU_s'] for r in receipts)
    result = dict(stage=stage, status='COMPLETE', cases=len(receipts), rows=sum(r['rows'] for r in receipts),
        not_evaluable_cases=sum(r['status'] != 'COMPLETE' for r in receipts),
        CPU_s=total_cpu, wall_s=time.perf_counter()-wall, workers=workers,
        hardware=dict(platform=platform.platform(), numpy=np.__version__),
        raw_manifest_sha256=sha(out/'raw_manifest.json'), summary_cells=len(table))
    if stage == 'pilot':
        # Treat every full case as a 4-hour DITL job, then scale replay linearly
        # by candidate count. Other days are shorter; high-load cases can still
        # have larger T_int. This is a scenario, not a bound or a cloud timing.
        training_cpu = sum(r['training']['CPU_s'] for r in receipts)
        result['projection'] = runtime_projection(total_cpu, training_cpu, result['rows'], plan)
    write_json(out/'summary.json', result)
    return result


def reference(out):
    """Re-run one existing EV-D4b train case; no EV test outcome generation."""
    out = output_path(out)
    out.mkdir(parents=True)
    case = json.loads((ROOT/'results/ext_validity/ev_d4b/cases.json').read_text())[0]
    old_path = ROOT/'results/ext_validity/ev_d4b/train'/f"{case['id']}_s{case['seed']}.json"
    old = json.loads(old_path.read_text())
    new = P.train(case)
    fields = ('mean_stay', 'mean_switch', 's_train', 'T_int')
    comparison = {k: dict(saved=old[k], replay=new[k], abs_error=abs(new[k]-old[k])) for k in fields}
    passed = all(np.isclose(old[k], new[k], rtol=1e-11, atol=1e-11) for k in fields)
    passed = passed and old['T_int_censored'] == new['T_int_censored']
    result = dict(status='PASS' if passed else 'FAIL', case=case, reference_path=str(old_path.relative_to(ROOT)),
        reference_sha256=sha(old_path), comparison=comparison, CPU_s=new['CPU'],
        note='Legacy periodic full-trace calibration only; S1-C uses chronological prefixes instead.')
    write_json(out/'reference.json', result)
    if not passed:
        raise AssertionError('EV-D4b train reproduction failed')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('design', 'reference', 'pilot', 'run'))
    parser.add_argument('--out', required=True)
    parser.add_argument('--plan', default=str(OUT/'design_ready/plan.json'))
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args(argv)
    if args.command == 'design':
        result = design(args.out)
        result = dict(cases=len(result['cases']), pilot_case=result['pilot_case'])
    elif args.command == 'reference':
        result = reference(args.out)
    else:
        result = execute(args.plan, args.out, 'pilot' if args.command == 'pilot' else 'full', args.workers)
    print(json.dumps(result, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
