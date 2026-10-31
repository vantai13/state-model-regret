# A3/B1 — sensitivity check cuối của baseline, 31/10/2026

Người phụ trách: **Doan Van Tai**. Thiết kế nguồn do AI (Claude) cung cấp;
AI triển khai và soạn forecast theo ủy quyền tiếp diễn, không tác giả tự viết.

**MV và SH đều STABLE theo B1. Nhánh numerical kết thúc tại A3; không A4.**

## A. Thực hiện

Dùng nguyên runner A1, 90 keys (18 MV/72 SH), rho grid và helpers DL104.
Phần mới chỉ là summarizer nhỏ `experiments/P4_A3/b1_summary.py` và 9 tests.
Giữ mọi NOT_READY; riêng từng support, cùng rho* và cùng narrow/not-narrow tại
640/4, 320/4, 640/2 thì STABLE, khác thì UNRESOLVED. Không thêm diagnostic phụ,
optional claim-readiness gate, replay toàn 57, lesson hoặc lock framework mới.

Protocol ở `experiments/P4_A1/runs/L44_A3/amendment.md`; choices/design cùng thư mục.
Code/protocol commit d444bc8, prereg 06aa5dc trước mọi A3 evaluation. Prereg SHA:
`98808fdeec81ec18dd793ee1514b88be9064858d2127f4828e61e624d98bc6c9`.
Forms/prereg/budget commit được giữ để dùng nguyên runner hiện có. Source A1/A2,
engine, metric, threshold và card v2 không đổi.

## B. Lệnh và kiểm chứng

```bash
.venv/bin/python -m pytest -q tests/test_p4_a3.py
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.P4_A1.freeze --run L44_A3
.venv/bin/python -m experiments.P4_A1.run control --run L44_A3
.venv/bin/python -m experiments.P4_A1.run benchmark --run L44_A3
.venv/bin/python -m experiments.P4_A3.b1_summary replay
.venv/bin/python -m experiments.P4_A1.run budget --run L44_A3
.venv/bin/python -m experiments.P4_A1.run full --run L44_A3
.venv/bin/python -m experiments.P4_A3.b1_summary summarize
```

9 targeted tests PASS (0,30 s); 879 full tests PASS (87,33 s). Control PASS;
benchmark 4/4 hoàn tất (3 PASS/1 NOT_READY), reference replay 12/12 khớp saved
numerical fields và significant bits parse lại. Environment khớp A1 cả 6 trường.
Budget theo luật cũ 2,683995 CPU giờ, cap 8 giờ; 2 workers, một BLAS thread/worker.

Full 90/90 hoàn tất, 54 PASS/36 NOT_READY, không stop reasons. Có đúng 270 case
levels và 1 control: **271 evaluations**; các benchmark rows được reuse khi full.
0 BUG/execution failure. Arithmetic Fraction độc lập tái tính mọi argmin và median
trên đủ 90 keys tại 3 mức, khớp 6/6 readings và verdict; không gọi thêm engine.
Raw arithmetic/validity flags vẫn giữ ở 131/271 rows, không đổi chúng thành BUG
hoặc xóa khỏi output. Native row readiness 90/90, baseline NOT_READY 36/72 SH;
MV 18/18 ready. Đây counts trên inventory discovery, không ước tần suất population.

`git diff --check` ban đầu báo whitespace cuối dòng trong worker log; đã giữ
nguyên raw logs và dùng cùng whitespace rule như A1. Không có experiment lỗi
bị ghi thành PASS, không đổi scientific source sau freeze.

## C. Số đo

| Support | K_ref | rho* | Median tại rho* | Narrow? |
|---|---|---|---|---|
| MV+A | 640_4 | 1/20 | R_M=0.862967 | Có |
| MV+A | 320_4 | 1/20 | R_M=0.867986 | Có |
| MV+A | 640_2 | 1/20 | R_M=0.867061 | Có |
| SH+A | 640_4 | 0 | abs(GSθ)/Cref=4.685250%; ΔL10=0 packet·s | Không |
| SH+A | 320_4 | 0 | abs(GSθ)/Cref=4.679597%; ΔL10=0 packet·s | Không |
| SH+A | 640_2 | 0 | abs(GSθ)/Cref=4.701969%; ΔL10=0 packet·s | Không |

Cả 3 mức cùng MV rho=1/20 (5%), narrow=True; SH rho=0, narrow=False.
R_M không có đơn vị, là phần model gain được margin lấy lại, không phải phần
chi phí tuyệt đối giảm đi. Tất cả 18 mẫu số MV được certified ở cả 3 mức,
0 undefined. SH dùng median abs(GSθ)/Cref<0,5% và median ΔL10<0 packet·s;
ρ=0 cho ΔL10=0 nên không đạt điều kiện cải thiện nghiêm ngặt.

CPU evaluation gồm control **1934.611542 s =
0.537392095 CPU giờ**; full-stage wall 896.600378 s
(không gồm benchmark/control). Không MC/seed RNG hoặc statistical CI.
Forecast AI dự đoán 12 NOT_READY, thực tế 36 (sai); dự đoán cả 2 rho/reading stable,
SH median>=0,5%, MV R_M>=1/2 và replay 12/12 khớp với kết quả.

## D. Files

- Source: `experiments/P4_A3/b1_summary.py`; tests `tests/test_p4_a3.py`.
- Config/protocol: `experiments/P4_A1/runs/L44_A3/`; rho policy: `rho_freeze.json`.
- JSON kết quả: `results/lessons/l4_4/a3/summary/b1_summary.json`.
- CSV 6 dòng: `results/lessons/l4_4/a3/summary/level_summary.csv`.
- Raw rows/comparisons/worker logs: `results/lessons/l4_4/a3/native/`;
  control/budget/full summary cùng output root. Cache giữ local, Git-ignored.
- Command/test logs, environment và `verification.json`: `results/lessons/p4_a3/`.
  Không tạo figure hoặc completion/manifest framework riêng.

## E. Kết luận và dừng

**MV: thu hẹp câu claim về lợi ích so với mean-field không margin**, vì margin
đơn giản lấy lại khoảng 86,30–86,80% model gain ở median trên 18 keys đã kiểm.
**SH: không thu hẹp theo baseline đã thử**; lựa chọn tối ưu là không margin.
Đây discovery reading, không CF verdict hoặc novelty/human-Understanding proof.

STABLE chỉ xác nhận cùng kết luận trong 3 resolutions đã kiểm. Ba mức có thể cùng
bias; 36 điểm SH vẫn NOT_READY. Không gọi numerics/convergence từng point đã
solved, không chạy A4 hoặc thêm mức để làm đẹp kết quả.

Chuyển tiếp **L4.5 Part B** với rho policy đã chốt. A3 không tự cấp native/baseline
readiness cho candidate SV/SUB hoặc tạo box counts; dùng evidence candidate đã có
và phạm vi riêng khi sàng. SV/SUB giữ nguyên, G1, không CF/sealed outcomes mới.
