# L3R.5 — Contract v1.3 và kiểm chứng

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026 · DL-071.
Trạng thái lúc chuẩn bị tag: **READY_TO_TAG_WITH_DEFERRED**; xem lock receipt
sau bước tag để biết commit bất biến. Phase4 vẫn HOLD.

## Đã thực hiện

Đọc đủ bốn file lesson, đối chiếu contract v1.2, draft DL-061, T07, DL-068/070
và completion audit/realism. Tác giả xác nhận ba lựa chọn trước khi khóa:
gói P1/RoE/ngưỡng/c_sw0; cam kết D22; tag phương án A. Trả lời nguyên văn lưu
ở [author_choices.json](author_choices.json), commit7f0a451 trước contract.
Không suy việc tác giả đã tự read-back từ yêu cầu triển khai hoặc lựa chọn này.

Đã tạo [contract v1.3](../../../notes/01_definitions_v1_3.md),
[brief](../../../notes/00_research_brief_v1_3.md),
[diff v1.2](../../../notes/design/v1_3_contract_diff.md),
[chuỗi nghiên cứu](../../../notes/design/v1_3_research_chain.md),
[kế hoạch numerics freeze](../../../notes/design/v1_3_numerics_freeze_plan.md)
và [khung claim boundary](../../../notes/01_claim_boundary_v1_3.md) để L3R.6 điền.
Khung claim chưa frozen; không tạo card/vùng/CF trong lesson này.

Nội dung khoa học khóa: P1 stationary pre-Stay, epoch độc lập state; S0 true
shared posterior; S1 gồm hidden modes; giữ plant/objective/information rights;
primary ratio-of-expectations Ḡ/C̄ref, stakes chỉ mô tả; εR1%, εE.5%, sensitivity
.5%/2% không cứu verdict; primary c_sw0; λA không outcome-anchor. Quyết định sau
pilot, trước confirmation; không chạy so các phương án theo số regime PASS để
chọn thước. Sự tiếp xúc với discovery vẫn được ghi, không nhận pre-pilot choice.

Schema hữu tỉ và semantic validator tách scientific identity khỏi settings K/ref,
giữ c_sw. [JSON schema](../../../notes/design/regime_schema_v1_3.json) mô tả cấu
trúc; Python kiểm inequalities/cross-field semantics. Không có thư viện JSONSchema
trong venv, nên không nhận đã chạy một external JSONSchema validator. Không thêm
dependency. Freeze checker kiểm annotated tag/commit/byte hashes và fail closed.

## Các điểm được chỉnh lý luận

- Refinement difference nhỏ không là cận sai số thật/cumulative error. Ví dụ
  e(n)=.6/√n: gap1→2≈.175736 trong khi residual≈.424264, đơn vị pp minh họa.
  Vì vậy việc hoãn mức vẫn có residual degrees of freedom; hạn chế bằng rule,
  exposure/freeze và UNRESOLVED, không nói nó không thể đổi verdict.
- dt đổi transition law, stationary law và endpoint objective của slotted model.
  Contract khóa họ estimands L̄(c;dt), hoãn chọn dt*; K là quadrature resolution.
  Không âm thầm chuyển sang continuous-limit objective.
- S1 invariance chỉ khi giữ π/J/policy, không mặc định theoκ. P2a có thể đổi
  marginal X; recovery v1.2 tại y* phải condition toàn joint, gồm S1.
- Scientific validity chỉ cần stability trước decision. Post-Switch overload
  trong finite horizon không tự vô nghĩa; cận .95 thuộc frame, không validator.
- Adapter đọc c_sw từ trường thứ chín của pilot; snippet mặc định0 nếu dùng
  máy móc cho Stage3 sẽ làm mất switching-cost scenarios. K/ref không là physics.
- R6 xét cả effect+εR, harm−εR, equivalence±εE; finite escalation budget dùng
  chung. Các coarse K/dt được kiểm riêng, tránh hai lỗi triệt tiêu ở joint step.

## Đã chạy và số đo

| Phép kiểm | Kết quả thực |
|---|---:|
| Targeted tests | **41/41 PASS**, .13s |
| Full suite | **532/532 PASS**, 62.57s |
| Main design records | **216** =60+108+48 |
| Scientific identities | **210** |
| Nếu quên c_sw | **162**, gộp nhầm48 scenarios |
| Main+robustness records | **234**, cùng210 scientific identities |
| Nếu đưa K/ref vào identity | **228**, đếm nhầm numerical variants |
| Invalid metadata | **0/234** |
| λB8: φ=eta_pilot | **144/144** |
| Main c_sw0 | **168 ID /162 scientific identities** |

Không đọc outcome CSV của pilot để chọn thước. Inputs của lần kiểm là năm
`specs.json` trên tag `explore-v13-pilot` tại a7435e9; SHA từng input có trong
[candidate_verification.json](candidate_verification.json).

Các toy minh họa có đáp án exact, đơn vị **toy cost**, không số đo network:

| Đại lượng | Kết quả |
|---|---:|
| RoE hai snapshot | 1/100 =**1%** |
| EoR cùng ví dụ | 1/19 ≈**5.263158%** |
| P1 ba snapshot | 3/100 =**3%** |
| P2a giữ y2/y3 | 6/175 ≈**3.428571%** |
| Estimate .98%, measured refinement .2pp | **UNRESOLVED** ở threshold1% |
| Mẫu số0 | **undefined/null**, không floor |

| D22 golden replay | ḠS | F̄ | V̄ |
|---|---:|---:|---:|
| Mode-only | −1/2 | 0 | −1/2 |
| Backlog-only | −1/2 | −1/2 | 0 |
| Triệt tiêu | 0 | −1/2 | +1/2 |

Ba D22 golden replay khớp T07; **không phải physical population D22 implementation
hoặc audit đã hoàn tất**. Full suite gồm regression/golden cũ, không tạo research
outcome mới. Không run simulation/MC, không seed nghiên cứu mới, không sinh CF,
không mở R09/R10, không thay engine/src hoặc merge pilot branch.

## Lệnh và file output

```bash
.venv/bin/python -m pytest tests/test_v1_3_schema.py tests/test_v1_3_rules.py tests/test_v1_3_freeze.py -q
.venv/bin/python -m experiments.R3R_05_contract.run_checks
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_5/full_suite.xml
.venv/bin/python -m experiments.lessons.audit_l3r_5
```

Source: [schema.py](../../../experiments/R3R_05_contract/schema.py),
[rules.py](../../../experiments/R3R_05_contract/rules.py),
[freeze.py](../../../experiments/R3R_05_contract/freeze.py),
[run_checks.py](../../../experiments/R3R_05_contract/run_checks.py).
Config: [contract_spec.json](../../../experiments/R3R_05_contract/contract_spec.json).
Data: [scientific_regimes.csv](scientific_regimes.csv),
[toy_metrics.csv](toy_metrics.csv), [toy_metrics.json](toy_metrics.json).
Logs: [targeted](targeted_tests.log), [full suite](full_suite.log),
[design checks](design_checks.log), [audit](audit.log).
Integrity: [verification.json](verification.json), [artifact_index.json](artifact_index.json).
Không tạo chart/PDF hoặc literature search trong phiên này.
Lần audit đầu dừng vì kiểm link tới artifact_index của chính nó trước khi tạo
output; đã tách self-output khỏi input-link checks và giữ
[log lần đầu](audit_attempt1_self_outputs.log). Không đổi luật hoặc chạy lại engine.

## Phần còn DEFERRED và ý nghĩa

| Phần | Đã khóa | Deadline thực thi/đóng |
|---|---|---|
| D22 | Định nghĩa/cam kết | Engine path và audit trước Phase4 |
| Numerics | R1–R8,tolerance.25pp,u_max10%,2 bước escalation chung | K*/dt*,quadrature-tail,S1 route,auditcoverage→v1.3.1 trước L3R.7 sampling |
| RQ2 | Vai trò của H0/H1 | Model/null/fit budget→Phase5 prereg |

Inventory21dòng giữ18LOCKED,2DEFERRED và1LOCKED-definition/DEFERRED-execution.
“Interact” chỉ mô tả trừ khi L3R.6 dành một primary slot choΓ; Hyp-MI chưa kiểm
cơ chế; εR convention chưa chứng minh practical value. Chưa có confirmation
evidence mới, contribution hoặc novelty. Realism **HOLD_UNSOURCED**, auditL3R.3
**HOLD**, G1 không đổi. P0-V10/L8/T05/Understanding giữ OPEN.

Sau tag đã kiểm chứng, L3R.6 được viết/khóa trên contract cố định. CF sampling
và Phase4 vẫn bị giữ theo các điều kiện trên; tag không phải permission chạy.
