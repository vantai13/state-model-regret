# Numerics candidate — cùng P1, biểu diễn có kiểm sai số

Người phụ trách: **Doan Van Tai**. Trạng thái: CANDIDATE, chưa tạo v1.3.1.
Không đổi plant, arrival/managed rates, R2, age1s, h, objective D13, card hoặc
R1–R8. Những thuật toán/mức còn DEFERRED được khai trước calibration mới.

## 1. Phân phối và moment vô hạn

Giữ spectral proposals/refinement80digits và cùng residual/return-time/tail
certificate. Native dyadic products dùng cpp_int chính xác,384binarybits;
chỉ thay cách tính các tích P'(r). Complex center và radius L∞ được nhân bằng
số nguyên; mỗi lần bỏ bit tăng radius theo hướng ngoài. Cây tích cân bằng
giữ độ sâu log. Các roots là dữ liệu decimal80 cố định, không giả định Newton
đã tìm exact polynomial roots. Residual F(r) vẫn có trong certificate.

Duplicate check dùng lưới1e-40 với9ô lân cận và cùng distance threshold; count
b roots, decay, nonzero normalizer và lỗi stored coefficients vẫn bắt buộc.
Original spectral certificate kiểm độc lập ở small cases; native product có
reference160digits trên các input decimal đã khai. Cache gắn input, source
fingerprint, package version và SHA256; không sửa/ghi đè cache không khớp.

Forward evaluation dùng integer powers bằng multiplication có error radius,
không dựa vào một cam kết sai số ngầm của complex pow. CDF-mass bounds,
posterior và stationary error báo riêng. Chỉ project vào probability domain
khi interval chứng nhận có giao; cộng phần dịch vào error, không bỏ mass.

Mean Q không suy từ TV đơn thuần. Trên[0,N] dùng2N*law_error; cộng true moment
tail từ Chernoff prefactor/theta và spectral absolute moment tail. Geometric
first moment của spectral law được đánh giá interval80digits, rồi cộng lỗi
conversion. Đây numerical tail, không finite physical buffer.

## 2. Bellman trên lattice thật

Lấy quantum gcd của cả hai action và stationary lattice. Increment của mọi
action là integer đúng. W_t(q,m) là weighted idle cost raw units:

    W_t(q,m)=t max(0,-q-a_m)+sum_n P_mn W_(t-1)(max(0,q+a_m),n).

Biểu diễn piecewise affine trên integer knots. Shift/clip/Bellman là đúng trên
lattice; sau đó chỉ nén biểu diễn. Error giữa chord mới và tất cả knot cũ được
đo; giữa knots là affine nên bound có hiệu lực toàn miền. Propagation là
nonexpansive sup norm; cộng compression error, probability perturbation và
roundoff allowance1024eps*(max_value+reward+1) mỗi bước. Không đổi dynamics
sang coarse/fluid queue. Bên ngoài maximum possible drain, idle đúngzero.

M0 mean path dùng tổng các hinges của running deficit; thêm floor/ceil của
threshold vào integer knots để giữ đúng giá trị tại mọi state lattice.
R2/power/sum/conversion error cộng riêng. Age expectation dùng cùng Bellman
transition, không reward, và error budget riêng. Uniform cost budget mỗi
action/age là min(1e-4,h²/1e7) packet*s; bounds đo được vẫn được báo thực tế.

Saturation M0 OFF khi slot đầu empty và toàn bộ mean net âm có triangular
managed-load difference chính xác. Hai queue có opposite contribution nên
joint mean tie được chứng nhận bằng identity, không epsilon. u0 cho identical
actions và sáu contrasts zero chính xác. Các action chưa định được vì arithmetic
được bound cả loss possibilities, không ngầm gọi Stay là nghiệm đã chứng nhận.

## 3. Population integration

P1 + Stay giữ đúng stationary law, vì thế E[JStay]=h E[QA+QB]. Mean/tail ở§1
chứng nhận lớp này, không bỏ tail rồi renormalize. S1 tích phân trực tiếp π,
đúng lựa chọn còn mở của contract. S0 lấy conditional old-mode posterior thật
và age-expectations của true/M0 gaps; giữ chung D giữa models.

Quadrature giữ riêng atom q0; chia phần positive trên support hữu hạn của
gaps thành K equal-mass bins, representative median; tail ngoài support thành
atom zero-feature theo mode. Tail ở đây có probability thật; cost tuyến tính
đã nằm trong moment đầy đủ, không đổi thành zero cost hoặc finite buffer.
Mode weights là CDF differences của từng bin, không posterior tại representative
cho S1. S0 posterior tại representative là numerical quadrature như khai.

K-quadrature sai khác vẫn là diagnostic theoR7, KHÔNG là certified total error.
R1 kiểm cả raw-scale/ratio/Cref, riêng K/dt. Kernel/roundoff/weight/moment và
action ambiguity có bounds riêng; R6 dùng cả arithmetic interval và measured
refinement khi xét near-threshold. Scorer card, thresholds và R4/R5 không đổi.

## 4. Chọn mức, timing và giới hạn

Prereg máy đọc khóa corners +8auditIDs, thêm các rational-rate designs xác định,
không sample thử từ vùng. Stage0 replay3anchors và6marginal tests trước mở full
calibration. Candidates hữu hạn80/2 →160/2 →160/4; mỗi mức có cả hai coarse axes.
Chọn mức đầu có toàn bộ R1/arithmetic/validity checks đạt. Nếu không đạt: HOLD,
không tự tạo tag, n, root hoặc CF.

Timing bundle tính cold charges theo unique law/profile keys kể cả khi cache
đã được tạo bởi một calibration khác; báo riêng actual CPU và planning charge.
P95(method=higher) theo lớp rational-rate và corner/audit được báo riêng; lấy
lớn hơn làm planning p95 đã khai trước, không coi là population p95 guarantee.
B48CPUh và luật n vẫn giữ; không tăng n để bù numerical unresolved.

Chỉ sau full audit/controls/coverage/timing mới có thể ghi spec/receipt/tag mới
v1.3.1. Dry-run B sau đó chỉ chạy dữ liệu discovery/calibration đã thấy. Không
CF engine trong lesson7; Phase4 còn D22, human và Gate3R. Không tự đóng Understanding.
