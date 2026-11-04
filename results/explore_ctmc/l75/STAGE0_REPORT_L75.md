# L7.5 Stage 0 — quét tuổi telemetry τ (ctmc-v1, a = 6): zero-fit, control, thẻ nháp

Doan Van Tai — **AI (Claude) thực hiện theo ủy quyền** ("bạn hãy đóng vai trò là tôi và thực hiện đầy đủ các yêu cầu
đi… đây là mệnh lệnh", 04/11/2026). Không phải author-self.
- Nhánh `explore/tau-l75` (từ `explore/twoscale-l73`), worktree `/home/vantai/smr-tau`.
- **Không có truth ở τ ≠ 1** ngoài hai regime control CT1, CT2, cả hai bị loại khỏi mọi case list.
- Mọi số zero-fit và control tính trên GCP `dt4n-research-01` (quy tắc một máy).

## 1. Checklist của prompt

| # | Việc | Trạng thái |
|---|---|---|
| 1 | Trục mới duy nhất là τ; chỉ pipeline dùng Y đổi theo τ | Xong. [SPEC_tau](../../../experiments/explore_ctmc/SPEC_tau.md) viết trước code. `tau.at_tau(τ)` chỉ thay `ctmc.TAU`, `posterior_mean`, `joint_old_current`; `ctmc.py` không đổi byte nào |
| 2 | Lưới τ/T_int ∈ {0,003; 0,01; 0,03; 0,1; 0,3; 1; 3; 10} | Xong; T_int = max của 4 chain (cùng định nghĩa h/T_int); thêm τ = 1 s nối L7.1 |
| 3 | Case list write-once | Xong, commit `39afbda5` **trước** mọi zero-fit. Chi tiết dưới bảng |
| 4 | Zero-fit mọi (regime, τ, h); tái lập τ = 1 | **1.625/1.625 unit COMPLETED**, 0 UNRESOLVED/ERROR, 12,3 CPU-h. τ = 1 tái lập L7.1 tới bit cuối và L7.2 lát x tới 5e−14 (control (a)) |
| 5 | Ước lượng n cho dự đoán | Xong (§4) |
| 6 | Guard: từ chối truth ở τ ≠ 1 tới khi có `locks_l75.json` | Xong. Guard nằm ở `Chain.V` bên trong `at_tau`, nên gọi thẳng `ctmc.evaluate` trong context cũng bị chặn. Runner `scan_tau --mode l75` kiểm thêm hash, stage, máy |
| 7 | `ZEROFIT_tau.csv` + bảng tóm tắt; dừng và báo | Xong (§3). **Dừng ở đây.** |

Chi tiết case list (mục 3):
- **sobol:** 81 regime mới, 27 mỗi tầng x (x < 0; 0 < x ≤ 0,35; x ≥ 0,4), không trùng 3.725 tuple a = 6 đã chạy. Bỏ 28
  điểm vì trần chi phí và 95 điểm ngoài miền.
- **old:** 10 regime asym L7.1, gồm 3 regime của bảng mentor.
- **xs:** 269 regime lát x của L7.2 (bỏ 7 regime ở mép trên miền, x ≥ 0,7, theo trần chi phí), h = 10·T_int, 3 tuổi τ.

## 2. Control (tiêu chí ghi trong SPEC_tau §5 trước khi chạy)

| Control | Kết quả | Ghi chú |
|---|---|---|
| (a) τ = 1 tái lập v1 | **PASS** (attempt02) | 10 regime cũ: lệch ≤ 4e−16, share trùng. 269 lát x: z lệch ≤ 5,2e−14, share ≤ 1,1e−16. **attempt01 FAIL** do code control so share ở h = 10·T_int với CSV L7.2 vốn lưu share ở h = ∞; giữ `attempt01/a.json` kèm chẩn đoán, sửa phép so, tiêu chí không đổi |
| (b) posterior so với `expm` dày | **PASS** | lệch ≤ 7,0e−15 (2 control × 2 chain × 4 τ) |
| (c) Monte Carlo đầu-cuối, CRN, 200.000 episode, gồm D22 | **PASS** | max\|z\| 2,76 / 0,79 (CT1, τ = 0,1 / 3·T_int); 3,06 / 1,25 (CT2). Một đại lượng MC không phân giải: G_M ở CT1, τ = 3·T_int, exact 4,6e−9·C_ref. Tiêu chí cho trường hợp se = 0 được sửa **trước** lượt chính thức, sau một lần chạy thử 2.000 episode (SPEC §5). 1.389 CPU-s |
| (d) cô lập context | **PASS** | sau mỗi context các tên trở lại nguyên; τ = 1 sau τ ≠ 1 trùng JSON với v1 |
| (e) D22 ở τ ≠ 1 | **PASS** | marginal ≤ 8,4e−15, tower ≤ 1,2e−14 |
| (f) τ lớn so với posterior dừng | chỉ báo | ở τ = 10·T_int, \|F_old − quyết định trên posterior dừng\| < 1e−3 ở 97,8% regime (trung vị 6e−16) |
| (m) bảng τ của mentor | chỉ báo | 22/24 ô khớp; 2 ô lệch ở chữ số làm tròn (−1,225 / −1,22; −6,578 / −6,57) |

## 3. Zero-fit theo τ (z = G_S của M0, % C_ref; < 0 là harm; [F7](F7_tau_zinf.png))

| τ/T_int | 0,003 | 0,01 | 0,03 | 0,1 | 0,3 | 1 | 3 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| x < 0 (n 27) | −0,46 | −0,49 | −1,12 | −2,04 | −2,86 | −2,89 | −2,89 | −2,89 |
| x ≥ 0,4 (n 27) | −0,48 | −1,05 | −2,16 | −3,95 | −5,85 | −7,25 | −7,97 | −7,97 |
| 0 < x ≤ 0,35 (n 27) | −0,04 | −0,03 | +0,01 | +0,75 | +4,86 | +5,98 | +5,98 | +5,98 |
| 10 regime cũ | −0,71 | −0,82 | −1,47 | −2,70 | −3,72 | −4,12 | −4,07 | −4,07 |

Các ô là trung vị của z_∞ (h = ∞).

**Đọc (zero-fit, chưa truth):**
- **Ngoài dải giúp, harm tăng theo tuổi của telemetry bị thay rồi bão hòa** từ khoảng τ ≈ 0,3–1·T_int. Đơn điệu không tăng
  ở 27/27 (x < 0) và 19/27 (x ≥ 0,4) regime. Bão hòa vì ở τ lớn, Y gần như không còn thông tin (control (f)).
- **Trong dải giúp, chiều ngược lại:** 23/27 regime có z_∞ không giảm theo τ, và 21 regime đổi dấu từ harm (τ nhỏ) sang
  help (τ lớn). Câu "telemetry càng tươi càng hại" vì vậy **chỉ đúng ngoài dải**. Trong dải, state tươi có ích khi nó thay
  telemetry đủ cũ.
- **Biên dải x*(τ) dịch mạnh** ở h = 10·T_int (zero-fit z_pred1, 6 họ): 0,10–0,32 (τ = 0,01·T_int), 0,29–0,35 (0,1·T_int),
  0,42–0,47 (1·T_int). Ở τ = 1 s, L7.2 cho 0,15–0,24.
- **Tổng 91 regime:** 52 không tăng, 26 không giảm, 13 không đơn điệu.
- **D22, phần backlog z_F,∞/z_∞ trên dòng harm:** 0,65 (τ nhỏ) lên 0,89–0,91 (τ = 0,1–1·T_int).
- **KO:** z_∞^KO tăng từ 0,01 lên 0,54.

## 4. Ước lượng n (mục 5 của prompt)

| Dự đoán tiềm năng | Đơn vị | n |
|---|---|---:|
| Liều–đáp ứng ở h ≥ 7·T_int, chuỗi zero-fit harm ở mọi tuổi | chuỗi (regime, h) | 87 (26 / 30 / 31 ở 7 / 15 / 30·T_int) |
| Onset ở mọi τ | dòng mỗi phần (3 nhóm tuổi × 3 horizon) | 273 / 182 / 273 |
| S(τ) không giảm | chuỗi | 546 |
| Biên dải theo τ | series (6 họ × 3 tuổi) | 18, cả 18 có biên zero-fit |
| Dải giúp, chiều ngược (chỉ báo) | chuỗi tầng band | 162 |

Dòng harm dự kiến theo khoảng τ × h (z_pred1 < −0,5, trên 91 regime mỗi ô) có trong `zerofit_summary.json`
(`n_estimates`):
- h = 3·T_int: 26–38 dòng; h ≥ 7·T_int: 30–51 dòng;
- h = 0,3·T_int: 21–38 dòng;
- **h = T_int: chỉ 4–8 dòng.** Vì vậy thẻ không đặt dự đoán harm nào ở h ≈ T_int.

Bài học L73-4 (n = 24) không lặp lại: mọi dự đoán chấm đều có n ≥ 18 đơn vị, phần lớn hàng trăm.

## 5. Thẻ τ (nháp, CHƯA KHÓA)

[CARD_L7_5.md](CARD_L7_5.md):
- **AI soạn theo mệnh lệnh của tác giả.** Mentor khuyên đây là thẻ của chính tác giả và **review trước khi khóa**.
- **Bốn dự đoán:**
  - L75-1 liều–đáp ứng: nhãn onset, vì zero-fit đã báo trước 87/87;
  - L75-2 onset ở mọi τ;
  - L75-3 S(τ) không giảm: rủi ro, vì Y chỉ có backlog;
  - L75-4 biên dải theo τ: rủi ro.
- **Checker:** [`check_l75.py`](../../../experiments/explore_ctmc/check_l75.py) đã thử trên dữ liệu giả. Trên zero-fit
  thật khi chưa có truth, mọi verdict là INCONCLUSIVE và n khớp §4.
- **Quyết định trước khóa** (AI theo ủy quyền): truth không tính D22 (`TRUTH_D22 = False`). D22 chiếm 92% CPU zero-fit và
  không dự đoán nào dùng.
- **Dự trù truth:** 5–15 CPU-h trên GCP.

## 6. Việc còn mở

- Mentor review thẻ và checker; tác giả nói "khóa"; sau đó mới ghi `locks_l75.json` và chạy truth đúng một lần.
- **Không viết câu "telemetry tươi hơn làm hại"** trước khi có kết quả có khóa (Lesson Gate L7.5). Bảng §3 chỉ là zero-fit.
- Định vị so với M00/Dahlin và Shisher–Sun (đề xuất novelty L7.4, chờ duyệt).

## 7. Chi phí

| Hạng mục | CPU |
|---|---:|
| Zero-fit | 12,3 CPU-h (sobol 5,0; old 0,6; xs 6,7; D22 chiếm 11,4) |
| Control | a 56 + 55 (attempt01 + 02), b 5, c 1.389, d 1, e 13, m 12 CPU-s |
| Thiết kế và test | dưới 0,1 CPU-h |

## 8. File

- Case list: `cases_l75/{sobol,old,xs,design_report}.json`.
- Zero-fit thô: `m0_l75/<stage>/<id>__t<τ>.json`.
- Tổng hợp: `l75/ZEROFIT_tau.csv`, `l75/zerofit_summary.json`, `l75/monotone_tau.csv`, `l75/F7_*`.
- Control: `controls_l75/{a,b,c,d,e,m}.json` và `controls_l75/attempt01/a.json`.
- Log: `logs/l75_*.log`.
