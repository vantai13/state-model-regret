# Phase 1 — HOLD: B4 không đạt sau một redesign

Người phụ trách: **Doan Van Tai**, cập nhật23/10/2026. Kết quả PhầnA: solver/prior đã vượt nút thắt, nhưng lưới **REJECTED / NARROW REQUIRED**. Initial8/22 main in; một redesign11/22, yêu cầu15/22. Đã hết lượt redesign trong protocol này. Giữ đủ28ô+6reserve; chưa chốt calibration, chưa nâng contract draft hoặc tagv1.1, A01/A04 chưa mở.

| Gate / mục | Trạng thái thực tế |
|---|---|
| V1 | AUTHOR-ATTESTED: tác giả xác nhận trực tiếp đã làm ngoài repo, không lưu artifact để kiểm độc lập |
| V2/V3/V4 | Hạ tầng plant/belief/idle identity và strict-sign screen có tests/audits; chưa validation mạng |
| V5 | Chưa final grid dt hoặc calibration A01; budget tới dt/16 chỉ là ước lượng |
| V6/V7 | B2/B3 đủ chronology, B4 thất bại11/22<15/22; B5 readiness NOT_READY |
| V8 | AUTHOR-ATTESTED: tác giả xác nhận trao đổi người thật ngoài repo, không lưu record |
| V9 | Chưa external feedback; heads-up chỉ là nháp nội bộ theo chỉ dẫn tác giả |
| P0-V3 | AUTHOR-ATTESTED: tác giả xác nhận read-back ngoài repo |
| P0-V11 | AUTHOR-ATTESTED: tác giả xác nhận hoàn thành ngoài repo; không ghi independently verified |
| P0-V10 | Người đọc độc lập còn thiếu, chặn Phase4; không phải nguyên nhân B4 rejected |

Solver:20/20 certificate original và20/20 sau một redesign, law≤1e−10/posterior≤1e−8; phương án phổ dùng interval residual, independent tail và Bellman bound. Không thay plant để vừa cap50.000. D lưu theo queue; screen88rows ởdt1/120 và1/240, không lưu margin/Lstar/contrasts, không reserve p_sw. Negative controlsN01/N02 SD,N03/N04 conservation có kỳ vọng sáu contrasts0 theo chứng chỉ, chưa chạy contrasts.

Sáu consistency checks:4 PASS,1 PARTIAL (full Final Review source chưa có),1 FAIL (grid/calibration prerequisite không đạt; numerical cross-constraints PASS). [Receipt](../../results/lessons/v1_1_a6/readiness.json), [báo cáo PhầnA](../verification/v1_1_part_a/README.md), [grid decision record](../design/grid_v1_1.md). Full suite và mutation evidence xem báo cáo; code PASS không đổi kết luận B4.

Bốn human gates được tác giả xác nhận trong chat23/10 sau record thiếu xác nhận trước đây; không tạo ảnh, biên bản hoặc commit kín sách thay tác giả. PHASE_1 source chỉ có digest rút gọn47f9a335…d4d7ba và dòng332/1953 do review báo; tìm385 attachment text (original/LF) không tìm hash đầy đủ. Không tự điền full SHA hoặc quote chưa mở. Câu ngoại lệ PartE không dùng để bỏ gate.

Tag contract-v1 giữ nguyên6bb631f; CONDITIONAL GO22/10 là lịch sử. Heads-up chưa gửi. G1 giữ nguyên. Bước tiếp theo cần protocol NARROW/REFORMULATE mới, với reason và exposure đã có; không âm thầm bỏ ôout hoặc thử λ lần thứ hai để báo PASS. Chưa có bằng chứng hypothesis/novelty/practical-network value.
