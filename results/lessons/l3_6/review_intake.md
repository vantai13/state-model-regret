# L3.6 — tiếp nhận lesson/review, không mặc định mọi diễn giải đều đúng

Người phụ trách: **Doan Van Tai**. Nguồn nguyên byte: lesson_part1_and_review.txt,
lesson_part2.txt, lesson_part3.txt trong thư mục này. Review cung cấp tự báo
348 tests/74s và kiểm độc lập; chưa nhận là GVHD/người thật hoặc rerun local.

Đã kiểm A04/card/source guard và tự tính lại trên 38 ô: 20 lát; a01 khớp target
ở 38/38; GM nominal0 ở 34/38; upper GM/Cref≤.005 ở36/38; ≥.01 ở2/38.
Tái dựng bằng phân số từ raw decimals có max error2.8118260293981116e-19;
bản float64 dùng cho surrogate có max error1.8865117801247777e-17.
Không vi phạm feasibility ở38ô. Các số này là local measured, không chép review.

Các điểm cần giới hạn hoặc sửa:

1. **Headroom:** tại baseline đã đo của M19–M22, upperR00/Cref<.005 nên
   GM≤R00 đã đủ đảm bảo vếK. Không từ đó nói “bất kể thayM0thế nào” vì thay
   baselinepolicy có thể đổi chính R00. P3 bị giới hạn bởi GS=0 và headroom ở
   chính hai ô của nó; card không đổi.
2. **E[Delta_hat]=0** là trung bình bằng0; không tự chứng minh từng state gap0,
   không tự chứng minh không có idle hoặc mô hình “mù” trên mọi state. a00=Stay
   là kết luận trực tiếp theo luật hòa. Chưa dựng lại state tables để chứng minh
   nhận xét vật lý mạnh hơn, vì không cần cho addendum/fit.
3. **rho=0** vẫn sinh Gamma>0 và GS<0 khi tau>0, như chính golden của lesson.
   Không coi thiếu rho tự động là strawman; các giả định Gaussian/rho cố định
   vẫn phải báo là giới hạn. Gaussian không có dynamics chỉ là threshold null.
4. **Thông tin chung:** cho hai bên cùng quyền dùnglambdaA không chứng minh
   mọi leakage/endogeneity bias đã hết; hai họ feature có thể tận dụng nó khác
   nhau. Nếu chọn D25(ii), claim chỉ là predictive comparison có điều kiện trên
   thiết kế neo, không causal value hoặc absolute forecast accuracy độc lập.
5. **Base rate phải cùng sự kiện:** (34/38)^4=.6408867335 là heuristic cho
   GMnominal=0. Nếu C1 được khóa thành equivalence GM/Cref≤.005, base rate đúng
   sự kiện đó là36/38, heuristic(36/38)^4=.8055186808. Báo cả hai, không gắn
   .64 cho một luật equivalence yếu hơn. K5(36/38)^2=.8975069252.
6. **Enclosure của MAE:** mỗi absolute loss có kink tại dự báo; min không luôn
   nằm ở đầu mút. Với paired difference |p0−y|−|p1−y|, hàm đơn điệu nên chỉ
   cần hai đầu mút cho d. Code dùng cách thứ hai và kiểm độc lập bằng dữ liệu giả.
7. **D≥m** chỉ là điều kiện phân biệt cần; không chứng minh statistical power
   hoặc khả năng mọi kết luận đều có thể xảy ra trong plant thật. D<m chắc chắn
   không thể đạt margin; giữ luật không mở cho comparison đó.
8. **kappa là thời gian nhớ**, không phải switching rate: r2_keep dùng
   exp(−2dt/kappa). Mọi variance feature phải dùng convention này. Không đảo
   kappa thành rate khi đưa công thức telegraph vào prereg.

Lựa chọn D25 và phạm vi A05-F đang được hỏi tác giả trước khi chốt prereg.
Các phép tính/kiểm toán ở đây chỉ dùng A04 hoặc toy, không target held-out outcomes.
