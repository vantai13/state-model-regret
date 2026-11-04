# Thẻ giả thuyết L7.5 — tuổi telemetry τ (ctmc-v1, a = 6)

> **Provenance.**
> - **Bản đầu.** Doan Van Tai — AI (Claude) soạn theo mệnh lệnh "bạn hãy đóng vai trò là tôi và thực hiện đầy đủ các yêu
>   cầu đi… đây là mệnh lệnh" (04/11/2026).
> - **Mentor review (04/11/2026).** Mentor đã review thẻ và `check_l75.py`. Mentor tính lại z_∞(τ) bằng code riêng
>   (TN0003, TP0079, TB0007; lệch ≤ 4e−11) và xem các phân tích zero-fit ở mục 1 và 4. **Mentor không xem truth nào ở
>   τ ≠ 1.** Các sửa đổi trong bản này (bit prior, L75-1a/1b, bộ lọc biên độ của L75-3, eligibility của L75-4, chỉ báo của
>   L75-2, cách diễn đạt SS22, stage D22) do mentor đề xuất; AI cài theo ủy quyền.
> - **Ba quyết định mentor để cho tác giả, AI quyết theo ủy quyền** ("bạn không chờ tôi nói khóa… tự chạy luôn đi",
>   04/11/2026):
>   1. dùng bit prior cho L75-1;
>   2. L75-4 nhận 8 series, n_min = 6;
>   3. bật stage D22, chỉ báo.
> - **Khóa theo cùng lời ủy quyền đó.** Tác giả chưa tự viết lại claim bằng lời mình. Các câu "nếu chỉ đạt…" là của AI.
>   G-level G1. Kết quả phải báo là "test theo thẻ do AI soạn theo ủy quyền, có mentor review trước khóa".
> - **File khóa** (`locks_l75.json`): thẻ, `check_l75.py`, `tau.py`, `ctmc.py`, `scan_tau.py`, `scan2.py`, ba case list,
>   `ZEROFIT_tau.csv`, `zerofit_summary.json`, `PRIOR_BIT.csv`, `L75_4_ELIGIBILITY.csv`.

## 1. Ngày, nhánh, namespace

- 04/11/2026, nhánh `explore/tau-l75`.
- Namespace **ctmc-v1**, a = 6, μ = 10, c_sw = 0, P1, S0/S1, D19, D22 ([SPEC_tau](../../../experiments/explore_ctmc/SPEC_tau.md)).
- **Trục mới duy nhất là τ**, tuổi của Y (backlog đọc ở t0 − τ). Chỉ L00, L01, D22 và twin trên state cũ đổi theo τ;
  V, L10, L11, C_ref không đổi.

## 2. Bốn claim (câu abstract)

- **C-τ1 (liều–đáp ứng, chiều do bit prior quyết định).**
  - Ở h ≥ 7·T_int, chiều của G_S theo τ được quyết định bởi một bit tính được từ zero-fit: quyết định mù thông tin của M0
    (F_stat, M0 trên posterior dừng) có trùng action tốt hơn dài hạn (dấu của s) không.
  - **Prior đúng:** telemetry bị thay càng cũ thì state tươi càng hại; G_S không tăng theo τ.
  - **Prior sai:** khi telemetry bị thay đủ cũ, state tươi có ích; G_S > 0 ở τ = 10·T_int.
- **C-τ2 (onset ở mọi tuổi).** Công thức zero-fit z_pred1(τ, h) đúng tới 0,1 pp từ khoảng 7·T_int ở mọi τ, như ở τ = 1 s.
- **C-τ3 (model đúng, rủi ro).** Với model đúng, giá trị của state tươi S(τ) = L01 − L11 không giảm khi τ tăng.
  - Toán không bảo đảm: Y chỉ có backlog nên chuỗi không Markov.
  - Với Y là cả state (n, m), tính chất này đúng theo bất đẳng thức xử lý dữ liệu (Blackwell).
- **C-τ4 (biên dải theo τ, rủi ro).** Trên các series lát x đủ phân giải (§6, L75-4), biên trên của dải giúp đo bằng truth
  khớp biên tính từ z_pred1 ở cùng (τ, h = 10·T_int), tới 0,01.

### Định vị so với prior (đọc 04/11, AI-T; L7_4_novelty_check §5)

- **C-τ3 đặt trong khung Shisher–Sun 2022** (SS22, Thm 3.4, tr. 34): sai số tối ưu không giảm theo AoI khi chuỗi
  (target, feature) Markov, có thể không đơn điệu khi xa Markov. **Cách ánh xạ target, feature và loss của định lý sang bài
  toán quyết định này chưa kiểm.** Kết quả L75-3 phải báo kèm trích SS22.
- **C-τ1** khác SS22: M0 không phải người quyết định tối ưu, harm đến từ model mù horizon.
  - Ý "thông tin có thể hại người ra quyết định dùng model sai" đã có prior (Galanis 2015, L6.4).
  - Phần có thể là của ta: twin mean-value mù horizon rơi đúng vào trường hợp này, với một bit tính được từ twin và s,
    cộng luật độ lớn z_pred1. Bit cần biết s; ngoài thực tế s phải ước lượng.
- **Câu thực dụng** có nguyên tắc gần nhất là Dahlin 2000 (DAH00, §6, tr. 1045: herding, nhiều request).
- Không claim novelty.

## 3. Tập, trần, cách chạy

| Tập | File (write-once, commit `39afbda5`) | Nội dung | Unit | Dùng cho |
|---|---|---|---:|---|
| SO | `cases_l75/sobol.json` | 81 regime **mới**, 27 mỗi tầng x | 728 | L75-1, -2, -3 |
| OLD | `cases_l75/old.json` | 10 regime asym L7.1 (truth ở τ = 1 đã thấy) | 90 | L75-1, -2, -3 |
| XS | `cases_l75/xs.json` | 269 regime lát x (`zf_a6_xs`), h = 10·T_int | 807 | L75-4 |

- Mỗi regime SO, OLD có 8 tuổi τ/T_int ∈ {0,003; 0,01; 0,03; 0,1; 0,3; 1; 3; 10} và thêm τ = 1 s (không chấm), cùng
  6 horizon h/T_int ∈ {0,3; 1; 3; 7; 15; 30}.
- **Truth chính:** mỗi unit gọi `tau.evaluate(..., disagree=False)` một lần, **không D22** (`scan_tau.TRUTH_D22 = False`).
- **Stage D22 (chỉ báo, mentor mục 6, AI quyết theo ủy quyền):**
  - `scan_tau --mode l75d22`, chạy **sau** truth chính, chỉ trên SO và OLD;
  - chỉ các unit có cờ `d22` (J ≤ 60 CPU-s); thư mục riêng `runs_l75_d22`;
  - UNRESOLVED ở stage này không ảnh hưởng L75-1…4.
  - Dự trù: khoảng 5,1 CPU-h, ước từ CPU D22 đo ở zero-fit (J giống hệt ở truth). Truth bị guard chặn trước khóa nên
    không đo trước được; ba unit nặng nhất chạy đầu tiên và được báo so với ước lượng.
- **Trần:** 900 CPU-s mỗi unit, cả hai stage. Vượt trần thì UNRESOLVED, **không chạy lại**.
- **Một máy:** chỉ GCP `dt4n-research-01`. Không `--shard`, không `--ids`.
- **Dự trù truth chính:** 5–15 CPU-h.

## 4. Những gì đã thấy trước khi viết (và trước khi khóa)

- Toàn bộ truth ctmc-v1 ở τ = 1 s (L7.1, D22, L7.2 a = 6).
- Bảng τ của mentor; AI tái lập 22/24 ô (2 ô lệch chữ số làm tròn), `controls_l75/m.json`.
- **Zero-fit L7.5, không truth** ([STAGE0_REPORT_L75](STAGE0_REPORT_L75.md), [F7](F7_tau_zinf.png)):
  - Trung vị z_∞ theo τ/T_int: x < 0 từ −0,46 → −2,89; x ≥ 0,4 từ −0,48 → −7,97; dải 0 < x ≤ 0,35 từ −0,04 → +5,98.
    Bão hòa ở τ ≈ 0,3–1·T_int.
  - x*(τ) zero-fit: 0,10–0,32 (τ = 0,01·T_int) → 0,42–0,47 (τ = T_int).
- **Bit prior** ([PRIOR_BIT.csv](PRIOR_BIT.csv), tính trên GCP):
  - 58 regime prior đúng, 33 prior sai. Mọi regime prior sai có s > 0, F_stat = 1, x ∈ [0,03; 0,50].
  - Dấu z_∞(10·T_int) = dấu s·(F_stat − F_new) ở 91/91. Đây là **đẳng thức**, không phải bằng chứng.
- **Phần gap M0 ở h = ∞** (mục 8 của mentor, [M0_GAP_PARTS.json](M0_GAP_PARTS.json); số, không diễn giải):

  | Regime | x | s | gap A | gap B | tổng | M0 mù chọn |
  |---|---:|---:|---:|---:|---:|---|
  | TN0003 | −0,54 | −3,43 | −106,9 | +13,6 | −93,3 | Switch (đúng) |
  | TB0007 | 0,28 | +18,88 | −199,1 | +78,9 | −120,2 | Switch (sai) |
  | TP0079 | 0,81 | +1,16 | −1,53 | +2,47 | +0,94 | Stay (đúng) |

- **Ba regime cho hình G_S(τ) cạnh S(τ) sau truth** (chọn từ zero-fit, trước khóa): TN0003 (prior đúng), TB0007 (prior
  sai), TP0079 (harm xuất hiện theo τ: z_pred1 ở 7·T_int từ −0,21 xuống −5,89).
- **Truth ở τ ≠ 1 chỉ ở hai regime control CT1, CT2**, bị loại khỏi mọi tập.

## 5. Quy ước chung

- **Unit** = (regime, τ). **Dòng** = (unit, h). **Chuỗi** = (regime, h) qua 8 tuổi τ của lưới, sắp theo τ. τ của lưới
  tra chính xác từ case list (`tau.tau_grid_map`); τ = 1 s thêm vào bị bỏ, nhưng τ lưới làm tròn đúng 1 s (TB0001) được giữ.
- h gom theo bội số lưới gần nhất (R1 trong `check_l75.py`).
- Mọi % là % của C_ref. G_S so với z_pred1 ở **cùng (τ, h)**; z_pred1 lấy nguyên văn từ `ZEROFIT_tau.csv`.
- **n tối thiểu:** 10 mỗi dự đoán hoặc phần, trừ L75-4 (6; lý do ở L75-4).
- **UNRESOLVED:** chuỗi hoặc series có unit UNRESOLVED/ERROR/thiếu file là unresolved. Hơn 10% thì INCONCLUSIVE; ngược lại
  bỏ khỏi mẫu số và báo số lượng.
- Các phần kết hợp: có FAIL thì FAIL; mọi phần PASS thì PASS; còn lại INCONCLUSIVE.

## 6. Bảng dự đoán

| ID | Claim | Loại | Tập và điều kiện | Đại lượng | Ngưỡng |
|---|---|---|---|---|---|
| L75-1a | C-τ1 | onset (zero-fit 171/174) | SO ∪ OLD, **prior đúng**, h ∈ {7, 15, 30}·T_int: 174 chuỗi, 58 regime | tỷ lệ chuỗi có G_S(τ_{k+1}) ≤ G_S(τ_k) + 0,05 pp ở mọi bước | ≥ 0,90 |
| L75-1b | C-τ1 | onset (zero-fit 98/98) | SO ∪ OLD, **prior sai**, h ∈ {7, 15, 30}·T_int, τ = 10·T_int, dòng có z_pred1 ≥ 0,1: 98 dòng, 33 regime | tỷ lệ dòng có G_S > 0 | ≥ 0,90 |
| L75-2 | C-τ2 | onset | SO ∪ OLD; 3 nhóm tuổi (τ/T_int ≤ 0,03; 0,1–0,3; ≥ 1) × h ∈ {7, 15, 30}·T_int (9 phần; 273/182/273 dòng) | tỷ lệ dòng có \|G_S − z_pred1\| ≤ 0,1 pp | ≥ 0,90 ở 7·T_int; ≥ 0,95 ở 15 và 30·T_int; cả 9 phần |
| L75-3 | C-τ3 | rủi ro | SO ∪ OLD; 546 chuỗi (6 horizon). **Mẫu số:** chuỗi resolved có biên độ S theo τ (max − min) ≥ 0,01 pp | tỷ lệ chuỗi có S(τ_{k+1}) ≥ S(τ_k) − 0,01 pp ở mọi bước | ≥ 0,90 |
| L75-4 | C-τ4 | rủi ro | XS; **8 series đủ phân giải** từ [L75_4_ELIGIBILITY.csv](L75_4_ELIGIBILITY.csv): 6 họ ở τ = T_int, 2 họ u = 2 ở τ = 0,1·T_int | \|x_edge(truth) − x_edge(z_pred1)\| ≤ 0,01 | ≥ 90% (8/8); n_min 6 |

**Ghi chú từng dự đoán:**
- **L75-1:** đạt khi cả 1a và 1b đạt. Quy tắc cũ (z_pred1 < −0,5 ở cả 8 τ, 87 chuỗi) chuyển thành chỉ báo.
- **L75-2:** thêm chỉ báo trên dòng |z_pred1| ≥ 0,5 (44–48% số dòng ở τ ≤ 0,03·T_int) và h = 3·T_int. Verdict không đổi.
- **L75-3, bộ lọc biên độ.** Chuỗi có biên độ < 0,01 pp đếm riêng là "đạt hiển nhiên". Lý do hợp lệ dù bộ lọc dùng truth:
  chuỗi trượt (một bước giảm quá 0,01) luôn có biên độ > 0,01, nên bộ lọc chỉ bỏ chuỗi không thể trượt (test (a)).
  UNRESOLVED tính trên cả 546 chuỗi. Báo thêm: theo h, số regime, mọi vi phạm > 0,1 pp kèm độ lớn.
- **L75-4, eligibility.** Series đủ phân giải khi chiều cao dải ≥ 0,5 pp **và** 0,1 pp / |độ dốc của z_pred1 tại biên|
  ≤ 0,01 (dung sai phải lớn hơn độ chính xác đã kiểm của predictor nhân độ nhạy).
  - n_min = 6 vì 8 series là toàn bộ series đủ phân giải, mỗi series một cặp (họ, τ) khác nhau.
  - 10 series còn lại chỉ báo, kèm max G_S trên x > 0.
- **Chỉ báo khác, không chấm:** R-a (tầng band: G_S không giảm theo τ); D22 (phần backlog F/G_S trên dòng harm theo τ).

### "Nếu chỉ đạt … thì claim còn đứng không" (AI trả lời thay tác giả)

- **L75-1a/1b ≥ 0,90.**
  - Zero-fit đã báo trước (171/174, 98/98), nên đây là onset: kiểm z_pred1 ở τ ≠ 1 trên tập chọn theo cơ chế.
  - Nếu 1a chỉ đạt 0,80, đường liều–đáp ứng ở regime prior đúng gãy dù z_pred1 thì không. Câu "harm tăng theo tuổi"
    không đứng ở dạng đơn điệu.
  - Nếu 1b trượt, bit prior không dự báo được chiều có ích, và câu cơ chế của C5 không đứng.
- **L75-2:** giữ ngưỡng L73-1. Một nhóm tuổi trượt thì claim co về các tuổi đạt.
- **L75-3 ≥ 0,90 trên chuỗi có thông tin.**
  - Đây là dự đoán rủi ro thật duy nhất, không có số zero-fit nào cho S.
  - Nếu chỉ đạt 0,70, giá trị thông tin theo tuổi với model đúng không đơn điệu khi chỉ quan sát backlog, nghĩa là khung
    SS22 thể hiện ở đây. Đó là kết quả riêng; câu thực dụng "twin nhìn được horizon thì nên refresh" phải co lại.
- **L75-4 8/8.** Dung sai 0,01 lớn hơn sai số dự kiến (≤ 0,0044 đơn vị x tương ứng 0,1 pp) trên các series này. Một FAIL
  nói rằng biên dải theo τ không tính trước được, ngay cả nơi đủ phân giải.

## 7. Ý nghĩa từng kết cục

- **L75-1 và L75-2 đạt:** câu tiêu đề được viết (trong model): "với twin mean-value mù horizon, chiều của giá trị
  refresh theo tuổi telemetry do một bit quyết định, bit đó là quyết định mù của twin có trùng action dài hạn không. Prior
  đúng thì refresh càng hại khi telemetry bị thay càng cũ, bão hòa từ khoảng τ ≈ T_int; prior sai thì refresh có ích".
- **L75-1 trượt, L75-2 đạt:** mâu thuẫn nội bộ, xem chuỗi cụ thể. Không viết câu tiêu đề.
- **L75-3:** đạt thì với model đúng, state tươi có giá trị hơn khi state cũ cũ hơn. Trượt thì giá trị thông tin theo tuổi
  không đơn điệu ngay cả với model đúng; đây là kết quả riêng, báo kèm SS22.
- **L75-4:** đạt thì biên dải theo τ tính trước được ở nơi đủ phân giải; trượt thì chỉ giữ "dải rộng ra theo τ" định tính.
- Không có kết luận "đạt" chung. Chỉ báo (R-a, D22, quy tắc cũ của L75-1, các báo cáo phụ) không đổi verdict.

## 8. Cấm sau khi mở

- Không đổi ngưỡng, tập, nhóm, dung sai, bộ lọc, bit prior, bảng eligibility, file zero-fit, trần CPU hay máy chạy.
  Không chạy lại unit UNRESOLVED.
- Không bỏ chuỗi sau khi thấy kết quả. Không thêm dự đoán rồi gọi là đã khóa.
- Quan sát mới sau khi mở ghi riêng, nhãn "khám phá sau khi mở".
- **Không viết câu "telemetry tươi hơn làm hại" ngoài phạm vi và điều kiện của kết quả có khóa** (Lesson Gate L7.5).
