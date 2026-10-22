# B1 v1.1 — index kiểm chứng

Người tích hợp/chạy kiểm: **Doan Van Tai** · **23/10/2026**, Asia/Saigon.

Nguồn: bốn attachment người dùng cung cấp (review, hướng dẫn B1, draft ĐK1–ĐK8, patch). Patch tự ghi commit gốc `e1763b16bff6a4ecd56aa0534fca2592318e0e5c`; đã dùng `git apply --check` rồi `git apply`, không giả commit đó có trong lịch sử repo. Attribution/byline nguồn trong file được nhập giữ nguyên, không gán nguồn ấy thành bài tự làm của tác giả. SHA256 input gốc và source tích hợp ở [config](../../../results/lessons/l1_8_v1_1_b1/config.json). Bản làm việc patch chỉ chuẩn hóa CRLF→LF trước apply; hash input là byte gốc.

**Kết quả thực:** baseline146/146 PASS, dominance8/8 PASS, full154/154 PASS. Giữ9.216 ca gốc và thêm3.456 ca low-arrival/H1, tổng12.672 cases/116.352 cặp path. Coverage SD1=4.128, SD2=1.488, WD1=4.128, WD2=1.488;0 vi phạm path-wise/M0. Ba mutant3/3 KILLED. V1 có13SD-cell,2conservation-cell,13candidate; cả3calibration SD nên HOLD A01/A04 trên v1.

- [Báo cáo](../../../results/lessons/l1_8_v1_1_b1/report.md), [results JSON](../../../results/lessons/l1_8_v1_1_b1/results.json), [run log](../../../results/lessons/l1_8_v1_1_b1/run_output.txt).
- [Exhaustive counts](../../../results/lessons/l1_8_v1_1_b1/exhaustive_conditions.csv), [28 ô v1](../../../results/lessons/l1_8_v1_1_b1/v1_classification.csv), [old reserve chỉ tham số](../../../results/lessons/l1_8_v1_1_b1/v1_reserve_parameters.csv), [WD/tie](../../../results/lessons/l1_8_v1_1_b1/wd_tie_example.csv), [mutants](../../../results/lessons/l1_8_v1_1_b1/mutation_checks.csv).
- [Baseline log](../../../results/lessons/l1_8_v1_1_b1/baseline.txt), [full-suite log](../../../results/lessons/l1_8_v1_1_b1/full_suite.txt), [JUnit](../../../results/lessons/l1_8_v1_1_b1/full_suite.xml), [artifact checks](../../../results/lessons/l1_8_v1_1_b1/artifact_checks.json), [SHA256 manifest](../../../results/lessons/l1_8_v1_1_b1/artifact_manifest.json).
- [Lần đầu FAIL coverage](../../../results/lessons/l1_8_v1_1_b1/first_run/coverage_failure.json), [log gốc](../../../results/lessons/l1_8_v1_1_b1/first_run/run_output.txt). Tests đã PASS nhưng SD2/WD2 có0ca, nên runner từ chối kết luận bốn điều kiện được kiểm. Không xóa failure hoặc hạ tiêu chí.
- [Điều kiện DRAFT](../../design/design_conditions_v1_1.md), [status thiết kế](../../design/README.md), [dominance.py](../../../src/smr/dominance.py), [tests](../../../tests/test_dominance_v1_1.py), [runner](../../../experiments/lessons/run_v1_1_b1.py).

Đơn vị ví dụ WD là packet×teaching time unit, không phải measured physical delay. Không Monte Carlo/seed mới; không tạo biểu đồ. Không p_switch, grid/calibration/reserve hoặc tag v1.1. Bảy lựa chọn §11, Δt screen và cách kiểm dấu R2 còn cần chốt trước B3. V11/read-back/independent feedback chưa hoàn tất; full PHASE_1 chưa có để xác minh xung đột nguồn gate. Snapshot khoa học v1 và artifacts A/B/CDE giữ byte.

Chạy lại các test trên checkout đã áp patch: `.venv/bin/python -m pytest -q tests/test_dominance_v1_1.py` và `.venv/bin/python -m pytest -q`. Runner bảo vệ output cũ khỏi ghi đè; một output-dir mới cần bản baseline.json/.txt/.xml đã được lưu **trước patch**. Không chạy lại154test rồi gọi đó là baseline146test. Input attachment gốc cần có để runner đối chiếu SHA256; test khoa học không cần attachment này.
