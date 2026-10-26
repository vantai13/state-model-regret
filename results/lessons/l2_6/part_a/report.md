# L2.6 Part A — triển khai và kết quả

Người phụ trách: **Doan Van Tai** · **26/10/2026**.
**Hoàn tất kỹ thuật Part A; không tự cấp Understanding/L-self/formal Gate.**

## Đã làm

| Yêu cầu | Output / trạng thái |
|---|---|
| Đọc S11/A.5, đúng version/DOI | [S11](../../../../notes/literature/papers/S11.md): AI-T arxivv3 §§I–III/§VII-C–D. Journal identity TIT2026 đúng đã kiểm; DOI TWC related sai được ghi riêng |
| K3 bằng estimand dễ phân biệt | [Bài L2.6](../../../../notes/literature/freshness_decision_value.md): AoI/uncertainty/true-model decision value/fixed-M0 GS; nguồn phụ tách mức đọc |
| Tính mode/AoI/heuristic và bài tập | [Code](../../../../experiments/lessons/l2_6_freshness.py), [config](config.json), [JSON](toy_results.json),5CSV bên dưới |
| Danh sách đã biết | [Prior boundary K-S9…11](../../../../notes/literature/prior_boundary.md#freshness-và-decision-value--l26-part-a-26102026); giữ nguyên bảng PC/forecast và nội dung L2.5 |
| Heuristic vào candidate list | [H1-Q01](../../../../notes/literature/h1_candidates.md): provenance AI/exposed, chưa khóa H1, không lưới/held-out outcomes |
| Lookup + keyword log thật | [Search log](../../../../notes/literature/search_log.md), [raw metadata/title screen](lookup_records.json); không sao chép số đếm của mentor |
| Excel / thư viện | [Excel9rows](../../../../papers/paper_comparison.xlsx): chỉ thêm S11;8record notes/progress cũ giữ nguyên; PDF ngoài Git |
| Bài tập/tự kiểm | Đáp án AI trong bài; không thay record tác giả tự hiểu/đọc. Part B/P13 chưa thực hiện |

Attachment là L2.6 Part A phiên bản lesson mới; PHASE_2 gốc trong attachment
cũ có numbering/content khác (L2.5=P13, L2.6=state networking). Đã đọc đoạn liên
quan để đối chiếu và ưu tiên phạm vi attachment hiện tại, không tự mở P13/Part B.

## Số đo thực chạy

**293checks PASS**,125binary-cost cases; Fraction exact cho AoI/cost contrasts,
float cho exponential formulas. Không seed/Monte Carlo/CI; đây là verification
analytic/toy, không kết quả hypothesis hoặc replication paper.

| κ=Tmode/age, age1s | P(cùng giá trị mode sau1s) | Sau8s | SD integrated input (packet) |
|---|---:|---:|---:|
| .3 | .500636317 | .500000000 | 3.030191688 |
| 1 | .567667642 | .500000056 | 4.520623309 |
| 3 | .756708560 | .502413975 | 5.401256639 |

Same probability bao gồm even switches; ở κ3, P(không switch trong1s)=.716531311,
khác.756708560. CTMC one-step/semigroup error max **1.2212453e−15**.
Input variance dùng δ6packet/s,τ1s,stationary symmetric telegraph; quadrature
Simpson n2000 sai số tuyệt đối max **1.0736301e−11 packet²**. Chưa phải queue
posterior/snapshot error, chưa tính F/V hay cô lập hiệu ứng κ trên grid.

| Cost-table exercise | L01 | L11 | GSgivenM1 |
|---|---:|---:|---:|
| V1 thật, gap hi−1/2 / lo−3/2 | 5/4 | 5/4 | 0 |
| Giả định đổi lo gap thành+3/2 | 9/4 | 2 | 1/4 |

Đơn vị packet·s, hai states equiprobable. Bảng thứ hai chỉ đổi abstract costs,
không đổi queue/contract. Với V1, entropy giảm1bit nhưng true-model value0 và
fixed-M0 GS=−1/4 từ frozen L2.5. Timestamps age1→0 chỉ teaching setup riêng,
không giả finite-time R2 quên mode hoàn toàn.

## Command và file kết quả

```bash
set -euo pipefail
.venv/bin/python -B experiments/lessons/l2_6_freshness.py | tee results/lessons/l2_6/part_a/run.log
.venv/bin/python -B tools/paper_library/build_notes.py | tee results/lessons/l2_6/part_a/workbook_build.log
.venv/bin/python -B experiments/lessons/audit_l2_6_part_a.py | tee results/lessons/l2_6/part_a/audit.log
sha256sum -c results/lessons/part_a/SHA256SUMS
git diff --cached --check
```

- [AoI9cấu hình](periodic_age.csv), [mode/variance3κ](mode_and_input_variance.csv),
  [identity125cases](binary_identity.csv), [gap exercise](gap_exercise.csv),
  [AoI/AoII minh họa](aoi_aoii_example.csv).
- [Run log](run.log), [auditor](../../../../experiments/lessons/audit_l2_6_part_a.py),
  [audit log](audit.log), [verification](verification.json), checksum log `checksums.log`.
- [Source metadata](source_metadata.json), [access/hash/reading levels](source_access.json),
  [thẻ trước truy vấn](reading_card.md), [lookup/title records](lookup_records.json).
- [Workbook build](workbook_build.log), [kiểm Excel](../../../../papers/data/verification.json).
  Backup local trước thay: `~/papers/state-model-regret/archive/2026-10-26_before_l2_6_part_a/`.

Auditor dựng lại giá trị từ CSV, đối chiếu source one-step keep, kiểm8record cũ,
127protected files (gồm src/tests/design/old numerical outputs/claims/proof),
52checksum và local links. Chỉ hash các index/literature ledger đã thay được
cập nhật; số liệu/source/proof cũ giữ nguyên. Không rerun202tests lịch sử;
không production plant change, không chạy lưới, không tạo biểu đồ mới.

Audit thực chạy **PASS**:8record cũ bảo toàn,127file protected không đổi,
249local links tồn tại,52/52checksum khớp; kiểm mode bằng Poisson parity độc lập
sai số max **2.2204460e−16**. Không có test/numerical failure trong phiên này.

## Những câu được sửa và hạn chế

- S11 có journal TIT2026; “DOI related sai” không suy ra “chưa xuất bản”. Vẫn
  ghi version thực đọc v3; chưa xác nhận mọi chi tiết giống VoR.
- AoII không chỉ là thời gian kể từ khi sai: §II có time×error penalty. AY19
  dùng quadratic error/uncertainty, không Shannon bit; đã đánh mức T đúng phạm vi.
- Mode same-value không phải no-switch; correlation time không là hạn quên cứng.
- Dải p_sw không bảo đảm strict two-sided gaps; code kiểm counterexample tie.
- S11 threshold là plateau của optimal cost theo allowed budget; proof chưa đọc.
  §VII-C có approximate LP, không viết “S11 không có approximation”. Footnote6
  về regeneration/bounded waiting cần giả định thêm; không kiểm lại theorem.
- Hai keyword queries có18+10title records, nhiều nhiễu; không coverage/novelty
  clearance. Một metadata candidate chuyển A4, không tải/note hoặc thêm catalog.
- Kaul direct IEEE bot challenge; abstract từ kho tác giả/IEEE index đủ mức A.
  R32 lượt này chỉ A, giữ targeted record cũ; chưa kiểm toàn bộ model assumptions.

Đã xác nhận số trong phạm vi toy/analytic và formulation đã đọc. **Chưa xác nhận**
GS/Γ/F/V trên grid, novelty, H1 thắng null, full paper proofs, tác giả L-self
hoặc Gate. G1, contract, forecasts/thresholds và HOLD Phase4 giữ nguyên.
Bước tiếp theo theo lesson là Part B/P13, không tự coi Part A đóng toàn bộ L2.6.
