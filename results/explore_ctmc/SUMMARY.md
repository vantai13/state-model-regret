# L7.1 — CTMC MMPP/M/1 (ctmc-v1): tổng kết

Doan Van Tai — **AI (Claude) thiết kế, chạy và soạn theo ủy quyền** ("thực hiện theo hướng dẫn và bạn tự chạy đi",
03/11/2026). Exploration trên nhánh `explore/ctmc-phase7`, worktree `/home/vantai/smr-ctmc`. Không phải author-self,
không phải confirmation của contract v1.3, không phải claim novelty. Tác giả không ghi dự đoán riêng (mục 9 lesson);
mọi dự đoán là của AI. Plant khác contract (packet-level, μ = 10, a = 6, τ = 1), giữ P1, S0/S1, D19.

> **Đính chính sau review của mentor (03/11/2026, tối).** Bốn câu dưới đây đã viết quá; số chấm và verdict giữ nguyên,
> chỉ đổi cách đọc. Kiểm lại bằng dữ liệu thô đã lưu, không chạy lại gì.
> 1. **AS-R3 (hybrid xóa harm) đổi nhãn thành "gần như toán", không phải bằng chứng nhân quả.** Trên 193 dòng chấm,
>    hybrid khác Static ở trung vị 0% số state (lớn nhất 1,8%), M0 khác Static ở 37% (q90 49%), truth ở 0,03%.
>    Hybrid xóa harm vì nó thôi nhìn state; luật nào không nhìn state cũng vậy. Cách đọc đúng: *ở vùng telemetry tươi
>    gây hại, quyết định đúng gần như không phụ thuộc state; twin mù horizon tự tạo ra phụ thuộc state.* Phép kiểm nhân
>    quả không tầm thường là knockout KO (L7.2 Phần 1A, [PREDICTIONS_ko.md](PREDICTIONS_ko.md)).
> 2. **Onset của khai triển bậc một phải đọc theo từng khoảng:** trong 0,1 pp ở 10% dòng khi h/T_int ∈ (1; 2], 50% ở
>    (2; 4], 100% ở (4; 7], (7; 15], (15; 40]. Câu "từ 3·T_int" là kết quả gộp; đúng ra là "từ khoảng 4–7·T_int".
> 3. **D22: phần backlog giảm theo κ**, trung vị 0,885 (κ ≤ 0,05), 0,878, 0,769, 0,599 (κ ∈ (1; 5]); ở κ > 5 chỉ có 25
>    regime và không có dòng harm (zero-fit cho khoảng 0,32). D-R1 phần lớn đã được zero-fit báo trước (z_F,∞ < 0 ở cả
>    1.982 regime harm); phần rủi ro thật của D22 là D-R3 và D-R4.
> 4. **P là biến xếp thứ tự tốt nhất nhưng không phải biên sắc nét:** P* = 36 trên bridge (S > M ở 73%) và ≈ 14 ở
>    Stage E (S > M ở 14%) do thành phần mẫu; ở Stage E các biến cách nhau mỏng (P 95,4%, h·|s|/r_min 93,1%, h/κ 92,8%,
>    nền 86,2%), và không tách dòng đã nhìn / chưa nhìn.

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
| AS-R3 | hybrid xóa harm (G_S^hyb ≥ −0,1%) ở ≥ 90% | 193/193 | ✅ → **gần như toán** (đính chính 1) |
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
  Theo đính chính 1, đây là hệ quả của việc hybrid ≈ Static ở dòng harm, không phải bằng chứng nhân quả.
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

## 5b. D22: state mới chỉ có backlog, không có mode ([PREDICTIONS_d22.md](PREDICTIONS_d22.md), [score](score_d22.json))

Làm sau L7.1 theo yêu cầu "thực hiện D22 luôn đi". Định nghĩa theo contract D22: a_cb0(Y, Q) dùng M0 cố định,
a_cb1(Y, Q) dùng model đúng, Q = hai backlog hiện tại, mode suy từ (Y, Q). Tách G_S = F + V (F: giá trị backlog,
V: phần do mode oracle) và S = F1 + V1. Phạm vi: 2.767 tuple đã chạy có N ≤ 3.000 mỗi path (bridge 821, xslice 86,
pslice 78, asym 29, wide 1.753). G_S, S của các tuple này đã thấy; phần mới là phép tách. Control V3-D22 (Monte Carlo
đầu-cuối) đạt, |z| ≤ 2,72; V7-D22 giống từng bit giữa hai máy. Khóa ở `b2523097`.

| ID | Dự đoán | Kết quả | |
|---|---|---|---|
| D-T1 | F + V = G_S, F1 + V1 = S; F1, V1 ≥ 0 | đúng trên 2.941 dòng, sai số ≤ 4e−14 | toán |
| D-T2 | F, V tới giá trị zero-fit từ h/T_int ≥ 10 | 94,2% | toán + onset |
| D-R1 | dòng harm: F < −0,1% ở ≥ 80% | **100% (n = 949)** | ✅ |
| D-R2 | tỷ lệ F/G_S khớp zero-fit ±0,1 từ h/T_int ≥ 3 | 99,8% | ✅ |
| D-R3 | horizon ngắn (h < T_int), dòng harm: F < 0 | 100% | ✅ |
| D-R4 | với model đúng, F1 ≥ V1 ở ≥ 70% dòng S ≥ 0,5% | 100% (n = 301) | ✅ |
| D-R5 | h ≥ 3·T_int: Static không thua M0 với (Y, Q) ở ≥ 90% | 86,6% | ❌ |

**Đọc:**
- **Harm không cần mode oracle.** Ở mọi dòng có G_S < −0,5%, state mới chỉ gồm backlog đã làm M0 tệ hơn; phần
  backlog chiếm 60–89% harm tùy κ (trung vị gộp 82%) và giảm khi burst dài ra; chưa có truth ở κ > 5 hay tải > 9,75
  (đính chính 3). Câu "harm chỉ vì S1 biết mode" bị bác trong ctmc-v1, trong miền đã chạy.
- **Với model đúng, mode gần như không thêm gì sau khi đã có backlog hiện tại + backlog cũ:** V1/S trung vị 2,8%,
  lớn nhất 26%.
- D-R5 trượt chủ yếu ở δ = 0 (85/98 dòng): s = 0 nên Static luôn Stay, còn M0 với backlog gần tối ưu. Bỏ δ = 0 thì đạt
  98%. Dự đoán viết không loại δ = 0 dù Stage E đã cho thấy Static dở ở x = 0; giải thích này là hậu nghiệm, verdict
  FAIL giữ nguyên.
- Giới hạn: N ≤ 3.000 loại các góc tải nặng/κ lớn (tại đó phần mode lớn nhất theo xu hướng zero-fit: tỷ lệ backlog
  0,32 ở κ > 5). Ô (y, n) khối lượng < 1e−20 bị bỏ, tổng ≤ 1e−12.

## 6. Tổng số và cách đọc

**Dự đoán rủi ro: 19 đạt, 7 trượt, 1 INCONCLUSIVE** (bridge 6/10, asymptote 6/8, Stage F 3/3 + 1 INC, D22 4/5). Mọi dự đoán
nhãn toán đều đạt; theo lesson, chúng chỉ chứng tỏ code và lý thuyết chain-hữu-hạn nhất quán.

Đọc theo bảng kết cục của lesson (mục 12):
- **Lớp ở P lớn khớp một phần, P vẫn là biến gom tốt nhất, nhưng ngưỡng dịch theo đồng hồ** (BR-R3: P* = 36 trên
  tập ngắn; Stage E: P* ≈ 14). Cấu trúc định tính không phải artifact của fluid; các ngưỡng định lượng phụ thuộc
  representation. BR-R4b/c trượt vì dải giúp trong CTMC hẹp hơn (đã dự đoán ở BR-R5) và lớp "thay thế" (Γ < 0) hiếm hơn.
- ~~Can thiệp hybrid xóa harm ... bằng chứng nhân quả~~ (rút lại, đính chính 1). Đọc đúng: ở vùng harm, quyết định
  tối ưu gần như không phụ thuộc state, còn M0 phản ứng với state ở khoảng một phần ba số state và mỗi lần trả khoảng
  h·|s|. Phép kiểm nhân quả là KO (L7.2 Phần 1A).
- **z → z_∞**: khai triển bậc một zero-fit chính xác ≤ 0,1 pp từ khoảng 4–7·T_int (theo khoảng: 50% ở (2; 4],
  100% từ (4; 7]; đính chính 2), sai ở h ≈ T_int (AS-R1b). Đồng hồ của tiệm cận là T_int, không phải κ.
- **Phase 6 nhìn từ CTMC:** ở h/κ = 80–160, nhiều regime CTMC vẫn có h < 3·T_int, tức tiền tiệm cận; và cơ chế D(ii)
  (switching cost làm state tươi gây hại) không xuất hiện trong CTMC (F-R2). CTMC không chứng minh gì cho plant fluid;
  nó chỉ cho thấy dấu của nhánh D phụ thuộc representation (posterior hẹp của fluid so với posterior rộng của Poisson).
- **Predictor dừng (kiểu H-L2) luôn dự đoán cao hơn truth** (100%, cùng chiều fluid 10/10) và chỉ đạt 82–95% ở
  h = 10–30·T_int.

## 7. Được claim / chưa được claim

**Được** (sau khi control đạt, có số dự đoán khóa trước đạt/trượt): kết quả trong hai representation Markov ở
a/μ = 0,6, plant hai path, S1 gồm mode oracle, P1 stationary. Phần còn lại ghi là "exploration, AI theo ủy quyền".

**Chưa được:** mạng thật; biên độ khác (held-out cho L7.2); traffic không-Markov; "telemetry khả thi gây hại" ngoài
ctmc-v1 (D22 chỉ trong model, N ≤ 3.000); novelty; nâng G-level (vẫn G1, fragile; tác giả chưa tự dẫn lại; chưa có realism).

## 8. Hạn chế

- Một mức số (N theo luật đuôi 1e−13, tolerance mặc định của expm_multiply); V5 chỉ kiểm 4 góc nặng nhất.
- Mật độ điểm theo thiết kế Sobol, không theo tần suất ngoài đời.
- Exposure trước khóa: 3 timing probe (T1–T3) in truth, bị loại khỏi chấm; số của bridge viết sau khi thấy M0-only và
  dữ liệu fluid (được phép); Stage F viết sau khi đọc D và E; ba base của F có truth c = 0 ở h/κ = 50/150 trong xslice.
- D22 chỉ trên N ≤ 3.000; các tuple của D22 đã có G_S/S từ Stage D/E (phần mới là phép tách).
- Lesson ghi gcp1 + gcp2; chỉ có một VM GCP. "Prompt gốc" của lesson không có trong repo; làm theo phụ lục L7.1.

## 9. Chi phí

Khoảng 19,2 CPU-giờ đo trong các file kết quả: Stage E 16,1; asym 1,4; bridge/xslice/pslice 0,5; Stage F 0,03;
M0-only 0,7; control 0,4. Thêm V5 (ước lượng 2–3 CPU-giờ, không ghi vào file) và một ít case tính trùng khi chia việc
giữa hai máy. L7.1 khoảng 22 CPU-giờ. D22 thêm 20,8 CPU-giờ (truth 9,1; M0-only 11,5 vì phải dựng luật đồng thời
(Y, X); control 0,3). Tổng khoảng 43 CPU-giờ trên ngân sách 200. Hai máy: local 10 lõi, GCP 8 vCPU (GCP tắt giữa chừng
rồi bật lại; firewall phải thêm IP mới vì mạng của tác giả đổi IP ra ngoài).

## 10. Việc tiếp theo (không tự làm)

- **L7.2 (tác giả):** viết thẻ giả thuyết cho biên độ a/μ ≠ 0,6 và mở held-out một lần. Có hai dự đoán đối nghịch cần
  chọn: SUMMARY fluid §5.6 đoán x* gần như không đổi theo a; review đoán x* dịch theo a.
- Tác giả tự dẫn lại z_∞ và khai triển bậc một (mục 16 lesson).

## 11. L7.2 Phần 1 (03/11/2026, tối; AI theo ủy quyền, exploration)

### A. Knockout KO ở a = 6 ([PREDICTIONS_ko.md](PREDICTIONS_ko.md), [score](score_ko.json))

KO = model đúng bỏ đúng phần dài hạn: gap_KO = Δ − h·s. Hoàn thiện bảng 2×2 bên trong trục model (phần ngắn hạn
{fluid, đúng} × phần dài hạn {không, có}). Khóa ở `86056ac2` trước truth của KO. Tập: 33 regime asym × 7 horizon
(G_S của M0 đã thấy) + 201 regime **mới** (`ko_slice`). Dự đoán rủi ro và onset: **9 đạt, 0 trượt**; KO-T1 (toán) đạt.

| | không có phần dài hạn | có h·s |
|---|---|---|
| ngắn hạn fluid | M0: G_S trung vị tới −3,9% ở dòng harm; phụ thuộc state 32% | Hybrid: ≈ 0; phụ thuộc state 0% (tầm thường) |
| ngắn hạn đúng | **KO: G_S ≈ 0 hoặc dương (trung vị +0,02…+0,37), vì sai đều (chọn đúng ~14% state); phụ thuộc state 90%** | M1: G_S = S ≥ 0; phụ thuộc state 0% |

- KO-R1: |G_S^KO| < ½|G_S^M0| ở 95,2% dòng harm (n = 252). KO-R2: G_S^KO ≥ −0,25% ở 99,3% dòng (nhỏ nhất −0,36%).
- KO-R5: KO khác Static ở ≥ 50% state ở 100% dòng h ≥ 4·T_int, nên phép knockout không tầm thường.
- Onset của KO theo khoảng: 89,6% ở (2; 4], 96,9% ở (4; 7], 100% ở (7; 15] và (15; 40].
- ~~Đọc: mù horizon một mình không tạo harm; harm là tương tác giữa mù horizon và xấp xỉ fluid~~ (**rút lại sau review
  mentor, 03/11 tối**). Số đúng, cách đọc sai. Trên dòng harm có h > 4·T_int (n = 138): KO chọn đúng action dài hạn chỉ
  ở 13% (state cũ) và 15% (state mới) số state, regret 31,6% / 31,5% C_ref, so với M0 là 0,83 / 0,67 và 3,4% / 6,5%.
  **KO sai đều với cả hai loại state**, nên state mới không còn chỗ để làm nó tệ thêm: G_S^KO ≈ 0 không chứng minh mù
  horizon vô hại. Bỏ h·s khỏi model đúng chỉ để lại chi phí chuyển tiếp sang chế độ mới, và chi phí đó gần như luôn
  nghiêng ngược với action dài hạn ở các dòng harm.
- **Điều KO thật sự cho thấy:** harm từ state tươi xảy ra khi twin, với state cũ, đang **đúng nhờ lấy trung bình**. Ở
  a = 6, h ≥ 4·T_int, δ ≠ 0: dòng harm (G_S < −0,1; n = 543) có M0 chọn đúng action dài hạn ở 0,90 (cũ) so với 0,73
  (mới), trung vị; dòng help (G_S > 0,1; n = 63) ở 0,24 so với 0,34. Giả thuyết cơ chế (của mentor, chưa kiểm):
  trung bình gap drain của M0 trên posterior gần dừng tăng theo tải, nên M0 với state cũ hành xử như một **planner dừng
  ngầm**; state tươi thay backlog điển hình bằng backlog thực tế và M0 chuyển sang phản ứng theo dao động. KO không có
  planner ngầm vì gap của nó đo so với mức dừng của từng action.
- **Nhãn:** KO-R1 và KO-R2 được viết sau khi thấy z_∞^KO nhỏ, nên chủ yếu là toán/onset; verdict giữ nguyên, không
  dùng chúng làm bằng chứng cơ chế. Tỷ lệ regret KO/M0 tươi trên dòng harm (h > 4·T_int): q10 1,71, trung vị 2,6, q90 7,2.

### B. Số zero-fit ở biên độ held-out ([l72/](l72/), không có cột truth)

Code chỉ cho a ∈ {3; 15/2} ở chế độ zero-fit; V, mọi L/G và quyết định truth ở h hữu hạn bị từ chối (PermissionError)
cho tới khi có `locks_l72.json` chứa hash thẻ của tác giả. Đã kiểm: 0 file truth có a ≠ 6.

| | a = 3 (a/μ = 0,3) | a = 6 (đã chạy) | a = 7,5 (a/μ = 0,75; λ ≥ 7,5) |
|---|---|---|---|
| T_int (q10/q50/q90, s) | 6,8 / 41 / 383 | 9,1 / 38 / 369 (asym) | 29 / 339 / 1.718 |
| N lớn nhất (q50/q90/max) | 614 / 1.842 / 4.511 | | 1.787 / 8.518 / 21.052 |
| z_∞ < −0,5 / z_∞ > 0,5 (Sobol) | 74% / 8,7% | | 58% / 0,2% |
| phần backlog z_F,∞/z_∞ (q10/q50/q90, harm) | 0,54 / 0,83 / 0,96 | 0,57 / 0,82 / 0,95 | 0,75 / 0,90 / 0,97 |
| z_∞^KO/z_∞ (trung vị, harm) | −0,018 | −0,025 | −0,007 |
| x* (biên trên dải giúp, theo họ (u, λA, κ)) | 0,19–0,29 | 0,15–0,24 (cùng họ với a = 3) | 0,12–0,16 (họ khác) |
| CPU ước lượng cho truth: asym / Sobol | 0,17 / 0,86 CPU-h | | 1,2 / 20,9 CPU-h (0,53 / 6,6 nếu trần 900 s/case; 1 và 16 case vượt) |

- **x* có dịch theo a, nhưng ít:** cùng họ (u, λA, κ), a = 3 cho x* lớn hơn a = 6 khoảng 0,01–0,05. Không ủng hộ hẳn
  "x* không đổi theo a" (SUMMARY fluid §5.6) lẫn "x* dịch mạnh".
- a = 7,5 gần như không có vùng state giúp (0,2%); dải giúp hẹp (x* ≈ 0,12–0,16). Truth ở a = 7,5 đắt ở tải gần 10;
  đề xuất trần 900 CPU-s/case hoặc load_max ≤ 9,5 nếu tác giả chọn mở biên độ này.
- Dừng sau B theo prompt; không chạy truth ở a ≠ 6. Thẻ L7.2 Phần 2 do tác giả viết.
- Chi phí L7.2 Phần 1: truth KO 2.5 CPU-giờ, zero-fit held-out 3.6, zero-fit KO 0.02; tổng khoảng 6.1 CPU-giờ (cộng dồn toàn nhánh khoảng 49 CPU-giờ trên 200).

## 12. L7.2 Phần 2: mở held-out a = 3 và a = 7,5 theo thẻ đã khóa ([score_l72.json](score_l72.json))

**Đây là test theo thẻ do AI soạn theo ủy quyền tác giả** ([CARD_L7_2.md](l72/CARD_L7_2.md)), không phải thẻ tác giả tự
viết. Tác giả nói "khóa" sau khi đọc thẻ và trước khi có `check_l72.py`; mentor chưa review thẻ. G-level vẫn G1. Khóa ở
`58312baf` ([locks_l72.json](locks_l72.json)), trước mọi truth ở a ≠ 6. Chấm bằng `check_l72.py` nguyên văn; không đổi ngưỡng.

**Cách chạy:** mỗi case list một lần, trần 900 CPU-s/case, trên local và GCP. Lần chạy đầu bị treo khoảng 50 phút trên
cả hai máy, vì `multiprocessing.Pool` mất task của worker bị kernel giết ở hard limit (900 + 60 CPU-s). Runner được
sửa (`run_robust`, commit `8d7e842f`): mỗi case một process, parent tự ghi UNRESOLVED khi worker chết. 17 case lát x
a = 7,5 bị kernel giết (dmesg 17 lần, 0 OOM) được ghi UNRESOLVED, không chạy lại. 20 case Sobol a = 7,5 bị mất trên GCP
(không có log kernel) được tính lại với **cùng** trần; 19 lại vượt trần. Không có case nào chạy lại với trần khác.

**UNRESOLVED:** a = 3: 2/909 case; a = 7,5: 45/827 case (asym 1, Sobol 25, lát x 19). CPU đo được 27,2 CPU-giờ, cộng
17 case bị giết không có số đo (mỗi case ≥ 900 CPU-s).

**Bit-identity giữa hai máy ở held-out:** 63 case Sobol a = 3 được cả hai máy tính độc lập; 59 không trùng từng bit.
Lệch ở mức làm tròn (L, Cref, regret: tương đối ≤ 1e−15); lệch lớn nhất là tỷ lệ Switch backlog-only của M0 (`share_cb0`,
tới 0,06 khối lượng) do quyết định gần hòa bị lật, ảnh hưởng F ≤ 5,2e−5 pp. Chấm lại với phiên bản GCP của cả 63 case
cho **verdict y hệt**. Trên cùng một máy kết quả tất định (3 lần chạy trùng hash). Control V7 trước đây chỉ phủ chain nhỏ
(N ≤ 680); ở N lớn hai máy lệch ở bit cuối dù đã ghim môi trường. Ghi nhận, không sửa sau khi đã có truth.

| ID | Claim | a = 3 | a = 7,5 |
|---|---|---|---|
| L72-1 onset | C-A | **PASS**: (4; 7] 94,4% (n 54), (7; 15] 100% (n 111), (15; 40] 100% (n 101); (2; 4] 38% (chỉ báo) | **INCONCLUSIVE**: (4; 7] 97,9%, (7; 15] 100% đạt; (15; 40] có 17% case UNRESOLVED (> 10%) |
| L72-2 biên dải | C-B | **FAIL**: 3/6 chuỗi trong ±0,05 | **FAIL**: 4/6 chuỗi (cần ≥ 5/6) |
| L72-3 planner dừng | C-C | **PASS** 95,3% (n 213) | **PASS** 100% (n 139) |
| L72-4 dải co (hai biên độ) | C-C | p_3 = 0,093 | p_7,5 = 0,0375 → **PASS** (chênh 0,055 ≥ 0,05, sát ngưỡng) |
| L72-5 D22 h ngắn | C-D | **PASS** 98,9% (n 91) | **PASS** 100% (n 35) |
| L72-6 D22 tỷ lệ zero-fit | C-D | **PASS** 100% (n 169) | **PASS** 100% (n 84) |
| L72-7 KO tệ hơn M0 | C-E | **PASS** 99,5% (n 214) | **INCONCLUSIVE** (11,8% case UNRESOLVED) |
| L72-8 hai đồng hồ | C-E | **PASS**: P 93,2% vs đa số 81,8%, h/T_int 86,0%; Spearman −0,886 vs −0,640 | **FAIL** ở (a): P 96,5% vs đa số 95,5% (cần ≥ 100,5%); (b) đạt: −0,959 vs −0,812 |
| L72-Z (zero-fit, không tính) | C-E | đạt: 0,92 / 0,73 | đạt: 0,80 / 0,71 |

**Đếm:** a = 3: 6 PASS, 1 FAIL. a = 7,5: 3 PASS, 2 FAIL, 2 INCONCLUSIVE. Liên biên độ: L72-4 PASS. Không gộp thành một
kết luận chung.

**Đọc theo mục 7 của thẻ (không đổi ngưỡng):**
- **C-A** đứng ở a = 3 như viết; ở a = 7,5 hai khoảng đầu đạt, khoảng dài nhất không chấm được (case vượt trần). Câu
  claim co về "từ khoảng 4·T_int, ở các case tính được".
- **C-B** trượt ở cả hai biên độ: biên dải giúp **không** tính trước được tới ±0,05 ở h = 10·T_int. Chỉ giữ "dải hẹp"
  định tính.
- **C-C** đứng: planner dừng ≤ 0,1% regret ở ≥ 95% dòng h > 7·T_int cả hai biên độ; dải giúp ở horizon vừa co từ 9,3% xuống
  3,75% khi burst mạnh (sát ngưỡng).
- **C-D** đứng ở cả hai biên độ trong phạm vi N ≤ 3.000: harm đã có khi state mới chỉ gồm backlog, tỷ lệ backlog khớp
  zero-fit.
- **C-E:** KO tệ hơn M0 ≥ 1,5 lần ở 99,5% dòng harm (a = 3), không chấm được ở a = 7,5. "Hai đồng hồ" đứng ở a = 3; ở
  a = 7,5 phần P trượt, phần h/T_int đạt.

**Khám phá sau khi mở (không phải test):**
- L72-2: các chuỗi trượt đều có biên truth **rộng hơn** zero-fit (a = 3: 0,32–0,37 so với 0,19–0,24 ở u = 1/2 và
  u = 1, κ = 1; a = 7,5: 0,23–0,24 so với 0,14–0,16 ở u = 1/2). Các chuỗi u lớn khớp tới 0,005. Gợi ý: ở h = 10·T_int,
  phần hiệu chỉnh B/h còn đẩy biên ra ngoài khi u nhỏ; chưa kiểm.
- L72-8(a) ở a = 7,5: lớp đa số đã là 95,5%, nên điều kiện "đa số + 0,05" gần như không thể đạt. Đây là lỗi thiết kế
  ngưỡng của thẻ do AI soạn; verdict FAIL giữ nguyên.
