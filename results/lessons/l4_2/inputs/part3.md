# LESSON 4.2, Part 3/3: Từ toy đến dữ liệu

```text
L4.2  Part 1 ✓ Chiều thật   Part 2 ✓ Ba toy   Part 3 ← BẠN Ở ĐÂY → Lesson Gate L4.2
```

### 0. Hai điều cần biết trước

1. **Bài dự đoán ở Bước 6 không còn mù.** Kết quả "lớp AB và C tách theo δ" đã nằm sẵn trong PHASE_4 (mục K9b và dòng 8 của bảng sửa đổi), và tôi đã in nó trong output recount ở L4.1 Part 3. Tôi đề xuất cách làm trung thực ở §5.
2. **Một chỗ plan nói hơi quá.** Khái niệm 4 viết "lớp AB và C dồn quanh Ḡ_S|M1 ≈ 0". Tôi đếm lại:
   - Với lớp C thì đúng: 255/334 điểm có Ḡ_S|M1 < 0,1.
   - Với lớp AB thì **không** đúng: trung vị 0,71; 67/161 điểm dưới 0,5, nhưng cũng có 67/161 điểm ≥ 1.

   Lớp AB không đồng nhất: một số điểm giống C (state chỉ bù lỗi cho model), một số có giá trị thông tin thật. Điểm này quan trọng nếu sau này bạn viết card SUB.

## 1. Câu hỏi của Part 3

> Làm sao đọc pattern trên dữ liệu thật mà không nhầm phần bị identity ép thành phát hiện? Và làm sao nối câu chuyện của toy với một tọa độ thiết kế?

## 2. Tại sao cần?

Ở L4.5 bạn sẽ vẽ hộp cho card ứng viên. Nếu đọc nhầm hình, bạn có thể vẽ hộp quanh một pattern **do định nghĩa tạo ra**. Hoặc bạn vẽ hộp theo trục thô, trộn hai lớp ngược dấu vào nhau, khiến tỉ lệ thành công p⁺ thấp.

---

## 3. Khái niệm A: không gian outcome khác không gian tham số

- **Không gian tham số:** các trục là thứ bạn **chọn trước** khi chạy (λA, λB, κ, h…). Vùng của card phải nằm ở đây, vì Phase 5 rút điểm mới trong không gian này.
- **Không gian outcome:** các trục là thứ **tính ra** sau khi chạy (Ḡ_S, Ḡ_M…).

Cả hai hình bạn vừa nhận (`regime_map_differ.png`, `regime_map_mechanism.png`) đều nằm trong **không gian outcome**. Chúng cho biết các contrast liên quan với nhau thế nào, nhưng **không thể vẽ hộp card lên chúng**.

---

## 4. Đọc hai hình từng bước

### 4.1 `regime_map_differ.png`

| Bước đọc | Nội dung |
|---|---|
| Trục x | Ḡ_S (tự do về dấu), đơn vị % C̄_ref |
| Trục y | Ḡ_M, đơn vị % C̄_ref |
| Thang | **Symlog**: tuyến tính quanh 0, logarit ở xa. Khoảng cách trên hình không tỉ lệ với khoảng cách thật; cụm A trông lớn nhưng chỉ trải từ 1 đến 4% |
| Đường đứt | ±1%, tức ngưỡng phân lớp |
| Màu | Lớp của từng điểm |
| Điểm rỗng | Điểm nằm trong hộp card khi quy về age 1, tức đã lộ |

**Những gì trên hình không phải thông tin:**
- **Màu là luật phân lớp được vẽ ra.** Vị trí quyết định màu theo định nghĩa (trừ J và D). Thấy bốn góc tô bốn màu không phải phát hiện.
- **Không có điểm nào dưới y = 0.** Đó là identity Ḡ_M ≥ 0.
- **Mật độ điểm là do cách lấy mẫu** (map2 dồn mẫu vào A và AB).

**Những gì là thông tin:** **độ trải** bên trong mỗi lớp. Ví dụ, lớp C trải từ Ḡ_M = 0 tới khoảng 20%. Nghĩa là lớp C gồm cả những điểm "model không liên quan" (cụm nằm trên y = 0) lẫn những điểm "model rất quan trọng" (kiểu MV+A).

### 4.2 `regime_map_mechanism.png`: phần nào bị ép, phần nào là thông tin

Hai trục là Ḡ_S|M1 và Ḡ_M|S1. Cả hai ≥ 0 theo S07, nên chỉ có góc phần tư dương. Đường chấm là đường hai giá trị bằng nhau.

Thoạt nhìn, hình cho thấy "A ở dưới-phải, C ở trên-trái", trông như một bản đồ cơ chế đẹp. Nhưng hãy tách từng pattern:

| Pattern nhìn thấy | Bị ép? | Vì sao | Số kiểm (tôi chạy) |
|---|---|---|---|
| Lớp C nằm cao (Ḡ_M\|S1 ≥ 1) | **Bị ép** | S12: Ḡ_M\|S1 ≥ \|Ḡ_S\| + Ḡ_M, mà lớp C có \|Ḡ_S\| ≥ 1 | min = 1,09; 0 vi phạm |
| Lớp A nằm bên phải | **Gần như bị ép** | Từ cận Γ̄ ≥ −Ḡ_M suy ra Ḡ_S\|M1 = Ḡ_S + Γ̄ ≥ Ḡ_S − Ḡ_M, mà lớp A có Ḡ_S ≥ 1 và Ḡ_M nhỏ | 0 vi phạm; min(Ḡ_S − Ḡ_M) = 0,56 |
| Lớp C dính sát x ≈ 0 | **Không** | Identity chỉ đòi Ḡ_S\|M1 ≥ 0 | 255/334 điểm < 0,1 |
| Lớp A nằm thấp | **Không** | Không có ràng buộc nào | 286/301 điểm có Ḡ_M\|S1 < 0,5 |
| Lớp AB trải rộng trên trục x | **Không** | — | Trung vị 0,71; 67/161 < 0,5; 67/161 ≥ 1 |

**Cách đọc trung thực:**
- **Ở lớp C:** nếu model đúng, state tươi gần như không đáng giá. Tác hại của state chỉ tồn tại vì M0 sai, đúng như toy T-C′.
- **Ở lớp A:** nếu state đúng, sửa model gần như không thêm gì.
- **Ở lớp AB:** có hai loại điểm. Một số giống T-AB, tức state chỉ bù lỗi cho model. Một số thì thông tin có giá trị thật.

Một nửa ấn tượng "hai lớp tách nhau gọn gàng" đến từ định nghĩa, không đến từ mạng.

---

## 5. Khái niệm B: tọa độ tổ chức δ = λB − λA

### 5.1 Trực giác

Có những hình nhìn từ trục thô thì màu trộn lẫn lộn, nhưng xoay góc nhìn theo một trục chéo thì hiện ra thành các sọc rõ ràng.

### 5.2 Bảng chéo λA × λB

Tôi lập bảng trong vùng κ/τ ∈ [0,05; 0,15], h/τ ∈ [4; 8], η ∈ [⅝; ⅞], gồm 238 điểm. Mỗi ô ghi lớp chiếm đa số và tỉ lệ của nó.

```text
λA \ λB     6,0       6,5        7,0        7,5       8,0
 6,00        .     AB 18/18    C 18/18    C 18/18      .
 6,25        .     AB 18/18   AB  8/18    C 18/18      .
 6,50     C 2/2     D 15/18   AB 20/20    C 18/18    C 4/4
 6,75        .      C 15/18   AB 18/18    C 13/18      .
 7,0–8,0  (thưa: 1–4 điểm pilot mỗi ô)
```

**Cách đọc:** các ô cùng nằm trên một **đường chéo** thì có cùng δ.
- δ = 0,5, tức các ô (6; 6,5) và (6,5; 7): lớp AB.
- δ = 1, tức các ô (6; 7) và (6,5; 7,5): lớp C.

Cùng một δ thì cùng lớp, dù λA khác nhau. Đó là dấu hiệu δ tổ chức dữ liệu tốt hơn λA hay λB đứng riêng.

**Tóm tắt theo δ** (từ L4.1 Part 3):

| δ | Lớp chiếm đa số |
|---|---|
| ≤ −0,25 | Gần như toàn C |
| 0 | Không có AB hay C (trung tính) |
| 0,25 và 0,5 | Gần như toàn AB |
| 0,75 | Dải chuyển tiếp |
| ≥ 1 | Toàn C |

### 5.3 Nối với toy (cách đọc ứng viên, chưa kiểm)

Khi B nặng dần so với A, cả độ chênh thật lẫn dự đoán "nhòe" của M0 đều dịch dần về phía Stay.
- **Ở δ khoảng 0,25–0,5:** đáp án thật đã là Stay, nhưng trung bình của M0 vẫn nói Switch, tức rơi sai phía. Đây là T-AB.
- **Ở δ ≥ 1:** trung bình của M0 cũng nói Stay, tức đúng phía nhờ may, và state tươi làm lộ lỗi của M0 ở từng state. Đây là T-C′.

Tôi **chưa** kiểm được rằng quyết định nhòe của M0 trong plant thật sự lật dấu quanh δ ≈ 0,75. Đây là giả thuyết cho Phase 6.

### 5.4 Ba lời cảnh báo

**(1) Phía trái chưa được giải thích.** Ở δ ≤ −0,25 cũng là lớp C, nhưng cách đọc ở §5.3 chỉ viết cho phía phải. Bằng chứng ở phía trái lại mỏng: tổng cộng 27 điểm, trong đó 18 điểm ở δ = −0,25 và chỉ 9 điểm ở δ ≤ −0,5. Một cơ chế tốt phải giải thích **toàn bộ** pattern, kể cả phần không đơn điệu.

**(2) Tính đồng tuyến (collinearity).** Trên lưới hẹp này (λA phần lớn từ 6 đến 6,75), δ gần như đi song song với các tọa độ ứng viên khác, chẳng hạn tỉ lệ headroom (μ − λB)/(μ − λA) trong MASTER PLAN F8. Ví dụ:
- Ô (6,25; 7) có δ = 0,75 và lớp hỗn hợp; tỉ lệ headroom của nó là 0,8.
- Ô (7,5; 8) có δ = 0,5 (AB 2/4); tỉ lệ headroom cũng là 0,8.

Dữ liệu hiện có không phân biệt được hai tọa độ này. Muốn tách chúng, cần một thiết kế cho λA thay đổi rộng trong khi giữ δ cố định. Đó là việc của Phase 6.

**(3) δ được tìm ra sau khi nhìn dữ liệu.** Đây là discovery, nên phải ghi vào forking log. Một hộp vẽ theo δ vẫn có thể thành card, nhưng phải được xác nhận trên điểm CF mới.

**Hệ quả cho L4.5:**
- Hộp vẽ theo trục thô, ví dụ λA ∈ [6; 6,75] × λB ∈ [6,5; 7,5], sẽ trộn AB với C, nên p⁺ thấp.
- Hộp vẽ theo δ ∈ [0,25; 0,5] thì thuần hơn, nhưng mang theo một lựa chọn post-hoc.

Chọn cách nào là quyết định của bạn ở L4.5.

### 5.5 Làm Bước 6 cho trung thực

**(a) Bắt buộc nếu ghi sổ chặt chẽ.** Đổi Bước 6 thành bài *giải thích cơ chế ứng viên*, và ghi vào forking log: "bảng δ đã được thấy trước, qua PHASE_4 §0.3 và phiên dạy L4.1".

**(b) Tùy chọn, nếu muốn luyện dự đoán thật.** Có một câu hỏi tôi chưa tính và PHASE_4 chưa báo: **trong vùng của lớp A** (κ/τ ∈ [0,2; 1], h/τ ∈ [1; 4], η ≥ ½), δ có tổ chức các lớp A, C, D không?

Cần nói rõ: REGIME_MAP mục 3 có cho thông tin một phần ("lớp A ở λB 7–7,5, λA 6–7,5"), nên đây không phải hoàn toàn mù. Hãy viết một dòng "Tôi dự đoán … vì …" **trước**, rồi mới chạy:

```python
# Chạy SAU khi đã viết dự đoán. Dùng lại load/dedup/cls của recount.py (L4.1 Part 3).
import sys; from collections import Counter, defaultdict
sys.path.insert(0, "scripts"); import recount as rc
tab, _ = rc.dedup(rc.load("check/raw"))
by = defaultdict(Counter)
for r in tab:
    k, h = r["kappa"] / r["age"], r["h"] / r["age"]
    if r["amp"] == 6 and .2 <= k <= 1 and 1 <= h <= 4 and r["eta"] >= .5:
        by[round(r["lambdaB"] - r["lambdaA"], 3)][rc.cls(r)] += 1
for dl in sorted(by): print(dl, dict(by[dl]))
```

Đây vẫn là phân tích discovery, phân tích lại dữ liệu đã thấy (§0.8 cho phép). Nó có giá trị **luyện tập**, không phải evidence. Hãy ghi nó vào forking log, vì nó có thể ảnh hưởng tới hộp của card SV sau này.

---

## 6. T07 addendum "P4": khung để bạn tự viết

Plan quy định AI **không** viết phần này thay bạn. Bạn nên tự viết, tối đa một trang, gắn nhãn "tác giả viết", với bốn mục:

1. **Co giãn thời gian:** phép chứng minh 5–8 dòng, cùng bốn giả định (fluid, cost tuyến tính, buffer vô hạn, c_sw = 0).
2. **Cận Γ̄ ≥ −min(Ḡ_S, Ḡ_M)** và ba hệ quả cho thiết kế card.
3. **Bảng ba toy** (T-A, T-AB, T-C′), kèm câu "AB và C cùng nguồn — trong toy", và ghi chú rằng toy không có hàng đợi.
4. **Đọc Ḡ_S|M1 = min(P, N)** như giá trị thông tin; câu "bất định ≠ giá trị thông tin".

---

## 7. Golden test

**Code này tồn tại để kiểm:** bảng toy trong addendum và các identity có đúng chính xác không, trên những trường hợp mà ta biết trước từng con số. Test dùng phân số, không dùng số thực, để không có sai số làm tròn.

```python
"""Golden test for the three two-state toys of L4.2 (exact fractions)."""
from fractions import Fraction as F
import pytest

def cells(d, dh, tie_stay=True, js=F(10)):
    """Four population costs for two equally likely states; Switch iff gap < 0."""
    p = (F(1, 2), F(1, 2))
    A = (lambda z: 1 if z < 0 else 0) if tie_stay else (lambda z: 1 if z <= 0 else 0)
    J = lambda a, i: js + a * d[i]                       # J(Stay)=js, J(Switch)=js+Δ
    g = sum(p[i] * d[i] for i in range(2))               # E[Δ | y]
    gh = sum(p[i] * dh[i] for i in range(2))             # E[Δ̂ | y]
    L00 = sum(p[i] * J(A(gh), i) for i in range(2))
    L01 = sum(p[i] * J(A(g), i) for i in range(2))
    L10 = sum(p[i] * J(A(dh[i]), i) for i in range(2))
    L11 = sum(p[i] * J(A(d[i]), i) for i in range(2))
    c = dict(GS=L00 - L10, GM=L00 - L01, GSM=L00 - L11, Gam=L10 + L01 - L00 - L11,
             GS_M1=L01 - L11, GM_S1=L10 - L11, Cref=L11)
    c["P"] = sum(p[i] * max(d[i], 0) for i in range(2))
    c["N"] = sum(p[i] * max(-d[i], 0) for i in range(2))
    return c

def cls(c):  # REGIME_MAP rule on % of Cref, C checked first
    gs, gm = 100 * c["GS"] / c["Cref"], 100 * c["GM"] / c["Cref"]
    gsm, gam = 100 * c["GSM"] / c["Cref"], 100 * c["Gam"] / c["Cref"]
    if gs <= -1: return "C"
    if gs >= 1: return "A" if gm < 1 else "AB"
    if gm >= 1: return "B"
    if gsm >= 1 and gam >= max(gs, gm): return "J"
    return "D"

TOYS = {  # name: (Δ, Δ̂, expected GS, GM, Gam, GS|M1, class)
    "T-A":  ((F(-1), F(6, 5)), (F(-1), F(6, 5)), F(1, 2), F(0), F(0), F(1, 2), "A"),
    "T-AB": ((F(1), F(1)), (F(-3), F(1)), F(1, 2), F(1), F(-1, 2), F(0), "AB"),
    "T-C'": ((F(1), F(1)), (F(-3), F(4)), F(-1, 2), F(0), F(1, 2), F(0), "C"),
}

@pytest.mark.parametrize("name", TOYS)
def test_toy_table(name):
    d, dh, gs, gm, gam, gsm1, k = TOYS[name]
    c = cells(d, dh)
    assert (c["GS"], c["GM"], c["Gam"], c["GS_M1"]) == (gs, gm, gam, gsm1)
    assert cls(c) == k

@pytest.mark.parametrize("name", TOYS)
def test_identities(name):
    c = cells(*TOYS[name][:2])
    assert min(c["GM"], c["GSM"], c["GS_M1"], c["GM_S1"]) >= 0           # S07, S08
    assert c["Gam"] == c["GS_M1"] - c["GS"] == c["GM_S1"] - c["GM"]       # S11
    assert c["GS_M1"] == min(c["P"], c["N"])                              # S10
    assert c["Gam"] >= -min(c["GS"], c["GM"])                             # bound
    if c["GS"] < 0:
        assert c["Gam"] >= -c["GS"]                                       # S12

def test_mutant_mechanism():
    """Move only Δ̂(x2) of T-AB from +1 to +4: the blurred mean crosses 0, AB -> C."""
    assert cls(cells((F(1), F(1)), (F(-3), F(1)))) == "AB"
    assert cls(cells((F(1), F(1)), (F(-3), F(4)))) == "C"

def test_mutant_tie_rule():
    """Δ̂(x2)=+3 puts E[Δ̂] exactly at 0: the class is decided by the tie rule alone."""
    assert cls(cells((F(1), F(1)), (F(-3), F(3)), tie_stay=True)) == "C"
    assert cls(cells((F(1), F(1)), (F(-3), F(3)), tie_stay=False)) == "AB"
```

**Kết quả khi tôi chạy: 8 passed.**

**Mục đích của hai test mutant.** Một test không bao giờ có thể fail thì vô dụng, giống hệt một vùng đối chứng không thể thất bại (Part 2, §7.3). Hai mutant cho thấy bộ test **phát hiện được** khi đổi đúng một chỗ:
- Đổi Δ̂(x₂) của T-AB thành +4 → lớp đổi từ AB sang C (cơ chế).
- Giữ Δ̂(x₂) = +3, chỉ đổi luật hòa → lớp đổi từ C về AB.

Mutant thứ hai cũng chứng minh nhận xét ở Part 2 §0: mutant +3 mà plan đề xuất thực chất đang kiểm luật hòa, không kiểm cơ chế.

---

## 8. 🔗 Liên hệ với việc bạn từng làm

- **Quan sát cũ ở L3R.7.** PHASE_4 ghi rằng "15 non-meets của SH+A tập trung gần λA ≈ λB"; đây là ghi chép của AI, tôi chưa kiểm. Nó khớp với "δ = 0 là trung tính". Hộp SH+A có δ ∈ [−2; 0], nên phần gần δ = 0 có thể kéo p⁺ của card SH xuống. **Không** được sửa card v2 vì điều này. Đây chỉ là điều nên nhớ khi đọc kết quả ở Phase 5.
- **Các heatmap trong repo cũ** (`experiments/scan/*`: map, frontier) gặp đúng những bẫy hôm nay: trục thô, màu do luật định nghĩa vẽ ra, mật độ điểm do cách lấy mẫu.

## 9. Toàn bộ L4.2 cho phép nói gì

**Được nói:**
- Trong plant hợp đồng có 5 chiều thật; age là thang thời gian.
- Lớp là công cụ đọc, vùng mới là đối tượng kiểm định.
- Trong toy, cùng một lỗi của M0 sinh ra cả lớp AB lẫn lớp C.
- Trên bản đồ, lớp AB và C tách nhau theo δ ở phía δ > 0.
- Một nửa sự "tách bạch" trong hình mechanism là do định nghĩa.

**Không được nói:**
- "δ là cơ chế."
- "δ tốt hơn tỉ lệ headroom."
- "Lớp AB là vùng state chỉ bù lỗi model." Lớp AB không đồng nhất.
- "Hình mechanism chứng minh hai loại hành vi khác nhau."

## 10. Reviewer có thể hỏi

1. *"Bản đồ cơ chế của bạn có bị định nghĩa ép không?"* **Đã trả lời** (§4.2): một phần có, và đã tách rõ phần nào.
2. *"Vì sao chọn δ mà không chọn tỉ lệ headroom?"* **Chưa trả lời được:** dữ liệu không phân biệt hai tọa độ này. Để Phase 6.
3. *"Còn các điểm lớp C ở δ < 0 thì sao?"* **Chưa trả lời,** và bằng chứng ở đó cũng mỏng.
4. *"δ được tìm ra trước hay sau khi nhìn dữ liệu?"* **Sau.** Đã ghi là discovery.

## 11. ⚠️ Bẫy người mới

1. Vẽ hộp card lên hình trong không gian outcome.
2. Đọc màu, hoặc khoảng trống dưới y = 0, như thể đó là phát hiện.
3. Gọi cách tách A/C trong hình mechanism là "bằng chứng cơ chế".
4. Coi δ là tọa độ duy nhất có thể, quên tính đồng tuyến.
5. Viết "dự đoán" cho Bước 6 sau khi đã thấy bảng, rồi ghi nó như một dự đoán thật.
6. Viết test mà không kiểm nó có thể fail.

## 12. 🧠 Tư duy researcher

> Trước mỗi hình, hãy hỏi theo thứ tự: **(1)** trục thuộc không gian nào? **(2)** phần nào của pattern do định nghĩa hoặc identity tạo ra? **(3)** mật độ điểm do cách lấy mẫu hay do thế giới? **(4)** có tọa độ nào khác giải thích dữ liệu tốt ngang bằng không? Chỉ phần còn lại sau bốn câu hỏi đó mới là thông tin.

## 13. Bài tập hiểu (khuyến nghị)

- Viết T07 addendum "P4" bằng lời của bạn, tối đa một trang.
- Tự dẫn hai pattern bị ép ở §4.2, mỗi cái trong 1–2 dòng.
- Nếu muốn luyện dự đoán thật, làm bài (b) ở §5.5.

## 14. Tự kiểm (tùy chọn)

1. Vì sao không thể vẽ hộp card lên `regime_map_differ.png`?
2. Trong hình mechanism, lớp C nằm cao là do identity nào?
3. Đọc một đường chéo của bảng λA × λB nghĩa là đang giữ cố định cái gì?
4. Hãy nêu một thiết kế giúp phân biệt δ với tỉ lệ headroom.
5. Vì sao test mutant +3 kiểm luật hòa chứ không kiểm cơ chế?

---

## 15. LESSON GATE: L4.2

**Hiểu biết.** Sau L4.2, bạn nên tự giải thích được:
- Phép co giãn thời gian và các giả định của nó; vì sao có 5 chiều thật.
- Biên độ là plant khác; lớp khác vùng.
- Ba toy, và câu "AB và C cùng nguồn" trong toy.
- Ḡ_S|M1 = min(P, N).
- Ba hệ quả của cận Γ̄, và vì sao đối chứng "lật một nhân tố" vô dụng với claim về Γ̄.
- Cách đọc hai hình: phần bị ép và phần là thông tin.
- δ là gì, và ba lời cảnh báo về nó.

**Trạng thái thực thi:** chưa bắt đầu.
- Còn lại cho bạn: T07 addendum ⬜, đưa golden test vào `tests/` ⬜, ghi forking log cho bảng δ ⬜.
- Phần AI đã làm giúp: tính toy bằng phân số, chạy golden test (8 passed), lập bảng chéo, định lượng phần bị ép trong hình.

**Phụ thuộc khoa học:** L4.5 cần ba hệ quả ở Part 2 §7.2 làm bộ lọc identity, và cần §5.4 khi chọn trục để vẽ hộp.

**G-level:** vẫn là G1.

**Có học L4.3 được không?** Có. L4.3 chuyển từ "đọc đúng" sang "số có đúng không": audit các con số mà một claim mới sẽ dựa vào, dưới engine dùng cho confirmation. Bài đó gồm vì sao dung sai phải viết trước khi chạy, sai số chung giữa các ô (đã chạm tới ở E11), nhãn sát ngưỡng có thể lật, và cách không biến audit thành một chứng chỉ số nặng nề.

**Điều cần giữ trong đầu.** Bản đồ chỉ có 5 chiều thật. Một nửa vẻ đẹp của nó đến từ định nghĩa. Phần còn lại là thông tin thật: lớp C ở sát Ḡ_S|M1 ≈ 0, lớp A có Ḡ_M|S1 nhỏ, và AB/C tách nhau theo δ. Cả ba đều là discovery, đã thấy rồi, và mỗi cái có ít nhất một cách giải thích thay thế chưa bị loại.