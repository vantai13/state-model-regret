# AUDIT độc lập — external validity waves 1–3

Người phụ trách: **Doan Van Tai**. Ngày 14/11/2026; audit do AI thực hiện theo ủy quyền, không phải human review. Nhánh `ext/validity`; revision đầu phiên nằm trong `results/ext_validity/audit/input_manifest.json`. Không sửa source, CARD, lock, báo cáo cũ hoặc decision log; không commit, không truy cập outputs `ev_d4*`.

**Kết quả chính:** không phát hiện verdict đã lưu nào chấm sai. Có các lỗi diễn giải quan trọng về T12, nguyên nhân hybrid FAIL và tính đại diện của trace replay. Những lỗi này có thể đổi kết luận trong paper, dù bảng chấm theo CARD giữ nguyên.

## A. Tính lại verdict

Script độc lập `results/ext_validity/audit/recompute.py` chỉ dùng Python standard library, **không import scoring code hoặc engine**. Tính lại G từ chi phí/thành phần số gốc khi artifact có lưu; ghép prediction theo ID/h/twin, áp đúng dung sai, minimum-n và completion gate trong CARD. Với packet DES, JSON chỉ lưu thống kê tổng hợp: tính lại `100·G_S/E_stay`, nhưng phải sử dụng `se_pct` đã lưu; không có vector từng instant để tái ước lượng SE độc lập. EV-A2/EV-B chỉ có truth CSV, không có đủ từng cell để audit lại phép giải truth.

| Experiment | ID | Reported | Tính lại | Khớp? |
|---|---|---|---|---|
| EV-A | A1 | PASS 180/180 | PASS 180/180 | Có |
| EV-A | A2 | PASS 40/40 | PASS 40/40 | Có |
| EV-A2 | Z1 | FAIL 15/30 | FAIL 15/30 | Có |
| EV-B | B1 | PASS 30/30 | PASS 30/30 | Có |
| EV-B | B2 | PASS 10/10 | PASS 10/10 | Có |
| EV-B-rep q75 | R1 | PASS 30/30 | PASS 30/30 | Có |
| EV-B-rep q75 | R2 | PASS 14/14 | PASS 14/14 | Có |
| EV-B-rep q75 | R3 | FAIL, giữ harm 4/18 | FAIL, giữ harm 4/18 | Có |
| EV-B-rep q95 | R1 | PASS 30/30 | PASS 30/30 | Có |
| EV-B-rep q95 | R2 | PASS 7/7 | PASS 7/7 | Có |
| EV-B-rep q95 | R3 | PASS, giữ harm 0/18 | PASS, giữ harm 0/18 | Có |
| EV-D | D1 | Wave 1: PASS 116/120 | PASS 116/120 | Report khớp; thiếu score |
| EV-D | D2 | Wave 1: PASS 61/64 | PASS 61/64 | Report khớp; thiếu score |
| EV-D | D3 | Wave 1: PASS 120/120 | PASS 120/120 | Report khớp; thiếu score |
| EV-D | D4 | Wave 1: PASS 120/120 | PASS 120/120 | Report khớp; thiếu score |
| EV-D2 | D1 | PASS 40/40 | PASS 40/40 | Có |
| EV-D2 | D2 | NOT_EVALUABLE 0 | NOT_EVALUABLE 0 | Có |
| EV-D2 | D3 | PASS 40/40 | PASS 40/40 | Có |
| EV-D2 | D4 | PASS 40/40 | PASS 40/40 | Có |
| EV-D3a | D1 | PASS 78/80 | PASS 78/80 | Có |
| EV-D3a | D2 | PASS 54/56 | PASS 54/56 | Có |
| EV-D3a | D3 | FAIL 39/80 | FAIL 39/80 | Có |
| EV-D3a | D4 | FAIL 47/80 | FAIL 47/80 | Có |
| EV-D3b | D1 | FAIL 54/80 | FAIL 54/80 | Có |
| EV-D3b | D2 | PASS 66/68 | PASS 66/68 | Có |
| EV-D3b | D3 | FAIL 62/80 | FAIL 62/80 | Có |
| EV-D3b | D4 | FAIL 64/80 | FAIL 64/80 | Có |
| c_sw harm | S1 | FAIL 385/450 | FAIL 385/450 | Có |
| c_sw harm | S2 | PASS, luật gần hơn 288/288 | PASS 288/288 | Có |
| c_sw harm | S3 | NOT_EVALUABLE 0 | NOT_EVALUABLE 0 | Có |

**26/26 verdict có score khớp; 4/4 EV-D khớp report nhưng `ev_d/score.json` không tồn tại.** Hoàn tất 420/420 EV-A, 180/180 EV-D, 60/60 EV-D2, 80/80 mỗi EV-D3a/b. 9.070 kiểm tra arithmetic/metadata/prediction/control: **0 mismatch**. S2: median error luật **0,000322458 pp**, null **1,314794325 pp**. C_sw controls khớp, 6 MC units/12 checks đạt, max |z| **1,350061**; chỉ tính lại từ MC summaries, không chạy lại 40.000 episodes/unit.

**Lock:** 11 lock files, **63/65 entries khớp current files**. Hai mismatch đều là `experiments/ext_validity/packet.py`:

| Lock | SHA256 đã khóa | Phiên bản khôi phục được từ Git |
|---|---|---|
| EV-D | `3cac857c74737251dc12126de2524211fb0e6194be9a14fb3d669a51ebc8cd35` | `0abbd7f7` |
| EV-D2 | `1aa26bd71b6dad018ebabdcf0636b42aece424a5f8946a32216cb7678610552d` | `44b0284d` |

Current SHA là `8683410eec7c8d42bb6247aa56c50e2c7111cb7175565018a5bed9ba928e830a`. Diff chỉ thêm trace dispatch/calibration và τ per-case. Hai toy train/test default-τ so với source lịch sử khớp **bitwise** sau bỏ CPU/wall. Đây là source evolution có provenance; chưa có bằng chứng đổi verdict. Không coi lock hiện tại đã PASS toàn bộ, cũng không sửa lock cũ.

## B. Bugs và risks

Không tìm thấy **blocker về arithmetic của verdict hiện hành**. Các mục major dưới đây chặn cách diễn giải tương ứng trong paper.

| Mục | Severity | Evidence và reproducer | Ảnh hưởng |
|---|---|---|---|
| B1. Đồng nhất T12 với “plug-in không harm ở 30T” | **major** | `notes/theory/T12_plugin_stationarity.md:15–36`; `WAVE3_REPORT.md:35–39`. `audit/repro_checks.py::stationary_plugin_counterexample`: CTMC dừng, mixing, T_int=0,5 s; G=-0,216166 packet·s và **-1,441108% E_stay tại h=30T**, nhưng -0,144111% tại 300T. | **Đổi kết luận lý thuyết**: T12 cho O(1) tuyệt đối/o(h), không cho G≥0 hoặc ngưỡng 0,25%. D1 FAIL không tự bác T12; D1 PASS cũng không chứng minh theorem. Verdict giữ. |
| B2. Phép dẫn T12 thiếu điều kiện được viết rõ | **major** | T12:15–27 thay D bằng E[D\|Z_t] trong tích có action phụ thuộc quá khứ. Cần state đủ cho future costs khi biết history và remainder L1/uniform thích hợp. Toy iid trong cùng reproducer: G thực **0**, RHS ghi trong phép dẫn **-0,5** nếu Z thiếu memory. | Equality chưa được chứng minh cho hệ dừng tổng quát. **Không phải** phản ví dụ cho CTMC đầy đủ state của repo. Verdict không đổi. |
| B3. Trace replay không có “thang mixing chậm nhất” hữu hạn như report gợi ý | **major** | `trace_cox.py:85–101`: phase uniform một lần/path, modulo nguyên chu kỳ. Reproducer `periodic_phase`: covariance intensity tại kL bằng variance ở mọi k; relative phase A–B bất biến. Square-wave joint product time mean có thể **0 hoặc 2**, ensemble mean **1**. | Sampling nhiều instant trong một run không tích phân hết population của independent phases; train/test có thể giữ relative phase khác nhau. **Có thể ảnh hưởng mean, SE và kết luận tái lập**, chưa định lượng mức lật verdict. Cả hai trace chịu giới hạn này. |
| B4. “Hybrid FAIL không do ŝ” chưa được loại trừ | **major** | `WAVE3_REPORT.md:32`, DL-145; `ev_d3/diag_s_long.json`; reproducer/accounting `audit/exploratory.py`, mục `slope_diagnostic`. Median relative deviation **5,1029%**, max **147,6714%**; RB01: **9,69324 → 3,91375**, RN00: **-1,74725 → -3,15650**. | Median nhỏ không chứng minh causal attribution. Cần thay ŝ bằng reference độc lập trên **cùng histories**, tái tính actions/transient residual. **Có thể đổi giải thích và hybrid performance**, chưa chạy counterfactual, không thay verdict đã khóa. |
| B5. Alarm population khác true event-triggered epochs | **major** | `alarm.py:81–87` là stationary occupancy có điều kiện backlog cũ ≥ threshold; không mô phỏng first passage, crossing, hysteresis hay alarm retrigger. `repro_checks.py::alarm_population`: birth–death toy cho population {1,2}=(1/2,1/2), crossing=(1,0), signed outcome **+1 vs -1**. | Kết quả EV-B đúng với CARD, nhưng **không giải quyết K5 cho mọi event-triggered controller**. Population khác có thể đổi dấu; chưa tính cho panel hiện tại. |
| B6. SE và effective replication chưa được audit trọn | **major risk** | `packet.py:273–278,375–413`; train F/ŝ/OLS được coi cố định trong tolerances; output không lưu per-instant/batch vectors. H10/H30 dùng lại seed, hai twins cùng truth. Correlation fluid/ratefluid nowcast h30: **0,999617/0,999875** trên hai trace. | 120/124 không phải 124 phép thử độc lập hay “statistically significant effects”. SE trong run không bao trùm train uncertainty/phase uncertainty. **Khả năng đổi verdict dưới uncertainty đúng chưa biết**; không tự đổi công thức CARD. |
| B7. Current source không khớp hai lock lịch sử | **minor**, cần provenance khi tái lập | `audit/lock_checks.csv`, `packet_history.json`, `history_replay.py`. Các runner thường chỉ kiểm tồn tại lock, không verify toàn dependency/runtime hash. | Không phát hiện đổi verdict; replay cần checkout/source snapshot đúng lock. Toy bitwise không thay thế full-panel replay. |
| B8. A2 thiếu completion override | **minor**, latent bug | `ev_a_panel.py:131–134`: A1 xét completion, A2 không. `repro_checks.py::completion_gate`: 80/100 completed, 10/10 sign → implementation PASS, CARD INCONCLUSIVE. | Có thể lật A2 ở partial run; **không ảnh hưởng run này 420/420**. |
| B9. τ input validation chưa đủ | **minor**, latent bug | `packet.py:423–438`; `repro_checks.py::tau_validation`: nhận τ=-1, NaN, τ=50.000 khi train_T=20.000. | Có thể dùng future information/empty train ở input khác; **mọi scored case hiện hành có τ hợp lệ**. |

Các nghi vấn kỹ thuật đã kiểm và **không thấy lỗi** trong phạm vi chạy: `closed_loop.py:97–110` truyền τ dưới old action rồi Δ−τ dưới action mới; cost từ actuation đến actuation có cùng long-run mean với cách cộng hai đoạn tại observation epoch (**diff 8,88e−16**). Kronecker reference max error **2,36e−16**, stationary residual **1,84e−15**. Normalisation không che mass drift lớn trong toy. `zero_fit_first_order` sử dụng M0/g/π/posterior, không gọi truth V. Lindley so 100 scalar references: max **1,78e−15**; u=0 CRN futures và long-run khớp bitwise. Sign `G_S=(a_stale-a_fresh)·(C_switch-C_stay)` ở `packet.py:409` đúng. Test kiểm fluid/ratefluid gaps, saturated ties, OLS feature order, rate windows, C parser hash/binning và phase/intensity normalization đều đạt. Ratefluid shortcut hợp với mean-stable drift giảm/rise-then-drain đang dùng; chưa phải kiểm chứng mọi arrival model.

## C. Report-consistency errata

Inventory **108 mục** ở `audit/report_consistency.csv`: 86 khớp local artifacts; 3 errata, 6 overclaims, 1 proof gap, 3 thiếu scope, 6 chưa kiểm chứng và 3 chỉ có evidence hạn chế/local note. Không chuyển các mục chưa kiểm chứng thành PASS.

1. **Wave 1:13 / DL-143:** sign agreement cho toàn 240 rows Δ≤T là **181/240=75,4167%**, nên ghi số này thay “~80%”. Các median -0,86/-0,91 → +0,30/+0,39 đúng **trên diagonal Δ=h_p**. Nếu giữ h_p=10T, median tại Δ=T ở neg/pos vẫn **-0,0178/-0,0909%**; không nói toàn bộ Δ≤T đảo dấu.
2. **Wave 1:16:** 15/20 và KO≈12% dùng **neg+pos**, bỏ band nhưng chưa nói rõ. Toàn EV-B panel: M0 harm **18/30**, KO median regret **8,6812%**, so với **11,8322%** trên neg+pos. Hybrid có 0 harm ở cả hai cách lấy scope.
3. **Wave 1:68:** liệt kê EV-D có score nhưng file không tồn tại. Kết quả recomputed đúng; không tự bổ sung file cũ.
4. **Wave 2:14:** truth EV-D2 <0,25 pp đúng ở **h30** (max nowcast **0,13533 pp**), không đúng mọi h (h3 max **0,43660 pp**). `D2 NOT_EVALUABLE` vẫn đúng. T_int median **77,5071 s**, β₁ path A **0,994748** khớp cách làm tròn. Nhánh c25 train: T_int median **26,1043 phút**, backlog **7.138,36 packets**, khớp mô tả.
5. **Wave 2:37–41:** luật closed-loop không được xác nhận trên cả ba lớp packet/trace: các arm đó kiểm **one-shot train-estimated leading term**. “Decision times không bị chọn lọc” không phải điều kiện cần cho harm: q75 còn **4/18** harm. Đây là moderators, không phải ba điều kiện cần đã chứng minh.
6. **Wave 3:29–30 / DL-145:** 120/124 là đếm trên rows **được chọn bởi |prediction|≥0,25**, không phải significance test. “Độ lớn ±40–60%” không có denominator/coverage và không phải bound: trên h30 selected rows, median `|G−pred|/|pred|` là **42,3782%/19,2970%**, maxima **346,9182%/106,2549%** ở trace 1/2.
7. **Wave 3:32–39 / DL-145 / T12:** sửa diễn giải theo B1–B4. Minute-rate ratio trace 2 **0,6294–1,7723×** đúng; trace 1 cũng dao động, **0,6930–2,8611×**. Riêng range này không xác lập nguyên nhân khác biệt D1 giữa hai trace. Không suy nguyên nhân mixing từ một horizon.
8. **Provenance/giới hạn:** EV-D3b CARD giữ block copy của trace1/seed cũ rồi ghi override ở cuối; thresholds/actual cases đúng theo specifics, nhưng nên loại ambiguity ở bản trình bày tiếp theo. 16/30 decoupled approximation chỉ có rounded text log để kiểm, không raw full-precision. Các số 73/180 local +107 remote, VM quota/RAM, download54phút, pilot9/9, historical pytest902PASS+1FAIL chưa xác nhận độc lập từ scoped artifacts; `test.log` chỉ ghi 71 records. Literature metadata/bounds chỉ đối chiếu existing W2 note, **không primary-paper re-audit hoặc literature search mới**. Official MAWI count chỉ đối chiếu metadata/binary local, không truy cập website. Các verdict, medians h30, 6,2330 CPU-h EV-A và số packet hai trace đều khớp.

## D. Exploitable findings — tất cả post-hoc / exploratory

Không dùng các phát hiện sau để sửa CARD/verdict hoặc nhận novelty.

| Claim có thể khai thác | Evidence hiện có | Post-hoc? | Confirmatory test cần |
|---|---|---|---|
| Age là moderator mạnh, nhưng không có monotonicity từng regime | Fluid-nowcast h30: τ1/30/300, trace1 median **+0,02194/-0,59716/-1,22635%**; trace2 τ30/300 **-1,63073/-4,09181%**. Ghép trong D3a/b: harm tăng ở **18/20**, **17/20**; median paired change **-0,90033/-1,83062 pp**. τ/T median tương ứng **0,01298/0,41682/4,16522**, trace2 **0,75085/7,51697**. | Có; τ1 khác panel, không paired với D3. | Cùng regimes, cùng exogenous histories, fixed independent RNG substreams cho path/service/phase; prereg age grid và aggregate statistic; outer seed/phase replication. |
| Tách share shift khỏi finite-h residual giúp chẩn đoán magnitude failure | Thay Fdiff_train bằng **Fdiff_test** trong leading term: h30 median absolute error **0,26791→0,22717 pp** (a), **0,50287→0,25961 pp** (b). Giữ nguyên tolerance của prediction cũ: hit **39→52/80**, **62→70/80**. | Có, dùng test information; **không phải predictor trước truth**, không rescore D3. | Ước lượng F bằng calibration độc lập có replicate phases, khóa trước test; kiểm cả original prediction và calibrated variant trên trace khác. |
| Hybrid dễ hụt khi stationary contrast nhỏ so backlog scale | τ300,h30: median `|ŝ|/mean_stay` ở D4-row FAIL/PASS = **0,04409/0,10147** (a), **0,12090/0,21656** (b); n FAIL/PASS **11/9**, **4/16**. | Có; phù hợp transient-dominance, chưa tách slope error. | Khóa dimensionless ratio và residual diagnostic; factorial reference-slope × reference-transient trên histories chung, không chỉ đổi mỗi ŝ rồi suy cơ chế. |
| Một scalar τ/T chưa collapse được magnitude error qua trace | Spearman với relative error của fluid-nowcast selected h30: τ/T **+0,284 (n28)** vs **-0,111 (n34)**; load predictor cũng không nhất quán. `χ=100·(ŝ/mean_stay)·ΔF_train` là dạng dimensionless của **luật hiện có**, không phát hiện predictor mới. | Có; đã xem nhiều features, không p-value/CI population. | Định nghĩa timescale và predictor trước test; leave-trace-out với nhiều traces dài, outer replication; báo cả failure của collapse. |
| Trigger và clock cần giữ như các moderators riêng thay vì điều kiện cần | q75 giữ4/18, q95 giữ0/18 trên cùng replication panel; EV-A2 chỉ15/30 both-sign, nhưng 2Δ* harm30/30. | R3/Z1 có thẻ; **diễn giải moderator kết hợp là post-hoc**. | True crossing/retrigger controller và Δ×trigger factorial khóa trước; gồm small-Δ counterexamples, không chọn riêng trường hợp đảo dấu. |

Evidence đầy đủ: `audit/exploratory.json`, `prediction_diagnostics.csv`, `recomputed_rows.csv`. Không tính population confidence interval từ các row tương quan này.

## E. Reviewer threats, theo ưu tiên

1. **Estimand và generalization:** hai traces 15 phút, cùng một flow-hash stream, random-phase periodic Cox; không giữ burst/flow/service dependence thật. Outer phase không ergodic trong một run; cần nhiều traces dài và nhiều phase/seed replicas trước claim thực tế.
2. **Theory-to-test mismatch:** T12 asymptotic không suy finite-h no-harm. Cần state/history assumptions, remainder/control theo h; đo h/T_int với first-zero ACF không phải certificate mixing. “Slowest timescale” chưa được đo hoặc chứng minh.
3. **Causal attribution còn thiếu:** smoothing/nowcast, information set, feedback và population selection cùng ảnh hưởng actions. Harm không chứng minh dữ liệu tươi tự thân kém thông tin; fresh controller có thể dùng cả history/smoother. Hybrid FAIL chưa phân rã được slope/transient/share errors.
4. **Event-triggering và implementation realism:** threshold occupancy khác crossing; chưa có sensor noise, endogenous age/jitter, actuation delay/cost, finite-buffer losses, topology/routing nhiều nút hoặc production controller baseline. τ30/300 là tham số minh họa, chưa có operational calibration cho use case cụ thể.
5. **Inference và model selection:** strata/cost filters/short pilots, sequential waves và AI-chosen tolerances có exposure. D2 selection theo prediction, twins/horizons tương quan; fixed batch SE bỏ qua train/phase uncertainty. D3b chỉ thiếu2 hits để đạt64/80: precision/replication matter, không hạ threshold để cứu PASS.
6. **Reproducibility và novelty:** source lịch sử có nhưng runtime receipts/dependency hashes và raw instant/batch statistics chưa đủ; EV-D thiếu score. Cần đóng gói đúng source/environment và artifacts để replay. Literature audit này không clearance novelty; independent AI audit không thay human/author ownership hoặc Gate.

## F. Đánh giá tổng thể và kiểm chứng

Chương trình có evidence thật, báo cả FAIL và NOT_EVALUABLE, và các verdict đã lưu tái lập chính xác từ artifacts theo CARD. EV-A long-period và dấu nowcast trên hai trace là các observation đáng giữ. Tuy nhiên, evidence hiện tại chưa cho phép khẳng định plug-in không thể harm ở finite horizon, quy mọi hybrid failure cho transient bias, hay tổng quát sang event-triggered/traffic thực tế độc lập. Không cần đổi verdict; cần thu hẹp câu chữ T12/Wave2/Wave3 và giữ riêng phase/seed uncertainty. Các đề xuất kiểm chứng ở D–E là bước tiếp theo có điều kiện, không được tự chạy trong audit này; không đổi contract/PC/Gate/G1.

Các command đã chạy từ root, sau `source .venv/bin/activate && source experiments/explore_ctmc/env.sh`, với `PYTHONDONTWRITEBYTECODE=1`:

```bash
python results/ext_validity/audit/recompute.py
python results/ext_validity/audit/repro_checks.py
python results/ext_validity/audit/history_replay.py
python results/ext_validity/audit/exploratory.py
python results/ext_validity/audit/report_consistency.py
TMPDIR="$PWD/results/ext_validity/audit/system_tmp" python -m pytest \
  tests/test_ext_closed_loop.py tests/test_ext_packet.py \
  tests/test_ext_trace_rates.py tests/test_ext_alarm.py -q -p no:cacheprovider \
  --basetemp=results/ext_validity/audit/pytest_final_tmp
python results/ext_validity/audit/verify_audit.py
```

Script outputs và assertions **PASS**; targeted pytest **50/50 PASS, 32,84 s** (`pytest_final.log`). Không chạy full suite, không rerun study panel, không chạy GCP. Lượt pytest đầu dùng một số thư mục tạm hệ thống do helper tự tạo/tự xóa; lượt cuối đặt TMPDIR trong audit. Hai probe tương tác ban đầu lỗi vì chưa activate Python/empty selected subset, đã sửa; không dùng làm kết quả.

Artifacts mới đều ở `results/ext_validity/audit/`: source scripts, `*.log`, `verdicts.csv`, `recomputation.json`, `arithmetic_checks.csv`, `lock_checks.csv`, `packet_history.json`, `history_replay.json`, `repro_checks.json`, `exploratory.json`, `prediction_diagnostics.csv`, `report_consistency.csv`, input manifest và `final_verification.json`. `recomputed_rows.csv` chứa mọi row đã tính lại; report hiện tại là `notes/ops/codex/AUDIT_report.md`. Không tạo scientific figure hoặc config thí nghiệm mới; fixtures/toys chỉ phục vụ audit. Verification cuối kiểm lại hash của toàn bộ **1.404 input files** so đầu phiên và liệt kê rõ mọi drift nếu có.
