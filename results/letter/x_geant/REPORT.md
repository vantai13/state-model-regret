# X-GÉANT — chuẩn bị hoàn tất; không chạy truth hoặc score

Người phụ trách: **Doan Van Tai**. Ngày: 20/11/2026. AI triển khai theo brief đã được tác giả yêu cầu; không mentor review hoặc author-self attestation.

**X2: SIGNAL_OK. X4: NOT_ENOUGH_SIGNAL.** Đây là kết quả decisions-only, chưa xác nhận harm, regret, chất lượng correction hay độ chính xác dấu trên truth.

## 1. Phạm vi và cấu hình

Chỉ tạo `experiments/letter/x_geant.py`, `tests/test_x_geant.py` và `results/letter/x_geant/`. Không sửa source, test, card hoặc dữ liệu có sẵn; không ssh, không tạo commit, không chạy CLI truth/score, không mở file X-CTMC.

Brief `DESIGN_X_GEANT.md` khớp byte với commit **581e769** của letter_smr; SHA256 `f48112dc1b277bc1116648f337aa2cec432abf1c0737d3bab5afded4447e6e1b`.

Capacity **12544.525173885328 Mbit/s**; 26 train weekday 05/05–14/06/2005; window 10:15–16:15; beta=.3, flip rate=1/s, dt=.05 s, c=0, fluid per-link/infinite buffers. N=32, K=64, R_dec=64, R_eval=128; tau=300/900 s, h=1/2/4/6 h.

CLI đã có: configure, step0, pilot, predict, lock, verify-lock, truth --workers N, score. Các helper/kernel V7-3 được import nguyên byte. Forecast chỉ bỏ phần đuôi nếu endpoint của helper cũ cho queue=0, mode=0 chính xác và toàn bộ mean-load tương lai không vượt capacity; các trường hợp khác gọi nguyên helper đầy đủ. Kiểm tra so với helper gốc/saved V7-3 đều bit-identical trong regression đã chạy.

Các diễn giải đã ghi trong protocol trước test-day:

- Giữ base seed test/train/pilot **7412001/7402001/7472001** theo brief. Test/pilot base đã có ở V7-4, trái với câu yêu cầu mọi base đều mới; mỗi stream thực tế dùng namespace `X-GEANT|regime|date` để tách với V7-4. Không tuyên bố các base số là chưa từng dùng.
- Giữ công thức TH ở §4. Câu theta>=1 không Switch ở §9 đúng khi max-util Stay<=1; instantaneous overload có phản ví dụ. Có test cho cả tiền đề và phản ví dụ, không thêm sentinel theta ngoài công thức.
- G_S = L_stale - L_fresh theo letter Sec II/V7-3 và slope_pred ở §6. Cụm fresh-minus-stale trong §8 không nhất quán; không đảo dấu letter.
- Fresh và stale dùng cùng ma trận của decision slot, chỉ khác mode information; stale lấy mean endpoint modes của đúng K posterior samples, rồi max expected link load. Đây là giả định biết slot matrix chung, không phải chứng nhận mọi thành phần traffic thực tế đều được quan sát cùng tuổi.
- K hữu hạn không có empirical mean mode bằng 0 chính xác ở tuổi vô hạn. Analytic conditional expectation tiến về slot mean; test tuổi lớn kiểm tra kỳ vọng này, vẫn giữ sampling noise của K64 khi thực chạy.
- Các ngày test đã có exposure trong V7-3/V7-4; OD và stream mới không đồng nghĩa toàn bộ dữ liệu hoàn toàn unseen. Prediction ghi sau decisions-only, trước pilot và trước mọi truth.

## 2. Regime chỉ chọn từ train

Tiêu chí X2: bỏ DAY1/2/3 ODs; Stay qua link bận nhất toàn mạng, Switch là Yen second path tránh link đó; xếp giảm mean OD, rồi OD id. X4: bỏ OD cũ và X2; ratio max-util path Switch/Stay >=.75; ưu tiên bottleneck khác nhau, rồi giảm min(hai max-util), giảm mean OD, OD id. Chỉ dùng 26 weekday/window train. Không chọn theo queue, s_hat, decision hay outcome.

| Regime | OD | mean OD Mbit/s | max-util path Stay | max-util path Switch | ratio |
|---|---|---:|---:|---:|---:|
| NEW1 | hu1.hu_se1.se | 1416.340867910 | 0.900000000 | 0.610733502 | 0.678592780 |
| NEW2 | si1.si_se1.se | 966.639603383 | 0.900000000 | 0.323403980 | 0.359337756 |
| NEW3 | ny1.ny_de1.de | 398.709542857 | 0.900000000 | 0.170519868 | 0.189466520 |
| BOTH1 | de1.de_si1.si | 2890.912175079 | 0.614852003 | 0.710310838 | 1.155254979 |
| BOTH2 | cz1.cz_si1.si | 30.755355705 | 0.614852003 | 0.613185197 | 0.997289094 |
| BOTH3 | cz1.cz_at1.at | 0.026057165 | 0.614852003 | 0.610735579 | 0.993305016 |

Max-util là tổng traffic với managed OD được tính đúng một lần trên action path; không chỉ riêng volume managed flow. Các mức này là train mean, không phải bằng chứng cả hai path thực sự queue. Bảng từng directed link/action/peak: `train_utilizations.csv`.

- **NEW1** Stay: hu1.hu → at1.at → de1.de → se1.se; Switch: hu1.hu → at1.at → ny1.ny → uk1.uk → se1.se.
- **NEW2** Stay: si1.si → at1.at → de1.de → se1.se; Switch: si1.si → at1.at → ny1.ny → uk1.uk → se1.se.
- **NEW3** Stay: ny1.ny → at1.at → de1.de; Switch: ny1.ny → uk1.uk → fr1.fr → de1.de.
- **BOTH1** Stay: de1.de → at1.at → si1.si; Switch: de1.de → at1.at → hu1.hu → hr1.hr → si1.si.
- **BOTH2** Stay: cz1.cz → de1.de → at1.at → si1.si; Switch: cz1.cz → sk1.sk → hu1.hu → at1.at → si1.si.
- **BOTH3** Stay: cz1.cz → de1.de → at1.at; Switch: cz1.cz → sk1.sk → hu1.hu → at1.at.

## 3. Bước 0: số đếm nguyên

Đủ **156 train records** (84 S/72 O) và **174 test-S records**, tức 29 ngày S mỗi regime. **126 test-O records NOT_RUN**. Tổng 330 decisions records, không evaluation/C_ref/regret của test trong bước này.

X2: mỗi instance/tau đúng một comparison, không lặp bốn horizon. Train-all mẫu số 4992; train-S 2688; test-S 5568. Gate chỉ dùng test-S, pool ba regime/hai tau; ít nhất một TH đạt >=1%. MLU không mở gate.

| Rule | Train-all bất đồng/n | Train-S bất đồng/n | Test-S bất đồng/n | Test-S % |
|---|---:|---:|---:|---:|
| TH_0.5 | 2/4992 | 2/2688 | 501/5568 | 8.997844828 |
| TH_0.65 | 270/4992 | 244/2688 | 582/5568 | 10.452586207 |
| TH_0.8 | 1190/4992 | 831/2688 | 361/5568 | 6.483477011 |
| TH_0.9 | 1608/4992 | 777/2688 | 177/5568 | 3.178879310 |
| MLU | 2/4992 | 2/2688 | 443/5568 | 7.956178161 |

**X2 SIGNAL_OK**. TH .65/.8/.9 đều có 0 tie ở test-S trên cả ba phía và mọi h. TH .5 và MLU vẫn có tie, báo đủ ở bảng dưới.

X4: mỗi h pool ba regime và ba phía duy nhất (fresh tính một lần, stale300, stale900). Gate cần >=1% disagreement Hybrid/Stationary tại h<=2 h. Bảng tách phía/tau và mọi h giữ trong JSON/CSV.

| Population | h (giờ) | Hybrid/Stationary bất đồng/n | Fluid chặt về action có pooled rate lớn hơn/n |
|---|---:|---:|---:|
| train_all | 1 | 0/7488 | 377/7488 |
| train_all | 2 | 0/7488 | 377/7488 |
| train_all | 4 | 0/7488 | 377/7488 |
| train_all | 6 | 0/7488 | 377/7488 |
| train_S | 1 | 0/4032 | 287/4032 |
| train_S | 2 | 0/4032 | 287/4032 |
| train_S | 4 | 0/4032 | 287/4032 |
| train_S | 6 | 0/4032 | 287/4032 |
| test_S | 1 | 0/8352 | 0/8352 |
| test_S | 2 | 0/8352 | 0/8352 |
| test_S | 4 | 0/8352 | 0/8352 |
| test_S | 6 | 0/8352 | 0/8352 |

**X4 NOT_ENOUGH_SIGNAL**, do đó 87 bản ghi X4-S không vào truth. Không đổi regime, h, rho, K/R hoặc threshold để cứu gate.

Tie counts trên test-S tại h=1 h; mỗi ô có mẫu số 2784. Các h/population khác có đủ trong `step0_ties.csv`. TH: exact equality với threshold, hoặc path maxima bằng nhau khi threshold active; MLU: path maxima bằng nhau; M0/Hybrid: objective equality; Stationary: s_hat=0. Không dùng epsilon.

| Set | Rule | Fresh tie/n | Stale300 tie/n | Stale900 tie/n |
|---|---|---:|---:|---:|
| X2 | M0 | 2424/2784 | 7/2784 | 5/2784 |
| X2 | Hybrid | 0/2784 | 0/2784 | 0/2784 |
| X2 | Stationary | 0/2784 | 0/2784 | 0/2784 |
| X2 | TH_0.5 | 133/2784 | 26/2784 | 25/2784 |
| X2 | TH_0.65 | 0/2784 | 0/2784 | 0/2784 |
| X2 | TH_0.8 | 0/2784 | 0/2784 | 0/2784 |
| X2 | TH_0.9 | 0/2784 | 0/2784 | 0/2784 |
| X2 | MLU | 530/2784 | 464/2784 | 457/2784 |
| X4 | M0 | 2784/2784 | 2784/2784 | 2784/2784 |
| X4 | Hybrid | 0/2784 | 0/2784 | 0/2784 |
| X4 | Stationary | 0/2784 | 0/2784 | 0/2784 |
| X4 | TH_0.5 | 53/2784 | 66/2784 | 65/2784 |
| X4 | TH_0.65 | 41/2784 | 61/2784 | 64/2784 |
| X4 | TH_0.8 | 11/2784 | 0/2784 | 0/2784 |
| X4 | TH_0.9 | 0/2784 | 0/2784 | 0/2784 |
| X4 | MLU | 112/2784 | 90/2784 | 95/2784 |

Phân tích từ raw đã lưu: X4 M0 tie **2784/2784** trên mỗi phía, ở mọi h được xét. Khi fluid gap=0, dấu của corrected gap h*s_hat chính là dấu s_hat, nên Hybrid trùng Stationary. Trên train-S có fluid preference ngược pooled rate 287/4032, nhưng chưa đủ đảo correction tại h>=1 h (disagreement vẫn 0/4032). Đây là chẩn đoán quyết định, chưa phải kết luận về utility/harm. Không thêm thí nghiệm hoặc chỉnh thiết kế.

Các mẫu số dùng chung ngày, instance, phía/horizon; không phải independent trials.

CPU measured của 330 decisions records: **4606.577974232 s**; step0 command wall **1554.922160921 s** (gồm phần train-rate chạy 4 worker). Train-rate CPU riêng **1468.340222481 s**.

## 4. Prediction train-only

| Regime | pooled s_hat (Mbit) |
|---|---:|
| NEW1 | -834226.35895 |
| NEW2 | -832501.053629 |
| NEW3 | -84227.4306263 |
| BOTH1 | 12.1034549161 |
| BOTH2 | -0.557901830186 |
| BOTH3 | 4.64397623157e-05 |

Đã ghi **192 prediction rows** tại `predictions.json`/`.csv`: deltaF của ngày train-S, pooled s_hat từ đủ 26 ngày, slope_pred=s_hat*deltaF cho h=4/6 h. Null = chênh train-S mean path max-util nhân cùng deltaF, không dùng queue. Slope có đơn vị Mbit (dự báo G_S/h); chỉ dấu của nó dự báo dấu G_S. Zero là không dự báo dấu. Chưa so với truth.

## 5. Pilot và dự phóng

Pilot chọn **BOTH1, 19/07/2005** trước outcome bằng proxy sparse-link/OD step-work lớn nhất trong 174 S records; earliest regime/date khi tie. Đây là bản ghi nặng nhất theo proxy, chưa chứng minh nặng nhất theo CPU thực tế. Seed **7472001**, đủ N32/K64/R_dec64/R_eval128, tau và h nguyên brief. Pilot được phép riêng để đo chi phí dù X4 fail screen; không mở gate X4.

- Record CPU: **360.450706757 s**; wall **360.455776687 s**; peak process RSS **160.953125 MiB**.
- Dự phóng 87 eligible X2 records: **31359.211487859 CPU-s = 8.710892080 CPU-h**.
- Chia lý tưởng 30 worker n2-highcpu-32: **17.421784160 phút wall**.
- Giả định cả 174 S records (không được chạy vì gate X4): **17.421784160 CPU-h**, wall lý tưởng 34.843568320 phút ở 30 worker.

Đây là phép ngoại suy tuyến tính một record local; không phải đo GCP, upper bound, guarantee hoặc CI. Không dự phóng từ R/K rút gọn. Pilot outcomes là exposure trước truth, không được dùng chọn lại regime/threshold.

| Component | CPU-s | Wall-s |
|---|---:|---:|
| M0_fresh | 0.367137874 | 0.367151678 |
| M0_stale_300 | 22.077220480 | 22.077604350 |
| M0_stale_900 | 21.895540547 | 21.895960861 |
| paired_evaluation | 196.275595409 | 196.277392543 |
| posterior_300 | 2.898410338 | 2.898476470 |
| posterior_900 | 15.719381586 | 15.719592175 |
| reference_decision | 98.939649164 | 98.941724259 |
| warmup | 2.266592315 | 2.266715070 |

## 6. Test và kiểm chứng

- Tests mới: **30 PASS, 1.49 s**, gồm saved V7-3 decisions bit-identical cho cả ba pipeline, mọi h/phía; analytic stale limit; strict TH boundaries; CRN zero identity; isolation khỏi future evaluation; source/lock/no-overwrite guards; forecast certificate/fallback equivalence.
- Regression liên quan: **131 PASS, 258.56 s**, đã gồm 30 tests mới; 4 `PytestUnknownMarkWarning` ở marker slow của test cũ. Không cộng thành 161 tests khác nhau. Regression cũ có validation bằng synthetic/train/pilot cũ; không chạy X-GÉANT truth/score.
- Lượt triển khai đầu: 2 FAIL, 25 PASS, 1 SKIP do scalar NPZ shape (1,) không chuyển trực tiếp float ở NumPy hiện tại; đã sửa bằng .item() trước configure/scientific runs. Giữ `pytest_initial.log`; sau sửa 29 PASS/1 SKIP (.93 s), sau configure 30/30 PASS. Không thay engine hoặc tiêu chí.
- Independent vectorized decision audit: **1013760 actions + 1013760 tie flags**, 330 checksums/records, 156 rates/pooled estimates tái lập; 126 test-O đều không có output decisions; không future outcome arrays ở step0. PASS.
- Pilot raw integrity: đủ shapes `[32,64,2,4]` reference và `[32,128,2,4]` evaluation, streams distinct, CRN gathers/C_ref/G_S identities PASS; all floats finite. Không chấm hypothesis.
- Content lock **1014 files**, verify-lock PASS. SHA256 **4a3f91aa747801856dda5472fc0c1472b08339e7e0cd9f6f455badecde1200d1**. Lock chưa commit theo yêu cầu; không nhận đây là committed preregistration.
- HEAD của repo thay đổi ngoài lượt này từ 7dd868931 sang 7d54b39aa (commit library). Code/tests/results X-GÉANT vẫn untracked; tôi không thực thi git add/commit. Mọi locked dependency vẫn khớp; git diff tracked rỗng ở kiểm cuối.

Commands đã thực thi (môi trường đã source .venv/bin/activate và experiments/explore_ctmc/env.sh; PYTHONDONTWRITEBYTECODE=1, TMPDIR trong results/letter/x_geant/build):

```bash
python -m experiments.letter.x_geant configure
python -m experiments.letter.x_geant step0 --workers 4
python -m experiments.letter.x_geant predict
python -m experiments.letter.x_geant pilot
python -m experiments.letter.x_geant lock
python -m experiments.letter.x_geant verify-lock
python -m pytest -q -p no:cacheprovider tests/test_x_geant.py --basetemp=results/letter/x_geant/pytest_final
python -m pytest -q -p no:cacheprovider tests/test_x_geant.py tests/test_letter_v7_3.py tests/test_letter_v7_3_day.py tests/test_letter_v7_3_test.py tests/test_v7_4_short.py --basetemp=results/letter/x_geant/pytest_regression
```

Các audit là snippets NumPy/read-only trên artifacts đã lưu; chỉ ghi JSON audit trong folder được phép.

## 7. Artifact thực có

- Source: `experiments/letter/x_geant.py`; test: `tests/test_x_geant.py`.
- Cấu hình/trước test: `protocol.json`, `configuration.json`, `configuration.npz`, `regimes.md`, `train_utilizations.csv`, `candidate_ranking_inputs.csv`.
- Train raw: `training_rates/*.npz` và `*.json` (156 cặp), `training_summary.json`.
- Decisions: `inputs.json`, `step0_started.json`, `step0/train/` (156 cặp), `step0/test/` (174 cặp), `signal.json`, `step0_X2.csv`, `step0_X4.csv`, `step0_ties.csv`, `step0_by_record.csv`.
- Prediction: `predictions.json`, `predictions.csv`.
- Pilot: `pilot/selection.json`, `pilot/records/BOTH1_2005-07-19.npz`, `.json`, `pilot/summary.json`.
- Kiểm chứng: `decisions_audit.json`, `final_verification.json`, `lock.json`.
- Logs: `configure.log`, `step0.log`, `predict.log`, `pilot.log`, `lock.log`, `verify_lock.log`, `pytest_initial.log`, `pytest_fixed.log`, `pytest_final.log`, `pytest_regression.log`.
- Báo cáo: `REPORT.md` (file này). Không tạo biểu đồ. Không có folder truth, score.json hoặc score.csv X-GÉANT. Các test fixtures giữ riêng trong các folder pytest_* của lượt này.

## 8. Kết luận

Đã xác nhận bằng chạy thật: pipeline mới khớp quyết định V7-3, X2 có decision signal của các rule ngưỡng không tie, X4 không tách được Hybrid/Stationary trên panel/holds đã định; runtime/memory của một pilot full-size đã đo. Chưa xác nhận harm, độ chính xác sign law, lợi ích correction hoặc paired regret trên truth. Không chạy thêm để cứu X4. Gói code/inputs/prediction đã có content lock để Claude xem và thực hiện bước truth sau; independent truth rescore để lượt sau theo brief.
