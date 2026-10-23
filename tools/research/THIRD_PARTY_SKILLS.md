# Nguồn gốc các skill bên thứ ba trong `.claude/skills/`

```
PROVENANCE
- Source repo: https://github.com/K-Dense-AI/claude-scientific-skills
- Commit: 593377bb048752abb0152deab9fbb1083a6087df (lấy ngày 23/10/2026, git clone --depth 1)
- License: MIT (Copyright (c) 2025 K-Dense Inc.) — bản LICENSE.md được chép vào từng thư mục skill
- Skills đã chép nguyên thư mục: paper-lookup, citation-management, scientific-critical-thinking,
  peer-review, scientific-writing, statistical-power, experimental-design, simpy
- Sửa đổi: (1) xoá __pycache__; (2) scientific-writing/SKILL.md thêm
  `disable-model-invocation: true` để Claude chỉ chạy skill viết khi tác giả gọi /scientific-writing.
  Không sửa nội dung nào khác.
- Kiểm trước khi chép: script chỉ gọi API học thuật (OpenAlex, Crossref, arXiv, doi.org, NCBI, DataCite);
  không thấy lệnh xoá file, đọc khoá bí mật hay gửi dữ liệu ra ngoài.
- Vì sao chọn 8 skill này trong 177: chúng phục vụ trực tiếp Phase 2 (tìm, ghi, kiểm citation),
  Phase 3–4 (thiết kế factorial, power bằng mô phỏng), Phase 7 (DES độc lập) và phản biện/viết.
  Các skill sinh học, hoá học, y khoa không liên quan RQ nên không chép.
```

Cập nhật: clone lại repo nguồn, chép đè đúng các thư mục trên, ghi commit mới vào file này, chạy
`python tools/research/check_mcp.py` và `python -m pytest -q`.

Skill do repo này tự viết (không phải bên thứ ba): `paper-note`, `search-log`.
