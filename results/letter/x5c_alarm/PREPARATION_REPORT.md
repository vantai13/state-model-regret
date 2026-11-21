# X5c — báo cáo chuẩn bị

Người phụ trách: **Doan Van Tai**.

Triển khai và đo theo DESIGN_X5C_ALARM.md, CARD_X5C.md và T1–T4 nguyên từ CARD_X5.md.
Không commit, push hoặc SSH. Không chạy experiment truth/score. Công việc triển khai không phải tác giả tự viết/đọc.

M=512, N≤32, MIN_ALARMS=8, K=64, R_dec=64, R_eval=128. Cùng 60 test-S regime/day của X4b.
h=300/600/900/1200/1800/3600/7200 s; stale ages=300/900 s; dt=0,05 s.
Các mẫu chia sẻ ngày, instance và h; các mẫu số không phải số thử nghiệm độc lập.

## Slope và link cảnh báo

| Nhánh | Regime | η | ŝ pooled train (Mbit) | Luật tĩnh | Link index / tên | Ngưỡng (Mbit) |
|---|---|---:|---:|---|---|---:|
| A | NEWB1 | 0.3 | 64371.266983335532 | Stay | 1 / at1.at_de1.de:at1.at>de1.de | 12.544525173885 |
| A | NEWB2 | 0.3 | -76945.746287496062 | Switch | 21 / de1.de_se1.se:de1.de>se1.se | 9.126508697966 |
| A | NEWB3 | 0.3 | 29918.098814829620 | Stay | 1 / at1.at_de1.de:at1.at>de1.de | 12.544525173885 |
| B | NEWB1 | 0.6 | 62812.710843280525 | Stay | 1 / at1.at_de1.de:at1.at>de1.de | 12.544525173885 |
| B | NEWB2 | 0.6 | -78887.147942050127 | Switch | 21 / de1.de_se1.se:de1.de>se1.se | 9.126508697966 |
| B | NEWB3 | 0.6 | 28352.985968247878 | Stay | 1 / at1.at_de1.de:at1.at>de1.de | 12.544525173885 |

Nhánh A nhập nguyên ŝ X4b. Nhánh B gọi đúng B.train_record trên đủ 26 weekday × 3 regime, gồm S và O,
N32 và 6 h rollout, seed train 7200005, namespace X5C-B|regime|date. Pool daily slopes với trọng số đều.
train/summary.json đã được đóng và hash trước khi mở test plan hoặc test TMs.

## Đo theo nhánh

### Nhánh A: NOT_ENOUGH_SIGNAL

Seed test 7100001, pilot 7100003; namespace X5C-A|regime|date.

| Regime | Cảnh báo / ứng viên | ALARM_RARE / bản ghi | Không RARE | Instance dùng quyết định |
|---|---:|---:|---:|---:|
| NEWB1 | 52/4096 = 1.269531% | 7/8 | 1 | 32 |
| NEWB2 | 0/14848 = 0.000000% | 29/29 | 0 | 0 |
| NEWB3 | 678/11776 = 5.757473% | 20/23 | 3 | 96 |
| Tổng | 730/30720 = 2.376302% | 56/60 | 4 | 128 |

**Share bất đồng Hybrid ≠ Stationary theo regime × h × side:**

| Regime | h (s) | Fresh | Stale 300 | Stale 900 |
|---|---:|---:|---:|---:|
| NEWB1 | 300 | 0/32 = 0.000000% | 0/32 = 0.000000% | 0/32 = 0.000000% |
| NEWB1 | 600 | 0/32 = 0.000000% | 0/32 = 0.000000% | 0/32 = 0.000000% |
| NEWB1 | 900 | 0/32 = 0.000000% | 0/32 = 0.000000% | 0/32 = 0.000000% |
| NEWB1 | 1200 | 0/32 = 0.000000% | 0/32 = 0.000000% | 0/32 = 0.000000% |
| NEWB1 | 1800 | 0/32 = 0.000000% | 0/32 = 0.000000% | 0/32 = 0.000000% |
| NEWB1 | 3600 | 0/32 = 0.000000% | 0/32 = 0.000000% | 0/32 = 0.000000% |
| NEWB1 | 7200 | 0/32 = 0.000000% | 0/32 = 0.000000% | 0/32 = 0.000000% |
| NEWB2 | 300 | NA | NA | NA |
| NEWB2 | 600 | NA | NA | NA |
| NEWB2 | 900 | NA | NA | NA |
| NEWB2 | 1200 | NA | NA | NA |
| NEWB2 | 1800 | NA | NA | NA |
| NEWB2 | 3600 | NA | NA | NA |
| NEWB2 | 7200 | NA | NA | NA |
| NEWB3 | 300 | 0/96 = 0.000000% | 0/96 = 0.000000% | 0/96 = 0.000000% |
| NEWB3 | 600 | 0/96 = 0.000000% | 0/96 = 0.000000% | 0/96 = 0.000000% |
| NEWB3 | 900 | 31/96 = 32.291667% | 31/96 = 32.291667% | 32/96 = 33.333333% |
| NEWB3 | 1200 | 16/96 = 16.666667% | 15/96 = 15.625000% | 14/96 = 14.583333% |
| NEWB3 | 1800 | 0/96 = 0.000000% | 0/96 = 0.000000% | 0/96 = 0.000000% |
| NEWB3 | 3600 | 0/96 = 0.000000% | 0/96 = 0.000000% | 0/96 = 0.000000% |
| NEWB3 | 7200 | 0/96 = 0.000000% | 0/96 = 0.000000% | 0/96 = 0.000000% |

**Share tie M0 tươi:**

| h (s) | NEWB1 | NEWB2 | NEWB3 |
|---:|---:|---:|---:|
| 300 | 0/32 = 0.000000% | NA | 0/96 = 0.000000% |
| 600 | 0/32 = 0.000000% | NA | 0/96 = 0.000000% |
| 900 | 0/32 = 0.000000% | NA | 0/96 = 0.000000% |
| 1200 | 0/32 = 0.000000% | NA | 0/96 = 0.000000% |
| 1800 | 0/32 = 0.000000% | NA | 0/96 = 0.000000% |
| 3600 | 0/32 = 0.000000% | NA | 0/96 = 0.000000% |
| 7200 | 0/32 = 0.000000% | NA | 0/96 = 0.000000% |

Tie gộp: **0/896 = 0.000000%**, fresh một lần cho mỗi instance × h, không lặp theo stale age.
Step0: 406.401104089 CPU-s cộng qua các bản ghi; 126.325601798 wall-s.
Preflight step0: 585.093581 wall-s với 8 worker (ước lượng, không guarantee/CI).
Pilot **NOT_RUN** theo cổng; CPU pilot và dự phóng truth **NA**; không tạo lock.
Truth/score **NOT_RUN**; T1–T4 chưa được xác nhận bằng truth. Không tạo raw truth/card_verdicts.json/REPORT_X5C.md.

### Nhánh B: NOT_ENOUGH_SIGNAL

Seed test 7200001, pilot 7200003; namespace X5C-B|regime|date.

| Regime | Cảnh báo / ứng viên | ALARM_RARE / bản ghi | Không RARE | Instance dùng quyết định |
|---|---:|---:|---:|---:|
| NEWB1 | 207/4096 = 5.053711% | 6/8 | 2 | 59 |
| NEWB2 | 307/14848 = 2.067619% | 26/29 | 3 | 72 |
| NEWB3 | 999/11776 = 8.483356% | 19/23 | 4 | 120 |
| Tổng | 1513/30720 = 4.925130% | 51/60 | 9 | 251 |

**Share bất đồng Hybrid ≠ Stationary theo regime × h × side:**

| Regime | h (s) | Fresh | Stale 300 | Stale 900 |
|---|---:|---:|---:|---:|
| NEWB1 | 300 | 0/59 = 0.000000% | 0/59 = 0.000000% | 0/59 = 0.000000% |
| NEWB1 | 600 | 0/59 = 0.000000% | 0/59 = 0.000000% | 0/59 = 0.000000% |
| NEWB1 | 900 | 0/59 = 0.000000% | 0/59 = 0.000000% | 0/59 = 0.000000% |
| NEWB1 | 1200 | 0/59 = 0.000000% | 0/59 = 0.000000% | 0/59 = 0.000000% |
| NEWB1 | 1800 | 0/59 = 0.000000% | 0/59 = 0.000000% | 0/59 = 0.000000% |
| NEWB1 | 3600 | 0/59 = 0.000000% | 0/59 = 0.000000% | 0/59 = 0.000000% |
| NEWB1 | 7200 | 0/59 = 0.000000% | 0/59 = 0.000000% | 0/59 = 0.000000% |
| NEWB2 | 300 | 0/72 = 0.000000% | 0/72 = 0.000000% | 0/72 = 0.000000% |
| NEWB2 | 600 | 0/72 = 0.000000% | 0/72 = 0.000000% | 0/72 = 0.000000% |
| NEWB2 | 900 | 0/72 = 0.000000% | 0/72 = 0.000000% | 0/72 = 0.000000% |
| NEWB2 | 1200 | 0/72 = 0.000000% | 0/72 = 0.000000% | 0/72 = 0.000000% |
| NEWB2 | 1800 | 0/72 = 0.000000% | 0/72 = 0.000000% | 0/72 = 0.000000% |
| NEWB2 | 3600 | 0/72 = 0.000000% | 0/72 = 0.000000% | 0/72 = 0.000000% |
| NEWB2 | 7200 | 0/72 = 0.000000% | 0/72 = 0.000000% | 0/72 = 0.000000% |
| NEWB3 | 300 | 0/120 = 0.000000% | 0/120 = 0.000000% | 0/120 = 0.000000% |
| NEWB3 | 600 | 0/120 = 0.000000% | 0/120 = 0.000000% | 0/120 = 0.000000% |
| NEWB3 | 900 | 22/120 = 18.333333% | 22/120 = 18.333333% | 20/120 = 16.666667% |
| NEWB3 | 1200 | 13/120 = 10.833333% | 14/120 = 11.666667% | 14/120 = 11.666667% |
| NEWB3 | 1800 | 6/120 = 5.000000% | 6/120 = 5.000000% | 5/120 = 4.166667% |
| NEWB3 | 3600 | 0/120 = 0.000000% | 0/120 = 0.000000% | 0/120 = 0.000000% |
| NEWB3 | 7200 | 0/120 = 0.000000% | 0/120 = 0.000000% | 0/120 = 0.000000% |

**Share tie M0 tươi:**

| h (s) | NEWB1 | NEWB2 | NEWB3 |
|---:|---:|---:|---:|
| 300 | 0/59 = 0.000000% | 41/72 = 56.944444% | 0/120 = 0.000000% |
| 600 | 0/59 = 0.000000% | 41/72 = 56.944444% | 0/120 = 0.000000% |
| 900 | 0/59 = 0.000000% | 41/72 = 56.944444% | 0/120 = 0.000000% |
| 1200 | 0/59 = 0.000000% | 41/72 = 56.944444% | 0/120 = 0.000000% |
| 1800 | 0/59 = 0.000000% | 41/72 = 56.944444% | 0/120 = 0.000000% |
| 3600 | 0/59 = 0.000000% | 41/72 = 56.944444% | 0/120 = 0.000000% |
| 7200 | 0/59 = 0.000000% | 41/72 = 56.944444% | 0/120 = 0.000000% |

Tie gộp: **287/1757 = 16.334661%**, fresh một lần cho mỗi instance × h, không lặp theo stale age.
Step0: 1477.119054441 CPU-s cộng qua các bản ghi; 297.517651453 wall-s.
Preflight step0: 907.944450 wall-s với 8 worker (ước lượng, không guarantee/CI).
Train B: 1403.976248427 CPU-s, 200.390288618 wall-s; 78/78 bản ghi.
Pilot **NOT_RUN** theo cổng; CPU pilot và dự phóng truth **NA**; không tạo lock.
Truth/score **NOT_RUN**; T1–T4 chưa được xác nhận bằng truth. Không tạo raw truth/card_verdicts.json/REPORT_X5C.md.

## Kiểm chứng và lỗi đã giữ

- 158/158 PASS ở lượt đầu (8,98 s); bổ sung kiểm mean/warmup: 159/159 PASS (6,76 s).
- Configure B lần đầu FAIL trước simulator vì parent arm_B chưa tồn tại. Không có train outcome/test B; giữ configure_B.log.
- Chỉ sửa mkdir(parents=True) trong module mới; snapshot source_at_arm_A_step0.py giữ source A. Không rerun A.
- Regression sau sửa: **160/160 PASS, 7,35 s**; thêm test tạo parent trước first worker.
- Audit độc lập không import experiment/scorer: A: 60 records, 30720 candidate queues, 16128 decision/tie values, 0 train records; B: 60 records, 30720 candidate queues, 31626 decision/tie values, 78 train records.
- Audit A kiểm snapshot đúng SHA lúc bắt đầu và chứng minh source hiện hành khác đúng một dòng mkdir. B kiểm source hiện hành đúng SHA.
- SHA-256 **52740 file có sẵn PASS**, không sửa/xóa; HEAD giữ nguyên 4bc51d97213e51c0f36ce2edef1f0d8447af350e.
- bash -n PASS. Shell harness dùng stub kiểm A/B chạy nối tiếp, log riêng, A lỗi không chặn B và poweroff đúng một lần cuối; không gọi cloud/poweroff thật.

Lệnh chính (đã source .venv/bin/activate và experiments/explore_ctmc/env.sh, đặt PYTHONDONTWRITEBYTECODE=1, TMPDIR/MPLCONFIGDIR trong build):

```bash
python3 -m pytest -q -p no:cacheprovider --basetemp=results/letter/x5c_alarm/pytest_parent_fix tests/test_x5c_alarm.py tests/test_x5_alarm.py tests/test_x4b.py tests/test_x4b_card.py tests/test_x4b_truth.py
bash -n experiments/letter/x5c_gcp.sh
python3 -m experiments.letter.x5c_alarm configure --arm A
python3 -m experiments.letter.x5c_alarm step0 --arm A --workers 8
python3 -m experiments.letter.x5c_alarm configure --arm B --workers 8
python3 -m experiments.letter.x5c_alarm step0 --arm B --workers 8
python3 results/letter/x5c_alarm/audit_preparation.py
```

## Những chỗ phải chọn vì brief chưa chỉ rõ

1. Dùng trực tiếp x5_alarm_card; không cần x5c_card riêng. T1–T4 và các quy ước X5 được áp riêng từng nhánh: SE qua ngày ddof=1, tie fresh không lặp theo stale, T3 mean daily percentages, T4 một regime/day cần cả fresh và hai stale ages đạt.
2. ŝ=0 chọn Stay theo nhánh “ngược lại” trong brief. Alarm threshold dùng capacity của đúng link đã chọn, không capacity đồng nhất.
3. Train B dùng 8 worker local, cùng giới hạn step0. Preflight tái dùng record có input-work proxy cao nhất, không rerun record đầu; thứ tự deterministic theo work/regime/date. Slope là mean đều 26 ngày.
4. Pilot, nếu cổng qua, chọn hai record theo work proxy đầu vào và screen bằng pilot seed; không chọn theo regret. Dự phóng local trước pilot từ phép đo X4b, rồi kiểm lại bằng pilot thứ nhất trước bản ghi thứ hai.
5. Lock là content lock chưa commit. Brief snapshot nguyên byte giúp verify trên GCP; nguồn gốc và hash brief vẫn lưu. Không coi lock là quyền tự chạy truth.
6. ARMS="A B" chạy hai nhánh độc lập nối tiếp. Nhánh lỗi giữ exit code và log, nhánh kia vẫn được verify/run; chỉ poweroff sau nhánh cuối. Script chưa được thực thi với engine thật.

## File

- Source mới: experiments/letter/x5c_alarm.py; experiments/letter/x5c_gcp.sh; tests/test_x5c_alarm.py.
- Cấu hình và số liệu mỗi nhánh: arm_A/ hoặc arm_B/: configuration.json; step0/summary.json, alarms.csv, disagreement.csv, M0_fresh_ties.csv, preflight.json, test/*.npz và *.json.
- Train B: arm_B/train/summary.json, preflight.json, started.json, training_rates/*.npz và *.json.
- Audit: audit_preparation.py, preparation_audit.json, arm_A_audit.json, preexisting_inventory.json, workspace_audit.json; rà η: BETA_AUDIT.md.
- Log: configure_A.log, step0_A.log, configure_B.log (FAIL), configure_B_parent_fix.log, step0_B.log, pytest_initial.log, pytest_regression.log, pytest_parent_fix.log, preparation_audit.log.
- Báo cáo này: PREPARATION_REPORT.md; số gọn: measured_summary.json. Không tạo biểu đồ.

## Kết luận

Đã kiểm implementation, runtime η, selection, train/test order và cổng bằng dữ liệu lưu thật. Kết quả cổng mỗi nhánh giữ nguyên; không đổi seed, threshold, regime hoặc h để cứu tín hiệu.
T1–T4, regret thực nghiệm và hiệu quả correction chưa được xác nhận khi chưa có truth/score. Các ngày test vốn đã exposed từ X4b; X5c không phải dữ liệu traffic mới.
