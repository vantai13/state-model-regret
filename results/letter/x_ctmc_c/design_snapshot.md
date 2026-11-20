# Design X1c: xác nhận cải thiện post-hoc của T3 trên lưới mới (Claude, 20/11/2026; Codex hết quota)

- **Người phụ trách:** Doan Van Tai. Claude quyết thay tác giả theo ủy quyền.
- **Lý do:** thẻ X-CTMC có T3 KHÔNG ĐỨNG (sai số độ dốc 0,268 > 0,25). Phân tích post-hoc
  (`results/letter/x_ctmc/posthoc_shat/summary.json`) cho thấy:
  - cùng estimator W2 với bản ghi **1000 T_int** cho sai số 0,117 và độ chính xác dấu 0,964;
  - M/M/1 theo tải trung bình kém (0,64).
  - Đây là post-hoc trên truth đã thấy, nên phải xác nhận trên **lưới mới**.
- **Code:** `experiments/letter/x_ctmc_c.py` là bản sao **nguyên thuật toán** của `x_ctmc.py` (đã khóa, không sửa). Chỉ khác:
  - (1) namespace `x-ctmc-c-v1`;
  - (2) seed grid/train/test/pilot = 2611301/2611302/2611303/2611304;
  - (3) `estimate_s` dùng bản ghi W = 1000 T_int (không còn 100 T_int);
  - (4) OUT = `results/letter/x_ctmc_c/`, BRIEF = file này;
  - (5) pilot chạy 4 regime **song song** (4 tiến trình) để rút wall-time; lựa chọn pilot giữ nguyên.
- **Lưới, rule, h, τ, cap, luật loại:** giữ nguyên `DESIGN_X_CTMC.md` §3–§5.
- **Test** (thẻ `CARD_X1C.md`, viết trước predict và truth): lặp lại T1–T6b với cùng ngưỡng. **Chính** là T3 (slope ≤ 0,25) và T1 (dấu ≥ 0,90).
- **Truth:** laptop, 8 worker, một lần.
- **Chấm lại độc lập:** script của Claude (không import scorer), và Codex khi có quota.
