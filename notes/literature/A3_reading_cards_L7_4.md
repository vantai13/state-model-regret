# A3 (L7.4) — ba nguồn, đúng phần được trích, mỗi nguồn ba câu

Doan Van Tai — **AI (Claude) đọc và viết theo ủy quyền** ("đóng vai trò là tôi", 04/11/2026). Mentor ghi A3 là việc của
tác giả. **Đây không phải tác giả đọc**: mức đọc của tác giả cho ba nguồn vẫn là "chưa có xác nhận", và cột "Mức tôi đã
đọc" trong Excel không đổi. AI đã mở lại PDF ở đúng các trang dưới đây trong phiên này (pdftotext; tr. là trang PDF).

## LPC04 — Lakhina et al., SIGMETRICS 2004 · §5.2 và Table 2

PDF `~/papers/state-model-regret/l73/LPC04/LPC04_odflows_SIGMETRICS04.pdf`, tr. 9.

1. **Bài đo gì.** Bài phân rã phương sai của các OD flow trên hai backbone thành ba loại eigenflow: chu kỳ xác định (d),
   spike (s) và nhiễu (n). Mỗi OD flow được chuẩn hóa về trung bình 0, phương sai 1, gom theo bin 10 phút (Sprint) hoặc
   5 phút (Abilene).
2. **Số ta dùng.** Table 2 (tr. 9): phần năng lượng của d/s/n là 92,17%/5,59%/2,24% (Sprint-1) và 69,79%/18,60%/11,61%
   (Abilene). §5.2: flow lớn chủ yếu là chu kỳ.
3. **Khác định nghĩa.** Thành phần chậm của bài là **chu kỳ biết trước theo giờ**, không phải mode Markov ẩn như κ của
   ta. Tỷ lệ năng lượng tính sau khi chuẩn hóa từng flow, không phải phần phương sai của tải trên một link. Thang thời gian
   ≥ 5 phút, không đo được gì dưới bin.

## BAAZ11 — Benson et al., MicroTE, CoNEXT 2011 · §4.1.1 và §5

PDF `~/papers/state-model-regret/l73/BAAZ11/BAAZ11_MicroTE_CoNEXT11_VoR.pdf`, tr. 5–6.

1. **Bài đo gì.** §4.1.1 (tr. 5) đo mức dự đoán được của traffic giữa các cặp ToR ở hai DC (CLD MapReduce, UNV): một cặp
   "dự đoán được" nếu traffic đổi không quá 20% trong 1 s. §5 (tr. 6) thiết kế MicroTE: mỗi khoảng 1 s route tối ưu phần
   dự đoán được, phần còn lại chia bằng weighted ECMP.
2. **Số ta dùng.** Khoảng 35% tổng traffic dự đoán được. Ở CLD, 60% số cặp ổn định trung bình 1,6–2,5 s. Ở UNV, khoảng
   35% số cặp ổn định 1,5–5 s. Chu kỳ quyết định h = 1 s.
3. **Khác định nghĩa.** "Thời gian ổn định" của bài là run-length dưới ngưỡng 20%, chỉ xét top 100 cặp, **không phải**
   thời gian lưu của một mode exponential (κ) hay T_int của backlog. Câu "không dự đoán được từ 150 s" ở §4 là dẫn lại
   [13], [6], bài không tự đo.

## GZL22 — Ghabashneh et al., IMC 2022 · §5–6

PDF `~/papers/state-model-regret/l73/GZL22/GZL22_microscopic_bursts_IMC22.pdf`, tr. 6–7.

1. **Bài đo gì.** §5 (tr. 6) mô tả dữ liệu Millisampler ở host (Meta), mẫu 1 ms trong khoảng 2 s mỗi run. Burst là chuỗi
   mẫu 1 ms liên tiếp vượt 50% line rate. §6 (tr. 7) cho thống kê burst.
2. **Số ta dùng.** Trung vị 7,5 burst/s (p90 39,8). Thời lượng trung vị 2 ms (p90 8 ms). Utilization trong burst trung
   vị 65,5%, ngoài burst 5,5%. 34% số run có ingress bursty.
3. **Khác định nghĩa.** Burst định nghĩa bằng ngưỡng 50% trên mẫu 1 ms, nên thời lượng phụ thuộc độ phân giải
   (ZLK17 ở 25 µs cho thang khác). ON/OFF **rất bất đối xứng** (T_on ≈ 2 ms so với T_off ≈ 133 ms, AI tính), trong khi
   ctmc-v1/v2 giả định mode đối xứng. Cả hai mode đều dưới tải ổn định ở link host, nên stake backlog ở link host nhỏ.

**Việc của tác giả còn mở:** tự mở ba PDF ở đúng các trang trên, tự viết ba câu cho mỗi nguồn, ghi lời của mình vào
`author_reading_record.md`. AI không điền record đó.
