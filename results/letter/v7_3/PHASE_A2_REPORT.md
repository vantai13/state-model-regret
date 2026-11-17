# V7-3 Phase A2 daytime training và pilot

Người phụ trách **Doan Van Tai**. Báo cáo và kiểm chứng được trí tuệ nhân tạo (AI) thực hiện theo brief. Chưa có human review hoặc author-self confirmation từ công việc này.

Brief A2 gốc với capacity provisioned đã hoàn tất training, pilot và independent replay. Scenario congested được tác giả chọn trong commit `HEAD` `b11427824215a55e57a3908a5f544c43e40be802` đang có một job training riêng. Báo cáo ghi checkpoint của job đó và chưa nhận toàn bộ scenario congested hoàn tất. Không commit, kết nối qua Secure Shell (SSH) hoặc tính test-day outcome trong lượt resume.

## Phạm vi và cấu hình

Tiếp tục `V7_3_phaseA2_resume_brief.md` và `V7_3_phaseA2_brief.md` tại `HEAD`. Giữ 26 train weekdays thuộc split Phase A, từ 2005-05-05 đến 2005-06-14. Có 50 later test weekdays được đếm từ metadata. Không mở demand intensity hoặc outcome của test days. Exclusion rule Phase A được giữ nguyên, kể cả yêu cầu đủ warmup của ngày trước. Cache chỉ chứa training data.

Window được chọn là **10:15 đến 16:15**, tối đa mean total demand trên 73 starts trong ngày với bước 15 phút. Tổng demand trung bình **61547.144945 Mbit/s**. Clock theo dữ liệu nguồn, timezone và daylight saving time (DST) chưa được xác nhận. Warmup Stay bắt đầu 08:15, trước decision hai giờ.

Uniform capacity **23128.606845556 Mbit/s**, trùng Phase A. Quy tắc dùng peak 15 phút trong train daytime 06:00 đến 21:45 chia 0,9. Busiest Stay link trong window là `at1.at_de1.de:at1.at>de1.de`. Top ba cặp origin-destination (OD) được chọn theo mean volume, giữ cả OD có second-shortest path vẫn qua link đó.

`DAY1` quản lý `hu1.hu_de1.de`, volume trung bình 2699.851812 Mbit/s. Stay `hu1.hu → at1.at → de1.de`. Switch `hu1.hu → sk1.sk → cz1.cz → de1.de`. Tránh busiest Stay link.

`DAY2` quản lý `si1.si_de1.de`, volume trung bình 2036.525657 Mbit/s. Stay `si1.si → at1.at → de1.de`. Switch `si1.si → at1.at → ch1.ch → fr1.fr → de1.de`. Tránh busiest Stay link.

`DAY3` quản lý `hr1.hr_de1.de`, volume trung bình 1785.308271 Mbit/s. Stay `hr1.hr → hu1.hu → at1.at → de1.de`. Switch `hr1.hr → si1.si → at1.at → de1.de`. Vẫn đi qua busiest Stay link.

Truth giữ real 15-minute traffic matrices nhân two-state OD modulation độc lập, β=0,3 và flip rate 1/s. Truth dt=0,05 s. M0 dùng train-average weekday profile. Hybrid cộng h·ŝ vào gap Switch trừ Stay. Stationary chọn Switch khi ŝ âm. c=0 và exact ties chọn Stay. Stale telemetry có tuổi 5 hoặc 15 phút, posterior K=64 dưới Stay. Các horizons 1, 2, 4 và 6 giờ lấy từ cùng rollout.

## Utilization của provisioned

Mean là max theo link sau khi lấy trung bình trên ngày và slot. Peak là max 15-minute mean trong window. Upper nhân peak với 1,3, chặn mọi fast-mode realization.

| Regime | Mean Stay | Mean Switch | Peak Stay | Peak Switch | Upper Stay | Upper Switch |
|---|---:|---:|---:|---:|---:|---:|
| `DAY1` | 48.814322% | 37.141108% | 66.994777% | 60.337282% | 87.093210% | 78.438466% |
| `DAY2` | 48.814322% | 40.009098% | 66.994777% | 60.337282% | 87.093210% | 78.438466% |
| `DAY3` | 48.814322% | 48.814322% | 66.994777% | 66.994777% | 87.093210% | 87.093210% |

Warmup Stay có upper utilization **0.726370566**. Forecast của cả ba regimes có upper **0.647399912**. Các envelope đều dưới capacity, nên từ empty initial queues, mọi queue trong training window luôn bằng 0 dưới cả hai actions. Đây là chứng chỉ theo offered-load envelope và được raw outputs xác nhận.

## Training outputs

Đủ **78/78 regime-day records**, N=200 mỗi regime-day, tức 5.200 instances mỗi regime. Training seed **7302001** và pilot seed **7372001**, tách biệt. K=64 cho mỗi stale age. Thời gian tính toán trên central processing unit (CPU) từ artifacts có sẵn **57.143766 CPU-s**. Training đã hoàn tất trước lượt resume, các raw records được dùng lại và kiểm toán, không chạy lại.

| Regime | Mean backlog rate Stay / Switch (Mbit) | ŝ (Mbit) | Conditional Monte Carlo (MC) standard error (SE) (Mbit) | Positive / zero / negative days | Directional sign stability |
|---|---:|---:|---:|---|---|
| `DAY1` | 0 / 0 | 0 | 0 | 0 / 26 / 0 | Không xác định |
| `DAY2` | 0 / 0 | 0 | 0 | 0 / 26 / 0 | Không xác định |
| `DAY3` | 0 / 0 | 0 | 0 | 0 / 26 / 0 | Không xác định |

Exact-zero share là 26/26 cho mỗi regime. M0 exact tie share **100%**, fresh và cả hai stale ages, ở cả bốn horizons. Mẫu số cho mỗi regime, horizon và side là 5.200 decisions. K posterior samples không được đếm thành independent decisions. Hybrid và Stationary cũng chọn Stay trong pilot. Không có bằng chứng superiority của một pipeline từ các zero costs này.

T_int dùng first-zero integrated autocovariance estimator của letter trên instance 0 từng ngày và action, không nối ngày. **156/156 traces** ở dt=0,05 s có zero variance. Check bổ sung dùng rollout đầu tiên của mỗi regime trên train day sớm nhất ở dt=0,005 s, rồi subsample 0,01 và 0,05 s. Cả 18 action/grid checks vẫn zero variance. Do đó **T_int và 6h/T_int không xác định**, không báo T_int bằng dt, bằng 0 hoặc ratio vô hạn. Check này không tạo một correlation scale khi backlog hằng 0.

Trong window, ordinary least squares (OLS) total-demand slope theo slot midpoint có min/q25/median/q75/max **-1748.426800, -81.113270, 118.636367, 468.518352, 866.000102 Mbit/s mỗi giờ**. Coefficient of variation có min/median/max **0.013347, 0.026054, 0.089164**. Có nonstationarity trên input, dù queue vẫn bằng 0. Các rate và T_int chỉ mô tả finite training windows.

## Pilot và compute projection

Lượt resume đã chạy hai train days **2005-05-05** và **2005-05-09**, ngày sớm nhất và ngày có tổng window demand cao nhất. Ba regimes tạo sáu end-to-end pilot records. N=2, giữ full K=64, R_dec=64, R_eval=128. Reference decision và evaluation dùng seed streams khác nhau, evaluation common random numbers (CRN) ghép hai actions. **C_ref=0 Mbit·s** cho cả bốn horizons ở mọi pilot record. M0, Hybrid và Stationary có regret=0 và G_S=0 Mbit·s. Các tỷ lệ chia C_ref không xác định.

Projection cho 50 test weekdays × 3 regimes × N=200, 20 workers trên n2-standard-32, nhân N với 200/2. K và R đã dùng full size trong pilot.

| Component | Projected CPU-s |
|---|---:|
| M0_fresh | 2.814955 |
| M0_stale_300 | 2.477657 |
| M0_stale_900 | 2.230542 |
| choices_fresh | 1.897107 |
| choices_stale_300 | 1.422230 |
| choices_stale_900 | 1.366698 |
| metrics_gather | 52.463953 |
| paired_evaluation | 250.877400 |
| posterior_300 | 155.324518 |
| posterior_900 | 111.627268 |
| reference_decision | 231.550020 |
| warmup | 111.232495 |
| write_raw_npz | 128.551755 |

Mean-day projection **1053.836598 CPU-s = 0.292732 CPU-hours**, ideal 20-worker wall **52.691830 s**. Chọn ngày chậm hơn riêng từng component và regime cho **1583.058075 CPU-s**, ideal wall **79.152904 s**. Đây là projection từ local pilot, không đo tốc độ n2-standard-32. Các exact-empty-queue shortcuts làm workload này rất nhỏ. Không áp projection này cho congested. Pilot timing có overhead và CPU threads của NumPy, còn verification/tests được chạy với OPENBLAS_NUM_THREADS=1. Hai phép ngoại suy không có confidence interval (CI) hoặc upper-bound guarantee cho test workload.

## Night scope observation giữ riêng

Phase A night artifacts giữ nguyên byte. Train mean backlog rate Stay **0 Mbit**, Switch **0.287965650082 Mbit**, ŝ **0.287965650082 Mbit**. M0 ties 100%, C_ref=0 trên hai train-night pilots. Night và provisioned daytime là scope observations của objective chỉ tính backlog với c=0. Không gộp zero regret thành bằng chứng về hiệu quả trên test.

## Congested scenario đang chạy riêng

Theo `notes/ops/codex/V7_3_congested_decision.md`, giữ window, flows, paths và data, đặt capacity **12544.525173885 Mbit/s** để busiest Stay link có window-mean ρ=0,9.

| Regime | Mean Stay | Mean Switch | Peak Stay | Peak Switch |
|---|---:|---:|---:|---:|
| `DAY1` | 0.900000 | 0.684778 | 1.235197 | 1.112451 |
| `DAY2` | 0.900000 | 0.737656 | 1.235197 | 1.112451 |
| `DAY3` | 0.900000 | 0.900000 | 1.235197 | 1.235197 |

Checkpoint lúc **2026-11-17T17:03:09.276096+00:00** có **15/78** complete raw JavaScript Object Notation (JSON)/NumPy zipped archive (NPZ) pairs. Full summary hiện có `False`, pilot summary hiện có `False`. Số rows đã tăng trong lúc resume, nên không launch một training job trùng. Chưa báo ŝ pooled, sign stability, full T_int, C_ref hoặc compute projection cho congested từ subset đang chạy.

Hai metadata fields trong congested configuration được kế thừa từ provisioned và còn giá trị cũ. `capacity_identical_to_phase_A` lưu true nhưng phép so capacity hiện tại cho false. `capacity_peak_utilization` lưu 0,9 nhưng daytime peak-driver load chia capacity mới là **1.659349068**. Các trường utilization mới trong `regimes` đã dùng capacity congested. Ghi correction ở `day_train/report_numbers.json`, giữ configuration và running source nguyên byte.

## Kiểm chứng, file và command

Bộ kiểm tra đạt **54 passed, 18 deselected in 0.30s**. Gồm Phase A/A2/congested controls, ba E4 regression controls, và sáu nonzero/corruption controls cho independent replay. Test corruption kiểm reference khác evaluation, tie chọn Stay, signed G_S và khả năng empirical regret âm. Không chạy full repo suite ngoài scope.

Independent saved-artifact replay `PASS`, không gọi simulator. Kiểm 73 windows, 432 link rows, 156 day-utilization rows, 78 training records, sáu pilot records, raw rates/SE/signs/ties/autocovariance, C_ref/reference/CRN/regret/G_S và projection. **1038 protected file hashes khớp**, gồm night artifacts và V7-1 đã scored. `git diff --exit-code` `PASS` trước báo cáo. `HEAD` không đổi trong lượt resume.

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
