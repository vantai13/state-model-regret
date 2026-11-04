# L7.4 — Bảng claim–evidence (chuẩn bị viết)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền** (04/11/2026, "đóng vai trò là tôi và thực hiện đầy đủ các yêu cầu").
Chỉ đọc kết quả đã lưu; không chạy truth mới. Nhánh `synthesis-l74`, từ `explore/twoscale-l73` (`73b1b7ec`).
G-level vẫn G1. Mọi thẻ của L7.2 và L7.3 do AI soạn, không có mentor review trước khi khóa. Chưa có câu nào ở đây được
tác giả tự viết lại.

**Loại bằng chứng:**
- **toán**: đẳng thức hoặc mệnh đề có chứng minh (T11), đúng theo cấu trúc;
- **khóa (AI)**: test khóa trước theo thẻ do AI soạn;
- **khám phá**: chạy rộng, không chấm;
- **sau mở**: phân tích sau khi đã mở kết quả, không phải test.

Phạm vi chung, trừ khi ghi khác:
- ctmc-v1: hai path MMPP/M/1, μ = 10, τ = 1 s, P1 stationary, c_sw = 0, một action giữ suốt h, S1 gồm mode oracle;
- ctmc-v2: hai bộ điều biến đối xứng, đỉnh a_f + a_s = 6.

## C1 — Luật bậc một zero-fit cho twin mù horizon

> Với twin M0 (rollout trung bình có điều kiện, mù horizon), G_S(h) = h·s·ΔF + B + O(e^{−γh}). Do đó z(h) khớp công thức
> z_pred1(h), tính chỉ từ M0 và đại lượng dừng, tới 0,1 pp từ khoảng 4–7·T_int.

| Bằng chứng | Loại | Số |
|---|---|---|
| [T11](../theory/T11_proposition1_first_order.md) Mệnh đề 1 | toán (AI viết) | phần (i) chính xác với mọi h; R_h giảm theo hàm mũ, 1/γ ≈ 1,8·T_int ở regime kiểm (T11 §7) |
| AS-R1a ([score_asymptote](../../results/explore_ctmc/score_asymptote.json)) | khóa (AI) | 91,9% dòng h/T_int ≥ 3 trong 0,1 pp (gộp khoảng); đọc lại theo khoảng: 10% ở (1; 2], 50% ở (2; 4], 100% từ (4; 7] |
| AS-R1b | khóa (AI) | **FAIL** 43,2% ở 1 ≤ h/T_int < 3 |
| L72-1 ([score_l72](../../results/explore_ctmc/score_l72.json)) | khóa (AI) | a = 3 PASS: (4; 7] 94,4% (n 54), (7; 15] 100%, (15; 40] 100%. a = 7,5 INCONCLUSIVE: (15; 40] có 17% case UNRESOLVED |
| L73-1 ([score_l73](../../results/explore_ctmc/score_l73.json)) | khóa (AI) | PASS cả 6 phần: T_s/T_f = 10: 1,00/1,00/1,00; T_s/T_f = 100: 0,993/1,00/1,00 |
| KO onset (L7.2 Phần 1) | khóa (AI) | 89,6% ở (2; 4], 96,9% ở (4; 7], 100% từ (7; 15] |
| Hình F1 | mô tả | [F1_onset.png](../../results/explore_ctmc/figures_l74/F1_onset.png) |

- **Phạm vi:** ctmc-v1 a ∈ {3, 6, 7,5}; ctmc-v2 T_s/T_f ∈ {10, 100}; tải ≤ 9,75; N theo luật đuôi 1e−13 (ctmc-v2: N ≤ 3000).
- **Claim co lại khi:**
  - h < 4·T_int: z_pred1 sai cả dấu ở h ≈ T_int/3 (T11 §7);
  - (1; 2] chỉ 3%, (2; 4] 26% ở ctmc-v2;
  - a = 7,5 với horizon dài nhất: không chấm được vì case vượt trần;
  - τ ≠ 1: chưa kiểm (L7.5 đang chạy Stage 0).

## C2 — Planner dừng đủ dùng ở horizon dài

> Từ khoảng 7·T_int, luật dừng Static (chọn action có r nhỏ hơn, không nhìn state) có regret ≤ 0,1% C_ref ở ≥ 95% dòng
> δ ≠ 0.

| Bằng chứng | Loại | Số |
|---|---|---|
| T11 §5 | toán | truth hội tụ về action dài hạn: share Switch 0,9969 ở 1·T_int, 0,999996 ở 3·T_int |
| AS-R5a | khóa (AI) | Static thắng M0 tươi ở 90,9% regime khi h ≥ 3·T_int (sát ngưỡng 90%) |
| L72-3 | khóa (AI) | a = 3: 95,3% (n 213); a = 7,5: 100% (n 139) |
| L73-2 | khóa (AI) | 0,967 (n 727), cả hai T_s/T_f (0,964; 0,971) |
| D-R5 | khóa (AI) | **FAIL** 86,6%: Static thua M0 với (Y, Q) ở δ = 0 (85/98 dòng trượt). Đọc sau mở: bỏ δ = 0 thì 98% |
| Hình F2 | mô tả | [F2_static.png](../../results/explore_ctmc/figures_l74/F2_static.png) |

- **Phạm vi:** như C1. Static chỉ là luật nhìn dấu của s, nên cần biết s (model đúng ở dài hạn).
- **Claim co lại khi:** δ = 0 (s = 0, Static luôn Stay); h trong khoảng 3–7·T_int (AS-R5a sát ngưỡng).

## C3 — Telemetry tươi hại twin mù horizon ở đa số regime; dải giúp hẹp

> Ở h dài, thay state cũ bằng state tươi làm M0 tệ hơn (G_S < 0) ở đa số regime. Dải giúp chỉ ở 0 < x < x*, với
> x* ≈ 0,12–0,29 tùy họ (u, λA, κ) và biên độ.

| Bằng chứng | Loại | Số |
|---|---|---|
| BR-R5 | khóa (AI) | x lớn nhất có G_S > 0,1% ≤ 0,35 ở cả 4 chuỗi (0,2–0,3) |
| BR-R4a / R4b | khóa (AI) | x < 0, P ≥ 30: 96,6% harm (PASS); x > 0,5: 82,9% (**FAIL**, cần 90%) |
| Stage E | khám phá | h ≥ 3·T_int: x < 0 và x > 0,5 bị hại ở 95–100%; dải giúp khoảng (0; 0,25) |
| L72-2 | khóa (AI) | **FAIL** cả a = 3 (3/6) và a = 7,5 (4/6): biên dải truth không khớp biên z_∞ tới ±0,05 |
| L72-2 so với z_pred1 cùng h | **sau mở** | lệch lớn nhất 0,00057 (a = 3), 0,00031 (a = 7,5), 12/12 chuỗi. Mọi z_pred1 đã hash trước truth, nhưng phép so là sau mở |
| L72-4 | khóa (AI) | dải co từ 9,3% xuống 3,75% khi a = 3 → 7,5 (PASS sát ngưỡng 0,05) |
| x* theo a (zero-fit) | khám phá | cùng họ, a = 3 cho x* lớn hơn a = 6 khoảng 0,001–0,047 (SUMMARY §11B) |
| Hình F3 | mô tả | [F3_band.png](../../results/explore_ctmc/figures_l74/F3_band.png) |

- **Phạm vi:** τ = 1 s. Sobol thiết kế theo mật độ của thiết kế, **không** theo tần suất ngoài đời, nên "đa số regime" là
  tỷ lệ trong thiết kế.
- **Claim co lại khi:**
  - không dự báo được biên dải tới ±0,05 bằng z_∞ (L72-2 FAIL); chỉ giữ "dải hẹp" định tính;
  - dấu ở dải giúp có thể đổi theo τ (bảng τ của mentor; L7.5).
  - ở τ ≥ T_int, dải giúp zero-fit kéo tới x ≈ 0,42–0,5 (L7.5 Stage 0); "dải hẹp" chỉ đúng khi τ ≪ T_int. Theo bit prior
    (mentor review 04/11), dải giúp ở τ lớn là tập regime mà quyết định mù của M0 (F_stat) sai so với action dài hạn: 33/91
    regime, tất cả có s > 0, F_stat = 1, x ∈ [0,03; 0,50] (`l75/PRIOR_BIT.csv`, zero-fit).

## C4 — Harm có cả khi telemetry tươi chỉ có backlog

> State tươi chỉ gồm backlog (không có mode) đã đủ làm M0 tệ hơn. Phần backlog chiếm 60–89% harm tùy κ ở ctmc-v1, và
> 24–71% ở ctmc-v2 tùy phần thang chậm f.

| Bằng chứng | Loại | Số |
|---|---|---|
| D-T1 | toán | F + V = G_S và F1 + V1 = S trên 2.941 dòng, sai số ≤ 4e−14 |
| D-R1 | khóa (AI) | dòng harm có F < −0,1% ở **100% (n 949)**. Phần lớn đã được zero-fit báo trước (z_F,∞ < 0 ở 1.982 regime harm) |
| D-R3, D-R4 | khóa (AI) | h < T_int: F < 0 ở 100%; với model đúng F1 ≥ V1 ở 100% (n 301) |
| L72-5, L72-6 | khóa (AI) | PASS ở cả a = 3 (98,9%, n 91; 100%, n 169) và a = 7,5 (100%, n 35; 100%, n 84) |
| L73-4 | khóa (AI) | 0,958, nhưng **chỉ n = 24** (T_s/T_f = 10 có n = 10, bằng mức tối thiểu) |
| z_F,∞/z_∞ ở ctmc-v2 | zero-fit | trung vị 0,24–0,71 theo (f, T_s/T_f) (Stage 0 L7.3 §4) |
| Hình F4 | mô tả | [F4_backlog.png](../../results/explore_ctmc/figures_l74/F4_backlog.png): trung vị 0,89 ở κ ≈ 0,03 xuống 0,49 ở κ ≈ 3 |

- **Phạm vi:** N ≤ 3000 mỗi path (D22); κ ≤ 5; tải ≤ 9,75.
- **Claim co lại khi:**
  - κ lớn hoặc thang chậm chiếm nhiều phương sai: phần mode lớn dần (0,32 ở κ > 5 theo zero-fit; 0,24 ở f = 1/2,
    T_s/T_f = 100);
  - ctmc-v2 chỉ có 24 dòng harm.

## C5 — Cơ chế "planner dừng ngầm" (giả thuyết, chưa đứng)

> Với state cũ (posterior gần dừng), M0 đúng nhờ lấy trung bình. State tươi khiến nó phản ứng theo dao động, và mỗi lần
> phản ứng sai trả khoảng h·|s|.

| Bằng chứng | Loại | Số |
|---|---|---|
| KO-R1, KO-R2, KO-R5 | khóa (AI) | 9/0. Nhưng KO-R1/R2 viết sau khi thấy z_∞^KO nhỏ, nên chủ yếu là toán/onset. **Cách đọc cũ đã rút lại** |
| KO sai đều | sau mở | trên dòng harm h > 4·T_int, KO chọn action dài hạn ở 13–15% state; regret 31,6%/31,5% C_ref |
| M0 đúng nhờ trung bình | sau mở | a = 6, h ≥ 4·T_int, δ ≠ 0: harm (n 604) chọn action dài hạn ở 0,895 (cũ) và 0,723 (mới); help (n 110): 0,257 và 0,345 ([F5](../../results/explore_ctmc/figures_l74/F5_planner.png)). SUMMARY §11A ghi n 543, cùng giá trị, trên tập hẹp hơn |
| L72-7 | khóa (AI) | KO tệ hơn M0 ≥ 1,5 lần ở 99,5% dòng harm (a = 3); a = 7,5 INCONCLUSIVE |
| L73-3 | khóa (AI) | 0,939 PASS, nhưng **không tách được** khỏi đồng hồ T_int (review mentor: không tăng theo f; 93/95/93%) |

- **Trạng thái:** giả thuyết. Có mô tả phù hợp nhưng chưa có test phân biệt với giả thuyết đối thủ.
- **Test đề xuất:** quét τ (L7.5) là phép thử liều–đáp ứng. Posterior càng cũ thì càng gần dừng, nên harm phải tăng đơn
  điệu theo tuổi của telemetry bị thay.
- **Claim co lại khi:** quét τ cho thấy không đơn điệu; hoặc ở dải giúp dấu đổi theo τ mà cơ chế không dự báo.

## C6 — Hai đồng hồ: T_int xếp hội tụ, P xếp "state hay model"

| Bằng chứng | Loại | Số |
|---|---|---|
| AS-R4 | khóa (AI) | Spearman −0,921 (h/T_int) so với −0,735 (h/κ), n 210 ([F6](../../results/explore_ctmc/figures_l74/F6_clocks.png) tái lập đúng) |
| L72-8(b) | khóa (AI) | a = 3: −0,886 so với −0,640; a = 7,5: −0,959 so với −0,812 (PASS) |
| BR-R3 | khóa (AI) | **FAIL**: P đúng 85,0% nhưng P* = 36, ngoài [5, 30] |
| L72-8(a) | khóa (AI) | a = 3 PASS (P 93,2% so với đa số 81,8%); a = 7,5 **FAIL** (ngưỡng không thể đạt do thẻ, lỗi thiết kế AI) |
| Stage E | khám phá | P 95,4% (P* ≈ 14), h·\|s\|/r_min 93,1%, h/κ 92,8%, h/T_int 87,9%; tỷ lệ nền 86,2% |
| T_relax/T_int | zero-fit | 1,4–1,9 ở ctmc-v2: đồng hồ tích phân và đồng hồ chậm nhất gần nhau, chưa phân biệt được |

- **Claim co lại khi:** ngưỡng P* phụ thuộc representation và thành phần mẫu (36 so với 14). Chỉ giữ "P xếp thứ tự tốt
  nhất", không giữ một ngưỡng.

## C7 — Representation: cấu trúc định tính giữ, ngưỡng dịch

| Bằng chứng | Loại | Số |
|---|---|---|
| BR-R1 | khóa (AI) | dấu G_S trùng fluid 79,4% (n 345), cần 75% |
| BR-R2 | khóa (AI) | **FAIL** 79,6%, cần 80% (sát) |
| F-R2 (Stage F, c_sw > 0) | khóa (AI) | không có harm: G_S ≥ −0,25% ở 100% dòng c*. Cơ chế D(ii) của Phase 6 không xuất hiện trong CTMC |
| Theo κ | khám phá | cùng dấu với fluid: 61% (κ ≤ 0,05) → 100% (κ ∈ (1; 5]) |

- **Đọc:** Gate D của Phase 6 (REFORMULATE) là trong plant fluid. CTMC cho thấy dấu của nhánh D phụ thuộc
  representation. Xem [ghi chú đóng Gate D](L7_4_closures.md#5-gate-d-phase-6).

## Phân tích sau khi mở (tách riêng, không dùng làm bằng chứng khóa)

1. Biên dải theo z_pred1 cùng h, 12/12 chuỗi (L72-2, của mentor, AI kiểm lại).
2. So khớp L73-3 theo cùng h/T_int, theo κ và theo f (review mentor 04/11): không gán phần dư cho mode chậm.
3. Cách đọc lại KO: "sai đều", "đúng nhờ trung bình" (đính chính trong SUMMARY §11A).
4. D-R5 bỏ δ = 0 (98%).
5. L73-1 ở (1; 2] và (2; 4] (0,03; 0,26).
6. Tất cả các trung vị trong F4–F5.

## Liên hệ với dòng chính (main, không thuộc Phase 7)

- Phase 5: H-L1 v1.1 PASS 10/0/0 nhưng là post-hoc design revision; Gate C = NARROW.
- Phase 6: Gate D = REFORMULATE (predictor weighting).

Các claim ở trên **không** thay kết quả dòng chính. Chúng là bằng chứng của nhánh khám phá CTMC, cần merge có quyết định
riêng (tag `phase-7-evidence` chỉ khi Gate Phase 7 GO).
