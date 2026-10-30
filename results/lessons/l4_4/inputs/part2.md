# LESSON 4.4, Part 2/2: Từ ý tưởng tới một đặc tả do chính bạn ký

```text
L4.4  Part 1 ✓ Baseline khoa học, S0 đã đủ mạnh, margin, toy
      Part 2 ← BẠN Ở ĐÂY: chọn θ công bằng · đọc kết quả · claim chứ không phải verdict · đặc tả · sanity · chạy
      → Lesson Gate L4.4
```

### 0. Những gì tôi đã kiểm cho Part 2

- **Bốn ô được tính ở đâu trong engine.** Hàm `evaluate()` tính ô 00 = `base + pair_loss(old, model='mean')` và ô 10 = `base + pair_loss(current, model='mean')`. Ô có margin dùng lại đúng các mảng mà `side()` đã tính sẵn. Phần đắt nhất là `side()`, nên chi phí thêm cho baseline **dự kiến nhỏ**. Tôi chỉ đọc code, chưa đo.
- **Một phiên bản margin của `pair_loss` đã được kiểm trên dữ liệu tổng hợp.** Tôi viết hàm này (in ở §6) và chạy 200 lượt ngẫu nhiên. Mã nguồn `pair_loss` được nạp nguyên byte từ repo, nên phép so sánh θ = 0 là so với hàm thật của engine, không phải bản chép tay. Bốn sanity đều đạt:
  - θ = 0 trùng **từng bit** với `pair_loss`;
  - θ rất lớn cho kết quả bằng Stay;
  - controller có margin không bao giờ thắng oracle;
  - không có action nào thay đổi (u = 0) thì gap bằng 0.
- **Giới hạn:** tôi chưa chạy hàm này trên plant thật, và chưa chạy ở bất kỳ điểm nào.

---

## 1. Câu hỏi của Part 2

> Làm sao viết một đặc tả baseline **công bằng**, **viết trước**, kèm một **luật đọc** biến kết quả thành câu claim, mà không biến baseline thành công cụ cứu claim hay giết claim?

---

## 2. Khái niệm 4: chọn θ thế nào cho công bằng

### 2.1 Hai cách để thiếu công bằng

| Lỗi | Ví dụ | Ai được lợi |
|---|---|---|
| **Baseline quá yếu** (strawman) | θ tùy ý, quá nhỏ hoặc quá lớn | Claim (claim đứng một cách dễ dàng) |
| **Tune trên đề thi** | Thử θ trên CF rồi mới chọn | Ai cũng được, tùy chọn kiểu gì. Dù sao đây cũng là gian lận |

### 2.2 Thang của θ phải tôn trọng quyền thông tin

| Cách đặt θ | Controller có tính được không? | Đánh giá |
|---|---|---|
| θ tuyệt đối (packet·s) | Có | Không so được giữa các regime có h khác nhau |
| θ = ρ · C̄_ref | **Không.** C̄_ref = L̄11 là chi phí của oracle | **Không hợp lệ.** Baseline sẽ có nhiều thông tin hơn mức cho phép |
| **θ = ρ · E[J_Stay]** | Có, vì S0 đã giả định biết luật của plant | **Khuyến nghị (plan đề xuất):** khả thi, so được giữa các regime, đơn giản |
| θ = ρ · E[J_Stay \| y] | Có | Linh hoạt hơn nhưng phức tạp hơn. Tùy chọn |

Bài học: **ngay cả con số dùng để co giãn θ cũng phải qua phép kiểm quyền thông tin.**

### 2.3 Ba loại ρ

- **Lưới ρ:** nhỏ, viết trước, **có cả ρ = 0** để mốc "không margin" nằm sẵn trong lưới. Ví dụ minh họa: {0; 0,5%; 1%; 2%; 5%}.
- **ρ\*:** baseline khả thi, chọn trên điểm discovery bằng một luật viết trước, rồi **giữ nguyên** cho Phase 5.
- **ρ_best(c):** ρ tốt nhất trên lưới cho từng regime c. **Không khả thi**, vì muốn biết nó phải dùng evaluator. Nó chỉ dùng làm **cận trên** cho câu hỏi "một margin giỏi nhất có thể làm được bao nhiêu".

### 2.4 Một vấn đề ẩn: chọn ρ\* trên tập điểm nào?

Plan đề xuất một ρ\* chung, chọn bằng cách lấy trung bình trên các điểm discovery. Nghe thì có vẻ trung lập, nhưng **thành phần của tập điểm quyết định ai được lợi**:

- Tối ưu ρ\* để baseline có regret nhỏ nhất làm baseline **mạnh**, tức là **bảo thủ** cho claim. Điều này chỉ đúng **nếu tập điểm giống vùng của claim**.
- Thực tế nếu dùng hợp của mọi vùng, vùng A (450 tọa độ) sẽ áp đảo về số lượng. Ở vùng A, M0 gần như đúng, nên margin gây thiệt, đúng như toy T-A. Kết quả là ρ\* bị kéo về gần 0, và baseline trở nên **yếu** đúng ở vùng MV. Như vậy lựa chọn này lại **có lợi cho claim**.

| Phương án | Cách chọn | Ưu | Nhược |
|---|---|---|---|
| (a) ρ\* chung, mỗi điểm một phiếu (plan) | argmin trên hợp mọi điểm | Đơn giản | Bị vùng đông điểm chi phối; có thể yếu ở vùng MV |
| (b) ρ\* chung, mỗi vùng claim một phiếu | argmin trung bình theo vùng | Cân bằng hơn, vẫn chỉ một số | Vẫn là thỏa hiệp giữa các vùng |
| **(c) ρ\* riêng cho từng vùng claim** | argmin trong từng vùng, luật viết trước | Đối thủ mạnh nhất cho mỗi claim, tức bảo thủ nhất | 2–4 con số; Ω_MV⁺ chỉ có khoảng 16–18 điểm, nhưng lưới nhỏ nên rủi ro overfit thấp |

**Khuyến nghị của tôi: (c)** cho F1 (MV, SH), kèm báo cáo ρ_best(c).

Phương án (c) **không phải** cái bẫy "chọn ρ khác nhau để claim đứng". Cái bẫy đó là chọn **sau** khi thấy số và chọn **theo chiều có lợi cho claim**. Còn (c) được viết **trước**, và luôn chọn theo chiều làm baseline **mạnh nhất**. Controller biết tham số regime ngay từ thiết kế, nên một lịch margin theo vùng vẫn là khả thi.

**Luật chọn phải ghi rõ đang tối ưu cho controller nào:**
- Với MV: tối ưu S0M0^θ, vì MV so ô 00 với ô 01.
- Với SH: tối ưu S1M0^θ, vì SH hỏi về tác hại của state tươi đối với M0.
- Khi tính Ḡ_S^θ, dùng **cùng một θ** cho cả ô 00 và ô 10.
- Nên ghi luôn luật phá hòa, ví dụ: nếu hai ρ cho regret bằng nhau thì chọn ρ nhỏ hơn.

Lưu ý: argmin trên dữ liệu discovery chỉ là một **luật chọn**, không phải ước lượng cho population, vì mẫu discovery được lấy thích nghi.

---

## 3. Khái niệm 5: đọc kết quả

### 3.1 Ba đại lượng chính

**Recovery của giá trị model**, chỉ định nghĩa khi Ḡ_M > 0:

```text
R_M(θ) = (L̄00 − L̄00^θ) / Ḡ_M
```

Margin lấy lại được bao nhiêu phần lợi ích mà việc sửa model mang lại?
- R_M ≈ 1: margin làm được gần bằng sửa model.
- R_M ≈ 0: margin không giúp gì.
- R_M < 0: margin còn làm tệ hơn.

**Sửa state dưới controller có margin:**

```text
Ḡ_S^θ = L̄00^θ − L̄10^θ
```

**Stay**, tính miễn phí vì `base` đã có sẵn:
- **(L̄_Stay − L̄11)/C̄_ref:** headroom. Việc đổi đường ở đây có đáng không?
- **(L̄_Stay − L̄00)/C̄_ref:** pipeline cũ có tốt hơn "không làm gì" không?
- Ở lớp C, đáng xem S1M0 có tệ hơn cả Stay hay không.

### 3.2 Điều kiện đối thủ (tôi đề xuất thêm)

Plan đọc Ḡ_S^θ trực tiếp. Tôi đề xuất thêm một điều kiện, vì toy T-A ở Part 1: ở đó margin làm Ḡ_S^θ = 0 **không phải** vì ô 00 quá yếu, mà vì margin làm controller dùng state tươi **tệ đi** (10 so với 9,5).

> **Chỉ đọc "pattern biến mất khi có margin" thành "pattern phụ thuộc vào mốc yếu" khi margin thật sự làm controller liên quan *tốt lên* trong vùng đó.**

- **Với MV:** điều kiện tự thỏa. R_M > 0 tương đương với L̄00^θ < L̄00.
- **Với SH và SV:** báo kèm ΔL̄10 = L̄10^ρ\* − L̄10.
  - ΔL̄10 < 0: margin cải thiện controller dùng state tươi, nên việc tác hại biến mất là bằng chứng cho giải thích "chỉ vì đổi đường với lợi rất nhỏ".
  - ΔL̄10 > 0: ghi là "margin không phải đối thủ mạnh hơn ở vùng này", và **không** thu hẹp claim vì lý do baseline.

### 3.3 Luật đọc: viết cho CF, xem trước trên discovery

**Số nào đến từ đâu:**
- **Discovery:** dùng để chọn ρ\* và xem trước kết quả.
- **CF ở Phase 5:** runner tính các output mô tả này và báo cạnh verdict. Chính **luật đọc đã viết trước** áp lên các số CF sẽ quyết định câu claim.

**Luật đọc mẫu** (ngưỡng chỉ để minh họa; bạn chọn):
- *MV:* nếu trung vị R_M(ρ\*) ≥ ½ ở Ω_MV⁺, thì câu claim thêm: "…so với controller mean-field không có margin; một margin đơn giản đã lấy lại phần lớn lợi ích này".
- *SH:* nếu trung vị |Ḡ_S^ρ\*| < ½% **và** trung vị ΔL̄10 < 0 ở Ω_SH⁺, thì SH chỉ được nói là "tác hại đối với controller không có margin".

**Vì sao dùng trung vị mà không dùng test thống kê?** Mỗi vùng chỉ có ít điểm, và mẫu discovery được lấy thích nghi. Đây là một **luật mô tả viết trước** để quyết định câu chữ, không phải một phép suy luận thống kê. Gắn p-value vào một mẫu thích nghi sẽ tạo cảm giác chắc chắn giả.

---

## 4. Khái niệm 6: baseline đổi câu claim, không đổi verdict

**Trực giác.** Đề thi đã in thì điểm không đổi. Nhưng lời phê "giỏi so với lớp" khác với lời phê "giỏi so với đề".

Card v2 khóa tiêu chí trên Ḡ_M và Ḡ_S, và không nhắc gì tới baseline. Phase 5 chấm đúng như đã khóa. Baseline chỉ quyết định **câu nào được nói**. Đây là outcome **NARROW** trong MASTER PLAN.

| Tình huống ở Phase 5 | Câu được nói |
|---|---|
| MV PASS, trung vị R_M(ρ\*) ≈ 0,8 | "Ḡ_M ≥ 1% ở đa số Ω_MV⁺ so với controller không margin; một margin đơn giản lấy lại phần lớn lợi ích này" |
| MV PASS, trung vị R_M(ρ\*) ≈ 0,1 | "…và lợi ích này không bị một margin đơn giản thay thế (trên các điểm đã kiểm)". Câu mạnh hơn |
| MV FALSIFY | Verdict là FALSIFY, bất kể baseline nói gì |

**Có nên cho baseline một verdict riêng không?** Ví dụ card "MV vẫn đạt khi M0 có margin". Làm vậy là thêm một card vào F2, chiếm một trong hai suất. **Khuyến nghị: không**, trừ khi bạn coi đây là câu hỏi trung tâm của paper.

---

## 5. Đặc tả: khung để **bạn** điền

Đây là quyết định #1 của DL-103. Tôi chỉ điền sẵn những phần **không phải quyết định**. Mọi chỗ ⟨…⟩ là của bạn.

```markdown
# experiments/P4_04_baseline/spec.md — commit TRƯỚC mọi phép tính baseline
Người ký: Doan Van Tai · ⟨ngày⟩ · Provenance: ⟨tác giả viết | AI soạn, tác giả duyệt⟩
Đã thấy khi viết: output L4.1–L4.3 (REGIME_MAP, recount, 3 điểm native benchmark).
CHƯA có giá trị baseline nào ở bất kỳ điểm nào.

## 1. Claim → giải thích thay thế → baseline
| Claim | Giải thích thay thế | Baseline | Giữ/Bỏ |
| MV  | "chỉ cần margin, không cần model đúng"          | B_θ trên ô 00: R_M        | ⟨…⟩ |
| SH  | "tác hại chỉ vì M0 đổi đường với lợi rất nhỏ"   | B_θ trên 00, 10: Ḡ_S^θ, ΔL̄10 | ⟨…⟩ |
| SV/SUB (nếu sống sau L4.5 Part A) | ⟨…⟩               | ⟨…⟩                        | ⟨…⟩ |
| Mọi claim | "đổi đường ở đây có đáng không?"          | Stay: headroom (miễn phí) | giữ |

## 2. Baseline
- Age-aware: đã đáp ứng bởi định nghĩa S0 (posterior Bayes chính xác, T07 §2). Không implement.
- B_θ: ⟨giữ/bỏ⟩ · Stay: tính từ base.
- Last observation / current-metric heuristic / steady-state: ⟨bỏ hoặc để Phase 8, kèm lý do⟩

## 3. Thang và lưới
θ = ρ · E[J_Stay]   (controller tính được; không dùng C̄_ref)
Lưới ρ = ⟨…⟩   (phải có 0)

## 4. Luật chọn ρ*
Phương án ⟨a | b | c⟩ · controller mục tiêu: MV → ⟨…⟩; SH → ⟨…⟩
Trọng số: ⟨…⟩ · Phá hòa: ⟨…⟩ · Báo thêm ρ_best(c) như cận trên, không khả thi

## 5. Luật đọc (áp cho output mô tả trên CF ở Phase 5; discovery chỉ xem trước)
MV: nếu trung vị R_M(ρ*) ≥ ⟨…⟩ thì câu claim = "⟨…⟩"
SH: nếu trung vị |Ḡ_S^ρ*| < ⟨…⟩ ⟨và trung vị ΔL̄10 < 0?⟩ thì câu claim = "⟨…⟩"
Nếu điều kiện đối thủ không đạt: ⟨…⟩
Baseline KHÔNG đổi verdict của card v2.

## 6. Tập điểm
Điểm discovery đã lộ trong Ω_MV⁺, Ω_SH⁺ (quy về age 1, có trong inventory v3).
⟨Vùng A/AB: chỉ sau L4.3 / L4.5⟩ · Guard: khóa CF-v2, R10 niêm phong.

## 7. Dự đoán — tác giả tự viết, mỗi claim một dòng, TRƯỚC khi chạy
MV: Tôi dự đoán … vì …
SH: Tôi dự đoán … vì …
```

**Lời khuyên duy nhất của tôi về đặc tả:** mục 7 hãy tự viết, kể cả khi viết thô hoặc sai. Một dự đoán sai mà là của bạn có giá trị khoa học hơn một dự đoán đúng do AI viết thay.

---

## 6. Implement và sanity (Part B)

**Code này tồn tại để trả lời Q4.4:** khi controller của ô 00 và ô 10 có một margin hợp lý, pattern còn lại bao nhiêu?

So với `pair_loss`, hàm mới chỉ khác **hai chỗ**: biên quyết định dời từ 0 sang −θ, và θ **không** xuất hiện trong chi phí.

```python
def pair_loss_margin(A, B, cost=F(0), *, model="mean", theta=LD(0)):
    """Same as pair_loss but Switch iff forecast < -theta; theta changes decisions only."""
    d = A['d'][:, None] + B['d'][None, :] + number(cost)
    ed = A['ed'][:, None] + B['ed'][None, :] + 64 * EPS * (abs(d) + 1)
    if model == 'true':
        h = d; eh = ed
    else:
        h = A['h'][:, None] + B['h'][None, :] + number(cost)
        eh = A['eh'][:, None] + B['eh'][None, :] + 64 * EPS * (abs(h) + 1)
        certified = (A['zero_h'][:, None] & B['zero_h'][None, :]) | (A['sat_h'][:, None] & B['sat_h'][None, :])
        h = np.where(certified, number(cost), h); eh = np.where(certified, LD(0), eh)
    weights = A['w'][:, None] * B['w'][None, :]
    s = h + theta                                   # only the decision boundary moves
    switch = s < 0; ambiguous = (s - eh < 0) & (s + eh >= 0)
    contribution = np.where(switch, d, LD(0))       # true gap d: no theta in the cost
    loss = (weights * contribution).sum(dtype=LD)
    error = (weights * np.where(ambiguous, abs(d) + ed, np.where(switch, ed, LD(0)))).sum(dtype=LD)
    maxcost = max(LD(1), np.max(abs(d) + ed))
    error += (A['w_error'] + B['w_error'] + A['w_error'] * B['w_error']) * maxcost
    error += 1024 * weights.size * EPS * maxcost
    return loss, error, float(weights[ambiguous].sum(dtype=LD))

# L̄00^θ = base + pair_loss_margin(A['old'],     B['old'],     theta=θ)[0]
# L̄10^θ = base + pair_loss_margin(A['current'], B['current'], theta=θ)[0]
```

**Mục đích khoa học của hai dòng quan trọng:**
- `s = h + theta` chỉ dời **biên quyết định**. Đây là định nghĩa của B_θ.
- `contribution = np.where(switch, d, …)` dùng gap **thật** d, không có θ. Nếu cộng θ vào đây, margin sẽ biến thành switching cost, và bạn đang đo một thứ khác hẳn.

**Sanity theo thứ tự. Fail ở bước nào thì dừng ở bước đó, vì đó là bug, không phải kết quả:**
1. θ = 0 cho L̄00 và L̄10 trùng **từng bit** với engine. *(Đã đạt trên dữ liệu tổng hợp.)*
2. θ rất lớn cho đúng `base`. *(Đã đạt trên dữ liệu tổng hợp.)*
3. u = 0 làm mọi ô bằng nhau. *(Đã đạt ở dạng tầm thường.)*
4. L̄^θ ≥ L̄11 − sai số, trên mọi điểm. *(Đã đạt trên dữ liệu tổng hợp.)*
5. Golden test: ví dụ ba snapshot ra đúng 9,467 / 9,0 / 10; ba toy có margin ra đúng bảng ở Part 1 §11.

Khi chạy trên plant, sanity 1–4 phải được kiểm lại trên **mảng thật**.

---

## 7. Chạy (Part C), song song với HOLD

**Có thể chạy ngay sau khi commit đặc tả.** Các điểm discovery đã lộ trong Ω_MV⁺ và Ω_SH⁺ nằm trong frame của card v2, nên có lẽ không bị HOLD chặn. Khi chạy vẫn phải kiểm R1 ở từng điểm, cùng guard khóa CF và R10.

**Phải chờ:** vùng A và vùng AB chờ L4.3 được xử lý và L4.5 Part A.

**Gộp lần chạy.** Lần chạy native kế tiếp nên tính luôn các ô baseline. Kết quả chỉ ghi một lần.

**Bảng kết quả theo vùng:** số điểm; trung vị và min–max của R_M(ρ\*), Ḡ_S^ρ\*, ΔL̄10, ρ_best, headroom của Stay.

**Sau khi có bảng:**
1. So với dự đoán ở mục 7 của đặc tả; ghi mọi chỗ lệch.
2. Viết DL luật đọc và tự ký.
3. Đóng băng ρ\*.
4. Liệt kê các output mô tả mà runner (L4.8) phải tính trên CF.
5. Thêm dòng exposure.

### Các kết cục có thể xảy ra

| Kết cục trên discovery | Ý nghĩa | Hệ quả |
|---|---|---|
| R_M nhỏ ở Ω_MV⁺ | Margin không thay được model fidelity | Câu MV nếu PASS sẽ mạnh |
| R_M lớn ở Ω_MV⁺ | Một phần lớn "giá trị model" là giá trị của việc có margin | Viết trước câu hẹp lại; cân nhắc lại card SUB ở L4.5 |
| \|Ḡ_S^ρ\*\| nhỏ và ΔL̄10 < 0 ở Ω_SH⁺ | Tác hại nhạy với margin | SH nếu PASS chỉ được nói "với controller không margin" |
| \|Ḡ_S^ρ\*\| nhỏ nhưng ΔL̄10 > 0 | Margin không phải đối thủ tốt hơn ở đây | Không hẹp claim vì baseline; ghi rõ lý do |
| Sanity fail | Bug | Dừng, sửa code, không đọc kết quả |

---

## 8. Toàn bộ L4.4 cho phép nói gì

**Được nói** (sau khi thực thi): "Trên các điểm discovery đã biết, pattern X còn (hoặc không còn) khi so với controller có margin được chọn theo luật viết trước. Nếu Phase 5 cho kết quả tương tự, câu claim sẽ là … (đã viết trước)."

**Không được nói:**
- Pattern đứng vững trước **mọi** baseline. Ta mới so với Stay và margin.
- Bất cứ điều gì về chuyện có đáng triển khai không. Đó là Phase 8.
- Số trên discovery là tần suất.

## 9. Reviewer có thể hỏi

1. *"So với một margin hợp lý thì sao?"* Trả lời bằng bảng kết quả trên discovery và luật đọc viết trước, sau khi thực thi.
2. *"ρ\* chọn trên discovery thì có lợi cho baseline hay cho claim?"* **Đã trả lời** (§2.4): có lợi cho baseline, tức bảo thủ cho claim, **nếu** tập điểm giống vùng claim. Đó là lý do khuyến nghị chọn theo từng vùng.
3. *"Margin biến mất tác hại ở SH, vậy tác hại có phải ảo không?"* **Đã trả lời** (§3.2): phải xem ΔL̄10.
4. *"Sao không cho baseline một verdict riêng?"* **Đã trả lời** (§4): đó là một lựa chọn, sẽ tốn một suất của F2.

## 10. ⚠️ Bẫy người mới

1. Co giãn θ theo C̄_ref. Làm vậy là baseline dùng thông tin của oracle.
2. Chọn ρ\* trên một tập bị vùng A áp đảo rồi gọi baseline là "mạnh".
3. Đọc "|Ḡ_S^θ| nhỏ" mà không xem ΔL̄10.
4. Viết luật đọc cho discovery mà quên rằng câu claim thật được quyết định bởi số trên CF.
5. Cộng θ vào chi phí.
6. Để AI viết mục dự đoán "đóng vai bạn" thêm một lần nữa.

## 11. 🧠 Tư duy researcher

> Một baseline công bằng là đối thủ **mạnh nhất có thể**, với **cùng lượng thông tin**, được chọn **trước**, theo chiều **bất lợi cho claim của chính mình**. Mọi lựa chọn trong đặc tả, kể cả tập điểm dùng để tune, đều phải qua câu hỏi: "lựa chọn này làm baseline mạnh lên hay yếu đi?"

## 12. Bài tập hiểu (khuyến nghị)

- **Tự điền mục 3, 4, 5, 7 của khung đặc tả,** kể cả ở dạng nháp.
- **Với mỗi lựa chọn, viết một dòng:** "lựa chọn này làm baseline mạnh hơn hay yếu hơn, và vì sao?"

## 13. Tự kiểm (tùy chọn)

1. Vì sao θ = ρ · C̄_ref vi phạm quyền thông tin?
2. Vì sao một ρ\* chung, chọn trên hợp mọi điểm, có thể **có lợi cho claim**?
3. Ở Ω_SH⁺, |Ḡ_S^ρ\*| ≈ 0 nhưng ΔL̄10 > 0. Bạn được nói gì?
4. MV PASS ở Phase 5 và trung vị R_M(ρ\*) = 0,8. Câu claim là gì, và câu nào **không** được nói?
5. Vì sao dòng `contribution` dùng d mà không dùng d + θ?

---

## 14. LESSON GATE: L4.4

**Hiểu biết.** Sau L4.4, bạn nên tự giải thích được:
- Baseline khoa học khác baseline vận hành và khác bốn ô.
- Vì sao S0 đã là bản bù tuổi mạnh nhất.
- Strawman nằm ở luật quyết định; định nghĩa B_θ.
- Công thức L̄ = E[J_Stay] + E[a·g].
- Ba toy có margin.
- Thang θ phải tôn trọng quyền thông tin; ba loại ρ; vì sao tập điểm dùng để tune quyết định ai được lợi.
- R_M, Ḡ_S^θ, điều kiện đối thủ, Stay.
- Baseline đổi câu claim, không đổi verdict.

**Trạng thái thực thi:** chưa bắt đầu.
- Việc của bạn: `spec.md` (quyết định #1, kèm dự đoán của chính bạn) ⬜; `margin.py` và test trong repo ⬜; chạy trên Ω_MV⁺ và Ω_SH⁺ ⬜; DL luật đọc ⬜; output mô tả cho runner ⬜.
- AI đã làm giúp: kiểm hàm margin trên dữ liệu tổng hợp so với `pair_loss` gốc (200 lượt, bốn sanity đạt); tính lại ví dụ ba snapshot và ba toy có margin.

**Phụ thuộc khoa học:**
- Đặc tả phải được commit trước khi tính baseline ở bất kỳ điểm nào.
- L4.5 Part B dùng kết quả L4.4 làm bộ lọc thứ năm.
- Gate 4 cần: đặc tả, kết quả trên discovery, DL luật đọc, và các output mô tả đã nằm sẵn trong runner.

**G-level:** vẫn là G1.

**Có học L4.5 được không?** Có. L4.5 gom mọi thứ lại: năm bộ lọc (identity, prior, giá trị cho RQ, khả thi, baseline) dẫn tới quyết định thêm 0, 1 hay 2 card. Đó là quyết định #2 của bạn, và cũng là nơi quyết định HOLD ở κ/τ = 0,05 có còn quan trọng không.

**Điều cần giữ trong đầu.** Baseline không phải để thắng hay thua. Nó trả lời câu hỏi của reviewer **trước** khi reviewer hỏi, và theo một luật bạn đã viết khi chưa thấy số. Ở Phase 4, đây là quyết định đáng tự tay làm nhất.