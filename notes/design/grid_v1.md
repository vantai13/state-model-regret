# L1.8C — thiết kế lưới v1

Người thực hiện: **Doan Van Tai** · 22/10/2026.

Cấu hình này được tác giả chọn bằng câu trả lời “Dùng cấu hình đề xuất để khóa v1 có điều kiện” ngày 22/10/2026. Đây là thiết kế nghiên cứu lý tưởng hóa, không phải tham số đã đo trên mạng. Giá trị máy đọc: [grid_v1.json](grid_v1.json). Không chọn ô theo gain hoặc margin.

| Đại lượng | Giá trị / quy tắc |
|---|---|
| Capacity A/B | Cùng μ=10 packet/s ở hệ chuẩn; backlog fluid có thể phân số |
| Nền A | Deterministic 5 packet/s; ρA_pre=(5+u)/10 <1 cho cả main và stress |
| Nền B | OFF=2, ON=14 packet/s; mode đối xứng, trung bình 8 packet/s; ρB=.8 |
| Age hiệu dụng | 1 s; diagnostic action tức thời, không cộng thêm actuation delay lần nữa |
| z | {1/3,1,3,10}; yB=2z packet; yA=yB |
| κ | {.3,1,3}; Tmode=κ s; R2: keep=(1+exp(-2dt/Tmode))/2 |
| η | {.5,.9}; u=2η packet/s; main post-load B=.9 hoặc .98 <1 |
| Horizon main | h=Tdrain_post=z/(1−η) s; từ 2/3 đến 100 s |
| Slot ứng viên của lưới | dt=age/120=1/120 s; không phải slot cuối đã qua calibration |
| Quy đổi hai neo | Nếu chọn age(a)=5 ms, age(b)=200 ms, dt lưới tương ứng 0.0416667 ms và 1.666667 ms. Slot minh họa A (.12/12 ms) giữ trong lịch sử, không tự coi đạt ngưỡng v1 |

24 tổ hợp factorial M01–M24 được giữ toàn bộ. N01: yA=yB=100, κ=.3, η=.5, h=.5s; N02: cùng backlog100, κ=3, η=.9, h=1s. Hai ô kiểm âm có z=50, cố ý override h/Tdrain_post. S01: z=1,κ=.3,η=1.5,h=1s; S02: z=3,κ=3,η=1.5,h=3s. Stress có Tdrain_post=∞; quy tắc h=Tdrain_pre hữu hạn, không chia cho số âm. Tổng **28 ô**, không loại ô theo diagnostic.

Calibration khai báo trước: **M01, M02, M10** (z=1/3,κ=.3,η=.5/.9 và z=1,κ=1,η=.9). Dùng calibration chọn slot, không gọi những ô này là confirmation. Sau tag contract-v1 mới được tính J/gap/contrast của các ô này.

Reserve: z={.6,2,5} × κ={.6,2} × η={.5,.9}: 12 ô held-out; cộng z=30 × κ={.6,2} × η={.5,.9}: 4 ô extrapolation. Chỉ khai báo tọa độ; không sinh D, không screen, không tính outcome ở reserve trong L1.8. Những giá trị này có thể từng xuất hiện đơn lẻ ở lesson; chưa có outcome của các tổ hợp/profile này trong phiên này. Trước confirmation phải audit exposure ngoài phiên và khóa A05.

D chính: **dừng có điều kiện của queue B trước quyết định**, không phải mode .5 độc lập y. Queue A khởi tạo có kiểm soát ở yA; không khẳng định yA>0 thuộc phân phối dừng của A. Từ thời điểm đo đến t0 chạy plant dưới Stay, quan sát một snapshot backlog có timestamp, không có nhiễu hoặc mode. S0 gọi cùng law từ observation/law đã khai báo, không nhận realization evaluator; một belief dùng chung cho M0/M1.

## Prior B vô hạn và công thức kiểm được

Quantum backlog B trước quyết định là d=4dt packet. OFF giảm 2d, ON tăng d. yB/d=60z nguyên ở slot ứng viên và mọi mức chia đôi, kể cả reserve. Đặt s=keep và r là nghiệm dương <1 của s r²+(1−s)r−s=0. Với b=r(1+r), A=[b/(1−s)+(1+b)r/(1−r)]⁻¹:

- q≥1: π(q,off)=Ar^q; π(q,on)=Abr^q.
- q=0: π(0,off)=Asb/(1−s); π(0,on)=Ab.
- P(on|q>0)=b/(1+b); P(on|q=0)=1−s.

Chuẩn hóa bằng tổng geometric vô hạn; kiểm stationarity bằng tổng dòng vào từng state và marginal mode=.5. Không cắt đuôi/không warm-up. P(on|0)=1−s ở đây đúng vì ON luôn để lại backlog d>0; không phải định lý cho mọi rate ON. Khi làm mịn phải tính lại prior của plant rời rạc tương ứng; đây là một phần sai số rời rạc hóa của D, không giả D giống hệt giữa các mức.

## Ba diagnostic trước outcome

Chỉ tính: (1) s_bt, mass của state không queue nào có thể idle dưới cả hai action; (2) ratios timescale; (3) ước lượng operation/memory và thời gian thực chạy diagnostic. Giữ mode slot0, OFF từ slot1 là path ít arrival nhất vì R2 hữu hạn có mọi transition dương. Q=0/embedding identity không thỏa điều kiện này. Kiểm idle bằng bất đẳng thức **q+a<c**; chạm 0 bằng đúng capacity không đủ.

Sàng lọc không chứng minh effect khác 0, không chứng minh tính đại diện của mạng. Không tính margin/true action values để chọn thiết kế. Nhánh negative controls được xác nhận bảo toàn bằng s_bt, chưa chạy pipeline contrast trên chúng trước tag.

Budget trong CSV là upper bound cho dense rational-grid DP (không phải measured simulation runtime). Không mặc định mọi ô chạy rẻ: h tới100s và tinh lưới có thể rất đắt. Budget A01: tối đa 2×10⁹ scalar state-mode-action updates và 1 GiB workspace ước lượng mỗi ô/mức, slot tới dt/128. Nếu quá budget: tối ưu thuật toán rồi ghi NARROW/HOLD, giữ ô và nguyên threshold; không bỏ outcome khó. Chưa benchmark full-grid J.

## A01 sau tag: chọn độ phân giải

Khởi đầu ba mức dt,dt/2,dt/4 ở M01/M02/M10; tiếp tục chia đôi đến dt/128 nếu cần. Mọi rate vật lý, age,h,y,u,Tmode giữ nguyên; lượng/slot và prior D thay theo dt. Cref **mỗi ô và mỗi mức** là Lstar tại cùng mức. Với cả sáu contrast: |G(coarse)−G(fine)| ≤ .0025*Cref(fine), không có sign flip khi magnitude vượt vùng equivalence .005*Cref(fine). Báo level fine của cặp đạt; kiểm triplet gần nhất, rho và Richardson chỉ diagnostic, flat để undefined. Nếu không ổn định hoặc không đạt budget thì A01 HOLD, không chứng nhận limit hoặc equivalence. Không ép rho≈.5 cho mọi metric; Part B đã cho phản ví dụ convergence không đều.

Slot được chấp nhận theo protocol này vẫn cần kiểm adjacent-level trên từng ô A04; cell fail được báo fail và refine, không suy ba calibration chứng minh mọi ô. Sensitivity εR=.5%/2% giữ εE=.5% và error budget .25%; mức .5% có practical/equivalence boundary trùng nhau, báo bằng hai flags, không gọi verdict() vốn yêu cầu εE<εR. Không dùng sensitivity để đổi primary1%.

## Sửa điểm sai của tài liệu nguồn

Một finite grid không đóng vô hạn khi net arrival dương. Kernel tạo các tập reachable **hữu hạn theo horizon**, không clamp upper backlog. Tách J_A+J_B cho action cố định và cost cộng dựa trên tuyến tính của kỳ vọng, **không cần nền độc lập** nếu dùng đúng marginals. Shared capacity/coupled dynamics làm hỏng việc giải riêng; tương quan có thể làm thay đổi joint belief. Hai ví dụ dạy cũ giữ η=4,ρA=1 riêng, không nhập làm main grid. Các con số này không được điều chỉnh theo outcome.
