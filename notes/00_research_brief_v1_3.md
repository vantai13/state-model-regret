# Research brief v1.3

Người phụ trách/người soạn: **Doan Van Tai** · 29/10/2026 · DL-071.
Đi cùng [contract v1.3](01_definitions_v1_3.md), tag `contract-v1.3`.
Soạn theo ủy quyền; các lựa chọn khoa học đã được tác giả xác nhận. Tác giả tự
viết lại/read-back vẫn OPEN. Brief v1.2 và draft DL-061 giữ nguyên lịch sử.

**Main RQ:** For load-changing routing actions, how do improvements in
current-state information and action-response model fidelity differ and interact
in their effect on expected decision regret?

**Vấn đề và cách hỏi.** Quyết định routing chuyển tải làm thay đổi chi phí của
hai đường. Tôi so state repair và model repair bằng bốn pipeline cùng plant và
quyền thông tin đã khai. Phase 3 điều kiện tại một snapshot; v1.3 lấy kỳ vọng
qua population P1 stationary trước quyết định, dưới Stay, tại epoch độc lập với
state. Đây là đổi estimand sau discovery, không phải bằng chứng giả thuyết đúng.

**Thiết kế.** Regime là `(λA,λB,u,κ,h,c_sw)`; μ=10, a=6, τ=1s. Primary c_sw=0.
Lưu u trực tiếp; φ=u/(μ−λB) là dẫn xuất, khác nhãn pilot η=u/2. λA không được
neo theo p_sw hoặc outcome. Y là backlog cũ, X là backlog và mode hiện tại.
Một joint law sinh p(Y), D(X|Y), π(X). S0 dùng true posterior chung giữa M0/M1;
S1 biết X, gồm hidden modes oracle. M0 là cost của mean rollout từng state;
M1 dùng true expected future cost. Oracle không biết realized future.

**Đo lường.** Giữ objective endpoint occupancy và luật hòa Stay của v1.2.
L̄_sm(c;dt) lấy kỳ vọng theo joint law; sáu contrast giữ phép trừ D19.
Primary normalization là Ḡ/C̄ref, C̄ref=L̄11: tỉ số của kỳ vọng. Stakes chỉ mô
tả, không verdict “hoặc”. εR=1%, εE=0,5% là quy ước; độ nhạy 0,5%/2% không
lật verdict. Con số giữ từ v1.2, ý nghĩa population mới không tự kế thừa. Mẫu
số 0 thì relative undefined, giữ absolute output và lý do loại riêng.

**Cái gì sẽ được kiểm?** L3R.6 có tối đa hai primary và một secondary card,
vùng theo tọa độ thiết kế, tiêu chí gộp và kiểm đa so sánh phải khóa trước CF.
“Interact” hiện chỉ mô tả qua Γ nếu không cấp một suất primary cho nó. Dấu Γ
trong vùng harm bị ép bởi identity, không là confirmation riêng. Hyp-MI là
association, chưa kiểm cơ chế RQ2; H0/H1 và ngân sách fit thuộc Phase 5. Quy
ước 1% chưa trả lời tính đáng triển khai/RQ3; điều đó thuộc Phase 7.

**D22.** Đã cam kết bổ sung đường thấy hai current backlogs nhưng giấu modes,
giữ Y và fixed M0. ḠS=F̄+V̄. Định nghĩa đã khóa; engine implementation và audit
phải xong trước Phase 4. Khi chưa có D22, claim SH chỉ nói state gồm backlog
và mode oracle, chưa nói harm do telemetry tươi.

**Phần chưa đóng.** Audit L3R.3 HOLD; khóa numerical rules, không gán K*/dt*.
dt thay đổi cả slotted law/cost, nên contract khóa họ mô hình theo dt; chưa
adopt continuous-limit target. Numerics freeze v1.3.1 phải đóng global levels,
quadrature/tail policy và route S1 trước khi L3R.7 sinh CF. Mọi regime kiểm
riêng K và dt; finite escalation và near-threshold UNRESOLVED đã khai;
u_max=10% mỗi stratum. Refinement differences không là error certificates.

**Phạm vi.** Plant fluid hai đường rời, background ngoại sinh hai mức a/μ=.6,
buffer vô hạn, action tức thời, ideal backlog, P1 stationary/one-shot, c_sw=0.
S1 là oracle thông tin, không phải feasible telemetry. Realism cả MV và SH
vẫn HOLD_UNSOURCED; chưa biết các vùng có gặp ở mạng thật không. Không diễn
giải thiếu nguồn thành OUT hoặc network validation.

**Dữ liệu và gate.** A04, mười R đã mở và 216 pilot ID đều discovery. R09/R10
giữ niêm phong, không tự đưa vào CF. Tag v1.3 cho phép viết card trên bản cố
định; chưa mở CF sampling hoặc Phase 4. Còn numerics/D22 audit, P0-V10, L8 và
Gate 3R. Understanding/T05 author-writing vẫn OPEN; G1 không đổi.
