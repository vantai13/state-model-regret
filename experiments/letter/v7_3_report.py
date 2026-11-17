"""Doan Van Tai — regenerate Phase A report from saved train/pilot artifacts.

No simulator calls and no test traffic input. Output is exclusive-create.
"""
import json
from pathlib import Path

import numpy as np

from experiments.letter import v7_3_data as D


def report(out=D.OUT):
    read=lambda p:json.loads((out/p).read_text())
    manifest,config,train,pilot,verify=[read(p) for p in (
        'data_manifest.json','train/configuration.json','train/summary.json','pilot/summary.json',
        'verification_final.json' if (out/'verification_final.json').exists() else 'verification.json')]
    tr,cf=D.load_training(out=out)
    net=D.topology();inc=cf['incidence'];cap=float(cf['capacity'].item())
    loads=np.einsum('nsd,aed->nsae',tr['days'][:,:24],inc,optimize=True)/cap
    rows=[]
    for a,action in enumerate(['Stay','Switch']):
        for e,link in enumerate(net['links']):
            rows.append(dict(action=action,link=link['id'],
                             removed_in_Switch=link['id'].split(':')[0] in config['removed'],
                             mean_night_utilization=float(loads[:,:,a,e].mean()),
                             max_15min_night_utilization=float(loads[:,:,a,e].max())))
    D.T.write_csv(out/'train/link_utilizations.csv',rows)
    timing_rows=[]
    for date in pilot['pilot_dates']:
        meta=read(f'pilot/{date}.json')
        timing_rows += [dict(date=date,component=k,**v) for k,v in meta['timings'].items()]
    D.T.write_csv(out/'pilot/component_timings.csv',timing_rows)
    removed='\n'.join(f'- `{name}`' for name in config['removed'])
    ti_rows=[]
    for item in verify['T_int_details'][1]:
        ti_rows.append(f"| {item['date']} | {item['T_int_s']:.9f} | {item['h6_over_T_int']:.3f} |")
    pos=[]
    for date in tr['dates']:
        r=read(f'train/raw/{date}.json')
        if r['s_hat_Mbit']>0:
            pos.append(f"| {date} | {r['s_hat_Mbit']:.12g} |")
    time_table=[]
    for name, projected in pilot['CPU_s_by_component'].items():
        values=[r['CPU_s'] for r in timing_rows if r['component']==name]
        time_table.append(f'| {name} | {values[0]:.9f} | {values[1]:.9f} | {projected:.6f} |')
    train_first,train_last=manifest['train_dates'][0],manifest['train_dates'][-1]
    test_first,test_last=manifest['test_dates'][0],manifest['test_dates'][-1]
    text=f'''# V7-3 Phase A — GÉANT night consolidation

Người phụ trách: **Doan Van Tai**. Code, phép tính và báo cáo do AI thực hiện theo brief;
không phải author-self work hoặc independent human review.

**Hoàn tất Phase A: dữ liệu, code, training và pilot. Chưa có test-night outcome,
chưa có test card và không kết luận hiệu quả trên test. Không commit.**
Brief tại HEAD khi bắt đầu `{read('PHASE_A_PROTOCOL.json')['brief_commit']}`.

## Dữ liệu và split (chỉ metadata/completeness trên test)

- [Official SNDlib dynamic-matrices index]({manifest['official_index_url']}) xác nhận đúng archive;
  HTML đã lưu ở `sndlib_dynamic.html`. Download URL: {manifest['source_url']}.
- Archive {manifest['bytes']:,} bytes; SHA256 `{manifest['sha256']}`.
  Native format 1.0, đơn vị Mbit/s; HTTP Last-Modified
  `{manifest['archive_http_headers']['Last-Modified']}`. Đây là HTTP version metadata,
  không tự suy một semantic release number. Topology SHA256
  `{manifest['topology_sha256']}`.
- {manifest['n_tm_files']:,} TM files, {manifest['n_valid_tm']:,} hợp lệ;
  {len(manifest['invalid'])} file có DEMANDS rỗng được loại theo parser viết trước ingestion.
  OD vắng trong sparse TM được hiểu là demand 0; không đồng nghĩa cả TM bị mất.
- Khoảng timestamp: {manifest['date_range'][0]} → {manifest['date_range'][1]}.
  Clock giữ nguyên từ nguồn; timezone/DST chưa xác nhận.
- Train window là 42 ngày lịch đầu: 04/05–14/06/2005; cutoff **15/06/2005**,
  áp trước completeness filtering. Giữ **{len(manifest['train_dates'])} train nights**
  ({train_first} → {train_last}) và **{len(manifest['test_dates'])} test nights**
  ({test_first} → {test_last}); loại {len(manifest['dropped_nights'])} ngày/đêm.
  Danh sách ngày và slot thiếu/hỏng nằm đầy đủ trong `data_manifest.json`.
- Ngày hợp lệ phải đủ 96 TM quarter-hour và đủ 8 TM warmup 22:00–23:45 hôm trước.
  Không lọc theo mức tải, cost hay model output. Parser zero-fill OD vắng trong
  universe 462 directed ODs, kiểm node/OD/unit/negative/nonfinite/duplicate/time.
  Quy tắc và clarification schema trước ingestion: `PHASE_A_PROTOCOL.json`.
- Raw archive và cache **train-only** ở `{D.T.data_root()}`; cache
  `v7_3_train.npz` không chứa test dates. Test TM chỉ đọc để parse/hash/validity;
  không tính link load, forecast truth, state, decision hoặc cost của test nights.

## Scenario triển khai, không đổi thiết kế trong brief

GÉANT: 22 nodes, 36 undirected physical links = 72 directed queues. Stay dùng
min-hop/lexicographic complete node-sequence tie rule của EV-TE. Capacity uniform
**{cap:.9f} Mbit/s** = busiest Stay train-daytime 15-min mean / 0.9;
daytime convention là 06:00–21:45. Peak utilization kiểm lại =
**{config['daytime_peak_utilization']:.15f}**.

Thứ tự xét link cố định theo initial train-mean 00:00–06:00 bidirectional load,
tie theo link ID. Tắt cả hai directions, skip bridge; dừng trước lần connected
removal đầu tiên vượt train-mean utilization 0.8. Chỉ OD có đường hiện tại đi qua
link bị bỏ mới reroute. Đã tắt **{len(config['removed'])}/36 physical links**,
giữ 21 links, connected (một tree); không gặp stop vì utilization.

{removed}

| Configuration | Busiest link, train-mean night utilization | Maximum individual 15-min train-night utilization |
|---|---:|---:|
| Stay | {100*max(config['nighttime_utilization_mean_by_action'][0]):.6f}% | {100*max(config['nighttime_utilization_max_by_action'][0]):.6f}% |
| Switch | {100*max(config['nighttime_utilization_mean_by_action'][1]):.6f}% | {100*max(config['nighttime_utilization_max_by_action'][1]):.6f}% |

Các utilization trên chưa nhân fast modulation. Per-link có 144 rows trong
`train/link_utilizations.csv`; per-night/config có 76 rows trong
`train/night_utilizations.csv`. Removed links/routing/profile nằm trong
`train/configuration.json` và `.npz`; weekday/weekend forecast có 26/12 train dates.

Truth là per-link fluid queue của EV-TE, actual 15-min TM piecewise constant nhân
independent two-state OD modulation 1±0.3, kappa=1/second, không slow mode.
dt=0.05 second; dùng nguyên EV-TE RNG/Sparse/fluid-step source qua import,
mở rộng riêng adapter cho TM thay đổi, giữ queue của **cả hai actions** qua slot.
Constant-TM adapter đã so bitwise với EV-TE. Mean rollout gọi `T.twin_costs`;
conditional mean mode decay exp(-2t) tiếp tục xuyên slot.

Warmup Stay từ empty queue lúc 22:00, independent seed từng instance; lưu full
OD modes + directed-link queues tại 23:45, 23:55, 00:00. 5/15-min telemetry chỉ
khác age. Posterior dùng actual past TM của slot 23:45, dưới Stay. M0 future
chỉ dùng weekday/weekend train-average profile; không dùng actual future của
đêm cần ra quyết định. Hybrid gap = M0(Switch−Stay)+h·ŝ; Stationary chọn rate nhỏ hơn.
Exact ties chọn Stay theo E4. h=1/2/4/6 giờ lấy từ cùng rollout, c=0.

Certified optimization: link có empty queue và (1+beta)·load≤capacity xuyên interval
không thể phát sinh backlog; chỉ fast-forward mode endpoint theo đúng E4 chain law.
OD không thể tác động cost được marginalize với independent conditional endpoint.
Đây là phép rút gọn có chứng chỉ, không threshold nhỏ/epsilon; không sửa native engine.
Action CRN dùng chung mode path; reference decision và evaluation dùng hai seed streams riêng.

## Training-only results

N=200 mỗi đêm, 38 đêm = **7.600 instances**; K=64 cho mỗi stale age.
Train seed 730001; pilot seed 7370001; test seed 7390001 **chưa dùng**.
Rate là finite-night mean, không khẳng định stationary distribution của TM đang giảm.

| Quantity | Stay | Switch |
|---|---:|---:|
| Mean 00:00–06:00 backlog cost rate (Mbit) | {train['mean_backlog_rates_Mbit'][0]:.12g} | {train['mean_backlog_rates_Mbit'][1]:.12g} |
| Defined network-backlog T_int nights, trace instance 0 | 0/38 | {verify['T_int_defined'][1]}/38 |

**ŝ = Switch−Stay = +{train['s_hat_Mbit']:.12g} Mbit**. Conditional Monte Carlo SE
**{verify['s_hat_conditional_MC_SE_Mbit']:.12g} Mbit**, chỉ cho synthetic randomness trên
38 fixed train TMs; không phải uncertainty về population nights hay test.
Across-night median ŝ=0. Sign counts: **4 positive / 34 exact zero / 0 negative**.
Strict same-sign fraction so với pooled positive sign = **4/38 = 10.526316%**;
không gộp zero vào positive để nhận sign stability cao.

| Train date có ŝ>0 | ŝ (Mbit) |
|---|---:|
{chr(10).join(pos)}

M0 exact tie share **100%** ở h=1/2/4/6h, fresh và stale tau=5/15min
(7.600 decisions/h/side/age; K posterior samples không phải independent decisions).
Từ M0 costs=0 và ŝ>0 suy ra Hybrid và Stationary đều chọn Stay.
Đây là suy luận từ kết quả train-only; pilot bên dưới kiểm tra trực tiếp.

T_int dùng đúng FFT unbiased autocovariance/first-zero trapezoid estimator của letter.
Để lưu và kiểm toán full-resolution series, **một instance đã chọn trước (ID 0)
trên mỗi train night/config** được ghi backlog mỗi 0.05s; rates/ties vẫn dùng đủ N=200.
Không nối các đêm thành một chuỗi, không báo zero-variance như T_int=0 hay h/T_int=infinity.

| Train date | T_int Switch (s) | 6h / T_int |
|---|---:|---:|
{chr(10).join(ti_rows)}

Stay **38/38 undefined**, Switch **35/38 undefined** do zero-variance first-instance trace.
Có 4 nights ŝ>0 nhưng chỉ 3 first-instance traces có event: một trace không đại diện
toàn bộ 200 trajectories. T_int≈0.063s chỉ ≈1.26 grid steps, chưa resolved như
continuous-time correlation scale; mọi h/T_int trên chỉ mô tả grid và trace này.
Không có CI/population claim. Backlog occupancy/max và lỗi estimator được giữ ở raw JSON.

Nonstationarity: OLS total-demand slope theo 24 slot midpoints 00:00–06:00,
đơn vị Mbit/s per hour; min/q25/median/q75/max =
**{', '.join(f'{x:.6f}' for x in train['nonstationarity_slope_quantiles_Mbps_per_hour'])}**.
38/38 slopes âm. `train/night_statistics.csv` ghi từng đêm.
Measured training component CPU = **{train['total_measured_component_CPU_s']:.6f} CPU-s**;
không tính toàn bộ ingestion/compression/checksum/FFT/report overhead vào số component này.

### Vì sao outcome suy biến trên train/pilot

Train-only pathwise upper bounds: Stay warmup utilization max
**{verify['envelope_max_utilization']['warmup_Stay']:.9f}**, Stay night max
**{verify['envelope_max_utilization']['train_night_Stay']:.9f}**, cả hai M0 forecast configs max
**{verify['envelope_max_utilization']['M0_profile_both_actions']:.9f}**, đều <1 kể cả +30% modulation.
Do đó warm/fresh/posterior Stay queue là zero; mean forecasts cả hai configs không
phát sinh queue từ đó. M0 cost tie là hệ quả của envelope, không phải numerical underflow.
Stay actual cost 0 trên train; occasional Switch bursts làm ŝ≥0.
Không tự đổi capacity, beta, objective, threshold hoặc tie rule để tạo effect.

## Pilot và compute projection (hai đêm train)

Pilot dùng **{', '.join(pilot['pilot_dates'])}**, lần lượt earliest eligible weekday/weekend,
chọn trước trong protocol. N=2, K=4, R_dec=4, R_eval=8, h và tau giữ nguyên.
Mỗi đêm chạy end-to-end: warm → fresh/stale twins → fresh true-model reference decision
→ independent paired evaluation → regret và G_S. C_ref=0 ở cả bốn horizons;
mọi pipeline/side/age regret=0 Mbit·s và G_S=0 Mbit·s, absolute.
Regret/C_ref và G_S/C_ref **undefined**, không đổi mẫu số hoặc ghi 0%.

| Component | 2005-05-05 CPU-s | 2005-05-07 CPU-s | Projected full-test CPU-s |
|---|---:|---:|---:|
{chr(10).join(time_table)}

Full plan (chưa chạy): 69 test nights × N=200 = 13.800 instances,
K=64 mỗi age, R_dec=64, R_eval=128. Future paths dùng CRN cho hai configs và chung
bốn horizons: 2.649.600 six-hour paired future paths, không nhân thêm 4 cho horizons.
Projected từ mean hai pilot nights và linear sample-count scaling:
**{pilot['projected_CPU_s']:.6f} CPU-s = {pilot['projected_CPU_hours']:.6f} CPU-hours**.
Với **20 independent workers trên n2-standard-32**, ideal wall
**{pilot['ideal_wall_hours_20_workers']:.6f} giờ** nếu tốc độ mỗi core giống máy đo.

Máy thực đo: {pilot['hardware']['processor']}, WSL2, Python {pilot['hardware']['python']},
OPENBLAS_NUM_THREADS=1. Không có measurement trên n2; không SSH/bật VM trong phase này.
Hai pilot có workload rất khác nhau (weekday có potential overload, weekend có chứng chỉ zero).
Stress proxy dùng đêm train tốn CPU nhất {pilot['stress_train_night']}:
N=200 rollout **{pilot['stress_full_train_rollout_CPU_s']:.6f} CPU-s**; thay future components
bằng 192 lần cost này mỗi night → **{pilot['stress_projected_CPU_s']:.6f} CPU-s**,
ideal 20-worker wall **{pilot['stress_ideal_wall_hours_20_workers']:.6f} giờ**.
Đây không phải upper bound/CI hoặc cloud benchmark: chưa biết test workload,
CPU khác, contention, marshaling, I/O và sample-size scaling có thể làm sai projection.

## Kiểm chứng thực tế

- 22 new tests PASS + 3 E4 regression tests PASS (25 total, 18 unrelated E4 tests deselected).
  Native parser semantic round trip/presence, invalid data, calendar split, connectivity,
  unaffected-route preservation, capacity 0.9, consolidation stop, exact EV-TE constant-TM
  regression, slot queue continuity, CRN identical decisions/actions, known-answer toy,
  analytical conditional-mean path, certified endpoint law, và no-test-date guard.
- Independent saved-artifact replay **PASS**: không import scorer/simulator,
  tính lại rates/ŝ/signs/T_int/slopes/CRN selection/regret/G_S/projection.
  {verify['checks']-len(json.loads((out/'initial_tracked_sha256.json').read_text()))} counted consistency checks
  và {len(json.loads((out/'initial_tracked_sha256.json').read_text())):,} tracked file hashes;
  **0 original tracked files changed**, brief/imported source giữ nguyên byte.
  HEAD tiến do concurrent V7-1/V7-2 note commits; lượt V7-3 không commit.
  `verification.json` là snapshot trước khi HEAD tiến, `verification_final.json`
  kiểm lại sau đó: chỉ nới kiểm tra HEAD thành ancestor + same committed brief,
  không sửa scientific code hoặc rerun simulator. V7-1/V7-2 không bị sửa.
- Giữ failure logs: initial toy stop fixture chưa tạo load trên reverse edge như kỳ vọng
  (đã sửa fixture); train launch 1 scalar conversion shape (NPZ promotes scalar to 1D),
  launch 2 ctypes non-C-contiguous output buffer (đã sửa adapter, thêm regression).
  Hai launch dừng trước khi tạo scientific night output. Final training và pilot complete,
  không test-night outcome/rerun được thực hiện.

Command thực tế (thêm env `PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1`):

```bash
.venv/bin/python -u -m experiments.letter.v7_3_data ingest
.venv/bin/python -u -m experiments.letter.v7_3_data configure
.venv/bin/python -u -m experiments.letter.v7_3_run train
.venv/bin/python -u -m experiments.letter.v7_3_run pilot
.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=results/letter/v7_3/pytest_tmp tests/test_letter_v7_3.py tests/test_letter_e4.py -k 'v7_3 or exact_ties_stay or per_action_evaluation or constant_rhat'
.venv/bin/python -m experiments.letter.v7_3_verify
.venv/bin/python -m experiments.letter.v7_3_verify --output verification_final.json
.venv/bin/python -m experiments.letter.v7_3_report
```

Các artifacts dùng exclusive-create; command lặp lại vào cùng output sẽ từ chối overwrite.
Không chạy full repo test suite; checks được giới hạn ở scenario và imports liên quan,
tránh các runs và guards frozen không liên quan của repo.

## Đề xuất cho Claude trước card — chưa áp dụng

1. **Cân nhắc lại objective của use case consolidation**: cost chỉ có backlog và c=0,
   không có benefit cho tiết kiệm link/energy; Stay đã có zero cost trên toàn train.
   Nếu bổ sung energy reward/tradeoff thì cần brief/card mới, units và weight có căn cứ;
   không thêm reward trong phase A này. Nếu giữ objective hiện tại, đọc đây là zero-cost
   control, không dùng zero regret như bằng chứng Hybrid thắng.
2. **Nếu muốn câu hỏi congestion có thể phân biệt model/state**, cần thiết kế train-only mới
   với activity dưới cả configs và negative controls, không tune theo test outcomes.
   Capacity rule/beta/consolidation hiện tại giữ nguyên; phase A không tự mở load sweep.
3. **Khóa reporting khi C_ref=0**: giữ absolute Mbit·s + N/A cho normalized regret,
   và action/tie shares. Không tự đổi sang một mẫu số thuận lợi. Claude quyết định card.
4. **Khóa units/numerics/domain**: một E4 fast unit=second là convention; timezone,
   daytime=06:00–22:00 và treatment of inherited off-link backlog cần nói rõ trước card.
   Hiện adapter giữ service drain như EV-TE (actual warmup queues ở đây đều zero).
   dt sensitivity train-only sẽ cần trước khi claim T_int liên tục ở trace≈0.063s;
   không tự chạy refinement hoặc dùng h/T_int undefined để nhận test PASS.

Synthetic fast modulation, per-link offered-load queue (không downstream shaping),
in-sample operator forecast, one-trace T_int, nonstationary finite nights và local-to-cloud
projection là limitations. Không literature/novelty claim, không author understanding PASS.

## File giao lại

- Source mới: `experiments/letter/v7_3_data.py`, `v7_3_sim.py`, `v7_3_run.py`,
  `v7_3_verify.py`, `v7_3_report.py`; tests: `tests/test_letter_v7_3.py`.
- Manifest/protocol/provenance: `data_manifest.json`, `PHASE_A_PROTOCOL.json`,
  `download.json`, `initial_tracked_sha256.json`, `verification.json`,
  `verification_final.json`, `final_integrity.json`.
- Training: `train/configuration.json`, `.npz`, `link_utilizations.csv`,
  `night_utilizations.csv`, `night_statistics.csv`, `summary.json`, 38 raw NPZ/JSON pairs.
- Pilot: `pilot/summary.json`, `component_timings.csv`, two raw NPZ/JSON pairs.
- Logs: `ingest.log`, `configure.log`, `train_execution.log`, `pilot.log`,
  `pytest_regression.log`, `verify.log`; failed/preflight logs giữ cùng thư mục.
- Không tạo plot/PDF, không tạo card, không có test outcomes hoặc GCP artifacts.

Claude có thể đọc training report để viết card; mọi thay đổi thiết kế đề xuất ở trên
vẫn chưa áp dụng. Phase A hoàn tất không tự mở Phase B.
'''
    with (out/'PHASE_A_REPORT.md').open('x') as f:
        f.write(text)
    print(out/'PHASE_A_REPORT.md')


if __name__=='__main__':
    report()
