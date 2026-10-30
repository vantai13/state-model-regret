# Candidate đánh giá posterior bằng dyadic intervals

Người phụ trách: **Doan Van Tai**. Candidate độc lập, **chưa adopted**; không
thay source hoặc runtime của recovery04 đang chạy.

Đích số học vẫn là các decimal80digits đã lưu trong spectral law. Mỗi complex
box biểu diễn `(re ± rad, im ± rad) * 2**exp` bằng số nguyên. Decimal được làm
tròn xuống ở384bits và cộng1ulp vào radius. Khi truncate/align, radius luôn
làm tròn lên và cộng1ulp cho dịch tâm. Với hai boxes, common-radius của tích là

`(|ar|+|ai|)*brad + (|br|+|bi|)*arad + 2*arad*brad`.

Cộng box dùng exponent lớn hơn, bao cả phần dịch tâm; tổng khởi tạo zero được
xử lý chính xác để tránh mất precision. Lũy thừa nguyên dùng repeated squaring,
không complex libm pow. Cộng spectral terms sau mỗi tích giữ enclosure; q0 dùng
atom riêng. Không dựng dense PMF hoặc đặt physical buffer. Ngân sách số học
native q≤2^40 và ≤20000terms là guard thực thi, không cắt distribution/tail.

Sau point sums, chuyển lại interval80digits với outward rounding. Giữ nguyên
infinite-law error, positive conditioning check và công thức posterior reference:
`2*law_error/positive_mass_lower + interval_ratio_width + 4e-16`, giới hạn1e-8.
Conversion sang longdouble cộng allowance như code fast cũ. Không sửa certificate
law, threshold, plant, objective, rounding, K/ref hoặc card.

Tests đối chiếu complex sums có cancellation với Fraction chính xác; atom q0;
posterior với reference interval cũ; điều kiện xác suất không chứng nhận;
positive mass nhưng posterior quá sai số vẫn reject; integer exponent guards;
underflow ở số mũ lớn và fallback cache. Chúng không phải full population audit.

Benchmark đã đăng ký chỉ đọc law cache đã có của
`lambda=7123/1000, managed=617/500, kappa=3, ref=2`, tại ba q
`916318,1341550,1450400` đã có trong diagnostic DL-088. Ba lượt cho mỗi evaluator,
báo từng lượt CPU/wall và median; compile/setup báo riêng. Chạy local trên cùng
cached decimals, không suy speedup GCP hoặc p95 population. Không sinh law mới,
joint regime, mẫu thử từ measure, CF hoặc seed. Nếu law cache không khớp
parameters/source/SHA thì từ chối benchmark.

Adoption nếu cần sẽ có prereg/version riêng và full replay registered batch;
không chèn candidate vào recovery04 hoặc sửa kết quả đã có.
