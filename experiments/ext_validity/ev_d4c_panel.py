"""Doan Van Tai — EV-D4c three-arm sign-law card (15/11/2026).

The card is results/ext_validity/ev_d4c/CARD.md. No experiment runs on import.
Design/summary writers are exclusive; test execution resumes via EV-D4b.
"""
from collections import defaultdict
from contextlib import contextmanager
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

from experiments.ext_validity import ev_d4_panel as D4
from experiments.ext_validity import ev_d4b_panel as D4B

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/ext_validity/ev_d4c'
R = (0.1, 0.3, 0.5, 0.8, 1.0, 1.2, 2.5, 5.0)
GROUPS = dict(low=R[:3], band=R[3:6], high=R[6:])
ARMS = ('C', 'L', 'H')
TINT_MAX, MIN_REGIMES = 240.0, 10
SER_C = 'results/ext_validity/ev_d4/series_ditl4h_mod10.npz'
SER_L = 'results/ext_validity/ev_d4/diag_loop15/series_202304121000.npz'
ROW_FIELDS = ('arm', 'regime', 'r', 'tau', 'twin', 'pred30', 'G30', 'G10_abs',
              'G30_abs', 'pred10_abs', 'pred30_abs', 'inc_ok', 'level_ok',
              'inc_ratio', 'noise_ok')


def _new(*paths):
    for path in paths:
        if path.exists():
            raise FileExistsError(path)


def _read(path):
    return json.loads(path.read_text())


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(value, indent=1, allow_nan=False) + '\n')


def _train_path(case, probe=False):
    return OUT / ('train_probe' if probe else 'train') / f"{case['id']}_s{case['seed']}.json"


def _regimes(seed, cap, floor=0.):
    """EV-D4b.design's generator has no importable helper; retain its formulas."""
    from scipy.stats import qmc
    for k, (name, (lo, hi, n)) in enumerate(D4.STRATA.items()):
        accepted = 0
        for pu, pa, px in qmc.Sobol(3, scramble=True, seed=seed + k).random(4096):
            if accepted == n:
                break
            u = 0.25 * (1 + int(pu * 7))
            lamA = 6 + 0.25 * int(pa * max(1, int((cap - u - 6) * 4) + 1))
            x = round(lo + (hi - lo) * px, 2)
            lamB = round(lamA + x * u, 4)
            if not (lamB >= 6 and floor < max(lamA, lamB) + u <= cap):
                continue
            yield name, f'{name[0].upper()}{accepted:02d}', lamA, lamB, u
            accepted += 1
        if accepted != n:
            raise RuntimeError(f'stratum {name}: only {accepted}/{n} regimes in ({floor}, {cap}]')


def design_probe():
    path = OUT / 'probe_cases.json'
    _new(path)
    low = list(_regimes(20270115, 7.75))
    high = list(_regimes(20270126, 9.75, 7.75))
    cases = []
    for arm in ARMS:
        for i, (stratum, suffix, lamA, lamB, u) in enumerate(high if arm == 'H' else low):
            regime = arm + suffix
            cases.append(dict(id=regime + '_probe', arm=arm, regime=regime, r=None, tau=1.0,
                              lamA=lamA, lamB=lamB, u=u, seed=(17000 if arm == 'H' else 15000) + i,
                              n_inst=10000, spacing_mult=3, train_T=100000., sample_dt=0.2,
                              h_mult=[10, 30], batches=40, cls='trace_cox',
                              params=dict(series=SER_C if arm == 'C' else SER_L, key='s0',
                                          path_keys=['s0', 's1'], bin=0.01),
                              stratum=stratum, trace='ditl4h'))
    _write(path, cases)
    print(len(cases), 'probe cases')


def design():
    path, exclusions = OUT / 'cases_all.json', OUT / 'design_excluded.json'
    _new(path, exclusions)
    cases, excluded = [], []
    for probe in _read(OUT / 'probe_cases.json'):
        tr = _read(_train_path(probe, probe=True))
        ti = tr['T_int']
        if tr['T_int_censored'] or ti <= 0:
            excluded.append(dict(arm=probe['arm'], regime=probe['regime'], T_int=ti,
                                 reason='probe T_int censored' if tr['T_int_censored'] else 'probe T_int <= 0'))
            continue
        if not math.isfinite(ti):
            raise ValueError(f"{probe['regime']}: nonfinite probe T_int")
        for r in R:
            tau = round(r * ti, 2)
            if tau < 0.01:
                raise ValueError(f"{probe['regime']}: tau {tau} < 0.01 at r={r}")
            cases.append(dict(probe, id=f"{probe['regime']}_r{round(r * 10):02d}", r=r, tau=tau))
    _write(path, cases)
    _write(exclusions, dict(excluded=excluded))
    print(len(cases), 'cases;', len(excluded), 'probe exclusions')


def select():
    path, selection_path = OUT / 'cases.json', OUT / 'selection.json'
    _new(path, selection_path)
    cases = _read(OUT / 'cases_all.json')
    by_regime, reasons = defaultdict(list), {}
    for case in cases:
        by_regime[case['regime']].append(case)
    for regime, group in by_regime.items():
        why = []
        if len(group) != len(R) or {c['r'] for c in group} != set(R):
            why.append('missing or duplicate design r cases')
        for case in group:
            tr = _read(_train_path(case))
            if tr['T_int_censored']:
                why.append(f"{case['id']}: T_int censored")
            elif not 0 < tr['T_int'] <= TINT_MAX:
                why.append(f"{case['id']}: T_int outside (0, {TINT_MAX}]")
        reasons[regime] = why
    for item in _read(OUT / 'design_excluded.json')['excluded']:
        reasons[item['regime']] = [item['reason']]
    # Pair on the suffix, retaining each arm's own training and its own tau.
    paired_reasons = {regime: list(why) for regime, why in reasons.items()}
    for regime in list(reasons):
        if regime[0] in ('C', 'L'):
            other = ('L' if regime[0] == 'C' else 'C') + regime[1:]
            if other not in reasons or reasons[other]:
                paired_reasons[regime].append(f"paired {other}: " + '; '.join(reasons.get(other, ['missing regime'])))
    arms = {}
    rule = f'Every design r has uncensored 0 < T_int <= {TINT_MAX} s; C/L must both pass; minimum {MIN_REGIMES} regimes per arm'
    for arm in ARMS:
        eligible = sorted(regime for regime, why in paired_reasons.items() if regime[0] == arm and not why)
        arms[arm] = dict(kept_regimes=len(eligible), regimes=eligible, rule=rule,
                         arm_status='OK' if len(eligible) >= MIN_REGIMES else 'STOP',
                         excluded=[dict(regime=regime, reasons=why) for regime, why in sorted(paired_reasons.items())
                                   if regime[0] == arm and why])
    kept = [c for c in cases if not paired_reasons[c['regime']] and arms[c['arm']]['arm_status'] == 'OK']
    _write(path, kept)
    _write(selection_path, dict(arms=arms))
    print(json.dumps(arms, indent=1))
    if all(a['arm_status'] == 'STOP' for a in arms.values()):
        raise SystemExit('STOP: all three arms have fewer than 10 eligible regimes')


@contextmanager
def _bind(module):
    original = module.OUT, module.CASES, module.PRED
    module.OUT, module.CASES, module.PRED = OUT, OUT / 'cases.json', OUT / 'predictions.csv'
    try:
        yield
    finally:
        module.OUT, module.CASES, module.PRED = original


def predict():
    with _bind(D4):
        D4.predict()


def run(workers):
    if workers < 1:
        raise ValueError('workers must be positive')
    # Includes signature assertion, fixed test seed, resume and heavy-first ordering.
    with _bind(D4B):
        D4B.run(workers)


def manifest():
    path = OUT / 'raw_manifest.json'
    _new(path)
    files = sorted((OUT / 'test').glob('*.json'))
    result = dict(created=time.strftime('%Y-%m-%dT%H:%M:%S%z'), n=len(files),
                  sha256={f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files})
    _write(path, result)
    print(result['n'], 'raw files hashed at', result['created'])


def verify_lock():
    failed = []
    hashes = _read(OUT / 'lock.json')['sha256']
    for relative, expected in hashes.items():
        path = ROOT / relative
        try:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as error:
            failed.append(f'{relative}: {error}')
            continue
        if actual != expected:
            failed.append(f'{relative}: SHA256 mismatch')
    if failed:
        print('LOCK_FAIL\n' + '\n'.join(failed))
        raise SystemExit(1)
    print('LOCK_PASS', len(hashes))


def _predictions():
    with (OUT / 'predictions.csv').open(newline='') as f:
        return {(row['id'], int(row['h_mult']), row['twin']): float(row['pred_abs'])
                for row in csv.DictReader(f)}


def _median(values):
    return float(np.median(values)) if values else None


def describe():
    """Train-only lock preview: deliberately no reference to the test directory."""
    path = OUT / 'seen_before_lock.json'
    _new(path)
    cases, predictions = _read(OUT / 'cases.json'), _predictions()
    training = {c['id']: _read(_train_path(c)) for c in cases}
    arms = {}
    for arm in ARMS:
        group = [c for c in cases if c['arm'] == arm]
        times = [training[c['id']]['T_int'] for c in group]
        by_r, by_group = {}, {}
        for r in R:
            selected = [training[c['id']] for c in group if c['r'] == r]
            by_r[str(r)] = dict(n_cases=len(selected),
                                median_beta1_A=_median([t['nowcast']['A']['beta'][1] for t in selected]),
                                median_F_old_minus_F_new_h30=_median([
                                    t['shares']['30']['F_old_fluid_nowcast'] - t['shares']['30']['F_new']
                                    for t in selected]))
        for name, rs in GROUPS.items():
            n = sum(abs(100 * predictions[c['id'], 30, twin] / training[c['id']]['mean_stay']) >= .25
                    for c in group if c['r'] in rs for twin, _, _ in D4.NOWCAST)
            by_group[name] = dict(n_filter_rows_h30=n)
        arms[arm] = dict(kept_regimes=len({c['regime'] for c in group}),
                         T_int=dict(min=min(times) if times else None, median=_median(times),
                                    max=max(times) if times else None, over='main_train_cases'),
                         by_r=by_r, by_group=by_group)
    result = dict(arms=arms, filter='abs(100 * pred_abs_h30 / train.mean_stay) >= 0.25 (approximate)')
    _write(path, result)
    print(json.dumps(result, indent=1))


def _stats(rows, inconclusive):
    n = len(rows)
    noise = [row for row in rows if row['noise_ok']]
    ratios = [row['inc_ratio'] for row in rows if row['inc_ratio'] is not None]
    return dict(n=n, inc_share=sum(row['inc_ok'] for row in rows) / n if n else None,
                level_share=sum(row['level_ok'] for row in rows) / n if n else None,
                median_inc_ratio=_median(ratios), n_inc_ratio=len(ratios),
                n_regimes=len({row['regime'] for row in rows}), n_noise=len(noise),
                inc_share_noise=sum(row['inc_ok'] for row in noise) / len(noise) if noise else None,
                status='NOT_EVALUABLE' if n < 10 else ('INCONCLUSIVE' if inconclusive else 'OK'))


def _sign(value):
    return (value > 0) - (value < 0)


def _band_label(stats):
    if stats['status'] != 'OK':
        return stats['status']
    if stats['inc_share'] >= .8:
        return 'WORKS'
    return 'FAILS' if stats['inc_share'] <= .65 else 'MIXED'


def _h3(h2, low_load, high_load):
    if h2 != 'PASS' or low_load not in ('WORKS', 'FAILS', 'MIXED'):
        return 'UNRESOLVED'
    if low_load == 'WORKS':
        # The card says "any" for H here; H is needed only for the LOAD/TRACE branch.
        return 'LOOPING'
    if low_load == 'FAILS' and high_load == 'WORKS':
        return 'LOAD'
    if low_load == high_load == 'FAILS':
        return 'TRACE_OR_OTHER'
    return 'UNRESOLVED'


def score():
    path, row_path = OUT / 'score.json', OUT / 'score_rows.csv'
    _new(path, row_path)
    cases, predictions = _read(OUT / 'cases.json'), _predictions()
    selection_path = OUT / 'selection.json'
    selection = _read(selection_path)['arms'] if selection_path.exists() else {}
    result, records = dict(arms={}), []
    for arm in ARMS:
        group = [c for c in cases if c['arm'] == arm]
        if selection.get(arm, {}).get('arm_status', 'OK' if group else 'STOP') == 'STOP':
            result['arms'][arm] = dict(arm_status='STOP')
            result['D6-' + arm] = dict(verdict='STOP', exploratory=arm != 'C')
            continue
        raw = {}
        for case in group:
            for m in case['h_mult']:
                raw_path = OUT / 'test' / f"{case['id']}_s{case['seed']}_h{m}.json"
                if raw_path.exists():
                    raw[case['id'], m] = _read(raw_path)
        expected = sum(len(c['h_mult']) for c in group)
        inconclusive = len(raw) < .9 * expected
        rows, d6 = [], []
        for case in group:
            if (case['id'], 10) not in raw or (case['id'], 30) not in raw:
                continue
            g10, g30 = raw[case['id'], 10], raw[case['id'], 30]
            e = g10['E_stay']['mean'] / g30['E_stay']['mean']
            for twin, _, _ in D4.NOWCAST:
                p10, p30 = (predictions[case['id'], m, twin] for m in (10, 30))
                pred30 = 100 * p30 / g30['E_stay']['mean']
                if abs(pred30) < .25:
                    continue
                a, b = g10['twins'][twin], g30['twins'][twin]
                delta, pred_delta = b['G_S'] - a['G_S'], p30 - p10
                row = dict(arm=arm, regime=case['regime'], r=case['r'], tau=case['tau'], twin=twin,
                           pred30=pred30, G30=b['pct_E_stay'], G10_abs=a['G_S'], G30_abs=b['G_S'],
                           pred10_abs=p10, pred30_abs=p30, inc_ok=_sign(delta) == _sign(pred_delta),
                           level_ok=_sign(b['pct_E_stay']) == _sign(pred30),
                           inc_ratio=delta / pred_delta if pred_delta != 0 else None,
                           noise_ok=abs(delta) > 2 * (a['se'] + b['se']))
                rows.append(row)
            for twin in D4.PLUGIN:
                a, b = g10['twins'][twin], g30['twins'][twin]
                growth = b['pct_E_stay'] - e * a['pct_E_stay']
                se = b['se_pct'] + e * a['se_pct']
                d6.append(abs(growth) <= max(.25, 2 * se))
        records.extend(rows)
        result['arms'][arm] = dict(arm_status='INCONCLUSIVE' if inconclusive else 'OK',
                                   completed=len(raw), of=expected, inconclusive=inconclusive,
                                   groups={name: _stats([row for row in rows if row['r'] in rs], inconclusive)
                                           for name, rs in GROUPS.items()},
                                   by_r={str(r): _stats([row for row in rows if row['r'] == r], inconclusive) for r in R})
        share = sum(d6) / len(d6) if d6 else None
        result['D6-' + arm] = dict(n=len(d6), share=share, threshold=.90, exploratory=arm != 'C',
                                   verdict='INCONCLUSIVE' if inconclusive else (
                                       'NOT_EVALUABLE' if len(d6) < 10 else ('PASS' if share >= .9 else 'FAIL')))
    c = result['arms']['C']
    for hypothesis, name in (('H1', 'low'), ('H2', 'band')):
        stats = c.get('groups', {}).get(name, {})
        status = 'STOP' if c['arm_status'] == 'STOP' else (
            'INCONCLUSIVE' if c['inconclusive'] else stats['status'])
        if status == 'OK':
            if hypothesis == 'H1':
                passed = stats['inc_share'] >= .8
            else:
                passed = stats['inc_share'] <= .65 and stats['median_inc_ratio'] is not None and stats['median_inc_ratio'] < .5
            status = ('NOT_EVALUABLE' if hypothesis == 'H2' and stats['median_inc_ratio'] is None
                      else ('PASS' if passed else 'FAIL'))
        result[hypothesis] = dict(verdict=status, n=stats.get('n', 0), inc_share=stats.get('inc_share'),
                                  median_inc_ratio=stats.get('median_inc_ratio'))
    result['H1']['threshold'] = .8
    result['H2'].update(max_inc_share=.65, median_inc_ratio_strictly_below=.5)
    labels = {arm: ('STOP' if result['arms'][arm]['arm_status'] == 'STOP'
                    else _band_label(result['arms'][arm]['groups']['band'])) for arm in ('L', 'H')}
    for arm, label in labels.items():
        result['arms'][arm]['band_label'] = label
    result['H3'] = dict(verdict=_h3(result['H2']['verdict'], labels['L'], labels['H']),
                        L_band=labels['L'], H_band=labels['H'])
    OUT.mkdir(parents=True, exist_ok=True)
    with row_path.open('x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=ROW_FIELDS)
        writer.writeheader()
        writer.writerows(records)
    _write(path, result)
    print(json.dumps(result, indent=1))


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('design-probe', 'design', 'select', 'predict', 'describe',
                                            'run', 'manifest', 'verify-lock', 'score'))
    parser.add_argument('workers', type=int, nargs='?')
    args = parser.parse_args(argv)
    if args.command == 'run':
        if args.workers is None or args.workers < 1:
            parser.error('run needs a positive worker count')
        run(args.workers)
    else:
        if args.workers is not None:
            parser.error('workers is only used by run')
        {'design-probe': design_probe, 'design': design, 'select': select, 'predict': predict,
         'describe': describe, 'manifest': manifest, 'verify-lock': verify_lock, 'score': score}[args.command]()


if __name__ == '__main__':
    main()
