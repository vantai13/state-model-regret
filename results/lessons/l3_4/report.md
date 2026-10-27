# L3.4 / A01 — báo cáo thực chạy

Người phụ trách: **Doan Van Tai** · 27/10/2026.

**Kết quả A01: PASS; ref chung = 2; dt cuối = 1/240 s.**

A01 kiểm implementation và độ ổn định trên ba ô calibration; không chấm prediction card hoặc xác nhận Main RQ.

## Thực hiện và baseline lý thuyết

Đã khóa prereg/receipt, triển khai selector, Part0→A→B và sửa biểu diễn GS_M1 bằng hai direct cuts.
Run01 dừng tại N01; giữ toàn bộ dữ liệu/lỗi. Certificate always-empty sửa predicted tie sai −1.35525e−20;
không đổi plant, control, threshold, card, mức dt hoặc budget. Xem DL-050/051.
Run02 PASS controls, tạm dừng tại M01/ref8 để sửa O(n²) conversions trong D22; giữ đủ partial outputs.
Run03 chạy mới Part0/A và đủ15 mức PartB bằng6 processes, không dùng lại controls/code cũ (DL-052).

- Full suite sau sửa: **336 PASS**, mutant **11/11 KILLED**; targeted23 PASS.
- Part0: **9/9** khoảng p_sw khớp bit-for-bit public baseline.
- C1/C2/C3: **18/18** cell-control-level identities PASS; C2prime6 quan sát, không là yêu cầu zero.
- C4: independent rational min-cost enumeration + strict-tie action PASS; không là physical-kernel proof độc lập.
- C5: **10/10** cell-level, **60/60** contrast entries bằng0 chính xác; C6 **6/6** GS_M1 bằng0 chính xác.
- PartB: **15/15** cell-level; numeric precision PASS **15/15**.
- max e_num/Cref_lower = 2.51157748e-05 (cap .0025); max unresolved mass = 1.71586249e-05 (cap .01).

- Optimization replay: 3/3 M01 calibration JSON ref1/2/4 và4/4 control artifacts trùng từng byte với run02 tuần tự; không đọc cache làm kết quả mới.

## Làm mịn — đủ mọi cặp, không chọn kết quả thuận lợi

| Cell | Cặp ref | max change / min Cref (%) | Cận trên gồm e_num (%) | PASS |
|---|---|---:|---:|---|
| M01 | 1→2 | 0.02442132 | 0.02442132 | True |
| M01 | 2→4 | 0.01190075 | 0.01190076 | True |
| M01 | 4→8 | 0.005690339 | 0.00569034 | True |
| M01 | 8→16 | 0.002895683 | 0.002895686 | True |
| M09 | 1→2 | 0.00891751 | 0.00891751 | True |
| M09 | 2→4 | 0.004429181 | 0.004429181 | True |
| M09 | 4→8 | 0.0007229278 | 0.0007229285 | True |
| M09 | 8→16 | 0.001272186 | 0.001272188 | True |
| M22 | 1→2 | 0.0004369689 | 0.000436969 | True |
| M22 | 2→4 | 0.0002204698 | 0.0002204699 | True |
| M22 | 4→8 | 8.633299e-05 | 8.633317e-05 | True |
| M22 | 8→16 | 5.497778e-05 | 5.497849e-05 | True |

Picks từng ô: `{'M01': 2, 'M09': 2, 'M22': 2}`; cutoff mỗi cặp **0.25%**. Rho/Richardson chỉ diagnostics.

## Toàn bộ contrast đo được (packet·s)

| Cell | m | Cref | GS | GM | GSM | Gamma | GS_M1 | GM_S1 | a00 | status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| M01 | 1 | 34.4747183 | 1.13825004 | 0.67117974 | 1.60405126 | -0.205378518 | 0.93287152 | 0.465801221 | 1 | BOUNDED |
| M01 | 2 | 34.4442342 | 1.13867216 | 0.679591477 | 1.60625445 | -0.212009188 | 0.926662974 | 0.467582288 | 1 | BOUNDED |
| M01 | 4 | 34.4309559 | 1.13816953 | 0.68368902 | 1.60733712 | -0.214521429 | 0.923648099 | 0.469167591 | 1 | BOUNDED |
| M01 | 8 | 34.424988 | 1.13822954 | 0.685647919 | 1.60784066 | -0.216036801 | 0.922192744 | 0.469611117 | 1 | BOUNDED |
| M01 | 16 | 34.4220542 | 1.13809968 | 0.686644672 | 1.6081027 | -0.216641657 | 0.921458027 | 0.470003016 | 1 | BOUNDED |
| M09 | 1 | 74.4966595 | 0.625638307 | 0 | 1.08674857 | 0.46111026 | 1.08674857 | 0.46111026 | 0 | BOUNDED |
| M09 | 2 | 74.4444018 | 0.61899972 | 0 | 1.08125441 | 0.462254687 | 1.08125441 | 0.462254687 | 0 | BOUNDED |
| M09 | 4 | 74.4172419 | 0.615703646 | 0 | 1.07843263 | 0.46272898 | 1.07843263 | 0.46272898 | 0 | BOUNDED |
| M09 | 8 | 74.4337837 | 0.616241629 | 0 | 1.07890662 | 0.462664991 | 1.07890662 | 0.462664991 | 0 | BOUNDED |
| M09 | 16 | 74.4272339 | 0.615294776 | 0 | 1.07821359 | 0.462918818 | 1.07821359 | 0.462918818 | 0 | BOUNDED |
| M22 | 1 | 738.476604 | 0 | 0.182964858 | 1.21505289 | 1.03208803 | 1.03208803 | 1.21505289 | 0 | BOUNDED |
| M22 | 2 | 738.621932 | 0 | 0.185035356 | 1.21389648 | 1.02886112 | 1.02886112 | 1.21389648 | 0 | BOUNDED |
| M22 | 4 | 738.695848 | 0 | 0.186100156 | 1.21333284 | 1.02723268 | 1.02723268 | 1.21333284 | 0 | BOUNDED |
| M22 | 8 | 738.686563 | 0 | 0.18562943 | 1.21269511 | 1.02706568 | 1.02706568 | 1.21269511 | 0 | BOUNDED |
| M22 | 16 | 738.704998 | 0 | 0.185894616 | 1.21255418 | 1.02665956 | 1.02665956 | 1.21255418 | 0 | BOUNDED |

## Ô WD — chỉ GS_M1 là zero bắt buộc

| Cell | ref | GS_M1 | GM | GS | p_sw |
|---|---:|---:|---:|---:|---:|
| W01 | 1 | -0.0 | 0 | -0.000255765268 | 0.770056902 |
| W01 | 2 | -0.0 | 0 | -0.000251613558 | 0.777113831 |
| S01 | 1 | -0.0 | 0 | -0.203092276 | 1 |
| S01 | 2 | -0.0 | 0 | -0.202932207 | 1 |
| P02 | 1 | -0.0 | 0.128215019 | 0 | 0.524489708 |
| P02 | 2 | -0.0 | 0.127683215 | 0 | 0.527283157 |

## Lệnh đã thực thi

```bash
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_4/preflight/full_suite_final.xml
.venv/bin/python -u -m experiments.A00_engine.run_mutants --out results/lessons/l3_4/preflight/mutants_final
.venv/bin/python -u -m experiments.A01_null_refinement.run --run-id 20261027_01 --allow-grid
.venv/bin/python -u -m experiments.A01_null_refinement.run --run-id 20261027_02 --allow-grid
.venv/bin/python -u -m experiments.A01_null_refinement.run --run-id 20261027_03 --allow-grid --workers 6
.venv/bin/python -m experiments.A01_null_refinement.selection results/A01/20261027_03/refinement.csv
.venv/bin/python -m experiments.lessons.report_l3_4 20261027_03
```

## Provenance và output

- Prereg commit `81233ef9478e88f03b548c6bef21b9fa98b51a25` / SHA `9b8dc2f358792f4ac1e7df146ca8dc334599773f7de60378999a86efe5debe0f`.
- Run code/receipt `60a1032e30c6d37a0dc4c69ab70ca272f17e5070`; card SHA `14021a83c6d45a3fbeba6b7cbe27e9c8c0e572734557af1598cf79b819f34639`.
- Config: `experiments/A01_null_refinement/config.json`, bản copy/config hash trong run manifest.
- Run data/log: `results/A01/20261027_03/` và `results/A01/20261027_03.console.log`.
- CSV: psw_check, nulls, negative_cells, refinement, refinement_pairs, refinement_diagnostics.
- JSON: manifest/config/controls_status/selection/run_status, mỗi calibration cell-level và negative cell-level.
- Report/metric/plot: thư mục này: `report.md`, `verification.json`, `jump_diagnostics.json`, `refinement.png`.
- Source: A01 runner/selector/controls/psw/provenance; sửa A00 factorial_core/physical/precision.

## Giới hạn và gate

Exact expectation trên finite slot law, deterministic, không Monte Carlo nên không sampling CI/seed.
Cận số conditional trên input/kernel bounds; không phải formal proof toàn bộ physical enclosures.
Không chứng minh continuum limit, 35main còn lại ổn định hoặc plant giống mạng thật.
M01/M09/M22 mọi mức đã exposed, chỉ còn đánh giá theo card đã khóa; ngoài card là discovery.
A04 **chưa chạy, V9 chưa gửi nên chờ**; nếu chạy phải kiểm cặp 2dt_final/dt_final từng ô.
Không D/outcomes held-out mới. H1/null/A05-F chưa khóa; L8/P0-V10/T05 author-writing vẫn mở.
