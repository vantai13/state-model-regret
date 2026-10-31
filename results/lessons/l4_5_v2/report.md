# L4.5 (v2) — đã thực hiện research task, 31/10/2026

Người phụ trách: **Doan Van Tai**. AI soạn/thực hiện theo ủy quyền tiếp diễn và
lệnh thực hiện lesson; không giả tác giả tự viết, tự ký hoặc Understanding PASS.

**DL-117: park SUB và gói CF-v2, chọn 0 card mới cho hướng hiện tại.** Đây là
quyết định đổi thiết kế evidence, không phải kết luận SUB FAIL hoặc card v2 sai.
Lesson này không tạo scientific evidence mới, G1 giữ nguyên.

## A. Đã thực hiện

- Chọn phương án khuyến nghị (a): giữ 10/76 SUB keys làm discovery đã thấy.
  Kết thúc process group257934 khi đang SIGSTOP, không SIGCONT; không tính nốt
  66 keys. Hai calls chưa lưu kết quả bị hủy; toàn bộ30 native level rows và
  10 comparisons đã lưu giữ nguyên. Exit137 là park có chủ đích, không engine BUG.
- Park270 CF-v2 parameters/gói MV–SH để chỉ xem lại riêng như kiểm phụ; không CF
  outcomes, thay card/alpha, mở sealed hoặc tự gỡ P0-V10 cho gói cũ.
- Ghi DL-117; lập bảng giữ/park, bản diễn giải học tập8 dòng,3 câu personal artifact
  và5 self-check answers do AI soạn. Chỉnh lý phát biểu median/power, log-measure,
  exact/continuous và0/48 trong lesson; raw lesson không bị sửa.
- Tạo PHASE_4_v2 tối thiểu với §0.1 trạng thái thật và lộ trình L4.6–4.9;
  cập nhật README/progress/index/AGENTS. Không đóng toàn Phase4, chưa chạy L4.6.

## B. Đã chạy và kiểm

Các kiểm tra read-only thực tế: verify_run cho L44_A1/L43_A1_SV/SUB_PROBE/
L44_A3/SUB_BOX, verify A2, rules_adopted của screening, verify_saved_comparison
cho 10 SUB keys; so diff với commit78c3210, kiểmprocessgroup và các arithmetic
facts từ dữ liệu đã lưu. Có log ở verification.log và số đo ở verification.json.

```bash
git diff --numstat
git diff --check
```

**PASS**:5 prereg/source runs, A2 source/history, screening rules và frozen
engine/card/contract snapshots khớp; protected files không đổi. Chỉ thêm nội dung
và pointer, không xóa lịch sử hoặc sửa frozen bytes. Không thêm test/runner/gate
framework hoặc chạy lại880 unit tests cho thay đổi tài liệu/process này.

**PASS**:không còn live worker của job cũ;10 complete keys vẫnPASS,30 levels giữ
nguyên; không xuất hiện full_summary/rho_freeze/manifest/SUB trial. Không native
engine call hoặc outcomeCF mới. Việc kiểm là validation trạng thái, không nâng
SV/SUB thành confirmation hoặc numerical coverage toàn miền.

## C. Kết quả đo/đối chiếu trực tiếp

| Đại lượng | Kết quả |
|---|---|
| SUB hoàn tất được giữ |10/76 keys,10PASS,30 native level rows|
| SUB chưa có kết quả hoàn chỉnh |66 keys (gồm2calls dở đã bỏ)|
| Live process job cũ |0|
| SUB screen / verdict |Chưa chạy / NOT_EVALUATED|
| Card mới hiện hành |0,dođổi design|
| CF-v2 |270parameter rows,park,0new outcomes|
| SV-plus median GS/Cref trên448 READY |0.971841365%|
| SV MEETS fraction all / resolved |48.106904% /49.090909%|
| SV-minus GS/Cref min/median/max |−0.051785% /0.060593% /0.697799%|
| Toy log-uniform mass[.2,1] trong[.2,3] |59.431613%,không 40%|

Counterexample cho median equivalence không điều kiện: toy[0%,1.5%],threshold1%
cho fraction≥threshold=.5 nhưng sample median=.75%<1%. Công thức đúng tổng
quát là p_epsilon=1−F_Z(epsilon−); ties/atoms/median không duy nhất cần nói rõ.
FAIL_SCREEN vẫn là luật power/haircut/unresolved; không đồng nhất với median.

SV FAIL_SCREEN và MV baseline recovery≈86% là kết quả **cũ đã được giữ**, không
phải finding mới của lesson. Giữ mọi numerical flags/limitations, không gán
native coverage cho1376 pilot points hoặc tuyên bố dữ liệu thích nghi đại diện
measure của card. Không statistical CI hoặc figure mới trong phiên này.

## D. Files thực có

- Quyết định: `notes/02_decision_log.md`, DL-117.
- Bảng giữ/park, learning note, §0.1 và lộ trình:
  `notes/phases/PHASE_4_v2.md`.
- Header/pointer: `notes/phases/PHASE_4.md`.
- State/action record: `results/lessons/l4_5_v2/parking.json`.
- Raw lesson, verification log/JSON và báo cáo này: `results/lessons/l4_5_v2/`.
- Raw SUB vẫn ở `results/lessons/l4_5/sub_native/`; SV trial gốc và pause/checkpoint
  cũ không đổi. Mọi nguồn code/config frozen vẫn ở vị trí trước đó, không filecode
  nào được chỉnh trong nhiệm vụ này.

## E. Giới hạn và bước tiếp

Không tìm thấy PHASE_4.md v1.1 hoặc PHASE_4_v2 gốc trong repo và thư mục đã kiểm.
Vì vậy header được tạo ở **pointer mới**, §0.1 nằm trong bản triển khai tối thiểu
có nhãn nguồn rõ; không giả đã sửa toàn văn/Phụ lục B hoặc Master Plan gốc.

Bước tiếp là L4.6 tách nguồn trên dữ liệu đã có; D22/native audit, mechanism,
realism và freeze/held-out condition vẫn chưa thực hiện. Không auto-resume SUB
hoặc chạy gói CF vì snapshot cũ có lệnh resume. Muốn xem lại cần quyết định
nghiên cứu mới rõ ràng. Learning artifact củaAI không thay author self-writing,
human review hoặc author Understanding; G1/novelty/realism không tự nâng.
