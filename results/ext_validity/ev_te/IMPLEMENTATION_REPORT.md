# EV-TE — báo cáo triển khai và chạy theo brief

Người phụ trách: **Doan Van Tai**. Ngày thực thi: 15–16/11/2026. Nhánh `ext/validity`.

Đã hoàn tất code, tests, xác minh dữ liệu, Arm S training/prediction, Arm R train strict và timing pilot seed 777. Các vấn đề design bên dưới còn mở; đây không phải kết luận H1–H4 hoặc xác nhận Proposition 1 trên toàn grid.

## File và implementation

- `experiments/ext_validity/ev_te.py`: SNDlib parser, routing, scaling, active-link/OD reduction, exact sampled chain, exact constant-load queue step, deterministic mean twin, posterior, CRN decisions/evaluation, training, predictor, truth CLI, lock checker và scorer.
- `experiments/ext_validity/ev_te_trace.py`: strict TM parser, calendar split, observed-support reduction, minute-unit replay, train-only relaxation/OLS, descriptive run/summary CLI.
- `experiments/ext_validity/ev_te_pipeline.sh`: GCP pipeline đã viết, executable, `bash -n` PASS; chưa chạy. Một invocation truth, không retry; tự poweroff khi kết thúc. Scoring là bước riêng sau khi raw được lưu/commit bởi orchestrator.
- `tests/test_ev_te.py`: 17 tests mới; tổng cùng packet và D4c regression là 73 PASS.
- Không sửa file cũ, DESIGN.md, catalog, contract hoặc AGENTS.md. Không commit, ssh hay dùng mạng.

Kernel C++ nằm trong ev_te.py, build bằng g++ tại /tmp; không thêm dependency bằng network. Mean twin cộng đúng các bước fluid trên dt grid bằng geometric sums giữa các lần đổi dấu drift. Sparse optimization chỉ bỏ hệ số routing bằng 0, giữ thứ tự OD và RNG. Training đã chạy kernel dense trước tối ưu; `training_kernel_provenance.json` giữ toàn bộ source dense, flags và hashes. `sparse_kernel_audit.json`: 64 mô hình, 110.360 giá trị bitwise bằng nhau; final physics/regression tests chạy trên bản sparse.

## Commands thực tế và trạng thái

Mọi command Python đã source `.venv/bin/activate` và `experiments/explore_ctmc/env.sh`.

```bash
# fetch/design được gọi trong Python smoke heredoc: e.fetch(); e.design()
python3 -m experiments.ext_validity.ev_te train --workers 8
python3 -m experiments.ext_validity.ev_te predict
python3 -m experiments.ext_validity.ev_te_trace train
python3 -m experiments.ext_validity.ev_te run --workers 4 --timing-only --regimes A4_r90_b6_s0 A2_r90_b6_s1 G4_r90_b6_s0 G4_r90_b6_s1 --N 3 --K 128 --R-dec 128 --R-eval 256
python3 -m pytest -q tests/test_ev_te.py tests/test_ext_packet.py tests/test_ev_d4c.py --basetemp=/tmp/ev_te_pytest_sparse -o cache_dir=/tmp/ev_te_pytest_cache
bash -n experiments/ext_validity/ev_te_pipeline.sh
python3 -m experiments.ext_validity.ev_te verify-lock
```

Các bước compute exit 0; pytest **73 PASS, 0 FAIL, 12,73 s**. verify-lock exit **1 có chủ đích**, vì lock.json chưa được Claude tạo; log giữ lỗi FileNotFoundError. Unit tests xác nhận truth run dừng trước engine khi thiếu/invalid lock. Không gọi truth run, Arm R run, score hoặc Arm R summary.

Kiểm tra phát triển: smoke ban đầu phát hiện sai dấu half-step trong geometric cost sum; đã sửa trước fetch/design/train. Audit routing đầu tiên đánh dấu hai OD qua leaf link do so [path] với [path,None]; bản reference đã sửa cách biểu diễn không có second path. `routing_audit.json` giữ lần đầu, `routing_audit_final.json` xác nhận 594/594 OD khớp enumeration loopless độc lập; không đổi routing implementation.

## Dữ liệu và design

Dữ liệu đọc từ `/home/vantai/papers/data/sndlib`, ngoài Git; fetch chỉ hash và ghi manifest. Có **48,096 TM files**. `data_manifest.json` có URL, byte size/SHA256 của zip/tgz/hai topology và digest sorted basename<TAB>sha256<LF> cho toàn bộ TM. Đã hash lại toàn bộ dữ liệu sau compute: MATCH.

| Topology | Directed bottleneck e* | OD1 / OD2 / OD3 | alpha rho=.8 / .9 |
|---|---|---|---|
| abilene | ATLAng_IPLSng:IPLSng>ATLAng | CHINng_LOSAng / CHINng_HSTNng / CHINng_ATLAng | 0.00243259779129 / 0.0027366725152 |
| geant | at1.at_ch1.ch:ch1.ch>at1.at | ch1.ch_de1.de / ch1.ch_se1.se / ch1.ch_at1.at | 0.0128633287401 / 0.0144712448326 |

Set 4 = {OD1,OD2}. Design đủ 64 specs, 1–5 active links/regime. GÉANT pre-installed capacities bằng 0; đã dùng 10000 Mb/s mỗi directed link như brief và ghi limitation.

## Arm S: training và predictions

Seed A=1, N_train=2000, K=128, workers=8. **64/64 train JSON**, 61 retained, **732 prediction rows**. Tổng CPU training **13264.092035 CPU-s**.

Ba exclusions đều từ calibration P(total backlog>0)<.01:

| Regime | P(Q>0) | Lý do |
|---|---:|---|
| G1_r80_b3_s0 | 0.0092500 | P(total backlog > 0) < 0.01 |
| G2_r80_b3_s0 | 0.0097125 | P(total backlog > 0) < 0.01 |
| G3_r80_b3_s0 | 0.0098950 | P(total backlog > 0) < 0.01 |

T_int calibration: **0.292864879–96.633304280** fast-mode time units. dt: **0.007321621982–0.05**. T_int kiểm tra trên final grid: **0.310173793–92.512699781**.

| Topology, single OD | Switch < Stay | Switch > Stay | Median r_Stay (Mb) | Median r_Switch (Mb) |
|---|---:|---:|---:|---:|
| abilene | 24/24 | 0/24 | 409.514042 | 0.000000 |
| geant | 6/21 | 15/21 | 779.704315 | 1953.788857 |

Hai OD: số r_a<r_0 theo actions 1/2/3 là Abilene **8/8,8/8,8/8**, GÉANT **0/8,3/8,0/8**. Có ít nhất một Switch action thấp hơn Stay ở **41/61** retained regimes. Đây là dấu của point estimates training, không phải hypothesis verdict hoặc kiểm định ý nghĩa thống kê. CSV giữ đầy đủ r_a, batch-means SE và s-type cho từng regime; không chỉ báo kết quả thuận lợi.

`training_prediction_audit.json`: F counts đúng 2000 mỗi cell, normalized shares, fresh shares giống nhau qua tau, công thức predictor tính lại độc lập cho 732 rows có max residual **0**. S-type lưu sẵn có roundoff tối đa 6.445e-7 Mb so với hiệu các r_a; predictions dùng chính r_a và F.

## Timing và proposal

N_pilot=3 mỗi regime, seed 777 độc lập training/truth; K=128,R_dec=128,R_eval=256. Không ghi costs hoặc NPZ. Peak RSS quan sát **64.410 MiB/worker** ở pilot N=3; chưa đo peak cho N=500.

| Regime | CPU-s/instance | CPU pilot |
|---|---:|---:|
| A2_r90_b6_s1 | 4.033243 | 12.099729 |
| A4_r90_b6_s0 | 0.521739 | 1.565217 |
| G4_r90_b6_s0 | 3.526688 | 10.580064 |
| G4_r90_b6_s1 | 15.763741 | 47.291222 |

Proposal: **N=500, K=128, R_dec=128, R_eval=256, workers=32**, cho 61 regimes = 30.500 instances. Envelope lấy CPU/instance của pilot có proxy workload lớn nhất cho mỗi topology/slow group: **185473.254 CPU-s**. Dự phòng 2×: **370946.509 CPU-s < 800.000**; không cần hạ N của GÉANT theo dự toán này.

Quy đổi work/32 lý tưởng với 2× là 3.220 h; một regime lớn nhất là 4.379 h. Greedy-list schedule bound theo các giả định envelope là 7.462 h. Đây là planning estimate từ máy local; 2× không phải CI hoặc speed ratio GCP đã đo. Proposal chưa phải parameter lock và chưa cho phép truth run.

## Arm R strict training

Calendar split: train từ 2004-03-01T00:00:00 đến trước 2004-05-01T00:00:00; phần còn lại test. 48,096 files; **7,776 missing calendar bins**, **44,947 files bị parser strict đánh dấu thiếu OD**, **3,149 files đủ 132 OD**. Train valid 1,617/17,568; test valid 1,532/38,304.

| Regime | T_int train (min) | Managed ODs | Bottleneck |
|---|---:|---|---|
| R1_r80 | 115.268622586 | LOSAng_CHINng | ATLAng_IPLSng:ATLAng>IPLSng |
| R4_r80 | 115.268622586 | LOSAng_CHINng, WASHng_IPLSng | ATLAng_IPLSng:ATLAng>IPLSng |
| R1_r90 | 115.487009528 | LOSAng_CHINng | ATLAng_IPLSng:ATLAng>IPLSng |
| R4_r90 | 115.487009528 | LOSAng_CHINng, WASHng_IPLSng | ATLAng_IPLSng:ATLAng>IPLSng |

T_int dùng longest uninterrupted train segment **205 bins = 1025 min**, không nội suy qua gap. OLS fit riêng tau=1/2 từ 1125/1030 train windows. Rates Mb/s được nhân 60 để replay có queue Mb và cost Mb·min. Backlog reset sau gap, ghi limitation; nonpositive OD lag-1 correlation dùng Tr=5 min. Arm R chỉ train, **không có test costs**. Các T_int/managed ODs này thuộc strict subset, chưa đại diện toàn trace.

## Điểm chưa thể hiểu như một design đã khóa

1. **Vòng T_int/dt:** dùng calibration all-Stay seed A, dt=.05,T=20000,burn=500 để cố định T_int và chọn dt=min(.05,T_int/40). Run final-grid r_a dùng T=max(20000,2000*T_int), burn=50*T_int; T_int đo lại được lưu riêng, không đổi h/tau sau khi thấy kiểm tra. T_int_check/T_int nằm trong 0.596627–2.819650. Đây là cách giải vòng phụ thuộc được công khai; brief không quy định fixed-point hoặc hai-stage rule. Cần review trước lock.
2. **12 regimes có action mean utilization >1** (max **1.196823**): G4 rho=.8 ở cả beta/slow; G1 và G4 rho=.9 ở cả beta/slow. r_a của action đó chỉ là finite-duration average, không có finite stationary mean. Không tự thêm exclusion ngoài brief; predictions giữ cờ stationary_rate_valid=False/nonstationary_actions. Proposition 1 không được xác nhận cho các regimes này.
3. **Sparse TM semantics:** OD vắng mặt có thể mã hóa demand=0, nhưng archive không có tài liệu xác nhận. Chưa được phép impute; parser strict chỉ nhận đúng 132 entries. Cần xác minh ý nghĩa trước diễn giải Arm R; không nhận 44.947 files là dữ liệu hỏng đã được nguồn chính thức xác nhận.
4. **Pilot/lock:** brief yêu cầu timing trước khi Claude tạo lock nhưng cũng yêu cầu run gọi verify-lock. Chỉ seed 777 timing-only được miễn khi lock chưa tồn tại, không ghi costs; nếu lock tồn tại vẫn phải verify. Truth luôn verify trước đọc inputs/compile/engine và thiếu lock exit nonzero. Chưa tạo lock.json.
5. **Từ slope trong two-action test:** slope=s*DeltaF; level=h*s*DeltaF. Code lưu cả slope và level, test kiểm đúng đồng nhất thức level.

## Artifact và kết luận

- Source: bốn file mới liệt kê đầu báo cáo.
- Config/data provenance: `design.json`, `regimes.json`, `data_manifest.json`.
- Training: `train/` (64 JSON), `training_summary.csv`, `training_summary.json`, `design_excluded.json`, `predictions.csv`.
- Timing/budget: `pilot_selection.json`, `timing.json`, `budget_proposal.json`.
- Arm R: `arm_r/train.json` (giữ danh sách đầy đủ files thiếu OD).
- Logs: `train.log`, `predict.log`, `arm_r_train.log`, `timing.log`, `prediction_pilot_ops.log`, `tests_sparse_final.log`, `verify_lock_missing.log`.
- Checks: `training_prediction_audit.json`, `routing_audit_final.json`, `sparse_kernel_audit.json`, `training_kernel_provenance.json`, `pipeline_syntax.json`.
- Receipt hiện tại: `completion.json`, gồm source hashes và kiểm tra data/forbidden outputs.
- Không tạo chart. Không có raw truth, Arm R raw, score.json, score_cells.csv hoặc Arm R summary.

Đã xác nhận implementation checks, training/prediction consistency và pilot workload. Chưa kiểm H1–H4, chưa xác nhận external validity/realism/novelty, chưa chạy GCP. Orchestrator cần review các vấn đề design, chọn/khóa parameter card và lock trước mọi truth computation.
