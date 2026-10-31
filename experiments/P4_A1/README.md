# Phase 4 amendment A1

Người phụ trách: **Doan Van Tai**. Patch nguồn do AI (Claude) soạn, người dùng cung cấp;
phiên triển khai kiểm tra và sửa trước freeze. Không thay source/card/receipt cũ.

Ba run riêng: `L44_A1`, `L43_A1_SV`, `SUB_PROBE`. Mỗi run phải có diagnosis đã commit,
quyết định đúng provenance, prereg đã commit, control, benchmark và budget đã commit trước full.
Người dùng đã ủy quyền AI soạn quyết định/dự đoán trong chat; không ghi thành tác giả tự viết.

Các sửa bổ sung trước freeze so với patch đầu vào:

- NOT_READY do baseline cũng xuất thành UNRESOLVED, không lọt vào screening như READY.
- Giữ S11 bookkeeping; same-route và theta0 kiểm riêng khỏi cross-route quadrature.
- BUG/execution error dừng trước level kế tiếp; giữ row và CPU đã đo.
- Resume kiểm receipt, exact identity, K/ref, CF flag và dựng lại comparison từ rows.
- Summary kiểm lại cached comparison trước selection/export.
- Quyết định được AI soạn theo ủy quyền dùng status riêng và evidence trong Git.
- Diagnosis gọi đúng là equality của saved decimal strings, hash mọi input đọc.

Cap NOT_READY>0 cho phép selection trên READY subset; đây là đổi phạm vi so với DL-104,
không phải full-scope baseline đã được xác nhận. Report giữ cả N kế hoạch và N_ready.
Hai lưới có thể lệch nhau; chưa có certified total quadrature bound. G1 không đổi.

Chỉ sửa code trước freeze đầu tiên. Sau freeze, nếu cần sửa physical/runner code, tạo A2/run mới,
giữ mọi attempt A1; không sửa hash hoặc dữ liệu để tiếp tục run đã khóa.
