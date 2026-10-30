# LESSON 4.3, Part 2/2: Thiết kế một audit có thể nói "không"

```text
L4.3  Part 1 ✓ Một con số "đúng" nghĩa là gì
      Part 2 ← BẠN Ở ĐÂY: dung sai viết trước · vùng ứng viên · chạy · quyết định · luật MC · code
      → Lesson Gate L4.3
```

### 0. Những gì tôi đã kiểm trong repo cho Part 2

- **Giao diện engine native.** Tôi đã đọc code: hàm `evaluate_level(case_id, parameters, K, ref, cache)` nằm trong `experiments/R3R_14_lean_close/engine.py`, và có sẵn hàm `write_once`. Mỗi dòng kết quả native có các trường `Cref`, `G_S`, `G_M`, `Gamma`, `G_S_M1`, `G_M_S1`, `arithmetic_pass`, `validity_errors`, `CF_computed`.
- **Danh sách CF-v2** nằm ở `cf_generation/attempt01/regimes_cf.json`: 270 dòng, tham số ghi bằng phân số chính xác.
- **Receipt numerics chỉ phủ frame của card v2.** Phần scope ghi đúng câu: "card v2 frame only". Vì vậy chạy native trên vùng của bản đồ là chạy **ngoài** vùng đã được chứng nhận. Đây là thêm một lý do Part B của L4.3 cần tồn tại, và cũng là lý do L4.7 sau này phải làm numerics coverage riêng cho frame v3.
- **Test (2) của plan không làm được như đã viết.** Plan yêu cầu tái tạo chính xác 8 kết quả native trong file `native_probe_summary.csv`, nhưng file này nằm trong gói kiểm tra đang thiếu. Cách xử lý: xin lại file đó, hoặc chỉ so với phần tóm tắt K6 trong PHASE_4 §0.3. Phần tóm tắt yếu hơn, vì chỉ có giá trị lớn nhất và một điểm XM2S110.
- **Tôi không chạy được engine native.** Code `relabel.py` ở §7 là bộ khung, **chưa chạy**.

---

## 1. Câu hỏi của Part 2

> Thiết kế audit thế nào để kết quả của nó **có thể buộc mình dừng lại**, và để không ai nói được rằng mình chọn luật sau khi đã thấy số?

## 2. Mental model: audit là một thí nghiệm nhỏ có prereg riêng

Audit trông giống một thủ tục kỹ thuật, nhưng thực chất nó là một thí nghiệm. Vì vậy nó cần một Experiment Card:

| Mục | Nội dung |
|---|---|
| **Question** | Những con số dùng để ra quyết định trên bản đồ có đứng vững dưới engine native ở mức (640, 4) không? |
| **Why** | Mọi claim mới sẽ được chấm bằng engine native |
| **Kỳ vọng** | Đây là verification, không phải giả thuyết khoa học. Dựa vào K6, ta kỳ vọng độ dịch Ḡ_S phần lớn âm và nằm trong dung sai, kèm một số điểm lật nhãn gần mức 1% |
| **Biến độc lập** (thứ mình thay đổi) | Engine: pilot so với native. Mức số học: (640, 4) so với hai mức lân cận |
| **Biến phụ thuộc** (thứ mình đo) | Sáu contrast tính theo % C̄_ref; nhãn lớp; d; cờ UNRESOLVED |
| **Giữ cố định** | Tọa độ regime (quy về age 1), plant, luật phản ứng, c_sw = 0 |
| **Confounder** (yếu tố gây nhiễu kết luận) | (i) Pilot dùng dt = 1/120 s, native dùng 1/480 s, nên một phần độ dịch là do dt chứ không phải bug. (ii) Điểm map3age quy về age 1 chỉ tương đương xấp xỉ. (iii) Vùng của bản đồ nằm ngoài frame đã chứng nhận |
| **Đối chứng** | Số pilot (để so sánh), cùng hai mức native lân cận (cho luật R1) |
| **Metric chính** | Danh sách điểm lật nhãn và tỉ lệ UNRESOLVED dự kiến trong mỗi vùng, vì đây là thứ làm đổi quyết định |
| **Metric phụ** | Phân phối độ dịch (trung vị, max, dấu) |
| **Chứng minh được** | Trên các điểm đã biết, các con số mà quyết định dựa vào chính là con số engine chấm sẽ thấy |
| **Không chứng minh được** | Regime **mới** trong hộp sẽ cư xử giống điểm discovery; engine đúng với mạng thật; engine đúng ở mọi đường code |

---

## 3. Các bước, và vì sao mỗi bước tồn tại

### Bước 1: viết dung sai **trước** khi chạy

Lưu vào `experiments/P4_03_map_audit/prereg.md` và commit trước mọi lần chạy native.

| Phép kiểm | Dung sai | Bảo vệ khỏi | Nếu không đạt |
|---|---|---|---|
| Tái lập trùng bit trên một mẫu dòng | Trùng cả 9 trường | Dữ liệu bị hỏng do sự cố khi chạy | HOLD, điều tra đoạn chạy đó |
| Identity trên mọi dòng | Như K4 | Sổ sách sai | HOLD |
| Độ dịch native so với pilot (Ḡ_S, Ḡ_M, Γ̄, Ḡ_S\|M1, Ḡ_M\|S1) | ≤ 0,25 pp | Một engine có bug | HOLD, có thể cần MC làm trọng tài |
| R1 ở (640, 4); `arithmetic_pass`; validity | Chênh với hai mức lân cận ≤ 0,25 pp; không có lỗi | Độ phân giải số học không đủ | Nâng mức theo R3, hoặc HOLD |
| Nhãn lớp | **Không đặt dung sai.** Chỉ liệt kê mọi điểm lật | — | — |

**Vì sao không đặt dung sai cho nhãn?** Nhãn native là **sản phẩm** của audit, sẽ được dùng ở L4.5. Nó không phải một phép kiểm đạt/không đạt. Nếu đặt ngưỡng kiểu "tối đa 10 điểm lật", bạn tự mời mình chỉnh ngưỡng sau khi thấy số.

**Một dòng trung thực phải có trong file prereg:** *"Khi viết file này tôi đã thấy K6: 8 điểm, độ dịch lớn nhất 0,136 pp."*

Một dung sai viết sau khi đã thấy một phần dữ liệu thì yếu hơn. Điều làm nó vẫn bảo vệ được là con số 0,25 pp **không do bạn chọn sau khi thấy K6**. Nó lấy từ contract: TOL_NUM = 1/400 C̄. Một con số cố định từ bên ngoài, có trước dữ liệu, là thứ khó bị nghi ngờ nhất.

### Bước 2: tái lập trùng bit, phiên bản gọn

Chỉ lấy dòng từ những chỗ có rủi ro thật:
- **Đoạn chạy tiếp của map2** (lấy ID từ `map2_resume.log`) và **đoạn chạy tiếp của plantrobust**. Đây là nơi hai tiến trình từng ghi chung một thư mục.
- **Vài dòng map3age có age ≠ 1**, vì chúng đi qua phần code mở rộng.
- Cộng thêm 6 dòng của K2.

Mức kiểm này (mức 1) bắt đúng loại rủi ro mà sự cố tạo ra, và không làm gì thừa.

### Bước 3: identity trên mọi dòng

Chạy lại `recount.py` (L4.1 Part 3) trên một checkout sạch của tag. AI đã chạy một lần; khi thực thi, bạn tự chạy lại để có bằng chứng của chính bạn.

### Bước 4: chốt vùng ứng viên **trước khi** vẽ hộp

**Vì sao.** Bước này chặn một vòng lặp nguy hiểm:

```text
vẽ hộp → chỉ gán nhãn lại điểm trong hộp → hộp có vẻ chưa đẹp → vẽ lại → …
```

Mỗi vòng là một forking path. Sau vài vòng, tập điểm được kiểm co lại thành đúng những điểm ủng hộ cái hộp.

**Cách làm.**
- Vùng ứng viên phải **rộng**, lấy từ chính lời mô tả của REGIME_MAP, viết theo tọa độ age 1, và commit trước khi chạy.
- Ví dụ trong plan cho vùng A rộng gồm 428 điểm. Vùng AB rộng gồm 218 điểm; nó vẽ theo trục thô nên trộn cả lớp C, nhưng như vậy là ổn cho việc gán nhãn lại.
- Điểm map3age được chạy ở tọa độ age 1 tương đương, tức (κ/a, h/a).

**Nếu muốn gọn hơn,** làm Part A của L4.5 trước (lọc bằng identity, prior, và giá trị cho RQ; không cần số native). Ứng viên nào bị loại ở đó thì bỏ luôn vùng của nó.

### Bước 5: chạy bundle native

**Chạy gì.** Với mỗi điểm, chạy ba mức (640, 4), (320, 4), (640, 2).

**Bốn nguyên tắc khi chạy:**
- Kết quả chỉ ghi một lần (write-once).
- Chạy tiếp được nếu bị dừng.
- Kiểm hash mã nguồn so với receipt trước khi bắt đầu.
- Có guard từ chối mọi khóa trùng với CF.

Nếu đặc tả baseline của L4.4 đã được commit, tính luôn các ô baseline trong cùng lần chạy để đỡ tốn compute.

**Ngân sách** (ước lượng thô, có điều kiện):
- Theo §5.5 của plan, mỗi lần chạy ở (640, 4) mất 2,8–9,4 s khi h ≤ 4 và khoảng 42 s khi h = 8. Một dòng calibration tôi xem (h = 8) mất 18 s.
- Vùng A: 428 điểm, đều có h/τ ≤ 4.
- Vùng AB: 218 điểm, khoảng một nửa có h/τ = 8.
- Cộng lại cỡ **vài CPU-giờ**.
- Các số thời gian này đo trên 8 điểm với 2 CPU. Hãy **đo 3–5 điểm đại diện trước**, rồi mới chốt ngân sách.

### Bước 6: kiểm từng dòng native

Mỗi dòng phải thỏa: identity đúng; `arithmetic_pass` là True; `validity_errors` rỗng; `CF_computed` là False; R1 đạt.

### Bước 7: lập bảng so sánh

Bảng gồm:
- **Phân phối độ dịch:** trung vị, max, và tỉ lệ dịch âm.
- **Danh sách điểm lật nhãn.**
- **Tỉ lệ UNRESOLVED dự kiến** cho mỗi vùng, tức tỉ lệ điểm có |z − ngưỡng| ≤ d.
- **Các vi phạm R1** (nếu có).

**Cách đọc.** Nếu khoảng 95% độ dịch cùng dấu, đó là độ dịch **có hệ thống**: vùng sẽ co hoặc nở theo một hướng (Part 1, §9). Còn nếu dấu ngẫu nhiên thì độ dịch chỉ là nhiễu.

### Bước 8: quyết định

| Kết cục | Điều kiện | Hệ quả |
|---|---|---|
| **PASS** | Mọi dung sai đạt; không điểm nào lật nhãn | Dùng nhãn native (trùng với pilot) |
| **PASS có giới hạn** | Mọi dung sai đạt; có điểm lật nhãn | Dùng nhãn native; liệt kê điểm lật; L4.5 chỉ dùng native |
| **HOLD** | Vi phạm tái lập, identity, R1, validity hoặc dung sai | Điều tra như một bug; không vẽ hộp, không thêm card cho tới khi giải quyết xong |

Sau đó viết báo cáo và thêm dòng exposure: "gán nhãn native cho N điểm discovery đã lộ". Người quyết định nhãn audit là **bạn**.

---

## 4. Dự đoán trước khi chạy (khuyến nghị)

Khác với Bước 6 của L4.2, ở đây **chưa ai** tính native trên các vùng này, ngoài 8 điểm của K6. Đây là một cơ hội dự đoán thật.

Tôi không đưa sẵn con số, để tránh neo suy nghĩ của bạn. Đây là khung lập luận:

1. K6 cho 8/8 độ dịch âm, độ lớn từ 0,002 đến 0,136 pp. Vậy bạn dự đoán bao nhiêu % điểm có độ dịch âm?
2. Ở L4.3 Part 1, tôi đếm được 27/263 dòng lớp A có Ḡ_S < 1,136. Vậy bạn dự đoán bao nhiêu điểm lật nhãn trong vùng A?
3. Bạn có dự đoán điểm nào vượt dung sai 0,25 pp không? Nếu có, ở đâu? (Gợi ý: những nơi chưa có điểm kiểm nào chạm tới, như κ/τ = 0,05.)

Viết câu trả lời vào `prereg.md`, theo dạng: *"Tôi dự đoán … vì …"*.

---

## 5. Bug khác negative result, áp vào audit

- **Negative result trong audit** là chuyện như: nhiều điểm lật nhãn, hay vùng A co lại dưới native. Đây là **thông tin**, không phải audit thất bại. Đừng "sửa" nó bằng cách đổi mức số học hay nới dung sai. Kết quả đúng phải ghi là: "dưới engine chấm, vùng A nhỏ hơn bản đồ".
- **Bug** là một vi phạm, ví dụ độ dịch 0,6 pp tại một điểm. Khi đó **đừng mặc định native đúng** chỉ vì nó mịn hơn. Hãy điều tra theo thứ tự:

```text
(1) Kiểm input: quy đổi về age 1, làm tròn, tham số    ← lỗi hay gặp nhất, rẻ nhất để kiểm
(2) Kiểm R1 ở CẢ HAI engine: engine nào chưa hội tụ?
(3) Ý kiến thứ ba: MC (mức 3) ngay tại điểm đó          ← trọng tài khi hai engine bất đồng
```

---

## 6. Khái niệm 6: kiểm chứng bắc cầu, và khi nào cần MC trực tiếp

**Trực giác (bất đẳng thức tam giác).** Nếu A khớp B trong phạm vi t₁, và B khớp C trong phạm vi t₂, thì A khớp C trong phạm vi t₁ + t₂.

**Trong project:**
- **MC ↔ pilot:** đã có từ L3R.3, trên 8 regime, ở dt = 1/120 s.
- **Pilot ↔ native:** đã có qua các anchor X2065, X1008, X1009 và 8 điểm của K6.
- **Suy ra MC ↔ native:** chỉ là một cận lỏng. Một phần chênh lệch đến từ dt khác nhau.

**Giới hạn của bắc cầu.** Bắc cầu chỉ đúng ở **những vùng mà cả hai mắt xích đã được kiểm**. Một mắt xích kiểm ở κ ≥ 0,1 không nói gì về κ = 0,05.

**Luật gọn của plan.** Chỉ chạy MC trực tiếp trên native khi:
- **(i)** native và pilot lệch nhau quá 0,25 pp tại một điểm có ảnh hưởng tới quyết định; **hoặc**
- **(ii)** claim mới phụ thuộc vào một đường code mà chưa anchor hay probe nào chạm tới.

Nếu không rơi vào hai trường hợp đó, viết lập luận bắc cầu và dừng.

**Vì sao không chạy MC cho mọi thứ?** Ngoài chi phí, còn một lý do kỹ thuật. MC có nhiễu lấy mẫu riêng. Để phân giải được khoảng cách cỡ 0,03 pp quanh ngưỡng, nhiều khả năng MC cần một số mẫu rất lớn; tôi chưa tính con số cụ thể. MC là công cụ tốt để bắt **lỗi đặc tả thô** (sai lệch lớn hơn 0,1 pp rất nhiều), không phải công cụ để quyết định nhãn ở sát ngưỡng.

**Trong project này:** vùng AB có 73 điểm ở κ/τ = 0,05, nên luật (ii) **có khả năng** bị kích hoạt nếu card SUB sống sót qua L4.5.

---

## 7. Code: bộ khung `relabel.py` (chưa chạy)

**Code này tồn tại để trả lời Q4.3:** các con số quyết định của bản đồ có đứng vững dưới engine confirmation không?

**Pseudocode:**

```text
verify_sources()          → hash mã nguồn engine khớp receipt, nếu không thì dừng
forbidden = cf_keys()     → tập khóa CF-v2, chỉ dùng để TỪ CHỐI
for point in zone_points(table, zone, forbidden):
    rows = run_bundle(point)          → 3 mức, write-once, chạy tiếp được
    result = compare(pilot, rows)     → guard identity/validity, shift, d, cờ
```

**Code:**

```python
"""relabel.py — L4.3 Part B skeleton (NOT run here: native engine needs C++/Boost).
Serves Q4.3: do decision-relevant regime-map numbers hold under the confirmation engine?"""
import hashlib, json
from fractions import Fraction as F
from pathlib import Path

LOCK = "notes/phases/numerics_v1_3_1_lean.lock.json"
CF_V2 = "results/lessons/l3r_7/lean_close/cf_generation/attempt01/regimes_cf.json"
LEVELS = [(640, 4), (320, 4), (640, 2)]            # (K*, ref*) and its two R1 neighbours
METRICS = ["G_S", "G_M", "Gamma", "G_S_M1", "G_M_S1"]

def require(ok, msg):                               # explicit raise: survives python -O
    if not ok:
        raise RuntimeError(msg)

def verify_sources():
    """Refuse to run if a frozen engine file differs from the numerics receipt."""
    for path, sha in json.load(open(LOCK))["source_sha256"].items():
        require(hashlib.sha256(Path(path).read_bytes()).hexdigest() == sha, f"source changed: {path}")

def cf_keys():
    rows = json.load(open(CF_V2))["rows"]
    return {tuple(F(r["regime"][k]) for k in ("lambdaA", "lambdaB", "u", "kappa", "h")) for r in rows}

def zone_points(table_rows, zone, forbidden):
    """Discovery points inside a pre-committed broad zone, at age-1 equivalent coordinates."""
    out = []
    for r in table_rows:
        age = F(r["age"])
        p = dict(lamA=F(r["lambdaA"]), lamB=F(r["lambdaB"]), u=2 * F(r["eta"]),
                 kappa=F(r["kappa"]) / age, h=F(r["h"]) / age)
        if F(r["amp"]) == 6 and zone(p):
            key = (p["lamA"], p["lamB"], p["u"], p["kappa"], p["h"])
            require(key not in forbidden, f"{r['id']} is a CF-v2 regime")   # golden rule 1
            out.append((r["id"], p, {m: float(r[m + "_pctC"]) for m in METRICS}))
    return out

def run_bundle(case_id, p, outdir, cache):
    from experiments.R3R_14_lean_close import engine
    engine.configure()
    params = (p["lamA"], p["lamB"], p["kappa"], p["u"] / 2, p["h"], F(0))
    rows = {}
    for K, ref in LEVELS:
        path = Path(outdir) / case_id / f"level_{K}_{ref}.json"
        if path.exists():                           # resumable: never recompute, never overwrite
            rows[(K, ref)] = json.load(open(path)); continue
        row = engine.evaluate_level(case_id, params, K, ref, cache)
        engine.write_once(path, row); rows[(K, ref)] = row
    return rows

def pct(row, m):
    return 100 * float(F(row[m]) / F(row["Cref"]))

def compare(pilot, rows, metric="G_S", boundary=1.0, tol=0.25):
    main = rows[(640, 4)]
    z = {m: pct(main, m) for m in METRICS}
    require(abs(z["Gamma"] - (z["G_S_M1"] - z["G_S"])) < 1e-9, "S11 violated")          # identity guards
    require(min(z["G_M"], z["G_S_M1"], z["G_M_S1"]) > -1e-9, "S07/S08 violated")
    require(main["arithmetic_pass"] and not main["validity_errors"] and not main["CF_computed"], "validity")
    d = {m: max(abs(pct(rows[l], m) - z[m]) for l in LEVELS[1:]) for m in METRICS}        # R1 per metric
    shift = {m: z[m] - pilot[m] for m in METRICS}
    return dict(z=z, d=d, shift=shift,
                over_tol=[m for m in METRICS if abs(shift[m]) > tol or d[m] > tol],      # → HOLD
                unresolved=abs(z[metric] - boundary) <= d[metric])                        # R6
```

**Mục đích khoa học của từng khối:**
- **`verify_sources`.** Nếu engine đã bị sửa, dù chỉ một byte, thì "native" không còn là engine sẽ chấm confirmation, và cả audit mất ý nghĩa.
- **Guard trong `zone_points`.** Đây là luật vàng 1 được viết thành code: không bao giờ chạy native trên một regime CF. Bình thường không có điểm nào trùng, vì CF đã được rút cách xa các điểm đã thấy. Guard tồn tại để bắt những lỗi không ai lường trước.
- **`require` trong `compare`.** Biến vi phạm identity hoặc validity thành **dừng chương trình** thay vì một cảnh báo dễ bị bỏ qua. Tôi dùng `raise` tường minh thay vì `assert`, vì `assert` bị tắt khi chạy Python với cờ `-O`.
- **`metric` và `boundary` là tham số.** Vùng A dùng Ḡ_S với ngưỡng 1%. Một card SUB sẽ dùng Γ̄ với ngưỡng riêng của nó.

**Các test nên có:**
1. Guard CF từ chối một dòng giả có khóa trùng CF.
2. Guard identity bắt được một dòng giả đã bị sửa giá trị `Gamma`.
3. Tái tạo 8 kết quả của K6: **đang bị chặn** vì thiếu file (xem §0).

---

## 8. Các kết cục có thể xảy ra, và mỗi kết cục dạy gì

| Kết cục | Ý nghĩa | Ảnh hưởng tới L4.5 |
|---|---|---|
| PASS có giới hạn, vài điểm lật, vùng A co nhẹ | Kết cục được kỳ vọng nhất | Vẽ hộp trên nhãn native; ước p̂ thấp hơn bản đồ |
| Nhiều điểm sát ngưỡng thành UNRESOLVED | Card SV có rủi ro R5 về mặt cấu trúc | Có thể chọn 0 card SV, hoặc hộp xa ngưỡng hơn (ghi forking log) |
| HOLD tại κ/τ = 0,05 | Có thể engine sai ở vùng chưa kiểm, hoặc có thể pilot sai | Chạy MC làm trọng tài; tạm dừng card SUB |
| PASS không điểm nào lật | Ít khả năng xảy ra, vì K6 đã có một điểm lật | Kiểm lại xem có đúng là native đã được chạy không |

## 9. 🔗 Liên hệ với việc bạn từng làm

- **Ở Phase 3R,** native05 từng mất hai dòng kết quả vì lỗi serialize kiểu bool của NumPy; docstring của `engine.py` ghi lại điều này. Đó là lý do `write_once` tồn tại. Một bài học vận hành cụ thể đã được biến thành code.
- **Kỷ luật "dung sai viết trước" bạn đã dùng ở L3R.3,** khi calibration native được chấm theo luật có sẵn. L4.3 áp lại đúng kỷ luật đó cho một frame mới.

## 10. Toàn bộ L4.3 cho phép nói gì (khi đã thực thi xong)

**Được nói:**
- "Trong phạm vi các phép kiểm này, các con số mà quyết định của Phase 4 dựa vào chính là con số engine confirmation sẽ thấy, trên các điểm đã biết."
- Có một danh sách điểm lật nhãn.
- Có ước lượng tỉ lệ UNRESOLVED cho mỗi vùng.

**Không được nói:**
- "Regime mới trong hộp sẽ cư xử như thế này." Đó là việc của Phase 5.
- "Engine đúng với mạng thật."
- "Đã kiểm độc lập mọi đường code."

## 11. Reviewer có thể hỏi

1. *"Dung sai được chọn trước hay sau khi thấy số?"* **Đã trả lời:** con số đến từ contract, và trong prereg có ghi rõ là đã thấy K6.
2. *"Điểm nào của bạn đổi nhãn dưới engine chấm?"* Trả lời bằng danh sách điểm lật, sau khi thực thi.
3. *"Vì sao không kiểm MC mọi nơi?"* **Đã trả lời** (§6): theo luật gọn, và vì MC không phân giải được ở sát ngưỡng.
4. *"Engine có được kiểm ở κ/τ = 0,05 không?"* **Chưa:** có thể cần MC.

## 12. ⚠️ Bẫy người mới

1. Viết dung sai sau khi đã thấy bảng so sánh.
2. Vẽ hộp trước, rồi chỉ gán nhãn lại các điểm trong hộp.
3. Nới dung sai, hoặc đổi mức số học, để "cứu" một vùng.
4. Mặc định native đúng khi hai engine bất đồng.
5. Quên quy điểm map3age về tọa độ age 1.
6. Chạy native trên một regime CF, kể cả "chỉ để đo thời gian".
7. Dùng `assert` làm guard rồi chạy với `-O`.

## 13. 🧠 Tư duy researcher

> Một phép kiểm chỉ có giá trị khi nó **có thể** buộc bạn dừng lại. Hãy viết điều kiện dừng **trước**, ưu tiên những con số cố định từ bên ngoài (như contract), và ghi thật rõ những gì bạn đã thấy trước khi viết chúng.

## 14. Bài tập hiểu (khuyến nghị)

- Viết `prereg.md` cho audit: bảng dung sai ở Bước 1, câu "đã thấy K6", định nghĩa vùng ứng viên rộng, và ba dự đoán theo khung ở §4.
- Vẽ cây xử lý khi gặp HOLD (§5) bằng lời của bạn.

## 15. Tự kiểm (tùy chọn)

1. Vì sao nhãn lớp không có dung sai, còn độ dịch thì có?
2. Vì sao vùng ứng viên phải chốt trước khi vẽ hộp?
3. Native và pilot lệch nhau 0,5 pp tại một điểm. Ba bước đầu tiên bạn làm là gì?
4. Bắc cầu MC ↔ pilot ↔ native có áp dụng được cho κ/τ = 0,05 không? Vì sao?
5. Vì sao MC không phải công cụ phù hợp để quyết định nhãn ở sát ngưỡng?

---

## 16. LESSON GATE: L4.3

**Hiểu biết.** Sau L4.3, bạn nên tự giải thích được:
- Audit theo claim; ba mức "đúng".
- Sai số ở mức L̄ khác sai số ở contrast, theo cơ chế trọng số chung.
- Độ dịch có hệ thống và nhãn sát ngưỡng.
- R1, R6, R5, và nhãn UNRESOLVED.
- Dung sai bắt bug, còn nhãn native dùng để ra quyết định.
- Vì sao phải chốt vùng trước khi vẽ hộp.
- Ba kết cục; phân biệt bug với negative result; luật MC.

**Trạng thái thực thi:** chưa bắt đầu.
- Việc còn lại: `prereg.md` ⬜; tái lập bit ⬜; identity (chạy lại `recount.py`) ⬜; vùng ứng viên ⬜; bundle native ⬜; bảng so sánh ⬜; nhãn audit ⬜; dòng exposure ⬜.
- Thiếu `native_probe_summary.csv` để làm test (2).

**Phụ thuộc khoa học:**
- Part B của L4.3 chỉ chạy sau khi record và DL-103 của L4.1 đã được commit.
- L4.5 Part B chỉ dùng nhãn native.
- Nếu audit ra HOLD: không vẽ hộp, không thêm card.

**G-level:** vẫn là G1. Audit là verification, không phải evidence cho RQ.

**Có học L4.4 được không?** Có. L4.4 hỏi một câu khác hẳn và rất reviewer: các pattern (MV, SH, lớp A, lớp AB) có còn đứng vững khi so với một **controller đơn giản nhưng hợp lý**, chẳng hạn một luật Stay có margin, hay chúng chỉ tồn tại vì ô 00 là một controller quá yếu (đổi đường ngay khi dự báo có lợi dù chỉ một chút)?

**Điều cần giữ trong đầu.** Audit không hỏi "bản đồ có đẹp không". Nó hỏi "con số mình sắp dùng có phải con số giám khảo sẽ thấy không". Viết điều kiện dừng trước, chỉ kiểm những gì làm đổi quyết định, và coi "vùng nhỏ hơn mình tưởng" là thông tin chứ không phải thất bại.