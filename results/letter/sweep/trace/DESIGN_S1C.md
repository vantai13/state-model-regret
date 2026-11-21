# S1-C — thiết kế khám phá trước pilot

Người phụ trách: **Doan Van Tai**. AI hỗ trợ thiết kế và hiện thực theo brief S1-C
21/11/2026. Không phải xác nhận hypothesis hay tác giả tự dự đoán. Không commit,
SSH, tải mới hoặc chạy full sweep trong phiên này. Chỉ tạo ba source được phép
và artifact dưới `results/letter/sweep/trace/`. Không đụng nhánh S1-A.

## Dữ liệu và mô hình

Dùng `s0`, `s1` (hai tập flow rời nhau) của ba NPZ có sẵn: DITL 2023-04-12
4 giờ, MAWI 2025-03-11 và 2026-04-14 khoảng 15 phút/ngày. Bin 10 ms; giữ cùng
thời gian A/B. Các đoạn DITL 10:00 và 12:00, bản mod250, c1 trùng, c25 nén
chỉ được kiểm kê, không thêm thành ngày độc lập trong sweep.

Mô hình lấy từ EV-D4b/c: background Poisson có cường độ theo count trace,
managed flow Poisson độc lập, hai hàng đợi FIFO, service exponential, c_sw=0.
Chi phí là tích phân **tổng số packet của cả hai queue**, đơn vị packet·s.
Đây là cấu trúc tốc độ đo thật + packet/service tổng hợp, không phải replay
nguyên packet của PCAP hay topology/production network thật. Hai path thực
nghiệm là flow partitions cùng một link, không phải hai link vật lý đã đo.

Khác triển khai EV cũ: không lặp trace, không đổi pha, không chuẩn hóa bằng
toàn trace, cho phép service capacities khác nhau, chỉ dùng đoạn test hữu hạn.
Queue bắt đầu rỗng ở đầu mỗi train/test; test dùng lịch sử action 0 (managed
ở A), có warmup trước mọi quan sát. Các action tương lai dùng đúng pending
packets và residual services trong lịch sử chung, không reset queue tại epoch.

## Chia thời gian, pipeline và điểm quyết định

- Bỏ bin cuối để tránh dùng bin chưa đủ. Nửa đầu train, nửa sau test; không
  lặp/wrap qua biên. Test có seed riêng, không phải một ngày chưa từng exposed.
- Train-prefix mean của từng key dùng để scale cường độ cho cả train và test;
  test không được renormalize. `lam=[6.5,6.8]*scale`, managed rate `u=1` packet/s.
- Train chạy cả hai action với CRN. Bỏ 10% đầu train, tính time-average cost
  rate thực nghiệm mỗi action; ŝ = mean_switch − mean_stay, đơn vị packets.
  Đây là finite-train estimate, không tự nhận stationary slope chính xác.
- T_int: autocorrelation integral của tổng queue trong train/action 0, sample
  0.2 s, FFT/first zero giống `packet.tint`. Nếu censored/không xác định:
  NOT_EVALUABLE, không thay bằng timescale thuận lợi khác.
- M0: gap fluid switch − stay trên backlog quan sát, mean rates train;
  static: `1{ŝ<0}`; hybrid: `1{gap_fluid+h*ŝ<0}`; tie chọn action 0.
  Fresh τ=0 là so sánh trạng thái hiện tại; các τ>0 là plug-in stale.
- Oracle: min hai cost trên **cùng realized future**; C_ref là realized-path
  lower bound, không phải oracle lấy kỳ vọng điều kiện hay chứng nhận CTMC.
- τ={0,1,10,30,60,120,300} s; h/T_int={0.3,0.5,1,2,3,5,10}.
- Candidate grid đều trên test từ `max(10,2*T_int)+max(τ)` đến
  `duration_test−0.3*T_int`. Dùng cùng grid cho mọi h; mỗi h chỉ loại tail
  thiếu future, lưu số thiếu và n thực tế. N=24 pilot, N=128 full.
- Alarm là cùng candidate grid có `q_static(t−τ)≥max(1,train q90)`; threshold
  train lấy queue của path static chọn trong lịch sử action 0. Đây là
  occupancy-conditioned alarm, không phải first passage, retrigger hay loop.
  Không chọn epoch dựa trên future cost, bất đồng hay regret.

## Grid, metric và suy luận

3 ngày × scale {0.8,1,1.2} × capacity pairs {(10,10),(9.5,10.5),(10.5,9.5)}
= **27 cấu hình**, không coi là 27 ngày độc lập. Giữ đủ cả hai population
uniform và alarm, toàn bộ h/τ; thiếu alarm hoặc horizon không đổi thành 0.

Metric chính: mean paired `regret_static − regret_hybrid` trên **toàn bộ
epoch hợp lệ** của population/h/τ, dương là hybrid tốt hơn. Báo cả hai regret,
regret M0, mean C_ref, đơn vị packet·s và `100*mean(delta)/mean(C_ref)`;
không tính bình quân các % khi C_ref nhỏ. Phụ: numerator/denominator bất đồng,
regret và paired gain khi bất đồng, q90 regret, exact tie share của M0.

CI 95% descriptive theo 8 đoạn thời gian cố định trong phần test: Student-t
trên các block means có epoch, báo riêng center theo block và mean theo epoch
(hai trọng số khác nhau khi block thiếu mẫu). Futures có thể overlap, block
có thể còn tương quan: không xem epoch độc lập hoặc coi đây là population CI.
Tổng hợp ngày: gộp đều các cấu hình available trong từng ngày, rồi Student-t
trên day means; dưới 2 ngày thì CI=null. Chỉ tối đa 3 ngày và coverage khác nhau
theo h; không suy ra external validity rộng hoặc chọn vùng dựa trên CI này.

Pilot duy nhất: **DITL scale1.2, mu=(9.5,10.5)**, chọn trước outcome vì input
dài, tải cao. Pilot seed 211121, full seed 311121, test seed +1000000; ngày sau
cộng 100/200. Không có ngưỡng PASS/FAIL cho lợi ích hoặc bất đồng, không cứu
signal bằng đổi grid sau pilot. Forecast: lợi ích/bất đồng chưa biết; h dài có
thể về static. Kết quả pilot chỉ exploratory, không là claim đưa vào paper.

## Kiểm chứng, CPU và handoff

Kiểm cost với Lindley integral, gap với closed form/EV equal-capacity,
u=0 CRN, replay action0 khớp integral lịch sử, residual services, giữ future
giữa τ và h, train không đổi khi thay test tail, thiếu dữ liệu, CI theo block,
write-once và input hashes. Tái chạy một train case EV-D4b nguyên cấu hình để
đối chiếu mean_stay, mean_switch, ŝ, T_int với JSON có sẵn; không chạy test EV.

Đo process CPU và wall pilot. Dự phóng dùng train CPU cộng replay CPU scale
128/24, nhân 27 cấu hình như đều dài 4 giờ; báo ideal wall/15 và stress ×3.
Không phải upper bound, CI, cloud benchmark hoặc bảo đảm chi phí. Script GCP
verify source/data hashes, ghi raw manifest trước summary, chạy workers15,
không SSH/poweroff, không overwrite kết quả cũ. Chỉ Claude launch full.

Không tra literature/tải mới. Nếu cần mở rộng, ưu tiên khung liên tục dài hơn
trên các ngày khác và dữ liệu hai link/queue thực tế; đây là đề xuất nhu cầu
dữ liệu, chưa khẳng định một nguồn cụ thể đang cung cấp chúng.
