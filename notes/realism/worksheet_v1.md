# L3R.4 — Worksheet nguồn, v1

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026.
Hai bối cảnh giữ đúng DL-008 (08/10), không thêm bối cảnh sau pilot.
Nguồn mới đã được tác giả duyệt cả 3; mức đọc thực hiện thay tác giả là AI-T,
không phải L-self. [Approval/access](../../results/lessons/l3r_4/literature/approval.json).

| Đại lượng | Bối cảnh | Evidence có thể dùng | Định nghĩa/vị trí | Giới hạn chuyển sang envelope | Dải dùng phân loại |
|---|---|---|---|---|---|
| Capacity | a: DC 1–10 Gb/s | DL-008; ZLK17 có server–ToR 10Gb/s, uplink 40/100Gb/s | ZLK17 §4.2, PDF3 | Chỉ downlink10Gb/s trùng đầu miền a; không mở rộng miền sang100Gb/s | Bối cảnh định trước; không là bằng chứng về traffic offered |
| Capacity | b: edge10–100Mb/s | DL-008 | Quyết định phạm vi, không measurement | LTWW94 là LAN lịch sử, không đại diện edge hiện đại | Bối cảnh định trước |
| τ_eff | a/b | T00/EV-31: Planck đo rate cỡ ms; counter/poll có chu kỳ khác | T00 bảng telemetry; τ_eff≈P/2+L+W/2 | Chưa có P,L,W cùng schema backlog và cùng use case; latency/poll không tự bằng tuổi | **UNSOURCED** |
| d_act | a/b | Planck response2.5–9ms; Kuźniar confirmation/data-plane gap250/400ms | T00/EV-29, primary đối chiếu08/10; Planck§7.2/Fig16, Kuźniar§4.1/Table2 | Hai khoảng đo khác nhau; chưa có end-to-end action delay của use case | **UNSOURCED** |
| h giữ quyết định | a/b | MicroTE1s/Hedera5s trong T00 | Chu kỳ loop/poll, không thời gian giữ quyết định | Không thay giữ quyết định bằng chu kỳ | **UNSOURCED** |
| Observation | a/b | Planck rate; ZLK17 bytes/counter và peak shared-buffer occupancy | T00; ZLK17§4.1/PDF3,§6.4/PDF7 | Chưa chứng minh backlog chính xác+tuổi đến controller; mode ẩn không đo trực tiếp | **UNSOURCED**, mode oracle là scope |
| CV_rate(1ms,10ms,100ms,1s) | a | BAM10 traces binned10µs; ZLK17 throughput25µs | BAM10§3.1/PDF3; ZLK17§4.1/PDF3 | Không có dải CV_rate trên cả bốn cửa sổ; không tự đọc tọa độ figure thành CV | **UNSOURCED** |
| CV_rate cùng cửa sổ | b | LTWW94 count/byte series10ms; variance-time và IDC nhiều thang | LTWW94§4.1/PDF7,§5.2/PDF12 | IDC và CV interarrival không phải CV_rate; LAN1989–92 không là edge10–100Mb/s hiện đại | **UNSOURCED** |
| T_mode | a | Burst egress hot>50% trên25µs; p90<200µs cả3workloads, Web50µs | ZLK17§5.1/PDF4 (in81), Fig3/PDF3; Table2/PDF4 | Burst theo ngưỡng egress khác thời gian mode offered input; không gán p90=T_mode. Inter-burst không exponential§5.2 | **UNSOURCED** cho T_mode; evidence phản bác cấu trúc đơn giản |
| T_mode | b | Không có chiều dài burst duy nhất trên các LAN đã đo | LTWW94§3.1/PDF4,§4/PDF7–8,§5.2/PDF12 | Nhiều thang là cảnh báo mô hình, không số T_mode của edge hiện đại | **UNSOURCED** |
| Mean/peak offered load | a | BAM10 hotspot≥70%, nhiều cửa sổ5phút; ZLK17 egress hot>50% tại25µs | BAM10§6.2–6.3/PDF9; ZLK17§5.1/5.4/PDF4–5 | Ngưỡng định nghĩa không phải dải khả thi. Egress≤capacity không chặn offered arrivals>capacity | **UNSOURCED** |
| Mean/peak offered load | b | LTWW94 TableI/PDF2, utilization từng trace/giờ | Historical LAN byte counts | Không chọn min/max của trace thành giới hạn phổ quát cho edge hoặc cho offered input | **UNSOURCED** |
| Buffer B_t=buffer/c | a | ZLK17 shared buffer carving động; occupancy normalize theo maximum quan sát | §6.4/PDF7, Fig10 | Không absolute buffer bytes/per-port budget để đổi sang thời gian; caption300µs và text50ms là hai mô tả cần giữ riêng | **UNSOURCED** |
| Buffer B_t | b | Không có số phù hợp trong các mục đã đọc | — | Không đoán buffer từ RTT/end-to-end latency | **UNSOURCED** |
| Hình dạng traffic | a | BAM10 ON/OFF theo gaparrival95, fits lognormal/Weibull; ZLK17 hot process bất đối xứng | BAM10§5.2/PDF6–7/Table4; ZLK17Table2/PDF4 | ON/OFF trong paper không chứng nhận symmetric exponential modes ±0.6c | Scope/risk, không chứng nhận phân phối |
| Hình dạng traffic | b | LTWW94 self-similar, variance giảm chậm/IDC tăng nhiều thang | §4.1–4.2/PDF7–8;§5.2/PDF12 | Không kết luận tất cả Ethernet/edge giống dữ liệu lịch sử | Scope/risk |

Các dòng T00 là đọc lại evidence đã có, không ghi lần này đã đọc lại toàn bộ
primary Planck/Kuźniar/Hedera. Ba paper mới chỉ targeted, không full-read và
không có xác nhận tác giả tự đọc. Mỗi nguồn có note riêng trong
[literature/papers](../literature/papers/).

Kết luận trước bảng216: chưa xây được envelope số đồng nhất về định nghĩa cho
cả a lẫn b. **Không đủ nguồn không đồng nghĩa phi thực tế.** Envelope v1 sẽ lưu
null ở các ràng buộc bắt buộc, phân loại UNSOURCED và ghi HOLD realism.
Không dùng các con số hữu ích nhưng khác định nghĩa để tạo IN hoặc OUT giả.
