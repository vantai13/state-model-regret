# EV-TE — Prop 1 nhiều action trên hai topology WAN thật (Abilene, GÉANT) (16/11/2026)

Doan Van Tai — **AI theo ủy quyền**:
- Claude thiết kế, viết thẻ, khóa, chấm và viết báo cáo này; Codex viết code và chấm lại độc lập.
- Tác giả duyệt thiết kế ("oke", 15/11) và giao chạy ("bạn tự chạy kiểm tra tất cả").
- Không có mentor review và không có kỳ vọng nào của tác giả được ghi trước khi chạy.
- Nhánh `ext/validity`, không merge vào main.
- Thẻ giả thuyết: [CARD.md](CARD.md). Thiết kế: [DESIGN.md](DESIGN.md).

## Trình tự

| Bước | Commit | Ghi chú |
|---|---|---|
| Code (Codex, 73 test), train seed A, 732 dự đoán, thẻ, khóa 70 file và dấu vân tay dữ liệu | `56dbc52b` | Chưa có giá trị nào của seed truth B |
| Arm R v2: sửa parser, chạy mô tả, ngoài khóa | `14a4d79e` | Theo D2 của thẻ |
| Một lần chạy truth trên VM n2-standard-32 | — | 61/61 regime, 17:51–21:29 UTC 15/11 (3 giờ 38 phút), `PIPELINE_EXIT rc=0`, verify-lock PASS hai lần |
| Dữ liệu thô | `effcf40e` | 122 file, checksum khớp với VM; commit trước khi chấm |
| Điểm | `ae046daa` | Code chấm đã khóa (`ev_te.score`); có một sự cố ghi file, xem bên dưới |
| Codex chấm lại độc lập | (commit cùng báo cáo) | numpy/stdlib, không import `ev_te`: H1–H4 và mọi cờ eligible/pass **khớp**; sai khác lớn nhất ngoài Γ là 3,0×10⁻⁷ pp. Codex ghi "MISMATCH về dấu Γ": nó dùng $\Gamma=L_{00}-L_{10}-L_{01}+L_{11}$, ngược dấu với paper (§II, $\Gamma=L_{10}+L_{01}-L_{00}-L_{11}$, cũng là quy ước của code đã khóa); đảo dấu thì phần dư 1,2×10⁻¹⁰. Thẻ không định nghĩa Γ; Γ chỉ là số mô tả. [rescore_independent.md](rescore_independent.md) |
| Mô tả post-hoc | `ev_te_describe.py` | Không tạo verdict; [descriptive.json](descriptive.json) |

**Sự cố khi chấm (lệch protocol, chỉ ở bước ghi file).**
- Lần 1, `ev_te.score` đã khóa chạy verify-lock PASS, tính hết các số và ghi đủ `score_cells.csv`.
- Sau đó nó lỗi khi ghi `score.json`: `TypeError: Object of type int64 is not JSON serializable`, vì số ô PASS là tổng của các `numpy.bool_`.
- Lần 2 dùng `ev_te_score_post.py`, làm theo tiền lệ L7.5 `score_l75_post.py`:
  - kiểm sha256 của `ev_te.py` đã khóa;
  - chỉ thay `write_json` bằng bản đổi số vô hướng numpy sang giá trị Python bằng nhau;
  - rồi gọi đúng `ev_te.score()`.
- `score_cells.csv` lần 2 trùng từng byte với lần 1. Phần JSON lần 1 ghi được là tiền tố đúng của `score.json` lần 2. Lần 1 được giữ nguyên trong [score_attempt01_failed/](score_attempt01_failed/).
- Không chạy lại truth.

## Thiết kế (tóm tắt)

**Topology** (SNDlib):
- Abilene: dung lượng thật.
- GÉANT: SNDlib không có dung lượng lắp đặt, nên mọi link đặt 10 000 Mb/s.

**Mô hình.**
- Hàng đợi fluid trên từng link; chi phí $\sum_e\int Q_e\,dt$.
- Mỗi OD có tải điều biến hai trạng thái $d(1\pm\beta)$.
- Stay là đường min-hop; Switch là đường thứ hai (Yen $k=2$).
- Bốn tập OD được điều khiển tại link nghẽn.
- $\rho\in\{0{,}8;0{,}9\}$, $\beta\in\{0{,}3;0{,}6\}$, nhanh/chậm.
- 64 regime. Loại 3 theo E0; 12 regime GÉANT là D1 (có action không ổn định), chỉ báo mô tả. Còn **49 regime × 4 τ = 196 ô** để kiểm.

**Thông tin.** Stale và fresh chỉ khác **tuổi** của trạng thái đầy đủ: τ so với 0.

**Lưới.** $\tau/T_{int}\in\{0{,}1;0{,}3;1;3\}$, $h/T_{int}\in\{1,2,4,7,15,30\}$.

**Chạy.** N=500 instance mỗi regime, K=128, R_dec=128, R_eval=256, random số chung.
- CPU worker 113 997,5 s; dự toán 1,9×10⁵.
- Regime dài nhất G2_r90_b6_s1: 12 521 s.
- RSS đỉnh 115 MiB mỗi worker.

## Kết quả theo thẻ

| ID | Kết quả | Verdict | Dự báo của Claude trước khi chạy |
|---|---|---|---|
| H1: dấu $z_{M0}$ = dấu dự đoán, ≥ 90% | 195/196 = 99,5% | **PASS** | không chắc |
| H2: dấu phần tăng $\Delta$ (7→30 $T_{int}$), ≥ 90% | 192/192 = 100% | **PASS** | không chắc |
| H3: độ lớn $\Delta$ trong 25% (hoặc 0,25 pp, 2 se), ≥ 80% | 183/192 = 95,3% | **PASS** | khó nhất |
| H4: plug-in, $\lvert\Delta^P\rvert\le\max(0{,}25;\,2\,\text{se})$, ≥ 90% | 191/196 = 97,4% | **PASS** (kiểm định yếu, xem dưới) | nên PASS |

**Theo regime** (một regime PASS khi mọi τ đủ điều kiện đều PASS):
- H1: 48/49.
- H2: 48/48.
- H3: 45/48.
- H4: 45/49.

Các ô không độc lập. Bốn τ của một regime dùng chung instance. Nhiều ô τ = 1 và τ = 3 cho giá trị trùng nhau, vì khi đó quyết định với thông tin cũ không đổi theo τ.

## Đọc kết quả

### Đơn vị và độ lớn hiệu ứng

$z$ tính theo % của $C_{ref}=L(\text{M1\_new})$.
- **Ở Abilene, $C_{ref}$ rất nhỏ:** chỉ 0,02–67% của $E_{stay}$, trung vị 0,3%, vì Switch xóa gần hết hàng đợi dài hạn ($r_{Switch}=0$). Vì vậy $z$ ở Abilene có cỡ −20% đến −285 000% của $C_{ref}$, và các ngưỡng 0,25 pp rất dễ vượt.
- Quy về % của $E_{stay}$, tại $h=30T_{int}$, ô hợp lệ, hiệu ứng là:

| | $G_S^{M0}$ (% $E_{stay}$) | $G_S^{P}$ (% $E_{stay}$) | $C_{ref}/E_{stay}$ |
|---|---|---|---|
| Abilene (128 ô) | trung vị −46,9%; khoảng −77,0 … −11,4% | trung vị +0,9%; −6,4 … +7,1% | trung vị 0,003 |
| GÉANT (68 ô) | trung vị −18,5%; q25 −35,5%, q75 +19,5% | trung vị +0,7%; q25 −0,3%, q75 +1,9% | trung vị 1,00 |

$G_S<0$ nghĩa là telemetry tươi làm chi phí tăng.
- **Abilene:** với twin M0 trong mô hình này, telemetry tươi làm chi phí tăng ở cả 128/128 ô, 11–77% $E_{stay}$.
- **GÉANT:** có cả hai dấu.

### H1 và H2: dấu

- Ở Abilene, độ dốc dự đoán âm ở cả 32 regime (vì $r_{Switch}=0$), và 128/128 ô cùng dấu âm. Vì vậy **sự đa dạng dấu chỉ đến từ GÉANT**: 67/68 ô PASS (32 ô +/+, 35 ô −/−).
- **Ô H1 duy nhất không PASS** là G1_r80_b3_s1, τ = 0,1: $z=+1155\%\pm1186\%$ ($\lvert z\rvert$/se = 0,97), tức là nhiễu.
- Điều kiện đủ để kiểm H1 không đòi ý nghĩa thống kê: 4/196 ô đủ điều kiện có $\lvert z\rvert$/se < 2.
- **H2:** 4 ô không đủ điều kiện, cả 4 ở G1_r80_b3_s1, vì $\lvert\Delta_{meas}\rvert<2$ se.

### H3: độ lớn

- Tỷ số $z/\text{pred}$ (196 ô): trung vị 0,966, q25 0,906, q75 1,021.
- Sai số tương đối $\lvert\Delta_{meas}-\Delta_{pred}\rvert/\lvert\Delta_{pred}\rvert$: trung vị 6,2%, q75 9,5%, max 36,6%.
- Vế ràng buộc của dung sai là $0{,}25\lvert\Delta_{pred}\rvert$ ở 183/192 ô và 2 se ở 9 ô. Như vậy H3 phần lớn được kiểm bằng sai số 25%, không phải nhờ độ rộng nhiễu.
- **9 ô không PASS, đều ở GÉANT:**
  - G2_r90_b6_s0: cả 4 τ;
  - G3_r90_b6_s0: cả 4 τ;
  - G3_r80_b3_s1: τ = 0,3.
- Ở cả 9 ô, giá trị đo cùng dấu dương với dự đoán (telemetry tươi giúp) nhưng nhỏ hơn dự đoán 25–37%.

### H4: twin plug-in, PASS nhưng yếu

- **Ngưỡng $\max(0{,}25\text{ pp};\,2\,\text{se})$ chủ yếu được đạt nhờ vế 2 se.** Chỉ 26/196 ô có $\lvert\Delta^P\rvert\le0{,}25$ pp; 165 ô PASS chỉ nhờ vế 2 se.
- Quy về % $E_{stay}$:

  | | $\lvert\Delta^P\rvert$ trung vị | se trung vị |
  |---|---|---|
  | Abilene | 0,64% | 1,8% |
  | GÉANT | 0,49% | 1,3% |

- Vậy H4 PASS chỉ nói rằng, ở N = 500, phần tăng của plug-in từ 7 đến 30 $T_{int}$ chưa tách được khỏi 0. Nó **không** chứng minh một cận O(1) chặt tính theo pp của $C_{ref}$.
- **5 ô không PASS:**
  - A4_r80_b3_s1 τ = 0,3;
  - A1_r90_b3_s0 τ = 1;
  - A4_r90_b6_s1 τ = 0,3 và τ = 1;
  - G2_r80_b3_s1 τ = 1.

  Ở các ô này $\lvert\Delta^P\rvert$ khoảng 2–2,6 se.
- Tỷ lệ ô plug-in có $z<-0{,}1\%$ tăng theo h: 5/244 ở $h=T_{int}$ và 72/244 ở $30T_{int}$. Đây là số mô tả, tính theo % của một $C_{ref}$ rất nhỏ ở Abilene.

## Mô tả khác (không có verdict)

- **Tỷ lệ ô có $z<-0{,}1\%$, $h=T_{int}\to30T_{int}$, 244 ô:**
  - M0: 170 → 187;
  - CE: 148 → 160;
  - P: 5 → 72.
- **Chậm và nhanh ở GÉANT** ($z_{M0}$ tại $30T_{int}$):
  - slow = 0: trung vị +13,7% (telemetry tươi giúp);
  - slow = 1: trung vị −72,3% (telemetry tươi hại).
  - Ở GÉANT, phần lớn ô slow = 0 dương (q25 +6,5%) và phần lớn ô slow = 1 âm (q75 −45,8%); mỗi nhóm vẫn có ngoại lệ. Abilene âm ở cả hai.
- **$G_M$:** ở Abilene trung vị bằng 0, tức là với thông tin cũ, M0 và M1 chọn cùng action. Ở GÉANT trung vị 22,4% $C_{ref}$.
- **$\Gamma$** (quy ước của paper, $L_{10}+L_{01}-L_{00}-L_{11}$): ở Abilene trung vị +12 800% $C_{ref}$; ở GÉANT trung vị +40%.
- **CE twin:**
  - Ở Abilene gần như trùng M0.
  - Ở GÉANT trung vị $G_S^{CE}$ +21% $E_{stay}$, với vài ô cực lớn (tới 1,5×10⁵ % $E_{stay}$): CE với thông tin cũ chọn action có chi phí rất lớn ở một số regime.
- **12 regime D1** (action không ổn định), $z$ theo % $C_{ref}$:
  - M0: trung vị −27 đến −35%;
  - P: trung vị gần 0.
- **Arm R** (mô tả, ngoài khóa, [arm_r_v2/README.md](arm_r_v2/README.md)):
  - Trên ma trận traffic 5 phút thật của Abilene (2004), $T_{int}$ là 284 phút (ρ = 0,8) và 439 phút (ρ = 0,9).
  - Epoch TE 5–60 phút ứng với $h/T_{int}$ = 0,01–0,21.
  - $G_S$ cỡ $10^{-3}$% $E_{stay}$: plug-in hơi dương; nowcast âm ở h = 30–60 phút.

## Giới hạn

1. **Topology thật, tải tổng hợp.**
   - Tải là điều biến hai trạng thái, không phải traffic thật.
   - Dung lượng GÉANT đặt đều.
   - Chỉ có Stay và Switch (k = 2).
2. **Cấu trúc dấu ở Abilene.** Abilene đóng góp 128/196 ô, tất cả cùng một dấu do cấu trúc ($r_{Switch}=0$). Bằng chứng về dự đoán dấu khi dấu thay đổi là 68 ô GÉANT của 17 regime.
3. **Chuẩn hóa theo $C_{ref}$.** Ở Abilene, $C_{ref}$ nhỏ làm số pp phình to, nên ngưỡng 0,25 pp gần như không ràng buộc. H4 là kiểm định yếu.
4. **Ô không độc lập** (chung instance theo τ). Không có khoảng tin cậy cho tỷ lệ PASS.
5. **Chỉ ở chân trời dài.** Kiểm định ở $h=7$ và $30T_{int}$. Arm R cho thấy epoch TE thực tế trên Abilene nằm ở $h/T_{int}<1$: đó là vùng quá độ, nơi luật dài hạn không phải mô tả chính.
6. **AI theo ủy quyền.** Thiết kế, thẻ, khóa và chấm do Claude; code do Codex. Không có mentor review. Chấm lần 2 qua wrapper (xem Sự cố). Không có tác giả tự đọc hay tự kiểm.
7. **Không kết luận novelty.**

## Hệ quả

- **Phần luật đứng.** Trên hai topology WAN thật với tải điều biến tổng hợp, luật độ dốc nhiều action $\sum_a r_a[F_{old}(a)-F_{new}(a)]$ dự đoán đúng:
  - dấu của $G_S$ tại $30T_{int}$ ở 195/196 ô;
  - dấu phần tăng ở 192/192 ô;
  - độ lớn phần tăng trong 25% ở 183/192 ô.
- **Telemetry tươi có thể hại.** Với twin M0, telemetry tươi làm chi phí tăng ở 128/128 ô Abilene và 35/68 ô GÉANT đủ điều kiện H1; các ô GÉANT có dấu ngược lại (32/68) cũng được luật dự đoán đúng dấu.
- **Plug-in.** Kết quả cho twin plug-in khớp với Corollary 1, nhưng kiểm định có độ nhạy thấp.
- **Giới hạn thực tế.** Arm R cho thấy, với traffic thật của Abilene và epoch TE thông thường, hệ đang ở vùng $h\ll T_{int}$ và hiệu ứng rất nhỏ. Kết quả dài hạn ở đây là về mô hình trên topology thật, không phải về vận hành thật.
- **Paper chưa sửa.** Viết EV-TE vào paper chỉ khi tác giả yêu cầu.

**Không đổi:** MainRQ, contract, PC, Gate, G1, các verdict cũ.
