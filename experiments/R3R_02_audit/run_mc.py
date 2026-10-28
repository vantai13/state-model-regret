"""Doan Van Tai — preregistered comparison of engine black box and independent MC.

The independent simulator is immutable after its specification-only session.
Engine policy code is supplied only to this integration runner, not its author.
"""
import argparse
import json
import math
import pickle
import sys
import time
from pathlib import Path
from fractions import Fraction as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from experiments.R3R_02_audit import bridge as B
from experiments.R3R_02_audit import independent_mc as M

NAMES = ('00', '01', '10', '11')
MAP = {'GS': 'G_S', 'GM': 'G_M', 'GSM': 'G_SM', 'Gamma': 'Gamma',
       'GS_given_M1': 'G_S_M1', 'GM_given_S1': 'G_M_S1'}


def clean(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, F):
        return str(value)
    raise TypeError(type(value).__name__)


def write(path, data):
    path.write_text(json.dumps(data, default=clean, indent=2) + '\n')


def stats(v):
    v = np.asarray(v, dtype=float)
    return dict(mean=float(v.mean()), sd=float(v.std(ddof=1)), se=float(v.std(ddof=1) / np.sqrt(len(v))), n=len(v))


def comparison(engine, observed, allowance=0.):
    difference = abs(float(engine) - observed['mean'])
    se = observed['se']
    z = difference / se if se else (0. if difference == 0 else float('inf'))
    limit = 3 * se + allowance
    return dict(engine=float(engine), **observed, absolute_difference=difference,
                z=z, numerical_allowance=allowance, limit=limit,
                status='PASS' if difference <= limit else 'ALARM')


def policies(model, data):
    a = model.actions(data.y, data.x)
    return dict(zip(NAMES, a.T))


def nodes(model):
    coords, weights = [], []
    ua, ra, wa, _ = B.P.observation_bins(model.cell, 'A', int(model.spec[6]), int(model.spec[7]))
    ub, rb, wb, _ = B.P.observation_bins(model.cell, 'B', int(model.spec[6]), int(model.spec[7]))
    for ia, pa in zip(ra, wa):
        for ib, pb in zip(rb, wb):
            coords.append([float(ua * ia), float(ub * ib)]); weights.append(float(pa * pb))
    return np.asarray(coords), np.asarray(weights)


def target(r):
    C = r['Cbar']
    out = {'L11': C, 'Cbar': C, 'L00': C + r['G_SM'],
           'L10': C + r['G_M_S1'], 'L01': C + r['G_S_M1']}
    out.update({k: r[v] for k, v in MAP.items()})
    return out


def sample(model, la, lb, n, seed, kind):
    kwargs = dict(u=float(model.cell['u']), h=float(model.cell['h']), n=n, seed=seed,
                  c_sw=float(F(model.spec[8])))
    if kind == 'nodes':
        kwargs.update(zip(('y_nodes', 'node_weights'), nodes(model)))
    return M.sample_population(la, lb, **kwargs)


def prepare(rid, out):
    resumed = out.exists()
    if resumed and (out / 'prepare.json').exists() and json.loads((out / 'prepare.json').read_text())['status'] == 'COMPLETE':
        raise ValueError('preserve completed MC prepare output')
    out.mkdir(parents=True, exist_ok=True)
    row = list(B.specs()).index(rid)
    seed = 318301000 + 1000 * row
    start = time.monotonic()
    if resumed:
        with (out / 'engine_cache.pkl').open('rb') as f: model, la, lb = pickle.load(f)
        result = json.loads((out / 'prepare.json').read_text())
        result['resumed_after_diagnostic_index_guard_fix'] = True
    else:
        model = B.BlackBox(B.spec(rid))
        la = M.stationary_law(float(model.cell['lambdaA']), float(model.cell['u']), float(model.cell['kappa']))
        lb = M.stationary_law(float(model.cell['lambdaB']), 0., float(model.cell['kappa']))
        (out / 'stationary.json').write_text(json.dumps({'A': la.diagnostics, 'B': lb.diagnostics}, indent=2) + '\n')
        # Local reusable cache, not a published scientific output or dependency on pilot cache.
        with (out / 'engine_cache.pkl').open('wb') as f: pickle.dump((model, la, lb), f, protocol=5)
        result = {'id': rid, 'seed_base': seed, 'C1': [], 'C2': [], 'pilot': {}, 'status': 'RUNNING'}
    c = model.cell
    def save(): write(out / 'prepare.json', result)
    save()
    states = [(0, 0, 0, 0), (0, 1, 0, 1), (1, 0, 1, 1), (5, 1, 5, 0), (200, 0, 200, 1)]
    for j, state in enumerate(states):
        if len(result['C1']) > j: continue
        expected = model.costs(np.asarray([state], dtype=float))[0]
        history = []
        for retry in (0, 1):
            data = M.sample_fixed_state(*state, lambda_a=float(c['lambdaA']), lambda_b=float(c['lambdaB']),
                                       u=float(c['u']), kappa=float(c['kappa']), h=float(c['h']),
                                       c_sw=float(F(model.spec[8])), n=65536 * 4 ** retry,
                                       seed=seed + 10 + j + 50000 * retry)
            observed = [comparison(v, stats(x)) for v, x in zip(expected, (data.CStay, data.CSwitch))]
            history.append({'retry': retry, 'seed': data.metadata['seed'], 'checks': observed})
            if all(v['status'] == 'PASS' for v in observed): break
        result['C1'].append({'state': state, 'history': history}); save()
    for side, law in [('A', la), ('B', lb)]:
        engine_side = getattr(model, side)
        positive = law.joint.sum(axis=1).copy(); positive[0] = 0
        positive /= positive.sum()
        qvals = sorted({0., *[float(np.searchsorted(np.cumsum(positive), p) * law.quantum) for p in (.25, .5, .75, .9)]})
        for j, y in enumerate(qvals):
            if any(row['side'] == side and row['y'] == y for row in result['C2']): continue
            d, _ = engine_side.old_gap(np.asarray([y]))
            linear = float((engine_side.post - engine_side.pre) * engine_side.dt ** 2 * engine_side.H * (engine_side.H + 1) / 2)
            expected = float(d[0]) + linear
            history = []
            for retry in (0, 1):
                data = M.sample_side_conditional(law, y, managed_stay=float(engine_side.pre),
                                               managed_switch=float(engine_side.post), h=float(c['h']),
                                               n=65536 * 4 ** retry, seed=seed + 100 + (20 if side == 'B' else 0) + j + 50000 * retry)
                observed = comparison(expected, stats(data['gap']))
                history.append({'retry': retry, 'seed': data['metadata']['seed'], 'comparison': observed,
                                'condition': data['metadata']['condition']})
                if observed['status'] == 'PASS': break
            # MC distribution is unchanged for mutants; only the claimed engine expectation changes.
            index = engine_side._indices(np.asarray([y]))[0]
            no_age = float((engine_side.d[index] * engine_side.old_mode[index]).sum()) + linear if index <= engine_side.cap else linear
            independent_mode = (float(engine_side.old_d[index].mean()) if index < len(engine_side.old_d) else 0.) + linear
            result['C2'].append({'side': side, 'y': y, 'history': history,
                                 'mutant_no_age': comparison(no_age, stats(data['gap'])),
                                 'mutant_old_mode_independent': comparison(independent_mode, stats(data['gap']))})
            save()
    for i, kind in enumerate(('nodes', 'stationary')):
        if kind in result['pilot']: continue
        data = sample(model, la, lb, 2048, seed + 200 + i, kind)
        score = M.score_policies(data, policies(model, data))
        expected = json.loads((ROOT / f'results/lessons/l3r_3/engine_run01/{rid}/audit.json').read_text())['levels'][0]
        ratio = max(score['sd'][k] for k in MAP) / (.001 * expected['Cbar'])
        desired = max(32768, int(math.ceil(ratio ** 2)))
        final_n = min(524288, 2 ** math.ceil(math.log2(desired)))
        result['pilot'][kind] = {'N0': 2048, 'seed': seed + 200 + i, 'SD': score['sd'],
                                 'requested_N': desired, 'final_N': final_n,
                                 'maximum_cap_reached': desired > 524288,
                                 'pilot_mean_not_final': score['mean']}
        save()
    result['wall_s'] = time.monotonic() - start
    result['status'] = 'COMPLETE'
    save()
    print(json.dumps({'id': rid, 'prepare': 'COMPLETE', 'N': {k: v['final_N'] for k, v in result['pilot'].items()}, 'wall_s': result['wall_s']}))


def final(rid, out):
    selection = json.loads((ROOT / 'experiments/R3R_02_audit/MC_N_selection.json').read_text())
    if (out / 'final.json').exists(): raise ValueError('preserve previous MC final')
    prepare = json.loads((out / 'prepare.json').read_text())
    with (out / 'engine_cache.pkl').open('rb') as f:
        model, la, lb = pickle.load(f)
    source = json.loads((ROOT / f'results/lessons/l3r_3/engine_run01/{rid}/audit.json').read_text())
    base, expected = source['levels'][0], target(source['levels'][0])
    alternates = [target(v) for v in source['levels'][1:]]
    numerical = {k: max(abs(v[k] - expected[k]) for v in alternates) for k in expected}
    cap_bounds = M.population_cost_truncation_bound(la, lb, u=float(model.cell['u']), h=float(model.cell['h']), c_sw=float(F(model.spec[8])))
    result = {'id': rid, 'status': 'RUNNING', 'N_selection_commit': selection['selection_commit_placeholder'],
              'C3': {}, 'numerical_allowance_status': 'refinement differences, not certified bounds'}
    for i, kind in enumerate(('nodes', 'stationary')):
        n = selection['regimes'][rid][kind]['final_N']
        hist = []
        for retry in (0, 1):
            seed = prepare['seed_base'] + 300 + i + retry * 50000
            data = sample(model, la, lb, n * 4 ** retry, seed, kind)
            score = M.score_policies(data, policies(model, data), save_path=out / f'{kind}_retry{retry}_moments.npz')
            checks = {}
            for k, exp in expected.items():
                allowance = 0.
                if kind == 'stationary':
                    allowance = numerical[k] + (cap_bounds['contrast_absolute_bias_bounds'].get(k, cap_bounds['per_policy_loss_absolute_bias_bound']))
                checks[k] = comparison(exp, {'mean': score['mean'][k], 'sd': score['sd'][k], 'se': score['se'][k], 'n': score['n']}, allowance)
            record = {'retry': retry, 'seed': seed, 'N': score['n'], 'checks': checks,
                      'contrast_SE_max_ppC': 100 * max(score['se'][k] for k in MAP) / base['Cbar'],
                      'SE_target_met': max(score['se'][k] for k in MAP) <= .001 * base['Cbar']}
            hist.append(record)
            if all(v['status'] == 'PASS' for v in checks.values()): break
        result['C3'][kind] = hist
        write(out / 'final.json', result)
    result['status'] = 'PASS' if all(v[-1]['SE_target_met'] and all(c['status'] == 'PASS' for c in v[-1]['checks'].values()) for v in result['C3'].values()) else 'UNRESOLVED'
    write(out / 'final.json', result)
    print(json.dumps({'id': rid, 'final': result['status']}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('phase', choices=('prepare', 'final')); p.add_argument('rid'); p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    (prepare if a.phase == 'prepare' else final)(a.rid, a.out)
