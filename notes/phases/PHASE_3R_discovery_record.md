# Phase 3R — Discovery record: pilot population v1.3

Người phụ trách: **Doan Van Tai** · 28/10/2026 · DL-064. Nhãn: **DISCOVERY**. Không phải contract,
prereg hay evidence cho RQ. Hồ sơ soạn theo ủy quyền tác giả, không phải bài tự kiểm kín sách. Mọi số dưới đây lấy từ
[report đếm lại](../../results/R3R_01_recount/20261028_01/report.md), sinh bởi
[`recount.py`](../../experiments/R3R_01_recount/recount.py).

## 1. Pilot là gì, ở đâu

| Mục | Giá trị | Nguồn |
|---|---|---|
| Địa chỉ cố định | Tag `explore-v13-pilot` → commit `a7435e9a3cb0d1625479c942041ec6748444014a`, branch `explore/v13-population`. **Không merge, không xóa** | `git show explore-v13-pilot` |
| Trách nhiệm và lịch sử thực thi | **Doan Van Tai** phụ trách; pilot được triển khai theo ủy quyền, nguồn gốc giữ ở tag. Commit pilot 28/10/2026 19:21 +07; lúc đó chưa có DL/exposure trong main | SUMMARY.md/docstring nguyên bản tại tag |
| Quy mô | 216 ID chính = **210 regime phân biệt** (6 ID Stage 2 lặp đúng regime Stage 1, output giống hệt) và 18 ID robustness | report §0 |
| Mức số | Stage 1–3: ref 1 (dt 1/120 s), K = 40. Robustness: 9 regime K = 80 (ref 1); 9 regime ref 2 (dt 1/240 s) | report §4 |

## 2. Thiết kế lấy mẫu — đọc mọi tỉ lệ qua mục này

- **Stage 1** (60 ID): λB = 8; λA ∈ {6; 6,5; 7; 7,5; 8}; κ ∈ {0,3; 1; 3}; η ∈ {1/2; 3/4}; h ∈ {2; 8}.
- **Stage 2** (108 ID, chọn **sau khi** thấy Stage 1): λA ∈ {7; 7,5; 8}; λB ∈ {6; 7; 8}; κ ∈ {0,1; 0,3};
  η ∈ {1/2; 3/4}; h ∈ {8; 12; 16}. Sáu ID trùng regime Stage 1.
- **Stage 3** (48 ID): 24 tọa độ của Stage 1 (h = 8, λA ≥ 6,5) × c_sw ∈ {1; 4}. Nằm ngoài D13 của v1.2 (c_sw = 0).
- Hệ quả: mọi tỉ lệ gộp (80/216, 78/210, …) phụ thuộc cách chia stage. **Không phải prevalence.**
- Chỉ báo M0 (Spearman +0,75) là 1 trong 5 chỉ báo, chọn sau khi thấy dữ liệu (SUMMARY tự ghi).

## 3. Errata của SUMMARY.md

SUMMARY.md trên tag giữ nguyên byte. Errata chỉ ghi thêm ở đây (append-only).

| ID | Bản cũ ghi | Raw / đúng là | Kiểm ở | Trạng thái |
|---|---|---|---|---|
| E1 | "Ḡ_S ≤ −1% ở 79/216 regime" | 80/216 theo ID (Stage 1+2: 79/168). Theo regime phân biệt: **78/210** (Stage 1+2: 77/162), vì X1025 = X2030 và X1027 = X2033 là harm bị đếm hai lần | report §0, §2 | Đã đối chiếu raw trong lần đếm này |
| E2 | "mọi đại lượng đổi ≤ khoảng 0,15 điểm %" | Thang % C̄: max 0,153 (K), **0,193** (dt; X2029, Ḡ_S −21,570 → −21,763). Thang % S̄: max 0,630 (K), 0,428 (dt). Chỉ 9 regime. Vẫn dưới dung sai 0,25 điểm % C_ref của v1.2 D1 ở 9 regime này; 207 ID khác (201 cấu hình phân biệt khác) chưa có kiểm tương ứng | report §3 | Đã đối chiếu raw trong lần đếm này |
| E3 | "Switching cost không đổi bức tranh" (POST_PHASE3_CONTEXT §34; PHASE_3R v1.0 §0.1 nêu lý do "Stage 3 không ghép cặp với Stage 2") | Stage 3 **có** ghép tọa độ: với 24 regime Stage 1 và 6 regime Stage 2 (c_sw = 0). Nhưng max Ḡ_M của mọi regime gốc này là 0,852% C̄ < 1%. Câu đúng: "Stage 3 không chạm vùng có model value ≥ 1%, nên không nói được gì về c_sw ở vùng đó" | report §4 | Đã đối chiếu raw trong lần đếm này |
| E4 | "Kết quả (216 regime)" | 216 ID, **210 regime phân biệt**. Sáu cặp trùng cho output giống hệt (chênh 0 trên mọi cột): đó là một kiểm tính tất định, không phải 12 quan sát | report §0 | Đã đối chiếu raw trong lần đếm này |
| E5 | "Chỉ dùng regime mới (ID X…); không dùng ô lưới v1.2, ô R hay R09/R10" | Đúng ở mức **ID**. Ở mức **tọa độ plant**: 45 ID trùng 23 ô v1.2 (21 ô main, R05, R11); 21 ID trong đó có c_sw = 0 như v1.2. R05 và R11 đã mở ở A05-T. Không ID nào cùng κ (3/5) hoặc cùng h (4 s) với R09/R10 | report §6 | Đã đối chiếu raw trong lần đếm này |
| E6 | Stage 3 "như đợt 1 (h = 8) cộng c_sw ∈ {1, 4}" | Bỏ λA = 6: 24/30 tọa độ của Stage 1 h = 8. Code không ghi lý do | report §4 | Đã đối chiếu raw trong lần đếm này |
| E7 | "Đánh giá: TỐT"; "dấu của Γ̄ không đổi" được xếp vào "chưa đạt để lên rất tốt" | Rubric trong docstring `population.py` đặt điều kiện "Γ̄ non-negligible with a sign that varies across regimes" ở mức **TOT (good)**, không ở RAT TOT. Raw: 0 ID có Γ̄ ≤ −0,5% C̄; min Γ̄ = −0,137%, chỉ khi c_sw > 0. **Đánh giá thận trọng:** non-negligible chưa có luật chấm vận hành được khóa; số theo ngưỡng0,5% C̄ chỉ là diagnostic, không tự thay điều kiện “hoặc10% stakes”; nhãn TỐT chưa được xác nhận như một verdict | docstring tại tag; report §9 | Đã ghi giới hạn rubric; không dùng nhãn TỐT làm verdict |

## 4. Ghi chú provenance (không phải lỗi số)

- **N1 — dt.** Stage 1–3 chạy ở dt 1/120 s, thô hơn dt đã khóa của Phase 3 (1/240 s, DL-053). Mọi số pilot
  là mức ref 1, trừ 9 regime robustdt.
- **N2 — λB và η.** Pilot cho λB ∈ {6; 7; 8}, ra ngoài v1.2 D4 (B OFF 2/ON 14, tức λB = 8). Nhãn η giữ đúng
  câu chữ v1.2 D5 (u = 2η). Khi λB ≠ 8, phần chỗ trống của B mà tải chuyển chiếm là u/(μ − λB), khác η
  (report §5; ví dụ λB = 6, η = 3/4 → u/(μ − λB) = 3/8). Nếu v1.3 giữ λB làm trục thiết kế thì cần DL
  (draft v1.3 §2) và phải chọn định nghĩa η. **OPEN — quyết định nghĩa ở L3R.5, không sửa dữ liệu cũ.**
- **N3 — chỉ báo M0.** Commit `a7435e9` không có code tính 5 chỉ báo hay Spearman +0,75, nên con số này
  chưa tái lập được từ repo. Nếu Hyp-MI dùng chỉ báo này, phải viết định nghĩa trước rồi mới tính.
- **N4 — rubric "viết trước".** Docstring ghi rubric viết trước khi quét. Nhưng code, rubric và kết quả nằm
  trong **một** commit, nên git không chứng minh được thứ tự đó.
- **N5 — D22.** Pilot không tính pipeline D22 (backlog tươi, mode ẩn), nên chưa tách được harm do backlog
  tươi hay do thấy mode.
- **N6 — c_sw.** CSV Stage 1–2 không có cột c_sw; recount gán 0 theo mặc định của `scan.py`.

## 5. Những gì đã thấy — DISCOVERY, chưa kiểm

Số theo regime phân biệt, Stage 1+2 (c_sw = 0, n = 162), trừ khi ghi khác.

| # | Phát biểu | Trạng thái | Nguồn |
|---|---|---|---|
| 1 | Ḡ_M ≥ 1% C̄ chỉ xuất hiện ở λB = 8 (20 regime); max 13,41% C̄ tại X2065 | Discovery → candidate cho Hyp-MV | §8, §2 |
| 2 | Harm (Ḡ_S ≤ −1% C̄): 77 regime; theo λB = 6/7/8: 36/21/20 | Discovery trên mẫu thích nghi | §8 |
| 3 | Chỉ 14 regime có cả harm và Ḡ_M ≥ 1% | Discovery; câu “cùng vùng” quá rộng, chưa là hypothesis theo vùng đã khóa | §8 |
| 4 | 50/77 regime harm có \|Ḡ_M\| và \|Ḡ_SM\| < 0,05% C̄ (54 ở ngưỡng 0,1%; 59 ở 0,5%) | Discovery; gợi ý cơ chế "snapshot cũ che lỗi phụ thuộc state của M0" — chưa kiểm | §8 |
| 5 | \|Γ̄\| ≥ 1%: 79 regime, cả 79 có Ḡ_S < 0; trong 73 regime có Ḡ_S ≥ 0, không regime nào có Γ̄ ≥ 1% | Discovery về ngưỡng/độ lớn; dấu Γ̄ dương trong vùng harm là hệ quả identity, không finding độc lập | §8 |
| 6 | Ḡ_S\|M1: max 1,753%; ≥ 1% ở 10 regime; trung vị 0,1455% | Discovery | §8 |
| 7 | Raw thỏa các identity đã kiểm | Sanity; không chứng minh engine đúng (L3R.3) | §7 |
| 8 | 9 regime robustness: chênh ≤ 0,193 điểm % C̄ | Verification điểm | §3 |

**Điều tôi rút ra — bản tổng hợp theo ủy quyền, không phải attestation tự viết:**

> Tôi phân biệt 216 ID với210 cấu hình trước khi dùng một tỉ lệ. Tôi giữ riêng vùng harm và
> vùng model value, không gộp hai pattern thành một quy luật. Tôi đọc eta theo đúng code của
> pilot và dùng các đính chính trên thay cho câu chữ SUMMARY. Kết quả này cho biết dữ liệu
> đã lưu nói gì; tính đúng của engine và realism vẫn phải kiểm ở L3R.3/L3R.4.

## 6. Dữ liệu đã lộ — dùng ở L3R.7

**Đính chính diễn giải Part1:** 14 cấu hình chồng lấn tương ứng **14/20=70%** tập có
model value và **14/77≈18,18%** tập harm phân biệt. Vì vậy hai tập không trùng nhau,
nhưng không đủ căn cứ gọi chúng “gần như tách rời”. Nhận xét harm ở λB6 cũng chỉ là
nhóm đông nhất (36/77), không phải đa số vượt50%.

- [`discovery_regimes.csv`](../../results/R3R_01_recount/20261028_01/discovery_regimes.csv): 234 ID (216 chính
  và 18 robustness), **chỉ tham số**, không outcome.
- Tọa độ plant v1.2 đã bị pilot chạm: 23 ô (21 main, R05, R11). Danh sách ở report §6.
- R09/R10: không ID pilot nào cùng κ hoặc cùng h.
- *(Later — L3R.3)* 21 ID pilot c_sw = 0 trùng tọa độ ô v1.2 là chỗ có thể đối chiếu engine population với
  engine v1.2 tại cùng y.

## 7. Record này KHÔNG cho phép nói

- "x% mạng có harm" — mẫu thích nghi (§2).
- "Engine population tính đúng" — chưa audit (L3R.3).
- "Fresh telemetry có hại" — S1 gồm cả mode; không có D22 (N5).
- "Switching cost không đổi bức tranh" — E3.
- "State và model bổ trợ nhau" như một phát hiện độc lập — identity (§5 dòng 5).
- "η = phần chỗ trống của B" khi λB ≠ 8 — N2.
- "Chỉ báo M0 dự báo được model value" — chọn hậu nghiệm và chưa tái lập (N3).


## 8. Kiểm chứng và trạng thái thực thi L3R.1

- Đếm local đúng một lần từ tag; output khớp preview ZIP ngoài dòng Rev. Bản paste thiếu
  newline cuối, không khác nội dung; lỗi assertion phần trình bày đã được ghi và phục hồi
  metadata, không đếm lại hoặc sửa report máy sinh.
- 13/13 tests riêng,423/423 toàn repo PASS;3/3 mutant bị bắt trên CSV giả.
- Tag được tạo trước commit khai trước do bước kiểm định dạng chặn commit ban đầu;
  cả tag và commit khai trước đã lên remote **trước** khi đếm. Không sửa/di chuyển tag.
- Điều kiện “pilot không trùng tọa độ v1.2” trong plan không thỏa; đã báo45 ID overlap,
  không gọi đó là lỗi script hoặc sửa dữ liệu để ép PASS. Chưa có outcome R09/R10 mới.
- V9 WAIVED_BY_AUTHOR; P0-V10/L8/T05/Understanding và các mục tự viết giữ trạng thái cũ.
  Học L3R.2 được; L3R.3/L3R.4 vẫn theo phụ thuộc T07/tag/exposure của plan.

[Báo cáo thực thi](../../results/lessons/l3r_1/report.md) ·
[Manifest](../../results/R3R_01_recount/20261028_01/manifest.json) ·
[Verification](../../results/lessons/l3r_1/verification.json).
