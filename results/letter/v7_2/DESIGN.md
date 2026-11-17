# V7-2 — design draft: chronological continuous trace for the letter

Người phụ trách: **Doan Van Tai**. Trạng thái: **DESIGN_DRAFT, chưa khóa**.
Phạm vi: audit và thiết kế theo brief tại HEAD `fc3ee0a1096b76a271e78a5011f79916acf8e746`.
Chưa có card, forecast khoa học, threshold mới hoặc test outcome V7-2.

## 1. Câu hỏi và điều kiện khả thi

Phân loại **B có điều kiện về dữ liệu**: tái dùng FIFO DES và công thức fluid,
thêm adapter chia thời gian, posterior, conditional stochastic reference và raw
per-instance. Không cần viết lại simulator hàng đợi. Output cũ không trả lời trực
tiếp setting letter. Gói local hiện có **không đủ cho cả 1/2/4 giờ** với train trước
test và không lặp trace.

Nguồn được kiểm: MAWI samplepoint-F DITL 2023-04-12, 16 file liên tiếp nhãn
10:00–13:45, NPZ 1.440.007 bin × 0,01 s = **14.400,07 s**. SHA256
`39f75928a27ab03a9751939277f980e7126bc22bdaef5268d57bb9207aa4b81c`.
Hai tập flow mod-10 = 0/1 được dùng làm hai đường A/B, giữ cùng cursor thời gian.
Manifest ghi 8 bin được điền, 0 bin overlap; không gọi đây là capture hoàn hảo
không có gap. Không truy cập VM trong lượt này vì NPZ cần cho audit/pilot đã local;
chưa xác minh VM có capture liên tục dài hơn hay còn PCAP timestamp gốc.

NPZ chứa **packet counts**, không còn timestamp từng packet. Setting tái dùng là
**trace-conditioned Cox packet queues**: giữ intensity 10 ms từ trace, sinh Poisson
arrivals và exponential services mới. Đây không phải replay nguyên packet/flow
dependence. Nếu yêu cầu là replay nguyên timestamp, cần xác minh PCAP trên VM và
thiết kế adapter đầu vào khác trước card; không đổi nhãn Cox thành literal replay.

## 2. Split và holds, không wrap

Dự thảo dùng first hour `[0,3600)` làm train, gồm warmup `[0,900)` và khoảng tính
rate `[900,3600)`. Không đưa phần test vào normalization, fit, chọn regime hoặc
chọn action tĩnh. Giữ lịch sử Stay từ đầu record để lấy các state liên quan.

Tuổi dự thảo: **τ = {1,10,30,60,120,300} s**. Anchor đầu tiên
`t0 = 3600 + max(τ) = 3900 s`, để cả observation cũ nhất cũng sau train.
Holds là **h = {3600,7200,14400} s**; không thay bằng 10/30 T_int, không scale
đơn vị thời gian để làm 4 h vừa record. Điều kiện cứng: `t − τ ≥ 3600` và
`t + h ≤ L`; generator không dùng modulo, random circular phase hoặc nối cuối về đầu.

| Hold | Anchor hợp lệ trên lưới 300 s, record hiện tại | Điều kiện dữ liệu |
|---|---|---|
| 1 h | 3900…10800 s, 24 anchor | Có đủ metadata coverage |
| 2 h | 3900…7200 s, 12 anchor | Có đủ metadata coverage |
| 4 h | 0 anchor | Ít nhất 18300 s = 5 h 5 min cho một anchor |

Để so các hold trên cùng instance, đề xuất dùng **12 anchor chung**
`3900,4200,…,7200 s`, mỗi anchor 8 lịch sử stochastic → **96 state/regime**.
Với cả ba hold, record liên tục phải dài **ít nhất 21600 s = 6 h**. Với NPZ đang
có, 12 anchor này chỉ hỗ trợ 1/2 h. Giữ mục 4 h là **DATA_BLOCKED**, không tự bỏ
khỏi denominator, không tự chạy subset thay cho câu hỏi ba hold. Claude cần chốt
coverage và card trước run; lượt này không tìm/tải thêm trace.

20 regime đề xuất là 20 bộ `(λA,λB,u)` đã dùng ở EV-D4b, mỗi bộ lấy một lần,
không nhân sáu tuổi thành sáu regime độc lập. Đây là panel đã exposed, chưa gọi là
confirmation độc lập. `max(λA,λB)+u ≤ 7,75`, μ = 10 packet/s. Cap **0,775 là mean
parameter load của panel cũ**, không chặn instantaneous intensity. Khi normalize
bằng train thay vì full record, test-period mean load có thể khác cap; phải báo
load test theo card, không loại hậu nghiệm những window bất lợi.

## 3. Model, full state và posterior

Giữ hai FIFO queues vô hạn, service i.i.d. Exp(μ=10), managed Poisson flow rate u;
action 0 = Stay (flow ở A), action 1 = Switch (flow ở B), giữ action suốt h.
Cost `J_a = ∫₀ʰ (Q_A^a(s)+Q_B^a(s)) ds`, đơn vị packet·s; không có switching fee
hoặc terminal surcharge trong model EV-D này.

Với trace intensity có lịch theo thời gian, backlog đơn lẻ hoặc backlog cộng một
window-rate chưa bảo đảm là full Markov state. Dự thảo định nghĩa
**X_t = (Q_A(t),Q_B(t),φ_t)**, với φ là cursor của cặp intensity trace. Nhờ
exponential service/Poisson managed flow, không cần residual service hay managed
interarrival age. Fresh quan sát `X_t`, stale quan sát **cùng loại** `X_{t−τ}`.
M0 có thể bỏ qua cursor do model misspecification; không được bỏ cursor khỏi
reference state rồi gọi queue-only observation là full-state.

Posterior dưới luật reference có điều kiện theo record cố định:
`X_t^(k) ~ P_ref(X_t | X_{t−τ}, Stay trên (t−τ,t])`, K dự thảo = 128.
Propagate q cũ với conditional exponential residual services và intensity tại
cursor tương ứng; không đưa q mới thực tế vào sampler. Cursor mới là thời gian
cũ cộng τ, không lấy phase random mới. Các pipeline dùng chung posterior samples.

Stale twin phải tính **mean của action cost/gap sau propagation**, ví dụ
`g0_old = K⁻¹ Σ_k g0(Q_t^(k);h)`; không dùng `g0(E[Q_t|old];h)`, không OLS
point nowcast, không trực tiếp đánh giá ở q cũ. Nonlinearity/clipping khiến các
cách này khác nhau. Posterior dùng reference conditional law là inference oracle
cho thí nghiệm age-only, chưa phải posterior operator có thể học chính xác từ
một giờ traffic. Nếu đổi sang posterior fit từ train, phải ghi thành yếu tố
misspecification riêng trước card.

Đây là model-conditioned reference với trace schedule cố định được biết bởi
simulator/reference; không diễn giải nó thành dự báo tương lai traffic ngoài đời.

## 4. Train-only rates và ŝ

Tính `m_j_train = mean(count_j[0:3600])` theo bin trên train, khóa trước test.
Intensity test là `λ_j × count_j(t)/m_j_train` với λ_j là design parameter; không
gọi `trace_cox.series()` nguyên trạng vì nó normalize bằng mean **cả record**.
M0 dùng λ_j train-mean cố định. Không refit bằng mean của test window.

Cho mỗi regime, chạy đề xuất 32 paired CRN training replicas trên **một lượt đi
tới** record train: chung background packets, managed packets, per-packet
services cho hai action. Khởi tạo queue rỗng như model, bỏ 900 s đầu, rồi tính
`rhat_a = mean_replicates [ (1/2700) ∫₉₀₀³⁶⁰⁰ (Q_A^a+Q_B^a) dt ]`,
`ŝ = rhat_Switch − rhat_Stay` (packet). Giữ batch/replica uncertainty và ký hiệu
finite-window estimate; một giờ nonstationary không chứng nhận true stationary
mean. Không lấy ŝ cũ từ EV-D4b/c vì train cũ đi qua/lặp toàn record.

Freeze calibration, training seeds, rhat/ŝ, observation model và schedule trước
test. Các training replicas chỉ đo Monte Carlo variance trên cùng train record;
không tạo thêm trace độc lập. Học transition law hoàn chỉnh của traffic từ một
giờ dữ liệu chưa được xác nhận bởi design này.

## 5. Pipelines và tie rule

Đặt `g0(q,h) = V0_Switch(q,h) − V0_Stay(q,h)`, từ `packet.fluid_gap` ổn định
về cancellation; M0 là constant-mean deterministic fluid twin.

| Pipeline | Fresh | Stale |
|---|---|---|
| M0 | `g0(Q_t,h)` | posterior mean `g0_old` |
| Hybrid-train | `g0(Q_t,h) + h·ŝ` | `g0_old + h·ŝ` |
| Stationary-train | Switch iff `ŝ < 0` | Cùng action, không dùng state |
| M1_new reference | conditional stochastic cost, decision stream riêng | Không cần M1_old cho câu hỏi này |

Mỗi gap < 0 chọn Switch; gap = 0 chọn Stay. Báo exact tie share và action share
theo side/age/hold. Không thêm epsilon hoặc tie-break khác sau khi thấy kết quả.
Stationary có `G_S = 0` theo cấu trúc, không được đếm là bằng chứng hybrid đã sửa
harm. So cả M0, hybrid và stationary về cost/regret fresh **và** stale.

## 6. C_ref và evaluation không dùng realized clairvoyance

Với mỗi fresh state, mỗi action và mỗi hold, dùng stochastic FIFO futures trên
đúng interval tiếp theo của record, cùng background/managed packet/service CRN
giữa action. Thay background realization trong từng conditional replica; không
giữ một background chung rồi gọi noise của managed flow là toàn bộ reference.

Dùng hai stream độc lập, kích thước đề xuất lấy theo letter E4:

- `R_dec = 128`: lấy mean conditional costs để chọn `a_ref = argmin_a Vhat_dec,a`.
- `R_eval = 256`: lấy mean action costs `Vhat_eval,a` độc lập; chấm **mọi** pipeline
  và reference bằng cùng array này, không simulate lại theo pipeline.
- `C_ref(h) = mean_i Vhat_eval,i,a_ref(i,h)(h)`; lưu cả E_stay để đối chiếu denominator.
  Không dùng `mean min_a realized J_a`, không dùng E_stay thay C_ref.

Holds nested dùng chung realization tới h_max, lưu prefix residence costs cho
từng h. Đây là adapter mới cần kiểm trước truth; không xem timing pilot là kiểm
độ chính xác reference. Reference finite-R là policy MC, chưa phải exact optimum;
regret signed không clamp nếu estimate âm. Precision/tolerance phải do card chốt.

`G_S = L_stale − L_fresh`; regret side = `L_side − C_ref`, báo raw packet·s và
`100×()/C_ref`. Báo paired Monte Carlo SE theo lịch sử, cùng thống kê theo anchor;
không coi 12 overlapping windows × 8 replicas × 6 tuổi là independent traffic
trials, không population CI từ một trace.

Raw mới cần có `q_fresh`, `q_stale`, cursor, anchor/replica IDs, parameters,
posterior seed/K hoặc samples, per-action evaluation means và uncertainty,
reference decisions, pipeline decisions/ties, τ/h, train/input hashes, CPU/wall.
Đủ để gather lại costs và rescore độc lập; JSON aggregates cũ không đủ.

## 7. Adapter scope và checks trước một run sau này

Tái dùng `packet.departures`, `backlog`, `fluid_gap`, `lindley_cost` và CRN
construction trong `long_run_crn`; tái dùng cấu trúc mean-before-argmin,
decision/evaluation split, gathering của letter E4. Không monkey-patch hay sửa
source frozen EV-D4b/c. Adapter sau này phải độc lập: generator đi tới có cursor
và train normalization; conditional state propagation; explicit-second holds;
conditional futures; prefix costs và raw per-instance writer.

Checks cần trước card/truth: τ=0 stale/fresh khớp; Jensen/nonlinear averaging toy;
u=0 hai action khớp; age-only state schema; no-wrap tại end; train-normalizer
không đọc test; CRN action equality; decision/eval seeds khác; synthetic
exponential queue reduction; prefix cost khớp direct integration. Lượt V7-2 này
**chưa implement hoặc xác nhận** các adapter posterior/reference đó.

## 8. Compute estimate, đo được và ngoại suy

Pilot local chỉ dùng train calibration `[0,3600)` và physics prefixes 60/120/300 s,
q ban đầu tổng hợp = (0,0), 16 paired rollouts/mức, seeds 8722001/2/3,
`λA=7,25, λB=7,03, u=0,5`, một process/BLAS thread. Không chọn action, không
ước lượng ŝ, không tính G_S/regret/test outcome. Cost train vừa tính bị bỏ ngay.

| Prefix | CPU tổng | Wall | CPU/(paired rollout·s horizon) |
|---|---:|---:|---:|
| 60 s | 0,011316482 s | 0,011316609 s | 1,1788002e−5 |
| 120 s | 0,017170726 s | 0,017174760 s | 8,9430865e−6 |
| 300 s | 0,037115043 s | 0,037118581 s | 7,7323006e−6 |

Peak process RSS pilot 56,20 MiB. Đây là microbenchmark ngắn, không phải pilot
precision/long-horizon memory. EV-D4b saved test tổng **31577,153456 CPU-s**, median
116,433141 s/job, throughput median 5,977133e−6 CPU-s/(instance·s horizon);
continuous EV-D4c C median 7,924061e−6. Chúng cùng bậc nhưng khác máy/workload.

Với G=20, N=96, K=128, R_dec+R_eval=384, R_train=32:

`work = G·N·384·h_max + G·N·K·Στ + G·32·3600 + G·8·7200`.

Central CPU = work × throughput 300 s pilot. Scenario dự phòng thay h_max bằng
Σh, dùng worst observed throughput (pilot/D4b/C), nhân thêm **2× contingency**.
Đó là giả định planning, không runtime bound/CI hay budget được duyệt.

| Phạm vi | Central CPU-hours | Scenario dự phòng CPU-hours | Wall giả định 12 workers, 65% utilization |
|---|---:|---:|---:|
| 1/2 h trên record đang có | 11,68 | 53,01 | 1,50–6,80 h |
| 1/2/4 h khi có ≥6 h record | 23,09 | 122,54 | 2,96–15,71 h |

Khác biệt với run D4b ~44 phút là D4b chỉ có một sampled cost pair/instance,
không R_dec+R_eval conditional rollouts và không posterior K. R/K/N chưa kiểm
precision; Claude có thể chốt thiết kế khác **trước** outcomes và tính lại budget.
Không có VM shape/action được chọn trong lượt này.

4 h ở throughput/mean rates này cho khoảng 212832 events/paired rollout. Ước
lượng 12 float64 arrays: batch8 ~0,152 GiB; batch16 ~0,304 GiB;
batch256 ~4,87 GiB/worker, **chưa** padding peaks/sorting/objects. Không giữ nguyên
batch256 của `packet.simulate`; batch nhỏ/prefix reuse là yêu cầu feasibility,
không thay physics. Không khẳng định peak memory 4 h từ peak pilot.

## 9. Exposure, rủi ro và điểm dừng

Đã đọc reports, code, manifest và metadata/timings raw cũ; cùng trace/regime đã
có outcomes D4b/c. Pilot thêm exposure train means 86,473578/160,612106 counts/bin,
không thêm test outcomes. Split mới không biến record cũ thành unseen trace.

Giữ đủ giới hạn: một trace/khung giờ; hai flow subsets cùng một link; low
mean-load panel ≤0,775; mất packet/flow dependence khi Cox hóa; nonstationarity
và finite train rates; conditional-reference/oracle information; uncertainty MC
chưa đo; nhiều windows chồng lấn; sign law cũ yếu gần τ≈T_int. D4b sign agreement
110/158, D4c C band increment agreement ~54% là evidence cũ, không forecast cho
posterior twin mới. Không chuyển verdict plug-in/OLS sang posterior setting.

**Dừng tại draft.** Claude viết card sau khi giải quyết 4 h coverage, model/state
semantics, kích thước mẫu, precision và budget. Không có run, score, commit,
download, SSH hoặc VM mutation trong V7-2 này.
