"""Doan Van Tai — independent read-only arithmetic audit of saved X5 step0.

No experiment/scoring module is imported and no trajectory is simulated.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    config, summary = read(OUT/'configuration.json'), read(OUT/'step0/summary.json')
    source = read(ROOT/'results/letter/x4b/configuration.json')
    plan = [r for r in read(ROOT/'results/letter/x4b/inputs.json')['records']
            if r['split'] == 'test' and r['stratum'] == 'S']
    assert config['test_records'] == plan and len(plan) == 60
    expected = {f"{r['regime']}_{r['date']}{ext}" for r in plan for ext in ('.json', '.npz')}
    assert {p.name for p in (OUT/'step0/test').iterdir()} == expected
    with np.load(ROOT/'results/letter/x4b/configuration.npz', allow_pickle=False) as f:
        capacities = f['capacity']
    metas = {(r['regime'], r['date']): r for r in summary['records']}
    counts, ties, regions, nonzero = {}, {}, {}, []
    rare = alarms = selected = 0
    for record in plan:
        regime, date = record['regime'], record['date']
        stem = OUT/'step0/test'/f'{regime}_{date}'
        meta = read(stem.with_suffix('.json'))
        assert meta == metas[(regime, date)]
        assert meta['npz_sha256'] == sha(stem.with_suffix('.npz'))
        assert (meta['seed_base'], meta['stage'], meta['candidates'], meta['K']) == (7000001, 'decisions-only', 512, 64)
        assert not meta['evaluation_called'] and not meta['C_ref_computed']
        r = [i['id'] for i in source['regimes']].index(regime)
        e = source['regimes'][r]['e_star_index']
        threshold = .001*capacities[r, e]
        assert meta['e_star_index'] == e and meta['alarm_threshold_Mbit'] == threshold
        with np.load(stem.with_suffix('.npz'), allow_pickle=False) as f:
            raw = {k: f[k] for k in f.files}
        assert not {'V', 'C_ref', 'regret', 'G_S', 'costs'}.intersection(raw)
        q = raw['candidate_alarm_queues_Mbit']
        assert q.shape == (512,) and np.isfinite(q).all() and (q >= 0).all()
        mask = q >= threshold
        indices = np.flatnonzero(mask)[:32]
        count = int(mask.sum())
        assert np.array_equal(raw['alarm_mask'], mask)
        assert np.array_equal(raw['selected_indices'], indices)
        assert meta['selected_indices'] == indices.tolist() and meta['N'] == len(indices) and meta['alarms'] == count
        assert np.array_equal(raw['fresh_queues'][:, e], q[indices])
        assert np.array_equal(raw['capacity_Mbps'], capacities[r])
        assert raw['stale_queues'].shape == (len(indices), 2, len(capacities[r]))
        assert raw['stale_modes'].shape[:2] == (len(indices), 2)
        region = regions.setdefault(regime, dict(records=0, rare=0, alarms=0, candidates=0, min_alarms=512, max_alarms=0))
        region['records'] += 1; region['candidates'] += 512; region['alarms'] += count
        region['min_alarms'] = min(region['min_alarms'], count)
        region['max_alarms'] = max(region['max_alarms'], count)
        alarms += count
        if count:
            nonzero.append(dict(regime=regime, date=date, alarms=count, selected=len(indices), max_queue_Mbit=float(q.max())))
        if count < 8:
            assert meta['status'] == 'ALARM_RARE' and 'decisions' not in raw
            rare += 1; region['rare'] += 1
            continue
        assert meta['status'] == 'SELECTED'
        selected += len(indices)
        hs = raw['h_seconds']
        assert hs.tolist() == [300, 600, 900, 1200, 1800, 3600, 7200]
        slope = float(raw['s_hat_Mbit'].item())
        assert slope == config['s_hat_pooled_Mbit'][regime]
        for side, label in enumerate(('fresh', 'stale_300', 'stale_900')):
            costs = raw['M0_predicted_fresh'] if side == 0 else raw['M0_predicted_stale'][:, side-1]
            corrected = costs + np.array([0., slope])[None, :, None]*hs[None, None, :]
            expected_choices = np.stack([costs.argmin(axis=1), corrected.argmin(axis=1),
                np.full((len(indices), len(hs)), int(slope < 0))], axis=1)
            expected_ties = np.stack([costs[:, 0] == costs[:, 1], corrected[:, 0] == corrected[:, 1],
                np.full((len(indices), len(hs)), slope == 0)], axis=1)
            assert np.array_equal(raw['decisions'][:, :, side], expected_choices)
            assert np.array_equal(raw['tie_flags'][:, :, side], expected_ties)
            for ih, h in enumerate(hs):
                c = counts.setdefault((regime, int(h), label), [0, 0, 0])
                c[0] += int(np.count_nonzero(expected_choices[:, 1, ih] != expected_choices[:, 2, ih]))
                c[1] += len(indices); c[2] += 1
                if side == 0:
                    t = ties.setdefault((regime, int(h)), [0, 0])
                    t[0] += int(expected_ties[:, 0, ih].sum()); t[1] += len(indices)
    for row in summary['disagreement']:
        assert counts[(row['regime'], row['h_s'], row['side'])] == [row['numerator'], row['denominator'], row['records']]
    assert len(summary['disagreement']) == len(counts)
    for row in summary['M0_fresh_ties']:
        assert ties[(row['regime'], row['h_s'])] == [row['numerator'], row['denominator']]
    assert len(summary['M0_fresh_ties']) == len(ties)
    num, den = sum(v[0] for v in ties.values()), sum(v[1] for v in ties.values())
    assert summary['M0_fresh_tie_pooled'] == dict(numerator=num, denominator=den, share=num/den if den else None)
    gate_ok = any(side == 'fresh' and h <= 1800 and v[2] >= 5 and v[1] > 0 and 20*v[0] >= v[1]
                  for (regime, h, side), v in counts.items())
    gate = 'SIGNAL_OK' if gate_ok else 'NOT_ENOUGH_SIGNAL'
    assert gate == summary['gate']['verdict']
    assert (summary['alarm_rare_records'], summary['alarms'], summary['selected_instances']) == (rare, alarms, selected)
    assert summary['alarm_candidates'] == 60*512
    assert read(OUT/'step0/started.json')['source_sha256'] == sha(ROOT/'experiments/letter/x5_alarm.py')
    assert sha(OUT/'CARD_X5.md') == config['card_sha256']
    return dict(owner='Doan Van Tai', status='PASS', records=60, candidate_queues_checked=60*512,
        gate=gate, ALARM_RARE=rare, alarms=alarms, alarm_rate=alarms/(60*512),
        selected_instances=selected, regions=regions, nonzero_alarm_records=nonzero,
        fresh_tie_numerator=num, fresh_tie_denominator=den,
        groups_checked=len(counts), decision_tie_bits_checked=selected*3*3*7*2,
        step0_summary_sha256=sha(OUT/'step0/summary.json'),
        no_simulation=True, no_truth_or_score=True)


if __name__ == '__main__':
    result = audit()
    with (OUT/'step0_audit.json').open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps(result, sort_keys=True, allow_nan=False))
