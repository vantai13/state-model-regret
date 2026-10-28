# L3R.1 — Timeline và phân loại phát biểu

Người phụ trách: **Doan Van Tai** · 28/10/2026 · DL-064.
Bản tổng hợp theo ủy quyền từ hồ sơ đã mở, không phải bài kín sách hoặc xác nhận
tác giả tự nhớ/đọc hết raw. Người phụ trách không thay attribution nguồn có sẵn.

## Timeline 10 dòng tái dựng từ repo

1. Engine/card Phase3 được kiểm và khóa theo DL-045–049 trước outcomes lưới.
2. A01 chọn dt cuối1/240s, giữ các run FAIL/partial (DL-050–053).
3. A04 chấm card trước discovery; P5 đứng danh sách, P2/P3/P6 không đứng (DL-055–056).
4. A05-F khóa H0/H1/metric/margin/split/θ/predictions đúng thứ tự (DL-057–058).
5. A05-T mở10ôR: PC4 WEAKEN/FALSIFY, K5 bác R04, C1 đứng4ô (DL-059–060).
6. Tác giả chọn Gate A REFORMULATE; hồ sơ closeout soạn theo ủy quyền (DL-061).
7. Step1 khai trước81b1c3f, outcome66f167d: P(a)PASS, P(b)/P(c)FAIL → fallback (DL-062–063).
8. Population pilot Stage1 tính60ID trên branch exploration, không thành confirmation.
9. Stage2 thêm108ID thích nghi, Stage3 thêm48ID với c_sw;216ID chỉ210cấu hình phân biệt.
10. L3R.1 đóng băng tag, khai trước DL-064, đếm raw đã lưu một lần, ghi errata/exposure.

Nguồn: [DL](../02_decision_log.md), [Step1](../../results/V13_step1/report.md),
[discovery record](../phases/PHASE_3R_discovery_record.md),
[manifest local](../../results/R3R_01_recount/20261028_01/manifest.json).

## Phân loại 14 phát biểu (bao phủ 12 câu của plan)

| # | Phát biểu | Trạng thái / giới hạn | Nguồn |
|---|---|---|---|
| 1 | Ḡ_M≥0 | Identity khi cùng thông tin và posterior/law đúng; không novelty | [T01](../theory/T01_single_observation.md), [contract](../01_definitions_v1_2.md) |
| 2 | X2065 có Ḡ_M≈13,407%C̄ | Discovery, cực trị trong tập đã thử | [report §2](../../results/R3R_01_recount/20261028_01/report.md) |
| 3 | 80/216 có harm | Discovery theoID;78/210 theo cấu hình; không prevalence | [report §0–2](../../results/R3R_01_recount/20261028_01/report.md) |
| 4 | Γ̄ gần như≥0 khi c_sw0 | Discovery về dấu; trong vùngGS<0 thì dấu dương được identity kéo theo; không nói mọi dấu là identity | [report §8–9](../../results/R3R_01_recount/20261028_01/report.md) |
| 5 | Chỉ báo M0 có Spearman≈0,75 | Reviewer/SUMMARY-reported, chọn hậu nghiệm; chưa tái lập được từ code được cung cấp | [record N3](../phases/PHASE_3R_discovery_record.md) |
| 6 | Blind cells không chạm biên rỗng | Kết quả cấu trúc trên discovery Step1, không test mới ngoài mẫu | [Step1](../../results/V13_step1/report.md) |
| 7 | Margin nhỏ + méo không đều gây đảo thứ hạng | Candidate hậu nghiệm trên2ô; chưa hypothesis chính | [Step1](../../results/V13_step1/report.md) |
| 8 | Refinement≤khoảng0,20ppC̄ | Verification điểm trên9cấu hình, không chứng nhận toàn bộ pilot | [report §3](../../results/R3R_01_recount/20261028_01/report.md) |
| 9 | Switching cost không đổi bức tranh | Quá rộng; Stage3 có ghép một phần nhưng không kiểm vùngMV≥1% | [record E3](../phases/PHASE_3R_discovery_record.md) |
| 10 | Telemetry tươi có hại | Quá rộng: S1 gồm mode; pilot chưa tính D22 để tách backlog/mode | [contract D20–22](../01_definitions_v1_2.md) |
| 11 | Ḡ_S<0⇒Γ̄>0 | Identity vì Γ̄=Ḡ_S\|M1−Ḡ_S và Ḡ_S\|M1≥0 | [contract D19](../01_definitions_v1_2.md) |
| 12 | Model value ở B ít headroom/traffic nhanh/horizon dài | Candidate cho Hyp-MV; vùng/luật chưa khóa | [record](../phases/PHASE_3R_discovery_record.md) |
| 13 | Harm và model value cùng vùng | Quá rộng;14/20MV=70% có harm,14/77harm≈18,18% cóMV; hai tập không trùng, không gọi gần như tách rời | [report §8](../../results/R3R_01_recount/20261028_01/report.md) |
| 14 | Đa số harm gần oracle ở S0M0 | Discovery:50/77 có cả\|GM\|,\|GSM\|<0,05%C̄; không exact oracle hoặc equivalence claim prereg | [report §8](../../results/R3R_01_recount/20261028_01/report.md) |

## Điều tôi rút ra — phần soạn theo ủy quyền

Tôi dùng số cấu hình phân biệt khi nói về tập pilot, đồng thời giữ số theo ID để
truy được SUMMARY. Tôi không dùng tỉ lệ trong Stage2 thích nghi để nói tần suất
ngoài đời. Tôi phân biệt dấu Γ bắt buộc trong vùng harm với một phát hiện cơ chế.
Tôi để kết luận engine đúng và realism cho L3R.3/L3R.4; L3R.1 chỉ kiểm sổ dữ liệu đã lưu.

**Understanding/tự làm kín sách: OPEN.** Không có xác nhận mới về human reader,
tự dẫn T07 hoặc tác giả đã tự làm timeline/phân loại mà không xem tài liệu.
