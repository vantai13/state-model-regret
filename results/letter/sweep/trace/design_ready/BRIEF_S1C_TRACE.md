# Brief S1-C (Codex): hybrid so với luật tĩnh trên trace thật có burst mức giây (Claude, 21/11/2026)

Plan chung: `PLAN_SWEEP.md`. **Khám phá**, tác giả ủy quyền linh hoạt ("nếu GÉANT không tốt có thể thử cái khác").
Repo `/home/vantai/state-model-regret`, nhánh `letter`; `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`.

## Luật
- Không sửa file có sẵn. Chỉ tạo `experiments/letter/sweep_trace.py`, `tests/test_sweep_trace.py`, `experiments/letter/sweep_trace_gcp.sh`,
  file trong `results/letter/sweep/trace/`. Không commit, không ssh, không tải dữ liệu mới (chỉ dùng trace đã có trên máy; nếu thấy cần
  nguồn khác thì đề xuất trong báo cáo). Job S1-A chạy song song ở `sweep_ctmc*`; không đụng file của nó.
- Chỉ thiết kế, hiện thực, pilot và dự phóng; Claude chạy bản đầy đủ trên GCP.

## Bối cảnh
- Letter: fluid twin M0, hybrid = gap fluid + h·ŝ, luật tĩnh 1{ŝ<0}. Trên ma trận GÉANT 15 phút với điều biến tổng hợp bị chặn, đường mà luật tĩnh chọn
  gần như không nghẽn tức thời, nên hybrid gần như luôn trùng luật tĩnh (X5/X5c: `results/letter/x5_alarm/`, `results/letter/x5c_alarm/`).
- Nhánh external validity đã có simulator dùng trace thật (MAWI, DITL) với burst mức giây: `experiments/ext_validity/ev_d*.py`,
  `ev_d4b_*`, `ev_d4c_*`, báo cáo `results/ext_validity/WAVE*_REPORT.md`, `results/ext_validity/ev_d4b/REPORT_EV_D4B.md`, `ev_d4c/`.

## Làm gì
1. Đọc các file trên; tìm trace có sẵn trên máy (đường dẫn, độ dài, độ phân giải). Tóm tắt mô hình hai đường/hàng đợi và các twin của nhánh đó.
2. Thiết kế và hiện thực `sweep_trace.py` để so trên trace thật:
   - **Luật:** M0 (fluid, dùng trạng thái hiện tại), luật tĩnh (ŝ từ phần train của trace), hybrid (gap fluid + h·ŝ), oracle (replay trace thật
     cho C_ref), cùng một realization (common random numbers hoặc cùng đoạn trace).
   - **Điểm quyết định:** nhiều thời điểm dọc trace phần test (tách train/test theo thời gian, ŝ chỉ từ train); h/T_int ∈ {0,3; 0,5; 1; 2; 3; 5; 10};
     τ thực tế (như EV-D4b/c).
   - **Quét:** tải trung bình (hệ số scale trace), dung lượng hai đường, trace/ngày khác nhau; cả quyết định đều và quyết định khi có cảnh báo
     backlog trên đường luật tĩnh chọn.
   - **Metric:** regret theo cặp luật tĩnh − hybrid trên toàn bộ điểm quyết định theo h, khoảng tin cậy theo đoạn trace/ngày, share bất đồng,
     regret khi bất đồng, tie share của M0.
3. **Test:** tái lập một số liệu đã có của EV-D4b/c trên cùng cấu hình; tách train/test không rò rỉ.
4. **pilot:** một trace, ít điểm, đo CPU; dự phóng cho lưới quét. `sweep_trace_gcp.sh` chạy với `--workers 15`, không tự poweroff.

## Báo cáo cuối (tiếng Việt)
Trace có sẵn, mô hình đã dùng, thiết kế quét, kết quả pilot (kể cả share bất đồng sơ bộ nếu có), dự phóng CPU, test, đường dẫn, đề xuất nguồn trace khác nếu cần.
