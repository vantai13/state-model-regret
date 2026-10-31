# L4.5 Part B — SV đã sàng, SUB tạm dừng theo yêu cầu

Người phụ trách: **Doan Van Tai**. Code/chi tiết/forecast do AI soạn theo ủy quyền;
tác giả chọn rõ “Chạy một hộp SUB (khuyến nghị)”, sau đó yêu cầu tạm dừng job dài
và push phần đã xong. Ghi nhận pause UTC: 2026-10-31T08:30:58.016908+00:00.

**Trạng thái hiện tại: SV FAIL_SCREEN; SUB PAUSED_PARTIAL; số card chưa quyết định.**
Không gọi Part B hoàn tất và không tự suy “0 card” từ việc tạm dừng.

## A. Đã hoàn thành các phần ngắn

- Sửa preflight theo candidate: SV có thể READY khi SUB chưa có receipt. Các
  hàm label/count/power và rules v1 giữ nguyên byte; không đổi thresholds.
- Commit cả hai hộp một lần trước counts, chỉ một hộp mỗi candidate. SV dùng
  đúng 449/48 frozen A1 keys; plus envelope có 7 key discovery khác ngoài support,
  không giả đã native-audit toàn envelope. SUB gồm 76 keys chọn bằng tọa độ,
  không lọc pilot class hoặc outcome;0CF/sealed collision.
- Không viết freezer/runner mới: dùng explicit-case loader của A1 (kindL44 là
  tên adapter), main 640/8 và neighbors 320/8,640/4, target00/readingMV+A.
- Bổ sung DL114 chốt A3, DL115 khóa scope/luật trước counts; cập nhật baseline
  vào claim_boundary_v1_4_draft. Không sửa contract/cardv2 hoặc mở A4.
- Sửa diễn giải nguồn: recovery không đơn điệu theo rho; rho 5% đã là witness
  đủ để narrow MV. Score drift tối đa MV .03352%Cref, không phải <=.02% như
  ước lượng nguồn; gap runner-up vẫn >=.94165%. A3 không có reason tại rho*.

## B. Đã chạy và kiểm

```bash
.venv/bin/python -m pytest -q tests/test_p4_05_candidates.py
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.P4_A1.freeze --run SUB_BOX
.venv/bin/python -m experiments.P4_05_candidates.screen preflight --candidate SV
.venv/bin/python -m experiments.P4_05_candidates.screen screen --candidate SV --box experiments/P4_05_candidates/boxes/SV_01_full_support.json --native-manifest results/lessons/l4_3/a1_sv/summary/native_manifest.json
.venv/bin/python -m experiments.P4_A1.run control --run SUB_BOX
.venv/bin/python -m experiments.P4_A1.run benchmark --run SUB_BOX
.venv/bin/python -m experiments.P4_A1.run budget --run SUB_BOX
.venv/bin/python -m experiments.P4_A1.run full --run SUB_BOX
```

17 targeted tests PASS 0.61 s; **880 full tests PASS 86.80 s**. Sau SV screen, chạy lại
17 tests PASS 0.66 s. Independent native-label counts và exact power từ saved rows
khớp; frozen A1/SV/SUB sources verify PASS. Không gọi thêm engine khi audit.

SUB control PASS (17.081308 CPU-s), benchmark 2/2 PASS; fixed-reference replay 3/3
saved numerical fields/reparsed bits khớp SUB_PROBE. Budget authorized 1.953305
CPUh, cap 8 CPUh,2 workers/BLAS1thread. Full run đã bắt đầu rồi được **SIGSTOP**
theo yêu cầu; không có full_summary PASS/HOLD vì job chưa kết thúc.
Raw input có whitespace cuối dòng; giữ nguyên bytes bằng .gitattributes.
Không có test/experiment lỗi bị ghi thành PASS.

## C. Số đo thật

| SV support | N | MEETS | FAILS | UNRESOLVED | p_cond | r_hat |
|---|---:|---:|---:|---:|---:|---:|
| plus |449|216|224|9|49.090909%|2.004454%|
| minus|48|0|48|0|0%|0%|

SV p_plan = p_cond−.10 = **39.090909%**. Planning power =
**2.56551360569e-05**, thấp hơn .5; decision **FAIL_SCREEN**, trial 1.
Không thêm hộp SV sau kết quả. Đây feasibility trên support discovery đã đăng
ký, không population frequency hoặc confirmation evidence.

| SUB tại thời điểm pause | Số lượng/trạng thái |
|---|---|
| Keys đã hoàn tất đủ 3 levels | 10/76, tất cả PASS |
| Keys đang tính dở, chưa có savedlevel | 2: SUB_0009/SUB_0010 |
| Keys chưa bắt đầu | 64 |
| Completed native level rows đã lưu | 30 |
| Control level đã lưu |1|
| CPU của completed calls đã lưu, gồm control | 1004.273106 s |
| Full / baseline summary / rho* / SUB screen | Chưa có |
| Số card cuối | Chưa quyết định (null) |

CPU trên là **lower bound**: không gồm CPU đã dùng trong hai calls bị dừng khi
chưa ghi row, không phải total job CPU.10 keys gồm 2 benchmark keys, không cộng
benchmark lần hai. Forecast SUB chưa được chấm vì run chưa đủ; SV forecastFAIL
khớp. Không tạo p-hat/power SUB từ tập partial.

## D. Lưu ở đâu

- Source sửa: `experiments/P4_05_candidates/screen.py`,
  `tests/test_p4_05_candidates.py`; numeric rules JSON không đổi.
- Config/prereg/cases/protocol: `experiments/P4_A1/runs/SUB_BOX/`.
- Hai hộp: `experiments/P4_05_candidates/boxes/`; scope author/delegation ở
  `notes/phases/L4_5_part_b_scope.json`.
- SV actual result: `results/lessons/l4_5/box_trials/SV/trial_01.result.json`.
- SUB raw rows/worker logs/control/benchmark/budget: `results/lessons/l4_5/sub_native/`.
- Test/command logs: `results/lessons/l4_5/part_b/` (các file*.log).
- Pause/checkpoint: `pause.json`, `SUB_checkpoint.json` cùng thư mục report.
- Audit số liệu: `verification.json`; CSV ngắn `measured_status.csv`.
- Không tạo SUB rho_freeze, SUB manifest, SUB trial, final0/1/2card hoặc biểu đồ.
  Native cache giữ local và Git-ignored.

## E. Tạm dừng và tiếp tục sau

Job dài đang dừng bằng SIGSTOP, giữ RAM/state local, không chạy CPU hoặc schedule
khóa mới. Process group hiện tại **257934**; chi tiếtPID trong pause.json.
**Chỉ resume khi tác giả yêu cầu tiếp.** Trước SIGCONT phải kiểm processgroup vẫn
là đúng SUB_BOX job; không chạy instance thứ hai song song. Nếu processgroup
không còn, dùng lại cùng frozen full command và các rows đã lưu để resume.

Sau khi đủ 76 keys mới summarize baseline, đăng ký receipt SUB, sàng đúng hộp
đã khai và áp DL sốcard. Không mở thêm hộp/mức để cứu kết quả; không CF hoặc
Phase5 outcomes trong phiên này. G1 và các failure lịch sử giữ nguyên.
