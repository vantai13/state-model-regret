# L2.7 Part A — kết quả thực hiện26/10/2026

Người phụ trách: **Doan Van Tai**. **Hoàn tất các phép tính và artifact;
chưa hoàn tất primary reading P02 vì truy cập full text bị chặn.**
AI-T không thay L-self/Understanding/Gate. Part B/P12/OεRE chưa thực hiện.

## Đã làm gì?

- Đọc primary P03=R51 (PMLR27trang) và P07/DOTE (USENIX26trang gồmcover) ở mức
  targeted; nhìn4trang công thức/hình. P02 kiểm DOI/official abstract, **AI-A**,
  không ghi targeted theo lời lesson. [Nguồn/version/hash/lỗi](source_access.json),
  [metadata](source_metadata.json), [thẻ trước đọc](reading_card.md).
- Lưu [bài và đáp án bài tập AI](../../../../notes/literature/model_fidelity_methods.md),
  [P03](../../../../notes/literature/papers/P03.md),
  [P07](../../../../notes/literature/papers/P07.md),
  [P02/pending](../../../../notes/literature/papers/P02.md).
- Thêm K-M1…5, matrix/log và [MT1…8 cho Phase4/HOLD](../../../../notes/phases/PHASE_4_methodology_threats.md).
  K-M5/MT2/6/7 giữ rõ phần P02 chưa kiểm; MT5 chờ A05, không chọn null.
- Sửa metric#5 trong landscape: P03 đã dùng expected-return decision regret;
  sửa L(cost)≠R(regret), OAT/factorial và simple/averaged effects. Không gán Γ cho
  P02/P04; arxiv2303.00735v1 hiển thị tên DOTE, trái alias lesson nêu.
- [Excel](../../../../papers/paper_comparison.xlsx)10→12công trình, chỉ thêm
  P07/P02; P03 dùng chung R51. Mười tiến độ tác giả giữ nguyên; chín notes khác
  giữ nguyên, R51 AI note nâng từ thứ cấp lên T có [migration record](workbook_note_update.json).
  Backup đầy đủ trước sửa ở `~/papers/state-model-regret/archive/2026-10-26_before_l2_7_part_a/`.

## Đã chạy và số đo

```bash
.venv/bin/python -B experiments/lessons/l2_7_model_methods.py
.venv/bin/python -B tools/paper_library/build_notes.py
.venv/bin/python -B experiments/lessons/audit_l2_7_part_a.py
git diff --check
```

Generator **14/14checks PASS**; exhaustive256factorial tables và256two-future
decision problems, replay CSV độc lập bằng enumeration contingent policies và
saturated-factorial coefficients. Đây là teaching examples exact, không là
Monte Carlo, paper replication, null test hoặc Phase3 grid.
Arithmetic Fraction, seed **N/A**, hai futures xác suất1/2, tie chọnStay.
Cost minh họa tùy ý; riêng V1 giữ unit packet·s từ artifact cũ, không là ms.

| Trường hợp | Controller | Expected cost | RP | WS | Avoidable regret | Hindsight gap |
|---|---|---:|---:|---:|---:|---:|
| Lesson | Stay | 4 | 3,5 | 2,5 | 0,5 | 1,5 |
| Lesson | Switch tối ưu | 3,5 | 3,5 | 2,5 | 0 | 1 |
| Bài tập đổi cost | Stay tối ưu | 4 | 4 | 2,5 | 0 | 1,5 |
| Bài tập đổi cost | Switch | 4,5 | 4 | 2,5 | 0,5 | 2 |

Future EVPI=**1** ở lesson, **1,5** ở bài tập. Cùng controller chọn đúng vẫn có
hindsight gap dương; không đem optimality ratio của DOTE so với D18/Cref.

V1: **L=(1,25;1,50;1,25;1,25)** theo00/10/01/11;
**R=(0;0,25;0;0)**, GS=−0,25, GM=GSM=0, Γ=**+0,25**.
Additive prediction L00=1,50 thay vì1,25; error0,25=Γ.
Averaged state/model effects=−0,125/+0,125. Additive exercise (4,3,2,1):Γ=0.
Cùng ba observed corners với L00=1,25/1,50/1,75 cho Γ=+0,25/0/−0,25.
Đây là abstract completions không thêm ràng buộc từ J/law, không phải ba
V1/contract configurations khả thi với cùng fixed M0.
Không có estimated CI vì các phép tính hữu hạn này là exact; không suy uncertainty
bounds hoặc effect trên lưới nghiên cứu từ chúng.

Audit kiểm167protected files,52file trong manifest cũ, preserve10human progress,
9notes khác và guarded migration của R51. Excel3tabs/12unique rows,9PDFlocal,
0PDFembedded. [Kết quả audit máy đọc](verification.json),
[kiểm Excel](../../../../papers/data/verification.json).

## Output thực có

| Loại | Nơi lưu |
|---|---|
| Source / audit | [generator](../../../../experiments/lessons/l2_7_model_methods.py), [auditor](../../../../experiments/lessons/audit_l2_7_part_a.py), [workbook builder](../../../../tools/paper_library/build_notes.py) |
| Log chạy | [run.log](run.log), [workbook_build.log](workbook_build.log), [audit.log](audit.log) |
| Số liệu | [toy_results.json](toy_results.json), [oracle_examples.csv](oracle_examples.csv), [factorial_examples.csv](factorial_examples.csv), [oracle_sweep.csv](oracle_sweep.csv), [factorial_sweep.csv](factorial_sweep.csv) |
| Configuration | [config.json](config.json), [protected_before.json](protected_before.json) |
| Literature | [search log](../../../../notes/literature/search_log.md), [prior boundary](../../../../notes/literature/prior_boundary.md), [MT queue](../../../../notes/phases/PHASE_4_methodology_threats.md) |

Không tạo biểu đồ vì các bảng đủ trình bày kết quả. PDF2bài và4trang render lưu
ngoài Git, exact paths ở source_access; **không có PDF P02**. Không tạo simulator
outputs, outcomes grid/held-out, Phase4 prereg hoặc null implementation.

## Phần còn mở và giới hạn

| Yêu cầu | Trạng thái thực |
|---|---|
| P03 formulation/theorem/experiments/limitations | AI-T; không full-read mọi appendix hoặc chạy code paper |
| P07 formulation/oracle | AI-T, cao hơn A vì đã kiểm selected sections; không full proof |
| P02 §2.1/2.2.4/3.1–3.3/4/captions | **BLOCKED**: timeout/403; Unpaywall không trả PDF; provider fallback báo candidates không khớp. Official abstract/metadata có, không xác nhận numbers/OAT/recorded future |
| Bài tập oracle, factorial, V1 | PASS exact; kiểm teaching examples và artifact cũ, không hypothesis evidence trên grid |
| K-M/MT/index/Excel | Đã lưu; K-M5 và phần P02 trong MT2/6/7 là pending; không giả complete literature evidence |
| Understanding/L-self/Gate/A4/A05/L2.8–2.9 | Chưa đóng; formal author/human tasks giữ nguyên |
| L2.7 Part B/P12/OεRE | Chưa thực hiện; không tự chuyển scope |

Lỗi môi trường nhỏ: lệnh helper `python` không có, đã dùng `.venv/bin/python`;
không ảnh hưởng các run PASS. Staged whitespace check bắt CSV mặc định CRLF;
generator đã đổi sang LF và chạy lại trước commit. Lỗi full-text là lỗi truy cập, không là bằng chứng
paper không OA hoặc không có kết quả liên quan. Việc cần bổ sung cho PartA là
primary P02 khi nguồn đọc được; chỉ sau đó mới hoàn tất ba note theo lesson.
G1/HOLD Phase4, contract/grid/PC/forecast/thresholds giữ nguyên.
