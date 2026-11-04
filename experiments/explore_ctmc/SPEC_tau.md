# SPEC L7.5 — tuổi telemetry τ là trục mới duy nhất (ctmc-v1, a = 6)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền** ("đóng vai trò là tôi… đây là mệnh lệnh", 04/11/2026). Viết trước code.
Nhánh `explore/tau-l75` từ `explore/twoscale-l73`. Không truth ở τ ≠ 1 ngoài hai regime control.

## 1. Model

- Plant, chi phí, các twin, P1 và D22: **y hệt ctmc-v1** (`ctmc.py`, không sửa byte nào). a = 6, μ = 10.
- Chỉ đổi τ: Y là backlog đọc ở t0 − τ (mode cộng bỏ), X là state ở t0.
  - Posterior cũ: E[v(X) | Y = y] = Σ_m π(y, m) [e^{Q_Stay τ} v](y, m) / p(y). Đây là `ctmc.posterior_mean` với tham số τ.
  - D22: J[y, n, m] = P(Y = y, X = (n, m)), qua `ctmc._joint_old_current(stay, τ)`.
- Pipeline đổi theo τ: L00, L01 (twin trên state cũ), D22 (L_cb0, L_cb1, F, V, F1, V1), KO và hybrid trên state cũ,
  margin trên state cũ. **Không đổi:** V, L10, L11, C_ref, twin trên state mới.
- Cách cài: `tau.at_tau(τ)` thay tạm `ctmc.TAU`, `ctmc.posterior_mean` và `ctmc.joint_old_current` bằng bản có τ, rồi trả
  lại. Ở τ = 1, mọi phép tính đi đúng đường code v1, nên số phải trùng v1 tới từng bit trên cùng một máy.
- D22 ở τ ≠ 1 không ghi cache ra đĩa (tránh đầy ổ); J giữ trong bộ nhớ trong một context.

## 2. Lưới

- τ/T_int ∈ {0,003; 0,01; 0,03; 0,1; 0,3; 1; 3; 10}. T_int là T_int lớn nhất của bốn chuỗi, cùng định nghĩa với h/T_int
  của v1. τ làm tròn 3 chữ số có nghĩa (`design.rational`). Thêm τ = 1 s làm điểm nối với L7.1.
- h/T_int ∈ {0,3; 1; 3; 7; 15; 30}, cùng cách làm tròn. Cộng h = ∞ cho đại lượng tiệm cận.
- Lát x: ba họ (u, λA) ∈ {(1, 7), (2, 13/2), (1/2, 8)}, κ ∈ {1/5, 1}, x bước 1/20 (như `zf_a6_xs` của L7.2), h = 10·T_int,
  ba giá trị τ/T_int ∈ {0,01; 0,1; 1}.

## 3. Đại lượng zero-fit (không cần truth)

Với mỗi (regime, τ, h): F_new, F_old(τ), z_pred1(τ, h), z_∞(τ), B(τ), β_C. Với N ≤ D22_NMAX_TAU (mục 5): F_cb(τ),
z_F,∞(τ) và z_V,∞(τ). Trên lát x: x*(τ), là đổi dấu đầu tiên + → − của z (cùng quy tắc `zf_report.x_star`), tính cả từ
z_∞ và từ z_pred1 ở h = 10·T_int.

## 4. Guard

- Mọi truth (`Chain.V`, `Chain.V_aug`) chạy trong `at_tau(τ)` với τ ≠ 1 bị từ chối (PermissionError), trừ khi:
  1. regime nằm trong `CONTROL_REGIMES_L75` (loại khỏi mọi case list); hoặc
  2. `results/explore_ctmc/locks_l75.json` chứa sha256 của thẻ và thẻ trên đĩa còn khớp.
- Runner truth (sau này) còn kiểm thêm toàn bộ hash đã khóa, stage và máy (`dt4n-research-01`), như `scan2`.

## 5. Control và tiêu chí (ghi trước khi chạy)

| Control | Việc | Đạt khi |
|---|---|---|
| (a) | τ = 1 tái lập zero-fit v1: 10 regime asym cũ và `zf_a6_xs` | z_∞, F_new, F_old, z_pred1 lệch tương đối ≤ 1e−12 và mọi share quyết định trùng |
| (b) | Posterior qua `expm_multiply` so với `scipy.linalg.expm` dày, N nhỏ, 4 giá trị τ | lệch tuyệt đối ≤ 1e−10 (đã chuẩn hóa theo max\|v\|) |
| (c) | Monte Carlo đầu-cuối (CRN, `mc.end_to_end`, gồm D22) ở hai regime control, τ/T_int ∈ {1/10; 3}, h = 3·T_int, 200.000 episode | mọi \|z\| ≤ 3,5 khi se > 0; khi se = 0 (MC không thấy bất đồng nào) thì báo "MC không phân giải" và cần \|exact\| ≤ 1e−4·C_ref |
| (d) | Cô lập: sau mỗi context, hàm và hằng của `ctmc` trở lại nguyên; τ = 1 sau một lần τ ≠ 1 cho cùng bit | đúng |
| (e) | D22: marginal của J khớp π, tower check (trong `evaluate_d22`) ở hai τ | ≤ 1e−10 |
| (f) | τ lớn: F_old(τ = 10·T_int) so với quyết định trên posterior dừng (Y không mang thông tin) | chỉ báo cáo |

**Sửa (c), 04/11, sau một lần chạy thử 2.000 episode và trước lượt chính thức:** ở τ = 3·T_int, M0 và M1 trên state cũ
gần như luôn chọn Switch; G_M chỉ khác 0 trên khối lượng ~1e−7 nên MC thấy se = 0 và z = ∞ (exact 9e−7). Tiêu chí cũ
"mọi |z| ≤ 3,5" không định nghĩa được z ở trường hợp này. Đại lượng đó không được MC kiểm, và được báo riêng.

D22_NMAX_TAU: J có (N + 1) cột và chi phí `expm_multiply` tăng theo τ·‖Q‖, nên D22 zero-fit chỉ tính khi
N·(1 + τ·‖Q‖) nằm dưới ngân sách đo ở Stage 0 (ghi trong báo cáo, kể cả số điểm bỏ).

## 6. Máy

Mọi số dùng cho thẻ và để chấm tính trên GCP `dt4n-research-01` (quy tắc một máy từ L7.3 control (e)). Máy local chỉ để
viết code và test.
