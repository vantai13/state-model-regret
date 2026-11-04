# Dự đoán horizon dài trong CTMC (khóa trước mọi regime có h/κ > 160 hoặc h/T_int ≥ 10)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền L7.1**, exploration, không phải author-self, không phải claim.
Ghi ngày 03/11/2026. Bộ chấm: [check_asymptote.py](../../experiments/explore_ctmc/check_asymptote.py). Số zero-fit
đóng băng cho từng (regime, h): [PREDICTIONS_asymptote_numbers.csv](PREDICTIONS_asymptote_numbers.csv), tính bằng
`--mode m0` (chỉ M0, π, r, s, g, T_int; không gọi V, không có gap thật).

## Exposure phải khai

Lệnh đo thời gian đã in truth của regime T3 = (7, 13/2, 5/2, 2): ở h = 2000 (h/T_int ≈ 5,4) z = −4,418%, khai triển
bậc một (quyết định M0 ở h = ∞) cho −4,405%, z_∞ = −5,351%. Tức là mình đã thấy **một** điểm cho thấy khai triển
bậc một chính xác cỡ 0,01 pp ở h/T_int ≈ 5. Ngưỡng của AS-R1 đặt sau khi thấy điểm đó. T3 không nằm trong tập chấm.

## Luật và dạng dự đoán

Với chain đã cắt, V_a(h) = h·r_a + g_a − e^{Q_a h} g_a. Đặt b(x) = Σ_path (g_Switch − g_Stay)(x) + c. Khi quyết định của M0
đã ổn định theo h (M0 mù horizon), và phần e^{Qh}g đã tắt:

- G_S(h) ≈ h·s·(F_old − F_new) + B, với B = E[a00·b] − E[a10·b];
- C_ref(h) ≈ h·r_min + β_C, với β_C = E[b] nếu s < 0, 0 nếu s > 0;
- z(h) = 100·G_S/C_ref ≈ z_pred1(h) → z_∞ = 100·s·(F_old − F_new)/r_min, sai số còn lại cỡ 1/h.

z_pred1 dùng F và B của M0 tại đúng h (cột `z_pred_first_order` trong CSV). M_pred = 100·|s|·P(a_M0 ≠ a_∞)/r_min
trên state mới (tương tự predictor H-L2 của fluid). Không có tham số nào fit từ kết quả.

## Tập chấm

`asym`: 33 regime (u=1, λA=7, x ∈ {−1, −1/2, 1/4, 1/2, 1}; u=1/2, λA=9, x ∈ {−2, −1, 1/2}; u=2, λA=13/2,
x ∈ {−1/4, 1/4, 1/2}; κ ∈ {1/20, 1/2, 2}) × 7 horizon: h/T_int ∈ {1/3, 1, 3, 10, 30} (T_int lớn nhất trong 4 chain,
h làm tròn 3 chữ số) và h/κ ∈ {160, 1000}. AS-R3 dùng thêm các dòng của xslice, pslice. P = (h/κ)·|δ|.

## Dự đoán

| ID | Nhãn | Điều kiện | Dự đoán (ngưỡng) |
|---|---|---|---|
| AS-T1 | toán | dòng h lớn nhất của mỗi regime (h/T_int ≈ 30 hoặc h/κ = 1000) | \|z − z_∞\| ≤ 0,1 + 0,1·\|z_∞\| (pp) ở mọi regime |
| AS-R1a | rủi ro (onset) | dòng h/T_int ≥ 3 | \|z − z_pred1\| ≤ 0,1 pp ở ≥ 90% dòng |
| AS-R1b | rủi ro (onset) | dòng 1 ≤ h/T_int < 3 | \|z − z_pred1\| ≤ 0,1 + 0,1·\|z\| ở ≥ 70% dòng |
| AS-T2 | toán | dòng h/T_int ≥ 10 | S ≤ 0,5% ở ≥ 90% dòng |
| AS-T3 | toán | dòng h/T_int ≥ 10 | regret Static ≤ 0,5% ở ≥ 90% dòng |
| AS-R2a | rủi ro (H-L2) | dòng h/T_int ≥ 10, M_pred ≥ 1% | \|M − M_pred\| ≤ 0,15·M_pred ở ≥ 90% dòng |
| AS-R2b | rủi ro (H-L2) | như trên | M < M_pred ở ≥ 80% dòng (fluid: dự đoán cao hơn truth 10/10) |
| AS-R3 | rủi ro (can thiệp) | dòng asym+xslice+pslice có G_S < −0,5% và P ≥ 10 | G_S^hybrid ≥ −0,1% ở ≥ 90% dòng |
| AS-R4 | rủi ro (đồng hồ) | dòng asym có \|z_∞\| ≥ 0,5 | Spearman(\|z − z_∞\|/\|z_∞\|, h/T_int) ≤ Spearman(cùng sai số, h/κ) − 0,1 |
| AS-R5a | rủi ro (twin) | mỗi regime asym | regret Static < regret M0 (state mới) ở mọi dòng h/T_int ≥ 3, đạt ở ≥ 90% regime |
| AS-R5b | rủi ro (twin) | dòng h/T_int = 1/3 | regret M0 (state mới) < regret Static ở ≥ 50% regime |

AS-T* đạt nghĩa là code và lý thuyết chain-hữu-hạn nhất quán, không phải bằng chứng thực nghiệm. Phần mang thông
tin: onset (AS-R1), độ lớn và chiều sai số của predictor dừng (AS-R2), can thiệp (AS-R3), đồng hồ (AS-R4) và điểm
giao Static–M0 (AS-R5).

## Ý nghĩa từng kết cục

- AS-T1 trượt dù h/T_int ≈ 30 → gần như chắc là bug (hoặc F_old − F_new ≈ 0 làm B quyết định); dừng, kiểm control.
- AS-R1 trượt → khai triển bậc một chưa đủ ở h vài T_int; tìm thang khác (ví dụ thời gian xả của đuôi backlog).
- AS-R2b trượt (M ≥ M_pred) → chiều sai số của predictor dừng khác fluid; ghi lại.
- AS-R3 trượt → phần ngắn hạn của M0 cũng gây harm, không chỉ mù horizon. Bước tiếp: vá phần ngắn hạn.
- AS-R4 trượt → h/T_int không tốt hơn h/κ; đồng hồ cần tìm ở Stage E.
- AS-R5 trượt → điểm giao twin dừng/M0 không nằm trong (1/3, 3)·T_int.
