# L3R.1 — hoàn tất re-entry và đóng băng discovery

Người phụ trách: **Doan Van Tai** · 28/10/2026 · DL-064.
Triển khai và tổng hợp theo ủy quyền tác giả; không xác nhận tự làm kín sách/human review.

## Đã làm và mục đích

Đã đọc đầy đủ hai tài liệu truy cập được, hướng dẫn/script/test/template/preview trong
ZIP. Một attachment (`e91e6337…/Pasted text.txt`) không tồn tại ở đường dẫn được cấp;
đã tìm trong thư mục attachments nhưng không có. Hướng dẫn Part2 đầy đủ trong ZIP
được dùng thay; không nhận đã đọc file thiếu đó. [Intake](bundle_intake.json).

Đã xóa `results/explore_v13/stage3/L3R1_part2_bundle.zip` sau khi đọc; không stage,
commit hoặc push ZIP. Chỉ giữ hash/inventory nguồn. Attribution nguồn cung cấp giữ
nguyên; trường người phụ trách/triển khai dùng Doan Van Tai.

Đã chuyển về main từ branch pilot, nhập script/test vào main **không merge pilot**,
thêm guard dữ liệu hữu hạn/đủ cột/đủ số dòng và chặn output có sẵn trước khi đọc.
Các công thức/ngưỡng/count semantics của script gốc giữ nguyên.

Đã khai DL-064/exposure/prereg ở commit `c8c165e`, push trước khi đếm. Annotated tag
`explore-v13-pilot` trỏ đúng `a7435e9a3cb0d1625479c942041ec6748444014a`; branch pilot giữ nguyên.
Mục đích là biết chính xác dữ liệu nào đã thấy và sửa sai lệch SUMMARY trước khi viết hypothesis.

## Đã chạy

```bash
.venv/bin/python -m pytest -q tests/test_r3r_01_recount.py --junitxml=results/lessons/l3r_1/recount_tests.xml
.venv/bin/python -m experiments.R3R_01_recount.mutants
.venv/bin/python -m pytest -q --junitxml=results/lessons/l3r_1/full_suite.xml
.venv/bin/python experiments/R3R_01_recount/recount.py --rev explore-v13-pilot --out results/R3R_01_recount/20261028_01
.venv/bin/python experiments/lessons/audit_l3r_1.py
```

- **13/13 tests riêng PASS** (9 gốc +4 finite/output guards), **0,33s**.
- **423/423 toàn repo PASS**, **65,03s**; không chạy lại toàn bộ sau các thay đổi tài liệu.
- **3/3 mutant KILLED**: loại dấu bằng ở harm/model-value, sai mapping u=2eta; chỉ dùng CSV giả.
- Recount subprocess **exit0**, đúng **một** invocation local. Chỉ git-show dữ liệu đã lưu,
  không gọi engine, không tính regime/CF outcome mới. Seed=null vì phép đếm tất định.
- Thời gian của cả lệnh controller được tool đo **0,160293242s**, gồm prechecks/so sánh;
  thời gian riêng subprocess không được lưu trước lỗi kiểm trình bày, nên không tự tạo số đó.
- Bản output khớp preview ZIP ngoài Rev; bản paste cùng nội dung nhưng thiếu newline cuối.

[Log tests](tests.log) · [full tests](full_tests.log) · [mutants](mutants.json) ·
[log recount](recount_console.log) · [preview comparison](preview_comparison.json).

## Kết quả đo lại từ dữ liệu lưu

Harm: Ḡ_S/C̄≤−1%; model value: Ḡ_M/C̄≥1%. C̄=L̄11 của regime.
Pilot chính: ref1, dt1/120s, K40; Stage1/2 c_sw0, Stage3 c_sw1 hoặc4.
Đây là số trên mẫu khám phá thích nghi, không CI hoặc prevalence mạng thật.

| Mục | Kết quả local |
|---|---|
| ID chính / cấu hình phân biệt | **216 /210**,6cặp trùng output giống hệt |
| ID robustness | **18**, gồm9K-refinement và9dt-refinement trên cùng9tọa độ |
| Harm theo stage | **6/60;73/108;1/48** |
| Harm gộp | **80/216ID;78/210cấu hình** |
| Stage1+2 | **79/168ID;77/162cấu hình** có harm |
| Model value≥1% | **20 cấu hình**, tất cảλB8 |
| Max model value | **13,407%C̄** tại X2065;≈42,348%stakes |
| Min state gain | **−21,570%C̄**, tại X2029 |
| Max K refinement | **0,152767ppC̄;0,629855ppstakes** |
| Max dt refinement | **0,193329ppC̄;0,428252ppstakes** |
| Trùng tọa độ v1.2 | **45ID chạm23ô**;21ID c_sw0,24ID kháccost; R05/R11 đã mở |
| R09/R10 | Không pilot cùngκ/h; chỉ so tham số, không outcome được mở |
| Bảng theo stage của SUMMARY | **30/30 ô số khớp**, phần chữ E1/E2 sai |

Trên Stage1+2 phân biệt: harm theoλB6/7/8 là36/21/20; chỉ14cấu hình vừa harm vừa
model value.50/77 cấu hình harm có cả|GM|,|GSM|<0,05%C̄ (diagnostic gần oracle, không exact).
79cấu hình|Γ|≥1%C̄ đều GS<0; không có GS≥0 vàΓ≥1%C̄ trong tập này.

Đính chính diễn giải của lesson cung cấp:14/20=70% tậpMV cũng có harm, còn14/77≈18,18%
tập harm cóMV. Không nói hai vùng “gần như tách rời” từ số14;36/77 ởλB6 là nhóm
đông nhất, không phải majority>50%. Đây là đọc đúng mẫu số, không phải hypothesis mới.

SUMMARY/raw tại tag không bị sửa. [Discovery record](../../../notes/phases/PHASE_3R_discovery_record.md)
ghi **E1–E7**, mappingeta, thiếuD22, mức số khácPhase3, thiếu mã tái lập chỉ báo M0.
Đã ghi rubric “TỐT” chưa có đủ định nghĩa chấm được khóa; không tự áp ngưỡng C̄ để
loại vế stakes hoặc biến nhãn đánh giá khám phá thành verdict.

## Sai sót trong quá trình thực thi và cách xử lý

1. Kiểm diff từ chối dòng trống cuối plan nguồn. Tôi đã gọi bước tag trước khi kiểm
   kết quả commit; do đó tag được tạo/push **trước** commit khai trước, khác hướng dẫn
   bundle. Sau đó commit/push khai trước thành công; **cả hai đều trước recount**.
   Giữ tag đúng target, không force/rewrite; ghi [process note](process_note.json).
2. Recount đã exit0 và khớp preview ZIP, nhưng controller kiểm thêm bản paste gặp
   assertion vì thiếu newline cuối. Đối chiếu từng dòng không khác; phục hồi manifest
   với thời gian artifact ghi thật, không rerun recount hoặc sửa ba file output gốc.
   Không ghi controller ban đầu đã PASS. [Manifest](../../R3R_01_recount/20261028_01/manifest.json).

Hai việc trên là sai lệch quy trình/kiểm trình bày đã công bố, không đổi dữ liệu,
ngưỡng hoặc kết quả đếm. Câu “pilot không trùng tọa độ v1.2” trong plan không thỏa;
đã ghi45overlap thay vì sửa dữ liệu để ép điều kiện đó PASS.

## File lưu

- Source: [recount.py](../../../experiments/R3R_01_recount/recount.py),
  [mutants.py](../../../experiments/R3R_01_recount/mutants.py),
  [tests](../../../tests/test_r3r_01_recount.py),
  [audit](../../../experiments/lessons/audit_l3r_1.py).
- Config: [prereg.json](../../../experiments/R3R_01_recount/prereg.json).
- Số liệu: [recount.json](../../R3R_01_recount/20261028_01/recount.json),
  [report máy sinh](../../R3R_01_recount/20261028_01/report.md),
  [CSV234ID chỉ tham số](../../R3R_01_recount/20261028_01/discovery_regimes.csv).
- Provenance: [manifest](../../R3R_01_recount/20261028_01/manifest.json),
  [output hashes](../../R3R_01_recount/20261028_01/output_hashes.json), [verification](verification.json).
- Hồ sơ: [discovery record](../../../notes/phases/PHASE_3R_discovery_record.md),
  [timeline/14 phát biểu](../../../notes/lessons/L3R.1_evidence_ledger.md),
  [DL/exposure](../../../notes/02_decision_log.md), [completion](../../../notes/phases/L3R_1_completion.json).

Không tạo plot hoặc raw simulation mới trong lesson này.

## Kết luận và giới hạn

Đã xác nhận các số đếm/errata từ artifact tại pilot commit cố định; chưa xác nhận
engine population đúng, realism hoặc hypothesis. **L3R.1 hoàn tất kỹ thuật**,
Understanding tự kiểm/human reader giữ OPEN. Được học L3R.2; audit cần T07 ở L3R.2.
P0-V10/L8/T05 và Phase4 HOLD giữ nguyên; không tự khóa v1.3 hoặc nâng G1.
