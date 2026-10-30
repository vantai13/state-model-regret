# LESSON 4.5: Từ bản đồ đến claim ứng viên — thêm 0, 1 hay 2 card?

## Part 1/2: Câu hỏi của bạn còn thiếu gì, và ứng viên nào đáng xét?

### 0. Kiểm nguồn và điều chỉnh plan

L4.5 khớp với trạng thái hiện tại. Quyết định thêm 0, 1 hay 2 card là quyết định #2 mà DL-103 dành cho bạn.

**Tình trạng hai track:**
- **Part A** (ba bộ lọc định tính: identity, prior, giá trị cho RQ) **làm được ngay**, vì không cần số native nào. Kết quả của Part A sẽ quyết định HOLD ở κ/τ = 0,05 còn quan trọng hay không.
- **Part B** (sàng khả thi) **đang bị chặn** bởi hai thứ: L4.3 chưa có nhãn native (đang HOLD), và L4.4 chưa có kết quả baseline.

**Những gì tôi đã kiểm:**
- Bảng power của plan được tái tạo **khớp** bằng chính hàm `power.pass_power` và `verdict.plus_power` của repo. Với n = 60, cần ít nhất 39 MEETS ở Ω⁺ và tối đa 21 ở Ω⁻.
- Tôi đã đọc các dòng prior liên quan trong `prior_boundary.md`, `already_implied.md` và `freshness_decision_value.md`. Lưu ý: đây là ghi chú do AI đọc paper (nhãn AI-T). Cột "tác giả chấm" trong các file đó **vẫn còn trống**, và tôi không đối chiếu lại với bản gốc của paper.

**Hai điều chỉnh tôi đề xuất:**

1. **Về phần "differ".** Plan ghi rằng phần còn thiếu là "không có vùng nào mà sửa state có ích". Tôi đề xuất nói chính xác hơn: gói v2 **đã** cho thấy hai repair khác nhau (sửa model có ích ở vùng này, sửa state gây hại ở vùng kia). Cái còn thiếu là một **phân ly kép** (double dissociation), giải thích ở §6. Cách nhìn này cho thấy chính xác SV đáng giá ở đâu.
2. **Về sàng khả thi.** Nên tính cả **numerics coverage** vào bộ lọc khả thi. Lý do là HOLD ở κ/τ = 0,05 nằm ngay trong vùng của ứng viên SUB. Cần phân biệt hai việc: loại một vùng vì **không đo được** (một vấn đề validity) thì hợp lệ; loại một vùng vì **kết quả xấu** (outcome) thì không.

**Map của L4.5:**

| Part | Nội dung | Khái niệm trong plan |
|---|---|---|
| **1 (bài này)** | Kiểm độ phủ RQ; premise đã đổi; ba bộ lọc định tính áp lên mọi ứng viên | 1, 2, 3 (bộ lọc 1–3) |
| 2 | Khả thi (p⁺ trung thực, power, R5); baseline; multiplicity; "0 card" cũng là một kết quả; các phương án và hệ quả; DL và forking log | 3 (bộ lọc 4–5), 4, 5, 6 |

---

### 1. Bạn đang ở đâu?

```text
PHASE 4
  L4.1 ✓  L4.2 ✓  L4.3 ✓ (thực thi: HOLD)  L4.4 ✓ (học xong; spec chưa viết)
  L4.5 Quyết định card ← BẠN Ở ĐÂY (Part 1/2)     ← quyết định #2 của bạn
        ├── 0 card ──────────────► L4.8 Runner
        └── ≥1 card ─► L4.6 card set v3 ─► L4.7 gói CF-v3 ─► L4.8
```

### 2. Câu hỏi của L4.5

> Lần confirmation **duy nhất** sẽ kiểm thêm điều gì ngoài MV và SH, nếu có? Và vì sao?

### 3. Tại sao cần?

Đây là lesson **đầu tiên** của Phase 4 quyết định trực tiếp Main RQ sẽ nhận được evidence gì. Có năm rủi ro cụ thể:

1. **Multiplicity:** thử nhiều claim, nhiều hộp, thì khả năng "có ít nhất một PASS" do may mắn tăng lên.
2. **Claim chỉ tái hiện identity:** nó PASS chắc chắn nhưng không kiểm được gì.
3. **Claim trùng với prior:** PASS nhưng không tạo ra tri thức mới.
4. **Card thiếu power:** ra INCONCLUSIVE, và lần confirmation duy nhất bị lãng phí.
5. **Lạc quan hậu nghiệm:** hộp được vẽ quanh những điểm đẹp, nên tỉ lệ thật trên điểm mới thấp hơn.

### 4. Liên hệ với Main RQ

```text
"how ... differ"   ──► MV, SH (đã có)  + SV? ──► phân ly kép
"and interact"     ──► Γ̄ chỉ diagnostic + SUB? ──► interaction không bị identity ép
"expected regret"  ──► mọi card dùng Ḡ/C̄_ref (đã đúng)
```

Liên hệ này **trực tiếp**: mỗi card thêm vào là một câu Phase 5 có thể nói về RQ.

### 5. Prerequisite

- L4.1 Part 2: identity và cây phân loại bốn hộp.
- L4.2: cận Γ̄ ≥ −min(Ḡ_S, Ḡ_M) và ba hệ quả của nó; ba toy; vai trò của δ.
- L4.3: nhãn native, UNRESOLVED, HOLD.
- L4.4: baseline có margin; toy T-AB cho thấy margin có thể lấy lại toàn bộ giá trị của sửa model.

---

## 6. Khái niệm 1: kiểm độ phủ RQ, và phân ly kép

**Trực giác.** Đề thi có ba câu, nhưng bạn mới chuẩn bị lời giải cho một câu rưỡi.

**Bảng độ phủ** (dựa trên plan, tôi sửa dòng "differ"):

| Phần của Main RQ | Gói v2 kiểm gì | Nếu v2 PASS, bạn được nói | Còn thiếu |
|---|---|---|---|
| **differ** | MV: Ḡ_M ≥ 1% ở Ω_MV⁺. SH: Ḡ_S ≤ −1% ở Ω_SH⁺ | Có vùng sửa model có ích; có vùng sửa state (dưới M0) gây hại | **Phân ly kép:** chưa có vùng nào mà sửa *state* là repair có giá trị trong khi sửa model thì không |
| **interact** | Không có card; Γ̄ chỉ là chẩn đoán | Trong vùng harm, Γ̄ > 0. Nhưng đó là S12 | **Không có phép kiểm interaction nào không bị identity ép** |
| expected regret | Cả hai card dùng Ḡ/C̄_ref | Đúng đơn vị của câu hỏi | — |

### Phân ly kép (double dissociation)

**Trực giác.** Có hai chìa khóa và hai ổ khóa. Chỉ chứng minh "chìa X mở ổ 1" thì chưa nói được hai chìa khác nhau, vì có thể chìa Y cũng mở được ổ 1. Phải chứng minh thêm "chìa Y mở ổ 2, còn chìa X thì không" mới thấy rõ mỗi chìa có vai trò riêng.

**Trong RQ của bạn:**
- **Vùng MV:** sửa model có ích, còn sửa state thì không. Thực tế, trong MV+A có 11/18 điểm sửa state còn gây hại.
- **Vùng SV (ứng viên):** sửa state có ích, còn sửa model gần như không.

Có cả hai vùng thì "differ" được trả lời ở dạng mạnh nhất. Chỉ có MV cộng SH thì mới là "một repair giúp ở đây, repair kia hại ở chỗ khác", tức thiếu hẳn nửa cho thấy state có vai trò riêng. **Đây chính là giá trị của SV đối với RQ.**

**Luật:** một card mới chỉ đáng thêm khi nó lấp được một dòng trong cột "còn thiếu".

---

## 7. Khái niệm 2: premise đã đổi

**Trực giác.** Hôm qua bạn quyết không mang ô vì dự báo chỉ 3% mưa. Sáng nay dự báo là 60%. Quyết định hôm qua không sai vào lúc đó, nhưng nên xem lại **trước khi ra khỏi nhà**.

**Trong project.** Ở L3R.6 (DL-073), bạn không cấp suất cho một card về interaction, vì discovery lúc đó chỉ có 3/162 cấu hình có cả hai contrast đủ lớn. Lý do: muốn có substitution ≥ 1% thì cả Ḡ_S lẫn Ḡ_M đều phải ≥ 1% (hệ quả 1 của cận Γ̄). Bản đồ bây giờ có 161 cấu hình AB.

**Luật xem lại một DL:**
- Premise đổi **trước** khi có dữ liệu kiểm, thì được xem lại.
- Premise đổi **sau** khi có dữ liệu kiểm, thì không được dùng để sửa một thiết kế đã chạy.

Hiện tại chưa có outcome CF nào, nên việc xem lại là hợp lệ.

**Cần nói đúng về con số.** "161" đến từ map2, đợt cố ý dồn mẫu vào vùng AB. Vì vậy nó **không** phải tần suất. Premise thật sự đổi ở câu hỏi **tồn tại**: có một vùng kiểm được, nơi substitution ≥ 1% là khả dĩ. Câu trả lời là có. Ở dải δ ∈ [0,25; 0,5], 94,9% điểm lưới là AB với Γ̄ ≤ −1% (theo số pilot). DL quyết định của bạn phải trích DL-073 và nói rõ **premise nào** đã đổi.

---

## 8. Khái niệm 3: ba bộ lọc định tính, áp lên mọi ứng viên

Thứ tự lọc nên theo chi phí, rẻ trước đắt sau:
1. **Identity**: làm trên giấy.
2. **Prior**: đọc lại ghi chú.
3. **Giá trị cho RQ**: làm trên giấy.

Sau đó mới tới **baseline** và **khả thi**, hai bộ lọc cần số native (Part 2).

### 8.1 Ứng viên SV: "ở Ω_SV⁺, đa số regime có Ḡ_S ≥ 1%"

| Bộ lọc | Đánh giá | Ghi chú |
|---|---|---|
| **Identity** | Không bị ép. Ḡ_S tự do về dấu | Ω⁻ (lật κ sang các mode kéo dài) có thể thất bại thật, nên dùng được **thiết kế hai vùng** |
| **Prior** | Đánh giá độ tươi của thông tin theo chi phí quyết định ở phía sau **đã được biết** (K-S9/K-F1, qua S11; stale link state qua P04) | Phần mới chỉ có thể là **ở đâu và bao nhiêu** trong rerouting làm đổi tải, **đặt cạnh MV** với cùng estimand. **Không được nói:** "thông tin tươi có giá trị quyết định" như một phát hiện |
| **Giá trị cho RQ** | Hoàn thiện phân ly kép cho "differ" | Đây là claim state value dương **duy nhất** có thể có |
| *Khả thi (sơ bộ, chờ Part 2)* | Đáng lo | Hiệu ứng nhỏ (trung vị pilot 1,53%), sát ngưỡng, và native thấp hơn pilot một cách có hệ thống |

### 8.2 Ứng viên SUB: "ở Ω_SUB⁺ (trong dải δ), đa số regime có Γ̄ ≤ −1%"

| Bộ lọc | Đánh giá | Ghi chú |
|---|---|---|
| **Identity** | Tiêu chí không bị ép, nhưng **kéo theo** Ḡ_S ≥ 1% và Ḡ_M ≥ 1% (hệ quả 1). Đối chứng hai vùng thì bị ép | Phải dùng **thiết kế một vùng** (`gamma_verdict`). Nội dung kiểm được là "Ḡ_S\|M1 nhỏ so với Ḡ_S" |
| **Prior** | Theo dòng PC3 của `prior_boundary.md`: WM26 có một bảng 2×2 sửa hai nguồn lỗi, báo các hiệu riêng lẻ nhưng **không thấy** contrast interaction trong các trang đã đọc. Hai repair của WM26 dùng **tương lai thật** (oracle biết trước tương lai). R02 cho thấy thông tin có thể làm hại một policy xấp xỉ; R04 nêu điều kiện để không hại | Khác ở ba trục: **E** (estimand: interaction với oracle không biết tương lai), **M** (phép can thiệp: lộ state ẩn hiện tại × biểu diễn đúng randomness), **R** (regime: một quyết định làm đổi tải). ⚠️ Đây là ghi chú AI-T, tác giả **chưa chấm** |
| **Giá trị cho RQ** | Phép kiểm interaction **không bị identity ép duy nhất** | Lấp đúng dòng "interact" |
| *Khả thi và baseline (sơ bộ)* | Hiệu ứng lớn, nhưng có ba rủi ro | (i) δ được tìm ra sau khi nhìn dữ liệu. (ii) Vùng chứa κ/τ = 0,05, đúng chỗ đang HOLD. (iii) Toy T-AB ở L4.4 cho thấy margin có thể lấy lại toàn bộ giá trị của sửa model. Nếu điều đó xảy ra trên plant, SUB chỉ còn nói được "hai repair cùng chữa một lỗi mà một margin cũng chữa được" |

### 8.3 Các ứng viên khác

| Ứng viên | Plan gợi ý | Ý kiến của tôi |
|---|---|---|
| **MD** (lớp B: Ḡ_M ≥ 1%, \|Ḡ_S\| < 1%) | Không | Đồng ý. Phần lớn trùng MV; tiêu chí kép cần code mới |
| **J** ("cộng hưởng") | Loại | Đồng ý. 8/14 điểm bị S12 ép; cái tên gợi ý một cơ chế chưa hề có |
| **AMP** (biên độ) | Loại, chuyển Phase 7 | Đồng ý. Đây là plant khác (L4.2) |
| **AGE** | Loại | Đồng ý. Age chỉ là đổi thang thời gian, và kết quả đã được kỳ vọng |
| **X** ("không repair nào luôn thắng") | Không làm card riêng | Đồng ý. Câu này chỉ có nghĩa khi SV đặt cạnh MV, tức chính là phân ly kép |
| **δ** (dấu của Ḡ_S đổi theo δ) | Ghi lại cho Phase 6 | Đồng ý. Đây là cơ chế (RQ2), cần can thiệp có kiểm soát, cộng thêm vấn đề đồng tuyến với headroom ratio (L4.2) |

Cột "Bạn quyết" là của bạn. Bảng trên chỉ là gợi ý để bạn phản biện.

---

## 9. 🔗 Liên hệ với việc bạn từng làm

- **L3R.6 và DL-073.** Bạn (qua ủy quyền) đã chọn "phương án D", không cấp suất cho interaction. L4.5 là lần xem lại quyết định đó một cách hợp lệ, trước khi có dữ liệu.
- **Phase 2.** Bảng prior boundary có cột "⟨tác giả chấm⟩" vẫn còn trống. Những ô trống ấy giờ trở thành điều kiện cho bộ lọc prior: muốn giữ SUB, dòng PC3 cần được chính bạn chấm.
- **Repo cũ** từng có `novelty_matrix.xlsx` (đã archive). Bài học khác biệt: novelty bây giờ được đánh giá theo ba trục E/M/R so với nguồn **gần nhất**, chứ không theo số ô trống trong một ma trận.

## 10. Part 1 cho phép nói gì

**Được nói:**
- Gói v2 chưa có phân ly kép, và chưa có phép kiểm interaction nào không bị ép.
- SV và SUB là hai ứng viên duy nhất qua được ba bộ lọc định tính, nếu bạn đồng ý với các đánh giá ở §8.
- Premise của DL-073 đã đổi ở câu hỏi **tồn tại**, không phải tần suất.

**Không được nói:**
- "SV/SUB mới." Prior chưa được tác giả chấm.
- "SUB khả thi." Chưa có nhãn native và chưa có baseline.
- "161 cấu hình AB cho thấy substitution phổ biến."

## 11. Reviewer có thể hỏi

1. *"Vì sao thêm claim sau khi đã có một gói confirmation?"* **Đã trả lời:** premise đổi trước khi có dữ liệu kiểm, và claim mới thuộc một family riêng, khai trước.
2. *"Substitution có phải hệ quả hiển nhiên khi cả hai repair cùng sửa một lỗi không?"* **Trả lời được một phần:** hệ quả 1 là đại số; phần kiểm được là "Ḡ_S|M1 nhỏ"; còn khả năng margin giải thích được thì phải chờ L4.4.
3. *"Giá trị của thông tin tươi đã được biết từ lâu?"* **Đã trả lời:** đúng; SV chỉ có thể mới ở "ở đâu, bao nhiêu, cạnh MV".
4. *"Vì sao không có card cho δ?"* **Đã trả lời:** đó là cơ chế, để Phase 6.

## 12. ⚠️ Bẫy người mới

1. Bỏ qua bộ lọc prior với lý do "chưa thấy ai làm".
2. Coi 161 là bằng chứng tần suất.
3. Cho rằng "differ" chưa được kiểm chút nào. Thực ra nó đã được kiểm một nửa.
4. Thiết kế SUB với vùng đối chứng lật κ (bị ép).
5. Coi SV là "dễ" vì ai cũng tin thông tin tươi có ích. Thực tế, hiệu ứng nhỏ cộng sát ngưỡng làm SV khó kiểm.
6. Quyết định 0/1/2 card ngay bây giờ, khi chưa có nhãn native và baseline.

## 13. 🧠 Tư duy researcher

> Trước khi hỏi "còn kiểm được thêm gì?", hãy hỏi "câu hỏi của mình còn thiếu phần nào?". Chỉ thêm phép kiểm để lấp chỗ thiếu. Mọi phép kiểm thêm khác chỉ làm tăng multiplicity.

## 14. Bài tập hiểu (khuyến nghị)

Đây là phần làm được ngay, không cần compute:

- Viết bảng độ phủ RQ (§6) bằng lời của bạn.
- Đọc dòng PC3 trong `prior_boundary.md` và các dòng K-F/K-S trong `freshness_decision_value.md`. Với mỗi ứng viên SV và SUB, viết ba dòng: "đã biết gần nhất", "khác ở trục nào", "câu không được nói".
- Điền cột "Bạn quyết" cho bộ lọc 1–3.

Nếu sau bước này SUB bị loại vì prior, HOLD ở κ/τ = 0,05 không còn chặn claim nào. Nếu SUB sống, bạn biết cần xử lý numerics ở đó.

## 15. Tự kiểm (tùy chọn)

1. Phần nào của Main RQ mà gói v2 kiểm chưa trọn, và vì sao?
2. Phân ly kép là gì? Vì sao MV cộng SH chưa phải phân ly kép?
3. Premise nào của DL-073 đã đổi? Vì sao "161" không phải là premise đúng để trích dẫn?
4. Vì sao SUB bắt buộc dùng thiết kế một vùng, còn SV thì có thể dùng hai vùng?
5. Loại một vùng vì numerics HOLD khác gì với loại một vùng vì kết quả xấu?

## 16. Trạng thái Part 1

- **Hiểu biết cần có:** bảng độ phủ và khái niệm phân ly kép; luật xem lại premise; cách áp ba bộ lọc định tính cho SV và SUB, và vì sao các ứng viên khác bị loại.
- **Việc nên làm khi thực thi:** Part A của L4.5. Đây là bước rẻ nhất có thể quyết định số phận của HOLD ở L4.3.
- **Phụ thuộc khoa học:** Part B (sàng khả thi) cần nhãn native từ L4.3 và kết quả từ L4.4. DL quyết định phải có trước L4.6.
- **Có học tiếp được không?** Có. Part 2 gồm: vì sao p̂ trên discovery luôn lạc quan và luật "trừ 0,10"; cách đọc bảng power (với p⁺ = 0,6, ba trên bốn lần bạn sẽ **không** PASS dù hiện tượng có thật); vì sao tỉ lệ UNRESOLVED phải ≤ 5%; family F2 và FWER; vì sao "0 card" là một kết quả hợp lệ; các phương án 0/1/2 card và hệ quả của từng phương án, kèm khuyến nghị có điều kiện của tôi. Khi muốn, bạn chỉ cần nói "tiếp tục Part 2".