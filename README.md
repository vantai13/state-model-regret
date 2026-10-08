# State × Model — giá trị cải thiện quyết định routing

Tác giả: **Doan Van Tai**.

Main RQ (nguyên văn Final Review cập nhật 06/10/2026):
> For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

Trạng thái nghiên cứu: **Phase 0 đã đóng có điều kiện — phương án B (08/10/2026)**; sang Phase 1 chỉ phân tích/exact nhỏ. **G1/candidate gap** giữ nguyên; **HOLD Phase 4 tới khi V10 đạt**. V3/V11 mang sang theo [closeout](notes/phases/PHASE_0_closeout.md).
CONDITIONAL GO chỉ analytical/exact pre-spike; full study và novelty vẫn HOLD.
L0.1: **SCIENTIFIC/UNDERSTANDING PASS — PRACTICAL PENDING**; heads-up chưa gửi.
L0.2: đã thêm [RQ card v0](notes/lessons/L0.2_rq_card.md) ngày 08/10/2026; phần diễn giải chờ tác giả xác nhận, read-back chưa làm; V3/V11 còn mở và được mang sang theo phương án B.
Contract v0: [D1–D25, quyền thông tin, estimand, repairs, scope và năm sửa đổi DL-010](notes/01_definitions.md), bản kỹ thuật đóng băng tại **`contract-v0`**. Các nhãn DRAFT/OPEN giữ bên trong snapshot; tự kiểm chưa hoàn thành. Quyết định phase tại **`phase-0-closeout`**.
[T00 — timescale sanity](notes/theory/T00_timescale_sanity.md): đã cập nhật phương án A, giữ cả neo (a) ms/datacenter và (b) polling/edge; trục tổng tuổi/delay 5 ms–30 s. **10 test timescale đạt**, ma trận 40 ô khớp; AoI prototype chỉ đối chiếu. Đây là kiểm fluid có điều kiện; chưa chứng minh practical gain.
[L0.5 — phân loại legacy](legacy/INDEX.md): đã bổ sung 21 dòng phân loại và 10 giả định không mang sang; bài tác giả tự kiểm 5 dòng còn chờ. Khung package `smr` đã cài editable và **11 test đạt** (10 timescale + 1 smoke).
File 8: đã thêm khung [L0.3 — objects](notes/lessons/L0.3_objects.md), [L0.4 — estimand](notes/lessons/L0.4_estimand.md), [L0.5 — legacy](notes/lessons/L0.5_legacy.md), [L0.6 — scope](notes/lessons/L0.6_scope.md), [L0.7 — review](notes/lessons/L0.7_review.md). MẪU và bài chưa làm được ghi riêng; chưa có đủ understanding artifacts hoặc record người đọc độc lập. V3/V10/V11 còn mở; File 9 đã đóng theo B và ghi rõ điều kiện/mốc xử lý.
[Ownership Review — phần đã chọn và việc chưa hoàn thành](notes/PHASE_0_ownership_review.md): đã nêu chọn B2 và domain hai neo; self-explanation, tính tay, review và liên hệ GVHD còn Pending; formal closeout đã ghi B có điều kiện.
Review chuyển phase 08/10 ([DL-010](notes/02_decision_log.md#dl-010), review kỹ thuật tự động): **GO WITH CAUTION**; năm sửa đổi đã áp, bảo toàn/Jensen được tái lập bằng [script hữu hạn](notes/verification/verify_dl010.py). [Closeout §6](notes/phases/PHASE_0_closeout.md) ghi B, **V3/V10/V11 còn mở**; không phải GVHD duyệt.
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
