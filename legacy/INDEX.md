# Legacy index — kiểm ngày 07/10/2026

| Repo | Tag | Commit đầy đủ | Ghi chú |
|---|---|---|---|
| dt4n-decision-risk-project | [`archive-switch-or-stay-2026-10-02`](https://github.com/vantai13/dt4n-decision-risk-project/tree/e669f5c8053a81d6de192de9f9d0d6304ee67802) | `e669f5c8053a81d6de192de9f9d0d6304ee67802` | Annotated, push/peeled hash đạt; 10 nhánh remote ban đầu là ancestors. |
| dt4n-decision-risk-project | [`archive-switch-or-stay-2026-10-02-wip-local-2026-10-07`](https://github.com/vantai13/dt4n-decision-risk-project/tree/2e7543b2794a85645d60c0a55afb5a670166a099) | `2e7543b2794a85645d60c0a55afb5a670166a099` | Giữ riêng 3 local commits N0–N2 ngày 02/10, nhánh wip-local-2026-10-07. |
| dt4n | [`archive-2026-09`](https://github.com/vantai13/dt4n/tree/d45cf4ff26d8c6204a181f0fa77887e087a4d381) | `d45cf4ff26d8c6204a181f0fa77887e087a4d381` | Remote hash đã kiểm; MAP.md mở được, tag không có README.md. |

Bốn tag cũ phase-0-complete, phase-0v2-complete, pre-pivot-v14, prereg-f7 đều IN archive chính. Tổng 11 nhánh được giữ bởi tag chính/tag phụ; không merge và không di chuyển tag.
Seeds đã xem: [registry immutable](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/seed_registry.md) và [sổ exposure bổ sung](../notes/00_exposure_register.md).

## Bằng chứng mở công khai

- [Inventory/source links](../notes/00_evidence_inventory.md), [source digests](../notes/verification/source_checks.json).
- [Script tái kiểm](../notes/verification/verify_archive.py), [JSON số liệu](../notes/verification/verification_results.json), [cách chạy](../notes/verification/README.md).
- [Bundle manifest](../notes/verification/bundle_manifest.json): metadata rút gọn từ manifest thật, không phải nội dung bundle.
- [Raw AoI manifest](../notes/verification/raw_backup_manifest.json): 30 aoi_*.jsonl, 71.674.153 byte không nén; cả tar có 1.141 file, 444.748.020 byte không nén, 58.057.695 byte nén. Không đồng nhất raw AoI với toàn tar hay bộ “427 MiB” chưa xác định.
- [Final Review reading note](../notes/verification/final_review_reading_note.md): tóm tắt sections đã đối chiếu; full snapshot có SHA-256 `fc766e319427ba01da7362de2018cd4da6695dc1fcaa9812ed7badd5c0651fd1`, chưa công khai và chưa có byline rõ. Không phải bản gốc thay thế.

## Ngoài archive / nguồn chưa công khai

- dt4n có 4 local commits chưa nằm trên remote tại inventory đầu, tip d387f4df694a95719ce5287b99a1246c0060de94 và 2 stash; giữ bằng bundle local, không tuyên bố đã push.
- dt4n-core có remote riêng và bundle riêng, không thuộc hai tag switch-or-stay. Lỗi fetch SSH đã được kiểm lại qua HTTPS; không có local branch commits ngoài remote sau fetch.
- Ba bundles dt4n.bundle, dt4n-core.bundle, ndt-decision-risk.bundle đã verify và có bản sao thứ hai trên filesystem Windows cùng máy, SHA-256 trùng manifest. Chưa phải independent off-site backup; không upload bundle lên repo public.
- Inventory đầu ghi 16.380 ignored files trong working tree cũ, gồm venv/cache/raw results. Danh sách chi tiết vẫn local-only; tags không giữ ignored files. Không dùng con trỏ local làm bằng chứng có thể mở cho người đọc GitHub.
- Raw backup dt4n-raw-phase23-aoi-20260827.tar.gz và backup lớn dt4n-FULL-BACKUP-20260828.tar.gz vẫn local-only; backup lớn chưa audit nội dung ở L0.1. Metadata raw không thay remeasurement AoI.
- Sandbox/Colab/máy khác chưa kiểm được; không khẳng định lưu đủ mọi công việc hoặc mọi dữ liệu đã nhìn.
- PHASE_0/master plan v1.1 đầy đủ và bảng EV numbering gốc chưa có để đối chiếu. Primary literature chưa tự kiểm lại; giới hạn được giữ ở inventory.
- Không chép nguyên văn private feedback/biên bản GVHD vào repo public khi chưa có permission. Việc hỏi quyền chia sẻ tài liệu sẽ đưa vào memo; chưa có record đã hỏi/được đồng ý.

Bảng phân loại Keep/Reference/Archive: làm ở L0.5
