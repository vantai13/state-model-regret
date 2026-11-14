# I_Δ vòng 2 — kết quả run02 (14/11/2026, giờ VM 02:10–02:24 UTC)

Doan Van Tai — **AI (Claude) soạn thẻ, khóa, chạy và chấm theo ủy quyền** ("tự soạn thực hiện rồi tự chạy").
Không mentor review, không author-self, không confirmation chính thức, không đổi RQ/contract/PC/Gate/G1.

- Thẻ: [CARD_IDELTA2.md](CARD_IDELTA2.md), sha256 `b1968cc2…`, khớp lúc chạy và lúc chấm. Lock:
  [lock_idelta2.json](lock_idelta2.json), 14 file.
- Hiệu chỉnh trước thẻ: [calibration_idelta2.json](calibration_idelta2.json) (run01 + 4 điểm pilot fluid).
- Code: [idelta2.py](../../../experiments/explore_ctmc/idelta2.py); test 14/14 PASS ở local và GCP.
- Một run trên `dt4n-research-01`: 45/45 regime CTMC COMPLETED, 24 điểm × 4 h fluid; 3.735 CPU-s.
  Chấm tự động ngay sau run. VM đã tắt. Chưa commit.

## 1. Chấm

| Mục | Ngưỡng | Kết quả | Verdict |
|---|---|---|---|
| C1 control | identity ≤ 1e−7, tower ≤ 1e−9, Γ khớp, biên trên ≤ 1e−6 | 1,8e−11; 6,7e−15; 0 (từng bit); 4,6e−12 | PASS |
| **H1** (chính) | median ρ_lo ≤ 0,25 và median ρ_hi ≥ 0,5 | **0,114** (n 28) và **1,134** (n 35) | **PASS** |
| **H2** (chính) | ρ_hi > ρ_lo ở ≥ 60% | **82%** (23/28) | **PASS** |
| H3 | E\|I_Δ\| giảm lo→hi ở ≥ 90% | 100% (45/45); median 1,55 → 0,058 %Cref | PASS |
| H4 | κ_add tăng lo→hi ở ≥ 90% | 100% (45/45); median 0,27 → 1,00 | PASS |
| F1 | E\|I_Δ\| giảm h 8→32 ở ≥ 75% | 96% (bỏ HOLD: 89%) | PASS |
| F2 | κ_add tăng h ½→32 ở ≥ 80% | 83% (bỏ HOLD: 89%) | PASS |
| **F3** | ρ tăng ở ≥ 60%, cần ≥ 8 điểm | 5/5, nhưng chỉ 5 điểm | **NOT_EVALUABLE** |
| **F4** | median ρ ≤ 0,25 / ≥ 0,5, cần ≥ 8 điểm mỗi mức | 0,015 (n 7) / 0,909 (n 14) | **NOT_EVALUABLE** |

**Cách đọc theo luật đã khai:**
- "Đọc theo h đứng ở regime CTMC mới": **có** (H1 và H2 PASS, trên 45 regime chưa từng tính).
- "Chuyển sang fluid": **chưa chấm được** (F3/F4 thiếu điểm), dù F1/F2 PASS và hướng của ρ giống CTMC.

## 2. CTMC — số chính

ρ = Γ_add/Γ chỉ đọc khi |Γ| ≥ 0,05 pp.
- Median |Γ| tăng 0,096 → 0,618 pp từ h ≈ T_int tới 7 T_int.
- E|I_Δ| giảm 1,55 → 0,058 %Cref.
- κ_add tăng 0,27 → 1,00: ở h dài, sai số của M0 gần như hằng ở mọi state.

**Dị biệt theo stratum (mô tả, không khai trước):**

| stratum | median ρ ở T_int | median ρ ở 7 T_int | ρ_7T < 0,25 |
|---|---|---|---|
| neg (x < 0) | 0,002 | 1,20 | 2/12 |
| band (0 < x ≤ 0,35) | 0,34 | 0,37 | 4/10 |
| pos (x ≥ 0,4) | 0,13 | 1,25 | 0/13 |

Trong band, đọc theo h **không đứng**:
- Ở h dài, sai số gần như hằng (κ_add ≥ 0,98), nhưng Γ_add vẫn không tái tạo Γ (IB0005, IB0015, IB0025 có Γ < 0
  trong khi Γ_add ≈ 0).
- Ở h ≈ T_int, ba regime band đã có ρ > 0,5.
- Lý do khả dĩ, chưa kiểm: trong band nhiều state nằm sát ngưỡng quyết định, nên một phần biến thiên rất nhỏ của sai số
  vẫn lật action. κ_add đo biến thiên so với bias, không so với khoảng cách tới ngưỡng.

## 3. Fluid — mô tả

| h (s) | median \|Γ\| (pp) | median E\|I_Δ\| (%Cref) | median κ_add | n đủ điều kiện | median ρ |
|---|---|---|---|---|---|
| ½ | 0,017 | 0,44 | 0,12 | 7 | 0,015 |
| 2 | 0,038 | 3,78 | 0,23 | 10 | 0,35 |
| 8 | 0,030 | 10,05 | 0,45 | 10 | 0,37 |
| 32 | 0,785 | 0,90 | 0,94 | 14 | 0,91 |

- Hướng giống CTMC: sai số dần thành hằng, và phần "chỉ ngưỡng" tăng theo h.
- E|I_Δ| hình chuông, đỉnh ở h = 8, như pilot đã cho thấy.
- Ở h = 32, ba điểm có ρ < 0,25: FT19 (κ_add 0,10), FT24 (0,43), FT26 (|Γ| = 0,07, sát ngưỡng đọc).
  Hai điểm đầu là những điểm sai số **chưa** thành hằng, khớp với cơ chế.
- F3/F4 không chấm được là lỗi thiết kế của tôi. Ở h = ½ s, Γ fluid quá nhỏ (median 0,017 pp), nên chỉ 7 điểm qua
  ngưỡng 0,05 pp. Mức lo nên chọn h = 2 s, hoặc panel cần nhiều điểm hơn.
- 34/96 dòng fluid HOLD_PRECISION; bỏ chúng không đổi F1/F2.

## 4. Đánh giá

- **Mạnh hơn run01:** dự đoán định lượng khai trước, regime mới, chấm tự động, H1–H4 đều PASS. Mệnh đề "ở h ≈ T_int,
  Γ đến từ sai số phụ thuộc state; ở h ≈ 7 T_int, Γ chủ yếu là ngưỡng cộng bias" đứng ở CTMC cho x < 0 và x ≥ 0,4.
- **Giới hạn mới:** không đứng trong help band, đúng vùng mà các phase trước quan tâm nhất (G_S đổi dấu). Đây là
  post-hoc theo stratum, cần thẻ riêng nếu muốn khẳng định.
- **Fluid:** cùng hướng nhưng chưa có verdict chính. Muốn có cần thẻ mới, lo = 2 s và nhiều điểm hơn, không chạy lại
  run02 để cứu.
- Vẫn là plant mô phỏng; Γ_add là một counterfactual (b = trung bình); AI tự soạn và tự chấm.

## 5. File

`run02/`: `environment.json` (lock, version, sha256), `regimes/<id>.json` + `_dose.csv` (45 regime), `fluid.json`
(96 dòng), `score.json`, `done.json`; log `results/explore_ctmc/logs/idelta_run02.log`. Phần thiết kế:
`cases_fresh.json`, `fluid_points.json`, `design_fresh_report.json`, `fluid_pilot.json`.
