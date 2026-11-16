"""Doan Van Tai — local W2 controls; no production wave is launched here."""
from copy import deepcopy
from fractions import Fraction as F
import json
import math
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.linalg import expm

from experiments.explore_ctmc import ctmc
from experiments.letter import mmpp, shat2, w2_eval, w2_run
from experiments.letter.e3_agediff import evaluate_agediff, prepare_regime
from experiments.letter.shat import load_cases


@pytest.mark.parametrize('alpha,load', [(3, 6), (3, 8), (6, 7), (6, 8.5), (7.5, 8), (7.5, 9)])
def test_sparse_solver_matches_ctmc_at_exact_parameters(alpha, load):
    N = ctmc.choose_N(load, .5, a=alpha)
    reference = ctmc.chain(load, .5, N, a=alpha)
    result = mmpp.stationary_mean(load, .5, alpha, N=N)
    assert abs(result.r-reference.r)/reference.r < 1e-8
    assert result.tail <= 1e-13
    assert result.residual <= 1e-9


def test_solver_continuous_amplitude_and_mm1_reduction():
    arbitrary = mmpp.stationary_mean(8, .37, 4.12345)
    larger = mmpp.stationary_mean(8, .37, 4.12345, N=2*arbitrary.N)
    assert arbitrary.tail <= 1e-13
    assert arbitrary.r == pytest.approx(larger.r, rel=1e-10)
    for alpha, load in ((0, 8), (0, 0)):
        result = mmpp.stationary_mean(load, .13, alpha)
        assert result.r == pytest.approx(load/(10-load), abs=1e-10)
    with pytest.raises(ValueError):
        mmpp.stationary_mean(8, .5, 8.1)


def test_chunk_fft_matches_every_direct_autocovariance():
    counts = np.random.default_rng(91).poisson(.8, 109)
    centered = (counts-counts.mean())/.01
    direct = np.array([centered[:len(counts)-k]@centered[k:]/(len(counts)-k) for k in range(48)])
    # Lag longer than a core chunk and a final tiny chunk exercise boundaries.
    actual = shat2.autocovariances(counts, .01, 47, chunk_bins=13)
    np.testing.assert_allclose(actual, direct, atol=1e-10, rtol=1e-12)


def test_fixed_count_estimator_on_long_known_mmpp():
    est = shat2.estimate_path(8., 0., 6., 1., 1., np.random.default_rng(70317), W=40000.)
    assert abs(est['lambda_hat']/8-1) < .05
    assert abs(est['alpha_hat']/6-1) < .05
    assert abs(est['kappa_hat']/1-1) < .15
    assert est['W'] == 40000. and est['delta'] == .01
    assert est['n_bins'] == 4000000 and est['status'] == 'VALID'
    assert est['alpha_hat']**2 == pytest.approx(max(0., est['rate_variance']-est['lambda_hat']/.01))
    cov = np.array(est['autocovariances'])
    used = est['positive_lags_summed']
    assert np.all(cov[1:used+1] > 0)
    assert cov[used+1] <= 0
    assert est['kappa_hat'] == pytest.approx(2*cov[1:used+1].sum()*.01/est['alpha_hat']**2)


def test_exact_within_bin_mode_simulation_reproduces_and_records_partial():
    first, second = np.empty(109, dtype=np.int32), np.empty(109, dtype=np.int32)
    a = shat2.simulate_counts(8, 6, .05, 1.095, np.random.default_rng(27), first, chunk_bins=13)
    b = shat2.simulate_counts(8, 6, .05, 1.095, np.random.default_rng(27), second, chunk_bins=13)
    assert a == b
    np.testing.assert_array_equal(first, second)
    assert a['partial_bin_duration'] == pytest.approx(.005)
    assert a['mode_switches'] > 0


@pytest.fixture(scope='module')
def real_prepared():
    return prepare_regime('7', '6', '1', '1/20', ['1/10', '10'])


def test_onset_theta_zero_equals_plain_hybrid_gap_and_regret(real_prepared):
    p = real_prepared
    raw = evaluate_agediff(*p['parameters'][:4], p['hs'], 1, prepared=p, arrays=True, disagree=False)
    arr = raw['_arrays']
    for k, base in enumerate(raw['h']):
        for level, s in (('true_s', p['s']), ('mm1', p['s_mm1'])):
            h = float(p['hs'][k])
            assert w2_eval.onset_shift(h, s, 0, p['T_int']) == h*s
            v = w2_eval._variant(arr, k, base, w2_eval.onset_shift(h, s, 0, p['T_int']))
            for key in ('regret_new', 'regret_old', 'G_S', 'share_new', 'share_old'):
                assert v[key] == pytest.approx(base['hybrid_levels'][level][key], abs=2e-12)


def test_probabilistic_bound_covers_actual_joint_disagreement_on_real_regime(real_prepared, tmp_path):
    p = real_prepared
    joint = w2_eval.JointDisagreement(p['Ast'], p['Bst'], p['T_int'], tmp_path)
    result = w2_eval.evaluate_age(p, p['T_int'], dict(s_hat_mmpp=None), include_bound=True, joint=joint)
    for row in result['h']:
        b = row['bound']
        assert 0 <= b['disagreement'] <= 1
        assert b['disagreement'] <= b['D']+1e-9
        assert b['P17_holds']


def test_joint_disagreement_matches_four_index_brute_force_and_sorted_cdf(tmp_path):
    A, B = ctmc.chain(8, .5, 3), ctmc.chain(7, .5, 4)
    joint = w2_eval.JointDisagreement(A, B, .7, tmp_path)
    rng = np.random.default_rng(83)
    a, ao, b, bo = [rng.integers(-2, 3, n).astype(float) for n in (A.n, A.n, B.n, B.n)]
    PA, PB = expm(A.Q.toarray()*.7), expm(B.Q.toarray()*.7)
    JA, JB = A.pi[:, None]*PA, B.pi[:, None]*PB
    for correction in (0., -.3, 1.):
        fresh = a[None, :, None, None]+b[None, None, None, :]+correction < 0
        stale = ao[:, None, None, None]+bo[None, None, :, None]+correction < 0
        brute = float(np.sum(JA[:, :, None, None]*JB[None, None, :, :]*(fresh != stale)))
        assert joint.mass(a, ao, b, bo, correction) == pytest.approx(brute, abs=2e-12)
    # Force the sorted-CDF path using >3000 pairs and compare a direct tensor
    # through the joint-event dense helper (bounded at ~10 million entries).
    C, D = ctmc.chain(8, .5, 27), ctmc.chain(7, .5, 27)
    sub = tmp_path/'large'; sub.mkdir()
    big = w2_eval.JointDisagreement(C, D, .7, sub)
    a, ao, b, bo = [rng.integers(-2, 3, n).astype(float) for n in (C.n, C.n, D.n, D.n)]
    dense = ctmc.dense_disagree(big.paths['A'].ravel(), np.tile(a, C.n), np.repeat(ao, C.n),
                              big.paths['B'].ravel(), np.tile(b, D.n), np.repeat(bo, D.n), .3)
    assert big.mass(a, ao, b, bo, .3) == pytest.approx(dense, abs=2e-12)


def test_exact_tie_break_adds_tie_true_cost_not_only_switch_mass():
    wA, wB = np.array([.2, .8]), np.array([.4, .6])
    a, b = np.array([-1., 0.]), np.array([0., 1.])
    va, vb = np.array([2., 3.]), np.array([5., 6.])
    mass, cost, ties = w2_eval._inclusive_pair(wA, a, va, wB, b, vb)
    joint = wA[:, None]*wB[None, :]
    chosen = a[:, None]+b[None, :] <= 0
    assert mass == pytest.approx(joint[chosen].sum())
    assert cost == pytest.approx(np.sum(joint*chosen*(va[:, None]+vb[None, :])))
    assert ties == pytest.approx(joint[a[:, None]+b[None, :] == 0].sum())


def test_inclusive_absolute_tail_keeps_both_boundaries():
    wA, wB = np.array([.2, .8]), np.array([.4, .6])
    a, b = np.array([-1., 0.]), np.array([0., 1.])
    for threshold in (0, .5, 1, 2):
        brute = np.sum(wA[:, None]*wB[None, :]*(np.abs(a[:, None]+b[None, :]) >= threshold))
        assert w2_eval.absolute_tail_mass(wA, a, wB, b, threshold) == pytest.approx(brute)


def test_sorted_same_index_disagreement_matches_dense(monkeypatch):
    rng = np.random.default_rng(94)
    wA, wB = rng.dirichlet(np.ones(19)), rng.dirichlet(np.ones(23))
    a1, a2, b1, b2 = [rng.integers(-2, 3, n).astype(float) for n in (19, 19, 23, 23)]
    reference = ctmc.dense_disagree(wA, a1, a2, wB, b1, b2, 0)
    monkeypatch.setattr(ctmc, 'DENSE_PAIRS', 1)
    assert w2_eval.sorted_disagreement(wA, a1, a2, wB, b1, b2) == pytest.approx(reference, abs=2e-12)


def test_theta_selection_cannot_read_held_out_outcomes():
    row = {'onset': {level: {f'{t:g}': {'regret_new': t, 'regret_old': t} for t in w2_eval.THETAS}
                     for level in w2_eval.LEVELS}}
    training = dict(family='asym', evaluations=[dict(h=[row])])
    # The held-out object deliberately has no outcomes.
    assert w2_run.choose_theta([training, dict(family='zf_a3_asym')])[0] == dict(true_s='0.5', mm1='0.5')
    before = deepcopy(training)
    w2_run.choose_theta([training])
    assert before == training


def test_case_count_seed_indices_e1_selection_and_atomic_write_once(tmp_path):
    cases = load_cases()
    assert len(cases) == 93 and [c['regime_index'] for c in cases] == list(range(93))
    selected = w2_eval.e1_regimes(cases)
    assert selected == {f: next(c['id'] for c in cases if c['family'] == f) for f in w2_run.FAMILIES}
    target = tmp_path/'raw.json'
    w2_eval.write_json_once(target, dict(value=1))
    with pytest.raises(FileExistsError):
        w2_eval.write_json_once(target, dict(value=2))
    assert json.loads(target.read_text()) == dict(value=1)
    with pytest.raises(ValueError):
        w2_eval.write_json_once(tmp_path/'bad.json', dict(value=math.nan))
    assert not (tmp_path/'bad.json').exists()


def _synthetic_analysis_records():
    """Tiny invented scorer fixtures, never plant outcomes or saved W2 raw."""
    records = []
    for family in w2_run.FAMILIES:
        rows = []
        for h in (.5, 4.):
            variant = dict(regret_new=.01, regret_old=.01, G_S=0.)
            rows.append(dict(h_Tint=h, h=str(h), M0=dict(regret_new=1., regret_old=1., G_S=0.),
                             hybrid={level: dict(variant) for level in ('true_s', 'mm1', 'mmpp')},
                             onset={level: {f'{t:g}': dict(regret_new=.01+t*.001, regret_old=.01+t*.001, G_S=0.)
                                            for t in w2_eval.THETAS} for level in w2_eval.LEVELS},
                             tie_break={level: dict(regret_new=1., regret_old=1., G_S=0.) for level in w2_eval.LEVELS},
                             bound=dict(D=.001, disagreement=.0005, P17_holds=True)))
        records.append(dict(id='synthetic_'+family, family=family, s=-1.,
                            estimator=dict(status='VALID', relative_error=.1, sign_correct=True),
                            evaluations=[dict(age_label=label, h=deepcopy(rows)) for label in ('seconds_1', 'Tint_1')],
                            e1=dict(P19_flat=True, P19_slope_identity=True), cpu_seconds=.1))
    return records


def test_prediction_scorer_known_verdicts_and_invalid_denominators():
    records = _synthetic_analysis_records()
    summary = w2_run.analyze_data(records)
    assert summary['selection']['chosen_theta'] == dict(true_s='0.5', mm1='0.5')
    assert all(p['status'] == 'held' for p in summary['predictions'].values())
    records[0]['estimator'] = dict(status='INVALID', relative_error=None, sign_correct=None)
    for ev in records[0]['evaluations']:
        for row in ev['h']:
            row['hybrid']['mmpp'] = dict(regret_new=None, regret_old=None, G_S=None)
    altered = w2_run.analyze_data(records)
    assert altered['predictions']['P13']['status'] == 'not held'
    assert altered['predictions']['P13']['sign']['denominator'] == 3
    assert altered['predictions']['P13']['sign']['meets'] == 2
    assert altered['predictions']['P14']['status'] == 'not held'
    assert altered['predictions']['P14']['by_side']['new']['denominator'] == 3
    assert altered['estimator_invalid_ids'] == ['synthetic_asym']


def test_full_analysis_refuses_partial_smoke(tmp_path):
    with pytest.raises(ValueError, match='all 93 completed regimes'):
        w2_run.analyze(SimpleNamespace(raw=tmp_path/'raw', out=tmp_path/'out'))
    assert not (tmp_path/'out').exists()


def test_e1_exports_three_panels_from_synthetic_fixture_only(tmp_path):
    rawdir, outdir = tmp_path/'synthetic_raw', tmp_path/'synthetic_figures'
    rawdir.mkdir()
    for family, case_id in w2_eval.e1_regimes().items():
        values = [[0., .2, .8, 1.2], [1., 1.2, 1.8, 2.2], [2., 2.2, 2.8, 3.2]]
        e1 = dict(h_Tint=[.1, 1., 4., 30.], state_labels=['empty_low', 'median_high', 'q95_high'],
                  actions={a: dict(V=values, V_hat=values) for a in ('stay', 'switch')})
        (rawdir/(case_id+'.json')).write_text(json.dumps(dict(status='COMPLETED', family=family, s=-1., e1=e1)))
    args = SimpleNamespace(raw=rawdir, out=outdir)
    w2_run.figure_e1(args)
    eps, pdf = outdir/'fig_e1.eps', outdir/'fig_e1.pdf'
    assert eps.read_bytes().startswith(b'%!PS-Adobe')
    assert pdf.read_bytes().startswith(b'%PDF')
    before = pdf.read_bytes()
    with pytest.raises(FileExistsError):
        w2_run.figure_e1(args)
    assert pdf.read_bytes() == before
