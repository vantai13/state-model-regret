# Part B tối thiểu — một hộp mỗi candidate, trước mọi count

Người phụ trách: **Doan Van Tai**. AI soạn theo ủy quyền; tác giả chọn rõ
“Chạy một hộp SUB (khuyến nghị)”. Không có author self-writing/human review.

SV dùng nguyên 449/48 keys và baseline A1, một box envelope; 7 discovery keys
khác trong plus envelope ngoài support, không giả đã có native coverage.
SUB giữ toàn bộ76 fixed-plant keys trong delta[1/4,1/2],kappa[1/20,3/20],
eta[5/8,7/8],h[4,8],lambdaA/B[6,17/2],c_sw0. Không lọc nhãn pilot hoặc A/AB.
Cả hai hộp được commit một lần trước counts; không hộp thứ hai sau FAIL.

Không viết freezer/runner mới: explicit cases_source của A1, kindL44 chỉ là
adapter đọc danh sách. Main640/ref8 cần neighbors320/ref8 và640/ref4 như
SUB_PROBE; không chạy một row đơn rồi bỏ R1. Control/benchmark/budget/full
và BUG guards nguyên bản. Cap8CPUh,2workers,1BLASthread; NOT_READYcap1 để giữ
unresolved vào screening, không sửa readiness. Hỏng execution/BUG/cap thìdừng.

SUB chọn rho trên READY subset bằng mean normalized regret,target00,tieexact
chọnrho nhỏ hơn, gridcũ; báo toàn bộ exclusions. ReadingMV+A khôngđổi: median
recovery>=1/2 thì câuSUB kèm “so với controller không margin”. Không thaymetric
Gamma hoặc threshold-1%. Không sample split/measure weighting mới.

Sàng đúng một hộp/candidate với kernel/power/haircut/Ucap v1 nguyên byte.
PASS_SCREEN -> thêm một card theo ủy quyền; fail/validity-block -> không thêm.
Narrow baseline chỉ đổi câu claim, không đổi luật power. Kết thúc bằngDL0/1/2
card; không tự chạyCF/Phase5, không numerical rabbit hole A4 hoặc hộp bổ sung.
