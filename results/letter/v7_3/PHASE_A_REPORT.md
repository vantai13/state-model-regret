# V7-3 Phase A — GÉANT night consolidation

Người phụ trách: **Doan Van Tai**. Code, phép tính và báo cáo do AI thực hiện theo brief;
không phải author-self work hoặc independent human review.

**Hoàn tất Phase A: dữ liệu, code, training và pilot. Chưa có test-night outcome,
chưa có test card và không kết luận hiệu quả trên test. Không commit.**
Brief tại HEAD khi bắt đầu `fc3ee0a1096b76a271e78a5011f79916acf8e746`.

## Dữ liệu và split (chỉ metadata/completeness trên test)

- [Official SNDlib dynamic-matrices index](https://sndlib.put.poznan.pl/dynamicmatrices.overview.action) xác nhận đúng archive;
  HTML đã lưu ở `sndlib_dynamic.html`. Download URL: https://sndlib.put.poznan.pl/download/directed-geant-uhlig-15min-over-4months-ALL-native.tgz.
- Archive 39,570,674 bytes; SHA256 `92d72a808d6de9d26be66844c098d3f32d5b9bb6c69af170e82b73118faef0df`.
  Native format 1.0, đơn vị Mbit/s; HTTP Last-Modified
  `Wed, 22 Nov 2023 13:22:15 GMT`. Đây là HTTP version metadata,
  không tự suy một semantic release number. Topology SHA256
  `ff316c23220ff4485deafcb8701d49c353db0c80072152df3ed9023ed4b4f4ff`.
- 11,460 TM files, 10,773 hợp lệ;
  687 file có DEMANDS rỗng được loại theo parser viết trước ingestion.
  OD vắng trong sparse TM được hiểu là demand 0; không đồng nghĩa cả TM bị mất.
- Khoảng timestamp: 2005-05-04T15:00:00 → 2005-08-31T23:45:00.
  Clock giữ nguyên từ nguồn; timezone/DST chưa xác nhận.
- Train window là 42 ngày lịch đầu: 04/05–14/06/2005; cutoff **15/06/2005**,
  áp trước completeness filtering. Giữ **38 train nights**
  (2005-05-05 → 2005-06-14) và **69 test nights**
  (2005-06-15 → 2005-08-30); loại 13 ngày/đêm.
  Danh sách ngày và slot thiếu/hỏng nằm đầy đủ trong `data_manifest.json`.
- Ngày hợp lệ phải đủ 96 TM quarter-hour và đủ 8 TM warmup 22:00–23:45 hôm trước.
  Không lọc theo mức tải, cost hay model output. Parser zero-fill OD vắng trong
  universe 462 directed ODs, kiểm node/OD/unit/negative/nonfinite/duplicate/time.
  Quy tắc và clarification schema trước ingestion: `PHASE_A_PROTOCOL.json`.
- Raw archive và cache **train-only** ở `/home/vantai/papers/data/sndlib`; cache
  `v7_3_train.npz` không chứa test dates. Test TM chỉ đọc để parse/hash/validity;
  không tính link load, forecast truth, state, decision hoặc cost của test nights.

## Scenario triển khai, không đổi thiết kế trong brief

GÉANT: 22 nodes, 36 undirected physical links = 72 directed queues. Stay dùng
min-hop/lexicographic complete node-sequence tie rule của EV-TE. Capacity uniform
**23128.606845556 Mbit/s** = busiest Stay train-daytime 15-min mean / 0.9;
daytime convention là 06:00–21:45. Peak utilization kiểm lại =
**0.900000000000000**.

Thứ tự xét link cố định theo initial train-mean 00:00–06:00 bidirectional load,
tie theo link ID. Tắt cả hai directions, skip bridge; dừng trước lần connected
removal đầu tiên vượt train-mean utilization 0.8. Chỉ OD có đường hiện tại đi qua
link bị bỏ mới reroute. Đã tắt **15/36 physical links**,
giữ 21 links, connected (một tree); không gặp stop vì utilization.

- `be1.be_lu1.lu`
- `hr1.hr_si1.si`
- `ie1.ie_uk1.uk`
- `il1.il_nl1.nl`
- `hu1.hu_sk1.sk`
- `pl1.pl_se1.se`
- `es1.es_it1.it`
- `be1.be_nl1.nl`
- `gr1.gr_it1.it`
- `es1.es_pt1.pt`
- `ch1.ch_it1.it`
- `nl1.nl_uk1.uk`
- `ch1.ch_fr1.fr`
- `at1.at_ny1.ny`
- `de1.de_fr1.fr`

| Configuration | Busiest link, train-mean night utilization | Maximum individual 15-min train-night utilization |
|---|---:|---:|
| Stay | 36.423786% | 53.673074% |
| Switch | 40.474065% | 91.419848% |

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
| Mean 00:00–06:00 backlog cost rate (Mbit) | 0 | 0.287965650082 |
| Defined network-backlog T_int nights, trace instance 0 | 0/38 | 3/38 |

**ŝ = Switch−Stay = +0.287965650082 Mbit**. Conditional Monte Carlo SE
**0.00218500749348 Mbit**, chỉ cho synthetic randomness trên
38 fixed train TMs; không phải uncertainty về population nights hay test.
Across-night median ŝ=0. Sign counts: **4 positive / 34 exact zero / 0 negative**.
Strict same-sign fraction so với pooled positive sign = **4/38 = 10.526316%**;
không gộp zero vào positive để nhận sign stability cao.

| Train date có ŝ>0 | ŝ (Mbit) |
|---|---:|
| 2005-05-05 | 0.042469197893 |
| 2005-05-06 | 1.47898877087e-05 |
| 2005-05-10 | 10.9002098434 |
| 2005-05-18 | 8.71891849548e-07 |

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
| 2005-05-05 | 0.299708558 | 72070.014 |
| 2005-05-06 | 0.063237596 | 341568.964 |
| 2005-05-10 | 100.310529870 | 215.331 |

Stay **38/38 undefined**, Switch **35/38 undefined** do zero-variance first-instance trace.
Có 4 nights ŝ>0 nhưng chỉ 3 first-instance traces có event: một trace không đại diện
toàn bộ 200 trajectories. T_int≈0.063s chỉ ≈1.26 grid steps, chưa resolved như
continuous-time correlation scale; mọi h/T_int trên chỉ mô tả grid và trace này.
Không có CI/population claim. Backlog occupancy/max và lỗi estimator được giữ ở raw JSON.

Nonstationarity: OLS total-demand slope theo 24 slot midpoints 00:00–06:00,
đơn vị Mbit/s per hour; min/q25/median/q75/max =
**-2060.009897, -1648.412792, -1563.384772, -1418.080787, -789.236682**.
38/38 slopes âm. `train/night_statistics.csv` ghi từng đêm.
Measured training component CPU = **213.422449 CPU-s**;
không tính toàn bộ ingestion/compression/checksum/FFT/report overhead vào số component này.

### Vì sao outcome suy biến trên train/pilot

Train-only pathwise upper bounds: Stay warmup utilization max
**0.733287736**, Stay night max
**0.697749964**, cả hai M0 forecast configs max
**0.619849883**, đều <1 kể cả +30% modulation.
Do đó warm/fresh/posterior Stay queue là zero; mean forecasts cả hai configs không
phát sinh queue từ đó. M0 cost tie là hệ quả của envelope, không phải numerical underflow.
Stay actual cost 0 trên train; occasional Switch bursts làm ŝ≥0.
Không tự đổi capacity, beta, objective, threshold hoặc tie rule để tạo effect.

## Pilot và compute projection (hai đêm train)

Pilot dùng **2005-05-05, 2005-05-07**, lần lượt earliest eligible weekday/weekend,
chọn trước trong protocol. N=2, K=4, R_dec=4, R_eval=8, h và tau giữ nguyên.
Mỗi đêm chạy end-to-end: warm → fresh/stale twins → fresh true-model reference decision
→ independent paired evaluation → regret và G_S. C_ref=0 ở cả bốn horizons;
mọi pipeline/side/age regret=0 Mbit·s và G_S=0 Mbit·s, absolute.
Regret/C_ref và G_S/C_ref **undefined**, không đổi mẫu số hoặc ghi 0%.

| Component | 2005-05-05 CPU-s | 2005-05-07 CPU-s | Projected full-test CPU-s |
|---|---:|---:|---:|
| M0_fresh | 0.000769443 | 0.000314358 | 3.739113 |
| M0_stale_300 | 0.000534453 | 0.000329687 | 47.700528 |
| M0_stale_900 | 0.000295832 | 0.000270885 | 31.282778 |
| choices_fresh | 0.000447711 | 0.000141529 | 2.032878 |
| choices_stale_300 | 0.000231771 | 0.000143182 | 1.293588 |
| choices_stale_900 | 0.000126180 | 0.000116932 | 0.838736 |
| metrics_gather | 0.000470518 | 0.000186956 | 36.292565 |
| paired_evaluation | 5.122331854 | 0.000941480 | 282804.688037 |
| posterior_300 | 0.003600738 | 0.000844927 | 245.400708 |
| posterior_900 | 0.000893830 | 0.000712875 | 88.690116 |
| reference_decision | 2.474568012 | 0.000868782 | 136644.111029 |
| warmup | 0.002205013 | 0.000912625 | 10.755851 |
| write_raw_npz | 0.004442499 | 0.002830777 | 401.484835 |

Full plan (chưa chạy): 69 test nights × N=200 = 13.800 instances,
K=64 mỗi age, R_dec=64, R_eval=128. Future paths dùng CRN cho hai configs và chung
bốn horizons: 2.649.600 six-hour paired future paths, không nhân thêm 4 cho horizons.
Projected từ mean hai pilot nights và linear sample-count scaling:
**420318.310763 CPU-s = 116.755086 CPU-hours**.
Với **20 independent workers trên n2-standard-32**, ideal wall
**5.837754 giờ** nếu tốc độ mỗi core giống máy đo.

Máy thực đo: AMD Ryzen 5 7535HS with Radeon Graphics, WSL2, Python 3.14.5,
OPENBLAS_NUM_THREADS=1. Không có measurement trên n2; không SSH/bật VM trong phase này.
Hai pilot có workload rất khác nhau (weekday có potential overload, weekend có chứng chỉ zero).
Stress proxy dùng đêm train tốn CPU nhất 2005-05-10:
N=200 rollout **87.071011 CPU-s**; thay future components
bằng 192 lần cost này mỗi night → **1154386.259238 CPU-s**,
ideal 20-worker wall **16.033142 giờ**.
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
  296 counted consistency checks
  và 36,334 tracked file hashes;
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
