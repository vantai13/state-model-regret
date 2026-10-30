Tôi sẽ đọc ba tài liệu và kéo repo về trước, rồi xác định Lesson đầu tiên của Phase 4 và bắt đầu dạy.

# LESSON 4.1: Đưa regime map vào main như một discovery có địa chỉ

## Part 1/3: Bản đồ là gì, và vì sao phải ghi sổ nó trước khi làm gì khác

### 0. Kiểm nguồn trước khi dạy

Đầu template của bạn ghi "Phase 0, Lesson 0", nhưng cuối tin bạn nói "lesson đầu tiên phase 4". Vì vậy tôi dạy **L4.1** theo `PHASE_4.md` v1.1 (30/10).

Tôi dùng nguồn theo thứ tự ưu tiên: Final Review (Main RQ, KEEP) → các DL và gói v2 đã đóng băng trong repo → PHASE_4.md → MASTER PLAN v1.0 → code. Có ba chỗ bạn cần biết:

1. **Cách đánh số phase đang mâu thuẫn.** Trong MASTER PLAN v1.0, Phase 4 là "controlled core". Bản v1.1 (AI áp ngoài repo) gọi Phase 4 là confirmation. PHASE_4.md đề xuất v1.2: Phase 4 là hợp nhất bản đồ, Phase 5 là confirmation. Chính L4.1 sẽ xử lý chuyện này (DL-103, ở Part 3). Từ giờ đến lúc đó tôi viết "Phase N (tên)" cho khỏi nhầm.
2. **Bảng §0 của MASTER PLAN đã cũ** (vẫn ghi Phase 0, ngày 06/10). Nó chỉ chưa được cập nhật, nội dung không mâu thuẫn.
3. **"Gói kiểm tra" mà PHASE_4.md nói là đi kèm không có ở đâu cả.** Tôi đã tìm `recount_map.py` và `native_probe_summary.csv` trong ba file bạn gửi, trên main và trên nhánh bản đồ. Việc này không cản việc học, nhưng cản Bước 3 khi thực thi. Tôi bàn cách xử lý ở Part 3.

**Những gì tôi đã tự kiểm trên repo,** để các con số trong bài là fact chứ không phải chép lại:
- Giờ commit của các mốc trong timeline.
- Số lớp trên bảng tổng: A 301, B 43, AB 161, J 14, C 334, D 523.
- Số lớp trên lưới đều map1 (raw, 344 điểm): A 21, B 4, AB 7, J 1, C 68, D 243.
- Identity Γ̄ = Ḡ_S|M1 − Ḡ_S khớp tới 4·10⁻¹⁵.
- X2065 đúng là lớp C.

**Những gì tôi chưa kiểm:** bước gộp 1430 → 1376 dòng, các kết quả engine native (K5, K6) và E10.

**Lesson có còn phù hợp không?** Có. Tôi chỉ đề xuất một điều chỉnh về thứ tự dạy. Plan đặt bài phân loại 10 phát biểu ngay trong L4.1. Nhưng muốn xếp một câu vào nhóm "identity" thì phải biết identity là gì, mà plan lại để phần đó sang L4.2. Tôi sẽ chèn một mini-lesson về identity vào Part 2, trước bài phân loại. Nếu không, bài phân loại chỉ còn là đoán đáp án.

**Một quan sát thẳng thắn.** Từ lúc card v1 đóng băng (29/10, 10:17) đến lúc đóng Phase 3R (30/10, 13:57) chỉ khoảng 28 giờ. Trong khoảng đó có 43 commit trên main, cộng toàn bộ bản đồ trên nhánh, phần lớn do AI chạy theo ủy quyền. Điều này không làm dữ liệu sai. Nhưng gần như chắc chắn bạn chưa kịp hiểu hết, và chính PHASE_4.md gọi đây là rủi ro lớn nhất của project (ER3). L4.1 là chỗ tốt để bắt đầu lấy lại quyền sở hữu, vì việc chính của nó là đọc và kể lại.

---

### 1. Bạn đang ở đâu?

```text
Main RQ (KEEP): sửa state vs sửa model — differ? interact? → expected regret
   │
Phase 3R (đóng, Gate NARROW): gói confirmation v2 FROZEN — chỉ kiểm MV và SH
   │      └── nhánh explore: regime map 1376 dòng (DISCOVERY, chưa có record trên main)
   ▼
PHASE 4 — hợp nhất discovery, hoàn tất gói (không tính outcome CF nào)
   L4.1 Re-entry ← BẠN Ở ĐÂY (Part 1/3)
   L4.2 Đọc bản đồ đúng cách
   L4.3 Audit số của bản đồ dưới engine native
   L4.4 Baseline khoa học tối thiểu
   L4.5 Quyết định thêm 0/1/2 card
   L4.6–4.7 (nếu có card) → L4.8 Runner → L4.9 Gate 4
   ▼
PHASE 5 (confirmation): chạy đúng một lần
```

### 2. Lesson này trả lời câu hỏi gì?

> Bản đồ đã thấy chính xác gì, được tạo ra bằng cách nào, và từ nay mình **được** và **không được** dùng nó để nói gì?

| Part | Nội dung | Phần câu hỏi |
|---|---|---|
| **1 (bài này)** | Bản đồ là gì; discovery khác confirmation; vì sao cần record; timeline; số đếm không phải tần suất | "tạo ra bằng cách nào" |
| 2 | Mini-lesson identity → phân loại 10 phát biểu | "đã thấy chính xác gì" |
| 3 | Errata, nhãn provenance, viết record, DL-103, exposure | "không được nói gì" và các bước thực thi |

### 3. Tại sao cần lesson này?

**Ở tầng nghiên cứu,** L4.1 không tạo ra evidence nào. Nó bảo vệ **tư cách** của các claim sau này. Nếu L4.5 sinh ra một card mới từ bản đồ, người đọc cần biết card đó đến từ một cuộc quét thích nghi và được đóng băng trước khi có dữ liệu mới. Không có record thì không ai kiểm được điều đó, kể cả bạn ba tháng sau.

**Ở tầng thực hành,** khi thực thi xong bạn sẽ có trên main: một discovery record, DL-103 và các dòng exposure.

**Nếu bỏ lesson này, những chuyện cụ thể có thể sai:**
- Bạn viết "state repair có ích ở 22% regime" (301/1376). Câu này sai, xem §9.
- Bạn lấy ví dụ X2065 trong REGIME_MAP và kể "hộp MV là vùng model thắng". Thực tế 11/18 điểm discovery trong hộp đó là lớp C.
- Reviewer hỏi "vùng A được chọn khi nào, từ dữ liệu nào?" và bạn chỉ có một file AI viết trên một nhánh chưa merge.

### 4. Liên hệ với Main RQ

```text
L4.1 record ──► lớp A ≈ "differ" (state có giá trị, model không)
            ──► lớp AB với Γ̄ < 0 ≈ "interact" (hai repair thay thế nhau)
                     │
                     ▼
            L4.5: có nên viết thành card ứng viên (SV, SUB)?
                     ▼
            Phase 5: card được kiểm trên điểm MỚI → evidence cho "differ/interact"
```

Liên hệ này **gián tiếp**: L4.1 không trả lời RQ. Nó bảo đảm rằng nếu sau này có câu trả lời, câu trả lời đó không bị nghi là được chọn sau khi đã thấy kết quả.

---

### 5. Prerequisite: đọc được một dòng của bản đồ

Phần này là recap ngắn, vì mọi thứ phía sau đều dựa vào nó.

**5.1 Một episode.** Có một nhóm traffic đang đi trên path A. Lưu lượng của nó là u = 2η đơn vị traffic/s; η là núm điều chỉnh lượng traffic đó. Controller chọn **Stay** (giữ ở A) hoặc **Switch** (chuyển cả nhóm sang B), rồi giữ quyết định suốt horizon h giây. Traffic nền trên mỗi path dao động ON/OFF quanh mức trung bình λ, với biên độ ±6 và capacity μ = 10. Mỗi mode ON hoặc OFF kéo dài cỡ **κ giây**.

Errata E1 sửa đúng chỗ người mới hay đọc nhầm: κ là thời gian một mode kéo dài, không phải tốc độ đổi mode. κ nhỏ nghĩa là mode đổi nhanh.

**5.2 Bốn ô.**

```text
                         M0 (dự báo bằng tải trung bình)   M1 (luật phản ứng thật)
S0 (ảnh cũ: backlog
    τ = 1 s trước,
    không thấy mode)            L̄00                              L̄01
S1 (state thật lúc t0:
    backlog + mode)             L̄10                              L̄11  = C̄_ref
```

- **S1 và M1 đều là repair kiểu oracle**: chúng là mức trần lý tưởng, không phải thứ triển khai được.
- **L̄_sm** là chi phí thật kỳ vọng khi để pipeline (s, m) quyết định. Dấu gạch ngang trên đầu nghĩa là đã lấy trung bình trên mọi snapshot có thể gặp trong regime.
- **Regime** là một bộ tham số vật lý cố định (λA, λB, κ, η, h, τ). Bên trong một regime, snapshot là ngẫu nhiên.

**5.3 Contrast (độ chênh) là hiệu giữa hai ô.** Để dễ tính, tôi dùng số minh họa với L̄11 = 100, nên mọi số đọc thẳng ra % C̄_ref.

| Contrast | Công thức | Ý nghĩa | Regime "kiểu A" | Regime "kiểu C" |
|---|---|---|---|---|
| | | | L̄00 = 103 · L̄10 = 100,5 · L̄01 = 102,8 | L̄00 = 100,3 · L̄10 = 103 · L̄01 = 100,3 |
| Ḡ_S | L̄00 − L̄10 | Giá trị sửa state khi model vẫn là M0 | **2,5** | **−2,7** |
| Ḡ_M | L̄00 − L̄01 | Giá trị sửa model khi state vẫn cũ | **0,2** | 0 |
| Ḡ_SM | L̄00 − L̄11 | Giá trị sửa cả hai | 3,0 | 0,3 |
| Ḡ_S\|M1 | L̄01 − L̄11 | Giá trị sửa state khi model đã đúng | 2,8 | 0,3 |
| Ḡ_M\|S1 | L̄10 − L̄11 | Giá trị sửa model khi state đã đúng | 0,5 | 3,0 |
| Γ̄ | L̄10 + L̄01 − L̄00 − L̄11 | Làm cả hai khác tổng hai phần riêng bao nhiêu | 0,3 | 3,0 |

Ḡ dương nghĩa là repair làm chi phí giảm. Regime "kiểu C" là chỗ phản trực giác: cho M0 biết state tươi lại làm quyết định **tệ hơn** 2,7%. Vì sao chuyện này xảy ra là việc của Part 2.

**5.4 Sáu lớp.** Mỗi regime được gán một lớp, với ngưỡng ±1% C̄_ref. C được xét **trước** mọi lớp khác.

| Lớp | Điều kiện (tóm tắt) | Đọc là |
|---|---|---|
| C | Ḡ_S ≤ −1 | State tươi gây hại khi dùng với M0 |
| A | Ḡ_S ≥ 1, Ḡ_M < 1 | Sửa state đáng, sửa model không đáng |
| B | Ḡ_M ≥ 1, \|Ḡ_S\| < 1 | Ngược lại với A |
| AB | cả hai ≥ 1 | Cả hai đáng; hầu hết thay thế nhau (Γ̄ < 0) |
| J | riêng lẻ < 1, làm cùng nhau ≥ 1 | Nhãn mô tả, không phải "cộng hưởng" |
| D | còn lại | Không đáng kể |

Theo T07 và PHASE_4, mỗi L̄ được engine tính bằng **xấp xỉ số tất định**, không rút episode ngẫu nhiên. Vì vậy một dòng của bản đồ không có nhiễu lấy mẫu. Nó chỉ có **sai số số học**, nên một điểm có Ḡ_S = 1,008 có thể lật sang 0,970 dưới engine khác. Đó là việc của L4.3.

---

### 6. Mental model: discovery và confirmation

**6.1 Ví dụ đời thường.** Một người bắn 50 mũi tên vào vách nhà kho. Sau đó anh ta vẽ cái bia quanh chỗ tên cắm dày nhất, rồi khoe "tôi trúng hồng tâm". Mũi tên nào cũng thật. Cái sai duy nhất là **bia được vẽ sau** (*Texas sharpshooter*).

**6.2 Phiên bản networking.**
- map1 quét 344 tổ hợp và thấy ở góc "h ngắn, κ 0,2–1 s" có vài điểm lớp A.
- map2 dồn 360 điểm vào đúng góc đó.
- Giờ bạn vẽ một hộp quanh vùng dày điểm A và nói "trong hộp này, state thắng".

Nếu kiểm câu đó trên chính các điểm đã dùng để vẽ hộp, kết quả gần như chắc chắn đẹp, vì hộp được vẽ để ôm điểm đẹp. Câu hỏi khoa học thật là: **rút điểm mới trong hộp, đa số có còn là A không?**

**6.3 Khái niệm chính xác.**
- **Discovery (khám phá):** dữ liệu dùng để tìm và định hình giả thuyết. Ở đây được phép đổi phân tích tùy ý. Kết luận được phép là "có candidate pattern".
- **Confirmation (xác nhận):** điểm **mới**, chưa ai thấy, cùng với luật chấm **khóa trước** khi thấy dữ liệu. Kết luận được phép là "pattern đứng trong domain đã khai báo".
- **Pre-registration:** giả thuyết, luật chấm và điều kiện bác bỏ được commit trước khi có dữ liệu. Trong repo của bạn đó là card và `cf_prereg.json`.
- **Garden of forking paths** (Gelman & Loken): mỗi lựa chọn phân tích phụ thuộc vào dữ liệu, dù nhỏ và có lý, đều làm tăng khả năng "thấy" pattern, kể cả khi không ai cố ý.
- **HARKing** (Kerr, 1998): trình bày giả thuyết nghĩ ra sau khi đã thấy kết quả như thể nó có từ trước.

Có một điểm tinh tế. Từng dòng của bản đồ không có nhiễu, vậy forking paths đến từ đâu? Từ ba chỗ:
1. Hộp được vẽ quanh những điểm đã biết là đẹp, trong khi claim nói về **mọi** điểm trong hộp.
2. Ngưỡng 1%, thứ tự xét lớp và trục tọa độ đều được chọn sau khi thấy dữ liệu. K9b cho thấy nếu vẽ theo trục (λA, λB) thì hai lớp ngược dấu AB và C bị trộn vào nhau; vẽ theo δ = λB − λA thì chúng tách ra.
3. Sai số số học đẩy các điểm sát ngưỡng qua lại giữa hai lớp.

**6.4 Bản đồ là một discovery rất "đậm".**

| Đặc điểm | Thực tế | Hệ quả |
|---|---|---|
| Không có gì viết trước | REGIME_MAP ghi rõ: "không cần viết trước hay dự đoán" | Không phát biểu nào của bản đồ là prediction; tất cả là quan sát |
| Lấy mẫu thích nghi | map2 chọn sau map1 và dồn vào A/AB; age và amp được thêm sau | Số đếm phản ánh chỗ đã nhìn (§9) |
| AI thiết kế, chạy và tự đánh giá | Ghi là "theo ủy quyền" | Mục "cái gì thật sự mới" là đánh giá của AI, cần bạn kiểm lại |
| Dùng engine pilot | K = 40, dt = 1/120 s, khác engine sẽ chấm confirmation | Nhãn sát ngưỡng 1% có thể lật |
| Có sự cố khi chạy | Một lệnh bạn đã từ chối vẫn chạy song song; hai tiến trình ghi chung một thư mục; WSL khởi động lại | Sự cố là lý do để **kiểm tái lập**, không tự động là lý do vứt dữ liệu. PHASE_4 báo đã tái lập trùng bit 6 dòng (K2); tôi chưa tự chạy lại |

**6.5 Discovery không phải đồ bỏ đi.** Chính card v1 sinh ra từ pilot discovery. Trình tự đúng là discovery → đóng băng → confirmation. Một discovery được ghi chép trung thực, kể cả sự cố, là tài sản. Một discovery không được ghi lại là món nợ.

---

### 7. Discovery record làm được gì mà REGIME_MAP không làm được?

| | REGIME_MAP.md | Record trên main |
|---|---|---|
| Ở đâu | Nhánh explore, chưa merge | Main, nơi mọi quyết định khoa học tham chiếu tới |
| Ai viết | AI theo ủy quyền | Bạn (AI có thể soạn khung) |
| Số lấy từ đâu | AI tự tóm tắt | Script đếm lại từ raw |
| Mục "không được nói gì" | Có rải rác | Bắt buộc, do bạn viết |
| Errata | E1–E8 | E1–E14, chỉ ghi thêm, không sửa cũ |

Chức năng quan trọng nhất của record là: **thời điểm commit là bằng chứng.** Repo của bạn không đăng ký trước trên website nào. Thứ chứng minh "tôi chưa nhìn trước" là thứ tự commit.

Khi record được commit trước mọi phân tích mới (audit native, tính hộp, baseline), nó đóng dấu "đây là tất cả những gì tôi biết lúc này". Mọi phân tích sau đó hiện rõ trong git là làm thêm sau. Đó là lý do plan bắt record đi trước L4.3 Part B và L4.5.

**Vì sao không merge nhánh?** Main chứa những gì thuộc pipeline đã khóa. Merge sẽ đưa code exploration (bản sao `queue_D` có thêm age/amp) vào main như thể nó là một phần của contract. Thay vào đó, tag là một địa chỉ bất biến và record trỏ tới tag. Pilot cũng đã được xử lý đúng như vậy.

---

### 8. Timeline: cái gì có thể đã ảnh hưởng cái gì?

Giờ commit lấy từ git. Hai mốc bắt đầu chạy map1 và map3age lấy theo REGIME_MAP.

```text
28/10 19:21  pilot 216 regime              [discovery #1 — đã có record trên main]
29/10 10:17  CARD v1 ĐÓNG BĂNG             ← vùng MV, SH chọn từ pilot
29/10 22:37  map1 bắt đầu                  (theo REGIME_MAP)
30/10 00:11  map3age bắt đầu; map2 chạy tiếp, có sự cố chạy song song
30/10 08:12  commit bản đồ (050b419)
30/10 11:01  errata E1–E8 (574a36f)
30/10 12:28  CARD v2 = v1, chỉ đổi bước làm tròn thành 1/100
30/10 13:24  rút 270 CF (chỉ tham số, 0 outcome)
30/10 13:57  đóng Phase 3R
```

Ảnh hưởng chỉ đi xuôi thời gian. Nhưng phải tách **hai rủi ro khác nhau**:

**Rủi ro 1: nhiễm thiết kế** (giả thuyết được chọn sau khi thấy dữ liệu). Card v2 được commit sau bản đồ, nhưng vùng của nó giữ nguyên từng byte so với v1, mà v1 có trước map1 12 giờ. Vì vậy **vùng card v2 không thể được chọn nhờ bản đồ.**

**Rủi ro 2: lộ dữ liệu, tức exposure** (điểm dùng để kiểm đã có người nhìn outcome). Errata E3: khi quy về age 1, có 10 điểm của map3age rơi vào hộp của card MV, một phần nằm trong vùng đối chứng Ω⁻. Vùng đó không còn hoàn toàn "chưa ai thấy". Repo xử lý bằng inventory v3: một danh sách mọi tọa độ đã lộ, kể cả của bản đồ. 270 CF được rút **sau đó** và tránh các tọa độ này.

Hai rủi ro này chữa bằng hai cách khác nhau. Rủi ro 1 chữa bằng **thứ tự commit**. Rủi ro 2 chữa bằng **điểm mới cộng với sổ exposure**.

**Hệ quả cho Phase 4:** mọi card v3 sinh ra từ bản đồ đều mang rủi ro 1 ngay từ thiết kế. Với discovery, điều đó là bình thường. Card đó chỉ có giá trị nếu được đóng băng **trước** khi rút bộ CF mới của chính nó (luật vàng thứ 3).

---

### 9. Số đếm lớp không phải tần suất

Tôi đã đếm lại hai con số:
- Bảng tổng: lớp A có 301/1376 ≈ 22%.
- Lưới đều map1: lớp A có 21/344 ≈ 6%.

Chênh nhau gần 4 lần vì map2 cố ý dồn 576 điểm vào vùng A và AB. Giống như đo "bao nhiêu % link bị nghẽn" mà đặt phần lớn probe vào những link bạn đã nghi là nghẽn.

**Tầng bẫy thứ hai:** ngay cả 21/344 cũng **không phải tần suất**. Đó là tỉ lệ trên một lưới mà khoảng và bước do người thiết kế chọn (κ ∈ {0,1; 0,3; 1; 3}, λB từ 6 đến 8,5…). Đổi lưới thì tỉ lệ đổi. Và không có phân phối regime ngoài đời nào gắn với lưới này: realism đang ở trạng thái UNSOURCED (DL-098).

Vì vậy dạng câu duy nhất được phép là: *"Lớp A tồn tại và tụ ở vùng X; trong lưới map1, 21/344 điểm là A."* Không được nói "A phổ biến" hay "A hiếm".

---

### 10. 🔗 Liên hệ với việc bạn từng làm

- **Pilot (28/10)** đã đi qua đúng quy trình này: `PHASE_3R_discovery_record.md` có provenance, một mục "đọc mọi tỉ lệ qua thiết kế lấy mẫu", và errata E1–E7 chỉ ghi thêm. Ví dụ E1 sửa "79/216" thành 80/216 theo ID, 78/210 theo regime phân biệt. **L4.1 là cuốn sổ thứ hai, cùng khuôn với cuốn thứ nhất.**
- **Repo cũ `dt4n-decision-risk-project`:** MASTER PLAN IX.1 ghi lại rằng *GO switch v1* đã dùng lại seed test sau khi phân tích trên chính chúng, và báo cáo đó tự nhận không phải xác nhận độc lập. Đó chính là bẫy "kiểm hộp trên điểm đã dùng để vẽ hộp". Hồi đó bạn chữa bằng cách ghi chú lại. Bây giờ cấu trúc repo chặn bẫy này từ thiết kế: có inventory, và CF được rút sau khi đóng băng.
- Công việc static threshold trong repo cũ sẽ quay lại ở L4.4, vì một margin cho controller về bản chất là một ngưỡng tĩnh. Lúc này chưa cần đào sâu.

---

### 11. Part 1 cho phép nói gì

**Được nói:**
- Bản đồ là discovery thích nghi, do AI thiết kế và chạy.
- Vùng card v2 không thể được chọn nhờ bản đồ.
- Một phần vùng đối chứng của MV đã bị lộ.
- Số đếm lớp mô tả mẫu, không phải tần suất.

**Không được nói:**
- "Vùng A đã được chứng minh."
- "22% regime có state thắng."
- "Card v2 hoàn toàn không bị bản đồ ảnh hưởng." Câu này mơ hồ; phải nói rõ ảnh hưởng ở thiết kế hay ở exposure.
- "Sự cố khi chạy làm dữ liệu vô giá trị."

### 12. Reviewer có thể hỏi

1. *"Vùng A được tìm bằng quét thích nghi. Sao biết nó không phải hệ quả của việc vẽ hộp quanh điểm đẹp?"* Part 1 trả lời: **chưa biết**. Chỉ Phase 5, trên điểm mới, mới trả lời được.
2. *"Ai thiết kế bản đồ, và claim được viết trước hay sau dữ liệu?"* Timeline cộng record trả lời được câu này.
3. *"Hiện tượng này gặp thường đến đâu?"* Chỉ trả lời được "trong lưới X". Ngoài đời thì UNSOURCED.
4. *"Số liệu của bản đồ có cùng engine với engine chấm không?"* Chưa. Đây là việc của L4.3.

### 13. ⚠️ Bẫy người mới

1. Thấy card v2 commit sau bản đồ rồi kết luận card v2 bị nhiễm. Sai: vùng của nó giữ nguyên từng byte so với v1.
2. Bẫy ngược lại: kết luận "không có gì của card bị lộ". Sai: errata E3.
3. Đọc 301, hay cả 21/344, như tần suất.
4. Đọc κ là tốc độ đổi mode (E1).
5. Chép mục "Cái gì thật sự mới" của REGIME_MAP vào record như kết luận của chính bạn. Đó là đánh giá của AI.
6. Vứt dữ liệu vì sự cố khi chạy, hoặc lờ sự cố đi. Cách đúng: sự cố → kiểm tái lập.

### 14. 🧠 Tư duy researcher cần học ở đây

> Trước khi hỏi *"kết quả nói gì?"*, hãy hỏi *"kết quả này được tạo ra bằng quy trình nào, và chính quy trình đó có thể tự sinh ra pattern này không?"*

Thứ tự thời gian của hiểu biết, tức ai biết gì và lúc nào, là một phần của bằng chứng.

### 15. Bài tập hiểu (khuyến nghị, không cần gửi lại)

- **(a)** Viết timeline 8 dòng mà không nhìn tài liệu. Thêm một cột: *"mốc này có thể ảnh hưởng tới mốc nào sau nó, và qua rủi ro 1 hay rủi ro 2?"*
- **(b)** Viết ba câu *"Bản đồ KHÔNG cho phép tôi nói…"* bằng lời của bạn. Chúng sẽ thành mục (8) của record ở Part 3.

### 16. Tự kiểm (tùy chọn)

1. Discovery khác confirmation ở hai điểm nào?
2. Từng dòng của bản đồ không có nhiễu lấy mẫu, vậy vì sao forking paths vẫn là vấn đề?
3. Giả sử map2 dồn 576 điểm vào lớp C thay vì A/AB. Con số 301 và 334 đổi thế nào? Cái gì **không** đổi?
4. Card v2 an toàn với rủi ro nào, và không an toàn với rủi ro nào?
5. Reviewer nói: *"Lớp A chỉ có 21/344, hiện tượng hiếm, không đáng quan tâm."* Câu này sai ở đâu?

### 17. Trạng thái Part 1

- **Hiểu biết cần có sau bài này:** đọc được một dòng của bản đồ (bốn ô, sáu contrast, lớp); phân biệt discovery với confirmation; tách được nhiễm thiết kế với exposure; giải thích được vì sao số đếm lớp không phải tần suất.
- **Việc nên làm khi thực thi:** Part 1 chưa có gì để chạy, ngoài bài timeline.
- **Phụ thuộc khoa học:** khi thực thi thật, record, DL-103 và dòng exposure phải được commit **trước** L4.3 Part B và L4.5.
- **Có học tiếp được không?** Có. Part 2 (mini-lesson identity và phân loại 10 phát biểu) là phần cốt lõi về trí tuệ của L4.1. Khi muốn học tiếp, bạn chỉ cần nói "tiếp tục Part 2".