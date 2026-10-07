# Decision log

Entries ghi đúng thời điểm thực hiện; không biến đề xuất của AI thành quyết định của GVHD.

### DL-000 — Genesis (2026-10-07)
- Decision: thực hiện yêu cầu đóng băng snapshot switch-or-stay tại `archive-switch-or-stay-2026-10-02` / `e669f5c8053a81d6de192de9f9d0d6304ee67802`; giữ riêng local tip `archive-switch-or-stay-2026-10-02-wip-local-2026-10-07` / `2e7543b2794a85645d60c0a55afb5a670166a099`; tạo notes-only repo local cho Phase 0. Nguồn RQ: Final Review bản cập nhật 06/10/2026, SHA-256 `fc766e319427ba01da7362de2018cd4da6695dc1fcaa9812ed7badd5c0651fd1`.
- Why: trích dẫn cần trỏ vào nội dung cố định và công việc local phải được ghi danh; chọn e669f5c vì fresh clone xác nhận nó chứa cả 10 nhánh remote ban đầu. main dừng ở 7c60c76630de0e4bd6459b00d201fa2e744a46fe và không giữ các commit rollout mới hơn.
- Alternatives: tag main không bao phủ snapshot mới nhất; dùng branch rollout-v6 làm trích dẫn sẽ trôi; không tag thiếu neo trích dẫn. Dùng tiếp thư mục cũ cho deliverable notes không khớp yêu cầu tách notes của Part 2; biện minh thay đổi estimand dành cho L0.5.
- Consequence: cite `tag:path`; không di chuyển tag, không merge để gom archive; không sửa code/tài liệu cũ; bảo tồn khác xác nhận. Các stash/raw/sandbox ngoài tag được kê tại legacy/INDEX.md.
- Revisit when: GVHD yêu cầu bổ sung cho NCKH hoặc phát hiện sai nguồn → tạo nhánh từ tag và entry đính chính; không sửa tag cũ.
- Ai quyết: tác giả đã yêu cầu thực hiện trong chat; Codex thực thi và soạn notes; GVHD chưa xác nhận hướng mới, tác giả chưa xác nhận mọi diễn giải.
- Tồn đọng tại genesis: tạo remote private bị HTTP 403, chưa có remote notes để push; heads-up chưa gửi vì thiếu kênh/người nhận/chữ ký. Cập nhật bằng entry mới khi xử lý được.
