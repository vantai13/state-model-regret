"""Doan Van Tai — direct centered moments on saved Phase 6 response surfaces.

Post-hoc arithmetic, no evaluator/profile construction and no new plant points.
Keep the DL-137 analyzer and outputs unchanged. Both conditional grids' mean
gaps are reported: their numerical mismatch must not be hidden in covariance.
"""
import csv
import json
from contextlib import ExitStack
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

import numpy as np

from tools import analyze_phase6_saved as S

ROOT = S.ROOT
OUT = ROOT / 'results/phase6/closeout_l6_4'


def centered_moments(weights, gaps, actions, common_mean):
    """Direct products, without obtaining alignment by subtracting saved G_S."""
    w, d, a = (np.asarray(v, dtype=S.P.LD) for v in (weights, gaps, actions))
    mass = w.sum(dtype=S.P.LD)
    assert abs(mass - 1) < S.P.LD('1e-12'), 'NONUNIT_PROBABILITY_MASS'
    share = (w * a).sum(dtype=S.P.LD)
    mean = (w * d).sum(dtype=S.P.LD)
    return dict(mass=mass, share=share, mean_gap=mean,
                covariance=(w * (d - mean) * (a - share)).sum(dtype=S.P.LD),
                common_centered=(w * (d - common_mean) * a).sum(dtype=S.P.LD))


def grid_moments(A, B, cost, common_mean):
    # Pass one obtains the means; pass two sums the centered products directly.
    stats = S.aggregate(A, B, cost)
    mean = S.P.LD(stats['mean_gap'])
    share = S.P.LD(stats['share'])
    totals = {k: S.P.LD(0) for k in ('mass', 'covariance', 'common_centered')}
    for start in range(0, len(A['w']), 128):
        sl = slice(start, start + 128)
        w = A['w'][sl, None] * B['w'][None, :]
        d = A['d'][sl, None] + B['d'][None, :] + S.P.number(cost)
        h = A['h'][sl, None] + B['h'][None, :] + S.P.number(cost)
        certified = ((A['zero'][sl, None] & B['zero'][None, :]) |
                     (A['sat'][sl, None] & B['sat'][None, :]))
        action = np.where(certified, S.P.number(cost), h) < 0
        totals['mass'] += w.sum(dtype=S.P.LD)
        totals['covariance'] += (w * (d - mean) * (action - share)).sum(dtype=S.P.LD)
        totals['common_centered'] += (w * (d - common_mean) * action).sum(dtype=S.P.LD)
    assert abs(totals['mass'] - 1) < S.P.LD('1e-12'), 'NONUNIT_PROBABILITY_MASS'
    return dict(stats, **{k: float(v) for k, v in totals.items()})


def analyze(root=ROOT, cache_dir=S.CACHE):
    root = Path(root)
    S.R.gate_record(root)
    original = root / 'results/phase6/analysis_l6_4'
    before = json.loads((original / 'summary.json').read_text())
    for group in ('input_sha256', 'cache_files_sha256'):
        for name, digest in before[group].items():
            assert S.sha(root / name) == digest, ('CHANGED_INPUT', name)
    source_rows = list(csv.DictReader((original / 'members.csv').open()))
    cache = S.SavedCache(cache_dir)
    out = []

    def forbidden(*args, **kwargs):
        raise AssertionError('NEW_EVALUATION_FORBIDDEN')

    with ExitStack() as stack:
        for obj, name in ((S.population, 'evaluate'), (S.population, 'side'),
                          (S.population, 'pair_loss'), (S.profiles, 'get'),
                          (S.law_cache, 'get'), (S.P, 'idle'), (S.P, 'mean_idle'),
                          (S.P, 'age'), (S.NativeLaw, '__init__')):
            stack.enter_context(patch.object(obj, name, forbidden))
        for r in source_rows:
            path = root / S.R.PANEL_OUT / r['id'] / 'level_640_4.json'
            raw = json.loads(path.read_text())
            A, B = cache.side(raw, 'A'), cache.side(raw, 'B')
            c = F(r['c'])
            bar = S.P.LD(r['actual_mean_gap'])
            old = grid_moments(A['old'], B['old'], c, bar)
            new = grid_moments(A['current'], B['current'], c, bar)
            alpha = float(r['stationary_stake'])
            df = old['share'] - new['share']
            bias = alpha * df
            stake = (float(bar) - alpha) * df
            alignment = old['common_centered'] - new['common_centered']
            centered_cov = old['covariance'] - new['covariance']
            # The old and current quadratures approximate one common joint law.
            # Record their mean-gap discrepancy rather than asserting it is zero.
            mean_bridge = old['share'] * (old['mean_gap'] - float(bar))
            mean_bridge -= new['share'] * (new['mean_gap'] - float(bar))
            gs = float(r['G_S'])
            err = gs - bias - stake - alignment
            assert abs(err) < 1e-10 * max(1, abs(gs)), (r['id'], err)
            cov_error = alignment - centered_cov - mean_bridge
            assert abs(cov_error) < 1e-10 * max(1, abs(gs)), (r['id'], cov_error)
            out.append(dict(id=r['id'], scan_id=r['scan_id'], role=r['role'], label=r['label'],
                h_over_kappa=str(F(r['h']) / F(r['kappa'])), Cref=r['Cref'], G_S=gs,
                stake_ratio=float(bar) / alpha, delta_F=df,
                oracle_switch_share=float(r['oracle_switch_share']),
                bias=bias, mean_stake_error=stake, alignment_common_centered=alignment,
                covariance_old=old['covariance'], covariance_new=new['covariance'],
                covariance_difference=centered_cov, conditional_mean_bridge=mean_bridge,
                conditional_mean_gap_difference=old['mean_gap'] - new['mean_gap'],
                old_mass=old['mass'], new_mass=new['mass'],
                decomposition_residual=err, covariance_bridge_residual=cov_error,
                **{k + '_pp': 100 * v / float(r['Cref']) for k, v in
                   [('bias', bias), ('mean_stake_error', stake),
                    ('alignment_common_centered', alignment),
                    ('covariance_difference', centered_cov), ('conditional_mean_bridge', mean_bridge)]}))
            print(r['scan_id'], 'DIRECT_CENTERED_MOMENTS_OK', flush=True)
    D = [r for r in out if r['role'] == 'D']
    correlation = float(np.corrcoef(
        [float(r['G_S']) / float(r['Cref']) for r in D],
        [r['oracle_switch_share'] for r in D])[0, 1])
    summary = dict(analysis='POST_HOC_SAVED_DATA_ONLY', primary_verdict='INCONCLUSIVE',
        members=len(out), D_count=len(D), new_evaluator_calls=0, new_profiles_built=0,
        Pearson_z_oracle_switch_share_posthoc=correlation,
        max_decomposition_residual=max(abs(r['decomposition_residual']) for r in out),
        max_covariance_bridge_residual=max(abs(r['covariance_bridge_residual']) for r in out),
        max_conditional_mean_gap_difference=max(abs(r['conditional_mean_gap_difference']) for r in out),
        max_conditional_mean_bridge_pp=max(abs(r['conditional_mean_bridge_pp']) for r in out),
        input_sha256={str(p.relative_to(root)): S.sha(p) for p in
            [original / 'members.csv', original / 'summary.json', root / 'tools/analyze_phase6_saved.py']},
        original_input_sha256=before['input_sha256'], cache_files_sha256=cache.provenance,
        limitations=['Exploratory Pearson on 13 selected points, no prospective test or population inference',
                     'Same cached surfaces, shared numerical bias remains',
                     'Conditional-grid mean mismatch is explicitly retained, not hidden in covariance',
                     'No new predictor, fit, threshold, representation or experimental design adopted'])
    for group in ('input_sha256', 'original_input_sha256', 'cache_files_sha256'):
        for name, digest in summary[group].items():
            assert S.sha(root / name) == digest, ('INPUT_CHANGED_DURING_READ', name)
    return out, summary


def main():
    assert not OUT.exists(), 'OUTPUT_ALREADY_EXISTS'
    rows, summary = analyze()
    OUT.mkdir(parents=True, exist_ok=False)
    with (OUT / 'covariance.csv').open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary['analyzer_sha256'] = S.sha(__file__)
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if not k.endswith('sha256')}, indent=2))


if __name__ == '__main__':
    main()
