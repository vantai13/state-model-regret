# S3 CTMC — báo cáo chuẩn bị và bàn giao

Người phụ trách: **Doan Van Tai**. Theo BRIEF_S3_CTMC.md ngày 21/11/2026.
Trạng thái: **PREPARATION PASS; S3 TRUTH NOT_RUN; S3 SCORE NOT_RUN**.
Không commit, không SSH, không thay file đã có hoặc CARD_S3.md.

## Công việc và thiết kế

Tạo `runner.py` (wrapper sampler/estimator/evaluator S1-A, sample, pilot, lock,
verify-lock, run-shard), `s3_gcp.sh`, scorer và rescorer độc lập, tests, README
và integrity helper; tất cả source ở `experiments/letter/s3_ctmc/`.
Output mới chỉ ở `results/letter/sweep/s3/`.
Thẻ, miền, 300 T_int, lưới 14×3×8, fallback, ties và resource caps giữ nguyên.
600 regime đầu tiên đạt initial screen và frozen pilot screen S1-A;
không dùng outcome để chọn hay loại. INVALID vẫn trong N=600.
D_hat đúng H-C S2: mean_tau(D_fresh + D_stale), khác share bất đồng thực tế.
Scorer gộp tuổi trong regime trước Student t, dùng paired C_ref.
Không có D hoặc paired outcome thì không impute; mean test bị ảnh hưởng
NOT_EVALUABLE. T1/T2/T3 và secondary giữ các threshold của thẻ.

| Seed | Giá trị |
|---|---:|
| Sobol S3 | 630951401 |
| Record S3 | 630951402 |
| Sobol pilot riêng | 630951403 |
| Record pilot riêng | 630951404 |

Seed audit: 45,719 file text cũ,
1,772,548,551 byte, 0 literal collision; bốn seed phân biệt và
khác S1-A 8100001–8100004. Phạm vi/giới hạn kiểm seed được ghi trong seeds.json;
không chứng minh được một seed tính từ công thức tùy ý chưa được ghi nhận.
Mẫu mới và pilot không trùng physical regime S1-A hoặc nhau.

## Số đo và dự phóng tài nguyên

Sample: **600/612**, loại 12:
7 TRUNCATION_RESOURCE_CAP, 3 PROJECTED_CPU_CAP, 2 TELEMETRY_RESOURCE_CAP.
Shard 0/2: 302 regime; shard 1/2: 298, disjoint/exhaustive. Không đổi ID sau loại.

| Mô hình chi phí từ S1-A | CPU-giờ | Wall lý tưởng tổng/30 (phút) | Shard chậm hơn /15 (phút) | Shard chậm hơn ở 90% (phút) |
|---|---:|---:|---:|---:|
| Fit timings/work receipt GCP 1000 regime | 8.500811 | 17.002 | 17.418 | 19.353 |
| Envelope pilot S1-A × safety 1.5 | 17.566761 | 35.134 | 35.835 | 39.816 |

Đây là extrapolation theo regime work, không guarantee hoặc confidence interval.
Pilot mới không recalibrate hay thay screen. Tối đa đúng 3 regime từ một seed
pilot riêng, chọn ba resource proxy lớn nhất trong 64 ứng viên pilot trước
outcomes, chỉ lưới timing S1-A h/T_int={0.1,1}, tau/T_int={0.3}:

| Regime pilot | CPU-s |
|---|---:|
| S3P_0061 | 11.758988587 |
| S3P_0024 | 4.974588240 |
| S3P_0012 | 6.083795500 |

Pilot **3/3 COMPLETED**, tổng 22.817372327 CPU-s,
22.837964436 wall-s, 1 worker; 0 CPU_CAP/ERROR.
Timing bằng 38.5–42.6% envelope S1-A trên cùng subset. Không sửa dự phóng từ
pilot này. Chỉ kiểm timing, seed/schema/hash; scientific outcomes không chấm.

## Kiểm chứng

- Final pytest **81 PASS** (38 S3 mới + 43 S1-A cũ), 25.13 giây.
- Initial pytest 1 FAIL/77 PASS: assertion tùy ý đòi >1000 trường ở panel giả
  chỉ có 790 trường; đã bỏ điều kiện đếm đó, giữ toàn bộ phép đối chiếu.
  Sau thêm controls cho seed/grid và chặn pilot raw, lượt cuối 81 PASS.
- Test synthetic T1/T2/T3, các FAIL và NOT_EVALUABLE khi vùng <5; CI theo
  regime, inclusive D threshold, INVALID/missing, raw corruption, no overwrite,
  guard trước engine và mutation/pin SHA.
- Scorer trên raw S1-A ID chẵn (chỉ test, không ghi score/):
  **99/501**, baseline
  **2.427720094%** → hybrid
  **0.317065014% C_ref**,
  Δ **2.110655080 điểm**, CI95%
  **[1.284328765; 2.936981395]**.
  Lợi tuyệt đối **5.588285053 packet·s**.
- D_hat khớp `analyze_s2.load_pairs()` trên 3 regime ×14 h×2 side =84 so sánh.
- Rescore độc lập raw S1-A: **2155 trường số liệu/verdict khớp**.
  Không import scorer/analyzer; D lấy từ policy rows, arithmetic độc lập.
- `bash -n` PASS; invalid shard exit 2 trong test, không launch hợp lệ local.
- `verify-lock` PASS, **39 file**; 1683 file có sẵn
  kiểm SHA256, **0 thay đổi**. `git diff --name-only` rỗng.

## Command thực thi

Python đều dùng `.venv`, source `experiments/explore_ctmc/env.sh`,
`PYTHONDONTWRITEBYTECODE=1`; pytest không cache, basetemp dưới output được phép.

```bash
python3 -B -u -m experiments.letter.s3_ctmc.runner sample
python3 -B -m pytest -q -s -p no:cacheprovider --basetemp results/letter/sweep/s3/checks/pytest_final experiments/letter/s3_ctmc/test_s3_ctmc.py tests/test_sweep_ctmc.py
python3 -B -u -m experiments.letter.s3_ctmc.runner pilot
python3 -B -u -m experiments.letter.s3_ctmc.runner lock
bash -n experiments/letter/s3_ctmc/s3_gcp.sh
python3 -B -m experiments.letter.s3_ctmc.runner verify-lock --expected-sha 781da0b28d63d1abae8bdcf546c42e5f8a6d428d35427961ffc300214c7d5dc0
```

## Bàn giao launch Claude — CHƯA CHẠY

Máy `n2-highcpu-32`, 2 shard ×15 worker. Sync đúng 39 file trong lock và
lock.json (danh sách portable `locked_files.txt`, 40 dòng), giữ relative paths
trong `~/smr`. Pin SHA256 bên dưới là trust anchor; không tạo lock mới trên VM.
Các lệnh chạy trong driver của Claude, driver thu exit cả hai shard và
chịu trách nhiệm `sudo -n poweroff`, revert `n2-custom-12-49152`, TERMINATED.
Script shard chỉ log PIPELINE_START/EXIT, timeout 6 giờ, không poweroff,
không retry/resume. Các lệnh sau chưa thực thi trong nhiệm vụ:

```bash
cd ~/smr
export S3_LOCK_SHA256=781da0b28d63d1abae8bdcf546c42e5f8a6d428d35427961ffc300214c7d5dc0
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
python3 -B -m experiments.letter.s3_ctmc.runner verify-lock --expected-sha "$S3_LOCK_SHA256"
bash experiments/letter/s3_ctmc/s3_gcp.sh 0 &
s3_pid0=$!
bash experiments/letter/s3_ctmc/s3_gcp.sh 1 &
s3_pid1=$!
s3_rc=0
wait "$s3_pid0" || s3_rc=$?
wait "$s3_pid1" || s3_rc=$?
exit "$s3_rc"
```

Sau khi Claude rsync + checksum và commit raw trước scoring:

```bash
python3 -B -m experiments.letter.s3_ctmc.score_s3 --expected-lock-sha "$S3_LOCK_SHA256"
python3 -B -m experiments.letter.s3_ctmc.rescore_s3 --expected-lock-sha "$S3_LOCK_SHA256"
```

## Nơi lưu

- Source và hướng dẫn: `experiments/letter/s3_ctmc/README.md`, `runner.py`,
  `integrity.py`, `score_s3.py`, `rescore_s3.py`, `test_s3_ctmc.py`, `s3_gcp.sh`.
- Card gốc giữ byte: `results/letter/sweep/s3/CARD_S3.md`.
- Cấu hình/seeds/mẫu: `sample/config.json`, `sample/seeds.json`,
  `sample/sample.json`, `sample/sample.csv`; cost estimates `sample/projection.json`.
- Pilot: `pilot/plan.json`, `pilot/receipt.json`, `pilot/raw/S3P_*.json`;
  `checks/pilot_audit.json`.
- Logs thực chạy: `checks/sample.log`, `checks/pilot.log`,
  `checks/pytest_initial.log`, `checks/pytest_final.log`, `checks/lock.log`,
  `checks/verify_lock.log`.
- Regression/audit: `checks/s1a_regression.json`, `checks/final_verification.json`,
  `checks/preexisting_sha256.json`, `checks/immutability.json`.
- Freeze: `lock.json`, SHA256 `781da0b28d63d1abae8bdcf546c42e5f8a6d428d35427961ffc300214c7d5dc0`; sync manifest `locked_files.txt`.
- Báo cáo này: `results/letter/sweep/s3/report.md`.

Chưa có `runs/`/`score/` S3 hoặc biểu đồ; đây là đúng phạm vi chuẩn bị.
S3 PASS/FAIL, thực tế CPU trên GCP và lợi ích trên mẫu mới chưa được xác nhận.
Bước tiếp là Claude chạy đúng một lần từ lock; không chỉnh ngưỡng sau outcomes.
