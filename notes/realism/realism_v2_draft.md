# Realism v2 — L7.3 Phần 1 (hoàn tất kỹ thuật, 04/11/2026)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền L7.3 Phần 1**, nhánh `explore/realism-l73` từ `explore/ctmc-phase7`.

Phạm vi và giới hạn:
- Không phải author-self. Không sửa [envelope v1](envelope_v1.json). Không chạy truth mới.
- Mọi tỷ số T_int/T_mode là đại lượng dừng của chain, không phải truth.
- Mọi nhãn vùng là **minh họa có điều kiện**, không phải calibration.

**Hoàn tất kỹ thuật** nghĩa là:
- mỗi ô của bảng use case đã có nguồn hoặc ghi UNSOURCED;
- mọi nguồn có được đã đọc AI-T kèm §/trang.

Nó **không** nghĩa là tác giả đã đọc, không nghĩa là có Gate, và không đóng Phần 2.

**Nguồn và cách duyệt qua các đợt** (chi tiết ở [search log L7.3-R1/R2](../literature/search_log.md)):

| Đợt | Ngày | Nguồn | Cách duyệt |
|---|---|---|---|
| 1 | 03/11 | Thư viện có sẵn: ZLK17, BAM10, NDT1, LTWW94, T00 | Mức đọc theo note gốc |
| 2 | 03/11 | SWAN, CONGA, Roy2015 | **AI-delegated** ("bạn hãy tự làm tự chạy thực hiện cho tôi luôn đi") |
| 3 | 04/11 | MicroTE, Roughan, Kuźniar'18, SWAN VoR; 4 paper NDT cũ của tác giả; đọc thêm BAM10 §6.4 và P07 | Tác giả tự tải hoặc yêu cầu đọc |
| 4 | 04/11 | Ghabashneh'22, Lakhina'04 (bị bỏ sót ở đợt 3, đã đính chính) | Tác giả tự tải |
| 5 | 04/11 | Kandula'09, Benson WREN'09, Jupiter Evolving, FLARE, LetFlow, OnlineTE (preprint), Heffes–Lucantoni, Yates AoI | Tác giả tự tải |

Mức đọc của mọi nguồn mới là AI-T. Tác giả tự đọc: chưa có xác nhận.

> **Đính chính 04/11/2026 (L7.3 Phần 2, AI theo ủy quyền).**
> 1. **Bộ mốc vùng** đổi sang mốc của bản đồ twin Stage E: state h/T_int < 0,3; chuyển tiếp 0,3–3; tiệm cận ≥ 3. Mốc
>    4–7·T_int chỉ còn là "onset của z_pred1". Nhãn trong §1 và §3 đọc theo
>    [zone_thresholds_L73.md](zone_thresholds_L73.md), có bảng đổi nhãn từng dòng; số h/T_int không đổi.
> 2. **Công thức xấp xỉ §3d** chỉ đúng bậc độ lớn: trên 1.051 case ctmc-v2, nó ước T_int cao hơn giá trị chính xác
>    11–98% (trung vị 49%) ([zerofit_summary](../../results/explore_ctmc/l73/zerofit_summary.json)). Queue khuếch đại
>    thành phần chậm: chỉ 5% phương sai ở thang chậm đã làm T_int gần gấp ba (bảng dừng của mentor, tái lập ở
>    controls_l73/attempt03/g.json). T_relax/T_int chỉ 1,4–1,9, nên hai đồng hồ gần nhau.

## 0. Tóm tắt kết quả Phần 1

| Use case | h (nguồn) | τ (nguồn) | Vùng trong ctmc-v1 | Vì sao chưa bền |
|---|---|---|---|---|
| (i) Flowlet LB trong DC | ≥ timeout 0,2–0,5 ms (VPA17, AED14), nhưng **nội sinh**: flowlet co giãn theo nghẽn (VPA17) | 0,1–0,5 ms, là hằng số DRE (AED14) | state hoặc chuyển tiếp, nếu mượn T_mode microburst (§3b, §3f) | h không ngoại sinh; ON/OFF bất đối xứng; T_mode phụ thuộc độ phân giải đo (25 µs so với 1 ms) |
| (ii) DC TE thang giây | 1 s (MicroTE); O(giây)–O(phút) (Jupiter) | ≈ 0,6–0,7 s (MicroTE, AI-tính); Jupiter dùng TM 30 s và **đỉnh 1 giờ** | microburst-only: **tiệm cận** (§3a). Thành phần thang giây là mode: **state** ở ρ ≥ 0,6 (§3e) | Chưa có f (tỷ lệ phương sai) theo thang. Câu "≥ 150 s không dự đoán được" **không tìm thấy** trong hai nguồn được dẫn |
| (iii) WAN TE | 5 phút (SWAN; OnlineTE: "every few minutes") | ≈ 5 phút (AI-tính); P/2 + L có cơ sở ở YSB21 eq. 21 | **UNRESOLVED**: ngưỡng chuyển rơi đúng độ phân giải 5 phút (§3c) | Dưới 5 phút không có số đo. Trên 5 phút, 70–92% phương sai là chu kỳ xác định (LPC04) |
| (iv) NDT what-if | **UNSOURCED** | Cộng thêm 5 ms–1 s, có thể tới cỡ trăm giây nếu search tuần tự (AI-tính) | Thừa hưởng vùng của vòng nền | NDT là thủ tục ra quyết định, không phải use case riêng |

**Câu được phép viết:** "trong ctmc-v1, vùng phụ thuộc h/T_int; T_int thật bị chi phối bởi thành phần còn đáng kể chậm nhất,
nên nhãn vùng của một use case cần số đo đa thang và phụ thuộc thành phần nào được coi là mode".

Các câu sau **chưa được phép** viết như kết quả:
- "TE ở vùng tiệm cận";
- "flowlet LB ở vùng state";
- "Jupiter/CONGA validate ctmc-v1".

## 1. Câu hỏi và cách quy đổi

Với mỗi bối cảnh: các tỷ số h/T_int, τ/T_int, tải ρ, a/μ và μ·κ rơi vào vùng nào của ctmc-v1?

- **Vùng state:** h ≲ T_int. Telemetry tươi có giá trị (M0 tươi thắng Static; Stage E, L7.1).
- **Vùng chuyển tiếp:** T_int < h < 4·T_int. Cần model stochastic (bản đồ twin Stage E).
- **Vùng tiệm cận:** h ≳ 4–7·T_int. Planner dừng là đủ dùng (L72-3 đạt ở a = 3 và a = 7,5). Twin mean-value mù horizon
  bị telemetry tươi làm hại; công thức zero-fit đúng tới 0,1 pp từ (4; 7]·T_int ở a = 3.

**Quy đổi.** T_int,phys = (T_int/T_mode)(ρ, μ·κ, a/μ) × T_mode,phys.
- μ·κ là số packet được phục vụ trong một thời gian mode. Ở 10 Gb/s với gói 1.500 byte, μ ≈ 833.333 packet/s.
- Bảng dưới lấy từ CTMC ctmc-v1 ở a/μ = 0,6. Khi μ·κ ≥ 50, tỷ số đã gần giới hạn fluid.

| ρ | μ·κ = 1 | 10 | 42 | 50 | 167 | 200 (≈ fluid) |
|---|---:|---:|---:|---:|---:|---:|
| 0,60 | 13,1 | 3,69 | 2,76 | 2,71 | 2,53 | 2,52 |
| 0,70 | 23,9 | 6,44 | | 4,71 | | 4,37 |
| 0,80 | 55,2 | 14,2 | 10,5 | 10,3 | 9,61 | 9,56 |
| 0,85 | 99,7 | 25,1 | | 18,1 | | 16,8 |
| 0,90 | 228 | 56,1 | 41,2 | 40,4 | 37,6 | 37,4 |
| 0,95 | 928 | 224 | 163 | 160 | 149 | 148 |

**Tải thấp.** Ở a/μ = 0,6 chain cần ρ ≥ 0,6. Với ρ < 0,6 (WAN, DC), bảng dùng a/μ = 0,3, nơi cả hai mode đều ổn định:

| ρ (a/μ = 0,3) | μ·κ = 50 | 167 | 1000 |
|---|---:|---:|---:|
| 0,30 | 0,257 | 0,164 | 0,124 |
| 0,40 | 0,345 | 0,203 | 0,135 |
| 0,50 | 0,514 | 0,297 | 0,164 |
| 0,60 | 0,850 | 0,541 | 0,269 |
| 0,80 | 3,47 | 2,76 | 2,51 |

Khi ρ + a/μ < 1, backlog chỉ cỡ O(1) packet. T_int/T_mode còn giảm thêm theo μ·κ, vì phương sai nhanh của hàng đợi chiếm
phần lớn. Hệ quả là stake của backlog cost rất nhỏ.

Bảng phụ thuộc a/μ và giả định hai mode đối xứng exponential. Đổi biên độ, hình dạng hoặc độ bất đối xứng của burst sẽ
đổi bảng (§3f).

**Định nghĩa τ.** Công thức τ_eff ≈ P/2 + L + W/2 lấy từ T00.
- Phần P/2 + L có cơ sở primary: với update định kỳ chu kỳ P và service memoryless, Δ_D/M/1* = E[S] + P/2 (YSB21
  §III-A, eq. 21, tr. 1189).
- Phần W/2 (cửa sổ trung bình) là quy ước của T00, vẫn là AI-tính.
- Nếu update xếp hàng FCFS ở tải cao, tuổi lớn hơn công thức này (YSB21 eq. 17), nên τ_eff là cận dưới.

## 2. Bảng use case (mỗi ô có nguồn hoặc UNSOURCED)

Quy ước: **AI-tính** là phép tính của AI từ số trong bài, không phải số đo.

| Bối cảnh | Horizon h | Tuổi τ | Thang burst | Tải | Nguồn và giới hạn định nghĩa |
|---|---|---|---|---|---|
| (i) Flowlet LB trong DC | Timeout: CONGA mặc định 500 µs, khoảng bền 300 µs–1 ms (AED14 §3.6/PDF6); LetFlow 200 µs với RTT 50 µs (VPA17 §4.1/PDF6); age bit cho timeout thực trong [Δ, 2Δ] (VPA17 §3/PDF6, AED14 §3.4). Thời lượng flowlet **nội sinh**: path chậm cho flowlet ngắn; chỉ 2% quyết định đi S0 thì flowlet trên S0 lớn lên khoảng 65× (VPA17 §2.2/PDF5, Fig. 4); đổi path chủ yếu trong 30 ms đầu rồi hiếm (§4.1/PDF7). Flowlet trung vị theo byte ≈ 500 KB (AED14 §2.6.1/PDF4), tức 0,4–4 ms ở 1–10 Gb/s (AI-tính) | DRE τ = 160 µs mặc định, 100–500 µs (AED14 §3.2/PDF5, §3.6/PDF6). Cộng trễ piggyback (§3.3/PDF5, UNSOURCED); aging 10 ms (§3.3) | p90 hot-burst < 200 µs, Web 50 µs ở counter 25 µs (ZLK17 §5.1/PDF4). Ở mẫu 1 ms: trung vị 2 ms, p90 8 ms, 7,5 burst/s (GZL22 §5–6/PDF7). ON/OFF lognormal: ON khoảng 20–100 ms, OFF 20–100 s ở một switch, đọc từ trục hình (BAAZ09 §4.2, Fig. 7–8, tr. 69). Heavy hitter đổi giữa các khoảng 1/10/100 ms (RZB15 §5.3) | Tải trong/ngoài burst trên link host: 65,5%/5,5% (GZL22 §6/PDF7). Trung bình 1 phút: 99% link < 10% (RZB15 §4.1/PDF5) | Metric CONGA là rate lượng tử 3 bit; LetFlow chọn path **ngẫu nhiên** (VPA17 §3). Timeout tỷ lệ với chênh lệch trễ giữa các path (KKSB07 §4/PDF3: 50 ms trên ISP) |
| (ii) TE/lập lịch flow DC ở thang giây | MicroTE quyết định lại mỗi 1 s (BAAZ11 §5/PDF6). Hedera 5 s (T00). Jupiter: TE là vòng trong "O(seconds) to O(minutes)", lời giải trong vài chục giây; topology vài tuần (PMO22, PDF8) | MicroTE: ghi TM mỗi 0,1 s, gửi mỗi 1 s (§5.1.3/PDF7), cài route 40–150 ms (§7.3.2/PDF11), nên τ_eff ≈ 0,6–0,7 s (AI-tính). Jupiter: TM mỗi 30 s; ma trận dự đoán là **đỉnh 1 giờ**, làm mới hằng giờ hoặc khi thay đổi lớn, cộng hedging (PMO22 §4.4/PDF7) | Thành phần thang giây: cặp ToR ổn định 1,6–2,5 s (CLD) hoặc 1,5–5 s (UNV), khoảng 35% traffic dự đoán được qua 1 s (BAAZ11 §4.1.1/PDF5). TM đổi trung vị 82% ở cả τ = 10 s và 100 s; nghẽn > 1 s phần lớn ≤ 2 s, có episode tới 382 s (KSG09 §4.2–4.3, tr. 204–205). Trace 30 s "high variability", đỉnh quá khứ thường không dự đoán đỉnh tương lai (PMO22 §4.4). Chu kỳ ngày/tuần (BAM10 §6.4; RZB15 §4.1). Frontend ổn định 1–10 s, Hadoop không (RZB15 §5.2) | Hotspot ≥ 70% theo cửa sổ 5 phút (BAM10 §6.2–6.3) là định nghĩa. Link host trung bình 1 phút < 1% (RZB15 §4.1). Nghẽn theo định nghĩa > 70% utilization (KSG09 §4.2) | Mục tiêu MLU (MicroTE, Jupiter), không phải backlog. Run-length dưới ngưỡng 20% không phải thời gian lưu mode. **Câu "≥ 150 s"**: RZB15 §2 dẫn MicroTE; MicroTE §4/PDF4 dẫn Kandula'09 và Benson WREN'09; **không tìm thấy** ở cả hai (KSG09, BAAZ09 note) |
| (iii) TE trên WAN | T_c = 5 phút (HKM13 §4/PDF5). TE triển khai "re-optimize only once every few minutes" (GNM26 §1/PDF1, preprint; dẫn RedTE và Teal). Epoch "a few minutes" (P07 §3/PDF6) | Demand = trung bình 5 phút gần nhất (HKM13 §4.2/PDF6); broker báo mỗi 5 phút (§3/PDF4); cập nhật xong ≈ 22 s (§6.6/PDF11). τ_eff ≈ 2,5 + 2,5 + 0,4 ≈ 5 phút (AI-tính) | **UNSOURCED dưới 5 phút**: log 5 phút (HKM13 §6.1); SNMP 5 phút không đặc trưng được phần ngẫu nhiên (RGK03 §2.2). GNM26 dẫn "nearly 40% within a 5-minute interval" và biến động nhanh hơn chu kỳ TE (dẫn lại, chưa đọc nguồn). Trên 5 phút: chu kỳ/spike/nhiễu 92/6/2% (Sprint) và 70/19/12% (Abilene) (LPC04 Table 2/PDF9); peakedness a ≈ 0,5–3 (RGK03 §4, §6); regression 1 giờ dự đoán được 5 phút sau (P07 App. A); customer-facing có lúc > 100× trung bình (P07 §2.1) | Một nửa link < 30%, ba phần tư < 50% (HKM13 §2/PDF2); link bận 40–60% (§1/PDF1) | Background traffic elastic do SWAN điều khiển rate, nên tải không ngoại sinh. Mục tiêu throughput/fairness hoặc MLU. Thành phần chậm là chu kỳ biết theo giờ |
| (iv) Vòng what-if của NDT | **UNSOURCED**: AAA25 kích hoạt theo failure và chưa đo thời gian phản hồi (§VI/PDF6); ZBEK26 không nêu thời gian giữ | Đồng bộ NDT quang 0,009–0,96 s trung bình (VGC23 §III/PDF5–6). Twin cập nhật < 5 ms, 0,173 s mỗi yêu cầu, rerouting 187–214 ms (HHZ26 Tables 11, 15). Một lần đánh giá twin 200 ms cho 25k flow; search N = 1000 vòng hoặc theo time budget (ZBEK26 §I-C, §IV-D, §V-D). Cận trên AI-tính nếu tuần tự: ≈ 200 s | **UNSOURCED** | **UNSOURCED** | NDT là thủ tục ra quyết định gắn vào một vòng khác ([NDT_timing_L73](../literature/papers/NDT_timing_L73.md)). NDT1 §IV-B: optimizer đổi trọng số OSPF theo delay dự đoán |
| Trễ actuation (chung) | — | Planck ARP 2,5–3,5 ms / OpenFlow 4–9 ms (T00). Kuźniar 250/400 ms, đuôi 22 s và 4 phút (KPKC18 §4.1/Table 2). MicroTE 40–150 ms (BAAZ11 §7.3.2). SWAN ≈ 22 s, data plane 600 ms (HKM13 §6.6) | — | — | Các khoảng đo khác định nghĩa; không cộng máy móc (T00) |

## 3. Vùng (ILLUSTRATIVE — không phải calibration)

Giả định minh họa chung:
- Link 10 Gb/s.
- Với DC microburst: T_mode = 50–200 µs, mượn từ ZLK17 (khác định nghĩa), nên μ·κ ≈ 42–167.
- Cận dưới của T_int lấy ở μ·κ = 42 với T_mode = 50 µs; cận trên ở μ·κ = 167 với T_mode = 200 µs.

### 3a. (ii) DC TE ở thang giây, microburst-only

| | ρ = 0,6 | ρ = 0,8 | ρ = 0,9 | ρ = 0,95 |
|---|---|---|---|---|
| T_int (microburst-only) | 0,14–0,51 ms | 0,53–1,9 ms | 2,1–7,5 ms | 8,2–30 ms |
| h/T_int, h = 1 s (MicroTE) | 2.000–7.300 | 520–1.900 | 130–490 | 34–120 |
| h/T_int, h = 5 s (Hedera) | 9.900–36.000 | 2.600–9.500 | 670–2.400 | 170–610 |
| τ/T_int, τ ≈ 0,6–5 s | ≫ 1 | ≫ 1 | ≫ 1 | ≫ 1 |
| Vùng | tiệm cận | tiệm cận | tiệm cận | tiệm cận |

### 3b. (i) Flowlet LB, cùng T_int với 3a

| | ρ = 0,6 | ρ = 0,8 | ρ = 0,9 |
|---|---|---|---|
| h/T_int, h = T_fl = 0,5 ms | 0,99–3,6 | 0,26–0,95 | 0,07–0,24 |
| h/T_int, h = 0,4–4 ms (flowlet 500 KB, AI-tính) | 0,79–29 | 0,21–7,6 | 0,05–1,9 |
| τ/T_int, τ = 0,1–0,5 ms (DRE) | 0,20–3,6 | 0,05–0,95 | 0,01–0,24 |
| Vùng | chuyển tiếp; tới tiệm cận nếu flowlet dài | state–chuyển tiếp | state |

Ở ρ = 0,6, τ/T_int có thể ≳ 1: thông tin của CONGA cũ ngang T_int.

Hai giới hạn của phép quy đổi cho (i):
- VPA17 cho thấy h là nội sinh: ở cân bằng, đổi path hiếm, nên h hiệu dụng dài hơn timeout. ctmc-v1 coi h là tham số
  ngoại sinh.
- LetFlow vẫn cân tải tốt dù chọn path **ngẫu nhiên** (VPA17 §2.2, §4). Vì vậy giá trị của state tươi ở (i) không phải
  cơ chế duy nhất; có cơ chế khác không cần telemetry.

### 3c. (iii) WAN TE: chỉ tính được dạng điều kiện

h = 5 phút; τ ≈ 5 phút ≈ h. Thời gian mode của demand WAN dưới 5 phút là UNSOURCED. Ta có h/T_int = h/(r(ρ)·T_mode),
với r lấy từ bảng tải thấp ở §1, cột μ·κ lớn nhất.

| ρ (a/μ) | r | Tiệm cận (h/T_int ≥ 7) nếu | State (h/T_int ≤ 1) nếu |
|---|---:|---|---|
| 0,3 (0,3) | 0,124 | T_mode ≲ 350 s | T_mode ≳ 2.400 s |
| 0,5 (0,3) | 0,164 | T_mode ≲ 260 s | T_mode ≳ 1.800 s |
| 0,6 (0,6) | 2,53 | T_mode ≲ 17 s | T_mode ≳ 120 s |
| 0,8 (0,6) | 9,61 | T_mode ≲ 4,5 s | T_mode ≳ 31 s |

Với a/μ = 0,3, ngưỡng chuyển của tải điển hình trên IDN (30–50%) nằm ở T_mode ≈ 4–6 phút, đúng bằng độ phân giải của
log 5 phút. r còn giảm khi μ·κ tăng, nên ngưỡng thật còn dịch lên một chút. Thêm vào đó, τ ≈ h, và ở ρ + a/μ < 1 stake
backlog gần 0.

### 3c′. Tỷ lệ phương sai ở WAN trên thang 5 phút (LPC04, RGK03)

| | Chu kỳ | Spike | Nhiễu |
|---|---:|---:|---:|
| Sprint (bin 10 phút) | 92% | 6% | 2% |
| Abilene (bin 5 phút) | 70% | 19% | 12% |

Nguồn: LPC04 Table 2/PDF9, OD flow đã chuẩn hóa.

RGK03 (§2.2) mô tả cùng cấu trúc: m(t) gồm xu hướng và chu kỳ ngày/tuần, phần dư có peakedness a ≈ 0,5–3. Độ lệch chuẩn
tương đối của phần dư là √(a/m) ≈ 4–9%, tính với m = 350 Mbps là tham số mô phỏng của RGK03 §5.1 (AI-tính).

Kết luận cho (iii):
- Phần lớn phương sai trên 5 phút là chu kỳ **xác định theo giờ**. Đó là một mode quan sát được, không phải mode Markov ẩn
  của ctmc-v1.
- Phần ngẫu nhiên (8–30%) có thang dưới 5 phút chưa đo, nên ô (iii) vẫn UNRESOLVED.
- Có thể nói rõ: trên 5 phút, ctmc-v1 **không** mô tả phần lớn phương sai của WAN.

### 3d. Khi thang burst chậm hơn (kịch bản đa thang, ILLUSTRATIVE)

Giả sử nền có thêm một thành phần chậm, mang tỷ lệ f phương sai, với thời gian mode T_slow. Xấp xỉ thô: T_int ≈
f·(T_int/T_mode)(ρ)·T_slow. Với ρ = 0,8 và f = 0,1:

| T_slow | T_int (thành phần chậm) | h/T_int, h = 1 s | h/T_int, h = 5 s | Vùng của (ii) |
|---|---|---|---|---|
| 10 s | ≈ 9,6 s | 0,10 | 0,52 | **state** |
| 60 s | ≈ 57 s | 0,02 | 0,09 | **state** |
| 600 s | ≈ 570 s | 0,002 | 0,009 | **state** |

Chỉ cần 10% phương sai nằm ở thang chục giây trở lên là (ii) đổi nhãn từ tiệm cận sang state.

Bằng chứng về thành phần chậm ở DC:
- **Ở thang giây–phút:**
  - TM đổi khoảng 82% ở cả 10 s và 100 s (KSG09 §4.3);
  - nghẽn có episode hàng trăm giây (KSG09 §4.2);
  - trace 30 s biến động mạnh (PMO22 §4.4);
  - OFF dài 20–100 s ở một switch (BAAZ09 Fig. 7).
- **Ở thang ngày:**
  - chu kỳ ngày/tuần (BAM10 §6.4, RZB15 §4.1);
  - GZL22 §7: chu kỳ ngày "not as dominant" với tranh chấp buffer.
- **Ổn định ở thang giây:** Frontend (RZB15 §5.2) và top cặp ToR (BAAZ11 §4.1.1).

Chưa nguồn nào cho f và T_slow theo nghĩa phương sai của tải đầu vào một path. Công thức xấp xỉ chưa được kiểm trong model
có hai thang; đó là việc của Phần 2.

### 3e. (ii) khi lấy thành phần thang giây của MicroTE làm mode (ILLUSTRATIVE)

Dùng run-length 1,5–5 s (BAAZ11 §4.1.1) làm T_mode,phys, cột fluid:

| ρ (a/μ) | T_int | h/T_int, h = 1 s | h/T_int, h = 5 s | τ/T_int, τ ≈ 0,6–0,7 s | Vùng |
|---|---|---|---|---|---|
| 0,6 (0,6) | 3,8–13 s | 0,08–0,26 | 0,40–1,3 | 0,05–0,19 | state (Hedera: state–chuyển tiếp) |
| 0,8 (0,6) | 14–48 s | 0,02–0,07 | 0,10–0,35 | 0,01–0,05 | state |
| 0,9 (0,6) | 56–190 s | 0,005–0,02 | 0,03–0,09 | ≤ 0,01 | state |
| 0,3 (0,3) | 0,19–0,62 s | 1,6–5,4 | 8,1–27 | 0,97–3,8 | chuyển tiếp (Hedera: tiệm cận) |
| 0,5 (0,3) | 0,25–0,82 s | 1,2–4,1 | 6,1–20 | 0,73–2,9 | chuyển tiếp (Hedera: tiệm cận) |

Hai dòng a/μ = 0,3 dùng cột μ·κ = 1000; ở hai dòng này stake backlog ≈ 0.

Cùng một use case (ii) cho ba nhãn tùy thành phần nào là mode và ρ:
- microburst: tiệm cận;
- thang giây, tải cao: state;
- tải thấp: chuyển tiếp hoặc tiệm cận, nhưng stake ≈ 0.

**Đối chiếu với thực tế (không phải validation).** Jupiter (PMO22 §4.4) chạy TE ở thang giây–phút nhưng dùng **đỉnh 1 giờ
cộng hedging**, không dùng ước lượng điểm từ state tươi. Lựa chọn thiết kế này nhất quán với vùng tiệm cận (planner dài hạn
đủ dùng). Nó không chứng minh vùng: mục tiêu là MLU, hedging là robust optimization, và bài không so với phương án dùng
state tươi.

Giới hạn của phép quy đổi:
- Run-length dưới ngưỡng 20% không phải thời gian lưu exponential.
- Top 100 cặp ToR không phải tải của một path.
- 35% traffic dự đoán được là tỷ lệ traffic, không phải tỷ lệ phương sai.

### 3f. Burst bất đối xứng và phụ thuộc độ phân giải (GZL22, BAAZ09, ILLUSTRATIVE)

GZL22 (mẫu 1 ms): T_on ≈ 2 ms; T_off ≈ 1/(7,5/s) ≈ 133 ms (AI-tính, coi burst đều). BAAZ09 (một switch, 2009): ON chục
ms, OFF chục giây, cả hai lognormal.

Với chuỗi Markov hai trạng thái, thời gian tương quan của mode là 1/(1/T_on + 1/T_off). Ở GZL22 con số này ≈ 1,97 ms, tức
mode "quên" sau khoảng T_on dù OFF dài. Đây là đồng nhất thức toán, chỉ áp dụng nếu ON/OFF xấp xỉ exponential; BAAZ09 cho
thấy chúng lognormal.

ctmc-v1 chỉ có hai mode đối xứng, nên chưa tính được T_int cho các cặp này. Nếu tạm coi T_int cùng bậc với 2 ms:
- (ii) với h = 1 s cho h/T_int cỡ vài trăm, vẫn tiệm cận;
- (i) với h = 0,5–4 ms cho h/T_int ≈ 0,25–2, state hoặc chuyển tiếp.

Đây chỉ là bậc độ lớn.

Hai điểm lệch:
1. Thang burst phụ thuộc độ phân giải đo, dù cùng ngưỡng 50%: 25 µs cho p90 dưới 200 µs (ZLK17), 1 ms cho 2–8 ms (GZL22).
2. Cả hai mode đều ổn định trên link host (65,5%/5,5%). Stake thật là tranh chấp buffer chung của rack, nằm ngoài ctmc-v1.

## 4. Mối đe dọa realism

| Mối đe dọa | Nguồn | Ảnh hưởng tới nhãn vùng |
|---|---|---|
| Burst đa thang / self-similar | LTWW94 §4–5; BAM10 §5.2, §6.4; ZLK17 §5.2; RZB15 §4.1, §5.2, §6.2; BAAZ11 §4.1.1; KSG09 §4.2–4.3; PMO22 §4.4; RGK03 §2.2; LPC04 Table 2 | Có thể đổi (ii) từ tiệm cận sang state (§3d, §3e) |
| ON/OFF bất đối xứng, không exponential | GZL22 §6 (2 ms / 133 ms); BAAZ09 §4.2 (lognormal; ON chục ms, OFF chục giây) | Bảng T_int/T_mode (hai mode đối xứng exponential) không áp dụng trực tiếp (§3f) |
| Thang burst phụ thuộc độ phân giải đo | ZLK17 (25 µs) so với GZL22 (1 ms); BAAZ09 (bin 15/100 ms); Meta switch chỉ có counter 1 phút (GZL22 §7) | T_mode không có một giá trị duy nhất; nhãn vùng phụ thuộc cách đo |
| h nội sinh | VPA17 §2.2, §4.1 (flowlet co giãn theo nghẽn); KKSB07 §4 (timeout theo chênh lệch trễ) | (i) không có h ngoại sinh như ctmc-v1 |
| Tải không ngoại sinh | SWAN điều khiển rate background (HKM13 §3–4.2). TCP feedback **UNSOURCED** ngoài VPA17 §4.1 (ACK clocking giữ flow trên path) | Plant khác contract |
| Mục tiêu khác backlog cost | CONGA min-max congestion (AED14); SWAN throughput/fairness (HKM13); MicroTE, Jupiter, OnlineTE dùng MLU (BAAZ11, PMO22, GNM26) | Nhãn vùng chỉ nói về regret của ctmc-v1 |
| Planner thực tế là robust, không phải dừng | Jupiter đỉnh 1 giờ + hedging (PMO22 §4.4); SWAN nâng demand theo sai số dự báo (HKM13 §4.2) | So sánh "planner dừng vs state tươi" của ctmc-v1 khác với lựa chọn robust/hedging của hệ thật |
| Tải thấp | RZB15 §4.1; HKM13 §2; GZL22 §6 (run trung vị 6,4%) | Ở ρ + a/μ < 1 stake backlog ≈ 0 |
| Dự đoán heavy hitter gần ngẫu nhiên | RZB15 §5.3 | Ủng hộ "thông tin per-flow mất giá trị sau một khoảng" ở thang ms |
| Nhiều path / topology | ZLK17 §6.1; AED14 §5.1; PMO22 (direct + transit); NDT1 §IV-B | Hai path rời là trừu tượng hóa |
| Buffer hữu hạn, chia sẻ | ZLK17 §6.4; GZL22 §7 (tranh chấp buffer, mất 33% buffer ở run trung vị) | Không có kích thước tuyệt đối; tranh chấp nằm ngoài model |
| Trễ actuation có đuôi dài | KPKC18 Table 2 (22 s, 4 phút); HKM13 §6.6 (22 s) | τ hiệu dụng có thể ≫ trung bình |
| Mode quan sát được hoặc xác định | D22 L7.1 (backlog-only đã có harm); RGK03, LPC04, P07 (chu kỳ theo giờ) | ctmc-v1 không có trục "biết giờ là biết mode" |

## 5. Kết luận Phần 1 (AI theo ủy quyền; chưa có tác giả đọc)

1. **Nhãn vùng của một use case không phải thuộc tính của use case đó.** Nó là thuộc tính của cặp (use case, thành phần
   traffic được coi là mode). Với (ii), ba cách chọn cho ba nhãn (§3e). Đây là kết quả chính của Phần 1, và là lý do Phần
   2 cần model hai thang.
2. **h và τ đã có nguồn primary cho (i), (ii), (iii).**
   - (i): timeout 0,2–0,5 ms, DRE 0,1–0,5 ms.
   - (ii): 1 s và khoảng 0,6–0,7 s (MicroTE); giây–phút với TM 30 s và đỉnh 1 giờ (Jupiter).
   - (iii): 5 phút và khoảng 5 phút.

   (iv) vẫn không có h.
3. **Thang burst và tỷ lệ phương sai mới có một phần.**
   - DC: thang µs (ZLK17), ms (GZL22, BAAZ09), giây (BAAZ11, KSG09), ngày (BAM10, RZB15).
   - WAN: f ở ≥ 5 phút (LPC04).
   - Thiếu f cho DC và mọi số đo dưới 5 phút cho WAN.
4. **Câu "≥ 150 s không dự đoán được" không có nguồn đo.** Chuỗi dẫn là RZB15 → MicroTE → Kandula'09 và Benson WREN'09, và
   không tìm thấy con số này ở hai nguồn cuối. Không được dùng câu này như số đo; chỉ có thể dẫn như phát biểu của MicroTE.
5. **Hệ thật lệch contract ở bốn trục:** mục tiêu (MLU/throughput), h nội sinh, tải bị điều khiển, mode bất đối xứng hoặc
   xác định. Bất kỳ câu thực dụng nào cũng phải nêu các trục này.
6. **Câu được phép** như ở §0. Không có claim novelty, không đổi nhãn PC/Gate.

## 6. Bàn giao cho Phần 2

Phần 2 là held-out hai thang (4 mode). **Thẻ do tác giả viết**; AI không soạn thẻ trong Phần 1.

Thông tin Phần 1 có thể dùng làm đầu vào:
- **Hai thang có nguồn ở DC (§3d, §3e):**
  - thang nhanh (µs–ms): microburst ZLK17, GZL22;
  - thang chậm (giây): BAAZ11 1,5–5 s; KSG09 đổi mạnh trong 10 s.

  Tỷ số thang ≈ 10³–10⁵ (1,5 s / 2 ms ≈ 750; 10 s / 50 µs ≈ 2 × 10⁵).
- **Bất đối xứng (§3f).** T_on/T_off ≈ 1/65 (GZL22) tới ≈ 1/1000 (BAAZ09, bậc độ lớn). Một held-out đối xứng sẽ không kiểm
  điểm lệch này.
- **Phương pháp nối số đo với tham số chain (HL86 §III).** Fit MMPP bằng rate trung bình, tỷ số phương sai/trung bình ở hai
  thang thời gian và moment bậc ba. Áp vào counter ở nhiều độ phân giải (25 µs, 1 ms, 5 phút) sẽ ra tham số mode mà không
  cần quan sát mode.
- **Đại lượng cần dự đoán.** Công thức xấp xỉ T_int ≈ f·(T_int/T_mode)·T_slow ở §3d chưa kiểm. Đây là ứng viên tự nhiên
  cho một dự đoán zero-fit trong Phần 2, nếu tác giả chọn.
- **Không làm trong Phần 1:** không chạy chain 4 mode, không khóa thẻ, không chấm.

## 7. Nguồn của Phần 1

| ID | Nguồn | Định danh | Bản đọc | Note |
|---|---|---|---|---|
| HKM13 | Hong et al., SWAN, SIGCOMM'13, tr. 15–26 | DOI 10.1145/2486001.2486012 | Trang hội nghị + VoR ACM (trùng chữ) | [HKM13](../literature/papers/HKM13.md) |
| AED14 | Alizadeh et al., CONGA, SIGCOMM'14, tr. 503–514 | DOI 10.1145/2619239.2626316 | Trang tác giả | [AED14](../literature/papers/AED14.md) |
| RZB15 | Roy et al., SIGCOMM'15, tr. 123–137 | DOI 10.1145/2785956.2787472 | Trang tác giả | [RZB15](../literature/papers/RZB15.md) |
| BAAZ11 | Benson et al., MicroTE, CoNEXT'11, tr. 1–12 | DOI 10.1145/2079296.2079304 | VoR ACM | [BAAZ11](../literature/papers/BAAZ11.md) |
| RGK03 | Roughan et al., backbone variability (IMW'02 / ITC'03) | DOI 10.1145/637201.637213; 10.1016/s1388-3437(03)80183-x | Bản tác giả của bản ITC | [RGK03](../literature/papers/RGK03.md) |
| KPKC18 | Kuźniar et al., Comput. Netw. 136 (2018) | DOI 10.1016/j.comnet.2018.02.014 | Accepted manuscript | [KPKC18](../literature/papers/KPKC18.md) |
| GZL22 | Ghabashneh et al., IMC'22, tr. 567–580 | DOI 10.1145/3517745.3561430 | Camera-ready | [GZL22](../literature/papers/GZL22.md) |
| LPC04 | Lakhina et al., SIGMETRICS'04, tr. 61–72 | DOI 10.1145/1005686.1005697 | Camera-ready | [LPC04](../literature/papers/LPC04.md) |
| KSG09 | Kandula et al., IMC'09, tr. 202–208 | DOI 10.1145/1644893.1644918 | Camera-ready (đọc ảnh render) | [KSG09](../literature/papers/KSG09.md) |
| BAAZ09 | Benson et al., WREN'09, tr. 65–72 | DOI 10.1145/1592681.1592692 | Camera-ready | [BAAZ09](../literature/papers/BAAZ09.md) |
| PMO22 | Poutievski et al., Jupiter Evolving, SIGCOMM'22, tr. 66–85 | DOI 10.1145/3544216.3544265 | Camera-ready OA | [PMO22](../literature/papers/PMO22.md) |
| KKSB07 | Kandula et al., FLARE, CCR 37(2) 2007, tr. 51–62 | DOI 10.1145/1232919.1232925 | Bản CCR có public review | [KKSB07](../literature/papers/KKSB07.md) |
| VPA17 | Vanini et al., LetFlow, NSDI'17, tr. 407–420 | USENIX (không DOI) | Bản USENIX OA | [VPA17](../literature/papers/VPA17.md) |
| GNM26 | Ghavidel et al., OnlineTE | arXiv 2605.16187v1 | **Preprint** | [GNM26](../literature/papers/GNM26.md) |
| HL86 | Heffes & Lucantoni, JSAC SAC-4(6) 1986, tr. 856–868 | DOI 10.1109/JSAC.1986.1146393 | VoR scan | [HL86](../literature/papers/HL86.md) |
| YSB21 | Yates et al., AoI survey, JSAC 39(5) 2021, tr. 1183–1210 | DOI 10.1109/JSAC.2021.3065072 | VoR | [YSB21](../literature/papers/YSB21.md) |
| ZBEK26, VGC23, HHZ26, AAA25 | Paper NDT cũ của tác giả | xem note | Author version / AM / in press / arXiv | [NDT_timing_L73](../literature/papers/NDT_timing_L73.md) |

Thư viện có sẵn được dùng lại: ZLK17, BAM10, LTWW94, NDT1, P07, T00.

Ghi chú về nguồn:
- PDF lưu ngoài Git ở `~/papers/state-model-regret/l73/`; sha256 ghi trong từng note.
- Chưa có bản chính thức của CONGA, RZB15, NDT1, Planck, RGK03 (VoR IMW) và KPKC18 (VoR Elsevier).
- B4 không dùng.
- Chưa thêm các nguồn vào `papers/data/catalog.json` và Excel trên `main`.
- **Ứng viên cho đợt sau** (dẫn lại từ GNM26, chưa tra DOI, chưa đề xuất): RedTE (SIGCOMM'24) về burst dưới một giây trên
  WAN; Namyar et al. (NSDI'24) về biến động 5 phút. Hai bài này là lối duy nhất đã thấy để lấp thang dưới 5 phút của (iii).
