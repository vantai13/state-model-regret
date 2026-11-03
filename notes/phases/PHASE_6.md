# Phase 6 — bản triển khai từ lesson 6.2 Part B và Part C

Người phụ trách: **Doan Van Tai** · 03/11/2026.

Đây là bản triển khai theo hai lesson được gửi ngày 03/11, không phải bản
PHASE_6 gốc mà lesson trích §9/§14. Bản gốc chưa được cung cấp hoặc tìm thấy;
không nhận đã khôi phục đầy đủ nó. Main RQ, contract v1.3 và frozen engine
giữ nguyên. DL-129–133 là lịch sử có thẩm quyền với các bước đã chạy.

## Phạm vi và thứ tự

Part A′ có 13 D(ii), 13 twin và A− B001C00, chỉ là predictor readiness.
Part B khóa luật đọc trước truth, rồi kiểm đúng ba probe B027C02/B040C02/
B050C02 tại c=1/16. Mỗi probe có ba levels (640,4), (320,4), (640,2).
Đó là các keys khác panel nhưng cùng ba base, không phải clean held-out.
Raw probe được tính và commit, giữ kín G_S/z tới L6.4. Summary chỉ có
readiness, d, widths, R1 deltas, uncertain action mass, CPU và quyết định.

Chỉ nếu probe PASS hoặc PASS_REDUCED mới thực hiện Part C: freeze members
và predictions, analysis_plan_v2, runner, tests, một replay positive control,
rồi Gate D-entry. Gate GO không tự cho phép chạy L6.3 trong nhiệm vụ này.
Part B STOP/HOLD/BUG/resource failure thì dừng, không probe lần hai.

## Luật đã khóa trước probe

G_S=L00−L10 được phép âm. READY xét riêng G_S: R1 ở cả trục K và dt với
max(|G_f−G_c|/C_f, |G_f/C_f−G_c/C_c|) ≤1/400; normalized arithmetic width
≤1/4000 ở cả ba levels; không sign flip khi cả hai |z|>1/200. Không thêm
nonnegative-contrast gate hoặc Cref-delta gate của bài khác.
d=max(hai R1 deltas, width tại main), là diagnostic, không certified bound.
Nhãn '+' nếu READY và z≥1/200+d, '-' nếu READY và z≤−1/200−d; còn lại U.
U gồm NOT_READY và READY trong deadband, không đồng nghĩa tất cả là lỗi số.

Verdict chỉ dùng D, giữ full planned denominator sau quyết định cơ học
Part B: H1_SUPPORTED khi số '-'≥ceil(4N_D/5) và U≤floor(N_D/10);
H0_SUPPORTED tương tự cho '+'. U vượt cap → INCONCLUSIVE; còn lại MIXED.
N_D=13 cần 11 dấu cùng phía, tối đa 1 U. N_D=10 cần 8, tối đa 1 U.
Incomplete execution không được thay bằng verdict trên phần thuận lợi.
A− phải có nhãn '-'; nếu sai thì dừng validity. Twin không '+' chỉ là
kết quả cần báo, không BUG. Chỉ cặp twin '+' và D '-' là sign flip.
Chữ 'lật dấu' ở mức aggregate cần ít nhất ceil(4N_D/5) cặp và H1_SUPPORTED.

Thứ tự panel: A− trước, sau đó base ID tăng dần, twin rồi D. Budget có thể
hết giữa một cặp; không hứa mọi cặp luôn hoàn tất. Không dừng sớm do nhiều U;
vẫn thu dữ liệu mô tả theo lịch cố định, nhưng dừng vì BUG/execution/
resource/budget/A− failure. Không retry, resume, refinement hoặc P6 v1.1.

## Probe, quyết định và budget

Ba class là (h,κ)=(8,1/10), (16,1/10), (16,1/5), có 3/7/3 D base.
Chọn tải nặng nhất mỗi class, tie theo base ID lớn hơn, đúng ba keys đã nêu.
Class không READY bị loại cả D và twin. Còn <10 D hoặc <5 base → STOP_NUMERICS.
Estimate=1.5×tổng CPU ba levels của class cho từng member; A− dùng class
của nó nếu có, nếu không dùng class tốn CPU nhất. Estimate≤7200 giữ mọi
member còn lại; nếu vượt thì bỏ toàn bộ twin và tính lại; còn vượt → HOLD_BUDGET.
Không đổi c_probe, thresholds hoặc điều kiện theo kết quả.

Probe cap 1800 CPU-s; panel subset cap 7200 CPU-s; toàn Phase 6 cap14400
CPU-s, cộng dồn cả tests, guards, startup, failures và descendants. Một
worker và một BLAS thread. Prior upper bàn giao là1750 CPU-s, không actual.

## Giới hạn và claim

Probe không phủ c lớn của B050 (c=6); cùng class không bảo đảm mọi điểm
READY. Ba levels chỉ cung cấp finite diagnostic, không proof hội tụ.
So H1/H0a chỉ kiểm hai luật này trong plant, không causal identification,
novelty, prevalence hoặc realism. H0a fit discovery; H1 zero empirical fit
vẫn phụ thuộc A1/A2 chưa được xác nhận. Không gọi state oracle (backlog +
mode) là telemetry khả thi. G1 và các mục ownership/Understanding giữ nguyên.
CF/SUB park, R09/R10 sealed và 76 outcomes p4 chưa mở vẫn được giữ.
