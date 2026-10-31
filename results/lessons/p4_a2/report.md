# P4-A2 — Kết quả probe baseline L4.4, 31/10/2026

Người phụ trách: **Doan Van Tai**. Thiết kế nguồn do AI (Claude) cung cấp; triển khai, lựa chọn và forecast do AI soạn theo ủy quyền tiếp diễn. Không phải tác giả tự viết hoặc human review.

**A2 hoàn tất kỹ thuật; F1 baseline vẫn HOLD.** Đã chạy đủ 8 điểm × 7 levels và một control, tổng 57 evaluation calls, không BUG/mismatch. Chỉ 2/8 điểm từng READY và 0/8 READY ở bậc cuối. Theo luật khóa trước run, nhánh là **B1_CLAIM_LEVEL_ROBUSTNESS**; chưa chạy A3, chọn ρ* hoặc đọc baseline toàn vùng.

## A. Đã thực hiện

- Đọc toàn bộ hướng dẫn; giữ nguyên raw input tại `inputs/instructions_original.txt` (SHA trong `intake.json`). Tái lập diagnosis 19 điểm/95 cặp: 8 fail tại 8 điểm, mỗi điểm một ρ, W3/K6/D3; chỉ L00/GS_theta refinement vượt tolerance.
- Tạo `experiments/P4_A2/diagnose_l44.py`, `guards.py`, `probe.py`, `__init__.py`, `README.md`, thiết kế/choices/amendment/prereg và `tests/test_p4_a2.py`. Sửa guard/replay/resume/decision trước freeze; không sửa A1 hoặc engine. Diagnostic median được sửa upper-middle thành median chuẩn, không sửa readiness hoặc metric nghiên cứu.
- Chuỗi commit trước engine: 15fd087 input/diagnosis source → 885401d diagnosis → e4e989c hardened code/tests → a6f69ca choices/forecast/B1/DL112 → b5ae553 prereg. Prereg SHA256 `b98ef52c245e0556eb845475f3868d7f44d507f1ced5ce7d4c3fa5f86d7d73a1`; full commit `b5ae5539d29af556db679ff64afb29dad7451ce3`.
- Probe đủ 8 failures, giữ mọi ρ và đủ 7 unique levels: 640/4, 320/4, 640/2, 1280/4, 1280/2, 1280/8, 640/8. Các main theo thứ tự 640/4 → 1280/4 → 1280/8, mỗi main kiểm 2 coarse axes. Một worker, BLAS một thread; mỗi process tối đa 3.600 CPU-s/4.800 wall-s/3 GiB; cap toàn probe 3 CPU giờ.

## B. Lệnh thực tế và kiểm chứng

```bash
.venv/bin/python -m experiments.P4_A2.diagnose_l44
.venv/bin/python -m pytest -q tests/test_p4_a2.py
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.P4_A2.probe freeze
.venv/bin/python -m experiments.P4_A2.probe control
.venv/bin/python -m experiments.P4_A2.probe run
.venv/bin/python -m experiments.P4_A2.probe decide
.venv/bin/python notes/verification/p4_a2/verify_results.py
```

28 targeted tests PASS (1,48 s); 870 full tests PASS (86,83 s), trước freeze. Diagnosis chạy lại im lặng và khớp. Plumbing fake-evaluator trong tmp kiểm 57 calls và resume không gọi thêm; đây không phải numerical evidence.

Control thực tại 1280/8 PASS, six contrasts đúng 0. Run thực có 8/8 điểm exit 0, đủ 56 discovery levels. Replay 24/24 saved numerical/error/baseline fields và significant bits được parse lại khớp A1; không claim toàn JSON/timing/ABI bytes trùng. Có 0 BUG, 0 reproduction mismatch, 0 execution failure.

Audit riêng không import/gọi engine: công thức Fraction độc lập tái lập 19/19 trạng thái A1, sau đó khớp mọi step/ρ của A2, SHA/receipt/CPU/nhánh. Có 14 source locks và 80 history locks PASS; ba preregs A1/SV/SUB vẫn verify. Environment khớp cả 6 trường Python/platform/NumPy/SciPy/mpmath/long-double: Python 3.14.5, NumPy 2.5.3, SciPy 1.18.1, mpmath 1.3.0; long-double có 63 mantissa bits.

Bước compile đầu của script audit bổ sung phát hiện thiếu dấu ngoặc; đã sửa và compile PASS trước khi chạy audit. Source experiment đã freeze không đổi. Không có test/experiment FAIL bị ghi thành PASS.

## C. Số đo thực tế

| Đại lượng |640/4|1280/4|1280/8|
|---|---:|---:|---:|
| Native row readiness |8/8|8/8|8/8|
| Baseline toàn bộρ cùng READY |0/8|2/8|0/8|
| Số cặp failW |3|3|3|
| Số cặp failK |6|3|6|
| Số cặp failD |3|1|4|

Một cặp có thể đồng thời thuộc W/K/D. W là width >1/4000 Cref (=0,025% Cref), K/D là chênh refinement >1/400 Cref (=0,25% Cref); không đổi ngưỡng. Mọi lỗi refinement vẫn chỉ ở L00/GS_theta. Không xuất hiện failing ρ mới ở điểm nào.

Bảng dưới dùng **max** của hai trục K/dt cho L00 tại ρ đã fail ở A1; đơn vị **%Cref**, không phải thay đổi chi phí tuyệt đối. `READY` trong cột flags chỉ áp cho ρ mục tiêu; trong dữ liệu này không có ρ fail khác. Step được đánh số 0, 1, 2.

| Điểm |ρ mục tiêu|ΔL00 refinement step0|step1|step2|Flags step0→1→2|Bậc READY đầu|
|---|---|---:|---:|---:|---|---|
| P44_000 | 1/100 | 0.174304 | 0.173854 | 0.082506 | W → W → W | Không |
| P44_002 | 1/200 | 0.185091 | 0.184727 | 0.090474 | W → W → W | Không |
| P44_006 | 1/50 | 0.366384 | 0.078906 | 0.269075 | K → READY → K | 1 (1280,4) |
| P44_007 | 1/50 | 0.321465 | 0.091059 | 0.264282 | K → READY → K | 1 (1280,4) |
| P44_008 | 1/100 | 0.408744 | 0.080883 | 0.300999 | WK → W → WKD | Không |
| P44_009 | 1/20 | 0.816096 | 0.461628 | 0.634977 | KD → K → KD | Không |
| P44_010 | 1/50 | 1.040641 | 0.567240 | 1.134585 | KD → K → KD | Không |
| P44_011 | 1/50 | 0.881471 | 0.593924 | 0.836799 | KD → KD → KD | Không |

P44_006/P44_007 đạt READY ở 1280/4 nhưng lại fail K tại 1280/8 (0,269075%/0,264282% Cref, xem JSON/CSV cho precision đầy đủ). Quy tắc first-READY đã khóa vẫn đếm 2 điểm; báo cả kết quả bậc cuối 0 READY để không che non-monotonicity.

CPU evaluation tổng **1.280,950894 s = 0,355819693 CPU giờ**, gồm control 16,556818 s; discovery 1.264,394076 s, dưới cap 10.800 s. Đây CPU đo trong evaluation, không phải toàn bộ wall/import/launcher cost. Native quadrature deterministic, không MC/seed RNG và không statistical CI; refinement là diagnostic, không phải error certificate của true estimand.

Raw flags giữ nguyên: 20/57 rows có arithmetic_pass=True, 37 False; 37 rows có validity_errors gồm negative_nonnegative_contrast:G_SM và G_S_M1. Đây là raw reports về các contrast so giữa hai quadratures theo A1, không cùng nghĩa BUG hoặc native lean readiness. Không xóa flags hoặc coi chúng là cùng-route invariant failure.

So với forecast AI đã commit: dự đoán 4 READY, thực tế 2 (không khớp); K giảm 6→3 ở bậc giữa nhưng trở lại 6 ở bậc cuối, W giữ 3; dự đoán có ρ fail mới không khớp (thực tế 0). Dự đoán 0 BUG và 24/24 replay khớp. Ít điểm được ladder sửa phù hợp với hướng nghiêng H_cliff trong phạm vi probe, **không chứng minh cơ chế vật lý/atom hoặc phủ định mọi refinement sâu hơn**.

## D. Artifacts

- Code/config: `experiments/P4_A2/`; prereg `experiments/P4_A2/runs/L44_PROBE/prereg.json`; choices/amendment cùng thư mục. Source A1 và các preregs cũ không đổi.
- Raw outputs/receipts/replay/worker logs: `results/lessons/l4_4/a2_probe/`; quyết định `decision.json`, CPU `run_summary.json`, control `control_summary.json`.
- Log commands: `results/lessons/p4_a2/execution/` gồm `control.log`, `run.log`, `decide.log`, `independent_verification.log`, `frozen_integrity.log`. Tests/environment/precheck ở `preflight/`; `diagnosis.log` và `diagnosis_repeat.log` ở thư mục report.
- Audit/source: `notes/verification/p4_a2/verify_results.py`; `verification.json` chứa SHA các57rows, summary/decision. CSV `point_summary.csv` có8rows; `rho_step_diagnostics.csv` có120rows (8×3×5). `forecast_check.json` ghi đối chiếu forecast.
- Completion: `notes/phases/P4_A2_completion.json`; quyết định DL113, exposure và forking#26 trong các ledger. Báo cáo này `results/lessons/p4_a2/report.md`.
- Cache198files/207052416bytes giữ local ở `results/lessons/l4_4/a2_probe/native_cache/`, Git-ignored; SHA manifest `native_cache_manifest.json`. Không tạo biểu đồ hoặc statistical CI.

## E. Kết luận và bước kế

Áp đúng nhánh **B1** đã khóa vì 2≤4. Thang R3 hữu hạn không giải quyết đủ baseline failures ở góc λA=7/λB=6; đây là kết quả về numerical readiness, không phải MainRQ falsification hoặc physical discovery.

Theo hướng dẫn, A3 cần package/prereg riêng và full 90 keys, giữ mọi điểm; áp argmin/luật đọc DL104 riêng trên 640/4, 320/4, 640/2, chỉ gọi aggregate reading stable khi cả 3 cùng ρ* và cùng quyết định. Stable trên 3 levels không bảo đảm không cùng bias hoặc thay thế certificate/R1 per-point. A2 chỉ trả nhánh/decision; hướng dẫn ghi sẽ cung cấp code A3 sau kết quả này. Không rerun A1 hoặc tính ρ/median trên 19 điểm đã thấy.

F1 baseline **HOLD chờ A3 validity**. SV/SUB nguyên trạng; L4.5 Part B/combined SUB/readiness/Gate 4/P0-V10/L8/Understanding còn mở, G1 giữ nguyên. Có 0 CF/sealed outcomes/new coordinates/box counts; không đổi card v2/contract/ngưỡng hoặc ghi AI-work thành author ownership.
