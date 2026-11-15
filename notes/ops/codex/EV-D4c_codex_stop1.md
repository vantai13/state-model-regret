Đã **dừng theo điều kiện “stop and report”** trong [brief](/home/vantai/state-model-regret/notes/ops/codex/EV-D4c_brief.md:19), vì phát hiện blocker thực tế.

- **Blocker:** brief yêu cầu ID như `LB00_r0.1`, nhưng [packet.py](/home/vantai/state-model-regret/experiments/ext_validity/packet.py:443) cấm dấu chấm. Main train qua CLI sẽ báo `ValueError: unsafe case id`.
- **Đã kiểm chứng:** chạy `python3` trong môi trường được chỉ định, gọi `packet.validate()` cho đủ 8 giá trị r: **6 bị từ chối**, chỉ `r1` và `r5` được chấp nhận; command mất khoảng **0,21 giây**.
- **τ < 1 s:** qua đọc code, `max(TAU, ...)` giới hạn spacing; τ vẫn được dùng trong `ts - tau`. Chưa chạy smoke train/simulate vì đã gặp điều kiện dừng.
- **File/output:** chưa tạo ba file mới, không sửa file hiện có; không tạo log, CSV/JSON hoặc báo cáo. Chưa chạy pytest, probe hay full panel; không commit hoặc SSH.
- **Ước lượng chi phí:** chưa đo probe. Theo mốc EV-D4b trong brief, 960 test outputs tối đa tương ứng khoảng **176 phút trên 12 vCPU × tỷ lệ T_int trung bình**, chưa gồm train; đây chỉ là ngoại suy.

Cần sửa yêu cầu ID trong brief, chẳng hạn dùng `LB00_r0p1` và giữ trường số `r=0.1`, trước khi triển khai tiếp. Tôi chưa tự áp dụng thay đổi này.