# Paper — mở bảng này trước

Người phụ trách: **Doan Van Tai** · dọn ngày **24/10/2026**.

**[Excel đang dùng](paper_comparison.xlsx)** chỉ giữ 3 nguồn gần đề tài từ thư viện cũ.
Đây là bảng tham khảo, không phải danh sách đầy đủ về NDT hay bài tập phải đọc hết.

| Mã | Vì sao giữ trong bảng chính? | Trạng thái hiện có |
|---|---|---|
| R32 | VoI trong feedback control: gần trục thông tin state | Có PDF; AI đã đọc một số mục |
| R34 | Điều khiển queue khi thông tin chiều dài queue bị trễ | Metadata; chưa có PDF |
| R51 = P03 | DT²: cầu nối giữa model và chất lượng quyết định | Qua nguồn thứ cấp; chưa có PDF; **DT chung, không chuyên networking** |

Excel có 3 tab: `Danh_sach`, `Ghi_chu_doc`, `Huong_dan`. Cập nhật mức bạn đọc
ở `Danh_sach`; mức AI đọc và ghi chú nằm riêng. Ghi chú cũ giữ nguyên provenance.

## Thư mục còn lại dùng làm gì?

| Nơi | Dùng khi nào? |
|---|---|
| `PDF_local/` | Mở PDF thuộc bảng đang dùng; hiện chỉ có R32 |
| `data/` | Catalog 3 bài và kết quả kiểm Excel; không cần mở khi học |
| [archive/](archive/README.md) | Tra lại thư viện 21 bài, ghi chú và phân nhóm cũ |

**18 bài đã bỏ khỏi bảng chính và lưu tạm.** SOB14, B82, P11 chỉ tra tên khái niệm
khi cần; các bài health economics, revenue management, weather, vehicle routing,
sách và lý thuyết bổ sung được cất lại. Lưu tạm không có nghĩa là đã bác bỏ nguồn
hay đã giải quyết rủi ro prior. Các note/proof Part A vẫn ở `notes/literature/`.

Trước khi tìm/thêm bài: [quy tắc + checklist](../notes/literature/search_protocol.md).
Không thêm hoặc tải paper mới trong lượt dọn này.

Tái tạo Excel: `.venv/bin/python tools/paper_library/build_notes.py`.
Builder giữ mức đọc và ghi chú theo ID; không tự tái tạo 4 nhóm cũ hay tải PDF.
[Kiểm Excel](data/verification.json) · [Lịch sử di chuyển](archive/cleanup_manifest.json).
