# L3R.6 — Hypothesis cards v1: báo cáo thực thi

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026 · DL-073–074.
Trạng thái: **CARDS_FROZEN**, freeze commit `1414d9299d767b2abd56642c4d56048867b83095`,
[receipt](../../../notes/phases/PHASE_3R_hypothesis_cards.lock.json) verify PASS.
AI (Claude) triển khai và soạn câu chữ; tác giả chọn phân suất, vùng và gói luật
([nguyên văn](author_choices.json)). Không ghi tác giả dự đoán, tự viết cơ chế hoặc read-back.

## 1. Đã làm theo thứ tự

| Bước | Commit | Nội dung |
|---|---|---|
| Công cụ + mục 0 log | `64f20ee` | CP exact, bảng verdict, luật vùng DesignView, logger; 13 luật ứng viên cố định trong code trước khi đọc outcome |
| Tóm tắt discovery + lựa chọn tác giả | `5b5760b` | Log #1–#20, DL-073, note lọc identity/prior |
| Freeze card | `1414d92` | Cards, forking log md/jsonl, claim boundary, 9 checks, code chấm |
| Receipt + hồ sơ | commit sau | Lock receipt, DL-074, tests receipt, logs, report, pointers |

Lesson Part1 bị cắt ở lần gửi đầu; tác giả đã chọn phân suất khi biết điều đó, sau đó gửi lại
Part1. Lựa chọn trùng **phương án D** của Part1 §11, không hỏi lại.

## 2. Kết quả discovery đã log (DISCOVERY, không phải evidence)

Cơ sở: pilot tag `a7435e9`, Stage1+2, c_sw=0, **162 cấu hình phân biệt** (168 ID, 6 cặp trùng chênh 0).
Bảng phủ Part2 §5.1, cặp ρA=.9, MV theo λA, SH 36/36–21/36–0/40 đều tái lập khớp.

| Luật | n | MV (ḠM≥1%) | SH (ḠS≤−1%) | Ghi chú |
|---|---:|---:|---:|---|
| **MV+A** (chọn Ω_MV⁺) | 16 | 16 | 11 | hộp vẽ quanh điểm đã thấy; chứa tọa độ R11 |
| MV+B | 24 | 20 | 16 | bỏ |
| **MV-ii** (chọn Ω_MV⁻) | 0 | — | — | ngoại suy |
| MV-i | 32 | 0 | 24 | bỏ: đối chứng gần như chắc đạt |
| MV-BND | 8 | 8 | 4 | mô tả |
| **SH+A** (chọn Ω_SH⁺) | 72 | 0 | 57 | 57/57 harm có \|ḠSM\|<.5% |
| SH+B | 108 | 20 | 73 | bỏ |
| **SH-ii** (chọn Ω_SH⁻) | 0 | — | — | ngoại suy |
| SH-i | 36 | 20 | 16 | bỏ: 0,44 không sạch |
| G-A / G-B / G-C | 16/8/36 | — | — | ḠS≥0: 3/3/18; min(ḠS,ḠM)>.5%: 1/1/3 |

Chẩn đoán Γ trên 162: Γ̄≥−.5% ở **162/162**, min Γ̄=−0,0000517% C̄; ḠS≥0 ở 73; chỉ **3/162**
có min(ḠS,ḠM)>.5%. Vì Γ̄≥−min(ḠS,ḠM) (T07 S11+S07), 70/73 cấu hình ḠS≥0 đạt “không
substitution” do identity. Đây là lý do card Γ không được cấp suất.

## 3. Card đã đóng băng

| | Hyp-MV (primary1) | Hyp-SH (primary2) |
|---|---|---|
| Metric / MEETS | ḠM/C̄ref ≥ 1/100 | ḠS/C̄ref ≤ −1/100 |
| Ω⁺ | λB=8, λA∈[7;15/2], u∈[1;3/2], κ∈[1/10;3/10], h∈[12;16] | λB∈[6;7], λA∈[7;8], u∈[1;3/2], κ∈[1/10;3/10], h∈[8;16] |
| Ω⁻ | như Ω⁺, κ∈[1;3] (ngoại suy) | như Ω⁺, κ∈[1;3] (ngoại suy) |
| Ω_BND | κ∈[3/10;1], mô tả | κ∈[3/10;1], mô tả, khai không nhìn dữ liệu |
| Gộp | π₀=1/2, CP một phía 97,5%, Bonferroni, AND | như MV, không WEAKEN theo dấu |

Measure: λ/u đều, κ/h log-đều, độc lập; làm tròn 1/1000 và h tới 1/120 s. c_sw=0 ở mọi vùng.

## 4. Chín phép kiểm và số đo

| # | Phép kiểm | Kết quả |
|---|---|---|
| 1 | Có thể sai | PASS: n=30, ≤9 MEETS ở Ω⁺ → FALSIFY với mọi Ω⁻ |
| 2 | Không phải identity | PASS: identity chỉ cho 0≤ḠM≤σ̄, \|ḠS\|≤σ̄; discovery có FAILS (MV-i 32/32, SH+A 15/72) |
| 3 | Hệ quả chung | PASS: Γ̄≥−min(ḠS,ḠM); Ω_MV (λB=8) rời Ω_SH (λB≤7) |
| 4 | Lọc prior | PASS (khai): P11/P12/AIS22/P13; K-RM1/K-RM3/V1; trục E/M/R |
| 5 | Vùng chỉ tọa độ | PASS: 6 vùng, mọi góc hợp lệ primary, biên ở giá trị lưới, ≤3 tọa độ chủ động |
| 6 | Đối chứng có thể thất bại | PASS: chỉ lật κ; Y⁻ khi ≥21/30; discovery trong Ω⁻ = 0 |
| 7 | Cơ chế | PASS có điều kiện: nguồn/độ lớn tách; **AI soạn, tác giả duyệt; bằng lời tác giả OPEN** |
| 8 | Bảng verdict phủ hết | PASS: 12 ô, đạt cả 4 verdict, 0 vi phạm; 12.400 trường hợp pipeline; 4 góc vs 2 đồng loạt khác 0 lần |
| 9 | Có thể PASS (sơ bộ) | PASS: xem bảng dưới |

P(PASS) của một primary, giả định p⁺=0,7 (thấp hơn discovery) và p⁻=0,2, không UNRESOLVED:

| n mỗi vùng | P(S⁺) | P(N⁻) | P(PASS) | P(S⁺) khi p⁺=0,5 |
|---:|---:|---:|---:|---:|
| 20 | 0,416 | 0,804 | 0,335 | 0,021 |
| 30 | 0,589 | 0,939 | **0,553** | 0,021 |
| 40 | 0,703 | 0,981 | 0,690 | 0,019 |
| 60 | 0,838 | 0,998 | 0,837 | 0,014 |

Đây là toán trên tỉ lệ giả định, không phải dự báo kết quả CF. L3R.7 chọn n sau numerics v1.3.1.

## 5. Đính chính tài liệu lesson (đã kiểm bằng rational exact)

- Part3 §16(b): Ω⁻ 20/30 có cận dưới 97,5% = **0,472** < 0,5 (P(X≥20\|½)=0,0494) → U⁻ →
  **WEAKEN-W2**, không phải W1. Card dùng kết quả toán đúng.
- Part1 §9.2: cận đúng là **Γ̄≥−min(ḠS,ḠM)**, không chỉ −ḠM; substitution còn bị ḠS chặn.
  Tự kiểm 3: ḠS=.1%, ḠS\|M1=.2% ⇒ Γ̄=.1% xác định.
- Part2 §8.3: h=2 là **0/30** (κ .3/1/3), không 0/20. §8.1: góc λA=8 có 1/12 cấu hình λB=7 ḠM>.09%.
- R4 “hai kịch bản đồng loạt” không phải hai cực khi Ω⁻ cũng có UNRESOLVED; card dùng bốn góc
  (nghiêm hơn), trên lưới quét không đổi verdict.
- Khớp: CP 21/30=.506; bảng 5.4 (k=15/21/27); ví dụ AND .589×.939≈.553; bảng Γ 5.5; bảng phủ 5.1.

## 6. Lệnh đã chạy

```bash
.venv/bin/python -m experiments.R3R_05_contract.freeze                    # PASS trước và sau
.venv/bin/python -m pytest tests/test_r3r_06_cards.py -q                  # 15 → 17/17 PASS
.venv/bin/python -m experiments.R3R_06_cards.run_discovery --entry0
.venv/bin/python -m experiments.R3R_06_cards.run_discovery --part-a       # log #1–#6
.venv/bin/python -m experiments.R3R_06_cards.run_discovery --candidates   # log #7–#19
.venv/bin/python -m experiments.R3R_06_cards.run_discovery --decision     # log #20
.venv/bin/python -m experiments.R3R_06_cards.check_cards                  # 9/9 + 7 extra PASS
.venv/bin/python -m experiments.R3R_06_cards.render_log
.venv/bin/python -m experiments.R3R_06_cards.verify_cards --create 1414d92…   # receipt
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_6/logs/full_suite.xml   # 549/549
```

Lỗi trong phiên: test bài (b) ban đầu viết theo đáp án lesson (W1) và **FAIL**; kiểm lại cho thấy
đáp án lesson sai, test sửa theo toán exact. Không có lỗi engine (không gọi engine).

## 7. File

Source: [stats](../../../experiments/R3R_06_cards/stats.py), [verdict](../../../experiments/R3R_06_cards/verdict.py),
[regions](../../../experiments/R3R_06_cards/regions.py), [discovery](../../../experiments/R3R_06_cards/discovery.py),
[run_discovery](../../../experiments/R3R_06_cards/run_discovery.py), [check_cards](../../../experiments/R3R_06_cards/check_cards.py),
[verify_cards](../../../experiments/R3R_06_cards/verify_cards.py), [render_log](../../../experiments/R3R_06_cards/render_log.py),
[tests](../../../tests/test_r3r_06_cards.py).
Data: [forking_paths.jsonl](forking_paths.jsonl), [part_a.json](discovery/part_a.json),
[candidates.json](discovery/candidates.json), [card_checks.json](card_checks.json), [author_choices.json](author_choices.json).
Logs: [targeted](logs/targeted_tests.log), [full suite](logs/full_suite.log) + [xml](logs/full_suite.xml),
[contract verify](logs/contract_freeze_verify.log), [receipt verify](logs/card_receipt_verify.log).
Notes: [cards](../../../notes/phases/PHASE_3R_hypothesis_cards.md), [forking paths](../../../notes/phases/PHASE_3R_forking_paths.md),
[lọc identity/prior](../../../notes/lessons/L3R.6_identity_prior_filter.md), [claim boundary](../../../notes/01_claim_boundary_v1_3.md).
Không tạo chart/PDF, không literature search, không tag mới.

## 8. Ý nghĩa và giới hạn

Đã xác nhận: card có thể sai, có thể PASS ở n khả thi theo giả định, vùng chỉ dùng tọa độ, bảng
verdict phủ hết, thứ tự commit đúng (công cụ → tóm tắt → lựa chọn → freeze → receipt). Chưa xác nhận:
hypothesis đúng/sai, cơ chế, realism, novelty. “Interact” chỉ mô tả. Ω⁻ là ngoại suy; κ=3/h=16
là góc số khó, cần numerics v1.3.1 phủ. Phép7 bằng lời tác giả và Understanding OPEN.
L3R.7 được học; thực thi rút mẫu chờ numerics v1.3.1. Phase4 HOLD; G1 không đổi.
