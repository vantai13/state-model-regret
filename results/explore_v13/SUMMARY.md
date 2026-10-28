# v1.3 Population — pilot khả thi (nhánh `explore/v13-population`, 28/10/2026)

Người phụ trách: **Doan Van Tai**. AI (Claude) tự thiết kế và chạy theo ủy quyền trực tiếp. Nhãn
**EXPLORATION**: không phải contract, prereg hay xác nhận. Mọi regime ở đây trở thành dữ liệu đã thấy.
Chỉ dùng regime mới (ID X…); không dùng ô lưới v1.2, ô R hay R09/R10.

## Cách đo

- Mỗi regime gồm λA, λB, κ, η, h (age = 1 s, capacity 10, nền ±6 ON/OFF).
- Observation Y = (y_A, y_B) lấy từ luật dừng trước quyết định, độc lập theo queue. Quadrature:
  giữ chính xác nguyên tử q = 0, phần còn lại chia K = 40 khoảng.
- Với mỗi y: bốn pipeline S0/S1 × M0/M1 như v1.2, rồi lấy trung bình trên p(y) để ra Ḡ.
- Kiểm cỗ máy: so với engine `evaluate_sides` trên 8 cặp y, sai khác bằng 0, action trùng.
  Test: 19 test ledger (brute-force, có c_sw).
- Độ bền trên 9 regime then chốt: K = 40/80 và dt 1/120 / 1/240 s, mọi đại lượng đổi ≤ khoảng 0,15 điểm %.

## Kết quả (216 regime)

| Đợt | n | Ḡ_M ≥ 1% C̄ | Ḡ_M ≥ 10% S̄ | Ḡ_S ≥ +1% | Ḡ_S ≤ −1% | \|Γ̄\| ≥ 1% | Γ̄ ≤ −0,05% | G_SM ≥ 1% | max Ḡ_M | min Ḡ_S |
|---|---|---|---|---|---|---|---|---|---|---|
| 1: λA × κ{0,3; 1; 3} × η × h{2, 8}, λB = 8 | 60 | 0 | 0 | 6 | 6 | 6 | 0 | 9 | 0,85% | −8,3% |
| 2: λA{7; 7,5; 8} × λB{6; 7; 8} × κ{0,1; 0,3} × η × h{8; 12; 16} | 108 | **20** | **11** | 3 | **73** | 75 | 0 | 26 | **13,4%** | **−21,6%** |
| 3: như đợt 1 (h = 8) cộng c_sw ∈ {1, 4} | 48 | 0 | 0 | 3 | 1 | 1 | 4 | 7 | 0,65% | −1,5% |

**Vùng có giá trị model repair:**
- Điều kiện: κ = 0,1–0,3, λB = 8 (B gần bão hòa sau khi chuyển), λA = 7–7,5, h = 8–16 s.
- Ví dụ X2065: Ḡ_M = 13,4% C̄_ref (42% stakes), P(flip) = 0,47, P(xếp hạng sai) = 0,54.
- Khi B còn nhiều chỗ trống (λB = 6–7), quyết định gần như cố định: Ḡ_M ≈ 0, G_SM ≈ 0.

**Đưa state tươi cho M0 gây hại:**
- Ḡ_S ≤ −1% ở 79/216 regime, tới −21,6% C̄_ref, kèm Γ̄ lớn tương ứng (tới +21,6%).
- Dấu của Γ̄ gần như không đổi (≥ 0). Phần âm thật chỉ khoảng −0,1% và chỉ xuất hiện khi có c_sw.

**Luật dự báo chỉ dùng M0** (không cần model thật):
- Độ cân bằng Stay/Switch của M0 trên p(y) xếp hạng 168 regime theo Ḡ_M/S̄ với Spearman +0,75.
- Đây là 1 trong 5 chỉ số được thử, chọn sau khi đã thấy dữ liệu, nên chưa phải kết quả xác nhận.
- Bốn chỉ số còn lại: −0,19 đến +0,13.

## Đánh giá: TỐT (mức pilot, có điều kiện)

- **Đạt:** Ḡ_M ≥ 1% C̄_ref ở vùng xác định được; hiệu ứng 2×2 lớn (Ḡ_S, Γ̄, G_SM tới 13–22%);
  bền theo K và dt; có một luật chỉ dùng M0 đạt Spearman ≥ 0,7.
- **Chưa đạt để lên "rất tốt":**
  - dấu của Γ̄ không đổi;
  - Ḡ_S dương ≥ 1% hiếm;
  - luật dự báo được chọn hậu nghiệm;
  - vùng thú vị cần κ ngắn (mode nhớ 0,1–0,3 s so với tuổi 1 s), B gần bão hòa và h dài,
    nên tính thực tế phải kiểm ở Phase 8.

**Hướng nên theo:** v1.3 population, quanh hai claim có thể kiểm ngoài mẫu:
1. Model repair có giá trị khi tải chuyển sang đẩy đường thay thế vào vùng tải cao và horizon đủ dài,
   và luật chỉ-M0 dự báo được vùng đó.
2. State tươi cộng mean-field twin gây hại; hai repair bổ trợ nhau.

Cả hai cần prereg và mẫu regime mới. Regime trong pilot này chỉ là discovery.
