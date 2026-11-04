# L7.4 — Bảng đe dọa (threats to validity)

Doan Van Tai — **AI (Claude) soạn theo ủy quyền** (04/11/2026). Mỗi dòng ghi: đe dọa, đã xử lý chưa, xử lý bằng gì, hoặc
ghi là giới hạn. Claim C1–C7 xem [CLAIMS_EVIDENCE](CLAIMS_EVIDENCE.md).

**Trạng thái:** ✅ đã xử lý · ◐ xử lý một phần · ❌ chưa xử lý (ghi là giới hạn) · 🔄 đang xử lý.

## 1. Internal validity (kết luận có đúng trong model không)

| # | Đe dọa | Trạng thái | Xử lý / giới hạn |
|---|---|---|---|
| I1 | Thẻ dự đoán do AI soạn và AI chạy; tác giả chưa tự viết dự đoán nào | ❌ | Ghi rõ "test theo thẻ AI soạn". G-level giữ G1. Thẻ τ (L7.5) mentor khuyên là thẻ của tác giả |
| I2 | Thẻ L7.2, L7.3 khóa không qua mentor review | ◐ | Khóa có hash trước truth (`locks_l72.json`, `locks_l73.json`). Review chỉ còn hồi cứu; mentor đã chỉ 2 lỗi thiết kế thẻ L7.3 (L73-3 không phân biệt; L73-4 thiếu n) |
| I3 | Exposure: số zero-fit và một phần truth τ = 1 đã thấy trước khi viết thẻ | ◐ | Được phép theo thiết kế (zero-fit không chứa truth). Các tuple cũ ghi rõ trong case list (`old`, `seen`). Bridge viết sau khi thấy M0-only và fluid (SUMMARY §8) |
| I4 | Forking paths: mốc vùng đổi từ 1/4–7 sang 0,3/3 (AI quyết thay tác giả) | ◐ | Quyết định ghi trong `notes/realism/zone_thresholds_L73.md` trước truth L7.3. Không đổi sau khi mở |
| I5 | Bug evaluator | ✅ | Control bắt được 2 lỗi trước khi khóa: hòa M0 chính xác (L7.1) và luật bão hòa T ≈ h (L7.3 attempt01). Cả hai sửa trước truth và ghi lịch sử attempt |
| I6 | Đa so sánh: nhiều dự đoán, đếm PASS/FAIL không hiệu chỉnh | ❌ | Kết quả là tính chính xác (không lấy mẫu), nên không có p-value để hiệu chỉnh. Nhưng việc chọn ngưỡng và khoảng vẫn là forking. Báo cáo đủ cả FAIL (AS-R1b, BR-R2/R3/R4b/R4c, D-R5, L72-2, L72-8(a)) |
| I7 | Cơ chế C5 chỉ có mô tả sau mở | ❌ | Ghi là giả thuyết. Test liều–đáp ứng theo τ đang chuẩn bị (L7.5 Stage 0, chưa truth) |
| I8 | Dự đoán "toán" làm phồng số PASS | ◐ | Nhãn "toán" tách riêng trong mọi bảng; không tính vào số dự đoán rủi ro |

## 2. Construct validity (đo có đúng thứ muốn đo không)

| # | Đe dọa | Trạng thái | Xử lý / giới hạn |
|---|---|---|---|
| K1 | z = G_S/C_ref (% C_ref) phụ thuộc mẫu số; C_ref tăng theo h | ◐ | Báo cả G_S tuyệt đối (packet·s) ở T11 §7. Ngưỡng ±0,5% và 0,1 pp đều là quy ước |
| K2 | M0 là một lớp twin cụ thể (rollout trung bình có điều kiện, biết mode) | ❌ | Twin NDT thật có thể là công thức queue, mô phỏng hoặc ML. Claim chỉ cho twin mean-value mù horizon. KO và hybrid là biến thể đã kiểm |
| K3 | S1 gồm mode oracle, không khả thi | ✅ | D22: state tươi chỉ backlog đã đủ gây harm (C4) |
| K4 | Một action giữ suốt h, không quyết định lại | ❌ | Giới hạn chính. Vòng kín (quyết định lặp) chưa mô hình. Mentor xếp là mở rộng lớn có thể bị hỏi |
| K5 | P1: hệ ở phân phối dừng của Stay tại t0 | ❌ | Giới hạn. Khởi đầu ngoài dừng (sau sự kiện) chưa kiểm |
| K6 | "Harm" định nghĩa bằng ngưỡng −0,5% C_ref | ◐ | Báo cả −0,1% ở các phép đo cơ chế; ngưỡng ghi trong thẻ trước truth |
| K7 | c_sw = 0 hầu hết | ◐ | Stage F (c_sw > 0): harm biến mất ở c* (F-R2). Claim C3 chỉ ở c_sw = 0 |
| K8 | Tuổi telemetry τ cố định 1 s | 🔄 | L7.5 Stage 0 (zero-fit, chưa truth). Mentor coi đây là lỗ hổng lớn nhất |

## 3. External validity (có chuyển sang mạng thật không)

| # | Đe dọa | Trạng thái | Xử lý / giới hạn |
|---|---|---|---|
| E1 | Hai path, MMPP/M/1, μ = 10 | ❌ | Giới hạn. Nhiều path, link chung chưa mô hình |
| E2 | Hai mode đối xứng; ctmc-v2 hai thang đối xứng | ◐ | Biên độ a/μ ∈ {0,3; 0,6; 0,75} và hai thang (T_s/T_f ≤ 100) đã kiểm. Burst bất đối xứng (GZL22: T_on ≈ 2 ms, T_off ≈ 133 ms) chưa |
| E3 | Tải ≤ 9,75/μ, κ ≤ 5, N ≤ 3000 (D22) | ❌ | Góc tải nặng/κ lớn ngoài miền, ghi số case bị loại theo trần CPU |
| E4 | Realism: use case DC minh họa; WAN dưới 5 phút UNRESOLVED; h của NDT không có nguồn | ◐ | realism v2 ghi vùng cho từng use case kèm nguồn. Mục 3 của mentor (h của NDT) đóng bằng câu "NDT dùng h của vòng nó phục vụ" ([closures](L7_4_closures.md)) |
| E5 | Traffic không-Markov (heavy tail, chu kỳ ngày) | ❌ | LPC04: 70–92% phương sai ở bin 5–10 phút là chu kỳ biết trước, không phải mode ẩn. Không mô hình |
| E6 | Một implementation evaluator | ◐ | Control độc lập: MC đầu-cuối (CRN), tích phân số cho M0, matrix-geometric, N → 2N. Chưa có implementation thứ hai |

## 4. Thống kê và số học

| # | Đe dọa | Trạng thái | Xử lý / giới hạn |
|---|---|---|---|
| S1 | Tỷ lệ "x% regime" phụ thuộc mật độ thiết kế Sobol | ❌ | Ghi rõ là tỷ lệ trong thiết kế, không phải tần suất ngoài đời |
| S2 | Cắt N (đuôi 1e−13) | ✅ | V5 N → 2N (thay đổi ≤ 1,2e−10 pp); control (d) ở L7.3 |
| S3 | Hai máy lệch bit cuối; quyết định gần hòa bị lật | ✅ | Quy tắc một máy (GCP `dt4n-research-01`) cho mọi số chấm L7.3 trở đi. L7.2: đổi phiên bản 63 case cho verdict y hệt |
| S4 | Case vượt trần CPU (UNRESOLVED) | ◐ | Luật UNRESOLVED > 10% → INCONCLUSIVE, không chạy lại với trần khác (a = 7,5: 45/827) |
| S5 | Cỡ mẫu mỏng | ◐ | L73-4 n = 24. Bài học: ước lượng n từ zero-fit trước khi khóa (L7.5 Stage 0 mục 5) |
| S6 | Kết quả sát ngưỡng | ❌ | AS-R5a 90,9%, BR-R2 79,6%, L72-4 0,055: báo nguyên, không làm tròn thành PASS/FAIL khác |
| S7 | Phép kiểm MC không phân giải sự kiện hiếm | ◐ | L7.5 control (c): khi se = 0 thì báo "MC không phân giải" và chỉ chấp nhận khi \|exact\| ≤ 1e−4·C_ref (sửa trước lượt chính thức) |
| S8 | Ma trận chuyển dày/thưa và expm_multiply | ◐ | L7.1 V10 (posterior) đạt. L7.5 control (b): expm_multiply so với expm dày, lệch ≤ 7e−15 ở lần chạy thử local; lượt chính thức chạy trên GCP |

## 5. Ba đe dọa reviewer dễ hỏi nhất (AI đề xuất thứ tự)

1. **K8 τ cố định** (đang xử lý, L7.5).
2. **K4 một quyết định, không vòng kín.** Chỉ mở rộng nếu bảng novelty cho thấy thiếu nó là bị từ chối.
3. **K2 lớp twin hẹp.** Cần câu định vị rõ: claim cho twin mean-value mù horizon, không cho mọi twin.

Chưa chọn mở rộng lớn nào; mentor khuyên đợi bảng này và kết quả novelty.
