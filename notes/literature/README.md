# Literature — L2.1–L2.3, Part A

Người phụ trách: **Doan Van Tai** · 24/10/2026.

**Tìm hoặc kiểm paper mới: mở [quy tắc + checklist](search_protocol.md) trước.**
Hỏi → Tìm → Kiểm → Duyệt → Đọc → Ghi → Dừng. Áp dụng cả tra DOI và khảo sát;
ưu tiên NDT/networking, ghi kết quả thực vào [search log](search_log.md).
Các mục Part A bên dưới là artifact đã lưu, không phải yêu cầu đọc hết trước
khi tìm paper networking.
[Thư viện đang dùng](../../papers/README.md) · [18 bài lưu tạm và snapshot cũ](../../papers/archive/README.md).

Provenance: AI triển khai theo ủy quyền của tác giả. Nguồn được AI đọc không phải
L-self của tác giả. Ngày này là ngày lưu artifact và tái kiểm; không phải ngày dự
đoán mù. Contract v1.2, Main RQ, lưới, thresholds và held-out không đổi.

## L2.7 Part B — value equivalence và OεRE

[Bài ngắn/bài tập/đính chính](model_equivalence.md) · [P12](papers/P12.md) ·
[R43](papers/R43.md) · [OεRE](terms.md) ·
[L3.3/A05 queue](../lessons/L3.3_equivalence_queue.md) ·
[report](../../results/lessons/l2_7/part_b/report.md).
P12 AI-T; R43 official abstract lượt này và archived AI-T24/10 ghi tách riêng.
27checks PASS/625exact cases; chỉ kiểm membership theo tọa độ held-out.
PartB technical artifacts có, toàn L2.7 còn P02 full text/author Understanding/Gate.

## L2.7 Part A — trục model

[Bài ngắn, bài tập và đính chính](model_fidelity_methods.md) ·
[P03=R51](papers/P03.md) · [P07/DOTE](papers/P07.md) · [P02](papers/P02.md) ·
[MT1–MT8/HOLD](../phases/PHASE_4_methodology_threats.md) ·
[report](../../results/lessons/l2_7/part_a/report.md).
14checks exact PASS,2sweeps×256cases. P03/P07 AI-T; P02 AI-A, full text BLOCKED.
Part A chưa hoàn tất phần primary P02; PartB/P12/OεRE và human Gate còn mở.

## L2.6 Part B — backlog/horizon, P13

[Bài giải và crosswalk](horizon_transient.md) · [P13 journal](papers/P13.md) ·
[report/checklist](../../results/lessons/l2_6/part_b/report.md) ·
[T-H1](../01_claim_boundary_v1_2.md#t-h1--giới-hạn-diễn-giải-do-horizon-hữu-hạn-26102026).
122checks exact PASS, đọc targeted và kiểm numbering journal/arxiv. Cả2parts có
artifact kỹ thuật; tác giả L-self/Understanding/Gate và audit A4/L2.9 còn mở.

## L2.6 Part A — AoI và giá trị quyết định

[Bài ngắn + K3](freshness_decision_value.md) · [S11](papers/S11.md) ·
[heuristic queue H1, chưa khóa](h1_candidates.md) ·
[kết quả và checklist](../../results/lessons/l2_6/part_a/report.md).
Đã kiểm S11 arxivv3 và journal identity TIT2026, phân biệt age/uncertainty/value,
tính mode/variance và bài tập gap. Record PartA giữ nguyên; PartB được bổ sung
ở trên, tác giả L-self/Gate còn mở.

## L2.5 Part2 — herding khác approximate-model harm

Mở [information_harm.md](information_harm.md): V1 tính độc lập và bài tập hi={2,5},
toy4servers, đính chính cơ chế, [K-S1…8 và A4](prior_boundary.md#trục-state--l25-part2-26102026).
[M00](papers/M00.md) AI-T trên submission; [P01](papers/P01.md) targeted screen,
skip full read có lý do. [Báo cáo/kiểm](../../results/lessons/l2_5/part2/report.md).
Part1+Part2 đã có artifact kỹ thuật; tác giả Understanding/L-self/Gate chưa xác nhận.

## L2.5 Part1 — stale state trong QoS routing

Mở [state_staleness.md](state_staleness.md) và [note P04](papers/P04.md):5dòng prior,
bảng dịch sang contract, Fig8 và các điều cần sửa, toy T1…T10 và trigger counterexample.
Đã đọc primary PDF targeted; chưa là L-self hoặc formal Gate.

## L2.4 Part 2–3 — NDT/networking

Mở [ndt_landscape.md](ndt_landscape.md): pipeline, bảng biến, metric,6nguồn,
đính chính lesson, snowball thật và5câu định vị. Note chính: [NDT1](papers/NDT1.md),
[P05](papers/P05.md), [P10](papers/P10.md). Tất cả là AI-only; giữ G1, chờ L-self/Gate.

## Điểm bắt đầu

- [Báo cáo và checklist ba lesson](../../results/lessons/part_a/report.md).
- [Claims và điều kiện bác bỏ](claims.md), [dự đoán đã exposed](prior_predictions.md).
- [Ánh xạ sáu contrast](already_implied.md), [T03 v2: phép dẫn](../theory/T03_primary_reading_start.md).
- [Prior boundary](prior_boundary.md), [matrix](matrix.md), [search log](search_log.md).
- [P11](papers/P11.md), [SOB14](papers/SOB14.md), [B82](papers/B82.md),
  [MAB11](papers/MAB11.md), [E07](papers/E07.md), [SOC12](papers/SOC12.md).
- [Phân loại artifact](artifact_classification.md), [thuật ngữ](terms.md).

## Quyền sử dụng evidence

S = screen; A = abstract; T(§/trang) = targeted; F = full. T và F khác nhau.
Mỗi note ghi thêm mức `metadata-only`, `abstract-only` hoặc
`AI đọc full text (§…/trang …)`; cách ghi cuối chỉ phạm vi full-text đã tiếp cận,
không tự nâng targeted reading thành full reading. Tất cả note hiện là **AI-only**;
L-self chỉ đổi khi có record tác giả mở nguồn và kiểm thật.

Fact, Claim, Evidence, Inference được tách trong từng note. Mọi inference về
contract là suy luận của dự án, không gán cho paper. Nhãn prior boundary là
**AI đề xuất**, chưa phải quyết định cuối Gate L. Không xác nhận novelty/G2.

PDF và text trích xuất nằm ngoài repo tại `~/papers/l2_part_a/`; checksum và trạng
thái tải được ghi trong `results/lessons/part_a/source_access.json`.

## Luật dừng đã lưu

Mỗi nguồn: dừng khi trả lời được câu hỏi hoặc khoảng 90 phút không tiến triển;
ghi Unclear nếu thiếu nội dung. Mỗi vùng blind-spot: hai query liên tiếp, mỗi
query screen 20 kết quả đầu mà không có candidate mới. Đây là quy tắc quy trình,
không chứng minh coverage. Lượt này là lookup nguồn có tên, không phải bốn phiên
blind-spot L2.8; không ghi đã đạt điều kiện đó.

## Deviation và điều kiện còn mở

1. Nội dung L2.1–L2.3 đã xuất hiện trong chat trước khi tạo thư mục này. Không thể
   phục hồi commit dự đoán trước exposure; giữ nguyên lịch sử, ghi deviation.
2. Dự đoán do AI hỗ trợ theo yêu cầu tác giả; không đo calibration cá nhân/mù.
3. Tác giả tự dẫn kín sách, L-self, đọc lại sau một ngày và người đọc độc lập chưa
   có record. Không tạo bằng chứng thay người thật.
4. Technical completion và formal Gate là hai trường riêng trong báo cáo.
   Không commit L3.3 prediction card hoặc chạy Phase 3 trong tác vụ này.
