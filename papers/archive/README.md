# Lưu tạm — không phải danh sách cần học

Người phụ trách: **Doan Van Tai** · **24/10/2026**.

Quay lại [bảng chính 3 bài](../paper_comparison.xlsx).

**18 bài được cất khỏi bảng chính**, không bị kết luận là sai hoặc không có ích:

| Cách dùng | Mã |
|---|---|
| Chỉ tra tên EVPPI/VSS/EVMI khi cần | SOB14, B82, P11 |
| Cất lại; mở khi có câu hỏi/claim cụ thể cần | MAB11, E07, SOC12, R01, R04, R02, R43, R06, R25, R29, R12, R10, R03, R07, R18 |

## Những gì được giữ nguyên

- [Excel cũ 21 bài](paper_comparison_part_a.xlsx): nguyên file, đủ mức đọc và ghi chú; gồm cả 3 bài còn dùng để giữ snapshot đầy đủ.
- `data/`: catalog, note và kết quả kiểm **trước dọn**; PASS trong đó thuộc trạng thái cũ.
- `groups/`: 4 phân nhóm **đã ngừng dùng**, chỉ giữ lịch sử; thứ tự đọc cũ không còn là yêu cầu.
- `part_a_quick_view.csv`: bảng 6 nguồn Part A gốc, đã ngừng dùng làm bảng chính.
- `PDF_local/`: lối mở local đến kho cũ; PDF không đưa vào Git.
- [Manifest di chuyển](cleanup_manifest.json): tên cũ/mới và checksum để tra hoặc khôi phục.

## PDF, audit và sao lưu cục bộ

Kho cũ ở `~/papers/state-model-regret/archive/2026-10-24/`:

- `Part_A/`, `review_2026-10-24/`, `inbox/`: PDF gốc và text đã trích.
- `failed_downloads/`: 5 phản hồi tải lỗi/rỗng, đổi đuôi thành `.response` để không nhầm là PDF.
- `review_notes/`: lượt audit 59 nguồn trước đây ở `notes/literature/review_runs/`; giữ nguyên 16 file, không đưa các file vốn chưa tracked lên Git.
- `_backups/`: bản sao lưu cũ; 4 thư mục nhóm đọc cũ cũng được giữ trong kho này.

Sao lưu trước dọn: `~/papers/state-model-regret-cleanup-backup-2026-10-24/`.
Tra đường chuyển bằng manifest trước khi khôi phục. Không chép đè mức đọc hoặc ghi chú mới.

Việc dọn không đổi RQ, contract, claims, kết quả hay Gate. Không suy “không có prior”
từ việc một nguồn đã được lưu tạm.
