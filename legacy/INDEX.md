# Legacy index — kiểm ngày 07/10/2026 (Asia/Saigon)

| Repo | Tag | Commit đầy đủ | Ngày tạo tag / kiểm | Ghi chú |
|---|---|---|---|---|
| https://github.com/vantai13/dt4n-decision-risk-project | `archive-switch-or-stay-2026-10-02` | `e669f5c8053a81d6de192de9f9d0d6304ee67802` | 07/10/2026 | Trạng thái 02/10; 10 nhánh remote ban đầu đều là tổ tiên; tag annotated đã push và kiểm peeled hash. |
| https://github.com/vantai13/dt4n-decision-risk-project | `archive-switch-or-stay-2026-10-02-wip-local-2026-10-07` | `2e7543b2794a85645d60c0a55afb5a670166a099` | 07/10/2026 | Giữ riêng 3 commit local L1.1–L1.3; nhánh `wip-local-2026-10-07`; không merge vào archive chính. |
| https://github.com/vantai13/dt4n | `archive-2026-09` | `d45cf4ff26d8c6204a181f0fa77887e087a4d381` | kiểm 07/10/2026 | Tag cũ đã có remote; kiểm hash peeled bằng ls-remote và file `MAP.md` bằng cat-file. Tag không có README.md. |

Các tag cũ `phase-0-complete`, `phase-0v2-complete`, `pre-pivot-v14`, `prereg-f7` đều IN trong archive chính, không có OUTSIDE trong 4 tag ban đầu.
Tham chiếu seeds đã xem: `archive-switch-or-stay-2026-10-02:notes/seed_registry.md`; không dùng danh sách “chưa dùng” cũ hơn trong F6 để mặc nhiên xác nhận held-out.

## Ngoài archive

- `/home/vantai/dt4n`: 4 commit chưa nằm trên remote tại lần kiểm đầu, gồm tip `d387f4df694a95719ce5287b99a1246c0060de94`; 2 stash. Đã giữ bằng Git bundle local, không tuyên bố đã push chúng.
- Git bundles đã verify: `/home/vantai/archive-audit-2026-10-07/dt4n.bundle`, `dt4n-core.bundle`, `ndt-decision-risk.bundle`; hash/size ở `bundle_manifest.json`. Chỉ giữ objects/refs, không giữ ignored files.
- Repo `dt4n-core` có remote riêng, không thuộc hai tag switch-or-stay. Fetch SSH ban đầu lỗi; fetch HTTPS sau đó đạt; không có local branch commit ngoài remote sau fetch. Không thay cấu hình SSH của tác giả.
- 16380 ignored files trong working tree ndt-decision-risk tại lúc kiểm, gồm cache/venv và raw kết quả. Danh sách đầy đủ: `/home/vantai/archive-audit-2026-10-07/ignored_paths.txt`; không giả định ignored files được tag giữ.
- Có backup local `/home/vantai/dt4n-raw-phase23-aoi-20260827.tar.gz`: 58057695 byte nén, 1141 file, 30 file aoi_*.jsonl (71674153 byte không nén). Chưa chứng minh đây chính là bộ raw khoảng 427 MiB được plan nhắc; chưa đo lại AoI 0,36 s.
- Backup lớn `/home/vantai/dt4n-FULL-BACKUP-20260828.tar.gz` có trên đĩa; chưa kiểm nội dung/checksum ở Part 2 này.
- Sandbox AI/Colab/máy khác không truy cập được trong phiên này: không khẳng định đã thu đủ, không khẳng định không còn dữ liệu.
- Final Review có snapshot local `/home/vantai/archive-audit-2026-10-07/Final_Review_source_snapshot.md`, SHA-256 `fc766e319427ba01da7362de2018cd4da6695dc1fcaa9812ed7badd5c0651fd1`; thiếu byline, chưa xác nhận người viết. PHASE_0 và master plan v1.1 đầy đủ chưa được cung cấp/tìm thấy theo đúng tên, không giả làm đã đối chiếu chúng.

Bảng phân loại Keep/Reference/Archive: làm ở L0.5
