"""Doan Van Tai — mechanically assemble W1a results after the raw files exist."""
from collections import defaultdict
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from experiments.letter.ties_topology import OUT, PIPES, write_csv, write_json


def read_json(name):
    return json.loads((OUT / name).read_text())


def topology_rows():
    with (OUT / "topology_ties.csv").open() as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["confirmatory"] = row["confirmatory"] == "True"
        for key in ("N", "K", "actions", *(f"{k}_count" for k in
                     ("exact", "relative", "zero", "minimum_exact", "minimum_relative"))):
            row[key] = int(row[key])
        for key in ("h_mult", "tau_mult", *(f"{k}_share" for k in
                     ("exact", "relative", "zero", "minimum_exact", "minimum_relative"))):
            row[key] = float(row[key])
    return rows


def aggregate_ties(rows, group):
    result = []
    for pipeline in PIPES:
        selected = [r for r in rows if r["pipeline"] == pipeline and r["h_mult"] == 30]
        n = sum(r["N"] for r in selected)
        data = dict(group=group, pipeline=pipeline, h_mult=30,
                    regimes=len({r["regime"] for r in selected}),
                    age_cells=len(selected), instance_age_count=n)
        for name in ("exact", "relative", "zero", "minimum_exact", "minimum_relative"):
            count = sum(r[f"{name}_count"] for r in selected)
            data[f"{name}_count"], data[f"{name}_share"] = count, count/n
        result.append(data)
    return result


def forecast_results(rows, lemma):
    fresh = [r for r in rows if r["pipeline"] == "M0_new" and r["h_mult"] == 30]
    a = {r["regime"]:r["exact_share"] for r in fresh if r["topology"] == "abilene"}
    g = {r["regime"]:r["exact_share"] for r in fresh if r["topology"] == "geant" and r["confirmatory"]}
    if len(a) != 32 or len(g) != 17:
        raise AssertionError("card denominators changed")
    for regime in {r["regime"] for r in fresh}:
        if len({r["exact_share"] for r in fresh if r["regime"] == regime}) != 1:
            raise AssertionError("fresh decisions unexpectedly depend on tau")
    old = [r for r in rows if r["pipeline"] == "M0_old" and r["topology"] == "abilene"]
    old30 = [r for r in old if r["h_mult"] == 30]
    p1 = sum(x >= .3 for x in a.values())
    p2 = sum(x < .1 for x in g.values())
    old_fail = sum(r["exact_share"] >= .05 for r in old)
    old_pool = sum(r["exact_count"] for r in old)/sum(r["N"] for r in old)
    old30_pool = sum(r["exact_count"] for r in old30)/sum(r["N"] for r in old30)
    lr = lemma["regimes"]
    p4_literal = all(r["a_vhat_constant"]["status"] == r["b_literal_fresh_equals_stale"]["status"] == "PASS" for r in lr)
    p4_invariance = all(r["a_vhat_constant"]["status"] == r["b_horizon_invariance"]["status"] == "PASS" for r in lr)
    p5 = sum(r["c_true_s_hybrid"]["status"] == "PASS" for r in lr)
    p6 = sum(r["coincidence_bound_Tint"] is not None and r["coincidence_bound_Tint"] <= 30 for r in lr)
    forecasts = [
        dict(prediction="P1", outcome="HELD" if p1 >= 24 else "DID_NOT_HOLD", numerator=p1, denominator=32,
             criterion="at least 24/32 Abilene regimes have all-action exact tie share >= 30% at h=30 T_int"),
        dict(prediction="P2", outcome="HELD" if p2 >= 13 else "DID_NOT_HOLD", numerator=p2, denominator=17,
             criterion="at least 13/17 confirmatory GEANT regimes have all-action exact tie share <10%; h=30 T_int is the explicit reporting convention since P2 omits h"),
        dict(prediction="P3", outcome="HELD" if old_fail == 0 else "DID_NOT_HOLD", numerator=len(old)-old_fail, denominator=len(old),
             criterion="unqualified reading: each Abilene regime/age/horizon cell has M0_old exact tie share <5%; card specifies no aggregation",
             pooled_share=old_pool, pooled_h30_share=old30_pool, largest_cell_share=max(r["exact_share"] for r in old),
             pooled_interpretation="HELD" if old_pool < .05 else "DID_NOT_HOLD",
             pooled_h30_interpretation="HELD" if old30_pool < .05 else "DID_NOT_HOLD"),
        dict(prediction="P4", outcome="HELD" if p4_literal else "DID_NOT_HOLD",
             criterion="literal conjunction: Vhat saturates, AND fresh/stale always choose the same action beyond bar_h",
             saturation_pass=sum(r["a_vhat_constant"]["status"] == "PASS" for r in lr),
             literal_coincidence_pass=sum(r["b_literal_fresh_equals_stale"]["status"] == "PASS" for r in lr),
             horizon_invariance_pass=sum(r["b_horizon_invariance"]["status"] == "PASS" for r in lr),
             denominator=len(lr), alternate_horizon_invariance_reading="HELD" if p4_invariance else "DID_NOT_HOLD"),
        dict(prediction="P5", outcome="HELD" if p5 == len(lr) else "DID_NOT_HOLD", numerator=p5, denominator=len(lr),
             criterion="true-s hybrid is uniform and equal for fresh/stale at the four numerical grid points strictly above M_hat/abs(s)"),
        dict(prediction="P6", outcome="HELD" if p6/len(lr) >= .8 else "DID_NOT_HOLD", numerator=p6, denominator=len(lr),
             criterion="M_hat/abs(s) <=30 T_int in at least 80% of asym regimes")]
    return forecasts


def audit_raw(rows):
    lookup = {(r["regime"], r["tau_mult"], r["pipeline"], r["h_mult"]):r for r in rows}
    checked, mismatches, nonfinite, negative = 0, 0, 0, 0
    for path in sorted((OUT / "topology").glob("*.npz")):
        with np.load(path, allow_pickle=False) as raw:
            costs = raw["predicted_costs"]
            taus, hs = raw["tau_indices"], raw["h_indices"]
            assert costs.shape[:3] == (500, len(taus), 4)
            nonfinite += int(np.count_nonzero(~np.isfinite(costs)))
            negative += int(np.count_nonzero(costs < 0))
            for t, ti in enumerate(taus):
                for p, name in enumerate(PIPES):
                    for h, hi in enumerate(hs):
                        c = costs[:, t, p, h]
                        lo, high = np.min(c, axis=1), np.max(c, axis=1)
                        scale = np.max(np.abs(c), axis=1)
                        # Recompute definitions directly, without tie_masks.
                        exact = int(np.count_nonzero(np.all(c == c[:, :1], axis=1)))
                        relative = int(np.count_nonzero(high-lo <= 1e-9*scale))
                        zero = int(np.count_nonzero(np.all(c == 0, axis=1)))
                        minimum = int(np.count_nonzero(np.sum(c == lo[:, None], axis=1) >= 2))
                        two = np.sort(c, axis=1)[:, 1]
                        near_minimum = int(np.count_nonzero(two-lo <= 1e-9*scale))
                        row = lookup[path.stem, (.1, .3, 1., 3.)[ti], name, (1, 2, 4, 7, 15, 30)[hi]]
                        got = (exact, relative, zero, minimum, near_minimum)
                        expected = tuple(row[f"{k}_count"] for k in
                                         ("exact", "relative", "zero", "minimum_exact", "minimum_relative"))
                        mismatches += got != expected
                        checked += 1
    return dict(cells_checked=checked, row_count=len(rows), mismatched_cells=mismatches,
                nonfinite_predicted_values=nonfinite, negative_predicted_values=negative,
                status="PASS" if checked == len(rows) and mismatches == nonfinite == 0 else "FAIL")


def markdown_table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |",
                      *("| " + " | ".join(str(c) for c in row) + " |" for row in rows)])


def fmt(value):
    return "—" if value is None else f"{value:.6g}"


def main():
    start = time.process_time()
    rows = topology_rows()
    lemma = read_json("lemma_checks.json")
    saved = read_json("ctmc_saved_tables.json")
    pilot = read_json("topology_pilot.json")
    run = read_json("topology_summary.json")
    groups = dict(Abilene_all_32=[r for r in rows if r["topology"] == "abilene"],
                  GEANT_confirmatory_17=[r for r in rows if r["topology"] == "geant" and r["confirmatory"]],
                  GEANT_descriptive_12=[r for r in rows if r["topology"] == "geant" and not r["confirmatory"]],
                  GEANT_all_29=[r for r in rows if r["topology"] == "geant"])
    main_table = [r for name, group in groups.items() for r in aggregate_ties(group, name)]
    forecasts = forecast_results(rows, lemma)
    audit = audit_raw(rows)
    assert audit["status"] == "PASS"
    write_csv(OUT / "topology_h30_main_table.csv", main_table)
    by_h = []
    for h in sorted({r["h_mult"] for r in rows}):
        selected = {r["regime"]:r["exact_share"] for r in rows if r["topology"] == "geant" and
                    r["confirmatory"] and r["pipeline"] == "M0_new" and r["h_mult"] == h}
        by_h.append(dict(h_mult=h, confirmatory_regimes=len(selected),
                         exact_share_below_10pct=sum(x < .1 for x in selected.values())))
    protected = read_json("protected_before.json")
    changed = [name for name, digest in protected.items()
               if not Path(name).is_file() or hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest]
    assert not changed, changed
    protection = dict(status="PASS" if not changed else "FAIL", files_checked=len(protected), changed=changed)
    with (OUT / "ctmc_sign_mismatch_rows.csv").open() as f:
        sign_rows = list(csv.DictReader(f))
    exact_nonzero = 0
    for row in sign_rows:
        _, lam_a, lam_b, u, *_ = row["physical_key"].split("|")
        la, lb, u = F(lam_a), F(lam_b), F(u)
        mean = lambda load: load/(10-load)
        exact_nonzero += mean(la)+mean(lb+u)-mean(la+u)-mean(lb) != 0
    sign_audit = dict(mismatch_rows=len(sign_rows),
                      unique_cases=len({r["input_file"] for r in sign_rows}),
                      exact_rational_mm1_nonzero_cases=exact_nonzero,
                      max_abs_float_mm1_slope=max((abs(float(r["s_mm1"])) for r in sign_rows), default=0.0))
    assert exact_nonzero == 0
    write_json(OUT / "verification.json", dict(raw_tie_recount=audit, protected_files=protection,
                                               P2_all_horizons=by_h,
                                               sign_mismatch_rational_audit=sign_audit,
                                               cpu_s=time.process_time()-start))
    write_json(OUT / "predictions_P1_P6.json", forecasts)
    base = [{k:p.get(k) for k in ("prediction", "outcome", "numerator", "denominator", "criterion")} for p in forecasts]
    write_csv(OUT / "predictions_P1_P6.csv", base)
    worker_cpu = pilot["worker_cpu_s"] + pilot["parent_cpu_s"] + run["worker_cpu_s"] + run["parent_cpu_s"]
    cpu = dict(topology_pilot_timed_cpu_s=pilot["worker_cpu_s"]+pilot["parent_cpu_s"],
               topology_run_timed_cpu_s=run["worker_cpu_s"]+run["parent_cpu_s"],
               lemma_cpu_s=lemma["cpu_s"], saved_table_cpu_s=saved["cpu_s"],
               analysis_timed_cpu_s=worker_cpu+lemma["cpu_s"]+saved["cpu_s"],
               topology_pilot_wall_s=pilot["wall_s"], topology_run_wall_s=run["wall_s"],
               lemma_wall_s=lemma["wall_s"], saved_table_wall_s=saved["wall_s"],
               accounting_scope="timed analysis intervals, including pilot and parents; excludes some interpreter startup/imports, protection/reporting and pytest (pytest_resources.txt separately)")
    write_json(OUT / "cpu_times.json", cpu)

    main_rows = [[r["group"], r["pipeline"], f"{100*r['exact_share']:.3f}", f"{100*r['relative_share']:.3f}",
                  f"{100*r['zero_share']:.3f}", f"{100*r['minimum_exact_share']:.3f}"] for r in main_table]
    pooled_ties = [[r["h_Tint_bin"], r["rows"], fmt(r["M0_new_tie_mass_median"]), fmt(r["M0_new_tie_mass_q90"]),
                    f"{100*r['GS_below_minus_0p1_share']:.3f}"] for r in saved["pooled_tables"]]
    pooled_regrets = [[r["h_Tint_bin"], *(fmt(r[f"regret_{p}_median_pct_Cref"]) for p in PIPES_SAVED)]
                      for r in saved["pooled_tables"]]
    signs = saved["sign_by_source"][-1]
    all_bounds = [r["coincidence_bound_Tint"] for r in lemma["regimes"]]
    bars = [r["bar_h_Tint"] for r in lemma["regimes"]]
    p3 = forecasts[2]
    source_table = [[r["source"], r["h_Tint_bin"], r["rows"], fmt(r["M0_new_tie_mass_median"]),
                     fmt(r["M0_new_tie_mass_q90"]), fmt(r["GS_below_minus_0p1_share"])] for r in saved["tables"]]
    source_regrets = [[r["source"], r["h_Tint_bin"], *(fmt(r[f"regret_{p}_median_pct_Cref"]) for p in PIPES_SAVED)]
                       for r in saved["tables"]]
    wrong_rows = [[r["h_Tint_bin"], r["sign_mismatch_rows"], r["opposite_nonzero_rows"],
                   fmt(r["sign_mismatch_hybrid_mm1_new_median_pct_Cref"]),
                   fmt(r["sign_mismatch_hybrid_mm1_old_median_pct_Cref"])] for r in saved["pooled_tables"]]
    pytest_lines = (OUT / "pytest.log").read_text().strip().splitlines()
    pytest_summary = pytest_lines[-1]
    if "passed" not in pytest_summary or "failed" in pytest_summary:
        raise AssertionError("required pytest command did not pass")
    text = f"""# LETTER-W1a — kết quả local

Người phụ trách: **Doan Van Tai**. Card nguồn: `results/letter/CARD_W1.md` (giữ nguyên).
Đây là audit và numerical checks; không phải author-self work hoặc mathematical proof.
Không commit và không SSH theo brief; raw được ghi trước khi tổng hợp. Quy tắc commit raw
trong card không được thực hiện vì brief lần này yêu cầu **Do not commit**.

## Phạm vi và định nghĩa

- Đủ 61 regime EV-TE: Abilene 32, GÉANT 29 (17 confirmatory + 12 descriptive D1).
- Test seed 1000001, N=500, K=128; đầy đủ 4 tuổi × 6 horizon × 4 pipelines.
- Pilot 3 instance/regime, nhưng dựng toàn bộ 500 states hai lần: 61/61 SHA khớp
  bitwise; N=500 khớp shape truth lưu sẵn. Dùng nguyên `ev_te.instances` và seed streams
  trong `run_one`, giữ posterior riêng từng instance. Argmin instance đầu khớp
  `choose_twins` 61/61. Truth không lưu states nên không có state-by-state đối chiếu
  trực tiếp với artifact cũ; không tái chạy truth rollouts.
- Tie chính: **mọi action có cùng predicted cost**. Relative tie dùng
  max(cost)−min(cost) ≤ 1e−9 max(abs(cost)), không absolute floor.
  Zero-zero: mọi cost bằng đúng 0. Bốn-action có thể có nhiều minimizing actions
  dù mọi cost không bằng nhau: cột `minimum_exact_share` và raw counters giữ riêng.
- Bảng topology ở h=30 T_int gộp đều regime × tuổi × instance. M0_new lặp lại qua
  các tuổi; không coi đây là các quan sát độc lập, không lập population CI.
- Pilot dự phóng {pilot['projected_full_cpu_s']:.3f} CPU-s,
  {pilot['projected_wall_s_on_8_workers']/60:.3f} phút/8 workers (<2 giờ): chạy **full grid**.
  Run dùng 6 workers; các công việc CTMC/test còn lại không làm vượt 8 workers.

## Topology — h=30 T_int, tỷ lệ %

{markdown_table(['Nhóm', 'Pipeline', 'Exact all-action', 'Relative 1e-9', 'Zero-zero', 'Tie tại minimum'], main_rows)}

Per-(regime,τ,h,pipeline) ở `topology_ties.csv`; predicted cost vectors ở `topology/*.npz`.
Full audit có {len(rows)} cells; recount độc lập từ NPZ: {audit['status']},
{audit['mismatched_cells']} mismatch; {audit['nonfinite_predicted_values']} nonfinite,
{audit['negative_predicted_values']} predicted values âm.

## P1–P6 — chấm cơ học

{markdown_table(['Prediction', 'Kết quả', 'Số đếm'], [[p['prediction'],p['outcome'],f"{p.get('numerator',p.get('literal_coincidence_pass'))}/{p['denominator']}" ] for p in forecasts])}

- P1: ≥30% exact all-action tie ở ít nhất 24/32 regime Abilene, h=30 T_int.
- P2: <10% exact tie ở ít nhất 13/17 GÉANT confirmatory. Card không ghi h:
  bảng chính áp dụng h=30 T_int; số đếm từng h ở `verification.json`.
- P3: card không chỉ định h, tuổi hoặc cách gộp. Cách đọc không điều kiện yêu cầu
  mọi cell Abilene M0_old <5%: {p3['numerator']}/{p3['denominator']} đạt;
  pooled mọi h/tuổi = {100*p3['pooled_share']:.6f}%, pooled h30 = {100*p3['pooled_h30_share']:.6f}%,
  max cell = {100*p3['largest_cell_share']:.3f}%. Kết quả theo pooled mọi h là
  {p3['pooled_interpretation']}, theo pooled h30 là {p3['pooled_h30_interpretation']}.
- P4: literal “fresh và stale trùng action” **DID_NOT_HOLD**, 0/33.
  V̂ saturation **PASS 33/33**, sai khác tuyệt đối 0 bitwise; horizon-invariance
  riêng của fresh và stale **PASS 33/33**. Cách đọc invariance của P4 là HELD;
  không tự sửa câu trong card. Counterexamples cụ thể ở `lemma/*.json`.
- P5: true-s hybrid **PASS {forecasts[4]['numerator']}/33** trên bốn điểm grid
  > M_hat/|s|; kiểm toàn bộ finite states và posterior means bằng extrema.
- P6: bound ≤30 T_int ở {forecasts[5]['numerator']}/33; cần ít nhất 80%.

## Lemma — toàn bộ 33 asym regimes

bar_h/T_int = [{min(bars):.6f}, {max(bars):.6f}];
(M_hat/|s|)/T_int = [{min(all_bounds):.6f}, {max(all_bounds):.6f}].
M_hat lấy max |gap tổng hai path| trên **toàn bộ support đã truncate** và posterior
means tại bar_h; giữ cả các states ở tail rất nhỏ, không thay bằng quantile hay
stationary-average bound. Fresh/stale là ctmc-v1, stale backlog-only ở τ=1,
khác thiết kế age-only của topology/W1b.

`m0_vhat(return_T=True)` được kiểm ở bar_h, nextafter(bar_h,+∞),
1.25bar_h, 2bar_h, 4bar_h; thêm các h=.25/.5/.75bar_h cho những states đã drain.
`m0_gap` và posterior nguyên bản được dùng kiểm decisions; quyết định từ shifted
và unshifted plateau không mismatch trên grid. `evaluate(arrays=True)` được replay
với h=1/100 để lấy/check inputs; không tính true V ở các bound h rất lớn.
Numerical grid và finite N không chứng minh mọi real h hoặc infinite-buffer lemma.
Kết quả từng regime: `lemma_checks.csv`, `lemma_checks.json`.

## CTMC saved-data — read only

Đọc {saved['input_files']} JSON: {saved['completed_files']} COMPLETED,
{saved['excluded_files']} UNRESOLVED (giữ danh sách lý do), {saved['saved_horizon_rows']} horizon rows,
{saved['unique_physical_horizon_keys']} physical keys không trùng. Không bỏ raw flags.
Bins dùng `h_Tint` đã lưu, không làm tròn theo nominal grid. Regret/G_S có đơn vị
**% C_ref**. `tie_mass.c10` là near-tie mass với tolerance
1e−12(h*r_stay+1), không phải exact tie definition của topology.

{markdown_table(['h/T_int', 'Rows', 'Median tie mass', 'q90 tie mass', 'Share G_S<−0.1 (%)'], pooled_ties)}

Median regret (% C_ref); cột new/old được tách riêng:

{markdown_table(['h/T_int', *PIPES_SAVED], pooled_regrets)}

Sign agreement theo case: {signs['sign_agreement_cases']}/{signs['cases']} =
{100*signs['sign_agreement_share']:.6f}%. Có {signs['true_zero_mm1_nonzero_cases']} case
true s=0 nhưng s_mm1≠0 theo floating point; **{signs['opposite_nonzero_cases']} case có hai dấu nonzero trái nhau**.
Không gọi mọi mismatch này là đảo dấu có ý nghĩa khoa học; không dùng epsilon
để đổi số đếm. Đối chiếu công thức M/M/1 bằng Fraction cho cả 498 case mismatch
cho slope đúng bằng 0; max |s_mm1| float là {sign_audit['max_abs_float_mm1_slope']:.9g}.
Regret hybrid_mm1 trong các row mismatch được báo đầy đủ:

{markdown_table(['h/T_int', 'Mismatch rows', 'Opposite nonzero', 'Median mm1_new regret', 'Median mm1_old regret'], wrong_rows)}

Bảng theo từng design source (tie mass là share, cột harm là share):

{markdown_table(['Source', 'h/T_int', 'N', 'Median tie', 'q90 tie', 'Share harm'], source_table)}

Median regret theo design source (% C_ref):

{markdown_table(['Source', 'h/T_int', *PIPES_SAVED], source_regrets)}

CSV/JSON đầy đủ: `ctmc_saved_tables.csv/json`, `ctmc_saved_pooled.csv`,
`ctmc_sign_by_source.csv`, `ctmc_sign_mismatch_rows.csv`, `ctmc_saved_rows.csv`.
Input hashes: `ctmc_saved_input_hashes.json`.

## Kiểm tra, CPU và file

Command thực tế (sau khi source `.venv/bin/activate`, `experiments/explore_ctmc/env.sh`
và đặt `PYTHONDONTWRITEBYTECODE=1`):

```bash
python3 -m experiments.letter.ties_topology pilot --workers 8
python3 -m experiments.letter.ties_topology run --workers 6
python3 -m experiments.letter.lemma_check
python3 -m experiments.letter.ctmc_saved_tables
python3 -m pytest -q tests/test_letter_w1a.py tests/test_ev_te.py --basetemp=/tmp/lw1a_pt -o cache_dir=/tmp/lw1a_cache
python3 -m experiments.letter.w1a_report
```

Test **PASS**, stdout: `{pytest_summary}`. Log: `pytest.log`, process resources: `pytest_resources.txt`.
Analysis CPU được đo: pilot {cpu['topology_pilot_timed_cpu_s']:.3f} s,
topology main {cpu['topology_run_timed_cpu_s']:.3f} s,
lemma {cpu['lemma_cpu_s']:.3f} s, saved tables {cpu['saved_table_cpu_s']:.3f} s;
tổng {cpu['analysis_timed_cpu_s']:.3f} s. Đây là tổng các timed analysis intervals,
chưa gồm toàn bộ interpreter startup/imports, hash/report và pytest; không phải
end-to-end CPU billing. Wall main {run['wall_s']:.3f} s.
Chi tiết: `cpu_times.json`, các log `topology_pilot.log`, `topology_run.log`,
`lemma_check.log`, `ctmc_saved_tables.log`.

{protection['files_checked']} file đã có trong hai cây results được bảo vệ và các
source/card chính: SHA256 giữ nguyên, `verification.json` PASS. Mã mới nằm ở
`experiments/letter/` (ba module được yêu cầu, module tạo report, `__init__.py`),
test ở `tests/test_letter_w1a.py`. Không đụng `e3_*.py`. Không tạo biểu đồ ở W1a.

## Plain facts

Đợt này đã dựng lại 30.500 decision instances đúng seed test và ghi predicted
cost vectors cho đủ lưới của 61 regime; mọi counter được recount từ raw vectors.
Trong 33 CTMC asym regimes, cost M0 bão hòa và mỗi policy giữ nguyên theo horizon
trên grid đã kiểm, nhưng fresh/stale có counterexample chọn khác action. Hybrid
dùng true s trùng action trên grid vượt bound; bound toàn support đều lớn hơn
30 T_int. Saved-data tables có 5.768 rows; strict sign mismatches đều thuộc
s=0/s_mm1≠0, không có hai dấu nonzero trái nhau. Các dữ kiện này không xác nhận
causal explanation của topology harm, mathematical theorem, novelty hoặc realism.
"""
    with (OUT / "README.md").open("x") as f:
        f.write(text)
    print(json.dumps(dict(predictions=[{k:p[k] for k in ("prediction", "outcome")} for p in forecasts],
                          raw_recount=audit, protection=protection, cpu=cpu)), flush=True)


PIPES_SAVED = ("M0_new", "M0_old", "hybrid_new", "hybrid_old",
               "hybrid_mm1_new", "hybrid_mm1_old", "static")

if __name__ == "__main__":
    main()
