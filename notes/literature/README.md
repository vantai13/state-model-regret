# Literature — L2.1–L2.3, Part A

Người phụ trách: **Doan Van Tai** · 24/10/2026.

**Tìm hoặc kiểm paper mới: mở [quy tắc + checklist](search_protocol.md) trước.**
Hỏi → Tìm → Kiểm → Duyệt → Đọc → Ghi → Dừng. Áp dụng cả tra DOI và khảo sát;
ưu tiên NDT/networking, ghi kết quả thực vào [search log](search_log.md).
Các mục Part A bên dưới là artifact đã lưu, không phải yêu cầu đọc hết trước
khi tìm paper networking.
[Thư viện đang dùng](../../papers/README.md) · [18 bài lưu tạm và snapshot cũ](../../papers/archive/README.md).

Provenance: AI triển khai theo ủy quyền của tác giả. Nguồn được AI đọc không phải
L-self của tác giả. Ngày này là ngày lưu artifact và tái kiểm; không phải ngày dự
đoán mù. Contract v1.2, Main RQ, lưới, thresholds và held-out không đổi.

## L2.4 Part 2–3 — NDT/networking

Mở [ndt_landscape.md](ndt_landscape.md): pipeline, bảng biến, metric,6nguồn,
đính chính lesson, snowball thật và5câu định vị. Note chính: [NDT1](papers/NDT1.md),
[P05](papers/P05.md), [P10](papers/P10.md). Tất cả là AI-only; giữ G1, chờ L-self/Gate.

## Điểm bắt đầu

- [Báo cáo và checklist ba lesson](../../results/lessons/part_a/report.md).
- [Claims và điều kiện bác bỏ](claims.md), [dự đoán đã exposed](prior_predictions.md).
- [Ánh xạ sáu contrast](already_implied.md), [T03 v2: phép dẫn](../theory/T03_primary_reading_start.md).
- [Prior boundary](prior_boundary.md), [matrix](matrix.md), [search log](search_log.md).
- [P11](papers/P11.md), [SOB14](papers/SOB14.md), [B82](papers/B82.md),
  [MAB11](papers/MAB11.md), [E07](papers/E07.md), [SOC12](papers/SOC12.md).
- [Phân loại artifact](artifact_classification.md), [thuật ngữ](terms.md).

## Quyền sử dụng evidence

S = screen; A = abstract; T(§/trang) = targeted; F = full. T và F khác nhau.
Mỗi note ghi thêm mức `metadata-only`, `abstract-only` hoặc
`AI đọc full text (§…/trang …)`; cách ghi cuối chỉ phạm vi full-text đã tiếp cận,
không tự nâng targeted reading thành full reading. Tất cả note hiện là **AI-only**;
L-self chỉ đổi khi có record tác giả mở nguồn và kiểm thật.

Fact, Claim, Evidence, Inference được tách trong từng note. Mọi inference về
contract là suy luận của dự án, không gán cho paper. Nhãn prior boundary là
**AI đề xuất**, chưa phải quyết định cuối Gate L. Không xác nhận novelty/G2.

PDF và text trích xuất nằm ngoài repo tại `~/papers/l2_part_a/`; checksum và trạng
thái tải được ghi trong `results/lessons/part_a/source_access.json`.

## Luật dừng đã lưu

Mỗi nguồn: dừng khi trả lời được câu hỏi hoặc khoảng 90 phút không tiến triển;
ghi Unclear nếu thiếu nội dung. Mỗi vùng blind-spot: hai query liên tiếp, mỗi
query screen 20 kết quả đầu mà không có candidate mới. Đây là quy tắc quy trình,
không chứng minh coverage. Lượt này là lookup nguồn có tên, không phải bốn phiên
blind-spot L2.8; không ghi đã đạt điều kiện đó.

## Deviation và điều kiện còn mở

1. Nội dung L2.1–L2.3 đã xuất hiện trong chat trước khi tạo thư mục này. Không thể
   phục hồi commit dự đoán trước exposure; giữ nguyên lịch sử, ghi deviation.
2. Dự đoán do AI hỗ trợ theo yêu cầu tác giả; không đo calibration cá nhân/mù.
3. Tác giả tự dẫn kín sách, L-self, đọc lại sau một ngày và người đọc độc lập chưa
   có record. Không tạo bằng chứng thay người thật.
4. Technical completion và formal Gate là hai trường riêng trong báo cáo.
   Không commit L3.3 prediction card hoặc chạy Phase 3 trong tác vụ này.
