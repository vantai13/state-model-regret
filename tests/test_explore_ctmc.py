"""Doan Van Tai — deterministic controls for the ctmc-v1 evaluator (L7.1) [AI (Claude) theo ủy quyền].

V1, V2, V4, V9, V10, V11 and the held-out guard of experiments/explore_ctmc/SPEC.md, plus unit checks.
"""
from fractions import Fraction as F
import math

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from experiments.explore_ctmc import ctmc


def test_generator_rows_sum_to_zero_with_nonnegative_rates():
    ch = ctmc.Chain(F(17, 2), F(1, 2), 60)
    Q = ch.Q.toarray()
    assert np.allclose(Q.sum(axis=1), 0, atol=1e-12)
    off = Q - np.diag(np.diag(Q))
    assert (off >= 0).all()
    # state (3, high) under load 8.5: arrival 14.5, service 10, flip 2
    i = 2 * 3 + 1
    assert Q[i, 2 * 4 + 1] == pytest.approx(14.5) and Q[i, 2 * 2 + 1] == pytest.approx(10)
    assert Q[i, 2 * 3] == pytest.approx(2)


def test_V2_amplitude_zero_gives_truncated_geometric():
    N = 200
    ch = ctmc.Chain(F(8), F(1, 2), N, a=0)
    rho = 0.8
    geo = (1 - rho) * rho ** np.arange(N + 1) / (1 - rho ** (N + 1))
    assert np.abs(ch.pi.reshape(-1, 2).sum(axis=1) - geo).max() <= 1e-12
    assert ch.r == pytest.approx((geo * np.arange(N + 1)).sum(), abs=1e-10)


def test_truncated_stationary_matches_matrix_geometric():
    load, kappa = F(17, 2), F(1, 2)
    N = ctmc.choose_N(load, kappa)
    ch = ctmc.Chain(load, kappa, N)
    inf = ctmc.matrix_geometric(load, kappa)
    levels = np.array([inf['pi0'] @ np.linalg.matrix_power(inf['R'], n) for n in range(N + 1)])
    assert np.abs(ch.pi.reshape(-1, 2) - levels).max() <= 1e-11
    assert ch.r == pytest.approx(inf['mean'], rel=1e-10)
    assert inf['tail'](N) <= 1e-13


def test_V4_poisson_and_augmented_methods_agree_short_and_long():
    ch = ctmc.Chain(F(17, 2), F(1, 2), ctmc.choose_N(F(17, 2), F(1, 2)))
    for h in (0.5, 5.0, 25 * ch.T_int):
        a, b = ch.V([h])[0], ch.V_aug(h)
        assert np.abs(a - b).max() <= 1e-8 * np.abs(b).max()


def test_V_short_horizon_is_backlog_times_h():
    ch = ctmc.Chain(F(7), F(1, 2), 80)
    h = 1e-5
    n = np.repeat(np.arange(81), 2)
    assert np.abs(ch.V([h])[0] / h - n)[:60].max() < 1e-2


def test_V9_mean_rollout_closed_form_matches_ode():
    a, mu = 6, 10
    for load, kappa, n, sigma in [(F(17, 2), F(1, 2), 0, 1), (F(17, 2), F(1, 2), 7, 1), (F(7), F(2), 3, -1),
                                  (F(31, 4), F(1, 50), 12, 1), (F(9), F(5), 0, 1)]:
        for h in (0.3, 4.0, 60.0):
            got = ctmc.m0_vhat(load, kappa, 20, [h])[0][2 * n + (sigma > 0)]

            def rhs(t, y):
                rate = float(load) + sigma * a * np.exp(-2 * t / float(kappa)) - mu
                q = y[0]
                dq = rate if q > 0 or rate > 0 else 0.0
                return [dq, max(q, 0.0)]
            sol = solve_ivp(rhs, (0, h), [n, 0.0], rtol=1e-11, atol=1e-12, max_step=0.01)
            assert got == pytest.approx(sol.y[1, -1], rel=1e-7, abs=1e-9)


def test_mean_rollout_infinite_horizon_and_exact_zero():
    v = ctmc.m0_vhat(F(7), F(1, 2), 10, [np.inf, 1e6])
    assert np.allclose(v[0], v[1], rtol=1e-12)
    assert v[0][0] == 0.0               # empty queue, low mode: drains at once, exactly zero


def test_V10_posterior_mean_matches_dense_expm():
    ch = ctmc.Chain(F(15, 2), F(1, 2), 40)
    rng = np.random.default_rng(1)
    vec = rng.normal(size=(ch.n, 2))
    got = ctmc.posterior_mean(ch, vec)
    P = expm(ch.Q.toarray() * 1.0)
    pi = ch.pi.reshape(-1, 2)
    push = (P @ vec).reshape(-1, 2, 2)                # (y, mode, column)
    want = (pi[:, :, None] * push).sum(axis=1) / pi.sum(axis=1)[:, None]
    assert np.abs(got - want).max() <= 1e-10 * np.abs(want).max()


def test_pair_sum_matches_brute_force_including_ties():
    rng = np.random.default_rng(2)
    wA, wB = rng.random(30), rng.random(25)
    uA, uB = rng.integers(-3, 4, 30).astype(float), rng.integers(-3, 4, 25).astype(float)
    vA, vB = rng.normal(size=30), rng.normal(size=25)
    for c in (0.0, 0.5):
        mass, value, tie = ctmc.pair_sum(wA, uA, vA, wB, uB, vB, c, tol=1e-12)
        gap = uA[:, None] + uB[None, :] + c
        W = wA[:, None] * wB[None, :]
        assert mass == pytest.approx((W * (gap < 0)).sum())
        assert value == pytest.approx((W * (gap < 0) * (vA[:, None] + vB[None, :] + c)).sum())
        assert tie == pytest.approx((W * (np.abs(gap) <= 1e-12)).sum())


def test_V1_no_managed_load_makes_all_four_losses_equal():
    out = ctmc.evaluate(F(7), F(15, 2), F(0), F(1, 2), [F(3)], control=True)
    row = out['h'][0]
    assert row['L00'] == row['L01'] == row['L10'] == row['L11']
    for k in ('G_S', 'G_M', 'G_SM', 'Gamma', 'S', 'M'):
        assert row[k] == 0.0


def test_V11_static_rule_follows_sign_of_delta():
    for lamA, lamB in ((F(7), F(15, 2)), (F(15, 2), F(7))):
        out = ctmc.evaluate(lamA, lamB, F(1), F(1, 2), [F(2)])
        assert (out['s'] < 0) == (lamB < lamA)


def test_heldout_amplitude_is_refused():
    with pytest.raises(ValueError):
        ctmc.evaluate(F(7), F(15, 2), F(1), F(1, 2), [F(2)], a=5)
    with pytest.raises(ValueError):
        ctmc.Chain(F(7), F(1, 2), 30, a=5)


def test_identities_and_inequalities_on_one_regime():
    out = ctmc.evaluate(F(7), F(15, 2), F(3, 2), F(1, 2), [F(4)])
    r = out['h'][0]
    assert r['G_SM'] == pytest.approx(r['G_S'] + r['M'], abs=1e-9)
    assert r['G_SM'] == pytest.approx(r['G_M'] + r['S'], abs=1e-9)
    assert r['Gamma'] == pytest.approx(r['S'] - r['G_S'], abs=1e-9)
    assert min(r['S'], r['M'], r['G_M']) >= -1e-9


def test_V8_simulated_backlog_cost_matches_exact_V():
    from experiments.explore_ctmc import mc
    from fractions import Fraction as F
    for state in ((0, 0), (6, 1)):
        mean, se, exact = mc.gillespie_V(F(15, 2), F(1, 2), 200, state, 3.0, 40000, seed=7)
        assert abs(mean - exact) <= 4 * se


def test_checkers_run_on_fake_runs(tmp_path, monkeypatch):
    """Schema smoke test of the locked scorers on copies of a control-regime output (V3_R1, excluded from scoring)."""
    import json as _json
    from experiments.explore_ctmc import check_asymptote, check_bridge
    base = ctmc.evaluate(F(7), F(15, 2), F(3, 2), F(1, 2), [F(4), F(40), F(400)], disagree=False)
    base.update(status='COMPLETED', tags={'sobol4': 'Q00000'})
    for stage, n in (('bridge', 3), ('xslice', 2), ('pslice', 2), ('asym', 2)):
        folder = tmp_path / 'runs' / stage
        folder.mkdir(parents=True)
        for i in range(n):
            d = dict(base, id=f'{stage}{i}')
            if stage != 'asym':
                d['h'] = [base['h'][i % 3]]
            (folder / f'{stage}{i}.json').write_text(_json.dumps(d, default=float))
    rows = [dict(id=f'asym{i}', h=r['h'], h_kappa=r['h_kappa'], h_Tint=r['h_Tint'], z_inf=base['asymptotic']['z_inf'],
                 z_pred_first_order=r['G_S'], F_old=0, F_new=0, M_pred_new=base['asymptotic']['M0_regret_new_pred'],
                 M_pred_old=0, x=0, kappa='1/2') for i in range(2) for r in base['h']]
    import pandas as _pd
    _pd.DataFrame(rows).to_csv(tmp_path / 'PREDICTIONS_asymptote_numbers.csv', index=False)
    monkeypatch.setattr(check_bridge, 'OUT', tmp_path)
    monkeypatch.setattr(check_asymptote, 'OUT', tmp_path)
    check_bridge.main()
    check_asymptote.main()
    assert (tmp_path / 'score_bridge.json').exists() and (tmp_path / 'score_asymptote.json').exists()


def test_deterministic_expm1_matches_libm_to_a_few_ulp():
    import math
    y = -np.concatenate([np.geomspace(1e-12, 800, 4000), [0.0, 0.3499, 0.35, 0.3501, 1.0, 744.0]])
    got = ctmc.det_expm1(y)
    want = np.array([math.expm1(v) for v in y])
    assert np.all(np.abs(got - want) <= 4 * np.spacing(np.abs(want)) + 1e-300)
    assert got[y == 0].tolist() == [0.0]


def test_m0_saturated_states_give_an_exact_tie():
    """Short horizon, both queues stay positive under both loads: the mean-rollout gaps cancel exactly (contract's
    certified tie), so Stay; never left to rounding."""
    hs = [0.1, math.inf]
    gA = ctmc.m0_gap(F(7), F(3, 2), F(1, 2), 80, hs, 'A')
    gB = ctmc.m0_gap(F(15, 2), F(3, 2), F(1, 2), 80, hs, 'B')
    hiA, hiB = gA[0][2 * 40:], gB[0][2 * 40:]          # n >= 40: no drain within 0.1 s
    assert (hiA == 0.0).all() and (hiB == 0.0).all()
    assert (gA[1] != 0).any()                          # infinite horizon: no saturation shift
    full = ctmc.m0_gap(F(7), F(3, 2), F(1, 2), 80, [0.1], 'A')[0] - 3 / 2 * 0.1 ** 2 / 2
    raw = (ctmc.m0_vhat(F(7), F(1, 2), 80, [0.1]) - ctmc.m0_vhat(F(17, 2), F(1, 2), 80, [0.1]))[0]
    assert np.allclose(full, raw, atol=1e-12)


def test_switching_cost_needs_the_stage_f_flag_and_c0_rows_are_unchanged():
    import json as _json
    from pathlib import Path as _P
    with pytest.raises(ValueError):
        ctmc.evaluate(F(7), F(71, 10), F(1), F(1, 5), [F(2)], c=F(1, 2))
    out = ctmc.evaluate(F(7), F(71, 10), F(1), F(1, 5), [F(2)], c=F(1, 2), allow_csw=True)
    assert out['parameters'][4] == '1/2'
    m0 = ctmc.evaluate_m0(F(7), F(71, 10), F(1), F(1, 5), [F(2)], c=F(1, 2), allow_csw=True)
    assert m0['parameters'][4] == '1/2'
    saved = _P(__file__).resolve().parents[1] / 'results/explore_ctmc/runs/xslice/X_u1_k1-5_hk50_x1-10.json'
    if saved.exists():
        old = _json.loads(saved.read_text())
        new = ctmc.evaluate(*(F(x) for x in old['parameters'][:4]), [F(h) for h in old['hs']])
        def sub(n, o):                        # restrict the new output to the keys the saved row already had
            return {k: sub(n[k], v) for k, v in o.items()} if isinstance(o, dict) else n
        for r_old, r_new in zip(old['h'], new['h']):
            r_old.pop('flags', None)          # added by scan.py when the row is written
            assert _json.dumps(r_old, default=float) == _json.dumps(sub(r_new, r_old), default=float)


def test_csw_checker_runs_on_fake_runs(tmp_path, monkeypatch):
    import json as _json
    import pandas as _pd
    from experiments.explore_ctmc import check_csw
    base = ctmc.evaluate(F(7), F(15, 2), F(3, 2), F(1, 2), [F(4), F(40), F(400)], disagree=False)
    base.update(status='COMPLETED')
    folder = tmp_path / 'runs' / 'csw'
    folder.mkdir(parents=True)
    rows = []
    for name in ('F_b1_c', 'F_b1_c0'):
        (folder / f'{name}.json').write_text(_json.dumps(dict(base, id=name), default=float))
        rows += [dict(id=name, h=r['h'], z_inf=base['asymptotic']['z_inf'], z_pred_first_order=r['G_S']) for r in base['h']]
    _pd.DataFrame(rows).to_csv(tmp_path / 'PREDICTIONS_csw_numbers.csv', index=False)
    monkeypatch.setattr(check_csw, 'OUT', tmp_path)
    check_csw.main()
    assert (tmp_path / 'score_csw.json').exists()


def test_d22_joint_law_has_the_right_marginals():
    stay = ctmc.Chain(F(17, 2), F(1, 2), 120)
    J = ctmc.joint_old_current(stay)                    # J[y, n, m] = P(Y = y, X = (n, m))
    pi = stay.pi.reshape(-1, 2)
    assert np.abs(J.sum(axis=0) - pi).max() <= 1e-12
    assert np.abs(J.sum(axis=(1, 2)) - pi.sum(axis=1)).max() <= 1e-12


def test_d22_conditional_means_obey_the_tower_property():
    stay = ctmc.Chain(F(17, 2), F(1, 2), 120)
    J = ctmc.joint_old_current(stay)
    v = np.random.default_rng(3).normal(size=stay.n)
    w, cond = ctmc.cond_on_backlog(J, v)
    p = J.sum(axis=(1, 2))
    old = ctmc.posterior_mean(stay, v)
    assert np.abs((w * cond).sum(axis=1) / p - old).max() <= 1e-10


def test_d22_decomposition_identities_and_signs():
    out = ctmc.evaluate_d22(F(7), F(15, 2), F(3, 2), F(1, 2), [F(4), F(40)])
    for r in out['h']:
        d = r['d22']
        assert d['F'] + d['V'] == pytest.approx(r['G_S'], abs=1e-9)
        assert d['F1'] + d['V1'] == pytest.approx(r['S'], abs=1e-9)
        assert min(d['F1'], d['V1']) >= -1e-9
        assert d['dropped_mass'] <= 1e-12


def test_d22_checker_runs_on_fake_runs(tmp_path, monkeypatch):
    import json as _json
    import pandas as _pd
    from experiments.explore_ctmc import check_d22
    base = ctmc.evaluate_d22(F(7), F(15, 2), F(3, 2), F(1, 2), [F(4), F(40), F(400)])
    base.update(status='COMPLETED')
    rows = []
    for stage in check_d22.STAGES[:2]:
        folder = tmp_path / 'runs_d22' / stage
        folder.mkdir(parents=True)
        (folder / 'X1.json').write_text(_json.dumps(dict(base, id='X1'), default=float))
        rows += [dict(stage=stage, id='X1', h=r['h'], z_inf=base['asymptotic']['z_inf'],
                      z_F_inf=base['d22_asymptotic']['z_F_inf'], z_V_inf=base['d22_asymptotic']['z_V_inf']) for r in base['h']]
    _pd.DataFrame(rows).to_csv(tmp_path / 'PREDICTIONS_d22_numbers.csv', index=False)
    monkeypatch.setattr(check_d22, 'OUT', tmp_path)
    check_d22.main()
    assert (tmp_path / 'score_d22.json').exists()


def test_knockout_twin_and_its_zero_fit_limit():
    out = ctmc.evaluate(F(7), F(15, 2), F(3, 2), F(1, 2), [F(4), F(1500)], disagree=False)
    asym = out['asymptotic']
    assert {'F_new_ko', 'F_old_ko', 'z_inf_ko', 'B_ko'} <= set(asym)
    long = out['h'][-1]
    assert abs(long['G_S_ko'] - asym['z_inf_ko']) <= 0.1 + 0.1 * abs(asym['z_inf_ko'])
    assert {'ko_new', 'ko_old'} <= set(long['regret'])


def test_state_dependence_is_disagreement_with_static():
    out = ctmc.evaluate(F(7), F(15, 2), F(3, 2), F(1, 2), [F(40)], disagree=False)
    r = out['h'][0]
    dep, sh = r['dep_static'], r['shares']
    for t in ('M1_new', 'M0_new', 'hybrid_new', 'ko_new', 'M1_old', 'M0_old', 'hybrid_old', 'ko_old'):
        want = sh[t] if sh['static'] == 0 else 1 - sh[t]
        assert dep[t] == pytest.approx(want)


def test_heldout_amplitudes_only_in_zero_fit_mode():
    m = ctmc.evaluate_m0(F(7), F(15, 2), F(1), F(1, 2), [F(4)], a=3)
    assert m['a'] == 3 and 'z_inf_ko' in m
    with pytest.raises(PermissionError):
        ctmc.evaluate(F(7), F(15, 2), F(1), F(1, 2), [F(4)], a=3)
    with pytest.raises(PermissionError):
        ctmc.Chain(F(8), F(1, 2), 200, a=3).V([1.0])
    with pytest.raises(ValueError):
        ctmc.evaluate_m0(F(7), F(15, 2), F(1), F(1, 2), [F(4)], a=5)
    with pytest.raises(ValueError):                          # low mode would go negative
        ctmc.evaluate_m0(F(7), F(8), F(1), F(1, 2), [F(4)], a=F(15, 2))


def test_amplitude_six_m0_rows_are_unchanged():
    import json as _json
    from pathlib import Path as _P
    saved = _P(__file__).resolve().parents[1] / 'results/explore_ctmc/m0/xslice/X_u1_k1-5_hk50_x1-10.json'
    if saved.exists():
        old = _json.loads(saved.read_text())
        new = ctmc.evaluate_m0(*(F(x) for x in old['parameters'][:4]), [F(h) for h in old['hs']])
        for k in ('z_inf', 's', 'r_min', 'M0_regret_new_pred'):
            assert new[k] == old[k]
        assert _json.dumps(new['h'], default=float) == _json.dumps(old['h'], default=float)


def test_ko_checker_runs_on_fake_runs(tmp_path, monkeypatch):
    import json as _json
    import pandas as _pd
    from experiments.explore_ctmc import check_ko
    d22 = ctmc.evaluate_d22(F(7), F(15, 2), F(3, 2), F(1, 2), [F(4), F(40), F(400)])
    plain = ctmc.evaluate(F(7), F(15, 2), F(3, 2), F(1, 2), [F(4), F(40), F(400)], disagree=False)
    rows = []
    for stage, base in zip(check_ko.STAGES, (d22, plain)):
        folder = tmp_path / 'runs_ko' / stage
        folder.mkdir(parents=True)
        (folder / 'K1.json').write_text(_json.dumps(dict(base, id='K1', status='COMPLETED'), default=float))
        rows += [dict(stage=stage, id='K1', h=r['h'], z_inf_ko=base['asymptotic']['z_inf_ko'],
                      z_pred1_ko=r['z_pred_first_order_ko']) for r in base['h']]
    _pd.DataFrame(rows).to_csv(tmp_path / 'PREDICTIONS_ko_numbers.csv', index=False)
    monkeypatch.setattr(check_ko, 'OUT', tmp_path)
    monkeypatch.setattr(check_ko.sys, 'argv', ['check_ko'])
    check_ko.main()
    assert (tmp_path / 'score_ko.json').exists()


def _fake_l72(tmp_path, unresolved_every=0):
    import json as _json
    import shutil
    import pandas as _pd
    root = _P_root()
    (tmp_path / 'l72').mkdir()
    for f in ('ZEROFIT_a3.csv', 'ZEROFIT_a7p5.csv', 'compare_amplitudes.json'):
        shutil.copy(root / 'results/explore_ctmc/l72' / f, tmp_path / 'l72' / f)
    rng = np.random.default_rng(0)
    for tag in ('a3', 'a7p5'):
        z = _pd.read_csv(tmp_path / 'l72' / f'ZEROFIT_{tag}.csv', dtype={'h': str})
        z = z[z.status == 'COMPLETED']
        for (stage, cid), g in z.groupby(['stage', 'id']):
            folder = tmp_path / 'runs_l72' / stage
            folder.mkdir(parents=True, exist_ok=True)
            k = len(list(folder.glob('*.json')))
            if unresolved_every and k % unresolved_every == 0:
                (folder / f'{cid}.json').write_text(_json.dumps(dict(id=cid, status='UNRESOLVED')))
                continue
            rows = []
            for r in g.itertuples():
                gs = r.z_pred1 + rng.normal(0, 0.02)
                row = dict(h=r.h, G_S=gs, S=abs(rng.normal(0, .3)), M=abs(rng.normal(0, 1)), h_kappa=r.h_kappa,
                           h_Tint=r.h_Tint, regret=dict(static=abs(rng.normal(0, .02)), ko_new=10.0, M0_new=2.0),
                           shares=dict(M0_old=0.9, M0_new=0.7))
                if max(r.N_A, r.N_B) <= 3000 and stage.endswith(('asym', 'sobol')):
                    row['d22'] = dict(F=0.8 * gs)
                rows.append(row)
            (folder / f'{cid}.json').write_text(_json.dumps(dict(id=cid, status='COMPLETED', s=float(g.s.iloc[0]), h=rows)))


def _P_root():
    from pathlib import Path as _P
    return _P(__file__).resolve().parents[1]


def test_l72_checker_scores_fake_truth(tmp_path, monkeypatch):
    import json as _json
    from experiments.explore_ctmc import check_l72
    _fake_l72(tmp_path)
    monkeypatch.setattr(check_l72, 'OUT', tmp_path)
    check_l72.main()
    out = _json.loads((tmp_path / 'score_l72.json').read_text())
    assert out['a3']['L72-1']['verdict'] == 'PASS'          # fake G_S = z_pred1 + 0.02 noise
    assert out['a3']['L72-7']['verdict'] in ('PASS', 'INCONCLUSIVE')
    assert set(out['cross_amplitude']) == {'L72-4'}


def test_l72_checker_unresolved_rule(tmp_path, monkeypatch):
    import json as _json
    from experiments.explore_ctmc import check_l72
    _fake_l72(tmp_path, unresolved_every=5)                 # 20% of cases unresolved -> every gate INCONCLUSIVE
    monkeypatch.setattr(check_l72, 'OUT', tmp_path)
    check_l72.main()
    out = _json.loads((tmp_path / 'score_l72.json').read_text())
    assert out['a3']['L72-3']['verdict'] == 'INCONCLUSIVE' and out['a7p5']['L72-2']['verdict'] == 'INCONCLUSIVE'


def test_l72_checker_fields_exist_in_real_output():
    out = ctmc.evaluate_d22(F(7), F(15, 2), F(3, 2), F(1, 2), [F(40)])
    r = out['h'][0]
    for k in ('G_S', 'S', 'M', 'h_kappa', 'h_Tint'):
        assert k in r
    assert {'static', 'ko_new', 'M0_new'} <= set(r['regret']) and {'M0_old', 'M0_new'} <= set(r['shares'])
    assert 'F' in r['d22'] and 's' in out
