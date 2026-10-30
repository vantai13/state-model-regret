# LESSON 4.2: Đọc bản đồ đúng cách

## Part 1/3: Bản đồ có bao nhiêu chiều thật?

### 0. Kiểm nguồn và điều chỉnh plan

L4.2 trong PHASE_4.md vẫn khớp với trạng thái hiện tại; tôi không thấy mâu thuẫn với Final Review hay các DL. Có ba điều chỉnh:

1. **Một phần L4.2 đã dạy ở L4.1 Part 2.** Đó là phép chứng minh Γ̄ ≥ −min(Ḡ_S, Ḡ_M) (Khái niệm 5) và toy T-C. Ở Part 2 của L4.2, tôi chỉ nhắc lại ngắn, rồi dành thời gian cho phần mới: cận này ràng buộc cách thiết kế card như thế nào.
2. **Bài "viết dự đoán trước" ở Bước 6 không còn mù nữa.** Plan muốn bạn đoán trước rằng lớp AB và C tách nhau theo trục nào. Nhưng kết quả (tách theo δ) đã nằm sẵn trong PHASE_4 §0.3 mục K9b, trong bảng sửa đổi dòng 8, và trong output recount tôi in ở L4.1 Part 3. Một dự đoán viết sau khi đã thấy đáp án thì không còn là dự đoán. Tôi đề xuất đổi Bước 6 thành "giải thích cơ chế ứng viên", và ghi vào forking log là "đã thấy trước". Nếu bạn muốn luyện dự đoán thật, ở Part 3 tôi sẽ đề xuất một lát cắt dữ liệu chưa ai xem.
3. **Câu "plant chỉ có năm chiều" đúng, nhưng có điều kiện.** Contract đã ghi điều này ở AS14, và ở dòng 224 có liệt kê sẵn các tọa độ không thứ nguyên. Plan chưa nêu đủ các điều kiện, nên tôi bổ sung ở §5.4.

**Những gì tôi đã tự kiểm cho Part 1:**
- 18 cặp tương đương theo age: cả 18 cùng lớp, lệch lớn nhất 0,201 pp.
- Cả 18 điểm trong hộp MV+A đều có Ḡ_M ≥ 1% (nhỏ nhất 1,33%).
- 148 dòng nằm trong khoảng 0,15 pp quanh một biên ±1.
- Recurrence và hàm cost lấy từ contract v1.3: `q_next = max(0, q + (r + managed − μ)δ)`, cost = δ·Σ(qA + qB).

**Map của L4.2:**

| Part | Nội dung | Khái niệm trong plan |
|---|---|---|
| **1 (bài này)** | Phân tích thứ nguyên (age không phải một chiều); biên độ là plant khác; lớp khác vùng | 1, 2, 3 |
| 2 | Ba toy: một kiểu lỗi của M0, ba câu chuyện; Ḡ_S\|M1 như EVPI; cận của Γ̄ ràng buộc thiết kế card | 4, 5, 6 |
| 3 | Tọa độ tổ chức δ; đọc hai hình của bản đồ; T07 addendum và golden test | 7, các bước thực hành |

---

### 1. Bạn đang ở đâu?

```text
PHASE 4 (không tính outcome CF nào)
  L4.1 Re-entry ✓ (học xong; thực thi chưa)
  L4.2 Đọc bản đồ đúng cách ← BẠN Ở ĐÂY (Part 1/3)
  L4.3 Audit dưới engine native
  L4.4 Baseline khoa học
  L4.5 Quyết định 0/1/2 card  ← L4.2 cung cấp "kính đọc" cho bước này
```

### 2. Part 1 trả lời câu hỏi gì?

> Bản đồ có bao nhiêu **núm thật sự độc lập**? Và một **nhãn lớp** khác một **vùng của card** ở chỗ nào?

### 3. Tại sao cần?

Ở L4.5 và L4.6 bạn sẽ viết claim dưới dạng "trong hộp tọa độ X thì Y". Nếu chọn sai tọa độ, hoặc đọc nhãn như vùng, claim sẽ sai ngay từ cách phát biểu. Ba ví dụ cụ thể:

- Bạn viết "giá trị của state tăng theo tuổi telemetry, một chiều mới của bài toán". Reviewer chỉ ra rằng đó chỉ là κ/τ và h/τ cùng giảm, tức bạn đang đếm một chiều hai lần.
- Bạn đề xuất một card về biên độ traffic nền. Nhưng biên độ là một plant khác hợp đồng, nên card đó vượt scope.
- Bạn vẽ hộp quanh các điểm có nhãn A, trong đó nhiều điểm chỉ vượt ngưỡng 1% một chút. Dưới engine native, chúng lật nhãn, và tỉ lệ thành công thật trong hộp thấp hơn bạn tưởng.

### 4. Liên hệ với Main RQ

```text
Tọa độ đúng ──► vùng card viết đúng chiều (L4.5–4.6) ──► Phase 5 kiểm đúng câu hỏi
            └─► Phase 8: câu hỏi realism trở nên chính xác
                ("có mạng thật nào mà mode kéo dài khoảng 0,2 × tuổi telemetry không?")
```

Liên hệ này gián tiếp: Part 1 không trả lời "differ" hay "interact". Nó quyết định bạn sẽ hỏi hai câu đó **trong hệ tọa độ nào**.

### 5. Prerequisite: ba ý toán nhỏ

- **Tỉ lệ thuận.** Nếu mọi chi phí cùng nhân một số k > 0, thì mọi tỉ số giữa chúng giữ nguyên, và mọi phép so sánh (cái nào lớn hơn) cũng giữ nguyên.
- **Thuần nhất dương của max(0, ·).** Với mọi c > 0: max(0, c·z) = c·max(0, z). Ví dụ: max(0, 2·(−3)) = 0 = 2·max(0, −3); max(0, 2·5) = 10 = 2·5. Đây là "luật" duy nhất cần dùng ở §6.
- **Ôn từ L4.1 Part 1 §5:** regime, bốn ô, sáu contrast, sáu lớp.

---

## 6. Khái niệm 1: phân tích thứ nguyên, và vì sao age không phải một chiều

### 6.1 Trực giác

Bạn quay phim một hàng đợi rồi chiếu chậm gấp đôi. Mọi chuyện xảy ra y hệt, chỉ chậm hơn. Mode ON kéo dài gấp đôi, horizon dài gấp đôi, telemetry cũ gấp đôi. Controller nào trong phim gốc chọn Switch thì trong phim chiếu chậm cũng chọn Switch.

### 6.2 Ví dụ networking nhỏ (lấy từ plan)

Path B nhận 12 packet/s, phục vụ 10 packet/s, bắt đầu rỗng. Backlog tăng 2 packet/s, nên q(t) = 2t.

```text
Chi phí tới h = 2 s:   ∫₀² 2t dt = 4 packet·s
Nhân thời gian ×2 (h = 4 s):  ∫₀⁴ 2t dt = 16 = 2² × 4
```

Backlog nhân 2, vì tích lũy lâu gấp đôi. Chi phí nhân 4, vì backlog nhân 2 **và** khoảng thời gian cũng nhân 2.

### 6.3 Vì sao điều này đúng trong engine của bạn: dẫn từng bước

**Câu hỏi.** Nếu nhân **mọi** đại lượng thời gian lên c lần, % contrast có đổi không?

**Các đại lượng thời gian:** độ dài slot δ, thời gian một mode κ, horizon h, tuổi telemetry τ. Các tốc độ (λ, μ, u, a) giữ nguyên.

**Bước 1: chuỗi mode không đổi luật.** Engine giữ nguyên mode với xác suất (1 + e^(−2δ/κ))/2 mỗi slot. Xác suất này chỉ phụ thuộc tỉ số δ/κ, mà nhân cả hai lên c thì tỉ số không đổi. Số slot của horizon (h/δ) và tuổi telemetry tính theo slot (τ/δ) cũng không đổi. Vậy dãy mode, đếm theo slot, có cùng luật xác suất như trước.

**Bước 2: backlog nhân c.** Giả sử ở slot k ta có q′_k = c·q_k. Khi đó:

```text
q′_{k+1} = max(0, q′_k + (r − μ)·cδ)
         = max(0, c·(q_k + (r − μ)·δ))
         = c·max(0, q_k + (r − μ)·δ)      ← thuần nhất dương
         = c·q_{k+1}
```

Theo quy nạp, đẳng thức đúng với mọi slot. Phân phối dừng ban đầu cũng co giãn theo đúng cách đó.

**Bước 3: chi phí nhân c².** cost′ = cδ·Σ c·q = c²·cost.

**Bước 4: quyết định không đổi.**
- Mọi J nhân c², nên mọi Δ nhân c², nên dấu của Δ không đổi.
- S0 thấy y′ = c·y, và niềm tin của nó co giãn theo cùng ánh xạ.
- M0 dùng mean rollout, tức cùng recurrence nhưng với tải trung bình, nên nó cũng thuần nhất và dự đoán của nó cũng nhân c².

Vậy cả bốn ô ra đúng các quyết định cũ. Mọi L̄ nhân c², nên **mọi Ḡ/C̄_ref giữ nguyên**.

**Kết luận** (chọn c = 1/a): (age a, κ, h) ≡ (age 1, κ/a, h/a).

**Tương tự cho tốc độ.** Nhân mọi tốc độ (λA, λB, u, μ, a) lên c thì backlog và chi phí đều nhân c, mọi tỉ số giữ nguyên. Phép chứng minh dùng đúng tính thuần nhất ấy.

**Đếm núm:**

```text
8 tham số thô:  5 tốc độ (λA, λB, u, μ, a)  +  3 thời gian (κ, h, τ)
− 2 "đơn vị":   một đơn vị tốc độ (μ), một đơn vị thời gian (τ)
= 6 chiều không thứ nguyên: λA/μ, λB/μ, u/μ, a/μ, κ/τ, h/τ
Contract khóa a/μ = 0,6  ⇒  còn 5 chiều thật
```

Nếu c_sw ≠ 0 thì có thêm chiều c_sw/(μτ²); contract dòng 224 đã ghi đúng như vậy.

### 6.4 ASSUMPTION: phép tương đương này cần những gì?

| Giả định | Nếu bị phá | Claim bị ảnh hưởng |
|---|---|---|
| **Plant fluid**: trong mỗi mode, tải là hằng số, không có nhiễu | Với packet Poisson, số packet trong một mode tỉ lệ với tốc độ × thời gian, nên độ nhiễu tương đối (cỡ 1/√N) đổi khi co giãn | "Age không phải một chiều" không còn đúng ở mức packet (packet DES ở Phase 7 có thể phá nó) |
| **Cost tuyến tính theo backlog** (∫q dt) | Một ngưỡng SLA cố định, ví dụ phạt khi delay > 50 ms, không co giãn theo | Phép ánh xạ vùng giữa các age |
| **Buffer vô hạn** (hoặc buffer co giãn cùng) | Buffer cố định cắt backlog, nên không còn thuần nhất | Như trên |
| **c_sw = 0** (hoặc c_sw co giãn theo μτ²) | Chi phí đổi đường cố định thì không nhân c² | Như trên |
| **δ cũng co giãn** | Pilot giữ δ = 1/120 s cố định, nên tương đương chỉ xấp xỉ | Sai lệch số học nhỏ; tôi kiểm: 18/18 cặp cùng lớp, lệch ≤ 0,201 pp |

Vì vậy contract AS14 ghi: "τ = 1 chỉ là mapping khi co toàn bộ times/q0/c_sw đúng".

### 6.5 Hệ quả cho nghiên cứu

1. **Map3age không phải "kiểm theo tuổi telemetry".** Nó chỉ thêm điểm vào mặt phẳng (κ/τ, h/τ) đã có. Câu số 5 ở L4.1 ("Ḡ_S|M1 tăng theo age") thực chất là đi dọc một tia về phía gốc tọa độ trong mặt phẳng này: κ/τ và h/τ cùng giảm.
2. **Mọi vùng của card nên viết ở age 1**, tức theo κ/τ và h/τ.
3. **Realism trở thành một câu hỏi chính xác.** Một claim ở κ/τ = 0,2 đúng cho "mode kéo dài 0,2 s với telemetry 1 s", và cũng đúng cho "burst 20 ms với telemetry 100 ms". Ở Phase 8, thứ cần tìm trong literature không phải "telemetry 1 s", mà là **tỉ số giữa thời gian một burst và tuổi telemetry** trong mạng thật.

---

## 7. Khái niệm 2: biên độ a/μ là chiều thật, nhưng thuộc một plant khác

Không phép đổi đơn vị nào xóa được a/μ, vì bản thân nó đã là tỉ số của hai tốc độ. Đổi biên độ tức là đổi độ "giật" của traffic nền.

**Ví dụ** với λB = 8, μ = 10:

```text
Biên độ ±6:  ON = 14 (quá tải +4),  OFF = 2
Biên độ ±4:  ON = 12 (quá tải +2),  OFF = 4
```

Mức quá tải trong mode ON giảm một nửa, nên backlog nhỏ hơn và C̄_ref nhỏ hơn. Tôi đã kiểm ở L4.1: trung vị C̄(±4)/C̄(±6) = 0,32. Vì thế mọi con số tính theo % "phồng" lên, trong khi Ḡ_M|S1 tính tuyệt đối chỉ tăng khoảng 15%.

Có một chi tiết cho thấy contract được thiết kế có chủ đích. Điều kiện hợp lệ λ ≥ a bảo đảm tốc độ ở mode OFF không âm. Với a = 6 thì λ ≥ 6, và đó là lý do lưới λ bắt đầu từ 6. Đổi biên độ là đổi cả miền tham số hợp lệ.

**Vì sao không làm card về biên độ.** Contract khóa a/μ = 0,6. Đổi biên độ nghĩa là cần namespace mới, numerics coverage mới và realism mới. Vai trò đúng của nó là ở Phase 7 (independent validation), như một **workload khác**, để hỏi pattern có sống sót khi đổi workload không. Đó là một phép thử khả năng khái quát (generalization), không phải một claim của Phase 5.

---

## 8. Khái niệm 3: lớp là công cụ đọc, không phải vùng

### 8.1 Trực giác

Tô màu bản đồ theo ngưỡng nhiệt độ giúp mắt nhìn ra vùng nóng, vùng lạnh. Nhưng đường ranh màu không phải biên giới quốc gia có luật riêng.

### 8.2 So sánh chính xác

| | **Lớp** (A, B, AB, C, D, J) | **Vùng Ω** của card |
|---|---|---|
| Là nhãn của | **Một** regime | **Một hộp** tọa độ thiết kế |
| Tính từ | Số pilot, ngưỡng ±1%, thứ tự ưu tiên (C xét trước) | Claim về **tỉ lệ** regime thỏa một điều kiện, theo một cách lấy mẫu (measure) đã khóa |
| Nhạy với | Sai số số học sát ngưỡng | Tỉ lệ thật p⁺ trong hộp; chịu được vài điểm trượt |
| Dùng để | Đọc, nhìn | Kiểm định |
| Ví dụ | X2065: lớp C | MV+A: "đa số regime có Ḡ_M ≥ 1%" |

### 8.3 Ví dụ: hộp MV+A

Tôi đã kiểm: hộp MV+A có 18 điểm discovery, gồm 11 điểm lớp C và 7 điểm lớp B. **Cả 18 đều có Ḡ_M ≥ 1%** (nhỏ nhất 1,33).

- **Card MV** chỉ claim Ḡ_M ≥ 1%, nên không mâu thuẫn gì với dữ liệu.
- **Câu chuyện "MV+A là vùng model thắng" thì sai.** Ở phần lớn hộp, sửa model có ích **và đồng thời** sửa state (khi model vẫn là M0) lại gây hại; Ḡ_S xuống tới −21,6%.

**Vì sao nhãn lớp giấu điều này.** Nhãn lớp nén sáu contrast xuống thành một chữ cái, theo một thứ tự ưu tiên. Một điểm có Ḡ_M = 13% vẫn bị dán nhãn C, chỉ vì Ḡ_S = −1,2% và luật xét C trước. Khi nén, thông tin bị mất.

### 8.4 Nhãn sát ngưỡng thì mong manh

Tôi đã đếm: 148 dòng nằm trong khoảng 0,15 pp quanh một biên ±1 của Ḡ_S hoặc Ḡ_M. Ở age 1, có 28/211 điểm lớp A với Ḡ_S < 1,15. Theo K6 (tôi chưa tự kiểm), engine native cho Ḡ_S thấp hơn pilot tới 0,136 pp, nên những điểm này có thể lật nhãn.

Hệ quả: "số điểm lớp A" là một con số mong manh. Claim về vùng dựa trên tỉ lệ cộng với một cận nhị thức, nên chịu được vài điểm lật.

### 8.5 Measure: "đa số" tính theo cách lấy mẫu nào?

"Đa số regime trong hộp" chỉ có nghĩa khi đã nói rõ rút điểm thế nào. Card v2 rút λ theo phân phối đều, và κ, h theo **log-đều**. Log-đều nghĩa là mỗi khoảng "gấp đôi" có cùng trọng số: khoảng 0,1–0,2 s được rút nhiều như khoảng 0,2–0,4 s. Cách này tự nhiên với các tham số thời gian, vì chúng tác động theo tỉ lệ. Chi tiết để L4.6.

**Hệ quả cho nghiên cứu:** L4.5 nói về **vùng**, không nói về lớp. Khi thấy một mảng màu đẹp, việc dịch nó thành thứ kiểm được là trả lời ba câu: **hộp nào, claim tỉ lệ nào, measure nào**.

---

## 9. 🔗 Liên hệ với việc bạn từng làm

- **Bạn đã dùng phân tích thứ nguyên mà không gọi tên nó.** Ở repo cũ có `mdk.py` (M/D/1/K dừng, đã verify). Kết quả của M/D/1/K chỉ phụ thuộc utilization ρ = λ/μ và K, với thời gian đo theo đơn vị service time. λA/μ ở đây chính là ρ của path A. Bài học hôm nay là cùng một ý, mở rộng sang các chiều thời gian.
- **Thói quen cũ cần sửa.** Repo cũ có nhiều heatmap (`experiments/scan/*`: map, frontier…) theo trục thô, và màu của heatmap dễ bị đọc như phát hiện. Ba câu hỏi mới cần hỏi trước mỗi heatmap:
  1. Trục có phải không thứ nguyên chưa?
  2. Phần nào là identity?
  3. Đây là lớp hay vùng?

## 10. Part 1 cho phép nói gì

**Được nói:**
- Trong plant hợp đồng (fluid, buffer vô hạn, cost tuyến tính, c_sw = 0, a/μ = 0,6), bản đồ có 5 chiều thật.
- Age là thang thời gian, không phải một chiều.
- Biên độ là chiều thật nhưng thuộc một plant khác.
- Card MV đúng về Ḡ_M ở MV+A.

**Không được nói:**
- "Age là một trục của bài toán."
- "Phép tương đương age đúng cho mạng packet."
- "Kết quả ở biên độ ±4 cho thấy hiệu ứng mạnh hơn."
- "MV+A là vùng model thắng."
- "Có X điểm lớp A" như một con số bền vững.

## 11. Reviewer có thể hỏi

1. *"Vì sao chỉ 5 chiều, trong khi thí nghiệm age của bạn có vẻ cho thấy nhiều hơn?"* **Đã trả lời:** §6.3, kèm kiểm số trên 18 cặp.
2. *"Kết luận có đúng với traffic ở mức packet không?"* **Chưa trả lời,** và có lý do để nghi ngờ (§6.4). Để Phase 7.
3. *"a/μ = 0,6 có thực tế không, và vì sao cố định nó?"* **Đã trả lời về scope**, chưa trả lời về realism. Để Phase 7/8.
4. *"Đếm lớp sát ngưỡng có bền không?"* **Đã trả lời:** không bền, nên claim phải là claim về vùng; gán nhãn lại bằng native ở L4.3.

## 12. ⚠️ Bẫy người mới

1. Gọi map3age là "kiểm theo tuổi telemetry" như thể đó là một chiều độc lập.
2. Quên rằng phép tương đương cần plant fluid, rồi mang nó sang packet DES hoặc mô hình có buffer hữu hạn.
3. So các con số % giữa hai biên độ khác nhau mà không để ý mẫu số đã đổi.
4. Đọc "lớp B" thành "vùng model thắng", hoặc đọc "lớp C" thành "model không có giá trị". Một điểm C có thể có Ḡ_M = 13%.
5. Vẽ hộp quanh các điểm vừa vượt ngưỡng 1% rồi kỳ vọng tỉ lệ thành công cao.

## 13. 🧠 Tư duy researcher

> **Đếm núm trước khi quét núm.** Trước khi thêm một tham số vào thí nghiệm, hãy hỏi: nó là một chiều độc lập, hay chỉ là đổi đơn vị của một chiều đã có? Thời gian quét một "chiều giả" là thời gian không học thêm được gì.

## 14. Bài tập hiểu (khuyến nghị)

- Viết lại phép chứng minh co giãn thời gian trong 5–8 dòng, không nhìn bài. Đánh dấu dòng nào dùng giả định fluid và dòng nào dùng tính thuần nhất của max(0, ·).
- Áp phép chứng minh vào toy path B: 4 → 16 packet·s.

## 15. Tự kiểm (tùy chọn)

1. Vì sao (age 2, κ 0,6, h 4) và (age 1, κ 0,3, h 2) cho cùng % contrast?
2. Dòng nào trong phép chứng minh sẽ gãy nếu buffer có kích thước cố định?
3. Vì sao a/μ không thể bị "quy đổi" giống như age?
4. Một điểm có Ḡ_M = 13% nhưng mang nhãn C. Điều đó nói gì về cách nhãn lớp được tạo ra?
5. Reviewer hỏi: "MV+A có 11/18 điểm lớp C, vậy card MV có sai không?" Bạn trả lời thế nào?

## 16. Trạng thái Part 1

- **Hiểu biết cần có:** tự dẫn được phép co giãn thời gian và nêu đủ các giả định của nó; đếm được 5 chiều thật; phân biệt được lớp với vùng; giải thích được vì sao biên độ không thành card.
- **Việc nên làm khi thực thi:** chưa có gì để chạy. Phép chứng minh ở §6.3 sẽ thành một phần của T07 addendum (Part 3).
- **Phụ thuộc khoa học:** mọi hộp vẽ ở L4.5 nên dùng tọa độ age 1 và không thứ nguyên.
- **Có học tiếp được không?** Có. Part 2 là phần thú vị nhất của L4.2: ba toy hai state cho thấy **cùng một kiểu lỗi của M0** có thể sinh ra cả lớp A, lớp AB (thay thế) lẫn lớp C (gây hại), cùng với hệ quả của điều đó khi thiết kế card về interaction. Khi muốn, bạn chỉ cần nói "tiếp tục Part 2".