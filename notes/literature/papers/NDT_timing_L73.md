# Thời gian vòng của NDT what-if — bốn paper cũ của tác giả (L7.3)

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả nhắn "bạn còn có là các paper cũ của tôi bạn hãy xem thử mục tải về ở window ... và bổ sung thông tin thêm
cho lesson đi". Đây là ủy quyền đọc. Mức đọc của cả bốn: AI-T, chỉ grep theo câu hỏi thời gian vòng rồi đọc đoạn quanh.
Tác giả tự đọc: chưa có xác nhận.

PDF chép (không di chuyển) từ thư mục Downloads của Windows vào `~/papers/state-model-regret/l73/ndt_old/`.

**Câu hỏi.** Một vòng NDT what-if cần bao lâu để đồng bộ trạng thái, đánh giá ứng viên và áp quyết định? Có nguồn nào
cho h, tức thời gian giữ quyết định?

| ID | Nguồn | Bản đọc | Số liên quan (vị trí) |
|---|---|---|---|
| ZBEK26 | Zalat, Barber, Esfandiari, Kunz, *A Reusable Network Digital Twin Architecture for QoS-Centric Network Management*, IEEE TNSM 23 (2026), tr. 8111–8124, [DOI 10.1109/TNSM.2026.3737654](https://doi.org/10.1109/TNSM.2026.3737654) | Author version, 14 tr., sha256 `d44a189db560…` | Twin dự đoán delay cho 25k flow trên mạng 260 node trong 200 ms, so với 82 phút của OMNeT++; đây là "preliminary experiment" (§I-C/PDF2). Search lặp N vòng "or, equivalently, until a fixed time budget elapses" (§IV-D/PDF6). Thí nghiệm BGP đặt N = 1000 (§V-D/PDF9) |
| VGC23 | Vilalta et al., *Applying Digital Twins to Optical Networks with Cloud-Native SDN Controllers*, IEEE Commun. Mag. 61(12) (2023), tr. 128–134, [DOI 10.1109/MCOM.003.2300105](https://doi.org/10.1109/MCOM.003.2300105) | Bản tác giả (pdfTeX, 7 tr.), không phải VoR, sha256 `a32dfd6cb1cc…` | Tạo NDT trung bình 2,38 s (sd 0,9 s), xóa 0,85 s. NDT cập nhật sau sự kiện: node down 0,96 s (sd 0,52), giảm bandwidth 0,03 s, mất link 0,009 s (§III/PDF5–6, Fig. 4–5) |
| HHZ26 | Hu, Huang, Zhang, Lin, Wu, *Digital twin-guided service-aware graph attention ant colony optimization for reliable dynamic IPv6 routing in power data networks*, Sci. Rep. (2026, article in press), [DOI 10.1038/s41598-026-71181-2](https://doi.org/10.1038/s41598-026-71181-2) | Bản "Article in Press", 31 tr., sha256 `397e326b6ee6…` | Twin cập nhật dưới 5 ms; trung bình 0,173 s mỗi yêu cầu route; phần lớn thời gian là ACO search (Table 15/PDF25). Full rerouting recovery 186,9–213,5 ms; chuyển backup 8,7–18,6 ms (Table 11/PDF24). Sai số trạng thái đến từ "discrete synchronization intervals", nhưng phần đã đọc không cho độ dài interval (PDF5) |
| AAA25 | Aben-Athar et al., *Network Digital Twin for Route Optimization in 5G/B5G Transport Slicing with What-If Analysis*, ICC Workshops 2025, [DOI 10.1109/ICCWorkshops67674.2025.11162404](https://doi.org/10.1109/ICCWorkshops67674.2025.11162404) | arXiv 2505.04879v1 (6 tr.), sha256 `3108a8fec0b2…` | Recommendation chạy khi có failure; route mới chọn ở các mốc N3/N5/N7, không có số giây (§V/PDF5). "Response time will also be included in decision-making" là hướng tương lai, tức bài **chưa đo** thời gian phản hồi (§VI/PDF6) |

Ghi chú:
- AAA25 (2505.04879) đã có trong `ndt_landscape.md`. Trong đợt đọc được duyệt 26/10/2026 (sau L2.9), tác giả từng quyết
  định "không đọc thêm" (search log, dòng R06/2211.01961v2/…). Lần này đọc lại là theo yêu cầu mới của tác giả, chỉ để tìm thời gian vòng.
- Ba file khác trong Downloads cũng đã mở trang đầu, nhưng chỉ có mô tả chung về "real-time synchronization" hoặc
  "twinning rate", không có số của vòng routing what-if:
  - Poorzare et al., IEEE Access 2025, survey NDT, DOI 10.1109/ACCESS.2025.3531947;
  - Hakiri et al., Computer Networks 244 (2024) 110350, survey;
  - Adhikari và Hathurusinghe, survey không rõ venue.

  Bài của Adhikari có nhắc "digital twin is updated at 10 ms" (PDF7), nhưng đó là dẫn lại một khung DRL không dây.
  Không dùng ba bài này làm nguồn.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- Không bài nào cho h (thời gian giữ quyết định) của vòng NDT what-if. AAA25 kích hoạt theo failure; ZBEK26 tối ưu
  trọng số IGP và gán route BGP, những loại cấu hình thường được giữ lâu, nhưng thời gian giữ đó là **UNSOURCED**.
- Các số trên chỉ góp vào τ: đồng bộ 0,009–0,96 s (quang), cập nhật twin dưới 5 ms, quyết định 0,17–0,2 s mỗi yêu cầu
  hoặc mỗi lần đánh giá.
- Nếu search đánh giá tuần tự 1.000 ứng viên, mỗi ứng viên 200 ms, thì quyết định mất cỡ 200 s. Đây là cận trên do AI
  tính; bài không báo con số này và có thể dừng theo time budget.
- Vì vậy NDT what-if **không tự mang một h riêng**. Nó là một thủ tục ra quyết định gắn vào một vòng điều khiển khác
  (DC TE, WAN TE, khôi phục sự cố), và cộng thêm vào τ của vòng đó.

PC liên quan: realism / RQ3, định vị NDT. Không đổi nhãn PC, không có claim novelty.
