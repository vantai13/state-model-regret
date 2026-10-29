# Phase 3R — Hypothesis cards v1 (L3R.6)

Người phụ trách: **Doan Van Tai** · 29/10/2026 · contract-v1.3 (`3d2359b`) · DL-073–074.
Trạng thái: **FROZEN — card set v1, trước mọi frame/sample/outcome CF của L3R.7**.

> **Provenance.** AI (Claude) soạn toàn bộ câu chữ, luật chấm và dòng cơ chế theo yêu cầu triển
> khai L3R.6. Tác giả **duyệt** bằng lựa chọn nguyên văn: phân suất D, vùng MV+A/SH+A với đối chứng
> lật κ, gói luật “theo lesson, AI soạn” ([record](../../results/lessons/l3r_6/author_choices.json)).
> Repo **không** ghi “tác giả dự đoán” hay “cơ chế bằng lời tác giả”; Understanding/read-back OPEN.
> Card vẫn là prereg hợp lệ vì commit trước mọi dữ liệu CF.

<!-- L3R6_CARDS
{
 "card_set_id": "L3R6",
 "version": 1,
 "status": "FROZEN",
 "responsible": "Doan Van Tai",
 "date": "2026-10-29",
 "contract": "contract-v1.3",
 "contract_commit": "3d2359b32d7bd24f9e9072d5b5b8131bd33fffa0",
 "allocation": {"primary": ["Hyp-MV", "Hyp-SH"], "secondary": null, "lesson_option": "D",
                "Gamma": "DIAGNOSTIC_ONLY", "MI": "PHASE5_NULL_ROLE"},
 "family": {"method": "bonferroni", "primaries": 2, "alpha_each": "1/40", "familywise": "1/20",
            "within_card": "intersection_union_AND_no_alpha_split"},
 "provenance": {"drafted_by": "AI (Claude)", "author_role": "selected allocation, regions and rule package verbatim",
                "author_predicted": false, "mechanism_author_words": false,
                "author_choices": "results/lessons/l3r_6/author_choices.json",
                "author_choices_sha256": "6ee1f1d23d91d7e122463e488c98459973e1bf0b87f39aa39fceefe8d8bde9c1"},
 "forking_log": {"path": "results/lessons/l3r_6/forking_paths.jsonl", "entries": 22, "rules_summarized": 13,
                 "rules_declared_without_data": 1,
                 "sha256": "a0833ab21cec40b7aedad346d741bf99102f8ebf614d001c90ea46aa1a02b728"},
 "discovery_basis": {"pilot_commit": "a7435e9a3cb0d1625479c942041ec6748444014a", "stages": ["stage1", "stage2"],
                     "c_sw": "0", "distinct_configs": 162, "label": "DISCOVERY_ADAPTIVE_NOT_EVIDENCE"},
 "regions": {
  "MV+A": {"role": "MV_plus", "scored": true,
           "bounds": {"lambdaA": ["7", "15/2"], "lambdaB": ["8", "8"], "u": ["1", "3/2"], "kappa": ["1/10", "3/10"], "h": ["12", "16"], "c_sw": ["0", "0"]},
           "active": ["lambdaB", "kappa", "h"], "scope": ["lambdaA", "u", "c_sw"],
           "coverage": "INTERPOLATION between pilot grid points lambdaA{7,15/2} u{1,3/2} kappa{1/10,3/10} h{12,16}; discovery 16/16 MV in a box drawn around seen points",
           "measure": {"lambdaA": "uniform", "u": "uniform", "kappa": "log_uniform", "h": "log_uniform"}},
  "MV-ii": {"role": "MV_minus", "scored": true,
           "bounds": {"lambdaA": ["7", "15/2"], "lambdaB": ["8", "8"], "u": ["1", "3/2"], "kappa": ["1", "3"], "h": ["12", "16"], "c_sw": ["0", "0"]},
           "flips": "kappa", "coverage": "EXTRAPOLATION: no pilot configuration in this box",
           "measure": {"lambdaA": "uniform", "u": "uniform", "kappa": "log_uniform", "h": "log_uniform"}},
  "MV-BND": {"role": "MV_bnd", "scored": false,
           "bounds": {"lambdaA": ["7", "15/2"], "lambdaB": ["8", "8"], "u": ["1", "3/2"], "kappa": ["3/10", "1"], "h": ["12", "16"], "c_sw": ["0", "0"]},
           "coverage": "only kappa=3/10 edge seen", "measure": {"lambdaA": "uniform", "u": "uniform", "kappa": "log_uniform", "h": "log_uniform"}},
  "SH+A": {"role": "SH_plus", "scored": true,
           "bounds": {"lambdaA": ["7", "8"], "lambdaB": ["6", "7"], "u": ["1", "3/2"], "kappa": ["1/10", "3/10"], "h": ["8", "16"], "c_sw": ["0", "0"]},
           "active": ["lambdaB", "kappa", "h"], "scope": ["lambdaA", "u", "c_sw"],
           "coverage": "INTERPOLATION between pilot grid points lambdaA{7,15/2,8} lambdaB{6,7} u{1,3/2} kappa{1/10,3/10} h{8,12,16}; discovery 57/72 SH",
           "measure": {"lambdaA": "uniform", "lambdaB": "uniform", "u": "uniform", "kappa": "log_uniform", "h": "log_uniform"}},
  "SH-ii": {"role": "SH_minus", "scored": true,
           "bounds": {"lambdaA": ["7", "8"], "lambdaB": ["6", "7"], "u": ["1", "3/2"], "kappa": ["1", "3"], "h": ["8", "16"], "c_sw": ["0", "0"]},
           "flips": "kappa", "coverage": "EXTRAPOLATION: no pilot configuration in this box",
           "measure": {"lambdaA": "uniform", "lambdaB": "uniform", "u": "uniform", "kappa": "log_uniform", "h": "log_uniform"}},
  "SH-BND": {"role": "SH_bnd", "scored": false,
           "bounds": {"lambdaA": ["7", "8"], "lambdaB": ["6", "7"], "u": ["1", "3/2"], "kappa": ["3/10", "1"], "h": ["8", "16"], "c_sw": ["0", "0"]},
           "coverage": "declared without data look; only kappa=3/10 edge seen", "measure": {"lambdaA": "uniform", "lambdaB": "uniform", "u": "uniform", "kappa": "log_uniform", "h": "log_uniform"}}
 },
 "measure_rules": {"independent_coordinates": true, "pinned": "coordinates with lo=hi are fixed",
                   "rounding": {"lambdaA": "1/1000", "lambdaB": "1/1000", "u": "1/1000", "kappa": "1/1000", "h": "1/120"},
                   "rounding_mode": "nearest multiple, ties to even multiple; bounds are multiples so draws stay in the closed box",
                   "collisions": "exact-key collisions with seen coordinates handled by the L3R.7 prereg rule fixed before sampling; never by outcome",
                   "L3R7_chooses": ["n per scored region", "seed", "collision mechanics", "numerical levels via v1.3.1"]},
 "cards": {
  "Hyp-MV": {"slot": "primary", "slot_index": 1, "metric": "G_M/Cref_bar", "criterion": "effect",
             "relation": ">=", "threshold": "1/100", "r6_boundary": "1/100",
             "regions": {"plus": "MV+A", "minus": "MV-ii", "bnd": "MV-BND"},
             "aggregate": {"pi0": "1/2", "bound": "clopper_pearson_one_sided", "alpha": "1/40", "decision": "exact_binomial_tail"},
             "verdict_map": "primary_v1", "r4": "four_corners", "r5_umax": "1/10", "scored_regions": ["plus", "minus"]},
  "Hyp-SH": {"slot": "primary", "slot_index": 2, "metric": "G_S/Cref_bar", "criterion": "harm",
             "relation": "<=", "threshold": "-1/100", "r6_boundary": "-1/100",
             "regions": {"plus": "SH+A", "minus": "SH-ii", "bnd": "SH-BND"},
             "aggregate": {"pi0": "1/2", "bound": "clopper_pearson_one_sided", "alpha": "1/40", "decision": "exact_binomial_tail"},
             "verdict_map": "primary_v1", "r4": "four_corners", "r5_umax": "1/10", "scored_regions": ["plus", "minus"],
             "no_sign_weaken": true}
 },
 "per_regime": {"label_order": ["UNDEFINED if Cref_bar=0", "UNRESOLVED if R1 not ready after R3 budget",
                                "UNRESOLVED if |z-boundary| <= d (R6) unless certified exact", "MEETS/FAILS by relation"],
                "d": "max over coarse_K and coarse_dt neighbours of R1 delta for the card metric at the final level",
                "undefined": "excluded from N, counted and reported"},
 "verdict_maps": {"primary_v1": {
   "plus_states": {"S": "CP lower(1-alpha) > pi0", "R": "CP upper(1-alpha) < pi0", "U_hi": "else and k/n > pi0", "U_lo": "else and k/n <= pi0"},
   "minus_states": {"N": "CP upper(1-alpha) < pi0", "Y": "CP lower(1-alpha) > pi0", "U": "else"},
   "table": {"S|N": "PASS", "S|U": "WEAKEN-W2", "S|Y": "WEAKEN-W1",
             "U_hi|N": "WEAKEN-W3", "U_hi|U": "WEAKEN-W3", "U_hi|Y": "WEAKEN-W1",
             "U_lo|N": "INCONCLUSIVE-PRECISION", "U_lo|U": "INCONCLUSIVE-PRECISION", "U_lo|Y": "INCONCLUSIVE-PRECISION",
             "R|N": "FALSIFY", "R|U": "FALSIFY", "R|Y": "FALSIFY"},
   "order": ["validity step 0", "R5 per scored region", "R4 four corners", "table"],
   "r4_combine": "same class kept (codes united); FALSIFY mixed with any other -> INCONCLUSIVE; else least favourable of PASS>WEAKEN>INCONCLUSIVE with R4_DOWNGRADE",
   "implementation": "experiments/R3R_06_cards/verdict.py"}},
 "validity_step0": ["controls exact zero (contract §5 stop controls)", "anchors X2065/X1008/X1009 replay per v1.3.1",
                    "numerics freeze v1.3.1 closed with receipts", "this card receipt and CF list verified before engine",
                    "R5 u_max per scored region"],
 "sealed": {"R09_R10_inside_any_region": false},
 "v12_cells_inside": {"MV+A": ["R11"], "MV-BND": ["R11"]}
}
-->

Trạng thái exposure: card viết sau khi xem discovery pilot đã lộ (forking log #0–#21);
**chưa có J, gap, regret, contrast hoặc outcome nào của regime CF**, vì CF chưa được sinh.
R09/R10 không nằm trong vùng nào và vẫn niêm phong. Tọa độ R11 (đã mở ở A05-T) nằm trong
MV+A/MV-BND; L3R.7 loại tuple trùng chính xác, không coi khoảng cách nhỏ là độc lập.

Quy tắc sửa: không amend/rebase/force qua freeze commit. Không sửa phần đã khóa; muốn đổi
vùng/measure/ngưỡng/bảng verdict phải tạo card v2 + DL mới trước khi L3R.7 viết frame, và
ghi rõ đã thấy gì. Sau khi có bất kỳ outcome CF nào, không có card v2 cho dữ liệu đó.

## 1. Phân suất và những gì không được kiểm

| Suất | Card | Đại lượng | Ghi chú |
|---|---|---|---|
| Primary 1 | **Hyp-MV** | ḠM/C̄ref | Model repair dưới state cũ (S0), không dùng ḠM\|S1 |
| Primary 2 | **Hyp-SH** | ḠS/C̄ref | State repair (backlog + mode oracle) dưới M0 |
| Secondary | — | — | Phương án D: không cấp |

“Interact” **chỉ mô tả** qua Γ̄: Γ̄≥−min(ḠS,ḠM) nên substitution vượt ε_E đòi cả ḠS và ḠM
>.5%; discovery chỉ có 3/162 cấu hình như vậy ([note lọc](../lessons/L3R.6_identity_prior_filter.md)).
Không nói “hai repair bổ trợ” hay “không substitution” như kết quả. Hyp-MI chuyển Phase5 làm null.

## 2. Hyp-MV · PRIMARY 1/2 · contract-v1.3 · v1 · 29/10/2026 · FROZEN

```text
Câu một dòng : Khi B gần bão hòa (λB=8), mode nền đổi nhanh so với tuổi observation
               (κ∈[0,1;0,3]) và horizon dài (h∈[12;16] s), sửa model (mean rollout → expected
               cost thật, cùng posterior D, cùng θ) giảm regret kỳ vọng P1 ít nhất εR=1% C̄ref
               ở đa số regime của Ω_MV⁺, KHI STATE VẪN CŨ; ở Ω_MV⁻ (chỉ lật κ∈[1;3]) thì không.
Observation  : ḠM≥1% chỉ ở λB=8 (20/162 cấu hình), Stage2 chọn sau Stage1; trong Ω⁺ discovery 16/16
               (hộp vẽ quanh điểm đã thấy). κ lẫn với h: κ≥1 chỉ từng thử ở h≤8 (log #1–#3).
Mechanism    : NGUỒN (cấu trúc) = clipping max(0,·) tại biên rỗng: nếu không đường nào chạm rỗng,
               fluid tuyến tính theo arrivals nên mean rollout đúng expected cost và M0=M1
               (MASTER PLAN F9; Step1 P(a) PASS). ĐIỀU DỰ BÁO ĐỘ LỚN = chưa rõ; ứng viên hậu nghiệm
               Step1 (DL-063: M0 phóng đại phản ứng của B sau Switch hơn A ở snapshot biên tương đối nhỏ)
               CHƯA KIỂM; lens “sai số tại biên” đã FAIL (P(c)). Chưa có cơ chế đã kiểm cho vai trò κ.
Vùng         : Ω⁺ = MV+A: λB=8; λA∈[7;7,5]; u∈[1;1,5]; κ∈[0,1;0,3]; h∈[12;16]; c_sw=0
               Ω⁻ = MV-ii: như Ω⁺ nhưng κ∈[1;3] — NGOẠI SUY (pilot chưa có cấu hình nào)
               Ω_BND = MV-BND: κ∈[0,3;1] — chỉ mô tả
               Chủ động: λB, κ, h. Phạm vi: λA, u, c_sw. Nội suy: λA, u, κ, h liên tục giữa điểm lưới.
Measure      : λA, u đều; κ, h log-đều trong dải; độc lập; làm tròn λA/u/κ tới 1/1000, h tới 1/120 s
Per-regime   : MEETS ⇔ ḠM/C̄ref ≥ 1/100; R6 biên +1/100; UNDEFINED nếu C̄ref=0;
               UNRESOLVED nếu R1 chưa đạt sau ngân sách R3 hoặc |z−.01|≤d
Gộp          : π₀=1/2; Clopper–Pearson một phía 97,5% (α=1/40, Bonferroni 2 primary), quyết
               bằng đuôi nhị thức exact; Ω⁺ và Ω⁻ cùng được chấm (AND, không chia α)
Verdict      : bước0 validity → R5 (u_max=1/10 mỗi vùng) → R4 bốn góc → bảng primary_v1 (§4)
Phụ (mô tả)  : P(flip) Ω⁺/Ω⁻/BND; tỉ lệ regime có E_π[Δ̂−Δ]<0 — HƯỚNG CHƯA DỰ ĐOÁN, CHỈ ĐO
               (Jensen chỉ nói M0 ước thấp từng action, không nói dấu của Δ̂−Δ); %stakes ḠM/σ̄;
               quantile 10/50/90 của ḠM/C̄ref; số MEETS ở εR .5%/2% (không lật verdict); Γ̄ diagnostic
Identity     : ḠM≥0 (S08); ḠM≤σ̄ (S09) — không phải prediction
Coupling     : Γ̄≥−min(ḠS,ḠM); Ω_MV và Ω_SH rời nhau (λB=8 vs [6;7]) nên không chung regime
Prior        : P11 §2.4 (EVMI); P12/AIS22 (value equivalence, model đủ cho quyết định); P13 (horizon)
               · khác ở E (regret P1 với observation cũ, cùng posterior), M (mean rollout từng state vs
               expected cost thật, cùng θ), R (rerouting làm đổi tải). Rủi ro hiển nhiên “gần bão hòa
               thì nhạy” → đối chứng giữ λB=8, chỉ lật κ.
Không được nói: “model quan trọng hơn state” nói chung; “telemetry”; tần suất ngoài đời/prevalence;
               cơ chế đã chứng minh; “M0 nghiêng về Switch”; “MV cần κ nhỏ” trước CF.
Realism      : UNSOURCED (envelope v1, HOLD_UNSOURCED) · Scope: câu phạm vi contract v1.3 §6
Provenance   : AI soạn, tác giả duyệt (DL-073) · hash: receipt PHASE_3R_hypothesis_cards.lock.json
```

## 3. Hyp-SH · PRIMARY 2/2 · contract-v1.3 · v1 · 29/10/2026 · FROZEN

```text
Câu một dòng : Khi B còn headroom (λB∈[6;7]) và mode nền đổi nhanh so với tuổi observation
               (κ∈[0,1;0,3]), với h∈[8;16] s, state repair (backlog + mode oracle tại t0) dưới M0 cố
               định làm TĂNG regret kỳ vọng P1 ít nhất εR=1% C̄ref (ḠS/C̄ref≤−1%) ở đa số regime của
               Ω_SH⁺; ở Ω_SH⁻ (chỉ lật κ∈[1;3]) thì không.
Observation  : harm 77/162 (λB6/7/8: 36/21/20); trong Ω⁺ discovery 57/72; λB≤7 chỉ từng thử κ≤.3,h≥8.
Mechanism    : NGUỒN ứng viên = “lỗi bù trừ” (S5): dưới S0 với κ nhỏ, mode tại t0 gần độc lập với Y cũ nên
               M0 lấy kỳ vọng forecast qua posterior và lỗi theo state của M0 bị trung bình hóa
               (L̄00≈L̄01≈L̄11); S1 lộ backlog+mode nên M0 quyết theo lỗi của từng state, trả giá ≈ḠM|S1.
               Đối chứng: κ lớn → Y cũ đã mang thông tin mode, S0 gần S1 hơn, harm có thể giảm.
               ĐIỀU DỰ BÁO ĐỘ LỚN = chưa rõ. Toàn bộ là ứng viên, CHƯA KIỂM.
Vùng         : Ω⁺ = SH+A: λB∈[6;7]; λA∈[7;8]; u∈[1;1,5]; κ∈[0,1;0,3]; h∈[8;16]; c_sw=0
               Ω⁻ = SH-ii: như Ω⁺ nhưng κ∈[1;3] — NGOẠI SUY (pilot chưa có cấu hình nào)
               Ω_BND = SH-BND: κ∈[0,3;1] — chỉ mô tả, khai không nhìn dữ liệu
               Chủ động: λB, κ, h. Phạm vi: λA, u, c_sw. Nội suy liên tục giữa điểm lưới.
Measure      : λA, λB, u đều; κ, h log-đều; độc lập; làm tròn như Hyp-MV
Per-regime   : MEETS ⇔ ḠS/C̄ref ≤ −1/100; R6 biên −1/100; UNDEFINED nếu C̄ref=0; UNRESOLVED như Hyp-MV
Gộp/Verdict  : như Hyp-MV (π₀=1/2, 97,5%, primary_v1, R4 bốn góc, R5). KHÔNG có WEAKEN theo dấu.
Phụ (mô tả)  : tỉ lệ ḠS<0 ở Ω⁺/Ω⁻ (khai trước, không vào verdict); trong các regime MEETS của Ω⁺,
               tỉ lệ có |ḠSM|/C̄ref<εE, dự đoán phụ “đa số” (báo kèm CP, không chấm); ḠM|S1 so |ḠS|;
               D22 F̄/V̄ chỉ khi D22 đã implement+audit, nếu không thì null (không gán cb0=0)
Identity     : ḠS<0 ⇒ Γ̄≥|ḠS| và ḠM|S1≥|ḠS|+ḠM (S12) — hệ quả, không báo như kết quả; |ḠS|≤σ̄ (S14);
               F̄+V̄=ḠS (S16)
Coupling     : rời Ω_MV; Γ̄>0 trong vùng harm là đại số
Prior        : K-RM1 (R02 §5 Ex1: thông tin làm hại policy xấp xỉ), K-RM3 (R04: điều kiện đủ không hại),
               toy V1 (information_harm) · khác ở M (lộ backlog+mode dưới M0 cố định, cùng θ), E (regret P1),
               R (rerouting đổi tải). Không claim “thông tin có thể hại” là mới; chỉ claim ở đâu/bao nhiêu.
               Ánh xạ vùng harm ↔ vi phạm điều kiện R04 là suy luận của lesson, chưa kiểm.
Không được nói: “telemetry tươi có hại”; “fresh state có hại”; harm do backlog tươi (trước D22);
               prevalence ngoài đời; “state và model bổ trợ” như finding; “SH không xảy ra ở κ≥1” trước CF.
Realism      : UNSOURCED (envelope v1, HOLD_UNSOURCED) · Scope: câu phạm vi contract v1.3 §6
Provenance   : AI soạn, tác giả duyệt (DL-073) · hash: receipt PHASE_3R_hypothesis_cards.lock.json
```

## 4. Bảng verdict primary_v1 (dùng chung hai card)

Bước 0: control/anchor/numerics v1.3.1/receipt lỗi → INCONCLUSIVE (validity, mã lý do).
R5: trong Ω⁺ hoặc Ω⁻, N_eligible=0 hoặc UNRESOLVED/N_eligible>1/10 → INCONCLUSIVE (validity).
Trạng thái vùng dùng α=1/40, π₀=1/2. Ω⁺: S (cận dưới>π₀), R (cận trên<π₀), U_hi/U_lo theo p̂.
Ω⁻: N (cận trên<π₀), Y (cận dưới>π₀), U.

| Ω⁺ \ Ω⁻ | N | U | Y |
|---|---|---|---|
| S | **PASS** | WEAKEN-W2 | WEAKEN-W1 |
| U, p̂⁺>½ | WEAKEN-W3 | WEAKEN-W3 | WEAKEN-W1 |
| U, p̂⁺≤½ | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| R | **FALSIFY** | FALSIFY | FALSIFY |

R4: tính bảng ở **bốn góc** (UNRESOLVED của Ω⁺ coi MEETS/FAILS × của Ω⁻ coi MEETS/FAILS). Cùng lớp
thì giữ (gộp mã); có FALSIFY lẫn lớp khác → INCONCLUSIVE; còn lại lấy lớp kém nhất của
PASS>WEAKEN>INCONCLUSIVE kèm R4_DOWNGRADE. FALSIFY không bao giờ thành WEAKEN. Ngưỡng n=30:
S⁺ cần ≥21 MEETS, R⁺/N⁻ cần ≤9. Không có secondary để cứu primary.

## 5. Chín phép kiểm trước khi đóng băng

Kết quả máy kiểm lưu ở [card_checks.json](../../results/lessons/l3r_6/card_checks.json); bảng tóm
tắt trong [report L3R.6](../../results/lessons/l3r_6/report.md). Phép 7 chỉ đạt ở mức “AI soạn,
tác giả duyệt”; “bằng lời tác giả” vẫn OPEN. Phép 9 là sơ bộ: L3R.7 chọn n sau numerics v1.3.1.
