# Hướng dẫn làm việc trong repo

Người phụ trách mặc định: **Doan Van Tai**. Báo cáo bằng tiếng Việt; giữ nguyên
attribution đã tồn tại. Không thay RQ, contract, giả định hoặc tiêu chí thí nghiệm
chỉ vì một nguồn literature hay hướng dẫn của AI đề xuất.

## Mỗi lần tìm, lấy, đọc, kiểm tra hoặc trích paper

1. Đọc [quy tắc và checklist](notes/literature/search_protocol.md) trước khi
   thao tác; áp dụng cả khi chỉ tra một bài đã biết tên/DOI.
2. Kiểm thư viện và log hiện có trước; ưu tiên NDT/networking. Viết câu hỏi,
   PC liên quan và lý do nguồn có thể ảnh hưởng claim. Không mở rộng ngoài ngành
   chỉ vì trùng thuật ngữ.
3. Phân biệt `lookup`, `keyword`, `backward`, `forward`, `author/venue` trong
   [search log](notes/literature/search_log.md). Chỉ ghi thao tác và số đếm thật;
   lookup không phải bằng chứng đã khảo sát lĩnh vực.
4. Mỗi đợt AI đề xuất tối đa 3 nguồn mới, có lý do giữ và PC liên quan. Chờ tác giả
   duyệt trước khi tải PDF hoặc tạo note nội dung mới. Yêu cầu trực tiếp tải/đọc
   một nguồn cụ thể đã là ủy quyền; không hỏi lại. Tra metadata, sàng ứng viên và
   ghi log được làm trước bước duyệt.
5. Kiểm DOI/arXiv/URL ở nguồn chính thức, phiên bản và trạng thái xuất bản.
   PDF lưu ngoài Git tại `~/papers/state-model-regret/`; không dùng thư viện lậu,
   không tự gửi email xin bài.
6. Ghi riêng mức đọc AI và tác giả; trích đúng §/trang/phương trình cho claim
   nội dung. Thiếu bằng chứng thì ghi chưa xác nhận. Không tự kết luận novelty
   hoặc đổi nhãn PC/Gate từ một kết quả tìm kiếm.
7. Cuối phiên ghi query, công cụ, bộ lọc, số thực sàng, số giữ không trùng, lý do,
   lỗi/hạn chế và lý do dừng; báo trực tiếp kết quả cùng đường dẫn đã lưu.

Nhắc nhanh: **Hỏi → Tìm → Kiểm → Duyệt → Đọc → Ghi → Dừng**.

## Thư viện sau dọn ngày 24/10/2026

Bảng hiện dùng: `papers/paper_comparison.xlsx`; dữ liệu: `papers/data/catalog.json`.
`papers/archive/` là snapshot lịch sử; không tự đưa 21 bài hoặc 4 nhóm đọc cũ
trở lại danh sách bắt buộc. Lưu tạm không đồng nghĩa nguồn đã bị bác bỏ.
Note/proof Part A và kết quả thí nghiệm vẫn là evidence, phải giữ nguyên.

Cập nhật25/10/2026: NDT1/P05/P10 được tác giả yêu cầu trong L2.4 và nằm đầu
catalog; R32/R34/R51 là tham khảo cũ. NMRG/P08/S07 ở landscape để tra bổ sung.
Ba đề xuất snowball chưa duyệt chỉ ở log, không tự tải hoặc thêm vào danh sách.

Cập nhật26/10/2026: P04 (Shaikh/Rexford/Shin2001, khác R04) là nguồn chính
L2.5 Part1, ở đầu Excel. M00/P01 và L2.5 Part2 chưa thực hiện.
Các toy L2.5 là connection-admission minh họa, không phải replication P04
hoặc kết quả lưới/expected regret của contract.
