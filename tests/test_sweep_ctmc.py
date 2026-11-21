"""Doan Van Tai — S1-A controls; no full sweep or new held-out outcomes."""
import csv
import itertools
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm

from experiments.letter import shat2, x_ctmc as x
from experiments.letter import sweep_ctmc as s


@pytest.fixture(scope="module")
def small():
    r = x.Regime("S1A_0001", x.PathSpec(1.8, 5., 1.2, .5),
                 x.PathSpec(2.8, 8., 1.8, 1.), .4)
    return x.prepare(r, Ns=dict(A=3, B=4))


@pytest.mark.parametrize("index", [1, 2])
def test_matches_saved_X_CTMC_two_old_regimes_at_common_horizons(index, tmp_path):
    old = s.read(s.ROOT/f"results/letter/x_ctmc/raw/XCTMC_{index:03d}.json")
    assert old["status"] == "COMPLETED"
    p = x.prepare(x.Regime.from_record(old["regime"]))
    assert p["T_int"] == pytest.approx(old["T_int"], rel=1e-13)
    common_rules = ("M0", "Hybrid_true", "Hybrid_hat", "Stationary_hat", "MLU", "TH_0.8")
    got = s.evaluate(p, [p["T_int"], 3*p["T_int"]], [p["T_int"], 3*p["T_int"]],
                     old["s_hat"], rules=s.RULES)
    lookup = {(r["rule"], round(r["h_T_int"], 12), round(r["tau_T_int"], 12)):r for r in old["rows"]}
    maximum = {}
    compared = 0
    for row in got["rows"]:
        if row["rule"] not in common_rules:
            continue
        saved = lookup[(row["rule"], row["h_T_int"], row["tau_T_int"])]
        assert row["status"] == saved["status"]
        if row["status"] != "COMPLETED":
            continue
        compared += 1
        for key in ("C_ref", "L_fresh", "L_stale", "regret_fresh", "regret_stale", "G_S", "p_new", "p_old"):
            error = abs(row[key]-saved[key])
            maximum[key] = max(maximum.get(key, 0.), error)
            assert row[key] == pytest.approx(saved[key], rel=1e-9, abs=2e-10)
    assert compared >= 16
    s.dump(tmp_path/"equivalence.json", dict(id=old["regime"]["id"], compared=compared,
                                            max_absolute_errors=maximum, source_sha256=x.sha(__file__)))


def test_sample_is_reproducible_1024_unique_and_within_parameter_constraints():
    a, b = s.sobol_regimes(), s.sobol_regimes()
    assert [r.record() for r in a] == [r.record() for r in b]
    assert len(a) == len({r.id for r in a}) == 1024
    assert len(set(s.SEEDS.values())) == len(s.SEEDS)
    for r in a:
        assert r.u > 0 and not x.heldout_collision(r)
        for p in (r.A, r.B):
            assert 5 <= p.mu <= 20 and .3 <= p.load/p.mu <= .92
            assert 0 <= p.alpha/p.load <= .9 and .02 <= p.kappa <= 5
            assert p.load+r.u < .97*p.mu


@pytest.mark.parametrize("count", [0, 3, 1000, -1])
def test_sobol_requires_power_of_two(count):
    with pytest.raises(ValueError, match="power of two"):
        s.sobol_regimes(count)


def test_sample_prefix_and_no_stationary_or_truth_during_parameter_generation(monkeypatch):
    monkeypatch.setattr(x, "prepare", lambda *a,**k:pytest.fail("sample generation requested stationarity"))
    assert [r.record() for r in s.sobol_regimes(16)] == [r.record() for r in s.sobol_regimes(32)[:16]]


def test_screen_uses_stationary_cost_only_and_tail_certificate(monkeypatch, small):
    monkeypatch.setattr(x.Chain, "V", lambda *a,**k:pytest.fail("screen requested finite-h truth"))
    row = s.screen_regime(small["regime"])
    assert row["status"] == "ELIGIBLE" and row["numerical_valid"]
    for side in ("A", "B"):
        assert all(a["selector_tail"] <= x.TAIL for a in row["truncation"][side]["actions"].values())
    capped = s.screen_regime(small["regime"], cpu_cap=1e-20)
    assert capped["reason"] == "PROJECTED_CPU_CAP" and capped["model_valid"]


def test_screen_retains_invalid_and_resource_capped_candidates(monkeypatch, small):
    bad = x.Regime("S1A_0002", small["regime"].A, small["regime"].B, 100.)
    assert s.screen_regime(bad)["reason"] == "UNSTABLE_OR_INVALID_PARAMETERS"
    monkeypatch.setattr(s, "MAX_N", 1)
    row = s.screen_regime(small["regime"])
    assert row["reason"] == "TRUNCATION_RESOURCE_CAP" and row["model_valid"]


@pytest.mark.parametrize("n", [1, 2, 3, 7, 2048])
def test_shards_are_disjoint_exhaustive_even_after_exclusion(n):
    rows = [dict(id=r.id) for i,r in enumerate(s.sobol_regimes(32)) if i not in (2, 4, 8)]
    groups = [s.shard_rows(rows, f"{i}/{n}") for i in range(n)]
    ids = [r["id"] for group in groups for r in group]
    assert len(ids) == len(set(ids)) == len(rows)
    assert set(ids) == {r["id"] for r in rows}


@pytest.mark.parametrize("shard", ["1/1", "-1/2", "0/0", "x/2", "0", "0/2/3"])
def test_invalid_shards_fail_before_computing(shard):
    with pytest.raises(ValueError, match="shard"):
        s.shard_rows([], shard)


def test_pilot_contains_five_heaviest_and_five_distinct_random():
    rows = [dict(id=f"S1A_{i:04d}", status="ELIGIBLE", initial_projected_cpu_seconds=float(i))
            for i in range(1, 33)]
    chosen = s.pilot_selection(rows)
    assert chosen == s.pilot_selection(rows)
    assert [r["id"] for r,why in chosen[:5]] == [f"S1A_{i:04d}" for i in (32,31,30,29,28)]
    assert len({r["id"] for r,why in chosen}) == 10
    assert [why for r,why in chosen] == ["heaviest_proxy"]*5+["random"]*5


def test_new_aggregation_matches_X_CTMC_full_and_backlog_observation(small):
    for observation in ("full", "backlog"):
        rules = tuple(r for r in s.RULES if r not in ("Stationary_true", "Oracle"))
        new = s.evaluate(small, [.2, .7], [0., .3], -.1, observation=observation)
        reference = x.evaluate(small, [.2, .7], [0., .3], -.1, rules=rules, observation=observation)
        lookup = {(r["rule"],r["h"],r["tau"]):r for r in reference["rows"]}
        for row in new["rows"]:
            if row["rule"] not in rules:
                continue
            old = lookup[(row["rule"],row["h"],row["tau"])]
            for key in ("C_ref","L_fresh","L_stale","regret_fresh","regret_stale","G_S","p_new","p_old"):
                assert row[key] == pytest.approx(old[key], abs=2e-14)


def test_horizon_age_labels_do_not_fragment_from_floating_division(small):
    result = s.evaluate(small, [.3*small["T_int"]], [.3*small["T_int"]], .1)
    assert {r["h_T_int"] for r in result["rows"]} == {.3}
    assert {r["tau_T_int"] for r in result["rows"]} == {.3}


def test_constant_rules_oracle_and_zero_age_have_zero_GS(small):
    result = s.evaluate(small, [.3, .7], [0., .2], -.1)
    assert len(result["rows"]) == 2*2*len(s.RULES)
    assert len(result["features"]) == 2*2*2*2
    for row in result["rows"]:
        if row["rule"].startswith("Stationary_") or row["rule"] == "Oracle" or row["tau"] == 0:
            assert row["G_S"] == 0.
        if row["rule"] == "Oracle":
            assert row["L_fresh"] == row["C_ref"] and row["regret_fresh"] == 0.


def test_stale_expected_cost_matches_dense_old_current_markov_coupling(small):
    h, tau, shat = .7, .2, -.1
    got = s.evaluate(small, [h], [tau], shat)
    ch = small["chains"]
    a,b = ch["Ast"],ch["Bst"]
    da,db = (ch[side+"sw"].V([h])[0]-ch[side+"st"].V([h])[0] for side in ("A","B"))
    pa,pb = expm(a.Q.toarray()*tau),expm(b.Q.toarray()*tau)
    d = x.decision_vectors(small,[h],tau,shat)
    for rule in ("M0","Hybrid_true","Hybrid_hat","MLU","TH_0.8"):
        inputs = x.rule_inputs(small,d,rule,"stale",0,h)
        cost = 0.
        for ya,yb,xa,xb in itertools.product(range(a.n),range(b.n),range(a.n),range(b.n)):
            switch = x.sampled_decisions(inputs,np.array([ya]),np.array([yb]))[0]
            cost += a.pi[ya]*b.pi[yb]*pa[ya,xa]*pb[yb,xb]*switch*(da[xa]+db[xb])
        row = next(r for r in got["rows"] if r["rule"]==rule)
        assert row["L_stale"] == pytest.approx(h*small["r_stay"]+cost, abs=8e-15)


@pytest.mark.parametrize("shat", [-.13, 0., .13, None])
def test_D_terms_and_hybrid_static_disagreement_match_dense(small, shat):
    h, tau = .4,.2
    result = s.evaluate(small,[h],[tau],shat)
    d = x.decision_vectors(small,[h],tau,shat)
    wa,wb = small["chains"]["Ast"].pi,small["chains"]["Bst"].pi
    weights = wa[:,None]*wb[None,:]
    for r in result["features"]:
        level = small["s"] if r["level"]=="true" else shat
        for side in ("fresh","stale"):
            fluid = d[side]["A"][0,:,None]+d[side]["B"][0,None,:]
            expected = float(np.sum(weights*(abs(fluid)>=h*abs(level))))
            assert r["D_"+side] == pytest.approx(expected, abs=5e-15)
        fluid = d[r["side"]]["A"][0,:,None]+d[r["side"]]["B"][0,None,:]
        actual = float(np.sum(weights*((fluid+h*level<0)!=(level<0))))
        assert r["hybrid_static_disagreement"] == pytest.approx(actual, abs=5e-15)
        assert r["D_applicable"] == (level!=0)


def test_weighted_absolute_gap_quantiles_include_atoms_and_ties():
    wa,wb = np.array([.2,.3,.5]),np.array([.3,.7])
    a,b = np.array([0.,-2.,1.]),np.array([0.,2.])
    values = abs(a[:,None]+b[None,:]).ravel()
    weights = (wa[:,None]*wb[None,:]).ravel()
    order = np.argsort(values)
    qs = (.1,.5,.9,.99)
    got = s.abs_gap_quantiles(wa,a,wb,b,qs)
    for q,value in zip(qs,got.values()):
        expected = values[order][np.searchsorted(np.cumsum(weights[order]),q,side="left")]
        assert value == pytest.approx(expected,abs=2e-14)
    assert s.abs_gap_quantiles(wa,np.zeros(3),wb,np.zeros(2)) == dict(q10=0.,q50=0.,q90=0.,q99=0.)


def test_count_estimator_matches_literal_W2_without_writing_old_result_root(tmp_path, monkeypatch):
    monkeypatch.setattr(shat2.tempfile,"tempdir",str(tmp_path))
    path = x.PathSpec(3.,10.,1.2,.2)
    ours = s.estimate_path(path,3.4,-.4,.02,np.random.default_rng(123))
    old = shat2.estimate_path(3.4,-.4,1.2,.2,.02,np.random.default_rng(123),W=6.)
    for key in ("count_sha256_le_i4","lambda_hat","alpha_hat","kappa_hat","autocovariances",
                "status","rate_variance","first_nonpositive_lag"):
        assert ours[key]==old[key]
    assert ours["W"]==6. and ours["n_bins"]==600


def fake_estimate(path, stay, shift, tint, rng):
    return dict(status="INVALID",errors=["synthetic invalid modulation fit"],lambda_hat=stay,
                stay_load_hat=stay,switch_load_hat=stay+shift)


def test_invalid_mmpp_uses_observed_mm1_for_both_static_and_hybrid(monkeypatch, small):
    monkeypatch.setattr(s,"estimate_path",fake_estimate)
    est = s.estimate_s(small,"pilot")
    r = small["regime"]
    expected = x.parameter_comparison(r)["s_mm1"]
    assert est["method"]=="M/M/1" and est["fallback"] and est["s_hat_mmpp"] is None
    assert est["s_hat"]==pytest.approx(expected)
    assert est["s_hat"]!=pytest.approx(small["s"])
    result = s.evaluate(small,[.4],[.2],est["s_hat"])
    assert all(r["status"]=="COMPLETED" for r in result["rows"])


def test_invalid_mm1_retains_missing_hat_rules_without_clipping(monkeypatch, small):
    def invalid(path, stay, shift, tint, rng):
        rec = fake_estimate(path,stay,shift,tint,rng)
        rec["stay_load_hat"] = rec["switch_load_hat"] = path.mu+1
        return rec
    monkeypatch.setattr(s,"estimate_path",invalid)
    est = s.estimate_s(small,"run")
    assert est["status"]=="INVALID_ESTIMATOR" and est["s_hat"] is None
    result = s.evaluate(small,[.4],[.2],None)
    assert {r["rule"] for r in result["rows"] if r["status"]!="COMPLETED"} == {"Stationary_hat","Hybrid_hat"}
    assert {r["level"] for r in result["features"]} == {"true"}


def test_record_stream_is_independent_of_worker_and_shard(monkeypatch, small):
    monkeypatch.setattr(s,"estimate_path",fake_estimate)
    a,b = s.estimate_s(small,"pilot"),s.estimate_s(small,"run")
    assert a["seed_coordinate"] != b["seed_coordinate"]
    assert s.estimate_s(small,"run")==b


def test_projection_uses_cost_only_and_reports_exclusion():
    rows = [dict(id=f"S1A_{i:04d}",status="ELIGIBLE",reason=None,
                 initial_projected_cpu_seconds=float(i),work={k:float(i) for k in s.INITIAL_COEFFICIENTS})
            for i in (1,2,3)]
    measured = [dict(id=f"S1A_{i:04d}",status="COMPLETED",cpu_seconds=float(5*i),
                     timing={k:float(i) for k in s.INITIAL_COEFFICIENTS}) for i in (1,2)]
    result = s.project(rows,measured,cpu_cap=16.)
    assert result["eligible"]==2
    assert result["rows"][2]["reason"]=="PROJECTED_CPU_CAP"
    assert result["projected_cpu_hours"]==pytest.approx(22.5/3600)
    assert result["projected_wall_hours_15_workers"]==pytest.approx(22.5/3600/15)


def test_affine_cost_model_separates_fixed_overhead_and_envelopes_all_timings():
    rows = [dict(id=f"S1A_{i:04d}",status="ELIGIBLE",reason=None,
                 initial_projected_cpu_seconds=float(i),work={k:float(w) for k in s.INITIAL_COEFFICIENTS})
            for i,w in enumerate((10,100,1000),1)]
    measured = [dict(id=row["id"],status="COMPLETED",cpu_seconds=30.,
                     timing={k:5.+.01*w for k,w in row["work"].items()}) for row in rows]
    result = s.project(rows,measured,cpu_cap=3600.)
    for k in s.INITIAL_COEFFICIENTS:
        assert result["coefficients"][k]==pytest.approx(.01)
        assert result["pilot_intercepts_seconds"][k]==pytest.approx(5.)
        for row,measurement in zip(rows,measured):
            assert result["coefficients"][k]*row["work"][k]+result["pilot_intercepts_seconds"][k]+1e-12 >= measurement["timing"][k]


def test_pilot_work_scales_to_full_requested_grid_without_changing_telemetry(small):
    full = s.work_proxy(small)
    pilot = s.work_proxy(small,s.PILOT_H,s.PILOT_AGES)
    assert full["values"]/pilot["values"]==pytest.approx(30.)
    assert full["posterior"]/pilot["posterior"]==pytest.approx(sum(s.AGES)/sum(s.PILOT_AGES)*29/5)
    assert full["pairs"]/pilot["pairs"]==pytest.approx(21.)
    assert full["telemetry"]==pilot["telemetry"] and full["prepare"]==pilot["prepare"]


def test_exclusive_creation_and_output_boundary(tmp_path):
    target = tmp_path/"record.json"
    s.dump(target,dict(a=1))
    before = target.read_bytes()
    with pytest.raises(FileExistsError):
        s.dump(target,dict(a=2))
    assert target.read_bytes()==before
    with pytest.raises(ValueError,match="outputs must"):
        s.validate_output(s.ROOT/"results/letter/x_ctmc")


def test_cli_run_handoff_only_parses_without_executing_engine(monkeypatch):
    called = []
    monkeypatch.setattr(s,"run",lambda **kwargs:called.append(kwargs))
    s.main(["run","--workers","15","--shard","1/2"])
    assert called==[dict(out=s.OUT,workers=15,shard="1/2")]


def test_run_rejects_source_change_before_any_engine_or_run_marker(monkeypatch,tmp_path):
    monkeypatch.setattr(s,"OUT",tmp_path)
    monkeypatch.setattr(s,"load_sample",lambda out:dict(candidates=[]))
    monkeypatch.setattr(x,"require_environment",lambda:None)
    monkeypatch.setattr(x.Chain,"V",lambda *a,**k:pytest.fail("engine used before guard"))
    s.dump(tmp_path/"pilot.json",dict(source_sha256="wrong",input_sha256=s.hashes()))
    with pytest.raises(ValueError,match="source/input differs"):
        s.run(tmp_path,workers=1,shard="0/2")
    assert not (tmp_path/"runs").exists()


def test_worker_keeps_failure_record_and_refuses_to_replace_it(monkeypatch,tmp_path,small):
    def fail(*args,**kwargs):
        raise ArithmeticError("synthetic preparation failure")
    monkeypatch.setattr(x,"prepare",fail)
    meta = dict(id="S1A_0001",regime=small["regime"].record(),
                truncation={side:dict(N=3) for side in ("A","B")})
    task = (meta,"pilot",str(tmp_path),30.)
    result = s.evaluate_one(task)
    target = tmp_path/"S1A_0001.json"
    assert result["status"]=="ERROR" and result["rows"]==0
    assert "synthetic preparation failure" in s.read(target)["error"]
    before = target.read_bytes()
    with pytest.raises(FileExistsError):
        s.evaluate_one(task)
    assert target.read_bytes()==before


def test_summarize_pilot_exports_both_policies_and_no_population_claim(monkeypatch,tmp_path,small):
    monkeypatch.setattr(s,"OUT",tmp_path)
    monkeypatch.setattr(s,"load_sample",lambda out:dict(candidate_count=1024))
    result = s.evaluate(small,[.3],[.1,.3],-.1)
    record = dict(id="S1A_0001",status="COMPLETED",estimator=dict(method="M/M/1"),**result)
    s.dump(tmp_path/"pilot/S1A_0001.json",record)
    s.dump(tmp_path/"pilot.json",dict(measured=[dict(id="S1A_0001",sha256=x.sha(tmp_path/"pilot/S1A_0001.json"))],
                                    projection=dict(eligible=1000)))
    summary = s.summarize(tmp_path,"pilot")
    assert summary["coverage"]=="PILOT_ONLY" and summary["feature_rows"]==8
    assert summary["invalid_policy_rows"]==0 and "no iid/population CI" in summary["statistics"]
    assert len(summary["by_h"])==4 and len(summary["by_h_and_age"])==8
    for row in summary["by_h"]:
        assert row["baseline_mean_regret_pct_C_ref"]-row["hybrid_mean_regret_pct_C_ref"] == pytest.approx(row["benefit_pp_C_ref_mean"])
    with (tmp_path/"pilot_summary/features_benefit.csv").open() as stream:
        assert len(list(csv.DictReader(stream)))==8
