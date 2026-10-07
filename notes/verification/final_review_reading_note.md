# Final Review — bản ghi đối chiếu nguồn

Bản nguồn cập nhật 06/10/2026; SHA-256 `fc766e319427ba01da7362de2018cd4da6695dc1fcaa9812ed7badd5c0651fd1`. Bản này là tóm tắt đối chiếu, không phải bản gốc nguyên văn và không thay đổi digest của bản gốc. Chưa có bản full snapshot mở công khai; đây là giới hạn nguồn EV-05/06/18. Không có byline rõ trong snapshot đã mở. Việc xác nhận người viết vẫn để ngỏ.

## RQ và verdict (§1, §22.2)

> For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

KEEP Main RQ; G1/candidate gap; CONDITIONAL GO cho analytical pre-spike; HOLD full project, claim novelty và operational recommendation.

## Đối chiếu logic (§2.2–2.3)

G_S=L00−L10, G_M=L00−L01, G_SM=L00−L11, Γ=L10+L01−L00−L11.
Cost thật Stay=20, Switch=18. Sai số cộng e_S=e_M=3 cho costs (20,20,20,18) và Γ=+2; sai số 1,5 cho (20,18,18,18) và Γ=−2. Không có queue trong ví dụ này. Phép tính được chạy lại tại [verification_results.json](verification_results.json), trường counterexamples.

## Known của field (§4)

Review trỏ P03/P07 cho khác biệt prediction fidelity/decision fidelity; P04 cho ảnh hưởng của stale state tới routing. Các prior P01–P13 gồm queue routing/service knowledge, predictive control, model improvement value, value equivalence và transient queues. Đây là literature thứ cấp trong L0.1; chưa xác nhận tác giả đã tự đọc primary papers. Không dùng nó chứng minh “chưa ai làm”.

## G2 và gate (§6, §11.5, §20)

G2 cần effect/equivalence có kích thước thực dụng, prediction trên dữ liệu chưa dùng xây giải thích, use case có timescale/cost hợp lý; nhánh mechanism còn cần phân biệt threshold null. Contract khóa chỉ mở pre-spike. Full study cần thêm preliminary evidence, prior boundary, baseline mạnh và timescale hợp lý.

## Hành động (§22.1)

Khóa contract/claim boundary → analytical/exact pre-spike với null có thể bác bỏ → chỉ xác nhận claim còn đứng sau pre-spike. L0.1 hiện chưa khởi động các bước nghiên cứu đó.
