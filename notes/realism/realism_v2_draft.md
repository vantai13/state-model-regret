# Realism v2 — bản nháp (L7.3 Phần 1)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền L7.3 Phần 1** (03/11/2026), nhánh `explore/realism-l73` từ
`explore/ctmc-phase7`. Không phải author-self, không sửa [envelope v1](envelope_v1.json), không chạy truth mới.
Đợt 1 chỉ dùng nguồn đã có trong thư viện (mức đọc ghi theo note gốc; **không** đọc lại primary trong phiên này).
Ba nguồn mới chỉ được đề xuất ở §6, chờ tác giả duyệt.

## 1. Câu hỏi và cách quy đổi

Với mỗi bối cảnh: các tỷ số h/T_int, τ/T_int, tải ρ, a/μ và μ·κ rơi vào vùng nào của ctmc-v1?

- **Vùng state:** h ≲ T_int, telemetry tươi có giá trị (M0 tươi thắng Static; Stage E, L7.1).
- **Vùng chuyển tiếp:** T_int < h < 4·T_int, cần model stochastic (bản đồ twin Stage E).
- **Vùng tiệm cận:** h ≳ 4–7·T_int, planner dừng đủ dùng (L72-3 đạt ở a = 3 và a = 7,5) và twin mean-value mù horizon
  bị telemetry tươi làm hại (công thức zero-fit đúng tới 0,1 pp từ (4; 7]·T_int ở a = 3).

**Quy đổi.** T_int,phys = (T_int/T_mode)(ρ, μ·κ, a/μ) × T_mode,phys, với μ·κ = số packet được phục vụ trong một thời gian
mode. Ở 10 Gb/s, gói 1.500 byte, μ ≈ 833.333 packet/s. Tỷ số T_int/T_mode lấy từ CTMC ctmc-v1 ở a/μ = 0,6 (đại lượng dừng,
không truth); khi μ·κ ≥ 50 nó gần giới hạn fluid.

| ρ | μ·κ = 1 | 10 | 50 | 200 (≈ fluid) |
|---|---:|---:|---:|---:|
| 0,60 | 13,1 | 3,69 | 2,71 | 2,52 |
| 0,70 | 23,9 | 6,44 | 4,71 | 4,37 |
| 0,80 | 55,2 | 14,2 | 10,3 | 9,56 |
| 0,85 | 99,7 | 25,1 | 18,1 | 16,8 |
| 0,90 | 228 | 56,1 | 40,4 | 37,4 |
| 0,95 | 928 | 224 | 160 | 148 |

Bảng phụ thuộc a/μ = 0,6 và giả định hai mode đối xứng exponential; đổi biên độ hoặc hình dạng burst sẽ đổi bảng.

## 2. Bảng use case (mỗi ô có nguồn hoặc UNSOURCED)

| Bối cảnh | Horizon h | Tuổi τ | Thang burst | Tải | Nguồn và giới hạn định nghĩa |
|---|---|---|---|---|---|
| (i) Flowlet LB trong DC | **UNSOURCED** | **UNSOURCED** (ứng viên: CONGA "react to congestion in microseconds", chỉ là abstract Crossref, chưa đọc) | p90 hot-burst < 200 µs, Web 50 µs (ZLK17 §5.1/PDF4) | **UNSOURCED** | Hot = egress > 50% trong 25 µs, không phải thời gian mode của input (ZLK17 note) |
| (ii) TE/lập lịch flow DC ở thang giây | Chu kỳ vòng: MicroTE 1 s, Hedera 5 s (T00, trích Planck §8 và Hedera §5.4) | Polling Hedera 5 s → τ_eff ≈ P/2 + L + W/2 ≈ 5 s nếu W = P (T00); counter OpenFlow 75–200 ms (Planck §2.2–2.3/Table 1, T00) | như (i), cộng đa thang (LTWW94 §4–5/PDF7–8, 12; BAM10 ON/OFF lognormal/Weibull §5.2/PDF6–7) | Hotspot ≥ 70% theo cửa sổ 5 phút (BAM10 §6.2–6.3/PDF9) là định nghĩa, không phải dải | Chu kỳ vòng ≠ thời gian giữ quyết định; Hedera 5 s do giới hạn đọc register NetFPGA (T00) |
| (iii) TE trên WAN | **UNSOURCED** (ứng viên: SWAN, B4) | **UNSOURCED** | **UNSOURCED** | **UNSOURCED** (B4 abstract: "near 100% utilization", chưa đọc) | — |
| (iv) Vòng what-if của NDT | **UNSOURCED** | **UNSOURCED** | **UNSOURCED** | **UNSOURCED** | NDT1 §IV-B/PDF5: optimizer đổi trọng số OSPF và chọn routing theo delay **dự đoán** (twin cho KPI dừng); cho biết lớp twin, không cho h, τ |
| Trễ actuation (chung) | — | Planck ARP 2,5–3,5 ms / OpenFlow 4–9 ms (§7.2/Fig.16); Kuźniar gap 250/400 ms (§4.1/Table 2), qua T00 | — | — | Hai khoảng đo khác định nghĩa; không cộng máy móc (T00) |

## 3. Vùng (ILLUSTRATIVE — không phải calibration)

Chỉ (ii) có đủ ô để tính minh họa. Giả định minh họa: 10 Gb/s, T_mode = 50–200 µs (mượn từ hot-burst ZLK17, khác định
nghĩa), nên μ·κ ≈ 42–167 (gần fluid).

| | ρ = 0,6 | ρ = 0,8 | ρ = 0,9 | ρ = 0,95 |
|---|---|---|---|---|
| T_int (microburst-only) | 0,13–0,50 ms | 0,52–1,9 ms | 2,0–7,5 ms | 8,0–30 ms |
| h/T_int, h = 1 s (MicroTE) | 2.000–7.700 | 520–1.900 | 130–500 | 33–125 |
| h/T_int, h = 5 s (Hedera) | 10.000–38.000 | 2.600–9.600 | 670–2.500 | 170–630 |
| τ/T_int, τ ≈ 1–5 s | ≫ 1 | ≫ 1 | ≫ 1 | ≫ 1 |
| Vùng | tiệm cận | tiệm cận | tiệm cận | tiệm cận |

Với (i): nếu h ≈ thời gian một flowlet cỡ 0,1–1 ms (UNSOURCED) và τ cỡ µs, thì h/T_int ≈ 0,003–8 và τ/T_int ≪ 1: vùng
state hoặc chuyển tiếp. Đây chỉ là minh họa cho chiều phụ thuộc, không phải nhãn có nguồn.

**Khi thang burst chậm hơn (kịch bản đa thang, ILLUSTRATIVE).** Nếu nền có thêm một thành phần chậm, mang tỷ lệ f phương sai
với thời gian mode T_slow, thì T_int bị thành phần chậm chi phối: xấp xỉ thô T_int ≈ f·(T_int/T_mode)(ρ)·T_slow. Với
ρ = 0,8, f = 0,1:

| T_slow | T_int (thành phần chậm) | h/T_int, h = 1 s | h/T_int, h = 5 s | Vùng của (ii) |
|---|---|---|---|---|
| 10 s | ≈ 9,6 s | 0,10 | 0,52 | **state** |
| 60 s | ≈ 57 s | 0,02 | 0,09 | **state** |
| 600 s | ≈ 570 s | 0,002 | 0,009 | **state** |

Tức là chỉ cần 10% phương sai nằm ở thang chục giây trở lên là (ii) đổi nhãn từ tiệm cận sang state. LTWW94 (§4.1/PDF7:
360.000 quan sát 10 ms trong một giờ; §5.2/Fig.8: IDC tăng qua nhiều thang) cho thấy loại cấu trúc này tồn tại ở LAN
lịch sử; không có nguồn trong thư viện cho f và T_slow của DC hay WAN hiện đại. Công thức xấp xỉ trên chưa được kiểm
trong model có hai thang; đó là việc của held-out L7.3 Phần 2.

## 4. Mối đe dọa realism

| Mối đe dọa | Nguồn hoặc UNSOURCED | Ảnh hưởng tới nhãn vùng |
|---|---|---|
| Burst đa thang / self-similar | LTWW94 §4–5/PDF7–8,12 (LAN 1989–92); BAM10 §5.2/PDF6–7 (ON/OFF lognormal/Weibull); ZLK17 §5.2/PDF4 (inter-burst không exponential) | Có thể đổi (ii) từ tiệm cận sang state (§3) |
| TCP phản hồi (tải offered phụ thuộc congestion) | **UNSOURCED** trong thư viện | Nền không còn ngoại sinh; plant khác contract |
| Nhiều path / topology | ZLK17 §6.1/PDF5 (uplink 40/100 Gb/s có load balancing); NDT1 §IV-B (25 node synthetic) | Hai path rời là trừu tượng hóa |
| Buffer hữu hạn | ZLK17 §6.4/PDF7 (shared buffer cấp phát động, chỉ normalized) | Không có kích thước tuyệt đối để quy B_t |
| Trễ actuation | Planck §7.2/Fig.16; Kuźniar §4.1/Table 2 (qua T00) | Cộng vào τ hiệu dụng; khác định nghĩa |
| Mode quan sát được (S1 oracle) | Planck đo rate, không backlog (T00); D22 L7.1 cho thấy harm đã có với backlog-only | Giảm, nhưng chỉ trong ctmc-v1 |

## 5. Kết luận tạm (AI, chưa có duyệt nguồn mới)

- Không ô nào của (i), (iii), (iv) có đủ nguồn cùng định nghĩa để gán vùng. Chỉ (ii) có h và τ (từ chu kỳ vòng và polling).
  Theo microburst-only, nó rơi vào vùng tiệm cận, nhưng nhãn đó **không bền** trước kịch bản đa thang.
- Câu thực dụng kiểu "TE ở vùng tiệm cận" **chưa được phép** viết trong paper. Câu được phép: "trong ctmc-v1, vùng phụ thuộc
  h/T_int; T_int thật bị chi phối bởi thành phần burst chậm nhất còn đáng kể, nên nhãn vùng của một use case cần số đo đa
  thang".
- Ưu tiên bằng chứng: (1) chu kỳ TE trên WAN và thời gian giữ cấu hình; (2) burst đa thang ở DC hiện đại; (3) h và τ của flowlet LB.

## 6. Đề xuất 3 nguồn mới (chờ duyệt; metadata-only)

| # | Nguồn | ID (Crossref, kiểm 03/11/2026) | Ô cần lấp | Lý do |
|---|---|---|---|---|
| 1 | Hong et al., *Achieving high utilization with software-driven WAN* (SWAN), SIGCOMM 2013, tr. 15–26 | DOI 10.1145/2486001.2486012 | (iii) h, τ, trễ cập nhật | Abstract: "frequently re-configuring the network's data plane to match current traffic demand" và congestion trong lúc cập nhật; có thể cho chu kỳ TE và thời gian giữ cấu hình |
| 2 | Alizadeh et al., *CONGA*, SIGCOMM 2014, tr. 503–514 | DOI 10.1145/2619239.2626316 | (i) h (flowlet), τ (feedback) | Abstract: flowlet, phản hồi congestion trong microsecond; là ví dụ chuẩn của load balancing dùng state tươi |
| 3 | Roy et al., *Inside the Social Network's (Datacenter) Network*, SIGCOMM 2015, tr. 123–137 | DOI 10.1145/2785956.2787472 | thang burst đa thang, tính ổn định/dự đoán được của traffic DC | Abstract: "locality, stability, and predictability of network traffic" và hệ quả cho TE |

Phương án thay: B4 (DOI 10.1145/2486001.2486019) thay SWAN nếu tác giả muốn nguồn có ba năm vận hành. Mức đọc hiện tại của
cả bốn: metadata-only (+ abstract Crossref của bản CCR). Chưa tải PDF, chưa tạo note nội dung.

**Dừng ở đây, chờ tác giả duyệt nguồn.** Search log: [L7.3-R1](../literature/search_log.md).
