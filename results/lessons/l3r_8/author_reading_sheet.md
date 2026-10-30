# L3R.8 Bước 1 — phiếu tự đọc của tác giả

> **30/10/2026:** tác giả xác nhận đã tự đọc và trả lời **ngoài vở** ([author-attested](author_attestation.json)).
> Câu trả lời không lưu trong repo; phiếu dưới đây giữ nguyên dạng trống.

Người phụ trách: **Doan Van Tai**. AI (Claude) chỉ dựng phiếu và đường dẫn; **mọi câu trả lời do tác giả tự viết**.
AI không điền, không gợi ý đáp án. Phần đã điền mới được ghi là "tác giả đã đọc card".

## Đọc gì (khoảng 45 phút)

1. Card v2, ba mục ([file](../../../notes/phases/PHASE_3R_hypothesis_cards_v2.md)):
   - §2 Hyp-MV (dòng 130–168);
   - §3 Hyp-SH (dòng 169–204);
   - §4 bảng verdict (dòng 205–223).
2. Contract §6, câu phạm vi bắt buộc đi cùng mọi claim ([file](../../../notes/01_definitions_v1_3.md), dòng 193–226).
3. Tùy chọn: [kết quả kiểm đóng băng](freeze_check.json).

Exposure cần biết khi đọc. Số khóa tham số đã tính trước khi rút CF, nằm trong từng vùng:

| Vùng | Khóa đã thấy | Nguồn |
|---|---|---|
| MV+A | 22 | pilot, calibration, regime map, lưới 1/100 |
| MV-ii | 24 | 17 calibration, 4 regime map, 3 lưới 1/100 |
| MV-BND | 20 | |
| SH+A | 85 | |
| SH-ii | 45 | 35 calibration, 10 lưới 1/100 |
| SH-BND | 52 | |

Vì vậy Ω⁻ **không còn** là "ngoại suy chưa ai thấy" như card ghi. Các regime CF trong Ω⁻ vẫn là điểm mới, nhưng
vùng đã có một phần lộ.

## Phiếu

```text
Ngày:            Thời gian đọc:          Đọc: card v2 §2–4, contract §6
Q1 Có câu nào trong card không thể sai không?
Q2 Vùng đối chứng (Ω⁻) có thật sự thất bại được không?
Q3 Envelope realism có dấu hiệu "may đo" cho vùng tín hiệu không?
Q4 Có lý do nào để nghi engine mà audit chưa kiểm không?
Q5 Câu chữ nào đang nói quá?
Q6 Nếu là reviewer, tôi sẽ hỏi gì đầu tiên?
Chỗ tôi chưa hiểu / không đồng ý:
Đề xuất sửa: "không"  hoặc  "card v3 + DL TRƯỚC Phase 4, có ghi exposure"
```

Khi điền xong, tác giả commit file này, hoặc nhắn nguyên văn để AI chép vào (ghi "author-attested", cơ chế DL-032).
