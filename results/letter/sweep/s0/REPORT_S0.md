# S0: hybrid khác luật tĩnh ở đâu, vì sao (Claude subagent, 21/11/2026; Claude điều phối lưu nguyên văn vì harness chặn subagent ghi file báo cáo)

Phân tích **post hoc, khám phá** trên dữ liệu đã lưu (không mô phỏng). Người phụ trách: Doan Van Tai. Mã: `analyze_s0.py`; số từ `summary_by_h.csv`,
`gate_counts.csv`, `feature_spearman.csv`, `*_groups.csv`, `key_numbers.json`. Quy ước: Δ = regret(luật tĩnh) − regret(hybrid), điểm % C_ref, theo cặp;
Δ > 0 là hybrid tốt hơn; "tốt/tệ" khi |Δ| > 0,05. Đơn vị độc lập: regime (CTMC, GÉANT; hai seed GÉANT chung tham số), ngày (X4b). Các ô (h, τ, phía)
cùng regime không độc lập.

## 1. Lợi ích theo h (Δ trung bình; tốt/tệ trên n)
| Nguồn | Phía | 1/3 T | 1 T | 3 T | 10 T | 30 T |
|---|---|---|---|---|---|---|
| W1b, s đúng (n=93) | fresh | 1,19 (68/0) | 0,75 (67/0) | 0,16 (32/0) | 0,009 (6/0) | 0,000 (0/0) |
| | stale τ=T | 0,015 (11/0) | 0,047 (26/0) | 0,016 (6/0) | 0,001 (0/0) | 0 |
| W1b, ŝ M/M/1 | fresh | 1,52 (81/0) | 0,88 (67/2) | 0,13 (30/9) | −0,025 (5/9) | −0,006 (0/4) |
| X-CTMC, ŝ (n=91) | fresh | | 0,56 (34/0) | 0,25 (17/0) | 0,052 (7/0) | 0,008 (3/0) |
| | stale τ=T | | 0,31 (9/0) | 0,19 (6/0) | 0,017 (3/0) | 0,001 (0/0) |

- W1b: MMPP INVALID ở 93/93, ŝ là fallback M/M/1 (dấu đúng 93/93). X-CTMC: 40 + 51 regime hai lưới (bỏ pilot và ŝ invalid); ở 100 T Δ ≈ 0.
- GÉANT tổng hợp (17 regime × 2 seed, Hybrid (i) so với argmin r̂(i), h = 1, 2, 4, 7, 15, 30 T):
  - fresh tốt 16, 15, 15, 15, 9, 1 trên 34 đơn vị, không ô tệ;
  - stale τ=T tốt/tệ 15/1, 13/3, 9/4, 6/2, 1/0, 0/0;
  - trung vị Δ = 0 mọi h; trung bình bị ba regime gần rỗng (b3_s1) đẩy lên;
  - bỏ ba regime đó, fresh còn 14,4 / 6,3 / 1,8 / 0,48 / 0,043 / 0,003 điểm; ở mọi h ≤ 7 T có 12/28 đơn vị ≥ 0,1 điểm.
- X4b (60 bản ghi): chỉ ngày NEWB3 19/07/2005 có hybrid ≠ luật tĩnh. Δ = 1,98 ± 0,09 (900 s), 1,45 ± 0,19 (1200 s), 0,19 ± 0,13 (1800 s); SE trên 32 instance. Ô khác Δ = 0.
- X5c: chỉ có quyết định, không regret; bất đồng 139/2688 (A), 122/5271 (B), cùng ngày NEWB3 19/07/2005.

## 2. Hybrid thắng/thua nhờ gì
- **Không nhờ tie.** Hybrid chỉ khác luật tĩnh khi gap fluid ngược dấu và |gap| > h|ŝ|; khi M0 tie, hybrid trả về luật tĩnh. Bất đồng nằm ở tie của M0:
  0/4422 (GÉANT, mọi h, τ, seed), 0/161 (X4b), 0/261 (X5c). CTMC fresh: share bất đồng 0 kéo theo |Δ| ≤ 9·10⁻⁹.
- **Nhờ trạng thái tức thời (phía fresh):**
  - GÉANT: 1820/1822 instance bất đồng, action của hybrid rẻ hơn theo đánh giá CRN; M1_new (rollout độc lập) đồng ý với hybrid 1815/1822, nên không phải nhiễu MC.
    Chi phí action tĩnh có trung vị gấp 2,6 lần trung bình regime (proxy "đang nghẽn", tính từ outcome; GÉANT không lưu backlog).
    1250/1822 vẫn bất đồng khi ŝ × 1,5, tức quyết định dứt khoát.
  - X4b: hybrid đúng 161/161, reference đồng ý 161/161. |gap|/(h|ŝ|) chỉ 1,01–1,40 (trung vị 1,05); backlog link nghẽn của đường tĩnh trung vị
    1,86·10⁶ Mbit, tức một đợt burst (n = 1 ngày).
- **Phía stale τ=T yếu hơn nhiều:** W1b (s đúng) 1 T: Δ 0,047 so với 0,75 fresh. GÉANT stale: 479 đúng / 313 sai, lợi 2,42·10⁶ so với lỗ 0,26·10⁶ Mb·s;
  ròng dương nhưng rời luật tĩnh dựa trên telemetry cũ thường sai.
- **Workload và độ tập trung (GÉANT):** fresh, 5 instance lớn nhất chiếm trung vị 27% lợi ích của ô (lợi ích trải rộng); stale 67% (tập trung).
- **Metric:** ba regime gần rỗng có C_ref ≈ 0,1–0,4 Mb·s, lợi tuyệt đối 0,20–0,26 Mb·s mỗi quyết định so với 106–239 ở regime khác, nên phần trăm bị phóng đại;
  S1 cần báo trung vị và giá trị tuyệt đối. CTMC chính xác nhưng C_ref nhỏ ở h = T/3.
- **Nguồn duy nhất làm hybrid tệ hơn là độ lớn ŝ:** W1b ŝ M/M/1 có 33 dòng tệ hơn, tất cả |ŝ|/|s| ≤ 0,42; tệ nhất −1,18 (fresh, 3 T), −5,42 (stale, 1 T).
  Khi |ŝ|/|s| ≥ 0,5, Δ nhỏ nhất −0,01. Với s đúng, hybrid không bao giờ tệ hơn; X-CTMC với ŝ có Δ nhỏ nhất −0,021.
  Ở h = T/3, hybrid M/M/1 (|ŝ| nhỏ hơn) hơn hybrid s đúng (1,52 so với 1,19): h·s hiệu chỉnh quá tay ở h ngắn.

## 3. Đặc trưng dự đoán Δ (Spearman theo regime, từng h)
- **|s|/r_min: âm, mạnh nhất.** Fresh: W1b −0,57 (1 T), −0,72 (3 T), −0,80 (10 T); X-CTMC −0,56/−0,57/−0,50; GÉANT −0,34 đến −0,48.
  X-CTMC |s|/r_min < 0,1: tốt 22/33 (1 T), 14/33 (3 T), 6/33 (10 T); ≥ 0,3: 0/28 mọi h. W1b < 0,1: 10/10, 9/10, 6/10.
- **κ/T_int: dương.** W1b 0,29–0,43 (h ≥ 1 T); X-CTMC (κ nhỏ nhất/T_int) 0,59/0,59/0,49; nhóm κ đường mang flow ≥ T_int tốt 13/23 tại 1 T.
- **Tải của action còn lại: âm.** X-CTMC ρ_max action kia −0,58 (1 và 3 T); GÉANT util_other −0,70 (1 T). Ngoài hai regime gần rỗng, GÉANT chỉ có lợi ở
  6 regime s0 của G2/G3, nơi hai đường gần cân bằng (0,79–0,90) và |s|/r_min = 0,23–1,0; G1 (0,94 so với 0,80) không có lợi.
- **Hướng của luật tĩnh: mạnh.** Lợi ích gần như chỉ có khi luật tĩnh giữ cấu hình hiện tại (Stay). W1b 1 T: fresh 41/51 (Stay) so với 26/42 (Switch);
  stale 26/51 so với 0/42. X-CTMC stale 1 T: 9/40 so với 0/51. GÉANT: cả 8 regime có bất đồng là Stay; 6 regime luật tĩnh Switch không bất đồng ở mọi h.
  Giải thích (chưa kiểm): trạng thái trước quyết định theo cấu hình hiện tại, nên hybrid rời luật tĩnh khi chính đường đang dùng bị nghẽn.
- **Share bất đồng: dương, rất mạnh, tính được không cần truth.** W1b fresh 0,93–0,99 (h ≤ 10 T); X-CTMC 0,98 (1 T), 0,94 (3 T); GÉANT fresh 0,79–0,99.
  Điều kiện cần: không bất đồng thì Δ = 0.
- Yếu: biên độ a/μ (|ρ| ≤ 0,10), tỉ số α (|ρ| ≤ 0,11). Có thể bị chi phối: T_int (−0,62 X-CTMC, −0,67 GÉANT), tie share của M0 (dương).

## 4. Đề xuất cho S1
Trục quét theo ưu tiên:
1. |s|/r_min, log 0,01–1, dày ở ≤ 0,3;
2. hướng luật tĩnh (Stay/Switch) cân bằng;
3. κ/T_int từng đường, log 0,01–10;
4. cân bằng tải ρ_kia − ρ_tĩnh ∈ [−0,15; 0,15] với mức tải 0,6–0,95;
5. h/T_int dày ở 0,3–10;
6. τ ∈ {0; 0,3; 1} T, thêm τ = 0 vì lợi ích chủ yếu ở phía fresh;
7. sai số độ lớn |ŝ|/|s| ∈ {0,25; 0,5; 1; 2} cùng ŝ MMPP và M/M/1.

Ưu tiên thấp: biên độ, tỉ số μ, tỉ số α. Mỗi ô lưu share bất đồng D(h) và quantile |gap|/(h|ŝ|) cho luật vùng ở S2.

Giả thuyết vùng (khám phá, chưa claim):
- **H-A:** fresh, h ≤ 3 T, |s|/r_min ≤ 0,1 và luật tĩnh Stay ⇒ hybrid hơn ≥ 0,1 điểm ở phần lớn regime. Trong mẫu, X-CTMC |s|/r_min < 0,1 gộp hai hướng
  đạt ≥ 0,1 điểm 19/33 (1 T), 12/33 (3 T).
- **H-B:** |s|/r_min ≥ 0,3 hoặc h ≥ 10 T ⇒ |Δ| < 0,05.
- **H-C:** luật một tham số: có lợi chỉ khi D(h) ≥ d*, d* chọn ở S2.
- **Rủi ro:** stale τ=T làm lợi co lại và có thể âm (GÉANT); ŝ bị đánh giá thấp xuống ≤ 0,4 lần gây lỗ 1–5 điểm.

Cổng S2 (≥ 10% regime ≥ 0,1 điểm): trong mẫu đã đạt ở fresh h ≤ 3 T (W1b 27/93 ở 3 T; X-CTMC 14/91 ở 3 T; GÉANT không tính regime gần rỗng 12/28 ở 7 T),
nhưng lưới là lưới thiết kế, không phải quần thể nhà mạng. Ma trận thật chỉ 1/60 bản ghi (một ngày burst), nên S1-C (trace mức giây) là đường duy nhất cho
bằng chứng dữ liệu thật.

## 5. Giới hạn
Post hoc, phụ thuộc thiết kế (X-CTMC phân tầng agree/disagree). CTMC không lưu dữ liệu cấp trạng thái; cơ chế trạng thái chỉ kiểm ở GÉANT và X4b; proxy
"nghẽn" của GÉANT tính từ outcome. X4b một ngày; X5c không có truth. Không đổi verdict hay thẻ cũ, không dùng cho paper nếu chưa qua S3.
