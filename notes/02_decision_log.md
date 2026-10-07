# Decision log

Quyết định ghi theo thời điểm; phê duyệt của tác giả khác phê duyệt của GVHD.

### DL-000 — Genesis (2026-10-07)
- Decision: đóng băng switch-or-stay tại `archive-switch-or-stay-2026-10-02` / `e669f5c8053a81d6de192de9f9d0d6304ee67802`, giữ local WIP bằng `archive-switch-or-stay-2026-10-02-wip-local-2026-10-07` / `2e7543b2794a85645d60c0a55afb5a670166a099`, mở workspace riêng cho State×Model Main RQ. Nguồn RQ: Final Review cập nhật 06/10 và tiền thân N0/N1/N2 ngày 02/10; xem inventory EV-05/13/14.
- Why: historical snapshot cố định tránh citation drift; ghi seed/workload/config đã nhìn để confirmation tương lai thật sự held-out. Chọn e669f5c vì nó giữ cả 10 nhánh remote ban đầu; main cũ dừng ở `7c60c76630de0e4bd6459b00d201fa2e744a46fe`.
- Alternatives: tag main không giữ toàn rollout work; merge mọi nhánh tạo project state chưa từng ở đó; tiếp tục phát triển RQ mới ngay repo cũ khó tách assumptions/objective/scope đang đổi; không archive làm trôi trích dẫn và mất exposure history. Biện minh estimand chi tiết dành L0.5.
- Consequence: historical citation dùng immutable tag:path; không phát triển old project như Main RQ hiện tại; giữ scope result cũ; ghi exposed seed/config; artifact mới vào workspace mới.
- Revisit when: GVHD yêu cầu bổ sung NCKH từ old project → branch từ đúng archive tag và decision entry; không sửa/di chuyển tag.
- Tác giả quyết định; GVHD chưa xác nhận Main RQ. Tại genesis remote tạo tự động gặp HTTP 403 và heads-up chưa gửi; các thay đổi sau ghi entry riêng.

### DL-001 — Publish notes sau xác nhận public (2026-10-07)
- Decision: tác giả xác nhận trực tiếp “Tôi xác nhận push lên repo public”; dùng `https://github.com/vantai13/state-model-regret` public thay mặc định private.
- Why: tác giả đã tạo remote; API chuyển private trả HTTP 403, sau đó tác giả chọn giữ public.
- Consequence: main và `l0.1-genesis-2026-10-07` đã push, clone từ GitHub kiểm đủ nội dung; tag genesis giữ commit `e0e563375b143da5d6ce472d9e82c28a3ebc752b`.
- Tác giả quyết định việc publish; không phải GVHD duyệt RQ hoặc nghiên cứu. Heads-up vẫn chưa gửi.

### DL-002 — Tích hợp nội dung tác giả xác nhận và sửa nguồn (2026-10-07)
- Decision: khôi phục A1 nguyên văn; tích hợp understanding/judgment tác giả cung cấp, B6 và nhãn history; lập inventory EV-01…EV-19, exposure, G-level, claim boundary v0 và closeout; bỏ các tên công cụ theo yêu cầu biên tập của tác giả.
- Why: tách đối chiếu nguồn khỏi hiểu bài, giữ scope old-world, sửa source discrepancies và làm bằng chứng nhỏ có thể mở từ repo public.
- Consequence: G1 giữ nguyên; không nâng lên G2; full study HOLD. Understanding tích hợp theo xác nhận tác giả, không giả có vấn đáp/read-back độc lập. Chỉ nội dung hiện hành được sửa; archive và genesis tags không bị di chuyển.
- Verification: script archive portable chạy từ clone mới; hashes/CI/source metadata được commit dưới notes/verification. Ba bundle có bản sao thứ hai trùng SHA-256 trên filesystem khác cùng máy; chưa phải off-site backup.
- Public scope: chỉ summary/metadata; không chép nguyên văn private feedback, email/address/token hay transcript nhạy cảm. Full raw/review/bundles local-only có limitation rõ.
- Status: SCIENTIFIC/UNDERSTANDING PASS — PRACTICAL PENDING theo rubric tích hợp tác giả yêu cầu; heads-up chưa gửi. Không bắt đầu L0.2.
- Tác giả xác nhận nội dung trong prompt; chưa có source mới xác nhận GVHD approve hướng này.
