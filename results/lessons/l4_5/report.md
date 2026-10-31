# L4.5 — Giữ SV/SUB có điều kiện, khóa luật sàng; Part B chưa chạy

Người phụ trách: **Doan Van Tai**.
Thực hiện 30/10, tiếp tục và chốt hồ sơ **31/10/2026**.
Provenance: AI soạn và triển khai; tác giả duyệt Part A và gói luật trực tiếp.

**Part A và luật sàng đã được duyệt/khóa. Part B vẫn BLOCKED_DEPENDENCIES.**
Không có hộp nghiên cứu nào được đếm, không p-hat SV/SUB mới, không quyết định
0/1/2 card. Các số power dưới đây là phép tính thiết kế giả định, không evidence
cho một claim hoặc tần suất trong mạng.

## A. Đã thực hiện

- Đọc đầy đủ hai input L4.5, kiểm repo, DL-073/DL-103, trạng thái L4.3–L4.4,
  nguồn T07 và code power/verdict/statistics frozen.
- Dùng skill paper-research cho local-note review: đối chiếu 7 note files và
  một author-attestation cũ. Không online search, không mở primary PDF, không
  thêm nguồn, không sửa Excel/catalog/mức đọc tác giả.
- Viết bảng độ phủ RQ, ba bộ lọc cho SV/SUB, phương án các ứng viên còn lại và
  claim boundary có điều kiện. Proposal **736633a** trước mọi đếm hộp.
- Tác giả chọn nguyên văn **“Giữ SV và SUB có điều kiện (khuyến nghị)”** và
  **“Chọn gói luật sàng đã soạn (khuyến nghị)”**. Lưu author_choices và DL-105.
- Khóa rules/source ở **624a9be**, trước mọi real-box p-hat. SV hai vùng,
  SUB một vùng; n60, α1/40, π0=1/2, haircut .10, power≥.5, unresolved≤.05,
  tối đa3hộp/candidate. r_minus đo riêng; không chép r_plus sang vùng đối chứng.
- Implement kernel và entrypoint có guard, registry reserve trước counts,
  CF/R09/R10 protection, xử lý duplicate/UNDEFINED/EMPTY/NO_RESOLVED. Baseline
  và quyết định tác giả tách khỏi PASS_SCREEN, không sửa verdict/card F1.
- Tái tạo exact power/R5 tables, kiểm phản ví dụ toán học, chạy tests và
  preflight/entrypoint. Chuẩn bị yêu cầu cho combined native run kế tiếp.

## B. Đã chạy và kiểm chứng

```bash
.venv/bin/python -m experiments.P4_05_candidates.design_power
.venv/bin/python -m pytest -q tests/test_p4_05_candidates.py
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.P4_05_candidates.screen preflight
.venv/bin/python -m experiments.P4_05_candidates.screen screen --candidate SUB --box NONEXISTENT_BOX_FILE --native-manifest NONEXISTENT_NATIVE_MANIFEST
.venv/bin/python -m experiments.P4_05_candidates.verify_results --output results/lessons/l4_5/verification.json
```

| Kiểm | Kết quả thực tế |
|---|---|
| Tests mới cuối cùng | **16 PASS trong0.18s** |
| Full suite | **813 PASS trong82.29s** |
| Power tables | **14/14 dòng khớp** các số làm tròn của lesson |
| Exact thresholds n60 | Ω⁺ cần **≥39 MEETS**, Ω⁻ cần **≤21 MEETS** |
| R4/R5 độc lập | Robust one-region khớp tổng multinomial và gamma_verdict thực trên fixture n10 |
| Kernel/registry | EMPTY/full synthetic, haircut, r_minus riêng, negativeΓ/R6, 3-box cap, CF/sealed/duplicate/pilot guards PASS |
| Preflight sau commit luật | **Exit2 có chủ đích: BLOCKED_PART_B**, author_rules_locked=true |
| Entrypoint với file không tồn tại | **Exit1 có chủ đích: PART_B_BLOCKED**, trước khi mở box/native input |
| Research engine / real boxes / CF outcomes mới | **0 / 0 / 0** |

Không RNG/seed hoặc simulation lấy mẫu trong bảng power: đây là tổng xác suất
exact bằng Fraction. Fixtures dùng cost quy ước, không packet·s đo từ plant.
Không có kết quả baseline mới hoặc so sánh pilot/native mới trong L4.5.

Hai lượt kiểm integration trước freeze có **1FAIL/15PASS** do fixture thiếu
`reasons=[]`, rồi fixture chưa mock CF keys khi dùng hộp synthetic bao toàn bộ.
Đã sửa setup fixture, không nới guard hoặc tiêu chí; giữ cả hai log FAIL.
Lượt 16/16 cuối và full813 kiểm source hiện đang khóa.

Phiên bị ngắt lúc commit chưa xảy ra vì `git diff --check` thấy whitespace có
sẵn trong traceback pytest. Giữ log nguyên byte; kiểm source/docs với raw logs
được loại khỏi whitespace-only check, rồi commit624a9be. Không thay dữ liệu,
source hash, metric hoặc threshold để vượt kiểm. Preflight trước commit được
giữ riêng; chỉ log `dependency_preflight_after_lock.log` là trạng thái hiện tại.

## C. Kết quả thiết kế đã tính được

### Power không UNRESOLVED

n=60, α=.025, π0=.5. Hai vùng dùng p_minus=.2 và giả định các lần lấy mẫu
độc lập giữa hai vùng. p_plus là giả định cho planning, không p-hat đo từ hộp.

| p_plus | Hai vùng (SV-style) | Một vùng (SUB-style) |
|---:|---:|---:|
|0.60|0.256281|0.256806|
|0.65|0.557890|0.559032|
|0.70|0.836469|0.838182|
|0.75|0.968216|0.970199|
|0.80|0.995917|0.997956|

Đây là xác suất đạt kết cục hỗ trợ khi các tham số giả định đúng, không xác
suất hypothesis đúng. R4/R5 đã nằm trong robust helper cho các bảng có U.

### Ảnh hưởng của UNRESOLVED, một vùng

p_cond là xác suất MEETS có điều kiện đã phân giải; r là xác suất UNRESOLVED.

| p_cond | r=0 | r=5% | r=10% |
|---:|---:|---:|---:|
|0.70|0.838182|0.644512|0.330504|
|0.75|0.970199|0.867407|0.499811|
|0.80|0.997956|0.954725|0.585927|

R5 ở n60 chặn khi số U>6:

- r=.05: P(R5 fail)=**0.029694102** ≈2.9694%.
- r=.08: P(R5 fail)=**0.201985632** ≈20.1986%.

Các helper là model binomial/multinomial i.i.d., UNDEFINED=0; tích hai vùng
giả định các mẫu vùng độc lập. Docstring frozen còn ghi U độc lập latent label.
Không nói helper “không có giả định”, hoặc native R6 đã được chứng minh tuân
theo mô hình đó. p_cond và r được mô tả riêng; trần5% là policy sàng đã chọn.

### p_plan tối thiểu để power≥.5

Bracket exact rộng <5.961e−8; bảng dưới làm tròn. SV dùng p_minus=.2.

| Thiết kế | Không U | U5% ở vùng liên quan |
|---|---:|---:|
| SV hai vùng |**0.6410348**|**0.6794676**, r_plus=r_minus=.05 trong scenario này |
| SUB một vùng |**0.6408766**|**0.6755331**, chỉ có r_plus |

Ví dụ SV không U cần p_cond native khoảng **0.7410348** sau khi cộng lại
haircut .10. Đây là hệ quả của rule, không tỷ lệ đã quan sát. Chưa có box
membership, p_cond, r_hat hoặc power từ dữ liệu SV/SUB thực.

### Đính chính logic và prior quan trọng

1. **SV PASS không tự là double dissociation.** Fixture exact có
   (L00,L01,L10,L11)=(11,10,10.5,10), nên GS=.5 và GM=1 cùng lớn. Card SV chỉ
   kiểm GS≥1% chưa kiểm GM nhỏ; MV cũng chưa khóa GS nhỏ. Không thêm điều kiện
   mới vào card để biến câu mạnh hơn thành đã kiểm.
2. **AB không tự là SUB.** Fixture exact (12,10,11.5,9) cho GS=.5, GM=2,
   Γ=.5>0, dù cả hai gains vượt1%Cref. Ngược lại, Γ≤−1%Cref kéo theo cả hai
   gains≥1%Cref theo identity. Không đếm161AB thành161SUB.
3. **Lậtκ không tự ép đối chứng.** Identity không chứaκ. Không-SUB bị ép nếu
   có thêmGS<0 hoặcGM<1%; coordinate flip đơn thuần cần physical prediction.
   Một vùng là thiết kế được chọn theo lesson, không theorem cấm mọi hai vùng.
4. **3/162 của DL-073 gắn min(GS,GM)>.5%**, không≥1% như input kể lại.
   Premise đổi ở support tồn tại đáng xét, không prevalence từ lưới thích nghi.
5. **PC3 đã được tác giả xác nhận ở DL-043**. Không coi ô trống của snapshot
   L2.9Part1 là latest state. Phiên này chỉ review note, không primary reread
   hoặc clearance novelty mới. WM26 limitations ở§8/PDF9 theo đính chính cũ.

## D. Phần chưa chạy và điều kiện cần

Part A giữ hai ứng viên **không có nghĩa chọn hai card**. DL-105 ghi rõ
final_card_count=null. Bộ lọc baseline và khả thi chưa có kết quả trên support.

- L4.3 còn Cref-dt R1 HOLD tạiκ=.05; nhãn native toàn support chưa đầy đủ.
- L4.4 còn oracle-bound sanity HOLD tại X2000, chưa cóρ* và full baseline.
- Spec L4.4 chỉ chạy MV/SH. Kể cả F1 baseline hoàn tất cũng không tự cấp
  baseline đúng vùng SV/SUB; cần candidate-specific coverage và rho policy.
- Chưa khai bounds hoặc minus policy SV, chưa thử bất kỳ hộp nào. Không tạo
  readiness=PASS giả, không dùng pilot hoặc 2MV points làm proxy.

F1 giữ nguyên. F2 nếu có1/2card, α=.025/card cho cận FWER .025/.05; cận hợp
F1+F2 tương ứng .075/.10. Không tự giảm α F1, không chỉ báo verdict thuận lợi.
Nếu sau này tác giả chọn0card, phải ghi phạm vi discovery và không tự gỡ F1
baseline HOLD/P0-V10. Chưa cócardv3,CFv3,budget,Gate4 hoặc confirmation outcome.

## E. File lưu kết quả

- [Part A](../../../notes/phases/PartA_candidate_filters.md),
  [DL-105](../../../notes/phases/L4_5_screening_decision.md),
  [author choices](../../../experiments/P4_05_candidates/author_choices.json).
- [Rules JSON](../../../experiments/P4_05_candidates/screening_rules.json),
  [rules đọc được](../../../experiments/P4_05_candidates/screening_rules.md),
  [source lock](../../../experiments/P4_05_candidates/rules.lock.json).
- Source: [screen.py](../../../experiments/P4_05_candidates/screen.py),
  [design_power.py](../../../experiments/P4_05_candidates/design_power.py),
  [identity_checks.py](../../../experiments/P4_05_candidates/identity_checks.py),
  [tests](../../../tests/test_p4_05_candidates.py).
- CSV/JSON: [power không U](design/power_no_unresolved.csv),
  [power có U](design/power_with_unresolved.csv), [R5](design/R5_failure.csv),
  [design summary/brackets](design/summary.json),
  [identity fixtures](design/identity_fixtures.json),
  [real-box registry=0](box_registry_status.json).
- Logs: [813tests](full_tests.log), [16tests PASS](targeted_tests_16_pass.log),
  [design run](design_power.log), [preflight sau lock](dependency_preflight_after_lock.log),
  [entrypoint blocked](blocked_screen_entrypoint.log), [verification](verification.log).
- [Literature scope/log](literature_review.md),
  [conditional claim boundary](../../../notes/phases/claim_boundary_v1_4_draft.md),
  [next native requirements](../../../notes/lessons/L4.5_next_native_requirements.md),
  [summary](summary.json), [completion](../../../notes/phases/L4_5_completion.json),
  [verification JSON](verification.json), [artifact manifest](artifact_manifest.json),
  [forking log](forking_paths.jsonl).

Không tạo box-levelp-hat CSV, real native/baseline dataset, cardv3, CFv3 hoặc
biểu đồ mới. Fixtures/tests trong tmp_path không phải hộp nghiên cứu đã thử.

## F. Kết luận

Đã xác nhận implementation/statistical design checks và hai lựa chọn tác giả;
chưa xác nhận SV/SUB khả thi hoặc đúng. **Part A/rules hoàn tất; L4.5 experimental
decision còn mở vì Part B BLOCKED.** G1, cardv2 và các HOLD cũ giữ nguyên.
Lần compute tiếp cần numerical readiness và combined native+baseline prereg
đúng support, rồi mới sàng tối đa3hộp/candidate và để tác giả quyết số card.
