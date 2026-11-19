# Quy ước triển khai V7-4 trước bước 0

Người phụ trách: **Doan Van Tai**. Code và kiểm tra do AI thực hiện theo brief;
không phải author-self hoặc human review. Không sửa thẻ `CARD_V7_4.md`.

- Tái sử dụng trực tiếp `v7_3_test.load_days/strata`, `v7_3_sim.warm_instances`,
  `forward_posterior`, `mean_rollout`, `variable`; `e4_geant.pick`,
  `hybrid_costs`, `costs_for_decisions`; seed, timer và I/O của V7-3.
  Không chép kernel, posterior, fluid hay luật chọn action.
- 87 record: DAY1–DAY3 × 29 ngày S lấy từ metadata input V7-3; kiểm lại strata
  bằng input local. Loại ngày 2005-06-27; không chạy O. Dùng đủ N32/K64.
- Giữ cây seed/nhãn V7-3: base → `V7-3-A2|DAYx` → `V7-3|date` → `warm`,
  `posterior-300.0`, `posterior-900.0`, `reference-decision`, `evaluation`.
  Base test 7412001, pilot 7472001; các horizon cùng warmup/posterior.
- Hybrid stable-only dùng tham số V7-3 đã có: DAY1 −320.6, DAY2 −314.0,
  DAY3 −0.4 Mbit. Không huấn luyện lại. Thêm Stationary_stable_only vào raw
  để comparison sensitivity có đủ hai luật (sign giống pooled ở cả ba DAY).
- Signal chính là DAY1/DAY2; gộp hai τ khi đọc tiêu chí fresh theo horizon.
  Mỗi fresh lặp theo τ như thẻ yêu cầu; lưu riêng bảng từng τ và DAY3.
  Chưa có C_ref nên không áp evaluable gate cho bước 0.
- Pilot đủ N32/K64/R_dec64/R_eval128 trên hai record S với **seed pilot**.
  Record 1 nặng nhất theo CPU đo ở decisions-only (hòa: regime/date giảm dần).
  Record 2 có work proxy input lớn nhất trong phần còn lại: số incidence khác 0
  + OD + link có thể active trong 1800 s, kể cả envelope warmup; hòa lấy
  regime/date tăng dần. Lưu selection trước rollout pilot. Đây không phải
  bằng chứng đã tìm đúng record truth nặng nhất.
- Dự phóng chính = overhead chuẩn bị bước 0 + 87 × max CPU của hai pilot đủ cỡ;
  báo thêm dự phóng từ mean. Nếu dự phóng chính >6 CPU-h: USE_GCP. Đây là
  dự phóng local, không phải cận trên hay phép đo GCP.
- Chỉ pilot mới có outcome trong lượt chuẩn bị này; không nhập vào H-P1.
  Truth lưu đủ 128 rollout cặp theo action, 64 rollout reference, decision/tie
  từng instance/pipeline/side/τ/h, C_ref, regret và cờ evaluable theo case.
  Chưa chấm H-P1; raw phải commit trước scoring.
- Case gate: mean_i(C_ref)/h ≥12.544525 Mbit, chung cho hai τ. Both-side regret
  của một pipeline là max giữa mean regret fresh và stale cùng case; dùng đúng
  tolerance tương đối 1e−9 của thẻ. Chênh chi phí instance dùng CRN và sd mẫu.
- Brief cấm commit; thẻ bước 0 yêu cầu code đã commit. Theo brief, code chỉ được
  hash trước bước 0 và ghi rõ chưa commit. Không nhận bước này là tuân thủ được
  điều kiện commit của thẻ. Claude cần duyệt và commit lock trước truth.
- Không commit/push/SSH, không sửa paper hoặc file V7-3. `truth` chỉ được cài;
  lock phải trùng byte với HEAD và mọi input/output chuẩn bị phải khớp SHA.
  Truth từ chối nếu thiếu signal hoặc có dấu đã chạy; không retry/resume.
