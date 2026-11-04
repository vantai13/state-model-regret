# GNM26 — OnlineTE: TE WAN phản ứng trực tuyến (preprint)

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải (thư mục Downloads, 07:06–07:08 ngày 04/11) sau danh sách L7.3-R2 đợt 3. Mức đọc: AI-T.
Tác giả tự đọc: chưa có xác nhận.

Ghavidel, Namyar, Matni, Willinger, Govindan. *Near-optimal Online Traffic Engineering*. arXiv 2605.16187v1
(15/05/2026). **Preprint, chưa bình duyệt**; chưa kiểm bản xuất bản. [arXiv](https://arxiv.org/abs/2605.16187).

**Phiên bản.** arXiv v1, 23 trang, lưu tại `~/papers/state-model-regret/l73/GNM26/GNM26_OnlineTE_arXiv2605.16187v1.pdf`,
sha256 `cb1414dc5f5b…`. Đọc targeted: abstract và §1/PDF1–2 (Fig. 1), §7.1–7.2/PDF8–10.

**Quan sát (trích vị trí)**
- **Hiện trạng (§1/PDF1, Fig. 1).** Vòng TE cổ điển chạy định kỳ trên controller ("Every 5 minutes"). "Deployed TE
  controllers typically re-optimize only once every few minutes" (dẫn [17] RedTE, SIGCOMM'24; [46] Teal, SIGCOMM'23).
  "Traffic demands can change over shorter timescales [17, 35] than the periodicity of TE."
- **Thí nghiệm (§7.1/PDF9).**
  - Demand đổi mỗi 20 s; trong 5 phút gần một nửa số entry đổi ít nhất 50%.
  - Bài viết mức này "comparable to dynamics observed in large WANs (nearly 40% within a 5-minute interval [35])"
    ([35] = Namyar et al., NSDI'24).
  - Baseline chạy lại mỗi 5 phút.
- **Kết quả (§7.2/PDF9–10).** OnlineTE hội tụ trong vài giây sau mỗi lần demand đổi. Regret của DeDe (chạy 5 phút) cao hơn
  khoảng 2–3×. Đây là regret theo MLU, không phải backlog.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- Ủng hộ h = T_c ≈ 5 phút cho TE WAN đang triển khai, cùng với HKM13 và P07.
- Gợi ý có biến động **dưới** chu kỳ TE, nhưng đó là dẫn lại ([17], [35]). Bản thân thí nghiệm của bài là demand tổng hợp
  (20 s), không phải đo.
- Hai nguồn đáng truy để lấp T_mode dưới 5 phút ở WAN: RedTE (SIGCOMM'24) và Namyar et al. (NSDI'24). Chưa tra DOI,
  chưa đề xuất.

PC liên quan: realism / RQ3. Không đổi nhãn PC.
