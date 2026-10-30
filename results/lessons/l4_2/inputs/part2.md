# LESSON 4.2, Part 2/3: Một kiểu lỗi của M0, ba câu chuyện

```text
L4.2  Part 1 ✓ Chiều thật, lớp khác vùng
      Part 2 ← BẠN Ở ĐÂY: ba toy · Ḡ_S|M1 là giá trị thông tin · cận của Γ̄ và thiết kế card
      Part 3   Tọa độ δ · đọc hình · T07 addendum + golden test
```

### 0. Một chỉnh sửa nhỏ so với plan

Tôi đã tính lại cả ba toy bằng phân số chính xác và kiểm mọi identity. Số trong bảng của plan đều đúng. Có hai chỗ diễn giải cần sửa:

1. **Plan viết:** "khác biệt duy nhất giữa T-AB và T-C là M0 ở x₂ (+1 so với +3)". Thực tế T-AB có Δ̂ = (−3; +1) còn T-C có Δ̂ = (−2; +3), tức khác nhau ở **cả hai** state. Tôi dùng biến thể **T-C′ = (−3; +4)**. T-C′ cho đúng bốn L̄ như T-C, nhưng giờ chỉ khác T-AB ở x₂, nên câu của plan đúng theo nghĩa đen.
2. **Plan đề xuất mutant:** đổi Δ̂(x₂) của T-AB thành +3. Khi đó E[Δ̂] = 0, đúng lúc hòa, nên kết quả phụ thuộc **luật hòa** (hòa thì chọn Stay). Mutant đó dùng để kiểm luật hòa thì tốt, nhưng để minh họa cơ chế thì nên dùng +4.

---

## 1. Câu hỏi của Part 2

> Vì sao **cùng một lỗi** của model mà sửa state lúc thì có ích, lúc vô ích, lúc lại gây hại? Và điều đó ràng buộc cách viết một card về interaction như thế nào?

## 2. Tại sao cần?

- **Ở L4.5, bạn sẽ xét hai card ứng viên:** SV (state value, từ lớp A) và SUB (substitution, từ lớp AB). Bạn cần phân biệt được hai thứ. Thứ nhất là state có giá trị *thật*, tức thông tin giúp quyết định tốt hơn. Thứ hai là state chỉ *bù lỗi* cho M0. Thiếu phân biệt này thì "differ" bị kể sai.
- **Card về Γ̄ có một cái bẫy riêng.** Vùng đối chứng có thể bị identity ép phải đúng, tức đối chứng không thể thất bại.
- **Câu "AB và C cùng nguồn" là ứng viên cơ chế cho Phase 6.** Bạn cần hiểu nó bằng toy trước khi đọc nó trên dữ liệu.

## 3. Liên hệ với Main RQ

| Động từ trong RQ | Đại lượng | Toy cho thấy gì |
|---|---|---|
| **differ** | Ḡ_S so với Ḡ_S\|M1 | Ḡ_S giống nhau (+0,5) có thể là giá trị thông tin thật (T-A) hoặc chỉ là bù lỗi model (T-AB) |
| **interact** | Γ̄ | Γ̄ < 0 (thay thế) và Γ̄ > 0 (bị ép, vùng gây hại) có thể sinh ra từ cùng một lỗi của M0 |

---

## 4. Mental model: hai "kính" và một "thước"

Mỗi ô của bảng 2×2 quyết định theo **dấu của một độ chênh** (Switch nếu âm; hòa thì Stay):

| Ô | Quyết định theo dấu của | Đọc là |
|---|---|---|
| 11 | Δ(x) | Thấy rõ, thước đúng |
| 10 | Δ̂(x) | Thấy rõ, thước lệch |
| 01 | E[Δ \| y] | Nhìn qua kính mờ, thước đúng |
| 00 | E[Δ̂ \| y] | Nhìn qua kính mờ, thước lệch |

- **S0 là kính mờ.** Ảnh cũ không cho biết state hiện tại, nên controller phải chọn **một** action cho mọi state có thể xảy ra, tức là quyết định theo **trung bình**.
- **M0 là thước lệch.** Dự đoán Δ̂ sai ở một số state.
- **Sửa state là tháo kính mờ.** **Sửa model là sửa thước.**

Mọi thứ trong Part 2 xoay quanh một câu: **khi nhìn qua kính mờ, lỗi của thước lệch bị trung bình hóa, và trung bình có thể rơi về phía đúng hoặc phía sai của số 0.**

---

## 5. Ba toy

**Bối cảnh chung.** Có hai state, mỗi cái xác suất ½: x₁ là B đang OFF (nhẹ), x₂ là B đang ON (nặng). Telemetry cũ 1 s không cho biết mode hiện tại, nên S0 tin ½–½. J(Stay) = 10 ở cả hai state.

Lưu ý: các Δ̂ ở đây là số **được chọn**, không suy ra từ vật lý của hàng đợi; T07 cũng ghi rõ điều này cho golden toy. Toy chỉ cho thấy một điều **có thể xảy ra về mặt logic**, không chứng minh cơ chế trong plant.

### 5.1 T-A: thước đúng, thông tin có giá trị thật

Δ = (−1; +1,2), và M0 dự đoán đúng: Δ̂ = Δ.

```text
11 và 10: từng state chọn đúng → x₁ Switch (9), x₂ Stay (10) → L̄ = 9,5
01 và 00: trung bình = ½(−1) + ½(1,2) = +0,1 → Stay cho cả hai → L̄ = 10
```

Ḡ_S = 0,5; Ḡ_M = 0; Γ̄ = 0; Ḡ_S|M1 = 0,5. Đây là lớp A.

Câu chuyện: hai state **bất đồng** về action tốt nhất. Kính mờ buộc controller chọn một action cho cả hai, nên mất 0,5. Sửa model vô ích vì thước vốn đúng.

### 5.2 T-AB và T-C′: cùng lỗi, hai số phận

Ở cả hai toy, sự thật là **Stay luôn tốt hơn** (Δ = +1 ở cả hai state). M0 sai ở x₁: khi B đang OFF, nó tưởng chuyển sang B có lợi (Δ̂ = −3).

| | **T-AB** | **T-C′** |
|---|---|---|
| Δ̂(x₁); Δ̂(x₂) | −3; **+1** | −3; **+4** |
| Trung bình qua kính mờ E[Δ̂] | **−1** → Switch (phía sai) | **+0,5** → Stay (phía đúng, nhờ may) |
| L̄00 | 11 | 10 |
| L̄10 (thấy rõ, thước lệch) | 10,5 | 10,5 |
| L̄01 | 10 | 10 |
| L̄11 | 10 | 10 |
| Ḡ_S | **+0,5** | **−0,5** |
| Ḡ_M | 1 | 0 |
| Γ̄ | **−0,5** (chạm cận −min) | **+0,5** (bị S12 ép) |
| Ḡ_S\|M1 | 0 | 0 |
| Lớp | AB | C |

Vị trí của trung bình trên trục quyết định:

```text
            Switch ◄────────────── 0 ──────────────► Stay
T-AB:   E[Δ̂] = −1  ●                                       → chọn sai
T-C′:                              ● E[Δ̂] = +0,5           → chọn đúng nhờ may
Sự thật:                                  ● Δ = +1 (mọi state)
```

**Đọc từng bước:**

1. **Hàng S1 giống hệt nhau** (L̄10 = 10,5 ở cả hai). Khi thấy rõ, M0 quyết định giống nhau: ở x₁ chọn Switch (sai), ở x₂ chọn Stay (đúng). Lỗi theo từng state của M0 **y hệt**.
2. **Chỉ L̄00 khác nhau,** và nó khác vì trung bình qua kính mờ rơi về hai phía của số 0.
3. **Ở T-AB, trung bình rơi sai phía.** Ô 00 sai ở cả hai state, nên trả 11.
   - Sửa state (tháo kính): x₂ được sửa, x₁ vẫn sai, cost 11 → 10,5, tức **+0,5**.
   - Sửa model (sửa thước): sửa được cả hai state, cost 11 → 10, tức **+1**.
   - Sửa cả hai cũng chỉ được **+1**. Sửa model đã bao trùm phần lợi của sửa state, nên Γ̄ = 1 − 0,5 − 1 = **−0,5**: hai repair **thay thế** nhau.
4. **Ở T-C′, trung bình rơi đúng phía nhờ may.** Ô 00 đúng ở cả hai state, trả 10.
   - Sửa state: kính mờ đang **che** lỗi ở x₁; tháo kính thì lỗi lộ ra, cost 10 → 10,5, tức **−0,5**.
   - Sửa model: không còn gì để sửa, tức 0.

**Kết luận của toy:** AB và C có **cùng nguồn**. Đó là cùng một lỗi của M0; khác biệt duy nhất là trung bình của lỗi rơi về phía nào của biên quyết định. Đây cũng là một ví dụ nữa của *prediction error ≠ decision regret*: lỗi dự đoán giống nhau, nhưng giá trị của repair ngược dấu.

---

## 6. Ḡ_S|M1 là giá trị thông tin (S10)

### 6.1 Câu hỏi

Khi model đã đúng, biết state hiện tại thay vì chỉ có ảnh cũ thì đáng giá bao nhiêu?

### 6.2 Dẫn công thức

Chia mỗi Δ thành phần dương và phần âm: Δ⁺ = max(Δ, 0), Δ⁻ = max(−Δ, 0). Với mỗi snapshot y, đặt:

- **P(y) = E[Δ⁺ | y]:** "khối lỗ" nếu chọn Switch, gom từ những state mà Stay tốt hơn.
- **N(y) = E[Δ⁻ | y]:** "khối lỗ" nếu chọn Stay, gom từ những state mà Switch tốt hơn.

Khi đó E[Δ | y] = P − N.

```text
Ô 01 (thước đúng, kính mờ):  L01(y) = E[J_Stay | y] + min(0, P − N)
                             (chọn Switch khi P − N < 0, và khi đó trả thêm P − N)
Ô 11 (thước đúng, thấy rõ):  L11(y) = E[J_Stay | y] − N
                             (ở state nào Switch tốt hơn thì lấy được phần N)
Hiệu:                        L01 − L11 = N + min(0, P − N) = min(P, N)
```

Bước cuối dùng quy tắc: N + min(0, P − N) = min(N, P). Nếu P ≥ N thì vế trái là N; nếu P < N thì vế trái là P.

**Ý nghĩa.** Với ảnh cũ, bạn phải chọn **một** action và chịu lỗ ở những state mà action kia tốt hơn. Bạn sẽ chọn phía có khối lỗ nhỏ hơn, nên mất min(P, N). Biết state hiện tại thì không mất gì. Vậy giá trị thông tin bằng **min(P, N)**. Đây là dạng EVPI (*expected value of perfect information*) cho bài toán hai action.

**Kiểm trên toy:**
- T-A: P = ½·1,2 = 0,6; N = ½·1 = 0,5 → min = 0,5 = Ḡ_S|M1 ✓
- T-AB và T-C′: P = 1, N = 0 → min = 0 ✓

### 6.3 Insight quan trọng: bất định không đồng nghĩa với thông tin có giá trị

Ở T-AB, S0 bất định tối đa (½–½), vậy mà thông tin **vô giá trị**: cả hai state đều đồng ý chọn Stay, nên biết thêm cũng không đổi quyết định. Thông tin chỉ có giá trị khi sự bất định **vắt qua biên quyết định**, tức là các state bất đồng về action tốt nhất (cả P và N đều dương).

### 6.4 Một cách đọc Ḡ_S (không phải phân rã nhân quả)

Từ S11 suy ra **Ḡ_S = Ḡ_S|M1 − Γ̄**:

| Toy | Ḡ_S | = Ḡ_S\|M1 (giá trị thông tin) | − Γ̄ (phần dính tới lỗi model) |
|---|---|---|---|
| T-A | +0,5 | 0,5 | 0 |
| T-AB | +0,5 | 0 | −(−0,5) |
| T-C′ | −0,5 | 0 | −(+0,5) |

Cùng một Ḡ_S = +0,5, nhưng ở T-A đó là thông tin thật, còn ở T-AB **toàn bộ** là bù lỗi cho M0. Câu số 7 của L4.1 ("trong AB, Ḡ_S lớn nhưng Ḡ_S|M1 nhỏ") chính là hiện tượng này trên dữ liệu.

⚠️ Final Review §2.2 nhắc: đây là **factorial contrast**, một cách đọc đại số, không phải hai phần nguyên nhân độc lập cộng lại. Hãy gọi nó là "cách đọc", đừng gọi là "phân rã nhân quả".

---

## 7. Cận của Γ̄ ràng buộc thiết kế card

### 7.1 Nhắc lại phép chứng minh ba dòng (đã học ở L4.1)

```text
Γ̄ = Ḡ_S|M1 − Ḡ_S ≥ −Ḡ_S      (vì Ḡ_S|M1 ≥ 0)
Γ̄ = Ḡ_M|S1 − Ḡ_M ≥ −Ḡ_M      (vì Ḡ_M|S1 ≥ 0)
⇒ Γ̄ ≥ −min(Ḡ_S, Ḡ_M)
```

### 7.2 Ba hệ quả

1. **Γ̄ ≤ −ε kéo theo cả Ḡ_S ≥ ε lẫn Ḡ_M ≥ ε.** Một claim "substitution ≥ 1%" đồng thời là claim "cả hai repair đều ≥ 1%". Nếu bạn có thêm card SV hoặc card MV, kết quả của chúng **phụ thuộc logic** vào nhau, không phải các bằng chứng độc lập.
2. **Ở đâu một trong hai contrast < ε, câu "không có substitution ≥ ε" là bắt buộc.**
3. **Ở đâu Ḡ_S < 0, Γ̄ > 0 là bắt buộc** (S12).

### 7.3 Một đối chứng phải có khả năng thất bại

Card v2 dùng thiết kế hai vùng. Ở **Ω⁺** claim dự đoán có hiệu ứng. Ở **Ω⁻** (chỉ lật κ sang [1; 3]) claim dự đoán không có. Verdict cần cả hai cùng đúng. Ω⁻ tồn tại để chứng minh hiệu ứng **đặc thù cho vùng**, không phải đúng ở mọi nơi. Giá trị của nó đến **hoàn toàn** từ việc nó có thể sai.

**Ví dụ tương tự.** Bạn kiểm một máy báo khói bằng hai phép thử: có khói thì phải kêu, không có khói thì không được kêu. Phép thử thứ hai chỉ có ý nghĩa nếu máy *có thể* kêu nhầm. Nếu bạn rút điện máy trước khi làm phép thử thứ hai, nó "đạt" chắc chắn nhưng không kiểm được gì.

**Áp vào một card SUB giả định.** Giả sử Ω⁻ được chọn bằng cách lật κ sang [1; 3], nơi các hiệu ứng nhỏ, hoặc lật sang vùng gây hại. Khi đó theo hệ quả 2 hoặc 3, dự đoán "không có substitution" **chắc chắn đúng**. Đó là máy báo khói đã rút điện.

**Đối chiếu với card v2:**
- **Ω⁻ của MV** ("Ḡ_M < 1%"): dấu của Ḡ_M bị ép ≥ 0, nhưng độ lớn thì không, nên đối chứng có thể thất bại ✓
- **Ω⁻ của SH** ("không gây hại"): Ḡ_S tự do về dấu, nên có thể thất bại ✓

Vậy cái bẫy này **đặc thù cho các claim về Γ̄**.

### 7.4 Một card SUB một vùng còn kiểm được gì?

Claim "đa số regime trong hộp có Γ̄ ≤ −ε" vẫn có thể sai. Nó sai khi Ḡ_S|M1 không đủ nhỏ so với Ḡ_S (vì Γ̄ = Ḡ_S|M1 − Ḡ_S), hoặc khi một trong hai contrast nhỏ hơn ε. Vậy nội dung kiểm được của nó là: **"ở đây, giá trị của state chủ yếu là bù lỗi cho M0"**.

Vì thế plan đề xuất: nếu chọn card SUB, dùng **một vùng** với `gamma_verdict` đã có, còn các vùng lân cận chỉ để mô tả.

---

## 8. 🔗 Liên hệ với việc bạn từng làm

- **RQ cũ "ngưỡng tĩnh vs độ rộng bất định".** Insight ở §6.3 trả lời trực tiếp nỗi băn khoăn cũ: bất định rộng chưa chắc làm thông tin có giá trị. Nó chỉ có giá trị khi vắt qua biên quyết định. Đây là một bài học rút từ repo cũ, giờ được viết thành công thức chính xác min(P, N).
- **Phase 1, L1.5 (đồng nhất thức regret r = |Δ|·1{Δ̂Δ < 0}).** Mọi toy hôm nay đều là phép đó, chỉ thêm bước lấy trung bình qua kính mờ.
- **Final Review §2.3 và §2.7. Đây là điểm phản biện quan trọng nhất của Part 2:** cả ba toy **không có hàng đợi nào**. AB và C ở đây sinh ra hoàn toàn từ logic ngưỡng cộng với phép lấy trung bình. Vậy thấy AB và C trên plant **chưa** chứng minh có một cơ chế động lực học hàng đợi đứng sau. Phân biệt giữa threshold null (H₀) và một giải thích bằng dynamics (H₁) là việc của Phase 6.

## 9. Part 2 cho phép nói gì

**Được nói:**
- Về mặt logic, cùng một lỗi của M0 có thể sinh ra cả lớp AB lẫn lớp C, tùy trung bình của lỗi rơi về phía nào của biên quyết định.
- Ḡ_S|M1 là giá trị thông tin, bằng min(P, N).
- Một card về Γ̄ với đối chứng "lật một nhân tố" có thể bị identity ép.

**Không được nói:**
- "AB và C cùng nguồn trong plant." Đó là ứng viên cơ chế, chờ Phase 6.
- "State value trong AB là giá trị thông tin." Nó có thể chủ yếu là bù lỗi model.
- "Ḡ_S = Ḡ_S|M1 − Γ̄ là phân rã nhân quả."

## 10. Reviewer có thể hỏi

1. *"Toy của bạn là số chọn tay. Chúng có phản ánh hàng đợi không?"* **Đã trả lời:** không; toy chỉ cho thấy khả năng về mặt logic.
2. *"Substitution có hiển nhiên không?"* **Trả lời được một phần:** theo hệ quả 1, một phần là hệ quả đại số; phần kiểm được là "Ḡ_S|M1 nhỏ". Câu hỏi về prior work để L4.5.
3. *"Vì sao không dùng đối chứng lật κ cho SUB như với MV và SH?"* **Đã trả lời** (§7.3).
4. *"AB và C có cần queue dynamics để giải thích không?"* **Chưa trả lời,** và toy cho thấy có thể là không. Để Phase 6.

## 11. ⚠️ Bẫy người mới

1. Thấy Ḡ_S > 0 rồi kết luận "thông tin state có giá trị". Phải xem thêm Ḡ_S|M1.
2. Nghĩ rằng S0 bất định nhiều thì thông tin tươi đáng giá nhiều.
3. Tìm **hai** cơ chế cho "state giúp" và "state hại", trong khi một cơ chế rơi về hai phía của ngưỡng là đủ giải thích.
4. Báo Γ̄ < 0 như bằng chứng độc lập với việc cả hai contrast ≥ 1%.
5. Dùng mutant rơi đúng điểm hòa (E[Δ̂] = 0) để minh họa cơ chế, rồi không nhận ra kết quả đến từ luật hòa.
6. Coi toy là bằng chứng cho cơ chế hàng đợi.

## 12. 🧠 Tư duy researcher

> Khi một can thiệp lúc giúp, lúc hại, **đừng vội tìm hai cơ chế**. Hãy hỏi trước: có phải chỉ một cơ chế, rơi về hai phía của một ngưỡng? Và: phần nào của kết quả sẽ vẫn xuất hiện ngay cả khi không có cơ chế vật lý nào, chỉ có logic quyết định?

## 13. Bài tập hiểu (khuyến nghị)

- **Toy thứ tư (Bước 3 của plan):** tự đặt một toy lớp **B**, tức sửa model có ích và sửa state gần như vô ích. Gợi ý: lỗi của M0 **cùng dấu ở mọi state**, nên tháo kính mờ không giúp gì.
- **Tính tay S10 cho T-A** mà không nhìn bài: P, N, rồi min(P, N).

## 14. Tự kiểm (tùy chọn)

1. Vì sao L̄10 giống nhau ở T-AB và T-C′?
2. Ở T-AB, vì sao Ḡ_S|M1 = 0 mà Ḡ_S = 0,5?
3. Đổi T-A thành Δ = (−1; +3). Ḡ_S|M1 thay đổi thế nào? Vì sao?
4. Một card SUB đặt Ω⁻ ở vùng gây hại. Vì sao đối chứng đó vô dụng?
5. Reviewer nói: "Bạn tìm thấy cả lớp AB lẫn lớp C, chứng tỏ queue dynamics phức tạp." Bác lại bằng toy.

## 15. Trạng thái Part 2

- **Hiểu biết cần có:** tính tay được ba toy; giải thích vì sao AB và C cùng nguồn trong toy; tự dẫn được S10; nói được vì sao đối chứng "lật một nhân tố" vô dụng với claim về Γ̄.
- **Việc nên làm khi thực thi:** ba toy (với T-C′ thay T-C, hoặc giữ T-C và sửa câu diễn giải) sẽ đi vào T07 addendum và golden test ở Part 3.
- **Phụ thuộc khoa học:** L4.5 dùng ba hệ quả ở §7.2 làm bộ lọc identity cho mọi card về interaction.
- **Có học tiếp được không?** Có. Part 3 nối toy với dữ liệu thật: vì sao δ = λB − λA có thể là thứ quyết định trung bình của M0 rơi về phía nào; cách đọc hai hình của bản đồ; vì sao bài dự đoán ở Bước 6 không còn mù và cách làm nó trung thực; và golden test bằng phân số. Khi muốn, bạn chỉ cần nói "tiếp tục Part 3".