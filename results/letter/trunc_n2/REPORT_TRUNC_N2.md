# TRUNC-N2 — kết quả chấm và chấm lại, 17/11/2026

Người phụ trách: **Doan Van Tai**.

## Kết luận theo card

Đủ **27/27 regimes α=7.5**, năm ages và mọi horizon đã lưu. So sánh chính
là **2N-VM với 1N-VM**, theo `DEVIATION_01.md`. Không loại regime hoặc đổi
field class/ngưỡng. Verdict chung **FAIL**, dù mọi đại lượng phần trăm đạt.

| Field class | Số leaves / schema fields | Ngưỡng | Max difference | Vi phạm | Verdict |
|---|---:|---:|---:|---:|---|
| (a) percentage-of-C_ref | 61,965 / 69 | 1e-6 pp | **7.7018285082886e-9 pp** | 0 | **PASS** |
| (b) cost, rate, T_int, bias và xác suất liên tục | 94,230 / 134 | relative ≤1e-9, không floor | infinity | 8,157 | **FAIL** |
| (c) discrete | 5,940 / 10 | giống hệt | 10 `margin_best.old` đổi | 10 | **FAIL** |

Arg-max class (a): `Za7p5_u3-2_lA31-4_x1-3_k1-20`, age `Tint_3`, h=8 s,
`[].h[].z_pred_first_order_inf_decisions`: **−2033.4645202669765 →
−2033.4645202746783 % C_ref**. Riêng G_S đo được: max **2.355403203968369e-9 pp**,
ở `Za7p5_u1-2_lA17-2_x-1_k2`, age `seconds_1`, h=222/5 s,
**0.0008164598976411646 → 0.0008164622530443686 % C_ref**.

## Phân tích failures trên dữ liệu đã lưu (POST-HOC)

Class (b) dùng đúng `abs(candidate-baseline)/abs(baseline)`. Có **1,061** failure
với baseline bằng 0. Arg-max infinity là share_new của `true_s_eps_+0.25`,
`Za7p5_u3-2_lA31-4_x1-3_k2`, age `seconds_1`, h=21200 s:
**0 → 2.258263464563715e-16**, absolute cũng là **2.258263464563715e-16**.
Không gán lại chúng sang class (a) hoặc thêm epsilon.

| Loại failure class (b) | Leaves | Max absolute difference | Đơn vị |
|---|---:|---:|---|
| Bias B_ko | 15 | 2.9994407668709755e-7 | packet·s |
| Stationarity residual | 245 | 3.3306690738754696e-16 | residual |
| Shares, tie mass, departure probability | 4,145 | 4.7937146918641815e-8 | probability mass |
| Hybrid excess cost | 3,752 | 2.0454172044992447e-7 | packet·s |

Không phải mọi failure đều do mẫu số gần 0. B_ko ở
`Za7p5_u3-2_lA31-4_x1-3_k2`, age `Tint_0.3`, đổi
**1.13953830889659 → 1.1395380089525133 packet·s**, relative
**2.6321543939802435e-7**, vượt ngưỡng. Các excess cost rất nhỏ được lấy bằng
hiệu hai cost lớn nên nhạy với cancellation. Ví dụ `mm1.excess_cost_old`,
`Za7p5_u3-2_lA31-4_x-1-6_k2`, age `Tint_1`, h=7090 s:
**−2.600136213004589e-7 → −5.547190085053444e-8 packet·s**, absolute
**2.0454172044992447e-7**, relative **0.7866577121110365**. Đây là diễn giải
numerical sensitivity từ saved values, không phải chứng minh sai số truncation
riêng rẽ với roundoff.

Max absolute trên *toàn bộ* class (b) là **9.830296039581299e-5 packet·s**, tại
`sign_flipped.excess_cost_old`, `Za7p5_u3-2_lA31-4_x1-3_k2`, age `Tint_3`,
h=63600 s: **10429689.89495437 → 10429689.894856067**. Relative ở điểm này
nhỏ hơn ngưỡng nên đây không phải max absolute của tập failures.

Cả 10 discrete changes đều là argmin `margin_best.old` ở age `Tint_3`, trong
ba regimes `Za7p5_u3-2_lA31-4_x1-3_k{2,1-2,1-20}`. Các coefficient được
chọn chuyển từ `1/200`, `1/100` hoặc `1/50` sang `1/20`. So regret của hai
coefficient cạnh tranh *trong từng raw* cho max **4.696937283554803e-14 pp**.
Điều này phù hợp argmin nhạy gần tie, nhưng **class (c) vẫn FAIL**. Không đổi
tie rule hay chạy lại engine. Chi tiết đủ 10 điểm ở `analysis_saved.json`.

Forecast cũ khoảng 1e-10 pp thấp hơn đo được khoảng 77 lần; forecast mọi
discrete field giống hệt là sai. Ngưỡng class (a) vẫn đạt. Không kết luận
toàn bộ truncation check PASS hoặc continuous/infinite-state exactness.

## So sánh phụ: 1N-VM với W1b local

| Class | Max difference | Failures | Verdict |
|---|---:|---:|---|
| (a) | 1.1440590697020525e-9 pp | 0 / 61,965 | PASS |
| (b) | infinity, có 6 zero-reference failures | 1,098 / 94,230 | FAIL |
| (c) | 0 | 0 / 5,940 | PASS |

Arg-max (a): `Za7p5_u3-2_lA31-4_x1-3_k2`, `Tint_3`, h=320 s,
`z_pred_first_order_inf_decisions`: −253.4475050763133 → −253.44750507516923.
Arg-max relative: `Za7p5_u1_lA8_x1-4_k2`, `seconds_1`, h=236 s,
`tie_mass.c11`: **0 → 5.436332506441729e-30**. Max absolute toàn class (b)
là **9.242445230484009e-6 packet·s** ở L00≈17,511,295.143; max absolute
trong failures là **4.0745362639427185e-7 packet·s** (B_ko). Đây là đo trên
toàn population; con số pilot ≤2.3e-12 trong deviation chỉ áp dụng pilot,
không áp dụng toàn population. Không nới reproduction tolerance.

## Thời gian, tài nguyên và provenance

| Run | Workers | Wall s | Task CPU s | Worker-process CPU s | Coordinator CPU s | Receipt peak RSS KiB |
|---|---:|---:|---:|---:|---:|---:|
| 1N-VM | 12 | 3827.084421672 | 16878.622001516 | 16879.061830 | 0.659736924 | 109364 |
| 2N-VM | 12 | 8212.177050613 | 34113.087596125 | 34113.796484 | 0.881037984 | 152116 |

RSS là peak được runner ghi, không phải tổng RSS đồng thời của 12 workers.
Hai run đều `RUN_EXIT rc=0`; `PIPELINE_EXIT rc=0`. Wall tổng hai receipt
**12039.261472285 s**, task CPU tổng **50991.709597641 s**. Không có seed
Monte Carlo mới: đây là CTMC deterministic numerical evaluation, dùng nguyên
levels và mọi saved ages/horizons của W1b. Môi trường BLAS lấy từ `env.sh`.

- Card `17498f7b2`; deviation/runner lock `b49b49538`, nguyên thresholds.
- Script replay chuẩn bị `81c9bf41a`; raw 1N `2bb6531cc`, raw 2N/logs
  **`91bee0fb0` đã push trước mọi compare**. Không chạy lại truth.
- Manifest kiểm lại **40/40 SHA MATCH**; raw/checksum retrieval do lượt trước
  ghi và commit. Run summary/input SHA được cả scorer và independent replay kiểm.
- VM xác nhận lại **TERMINATED**, shape `n2-custom-12-49152`,
  `vm_status_resume.json`. Không bật VM.

## Kiểm chứng và commands

`python3 -m experiments.letter.trunc_n2 compare --out results/letter/trunc_n2
--baseline results/letter/trunc_n2/raw_n1_vm --candidate results/letter/trunc_n2/raw_n2
--candidate-n-scale 2`: locked scientific verdict FAIL. `compare_run.log` giữ
stdout. Một lần gọi lặp gặp write-once `FileExistsError` trước tính toán;
giữ `primary_compare_run.log`, không ghi đè compare hoặc chạy lại raw.

`python3 -m experiments.letter.trunc_n2 compare --out results/letter/trunc_n2/platform_noise
--candidate results/letter/trunc_n2/raw_n1_vm --candidate-n-scale 1`: FAIL,
exit 2 theo locked verdict.

`python3 -m experiments.letter.trunc_n2_rescore`: replay đầu dừng ở relative
count vì chuỗi rational trong `evaluations[].parameters[]` bị phân loại là
relative thay vì discrete metadata. Sửa đúng nhánh schema này, giữ nguyên
locked primary scorer, classes và thresholds; log failed attempts còn nguyên.
Replay sau sửa **MATCH cả hai comparisons**, từng class, count, field schema,
max relative/absolute, số violations và verdict; **không import compare module**.
Field classes đã đối chiếu: 61,965 (a), 94,230 (b), 5,940 (c) cho mỗi phép so.

`python3 -m pytest -q tests/test_letter_trunc_n2.py tests/test_letter_trunc_n2_rescore.py`:
**32 PASS, 3.88 s** sau fix (31 PASS trước fix). Có regression cho rational
metadata và scientific rational horizon. `python3 -m experiments.letter.trunc_n2_analyze`
chỉ đọc saved raw, xuất breakdown; không đổi verdict hoặc sinh outcome mới.

## Output

- `compare.json`, `compare.md`; phụ `platform_noise/compare.json`, `compare.md`.
- `independent_rescore.json`, `independent_rescore_fixed.log`; log lỗi cũ giữ nguyên.
- `analysis_saved.json`, `analysis_by_field.csv`, `analysis_saved.log`;
  source `experiments/letter/trunc_n2_analyze.py`.
- `raw_n1_vm/`, `raw_n2/`, `gcp_run.log`, `manifest.sha256`,
  `manifest_resume_check.log`, `pytest_resume_r13_fixed.log`, `vm_status_resume.json`.

Letter phải báo max pp và thay đổi cost/near-tied margin selection theo
inclusion rule, không dùng câu mọi quantity hoặc discrete decision bất biến.
