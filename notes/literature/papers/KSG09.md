# KSG09 — Kandula et al.: bản chất traffic datacenter

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải (thư mục Downloads, 07:06–07:08 ngày 04/11) sau danh sách L7.3-R2 đợt 3. Mức đọc: AI-T.
Tác giả tự đọc: chưa có xác nhận.

Kandula, Sengupta, Greenberg, Patel, Chaiken. *The Nature of Datacenter Traffic: Measurements & Analysis*.
IMC 2009, tr. 202–208. [DOI 10.1145/1644893.1644918](https://doi.org/10.1145/1644893.1644918).

**Phiên bản.** 7 trang, có khối copyright ACM 2009 (camera-ready); chưa đối chiếu với ACM DL. Lưu tại
`~/papers/state-model-regret/l73/KSG09/KSG09_Kandula_IMC09.pdf`, sha256 `cccc43e9199e…`. pdftotext làm **mất chữ số**
(font), nên AI render và đọc ảnh các trang 202–206 và 208. Trang 207 (tomography) chỉ grep.

**Câu hỏi.** Câu "traffic matrix lacks predictability at time scales of 150 seconds or longer" mà MicroTE (BAAZ11 §4) trích
từ bài này có ở đâu? Traffic DC đổi nhanh cỡ nào?

**Quan sát (trích vị trí)**
- **Đo (§2–4, tr. 202–203).** Log socket trên 1.500 server (rack 20 server) hơn hai tháng. SNMP thường chỉ poll
  "once every five minutes". Ma trận traffic (TM) tính ở thang 1 s, 10 s và 100 s. Flow kết thúc theo inactivity timeout
  60 s.
- **Nghẽn (§4.2, tr. 204, Fig. 5–6).** Link được coi là nghẽn khi utilization > 70%.
  - Trong 150 link liên switch, 86% có nghẽn kéo dài ≥ 10 s; 15% có nghẽn kéo dài ≥ 100 s.
  - Trong các sự kiện nghẽn dài hơn 1 s, hơn 90% không quá 2 s.
  - Có 665 episode dài hơn 10 s trong một ngày; dài nhất 382 s.
- **Flow (§4.3, tr. 205, Fig. 9).** Hơn 80% flow kéo dài dưới 10 s, dưới 0,1% dài hơn 200 s. Hơn 50% byte nằm trong flow
  không quá 25 s.
- **Biến động của TM (§4.3, tr. 205–206, Fig. 10).** Normalized change |M(t+τ) − M(t)|/|M(t)|, với τ = 10 s và τ = 100 s:
  trung vị khoảng 82%; p10 là 37%, p90 là 149%. "Significant variability appears to be a key aspect of data center
  traffic."
- **Arrival của flow (§4.3, tr. 206, Fig. 11).** Có các mode chu kỳ cách nhau khoảng 15 ms. Toàn cluster có trung vị
  10⁵ flow/s.
- **Kết luận (§8, tr. 208).** Các thống kê này "more regular and better behaved" so với mạng ISP; "elephant" flow chỉ
  kéo dài khoảng 1 giây.

**Câu 150 s.** Không tìm thấy trong các trang đã xem (202–206 và 208, ảnh render). Bài cho TM đổi khoảng 82% ở cả 10 s và
100 s, tức gần như không có quán tính ở hai thang đó. Con số 150 s có thể là diễn giải của MicroTE; **chưa xác nhận**.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- Ở DC MapReduce này, TM giữa các server đổi mạnh ngay trong 10 s. Nếu coi đó là mode, T_mode,phys dưới 10 s. Điều này
  cùng chiều với BAAZ11 (ổn định 1,5–5 s cho top cặp ToR).
- Nghẽn có hai thang: phần lớn 1–2 s, nhưng có episode hàng trăm giây. Đây là đa thang ngay trong một DC.
- Dữ liệu một cluster năm 2009, workload mining.

PC liên quan: realism / RQ3. Không đổi nhãn PC.
