# Analysis plan v1 — L4.9 (v2), ngoại suy trong frozen plant

Người phụ trách: **Doan Van Tai** · 31/10/2026. AI hỗ trợ triển khai.
**FROZEN_FOR_FUTURE_EVALUATION** khi file này được commit; chưa chạy Phase 5,
chưa thông qua Gate 4. Lựa chọn tác giả lưu nguyên văn ở
[thresholds](../../results/lessons/l4_9_v2/author_choice.json) và
[roles](../../results/lessons/l4_9_v2/author_role_choice.json).

## 1. Câu hỏi và phạm vi

Trong slotted primary plant v1.3, liệu state value còn nhỏ ở 12 tọa độ có
h/κ lớn hơn discovery? H-L1 là primary. H-L2 là exploratory theo stop rule
sau Part B; giữ predictor và ngưỡng cũ, không fit thêm. Bỏ H-L3.
Không thay contract, S0/S1, M0/M1, cost, Cref hoặc baseline lịch sử.
[T09](../theory/T09_stationary_dominance_limits.md) sửa suy luận uniform h*:
pointwise transient O(1) không chặn được mọi backlog trong population unbounded.
Không dùng h* từ range M0 hoặc dự đoán exact zero sau một finite horizon.

## 2. H-L1 — primary, finite-panel state equivalence

| Thành phần | Đặc tả cố định |
|---|---|
| Đại lượng | z=GS\|M1/Cref=(L01−L11)/L11, Cref>0 |
| Điều kiện | Đúng 12 tọa độ §5; cả hai paths stable dưới cả hai actions |
| Cơ chế giả thuyết | Stationary cost có thể lấn át transient; h/κ chưa bảo đảm mixing hoặc uniform action |
| Dự đoán | z≤0,005 ở ít nhất 90% panel; dự đoán này áp dụng mọi điểm đã khai, không sàng theo predictor |
| Kiểm định | Fixed lean readiness + R6 ở §6; M/F/U tính trên mẫu số N=12 |
| Bác bỏ | Nếu (M+U)/12<0,9 và U/12≤0,1: FAIL; nếu M/12≥0,9 và U/12≤0,1: PASS; còn lại INCONCLUSIVE |

Với N=12 và không U, cần ít nhất 11 MEETS; 2 FAILS đã bác bỏ.
Không đổi sang mẫu số READY, không gọi tỷ lệ panel này là population prevalence.
Panel chưa đủ 12 hoặc U>1 thì INCONCLUSIVE. Không có binomial CI/p-value:
đây là các model coordinates cố định, không phải mẫu ngẫu nhiên từ mạng thật.

## 3. H-L2 — exploratory, magnitude predictor không fit

| Thành phần | Đặc tả cố định |
|---|---|
| Đại lượng | GM\|S1/Cref=(L10−L11)/L11, báo bằng %Cref |
| Điều kiện | Cùng panel; stationary moments xác định được dấu s; không dùng finite-h M1 để dự báo |
| Cơ chế giả thuyết | M0 bỏ stationary congestion cost; stationary action có thể quyết định leading-order loss |
| Predictor | s=rSwitch−rStay; aStat=1[s<0]; gHat=100·abs(s)·Prπ(aM0,h≠aStat)/min(rStay,rSwitch) |
| Ngưỡng tham khảo | Spearman≥0,7 **và** MedAE≤0,7·MedAE1NN; cả hai điều kiện |
| Đọc kết quả | Đủ 12 READY, cùng frozen predictions so với truth ở cả 3 levels: đạt cả 3→PASS exploratory; trượt cả 3→FAIL exploratory; mixed/missing→INCONCLUSIVE |

K predictor=320, ref=4; conditional mean-only `P.mean_idle`, exact ties chọn
Stay, giữ zero/saturation certificates. Không so mathematical signs tại ties.
Stationary laws/moments là true-law inputs của controlled study; không đọc
held-out losses/Cref/contrasts. s=0 do λA=λB cho predictor 0, không suy finite-h
GM bằng 0; sign chưa xác định thì NOT_READY. Không đổi K, formula, threshold,
scaling hoặc fit sau Part B/held-out. Constant ranks và null MedAE=0 không cho
claim thắng null. Exploratory PASS không nâng thành confirmatory evidence.

## 4. Null và dữ liệu tham chiếu

1-NN Euclidean trên (λA/10,λB/10,u/10,logκ,logh); không fit feature scaling.
Tie chọn canonical key nhỏ nhất theo thứ tự từ điển. Frozen training CSV:
[nn_training.csv](../../results/lessons/l4_9_v2/discovery/nn_training.csv),
1.231 unique physical keys = 597 native + 634 pilot amp6. Native ưu tiên;
pilot age1 rồi age variants. Loại CF/sealed trước khi parse metric; đã bỏ 1
pilot sealed alias. Discovery validation loại đúng physical key đang dự báo.
Không dùng outcome hoặc thêm calibration h32 vào null của panel tương lai.

## 5. Held-out panel — đúng 12 điểm, chưa có truth

μ=10, amplitude=6, τ=1, η=1/2 nên u=1, c_sw=0. Mỗi cặp load dưới đây dùng
ba (κ,h), theo thứ tự **(1/20,16), (1/10,32), (1/20,32)**:

| IDs theo thứ tự | λA | λB | h/κ tương ứng |
|---|---:|---:|---|
| P5_01–03 | 6 | 13/2 | 320,320,640 |
| P5_04–06 | 13/2 | 6 | 320,320,640 |
| P5_07–09 | 7 | 8 | 320,320,640 |
| P5_10–12 | 8 | 7 | 320,320,640 |

Exact parameter vectors và ID order nằm trong
[protocol.json](../../experiments/P4_09_stationary/protocol.json), commit
834b4074 trước predictor mới. Không dùng tổ hợp κ=.1,h=16 vì ratio=160.
Audit registry/training/R3R_11: max ratio đã đăng ký=160, 12 keys đều mới,
không CF hoặc sealed R09/R10. Không thay điểm, thêm N hay lọc theo prediction.
Đây là extrapolation theo ratio và exact coordinates, không bằng chứng toàn
khoảng [200,640], mọi load hoặc toàn miền realistic.

## 6. Numerical rule, budget và stop

Dùng nguyên native evaluator và frozen lean rules: main (640,4), coarse
(320,4) và (640,2). R1 hai axes, arithmetic width≤1/4000, lean consistency
≤1/400 Cref; `P4_A1.checks.row_readiness`. Kiểm same-route/algebra trên mỗi
level: BUG thì dừng, giữ output. Raw cross-route flags được báo, không thêm
gate mới. R6 `d_normalized` là max refinement deltas/arithmetic width:
**diagnostic, không certified bound/CI**. Tại main, với z và d của GS|M1:
không READY hoặc abs(z−.005)≤d→U; ngoài boundary zone, z≤.005→MEETS,
z>.005→DOES_NOT_MEET. Giữ số âm/flags, không clamp hoặc nới tolerance.

Budget tương lai 28.800 CPU-s (8 CPU-giờ), tính cả mọi child, failed call và
cache creation; một worker, 1 BLAS thread. Tối đa 12×3 levels, đúng ID order
và main→hai coarse. Kiểm lại gate/collision/frozen files trước mọi true call.
Hết budget, BUG, execution/resource failure hoặc U thứ hai: dừng và báo
INCONCLUSIVE nếu không đủ panel; không retry/refinement/A4 để cứu verdict.
H-L2 chỉ chấm đủ 12 READY ở ba levels. Không nhìn rồi thay order/cases.

## 7. Đã xem gì trước freeze

L4.1–4.8 và toàn discovery liên quan đã lộ; SV FAIL_SCREEN DL-116
(216 MEETS/224 FAILS/9 U trên449 plus), 10 SUB completed đã park; L4.6
1.118 unique pilot/597 native; L4.7 mechanism pass nhưng P_clip saturated,
S_clip/sigma identity; L4.8 empirical domain UNRESOLVED. SUB còn66 keys và
270 CF-v2 vẫn park; không gọi đó là panel mới của plan này.

Bảng exploration đã có trong lesson input (AI khác báo, raw pilot amp6):

| h/κ | n raw | median GS\|M1 (%Cref) | median GM\|S1 (%Cref) |
|---|---:|---:|---:|
| .6–3 | 230 | .55 | .10 |
| 3–10 | 338 | 1.13 | .11 |
| 10–30 | 284 | .58 | 1.08 |
| 30–100 | 248 | .06 | 4.89 |
| 100–161 | 36 | .00 | 10.68 |

Replay raw counts khớp 1.136, gồm18 exact duplicates; riêng bin3–10 bỏ metric
sealed XA097 trước conversion nên chỉ337 metrics, medianGS=1.136449, không
nhận đã tái lập toàn median338. Tìm rộng hơn có26 fixed κ=.1/age1 slices
h2→4→8:24 có state giảm/model tăng,2 ngoại lệ λA=λB=8.5. Sáu slices do
nguồn input chọn không có danh sách đầy đủ; không suy universal monotonicity.
[Replay artifact](../../results/lessons/l4_9_v2/supplied_exploration_replay.json).

Part B đã xem đủ86 native keys có h/κ≥30: Spearman .549016; MedAE predictor
5.267210 pp so1NN1.517567 pp (sai số lớn3.470825 lần). 41 raw flags được giữ;
45 điểm không raw flag vẫn thua: rho=.628611, MedAE5.175858 vs1.480960 pp.
Không fit/tạo predictor thay thế. Tác giả chọn thresholds **trước** Part B,
đổi H-L2 sang exploratory **sau** kết quả này và trước held-out.

Đã gọi lại 3 điểm h16 có profiles cached. H32 mới chỉ là calibration
(7,6,κ=.3,η=.5,h32), ratio106.67, disjoint panel; bị SIGXCPU sau60.552639
CPU-s, chưa có completed row. Giữ partial exposure, không gọi là truth cũ
hoặc dùng làm held-out/null. Lỗi adapter scale ban đầu đã sửa trước86 outputs;
failed attempt/test log giữ nguyên. Không tác giả tự viết proof/forecast kín sách.

## 8. Freeze và mức độ sẵn sàng

Code predictor/score, protocol, choices, null CSV và plan được hash trong
`analysis_plan_v1.lock.json`; lưu SHA commit trước mọi future truth output.
Parameter-only predictions có thể được lưu sau commit plan, vẫn trước truth;
không chọn lại panel theo chúng. Các frozen engine locks cũ vẫn phải verify.
Đây là freeze sau discovery, không prereg trước discovery.

Part C:3/3 cached h16 hoàn tất, warm native calls .298654/.662336/.320538 CPU-s;
original recorded calls28.790172/38.290002/12.097328 CPU-s có mức reuse khác
nhau, không phải đo fresh full bundle. H32 chưa đo xong nên **feasibility
UNRESOLVED**; N12/B8h là giới hạn thực thi có stop, không cam kết đủ budget.
Không chạy thêm benchmark dài trong L4.9. Freeze design không tự đóng Gate4,
P0-V10/L8/Understanding hoặc human review; Phase5 cần bước kiểm gate riêng.

## 9. Được nói và không được nói

Nếu H-L1 PASS chỉ nói state value nhỏ trên panel/model/resolutions đã khai.
Không nhận exact finite-h vanishing, uniform optimal action, numerics solved,
novelty của long-run transient, hoặc phổ quát hóa từ12 coordinates.
H-L2 hiện chưa có predictor magnitude đủ tốt trên discovery; exploratory
future check không cứu lại confirmatory label. Không dùng ratio of medians
để chứng minh SUB là99% interaction. Không claim telemetry tươi làm hại khi
D22 joint(Y,Q) còn DEFERRED; không claim production/DC realism từ scaling
minh họa. Chỉ dùng saved local P13 note trong lượt này, chưa primary reread mới.
