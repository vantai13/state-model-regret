"""Doan Van Tai — X-CTMC analytic controls; no panel truth or scoring."""
from fractions import Fraction as F
import itertools
import json
import math

import numpy as np
import pytest
from scipy import sparse
from scipy.linalg import expm
from scipy.sparse.linalg import expm_multiply

from experiments.explore_ctmc import ctmc
from experiments.letter import shat2
from experiments.letter import x_ctmc as x


def small_regime():
    return x.Regime("CONTROL_001", x.PathSpec(1.8, 5., 1.2, .5),
                    x.PathSpec(2.8, 8., 1.8, 1.), .4)


@pytest.fixture(scope="module")
def small():
    return x.prepare(small_regime(), Ns=dict(A=3, B=4))


@pytest.mark.parametrize("case_index", [0, 1])
def test_appendix_A_equivalence_to_two_old_regimes_at_amplitude6_mu10(case_index):
    cases = json.loads((x.ROOT/"results/explore_ctmc/cases/asym.json").read_text())
    case = cases[case_index]
    la, lb, u, k, _ = map(F, case["parameters"])
    hs = [F(1), F(3), F(10)]
    old = ctmc.evaluate(la, lb, u, k, hs, a=6, arrays=True, disagree=False)
    regime = x.Regime(case["id"], x.PathSpec(float(la), 10., 6., float(k)),
                      x.PathSpec(float(lb), 10., 6., float(k)), float(u))
    p = x.prepare(regime)
    # The compatibility option reproduces the old backlog-only observation;
    # all real X-CTMC commands use the full old state, as the brief specifies.
    new = x.evaluate(p, list(map(float, hs)), [1.], None, rules=("M0",), observation="backlog")
    assert p["truncation"]["A"]["N"] == old["N"]["A"]
    assert p["truncation"]["B"]["N"] == old["N"]["B"]
    legacy = dict(Ast=ctmc.Chain(la+u,k,old["N"]["A"],a=6,mu=10),
                  Asw=ctmc.Chain(la,k,old["N"]["A"],a=6,mu=10),
                  Bst=ctmc.Chain(lb,k,old["N"]["B"],a=6,mu=10),
                  Bsw=ctmc.Chain(lb+u,k,old["N"]["B"],a=6,mu=10))
    for key, old_chain in legacy.items():
        np.testing.assert_allclose(p["chains"][key].V(hs), old_chain.V(hs), rtol=1e-9, atol=1e-12)
    for side in ("A", "B"):
        dh = x.fluid_gap(getattr(regime, side), regime.u, old["N"][side], list(map(float,hs))+[math.inf], side)
        np.testing.assert_allclose(dh, old["_arrays"]["dh"+side], rtol=1e-9, atol=1e-12)
    for old_row, new_row in zip(old["h"], new["rows"]):
        assert new_row["G_S_pct_C_ref"] == pytest.approx(old_row["G_S"], rel=1e-9, abs=1e-12)
        assert new_row["C_ref"] == pytest.approx(old_row["Cref"], rel=1e-9)


def test_independent_chain_value_matches_augmented_generator_and_unsorted_horizons(small):
    chain = small["chains"]["Ast"]
    hs = [1.3, 0., .12, 1.3]
    got = chain.V(hs)
    qa = sparse.bmat([[chain.Q, sparse.csr_matrix(chain.f[:,None])],
                      [None, sparse.csr_matrix((1,1))]]).tocsr()
    unit = np.zeros(chain.n+1)
    unit[-1] = 1.
    for i,h in enumerate(hs):
        np.testing.assert_allclose(got[i], expm_multiply(qa*h, unit)[:-1], atol=8e-14)


def test_full_posterior_is_exact_semigroup_and_converges_to_zero_mode(small):
    chain = small["chains"]["Ast"]
    sigma = np.tile([-1.,1.], chain.N+1)
    tau = .23
    np.testing.assert_allclose(x.posterior(chain, sigma, tau), expm(chain.Q.toarray()*tau)@sigma, atol=3e-15)
    np.testing.assert_allclose(x.posterior(chain, sigma, 30.), 0., atol=1e-12)
    np.testing.assert_array_equal(x.posterior(chain, sigma, 0.), sigma)


def test_true_stale_cost_uses_old_current_markov_coupling(small):
    p = small
    h, tau = .7, .2
    result = x.evaluate(p, [h], [tau], .13, rules=("M0",))
    row = result["rows"][0]
    ch = p["chains"]
    a,b = ch["Ast"], ch["Bst"]
    da = ch["Asw"].V([h])[0]-a.V([h])[0]
    db = ch["Bsw"].V([h])[0]-b.V([h])[0]
    d = x.decision_vectors(p, [h], tau, .13)
    pa,pb = expm(a.Q.toarray()*tau), expm(b.Q.toarray()*tau)
    direct = 0.
    for ya,yb,xa,xb in itertools.product(range(a.n), range(b.n), range(a.n), range(b.n)):
        fresh = d["fresh"]["A"][0,xa]+d["fresh"]["B"][0,xb] < 0
        stale = d["stale"]["A"][0,ya]+d["stale"]["B"][0,yb] < 0
        direct += a.pi[ya]*b.pi[yb]*pa[ya,xa]*pb[yb,xb]*(int(stale)-int(fresh))*(da[xa]+db[xb])
    assert row["G_S"] == pytest.approx(direct, abs=5e-15)


def test_identical_rules_have_zero_GS_and_zero_age_equals_fresh(small):
    result = x.evaluate(small, [.2,.7], [0.,.2], -.1,
                        rules=("M0","Stationary_hat","Pool"))
    for row in result["rows"]:
        if row["rule"] in ("Stationary_hat","Pool") or row["tau"] == 0:
            assert row["G_S"] == 0.
            assert row["p_new"] == pytest.approx(row["p_old"], abs=2e-14)


def test_long_horizon_identity_GS_over_h_converges_to_s_deltaF(small):
    p = small
    result = x.evaluate(p, [20.,200.], [.4], None, rules=("M0",))
    asym = result["asymptotic_m0"]["0.4"]
    first,last = result["rows"]
    # Frozen infinite-horizon policies yield slope plus B_inf/h. Here all
    # fluid queues have drained by h=20, and the exact remainder decays.
    assert abs(last["G_S"]/200-asym["slope"]) < abs(first["G_S"]/20-asym["slope"])
    assert last["G_S"] == pytest.approx(200*asym["slope"]+asym["B_inf"], abs=2e-11)


@pytest.mark.parametrize("theta", x.THETAS)
def test_TH_and_MLU_match_literal_utilization_formula_even_with_mode_overload(small, theta):
    d = x.decision_vectors(small, [.7], .23, None)
    r = small["regime"]
    for side in ("fresh","stale"):
        mode = ({s:np.tile([-1.,1.], small["chains"][s+"st"].N+1) for s in ("A","B")}
                if side == "fresh" else d["old_mode"])
        ua0,ua1 = x.utilization(r.A, mode["A"], r.u, "A")
        ub0,ub1 = x.utilization(r.B, mode["B"], r.u, "B")
        ni = x.rule_inputs(small, d, f"TH_{theta:g}", side, 0, .7)
        mi = x.rule_inputs(small, d, "MLU", side, 0, .7)
        for a,b in itertools.product(range(len(ua0)),range(len(ub0))):
            got = x.sampled_decisions(ni,np.array([a]),np.array([b]))[0]
            assert got == (ua0[a]>theta and ub1[b]<ua0[a])
            assert bool(x.sampled_decisions(mi,np.array([a]),np.array([b]))[0]) == (
                max(ua1[a],ub1[b]) < max(ua0[a],ub0[b]))


def test_TH_at_or_above1_has_counterexample_under_allowed_MMPP_overload():
    # This documents the literal contradiction in DESIGN §8. No clipping or
    # theta>=1 sentinel is silently added to its §4 scientific rule.
    path_a = x.PathSpec(3.,5.,2.4,1.)
    path_b = x.PathSpec(2.,5.,.4,1.)
    ua0,_ = x.utilization(path_a,np.array([1.]),.3,"A")
    _,ub1 = x.utilization(path_b,np.array([-1.]),.3,"B")
    assert ua0[0] > 1 and ub1[0] < ua0[0]
    assert bool((ua0>1.) & (ub1<ua0))


@pytest.mark.xfail(strict=True, reason="DESIGN §8 contradicts §4 when an allowed MMPP high-mode rate exceeds mu; literal §4 retained pending author clarification")
def test_requested_theta_ge1_never_switch_sanity_from_design_section8():
    ua0,ub1=np.array([1.14]),np.array([.38])
    inputs=x.threshold_inputs(ua0,ub1,1.)
    assert not x.sampled_decisions(inputs,np.array([0]),np.array([0]))[0]


def test_utilization_null_averages_max_over_modes_instead_of_max_over_means():
    r=x.Regime("NULL",x.PathSpec(3.,5.,2.4,1.),x.PathSpec(2.,5.,.4,1.),.3)
    values=[]
    for ma,mb in itertools.product((-1,1),repeat=2):
        values.append(max((r.A.load+r.A.alpha*ma)/r.A.mu,
                          (r.B.load+r.B.alpha*mb+r.u)/r.B.mu)-
                      max((r.A.load+r.A.alpha*ma+r.u)/r.A.mu,
                          (r.B.load+r.B.alpha*mb)/r.B.mu))
    assert x.utilization_null(r)==pytest.approx(sum(values)/4)
    assert x.utilization_null(r)!=pytest.approx(x.parameter_comparison(r)["s_U"])


def test_threshold_sorted_aggregate_and_ties_match_dense_conjunction():
    wa,wb = np.array([.2,.3,.5]),np.array([.3,.7])
    ua0,ub1 = np.array([.5,.6,.9]),np.array([.5,.9])
    va,vb = np.array([-1.,2.,.1]),np.array([.3,-.7])
    theta=.5
    ni=dict(a=-ua0,b=ub1,gate=ua0>theta,boundary=ua0==theta)
    mass,value,ties=x.policy_sum(wa,wb,ni,va,vb)
    decision=np.maximum(theta-ua0[:,None],ub1[None,:]-ua0[:,None])
    weights=wa[:,None]*wb[None,:]
    assert mass == pytest.approx(float(np.sum(weights*(decision<0))))
    assert value == pytest.approx(float(np.sum(weights*(va[:,None]+vb[None,:])*(decision<0))))
    assert ties == pytest.approx(float(np.sum(weights*(decision==0))))


@pytest.mark.parametrize("a,b,gate", [
    ([-2.,-1.],[0.,.2],None),
    ([1.,2.],[-.1,0.],None),
    ([-1.,1.],[0.,.2],None),
    ([-2.,1.],[0.,.2],[False,False]),
    ([-2.,1.],[0.,.2],[False,True]),
])
def test_constant_action_certificate_matches_full_state_enumeration(a,b,gate):
    inputs=dict(a=np.array(a),b=np.array(b))
    if gate is not None:
        inputs["gate"]=np.array(gate)
    actions=[bool((inputs["b"][j] < -inputs["a"][i]) and (gate is None or gate[i]))
             for i,j in itertools.product(range(len(a)),range(len(b)))]
    expected=int(actions[0]) if len(set(actions))==1 else None
    assert x.constant_action(inputs)==expected


def test_constant_utilization_rules_have_exact_zero_GS_not_a_roundoff_sign():
    r=x.Regime("CONSTANT",x.PathSpec(3.,5.,.2,1.),x.PathSpec(1.,10.,.2,1.),.5)
    p=x.prepare(r,Ns=dict(A=3,B=4))
    result=x.evaluate(p,[.7],[1.1],None,rules=("MLU","TH_0.5","TH_0.9"))
    for row in result["rows"]:
        assert row["G_S"]==0.
        assert row["L_fresh"]==row["L_stale"]
        expected=0 if row["rule"]=="TH_0.9" else 1
        assert row["constant_action_fresh"]==row["constant_action_stale"]==expected
        assert row["p_new"]==row["p_old"]==float(expected)


def test_grid_64_balanced_reproducible_and_excludes_legacy_heldout():
    grid,meta=x.generate_grid()
    assert [r.record() for r in grid] == [r.record() for r in x.generate_grid()[0]]
    assert len(grid)==64 and len({r.id for r in grid})==64
    assert meta["accepted"] == dict(agree=32,disagree=32)
    assert len(set(x.SEEDS.values()))==4
    for r in grid:
        c=x.parameter_comparison(r)
        assert c["stratum"]==r.stratum
        assert all(.2<=rho<=.9 for rho in c["rho_stay"]+c["rho_switch"])
        assert not x.heldout_collision(r)
        for p in (r.A,r.B):
            assert p.mu in (5.,10.,20.) and p.kappa in (1.,5.,20.)
            assert any(math.isclose(p.alpha/p.load,a) for a in (.2,.5,.8))


def test_truncation_certifies_both_action_tails_in_heterogeneous_regime():
    p=x.prepare(small_regime())
    for side in ("A","B"):
        info=p["truncation"][side]
        assert all(a["selector_tail"]<=x.TAIL for a in info["actions"].values())
        assert all(info["N"]>=a["selector_N"] for a in info["actions"].values())


def test_uniformization_operator_and_event_chunks_equal_exact_generator(small):
    ch=small["chains"]["Bst"]
    matrix=np.zeros((ch.n,ch.n))
    for state in range(ch.n):
        load=ch.load+ch.alpha*(2*(state%2)-1)
        cut=sorted(set([0.,(1/ch.kappa)/ch.gamma,
                        (1/ch.kappa+load)/ch.gamma,(1/ch.kappa+load+ch.mu)/ch.gamma,1.]))
        for lo,hi in zip(cut,cut[1:]):
            target=x.uniformized_events(ch,np.array([.5*(lo+hi)]),state)[0]
            matrix[state,target]+=hi-lo
    np.testing.assert_allclose(matrix,np.eye(ch.n)+ch.Q.toarray()/ch.gamma,atol=2e-16)
    times=np.r_[0.,np.linspace(.001,3.,80)]
    a,ia=x.sample_at_times(ch,times,np.random.default_rng(2611204),chunk_events=7)
    b,ib=x.sample_at_times(ch,times,np.random.default_rng(2611204),chunk_events=200000)
    np.testing.assert_array_equal(a,b)
    assert ia==ib


def test_2000_pairs_use_exact_requested_age_and_finite_100Tint_history(small):
    y,z,info=x.history_pairs(small["chains"]["Ast"],.1,3,np.random.default_rng(2611204))
    assert y.shape==z.shape==(2000,)
    assert info["W"]==10. and info["tau"]==pytest.approx(.3)
    assert not info["independent_trials"]


def test_finite_record_estimator_reduces_to_literal_W2_mu10():
    p=x.PathSpec(7.,10.,6.,.5)
    ours=x.estimate_path(p,8.,-1.,.1,np.random.default_rng(2611204),W=2.)
    old=shat2.estimate_path(8.,-1.,6.,.5,.1,np.random.default_rng(2611204),W=2.)
    for key in ("count_sha256_le_i4","lambda_hat","alpha_hat","kappa_hat", "stay_load_hat",
                "switch_load_hat","autocovariances","status"):
        assert ours[key]==old[key]
    assert ours["fallback"] is None


def test_missing_estimator_retains_other_rules_without_true_s_fallback(small):
    result=x.evaluate(small,[.4],[.2],None)
    invalid=[r for r in result["rows"] if r["status"]=="INVALID_ESTIMATOR"]
    assert {r["rule"] for r in invalid}=={"Hybrid_hat","Stationary_hat"}
    assert len(result["rows"])==10
    assert all(r["s_hat"] is None for r in result["rows"])


def test_predict_helpers_never_request_chain_V(monkeypatch,small):
    def forbidden(*args,**kwargs):
        raise AssertionError("finite-h truth forbidden during predictions")
    monkeypatch.setattr(x.Chain,"V",forbidden)
    d=x.decision_vectors(small,[.2,.7],.2,None)
    assert d["fresh"]["A"].shape[0]==3
    assert x.asymptotic_m0(small,d,.2)["slope"] is not None


def test_pilot_selects_four_largest_state_products_and_cost_only_projection():
    metadata=[dict(id=f"x{i}",state_pair=i*10,work=dict(values=float(i),posterior=float(i),pairs=float(i),training=float(i)))
              for i in range(1,7)]
    assert [r["id"] for r in x.pilot_selection(metadata)]==["x6","x5","x4","x3"]
    measured=[dict(id="x6",status="COMPLETED",timing=dict(values=6.,posterior=6.,pairs=6.,training=6.))]
    rows,detail=x.project_costs(metadata,measured)
    assert len(rows)==6 and all(r["status"]=="PLANNED" for r in rows)
    assert detail["scale_factors"]["values"]==100.


def test_exclusive_outputs_do_not_replace_existing_data(tmp_path):
    path=tmp_path/"record.json"
    x.write_once(path,dict(a=1))
    before=path.read_bytes()
    with pytest.raises(FileExistsError):
        x.write_once(path,dict(a=2))
    assert path.read_bytes()==before


def test_lock_verification_detects_tampered_source_and_wrong_namespace(monkeypatch,tmp_path):
    monkeypatch.setattr(x,"ROOT",tmp_path)
    code=tmp_path/"input.py"
    code.write_text("original\n")
    monkeypatch.setattr(x,"source_paths",lambda out:[code])
    record=dict(namespace=x.NAMESPACE,sha256={"input.py":x.sha(code)},environment=x.environment())
    x.write_once(tmp_path/"lock.json",record)
    assert x.verify_lock(tmp_path)==record
    code.write_text("changed\n")
    with pytest.raises(ValueError,match="locked file changed"):
        x.verify_lock(tmp_path)
    code.write_text("original\n")
    # Files here were created by this test, under its own allowed tmp root.
    record["namespace"]="ctmc-v1"
    (tmp_path/"lock.json").write_text(json.dumps(record))
    with pytest.raises(ValueError,match="namespace/input set changed"):
        x.verify_lock(tmp_path)
