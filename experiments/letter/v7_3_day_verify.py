"""Doan Van Tai — independent A2 saved-artifact replay, without simulator imports.

Does not import v7_3_day, v7_3_run, v7_3_sim or the E4 scorer.
The topology/cache reader is reused; paths, selection and scoring are rebuilt.
"""
import argparse
import csv
from datetime import datetime
import hashlib
import heapq
import json
from pathlib import Path
import subprocess

import numpy as np

from experiments.letter import v7_3_data as D

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'results/letter/v7_3/day_train'


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def same(x, y):
    np.testing.assert_allclose(x, y, rtol=1e-12, atol=1e-12)


def paths_two(graph, source, target):
    """Independently enumerate simple paths in hop-count/lexicographic order."""
    queue = [(1, (source,))]
    result = []
    while queue and len(result) < 2:
        _, path = heapq.heappop(queue)
        if path[-1] == target:
            result.append(path)
        else:
            for nxt in sorted(graph[path[-1]]):
                if nxt not in path:
                    new = path+(nxt,)
                    heapq.heappush(queue, (len(new), new))
    if len(result) != 2:
        raise AssertionError('missing second path')
    return result


def tint(series, dt):
    z = series-series.mean()
    if not np.any(z):
        return None, True
    n = len(z)
    c = np.fft.irfft(np.abs(np.fft.rfft(z, n=2*n))**2)[:n//4]
    c /= np.arange(n, n-len(c), -1)
    rho = c/c[0]
    hits = np.flatnonzero(rho <= 0)
    end = int(hits[0]) if len(hits) else len(rho)-1
    value = np.trapezoid(rho[:end], dx=dt)
    value += .5*rho[end-1]*dt*(rho[end-1]/(rho[end-1]-rho[end]) if len(hits) else 1)
    return float(value), not bool(len(hits))


def verify(out=OUT):
    result_path = out/'verification.json'
    if result_path.exists():
        raise FileExistsError(result_path)
    initial = read(out/'initial_integrity.json')
    protocol = read(out/'protocol.json')
    config = read(out/'configuration.json')
    summary = read(out/'summary.json')
    pilot = read(out/'pilot/summary.json')
    manifest = read(D.OUT/'data_manifest.json')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert head == initial['HEAD'] == protocol['brief_HEAD']
    brief = 'notes/ops/codex/V7_3_phaseA2_brief.md'
    assert hashlib.sha256(subprocess.check_output(
        ['git', 'show', 'HEAD:'+brief])).hexdigest() == initial['brief_sha256'] == digest(ROOT/brief)
    changed = [name for name, sha in initial['sha256'].items()
               if not (ROOT/name).is_file() or digest(ROOT/name) != sha]
    assert not changed, changed
    for name, sha in protocol['source_sha256'].items():
        assert digest(ROOT/name) == sha, name
    assert digest(manifest['train_cache']) == manifest['train_cache_sha256'] == config['cache_sha256']
    with np.load(manifest['train_cache'], allow_pickle=False) as f:
        original = {k: f[k] for k in f.files}
    original_dates = original['dates'].tolist()
    assert original_dates == manifest['train_dates']
    keep = [i for i, date in enumerate(original_dates) if datetime.fromisoformat(date).weekday() < 5]
    dates = [original_dates[i] for i in keep]
    test = [d for d in manifest['test_dates'] if datetime.fromisoformat(d).weekday() < 5]
    assert dates == config['train_dates'] and test == config['test_weekday_dates_metadata_only']
    assert not set(dates) & set(test)
    full_days = original['days'][keep]
    # A cumulative-sum implementation independent of select_window's slicing.
    daily_totals = full_days.sum(axis=2)
    prefixes = np.pad(np.cumsum(daily_totals, axis=1), ((0, 0), (1, 0)))
    scores = (prefixes[:, 24:]-prefixes[:, :-24]).mean(axis=0)/24
    start = int(scores.argmax())
    assert start == config['start_slot']
    same(scores[start], config['mean_total_demand_Mbps'])
    with (out/'window_candidates.csv').open() as f:
        windows = list(csv.DictReader(f))
    assert len(windows) == 73
    same([float(r['mean_total_demand_Mbps']) for r in windows], scores)
    days = full_days[:, start:start+24]
    past = np.concatenate([original['warm'][keep], full_days], axis=1)[:, start:start+8]
    net = D.topology()
    graph = {node: set() for node in net['nodes']}
    edge = {}
    for e, link in enumerate(net['links']):
        graph[link['source']].add(link['target'])
        edge[link['source'], link['target']] = e
    stay = np.zeros((len(net['links']), len(net['demands'])))
    paths = [paths_two(graph, d['source'], d['target']) for d in net['demands']]
    for j, pp in enumerate(paths):
        for u, v in zip(pp[0][:-1], pp[0][1:]):
            stay[edge[u, v], j] = 1
    capacity = float((full_days[:, 24:88] @ stay.T).max()/.9)
    same(capacity, config['capacity_Mbps'])
    with np.load(out/'configuration.npz', allow_pickle=False) as f:
        arrays = {k: f[k] for k in f.files}
    same(arrays['profiles'], np.repeat(days.mean(axis=0)[None], 2, axis=0))
    same(arrays['capacity'].item(), capacity)
    mean_od = days.mean(axis=(0, 1))
    bottleneck = int((stay @ mean_od).argmax())
    assert net['links'][bottleneck]['id'] == config['busiest_Stay_link']
    ranked = sorted(np.flatnonzero(stay[bottleneck]),
                    key=lambda j: (-mean_od[j], net['demands'][j]['id']))[:3]
    assert [net['demands'][j]['id'] for j in ranked] == [r['managed_OD'] for r in config['regimes']]
    warm_upper = float((1.3*(past @ stay.T)/capacity).max())
    same(warm_upper, config['warmup_Stay_modulated_upper_utilization'])
    all_certificate = warm_upper <= 1
    expected_links, expected_day_utils = {}, {}
    for r, (info, j) in enumerate(zip(config['regimes'], ranked)):
        assert info['stay'] == list(paths[j][0]) and info['switch'] == list(paths[j][1])
        switch = stay.copy()
        switch[:, j] = 0
        for u, v in zip(paths[j][1][:-1], paths[j][1][1:]):
            switch[edge[u, v], j] = 1
        expected = np.stack([stay, switch])
        np.testing.assert_array_equal(expected, arrays['incidence'][r])
        assert info['switch_avoids_busiest_link'] == (switch[bottleneck, j] == 0)
        load = np.einsum('nsd,aed->nsae', days, expected, optimize=True)/capacity
        same(load.max(axis=(0, 1, 3)), info['peak_15min_link_utilization'])
        same(load.mean(axis=(0, 1)).max(axis=1), info['max_mean_link_utilization'])
        same(1.3*load.max(axis=(0, 1, 3)), info['modulated_upper_utilization'])
        all_certificate &= bool((1.3*load <= 1).all())
        for a, action in enumerate(('Stay', 'Switch')):
            for e, link in enumerate(net['links']):
                expected_links[info['id'], action, link['id']] = (
                    load[:, :, a, e].mean(), load[:, :, a, e].max(), 1.3*load[:, :, a, e].max())
            for i, date in enumerate(dates):
                expected_day_utils[info['id'], date, action] = (
                    load[i, :, a].mean(), load[i, :, a].mean(axis=0).max(), load[i, :, a].max())
    with (out/'link_utilizations.csv').open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(expected_links)
    for row in rows:
        same([float(row[k]) for k in ('mean_utilization', 'peak_utilization', 'modulated_upper')],
             expected_links[row['regime'], row['action'], row['link']])
    with (out/'day_utilizations.csv').open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(expected_day_utils)
    for row in rows:
        same([float(row[k]) for k in ('mean_utilization', 'max_mean_link_utilization', 'peak_utilization')],
             expected_day_utils[row['regime'], row['date'], row['action']])
    assert all_certificate == summary['C_ref_all_train_pathwise_zero_certificate']
    with (out/'nonstationarity.csv').open() as f:
        slopes = list(csv.DictReader(f))
    assert [r['date'] for r in slopes] == dates
    for row, values in zip(slopes, days):
        x = (np.arange(24)+.5)*.25
        total = values.sum(axis=1)
        slope = np.dot(x-x.mean(), total-total.mean())/np.dot(x-x.mean(), x-x.mean())
        same(slope, float(row['slope_Mbps_per_hour']))
        same([total[0], total[-1], total.min(), total.max(), total.std()/total.mean()],
             [float(row[k]) for k in ('first_Mbps', 'last_Mbps', 'min_Mbps', 'max_Mbps', 'coefficient_of_variation')])
    for info, learned in zip(config['regimes'], summary['regimes']):
        rate_gaps, means, variances, ties_fresh, ties_stale = [], [], [], [], []
        for date in dates:
            path = out/f'raw/{info["id"]}_{date}.npz'
            meta = read(path.with_suffix('.json'))
            assert meta['date'] == date and meta['training_only']
            assert meta['N'] == 200 and meta['K'] == 64
            with np.load(path, allow_pickle=False) as f:
                rates = f['costs'][:, :, -1]/21600
                np.testing.assert_array_equal(rates, f['rates'])
                delta = rates[:, 1]-rates[:, 0]
                rate_gaps.append(delta.mean())
                means.append(rates.mean(axis=0))
                variances.append(delta.var(ddof=1)/len(delta))
                same(delta.mean(), meta['s_hat_Mbit'])
                same(np.sqrt(variances[-1]), meta['conditional_MC_SE_Mbit'])
                for a in range(2):
                    ti, censored = tint(f['backlog_first_instance'][:, a], .05)
                    saved = meta['T_int'][a]
                    assert censored == saved['censored']
                    if ti is None:
                        assert saved['T_int_s'] is None and saved['h6_over_T_int'] is None
                        assert saved['status'] == 'UNDEFINED_ZERO_VARIANCE'
                    else:
                        same(ti, saved['T_int_s'])
                        same(21600/ti, saved['h6_over_T_int'])
                fresh = (f['M0'] == f['M0'].min(axis=1, keepdims=True)).sum(axis=1) > 1
                old = (f['M0_stale'] == f['M0_stale'].min(axis=2, keepdims=True)).sum(axis=2) > 1
                same(fresh.mean(axis=0), meta['M0_tie_share_fresh'])
                same(old.mean(axis=1), meta['M0_tie_share_stale'])
                ties_fresh.append(fresh.mean(axis=0))
                ties_stale.append(old.mean(axis=1))
                if all_certificate:
                    assert not f['costs'].any() and not f['fresh_queues'].any()
                    assert not f['backlog_first_instance'].any() and not f['M0'].any() and not f['M0_stale'].any()
        pooled = float(np.mean(rate_gaps))
        same(pooled, learned['s_hat_Mbit'])
        same(np.mean(means, axis=0), learned['mean_backlog_rates_Mbit'])
        same(np.sqrt(sum(variances))/len(dates), learned['s_hat_conditional_MC_SE_Mbit'])
        counts = dict(positive=sum(x > 0 for x in rate_gaps), zero=sum(x == 0 for x in rate_gaps),
                      negative=sum(x < 0 for x in rate_gaps))
        assert counts == learned['sign_counts']
        if pooled == 0:
            assert learned['nonzero_sign_stability_fraction'] is None
        else:
            same(sum(np.sign(x) == np.sign(pooled) for x in rate_gaps)/len(dates),
                 learned['nonzero_sign_stability_fraction'])
        same(np.mean(ties_fresh, axis=0), learned['M0_tie_share_fresh'])
        same(np.mean(ties_stale, axis=0), learned['M0_tie_share_stale'])
        with np.load(out/f'resolution/{info["id"]}.npz', allow_pickle=False) as f:
            assert str(f['date'].item()) == dates[0] and f['dt_s'].item() == .005
            assert len(f['backlog']) == round(21600/.005)
            for a in range(2):
                for k, stride in enumerate((1, 2, 10)):
                    ti, censored = tint(f['backlog'][::stride, a], stride*.005)
                    saved = learned['fine_resolution'][a][k]
                    assert saved['censored'] == censored
                    if ti is None:
                        assert saved['T_int_s'] is None and saved['status'] == 'UNDEFINED_ZERO_VARIANCE'
                    else:
                        same(ti, saved['T_int_s'])
    assert len(pilot['records']) == 6 and pilot['pilot_dates'] == config['pilot_dates']
    assert len(set(config['pilot_dates'])) == 2 and set(config['pilot_dates']) <= set(dates)
    for meta in pilot['records']:
        assert meta['date'] in dates and meta['date'] not in test
        assert (meta['N'], meta['K'], meta['R_dec'], meta['R_eval']) == (2, 64, 64, 128)
        with np.load(out/f'pilot/{meta["regime"]}_{meta["date"]}.npz', allow_pickle=False) as f:
            assert f['reference_decision_rollouts'].shape == (2, 64, 2, 4)
            assert f['paired_evaluation'].shape == (2, 128, 2, 4)
            v = f['paired_evaluation'].mean(axis=1)
            np.testing.assert_array_equal(v, f['V'])
            ref_costs = f['reference_decision_rollouts'].mean(axis=1)
            ref = ref_costs.argmin(axis=1)
            np.testing.assert_array_equal(ref, f['reference_decision'])
            cref = np.take_along_axis(v, ref[:, None, :], axis=1)[:, 0]
            np.testing.assert_array_equal(cref, f['C_ref'])
            decisions = f['decisions']
            selected = np.empty(decisions.shape)
            for index in np.ndindex(decisions.shape):
                i, p, side, tau, h = index
                selected[index] = v[i, decisions[index], h]
            np.testing.assert_array_equal(selected, f['costs'])
            np.testing.assert_array_equal(selected-cref[:, None, None, None], f['regret'])
            np.testing.assert_array_equal(selected[:, :, 1]-selected[:, :, 0], f['G_S'])
            same(cref.mean(axis=0), meta['C_ref_mean_Mbit_s'])
            same(f['regret'].mean(axis=0), meta['regret_mean_Mbit_s'])
            same(f['G_S'].mean(axis=0), meta['G_S_mean_Mbit_s'])
            np.testing.assert_array_equal(cref.mean(axis=0) > 0, meta['percentages_defined'])
            assert meta['reference_evaluation_streams_distinct']
            if all_certificate:
                assert not cref.any() and not f['regret'].any() and not f['G_S'].any()
                assert not decisions.any() and f['tie_flags'].all()
    components = {}
    slower = 0.
    for regime in [r['id'] for r in config['regimes']]:
        records = [r for r in pilot['records'] if r['regime'] == regime]
        assert len(records) == 2
        for name in records[0]['timings']:
            measured = [r['timings'][name]['CPU_s']*200/r['N'] for r in records]
            components[name] = components.get(name, 0.)+len(test)*sum(measured)/2
            slower += len(test)*max(measured)
    assert set(components) == set(pilot['CPU_s_by_component'])
    for name, value in components.items():
        same(value, pilot['CPU_s_by_component'][name])
    same(sum(components.values()), pilot['projected_CPU_s'])
    same(sum(components.values())/20, pilot['ideal_wall_s_20_workers'])
    same(slower, pilot['slower_day_projected_CPU_s'])
    result = dict(
        owner='Doan Van Tai', status='PASS', training_only=True,
        independent_saved_artifact_replay=True, simulator_calls=0, test_days_simulated=0,
        original_files_checked=len(initial['sha256']), original_files_changed=changed,
        source_files_checked=len(protocol['source_sha256']), HEAD_unchanged=True,
        train_weekdays=len(dates), test_weekdays_metadata_only=len(test),
        regimes=len(config['regimes']), train_records_checked=len(dates)*len(config['regimes']),
        pilot_records_checked=len(pilot['records']), link_rows_checked=len(expected_links),
        day_utilization_rows_checked=len(expected_day_utils), window_candidates_checked=len(windows),
        C_ref_all_train_pathwise_zero_certificate=bool(all_certificate),
        scientific_interpretation='TRAINING_DEGENERATE' if all_certificate else 'TRAINING_ONLY',
        T_int_note='zero covariance is undefined, not an estimate near dt or infinite h/T_int',
        checks=[
            'HEAD brief and all original tracked/protected V7-1 file bytes',
            'train-cache fingerprint, weekday split and absence of test dates in raw records',
            'independent rolling-window selection, simple-path enumeration and top-three OD ranking',
            'capacity, action incidences, per-link/per-day utilization and nonstationarity',
            'raw integrals/rates, s_hat signs, Monte Carlo SE, M0 tie denominators and first-zero T_int',
            'dt=.005/.01/.05 fine-resolution trace replay',
            'reference CRN decision/evaluation gather, regret and G_S for 1/2/4/6h',
            'all three regimes in N200/K64/R_dec64/R_eval128 compute extrapolation'])
    with result_path.open('x') as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    verify()
