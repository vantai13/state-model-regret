"""Doan Van Tai — LETTER E6 raw end-to-end costs, without card scoring.

Replay only E4 instances, fluid twins and stale posteriors. True per-action V
and M1_new decisions are read from E4/E4b; E5 records are read, never rerun.
Run `pilot` first, then `run --workers 8` if its CPU projection permits it.
The two pilot chunks are reused by the full run, without recomputation.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse
import json
from multiprocessing import get_context
from pathlib import Path
import resource
import subprocess
import time

import numpy as np

from experiments.ext_validity import ev_te as T
from experiments.letter import e4_geant as E
from experiments.letter import e5_replay as R

OUT = T.ROOT / 'results/letter/e6'
BRIEF = T.ROOT / 'notes/ops/codex/LETTER_E6_brief.md'
CARD = OUT / 'CARD_E6.md'
SEED_DIRS = {3000001: T.ROOT / 'results/letter/e4',
             5000001: T.ROOT / 'results/letter/e4b'}
LS, L_INDICES = (30, 100, 300), (3, 4, 5)
LEVELS = E.HYBRID_LEVELS  # Required six controls, plus Hybrid-ii.
CPU_LIMIT = 2 * 3600.


def sources():
    paths = [Path(__file__).resolve(), BRIEF, CARD, Path(E.__file__),
             T.ROOT / 'experiments/letter/e4_rhat.py', Path(T.__file__),
             Path(R.__file__), T.ROOT / 'experiments/explore_ctmc/env.sh']
    return {str(p.relative_to(T.ROOT)): T.sha256(p) for p in paths}


def check_authority():
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=T.ROOT, text=True).strip()
    if branch != 'letter':
        raise ValueError('E6 requires branch letter')
    for path in (BRIEF, CARD):
        saved = subprocess.check_output(['git', 'show', f'HEAD:{path.relative_to(T.ROOT)}'], cwd=T.ROOT)
        if saved != path.read_bytes():
            raise ValueError(f'committed instructions differ: {path}')


def training(spec):
    tr = T.read_json(E.EV / 'train' / f"{spec['id']}.json")
    if tr['excluded'] or tr['seed'] != E.TRAIN_SEED:
        raise ValueError('invalid E4 training provenance')
    return tr


def load_records(spec, tr):
    path = R.OUT / 'raw' / f"{spec['id']}.npz"
    meta = T.read_json(path.with_suffix('.json'))
    if (meta['regime'] != spec['id'] or meta['seed'] != R.SEED or meta['R'] != R.R
            or meta['L_Tint'] != list(R.LS) or meta['T_int'] != tr['T_int'] or meta['dt'] != tr['dt']
            or meta['training_r_a'] != [a['mean'] for a in tr['r_a']]):
        raise ValueError('E5 record provenance differs from E4 training')
    with np.load(path, allow_pickle=False) as data:
        means, lengths, reps = data['means'], data['L_Tint'], data['reps']
    actions = 2 ** len(spec['managed'])
    if (means.shape != (R.R, len(R.LS), actions) or not np.isfinite(means).all()
            or np.any(means < 0) or not np.array_equal(lengths, R.LS)
            or not np.array_equal(reps, np.arange(R.R))):
        raise ValueError('invalid E5 records/axes')
    return means[:, L_INDICES, :], dict(npz_sha256=T.sha256(path),
                                       json_sha256=T.sha256(path.with_suffix('.json')))


def load_saved_chunk(spec, tr, seed, chunk, size=E.CHUNK_SIZE):
    if seed not in SEED_DIRS or chunk not in range(E.N_CHUNKS) or not 1 <= size <= E.CHUNK_SIZE:
        raise ValueError('invalid E4 seed, chunk or prefix size')
    path = SEED_DIRS[seed] / 'raw' / f"{spec['id']}_chunk{chunk:02d}.npz"
    meta = T.read_json(path.with_suffix('.json'))
    if (meta['regime'] != spec['id'] or meta['seed'] != seed or meta['chunk'] != chunk
            or meta['pilot'] is not False or meta['N'] != E.CHUNK_SIZE or meta['K'] != E.K
            or meta['R_eval'] != E.R_EVAL or meta['R_dec'] != E.R_DEC
            or meta['T_int'] != tr['T_int'] or meta['dt'] != tr['dt']
            or meta['npz_sha256'] != T.sha256(path)):
        raise ValueError(f'E4 chunk provenance/hash mismatch: {path}')
    with np.load(path, allow_pickle=False) as data:
        raw = {key: data[key] for key in data.files}
    names = E.pipeline_names(meta['onset_theta'])
    taus, hs = E.e4_grid(tr['T_int'], tr['dt'])
    if (raw['pipelines'].tolist() != names or raw['sides'].tolist() != list(E.SIDES)
            or not np.array_equal(raw['h'], np.array(hs) * tr['dt'])
            or not np.array_equal(raw['tau'], np.array(taus) * tr['dt'])
            or not np.array_equal(raw['h_mult'], E.HS)
            or not np.array_equal(raw['tau_mult'], E.TAUS)
            or not np.array_equal(raw['instance_id'], chunk * E.CHUNK_SIZE + np.arange(E.CHUNK_SIZE))):
        raise ValueError('saved E4 grid/schema mismatch')
    v, d = raw['V'], raw['decisions']
    if (v.shape != (E.CHUNK_SIZE, 2 ** len(spec['managed']), len(E.HS))
            or not np.isfinite(v).all() or np.any(v < 0)
            or d.shape != (E.CHUNK_SIZE, len(names), 2, len(E.TAUS), len(E.HS))
            or not np.issubdtype(d.dtype, np.integer)
            or np.any(d[:, :, 0] < 0) or np.any(d[:, :-1, 1] < 0)
            or np.any(d >= v.shape[1]) or not np.all(d[:, -1, 1] == -1)):
        raise ValueError('invalid saved E4 true costs or decisions')
    if not np.all(d[:, :, 0] == d[:, :, 0, :1]):
        raise ValueError('saved fresh decisions depend on tau')
    available = np.ones((len(names), 2), dtype=bool)
    available[-1, 1] = False
    if not np.array_equal(raw['available'], available):
        raise ValueError('invalid saved E4 availability')
    for key in ('V', 'decisions', 'tie_flags', 'instance_id'):
        raw[key] = raw[key][:size]
    return raw, meta


def regenerate_twins(spec, tr, seed, chunk, size=E.CHUNK_SIZE):
    """Same per-instance native calls, streams and reduction order as E4.

    T.posterior internally evolves Stay to reconstruct information states; no
    action-evaluation futures or M1_new decision streams are evaluated here.
    Output axes: instance, side, tau, action, h.
    """
    model = T.make_model(spec)
    ti, dt = tr['T_int'], tr['dt']
    taus, hs = E.e4_grid(ti, dt)
    fresh, all_stale = T.instances(model, ti, dt, size,
                                  E.stream_seed(seed, spec['id'], chunk, 'instances'))
    stale = [all_stale[t] for t in E.TAU_INDEX]
    predicted = np.empty((size, 2, len(E.TAUS), len(model.weights), len(hs)))
    for i in range(size):
        state = tuple(x[i:i+1] for x in fresh)
        root = E.stream_seed(seed, spec['id'], chunk, f'instance={i}')
        predicted[i, 0] = T.twin_costs(model, *state, dt, hs)[0]
        for t, (old_state, age) in enumerate(zip(stale, taus)):
            sm, sq = (x[i:i+1] for x in old_state)
            pm, pq = T.posterior(model, sm, sq, dt, age, E.K, T.seed_for(root, 'posterior', t))
            predicted[i, 1, t] = T.twin_costs(model, pm, pq, dt, hs).reshape(
                1, E.K, len(model.weights), len(hs)).mean(axis=1)[0]
    if not np.isfinite(predicted).all():
        raise ValueError('nonfinite regenerated twins')
    return predicted


def hybrid_decisions(predicted, rates, h):
    """Use E4's centered correction and exact, lowest-index tie convention."""
    a = np.asarray(predicted)
    flat = a.reshape(-1, a.shape[-2], a.shape[-1])
    decision, _ = E.pick(E.hybrid_costs(flat, rates, h))
    return decision.reshape(a.shape[:-2] + (a.shape[-1],))


def validate(predicted, raw, levels):
    names = raw['pipelines'].tolist()
    result = {}
    for label in LEVELS:
        got = hybrid_decisions(predicted, levels[label], raw['h'])
        expected = raw['decisions'][:, names.index('Hybrid-' + label)]
        different = got != expected
        result[label] = dict(compared=int(different.size), mismatches=int(different.sum()),
                             by_side={s: int(different[:, i].sum()) for i, s in enumerate(E.SIDES)})
    return result


def record_cost_sums(predicted, values, rates, h):
    """Sum chosen saved costs over this chunk; retain all 200 x 3 records.

    Broadcasted objective is exactly E.hybrid_costs, including subtraction of
    the common rate before addition, so large common offsets preserve ties.
    """
    rates, h = np.asarray(rates), np.asarray(h)
    if (rates.ndim != 3 or rates.shape[-1] != values.shape[1]
            or not np.isfinite(rates).all() or np.any(rates < 0)
            or predicted.shape != (len(values), 2, len(E.TAUS), values.shape[1], len(h))):
        raise ValueError('invalid record rates or cost axes')
    offset = (rates - rates[:, :, :1])[:, :, None, None, None, :, None] * h
    objectives = predicted[None, None] + offset
    # rep, L, instance, side, tau, h -> instance first for E4's saved-V gather.
    d = objectives.argmin(axis=-2).astype(np.int16).transpose(2, 0, 1, 3, 4, 5)
    return E.costs_for_decisions(values, d).sum(axis=0)


def combine_validation(rows):
    result = {label: dict(compared=0, mismatches=0, by_side={s: 0 for s in E.SIDES}) for label in LEVELS}
    for row in rows:
        for label in LEVELS:
            for key in ('compared', 'mismatches'):
                result[label][key] += row[label][key]
            for side in E.SIDES:
                result[label]['by_side'][side] += row[label]['by_side'][side]
    return result


def compute_saved_chunk(task):
    spec, seed, chunk = task
    cpu, wall = time.process_time(), time.perf_counter()
    tr = training(spec)
    raw, old_meta = load_saved_chunk(spec, tr, seed, chunk)
    rates, record_hashes = load_records(spec, tr)
    levels, _ = E.rate_levels(T.make_model(spec), tr)
    start = time.process_time()
    predicted = regenerate_twins(spec, tr, seed, chunk)
    regenerate_cpu = time.process_time() - start
    start = time.process_time()
    counts = validate(predicted, raw, levels)
    validation_cpu = time.process_time() - start
    meta = dict(seed=seed, regime=spec['id'], chunk=chunk, N=len(raw['V']),
                validation=counts, regeneration_CPU=regenerate_cpu, validation_CPU=validation_cpu,
                input_sha256=dict(E4_npz=old_meta['npz_sha256'],
                    E4_json=T.sha256(SEED_DIRS[seed] / 'raw' / f"{spec['id']}_chunk{chunk:02d}.json"),
                    training=T.sha256(E.EV / 'train' / f"{spec['id']}.json"), E5=record_hashes),
                historical_E4_CPU=old_meta['CPU'])
    arrays = None
    if not any(c['mismatches'] for c in counts.values()):
        names = raw['pipelines'].tolist()
        ref_values = E.costs_for_decisions(raw['V'], raw['decisions'][:, names.index('M1_new'), 0, 0])
        arrays = dict(hybrid_cost_sum=record_cost_sums(predicted, raw['V'], rates, raw['h']),
                      V=raw['V'], ref_values=ref_values, instance_id=raw['instance_id'],
                      **{k: raw[k] for k in ('h', 'tau', 'h_mult', 'tau_mult')})
    meta.update(CPU=time.process_time() - cpu, wall=time.perf_counter() - wall)
    return arrays, meta


def finalize_regime(pieces, rates):
    pieces = sorted(pieces, key=lambda x: int(x['instance_id'][0]))
    ids = np.concatenate([p['instance_id'] for p in pieces])
    if len(pieces) != E.N_CHUNKS or not np.array_equal(ids, np.arange(E.N)):
        raise ValueError('E6 requires all ten chunks / all 500 instances')
    axes = {k: pieces[0][k] for k in ('h', 'tau', 'h_mult', 'tau_mult')}
    if any(not np.array_equal(p[k], axes[k]) for p in pieces for k in axes):
        raise ValueError('inconsistent E6 chunk axes')
    # Match cells.csv: gather saved M1_new choices first, then mean over N.
    ref = np.concatenate([p['ref_values'] for p in pieces]).mean(axis=0)
    if not np.isfinite(ref).all() or np.any(ref <= 0):
        raise ValueError('C_ref must be finite and positive; no cell exclusions')
    losses = np.stack([p['hybrid_cost_sum'] for p in pieces]).sum(axis=0) / E.N
    per_action = np.concatenate([p['V'] for p in pieces]).mean(axis=0)
    static_actions = rates.argmin(axis=-1)  # Exact ties, including both zero: action 0.
    static = per_action[static_actions[..., None], np.arange(per_action.shape[-1])]
    return dict(regret_hybrid=100 * (losses - ref) / ref,
                regret_static=100 * (static - ref) / ref,
                cost_hybrid=losses, cost_static=static, C_ref=ref,
                record_rates=rates, static_action=static_actions.astype(np.int16),
                reps=np.arange(R.R), L_Tint=np.array(LS), L_indices=np.array(L_INDICES),
                sides=np.array(E.SIDES), instance_id=ids, **axes)


def historical_costs(specs):
    return {(seed, s['id'], c): T.read_json(out / 'raw' / f"{s['id']}_chunk{c:02d}.json")['CPU']
            for seed, out in SEED_DIRS.items() for s in specs for c in range(E.N_CHUNKS)}


def pilot_selection(specs, old):
    ranked = sorted(specs, key=lambda s: sum(old[3000001, s['id'], c] for c in range(E.N_CHUNKS)))
    return [(ranked[0], 3000001, 0), (ranked[-1], 3000001, 0)]


def pilot_projection(metadata, historical):
    ratios = [m['CPU'] / m['historical_E4_CPU'] for m in metadata]
    base = sum(historical.values())
    # Budget gate uses the larger of the two observed multipliers. This is a
    # historical-work calibration, not a CI or a guaranteed runtime upper bound.
    return dict(chunks=2 * 17 * E.N_CHUNKS, historical_E4_E4b_CPU=base,
                pilot_E6_to_E4_CPU_ratios=ratios,
                total_CPU_seconds=base * max(ratios), total_CPU_hours=base * max(ratios) / 3600,
                observed_ratio_range_CPU_seconds=[base * min(ratios), base * max(ratios)],
                ideal_8_worker_wall_seconds=base * max(ratios) / 8,
                CPU_limit_seconds=CPU_LIMIT, allowed=base * max(ratios) <= CPU_LIMIT,
                method='sum of all 340 historical E4/E4b chunk CPUs times max observed E6/E4 pilot multiplier; not a CI/guarantee')


def child_cpu():
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def run(command, workers, out=OUT):
    if workers < 1 or workers > 8 or (command == 'run' and workers != 8):
        raise ValueError('full E6 uses exactly 8 local workers; pilot uses 1..8')
    check_authority()
    source_hashes = sources()
    specs = E.selected_specs()
    old = historical_costs(specs)
    pilot_tasks = pilot_selection(specs, old)
    target = out / 'pilot' if command == 'pilot' else out
    T.new(target / 'run_start.json', target / 'run_summary.json', target / 'validation.json', target / 'run.log')
    reused, pilot_summary = [], None
    if command == 'run':
        pilot_summary = T.read_json(out / 'pilot/run_summary.json')
        pilot_validation = T.read_json(out / 'pilot/validation.json')
        if (not pilot_summary['complete'] or not pilot_summary['projection']['allowed']
                or pilot_summary['source_sha256'] != source_hashes or not pilot_validation['passed']):
            raise ValueError('pilot missing, failed, over CPU budget, or source changed')
        for spec, seed, chunk in pilot_tasks:
            path = out / 'pilot/raw' / f"{seed}_{spec['id']}_chunk{chunk:02d}.npz"
            meta = T.read_json(path.with_suffix('.json'))
            if T.sha256(path) != meta['npz_sha256']:
                raise ValueError('pilot chunk hash mismatch')
            tr = training(spec)
            _, saved_meta = load_saved_chunk(spec, tr, seed, chunk)
            _, e5_hashes = load_records(spec, tr)
            if (meta['input_sha256']['E4_npz'] != saved_meta['npz_sha256']
                    or meta['input_sha256']['E4_json'] != T.sha256(SEED_DIRS[seed] / 'raw' / f"{spec['id']}_chunk{chunk:02d}.json")
                    or meta['input_sha256']['training'] != T.sha256(E.EV / 'train' / f"{spec['id']}.json")
                    or meta['input_sha256']['E5'] != e5_hashes):
                raise ValueError('pilot inputs changed')
            with np.load(path, allow_pickle=False) as data:
                reused.append(({k: data[k] for k in data.files}, meta))
        for s in specs:
            for seed in SEED_DIRS:
                path = out / 'raw' / f"{seed}_{s['id']}.npz"
                T.new(path, path.with_suffix('.json'))
    tasks = pilot_tasks if command == 'pilot' else [
        (s, seed, c) for s in specs for seed in SEED_DIRS for c in range(E.N_CHUNKS)
        if (seed, s['id'], c) not in {(m['seed'], m['regime'], m['chunk']) for _, m in reused}]
    tasks.sort(key=lambda t: -old[t[1], t[0]['id'], t[2]])
    E.write_json(target / 'run_start.json', dict(command=command, workers=workers,
        source_sha256=source_hashes, seed_dirs={str(k): str(v.relative_to(T.ROOT)) for k, v in SEED_DIRS.items()},
        E5_seed=R.SEED, L_Tint=list(LS), records=R.R, new_chunks=len(tasks), reused_pilot_chunks=len(reused),
        pilot_selection=[dict(seed=t[1], regime=t[0]['id'], chunk=t[2]) for t in pilot_tasks],
        no_scoring=True, no_new_true_costs=True))
    cpu0, children0, wall0 = time.process_time(), child_cpu(), time.perf_counter()
    results, failure = list(reused), None
    with (target / 'run.log').open('x') as log:
        def emit(event):
            line = json.dumps(event, sort_keys=True)
            print(line, flush=True)
            log.write(line + '\n')
            log.flush()
        emit(dict(event='start', command=command, workers=workers, chunks=len(tasks), reused=len(reused)))
        T.native()  # Build once locally before spawning, if not already cached in /tmp.
        with ProcessPoolExecutor(max_workers=workers, mp_context=get_context('spawn')) as pool:
            futures = {pool.submit(compute_saved_chunk, t): t for t in tasks}
            for future in as_completed(futures):
                task = futures[future]
                try:
                    arrays, meta = future.result()
                except Exception as error:
                    failure = dict(kind=type(error).__name__, message=str(error),
                                   seed=task[1], regime=task[0]['id'], chunk=task[2])
                    emit(dict(event='execution_failure', **failure))
                    break
                results.append((arrays, meta))
                mismatches = sum(x['mismatches'] for x in meta['validation'].values())
                emit(dict(event='chunk', seed=meta['seed'], regime=meta['regime'], chunk=meta['chunk'],
                          CPU=meta['CPU'], regeneration_CPU=meta['regeneration_CPU'], mismatches=mismatches,
                          completed=len(results)))
                if mismatches:
                    failure = dict(kind='VALIDATION_MISMATCH', seed=meta['seed'], regime=meta['regime'], chunk=meta['chunk'])
                    break
            if failure:
                for f in futures:
                    f.cancel()
        metadata = sorted([m for _, m in results], key=lambda m: (m['seed'], m['regime'], m['chunk']))
        counts = combine_validation([m['validation'] for m in metadata])
        complete = failure is None and len(results) == (2 if command == 'pilot' else 340)
        passed = complete and not any(c['mismatches'] for c in counts.values())
        validation = dict(passed=passed, complete=complete, chunks=len(results),
            compared=sum(c['compared'] for c in counts.values()),
            mismatches=sum(c['mismatches'] for c in counts.values()), levels=counts,
            regeneration_CPU=sum(m['regeneration_CPU'] for m in metadata),
            equality_check_CPU=sum(m['validation_CPU'] for m in metadata),
            task_CPU=sum(m['CPU'] for m in metadata), failure=failure, chunks_detail=metadata)
        E.write_json(target / 'validation.json', validation)
        outputs = []
        if passed:
            if command == 'pilot':
                for arrays, meta in results:
                    path = target / 'raw' / f"{meta['seed']}_{meta['regime']}_chunk{meta['chunk']:02d}.npz"
                    E.write_npz(path, arrays)
                    E.write_json(path.with_suffix('.json'), dict(meta, npz_sha256=T.sha256(path)))
                    outputs.append(str(path.relative_to(T.ROOT)))
            else:
                for spec in specs:
                    rates, _ = load_records(spec, training(spec))
                    for seed in SEED_DIRS:
                        pieces = [(a, m) for a, m in results if m['regime'] == spec['id'] and m['seed'] == seed]
                        arrays = finalize_regime([a for a, _ in pieces], rates)
                        path = out / 'raw' / f"{seed}_{spec['id']}.npz"
                        E.write_npz(path, arrays)
                        meta = dict(seed=seed, regime=spec['id'], N=E.N, records=R.R, L_Tint=list(LS),
                            CPU=sum(m['CPU'] for _, m in pieces),
                            validation=combine_validation([m['validation'] for _, m in pieces]),
                            chunks=sorted([m for _, m in pieces], key=lambda m: m['chunk']),
                            npz_sha256=T.sha256(path), source_sha256=source_hashes,
                            axes=dict(regret_hybrid=['rep', 'L', 'side', 'tau', 'h'],
                                      regret_static=['rep', 'L', 'h'], C_ref=['h']),
                            units=dict(cost='Mb*time (E4 saved costs)', regret='percent of C_ref'),
                            C_ref='mean saved V selected by saved M1_new/fresh decisions over all 500 instances',
                            no_scoring=True)
                        E.write_json(path.with_suffix('.json'), meta)
                        outputs.append(str(path.relative_to(T.ROOT)))
        parent_cpu, children_cpu = time.process_time() - cpu0, child_cpu() - children0
        summary = dict(command=command, complete=passed, workers=workers, CPU=parent_cpu + children_cpu,
            parent_CPU=parent_cpu, child_lifecycle_CPU=children_cpu, scientific_task_CPU=validation['task_CPU'],
            wall=time.perf_counter() - wall0, chunks_completed=len(results), new_chunks=len(results)-len(reused),
            reused_pilot_chunks=len(reused), source_sha256=source_hashes, outputs=outputs,
            validation_mismatches=validation['mismatches'], failure=failure, no_scoring=True)
        if command == 'pilot' and passed:
            summary['projection'] = pilot_projection(metadata, old)
        if pilot_summary:
            summary['cumulative_CPU_with_pilot'] = summary['CPU'] + pilot_summary['CPU']
            summary['pilot_projection'] = pilot_summary['projection']
        E.write_json(target / 'run_summary.json', summary)
        emit(dict(event='finished', complete=passed, CPU=summary['CPU'], wall=summary['wall'],
                  chunks=len(results), outputs=len(outputs), validation_mismatches=validation['mismatches']))
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('pilot', 'run'))
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args(argv)
    summary = run(args.command, args.workers)
    if not summary['complete']:
        raise SystemExit(1)
    if args.command == 'pilot':
        print(json.dumps(summary['projection'], sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
