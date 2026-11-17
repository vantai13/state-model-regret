"""Doan Van Tai — reproduce the A2 report from saved training/pilot artifacts.

No simulator, test TM reader, cloud call or outcome computation is imported.
The concurrent congested job is described only by a read-only checkpoint.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'results/letter/v7_3'
OUT = BASE/'day_train'


def read(path):
    return json.loads(Path(path).read_text())


def write(path, text):
    with Path(path).open('x') as f:
        f.write(text)


def generate():
    config = read(OUT/'configuration.json')
    summary = read(OUT/'summary.json')
    pilot = read(OUT/'pilot/summary.json')
    audit = read(OUT/'verification_final_resume.json')
    assert audit['status'] == 'PASS' and audit['scenario'] == 'provisioned'
    assert summary['C_ref_all_train_pathwise_zero_certificate']
    pytest = (OUT/'pytest_resume_final.log').read_text().strip().splitlines()[-1]
    assert re.fullmatch(r'54 passed, 18 deselected in [0-9.]+s', pytest)
    with (OUT/'nonstationarity.csv').open() as f:
        rows = list(csv.DictReader(f))
    quantiles = {k: np.quantile([float(r[k]) for r in rows], [0, .25, .5, .75, 1]).tolist()
                 for k in ('slope_Mbps_per_hour', 'coefficient_of_variation')}
    night = read(BASE/'train/summary.json')
    congested = BASE/'day_train_congested'
    other = read(congested/'configuration.json')
    expected = {f'{r["id"]}_{d}' for r in other['regimes'] for d in other['train_dates']}
    complete = sorted(p.stem for p in (congested/'raw').glob('*.json')
                      if p.with_suffix('.npz').exists())
    assert set(complete) <= expected
    checkpoint = dict(
        snapshot_UTC=datetime.now(timezone.utc).isoformat(),
        scenario='congested_business_hours', read_only=True,
        complete_raw_pairs=len(complete), expected_raw_pairs=len(expected),
        complete_stems=complete,
        summary_present=(congested/'summary.json').exists(),
        pilot_summary_present=(congested/'pilot/summary.json').exists(),
        note='Concurrent pre-existing training advanced during resume. No second job, simulation or overwrite was launched for this scenario.',
        inherited_metadata_corrections={
            'capacity_identical_to_phase_A': dict(
                saved=other['capacity_identical_to_phase_A'],
                recomputed=other['capacity_Mbps'] == other['phase_A_capacity_Mbps']),
            'capacity_peak_utilization': dict(
                saved=other['capacity_peak_utilization'],
                recomputed=other['capacity_peak_driver']['load_Mbps']/other['capacity_Mbps'])})
    numbers = dict(
        owner='Doan Van Tai', training_only=True, test_days_simulated=0,
        sources={name: dict(path=str(OUT/name), sha256=hashlib.sha256((OUT/name).read_bytes()).hexdigest())
                 for name in ('configuration.json', 'summary.json', 'pilot/summary.json',
                              'verification_final_resume.json', 'nonstationarity.csv')},
        window=[config['window_start'], config['window_end']],
        train_days=len(config['train_dates']), test_weekdays_metadata_only=len(config['test_weekday_dates_metadata_only']),
        capacity_Mbps=config['capacity_Mbps'], regimes=config['regimes'],
        s_hat_Mbit=[r['s_hat_Mbit'] for r in summary['regimes']],
        T_int_defined_by_action=[r['T_int_defined_by_action'] for r in summary['regimes']],
        C_ref_pilot_Mbit_s=[r['C_ref_mean_Mbit_s'] for r in pilot['records']],
        projected_CPU_s=pilot['projected_CPU_s'],
        slower_day_projected_CPU_s=pilot['slower_day_projected_CPU_s'],
        nonstationarity_quantiles=quantiles, protected_files=audit['original_files_checked'],
        pytest=pytest, congested_checkpoint=checkpoint)
    write(OUT/'report_numbers.json', json.dumps(numbers, indent=2, ensure_ascii=False, allow_nan=False)+'\n')

    util_rows = '\n'.join(
        f"| {r['id']} | {100*r['max_mean_link_utilization'][0]:.6f}% | {100*r['max_mean_link_utilization'][1]:.6f}% | "
        f"{100*r['peak_15min_link_utilization'][0]:.6f}% | {100*r['peak_15min_link_utilization'][1]:.6f}% | "
        f"{100*r['modulated_upper_utilization'][0]:.6f}% | {100*r['modulated_upper_utilization'][1]:.6f}% |"
        for r in config['regimes'])
    paths = '\n\n'.join(
        f"`{r['id']}` quản lý `{r['managed_OD']}`, volume trung bình {r['train_window_mean_volume_Mbps']:.6f} Mbit/s. "
        f"Stay `{ ' → '.join(r['stay']) }`. Switch `{ ' → '.join(r['switch']) }`. "
        f"{'Tránh' if r['switch_avoids_busiest_link'] else 'Vẫn đi qua'} busiest Stay link."
        for r in config['regimes'])
    component_rows = '\n'.join(f'| {k} | {v:.6f} |' for k, v in pilot['CPU_s_by_component'].items())
    q = quantiles['slope_Mbps_per_hour']
    cv = quantiles['coefficient_of_variation']
    train_cpu = sum(r['full_train_component_CPU_s'] for r in summary['regimes'])
    cong_rows = '\n'.join(
        f"| {r['id']} | {r['max_mean_link_utilization'][0]:.6f} | {r['max_mean_link_utilization'][1]:.6f} | "
        f"{r['peak_15min_link_utilization'][0]:.6f} | {r['peak_15min_link_utilization'][1]:.6f} |"
        for r in other['regimes'])
    report = f'''# V7-3 Phase A2 daytime training và pilot

Người phụ trách **Doan Van Tai**. Báo cáo và kiểm chứng được trí tuệ nhân tạo (AI) thực hiện theo brief. Chưa có human review hoặc author-self confirmation từ công việc này.

Brief A2 gốc với capacity provisioned đã hoàn tất training, pilot và independent replay. Scenario congested được tác giả chọn trong commit `HEAD` `b11427824215a55e57a3908a5f544c43e40be802` đang có một job training riêng. Báo cáo ghi checkpoint của job đó và chưa nhận toàn bộ scenario congested hoàn tất. Không commit, kết nối qua Secure Shell (SSH) hoặc tính test-day outcome trong lượt resume.

## Phạm vi và cấu hình

Tiếp tục `V7_3_phaseA2_resume_brief.md` và `V7_3_phaseA2_brief.md` tại `HEAD`. Giữ {len(config['train_dates'])} train weekdays thuộc split Phase A, từ {config['train_dates'][0]} đến {config['train_dates'][-1]}. Có {len(config['test_weekday_dates_metadata_only'])} later test weekdays được đếm từ metadata. Không mở demand intensity hoặc outcome của test days. Exclusion rule Phase A được giữ nguyên, kể cả yêu cầu đủ warmup của ngày trước. Cache chỉ chứa training data.

Window được chọn là **{config['window_start']} đến {config['window_end']}**, tối đa mean total demand trên 73 starts trong ngày với bước 15 phút. Tổng demand trung bình **{config['mean_total_demand_Mbps']:.6f} Mbit/s**. Clock theo dữ liệu nguồn, timezone và daylight saving time (DST) chưa được xác nhận. Warmup Stay bắt đầu 08:15, trước decision hai giờ.

Uniform capacity **{config['capacity_Mbps']:.9f} Mbit/s**, trùng Phase A. Quy tắc dùng peak 15 phút trong train daytime 06:00 đến 21:45 chia 0,9. Busiest Stay link trong window là `{config['busiest_Stay_link']}`. Top ba cặp origin-destination (OD) được chọn theo mean volume, giữ cả OD có second-shortest path vẫn qua link đó.

{paths}

Truth giữ real 15-minute traffic matrices nhân two-state OD modulation độc lập, β=0,3 và flip rate 1/s. Truth dt=0,05 s. M0 dùng train-average weekday profile. Hybrid cộng h·ŝ vào gap Switch trừ Stay. Stationary chọn Switch khi ŝ âm. c=0 và exact ties chọn Stay. Stale telemetry có tuổi 5 hoặc 15 phút, posterior K=64 dưới Stay. Các horizons 1, 2, 4 và 6 giờ lấy từ cùng rollout.

## Utilization của provisioned

Mean là max theo link sau khi lấy trung bình trên ngày và slot. Peak là max 15-minute mean trong window. Upper nhân peak với 1,3, chặn mọi fast-mode realization.

| Regime | Mean Stay | Mean Switch | Peak Stay | Peak Switch | Upper Stay | Upper Switch |
|---|---:|---:|---:|---:|---:|---:|
{util_rows}

Warmup Stay có upper utilization **{config['warmup_Stay_modulated_upper_utilization']:.9f}**. Forecast của cả ba regimes có upper **{max(config['forecast_modulated_upper_utilization_by_regime']):.9f}**. Các envelope đều dưới capacity, nên từ empty initial queues, mọi queue trong training window luôn bằng 0 dưới cả hai actions. Đây là chứng chỉ theo offered-load envelope và được raw outputs xác nhận.

## Training outputs

Đủ **78/78 regime-day records**, N=200 mỗi regime-day, tức 5.200 instances mỗi regime. Training seed **7302001** và pilot seed **7372001**, tách biệt. K=64 cho mỗi stale age. Thời gian tính toán trên central processing unit (CPU) từ artifacts có sẵn **{train_cpu:.6f} CPU-s**. Training đã hoàn tất trước lượt resume, các raw records được dùng lại và kiểm toán, không chạy lại.

| Regime | Mean backlog rate Stay / Switch (Mbit) | ŝ (Mbit) | Conditional Monte Carlo (MC) standard error (SE) (Mbit) | Positive / zero / negative days | Directional sign stability |
|---|---:|---:|---:|---|---|
| `DAY1` | 0 / 0 | 0 | 0 | 0 / 26 / 0 | Không xác định |
| `DAY2` | 0 / 0 | 0 | 0 | 0 / 26 / 0 | Không xác định |
| `DAY3` | 0 / 0 | 0 | 0 | 0 / 26 / 0 | Không xác định |

Exact-zero share là 26/26 cho mỗi regime. M0 exact tie share **100%**, fresh và cả hai stale ages, ở cả bốn horizons. Mẫu số cho mỗi regime, horizon và side là 5.200 decisions. K posterior samples không được đếm thành independent decisions. Hybrid và Stationary cũng chọn Stay trong pilot. Không có bằng chứng superiority của một pipeline từ các zero costs này.

T_int dùng first-zero integrated autocovariance estimator của letter trên instance 0 từng ngày và action, không nối ngày. **156/156 traces** ở dt=0,05 s có zero variance. Check bổ sung dùng rollout đầu tiên của mỗi regime trên train day sớm nhất ở dt=0,005 s, rồi subsample 0,01 và 0,05 s. Cả 18 action/grid checks vẫn zero variance. Do đó **T_int và 6h/T_int không xác định**, không báo T_int bằng dt, bằng 0 hoặc ratio vô hạn. Check này không tạo một correlation scale khi backlog hằng 0.

Trong window, ordinary least squares (OLS) total-demand slope theo slot midpoint có min/q25/median/q75/max **{q[0]:.6f}, {q[1]:.6f}, {q[2]:.6f}, {q[3]:.6f}, {q[4]:.6f} Mbit/s mỗi giờ**. Coefficient of variation có min/median/max **{cv[0]:.6f}, {cv[2]:.6f}, {cv[4]:.6f}**. Có nonstationarity trên input, dù queue vẫn bằng 0. Các rate và T_int chỉ mô tả finite training windows.

## Pilot và compute projection

Lượt resume đã chạy hai train days **{pilot['pilot_dates'][0]}** và **{pilot['pilot_dates'][1]}**, ngày sớm nhất và ngày có tổng window demand cao nhất. Ba regimes tạo sáu end-to-end pilot records. N=2, giữ full K=64, R_dec=64, R_eval=128. Reference decision và evaluation dùng seed streams khác nhau, evaluation common random numbers (CRN) ghép hai actions. **C_ref=0 Mbit·s** cho cả bốn horizons ở mọi pilot record. M0, Hybrid và Stationary có regret=0 và G_S=0 Mbit·s. Các tỷ lệ chia C_ref không xác định.

Projection cho 50 test weekdays × 3 regimes × N=200, 20 workers trên n2-standard-32, nhân N với 200/2. K và R đã dùng full size trong pilot.

| Component | Projected CPU-s |
|---|---:|
{component_rows}

Mean-day projection **{pilot['projected_CPU_s']:.6f} CPU-s = {pilot['projected_CPU_hours']:.6f} CPU-hours**, ideal 20-worker wall **{pilot['ideal_wall_s_20_workers']:.6f} s**. Chọn ngày chậm hơn riêng từng component và regime cho **{pilot['slower_day_projected_CPU_s']:.6f} CPU-s**, ideal wall **{pilot['slower_day_ideal_wall_s_20_workers']:.6f} s**. Đây là projection từ local pilot, không đo tốc độ n2-standard-32. Các exact-empty-queue shortcuts làm workload này rất nhỏ. Không áp projection này cho congested. Pilot timing có overhead và CPU threads của NumPy, còn verification/tests được chạy với OPENBLAS_NUM_THREADS=1. Hai phép ngoại suy không có confidence interval (CI) hoặc upper-bound guarantee cho test workload.

## Night scope observation giữ riêng

Phase A night artifacts giữ nguyên byte. Train mean backlog rate Stay **{night['mean_backlog_rates_Mbit'][0]:.12g} Mbit**, Switch **{night['mean_backlog_rates_Mbit'][1]:.12g} Mbit**, ŝ **{night['s_hat_Mbit']:.12g} Mbit**. M0 ties 100%, C_ref=0 trên hai train-night pilots. Night và provisioned daytime là scope observations của objective chỉ tính backlog với c=0. Không gộp zero regret thành bằng chứng về hiệu quả trên test.

## Congested scenario đang chạy riêng

Theo `notes/ops/codex/V7_3_congested_decision.md`, giữ window, flows, paths và data, đặt capacity **{other['capacity_Mbps']:.9f} Mbit/s** để busiest Stay link có window-mean ρ=0,9.

| Regime | Mean Stay | Mean Switch | Peak Stay | Peak Switch |
|---|---:|---:|---:|---:|
{cong_rows}

Checkpoint lúc **{checkpoint['snapshot_UTC']}** có **{len(complete)}/{len(expected)}** complete raw JavaScript Object Notation (JSON)/NumPy zipped archive (NPZ) pairs. Full summary hiện có `{checkpoint['summary_present']}`, pilot summary hiện có `{checkpoint['pilot_summary_present']}`. Số rows đã tăng trong lúc resume, nên không launch một training job trùng. Chưa báo ŝ pooled, sign stability, full T_int, C_ref hoặc compute projection cho congested từ subset đang chạy.

Hai metadata fields trong congested configuration được kế thừa từ provisioned và còn giá trị cũ. `capacity_identical_to_phase_A` lưu true nhưng phép so capacity hiện tại cho false. `capacity_peak_utilization` lưu 0,9 nhưng daytime peak-driver load chia capacity mới là **{checkpoint['inherited_metadata_corrections']['capacity_peak_utilization']['recomputed']:.9f}**. Các trường utilization mới trong `regimes` đã dùng capacity congested. Ghi correction ở `day_train/report_numbers.json`, giữ configuration và running source nguyên byte.

## Kiểm chứng, file và command

Bộ kiểm tra đạt **{pytest}**. Gồm Phase A/A2/congested controls, ba E4 regression controls, và sáu nonzero/corruption controls cho independent replay. Test corruption kiểm reference khác evaluation, tie chọn Stay, signed G_S và khả năng empirical regret âm. Không chạy full repo suite ngoài scope.

Independent saved-artifact replay `PASS`, không gọi simulator. Kiểm 73 windows, 432 link rows, 156 day-utilization rows, 78 training records, sáu pilot records, raw rates/SE/signs/ties/autocovariance, C_ref/reference/CRN/regret/G_S và projection. **{audit['original_files_checked']} protected file hashes khớp**, gồm night artifacts và V7-1 đã scored. `git diff --exit-code` `PASS` trước báo cáo. `HEAD` không đổi trong lượt resume.

Verifier cũ `v7_3_day_verify.py` vẫn nguyên byte trong source provenance. Kiểm tra `HEAD` của bản đó quá chặt đối với các commit V7-1 đã được brief cho phép. Entrypoint kiểm chứng hiện dùng là `v7_3_a2_verify.py`, kiểm committed brief không đổi qua các `HEAD` và hashes hiện hành. Scientific runner, seeds, sample counts và outputs đã có được giữ nguyên.

Command thực tế của lượt resume được ghi dưới đây. Training command lịch sử nằm ở `day_train/train.time`, không chạy lại trong lượt này.

```bash
python3 -m pytest -q tests/test_letter_v7_3.py tests/test_letter_v7_3_day.py tests/test_letter_v7_3_cong.py -p no:cacheprovider
/usr/bin/time -v -o results/letter/v7_3/day_train/pilot.time python3 -u -m experiments.letter.v7_3_day pilot
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_letter_v7_3.py tests/test_letter_v7_3_day.py tests/test_letter_v7_3_cong.py tests/test_letter_v7_3_a2.py tests/test_letter_e4.py -k 'v7_3 or exact_ties_stay or per_action_evaluation or constant_rhat'
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 -u -m experiments.letter.v7_3_a2_verify --output verification_final_resume.json
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.letter.v7_3_a2_report
git diff --exit-code
```

Source mới gồm `experiments/letter/v7_3_a2_verify.py`, `experiments/letter/v7_3_a2_report.py` và `tests/test_letter_v7_3_a2.py`. Code A2 dở dang `experiments/letter/v7_3_day.py`, verifier cũ và `tests/test_letter_v7_3_day.py` được review và giữ byte. Configuration/protocol, raw JSON/NPZ, utilization/nonstationarity comma-separated values (CSV), resolution traces, summary và pilot nằm trong `results/letter/v7_3/day_train/`. Logs của lượt này là `pytest_resume_preflight.log`, `pytest_resume_final.log`, `pilot.log`, `pilot.time`, `verify_resume.log`, `verify_final_resume.log` và các file `.time` tương ứng. Numbers ledger là `day_train/report_numbers.json`. Không tạo biểu đồ.

## Đề xuất và điều chưa xác nhận

Giữ provisioned cùng night như các scope controls có C_ref bằng 0. Scenario congested đã được tác giả chọn trước test, cần full training và hai-train-day pilot của job riêng trước khi viết test card. Giữ `DAY3` dù Switch vẫn qua bottleneck, tránh đổi flow selection sau khi thấy outcomes. Nếu congested T_int bị chi phối bởi daily profile, có thể đề xuất kiểm estimator theo window và detrending trong một bước diagnostic riêng. Chưa áp thay đổi đó.

Nghiên cứu còn một số hạn chế. Thứ nhất, fast modulation và uniform capacity là giả định tổng hợp trên real traffic matrices. Thứ hai, current evidence chỉ thuộc train và timing pilot nhỏ, chưa xác nhận test performance hoặc stationary mixing. Cuối cùng, local compute projection có thể khác khi workload có congestion và khi chạy trên Google Cloud Platform (GCP). Phase A2 gốc đã hoàn tất về kỹ thuật, còn full congested scenario đang chạy riêng.
'''
    write(BASE/'PHASE_A2_REPORT.md', report)
    print(BASE/'PHASE_A2_REPORT.md')
    return numbers


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    generate()
