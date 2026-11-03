# L7.1 — CTMC MMPP/M/1 (ctmc-v1): tổng kết

Doan Van Tai — **AI (Claude) thiết kế, chạy và soạn theo ủy quyền** ("thực hiện theo hướng dẫn và bạn tự chạy đi",
03/11/2026). Exploration trên nhánh `explore/ctmc-phase7`, worktree `/home/vantai/smr-ctmc`. Không phải author-self,
không phải confirmation của contract v1.3, không phải claim novelty. Tác giả không ghi dự đoán riêng (mục 9 lesson);
mọi dự đoán là của AI. Plant khác contract (packet-level, μ = 10, a = 6, τ = 1), giữ P1, S0/S1, D19.

## 1. Control (đọc trước)

| Control | Kết quả |
|---|---|
| V1 u = 0, V2 a = 0, V4 hai cách tính V, V9 M0 dạng đóng, V10 posterior, V11 dấu Static | PASS cả hai máy |
| V3 Monte Carlo đầu-cuối, 10⁵ episode, CRN, 3 regime | PASS, \|z\| ≤ 1,7 (ngưỡng 3,5); G_S, S lệch 10–32 SE khỏi 0; G_M yếu |
| V5 N → 2N, 4 góc nặng nhất (N tới 53.025; h tới 44.200 s) | PASS, thay đổi lớn nhất 1,2e−10 pp |
| V6 S, M, G_M ≥ 0 trên mọi dòng; V11 trên mọi case | 0 cờ, 0 lỗi trên 3.455 case |
| V7 bit-identical hai máy | attempt01 FAIL → sửa → PASS |

**Hai sửa đổi trước khi khóa dự đoán, cả hai do control bắt được:**
1. V7: numpy/OpenBLAS chọn kernel SIMD khác nhau giữa AMD local và Xeon GCP (AVX-512). Sửa bằng `env.sh` chung và
   `det_expm1`.
2. **Bug thật của evaluator:** ở horizon ngắn, gap M0 của hai path triệt tiêu chính xác khi cả hai queue không chạm 0
   (−u·h²/2 + u·h²/2), nhưng dấu đang do làm tròn quyết định (khối lượng tới 0,89). Sửa thành luật hòa chính xác
   (Stay), như certified tie của contract. Lịch sử: `controls/attempt01/`, `attempt02_killed/`, `m0_attempt01/02/`.

## 2. Bridge fluid → CTMC ([PREDICTIONS_bridge.md](PREDICTIONS_bridge.md), [score](score_bridge.json))

Khóa ở commit `27edf80b` trước mọi truth trên tập chấm. 1.374 case (1.200 tuple sobol4, xslice, pslice).

| ID | Dự đoán | Kết quả | |
|---|---|---|---|
| BR-G1, G2 | đồng nhất thức; Static theo dấu δ | đúng trên 1.374 case | toán |
| BR-R1 | dấu G_S trùng fluid ≥ 75% | 79,4% (n = 345) | ✅ |
| BR-R2 | nhãn S>M trùng fluid ≥ 80% | 79,6% (n = 147) | ❌ sát ngưỡng |
| BR-R3 | P đúng ≥ 85%, hơn h/κ ≥ 3 điểm, P* ∈ [5, 30] | 85,0%, hơn 5,6 điểm, nhưng **P* = 36** | ❌ |
| BR-R4a | P ≥ 30, x < 0: G_S < −0,1% ≥ 90% | 96,6% (n = 29) | ✅ |
| BR-R4b | P ≥ 30, x > 0,5: G_S < −0,1% ≥ 90% | 82,9% (n = 70) | ❌ |
| BR-R4c | P ≥ 30, 0 < x ≤ 0,5: Γ < 0 ≥ 40% | 27,3% (n = 44) | ❌ |
| BR-R5 | dải giúp hẹp: x lớn nhất có G_S > 0,1% ≤ 0,35 | 0,2–0,3 ở cả 4 chuỗi | ✅ |
| BR-R6 | δ = 0: M ≤ 0,3% ≥ 95% | 100% (n = 157) | ✅ |
| BR-R7 | κ ≤ 0,05: trung vị S+M CTMC < fluid | 0,14% so với 1,27% | ✅ |
| BR-R8 | h/T_int ≥ 3: truth chọn path nhẹ ≥ 90% | 100% (n = 18) | ✅ |
| BR-T1 | h/T_int ≥ 3: dấu G_S = dấu z_∞ ≥ 90% | 100% (n = 25) | toán + onset |

**Theo tầng κ (mô tả):** tỷ lệ cùng dấu G_S với fluid tăng theo κ: 61% (κ ≤ 0,05) → 75% → 95% → 100% (κ ∈ (1; 5]).
Khi burst lớn so với nhiễu Poisson, CTMC giống fluid; ở κ nhỏ, backlog Poisson chiếm chỗ và các stake tương đối nhỏ
hẳn đi. Tập bridge trong CTMC gần như toàn horizon ngắn (h/T_int trung vị 0,01).

## 3. Horizon dài ([PREDICTIONS_asymptote.md](PREDICTIONS_asymptote.md), [score](score_asymptote.json))

33 regime × 7 horizon. Ba dự đoán toán (AS-T1–T3) đều đạt. Dự đoán rủi ro:

| ID | Dự đoán | Kết quả | |
|---|---|---|---|
| AS-R1a | h/T_int ≥ 3: \|z − z_bậc_một\| ≤ 0,1 pp ở ≥ 90% | 91,9% | ✅ |
| AS-R1b | 1 ≤ h/T_int < 3: sai số ≤ 0,1 + 0,1\|z\| ở ≥ 70% | 43,2% | ❌ |
| AS-R2a | predictor dừng (kiểu H-L2) trong 15% ở ≥ 90% | 83,3% | ❌ |
| AS-R2b | predictor dừng dự đoán cao hơn truth ở ≥ 80% | 100% | ✅ |
| AS-R3 | hybrid xóa harm (G_S^hyb ≥ −0,1%) ở ≥ 90% | 193/193 | ✅ |
| AS-R4 | h/T_int là đồng hồ tốt hơn h/κ (Spearman) | −0,92 so với −0,74 | ✅ |
| AS-R5a | h ≥ 3·T_int: Static thắng M0 tươi ở ≥ 90% regime | 90,9% | ✅ sát ngưỡng |
| AS-R5b | h = T_int/3: M0 tươi thắng Static ở ≥ 50% regime | 72,7% | ✅ |

**Hội tụ z → z_∞** (trung vị trên 231 dòng):

| h/T_int | \|z − z_∞\| (pp) | \|z − z bậc một\| (pp) | M / M_pred | regret Static (%) | regret M0 tươi (%) |
|---|---|---|---|---|---|
| ≈ 1/3 | 2,53 | 6,32 | 0,02 | 0,99 | 0,24 |
| ≈ 1 | 2,49 | 1,78 | 0,17 | 0,23 | 1,42 |
| ≈ 3 | 1,30 | 0,11 | 0,54 | 0,007 | 4,24 |
| ≈ 10 | 0,46 | 0,001 | 0,82 | 0 | 5,42 |
| ≈ 30 | 0,11 | 0,000 | 0,95 | 0 | 6,47 |

## 4. Khám phá rộng Stage E ([analysis_wide.json](analysis_wide.json), discovery, không chấm)

2.036 regime Sobol, κ ∈ [0,02; 5], h/T_int log-đều trong [0,03; 30]. 12 case bị loại vì CPU ước lượng > 900 s
(tải gần 10, κ gần 5). κ tối đa thu hẹp từ 20 xuống 5 vì N ≥ 26.000 và T_int ≥ 3.000 s ở góc đó.

- **Hai đồng hồ cho hai câu hỏi.** "State hay model thắng" (S > M) gom tốt nhất theo P = (h/κ)·|δ|: 95,4%, P* ≈ 14,
  gần P* ≈ 12 của fluid. Tiếp theo: h·|s|/r_min 93,1%, h/κ 92,8%, h/T_int 87,9% (tỷ lệ nền 86,2%). Còn "z đã tới z_∞
  chưa" gom theo h/T_int (AS-R4).
- **Lớp ở h ≥ 3·T_int:** x < 0 và x > 0,5 → G_S < −0,1% ở 95–100%; dải giúp còn khoảng (0; 0,25); 0,25 < x ≤ 0,5 phần
  lớn bị hại (73–90%); x = 0 không bao giờ bị hại.
- **Bản đồ twin** (regret % C_ref, trung vị):

| h/T_int | x < 0 hoặc x > 0,5 | 0 < x ≤ 0,5 | x = 0 |
|---|---|---|---|
| < 0,3 | M0 tươi / margin tốt nhất; Static đủ ở 64–94% | state cần: Static thua (regret 3,4–10,7) | M0 tươi tối ưu |
| 0,3–3 | M1 với state cũ tốt nhất; Static đủ ở 78–99% | **vùng cần M1**: mọi twin khác > 0,5% ở tới 39% regime | M0 tươi tối ưu, Static 11–17% |
| ≥ 3 | Static ≈ tối ưu (100%); M0 tươi 5–14% | Static ≈ tối ưu ở 71–100% | Static 1,5–5%; M0 tươi 0 |

- **Hybrid** (M0 + h·s): G_S^hyb trung vị 0,0 và ≥ −0,1% ở 100% của hơn 900 dòng có G_S < −0,5%, ở mọi mức h/T_int.
- **Dấu z so với z_∞** (\|z_∞\| ≥ 0,5): trùng 44% (h/T_int < 0,1) → 58% → 83% → 96% → 100% (≥ 3).

## 5. Stage F: switching cost c_sw > 0 ([PREDICTIONS_csw.md](PREDICTIONS_csw.md), [score](score_csw.json))

Bản CTMC của nhánh D(ii) Phase 6. Thiết kế (chỉ M0, trước truth): khi c tăng, tỷ lệ Switch của M0 trên state cũ và
trên state mới cùng giảm và tiến sát nhau, nên z_∞(c*) chỉ còn −0,089 đến +0,205. Khóa ở `8f31097e`.

| ID | Dự đoán | Kết quả | |
|---|---|---|---|
| F-T1 | z → z_∞(c) ở h ≈ 30·T_int | 12/12 | toán |
| F-R1 | bậc một chính xác ≤ 0,1 pp từ h/T_int ≥ 3 ở ≥ 90% | 97,5% | ✅ |
| F-R2 | không có harm: G_S ≥ −0,25% ở ≥ 90% dòng c* | 100%, nhỏ nhất −0,042% | ✅ |
| F-R3 | h < 3·T_int: state tươi vẫn giúp (G_S > 0) ở ≥ 70% | 90,9% | ✅ |
| F-R4 | G_S(c*) < G_S(0) từ h/T_int ≥ 3 | 100% | toán + onset |
| F-R5 | hybrid khi có harm | không có dòng harm | INCONCLUSIVE |

## 6. Tổng số và cách đọc

**Dự đoán rủi ro: 15 đạt, 6 trượt, 1 INCONCLUSIVE** (bridge 6/10, asymptote 6/8, Stage F 3/3 + 1 INC). Mọi dự đoán
nhãn toán đều đạt; theo lesson, chúng chỉ chứng tỏ code và lý thuyết chain-hữu-hạn nhất quán.

Đọc theo bảng kết cục của lesson (mục 12):
- **Lớp ở P lớn khớp một phần, P vẫn là biến gom tốt nhất, nhưng ngưỡng dịch theo đồng hồ** (BR-R3: P* = 36 trên
  tập ngắn; Stage E: P* ≈ 14). Cấu trúc định tính không phải artifact của fluid; các ngưỡng định lượng phụ thuộc
  representation. BR-R4b/c trượt vì dải giúp trong CTMC hẹp hơn (đã dự đoán ở BR-R5) và lớp "thay thế" (Γ < 0) hiếm hơn.
- **Can thiệp hybrid xóa harm** ở mọi dòng có harm (AS-R3, Stage E): trong model này, mù horizon là nguyên nhân của
  harm từ state tươi với M0. Đây là bằng chứng nhân quả trong model, không phải ngoài đời.
- **z → z_∞ đúng lúc dự đoán**: khai triển bậc một zero-fit chính xác ≤ 0,1 pp từ h ≈ 3·T_int (AS-R1a, F-R1), sai ở
  h ≈ T_int (AS-R1b). Đồng hồ của tiệm cận là T_int, không phải κ.
- **Phase 6 nhìn từ CTMC:** ở h/κ = 80–160, nhiều regime CTMC vẫn có h < 3·T_int, tức tiền tiệm cận; và cơ chế D(ii)
  (switching cost làm state tươi gây hại) không xuất hiện trong CTMC (F-R2). CTMC không chứng minh gì cho plant fluid;
  nó chỉ cho thấy dấu của nhánh D phụ thuộc representation (posterior hẹp của fluid so với posterior rộng của Poisson).
- **Predictor dừng (kiểu H-L2) luôn dự đoán cao hơn truth** (100%, cùng chiều fluid 10/10) và chỉ đạt 82–95% ở
  h = 10–30·T_int.

## 7. Được claim / chưa được claim

**Được** (sau khi control đạt, có số dự đoán khóa trước đạt/trượt): kết quả trong hai representation Markov ở
a/μ = 0,6, plant hai path, S1 gồm mode oracle, P1 stationary. Phần còn lại ghi là "exploration, AI theo ủy quyền".

**Chưa được:** mạng thật; biên độ khác (held-out cho L7.2); traffic không-Markov; "telemetry khả thi gây hại" (D22
chưa làm); novelty; nâng G-level (vẫn G1, fragile; tác giả chưa tự dẫn lại; chưa có realism).

## 8. Hạn chế

- Một mức số (N theo luật đuôi 1e−13, tolerance mặc định của expm_multiply); V5 chỉ kiểm 4 góc nặng nhất.
- Mật độ điểm theo thiết kế Sobol, không theo tần suất ngoài đời.
- Exposure trước khóa: 3 timing probe (T1–T3) in truth, bị loại khỏi chấm; số của bridge viết sau khi thấy M0-only và
  dữ liệu fluid (được phép); Stage F viết sau khi đọc D và E; ba base của F có truth c = 0 ở h/κ = 50/150 trong xslice.
- D22 (state mới chỉ có backlog) chưa làm; S1 vẫn gồm mode oracle.
- Lesson ghi gcp1 + gcp2; chỉ có một VM GCP. "Prompt gốc" của lesson không có trong repo; làm theo phụ lục L7.1.

## 9. Chi phí

Khoảng 19,2 CPU-giờ đo trong các file kết quả: Stage E 16,1; asym 1,4; bridge/xslice/pslice 0,5; Stage F 0,03;
M0-only 0,7; control 0,4. Thêm V5 (ước lượng 2–3 CPU-giờ, không ghi vào file) và một ít case tính trùng khi chia việc
giữa hai máy. Toàn bộ khoảng 22 CPU-giờ trên ngân sách 200. Hai máy: local 10 lõi, GCP 8 vCPU.

## 10. Việc tiếp theo (không tự làm)

- **L7.2 (tác giả):** viết thẻ giả thuyết cho biên độ a/μ ≠ 0,6 và mở held-out một lần. Có hai dự đoán đối nghịch cần
  chọn: SUMMARY fluid §5.6 đoán x* gần như không đổi theo a; review đoán x* dịch theo a.
- **D22** nếu muốn trả lời "harm có phải chỉ vì S1 biết mode".
- Tác giả tự dẫn lại z_∞ và khai triển bậc một (mục 16 lesson).
