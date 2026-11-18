"""Doan Van Tai — V7-3 DEVIATION 01, saved-raw amended analysis only.

The original one-shot run stays INCOMPLETE. Metrics and verdicts come from
the locked scorer; this wrapper changes only the declared input population.
"""
import csv
from datetime import datetime
import io
from pathlib import Path

import numpy as np

from experiments.letter import v7_3_cong as Cong
from experiments.letter import v7_3_day as Day
from experiments.letter import v7_3_score as Score
from experiments.letter import v7_3_test as Test
from experiments.letter import v7_3_test_common as C

THRESHOLD = 2.0
ANALYSIS = 'AMENDED_ANALYSIS_DEVIATION_01'
REASON = ('DEVIATION_V7_3_01: maximum 15-min total demand in the decision '
          'window exceeds 2x the training-window maximum')


def json_native(value):
    """I/O only: numpy scalar -> identical Python scalar, including zero counts."""
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {k: json_native(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_native(v) for v in value]
    return value


def exclusion_from_maxima(dates, maxima, train_maximum, *, threshold=THRESHOLD):
    """Strict input-only threshold, in Mbit/s; no outcome-based selection."""
    dates = list(dates)
    maxima = np.asarray(maxima, dtype=float)
    if (not np.isfinite(train_maximum) or train_maximum <= 0 or
            not np.isfinite(threshold) or threshold <= 0 or
            maxima.shape != (len(dates),) or len(set(dates)) != len(dates) or
            not np.isfinite(maxima).all() or (maxima < 0).any()):
        raise ValueError('invalid demand maxima or exclusion threshold')
    ratios = [dict(date=d, max_15min_total_demand_Mbps=float(x),
                   ratio=float(x/train_maximum)) for d, x in zip(dates, maxima)]
    excluded = [dict(row, reason=REASON) for row, x in zip(ratios, maxima)
                if x > threshold*train_maximum]
    return dict(threshold_ratio=float(threshold),
                train_maximum_Mbps=float(train_maximum), demand_unit='Mbit/s',
                comparison='test maximum > threshold_ratio * train maximum',
                excluded_days=excluded,
                top_5_test_ratios=sorted(ratios, key=lambda r: (-r['ratio'], r['date']))[:5])


def recompute_exclusion(inputs, verified):
    manifest = C.read_json(C.ROOT/C.BASE/'data_manifest.json')
    dates = sorted(d for d in manifest['test_dates']
                   if datetime.fromisoformat(d).weekday() < 5)
    if inputs['requested_dates'] != dates:
        raise ValueError('input calendar differs from locked manifest')
    training, _, config = Day.load(Cong.OUT)
    days, exclusions = Test.load_days(dates, config, verified=verified,
                                      root=C.data_root(), manifest=manifest)
    if inputs['dates'] != days['dates'].tolist() or inputs['exclusions'] != exclusions:
        raise ValueError('input calendar/exclusions differ from locked loader')
    train_maximum = float(training['days'].sum(axis=2).max())
    maxima = days['days'].sum(axis=2).max(axis=1)
    return exclusion_from_maxima(inputs['dates'], maxima, train_maximum)


def amend_inputs(inputs, run, params, deviation):
    """Require the entire amended Cartesian population, never a partial subset."""
    if run['status'] != 'INCOMPLETE':
        raise ValueError('DEVIATION 01 requires the original INCOMPLETE run')
    dates = inputs['dates']
    if dates != sorted(set(dates)):
        raise ValueError('duplicate/unsorted input calendar')
    original = {(g, d) for g in params['regimes'] for d in dates}
    labels = inputs['records']
    if (len(labels) != len(original) or
            {(r['regime'], r['date']) for r in labels} != original or
            any(r['stratum'] not in ('S', 'O') for r in labels)):
        raise ValueError('input population differs from locked regimes/calendar')
    removed = [r['date'] for r in deviation['excluded_days']]
    if len(removed) != len(set(removed)) or not set(removed) <= set(dates):
        raise ValueError('duplicate/unknown deviation exclusion')
    retained = [d for d in dates if d not in removed]
    expected = {(g, d) for g in params['regimes'] for d in retained}
    actual = {(r['regime'], r['date']) for r in run['records']}
    if actual != expected or len(run['records']) != len(expected):
        raise ValueError('completed set differs from every regime x non-excluded day')
    if run['expected_records'] != len(original):
        raise ValueError('original run schedule differs from input population')
    return dict(inputs, dates=retained,
                records=[r for r in labels if r['date'] not in removed],
                exclusions=inputs['exclusions']+deviation['excluded_days'])


def read_completed_records(out, inputs, run, params):
    """Apply the locked read_records integrity checks without relabeling the run."""
    expected = {(r['regime'], r['date']) for r in inputs['records']}
    stems = {f'{g}_{d}' for g, d in expected}
    for suffix in ('npz', 'json'):
        if {p.stem for p in (out/'records').glob('*.'+suffix)} != stems:
            raise ValueError('unexpected or missing raw files')
    receipts = {(r['regime'], r['date']): r for r in run['records']}
    rows = []
    for label in sorted(inputs['records'], key=lambda r: (r['regime'], r['date'])):
        path = out/'records'/f'{label["regime"]}_{label["date"]}.npz'
        meta = C.read_json(path.with_suffix('.json'))
        digest = C.sha256(path)
        if (digest != meta['npz_sha256'] or
                digest != receipts[label['regime'], label['date']]['npz_sha256'] or
                meta['status'] != 'COMPLETE' or
                any(meta[k] != label[k] for k in label)):
            raise ValueError('record integrity/stratum mismatch')
        with np.load(path, allow_pickle=False) as saved:
            raw = {k: saved[k] for k in saved.files}
        if (raw['V'].shape != (params['N_test'], 2, 4) or
                raw['paired_evaluation'].shape != (params['N_test'], params['R_eval'], 2, 4) or
                raw['reference_decision_rollouts'].shape != (params['N_test'], params['R_dec'], 2, 4)):
            raise ValueError('record sample counts differ from card')
        rows.extend(Score.case_rows(raw, meta, params))
    return sorted(rows, key=lambda r: (r['regime'], r['date'], r['tau_s'], r['h_hours']))


def score(out=C.OUT):
    verified = C.verify_lock(out)  # First: before inputs, loaders or saved outcomes.
    out = Path(out)
    target = out/'score_dev1'
    for name in ('summary.json', 'deviation.json'):
        if (target/name).exists():
            raise FileExistsError(target/name)
    params = C.read_json(C.ROOT/C.PARAMS)
    inputs = C.read_json(out/'inputs.json')
    run = C.read_json(out/'run_summary.json')
    if inputs['lock_sha256'] != verified.digest or run['lock_sha256'] != verified.digest:
        raise ValueError('inputs/run were generated under a different lock')
    deviation = recompute_exclusion(inputs, verified)
    filtered = amend_inputs(inputs, run, params, deviation)
    rows = read_completed_records(out, filtered, run, params)
    summary = Score.summarize(rows, filtered, params)
    summary.update(analysis=ANALYSIS, original_run_status=run['status'],
                   original_usable_weekdays=len(inputs['dates']),
                   completed_records=len(run['records']), lock_sha256=verified.digest,
                   F1_original_population=Score.summarize([], inputs, params)['forecasts']['F1'])
    deviation.update(analysis=ANALYSIS, original_run_status=run['status'],
                     original_usable_weekdays=len(inputs['dates']),
                     usable_weekdays=len(filtered['dates']),
                     completed_records=len(run['records']),
                     wrapper_sha256=C.sha256(Path(__file__)), lock_sha256=verified.digest)

    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    csv_bytes = buffer.getvalue().encode('utf-8')
    csv_path = target/'cases.csv'
    if csv_path.exists():
        # Preserve the first attempt after a JSON-only failure. Never overwrite it.
        if csv_path.read_bytes() != csv_bytes:
            raise ValueError('existing partial cases.csv is not byte-identical')
    else:
        C.atomic_write(csv_path, lambda p: p.write_bytes(csv_bytes))
    C.write_json(target/'summary.json', json_native(summary))
    C.write_json(target/'deviation.json', deviation)
    return summary


if __name__ == '__main__':
    result = score()
    print(f'{ANALYSIS}: {result["completed_records"]} records, '
          f'{result["usable_weekdays"]} weekdays, {result["cases"]} cases')
    for name, entry in result['tests'].items():
        print(f'{name}: {entry["verdict"]} {entry["numerator"]}/{entry["denominator"]}')
