# L3R.8 — các DL soạn sẵn (bản nháp lịch sử)

> **Đã chốt 30/10/2026 ở DL-097–102** trong decision log, theo yêu cầu nguyên văn của tác giả "… đống lesson cho tôi
> đi đây là yêu cầu". Khác bản nháp: DL-099 giữ P0-V10 **OPEN** (AI không tự miễn luật của tác giả); DL-101 là đóng
> audit L3R.3; Gate 3R là DL-102. File dưới đây giữ nguyên nội dung nháp.

Người phụ trách: **Doan Van Tai**. AI (Claude) soạn theo lesson L3R.8 và yêu cầu "làm những cái bạn có thể tự làm".
**Chưa có DL nào dưới đây được ghi vào `notes/02_decision_log.md`.** Mỗi DL chỉ vào log khi tác giả trả lời nguyên văn
(ví dụ "duyệt DL-097", "chọn (a) cho P0-V10"). Khuyến nghị lấy từ lesson; AI không tự chọn thay.

---

### DL-097 (nháp) — D22: chuyển từ điều kiện vào Phase 4 sang Phase 5

- **Vấn đề (G4).** Hai văn bản mâu thuẫn:
  - contract v1.3 §3: "D22 … implementation và audit DEFERRED trước Phase 4";
  - card v2 dòng 191: "D22 F̄/V̄ chỉ khi D22 đã implement+audit, nếu không thì null (không gán cb0=0)".
- **Quyết định đề xuất.** Phase 4 chạy không có D22; F̄/V̄ = null, đúng như card v2 cho phép. Mục D22 của contract
  sửa thành "trước Phase 5" trong một bản contract v1.3.x mới (tag mới, số cụ thể đặt khi tạo); tag `contract-v1.3` giữ nguyên.
- **Lý do.** F̄/V̄ không vào verdict nào. D22 là phép tách cơ chế (backlog tươi so với biết mode), Phase 5 đằng nào
  cũng cần.
- **Hệ quả.**
  - Câu chữ SH giữ đúng card: "state repair (backlog + mode oracle) dưới M0".
  - Không được nói "backlog tươi có hại" hay "telemetry tươi có hại".
  - D22 tính sau trên regime CF là phân tích cơ chế/discovery, không phải confirmation.
- **Không đổi:** card v1/v2, numerics, n, root, danh sách CF.
- **Phương án khác:** implement và audit D22 trước Phase 4, như cam kết gốc. Tốn thêm một đường tính cb0 và audit;
  không đổi verdict.

### DL-098 (nháp) — Realism: Phase 4 chạy, claim ở mức mô hình

- **Phân loại.** HOLD_UNSOURCED là **outcome** của L3R.4, không phải lỗi validity. Quy trình đúng: envelope `6bef959`
  có trước nhãn `1164500` (đã kiểm ancestry).
- **Quyết định đề xuất (lựa chọn b).**
  - Không chặn Phase 4.
  - Mọi claim kèm câu phạm vi contract §6: "Realism vùng discovery chưa sàng lọc được … Chưa biết có gặp ở mạng
    thật không; không đồng nghĩa đã biết OUT".
  - Realism chuyển sang Phase 6/7.
- **Không được:** claim realism, tần suất ngoài đời, hay khuyến nghị vận hành.
- **Phương án khác:**
  - (a) chặn Phase 4 tới khi có nguồn: có thể không bao giờ mở;
  - (c) envelope v2 ngay: quá tay so với giá trị.

### DL-099 (nháp, HAI PHƯƠNG ÁN — tác giả chọn) — P0-V10 người đọc độc lập

- **(a) Có người đọc.** Một người có quyền nói "không" đọc gói tài liệu (card v2 §2–4, contract §6, gate note) cùng
  sáu câu ở [phiếu đọc](author_reading_sheet.md), khoảng một giờ. Ghi vai trò người đọc, ngày, đã đọc gì, đã phản hồi
  gì, đã sửa gì.
- **(b) Miễn bằng DL**, giống V9 (DL-054). Ghi rõ rủi ro ER3 được giữ lại: chuỗi review → pilot → card → numerics → CF
  phần lớn do AI soạn hoặc chạy, nên lỗi có thể đi cùng một hướng. Review của AI, kể cả lesson L3R.8, không tính là
  đọc độc lập.

### DL-100 (nháp) — L8 dời sang Phase 8

- L8 (người đọc ranh giới prior/novelty) ảnh hưởng claim novelty, không ảnh hưởng validity của Phase 4.
- Dời sang Phase 8 (final novelty audit). Gate L vẫn tối đa "GO có điều kiện"; không claim novelty trước đó.

### DL-101 (khung) — Nhãn Gate 3R (TÁC GIẢ CHỌN VÀ VIẾT LÝ DO)

```text
Nhãn: ⟨…⟩   (lesson khuyên NARROW: thu hẹp miền claim về mức mô hình; không phải số hypothesis)
Claim gắn kèm: ⟨xem gate note nháp⟩
Lý do (tác giả viết, 3–5 câu): ⟨…⟩
```

---

## Ghi chú kèm (không cần quyết, chỉ cần nói rõ)

- **G2.** Card v2 (chép từ v1) ghi Ω⁻ là "NGOẠI SUY (pilot chưa có cấu hình nào)". Đúng với pilot, nhưng trước khi rút
  CF đã có 24 khóa trong MV-ii và 45 trong SH-ii ([freeze_check](freeze_check.json)). Card đã đóng băng nên không sửa
  tại chỗ; ghi trong gate note và báo cáo Phase 4.
- **G6.** Plan liệt kê control "conservation" (regime không chạm biên rỗng) trong V3R-2.
  - Dưới P1, phân phối dừng có nguyên tử dương tại q = 0 ở mọi regime ổn định (mode OFF luôn rút cạn vì λ + u < 10),
    nên **không tồn tại** regime conservation trong họ này.
  - Ghi "không áp dụng dưới P1; thay bằng zero-action và identical-model (0 chính xác, dry-run B)", không lặng lẽ bỏ.
- **G5.** Tag `explore-v13-regime-map` → `574a36f` đã tạo ở máy local (Bước 4), chưa push.
- **G1.** Runner Phase 4 chưa nối (`R3R_07_confirmation/run.py` vẫn DEFERRED). Đây là Bước 0 của Phase 4, là điều kiện
  vào Phase 4, không phải lỗi validity của Phase 3R.
