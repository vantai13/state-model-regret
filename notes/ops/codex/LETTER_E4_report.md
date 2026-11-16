Đã hoàn thành theo brief `db0268e5`: code, training checks và pilot. **Không commit, không SSH, không sửa file có sẵn; chưa chạy truth seed `3000001`.**

Mã mới: [e4_geant.py](/home/vantai/state-model-regret/experiments/letter/e4_geant.py), [e4_rhat.py](/home/vantai/state-model-regret/experiments/letter/e4_rhat.py), [tests](/home/vantai/state-model-regret/tests/test_letter_e4.py).

**Kiểm chứng:** E4 **21/21 PASS**, EV-TE **29/29 PASS**. Regression GÉANT M0_new khớp bitwise với `pipeline_V` đã khóa. Merge/score mô tả chạy thành công; tính lại độc lập **468 hàng pilot** khớp raw.

```bash
python3 -m pytest -q tests/test_letter_e4.py --basetemp=/tmp/le4_pt -o cache_dir=/tmp/le4_cache
python3 -m pytest -q tests/test_ev_te.py --basetemp=/tmp/le4_ev_pt -o cache_dir=/tmp/le4_ev_cache
```

Training seed `1`, N=100/regime, K=128. Cả 17 regime đều có 2 actions nên best-action agreement và full-order agreement có cùng kết quả dưới đây.

| Regime | ii khớp i | iii khớp i | Tie fresh % | Tie stale % |
|---|:---:|:---:|---:|---:|
| G1_r80_b3_s1 | ✓ | ✓ | 51 | 0 |
| G1_r80_b6_s0 | ✓ | ✓ | 43 | 0 |
| G1_r80_b6_s1 | ✓ | ✓ | 41 | 0 |
| G2_r80_b3_s1 | ✗ | ✗ | 97 | 40,33 |
| G2_r80_b6_s0 | ✗ | ✗ | 47 | 0 |
| G2_r80_b6_s1 | ✓ | ✓ | 55 | 0 |
| G2_r90_b3_s0 | ✓ | ✗ | 47 | 0 |
| G2_r90_b3_s1 | ✓ | ✓ | 47 | 0 |
| G2_r90_b6_s0 | ✓ | ✗ | 24 | 0 |
| G2_r90_b6_s1 | ✓ | ✓ | 13 | 0 |
| G3_r80_b3_s1 | ✗ | ✗ | 97 | 16,67 |
| G3_r80_b6_s0 | ✓ | ✗ | 45 | 0 |
| G3_r80_b6_s1 | ✓ | ✓ | 53 | 0 |
| G3_r90_b3_s0 | ✓ | ✗ | 50 | 0 |
| G3_r90_b3_s1 | ✓ | ✓ | 42 | 0 |
| G3_r90_b6_s0 | ✓ | ✗ | 10 | 0 |
| G3_r90_b6_s1 | ✓ | ✓ | 19 | 0 |

Gaussian ii đạt **14/17 = 82,35%**; ordering-only iii đạt **9/17 = 52,94%**. Mức **90% dự kiến cho E4-3 chưa đạt trong training**. Tie trung bình: fresh **45,94%**, stale **3,35%**; đây là tỷ lệ mô tả, không phải các thử nghiệm độc lập.

Pilot seed `7000001`, mỗi chunk N=50/K=128/R_eval=256/R_dec=128:

| Regime chọn theo CPU EV-TE | CPU/chunk |
|---|---:|
| Rẻ nhất: G3_r80_b3_s1 | 11,968 s |
| Đắt nhất: G2_r90_b6_s1 | 370,887 s |

Dự phóng **170 chunks ≈ 12.160 CPU-s = 3,378 CPU-h**, khoảng nhạy **2,924–3,831 CPU-h**, hiệu chỉnh theo CPU EV-TE của đủ 17 regime. Đây là ước tính từ local, chưa phải phép đo GCP.

Lệnh đã chạy:

```bash
python3 -m experiments.letter.e4_geant train-checks
python3 -m experiments.letter.e4_geant run --workers 4 --chunks 0 --regimes G3_r80_b3_s1 G2_r90_b6_s1 --pilot --out /tmp/e4_pilot
python3 -m experiments.letter.e4_geant merge --out /tmp/e4_pilot
python3 -m experiments.letter.e4_geant score --out /tmp/e4_pilot
```

Lệnh GCP sau khi Claude viết card và khóa inputs, với onset tắt:

```bash
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m experiments.letter.e4_geant run --workers 32 --chunks all --card results/letter/e4/CARD_E4.json
```

Card còn cần chốt cách gộp các horizon `h ≥ 7·T_int`; onset-hybrid đang tắt. NPZ tái tạo cùng byte; JSON CPU/wall chứa thời gian đo thực nên thay đổi giữa các lần chạy.

Kết quả lưu tại [báo cáo đầy đủ](/home/vantai/state-model-regret/results/letter/e4/REPORT.md), [training JSON](/home/vantai/state-model-regret/results/letter/e4/training_checks.json), [CSV](/home/vantai/state-model-regret/results/letter/e4/training_summary.csv), [pilot summary](/home/vantai/state-model-regret/results/letter/e4/pilot/run_summary.json), [pilot log](/home/vantai/state-model-regret/results/letter/e4/audit/pilot.log) và [card format](/home/vantai/state-model-regret/results/letter/e4/card_format.json). Raw pilot có bản sao tại `results/letter/e4/pilot/raw/`. Chưa tạo card/lock truth hoặc biểu đồ.