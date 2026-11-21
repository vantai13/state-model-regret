# S3 CTMC — chuẩn bị và bàn giao

Người phụ trách: **Doan Van Tai**. Theo `BRIEF_S3_CTMC.md`, thẻ gốc ở
`results/letter/sweep/s3/CARD_S3.md` giữ nguyên. Codex chỉ sample, test, pilot
tài nguyên (tối đa 3 regime ngoài mẫu), lock; Claude chạy truth trên GCP.
Không commit hoặc SSH trong nhiệm vụ chuẩn bị.

## Thiết kế được giữ nguyên

600 regime đủ điều kiện đầu tiên theo Sobol mới; ID giữ chỉ số ứng viên,
không đánh số lại sau loại. Wrapper gọi sampler, stationary resource screen,
estimator và evaluator S1-A, không sửa file cũ. Resource screen gồm initial
screen S1-A và cost envelope từ pilot S1-A v2; pilot mới không thay mẫu/screen.
Lưới 14 horizon × 3 tuổi × 8 luật, record 300 T_int, strict ties về Stay,
truncation/cap/fallback đều giữ nguyên. Hai shard chia theo parity của chỉ số
ứng viên như runner cũ; mỗi shard đúng 15 worker.

Seeds:

| Mục đích | Seed |
|---|---:|
| Sobol S3 | 630951401 |
| Record S3 | 630951402 |
| Sobol pilot riêng | 630951403 |
| Record pilot riêng | 630951404 |

Record stream giữ `SeedSequence([record_seed, candidate_index]).spawn(2)`
như S1-A. `sample/seeds.json` ghi kiểm tra collision trên dữ liệu cũ; seed
chưa ghi nhận hoặc công thức tùy ý ngoài repo không thể được kiểm chứng.

## Chuẩn bị local (đã chạy thì không chạy lại)

```bash
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
python3 -B -m experiments.letter.s3_ctmc.runner sample
python3 -B -m pytest -q -s -p no:cacheprovider \
  --basetemp results/letter/sweep/s3/checks/pytest_final \
  experiments/letter/s3_ctmc/test_s3_ctmc.py tests/test_sweep_ctmc.py
python3 -B -m experiments.letter.s3_ctmc.runner pilot
python3 -B -m experiments.letter.s3_ctmc.runner lock
python3 -B -m experiments.letter.s3_ctmc.runner verify-lock
bash -n experiments/letter/s3_ctmc/s3_gcp.sh
```

Sample config, seed audit, số loại và hai dự phóng chi phí ở `sample/`.
`sample/projection.json` dùng timings/work của 1000 receipt S1-A GCP và ghi
riêng envelope bảo thủ của pilot S1-A; không dùng benefit để fit chi phí.
Pilot riêng dùng lưới timing S1-A `{0.1,1} × {0.3}`, không chấm hoặc xem
scientific outcomes để chọn mẫu/ngưỡng. Raw pilot được giữ để audit.

## Launch bàn giao Claude (chưa chạy local)

Trên `n2-highcpu-32`, thư mục `~/smr`, sau khi sync toàn bộ file thuộc lock,
Claude dùng SHA256 cụ thể trong báo cáo bàn giao, không tạo lock mới trên VM:

```bash
cd ~/smr
export S3_LOCK_SHA256=<SHA256-trong-bao-cao-ban-giao>
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
python3 -B -m experiments.letter.s3_ctmc.runner verify-lock --expected-sha "$S3_LOCK_SHA256"
bash experiments/letter/s3_ctmc/s3_gcp.sh 0 &
s3_pid0=$!
bash experiments/letter/s3_ctmc/s3_gcp.sh 1 &
s3_pid1=$!
wait "$s3_pid0"
wait "$s3_pid1"
```

Đây là các lệnh trong driver của Claude, không phải hướng dẫn giữ phiên SSH
mở. Driver phải thu exit code cả hai shard và đảm bảo `sudo -n poweroff`
trên exit, sau đó revert `n2-custom-12-49152`, để VM `TERMINATED`. Script
shard không poweroff; có timeout 6 giờ/shard và log `PIPELINE_START/EXIT`.
Log/started marker/receipt/raw đều exclusive-create; cấm retry/resume.
Lỗi hoặc interrupt phải giữ artifact và báo INCOMPLETE.

## Chấm sau khi Claude lấy và commit raw

Sau rsync + checksum và commit raw, dùng đúng lock trước truth:

```bash
python3 -B -m experiments.letter.s3_ctmc.score_s3 --expected-lock-sha "$S3_LOCK_SHA256"
python3 -B -m experiments.letter.s3_ctmc.rescore_s3 --expected-lock-sha "$S3_LOCK_SHA256"
```

Scorer chỉ nhận hai receipt đủ đúng 600 ID và raw khớp hash, parameters,
namespace, purpose, record seeds; không nhận pilot. Output chỉ ở `score/`,
mọi file mở `x`. T1/T2/T3 dùng h/T_int=1, fresh, hat và d*=0.28 cố định.
`D_hat = mean_tau(D_fresh + D_stale)` đúng S2 H-C, khác share bất đồng thật;
không dùng regret/C_ref để định vùng. Δ tính từ paired regret với cùng C_ref,
trung bình đều ba tuổi trong regime trước CI Student t.

INVALID ở lại mẫu số N=600, không gán Δ=0 hay loại để tăng coverage. Nếu
không biết D/paired outcome thì chưa thể xác nhận mean của vùng/complement:
các mean test bị ảnh hưởng NOT_EVALUABLE; luôn báo số unknown riêng. |R|<5
làm T2 NOT_EVALUABLE; ngoài R<5 làm T3 NOT_EVALUABLE. Chỉ PASS khi cả ba PASS.

Output gồm summary T1/T2/T3, baseline/hybrid, harm counts ≤−0.05/−0.1,
packet·s và CI, fallback/INVALID, hai secondary đã định trước, bảng mọi h,
fresh/stale và true/hat, paired CSV để kiểm lại. Rescorer không import scorer
hoặc analyzer; tính D từ raw policy rows và dùng arithmetic độc lập. Test
S1-A chỉ ghi dưới `checks/`, không tạo `score/` và không phải kết quả S3.

CI là mô tả finite resource-screened Sobol panel, không là population
guarantee. CTMC truncated có tail certificate, không symbolic exact.
