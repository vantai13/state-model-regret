"""Doan Van Tai — tests for the L7.5 telemetry-age axis (ctmc-v1, a = 6) [EXPLORATION ONLY; AI (Claude) theo ủy quyền]."""
from fractions import Fraction as F
import json
from pathlib import Path

import numpy as np
import pytest
import scipy.linalg

from experiments.explore_ctmc import ctmc, tau as T5

ROOT = Path(__file__).resolve().parents[1]
CT1 = T5.CONTROL_REGIMES_L75['CT1']
CHEAP = (F(7), F(13, 2), F(1), F(1, 5))           # pslice regime, small N; not a control


def test_at_tau_restores_v1_names_even_after_an_error():
    with pytest.raises(RuntimeError):
        with T5.at_tau(F(1, 3)):
            assert ctmc.TAU == F(1, 3) and not T5.restored()
            raise RuntimeError('boom')
    assert T5.restored()


def test_tau_one_is_v1_bit_for_bit():
    hs = [F(2), F(10)]
    v1 = ctmc.evaluate_m0(*CHEAP, hs)
    with T5.at_tau(F(1, 7)):
        ctmc.evaluate_m0(*CHEAP, hs)                  # a different tau in between must leave no state behind
    got = T5.evaluate_m0(*CHEAP, hs, 1)
    assert got['z_inf'] == v1['z_inf']
    assert [r['F_old'] for r in got['h']] == [r['F_old'] for r in v1['h']]
    assert [r.get('z_pred_first_order') for r in got['h']] == [r.get('z_pred_first_order') for r in v1['h']]


def test_tau_changes_only_the_old_state():
    a = T5.evaluate_m0(*CHEAP, [F(5)], F(1, 10))
    b = T5.evaluate_m0(*CHEAP, [F(5)], F(10))
    assert [r['F_new'] for r in a['h']] == [r['F_new'] for r in b['h']]
    assert a['F_new_ko'] == b['F_new_ko'] and a['F_old_ko'] != b['F_old_ko']
    assert a['h'][-1]['F_old'] != b['h'][-1]['F_old']


def test_truth_guard(monkeypatch, tmp_path):
    monkeypatch.setattr(T5, 'LOCKS_L75', tmp_path / 'locks_l75.json')
    with pytest.raises(PermissionError):
        T5.evaluate(*CHEAP, [F(2)], F(1, 2))
    with pytest.raises(PermissionError):                 # a direct ctmc call inside the context is guarded too
        with T5.at_tau(F(1, 2), CHEAP):
            ctmc.evaluate(*CHEAP, [F(2)], disagree=False)
    T5.evaluate(*CT1, [F(2)], F(1, 2), disagree=False)   # control regime
    T5.evaluate(*CHEAP, [F(2)], 1, disagree=False)       # tau = 1 is ctmc-v1
    assert T5.restored()


def test_vmemo_does_not_change_truth():
    memo = {}
    a = T5.evaluate(*CT1, [F(3)], F(1, 4), disagree=False, vmemo=memo)
    b = T5.evaluate(*CT1, [F(3)], F(2), disagree=False, vmemo=memo)
    c = T5.evaluate(*CT1, [F(3)], F(2), disagree=False)
    assert memo and json.dumps(b, default=str) == json.dumps(c, default=str)
    assert a['h'][0]['L11'] == b['h'][0]['L11'] and a['h'][0]['L00'] != b['h'][0]['L00']


@pytest.mark.parametrize('t', [F(1, 100), F(1, 3), F(3), F(30)])
def test_posterior_matches_dense_expm(t):
    lamA, lamB, u, kappa = CT1
    N = ctmc.choose_N(lamA + u, kappa)
    st = ctmc.chain(lamA + u, kappa, N)
    v = np.random.default_rng(0).standard_normal((st.n, 3))
    with T5.at_tau(t):
        got = ctmc.posterior_mean(st, v)
    P = scipy.linalg.expm(st.Q.toarray() * float(t))
    pi = st.pi.reshape(-1, 2)
    want = (pi[:, :, None] * (P @ v).reshape(-1, 2, 3)).sum(axis=1) / pi.sum(axis=1)[:, None]
    assert np.abs(got - want).max() <= 1e-10 * np.abs(v).max()


def test_joint_marginal_and_no_disk_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(ctmc, 'D22_CACHE', tmp_path / 'cache')
    lamA, lamB, u, kappa = CT1
    N = ctmc.choose_N(lamA + u, kappa)
    st = ctmc.chain(lamA + u, kappa, N)
    with T5.at_tau(F(5, 2)):
        J = ctmc.joint_old_current(st)
    assert np.abs(J.sum(axis=0) - st.pi.reshape(-1, 2)).max() <= 1e-12
    assert np.abs(J.sum(axis=(1, 2)) - st.pi.reshape(-1, 2).sum(axis=1)).max() <= 1e-12
    assert not (tmp_path / 'cache').exists()


def test_case_lists_exclude_controls_and_seen_tuples():
    folder = ROOT / 'results/explore_ctmc/cases_l75'
    if not folder.exists():
        pytest.skip('case lists not written yet')
    from experiments.explore_ctmc import design_l75
    sobol = json.loads((folder / 'sobol.json').read_text())
    seen = design_l75.seen_tuples()
    for c in sobol:
        key = tuple(F(x) for x in c['parameters'][:4])
        assert key not in seen and not T5.is_control(key)
    for name in ('sobol', 'old', 'xs'):
        for c in json.loads((folder / f'{name}.json').read_text()):
            assert not T5.is_control(c['parameters'])
            assert max(un['est_truth'] for un in c['units']) <= design_l75.CAP / 2


def test_scan_tau_truth_refused_without_locks(tmp_path, monkeypatch):
    from experiments.explore_ctmc import scan_tau
    monkeypatch.setattr(scan_tau, 'LOCKS_L75', tmp_path / 'locks_l75.json')
    with pytest.raises(SystemExit):
        scan_tau.check_l75_locks('sobol')


def test_run_unit_zero_fit_writes_a_completed_row(tmp_path):
    from experiments.explore_ctmc import scan_tau
    case = dict(id='CHEAP', parameters=[str(x) for x in CHEAP] + ['0'], hs=['2', '10'], tau='1/2',
                unit=dict(tau='1/2', d22=True, est_truth=1.0), tags={})
    path = tmp_path / 'u.json'
    import multiprocessing
    proc = multiprocessing.get_context('fork').Process(target=scan_tau.run_unit, args=((case, path, 120, 'zf'),))
    proc.start()                                     # in a child: run_unit sets RLIMIT_CPU on its own process
    proc.join()
    d = json.loads(path.read_text())
    assert d['status'] == 'COMPLETED' and d['tau'] == '1/2' and 'z_F_inf' in d and d['kind'].startswith('D22')


# ---------------------------------------------------------------- check_l75 on fake data (no truth at tau != 1 exists)
def _fake_l75(n_reg=12, dose_up=0.0, s_down=0.0, onset_err=0.0, edge_shift=0.0, undone=0, wrong_gs=None):
    """Fake merged frame: n_reg prior-correct regimes (harm growing with tau), n_reg prior-wrong regimes (help at large
    tau), 12 x-slice families x 3 tau. Returns (frame, eligibility table)."""
    import pandas as pd
    rows = []
    taus = [float(t) for t in T5.TAU_GRID]
    for r in range(2 * n_reg):
        correct = r < n_reg
        for hm in (float(h) for h in T5.H_GRID):
            for k, t in enumerate(taus):
                z = (-1.0 - 0.1 * k) if correct else (0.5 + 0.1 * k)
                g = z + onset_err + (dose_up * k if correct else 0.0)
                if not correct and t == 10.0 and wrong_gs is not None:
                    g = wrong_gs
                rows.append(dict(stage='sobol', id=f'R{r}', h=f'{hm}', tau=f'{t}', tau_s=t, tau_mult=t, h_mult=hm,
                                 z_pred1=z, G_S=g, S=0.5 + 0.01 * k - s_down * k, prior_correct=correct,
                                 stratum='neg' if correct else 'band', done=not (r < undone), x=-0.5, family='f'))
    elig = []
    for fam in range(12):
        for t in (float(x) for x in T5.XS_TAU):
            elig.append(dict(family=f'fam{fam}', tau_mult=t, eligible=True))
            for x in np.arange(-0.5, 1.0, 0.05):
                x = round(float(x), 2)
                if x == 0:
                    continue
                z = 0.25 - x
                rows.append(dict(stage='xs', id=f'X{fam}_{x}', h='10', tau=f'{t}', tau_s=t, tau_mult=t, h_mult=10.0,
                                 z_pred1=z, G_S=z - edge_shift, S=0.1, prior_correct=True, stratum='xs', done=True,
                                 x=x, family=f'fam{fam}'))
    return pd.DataFrame(rows), pd.DataFrame(elig)


def _verdicts(fake):
    from experiments.explore_ctmc import check_l75
    m, elig = fake
    return {k: r['verdict'] for k, r in check_l75.score(m, elig).items() if r['verdict'] != 'REPORT'}


def test_check_l75_all_pass_and_single_failures():
    assert _verdicts(_fake_l75()) == {'L75-1': 'PASS', 'L75-2': 'PASS', 'L75-3': 'PASS', 'L75-4': 'PASS'}
    assert _verdicts(_fake_l75(dose_up=0.2))['L75-1'] == 'FAIL'      # 1a: harm shrinks as tau grows
    assert _verdicts(_fake_l75(wrong_gs=-0.3))['L75-1'] == 'FAIL'    # 1b: prior wrong but fresh state does not help
    assert _verdicts(_fake_l75(s_down=0.05))['L75-3'] == 'FAIL'      # S decreases with tau
    assert _verdicts(_fake_l75(onset_err=0.5))['L75-2'] == 'FAIL'
    assert _verdicts(_fake_l75(edge_shift=0.05))['L75-4'] == 'FAIL'  # truth edge 0.05 left of the zero-fit edge


def test_check_l75_unresolved_series_give_inconclusive():
    v = _verdicts(_fake_l75(undone=3))                               # 3 of 24 regimes unresolved (> 10%)
    assert v['L75-1'] == 'INCONCLUSIVE' and v['L75-3'] == 'INCONCLUSIVE'


def test_amplitude_filter_never_drops_a_failing_series():
    """(a) mentor review §3a: a series that fails (a step drop > TOL_S) is never classified 'flat'."""
    from experiments.explore_ctmc import check_l75
    rng = np.random.default_rng(7)
    for _ in range(20000):
        v = np.cumsum(rng.normal(0, rng.choice([1e-4, 3e-3, 1e-2, 0.1]), 8))
        c = check_l75.s_class(v)
        if (np.diff(v) < -check_l75.TOL_S).any():
            assert c == 'fail'
        if c == 'flat':
            assert v.max() - v.min() < check_l75.AMP_MIN and (np.diff(v) >= -check_l75.TOL_S).all()
    assert check_l75.AMP_MIN <= check_l75.TOL_S


def test_l75_4_eligibility_reproduces_the_frozen_eight_series():
    """(b) the eligibility rule applied to ZEROFIT_tau.csv gives the frozen table: 6 families at tau = T_int and the
    two u = 2 families at tau = 0.1 T_int."""
    import pandas as pd
    l75 = ROOT / 'results/explore_ctmc/l75'
    if not (l75 / 'L75_4_ELIGIBILITY.csv').exists():
        pytest.skip('eligibility table not frozen yet')
    from experiments.explore_ctmc import prefreeze_l75
    got = prefreeze_l75.eligibility(pd.read_csv(l75 / 'ZEROFIT_tau.csv', dtype={'h': str, 'tau': str}))
    frozen = pd.read_csv(l75 / 'L75_4_ELIGIBILITY.csv')
    ok = {(r.family, float(r.tau_mult)) for r in got.itertuples() if r.eligible}
    assert ok == {(r.family, float(r.tau_mult)) for r in frozen.itertuples() if r.eligible}
    fams = set(got.family)
    assert ok == {(f, 1.0) for f in fams} | {('u2_lA13/2_k1', 0.1), ('u2_lA13/2_k1/5', 0.1)}


def test_l75_1_reads_the_frozen_prior_bit():
    """(c) load() attaches PRIOR_BIT.csv; 1a has 174 series over 58 regimes, 1b 98 rows over 33 regimes."""
    l75 = ROOT / 'results/explore_ctmc/l75'
    if not (l75 / 'PRIOR_BIT.csv').exists():
        pytest.skip('prior bit not frozen yet')
    from experiments.explore_ctmc import check_l75
    res = check_l75.score(check_l75.load())
    p = res['L75-1']['parts']
    assert (p['1a prior đúng']['eligible'], p['1a prior đúng']['regimes']) == (174, 58)
    assert (p['1b prior sai']['eligible'], p['1b prior sai']['regimes']) == (98, 33)
    assert res['L75-3']['eligible'] == 546 and res['L75-4']['eligible'] == 8


def test_nearest_grid_multiple_handles_rounding():
    from experiments.explore_ctmc import check_l75
    got = check_l75.nearest([6.998, 7.002, 14.9, 0.2996], T5.H_GRID)
    assert got.tolist() == [7.0, 7.0, 15.0, 0.3]


def test_grid_tau_rounding_to_one_second_stays_on_the_grid():
    folder = ROOT / 'results/explore_ctmc/cases_l75'
    if not folder.exists():
        pytest.skip('case lists not written yet')
    case = next(c for c in json.loads((folder / 'sobol.json').read_text()) if c['id'] == 'TB0001')
    gm = T5.tau_grid_map(case, 'sobol')
    assert gm['1'] == 0.3 and len(gm) == 8 and len(case['taus']) == 8      # 0.3 T_int rounds to exactly 1 s
