# Dự đoán knockout KO (L7.2 Phần 1A, a = 6; khóa trước truth của KO)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền L7.2 Phần 1**, exploration, không phải author-self, không phải claim.
Ghi ngày 03/11/2026, sau review của mentor về hybrid. Bộ chấm: [check_ko.py](../../experiments/explore_ctmc/check_ko.py).
Số zero-fit đóng băng: [PREDICTIONS_ko_numbers.csv](PREDICTIONS_ko_numbers.csv), tính bằng `--mode m0` (M0, π, g,
posterior; không gọi V, không có gap thật).

## Vì sao cần KO

Hybrid (M0 + h·s) trùng với Static ở các dòng harm (khác Static ở 0% state, trung vị), nên việc nó xóa harm chỉ nói lại
tiền đề. KO là phép knockout không tầm thường: lấy model đúng rồi cắt đúng phần dài hạn,
gap_KO(h, x) = Δ(h, x) − h·s. Bảng 2×2 bên trong trục model:

| | không có phần dài hạn | có h·s |
|---|---|---|
| phần ngắn hạn xấp xỉ fluid | M0 | Hybrid |
| phần ngắn hạn đúng | **KO** | M1 (G_S = S ≥ 0) |

Ở h = ∞, KO quyết định theo c + b(x), với b = g_Switch − g_Stay: z_∞^KO = 100·s·(F_old^KO − F_new^KO)/r_min.

## Tập chấm

`ko_asym`: 33 regime asym × 7 horizon của L7.1 (G_S của M0 đã thấy; KO mới). `ko_slice`: 201 regime **mới** (a = 6),
phân tầng x < 0, 0 < x < 1/4, x > 1/4, κ ∈ [0,02; 5], h/T_int ∈ [0,3; 30], không trùng tuple nào đã chạy.
Khoảng h/T_int để chấm onset: (0,3; 1], (1; 2], (2; 4], (4; 7], (7; 15], (15; 40].

## Điều đã thấy trước khi viết (zero-fit, 234 regime)

KO phụ thuộc state rất mạnh ở h = ∞: khác Static ở trung vị 95% số state (M0: 43%). Nhưng z_∞^KO nhỏ: ở 170 regime
có z_∞ < −0,5, chỉ 1,8% có z_∞^KO < −0,1; tỷ lệ z_∞^KO/z_∞ trung vị −0,025. |z_∞^KO| ≥ 0,25 ở 35/234 regime.
Ở h nhỏ, h·s nhỏ nên KO ≈ M1 (G_S ≈ S ≥ 0).

## Dự đoán

| ID | Nhãn | Điều kiện | Dự đoán (ngưỡng) |
|---|---|---|---|
| KO-T1 | toán | dòng có h/T_int ≥ 15 | \|G_S^KO − z_∞^KO\| ≤ 0,1 + 0,1·\|z_∞^KO\| ở mọi dòng |
| KO-R1 | rủi ro (trung tâm) | dòng harm của M0 (G_S < −0,5%) | \|G_S^KO\| < 0,5·\|G_S\| ở ≥ 80% dòng |
| KO-R2 | rủi ro | mọi dòng | G_S^KO ≥ −0,25% ở ≥ 90% dòng |
| KO-R3 | rủi ro (h ngắn) | dòng h/T_int ≤ 1 | G_S^KO ≥ −0,1% ở ≥ 90% dòng |
| KO-R4a | onset | dòng h/T_int ∈ (2; 4] | \|G_S^KO − z_bậc_một^KO\| ≤ 0,1 pp ở ≥ 50% |
| KO-R4b | onset | (4; 7] | như trên, ở ≥ 90% |
| KO-R4c | onset | (7; 15] | như trên, ở ≥ 90% |
| KO-R4d | onset | (15; 40] | như trên, ở ≥ 95% |
| KO-R5 | rủi ro (không tầm thường) | dòng h/T_int ≥ 4 | KO trên state mới khác Static ở ≥ 50% state, ở ≥ 90% dòng |
| KO-R6 | rủi ro (dấu) | dòng h/T_int ≥ 7, \|z_∞^KO\| ≥ 0,25 | dấu G_S^KO = dấu z_∞^KO ở ≥ 90% dòng |

**Ghi kèm (mô tả):** bảng 2×2 G_S (trung vị) của M0, Hybrid, KO, M1 theo lớp x và khoảng h/T_int; độ phụ thuộc state
của mọi twin trên state cũ, state mới và backlog-only.

## Ý nghĩa từng kết cục

- KO-R1 và KO-R2 đạt → mù horizon một mình (phần ngắn hạn đúng) **không** tạo harm từ state tươi; harm cần cả cấu trúc
  ngắn hạn kiểu fluid của M0 cùng với mù horizon (tương tác bên trong trục model). Cách kể "M0 mù horizon tự tạo phụ
  thuộc state" phải nói rõ là phụ thuộc state *có hướng*, không phải mọi phụ thuộc state.
- KO-R1 trượt (|G_S^KO| ≈ |G_S|) → mù horizon một mình đã đủ gây harm; xấp xỉ fluid không phải nguyên nhân.
- KO-R5 trượt → phép knockout tầm thường như hybrid; không đọc được nhân quả.
- KO-R4 trượt ở (4; 7] → onset của KO muộn hơn của M0.
