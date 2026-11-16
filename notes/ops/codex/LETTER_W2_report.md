Đã hoàn thành W2 đến local smoke. Chỉ tạo 4 module mới và [tests/test_letter_w2.py](/home/vantai/state-model-regret/tests/test_letter_w2.py); giữ nguyên W1b, không commit hoặc SSH.

- Source: [mmpp.py](/home/vantai/state-model-regret/experiments/letter/mmpp.py), [shat2.py](/home/vantai/state-model-regret/experiments/letter/shat2.py), [w2_eval.py](/home/vantai/state-model-regret/experiments/letter/w2_eval.py), [w2_run.py](/home/vantai/state-model-regret/experiments/letter/w2_run.py).
- **21 tests PASS, 8,10 s**. Lỗi padding FFT phát hiện ban đầu đã sửa. Scorer và xuất EPS/PDF được kiểm bằng fixture.
- Smoke đúng **2 regimes**, `--workers 4`:

| Regime asym | CPU-s | Sai số tương đối ŝ |
|---|---:|---:|
| κ = 0,05 | 9,355 | 30,77% |
| κ = 0,5 | 9,256 | 34,71% |

ŝ đúng dấu **2/2**; bound thỏa **14/14 rows** trong tolerance số học `1e-9`. Resume bỏ qua cả hai file, SHA256 giữ nguyên.

Ngoại suy tuyến tính: **865,39 CPU-s ≈ 0,2404 CPU-h cho 93 regimes**. Hai regimes đầu chưa đại diện các trường hợp lớn; đây không phải bảo đảm runtime.

Các lệnh local đã chạy:

```bash
python3 -m pytest -q tests/test_letter_w2.py --basetemp=/tmp/lw2_pt -o cache_dir=/tmp/lw2_cache
python3 -m experiments.letter.w2_run run --workers 4 --families asym --limit 2 --out /tmp/w2_smoke/
```

Raw JSON ở [/tmp/w2_smoke/](/tmp/w2_smoke/); [log tests](/tmp/letter_w2_pytest_final.log), [log smoke](/tmp/letter_w2_smoke.log), [verification JSON](/tmp/letter_w2_verification.json). Chưa chạy toàn bộ 93 regimes, chấm P13–P20 hoặc tạo hình E1 thực tế đủ ba regimes.

Card còn mơ hồ về `κ_guess`, cách gộp fresh/stale khi chọn θ, mẫu số P20 và state E1. Các quy ước đã ghi trong `w2_run.py`: θ riêng từng ŝ và gộp hai phía; disagreement dùng joint Markov law thật; P19 hiểu slope theo giới hạn tiệm cận.

Lệnh GCP chính xác, **chưa thực thi**:

```bash
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
python3 -m experiments.letter.w2_run run --workers 4 --families asym,zf_a3_asym,zf_a7p5_asym --out results/letter/w2/raw
python3 -m experiments.letter.w2_run analyze
python3 -m experiments.letter.w2_run figure_e1
```