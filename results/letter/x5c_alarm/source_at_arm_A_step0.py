"""Doan Van Tai — X5c, selected-path alarms and independent eta arms.

Only configure/step0/pilot/lock are preparation. Truth is one-shot and score
requires committed raw files. Existing X5/X4b sources and outputs are inputs.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from functools import partial
import multiprocessing as mp
import os
from pathlib import Path
import platform
import time
import traceback

import numpy as np

from experiments.letter import x5_alarm as A

B, X, C, S, T, R = A.B, A.X, A.C, A.S, A.T, A.R
ROOT = A.ROOT
OUT = ROOT / 'results/letter/x5c_alarm'
BRIEF = Path('/home/vantai/state-model-regret-papers/letter_smr/briefs/strengthen2/DESIGN_X5C_ALARM.md')
CARD = OUT / 'CARD_X5C.md'
X5_CARD = A.OUT / 'CARD_X5.md'
BRIEF_SNAPSHOT = OUT / 'DESIGN_X5C_ALARM.md'
M, N, MIN_ALARMS, ALARM_SERVICE_S = A.M, A.N, A.MIN_ALARMS, A.ALARM_SERVICE_S
K, R_DEC, R_EVAL = A.K, A.R_DEC, A.R_EVAL
H_SECONDS, PIPES, SIDES = A.H_SECONDS, A.PIPES, A.SIDES
ARMS = {'A': dict(beta=.3, test_seed=7100001, pilot_seed=7100003),
        'B': dict(beta=.6, test_seed=7200001, pilot_seed=7200003, train_seed=7200005)}
LOCK_SCHEMA = 'x5c-alarm-lock-v1'
LOCAL_LIMIT_S = 2400
npz, read_npz, emit = B.npz, B.read_npz, B.emit
signal_gate, signal_tables = A.signal_gate, A.signal_tables
_CONTEXT = None


def arm_settings(arm):
    if arm not in ARMS:
        raise ValueError('arm must be A or B')
    return ARMS[arm]


def arm_out(arm, out=None):
    arm_settings(arm)
    return OUT / ('arm_' + arm) if out is None else Path(out)


def parameters(arm):
    setting = arm_settings(arm)
    return dict(A.parameters(), **setting, arm=arm, namespace=f'X5C-{arm}|regime|date')


def _set_simulator(arm):
    """All changes are process-local Python state; no imported file is edited.

    Both keyword defaults capture beta at definition time. Changing only the
    module scalar would leave stochastic warmups/posteriors/rollouts at .3.
    """
    beta = arm_settings(arm)['beta']
    S.BETA = beta
    S.variable.__kwdefaults__ = dict(S.variable.__kwdefaults__ or {}, beta=beta)
    X.expected_loads.__kwdefaults__ = dict(X.expected_loads.__kwdefaults__ or {}, beta=beta)


@contextmanager
def simulator_arm(arm):
    old = S.BETA, S.variable.__kwdefaults__, X.expected_loads.__kwdefaults__
    _set_simulator(arm)
    try:
        yield
    finally:
        S.BETA, S.variable.__kwdefaults__, X.expected_loads.__kwdefaults__ = old


def runtime_beta():
    return dict(S_BETA=S.BETA, variable_default=S.variable.__kwdefaults__['beta'],
                expected_loads_default=X.expected_loads.__kwdefaults__['beta'])


def seeds_for(seed, regime, date, *, arm):
    arm_settings(arm)
    root = T.seed_for(seed, f'X5C-{arm}|{regime}|{date}')
    return dict(base=seed, record=root, **{label: T.seed_for(root, label) for label in
        ('warm', 'rate', 'posterior-300.0', 'posterior-900.0', 'reference-decision', 'evaluation')})


def alarm_spec(info, cap, slope):
    if not np.isfinite(slope):
        raise ValueError('finite train slope required')
    action = int(slope < 0)
    link = int(info['e_star_index'] if action else info['path_bottleneck_indices_after'][0])
    if not 0 <= link < len(cap):
        raise ValueError('invalid selected-path alarm link')
    return dict(alarm_link_index=link, alarm_action='Switch' if action else 'Stay',
        alarm_threshold_Mbit=float(ALARM_SERVICE_S * cap[link]), s_hat_Mbit=float(slope))


def source_paths():
    paths = A.source_paths()
    for name in ('experiments/letter/x5_alarm.py', 'experiments/letter/x5_alarm_card.py'):
        paths['repo:' + name] = ROOT / name
    return paths


def _initialize(context, out, arm, token=None):
    global _CONTEXT
    _set_simulator(arm)
    if any(v != arm_settings(arm)['beta'] for v in runtime_beta().values()):
        raise ValueError('worker eta mismatch')
    _CONTEXT = context, Path(out), arm, token


def run_jobs(fn, records, context, out, workers, arm, token=None):
    if workers < 1:
        raise ValueError('positive workers required')
    with simulator_arm(arm):
        if workers == 1:
            _initialize(context, out, arm, token)
            return [fn(r) for r in records]
        with ProcessPoolExecutor(workers, mp_context=mp.get_context('spawn'), initializer=_initialize,
                                 initargs=(context, out, arm, token)) as pool:
            return list(pool.map(fn, records, chunksize=1))


def _beta_probe(record):
    """Tiny analytic test only; not a physical experiment record."""
    inc = np.ones((1, 1, 1))
    result = S.variable(inc, np.ones((1, 1)), [1.4], np.ones((1, 1)),
                        np.zeros((1, 1)), 11, lengths=[1], hs=[1])
    return dict(pid=os.getpid(), runtime_beta=runtime_beta(),
                queue_Mbit=float(result[2][0, 0, 0]))


def _train_worker(record):
    """Call B.train_record verbatim, with this arm's seed and namespace."""
    context, out, arm, _ = _CONTEXT
    if arm != 'B' or 'test' in context[0]:
        raise ValueError('B training must precede test loading')
    saved = B._CONTEXT, B.TRAIN_SEED, B.seeds_for, X.publish
    original_publish = X.publish
    def publish(directory, folder, rec, raw, meta):
        meta.update(arm=arm, beta=S.BETA, runtime_beta=runtime_beta())
        return original_publish(directory, folder, rec, raw, meta)
    try:
        B._initialize(context, out / 'train', None)
        B.TRAIN_SEED = arm_settings(arm)['train_seed']
        B.seeds_for = partial(seeds_for, arm=arm)
        X.publish = publish
        return B.train_record(record)
    finally:
        B._CONTEXT, B.TRAIN_SEED, B.seeds_for, X.publish = saved


def _training(config, arrays, out, workers):
    T.new(out / 'train')
    wall = time.perf_counter()
    original, _ = B.D.load_training()
    data = B.A.window_training(original, config['start_slot'])
    if data['dates'].tolist() != config['train_dates'] or len(data['dates']) != 26:
        raise ValueError('unchanged 26 X4b train weekdays required')
    context = dict(train=data), arrays, config
    records = B.records_for(data, arrays, config, 'train')
    if len(records) != 78:
        raise ValueError('all 78 train regime/day records required, including O')
    with simulator_arm('B'):
        ranked = sorted(records, key=lambda r: (-B.pilot_work_proxy(data, arrays, config, r), r['regime'], r['date']))
    (out / 'train').mkdir(exist_ok=False)
    C.write_json(out / 'train/started.json', dict(owner='Doan Van Tai', seed=7200005, beta=.6,
        source_sha256=C.sha256(__file__), workers=workers, test_data_loaded=False))
    first = run_jobs(_train_worker, ranked[:1], context, out, 1, 'B')[0]
    estimate = first['wall_s'] * (1 + (len(records) - 1) / workers)
    preflight = dict(record=ranked[0], CPU_s=first['CPU_s'], wall_s=first['wall_s'],
        projected_wall_s=estimate, local_limit_s=LOCAL_LIMIT_S, workers=workers,
        continue_local=estimate <= LOCAL_LIMIT_S, first_record_reused=True,
        estimate_is_not_guarantee=True, test_data_loaded=False)
    C.write_json(out / 'train/preflight.json', preflight)
    emit(dict(train_preflight=preflight))
    if estimate > LOCAL_LIMIT_S:
        return dict(status='LOCAL_RUNTIME_LIMIT', preflight=preflight, complete=False)
    metas = [first] + run_jobs(_train_worker, ranked[1:], context, out, workers, 'B')
    slopes = {r['id']: float(np.mean([m['s_hat_Mbit'] for m in metas if m['regime'] == r['id']]))
              for r in config['regimes']}
    result = dict(owner='Doan Van Tai', arm='B', beta=.6, seed=7200005, N=B.N,
        record_count=len(metas), records=metas, s_hat_pooled_Mbit=slopes, complete=True,
        CPU_s_records=sum(m['CPU_s'] for m in metas), wall_s=time.perf_counter()-wall,
        test_data_loaded=False, method='B.train_record; equal daily pooling of all 26 weekdays, S and O')
    C.write_json(out / 'train/summary.json', result)
    return result


def configure(arm, out=None, workers=8):
    out = arm_out(arm, out)
    if workers not in range(1, 9):
        raise ValueError('local preparation uses 1--8 workers')
    T.new(out / 'configuration.json', out / 'train')
    if not BRIEF_SNAPSHOT.exists():
        B.text_file(BRIEF_SNAPSHOT, BRIEF.read_text())
    if C.sha256(BRIEF_SNAPSHOT) != C.sha256(BRIEF):
        raise ValueError('brief snapshot drift')
    config = C.read_json(B.OUT / 'configuration.json')
    arrays = read_npz(B.OUT / 'configuration.npz')
    if [r['id'] for r in config['regimes']] != ['NEWB1', 'NEWB2', 'NEWB3']:
        raise ValueError('unchanged NEWB1--3 required')
    sources = {name: dict(path=str(p), sha256=C.sha256(p)) for name, p in sorted(source_paths().items())}
    if arm == 'B':
        training = _training(config, arrays, out, workers)
        if not training['complete']:
            return training
        slopes = training['s_hat_pooled_Mbit']
    else:
        slopes = C.read_json(B.OUT / 'training_summary.json')['s_hat_pooled_Mbit']
    # The B summary is on disk before this function opens the X4b test plan.
    records = B.planned_truth_records(B.OUT)
    links = B.D.topology()['links']
    for r, info in enumerate(config['regimes']):
        info.update(alarm_spec(info, B.regime_capacity(arrays, r), slopes[info['id']]))
        info['alarm_link'] = links[info['alarm_link_index']]['id']
    config.update(schema='x5c-alarm-configuration-v1', owner='Doan Van Tai', arm=arm,
        parameters=parameters(arm), sources=sources, s_hat_pooled_Mbit=slopes, test_records=records,
        brief_source=str(BRIEF), brief_sha256=C.sha256(BRIEF_SNAPSHOT),
        card_sha256=C.sha256(CARD), x5_card_sha256=C.sha256(X5_CARD),
        train_summary_sha256=C.sha256(out / 'train/summary.json') if arm == 'B' else None,
        exposure='Same 60 X4b test-S regime/day records, already exposed; new X5c seeds and alarm selection.',
        choices=dict(tie_pool='Fresh M0 once per instance,h across seven holds, no stale duplication.',
            scorer='Unchanged X5 T1--T4 and X5 reporting choices; evaluate each arm separately.',
            pilot='Two highest input-work non-RARE step0 records, screen pilot seed before rollouts.',
            local_runtime='Reuse highest input-work first record for train/step0; project before remaining work.',
            pilot_runtime='Input-work-scaled X4b pilot estimate, then first X5c pilot before second; stop above 40min.',
            zero_slope='Stay when s_hat >= 0, including exact zero.',
            beta='Process-local S.BETA and the captured keyword defaults in S.variable and X.expected_loads.',
            lock='Content lock, uncommitted as requested; portable brief snapshot is byte-identical to original.'))
    C.write_json(out / 'configuration.json', config)
    return dict(status='CONFIGURED', records=len(records), regimes=config['regimes'])


def check_sources(out, arm):
    out = Path(out)
    config = C.read_json(out / 'configuration.json')
    if config.get('schema') != 'x5c-alarm-configuration-v1' or config.get('arm') != arm or config['parameters'] != parameters(arm):
        raise ValueError('X5c arm/stage/count/seed/parameter override or configuration drift')
    now = {name: C.sha256(p) for name, p in sorted(source_paths().items())}
    if now != {name: item['sha256'] for name, item in config['sources'].items()}:
        raise ValueError('X4b/X5 source/input drift')
    for p, key in ((CARD, 'card_sha256'), (X5_CARD, 'x5_card_sha256'), (BRIEF_SNAPSHOT, 'brief_sha256')):
        if C.sha256(p) != config[key]:
            raise ValueError('X5c card/brief drift')
    if BRIEF.exists() and C.sha256(BRIEF) != config['brief_sha256']:
        raise ValueError('X5c original brief drift')
    if arm == 'B':
        summary = C.read_json(out / 'train/summary.json')
        if (not summary['complete'] or summary['record_count'] != 78 or summary['seed'] != 7200005
                or summary['s_hat_pooled_Mbit'] != config['s_hat_pooled_Mbit']
                or C.sha256(out / 'train/summary.json') != config['train_summary_sha256']):
            raise ValueError('completed B training required before test')
    elif config['s_hat_pooled_Mbit'] != C.read_json(B.OUT / 'training_summary.json')['s_hat_pooled_Mbit']:
        raise ValueError('inherited A slope drift')
    arrays = read_npz(B.OUT / 'configuration.npz')
    for r, info in enumerate(config['regimes']):
        expected = alarm_spec(info, B.regime_capacity(arrays, r), config['s_hat_pooled_Mbit'][info['id']])
        if any(info[k] != v for k, v in expected.items()):
            raise ValueError('selected-path alarm specification drift')
    if config['test_records'] != B.planned_truth_records(B.OUT):
        raise ValueError('X4b 60-record test-S plan drift')
    return config


def load_context(out, arm):
    config = check_sources(out, arm)
    token = C.VerifiedLock(str((Path(out) / 'configuration.json').resolve()), C.sha256(Path(out) / 'configuration.json'))
    dates = sorted({r['date'] for r in config['test_records']})
    data, exclusions = B.V3.load_days(dates, config, verified=token)
    if exclusions or set(data['dates']) != set(dates):
        raise ValueError('locked test dates excluded: ' + repr(exclusions))
    return dict(test=data), read_npz(B.OUT / 'configuration.npz'), config


def decision_record_x5c(data, arrays, config, record, s_hat, *, arm, seed,
                        m=M, n=N, k=K, min_alarms=MIN_ALARMS,
                        alarm_threshold=None, horizons=H_SECONDS, streams=None):
    r = [v['id'] for v in config['regimes']].index(record['regime'])
    info = config['regimes'][r]
    spec = alarm_spec(info, B.regime_capacity(arrays, r), s_hat)
    # X5's selector reads e_star_index. Supply a temporary view only; retain
    # the physical X4b e* in saved metadata and the unchanged configuration.
    view = dict(config, regimes=[dict(v) for v in config['regimes']])
    view['regimes'][r].update(e_star_index=spec['alarm_link_index'],
                            alarm_threshold_Mbit=spec['alarm_threshold_Mbit'])
    streams = seeds_for(seed, record['regime'], record['date'], arm=arm) if streams is None else streams
    with simulator_arm(arm):
        raw, meta = A.decision_record_x5(data, arrays, view, record, s_hat, seed=seed,
            m=m, n=n, k=k, min_alarms=min_alarms, alarm_threshold=alarm_threshold,
            horizons=horizons, streams=streams)
        meta.update(arm=arm, beta=S.BETA, runtime_beta=runtime_beta(),
            e_star_index=int(info['e_star_index']), alarm_link_index=spec['alarm_link_index'],
            alarm_action=spec['alarm_action'], s_hat_Mbit=float(s_hat))
    return raw, meta


def _decision_worker(record):
    (datasets, arrays, config), out, arm, _ = _CONTEXT
    raw, meta = decision_record_x5c(datasets['test'], arrays, config, record,
        config['s_hat_pooled_Mbit'][record['regime']], arm=arm, seed=arm_settings(arm)['test_seed'])
    return X.publish(out, 'step0/test', record, raw, meta)


def step0(arm, out=None, workers=1):
    out = arm_out(arm, out)
    if workers not in range(1, 9):
        raise ValueError('local step0 uses 1--8 workers')
    T.new(out / 'step0')
    wall = time.perf_counter()
    context = load_context(out, arm)
    records = context[2]['test_records']
    with simulator_arm(arm):
        ranked = sorted(records, key=lambda r: (-B.pilot_work_proxy(context[0]['test'], context[1], context[2], r), r['regime'], r['date']))
    (out / 'step0').mkdir(exist_ok=False)
    C.write_json(out / 'step0/started.json', dict(owner='Doan Van Tai', arm=arm, stage='decisions-only',
        workers=workers, source_sha256=C.sha256(__file__), test_outcomes_computed=False))
    first = run_jobs(_decision_worker, ranked[:1], context, out, 1, arm)[0]
    estimate = first['wall_s'] * (1 + (len(records) - 1) / workers)
    preflight = dict(record=ranked[0], CPU_s=first['CPU_s'], wall_s=first['wall_s'],
        workers=workers, records=len(records), projected_wall_s=estimate, local_limit_s=LOCAL_LIMIT_S,
        continue_local=estimate <= LOCAL_LIMIT_S, estimate_is_not_guarantee=True, first_record_reused=True)
    C.write_json(out / 'step0/preflight.json', preflight)
    emit(dict(arm=arm, preflight=preflight))
    if estimate > LOCAL_LIMIT_S:
        return dict(status='LOCAL_RUNTIME_LIMIT', preflight=preflight, complete=False)
    run_jobs(_decision_worker, ranked[1:], context, out, workers, arm)
    result = signal_tables(out, records)
    result.update(owner='Doan Van Tai', arm=arm, stage='decisions-only', complete=True,
        decisions_record_count=len(records), parameters=parameters(arm), gate=signal_gate(result['disagreement']),
        CPU_s_records=sum(m['CPU_s'] for m in result['records']), wall_s=time.perf_counter()-wall,
        evaluation_called=False, C_ref_computed=False, test_outcomes_computed=False,
        counts_are_not_independent_trials=True)
    C.write_json(out / 'step0/summary.json', result)
    for name in ('disagreement', 'M0_fresh_ties'):
        T.write_csv(out / f'step0/{name}.csv', result[name])
    T.write_csv(out / 'step0/alarms.csv', [{k: m[k] for k in
        ('regime', 'date', 'candidates', 'alarms', 'N', 'status', 'alarm_threshold_Mbit', 'alarm_link_index', 'e_star_index')}
        for m in result['records']])
    return result


def require_signal(out):
    summary = C.read_json(Path(out) / 'step0/summary.json')
    if not summary.get('complete') or summary['gate']['verdict'] != 'SIGNAL_OK':
        raise ValueError('NOT_ENOUGH_SIGNAL: no pilot, lock or truth for this arm')
    return summary


def planned_truth_records(out):
    config, summary = C.read_json(Path(out) / 'configuration.json'), require_signal(out)
    selected = {(m['regime'], m['date']) for m in summary['records'] if m['status'] != 'ALARM_RARE'}
    return [r for r in config['test_records'] if (r['regime'], r['date']) in selected]


def outcome_record_x5c(context, record, slopes, *, arm, stage, verified=None, out=None,
                       m=M, n=N, k=K, min_alarms=MIN_ALARMS, alarm_threshold=None,
                       r_dec=R_DEC, r_eval=R_EVAL, horizons=H_SECONDS, streams=None, seed=None, _prepared=None):
    out = arm_out(arm, out)
    if stage not in ('pilot', 'truth'):
        raise ValueError('explicit pilot or truth stage required')
    if record['split'] != 'test' or record['stratum'] != 'S':
        raise ValueError('only planned test-S records may enter pilot/truth')
    if stage == 'truth':
        token = verify_lock(arm, out)
        require_signal(out)
        if not isinstance(verified, C.VerifiedLock) or verified != token:
            raise ValueError('verified X5c truth lock required')
        if ((m, n, k, min_alarms, r_dec, r_eval) != (M, N, K, MIN_ALARMS, R_DEC, R_EVAL)
                or any(v is not None for v in (streams, alarm_threshold, _prepared, seed))
                or not np.array_equal(horizons, H_SECONDS)):
            raise ValueError('truth cannot override locked stage/counts/seed/streams/threshold/horizons')
        if record not in planned_truth_records(out):
            raise ValueError('record outside locked non-RARE test-S plan')
    datasets, arrays, config = context
    expected_seed = arm_settings(arm)['pilot_seed' if stage == 'pilot' else 'test_seed']
    seed = expected_seed if seed is None else seed
    if _prepared is None:
        raw, meta = decision_record_x5c(datasets['test'], arrays, config, record, slopes[record['regime']],
            arm=arm, seed=seed, m=m, n=n, k=k, min_alarms=min_alarms,
            alarm_threshold=alarm_threshold, horizons=horizons, streams=streams)
    else:
        raw, meta = _prepared
    if meta['status'] == 'ALARM_RARE':
        if stage == 'truth':
            raise ValueError('non-RARE truth record became ALARM_RARE')
        return raw, meta
    if stage == 'truth':
        old = read_npz(out / 'step0/test' / f"{record['regime']}_{record['date']}.npz")
        if set(old) != set(raw):
            raise ValueError('truth differs from step0 keys')
        for key in old:
            if old[key].dtype != raw[key].dtype or old[key].shape != raw[key].shape or old[key].tobytes() != raw[key].tobytes():
                raise ValueError('truth differs from step0: ' + key)
    cpu, wall = time.process_time(), time.perf_counter()
    j, _, inc, cap = B.record_inputs(datasets['test'], arrays, config, record)
    selected = len(raw['fresh_modes'])
    def rollout(count, purpose):
        modes, queues = (np.repeat(raw[key], count, axis=0) for key in ('fresh_modes', 'fresh_queues'))
        value = S.variable(inc, datasets['test']['days'][j], cap, modes, queues, meta['streams'][purpose],
            hs=np.rint(np.asarray(horizons) / S.DT).astype(int))[0]
        return value.reshape(selected, count, 2, len(horizons))
    with simulator_arm(arm):
        reference = R.timer(meta['timings'], 'reference_decision', lambda: rollout(r_dec, 'reference-decision'))
        evaluation = R.timer(meta['timings'], 'paired_evaluation', lambda: rollout(r_eval, 'evaluation'))
    raw.update(B.paired_metrics(raw, reference, evaluation))
    meta.update(stage=stage, pilot=stage == 'pilot', status='COMPLETE', evaluation_called=True,
        C_ref_computed=True, R_dec=r_dec, R_eval=r_eval,
        CPU_s=meta['CPU_s'] + time.process_time()-cpu, wall_s=meta['wall_s'] + time.perf_counter()-wall,
        G_S='L_stale-L_fresh', units=dict(cost='Mbit*s', backlog='Mbit', capacity='Mbit/s', time='s'))
    return raw, meta


def pilot(arm, out=None):
    out = arm_out(arm, out)
    summary = require_signal(out)
    T.new(out / 'pilot')
    context = load_context(out, arm)
    data, arrays, config = context[0]['test'], context[1], context[2]
    with simulator_arm(arm):
        ranks = sorted([(B.pilot_work_proxy(data, arrays, config, r), r) for r in planned_truth_records(out)],
            key=lambda item: (-item[0], item[1]['regime'], item[1]['date']))
    baseline = C.read_json(B.OUT / 'pilot/summary.json')['record']
    with simulator_arm('A'):
        baseline_work = B.pilot_work_proxy(data, arrays, config, baseline)
    estimate = baseline['wall_s'] * sum(w / max(1, baseline_work) for w, _ in ranks[:2])
    (out / 'pilot').mkdir(exist_ok=False)
    C.write_json(out / 'pilot/preflight.json', dict(projected_wall_s=estimate,
        local_limit_s=LOCAL_LIMIT_S, continue_local=estimate <= LOCAL_LIMIT_S,
        method='Input-work scaling of existing X4b pilot; eta effects and selected queues are unmeasured.',
        estimate_is_not_guarantee=True))
    if estimate > LOCAL_LIMIT_S:
        return dict(status='LOCAL_RUNTIME_LIMIT', projected_wall_s=estimate, complete=False)
    selected, screened = [], []
    for work, record in ranks:
        raw, meta = decision_record_x5c(data, arrays, config, record, config['s_hat_pooled_Mbit'][record['regime']],
            arm=arm, seed=arm_settings(arm)['pilot_seed'])
        screened.append(X.publish(out, 'pilot/screen', record, raw, meta.copy()))
        if meta['status'] != 'ALARM_RARE':
            selected.append((work, record, raw, meta))
        if len(selected) == 2:
            break
    C.write_json(out / 'pilot/selection.json', dict(owner='Doan Van Tai', arm=arm,
        seed=arm_settings(arm)['pilot_seed'], no_outcomes_used_in_selection=True, screened=screened,
        records=[r for _, r, _, _ in selected], ranking=[dict(record=r, work_proxy=w) for w, r in ranks]))
    if len(selected) != 2:
        raise ValueError('fewer than two pilot-seed non-RARE records; preserve screening')
    metas = []
    for _, record, raw, meta in selected:
        if metas and 2 * metas[0]['wall_s'] > LOCAL_LIMIT_S:
            C.write_json(out / 'pilot/runtime_stop.json', dict(status='LOCAL_RUNTIME_LIMIT',
                projected_wall_s=2 * metas[0]['wall_s'], local_limit_s=LOCAL_LIMIT_S))
            return dict(status='LOCAL_RUNTIME_LIMIT', complete=False)
        raw, meta = outcome_record_x5c(context, record, config['s_hat_pooled_Mbit'], arm=arm,
            stage='pilot', out=out, _prepared=(raw, meta))
        metas.append(X.publish(out, 'pilot/records', record, raw, meta))
        emit(dict(arm=arm, pilot_record=record, CPU_s=meta['CPU_s'], wall_s=meta['wall_s']))
    eligible = len(planned_truth_records(out))
    mean_cpu, max_cpu = float(np.mean([r['CPU_s'] for r in metas])), max(r['CPU_s'] for r in metas)
    result = dict(owner='Doan Van Tai', arm=arm, stage='pilot', seed=arm_settings(arm)['pilot_seed'],
        records=metas, actual_truth_eligible_records=eligible, mean_CPU_s=mean_cpu, max_CPU_s=max_cpu,
        CPU_s_records=sum(r['CPU_s'] for r in metas),
        CPU_s_screening_only=sum(r['CPU_s'] for r in screened if r['status'] == 'ALARM_RARE'),
        projected_CPU_hours=mean_cpu * eligible / 3600, projected_max_pilot_CPU_hours=max_cpu * eligible / 3600,
        ideal_wall_hours_30_workers=mean_cpu * eligible / (30 * 3600), step0_CPU_s=summary['CPU_s_records'],
        hardware=dict(platform=platform.platform(), numpy=np.__version__),
        limitations=['Two input-work-ranked pilots at separate seed; not test-seed truth or T1--T4 scoring.',
                     'Linear estimate without cloud measurement, guarantee or confidence interval.'])
    C.write_json(out / 'pilot/summary.json', result)
    return result


def validate_preparation(out, arm):
    out = Path(out)
    config, summary = check_sources(out, arm), require_signal(out)
    records = config['test_records']
    if len(records) != 60 or len({(r['regime'], r['date']) for r in records}) != 60:
        raise ValueError('exactly 60 distinct test-S records required')
    if summary['parameters'] != parameters(arm) or summary['decisions_record_count'] != 60:
        raise ValueError('incomplete step0 or stage/count/seed override')
    expected = {f"{r['regime']}_{r['date']}{ext}" for r in records for ext in ('.npz', '.json')}
    if {p.name for p in (out / 'step0/test').iterdir()} != expected:
        raise ValueError('incomplete/extra step0 records')
    recomputed = signal_tables(out, records)
    if any(summary[k] != v for k, v in recomputed.items()) or summary['gate'] != signal_gate(recomputed['disagreement']):
        raise ValueError('step0 summary/gate mismatch')
    for meta in recomputed['records']:
        stem = out / 'step0/test' / f"{meta['regime']}_{meta['date']}"
        raw = read_npz(stem.with_suffix('.npz'))
        info = next(v for v in config['regimes'] if v['id'] == meta['regime'])
        mask = raw['candidate_alarm_queues_Mbit'] >= info['alarm_threshold_Mbit']
        indices = np.flatnonzero(mask)[:N]
        if ((meta['stage'], meta['seed_base'], meta['candidates'], meta['K'], meta['arm'])
                != ('decisions-only', arm_settings(arm)['test_seed'], M, K, arm)
                or meta['streams'] != seeds_for(meta['seed_base'], meta['regime'], meta['date'], arm=arm)
                or any(v != arm_settings(arm)['beta'] for v in meta['runtime_beta'].values())):
            raise ValueError('invalid step0 arm/stage/count/seed/eta')
        if (meta['N'] != len(indices) or meta['selected_indices'] != indices.tolist()
                or not np.array_equal(raw['selected_indices'], indices)
                or not np.array_equal(raw['alarm_mask'], mask) or len(mask) != M
                or meta['alarms'] != int(mask.sum())
                or meta['alarm_link_index'] != info['alarm_link_index']
                or meta['alarm_threshold_Mbit'] != info['alarm_threshold_Mbit']
                or meta['status'] != ('ALARM_RARE' if mask.sum() < MIN_ALARMS else 'SELECTED')):
            raise ValueError('invalid alarm selection/count/link')
        if meta['evaluation_called'] or meta['C_ref_computed'] or {'V', 'C_ref', 'regret', 'costs'}.intersection(raw):
            raise ValueError('step0 contains outcomes')
        if C.sha256(stem.with_suffix('.npz')) != meta['npz_sha256']:
            raise ValueError('step0 raw checksum mismatch')
    if C.read_json(out / 'step0/started.json')['source_sha256'] != C.sha256(__file__):
        raise ValueError('X5c module changed after step0 started')
    pilot_summary = C.read_json(out / 'pilot/summary.json')
    if len(pilot_summary['records']) != 2:
        raise ValueError('two complete pilot-seed records required')
    for meta in pilot_summary['records']:
        stem = out / 'pilot/records' / f"{meta['regime']}_{meta['date']}"
        if (meta['stage'], meta['seed_base'], meta['status'], meta['arm']) != ('pilot', arm_settings(arm)['pilot_seed'], 'COMPLETE', arm):
            raise ValueError('invalid pilot arm/stage/seed')
        if C.read_json(stem.with_suffix('.json')) != meta or C.sha256(stem.with_suffix('.npz')) != meta['npz_sha256']:
            raise ValueError('pilot checksum mismatch')
    return summary


def lock_paths(out):
    out = Path(out)
    paths = source_paths()
    for name in ('experiments/letter/x5c_alarm.py', 'experiments/letter/x5c_gcp.sh', 'tests/test_x5c_alarm.py'):
        paths['repo:' + name] = ROOT / name
    paths.update({'card:X5c': CARD, 'card:X5': X5_CARD, 'brief:X5c': BRIEF_SNAPSHOT})
    paths['output:configuration.json'] = out / 'configuration.json'
    for folder in ('train', 'step0', 'pilot'):
        for p in sorted((out / folder).rglob('*')):
            if p.is_file():
                paths['output:' + str(p.relative_to(out))] = p
    return paths


def create_lock(arm, out=None):
    out = arm_out(arm, out)
    T.new(out / 'lock.json', out / 'truth')
    summary = validate_preparation(out, arm)
    result = dict(owner='Doan Van Tai', schema=LOCK_SCHEMA, arm=arm, parameters=parameters(arm),
        sha256={name: C.sha256(p) for name, p in sorted(lock_paths(out).items())},
        gate=summary['gate'], truth_records=len(planned_truth_records(out)), committed=False,
        brief_original_sha256=C.read_json(out / 'configuration.json')['brief_sha256'],
        note='Content lock only; no commit, push, SSH, truth or score performed.')
    C.write_json(out / 'lock.json', result)
    return result


def verify_lock(arm, out=None):
    out = arm_out(arm, out)
    if not (out / 'lock.json').is_file():
        raise ValueError('X5c lock required before truth/score')
    locked = C.read_json(out / 'lock.json')
    now = {name: C.sha256(p) for name, p in sorted(lock_paths(out).items())}
    if (locked.get('schema') != LOCK_SCHEMA or locked.get('arm') != arm
            or locked.get('parameters') != parameters(arm) or locked['sha256'] != now):
        raise ValueError('X5c lock mismatch or arm/stage/count/seed override')
    check_sources(out, arm)
    require_signal(out)
    return C.VerifiedLock(str((out / 'lock.json').resolve()), C.sha256(out / 'lock.json'))


def _truth_worker(record):
    context, out, arm, token = _CONTEXT
    raw, meta = outcome_record_x5c(context, record, context[2]['s_hat_pooled_Mbit'],
        arm=arm, stage='truth', verified=token, out=out)
    return X.publish(out, 'truth/records', record, raw, meta)


def truth(arm, out=None, workers=30):
    """Future explicit command; never run during preparation."""
    out = arm_out(arm, out)
    if workers < 1:
        raise ValueError('positive workers required')
    token = verify_lock(arm, out)
    validate_preparation(out, arm)
    records = planned_truth_records(out)
    (out / 'truth').mkdir(exist_ok=False)
    start = time.perf_counter()
    C.write_json(out / 'truth/started.json', dict(owner='Doan Van Tai', arm=arm, status='INCOMPLETE',
        records=records, workers=workers, lock_sha256=token.digest,
        seed=arm_settings(arm)['test_seed'], one_shot=True, retry=False, resume=False))
    result = dict(owner='Doan Van Tai', arm=arm, status='INCOMPLETE', lock_sha256=token.digest, scored=False)
    try:
        context = load_context(out, arm)
        metas = run_jobs(_truth_worker, records, context, out, workers, arm, token)
        if {(m['regime'], m['date']) for m in metas} != {(r['regime'], r['date']) for r in records}:
            raise ValueError('incomplete/extra truth records')
        verify_lock(arm, out)
        manifest = {str(p.relative_to(out)): C.sha256(p) for p in sorted((out / 'truth/records').glob('*')) if p.is_file()}
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


def score(arm, out=None):
    from experiments.letter import x5_alarm_card as card
    out = arm_out(arm, out)
    token = verify_lock(arm, out)
    T.new(out / 'card_verdicts.json', out / 'REPORT_X5C.md')
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
            raise ValueError('raw checksum mismatch: ' + name)
    head = B.require_raw_committed([out / n for n in sorted(manifest)] +
        [out / 'truth/receipt.json', out / 'truth/raw_manifest.json'])
    metas = receipt['records']
    if len(metas) != len(records) or {(m['regime'], m['date']) for m in metas} != {(r['regime'], r['date']) for r in records}:
        raise ValueError('receipt is not complete planned record set')
    inputs = []
    for meta in metas:
        stem = out / 'truth/records' / f"{meta['regime']}_{meta['date']}"
        if (meta != C.read_json(stem.with_suffix('.json'))
                or (meta['stage'], meta['seed_base'], meta['split'], meta['stratum'], meta['arm'])
                != ('truth', arm_settings(arm)['test_seed'], 'test', 'S', arm)):
            raise ValueError('invalid truth metadata')
        if C.sha256(stem.with_suffix('.npz')) != meta['npz_sha256']:
            raise ValueError('truth NPZ checksum mismatch')
        inputs.append((read_npz(stem.with_suffix('.npz')), meta))
    result = card.evaluate_raw(inputs)
    screen = C.read_json(out / 'step0/summary.json')
    result['alarm_screen'] = dict(records=60, alarms=screen['alarms'], candidates=screen['alarm_candidates'],
        alarm_rate=screen['alarms'] / screen['alarm_candidates'], ALARM_RARE=screen['alarm_rare_records'])
    result.update(arm=arm, beta=arm_settings(arm)['beta'], lock_sha256=token.digest,
        raw_commit=head, independent_rescore='PENDING')
    C.write_json(out / 'card_verdicts.json', result)
    B.text_file(out / 'REPORT_X5C.md', card.report(result).replace('# X5\n', f'# X5c — arm {arm}\n', 1))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('configure', 'step0', 'pilot', 'lock', 'verify-lock', 'truth', 'score'))
    parser.add_argument('--arm', required=True, choices=tuple(ARMS))
    parser.add_argument('--workers', type=int, default=None)
    args = parser.parse_args(argv)
    if args.workers is not None and args.command not in ('configure', 'step0', 'truth'):
        parser.error('--workers applies only to configure/step0/truth')
    if args.command in ('configure', 'step0', 'truth'):
        fn = dict(configure=configure, step0=step0, truth=truth)[args.command]
        default = 30 if args.command == 'truth' else (8 if args.command == 'configure' else 1)
        result = fn(args.arm, workers=default if args.workers is None else args.workers)
    else:
        result = dict(pilot=pilot, lock=create_lock, score=score, **{'verify-lock': verify_lock})[args.command](args.arm)
    if isinstance(result, C.VerifiedLock):
        emit(dict(arm=args.arm, verified=True, lock_sha256=result.digest))
    else:
        emit(dict(arm=args.arm, **{k: result[k] for k in
            ('gate', 'status', 'decisions_record_count', 'projected_CPU_hours') if k in result}))


if __name__ == '__main__':
    main()
