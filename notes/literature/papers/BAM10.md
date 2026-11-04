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

**Bổ sung L7.3 (04/11/2026, AI-T, chỉ §6.4).**
- §6.4/PDF10–11 (Fig. 14–15): chu kỳ ngày và chênh lệch ngày thường/cuối tuần có ở mọi DC trong một tuần đo.
- Chênh lệch đỉnh–đáy dưới 10% ở ít nhất 80% link biên; aggregation biến động hơn một chút (PRV2 biến động rõ).
- Ở lõi, phần lớn DC biến động dưới 1%; riêng CLD4 và CLD5 biến động rõ.
- Không có phần nào ở §6.4 nói câu "không dự đoán được từ 150 s"; MicroTE dẫn câu đó từ [13] Kandula'09 và
  [6] Benson WREN'09.
