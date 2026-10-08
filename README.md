# State × Model — giá trị cải thiện quyết định routing

Tác giả: **Doan Van Tai**.

Main RQ (nguyên văn Final Review cập nhật 06/10/2026):
> For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

Trạng thái nghiên cứu: Phase 0, **G1/candidate gap**; chưa có network evidence đúng Main RQ để lên G2.
CONDITIONAL GO chỉ analytical/exact pre-spike; full study và novelty vẫn HOLD.
L0.1: **SCIENTIFIC/UNDERSTANDING PASS — PRACTICAL PENDING**; heads-up chưa gửi.
L0.2: đã thêm [RQ card v0](notes/lessons/L0.2_rq_card.md) ngày 08/10/2026; phần diễn giải chờ tác giả xác nhận, read-back chưa làm; V3/V11 còn mở. Phase 0 chưa đóng.
Contract v0: [đủ Phần 1–3/3 — D1–D25, quyền thông tin, estimand, repairs, scope và mục mở](notes/01_definitions.md), lưu DRAFT cùng [research brief v0](notes/00_research_brief.md) ở File 7. Năm phép kiểm đã đối chiếu kỹ thuật, gồm mapping thuật ngữ brief; tác giả còn tự kiểm/xác nhận, chưa gắn tag `contract-v0`.
[T00 — timescale sanity](notes/theory/T00_timescale_sanity.md): đã thêm script và **7 test đạt**, chạy bảng với tổng độ trễ 0,35 / 0,6 / 1,0 s. Đây là kiểm fluid có điều kiện; chưa chứng minh practical gain.
[L0.5 — phân loại legacy](legacy/INDEX.md): đã bổ sung 21 dòng phân loại và 10 giả định không mang sang; bài tác giả tự kiểm 5 dòng còn chờ. Khung package `smr` đã cài editable và **8 test đạt** (7 timescale + 1 smoke).
File 8: đã thêm khung [L0.3 — objects](notes/lessons/L0.3_objects.md), [L0.4 — estimand](notes/lessons/L0.4_estimand.md), [L0.5 — legacy](notes/lessons/L0.5_legacy.md), [L0.6 — scope](notes/lessons/L0.6_scope.md), [L0.7 — review](notes/lessons/L0.7_review.md). MẪU và bài chưa làm được ghi riêng; chưa có đủ understanding artifacts hoặc record người đọc độc lập. V3/V10/V11 còn mở, File 9/closeout chưa làm.
[Inventory](notes/00_evidence_inventory.md) · [Exposure](notes/00_exposure_register.md) · [Claim boundary](notes/01_claim_boundary_v0.md).
[History](notes/00_history.md) · [Archive index](legacy/INDEX.md) · [Closeout](notes/lessons/L0.1_CLOSEOUT.md).
[Kết quả và nguồn kiểm chứng](notes/verification/2026-10-07_report.md) · [Cách tái kiểm](notes/verification/README.md).
Understanding/judgment được tác giả xác nhận ngày 07/10/2026; chưa phải GVHD phê duyệt hướng mới.

Cài môi trường và chạy kiểm thử (Python >= 3.10):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
```
