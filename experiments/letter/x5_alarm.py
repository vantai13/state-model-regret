"""Doan Van Tai — X5 congestion-triggered decisions under CARD_X5.md.

Preparation commands never call truth or score. Existing X4b files are inputs.
All outputs are exclusive writes; truth is a single invocation without resume.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
from pathlib import Path
import platform
import resource
import time
import traceback

import numpy as np

from experiments.letter import x4b as B

X, C, S, T, R = B.X, B.C, B.S, B.T, B.R
ROOT = B.ROOT
OUT = ROOT / 'results/letter/x5_alarm'
BRIEF = Path('/home/vantai/state-model-regret-papers/letter_smr/briefs/strengthen2/DESIGN_X5_ALARM.md')
M, N, MIN_ALARMS, ALARM_SERVICE_S = 512, 32, 8, .001
TEST_SEED, PILOT_SEED = 7000001, 7000003
K, R_DEC, R_EVAL = B.K, B.R_DEC, B.R_EVAL
H_SECONDS, PIPES, SIDES = B.H_SECONDS, B.PIPES, B.SIDES
LOCK_SCHEMA = 'x5-alarm-lock-v1'
npz, read_npz, emit = B.npz, B.read_npz, B.emit


def parameters():
    return dict(M=M, N=N, MIN_ALARMS=MIN_ALARMS, ALARM_SERVICE_S=ALARM_SERVICE_S,
        K=K, R_dec=R_DEC, R_eval=R_EVAL, h_seconds=H_SECONDS.tolist(),
        tau_seconds=list(S.TAU_SECONDS), dt_s=S.DT, pipelines=list(PIPES), sides=list(SIDES),
        test_seed=TEST_SEED, pilot_seed=PILOT_SEED, namespace='X5|regime|date',
        evaluability_capacity_Mbps=B.EVALUABILITY_CAPACITY_MBPS)


def source_paths():
    paths = {'repo:'+str(p): ROOT / p for p in X.source_paths()}
    for name in ('experiments/letter/x4b.py', 'experiments/explore_ctmc/env.sh',
                 'results/letter/x4b/configuration.json', 'results/letter/x4b/configuration.npz',
                 'results/letter/x4b/training_summary.json', 'results/letter/x4b/inputs.json',
                 'results/letter/v7_3/data_manifest.json'):
        paths['repo:'+name] = ROOT / name
    paths.update({'sndlib:archive': T.data_root() / B.D.TM_NAME,
                  'sndlib:topology': T.data_root() / 'sndlib-networks-native/geant.txt'})
    return paths


def configure(out=OUT):
    out = Path(out)
    T.new(out / 'configuration.json', out / 'DESIGN_X5_ALARM.md')
    config = C.read_json(B.OUT / 'configuration.json')
    arrays = read_npz(B.OUT / 'configuration.npz')
    records = B.planned_truth_records(B.OUT)
    slopes = C.read_json(B.OUT / 'training_summary.json')['s_hat_pooled_Mbit']
    if [r['id'] for r in config['regimes']] != ['NEWB1', 'NEWB2', 'NEWB3']:
        raise ValueError('X5 requires unchanged NEWB1--3')
    for r, info in enumerate(config['regimes']):
        e = info['e_star_index']
        threshold = ALARM_SERVICE_S * B.regime_capacity(arrays, r)[e]
        info['alarm_threshold_Mbit'] = float(threshold)
        if not np.isfinite(slopes[info['id']]):
            raise ValueError('nonfinite inherited train slope')
    sources = {name: dict(path=str(p), sha256=C.sha256(p)) for name, p in sorted(source_paths().items())}
    brief = BRIEF.read_text()
    B.text_file(out / 'DESIGN_X5_ALARM.md', brief)
    config.update(schema='x5-alarm-configuration-v1', owner='Doan Van Tai',
        parameters=parameters(), sources=sources, s_hat_pooled_Mbit=slopes, test_records=records,
        brief_source=str(BRIEF), brief_sha256=C.sha256(BRIEF),
        brief_snapshot_sha256=C.sha256(out / 'DESIGN_X5_ALARM.md'),
        card_sha256=C.sha256(out / 'CARD_X5.md'),
        exposure='Same 60 X4b test-S regime/day records; new X5 alarm selection and RNG namespace.',
        choices=dict(tie_pool='Fresh M0 once per instance,h over all seven holds; no duplicate stale age.',
            T1='No additional evaluability filter; daily paired percentages as X4b.',
            T3='Mean of daily M0 fresh regret percentages within each regime at 7200s.',
            T4='One trial per evaluable regime/day; require max of fresh and BOTH stale-age mean regrets <=0.5%.',
            pilot='Rank non-RARE step0 records by X4b input-only work proxy; screen with pilot seed, take first two non-RARE.',
            timing='First highest input-work record is reused in step0; stop if its projected total local wall exceeds 40 minutes.'))
    C.write_json(out / 'configuration.json', config)
    return dict(records=len(records), regimes=config['regimes'])


def check_sources(out):
    out = Path(out)
    config = C.read_json(out / 'configuration.json')
    if config.get('schema') != 'x5-alarm-configuration-v1' or config['parameters'] != parameters():
        raise ValueError('X5 stage/count/parameter override or configuration drift')
    now = {name: C.sha256(p) for name, p in sorted(source_paths().items())}
    if now != {name: item['sha256'] for name, item in config['sources'].items()}:
        raise ValueError('X4b source/input drift')
    if C.sha256(out / 'CARD_X5.md') != config['card_sha256']:
        raise ValueError('CARD_X5 drift')
    if C.sha256(out / 'DESIGN_X5_ALARM.md') != config['brief_sha256']:
        raise ValueError('X5 brief snapshot drift')
    if BRIEF.exists() and C.sha256(BRIEF) != config['brief_sha256']:
        raise ValueError('X5 original brief drift')
    if config['test_records'] != B.planned_truth_records(B.OUT):
        raise ValueError('X4b 60-record test-S plan drift')
    return config


def load_context(out=OUT):
    out = Path(out)
    config = check_sources(out)
    token = C.VerifiedLock(str((out / 'configuration.json').resolve()), C.sha256(out / 'configuration.json'))
    dates = sorted({r['date'] for r in config['test_records']})
    data, exclusions = B.V3.load_days(dates, config, verified=token)
    if exclusions or set(data['dates']) != set(dates):
        raise ValueError('locked test dates excluded: '+repr(exclusions))
    return dict(test=data), read_npz(B.OUT / 'configuration.npz'), config


def seeds_for(seed, regime, date):
    root = T.seed_for(seed, f'X5|{regime}|{date}')
    return dict(base=seed, record=root, **{label: T.seed_for(root, label) for label in
        ('warm', 'rate', 'posterior-300.0', 'posterior-900.0', 'reference-decision', 'evaluation')})


def decision_record_x5(data, arrays, config, record, s_hat, *, seed,
                       m=M, n=N, k=K, min_alarms=MIN_ALARMS,
                       alarm_threshold=None, horizons=H_SECONDS, streams=None):
    cpu, wall = time.process_time(), time.perf_counter()
    if min(m, n, k, min_alarms) < 1 or n > m:
        raise ValueError('positive counts and N <= M required')
    j, r, inc, cap = B.record_inputs(data, arrays, config, record)
    info = config['regimes'][r]
    e_star = int(info['e_star_index'])
    threshold = float(info.get('alarm_threshold_Mbit', ALARM_SERVICE_S*cap[e_star])
                      if alarm_threshold is None else alarm_threshold)
    if np.isnan(threshold):
        raise ValueError('NaN alarm threshold')
    streams = seeds_for(seed, record['regime'], record['date']) if streams is None else streams
    times = {}
    fresh, stale = R.timer(times, 'warmup', lambda: S.warm_instances(inc, data['warm'][j], cap, m, streams['warm']))
    candidate_queues = fresh[1][:, e_star].copy()
    mask = candidate_queues >= threshold
    indices = np.flatnonzero(mask)[:n]
    alarms = int(mask.sum())
    fresh = tuple(v[indices] for v in fresh)
    stale = {tau: tuple(v[indices] for v in state) for tau, state in stale.items()}
    selected = len(indices)
    raw = dict(fresh_modes=fresh[0], fresh_queues=fresh[1],
        stale_modes=np.stack([stale[t][0] for t in S.TAU_SECONDS], axis=1),
        stale_queues=np.stack([stale[t][1] for t in S.TAU_SECONDS], axis=1),
        selected_indices=indices, candidate_alarm_queues_Mbit=candidate_queues, alarm_mask=mask,
        h_seconds=np.asarray(horizons), tau_seconds=np.array(S.TAU_SECONDS),
        pipelines=np.array(PIPES), sides=np.array(SIDES), capacity_Mbps=cap, s_hat_Mbit=np.array(s_hat))
    meta = dict(record, owner='Doan Van Tai', seed_base=seed, streams=streams,
        candidates=m, alarms=alarms, selected_indices=indices.tolist(), N=selected, K=k,
        alarm_threshold_Mbit=threshold, e_star_index=e_star, timings=times,
        stage='decisions-only', status='ALARM_RARE' if alarms < min_alarms else 'SELECTED',
        evaluation_called=False, C_ref_computed=False)
    if alarms >= min_alarms:
        profile = arrays['profiles'][0]
        costs = [R.timer(times, 'M0_fresh', lambda: B.mean_forecast(inc, profile, cap, *fresh, horizons))]
        util = [X.path_utilizations(inc, data['days'][j, 0], fresh[0], cap, info['managed_index'])]
        posterior_means = []
        for tau in S.TAU_SECONDS:
            pm, pq = R.timer(times, f'posterior_{int(tau)}', lambda tau=tau: S.forward_posterior(
                inc, data['warm'][j, -1], cap, stale[tau], tau, k, streams[f'posterior-{tau}']))
            costs.append(R.timer(times, f'M0_stale_{int(tau)}', lambda: B.mean_forecast(
                inc, profile, cap, pm, pq, horizons).reshape(selected, k, 2, len(horizons)).mean(axis=1)))
            mean = pm.reshape(selected, k, -1).mean(axis=1)
            posterior_means.append(mean)
            util.append(X.path_utilizations(inc, data['days'][j, 0], mean, cap, info['managed_index']))
        decisions, ties = zip(*(X.fluid_choices(c, s_hat, horizons) for c in costs))
        raw.update(decisions=np.stack(decisions, axis=2), tie_flags=np.stack(ties, axis=2),
            M0_predicted_fresh=costs[0], M0_predicted_stale=np.stack(costs[1:], axis=1),
            path_utilization=np.stack(util, axis=1), posterior_mean_modes=np.stack(posterior_means, axis=1))
    meta.update(CPU_s=time.process_time()-cpu, wall_s=time.perf_counter()-wall,
        peak_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
    return raw, meta


_CONTEXT = None


def _initialize(context, out, token=None):
    global _CONTEXT
    _CONTEXT = context, Path(out), token


def _decision_worker(record):
    (datasets, arrays, config), out, _ = _CONTEXT
    raw, meta = decision_record_x5(datasets['test'], arrays, config, record,
        config['s_hat_pooled_Mbit'][record['regime']], seed=TEST_SEED)
    return X.publish(out, 'step0/test', record, raw, meta)


def run_jobs(fn, records, context, out, workers, token=None):
    if workers < 1:
        raise ValueError('positive workers required')
    if workers == 1:
        _initialize(context, out, token)
        return [fn(r) for r in records]
    with ProcessPoolExecutor(workers, mp_context=mp.get_context('spawn'), initializer=_initialize,
                             initargs=(context, out, token)) as pool:
        return list(pool.map(fn, records, chunksize=1))


def signal_gate(rows):
    qualifying = [r for r in rows if r['side'] == 'fresh' and r['h_s'] <= 1800
        and r['records'] >= 5 and r['denominator'] > 0 and 20*r['numerator'] >= r['denominator']]
    return dict(verdict='SIGNAL_OK' if qualifying else 'NOT_ENOUGH_SIGNAL',
        threshold=.05, minimum_records=5, qualifying_cells=qualifying)


def signal_tables(out, records):
    groups, ties, metas = {}, {}, []
    for record in records:
        stem = Path(out) / 'step0/test' / f"{record['regime']}_{record['date']}"
        meta, raw = C.read_json(stem.with_suffix('.json')), read_npz(stem.with_suffix('.npz'))
        metas.append(meta)
        if meta['status'] == 'ALARM_RARE':
            continue
        for ih, h in enumerate(H_SECONDS):
            for side, label in enumerate(SIDES):
                g = groups.setdefault((record['regime'], int(h), label), [0, 0, 0])
                g[0] += int(np.count_nonzero(raw['decisions'][:, 1, side, ih] != raw['decisions'][:, 2, side, ih]))
                g[1] += meta['N']
                g[2] += 1
            g = ties.setdefault((record['regime'], int(h)), [0, 0])
            g[0] += int(raw['tie_flags'][:, 0, 0, ih].sum())
            g[1] += meta['N']
    disagreement = [dict(regime=regime, h_s=h, side=side, numerator=v[0], denominator=v[1],
        records=v[2], share=v[0]/v[1]) for (regime, h, side), v in sorted(groups.items())]
    tie_rows = [dict(regime=regime, h_s=h, numerator=v[0], denominator=v[1], share=v[0]/v[1])
        for (regime, h), v in sorted(ties.items())]
    num, den = sum(v[0] for v in ties.values()), sum(v[1] for v in ties.values())
    return dict(records=metas, disagreement=disagreement, M0_fresh_ties=tie_rows,
        M0_fresh_tie_pooled=dict(numerator=num, denominator=den, share=num/den if den else None),
        alarm_rare_records=sum(m['status'] == 'ALARM_RARE' for m in metas),
        alarm_candidates=sum(m['candidates'] for m in metas), alarms=sum(m['alarms'] for m in metas),
        selected_instances=sum(m['N'] for m in metas if m['status'] != 'ALARM_RARE'))


def step0(out=OUT, workers=1):
    out = Path(out)
    if workers not in range(1, 9):
        raise ValueError('local step0 uses 1--8 workers')
    T.new(out / 'step0')
    wall = time.perf_counter()
    context = load_context(out)
    records = context[2]['test_records']
    ranked = sorted(records, key=lambda r: (-B.pilot_work_proxy(context[0]['test'], context[1], context[2], r), r['regime'], r['date']))
    (out / 'step0').mkdir(exist_ok=False)
    C.write_json(out / 'step0/started.json', dict(owner='Doan Van Tai', stage='decisions-only',
        workers=workers, source_sha256=C.sha256(__file__), test_outcomes_computed=False))
    first = run_jobs(_decision_worker, ranked[:1], context, out, 1)[0]
    estimate = first['wall_s'] * (1+(len(records)-1)/workers)
    preflight = dict(record=ranked[0], CPU_s=first['CPU_s'], wall_s=first['wall_s'],
        workers=workers, records=len(records), projected_wall_s=estimate,
        local_limit_s=2400, continue_local=estimate <= 2400,
        estimate_is_not_guarantee=True, first_record_reused=True)
    C.write_json(out / 'step0/preflight.json', preflight)
    emit(dict(preflight=preflight))
    if estimate > 2400:
        return dict(status='LOCAL_RUNTIME_LIMIT', preflight=preflight, complete=False)
    run_jobs(_decision_worker, ranked[1:], context, out, workers)
    result = signal_tables(out, records)
    result.update(owner='Doan Van Tai', stage='decisions-only', complete=True,
        decisions_record_count=len(records), parameters=parameters(), gate=signal_gate(result['disagreement']),
        CPU_s_records=sum(m['CPU_s'] for m in result['records']), wall_s=time.perf_counter()-wall,
        evaluation_called=False, C_ref_computed=False, test_outcomes_computed=False,
        counts_are_not_independent_trials=True)
    C.write_json(out / 'step0/summary.json', result)
    T.write_csv(out / 'step0/disagreement.csv', result['disagreement'])
    T.write_csv(out / 'step0/M0_fresh_ties.csv', result['M0_fresh_ties'])
    T.write_csv(out / 'step0/alarms.csv', [{k: m[k] for k in
        ('regime', 'date', 'candidates', 'alarms', 'N', 'status', 'alarm_threshold_Mbit', 'e_star_index')}
        for m in result['records']])
    return result


def require_signal(out):
    summary = C.read_json(Path(out) / 'step0/summary.json')
    if not summary.get('complete') or summary['gate']['verdict'] != 'SIGNAL_OK':
        raise ValueError('NOT_ENOUGH_SIGNAL: no pilot, lock or truth')
    return summary


def planned_truth_records(out):
    config = C.read_json(Path(out) / 'configuration.json')
    summary = require_signal(out)
    selected = {(m['regime'], m['date']) for m in summary['records'] if m['status'] != 'ALARM_RARE'}
    return [r for r in config['test_records'] if (r['regime'], r['date']) in selected]


def outcome_record_x5(context, record, slopes, *, stage, verified=None, out=OUT,
                      m=M, n=N, k=K, min_alarms=MIN_ALARMS, alarm_threshold=None,
                      r_dec=R_DEC, r_eval=R_EVAL, horizons=H_SECONDS, streams=None, _prepared=None):
    if stage not in ('pilot', 'truth'):
        raise ValueError('explicit pilot or truth stage required')
    if record['split'] != 'test' or record['stratum'] != 'S':
        raise ValueError('only planned test-S records may enter pilot/truth')
    if stage == 'truth':
        token = verify_lock(out)
        require_signal(out)
        if not isinstance(verified, C.VerifiedLock) or verified != token:
            raise ValueError('verified X5 truth lock required')
        if (m, n, k, min_alarms, r_dec, r_eval) != (M, N, K, MIN_ALARMS, R_DEC, R_EVAL) or streams is not None or alarm_threshold is not None or _prepared is not None or not np.array_equal(horizons, H_SECONDS):
            raise ValueError('truth cannot override locked stage/counts/streams/threshold/horizons')
        if record not in planned_truth_records(out):
            raise ValueError('record outside locked non-RARE test-S plan')
    datasets, arrays, config = context
    seed = PILOT_SEED if stage == 'pilot' else TEST_SEED
    if _prepared is None:
        raw, meta = decision_record_x5(datasets['test'], arrays, config, record,
            slopes[record['regime']], seed=seed, m=m, n=n, k=k,
            min_alarms=min_alarms, alarm_threshold=alarm_threshold, horizons=horizons, streams=streams)
    else:
        raw, meta = _prepared
    if meta['status'] == 'ALARM_RARE':
        if stage == 'truth':
            raise ValueError('non-RARE truth record became ALARM_RARE')
        return raw, meta
    cpu, wall = time.process_time(), time.perf_counter()
    decision_cpu, decision_wall = meta['CPU_s'], meta['wall_s']
    if stage == 'truth':
        old = read_npz(Path(out) / 'step0/test' / f"{record['regime']}_{record['date']}.npz")
        if set(old) != set(raw):
            raise ValueError('truth differs from step0 keys')
        for key in old:
            if old[key].dtype != raw[key].dtype or old[key].shape != raw[key].shape or old[key].tobytes() != raw[key].tobytes():
                raise ValueError('truth differs from step0: '+key)
    j, _, inc, cap = B.record_inputs(datasets['test'], arrays, config, record)
    selected = len(raw['fresh_modes'])
    def rollout(count, purpose):
        modes, queues = (np.repeat(raw[key], count, axis=0) for key in ('fresh_modes', 'fresh_queues'))
        value = S.variable(inc, datasets['test']['days'][j], cap, modes, queues, meta['streams'][purpose],
            hs=np.rint(np.asarray(horizons)/S.DT).astype(int))[0]
        return value.reshape(selected, count, 2, len(horizons))
    reference = R.timer(meta['timings'], 'reference_decision', lambda: rollout(r_dec, 'reference-decision'))
    evaluation = R.timer(meta['timings'], 'paired_evaluation', lambda: rollout(r_eval, 'evaluation'))
    raw.update(B.paired_metrics(raw, reference, evaluation))
    meta.update(stage=stage, pilot=stage == 'pilot', status='COMPLETE', evaluation_called=True,
        C_ref_computed=True, R_dec=r_dec, R_eval=r_eval,
        CPU_s=decision_cpu+time.process_time()-cpu, wall_s=decision_wall+time.perf_counter()-wall,
        peak_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        G_S='L_stale-L_fresh', units=dict(cost='Mbit*s', backlog='Mbit', capacity='Mbit/s', time='s'))
    return raw, meta


def pilot(out=OUT):
    out = Path(out)
    summary = require_signal(out)
    T.new(out / 'pilot')
    context = load_context(out)
    data, arrays, config = context[0]['test'], context[1], context[2]
    ranks = sorted([(B.pilot_work_proxy(data, arrays, config, r), r) for r in planned_truth_records(out)],
        key=lambda item: (-item[0], item[1]['regime'], item[1]['date']))
    (out / 'pilot').mkdir(exist_ok=False)
    selected, screened = [], []
    for work, record in ranks:
        raw, meta = decision_record_x5(data, arrays, config, record,
            config['s_hat_pooled_Mbit'][record['regime']], seed=PILOT_SEED)
        screened.append(X.publish(out, 'pilot/screen', record, raw, meta.copy()))
        if meta['status'] != 'ALARM_RARE':
            selected.append((work, record, raw, meta))
        if len(selected) == 2:
            break
    C.write_json(out / 'pilot/selection.json', dict(owner='Doan Van Tai', seed=PILOT_SEED,
        no_outcomes_used_in_selection=True, screened=screened,
        records=[r for _, r, _, _ in selected], ranking=[dict(record=r, work_proxy=w) for w, r in ranks]))
    if len(selected) != 2:
        raise ValueError('fewer than two pilot-seed non-RARE records; preserve screening')
    metas = []
    for _, record, raw, meta in selected:
        raw, meta = outcome_record_x5(context, record, config['s_hat_pooled_Mbit'], stage='pilot',
            out=out, _prepared=(raw, meta))
        metas.append(X.publish(out, 'pilot/records', record, raw, meta))
    eligible = len(planned_truth_records(out))
    mean_cpu = float(np.mean([r['CPU_s'] for r in metas]))
    max_cpu = max(r['CPU_s'] for r in metas)
    result = dict(owner='Doan Van Tai', stage='pilot', seed=PILOT_SEED, records=metas,
        actual_truth_eligible_records=eligible, mean_CPU_s=mean_cpu, max_CPU_s=max_cpu,
        CPU_s_records=sum(r['CPU_s'] for r in metas),
        CPU_s_screening_only=sum(r['CPU_s'] for r in screened if r['status'] == 'ALARM_RARE'),
        projected_CPU_hours=mean_cpu*eligible/3600, projected_max_pilot_CPU_hours=max_cpu*eligible/3600,
        ideal_wall_hours_30_workers=mean_cpu*eligible/(30*3600),
        step0_CPU_s=summary['CPU_s_records'], hardware=dict(platform=platform.platform(), numpy=np.__version__),
        limitations=['Two input-work-ranked local pilot records, distinct seed; not test-seed truth.',
            'Linear extrapolation, ideal parallel division, no cloud measurement, guarantee or confidence interval.',
            'Pilot-seed outcomes are exposure; no card scoring.'])
    C.write_json(out / 'pilot/summary.json', result)
    return result


def validate_preparation(out):
    out = Path(out)
    config, summary = check_sources(out), require_signal(out)
    records = config['test_records']
    if len(records) != 60 or len({(r['regime'], r['date']) for r in records}) != 60:
        raise ValueError('exactly 60 distinct test-S records required')
    if summary['parameters'] != parameters() or summary['decisions_record_count'] != 60:
        raise ValueError('incomplete step0 or stage/count override')
    expected = {f"{r['regime']}_{r['date']}{ext}" for r in records for ext in ('.npz', '.json')}
    if {p.name for p in (out / 'step0/test').iterdir()} != expected:
        raise ValueError('incomplete/extra step0 records')
    recomputed = signal_tables(out, records)
    for key, value in recomputed.items():
        if summary[key] != value:
            raise ValueError('step0 summary mismatch: '+key)
    if summary['gate'] != signal_gate(recomputed['disagreement']):
        raise ValueError('step0 signal gate mismatch')
    for meta in recomputed['records']:
        stem = out / 'step0/test' / f"{meta['regime']}_{meta['date']}"
        raw = read_npz(stem.with_suffix('.npz'))
        indices = np.flatnonzero(raw['candidate_alarm_queues_Mbit'] >= meta['alarm_threshold_Mbit'])[:N]
        if (meta['stage'], meta['seed_base'], meta['candidates'], meta['K']) != ('decisions-only', TEST_SEED, M, K):
            raise ValueError('invalid step0 stage/count/seed')
        if meta['N'] != len(indices) or meta['selected_indices'] != indices.tolist() or not np.array_equal(raw['selected_indices'], indices):
            raise ValueError('invalid alarm selection')
        if len(raw['candidate_alarm_queues_Mbit']) != M or meta['alarms'] != int(raw['alarm_mask'].sum()):
            raise ValueError('invalid alarm counts')
        if meta['evaluation_called'] or meta['C_ref_computed'] or {'V', 'C_ref', 'regret', 'costs'}.intersection(raw):
            raise ValueError('step0 contains outcomes')
        if C.sha256(stem.with_suffix('.npz')) != meta['npz_sha256']:
            raise ValueError('step0 raw checksum mismatch')
    if C.read_json(out / 'step0/started.json')['source_sha256'] != C.sha256(__file__):
        raise ValueError('X5 module changed after step0 started')
    pilot_summary = C.read_json(out / 'pilot/summary.json')
    if len(pilot_summary['records']) != 2 or any(m['stage'] != 'pilot' or m['seed_base'] != PILOT_SEED for m in pilot_summary['records']):
        raise ValueError('two complete pilot-seed records required')
    return summary


def lock_paths(out):
    out = Path(out)
    paths = source_paths()
    for name in ('experiments/letter/x5_alarm.py', 'experiments/letter/x5_alarm_card.py',
                 'experiments/letter/x5_gcp.sh', 'tests/test_x5_alarm.py'):
        paths['repo:'+name] = ROOT / name
    for name in ('configuration.json', 'DESIGN_X5_ALARM.md', 'CARD_X5.md',
                 'step0/summary.json', 'step0/started.json', 'step0/preflight.json',
                 'step0/disagreement.csv', 'step0/M0_fresh_ties.csv', 'step0/alarms.csv',
                 'pilot/selection.json', 'pilot/summary.json'):
        paths['output:'+name] = out / name
    for folder in ('step0/test', 'pilot/screen', 'pilot/records'):
        for p in sorted((out / folder).glob('*')):
            if p.is_file():
                paths['output:'+str(p.relative_to(out))] = p
    return paths


def create_lock(out=OUT):
    out = Path(out)
    T.new(out / 'lock.json', out / 'truth')
    summary = validate_preparation(out)
    result = dict(owner='Doan Van Tai', schema=LOCK_SCHEMA, parameters=parameters(),
        sha256={name: C.sha256(p) for name, p in sorted(lock_paths(out).items())},
        gate=summary['gate'], truth_records=len(planned_truth_records(out)), committed=False,
        brief_original_sha256=C.read_json(out / 'configuration.json')['brief_sha256'],
        note='Content lock only; no commit, push, SSH, truth or score performed. Brief snapshot supports remote verification.')
    C.write_json(out / 'lock.json', result)
    return result


def verify_lock(out=OUT):
    out = Path(out)
    if not (out / 'lock.json').is_file():
        raise ValueError('X5 lock required before truth/score')
    locked = C.read_json(out / 'lock.json')
    now = {name: C.sha256(p) for name, p in sorted(lock_paths(out).items())}
    if locked.get('schema') != LOCK_SCHEMA or locked.get('parameters') != parameters() or locked['sha256'] != now:
        raise ValueError('X5 lock mismatch or stage/count override')
    check_sources(out)
    return C.VerifiedLock(str((out / 'lock.json').resolve()), C.sha256(out / 'lock.json'))


def _truth_worker(record):
    context, out, token = _CONTEXT
    raw, meta = outcome_record_x5(context, record, context[2]['s_hat_pooled_Mbit'],
        stage='truth', verified=token, out=out)
    return X.publish(out, 'truth/records', record, raw, meta)


def truth(out=OUT, workers=30):
    """Explicit future Claude command; never called during preparation."""
    if workers < 1:
        raise ValueError('positive workers required')
    out = Path(out)
    token = verify_lock(out)
    validate_preparation(out)
    records = planned_truth_records(out)
    (out / 'truth').mkdir(exist_ok=False)
    start = time.perf_counter()
    C.write_json(out / 'truth/started.json', dict(owner='Doan Van Tai', status='INCOMPLETE',
        records=records, workers=workers, lock_sha256=token.digest,
        seed=TEST_SEED, one_shot=True, retry=False, resume=False))
    result = dict(owner='Doan Van Tai', status='INCOMPLETE', lock_sha256=token.digest, scored=False)
    try:
        context = load_context(out)
        metas = run_jobs(_truth_worker, records, context, out, workers, token)
        if {(m['regime'], m['date']) for m in metas} != {(r['regime'], r['date']) for r in records}:
            raise ValueError('incomplete/extra truth records')
        verify_lock(out)
        manifest = {str(p.relative_to(out)): C.sha256(p)
                    for p in sorted((out / 'truth/records').glob('*')) if p.is_file()}
        manifest['truth/started.json'] = C.sha256(out / 'truth/started.json')
        C.write_json(out / 'truth/raw_manifest.json', dict(owner='Doan Van Tai', sha256=manifest))
        result['status'] = 'COMPLETE'
    except BaseException:
        result['error'] = traceback.format_exc()
        raise
    finally:
        metas = [C.read_json(p) for p in sorted((out / 'truth/records').glob('*.json'))]
        result.update(records=metas, planned_records=len(records), wall_s=time.perf_counter()-start,
            CPU_s_records=sum(m['CPU_s'] for m in metas))
        C.write_json(out / 'truth/receipt.json', result)
    return result


def score(out=OUT):
    """Commit-gated future scoring; never called during preparation."""
    from experiments.letter import x5_alarm_card as card
    out = Path(out)
    token = verify_lock(out)
    require_signal(out)
    T.new(out / 'card_verdicts.json', out / 'REPORT_X5.md')
    receipt = C.read_json(out / 'truth/receipt.json')
    if receipt['status'] != 'COMPLETE' or receipt['lock_sha256'] != token.digest:
        raise ValueError('cannot score INCOMPLETE truth or different lock')
    records = planned_truth_records(out)
    expected = {f"truth/records/{r['regime']}_{r['date']}{ext}" for r in records for ext in ('.npz', '.json')}
    manifest = C.read_json(out / 'truth/raw_manifest.json')['sha256']
    if set(manifest) != expected | {'truth/started.json'}:
        raise ValueError('incomplete/extra raw manifest')
    if {str(p.relative_to(out)) for p in (out / 'truth/records').iterdir()} != expected:
        raise ValueError('incomplete/extra truth directory')
    for name, digest in manifest.items():
        if C.sha256(out / name) != digest:
            raise ValueError('raw checksum mismatch: '+name)
    head = B.require_raw_committed([out / n for n in sorted(manifest)] +
        [out / 'truth/receipt.json', out / 'truth/raw_manifest.json'])
    metas = receipt['records']
    if len(metas) != len(records) or {(m['regime'], m['date']) for m in metas} != {(r['regime'], r['date']) for r in records}:
        raise ValueError('receipt is not the complete planned record set')
    inputs = []
    for meta in metas:
        stem = out / 'truth/records' / f"{meta['regime']}_{meta['date']}"
        if meta != C.read_json(stem.with_suffix('.json')) or (meta['stage'], meta['seed_base'], meta['split'], meta['stratum']) != ('truth', TEST_SEED, 'test', 'S'):
            raise ValueError('invalid truth metadata')
        if C.sha256(stem.with_suffix('.npz')) != meta['npz_sha256']:
            raise ValueError('truth NPZ checksum mismatch')
        inputs.append((read_npz(stem.with_suffix('.npz')), meta))
    result = card.evaluate_raw(inputs)
    screen = C.read_json(out / 'step0/summary.json')
    result['alarm_screen'] = dict(records=screen['decisions_record_count'], alarms=screen['alarms'],
        candidates=screen['alarm_candidates'], alarm_rate=screen['alarms']/screen['alarm_candidates'],
        ALARM_RARE=screen['alarm_rare_records'])
    result.update(lock_sha256=token.digest, raw_commit=head, independent_rescore='PENDING')
    C.write_json(out / 'card_verdicts.json', result)
    B.text_file(out / 'REPORT_X5.md', card.report(result))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('configure', 'step0', 'pilot', 'lock', 'verify-lock', 'truth', 'score'))
    parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--workers', type=int, default=None)
    args = parser.parse_args(argv)
    if args.command in ('step0', 'truth'):
        fn = step0 if args.command == 'step0' else truth
        result = fn(args.out, args.workers if args.workers is not None else (1 if args.command == 'step0' else 30))
    else:
        result = dict(configure=configure, pilot=pilot, lock=create_lock, score=score,
                      **{'verify-lock': verify_lock})[args.command](args.out)
    if isinstance(result, C.VerifiedLock):
        emit(dict(verified=True, lock_sha256=result.digest))
    else:
        emit({k: result[k] for k in ('gate', 'status', 'records', 'decisions_record_count', 'projected_CPU_hours') if k in result and k != 'records'})


if __name__ == '__main__':
    main()
