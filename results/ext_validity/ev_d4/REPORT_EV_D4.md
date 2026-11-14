# EV-D4 — telemetry-age dose response on a 4 h continuous MAWI trace: STOPPED as infeasible before the test (14/11/2026)

Doan Van Tai — **AI (Claude) theo ủy quyền** ("thực hiện như bạn đề xuất"). Chạy trên VM GCP. Nhánh `ext/validity`.

## Thiết kế (khóa trong commit, trước khi train)

- **Trace:** 16 file MAWI DITL 2023-04-12 liên tiếp (10:00–14:00, 1,44 triệu bin 10 ms, chỉ hụt 8 bin).
- **Panel:** 20 regime × τ ∈ {1, 10, 30, 60, 120, 300} s = 120 case.
- **Sửa theo audit:**
  - B3: hai đường A/B dùng hai mẫu luồng rời nhau (s0, s1) và **chung một pha thời gian thật**;
  - B1: thêm D6, phép thử đúng nội dung T12 (hại không tăng từ 10T lên 30T);
  - thêm D5 (dose response theo τ).
- **Luật khả thi** (khai trước train): bỏ regime nếu T_int bị kiểm duyệt (censored) hoặc 30·T_int > 7200 s.

## Diễn biến (chỉ có train, không có output test nào)

| Lần | Mức gộp | T_int train (trung vị, khoảng) | Regime bị loại | Quyết định |
|---|---|---|---|---|
| 1 (`83b7bec4`) | mod 250 (0,4% luồng; cùng lưu lượng mẫu EV-D3b) | 1445 s (1135–1836) | 20/20 | thiết kế lại một lần, ghi trước (`d98becf5`) |
| 2 (`2be6e3fc`) | mod 10 (10% luồng) | 535 s (86–1385) | 16/20 (80%) | **dừng** theo luật khai trước (> 50%) |

Mô tả chuỗi, không cần train:

| Chuỗi | Trung bình theo phút / trung bình chung |
|---|---|
| mod 1000 | 0,16–14,9× |
| mod 250 | 0,31–6,8× |
| mod 10 | 0,63–1,87× |
| toàn link | 0,84–1,27× |

T_int tăng mạnh theo tải. Bốn regime còn lại sau luật đều có tải lớn nhất ≤ 0,87 và T_int 86–215 s.

## Chẩn đoán sau khi dừng (chỉ train, không có outcome): việc lặp trace 15 phút có làm T_int ngắn đi không?

- **Cách làm:** giữ nguyên 20 regime, seed, τ = 30 s và cách chung pha. Chỉ thay chuỗi bằng **một file 15 phút** của cùng bản trích mod 10, cho lặp như EV-D2/D3. Thử hai đoạn: 10:00 và 12:00.
- **Code:** `experiments/ext_validity/ev_d4_loopdiag.py`; output ở `diag_loop15/summary.json`.

| Chuỗi | T_int trung vị (min–max) | Tỷ lệ lặp/4 giờ (trung vị, khoảng) |
|---|---|---|
| 4 giờ liên tục | 536 s (86–1385) | — |
| Lặp đoạn 10:00 | 57 s (8–129) | 0,10 (0,09–0,16) |
| Lặp đoạn 12:00 | 104 s (10–136) | 0,17 (0,09–0,31) |

**Đọc kết quả.** Đây là chẩn đoán sau, chỉ mô tả, trên một trace.
- Phát lại một đoạn 15 phút loại bỏ mọi biến động chậm hơn 15 phút. Trong traffic này, chính phần biến động đó quyết định T_int, nên T_int bị rút ngắn 6–10 lần.
- T_int của wave 2–3 (40–78 s) cùng cỡ với T_int của trace lặp, nên **có thể cũng bị rút ngắn giả tạo**.
- Hệ quả 1: các kết quả "h = 30 T_int" của wave 3 vẫn đúng cho **quá trình Cox tuần hoàn 15 phút** đã mô phỏng. Nhưng **không được** đọc là horizon "dài" của traffic thật liên tục. Với traffic thật, h ≈ 20–36 phút chỉ tương đương khoảng 2–5 T_int.
- Hệ quả 2: trên traffic thật liên tục ở tải ≥ 0,85, vùng h ≫ T_int (nơi luật bậc một và T12 có hiệu lực) cần horizon **nhiều giờ**.

## Giới hạn

- Chỉ một trace và một khung giờ. Hai đoạn lặp có thể khác đặc trưng với phần còn lại của 4 giờ (xu hướng chậm).
- T_int đo bằng cách cắt tích phân ACF ở điểm cắt 0 đầu tiên, như các wave trước.
- Không có outcome, nên chưa biết tác động lên dấu hay độ lớn của harm.
- AI tự thiết kế. Hai lần dừng/thiết kế lại đều được ghi trước khi train.

## Việc tiếp (đề xuất, chờ tác giả)

1. **Trước khi viết claim thực tế:** thêm vào câu claim của wave 3 rằng T_int đo trên trace lặp. Nếu muốn kiểm harm trên traffic liên tục, cần horizon nhiều giờ, nghĩa là trace 24 giờ trở lên, hoặc giới hạn ở tải thấp (≤ 0,85). Lựa chọn này thuộc về tác giả.
2. Thử lại đúng thiết kế EV-D4, chỉ trên regime tải thấp. Đây sẽ là một thẻ mới, không phải cứu EV-D4.
