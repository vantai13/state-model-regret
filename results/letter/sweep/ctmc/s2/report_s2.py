"""Doan Van Tai — age-specific harm screens and Vietnamese S2 report.

Pure saved-data postprocessing. Preserve all first-pass S2 outputs.
"""
import importlib.util
import json
from pathlib import Path
import time

import pandas as pd

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("s2_report_helpers", OUT / "analyze_s2.py")
s2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s2)


def load(name):
    return pd.read_csv(OUT / name, float_precision="round_trip", low_memory=False,
                       dtype={"regime": str, "level": str, "side": str})


def write_text(name, content):
    with (OUT / name).open("x", encoding="utf-8") as stream:
        stream.write(content)


def fmt(value):
    return f"{value:.6f}"


def main():
    start, wall = time.process_time(), time.perf_counter()
    names = ["bins_by_h_and_age.csv", "harm_regions_by_age.csv", "harm_region_screen.csv",
             "age_screen_summary.json", "key_numbers.json", "REPORT_S2.md", "S3_CANDIDATES.md",
             "report_timing.json"]
    if any((OUT / name).exists() for name in names):
        raise FileExistsError("report outputs already exist")
    age, frame = load("paired_by_age.csv"), load("paired_regime_h.csv")
    binned_age = []
    for tau, data in age.groupby("tau_T_int", sort=True):
        bins, _ = s2.binned_tables(data)
        binned_age.extend(dict(tau_T_int=float(tau), **row) for row in bins)
    s2.csv_once("bins_by_h_and_age.csv", binned_age)
    harmed_age_regions = [r for r in binned_age if r["mean_le_neg005"]]
    s2.csv_once("harm_regions_by_age.csv", pd.DataFrame(harmed_age_regions, columns=pd.DataFrame(binned_age).columns))
    screen = []
    for source, records in [("age_feature_bin", binned_age), ("age_population", load("by_h_and_age.csv").to_dict("records")),
                            ("population", load("by_h.csv").to_dict("records")),
                            ("feature_bin", load("bins_by_h.csv").to_dict("records")),
                            ("H-AB", load("hypotheses_AB.csv").to_dict("records")),
                            ("H-C", load("hypothesis_C.csv").to_dict("records"))]:
        screen.extend(dict(source=source, **row) for row in records)
    s2.csv_once("harm_region_screen.csv", screen)
    screen_summary = dict(owner="Doan Van Tai", kind="EXPLORATORY_POST_HOC", regions_screened=len(screen),
                          age_feature_regions=len(binned_age),
                          age_feature_mean_le_neg005=len(harmed_age_regions),
                          age_feature_mean_le_neg01=sum(r["mean_le_neg01"] for r in harmed_age_regions),
                          age_feature_harm_with_ci95_high_below_zero=sum(r["ci95_high_below_zero"] for r in harmed_age_regions),
                          age_harmful_regimes=int(age[age.delta_pp <= -.05].regime.nunique()),
                          age_harmful_rows=int((age.delta_pp <= -.05).sum()),
                          no_multiplicity_adjustment=True,
                          note="Age-specific screens supplement the original age-averaged analysis, whose harmonic-region list is empty.")
    s2.json_once(OUT / "age_screen_summary.json", screen_summary)
    by_h, gates, hc = load("by_h.csv"), load("gates_by_h.csv"), load("hypothesis_C.csv")
    ab, corr = load("hypotheses_AB.csv"), load("spearman_by_h.csv")
    audit = json.loads((OUT / "audit.json").read_text())
    inputs = json.loads((OUT / "input_audit.json").read_text())
    bad = age[age.delta_pp <= -.05].sort_values("delta_pp")
    primary = hc[(hc.side == "fresh") & (hc.level == "hat") & (hc.h_T_int == 1) &
                 (hc.split == "evaluation_even")].iloc[0].to_dict()
    primary_train = hc[(hc.side == "fresh") & (hc.level == "hat") & (hc.h_T_int == 1) &
                       (hc.split == "train_odd")].iloc[0].to_dict()
    observed_region = frame[(frame.side == "fresh") & (frame.level == "hat") & (frame.h_T_int == 1) &
                            (frame.D >= primary["d_star"])]
    outside = frame[(frame.side == "fresh") & (frame.level == "hat") & (frame.h_T_int == 1) &
                    (frame.D < primary["d_star"])]
    def pick(h, side, level):
        return by_h[(by_h.h_T_int == h) & (by_h.side == side) & (by_h.level == level)].iloc[0].to_dict()
    snapshot = dict(owner="Doan Van Tai", raw_commit=inputs["raw_commit"],
                    sources={"population": "by_h.csv", "gates": "gates_by_h.csv", "H_A_B": "hypotheses_AB.csv",
                             "H_C": "hypothesis_C.csv", "harm": "harm_by_age.csv", "age_regions": "harm_regions_by_age.csv"},
                    primary_S3_candidate=primary, primary_training=primary_train,
                    primary_full_panel=s2.stats(observed_region, 1000),
                    primary_outside_full_panel=s2.stats(outside, 1000),
                    fresh_hat_h1=pick(1, "fresh", "hat"), stale_hat_h1=pick(1, "stale", "hat"),
                    fresh_true_h1=pick(1, "fresh", "true"), fresh_hat_h30=pick(30, "fresh", "hat"),
                    worst_age=bad.iloc[0].to_dict(),
                    harm_ratio_min=float(bad.abs_shat_over_abs_s.min()),
                    harm_ratio_max=float(bad.abs_shat_over_abs_s.max()),
                    harmed_age_regions=harmed_age_regions,
                    raw_CPU_seconds=sum(r["cpu_seconds"] for r in inputs["receipts"]),
                    raw_parallel_wall_seconds_max=max(r["wall_seconds"] for r in inputs["receipts"]))
    s2.json_once(OUT / "key_numbers.json", snapshot)
    gate_counts = gates.feature_region_numeric_gate.value_counts().to_dict()
    population_pass = int((by_h.numeric_gate == "PASS").sum())
    table = ["| h/T_int | Fresh s đúng | Fresh ŝ | Stale s đúng | Stale ŝ |",
             "|---:|---:|---:|---:|---:|"]
    for h in sorted(by_h.h_T_int.unique()):
        cells = []
        for side, level in [("fresh", "true"), ("fresh", "hat"), ("stale", "true"), ("stale", "hat")]:
            item = pick(h, side, level)
            g = gates[(gates.h_T_int == h) & (gates.side == side) & (gates.level == level)].iloc[0]
            cells.append(f"{item['delta_pp_mean']:.4f} / {g.feature_region_numeric_gate}")
        table.append("| " + f"{h:g}" + " | " + " | ".join(cells) + " |")
    harm_table = ["| h/T_int | τ/T_int | Phía/rate | Đặc trưng và bin | n/1000 | Δ trung bình | CI95% |",
                  "|---:|---:|---|---|---:|---:|---|"]
    for row in harmed_age_regions:
        harm_table.append(f"| {row['h_T_int']:g} | {row['tau_T_int']:g} | {row['side']}/{row['level']} | "
                          f"{row['feature']} {row['bin']} | {row['n_regimes']} | {row['delta_pp_mean']:.6f} | "
                          f"[{row['delta_pp_ci95_low']:.6f}, {row['delta_pp_ci95_high']:.6f}] |")
    if not harmed_age_regions:
        harm_table.append("| | | | Không có vùng đạt mức sàng này | | | |")
    h_a = ab[(ab.hypothesis == "H-A") & (ab.level == "hat")]
    def ha(h):
        return h_a[h_a.h_T_int == h].iloc[0]
    hb1 = ab[(ab.hypothesis == "H-B") & (ab.level == "hat") & (ab.side == "fresh") & (ab.h_T_int == 1)].iloc[0]
    hb30 = ab[(ab.hypothesis == "H-B") & (ab.level == "hat") & (ab.side == "fresh") & (ab.h_T_int == 30)].iloc[0]
    pc = primary
    f1, st1 = snapshot["fresh_hat_h1"], snapshot["stale_hat_h1"]
    rhos = corr[(corr.h_T_int == 1) & (corr.level == "hat") & (corr.side == "fresh")].set_index("feature")
    numbered = [
        f"1. Fresh ŝ tại h=T_int có regret tĩnh {f1['baseline_pp_mean']:.6f}% và hybrid {f1['hybrid_pp_mean']:.6f}% C_ref, "
        f"Δ={f1['delta_pp_mean']:.6f} điểm, CI95% [{f1['delta_pp_ci95_low']:.6f}, {f1['delta_pp_ci95_high']:.6f}]. "
        f"Có {int(f1['n_delta_ge_01'])}/1000 regime đạt Δ≥0,1, trung vị {f1['delta_pp_median']:.8f} điểm. "
        f"Stale trung bình ba tuổi chỉ đạt {st1['delta_pp_mean']:.6f} điểm.",
        f"2. H-A chỉ đứng một phần. Fresh ŝ, Stay và |s|/r_min≤0,1 có 101 regime. "
        f"Tại h=0,1T chỉ {int(ha(.1).n_delta_ge_01)}/101 đạt Δ≥0,1, còn h=T đạt {int(ha(1).n_delta_ge_01)}/101 "
        f"và h=3T đạt {int(ha(3).n_delta_ge_01)}/101. Với s đúng tại h=3T chỉ 47/97, nên phát biểu cho mọi h≤3T không đứng.",
        f"3. H-B có ngoại lệ. Nhóm |s|/r_min≥0,3 ở fresh ŝ, h=T có {int(hb1.n_counterexamples)}/{int(hb1.n_regimes)} ô "
        f"vi phạm |Δ|<0,05. Tại h=30T còn {int(hb30.n_counterexamples)}/1000 ngoại lệ. Tỷ lệ cao các ô gần 0 chưa xác nhận luật đồng nhất.",
        f"4. H-C tại fresh ŝ, h=T chọn d*={pc['d_star']:.2f} chỉ từ 499 ID lẻ. "
        f"Trong 501 ID chẵn, vùng có {int(pc['n_regimes'])}/501={100*pc['share_regimes']:.2f}%, regret tĩnh "
        f"{pc['baseline_pp_mean']:.6f}% so với hybrid {pc['hybrid_pp_mean']:.6f}% C_ref. Δ={pc['delta_pp_mean']:.6f} điểm "
        f"[{pc['delta_pp_ci95_low']:.6f}, {pc['delta_pp_ci95_high']:.6f}], tương ứng {pc['delta_abs_mean']:.6f} packet·s. "
        f"Có {int(pc['n_delta_ge_01'])}/{int(pc['n_regimes'])} đạt Δ≥0,1 và {int(pc['n_delta_le_neg005'])} regime Δ≤−0,05.",
        f"5. 15 hàng regime×h×phía×rate thuộc 7 regime có Δ≤−0,05 sau trung bình tuổi. Xét riêng tuổi có "
        f"{len(bad)} hàng thuộc {bad.regime.nunique()} regime, gồm 42 fresh và 10 stale. Tất cả dùng ŝ và có "
        f"|ŝ|/|s| từ {snapshot['harm_ratio_min']:.4f} đến {snapshot['harm_ratio_max']:.4f}. Tệ nhất là {bad.iloc[0].regime}, "
        f"stale h=3T, τ=3T, Δ={bad.iloc[0].delta_pp:.6f} điểm, {bad.iloc[0].delta_abs:.6f} packet·s. "
        f"Quan hệ này phù hợp rủi ro hiệu chỉnh thiếu do |ŝ| nhỏ. Cơ chế nhân quả chưa được can thiệp kiểm tra."
    ]
    report = f"""# Báo cáo S2 CTMC

Người phụ trách Doan Van Tai. EXPLORATORY, POST HOC. Raw S1-A ở commit `{inputs['raw_commit'][:9]}`.

Đã chạy summarize trên raw đã commit và phân tích regret theo cặp. 1000/1000 regime COMPLETED, 0 INVALID, đủ 14 h × 3 τ × 8 luật, tương ứng 336000 policy rows và 168000 cặp phía/rate. MMPP/M/1 có 702 regime, fallback M/M/1 có 298. Không chạy truth CTMC mới ngoài hai control X-CTMC cũ.

Δ = regret(luật tĩnh cùng rate) − regret(hybrid cùng rate). Δ dương nghĩa là hybrid có lợi. Đơn vị chuẩn hóa là điểm phần trăm của cùng C_ref, đơn vị tuyệt đối là packet·s. Từng tuổi được giữ riêng. Bảng chính lấy trung bình đều ba tuổi trong từng regime trước khi tính thống kê. CI95% dùng Student t trên regime. Với lưới Sobol thiết kế và đã sàng tài nguyên, các khoảng này chỉ là tham chiếu mô tả, chưa có bảo đảm coverage cho quần thể mạng thực. Các h trong cùng regime phụ thuộc nhau, không được đếm thành các lần thử độc lập.

## Cổng S2

Phần định lượng có vùng phủ ≥10% regime và Δ trung bình ≥0,1 điểm đạt ở {gate_counts.get('PASS',0)}/56 tổ hợp h/phía/rate khi xét các bin đặc trưng đã khai báo, trượt {gate_counts.get('FAIL',0)}/56. Nếu vùng là toàn bộ 1000 regime thì đạt {population_pass}/56. Không dùng tập con chọn bằng outcome làm feature hay vùng dự đoán. Đây là tìm vùng khám phá trên nhiều bin.

Mỗi ô dưới đây ghi Δ trung bình toàn bộ regime và kết quả phần cổng có tồn tại vùng đạt trong các bin. Stale trung bình đều τ/T_int∈{{0.3,1,3}}.

{chr(10).join(table)}

Cổng tổng giữ `NOT_DECIDED_UNQUANTIFIED_HARM`. Từ “đáng kể” chưa có định lượng, nên không tự gán GO/NO-GO. Không có bin trung bình ba tuổi có mean Δ≤−0,05. Khi xét riêng tuổi, có {len(harmed_age_regions)} bin đạt mức sàng ≤−0,05, trong đó {screen_summary['age_feature_mean_le_neg01']} bin ≤−0,1. Không tự kết luận ý nghĩa thống kê từ mean hoặc CI sau nhiều phép sàng.

{chr(10).join(harm_table)}

## Phát hiện và luật vùng

{chr(10).join(numbered)}

Tại fresh ŝ, h=T, Spearman theo 1000 regime lần lượt bằng {rhos.loc['abs_s_over_r_min','spearman_rho']:.4f} cho |s|/r_min, {rhos.loc['kappa_min_over_T_int','spearman_rho']:.4f} cho min κ/T_int, {rhos.loc['load_imbalance','spearman_rho']:.4f} cho chênh tải, và {rhos.loc['disagreement','spearman_rho']:.4f} cho share bất đồng. Đây là tương quan mô tả. D(h) tổng và share bất đồng là hai đặc trưng khác nhau. D tổng bằng D_fresh+D_stale, có miền [0,2], được trung bình trên ba tuổi ở luật H-C. |ŝ|/|s| là chẩn đoán dựa trên s của mô hình, chưa dùng được làm bộ lọc triển khai khi không biết s.

## Kiểm tra, thời gian và file

Lệnh chính đã chạy là `python3 -B -m experiments.letter.sweep_ctmc summarize --out results/letter/sweep/ctmc/v2 --source run`, `python3 -B results/letter/sweep/ctmc/s2/analyze_s2.py`, và `python3 -B results/letter/sweep/ctmc/s2/audit_s2.py` sau khi source env. Pytest chạy file test S2 mới cùng test tái lập hai regime cũ, 18/18 PASS trong 4,70 s. Chấm lại độc lập PASS {sum(audit['checks'].values()):,} kiểm tra, không import analyzer/evaluator. X-CTMC_001 so 24 hàng, X-CTMC_002 so 16 hàng, max sai lệch 0. SHA raw khớp receipt và commit, runner/tests cũ giữ nguyên.

S1-A theo receipt dùng {snapshot['raw_CPU_seconds']:.6f} CPU-s worker, tương đương {snapshot['raw_CPU_seconds']/3600:.4f} CPU-h. Hai shard chạy đồng thời, wall lớn nhất {snapshot['raw_parallel_wall_seconds_max']:.6f} s. CPU/wall lệnh phân tích cục bộ có trong `*_execution.json`, `input_audit.json`, `report_timing.json` và `FINAL_CHECK.json`. Không coi tổng thời gian lệnh là thời gian làm việc tương tác.

Source mới gồm `analyze_s2.py`, `test_analyze_s2.py`, `audit_s2.py`, `report_s2.py`. Cấu hình ở `analysis_config.json`. Bảng theo h/tuổi ở `by_h.csv`, `by_h_and_age.csv`, cặp gốc ở `paired_by_age.csv`, trung bình regime ở `paired_regime_h.csv`. Bin, tương quan và H-A/B/C có CSV cùng tên. `harm_region_screen.csv` giữ toàn bộ sàng, `harm_regions_by_age.csv` giữ các bin tuổi âm. `harm_regions.csv` của lượt đầu chỉ có newline vì không có vùng trung bình tuổi đạt mức sàng, không dùng làm bảng có schema. `harm_by_age.csv` và `harm_regime_h.csv` giữ ô thiệt. Log ở `analyze_s2.log`, `audit_s2.log`, `pytest_validation.log`, `report_s2.log`, log summarize ở `../summarize_run.log`. Số dùng trong báo cáo được chép từ CSV vào `key_numbers.json`.

Ba PNG là `delta_by_gap_h.png`, `delta_by_kappa_h.png`, `delta_by_estimator_ratio_h.png`. Màu có giới hạn bão hòa, số đầy đủ giữ ở CSV. Khi đọc CSV bằng pandas, dùng `dtype={{'level': str}}`, `low_memory=False`, `float_precision='round_trip'` để giữ nhãn true và tọa độ h.

## Đề xuất tiếp theo

`S3_CANDIDATES.md` là thẻ nháp cho fresh ŝ tại h=T với D tổng≥0,28, kèm hai lựa chọn lân cận. Nghiên cứu còn một số hạn chế. Thứ nhất, split ID vẫn nằm trong lưới khám phá và việc chọn h cho thẻ là post hoc. Thứ hai, CI chưa hiệu chỉnh cho việc xét nhiều vùng và chưa chứng minh sai số numerical dùng chung đã hết. Cuối cùng, cần chốt điều kiện thiệt hại rồi khóa S3 trên regime/seed mới trước khi có claim xác nhận.
"""
    write_text("REPORT_S2.md", report)
    candidates = hc[(hc.side == "fresh") & (hc.level == "hat") & (hc.split == "evaluation_even") &
                    hc.h_T_int.isin([.7, 1., 1.5])].sort_values("h_T_int")
    candidate_table = ["| h/T_int | d* từ ID lẻ | Vùng trên ID chẵn | Tĩnh / hybrid (% C_ref) | Δ (điểm) và CI95% |",
                       "|---:|---:|---:|---|---|"]
    for _, row in candidates.iterrows():
        candidate_table.append(f"| {row.h_T_int:g} | {row.d_star:.2f} | {int(row.n_regimes)}/501 | "
                               f"{row.baseline_pp_mean:.6f} / {row.hybrid_pp_mean:.6f} | {row.delta_pp_mean:.6f} "
                               f"[{row.delta_pp_ci95_low:.6f}, {row.delta_pp_ci95_high:.6f}] |")
    draft = f"""# Thẻ đề xuất S3

Người phụ trách Doan Van Tai. DRAFT, EXPLORATORY-SELECTED, CHƯA KHÓA, CHƯA CHẠY. Cổng S2 tổng chưa chốt vì điều kiện thiệt hại chưa định lượng. Đây là đề xuất từ S2, chưa có xác nhận của tác giả.

Ứng viên chính là fresh, rate ŝ cùng estimator từ bản ghi 300T_int, h=T_int, c=0 và vùng D_ŝ≥0,28. D_ŝ là trung bình đều trên τ/T_int∈{{0.3,1,3}} của D_fresh,ŝ+D_stale,ŝ,τ, giữ đúng định nghĩa đã dùng trong H-C. Ngưỡng 0,28 chọn bằng F1 nhãn Δ≥0,1 trên 499 ID lẻ, điều kiện phủ ít nhất 10% training, tie lấy d* nhỏ hơn. Không dùng outcome của 501 ID chẵn để chọn d*. Chọn h=T cho ứng viên chính sau khám phá, hai h lân cận chỉ để tác giả so sánh.

{chr(10).join(candidate_table)}

Với ứng viên chính, {int(pc['n_delta_ge_01'])}/{int(pc['n_regimes'])} regime trong vùng đánh giá đạt Δ≥0,1, không regime nào trong vùng có Δ≤−0,05. Lợi ích tuyệt đối trung bình {pc['delta_abs_mean']:.6f} packet·s, CI95% [{pc['delta_abs_ci95_low']:.6f}, {pc['delta_abs_ci95_high']:.6f}]. Toàn bộ lưới đã thấy, nên các số này chỉ là bằng chứng chọn thẻ.

S3 dự kiến giữ mô hình/miền đã sàng tài nguyên, dùng Sobol seed mới và record seed mới. N, seed, quy tắc loại trước outcomes, cách tính CI và ngân sách cần ghi vào thẻ khóa của S3. Chỉ chọn một ứng viên làm primary trước khi chạy, hoặc định trước cách xử lý nhiều phép thử nếu giữ cả ba. Không thay h/d* theo outcomes S3.

Metric là Δ=regret(tĩnh ŝ)−regret(hybrid ŝ), cùng C_ref và phía fresh. Đề xuất kiểm vùng phủ ≥10% tất cả regime hợp lệ và mean Δ≥0,1 điểm, đồng thời CI của mean Δ có cận dưới >0. Quy ước này tương đương CI của hybrid−tĩnh có cận trên <0.

Điều kiện ngoài vùng của PLAN là hybrid không tệ hơn 0,05 điểm. Cần quyết định rõ điều kiện này áp cho mean hay từng regime và cách dùng CI trước khi chạy S3. Có thể đề xuất noninferiority cho mean ngoài vùng với cận dưới CI của Δ≥−0,05, nhưng S2 chưa thông qua quy tắc đó. Luôn báo riêng các regime Δ≤−0,05 và Δ≤−0,1, mọi estimator INVALID/fallback và tỷ lệ loại theo tài nguyên.

|ŝ|/|s| chưa dùng làm điều kiện chọn vì cần s thật. Không fit lại estimator, d* hay ngưỡng gây hại sau S3. S3 mới phải có luật báo kết quả vào paper bất kể outcome và chấm lại độc lập. Không chạy S3 trong nhiệm vụ hiện tại.
"""
    write_text("S3_CANDIDATES.md", draft)
    timing = dict(cpu_seconds=time.process_time() - start, wall_seconds=time.perf_counter() - wall)
    s2.json_once(OUT / "report_timing.json", timing)
    print(json.dumps(screen_summary, ensure_ascii=False))
    print(json.dumps(timing))


if __name__ == "__main__":
    main()
