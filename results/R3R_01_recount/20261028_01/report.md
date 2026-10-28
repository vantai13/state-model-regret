# R3R_01 — Đếm lại pilot v1.3 từ raw

Sinh tự động bởi `experiments/R3R_01_recount/recount.py`. **Không sửa tay file này.** Nhãn: VERIFICATION trên dữ liệu DISCOVERY đã lộ; không phải evidence cho RQ.

- Rev: `explore-v13-pilot` → commit `a7435e9a3cb0d1625479c942041ec6748444014a`
- `results/explore_v13/stage1/regimes.csv` blob `a899dd993c79`
- `results/explore_v13/stage2/regimes.csv` blob `2411fb274356`
- `results/explore_v13/stage3/regimes.csv` blob `98caa04bcc10`
- `results/explore_v13/robustK/regimes.csv` blob `bf78b3dbbee9`
- `results/explore_v13/robustdt/regimes.csv` blob `7e76639be2c1`
- `results/explore_v13/SUMMARY.md` blob `cb279fb5b17e`
- `notes/design/grid_v1_2.json` blob `30f9f4a976e0`

## 0. Invariant của dữ liệu

PASS: 216 ID chính, ID không trùng (kể cả robust), đủ cột.

Regime phân biệt (cùng λA, λB, κ, η, h, c_sw, ref, K): **210** trên 216 ID. Nhóm trùng: 6.
- X1025 = X2030: chênh lớn nhất trên mọi cột số = 0.0e+00
- X1027 = X2033: chênh lớn nhất trên mọi cột số = 0.0e+00
- X1037 = X2066: chênh lớn nhất trên mọi cột số = 0.0e+00
- X1039 = X2069: chênh lớn nhất trên mọi cột số = 0.0e+00
- X1049 = X2102: chênh lớn nhất trên mọi cột số = 0.0e+00
- X1051 = X2105: chênh lớn nhất trên mọi cột số = 0.0e+00

Trong từng Stage không có trùng; trùng chỉ xuất hiện khi gộp các Stage. Kết quả của các ID trùng giống hệt nhau là một kiểm tính tất định (cùng input → cùng output), không phải hai quan sát độc lập.

## 1. Bảng SUMMARY so với raw (theo Stage)

| Cột | stage1 raw | stage1 SUMMARY | stage2 raw | stage2 SUMMARY | stage3 raw | stage3 SUMMARY |
|---|---|---|---|---|---|---|
| n | 60 | 60 | 108 | 108 | 48 | 48 |
| Ḡ_M ≥ 1% C̄ | 0 | 0 | 20 | 20 | 0 | 0 |
| Ḡ_M ≥ 10% S̄ | 0 | 0 | 11 | 11 | 0 | 0 |
| Ḡ_S ≥ +1% | 6 | 6 | 3 | 3 | 3 | 3 |
| Ḡ_S ≤ −1% | 6 | 6 | 73 | 73 | 1 | 1 |
| \|Γ̄\| ≥ 1% | 6 | 6 | 75 | 75 | 1 | 1 |
| Γ̄ ≤ −0,05% | 0 | 0 | 0 | 0 | 4 | 4 |
| G_SM ≥ 1% | 9 | 9 | 26 | 26 | 7 | 7 |
| max Ḡ_M (%C̄) | 0.852 | 0,85 | 13.407 | 13,4 | 0.649 | 0,65 |
| min Ḡ_S (%C̄) | -8.258 | −8,3 | -21.570 | −21,6 | -1.455 | −1,5 |

So khớp: số đếm phải bằng đúng; số thập phân so sau khi làm tròn đến số chữ số SUMMARY hiển thị.

## 2. Các câu trong phần chữ của SUMMARY

| Câu trong SUMMARY | Raw | Khớp? |
|---|---|---|
| Ḡ_S ≤ −1% ở 79/216 regime | 80/216 | **không** |
| (Stage 1+2) — không có trong SUMMARY | 79/168 | — |
| (theo regime phân biệt) — không có trong SUMMARY | 78/210 (Stage 1+2: 77/162) | — |
| X2065: Ḡ_M = 13,4% C̄_ref | 13.407 | có |
| X2065: 42% stakes | 42.348 | có |
| X2065: P(flip) = 0,47 | 0.4675 | có |
| X2065: P(xếp hạng sai) = 0,54 | 0.5364 | có |
| Γ̄ tới +21,6% | 21.570 | có |
| Γ̄ âm chỉ khoảng −0,1% và chỉ khi có c_sw | min Γ̄ = -0.137%; số regime c_sw = 0 có Γ̄ ≤ −0,05%: 0 | có |

## 3. Độ bền (robustness) — so với regime Stage 2 cùng tọa độ

| Phép làm mịn / thang | Số cặp | Max \|chênh\| (điểm %) | Ở đâu |
|---|---|---|---|
| robustK/pctC | 9 | 0.1528 | XRK5 vs X2035, Gamma_pctC: 6.186 → 6.033 |
| robustK/pctS | 9 | 0.6299 | XRK2 vs X2063, G_SM_pctS: 34.475 → 33.845 |
| robustdt/pctC | 9 | 0.1933 | XRD4 vs X2029, G_S_pctC: -21.570 → -21.763 |
| robustdt/pctS | 9 | 0.4283 | XRD5 vs X2035, G_M_pctS: 11.068 → 11.496 |

SUMMARY ghi "≤ khoảng 0,15 điểm %". Raw (thang % C̄): max 0.1933 điểm % → **không khớp**. Dung sai làm mịn của v1.2 (D1) là 0.25 điểm % C_ref. Chỉ 9 regime được kiểm; các regime khác chưa có kiểm tương ứng.

## 4. Thiết kế quét (tham số thật trong raw)

| Stage | λA | λB | κ | η (nhãn) | h | c_sw | ref | K |
|---|---|---|---|---|---|---|---|---|
| stage1 | 6, 13/2, 7, 15/2, 8 | 8 | 3/10, 1, 3 | 1/2, 3/4 | 2, 8 | 0 | 1 | 40 |
| stage2 | 7, 15/2, 8 | 6, 7, 8 | 1/10, 3/10 | 1/2, 3/4 | 8, 12, 16 | 0 | 1 | 40 |
| stage3 | 13/2, 7, 15/2, 8 | 8 | 3/10, 1, 3 | 1/2, 3/4 | 8 | 1, 4 | 1 | 40 |
| robustK | 7, 15/2 | 6, 8 | 1/10, 3/10 | 1/2, 3/4 | 8, 12, 16 | 0 | 1 | 80 |
| robustdt | 7, 15/2 | 6, 8 | 1/10, 3/10 | 1/2, 3/4 | 8, 12, 16 | 0 | 2 | 40 |

Điểm (λA, κ, η) của Stage 1 có h = 8 nhưng **không** có trong Stage 3: 6 — [('6', '1', '1/2'), ('6', '1', '3/4'), ('6', '3', '1/2'), ('6', '3', '3/4'), ('6', '3/10', '1/2'), ('6', '3/10', '3/4')]. Điểm Stage 3 không có trong Stage 1 h = 8: [].

Stage 3 có 24 tọa độ plant (mỗi tọa độ × 2 mức c_sw). Tọa độ trùng regime c_sw = 0: Stage 1 = 24 (max Ḡ_M của các regime gốc = 0.852% C̄), Stage 2 = 6 (max Ḡ_M = 0.852% C̄).

ref 1 = dt 1/120 s; ref 2 = dt 1/240 s (dt đã khóa ở Phase 3, DL-053). CSV không có cột c_sw (gán 0 theo mặc định của scan.py): stage1, stage2.

## 5. Nhãn η: u = 2η (câu chữ v1.2 D5) so với u/(μ − λB)

| λB | η (nhãn) | u = 2η | u/(μ − λB) |
|---|---|---|---|
| 6 | 1/2 | 1 | 1/4 |
| 6 | 3/4 | 3/2 | 3/8 |
| 7 | 1/2 | 1 | 1/3 |
| 7 | 3/4 | 3/2 | 1/2 |
| 8 | 1/2 | 1 | 1/2 |
| 8 | 3/4 | 3/2 | 3/4 |

v1.2 cố định λB = 8 (D4), nên hai cách đọc trùng nhau trong v1.2. Pilot cho λB thay đổi, nên chúng tách ra.

## 6. Trùng tọa độ với lưới v1.2 (38 main + 12 held-out)

So (λA, λB, κ, u, h) với 43 bộ tọa độ v1.2 (chỉ tham số, λB = 8 theo D4). Số regime pilot trùng đúng tọa độ plant: **45**, chạm 23 ô v1.2; trong đó 21 regime có c_sw = 0 như v1.2 (D13) và 24 regime Stage 3 có c_sw ≠ 0 (cùng plant, khác hàm cost).

- X1002 (c_sw = 0) ↔ M33 tại ['6', '8', '3/10', '3/2', '2']
- X1007 (c_sw = 0) ↔ M11 tại ['6', '8', '1', '3/2', '8']
- X1009 (c_sw = 0) ↔ M17 tại ['6', '8', '3', '1', '8']
- X1014 (c_sw = 0) ↔ M37 tại ['13/2', '8', '3/10', '3/2', '2']
- X1017 (c_sw = 0) ↔ R05 tại ['13/2', '8', '1', '1', '8']
- X1019 (c_sw = 0) ↔ M12, M15 tại ['13/2', '8', '1', '3/2', '8']
- X1023 (c_sw = 0) ↔ M21 tại ['13/2', '8', '3', '3/2', '8']
- X1027 (c_sw = 0) ↔ M03, M07 tại ['7', '8', '3/10', '3/2', '8']
- X1029 (c_sw = 0) ↔ M10, M13, M23 tại ['7', '8', '1', '1', '8']
- X1031 (c_sw = 0) ↔ M16 tại ['7', '8', '1', '3/2', '8']
- X1033 (c_sw = 0) ↔ M19 tại ['7', '8', '3', '1', '8']
- X1036 (c_sw = 0) ↔ M36 tại ['15/2', '8', '3/10', '1', '2']
- X1037 (c_sw = 0) ↔ M02 tại ['15/2', '8', '3/10', '1', '8']
- X1039 (c_sw = 0) ↔ M08 tại ['15/2', '8', '3/10', '3/2', '8']
- X1041 (c_sw = 0) ↔ M14 tại ['15/2', '8', '1', '1', '8']
- X1053 (c_sw = 0) ↔ M24, M27 tại ['8', '8', '1', '1', '8']
- X1055 (c_sw = 0) ↔ M30 tại ['8', '8', '1', '3/2', '8']
- X2033 (c_sw = 0) ↔ M03, M07 tại ['7', '8', '3/10', '3/2', '8']
- X2066 (c_sw = 0) ↔ M02 tại ['15/2', '8', '3/10', '1', '8']
- X2067 (c_sw = 0) ↔ R11 tại ['15/2', '8', '3/10', '1', '12']
- X2069 (c_sw = 0) ↔ M08 tại ['15/2', '8', '3/10', '3/2', '8']
- X3004 (c_sw = 1) ↔ R05 tại ['13/2', '8', '1', '1', '8']
- X3005 (c_sw = 4) ↔ R05 tại ['13/2', '8', '1', '1', '8']
- X3006 (c_sw = 1) ↔ M12, M15 tại ['13/2', '8', '1', '3/2', '8']
- X3007 (c_sw = 4) ↔ M12, M15 tại ['13/2', '8', '1', '3/2', '8']
- X3010 (c_sw = 1) ↔ M21 tại ['13/2', '8', '3', '3/2', '8']
- X3011 (c_sw = 4) ↔ M21 tại ['13/2', '8', '3', '3/2', '8']
- X3014 (c_sw = 1) ↔ M03, M07 tại ['7', '8', '3/10', '3/2', '8']
- X3015 (c_sw = 4) ↔ M03, M07 tại ['7', '8', '3/10', '3/2', '8']
- X3016 (c_sw = 1) ↔ M10, M13, M23 tại ['7', '8', '1', '1', '8']
- X3017 (c_sw = 4) ↔ M10, M13, M23 tại ['7', '8', '1', '1', '8']
- X3018 (c_sw = 1) ↔ M16 tại ['7', '8', '1', '3/2', '8']
- X3019 (c_sw = 4) ↔ M16 tại ['7', '8', '1', '3/2', '8']
- X3020 (c_sw = 1) ↔ M19 tại ['7', '8', '3', '1', '8']
- X3021 (c_sw = 4) ↔ M19 tại ['7', '8', '3', '1', '8']
- X3024 (c_sw = 1) ↔ M02 tại ['15/2', '8', '3/10', '1', '8']
- X3025 (c_sw = 4) ↔ M02 tại ['15/2', '8', '3/10', '1', '8']
- X3026 (c_sw = 1) ↔ M08 tại ['15/2', '8', '3/10', '3/2', '8']
- X3027 (c_sw = 4) ↔ M08 tại ['15/2', '8', '3/10', '3/2', '8']
- X3028 (c_sw = 1) ↔ M14 tại ['15/2', '8', '1', '1', '8']
- X3029 (c_sw = 4) ↔ M14 tại ['15/2', '8', '1', '1', '8']
- X3040 (c_sw = 1) ↔ M24, M27 tại ['8', '8', '1', '1', '8']
- X3041 (c_sw = 4) ↔ M24, M27 tại ['8', '8', '1', '1', '8']
- X3042 (c_sw = 1) ↔ M30 tại ['8', '8', '1', '3/2', '8']
- X3043 (c_sw = 4) ↔ M30 tại ['8', '8', '1', '3/2', '8']

- Ô niêm phong R09 (κ = 3/5, h = 4): regime pilot cùng κ = 0, cùng h = 0, cùng cả hai = 0 (chỉ so tham số).
- Ô niêm phong R10 (κ = 3/5, h = 4): regime pilot cùng κ = 0, cùng h = 0, cùng cả hai = 0 (chỉ so tham số).

Lưu ý: trùng tọa độ plant không có nghĩa trùng estimand (v1.2 cố định một snapshot; pilot lấy trung bình theo p(y)). Khoảng cách "gần" để tránh pseudo-replication là việc của L3R.7.

## 7. Identity trên raw (sanity, không phải bằng chứng engine đúng)

- min_G_M = 0.000e+00
- min_G_SM = -1.776e-15
- min_G_S_M1 = -1.776e-15
- min_G_M_S1 = 1.805e-07
- max_abs_gamma_identity_1 = 0.000e+00
- max_abs_gamma_identity_2 = 0.000e+00
- max_abs_GM_identity_gap = 5.178e-13

## 8. Bảng đã xem trong L3R.1 Part 1 (Stage 1+2, c_sw = 0) — tái lập để có nguồn

Cột "theo ID" là cách Part 1 đã đếm; cột "phân biệt" bỏ 6 ID trùng (mục 0).

| Đại lượng | Theo ID | Phân biệt |
|---|---|---|
| n | 168 | 162 |
| harm (Ḡ_S ≤ −1% C̄) | 79 | 77 |
| harm theo λB | {'6': 36, '7': 21, '8': 22} | {'6': 36, '7': 21, '8': 20} |
| Ḡ_M ≥ 1% C̄ theo λB | {'6': 0, '7': 0, '8': 20} | {'6': 0, '7': 0, '8': 20} |
| cả harm và Ḡ_M ≥ 1% | 14 | 14 |
| harm có \|Ḡ_M\|, \|Ḡ_SM\| < 0.05% C̄ | 50 | 50 |
| … độ nhạy theo ngưỡng (% C̄) | {'0.05': 50, '0.1': 54, '0.25': 57, '0.5': 59} | {'0.05': 50, '0.1': 54, '0.25': 57, '0.5': 59} |
| \|Γ̄\| ≥ 1% (trong đó Ḡ_S < 0) | 81 (81) | 79 (79) |
| Ḡ_S ≥ 0 (trong đó Γ̄ ≥ 1%) | 77 (0) | 73 (0) |
| Ḡ_S\|M1 ≥ 1% / ≥ 0,1% | 11 / 93 | 10 / 87 |
| Ḡ_S\|M1 max / trung vị (% C̄) | 1.753 / 0.1772 | 1.753 / 0.1455 |
| S̄/C̄ min … max (cả pilot) | 0.0042 … 1.491 | 0.0042 … 1.491 |

## 9. Các điều kiện của rubric trong docstring `population.py` (đếm theo ID, không gán nhãn)

- GS_pos_C_or_S = 37
- GM_C_or_S = 20
- Gamma_ge_+0.05 = 163
- Gamma_le_-0.05 = 4
- Gamma_ge_+0.5 = 89
- Gamma_le_-0.5 = 0
- Gamma_ge_+1.0 = 82
- Gamma_le_-1.0 = 0
- min_Gamma_pctC = -0.137
- min_Gamma_pctC_csw0 = -0.000

Script không kết luận rubric đạt hay không: việc so với câu chữ rubric và gán nhãn là của tác giả.
