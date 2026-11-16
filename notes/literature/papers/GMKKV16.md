# GMKKV16 — Govindan et al., "Evolve or Die", SIGCOMM 2016

Người phụ trách: **Doan Van Tai** · 16/11/2026 · tác giả tải PDF và yêu cầu chọn bài hợp lý để trích; **AI-T (Claude)**, tác giả tự đọc: chưa xác nhận.

R. Govindan, I. Minei, M. Kallahalla, B. Koley, A. Vahdat, "Evolve or Die: High-Availability Design Principles Drawn from Google's Network Infrastructure", *Proc. ACM SIGCOMM 2016*, pp. 58–72, [DOI 10.1145/2934872.2934891](https://doi.org/10.1145/2934872.2934891). Bản đọc: PDF ACM do tác giả tải, lưu ngoài Git `~/papers/state-model-regret/letter_story/Govindan_SIGCOMM2016.pdf`, sha256 `c7a0fd97…a9fa`.

**Câu hỏi:** có nguồn vận hành thật cho quyết định giữ hàng giờ, được đánh giá bằng mô hình trước khi làm, không? Mục đích như CMN12.

**Đã đọc (targeted):** §2–3 phần ràng buộc vận hành (PDF tr.4–5); §4 risk-assessment failures (PDF tr.9).
- **PDF tr.4:** "upgrading a border router can take more than 8 hours"; có thể drain dịch vụ khỏi cluster bị ảnh hưởng trong lúc nâng cấp.
- **PDF tr.5:** mỗi management operation (MOp) có tài liệu, thời lượng ước tính và đánh giá rủi ro; MOp rủi ro cao thì "operators drain affected services before executing the MOp".
- **PDF tr.9 (Risk-1, Risk-2):** một MOp "scheduled to last over 30 hours" dùng đánh giá rủi ro đơn giản hóa, dự đoán giảm khoảng 30% dung lượng, thực tế giảm hơn 50%. Một MOp khác "scheduled to last five days" đánh giá thấp dung lượng dư nhỏ nhất 2 lần; cùng với lỗi đồng thời, gây mất gói.

**Dùng trong letter:** thao tác vận hành được giữ từ hàng giờ đến nhiều ngày, và quyết định dựa trên đánh giá trước bằng mô hình đơn giản hóa có thể sai.
**Không được nói:** lỗi ở đây là ước lượng dung lượng, không phải do telemetry tươi hay hàng đợi ngẫu nhiên; không gán cơ chế SMR cho các sự cố này.
