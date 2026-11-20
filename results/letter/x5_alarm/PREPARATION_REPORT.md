# X5 — báo cáo chuẩn bị

Người phụ trách: **Doan Van Tai**. Triển khai theo ủy quyền của tác giả, đúng
`DESIGN_X5_ALARM.md` và `CARD_X5.md`; không đồng nhất công việc AI với tác giả tự thực hiện.

**Cổng step0: NOT_ENOUGH_SIGNAL. Dừng theo thẻ.** Không chạy pilot, truth hoặc
score; không tạo lock. Không commit, push hoặc SSH. Không chỉnh file đã có khi
bắt đầu nhiệm vụ. CARD_X5, các file X4b và nguồn nhập được giữ nguyên.

## Step0 đã đo

Đúng 60 bản ghi test-S của X4b, seed 7000001, namespace `X5|regime|date`.
M=512, N tối đa 32, MIN_ALARMS=8, K=64; h=300/600/900/1200/1800/3600/7200 s.
Capacity và slope pooled train được nhập nguyên từ X4b. Ngưỡng cảnh báo là
0,001 × capacity của e*, đơn vị Mbit, không dùng capacity đồng nhất thay thế.

| Regime | Bản ghi | e* | Ngưỡng Mbit | Cảnh báo / ứng viên | ALARM_RARE | Không RARE |
|---|---:|---:|---:|---:|---:|---:|
| NEWB1 | 8 | 27 | 2,107079186150075 | 0/4096 | 8 | 0 |
| NEWB2 | 29 | 21 | 9,126508697965683 | 0/14848 | 29 | 0 |
| NEWB3 | 23 | 27 | 1,9538802060727753 | 517/11776 | 22 | 1 |
| Tổng | 60 | — | — | 517/30720 = 1,682943% | 59 | 1 |

Chỉ ba bản ghi có cảnh báo; 57 bản ghi còn lại đều 0/512:

| Regime | Ngày | Cảnh báo / 512 | Chỉ số được giữ | Trạng thái |
|---|---|---:|---|---|
| NEWB3 | 2005-06-17 | 2 | Có lưu 2 chỉ số để kiểm tra; không tính quyết định | ALARM_RARE |
| NEWB3 | 2005-07-26 | 3 | Có lưu 3 chỉ số để kiểm tra; không tính quyết định | ALARM_RARE |
| NEWB3 | 2005-08-29 | 512 | 0–31, đúng thứ tự | SELECTED |

Share bất đồng **Hybrid ≠ Stationary phía tươi**, từng regime × h:

| h (s) | NEWB1 | NEWB2 | NEWB3 |
|---:|---|---|---:|
| 300 | NA, không có bản ghi không RARE | NA, không có bản ghi không RARE | 0/32 = 0% |
| 600 | NA | NA | 0/32 = 0% |
| 900 | NA | NA | 0/32 = 0% |
| 1200 | NA | NA | 0/32 = 0% |
| 1800 | NA | NA | 0/32 = 0% |
| 3600 | NA | NA | 0/32 = 0% |
| 7200 | NA | NA | 0/32 = 0% |

Hai phía stale_300 và stale_900 cũng bất đồng **0/32 tại từng h** trên cùng
bản ghi NEWB3. Phía tươi gộp bảy h: 0/224 bất đồng. Share tie M0 tươi:
**0/32 tại từng h**, gộp **0/224 = 0%**. 224 là instance × h trên 32 instance
của một ngày, không phải 224 ngày/thử nghiệm độc lập. NEWB1/NEWB2 không có mẫu
quyết định hợp lệ để tính share; NA không được đổi thành 0%.

Không regime nào có ít nhất 5 bản ghi không RARE. Regime duy nhất có quyết định
cũng không đạt share bất đồng 5%. Do đó cả hai điều kiện của cổng đều không đủ.
Đây là kết quả screen theo thiết kế, không phải kết luận T1–T4 hay bằng chứng về
regret của M0/Hybrid. Dự báo cổng qua trong thẻ không xảy ra.

## Thời gian và các bước không chạy

- Preflight dùng NEWB3/2005-07-19, work proxy đầu vào cao nhất: 34,906267500 CPU-s,
  34,907421899 wall-s. Dự phóng step0 local 292,349658404 s = 4,872494 phút với
  8 worker, dưới giới hạn 40 phút. Kết quả này được dùng lại, không mô phỏng lại.
- Step0 thực tế: **330,236380892 CPU-s** cộng qua các bản ghi,
  **109,993047051 wall-s**, 8 worker local. Không có rollout tương lai để tính
  regret/C_ref ở test seed; warmup, posterior và mean forecasts thuộc step0.
- Pilot seed 7000003: **NOT_RUN**, vì cổng yêu cầu dừng. Không có CPU pilot hoặc
  dự phóng CPU-h truth từ pilot; không thay bằng số giả định.
- Lock: **NOT_CREATED**. Verify-lock không chạy khi không có lock.
- Truth/score: **NOT_RUN**. Không có raw truth, card verdict thực nghiệm,
  `card_verdicts.json` hay `REPORT_X5.md`. Scorer chỉ được kiểm bằng dữ liệu tổng hợp.

## Kiểm chứng

Sau khi source `.venv/bin/activate` và `experiments/explore_ctmc/env.sh`, mọi
lệnh Python số học đặt `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR` và `MPLCONFIGDIR`
vào `results/letter/x5_alarm/build/` để tránh ghi vào khu vực khác.

Các lệnh thực tế chính:

```bash
python3 -m pytest -q -p no:cacheprovider --basetemp=results/letter/x5_alarm/pytest_initial tests/test_x5_alarm.py tests/test_x4b.py
python3 -m pytest -q -p no:cacheprovider --basetemp=results/letter/x5_alarm/pytest_selection_fixed tests/test_x5_alarm.py tests/test_x4b.py
python3 -m pytest -q -p no:cacheprovider --basetemp=results/letter/x5_alarm/pytest_regression tests/test_x5_alarm.py tests/test_x4b.py tests/test_x4b_card.py tests/test_x4b_truth.py
bash -n experiments/letter/x5_gcp.sh
python3 -m experiments.letter.x5_alarm configure
python3 -m experiments.letter.x5_alarm step0 --workers 8
python3 results/letter/x5_alarm/audit_step0.py
git diff --exit-code
```

- Lượt đầu: **2 FAIL, 81 PASS**. Fixture của test selection dùng mode ngoài miền
  [-1,1], bị helper utilization của X4b từ chối đúng. Đã sửa fixture của file
  mới, không sửa helper/source X4b; giữ log ban đầu.
- Sau sửa fixture: **83 PASS / 4,21 s**.
- Regression cuối: **118 PASS / 4,26 s**, gồm giảm bitwise về B.decision_record
  trên một bản ghi thật, chọn/cắt fresh và stale cùng chỉ số, biên ALARM_RARE,
  cổng, T1 GAIN/LOSS/UNRESOLVED/NOT_EVALUABLE, SE qua ngày ddof=1, T2–T4 hai phía
  ngưỡng, guard lock/stage/count/seed và test X4b/card/truth hiện hữu.
- `bash -n`: **PASS**; script GCP không được thực thi.
- Audit độc lập từ saved NPZ, không import module experiment/scorer:
  **60/60 bản ghi, 30720 candidate queues, 4032 giá trị decision/tie và
  21 nhóm regime × h × side PASS**; gate/count/share/checksum đều khớp.
  Lần đầu audit gặp `TypeError` do ép array NPZ kích thước 1 thành float trên
  NumPy hiện tại; đổi riêng audit sang `.item()`, chạy lại audit đọc file.
  Không chạy lại simulation, không sửa source đã dùng cho step0 hoặc raw NPZ.
- 688 file bảo vệ được đối chiếu SHA-256 với snapshot trước triển khai; kết quả
  kiểm cuối lưu trong `workspace_audit.json`. Không có diff trên file tracked.

## Các quy ước phải chọn vì brief/thẻ chưa chỉ rõ

1. Share tie tươi gộp tính một lần cho mỗi instance × h trên đủ bảy h; không
   nhân đôi theo hai tuổi stale. Báo thêm từng h để thấy đúng mẫu số.
2. T1 chỉ dùng eligibility được thẻ nêu: ≥5 ngày và ≥5% bất đồng pooled. Không
   thêm evaluability filter của X4b vào T1. D là trung bình đều các paired
   percentage theo ngày; SE qua ngày, ddof=1. Khi không có C_ref dương để chuẩn
   hóa, không tự gán một con số phần trăm.
3. T3 dùng trung bình đều regret phần trăm theo ngày trong từng regime ở 7200 s;
   share tie dùng quy ước ở mục 1. Không lọc thêm evaluability vào T3.
4. T4 giữ đơn vị “bản ghi” của thẻ: lấy max của mean regret fresh, stale_300 và
   stale_900, dùng chung C_ref và X4b evaluability gate. Một regime/day chỉ được
   đếm một lần; phải đạt cả hai so sánh fresh/stale_age của X4b.
5. Hai pilot dự kiến chọn theo work proxy đầu vào của X4b, thứ tự giảm dần rồi
   regime/date; sàng ALARM_RARE bằng pilot seed trước khi rollout. Không chọn
   theo outcome. Quy tắc đã code nhưng không thực hiện vì screen không qua.
6. Preflight chọn bản ghi có work proxy đầu vào cao nhất, được dùng lại trong
   step0. Dự phóng tuyến tính chỉ là ước lượng khả thi local, không guarantee/CI.
7. Lưu bản sao nguyên byte brief tại `DESIGN_X5_ALARM.md` trong thư mục X5 để
   verify-lock trên GCP không phụ thuộc đường dẫn local của thư mục paper.
   Configuration vẫn ghi đường dẫn và SHA-256 nguồn gốc. Không sửa brief gốc.

## File đã tạo

Source mới:

- `experiments/letter/x5_alarm.py`
- `experiments/letter/x5_alarm_card.py`
- `experiments/letter/x5_gcp.sh`
- `tests/test_x5_alarm.py`

Kết quả trong `results/letter/x5_alarm/`:

- `configuration.json`: cấu hình, slope train, 60 bản ghi và provenance/hash nguồn.
- `DESIGN_X5_ALARM.md`: snapshot brief, không thay brief gốc.
- `step0/summary.json`, `step0/alarms.csv`, `step0/disagreement.csv`,
  `step0/M0_fresh_ties.csv`, `step0/preflight.json`, `step0/started.json`.
- `step0/test/*.npz` và `*.json`: 60 cặp raw/metadata; giữ cả ALARM_RARE.
- `audit_step0.py`, `step0_audit.json`: audit độc lập và kết quả.
- Log: `configure.log`, `step0.log`, `pytest_initial.log`,
  `pytest_selection_fixed.log`, `pytest_regression.log`, `step0_audit.log`
  (lỗi lần đầu), `step0_audit_fixed.log` (PASS).
- `preexisting_inventory.json`, `workspace_audit.json`: bằng chứng phạm vi ghi file.
- `PREPARATION_REPORT.md`: báo cáo này. Không tạo biểu đồ.

Kết luận đã kiểm: implementation và test đạt; screen có 59 bản ghi RARE,
chỉ một ngày đủ cảnh báo và không có bất đồng Hybrid/Stationary. Dừng X5 ở
NOT_ENOUGH_SIGNAL theo thẻ. Regret, lợi ích correction và T1–T4 chưa được
xác nhận bằng truth; không điều chỉnh ngưỡng, seed, regime hoặc h để cứu cổng.
