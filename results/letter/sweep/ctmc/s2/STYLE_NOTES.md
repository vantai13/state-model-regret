# Ghi chú thuật ngữ và lint S2

Người phụ trách Doan Van Tai. `style_lint.log` ghi 0 ERROR và 22 WARN.
Các cảnh báo đều thuộc bộ dò acronym. Báo cáo là hồ sơ thực nghiệm nội bộ,
giữ tên cột và trạng thái trong brief để đối chiếu với CSV/JSON.

| Từ bị cảnh báo | Nghĩa và lý do giữ |
|---|---|
| CTMC | Continuous-time Markov chain, chuỗi Markov thời gian liên tục của mô hình đã quét. |
| MMPP | Markov-modulated Poisson process, quá trình Poisson điều biến bởi chuỗi Markov trong estimator MMPP/M/1. |
| CI, CI95 | Confidence interval ở mức 95%, dùng Student t trên regime. Các khoảng chỉ là tham chiếu mô tả trên lưới thiết kế. |
| ID | Identifier, mã regime. Chẵn/lẻ lấy từ phần số của mã. |
| SHA | Secure Hash Algorithm, ở đây dùng SHA256 cho checksum artifact. |
| CPU | Central processing unit. CPU-s là thời gian xử lý, khác wall-s là thời gian đồng hồ. |
| CSV | Comma-separated values, định dạng các bảng được xuất. |
| PNG | Portable Network Graphics, định dạng ba hình. |
| POST, HOC | Hai từ Latin trong nhãn “post hoc”, không phải hai acronym. Nhãn này do brief yêu cầu. |
| INVALID, PASS, FAIL | Nhãn trạng thái để đối chiếu máy, giữ nguyên cách viết trong output. |
| GO, NO | Các từ trong GO/NO-GO của quyết định chuyển bước, giữ nguyên để tránh lẫn với numeric gate. |
| DRAFT | Trạng thái của thẻ S3 chưa khóa và chưa được tác giả thông qua. |
| PLAN | Tên viết tắt theo tên file PLAN_SWEEP.md mà brief dẫn. |

Không áp quy tắc bỏ ngôn ngữ audit của bản paper vào hồ sơ này vì brief yêu cầu
ghi trực tiếp PASS/FAIL, post hoc, thẻ và kết quả kiểm tra. Không có cảnh báo từ
nhóm từ cấm, cấu trúc câu, dấu câu hoặc novelty.
