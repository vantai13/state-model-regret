# L44_PROBE A2 — probe R3 sau HOLD baseline, 31/10/2026

Người phụ trách: **Doan Van Tai**. Thiết kế nguồn do AI (Claude) soạn và người dùng
cung cấp; phần triển khai, lựa chọn chi tiết và forecast do AI soạn theo ủy quyền
trước đó và yêu cầu tiếp tục hiện tại. Không phải tác giả tự viết hoặc human review.
Trạng thái: ADOPTED_BY_AUTHOR_DELEGATION; choices/forecast do AI soạn theo ủy quyền, chưa gọi engine A2.

## Premise và câu hỏi

Diagnosis đã commit: 19 điểm A1 / 95 cặp; 8 failing pairs tại 8 điểm, mỗi điểm một
rho, W3/K6/D3; L00 và GS_theta là các fields vượt tolerance. Các điểm đều ở góc
lambdaA=7,lambdaB=6. Có 25 cặp không fail dù jump>5%Cref. Không coi 8/72 là estimate
prevalence, hoặc staircase trên lưới là bằng chứng cơ chế vật lý.

H_res: tăng resolution có thể làm đủ mọi rho cùng READY. H_cliff: dữ liệu có thể
vẫn ill-conditioned tại margin, lỗi giữ nguyên hoặc chuyển rho. Đây là hai giả
thuyết vận hành của probe; finite ladder không chứng minh một nguyên nhân duy nhất.

## Giữ và thay đổi

Giữ nguyên toàn bộ engine, code và artifacts A1; lưới rho; row_readiness và
baseline_readiness của A1; R1, arithmetic width, lean consistency và BUG checks.
Không chọn rho, không tính R_M/GS regional medians, không gọi CF/sealed outcomes.

Chỉ thêm các level thuộc thang scorer đã frozen: main640/4 ->1280/4 ->1280/8,
mỗi main cùng hai coarse neighbors. Đo đủ cả 7 levels cho cả 8 điểm; không chọn
subset hoặc dừng sớm khi một bậc đã READY. Decision dùng first READY trong ladder,
đúng nghĩa scorer dừng tại bước đầu phân giải được; vẫn báo mọi bậc để thấy
non-monotonicity. Control u0 ở1280/8. Budget3CPUh, một worker, mỗi process3600CPU-s,
4800wall-s,3GiB; budget tính unique evaluation CPU gồm control và kiểm giữa các điểm.

Replay 3 level cũ phải khớp mọi saved numerical/error/baseline fields và significant
bits được parse lại từ các giá trị đã lưu; không so timing/cache metadata hoặc ABI
padding. Pin SHA cả A1 raw rows và comparisons. Mismatch/BUG/guard/execution failure
thì dừng trước level/điểm kế tiếp, giữ artifacts; không quyết định trên run thiếu/lỗi.

## Luật quyết định khóa trước probe

- >=7/8 READY ở ít nhất một bậc: LADDER_RESOLVES, đề xuất A3 full90 với escalation
  trước khi tính NOT_READY, cap theo phương án đã khai.
- <=4/8: B1_CLAIM_LEVEL_ROBUSTNESS (lựa chọn AI theo ủy quyền, khuyến nghị từ input).
- 5–6/8: INCONCLUSIVE_AUTHOR_DECIDES_WITH_NEW_DL; không chọn lại nhánh trong A2.

## Định nghĩa nhánh B1 cho A3 sau này

Một package/prereg A3 riêng phải rerun đủ90 điểm, không bỏ điểm NOT_READY và không
chọn rho trên19 điểm đã có. BUG/control/guard/execution failures vẫn dừng.
Trên mỗi bộ số640/4,320/4,640/2, áp lại argmin mean normalized regret theo vùng:
MV target00,SH target10,mỗi physical key một phiếu, exact tie chọn rho nhỏ hơn.
Tính luật đọc DL104 riêng tại mỗi level (MV median R_M>=1/2; SH median |GS_theta|/Cref<.5%
và median deltaL10<0). Baseline aggregate reading chỉ được gọi stable khi cả3 có
cùng rho và cùng narrow/not-narrow decision; khác nhau thì baseline UNRESOLVED.

Đây là đề xuất thay scope validity của baseline trong A3, không tương đương error
certificate hoặc R1 per-point, không sửa scorer/card/contract/CF. Stable3levels có
thể cùng bias; phải báo đầy đủ raw readiness/width/refinement và không coi nó là
confirmation/novelty. A2 chỉ khóa nhánh, chưa chạy hoặc tự chứng nhận A3 validity.
