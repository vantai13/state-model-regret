# LPC04 — Lakhina et al.: phân rã cấu trúc của OD flow trên backbone

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải (`Downloads/tmp/odflows-sigm04.pdf`, 06:38 ngày 04/11) sau danh sách L7.3-R2. Mức đọc: AI-T.
Tác giả tự đọc: chưa có xác nhận.

Lakhina, Papagiannaki, Crovella, Diot, Kolaczyk, Taft. *Structural Analysis of Network Traffic Flows*.
SIGMETRICS/Performance 2004, tr. 61–72. [DOI 10.1145/1005686.1005697](https://doi.org/10.1145/1005686.1005697).

**Phiên bản.** 12 trang, trang 1 có khối copyright ACM 2004, file tạo 03/04/2004. AI coi đây là bản camera-ready của
tác giả; chưa đối chiếu với ACM DL. Lưu tại `~/papers/state-model-regret/l73/LPC04/LPC04_odflows_SIGMETRICS04.pdf`,
sha256 `3c6a24aef511…`.
Đọc targeted: §3.1–3.2/PDF4, §4.1/PDF5, §5.1–5.2/PDF7–9 (Table 2, Fig. 12), §6/PDF10. Không kiểm lại các phương
trình PCA.

**Câu hỏi.** Trên backbone, phương sai của traffic chia cho các thành phần chu kỳ, burst và nhiễu theo tỷ lệ nào?

**Quan sát (trích vị trí)**
- **Dữ liệu (§3.1–3.2/PDF4).**
  - Sprint-Europe: 13 PoP, traffic thương mại; NetFlow lấy 1/250 packet; gom vào bin 10 phút.
  - Abilene: 11 PoP, traffic đại học; lấy mẫu 1%; gom vào bin 5 phút.
  - Chuỗi dài nhiều ngày tới nhiều tuần.
- **Chuẩn hóa (§4.1/PDF5).** Mỗi OD flow được chuẩn hóa về trung bình 0 và phương sai 1 trước PCA.
- **Phân loại eigenflow (§5.1/PDF7–8).**
  - d-eigenflow: đỉnh phổ ở 12 h hoặc 24 h, tức chu kỳ ngày và khác biệt ngày thường/cuối tuần, "relatively
    predictable".
  - s-eigenflow: spike ngắn vượt 5σ.
  - n-eigenflow: gần dừng và gần Gaussian.
  - Chỉ 4 (Sprint) và 2 (Abilene) eigenflow không phân loại được, chiếm 0,012% và 0,26% năng lượng.
- **Tỷ lệ năng lượng (§5.2, Table 2/PDF9).**

  | | Chu kỳ (d) | Spike (s) | Nhiễu (n) |
  |---|---:|---:|---:|
  | Sprint-1 | 92,17% | 5,59% | 2,24% |
  | Abilene | 69,79% | 18,60% | 11,61% |

- **Theo kích thước flow (§5.2/PDF9, Fig. 12).** OD flow lớn chủ yếu là chu kỳ. Flow nhỏ chủ yếu là spike (Sprint)
  hoặc nhiễu (Abilene).
- **Ổn định theo thời gian (§6/PDF10).** Thành phần chính của tuần 1 xấp xỉ tuần 2 với sai số tương đối khoảng 10% cho
  khoảng 20 flow nặng nhất.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- Đây là nguồn đầu tiên trong L7.3 cho **tỷ lệ phương sai f theo thành phần**, nhưng chỉ ở bin 5–10 phút. Ở thang đó:
  - 70–92% phương sai (sau chuẩn hóa) là chu kỳ xác định, dự đoán được theo giờ;
  - 6–19% là spike;
  - 2–12% là nhiễu.
- Vì mỗi flow được chuẩn hóa phương sai 1, tỷ lệ trên cân bằng flow nhỏ với flow lớn. Với tải tổng của một link, flow
  lớn (chủ yếu chu kỳ) còn chiếm phần lớn hơn. Đây là suy luận, chưa tính.
- Phương sai dưới 5 phút vẫn không đo được, nên T_mode dưới 5 phút của ô (iii) vẫn UNSOURCED.
- Thành phần chậm là chu kỳ biết theo giờ, không phải mode Markov ẩn. Kết luận này cùng chiều với RGK03.
- Dữ liệu năm 2003–2004, hai backbone (một thương mại, một học thuật).

PC liên quan: realism / RQ3. Không đổi nhãn PC, không có claim novelty.
