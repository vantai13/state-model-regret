Đã sửa [ev_te_trace.py](/home/vantai/state-model-regret/experiments/ext_validity/ev_te_trace.py:29), thêm test Arm R trong [test_ev_te.py](/home/vantai/state-model-regret/tests/test_ev_te.py) và chạy `train → run → summary` trên local với **1 worker**. Không commit, không SSH.

Parser ghi nhận:

| Đại lượng | Số lượng |
|---|---:|
| File TM | 48.096 |
| OD vắng được điền 0 trong bin giữ lại | 196.870 |
| Bin node outage | 6.412 |
| Bin vắng file | 7.776 |
| Bin hợp lệ | 41.684 |
| File malformed khác | 0 |

Tổng OD vắng kể cả các file outage bị loại: **332.697**.

Train giữ nguyên hai tháng lịch **03–04/2004**, có **3.742/17.568 bin hợp lệ**. Managed OD1 = `LOSAng_CHINng`; OD2 = `WASHng_IPLSng`.

| ρ | \(T_{int}\), phút | Thời gian backlogged train | Thời gian backlogged test |
|---|---:|---:|---:|
| 0.8 | 283.733818 | 33.4467% | 48.5382% |
| 0.9 | 438.891424 | 66.2775% | 55.1819% |

Bảng đủ 80 ô dưới đây gộp theo horizon. **Đơn vị \(G_S±SE\) là \(10^{-3}\%\ E_{stay}\)**: chẳng hạn `0.355` tương ứng `0.000355% E_stay`. Mỗi ô có **n = 37.717**, trên **132 ngày**; SE tính từ daily paired means. R1 = `{OD1}`, R4 = `{OD1, OD2}`; τ và h tính bằng phút.

| ρ | Set | h | h/Tint | P τ=5 | N τ=5 | P τ=10 | N τ=10 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0.8 | R1 | 5 | .01762 | .355±.061 | .038±.051 | .694±.121 | −.099±.053 |
| 0.8 | R1 | 10 | .03524 | .603±.107 | −.009±.104 | 1.237±.225 | −.311±.109 |
| 0.8 | R1 | 15 | .05287 | .802±.146 | −.134±.165 | 1.700±.317 | −.645±.177 |
| 0.8 | R1 | 30 | .10573 | 1.315±.246 | −.828±.397 | 2.838±.551 | −2.175±.473 |
| 0.8 | R1 | 60 | .21147 | 2.145±.419 | −3.493±1.180 | 4.535±.911 | −7.023±1.490 |
| 0.8 | R4 | 5 | .01762 | .375±.063 | .060±.052 | .735±.125 | .080±.080 |
| 0.8 | R4 | 10 | .03524 | .630±.110 | .028±.106 | 1.297±.232 | .051±.166 |
| 0.8 | R4 | 15 | .05287 | .835±.150 | −.076±.167 | 1.777±.327 | −.084±.264 |
| 0.8 | R4 | 30 | .10573 | 1.356±.252 | −.709±.399 | 2.943±.567 | −.959±.657 |
| 0.8 | R4 | 60 | .21147 | 2.180±.424 | −3.178±1.186 | 4.656±.930 | −4.284±1.861 |
| 0.9 | R1 | 5 | .01139 | .222±.041 | .068±.037 | .427±.083 | −.008±.042 |
| 0.9 | R1 | 10 | .02278 | .363±.071 | .065±.072 | .744±.152 | −.092±.085 |
| 0.9 | R1 | 15 | .03418 | .478±.096 | .030±.111 | 1.011±.212 | −.235±.130 |
| 0.9 | R1 | 30 | .06835 | .772±.162 | −.216±.246 | 1.676±.369 | −.920±.307 |
| 0.9 | R1 | 60 | .13671 | 1.253±.277 | −1.314±.671 | 2.695±.615 | −3.169±.897 |
| 0.9 | R4 | 5 | .01139 | .241±.043 | .082±.037 | .467±.086 | .017±.042 |
| 0.9 | R4 | 10 | .02278 | .386±.073 | .086±.073 | .797±.156 | −.055±.085 |
| 0.9 | R4 | 15 | .03418 | .503±.099 | .058±.112 | 1.074±.217 | −.180±.129 |
| 0.9 | R4 | 30 | .06835 | .809±.165 | −.153±.248 | 1.766±.378 | −.811±.304 |
| 0.9 | R4 | 60 | .13671 | 1.293±.280 | −1.206±.673 | 2.805±.627 | −2.939±.895 |

Các command đã chạy trong môi trường brief:

```bash
python3 -m experiments.ext_validity.ev_te_trace train
python3 -m experiments.ext_validity.ev_te_trace run
python3 -m experiments.ext_validity.ev_te_trace summary
python3 -m pytest -q tests/test_ev_te.py tests/test_ext_packet.py tests/test_ev_d4c.py --basetemp=/tmp/evte_r2_pt -o cache_dir=/tmp/evte_r2_cache
python3 -m experiments.ext_validity.ev_te verify-lock
```

**85 tests PASS trong 9,70 giây**. Train/run/summary đều exit 0; đối chiếu độc lập khớp 80 ô summary và timestamp. SHA256 của **73 file được bảo vệ** không đổi, gồm toàn bộ 70 file khóa và lịch sử Arm R; `verify-lock` khớp cả dữ liệu ngoài repo.

Các điểm cần làm rõ: runner hiện không có `--workers`, nên dùng tuần tự; số điền 0 không tính outage bị loại. Tỷ lệ backlogged phía trên tích phân thời gian trong bin; tỷ lệ mẫu cuối bin được ghi riêng trong README. Queue được reset sau gap và coverage train còn hạn chế. Kết quả chỉ **descriptive**, không chấm verdict.

Output mới đều ở [arm_r_v2/](/home/vantai/state-model-regret/results/ext_validity/ev_te/arm_r_v2):

- [README đầy đủ](/home/vantai/state-model-regret/results/ext_validity/ev_te/arm_r_v2/README.md), gồm baseline \(E_{stay}\), đơn vị và giới hạn.
- [CSV số liệu](/home/vantai/state-model-regret/results/ext_validity/ev_te/arm_r_v2/summary_cells.csv), [raw NPZ](/home/vantai/state-model-regret/results/ext_validity/ev_te/arm_r_v2/raw).
- [Training/configuration](/home/vantai/state-model-regret/results/ext_validity/ev_te/arm_r_v2/train.json), [train log](/home/vantai/state-model-regret/results/ext_validity/ev_te/arm_r_v2/train.log), [test log](/home/vantai/state-model-regret/results/ext_validity/ev_te/arm_r_v2/tests.log), [verification](/home/vantai/state-model-regret/results/ext_validity/ev_te/arm_r_v2/verification.json).

Không tạo biểu đồ.