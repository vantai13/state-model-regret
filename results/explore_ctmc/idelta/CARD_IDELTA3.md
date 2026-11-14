# Thẻ I_Δ vòng 3 — help band và kiểm lại fluid (khóa trước khi chạy panel)

Doan Van Tai — **AI (Claude) soạn, khóa và chạy theo ủy quyền** ("tiếp tục đi", 14/11/2026). Exploration, không phải
thẻ tác giả, không mentor review, không đổi RQ/contract/PC/Gate/G1. Khóa = sha256 trong `lock_idelta3.json`.

## 0. Những gì đã thử và trượt trước thẻ này (giữ nguyên hồ sơ)

Trên dữ liệu đã lộ (run01: 9 regime, run02: 45 regime, 28 điểm fluid của run02), hai ứng viên cơ chế cho ngoại lệ
help band đều **không** giải thích được ρ = Γ_add/Γ ở mức từng regime (7 T_int):
- T_prox = E|ẽ| / E|Δ + b|: Spearman −0,21; band không có T_prox cao hơn
  (`calibration_idelta3_pass1_Tprox.json`).
- κ_Δ = |EΔ| / √E[Δ²]: Spearman +0,27; band có κ_Δ thấp hơn về median (0,66 so với 0,93/0,99) nhưng không tách
  từng dòng (`calibration_idelta3.json`).

Ứng viên thứ ba, cũng là cái cuối cùng tôi thử trước khi khóa (không thử thêm): **dấu của G_S ở 7 T_int**. Ở h dài,
Γ ≈ −G_S (sai khác median 0,003 pp). Trên dữ liệu hiệu chỉnh:
- G_S > 0 ("state mới giúp M0"): 9/10 dòng có ρ ≤ 0,5;
- G_S < 0 ("state mới hại M0"): 24/33 dòng có ρ ≥ 0,75;
- band có G_S > 0 ở 16/18 regime.

Đây là quan hệ giữa hai outcome tìm được sau hai lần thử, nên cần panel mới.

## 1. Mệnh đề

Ở h ≈ 7 T_int:
- Phần "state mới **hại** M0" tái tạo được bằng một M0 chỉ lệch hằng, tức là ngưỡng cộng mù horizon.
- Phần "state mới **giúp** M0" (help band) cần cấu trúc phụ thuộc state của sai số; một model chỉ lệch hằng
  không tái tạo được.

Ở fluid: kiểm lại hướng của h với mức ngắn h = 2 s.

## 2. Panel (write-once, cố định trước khi chạy)

- **CTMC:** `cases_r3.json`, 40 regime mới (seed 20261115; band 20, neg 10, pos 10). Cùng miền, cách Sobol và luật
  chi phí như L7.5; 0 trùng với mọi case list cũ và `cases_fresh.json`. h = {0,3; 1; 3; 7} × T_int_max. Chỉ tính phần
  nhẹ (`light_regime`): Γ, Γ_add, G_S, κ_add, κ_Δ, T_prox; không J, không số hạng biên.
- **Fluid:** `fluid_points_r3.json`, 64 điểm toy mới trên cùng lưới như vòng 2, không trùng 28 điểm cũ, không κ = 3/5,
  không h = 4. h ∈ {2, 8, 32} s, ref 2.

## 3. Dự đoán (giá trị hiệu chỉnh trong ngoặc)

ρ chỉ đọc khi |Γ| ≥ 0,05 pp. "Ngoài band" = neg ∪ pos.

**CTMC:**
- **B1 (lặp lại ngoại lệ band):** median ρ_7T của band ≤ 0,5 **và** median ρ_7T ngoài band ≥ 0,75. (0,41 / 1,25)
- **B2 (quan hệ với dấu G_S):** trong các dòng 7T có G_S > 0, ≥ 70% có ρ ≤ 0,5; trong các dòng có G_S < 0, ≥ 60% có
  ρ ≥ 0,75. Mỗi nhóm cần ≥ 6 dòng, nếu không thì NOT_EVALUABLE. (90% / 73%)
- **B3:** ≥ 70% regime band có G_S_7T > 0. (89%)
- **B4 (lặp lại H1 vòng 2, chỉ ngoài band):** median ρ_1T ≤ 0,25 **và** median ρ_7T ≥ 0,5. (0,07 / 1,25)

**Fluid:**
- **G1:** tỷ lệ điểm có ρ(32) > ρ(2) **dưới** 60% (dự đoán không đơn điệu trong từng điểm); cần ≥ 8 điểm.
  (36% / 40% khi bỏ HOLD)
- **G2:** median ρ(2) ≤ 0,5 **và** median ρ(32) ≥ 0,75; cần ≥ 8 điểm mỗi mức. (0,28 / 0,85)
- **G3:** κ_add tăng 2 → 32 ở ≥ 80% điểm. (89%)
- **G4:** Spearman(κ_add, ρ) trên các dòng đủ điều kiện ≥ 0,3. (0,47; có nhiễu h chung, chỉ mô tả hướng)

**Control và luật:**
- C1: Γ tự tính khớp engine ≤ 1e−7 pp.
- Dưới 90% regime COMPLETED → B1–B4 INCONCLUSIVE.
- Fluid: một verdict đổi khi bỏ điểm HOLD_PRECISION → INCONCLUSIVE.
- Spearman của T_prox, κ_Δ, κ_add trong CTMC chỉ báo mô tả, không có dự đoán (chúng đã trượt khi hiệu chỉnh).
- Không đổi ngưỡng/panel sau khi thấy kết quả; không chạy lại.

**Cách đọc:**
- "Ngoại lệ band lặp lại" chỉ khi B1 PASS.
- "Help cần sai số phụ thuộc state, harm là ngưỡng cộng bias" chỉ khi B2 PASS và B3 PASS.
- "Hướng theo h ở fluid đứng ở mức median" chỉ khi G2 PASS.

## 4. Không nhận

B2 là quan hệ outcome–outcome, không phải predictor tham số. Không phải bằng chứng mạng thật, không novelty; Γ_add là
một counterfactual (b = trung bình); AI soạn và tự chấm.
