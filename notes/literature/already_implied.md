# Sáu contrast — phần đã có cơ sở và phần còn phải tìm

Người phụ trách: **Doan Van Tai** · 24/10/2026 · AI đề xuất; source notes AI-only.
Điều kiện G1–G5 và proof ở [T03 v2](../theory/T03_primary_reading_start.md).

| Contrast | Khái niệm/identity | Điều kiện | Nguồn, mức đọc | Trạng thái |
|---|---|---|---|---|
| GSgivenM1 | EVPPI của current state conditional on y | G1–G4, đúng argmin và khả tích | SOB14 Method Eq4, AI T; T01/T03 | Có tên; ≥0 là hệ quả; >0 cần hai dấu gap strict có mass |
| GMgivenS1 | E_D[VSS(x)] theo conditional mean-future problem | G2–G5, cùng cost/action set | T03 proof; B82 abstract A, không mượn bounds | Có tên theo định nghĩa; original full reading chưa đủ |
| GM | Gain khi giữ belief state, thay mean rollout theo state bằng đúng expectation | G1/G3/G4 bảo đảm không âm | D10/D19; T01/T03, E0 | Không tự global VSS hoặc EVMI; tên literature còn phải tìm ở L2.8 |
| GS | Giá trị sửa state với fixed approximate M0 | D20/D21, cùng D | T03/V1; exact toy E1 | Có thể âm; không áp VOI≥0 của Bayes đúng-model |
| GSM=R00 | Headroom so với ô00 | Ô11 đúng oracle, cùng D/objective/actions | D15/D18/D19 | Bookkeeping, cận chung; chưa là practical feasible gain |
| Gamma | GSgivenM1−GS = GMgivenS1−GM | D19 | Đại số; exact toy verification | Hai dấu không tự là mechanism; related conditional VOI cần L2.8 |

P11 §2.4 Eq2.7: EVPI(delta) là VOI theo belief, diễn giải upper bound cho EVMI;
GM và GMgivenS1 không tự là đại lượng đó. “Input information so với model
improvement” không được claim mới. Đúng theta không loại hidden x ở S0.

Các bounds cần phân biệt: fixed-M0 oracle-state gain không luôn là cận cho
feasible state repair. Với fixed information/matched belief, M1 tối ưu expected
true cost, nên GM (hoặc GMgivenS1) là cận model repair cùng thông tin. R00 là cận
chung từ ô00, không phải cận duy nhất. Không mở rộng sang model/belief sai.

Không dùng p_sw band/candidate để chứng nhận strict gain; không gọi toy là
Phase3 discovery; không gọi EVIU đã kiểm original source. L2.8 chưa chạy.
