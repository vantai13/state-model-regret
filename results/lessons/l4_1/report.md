# L4.1 — Re-entry regime map: báo cáo thực thi

Người phụ trách: **Doan Van Tai** · 30/10/2026.
Provenance: **AI theo ủy quyền**; numbering v1.2 do tác giả chọn trực tiếp trong chat.
**Hoàn tất phần kỹ thuật L4.1; phần tự viết/tự hiểu của tác giả vẫn OPEN.**

## A. Đã thực hiện

- Đọc toàn bộ ba input; lưu snapshot nguyên byte, SHA256 và provenance.
- Kiểm repo, T07, pilot record, DL-097–102, card/locks, inventory; `git fetch origin`
  xác nhận local khớp origin/main tại `028ab8f` trước thay đổi.
- Viết recount độc lập với code exploration, đọc git blobs tại tag bất biến
  `explore-v13-regime-map` → `574a36fb4213a79d3d2aa305a489701cfc3059f2`.
  Không merge nhánh. Khóa tọa độ Fraction chính xác; kiểm cả các deterministic
  numeric columns dùng chung khi dedup; bỏ wall_s khỏi phép so bản sao.
- Tạo record đủ tám mục, phân loại mười phát biểu, errata E1–E14 append-only;
  ghi rõ E11/E12 source-reported, chưa kiểm native.
- Tác giả chọn v1.2 sau khi xem hai phương án: Phase4(hợp nhất),5(confirmation),
  6(mechanism). DL-103 có bảng ánh xạ sáu dòng; không sửa tài liệu frozen cũ.
- Ghi exposure và forking log#0, phân biệt số được input báo với phép tính
  recount thật; không mặc định tám unsaved probes là tám native probes K6.
- Tạo CSV giả7dòng/6lớp+1duplicate và đáp án bốn loss; fixture và đáp án do AI
  suy đại số, **không phải tác giả tự tính hoặc independent human review**.

Ba commit prerequisite đã có đúng thứ tự, trước bất kỳ native audit map hay hộp mới:

| Bước | Commit |
|---|---|
| Record + errata + code/raw recount | `7385015` |
| DL-103 + author choice | `87d6f83` |
| Exposure + forking#0 | `c3aa70b` |

## B. Command và kiểm chứng

| Command thực tế | Trạng thái / output |
|---|---|
| `git fetch origin` | exit0; main khớp origin trước thay đổi |
| `.venv/bin/python -m pytest -q tests/test_p4_01_recount.py` | **21 PASS**, lượt có log0.05s |
| `.venv/bin/python -m experiments.P4_01_recount.recount_map --out results/P4_01_recount/20261030_01` | **PASS,10/10checks**;0native calls trong recount |
| `.venv/bin/python -m experiments.P4_01_recount.verify_artifacts` | **PASS**; hash/ancestry, không engine |
| `.venv/bin/python -m pytest -q` | **731 PASS,84.52s**, exit0 |
| `git -c core.whitespace=cr-at-eol diff --cached --check` | PASS; bảo toàn byte input/CSV CRLF |

Các test mới kiểm đáp án từ bốn loss, C priority, inclusive thresholds, điều kiện
Γ của J, duplicate mâu thuẫn (contrast/Cbar/ref), exact key không gộp điểm gần,
c_sw filter, defaults, nonfinite, quantile, age-scaling và output overwrite guard.
Full suite dùng các test regression/fixture hiện có; không phải native audit mới
trên regime map hoặc run confirmation. Không chạy lại A05-T hay audit K2/K5/K6.

Hai lỗi môi trường/định dạng đã xử lý, không che là PASS từ đầu:
- Shell không có executable `python` (exit127); các lần chạy thật dùng `.venv/bin/python`.
- `git diff --cached --check` đầu tiên exit2 vì CRLF bị đọc là trailing whitespace
  trong bản sao nguyên byte và CSV chuẩn của csv.writer. Commit chưa diễn ra;
  kiểm lại bằng `core.whitespace=cr-at-eol` đạt, không sửa nội dung/hash để che lỗi.

## C. Số đo thực tế

Điều kiện: sáu batch stage1/stage2/map1/map2/map3age/map4amp, c_sw=0,
K40,ref1,dt1/120s; tuổi/biên độ theo từng dòng. Xấp xỉ số tất định, seed không áp
dụng; không có sampling CI hoặc phân phối regime thực tế. Sai số engine native
chưa đo ở phiên này. % là theo C̄ref; pp là chênh hai giá trị phần trăm.

**1430raw→1376dedup;54/54 bản bị bỏ khớp hoàn toàn** trên deterministic numeric
columns dùng chung. Bảng sinh lại khớp toàn bộ tọa độ/lớp/sáu contrast với bảng ở tag.

| Mẫu | A | B | AB | J | C | D |
|---|---:|---:|---:|---:|---:|---:|
| Dedup1376 |301|43|161|14|334|523|
| map1raw344 |21|4|7|1|68|243|

Hai dòng này mô tả thiết kế lấy mẫu khác nhau, **không là so sánh baseline/phương
pháp mới hoặc tần suất ngoài đời**. Phiên này không triển khai baseline mới.

| Metric | Đo được |
|---|---:|
| A ở age1,amp6 |211dòng|
| Median GS của A |1.531432882% C̄ref|
| q90linear GS của A |2.444123771% C̄ref|
| Max GS của A |4.010867687% C̄ref|
| Median GM của A |0.012151337% C̄ref|
| AB: median GS / GS\|M1 |4.959355698% /0.709285075%|
| AB có Γ<0 |155/161|
| Near-substitution: abs(Γ+min(GS,GM))<0.1pp /<0.05pp |33/161 /24/161|
| MV+A đã có, quy age1 |11C,7B|
| X2065 |C; GS−1.212335456%,GM13.406930031%|
| S11 max error, vế state /vế model |3.552713679e−15 /7.105427358e−15pp|
| Vi phạm lower boundΓ /S12 |0 /0 (diagnostic tolerance1e−12pp)|
| Monotonic GS\|M1 theo age |54/54nhóm, mỗi nhóm5tuổi|
| Median C̄(amp4)/C̄(amp6),54cặp |0.321561574|
| Median GM\|S1 tuyệt đối ratio amp4/6 |1.151416121|
| Inventoryv3 distinct v1.3 keys |1396; không tọa độ raw nào thiếu|

Lát δ đã có trong input: δ=.25 có36/36AB;δ=.5 có40/42AB;δ=.75 có9AB/20C/7B.
Bảng đầy đủ và điều kiện lọc có trong delta_classes.csv/script, không khóa hộp mới.
Bốn batch map chính có1262source records;1396là distinctkeys **toàn inventory**.

Kiểm nguyên vẹn: bốn receipt có21/10/12/15entries đều khớp hash;12artifact CF
prereg cũng khớp. Có overlap giữa receipt, không cộng chúng thành số file phân biệt.
Record→DL→exposure ancestry PASS; tag và SHA256 output/input/script đều khớp.

Đính chính logic trong input đã ghi vào record: naiveS0 có thể phá S08 nhưng không
tự phá oracle floor S07; toyT-C GS−0.5cost với Cref10 tương đương−5%, không−0.5%.

## D. File đã lưu

- Source: [recount_map.py](../../../experiments/P4_01_recount/recount_map.py),
  [verify_artifacts.py](../../../experiments/P4_01_recount/verify_artifacts.py),
  [test_p4_01_recount.py](../../../tests/test_p4_01_recount.py).
- Hồ sơ: [record](../../../notes/phases/PHASE_4_regime_map_discovery_record.md),
  [DL-103 entry](../../../notes/phases/PHASE_4_entry_decision.md),
  [decision log](../../../notes/02_decision_log.md),
  [exposure](../../../notes/00_exposure_register.md),
  [forking note](../../../notes/phases/PHASE_4_forking_paths.md),
  [forking JSONL](forking_paths.jsonl), [author choice](author_decision.json).
- Số đo/config/hash: [recount.json](../../P4_01_recount/20261030_01/recount.json),
  [manifest.json](../../P4_01_recount/20261030_01/manifest.json),
  [regime CSV](../../P4_01_recount/20261030_01/recounted_regimes.csv),
  [duplicates](../../P4_01_recount/20261030_01/duplicates.csv),
  [delta CSV](../../P4_01_recount/20261030_01/delta_classes.csv),
  [parameters only](../../P4_01_recount/20261030_01/discovery_parameters.csv).
- Log: [recount](recount.log), [21tests](targeted_tests.log),
  [731tests](full_tests.log), [integrity](integrity_check.json),
  [format check](whitespace_check.log).
- Input/fixture: [input manifest](input_manifest.json), [CSV giả](synthetic_fixture.csv),
  [đáp án bốn loss](synthetic_expected.json).
- Trạng thái: [completion](../../../notes/phases/L4_1_completion.json).

Không tạo biểu đồ, native_probe_summary, dữ liệu simulation hoặc CF outcome mới.
Raw gốc vẫn ở git tag/nhánh exploration; main chứa con trỏ và bảng recount dẫn xuất.

## E. Kết luận và giới hạn

Đã xác nhận số trích trong record đi từ raw, dedup nhất quán, các identity kiểm
được không vi phạm ngoài roundoff, và sổ/commit/provenance có địa chỉ.
Chỉ vùng A và GS|M1 nhỏ trong AB là discovery ứng viên; **chưa xác nhận hypothesis,
native accuracy, realism, novelty hoặc cơ chế**. Không nâng G1.

E11/E12 và K2 chờ L4.3; thiếu PHASE_4.md/full verification package được ghi rõ.
Không đủ thông tin đối chiếu K6 với8unsaved probes. Mục8record hiện là AI soạn,
không phải tác giả tự viết; Understanding/ownership/P0-V10/L8 vẫn OPEN.
Baseline/card/CF-v3/Gate4 còn do tác giả chọn. Có thể học L4.2; chưa thực hiện
L4.3 audit, L4.4baseline, L4.5card design hoặc Phase5confirmation.
