# Phase 3R Closeout (BẢN NHÁP)

> ⟨ngày⟩ · Người phụ trách: **Doan Van Tai** · Contract v1.3 · Tag `phase-3R-closeout` (chưa tạo)
>
> Provenance:
> - **Hai mục đầu: tác giả tự viết, để trống.** AI không soạn; nếu AI soạn thì phải ghi "AI soạn" và không tính là tự viết.
> - Các mục còn lại: **AI (Claude) soạn từ bằng chứng trong repo, chờ tác giả duyệt** (lesson L3R.8, Bước 7).
> - Nhãn gate và trạng thái điều kiện quy trình do tác giả điền.

## What I understood
⟨Tác giả tự viết: 5–10 câu, không nhìn tài liệu. Không ủy quyền được.⟩

## What changed in my mental model
⟨Tác giả tự viết: trước Phase 3R tôi nghĩ… ; bây giờ tôi nghĩ… ; vì evidence…⟩

## Decisions made

| DL | Quyết định | Evidence |
|---|---|---|
| DL-064 | Mở Phase 3R; pilot population v1.3 là discovery | Tag `explore-v13-pilot` |
| DL-065 | T07 và golden reference trước audit | [T07](../theory/T07_population_estimand.md) |
| DL-066–068 | Audit engine population: HOLD có giới hạn; giữ lõi, thêm lớp test/API | [L3R.3 report](../../results/lessons/l3r_3/report.md) |
| DL-069–070 | Realism v1: nguồn/luật khóa trước bảng; MV/SH HOLD_UNSOURCED | [L3R.4 report](../../results/lessons/l3r_4/report.md) |
| DL-071–072 | Contract v1.3 khóa có mục DEFERRED; tag | `contract-v1.3` → `3d2359b` |
| DL-073–074 | Cards v1: hai primary (MV, SH), đối chứng lật κ; đóng băng | Card v1 `1414d92` |
| DL-075–077 | Chuẩn bị confirmation; tác giả duyệt luật n, ngân sách 48 CPU-giờ | [design](../design/confirmation_v1_3.md) |
| DL-078–094 | Numerics card v1 (lưới 1/1000): calibration, GCP, native evaluator; HOLD rồi tạm dừng theo tác giả | [pause report](../../results/lessons/l3r_7/pause_report_20261030.md) |
| DL-095–096 | Đóng L3R.7 gọn: card v2 (bước tốc độ 1/100), numerics (640, 4), n = 60/BND = 15, 270 CF chỉ tham số | [report](../../results/lessons/l3r_7/lean_close/report.md) |
| DL-097–101 | ⟨nháp: D22 → Phase 5; realism mức mô hình; P0-V10; L8 → Phase 8; nhãn Gate 3R⟩ | [nháp](../../results/lessons/l3r_8/decisions_DRAFT.md) |

## Evidence created

- **Verification engine population** (tầng E1, trong mô hình đã khai báo):
  - L3R.3: test, mutant, tái lập, MC độc lập trên engine pilot;
  - L3R.7: engine native đạt R1 trên 118 ca calibration ở (640, 4);
  - zero-action và identical-model ra 0 chính xác.
- **Realism screen** ở mức thiết kế và nguồn: toàn bộ UNSOURCED.
- **Hai prediction đóng băng** có hash trước dữ liệu CF; 270 regime CF chỉ có tham số.
- **Không có evidence khoa học mới nào về các hypothesis.** Pilot và regime map là discovery.

## Assumptions still open

- AS1–AS14.
- Cờ realism: buffer vô hạn, action tức thời, quyền oracle về mode (S1).
- S0 là posterior Bayes chính xác.
- c_sw = 0.
- Quá trình trước quyết định ở trạng thái dừng (pre-Stay stationary).
- D13 không tính chi phí sau h.
- Biên độ nền a/μ = 0,6 cố định.
- Card v2 chỉ phủ tốc độ trên lưới 1/100.

## Risks still open

| Risk | Lộ ra ở |
|---|---|
| ER3: chuỗi review → pilot → card → numerics → CF phần lớn do AI soạn/chạy, lỗi có thể đi cùng hướng | Người đọc thật (P0-V10), Phase 4 |
| Ω⁻ đã lộ một phần trước khi rút (MV-ii 24 khóa, SH-ii 45 khóa) | Báo cáo Phase 4 |
| Effect gần ngưỡng → UNRESOLVED nhiều → R5 INCONCLUSIVE | Phase 4 |
| p⁺ thật chỉ khoảng 0,6 → P(PASS) khoảng 0,26 → WEAKEN | Phase 4 |
| Chưa có MC độc lập trên engine native ở (640, 4) | Phase 4 (control, anchor), Phase 6 |
| Realism UNSOURCED: kết quả có thể không gặp ở mạng thật | Phase 6/7 |
| D22 chưa có: không tách được backlog với mode trong harm | Phase 5 |

## What I am allowed to claim

- Engine population tính estimand v1.3 đúng trong phạm vi các kiểm đã làm, kèm giới hạn: chênh lệch làm mịn là chẩn
  đoán, không phải cận được chứng nhận.
- Pilot và regime map cho tín hiệu **discovery** ở các vùng đã mô tả; realism ở mọi bối cảnh đã chọn: UNSOURCED.
- Các prediction Hyp-MV và Hyp-SH đã được đóng băng trước dữ liệu CF: card v1 `1414d92`; card v2 sha `60335b61…`.

## What I am NOT allowed to claim

- bất kỳ hypothesis nào đúng;
- tần suất trong mạng thật;
- "fresh telemetry có hại";
- complementarity như phát hiện riêng;
- robustness với switching cost;
- novelty;
- G2;
- khuyến nghị vận hành;
- "Ω⁻ là ngoại suy hoàn toàn chưa thấy";
- "tác giả dự đoán" cho phần do AI soạn.

## Gate decision

Ba bảng và hash: xem [gate note (nháp)](PHASE_3R_gate_note_DRAFT.md).

**Nhãn:** ⟨tác giả chọn⟩ · **Claim gắn với nhãn:** ⟨…⟩ · **Trạng thái P0-V10:** ⟨…⟩

## Next phase

Phase 4 (confirmation v1.3, chạy đúng một lần) bắt đầu bằng Bước 0, nối runner. Runner kiểm trước trên 4 góc dry-run B,
kết quả phải trùng chính xác; commit runner và hash trước lần gọi CF đầu tiên.

Điều kiện: nhãn Gate 3R có trong DL; quyết định D22 và người đọc theo DL-097/DL-099; kiểm hash lúc bắt đầu;
control và anchor chạy trước.
