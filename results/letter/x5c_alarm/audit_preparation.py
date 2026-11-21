"""Doan Van Tai — independent read-only audit of X5c saved preparation data.

No experiment/scorer import and no simulator, truth or scientific score call.
Only the final audit JSON is written, exclusively.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'results/letter/x5c_alarm'


def read(path):
    return json.loads(path.read_text())


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def arrays(path):
    with np.load(path, allow_pickle=False) as f:
        return {k: f[k] for k in f.files}


def seed_for(seed, label):
    token = int.from_bytes(hashlib.sha256(label.encode()).digest()[:4], 'little')
    return int(np.random.SeedSequence([seed, token, 0]).generate_state(1, dtype=np.uint64)[0])


def streams_for(seed, arm, regime, date):
    root = seed_for(seed, f'X5C-{arm}|{regime}|{date}')
    labels = ('warm', 'rate', 'posterior-300.0', 'posterior-900.0', 'reference-decision', 'evaluation')
    return dict(base=seed, record=root, **{label: seed_for(root, label) for label in labels})


def audit_arm(arm):
    out = OUT / ('arm_' + arm)
    config = read(out / 'configuration.json')
    summary = read(out / 'step0/summary.json')
    beta, test_seed = (.3, 7100001) if arm == 'A' else (.6, 7200001)
    assert config['arm'] == arm and config['parameters']['beta'] == beta
    assert summary['complete'] and summary['decisions_record_count'] == 60
    for item in config['sources'].values():
        assert digest(Path(item['path'])) == item['sha256'], item['path']
    old = read(ROOT / 'results/letter/x4b/configuration.json')
    old_arrays = arrays(ROOT / 'results/letter/x4b/configuration.npz')
    for expected, info in zip(old['regimes'], config['regimes'], strict=True):
        assert all(info[k] == v for k, v in expected.items())
    if arm == 'B':
        train = read(out / 'train/summary.json')
        assert train['complete'] and train['record_count'] == len(train['records']) == 78
        assert train['seed'] == 7200005 and train['beta'] == .6 and not train['test_data_loaded']
        assert digest(out / 'train/summary.json') == config['train_summary_sha256']
        train_keys = set()
        for meta in train['records']:
            key = meta['regime'], meta['date']
            assert key not in train_keys
            train_keys.add(key)
            stem = out / 'train/training_rates' / ('_'.join(key))
            raw = arrays(stem.with_suffix('.npz'))
            assert read(stem.with_suffix('.json')) == meta
            assert digest(stem.with_suffix('.npz')) == meta['npz_sha256']
            assert meta['seed_base'] == 7200005 and meta['split'] == 'train'
            assert meta['streams'] == streams_for(7200005, arm, *key)
            assert all(v == .6 for v in meta['runtime_beta'].values())
            assert not meta['test_outcomes'] and meta['stage'] == 'training-rate'
            rates = raw['costs'][:, :, 0] / 21600
            assert np.array_equal(rates, raw['rates'])
            assert float((rates[:, 1] - rates[:, 0]).mean()) == meta['s_hat_Mbit']
        slopes = {info['id']: float(np.mean([m['s_hat_Mbit'] for m in train['records'] if m['regime'] == info['id']]))
                  for info in config['regimes']}
        assert slopes == config['s_hat_pooled_Mbit'] == train['s_hat_pooled_Mbit']
    else:
        assert config['s_hat_pooled_Mbit'] == read(ROOT / 'results/letter/x4b/training_summary.json')['s_hat_pooled_Mbit']
    expected_files = {f"{m['regime']}_{m['date']}{ext}" for m in config['test_records'] for ext in ('.json', '.npz')}
    assert {p.name for p in (out / 'step0/test').iterdir()} == expected_files
    groups, ties, metas = {}, {}, []
    decisions_checked = 0
    for record in config['test_records']:
        regime, date = record['regime'], record['date']
        stem = out / 'step0/test' / f'{regime}_{date}'
        meta, raw = read(stem.with_suffix('.json')), arrays(stem.with_suffix('.npz'))
        assert digest(stem.with_suffix('.npz')) == meta['npz_sha256']
        assert meta['stage'] == 'decisions-only' and meta['seed_base'] == test_seed
        assert meta['arm'] == arm and meta['beta'] == beta
        assert meta['streams'] == streams_for(test_seed, arm, regime, date)
        assert all(v == beta for v in meta['runtime_beta'].values())
        assert not meta['evaluation_called'] and not meta['C_ref_computed']
        assert {'V', 'costs', 'C_ref', 'regret'}.isdisjoint(raw)
        r = [v['id'] for v in config['regimes']].index(regime)
        info, cap = config['regimes'][r], old_arrays['capacity'][r]
        slope = config['s_hat_pooled_Mbit'][regime]
        link = info['e_star_index'] if slope < 0 else info['path_bottleneck_indices_after'][0]
        assert info['alarm_link_index'] == meta['alarm_link_index'] == link
        threshold = .001 * cap[link]
        assert threshold == info['alarm_threshold_Mbit'] == meta['alarm_threshold_Mbit']
        assert float(raw['s_hat_Mbit'].item()) == slope
        np.testing.assert_array_equal(raw['capacity_Mbps'], cap)
        mask = raw['candidate_alarm_queues_Mbit'] >= threshold
        indices = np.flatnonzero(mask)[:32]
        assert len(mask) == meta['candidates'] == 512 and meta['K'] == 64
        assert int(mask.sum()) == meta['alarms']
        np.testing.assert_array_equal(raw['alarm_mask'], mask)
        np.testing.assert_array_equal(raw['selected_indices'], indices)
        assert indices.tolist() == meta['selected_indices'] and len(indices) == meta['N']
        np.testing.assert_array_equal(raw['fresh_queues'][:, link], raw['candidate_alarm_queues_Mbit'][indices])
        metas.append(meta)
        if mask.sum() < 8:
            assert meta['status'] == 'ALARM_RARE' and 'decisions' not in raw
            continue
        assert meta['status'] == 'SELECTED'
        n = len(indices)
        hs = raw['h_seconds']
        assert list(hs) == [300, 600, 900, 1200, 1800, 3600, 7200]
        costs = [raw['M0_predicted_fresh']] + [raw['M0_predicted_stale'][:, i] for i in range(2)]
        for side, cost in enumerate(costs):
            hybrid = cost + np.array([0., slope])[None, :, None] * hs[None, None, :]
            expected_d = np.stack([np.argmin(cost, axis=1), np.argmin(hybrid, axis=1),
                                   np.full((n, len(hs)), int(slope < 0))], axis=1)
            expected_t = np.stack([cost[:, 0] == cost[:, 1], hybrid[:, 0] == hybrid[:, 1],
                                   np.full((n, len(hs)), slope == 0)], axis=1)
            np.testing.assert_array_equal(raw['decisions'][:, :, side], expected_d)
            np.testing.assert_array_equal(raw['tie_flags'][:, :, side], expected_t)
            decisions_checked += expected_d.size + expected_t.size
            for ih, h in enumerate(hs):
                g = groups.setdefault((regime, int(h), ('fresh', 'stale_300', 'stale_900')[side]), [0, 0, 0])
                g[0] += int((expected_d[:, 1, ih] != expected_d[:, 2, ih]).sum())
                g[1] += n
                g[2] += 1
        for ih, h in enumerate(hs):
            g = ties.setdefault((regime, int(h)), [0, 0])
            g[0] += int(raw['tie_flags'][:, 0, 0, ih].sum())
            g[1] += n
    rows = [dict(regime=r, h_s=h, side=s, numerator=v[0], denominator=v[1], records=v[2], share=v[0] / v[1])
            for (r, h, s), v in sorted(groups.items())]
    tie_rows = [dict(regime=r, h_s=h, numerator=v[0], denominator=v[1], share=v[0] / v[1])
                for (r, h), v in sorted(ties.items())]
    assert summary['records'] == metas and summary['disagreement'] == rows and summary['M0_fresh_ties'] == tie_rows
    num, den = sum(v[0] for v in ties.values()), sum(v[1] for v in ties.values())
    assert summary['M0_fresh_tie_pooled'] == dict(numerator=num, denominator=den, share=num / den if den else None)
    assert summary['alarms'] == sum(m['alarms'] for m in metas)
    assert summary['alarm_candidates'] == sum(m['candidates'] for m in metas) == 30720
    assert summary['alarm_rare_records'] == sum(m['status'] == 'ALARM_RARE' for m in metas)
    assert summary['selected_instances'] == sum(m['N'] for m in metas if m['status'] != 'ALARM_RARE')
    qualifying = [r for r in rows if r['side'] == 'fresh' and r['h_s'] <= 1800
                  and r['records'] >= 5 and 20 * r['numerator'] >= r['denominator']]
    gate = dict(verdict='SIGNAL_OK' if qualifying else 'NOT_ENOUGH_SIGNAL', threshold=.05,
                minimum_records=5, qualifying_cells=qualifying)
    assert summary['gate'] == gate
    source = ROOT / 'experiments/letter/x5c_alarm.py'
    source_digest = read(out / 'step0/started.json')['source_sha256']
    if arm == 'A':
        historical = OUT / 'source_at_arm_A_step0.py'
        assert digest(historical) == source_digest
        assert historical.read_text().replace("(out / 'train').mkdir(exist_ok=False)",
            "(out / 'train').mkdir(parents=True, exist_ok=False)") == source.read_text()
    else:
        assert digest(source) == source_digest
    if gate['verdict'] != 'SIGNAL_OK':
        assert not any((out / name).exists() for name in ('pilot', 'lock.json', 'truth', 'card_verdicts.json'))
    if (out / 'pilot/summary.json').exists():
        pilot = read(out / 'pilot/summary.json')
        assert len(pilot['records']) == 2
        for meta in pilot['records']:
            stem = out / 'pilot/records' / f"{meta['regime']}_{meta['date']}"
            assert meta == read(stem.with_suffix('.json'))
            assert digest(stem.with_suffix('.npz')) == meta['npz_sha256']
            assert meta['seed_base'] == (7100003 if arm == 'A' else 7200003)
            assert meta['stage'] == 'pilot' and meta['status'] == 'COMPLETE'
        assert pilot['CPU_s_records'] == sum(m['CPU_s'] for m in pilot['records'])
        assert pilot['projected_CPU_hours'] == pilot['mean_CPU_s'] * pilot['actual_truth_eligible_records'] / 3600
    return dict(status='PASS', records=60, candidate_queues_checked=30720,
        decision_and_tie_values_checked=decisions_checked, regime_h_side_groups=len(rows),
        train_records_checked=78 if arm == 'B' else 0, gate=gate)


if __name__ == '__main__':
    result = dict(owner='Doan Van Tai', independent=True, simulator_called=False,
                  arms={arm: audit_arm(arm) for arm in ('A', 'B')})
    with (OUT / 'preparation_audit.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps(result, sort_keys=True))
