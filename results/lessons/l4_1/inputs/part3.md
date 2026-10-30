# LESSON 4.1, Part 3/3: Ghi sổ (errata, provenance, record, DL-103, exposure)

```text
L4.1  Part 1 ✓  Part 2 ✓  Part 3 ← BẠN Ở ĐÂY  →  Lesson Gate L4.1
```

## 1. Câu hỏi của Part 3

> Làm sao biến những gì đã hiểu thành các bản ghi trên main, để người khác, hoặc chính bạn ba tháng sau, kiểm được mọi con số và biết ai đã khẳng định điều gì, mà không phải tin lời AI hay trí nhớ?

Part 3 thiên về thực thi. Bạn đang học trước, nên tôi dạy *vì sao* và *cách làm*; phần chạy thật để lúc bạn quay lại.

Lesson này tạo năm loại bản ghi. Mỗi loại tồn tại để chặn một rủi ro cụ thể:

| Bản ghi | Chặn rủi ro |
|---|---|
| Errata E9–E14 | Số trôi: trích những con số không khớp raw |
| Nhãn provenance | AI dựa trên AI (rủi ro ER3) |
| Record của bản đồ | Quên đã thấy gì; viết claim từ một tài liệu nằm ngoài main |
| DL-103 | Hiểu nhầm "Phase 5" nghĩa là gì; ủy quyền ngầm cho AI |
| Dòng exposure và forking log #0 | Các lựa chọn ẩn được làm trước L4.3/L4.5 |

---

## 2. Khái niệm 1: raw thắng bản tóm tắt; errata là bản ghi hạng nhất

**Trực giác, theo kiểu networking.** Dashboard báo latency p99 là 12 ms, nhưng tính lại từ log raw ra 14 ms, vì dashboard chỉ lấy mẫu 1/100 packet. Khi hai bên lệch nhau, raw đúng, và bạn ghi lại lý do lệch.

**Erratum là gì.** Mỗi erratum có bốn trường: giá trị cũ, giá trị đúng, cách kiểm, ảnh hưởng tới kết luận.

**Errata chỉ được ghi thêm (append-only).** REGIME_MAP tại tag giữ nguyên từng byte; errata nằm trong record. Lý do là lịch sử "ai tin điều gì, lúc nào" chính là bằng chứng (Part 1, §7). Sửa đè lên bản cũ là xóa mất bằng chứng đó.

**Một con số không có định nghĩa thì không trích được.** REGIME_MAP ghi "53/161 gần thay thế hoàn toàn" mà không nói "gần" nghĩa là bao nhiêu. Không ai tái lập được con số này, kể cả chính phiên AI đã viết nó.

### Bảng errata E9–E14, xếp theo mức ảnh hưởng

| # | Bản đồ viết | Đúng là | Đổi kết luận? | Tôi đã kiểm lại? |
|---|---|---|---|---|
| E9 | Phân vị 90% (q90) của Ḡ_S lớp A là "2,46%" | 2,444 theo nội suy tuyến tính; chênh do cách tính phân vị | Không. Chỉ cần ghi cách tính | ✓ |
| E10 | "53/161 gần thay thế hoàn toàn" | Không có định nghĩa. Với \|Γ̄ + min(Ḡ_S, Ḡ_M)\| < 0,1 pp: 33/161; < 0,05 pp: 24/161 | Không trích con số "53" | ✓ |
| E11 | "L̄10, L̄11 không phụ thuộc age; lệch ≤ 0,7% do cầu phương" | Đây là vi phạm identity S04 dưới engine pilot, tới 0,711% ở mức L̄ | Không trích mức L̄; các contrast ít bị ảnh hưởng | ✗ (cần chạy engine) |
| E12 | Các số Ḡ_S của bản đồ | Engine native cho số thấp hơn ở 8/8 điểm; XM2S110 lật từ lớp A sang D | Phải gán nhãn lại bằng native trước khi vẽ vùng | ✗ (để L4.3) |
| E13 | Lấy X2065 làm ví dụ lớp B | X2065 là lớp C; hộp MV+A có 11 điểm C, 7 điểm B | Câu "MV+A là vùng model thắng" sai | ✓ |
| E14 | (bản đồ chưa nói) | Lớp AB và C tách nhau theo δ = λB − λA | Ảnh hưởng cách vẽ hộp ở L4.5 | ✓ |

### Vì sao E11 không phá các contrast: sai số chung triệt tiêu trong phép trừ

Ví dụ dưới đây dùng số minh họa.

```text
Giá trị thật:            L̄10 = 100,0   L̄11 = 99,5   →  Ḡ_M|S1 = 0,5
Engine lệch +0,7% ở cả hai: L̄10 = 100,7   L̄11 = 100,2  →  Ḡ_M|S1 = 0,5
```

Mức L̄ sai 0,7%, nhưng hiệu giữa hai ô gần như đúng, vì sai số nằm chung ở cả hai ô. Trên dữ liệu thật, sự triệt tiêu chỉ gần đúng: 18 cặp tương đương theo age lệch nhau ≤ 0,201 pp.

Đây cũng là nguyên lý đứng sau paired design và CRN (common random numbers) trong MASTER PLAN IX.5: cho hai phương án dùng chung nguồn nhiễu thì nhiễu triệt tiêu khi lấy hiệu.

**Phân bổ công sức.** E9 chỉ cần một dòng ghi cách tính. Thời gian nên dồn vào E11–E13, vì chúng bảo vệ các claim.

---

## 3. Khái niệm 2: bốn nhãn provenance

| Nhãn | Nghĩa | Ví dụ trong project |
|---|---|---|
| **Tác giả viết** | Bạn tự viết bằng lời của mình | Mục (8) của record, nếu bạn tự viết |
| **Author-attested** | Bạn tuyên bố đã đọc/hiểu, nhưng bằng chứng nằm ngoài repo | Phần đọc card/contract "ngoài vở" trong closeout 3R |
| **AI soạn, tác giả duyệt** | AI viết nháp, bạn đọc và sửa | DL-103, nếu bạn dùng khung ở Phụ lục D rồi sửa |
| **AI theo ủy quyền** | AI tự thiết kế, chạy và viết; bạn chưa kiểm | REGIME_MAP, mục "cái gì thật sự mới"; T07 |

**Luật nâng nhãn.** Một phát biểu chỉ được lên nhãn cao hơn khi bạn tự kiểm lại và ghi bằng lời của mình. Ví dụ: sau Part 2, nếu bạn tự giải thích được vì sao chỉ câu 6 và câu 7 sống sót, bảng phân loại được ghi là "tác giả kiểm lại".

Ba câu hỏi dưới đây hay bị trộn vào nhau:

| Câu hỏi | Phụ thuộc vào | Ví dụ |
|---|---|---|
| Prereg có hợp lệ không? | Thời điểm commit so với lúc có dữ liệu | Card v1 do AI soạn, commit trước bản đồ → **vẫn là prereg hợp lệ** |
| Ai hiểu và sở hữu nó? | Ai viết, ai tự kiểm | Không được ghi "tác giả dự đoán" nếu bạn chưa tự giải thích lại được |
| Nó có đúng không? | Verification | Recount khớp raw → số đúng, bất kể ai viết |

Bản recount tôi chạy ở §4 cũng mang nhãn "AI soạn, tác giả chưa kiểm" cho tới khi bạn đọc nó.

---

## 4. Khái niệm 3: record gồm tám mục, mỗi mục chặn một lỗi

| Mục | Nội dung | Chặn lỗi | Nguyên liệu |
|---|---|---|---|
| 1 | Provenance: nhánh, tag → `574a36f`, "AI theo ủy quyền", không có prereg | Không biết ai làm, bằng code nào | Part 1 §6.4 |
| 2 | Bảng các đợt chạy | Nhầm đợt lấy mẫu thích nghi với đợt dùng plant khác | REGIME_MAP |
| 3 | Sự cố khi chạy và cách đã kiểm | Vứt dữ liệu, hoặc lờ sự cố đi | REGIME_MAP, K2 |
| 4 | Bảng lớp, kèm cảnh báo về cách lấy mẫu | Đọc số đếm như tần suất | Part 1 §9 |
| 5 | Phân loại 10 phát biểu | Gán chữ "phát hiện" cho identity | Part 2 §5 |
| 6 | Errata E1–E14 | Trích số không khớp raw | §2 ở trên |
| 7 | Con trỏ tới inventory v3 | Không biết exposure đã được ghi ở đâu | §6 |
| 8 | **"Record này KHÔNG cho phép nói gì"**, do bạn viết | Vượt ranh giới claim | Part 1 §11, Part 2 §7 |

Luật chung: mọi con số phải có nguồn là một script; mọi đánh giá phải có nhãn provenance.

### Thiếu `recount_map.py` thì làm gì?

Có ba lựa chọn:
- **(a)** Xin lại gói kiểm tra từ phiên đã soạn PHASE_4. Nhanh, nhưng vẫn là AI dựa trên AI.
- **(b)** Tự viết recount. Chậm hơn, nhưng là cách tốt nhất để thật sự sở hữu các con số.
- **(c)** Dùng bản tham chiếu tôi vừa viết và chạy (ở dưới), rồi đọc tới mức tự giải thích được từng khối.

Tôi khuyên dùng (c) ngay bây giờ để học, rồi chọn (b) hoặc đọc thật kỹ (c) khi thực thi.

**Pseudocode trước:**

```text
1. Đọc 6 file raw (stage1, stage2, map1, map2, map3age, map4amp), bỏ các dòng có c_sw ≠ 0
2. Gộp theo tọa độ (λA, λB, κ, η, h, age, amp); dòng bị bỏ phải có số y hệt bản được giữ
3. Phân lớp theo luật của REGIME_MAP (lớp C được xét trước)
4. Kiểm identity: S11, S07/S08, cận dưới của Γ̄
5. Tóm tắt: lớp A (age 1, ±6), lớp AB, hộp MV+A (quy về age 1), bảng theo δ
```

**Code:**

```python
"""Recount the regime map from raw batch CSVs (L4.1, Step 3).
Scientific purpose: check that numbers a record would cite follow from the raw
files at tag explore-v13-regime-map, not from the AI-written summary."""
import csv, sys, statistics as st
from collections import Counter, defaultdict

ORDER = ["stage1", "stage2", "map1", "map2", "map3age", "map4amp"]  # first copy kept
NUM = ["G_S_pctC", "G_M_pctC", "G_SM_pctC", "Gamma_pctC", "G_S_M1_pctC", "G_M_S1_pctC"]

def load(d):
    rows = []
    for b in ORDER:
        for r in csv.DictReader(open(f"{d}/{b}.csv")):
            if float(r.get("c_sw", 0)) != 0:
                continue
            r["batch"] = b
            r["age"] = float(r.get("age", 1)); r["amp"] = float(r.get("amp", 6))
            for k in ["lambdaA", "lambdaB", "kappa", "eta", "h"] + NUM:
                r[k] = float(r[k])
            rows.append(r)
    return rows

def key(r):
    return tuple(round(r[k], 9) for k in ["lambdaA", "lambdaB", "kappa", "eta", "h", "age", "amp"])

def dedup(rows):
    kept, seen, dropped_ok = [], {}, 0
    for r in rows:
        k = key(r)
        if k in seen:  # invariant: a dropped row must equal its kept copy exactly
            assert all(r[c] == seen[k][c] for c in NUM), (r["id"], seen[k]["id"])
            dropped_ok += 1
        else:
            seen[k] = r; kept.append(r)
    return kept, dropped_ok

def cls(r):  # class rule of REGIME_MAP; C is checked first
    gs, gm, gsm, g = r["G_S_pctC"], r["G_M_pctC"], r["G_SM_pctC"], r["Gamma_pctC"]
    if gs <= -1: return "C"
    if gs >= 1: return "A" if gm < 1 else "AB"
    if gm >= 1: return "B"
    if gsm >= 1 and g >= max(gs, gm): return "J"
    return "D"

def q_linear(xs, q):  # numpy default ("linear") quantile
    xs = sorted(xs); p = (len(xs) - 1) * q; i = int(p)
    return xs[i] if i + 1 == len(xs) else xs[i] + (p - i) * (xs[i + 1] - xs[i])

def main(d):
    raw = load(d)
    tab, dropped = dedup(raw)
    print("raw", len(raw), "-> table", len(tab), "| dropped with exact copy:", dropped)
    print("per batch kept", Counter(r["batch"] for r in tab))
    print("classes", Counter(cls(r) for r in tab))
    print("map1 raw grid", Counter(cls(r) for r in raw if r["batch"] == "map1"))

    e11 = max(abs(r["Gamma_pctC"] - (r["G_S_M1_pctC"] - r["G_S_pctC"])) for r in tab)
    mins = {c: min(r[c] for r in tab) for c in ["G_M_pctC", "G_S_M1_pctC", "G_SM_pctC", "G_M_S1_pctC"]}
    lb = sum(r["Gamma_pctC"] < -min(r["G_S_pctC"], r["G_M_pctC"]) - 1e-12 for r in tab)
    print("S11 max err", e11, "| mins", mins, "| Gamma<-min violations", lb)

    base = [r for r in tab if r["age"] == 1 and r["amp"] == 6]
    A = [r["G_S_pctC"] for r in base if cls(r) == "A"]
    print("A (age1,+-6): n", len(A), "median", round(st.median(A), 3), "q90 linear",
          round(q_linear(A, .9), 3), "max", round(max(A), 3),
          "median G_M", round(st.median(r["G_M_pctC"] for r in base if cls(r) == "A"), 3))
    AB = [r for r in tab if cls(r) == "AB"]
    near = lambda t: sum(abs(r["Gamma_pctC"] + min(r["G_S_pctC"], r["G_M_pctC"])) < t for r in AB)
    print("AB n", len(AB), "Gamma<0", sum(r["Gamma_pctC"] < 0 for r in AB),
          "| near full substitution <0.1:", near(.1), "<0.05:", near(.05))

    def in_mvA(r):  # MV+A box of card v2, rescaled to age 1 (u = 2*eta)
        k, h = r["kappa"] / r["age"], r["h"] / r["age"]
        return (r["amp"] == 6 and r["lambdaB"] == 8 and 7 <= r["lambdaA"] <= 7.5
                and 1 <= 2 * r["eta"] <= 1.5 and .1 <= k <= .3 and 12 <= h <= 16)
    print("MV+A composition", Counter(cls(r) for r in tab if in_mvA(r)))

    by = defaultdict(Counter)  # delta = lambdaB - lambdaA in the substitution/harm region (E14)
    for r in tab:
        k, h = r["kappa"] / r["age"], r["h"] / r["age"]
        if r["amp"] == 6 and .05 <= k <= .15 and 4 <= h <= 8 and .625 <= r["eta"] <= .875:
            by[round(r["lambdaB"] - r["lambdaA"], 3)][cls(r)] += 1
    for dl in sorted(by):
        c = by[dl]; n = sum(c.values())
        print(f"delta {dl:+.2f}: n={n:3d} AB={c['AB']/n:.0%} C={c['C']/n:.0%} other={1-(c['AB']+c['C'])/n:.0%}")

if __name__ == "__main__":
    main(sys.argv[1])
```

**Mục đích khoa học của từng khối:**
- **`dedup` và câu `assert`.** Dòng bị bỏ khi gộp phải giống hệt bản được giữ. Nếu `assert` fail, bước gộp bảng sai, và mọi số đếm phía sau đều đáng ngờ.
- **`cls`, với C được xét trước.** Đây chính là thứ tự ưu tiên giải thích E13: X2065 có Ḡ_M = 13,4 nhưng vẫn bị xếp vào C.
- **Khối identity.** Đây là test, không phải phát hiện (Part 2). Ngưỡng 1e-12 để phân biệt sai số làm tròn với vi phạm thật.
- **`q_linear`.** Đây là E9: record phải ghi rõ cách tính phân vị.
- **`in_mvA` quy tọa độ về age 1.** Đây đúng là lỗi mà errata E3 từng sửa: bộ lọc cũ so tọa độ thô, chưa quy về age 1.

**Output khi tôi chạy trên raw tại tag:**
- 1430 dòng raw → 1376 dòng bảng; 54 dòng bị bỏ đều có bản sao giữ lại với số y hệt.
- Số lớp: A 301, B 43, AB 161, J 14, C 334, D 523. Lưới đều map1: 21/4/7/1/68/243.
- S11 sai lệch lớn nhất 3,6·10⁻¹⁵; 0 vi phạm cận dưới của Γ̄.
- Lớp A (age 1, ±6): n = 211, trung vị 1,531, q90 = 2,444, max 4,011, trung vị Ḡ_M 0,012.
- Lớp AB: 155/161 dòng có Γ̄ < 0; số dòng gần thay thế hoàn toàn: 33 (ngưỡng < 0,1 pp) và 24 (< 0,05 pp).
- Hộp MV+A: 11 C, 7 B.
- Bảng theo δ: δ ∈ {0,25; 0,5} gần như toàn AB (100%, 95%); δ ≤ −0,5 và δ ≥ 1 toàn C (δ = −0,25: 83% C); δ = 0,75 là dải chuyển tiếp; δ = 0 không có dòng AB hay C nào.

Tôi cũng đã kiểm Bước 5:
- Tag `explore-v13-regime-map` là annotated tag, trỏ tới commit `574a36f` ✓.
- Inventory v3 có map1 344, map2 576, map3age 216, map4amp 126, tổng 1396 khóa ✓.

**Kết quả: 9 phép kiểm khớp PHASE_4.** Chưa kiểm được K2, K5/E11 và K6/E12, vì cả ba cần chạy engine.

**Một test nên thêm (tôi chưa làm):** một file CSV giả 6 dòng, mỗi dòng thuộc một lớp, cộng một dòng trùng tọa độ, với đáp án **bạn tự tính tay**. Lý do: script của tôi khớp số của AI chưa chứng minh cả hai đúng, vì hai bên có thể cùng hiểu sai một luật. Chỉ có đáp án tính tay mới độc lập với logic của AI.

---

## 5. Khái niệm 4: DL-103, một quyết định chỉ bạn ký

DL-103 quyết ba việc:
1. Mở Phase 4 theo PHASE_4.md.
2. Chọn cách đánh số phase.
3. Ghi rõ bốn quyết định chỉ tác giả được ký.

**Hai phương án đánh số:**

| | **v1.2** (PHASE_4 đề xuất) | **Giữ v1.1, gọi Phase 4A/4B** |
|---|---|---|
| Khớp MASTER PLAN v1.0 bạn đang dùng | Có (từ Phase 4 trở đi) | Không |
| Văn bản đã đóng băng có bị lệch số? | Có, nên cần bảng ánh xạ 6 dòng | Không |
| Rủi ro | Đọc nhầm "Phase 5" trong DL-097 | Chạy song song hai hệ đánh số khác với plan bạn dùng |

**Luật an toàn cho cả hai phương án:** không sửa văn bản đã đóng băng; ghi bảng ánh xạ trong DL; luôn viết **"Phase N (tên)"**. Tên trong ngoặc mang nghĩa, còn con số chỉ là nhãn. Ví dụ: hạn của D22 luôn là "trước phase mechanism", dù phase đó mang số 5 hay 6.

**Khuyến nghị của tôi: chọn v1.2.** Bản v1.1 do AI áp ngoài repo, bạn chưa thật sự dùng nó. Bảng ánh xạ lại nhỏ. Dù sao đây là quyết định sổ sách, không phải quyết định khoa học; chọn bên nào cũng được miễn có bảng ánh xạ. Đừng tốn quá 15 phút cho nó.

**Vì sao ghi "bốn quyết định chỉ tác giả ký" ngay trong DL mở phase?** Bốn quyết định đó là: baseline và luật đọc kết quả; số card mới và vùng của chúng; ngân sách CF-v3; nhãn Gate 4. Đây là một cam kết trước, chống lại việc ủy quyền dần dần trôi đi, như ở Phase 3R khi nhãn Gate do AI chọn. Nó giống đặt luật trước khi gặp cám dỗ. Đây là luật bạn tự đặt cho mình; tôi không áp nó lên bạn.

**Một điểm nên tự kiểm trước khi ký.** Phần "Why" của khung DL-103 ghi: "gói v2 bỏ ngỏ *differ* và *interact*". Sau Part 2, bạn kiểm được câu này. Câu 6 (vùng A) ứng với *differ*: state có giá trị dương trong khi model gần 0. Câu 7 ứng với *interact*: substitution trong AB **không** bị identity ép, khác với Γ̄ > 0 trong vùng C. Nếu bạn tự giải thích được hai ý này, phần "Why" là của bạn.

---

## 6. Khái niệm 5: exposure và forking log #0

| | Exposure register | Forking log |
|---|---|---|
| Ghi gì | Tọa độ nào đã có người nhìn outcome | Phân tích hoặc lựa chọn nào đã được thử |
| Bảo vệ | Tính độc lập của mẫu confirmation (rủi ro 2 ở Part 1) | Chống multiplicity ẩn khi chọn claim (rủi ro 1) |
| Ví dụ | 8 điểm chạy engine native trong phiên soạn PHASE_4 | Bảng theo δ, thành phần MV+A, hộp minh họa vùng A |

**Vì sao phải ghi cả những phân tích không tạo tọa độ mới?** Vì chúng định hình những hộp bạn sẽ vẽ sau này. Nếu L4.5 vẽ hộp theo trục δ, người đọc cần biết bảng δ **đã được xem trước đó**. Đó là lý do có forking log #0.

**Thành thật về phiên này.** Chính phiên dạy học này cũng đã "nhìn" dữ liệu: tôi đã tính bảng δ, thành phần MV+A, tỉ số C̄ theo biên độ và tính đơn điệu theo age. Không chạy engine, không tạo tọa độ mới. Nếu muốn ghi chặt chẽ, có thể thêm một dòng:

> *"Phiên AI 30/10, dạy L4.1: đếm lại từ raw tại tag; bảng δ; thành phần MV+A; tỉ số C̄ theo biên độ; tính đơn điệu theo age. Không chạy engine, không tạo tọa độ mới."*

**Một điểm tôi chưa rõ.** Inventory v3 đã có mục `ai_session_probe_unsaved` với 8 bản ghi. Tôi không biết đó có phải 8 điểm của K6 hay không. Hãy kiểm khi viết dòng exposure, đừng giả định.

---

## 7. Thứ tự commit khi thực thi

```text
1. Record (sinh từ raw) + errata E1–E14
2. DL-103
3. Dòng exposure + forking log #0
   ── tất cả phải có TRƯỚC: dung sai của L4.3 Part B, mọi lần chạy native,
      và việc tính bất kỳ hộp nào ở L4.5
```

Lý do: commit là dấu thời gian của câu "tôi đã biết những gì".

## 8. Có đang làm quá mức cần thiết không?

| Việc | Bảo vệ claim nào | Mức |
|---|---|---|
| Record sinh từ raw + mục (8) | Mọi claim lấy từ bản đồ | **Essential** |
| E11, E12, E13 | Cách vẽ vùng; cách kể chuyện | **Essential** |
| DL-103 + bảng ánh xạ | Hạn D22; nghĩa của "Phase 5" | **Essential**, nhưng chỉ mất khoảng 15 phút |
| Dòng exposure | Tính độc lập của mẫu CF | **Essential** |
| E14 | Cách vẽ hộp ở L4.5 | Recommended |
| Test CSV giả 6 dòng | Độc lập với logic của AI | Recommended |
| E9 | Không bảo vệ claim nào | Một dòng là đủ |
| Tự chạy lại 25 test của nhánh (K1) | Code bản đồ khớp plant | Optional cho L4.1 |

Ước lượng 0,5–1 ngày của plan là hợp lý. Pilot từng có `experiments/R3R_01_recount/mutants.py`; theo tên thì có lẽ đó là các phiên bản cố ý làm sai để kiểm script (tôi chưa đọc). Với L4.1 thì làm vậy là quá mức cần thiết.

## 9. 🔗 Liên hệ với việc bạn từng làm

`PHASE_3R_discovery_record.md` của pilot là khuôn mẫu sẵn: có provenance, mục thiết kế lấy mẫu, errata append-only E1–E7. Record của bản đồ nên có cùng khung, để người đọc thấy hai cuốn sổ discovery được ghi cùng một cách.

---

## 10. Toàn bộ L4.1 cho phép nói gì

**Được nói:**
- Main có record của regime map.
- Bản đồ là discovery thích nghi do AI thiết kế và chạy.
- Các con số được trích khớp raw, trừ E11/E12 đang chờ L4.3.
- Chỉ hai phát biểu là discovery ứng viên.

**Không được nói:**
- Bất cứ điều gì về độ đúng của bản đồ dưới engine native.
- Bất cứ điều gì về realism hay novelty.
- Rằng bản đồ là evidence.

## 11. Reviewer có thể hỏi

1. *"Claim vùng A đến từ một lượt quét thích nghi do AI chạy. Người đọc biết được gì đã được thấy trước khi giả thuyết bị khóa?"* Câu này được trả lời bằng record và thứ tự commit, khi bạn thực thi.
2. *"Các con số trong câu chuyện của bạn có lấy từ raw không?"* Đã trả lời được 9 phép kiểm; E11 và E12 còn chờ.
3. *"Ai ra các quyết định khoa học?"* Chỉ trả lời được một phần: DL-103 và nhãn provenance có giá trị khi bạn thật sự đọc rồi ký.

## 12. ⚠️ Bẫy người mới

1. Sửa REGIME_MAP trên nhánh cho "đúng". Làm vậy là phá nguyên tắc append-only.
2. Thấy script của mình khớp số của AI rồi kết luận "đã kiểm độc lập". Chỉ độc lập khi bạn tự viết luật, hoặc có đáp án tính tay.
3. Ghi "tác giả kiểm lại" cho E11/E12 khi chưa chạy engine.
4. Ký DL-103 do AI soạn mà không đọc bảng ánh xạ. Đó chính xác là rủi ro ER3.
5. Quên ghi chính phiên dạy học này vào exposure hoặc forking log.
6. Merge nhánh bản đồ vào main.

## 13. 🧠 Tư duy researcher

> Một con số chỉ đáng trích khi bạn chỉ ra được: nó sinh từ file nào, bằng luật nào, ai kiểm, lúc nào.

Ghi sổ không phải thủ tục hành chính. Nó là cách để tương lai kiểm được quá khứ.

## 14. Bài tập hiểu (khuyến nghị)

- Viết mục (8) của record: 4–6 câu "record này không cho phép nói…" bằng lời của bạn.
- Tự tạo file CSV giả 6 dòng, tính tay lớp của từng dòng, rồi chạy qua hàm `cls()` để so.

## 15. Tự kiểm (tùy chọn)

1. Một erratum có bốn trường nào? Vì sao errata phải append-only?
2. Vì sao mức L̄ lệch 0,7% mà contrast không lệch 0,7 pp?
3. Một card do AI soạn, commit trước khi có dữ liệu: đó có phải prereg hợp lệ không? Có được ghi "tác giả dự đoán" không?
4. Exposure register và forking log bảo vệ khỏi hai rủi ro nào?
5. Từ giờ, bạn viết hạn của D22 như thế nào?

---

## 16. LESSON GATE: L4.1

**Hiểu biết.** Sau L4.1, bạn nên tự giải thích được:
- Bản đồ được tạo ra thế nào, và vì sao nó là discovery.
- Hai rủi ro: nhiễm thiết kế và exposure.
- Vì sao số đếm lớp không phải tần suất.
- Cách tự dẫn S07, S08, S11, S12 và cận dưới của Γ̄.
- Vì sao chỉ câu 6 và câu 7 sống sót.
- Errata là gì; bốn nhãn provenance; vì sao thứ tự commit là bằng chứng.

**Trạng thái thực thi:** chưa bắt đầu. Record ⬜ · DL-103 ⬜ · dòng exposure ⬜ · forking log #0 ⬜.
- Phần AI đã kiểm giúp: recount 9 phép kiểm ✓, tag ✓, inventory ✓.
- Còn chờ: E11 và E12, sẽ kiểm ở L4.3.

**Phụ thuộc khoa học.** Khi thực thi thật, L4.3 Part B và L4.5 chỉ nên bắt đầu sau khi record, DL-103 và dòng exposure đã được commit.

**G-level:** vẫn là G1. L4.1 không tạo evidence nên không nâng mức.

**Có học L4.2 được không?** Có. L4.2 xây trực tiếp trên Part 2: ba toy hai state, phân tích thứ nguyên (vì sao age không phải một chiều), và δ như một tọa độ tổ chức.

**Điều cần giữ trong đầu.** Bản đồ là một discovery rộng, do AI chạy, và hầu hết những gì nó "thấy" là identity hoặc điều đã kỳ vọng. Hai thứ có thể là tri thức mới là vùng A và việc Ḡ_S|M1 nhỏ trong lớp AB. Cả hai mới chỉ là ứng viên. Nhiệm vụ của L4.1 không phải chứng minh chúng, mà là ghi lại trung thực những gì đã thấy, trước khi bất kỳ phân tích mới nào có thể làm mờ ranh giới giữa "đã thấy" và "đã dự đoán".

Nếu bạn muốn giữ file `recount.py` để chạy sau, tôi có thể gửi nó. Khi muốn học tiếp, bạn chỉ cần nói "tiếp tục L4.2".