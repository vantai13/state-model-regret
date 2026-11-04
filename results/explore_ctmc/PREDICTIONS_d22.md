# Dự đoán D22: state mới chỉ có backlog, không có mode (khóa trước khi chạy truth D22)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền** ("thực hiện D22 luôn đi", 03/11/2026). Exploration, không phải
author-self, không phải claim. Viết sau khi đã đọc Stage D–F của L7.1, trước mọi dòng truth D22. Bộ chấm:
[check_d22.py](../../experiments/explore_ctmc/check_d22.py). Số zero-fit đóng băng:
[PREDICTIONS_d22_numbers.csv](PREDICTIONS_d22_numbers.csv), tính bằng `--mode d22m0` (M0, π, luật đồng thời (Y, X);
không gọi V, không có gap thật).

## Định nghĩa (contract v1.3 §3 D22, triển khai trong ctmc-v1)

- a_cb0(Y, Q) = 1[E[Δ̂(X) | Y, Q] < 0]: M0 cố định, Q = hai backlog hiện tại, mode suy từ (Y, Q) bằng posterior đúng.
- a_cb1(Y, Q) = 1[E[Δ(X) | Y, Q] < 0]: cùng thông tin, model đúng.
- F = L00 − L_cb0: giá trị của backlog hiện tại với M0; V = L_cb0 − L10: phần còn lại do mode oracle; G_S = F + V.
- F1 = L01 − L_cb1 và V1 = L_cb1 − L11, S = F1 + V1; F1, V1 ≥ 0 vì model đúng không thể tệ hơn khi có thêm thông tin.
- Zero-fit ở h = ∞: z_F,∞ = 100·s·(F_old − F_cb)/r_min, z_V,∞ = 100·s·(F_cb − F_new)/r_min; z_F,∞ + z_V,∞ = z_∞.

## Phạm vi

Các tuple đã chạy của L7.1 có N ≤ 3.000 mỗi path (giới hạn bộ nhớ của lưới (y, n)): bridge 821/1.200, xslice
86/96, pslice 78/78, asym 29/33, wide 1.753/2.036 (chia thành `d22_wide` 500 case và `d22_wide_rest` 1.253 case,
cùng tập). G_S, S của các tuple này **đã được nhìn** ở Stage D/E; phần mới là phép tách F/V và F1/V1.
Ô (y, n) có khối lượng < 1e−20 bị bỏ; khối lượng bỏ được báo (≤ 1e−12).

## Điều đã thấy trước khi viết (M0-only)

Ngưỡng viết sau khi thấy 1.014 regime asym/xslice/pslice/bridge; kiểm lại trên đủ 2.767 regime trước khi khóa:
z_∞ < −0,5 ở 1.982 regime, z_F,∞ < 0 ở cả 1.982, tỷ lệ z_F,∞/z_∞ trung vị 0,816 (q10 0,571; q90 0,949). Trên 1.014 regime đầu, ở mọi regime có z_∞ < −0,5 (723), z_F,∞ < 0. Phần backlog z_F,∞/z_∞ có trung vị 0,81 (q10 0,55; q90 0,95) và giảm
theo κ: 0,90 (κ ≤ 0,05), 0,88, 0,76, 0,62, 0,32 (κ > 5). Control V3-D22 (Monte Carlo đầu-cuối) đạt, |z| ≤ 2,72; V7-D22 giống từng bit giữa local và GCP.

## Dự đoán

| ID | Nhãn | Điều kiện | Dự đoán (ngưỡng) |
|---|---|---|---|
| D-T1 | toán | mọi dòng | F + V = G_S, F1 + V1 = S sai ≤ 1e−9 pp; F1, V1 ≥ −1e−9; khối lượng bỏ ≤ 1e−12 |
| D-T2 | toán + onset | dòng h/T_int ≥ 10 | \|F − z_F,∞\| và \|V − z_V,∞\| đều ≤ 0,1 + 0,1·\|giá trị zero-fit\| ở ≥ 90% dòng |
| D-R1 | rủi ro (harm không cần mode) | dòng có G_S < −0,5% | F < −0,1% ở ≥ 80% dòng |
| D-R2 | rủi ro (tỷ lệ zero-fit) | dòng harm, h/T_int ≥ 3, \|z_∞\| ≥ 0,5 | \|F/G_S − z_F,∞/z_∞\| ≤ 0,1 ở ≥ 80% dòng |
| D-R3 | rủi ro (horizon ngắn) | dòng harm, h/T_int < 1 | F < 0 ở ≥ 70% dòng |
| D-R4 | rủi ro (model đúng) | dòng có S ≥ 0,5% | F1 ≥ V1 (backlog đáng giá hơn mode) ở ≥ 70% dòng |
| D-R5 | rủi ro (twin khả thi) | dòng h/T_int ≥ 3 | regret Static ≤ regret của M0 với (Y, Q) ở ≥ 90% dòng |

## Ý nghĩa từng kết cục

- D-R1 đạt → harm của state tươi với M0 không chỉ do S1 biết mode: telemetry khả thi (backlog) đã đủ gây harm trong
  ctmc-v1. Trượt → phần lớn harm cần mode oracle; claim "telemetry tươi gây hại" phải thu hẹp về mode.
- D-R2 trượt → tỷ lệ zero-fit chưa đúng ở h vài T_int (phần bị chặn khác giữa F và V).
- D-R4 trượt → với model đúng, thông tin mode quan trọng hơn backlog (dự kiến ở κ lớn).
- D-T1 trượt → bug; dừng.
