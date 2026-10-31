# P4-A1 — kết quả thực thi ngày 31/10/2026

Người phụ trách: **Doan Van Tai**. Quyết định, dự đoán và phần triển khai do AI
soạn theo ủy quyền trực tiếp trong chat. Không ghi thành tác giả tự viết, tự dự
đoán độc lập hoặc human review.

## A. Đã triển khai

- Áp hai input người dùng lên `5043b4d`; giữ nguyên bản gốc trong `inputs/`.
  Patch thiếu newline cuối được chuẩn hóa trước `git apply`.
- Tạo gói `experiments/P4_A1/`, không sửa source/contract/card/CF frozen cũ.
- Sửa trước freeze: giữ NOT_READY khi export; kiểm S11; kiểm identity, K/ref,
  CF flag và receipt khi resume; dựng lại comparison từ rows; dừng bundle ngay
  sau BUG; giữ CPU đã đo khi lỗi; ghi provenance ủy quyền và SHA mọi input diagnosis.
- Diagnosis `1a8d83a`, choices/forecasts `195672a`, rồi ba prereg
  `d1c2879` / `7c7c956` / `bf767f2`, đều trước plant calls A1.
  Code A1 không đổi sau freeze đầu tiên.
- Mỗi run theo control → benchmark → budget commit → full → summarize nếu PASS.
  Ba nhánh độc lập chạy xen kẽ với số worker 2/2/1, budget CPU riêng.

## B. Đã kiểm chứng

| Kiểm tra | Kết quả thực tế |
|---|---:|
| Targeted tests của patch ban đầu | 72 PASS, 3,31 s |
| Targeted tests sau các sửa bổ sung | 80 PASS, 2,90 s |
| Full suite trước freeze | **842 PASS, 88,76 s** |
| Diagnosis trên calibration | 1.298 rows; same-route vi phạm 0/0, cross-route 236/279 |
| Controls chạy engine thật | **3/3 PASS**, exact zero action |
| Arithmetic, rescore ρ* và export từ saved outputs | **PASS** |
| Lock receipts và frozen source/history | **6/6 khớp SHA**, không mismatch |

Một lượt test fixture mới có 1 FAIL/79 PASS do NameError trong setup; đã sửa
trước freeze và giữ log lỗi. Lượt thử apply ban đầu không chạy được tests vì
patch thiếu newline cuối. Không đổi tolerance hoặc số liệu để vượt các kiểm này.

Lệnh chính đã chạy:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.P4_A1.diagnose
.venv/bin/python -m experiments.P4_A1.freeze --run RUN_ID
.venv/bin/python -m experiments.P4_A1.run control --run RUN_ID
.venv/bin/python -m experiments.P4_A1.run benchmark --run RUN_ID
.venv/bin/python -m experiments.P4_A1.run budget --run RUN_ID
# Commit budget trước full
.venv/bin/python -m experiments.P4_A1.run full --run RUN_ID
.venv/bin/python -m experiments.P4_A1.summarize --run RUN_ID
PYTHONPATH=src:. .venv/bin/python notes/verification/p4_a1/verify_outputs.py
```

`RUN_ID` lần lượt là `L44_A1`, `L43_A1_SV`, `SUB_PROBE`. Summarize của L44
trả exit 1 đúng dự kiến vì full HOLD; không chọn ρ hoặc xuất manifest cho run đó.
Rescore độc lập ở đây là đường tính khác trên artifact trong cùng phiên AI,
không phải người đọc độc lập.

## C. Kết quả đo được

| Run | Full stage / kế hoạch | PASS / NOT_READY / BUG | Đã quan sát kể cả benchmark | Evaluation CPU gồm control |
|---|---:|---:|---:|---:|
| L44_A1 — **HOLD** | 16/90 | 8 / 8 / 0 | 19 | 829,655796 s |
| L43_A1_SV — hoàn tất protocol | 497/497 | 496 / 1 / 0 | 497 | 5.821,730407 s |
| SUB_PROBE — hoàn tất protocol | 5/5 | 4 / 1 / 0 | 5 | 425,712089 s |

Tổng **1.566 lượt evaluate cấp level**, **7.077,098292 evaluation CPU-s** gồm
controls. Đây không phải tổng mọi chi phí import, compiler, launcher hoặc wall
clock. Không dùng RNG cho research runs; số liệu là deterministic discovery
re-evaluation trong plant đã khai.

### L44: vẫn HOLD vì baseline numerics

Full dừng khi **8/72 điểm SH NOT_READY > cap 10%**. Tính cả benchmark, đã quan
sát 19 tọa độ: 11 PASS, 8 NOT_READY; 71 NOT_RUN. MV có 2 PASS/16 NOT_RUN;
SH có 9 PASS/8 NOT_READY/55 NOT_RUN. Ledger giữ đủ 90 điểm kế hoạch.

Cả 19 tọa độ đều native-ready. Blockers mới thuộc baseline: 9 arithmetic events
và 12 R1 events; đây là số sự kiện, không phải số điểm. Không có ρ* và không
chấm median MV/SH trên toàn scope. Forecast NOT_READY≤3 điểm SH không đứng vì
đã quan sát 8; các forecast baseline toàn vùng chưa đánh giá được.

Kiểm same-route không phát hiện BUG trong phạm vi đã chạy. Điều này chưa loại
trừ mọi bug hoặc xác nhận root cause của OLD/CURRENT mismatch.

### SV: baseline không thu hẹp theo luật đã khóa

SV+ có **448/449 READY**; SV− có **48/48 READY**. `P43_0605` NOT_READY vì
baseline R1 ở ρ=5% cho L00 và GSθ, dù native-ready; export giữ nó là UNRESOLVED.

| Metric trên 448 điểm SV+ READY | Không margin | Margin được chọn |
|---|---:|---:|
| ρ* | 0 | **1%** |
| Median GS/Cref | **0,971841365%** | **1,021545257%** |
| Median ΔL00 | 0 | **+0,000505476 packet·s** |

Luật yêu cầu median GSθ/Cref<0,5% **và** median ΔL00<0 để narrow. Cả hai điều
kiện đều không đạt, nên **không narrow**. Không suy margin kém tại mọi regime:
argmin dùng mean normalized regret, còn luật đọc dùng median và raw ΔL00.
Selection áp dụng trên READY subset, không phải full-scope DL-104.

Map audit ghi 5 physical class flips, 19 điểm có full-class R6 UNRESOLVED,
0 điểm có pilot flags. Với riêng tiêu chí GS ở support đã khai: 1 NOT_READY +
8 near-boundary = 9/449 numerical UNRESOLVED; SV− là 0/48. Đây không phải
MEETS frequency/p-hat của hộp; chưa thử box nào. Forecast R6 10–30% không đứng
ở support này (~2% tổng uncertainty).

Kiểm thêm ΔL00 từ artifact chỉ fail đúng `P43_0605` đã NOT_READY; mọi điểm READY
được chọn đều đạt kiểm bổ sung. Đây là diagnostic sau run, không đổi criterion
A1 hoặc chọn lại ρ. Export 497 rows, hashes, identities, metric values và
refinement deltas khớp raw outputs.

### SUB: áp đúng luật probe, chưa xác nhận toàn vùng

Có **4/5 native-ready**, max bundle **164,404769 CPU-s≤600 s**. Theo luật đã
commit, đề xuất giữ κ≥1/20 để kiểm coverage L4.7 tiếp. Một điểm `P43_0595`
vẫn fail R1 K/dt và arithmetic width. Cref-dt của cả 5 điểm đạt chưa đủ thay
thế mọi kiểm R1.

Tại XM2X000, Cref-dt giảm từ **0,3105391881%** ở ref4 xuống **0,0779178392%**
ở ref8. Không suy bậc hội tụ hoặc global coverage từ một điểm. Probe không
kiểm hiệu ứng SUB; combined SUB và candidate readiness còn thiếu.

## D. File lưu kết quả

- Source và config: `experiments/P4_A1/`; choices/preregs trong ba thư mục `runs/`.
- Test/input/diagnosis logs: `results/lessons/p4_a1/preflight/`, `inputs/`, `diagnosis/`.
- Command/worker logs: `results/lessons/p4_a1/execution/` và `native/*/worker_*.log`.
- Raw, budget, full summaries: `results/lessons/l4_4/a1/`,
  `results/lessons/l4_3/a1_sv/`, `results/lessons/l4_3/a1_sub_probe/`.
- CSV/JSON tổng hợp: `measured_runs.csv`, `verification.json`, `final_integrity.json`.
- L44: `hold_case_ledger.csv`; SV: `summary/selected_baseline.csv`,
  `summary/native_manifest.json`, `runs/L43_A1_SV/rho_freeze.json`;
  SUB: `probe_metrics.csv`, `predeclared_decision.json`.
- Completion mới: `notes/phases/P4_A1_completion.json` và completion riêng từng run.
- Cache manifests có SHA/size; `native_cache/` giữ local ngoài Git, không xóa.

Không tạo biểu đồ, box-level p-hat hoặc CF outcomes mới.

## E. Kết luận

Implementation đã qua tests và chạy plant thật đúng scope đăng ký; dữ liệu và
phép tính/reporting đã được đối chiếu. Các kết quả vẫn là discovery trong mô
hình, chưa xác nhận hypothesis, novelty hoặc tần suất trong mạng thật. Refinement
differences không phải certified total error bounds; không có MC/CI mới.

**F1 baseline vẫn HOLD; L4.5 Part B chưa mở.** Cần numerical prereg/package mới
cho baseline nếu tiếp tục, cùng combined SUB/support receipts và coverage trước
candidate readiness. Không sửa A1 sau freeze để cứu HOLD. Card v2/F1/CF/contract,
G1, P0-V10, L8 và Understanding giữ trạng thái cũ. Không có CF/sealed outcomes,
box counts hoặc quyết định card/Gate 4 mới.
