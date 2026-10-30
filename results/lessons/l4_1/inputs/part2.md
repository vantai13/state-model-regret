# LESSON 4.1, Part 2/3: Phát biểu nào là phát hiện thật?

```text
L4.1  Part 1 ✓ Bản đồ là gì, vì sao cần record
      Part 2 ← BẠN Ở ĐÂY: identity / điều đã kỳ vọng / discovery ứng viên / sai
      Part 3   Errata, provenance, viết record, DL-103, exposure
```

## 1. Câu hỏi của Part 2

> Với một câu nói về bản đồ, nó thuộc loại nào: **identity**, **điều đã kỳ vọng**, **discovery ứng viên**, hay **sai / gây hiểu nhầm**? Vì sao chỉ loại thứ ba mới có thể thành card?

Nếu đọc nhầm loại, ba chuyện cụ thể sẽ xảy ra:

1. Bạn viết vào paper "chúng tôi phát hiện sửa model không bao giờ làm tệ hơn". Reviewer chỉ cần một câu là bác: *"đúng do cách bạn định nghĩa M1"*. Final Review §9.2 xếp loại kết quả này vào nhóm "obvious".
2. Bạn thiết kế một card mà vùng đối chứng (Ω⁻) **không thể thất bại**. Ví dụ: kiểm "Γ̄ > 0" ở vùng có Ḡ_S < 0. Card đó PASS chắc chắn, nhưng không kiểm được gì.
3. Bạn đếm một sự thật hai lần: "Ḡ_S|M1 nhỏ" và "Γ̄ < 0" trong lớp AB thực chất là **cùng một** quan sát (§6.3).

## 2. Mental model: bốn hộp và một câu hỏi kiểm tra

```text
Giả sử code đúng. Dữ liệu có THỂ làm câu này sai không?
   │
   ├── Không thể ──────────────────────────► IDENTITY
   │                                         (vai trò: test phát hiện bug, không phải phát hiện)
   └── Có thể
         │
         ├── Người hiểu hệ thống sẽ đoán trúng
         │   trước khi xem dữ liệu, gần như chắc ──► ĐIỀU ĐÃ KỲ VỌNG
         │                                         (ít tin mới; không bảo đảm toán học)
         ├── Không hiển nhiên ─────────────────► DISCOVERY ỨNG VIÊN
         │                                         (đáng kiểm trên điểm mới)
         └── Câu này mâu thuẫn raw, hoặc đọc
             sai thiết kế ──────────────────────► SAI / GÂY HIỂU NHẦM
```

Để dùng được cây này, bạn phải biết chắc câu nào thuộc nhánh "không thể sai". Đó là phần mini-lesson ngay dưới đây.

---

## 3. Mini-lesson: identity là gì?

### 3.1 Trực giác

**Đời thường.** Bạn đếm dân một làng và thấy "số người độc thân + số người đã kết hôn + … = tổng dân số". Đây không phải phát hiện, vì cách bạn chia nhóm buộc nó phải đúng. Nếu số liệu **không** khớp, bạn kết luận mình đếm sai, chứ không phải tìm ra một quy luật xã hội mới.

**Networking.** Bảo toàn traffic: lượng vào = lượng ra + phần backlog tăng thêm. Trên trace, nếu thấy đẳng thức này đúng thì đó là kiểm tra; nếu thấy nó sai thì đó là **bug** (mất bản ghi, lệch đồng hồ…).

**Định nghĩa.** *Identity* là phát biểu đúng **với mọi giá trị tham số**, chỉ do định nghĩa và giả định. Dữ liệu không thể bác nó, chỉ có thể lộ ra bug. Vì vậy identity là **invariant test**, không phải kết quả nghiên cứu.

### 3.2 Identity luôn có điều kiện

Đây là điểm người mới hay bỏ qua: identity đúng **trong hợp đồng này**, không đúng "với mạng nói chung". Hai điều kiện quan trọng nhất của T07 là:

- **B1.** S0 không ngây thơ. Nó biết snapshot đã cũ 1 s và tính **đúng** xác suất của state hiện tại theo luật thật (posterior Bayes chính xác). M1 là luật phản ứng thật.
- **B3.** Chỉ có hai action. Khi hòa thì chọn Stay.

Nếu đổi định nghĩa, identity có thể biến mất. Ví dụ: nếu M1 chỉ là "model tốt hơn M0 nhưng vẫn sai", hoặc S0 dùng ảnh cũ như thể đó là hiện tại, thì "sửa model không bao giờ làm tệ hơn" **không còn được bảo đảm**. Lúc đó nó trở thành câu hỏi thực nghiệm. Câu đúng phải là: *"đúng do cách ta định nghĩa repair (oracle)"*, không phải *"mạng có tính chất này"*.

### 3.3 Ba viên gạch

Ôn lại: với một state thật x, Δ(x) = J(Switch; x) − J(Stay; x). Vì chỉ có hai action, **regret tại một state chỉ có thể là 0** (chọn đúng) **hoặc |Δ(x)|** (chọn sai).

**Viên gạch 1: ô 11 là "sàn".** Ô 11 biết state thật và dùng luật thật, nên ở **mọi** x nó chọn action rẻ hơn. Mọi ô khác, tại mỗi x cụ thể, trả J(action đã chọn; x) ≥ min. Lấy trung bình hai vế ta được:

```text
L̄00, L̄01, L̄10  ≥  L̄11
⇒  Ḡ_SM = L̄00 − L̄11 ≥ 0
   Ḡ_S|M1 = L̄01 − L̄11 ≥ 0
   Ḡ_M|S1 = L̄10 − L̄11 ≥ 0          (S07)
```

**Viên gạch 2: trong hàng S0, M1 không thể thua M0.** Ô 00 và ô 01 thấy **cùng** snapshot y và cùng niềm tin về state hiện tại (B2). Với niềm tin đúng (B1), M1 tính được chi phí kỳ vọng thật của Stay và của Switch, rồi chọn cái nhỏ hơn. M0 chọn gì thì chi phí thật của nó cũng là một trong hai số đó, tức ≥ số nhỏ hơn. Ví dụ: với y cho trước, E[J(Stay)|y] = 10 và E[J(Switch)|y] = 11. M1 chọn Stay và trả 10; M0 trả 10 hoặc 11.

```text
Ḡ_M = L̄00 − L̄01 ≥ 0                  (S08)
```

**Viên gạch 3: đại số thuần.**

```text
Ḡ_S|M1 − Ḡ_S = (L̄01 − L̄11) − (L̄00 − L̄10) = L̄10 + L̄01 − L̄00 − L̄11 = Γ̄
Ḡ_M|S1 − Ḡ_M = (L̄10 − L̄11) − (L̄00 − L̄01) = Γ̄             (S11)
```

Ý nghĩa: **Γ̄ cho biết giá trị của sửa state thay đổi bao nhiêu khi model đã được sửa trước.** Interaction chính là hiệu giữa hai hiệu ứng có điều kiện.

### 3.4 Hai hệ quả, mỗi cái chỉ cần một dòng

```text
(S12)  Nếu Ḡ_S < 0:   Γ̄ = Ḡ_S|M1 − Ḡ_S ≥ 0 − Ḡ_S = |Ḡ_S| > 0
(cận)  Γ̄ = Ḡ_S|M1 − Ḡ_S ≥ −Ḡ_S   và   Γ̄ = Ḡ_M|S1 − Ḡ_M ≥ −Ḡ_M
       ⇒  Γ̄ ≥ −min(Ḡ_S, Ḡ_M)
```

Đọc bằng lời: hai repair có thể "chồng lấn" nhau, nhưng phần chồng lấn **không thể lớn hơn repair nhỏ hơn**.

### 3.5 Bức tranh gọn cần nhớ

| Contrast | Dấu |
|---|---|
| Ḡ_M, Ḡ_SM, Ḡ_S\|M1, Ḡ_M\|S1 | **Bị ép ≥ 0** |
| Ḡ_S | **Tự do**: model sai được cho thêm thông tin có thể quyết định tệ hơn (lớp C) |
| Γ̄ | Tự do một phần: bị chặn dưới bởi −min(Ḡ_S, Ḡ_M), và bị ép dương khi Ḡ_S < 0 |

**Hệ quả:** một **dấu** bị ép thì không bao giờ là phát hiện. Nhưng **độ lớn và vị trí** của cả sáu contrast vẫn có thể là phát hiện. T07 §6 ("danh sách có thể sai") nói đúng điều này.

### 3.6 Kiểm bằng số: toy T-C

Toy này lấy từ L4.2; L4.2 sẽ giải thích **vì sao** M0 tạo ra kết quả này. Ở đây ta chỉ dùng nó để kiểm identity.

Telemetry cũ 1 s nên S0 không biết mode hiện tại của B: x₁ = B đang OFF, x₂ = B đang ON, mỗi trường hợp xác suất ½. J(Stay) = 10 và J(Switch) = 11 ở cả hai state, tức Δ = +1: Stay luôn tốt hơn. M0 dự đoán sai: Δ̂(x₁) = −2 và Δ̂(x₂) = +3.

| Ô | Controller thấy gì → quyết định | Chi phí thật L̄ |
|---|---|---|
| 11 | Từng x: Δ = +1 → Stay | 10 |
| 01 | Trung bình E[Δ] = +1 → Stay | 10 |
| 00 | Trung bình E[Δ̂] = ½(−2) + ½(3) = +0,5 → Stay | 10 |
| 10 | x₁: Δ̂ = −2 → Switch (trả 11); x₂: +3 → Stay (trả 10) | 10,5 |

Kết quả: Ḡ_S = −0,5 (lớp C), Ḡ_M = 0, Ḡ_S|M1 = 0, Ḡ_M|S1 = 0,5, Γ̄ = 0,5.

Kiểm từng identity:
- S07: 0, 0, 0,5 đều ≥ 0 ✓
- S08: Ḡ_M = 0 ✓
- S11: Γ̄ = 0 − (−0,5) = 0,5 − 0 = 0,5 ✓
- S12: Γ̄ ≥ |Ḡ_S| = 0,5 ✓ (đúng bằng)

Toy này dạy hai điều:
1. Γ̄ = 0,5 trông như "interaction", nhưng nó **bị ép 100%**, không có gì để khám phá.
2. M0 sai ở **cả hai** state mà Ḡ_M vẫn bằng 0. Lý do: dưới ảnh cũ, hai lỗi của M0 trung bình ra đúng quyết định. Đây là ví dụ sống của *prediction error ≠ decision regret* (Final Review §1.3).

### 3.7 Trên dữ liệu thật, identity đóng vai test

Tôi đã kiểm trên bảng 1376 dòng của nhánh:
- S11 khớp tới 4·10⁻¹⁵.
- min Ḡ_M = 0; min Ḡ_S|M1 = −1,5·10⁻¹⁴.
- Trong lớp C, min Γ̄ = 1,09, không dòng nào vi phạm Γ̄ ≥ |Ḡ_S|.

Con số −1,5·10⁻¹⁴ là **sai số làm tròn của máy tính**, không phải vi phạm. Nếu thấy −0,01 thì đó mới là dấu hiệu bug.

PHASE_4 (mục K5) báo một trường hợp identity **bị vi phạm thật**: S04 (hai ô S1 không phụ thuộc tuổi quan sát) lệch tới 0,711% dưới engine pilot. Tôi chưa tự kiểm con số này. Nhưng nó cho thấy identity hữu ích nhất ở đâu: **bắt sai số của engine**. Part 3 sẽ dùng nó (errata E11).

---

## 4. Ba loại còn lại, mỗi loại có cái tinh tế riêng

### 4.1 "Điều đã kỳ vọng" khác identity ở đâu?

Lấy câu số 5: *"Ḡ_S|M1 không giảm khi age tăng."*

Ḡ_S|M1 là giá trị của việc biết state hiện tại, khi model đã đúng. Nó gần giống **EVPI** (*expected value of perfect information*): bạn sẵn sàng trả bao nhiêu để biết chính xác tình hình trước khi quyết định. Ảnh càng cũ, bạn càng biết ít, nên thông tin tươi càng đáng giá. Ai hiểu hệ thống cũng đoán được điều này.

**Vì sao nó vẫn không phải identity?** (Phần này *nice to know*.) Định lý Blackwell nói: nếu nguồn tin X là "bản mờ" của nguồn tin Y, tức tạo được X từ Y chỉ bằng cách thêm nhiễu mà không cần nhìn lại thế giới, thì X không bao giờ đáng giá hơn Y.

- Nếu snapshot chụp **toàn bộ** state (backlog + mode), ảnh 2 s trước đúng là bản mờ của ảnh 1 s trước. Lý do là tính Markov: đã biết ảnh 1 s trước thì ảnh 2 s trước không nói thêm gì về hiện tại.
- Nhưng snapshot ở đây **chỉ chụp backlog**, còn mode bị ẩn. Ảnh 1 s trước không còn "che" được ảnh 2 s trước, nên không có định lý nào bảo đảm thứ tự.

Kết luận: dự đoán hợp lý nhưng có thể sai ở vài regime. Tôi đã kiểm: 54/54 cấu hình tăng đơn điệu theo age. Kết quả này **khớp kỳ vọng**, nên mang rất ít tin mới.

### 4.2 "Discovery ứng viên" chưa có nghĩa là mới hay quan trọng

Lấy câu số 6, về vùng A (Ḡ_S ≥ 1%, Ḡ_M < 1%).

**Không bị ép.** Identity cho phép Ḡ_S mang bất kỳ dấu nào và Ḡ_M ≥ 0 với bất kỳ độ lớn nào. Không có gì buộc một vùng như vậy phải tồn tại.

**Nhưng không hoàn toàn bất ngờ:**
- "Thông tin tươi có giá trị khi quan sát cũ so với thời gian một mode kéo dài" đã có trong prior work (P04, nhóm literature về freshness).
- "Horizon ngắn thì lỗi mean-field của M0 nhỏ" cũng là một giải thích dễ nghĩ ra.

Vì vậy phần có thể mới chỉ nằm ở **"ở đâu, bao nhiêu, và Ḡ_M gần 0 cùng lúc"**. PHASE_4 §5.4 cũng nói vậy. Thêm vào đó, hiệu ứng nhỏ (trung vị 1,53%), sát ngưỡng, và theo K6 thì engine native cho Ḡ_S thấp hơn ở 8/8 điểm đã thử. Tôi chưa tự kiểm K6.

Ba khái niệm cần tách bạch: **ứng viên** (đáng kiểm) ≠ **mới** (phải lọc prior ở L4.5) ≠ **quan trọng** (phải qua baseline ở L4.4 và realism ở Phase 8).

### 4.3 Cùng một sự thật nói hai lần

Lấy câu số 7: *"Trong AB, Ḡ_S lớn nhưng Ḡ_S|M1 nhỏ."*

Theo S11, Γ̄ = Ḡ_S|M1 − Ḡ_S. Nên "Ḡ_S lớn + Ḡ_S|M1 nhỏ" **tự động** cho ra "Γ̄ âm mạnh". Hai câu "có substitution" và "Ḡ_S|M1 nhỏ" là **một** quan sát viết hai cách.

Phần có thể sai chỉ là "Ḡ_S|M1 nhỏ": identity chỉ đòi Ḡ_S|M1 ≥ 0, không đòi nó nhỏ. Ý nghĩa vật lý của nó: khi model đúng, ảnh cũ đã gần đủ để quyết định, và thông tin tươi chủ yếu dùng để bù lỗi cho M0.

Dữ liệu tôi đã kiểm:
- Trung vị Ḡ_S = 4,96, trung vị Ḡ_S|M1 = 0,71; 155/161 dòng có Γ̄ < 0.
- Ví dụ cực trị XM2X077: Ḡ_S = 20,39, Ḡ_M = 37,75, Γ̄ = −20,39 = −min, Ḡ_S|M1 = 0. Điểm này **chạm đúng cận** ở §3.4.

### 4.4 Sai / gây hiểu nhầm: ba kiểu khác nhau

**Đếm một chiều hai lần (câu 4: "age là chiều mới").** Plant là fluid, các tốc độ cố định trong mỗi mode. Nhân age, κ và h cùng một hệ số thì backlog và chi phí đổi theo cùng tỉ lệ, nên mọi % contrast giữ nguyên. Vì vậy (age a, κ, h) ≡ (1, κ/a, h/a). Map3age chỉ là thêm điểm vào mặt phẳng (κ/τ, h/τ) đã có. L4.2 sẽ chứng minh kỹ.

**Đọc mẫu như tần suất (câu 8: "A có 301 regime").** Xem Part 1, §9.

**Hiệu ứng mẫu số (câu 9: "biên độ ±4 làm mọi hiệu ứng lớn lên").** Mọi số đều tính theo % C̄_ref. Nếu C̄_ref nhỏ đi thì % phồng lên dù hiệu ứng tuyệt đối gần như không đổi. Tôi đã kiểm: trung vị C̄(±4)/C̄(±6) = **0,32**, trong khi Ḡ_M|S1 tính tuyệt đối chỉ tăng khoảng **15%** (trung vị). Ngoài ra, biên độ ±4 là **plant khác hợp đồng**, nên nằm ngoài scope.

---

## 5. Phân loại 10 phát biểu

Nếu muốn tự thử, che bảng dưới, dùng cây ở §2 rồi mới đọc.

| # | Phát biểu | Nhãn | Lý do | Kiểm trên data (tôi chạy) |
|---|---|---|---|---|
| 1 | Không có vùng nào sửa model làm tệ hơn | **Identity** (có điều kiện B1) | Ḡ_M ≥ 0 (S08); Ḡ_M\|S1 ≥ 0 (S07) | min Ḡ_M = 0 |
| 2 | State chỉ gây hại khi model sai | **Identity** | Ḡ_S\|M1 ≥ 0 (S07) | min = −1,5·10⁻¹⁴ (làm tròn) |
| 3 | Trong lớp C, Γ̄ > 0 | **Identity** | C nghĩa là Ḡ_S ≤ −1, nên Γ̄ ≥ 1 (S12) | min Γ̄ trong C = 1,09; 0 vi phạm |
| 4 | Age là một chiều mới | **Sai** | Age chỉ là đổi thang thời gian (E2) | — |
| 5 | Ḡ_S\|M1 không giảm khi age tăng (54/54) | **Đã kỳ vọng** | Trực giác EVPI; không có thứ tự Blackwell vì mode bị ẩn | 54/54 ✓ |
| 6 | Vùng A: Ḡ_S ≥ 1%, Ḡ_M < 1% ở h ngắn, κ 0,2–1 s | **Discovery ứng viên** | Không bị ép; phần mới chỉ có thể là "ở đâu, bao nhiêu"; nhỏ, sát ngưỡng | — |
| 7 | Trong AB, Ḡ_S lớn nhưng Ḡ_S\|M1 nhỏ | **Discovery ứng viên** (chỉ phần "Ḡ_S\|M1 nhỏ") | Γ̄ < 0 là hệ quả đại số, không đếm riêng | 4,96 so với 0,71; 155/161 |
| 8 | A có 301 regime | **Gây hiểu nhầm** nếu đọc như tần suất | Số đếm do map2 dồn mẫu (E6) | Lưới đều: 21/344 |
| 9 | Biên độ ±4 làm mọi hiệu ứng lớn lên | **Gây hiểu nhầm + ngoài plant** | Phần lớn là hiệu ứng mẫu số | C̄ ratio 0,32; tuyệt đối +15% |
| 10 | J là "cộng hưởng" giữa hai repair | **Phần lớn identity + tên gây hiểu nhầm** | 8/14 dòng có Ḡ_S < 0 nên Γ̄ > 0 bị ép; 6 dòng còn lại có Γ̄ ≤ 1,11%. Final Review §2.3 cho thấy ngưỡng quyết định một mình đã tạo được Γ ≠ 0, nên "cộng hưởng" ngụ ý một cơ chế chưa hề được chứng minh | 8/14 ✓; max 1,11 ✓ |

Chỉ hai dòng 6 và 7 sống sót để đi tiếp sang L4.5. Kết quả này khớp với đánh giá của REGIME_MAP, nhưng giờ bạn biết **vì sao**, và đã có số tự kiểm.

---

## 6. 🔗 Liên hệ với việc bạn từng làm

- **Phase 1 (L1.5) và Final Review §2.3: phản ví dụ "interaction không cần queue".** Hai sai số cộng đơn giản, e_S = e_M = 3, cho Γ = 2 chỉ vì gap dự đoán đi qua số 0. Câu 10 là phiên bản trên dữ liệu thật của đúng bài học đó.
- **Final Review §2.7: "threshold identity khác một null có thể bị bác bỏ".** Công thức regret là identity; không thể tìm ra phần regret nào "vượt khỏi" nó. Đây cùng tinh thần với Part 2: thứ không thể sai thì không phải phát hiện.
- **T07 và danh sách S01–S18 được soạn theo ủy quyền**, và chính file ghi "Understanding/ownership OPEN". Part 2 là lần đầu bạn tự dẫn S07, S08, S11, S12 với số cụ thể. Đây là bước thật để đóng mục OPEN đó.

## 7. Part 2 cho phép nói gì

**Được nói:**
- Bốn trong sáu contrast có dấu bị ép bởi định nghĩa oracle.
- Γ̄ > 0 trong vùng harm là bắt buộc.
- Trong số phát biểu của bản đồ, chỉ "vùng A" và "Ḡ_S|M1 nhỏ trong AB" là discovery ứng viên.

**Không được nói:**
- "Chúng tôi phát hiện sửa model không bao giờ gây hại."
- "Có hiện tượng cộng hưởng."
- "Substitution và Ḡ_S|M1 nhỏ là hai phát hiện."
- "Vùng A là kết quả mới." Nó mới chỉ là ứng viên, novelty chưa được lọc.

## 8. Reviewer có thể hỏi

1. *"Ḡ_M ≥ 0 chẳng phải chỉ vì M1 là model thật sao?"* **Đã trả lời:** đúng, do định nghĩa; ta không claim nó.
2. *"Γ̄ > 0 trong vùng harm có gì mới?"* **Đã trả lời:** không có gì mới (S12).
3. *"Substitution chẳng phải hiển nhiên sao, khi hai repair cùng sửa một lỗi?"* **Chưa trả lời:** đây là rủi ro "already implied", L4.5 sẽ đối chiếu `prior_boundary.md` và `already_implied.md`.
4. *"Vùng A có sống được khi so với một controller có margin không?"* **Chưa trả lời:** L4.4.

## 9. ⚠️ Bẫy người mới

1. Gọi một identity là "kết quả bền vững vì 1376/1376 dòng đều thỏa". Nó thỏa vì **không thể không thỏa**.
2. Quên rằng identity có điều kiện. Đổi S0 thành ngây thơ, hoặc M1 thành "model tốt hơn", thì các câu 1 và 2 không còn được bảo đảm.
3. Coi −1,5·10⁻¹⁴ là vi phạm, hoặc ngược lại, coi một vi phạm thật như S04 (0,7%) là làm tròn.
4. Báo Γ̄ < 0 và "Ḡ_S|M1 nhỏ" như hai bằng chứng độc lập.
5. Đánh đồng "discovery ứng viên" với "novel".
6. Thiết kế đối chứng cho card về Γ̄ ở nơi identity ép kết quả (vùng harm, hoặc nơi một contrast < 1%).

## 10. 🧠 Tư duy researcher

> Trước khi gọi một pattern là phát hiện, hãy hỏi: **"Nếu code đúng, dữ liệu có cách nào làm câu này sai không?"** Nếu không, nó là test, không phải tri thức mới. Còn nếu có, hãy hỏi tiếp: một người hiểu hệ thống có đoán được nó trước khi nhìn dữ liệu không?

## 11. Bài tập hiểu (khuyến nghị, không cần gửi lại)

- Chứng minh lại Γ̄ ≥ −min(Ḡ_S, Ḡ_M) trên giấy trong ba dòng, không nhìn bài.
- Tự đặt một toy hai state trong đó S0 là **ngây thơ** (dùng ảnh cũ như hiện tại) và Ḡ_M < 0. Nếu làm được, bạn đã tự thấy identity phụ thuộc điều kiện B1 như thế nào.

## 12. Tự kiểm (tùy chọn)

1. Bốn contrast nào có dấu bị ép, và bởi identity nào?
2. Vì sao Ḡ_S lại tự do về dấu, trong khi Ḡ_M thì không?
3. Ở toy T-C, M0 sai ở cả hai state mà Ḡ_M = 0. Giải thích bằng một câu.
4. Một card claim "Γ̄ ≤ −1% trong hộp X". Claim này ngầm đòi hai điều gì khác?
5. Reviewer nói "J là cộng hưởng vì Γ̄ ≥ max(Ḡ_S, Ḡ_M) ở cả 14 dòng". Bác lại bằng hai lý do.

## 13. Trạng thái Part 2

- **Hiểu biết cần có:** tự dẫn được S07, S08, S11, S12 và cận của Γ̄; dùng được cây bốn hộp; biết vì sao chỉ câu 6 và 7 đi tiếp.
- **Việc nên làm khi thực thi:** bảng phân loại này sẽ thành mục (5) của record. Nhãn provenance của nó là "tác giả kiểm lại" nếu bạn tự làm lại được, còn không thì giữ "AI soạn".
- **Phụ thuộc khoa học:** L4.5 dùng ba hệ quả của cận Γ̄ làm bộ lọc identity. Hiểu sai ở đây thì có thể khóa một card không bao giờ thất bại.
- **Có học tiếp được không?** Có. Part 3 nặng phần thực thi hơn: errata E9–E14, bốn nhãn provenance, viết record (kể cả cách xử lý khi thiếu `recount_map.py`), DL-103 về đánh số phase, và dòng exposure. Khi muốn, bạn chỉ cần nói "tiếp tục Part 3".