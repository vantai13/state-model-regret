# EV-TE independent rescore

**MISMATCH**

Người phụ trách: Doan Van Tai.

Đã tính độc lập bằng NumPy/stdlib trước khi mở score.json và score_cells.csv; không đọc/import ev_te, ev_te_score_post.py hoặc score_attempt01_failed/.

61 regimes × 4 ages = 244 cells; 49 regimes hợp lệ = 196 cells; 732 dòng theo twin và 1464 dòng theo horizon. N=500, seed B=1000001; paired SE dùng ddof=1, ghép từng instance h30−h7.

| Test | Passed/eligible (độc lập) | Claude | Fraction | Verdict |
|---|---:|---:|---:|---|
| H1 | 195/196 | 195/196 | 99.489795918% | PASS |
| H2 | 192/192 | 192/192 | 100.000000000% | PASS |
| H3 | 183/192 | 183/192 | 95.312500000% | PASS |
| H4 | 191/196 | 191/196 | 97.448979592% | PASS |

Tổng H1–H4 khớp; không thay đổi eligibility hay ngưỡng CARD. Cell là denominator, không phải trial độc lập; không suy population CI hoặc novelty.

Sai khác số lớn nhất: **7937820.3064649524**, trường `score_cells.csv.Gamma`, key `['A2_r90_b6_s1', 0.1, 30]`.
Bỏ hai trường dấu Γ: sai khác lớn nhất `2.9802322387695312e-07` tại `score_cells.csv.pred_CE_pp`; tolerance đối chiếu abs=1e-10, rel=1e-12.

CARD §3 không định nghĩa công thức GM/Γ. Bản tính độc lập đầu dùng Γ=L00−L10−L01+L11; score dùng dấu ngược lại trên dữ liệu này. Giữ nguyên quy ước độc lập đã tính trước khi mở score; khác biệt này không chứng minh scorer sai.
Residual nếu đối chiếu Γ độc lập với −Γ score: `{'Gamma': 1.1641532182693481e-10, 'z_Gamma': 1.1641532182693481e-10}`.

Cờ eligibility/pass sau khi quy về cùng nghĩa JSON: 0 mismatch. Có 184 khác biệt giữa pass có gộp eligibility trong bản đầu và pass predicate riêng của score; không làm đổi bất kỳ count nào.
Structural mismatches: 0. Self-checks: PASS (7 checks).

## Đối chiếu từng trường

| Field | Số so sánh | Max absolute difference | Mismatches |
|---|---:|---:|---:|
| score.json.cells.H1_eligible | 244 | — | 0 |
| score.json.cells.H1_pass | 244 | — | 0 |
| score.json.cells.H2_eligible | 244 | — | 0 |
| score.json.cells.H2_pass | 244 | — | 0 |
| score.json.cells.H3_eligible | 244 | — | 0 |
| score.json.cells.H3_pass | 244 | — | 0 |
| score.json.cells.H4_eligible | 244 | — | 0 |
| score.json.cells.H4_pass | 244 | — | 0 |
| score.json.cells.regime | 244 | — | 0 |
| score.json.cells.stationary_rate_valid | 244 | — | 0 |
| score.json.cells.tau_mult | 244 | 0 | 0 |
| score.json.descriptive_harm.CE | 1 | 0 | 0 |
| score.json.descriptive_harm.M0 | 1 | 0 | 0 |
| score.json.descriptive_harm.P | 1 | 0 | 0 |
| score.json.hypotheses.H1.eligible | 1 | 0 | 0 |
| score.json.hypotheses.H1.fraction | 1 | 0 | 0 |
| score.json.hypotheses.H1.passed | 1 | 0 | 0 |
| score.json.hypotheses.H1.threshold | 1 | 0 | 0 |
| score.json.hypotheses.H1.verdict | 1 | — | 0 |
| score.json.hypotheses.H2.eligible | 1 | 0 | 0 |
| score.json.hypotheses.H2.fraction | 1 | 0 | 0 |
| score.json.hypotheses.H2.passed | 1 | 0 | 0 |
| score.json.hypotheses.H2.threshold | 1 | 0 | 0 |
| score.json.hypotheses.H2.verdict | 1 | — | 0 |
| score.json.hypotheses.H3.eligible | 1 | 0 | 0 |
| score.json.hypotheses.H3.fraction | 1 | 0 | 0 |
| score.json.hypotheses.H3.passed | 1 | 0 | 0 |
| score.json.hypotheses.H3.threshold | 1 | 0 | 0 |
| score.json.hypotheses.H3.verdict | 1 | — | 0 |
| score.json.hypotheses.H4.eligible | 1 | 0 | 0 |
| score.json.hypotheses.H4.fraction | 1 | 0 | 0 |
| score.json.hypotheses.H4.passed | 1 | 0 | 0 |
| score.json.hypotheses.H4.threshold | 1 | 0 | 0 |
| score.json.hypotheses.H4.verdict | 1 | — | 0 |
| score.json.n_cells | 1 | 0 | 0 |
| score_cells.csv.C_ref | 1464 | 4.6566128730773926e-09 | 0 |
| score_cells.csv.Delta_CE_meas_pp | 1464 | 1.1641532182693481e-10 | 0 |
| score_cells.csv.Delta_CE_pred_pp | 1464 | 1.1641532182693481e-10 | 0 |
| score_cells.csv.Delta_CE_se_pp | 1464 | 4.5474735088646412e-12 | 0 |
| score_cells.csv.Delta_M0_meas_pp | 1464 | 8.7311491370201111e-11 | 0 |
| score_cells.csv.Delta_M0_pred_pp | 1464 | 8.7311491370201111e-11 | 0 |
| score_cells.csv.Delta_M0_se_pp | 1464 | 2.7284841053187847e-12 | 0 |
| score_cells.csv.Delta_P_meas_pp | 1464 | 2.7284841053187847e-12 | 0 |
| score_cells.csv.Delta_P_pred_pp | 1464 | 1.3642420526593924e-12 | 0 |
| score_cells.csv.Delta_P_se_pp | 1464 | 2.7284841053187847e-12 | 0 |
| score_cells.csv.E_stay | 1464 | 0 | 0 |
| score_cells.csv.GM | 1464 | 0 | 0 |
| score_cells.csv.GM_se | 1464 | 0 | 0 |
| score_cells.csv.GS_CE | 1464 | 0 | 0 |
| score_cells.csv.GS_CE_se | 1464 | 0 | 0 |
| score_cells.csv.GS_M0 | 1464 | 0 | 0 |
| score_cells.csv.GS_M0_se | 1464 | 0 | 0 |
| score_cells.csv.GS_P | 1464 | 0 | 0 |
| score_cells.csv.GS_P_se | 1464 | 0 | 0 |
| score_cells.csv.Gamma | 1464 | 7937820.3064649524 | 1393 |
| score_cells.csv.Gamma_se | 1464 | 1.4551915228366852e-11 | 0 |
| score_cells.csv.L_CE_old | 1464 | 5.5879354476928711e-09 | 0 |
| score_cells.csv.L_M0_new | 1464 | 6.5192580223083496e-09 | 0 |
| score_cells.csv.L_M0_old | 1464 | 4.6566128730773926e-09 | 0 |
| score_cells.csv.L_M1_new | 1464 | 4.6566128730773926e-09 | 0 |
| score_cells.csv.L_M1_old | 1464 | 4.6566128730773926e-09 | 0 |
| score_cells.csv.L_P_old | 1464 | 3.7252902984619141e-09 | 0 |
| score_cells.csv.N | 1464 | 0 | 0 |
| score_cells.csv.h_mult | 1464 | 0 | 0 |
| score_cells.csv.pred_CE_pp | 1464 | 2.9802322387695312e-07 | 0 |
| score_cells.csv.pred_M0_pp | 1464 | 1.4551915228366852e-10 | 0 |
| score_cells.csv.pred_P_pp | 1464 | 7.2759576141834259e-12 | 0 |
| score_cells.csv.regime | 1464 | — | 0 |
| score_cells.csv.tau_mult | 1464 | 0 | 0 |
| score_cells.csv.z_GM | 1464 | 2.9103830456733704e-11 | 0 |
| score_cells.csv.z_GM_se | 1464 | 2.7284841053187847e-12 | 0 |
| score_cells.csv.z_GS_CE | 1464 | 8.7311491370201111e-11 | 0 |
| score_cells.csv.z_GS_CE_se | 1464 | 5.4569682106375694e-12 | 0 |
| score_cells.csv.z_GS_M0 | 1464 | 1.1641532182693481e-10 | 0 |
| score_cells.csv.z_GS_M0_se | 1464 | 3.637978807091713e-12 | 0 |
| score_cells.csv.z_GS_P | 1464 | 4.5474735088646412e-12 | 0 |
| score_cells.csv.z_GS_P_se | 1464 | 4.5474735088646412e-12 | 0 |
| score_cells.csv.z_Gamma | 1464 | 570609.98238057678 | 1393 |
| score_cells.csv.z_Gamma_se | 1464 | 3.637978807091713e-12 | 0 |

## Lệnh và artifacts

```bash
source .venv/bin/activate
PYTHONDONTWRITEBYTECODE=1 python experiments/ext_validity/ev_te_rescore.py --compute-only
PYTHONDONTWRITEBYTECODE=1 python experiments/ext_validity/ev_te_rescore.py
```

Lượt đầu compute-only dừng ở assert lưới h/Tint chính xác; raw dùng integer dt steps. Sửa kiểm tra lưới theo rounding ≤dt/2 và kiểm h=steps×dt; lần compute-only sau PASS. Không thay raw data hoặc số đo.

Lượt xuất thử có lỗi ở adapter CSV: chuẩn hóa increment theo horizon của dòng thay vì Cref(h30). Đã sửa theo công thức CARD §3 và tái xuất các file mới của nhiệm vụ; hash số H1–H4/từng twin giữ nguyên. Không sửa dấu Γ sau đối chiếu.

Script: `experiments/ext_validity/ev_te_rescore.py`.
JSON: `results/ext_validity/ev_te/rescore_independent.json` (giá trị từng cell/horizon, toàn bộ sai khác và SHA-256 inputs).
Report: `results/ext_validity/ev_te/rescore_independent.md`. Không tạo CSV/log riêng; log thực thi hiển thị trong phiên.

SHA-256 số độc lập trước đối chiếu: `bd2c4d63b2cd0bae1cb0f7084792276bfb6255f64c8e67db388bb6efe73c9b29`.

Không commit, không SSH, không sửa file đã có trước nhiệm vụ. Đây là rescore raw truth đã có, không chạy lại simulation.
