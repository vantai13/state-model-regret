# Phase 3 — bản triển khai hiện hành từ L3.1 Part 3

Người phụ trách: **Doan Van Tai** · 27/10/2026 · Contract: `contract-v1.2`.
AI soạn theo yêu cầu triển khai; không phải bằng chứng tác giả đã tự giải thích.
Nguồn: [lesson được cung cấp](../../results/lessons/l3_1/part3/lesson_source.txt).
Đây là bản triển khai phạm vi lesson, **không phải bản chép PHASE_3 v2.0**:
bản plan đầy đủ được lesson nhắc tới không có trong repo hoặc Downloads hiện tại.

## 0.4. Tránh nhầm ký hiệu và phiên bản

| Ký hiệu | Nghĩa | Nơi quyết |
|---|---|---|
| P0-V9 | Timescale có nguồn hoặc ghi chưa có nguồn | PHASE_0_closeout, giữ nguyên |
| P1-V9 (V9 ở Phase 3) | Điều kiện heads-up/memo trước A04 được tác giả **waive**; memo chưa gửi | DL-054 thay điều kiện chờ ở DL-043/044 |
| P0-V10 | Người thật đọc contract **v1.2**, brief và claim boundary hiện hành | HOLD thực thi Phase 4 |
| L8 | Người thật đọc prior boundary, related work và giới hạn claim | Điều kiện Gate L |

## 1. Trạng thái vào Phase 3

[DL-043](../02_decision_log.md#dl-043--gate-l-go-có-điều-kiện-2026-10-26):
Gate L **GO có điều kiện**, tag `phase-2-closeout`. Phase 3 mở; L3.1 Part 3
hoàn tất phần kỹ thuật khi verification PASS. Không ghi toàn L3.1 Understanding
PASS: chưa có record tác giả tự kiểm Part 1–3 trong phiên này.

## 2. Bốn dòng mở Phase 3

Theo DL-044, cập nhật riêng V9 bằng **DL-054**:

1. **V9: WAIVED_BY_AUTHOR.** Tác giả yêu cầu bỏ chặn để triển khai L3.5; memo vẫn chưa gửi,
   không ghi GVHD đã phản hồi. [Gate record](A04_execution_gate.json) và DL-054 ghi rủi ro
   tính lại A04 nếu hướng đề tài thay đổi. Còn hoàn tất prereg/exposure/runner trước run.
2. **Người đọc: P0-V10 và L8 OPEN.** Có [gói 30–45 phút](../meetings/phase2_reader_packet.md), chưa có buổi đọc.
3. **Tự viết: OPEN.** Lý do DL-038 và §1–2 của closeout Phase 1/2 vẫn chờ lời tác giả; không chặn việc học/thực thi Phase 3.
4. **Provenance:** commit L3.3 trước mọi A01; khóa A05-F trước A05-T; discovery A04 không trở thành confirmation; giữ exposure thật.

## 3. Ràng buộc thực thi

- **L3.2:** có thể học/kiểm engine trước các việc người thật. Engine phải dùng D v1.2;
  migration ở §8 chỉ kiểm dựng cell/D, chưa xác nhận engine hoặc estimand D18–D19 hoàn chỉnh.
- **L3.3 → A01:** card chứa claim còn đứng, sau nhãn tác giả xác nhận + L-self WM26
  (đã author-attested ở DL-043), và được commit trước lần chạy A01 đầu tiên.
- **A01:** PASS theo DL-053; M01/M09/M22 đủ ref1–16, dt cuối1/240 s; C1–C6 PASS.
- **A04:** A01 PASS; DL-054 đã gỡ riêng V9 theo yêu cầu tác giả. Trước run phải có
  prereg/exposure và kiểm runner/card/dt;38 main + controls, báo đầy đủ tọa độ dẫn xuất
  và p_sw thực. Chưa chạy A04 trong nhiệm vụ đổi gate này.
- **A05-F:** khóa H1/null/metric/biên/split theo D25, cùng quyền thông tin/ngân sách fit;
  nên có người đọc trước bước này. **A05-T:** chỉ sau freeze, dùng R01–R12.
- **Phase 4:** HOLD tới P0-V10. L8 và P0-V10 có thể dùng chung một buổi nếu đủ phạm vi.

## 4. V9 bảo vệ ER8

Đổi D13, phạm vi D20/D21 hoặc luật chọn lưới sau A04 sẽ đổi estimand hoặc miền
đánh giá; phải chạy/tính lại và mất giá trị prediction theo thiết kế cũ. Đổi εR
chủ yếu đổi nhãn, rẻ hơn nhưng vẫn phải ghi sensitivity/post hoc, không sửa
ngưỡng đã khóa để làm kết quả thuận lợi. Read-back với bạn học giảm ER3, không
loại rủi ro GVHD muốn đổi hướng. **DL-054 đã ghi quyết định tác giả tiếp tục trước
khi gửi memo**, cùng rủi ro phải tính lại khi hướng thay đổi. Kết quả cũ chỉ có
giá trị theo estimand cũ; giữ provenance/post-outcome status của mọi redesign.
Waiver không phải human review và không đóng L8/P0-V10.

## 5. Người đọc và giới hạn evidence

P0-V10 làm rõ điều kiện gốc “contract v0” thành đọc **thiết kế đang thực thi v1.2**;
đọc snapshot cũ không đủ. Đưa brief/contract ở tag `contract-v1.2` cùng claim boundary
và phần bổ sung Phase 2 hiện hành; ghi commit của bản đọc. L8 cần thêm ba mục của
reader packet. Chỉ đổi trạng thái khi có vai trò, ngày, phạm vi đọc và xử lý phản hồi.
Không có nền queueing vẫn có thể góp ý khung; “không phản đối” không kiểm chứng toán.
Verification, AI review và người thật có quyền phản đối là ba tầng khác nhau.

## 6. Ownership còn mở

DL-038 cần tác giả tự giải thích: vì sao λA chung thất bại; vì sao neo thay NARROW
11 ô; đánh đổi cùng độ khó/khác tải; h chọn sau exposure p_sw thiết kế. Điều cuối
phải ghi là lựa chọn sau screen, không giả thành preregistration ban đầu.
Hai mục đầu mỗi closeout cần 5–10 câu “trước tôi nghĩ…, giờ…, vì…”. AI có thể soạn
card nhưng không tạo evidence tự hiểu thay tác giả. Chưa có tự chấm “tôi bảo vệ được”
cho năm quyết định trong lesson; không điền thay một trải nghiệm của tác giả.

## 7. Bản hiện hành và experiment index

[Khối con trỏ](../../README.md) · [index A01/A04/A05-F/A05-T](../03_experiment_index.md)
· [tiến độ lịch sử](../00_progress_log.md). `00_history.md` chỉ giữ lịch sử các thế hệ.
D1–D25/lưới khóa tại tag; claim boundary hiện hành có addendum Phase 2, không sửa estimand.

## 8. Bước 9 — Keep / Reference / Archive / Rebuild

| Artifact | Nhãn | Áp dụng trong v1.2 |
|---|---|---|
| Definitions/brief/claim boundary v1.2, grid/protocol v1.2 | Keep | Luật hiện hành; ghi rõ addendum sau tag |
| `anchoring.py`, `stationary_spectral.py`, T04 | Keep | Luật neo và solver chọn ở DL-033 |
| `exact.py`, `idle_gap.py`, `dominance.py`, `single_observation.py` | Keep | Thành phần toán; vẫn phải kiểm engine tích hợp tại L3.2 |
| `gap_screen.py` và native kernel | Keep | Chẩn đoán thiết kế; không tự thay engine regret |
| `src/smr/design.py` | Reference | Plant L1.8C bước −2/+1; không dùng làm D v1.2 |
| `src/smr/stationary_v2.py` | Reference | Prototype trước lựa chọn spectral DL-033 |
| `queue_D`, `law_for`, `lattice`, `make_cell` trong experiments | Rebuild → `src/smr/cells.py` | Giữ file gốc nguyên byte; so khớp constructor và D |
| `src/smr/cells.py` | Keep sau verification | API dựng cell/D v1.2, không import experiments |
| Definitions/brief v0/v1/v1.1 và lưới cũ | Archive | Giữ nguyên provenance, không dùng làm contract mới |
| `2026-10-23_headsup.md` | Archive | Nháp v1.1 lỗi thời; không dùng nguyên trạng để gửi |
| Evidence/tests/results Phase 1–2, source experiments | Keep | Không xóa hoặc viết đè artifact lịch sử |

§8 là phân loại trên file hiện có, không nhận đã xác nhận một bảng đầy đủ từ plan v2.0.
Rebuild giữ nguyên body bốn hàm, gồm giả định age=1 s và capacity=10; nguồn và SHA-256
ở [config](../../results/lessons/l3_1/part3/config.json). Kiểm 38 main constructors,
D tách A/B trên M01/M09/M22 và N01 ở ref 1/2/4, invariant N01; không dựng D held-out.

## 9. Kết quả phiên L3.1 Part 3

[Report/commands](../../results/lessons/l3_1/part3/report.md) ·
[verification.json](../../results/lessons/l3_1/part3/verification.json).
Part 3 không đo hypothesis: không có baseline/new-method regret hoặc confidence interval.
Chỉ báo số kiểm migration, sai lệch numerical và regression tests thực chạy.

## 10. L3.2 — engine exact v1 thực nghiệm (27/10/2026)

Theo DL-045/046, [engine](../../experiments/A00_engine/) có core Side/aggregate,
vật lý native/mean-path, D22, numeric enclosures và guard. [T05](../theory/T05_exact_engine.md)
vẫn **OPEN ở phần tác giả**: code mới giữ trong experiments, chưa promote vào src.
Technical verification: **72 tests mới, 300 toàn repo PASS; 11/11 mutant bị bắt**.
[Báo cáo và số đo](../../results/lessons/l3_2/report.md). Không nhận Understanding PASS.

Chỉ toy outcomes và D-only migration đã khai báo; không outcome grid. Cờ allow-grid không
thay card L3.3, T05/ownership hoặc các điều kiện runner (V9/A01). Held-out cần purpose
A05-T và commit A05-F sạch; tên path minh họa được ghi trong engine guard.
Các invariant báo cáo không thay checker độc lập; E3/E6 không là D7 H=1 known-mode states.
EVPI_w/flip mass 2D để sau. Bước tiếp: L3.3; A01 vẫn chưa chạy.

## 11. L3.3 / A03 — prediction card (27/10/2026)

[Card v1](PHASE_3_prediction_card.md) có14sanity,4forecast,1luật K5; [receipt](PHASE_3_prediction_card.lock.json)
ghi card commit/SHA-256, tag `a03-card-v1` trên commit receipt tiếp theo. Tác giả chọn
K5 danh sách và luật κ≥2/q90/q90/h8; read-back already_implied/engine T05 author-attested
(DL-048). Cơ chế chưa có: dùng lựa chọn “forecast không cơ chế”, không tự gán route.
P1 sanity, P4 deferred; optionalP2/P3 coordinate extensions chưa adopt. K5 rule carry
mọi trạng thái main chưa bị bác, kể cả unknown, nguyên văn sang A05-F; báo k/m, m=1.

324 tests PASS,11/11 mutant bị bắt,4000ledger0vi phạm. [Report](../../results/lessons/l3_3/report.md).
Guard đổi đúng card path, từ chối DRAFT, kiểm SHA/commit/tag trước mọi D/cost work.
Sửa signed-ratio enclosure, giữ εE/εR và claims.md byte. Review là AI tự kiểm, không
independent review/novelty hoặc fixed-grid feasibility. Không A01/A04/A05 hoặc src promotion.

## 12. L3.4 / A01 — dt cuối đã chọn (27/10/2026)

[Prereg](../../experiments/A01_null_refinement/prereg.md) commit81233ef/SHA9b8dc2f3…,
receipt/source versions giữ theo DL-050–052; A03 card nguyên byte. Run01 FAIL tại
SD N01 vì model tie −1.35525e−20; sửa always-empty/mean-no-idle certificates,
không epsilon. Run02 controls PASS, interrupted M01/ref8 do O(n²) conversions;
hoist immutable array và6 independent processes, giữ toàn bộ historical artifacts.

Run03 code60a1032: **PASS**, 9/9 p_sw bitwise,18 C1–C3 identities, C4 toy independent
aggregation/tie PASS,60 C5 zero entries và6 WD GS_M1 zero entries exact. 15/15
cell-level BOUNDED,12/12 adjacent pairs PASS; **dt cuối=1/240 s (ref2)** cho cả ba ô.
336 tests/11 mutants PASS; CSV replay cùng pick;3 M01 JSON +4 control artifacts
trùng từng byte với run02. [Report](../../results/lessons/l3_4/report.md),
[verification](../../results/lessons/l3_4/verification.json), [plot](../../results/lessons/l3_4/refinement.png).

DL-053 khóa dt cho các bước sau, không xác nhận continuum hoặc35 ô còn lại.
A04 **chưa chạy, V9 chưa gửi**; khi đủ gate cần kiểm pair1/120→1/240 từng ô.
Không chấm forecasts/H1/null/held-out trong A01; exposure calibration cập nhật.
Không tự ghi Understanding PASS; T05 author-writing/L8/P0-V10 vẫn mở.

## 13. Sau review mô phỏng — DL-054 (27/10/2026)

Tác giả cung cấp bản review chỉ xem remotef72306f (không có A01) và yêu cầu bỏ
chặn để triển khai L3.5. [Nguồn/provenance](../reviews/2026-10-27_pre_A04/provenance.json)
giữ đúng tác giả/phạm vi của review; không chuyển thành phản hồi GVHD thật.
[Intake](../reviews/2026-10-27_pre_A04/intake.md) phân biệt nhận xét đúng, điểm đã
được A01 local xử lý và đề xuất chưa adopt. 51artifact hashes/guards được kiểm lại,
không rerun336tests hoặc20.000toy của reviewer trong nhiệm vụ này.

**V9 WAIVED_BY_AUTHOR** mở việc tiếp tục L3.5. [Preflight](../lessons/L3.5_preflight.md)
liệt kê phần triển khai/prereg còn lại; không đồng nghĩa đã chạy38ô hoặc chấm card.
Ref4/FV/flip mass/cheap-kill miền là đầu vào cần chốt trước run, không sửa card
theo nhận xét. A05-F/held-out và Phase4/P0-V10 tiếp tục theo các gate cũ.
