# Kiểm tra và giải thích L3.7 / A05-T

Người phụ trách: **Doan Van Tai**. Ngày kiểm tra: 28/10/2026.
Đây là review có AI hỗ trợ theo yêu cầu tác giả, không phải phản hồi của GVHD/người đọc thật.
HEAD được kiểm: `ec022d1de4aebc5761d10df558d06b186c963547`.

**Kết luận:** trong phạm vi code, lịch sử commit, dữ liệu lưu và 43 test đã kiểm,
chưa tìm thấy lỗi thực thi làm đổi verdict. Thí nghiệm hợp lệ theo các cổng đã khóa;
giả thuyết chính không đạt SUPPORT. Hai điều này hoàn toàn có thể cùng đúng.
Không chạy lại engine, không fit lại model và không đổi ngưỡng/metric/phạm vi test.

## Bạn đang làm gì và vì sao?

Dự án xem quyết định routing chịu ảnh hưởng thế nào khi trạng thái đầu vào và model
dự báo có sai lệch. Engine tính chi phí trong bốn trường hợp: L00 chưa sửa hai thứ,
L01 sửa model, L10 sửa state, L11 sửa cả hai. C_ref là L11 của chính ô đang xét.
Chi phí có đơn vị packet·s; thấp hơn tốt hơn. Chênh lệch giữa các trường hợp cho biết
sửa từng thành phần đem lại lợi ích gì và hai cách sửa tương tác thế nào.

L3.5 dùng 38 ô chính để khám phá. L3.6 khóa hai cách **dự báo các lợi ích sửa**:
H0 dùng feature tọa độ, H1 dùng feature động học theo thiết kế đã chọn. Mỗi model
có 12 hệ số, 2 candidate, 2 start và cùng quyền dùng λA theo D25(ii).
H0/H1 là hai bộ dự báo; chúng khác với M0/M1 là trạng thái model trong bốn trường hợp.
H1 dự báo kém không đồng nghĩa việc sửa model vô ích.

L3.7 tính kết quả thật cho ô mới để so dự báo đã khóa với sự thật. Mục đích là kiểm
khả năng khái quát hóa, tránh nhận một pattern chỉ khớp dữ liệu đã xem làm quy luật.

## Đã chạy gì?

Run gốc do Claude thực hiện theo ủy quyền được ghi trong DL-059, không phải run mới
của phiên review này. Mở R01–R08 và R11/R12, mỗi ô tính ở dt=1/120 và 1/240 s:
**10 ô × 2 mức = 20 cell-level**. Mỗi cell-level chứa cả bốn chi phí L00/L01/L10/L11.
R09/R10 không mở outcome do D đã khóa thấp hơn margin; trục h=4 s chưa được test.
Không có random sampling; seed=null, không có sampling CI/p-value.

Run bắt đầu 08:33:04, kết thúc 08:33:27 ngày 28/10/2026 (+07), wall time **22,6443 s**,
6 worker. Quyết định mở đã commit lúc 08:32:50. Freeze, runner, decision, run,
output và báo cáo có đúng thứ tự trong lịch sử được kiểm.

## Số đo và cách đọc

MAE là sai số tuyệt đối trung bình trên (G_S, G_M, Γ)/C_ref, với trọng số đều.
MAE thấp hơn tốt hơn; d=MAE0−MAE1 dương nghĩa là H1 có MAE thấp hơn.
Đơn vị bảng: **điểm phần trăm C_ref**. Đây không phải phần trăm cải thiện tương đối.

| Nhánh | Kết quả đo | Verdict đã khóa | Ý nghĩa |
|---|---|---|---|
| Nội suy, 8/8 ô | MAE0 [0,689644; 0,689708]; MAE1 [0,442608; 0,442673]; d [0,247035552637; 0,247035552739] | **WEAKEN** | H1 tốt hơn nhưng chưa đủ margin 0,25 |
| Ngoại suy h=12 s, 2/2 ô | MAE0 [2,046199; 2,046684]; MAE1 [2,187950; 2,188434]; d=−0,141750547776 | **FALSIFY** | H1 kém H0 ở hai ô này |
| K5, R03/R04 | R03 đứng; R04 G_M/C_ref [0,527926377014; 0,527926377069]% >0,5% | **DOES_NOT_STAND** | Luật mở rộng bị phản ví dụ R04 |
| C1, R05–R08 | Cả bốn đứng; G_M danh nghĩa bằng 0 | **STANDS** | Chỉ xác nhận equivalence ≤0,5% ở bốn ô này |

Ở nội suy, H1 giảm MAE tương đối khoảng **35,82%** so với H0, nhưng luật chính đòi
giảm tuyệt đối ít nhất **0,25 điểm % C_ref**. Mức đo được thiếu khoảng 0,00296445
điểm %. Độ rộng enclosure của d chỉ khoảng 1,016×10⁻¹⁰ điểm %, nên không có căn cứ
đổ chênh lệch này cho làm tròn hoặc đổi WEAKEN thành SUPPORT.

Các enclosure mô tả sai số số học có điều kiện trên input bounds của slot-model;
không phải khoảng tin cậy thống kê, không bao gồm mọi sai lệch mô hình hoặc sai số dt.
Hai mức dt được kiểm riêng. Prereg không đặt tiêu chí đủ chính xác tuyệt đối cho H0/H1;
ε_E=0,5% là ngưỡng equivalence của gain, không phải luật PASS/FAIL của MAE dự báo.

Ví dụ dễ thấy: R04 có L00=527,692242 và L01=524,923180 packet·s. Sửa model giúp giảm
**2,769062 packet·s**, tương đương **0,527926% C_ref**. K5 từng đoán lợi ích này
≤0,5%; thực tế cao hơn. Đây là phản ví dụ khoa học, không tự nó là lỗi lập trình.
Quan sát M19–M22 của A04 vẫn giữ nguyên, chỉ luật suy rộng không đứng.

## Tốt, tệ và tốt nhất được hiểu thế nào?

Đối với **giả thuyết PC4**: SUPPORT tốt nhất theo tiêu chí đã cam kết khi toàn bộ
khoảng d≥0,25; WEAKEN nghĩa là cải thiện dương nhưng chưa đủ; FALSIFY nghĩa là
H1 không thắng H0 theo luật khoảng; INCONCLUSIVE nghĩa là chưa đủ cơ sở chấm.
Kết quả ngoại suy phải báo riêng, không gộp với nội suy để có một điểm chung đẹp hơn.
SUPPORT cũng không chứng minh H1 tuyệt đối chính xác, cơ chế đúng hoặc áp dụng cho mạng thật.

Đối với **chất lượng nghiên cứu**, điều tốt là chạy đúng thiết kế, giữ kết quả bất lợi,
phân biệt điều đo được với điều suy luận và thu hẹp claim. Kết quả hiện tại làm được
các việc đó. Điều tệ sẽ là đổi margin sau khi thấy 0,247, dùng lại 10 ô để tự nhận
validation độc lập cho model đã chỉnh, hoặc bỏ nhánh ngoại suy/K5. Không tìm thấy
các thao tác này trong phạm vi repo được kiểm.

## Kiểm tra thực tế trong phiên review

- **43/43 test PASS**, 0 fail/error/skip, 1,697 s. Đây là bộ test liên quan được chạy
  lại, không phải xác nhận mới toàn bộ 391 test được báo ở run trước.
- `verify_frozen()` và gate quyết định commit PASS trước khi tạo các file review.
  Preflight bị từ chối vì output one-shot đã có: đây là **guard hoạt động đúng**.
- Hash: **29/29 file output**, console SHA, **22/22 file nguồn freeze/runner** cùng
  prediction/discrimination hash khớp. Engine/card/A01/A04 không đổi so với receipt.
- 20 raw engine payload khớp chính xác grading_input; đúng 10 ID×2 dt; không có raw
  R09/R10 trong run. Đã kiểm schema/nguồn định danh trong code; không suy từ chuỗi
  `R10` đơn lẻ vì đó còn là khóa regret (nhánh 1,0).
- Dữ liệu lưu: **20/20 BOUNDED**, numeric gates đạt, **10/10 cặp dt đạt**;
  max thay đổi giữa hai dt=**0,0116998% C_ref**, dưới dung sai 0,25%.
- p_sw: file run ghi **20/20 bitwise match**. Review kiểm các record và hash,
  không tính lại p_sw/D bằng engine.
- Rescorer sẵn có: agreement PASS. Script review độc lập dùng Fraction để tính lại
  cả MAE0, MAE1, paired d, K5/C1, headroom labels, numeric/precision/dt gates;
  **tất cả khớp chính xác** verdict lưu.

Lệnh thực tế của phiên review:

```bash
.venv/bin/python -m pytest tests/test_a05_math.py tests/test_a05_freeze.py tests/test_a05_test.py -q --junitxml=/tmp/l37_review_tests.xml
.venv/bin/python -m experiments.A05_test.rescore results/A05_test/20261028_01
.venv/bin/python results/reviews/l3_7_20261028/audit_saved_run.py
.venv/bin/python results/reviews/l3_7_20261028/plot_results.py
```

Ngoài ra gọi read-only `verify_frozen`, `require_committed_decision`, `preflight`.
Lệnh in diagnostic đầu tiên dùng nhầm khóa `commit`, gặp KeyError; sửa thành
`decision_commit` rồi kiểm lại PASS. Đây là lỗi lệnh kiểm tra của phiên review,
không phải lỗi run A05-T. Không gọi runner A05-T trong phiên này.

## Sai sót/cách diễn đạt cần sửa trong tài liệu

1. **Lesson Part 2, dòng 18: “R00/C_ref<0,5% thì mọi contrast đều nhỏ” là sai nếu
   nói mọi contrast.** Headroom này chặn trên G_M và tổng gain, nhưng không chặn
   toàn bộ Γ/G_M|S1 hoặc độ lớn |G_S|. Phản ví dụ đại số minh họa, không phải ô
   thực nghiệm mới: (L00,L01,L10,L11)=(100,4;100,4;101,5;100). Khi đó R00/C_ref=0,4%,
   G_M=0 nhưng Γ/C_ref=1,5% và G_S/C_ref=−1,1%. Nhãn headroom của R03 trong code
   dùng G_M nên kết luận K5 hiện tại không bị lỗi câu giải thích này.
2. **Lesson Part 2, dòng 136: “H0/H1 chỉ khác intercept của τ; theta xác nhận”
   không khớp theta hiện hành.** Cả bốn hàng beta đều khác, feature và scaling cũng
   khác. Chẩn đoán level/shape cho thấy lợi thế có thành phần dịch mức lớn; không
   chứng minh nguyên nhân chỉ do τ. Không có knockout riêng trong A05-T.
3. **Báo cáo hiện hành nói C1 yếu vì hình thành sau A04:** cần nói chính xác hơn.
   C1 được khóa trước A05-T nên vẫn có giá trị kiểm tra held-out. Điều hạn chế là
   n=4, phạm vi hẹp và event equivalence vốn phổ biến (36/38 ô discovery). Heuristic
   (36/38)^4≈0,8055 không phải xác suất thật vì các ô không phải mẫu IID ngẫu nhiên.
   Không kết luận cơ chế hoặc toàn vùng chỉ từ bốn ô đứng.

## Điều còn chưa xác nhận và bước tiếp theo

Không có kỳ vọng tự viết trước run hoặc người đọc thật trước A05-T; lesson khuyến
nghị nhưng không bắt buộc hai việc này. Không điền hồi tố thành đã làm. L8,
P0-V10, T05 author-writing/Understanding và điều kiện Phase4 vẫn theo trạng thái
repo. Đã chạy code không chứng minh bạn đã tự hiểu hoặc có GVHD duyệt.

Giới hạn: 10 điểm thiết kế có chủ ý, Gaussian/rho=0 và các feature xấp xỉ;
enclosure có điều kiện. Chưa chứng minh tổng quát, cơ chế, hiệu quả mạng thật hoặc
hành động ngoài lịch sử/file repo. Run hiện tại không có bằng chứng đủ để nói
H0 đã đủ tốt, H1 đúng, hay động học không bao giờ hữu ích.

Bước hợp lý là L3.8: tổng hợp claim đã thu hẹp để tác giả quyết Gate A; không tự
động GO Phase4. Nếu muốn sửa H1, dùng kết quả này cho discovery và lập một test mới
độc lập theo roadmap; không sửa dự báo rồi gọi 10 ô đã thấy là held-out mới.

## File của review

- `audit_saved_run.py`: kiểm dữ liệu đã lưu, không import/call engine.
- `audit.json`, `cells.csv`: check và số đo tính lại, 10 ô đã mở.
- `audit.log`, `preflight.log`, `rescore.log`, `targeted_tests.xml`: bằng chứng kiểm.
- `plot_results.py`, `plot.log`, `results_comparison.png`, `results_comparison.pdf`: biểu đồ từ số đo lưu.
- Báo cáo này: `report.md`.

Run gốc vẫn ở `results/A05_test/20261028_01/`; cấu hình gốc
`experiments/A05_freeze/config.json`; quyết định `experiments/A05_test/decision.json`;
báo cáo gốc `results/lessons/l3_7/report.md`. Review chỉ thêm file trong thư mục này,
không sửa artifact gốc và chưa commit/push các file review.
