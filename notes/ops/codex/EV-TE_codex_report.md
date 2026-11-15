Đã tạo [Arm S]( /home/vantai/state-model-regret/experiments/ext_validity/ev_te.py), [Arm R](/home/vantai/state-model-regret/experiments/ext_validity/ev_te_trace.py), [pipeline GCP](/home/vantai/state-model-regret/experiments/ext_validity/ev_te_pipeline.sh) và [tests](/home/vantai/state-model-regret/tests/test_ev_te.py). Không sửa file cũ, commit hoặc SSH; **chưa chạy truth, Arm R evaluation hay score**.

Đã chạy `fetch`, `design`, `train --workers 8`, `predict`, Arm R `train` và bốn timing pilots seed 777. Kiểm chứng cuối: **73 tests PASS trong 12,73 s**, routing **594/594 ODs khớp**; pipeline `bash -n` PASS. Lỗi half-step ở smoke ban đầu đã sửa trước training.

Training seed A=1, `N_train=2000`, `K=128`:

- **64/64 files**, giữ 61 regimes, tạo **732 prediction rows**.
- CPU training: **13.264,092 CPU-s**.
- `T_int`: **0,292865–96,633304** fast-mode time units.
- Loại `G1_r80_b3_s0`, `G2_r80_b3_s0`, `G3_r80_b3_s0`: `P(Q>0)` lần lượt **0,925%; 0,97125%; 0,9895%**, đều dưới 1%.

| Topology | Bottleneck | OD1 / OD2 / OD3 |
|---|---|---|
| Abilene | IPLSng → ATLAng | CHINng_LOSAng / CHINng_HSTNng / CHINng_ATLAng |
| GÉANT | ch1.ch → at1.at | ch1.ch_de1.de / ch1.ch_se1.se / ch1.ch_at1.at |

Set 4 là `{OD1, OD2}`. Với single OD, `rSwitch < rStay` ở **24/24 Abilene**, **6/21 GÉANT**. Median training `rStay → rSwitch`: **409,514 → 0 Mb** và **779,704 → 1.953,789 Mb**. Với hai OD, số action thấp hơn Stay theo actions 1/2/3: Abilene **8/8, 8/8, 8/8**; GÉANT **0/8, 3/8, 0/8**.

| Timing pilot, N=3 | CPU-s/instance |
|---|---:|
| A4_r90_b6_s0 | 0,522 |
| A2_r90_b6_s1 | 4,033 |
| G4_r90_b6_s0 | 3,527 |
| G4_r90_b6_s1 | 15,764 |

Peak RSS pilot: **64,410 MiB/worker**. Đề xuất giữ **N=500, K=128, R_dec=128, R_eval=256, 32 workers**: dự toán **185.473 CPU-s**, dự phòng 2× thành **370.947 CPU-s < 800.000**. Đây là ngoại suy từ máy local, chưa phải timing GCP.

Arm R strict training đo `T_int` **115,269 phút** tại ρ=0,8 và **115,487 phút** tại ρ=0,9. Managed sets: `LOSAng_CHINng` và `{LOSAng_CHINng, WASHng_IPLSng}`. Có **7.776 missing bins**; parser strict đánh dấu **44.947 files thiếu OD**, giữ **3.149 files đủ 132 entries**.

Ba điểm cần review trước lock:

- **12 regimes có action mean utilization >1**: `r_a` chỉ là finite-run average; predictions đã gắn cờ nonstationary.
- `dt` được chọn từ pilot training; `T_int` kiểm tra trên grid cuối được lưu riêng.
- Chưa xác nhận OD vắng trong TM là zero hay missing; Arm R hiện chỉ phản ánh strict subset.

Báo cáo đầy đủ, commands, lỗi ban đầu và đường dẫn artifact nằm tại [IMPLEMENTATION_REPORT.md](/home/vantai/state-model-regret/results/ext_validity/ev_te/IMPLEMENTATION_REPORT.md). Số liệu chính: [training CSV](/home/vantai/state-model-regret/results/ext_validity/ev_te/training_summary.csv), [predictions](/home/vantai/state-model-regret/results/ext_validity/ev_te/predictions.csv), [timing](/home/vantai/state-model-regret/results/ext_validity/ev_te/timing.json), [budget proposal](/home/vantai/state-model-regret/results/ext_validity/ev_te/budget_proposal.json), [test log](/home/vantai/state-model-regret/results/ext_validity/ev_te/tests_sparse_final.log).

Chưa tạo biểu đồ hoặc lock. **H1–H4 chưa được kiểm định.**