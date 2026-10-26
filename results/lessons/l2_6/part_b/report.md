# L2.6 Part B — kết quả và closeout kỹ thuật của lesson

Người phụ trách: **Doan Van Tai** · **26/10/2026**.
**Part A+B có artifact kỹ thuật; tác giả Understanding/L-self/formal Gate chưa xác nhận.**

## Checklist thực hiện

| Yêu cầu | Artifact / trạng thái |
|---|---|
| P13 từ nguồn gốc, đúng version/numbering | [Note P13](../../../../notes/literature/papers/P13.md): CWI journal36trang, AI-T; arxivv1 chỉ đối chiếu HTML |
| Crosswalk, multiply-by-T,25 và bài tập100 | [Bài Part B](../../../../notes/literature/horizon_transient.md), [fluid CSV](fluid.csv); không transfer theorem sang R2 plant |
| Continuous/binary/density/finite-support examples | [Các CSV dưới](#commands-và-output); giữ rõ assumptions/units, không gọi mọi S1 là quadratic |
| K-F1…3 / K-H1…4 | [Prior boundary](../../../../notes/literature/prior_boundary.md#l26-part-b--horizon-và-transient-26102026); PartA levels kế thừa đúng, không mới đọc S11/AoII |
| T-H1 trước diễn giải regret | [Claim boundary](../../../../notes/01_claim_boundary_v1_2.md#t-h1--giới-hạn-diễn-giải-do-horizon-hữu-hạn-26102026), [DL-041](../../../../notes/02_decision_log.md#dl-041--l26-part-b-prior-và-interpretation-threat-2026-10-26); chỉ append, không đổi D13 |
| Hai H1 candidates / methodology question | [H1-Q01/Q02 và Q-L27-01](../../../../notes/literature/h1_candidates.md); chưa chọn/freeze H1 hoặc null |
| Search log và library | [Log](../../../../notes/literature/search_log.md), [Excel10rows](../../../../papers/paper_comparison.xlsx);9record cũ giữ nguyên; PDF ngoài Git |
| Tự kiểm / formal Gate | Đáp án AI trong bài; không tạo record đọc/hiểu thay tác giả. G1/HOLD Phase4/A4/L2.9 giữ nguyên |

PartA S11/K3/heuristic Q01 đã lưu tại [report lịch sử](../part_a/report.md);
không sửa output hoặc trạng thái được ghi tại thời điểm đó.

## Số đo thực chạy

**122checks PASS**, Fraction exact; không random seed, Monte Carlo hay CI.
Các kết quả fluid có unit packet·s/packet/s. Abstract cost tables dùng arbitrary
cost units, không được gọi là packet·s của một grid cell.

| q0(packet), r=2packet/s | h(s) | Integral(packet·s) | Average(packet) |
|---|---:|---:|---:|
| 10 | 10 | 25 | 2.5 |
| 10 | 100 | 25 | .25 |
| 20 | 10 | 100 | 10 |
| 20 | 100 | 100 | 1 |

Same fluid/D13-style endpoint sums ở h10 hoặc100: dt1=20,dt.1=24.5,dt.01=24.95,
hội tụ25; không đồng nhất integral với discrete objective. Ở q0=10,h2 còn qH6:
integral16, phần tail9; endpoint dt1 có cost14, trong đó charge endpoint cuối6.
Do đó T-H1 không được viết “D13 không tính backlog cuối kỳ”.

| Ví dụ decision | Kết quả exact |
|---|---|
| Smooth optimizer shift1/T | normalized loss T10=.01,T100=.0001; cumulative .1,.01 |
| S0 mean gap−.5 | bias.4:Switch/loss0; bias.5 tie:Stay/loss.5; bias.6:Stay/loss.5 |
| Uniform gap[−4,4] | bias1:1/16; bias2:1/4 |
| Bài tập Uniform[−2,2] | bias1:1/8 |
| Finite gaps−2,−1,0,1,2, bias1/4 | S1 model loss0; plateau, không bắt buộc quadratic |
| No-queue balanced5, bias1 | L00/L10/L01/L11=5,23/5,5,22/5; GM0,GMgivenS1=1/5,Γ=1/5 |
| No-queue gaps−3/2,1/2, bias3/5 | L00/L10/L01/L11=5,17/4,9/2,17/4; GM1/2,GMgivenS1=0,Γ=−1/2 |

Những bias examples không phải D21 conditional-mean response model; Γ khác0
không tự là mechanism của grid. Toàn bộ22finite tables được lưu, không chỉ hai
hàng thuận lợi. Gap-horizon example {7,1} có EΔ+=**4**, sửa lỗi số trong lesson.

Heuristic B-only fluid: q10,r2,η.75 cho long-h difference75 nhưng tại h8 chỉ39
packet·s; không dùng75 như finite-h GS. Mean B sau Switch=9 hoặc9.5<capacity10,
ON overload không chứng minh global instability. Không tính grid J/regret/F/V.

## Commands và output

```bash
set -euo pipefail
.venv/bin/python -B experiments/lessons/l2_6_horizon.py | tee results/lessons/l2_6/part_b/run.log
.venv/bin/python -B tools/paper_library/build_notes.py | tee results/lessons/l2_6/part_b/workbook_build.log
.venv/bin/python -B experiments/lessons/audit_l2_6_part_b.py | tee results/lessons/l2_6/part_b/audit.log
sha256sum -c results/lessons/part_a/SHA256SUMS
git diff --cached --check
```

- [Code](../../../../experiments/lessons/l2_6_horizon.py), [config](config.json),
  [JSON/check list](toy_results.json), [run log](run.log).
- [Fluid](fluid.csv), [endpoint sums](endpoint_sum.csv), [gap/horizon](gap_horizon.csv),
  [smooth optimization](continuous_optimizer.csv), [binary step](binary_step.csv),
  [uniform density](uniform_bias.csv), [finite2×2](finite_support_2x2.csv),
  [moment heuristic](moment_heuristic.csv): tổng102data rows.
- [Auditor độc lập](../../../../experiments/lessons/audit_l2_6_part_b.py),
  [audit log](audit.log), [verification](verification.json), checksum log `checksums.log`.
- [Lookup/metadata](lookup_records.json), [PDF hash/reading level](source_access.json),
  [thẻ trước lookup](reading_card.md), [Excel check](../../../../papers/data/verification.json),
  [workbook build](workbook_build.log).
- Backup workbook ngoài Git: `~/papers/state-model-regret/archive/2026-10-26_before_l2_6_part_b/`.
  Không tạo scientific plot mới; PDF source chỉ có local ngoài Git.

Auditor kiểm CSV bằng công thức tổng endpoint độc lập recurrence, enumerate
finite policies/costs và bảo toàn9notes/progress.146files protected gồm src/tests,
T00/T03, contract, claims/forecasts, design và toàn bộ numerical outputs cũ.
Boundary/prior/log chỉ append;52checksum giữ cùng file set, chỉ cập nhật hash
các documents đã đổi. Không rerun202tests lịch sử vì production plant không đổi.

Audit cuối **PASS**:102rows trong8CSV,9record Excel cũ bảo toàn,146protected
files không đổi,4document prefixes chỉ được append,52/52checksum khớp và
344local file-link targets tồn tại. Không xác nhận remote fragment anchors từ
phép kiểm local này; staged whitespace check được chạy trước commit.

## Sửa lesson / hạn chế và kết luận

ΩT ở Eq2.7, không3.5; terminal explanation journal§6/tr289 khác arxiv§5.3.
Prop5 là loss normalized; multiplier T đổi bound. Finite staffing domain μ≥0,
không mọi optimizer phải stable. u3 in3 ở §5.1 không khớp central-moment definition;
đã tính riêng raw moments1/3/13 cho central3=6, không dùng typo để replication.
M0 fluid-like có conditional input thường time-varying, không chính xác là
constant-drift Lévy model. Density quanh0 không được bảo đảm bởi p_sw band.

Lượt làm bị gián đoạn một lần; đọc local ban đầu thử src/smr/queue.py không tồn
tại, sau đó tìm đúng recurrence trong src/smr/exact.py. Hai patch bị từ chối
do format/context, đã sửa và áp dụng; không numerical/test failure. Không thay
source/evidence gốc để che các lỗi hoặc đổi metric.

Đã xác nhận các teaching calculations và đọc đúng phạm vi statement/section.
**Chưa xác nhận:** P13 proofs/replication, transfer sang correlated R2 input,
grid hypotheses/Γ mechanism, H1/null, novelty hoặc tác giả Understanding/L-self.
Technical execution đủ cho2parts; formal Gate còn mở. Bước học tiếp là L2.7;
không tự chạy Phase3, freeze A05 hoặc mở HOLD Phase4.
