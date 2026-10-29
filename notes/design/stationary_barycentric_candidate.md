# Numerical candidate — thay hệ coefficient bằng nghiệm Vandermonde tường minh

Người phụ trách: **Doan Van Tai** · 29/10/2026 · **CANDIDATE_NOT_ADOPTED**.
Phát triển khi v2baseline còn chạy, sau v1 cho thấy LU437×437 tốn hơn120CPU-s.
Không sửa source/limit/môi trường của v2 đang chạy; không đổi plant/measure/card.

Với b stable roots r_j và v_j của spectral law, bản cũ tìm c_j từ:

    sum_j c_j v_j r_j^(-i-1) = 0, i=0,...,b-2,
    sum_j c_j [v_j/(1-s)+(1+v_j)r_j/(1-r_j)] = 1.

Đặt P(t)=product_j(t-r_j). Leading coefficient trong nội suy Lagrange của
t^k, k<b-1, bằng0, suyra sum_j r_j^k/P'(r_j)=0. Vì vậy một nullvector của
b-1hàng đầu là c_j tỷ lệ r_j^(b-1)/(v_j P'(r_j)). Chia bởi đúng hàng
normalization cũ cho hệ số cuối. Đây là biến đổi đại số của cùng hệ,không
thay mô hình queue. Roots phải distinct và normalizer khác0, nếu không reject.

Triển khai dùng O(b²) phép nhân và O(b) bộ nhớ cho coefficient, tránh dense
LU O(b³)/matrixO(b²). Floating cancellation vẫn có thể khiến candidate không
đạt; **giữ nguyên interval residual certificate80digits/tolerance1e-10** để
reject, không gán nghiệm mới là chính xác chỉ vì có công thức.

Test độc lập: coefficient so denseLU trên roots thực/complex; full law so
reference ở vài integerincrements đãbiết; closedform(-2,1); corruption phải
bị certificate cũ bắt; cấm gọi denseLU trong candidate.

Candidate chưa thay ReferenceLaw trong src hay confirmation. Rootproposal
numpy_roots/certification vẫn như cũ, nên chưa hứa giải được degree12000.
Muốn đo các probe lớn bằng candidate cần prereg/version riêng trước run;
full audit và runtime/cost-tail coverage vẫn bắt buộc trước v1.3.1.
