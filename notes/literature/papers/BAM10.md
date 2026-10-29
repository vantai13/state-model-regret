# BAM10 — Data-center traffic measurement

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026.
Được duyệt L3R.4; AI-T, tác giả tự đọc: chưa có xác nhận.

Benson, Akella, Maltz. IMC2010,267–280.
[DOI](https://doi.org/10.1145/1879141.1879175).
PDF14trang từ [Microsoft Research](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/11/DC-Network-Characterization-imc2010.pdf),
bản local `~/papers/state-model-regret/l3r_4/BAM10.pdf`.

Câu hỏi: có số đo hỗ trợ offered-load envelope và giả định nền đối xứng exponential không?
Mức đọc: targeted §3.1/PDF3,§5.2/PDF6–7/Table4,§6.2–6.3/PDF9;
đã xem hình/bảng PDF7. Không full-read.

Observation: mười DC; SNMP bytes-in/out được poll mỗi1–30phút (§3.1).
Đồ thị utilization lấy các khoảng5phút; hotspot định nghĩa utilization≥70%
(§6.2–6.3). Packet ON/OFF xác định từ ngưỡng95th-percentile gap;
Table4 fit OFF lognormal, ON lognormal/Weibull theo site (§5.2).

Inference cho L3R.4: traffic ON/OFF không chứng nhận hai rate cố định, holding
times exponential đối xứng. Coarse SNMP utilization và egress counts không
cho bound offered peak trong queue. Không lấy70% làm dải realism; không suy
novelty/PC hoặc phổ quát mọi DC. Chưa có CV_rate ở đủ4cửa sổ hay absolute buffer
theo thời gian cho hai bối cảnh. Nguồn giúp nêu limitation, chưa lấp các dải đó.
