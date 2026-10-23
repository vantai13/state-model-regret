# Phase 1 — HOLD, trạng thái cập nhật 23/10/2026

Người phụ trách: **Doan Van Tai**. **HOLD Gate1 và A01/A04**; G1 giữ nguyên. Bản CONDITIONAL GO ngày22/10 là lịch sử tại tag `contract-v1` (6bb631f), không là trạng thái hiện tại. Tag không di chuyển; f9ec182 chỉ thêm receipt, scientific files hai snapshot giống nhau.

Hai review mới dẫn PHASE_1 v1.0, SHA rút gọn47f9a335…d4d7ba, dòng332/1953: P0-V11 chưa đạt thì HOLD, không tag. Full file chưa được cung cấp để tự kiểm hash/câu gốc. Tạm áp quy tắc HOLD chặt hơn và ưu tiên master-plan được review dẫn; lời ngoại lệ từ lesson Part E không dùng để mở gate. Không ghi nguồn gốc đã verified khi chỉ có reviewer báo.

| Gate | Trạng thái và điều kiện gỡ HOLD |
|---|---|
| V1 | Bài/ảnh tính tay độc lập chưa có; golden supplied/reference không thay được |
| V2/V3/V4 | Hạ tầng kiểm, plant law và shared-belief interfaces đã có; giữ output lịch sử, thêm N1 kiểm strict ties |
| V5 | Final grid dt/calibration chưa có; old calibration SD invalid cho A01 |
| V6/V7 | v1 lỗi thiết kế13SD,3calibrationSD; v1.1 chưa có grid đã qua ĐK1/2 hoặc tag; six-check/source alignment còn chờ |
| V8 | Chưa có session giải thích cho người thật/record họ nói lại |
| V9 | External feedback chưa có; mock review không thay người đọc độc lập |
| P0-V3 | Read-back thực tế của tác giả chưa có |
| P0-V11 | Technical proof/reference có thể kiểm code; artifact kín sách/tự giải thích/xác nhận DL lõi chưa có |
| P0-V10 | Người đọc độc lập vẫn bắt buộc trước Phase4 |

[Mốc2](../design/decisions_v1_1_m2.md) đã ghi lựa chọn N2(a), numeric policy N1, model A stationary, fixed amplitude và các axis trước candidate calculations. Proof/test được tạo thay mặt tác giả là **technical reference**, không đóng understanding gates. Không tạo commit `[kín sách]` thay tác giả.

Gỡ HOLD cần: nguồn gate đầy đủ/đối chiếu được; V1/P0-V3/P0-V11/V8 thực có record; N1 đã kiểm non-circular strict sign; solver/prior và computational budget chứng nhận cho grid; B2/B3/B4 theo đúng chronological commits; B5 consistency rồi chỉ tag khi gate cho phép. A01/A04 không tự mở từ việc tests PASS. Phase2a có thể đọc riêng; chưa novelty hoặc network evidence.

Heads-up chỉ lưu nháp theo chỉ dẫn tác giả23/10, **không gửi**. Không tạo lịch/biên bản/read-back giả. Giữ lịch sử [CDE](../../results/lessons/l1_8_cde/report.md) và [B1](../../results/lessons/l1_8_v1_1_b1/report.md); input hash nguồn cũ đối chiếu snapshot git của lúc chạy, không sửa hash để khớp tài liệu active mới.
