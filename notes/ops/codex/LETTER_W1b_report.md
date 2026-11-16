Đã triển khai E3 age-only và các mức ŝ, chạy **93 regimes × 5 ages**: **3.255 dòng E3, 32.550 dòng hybrid**. `ctmc.py`, brief, card và toàn bộ **100 file đầu vào giữ nguyên hash**.

| Prediction | Kết quả đo được |
|---|---|
| **P7 — đứng** | **194/217 = 89,40%** dòng giữ harm, vượt ngưỡng 60%. |
| **P8 — đứng** | Median ratio age-only/confounded tại τ=1 s: **0,963718 < 1**. |
| **P9 — đứng** | True s: **98,13%** dòng đạt regret ≤0,1% C_ref trên cả fresh/stale; sáu mức ε đạt **97,53–98,13%**. |
| **P10 — chưa đánh giá được** | **0 VALID, 93 INVALID**, đều fallback M/M/1. API từ chối α̂ liên tục; 8 regimes đồng thời có lỗi miền tham số ước lượng. |
| **P11 — không đứng trên panel hữu hạn** | Với −s, ngay tại h≥7T_int, max \|G_S\| còn **2,050% C_ref**. Card chưa định lượng “≈”; giới hạn h→∞ được phân biệt riêng. |
| **P12 — đứng** | Khi h<T_int, true-s hybrid tệ hơn M0 ở ít nhất một phía trong **581/995 dòng**. |

Median regret, đơn vị **% C_ref**; mỗi ô là **fresh / stale**:

| h/T_int | M0 | Hybrid true s | Hybrid M/M/1 | Hybrid −s |
|---|---:|---:|---:|---:|
| <1 | 0,508 / 0,737 | 0,381 / 0,720 | 0,192 / 0,608 | 4,091 / 5,951 |
| 1–<4 | 3,076 / 0,876 | 0,01197 / 0,01406 | 0,01196 / 0,02896 | 14,969 / 17,107 |
| 4–<7 | 4,445 / 1,287 | 8,69e−5 / 1,84e−4 | 7,96e−4 / 2,91e−4 | 18,555 / 20,053 |
| ≥7 | 5,836 / 1,889 | 1,04e−7 / 4,45e−7 | 2,96e−6 / 1,95e−6 | 22,174 / 22,498 |

P7/P8 chỉ dùng **92 baselines có kết quả**. Baseline case cuối đã là `UNRESOLVED` từ trước. Ba case files thực tế chứa **93 regimes**, khác con số 99 trong brief.

Đã chạy các lệnh chính sau trong môi trường `.venv` và `env.sh`:

```bash
python3 -u -m experiments.letter.shat run --workers 8
python3 -u -m experiments.letter.shat recover --workers 8
python3 -m experiments.letter.shat analyze
python3 -m pytest -q tests/test_letter_w1b.py --basetemp=/tmp/lw1b_pt -o cache_dir=/tmp/lw1b_cache
```

Pytest cuối: **15 PASS, 1 XFAIL**. Tại τ=0, mọi pipeline có G_S=0; giả định τ→0⁺ trong brief không đúng trên exact M0 ties, được giữ thành XFAIL. Đối soát độc lập **PASS**, gồm 93 telemetry seed replays, hash và phép chấm P7/P8/P9/P12.

CPU đo được cho các evaluations hoàn tất: **20.715,78 s = 5,754 CPU-h**. Wall từ run plan đến raw cuối: **130,20 phút**. Lượt đầu gặp lỗi forkserver; sau đó có một lần dừng case cuối để sửa I/O baseline thiếu. **CPU phần bị dừng không đo được**, nên chưa có tổng CPU toàn phiên.

Các file chính:

- Mã: [e3_agediff.py](/home/vantai/state-model-regret/experiments/letter/e3_agediff.py), [shat.py](/home/vantai/state-model-regret/experiments/letter/shat.py), [tests](/home/vantai/state-model-regret/tests/test_letter_w1b.py).
- Báo cáo đầy đủ, gồm từng mức ŝ và switch shares: [README.md](/home/vantai/state-model-regret/results/letter/w1b/README.md), [summary.csv](/home/vantai/state-model-regret/results/letter/w1b/summary.csv), [analysis.json](/home/vantai/state-model-regret/results/letter/w1b/analysis.json).
- Raw và kiểm chứng: [raw manifest](/home/vantai/state-model-regret/results/letter/w1b/raw_manifest.json), [verification.json](/home/vantai/state-model-regret/results/letter/w1b/verification.json), [pytest log](/home/vantai/state-model-regret/results/letter/w1b/pytest_final.log).
- Lịch sử chạy: [run log](/home/vantai/state-model-regret/results/letter/w1b/run_fork.log), [recovery log](/home/vantai/state-model-regret/results/letter/w1b/recovery.log), [interruption](/home/vantai/state-model-regret/results/letter/w1b/interruption.json).
- Cấu hình: [run plan](/home/vantai/state-model-regret/results/letter/w1b/run_plan.json), [recovery plan](/home/vantai/state-model-regret/results/letter/w1b/io_recovery_plan.json), [environment](/home/vantai/state-model-regret/results/letter/w1b/environment.json).

Đây là kết quả trên panel CTMC hữu hạn, không có population CI hoặc kết luận novelty. Không tạo biểu đồ. Tôi không tạo commit và không dùng SSH; HEAD đã thay đổi trong lúc chạy, được ghi tại [git_state.json](/home/vantai/state-model-regret/results/letter/w1b/git_state.json).