"""Doan Van Tai — independent post-hoc audit/report, no engine or truth calls.

This intentionally does not import r2_o1_check or either numerical evaluator.
The budget stop remains effective. This script exclusively creates new files.
"""
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path
import time


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n"
    with (OUT/path).open("x") as f:
        f.write(value)


def main():
    start = time.process_time()
    pred = json.loads((OUT/"predictions_before.json").read_text())
    plan = json.loads((OUT/"pilot.json").read_text())
    assert plan["decision"] == "STOP_BUDGET" and plan["selected_grid"] == []
    paths = sorted((OUT/"raw").glob("*.json"))
    assert len(paths) == 1, "No main truth permitted after budget stop"
    raw = json.loads(paths[0].read_text())
    assert raw["regime"] == pred["pilot"]
    assert raw["prediction_sha256"] == digest(OUT/"predictions_before.json")
    for path, sha in pred["sources"].items():
        assert digest(path) == sha, path
    for reg in pred["regimes"]:
        assert digest(ROOT/reg["saved_source"]) == reg["saved_sha256"]
    reg = next(r for r in pred["regimes"] if r["regime"] == raw["regime"])
    checks = []

    def check(name, ok):
        checks.append(dict(name=name, passed=bool(ok)))

    original_rows = raw["rows"]
    rows = []
    for source in original_rows:
        row = dict(source)
        row["grid_kind"] = "W1B_REPLAY" if source["grid_kind"] == "W1B_REPLAY" else "PILOT_ONLY"
        if row["twin"] == "T4":
            slopes = sum(reg["T4"]["slope_by_modes"], [])
            row["s_hat_min"] = min(slopes)
            row["s_hat_max"] = max(slopes)
            row["s_hat_description"] = "state-dependent, four mode values in predictions_before.json"
        rows.append(row)
    requested = [r for r in rows if r["grid_kind"] == "PILOT_ONLY"]
    replay_rows = [r for r in rows if r["grid_kind"] == "W1B_REPLAY"]
    check("36 pilot twin-h cells", len(requested) == 36)
    check("7 W1b replay rows", len(replay_rows) == 7)
    check("pilot all six requested h levels", sorted(set(round(r["h_T_int"], 10) for r in requested)) == pred["proposed_grid"])
    for row in rows:
        prefix = f"{row['twin']} h={row['h']:.12g} {row['grid_kind']}"
        check(prefix+" percent normalization", math.isclose(row["G_S_pct_C_ref"], 100*row["G_S_abs"]/row["C_ref"], rel_tol=1e-14, abs_tol=1e-20))
        check(prefix+" positive C_ref", row["C_ref"]>0)
        if row["grid_kind"] == "W1B_REPLAY":
            continue
        lo, hi = row["P_dis_lower"], row["P_dis_upper"]
        check(prefix+" P_dis enclosure", 0 <= lo <= row["P_dis"] <= hi <= 1)
        frechet_lo = abs(row["F_old"]-row["F_new"])
        frechet_hi = min(1., row["F_old"]+row["F_new"], 2-row["F_old"]-row["F_new"])
        check(prefix+" Frechet compatibility", hi+1e-12 >= frechet_lo and lo-1e-12 <= frechet_hi)
        if row.get("threshold") is not None:
            check(prefix+" threshold formula", math.isclose(row["threshold"], row["M_hat"]/abs(row["s_hat"]), rel_tol=1e-14))
            check(prefix+" threshold eligibility", row["above_threshold"] == (row["h"]>row["threshold"]))
        if row["slope_predicted"] is not None:
            check(prefix+" measured slope", math.isclose(row["slope_measured"], row["G_S_abs"]/row["h"], rel_tol=1e-14))
    saved = json.loads((ROOT/reg["saved_source"]).read_text())
    original = next(e for e in saved["evaluations"] if e["age_label"] == "Tint_1")
    expected_h = {Fraction(r["h"]):r for r in original["h"]}
    replay = []
    for actual in raw["replay"]:
        expected = expected_h[Fraction(actual["h"])]["G_S"]
        relative = abs(actual["observed"]-expected)/max(abs(expected), 1e-300)
        check("W1b replay "+actual["h"], relative <= 1e-9)
        replay.append(dict(h=actual["h"], observed=actual["observed"], expected=expected, relative_error=relative))
    check("T0 slope before truth", math.isclose(reg["T0"]["slope_predicted"], reg["s"]*(reg["T0"]["F_old_inf"]-reg["T0"]["F_new_inf"]), rel_tol=1e-14))
    # The mode invariant law is uniform and independent across the two sources.
    four = sum(reg["T4"]["slope_by_modes"], [])
    f_new_nc = sum(v<0 for v in four)/4
    f_old_nc = sum(v<0 for v in sum(reg["T4"]["stale_rate_by_modes"], []))/4
    check("T4 pretruth slope independent reconstruction", reg["T4"]["slope_predicted"] == reg["s"]*(f_old_nc-f_new_nc))
    d2 = []
    for row in requested:
        if row["twin"] not in ("T1", "T2"):
            continue
        lhs = abs(row["G_S_abs"])
        lower_rhs = row["P_dis_lower"]*row["max_abs_true_gap"]
        upper_rhs = row["P_dis_upper"]*row["max_abs_true_gap"]
        tolerance = 1e-9*row["C_ref"]
        d2.append(dict(twin=row["twin"], h_T_int=row["h_T_int"], lhs=lhs,
                       lower_rhs=lower_rhs, upper_rhs=upper_rhs, tolerance=tolerance,
                       strict_lower_bound_holds=lhs <= lower_rhs,
                       arithmetic_lower_bound_holds=lhs <= lower_rhs+tolerance))
    d1_eligible = [r for r in requested if r["twin"] in ("T1", "T2") and r["above_threshold"]]
    d3_eligible = [r for r in requested if r["twin"].startswith("T3") and r["above_threshold"]]
    negative_forecasts = [r["regime"] for r in pred["regimes"] if r["T4"].get("slope_predicted", 0)<0]
    trends = []
    for twin in ("T0", "T4"):
        rs = sorted([r for r in requested if r["twin"]==twin], key=lambda r:r["h"])
        slope = rs[-1]["slope_predicted"]
        for i, row in enumerate(rs):
            trends.append(dict(twin=twin, h_T_int=row["h_T_int"], G_S_abs=row["G_S_abs"],
                G_S_pct_C_ref=row["G_S_pct_C_ref"], slope_predicted=slope, slope_measured=row["G_S_abs"]/row["h"],
                slope_relative_error=abs(row["G_S_abs"]/row["h"]-slope)/abs(slope),
                secant=None if i==0 else (row["G_S_abs"]-rs[i-1]["G_S_abs"])/(row["h"]-rs[i-1]["h"]),
                P_dis=row["P_dis"], P_dis_inf=reg["T4"]["P_dis_inf"] if twin=="T4" else None))
    check("no new arithmetic flags", not any(r["flags"] for r in requested))
    check("all D2 arithmetic checks pass in pilot", all(r["arithmetic_lower_bound_holds"] for r in d2))
    audit = dict(scope="INDEPENDENT_SAVED_DATA_RESCORE_NO_NEW_TRUTH", checks=checks,
        passed=sum(c["passed"] for c in checks), total=len(checks), all_passed=all(c["passed"] for c in checks),
        D1_eligible=len(d1_eligible), D3_eligible=len(d3_eligible), D2=d2,
        replay=replay, trends=trends, raw_sha256={p.name:digest(p) for p in paths},
        prediction_sha256=digest(OUT/"predictions_before.json"), sources_unchanged=True,
        limitations="Checks re-score algebra and saved outputs; they do not independently rerun V or reconstruct the real-regime joint P_dis. Synthetic 4D enumeration is tested separately.")
    assert audit["all_passed"], [c for c in checks if not c["passed"]]
    write("audit.json", audit)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    buf = io.StringIO(); wr = csv.DictWriter(buf, fieldnames=cols); wr.writeheader(); wr.writerows(rows)
    write("rows.csv", buf.getvalue())
    write("reproduction.json", replay)
    verd = dict(
        D1=dict(verdict="NOT_EVALUABLE", reason="0 h above threshold, even original 300*T_int grid", eligible=0),
        D2=dict(verdict="PASS_PILOT_ONLY", passed=sum(r["arithmetic_lower_bound_holds"] for r in d2), total=len(d2),
                strict_passed=sum(r["strict_lower_bound_holds"] for r in d2), panel_status="11 regimes NOT_RUN"),
        D3=dict(verdict="NOT_EVALUABLE", eligible=0),
        D4=dict(verdict="CONSISTENT_FINITE_PILOT", regime_count=1, limit_proved_by_numerics=False),
        D5=dict(verdict="CONSISTENT_FINITE_PILOT", observed_mixed_sign=1, planned_eligible=4, planned_mixed_sign=2,
                planned_constant_sign=2, skipped=8, limit_proved_by_numerics=False),
        D6=dict(verdict="PARTIAL_PILOT", negative_forecasts=negative_forecasts, observed_growing_harm=[reg["regime"]],
                not_run_negative_forecast=[name for name in negative_forecasts if name!=reg["regime"]]))
    scientific_cpu = pred["prepare_cpu_seconds"]+raw["cpu_seconds"]
    command_times = {}
    for name in ("tests_pre", "prepare", "pilot"):
        command_times[name] = json.loads((OUT/(name+".time.json")).read_text())
    summary = dict(status="STOP_BUDGET_AFTER_ONE_PILOT_NOT_FULL_PANEL", owner="Doan Van Tai", verdicts=verd,
        completed_regimes=1, planned_regimes=12, pilot_regime=reg["regime"], scientific_rows=36, replay_rows=7,
        actual_scientific_cpu_seconds=scientific_cpu, command_times=command_times,
        estimated_full_cpu_hours=plan["projections"][0]["projected_total_cpu_seconds"]/3600,
        estimated_min_grid_cpu_hours=plan["projections"][-1]["projected_total_cpu_seconds"]/3600,
        estimates_are_guarantees=False, numerical_flags=[], audit_passed=audit["passed"], audit_total=audit["total"],
        T0_reproduction_passed=len(replay), T0_max_relative_error=max(r["relative_error"] for r in replay),
        original_grid=pred["proposed_grid"], final_main_grid=[], seed=None,
        prediction_sha256=digest(OUT/"predictions_before.json"), raw_sha256=audit["raw_sha256"],
        posthoc_analysis_cpu_seconds=time.process_time()-start)
    write("summary.json", summary)
    final = {r["twin"]:r for r in requested if math.isclose(r["h_T_int"], 300)}
    lines = ["# R2-O1 — kiểm phạm vi mệnh đề (P)", "",
      "Người phụ trách: **Doan Van Tai**. Exploration kiểm mệnh đề; không phải kết quả paper, không đổi verdict đã khóa.", "",
      "**STOP_BUDGET sau 1 pilot; không hoàn tất panel 12 regime.** Dừng theo đúng brief: sau khi giảm lưới h đến `{1}`, dự phóng vẫn vượt 2 CPU-h. Không chạy thêm truth, không tự bỏ P_dis hoặc lấy subset để nhận full PASS.", "",
      f"Đã chọn đủ 12 regime theo thứ tự id và rounded linspace, 6 s<0 từ 42 và 6 s>0 từ 51. Predictions/threshold/w*/slope của cả 12 đã lưu trước truth. Pilot `{reg['regime']}`: `(lamA,lamB,u,kappa,alpha)=(7,6,1,1/20,3)`, c=0, mu=10, tau=T_int={reg['T_int']:.12g} s; N_A={reg['N_A']}, N_B={reg['N_B']}. Lưới pilot `h/T_int={1,3,10,30,100,300}`: 36 twin-h cells, 7 T0 replay rows. Không seed: deterministic finite CTMC.", "",
      "## D1–D6: đúng/sai và phạm vi thực sự đã kiểm", "",
      "| Dự đoán | Trạng thái | Bằng chứng/giới hạn |", "|---|---|---|",
      "| D1 | CHƯA ĐÁNH GIÁ ĐƯỢC | 0 ô đủ h>M_hat/abs(s_hat); không nhận PASS rỗng. Ngưỡng của cả 12 regime đều ngoài lưới gốc. |",
      f"| D2 | ĐÚNG TRÊN PILOT: {sum(r['arithmetic_lower_bound_holds'] for r in d2)}/{len(d2)} | T1/T2, 6 h; dùng P_dis lower bound và tolerance arithmetic 1e−9 C_ref. Có {sum(r['strict_lower_bound_holds'] for r in d2)}/{len(d2)} thỏa ngay không tolerance; không khẳng định toàn panel. |",
      "| D3 | CHƯA ĐÁNH GIÁ ĐƯỢC | 0 ô trên ngưỡng cho cả plug-in và 3tau; T3 vẫn được chạy đủ 6 mức h của pilot. |",
      f"| D4 | PHÙ HỢP HỮU HẠN TRÊN 1 PILOT | T0 slope dự đoán {reg['T0']['slope_predicted']:.12g}; G_S/h ở 300 T_int = {final['T0']['slope_measured']:.12g} packet. Chưa chứng minh giới hạn bằng chạy hữu hạn. |",
      f"| D5 | PHÙ HỢP HỮU HẠN TRÊN 1 PILOT | T4 w*=.25: P_dis={final['T4']['P_dis']:.12g}, dự đoán .25. Slope dự đoán {reg['T4']['slope_predicted']:.12g}; đo {final['T4']['slope_measured']:.12g}. 3 regime T4 hợp lệ khác chưa chạy, gồm 2 constant-sign. |",
      "| D6 | MỘT PHẦN | Dự đoán trước truth 2 regime slope âm; quan sát harm tăng ở 1 pilot, regime còn lại NOT_RUN. Không ghi 2/2 PASS. |", "",
      "D4/D5 dùng chữ ‘phù hợp hữu hạn’: brief không cho tolerance hội tụ hoặc tốc độ ‘gần tuyến tính’. Không tự đặt ngưỡng chấm sau khi thấy dữ liệu.", "",
      "## Kết quả đo trực tiếp", "",
      "| Twin ở h/T_int=300 | G_S (packet·s) | 100 G_S/C_ref (%) | P_dis |",
      "|---|---:|---:|---:|"]
    for twin in ("T0", "T1", "T2", "T3_plugin", "T3_3tau", "T4"):
        row = final[twin]
        lines.append(f"| {twin} | {row['G_S_abs']:.12g} | {row['G_S_pct_C_ref']:.12g} | {row['P_dis']:.12g} |")
    lines += ["", f"C_ref ở mức cuối = {final['T0']['C_ref']:.12g} packet·s. T0 baseline và T4 đều có harm (G_S<0); T1/T2/T3 chỉ gần 0 theo số học, không khẳng định tất cả state đã coincidence dưới ngưỡng bảo đảm.", "",
      "| Twin | h/T_int | G_S packet·s | G_S %C_ref | slope dự đoán | G_S/h đo | sai số slope tương đối | secant từ mức trước | P_dis |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in trends:
        secant = "n/a" if row["secant"] is None else f"{row['secant']:.12g}"
        lines.append(f"| {row['twin']} | {row['h_T_int']:.9g} | {row['G_S_abs']:.12g} | {row['G_S_pct_C_ref']:.12g} | {row['slope_predicted']:.12g} | {row['slope_measured']:.12g} | {100*row['slope_relative_error']:.9g}% | {secant} | {row['P_dis']:.12g} |")
    lines += ["", "T0 |G_S| tăng từ 0.105119892 lên 307.068749 packet·s; T4 từ 0.139054814 lên 295.169551 packet·s. Slope là G_S/h (packet), không phải %C_ref/h. Chuẩn hóa bởi C_ref tăng theo h có thể cho %C_ref hội tụ trong khi harm tuyệt đối tăng tuyến tính.", "",
      "## CPU, pilot và lý do dừng", "",
      f"Prediction preparation {pred['prepare_cpu_seconds']:.9f} CPU-s; pilot {raw['cpu_seconds']:.9f} CPU-s: truth {raw['truth_cpu_seconds']:.9f}, posterior {raw['posterior_cpu_seconds']:.9f}, joint {raw['joint_cpu_seconds']:.9f}. Tổng scientific đo được {scientific_cpu:.9f} CPU-s ({scientific_cpu/3600:.9f} CPU-h). Đây là thời gian thực đo, khác các dự phóng dưới đây.", "",
      "| Lưới dự phóng | CPU-s | CPU-h |", "|---|---:|---:|"]
    for projection in plan["projections"]:
        cost = projection["projected_total_cpu_seconds"]
        lines.append(f"| {projection['grid']} | {cost:.9f} | {cost/3600:.9f} |")
    lines += ["", "Dự phóng dùng saved prepare timings của từng regime cho V và work proxy (n_A²+n_B²)tau cho joint semigroups, calibration từ 1 pilot nhẹ, cộng 25% reserve và 180 CPU-s. Chi phí joint không mất đi khi chỉ giảm số h; kernel được tái dùng cho các twin/h trong mỗi regime. Joint term còn lại dự phóng 46960.870912 CPU-s. Đây là ước lượng phụ thuộc implementation/proxy, không lower bound về độ khó, không time guarantee và không bằng chứng không thể giải bằng thuật toán rẻ hơn. Một pilot nhẹ có hạn chế; chưa đo case nặng vì luật dừng đã áp dụng.", "",
      "## Danh sách trước truth và coverage", "",
      "| Regime | s thật | w* T4 | slope T4 dự đoán | threshold T1/T_int | threshold T2/T_int | h_bar/T_int | status |",
      "|---|---:|---:|---:|---:|---:|---:|---|"]
    for rr in pred["regimes"]:
        nc = rr["T4"]
        w = "SKIP" if not nc["eligible"] else str(nc["w_star"])
        slope = "n/a" if not nc["eligible"] else f"{nc['slope_predicted']:.12g}"
        status = "PILOT_COMPLETE" if rr["regime"]==reg["regime"] else "NOT_RUN_BUDGET"
        lines.append(f"| {rr['regime']} | {rr['s']:.12g} | {w} | {slope} | {rr['threshold_T1']/rr['T_int']:.9g} | {rr['threshold_T2']/rr['T_int']:.9g} | {rr['h_bar']/rr['T_int']:.9g} | {status} |")
    lines += ["", "T4: 4 regime hợp lệ, 8 SKIP vì không có w trong tập quy định cho max load < 0.95 mu. Trong 4 regime có 2 mixed-sign và 2 constant-sign strict; không có mode slope bằng 0. Hai slope âm được dự báo trước là -0.605765230574 và -0.213020924373 packet; chỉ slope sau đã có finite-h truth mới. s_hat của T4 là hàm state: CSV ghi min/max, bốn giá trị và posterior ở predictions; không gán scalar threshold M_hat/abs(s_hat) cho T4 mixed-sign.", "",
      "## Kiểm tra, ngoại lệ và flag", "",
      f"- T0 tái lập G_S tại đủ 7 h đã lưu của pilot: 7/7 PASS, max relative error {max(r['relative_error'] for r in replay):.12g} ≤1e−9. 11 regime khác chưa tái lập.",
      f"- Independent saved-data audit: {audit['passed']}/{audit['total']} PASS; không import scorer/engine, không gọi lại V. Kiểm normalization, ngưỡng, slope, Frechet bounds, replay và D2. Không nhận đây là một engine độc lập hay độc lập tính lại real-regime P_dis.",
      "- 8 tests mới PASS: 2D-CDF so với enumerate 4D nhỏ, actual P_dis khác |DeltaF|, wrong-kernel cost semantics, strict cutoff/tie, inequality, nowcast selection, full semigroup marginals, selection 12 regime. Các tests không chứng minh đầy đủ mọi implementation lỗi đều bị loại.",
      f"- 0 flag arithmetic mới trên 36 cells. Max stationary residual {raw['chain_residual_max']:.12g}. P_dis joint marginal errors và omission ở pilot.log; không suppress negative G_S vì đó là harm được định nghĩa.",
      "- P_dis là số đo deterministic kèm [lower,upper]: bỏ terminal stationary mass ≤1e−10 mỗi path, giữ full Q và mọi old-state row, không renormalize. Khoảng chỉ bao omission, không phải interval-arithmetic certificate cho scipy. Khi marginal bounds đủ hẹp (width≤1e−9), dùng enclosure trực tiếp; không nhận P_dis chính xác bằng 0 khi chỉ nhỏ hơn độ phân giải.",
      "- Chi phí T3 luôn dùng posterior thật exp(Q0*tau); plugin/3tau chỉ đổi kernel chọn action. Tie dùng strict <0 → Stay; không epsilon.",
      "- Rows replay không thuộc lưới h yêu cầu chỉ ghi T0 G_S; P_dis để trống, flag REPLAY_ONLY_NO_PDIS. Không giả 0. Tất cả 36 cells đúng lưới của pilot có P_dis và enclosure.",
      "- Không CI population: đây là finite deterministic CTMC; các h/twin trong cùng regime phụ thuộc nhau. Không suy thực tế/infinite-buffer từ một pilot cắt cụt.", "",
      "## Phạm vi mệnh đề (P) — không gọi là định lý", "",
      "1. **Lập luận đủ của (P) đúng cho probability kernel**: nếu |b|≤M thì |E_K b|≤M; h|s_hat|>M ép D_tilde và mọi posterior average cùng dấu. Khi đó hai action trùng nhau ở mọi state, G_S=0. K phải normalized, nonnegative; ‘mọi kernel’ không bao arbitrary linear/signed operator. Bất đẳng thức |G_S|≤P_dis max|V1−V0+c| xuất phát trực tiếp từ cost difference theo disagreement.",
      "2. **Có stationary term không tự đủ cho O(1)**. T4 pilot có term h*s_nc(x), bounded fluid remainder, mixed-sign state slopes và posterior slope negative ở mọi old mode. Pretruth F_new_inf=.75, F_old_inf=1 nên hệ số s*.25 khác 0. P_dis tiến gần .25 và G_S/h tiến gần -0.213020924373 trên lưới thực chạy: counterexample hữu hạn có cơ chế tiệm cận được chỉ rõ cho cách nói quá rộng ‘twin có stationary cost thì O(1)’. Không nhận phép chạy hữu hạn tự nó chứng minh giới hạn. Regime dự báo còn lại chưa có truth.",
      "3. **s_hat=0 không bảo đảm O(1)**: T0 là bounded fluid twin nhưng pretruth s*DeltaF_inf=-0.222286063158 và harm tuyệt đối tăng rõ. Đây là đối chứng bỏ stationary term. Tuy nhiên s_hat khác 0 không phải điều kiện cần cho mọi twin có G_S=O(1): một twin luôn chọn cùng action đã có G_S=0.",
      "4. **Hằng số độc lập state chỉ là điều kiện đủ mạnh**. Nếu s_hat(x) cùng dấu và inf_x|s_hat(x)|=eta>0 thì cutoff h>M/eta cũng cho coincidence. Trên finite support, strict common sign cho eta>0. Sign đổi tự nó cũng chưa bảo đảm slope harm khác 0: còn cần DeltaF_inf khác 0 và s khác 0. Hai constant-sign T4 cases chưa chạy nên không ghi numeric PASS cho nhánh này.",
      "5. **Uniform boundedness b không cần thiết để O(1)**. Trên finite support, b(h,x)=sqrt(h)u(x) là unbounded nhưng o(h), nên common nonzero slope vẫn thắng cuối cùng. Ngược lại, cho phép b=O(h) tùy state có thể tạo mixed-sign effective slope như T4; không thể bỏ toàn bộ kiểm soát relative growth của remainder. Đây là phân tích đại số phạm vi, không một experiment phụ hay giả định mới của letter.",
      "6. **Correct stationary-rate sign không cần cho G_S=0**: hai pipeline có thể cùng chọn action sai và có regret O(h). Nó cần khi yêu cầu long-run action đúng, không cần cho coincidence. Ở 12 regime đã chọn s_MM1 cùng dấu s; panel này không phải phép kiểm wrong-sign rate.",
      "7. **Uniform cutoff và G_S=O(1) khác nhau**: disagreement không cần triệt tiêu để expected G_S bounded. Plug-in stale có cùng switch share với fresh dưới stationary X,Y nên DeltaF=0; finite-state gain–bias cho phần còn lại O(1). Hoặc P_dis=O(1/h) cũng là điều kiện đủ khi max true gap=O(h). Vì vậy một giả định thất bại không đồng nghĩa O(1) thất bại.",
      "8. **M_hat phải thực sự bound remainder**. Prop.2 của letter dùng h>max(h_bar,M_hat/abs(s_hat)), D1 của brief chỉ ghi threshold sau. Ở 12 case này h_bar≈16.8–18.04 T_int thấp hơn mọi threshold, nên không đổi eligibility. Với fluid model cụ thể, từng path gap có dấu cố định và bounded bởi saturated path gap; empty low-mode cho gap 0, nên max network gap saturation bound mọi h. Không suy saturation M_hat là sup cho một twin tổng quát khác.",
      "9. **Giới hạn môi trường**: finite irreducible CTMC/bounded f cho bounded bias và exponentially decaying remainder; đây là lý do true gap có hệ số stationary độc lập initial state. Không suy cùng kết luận cho infinite support hoặc real traces. Phần đại số cutoff của (P) chỉ cần bounded remainder và probability kernel, không cần CTMC.", "",
      "## Kết luận và phần chưa xác nhận", "",
      "Đã có kiểm tra hữu hạn rõ về failure mode của state-dependent rate: trên 1 pilot, T4 không loại harm tăng theo horizon, còn T1/T2/T3 gần 0. D2 đúng với tolerance arithmetic trên 12 ô của pilot; T0 tái lập 7/7. D1/D3 chưa có ô trên cutoff và toàn bộ panel chưa chạy. Không đưa dữ liệu này vào paper, không gọi là định lý, không đổi verdict cũ. Không tự chạy thêm theo thẻ hiện tại sau budget stop. Muốn đủ 12 regime cần một lựa chọn kỹ thuật/ngân sách riêng cho joint P_dis; đây chỉ là hướng tiếp theo, chưa triển khai.", "",
      "## File, commands và provenance", "",
      "Nguồn mới: `experiments/letter/r2_o1_check.py`; tests mới: `tests/test_r2_o1_check.py`. Không sửa source đã có, không commit/SSH, không sửa state-model-regret-papers/, không ghi vào job p2_tier2.", "",
      "Commands đã chạy, sau khi source `.venv/bin/activate` và `experiments/explore_ctmc/env.sh`, đặt `PYTHONDONTWRITEBYTECODE=1`:", "",
      "```text",
      "python3 -m pytest -q -p no:cacheprovider --basetemp results/letter/r2_o1/pytest_tmp tests/test_r2_o1_check.py",
      "python3 -m experiments.letter.r2_o1_check prepare",
      "python3 -m experiments.letter.r2_o1_check pilot",
      "python3 results/letter/r2_o1/analyze_saved.py",
      "```", "",
      "Không chạy `run` sau STOP_BUDGET. Logs: `tests_pre.log`, `prepare.log`, `pilot.log`, `analysis.log`; command CPU/wall ở `*.time.json`. Raw duy nhất ở `raw/Za3_u1_lA7_x-1_k1-20.json`; số liệu ở `rows.csv`, `summary.json`, `audit.json`, `reproduction.json`; design/predictions ở `predictions_before.json`, resource decision ở `pilot.json`. Không tạo biểu đồ, PDF hay paper artifact.", "",
      f"Brief SHA256 `{pred['sources'][str(Path('/home/vantai/state-model-regret-papers/letter_smr/briefs/R2_O1_CHECK_BRIEF.md'))]}`; predictions SHA256 `{digest(OUT/'predictions_before.json')}`; raw SHA256 `{digest(paths[0])}`. Source/input hashes khớp audit. Predictions trước finite-h truth, không sửa sau pilot; phạm vi diễn giải/independent audit là post-hoc, không blind forecast mới.", "",
      "AI (Codex) triển khai, chạy, audit theo brief của Claude và ủy quyền tác giả; không human independent review, không author-self proof. Không literature lookup mới. research-workflow yêu cầu PRINCIPLES.md nhưng file không có trong skill root đã chỉ định; không tạo thay và không dùng để chặn scope được user ủy quyền. Bộ nhớ letter-current-state không có trong local memory roots/tools hiện có; brief và source local được dùng làm context, không tự sửa paper."]
    write("SUMMARY.md", "\n".join(lines)+"\n")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("raw_sha256", "prediction_sha256")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
