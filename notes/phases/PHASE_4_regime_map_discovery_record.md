# Phase 4 (hợp nhất discovery) — Record của regime map, L4.1

Người phụ trách: **Doan Van Tai** · 30/10/2026.
Nhãn: **DISCOVERY / AI theo ủy quyền**. Không phải confirmation, contract, novelty
hay bằng chứng xác nhận RQ; G-level giữ **G1**. AI soạn và chạy recount theo yêu cầu
triển khai ba phần lesson; chưa có xác nhận tác giả tự kiểm hoặc tự viết mục 8.

Số đo trong record lấy từ [recount.json](../../results/P4_01_recount/20261030_01/recount.json),
sinh bởi [recount_map.py](../../experiments/P4_01_recount/recount_map.py).
[Manifest](../../results/P4_01_recount/20261030_01/manifest.json) ghi SHA256 raw, code,
cấu hình và output. Đơn vị contrast: **% C̄ref**, chênh giữa hai giá trị này: **pp**.
Mọi đánh giá/phân loại dưới đây mang provenance **AI soạn, tác giả chưa kiểm**,
trừ quyết định numbering được tác giả chọn riêng tại DL-103.

## 1. Provenance và timeline

- Nhánh nguồn: `explore/v13-regime-map`; annotated tag `explore-v13-regime-map`
  → **574a36fb4213a79d3d2aa305a489701cfc3059f2**. Không merge, không di chuyển tag.
- REGIME_MAP nguyên bản giữ nguyên tại tag; [snapshot byte gốc](../../results/lessons/l4_1/inputs/REGIME_MAP_at_tag.md)
  có hash trong [input manifest](../../results/lessons/l4_1/input_manifest.json).
  Attribution Claude và mọi lịch sử đã có được giữ nguyên.
- Khám phá ban đầu do AI thiết kế, chạy, viết theo ủy quyền; không có prereg và
  không có prediction trước kết quả. Bản recount hiện tại cũng là AI theo ủy quyền.
- Ba [input lesson](../../results/lessons/l4_1/inputs/part1.md) được lưu cùng
  [Part 2](../../results/lessons/l4_1/inputs/part2.md) và [Part 3](../../results/lessons/l4_1/inputs/part3.md).
  Không tìm thấy `PHASE_4.md` v1.1 hoặc gói `native_probe_summary.csv`; không tự
  nhận đã đọc/áp các phần không được cung cấp.

| Mốc | Thời điểm +07 | Nguồn / giới hạn |
|---|---|---|
| Pilot discovery | 28/10 19:21 | `a7435e9` |
| Card v1 frozen | 29/10 10:17 | `1414d92` |
| map1 bắt đầu | 29/10 22:37 | REGIME_MAP ghi lại; không phải run receipt mới |
| map3age bắt đầu | 30/10 00:11 | REGIME_MAP ghi lại |
| Bản đồ đầu tiên | 30/10 08:12 | `050b419` |
| Errata E1–E8 | 30/10 11:01 | `574a36f` |
| Card v2 | 30/10 12:28 | `b62f329`; vùng/claim giữ từ v1, chỉ bước làm tròn đổi |
| Rút CF, chỉ tham số | 30/10 13:24 | `7173d70`; 270 điểm |
| Phase 3R closeout | 30/10 13:57 | `8ba161b`, Gate 3R NARROW |

Thứ tự card v1 trước map loại trừ việc **chọn vùng v1 từ map**. Không loại trừ
exposure: E3 có 10 điểm map3age trong các hộp MV sau quy về age 1. Inventory v3
đã reserve chúng trước khi rút CF. Recount này không tính outcome CF, không mở R09/R10.

## 2. Các đợt chạy và phép gộp

Recount đọc sáu CSV bằng `git show` tại commit đã ghim, theo đúng thứ tự dưới.
Lọc c_sw=0; mặc định các trường chưa có: age=1 s, amp=6, c_sw=0. Khóa tọa độ
(λA,λB,κ,η,h,age,amp) dùng Fraction chính xác từ decimal string, không làm tròn.
Giữ bản đầu; kiểm **mọi cột số tất định dùng chung** của bản bị bỏ với bản giữ
(ngoại trừ thời gian wall_s). K và ref cũng phải khớp, không trộn precision levels.

| Batch | Raw c_sw=0 | Giữ sau dedup | Thiết kế / scope |
|---|---:|---:|---|
| stage1 | 60 | 60 | Pilot thô |
| stage2 | 108 | 102 | Thích nghi sau stage1 |
| map1 | 344 | 318 | Lưới thô, loại hộp card; không là phân phối regime ngoài đời |
| map2 | 576 | 554 | 360 XM2S hướng A; 216 XM2X hướng AB/C, chọn sau map1 |
| map3age | 216 | 216 | Tuổi 1/4,1/2,2,4 s; age không là chiều độc lập |
| map4amp | 126 | 126 | ±4,±5,±7: **khác plant ±6 của contract** |
| **Tổng** | **1430** | **1376** | **54 bản sao khớp hoàn toàn** |

Tất cả sáu batch ở K=40, ref=1 (dt=1/120 s). Chỉ các file trên góp bảng chính.
Các đợt robustness tại tag: map1robustK/dt 8+8, plantrobust 12, jointrobust 6;
không cộng chúng vào 1376. Các kết quả robustness trong REGIME_MAP là **source-reported**,
không phải đã chạy lại trong phiên này. [duplicates.csv](../../results/P4_01_recount/20261030_01/duplicates.csv)
liệt kê đủ 54 cặp; bảng sinh lại khớp tọa độ, lớp và sáu contrast với bảng tại tag.

## 3. Sự cố và mức kiểm thực tế

Theo REGIME_MAP: lần map2 đầu không lưu kết quả khi VS Code khởi động lại;
một lệnh bị tác giả từ chối vẫn khởi động; hai tiến trình ghi chung thư mục;
dừng cả hai, giữ 460 checkpoint rồi chạy nốt 116; WSL khởi động lại lúc plantrobust
10/12 và sau đó resume. Không diễn giải sự cố như đã được khắc phục bằng recount.

Log gốc: `results/explore_v13/logs/` **tại tag**, không phải đường dẫn raw trên main.
Phiên này kiểm 54 cặp trùng từ raw, kiểm bảng lưu và hash; **không replay engine**.
Claim K2 “tái lập 6 dòng trùng bit” trong lesson là chưa tự kiểm; K1 25 test nhánh
không chạy lại. E11/K5 và E12/K6 chờ L4.3, không gán PASS do recount khớp.

## 4. Bảng lớp: số đếm mô tả mẫu

C xét trước: GS≤−1; sau đó A (GS≥1,GM<1), AB (GS≥1,GM≥1), B (GM≥1),
J (GSM≥1 và Γ≥max(GS,GM), sau khi các lớp trước loại hết), còn lại D.
Ngưỡng 1% là luật đọc bản đồ tại tag, không là scoring rule mới.

| Mẫu | A | B | AB | J | C | D | Tổng |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bảng dedup | 301 | 43 | 161 | 14 | 334 | 523 | 1376 |
| map1 raw | 21 | 4 | 7 | 1 | 68 | 243 | 344 |

301/1376 và 21/344 phụ thuộc lưới, phạm vi và cách dồn mẫu. Không là prevalence,
không có CI lấy mẫu hay seed: engine pilot là xấp xỉ số tất định, không phải số
chính xác của estimand liên tục. Độ lớn/vị trí/lớp có thể đổi dưới native.

- A ở age1,±6: n=211; median GS=**1.531432882%**, q90 linear=**2.444123771%**,
  max=**4.010867687%**; median GM=**0.012151337%**.
- AB: n=161; median GS=**4.959355698%**, GS|M1=**0.709285075%**; **155/161** Γ<0.
- S11: max sai lệch vế state **3.552713679e−15 pp**, vế model **7.105427358e−15 pp**.
  Min GM=0; min GSM=GS|M1=−1.507851211e−14 pp. Dung sai roundoff 1e−12 pp:
  **0** vi phạm S07/S08, cận Γ≥−min(GS,GM), và S12 trong C.
- Hộp MV+A (quy age1): **11 C,7 B**, không có A/AB/J/D.

## 5. Phân loại 10 phát biểu

AI soạn, tác giả chưa tự kiểm; suy luận dựa [T07 §4–5](../theory/T07_population_estimand.md).

| # | Phát biểu | Loại | Lý do / số đối chiếu |
|---|---|---|---|
| 1 | Model repair không gây hại | Identity có điều kiện | S08 cần true posterior/chung belief; S07 cho GM|S1≥0 |
| 2 | State chỉ gây hại khi model sai | Identity | S07: GS|M1≥0; oracle ô11 là sàn |
| 3 | Trong C, Γ>0 | Identity | S12: Γ≥abs(GS)≥1; min Γ=1.092041957% |
| 4 | Age là chiều mới | Sai | Fluid scaling đưa (age a,κ,h) về (1,κ/a,h/a), với c_sw=0 |
| 5 | GS|M1 không giảm theo age | Điều đã kỳ vọng, chưa là định lý | **54/54** nhóm, đủ 5 tuổi; mode ẩn không tự cho thứ tự Blackwell |
| 6 | Vùng A, model gần 0 | Discovery ứng viên | Chỉ độ lớn/vị trí; n=211 ở age1,±6; chưa native/baseline/novelty |
| 7 | GS lớn, GS|M1 nhỏ trong AB | Discovery ứng viên | 4.9594 so với 0.7093; Γ<0 là cùng quan sát qua S11, không đếm đôi |
| 8 | “A có 301 regime” như tần suất | Gây hiểu nhầm | 301 đúng là số đếm bảng, không đại diện population ngoài đời |
| 9 | ±4 làm mọi effect lớn hơn | Gây hiểu nhầm, khác plant | 54 cặp: median C̄4/C̄6=0.321561574; median GM|S1 tuyệt đối ratio=1.151416121 |
| 10 | J là “cộng hưởng” | Tên gây hiểu nhầm, dấu phần lớn bị ép | 8/14 GS<0; 6 dòng còn lại max Γ=1.111231973%; chưa chứng minh cơ chế |

Chỉ 6 và phần không bị identity ép của 7 đi tiếp như **ứng viên**, không khóa card.
Hai đính chính cho lesson để không truyền tiếp lỗi:

- Đổi S0 thành naive có thể làm mất S08 (GM≥0), nhưng **không tự làm mất S07**:
  bất kỳ policy ô01 nào vẫn có cost ≥ oracle ô11 nếu evaluator/law/objective giữ nguyên.
- Toy T-C cho GS=−0.5 **đơn vị cost**, với Cref=10 tức **−5% Cref**; không phải −0.5%.
  Minh họa này không là một dòng engine/đo mạng hay một bài tác giả đã tự tính.

## 6. Errata append-only E1–E14

Không sửa REGIME_MAP tại tag. E1–E8 kế thừa nguyên bản (giá trị chi tiết có trong snapshot);
E9–E14 ghi thêm dưới đây. Nhãn “kiểm” chỉ phạm vi kiểm raw hiện tại, không human review.

| ID | Cũ | Đúng / cách kiểm | Ảnh hưởng / trạng thái |
|---|---|---|---|
| E1 | κ là tốc độ đổi mode | κ là thời gian mode (s); κ nhỏ đổi nhanh | Kế thừa sửa nghĩa tại tag; không replay r2_keep |
| E2 | Age là chiều state uncertainty mới | Quy κ/age,h/age; không độc lập; fixed S1 marginal có S04 | Kế thừa; số 18 cặp/≤0.20pp source-reported, không kiểm mới |
| E3 | Không regime nào trong hộp card | 10 map3age sau scaling: 2 MV+A,4 MV-ii,4 BND | Kế thừa inventory; không gọi Ω− hoàn toàn unseen |
| E4 | η là biên độ nền | u=2η; amp là biên độ nền | Kế thừa; không đổi code contract |
| E5 | Nhiều kết quả là phát hiện | Phân loại ở mục5 | AI đánh giá; chưa author verification |
| E6 | 301 A được đọc như tỉ lệ regime | map1 chỉ 21/344; mẫu thích nghi | Kiểm raw hiện tại; không prevalence |
| E7 | map1robust có mỗi vùng | Chỉ A/B/AB/D; C ở plantrobust | Kế thừa; robustness không chạy lại |
| E8 | Comment “slow mode switching” cho κ nhỏ | κ nhỏ là fast switching | Kế thừa; không sửa nhánh |
| E9 | q90 A “2.46%” | **2.444123771%**, p=(n−1)q, linear interpolation | Đã kiểm raw; không đổi kết luận |
| E10 | “53/161 gần thay thế hoàn toàn”, không định nghĩa | abs(Γ+min(GS,GM))<0.1pp: **33/161**; <0.05pp: **24/161** | Đã kiểm raw; không trích53; hai ngưỡng mô tả post-hoc, không card |
| E11 | S1 levels không phụ thuộc age, sai ≤0.7% “do cầu phương” | Lesson báo vi phạm S04 tới **0.711%**; chưa có native receipt | **SOURCE_REPORTED_UNVERIFIED**; chờ L4.3. Không trích levels; không suy contrasts đã an toàn |
| E12 | GS pilot dùng để vẽ vùng | Lesson báo native thấp hơn8/8, XM2S110 A→D | **SOURCE_REPORTED_UNVERIFIED**; thiếu native_probe_summary.csv. L4.3 phải audit trước khi vẽ vùng |
| E13 | X2065 làm ví dụ B / MV+A model thắng | X2065 **C**: GS=−1.212335456, GM=13.406930031; MV+A **11 C,7 B** | Đã kiểm raw; C xét trước B; MV nói GM≥1, không đồng nghĩa toàn hộp là lớpB |
| E14 | Không có bảng theo δ | Trong lát κ/age∈[.05,.15],h/age∈[4,8],η∈[.625,.875],amp6: δ=.25 có36/36 AB;δ=.5 có40/42 AB;δ=.75 có9AB/20C/7B | Đã kiểm raw, bảngδ đã lộ; không là vùng mới khóa hay luật tất định |

Bảng δ đầy đủ: [delta_classes.csv](../../results/P4_01_recount/20261030_01/delta_classes.csv).
Sai số chung có thể triệt tiêu khi trừ hai cost nhưng không bảo đảm triệt tiêu;
không dùng ví dụ minh họa trong lesson thay cho kiểm numeric ở L4.3.

## 7. Inventory và exposure

[Inventory v3](../../results/lessons/l3r_7/lean_close/collision_inventory_v3.json)
giữ nguyên hash; **1396 khóa v1.3 phân biệt là toàn inventory**, không phải tổng bốn
batch map: 344+576+216+126=**1262** source records (còn robustness, pilot,
calibration/probes và trùng khóa). Recount xác nhận mọi tọa độ raw được bao phủ,
amp≠6 vào namespace riêng, age được quy về1. Không tái sinh CF hay chỉnh inventory frozen.

Tám `ai_session_probe_unsaved` có tọa độ trong inventory; K6 chỉ được lesson báo
“8 điểm” nhưng không có danh sách tọa độ/receipt. **Chưa xác định là cùng bộ**.
Không tạo số native hoặc gán chúng là K6. Forking log #0 ghi cả các bảng được input
báo đã xem và những phân tích recount thực sự làm trong phiên; không tạo tọa độ mới.

## 8. Record này KHÔNG cho phép nói gì

**AI soạn theo ủy quyền; tác giả chưa tự viết mục này, Understanding/ownership OPEN.**

Record này không cho phép nói vùng A hoặc substitution đã được xác nhận trên
điểm mới. Nó không cho phép đọc số lớp như tần suất operating regime ngoài đời.
Nó không chứng minh engine native giữ nguyên độ lớn hoặc nhãn của map pilot.
Nó không xác nhận realism, novelty, cơ chế, hiệu quả của repair khả thi hay giá trị
riêng của backlog tươi, vì S1 còn cấp mode oracle và D22 chưa implement.
Nó không biến identity thành finding hoặc biến công việc AI thành tự kiểm của tác giả.
Nó không cho phép dùng lại các tọa độ đã lộ như fresh confirmation, hoặc chạy CF
trước các điều kiện/quyết định còn mở.

## Trạng thái sử dụng

Record và recount đã có; E11/E12/K2 chưa audit; chưa thiết kế baseline/card/hộp mới.
DL-103 áp numbering theo lựa chọn tác giả, không ký thay bốn quyết định khoa học.
Record → DL-103 → exposure/forking phải được commit trước native audit L4.3 Part B
hoặc tính hộp mới L4.5. P0-V10, L8, author-written mục8 và Understanding còn OPEN.

## 9. Addendum kiểm chứng và nhãn provenance (cùng ngày, sau ba commit prerequisite)

21/21test mới và731/731full suite PASS (84.52s);10/10recountchecks PASS.
Full tests là regression/fixture, không native audit mới trên map hoặc CF run.
[Báo cáo](../../results/lessons/l4_1/report.md) ·
[Integrity check](../../results/lessons/l4_1/integrity_check.json) ·
[CSV giả](../../results/lessons/l4_1/synthetic_fixture.csv).

| Nhãn provenance | Áp dụng trong phiên này |
|---|---|
| Tác giả viết | Chưa có bài viết riêng cho mục8; không gán nhãn này cho record |
| Author-attested | Không có attestation tự đọc/tự hiểu mới; lịch sử cũ giữ nguyên |
| AI soạn, tác giả duyệt/chọn | DL-103: tác giả chọn rõ numbering v1.2; không suy ra tác giả kiểm mọi số trong record |
| AI theo ủy quyền | Code, fixture, recount, phân loại, errata, record và log; chưa author verification |
