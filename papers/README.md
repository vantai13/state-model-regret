# Paper — đọc lesson hiện tại ở đây

Người phụ trách: **Doan Van Tai** · cập nhật **26/10/2026**.

**[Excel và tiến độ đọc](paper_comparison.xlsx)**: **P12 của L2.7 Part B** ở đầu bảng,
tiếp theo R51=P03/P07/P02 của PartA và nguồn các lesson trước. Có13công trình,
không phải yêu cầu đọc hết cùng lúc. P12/P03/P07 AI-T; **P02 full text BLOCKED**.

| Khi nào | Nguồn | Dùng để hiểu gì? |
|---|---|---|
| Hiện tại: L2.7 Part B | **P12 — Grimm et al.2020** | Value equivalence, khác OεRE theo pipeline; AI-T Definition1/§3.1 |
| Tra bổ sung Part B | R43 — Approximate Value Equivalence2022 | Lượt này abstract; old AI-T note có provenance, không thêm hàng bắt buộc |
| Cùng lesson: Part A | **R51=P03 — DT²2026** | Fidelity khác decision quality; expected regret đã có; AI-T PMLR |
| Cùng part | **P07 — DOTE2023** | Networking TE tối ưu trực tiếp; hindsight oracle biết future demands; AI-T |
| Cùng part, còn vướng truy cập | **P02 — Poelman2023** | Sensitivity theo errors/horizon/update; AI-A, §2–4/hình chưa kiểm |
| Lesson trước: L2.6 Part B | **P13 — Mathijsen/Zwart2017** | Transient/horizon; journal36trang; cần phân biệt cost trung bình/cộng dồn |
| Cùng lesson: Part A | **S11 — Li et al.2026** | Goal-oriented sampling/remote decisions; đọc arxivv3, journal TIT2026 đã kiểm |
| Lesson trước: L2.5 Part2 | **M00 — Mitzenmacher2000** | Herding do nhiều decision dùng tin cũ; bản đọc submission28trang |
| Cùng lesson: Part1 | **P04 — Shaikh/Rexford/Shin2001** | Stale link-state, routing, blocking; §V-A/Fig8 |
| Lesson trước: L2.4 | NDT1 / P05 / P10 | NDT pipeline, what-if feedback và gate |
| Tra khi cần | R32 / R34 | VoI/control và queue trễ |

[Bài L2.7 ngắn](../notes/literature/model_fidelity_methods.md) ·
[Report/commands](../results/lessons/l2_7/part_a/report.md).
PartB: [bài ngắn](../notes/literature/model_equivalence.md) ·
[P12](../notes/literature/papers/P12.md) · [R43](../notes/literature/papers/R43.md) ·
[OεRE](../notes/literature/terms.md) · [report](../results/lessons/l2_7/part_b/report.md).
Lượt PartB chỉ thêm P12 và giữ12notes/progress hiện có. Chưa chọn K5, chưa
đóng human Gate; record PartA bên dưới là lịch sử lúc lưu.
P03 và R51 là **một bài**, không thêm hàng trùng. Mười mức đọc tác giả giữ
nguyên; R51 AI note nâng từ thứ cấp lên T có snapshot trước/sau. Các notes khác
giữ nguyên. Part A còn P02 full text; PartB/P12 nay có artifact ở trên, không tự cấp Gate.

**P04 khác R04**: R04 là Secomandi2008 đã cất trong archive.
P04 có PDF journal15trang local; AI đọc targeted, tác giả chưa được tự ghi đã đọc.

[Bài L2.5 Part1 và các đính chính](../notes/literature/state_staleness.md) ·
[Note P04](../notes/literature/papers/P04.md) ·
[Part2: hai cơ chế và toy](../notes/literature/information_harm.md) ·
[M00](../notes/literature/papers/M00.md) ·
[P01 screen/skip](../notes/literature/papers/P01.md) ·
[Bản đồ NDT L2.4](../notes/literature/ndt_landscape.md).
P01 đã đọc targeted để phân biệt regret; chưa cần đọc full, không thêm hàng bắt buộc.
NMRG/P08/S07 là nguồn bổ sung trong bản đồ L2.4.
P05 full text đọc qua web; PDF local vẫn403. OpenTwin v2 vẫn ghi preprint.

[Bài L2.6/K3](../notes/literature/freshness_decision_value.md) ·
[Note S11 và DOI đúng](../notes/literature/papers/S11.md).
Kaul/AoII/AY19 là tra bổ sung trong K3; không thêm thành hàng bắt buộc.
R32 có sẵn, giữ tiến độ. [P13/Part B](../notes/literature/horizon_transient.md)
đã thực hiện kỹ thuật; [note P13](../notes/literature/papers/P13.md) ghi đúng
version/numbering. Mức AI đọc khác mức bạn đọc; không tự cấp Gate.

| Nơi | Chức năng |
|---|---|
| `paper_comparison.xlsx` | Danh_sach, Ghi_chu_doc, Huong_dan; cập nhật mức bạn đọc theo ID |
| `PDF_local/` | Mở PDF có trên máy; không push PDF lên GitHub |
| `data/` | Catalog hiện dùng và kết quả kiểm |
| [archive/](archive/README.md) | Snapshot21 bài;18 bài đã cất không trở lại hàng đợi |

SOB14/B82/P11 chỉ tra khái niệm khi cần; note/proof Part A vẫn giữ.
Ba ứng viên snowball L2.4 chỉ ở log chờ duyệt; chưa tải hoặc thêm trong L2.5.

[Quy tắc + checklist](../notes/literature/search_protocol.md).
Tái tạo: `.venv/bin/python -B tools/paper_library/build_notes.py`.
[Kiểm Excel](data/verification.json) · [Nguồn P04](../results/lessons/l2_5/source_access.json).
[Nguồn M00/P01 và provenance A4](../results/lessons/l2_5/part2/source_access.json).
