"""Doan Van Tai — independent V7-3 DEVIATION 01 archive/raw rescore.

No import of the test runner, original scorer, or deviation scoring wrapper.
Only the locked independent rescorer's metric functions are used.
"""
import csv
from datetime import datetime, timedelta
from pathlib import Path
import tarfile

import numpy as np

from experiments.letter import v7_3_data as Data
from experiments.letter import v7_3_rescore as R
from experiments.letter import v7_3_test_common as C


def read_window_maxima(dates, start_slot, *, root=None):
    """Independent archive traversal: complete day plus the prior eight slots."""
    if start_slot not in range(73) or len(set(dates)) != len(dates):
        raise ValueError('invalid archive calendar/window')
    root = C.data_root() if root is None else Path(root)
    wanted = {datetime.fromisoformat(d)+timedelta(minutes=15*i)
              for d in dates for i in range(-8, 96)}
    network = Data.topology(root)
    totals, errors = {}, {}
    with tarfile.open(root/Data.TM_NAME) as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith('.txt'):
                continue
            stamp = Data.stamp(member.name)
            if stamp not in wanted:
                continue
            if stamp in totals:
                totals[stamp], errors[stamp] = None, 'duplicate timestamp'
                continue
            try:
                with archive.extractfile(member) as source:
                    text = source.read().decode('utf-8')
                meta = Data.re.search(r'time\s*=\s*(\d{8}-\d{4})', text)
                if not meta or Data.stamp(meta[1]) != stamp:
                    raise ValueError('filename/META time mismatch')
                totals[stamp] = float(Data.parse_tm(text, network)[0].sum())
            except (ValueError, UnicodeError) as exc:
                totals[stamp], errors[stamp] = None, str(exc)
    maxima, exclusions = {}, []
    for date in sorted(dates):
        start = datetime.fromisoformat(date)
        times = [start+timedelta(minutes=15*i) for i in range(-8, 96)]
        bad = [t for t in times if totals.get(t) is None]
        if bad:
            exclusions.append(dict(date=date,
                reason='incomplete day' if any(t >= start for t in bad) else 'incomplete 22:00 warmup',
                invalid_slots=[dict(timestamp=t.isoformat(), error=errors.get(t, 'missing')) for t in bad]))
        else:
            maxima[date] = max(totals[t] for t in times[8+start_slot:8+start_slot+24])
    return maxima, exclusions


def exclusion_from_maxima(dates, maxima, train_maximum, *, threshold=2.0):
    """Derive exclusions independently; retain precise rates and ratios."""
    if (not np.isfinite(train_maximum) or train_maximum <= 0 or
            not np.isfinite(threshold) or threshold <= 0 or
            len(set(dates)) != len(dates) or len(dates) != len(maxima) or
            any(not np.isfinite(v) or v < 0 for v in maxima)):
        raise ValueError('invalid demand maxima or exclusion threshold')
    ratios = [dict(date=d, max_15min_total_demand_Mbps=float(v),
                   ratio=float(v/train_maximum)) for d, v in zip(dates, maxima)]
    removed = []
    for row in ratios:
        if row['max_15min_total_demand_Mbps'] > train_maximum*threshold:
            removed.append(dict(row, reason=(
                'DEVIATION_V7_3_01: maximum 15-min total demand in the decision '
                'window exceeds 2x the training-window maximum')))
    return dict(threshold_ratio=float(threshold), train_maximum_Mbps=float(train_maximum),
                demand_unit='Mbit/s',
                comparison='test maximum > threshold_ratio * train maximum',
                excluded_days=removed,
                top_5_test_ratios=sorted(ratios, key=lambda r: (-r['ratio'], r['date']))[:5])


def independent_inputs(inputs, run, params):
    manifest = C.read_json(C.ROOT/C.BASE/'data_manifest.json')
    planned = sorted(d for d in manifest['test_dates'] if datetime.fromisoformat(d).weekday() < 5)
    config = C.read_json(C.ROOT/params['training_dir']/'configuration.json')
    train_dates = config['train_dates']
    if (set(train_dates) & set(planned) or
            train_dates != sorted(d for d in manifest['train_dates']
                                  if datetime.fromisoformat(d).weekday() < 5)):
        raise ValueError('training calendar differs from locked split')
    maxima, exclusions = read_window_maxima(train_dates+planned, config['start_slot'])
    if any(d not in maxima for d in train_dates):
        raise ValueError('incomplete training calendar in archive')
    test_exclusions = [e for e in exclusions if e['date'] in planned]
    retained = sorted(d for d in planned if d in maxima)
    if (inputs['requested_dates'] != planned or inputs['dates'] != retained or
            inputs['exclusions'] != test_exclusions):
        raise ValueError('input calendar/exclusions differ from independent archive reader')
    train_peak = max(maxima[d] for d in train_dates)
    deviation = exclusion_from_maxima(retained, [maxima[d] for d in retained], train_peak)
    original = {(g, d) for g in params['regimes'] for d in retained}
    labels = inputs['records']
    if (len(labels) != len(original) or
            {(r['regime'], r['date']) for r in labels} != original or
            any(r['stratum'] not in ('S', 'O') for r in labels)):
        raise ValueError('input population differs from locked regimes/calendar')
    removed = {e['date'] for e in deviation['excluded_days']}
    days = [d for d in retained if d not in removed]
    required = {(g, d) for g in params['regimes'] for d in days}
    if (run['status'] != 'INCOMPLETE' or run['expected_records'] != len(original) or
            len(run['records']) != len(required) or
            {(r['regime'], r['date']) for r in run['records']} != required):
        raise ValueError('completed set differs from every regime x non-excluded day')
    return dict(inputs, dates=days, records=[r for r in labels if r['date'] not in removed],
                exclusions=test_exclusions+deviation['excluded_days']), deviation


def rescore(out=C.OUT):
    verified = C.verify_lock(out)  # First, including archive and locked sources.
    out = Path(out)
    target = out/'score_dev1'
    if (target/'rescore.json').exists():
        raise FileExistsError(target/'rescore.json')
    mismatches, rows = [], []
    deviation = None
    try:
        params = C.read_json(C.ROOT/C.PARAMS)
        inputs = C.read_json(out/'inputs.json')
        run = C.read_json(out/'run_summary.json')
        if inputs['lock_sha256'] != verified.digest or run['lock_sha256'] != verified.digest:
            raise ValueError('different input/run lock')
        filtered, deviation = independent_inputs(inputs, run, params)
        required = {(r['regime'], r['date']) for r in filtered['records']}
        stems = {f'{g}_{d}' for g, d in required}
        for suffix in ('npz', 'json'):
            if {p.stem for p in (out/'records').glob('*.'+suffix)} != stems:
                raise ValueError('unexpected or missing raw files')
        receipts = {(r['regime'], r['date']): r for r in run['records']}
        for label in sorted(filtered['records'], key=lambda r: (r['regime'], r['date'])):
            path = out/'records'/f'{label["regime"]}_{label["date"]}.npz'
            meta = C.read_json(path.with_suffix('.json'))
            digest = C.sha256(path)
            if (digest != meta['npz_sha256'] or
                    digest != receipts[label['regime'], label['date']]['npz_sha256'] or
                    meta['status'] != 'COMPLETE' or
                    any(meta[k] != label[k] for k in label)):
                raise ValueError('raw record hash/label mismatch')
            with np.load(path, allow_pickle=False) as saved:
                raw = {k: saved[k] for k in saved.files}
            if (raw['V'].shape != (params['N_test'], 2, 4) or
                    raw['paired_evaluation'].shape != (params['N_test'], params['R_eval'], 2, 4) or
                    raw['reference_decision_rollouts'].shape != (params['N_test'], params['R_dec'], 2, 4)):
                raise ValueError('sample-count mismatch')
            rows.extend(R.recompute(raw, label, params))
        rows.sort(key=lambda r: (r['regime'], r['date'], r['tau_s'], r['h_hours']))
        summary = R.rebuild_summary(rows, filtered, params)
        summary.update(analysis='AMENDED_ANALYSIS_DEVIATION_01', original_run_status=run['status'],
                       original_usable_weekdays=len(inputs['dates']),
                       completed_records=len(run['records']), lock_sha256=verified.digest,
                       F1_original_population=R.rebuild_summary([], inputs, params)['forecasts']['F1'])
        deviation.update(analysis='AMENDED_ANALYSIS_DEVIATION_01', original_run_status=run['status'],
                         original_usable_weekdays=len(inputs['dates']),
                         usable_weekdays=len(filtered['dates']), completed_records=len(run['records']),
                         wrapper_sha256=C.sha256(Path(__file__).with_name('v7_3_score_dev1.py')),
                         lock_sha256=verified.digest)
        R.compare(deviation, C.read_json(target/'deviation.json'), 'deviation', mismatches)
        R.compare(summary, C.read_json(target/'summary.json'), 'summary', mismatches)
        with (target/'cases.csv').open(newline='') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames or []
            if len(fields) != len(set(fields)) or set(fields) != set(rows[0]):
                mismatches.append('cases: fields differ or duplicate header')
            saved_rows = list(reader)
        if len(saved_rows) != len(rows):
            mismatches.append('cases: row count differs')
        for i, (row, saved) in enumerate(zip(rows, saved_rows)):
            converted = {k: R.read_cell(v, row.get(k)) for k, v in saved.items()}
            R.compare(row, converted, 'cases/'+str(i), mismatches)
    except (ValueError, KeyError, IndexError, OSError, TypeError) as exc:
        mismatches.append(str(exc))
    result = dict(status='MATCH' if not mismatches else 'MISMATCH',
                  mismatches=sorted(mismatches), cases_recomputed=len(rows),
                  relative_tolerance=1e-12, absolute_tolerance=0.,
                  lock_sha256=verified.digest, rescorer_sha256=C.sha256(Path(__file__)),
                  analysis='AMENDED_ANALYSIS_DEVIATION_01', original_run_status='INCOMPLETE',
                  independent_exclusion=deviation)
    C.write_json(target/'rescore.json', result)
    return result


if __name__ == '__main__':
    result = rescore()
    print(result['status'])
    for mismatch in result['mismatches']:
        print(mismatch)
    raise SystemExit(0 if result['status'] == 'MATCH' else 1)
