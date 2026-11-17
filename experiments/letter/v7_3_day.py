"""Doan Van Tai — V7-3 A2 daytime training and two-train-day pilot.

No test runner is provided. Night code/results are imported read-only.
All times retain the source clock, whose timezone is unspecified.
"""
import argparse
from datetime import datetime
from pathlib import Path
import platform
import subprocess
import time

import numpy as np

from experiments.ext_validity import ev_te as T
from experiments.letter import e4_geant as E
from experiments.letter import v7_3_data as D
from experiments.letter import v7_3_run as R
from experiments.letter import v7_3_sim as S

OUT = D.OUT / 'day_train'
TRAIN_SEED, PILOT_SEED = 7302001, 7372001
N, K, R_DEC, R_EVAL = 200, 64, 64, 128
FINE_DT = .005


def weekday_dates(dates):
    return [str(d) for d in dates if datetime.fromisoformat(str(d)).weekday() < 5]


def select_window(days):
    """All 73 non-wrapping six-hour windows; earliest start breaks exact ties."""
    days = np.asarray(days, dtype=float)
    if days.ndim != 3 or days.shape[1] != 96 or not len(days):
        raise ValueError('complete training weekdays required')
    scores = np.array([days[:, i:i+24].sum(axis=2).mean() for i in range(73)])
    return int(scores.argmax()), scores


def clock(slot):
    return f'{slot//4:02d}:{15*(slot%4):02d}'


def window_training(training, start):
    """Retain phase-A eligible weekdays; move the two-hour warmup to start-2h."""
    if start not in range(73):
        raise ValueError('same-day six-hour window required')
    mask = np.array([str(d) in weekday_dates(training['dates']) for d in training['dates']])
    days = training['days'][mask]
    previous = training['warm'][mask]
    # In the concatenation, slice start:start+8 ends exactly at decision time.
    past = np.concatenate([previous, days], axis=1)
    return dict(dates=training['dates'][mask], days=days[:, start:start+24],
                warm=past[:, start:start+8])


def regimes_for(net, days, capacity):
    routes, stay = D.routes_and_incidence(net)
    mean_od = days.mean(axis=(0, 1))
    mean_load = stay @ mean_od
    bottleneck = int(mean_load.argmax())  # EV-TE link order breaks ties.
    candidates = sorted(np.flatnonzero(stay[bottleneck]),
                        key=lambda j: (-mean_od[j], net['demands'][j]['id']))
    if len(candidates) < 3:
        raise ValueError('fewer than three managed flows')
    graph = {node: set() for node in net['nodes']}
    edge_index = {}
    for i, link in enumerate(net['links']):
        graph[link['source']].add(link['target'])
        edge_index[link['source'], link['target']] = i
    infos, incidences = [], []
    for rank, j in enumerate(candidates[:3], 1):
        demand = net['demands'][j]
        first, second = T.two_paths(graph, demand['source'], demand['target'])
        if first != routes[j] or second is None:
            raise ValueError('managed flow lacks the specified Yen second path')
        switch = stay.copy()
        switch[:, j] = 0
        for u, v in zip(second[:-1], second[1:]):
            switch[edge_index[u, v], j] = 1
        inc = np.stack([stay, switch])
        load = np.einsum('nsd,aed->nsae', days, inc, optimize=True)
        infos.append(dict(id=f'DAY{rank}', managed_OD=demand['id'],
                          source=demand['source'], target=demand['target'],
                          train_window_mean_volume_Mbps=float(mean_od[j]),
                          stay=list(first), switch=list(second),
                          switch_avoids_busiest_link=bool(switch[bottleneck, j] == 0),
                          max_mean_link_utilization=(
                              load.mean(axis=(0, 1)).max(axis=1)/capacity).tolist(),
                          peak_15min_link_utilization=(
                              load.max(axis=(0, 1, 3))/capacity).tolist(),
                          modulated_upper_utilization=(
                              (1+S.BETA)*load.max(axis=(0, 1, 3))/capacity).tolist()))
        incidences.append(inc)
    return infos, np.stack(incidences), bottleneck


def source_hashes():
    paths = [Path(__file__), Path(D.__file__), Path(R.__file__), Path(S.__file__),
             Path(E.__file__), Path(T.__file__),
             T.ROOT/'notes/ops/codex/V7_3_phaseA2_brief.md']
    paths += sorted((T.ROOT/'experiments/letter').glob('v7_3_day_*.py'))
    paths += sorted((T.ROOT/'tests').glob('test_letter_v7_3_day*.py'))
    return {str(p.relative_to(T.ROOT)): T.sha256(p) for p in paths}


def configure(out=OUT):
    T.new(out/'protocol.json', out/'configuration.json', out/'configuration.npz')
    brief = 'notes/ops/codex/V7_3_phaseA2_brief.md'
    if subprocess.check_output(['git', 'show', 'HEAD:'+brief]) != (T.ROOT/brief).read_bytes():
        raise ValueError('working brief differs from HEAD')
    # Record implementation conventions before selection or simulation outcomes.
    protocol = dict(
        owner='Doan Van Tai', training_only=True, test_outcomes_allowed=False,
        brief_HEAD=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        source_sha256=source_hashes(), seeds=dict(train=TRAIN_SEED, pilot=PILOT_SEED),
        rules=dict(
            days='phase-A manifest/cache eligibility unchanged; weekdays only',
            window='maximize mean total demand across train weekdays and 24 slots; 73 within-day starts, 15-min grid, earliest exact tie',
            capacity='phase-A daytime 06:00-21:45 peak Stay rule on retained train weekdays; compare with phase-A value',
            busiest='largest train-window mean directed-link Stay load; EV-TE link order breaks ties',
            managed='top three ODs crossing that link, descending train-window mean volume, OD ID breaks ties; no filter requiring Switch to avoid it',
            warmup='two hours before selected window, empty Stay queues and independent per-instance mode roots; same phase-A lookback construction',
            truth='real 15-min TM times independent OD two-state modulation, beta=.3, kappa=1/s; phase-A dt=.05s',
            telemetry='full state at decision start versus 5/15min earlier; actual past TM, K=64 Stay posterior samples',
            forecast='one train-average weekday profile, 24 slots of the selected window; no actual future input to M0',
            hybrid='M0 Switch-minus-Stay gap plus h*s_hat; stationary chooses Switch iff s_hat<0; exact ties Stay',
            s_hat='pooled mean per-day N200 integral-cost-rate difference Switch-minus-Stay over 6h',
            T_int='same letter first-zero estimator, first instance per day/action; no concatenation; undefined if zero variance',
            resolution='retain dt=.05s trace every train day; independent dt=.005s first-instance rollout on earliest weekday for each regime; also subsample .01/.05s; resolved only if T_int>=10*dt and <=5% change at 2*dt; zero covariance remains UNDEFINED at every dt',
            pilot='earliest train weekday and largest train-window total-demand weekday (earliest tie), distinct; N=2, keep K64/R_dec64/R_eval128',
            reporting='all results exploratory training/pilot; no test card, outcome, SSH or commit'),
        planned=dict(N=N, K=K, R_dec=R_DEC, R_eval=R_EVAL,
                     h_hours=[1, 2, 4, 6], tau_minutes=[5, 15],
                     dt_s=S.DT, resolution_dt_s=FINE_DT, pilot_N=2))
    E.write_json(out/'protocol.json', protocol)
    original, night_cf = D.load_training()
    weekdays = weekday_dates(original['dates'])
    mask = np.isin(original['dates'], weekdays)
    start, scores = select_window(original['days'][mask])
    training = window_training(original, start)
    net = D.topology()
    _, stay = D.routes_and_incidence(net)
    daytime = original['days'][mask, 24:88]
    capacity = D.capacity_rule(daytime.reshape(-1, stay.shape[1]), stay)
    capacity_load = daytime @ stay.T
    peak_day, peak_slot, peak_link = np.unravel_index(capacity_load.argmax(), capacity_load.shape)
    infos, incs, bottleneck = regimes_for(net, training['days'], capacity)
    profile = training['days'].mean(axis=0)
    manifest = T.read_json(D.OUT/'data_manifest.json')
    totals = training['days'].sum(axis=(1, 2))
    heaviest = int(totals.argmax())
    if heaviest == 0:
        heaviest = 1
    dates = training['dates'].tolist()
    config = dict(
        owner='Doan Van Tai', training_only=True, train_dates=dates,
        test_weekday_dates_metadata_only=weekday_dates(manifest['test_dates']),
        start_slot=start, window_start=clock(start), window_end=clock(start+24),
        mean_total_demand_Mbps=float(scores[start]), capacity_Mbps=capacity,
        phase_A_capacity_Mbps=float(night_cf['capacity'].item()),
        capacity_identical_to_phase_A=capacity == float(night_cf['capacity'].item()),
        capacity_peak_utilization=float(capacity_load.max()/capacity),
        capacity_peak_driver=dict(date=weekdays[peak_day], time=clock(24+peak_slot),
                                  link=net['links'][peak_link]['id'],
                                  load_Mbps=float(capacity_load.max())),
        busiest_Stay_link=net['links'][bottleneck]['id'],
        regimes=infos, pilot_dates=[dates[0], dates[heaviest]],
        warmup_Stay_modulated_upper_utilization=float(
            ((1+S.BETA)*np.einsum('nsd,ed->nse', training['warm'], stay, optimize=True)/capacity).max()),
        forecast_modulated_upper_utilization_by_regime=[
            float(((1+S.BETA)*np.einsum('sd,aed->sae', profile, inc, optimize=True)/capacity).max())
            for inc in incs],
        units=dict(demand='Mbit/s', backlog='Mbit', cost='Mbit*s', time='s'),
        cache_sha256=manifest['train_cache_sha256'],
        timezone='source clock; timezone/DST not established')
    E.write_npz(out/'configuration.npz', dict(
        incidence=incs, profiles=np.stack([profile, profile]), capacity=np.array(capacity),
        start_slot=np.array(start), dates=training['dates']))
    E.write_json(out/'configuration.json', config)
    T.write_csv(out/'window_candidates.csv', [
        dict(start=clock(i), end=clock(i+24), mean_total_demand_Mbps=float(value),
             selected=i == start) for i, value in enumerate(scores)])
    link_rows, day_rows, slope_rows = [], [], []
    for info, inc in zip(infos, incs):
        load = np.einsum('nsd,aed->nsae', training['days'], inc, optimize=True)/capacity
        for a, action in enumerate(('Stay', 'Switch')):
            for e, link in enumerate(net['links']):
                link_rows.append(dict(regime=info['id'], action=action, link=link['id'],
                                      mean_utilization=float(load[:, :, a, e].mean()),
                                      peak_utilization=float(load[:, :, a, e].max()),
                                      modulated_upper=float((1+S.BETA)*load[:, :, a, e].max())))
            for j, date in enumerate(dates):
                day_rows.append(dict(regime=info['id'], date=date, action=action,
                                     mean_utilization=float(load[j, :, a].mean()),
                                     max_mean_link_utilization=float(load[j, :, a].mean(axis=0).max()),
                                     peak_utilization=float(load[j, :, a].max())))
    for date, values in zip(dates, training['days']):
        total = values.sum(axis=1)
        slope_rows.append(dict(date=date, slope_Mbps_per_hour=float(
            np.polyfit((np.arange(24)+.5)*.25, total, 1)[0]),
            first_Mbps=float(total[0]), last_Mbps=float(total[-1]),
            min_Mbps=float(total.min()), max_Mbps=float(total.max()),
            coefficient_of_variation=float(total.std()/total.mean())))
    T.write_csv(out/'link_utilizations.csv', link_rows)
    T.write_csv(out/'day_utilizations.csv', day_rows)
    T.write_csv(out/'nonstationarity.csv', slope_rows)
    print(E.json_bytes(config).decode(), flush=True)
    return config


def load(out=OUT):
    protocol = T.read_json(out/'protocol.json')
    for name, digest in protocol['source_sha256'].items():
        if T.sha256(T.ROOT/name) != digest:
            raise ValueError('A2 source/protocol provenance changed: '+name)
    original, _ = D.load_training()
    config = T.read_json(out/'configuration.json')
    training = window_training(original, config['start_slot'])
    if training['dates'].tolist() != config['train_dates']:
        raise ValueError('A2 training calendar changed')
    with np.load(out/'configuration.npz', allow_pickle=False) as f:
        arrays = {k: f[k] for k in f.files}
    return training, arrays, config


def resolution(trace, dt):
    """Report resolution separately from zero variance and finite-window censoring."""
    trace = np.asarray(trace, dtype=float)
    if trace.ndim != 1 or len(trace) < 8 or not np.isfinite(trace).all():
        raise ValueError('finite one-dimensional backlog trace required')
    if np.ptp(trace) == 0:
        # Exact zero covariance does not require a large FFT.
        return dict(T_int_s=None, h6_over_T_int=None, censored=True,
                    status='UNDEFINED_ZERO_VARIANCE', dt_s=dt,
                    steps_per_T_int=None, lag1_acf=None,
                    relative_change_at_2dt=None, variance_Mbit2=0.,
                    error='zero-variance train series')
    ti, censored, error = T.estimate_tint(trace, dt)
    coarse, _, _ = T.estimate_tint(trace[::2], 2*dt)
    centered = trace-trace.mean()
    lag1 = float(np.dot(centered[:-1], centered[1:])/(len(trace)-1)/np.mean(centered**2))
    relative = R.ratio(abs(ti-coarse), ti) if ti is not None and coarse is not None else None
    resolved = ti is not None and ti >= 10*dt and relative is not None and relative <= .05
    return dict(T_int_s=ti, h6_over_T_int=R.ratio(21600, ti), censored=censored,
                status='RESOLVED' if resolved and not censored else 'UNRESOLVED',
                dt_s=dt, steps_per_T_int=R.ratio(ti, dt), lag1_acf=lag1,
                relative_change_at_2dt=relative,
                variance_Mbit2=float(np.var(trace)), error=error)


def sign_summary(values):
    values = np.asarray(values, dtype=float)
    pooled = float(values.mean())
    sign = int(np.sign(pooled))
    numerator = int((np.sign(values) == sign).sum()) if sign else None
    return dict(s_hat_Mbit=pooled, pooled_sign=sign,
                sign_counts=dict(positive=int((values > 0).sum()),
                                 zero=int((values == 0).sum()), negative=int((values < 0).sum())),
                nonzero_sign_stability_numerator=numerator,
                nonzero_sign_stability_denominator=len(values),
                nonzero_sign_stability_fraction=None if sign == 0 else numerator/len(values),
                exact_zero_fraction=float((values == 0).mean()))


def train(out=OUT):
    T.new(out/'summary.json')
    training, arrays, config = load(out)
    S.native()
    T.native()
    hs = np.rint(S.HOURS*3600/S.DT).astype(int)
    summaries, table = [], []
    for r, info in enumerate(config['regimes']):
        inc, cap = arrays['incidence'][r], arrays['capacity'].item()
        records = []
        for date in training['dates']:
            j = R.require_train(training, date)  # Before every simulator call.
            root = T.seed_for(TRAIN_SEED, f'V7-3-A2|{info["id"]}|{date}')
            timings = {}
            fresh, stale = R.timer(timings, 'warmup', lambda: S.warm_instances(
                inc, training['warm'][j], cap, N, T.seed_for(root, 'warm')))
            costs, _, _, trace = R.timer(timings, 'true_train_window', lambda: S.variable(
                inc, training['days'][j], cap, *fresh, T.seed_for(root, 'rate'),
                hs=hs, trace=True))
            rates = costs[:, :, -1]/21600
            delta = rates[:, 1]-rates[:, 0]
            m0 = R.timer(timings, 'M0_fresh', lambda: S.mean_rollout(
                inc, arrays['profiles'][0], cap, *fresh))
            old_costs = []
            for tau in S.TAU_SECONDS:
                pm, pq = R.timer(timings, f'posterior_{int(tau)}', lambda tau=tau: S.forward_posterior(
                    inc, training['warm'][j, -1], cap, stale[tau], tau, K,
                    T.seed_for(root, f'posterior-{tau}')))
                old = R.timer(timings, f'M0_stale_{int(tau)}', lambda: S.mean_rollout(
                    inc, arrays['profiles'][0], cap, pm, pq).reshape(N, K, 2, 4).mean(axis=1))
                old_costs.append(old)
            tint = [resolution(trace[:, a], S.DT) for a in range(2)]
            fine = None
            if str(date) == config['train_dates'][0]:
                fine_cost, _, _, fine_trace = R.timer(timings, 'fine_resolution', lambda: S.variable(
                    inc, training['days'][j], cap, fresh[0][:1], fresh[1][:1],
                    T.seed_for(root, 'fine-resolution'), dt=FINE_DT, trace=True))
                fine = [[resolution(fine_trace[::stride, a], FINE_DT*stride)
                         for stride in (1, 2, 10)] for a in range(2)]
                E.write_npz(out/f'resolution/{info["id"]}.npz', dict(
                    backlog=fine_trace, costs=fine_cost, dt_s=np.array(FINE_DT),
                    date=np.array(date)))
            meta = dict(
                owner='Doan Van Tai', regime=info['id'], date=str(date),
                training_only=True, N=N, K=K, seed=root, dt_s=S.DT,
                mean_backlog_rates_Mbit=rates.mean(axis=0).tolist(),
                s_hat_Mbit=float(delta.mean()),
                conditional_MC_SE_Mbit=float(delta.std(ddof=1)/np.sqrt(N)),
                T_int=tint, T_int_trace_instance=0, fine_resolution=fine,
                M0_tie_share_fresh=E.pick(m0)[1].mean(axis=0).tolist(),
                M0_tie_share_stale=[E.pick(old)[1].mean(axis=0).tolist() for old in old_costs],
                timings=timings)
            E.write_npz(out/f'raw/{info["id"]}_{date}.npz', dict(
                costs=costs, rates=rates, fresh_modes=fresh[0], fresh_queues=fresh[1],
                backlog_first_instance=trace, M0=m0, M0_stale=np.stack(old_costs)))
            E.write_json(out/f'raw/{info["id"]}_{date}.json', meta)
            records.append(meta)
            table.append(dict(regime=info['id'], date=str(date), s_hat_Mbit=meta['s_hat_Mbit'],
                              T_int_Stay_s=tint[0]['T_int_s'], T_int_Switch_s=tint[1]['T_int_s'],
                              T_int_Stay_status=tint[0]['status'], T_int_Switch_status=tint[1]['status'],
                              component_CPU_s=sum(t['CPU_s'] for t in timings.values())))
            print(E.json_bytes(dict(regime=info['id'], date=str(date),
                                   s_hat_Mbit=meta['s_hat_Mbit'],
                                   T_int_status=[x['status'] for x in tint])).decode().strip(), flush=True)
        summary = dict(
            regime=info['id'], train_days=len(records), N=N, K=K,
            **sign_summary([x['s_hat_Mbit'] for x in records]),
            mean_backlog_rates_Mbit=np.mean([x['mean_backlog_rates_Mbit'] for x in records], axis=0).tolist(),
            s_hat_conditional_MC_SE_Mbit=float(np.sqrt(sum(
                x['conditional_MC_SE_Mbit']**2 for x in records))/len(records)),
            M0_tie_share_fresh=np.mean([x['M0_tie_share_fresh'] for x in records], axis=0).tolist(),
            M0_tie_share_stale=np.mean([x['M0_tie_share_stale'] for x in records], axis=0).tolist(),
            T_int_defined_by_action=[sum(x['T_int'][a]['T_int_s'] is not None for x in records)
                                    for a in range(2)],
            T_int_by_day=[dict(date=x['date'], actions=x['T_int']) for x in records],
            fine_resolution=records[0]['fine_resolution'],
            full_train_component_CPU_s=sum(sum(t['CPU_s'] for t in x['timings'].values())
                                           for x in records))
        summaries.append(summary)
    result = dict(
        owner='Doan Van Tai', training_only=True, N=N, K=K, train_days=len(training['dates']),
        regimes=summaries, seed=TRAIN_SEED, dt_s=S.DT, resolution_dt_s=FINE_DT,
        test_days_simulated=0,
        interpretation='finite nonstationary train-window rates; no stationary mixing certificate or population inference',
        C_ref_all_train_pathwise_zero_certificate=bool(
            config['warmup_Stay_modulated_upper_utilization'] <= 1
            and all(max(r['modulated_upper_utilization']) <= 1 for r in config['regimes'])),
        C_ref_note='certificate uses empty initial Stay queues plus <=capacity full-modulation envelope; actual R_dec/R_eval reference is evaluated on the two train pilot days only')
    E.write_json(out/'summary.json', result)
    T.write_csv(out/'day_statistics.csv', table)
    return result


def compute_day(training, arrays, config, date, regime, s_hat, *,
                n=2, k=K, r_dec=R_DEC, r_eval=R_EVAL, seed=PILOT_SEED):
    R.require_train(training, date)
    if str(date) not in config['train_dates'] or datetime.fromisoformat(str(date)).weekday() >= 5:
        raise ValueError('A2 forbids non-training/non-weekday simulation')
    ids = [x['id'] for x in config['regimes']]
    if regime not in ids:
        raise ValueError('unknown daytime regime')
    r = ids.index(regime)
    cf = dict(incidence=arrays['incidence'][r], profiles=arrays['profiles'],
              capacity=arrays['capacity'])
    raw, meta = R.compute_night(
        training, cf, date, s_hat, n=n, k=k, r_dec=r_dec, r_eval=r_eval,
        seed=T.seed_for(seed, 'V7-3-A2|'+regime))
    meta.update(regime=regime, scenario='daytime held OD reroute', seed_base=seed,
                window=[config['window_start'], config['window_end']],
                warmup='selected window start minus two hours; phase-A adapter reused by relative time')
    return raw, meta


def project(records, test_days, full_n=N, workers=20):
    ids = sorted({r['regime'] for r in records})
    components = {}
    for regime in ids:
        rows = [r for r in records if r['regime'] == regime]
        if len(rows) != 2:
            raise ValueError('exactly two pilot train days per regime required')
        for row in rows:
            if (row['K'], row['R_dec'], row['R_eval']) != (K, R_DEC, R_EVAL):
                raise ValueError('projection requires fixed full K/R pilot counts')
        for name in rows[0]['timings']:
            components[name] = components.get(name, 0.) + test_days*np.mean([
                r['timings'][name]['CPU_s']*full_n/r['N'] for r in rows])
    cpu = float(sum(components.values()))
    # A second estimate uses the slower measured day independently per component/regime.
    stress = float(sum(test_days*max(r['timings'][name]['CPU_s']*full_n/r['N']
                                    for r in records if r['regime'] == regime)
                       for regime in ids for name in next(
                           r for r in records if r['regime'] == regime)['timings']))
    return dict(
        projected_CPU_s=cpu, projected_CPU_hours=cpu/3600,
        ideal_wall_s_20_workers=cpu/workers, ideal_wall_hours_20_workers=cpu/(workers*3600),
        slower_day_projected_CPU_s=stress, slower_day_ideal_wall_s_20_workers=stress/workers,
        CPU_s_by_component={k: float(v) for k, v in components.items()},
        full=dict(N=full_n, K=K, R_dec=R_DEC, R_eval=R_EVAL, test_weekdays=test_days,
                  regimes=len(ids), workers=workers, target='n2-standard-32'),
        rule='scale N only (200/2); K64/R_dec64/R_eval128 already used in pilot; sum 3 regimes and metadata-only test-day count',
        limitations=[
            'Local CPU-seconds; ideal 20-worker division, not measured GCP performance or an upper bound.',
            'Train pilot may activate exact empty-queue certificates that need not hold on test days.',
            'Slower-day estimate is a measured-training proxy, not a confidence interval or test-workload guarantee.',
            'No test demand intensity, state, cost or outcome has been computed.'])


def pilot(out=OUT):
    T.new(out/'pilot/summary.json')
    training, arrays, config = load(out)
    summary = T.read_json(out/'summary.json')
    records = []
    for info, learned in zip(config['regimes'], summary['regimes']):
        for date in config['pilot_dates']:
            raw, meta = compute_day(training, arrays, config, date, info['id'],
                                    learned['s_hat_Mbit'])
            path = out/f'pilot/{info["id"]}_{date}.npz'
            R.timer(meta['timings'], 'write_raw_npz', lambda: E.write_npz(path, raw))
            E.write_json(path.with_suffix('.json'), meta)
            records.append(meta)
            print(E.json_bytes(dict(regime=info['id'], date=date,
                                   C_ref=meta['C_ref_mean_Mbit_s'],
                                   CPU_s=sum(x['CPU_s'] for x in meta['timings'].values()))).decode().strip(), flush=True)
    projection = project(records, len(config['test_weekday_dates_metadata_only']))
    result = dict(
        owner='Doan Van Tai', training_only=True, pilot_dates=config['pilot_dates'],
        pilot_N=2, pilot_K=K, pilot_R_dec=R_DEC, pilot_R_eval=R_EVAL,
        seed=PILOT_SEED, records=records, **projection,
        hardware=dict(
            machine=platform.machine(), platform=platform.platform(),
            python=platform.python_version(),
            processor=next((line.split(':', 1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines()
                            if line.startswith('model name')), platform.processor())))
    E.write_json(out/'pilot/summary.json', result)
    T.write_csv(out/'pilot/component_timings.csv', [
        dict(regime=r['regime'], date=r['date'], component=name, **values)
        for r in records for name, values in r['timings'].items()])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['configure', 'train', 'pilot'])
    args = parser.parse_args()
    dict(configure=configure, train=train, pilot=pilot)[args.command]()
