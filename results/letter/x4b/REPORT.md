# Báo cáo X4b — chuẩn bị theo DESIGN_X4B.md

Người phụ trách: Doan Van Tai. Brief khớp byte commit `dea74a3` của letter_smr; SHA256 `78f82644983dc9d5f4b35bccaac9a684d33f12f926f91ac33902c6c9f78873f0`.

**A. Đã thực hiện**

Chỉ tạo `experiments/letter/x4b.py`, `tests/test_x4b.py` và artifact trong `results/letter/x4b/`. Import X-GÉANT/V7-3 nguyên trạng; không commit, ssh, truth hoặc score. Các file của job X1c giữ riêng.

Đã chạy configure → step0 → predict → pilot → lock → verify-lock. N=32, K=64, R_dec=64, R_eval=128; β=0,3; flip=1/s; dt=0,05s; τ=300/900s; h=300/600/900/1200/1800/3600/7200s. Train 26 weekday; window 10:15–16:15.

Ba regime là hạng 4–6 của X2-eligible sau NEW1–3. Capacity dưới đây là capacity kịch bản; mỗi regime chỉ đổi một directed link. 71 link còn lại giữ 12544.525173885328 Mbit/s.

| Regime | OD | e* | Capacity mới (Mbit/s) | Util Switch trước | Util Switch sau | Max-util path Stay sau |
|---|---|---|---:|---:|---:|---:|
| NEWB1 | ch1.ch_de1.de | de1.de_fr1.fr:fr1.fr>de1.de | 2107.079186150 | 0.142772826 | 0.850000000 | 0.900000000 |
| NEWB2 | ch1.ch_se1.se | de1.de_se1.se:de1.de>se1.se | 9126.508697966 | 0.618399843 | 0.850000000 | 0.900000000 |
| NEWB3 | at1.at_de1.de | de1.de_fr1.fr:fr1.fr>de1.de | 1953.880206073 | 0.132392271 | 0.850000000 | 0.900000000 |

Công thức: c[e*] = mean(train-window Switch load[e*])/0,85; chọn e* trước khi đổi capacity. Bảng đủ từng link/action: [train_utilizations.csv](train_utilizations.csv). Audit độc lập: sai số mục tiêu tối đa 3,33e−16; các link khác nguyên giá trị.

| Regime | Stay | Switch |
|---|---|---|
| NEWB1 | ch1.ch → at1.at → de1.de | ch1.ch → fr1.fr → de1.de |
| NEWB2 | ch1.ch → at1.at → de1.de → se1.se | ch1.ch → fr1.fr → de1.de → se1.se |
| NEWB3 | at1.at → de1.de | at1.at → ch1.ch → fr1.fr → de1.de |

**B. Đã chạy và kiểm tra**

Các command dùng `source experiments/explore_ctmc/env.sh`, `PYTHONDONTWRITEBYTECODE=1`, và `TMPDIR="$PWD/results/letter/x4b/build"`:

```bash
.venv/bin/python -B -m pytest tests/test_x4b.py -q -p no:cacheprovider --basetemp=results/letter/x4b/pytest_initial
.venv/bin/python -B -m pytest tests/test_x_geant.py tests/test_letter_v7_3.py tests/test_letter_v7_3_day.py tests/test_letter_v7_3_cong.py -q -p no:cacheprovider --basetemp=results/letter/x4b/pytest_regression
.venv/bin/python -B -m experiments.letter.x4b configure
.venv/bin/python -B -m experiments.letter.x4b step0 --workers 6
.venv/bin/python -B -m experiments.letter.x4b predict
.venv/bin/python -B -m experiments.letter.x4b pilot
.venv/bin/python -B -m experiments.letter.x4b lock
.venv/bin/python -B -m experiments.letter.x4b verify-lock
```

26 test mới PASS (4,00s), gồm capacity-vector đồng nhất khớp bit-for-bit quyết định và chi phí pilot X-GÉANT trên một record thực với số mẫu nhỏ; công thức 0,85; identity G_S; cổng 1%; cấm future evaluation trong step0; từ chối truth/score CLI; chống overwrite/drift. 75 test hồi quy PASS (1,26s). Đây là các test liên quan, không phải full suite repo.

Audit raw 138 record quyết định, 84 dòng bất đồng và 189 dòng tie: PASS. Lượt audit đầu exit 1 do đọc scalar NPZ bằng float(array); sửa riêng audit sang `.item()`, audit lại PASS. Không sửa source thí nghiệm hoặc raw, không chạy lại experiment. Log lỗi được giữ.

Pilot raw: manual action gather, G_S=(a_stale−a_fresh)(V_Switch−V_Stay), G_S của Stationary=0, và reference triệt tiêu trong hiệu regret Hybrid−Stationary đều PASS. Lock 482 file PASS, `committed=false`; Git tracked/staged diff trống.

**C. Kết quả đo được**

| Regime | Train S/O | Test S/O | ŝ pooled (Mbit) | Stationary |
|---|---:|---:|---:|---|
| NEWB1 | 6/20 | 8/42 | 64371.266983 | Stay |
| NEWB2 | 12/14 | 29/21 | -76945.746287 | Switch |
| NEWB3 | 8/18 | 23/27 | 29918.098815 | Stay |

Có 60 test-S record, 90 test-O record NOT_RUN. Giữ nguyên ước lượng ŝ từ cả train S/O bằng paired 6h rate rollouts như pipeline gốc. Bước 0 gồm 78 train + 60 test-S = 138 record; không rollout đánh giá tương lai test.

| h (s) | Fresh bất đồng /1920 | Stale300 /1920 | Stale900 /1920 | Tổng /5760 | Share tổng |
|---:|---:|---:|---:|---:|---:|
| 300 | 0 | 0 | 0 | 0 | 0.000000% |
| 600 | 0 | 0 | 0 | 0 | 0.000000% |
| 900 | 31 | 31 | 31 | 93 | 1.614583% |
| 1200 | 21 | 20 | 21 | 62 | 1.076389% |
| 1800 | 2 | 2 | 2 | 6 | 0.104167% |
| 3600 | 0 | 0 | 0 | 0 | 0.000000% |
| 7200 | 0 | 0 | 0 | 0 | 0.000000% |

**SIGNAL_OK:** h=900s và 1200s đạt ≥1%. Tất cả bất đồng test nằm ở NEWB3 ngày 2005-07-19; hướng quyết định là Hybrid Switch / Stationary Stay. Không bỏ NEWB1/2 khỏi danh sách dự kiến.

Ưu tiên fluid chặt về action có pooled rate cao hơn: fresh 135/1920, stale300 956/1920, stale900 957/1920, tổng 2048/5760 (35,555556%) ở mỗi h. Ties không được tính vào ưu tiên chặt. Counts chia sẻ ngày/instance, không phải phép thử độc lập; tín hiệu một ngày không xác nhận hiệu regret.

Train-rate CPU: 894.980111s; decision-only CPU cộng record: 3153.611440s; wall toàn lệnh step0 với 6 worker: 710.485085s.

Predict có 126 dòng G_S-sign forecast và 63 dòng paired forecast chỉ từ train-S. Chúng là dự đoán theo rate ở grid h đã định, không phải card kiểm định mới.

Pilot: NEWB3 / 2005-07-19, seed 7472001, full N/K/R_dec/R_eval. Đo 189.907185 CPU-s, 189.914375s wall, peak RSS 146.0625 MiB. Chọn bằng input-only workload proxy, cùng ngày có tín hiệu, với seed khác test.

Dự phóng tuyến tính 60 record: 11394.431088 CPU-s = 3.165120 CPU-h. Chia lý tưởng 30 worker trên n2-highcpu-32: 6.330239 phút wall. Đây là ngoại suy local, không phải đo GCP, CI hoặc bảo đảm worst case.

**D. Artifact**

- Source: `experiments/letter/x4b.py`; test: `tests/test_x4b.py` (đường dẫn tính từ repo root).
- Cấu hình: [protocol.json](protocol.json), [configuration.json](configuration.json), [configuration.npz](configuration.npz), [regimes.md](regimes.md).
- Train/utilization: [train_utilizations.csv](train_utilizations.csv), [candidate_ranking_inputs.csv](candidate_ranking_inputs.csv), [training_summary.json](training_summary.json); raw ở `training_rates/`.
- Bước 0: [signal.json](signal.json), [step0_disagreement.csv](step0_disagreement.csv), [step0_by_record.csv](step0_by_record.csv), [step0_ties.csv](step0_ties.csv), [inputs.json](inputs.json); raw ở `step0/train/`, `step0/test/`.
- Dự đoán: [predictions.json](predictions.json), [predictions.csv](predictions.csv), [predictions_paired.csv](predictions_paired.csv).
- Pilot: [summary.json](pilot/summary.json), [selection.json](pilot/selection.json), [raw NPZ](pilot/records/NEWB3_2005-07-19.npz), [receipt JSON](pilot/records/NEWB3_2005-07-19.json).
- Audit/lock: [configuration_audit.json](configuration_audit.json), [step0_audit.json](step0_audit.json), [lock.json](lock.json), [final_verification.json](final_verification.json).
- Log: `configure.log`, `step0.log`, `predict.log`, `pilot.log`, `lock.log`, `verify_lock.log`, `pytest_initial.log`, `pytest_regression.log`, `step0_audit_initial.log`, `step0_audit.log`, `final_verification.log`.
- Không tạo truth/score output, prediction card hoặc biểu đồ.

**E. Kết luận và giới hạn**

Đã xác nhận implementation/preparation và cổng bất đồng quyết định, chưa kiểm định Hybrid tốt hơn hay kém Stationary về regret. Pilot là exposure trước truth. Claude còn viết card hai chiều sau bước 0 và trước truth; công việc này không tự tạo card hoặc cho phép truth.

Với capacity vector, brief chưa định nghĩa cách chuẩn hóa cổng evaluability “1 ms link service”. Module giữ chi phí tổng backlog Mbit·s và để cổng service-time này NOT_DECIDED, không thay bằng một scalar capacity tùy chọn. Cần xác định trước truth/scoring. Đây không phải thay đổi cổng SIGNAL_OK đã khai.

Underlying test days đã xuất hiện trong V7-3/X-GÉANT. S=mean-slot offered load<capacity, không chứng nhận mọi sample không nghẽn. Pilot và counts này không chứng minh novelty, stationary approximation đúng, hoặc lợi thế regret.
