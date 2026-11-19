"""Doan Van Tai — V7-4 short-hold preparation; truth is a separate, gated command.

Import the unchanged V7-3 data, fluid, posterior, decision and file helpers.
The decisions path has no reference/evaluation/gather call. Only the explicit
pilot and committed-lock truth paths can enter evaluation_rollouts().
"""
import argparse
import ast
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
import json
import multiprocessing as mp
from pathlib import Path
import platform
import resource
import subprocess
import time
import traceback

import numpy as np

from experiments.ext_validity import ev_te as T
from experiments.letter import e4_geant as E
from experiments.letter import v7_3_data as D
from experiments.letter import v7_3_day as A
from experiments.letter import v7_3_run as R
from experiments.letter import v7_3_sim as S
from experiments.letter import v7_3_test as V3
from experiments.letter import v7_3_test_common as C

ROOT = C.ROOT
OUT = ROOT / 'results/letter/v7_4_short'
CARD = OUT / 'CARD_V7_4.md'
TEST_FILE = ROOT / 'tests/test_v7_4_short.py'
BRIEF = Path('/home/vantai/state-model-regret-papers/letter_smr/briefs/V7_4_CODEX_BRIEF.md')
TEST_SEED, PILOT_SEED = 7412001, 7472001
H_SECONDS = np.array([300, 600, 900, 1200, 1800], dtype=int)
N, K, R_DEC, R_EVAL = 32, 64, 64, 128
REGIMES = ('DAY1', 'DAY2', 'DAY3')
SIDES = ('fresh', 'stale')
PIPES = ('M0', 'Hybrid', 'Stationary', 'Hybrid_stable_only', 'Stationary_stable_only')
VARIANTS = {'pooled': (1, 2), 'stable_only': (3, 4)}
EXCLUDED_DATE = '2005-06-27'
EVALUABLE_MBIT = 12.544525


def text_file(path, value):
    C.atomic_write(path, lambda p: p.write_text(value))


def save_npz(path, arrays):
    C.atomic_write(path, lambda p: E.write_npz(p, arrays))


def rel(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def dependencies():
    """Opaque file hashes only; no simulator or test outcome access."""
    params = C.read_json(ROOT / C.PARAMS)
    train = ROOT / params['training_dir']
    paths = {str(p): ROOT / p for p in C.source_paths()}
    for p in (Path(__file__), TEST_FILE, CARD, BRIEF, OUT / 'IMPLEMENTATION.md', ROOT / C.PARAMS,
              D.OUT / 'data_manifest.json', C.OUT / 'inputs.json',
              train / 'configuration.json', train / 'configuration.npz',
              train / 'protocol.json', train / 'summary.json', train / 'day_statistics.csv',
              ROOT / 'experiments/explore_ctmc/env.sh',
              C.OUT / 'records/DAY1_2005-06-16.npz'):
        paths[rel(p)] = p
    root = C.data_root()
    paths.update({'sndlib:archive': root / D.TM_NAME,
                  'sndlib:topology': root / 'sndlib-networks-native/geant.txt',
                  'sndlib:train_cache': root / 'v7_3_train.npz'})
    return paths


def input_fingerprint():
    paths = dependencies()
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise FileNotFoundError('local inputs missing; stop (no remote access): ' + ', '.join(missing))
    hashes = {name: C.sha256(p) for name, p in sorted(paths.items())}
    manifest = C.read_json(D.OUT / 'data_manifest.json')
    for name, field in (('archive', 'sha256'), ('topology', 'topology_sha256'),
                        ('train_cache', 'train_cache_sha256')):
        if hashes['sndlib:' + name] != manifest[field]:
            raise ValueError('SNDlib manifest fingerprint changed: ' + name)
    return dict(owner='Doan Van Tai', schema='v7-4-inputs-v1', sha256=hashes,
                permission='input strata, warmup, posterior and M0 only until explicit pilot/truth',
                code_committed_before_step0=False,
                code_commit_note='Brief forbids commit; CARD step 0 asks committed code. Preparation is hashed but uncommitted for Claude review.')


def preparation_token(out=OUT):
    """Issue V7-3's read token only after manifest/source/input hash checks."""
    path = Path(out) / 'input_fingerprints.json'
    now = input_fingerprint()
    if path.exists():
        if C.read_json(path) != now:
            raise ValueError('preparation input/source hashes changed')
    else:
        C.write_json(path, now)
    return C.VerifiedLock(str(path.resolve()), C.sha256(path))


def selected_records():
    inputs = C.read_json(C.OUT / 'inputs.json')
    manifest = C.read_json(D.OUT / 'data_manifest.json')
    records = [x for x in inputs['records'] if x['regime'] in REGIMES
               and x['stratum'] == 'S' and x['date'] != EXCLUDED_DATE]
    records.sort(key=lambda x: (x['regime'], x['date']))
    if len({(x['regime'], x['date']) for x in records}) != 87:
        raise ValueError('expected 87 distinct input-S records')
    for regime in REGIMES:
        if sum(x['regime'] == regime for x in records) != 29:
            raise ValueError('expected 29 stable days for ' + regime)
    for x in records:
        if (x['date'] not in manifest['test_dates'] or x['date'] in manifest['train_dates']
                or datetime.fromisoformat(x['date']).weekday() >= 5):
            raise ValueError('input selection split/weekday violation')
    return records


def load_context(out=OUT):
    token = preparation_token(out)
    params = C.read_json(ROOT / C.PARAMS)
    if (params['N_test'], params['K'], params['R_dec'], params['R_eval']) != (N, K, R_DEC, R_EVAL):
        raise ValueError('V7-3 population/rollout parameters changed')
    if tuple(params['tau_seconds']) != S.TAU_SECONDS or params['dt_s'] != S.DT:
        raise ValueError('V7-3 age/dt changed')
    train = ROOT / params['training_dir']
    config = C.read_json(train / 'configuration.json')
    with np.load(train / 'configuration.npz', allow_pickle=False) as f:
        arrays = {k: f[k] for k in f.files}
    records = selected_records()
    dates = sorted({x['date'] for x in records})
    data, exclusions = V3.load_days(dates, config, verified=token)
    if exclusions or data['dates'].tolist() != dates:
        raise ValueError('V7-3 input eligibility no longer matches the locked population')
    for x in records:
        j = data['dates'].tolist().index(x['date'])
        r = [i['id'] for i in config['regimes']].index(x['regime'])
        label = V3.strata(data['days'][j], arrays['incidence'][r], arrays['capacity'])
        if label['stratum'] != 'S' or not np.allclose(label['max_utilization_by_action'],
                   x['max_utilization_by_action'], rtol=0, atol=1e-12):
            raise ValueError('input-only stratum mismatch')
    return data, arrays, config, params, records


def record_inputs(data, arrays, config, record):
    dates = data['dates'].tolist()
    if record not in selected_records():
        raise ValueError('record outside the predeclared 87 input-S records')
    j = dates.index(record['date'])
    r = [x['id'] for x in config['regimes']].index(record['regime'])
    return j, arrays['incidence'][r], float(np.asarray(arrays['capacity']).item())


def seeds_for(seed, regime, date):
    """Keep V7-3 labels verbatim; only the root seed changes."""
    regime_seed = T.seed_for(seed, 'V7-3-A2|' + regime)
    root = T.seed_for(regime_seed, 'V7-3|' + date)
    result = dict(base=seed, regime=regime_seed, record=root)
    result.update({label: T.seed_for(root, label) for label in
                   ('warm', 'posterior-300.0', 'posterior-900.0',
                    'reference-decision', 'evaluation')})
    return result


def choices(costs, pooled, stable, horizons):
    """Only assemble pipelines; the V7-3 imported helpers decide every action."""
    n, _, nh = costs.shape
    plain = E.pick(costs)
    hybrid = E.pick(E.hybrid_costs(costs, [0., pooled], horizons))
    sensitive = E.pick(E.hybrid_costs(costs, [0., stable], horizons))
    stationary = np.full((n, nh), int(pooled < 0), dtype=np.int16)
    stable_stationary = np.full((n, nh), int(stable < 0), dtype=np.int16)
    d = np.stack((plain[0], hybrid[0], stationary, sensitive[0], stable_stationary), axis=1)
    ties = np.stack((plain[1], hybrid[1], np.full((n, nh), pooled == 0),
                     sensitive[1], np.full((n, nh), stable == 0)), axis=1)
    return d, ties


def decision_record(data, arrays, config, params, record, *, seed=TEST_SEED,
                    horizons=H_SECONDS, n=N, k=K):
    """State/posterior/forecast only. No future TM is passed to a forecast."""
    cpu, wall = time.process_time(), time.perf_counter()
    j, inc, cap = record_inputs(data, arrays, config, record)
    h = np.asarray(horizons, dtype=int)
    hs = np.rint(h / S.DT).astype(int)
    if len(h) == 0 or (h <= 0).any() or (np.diff(h) <= 0).any():
        raise ValueError('positive increasing horizons required')
    streams = seeds_for(seed, record['regime'], record['date'])
    times = {}
    fresh, stale = R.timer(times, 'warmup', lambda: S.warm_instances(
        inc, data['warm'][j], cap, n, streams['warm']))
    weekend = int(datetime.fromisoformat(record['date']).weekday() >= 5)
    profile = arrays['profiles'][weekend]
    m0 = R.timer(times, 'M0_fresh', lambda: S.mean_rollout(inc, profile, cap, *fresh, hs=hs))
    nh, nt = len(h), len(S.TAU_SECONDS)
    decisions = np.empty((n, len(PIPES), 2, nt, nh), dtype=np.int16)
    ties = np.empty_like(decisions, dtype=bool)
    pooled = params['s_hat_pooled_Mbit'][record['regime']]
    stable = params['s_hat_S_Mbit_sensitivity'][record['regime']]
    d, t = choices(m0, pooled, stable, h)
    decisions[:, :, 0], ties[:, :, 0] = d[:, :, None, :], t[:, :, None, :]
    old_costs = []
    for index, tau in enumerate(S.TAU_SECONDS):
        pm, pq = R.timer(times, f'posterior_{int(tau)}', lambda tau=tau: S.forward_posterior(
            inc, data['warm'][j, -1], cap, stale[tau], tau, k, streams[f'posterior-{tau}']))
        old = R.timer(times, f'M0_stale_{int(tau)}', lambda: S.mean_rollout(
            inc, profile, cap, pm, pq, hs=hs).reshape(n, k, 2, nh).mean(axis=1))
        old_costs.append(old)
        decisions[:, :, 1, index], ties[:, :, 1, index] = choices(old, pooled, stable, h)
    raw = dict(decisions=decisions, tie_flags=ties, M0_predicted_fresh=m0,
               M0_predicted_stale=np.stack(old_costs, axis=1),
               fresh_modes=fresh[0], fresh_queues=fresh[1], pipelines=np.array(PIPES),
               h_seconds=h, tau_seconds=np.array(S.TAU_SECONDS),
               s_hat_Mbit=np.array([pooled, stable]))
    meta = dict(owner='Doan Van Tai', **record, seed_base=seed, streams=streams,
                N=n, K=k, dt_s=S.DT, h_seconds=h.tolist(), timings=times,
                stage='decisions-only', evaluation_called=False, C_ref_computed=False,
                CPU_s=time.process_time()-cpu, wall_s=time.perf_counter()-wall)
    return raw, meta


def evaluation_rollouts(data, arrays, config, record, raw, count, purpose, seed):
    """The only future-action rollout entry; never called by decisions-only."""
    if purpose not in ('reference-decision', 'evaluation'):
        raise ValueError('unknown evaluation purpose')
    j, inc, cap = record_inputs(data, arrays, config, record)
    streams = seeds_for(seed, record['regime'], record['date'])
    m, q = (np.repeat(raw[key], count, axis=0) for key in ('fresh_modes', 'fresh_queues'))
    costs = S.variable(inc, data['days'][j], cap, m, q, streams[purpose],
                       hs=np.rint(raw['h_seconds']/S.DT).astype(int))[0]
    return costs.reshape(len(raw['fresh_modes']), count, 2, len(raw['h_seconds']))


def reference_metrics(raw, reference_rollouts, evaluation):
    """Unchanged V7-3 reference choice and paired gathers; no hypothesis score."""
    values = evaluation.mean(axis=1)
    reference, ties = E.pick(reference_rollouts.mean(axis=1))
    cref = E.costs_for_decisions(values, reference)
    selected = E.costs_for_decisions(values, raw['decisions'])
    return dict(V=values, reference_decision=reference, reference_tie_flags=ties,
                C_ref=cref, costs=selected, regret=selected-cref[:, None, None, None, :],
                paired_evaluation=evaluation, reference_decision_rollouts=reference_rollouts,
                evaluable=cref.mean(axis=0)/raw['h_seconds'] >= EVALUABLE_MBIT)


def outcome_record(data, arrays, config, params, record, *, stage, verified=None):
    if stage not in ('pilot', 'truth'):
        raise ValueError('outcomes require explicit pilot/truth stage')
    if stage == 'truth':
        V3.checked_token(verified)
    seed = PILOT_SEED if stage == 'pilot' else TEST_SEED
    cpu, wall = time.process_time(), time.perf_counter()
    raw, meta = decision_record(data, arrays, config, params, record, seed=seed)
    if stage == 'truth':
        oldpath = Path(verified.path).parent / 'decision_records' / (record['regime'] + '_' + record['date'] + '.npz')
        with np.load(oldpath, allow_pickle=False) as old:
            for key in ('decisions', 'tie_flags', 'fresh_modes', 'fresh_queues',
                        'M0_predicted_fresh', 'M0_predicted_stale'):
                if not np.array_equal(raw[key], old[key]):
                    raise AssertionError('truth/step0 decisions or states differ before evaluation: ' + key)
        meta['lock_sha256'] = verified.digest
    reference = R.timer(meta['timings'], 'reference_decision', lambda: evaluation_rollouts(
        data, arrays, config, record, raw, R_DEC, 'reference-decision', seed))
    evaluation = R.timer(meta['timings'], 'paired_evaluation', lambda: evaluation_rollouts(
        data, arrays, config, record, raw, R_EVAL, 'evaluation', seed))
    raw.update(reference_metrics(raw, reference, evaluation))
    meta.update(stage=stage, pilot=stage == 'pilot', evaluation_called=True,
                C_ref_computed=True, R_dec=R_DEC, R_eval=R_EVAL,
                CPU_s=time.process_time()-cpu, wall_s=time.perf_counter()-wall,
                axes=dict(decisions=['instance', 'pipeline', 'side', 'tau', 'h'],
                          paired_evaluation=['instance', 'rollout', 'action', 'h']),
                units=dict(cost='Mbit*s', backlog='Mbit', time='s'))
    return raw, meta


def publish_record(out, stage, record, raw, meta):
    folder = 'decision_records' if stage == 'decisions' else stage + '/records'
    stem = Path(out) / folder / (record['regime'] + '_' + record['date'])
    save_npz(stem.with_suffix('.npz'), raw)
    meta['npz_sha256'] = C.sha256(stem.with_suffix('.npz'))
    C.write_json(stem.with_suffix('.json'), meta)
    print(json.dumps({k: meta[k] for k in ('regime', 'date', 'stage', 'CPU_s')}, sort_keys=True), flush=True)
    return meta


def signal_rows(raw, record):
    d, ties = raw['decisions'], raw['tie_flags']
    rows = []
    for side, name in enumerate(SIDES):
        for t, tau in enumerate(raw['tau_seconds']):
            predicted = raw['M0_predicted_fresh'] if side == 0 else raw['M0_predicted_stale'][:, t]
            gap = predicted[:, 1] - predicted[:, 0]
            for v, (hybrid, stationary) in VARIANTS.items():
                rate = raw['s_hat_Mbit'][0 if v == 'pooled' else 1]
                for i, h in enumerate(raw['h_seconds']):
                    rows.append(dict(regime=record['regime'], date=record['date'], variant=v,
                        side=name, tau_s=int(tau), h_s=int(h), denominator=len(d),
                        disagree=int(np.count_nonzero(d[:, hybrid, side, t, i] != d[:, stationary, side, t, i])),
                        M0_ties=int(ties[:, 0, side, t, i].sum()),
                        Hybrid_ties=int(ties[:, hybrid, side, t, i].sum()),
                        abs_gap_gt_h_abs_s=int(np.count_nonzero(np.abs(gap[:, i]) > h*abs(rate)))))
    return rows


def aggregate_signal(rows, *, include_tau):
    groups = {}
    for row in rows:
        populations = ('DAY1_DAY2', 'ALL') if row['regime'] != 'DAY3' else ('DAY3', 'ALL')
        for population in populations:
            fields = dict(population=population, variant=row['variant'], h_s=row['h_s'], side=row['side'])
            if include_tau:
                fields['tau_s'] = row['tau_s']
            key = tuple(fields.items())
            counts = groups.setdefault(key, dict(fields, **{x: 0 for x in (
                'denominator', 'disagree', 'M0_ties', 'Hybrid_ties', 'abs_gap_gt_h_abs_s')}))
            for x in ('denominator', 'disagree', 'M0_ties', 'Hybrid_ties', 'abs_gap_gt_h_abs_s'):
                counts[x] += row[x]
    result = list(groups.values())
    for row in result:
        for field in ('disagree', 'M0_ties', 'Hybrid_ties', 'abs_gap_gt_h_abs_s'):
            row[field + '_share'] = row[field]/row['denominator']
    return sorted(result, key=lambda x: (x['population'], x['variant'], x['h_s'], x.get('tau_s', 0), x['side']))


def signal_verdict(by_h):
    primary = [r for r in by_h if r['population'] == 'DAY1_DAY2' and r['variant'] == 'pooled']
    total = sum(r['disagree'] for r in primary)
    horizons = sorted(r['h_s'] for r in primary if r['side'] == 'fresh' and r['disagree_share'] >= .01)
    return dict(verdict='SIGNAL_OK' if total >= 50 and len(horizons) >= 2 else 'NOT_ENOUGH_SIGNAL',
                primary_disagreements=total, required_disagreements=50,
                fresh_horizons_at_least_1_percent=horizons, required_horizons=2,
                fresh_rule='pool DAY1/DAY2 and both tau values within each h; count fresh again for each tau as CARD says all h/tau/sides',
                evaluable_gate_applied=False,
                interpretation='Decision signal only; no evidence about cheaper actions or H-P1.')


def signal_markdown(summary):
    lines = ['# V7-4 signal — decisions-only', '', 'Người phụ trách: Doan Van Tai.', '',
             '**' + summary['signal_gate']['verdict'] + '**; không rollout đánh giá, C_ref hay regret.', '',
             'Bảng chính: DAY1/DAY2 tầng S, gộp hai τ; mẫu số có lặp cùng fresh qua τ.', '',
             '| h (phút) | variant | phía | bất đồng / n | % bất đồng | % tie M0 | % tie Hybrid | % abs(gap)>h abs(s) |',
             '|---:|---|---|---:|---:|---:|---:|---:|']
    for r in summary['by_h']:
        if r['population'] == 'DAY1_DAY2':
            lines.append(f"| {r['h_s']//60} | {r['variant']} | {r['side']} | {r['disagree']}/{r['denominator']} | "
                         + ' | '.join(f"{100*r[x+'_share']:.6f}" for x in ('disagree', 'M0_ties', 'Hybrid_ties', 'abs_gap_gt_h_abs_s')) + ' |')
    lines += ['', f"Tổng bất đồng chính: {summary['signal_gate']['primary_disagreements']}; "
              f"horizon fresh ≥1%: {summary['signal_gate']['fresh_horizons_at_least_1_percent']} s.", '',
              'Các bảng theo τ, DAY3 và toàn bộ 87 bản ghi nằm trong signal.json. Các số đếm là mẫu số, không phải thử độc lập.',
              f"CPU record: {summary['CPU_s_records']:.6f} s; wall: {summary['wall_s']:.6f} s.", '',
              'Source chưa commit theo brief; SHA được lưu trước bước 0. Claude cần duyệt và commit trước truth.', '']
    return '\n'.join(lines)


def run_decisions(out=OUT):
    out = Path(out)
    if any((out / n).exists() for n in ('decisions_started.json', 'signal.json', 'decision_records')):
        raise FileExistsError('decisions already attempted; never overwrite')
    cpu, wall = time.process_time(), time.perf_counter()
    data, arrays, config, params, records = load_context(out)
    C.write_json(out / 'decisions_started.json', dict(owner='Doan Van Tai', seed=TEST_SEED,
        runner_sha256=C.sha256(__file__), count=len(records), truth_allowed=False))
    rows, metas = [], []
    for record in records:
        raw, meta = decision_record(data, arrays, config, params, record)
        metas.append(publish_record(out, 'decisions', record, raw, meta))
        rows.extend(signal_rows(raw, record))
    by_h = aggregate_signal(rows, include_tau=False)
    summary = dict(owner='Doan Van Tai', stage='decisions-only', seed=TEST_SEED,
        records=metas, record_count=len(records), N=N, K=K,
        evaluation_called=False, C_ref_computed=False, outcomes_computed=False,
        input_fingerprints_sha256=C.sha256(out / 'input_fingerprints.json'),
        by_h=by_h, by_h_tau=aggregate_signal(rows, include_tau=True),
        signal_gate=signal_verdict(by_h), counts_by_record=rows,
        CPU_s_records=sum(x['CPU_s'] for x in metas), CPU_s_command=time.process_time()-cpu,
        wall_s=time.perf_counter()-wall)
    C.write_json(out / 'signal.json', summary)
    text_file(out / 'signal.md', signal_markdown(summary))
    return summary


def pilot_work_proxy(data, arrays, config, record):
    """Only inputs: work envelope of active links/ODs over the longest hold."""
    j, inc, cap = record_inputs(data, arrays, config, record)
    demand = data['days'][j, :2]  # first 1800 s, exactly the longest hold
    upper = (1+S.BETA)*np.einsum('aed,sd->sae', inc, demand, optimize=True)
    active = (upper > cap).any(axis=(0, 1))
    # Include links potentially backlogged after warmup, without any future cost.
    active |= ((1+S.BETA)*np.einsum('ed,sd->se', inc[0], data['warm'][j], optimize=True) > cap).any(axis=0)
    relevant = (inc[:, active] != 0).any(axis=(0, 1))
    return int(np.count_nonzero(inc[:, active][:, :, relevant]) + relevant.sum() + active.sum())


def pilot_selection(context, summary):
    data, arrays, config, _, records = context
    by_key = {(r['regime'], r['date']): r for r in records}
    heaviest = max(summary['records'], key=lambda r: (r['CPU_s'], r['regime'], r['date']))
    first = by_key[heaviest['regime'], heaviest['date']]
    rest = [r for r in records if r != first]
    second = sorted(rest, key=lambda r: (-pilot_work_proxy(data, arrays, config, r), r['regime'], r['date']))[0]
    return dict(owner='Doan Van Tai', seed=PILOT_SEED, records=[first, second],
        rule='record 1: max measured decisions-only CPU (tie: descending regime/date); record 2: max input-only active-link/OD work proxy among remaining (tie: ascending regime/date)',
        heaviest_decisions_CPU_s=heaviest['CPU_s'],
        work_proxies=[pilot_work_proxy(data, arrays, config, x) for x in (first, second)],
        limitations='Heaviest is measured for decisions, not a guarantee of heaviest truth; the second record adds an input-based evaluation-work stress proxy.',
        pilot_outcomes_are_not_test_outcomes=True)


def run_pilot(out=OUT):
    out = Path(out)
    if (out / 'pilot').exists() or (out / 'pilot.json').exists():
        raise FileExistsError('pilot already attempted; never overwrite')
    cpu, wall = time.process_time(), time.perf_counter()
    summary = C.read_json(out / 'signal.json')
    context = load_context(out)
    data, arrays, config, params, records = context
    selection = pilot_selection(context, summary)
    C.write_json(out / 'pilot/selection.json', selection)  # before pilot outcomes
    metas = []
    for record in selection['records']:
        raw, meta = outcome_record(data, arrays, config, params, record, stage='pilot')
        metas.append(publish_record(out, 'pilot', record, raw, meta))
    overhead = max(0., summary['CPU_s_command']-summary['CPU_s_records'])
    projected_mean = overhead + len(records)*float(np.mean([m['CPU_s'] for m in metas]))
    projected = overhead + len(records)*max(m['CPU_s'] for m in metas)
    result = dict(owner='Doan Van Tai', stage='pilot', seed=PILOT_SEED,
        records=metas, N=N, K=K, R_dec=R_DEC, R_eval=R_EVAL,
        selection_sha256=C.sha256(out / 'pilot/selection.json'), expected_truth_records=len(records),
        projected_CPU_s=projected, projected_CPU_hours=projected/3600,
        mean_projected_CPU_s=projected_mean, mean_projected_CPU_hours=projected_mean/3600,
        decision='USE_GCP' if projected > 6*3600 else 'LOCAL', CPU_limit_hours=6,
        projection='input/decision preparation overhead + 87 * max(full-size pilot record CPU); mean projection also reported; no empirical upper bound',
        CPU_s_records=sum(m['CPU_s'] for m in metas), CPU_s_command=time.process_time()-cpu,
        wall_s=time.perf_counter()-wall, outcomes_are_pilot_only=True,
        hardware=dict(platform=platform.platform(), python=platform.python_version(), numpy=np.__version__),
        limitations=['Two pilot records; local CPU estimate can differ from test-seed or cloud cost.',
                    'No truth, no H-P1 score, no selection by pilot action quality.'])
    C.write_json(out / 'pilot.json', result)
    return result


def legacy_seeds():
    values = {int(C.read_json(ROOT / C.PARAMS)['test_seed'])}
    for p in sorted((ROOT / 'experiments/letter').glob('v7_3_*.py')):
        for node in ast.walk(ast.parse(p.read_text())):
            if isinstance(node, ast.Assign) and any('SEED' in ast.unparse(t) for t in node.targets):
                values.update(n.value for n in ast.walk(node.value)
                              if isinstance(n, ast.Constant) and type(n.value) is int)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = node.args.posonlyargs + node.args.args
                pairs = list(zip(args[-len(node.args.defaults):], node.args.defaults)) if node.args.defaults else []
                pairs += list(zip(node.args.kwonlyargs, node.args.kw_defaults))
                for arg, default in pairs:
                    if 'seed' in arg.arg and isinstance(default, ast.Constant) and type(default.value) is int:
                        values.add(default.value)
    return sorted(values | {T.TRAIN_SEED, T.TEST_SEED, T.PILOT_SEED, E.TRAIN_SEED, E.TEST_SEED, E.PILOT_SEED})


def predictions(out=OUT):
    out = Path(out)
    card = CARD.read_text()
    params = C.read_json(ROOT / C.PARAMS)
    records = selected_records()
    signal = C.read_json(out / 'signal.json')
    pilot = C.read_json(out / 'pilot.json')
    return dict(owner='Doan Van Tai', exploration=True, card=rel(CARD),
        card_sha256=C.sha256(CARD), h_seconds=H_SECONDS.tolist(), tau_seconds=list(S.TAU_SECONDS),
        seed_test=TEST_SEED, seed_pilot=PILOT_SEED, legacy_base_seeds=legacy_seeds(),
        seeds_rule='V7-3 hierarchy and labels verbatim; horizons do not enter seeds; same warmup and posterior states in decisions and truth; reference-decision and evaluation separate',
        N=N, K=K, R_dec=R_DEC, R_eval=R_EVAL, dt_s=S.DT, beta=S.BETA,
        records=records, expected_records_all=87, expected_records_primary=58,
        expected_cases_before_evaluable_gate_all=870, expected_cases_before_evaluable_gate_primary=580,
        expected_side_instances_all=55680, expected_side_instances_primary=37120,
        cases_after_evaluable_gate='UNKNOWN until truth; retain every case and store gate flag',
        instance_count_note='32 instances per record x 2 sides x 2 tau x 5 h; repeated days/instances/fresh sides are denominators, not independent tests',
        excluded_date=EXCLUDED_DATE, O_days_included=False,
        s_hat_pooled_Mbit=params['s_hat_pooled_Mbit'], s_hat_stable_only_Mbit=params['s_hat_S_Mbit_sensitivity'],
        capacity_Mbps_actual=C.read_json(ROOT / params['training_dir'] / 'configuration.json')['capacity_Mbps'],
        evaluable_threshold_Mbit=EVALUABLE_MBIT, evaluable_rule='mean(C_ref over 32 instances)/h >= 12.544525; same case gate for both tau and both sides',
        signal_rule_verbatim=card[card.index('**Tiêu chí đủ signal'):card.index('## Metric')].strip(),
        H_P1_reading_rule_verbatim=card[card.index('**H-P1 (chính'):card.index('## Dự báo')].strip(),
        metric_verbatim=card[card.index('## Metric'):card.index('## Quần thể')].strip(),
        forecasts_verbatim=card[card.index('## Dự báo'):card.index('## Luật đưa vào paper')].strip(),
        paper_rule_verbatim=card[card.index('## Luật đưa vào paper'):card.index('## Thực hiện')].strip(),
        signal_gate=signal['signal_gate'], pilot_decision=pilot['decision'],
        H_P1_verdict='NOT_RUN', truth_run=False, raw_before_scoring=True,
        case_b_convention='R_pipeline=max(mean_i(V(action_fresh)-C_ref), mean_i(V(action_stale)-C_ref)); R_Hybrid-R_Stationary; exact CARD relative 1e-9 equality, no additional epsilon',
        instance_a_convention='same per-instance eval rollouts for both actions and all pipelines; sample sd(ddof=1)/sqrt(128); resolved strictly abs(mean delta)>2*se',
        implementation_choices=[
            'All 32 V7-3 warm instances; no subsampling or posterior resampling beyond imported functions.',
            'Stable-only sensitivity uses the existing V7-3 params (DAY1 -320.6, DAY2 -314.0, DAY3 -0.4), not a new fit.',
            'Pilot on two input-S test records with independent pilot seed; record selection saved before pilot outcomes. Pilot never enters H-P1.',
            'Fresh repeats over tau as CARD requests; signal fresh share pools the two tau values within each horizon, with stratified tau tables retained.',
            'Keep full 128 paired action costs and all 64 reference-decision rollouts. No descriptive T_int trace: not requested and cannot enter decisions-only.',
            'Brief forbids commit; source hashed before step 0 rather than committed as CARD step 0 requests. Claude must review/commit the lock before truth.',
            'Lock may be prepared even for NOT_ENOUGH_SIGNAL; truth will still refuse that signal.',
        ])


def preparation_paths(out=OUT):
    out = Path(out)
    paths = dict(dependencies())
    files = [out / x for x in ('input_fingerprints.json', 'decisions_started.json',
             'signal.json', 'signal.md', 'pilot.json', 'pilot/selection.json', 'predictions.json')]
    for folder in ('decision_records', 'pilot/records'):
        files.extend(sorted((out / folder).glob('*.npz')))
        files.extend(sorted((out / folder).glob('*.json')))
    for p in files:
        paths[rel(p)] = p
    return paths


def create_lock(out=OUT):
    out = Path(out)
    if (out / 'lock.json').exists():
        raise FileExistsError('lock already exists; never replace')
    if C.read_json(out / 'input_fingerprints.json') != input_fingerprint():
        raise ValueError('preparation source/input drift')
    signal, pilot = C.read_json(out / 'signal.json'), C.read_json(out / 'pilot.json')
    if signal['record_count'] != 87 or len(pilot['records']) != 2:
        raise ValueError('incomplete signal/pilot')
    for folder, count in (('decision_records', 87), ('pilot/records', 2)):
        for extension in ('npz', 'json'):
            if len(list((out / folder).glob('*.' + extension))) != count:
                raise ValueError('incomplete preparation files: ' + folder)
    value = dict(owner='Doan Van Tai', schema='v7-4-short-lock-v1',
                 sha256={k: C.sha256(p) for k, p in sorted(preparation_paths(out).items())},
                 truth_prerequisites=['lock byte-identical to HEAD commit', 'all file hashes match',
                                      'SIGNAL_OK', 'one-shot output absent'])
    C.write_json(out / 'lock.json', value)
    return value


def verify_committed_lock(out=OUT):
    out = Path(out)
    path = out / 'lock.json'
    if not path.is_file():
        raise ValueError('truth refused: lock.json missing or not committed')
    try:
        saved = subprocess.check_output(['git', 'show', 'HEAD:' + rel(path)], cwd=ROOT, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as error:
        raise ValueError('truth refused: lock.json has not been committed to HEAD') from error
    if saved != path.read_bytes():
        raise ValueError('truth refused: lock.json differs from HEAD commit')
    locked = C.read_json(path)
    actual = {name: C.sha256(p) for name, p in sorted(preparation_paths(out).items())}
    if locked.get('schema') != 'v7-4-short-lock-v1' or locked.get('sha256') != actual:
        raise ValueError('truth refused: locked file hashes differ')
    if C.read_json(out / 'signal.json')['signal_gate']['verdict'] != 'SIGNAL_OK':
        raise ValueError('truth refused: NOT_ENOUGH_SIGNAL')
    return C.sha256(path)


_WORKER = None


def _initialize_truth(context, out, digest):
    global _WORKER
    # No engine call before the parent verified the committed lock.
    if C.sha256(Path(out) / 'lock.json') != digest:
        raise ValueError('truth worker lock changed')
    _WORKER = context, Path(out), C.VerifiedLock(str(Path(out) / 'lock.json'), digest)


def _truth_record(record):
    (data, arrays, config, params, _), out, verified = _WORKER
    raw, meta = outcome_record(data, arrays, config, params, record, stage='truth', verified=verified)
    return publish_record(out, 'truth', record, raw, meta)


def run_truth(out=OUT, workers=1):
    digest = verify_committed_lock(out)  # before any input or engine access
    out = Path(out)
    if workers < 1:
        raise ValueError('positive workers required')
    if (out / 'truth').exists():
        raise FileExistsError('truth already attempted; no retry/resume')
    C.write_json(out / 'truth/started.json', dict(owner='Doan Van Tai', lock_sha256=digest,
        seed=TEST_SEED, workers=workers, HEAD=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()))
    start = time.perf_counter()
    result = dict(owner='Doan Van Tai', status='INCOMPLETE', records=[], lock_sha256=digest,
                  scored=False, note='Commit raw before scoring; this command does not score H-P1.')
    pool = None
    try:
        context = load_context(out)
        if workers == 1:
            _initialize_truth(context, out, digest)
            for record in context[-1]:
                result['records'].append(_truth_record(record))
        else:
            pool = ProcessPoolExecutor(workers, mp_context=mp.get_context('spawn'),
                initializer=_initialize_truth, initargs=(context, out, digest))
            futures = [pool.submit(_truth_record, record) for record in context[-1]]
            for future in as_completed(futures):
                result['records'].append(future.result())
            pool.shutdown(wait=True)
            pool = None
        if len(result['records']) != 87:
            raise ValueError('truth record count mismatch')
        result['status'] = 'COMPLETE'
    except BaseException:
        result['error'] = traceback.format_exc()
        if pool is not None:
            for process in (getattr(pool, '_processes', None) or {}).values():
                if process.is_alive():
                    process.terminate()
            pool.shutdown(wait=True, cancel_futures=True)
        raise
    finally:
        result['records'].sort(key=lambda r: (r['regime'], r['date']))
        result['wall_s'] = time.perf_counter()-start
        result['CPU_s_records'] = sum(x['CPU_s'] for x in result['records'])
        result['children_CPU_s'] = sum(getattr(resource.getrusage(resource.RUSAGE_CHILDREN), k)
                                       for k in ('ru_utime', 'ru_stime'))
        C.write_json(out / 'truth/run_summary.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('decisions', 'pilot', 'truth'))
    parser.add_argument('--workers', type=int, default=1, help='truth only')
    args = parser.parse_args()
    if args.command == 'decisions':
        value = run_decisions()
        print(json.dumps(value['signal_gate'], sort_keys=True))
    elif args.command == 'pilot':
        value = run_pilot()
        C.write_json(OUT / 'predictions.json', predictions())
        create_lock()
        print(json.dumps({k: value[k] for k in ('decision', 'CPU_s_command', 'projected_CPU_hours')}, sort_keys=True))
    else:
        run_truth(workers=args.workers)


if __name__ == '__main__':
    main()
