# Phần A — kết quả thực chạy

Người phụ trách: **Doan Van Tai** ·23/10/2026.

**HOLD / NARROW REQUIRED.** Solver được gỡ nút thắt; B4 không đạt sau đúng một redesign. Không formal freeze/tagv1.1.

| Phép kiểm | Kết quả |
|---|---|
| Baseline → full suite |165 → **177/177 PASS**;12 tests mới|
| Stationary original / redesign |**20/20 +20/20 PASS** ởdt1/120 và1/240|
| Đối chiếu solver v1 |10/10 PASS; allowance array evaluation báo riêng|
| Max law error / posterior error |1.02853e-29 / 4e-16|
| Prior max wall / peak RSS |4.456s / 179.77MiB; cap1200s/4096MiB|
| Candidate/D/ĐK1 |28ô+6reserve mỗi thiết kế;272 queue-support artifacts audit; không Cartesian product|
| B3 |88 sign-only rows; unresolved mass0; reserve không screen|
| Max p_sw interval width |5.77094e-13|
| B4 acceptance |**8/22 →11/22**, yêu cầu**15/22**; không ô bị xóa|
| Screen total wall / max per row / peak RSS |91.725s / 22.227s / 98.43MiB|
| Sáu consistency checks |4PASS,1PARTIAL(full source),1FAIL(grid/calibration); numeric constraintsPASS|

Conditions: μ10packet/s; age1s; A backgroundλA±6, B2/14; κ.3/1/3; ηcore.5/spoke.9. Quantile coarse defines physical observation; finer prior recomputed at same observation, Hfine=2Hcoarse. No Monte Carlo/seed/CI lấy mẫu; đây là numeric bounds của law và p_sw.

Sparse longdouble trials được giữ, gồm law bound2.293e−10 vượt1e−10. Spectral approximation dùng interval balance, boundary, normalization, independent tail và Bellman return bound. Không gọi finite capped chain exact infinite law.

Native weighted-idle DP dùng integer lattice và zero-tail proof, không clip.6 tests mới kiểm native/Fraction, golden(+2,−1.5,+1.5,−3), hai Markov queues, sorted p_sw/brute force và syntheticH1000.6 tests stationary gồm closed-form/invalid coefficient/roundoff guard/large law. Native subtraction mutant lọt test dyadic đầu; đã giữ record và thêm keep.97 trong cùng conservation test: mutantFAIL đúng kỳ vọng, full177/177PASS sau bổ sung. Gamma mutantFAIL đúng kỳ vọng. Hai log subtraction mốc2 copy trongA3 là historical reference, không nhận là rerun native.

B4 dùng đúng một redesign đã commit trước outcome mới: λA7/7.2/8.1, center7.2.11ôin không đủ15; không chốt calibration dù có individual cells đạt. NegativeN01/N02 SD vàN03/N04 conservation: sáu contrast0 là kỳ vọng giải tích, chưa chạy contrast. Không được bỏout hay thử λ lần hai trong protocol này.

V1/V8/P0-V3/P0-V11 author-attested trực tiếp, không có artifact lưu; V9/P0-V10 chưa independently verified. Full PHASE_1/Final Review source chưa mở, chỉ có digest/reading note; không giả full SHA/quote hoặc gọi check4PASS. Heads-up chỉ là nháp repo, chưa gửi. G1 và MainRQ không đổi; failed screen convention không bác hypothesis.

## p_sw ởΔt/2 — đối chiếu đầy đủ

| Ô | Initial | Redesign | Nhãn cuối |
|---|---:|---:|---|
|M01|0.464365799–0.464365799|0.637720661–0.637720661|in|
|M02|0.057786434–0.057786434|0.227958518–0.227958518|in|
|M03|0.636062131–0.636062131|0.845552440–0.845552440|in|
|M04|0.000000000–0.000000000|0.169689190–0.169689190|in|
|M05|0.820954582–0.820954582|1.000000000–1.000000000|out|
|M06|0.000000000–0.000000000|0.128798010–0.128798010|in|
|M07|0.846505168–0.846505168|0.715245091–0.715245091|in|
|M08|0.562468330–0.562468330|0.339023342–0.339023342|in|
|M09|1.000000000–1.000000000|0.908711641–0.908711641|out|
|M10|0.623417979–0.623417979|0.292961222–0.292961222|in|
|M11|1.000000000–1.000000000|1.000000000–1.000000000|out|
|M12|0.704082905–0.704082905|0.229113183–0.229113183|in|
|M13|1.000000000–1.000000000|0.999105565–0.999105565|out|
|M14|1.000000000–1.000000000|0.971818100–0.971818100|out|
|M15|1.000000000–1.000000000|1.000000000–1.000000000|out|
|M16|1.000000000–1.000000000|1.000000000–1.000000000|out|
|M17|1.000000000–1.000000000|1.000000000–1.000000000|out|
|M18|1.000000000–1.000000000|1.000000000–1.000000000|out|
|M19|0.562226214–0.562226214|0.447816180–0.447816180|in|
|M20|1.000000000–1.000000000|0.946143377–0.946143377|out|
|M21|0.963075718–0.963075718|0.836694732–0.836694732|in|
|M22|1.000000000–1.000000000|1.000000000–1.000000000|out|

Intervals đầy đủ không làm tròn trongCSV;0/1 hiển thị9decimal không chứng nhận constant chính xác nếu interval vẫn chạm biên.

## Lệnh đã thực thi

```bash
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a1
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a2
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a4
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a1_redesign --output-dir /tmp/smr-a1-redesign-replay
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a2 --redesign
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a4 --redesign
PYTHONPATH=src:. .venv/bin/python -m experiments.lessons.run_v1_1_a5
.venv/bin/python -m pytest -q --junitxml=results/lessons/v1_1_a6/full_suite.xml
.venv/bin/python notes/verification/verify_v1_1_part_a.py
PYTHONPATH=src:. .venv/bin/python notes/verification/verify_v1_1_factorized_law.py
```

A1/A2 runners giữ output và từ chối ghi đè; A4 có resume và kiểm candidate/source hashes cho lần redesign. Tái lập trong clone/worktree sạch hoặc chọn output mới khi CLI hỗ trợ. Baseline165 là record mốc2, không giả rerun hiện tại vẫn165test.

## Artifacts

- config.json/results.json/readiness.json: cấu hình, metric và trạng thái từng check.
- full_suite.txt/xml, native_subtraction_mutant*.txt/xml, mutation_development_note.md: baseline thật và mutant trước/sau.
- screen_comparison.csv + part_A_diagnostics.png: p_sw hai thiết kế và plot standalone.
- dominance_mass.csv/factorized_law_audit.json: masses ĐK1 và136 legacyB comparisons (maxTV≈1.32e−14).
- ../v1_1_a1*/certificates.csv +certificate JSON:20+20 priors; ../v1_1_a2*/supports.json,NPZ,labels.csv,budget.csv: D/ĐK1/budget.
- ../v1_1_a4*/screen.csv/run_output.txt:88rows vàlog; ../v1_1_a5/selection.json: quyết định rejected vàcalibration rỗng.
- notes/design/grid_v1_1*.json/md: full decision/candidate manifests; definitions/boundary/brief v1.1 vẫn draft vì B4fail.
- source src/smr/stationary_spectral.py,stationary_v2.py,gap_screen.py,native/idle_backward.cpp; tests/test_stationary_spectral.py,test_gap_screen.py.
- Không cómargin/Lstar/contrast/network experiment hoặc tagv1.1 mới. Bước tiếp theo là protocol NARROW/REFORMULATE mới, chưa chọn tham số outcome-driven tiếp.
