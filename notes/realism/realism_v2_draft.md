# Realism v2 — bản nháp (L7.3 Phần 1)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền L7.3 Phần 1** (03/11/2026), nhánh `explore/realism-l73` từ
`explore/ctmc-phase7`. Không phải author-self, không sửa [envelope v1](envelope_v1.json), không chạy truth mới. Các tỷ số
T_int/T_mode dưới đây là đại lượng dừng của chain, không phải truth.

- **Đợt 1:** chỉ dùng nguồn đã có trong thư viện, mức đọc theo note gốc; không đọc lại primary.
- **Đợt 2 (cùng ngày):** ba nguồn mới SWAN (HKM13), CONGA (AED14) và Roy2015 (RZB15).
  - Được duyệt **theo ủy quyền**: tác giả nhắn "bạn hãy tự làm tự chạy thực hiện cho tôi luôn đi". Đây là duyệt
    AI-delegated, tác giả không tự sàng.
  - PDF lấy từ trang hội nghị và trang tác giả, lưu ngoài Git.
  - Mức đọc AI-T, có trích §/trang. Tác giả tự đọc: chưa có xác nhận.
  - Chi tiết ở [HKM13](../literature/papers/HKM13.md), [AED14](../literature/papers/AED14.md) và
    [RZB15](../literature/papers/RZB15.md).
- **Đợt 3 (04/11/2026).**
  - **Tác giả tự tải** sau danh sách L7.3-R2: MicroTE ([BAAZ11](../literature/papers/BAAZ11.md), VoR), Roughan et al.
    ([RGK03](../literature/papers/RGK03.md), bản tác giả của bản ITC 2003), Kuźniar'18
    ([KPKC18](../literature/papers/KPKC18.md), accepted manuscript) và bản ACM của SWAN (trùng chữ với bản đã đọc).
  - **Paper NDT cũ của tác giả** trong thư mục Downloads (theo yêu cầu đọc của tác giả):
    [NDT_timing_L73](../literature/papers/NDT_timing_L73.md).
  - **Nguồn đã có trong thư viện:** đọc thêm BAM10 §6.4 và P07 DOTE.
  - Mức đọc AI-T; tác giả tự đọc: chưa có xác nhận.

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

**Tải thấp.** Ở a/μ = 0,6 chain cần ρ ≥ 0,6. Với ρ < 0,6 (WAN, §2), bảng dùng a/μ = 0,3, nơi cả hai mode đều ổn định:

| ρ (a/μ = 0,3) | μ·κ = 50 | 167 | 1000 |
|---|---:|---:|---:|
| 0,30 | 0,257 | 0,164 | 0,124 |
| 0,40 | 0,345 | 0,203 | 0,135 |
| 0,50 | 0,514 | 0,297 | 0,164 |
| 0,60 | 0,850 | 0,541 | 0,269 |
| 0,80 | 3,47 | 2,76 | 2,51 |

Khi ρ + a/μ < 1, backlog chỉ cỡ O(1) packet. T_int/T_mode khi đó còn giảm thêm theo μ·κ: phương sai nhanh của hàng đợi
chiếm phần lớn, phần do mode chậm chiếm phần nhỏ. Hệ quả là stake của backlog cost rất nhỏ.

Bảng phụ thuộc a/μ và giả định hai mode đối xứng exponential; đổi biên độ hoặc hình dạng burst sẽ đổi bảng.

## 2. Bảng use case (mỗi ô có nguồn hoặc UNSOURCED)

Quy ước trong bảng: **AI-tính** là phép tính của AI từ số trong bài, không phải số đo.

| Bối cảnh | Horizon h | Tuổi τ | Thang burst | Tải | Nguồn và giới hạn định nghĩa |
|---|---|---|---|---|---|
| (i) Flowlet LB trong DC | ≥ T_fl. T_fl mặc định 500 µs, khoảng bền 300 µs–1 ms (AED14 §3.6/PDF6). Flowlet trung vị theo byte ≈ 500 KB (§2.6.1/PDF4), tức ≈ 0,4–4 ms ở 1–10 Gb/s (AI-tính; rate từng flow UNSOURCED) | DRE τ = 160 µs mặc định, 100–500 µs (§3.2/PDF5, §3.6/PDF6). Cộng trễ piggyback (§3.3/PDF5, UNSOURCED); phản ứng ở thang RTT ≈ 100 µs (§1/PDF2) | p90 hot-burst < 200 µs, Web 50 µs (ZLK17 §5.1/PDF4). Heavy hitter đổi giữa các khoảng 1/10/100 ms (RZB15 §5.3/PDF10–11) | **UNSOURCED** cho tải tức thời. Trung bình 1 phút: 99% link < 10% (RZB15 §4.1/PDF5), không phải ρ của một mode | Metric CONGA là rate lượng tử 3 bit, không phải backlog. Mục tiêu min-max congestion. h là thời lượng flowlet, không cố định (AED14 note) |
| (ii) TE/lập lịch flow DC ở thang giây | MicroTE quyết định lại route mỗi khoảng 1 s, nên h = 1 s (BAAZ11 §5/PDF6, primary). Hedera 5 s (T00, Hedera §5.4; AED14 §1/PDF2) | MicroTE: server ghi ma trận traffic mỗi 0,1 s, gửi mỗi 1 s (§5.1.3/PDF7); cài route < 40 ms trung bình, < 150 ms tệ nhất (§7.3.2/PDF11); LP 0,6 s ở 100 ToR (§7.3.3/PDF11). τ_eff ≈ 0,5 + 0,05 + 0,04–0,15 ≈ 0,6–0,7 s, chưa tính LP (AI-tính). Hedera τ_eff ≈ 5 s (T00) | Thành phần thang giây: traffic cặp ToR ổn định (đổi ≤ 20%) trung bình 1,6–2,5 s (CLD, 60% cặp) hoặc 1,5–5 s (UNV, 35% cặp); khoảng 35% traffic dự đoán được qua 1 s (BAAZ11 §4.1.1/PDF5, Fig. 2). Microburst như (i). Đa thang: LTWW94 §4–5; BAM10 §5.2 (ON/OFF), §6.4/PDF10–11 (chu kỳ ngày/tuần, biên < 10% đỉnh–đáy ở ≥ 80% link); RZB15 §5.2 (Frontend ổn định 1–10 s, Hadoop không), §4.1 (chu kỳ ngày). "Không dự đoán được từ ≥ 150 s" vẫn là dẫn lại: BAAZ11 §4/PDF4 trích Kandula'09 và Benson WREN'09, hai bài chưa đọc | Hotspot ≥ 70% theo cửa sổ 5 phút (BAM10 §6.2–6.3/PDF9) là định nghĩa. RZB15: trung bình 1 phút < 1% ở link host (§4.1/PDF5). MicroTE không cho ρ | Thời gian ổn định là run-length dưới ngưỡng 20% trên top 100 cặp, không phải thời gian lưu mode. Mục tiêu MicroTE là MLU, không phải backlog. Hedera 5 s do giới hạn đọc register NetFPGA (T00) |
| (iii) TE trên WAN | T_c = 5 phút (HKM13 §4/PDF5). Testbed dùng 1 phút để stress-test (§5.1/PDF8) | Demand = trung bình 5 phút gần nhất (§4.2/PDF6). Broker báo mỗi T_s = 5 phút (§3/PDF4). Cập nhật xong ≈ 22 s (§6.6/PDF11). τ_eff ≈ 2,5 + 2,5 + 0,4 ≈ 5 phút (AI-tính theo công thức T00) | **UNSOURCED** dưới 5 phút: log 5 phút (HKM13 §6.1/PDF9); SNMP 5 phút không đặc trưng được phần ngẫu nhiên (RGK03 §2.2/PDF3). Trên 5 phút: phần lớn biến động là xu hướng và chu kỳ ngày/tuần dự đoán được (RGK03 §1–2.2/PDF2–3; P07 App. A/PDF18). Phần dư có peakedness a ≈ 0,5–3 (RGK03 §4/PDF6, §6/PDF9). Interactive: chỉ 1% thời gian lệch dự báo > 1% (HKM13 §6.6/PDF11). Customer-facing: có lúc > 100× trung bình (P07 §2.1/PDF3) | Một nửa link < 30%, ba phần tư < 50% trên IDN (§2/PDF2); link bận 40–60% (§1/PDF1) | Background traffic là elastic và bị SWAN điều khiển rate, nên tải không ngoại sinh. Mục tiêu throughput/fairness, không phải backlog (HKM13 note). Thành phần chậm là chu kỳ theo giờ, gần với mode quan sát được hơn là mode Markov ẩn (RGK03 note). Epoch TE "a few minutes" (P07 §3/PDF6) |
| (iv) Vòng what-if của NDT | **UNSOURCED**: AAA25 kích hoạt theo failure và chưa đo thời gian phản hồi (§VI/PDF6). ZBEK26 tối ưu trọng số IGP và route BGP nhưng không nêu thời gian giữ | Các phần góp vào τ: đồng bộ NDT quang 0,009–0,96 s trung bình (VGC23 §III/PDF5–6); twin cập nhật < 5 ms, 0,173 s mỗi yêu cầu route, rerouting 187–214 ms (HHZ26 Tables 11, 15/PDF24–25); một lần đánh giá twin 200 ms cho 25k flow, search N = 1000 vòng hoặc theo time budget (ZBEK26 §I-C/PDF2, §IV-D/PDF6, §V-D/PDF9). Cận trên AI-tính nếu đánh giá tuần tự: ≈ 200 s | **UNSOURCED** | **UNSOURCED** | NDT là thủ tục ra quyết định gắn vào một vòng khác; h là của vòng đó, NDT cộng thêm vào τ ([NDT_timing_L73](../literature/papers/NDT_timing_L73.md)). NDT1 §IV-B/PDF5: optimizer đổi trọng số OSPF theo delay dự đoán |
| Trễ actuation (chung) | — | Planck ARP 2,5–3,5 ms / OpenFlow 4–9 ms (§7.2/Fig. 16); Kuźniar gap 250/400 ms (§4.1/Table 2; đã kiểm trên bản AM, KPKC18), đuôi tới 22 s ở một switch và tới 4 phút ở một firmware (KPKC18 Table 2/PDF9). MicroTE cài route 40–150 ms (BAAZ11 §7.3.2/PDF11). SWAN: ≈ 22 s mỗi lần cập nhật, data plane đổi trong ≈ 600 ms (HKM13 §6.6/PDF11) | — | — | Các khoảng đo khác định nghĩa; không cộng máy móc (T00) |

## 3. Vùng (ILLUSTRATIVE — không phải calibration)

Các bảng dưới dùng hai giả định minh họa:
- Link 10 Gb/s.
- Với DC: T_mode = 50–200 µs, mượn từ hot-burst của ZLK17 (khác định nghĩa), nên μ·κ ≈ 42–167.

Khoảng T_int lấy cận dưới ở μ·κ = 42 với T_mode = 50 µs, cận trên ở μ·κ = 167 với T_mode = 200 µs. Bản trước dùng cột
μ·κ = 50 và cột fluid; số dưới đây đã thay bằng cột 42/167, sai khác dưới 10%.

### 3a. (ii) DC TE ở thang giây, microburst-only

| | ρ = 0,6 | ρ = 0,8 | ρ = 0,9 | ρ = 0,95 |
|---|---|---|---|---|
| T_int (microburst-only) | 0,14–0,51 ms | 0,53–1,9 ms | 2,1–7,5 ms | 8,2–30 ms |
| h/T_int, h = 1 s (MicroTE) | 2.000–7.300 | 520–1.900 | 130–490 | 34–120 |
| h/T_int, h = 5 s (Hedera) | 9.900–36.000 | 2.600–9.500 | 670–2.400 | 170–610 |
| τ/T_int, τ ≈ 1–5 s | ≫ 1 | ≫ 1 | ≫ 1 | ≫ 1 |
| Vùng | tiệm cận | tiệm cận | tiệm cận | tiệm cận |

### 3b. (i) Flowlet LB, cùng T_int với 3a

| | ρ = 0,6 | ρ = 0,8 | ρ = 0,9 |
|---|---|---|---|
| h/T_int, h = T_fl = 0,5 ms | 0,99–3,6 | 0,26–0,95 | 0,07–0,24 |
| h/T_int, h = 0,4–4 ms (flowlet 500 KB, AI-tính) | 0,79–29 | 0,21–7,6 | 0,05–1,9 |
| τ/T_int, τ = 0,1–0,5 ms (DRE) | 0,20–3,6 | 0,05–0,95 | 0,01–0,24 |
| Vùng | chuyển tiếp; tới tiệm cận nếu flowlet dài | state–chuyển tiếp | state |

Ở ρ = 0,6, τ/T_int có thể ≳ 1: thông tin của CONGA cũ ngang T_int. Vùng của (i) bị chi phối bởi h là thời lượng
flowlet, mà thời lượng này không có nguồn trực tiếp.

### 3c. (iii) WAN TE: chỉ tính được dạng điều kiện

h = 5 phút; τ ≈ 5 phút ≈ h. Thời gian mode của demand WAN là UNSOURCED. Tỷ số h/T_int = h/(r(ρ)·T_mode), với r lấy từ
bảng tải thấp ở §1. Vì T_mode ≫ 1/μ nên dùng cột μ·κ lớn nhất.

| ρ (a/μ) | r | Tiệm cận (h/T_int ≥ 7) nếu | State (h/T_int ≤ 1) nếu |
|---|---:|---|---|
| 0,3 (0,3) | 0,124 | T_mode ≲ 350 s | T_mode ≳ 2.400 s |
| 0,5 (0,3) | 0,164 | T_mode ≲ 260 s | T_mode ≳ 1.800 s |
| 0,6 (0,6) | 2,53 | T_mode ≲ 17 s | T_mode ≳ 120 s |
| 0,8 (0,6) | 9,61 | T_mode ≲ 4,5 s | T_mode ≳ 31 s |

Với a/μ = 0,3, ngưỡng chuyển của tải điển hình trên IDN (30–50%) nằm ở T_mode ≈ 4–6 phút, đúng bằng độ phân giải
của log 5 phút. r còn giảm khi μ·κ tăng quá 1000, nên ngưỡng thật còn dịch lên một chút. Vì
vậy nguồn hiện có **không phân định được** (iii) thuộc vùng nào. Ngoài ra τ ≈ h, nên telemetry "tươi" trong SWAN đã cũ
bằng cả horizon. Ở ρ + a/μ < 1, stake của backlog cost gần như bằng 0, khác hẳn mục tiêu của SWAN (§4).

**Bổ sung đợt 3.** RGK03 và P07 không cho T_mode dưới 5 phút, nhưng cho biết cấu trúc ở trên 5 phút:
- Phần lớn biến động là xu hướng và chu kỳ ngày/tuần, dự đoán được (RGK03 §2.2/PDF3; P07 App. A/PDF18: regression từ
  1 giờ trước dự đoán được 5 phút sau).
- Phần dư ngẫu nhiên có độ lệch chuẩn tương đối √(a/m), khoảng 4–9%. Đây là AI-tính với m = 350 Mbps, là tham số mô
  phỏng của RGK03 §5.1, không phải số đo.

Với h = 5 phút, chu kỳ ngày gần như hằng trong một horizon và biết trước theo giờ. Nó giống một mode quan sát được hơn
là mode ẩn của ctmc-v1, nên **không** làm (iii) thành "vùng state" theo nghĩa telemetry tươi có giá trị. Ô (iii) vẫn
UNRESOLVED; mức lệch contract tăng thêm một điểm (mode có cấu trúc xác định).

### 3d. Khi thang burst chậm hơn (kịch bản đa thang, ILLUSTRATIVE)

Giả sử nền có thêm một thành phần chậm, mang tỷ lệ f phương sai, với thời gian mode T_slow. Khi đó T_int bị thành phần
chậm chi phối, xấp xỉ thô T_int ≈ f·(T_int/T_mode)(ρ)·T_slow. Với ρ = 0,8 và f = 0,1:

| T_slow | T_int (thành phần chậm) | h/T_int, h = 1 s | h/T_int, h = 5 s | Vùng của (ii) |
|---|---|---|---|---|
| 10 s | ≈ 9,6 s | 0,10 | 0,52 | **state** |
| 60 s | ≈ 57 s | 0,02 | 0,09 | **state** |
| 600 s | ≈ 570 s | 0,002 | 0,009 | **state** |

Tức là chỉ cần 10% phương sai nằm ở thang chục giây trở lên là (ii) đổi nhãn từ tiệm cận sang state.

Các nguồn đã đọc theo hai hướng:
- **Có thành phần chậm.**
  - LTWW94: 360.000 quan sát 10 ms trong một giờ (§4.1/PDF7); IDC tăng qua nhiều thang (§5.2/Fig. 8), ở LAN lịch sử.
  - RZB15: demand có chu kỳ ngày và tuần (§4.1/PDF5). Theo Benson, dẫn lại ở §2/PDF3, traffic không dự đoán được từ
    150 s trở lên. Với Hadoop (không load balance), 90% flow ở giữa lệch kích thước trung vị của chúng hơn sáu bậc độ lớn, trong cùng
    phép đo theo giây (§5.2/PDF10).
- **Ổn định ở thang giây với dịch vụ Frontend.** Rate Web/cache theo rack nằm trong hệ số 2 so với trung vị ở khoảng 90%
  số giây; flow trung vị đổi > 20% ở 45% số giây (RZB15 §5.2/PDF9–10).

Không nguồn nào cho f và T_slow theo nghĩa phương sai của tải đầu vào một path. Công thức xấp xỉ trên chưa được kiểm
trong model có hai thang; đó là việc của held-out L7.3 Phần 2.

### 3e. (ii) khi lấy thành phần thang giây của MicroTE làm mode (ILLUSTRATIVE)

BAAZ11 §4.1.1/PDF5 cho run-length ổn định của traffic cặp ToR là 1,5–5 s. Nếu coi đó là T_mode,phys (μ·κ rất lớn, dùng
cột fluid) thì:

| ρ (a/μ) | T_int | h/T_int, h = 1 s (MicroTE) | h/T_int, h = 5 s (Hedera) | τ/T_int, τ ≈ 0,6–0,7 s | Vùng |
|---|---|---|---|---|---|
| 0,6 (0,6) | 3,8–13 s | 0,08–0,26 | 0,40–1,3 | 0,05–0,19 | state (Hedera: state–chuyển tiếp) |
| 0,8 (0,6) | 14–48 s | 0,02–0,07 | 0,10–0,35 | 0,01–0,05 | state |
| 0,9 (0,6) | 56–190 s | 0,005–0,02 | 0,03–0,09 | ≤ 0,01 | state |
| 0,3 (0,3) | 0,19–0,62 s | 1,6–5,4 | 8,1–27 | 0,97–3,8 | chuyển tiếp (Hedera: tiệm cận) |
| 0,5 (0,3) | 0,25–0,82 s | 1,2–4,1 | 6,1–20 | 0,73–2,9 | chuyển tiếp (Hedera: tiệm cận) |

Hai dòng a/μ = 0,3 dùng cột μ·κ = 1000. Tỷ số còn giảm khi μ·κ tăng, nên h/T_int thật còn lớn hơn. Ở hai dòng này stake
backlog ≈ 0 (§1).

Như vậy, với cùng một use case (ii):
- coi microburst là mode thì ra **tiệm cận** (§3a);
- coi thành phần thang giây là mode, ở tải cao, thì ra **state** (bảng trên);
- ở tải thấp thì ra **chuyển tiếp hoặc tiệm cận**, nhưng stake gần 0.

Nhãn phụ thuộc vào việc thành phần nào chiếm phương sai, và vào ρ. Đây đúng là câu hỏi hai thang của Phần 2.

Giới hạn của phép quy đổi này:
- Run-length dưới ngưỡng 20% không phải thời gian lưu exponential.
- Top 100 cặp ToR không phải tải của một path.
- MicroTE không cho ρ, và 35% traffic dự đoán được là tỷ lệ traffic, không phải tỷ lệ phương sai f.

## 4. Mối đe dọa realism

| Mối đe dọa | Nguồn hoặc UNSOURCED | Ảnh hưởng tới nhãn vùng |
|---|---|---|
| Burst đa thang / self-similar | LTWW94 §4–5/PDF7–8, 12 (LAN 1989–92); BAM10 §5.2/PDF6–7 (ON/OFF lognormal/Weibull); ZLK17 §5.2/PDF4 (inter-burst không exponential); RZB15 §2/PDF3, §4.1/PDF5 (≥ 150 s, chu kỳ ngày); RZB15 §6.2/PDF12 (Hadoop không on/off ở 15/100 ms); BAAZ11 §4.1.1/PDF5 (thành phần ổn định 1,5–5 s); BAM10 §6.4/PDF10–11 và RGK03 §2.2/PDF3 (chu kỳ ngày/tuần) | Có thể đổi (ii) từ tiệm cận sang state (§3d, §3e) |
| Tải không ngoại sinh | SWAN điều khiển rate của background traffic (HKM13 §3–4.2/PDF4–6). TCP feedback vẫn **UNSOURCED**; AED14 §3.6 chỉ nói lọc burst dưới-RTT của TCP | Nền không còn là MMPP ngoại sinh; plant khác contract |
| Mục tiêu khác backlog cost | CONGA: min-max congestion trên path với metric rate 3 bit (AED14 §3.2/PDF5). SWAN: throughput/fairness dưới capacity (HKM13 §4.2) | Nhãn vùng chỉ nói về dạng regret của ctmc-v1, không về mục tiêu của hệ thật |
| Tải thấp | RZB15 §4.1/PDF5 (trung bình 1 phút < 1%, 99% link < 10%); HKM13 §2/PDF2 (30–50%) | Ở ρ + a/μ < 1, stake backlog ≈ 0; tải trung bình dài không phải ρ của một mode |
| Dự đoán heavy hitter gần ngẫu nhiên | RZB15 §5.3/PDF11 (≈ 50% tiếp tục ở khoảng sau; 5-tuple < 10–15%) | Ủng hộ "thông tin per-flow mất giá trị sau một khoảng" ở thang ms; không cho T_int của tổng tải |
| Nhiều path / topology | ZLK17 §6.1/PDF5 (uplink 40/100 Gb/s có load balancing); AED14 §5.1/PDF6 (2 leaf × 2 spine); NDT1 §IV-B (25 node synthetic) | Hai path rời là trừu tượng hóa |
| Buffer hữu hạn | ZLK17 §6.4/PDF7 (shared buffer cấp phát động, chỉ normalized) | Không có kích thước tuyệt đối để quy B_t |
| Trễ actuation | Planck §7.2/Fig. 16 (qua T00); KPKC18 §4.1/Table 2 (250/400 ms; đuôi 22 s và 4 phút); BAAZ11 §7.3.2/PDF11 (40–150 ms); HKM13 §6.6/PDF11 (22 s, data plane 600 ms); NDT: HHZ26, ZBEK26 (0,17–0,2 s mỗi yêu cầu hoặc lần đánh giá) | Cộng vào τ hiệu dụng; khác định nghĩa; đuôi dài có thể làm τ ≫ trung bình |
| Mode quan sát được (S1 oracle) | Planck đo rate, không backlog (T00); CONGA đo rate lọc với τ, không quan sát mode (AED14 §3.2); D22 L7.1 cho thấy harm đã có với backlog-only | Giảm, nhưng chỉ trong ctmc-v1 |
| Mode có cấu trúc xác định (chu kỳ ngày/tuần) | RGK03 §2.2/PDF3 (m(t) gồm trend + chu kỳ, phần "predictable"); P07 App. A/PDF18 (regression 1 giờ dự đoán 5 phút sau); BAM10 §6.4 | Thành phần chậm của WAN và DC không phải mode Markov ẩn; ctmc-v1 không có trục "biết giờ là biết mode" |

## 5. Kết luận tạm (AI, theo ủy quyền; cập nhật 04/11/2026; chưa có tác giả đọc)

- **(i) Flowlet LB.** Với T_mode mượn từ microburst, (i) ở vùng state hoặc chuyển tiếp, và τ cỡ T_int. Đây là vùng mà
  trong ctmc-v1 state tươi có giá trị. Điều này nhất quán với việc CONGA dùng state tươi ở thang RTT, nhưng **không phải
  validation**:
  - metric, mục tiêu và h đều khác contract;
  - T_mode không đo cùng định nghĩa.
- **(ii) DC TE ở thang giây.** Sau đợt 3, h và τ đã có nguồn primary (BAAZ11: h = 1 s, τ_eff ≈ 0,6–0,7 s). Nhãn vẫn
  **không bền**, và bây giờ biết rõ vì sao:
  - Nếu chỉ có microburst: tiệm cận.
  - Nếu thành phần thang giây (BAAZ11: ổn định 1,5–5 s, khoảng 35% traffic) là mode: state ở ρ ≥ 0,6. Ở tải thấp thì
    chuyển tiếp, nhưng stake ≈ 0 (§3e).
  - f (tỷ lệ phương sai) vẫn UNSOURCED. Câu "≥ 150 s không dự đoán được" vẫn là dẫn lại hai bước.
- **(iii) WAN TE.** Vẫn **UNRESOLVED**:
  - Dưới 5 phút không có số đo.
  - Trên 5 phút, phần lớn biến động là chu kỳ dự đoán được (RGK03, P07). Đó là mode có cấu trúc xác định, khác giả định
    mode ẩn của ctmc-v1.
  - Plant khác contract nhiều nhất: tải elastic bị điều khiển, mục tiêu là throughput, mode biết theo giờ.
- **(iv) NDT what-if.** h vẫn UNSOURCED. Bốn paper cũ chỉ cho phần NDT cộng vào τ: từ vài ms (cập nhật twin) tới
  0,2–1 s (đồng bộ, đánh giá), có thể tới cỡ trăm giây nếu search tuần tự (AI-tính). Cách đọc hợp lý: NDT what-if
  **không phải một use case riêng** mà là bộ ra quyết định gắn vào (ii), (iii) hoặc khôi phục sự cố. Vùng của nó là vùng
  của vòng nền, với τ lớn hơn.
- **Câu được phép viết** vẫn giữ: "trong ctmc-v1, vùng phụ thuộc h/T_int; T_int thật bị chi phối bởi thành phần burst
  chậm nhất còn đáng kể, nên nhãn vùng của một use case cần số đo đa thang". Câu kiểu "TE ở vùng tiệm cận" hay
  "flowlet LB ở vùng state" **chưa được phép** viết như kết quả. Chỉ được viết như minh họa có điều kiện, kèm giả định
  T_mode.
- **Ưu tiên bằng chứng tiếp theo.**
  1. Phân rã phương sai tải theo thang (f, T_slow) cho DC hiện đại và WAN. Ứng viên chưa có: Kandula'09 và Benson
     WREN'09 (nguồn gốc câu 150 s), Ghabashneh'22, Lakhina'04.
  2. Thời lượng flowlet hoặc rate từng flow của DC (ứng viên LetFlow, metadata-only).
  3. Thời gian giữ quyết định của một vòng NDT what-if thật (chưa có ứng viên).
- Phần 2 (held-out hai thang, 4 mode) là nơi kiểm công thức ở §3d. Thẻ của Phần 2 do tác giả viết.

## 6. Nguồn của đợt 2 và 3

| # | Nguồn | ID (Crossref, kiểm 03/11/2026) | Duyệt | PDF (ngoài Git) | Mức đọc | Note |
|---|---|---|---|---|---|---|
| 1 | Hong et al., SWAN, SIGCOMM 2013, tr. 15–26 | DOI 10.1145/2486001.2486012 | AI-delegated | Trang hội nghị, 12 tr., sha256 99bb9406a528… | AI-T | [HKM13](../literature/papers/HKM13.md) |
| 2 | Alizadeh et al., CONGA, SIGCOMM 2014, tr. 503–514 | DOI 10.1145/2619239.2626316 | AI-delegated | Trang tác giả, 12 tr., sha256 b0a6e69eaa00… | AI-T | [AED14](../literature/papers/AED14.md) |
| 3 | Roy et al., Inside the Social Network's (Datacenter) Network, SIGCOMM 2015, tr. 123–137 | DOI 10.1145/2785956.2787472 | AI-delegated | Trang tác giả, 15 tr., sha256 d95df8228cb8… | AI-T | [RZB15](../literature/papers/RZB15.md) |

**Đợt 3 (04/11/2026).** Tác giả tự tải; AI đọc AI-T.

| # | Nguồn | ID | Bản đọc | Note |
|---|---|---|---|---|
| 4 | Benson et al., MicroTE, CoNEXT 2011, tr. 1–12 | DOI 10.1145/2079296.2079304 | VoR ACM, sha256 c5bc8bdb75f7… | [BAAZ11](../literature/papers/BAAZ11.md) |
| 5 | Roughan et al., backbone traffic variability (IMW 2002 / ITC 2003) | DOI 10.1145/637201.637213; 10.1016/s1388-3437(03)80183-x | Bản tác giả của bản ITC, sha256 18be6ebc95b3… | [RGK03](../literature/papers/RGK03.md) |
| 6 | Kuźniar et al., Computer Networks 136 (2018) | DOI 10.1016/j.comnet.2018.02.014 | Accepted manuscript, sha256 6438138d8460… | [KPKC18](../literature/papers/KPKC18.md) |
| 1′ | SWAN, bản ACM | DOI 10.1145/2486001.2486012 | VoR, sha256 104dfbe99511…, trùng chữ bản đã đọc | [HKM13](../literature/papers/HKM13.md) |
| 7–10 | Paper NDT cũ của tác giả: ZBEK26, VGC23, HHZ26, AAA25 | xem note | Author version / AM / in press / arXiv | [NDT_timing_L73](../literature/papers/NDT_timing_L73.md) |

Tác giả chưa tải Ghabashneh'22 (DOI 10.1145/3517745.3561430) và các bản chính thức của CONGA, RZB15, NDT1, Planck.

Ghi chú về nguồn:
- B4 (DOI 10.1145/2486001.2486019) không dùng và vẫn là metadata-only.
- Chưa thêm ba nguồn vào `papers/data/catalog.json` và Excel trên `main`; nhánh này chỉ có note và log.
- Tác giả tự đọc: chưa có xác nhận cho cả ba.
- Search log ở [L7.3-R1 và L7.3-R2](../literature/search_log.md).
