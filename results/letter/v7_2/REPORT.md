# V7-2 — compatibility audit EV-D4b/c → letter

Người phụ trách: **Doan Van Tai**. Ngày brief: 17/11/2026.
Input brief tại HEAD `fc3ee0a1096b76a271e78a5011f79916acf8e746`, SHA256
`714f7826584098477e28a954cc12c8bff71b6770b182e535f2efe749a2f9fe0a`.
Trạng thái: audit hoàn tất, **design draft**, **0 test outcomes mới**.

## Kết luận phân loại

**B — cần run mới và adapter, không cần simulator hàng đợi mới.** FIFO DES,
fluid cost, residence-time integral và CRN dùng lại được. Cần bổ sung chronological
split/no-wrap, posterior mean-before-decision, conditional stochastic reference và
raw per-instance. **Không chọn A:** các output cũ thiếu các thành phần này và
hold chưa tới 2/4 h. **Không chọn C:** kernel queue đã hỗ trợ arrivals và arbitrary
finite horizon; thiếu input/adapter không phải lý do viết simulator mới.

Có chặn dữ liệu: record được xác minh chỉ **4 h 0,07 s**. Train first hour,
max-age 300 s → hold 4 h cần ít nhất **5 h 5 min** cho một test anchor, hoặc
**6 h** cho 12 anchor chung trong draft. Hiện có thể bố trí 1/2 h; câu hỏi đủ
1/2/4 h **DATA_BLOCKED**, không được nói đã khả thi toàn bộ. Chưa kiểm VM có
capture dài hơn. Không dùng vòng lặp trace hoặc scale thời gian để xóa chặn này.

“Real trace” ở đây là source của **Cox intensity**. NPZ là counts 10 ms; code
sinh packet Poisson mới, service Exp(10), không giữ nguyên timestamp/phụ thuộc
flow. Literal packet replay cần PCAP/arrival-time input được xác minh riêng.

## Model và phép tính thực tế của EV-D4b/c

| Thuộc tính | EV-D4b | EV-D4c C | EV-D4c L / H | Setting letter cần |
|---|---|---|---|---|
| Queue/cost | 2 infinite FIFO, service Exp(10 packet/s); ∫sum Q, packet·s | Giống D4b | Giống D4b | Có thể giữ cùng kernel; không đồng nhất packet queue với fluid topology GÉANT |
| Background | DITL 4 h, s0/s1 là hai 10% flow partitions; shared phase; Cox packets | Cùng 4 h | L/H dùng đoạn 10:00 15 min | Train đầu, test sau; cùng cursor A/B, không wrap |
| Managed flow/actions | Poisson u; Stay=A, Switch=B; h cố định; không switch fee | Giống D4b | Giống D4b | Hai action cố định trong 1/2/4 h |
| Load | max(λA,λB)+u≤7,75, μ=10 | ≤0,775 | L≤0,775; H danh nghĩa (0,775;0,975] | Giữ giới hạn mean-load; không claim overload/general deployment |
| Observation | q cũ/mới; rate twins thêm window-rate; OLS nowcast từ stale q/rate | Giống D4b | Giống D4b | Cùng full state, chỉ khác tuổi; định nghĩa trace cursor rõ |
| Age τ | 1/10/30/60/120/300 s | r·probe T_int, r=.1/.3/.5/.8/1/1.2/2.5/5; actual 6,19–902,55 s | L 0,98–133,56; H 1,99–722,04 s | Draft giữ sáu τ D4b, không tự khóa card |
| T_int train (min/median/max, s) | 62,756 / 111,322 / 176,535 | 61,917 / 125,845 / 181,294 | L 9,797 / 19,265 / 26,730; H 19,893 / 74,271 / 144,903 | Báo chẩn đoán, không đổi hold physical-hour thành T multiplier |
| Hold | 10/30 T_int: 627,559–5296,056 s (10,46–88,27 min) | 619,165–5438,831 s (10,32–90,65 min) | L 97,969–801,898; H 198,927–4347,096 s | 3600/7200/14400 s |
| Sampling | 20 regimes×6 ages×2 h; 10000 instants/job, spacing 3 T_int, 40 batches | 20×8×2; cùng sampling | Mỗi arm 20×8×2 | Explicit anchors/replicas; báo dependence của overlapping windows |
| Train/test split | Seed khác, cùng toàn record periodic; train_T=100000 s | Giống D4b | Periodic 15 min | Chronological disjoint windows, train-only normalization/rates |
| Stale computation | Plug-in q cũ hoặc OLS point nowcast rồi fluid cost | Giống D4b | Giống D4b | E[V0(X_t;h)\|X_old], không V0(E[X_t\|X_old];h) |
| Evaluation/reference | Một sampled pair chi phí/action/instance; G_S normalized E_stay | Giống D4b | Giống D4b | Conditional MC; independent decision/evaluation; C_ref=L(M1_new) |

T_int range được tính từ **metadata đã lưu**, không chạy lại estimation. Hai hold
cùng case lặp cùng T_int nên median theo raw files bằng median theo train case.
“Continuous 4 h” mô tả record gốc, **không** mô tả train/test không lặp:
`trace_cox.arrivals()` dùng modulo; test long-run D4b bao phủ khoảng
130,84–368,18 vòng record. Vì start phase random, ngay cả một h<L cũng có thể
đi qua seam cuối/đầu. Train/test seed separation không tạo chronological split.

## Tám twin đã tính và mapping

Quy ước gap: Switch−Stay; gap<0 chọn Switch, tie chọn Stay.

| Tên raw EV-D4b/c | Fresh | Stale hiện có | Mapping sang letter |
|---|---|---|---|
| fluid | Constant-mean fluid tại q mới | Fluid tại q cũ | Kernel M0 dùng lại; stale cần posterior averaging |
| hybrid_mm1 | Fluid + h·s_MM1 | Cùng correction, q cũ | Auxiliary crude-rate hybrid; không thay learned ŝ |
| hybrid_train | Fluid + h·s_train | Cùng correction, q cũ | Gần hybrid letter; phải fit trên earlier interval và sửa stale |
| ratefluid | Exponential relaxation của measured rate | Ratefluid với q/rate cũ | Twin khác; không đổi nhãn thành constant-mean M0 |
| ratefluid_hybrid_train | Ratefluid + h·s_train | q/rate cũ + correction | Hybrid của twin khác, không trực tiếp là primary letter |
| fluid_nowcast | Fluid tại q mới | OLS dự báo q, rồi fluid | Không phải posterior E[cost]; giữ làm evidence lịch sử |
| ratefluid_nowcast | Ratefluid tại q/rate mới | OLS dự báo q/rate | Không phải posterior, twin khác |
| ratefluid_nowcast_hybrid_train | Ratefluid fresh + h·s_train | OLS + correction | PASS cũ không xác nhận hybrid posterior letter |

Không có stationary pipeline cost/regret riêng hoặc stochastic M1_new C_ref
trong raw. Train `mean_stay/mean_switch` có thể cho action rate-rule lịch sử,
nhưng per-instance branch costs/choices đã bị bỏ, nên không thể khôi phục cost
của stationary rule hoặc reference normalization chỉ từ các aggregate.
Hybrid_train và ratefluid_hybrid_train cũng không được gộp thành cùng một twin.

## Raw nào thực sự còn và đã kiểm

| Artifact local | EV-D4b | EV-D4c | Nội dung và giới hạn |
|---|---:|---:|---|
| cases/cases_all | 120 / 120 | 480 / 480 | Parameters/seeds/grid, không outcomes mới |
| train JSON | 120 | 480 | means, s_train, T_int, shares, OLS coefficients, CPU/wall |
| probe train JSON | 0 | 60 | D4c chọn τ từ probe T_int |
| predictions.csv | 480 rows | 1920 rows | Train-based leading-term predictions |
| test JSON | 240 | 960 | Aggregate G_S/se của 8 twins, E_stay, shares, metadata/timings |
| raw manifest | 240/240 SHA khớp | 960/960 SHA khớp | Không thiếu/đổi raw trong manifest |
| train_manifest | Không có manifest riêng | 540/540 SHA khớp | 480 main + 60 probe |
| source/data lock | 11/11 SHA khớp | 17/17 SHA khớp | Shared source hashes được kiểm ở cả hai lock |
| score/posthoc | Có | Có, thêm score_rows/rescore_independent | Evidence cũ đã exposed; không chấm lại khoa học ở lượt này |
| Per-instance q, posterior, action costs/decisions, C_ref | Không có | Không có | Không đủ cho letter end-to-end rescore |

1200/1200 saved test case signatures khớp case JSON trong raw. Một NPZ nguồn
4 h local có embedded metadata khớp sidecar; cả hai old source-lock khớp SHA
NPZ. Sidecar ghi SHA từng extracted `.bin`; không có các `.bin`/PCAP gốc trong
gói local đã kiểm để verify extraction đầu-cuối. Không suy source provenance
đã chứng minh hoàn toàn chỉ từ SHA NPZ. EV-D4c còn dùng NPZ 15 min cho L/H,
được old lock kiểm, không được dùng thay record continuous trong draft.

## Design summary và compute

[DESIGN.md](DESIGN.md) ghi split first hour, 12 test anchors sau train, tuổi
1–300 s, full state gồm cursor, posterior K=128 trước action-cost averaging,
learned ŝ từ paired CRN train, M0/Hybrid/Stationary/M1_new, separate R_dec=128
và R_eval=256, tie Stay và denominator C_ref. Tất cả là proposal, chưa card/lock.

Pilot local q=(0,0), 16 paired rollouts trên prefixes train 60/120/300 s:
**0,011316 / 0,017171 / 0,037115 CPU-s**, hữu hạn 3/3; peak 56,20 MiB.
Tổng kernel timing **0,065602 CPU-s**. Không tính ŝ hoặc test action/regret.
Đã kiểm known Lindley/CRN toy và synthetic parser/intensity behavior.

Đối chiếu saved timing: D4b **31577,153456 CPU-s** cho 240 test jobs
(8,7714 CPU-h), train thêm **3310,433576 CPU-s**; report cũ ghi ~44 phút wall.
D4b throughput median 5,977133e−6; D4c continuous C 7,924061e−6;
pilot 300 s 7,732301e−6 CPU-s/(paired rollout·s horizon). Không dùng wall report
cũ làm guarantee cho nested conditional reference mới.

Với 20 regime×96 states, central dự thảo **11,68 CPU-h** cho 1/2 h, **23,09
CPU-h** cho 1/2/4 h khi có đủ dữ liệu. Scenario separate horizons, worst observed
throughput +2× contingency: **53,01 / 122,54 CPU-h**. Với giả định 12 workers,
65% utilization, tương ứng **1,50–6,80 / 2,96–15,71 h wall**. Đây là ngoại suy
planning, không CI/budget đã duyệt. Microbenchmark quá ngắn để chứng nhận
long-horizon memory, K/R precision hoặc runtime bound. Xem công thức và máy đo
trong [compute_estimate.json](compute_estimate.json), [pilot.json](pilot.json).

## Chạy và kiểm chứng

Các command thực tế (đều local, không truth run):

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B -m experiments.letter.v7_2_audit audit
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B -m experiments.letter.v7_2_audit pilot
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B -m experiments.letter.v7_2_audit estimate
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=results/letter/v7_2/pytest_tmp experiments/letter/v7_2_checks.py tests/test_ext_trace_rates.py tests/test_ext_packet.py::test_lindley_brute_and_crn
```

Lượt checks đầu: **26 PASS, 2,31 s**. Bao gồm no-wrap/end-of-record feasibility,
train-prefix sampling, supplied training calibration, hash tamper detection,
exclusive output, synthetic PCAP/intensity và Lindley/CRN reduction. Không phải
26 scientific claims. Log: `tests.log`; final recheck/final integrity được ghi
riêng, không ghi đè log đầu. Không chạy full suite unrelated với tài liệu audit.

Files mới: `experiments/letter/v7_2_audit.py`, `v7_2_checks.py`, và thư mục
`results/letter/v7_2/`: report/design, initial_state, audit JSON/log,
raw_inventory CSV, pilot JSON/log, compute_estimate JSON/log, tests logs và
verification cuối. Không tạo figure, prediction card, test scientific raw hoặc
config truth-run; thông số proposal nằm trong DESIGN/compute_estimate.

## Giới hạn và điều chưa được xác nhận

- Một trace/một khung giờ, flow partitions cùng link; không traffic population.
- Mean-load panel ≤0,775; không bằng chứng tải cao continuous. Test-period mean
  sau train normalization có thể khác cap; instant load không bị cap.
- Sign-law cũ **yếu ở τ≈T_int**: D4b 110/158 sign agreement (~69,6%); D4c band
  continuous increment agreement ~54,2%, ratio ~0,196. Không dùng kết quả này
  làm forecast cho stale posterior twin hoặc h=4 h.
- Đổi seed không xóa exposure source/regime; scalar train rates không giải quyết
  nonstationarity. Stationary action/hybrid zero G_S có thể là lựa chọn tĩnh.
- Kernel/pilot PASS không xác nhận hypothesis, posterior correctness, reference
  precision, real-network realism hoặc 4 h feasibility. Hàng đợi/capacity/action
  là model áp lên traffic một link, không measured deployed routing.

Điểm dừng đúng brief: bàn giao draft cho Claude viết card; cần xác minh đủ
continuous coverage và hoàn thiện/test adapter trước một truth run được yêu cầu
riêng. **Không commit, không sửa existing files, không truy cập/điều khiển VM.**
