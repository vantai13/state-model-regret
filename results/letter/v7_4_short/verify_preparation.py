"""Doan Van Tai — independent raw-only preparation audit; no runner import.

No simulation and no H-P1 scoring. Reads pilot outcomes only for raw-schema and
gather checks. Every non-pilot input read here is an input hash or a decision.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def group(rows, include_tau):
    buckets = {}
    for row in rows:
        for pop in ('ALL', 'DAY3' if row['regime'] == 'DAY3' else 'DAY1_DAY2'):
            key = (pop, row['variant'], row['h_s'], row['side']) + ((row['tau_s'],) if include_tau else ())
            a = buckets.setdefault(key, dict(population=pop, variant=row['variant'], h_s=row['h_s'], side=row['side'],
                **({'tau_s': row['tau_s']} if include_tau else {}), **{c: 0 for c in
                ('denominator', 'disagree', 'M0_ties', 'Hybrid_ties', 'abs_gap_gt_h_abs_s')}))
            for field in ('denominator', 'disagree', 'M0_ties', 'Hybrid_ties', 'abs_gap_gt_h_abs_s'):
                a[field] += row[field]
    for a in buckets.values():
        for field in ('disagree', 'M0_ties', 'Hybrid_ties', 'abs_gap_gt_h_abs_s'):
            a[field+'_share'] = a[field]/a['denominator']
    return sorted(buckets.values(), key=lambda x: (x['population'], x['variant'], x['h_s'], x.get('tau_s', 0), x['side']))


def main(signal_only=False):
    signal = read(OUT/'signal.json')
    rows, samples = [], []
    assert len(signal['records']) == 87
    assert not signal['evaluation_called'] and not signal['C_ref_computed'] and not signal['outcomes_computed']
    expected_h = np.array([300, 600, 900, 1200, 1800])
    for meta in signal['records']:
        path = OUT/'decision_records'/f"{meta['regime']}_{meta['date']}.npz"
        assert sha(path) == meta['npz_sha256']
        assert meta == read(path.with_suffix('.json'))
        assert meta['seed_base'] == 7412001
        with np.load(path, allow_pickle=False) as raw:
            assert {'C_ref', 'V', 'regret', 'paired_evaluation', 'reference_decision_rollouts'}.isdisjoint(raw.files)
            np.testing.assert_array_equal(raw['h_seconds'], expected_h)
            np.testing.assert_array_equal(raw['tau_seconds'], [300, 900])
            d, ties = raw['decisions'], raw['tie_flags']
            assert d.shape == (32, 5, 2, 2, 5)
            for side, side_name in enumerate(('fresh', 'stale')):
                for t, tau in enumerate((300, 900)):
                    costs = raw['M0_predicted_fresh'] if side == 0 else raw['M0_predicted_stale'][:, t]
                    assert np.isfinite(costs).all()
                    np.testing.assert_array_equal(costs.argmin(axis=1), d[:, 0, side, t])
                    plain_tie = costs[:, 0] == costs[:, 1]
                    np.testing.assert_array_equal(plain_tie, ties[:, 0, side, t])
                    for variant, hi, si, rate in (('pooled', 1, 2, raw['s_hat_Mbit'][0]),
                                                   ('stable_only', 3, 4, raw['s_hat_Mbit'][1])):
                        hybrid = costs.copy()
                        hybrid[:, 1] += expected_h*rate
                        hybrid_tie = hybrid[:, 0] == hybrid[:, 1]
                        np.testing.assert_array_equal(hybrid.argmin(axis=1), d[:, hi, side, t])
                        np.testing.assert_array_equal(hybrid_tie, ties[:, hi, side, t])
                        np.testing.assert_array_equal(d[:, si, side, t], np.full((32, 5), int(rate < 0)))
                        for i, h in enumerate(expected_h):
                            rows.append(dict(regime=meta['regime'], date=meta['date'], variant=variant,
                                side=side_name, tau_s=tau, h_s=int(h), denominator=32,
                                disagree=int((d[:, hi, side, t, i] != d[:, si, side, t, i]).sum()),
                                M0_ties=int(plain_tie[:, i].sum()), Hybrid_ties=int(hybrid_tie[:, i].sum()),
                                abs_gap_gt_h_abs_s=int((np.abs(costs[:, 1, i]-costs[:, 0, i]) > h*abs(rate)).sum())))
            if not any(x['regime'] == meta['regime'] for x in samples):
                samples.append(dict(regime=meta['regime'], date=meta['date'], instance=0,
                    h_s=300, tau_s=300, side='fresh',
                    actions=d[0, :, 0, 0, 0].tolist(), ties=ties[0, :, 0, 0, 0].tolist(),
                    predicted_gap_Mbit_s=float(raw['M0_predicted_fresh'][0, 1, 0]-raw['M0_predicted_fresh'][0, 0, 0])))
    assert rows == signal['counts_by_record']
    by_h = group(rows, False)
    assert by_h == signal['by_h'] and group(rows, True) == signal['by_h_tau']
    primary = [x for x in by_h if x['population'] == 'DAY1_DAY2' and x['variant'] == 'pooled']
    total = sum(x['disagree'] for x in primary)
    horizons = sorted(x['h_s'] for x in primary if x['side'] == 'fresh' and x['disagree_share'] >= .01)
    verdict = 'SIGNAL_OK' if total >= 50 and len(horizons) >= 2 else 'NOT_ENOUGH_SIGNAL'
    assert signal['signal_gate']['verdict'] == verdict
    assert signal['signal_gate']['primary_disagreements'] == total
    assert signal['signal_gate']['fresh_horizons_at_least_1_percent'] == horizons
    assert all(x['denominator'] == 3712 for x in primary)
    original_card = subprocess.check_output(['git', 'show', '28419eda3:results/letter/v7_4_short/CARD_V7_4.md'], cwd=ROOT)
    assert original_card == (OUT/'CARD_V7_4.md').read_bytes()
    assert not (OUT/'truth').exists()
    if signal_only:
        result = dict(owner='Doan Van Tai', status='PASS', stage='independent_signal_only_audit',
            signal_independent_verdict=verdict, raw_decision_records=87, decision_count_rows=len(rows),
            total_primary_disagreements=total, fresh_horizons_at_least_1_percent=horizons,
            card_unchanged=True, truth_directory_absent=True, manual_samples=samples,
            audit_source_sha256=sha(__file__))
        with (OUT/'signal_verification.json').open('x') as f:
            json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
            f.write('\n')
        print(json.dumps(result, sort_keys=True))
        return
    pilot, predictions, lock = read(OUT/'pilot.json'), read(OUT/'predictions.json'), read(OUT/'lock.json')
    assert len(pilot['records']) == 2
    pilot_counts = []
    for meta in pilot['records']:
        assert meta['seed_base'] == 7472001 and meta['stage'] == 'pilot' and meta['pilot']
        path = OUT/'pilot/records'/f"{meta['regime']}_{meta['date']}.npz"
        assert sha(path) == meta['npz_sha256']
        assert meta == read(path.with_suffix('.json'))
        with np.load(path, allow_pickle=False) as raw:
            evaluation, reference = raw['paired_evaluation'], raw['reference_decision_rollouts']
            assert evaluation.shape == (32, 128, 2, 5) and reference.shape == (32, 64, 2, 5)
            assert np.isfinite(evaluation).all() and np.isfinite(reference).all()
            values = evaluation.mean(axis=1)
            refchoice = reference.mean(axis=1).argmin(axis=1)
            cref = values[np.arange(32)[:, None], refchoice, np.arange(5)]
            selected = values[np.arange(32)[:, None, None, None, None], raw['decisions'], np.arange(5)]
            np.testing.assert_array_equal(values, raw['V'])
            np.testing.assert_array_equal(refchoice, raw['reference_decision'])
            np.testing.assert_array_equal(cref, raw['C_ref'])
            np.testing.assert_array_equal(selected, raw['costs'])
            np.testing.assert_array_equal(selected-cref[:, None, None, None, :], raw['regret'])
            np.testing.assert_array_equal(cref.mean(axis=0)/expected_h >= 12.544525, raw['evaluable'])
            pilot_counts.append(dict(regime=meta['regime'], date=meta['date'], N=32, R_eval=128, R_dec=64))
    projected = max(0, signal['CPU_s_command']-signal['CPU_s_records']) + 87*max(x['CPU_s'] for x in pilot['records'])
    assert projected == pilot['projected_CPU_s']
    assert pilot['decision'] == ('USE_GCP' if projected > 21600 else 'LOCAL')
    card = (OUT/'CARD_V7_4.md').read_text()
    assert predictions['H_P1_reading_rule_verbatim'] == card[card.index('**H-P1 (chính'):card.index('## Dự báo')].strip()
    assert predictions['expected_side_instances_primary'] == 58*32*2*2*5
    assert predictions['expected_side_instances_all'] == 87*32*2*2*5
    assert not predictions['truth_run'] and predictions['H_P1_verdict'] == 'NOT_RUN'
    sndlib = Path(os.environ.get('SMR_SNDLIB', '~/papers/data/sndlib')).expanduser()
    external = {'sndlib:archive': sndlib/'directed-geant-uhlig-15min-over-4months-ALL-native.tgz',
                'sndlib:topology': sndlib/'sndlib-networks-native/geant.txt',
                'sndlib:train_cache': sndlib/'v7_3_train.npz'}
    for name, digest in lock['sha256'].items():
        assert sha(external[name] if name in external else ROOT/name) == digest, name
    original_card = subprocess.check_output(['git', 'show', '28419eda3:results/letter/v7_4_short/CARD_V7_4.md'], cwd=ROOT)
    assert original_card == (OUT/'CARD_V7_4.md').read_bytes()
    assert not (OUT/'truth').exists()
    result = dict(owner='Doan Van Tai', status='PASS', signal_independent_verdict=verdict,
        raw_decision_records=87, decision_count_rows=len(rows), total_primary_disagreements=total,
        fresh_horizons_at_least_1_percent=horizons, pilot_records_checked=pilot_counts,
        lock_files_checked=len(lock['sha256']), card_unchanged=True, truth_directory_absent=True,
        manual_samples=samples, audit_source_sha256=sha(__file__))
    with (OUT/'verification.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main(signal_only='--signal-only' in sys.argv)
