"""DISCOVERY on branch explore/reformulate-grid (plan: notes/explore/reformulate_grid_plan.md).

Claude (AI) for Doan Van Tai, 23/10/2026. Screens a ladder of A-background loads for each
design slice, reusing the certified priors (SpectralLaw), the factorized D (run_v1_1_a2.queue_D)
and the native idle-gap sign screen (smr.gap_screen). Only sign probabilities, certificates and
budgets leave this module: never J, L*, margins, pipelines or per-state values.
"""
from experiments.lessons.v1_1_a_common import *
from experiments.lessons.run_v1_1_a2 import queue_D, common_unit, flags
from smr.gap_screen import backward, probability_interval, library
from smr.stationary import r2_keep
import argparse, itertools, multiprocessing, subprocess, time, traceback
import numpy as np

OUT = ROOT / 'results/explore_reformulate'
PLAN = 'notes/explore/reformulate_grid_plan.md'
LAMBDA_B = F(8)
KAPPAS = (F(3, 10), F(1), F(3))
QUANTILES_B = (F(1, 2), F(9, 10))
ETAS = (F(1, 2), F(3, 4))
HORIZONS = ('rh1', '2', '8')


def slices():
    out = [dict(kappa=k, alphaA=F(9, 10), alphaB=b, eta=e, horizon=h)
           for k, b, e, h in itertools.product(KAPPAS, QUANTILES_B, ETAS, HORIZONS)]
    out += [dict(kappa=F(1), alphaA=F(1, 2), alphaB=b, eta=e, horizon=h)
            for b, e, h in itertools.product(QUANTILES_B, ETAS, HORIZONS)]
    for i, s in enumerate(out, 1):
        s['slice'] = f'S{i:02}'
    return out


def ladder(eta):
    """A OFF rate >=0 needs lambdaA>=6; pre-decision A utilization (lambdaA+u)/mu <= .95."""
    u, lam, values = 2 * eta, F(6), []
    while (lam + u) / 10 <= F(95, 100):
        values.append(lam)
        lam += F(1, 4)
    return values


def make_cell(s, lam):
    u = 2 * s['eta']
    unit_a, law_a = law_for(lam, u, s['kappa'], 1)
    unit_b, law_b = law_for(LAMBDA_B, F(0), s['kappa'], 1)
    y_a = law_a.quantile(s['alphaA']) * unit_a
    y_b = law_b.quantile(s['alphaB']) * unit_b
    target_h = y_b / (2 - u) if s['horizon'] == 'rh1' else F(s['horizon'])
    H = math.ceil(target_h * 120)
    return dict(id=f"{s['slice']}@{lam}", slice=s['slice'], lambdaA=lam, kappa=s['kappa'], eta=s['eta'],
                u=u, ratesA=(lam - 6, lam + 6), ratesB=(F(2), F(14)), alphaA=s['alphaA'],
                alphaB=s['alphaB'], yA=y_a, yB=y_b, horizon=s['horizon'], target_h=target_h,
                H_coarse=H, h=F(H, 120), age=F(1))


def component(c, which, ref, native, mass, support, d_error, extended):
    """In-memory copy of run_v1_1_a4.component (same certificates and assertions)."""
    unit = common_unit(c, which, ref)
    factor = native / unit
    assert factor.denominator == 1
    indices = np.arange(len(mass), dtype=np.int64) * int(factor)
    H, dt = c['H_coarse'] * ref, F(1, 120 * ref)
    keep, keep_error = r2_keep(dt, c['kappa'])
    rates = c['rates' + which]
    stay_f = [(r + (c['u'] if which == 'A' else 0) - 10) * dt / unit for r in rates]
    switch_f = [(r + (c['u'] if which == 'B' else 0) - 10) * dt / unit for r in rates]
    assert all(v.denominator == 1 for v in stay_f + switch_f)
    stay, switch = tuple(map(int, stay_f)), tuple(map(int, switch_f))
    minimal = switch if which == 'A' else stay
    zero = np.column_stack([(indices + a >= 0) & (indices + a + (H - 1) * min(0, *minimal) >= 0)
                            for a in minimal])
    if np.all(zero[support]):
        return np.zeros(mass.shape, dtype=np.longdouble), mass, 0., float(d_error), zero.ravel()
    a, ea, _ = backward(indices, stay, H, keep, keep_error, extended)
    b, eb, _ = backward(indices, switch, H, keep, keep_error, extended)
    scale = np.longdouble(str((unit * dt).numerator)) / np.longdouble(str((unit * dt).denominator))
    value = (b.astype(np.longdouble) - a.astype(np.longdouble)) * scale
    error = (ea + eb) * float(scale) + float(16 * np.finfo(np.longdouble).eps * scale * (np.max(a) + np.max(b)))
    assert np.all(value[zero] == 0), 'nonidle certificate violated'
    if which == 'A':
        assert np.min(value) >= -error
    else:
        assert np.max(value) <= error
    return value, mass, error, float(d_error), zero.ravel()


def screen(c, ref):
    parts = {w: queue_D(c, w, ref) for w in 'AB'}

    def run(extended):
        A, pa, ea, da, za = component(c, 'A', ref, *parts['A'], extended)
        B, pb, eb, db, zb = component(c, 'B', ref, *parts['B'], extended)
        return probability_interval(A, B, pa, pb, ea, eb, da + db, za, zb)

    r = run(False)
    extended = r['unresolved_mass'] > .01
    if extended:
        r = run(True)
    if r['unresolved_mass'] > .01:
        label = 'HOLD_PRECISION'
    elif r['p_low'] >= .1 and r['p_high'] <= .9:
        label = 'in'
    elif r['p_high'] < .1 or r['p_low'] > .9:
        label = 'out'
    else:
        label = 'edge'
    return dict(p_low=r['p_low'], p_high=r['p_high'], unresolved=r['unresolved_mass'], D_error=r['D_error'],
                cls=label, extended=extended), parts


def budget(c, levels=(1, 2, 4, 8, 16)):
    """Same upper-bound formula as run_v1_1_a2 (A01 DP), per refinement level."""
    out = {}
    for ref in levels:
        updates, peak = 0, 0
        for which in 'AB':
            unit, dt, H = common_unit(c, which, ref), F(1, 120 * ref), c['H_coarse'] * ref
            growth = max(F(0), *((r + c['u'] - 10) * dt for r in c['rates' + which]))
            upper = c['y' + which] + 120 * ref * growth + H * growth
            drain = max(0, *(int((10 - r) * dt / unit) for r in c['rates' + which]))
            N = max(math.ceil(upper / unit) + 1, H * drain + 1)
            updates += 4 * N * H
            peak = max(peak, N * 2 * 8 * 8)
        out[ref] = (updates, peak)
    return out


def task(args):
    s, lam, levels, with_labels = args
    start = time.monotonic()
    row = dict(slice=s['slice'], lambdaA=lam, kappa=s['kappa'], eta=s['eta'], alphaA=s['alphaA'],
               alphaB=s['alphaB'], horizon=s['horizon'], u=2 * s['eta'], psi=(lam - LAMBDA_B) / 10,
               delta=(lam + 2 * s['eta'] - LAMBDA_B) / 10)
    try:
        c = make_cell(s, lam)
        row.update(yA=c['yA'], yB=c['yB'], h=c['h'], H_coarse=c['H_coarse'])
        for ref in levels:
            unit_a, law_a = law_for(lam, 2 * s['eta'], s['kappa'], ref)
            unit_b, law_b = law_for(LAMBDA_B, F(0), s['kappa'], ref)
            r, parts = screen(c, ref)
            row.update({f'{k}_{ref}': v for k, v in r.items()})
            row[f'law_error_{ref}'] = float(max(law_a.error, law_b.error))
            if with_labels:
                fa = flags(c, 'A', ref, parts['A'][0], parts['A'][2])
                fb = flags(c, 'B', ref, parts['B'][0], parts['B'][2])
                sd, wd = fa[1] or fb[0], fa[0] or fb[1]
                row[f'label_{ref}'] = ('conservation-cell' if fa[0] and fb[0] else 'SD-cell' if sd
                                       else 'WD-cell' if wd else 'candidate')
        for ref, (updates, peak) in budget(c).items():
            row[f'updates_{ref}'] = updates
            row[f'peak_{ref}'] = peak
        row['status'] = 'OK'
    except Exception as exc:  # recorded, never silently dropped
        row['status'] = f'{type(exc).__name__}: {exc}'
        row['trace'] = traceback.format_exc(limit=3)
    row['wall_s'] = time.monotonic() - start
    return clean(row)


def load_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def run(workers, stage):
    OUT.mkdir(parents=True, exist_ok=True)
    plan_commit = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', PLAN], text=True, cwd=ROOT).strip()
    assert plan_commit, 'plan must be committed before computing'
    library()  # build the native kernel once before forking
    if stage == 'ladder':
        tasks = [(s, lam, (1, 2), False) for s in slices() for lam in ladder(s['eta'])]
        path = OUT / 'ladder_rows.jsonl'
    else:
        raise SystemExit('unknown stage')
    config_path = OUT / f'config_{stage}.json'
    config = dict(author='Claude (AI) for Doan Van Tai', plan=PLAN, plan_commit=plan_commit, stage=stage,
                  label='DISCOVERY', outputs='sign intervals, certificates, budgets only',
                  forbidden=['J', 'Lstar', 'Cref', 'margins', 'beliefs', 'M0/M1', 'contrasts'],
                  tasks=len(tasks), source_hashes={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (
                      'src/smr/gap_screen.py', 'src/smr/native/idle_backward.cpp', 'src/smr/stationary_spectral.py',
                      'experiments/lessons/run_v1_1_a2.py', 'experiments/explore/reformulate_grid.py')})
    if config_path.exists():
        old = json.loads(config_path.read_text())
        assert old['source_hashes'] == config['source_hashes'], 'code changed since this stage started'
    else:
        write(config_path, config)
    done = {(r['slice'], r['lambdaA']) for r in load_rows(path)}
    todo = [t for t in tasks if (t[0]['slice'], str(t[1])) not in done]
    # Longest horizons first for load balance.
    todo.sort(key=lambda t: (t[0]['horizon'] != 'rh1', -t[0]['kappa'], -t[0]['alphaB'], -t[0]['eta']))
    print(f'{stage}: {len(tasks)} tasks, {len(todo)} to run', flush=True)
    with path.open('a') as handle, multiprocessing.get_context('fork').Pool(workers) as pool:
        for i, row in enumerate(pool.imap_unordered(task, todo, chunksize=1), 1):
            handle.write(json.dumps(row) + '\n')
            handle.flush()
            p = f"[{row.get('p_low_1', float('nan')):.3f},{row.get('p_high_1', float('nan')):.3f}]" if row['status'] == 'OK' else row['status']
            print(f"{i}/{len(todo)} {row['slice']} lam={row['lambdaA']} {p} {row['wall_s']:.1f}s", flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--stage', default='ladder')
    args = parser.parse_args()
    run(args.workers, args.stage)
