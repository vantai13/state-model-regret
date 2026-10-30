# Mandatory sealed-coordinate guard — trước native outcomes

Người phụ trách: **Doan Van Tai**. AI phát hiện giao tọa độ khi kiểm metadata.
Không nới hoặc miễn niêm phong R09/R10; không phải lựa chọn card/Gate4.

Nguồn thiết kế `notes/design/grid_v1_2.json` cho R10=(15/2,8,u1,κ3/5,h4,c_sw0).
Map3age XA097 ở age1/2 cóκ3/10,h2; quy age1 cho đúng tuple đó. Nó đã nằm trong
planA466, nativeID **P43_0628**. R09 không giao. Không điểm nào trong14PartAreplays
giao với R09/R10. Chưa gọi native khi phát hiện; K2/K6 thiếu input vẫn giữ nguyên.

Phạm vi đã chọn vẫn lưu **666tọa độ/684aliases**. Vì yêu cầu niêm phong có trước,
ghi P43_0628/XA097 là **SEALED_BLOCKED**, không gọi engine hoặc thay bằng điểm khác.
Nếu tới full run, chỉ schedule665tọa độ còn lại. Dòng bị chặn vẫn ở alias ledger,
không âm thầm đổi denominator A466 thành465 hoặc gọi full666 đã hoàn tất.
Các tỷ lệ/forecast toàn scope phải ghi partial/NOT_EVALUABLE khi thiếu điểm này.

`sealed_guard.py` là entrypoint bổ sung quanh resource_v2. Child worker được guard
trước native import; scheduler lọc chỉ theo hai sealed physical keys. Giữ nguyên
nguồn engine, parameters của665ca khác, three levels, R1, tolerance0.25pp, stop/HOLD.
Budget vẫn tính theo full scope ban đầu, là dự toán bảo thủ; không thay budgetCF.

Metadata exposure: lệnhrg ban đầu đã hiện dòng bảng thiết kế R09/R10 gồm tọa độ,
ψ/p_sw và budget cũ; các field đó không được dùng để chọn vùng, features hoặc metric.
JSON check chỉ chọn coordinates. Không D/J/gap/regret/contrast held-out mới được tính.
Giao physical key không tự đồng nhất estimand population pilot với A05-T conditional
snapshot; dù vậy không thực hiện thêm outcome ở key niêm phong.
