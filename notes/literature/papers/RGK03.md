# RGK03 — Roughan et al.: biến động traffic backbone

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải file `download.pdf` sau danh sách L7.3-R2. Mức đọc: AI-T. Tác giả tự đọc: chưa có xác nhận.

Roughan, Greenberg, Kalmanek, Rumsewicz, Yates, Zhang. *Experience in Measuring Internet Backbone Traffic
Variability: Models, Metrics, Measurements and Meaning*.

**Phiên bản.** Có hai bản trên Crossref:
- IMW 2002, [DOI 10.1145/637201.637213](https://doi.org/10.1145/637201.637213), tiêu đề không có chữ "Internet";
- chương sách ITC-18, *Teletraffic Science and Engineering* (2003), tr. 379–388,
  [DOI 10.1016/s1388-3437(03)80183-x](https://doi.org/10.1016/s1388-3437(03)80183-x).

File tác giả tải có 10 trang, tiêu đề có chữ "Internet", không có khối copyright, tạo bằng Ghostscript ngày 16/05/2003.
AI coi đây là **bản tác giả của bản ITC 2003**, không phải VoR của bản nào; chưa đối chiếu chữ với VoR. Lưu tại
`~/papers/state-model-regret/l73/RGK03/RGK03_Roughan_backbone_variability_ITC_authorcopy.pdf`, sha256 `18be6ebc95b3…`.
Đọc targeted: §1/PDF1–2, §2.1–2.2/PDF2–3, §3.2/PDF4, §4/PDF6, §5.1/PDF7–8, §5.2 và §6/PDF8–10. Không kiểm các
phương trình bị hỏng khi trích text (bias correction, §3).

**Câu hỏi.** Traffic backbone WAN biến động ở thang nào? Phần nào dự đoán được, phần nào ngẫu nhiên?

**Quan sát (trích vị trí)**
- **Dữ liệu (§1–2.1/PDF1–2).** SNMP của backbone Tier-1 (AT&T), archive hơn 1 năm, mạng cỡ 1.000 node. SNMP có
  khoảng lấy mẫu thô, thiếu dữ liệu và dữ liệu sai. Dữ liệu 5 phút là "typical for SNMP measurements".
- **Thành phần (§1/PDF2).** Traffic có thành phần chu kỳ ngày, chu kỳ tuần và xu hướng dài hạn. Chồng lên trên là biến
  động ngẫu nhiên ở thang ngắn hơn.
- **Mô hình (§2.2/PDF3).**
  - x(t) = m(t) + √(a·m(t))·W(t), dựa trên mô hình Norros.
  - m(t) gồm xu hướng và chu kỳ ngày/tuần, gọi là phần "predictable".
  - W là quá trình dừng, trung bình 0, phương sai 1. a là peakedness.
  - SNMP không cho phép đặc trưng chi tiết W; bản Norros gốc là FGN (LRD).
- **Ước lượng (§3.2/PDF4).** Lấy trung bình mùa hoặc moving average để bỏ chu kỳ, rồi ước a từ phần dư.
- **Đo (§4/PDF6).** Traffic 5 phút trên khoảng 50 link OC48 liên thành phố. Phần lớn giá trị a nằm trong 0,5–3 (đơn vị
  "Mbs" theo bài); 15–25% lớn hơn. Bỏ anomaly thì a giảm rõ.
- **Ý nghĩa (§5.1/PDF7–8).** Mô phỏng mạng metro với traffic trung bình 350 Mbps mỗi node và a từ 0 tới 3,5, để so
  cấu hình tĩnh với cấu hình động.
- **Kết luận (§6/PDF9–10).**
  - Độ lệch lớn khỏi dự báo (không do đổi routing) là hiếm.
  - Biến động thường ngày có a trong 0,5–3,0 với dữ liệu SNMP 5 phút.
  - Chu kỳ ngày lớn nhưng đồng pha khắp Bắc Mỹ, nên không cho phép chia sẻ capacity theo thời gian.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- Với WAN, phần biến động lớn nhất là chu kỳ **xác định và dự đoán được theo giờ**. Nó gần với một "mode quan sát được"
  (biết giờ là biết mode) hơn là một mode Markov ẩn như trong ctmc-v1.
- Phần ngẫu nhiên có độ lệch chuẩn tương đối √(a/m). Với m = 350 Mbps (tham số mô phỏng §5.1, không phải số đo) và
  a = 0,5–3, con số này khoảng 4–9% ở dữ liệu 5 phút. Đây là phép tính của AI.
- Thang thời gian của W dưới 5 phút vẫn không đo được. Ô T_mode của (iii) vẫn UNSOURCED dưới 5 phút.
- Dữ liệu năm 2001–2002, link OC48. Không suy rằng WAN hiện đại có cùng a.

PC liên quan: realism / RQ3. Không đổi nhãn PC, không có claim novelty.
