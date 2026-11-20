"""Doan Van Tai — X2/X4, train-selected GÉANT routes and decisions-only screen.

Implements DESIGN_X_GEANT.md at letter_smr commit 581e769. Imports the V7-3
fluid, posterior, exact-tie and CRN helpers unchanged. No work on import.
The pilot is the sole preparation command allowed to evaluate a test input,
with its own seed; truth and score are explicit, independently gated commands.
"""
import argparse
import ast
from concurrent.futures import ProcessPoolExecutor
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

ROOT = T.ROOT
OUT = ROOT / 'results/letter/x_geant'
BRIEF = Path('/home/vantai/state-model-regret-papers/letter_smr/briefs/strengthen/DESIGN_X_GEANT.md')
BRIEF_COMMIT = '581e769'
BRIEF_SHA256 = 'f48112dc1b277bc1116648f337aa2cec432abf1c0737d3bab5afded4447e6e1b'
BASE = D.OUT / 'day_train_congested'
TEST_SEED, TRAIN_SEED, PILOT_SEED = 7412001, 7402001, 7472001
N, K, R_DEC, R_EVAL = 32, 64, 64, 128
H_SECONDS = np.array([3600, 7200, 14400, 21600], dtype=int)
THETAS = (.5, .65, .8, .9)
PIPES = ('M0', 'Hybrid', 'Stationary', 'TH_0.5', 'TH_0.65', 'TH_0.8', 'TH_0.9', 'MLU')
SIDES = ('fresh', 'stale_300', 'stale_900')


def npz(path, arrays):
    C.atomic_write(path, lambda p: E.write_npz(p, arrays))


def text_file(path, value):
    C.atomic_write(path, lambda p: p.write_text(value))


def read_npz(path):
    with np.load(path, allow_pickle=False) as f:
        return {k: f[k] for k in f.files}


def emit(value):
    print(json.dumps(value, sort_keys=True, allow_nan=False), flush=True)


def source_paths():
    """Only the local import closure; never inspect the parallel X-CTMC job."""
    pending, found = [Path(__file__).resolve().relative_to(ROOT)], set()
    while pending:
        rel = pending.pop()
        if rel in found or not (ROOT / rel).is_file():
            continue
        found.add(rel)
        for parent in rel.parents:
            init = parent / '__init__.py'
            if (ROOT / init).is_file() and init not in found:
                pending.append(init)
        for node in ast.walk(ast.parse((ROOT / rel).read_text())):
            modules = []
            if isinstance(node, ast.Import):
                modules = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module] + [node.module + '.' + a.name for a in node.names]
            for module in modules:
                p = Path(*module.split('.'))
                for candidate in (p.with_suffix('.py'), p / '__init__.py'):
                    if (ROOT / candidate).is_file() and candidate not in found:
                        pending.append(candidate)
    return sorted(found)


def dependencies():
    files = {str(p): ROOT / p for p in source_paths()}
    for p in (ROOT / 'tests/test_x_geant.py', ROOT / 'experiments/explore_ctmc/env.sh',
              D.OUT / 'data_manifest.json', D.OUT / 'CARD_V7_3.md',
              D.OUT / 'card_v7_3_params.json', BASE / 'configuration.json',
              BASE / 'configuration.npz', BASE / 'protocol.json'):
        files[str(p.relative_to(ROOT))] = p
    data = T.data_root()
    files.update({'brief:581e769': BRIEF, 'sndlib:archive': data / D.TM_NAME,
                  'sndlib:topology': data / 'sndlib-networks-native/geant.txt',
                  'sndlib:train_cache': data / 'v7_3_train.npz'})
    return files


def fingerprints():
    hashes = {name: C.sha256(p) for name, p in sorted(dependencies().items())}
    if hashes['brief:581e769'] != BRIEF_SHA256:
        raise ValueError('brief differs from approved 581e769')
    manifest = C.read_json(D.OUT / 'data_manifest.json')
    for key, field in (('archive', 'sha256'), ('topology', 'topology_sha256'),
                       ('train_cache', 'train_cache_sha256')):
        if hashes['sndlib:' + key] != manifest[field]:
            raise ValueError('SNDlib input drift: ' + key)
    return hashes


def check_sources(out):
    protocol = C.read_json(Path(out) / 'protocol.json')
    if protocol['sha256'] != fingerprints():
        raise ValueError('preparation source/input drift; retain old attempt, do not overwrite')
    return protocol


def seeds_for(seed, regime, date):
    # These numeric test/pilot bases already occur in V7-4. Keep the explicit
    # brief numbers, and separate every actual RNG stream by this namespace.
    root = T.seed_for(seed, f'X-GEANT|{regime}|{date}')
    labels = ('warm', 'rate', 'posterior-300.0', 'posterior-900.0',
              'reference-decision', 'evaluation')
    return dict(base=seed, record=root, **{x: T.seed_for(root, x) for x in labels})


def select_regimes(net, days, capacity, old_ods):
    """Selection is entirely input-only, with deterministic training ranks."""
    routes, stay = D.routes_and_incidence(net)
    mean_od = np.asarray(days).mean(axis=(0, 1))
    busy = int((stay @ mean_od).argmax())
    edge = {(e['source'], e['target']): i for i, e in enumerate(net['links'])}
    graph = {n: set() for n in net['nodes']}
    for u, v in edge:
        graph[u].add(v)
    candidates, arrays = [], {}
    for j, demand in enumerate(net['demands']):
        if demand['id'] in old_ods or mean_od[j] <= 0:
            continue
        first, second = T.two_paths(graph, demand['source'], demand['target'])
        if second is None:
            continue
        if first != routes[j]:
            raise ValueError('EV-TE first path changed')
        se = np.flatnonzero(stay[:, j])
        we = np.array([edge[u, v] for u, v in zip(second[:-1], second[1:])])
        switch = stay.copy()
        switch[:, j] = 0
        switch[we, j] = 1
        inc = np.stack((stay, switch))
        u = inc @ mean_od / capacity
        us, uw = float(u[0, se].max()), float(u[1, we].max())
        # Prefer two different busy links for X4, but do not impose a new
        # utilization cutoff or select by any queue/cost/decision outcome.
        sb = set(se[u[0, se] == us].tolist())
        wb = set(we[u[1, we] == uw].tolist())
        row = dict(managed_OD=demand['id'], managed_index=j,
                   source=demand['source'], target=demand['target'],
                   stay=list(first), switch=list(second),
                   stay_edges=se.tolist(), switch_edges=we.tolist(),
                   train_window_mean_volume_Mbps=float(mean_od[j]),
                   stay_uses_busiest_link=bool(stay[busy, j]),
                   switch_avoids_busiest_link=bool(switch[busy, j] == 0),
                   distinct_path_bottlenecks=sb.isdisjoint(wb),
                   path_max_mean_utilization=[us, uw],
                   switch_to_stay_path_utilization_ratio=uw/us,
                   X2_eligible=bool(stay[busy, j] and switch[busy, j] == 0),
                   X4_eligible=bool(uw >= .75*us))
        candidates.append(row)
        arrays[demand['id']] = inc
    new = sorted((r for r in candidates if r['X2_eligible']),
                 key=lambda r: (-r['train_window_mean_volume_Mbps'], r['managed_OD']))[:3]
    used = {r['managed_OD'] for r in new}
    both = sorted((r for r in candidates if r['X4_eligible'] and r['managed_OD'] not in used),
                  key=lambda r: (not r['distinct_path_bottlenecks'],
                                 -min(r['path_max_mean_utilization']),
                                 -r['train_window_mean_volume_Mbps'], r['managed_OD']))[:3]
    if len(new) != 3 or len(both) != 3:
        raise ValueError('not enough training-only candidate routes')
    infos, incs = [], []
    for group, prefix, selected in (('X2', 'NEW', new), ('X4', 'BOTH', both)):
        for rank, candidate in enumerate(selected, 1):
            infos.append(dict(candidate, id=prefix + str(rank), set=group))
            incs.append(arrays[candidate['managed_OD']])
    return infos, np.stack(incs), busy, candidates


def configure(out=OUT):
    out = Path(out)
    T.new(out / 'protocol.json', out / 'configuration.json', out / 'configuration.npz')
    # Record all choices before selecting routes and before opening test-day TMs.
    protocol = dict(owner='Doan Van Tai', schema='x-geant-protocol-v1',
        brief_commit=BRIEF_COMMIT, sha256=fingerprints(),
        parameters=dict(N=N, K=K, R_dec=R_DEC, R_eval=R_EVAL, dt_s=S.DT,
                        beta=S.BETA, flip_rate_per_s=1., c=0., h_seconds=H_SECONDS.tolist(),
                        tau_seconds=list(S.TAU_SECONDS), theta=list(THETAS)),
        seeds=dict(test=TEST_SEED, train=TRAIN_SEED, pilot=PILOT_SEED,
                   namespace='X-GEANT|regime|date',
                   collision_note='7412001/7472001 were used by V7-4; explicit brief bases retained, actual streams are domain separated'),
        selection=dict(X2='exclude DAY1/2/3 ODs; Stay crosses global busiest link, Yen-2 Switch avoids it; descending train mean OD, then OD id',
                       X4='exclude old and selected X2 ODs; Switch path max train mean utilization >= .75 * Stay path max; prefer distinct bottlenecks, then descending min(two path maxima), descending mean OD, OD id',
                       utilization='total load with managed OD exactly once on the action-specific path; 26 train weekday/window average'),
        slope_training='N32 independent initial states on each of 26 train weekdays; 6h action-paired rate rollout, pooled per-day mean Switch-minus-Stay, including S and O; not test outcomes',
        screen=dict(X2='test-S: pool 3 regimes and both tau; one comparison per instance/tau, no horizon duplication; any TH >= 1% disagreement',
                    X4='test-S: pool 3 regimes and unique fresh/stale300/stale900 sides for each h; Hybrid/Stationary >=1% at h=1h or 2h',
                    train='identical tables on all train days and separately train-S; training gates descriptive only',
                    threshold=.01, O_test='NOT_RUN before any decisions or evaluation',
                    independence='counts are denominators sharing days/instances, not independent trials'),
        utilization=dict(fresh='decision slot TM (first window slot) times observed OD modes; full routed load, no queues',
                         stale='same decision slot TM times empirical endpoint-mode expectation from the same K Stay posterior samples as M0',
                         tie='MLU: equal path maxima; TH: exact Stay-threshold equality or equal path maxima while threshold active; report both boundaries too',
                         theta_ge_1='no Switch when max-util Stay<=1; no universal guarantee with instantaneous overload, per literal section 4 formula',
                         long_age='CTMC expected modes decay exp(-2*tau); analytic expectation equals slot mean at infinite age, empirical K still has sampling noise'),
        prediction=dict(population='train-S only; deltaF=Switch stale share minus fresh share',
                        sign='sign(pooled s_hat * deltaF), horizons 4h and 6h',
                        null='sign((train-S mean max-util Switch minus Stay, equally weighted days/instances/unique sides) * deltaF); no queues'),
        pilot='one full N32/K64/Rdec64/Reval128 record; max input-only active-link/OD step-work proxy over test-S, earliest regime/date tie; seed pilot; selection before outcomes',
        G_S='L_stale - L_fresh, as letter Sec II/V7-3 and brief section 6; section 8 fresh-minus-stale is inconsistent',
        exposure=['old V7-3/V7-4 data and decision results known; new ODs do not make underlying days unseen',
                  'test input matrices/strata and decision states may be read by step0; no future evaluation',
                  'pilot outcomes use a separate seed and are exposure before truth'],
        authority='approved design implementation; AI work is not author self-writing or mentor review',
        commit_policy='no commit in this task; lock is a content hash, not a claim of committed preregistration')
    C.write_json(out / 'protocol.json', protocol)
    old = C.read_json(BASE / 'configuration.json')
    original, _ = D.load_training()
    training = A.window_training(original, old['start_slot'])
    if training['dates'].tolist() != old['train_dates'] or len(training['dates']) != 26:
        raise ValueError('V7-3 training calendar changed')
    cap = float(old['capacity_Mbps'])
    if cap != float(np.asarray(read_npz(BASE / 'configuration.npz')['capacity']).item()):
        raise ValueError('capacity mismatch')
    net = D.topology()
    infos, incs, busy, candidates = select_regimes(net, training['days'], cap,
                                                {r['managed_OD'] for r in old['regimes']})
    profile = training['days'].mean(axis=0)
    arrays = dict(incidence=incs, profiles=np.stack([profile, profile]), capacity=np.array(cap))
    table = []
    for info, inc in zip(infos, incs):
        load = np.einsum('nsd,aed->nsae', training['days'], inc, optimize=True)/cap
        info['network_max_mean_utilization'] = load.mean(axis=(0, 1)).max(axis=1).tolist()
        info['peak_15min_utilization'] = load.max(axis=(0, 1, 3)).tolist()
        for a, side in enumerate(('Stay', 'Switch')):
            path_edges = info['stay_edges'] if a == 0 else info['switch_edges']
            for e, link in enumerate(net['links']):
                table.append(dict(regime=info['id'], set=info['set'], action=side,
                    managed_OD=info['managed_OD'], link=link['id'], on_managed_path=e in path_edges,
                    mean_utilization=float(load[:, :, a, e].mean()),
                    peak_15min_utilization=float(load[:, :, a, e].max())))
    config = dict(owner='Doan Van Tai', training_only_selection=True,
        capacity_Mbps=cap, start_slot=old['start_slot'], window_start=old['window_start'],
        window_end=old['window_end'], train_dates=training['dates'].tolist(),
        busiest_Stay_link=net['links'][busy]['id'], regimes=infos,
        rules=protocol['selection'], protocol_sha256=C.sha256(out / 'protocol.json'))
    npz(out / 'configuration.npz', arrays)
    C.write_json(out / 'configuration.json', config)
    T.write_csv(out / 'train_utilizations.csv', table)
    T.write_csv(out / 'candidate_ranking_inputs.csv', [
        {k: v for k, v in r.items() if k not in ('stay', 'switch', 'stay_edges', 'switch_edges')}
        for r in candidates])
    text_file(out / 'regimes.md', regime_markdown(config))
    return config


def regime_markdown(config):
    lines = ['# X-GÉANT — lựa chọn chỉ từ train', '', 'Người phụ trách: Doan Van Tai.', '',
             f"Capacity {config['capacity_Mbps']:.12f} Mbit/s; 26 weekday, window {config['window_start']}–{config['window_end']}.", '',
             '| Regime | OD | mean OD (Mbit/s) | max-util path Stay | max-util path Switch | ratio |',
             '|---|---|---:|---:|---:|---:|']
    for r in config['regimes']:
        us, uw = r['path_max_mean_utilization']
        lines.append(f"| {r['id']} | {r['managed_OD']} | {r['train_window_mean_volume_Mbps']:.6f} | {us:.9f} | {uw:.9f} | {uw/us:.9f} |")
    for r in config['regimes']:
        lines += ['', r['id'] + ' Stay: ' + ' → '.join(r['stay']),
                  r['id'] + ' Switch: ' + ' → '.join(r['switch'])]
    lines += ['', 'Tiêu chí: ' + json.dumps(config['rules'], ensure_ascii=False), '',
              'Bảng từng link/action: train_utilizations.csv. Đây là offered-load trung bình train, không phải chứng nhận cả hai path thực sự có queue.', '']
    return '\n'.join(lines)


def load_context(out=OUT, *, include_test=False):
    out = Path(out)
    check_sources(out)
    config = C.read_json(out / 'configuration.json')
    arrays = read_npz(out / 'configuration.npz')
    original, _ = D.load_training()
    training = A.window_training(original, config['start_slot'])
    if training['dates'].tolist() != config['train_dates']:
        raise ValueError('training calendar drift')
    datasets = {'train': training}
    if include_test:
        manifest = C.read_json(D.OUT / 'data_manifest.json')
        dates = A.weekday_dates(manifest['test_dates'])
        # Only an opaque verified preparation receipt is passed to the unchanged
        # V7-3 loader; this is not a truth authorization token.
        path = out / 'protocol.json'
        token = C.VerifiedLock(str(path.resolve()), C.sha256(path))
        testing, exclusions = V3.load_days(dates, config, verified=token)
        if exclusions:
            raise ValueError('eligible V7-3 input dates changed: ' + repr(exclusions))
        datasets['test'] = testing
    return datasets, arrays, config


def records_for(data, arrays, config, split):
    rows = []
    for r, info in enumerate(config['regimes']):
        for j, date in enumerate(data['dates']):
            label = V3.strata(data['days'][j], arrays['incidence'][r], arrays['capacity'])
            rows.append(dict(split=split, regime=info['id'], set=info['set'], date=str(date),
                             **label, status='NOT_RUN' if split == 'test' and label['stratum'] == 'O' else 'PLANNED'))
    return rows


def record_inputs(data, arrays, config, record):
    dates = data['dates'].tolist()
    if dates.count(record['date']) != 1 or datetime.fromisoformat(record['date']).weekday() >= 5:
        raise ValueError('record date outside supplied weekday split')
    if (record['date'] in config['train_dates']) != (record['split'] == 'train'):
        raise ValueError('train/test split mismatch')
    ids = [r['id'] for r in config['regimes']]
    if record['regime'] not in ids:
        raise ValueError('unknown managed flow')
    r, j = ids.index(record['regime']), dates.index(record['date'])
    inc, cap = arrays['incidence'][r], float(np.asarray(arrays['capacity']).item())
    label = V3.strata(data['days'][j], inc, cap)
    if label['stratum'] != record['stratum'] or (record['split'] == 'test' and label['stratum'] != 'S'):
        raise ValueError('test O is NOT_RUN; input stratum changed')
    return j, r, inc, cap


def expected_loads(slot, modes=None, *, observed_modes=None, tau=None, beta=S.BETA):
    """Linear OD expectation. Infinite-age law is exact; finite K is empirical."""
    slot = np.asarray(slot, dtype=float)
    if modes is not None:
        mean = np.asarray(modes, dtype=float)
    elif observed_modes is not None and tau is not None and tau >= 0:
        mean = np.asarray(observed_modes, dtype=float)*np.exp(-2*tau)
    else:
        raise ValueError('endpoint posterior mean or nonnegative telemetry age required')
    if not np.isfinite(slot).all() or (slot < 0).any() or not np.isfinite(mean).all() or (np.abs(mean) > 1).any():
        raise ValueError('invalid load/mode expectation')
    return slot*(1 + beta*mean)


def path_utilizations(inc, slot, modes, capacity, managed):
    load = expected_loads(slot, modes)
    full = np.einsum('nd,aed->nae', load, inc, optimize=True)/capacity
    return np.stack([full[:, a, inc[a, :, managed] > 0].max(axis=1) for a in range(2)], axis=1)


def utilization_choices(util, theta=None):
    util = np.asarray(util, dtype=float)
    if util.ndim != 2 or util.shape[1] != 2 or not np.isfinite(util).all() or (util < 0).any():
        raise ValueError('finite nonnegative n x 2 path utilization required')
    stay, switch = util.T
    if theta is None:
        return (switch < stay).astype(np.int16), switch == stay
    if not np.isfinite(theta) or theta < 0:
        raise ValueError('invalid utilization threshold')
    active = stay > theta
    return (active & (switch < stay)).astype(np.int16), (stay == theta) | (active & (switch == stay))


def fluid_choices(costs, s_hat, horizons=H_SECONDS):
    n, _, nh = costs.shape
    plain = E.pick(costs)
    hybrid = E.pick(E.hybrid_costs(costs, [0., s_hat], horizons))
    stationary = np.full((n, nh), int(s_hat < 0), dtype=np.int16)
    return np.stack([plain[0], hybrid[0], stationary], axis=1), np.stack([
        plain[1], hybrid[1], np.full((n, nh), s_hat == 0)], axis=1)


def mean_forecast(inc, profile, cap, modes, queues):
    """Unchanged S.mean_rollout, with an exact zero-tail certificate only.

    At 900 s exp(-2t) underflows to EXACT zero in the inherited discrete mean
    path. If its inherited endpoint helper gives zero queues for both actions,
    and every later slot mean load <= capacity, all later costs are exactly
    constant. Compute that first slot with S.mean_rollout and repeat its cost.
    No tolerance, altered drift, horizon truncation without a certificate, or
    replacement native kernel. Fallback is the full unmodified helper.
    """
    steps = round(S.SLOT/S.DT)
    if np.exp(-2*S.DT*steps) == 0 and ((inc @ profile[1:].T) <= cap).all():
        endpoint = []
        for a in range(2):
            w = np.ascontiguousarray((inc[a]*profile[0])[None])
            model = T.Model(w, np.full(inc.shape[1], cap), np.ones(inc.shape[2]), S.BETA, [], [])
            endpoint.append(S.mean_endpoint(model, modes, queues, S.DT, steps)[:, 0])
        if all(not q.any() for q in endpoint):
            first = S.mean_rollout(inc, profile[:1], cap, modes, queues, hs=[steps])
            return np.repeat(first, len(H_SECONDS), axis=2)
    return S.mean_rollout(inc, profile, cap, modes, queues, hs=np.rint(H_SECONDS/S.DT).astype(int))


def decision_record(data, arrays, config, record, s_hat, *, seed, n=N, k=K):
    """Only past state simulation and operator forecasts, never future outcomes."""
    cpu, wall = time.process_time(), time.perf_counter()
    j, r, inc, cap = record_inputs(data, arrays, config, record)
    streams = seeds_for(seed, record['regime'], record['date'])
    times = {}
    fresh, stale = R.timer(times, 'warmup', lambda: S.warm_instances(
        inc, data['warm'][j], cap, n, streams['warm']))
    profile = arrays['profiles'][0]
    m0 = R.timer(times, 'M0_fresh', lambda: mean_forecast(inc, profile, cap, *fresh))
    managed = config['regimes'][r]['managed_index']
    u = [path_utilizations(inc, data['days'][j, 0], fresh[0], cap, managed)]
    old_costs, posterior_means = [], []
    for tau in S.TAU_SECONDS:
        pm, pq = R.timer(times, f'posterior_{int(tau)}', lambda tau=tau: S.forward_posterior(
            inc, data['warm'][j, -1], cap, stale[tau], tau, k, streams[f'posterior-{tau}']))
        old = R.timer(times, f'M0_stale_{int(tau)}', lambda: mean_forecast(
            inc, profile, cap, pm, pq).reshape(n, k, 2, len(H_SECONDS)).mean(axis=1))
        old_costs.append(old)
        mean = pm.reshape(n, k, -1).mean(axis=1)
        posterior_means.append(mean)
        # max(E[link load]), not E[max(link load)]. Same decision-slot matrix
        # on both sides; only telemetry age/mode information differs.
        u.append(path_utilizations(inc, data['days'][j, 0], mean, cap, managed))
    costs = [m0] + old_costs
    decisions = np.empty((n, len(PIPES), 3, len(H_SECONDS)), dtype=np.int16)
    ties = np.empty_like(decisions, dtype=bool)
    for side in range(3):
        decisions[:, :3, side], ties[:, :3, side] = fluid_choices(costs[side], s_hat)
        for p, theta in enumerate((*THETAS, None), 3):
            d, t = utilization_choices(u[side], theta)
            decisions[:, p, side] = d[:, None]
            ties[:, p, side] = t[:, None]
    raw = dict(decisions=decisions, tie_flags=ties, M0_predicted_fresh=m0,
        M0_predicted_stale=np.stack(old_costs, axis=1),
        path_utilization=np.stack(u, axis=1), posterior_mean_modes=np.stack(posterior_means, axis=1),
        fresh_modes=fresh[0], fresh_queues=fresh[1], s_hat_Mbit=np.array(s_hat),
        h_seconds=H_SECONDS, tau_seconds=np.array(S.TAU_SECONDS), pipelines=np.array(PIPES), sides=np.array(SIDES))
    meta = dict(owner='Doan Van Tai', **record, seed_base=seed, streams=streams,
        N=n, K=k, timings=times, stage='decisions-only', evaluation_called=False,
        C_ref_computed=False, CPU_s=time.process_time()-cpu, wall_s=time.perf_counter()-wall,
        peak_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
    return raw, meta


def publish(out, folder, record, raw, meta):
    stem = Path(out) / folder / f"{record['regime']}_{record['date']}"
    npz(stem.with_suffix('.npz'), raw)
    meta['npz_sha256'] = C.sha256(stem.with_suffix('.npz'))
    C.write_json(stem.with_suffix('.json'), meta)
    emit({k: meta[k] for k in ('regime', 'date', 'split', 'stage', 'CPU_s')})
    return meta


_CONTEXT = None


def _initialize(context, out, slopes=None, token=None):
    global _CONTEXT
    _CONTEXT = context, Path(out), slopes, token


def train_record(record):
    (datasets, arrays, config), out, _, _ = _CONTEXT
    data = datasets['train']
    cpu, wall = time.process_time(), time.perf_counter()
    j, _, inc, cap = record_inputs(data, arrays, config, record)
    streams = seeds_for(TRAIN_SEED, record['regime'], record['date'])
    times = {}
    fresh, _ = R.timer(times, 'warmup', lambda: S.warm_instances(inc, data['warm'][j], cap, N, streams['warm']))
    costs = R.timer(times, 'training_rate_only', lambda: S.variable(
        inc, data['days'][j], cap, *fresh, streams['rate'], hs=[round(21600/S.DT)])[0])
    rates = costs[:, :, 0]/21600
    delta = rates[:, 1]-rates[:, 0]
    meta = dict(owner='Doan Van Tai', **record, seed_base=TRAIN_SEED, streams=streams,
        N=N, stage='training-rate', test_outcomes=False, s_hat_Mbit=float(delta.mean()),
        conditional_MC_SE_Mbit=float(delta.std(ddof=1)/np.sqrt(N)), timings=times,
        CPU_s=time.process_time()-cpu, wall_s=time.perf_counter()-wall)
    return publish(out, 'training_rates', record, dict(costs=costs, rates=rates, fresh_modes=fresh[0],
                   fresh_queues=fresh[1], h_seconds=np.array([21600])), meta)


def _decision_worker(record):
    context, out, slopes, _ = _CONTEXT
    datasets, arrays, config = context
    seed = TRAIN_SEED if record['split'] == 'train' else TEST_SEED
    raw, meta = decision_record(datasets[record['split']], arrays, config, record,
                                slopes[record['regime']], seed=seed)
    return publish(out, 'step0/' + record['split'], record, raw, meta)


def run_jobs(fn, records, context, out, workers, slopes=None, token=None):
    if workers < 1:
        raise ValueError('positive workers required')
    if workers == 1:
        _initialize(context, out, slopes, token)
        return [fn(r) for r in records]
    with ProcessPoolExecutor(workers, mp_context=mp.get_context('spawn'), initializer=_initialize,
                             initargs=(context, out, slopes, token)) as pool:
        return list(pool.map(fn, records, chunksize=1))


def learn_slopes(context, out, workers):
    train_records = records_for(context[0]['train'], context[1], context[2], 'train')
    rows = run_jobs(train_record, train_records, context, out, workers)
    slopes = {r['id']: float(np.mean([x['s_hat_Mbit'] for x in rows if x['regime'] == r['id']]))
              for r in context[2]['regimes']}
    C.write_json(Path(out) / 'training_summary.json', dict(owner='Doan Van Tai', N=N,
        seed=TRAIN_SEED, s_hat_pooled_Mbit=slopes, records=rows, record_count=len(rows),
        test_outcomes=False, CPU_s_records=sum(x['CPU_s'] for x in rows)))
    return slopes


def signal_tables(out, records):
    """Explicit integer counts; fresh counted once in each X4 h table."""
    x2, x4, tie_rows, by_record = [], [], [], []
    for population in ('train_all', 'train_S', 'test_S'):
        rr = [r for r in records if r['split'] == ('test' if population == 'test_S' else 'train')
              and (population == 'train_all' or r['stratum'] == 'S')]
        groups = {}
        for record in rr:
            raw = read_npz(Path(out) / 'step0' / record['split'] / f"{record['regime']}_{record['date']}.npz")
            d, ties = raw['decisions'], raw['tie_flags']
            for p, name in enumerate(PIPES):
                for s, side in enumerate(SIDES):
                    for ih, h in enumerate(H_SECONDS):
                        key = ('tie', record['set'], name, side, int(h))
                        counts = groups.setdefault(key, [0, 0])
                        counts[0] += int(ties[:, p, s, ih].sum())
                        counts[1] += len(d)
            if record['set'] == 'X2':
                for p in range(3, len(PIPES)):
                    for side in (1, 2):
                        num = int(np.count_nonzero(d[:, p, side, 0] != d[:, p, 0, 0]))
                        for tau in (0, int(S.TAU_SECONDS[side-1])):
                            key = ('X2', PIPES[p], tau)
                            counts = groups.setdefault(key, [0, 0])
                            counts[0] += num
                            counts[1] += len(d)
                        by_record.append(dict(population=population, **record, rule=PIPES[p],
                                              side=SIDES[side], disagree=num, denominator=len(d)))
            else:
                costs = [raw['M0_predicted_fresh']] + [raw['M0_predicted_stale'][:, t] for t in range(2)]
                for ih, h in enumerate(H_SECONDS):
                    for s, side in enumerate(SIDES):
                        num = int(np.count_nonzero(d[:, 1, s, ih] != d[:, 2, s, ih]))
                        gap = costs[s][:, 1, ih]-costs[s][:, 0, ih]
                        high = int(np.count_nonzero(gap*float(raw['s_hat_Mbit'].item()) < 0))
                        for label in (side, 'all_unique_sides'):
                            key = ('X4', int(h), label)
                            counts = groups.setdefault(key, [0, 0, 0])
                            counts[0] += num
                            counts[1] += len(d)
                            counts[2] += high
                        by_record.append(dict(population=population, **record, rule='Hybrid_vs_Stationary',
                            side=side, h_s=int(h), disagree=num, fluid_prefers_higher_rate=high, denominator=len(d)))
        for key, counts in groups.items():
            row = dict(population=population, numerator=counts[0], denominator=counts[1],
                       share=counts[0]/counts[1])
            if key[0] == 'tie':
                tie_rows.append(dict(row, set=key[1], rule=key[2], side=key[3], h_s=key[4]))
            elif key[0] == 'X2':
                x2.append(dict(row, rule=key[1], tau_s=key[2]))
            else:
                x4.append(dict(row, h_s=key[1], side=key[2],
                               fluid_prefers_higher_rate=counts[2], higher_rate_share=counts[2]/counts[1]))
    return dict(X2=x2, X4=x4, ties=tie_rows, by_record=by_record)


def signal_gates(tables, population='test_S'):
    a = [r for r in tables['X2'] if r['population'] == population and r['tau_s'] == 0 and r['rule'].startswith('TH_')]
    b = [r for r in tables['X4'] if r['population'] == population and r['h_s'] <= 7200 and r['side'] == 'all_unique_sides']
    return {name: dict(verdict='SIGNAL_OK' if any(100*r['numerator'] >= r['denominator'] and r['denominator'] > 0 for r in rr)
                              else 'NOT_ENOUGH_SIGNAL', threshold=.01, counts=rr)
            for name, rr in (('X2', a), ('X4', b))}


def step0(out=OUT, workers=1):
    out = Path(out)
    T.new(out / 'step0_started.json', out / 'training_summary.json', out / 'signal.json')
    cpu, wall = time.process_time(), time.perf_counter()
    context = load_context(out)
    C.write_json(out / 'step0_started.json', dict(owner='Doan Van Tai', workers=workers,
        source_sha256=C.sha256(__file__), test_future_evaluation=False))
    slopes = learn_slopes(context, out, workers)
    # Route selection and pooled training estimates are now on disk, BEFORE
    # any test-day traffic is opened.
    context = load_context(out, include_test=True)
    records = [r for split, data in context[0].items() for r in records_for(data, context[1], context[2], split)]
    C.write_json(out / 'inputs.json', dict(owner='Doan Van Tai', records=records,
        O_test_status='NOT_RUN', input_only=True, planned_truth='S records of SIGNAL_OK sets only'))
    selected = [r for r in records if r['status'] != 'NOT_RUN']
    metas = run_jobs(_decision_worker, selected, context, out, workers, slopes)
    tables = signal_tables(out, selected)
    result = dict(owner='Doan Van Tai', stage='decisions-only', N=N, K=K,
        decisions_record_count=len(metas), records=metas, gates=signal_gates(tables),
        train_S_gates_descriptive=signal_gates(tables, 'train_S'), tables=tables,
        evaluation_called=False, C_ref_computed=False, test_outcomes_computed=False,
        training_rate_rollouts_separate=True, CPU_s_records=sum(m['CPU_s'] for m in metas),
        CPU_s_parent=time.process_time()-cpu, wall_s=time.perf_counter()-wall)
    C.write_json(out / 'signal.json', result)
    for name, rows in tables.items():
        # by_record combines X2/X4 fields; normalize the CSV schema explicitly.
        fields = sorted({k for r in rows for k in r})
        T.write_csv(out / f'step0_{name}.csv', [{k: r.get(k) for k in fields} for r in rows])
    return result


def predict(out=OUT):
    out = Path(out)
    check_sources(out)
    signal = C.read_json(out / 'signal.json')
    slopes = C.read_json(out / 'training_summary.json')['s_hat_pooled_Mbit']
    records = [r for r in signal['records'] if r['split'] == 'train' and r['stratum'] == 'S']
    predictions = []
    for regime in sorted(slopes):
        rr = [r for r in records if r['regime'] == regime]
        raws = [read_npz(out / 'step0/train' / f"{regime}_{r['date']}.npz") for r in rr]
        if not raws:
            continue
        d = np.concatenate([raw['decisions'] for raw in raws])
        u = np.concatenate([raw['path_utilization'] for raw in raws])
        null_gap = float((u[:, :, 1]-u[:, :, 0]).mean())
        for p, rule in enumerate(PIPES):
            for side, tau in enumerate(S.TAU_SECONDS, 1):
                for ih in (2, 3):
                    ns, nf = int(d[:, p, side, ih].sum()), int(d[:, p, 0, ih].sum())
                    delta = (ns-nf)/len(d)
                    pred = slopes[regime]*delta
                    predictions.append(dict(regime=regime, rule=rule, tau_s=int(tau),
                        h_s=int(H_SECONDS[ih]), train_S_days=len(rr), denominator=len(d),
                        switch_stale=ns, switch_fresh=nf, delta_F_hat=delta,
                        s_hat_pooled_Mbit=slopes[regime], slope_pred_Mbit=pred,
                        predicted_G_S_sign=int(np.sign(pred)),
                        null_mean_path_max_util_difference=null_gap,
                        null_slope=null_gap*delta, null_sign=int(np.sign(null_gap*delta))))
    result = dict(owner='Doan Van Tai', training_only=True, G_S='L_stale-L_fresh',
        test_outcomes_read=False, rows=predictions, gates=signal['gates'],
        seed_train=TRAIN_SEED, training_summary_sha256=C.sha256(out / 'training_summary.json'),
        caveat='zero is an abstention/no predicted sign; pooled rate includes overload train days, same V7-3 convention')
    C.write_json(out / 'predictions.json', result)
    T.write_csv(out / 'predictions.csv', predictions)
    return result


def pilot_work_proxy(data, arrays, config, record):
    j, _, inc, cap = record_inputs(data, arrays, config, record)
    upper = (1+S.BETA)*np.einsum('sd,aed->sae', data['days'][j], inc, optimize=True)
    active = (upper > cap).any(axis=(0, 1))
    active |= ((1+S.BETA)*(data['warm'][j] @ inc[0].T) > cap).any(axis=0)
    relevant = (inc[:, active] != 0).any(axis=(0, 1))
    sparse = int(np.count_nonzero(inc[:, active][:, :, relevant]))
    return int(round(21600/S.DT)*(N*(R_DEC+R_EVAL)*(sparse + relevant.sum() + 2*active.sum())))


def paired_metrics(raw, reference, evaluation, cap):
    """Pure gather, same G_S sign and reference convention as letter Sec II."""
    values = evaluation.mean(axis=1)
    ref, rt = E.pick(reference.mean(axis=1))
    cref = E.costs_for_decisions(values, ref)
    costs = E.costs_for_decisions(values, raw['decisions'])
    regret = costs-cref[:, None, None, :]
    return dict(V=values, reference_decision=ref, reference_tie_flags=rt, C_ref=cref,
        costs=costs, regret=regret, G_S=costs[:, :, 1:]-costs[:, :, :1],
        paired_evaluation=evaluation, reference_decision_rollouts=reference,
        evaluable=cref.mean(axis=0)/raw['h_seconds'] >= cap*.001,
        paired_Hybrid_minus_Stationary=regret[:, 1]-regret[:, 2])


def outcome_record(context, record, slopes, *, stage, verified=None, out=OUT):
    if stage not in ('pilot', 'truth'):
        raise ValueError('explicit pilot or truth stage required')
    if stage == 'truth':
        # Verify all locked inputs here too, before data access or engine calls.
        digest = verify_lock(out).digest
        if not isinstance(verified, C.VerifiedLock) or verified.digest != digest:
            raise ValueError('verified X-GEANT truth lock required')
        gates = C.read_json(Path(out) / 'signal.json')['gates']
        if gates[record['set']]['verdict'] != 'SIGNAL_OK':
            raise ValueError('NOT_ENOUGH_SIGNAL set cannot enter truth')
    datasets, arrays, config = context
    data = datasets[record['split']]
    seed = PILOT_SEED if stage == 'pilot' else TEST_SEED
    cpu, wall = time.process_time(), time.perf_counter()
    raw, meta = decision_record(data, arrays, config, record, slopes[record['regime']], seed=seed)
    if stage == 'truth':
        old = read_npz(Path(out) / 'step0/test' / f"{record['regime']}_{record['date']}.npz")
        for key in ('decisions', 'tie_flags', 'fresh_modes', 'fresh_queues', 'M0_predicted_fresh', 'M0_predicted_stale'):
            if not np.array_equal(old[key], raw[key]):
                raise ValueError('truth differs from step0: ' + key)
    j, _, inc, cap = record_inputs(data, arrays, config, record)
    def rollout(count, purpose):
        modes, queues = (np.repeat(raw[k], count, axis=0) for k in ('fresh_modes', 'fresh_queues'))
        value = S.variable(inc, data['days'][j], cap, modes, queues, meta['streams'][purpose],
                           hs=np.rint(H_SECONDS/S.DT).astype(int))[0]
        return value.reshape(N, count, 2, len(H_SECONDS))
    reference = R.timer(meta['timings'], 'reference_decision', lambda: rollout(R_DEC, 'reference-decision'))
    evaluation = R.timer(meta['timings'], 'paired_evaluation', lambda: rollout(R_EVAL, 'evaluation'))
    raw.update(paired_metrics(raw, reference, evaluation, cap))
    meta.update(stage=stage, evaluation_called=True, C_ref_computed=True,
        R_dec=R_DEC, R_eval=R_EVAL, pilot=stage == 'pilot',
        CPU_s=time.process_time()-cpu, wall_s=time.perf_counter()-wall,
        peak_RSS_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        G_S='L_stale-L_fresh', units=dict(cost='Mbit*s', backlog='Mbit', time='s'),
        axes=dict(decisions=['instance', 'rule', 'unique_side', 'h'], V=['instance', 'action', 'h']))
    return raw, meta


def pilot(out=OUT):
    out = Path(out)
    T.new(out / 'pilot/selection.json', out / 'pilot/summary.json')
    context = load_context(out, include_test=True)
    data, arrays, config = context[0]['test'], context[1], context[2]
    signal = C.read_json(out / 'signal.json')
    # A timing pilot is permitted even for a failed screen; no truth is enabled.
    records = [r for r in C.read_json(out / 'inputs.json')['records'] if r['split'] == 'test' and r['stratum'] == 'S']
    ranks = sorted([(pilot_work_proxy(data, arrays, config, r), r) for r in records],
                   key=lambda x: (-x[0], x[1]['regime'], x[1]['date']))
    if not ranks:
        raise ValueError('no test-S pilot input')
    work, record = ranks[0]
    C.write_json(out / 'pilot/selection.json', dict(owner='Doan Van Tai', record=record,
        seed=PILOT_SEED, work_proxy=work, rule=check_sources(out)['pilot'],
        ranking=[dict(work_proxy=w, **r) for w, r in ranks],
        no_outcomes_used_in_selection=True))
    slopes = C.read_json(out / 'training_summary.json')['s_hat_pooled_Mbit']
    cpu, wall = time.process_time(), time.perf_counter()
    raw, meta = outcome_record(context, record, slopes, stage='pilot', out=out)
    publish(out, 'pilot/records', record, raw, meta)
    eligible = [r for r in records if signal['gates'][r['set']]['verdict'] == 'SIGNAL_OK']
    projected = meta['CPU_s']*len(eligible)
    result = dict(owner='Doan Van Tai', stage='pilot', record=meta, seed=PILOT_SEED,
        N=N, K=K, R_dec=R_DEC, R_eval=R_EVAL, actual_truth_eligible_records=len(eligible),
        all_S_records=len(records), projected_CPU_s=projected, projected_CPU_hours=projected/3600,
        all_sets_projected_CPU_hours=meta['CPU_s']*len(records)/3600,
        ideal_wall_hours_30_workers=projected/(30*3600), target='n2-highcpu-32', workers=30,
        CPU_s_command=time.process_time()-cpu, wall_s=time.perf_counter()-wall,
        hardware=dict(platform=platform.platform(), processor=platform.processor(),
                      python=platform.python_version(), numpy=np.__version__),
        limitations=['One full-size local pilot selected by an input work proxy, not a measured worst-case guarantee.',
                     'Linear record-count extrapolation; ideal worker division, no cloud measurement or confidence interval.',
                     'Pilot-seed outcomes are exposure; no test-seed truth or hypothesis score.'])
    C.write_json(out / 'pilot/summary.json', result)
    return result


def lock_paths(out):
    out = Path(out)
    paths = dependencies()
    for name in ('protocol.json', 'configuration.json', 'configuration.npz', 'regimes.md',
                 'train_utilizations.csv', 'candidate_ranking_inputs.csv', 'step0_started.json',
                 'training_summary.json', 'inputs.json', 'signal.json', 'predictions.json',
                 'predictions.csv', 'pilot/selection.json', 'pilot/summary.json'):
        paths['output:' + name] = out / name
    for folder in ('training_rates', 'step0/train', 'step0/test', 'pilot/records'):
        for p in sorted((out / folder).glob('*')):
            if p.suffix in ('.npz', '.json'):
                paths['output:' + str(p.relative_to(out))] = p
    return paths


def create_lock(out=OUT):
    out = Path(out)
    check_sources(out)
    T.new(out / 'lock.json')
    signal = C.read_json(out / 'signal.json')
    inputs = C.read_json(out / 'inputs.json')['records']
    expected = len([r for r in inputs if r['status'] != 'NOT_RUN'])
    if signal['decisions_record_count'] != expected:
        raise ValueError('incomplete decision screen')
    expected_rates = 6*26
    if C.read_json(out / 'training_summary.json')['record_count'] != expected_rates:
        raise ValueError('incomplete training estimates')
    for folder, n in (('training_rates', expected_rates), ('step0/train', 6*26),
                      ('step0/test', expected-6*26), ('pilot/records', 1)):
        for ext in ('.json', '.npz'):
            if len(list((out / folder).glob('*' + ext))) != n:
                raise ValueError('incomplete raw preparation: ' + folder)
    value = dict(owner='Doan Van Tai', schema='x-geant-lock-v1',
        sha256={k: C.sha256(p) for k, p in sorted(lock_paths(out).items())},
        gates=signal['gates'], committed=False,
        note='Uncommitted by explicit user instruction. Claude reviews/commits/transfers before truth; content verification is mandatory.')
    C.write_json(out / 'lock.json', value)
    return value


def verify_lock(out=OUT):
    out = Path(out)
    locked = C.read_json(out / 'lock.json')
    now = {k: C.sha256(p) for k, p in sorted(lock_paths(out).items())}
    if locked.get('schema') != 'x-geant-lock-v1' or locked['sha256'] != now:
        raise ValueError('X-GEANT lock mismatch')
    return C.VerifiedLock(str((out / 'lock.json').resolve()), C.sha256(out / 'lock.json'))


def _truth_worker(record):
    context, out, slopes, token = _CONTEXT
    raw, meta = outcome_record(context, record, slopes, stage='truth', verified=token, out=out)
    return publish(out, 'truth/records', record, raw, meta)


def truth(out=OUT, workers=30):
    # No CLI preparation command calls this function.
    token = verify_lock(out)
    out = Path(out)
    signal = C.read_json(out / 'signal.json')
    records = [r for r in C.read_json(out / 'inputs.json')['records']
               if r['split'] == 'test' and r['stratum'] == 'S' and signal['gates'][r['set']]['verdict'] == 'SIGNAL_OK']
    if not records:
        raise ValueError('NOT_ENOUGH_SIGNAL: no truth records')
    T.new(out / 'truth')
    C.write_json(out / 'truth/started.json', dict(owner='Doan Van Tai', seed=TEST_SEED,
        workers=workers, records=len(records), lock_sha256=token.digest, one_shot=True))
    start = time.perf_counter()
    result = dict(owner='Doan Van Tai', status='INCOMPLETE', records=[], lock_sha256=token.digest, scored=False)
    try:
        context = load_context(out, include_test=True)
        slopes = C.read_json(out / 'training_summary.json')['s_hat_pooled_Mbit']
        result['records'] = run_jobs(_truth_worker, records, context, out, workers, slopes, token)
        result['status'] = 'COMPLETE'
    except BaseException:
        result['error'] = traceback.format_exc()
        raise
    finally:
        # A failed pool still leaves exclusive per-record checkpoints. No retry.
        receipts = [C.read_json(p) for p in sorted((out / 'truth/records').glob('*.json'))]
        result.update(records=receipts, wall_s=time.perf_counter()-start,
                      CPU_s_records=sum(r['CPU_s'] for r in receipts),
                      peak_RSS_MiB=max([r['peak_RSS_MiB'] for r in receipts], default=None))
        C.write_json(out / 'truth/receipt.json', result)
    return result


def paired_stats(x):
    x = np.asarray(x, dtype=float)
    return dict(mean=float(x.mean()), se=float(x.std(ddof=1)/np.sqrt(len(x))))


def score(out=OUT):
    """Descriptive letter metrics only; no new success criteria invented."""
    out = Path(out)
    verify_lock(out)
    receipt = C.read_json(out / 'truth/receipt.json')
    if receipt['status'] != 'COMPLETE':
        raise ValueError('cannot score INCOMPLETE truth')
    C.write_json(out / 'truth/raw_manifest.json', dict(owner='Doan Van Tai',
        sha256={str(p.relative_to(out)): C.sha256(p) for p in sorted((out / 'truth/records').glob('*')) if p.is_file()}))
    rows = []
    cap = C.read_json(out / 'configuration.json')['capacity_Mbps']
    for meta in receipt['records']:
        path = out / 'truth/records' / f"{meta['regime']}_{meta['date']}.npz"
        if C.sha256(path) != meta['npz_sha256']:
            raise ValueError('raw checksum mismatch')
        raw = read_npz(path)
        for p, name in enumerate(PIPES):
            for t, tau in enumerate(S.TAU_SECONDS):
                for ih, h in enumerate(H_SECONDS):
                    cref = float(raw['C_ref'][:, ih].mean())
                    lf = float(raw['costs'][:, p, 0, ih].mean())
                    ls = float(raw['costs'][:, p, t+1, ih].mean())
                    gs = paired_stats(raw['G_S'][:, p, t, ih])
                    pair = paired_stats(raw['paired_Hybrid_minus_Stationary'][:, t+1, ih])
                    rf, rs = lf-cref, ls-cref
                    rows.append(dict(regime=meta['regime'], set=meta['set'], date=meta['date'],
                        rule=name, tau_s=int(tau), h_s=int(h), C_ref_Mbit_s=cref,
                        L_fresh_Mbit_s=lf, L_stale_Mbit_s=ls,
                        regret_fresh_Mbit_s=rf, regret_stale_Mbit_s=rs,
                        regret_fresh_pct=None if cref <= 0 else 100*rf/cref,
                        regret_stale_pct=None if cref <= 0 else 100*rs/cref,
                        both_side_regret_pct=None if cref <= 0 else 100*max(rf, rs)/cref,
                        G_S_Mbit_s=gs['mean'], G_S_SE_Mbit_s=gs['se'],
                        G_S_pct=None if cref <= 0 else 100*gs['mean']/cref,
                        G_S_over_h_Mbit=gs['mean']/h, G_S_service_ms=1000*gs['mean']/h/cap,
                        regret_fresh_service_ms=1000*rf/h/cap, regret_stale_service_ms=1000*rs/h/cap,
                        evaluable=bool(raw['evaluable'][ih]),
                        tie_share_fresh=float(raw['tie_flags'][:, p, 0, ih].mean()),
                        tie_share_stale=float(raw['tie_flags'][:, p, t+1, ih].mean()),
                        Hybrid_minus_Stationary_stale_Mbit_s=pair['mean'],
                        Hybrid_minus_Stationary_stale_SE_Mbit_s=pair['se'],
                        Hybrid_minus_Stationary_fresh_Mbit_s=float(raw['paired_Hybrid_minus_Stationary'][:, 0, ih].mean())))
    T.write_csv(out / 'score.csv', rows)
    C.write_json(out / 'score.json', dict(owner='Doan Van Tai', rows=rows,
        sign='G_S=L_stale-L_fresh; negative=fresh hurts', independent_rescore='PENDING',
        counts_are_not_independent_trials=True))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('configure', 'step0', 'pilot', 'predict', 'lock', 'verify-lock', 'truth', 'score'))
    parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args(argv)
    commands = dict(configure=configure, pilot=pilot, predict=predict, lock=create_lock,
                    **{'verify-lock': verify_lock}, score=score)
    if args.command in ('step0', 'truth'):
        result = dict(step0=step0, truth=truth)[args.command](args.out, args.workers)
    else:
        result = commands[args.command](args.out)
    if isinstance(result, C.VerifiedLock):
        emit(dict(verified=True, lock_sha256=result.digest))
    elif isinstance(result, dict):
        emit({k: result[k] for k in ('stage', 'gates', 'projected_CPU_hours', 'status') if k in result})


if __name__ == '__main__':
    main()
