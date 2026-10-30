# Rà soát các điều kiện còn mở — L3R.7 và các lesson trước

Người phụ trách: **Doan Van Tai**. Kiểm tra ngày30/10/2026,09:22 giờ Việt Nam.
Chỉ đọc repo, kiểm hash và hỏi trạng thái GCP; không chạy mới engine/MC, không
đổi contract/card, không đóng hoặc miễn gate. [Số kiểm thực tế](verification.json).

## 1. Điều đang chặn L3R.7

Nút thắt nghiên cứu chính là **numerics freeze v1.3.1 chưa đóng**. Trở ngại
hạ tầng hiện tại là chưa vào được GCP để lấy kết quả/checkpoint của full03.
Nhiều mục chưa có bên dưới là các bước phụ thuộc nối tiếp, không phải các lỗi
độc lập hoặc bằng chứng rằng mọi lesson trước đều thất bại.

| Mục | Bằng chứng hiện tại | Điều kiện để đi tiếp |
|---|---|---|
| Trạng thái full03 | Không có final summary/export03 trong repo; snapshot cuối29/10 ghi120lượt hoàn tất,3ca còn chạy ở vòng đầu | Khôi phục quyền truy cập, kiểm output và process thật, lấy checkpoint/log; chưa tự chạy lại từ đầu |
| Accuracy/audit closure | Chưa có kết quả full global refinement/coverage/timing được kiểm và khóa | Kiểm toàn bộ schedule đã đăng ký; R1 và arithmetic/validity, coverage, moment/tail, runtime; ghi đúng PASS/HOLD |
| Freeze v1.3.1 | Chưa có spec `notes/design/numerics_v1_3_1.json`, receipt hoặc tagv1.3.1 | Chỉ tạo khi có đủ evidence; giữ nguyên tagv1.3 |
| Dry-runB | DEFERRED; A trên số giả và C refusal đã làm | Dùng engine đã khóa trên discovery/calibration đã thấy qua format→engine→scorer; không dùng mẫu thử từ CF |
| n,seed,prereg và CF list | n/root cònnull; luật chọnn đã được tác giả duyệt,B48CPUh đã có | Từ timing bundle/p95 và fixedcost đã đo áp luật; commit n/seed/prereg rồi sinh list một lần |

Các candidate cho S1/tail/moment đã có implementation trong
`experiments/R3R_08_population_numerics/`; chúng **chưa adopted/frozen**, không
phải chưa viết gì. Luật chọnn không cần hỏi lại tác giả. Hypothesis cards v1
và contractv1.3 đã khóa, kiểm hash hiện tạiPASS21/10file;108numericalsourcefiles
cũng khớp prereg03. Đây là integrity check, không thay full numerical readiness.

Nguồn: [completionL7](../../../../notes/phases/L3R_7_completion.json),
[execution gates](../../../../experiments/R3R_07_confirmation/gates.py),
[candidate scope](../../../../notes/design/population_numerics_v1_3_1_candidate.md).

## 2. GCP vừa kiểm và giới hạn điều biết được

API báo VM `dt4n-research-01` **RUNNING**, n2-standard-8. Theo timestamps API,
quy đổi Asia/Saigon: dừng29/10 lúc**23:53:31**, bật lại30/10 lúc**09:19:08**.
[Bản trả API](gcp_state.json). SSH mới thử trả `Connection refused` ởport22.
Chưa xác minh được job hoặc các file cuối trongVM; không biết nguyên nhân VMdừng.

Các process chạy thủ công không giữ nguyên qua một lần VMdừng. Vì vậy không
được suy rằng full03 đã chạy liên tục suốt đêm. Có tựresume hay không phải kiểm
trongVM; localcollector đã được ghiNOT_RUNNING ở kiểm tra trước. Kết quả đã
ghi xuống disk có thể còn; chưa được đọc để xác nhận mức nào đã hoàn tất.

## 3. Vì sao mất nhiều giờ

L3R.7 là thiết kế phép kiểm chứng. Công việc nặng được gộp vào nó là hoàn thiện
và kiểm chứng engine/numerics, vốn tài liệu cho phép tách thành L3R.6b.
Việc gộp này và báo progress chỉ theo vòng đầu đã làm khối lượng khó hiểu.

- 114calibrationrecords,111tọa độ vật lý khác nhau; mỗi ca3mức ban đầu, tối đa7
  mức qua2bước làm mịn đã khai: tối đa**798populationevaluations**, không phải
 798regimes độc lập. Không nhất thiết phải chạy mọi mức nếu đóng được sớm.
- Số lẻ của rate làm lattice có hàng nghìn thành phần; posterior cần chuyển sang
  interval80digits khi forward bound của phép tính nhanh chưa đủ. Cùng một bài
  toán nhưng runtime mỗi ca rất khác nhau.
- Trong full03, log đã ghi `CAL_CORNER_001`3,532CPU-s;
  `RATE_SH_BASE_K1_10_H16`140,953CPU-s;
  `RATE_SH_BASE_K3_H16`723,242CPU-s, tức khoảng12phútCPU.
- Có2lỗi triển khai phải sửa: dispatch nhầm namespace ởfull01, và thiếu precision
  fallback cho posterior ởfull02. Không coi các record lỗi làPASS; giữ cảđợtcũ.
- Đợt full02 dừng vì `fast posterior error exceeds1e-8`, không vìCPU/RAMlimit;
  RSS mẫu lớn nhất toàn đợt165,313MiB. Không suy từ đó rằng mọi cấu hình tương lai
  luôn đủ tài nguyên. Những CPUlimit ở các candidate cũ vẫn giữ trong lịch sử.
- Trần calibration12CPUh là budget, không phải thời gian đã dùng hoặc ETA.
  B48CPUh là budget riêng của confirmation tương lai. Không cộng thành lời hứa
  số giờ chờ. VMstop và thiếu SSH là gián đoạn riêng với thời gian phép tính.

Nguồn: [prereg03](../../../../experiments/R3R_08_population_numerics/prereg_03.json),
[telemetry03](../full_numerics/telemetry03.jsonl),
[report02](../full_numerics/report02/verification.json), DL-087–088.

## 4. Các lesson trước còn gì

| Lesson | Phần đã có | Mục còn mở hiện còn liên quan |
|---|---|---|
| L3R.1 | Recount và hồ sơ pilot hoàn tất kỹ thuật | Understanding chưa có xác nhận mới; không có technical blocker riêng còn phải làm lại recount |
| L3R.2 | Estimand/T07 và tests hoàn tất kỹ thuật | Understanding/read-back cònOPEN; audit engine là việc chuyển sangL3R.3 |
| L3R.3 | Audit/tests/mutation/MC đã chạy; không xác nhận bug thay số pilot trong8regimes | GateHOLD: globalnumerics/error accounting chưa đóng, read-back cònOPEN. Các mứcK320 cải thiện ca cũ không tự là globalfreeze |
| L3R.4 | Screen và đọc các nguồn đã duyệt đã thực hiện | RealismHOLD_UNSOURCED:216ID/210tọa độ đều thiếu dải nguồn tương thích ở hai bối cảnh. Thiếu evidence không phải chứng minhOUT/phi thực tế |
| L3R.5 | Contractv1.3 đãtag vàkhóa | Numerics cònDEFERRED; D22 mới có định nghĩa/golden checks, productionimplementation vàaudit cònDEFERRED; carry realism/human |
| L3R.6 | Hai primarycardsMV/SH đãkhóa | Carry numerics/D22/realism/human; check7 bằng lời tác giả vàUnderstanding cònOPEN. Không cần tự mở lại card để cứu kết quả |

Các completionJSON là snapshot ở thời điểm đóng lesson. Ví dụ chữDRAFT ởL3R.2
đã được contracttag ởL3R.5 thay thế; không đếm nó là một blocker hiện tại khác.
Nguồn: `notes/phases/L3R_1_completion.json` tới `L3R_6_completion.json`,
[auditL3R.3](../../l3r_3/report.md), [screenL3R.4](../../l3r_4/report.md).

## 5. Điều kiện chủ yếu chặn Phase4, phân biệt với L3R.7

- **D22 implementation vàaudit:** tách phần giá trị backlog hiện tại khỏi phần
  biếtmode, để diễn giải đúng state repair. Đây là thực thi chưa có, không phải
  chỉ đổi một nhãn thànhPASS. Chặn Phase4, không chặn việc sinh CF list sau numerics.
- **Realism:** cần dữ liệu/nguồn phù hợp về tuổi backlog, horizon/hold, tải và
  burst ở cùng cửa sổ, buffer, actiondelay; hoặc disposition scope được ghi ởGate3R.
  Code chạy thêm không tự tạo evidence thực tế bị thiếu.
- **P0-V10 vàL8:** người thật đọc/phản biện contract và priorboundary/relatedwork;
  chưa có record đáp ứng. AIreview không thay được. Có thể tổ chức chung buổi nếu
  đủ phạm vi; không bắt buộc chỉGVHD. Chặn Phase4 theo rules hiện tại.
- **Gate3R/L3R.8:** chưa có quyết định mở Phase4 và bộ freeze/prereg đầy đủ. Đây là
  bước còn phải thực hiện sau thiết kế, không phải codebug củaL7.

**Ownership cònOPEN:** Understanding/read-back mới, phần tự viết đầu closeout
Phase1/2, và các bản Phase3 được viết theo ủy quyền chưa là self-writing evidence.
T05read-back cũ đãauthor-attested; mụcT05author-writing vẫnOPEN, chủ yếu chặn
promotion engine sang`src/`, không tự chặn việc hoàn thành kỹ thuật L3R.7.
OPEN về Understanding là thiếu record đủ điều kiện, không kết luận tác giả không hiểu.

**Không còn chặn theo nghĩa cũ:** memoV9 trướcA04 đãWAIVED_BY_AUTHOR ởDL-054.
PC4WEAKEN/FALSIFY vàK5bịphảnvídụ là kết quả Phase3 đãchốt, không phảiHOLD cần
chạy lại để có kết quả thuận lợi. A05-T vẫn không được tự chạy lại.

## 6. Thứ tự xử lý có căn cứ

1. Kiểm và khôi phục truy cập GCP, lấy output/checkpoint03; xác định còn thiếu gì
  trước khi quyết resume hoặc rerun theo đúng version/deviation.
2. Đóng audit/numerics với evidence thật hoặc báoHOLD có nguyên nhân; nếu đủ thì
  freezev1.3.1, dry-runB, chọnn, cấpseed và sinh danh sách một lần.
3. Làm song song phầnD22, realism và người đọc thật. L3R.8 quyếtGate3R trướcPhase4.

Không cần chạy lại toàn bộ lesson cũ. Không có thí nghiệm mới, nguồn paper mới,
thay đổi giả thuyết/ngưỡng hoặc miễn gate nào trong lần rà soát này. Không tạo chart.
