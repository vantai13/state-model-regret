# I_Δ vòng 3 — kết quả run03 (14/11/2026, giờ VM 03:13–03:22 UTC)

Doan Van Tai — **AI (Claude) soạn thẻ, khóa, chạy và chấm theo ủy quyền** ("tiếp tục đi"). Không mentor review,
không author-self, không confirmation chính thức, không đổi RQ/contract/PC/Gate/G1.

- Thẻ: [CARD_IDELTA3.md](CARD_IDELTA3.md), sha256 `a02d4592…`, khớp lúc chạy và lúc chấm. Lock: 15 file.
- Code: [idelta3.py](../../../experiments/explore_ctmc/idelta3.py); test 5/5 (+14 vòng trước) PASS ở local và GCP.
- Một run trên `dt4n-research-01`: 104/104 job COMPLETED (40 regime CTMC, 64 điểm fluid × 3 h); 3.335 CPU-s.
  VM đã tắt. Chưa commit.

## 0. Trước thẻ: hai giả thuyết cơ chế đã trượt trên dữ liệu hiệu chỉnh

Trên run01 + run02 (54 regime, 28 điểm fluid, đều đã lộ), ở 7 T_int:
- T_prox = E|ẽ|/E|Δ+b|: Spearman với ρ là −0,21 (`calibration_idelta3_pass1_Tprox.json`).
- κ_Δ = |EΔ|/√E[Δ²]: Spearman +0,27 (`calibration_idelta3.json`).

Trên panel mới, hai biến này vẫn yếu: Spearman −0,16 và +0,26, chỉ báo mô tả. Ứng viên thứ ba (dấu G_S) được khóa
thành B2 ở dưới.

## 1. Chấm

| Mục | Ngưỡng | Kết quả | Verdict |
|---|---|---|---|
| C1 | Γ tự tính khớp engine | sai khác 0,0 (từng bit), 40/40 COMPLETED | PASS |
| **B1** ngoại lệ band | band ≤ 0,5 và ngoài ≥ 0,75 | 0,454 (n 14) / 1,145 (n 17) | **PASS** |
| **B2** dấu G_S | G_S>0: ≥ 70% có ρ ≤ 0,5; G_S<0: ≥ 60% có ρ ≥ 0,75 | **64%** (7/11) / 80% (16/20) | **FAIL** |
| B3 | ≥ 70% band có G_S_7T > 0 | 80% (16/20) | PASS |
| B4 (H1 ngoài band) | median ρ_1T ≤ 0,25 và ρ_7T ≥ 0,5 | 0,011 (n 13) / 1,145 (n 17) | PASS |
| **G1** fluid không đơn điệu | tỷ lệ ρ(32) > ρ(2) **dưới** 60% | **76%** (16/21; bỏ HOLD: 80%) | **FAIL** |
| G2 fluid theo mức | median ρ(2) ≤ 0,5 và ρ(32) ≥ 0,75 | 0,103 (n 30) / 0,858 (n 43) | PASS |
| G3 | κ_add tăng 2 → 32 ở ≥ 80% | 89% | PASS |
| G4 | Spearman(κ_add, ρ) ≥ 0,3 | 0,52 | PASS |

HOLD_PRECISION có ở 56/192 dòng fluid; bỏ chúng không đổi verdict nào.

## 2. Đọc theo luật đã khai

- **Ngoại lệ help band lặp lại** trên 20 regime band mới (B1, B3).
- **Quy luật theo h ngoài band lặp lại lần thứ ba** (run01 post-hoc, run02 H1, run03 B4). Ở h ≈ T_int, Γ không tái tạo
  được bằng model chỉ lệch hằng (ρ ≈ 0,01). Ở 7 T_int thì tái tạo được (ρ ≈ 1,1).
- **"Help cần sai số phụ thuộc state, harm là ngưỡng cộng bias": không đạt.** Phía harm đứng (80%), phía help trượt
  một dòng (7/11; JB0007, JB0025, JB0030 có ρ 0,73–0,96). Hướng vẫn rõ (median help 0,28 so với harm 1,08), nhưng
  theo luật thì FAIL. Help band không đồng nhất: ở một phần regime, model chỉ lệch hằng cũng tái tạo được phần giúp.
- **Fluid:** hướng theo h đứng ở mức median (G2): ρ 0,10 → 0,30 → 0,86 qua h = 2 / 8 / 32 s, κ_add 0,22 → 0,52 → 0,97.
  Tôi dự đoán sai (G1) rằng trong từng điểm ρ sẽ không tăng đều. Thực tế 76% điểm tăng, tức là phép chuyển plant mạnh
  hơn tôi kỳ vọng. Phần này không được khai trước theo hướng đó, nên chỉ là quan sát.

## 3. Tổng hợp ba vòng (run01–run03)

| Mệnh đề | Bằng chứng | Mức |
|---|---|---|
| Interaction tầng prediction (I_Δ) tồn tại, gắn với biên rỗng | run01 P2–P5; fluid P4 ngưỡng sắc | đứng (trong plant, gần như định lý) |
| Ngoài band: h ≈ T_int thì Γ cần sai số phụ thuộc state; h ≈ 7 T_int thì Γ ≈ ngưỡng + bias | run02 H1/H2, run03 B4 | đứng, lặp lại trên 2 panel mới |
| Trong help band, quy luật trên không đứng | run02 post-hoc, run03 B1/B3 | đứng, đã lặp lại có khai trước |
| Cơ chế của ngoại lệ band | T_prox, κ_Δ trượt khi hiệu chỉnh; dấu G_S (B2) trượt sát nút | **chưa có** |
| Hướng theo h chuyển sang fluid | run02 F1/F2; run03 G2/G3 (+ G1 trượt theo hướng mạnh hơn) | đứng ở mức median; chưa kiểm thang (giây ≠ T_int) |

## 4. Giới hạn

- Plant mô phỏng (CTMC a = 6, τ = 1; fluid toy contract v1.2). Γ_add là một counterfactual (b = trung bình).
- B2 là quan hệ outcome–outcome. Ngưỡng hiệu chỉnh trên ≤ 54 regime và 28 điểm fluid.
- AI soạn, khóa, chạy và tự chấm, không mentor review.
- Fluid có 29% dòng HOLD_PRECISION (ngân sách sai số so với Cref nhỏ); verdict không đổi khi bỏ chúng.
- Không novelty. Chưa có bằng chứng ở mạng hay trace thật.

## 5. File

`run03/`: `environment.json` (lock, version, sha256), `ids.json`, `jobs/<id>.json` (40 regime + 64 điểm), `score.json`,
`done.json`. Hiệu chỉnh: `calib_r3/` (lượt 1), `calib_r3b/` (lượt 2), `calibration_idelta3*.json`, log `calib_r3*_pass*.log`.
Panel: `cases_r3.json`, `fluid_points_r3.json`, `design_r3_report.json`. Log run: `results/explore_ctmc/logs/idelta_run03.log`.
