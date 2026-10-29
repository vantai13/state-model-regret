# Candidate: nhân khoảng theo cây cân bằng

Người phụ trách: **Doan Van Tai** · 29/10/2026 · CANDIDATE_NOT_ADOPTED.

Candidate02 dừng sau 1260.709 giây ở `normalizer not certified nonzero`.
Đó là thất bại chứng nhận, không chứng minh normalizer thật bằng zero và không
phải lỗi thiếu RAM. Giữ nguyên toàn bộ raw và không chạy03/04 theo stop rule.

Nguyên nhân cần xử lý là wrapping của phép nhân các hình chữ nhật phức: một
left-fold dài có thể bao quá rộng dù mỗi factor rất chính xác. Regression độc lập
dùng 1024 factor quanh 1+i: tâm tích đúng là 2^512; left-fold chứa zero còn tích
theo cây giữ enclosure chặt. Đây toy interval arithmetic, không outcome nghiên cứu.

`BalancedProduct` ghép các nhóm cùng kích thước như binary counter, rồi ghép
các nhóm còn lại. Mỗi factor xuất hiện đúng một lần. Chỉ thay cách đặt ngoặc của
phép nhân; dùng interval arithmetic với outward rounding ở mọi node. Độ sâu
biểu thức O(log b), bộ nhớ cho toàn bộ derivatives O(b log b), không hạ precision.

Các công thức target coefficients, normalization, residual, stored-coefficient
L1 error, tail và return bound giữ nguyên từ algebraic candidate. Ngưỡng law
1e-10, posterior1e-8 và precision80 giữ nguyên. Không dùng midpoint của một
interval bao zero để ép chứng nhận; normalizer vẫn phải được certify nonzero.

Kiểm trước profile: exact factorial products qua các kích thước khác nhau;
regression wrapping; original certificate/quantiles trên small queue; independent
150-digit closed-form complete TV+tail; corrupt coefficient phải bị reject.
Global cost/accuracy audit và adoption vẫn chưa hoàn tất. Không đổi plant,
rounding, card, n/root/CF hoặc tag contract đã khóa.
