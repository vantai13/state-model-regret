"""Doan Van Tai — mathematical and saved-data controls for V7-1."""
from fractions import Fraction as F
import json

import numpy as np
import pytest

from experiments.letter.v7_1_rule import (
    ROOT, auc, bootstrap_auc, check_relative, extract_ctmc, law_quantile,
    onset_rows, pair_abs_cdf, run,
)
from experiments.letter.v7_1_rescore import mann_whitney, rescore


@pytest.mark.parametrize("labels,scores,expected", [
    ([0,0,1,1], [.1,.4,.35,.8], .75),
    ([0,0,1,1], [0,1,1,2], .875),
    ([0,1,0,1], [1,1,1,1], .5),
    ([0,0,1,1], [1,2,3,4], 1.),
    ([0,0,1,1], [4,3,2,1], 0.),
    ([1,1], [0,1], None),
])
def test_auc_known_mann_whitney_and_independent_route(labels, scores, expected):
    assert auc(labels,scores) == expected
    assert mann_whitney(labels,scores) == expected


def test_auc_rejects_nonfinite_and_nonbinary():
    with pytest.raises(ValueError): auc([0,1],[1,np.nan])
    with pytest.raises(ValueError): auc([0,2],[0,1])


def test_weighted_joint_quantile_against_brute_force_and_unequal_probabilities():
    x, z = np.array([-3.,0.,2.]), np.array([-1.,4.])
    wx, wz = np.array([.2,.3,.5]), np.array([.75,.25])
    values = np.abs(x[:,None]+z[None,:]).ravel()
    weights = (wx[:,None]*wz[None,:]).ravel()
    for threshold in (0,1,2,3,4,5,6):
        assert pair_abs_cdf(x,wx,z,wz,threshold) == pytest.approx(weights[values<=threshold].sum(), abs=1e-14)
    order = np.argsort(values)
    expected = values[order][np.searchsorted(weights[order].cumsum(), .9)]
    assert law_quantile([(1.,x,wx,z,wz)]) == expected


def test_conditional_expectation_before_absolute_value_and_equal_sides():
    x, wx, z, wz = np.array([-2.,2.]), np.array([.5,.5]), np.array([0.]), np.array([1.])
    old = np.array([0.,0.])
    components = [(.5,x,wx,z,wz),(.5,old,wx,z,wz)]
    assert law_quantile(components, .5) == 0.
    assert law_quantile(components, .9) == 2.


def test_relative_replay_has_no_absolute_tolerance_for_tiny_saved_values():
    assert check_relative("a", 1e-15, 1e-15)["relative_error"] == 0.
    with pytest.raises(ArithmeticError): check_relative("a", 2e-15, 1e-15)
    with pytest.raises(ArithmeticError): check_relative("zero", 1e-30, 0.)


def test_gap_extraction_reproduces_one_saved_regime_saturation_decision_mass():
    path = ROOT/"results/letter/w1b/raw/A_u1_lA7_x1-4_k1-20.json"
    raw = json.loads(path.read_text())
    result, arrays = extract_ctmc(raw)
    wa,wb = arrays["pi_A"], arrays["pi_B"]
    fresh = arrays["gap_A"][:,None]+arrays["gap_B"][None,:]
    measured = float(((wa[:,None]*wb[None,:])*(fresh<0)).sum())
    saved = raw["evaluations"][0]["asymptotic"]["F_new"]
    assert measured == pytest.approx(saved, rel=1e-9, abs=0.)
    assert result["scale"]["Q90"] > 0
    assert result["scale"]["M_hat"] == np.abs(fresh).max()
    assert len(result["checks"]) == 20
    assert max(c["relative_error"] for c in result["checks"]) <= 1e-9
    # The uncorrected saturation vectors must agree with direct fluid cost gaps.
    from experiments.explore_ctmc import ctmc
    la,lb,u,k,_ = map(F,raw["case"]["parameters"])
    na,nb = raw["evaluations"][0]["N"].values()
    da = (ctmc.m0_vhat(la,k,na,[np.inf])-ctmc.m0_vhat(la+u,k,na,[np.inf]))[0]
    db = (ctmc.m0_vhat(lb+u,k,nb,[np.inf])-ctmc.m0_vhat(lb,k,nb,[np.inf]))[0]
    np.testing.assert_array_equal(arrays["gap_A"], da)
    np.testing.assert_array_equal(arrays["gap_B"], db)


def test_onset_all_ages_and_all_later_horizons_not_first_success():
    rows = []
    for age, ys in (("a",[1,0,1]),("b",[1,1,1])):
        for h,y in zip((1,2,3),ys):
            rows.append(dict(dataset="toy",regime="r",seed="s",age=age,h_s=h,Y=y,
                             T_int_s=2,h_star_s=3,h_star_Tint=1.5))
    assert onset_rows(rows)[0]["onset_s"] == 3
    rows[-1]["Y"] = 0
    assert onset_rows(rows)[0]["censoring"] == "right"


def test_cluster_bootstrap_known_perfect_reversed_and_tied_scores():
    rows = [dict(regime=g,seed=s,Y=y,P1=y,P2=1-y,P3=1.)
            for g in ("a","b") for s in ("first","second") for y in (0,1)]
    result = bootstrap_auc(rows, draws=20)
    assert result["regimes"] == 2
    assert result["auc"]["P1"] == dict(value=1.,ci95=[1.,1.])
    assert result["auc"]["P2"] == dict(value=0.,ci95=[0.,0.])
    assert result["auc"]["P3"] == dict(value=.5,ci95=[.5,.5])
    assert result["auc_difference_P2_minus_P1"] == dict(value=-1.,ci95=[-1.,-1.])


def test_resource_stop_blocks_local_full_analysis_before_inputs(tmp_path):
    (tmp_path/"pilot.json").write_text(json.dumps(dict(status="STOP_FOR_GCP")))
    with pytest.raises(RuntimeError, match="exceeds 20 minutes"):
        run(tmp_path)
    assert not (tmp_path/"input_manifest.json").exists()


def test_rescore_refuses_partial_population_instead_of_reporting_pass(tmp_path):
    (tmp_path/"cells.csv").write_text("dataset,Y\nCTMC,1\n")
    (tmp_path/"summary.json").write_text("{}\n")
    with pytest.raises(ValueError,match="incomplete population"):
        rescore(tmp_path)
    assert not (tmp_path/"rescore.json").exists()
