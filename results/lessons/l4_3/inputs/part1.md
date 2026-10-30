# LESSON 4.3: Audit có phạm vi

## Part 1/2: Một con số "đúng" nghĩa là gì?

### 0. Kiểm nguồn và điều chỉnh plan

L4.3 khớp với trạng thái hiện tại. Phụ thuộc khi thực thi: Part B của L4.3 chỉ nên chạy sau khi record của L4.1 đã được commit; Part A của L4.5 (lọc định tính) có thể làm trước Bước 4 để thu hẹp phạm vi audit. Có bốn điểm tôi muốn làm rõ:

1. **Dung sai pilot–native dùng để bắt bug, không dùng để xác nhận nhãn.** Plan đề xuất dung sai |z_native − z_pilot| ≤ 0,25 pp, trong đó z là một contrast tính theo % C̄_ref. Nhưng K6 cho thấy độ dịch có hệ thống, tới 0,136 pp. Độ dịch này vẫn **đạt** dung sai, nhưng đủ để lật nhãn của những điểm sát ngưỡng 1%. Vì vậy:
   - Dung sai là **máy dò bug**: nếu vượt, audit chuyển sang HOLD và phải điều tra.
   - **Nhãn native** mới là thứ dùng để ra quyết định.

   Plan đã làm đúng như vậy (vẽ hộp trên nhãn native), nhưng không nói rõ sự phân vai này. Tôi nói rõ ra để bạn không nghĩ "đạt dung sai nghĩa là nhãn của bản đồ đúng".

2. **Part A (tái lập) có thể gọn hơn.**
   - Tái lập trùng bit chỉ thật sự cần ở các **đoạn chạy tiếp sau sự cố**, vì đó là nơi có rủi ro file bị ghi đè.
   - map4amp không phục vụ claim nào, nên bỏ.
   - Kiểm identity trên mọi dòng đã làm xong ở L4.1 (script `recount.py`). Khi thực thi chỉ cần chạy lại script đó trên một checkout sạch.

3. **Vùng AB "rộng" trong ví dụ của plan được vẽ theo trục thô.** Tôi đếm được 218 điểm: 107 điểm lớp C, 83 điểm lớp AB. Đây đúng là vấn đề trộn lớp do δ đã gặp ở L4.2. Với **gán nhãn lại** thì không sao, vì vùng này cố ý rộng. Nhưng không được dùng nó làm hộp của card.

4. **Có thể sẽ cần một phép Monte Carlo (MC) trực tiếp.** Vùng AB có 73 điểm ở κ/τ = 0,05. Frame của card v2 chỉ phủ κ ∈ [0,1; 0,3], nên 118 ca calibration native rất có thể chưa chạm tới κ/τ = 0,05. Tôi chưa kiểm anchor hay probe nào khác đã chạm tới vùng này chưa. Nếu card SUB sống sót qua L4.5, luật (ii) về MC trực tiếp (Part 2) có thể sẽ được kích hoạt.

**Những gì tôi không kiểm được:** engine native cần C++ và Boost, tôi chưa chạy. Mọi số native trong bài này (K6) đến từ phiên AI đã soạn PHASE_4.

**Map của L4.3:**

| Part | Nội dung | Khái niệm trong plan |
|---|---|---|
| **1 (bài này)** | Audit theo claim; ba mức "đúng"; sai số ở mức L̄ khác sai số ở contrast; dịch có hệ thống và nhãn sát ngưỡng; R1/R6/R5 và nhãn UNRESOLVED | 1–5 |
| 2 | Thiết kế audit: dung sai viết trước, vùng ứng viên chọn trước khi vẽ hộp, chạy, so sánh, quyết định PASS/HOLD; bug khác negative result; bắc cầu và luật MC; ngân sách; code | 6 + các bước thực hành |

---

### 1. Bạn đang ở đâu?

```text
PHASE 4
  L4.1 Re-entry ✓   L4.2 Đọc bản đồ ✓
  L4.3 Audit có phạm vi ← BẠN Ở ĐÂY (Part 1/2)     tầng evidence: E1 verification
  L4.4 Baseline   L4.5 Quyết định card ← dùng NHÃN NATIVE từ L4.3
```

### 2. L4.3 trả lời câu hỏi gì?

> Những con số mà quyết định ở L4.5 sẽ dựa vào có phải là con số mà **engine chấm confirmation** sẽ thấy không? Nếu không, chúng lệch ở đâu, và nhãn nào bị lật?

### 3. Tại sao cần?

**Ở tầng nghiên cứu,** mọi claim mới sẽ được **chấm** bằng engine native ở mức (640, 4). Bản đồ lại được tính bằng engine pilot (K = 40, dt = 1/120 s). Một hộp vẽ từ số pilot có thể không trùng với những gì native sẽ thấy.

**Ở tầng thực hành,** sau khi thực thi bạn sẽ có: bảng nhãn native, danh sách điểm lật nhãn, và ước lượng tỉ lệ UNRESOLVED cho mỗi vùng ứng viên.

**Nếu bỏ lesson này, ba chuyện cụ thể có thể xảy ra:**
1. Bạn vẽ hộp cho card SV trên nhãn pilot. Native thấp hơn pilot một cách có hệ thống, nên tỉ lệ thành công thật trong hộp thấp hơn thiết kế. Phase 5 trả về WEAKEN hoặc INCONCLUSIVE, và lần confirmation duy nhất bị lãng phí.
2. Hộp chứa nhiều điểm sát ngưỡng. Quá 10% điểm thành UNRESOLVED, luật R5 kích hoạt, và verdict là INCONCLUSIVE **bất kể giả thuyết đúng hay sai**.
3. Sự cố khi chạy bản đồ đã làm hỏng vài dòng mà không ai phát hiện.

### 4. Liên hệ với Main RQ

```text
L4.3 nhãn native ──► p̂ của các hộp ứng viên (bộ lọc khả thi ở L4.5)
                 ──► thiết kế card v3 (L4.6) ──► verdict hợp lệ ở Phase 5
```

Liên hệ này gián tiếp. L4.3 không trả lời "differ/interact"; nó bảo đảm rằng khi Phase 5 trả lời, câu trả lời đó **đo được**.

### 5. Prerequisite

- **Verification khác validation** (MASTER PLAN III.2). Verification hỏi: code có tính đúng mô hình đã định không? Validation hỏi: mô hình có khớp mạng thật không? **L4.3 chỉ là verification.**
- **Từ L4.1:** errata E11 (vi phạm S04 ở mức L̄) và E12 (native thấp hơn pilot).
- **Từ L4.2:** lớp khác vùng; nhãn sát ngưỡng thì mong manh.

---

## 6. Khái niệm 1: audit theo claim

**Trực giác.** Trước khi lái một chiếc xe, bạn kiểm phanh của **chính chiếc xe đó**, không kiểm cả bãi xe.

**Ví dụ networking.** Bạn không verify lại toàn bộ pipeline telemetry. Bạn verify đúng những metric đi vào quyết định routing.

**Định nghĩa.** Phạm vi audit là tập những con số có thể **làm đổi một quyết định**: vẽ hộp nào, p̂ bao nhiêu, thêm card hay không.

| Trong phạm vi | Ngoài phạm vi |
|---|---|
| Ḡ_S quanh mức 1% trong vùng A | map4amp (không có claim nào dùng) |
| Γ̄, Ḡ_S, Ḡ_M, Ḡ_S\|M1 trong dải δ của AB | Mức L̄ (không bao giờ trích dẫn) |
| Các điểm có thể lật nhãn | Lớp D ở xa mọi ngưỡng |

Đây là nguyên tắc **rigor where it protects the claim**: không gán nhãn lại cả 1376 dòng, chỉ gán nhãn những dòng có thể làm đổi một quyết định.

---

## 7. Khái niệm 2: ba mức "đúng"

**Trực giác.** Có ba cách kiểm một bài giải:
1. Bạn chép lại bài của chính mình và ra cùng đáp án.
2. Một người khác giải **cùng cách** và ra cùng đáp án.
3. Một người khác giải **cách khác** và ra cùng đáp án.

| Mức | Định nghĩa | Bắt được | **Không** bắt được | Trong project |
|---|---|---|---|---|
| **1. Tái lập bit** | Cùng code, cùng môi trường, ra kết quả trùng từng bit | File bị ghi đè hoặc hỏng; môi trường khác; kết quả không tất định | Code sai **một cách nhất quán** | K2 (6 dòng) |
| **2. Đồng thuận số** | Hai code khác nhau, cùng một định nghĩa, khác biệt nhỏ hơn dung sai | Lỗi riêng của một engine; sai số cầu phương | Lỗi **chung** của cả hai, ví dụ cùng hiểu sai đặc tả | K6 (8 điểm pilot so với native) |
| **3. Kiểm độc lập** | Một phương pháp khác, ví dụ MC viết lại từ đặc tả | Hiểu sai đặc tả trong engine | Bản thân đặc tả sai | MC của L3R.3 |

**Không mức nào kiểm validation**, tức mô hình có khớp mạng thật không. Đó là việc của Phase 7 và Phase 8.

**Ý chính:** mỗi mức trả lời một câu hỏi khác nhau, và mức cần dùng phụ thuộc vào **rủi ro** đang lo:
- Lo sự cố khi chạy làm hỏng dữ liệu → mức 1.
- Lo engine native sẽ thấy khác pilot → mức 2.
- Lo công thức trong engine bị hiểu sai → mức 3.

---

## 8. Khái niệm 3: sai số ở mức L̄ khác sai số ở contrast

**Trực giác.** Hai người cùng đứng lên một cái cân lệch 1 kg. Cân nặng của từng người đều sai, nhưng **hiệu** cân nặng giữa hai người vẫn đúng.

**Cơ chế.** Engine pilot tính cả bốn ô như trung bình trên **cùng một** bộ trọng số state π̃. Nếu sai số cầu phương làm π̃ lệch khỏi π thật, mọi L̄ đều dịch, nhưng dịch **gần như cùng một lượng**.

**Ví dụ số** (minh họa). Có hai state. Trọng số thật π = (0,5; 0,5); engine dùng π̃ = (0,55; 0,45). Ô X có cost theo từng state là (10; 20). Ô Y có cost (10; 19), tức hai ô chỉ quyết định khác nhau ở x₂.

```text
                    Thật                   Engine                    Sai số
L̄X              15                      0,55·10 + 0,45·20 = 14,5    −0,5  (≈ −3,3%)
L̄Y              14,5                    0,55·10 + 0,45·19 = 14,05   −0,45
Contrast X − Y   0,5                     0,45                         −0,05 (≈ 0,34 pp của C̄)
```

Mức L̄ sai khoảng 3,3%, nhưng contrast chỉ sai khoảng 0,34 pp, tức nhỏ hơn gần 10 lần. Công thức tổng quát:

```text
sai số contrast = Σ_x  e(x) · (c_X(x) − c_Y(x)),   với e(x) = π̃(x) − π(x)
```

Số hạng c_X(x) − c_Y(x) **chỉ khác 0 ở những state mà hai ô quyết định khác nhau**. Phần cost chung khổng lồ (ví dụ J_Stay) triệt tiêu khi trừ.

**Hệ quả:**
- **Không trích dẫn mức L̄ của bản đồ** (E11).
- Contrast của bản đồ tin được ở cỡ 0,2 pp (18 cặp tương đương theo age lệch ≤ 0,201 pp), nhưng vẫn phải kiểm lại bằng native.
- Đây cũng là nguyên lý vì sao paired design và CRN hiệu quả.

---

## 9. Khái niệm 4: dịch có hệ thống và nhãn sát ngưỡng

**Trực giác.** Một nhiệt kế đọc cao 0,1° vẫn đủ để biết "trời nóng". Nhưng nó không đủ để biết "có trên 37,0° hay không".

**Ví dụ.** Điểm XM2S110: pilot cho Ḡ_S = 1,008% (lớp A); native cho 0,970%, tức dưới ngưỡng.

**Định nghĩa.** Nhãn lật khi khoảng cách từ z_pilot tới ngưỡng nhỏ hơn độ dịch từ pilot sang native.

**Dịch ngẫu nhiên khác dịch có hệ thống:**
- **Dịch ngẫu nhiên:** nhãn lật theo cả hai chiều, giống nhiễu.
- **Dịch có hệ thống** (native thấp hơn pilot ở 8/8 điểm): **cả vùng** co lại hoặc nở ra theo một hướng. Với claim dạng "Ḡ_S ≥ 1%" (vùng A), vùng **co lại**, nên hộp vẽ trên nhãn pilot sẽ **đánh giá quá cao** p⁺. Với claim dạng "Ḡ_S ≤ −1%" (gây hại), cùng độ dịch đó làm vùng **nở ra**.

Hướng của độ dịch cho biết claim nào gặp rủi ro, và rủi ro theo chiều nào.

**Định lượng mức phơi nhiễm** (tôi đếm trên số pilot):
- Trong các dòng lớp A với biên độ ±6, có **27/263** dòng có Ḡ_S < 1,136. Chúng sẽ rơi xuống dưới 1% nếu bị dịch đúng bằng mức lớn nhất đã thấy.
- Trong vùng A rộng của plan, **76/428** điểm nằm trong khoảng ±0,171 pp quanh 1%. Con số 0,171 = độ dịch lớn nhất 0,136 + biên R6 khoảng 0,035.

Cảnh báo: con số 0,136 chỉ lấy từ 8 điểm. Phân phối độ dịch thật chưa ai biết, và đó chính là lý do phải gán nhãn lại bằng native.

---

## 10. Khái niệm 5: R1, R6, R5, và "chưa biết" là một nhãn hợp lệ

**Trực giác.** Bạn đo lại bằng một cây thước mịn hơn. Nếu hai lần đo chênh nhau nhiều hơn khoảng cách từ kết quả tới vạch ngưỡng, bạn chưa biết điểm đó nằm phía nào.

**Bốn luật của card v2:**

| Luật | Nội dung |
|---|---|
| **R1** | Chạy ở (640, 4) và hai mức thô hơn bên cạnh là (320, 4) và (640, 2). Chênh lệch lớn nhất giữa các mức gọi là **d**. Đây là chỉ báo độ phân giải số học, **không phải** cận sai số đã được chứng nhận (giới hạn ghi trong DL-101) |
| **R6** | Nếu \|z − ngưỡng\| ≤ d thì gán **UNRESOLVED**, trừ khi kết quả là chính xác |
| **R3** | Với các điểm UNRESOLVED, nâng mức số học (640, 4) → (1280, 4) → (1280, 8), chỉ tính cho những điểm này. Một số điểm có thể được "giải" ở Phase 5, đổi lại tốn thêm compute |
| **R5** | Trong một vùng được chấm, nếu tỉ lệ UNRESOLVED/N_eligible > 1/10 thì verdict là **INCONCLUSIVE**, một nhãn về validity |

**Áp vào XM2S110:** |0,970 − 1| = 0,030 ≤ d = 0,035, nên điểm này là **UNRESOLVED**.

**Vì sao thiết kế như vậy.** Từ chối gán nhãn khi thước không đủ mịn là một cách trung thực: nó ngăn nhiễu số học biến thành bằng chứng. Cái giá phải trả là một hộp ôm sát ngưỡng có nguy cơ ra INCONCLUSIVE dù giả thuyết đúng hay sai.

**Phân biệt hai nhãn:**
- **INCONCLUSIVE:** không đo được. Đây là thông tin về validity.
- **FALSIFY:** đo được, và giả thuyết sai.

**Hệ quả cho L4.5, cần thấy từ bây giờ.** Hiệu ứng ở vùng A nhỏ (trung vị Ḡ_S = 1,53%), nên nhiều điểm của nó nằm gần ngưỡng. Trên số pilot, 17/428 điểm (4%) nằm trong ±0,035 quanh 1%. Native thấp hơn pilot nên tỉ lệ này có thể tăng. Vì vậy card SV **về cấu trúc** có rủi ro WEAKEN hoặc INCONCLUSIVE.

Có thể chọn hộp nằm xa ngưỡng hơn, nhưng việc chọn hộp đó dựa trên dữ liệu discovery cũng là một forking path, và phải ghi lại.

---

## 11. 🔗 Liên hệ với việc bạn từng làm

- **Bạn đã từng làm một phép kiểm mức 3.** Repo cũ có `t01_mdk_des_check.py`, so DES với nghiệm giải tích của M/D/1/K. MASTER PLAN XI.1 gọi nó là "mẫu verification". Đó đúng là "một phương pháp khác cho cùng đáp án".
- **L3R.3 đã audit engine pilot** (MC độc lập, mutant, tái lập) và đã chạy 118 ca calibration native. L4.3 **không làm lại** những việc đó. Nó chỉ thêm hai thứ còn thiếu: provenance riêng của bản đồ, và native chạy trên **vùng của bản đồ**, vốn nằm ngoài frame của card v2.

## 12. Part 1 cho phép nói gì

**Được nói:**
- Contrast của bản đồ đáng tin hơn mức L̄ của nó rất nhiều.
- Độ dịch có hệ thống từ pilot sang native đe dọa các claim dạng "≥ 1%" nhiều nhất.
- UNRESOLVED là một nhãn hợp lệ, và R5 có thể chặn một vùng.

**Không được nói:**
- "Đạt dung sai 0,25 pp nghĩa là nhãn của bản đồ đúng."
- "Engine đúng với mạng thật."
- "Ba mức kiểm đã đủ cho mọi đường code."

## 13. Reviewer có thể hỏi

1. *"Vùng của bạn được vẽ bằng engine nào?"* **Đã trả lời:** bằng nhãn native, khi thực thi xong Part B.
2. *"Có bao nhiêu điểm sẽ lật nhãn dưới engine dùng để chấm?"* **Chưa trả lời:** chờ Part B.
3. *"Sai số cầu phương có làm hỏng contrast không?"* **Đã trả lời** (§8): ảnh hưởng nhỏ, và được giải thích bằng cơ chế trọng số chung.
4. *"Engine native có đúng ở κ/τ = 0,05 không?"* **Chưa trả lời,** có thể cần MC trực tiếp (Part 2).

## 14. ⚠️ Bẫy người mới

1. Coi "đạt dung sai pilot–native" là "nhãn đúng".
2. Coi độ lệch 0,136 pp là nhỏ mà không đặt nó cạnh khoảng cách tới ngưỡng.
3. Trích dẫn mức L̄ của bản đồ.
4. Nghĩ tái lập bit chứng minh code đúng. Nó chỉ chứng minh file không hỏng.
5. Đọc INCONCLUSIVE thành "giả thuyết sai".
6. Chạy native trên một regime CF "chỉ để đo thời gian". Việc này bị **cấm**.

## 15. 🧠 Tư duy researcher

> Không có con số nào "đúng" một cách tuyệt đối. Một con số đúng **ở một mức kiểm**, cho **một câu hỏi**. Hãy hỏi: con số này có thể làm đổi quyết định nào? Chỉ kiểm những con số đó, nhưng kiểm thật kỹ.

## 16. Bài tập hiểu (khuyến nghị)

Lập một bảng nhỏ gồm mọi con số bạn định trích dẫn ở L4.5 (ví dụ: trung vị Ḡ_S của vùng A, tỉ lệ AB theo δ). Với mỗi con số, ghi: nó đang ở **mức đúng** nào (1, 2 hay 3), và nó **cần** mức nào trước khi bạn dựa vào nó.

## 17. Tự kiểm (tùy chọn)

1. Vì sao mức L̄ lệch 0,711% mà contrast không lệch 0,711 pp?
2. Vì sao XM2S110 là UNRESOLVED dù native cho 0,970?
3. Tái lập bit bắt được loại lỗi nào mà đồng thuận số không bắt được, và ngược lại?
4. Native thấp hơn pilot một cách có hệ thống. Hộp của claim "Ḡ_S ≥ 1%" vẽ trên số pilot sẽ sai theo hướng nào? Hộp của claim gây hại thì sao?
5. Vì sao card SV có rủi ro INCONCLUSIVE ngay cả khi vùng A có thật?

## 18. Trạng thái Part 1

- **Hiểu biết cần có:** phạm vi audit theo claim; ba mức đúng và câu hỏi mỗi mức trả lời; cơ chế trọng số chung; độ dịch có hệ thống đe dọa claim nào; R1/R6/R5 và ý nghĩa của UNRESOLVED.
- **Việc nên làm khi thực thi:** chưa có gì. Part 2 sẽ thiết kế các bước chạy.
- **Phụ thuộc khoa học:** L4.5 Part B chỉ nên dùng nhãn native.
- **Có học tiếp được không?** Có. Part 2 biến lý thuyết này thành một thiết kế audit cụ thể: viết dung sai **trước**, chọn vùng ứng viên **trước** khi vẽ hộp, ba kết cục PASS / PASS có giới hạn / HOLD, phân biệt bug với negative result, luật gọn khi nào cần MC trực tiếp, ước lượng compute và code `relabel.py`. Khi muốn, bạn chỉ cần nói "tiếp tục Part 2".