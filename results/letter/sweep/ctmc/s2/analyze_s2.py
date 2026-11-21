"""Doan Van Tai — S2, exploratory POST HOC, saved S1-A tables only.

No evaluator is imported. All published outputs use exclusive creation.
See analysis_config.json for conventions fixed before inspecting S2 outcomes.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, t

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
SUMMARY = BASE / "v2/run_summary"
KEYS = ["regime", "h_T_int", "tau_T_int", "side", "level"]
GROUP = ["h_T_int", "side", "level"]
REGIME_GROUP = ["regime", *GROUP]
HARM = -.05
GAIN = .1
FEATURE_BINS = {
    "abs_s_over_r_min": [0, .03, .1, .3, 1, np.inf],
    "kappa_min_over_T_int": [0, .01, .03, .1, .3, 1, np.inf],
    "kappa_max_over_T_int": [0, .01, .03, .1, .3, 1, np.inf],
    "A_kappa_over_T_int": [0, .01, .03, .1, .3, 1, np.inf],
    "B_kappa_over_T_int": [0, .01, .03, .1, .3, 1, np.inf],
    "load_imbalance": [0, .05, .15, .3, np.inf],
    "load_balance_other_minus_chosen": [-np.inf, -.15, -.05, .05, .15, np.inf],
    "load_level": [0, .5, .7, .85, np.inf],
    "D": [0, .01, .05, .1, .3, .5, 1, 1.5, np.inf],
    "D_side": [0, .01, .05, .1, .3, .5, 1, np.inf],
    "disagreement": [0, .001, .01, .05, .1, .3, 1, np.inf],
    "abs_shat_over_abs_s": [0, .25, .5, .75, 1, 1.25, 2, 4, np.inf],
}
CATEGORICAL = ["static_action", "rate_sign", "estimator_method"]
FEATURES = [*FEATURE_BINS, "static_switch", "same_rate_sign"]
OUTPUTS = ["paired_by_age.csv", "paired_regime_h.csv", "by_h.csv", "by_h_and_age.csv",
           "bins_by_h.csv", "gates_by_h.csv", "spearman_by_h.csv", "hypotheses_AB.csv",
           "hc_threshold_selection.csv", "hypothesis_C.csv", "harm_regions.csv",
           "harm_regime_h.csv", "harm_by_age.csv", "risk_feature_summary.csv",
           "delta_by_gap_h.png", "delta_by_kappa_h.png", "delta_by_estimator_ratio_h.png",
           "feature_dictionary.json", "results.json", "analysis_timing.json"]


def json_once(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def csv_once(name, rows):
    df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    with (OUT / name).open("x", newline="", encoding="utf-8") as stream:
        df.to_csv(stream, index=False, float_format="%.17g")


def paired_delta(static, hybrid, reference):
    """Positive means hybrid wins; reference is the SAME paired oracle cost."""
    if not all(math.isfinite(v) for v in (static, hybrid, reference)) or reference <= 0:
        raise ValueError("finite regrets and positive paired C_ref required")
    absolute = static - hybrid
    return absolute, 100 * absolute / reference


def gate(n_region, n_total, mean_delta):
    """Only the numeric clause; the unspecified harm clause is never adopted."""
    if not 0 <= n_region <= n_total or n_total <= 0:
        raise ValueError("invalid regime denominator")
    if n_region == 0:
        return "NOT_EVALUABLE"
    if mean_delta is None or not math.isfinite(mean_delta):
        raise ValueError("nonempty region requires a finite mean")
    return "PASS" if n_region / n_total >= .1 and mean_delta >= .1 else "FAIL"


def ci(values):
    a = np.asarray(values, dtype=float)
    if not np.isfinite(a).all():
        raise ValueError("nonfinite outcomes")
    if len(a) < 2:
        return None, None
    half = float(t.ppf(.975, len(a) - 1) * np.std(a, ddof=1) / math.sqrt(len(a)))
    return float(np.mean(a) - half), float(np.mean(a) + half)


def stats(group, denominator):
    """One observation per regime; repeated ages/h are rejected here."""
    n = len(group)
    if group.regime.nunique() != n:
        raise ValueError("collapse repeated observations within regime before statistics")
    result = dict(n_regimes=n, denominator_regimes=denominator,
                  share_regimes=n / denominator if denominator else None)
    for col in ["delta_pp", "delta_abs"]:
        a = group[col].to_numpy(float)
        low, high = ci(a)
        result.update({col + "_" + key: value for key, value in dict(
            mean=float(a.mean()) if n else None,
            median=float(np.median(a)) if n else None,
            q10=float(np.quantile(a, .1)) if n else None,
            q90=float(np.quantile(a, .9)) if n else None,
            min=float(a.min()) if n else None,
            max=float(a.max()) if n else None,
            ci95_low=low, ci95_high=high).items()})
    for col in ["baseline_pp", "hybrid_pp", "baseline_abs", "hybrid_abs", "disagreement"]:
        result[col + "_mean"] = float(group[col].mean()) if n else None
    result.update(n_delta_ge_01=int((group.delta_pp >= .1).sum()),
                  n_delta_le_neg005=int((group.delta_pp <= -.05).sum()),
                  n_delta_le_neg01=int((group.delta_pp <= -.1).sum()),
                  n_abs_delta_lt_005=int((group.delta_pp.abs() < .05).sum()),
                  numeric_gate=gate(n, denominator, result["delta_pp_mean"]),
                  mean_le_neg005=bool(n and result["delta_pp_mean"] <= -.05),
                  mean_le_neg01=bool(n and result["delta_pp_mean"] <= -.1),
                  ci95_high_below_zero=bool(n > 1 and result["delta_pp_ci95_high"] < 0))
    return result


def split_ids(frame):
    """Odd IDs train, even IDs evaluate, with all horizons of an ID together."""
    parity = frame.regime.str.rsplit("_", n=1).str[-1].astype(int) % 2
    return frame[parity == 1], frame[parity == 0]


def select_threshold(training, grid):
    labels = training.delta_pp.to_numpy() >= GAIN
    candidates = []
    for threshold in grid:
        chosen = training.D.to_numpy() >= threshold
        count = int(chosen.sum())
        tp = int((chosen & labels).sum())
        fp, fn = count - tp, int(labels.sum()) - tp
        f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.
        candidates.append(dict(d_star=float(threshold), n_selected=count,
                               n_train=len(training), coverage=count / len(training),
                               true_positive=tp, false_positive=fp, false_negative=fn,
                               f1=f1, eligible_coverage=count / len(training) >= .1))
    eligible = [r for r in candidates if r["eligible_coverage"]]
    if not eligible:
        raise ValueError("no training threshold covers 10% of regimes")
    best = min(eligible, key=lambda r: (-r["f1"], r["d_star"]))
    return best, candidates


def load_pairs():
    """Recompute targets from policy regret rows; features are outcome-free."""
    cols = ["regime", "h_T_int", "tau_T_int", "rule", "status", "C_ref",
            "regret_fresh", "regret_stale", "L_fresh", "L_stale", "p_new", "p_old"]
    policies = pd.read_csv(SUMMARY / "policies.csv", usecols=cols)
    if not policies.status.eq("COMPLETED").all():
        raise ValueError("invalid policies require explicit missing-data handling")
    base_keys = KEYS[:3]
    pairs = []
    for level in ["true", "hat"]:
        static = policies[policies.rule == "Stationary_" + level].set_index(base_keys)
        hybrid = policies[policies.rule == "Hybrid_" + level].set_index(base_keys)
        if static.index.has_duplicates or not static.index.equals(hybrid.index):
            raise ValueError("unpaired or duplicated policy rows")
        if not np.array_equal(static.C_ref, hybrid.C_ref) or (static.C_ref <= 0).any():
            raise ValueError("invalid paired normalizer")
        for side, share in [("fresh", "p_new"), ("stale", "p_old")]:
            table = static.index.to_frame(index=False)
            table["side"], table["level"] = side, level
            table["C_ref"] = static.C_ref.to_numpy()
            table["baseline_abs"] = static["regret_" + side].to_numpy()
            table["hybrid_abs"] = hybrid["regret_" + side].to_numpy()
            table["delta_abs"] = table.baseline_abs - table.hybrid_abs
            for src, dest in [("baseline_abs", "baseline_pp"), ("hybrid_abs", "hybrid_pp"),
                              ("delta_abs", "delta_pp")]:
                table[dest] = 100 * table[src] / table.C_ref
            # L differences are an independent cancellation check, not the primary target.
            difference = static["L_" + side].to_numpy() - hybrid["L_" + side].to_numpy()
            assert np.allclose(table.delta_abs, difference, atol=2e-10, rtol=1e-9)
            table["p_hybrid_switch"] = hybrid[share].to_numpy()
            pairs.append(table)
    feature_cols = [*KEYS, "D", "D_fresh", "D_stale", "hybrid_static_disagreement",
                    "s", "s_hat", "r_min", "abs_s_over_r_min", "A_kappa_over_T_int",
                    "B_kappa_over_T_int", "A_base_rho", "B_base_rho", "A_rho_stay",
                    "B_rho_stay", "A_rho_switch", "B_rho_switch", "estimator_method",
                    "benefit_pp_C_ref", "benefit_static_minus_hybrid"]
    features = pd.read_csv(SUMMARY / "features_benefit.csv", usecols=feature_cols)
    result = pd.concat(pairs, ignore_index=True).merge(features, on=KEYS, validate="one_to_one")
    assert len(result) == len(features) == 168000
    assert np.allclose(result.delta_pp, result.benefit_pp_C_ref, atol=1e-10, rtol=1e-10)
    assert np.allclose(result.delta_abs, result.benefit_static_minus_hybrid, atol=1e-10, rtol=1e-10)
    result = result.drop(columns=["benefit_pp_C_ref", "benefit_static_minus_hybrid"])
    chosen_rate = np.where(result.level.eq("true"), result.s, result.s_hat)
    result["static_switch"] = (chosen_rate < 0).astype(int)
    result["static_action"] = np.where(result.static_switch, "Switch", "Stay")
    result["disagreement"] = np.where(result.static_switch, 1 - result.p_hybrid_switch,
                                       result.p_hybrid_switch)
    assert np.allclose(result.disagreement, result.hybrid_static_disagreement, atol=1e-12)
    result = result.drop(columns=["hybrid_static_disagreement", "p_hybrid_switch"])
    result["D_side"] = np.where(result.side.eq("fresh"), result.D_fresh, result.D_stale)
    assert ((result.disagreement >= -1e-9) & (result.disagreement <= result.D_side + 1e-9)).all()
    result["abs_shat_over_abs_s"] = result.s_hat.abs() / result.s.abs().replace(0, np.nan)
    result["same_rate_sign"] = (np.sign(result.s_hat) == np.sign(result.s)).astype(int)
    result["rate_sign"] = np.where(result.same_rate_sign, "same_sign", "different_sign")
    result["kappa_min_over_T_int"] = result[["A_kappa_over_T_int", "B_kappa_over_T_int"]].min(axis=1)
    result["kappa_max_over_T_int"] = result[["A_kappa_over_T_int", "B_kappa_over_T_int"]].max(axis=1)
    result["load_imbalance"] = (result.A_base_rho - result.B_base_rho).abs()
    result["load_level"] = result[["A_base_rho", "B_base_rho"]].max(axis=1)
    chosen = np.where(result.static_switch, result.B_rho_switch, result.A_rho_stay)
    other = np.where(result.static_switch, result.A_rho_switch, result.B_rho_stay)
    result["load_balance_other_minus_chosen"] = other - chosen
    result["split"] = np.where(result.regime.str[-4:].astype(int) % 2, "train_odd", "evaluation_even")
    # Fresh side is repeated at three ages: verify this before averaging anything.
    fresh = result[result.side == "fresh"]
    assert fresh.groupby(["regime", "h_T_int", "level"]).delta_pp.nunique().eq(1).all()
    # All 3 ages, both sides, both rate choices, for every regime and horizon.
    assert result.groupby(REGIME_GROUP).tau_T_int.nunique().eq(3).all()
    aggregation = {c: "mean" if pd.api.types.is_numeric_dtype(result[c]) else "first"
                   for c in result if c not in REGIME_GROUP + ["tau_T_int"]}
    collapsed = result.groupby(REGIME_GROUP, sort=True, as_index=False).agg(aggregation)
    collapsed["n_tau"] = 3
    return result, collapsed


def grouped_stats(frame, columns):
    records = []
    for key, group in frame.groupby(columns, sort=True):
        key = key if isinstance(key, tuple) else (key,)
        records.append(dict(zip(columns, key), **stats(group, group.regime.nunique())))
    return records


def binned_tables(frame):
    rows, correlation = [], []
    for key, group in frame.groupby(GROUP, sort=True):
        common = dict(zip(GROUP, key))
        n = len(group)
        for feature, edges in FEATURE_BINS.items():
            categories = pd.cut(group[feature], edges, right=False, include_lowest=True)
            for category in categories.cat.categories:
                selected = group[categories == category]
                if len(selected):
                    rows.append(dict(**common, feature=feature, bin=str(category),
                                     **stats(selected, n)))
        for feature in CATEGORICAL:
            for category, selected in group.groupby(feature, sort=True):
                rows.append(dict(**common, feature=feature, bin=str(category), **stats(selected, n)))
        for feature in FEATURES:
            good = group[[feature, "delta_pp"]].dropna()
            rho = None
            if len(good) > 2 and good[feature].nunique() > 1 and good.delta_pp.nunique() > 1:
                rho = float(spearmanr(good[feature], good.delta_pp).statistic)
            correlation.append(dict(**common, feature=feature, n_regimes=len(good),
                                    spearman_rho=rho, constant_feature=good[feature].nunique() <= 1,
                                    constant_target=good.delta_pp.nunique() <= 1))
    return rows, correlation


def hypotheses_ab(frame):
    rows = []
    for key, group in frame.groupby(GROUP, sort=True):
        common = dict(zip(GROUP, key))
        h, side, level = key
        if h <= 3 and side == "fresh":
            region = group[(group.abs_s_over_r_min <= .1) & (group.static_action == "Stay")]
            s = stats(region, len(group))
            fraction = s["n_delta_ge_01"] / len(region) if len(region) else None
            rows.append(dict(**common, hypothesis="H-A", **s, share_matching=fraction,
                             hypothesis_verdict="NOT_EVALUABLE" if fraction is None else
                             "PASS_MAJORITY" if fraction > .5 else "FAIL_MAJORITY"))
        region = group[(group.abs_s_over_r_min >= .3) | (h >= 10)]
        s = stats(region, len(group))
        fraction = s["n_abs_delta_lt_005"] / len(region) if len(region) else None
        rows.append(dict(**common, hypothesis="H-B", **s, share_matching=fraction,
                         hypothesis_verdict="NOT_EVALUABLE" if fraction is None else
                         "ALL_MATCH" if fraction == 1 else "COUNTEREXAMPLES",
                         n_counterexamples=len(region) - s["n_abs_delta_lt_005"]))
    return rows


def hypothesis_c(frame, config):
    rows, selection = [], []
    for key, group in frame.groupby(GROUP, sort=True):
        common = dict(zip(GROUP, key))
        training, evaluation = split_ids(group)
        assert set(training.regime).isdisjoint(set(evaluation.regime))
        best, candidates = select_threshold(training, config["H_C"]["threshold_grid"])
        threshold = best["d_star"]
        for candidate in candidates:
            selection.append(dict(**common, **candidate, selected=candidate["d_star"] == threshold))
        for split, data in [("train_odd", training), ("evaluation_even", evaluation)]:
            region = data[data.D >= threshold]
            s = stats(region, len(data))
            tp = s["n_delta_ge_01"]
            positives = int((data.delta_pp >= GAIN).sum())
            rows.append(dict(**common, split=split, d_star=threshold, **s,
                             true_positive=tp, false_positive=len(region) - tp,
                             false_negative=positives - tp, total_positive=positives,
                             precision=tp / len(region) if len(region) else None,
                             recall=tp / positives if positives else None,
                             training_f1=best["f1"]))
    return rows, selection


def figures(frame):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.colors import TwoSlopeNorm

    for feature, name in [("abs_s_over_r_min", "delta_by_gap_h.png"),
                          ("kappa_min_over_T_int", "delta_by_kappa_h.png"),
                          ("abs_shat_over_abs_s", "delta_by_estimator_ratio_h.png")]:
        edges = FEATURE_BINS[feature]
        labels = [f"{a:g}–{b:g}" for a, b in zip(edges[:-1], edges[1:])]
        h_values = sorted(frame.h_T_int.unique())
        fig, axes = plt.subplots(2, 2, figsize=(10, 5.8), layout="constrained")
        matrices = []
        for side in ["fresh", "stale"]:
            for level in ["true", "hat"]:
                subset = frame[(frame.side == side) & (frame.level == level)].copy()
                subset["bin"] = pd.cut(subset[feature], edges, labels=labels, right=False)
                matrix = subset.pivot_table(index="bin", columns="h_T_int", values="delta_pp",
                                            aggfunc="mean", observed=False).reindex(index=labels, columns=h_values)
                matrices.append(matrix.to_numpy())
        finite = np.concatenate([a[np.isfinite(a)] for a in matrices])
        limit = max(float(np.quantile(np.abs(finite), .98)), .1)
        norm = TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit)
        for ax, matrix, (side, level) in zip(axes.flat, matrices,
                                          [(s, l) for s in ["fresh", "stale"] for l in ["true", "hat"]]):
            im = ax.imshow(matrix, origin="lower", aspect="auto", cmap="RdBu", norm=norm)
            ax.set_title(f"{side}, {'s true' if level == 'true' else 's estimated'}", fontsize=10)
            ax.set_xticks(range(len(h_values)), [f"{h:g}" for h in h_values], fontsize=7)
            ax.set_yticks(range(len(labels)), labels, fontsize=7)
            ax.set_xlabel("h / T_int", fontsize=8)
            ax.set_ylabel(feature, fontsize=8)
        fig.colorbar(im, ax=axes.ravel().tolist(), shrink=.8, label="mean Δ (pp of C_ref); clipped colour scale")
        fig.suptitle("S2 exploratory / post hoc; ages averaged within regime", fontsize=11)
        with (OUT / name).open("xb") as stream:
            fig.savefig(stream, format="png", dpi=150)
        plt.close(fig)


def main():
    start, wall = time.process_time(), time.perf_counter()
    collisions = [name for name in OUTPUTS if (OUT / name).exists()]
    if collisions:
        raise FileExistsError("exclusive-create outputs already exist: " + ", ".join(collisions))
    config = json.loads((OUT / "analysis_config.json").read_text())
    input_audit = json.loads((OUT / "input_audit.json").read_text())
    summary = json.loads((SUMMARY / "summary.json").read_text())
    assert summary["coverage"] == "FULL" and summary["measured_regimes"] == 1000
    age, frame = load_pairs()
    csv_once("paired_by_age.csv", age)
    csv_once("paired_regime_h.csv", frame)
    by_h = grouped_stats(frame, GROUP)
    by_age = grouped_stats(age, GROUP + ["tau_T_int"])
    bins, correlation = binned_tables(frame)
    ab = hypotheses_ab(frame)
    hc, threshold_selection = hypothesis_c(frame, config)
    gates = []
    for population in by_h:
        common = {k: population[k] for k in GROUP}
        regions = [r for r in bins if all(r[k] == common[k] for k in GROUP)]
        passing = [r for r in regions if r["numeric_gate"] == "PASS"]
        gates.append(dict(**common, population_numeric_gate=population["numeric_gate"],
                          n_regimes=population["n_regimes"], mean_delta_pp=population["delta_pp_mean"],
                          n_delta_ge_01=population["n_delta_ge_01"],
                          share_individual_ge_01=population["n_delta_ge_01"] / population["n_regimes"],
                          feature_region_numeric_gate="PASS" if passing or population["numeric_gate"] == "PASS" else "FAIL",
                          n_passing_feature_bins=len(passing), harm_clause="NOT_DECIDED"))
    harms = []
    for source, records in [("population", by_h), ("feature_bin", bins), ("H-AB", ab), ("H-C", hc)]:
        for row in records:
            if row["mean_le_neg005"]:
                harms.append(dict(source=source, **row))
    bad = frame[frame.delta_pp <= HARM].copy().sort_values("delta_pp")
    bad_age = age[age.delta_pp <= HARM].copy().sort_values("delta_pp")
    risk = []
    # A regime occurs once per fixed h/side/rate in each comparison.
    for key, group in frame.groupby(GROUP, sort=True):
        for risk_class, subset in [("harm_le_neg005", group[group.delta_pp <= HARM]),
                                   ("other", group[group.delta_pp > HARM])]:
            row = dict(zip(GROUP, key), risk_class=risk_class, n_regimes=len(subset))
            for feature in FEATURES:
                v = subset[feature].dropna()
                row.update({feature + "_median": float(v.median()) if len(v) else None,
                            feature + "_q10": float(v.quantile(.1)) if len(v) else None,
                            feature + "_q90": float(v.quantile(.9)) if len(v) else None})
            row["n_rate_sign_mismatch"] = int((subset.same_rate_sign == 0).sum())
            risk.append(row)
    for name, records in [("by_h.csv", by_h), ("by_h_and_age.csv", by_age),
                          ("bins_by_h.csv", bins), ("gates_by_h.csv", gates),
                          ("spearman_by_h.csv", correlation), ("hypotheses_AB.csv", ab),
                          ("hc_threshold_selection.csv", threshold_selection),
                          ("hypothesis_C.csv", hc), ("harm_regions.csv", harms),
                          ("harm_regime_h.csv", bad), ("harm_by_age.csv", bad_age),
                          ("risk_feature_summary.csv", risk)]:
        csv_once(name, records)
    figures(frame)
    json_once(OUT / "feature_dictionary.json", dict(
        allowed_features=FEATURES + CATEGORICAL,
        provenance="parameters, stationary model, finite arrival record, policy decision disagreement; no regret/cost outcomes as predictors",
        D="D_fresh + D_stale of Corollary 1, mean over the 3 ages for regime/h summaries; range [0,2]",
        D_side="the corresponding one-side D tail; not the actual hybrid/static disagreement",
        load_imbalance="abs(A_base_rho - B_base_rho)",
        load_balance_other_minus_chosen="rho of other path minus chosen path under the stationary chosen action",
        load_level="max(A_base_rho, B_base_rho)",
        abs_shat_over_abs_s="diagnostic using model true s; unavailable without a model or validation reference; undefined when s=0",
        model_only="true s, true r_min, true T_int and true-side D require the generative model; outcome-free does not imply measured on a production network",
        excluded_outcome_features=["C_ref", "baseline_abs", "hybrid_abs", "baseline_pp", "hybrid_pp", "delta_abs", "delta_pp"],
        bins={k: [str(v) for v in edges] for k, edges in FEATURE_BINS.items()}))
    evaluation_candidates = [r for r in hc if r["split"] == "evaluation_even" and
                             r["numeric_gate"] == "PASS" and r["side"] == "fresh" and r["level"] == "hat"]
    evaluation_candidates.sort(key=lambda r: (-r["delta_pp_mean"], r["h_T_int"]))
    result = dict(owner="Doan Van Tai", kind="EXPLORATORY_POST_HOC", status="COMPLETE",
                  gate_overall="NOT_DECIDED_UNQUANTIFIED_HARM", numeric_gate_counts=dict(Counter(
                      r["feature_region_numeric_gate"] for r in gates)), by_h=gates,
                  regimes=frame.regime.nunique(), paired_age_rows=len(age), regime_h_rows=len(frame),
                  split_regimes={key: int(value) for key, value in frame.groupby("split").regime.nunique().items()},
                  estimator_methods=input_audit["estimator_methods"],
                  harmful_region_count=len(harms), harmful_regimes=int(bad.regime.nunique()),
                  harmful_regime_h_rows=len(bad), harmful_age_rows=len(bad_age),
                  worst_age_averaged=bad.head(5).to_dict("records"),
                  S3_proposals=evaluation_candidates[:3],
                  scientific_limits=["designed, resource-screened Sobol panel, not an operator population",
                                     "repeated h/age/side/rate within regimes are dependent",
                                     "working t intervals are descriptive, unadjusted for multiple search",
                                     "parity evaluation is exploratory internal validation, not new-regime S3",
                                     "tail-controlled truncated CTMC numerical results, not symbolic exactness"],
                  new_CTMC_evaluations=0, raw_commit=input_audit["raw_commit"],
                  analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    json_once(OUT / "results.json", result)
    timing = dict(cpu_seconds=time.process_time() - start, wall_seconds=time.perf_counter() - wall)
    json_once(OUT / "analysis_timing.json", timing)
    print(json.dumps({k: v for k, v in result.items() if k in ["status", "numeric_gate_counts", "harmful_regimes",
                     "harmful_region_count", "split_regimes", "gate_overall"]}, ensure_ascii=False))
    print(json.dumps(timing))


if __name__ == "__main__":
    main()
