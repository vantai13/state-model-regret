# Hàng đợi ý tưởng cho H1 — chưa phải preregistration

Người phụ trách: **Doan Van Tai** · 26/10/2026. AI-assisted, đã exposed từ lesson.
Không thay D25, claim PC4/PC6, metric, split, thresholds hay mô hình nào.

| ID | Candidate / provenance | Đã kiểm gì? | Còn thiếu trước dùng ở A05 |
|---|---|---|---|
| H1-Q01 | L2.6 PartA §7b: mode correlation time và integrated-input variance có thể gợi ý phải tách backlog/mode thay vì chỉ age/κ | Công thức unconditional telegraph variance + quadrature;3κ,δ6,τ1s. Code/output ở results/lessons/l2_6/part_a/ | Liên hệ với reflected posterior Var(q|y), gap/action flips và fixed-M0 F/V; chưa biết prediction direction hoặc thắng null |

**Giới hạn:** Var input không phải snapshot error của queue; không có outcome
lưới trong record này. κ lớn không tự chứng minh F lớn, V nhỏ hay ngược lại.
λA/quantiles/horizon thay cùng lát, không suy isolated causal effect từ grid.
Không chọn hàm/feature/fit/null bây giờ. A05 mới khóa trước confirmation đúng D25;
không xem held-out outcomes để chọn candidate. A4/L2.8/L2.9 còn mở.

[Bài và công thức](freshness_decision_value.md) ·
[Kết quả heuristic, không kết quả hypothesis](../../results/lessons/l2_6/part_a/mode_and_input_variance.csv).

## H1-Q02 — initial second moment và tốc độ xả, L2.6 Part B

Provenance: attachment PartB/mục10 và phép đối chiếu P13; **AI/exposed**, không
forecast mù. Với B-only constant-drift fluid, r>u>0 và horizon đủ dài:
E[qB²]/2·(1/(r−u)−1/r)=E[qB²]/(2r)·η/(1−η), với r2 thì u2η.
Đã kiểm đại số, E[q²]=(Eq)²+Var(q) và finite-h examples.

Chưa có full two-queue gap, mode-memory posterior, F/V hoặc predictive result.
Ví dụ qB10,η.75: long-h coefficient75 nhưng B-only difference ở h8 là39packet·s.
Không dùng coefficient làm GS hoặc input giả kết quả grid. Không chọn feature,
fit model, đổi null/threshold hay xem held-out để quyết định ở lượt này.

**Q-L27-01:** decision geometry/finite support/state-dependent gap bias có thể
góp phần vào Γ thế nào? Abstract tables không queue cho Γ=1/5 hoặc−1/2;
chúng không phải D21 plant. Cần tách explanation này trước gán Γ cho network
mechanism ở L2.7/A05. [Bài/các giả định](horizon_transient.md).

L2.7 PartA/26/10: Q-L27-01 đã chuyển thành
[MT5 trong Phase4 queue](../phases/PHASE_4_methodology_threats.md); vẫn chờ A05
chọn thiết kế null cụ thể. Các teaching tables ở L2.7 không được dùng tự khóa
null, H1 hoặc giải thích mechanism của lưới. P12/OεRE thuộc PartB chưa làm.

## H1-Q03 — R04 conditions → one-shot diagnostic, L2.8 Part2

Provenance: R04 primary Def3–4/Prop2/PDF9 và AI/exposed mapping,26/10/2026.
SC là old MP solution feasible, Π-accuracy là objective truthful cho policy.
Plant không có cùng sequential MP, chỉ dịch sufficient comparison: old action
khả thi và accurate old/new action-cost gap thì information repair không hại.
Với δ=J−Jhat, true gain=predicted gain+δold−δnew; V1 hi cho1/2+0−1=−1/2.

Đã kiểm frozen V1 và R02 Example1. **Chưa** có observable-only feature/certificate,
chưa đánh giá/fit grid, chưa chọn null hoặc H1. R04 Remark2/PDF10 cảnh báo error
terms cần policy evaluation; không dùng true outcomes để tự chứng nhận forecast.
WM26 §5/F.1 có2×2repair, phải thừa nhận prior trước wording PC3/PC4 ở L2.9.
[Crosswalk](literature_audit_part2.md); queue không phải A05 preregistration.
