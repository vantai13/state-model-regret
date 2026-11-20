"""Doan Van Tai — X4b under DESIGN_X4B.md and CARD_X4B.md.

Train-only link capacities, decisions-only screening, predictions, one timing
pilot, one-shot truth, and descriptive scoring. Imports X-GEANT/V7-3 unchanged.
Truth and score are explicit commands, never invoked by preparation or locking.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import multiprocessing as mp
from pathlib import Path
import platform
import resource
import subprocess
import time
import traceback

import numpy as np

from experiments.letter import x_geant as X

C, T, E, S, D, A, R, V3 = X.C, X.T, X.E, X.S, X.D, X.A, X.R, X.V3
ROOT = X.ROOT
OUT = ROOT / 'results/letter/x4b'
BRIEF = Path('/home/vantai/state-model-regret-papers/letter_smr/briefs/strengthen/DESIGN_X4B.md')
BRIEF_COMMIT = 'dea74a3'
BRIEF_SHA256 = '78f82644983dc9d5f4b35bccaac9a684d33f12f926f91ac33902c6c9f78873f0'
TRUTH_BRIEF = BRIEF.with_name('CODEX_X4B_TRUTH_BRIEF.md')
TRUTH_BRIEF_SHA256 = '419108f6ff8e2f8724dad8af5afb4ea81eaced3de3b1953aad3dde91a8e5cbb4'
LOCK_SCHEMA = 'x4b-lock-v2'
# The card fixes the displayed uniform capacity, independent of c[e*].
EVALUABILITY_CAPACITY_MBPS = 12544.525174
MIN_MEAN_BACKLOG_MBIT = .001 * EVALUABILITY_CAPACITY_MBPS
EXPECTED_TRUTH_RECORDS = 60
N, K, R_DEC, R_EVAL = X.N, X.K, X.R_DEC, X.R_EVAL
TEST_SEED, TRAIN_SEED, PILOT_SEED = X.TEST_SEED, X.TRAIN_SEED, X.PILOT_SEED
H_SECONDS = np.array([300, 600, 900, 1200, 1800, 3600, 7200], dtype=int)
PIPES, SIDES = X.PIPES[:3], X.SIDES
TARGET_UTILIZATION = .85
npz, read_npz, text_file, emit = X.npz, X.read_npz, X.text_file, X.emit


def dependencies():
    paths = X.dependencies()
    paths.update({'experiments/letter/x4b.py': Path(__file__).resolve(),
                  'experiments/letter/x4b_card.py': ROOT / 'experiments/letter/x4b_card.py',
                  'experiments/letter/x4b_gcp.sh': ROOT / 'experiments/letter/x4b_gcp.sh',
                  'brief:dea74a3': BRIEF,
                  'brief:3dbf9eb': TRUTH_BRIEF,
                  'x-geant:configuration': X.OUT / 'configuration.json'})
    paths.update({str(p.relative_to(ROOT)): p for p in sorted((ROOT / 'tests').glob('test_x4b*.py'))})
    return paths


def fingerprints():
    # The inherited check pins the original brief, native inputs and import
    # closure. Do not include unrelated outputs from the parallel X1c rescore.
    hashes = X.fingerprints()
    hashes.update({k: C.sha256(p) for k, p in dependencies().items() if k not in hashes})
    if hashes['brief:dea74a3'] != BRIEF_SHA256:
        raise ValueError('brief differs from approved dea74a3')
    if hashes['brief:3dbf9eb'] != TRUTH_BRIEF_SHA256:
        raise ValueError('truth brief differs from approved 3dbf9eb')
    return hashes


def check_sources(out):
    protocol = C.read_json(Path(out) / 'protocol.json')
    current = fingerprints()
    lock_path = Path(out) / 'lock.json'
    locked = C.read_json(lock_path) if lock_path.exists() else {}
    # protocol.json remains the byte-identical preparation record. The v2
    # lock explicitly records the authorized implementation added afterwards.
    expected = ({k: locked['sha256'].get(k) for k in current}
                if locked.get('schema') == LOCK_SCHEMA else protocol['sha256'])
    if expected != current:
        raise ValueError('X4b source/input drift; retain previous attempt')
    return protocol


def capacity_vector(capacity, edges):
    cap = np.broadcast_to(np.asarray(capacity, dtype=float), (edges,)).copy()
    if not np.isfinite(cap).all() or (cap <= 0).any():
        raise ValueError('finite positive per-link capacities required')
    return cap


def calibrate_capacity(inc, mean_od, switch_edges, base_capacity):
    """Choose e* at the UNCHANGED capacity; modify that one link exactly once."""
    cap = capacity_vector(base_capacity, inc.shape[1])
    load = inc @ mean_od
    edges = np.sort(np.asarray(switch_edges, dtype=int))
    if not len(edges):
        raise ValueError('empty Switch path')
    e_star = int(edges[np.argmax(load[1, edges] / cap[edges])])
    cap[e_star] = load[1, e_star] / TARGET_UTILIZATION
    return cap, e_star, load


def select_regimes(net, days, base_capacity, old_ods, previous):
    # Reuse the original candidate construction and ordering, then take ranks
    # 4--6 of X2 eligibility, not ranks 4--6 of its interleaved six regimes.
    _, _, busy, candidates = X.select_regimes(net, days, base_capacity, old_ods)
    eligible = sorted((r for r in candidates if r['X2_eligible']),
                      key=lambda r: (-r['train_window_mean_volume_Mbps'], r['managed_OD']))
    if len(eligible) < 6 or [r['managed_OD'] for r in eligible[:3]] != previous:
        raise ValueError('X2 ranking/NEW1--3 changed or fewer than six eligible flows')
    _, stay = D.routes_and_incidence(net)
    mean_od = np.asarray(days).mean(axis=(0, 1))
    infos, incidences, capacities = [], [], []
    for rank, row in enumerate(eligible[3:6], 1):
        switch = stay.copy()
        switch[:, row['managed_index']] = 0
        switch[row['switch_edges'], row['managed_index']] = 1
        inc = np.stack([stay, switch])
        cap, e_star, load = calibrate_capacity(inc, mean_od, row['switch_edges'], base_capacity)
        u = load / cap
        infos.append(dict(row, id=f'NEWB{rank}', set='X4b', X2_rank=rank+3,
            e_star_index=e_star, e_star_link=net['links'][e_star]['id'],
            e_star_capacity_Mbps=float(cap[e_star]),
            e_star_train_load_Switch_Mbps=float(load[1, e_star]),
            e_star_utilization_before=float(load[1, e_star]/base_capacity),
            e_star_utilization_after=float(u[1, e_star]),
            path_max_mean_utilization_before=row['path_max_mean_utilization'],
            path_max_mean_utilization_after=[float(u[a, row[key]].max())
                for a, key in enumerate(('stay_edges', 'switch_edges'))],
            path_bottleneck_indices_after=[int(np.asarray(row[key])[np.argmax(u[a, row[key]])])
                for a, key in enumerate(('stay_edges', 'switch_edges'))]))
        incidences.append(inc)
        capacities.append(cap)
    return infos, np.stack(incidences), np.stack(capacities), busy, eligible


def configure(out=OUT):
    out = Path(out)
    T.new(out / 'protocol.json', out / 'configuration.json', out / 'configuration.npz')
    protocol = dict(owner='Doan Van Tai', schema='x4b-protocol-v1', brief_commit=BRIEF_COMMIT,
        sha256=fingerprints(),
        parameters=dict(N=N, K=K, R_dec=R_DEC, R_eval=R_EVAL, dt_s=S.DT,
            beta=S.BETA, flip_rate_per_s=1., c=0., h_seconds=H_SECONDS.tolist(),
            tau_seconds=list(S.TAU_SECONDS), target_switch_utilization=TARGET_UTILIZATION),
        seeds=dict(test=TEST_SEED, train=TRAIN_SEED, pilot=PILOT_SEED, namespace='X4B|regime|date',
            note='Explicit X-GEANT numeric bases retained; every actual RNG stream separated by namespace.'),
        selection='Train only; same X2-eligible ranking excluding DAY1--3; skip NEW1--3, take ranks 4--6. Stay crosses busiest link, Switch avoids it.',
        capacity='e* maximizes mean train-window Switch utilization at the original uniform capacity; ties by native link index. Set only c[e*]=mean train Switch load[e*]/0.85. Keep full-precision V7-3 base capacity on every other link.',
        slope_training='Same X-GEANT procedure: N32 paired 6h rate rollout per regime/day on all 26 train weekdays (S and O); equally pool daily Switch-minus-Stay mean backlogs.',
        strata='V7-3 S iff every unmodulated 15min offered load for both actions is strictly below its own link capacity; otherwise O. Test O is NOT_RUN before warmup.',
        screen=dict(comparison='Hybrid vs Stationary per h, fresh once and each stale age once; also report each side separately.',
            higher_rate='Strict fluid preference has (fluid Switch-minus-Stay cost)*(pooled Switch-minus-Stay backlog rate)<0; exact ties excluded.',
            threshold=.01, h_max_s=1800, gate_population='test_S', gate_sides='all_unique_sides',
            gate='SIGNAL_OK iff numerator/denominator >=1% for at least one h<=1800; otherwise stop. No per-regime selection after screening.',
            train='Same descriptive tables on train_all and train_S.',
            independence='Counts share days and instances; denominators are not independent trials.'),
        prediction='Train-S only: deltaF=Switch(stale)-Switch(fresh); sign(s_hat*deltaF) for every declared h, with paired Hybrid-minus-Stationary action-share rate forecasts on each side. Small-h forecasts are descriptive, not a replacement prediction card.',
        pilot='SIGNAL_OK only; one full N32/K64/Rdec64/Reval128 test-S record at pilot seed. Select max input-only active-link/OD work proxy, then regime/date tie break; max hold 7200s.',
        G_S='L_stale-L_fresh, matching letter Sec II and X-GEANT implementation.',
        evaluability='Pilot preserves aggregate backlog costs in Mbit*s. No scalar capacity is substituted for a vector in the service-time evaluability gate; link-service evaluability is not decided in this preparation task.',
        card='PENDING: Claude writes the paired Hybrid-minus-Stationary card after step0 and before truth, both directions at h<=1800s.',
        restrictions='Preparation only: no truth/score implementation, commit, ssh, or edit of existing files.',
        exposure=['Train rates and train decisions; test input/stratum and decisions-only screen.',
                  'One independent pilot seed may expose pilot outcomes after SIGNAL_OK.',
                  'Underlying test days already appeared in V7-3/X-GEANT; new routes/capacities do not make them unseen.'],
        commit_policy='No commit authorized; a content lock is not committed preregistration or truth authorization.')
    C.write_json(out / 'protocol.json', protocol)
    old = C.read_json(X.BASE / 'configuration.json')
    original, _ = D.load_training()
    training = A.window_training(original, old['start_slot'])
    if training['dates'].tolist() != old['train_dates'] or len(training['dates']) != 26:
        raise ValueError('training calendar changed')
    base = float(old['capacity_Mbps'])
    inherited = C.read_json(X.OUT / 'configuration.json')
    previous = [r['managed_OD'] for r in inherited['regimes'] if r['set'] == 'X2']
    net = D.topology()
    infos, incs, caps, busy, eligible = select_regimes(net, training['days'], base,
        {r['managed_OD'] for r in old['regimes']}, previous)
    table = []
    for info, inc, cap in zip(infos, incs, caps):
        load = np.einsum('nsd,aed->nsae', training['days'], inc, optimize=True)
        for a, action in enumerate(('Stay', 'Switch')):
            path = info['stay_edges'] if a == 0 else info['switch_edges']
            for e, link in enumerate(net['links']):
                table.append(dict(regime=info['id'], managed_OD=info['managed_OD'], action=action,
                    link_index=e, link=link['id'], on_managed_path=e in path,
                    e_star=e == info['e_star_index'], capacity_before_Mbps=base,
                    capacity_after_Mbps=float(cap[e]),
                    mean_load_Mbps=float(load[:, :, a, e].mean()),
                    mean_utilization_before=float(load[:, :, a, e].mean()/base),
                    mean_utilization_after=float(load[:, :, a, e].mean()/cap[e]),
                    peak_15min_utilization_before=float(load[:, :, a, e].max()/base),
                    peak_15min_utilization_after=float(load[:, :, a, e].max()/cap[e])))
    profile = training['days'].mean(axis=0)
    config = dict(owner='Doan Van Tai', training_only_selection=True, base_capacity_Mbps=base,
        capacity_axes=['regime', 'native_directed_link'], start_slot=old['start_slot'],
        window_start=old['window_start'], window_end=old['window_end'],
        train_dates=training['dates'].tolist(), busiest_Stay_link=net['links'][busy]['id'],
        regimes=infos, protocol_sha256=C.sha256(out / 'protocol.json'))
    npz(out / 'configuration.npz', dict(incidence=incs, capacity=caps, profiles=np.stack([profile, profile])))
    C.write_json(out / 'configuration.json', config)
    T.write_csv(out / 'train_utilizations.csv', table)
    T.write_csv(out / 'candidate_ranking_inputs.csv', [dict(rank=i+1,
        **{k: v for k, v in r.items() if k not in ('stay', 'switch', 'stay_edges', 'switch_edges')})
        for i, r in enumerate(eligible)])
    lines = ['# X4b — lựa chọn chỉ từ train', '', 'Người phụ trách: Doan Van Tai.', '',
        f'26 weekday; {old["window_start"]}–{old["window_end"]}; base capacity {base:.12f} Mbit/s.', '',
        '| Regime | OD | e* | capacity e* Mbit/s | utilization trước → sau (Switch) |',
        '|---|---|---|---:|---|']
    for r in infos:
        lines.append(f'| {r["id"]} | {r["managed_OD"]} | {r["e_star_link"]} | {r["e_star_capacity_Mbps"]:.9f} | {r["e_star_utilization_before"]:.9f} → {r["e_star_utilization_after"]:.9f} |')
        lines += ['', r['id']+' Stay: '+' → '.join(r['stay']), r['id']+' Switch: '+' → '.join(r['switch'])]
    lines += ['', 'Mỗi regime chỉ thay một directed link. Offered-load utilization không chứng nhận queue hay congestion của mọi sample.', '']
    text_file(out / 'regimes.md', '\n'.join(lines))
    return config


def load_context(out=OUT, *, include_test=False):
    out = Path(out)
    check_sources(out)
    config, arrays = C.read_json(out / 'configuration.json'), read_npz(out / 'configuration.npz')
    original, _ = D.load_training()
    training = A.window_training(original, config['start_slot'])
    if training['dates'].tolist() != config['train_dates']:
        raise ValueError('training calendar drift')
    datasets = dict(train=training)
    if include_test:
        dates = A.weekday_dates(C.read_json(D.OUT / 'data_manifest.json')['test_dates'])
        path = out / 'protocol.json'
        token = C.VerifiedLock(str(path.resolve()), C.sha256(path))
        testing, exclusions = V3.load_days(dates, config, verified=token)
        if exclusions:
            raise ValueError('test eligibility changed: '+repr(exclusions))
        datasets['test'] = testing
    return datasets, arrays, config


def regime_capacity(arrays, r):
    cap = np.asarray(arrays['capacity'])
    if cap.ndim == 2:
        cap = cap[r]
    return capacity_vector(cap, arrays['incidence'].shape[2])


def strata(demand, inc, cap):
    load = np.einsum('sd,aed->sae', demand, inc, optimize=True)
    maximum = (load / capacity_vector(cap, inc.shape[1])).max(axis=(0, 2))
    return dict(max_utilization_by_action=maximum.tolist(), stratum='S' if (maximum < 1).all() else 'O')


def records_for(data, arrays, config, split):
    return [dict(split=split, regime=info['id'], set='X4b', date=str(date), **label,
                 status='NOT_RUN' if split == 'test' and label['stratum'] == 'O' else 'PLANNED')
        for r, info in enumerate(config['regimes']) for j, date in enumerate(data['dates'])
        for label in [strata(data['days'][j], arrays['incidence'][r], regime_capacity(arrays, r))]]


def record_inputs(data, arrays, config, record):
    dates, ids = data['dates'].tolist(), [r['id'] for r in config['regimes']]
    if dates.count(record['date']) != 1 or datetime.fromisoformat(record['date']).weekday() >= 5:
        raise ValueError('date outside supplied weekday split')
    if (record['date'] in config['train_dates']) != (record['split'] == 'train'):
        raise ValueError('train/test split mismatch')
    r, j = ids.index(record['regime']), dates.index(record['date'])
    inc, cap = arrays['incidence'][r], regime_capacity(arrays, r)
    label = strata(data['days'][j], inc, cap)
    if label['stratum'] != record['stratum'] or (record['split'] == 'test' and label['stratum'] != 'S'):
        raise ValueError('test O is NOT_RUN; input stratum changed')
    return j, r, inc, cap


def seeds_for(seed, regime, date):
    root = T.seed_for(seed, f'X4B|{regime}|{date}')
    return dict(base=seed, record=root, **{label: T.seed_for(root, label) for label in
        ('warm', 'rate', 'posterior-300.0', 'posterior-900.0', 'reference-decision', 'evaluation')})


def mean_forecast(inc, profile, cap, modes, queues, horizons=H_SECONDS):
    """Imported mean path, with the X-GEANT exact zero-tail certificate.

    Respect all early checkpoints when certifying the first-slot endpoint;
    splitting at 300/600s must use the same arithmetic as S.mean_rollout.
    Homogeneous capacity and the old h grid reduce bit-for-bit to X-GEANT.
    """
    cap = capacity_vector(cap, inc.shape[1])
    hs = np.rint(np.asarray(horizons)/S.DT).astype(int)
    steps = round(S.SLOT/S.DT)
    if np.exp(-2*S.DT*steps) == 0 and ((inc @ profile[1:].T) <= cap[None, :, None]).all() and hs[-1] > steps:
        first_hs = np.unique(np.r_[hs[hs < steps], steps])
        endpoints = []
        for a in range(2):
            model = T.Model(np.ascontiguousarray((inc[a]*profile[0])[None]), cap,
                            np.ones(inc.shape[2]), S.BETA, [], [])
            m, q, now = np.asarray(modes).copy(), np.asarray(queues).copy(), 0
            for stop in first_hs:
                length = int(stop)-now
                q = S.mean_endpoint(model, m, q, S.DT, length)[:, 0]
                m *= np.exp(-2*S.DT*length)
                now = int(stop)
            endpoints.append(q)
        if all(not q.any() for q in endpoints) and not m.any():
            first = S.mean_rollout(inc, profile[:1], cap, modes, queues, hs=first_hs)
            return first[:, :, np.searchsorted(first_hs, np.minimum(hs, steps))]
    return S.mean_rollout(inc, profile, cap, modes, queues, hs=hs)


def decision_record(data, arrays, config, record, s_hat, *, seed, n=N, k=K,
                    horizons=H_SECONDS, streams=None):
    cpu, wall = time.process_time(), time.perf_counter()
    j, r, inc, cap = record_inputs(data, arrays, config, record)
    streams = seeds_for(seed, record['regime'], record['date']) if streams is None else streams
    times = {}
    fresh, stale = R.timer(times, 'warmup', lambda: S.warm_instances(inc, data['warm'][j], cap, n, streams['warm']))
    profile = arrays['profiles'][0]
    costs = [R.timer(times, 'M0_fresh', lambda: mean_forecast(inc, profile, cap, *fresh, horizons))]
    managed = config['regimes'][r]['managed_index']
    util = [X.path_utilizations(inc, data['days'][j, 0], fresh[0], cap, managed)]
    posterior_means = []
    for tau in S.TAU_SECONDS:
        pm, pq = R.timer(times, f'posterior_{int(tau)}', lambda tau=tau: S.forward_posterior(
            inc, data['warm'][j, -1], cap, stale[tau], tau, k, streams[f'posterior-{tau}']))
        costs.append(R.timer(times, f'M0_stale_{int(tau)}', lambda: mean_forecast(
            inc, profile, cap, pm, pq, horizons).reshape(n, k, 2, len(horizons)).mean(axis=1)))
        mean = pm.reshape(n, k, -1).mean(axis=1)
        posterior_means.append(mean)
        util.append(X.path_utilizations(inc, data['days'][j, 0], mean, cap, managed))
    decisions, ties = zip(*(X.fluid_choices(c, s_hat, horizons) for c in costs))
    raw = dict(decisions=np.stack(decisions, axis=2), tie_flags=np.stack(ties, axis=2),
        M0_predicted_fresh=costs[0], M0_predicted_stale=np.stack(costs[1:], axis=1),
        path_utilization=np.stack(util, axis=1), posterior_mean_modes=np.stack(posterior_means, axis=1),
        fresh_modes=fresh[0], fresh_queues=fresh[1], s_hat_Mbit=np.array(s_hat),
        h_seconds=np.asarray(horizons), tau_seconds=np.array(S.TAU_SECONDS),
        pipelines=np.array(PIPES), sides=np.array(SIDES), capacity_Mbps=cap)
    meta = dict(owner='Doan Van Tai', **record, seed_base=seed, streams=streams, N=n, K=k,
        timings=times, stage='decisions-only', evaluation_called=False, C_ref_computed=False,
        CPU_s=time.process_time()-cpu, wall_s=time.perf_counter()-wall,
        peak_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
    return raw, meta


_CONTEXT = None


def _initialize(context, out, slopes, token=None):
    global _CONTEXT
    _CONTEXT = context, Path(out), slopes, token


def train_record(record):
    (datasets, arrays, config), out, _, _ = _CONTEXT
    data = datasets['train']
    cpu, wall = time.process_time(), time.perf_counter()
    j, _, inc, cap = record_inputs(data, arrays, config, record)
    streams, times = seeds_for(TRAIN_SEED, record['regime'], record['date']), {}
    fresh, _ = R.timer(times, 'warmup', lambda: S.warm_instances(inc, data['warm'][j], cap, N, streams['warm']))
    costs = R.timer(times, 'training_rate_only', lambda: S.variable(inc, data['days'][j], cap,
        *fresh, streams['rate'], hs=[round(21600/S.DT)])[0])
    rates = costs[:, :, 0]/21600
    delta = rates[:, 1]-rates[:, 0]
    meta = dict(owner='Doan Van Tai', **record, seed_base=TRAIN_SEED, streams=streams, N=N,
        stage='training-rate', test_outcomes=False, s_hat_Mbit=float(delta.mean()),
        conditional_MC_SE_Mbit=float(delta.std(ddof=1)/np.sqrt(N)), timings=times,
        CPU_s=time.process_time()-cpu, wall_s=time.perf_counter()-wall)
    return X.publish(out, 'training_rates', record, dict(costs=costs, rates=rates,
        fresh_modes=fresh[0], fresh_queues=fresh[1], h_seconds=np.array([21600]), capacity_Mbps=cap), meta)


def _decision_worker(record):
    (datasets, arrays, config), out, slopes, _ = _CONTEXT
    raw, meta = decision_record(datasets[record['split']], arrays, config, record,
        slopes[record['regime']], seed=TRAIN_SEED if record['split'] == 'train' else TEST_SEED)
    return X.publish(out, 'step0/'+record['split'], record, raw, meta)


def run_jobs(fn, records, context, out, workers, slopes=None, token=None):
    if workers < 1:
        raise ValueError('positive workers required')
    if workers == 1:
        _initialize(context, out, slopes, token)
        return [fn(r) for r in records]
    with ProcessPoolExecutor(workers, mp_context=mp.get_context('spawn'), initializer=_initialize,
                             initargs=(context, out, slopes, token)) as pool:
        return list(pool.map(fn, records, chunksize=1))


def signal_tables(out, records):
    rows, ties, by_record = [], [], []
    for population in ('train_all', 'train_S', 'test_S'):
        groups = {}
        selected = [r for r in records if r['split'] == ('test' if population == 'test_S' else 'train')
            and (population == 'train_all' or r['stratum'] == 'S')]
        for record in selected:
            raw = read_npz(Path(out) / 'step0' / record['split'] / f'{record["regime"]}_{record["date"]}.npz')
            d, tf = raw['decisions'], raw['tie_flags']
            costs = [raw['M0_predicted_fresh']] + [raw['M0_predicted_stale'][:, t] for t in range(2)]
            for ih, h in enumerate(H_SECONDS):
                for s, side in enumerate(SIDES):
                    disagree = int(np.count_nonzero(d[:, 1, s, ih] != d[:, 2, s, ih]))
                    gap = costs[s][:, 1, ih]-costs[s][:, 0, ih]
                    higher = int(np.count_nonzero(gap*float(raw['s_hat_Mbit'].item()) < 0))
                    for label in (side, 'all_unique_sides'):
                        counts = groups.setdefault(('signal', int(h), label), [0, 0, 0])
                        counts[0] += disagree
                        counts[1] += len(d)
                        counts[2] += higher
                    by_record.append(dict(population=population, split=record['split'],
                        regime=record['regime'], date=record['date'], h_s=int(h), side=side,
                        numerator=disagree, denominator=len(d), fluid_prefers_higher_rate=higher))
                    for p, rule in enumerate(PIPES):
                        counts = groups.setdefault(('tie', int(h), side, rule), [0, 0])
                        counts[0] += int(tf[:, p, s, ih].sum())
                        counts[1] += len(d)
        for key, counts in groups.items():
            row = dict(population=population, h_s=key[1], side=key[2], numerator=counts[0],
                       denominator=counts[1], share=counts[0]/counts[1])
            if key[0] == 'tie':
                ties.append(dict(row, rule=key[3]))
            else:
                rows.append(dict(row, fluid_prefers_higher_rate=counts[2], higher_rate_share=counts[2]/counts[1]))
    return dict(disagreement=rows, ties=ties, by_record=by_record)


def signal_gate(tables, population='test_S'):
    rows = [r for r in tables['disagreement'] if r['population'] == population
        and r['h_s'] <= 1800 and r['side'] == 'all_unique_sides']
    return dict(verdict='SIGNAL_OK' if any(r['denominator'] > 0 and 100*r['numerator'] >= r['denominator']
        for r in rows) else 'NOT_ENOUGH_SIGNAL', threshold=.01, counts=rows)


def step0(out=OUT, workers=1):
    out = Path(out)
    T.new(out / 'step0_started.json', out / 'training_summary.json', out / 'signal.json')
    cpu, wall = time.process_time(), time.perf_counter()
    context = load_context(out)
    C.write_json(out / 'step0_started.json', dict(owner='Doan Van Tai', workers=workers,
        source_sha256=C.sha256(__file__), test_future_evaluation=False))
    train_records = records_for(context[0]['train'], context[1], context[2], 'train')
    rates = run_jobs(train_record, train_records, context, out, workers)
    slopes = {r['id']: float(np.mean([x['s_hat_Mbit'] for x in rates if x['regime'] == r['id']]))
              for r in context[2]['regimes']}
    C.write_json(out / 'training_summary.json', dict(owner='Doan Van Tai', N=N, seed=TRAIN_SEED,
        s_hat_pooled_Mbit=slopes, records=rates, record_count=len(rates),
        test_outcomes=False, CPU_s_records=sum(r['CPU_s'] for r in rates)))
    # Commit to routes, capacities and slopes on disk before opening test TMs.
    context = load_context(out, include_test=True)
    records = [r for split, data in context[0].items() for r in records_for(data, context[1], context[2], split)]
    C.write_json(out / 'inputs.json', dict(owner='Doan Van Tai', records=records, input_only=True,
        O_test_status='NOT_RUN', planned_truth='All test-S records, only after SIGNAL_OK and a separate Claude card.'))
    selected = [r for r in records if r['status'] != 'NOT_RUN']
    metas = run_jobs(_decision_worker, selected, context, out, workers, slopes)
    tables = signal_tables(out, selected)
    result = dict(owner='Doan Van Tai', stage='decisions-only', N=N, K=K,
        decisions_record_count=len(metas), records=metas, gate=signal_gate(tables), tables=tables,
        train_S_gate_descriptive=signal_gate(tables, 'train_S'),
        evaluation_called=False, C_ref_computed=False, test_outcomes_computed=False,
        training_rate_rollouts_separate=True, CPU_s_records=sum(m['CPU_s'] for m in metas),
        CPU_s_parent=time.process_time()-cpu, wall_s=time.perf_counter()-wall)
    C.write_json(out / 'signal.json', result)
    for name, rows in tables.items():
        T.write_csv(out / f'step0_{name}.csv', rows)
    return result


def require_signal(out):
    check_sources(out)
    result = C.read_json(Path(out) / 'signal.json')
    if result['gate']['verdict'] != 'SIGNAL_OK':
        raise ValueError('NOT_ENOUGH_SIGNAL: stop, no predict/pilot/lock beyond screen')
    return result


def predict(out=OUT):
    out = Path(out)
    signal = require_signal(out)
    slopes = C.read_json(out / 'training_summary.json')['s_hat_pooled_Mbit']
    rows, paired = [], []
    for regime, slope in sorted(slopes.items()):
        records = [r for r in signal['records'] if r['split'] == 'train' and r['stratum'] == 'S' and r['regime'] == regime]
        if not records:
            continue
        raw = [read_npz(out / 'step0/train' / f'{regime}_{r["date"]}.npz') for r in records]
        d = np.concatenate([r['decisions'] for r in raw])
        u = np.concatenate([r['path_utilization'] for r in raw])
        null_gap = float((u[:, :, 1]-u[:, :, 0]).mean())
        for ih, h in enumerate(H_SECONDS):
            for p, rule in enumerate(PIPES):
                for s, tau in enumerate(S.TAU_SECONDS, 1):
                    ns, nf = int(d[:, p, s, ih].sum()), int(d[:, p, 0, ih].sum())
                    delta = (ns-nf)/len(d)
                    rows.append(dict(regime=regime, rule=rule, tau_s=int(tau), h_s=int(h),
                        train_S_days=len(records), denominator=len(d), switch_stale=ns, switch_fresh=nf,
                        delta_F_hat=delta, s_hat_pooled_Mbit=slope, slope_pred_Mbit=slope*delta,
                        predicted_G_S_sign=int(np.sign(slope*delta)),
                        null_mean_path_max_util_difference=null_gap, null_sign=int(np.sign(null_gap*delta))))
            for s, side in enumerate(SIDES):
                delta = float((d[:, 1, s, ih]-d[:, 2, s, ih]).mean())
                paired.append(dict(regime=regime, side=side, h_s=int(h), denominator=len(d),
                    train_S_days=len(records), delta_F_Hybrid_minus_Stationary=delta,
                    paired_rate_prediction_Mbit=slope*delta,
                    paired_predicted_sign=int(np.sign(slope*delta))))
    result = dict(owner='Doan Van Tai', training_only=True, G_S='L_stale-L_fresh',
        test_outcomes_read=False, seed_train=TRAIN_SEED, rows=rows, paired_rows=paired,
        training_summary_sha256=C.sha256(out / 'training_summary.json'),
        card_status='PENDING_CLAUDE', caveat='Descriptive rate-based forecasts at all declared h, not small-h guarantees or a hypothesis card; zero is abstention.')
    C.write_json(out / 'predictions.json', result)
    T.write_csv(out / 'predictions.csv', rows)
    T.write_csv(out / 'predictions_paired.csv', paired)
    return result


def pilot_work_proxy(data, arrays, config, record):
    j, _, inc, cap = record_inputs(data, arrays, config, record)
    upper = (1+S.BETA)*np.einsum('sd,aed->sae', data['days'][j, :8], inc, optimize=True)
    active = (upper > cap).any(axis=(0, 1))
    active |= ((1+S.BETA)*(data['warm'][j] @ inc[0].T) > cap).any(axis=0)
    relevant = (inc[:, active] != 0).any(axis=(0, 1))
    sparse = int(np.count_nonzero(inc[:, active][:, :, relevant]))
    return int(round(H_SECONDS[-1]/S.DT)*N*(R_DEC+R_EVAL)*(sparse+relevant.sum()+2*active.sum()))


def evaluability(cref, horizons):
    """Card gate: E_instance[C_ref]/h >= 0.001 * the fixed uniform c0."""
    cref, hs = np.asarray(cref, dtype=float), np.asarray(horizons, dtype=float)
    if cref.ndim != 2 or hs.ndim != 1 or cref.shape[1] != len(hs) or not len(cref):
        raise ValueError('C_ref axes must be instance,h')
    if not np.isfinite(cref).all() or not np.isfinite(hs).all() or (hs <= 0).any():
        raise ValueError('finite C_ref and positive horizons required')
    return cref.mean(axis=0)/hs >= MIN_MEAN_BACKLOG_MBIT


def paired_metrics(raw, reference, evaluation):
    """Pure action gather; no homogeneous-capacity normalization is assumed."""
    values = evaluation.mean(axis=1)
    ref, rt = E.pick(reference.mean(axis=1))
    cref = E.costs_for_decisions(values, ref)
    costs = E.costs_for_decisions(values, raw['decisions'])
    regret = costs-cref[:, None, None, :]
    return dict(V=values, reference_decision=ref, reference_tie_flags=rt, C_ref=cref,
        costs=costs, regret=regret, G_S=costs[:, :, 1:]-costs[:, :, :1],
        paired_evaluation=evaluation, reference_decision_rollouts=reference,
        mean_reference_backlog_Mbit=cref.mean(axis=0)/raw['h_seconds'],
        evaluable=evaluability(cref, raw['h_seconds']),
        paired_Hybrid_minus_Stationary=regret[:, 1]-regret[:, 2])


def outcome_record(context, record, slopes, *, stage, verified=None, out=OUT,
                   n=N, k=K, r_dec=R_DEC, r_eval=R_EVAL,
                   horizons=H_SECONDS, streams=None):
    if stage not in ('pilot', 'truth'):
        raise ValueError('explicit pilot or truth stage required')
    if record['split'] != 'test' or record['stratum'] != 'S':
        raise ValueError('only test-S may enter pilot/truth; test O is NOT_RUN')
    if stage == 'truth':
        token = verify_lock(out)
        if not isinstance(verified, C.VerifiedLock) or verified != token:
            raise ValueError('verified X4b truth lock required')
        from experiments.letter import x4b_card
        x4b_card.verify(out)
        if record not in planned_truth_records(out):
            raise ValueError('record outside locked test-S plan')
        if (n, k, r_dec, r_eval) != (N, K, R_DEC, R_EVAL) or streams is not None or not np.array_equal(horizons, H_SECONDS):
            raise ValueError('truth cannot override locked counts, streams or horizons')
    datasets, arrays, config = context
    seed = PILOT_SEED if stage == 'pilot' else TEST_SEED
    cpu, wall = time.process_time(), time.perf_counter()
    raw, meta = decision_record(datasets['test'], arrays, config, record, slopes[record['regime']],
        seed=seed, n=n, k=k, horizons=horizons, streams=streams)
    if stage == 'truth':
        old = read_npz(Path(out) / 'step0/test' / f"{record['regime']}_{record['date']}.npz")
        for key in ('decisions', 'tie_flags', 'fresh_modes', 'fresh_queues',
                    'M0_predicted_fresh', 'M0_predicted_stale'):
            if not np.array_equal(old[key], raw[key]):
                raise ValueError('truth differs from step0: '+key)
    j, _, inc, cap = record_inputs(datasets['test'], arrays, config, record)
    def rollout(count, purpose):
        m, q = (np.repeat(raw[key], count, axis=0) for key in ('fresh_modes', 'fresh_queues'))
        value = S.variable(inc, datasets['test']['days'][j], cap, m, q, meta['streams'][purpose],
            hs=np.rint(np.asarray(horizons)/S.DT).astype(int))[0]
        return value.reshape(n, count, 2, len(horizons))
    reference = R.timer(meta['timings'], 'reference_decision', lambda: rollout(r_dec, 'reference-decision'))
    evaluation = R.timer(meta['timings'], 'paired_evaluation', lambda: rollout(r_eval, 'evaluation'))
    raw.update(paired_metrics(raw, reference, evaluation))
    meta.update(stage=stage, pilot=stage == 'pilot', evaluation_called=True, C_ref_computed=True,
        R_dec=r_dec, R_eval=r_eval, CPU_s=time.process_time()-cpu, wall_s=time.perf_counter()-wall,
        peak_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        G_S='L_stale-L_fresh', evaluability_capacity_Mbps=EVALUABILITY_CAPACITY_MBPS,
        evaluability='mean(C_ref)/h >= 0.001*c0; fixed uniform c0 from CARD_X4B',
        units=dict(cost='Mbit*s', backlog='Mbit', capacity='Mbit/s', time='s'),
        axes=dict(decisions=['instance', 'rule', 'unique_side', 'h'], V=['instance', 'action', 'h']))
    return raw, meta


def pilot_record(context, record, slopes, **kwargs):
    return outcome_record(context, record, slopes, stage='pilot', **kwargs)


def pilot(out=OUT):
    out = Path(out)
    require_signal(out)
    T.new(out / 'pilot/selection.json', out / 'pilot/summary.json')
    context = load_context(out, include_test=True)
    data, arrays, config = context[0]['test'], context[1], context[2]
    records = [r for r in C.read_json(out / 'inputs.json')['records'] if r['split'] == 'test' and r['stratum'] == 'S']
    ranks = sorted([(pilot_work_proxy(data, arrays, config, r), r) for r in records],
        key=lambda x: (-x[0], x[1]['regime'], x[1]['date']))
    if not ranks:
        raise ValueError('no test-S pilot record')
    work, record = ranks[0]
    C.write_json(out / 'pilot/selection.json', dict(owner='Doan Van Tai', record=record, seed=PILOT_SEED,
        work_proxy=work, no_outcomes_used_in_selection=True,
        ranking=[dict(work_proxy=w, **r) for w, r in ranks]))
    slopes = C.read_json(out / 'training_summary.json')['s_hat_pooled_Mbit']
    raw, meta = pilot_record(context, record, slopes)
    X.publish(out, 'pilot/records', record, raw, meta)
    projected = meta['CPU_s']*len(records)
    result = dict(owner='Doan Van Tai', stage='pilot', record=meta, seed=PILOT_SEED,
        N=N, K=K, R_dec=R_DEC, R_eval=R_EVAL, actual_truth_eligible_records=len(records),
        projected_CPU_s=projected, projected_CPU_hours=projected/3600,
        ideal_wall_hours_30_workers=projected/(30*3600), target='n2-highcpu-32', workers=30,
        hardware=dict(platform=platform.platform(), processor=platform.processor(),
            python=platform.python_version(), numpy=np.__version__),
        limitations=['One local full-size pilot and input work proxy, not a measured worst-case guarantee.',
            'Linear extrapolation and ideal division by 30; no cloud measurement or confidence interval.',
            'Pilot-seed outcomes are exposure; no test-seed truth or hypothesis score.',
            'Claude prediction card remains required after step0, before any truth.'])
    C.write_json(out / 'pilot/summary.json', result)
    return result


def lock_paths(out):
    out = Path(out)
    paths = dependencies()
    for name in ('protocol.json', 'configuration.json', 'configuration.npz', 'regimes.md',
        'train_utilizations.csv', 'candidate_ranking_inputs.csv', 'step0_started.json',
        'training_summary.json', 'inputs.json', 'signal.json', 'step0_disagreement.csv',
        'step0_ties.csv', 'step0_by_record.csv', 'predictions.json', 'predictions.csv',
        'predictions_paired.csv', 'pilot/selection.json', 'pilot/summary.json', 'CARD_X4B.md'):
        paths['output:'+name] = out / name
    if (out / 'preparation_lock.json').exists():
        paths['output:preparation_lock.json'] = out / 'preparation_lock.json'
    for folder in ('training_rates', 'step0/train', 'step0/test', 'pilot/records'):
        for p in sorted((out / folder).glob('*')):
            if p.suffix in ('.npz', '.json'):
                paths['output:'+str(p.relative_to(out))] = p
    return paths


def create_lock(out=OUT):
    out = Path(out)
    T.new(out / 'truth', out / 'lock_card.json')
    lock_path = out / 'lock.json'
    previous = C.read_json(lock_path) if lock_path.exists() else None
    if previous is not None:
        if previous.get('schema') != 'x4b-lock-v1':
            raise FileExistsError('truth lock already exists; never relock after v2')
        T.new(out / 'preparation_lock.json')
        paths = lock_paths(out)
        # Only these two existing files were authorized to change. Every raw
        # preparation input/output must still match the previous content lock.
        allowed = {'experiments/letter/x4b.py', 'tests/test_x4b.py'}
        for key, digest in previous['sha256'].items():
            if key not in paths or (key not in allowed and C.sha256(paths[key]) != digest):
                raise ValueError('preparation drift outside authorized source changes: '+key)
        fingerprints()  # Also check all new dependencies and approved briefs.
    else:
        check_sources(out)
    signal = C.read_json(out / 'signal.json')
    if signal['gate']['verdict'] != 'SIGNAL_OK':
        raise ValueError('NOT_ENOUGH_SIGNAL: no truth lock')
    records = C.read_json(out / 'inputs.json')['records']
    selected = [r for r in records if r['status'] != 'NOT_RUN']
    train_count = len(C.read_json(out / 'configuration.json')['regimes'])*26
    if signal['decisions_record_count'] != len(selected) or C.read_json(out / 'training_summary.json')['record_count'] != train_count:
        raise ValueError('incomplete screen or training rates')
    for folder, expected in (('training_rates', train_count), ('step0/train', train_count),
        ('step0/test', len(selected)-train_count), ('pilot/records', 1)):
        expected_stems = {f'{r["regime"]}_{r["date"]}' for r in selected
            if r['split'] == ('test' if folder == 'step0/test' else 'train')}
        for ext in ('.json', '.npz'):
            found = {p.stem for p in (out / folder).glob('*'+ext)}
            if len(found) != expected or (folder != 'pilot/records' and found != expected_stems):
                raise ValueError('incomplete or extra preparation records: '+folder)
    planned_truth_records(out)
    if previous is not None:
        lock_path.rename(out / 'preparation_lock.json')
    result = dict(owner='Doan Van Tai', schema=LOCK_SCHEMA,
        sha256={k: C.sha256(p) for k, p in sorted(lock_paths(out).items())},
        gate=signal['gate'], committed=False, card_status='CARD_X4B_WRITTEN', truth_authorized=False,
        seed_test=TEST_SEED, namespace='X4B|regime|date', test_S_records=EXPECTED_TRUTH_RECORDS,
        evaluability_capacity_Mbps=EVALUABILITY_CAPACITY_MBPS,
        evaluability_min_mean_backlog_Mbit=MIN_MEAN_BACKLOG_MBIT,
        preparation_protocol_is_historical=True,
        note='Authorized implementation relock before truth. Preparation protocol/raw and previous lock retained byte-for-byte. Claude commits/transfers before the one-shot truth; raw must be committed before scoring. No truth/score/commit/ssh performed by this lock.')
    C.write_json(out / 'lock.json', result)
    return result


def verify_lock(out=OUT):
    out = Path(out)
    locked = C.read_json(out / 'lock.json')
    now = {k: C.sha256(p) for k, p in sorted(lock_paths(out).items())}
    if locked.get('schema') != LOCK_SCHEMA or locked['sha256'] != now:
        raise ValueError('X4b lock mismatch')
    return C.VerifiedLock(str((out / 'lock.json').resolve()), C.sha256(out / 'lock.json'))


def planned_truth_records(out):
    records = [r for r in C.read_json(Path(out) / 'inputs.json')['records']
               if r['split'] == 'test' and r['stratum'] == 'S']
    keys = [(r['regime'], r['date']) for r in records]
    if len(records) != EXPECTED_TRUTH_RECORDS or len(set(keys)) != len(keys) or any(r['status'] == 'NOT_RUN' for r in records):
        raise ValueError('truth requires all 60 distinct, planned test-S records')
    return records


def _truth_worker(record):
    context, out, slopes, token = _CONTEXT
    raw, meta = outcome_record(context, record, slopes, stage='truth', verified=token, out=out)
    return X.publish(out, 'truth/records', record, raw, meta)


def truth(out=OUT, workers=30):
    """One invocation only. An existing truth directory forbids retry/resume."""
    if workers < 1:
        raise ValueError('positive workers required')
    out = Path(out)
    token = verify_lock(out)
    from experiments.letter import x4b_card
    x4b_card.verify(out)
    require_signal(out)
    records = planned_truth_records(out)
    # mkdir, rather than a check followed by a write, excludes a second caller.
    (out / 'truth').mkdir(exist_ok=False)
    start, cpu = time.perf_counter(), time.process_time()
    children_cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
    C.write_json(out / 'truth/started.json', dict(owner='Doan Van Tai', seed=TEST_SEED,
        namespace='X4B|regime|date', workers=workers, records=records,
        lock_sha256=token.digest, card_lock_sha256=C.sha256(out / 'lock_card.json'),
        one_shot=True, retry=False, resume=False))
    result = dict(owner='Doan Van Tai', status='INCOMPLETE', records=[],
        planned_records=len(records), lock_sha256=token.digest, scored=False,
        CPU_s_records=None, wall_s=None, peak_RSS_MiB=None, measurements_finalized=False)
    # A timeout/SIGKILL still leaves an explicit INCOMPLETE receipt. Only this
    # status receipt is replaced on completion; raw records never overwrite.
    C.write_json(out / 'truth/receipt.json', result)
    try:
        context = load_context(out, include_test=True)
        slopes = C.read_json(out / 'training_summary.json')['s_hat_pooled_Mbit']
        run_jobs(_truth_worker, records, context, out, workers, slopes, token)
        metas = [C.read_json(p) for p in sorted((out / 'truth/records').glob('*.json'))]
        if {(m['regime'], m['date']) for m in metas} != {(r['regime'], r['date']) for r in records}:
            raise ValueError('incomplete/extra truth records')
        verify_lock(out)
        x4b_card.verify(out)
        manifest = {str(p.relative_to(out)): C.sha256(p)
                    for p in sorted((out / 'truth/records').glob('*')) if p.is_file()}
        manifest['truth/started.json'] = C.sha256(out / 'truth/started.json')
        C.write_json(out / 'truth/raw_manifest.json', dict(owner='Doan Van Tai', sha256=manifest))
        result['status'] = 'COMPLETE'
    except BaseException:
        result['error'] = traceback.format_exc()
        raise
    finally:
        receipts = [C.read_json(p) for p in sorted((out / 'truth/records').glob('*.json'))]
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        result.update(records=receipts, wall_s=time.perf_counter()-start, measurements_finalized=True,
            CPU_s_records=sum(r['CPU_s'] for r in receipts), CPU_s_parent=time.process_time()-cpu,
            CPU_s_children=usage.ru_utime+usage.ru_stime-children_cpu.ru_utime-children_cpu.ru_stime,
            peak_RSS_MiB=max([resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
                usage.ru_maxrss/1024]+[r['peak_RSS_MiB'] for r in receipts]),
            peak_RSS_scope='Largest process high-water mark; not simultaneous aggregate memory.')
        C.write_json(out / 'truth/receipt_final.json', result)
        (out / 'truth/receipt_final.json').replace(out / 'truth/receipt.json')
    return result


def paired_stats(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < 2 or not np.isfinite(values).all():
        raise ValueError('paired statistics require at least two finite instances')
    return dict(mean=float(values.mean()), se=float(values.std(ddof=1)/np.sqrt(len(values))))


def tie_strict_regret(regret, tie_flags):
    """Additive contributions over ALL instances, not conditional subgroup means.

    Keep signed finite-MC estimates, including negative contributions. No clip.
    """
    regret, ties = np.asarray(regret, dtype=float), np.asarray(tie_flags, dtype=bool)
    if regret.ndim != 1 or regret.shape != ties.shape or not len(regret) or not np.isfinite(regret).all():
        raise ValueError('aligned finite instance regret and tie flags required')
    total = float(regret.sum())
    tie, strict = float(regret[ties].sum()), float(regret[~ties].sum())
    return dict(instances=len(regret), tie_instances=int(ties.sum()), strict_instances=int((~ties).sum()),
        regret_Mbit_s=total/len(regret), tie_regret_Mbit_s=tie/len(regret), strict_regret_Mbit_s=strict/len(regret),
        regret_sum_Mbit_s=total, tie_regret_sum_Mbit_s=tie, strict_regret_sum_Mbit_s=strict,
        strict_regret_share=None if total == 0 else strict/total)


def descriptive_rows(raw, meta):
    """Pure synthetic-testable summaries; never load data or call a simulator."""
    rows, pairs, ties = [], [], []
    base = {k: meta[k] for k in ('regime', 'set', 'date')}
    evaluable = evaluability(raw['C_ref'], raw['h_seconds'])
    for ih, h in enumerate(raw['h_seconds']):
        cref = float(raw['C_ref'][:, ih].mean())
        eligible = bool(evaluable[ih])
        pct = lambda v: None if cref <= 0 else 100*v/cref
        for s, side in enumerate(SIDES):
            stats = paired_stats(raw['paired_Hybrid_minus_Stationary'][:, s, ih])
            different = raw['decisions'][:, 1, s, ih] != raw['decisions'][:, 2, s, ih]
            pairs.append(dict(base, side=side, h_s=int(h), evaluable=eligible, C_ref_Mbit_s=cref,
                paired_Hybrid_minus_Stationary_Mbit_s=stats['mean'],
                paired_Hybrid_minus_Stationary_SE_Mbit_s=stats['se'],
                paired_Hybrid_minus_Stationary_pct=pct(stats['mean']),
                disagreement_numerator=int(different.sum()), instances=len(different),
                disagreement_share=float(different.mean())))
        ties.append(dict(base, side='fresh', h_s=int(h), evaluable=eligible, C_ref_Mbit_s=cref,
            **tie_strict_regret(raw['regret'][:, 0, 0, ih], raw['tie_flags'][:, 0, 0, ih])))
        for p, name in enumerate(PIPES):
            for t, tau in enumerate(raw['tau_seconds']):
                lf, ls = (float(raw['costs'][:, p, s, ih].mean()) for s in (0, t+1))
                rf, rs = lf-cref, ls-cref
                gs = paired_stats(raw['G_S'][:, p, t, ih])
                pair_f, pair_s = (paired_stats(raw['paired_Hybrid_minus_Stationary'][:, s, ih]) for s in (0, t+1))
                rows.append(dict(base, rule=name, tau_s=int(tau), h_s=int(h), C_ref_Mbit_s=cref,
                    L_fresh_Mbit_s=lf, L_stale_Mbit_s=ls,
                    regret_fresh_Mbit_s=rf, regret_stale_Mbit_s=rs,
                    regret_fresh_pct=pct(rf), regret_stale_pct=pct(rs), both_side_regret_pct=pct(max(rf, rs)),
                    G_S_Mbit_s=gs['mean'], G_S_SE_Mbit_s=gs['se'], G_S_pct=pct(gs['mean']),
                    G_S_over_h_Mbit=gs['mean']/h,
                    G_S_service_ms=1000*gs['mean']/h/EVALUABILITY_CAPACITY_MBPS,
                    regret_fresh_service_ms=1000*rf/h/EVALUABILITY_CAPACITY_MBPS,
                    regret_stale_service_ms=1000*rs/h/EVALUABILITY_CAPACITY_MBPS,
                    evaluable=eligible, tie_share_fresh=float(raw['tie_flags'][:, p, 0, ih].mean()),
                    tie_share_stale=float(raw['tie_flags'][:, p, t+1, ih].mean()),
                    Hybrid_minus_Stationary_fresh_Mbit_s=pair_f['mean'],
                    Hybrid_minus_Stationary_fresh_SE_Mbit_s=pair_f['se'],
                    Hybrid_minus_Stationary_stale_Mbit_s=pair_s['mean'],
                    Hybrid_minus_Stationary_stale_SE_Mbit_s=pair_s['se']))
    return rows, pairs, ties


def require_raw_committed(paths):
    """Read-only git check: every raw byte must already be in local HEAD."""
    head = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    for path in paths:
        path = Path(path)
        rel = path.resolve().relative_to(ROOT).as_posix()
        try:
            expected = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD:'+rel],
                                               text=True, stderr=subprocess.PIPE).strip()
        except subprocess.CalledProcessError as exc:
            raise ValueError('raw must be committed before score: '+rel) from exc
        actual = subprocess.check_output(['git', '-C', str(ROOT), 'hash-object', str(path)], text=True).strip()
        if expected != actual:
            raise ValueError('raw differs from committed HEAD: '+rel)
    return head


def score(out=OUT):
    """Descriptive rows only. Card verdicts are a separate, locked command."""
    out = Path(out)
    token = verify_lock(out)
    from experiments.letter import x4b_card
    x4b_card.verify(out)
    T.new(out / 'score.json', out / 'score.csv', out / 'score_paired.csv', out / 'score_tie_strict.csv')
    receipt = C.read_json(out / 'truth/receipt.json')
    if receipt['status'] != 'COMPLETE' or receipt['lock_sha256'] != token.digest:
        raise ValueError('cannot score INCOMPLETE truth or a different lock')
    records = planned_truth_records(out)
    metas = receipt['records']
    if len(metas) != len(records) or {(r['regime'], r['date']) for r in metas} != {(r['regime'], r['date']) for r in records}:
        raise ValueError('receipt does not contain all planned test-S records')
    manifest = C.read_json(out / 'truth/raw_manifest.json')['sha256']
    expected_files = {'truth/started.json'} | {f'truth/records/{r["regime"]}_{r["date"]}{ext}'
        for r in records for ext in ('.json', '.npz')}
    if set(manifest) != expected_files:
        raise ValueError('incomplete/extra raw manifest')
    for name, digest in manifest.items():
        if C.sha256(out / name) != digest:
            raise ValueError('raw checksum mismatch: '+name)
    actual_files = {str(p.relative_to(out)) for p in (out / 'truth/records').iterdir()}
    if actual_files != expected_files-{'truth/started.json'}:
        raise ValueError('incomplete/extra raw directory')
    head = require_raw_committed([out / n for n in sorted(expected_files)] +
        [out / 'truth/receipt.json', out / 'truth/raw_manifest.json'])
    rows, pairs, ties = [], [], []
    for meta in metas:
        stem = out / 'truth/records' / f"{meta['regime']}_{meta['date']}"
        if meta != C.read_json(stem.with_suffix('.json')) or meta['split'] != 'test' or meta['stratum'] != 'S' or meta['seed_base'] != TEST_SEED or meta['stage'] != 'truth':
            raise ValueError('invalid truth metadata')
        if C.sha256(stem.with_suffix('.npz')) != meta['npz_sha256']:
            raise ValueError('raw NPZ checksum mismatch')
        r, p, t = descriptive_rows(read_npz(stem.with_suffix('.npz')), meta)
        rows.extend(r)
        pairs.extend(p)
        ties.extend(t)
    T.write_csv(out / 'score.csv', rows)
    T.write_csv(out / 'score_paired.csv', pairs)
    T.write_csv(out / 'score_tie_strict.csv', ties)
    C.write_json(out / 'score.json', dict(owner='Doan Van Tai', rows=rows, paired_rows=pairs,
        tie_strict_rows=ties, lock_sha256=token.digest, raw_commit=head,
        sign='G_S=L_stale-L_fresh; negative=fresh hurts', independent_rescore='PENDING',
        service_ms_capacity_Mbps=EVALUABILITY_CAPACITY_MBPS,
        counts_are_not_independent_trials=True,
        both_side='max(mean regret fresh, mean regret stale_tau); one case per record,tau,h',
        tie_strict='Signed additive contributions over all instances; fresh counted once, not twice by tau.'))
    return dict(rows=len(rows), paired_rows=len(pairs), tie_strict_rows=len(ties))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('configure', 'step0', 'predict', 'pilot', 'lock', 'verify-lock', 'truth', 'score'))
    parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args(argv)
    if args.command in ('step0', 'truth'):
        result = dict(step0=step0, truth=truth)[args.command](args.out, args.workers)
    else:
        result = dict(configure=configure, predict=predict, pilot=pilot,
            lock=create_lock, score=score, **{'verify-lock': verify_lock})[args.command](args.out)
    if isinstance(result, C.VerifiedLock):
        emit(dict(verified=True, path=result.path, digest=result.digest))
    else:
        emit({k: result[k] for k in ('gate', 'decisions_record_count', 'projected_CPU_hours', 'status', 'rows', 'paired_rows', 'tie_strict_rows') if k in result})


if __name__ == '__main__':
    main()
