# L4.2 — Đọc bản đồ đúng cách: báo cáo thực thi

Người phụ trách: **Doan Van Tai** · 30/10/2026.
Provenance: **AI theo ủy quyền**, không phải bài tác giả tự dẫn/tự tính.
**Phần kỹ thuật hoàn tất; T07 “P4” và Understanding/ownership của tác giả còn OPEN.**

## A. Đã thực hiện

Đã đọc toàn bộ ba input, đối chiếu repo tại `4a969c5`, record L4.1, frozen T07 và
contract AS14. Không có full `PHASE_4.md` trong input; áp đúng phạm vi lesson đã
cung cấp. Không sửa T07 gốc vì file này thuộc manifest contract frozen.

- Đưa ba toy T-A/T-AB/T-C′ vào code và golden tests bằng Fraction, đối chiếu bốn
  loss với helper T07 đã có. Tạo thêm T-B dưới nhãn **AI example**, không ghi là
  bài tác giả tự đặt. Lưu cả cost, contrast, actions và P/N chính xác.
- Kiểm fixture recurrence theo endpoint convention: time scaling, rate scaling,
  initial backlog, phản xạ ở0; thêm counterexamples cho fixed dt và fixed buffer.
- Tính lại từ CSV L4.1 có SHA:18 scaled-age pairs, near-boundary counts, hộp MV+A
  **đã có**, các phần bị identity ép trong hình mechanism, bảng λA×λB/δ/δ/μ/headroom
  trên lát238điểm đã lộ. Không tính hộp mới cho L4.5.
- Đọc trực tiếp hai hình gốc và plot source tại tag574a36f; lưu bản sao PNG nguyên
  byte với SHA256, không vẽ lại hoặc sửa attribution/nhãn nguồn.
- Chạy hai **implementation mutants** trong memory để xác nhận golden tests có
  thể bắt lỗi; không sửa production/frozen source.
- Tạo khung T07P4 với bốn mục để trống theo yêu cầu tác giả tự viết. Ghi exposure
  và forking#2–5; bảngδ đã thấy từ L4.1, không gọi là dự đoán mù.

Không chạy bài optional short-horizon A-by-δ: chưa có dòng dự đoán của tác giả
trước bước xem đó. Không tự tạo dự đoán rồi gán cho tác giả.

## B. Command thực tế và kết quả kiểm

```bash
.venv/bin/python -m pytest -q tests/test_p4_02_toys.py tests/test_p4_02_read_map.py
.venv/bin/python -m experiments.P4_02_reading.run --out results/lessons/l4_2/reading
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.P4_01_recount.verify_artifacts
```

| Kiểm tra | Đo được / trạng thái |
|---|---|
| Test mới | **26 PASS**,0.07s ở lượt có log |
| Golden checks theo ba toy supplied | **8/8 PASS**, phân số chính xác |
| Đối chiếu số trong lesson với pilot CSV | **10/10 PASS** |
| Implementation mutation: default tie thành Switch | **KILLED**, `test_mutant_tie_rule` bắt được |
| Implementation mutation: S0 nhìn state hiện tại | **KILLED**,6 golden checks bắt được |
| Toàn repo | **757 PASS**,**85.29s**, exit0 |
| Frozen/L4.1 integrity | PASS trước phân tích và sau triển khai |

Các test mới còn kiểm S10 phải lấy trung bình của conditional minima, oracle
bound/card implications trên toy, Cref0 không gán%, dữ liệu gần ngưỡng phải đếm
union theo dòng, age normalization giữ amp namespace, plurality khác majority,
source hash mismatch dừng trước đọc CSV, output tồn tại dừng trước đọc input.

**Lỗi đã gặp và sửa:** lượt targeted ban đầu có24PASS/1FAIL. Fixture bảng chéo
chỉ đổi chữ lớp nhưng để GS=GM=0, trong khi `counts` tính lại lớp từ contrast nên
raD. Đã sửa fixture với các contrast cho đúng lớp mong đợi; không sửa rule hoặc
raw data. Lượt targeted tiếp theo và full suite đều PASS. Hai test trong input
gọi “mutant” là input/behavior perturbations; báo cáo2KILLED ở đây là hai lỗi
implementation thật, có danh sách assertion bắt được trong JSON.

Full suite là các regression/fixture hiện có; không phải run native audit map,
confirmation hoặc chạy lại A05-T. Runner L4.2 không import/call engine vật lý.

## C. Kết quả đo được

### Toy exact

Một snapshot không phân biệt được hai state, xác suất mỗi state1/2,
J(Stay)=10; Switch iff gap<0, hòa Stay. Đơn vị dưới đây là **toy cost unit**,
không phải measured packet·s trong plant. Không RNG/seed hoặc sampling CI.

| Toy | L00 | L01 | L10 | L11 | GS | GM | Γ | GS\|M1 | Lớp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| T-A |10|10|19/2|19/2|1/2|0|0|1/2|A|
| T-AB |11|10|21/2|10|1/2|1|−1/2|0|AB|
| T-C′ |10|10|21/2|10|−1/2|0|1/2|0|C|
| T-B (AI example) |11|10|11|10|0|1|0|0|B|

T-A có P=3/5,N=1/2; T-AB/T-C′ có P=1,N=0. Hai toy sau có cùng action của S1M0,
nhưng Dhat(x2) khác (+1 so với+4); gh đi từ−1 sang+1/2, S0M0 đổi action. Đây là
khả năng logic không cần queue dynamics; không xác nhận cơ chế trong plant.

Fixture recurrence có cost gốc1, nhân mọi thời gian và q0×3 cho cost9, nhân rates
và q0×5 cho cost5; các đẳng thức backlog đúng chính xác. Ramp continuous integral
cho4→16, còn endpoint sum với4slot dt=.5→1 cho5→20. Không trộn hai cách tính.

### Bản đồ pilot đã thấy

Điều kiện:1376 dòng đã dedup ở L4.1, c_sw=0,K40,ref1,dt1/120s; age/amp như lưu
trong mỗi dòng. % theo C̄ref; pp là chênh giữa hai số phần trăm. Tất định nhưng
có approximation error; không gán sampling CI. Không có baseline/phương pháp mới
được triển khai trong L4.2.

| Metric | Đo được |
|---|---:|
| Cặp tương đương theo age / cùng lớp |18 /18|
| Max lệch trong sáu contrast |**0.2009889943pp**|
| Cặp/contrast lệch lớn nhất |XA001↔XM2S183,GS:1.6758420302% so với1.4748530359%|
| Dòng cách một biên GS/GM tại±1 không quá0.15pp |**148**|
| A ở age1,amp6 có GS<1.15% |**28/211**|
| MV+A: GM≥1% |**18/18**;minGM=**1.3296333190%**|
| MV+A: lớp và minGS |11C,7B;minGS=−21.5701652661%|
| C: minGM\|S1 / vi phạm oracle bound |1.0920419565% /0|
| A: min(GS−GM) / vi phạm information bound |0.5643047019% /0|
| C có GS\|M1<0.1% |**255/334**|
| A có GM\|S1<0.5% |**286/301**|
| AB: medianGS\|M1 |**0.7092850750%**|
| AB: GS\|M1<0.5% /≥1% |**67/161 /67/161**|

Ngưỡng0.15pp là diagnostic mô tả từ input, **không** dung sai L4.3 mới;148dòng
không phải số điểm đã lật native. Cặp age giữdt cố định nên chỉ tương đương xấp xỉ;
không đóng E11 (S04 levels) hoặc E12 (native GS).

Látκ/age∈[.05,.15],h/age∈[4,8],η∈[.625,.875],amp6 có**238điểm**:

| δ | n | A | B | AB | C | D |
|---|---:|---:|---:|---:|---:|---:|
| 0 |20|3|0|0|0|17|
| 1/4 |36|0|0|36|0|0|
| 1/2 |42|1|1|40|0|0|
| 3/4 |36|0|7|9|20|0|
| 1 |37|0|0|0|37|0|

Toàn phíaδ<0:27điểm,24C/3D; chưa có lời giải thích plant. Bảng đủ12giá trịδ
và23ôλA×λB ở CSV. δ được thêm cộtδ/μ (μ10) để ghi rõ rate unit và scale; không
khẳng định δ tốt hơn headroom ratio hoặc là tọa độ duy nhất.

### Đính chính diễn giải trong input

- “Cùngδthì cùnglớp” không đúng tất định; δ=.5 có40AB/1A/1B. Chỉ nhận xu hướng
  tổ chức dữ liệu trên lát pilot, chưa là cơ chế hoặc claim đã confirm.
- Ô(λA6.25,λB7):AB8/C7/B3. AB8/18 là plurality, không đa số>50%.
- Population S10 là **E_Y[min(P(y),N(y))]**; min(P,N) chỉ theo một y. Một fixture
  hai y cho giá trị thật0 nhưng min của các unconditional means là1/2.
- “Đối chứng lậtκ vô dụng vớiΓ” chỉ đúng khi có bảo đảm toán học về GS/GM trong
  vùng đối chứng. Lậtκ tự nó không làm contrast nhỏ theo identity; pilot nhỏ
  chưa là bảo đảm đó. Không tự đổi thiết kế/scorer/card SUB từ lời giải thích này.
- Rule A chỉ nói GM<1, không ép GM gần0 hoặc state value nằm xa0 một mức cố định.
  “Một nửa vẻ đẹp” trong lesson là cách nói, không metric50% đã đo.
- “CardMVđúng” chỉ được ghi18/18điểm discovery đạtGM, không là confirmation của hộp.

## D. File đã lưu

- Source: [toys.py](../../../experiments/P4_02_reading/toys.py),
  [read_map.py](../../../experiments/P4_02_reading/read_map.py),
  [run.py](../../../experiments/P4_02_reading/run.py).
- Test: [goldens](../../../tests/test_p4_02_toys.py),
  [đếm/lọc/group guards](../../../tests/test_p4_02_read_map.py).
- Số đo: [map_summary.json](reading/map_summary.json), [toys.json](reading/toys.json),
  [scaling](reading/scaling_fixture.json), [golden checks](reading/golden_checks.json),
  [implementation mutants](reading/implementation_mutants.json).
- CSV: [18agepairs](reading/age_pairs.csv), [148near-boundary](reading/near_boundary.csv),
  [λA×λB](reading/lambdaA_lambdaB_classes.csv), [δ](reading/delta_classes.csv).
- Hình gốc tại tag, sao nguyên byte: [differ](reading/regime_map_differ.png),
  [mechanism](reading/regime_map_mechanism.png). **Không có hình vẽ mới hoặc hình native**.
- Input/config/hash: [input manifest](input_manifest.json),
  [run manifest và cấu hình](reading/manifest.json).
- Log: [26test mới](targeted_tests.log), [runner](reading.log),
  [757fulltests](full_tests.log), [integrity sau run](integrity_after.json),
  [verification](verification.json).
- Hồ sơ: [technical note](../../../notes/verification/l4_2/reading_note.md),
  [T07P4 author template](../../../notes/theory/T07_P4_author_addendum.md),
  [forking JSONL](forking_paths.jsonl),
  [completion](../../../notes/phases/L4_2_completion.json).

Không tạo simulation/native_probe_summary/CF outcomes mới. Không đổi file source
trong `src/`, engine, card, contract, inventory hoặc full frozen prereg.

## E. Kết luận và phần còn mở

Đã kiểm code toy cho ra các đáp án exact, phát hiện được lỗi implementation đã
cài có chủ đích, và các số mô tả chính của lesson khớp CSV pilot. Từ số liệu phải
đọc AB là không đồng nhất; shape do inequality ép khác phần độ lớn/vị trí quan sát.

Chưa xác nhận queue mechanism, δ vượt headroom ratio, native accuracy, realism,
novelty hoặc hypothesis trên điểm mới. G1 giữ nguyên; E11/E12 còn chờ L4.3.
T07P4 vẫn trống theo Part3§6; Understanding/ownership/P0-V10/L8 giữOPEN. Bài
optional dự đoán chưa chạy. Baseline/card/CF-v3/Gate4 vẫn do tác giả quyết.
**Có thể học L4.3**, nhưng chưa tự chuyển sang audit native hoặc chọn dung sai.
