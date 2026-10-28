# v1.3 bước 1 — kết quả kiểm hình học chế độ sai số (DISCOVERY)

Người phụ trách: **Doan Van Tai** · 28/10/2026 · DL-062 (khai trước), DL-063 (kết quả).
AI (Claude) viết dự đoán, chạy và báo cáo theo ủy quyền trực tiếp của tác giả. Không human review.
38 ô main đã lộ ở A04, ref 2, dt 1/240 s. Không dùng ô R, không chạm R09/R10.

## Kết quả

| Dự đoán (commit `81b1c3f`, trước run) | Verdict | Số đo |
|---|---|---|
| P(a) Mù do cả hai đường fluid không chạm rỗng | **PASS** | 4/4 ô mù: 100% support cả A và B chứng nhận không idle; 34/34 ô còn lại có I_A + I_B > 0 |
| P(b) Đảo dấu khi M0 chỉ thấy một phía | **FAIL** | Tập "đoán đảo" rỗng; M01, M03 có I_A = I_B = 1,00 (hai phía đều chạm rỗng) |
| P(c) Lens tại biên bám G_M\|S1 tốt hơn lens bias trung bình | **FAIL** | Spearman lens biên = 0,163 (cần ≥ 0,6); lens trung bình = −0,701. Độ nhạy ε 0,05/0,2: 0,133/0,261 |

**Validity: PASS.**
- G_M|S1 tính lại từ bảng `Side` khớp A04 ở 38/38 ô.
- Khối lượng chưa phân giải bằng 0.
- Thời gian chạy: 14 giây.
- Test: 410 passed trước run (19 test mới).

## Đọc từng dự đoán

- **P(a).** Ở M19–M22, đường trung bình của cả hai queue không bao giờ rỗng trong h, nên M0 thấy
  hai action bằng nhau và luật hòa chọn Stay. Gap thật không bằng 0: đường ngẫu nhiên vẫn idle
  ở mọi state (J_A = J_B = 1). Điều này giải thích G_M > 0 ở M20, M22 (target 0,7) và R04 bị bác.
  Gần như đồng nhất thức (bảo toàn công việc), nhưng đã loại khả năng hai phía triệt tiêu nhau.
- **P(b).** Giả thuyết "fluid chỉ thấy một phía" của review **bị bác** trên dữ liệu discovery.
  Ở M01 và M03, M0 thấy cả hai phía nhưng phóng đại không đều:
  - M01: phía A gấp 1,229 lần, phía B gấp 1,346 lần;
  - M03: phía A gấp 1,217 lần, phía B gấp 1,372 lần.

  Gap thật là hiệu nhỏ của hai số lớn (M01: 23,55 − 22,87 = +0,68), nên chênh lệch phóng đại đủ
  lật dấu. Chỉ một ô (M28, target 0,7) là một-phía, và ô đó không đảo.
- **P(c).** Lens tại biên không bám được thiệt hại khi state đúng. Lens bias trung bình bám
  **ngược** (−0,70): bias trung bình lớn đi kèm thiệt hại nhỏ, đúng kiểu phóng đại tỉ lệ với Δ.

## Phân tích post-hoc (sau khi thấy kết quả; không phải dự đoán, không phải bằng chứng)

1. **Đảo dấu xảy ra ở biên tương đối nhỏ nhất.** Đặt m_rel = |EΔ| / (Eδ_A + |Eδ_B|). Hai ô đảo
   có m_rel nhỏ nhất trong 34 ô không mù (0,0146 và 0,0150); ô cùng dấu nhỏ nhất là M02 (0,0398).
   Ở ô Stay đúng, điều kiện đảo là m_rel < (k_B − k_A)/(k_B + k_A). Đây là đẳng thức đại số;
   phần thực nghiệm là k_B > k_A (trung vị trên ô cùng dấu: k_A 1,02, k_B 1,19).
2. **Thiệt hại khi state đúng đến từ sai số lớn ở state xa biên.** Tỉ số lens biên / thật có trung
   vị 0,76 nhưng trải từ 0,007 đến 9,5. Các ô hụt nặng nhất (M28, M30, M18, M17) cũng là các ô lens
   trung bình hụt hàng chục lần. Sai số của M0 không nhỏ so với margin của state, nên lý thuyết nhiễu
   nhỏ quanh biên (null mật độ-tại-biên của review) không đủ.

Cả hai điểm chỉ là ứng viên. Muốn dùng phải prereg và kiểm trên mẫu regime mới.

## Hàm ý theo bảng khai trước

P(b) và P(c) cùng FAIL. Theo bảng trong `predictions.md`, hướng tương ứng là **fallback**:
population characterization (câu chuyện 2 của review) hoặc NARROW.

**Không nên** đặt v1.3 quanh hai giả thuyết đã trượt:
- phân loại chế độ từ "fluid một phía";
- estimand "fidelity tại biên".

Bước này **không** kiểm bản v1.3 population như bản nháp hiện có; bản đó vẫn mở.

**Quyết định bước 2 là của tác giả.**

## Giới hạn

- Dữ liệu discovery đã lộ; nhãn ô đã biết trước khi viết dự đoán.
- Chỉ 2 ô đảo dấu trong main.
- Plant lý tưởng, D13, thiết kế neo.
- Ngưỡng 0,05/0,20 và ε = 0,1·stakes do AI chọn trước run, không qua người đọc.

[cells.csv](20261028_01/cells.csv) · [summary.json](20261028_01/summary.json) ·
[manifest](20261028_01/manifest.json) · [predictions](../../experiments/V13_step1/predictions.md) ·
[tiếp nhận review](../reviews/phase3_20261028/intake.md).
