# Thẻ I_Δ vòng 2 — phần Γ "chỉ do ngưỡng" có tăng theo h không? (khóa trước khi chạy panel)

Doan Van Tai — **AI (Claude) soạn, khóa và chạy theo ủy quyền** ("bạn có thể tự soạn thực hiện rồi tự chạy giúp tôi",
14/11/2026). Exploration, không phải thẻ của tác giả, không confirmation chính thức, không đổi RQ/contract/PC/Gate/G1.
Không qua mentor review. Khóa = sha256 trong `lock_idelta2.json`; runner từ chối nếu file khóa đổi.

## 1. Mệnh đề cần kiểm

Run01 (9 regime đã lộ, đọc post-hoc) gợi ý: ở h ≈ T_int, Γ chủ yếu đến từ sai số **phụ thuộc state** của M0
(I_Δ ≠ 0). Ở h ≈ 7 T_int, sai số gần như là **hằng**, và Γ giải thích được bằng ngưỡng cộng bias. Vòng 2 kiểm mệnh đề
này trên regime CTMC **mới** và kiểm xem nó có chuyển sang plant fluid (engine A00) không.

**Đại lượng:**
- Γ_add = Γ của M0 giả định có sai số hằng b = trung bình sai số (CTMC: E_π e; fluid: trung bình trong ô).
  Mô hình này có I_Δ ≡ 0, nên mọi interaction còn lại chỉ do ngưỡng.
- ρ = Γ_add / Γ, chỉ đọc khi |Γ| ≥ 0,05 pp.
- κ_add = |E e| / √E[e²] ∈ [0, 1]; bằng 1 nghĩa là sai số hằng ở mọi state.
- E|I_Δ| theo %Cref.

## 2. Panel (cố định trước khi chạy, write-once)

- **C2 — CTMC ctmc-v1** (a = 6, τ = 1, c_sw = 0): `cases_fresh.json`, 45 regime. Cùng miền, stratum, cách Sobol và
  luật loại chi phí của L7.5, seed 20261114, 15 regime mỗi stratum; 0 trùng tuple ở mọi case list cũ.
  h = {0,3; 1; 3; 7} × T_int_max; **lo = 1 T_int, hi = 7 T_int**.
- **F2 — fluid A00, ô toy** (contract v1.2, tuổi quan sát 1 s, B rates (2, 14), ref 2, dt = 1/240 s):
  `fluid_points.json`, 24 điểm panel rút ngẫu nhiên không lặp trên lưới κ ∈ {3/10, 1, 3}, λA ∈ {6, …, 8},
  η ∈ {1/2, 3/4}, yA, yB ∈ {0, 1, 3, 8}. h ∈ {1/2, 2, 8, 32} s; **lo = 1/2, hi = 32**.
  Không dùng κ = 3/5 hoặc h = 4 (trục niêm phong R09/R10); không trùng ô có tên nào của grid.
- Hiệu chỉnh ngưỡng **chỉ** dùng run01 và 4 điểm pilot fluid (`calibration_idelta2.json`). Panel tách rời phần hiệu chỉnh.

## 3. Dự đoán (ngưỡng; giá trị hiệu chỉnh trong ngoặc)

**CTMC (C2):**
- **H1 (chính):** median ρ_lo ≤ 0,25 **và** median ρ_hi ≥ 0,5. (run01: 0,05 / 1,30)
- **H2 (chính):** ρ_hi > ρ_lo ở ≥ 60% regime đủ điều kiện ở cả hai mức. (run01: 71%)
- **H3:** E|I_Δ|/Cref ở hi nhỏ hơn ở lo trong ≥ 90% regime. (run01: 100%)
- **H4:** κ_add ở hi lớn hơn ở lo trong ≥ 90% regime. (run01: 100%)

**Fluid (F2), kiểm khả năng chuyển plant:**
- **F1:** E|I_Δ|/Cref ở h = 32 nhỏ hơn ở h = 8 trong ≥ 75% điểm. (pilot 4/4; ở pilot, từ h = 1/2 tới 8 nó *tăng*)
- **F2:** κ_add ở h = 32 lớn hơn ở h = 1/2 trong ≥ 80% điểm. (pilot 4/4)
- **F3:** ρ_hi > ρ_lo ở ≥ 60% điểm đủ điều kiện ở cả hai mức; cần ≥ 8 điểm. (pilot 2/2)
- **F4:** median ρ_lo ≤ 0,25 **và** median ρ_hi ≥ 0,5; cần ≥ 8 điểm mỗi mức. (pilot 0,02 / 0,71; có một điểm pilot ngược,
  FT03 h = 32: Γ = 6,2 mà Γ_add = 0)

**Control:**
- **C1:** identity ≤ 1e−7, tower ≤ 1e−9, Γ khớp engine ≤ 1e−7 pp, biên trên ≤ 1e−6. Trượt → dừng, sửa, chạy lại
  và giữ attempt cũ.
- Hơn 10% regime CTMC không COMPLETED → H1–H4 là INCONCLUSIVE.
- Fluid HOLD_PRECISION: giữ và gắn cờ. Verdict F nào đổi khi bỏ điểm HOLD → INCONCLUSIVE.

**Cách đọc:**
- "Đọc theo h đứng ở regime CTMC mới" chỉ khi H1 **và** H2 PASS.
- "Chuyển sang fluid" chỉ khi F3 **và** F4 PASS.

Không đổi ngưỡng, panel hay định nghĩa sau khi thấy kết quả. Không chạy lại để cứu verdict.

## 4. Không nhận

- Không phải bằng chứng cơ chế ở mạng thật.
- Đơn vị h ở fluid (giây) không phải T_int, nên F chỉ kiểm hướng của hiệu ứng, không kiểm thang.
- Γ_add là một counterfactual (chọn b = trung bình), không phải phân rã duy nhất.
- AI soạn và tự chấm: không author-self, không Understanding, không novelty.
