# P2-TIER2 — phân tích mô tả hậu kiểm


Người phụ trách: **Doan Van Tai**. Triển khai và phân tích có AI hỗ trợ theo brief P2-TIER2 ngày 19/11/2026. Toàn bộ kết quả dưới đây là **post-hoc, exposed**; không phải kiểm định mới, không đổi verdict hoặc ngưỡng đã khóa. Các ô dùng chung regime, instances, records, tuổi hoặc horizon; mẫu số không phải các phép thử độc lập. Không suy population CI. Quantile dùng nội suy tuyến tính. Regret và GS tính bằng % C_ref; chênh lệch tính bằng percentage points (pp).


## 1. Fig. 4(a) có dấu — GÉANT


**MỚI:** phân phối có dấu và IQR; hai seed 3000001/5000001, 17 regime/seed/h, τ=T_int. Bảng dưới gộp hai seed để mô tả (n=34), không coi là 34 regime độc lập. JSON giữ thêm từng seed và mọi điểm. Stationary dùng argmin rate level-(i) đã lưu và có GS=0 chính xác. ID đối chiếu: G0, F1_R13.


| h/T_int | Pipeline | n | Median | Q25 | Q75 | Âm / 0 / dương | |GS|≤0.1% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | M0 | 34 | 8.42515 | -4.68168 | 42.5245 | 10/0/24 | 1 |
| 1 | Hybrid | 34 | 0 | 0 | 27.9038 | 0/18/16 | 18 |
| 1 | Stationary | 34 | 0 | 0 | 0 | 0/34/0 | 34 |
| 2 | M0 | 34 | -1.8777 | -30.1969 | 38.7106 | 18/0/16 | 0 |
| 2 | Hybrid | 34 | 0 | 0 | 12.6566 | 1/18/15 | 18 |
| 2 | Stationary | 34 | 0 | 0 | 0 | 0/34/0 | 34 |
| 4 | M0 | 34 | -23.8182 | -49.9962 | 35.1619 | 18/0/16 | 0 |
| 4 | Hybrid | 34 | 0 | 0 | 3.22309 | 0/18/16 | 18 |
| 4 | Stationary | 34 | 0 | 0 | 0 | 0/34/0 | 34 |
| 7 | M0 | 34 | -40.5416 | -70.6957 | 33.8772 | 18/0/16 | 0 |
| 7 | Hybrid | 34 | 0 | 0 | 1.01755 | 0/19/15 | 19 |
| 7 | Stationary | 34 | 0 | 0 | 0 | 0/34/0 | 34 |
| 15 | M0 | 34 | -55.2975 | -108.152 | 34.021 | 18/0/16 | 0 |
| 15 | Hybrid | 34 | 0 | 0 | 0.0415552 | 0/25/9 | 29 |
| 15 | Stationary | 34 | 0 | 0 | 0 | 0/34/0 | 34 |
| 30 | M0 | 34 | -61.7903 | -128.733 | 34.2511 | 18/0/16 | 0 |
| 30 | Hybrid | 34 | 0 | 0 | 0 | 0/33/1 | 34 |
| 30 | Stationary | 34 | 0 | 0 | 0 | 0/34/0 | 34 |


Âm/dương là dấu nghiêm ngặt, kể cả sai số rất nhỏ; |GS|≤0.1% chồng lấp với số âm/dương. JSON có phân hoạch không chồng lấp <-0.1 / [-0.1,0.1] / >0.1.


File: `fig4a_signed.json`, `fig4a_signed_candidate.pdf` và `.png`. Hình giữ dấu, không cắt outlier, rộng 227.680 pt đúng MediaBox của hình tham chiếu; không sửa hình paper.


## 2. Fig. 3 có IQR — CTMC


**MỚI:** IQR/median regret và tập full93 đúng brief. Có 93 W1b raw hoàn tất, nhưng F3 trong ledger lọc `baseline_available`, còn 92 regime. File mới cung cấp cả `full93` và `ledger92`; F3/F1_R13 được đối chiếu trên ledger92, không âm thầm đổi số cũ. Regime chỉ thiếu baseline cũ: `Za7p5_u3-2_lA31-4_x1-3_k2`; kết quả age-only W1b của regime này đã lưu đầy đủ. Chọn horizon gần nhất trong abs(log(actual/target))<0.02, không dùng giá trị h làm tròn để lọc các claim C2/C3.


| h/T_int | Pipeline | GS median [Q25,Q75] | Both-side regret median [Q25,Q75] |
| --- | --- | --- | --- |
| 0.333333 | M0 | 0.681967 [0.273487, 1.60419] | 1.16306 [0.497257, 2.82393] |
| 0.333333 | Hybrid | 0.305039 [7.45386e-12, 1.24732] | 1.00406 [0.477063, 2.42635] |
| 0.333333 | Stationary | 0 [0, 0] | 1.00406 [0.477063, 2.47981] |
| 1 | M0 | -0.564986 [-1.98307, 1.68779] | 2.13284 [0.919579, 7.46713] |
| 1 | Hybrid | 0.0946903 [0.0036433, 1.23247] | 0.247313 [0.0209903, 1.60165] |
| 1 | Stationary | 0 [0, 0] | 0.247315 [0.0209903, 1.66201] |
| 3 | M0 | -2.66186 [-4.35855, -0.423275] | 3.65262 [2.73865, 17.0036] |
| 3 | Hybrid | 0.00328206 [1.02352e-05, 0.259987] | 0.006325 [5.32593e-05, 0.335442] |
| 3 | Stationary | 0 [0, 0] | 0.00632756 [5.32594e-05, 0.345492] |
| 10 | M0 | -4.21127 [-6.34228, -2.24094] | 5.54391 [4.5857, 23.151] |
| 10 | Hybrid | 1.32089e-06 [7.64704e-11, 0.00286245] | 1.94937e-06 [1.67758e-10, 0.00332969] |
| 10 | Stationary | 0 [0, 0] | 1.94937e-06 [1.6735e-10, 0.0033752] |
| 30 | M0 | -4.81298 [-7.00587, -2.75898] | 6.53973 [5.34589, 25.1123] |
| 30 | Hybrid | 1.84366e-11 [1.65478e-12, 2.76644e-06] | 2.19811e-11 [1.82564e-12, 3.01747e-06] |
| 30 | Stationary | 0 [0, 0] | 1.39564e-11 [1.69321e-14, 3.0536e-06] |


File: `fig3_iqr.json`, `fig3_iqr_candidate.pdf` và `.png`. ID: C1/F3/F1_R13; full93 là MỚI, không thay figure paper.


## 3. Replay E6 — finite-record rates


Mỗi ô: mean_record(max(regret_fresh,regret_stale)) cho Hybrid; stationary mean_record cùng records. M0 dùng max của hai side means đã lưu E4/E4b. Mỗi h,L có 102 ô = 2 seeds×17 regimes×3 ages, mỗi ô 200 records; M0 lặp theo L vì không dùng rate estimate. **MỚI:** Q25/Q75/Q90 và sign-error breakdown. Median/mean trùng G20_R11/G22_R11 đã kiểm lại. Giữ regret âm đã lưu, không clip.


| L/T_int | h/T_int | Pipeline | Median | Q25 | Q75 | P90 |
| --- | --- | --- | --- | --- | --- | --- |
| 100 | 1 | M0 | 15.4919 | 9.36007 | 47.4871 | 131.325 |
| 100 | 1 | Hybrid | 13.4607 | 7.46633 | 39.9663 | 130.195 |
| 100 | 1 | Stationary | 18.4598 | 7.82037 | 45.4784 | 232.875 |
| 100 | 2 | M0 | 33.3225 | 20.9583 | 50.011 | 78.8393 |
| 100 | 2 | Hybrid | 7.59025 | -1.53448e-14 | 22.2191 | 110.268 |
| 100 | 2 | Stationary | 11.3559 | 0 | 25.0062 | 139.114 |
| 100 | 4 | M0 | 47.8952 | 30.9695 | 84.2109 | 145.504 |
| 100 | 4 | Hybrid | 4.66001 | 3.3372e-14 | 9.60067 | 77.5238 |
| 100 | 4 | Stationary | 6.01868 | 0 | 10.1562 | 78.3702 |
| 100 | 7 | M0 | 60.3792 | 38.8457 | 113.797 | 175.806 |
| 100 | 7 | Hybrid | 4.15939 | 3.86927e-14 | 8.58708 | 45.2471 |
| 100 | 7 | Stationary | 3.92693 | 0 | 9.27656 | 45.0202 |
| 100 | 15 | M0 | 68.3043 | 45.9229 | 136.012 | 252.809 |
| 100 | 15 | Hybrid | 4.50574 | 0 | 9.33788 | 29.3711 |
| 100 | 15 | Stationary | 4.01095 | 0 | 8.74267 | 29.2668 |
| 100 | 30 | M0 | 72.322 | 48.8817 | 158.951 | 322.802 |
| 100 | 30 | Hybrid | 4.65585 | 2.4805e-14 | 9.55219 | 28.2721 |
| 100 | 30 | Stationary | 4.16938 | 0 | 9.21531 | 28.2385 |
| 300 | 1 | M0 | 15.4919 | 9.36007 | 47.4871 | 131.325 |
| 300 | 1 | Hybrid | 13.4827 | 7.40793 | 39.0661 | 80.1138 |
| 300 | 1 | Stationary | 16.1726 | 7.40793 | 46.4621 | 175.943 |
| 300 | 2 | M0 | 33.3225 | 20.9583 | 50.011 | 78.8393 |
| 300 | 2 | Hybrid | 6.09612 | -3.45158e-14 | 19.132 | 51.7665 |
| 300 | 2 | Stationary | 7.02151 | 0 | 22.9336 | 83.8312 |
| 300 | 4 | M0 | 47.8952 | 30.9695 | 84.2109 | 145.504 |
| 300 | 4 | Hybrid | 0.175026 | -1.15368e-14 | 6.33027 | 39.7731 |
| 300 | 4 | Stationary | 0.175026 | 0 | 7.05427 | 50.3515 |
| 300 | 7 | M0 | 60.3792 | 38.8457 | 113.797 | 175.806 |
| 300 | 7 | Hybrid | 0.255961 | 0 | 3.30128 | 27.0241 |
| 300 | 7 | Stationary | 0.356633 | 0 | 3.5998 | 26.426 |
| 300 | 15 | M0 | 68.3043 | 45.9229 | 136.012 | 252.809 |
| 300 | 15 | Hybrid | 0.121552 | -4.05039e-14 | 2.64114 | 13.519 |
| 300 | 15 | Stationary | 0 | 0 | 2.5431 | 13.1076 |
| 300 | 30 | M0 | 72.322 | 48.8817 | 158.951 | 322.802 |
| 300 | 30 | Hybrid | 0.0585557 | 0 | 2.77136 | 12.6728 |
| 300 | 30 | Stationary | 0 | 0 | 2.68316 | 12.3973 |


Đối chiếu P90 đã có trong brief, gộp h∈{15,30} (204 ô/L), **không phải** P90 của mọi record riêng lẻ:


| L/T_int | Pipeline | Median | P90 (% C_ref) |
| --- | --- | --- | --- |
| 100 | M0 | 71.6036 | 261.158 |
| 100 | Hybrid | 4.56097 | 28.7857 |
| 100 | Stationary | 4.13172 | 28.8453 |
| 300 | M0 | 71.6036 | 261.158 |
| 300 | Hybrid | 0.0761088 | 13.0763 |
| 300 | Stationary | 0 | 12.8945 |


Tỷ lệ dấu sai so với sign(rhat_i[Switch]−rhat_i[Stay]) từ training E4 đã lưu, không phải dấu từ một truth run mới:


| L/T_int | Sai / unique records | Tỷ lệ | Số lượt khi lặp hai plant seed |
| --- | --- | --- | --- |
| 100 | 279/3400 | 0.0820588 | 6800 |
| 300 | 98/3400 | 0.0288235 | 6800 |


17/17 regime dùng cùng record_rates ở hai seed: 3400 unique records/L; 6800 là số lượt xuất hiện. File `e6_replay.json` giữ bảng theo regime, record và cell.


## 4. So cặp Hybrid − Stationary theo h


**MỚI:** số tốt hơn/bằng/tệ hơn. Δ<0 nghĩa Hybrid ít regret hơn. Bằng nếu |Δ|≤1e−9 max(|R_H|,|R_S|), không có absolute floor; với GÉANT thêm |Δ|≤2 paired SE. Paired SE lấy từ chênh chi phí trên cùng 500 instances, sau khi chọn side Hybrid có mean cost lớn hơn, rồi chuẩn hóa C_ref. Đây chỉ là độ phân giải mô tả sau chọn worse side, không phải kiểm định. Vì relative tolerance không có floor, chênh cực nhỏ khi một regret gần 0 vẫn có thể phân loại tốt/tệ; xem Δ đầy đủ trong JSON. CTMC/GÉANT trong bảng dùng τ=T_int; E6 dùng cả 3 tuổi như G22_R11. JSON có cả τ=T_int và all_saved_ages cho mọi nguồn, cùng từng seed GÉANT.


| Nguồn | h/T_int | n | Tốt hơn / bằng / tệ hơn | Median Δ (pp) | Mean Δ (pp) | Bằng chỉ nhờ 2SE |
| --- | --- | --- | --- | --- | --- | --- |
| CTMC | 0.333333 | 93 | 38/55/0 | -1.3145e-13 | -0.015149 | 0 |
| CTMC | 1 | 93 | 81/8/4 | -1.93743e-05 | -0.047165 | 0 |
| CTMC | 3 | 93 | 76/9/8 | -9.36192e-07 | -0.0158522 | 0 |
| CTMC | 10 | 93 | 67/9/17 | -3.35929e-10 | -0.00095249 | 0 |
| CTMC | 30 | 93 | 42/24/27 | 0 | -2.31556e-05 | 0 |
| e4 | 1 | 17 | 5/12/0 | 0 | -5.99099 | 3 |
| e4 | 2 | 17 | 2/15/0 | 0 | -0.479383 | 5 |
| e4 | 4 | 17 | 1/16/0 | 0 | 0.0883897 | 6 |
| e4 | 7 | 17 | 0/17/0 | 0 | 0.161478 | 5 |
| e4 | 15 | 17 | 0/17/0 | 0 | 0 | 0 |
| e4 | 30 | 17 | 0/17/0 | 0 | 0 | 0 |
| e4b | 1 | 17 | 3/14/0 | 0 | -17.6587 | 5 |
| e4b | 2 | 17 | 4/13/0 | 0 | -3.99344 | 4 |
| e4b | 4 | 17 | 0/17/0 | 0 | -1.08536 | 7 |
| e4b | 7 | 17 | 0/17/0 | 0 | -0.471971 | 3 |
| e4b | 15 | 17 | 0/17/0 | 0 | -0.00793674 | 1 |
| e4b | 30 | 17 | 0/17/0 | 0 | 0 | 0 |
| GEANT_both_seeds | 1 | 34 | 8/26/0 | 0 | -11.8248 | 8 |
| GEANT_both_seeds | 2 | 34 | 6/28/0 | 0 | -2.23641 | 9 |
| GEANT_both_seeds | 4 | 34 | 1/33/0 | 0 | -0.498485 | 13 |
| GEANT_both_seeds | 7 | 34 | 0/34/0 | 0 | -0.155246 | 8 |
| GEANT_both_seeds | 15 | 34 | 0/34/0 | 0 | -0.00396837 | 1 |
| GEANT_both_seeds | 30 | 34 | 0/34/0 | 0 | 0 | 0 |
| E6_L100 | 1 | 102 | 69/23/10 | -1.08492 | -15.4004 | 0 |
| E6_L100 | 2 | 102 | 67/17/18 | -0.290019 | -5.43982 | 0 |
| E6_L100 | 4 | 102 | 52/9/41 | -1.15368e-14 | -1.42925 | 0 |
| E6_L100 | 7 | 102 | 52/1/49 | -2.09655e-14 | -0.375222 | 0 |
| E6_L100 | 15 | 102 | 43/8/51 | 2.81871e-14 | 0.0454113 | 0 |
| E6_L100 | 30 | 102 | 35/9/58 | 6.03423e-14 | 0.102834 | 0 |
| E6_L300 | 1 | 102 | 55/38/9 | -1.72307e-13 | -14.5573 | 0 |
| E6_L300 | 2 | 102 | 55/30/17 | -7.61613e-14 | -4.78237 | 0 |
| E6_L300 | 4 | 102 | 50/9/43 | 0 | -1.16232 | 0 |
| E6_L300 | 7 | 102 | 46/3/53 | 2.5439e-14 | -0.273078 | 0 |
| E6_L300 | 15 | 102 | 37/9/56 | 3.5502e-14 | 0.0508008 | 0 |
| E6_L300 | 30 | 102 | 27/9/66 | 8.56473e-14 | 0.0751995 | 0 |


File `paired_by_h.json`; ID G22_R11 đối chiếu mean và median Δ E6 theo từng h,L. Median chênh lệch cặp không phải chênh của hai median.


## 5. Tách Switch-optimal và Stay-optimal


**MỚI:** bảng subgroup; tổng C2_AGE/C3/M2 giữ đúng ledger. s là rate gap dài hạn, không phải optimal action tại mọi state/h hữu hạn. C2_AGE giữ baseline_available và τ/T_int≥1, h/T_int≥3, harm nếu GS<−0.1%; C3 giữ τ/T_int≥1, h/T_int≥1, không thêm baseline filter. Các dòng seconds_1 được giữ nếu actual ratio thỏa điều kiện. Tie M2: 93 regime, τ=T_int, h≈30T_int, median exact tie_mass fresh/stale.


| Nhóm | Regime | C2: harm/n | Tỷ lệ | C2 median GS | C3 n | C3 median fresh / stale | M2 n | Tie fresh / stale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALL | 93 | 507/676 | 0.75 | -3.90979 | 904 | 5.06153/0.0118125 | 93 | 0.0154925/0 |
| Switch-optimal (s<0) | 42 | 324/324 | 1 | -4.37343 | 422 | 3.85408/1.60197e-05 | 42 | 0.0165257/0 |
| Stay-optimal (s>0) | 51 | 183/352 | 0.519886 | -1.03404 | 482 | 11.442/3.13509 | 51 | 0.0140848/0 |
| s=0 | 0 | 0/0 | N/A | N/A | 0 | N/A/N/A | 0 | N/A/N/A |


Tie là probability share [0,1], không phải % C_ref. Median tổng không là trung bình có trọng số của median nhóm. File `optimal_sign_splits.json`.


## 6. Dấu từ primitives: m₀ và π₀


**MỚI — chẩn đoán dùng π₀ thật, không phải dự báo ngoài mẫu.** Raw W1b không có mảng π/gap. Đã dùng generator và fluid functions CTMC hiện có với N/amplitude đã lưu; giải π dưới Stay trên hai path. m₀=Eπ_A[gap_A(∞)]+Eπ_B[gap_B(∞)]+c, đơn vị packet·s; s dùng nguyên từ raw, đơn vị packet. Không gọi Chain, Poisson bias, V, evaluator, chi phí thật hay rollout mới. ∞ chỉ cách lấy fluid gap sau drain; không khẳng định h̄ đồng nhất trên không gian trạng thái không chặn. CPU mục này 36.821455s, cap 3600 CPU-s.


| Nhóm | n | Dấu m₀ khớp / khác dấu s | Median m₀ (packet·s) | Median stale good-action τ=T_int | τ=3T_int |
| --- | --- | --- | --- | --- | --- |
| ALL | 93 | 64/29 | -11.164 | 0.999028 | 1 |
| Switch-optimal (s<0) | 42 | 42/0 | -163.308 | 1 | 1 |
| Stay-optimal (s>0) | 51 | 22/29 | -0.252974 | 0.748307 | 0.0150233 |


Confusion matrix (dấu nghiêm ngặt, không epsilon):


| sign(s) | sign(m₀) | n |
| --- | --- | --- |
| -1 | -1 | 42 |
| 1 | -1 | 29 |
| 1 | 1 | 22 |


Stale good-action share trong bảng dùng h gần 30T_int của từng regime/tuổi, không thay bằng m₀ sign. JSON có cả h thực, limiting fluid-decision share từ saved asymptotic, residual π và SHA từng π. M₀ trung bình chỉ mô tả cực hạn khi stale mất thông tin; tại tuổi hữu hạn cần phân phối conditional gap. File `primitive_signs.json`; M1/M2 là provenance cho shares/ties đã lưu, m₀ chưa có ledger.


## 7. Mẫu số V-C


Các số headline đã có V73_DENOM/V73_STRATA/V73_ATTRIB; **MỚI:** phép phân rã và bảng chi tiết dưới đây. Theo cases.csv và card: N=32 instances/record; 2 tuổi 300/900s; h={1,2,4,6}h; H1–H3 chỉ DAY1/DAY2, stratum S, evaluable, h={2,4,6}h. 49 usable test weekdays sau loại 2005-06-27; original run vẫn INCOMPLETE, đây là amended analysis DEVIATION_V7_3_01.


| Flow | S ngày | O ngày | S cases/evaluable | O cases/evaluable |
| --- | --- | --- | --- | --- |
| DAY1 | 29 | 20 | 232/46 | 160/120 |
| DAY2 | 29 | 20 | 232/46 | 160/132 |
| DAY3 | 29 | 20 | 232/58 | 160/156 |


| Số | Tái dựng |
| --- | --- |
| 348 | 29 S days * 2 flows (DAY1/DAY2) * 3 horizons (2,4,6h) * 2 ages |
| 480 | 20 O days * 3 flows * 4 horizons (1,2,4,6h) * 2 ages |
| 408 | O cases surviving C_ref/h evaluability; per-flow 136+136+136, not a full fixed-day rectangle |
| 76 | primary S cases surviving C_ref/h gate: 16 at 2h + 28 at 4h + 32 at 6h |
| 1216 | 38 unique flow-day-horizon tuples * 32 instances; fresh counted once across two ages |


| h (h) | Primary cases | Unique fresh record-horizons | Fresh decisions | Stale decisions |
| --- | --- | --- | --- | --- |
| 1 | 0 | 0 | 0 | 0 |
| 2 | 16 | 8 | 256 | 512 |
| 4 | 28 | 14 | 448 | 896 |
| 6 | 32 | 16 | 512 | 1024 |


76 cases thuộc 8 calendar days, 16 flow-days; số horizon qua evaluability gate khác nhau giữa ngày. 1216=38×32 đếm fresh một lần qua hai tuổi; stale=76×32=2432; tổng fresh+stale=3648. 408 là số O evaluable qua từng horizon, không phải 51 ngày độc lập; 480=20×3×4×2. DAY3 là control training slope gần 0, mô tả; 1h là sensitivity đã khai báo, ngoài population H1–H3. File `vc_denominators.json` có per-flow/per-horizon/per-day; không mở thêm outcomes.


## Kiểm chứng, thời gian và tái tạo


9576 checks PASS tại thời điểm lập báo cáo: raw/CSV, SHA chunks, ledger, quantile/count và file đầu vào bất biến. CPU phân tích (kể cả primitives và vẽ hình): 43.584085s; wall 44.131669s.


| Bước | CPU-s | Wall-s |
| --- | --- | --- |
| CTMC_saved_selection | 1.02243 | 1.02247 |
| 2_Fig3_IQR | 0.0175454 | 0.0175478 |
| GEANT_raw_replay | 1.2034 | 1.20346 |
| 1_Fig4_signed | 0.0071356 | 0.00713696 |
| 3_E6_replay | 0.199072 | 0.199082 |
| 4_paired_comparisons | 0.0328013 | 0.0328033 |
| 5_optimal_sign_splits | 0.0358295 | 0.0358329 |
| 6_primitive_signs | 37.0304 | 37.0321 |
| 7_VC_denominators | 0.0722437 | 0.0722475 |
| candidate_figures | 3.88763 | 4.43337 |
| input_integrity | 0.0739838 | 0.0740033 |


Lệnh chạy thực tế (log riêng trong thư mục kết quả):

```bash
cd /home/vantai/state-model-regret
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.letter.p2_tier2 --self-test
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.letter.p2_tier2
```


Tái tạo vào thư mục mới, không ghi đè kết quả đã có:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.letter.p2_tier2 --out results/letter/p2_tier2/reproduction_01
```


Mọi số của từng mục tái tạo cùng lệnh trên, từ `experiments/letter/p2_tier2.py`. `input_sha256.json` ghi từng file thực đọc (gồm brief, ledger và source); `validation.json` ghi actual/expected; `run_metadata.json` ghi environment, argv, source SHA, timing và provenance. Không tải/đọc paper mới.


Lịch sử thực thi: run_01.log: KeyError: 'decisions'. Giữ nguyên log lỗi; sửa adapter tên trường ledger, không sửa dữ liệu/công thức hay chạy truth. Tổng CPU primitives ghi nhận trong các lượt ở thư mục này: 69.665476s, dưới cap 3600s.


## Ngoại lệ và giới hạn


- Đã hoàn thành cả 7 phân tích. Khác biệt 93/92 được giữ ở hai bảng; không sửa ledger hoặc paper.
- E6 sign-error dùng ordering level-(i) training làm reference; records lặp qua hai seed/tuổi/horizon.
- GÉANT paired SE là SE mô tả của cost difference trên cùng instances, sau chọn worse side; không CI cho population.
- Relative equality không có absolute floor; các sign/count cực gần 0 không được diễn giải thành effect có độ lớn thực tiễn.
- m₀ dùng π₀ thật và support truncation đã lưu; không chứng minh prediction, deployment realism hay novelty.
- Không truth rollout mới; không thay threshold, card, verdict; không commit/SSH; không sửa file có trước.
