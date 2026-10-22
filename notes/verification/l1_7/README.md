# L1.7 — địa chỉ kết quả và cách tái chạy

Người thực hiện: **Doan Van Tai** · **22/10/2026**.

- [Report](../../../results/lessons/l1_7/report.md), [results JSON](../../../results/lessons/l1_7/results.json), [config](../../../results/lessons/l1_7/config.json).
- [Log runner](../../../results/lessons/l1_7/run_output.txt), [97 test toàn repo](../../../results/lessons/l1_7/full_suite.txt), [JUnit](../../../results/lessons/l1_7/full_suite.xml).
- [CRN summary](../../../results/lessons/l1_7/crn_summary.csv), [4000 raw rows](../../../results/lessons/l1_7/crn_episodes.csv), [exact moments](../../../results/lessons/l1_7/exact_moments.csv).
- [Leak summary](../../../results/lessons/l1_7/leak_summary.csv), [2000 raw episodes](../../../results/lessons/l1_7/leak_episodes.csv), [sampler checks](../../../results/lessons/l1_7/sampler_checks.csv).
- [PNG](../../../results/lessons/l1_7/crn_and_leak.png), [manifest](../../../results/lessons/l1_7/artifact_manifest.json).
- [Audit đọc lại artifact trong process mới](../../../results/lessons/l1_7/independent_artifact_audit.json): replay **11332** rows bằng plant, đối chiếu52 file manifest ban đầu,15 source hashes và11 JUnit suites; **PASS**. Dùng chung plant nên không gọi đây là scientific independent review/V10.
- [Card trước chạy](../../lessons/L1.7_experiment_card.md), [stream/exposure spec và mock tham khảo](../../lessons/L1.7_stream_exposure_spec.md), [seed register](../../seed_registry.md), [exposure register](../../00_exposure_register.md).

```bash
.venv/bin/python -m experiments.lessons.run_l1_7
.venv/bin/python notes/verification/verify_l1_7_artifacts.py
# Lưu một lần chạy khác mà giữ nguyên artifact hiện tại:
.venv/bin/python -m experiments.lessons.run_l1_7 --output-dir /tmp/l1_7-rerun
.venv/bin/python notes/verification/verify_l1_7_artifacts.py --output-dir /tmp/l1_7-rerun
```

Cần cài project/dev dependencies theo pyproject.toml và pin NumPy bằng
`experiments/lessons/requirements-l1_7.txt`. Môi trường thực tế: Python3.14.5,
NumPy2.5.3,pytest9.1.1,PCG64. Root là demo được cung cấp,không sinh mới.

Kết quả cuối:13/13 L1.7,72/72 sáu lesson,4/4 bổ sung,97/97 toàn repo PASS.
Mutants R1–R6 bị5/4/2/1/5/2 collected cases bắt; R7 equivalent đối với action nên13/13 PASS.
Các FAIL của mutant là có chủ đích, không phải baseline failure.

Trước lần chạy đầy đủ: gọi preflight đầu chưa thực thi pytest vì thiếu thư mục output;
sau khi tạo thư mục,17/17 preflight PASS. Lần khởi tạo runner đầu có SyntaxError
(dấu nháy tại phần tạo report), đã sửa; chưa chạy experiment ở lần khởi tạo lỗi đó.
Lần chạy đầy đủ sau sửa và audit artifact đều PASS; không thay seed/N/threshold.
Lỗi khởi tạo chỉ có trong tool output phiên làm việc, không có file log riêng.

Đây là verification/demo của lesson, chưa là Phase4/E01,held-out hoặc network
validation. Hai trục stage×role chưa khóa contract-v1. L0.5,mock kín sách của tác giả,
Phụ lụcD,V3/V10/V11 còn mở; G1 và HOLD Phase4 giữ nguyên.
