# VPA17 — LetFlow: load balancing bằng flowlet trong mạng bất đối xứng

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải (thư mục Downloads, 07:06–07:08 ngày 04/11) sau danh sách L7.3-R2 đợt 3. Mức đọc: AI-T.
Tác giả tự đọc: chưa có xác nhận.

Vanini, Pan, Alizadeh, Taheri, Edsall. *Let It Flow: Resilient Asymmetric Load Balancing with Flowlet Switching*.
NSDI 2017, tr. 407–420. [USENIX](https://www.usenix.org/conference/nsdi17/technical-sessions/presentation/vanini),
open access, không có DOI.

**Phiên bản.** Bản USENIX, 15 trang gồm cover. Lưu tại `~/papers/state-model-regret/l73/VPA17/VPA17_LetFlow_NSDI17.pdf`,
sha256 `8a89af468f60…`. Đọc targeted: §1/PDF2, §2.2/PDF5 (Fig. 3–4), §3/PDF6, §4.1–4.2/PDF6–7, Fig. 7–9/PDF8.
Không đọc §5 (đánh giá).

**Quan sát (trích vị trí)**
- **Định nghĩa (§1/PDF2, §2.2/PDF5).** Flowlet là một đợt packet tách khỏi đợt khác bởi khoảng trống lớn hơn flowlet
  timeout. Timeout phải lớn hơn chênh lệch trễ giữa các path.
- **Flowlet co giãn (§2.2/PDF5, Fig. 3–4).** Kích thước flowlet trên mỗi path thay đổi theo cách chia. Nếu chỉ 2% quyết
  định đi path S0, flowlet trên S0 lớn lên khoảng 65× so với path kia. Lý do: path chậm (rate thấp, trễ cao) dễ có
  timeout hơn, nên flowlet ngắn hơn.
- **Phát hiện flowlet (§3/PDF6).** Dùng age bit như CONGA, nên timeout thực nằm giữa Δ và 2Δ.
- **Ví dụ (§4.1/PDF6–7).** Timeout 200 µs, RTT 50 µs (không tính queueing). Việc đổi path xảy ra chủ yếu trong 30 ms đầu;
  sau đó flowlet timeout "become rare" và hệ đạt cân bằng.
- **Mô hình (§4.2/PDF7).** Mô hình Markov chain cho số flow trên mỗi path. Nếu Δ quá lớn thì không có timeout; nếu quá
  nhỏ thì đổi path ngẫu nhiên liên tục. Fig. 7–8 có đường 500 µs.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- **h của ô (i) là nội sinh.** Thời lượng flowlet, tức thời gian giữ một quyết định path, phụ thuộc vào chính trạng thái
  nghẽn và vào TCP. Ở cân bằng, đổi path trở nên hiếm, nên h hiệu dụng có thể dài hơn timeout nhiều bậc.
- ctmc-v1 coi h là tham số ngoại sinh. Đây là một điểm lệch contract cho ô (i).
- Lựa chọn path của LetFlow là **ngẫu nhiên**, không dùng state. Tác dụng cân tải đến từ cơ chế co giãn của flowlet, không
  đến từ telemetry tươi.

PC liên quan: realism / RQ3. Không đổi nhãn PC.
