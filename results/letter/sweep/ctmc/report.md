# S1-A CTMC — báo cáo sample/pilot và bàn giao

Người phụ trách: **Doan Van Tai**. Phạm vi: **EXPLORATORY**, theo `BRIEF_S1A_CTMC.md`; không thẻ xác nhận.

## Đã thực hiện

- Tạo `experiments/letter/sweep_ctmc.py`, `tests/test_sweep_ctmc.py`, `experiments/letter/sweep_ctmc_gcp.sh`. Các output mới chỉ ở `results/letter/sweep/ctmc/`.
- Các lệnh `sample`, `pilot`, `run --workers W --shard i/n`, `summarize`. Tái dùng X-CTMC Chain, generator, QBD truncation, fluid gap, posterior, policy sum, strict tie về Stay. Không sửa/bypass guard.
- Tám luật: M0, Stationary_true/hat, Hybrid_true/hat, min-MLU, TH_0.8, oracle C_ref. Oracle dùng trạng thái hiện tại làm reference trên cả hai phía; không phải stale-information Bayes oracle.
- Ghi L/regret fresh–stale, G_S, C_ref, share/tie, hybrid–static disagreement từng phía, D_fresh/D_stale, quantile |fluid gap|, các đặc trưng mô hình và target benefit cho S2.
- Estimator giữ W2 arrival-count moments/FFT covariance, W=300 T_int; revalidate theo mu từng đường. MMPP invalid hoặc quá cap solver → dùng M/M/1 từ cùng bản ghi cho cả hai path. M/M/1 cũng invalid → giữ INVALID_ESTIMATOR, không clip/không thay bằng s đúng. Counts dùng RAM, giữ seed/digest, không ghi tạm vào output cũ.

## Lựa chọn trước outcomes

- 1.024 scrambled Sobol 9D, seed 8100001, không lấy bù ứng viên bị loại. mu mỗi path log[5,20]; rho nền [0.3,0.92]; alpha/load [0,0.9]; kappa log[0.02,5] giây; u=[0.05,0.95]×min(0.97mu−load); c=0. High-mode overload được phép, hai action mean-stable.
- Truncation tail ≤1e-13 cho cả hai action; N≤4096, state pair≤16.000.000, complete telemetry bins≤10.000.000/path; cap dự phóng và runtime 3.600 CPU-s/regime.
- Full-grid handoff: h/T_int={0.1,0.2,0.3,0.5,0.7,1,1.5,2,3,5,7,10,20,30}; tau/T_int={0.3,1,3}.
- Pilot chọn đúng 5 regime có initial cost proxy lớn nhất + 5 random không trùng; seed chọn 8100002. Timing subset h/T_int={0.1,1}, tau/T_int={0.3}, được chọn sau parameter-only screen và trước truth. Bản ghi vẫn đủ 300 T_int. Full grid không đổi.
- Seed record pilot=8100003, run tương lai=8100004; tách theo id và path, độc lập workers/shards.

## Số đếm thực đo

- Candidates: 1024; model stable/nonnegative: 1024; stationary chains kiểm được: 1013. 11 candidates chưa dựng chain vì cap truncation/state, không phải bằng chứng mô hình bất ổn.
- Final eligible: 1000. Loại 24: 11 truncation/state cap + 12 telemetry cap + 1 initial projected CPU cap. Không loại theo regret/benefit; không thay mẫu.
- Sample v2: 10.011806 CPU-s, 10.015432 giây wall.
- Pilot v2: 10/10 COMPLETED, 84.052309 CPU-s tổng, 43.601675 giây wall với 2 worker. 160 policy rows, 80 feature/benefit rows, không policy row invalid.
- Estimator: 7 MMPP/M/1, 3 M/M/1 fallback. Fallback có lý do riêng trong raw; không suy từ dấu hiệu ứng.

| Regime | Chọn | CPU-s v2 | Estimator |
|---|---|---:|---|
| S1A_0021 | heaviest_proxy | 16.207414 | MMPP/M/1 |
| S1A_0082 | random | 0.219988 | M/M/1 |
| S1A_0099 | random | 1.955919 | M/M/1 |
| S1A_0343 | heaviest_proxy | 12.039757 | MMPP/M/1 |
| S1A_0378 | heaviest_proxy | 10.893791 | MMPP/M/1 |
| S1A_0533 | random | 0.295986 | M/M/1 |
| S1A_0642 | heaviest_proxy | 18.047212 | MMPP/M/1 |
| S1A_0815 | random | 1.043945 | MMPP/M/1 |
| S1A_0840 | random | 2.202624 | MMPP/M/1 |
| S1A_0855 | heaviest_proxy | 21.145673 | MMPP/M/1 |

## Dự phóng chi phí, giữ nguyên lịch sử

Mô hình đầu dùng max(time/work) của pilot. Fixed overhead của regime nhỏ làm hệ số posterior lớn khoảng 100 lần hệ số của regime nặng. Vì vậy ước lượng 159.553918 CPU-giờ/707 eligible ở bản đầu quá bảo thủ và loại sai về resource proxy. Đây là lỗi dự phóng, không phải FAIL của hypothesis. `cost_diagnostic.json` giữ phân tích chỉ từ timing/work.
Pilot đầu: 78.809903 CPU-s, 41.216201 giây wall. Bản cũ và source snapshot giữ nguyên trong thư mục cha. Cả hai pilot tổng cộng 162.862212 CPU-s; cùng 10 regime/timing grid/seed, không thêm coordinates.
Bản v2 dùng slope NNLS không âm theo từng component; intercept nâng tới mức bao mọi timing pilot; overhead scale theo số horizon/age; safety factor 1.5. Chỉ timing/work đi vào fit. Parameter candidates giống byte; mọi scientific field (rows, features, estimator, truncation, T_int) của hai pilot giống nhau trên 10/10 regime.
- Final toàn 1.000 regime: **28.167613 CPU-giờ**; **1.877841 giờ trên 15 worker** lý tưởng; **2.086490 giờ ở hiệu suất 90%**.

| Shard | Regimes | CPU-giờ | Wall 15 worker (giờ) | Wall ở 90% (giờ) |
|---|---:|---:|---:|---:|
| 0/2 | 499 | 13.292463 | 0.886164 | 0.984627 |
| 1/2 | 501 | 14.875150 | 0.991677 | 1.101863 |

Hai shard đồng thời cần 30 worker và dự phóng hoàn tất theo shard chậm hơn: khoảng 0.992 giờ lý tưởng, 1.102 giờ ở 90%. CPU/wall là extrapolation từ timing subset trên laptop, chưa đo GCP; không phải guarantee/CI. Không tự mở rộng cấp máy hoặc chạy full.

## Metric khoa học của pilot, chỉ mô tả

Regret trung bình, đơn vị % C_ref; benefit là điểm phần trăm C_ref, dấu dương có lợi cho hybrid. 10 regime gồm 5 nặng + 5 random nên không đại diện quần thể; không population CI. tau/T_int=0.3 trong mọi hàng dưới đây.

| h/T_int | Phía | Rate | Static regret (% C_ref) | Hybrid regret (% C_ref) | Benefit (pp) | Share bất đồng |
|---:|---|---|---:|---:|---:|---:|
| 0.1 | fresh | hat | 0.132606677 | 0.132606677 | 0.000000000 | 0.000000000 |
| 0.1 | fresh | true | 0.132606677 | 0.117495215 | 0.015111462 | 0.006309075 |
| 0.1 | stale | hat | 0.132606677 | 0.132606677 | 0.000000000 | 0.000000000 |
| 0.1 | stale | true | 0.132606677 | 0.132606677 | 0.000000000 | 0.000000000 |
| 1 | fresh | hat | 0.148249585 | 0.064328232 | 0.083921353 | 0.006024935 |
| 1 | fresh | true | 0.148249585 | 0.059347133 | 0.088902452 | 0.007863749 |
| 1 | stale | hat | 0.148249585 | 0.138838394 | 0.009411191 | 0.000792675 |
| 1 | stale | true | 0.148249585 | 0.138633295 | 0.009616290 | 0.001037926 |

Không dùng pilot để kết luận đã tìm được vùng lợi ích, đạt cổng S2 hoặc xác nhận hypothesis. Không chạy full-grid, S2/S3 hay thay các claim cũ.

## Command thực chạy và kiểm chứng

Các command Python có `PYTHONDONTWRITEBYTECODE=1`, env đã source; pytest tắt cacheprovider và đặt basetemp mới dưới output được phép.

```bash
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
export PYTHONDONTWRITEBYTECODE=1
python3 -B -m pytest -q -p no:cacheprovider --basetemp results/letter/sweep/ctmc/pytest_final tests/test_sweep_ctmc.py tests/test_x_ctmc.py tests/test_pl_posterior.py -k "not finite_record_estimator_reduces_to_literal_W2_mu10"
python3 -B -u -m experiments.letter.sweep_ctmc sample --out results/letter/sweep/ctmc/v2
python3 -B -u -m experiments.letter.sweep_ctmc pilot --out results/letter/sweep/ctmc/v2 --workers 2
python3 -B -u -m experiments.letter.sweep_ctmc summarize --out results/letter/sweep/ctmc/v2 --source pilot
bash -n experiments/letter/sweep_ctmc_gcp.sh
python3 -B results/letter/sweep/ctmc/rescore_audit.py
```

- Final pytest: **92 passed, 1 deselected, 1 xfailed in 27.51s**; 43 test mới. Không claim đã chạy toàn repo suite.
- Bỏ chọn đúng test cũ tạo temporary counts dưới `results/letter/x_ctmc/`, ngoài phạm vi ghi brief. Test mới đối chiếu literal W2 bằng tmp trong output được phép vẫn PASS.
- Xfail cũ: sanity theta≥1 không bao giờ Switch mâu thuẫn với rule literal khi MMPP high-mode overload được phép; không sửa định nghĩa. S1-A dùng theta=0.8.
- XCTMC_001/002: 24+16=40 completed common-policy rows ở h/T_int=1,3 và tau/T_int=1,3 khớp raw đã lưu; maximum absolute error **0** cho C_ref, L, regret, G_S, share. Các hat rows invalid của XCTMC_002 giữ nguyên.
- Các test khác: Sobol tái lập/prefix/điều kiện ổn định; cắt shard disjoint và exhaustive; heavy/random selection; stale cost bằng dense old–current Markov coupling; D hai vế và quantiles; MMPP invalid→MM1, MM1 invalid giữ missing; source guard trước engine; failure record + no overwrite; affine timing envelope.
- Bash syntax PASS; invalid SHARD trả exit 2 trước engine. Không launch script bằng SHARD hợp lệ ở local.
- Independent rescore dùng standard library, không import scorer: **2339 checks PASS** (L/regret/G_S/oracle, D, benefit/disagreement, summary distribution, chi phí/shard, raw hashes).
- Kiểm hash 598 file có sẵn: 0 đổi. Ba source mới vẫn untracked. Không dùng commit/SSH trong nhiệm vụ này.
- Inline audit đầu dừng tại giả định HEAD bất biến: công việc song song đã tạo commit 631ae0878/49e9a9524. Final audit ghi hai HEAD và kiểm hash đầu vào trực tiếp; không biến đổi Git để khôi phục HEAD. Pytest tạo symlink *_current; audit loại alias này khỏi đếm hai reference records.

## Bàn giao và nơi lưu

**Bản dùng để chạy tiếp: `results/letter/sweep/ctmc/v2/`. Thư mục cha giữ calibration đầu, không dùng làm full-run input.**

- `v2/sample_config.json`, `v2/candidates.json`, `v2/sample.json`, `v2/sample.csv`: cấu hình và toàn bộ 1.024 candidates, kể cả các loại resource.
- `v2/pilot_plan.json`, `v2/pilot.json`, `v2/pilot/*.json`, `v2/projection.csv`: selection trước outcomes, raw, timing, ŝ fit và dự phóng.
- `v2/pilot_summary/by_h.csv`, `by_h_and_age.csv`, `features_benefit.csv`, `policies.csv`, `summary.json`: bảng regret/distribution/disagreement/S2 features. Outcome target columns được ghi rõ để tránh target leakage.
- `sample_v2.log`, `pilot_v2.log`, `summarize_v2.log`, `pytest_final.log`, `rescore_audit.log`: log thực chạy.
- `verification.json`, `provenance.json`, `initial_existing_inputs.json`, `cost_diagnostic.json`, `pilot_source.py`, `rescore_audit.py`: evidence/hashes/audit và lịch sử sửa cost-only.
- Không tạo plot, không output full-run, không paper edit.

Các lệnh sau chỉ bàn giao cho Claude trên GCP, **chưa thực thi**:

```bash
bash experiments/letter/sweep_ctmc_gcp.sh 0
bash experiments/letter/sweep_ctmc_gcp.sh 1
# Sau khi hai shard có receipt:
python3 -B -m experiments.letter.sweep_ctmc summarize --out results/letter/sweep/ctmc/v2 --source run
```

Script chạy `run --workers 15 --shard 0/2` hoặc `1/2` trên v2, kiểm source/dependency/pilot/raw hashes trước engine; ghi PIPELINE_START/EXIT và từ chối ghi đè. Không SSH, không poweroff. Runtime failures giữ raw/receipt và trả lỗi; không tự retry.

## Giới hạn còn mở

Full-grid khoa học và timing thật GCP chưa xác nhận. CTMC truth là numerical trên truncated state space có tail certificate, không symbolic exact. Finite record 300 T_int có thể invalid; các ô/horizon/tuổi dùng chung regime nên phụ thuộc nhau. S1 exploratory không xác nhận một vùng để claim trong paper. Bước tiếp đúng brief là Claude review dự phóng rồi chạy hai shard; không tự chọn vùng, thay threshold hay chạy xác nhận S3.
