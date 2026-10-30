# LESSON 4.4: Baseline khoa học tối thiểu

## Part 1/2: Pattern có tồn tại chỉ vì ô tham chiếu quá yếu không?

### 0. Kiểm nguồn và điều chỉnh plan

L4.4 khớp với trạng thái hiện tại. DL-103 dành quyết định #1 (chọn baseline và luật đọc kết quả) cho bạn. Tôi đã tự kiểm ba điều trong tài liệu và code:

- **Bảng baseline tối thiểu** ở Final Review §11.4 khớp với những gì plan trích.
- **Trong engine, quyết định nằm ở một dòng duy nhất** `switch = h < 0` của hàm `pair_loss`, trong file `population.py`. Vì vậy baseline có margin chỉ là dời biên quyết định từ 0 sang −θ, viết trong một hàm **mới** mà không sửa `pair_loss`.
- **Ví dụ ba snapshot** của plan và **toy có margin** ở §11 đều đã được tôi tính chính xác bằng phân số.

Có hai điểm liên quan tới tình trạng hiện tại của bạn:

1. **HOLD ở L4.3 có lẽ không chặn baseline cho MV và SH.** Hộp Ω_MV⁺ và Ω_SH⁺ có κ ∈ [0,1; 0,3], nằm trong frame của card v2, nơi numerics v1.3.1 đã qua 118 ca calibration. HOLD xảy ra ở κ/τ = 0,05, trong vùng AB. Đây là suy luận của tôi; khi thực thi, hãy kiểm lại từng điểm. Chỉ những dòng về SV và SUB mới phải chờ L4.3 và L4.5.
2. **Ở Part 2, tôi sẽ đề xuất thêm một điều kiện khi đọc Ḡ_S^θ.** Toy ở §11 cho thấy margin có thể **xóa cả giá trị thật** của state. Vì vậy, thấy giá trị của state "biến mất khi có margin" chưa chắc nghĩa là ô 00 quá yếu.

**Map của L4.4:**

| Part | Nội dung | Khái niệm trong plan |
|---|---|---|
| **1 (bài này)** | Baseline khoa học là gì; vì sao S0 đã là bản "bù tuổi" mạnh nhất; vì sao strawman nằm ở luật quyết định; toán về chi phí của một luật quyết định; toy có margin | 1, 2, 3 + phần toán |
| 2 | Chọn θ công bằng; đọc kết quả (R_M, Ḡ_S^θ, Stay); baseline đổi câu claim chứ không đổi verdict; viết đặc tả (bạn ký); sanity check; chạy song song với HOLD | 4, 5, 6 + Part A–C |

---

### 1. Bạn đang ở đâu?

```text
PHASE 4
  L4.1 ✓  L4.2 ✓  L4.3 ✓ (thực thi: HOLD)
  L4.4 Baseline khoa học ← BẠN Ở ĐÂY (Part 1/2)    ← quyết định #1 của bạn
  L4.5 Quyết định 0/1/2 card ← dùng L4.4 làm bộ lọc thứ năm
```

### 2. Câu hỏi của L4.4

> Các pattern (MV, SH, và hai ứng viên là vùng A và lớp AB) có tồn tại **chỉ vì** ô tham chiếu 00 là một controller quá yếu không? Ô 00 đổi đường ngay khi M0 dự báo có lợi, dù lợi rất ít.

### 3. Tại sao cần?

**Chữ "improvement" luôn có một mốc so sánh.** Main RQ hỏi về *improvements in current-state information and model fidelity*. Hiện tại mốc là ô 00. Nếu chỉ cần thêm một margin đơn giản là lấy lại phần lớn Ḡ_M, thì câu "model fidelity có giá trị" thực chất đang đo "có margin hay không có margin".

**Vì sao làm ở Phase 4, không để Phase 8.** Có ba căn cứ:
- Final Review §11.4, căn cứ cao nhất, liệt kê *"conservative load-aware rule/hysteresis — lợi ích có vượt một safety margin đơn giản không?"*.
- MASTER PLAN v1.0 xếp rủi ro SR7 (*strawman baseline*, tức so với một đối thủ yếu dựng sẵn) ở mức cao.
- Cách đọc kết quả baseline phải được viết **trước** khi có outcome CF. Viết sau thì câu trả lời nào cũng bị nghi là post-hoc.

**Nếu bỏ lesson này.** Phase 5 cho MV PASS. Reviewer hỏi: "Một margin 2% có làm được gần như vậy không?". Bạn chỉ có thể trả lời sau khi đã thấy CF.

**Nếu làm quá.** Lesson biến thành một benchmark với mười heuristic, sinh thêm forking path mà không bảo vệ thêm claim nào. Luật của lesson là: **mỗi baseline phải gắn với một giải thích thay thế có tên, cho một claim có tên.**

### 4. Liên hệ với Main RQ

```text
"improvements in ... fidelity" ──► so với cái gì?
   ô 00 (không margin) ──► Ḡ_M, Ḡ_S          ← gói v2 đo cái này
   baseline B_θ (có margin) ──► R_M, Ḡ_S^θ   ← L4.4 đo trên discovery
        ──► luật đọc viết trước ──► câu claim ở Phase 5 rộng hay hẹp
```

### 5. Prerequisite

- Bảng 2×2. Identity Ḡ_M ≥ 0 (S08): trong hàng S0, M1 không bao giờ thua M0.
- Ba toy của L4.2: T-A, T-AB, T-C′.
- **Toán mới:** kỳ vọng của một luật chỉ nhận giá trị 0 hoặc 1, được dẫn ở §9.

---

## 6. Khái niệm 1: baseline khoa học khác baseline vận hành, và khác bốn ô

**Trực giác.** Khi thử một thuốc mới, so với giả dược thì chưa đủ; phải so với loại thuốc rẻ đang dùng. Còn câu hỏi "thuốc mới có đáng mua không" (giá, tác dụng phụ, quy trình bệnh viện) là một câu hỏi khác.

| | **Baseline khoa học** | **Baseline vận hành** |
|---|---|---|
| Câu hỏi | Pattern có tồn tại chỉ vì mốc so sánh quá yếu không? | Có đáng triển khai không, sau khi tính chi phí? |
| Quyền thông tin | **Không nhiều hơn** pipeline nó thách thức | Thông tin khả thi ngoài đời |
| Ví dụ | Stay; luật có margin chạy trên M0 | Telemetry có giá, actuation delay, SLA |
| Làm ở | Phase 4 (trên discovery), Phase 5 (chỉ báo mô tả) | Phase 8 |
| Nếu pattern thua baseline | Câu claim hẹp lại (NARROW) | Không được đưa ra claim vận hành |

**Định nghĩa.** Baseline khoa học là một pipeline thay thế thỏa hai điều:
- **(i)** Cùng action set, cùng objective, cùng horizon, và **không có nhiều thông tin hơn** pipeline nó thách thức.
- **(ii)** Được chọn để loại trừ **một giải thích thay thế cụ thể** cho **một claim cụ thể**.

**Dễ nhầm:**
- S1M1 là **oracle**, dùng để đo headroom (trần lợi ích có thể có). Nó không phải baseline.
- S0M0 là **ô tham chiếu** của bảng 2×2.
- Baseline là một pipeline **thứ ba**, nằm ngoài bảng 2×2.

---

## 7. Khái niệm 2: trong v1.3, S0 đã là bản "bù tuổi" mạnh nhất

**Trực giác.** Bạn nhận tin "đường A đang có 8 xe chờ", gửi từ 1 giây trước.
- Người ngây thơ coi như bây giờ vẫn là 8 xe.
- Người khôn nghĩ: "1 giây đã trôi qua, giờ chắc khoảng 6–9 xe, và đường đang ở mode tải cao với xác suất bao nhiêu đó".
- **S0 của bạn là người khôn hoàn hảo.** Nó biết đúng luật của plant, nên tính được phân phối chính xác D(x | y) của state hiện tại.

**Định nghĩa.** Khi model đúng (M1), quyết định của S0 đã tối ưu theo **mọi** thông tin có trong snapshot y. Không pipeline nào chỉ dùng y lại làm tốt hơn S0M1; đây cùng lý do với S08. Vì vậy Ḡ_S|M1 đã đo đúng thứ cần đo: **giá trị của state tươi vượt lên trên việc dùng tối ưu snapshot cũ**.

Final Review lo rằng lợi ích của state có thể bị thổi phồng chỉ vì snapshot cũ được dùng quá ngây thơ. Mối lo đó đã bị **loại trừ ngay từ thiết kế**, và theo hướng bảo thủ, vì S0 còn mạnh hơn mọi estimator khả thi ngoài đời.

**Cẩn thận.** Với M0 (model sai), một estimator "sai" có thể vô tình bù lỗi của M0, như cơ chế của T-C′. Nhưng một niềm tin cố ý lệch để bù lỗi M0 thực chất là **sửa model trá hình**, không phải một baseline về state. Câu hỏi "có cách rẻ nào bù lỗi M0 không" được hỏi sạch hơn ở Khái niệm 3.

**Hệ quả thực hành.** **Không cần implement** một baseline bù tuổi riêng. Đặc tả chỉ cần ghi: "dòng *age-aware* của Final Review §11.4 đã được đáp ứng bởi định nghĩa của S0". Baseline "dùng quan sát gần nhất như hiện tại" chỉ là mốc sàn, tùy chọn, và không bảo vệ claim nào.

---

## 8. Khái niệm 3: strawman nằm ở luật quyết định

**Trực giác.** Hai tài xế dùng cùng một app dự báo kẹt xe hơi sai. Tài xế 1 đổi làn ngay khi app báo "nhanh hơn 1 giây". Tài xế 2 chỉ đổi khi app báo "nhanh hơn ít nhất 30 giây". Khi app sai, tài xế 2 tránh được phần lớn những lần đổi làn tồi, và chỉ bỏ lỡ vài lần đổi làn tốt nhưng lợi nhỏ.

**Định nghĩa.** Baseline margin B_θ dùng **đúng thông tin và đúng model** của ô mà nó thay thế:

```text
a00^θ(y) = Switch  ⇔  E[Δ̂(X) | y] < −θ      (thay ô 00: snapshot cũ + M0)
a10^θ(x) = Switch  ⇔  Δ̂(x) < −θ             (thay ô 10: state tươi + M0)
```

- θ ≥ 0 là một hằng số thiết kế, đơn vị packet·s, chọn **trước** theo một luật viết sẵn.
- θ = 0 cho lại đúng ô 00 và ô 10.
- **Margin chỉ đổi quyết định.** Nó không phải chi phí thật, nên **không** được cộng vào cost.

**Plan ghi "hysteresis"; tôi đồng ý đổi thành margin.** Hysteresis là công cụ cho quyết định **lặp lại**, để chống đổi qua đổi lại. Contract v1.3 là quyết định **một lần**, giữ suốt horizon h. Phiên bản một lần của hysteresis chính là margin.

**Không nhầm với Phase 6.** Margin ở đây **không** phải threshold null của phase mechanism.
- L4.4 hỏi: "một luật rẻ có làm được gần bằng không?" Đây là câu hỏi về **mốc so sánh**.
- Phase 6 hỏi: "chỉ riêng hình học của quyết định có giải thích được pattern không?" Đây là câu hỏi về **cơ chế** (methodology threats MT3, MT5).

Cùng dùng một ngưỡng, nhưng hỏi hai câu khác nhau.

---

## 9. Toán: chi phí của một luật quyết định hai action

**Câu hỏi.** Một luật quyết định có chi phí kỳ vọng bao nhiêu, và margin làm thay đổi gì?

**Bước 1.** Action chỉ là 0 (Stay) hoặc 1 (Switch). Vì vậy:

```text
J(a; x) = J(0; x) + a · Δ(x)
```

Kiểm: a = 0 cho J(Stay); a = 1 cho J(Stay) + Δ = J(Switch).

**Bước 2.** Lấy kỳ vọng theo niềm tin D(x | y). Action a(y) là hằng số khi đã biết y, nên đưa được ra ngoài kỳ vọng:

```text
L(y) = E[J(0; X) | y] + a(y) · g(y),    với g(y) = E[Δ(X) | y]
```

**Bước 3.** Lấy kỳ vọng theo Y, dùng tính chất kỳ vọng lặp E[E[· | Y]] = E[·]:

```text
L̄ = E[J_Stay] + E_Y[ a(y) · g(y) ]
```

**Ý nghĩa.** Mọi luật đều trả cùng một "phần Stay". Các luật chỉ khác nhau ở **những snapshot mà chúng chọn Switch**. Mỗi snapshot như vậy đóng góp g(y): âm nghĩa là đổi đúng, dương nghĩa là đổi sai. Engine cũng tính đúng theo cách này: `pair_loss` chỉ cộng d tại những chỗ `switch` đúng, rồi cộng phần base riêng.

**Margin làm gì.** Với a^θ(y) = 1[ĝ(y) < −θ] và ĝ(y) = E[Δ̂(X) | y], margin **bỏ** những snapshot có −θ ≤ ĝ(y) < 0. Ở những snapshot đó:
- Nếu g(y) > 0 (lần đổi đó là sai), margin **có lợi**.
- Nếu g(y) < 0 (lần đổi đó đúng nhưng lợi nhỏ), margin **gây thiệt**.

**Invariant:**
- θ = 0 cho đúng L̄00.
- θ đủ lớn cho L̄_Stay.
- Với mọi θ, L̄^θ ≥ L̄11: không luật nào thắng được oracle.
- **Không** có gì bảo đảm L̄^θ đơn điệu theo θ.

**Phạm vi đúng:** hai action, quyết định một lần, giữ suốt h, và c_sw = 0.

---

## 10. Ví dụ ba snapshot (của plan, tôi đã tính lại chính xác)

Ba snapshot có xác suất bằng nhau, E[J_Stay] = 10.

| Snapshot | ĝ (M0 dự báo) | g (gap thật) | Ý nghĩa |
|---|---:|---:|---|
| y₁ | −0,5 | +2 | M0 tưởng có lợi nhỏ, thật ra Switch gây hại |
| y₂ | −4 | −3 | Lợi lớn, M0 đúng |
| y₃ | −0,8 | −0,6 | Lợi nhỏ, M0 đúng |

```text
θ = 0 (ô 00):          Switch cả ba   → L̄ = 10 + (2 − 3 − 0,6)/3 ≈ 9,467
Model đúng (ô 01):     Switch y₂, y₃  → L̄ = 10 − 3,6/3 = 8,8     ⇒ Ḡ_M ≈ 0,667
θ = 1:                 chỉ Switch y₂  → L̄ = 10 − 3/3 = 9,0
θ = 5:                 không Switch   → L̄ = 10 (tệ hơn cả ô 00)
```

**Recovery** R_M = (L̄00 − L̄00^θ) / Ḡ_M = (9,467 − 9,0) / 0,667 ≈ **0,70**. Margin lấy lại khoảng 70% giá trị của sửa model. Part 2 sẽ đọc kỹ chỉ số này.

**Ba bài học:**
1. Margin **có thể** lấy lại phần lớn Ḡ_M, nên claim MV cần được kiểm điều này.
2. Không có θ "an toàn" chung cho mọi trường hợp (θ = 5 còn tệ hơn không có margin), nên phải có luật chọn θ viết trước.
3. Ở ví dụ này margin có ích vì lỗi của M0 nằm ở những dự báo lợi **nhỏ**.

---

## 11. Toy có margin: giá trị của một repair phụ thuộc vào controller

Đây là phần tôi bổ sung. Tôi dùng lại ba toy của L4.2 (hai state, mỗi state xác suất ½, J(Stay) = 10), thêm margin, và tính chính xác bằng phân số.

| Toy | θ | L̄00^θ | L̄10^θ | Ḡ_S^θ | R_M(θ) |
|---|---:|---:|---:|---:|---:|
| **T-AB** (M0 sai ở x₁, trung bình rơi sai phía) | 0 | 11 | 10,5 | +0,5 | 0 |
| | **1,5** | **10** | 10,5 | **−0,5** | **1** |
| | 3,5 | 10 | 10 | 0 | 1 |
| **T-C′** (M0 sai ở x₁, trung bình rơi đúng phía nhờ may) | 0 | 10 | 10,5 | −0,5 | — (Ḡ_M = 0) |
| | 1,5 | 10 | 10,5 | **−0,5** | — |
| | 3,5 | 10 | 10 | 0 | — |
| **T-A** (M0 đúng, thông tin có giá trị thật) | 0 | 10 | 9,5 | +0,5 | — (Ḡ_M = 0) |
| | **1,5** | 10 | **10** | **0** | — |

**Đọc từng toy:**

- **T-AB.** Margin θ = 1,5 chặn được lần đổi sai của ô 00, vì E[Δ̂] = −1 > −1,5. Margin **lấy lại toàn bộ** giá trị của sửa model (R_M = 1). Nhưng đồng thời, dấu của Ḡ_S **lật** từ +0,5 sang −0,5: với controller có margin, sửa state lại **gây hại**. Câu chuyện "thay thế" (AB) biến thành câu chuyện "gây hại" (C).
- **T-C′.** Margin 1,5 không xóa được tác hại, vì lợi dự báo sai của M0 ở x₁ là −3, lớn hơn 1,5. Phải tới θ = 3,5 tác hại mới biến mất. **Margin chỉ bắt được những lỗi của M0 có lợi dự báo nhỏ hơn θ.**
- **T-A.** Ở đây M0 đúng, nhưng margin 1,5 **xóa luôn giá trị thật** của state (Ḡ_S^θ = 0). Controller dùng state tươi kèm margin trả 10, tệ hơn hẳn mức 9,5 khi không có margin, vì lợi thật ở x₁ chỉ bằng 1 và bị margin bỏ qua.

**Insight nghiên cứu:**
1. Margin là một sự đánh đổi. Nó bắt những lỗi của M0 đi kèm lợi dự báo nhỏ, nhưng đồng thời vứt bỏ những lợi ích thật mà nhỏ.
2. **Giá trị của một repair không phải là tính chất của riêng mạng. Nó phụ thuộc vào luật quyết định của controller dùng repair đó.** Ḡ_S có thể đổi dấu khi chỉ đổi luật quyết định.

Đó là lý do baseline quan trọng với cả SV và SUB, không chỉ với MV. Và cũng là lý do Part 2 cần một điều kiện khi đọc Ḡ_S^θ: nếu margin làm controller **tệ đi** trong một vùng (như T-A), thì giá trị của state "biến mất khi có margin" không chứng minh ô 00 là strawman.

---

## 12. 🔗 Liên hệ với việc bạn từng làm

**Chủ đề này là một vòng tròn khép lại.** RQ cũ của bạn là "ngưỡng tĩnh so với độ rộng bất định" (GO gate, static threshold trong repo cũ). Một ngưỡng tĩnh trên lợi ích dự báo **chính là** margin.
- Trước đây, ngưỡng đó là *phương pháp* bạn muốn chứng minh.
- Bây giờ, nó quay lại với một vai trò chính xác hơn: một **baseline** có khả năng giải thích đi mất các hiệu ứng mà RQ mới đo được.

Code cũ không dùng lại được, vì khác model class (twin steady-state cho luồng nhỏ). Nhưng trực giác của bạn về khi nào ngưỡng có ích thì dùng được ngay.

## 13. Part 1 cho phép nói gì

**Được nói:**
- S0 đã đáp ứng baseline bù tuổi của Final Review.
- Rủi ro strawman nằm ở luật quyết định không có margin của M0.
- Trong toy, margin có thể lấy lại giá trị của sửa model, đổi dấu Ḡ_S, hoặc xóa giá trị thật của state.

**Không được nói:**
- "Margin luôn giúp."
- "Nếu có margin thì MV hoặc SH sai."
- "Toy cho biết margin sẽ làm gì trên plant thật." Điều đó phải chạy mới biết.

## 14. Reviewer có thể hỏi

1. *"So với một controller có margin thì sao?"* **Chưa trả lời:** cần Part 2 và việc chạy trên discovery.
2. *"Có phải các anh dùng snapshot cũ quá ngây thơ không?"* **Đã trả lời:** S0 là posterior Bayes chính xác.
3. *"Margin của các anh có phải chính là threshold null không?"* **Đã trả lời:** khác câu hỏi (mốc so sánh so với cơ chế).

## 15. ⚠️ Bẫy người mới

1. Implement một baseline bù tuổi mới, trong khi S0 đã là posterior Bayes.
2. Cộng θ vào chi phí thật, biến margin thành switching cost.
3. Gọi S1M1 là "baseline".
4. Nghĩ margin luôn giúp, hoặc nghĩ L̄^θ giảm đều khi θ tăng.
5. Đọc "Ḡ_S^θ ≈ 0" thành "giá trị của state chỉ là ảo giác". Toy T-A là phản ví dụ.

## 16. 🧠 Tư duy researcher

> Mọi "improvement" đều là so với một thứ gì đó. Hãy hỏi: thứ đó có phải đối thủ hợp lý nhất **với cùng lượng thông tin** không? Và nhớ rằng giá trị của một repair là tính chất của **cặp (repair, controller)**, không phải của riêng mạng.

## 17. Bài tập hiểu (khuyến nghị)

- **Tính tay** câu tự kiểm số 4 bên dưới.
- **Bắt đầu nghĩ về dự đoán của chính bạn cho SH**, theo dạng: "Tôi dự đoán ở Ω_SH⁺, margin ρ = 1% xóa [ít hơn / nhiều hơn] một nửa tác hại, vì …". Đây sẽ là nội dung của Bước 4 trong đặc tả ở Part 2. Toy chỉ gợi ý, không thay được phán đoán của bạn.

## 18. Tự kiểm (tùy chọn)

1. Baseline khoa học khác baseline vận hành ở câu hỏi nào?
2. Vì sao không cần implement một baseline bù tuổi cho S0?
3. Vì sao một niềm tin "cố ý lệch" để bù lỗi M0 không phải là baseline về state?
4. Trong ví dụ ba snapshot, nếu y₁ có ĝ = −3 thay vì −0,5, margin θ = 1 còn giúp không? R_M bằng bao nhiêu?
5. Ở T-AB, vì sao margin vừa lấy lại toàn bộ Ḡ_M vừa làm Ḡ_S đổi dấu?

## 19. Trạng thái Part 1

- **Hiểu biết cần có:** phân biệt baseline khoa học với baseline vận hành và với bốn ô; vì sao S0 đã đủ mạnh; định nghĩa B_θ; tự dẫn được L̄ = E[J_Stay] + E[a·g]; đọc được ba toy có margin.
- **Việc nên làm khi thực thi:** chưa có. Đặc tả là Part 2, và là quyết định của bạn.
- **Phụ thuộc khoa học:** đặc tả baseline phải được commit trước khi tính baseline ở bất kỳ điểm nào. Lần chạy native kế tiếp nên tính luôn các ô baseline.
- **Có học tiếp được không?** Có. Part 2 bàn cách chọn θ công bằng (thang tương đối ρ, cách chọn ρ\*, cận trên ρ_best, và ai được lợi khi chọn trên discovery), cách đọc (R_M, Ḡ_S^θ cùng điều kiện tôi đề xuất, Stay/headroom), vì sao baseline đổi câu claim chứ không đổi verdict, khung đặc tả để bạn tự viết, sanity check, và cách chạy song song với HOLD. Khi muốn, bạn chỉ cần nói "tiếp tục Part 2".