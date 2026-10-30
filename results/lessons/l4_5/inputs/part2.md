# LESSON 4.5, Part 2/2: Sàng khả thi, multiplicity, và quyết định của bạn

```text
L4.5  Part 1 ✓ Độ phủ RQ, premise, ba bộ lọc định tính
      Part 2 ← BẠN Ở ĐÂY: khả thi · baseline · multiplicity · "0 card" · phương án · trình tự
      → Lesson Gate L4.5
```

### 0. Những gì tôi đã kiểm cho Part 2

- **Power khi có UNRESOLVED.** Tôi tính bằng hàm `robust_region_power` của repo. Hàm này mô phỏng đúng cách scorer xử lý điểm UNRESOLVED (luật R4 xét bốn góc, và R5 chặn nếu tỉ lệ UNRESOLVED quá cao), không giả định gì thêm.
- **Xác suất R5 làm một vùng thành INCONCLUSIVE**, tính bằng `r5_failure`.
- **Tôi cố ý không tính p̂ cho hộp nào**, kể cả trên nhãn pilot. Luật sàng của bạn chưa được khóa. Tính trước tức là tự tạo ra một forking path ẩn cho chính bạn.

---

## 1. Câu hỏi của Part 2

> Với mỗi ứng viên còn sống sau ba bộ lọc định tính, nếu đưa nó vào lần confirmation duy nhất thì **khả năng nó cho được một kết luận** là bao nhiêu? Cái giá phải trả là gì? Và quyết định cuối cùng nên được viết ra như thế nào?

---

## 2. Bộ lọc 5: khả thi, và vì sao p̂ trên discovery luôn lạc quan

### 2.1 Trực giác

Điểm thi thử luôn cao hơn điểm thi thật nếu bạn tự chọn đề thi thử đúng sở trường của mình.

### 2.2 Ba nguồn lạc quan

**(a) Chọn hộp sau khi đã nhìn dữ liệu.** Hiện tượng này gọi là *winner's curse* hay *regression to the mean*.

Ví dụ minh họa với số làm tròn:
- Giả sử có 10 hộp ứng viên, hộp nào cũng có tỉ lệ thật p = 0,7, và mỗi hộp có khoảng 30 điểm.
- Tỉ lệ quan sát p̂ của mỗi hộp dao động quanh 0,7 với độ lệch chuẩn khoảng √(0,7·0,3/30) ≈ 0,08.
- Nếu chọn hộp **đẹp nhất trong 10**, p̂ của nó trung bình khoảng 0,7 + 1,54 × 0,08 ≈ **0,83**, dù không hộp nào thật sự tốt hơn hộp nào.
- Nếu chỉ thử 3 hộp, độ lạc quan còn khoảng +0,85 × 0,08 ≈ **+0,07**.

Đó là trực giác đằng sau hai luật của plan: **trừ 0,10** và **tối đa 3 hộp cho mỗi ứng viên**. Con số 0,10 là một quy ước bảo thủ, không phải kết quả suy ra từ toán.

**(b) Lưới điểm khác measure của card.** Card rút κ và h theo phân phối log-đều, còn lưới discovery thì không. Tỉ lệ đếm trên lưới không phải tỉ lệ dưới cách lấy mẫu của card.

**(c) Engine pilot khác engine chấm.** Native thấp hơn pilot một cách có hệ thống (L4.3).

### 2.3 Luật sàng của plan, và ba đề xuất của tôi

**Luật của plan** (bạn khóa trước khi tính):

```text
p̂        = tỉ lệ MEETS trên NHÃN NATIVE của điểm discovery trong hộp (UNRESOLVED tính là FAILS)
p⁺_plan  = p̂ − 0,10
Card hai vùng: thêm nếu P(PASS | n = 60, p⁺_plan, p⁻_plan = 0,2) ≥ 0,5
Card một vùng: thêm nếu P(S | n = 60, p⁺_plan) ≥ 0,5
Tỉ lệ sẽ UNRESOLVED trong hộp ≤ 5%;  tối đa 3 hộp mỗi ứng viên, mỗi hộp một mục forking log
```

**Đề xuất của tôi:**

1. **Dùng hàm `robust_pass_power` có sẵn trong repo.** Hàm này nhận tỉ lệ MEETS có điều kiện và tỉ lệ UNRESOLVED r̂ riêng biệt, rồi tính đúng cách scorer xử lý R4 và R5. Luật của plan vừa tính UNRESOLVED là FAILS **vừa** đặt thêm một trần 5%, nên phần nào đếm UNRESOLVED hai lần. Hàm robust mô hình hóa đúng một lần. *Khuyến nghị: dùng.*
2. **Tùy chọn: tách mẫu thay vì trừ 0,10 cố định.** Chia điểm discovery thành hai nửa theo một seed đã đăng ký; chọn hộp trên nửa thứ nhất, ước lượng p̂ trên nửa thứ hai. Cách này khử winner's curse có cơ sở hơn, nhưng mỗi nửa chỉ còn một nửa số điểm: vùng A còn khoảng 225, dải δ của SUB còn khoảng 39.
3. **Tùy chọn: gán trọng số cho điểm theo measure của card** (log-đều cho κ và h) để giảm nguồn lạc quan (b).

Tôi khuyên dùng đề xuất 1, và giữ luật trừ 0,10 làm mặc định vì đơn giản. Bạn quyết.

**Một dòng phải có trong file luật sàng:** *"Khi viết luật này tôi đã thấy các p̂ pilot minh họa trong PHASE_4: 72,8% cho một hộp vùng A, 94,9% cho dải δ."*

### 2.4 Đọc bảng power

Bảng dưới đã được tôi tái tạo bằng hàm của repo, với n = 60, α = 1/40, π₀ = ½.

**Không có UNRESOLVED:**

| p⁺ thật | 0,60 | 0,65 | 0,70 | 0,75 | 0,80 |
|---|---:|---:|---:|---:|---:|
| P(PASS), card hai vùng | 0,256 | 0,558 | 0,836 | 0,968 | 0,996 |
| P(S), card một vùng | 0,257 | 0,559 | 0,838 | 0,970 | 0,998 |

**Có UNRESOLVED, vùng Ω⁺, dùng `robust_region_power`:**

| p (MEETS / đã phân giải) | r = 0 | r = 5% | r = 10% |
|---|---:|---:|---:|
| 0,70 | 0,838 | 0,645 | 0,331 |
| 0,75 | 0,970 | 0,867 | **0,500** |
| 0,80 | 0,998 | 0,955 | 0,586 |

**Hai điều cần thấy:**
1. Với p⁺ = 0,6, **ba trên bốn lần bạn sẽ không PASS**, ngay cả khi hiện tượng có thật.
2. UNRESOLVED kéo power xuống mạnh. Với p = 0,75, nếu 10% điểm UNRESOLVED thì cơ hội PASS chỉ còn một nửa.

### 2.5 Vì sao trần UNRESOLVED là 5%

Theo `r5_failure` với n = 60:
- Nếu tỉ lệ UNRESOLVED thật là 5%, xác suất vượt 10% (R5 kích hoạt, vùng thành INCONCLUSIVE) là khoảng **3%**.
- Nếu tỉ lệ thật là 8%, xác suất đó tăng lên khoảng **20%**.

Trần 5% giữ rủi ro "mất cả card vì không đo được" ở mức nhỏ.

**Liên hệ với ứng viên SV:** hiệu ứng nhỏ cộng sát ngưỡng cho thấy đây là chỗ SV dễ trượt nhất.

---

## 3. Bộ lọc 4: baseline (cần kết quả của L4.4)

| Ứng viên | Xem gì | Đọc thế nào |
|---|---|---|
| **SV** | Ḡ_S^ρ\* và ΔL̄10 trong hộp | Áp **điều kiện đối thủ** ở L4.4 Part 2 §3.2. Nếu margin làm controller tệ đi (giống toy T-A), thì giá trị của state "biến mất khi có margin" **không** phải lý do để loại SV |
| **SUB** | R_M(ρ\*) và Ḡ_S^ρ\* trong dải δ | Nếu margin lấy lại gần hết Ḡ_M (giống T-AB), câu của SUB sẽ rất hẹp: "hai repair thay thế nhau so với controller không margin". Câu hỏi khi đó: một câu hẹp như vậy có đáng chiếm một suất F2 không? |

Đây là phán đoán của bạn. Nếu muốn chặt chẽ, có thể viết trước một luật, ví dụ: *"nếu trung vị R_M(ρ\*) ≥ ½ trong hộp SUB, thì claim của SUB phải ghi kèm 'so với controller không margin'; card vẫn được phép, nhưng phải cân nhắc lại suất."*

---

## 4. Khái niệm 5: multiplicity, family riêng, báo hết mọi verdict

**Trực giác.** Mua thêm vé số làm tăng xác suất có ít nhất một vé trúng, kể cả khi không vé nào "đáng" trúng.

**Định nghĩa.** **FWER** (family-wise error rate) là xác suất có **ít nhất một** PASS sai trong một họ phép kiểm. **Bonferroni** là cách chặn FWER bằng tổng α của từng phép kiểm.

| Family | Card | α mỗi card | FWER (cận) |
|---|---|---|---|
| F1 (card v2, đã khóa) | MV, SH | 1/40 | ≤ 1/20 |
| F2 (card set v3, nếu có) | ≤ 2 card | 1/40 | ≤ 1/20 |
| Cả hai family | | | ≤ 1/10, theo cận hợp P(A ∪ B) ≤ P(A) + P(B) |

**Vì sao không gộp card mới vào F1?** Gộp vào thì α của từng card F1 phải giảm, tức là sửa một luật đã khóa. Vì vậy card mới phải thuộc **family F2, khai báo trước**.

**Mọi verdict của F1 và F2 đều phải được báo**, bất kể kết quả ra sao. Chỉ báo các PASS là cách nhanh nhất biến multiplicity thành tự lừa mình.

---

## 5. Khái niệm 6: "không thêm card" là một kết quả hợp lệ

**Trực giác.** Đừng mang theo dụng cụ mà bạn sẽ không dùng.

Nếu SV trượt sàng khả thi và SUB trượt prior hoặc baseline, thì không có card set v3. Khi đó:
- Bản đồ vẫn là một discovery có record đầy đủ.
- Phase 4 đóng nhanh hơn: bỏ L4.6–L4.7, đi thẳng tới L4.8.
- DL "0 card" phải nói rõ paper được viết gì về bản đồ: chỉ mô tả discovery, gắn nhãn rõ ràng.
- Câu về "differ" sẽ là "mới cho thấy một nửa"; câu về "interact" chỉ ở mức chẩn đoán.

Đây là một kết quả trung thực, không phải thất bại.

---

## 6. Các phương án và hệ quả

| Phương án | RQ nhận được gì nếu PASS | Rủi ro chính | Chi phí và hệ quả |
|---|---|---|---|
| **0 card** | Không có gì thêm. "differ" mới một nửa; "interact" chỉ chẩn đoán | Paper mỏng ở hai động từ của RQ | Rẻ nhất. HOLD ở κ/τ = 0,05 không còn chặn claim nào. Buổi đọc P0-V10 gọn hơn |
| **Chỉ SV** | Phân ly kép cho "differ" | Power thấp (hiệu ứng nhỏ, sát ngưỡng), dễ ra WEAKEN hoặc INCONCLUSIVE | Vùng A (h/τ ≤ 4) nằm **ngoài** frame của card v2, nên cần numerics coverage ở L4.7. Horizon ngắn nên chạy rẻ |
| **Chỉ SUB** | Phép kiểm interaction không bị ép duy nhất | Prior chưa được chấm (PC3); baseline có thể thu hẹp câu; δ là trục post hoc; numerics ở κ/τ = 0,05 | Hoặc giải quyết HOLD, hoặc giới hạn hộp ở κ/τ ∈ [0,1; 0,15] **vì lý do validity, có ghi forking log**. h/τ từ 4 đến 8 nên đắt hơn |
| **Cả hai** | Phủ cả "differ" lẫn "interact" | Cộng dồn mọi rủi ro trên; khả năng có ít nhất một INCONCLUSIVE cao hơn | Hai frame numerics, compute nhiều hơn; FWER của F2 ≤ 1/20 |

### Khuyến nghị có điều kiện của tôi

Đây chưa phải quyết định, vì chưa có nhãn native và chưa có baseline.

> **Hãy để luật sàng quyết định, đừng để cảm giác quyết định.**

Với những gì đã biết hiện nay:
- **SUB** có triển vọng khả thi tốt hơn, vì hiệu ứng lớn. Nhưng nó phải qua ba cửa: bạn **tự chấm** dòng prior PC3; baseline trong dải δ không lấy lại gần hết Ḡ_M; và numerics ở hộp cuối cùng được giải quyết.
- **SV** có giá trị cao cho RQ, nhưng khả năng qua sàng đáng ngờ. Nếu sau khi có nhãn native và trừ 0,10 mà P(PASS) < 0,5, hãy bỏ SV một cách trung thực và viết câu về "differ" như mới cho thấy một nửa.

Kết cục tôi thấy nhiều khả năng nhất là **1 card (SUB)**, hoặc **0 card** nếu SUB trượt prior hay baseline. Nhưng thứ quyết định là luật bạn khóa trước, không phải dự đoán này của tôi.

---

## 7. Trình tự thực thi thực tế (nối với tình trạng hiện tại)

```text
(1) L4.5 Part A: bộ lọc 1–3; tự chấm prior PC3 và các dòng freshness        ← làm được ngay
(2) Khóa luật sàng khả thi (commit trước mọi p̂), ghi các p̂ pilot đã thấy     ← làm được ngay
(3) L4.4 spec.md: baseline, luật chọn ρ*, luật đọc, dự đoán của bạn           ← làm được ngay
(4) MỘT lần chạy native, có prereg mới:
      nhãn native cho vùng của ứng viên còn sống + các ô baseline
      (+ numerics coverage ở κ/τ = 0,05, chỉ khi SUB còn sống và hộp chạm tới đó)
(5) L4.5 Part B: tối đa 3 hộp mỗi ứng viên; mỗi hộp một mục forking log
(6) DL quyết định 0/1/2 card (bạn ký) → L4.6 hoặc L4.8
```

Ba bước (1)–(3) không cần compute. Chúng là ba quyết định của bạn, và cùng nhau chúng xác định chính xác lần chạy (4) cần gì, nhờ vậy không phải chạy đi chạy lại.

---

## 8. Code: bộ khung `screen.py` (chưa chạy, vì chưa có nhãn native)

**Code này tồn tại để trả lời:** trên dữ liệu discovery đã gán nhãn native, hộp này tóm tắt ra sao, và power dự kiến bao nhiêu? Kết quả chỉ để **sàng**, không phải evidence.

```python
"""screen.py — L4.5 Part B skeleton. Discovery only; never evidence. Rules must be committed first."""
from fractions import Fraction as F
from experiments.R3R_07_confirmation import power

def screen_box(native_rows, box, rules, cf_keys, metric, meets):
    pts = [r for r in native_rows if box(r)]
    if any(r["key"] in cf_keys for r in pts):
        raise RuntimeError("box touches a CF-v2 regime")             # read discovery only
    n = len(pts)
    if n == 0:
        return dict(n=0, decision="EMPTY")
    unresolved = sum(r["label"] == "UNRESOLVED" for r in pts)
    resolved = [r for r in pts if r["label"] != "UNRESOLVED"]
    p_cond = F(sum(meets(r[metric]) for r in resolved), max(len(resolved), 1))
    r_hat = F(unresolved, n)
    p_plan = max(p_cond - rules["haircut"], F(0))                    # e.g. haircut = 1/10
    pw = (power.robust_region_power(60, p_plan, r_hat, plus=True) if rules["one_region"]
          else power.robust_pass_power(60, p_plan, rules["p_minus"], r_hat, r_hat))
    ok = pw >= rules["min_power"] and r_hat <= rules["max_unresolved"]
    return dict(n=n, p_cond=float(p_cond), r_hat=float(r_hat), p_plan=float(p_plan),
                power=float(pw), decision="PASS_SCREEN" if ok else "FAIL_SCREEN")
    # caller appends one forking-log entry per box tried (max 3 per candidate)
```

**Test nên có:**
- Hộp rỗng cho 0 điểm.
- Hộp bao toàn bộ cho đúng tổng số điểm.
- Với r = 0, power tái tạo được bảng ở §2.4.
- Hộp chạm vào một khóa CF thì bị từ chối.

Lưu ý: dòng Ω⁻ dùng chung r̂ cho cả hai vùng chỉ để minh họa. Khi viết thật, r̂ của Ω⁻ phải ước lượng riêng.

---

## 9. DL quyết định và claim boundary

**DL quyết định (bạn ký) cần có:**
- Số card (0, 1 hay 2) và card nào.
- Premise đã đổi, có trích DL-073.
- Kết quả của năm bộ lọc cho từng ứng viên.
- Các phương án đã cân nhắc (§6).
- Hệ quả: ngân sách, lịch, multiplicity, phạm vi buổi đọc P0-V10.
- Dòng "Ai quyết: tác giả".

**Nháp claim boundary v1.4, viết theo từng kết cục:**
- **0 card:** "Regime map là discovery do AI thiết kế và chạy. Không có claim đã xác nhận về state value dương hay về substitution. 'differ' mới được kiểm qua MV và SH."
- **Có SUB:** "Nếu SUB PASS: trong Ω_SUB⁺, đa số regime có Γ̄ ≤ −1% ở mức mô hình. Câu này kéo theo cả hai repair đều ≥ 1%. Kèm câu baseline theo luật đọc."
- **Có SV:** "Nếu SV PASS: trong Ω_SV⁺, đa số regime có Ḡ_S ≥ 1%. Đặt cạnh MV, đây là phân ly kép ở mức mô hình. Không claim 'thông tin tươi có giá trị' là mới."

---

## 10. 🔗 Liên hệ với việc bạn từng làm

- **Luật chọn n trong DL-077 và bảng power ở L3R.6.** Bảng power hôm nay dùng chính các hàm đó. Lúc ấy bạn dùng nó để chọn n cho MV và SH; bây giờ dùng để quyết định có nên thêm card hay không.
- **DL-073, "phương án D".** Hôm đó không cấp suất cho interaction vì không có vùng nào đủ lớn. Hôm nay câu hỏi được mở lại, đúng lúc, đúng luật.

## 11. Toàn bộ L4.5 cho phép nói gì

**Được nói** (sau khi thực thi): "Tôi đã quyết định kiểm (hoặc không kiểm) thêm X vì những lý do cụ thể, theo luật viết trước, và biết cái giá của từng lựa chọn."

**Không được nói:**
- p̂ trên discovery là tần suất hay evidence.
- Claim mới đúng hay sai. Đó là việc của Phase 5.

## 12. Reviewer có thể hỏi

1. *"Các anh đã thử bao nhiêu hộp?"* Trả lời bằng forking log, tối đa 3 hộp mỗi ứng viên.
2. *"Card mới có làm tăng xác suất PASS sai không?"* **Đã trả lời:** family F2 riêng, FWER ≤ 1/20, và báo hết mọi verdict.
3. *"Card có đủ power không?"* Trả lời bằng luật sàng với p̂ native, trừ 0,10, và hàm robust.
4. *"Vì sao không kiểm state value dương?"* Nếu chọn 0 card SV, trả lời bằng kết quả sàng, và thừa nhận "differ" mới được thấy một nửa.

## 13. ⚠️ Bẫy người mới

1. Tin p̂ thô trên discovery để tính power.
2. Thử hộp thứ 4, thứ 5 "chỉ để xem".
3. Chọn hộp đẹp nhất rồi đặt ngưỡng sàng sao cho hộp đó qua.
4. Gộp card mới vào F1.
5. Chỉ báo những verdict PASS.
6. Nghĩ "0 card" là thất bại.
7. Thu hẹp hộp SUB để tránh κ/τ = 0,05 mà không ghi lý do validity vào forking log.

## 14. 🧠 Tư duy researcher

> Một phép kiểm đáng thêm phải vượt qua cả ba câu hỏi: **nó lấp chỗ nào của câu hỏi**, **nó có thể sai không**, và **nó có đủ sức cho ra một kết luận không**. Thiếu câu nào thì nó chỉ làm tăng multiplicity và tiêu tốn lần confirmation duy nhất.

## 15. Bài tập hiểu (khuyến nghị)

- **Viết file luật sàng** (rule 4 của plan, cộng hoặc không cộng các đề xuất của tôi), có câu "đã thấy các p̂ pilot minh họa".
- **Tự trả lời bằng một câu:** với SV, giá trị p⁺_plan tối thiểu để qua sàng là bao nhiêu? (Gợi ý: xem bảng §2.4, ngưỡng P ≥ 0,5.)

## 16. Tự kiểm (tùy chọn)

1. Với p̂ = 0,73 trên discovery, vì sao không nên tin P(PASS) khoảng 0,9?
2. Vì sao UNRESOLVED 10% với p = 0,75 làm power giảm từ 0,97 xuống 0,50?
3. Vì sao không thể thêm card mới vào F1?
4. Khi nào "0 card" là quyết định đúng? Paper khi đó được nói gì về bản đồ?
5. Giới hạn hộp SUB ở κ/τ ≥ 0,1 vì numerics HOLD có phải là forking path xấu không? Cần ghi lại gì?

---

## 17. LESSON GATE: L4.5

**Hiểu biết.** Sau L4.5, bạn nên tự giải thích được:
- Bảng độ phủ RQ và khái niệm phân ly kép.
- Luật xem lại premise.
- Năm bộ lọc, áp cho SV và SUB.
- Ba nguồn lạc quan của p̂; luật trừ 0,10 và giới hạn 3 hộp.
- Cách đọc bảng power, có và không có UNRESOLVED; trần 5%.
- Family F2 và FWER.
- "0 card" là một kết quả.
- Bốn phương án và hệ quả của từng phương án.

**Trạng thái thực thi:** chưa bắt đầu.
- Làm được ngay, không cần compute: Part A (bộ lọc 1–3, chấm prior) ⬜; luật sàng ⬜.
- Bị chặn: Part B (cần nhãn native và baseline) ⬜; DL quyết định ⬜.

**Phụ thuộc khoa học:**
- Luật sàng phải được commit trước khi tính p̂ cho bất kỳ hộp nào.
- DL quyết định phải có trước L4.6.
- Nếu 0 card, bỏ L4.6–L4.7.

**G-level:** vẫn là G1.

**Có học tiếp được không?** Có. Lesson kế tiếp là L4.6 (card set v3, chỉ cần nếu có ít nhất 1 card). Bạn có thể học nó ngay để hiểu một card bổ sung được viết và đóng băng thế nào. Hoặc, nếu muốn học đúng nhánh "0 card", có thể nhảy sang L4.8 (runner).

**Điều cần giữ trong đầu.** L4.5 là nơi bạn quyết định Phase 5 sẽ hỏi thêm câu gì. Ba quyết định rẻ nhất và quan trọng nhất của toàn Phase 4 (Part A của L4.5, luật sàng, và spec của L4.4) đều làm được ngay, đều là của bạn, và cùng nhau chúng quyết định lần chạy native tiếp theo cần gì.