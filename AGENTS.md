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

Cập nhật26/10/2026: L2.5 Part1/Part2 đã hoàn tất kỹ thuật, P04 khác R04;
toy admission/bốn server/V1 không phải replication paper hoặc lưới v1.2.
L2.6 Part A có S11 ở đầu Excel, journal identity TIT2026 đã kiểm nhưng bản đọc
là arxivv3. K3/heuristic H1 chỉ là AI-assisted evidence/queue, không khóa H1.
L2.6 Part B/P13 nay có artifact kỹ thuật, journal CWI36trang; Eq2.7 định nghĩa
ΩT, Prop4–5/tr282 và terminal discussion §6/tr289 khác arxivv1 numbering.
T-H1: D13 đã chứa dt·qH, chỉ không có terminal surcharge/cost sau h; không đổi
metric. H1-Q02 và Q-L27-01 chỉ là queue, tác giả L-self/Gate/A4/L2.9 còn mở;
không tự đổi nhãn PC, khóa H1 hoặc chạy Phase3.

Cập nhật L2.7 PartA,26/10/2026: P03=R51 dùng chung một record, P03/P07 AI-T;
P02 mới official abstract AI-A, full text timeout/403/OA fallback thất bại.
Không ghi P02 đã T hoặc L2.7 PartA hoàn tất toàn bộ. Excel12nguồn;10tiến độ
tác giả và9notes khác giữ nguyên, R51 AI note nâng mức có snapshot. K-M1…5/
MT1…8 chỉ evidence/queue; K-M5 và MT2/6/7 còn primary P02 dependency. Không gán
dấu Γ cho P02/P04 hoặc nhận factorial/decision regret là mới. MT5 chờ A05,
PartB/P12/OεRE/L-self/Gate/A4/L2.8–2.9 còn mở; không tự chọn null hoặc chạy Phase3.

Cập nhật L2.7 PartB,26/10/2026: P12 primary NeurIPS AI-T; R43 lượt này AI-A,
archived AI-T24/10 có provenance riêng. OεRE đã có trong terms dưới dạng draft,
không contract-adopted; numeric/CI label helpers chỉ teaching/reporting proposal.
K5/S0 forecast giữ nguyên; rule κ≥2/q90/q90/h8 chỉ candidate L3.3, chưa chọn;
held-out chỉ đọc tọa độ/design labels, không outcomes/p_sw/λA. Excel13nguồn,
chỉ thêm P12, giữ12notes/progress cũ. PartB technical PASS không đóng toàn L2.7:
P02 PartA vẫn full-text BLOCKED, L-self/Understanding/Gate/A4/A05/L2.8–2.9 còn mở.
