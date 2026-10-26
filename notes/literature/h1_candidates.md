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
