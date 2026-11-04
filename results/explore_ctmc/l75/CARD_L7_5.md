# Thẻ giả thuyết L7.5 — tuổi telemetry τ (ctmc-v1, a = 6)

> **Provenance.** Doan Van Tai — **bản soạn của AI (Claude) theo mệnh lệnh "bạn hãy đóng vai trò là tôi và thực hiện đầy
> đủ các yêu cầu đi… đây là mệnh lệnh"** (04/11/2026).
> - Mentor khuyên thẻ τ "đáng nhất để là thẻ của chính bạn" vì đây là claim tiêu đề, và mentor muốn **review trước khi
>   khóa**. Bản này không thay được hai việc đó.
> - Tác giả chưa đọc, chưa sửa, chưa viết lại claim bằng lời mình. Các câu trả lời "nếu chỉ đạt… thì claim còn đứng không"
>   là của AI.
> - G-level vẫn G1. Kết quả, nếu chạy, phải báo là "test theo thẻ do AI soạn theo ủy quyền".
>
> **CHƯA KHÓA.** Chỉ khóa khi (1) mentor review thẻ này và [`check_l75.py`](../../../experiments/explore_ctmc/check_l75.py),
> (2) tác giả nói "khóa". Khi khóa, ghi `locks_l75.json` gồm sha256 của thẻ, checker, `tau.py`, `ctmc.py`,
> `scan_tau.py`, `scan2.py`, ba case list, `ZEROFIT_tau.csv` và `zerofit_summary.json`.

## 1. Ngày, nhánh, namespace

- 04/11/2026, nhánh `explore/tau-l75` (từ `explore/twoscale-l73`).
- Namespace **ctmc-v1**, a = 6, μ = 10, c_sw = 0, P1, S0/S1, D19, D22 ([SPEC_tau](../../../experiments/explore_ctmc/SPEC_tau.md)).
- **Trục mới duy nhất là τ**, tuổi của Y (backlog đọc ở t0 − τ). Chỉ L00, L01, D22 và twin trên state cũ đổi theo τ;
  V, L10, L11, C_ref không đổi.

## 2. Bốn claim (câu abstract)

- **C-τ1 (liều–đáp ứng).** Ở h ≥ 7·T_int, trên các regime mà zero-fit báo harm ở mọi τ, G_S của twin M0 không tăng khi
  τ tăng. Nói cách khác, telemetry bị thay càng cũ thì state tươi càng hại twin mù horizon.
- **C-τ2 (onset ở mọi tuổi).** Công thức zero-fit z_pred1(τ, h) đúng tới 0,1 pp từ khoảng 7·T_int ở mọi τ, như ở τ = 1 s.
- **C-τ3 (model đúng, rủi ro).** Với model đúng, giá trị của state tươi S(τ) = L01 − L11 không giảm khi τ tăng.
  - Toán không bảo đảm điều này: Y chỉ có backlog, nên Y ở tuổi lớn **không** phải bản "làm nhòe" của Y ở tuổi nhỏ
    (backlog một mình không Markov).
  - Với Y là cả state (n, m), tính chất này đúng theo bất đẳng thức xử lý dữ liệu (Blackwell).
- **C-τ4 (biên dải dịch theo τ, rủi ro).** Trên lát x ở h = 10·T_int, biên trên của dải giúp đo bằng truth khớp biên tính
  từ z_pred1 ở cùng (τ, h), tới 0,01, ở cả ba tuổi τ/T_int ∈ {0,01; 0,1; 1}.

## 3. Tập, trần, cách chạy

| Tập | File (write-once, commit `39afbda5`) | Nội dung | Unit | Dùng cho |
|---|---|---|---:|---|
| SO | `cases_l75/sobol.json` | 81 regime **mới**, 27 mỗi tầng x (x < 0; 0 < x ≤ 0,35; x ≥ 0,4) | 728 | C-τ1, C-τ2, C-τ3 |
| OLD | `cases_l75/old.json` | 10 regime asym L7.1 (truth ở τ = 1 đã thấy) | 90 | C-τ1, C-τ2, C-τ3 |
| XS | `cases_l75/xs.json` | 269 regime lát x của L7.2 (`zf_a6_xs`), h = 10·T_int | 807 | C-τ4 |

- Mỗi regime của SO và OLD có 8 tuổi τ/T_int ∈ {0,003; 0,01; 0,03; 0,1; 0,3; 1; 3; 10} và thêm τ = 1 s (nối với L7.1,
  không chấm), cùng 6 horizon h/T_int ∈ {0,3; 1; 3; 7; 15; 30}.
- **Truth:** mỗi unit (regime, τ) gọi `tau.evaluate(..., disagree=False)` một lần.
  - **Không tính D22 ở truth** (`scan_tau.TRUTH_D22 = False`, quyết định trước khi khóa): không dự đoán nào dùng D22, mà
    ma trận J của D22 chiếm 92% CPU của zero-fit (11,4/12,3 CPU-h).
  - D22 theo τ chỉ có ở zero-fit (§4).
- **Trần:** 900 CPU-s mỗi unit. Vượt trần thì UNRESOLVED, **không chạy lại**.
- **Một máy:** chỉ GCP `dt4n-research-01`. `scan_tau --mode l75` từ chối máy khác, từ chối khi thiếu khóa, không có
  `--shard` hay `--ids`.
- **Chi phí ước lượng:** 4,7 CPU-h theo công thức thiết kế. Công thức này ước thấp 1,5–3 lần so với CPU đo ở zero-fit,
  nên dự trù 5–15 CPU-h, tức 1–2 giờ trên 8 vCPU. Unit zero-fit nặng nhất tốn 398 CPU-s; truth không có D22 nên nhẹ hơn.

## 4. Những gì đã thấy trước khi viết

- Toàn bộ truth ctmc-v1 ở τ = 1 s (L7.1, D22, L7.2 a = 6): onset từ 4–7·T_int, planner dừng, D22.
- Bảng τ của mentor (3 regime, h = ∞, zero-fit). AI tái lập trên GCP khớp 22/24 ô; hai ô lệch ở chữ số làm tròn
  (−1,225 so với −1,22; −6,578 so với −6,57). Xem `controls_l75/m.json`.
- **Zero-fit L7.5, không truth** ([zerofit_summary](zerofit_summary.json), hình [F7](F7_tau_zinf.png)), 1.625/1.625
  unit, một máy:
  - **Dấu của liều–đáp ứng phụ thuộc x.** Trung vị z_∞ theo τ/T_int từ 0,003 tới 10:

    | Tầng | z_∞ trung vị | z_∞ không tăng theo τ |
    |---|---|---:|
    | x < 0 | −0,46 → −2,89 | 27/27 |
    | x ≥ 0,4 | −0,48 → −7,97 | 19/27 |
    | dải 0 < x ≤ 0,35 | −0,04 → **+5,98** | 0/27 (23/27 không giảm; 21 đổi dấu) |
    | 10 regime cũ | −0,71 → −4,07 | 6/10 |

  - **Bão hòa** từ khoảng τ ≈ 0,3–1·T_int. Control (f): ở τ = 10·T_int, quyết định trên state cũ trùng quyết định trên
    posterior dừng ở 97,8% regime.
  - **Biên dải zero-fit x*(τ)** ở h = 10·T_int: 0,10–0,32 (τ = 0,01·T_int), 0,29–0,35 (0,1·T_int), 0,42–0,47 (1·T_int),
    theo 6 họ. Dải giúp **rộng ra** khi telemetry bị thay càng cũ.
  - D22 (zero-fit, h = ∞, dòng harm): phần backlog z_F,∞/z_∞ trung vị 0,65 (τ = 0,003·T_int) lên 0,89–0,91
    (0,1–1·T_int), 0,86 (10·T_int).
  - KO: z_∞^KO trung vị tăng từ 0,01 lên 0,54 theo τ.
- **Truth ở τ ≠ 1 chỉ ở hai regime control CT1, CT2** (Monte Carlo control (c)), bị loại khỏi mọi tập trên.

## 5. Quy ước chung

- **Unit** = (regime, τ). **Dòng** = (unit, h). **Chuỗi** = (regime, h) qua 8 tuổi τ của lưới, sắp theo τ; bỏ τ = 1 s.
- h và τ gom theo **bội số lưới gần nhất** của h/T_int và τ/T_int, vì làm tròn 3 chữ số khiến 7·T_int có thể ra 6,998
  hoặc 7,002 (R1 trong `check_l75.py`).
- **Harm:** z_pred1 < −0,5% (zero-fit, cho điều kiện) hoặc G_S < −0,5% (truth). Mọi % là % của C_ref.
- **n tối thiểu:** 10 (dòng, chuỗi hoặc series) mỗi dự đoán hoặc phần. Ít hơn thì INCONCLUSIVE.
- **UNRESOLVED:** một chuỗi có unit UNRESOLVED/ERROR/thiếu file là chuỗi unresolved. Hơn 10% thì INCONCLUSIVE; ngược lại
  bỏ khỏi mẫu số và báo số lượng.
- G_S so với z_pred1 ở **cùng (τ, h)**, không so với z_∞. z_pred1 lấy nguyên văn từ `ZEROFIT_tau.csv`.

## 6. Bảng dự đoán

| ID | Claim | Loại | Tập và điều kiện | Đại lượng | Ngưỡng |
|---|---|---|---|---|---|
| L75-1 | C-τ1 | onset (zero-fit báo trước 87/87) | SO ∪ OLD; chuỗi có h ≥ 7·T_int và z_pred1 < −0,5 ở cả 8 tuổi | tỷ lệ chuỗi có G_S(τ_{k+1}) ≤ G_S(τ_k) + 0,05 pp ở mọi bước | ≥ 0,90 |
| L75-2 | C-τ2 | onset | SO ∪ OLD; 3 nhóm tuổi (τ/T_int ≤ 0,03; 0,1–0,3; ≥ 1) × h ∈ {7, 15, 30}·T_int (9 phần) | tỷ lệ dòng có \|G_S − z_pred1\| ≤ 0,1 pp | ≥ 0,90 ở 7·T_int; ≥ 0,95 ở 15 và 30·T_int. Đạt khi cả 9 phần đạt. h = 3·T_int chỉ báo |
| L75-3 | C-τ3 | rủi ro | SO ∪ OLD; mọi chuỗi (6 horizon) | tỷ lệ chuỗi có S(τ_{k+1}) ≥ S(τ_k) − 0,01 pp ở mọi bước | ≥ 0,90 |
| L75-4 | C-τ4 | rủi ro | XS; 6 họ (u, λA, κ) × 3 tuổi = 18 series; series không có biên zero-fit bị loại (báo) | \|x_edge(truth) − x_edge(z_pred1)\| ≤ 0,01 | ≥ 90% số series chấm được |

n dự kiến từ zero-fit (Stage 0 mục 5):
- **L75-1:** 87 chuỗi (26 ở 7·T_int, 30 ở 15·T_int, 31 ở 30·T_int). Zero-fit z_pred1 không tăng (dung sai 0,05 pp) ở
  87/87.
- **L75-2:** mỗi phần 273 / 182 / 273 dòng (ba nhóm tuổi).
- **L75-3:** 546 chuỗi.
- **L75-4:** 18 series, cả 18 có biên zero-fit; cần 17/18.
- **Chỉ báo, không chấm:**
  - (R-a) dải giúp: tỷ lệ chuỗi trong tầng band có G_S không giảm theo τ (zero-fit báo 23/27 regime ở h = ∞);
  - (R-b) L75-2 ở h = 3·T_int.

### "Nếu chỉ đạt … thì claim còn đứng không" (AI trả lời thay tác giả)

- **L75-1 ≥ 0,90.**
  - Zero-fit đã báo đơn điệu ở cả 87 chuỗi, nên đây không phải dự đoán rủi ro: nó kiểm onset của z_pred1 ở τ ≠ 1 trên
    các chuỗi harm.
  - Nếu chỉ đạt 0,80, đường liều–đáp ứng của truth gãy ở một số tuổi dù z_pred1 thì không. Câu tiêu đề "harm tăng theo
    tuổi" khi đó không đứng ở dạng đơn điệu, mà chỉ còn "harm lớn hơn khi telemetry bị thay cũ".
- **L75-2: ≥ 0,90 ở 7·T_int; ≥ 0,95 ở 15 và 30·T_int.**
  - Giữ đúng ngưỡng L73-1 để so được: ở τ = 1, 7·T_int đã đạt 100% ở ctmc-v1 và 94–98% ở a = 3/7,5.
  - Nếu chỉ một nhóm tuổi trượt, claim co về các tuổi đạt.
  - Nếu nhóm τ ≥ 1·T_int trượt, khai triển có thể cần thêm hạng do posterior gần dừng.
- **L75-3 ≥ 0,90.**
  - Rủi ro thật: Y chỉ có backlog, toán không bảo đảm. AI không có số zero-fit nào cho S.
  - Nếu chỉ đạt 0,70, "telemetry cũ hơn thì state tươi có giá trị hơn với model đúng" không còn là quy luật. Khi đó giá trị
    thông tin theo tuổi phụ thuộc pha mode bị mất, và câu thực dụng "twin nhìn được horizon thì nên refresh" phải co lại.
- **L75-4 ≥ 17/18, dung sai 0,01.**
  - Ở τ = 1, phân tích sau mở của L7.2 cho lệch ≤ 0,00057 trên 12/12 chuỗi, nên 0,01 là rộng.
  - Rủi ro nằm ở τ nhỏ, nơi biên zero-fit 0,10–0,32 dao động mạnh theo họ.
  - Nếu chỉ đạt 14/18, biên dải ở τ ≠ 1 không tính trước được bằng z_pred1. Câu "dải giúp rộng ra theo tuổi telemetry" khi
    đó chỉ giữ ở mức định tính.

## 7. Ý nghĩa từng kết cục

- **L75-1 và L75-2 đạt:** luật bậc một zero-fit và đường liều–đáp ứng chuyển sang mọi tuổi τ. Câu tiêu đề được viết
  (trong model): "với twin mean-value mù horizon, ngoài dải giúp, state tươi càng hại khi telemetry nó thay càng cũ, và
  bão hòa từ khoảng τ ≈ T_int".
- **L75-1 trượt, L75-2 đạt:** mâu thuẫn nội bộ (z_pred1 đúng mà đường liều–đáp ứng gãy), cần xem chuỗi cụ thể. Không viết
  câu tiêu đề.
- **L75-3:**
  - đạt: với model đúng, giá trị của state tươi tăng theo tuổi của state cũ. Cùng C-τ1, điều này cho câu thực dụng có
    điều kiện "refresh chỉ có ích cho twin nhìn được horizon";
  - trượt: giá trị thông tin theo tuổi không đơn điệu ngay cả với model đúng, khi chỉ quan sát backlog. Đây là kết quả
    riêng, đáng báo.
- **L75-4:** đạt thì biên dải theo τ tính trước được; trượt thì chỉ giữ "dải rộng ra theo τ" định tính.
- Không có kết luận "đạt" chung; mỗi dự đoán báo riêng. Phần chỉ báo (R-a, R-b) không đổi verdict.

## 8. Cấm sau khi mở

- Không đổi ngưỡng, tập, nhóm, dung sai, định nghĩa, file zero-fit, trần CPU hay máy chạy. Không chạy lại unit UNRESOLVED.
- Không bỏ chuỗi sau khi thấy kết quả. Không thêm dự đoán rồi gọi là đã khóa.
- Quan sát mới sau khi mở ghi riêng, nhãn "khám phá sau khi mở".
- **Không viết câu "telemetry tươi hơn làm hại" trước khi có kết quả quét τ có khóa** (Lesson Gate L7.5).
