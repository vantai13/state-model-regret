# L3.8 — Gate A REFORMULATE và closeout theo ủy quyền

Người phụ trách: **Doan Van Tai** · 28/10/2026 · contract-v1.2.
Tác giả chọn nhãn REFORMULATE; AI soạn claim/tổng hợp và hai mục ngôi “tôi” theo yêu cầu
trực tiếp. Chưa có xác nhận tác giả duyệt câu chữ hoặc human/Understanding review.

## Đã làm

- Đọc đủ [Part 1](lesson_part1.txt) và [Part 2](lesson_part2.txt), lưu nguyên byte + hash.
- Soạn [Gate note](../../../notes/phases/PHASE_3_gate.md): 11 mục validity, bảng điều kiện
  quy trình riêng, 5 outcome; một nhãn REFORMULATE, một claim/scope, DL-061.
- Soạn [Closeout](../../../notes/phases/PHASE_3_closeout.md), tổng hợp DL-044–060,
  evidence E0/E1, assumptions/risk/claim boundary. Hai mục đã viết ngôi “tôi” theo ủy quyền;
  trạng thái **tự viết/Understanding vẫn OPEN**, không nhập bản soạn thành author attestation.
- Soạn [đối chiếu lesson](../../../notes/lessons/L3.8_evidence_review.md) và
  [handoff/record quyết định](../../../notes/lessons/L3.8_author_handoff.md).
- Cập nhật README, Phase3, progress, experiment index, claim boundary, inventory và exposure.
  Giữ brief/RQ/contract v1.2 nguyên byte; thêm [v1.3 proposal](../../../notes/01_definitions_v1_3_draft.md)
  và [brief proposal](../../../notes/00_research_brief_v1_3_draft.md), chưa adopt/khóa/compute.
- Ghi **một DL-061** cho quyết định tác giả và exception ủy quyền; commit closeout trước tag,
  không force tag hoặc waive điều kiện người đọc.
- Thêm [script audit](../../../experiments/lessons/audit_l3_8.py) chỉ kiểm dữ liệu/lịch sử đã có;
  không import/call engine để tạo outcomes.

## Đã chạy và kiểm chứng

```bash
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3_8/full_suite.xml
.venv/bin/python experiments/lessons/audit_l3_8.py
```

Lệnh pytest thực tế redirect output vào `results/lessons/l3_8/tests.log`.
**391/391 PASS**, 0 failures/errors/skips, **62,64 s**. Đây là test local mới,
không chỉ chép số tests của reviewer. Bộ test chạy regression/toys và phép thiết kế
đã exposed; không gọi runner one-shot để chạy lại A05-T.

Audit gọi `verify_frozen()` để kiểm nguồn/hash/thứ tự commit, đọc manifest/status,
kiểm các index output, liên kết local/anchor và gọi lại rescorer trên dữ liệu đã lưu.
Kết quả chi tiết ở [verification](verification.json), [log audit](audit.log),
[log rescore](rescore.log), [test XML](full_suite.xml), [test log](tests.log).
Audit kỹ thuật PASS; số link và trạng thái commit/tag thực tế trong JSON là kết quả
tại thời điểm kiểm, không dùng câu trong report để tự xác nhận. Không chạy simulation/
engine mới, không tạo sampling CI/p-value.

## Kết quả thí nghiệm được mang sang Gate, không đo outcome mới

Đơn vị PC4 là điểm phần trăm C_ref, metric MAE đều trên GS/GM/Γ, dt chấm1/240s,
kiểm cặp1/120s; seed=null do kỳ vọng finite-law, không lấy mẫu ngẫu nhiên.

| Nhánh | H0 | H1 | Verdict / số đo |
|---|---|---|---|
| PC4 nội suy8ô | MAE0 [0,689644;0,689708] | MAE1 [0,442608;0,442673] | WEAKEN; d≈0,247036<margin0,25 |
| PC4 ngoại suy2ô h12 | MAE0 [2,046199;2,046684] | MAE1 [2,187950;2,188434] | FALSIFY; d≈−0,141751 |
| K5 | Không áp dụng H0/H1 | Không áp dụng H0/H1 | DOES_NOT_STAND: R04 GM/C_ref≈0,527926%>0,5% |
| C1 | Không áp dụng H0/H1 | Không áp dụng H0/H1 | STANDS ở R05–R08, scope4ô/base rate cao |

Các khoảng là enclosure số có điều kiện, không sampling CI. A04:92BOUNDED/46pairs;
A05-T:20BOUNDED/10pairs, p_sw20/20 theo record run. R09/R10 vẫn niêm phong.
29 output hashes A05-T và 100 output hashes A04 được kiểm trực tiếp theo index;
freeze/source/chronology và rescore được ghi số thực trong verification.

## Điều chỉnh logic so với hướng dẫn

- `GM>0 ⇔ lật` phải thêm điều kiện EΔ≠0; T01 đã có ngoại lệ true tie.
- Một observation không tự chứng minh Γ vô nghĩa hoặc buộc REFORMULATE; D19 vẫn
  có ý nghĩa factorial interaction, chưa là cơ chế. Không đổi RQ từ một inference.
- εE không phải ngưỡng accuracy tuyệt đối của H0/H1; MAE chỉ cho thang so sánh.
- C1 được khóa trước test: evidence hợp lệ, nhưng n4/base rate cao/phạm vi hẹp.
- §17–22 trong hồ sơ dựa trên lesson được cung cấp; plan PHASE_3 v2.0 đầy đủ chưa có
  trong repo. Không nhận đã đọc/kiểm template gốc mà chưa có nội dung.

[Lập luận và link nguồn repo](../../../notes/lessons/L3.8_evidence_review.md).

## Quyết định tác giả và exception được ghi nhận

Tác giả chọn nguyên văn **“REFORMULATE — chuẩn bị thiết kế mới”** và yêu cầu
**“tôi yêu cầu bạn hãy đóng vai là tôi và ghi cho tôi đây là yêu cầu”** cho hai mục
closeout. [Record](../../../notes/phases/PHASE_3_author_decision.json) giữ nguồn/timestamp.

Theo yêu cầu trực tiếp, đã viết hai đoạn ngôi “tôi”, ghi một DL-061, cập nhật gate/closeout.
Yêu cầu này thay quy tắc khôngủyquyền của lesson cho việc soạn/đóng hồ sơ; nó không biến
văn bản AI thành trải nghiệm tự học hoặc kỳ vọng trước run. Khuyến nghị NARROW trước đó
của AI không được adopt, không giữ làm nhãn thứ hai.

Claim duy nhất ở gate note nói estimand v1.2 còn điều kiện theo một observation và chưa
xác nhận luật khái quát; tác giả chọn chuẩn bị gain/Γ qua phân phối observations trước
Phase4. Không nóiΓvô nghĩa. Proposal v1.3 nêu joint law/mixture và bảng OPEN cần chốt:
population, support/tail, weights, normalization, grid, metric/margin/models/budget/split.
Không dùng vài quantile làm population hoặc sửa ngưỡng để cứu kết quả cũ.

Closeout commit trước annotated tag `phase-3-closeout`; trạng thái cụ thể của tag/commit
được audit vào completion/verification, không force hoặc ghi tag là Understanding PASS.

P0-V10/L8/T05 author-writing/Understanding vẫn OPEN. **Thực thi Phase4 HOLD tới P0-V10
và contract mới được khóa**; được học/chuẩn bị tiếp. Không nhận Gate A=HOLD chỉ vì
thiếu người đọc; nhãn chính thức là REFORMULATE theo quyết định tác giả.

## File và hạn chế

- [Completion trạng thái thật](../../../notes/phases/L3_8_completion.json).
- [Record lựa chọn/ủy quyền của tác giả](../../../notes/phases/PHASE_3_author_decision.json).
- [Gate](../../../notes/phases/PHASE_3_gate.md), [closeout](../../../notes/phases/PHASE_3_closeout.md),
  [handoff](../../../notes/lessons/L3.8_author_handoff.md), [audit code](../../../experiments/lessons/audit_l3_8.py).
- Run/config gốc: [A05-T](../../A05_test/20261028_01/),
  [config](../../../experiments/A05_freeze/config.json), [verdict](../../A05_test/20261028_01/verdict.json).

Không tạo CSV/biểu đồ outcome mới: lesson này tổng hợp quyết định; số liệu gốc vẫn ở
run A04/A05-T. File JSON/log/XML mới chỉ ghi kiểm chứng và trạng thái. Git/hash không
chứng minh được run bị xóa ngoài hồ sơ, không thay người đọc thật/Understanding hoặc
chứng minh external validity. Trạng thái tag/commit sau thao tác xem completion/verification;
closeout đóng hồ sơ với ownership OPEN, không mở thực thi Phase4.
