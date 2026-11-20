# Design X-CTMC (X1 + X1b + X3) và brief cho Codex, 20/11/2026

- **Từ:** Claude, quyết định thay tác giả theo ủy quyền ("mọi quyền quyết định đều có bạn quyết định"). Không có mentor review.
- **Cho:** Codex (code, test, pilot). **Tác giả:** Doan Van Tai.
- **Repo:** `/home/vantai/state-model-regret`, nhánh `letter` (không merge main).
- **Môi trường:** `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`; chỉ có `python3`, không có `rg`.

## 1. Mục đích
| Mã | Câu hỏi |
|---|---|
| X1 | Twin không có hàng đợi, quyết định theo **tải đo** (rule ngưỡng utilization, rule min-MLU), có bị telemetry tươi làm hại ở quyết định giữ lâu không? Dấu và độ dốc G_S/h có dự đoán được **chỉ từ dữ liệu nhà mạng có** (ŝ ước lượng từ bản ghi hữu hạn, share quyết định của chính twin trên lịch sử) không? |
| X1b | Kết quả chính cho M0 và Hybrid có còn đứng trên CTMC **dị biệt** (μ, α, κ khác nhau giữa hai path) không? |
| X3 | Cơ chế C5: rule stale dồn quyết định về "action gộp" sign(E_π0[Δ̂]). Harm của M0 ở h dài xảy ra khi action gộp trùng action dài hạn đúng |

## 2. Plant (giữ đúng định nghĩa paper Sec. II, chỉ mở rộng tham số theo path)
- Hai path độc lập, MMPP/M/1 mỗi path: mode m_p ∈ {−1, +1}, tốc độ đến ℓ_{p,a} + m_p α_p, mode đổi với rate 1/κ_p, service μ_p.
- Managed flow u: Stay (a = 0) đi path A; Switch (a = 1) đi path B. c = 0.
- Chi phí f(x) = n_A + n_B; V_a(h, x) chính xác.
- Truncation N_p theo đuôi dừng < 1e-13 (dùng `mmpp.choose_N` hoặc `ctmc.choose_N` với μ_p, α_p, κ_p của path).
- Stale: Y = X_{−τ} dưới luật dừng của Stay, kernel chính xác e^{Q_0 τ}. Tie về Stay.
- **Tái dùng nguyên văn** các primitive có sẵn:
  - `experiments/explore_ctmc/ctmc.py`: `Chain`, `generator`, `m0_vhat`, `posterior_mean`, `pair_sum`, `det_expm1`;
  - `experiments/letter/mmpp.py`, `shat.py`, `pl_posterior.py` (mẫu lịch sử bằng uniformization, ŝ từ bản ghi);
  - mẫu lock/verify/truth/score của `pl_posterior.py` và `v7_4_short.py`.

  Nếu primitive cứng μ = 10 hoặc cùng α, κ cho hai path, viết wrapper mới trong file mới gọi các hàm cấp path (`Chain(load, kappa, N, a,
  mu)`). **Không sửa file cũ.** Nếu gặp guard amplitude held-out (`_truth_allowed`), **không bypass**; dừng và báo.

## 3. Lưới regime mới (sinh trước mọi truth, seed 2611201)
- 64 regime, lấy mẫu có ràng buộc:
  - μ_p ∈ {5, 10, 20};
  - utilization trung bình ρ_{p,a} = ℓ_{p,a}/μ_p ∈ [0,2; 0,9] với cả hai action;
  - α_p/ℓ_p ∈ {0,2; 0,5; 0,8};
  - κ_p ∈ {1, 5, 20};
  - u sao cho cả hai action ổn định.
- **Phân tầng 32/32** theo nhãn tính **chỉ từ tham số**:
  - "agree": thứ tự theo max utilization trung bình trùng thứ tự theo chi phí dừng ước lượng M/M/1, Σ_p ρ/(1 − ρ);
  - "disagree": ngược nhau.

  Tầng disagree là chỗ phép thử có thể thất bại.
- **Luật loại (chỉ dựa trên tham số hoặc dữ liệu training, ghi trước):**
  - |X_A|·|X_B| hoặc chi phí pilot dự phóng > cap 3600 CPU-s mỗi regime: NOT_RUN;
  - P(backlog > 0) < 1% ở cả hai action (mạng gần rỗng): báo riêng.
- T_int tính như paper: max_{p,a} của tích phân hệ số tự tương quan dừng của backlog.

## 4. Twin và rule (mỗi rule có phía fresh và stale ở τ ∈ {1, 3} T_int)
| Rule | Định nghĩa |
|---|---|
| M0 | gap fluid Δ̂(h, x) của paper (Eq. fluid), mở rộng theo path |
| Hybrid_true | Δ̂ + h·s (s chính xác) |
| Hybrid_hat | Δ̂ + h·ŝ, ŝ từ estimator MMPP/M/1 bản ghi hữu hạn L = 100 T_int của paper (seed train) |
| Stationary_hat | Switch iff ŝ < 0 (không telemetry) |
| TH_θ, θ ∈ {0,5; 0,65; 0,8; 0,9} | Ước lượng rate đến mỗi path: fresh λ̂_p = ℓ_p + m_p α_p; stale λ̂_p = ℓ_p + α_p E[m_p(0) \| Y]. Utilization dự đoán U_{p,a} = (λ̂_p + u·1{flow ở p dưới a})/μ_p. Switch iff U_{A,0} > θ **và** U_{B,1} < U_{A,0}. Không dùng backlog |
| MLU | Switch iff max_p U_{p,1} < max_p U_{p,0} |
| Pool (X3) | action hằng 1{E_π0[Δ̂(h, X)] < 0}, không theo state |

## 5. Lưới đánh giá
h ∈ {1, 3, 10, 30, 100} T_int; τ ∈ {1, 3} T_int.

**Đầu ra mỗi (regime, rule, side, τ, h):**
- L, G_S, C_ref, regret;
- p_new, p_old (share Switch), tie share;
- s chính xác, ŝ, B_∞ nếu có.

## 6. Dự đoán từ dữ liệu nhà mạng (lệnh `predict`, chạy trước truth, ghi file, vào lock)
Dùng **seed train 2611202**, khác seed test 2611203 và seed pilot 2611204.
- **ŝ_hat:** từ bản ghi L = 100 T_int, cùng estimator paper.
- **ΔF̂_j(h, τ):** share Switch của rule j phía stale trừ phía fresh, ước lượng trên lịch sử hữu hạn của Stay. Gồm 2000 cặp (Y, X) cách nhau τ, lấy
  mẫu bằng uniformization. Rule stale dùng posterior chính xác của twin.
- **Dự đoán:**
  - slope_pred = ŝ_hat·ΔF̂;
  - dấu dự đoán của G_S(h) ở h ∈ {30, 100} T_int là dấu của slope_pred.
- **Null utilization:** thay ŝ_hat bằng s_U = (mean max-util của Switch) − (mean max-util của Stay). Null này không có hàng đợi.
- **Dự đoán C5 (X3):**
  - c5_sign = −1 (harm) nếu action gộp = action dài hạn đúng (1{s < 0}), ngược lại +1. Dùng s chính xác vì đây là phép thử cơ chế, không phải
    dự đoán vận hành.
  - Thêm chỉ số tập trung: |p_old − ½| so với |p_new − ½|.

## 7. Lệnh CLI
- `pilot`: 4 regime nặng nhất theo kích thước state, đo CPU-s; chỉ seed pilot; không chạm regime test ngoài pilot.
- `predict`: ghi `predictions.json`.
- `lock` và `verify-lock`.
- `truth --workers N`: một lần, cap CPU, ghi raw theo từng regime (checkpoint), receipt.
- `score`: theo thẻ.

Tách `rescore_independent.py`. Script này do Codex viết **ở lượt sau** và không import module chấm.

## 8. Test đơn vị bắt buộc (analytic sanity)
- Khi μ_A = μ_B = 10, α_A = α_B = 6, κ_A = κ_B, wrapper khớp `ctmc.evaluate` hoặc `evaluate_m0` cũ trên ít nhất 2 regime cũ (tới 1e-9 tương
  đối).
- G_S = 0 khi rule fresh và stale trùng nhau.
- Identity: G_S/h → s·ΔF_∞ trên một regime nhỏ.
- TH_θ với θ ≥ 1 không bao giờ Switch.
- Posterior với τ → ∞ cho E[m | Y] → 0.

## 9. Ranh giới file
- **Chỉ tạo:** `experiments/letter/x_ctmc.py`, `tests/test_x_ctmc.py`, `results/letter/x_ctmc/` (pilot, predictions, lock sau này).
- **Không sửa** file có sẵn. Không commit; Claude commit. Không ssh lên GCP; Claude chạy truth.
- Job Codex khác (X-GÉANT) chạy song song và chỉ ghi `experiments/letter/x_geant.py`, `tests/test_x_geant.py`, `results/letter/x_geant/`.

## 10. Kiểm phải chạy
- `python3 -m pytest -q tests/test_x_ctmc.py`;
- suite letter liên quan: `tests/test_pl_posterior.py`, nếu có;
- pilot thật với 4 regime nặng nhất, báo CPU-s và wall.

## 11. Báo cáo cuối (tiếng Việt)
- File đã tạo;
- danh sách 64 regime với nhãn tầng và số NOT_RUN dự kiến;
- pilot CPU-s, dự phóng CPU-h cho toàn truth;
- kết quả test.
- **Không** chạy `truth` hay `score`.

## 12. Phụ lục A (20/11, sau khi Codex dừng ở guard amplitude): quyết định của Claude theo ủy quyền
- `ctmc._truth_allowed` chỉ cho phép amplitude của namespace `ctmc-v1` (a = 6; held-out 3 và 7,5 của L7.2; control 0). Codex dừng đúng luật,
  không bypass.
- **Quyết định:** X-CTMC dùng namespace riêng **`x-ctmc-v1`**. Truth chính xác xây trên `experiments/letter/mmpp.generator`, module letter độc
  lập, nhận amplitude liên tục. W2 đã dùng module này; docstring ghi "No change to, or monkey patch of, the CTMC implementation". **Không gọi**
  `ctmc.Chain.V` hay bất kỳ hàm nào có guard với amplitude ngoài namespace của nó. Không sửa, không monkey-patch `ctmc.py`.
- **Viết mới trong `x_ctmc.py`:**
  - (i) chain mỗi path từ `mmpp.generator(load, kappa, N, alpha, mu)`;
  - (ii) truncation N bằng `mmpp.choose_N` (đuôi < 1e-13);
  - (iii) V_a(h, x) chính xác bằng `expm_multiply`, giống cách `ctmc.Chain.V` làm (đọc code để chép thuật toán, không gọi);
  - (iv) rollout fluid M0 tổng quát theo μ_p, α_p, κ_p (công thức Eq. fluid của paper);
  - (v) posterior chính xác e^{Q_0 τ}.
- **Test đối chiếu bắt buộc** (thay test §8 đầu tiên): ở a = 6, μ = 10 và cùng κ cho hai path, `x_ctmc` khớp `ctmc.evaluate` hoặc `evaluate_m0`
  (được phép ở a = 6) trên ít nhất 2 regime cũ, sai lệch tương đối ≤ 1e-9 cho V, Δ̂, G_S, C_ref. Không đạt thì dừng.
- **Thận trọng:** loại khỏi lưới mọi regime có μ_A = μ_B = 10 và α_A = α_B ∈ {3; 7,5} (trùng held-out L7.2). Lưới dị biệt hầu như không chạm điều
  này; ghi số regime bị loại.
