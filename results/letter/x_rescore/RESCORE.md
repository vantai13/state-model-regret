**Chấm lại độc lập X-CTMC và X-GÉANT — MATCH**

Người phụ trách: **Doan Van Tai**. Script độc lập thực hiện theo brief tại commit `9f27dee` của `letter_smr`.

Đối chiếu **18498/18498 trường MATCH**, **0 MISMATCH**. MATCH xác nhận việc tính lại khớp dữ liệu đã báo; không đồng nghĩa mọi hypothesis đứng.

SHA256 theo receipt khớp **63/63 JSON** và **87/87 NPZ**. Mọi input đều khớp blob đã commit. Không import/call module chấm, không đọc `score.json`, không chạy lại truth, không commit.

Quy ước: `G_S = L_stale − L_fresh`; âm là freshness gây hại. Không phát hiện khác biệt do quy ước dấu. Regret và G_S chuẩn hóa dùng % C_ref; chênh lệch D4 dùng điểm phần trăm (pp).

| Nhóm đối chiếu | Số trường | MISMATCH |
|---|---:|---:|
| CTMC.card | 87 | 0 |
| CTMC.raw | 17701 | 0 |
| GEANT.card | 490 | 0 |
| GEANT.posthoc_rolling | 17 | 0 |
| GEANT.raw | 87 | 0 |
| ledger.X_CTMC | 72 | 0 |
| ledger.X_GEANT | 24 | 0 |
| receipts_and_train_DeltaF | 20 | 0 |

Rescore không dùng RNG. Seed của dữ liệu nguồn CTMC: grid=2611201, train=2611202, test=2611203, pilot=2611204; truth GÉANT: 7412001. CTMC raw ghi test_rng unused vì tính deterministic; đây là replay số liệu đã lưu.

**X-CTMC**

| Test | Tính lại | Đã báo | Verdict tính lại / đã báo | So sánh |
|---|---:|---:|---|---|
| T1 | 558/618 = 0.902912621 | n=618; accuracy 0.902912621 | STANDS / STANDS | MATCH |
| T2 | law 234/257 = 0.910505837; null 116/257 = 0.451361868 | law 0.910505837; null 0.451361868; n=257 | STANDS / STANDS | MATCH |
| T3 | n=305; median relative error 0.267521666 | n=305; median relative error 0.267521666 | DOES_NOT_STAND / DOES_NOT_STAND | MATCH |
| T4 | 136/146 = 0.931506849 | n=146; accuracy 0.931506849 | STANDS / STANDS | MATCH |
| T5 | 146/148 = 0.986486486 | n=148; share 0.986486486 | STANDS / STANDS | MATCH |
| T6 | 146/146 = 1.000000000 | n=146; accuracy 1.000000000 | STANDS / STANDS | MATCH |
| T6b | 146/146 = 1.000000000 | n=146; share 1.000000000 | STANDS / STANDS | MATCH |

T1: 38 regime eligible, 34/38 đúng theo đa số nghiêm ngặt; agree 324/361; disagree 234/257. Đã loại 4 pilot (3 có raw, 1 NOT_RUN): còn 60 regime trong mô tả D1. T5 xét riêng dấu ŝ = dấu s ≠ 0, không áp bộ lọc ΔF của test dấu. 12 ô Hybrid_hat sai dấu có median both-side regret 4.171531233% C_ref.

| D1, h=30 T_int, τ=T_int | Harm / regime | Median G_S (% C_ref) |
|---|---:|---:|
| Hybrid_hat | 0/40 | 0 |
| Hybrid_true | 0/60 | 6.61498341e-15 |
| M0 | 42/60 | -3.98084869 |
| MLU | 31/60 | -1.4916298 |
| Pool | 0/60 | 0 |
| Stationary_hat | 0/40 | 0 |
| TH_0.5 | 32/60 | -1.09754282 |
| TH_0.65 | 30/60 | -0.757878588 |
| TH_0.8 | 19/60 | 0 |
| TH_0.9 | 5/60 | 0 |

D1 đối chiếu từng rule với card và sáu rule có mặt trong ledger. D4 đối chiếu Hybrid_hat − Stationary_hat trên cả fresh/stale, ngưỡng nghiêm ngặt ±0,05 pp:

| h/T_int | Phía | Số ô | Hybrid tốt hơn >0,05 pp | Hybrid tệ hơn >0,05 pp |
|---:|---|---:|---:|---:|
| 1 | fresh | 80 | 28 | 0 |
| 1 | stale | 80 | 8 | 0 |
| 3 | fresh | 80 | 18 | 0 |
| 3 | stale | 80 | 5 | 0 |
| 10 | fresh | 80 | 8 | 0 |
| 10 | stale | 80 | 2 | 0 |

D4: 480 ô, 0 ô tệ hơn ngưỡng; lợi lớn nhất 17.788896545 pp. Các trường D4 trong ledger đều được tính lại.

T3 DOES_NOT_STAND: phân rã post hoc trên đúng 305 ô cho median relative error `locked` 26.752167%; `true_s_hat_shares` 4.017383%; `estimated_s_exact_shares` 28.827976%; `identity` 1.066995%. Các phép thay một thành phần cho thấy sai số độ lớn của ŝ là thành phần đáng kể; đây là mô tả từ saved data, không sửa prediction hay verdict.

**X-GÉANT**

| Test | Tính lại từ NPZ | Đã báo | Verdict tính lại / đã báo |
|---|---|---|---|
| G1 | 0/36 ô gộp resolved; accuracy=null | 0/36; accuracy=null | NOT_EVALUABLE / NOT_EVALUABLE |
| G2 | G_S=0; median both-side regret 0% C_ref, n=102 | 0%; n=102 | STANDS / STANDS |
| G3 | Stationary ≤ min TH: 102/102 | 102/102 | STANDS / STANDS |

G1 gồm 3 regime × 3 rule × 2 τ × 2 h = 36 ô, mỗi ô có 8–9 ngày evaluable. SE = sample standard deviation của mean G_S từng ngày / √số ngày (ddof=1). 0/36 ô đạt vế 2·SE; 31/36 đạt vế 0,25% mean C_ref; phải đồng thời đạt cả hai. Dấu khớp 24/36 ô chưa resolved chỉ là mô tả. Ở mức bản ghi, 34/56 resolved đúng (0,607142857).

G_S trong NPZ bằng bitwise `costs_stale − costs_fresh` ở 178176 giá trị. Stationary G_S=0 được kiểm cả 87 bản ghi, mọi instance/τ và cả 4 horizon; median regret và G3 chỉ dùng 102 bộ (regime, ngày, τ, h) evaluable tại 4/6 h. Both-side regret = 100·max(mean cost_fresh − mean C_ref, mean cost_stale − mean C_ref)/mean C_ref.

**Post hoc TH_0,8 — train so với test evaluable**

ΔF_train tính lại bằng (switch_stale − switch_fresh)/denominator trong predictions.csv; ΔF_test tính từ decisions trong NPZ, lấy trung bình đều theo ngày evaluable. Bảng dưới chỉ gộp hai h khi các giá trị trùng nhau; JSON giữ đủ 12 ô và từng ngày.

| Regime | τ (s) | h (h) | Ngày train/test | ΔF_train | Mean ΔF_test | Dấu G_S quan sát / từ ΔF_test |
|---|---:|---|---|---:|---:|---|
| NEW1 | 300 | 4 | 14/8 | 0.111607143 | -0.050781250 | +1 / +1 |
| NEW1 | 300 | 6 | 14/9 | 0.111607143 | -0.045138889 | +1 / +1 |
| NEW1 | 900 | 4 | 14/8 | 0.111607143 | -0.050781250 | +1 / +1 |
| NEW1 | 900 | 6 | 14/9 | 0.111607143 | -0.045138889 | +1 / +1 |
| NEW2 | 300 | 4 | 14/8 | 0.049107143 | -0.023437500 | +1 / +1 |
| NEW2 | 300 | 6 | 14/9 | 0.049107143 | -0.020833333 | +1 / +1 |
| NEW2 | 900 | 4 | 14/8 | 0.078125000 | -0.023437500 | +1 / +1 |
| NEW2 | 900 | 6 | 14/9 | 0.078125000 | -0.020833333 | +1 / +1 |
| NEW3 | 300 | 4 | 14/8 | 0.095982143 | -0.050781250 | +1 / +1 |
| NEW3 | 300 | 6 | 14/9 | 0.095982143 | -0.045138889 | +1 / +1 |
| NEW3 | 900 | 4 | 14/8 | 0.095982143 | -0.050781250 | +1 / +1 |
| NEW3 | 900 | 6 | 14/9 | 0.095982143 | -0.045138889 | +1 / +1 |

Train ΔF nằm trong [0.049107143, 0.111607143], test evaluable trong [-0.050781250, -0.020833333]. Đảo dấu ở 12/12 ô; ŝ_train < 0 nên thay ΔF_train bằng ΔF_test cũng đảo dự đoán dấu. Đây là bằng chứng về thay đổi share giữa các cửa sổ dữ liệu đã xét; không đủ để quy nguyên nhân cho mùa hoặc xác nhận luật dấu trên population, vì G1 vẫn NOT_EVALUABLE.

Phải tách horizon khi đọc khoảng ΔF_test: h=4 h: [-0.050781250, -0.023437500]; h=6 h: [-0.045138889, -0.020833333]. Khác biệt do tập ngày evaluable có 8 ngày ở 4 h và 9 ngày ở 6 h; khoảng xấp xỉ −0,045…−0,02 chỉ mô tả phần 6 h, không bao hết cả hai horizon.

Kiểm tra phụ post hoc K=5 cũng khớp summary/ledger: dấu gộp train 24/36, rolling 34/36, same-period oracle 36/36; record-level tương ứng 34/56, 28/50, 38/56. Không dùng các số này thay G1 khóa trước truth.

**Sai khác và giới hạn**

Không có MISMATCH số liệu hoặc verdict. Sai khác floating point nhỏ, nếu có, nằm trong tolerance đối chiếu (relative 1e−12, absolute 1e−9); JSON lưu absolute_difference. Các ngưỡng khoa học giữ nguyên, không dùng epsilon khi quyết định eligibility/resolution/verdict.

Sai khác tuyệt đối lớn nhất giữa hai cách tính là 4.65661287e-10 (các trường có đơn vị khác nhau; đây chỉ là kiểm tra roundoff). Ví dụ median T3 tính lại bằng (L_stale−L_fresh)/h là 0.26752166557233736, đã báo 0.2675216655723372. JSON giữ mọi giá trị trước/sau và absolute_difference, kể cả các trường MATCH.

Các ô chia sẻ regime/ngày và CRN nên không phải các trial độc lập; không tạo population CI. Việc chấm lại xác nhận saved outputs và phép tổng hợp; không phải một truth run độc lập hoặc chứng chỉ loại mọi bias của engine. X4 0/8352 được đối chiếu từ decision-only signal.json; không chạy lại X4. Không mở X1c hay dữ liệu ngoài hai thí nghiệm trong brief.

Nhãn h/T_int và τ/T_int được ánh xạ về đúng lưới design để xử lý roundoff của phép chia (ví dụ 29.999999999999996 → 30); JSON lưu nhãn trước/sau và số dòng. Đây là nhận diện tọa độ, không nới ngưỡng khoa học.

Trong lúc kiểm tra script mới đã sửa hai lỗi: đường dẫn repo paper ban đầu thiếu `state-model-regret-papers` (dừng trước đọc dữ liệu), và so sánh trực tiếp nhãn horizon float (bản chạy tạm bỏ sót ô). Kết quả cuối được tính lại từ input nguyên byte sau khi sửa; không phải sửa scorer/ledger đã có hoặc chạy lại truth.

Kiểm tra phụ về lặp byte: lượt audit đầu có assertion không khớp hash output; không lưu diff của lượt đó nên chưa xác định nguyên nhân. Hai kiểm tra tiếp theo (chạy ở tiến trình riêng và chạy dưới guard import/ghi file) khớp byte. Kết luận MATCH dựa trên từng trường và tolerance đã nêu, không phải tuyên bố mọi môi trường hoặc mọi lượt chạy luôn trùng byte.

**Lệnh và output**

```bash
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
python -B experiments/letter/x_rescore_independent.py
```

Embedded analytic controls: 15/15 PASS. Script kiểm SHA256 và committed blobs trước khi đọc số liệu; toàn bộ so sánh card/ledger theo từng trường và cell membership nằm trong JSON.

- Script: `experiments/letter/x_rescore_independent.py`.
- Số liệu, provenance và đối chiếu: `results/letter/x_rescore/rescore_independent.json`.
- Báo cáo: `results/letter/x_rescore/RESCORE.md`.
- Không tạo log, CSV, biểu đồ hoặc cấu hình mới. Không sửa file đầu vào.
