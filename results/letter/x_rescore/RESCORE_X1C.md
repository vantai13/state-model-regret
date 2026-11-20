**X1c: MATCH.** Chấm lại độc lập từ saved raw cost và predictions; 7/7 test T1–T6b STANDS, khớp card và row X_CTMC_C trong ledger.

Người phụ trách: **Doan Van Tai**. Thực hiện theo brief tại commit f63d9fb của letter_smr. Tái dùng script độc lập có sẵn, chỉ đổi đường dẫn trong bộ nhớ. Không sửa script, scorer, raw, card hoặc ledger; không commit. Không import/gọi module chấm hoặc engine, không chạy lại truth.

Đối chiếu cuối: **18575/18575 MATCH, 0 MISMATCH**. Tolerance chỉ để so serialization/roundoff: relative 1e-12, absolute 1e-9; các ngưỡng khoa học dùng nguyên bất đẳng thức trong thẻ.

| Nhóm đối chiếu | MATCH | MISMATCH |
|---|---:|---:|
| CTMC.card | 87 | 0 |
| CTMC.raw | 18361 | 0 |
| CTMC.receipt | 4 | 0 |
| integrity | 47 | 0 |
| ledger.X_CTMC_C | 72 | 0 |
| sanity | 4 | 0 |

63/63 raw file khớp SHA256 receipt; 23/23 mục lock/card khớp SHA256 và committed Git blobs. 15/15 analytic controls PASS; 23760/23760 kiểm phụ công thức saved forecast PASS. Kiểm lại 92 input hash trước khi ghi: nguyên byte.

Research HEAD: 5c30c8d680f25a13a49332b1878f0fa672cb0c4c. Script gốc SHA256: 741d424e10eba32caee8faa4728177309b61f9059b5679eed67b9c51fe2e3259. Provenance, từng trường trước/sau, cell membership và seed nằm trong JSON.

Thiết kế có 64 regime; 63 regime truth COMPLETED. Pilot loại theo predictions.json: XCTMC_009, XCTMC_037, XCTMC_050, XCTMC_062. Trong đó XCTMC_062 không có raw truth, nên loại 3 raw pilot còn **60 regime**; 51 estimator VALID, 9 INVALID. Tổng 6.300 dòng: 6.120 COMPLETED và 180 INVALID_ESTIMATOR. Regime INVALID vẫn giữ trong mẫu, các ô thiếu operational prediction không vào test cần prediction đó.

Seeds grid/train/test/pilot = 2611301/2611302/2611303/2611304. h = 1, 3, 10, 30, 100 T_int; tau = 1, 3 T_int; 2.000 paired histories. Test dấu/độ dốc dùng h = 30/100, |DeltaF_hat| >= 0,01, |G_S| >= 0,25% C_ref, prediction có dấu khác 0, loại pilot. T5 dùng riêng Hybrid_hat có sign(s_hat) = sign(s), theo thẻ.

| Test | Tính lại | Đã báo | Ngưỡng | Verdict |
|---|---|---|---|---|
| T1 | 633/635 = 99.685039% | 633/635 | >=90%; >=20 ô, >=8 regime | STANDS |
| T2 disagree | law 325/327 = 99.388379%; null 158/327 = 48.318043% | Cùng số đếm/tỉ lệ | gap >=20 điểm phần trăm | STANDS |
| T3 | median relative error 12.055637%, 315 ô | 12.055637% | <=25% | STANDS |
| T4 M0 | 185/185 = 100% | 185/185 | >=90% | STANDS |
| T5 Hybrid_hat | 204/204 = 100% | 204/204 | >=90% ô có both-side regret <=0,5% C_ref | STANDS |
| T6 C5 | 183/185 = 98.918919% | 183/185 | >=85% | STANDS |
| T6b concentration | 179/185 = 96.756757% | 179/185 | >=80% | STANDS |

T1: 44 regime, 44/44 đa số đúng; agree 308/308, disagree 325/327. Law hơn null 51.070336 điểm phần trăm ở disagree. T4: 49 regime, 49/49 đa số đúng. T5 không có ô sai dấu s_hat/s trong quần thể Hybrid đủ điều kiện.

**Phân biệt độ dài bản ghi.** Khi chỉ thay thư mục, adapter cũ cho record_T_int=100, còn ledger=1000. Đây là khác nghĩa của metadata: adapter cũ lấy W/T_int của paired history, ledger X1c dùng W2 của estimator. design_snapshot.md và telemetry A/B của cả 63 planned regime xác nhận estimator W/T_int=1000; paired history vẫn 100. Đối chiếu cuối lấy record_T_int từ telemetry estimator, lưu history_record_T_int=100 riêng. JSON giữ nguyên sai lệch tạm 100 so với 1000 và nguyên nhân; không thay phép chấm T1–T6b.

D1 dùng G_S < -0,5% C_ref ở h=30 T_int, tau=T_int; không áp lại bộ lọc eligibility của T1.

| Rule | Harm / regime | Median G_S (% C_ref) |
|---|---:|---:|
| M0 | 46/60 | -3.867634511 |
| MLU | 32/60 | -1.192678024 |
| TH_0.5 | 30/60 | -0.506916973 |
| TH_0.65 | 27/60 | 0.000000000 |
| TH_0.8 | 17/60 | 0.000000000 |
| TH_0.9 | 3/60 | 0.000000000 |
| Hybrid_hat | 0/51 | 0.000000000 |
| Stationary_hat | 0/51 | 0.000000000 |

D4: Hybrid_hat trừ Stationary_hat trên cùng regime/tau/h/side, ngưỡng 0,05 điểm phần trăm C_ref; 102 cặp cho mỗi h và mỗi side, tổng 612 phép so sánh.

| h/T_int | Fresh: tốt hơn / trong ngưỡng / tệ hơn | Stale: tốt hơn / trong ngưỡng / tệ hơn |
|---:|---|---|
| 1 | 40 / 62 / 0 | 5 / 97 / 0 |
| 3 | 16 / 86 / 0 | 4 / 98 / 0 |
| 10 | 6 / 96 / 0 | 2 / 100 / 0 |

Hybrid tệ hơn >0,05 điểm phần trăm: 0/612; lợi lớn nhất 4.939452776 điểm phần trăm. D2 median max(tie_share_fresh, tie_share_stale) của M0 là 12.487957%; các rule còn lại 0. D2 và D3 cũng khớp card.

**Các ô không đúng và phân tích saved data.** T1 sai tại MLU/XCTMC_056 (h=30,tau=3: dự đoán âm, G_S=+0,328202567% C_ref) và MLU/XCTMC_061 (h=30,tau=1: dự đoán dương, G_S=-0,256949209% C_ref). DeltaF_hat là 0,0315 và 0,1035, còn |DeltaF_exact| xấp xỉ 5,55e-17 ở cả hai. Độ lớn DeltaF_exact ở mức roundoff, không dùng dấu của nó như bằng chứng. Sai lệch này phù hợp với sampled-share error cùng thành phần finite horizon; chưa tách riêng đầy đủ hai nguyên nhân.

C5 sai 2 ô tại XCTMC_048/M0, tau=1, h=30/100: c5_sign dự đoán dương, G_S lần lượt -0,438871673% và -0,372799317% C_ref. pooled_switch=False, long_run_switch=True. Vì vậy C5 không đúng trên từng ô, dù T6 vượt ngưỡng 85%; không nâng thành định luật không ngoại lệ.

Phân tách độ dốc bằng saved truth, chỉ mô tả sau chạy: median relative error của locked forecast 12.055637%; thay s_hat bằng s thật 3.647586%; chỉ thay sampled share bằng exact share 11.132300%; dùng cả s thật và exact share 0.973929%. Các thay thế này dùng truth, không phải predictor mới hay một lượt xác nhận độc lập. Không chạy cải thiện hoặc đổi ngưỡng.

Forecast F1 đúng khoảng (12,0556% trong 10–20%); F2 đúng verdict nhưng accuracy 99,6850% ngoài khoảng dự báo 93–97%; F3 đúng cả năm verdict; F4 sai khoảng (9 INVALID, dự báo 10–20/63).

Sai khác số học tối đa giữa các trường đối chiếu cuối: 9.31322575e-10 (nhiều đơn vị khác nhau, chỉ để theo dõi roundoff). T3 tính từ (L_stale-L_fresh)/h = 0,12055636687609009, đã báo 0,1205563668760907. Nhãn float h/tau được ánh xạ về lưới design; JSON lưu các nhãn và số dòng bị roundoff. Không dùng tolerance so sánh để nới eligibility.

Kiểm phụ đầu dừng TypeError do nhân s_hat=None ở estimator INVALID; lượt kiểm tiếp giả định nhầm sign không khả dụng là 0. JSON thực tế lưu null. Kiểm cuối xác minh slope_pred/sign_pred đều null ở 720 dòng tương ứng. Hai lỗi thuộc helper kiểm phụ, không thuộc scorer hoặc verdict; không có truth run hay input nào bị sửa.

Các ô chung regime không độc lập; không tính population CI. Kết quả xác nhận phép tổng hợp của saved outputs và đối chiếu card/ledger, chưa xác nhận engine truth bằng một implementation độc lập hoặc loại mọi shared numerical bias.

Lệnh đã chạy: source môi trường, python -B với heredoc để tái dùng script trong bộ nhớ, chấm lại và kiểm phụ. Có thể chạy lại phần core hoàn toàn chỉ đọc bằng đúng lệnh sau; code adapter nằm trong JSON:

```bash
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
python -B - <<'PY'
import json
from pathlib import Path
r = json.loads(Path('results/letter/x_rescore/rescore_x1c.json').read_bytes())
exec(compile(r['reproduction']['python'], '<X1c-rescore-replay>', 'exec'))
PY
```

Lượt core in số so sánh trước 4 kiểm consistency bổ sung; JSON cuối lưu toàn bộ so sánh. Các guard cấm import project scorer và giới hạn ghi đúng hai output của brief.

- JSON số liệu/provenance/đối chiếu: results/letter/x_rescore/rescore_x1c.json.
- Báo cáo tiếng Việt: results/letter/x_rescore/RESCORE_X1C.md.
- Script tái dùng, nguyên byte: experiments/letter/x_rescore_independent.py.
- Raw/receipt/card/predictions/lock: results/letter/x_ctmc_c/; row đối chiếu: letter_smr_argon/ledger/numbers.json, X_CTMC_C.
- Không tạo log riêng, CSV, biểu đồ, cấu hình hoặc source mới. Không sửa file x4b của job song song.
