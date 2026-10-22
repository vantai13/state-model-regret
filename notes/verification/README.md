# Bằng chứng kiểm nguồn và cách tái chạy

Các script audit archive/DL-010 trong thư mục này kiểm nguồn đã có. Các thư mục `l1_2/`…`l1_5/` lưu lần chạy verification của Phase 1 (bên dưới). Không mở seed mới; JSON/manifest là metadata hoặc kết quả tính lại, không phải raw data cũ.

## Chạy độc lập

Python 3.10+ và SciPy. Từ repo notes đã clone:

```bash
python -m venv /tmp/l01-audit-env
/tmp/l01-audit-env/bin/python -m pip install scipy
/tmp/l01-audit-env/bin/python notes/verification/verify_archive.py --output-dir /tmp/l01-audit-results
```

Script mặc định clone public repo cũ vào temporary directory, đọc nội dung **từ tag**, kiểm remote hashes/ancestry, tính lại CI F7 từ JSON per-seed, đọc GO-check contrast, kiểm n02 seeds và phản ví dụ Γ. Output ghi vào --output-dir, không sửa snapshot. Có thể dùng --archive-repo với một clone nguồn có đầy đủ refs; đầu clone mới vẫn là cách tái kiểm ưu tiên.

## File và phạm vi

| File | Vai trò |
|---|---|
| verify_archive.py | Bản portable của script audit có thật ở Part 2, cùng công thức F7; thêm GO-check/N2/logic checks cho Part 3. |
| verification_results.json / verification_output.txt | Output thực sự của lần chạy clone mới, không tự viết số giả. |
| source_checks.json | 22 file được mở từ immutable tags, full SHA-256, URL tại commit; review digest riêng. |
| bundle_manifest.json | Public metadata rút từ manifest thật; không publish verbose private refs/local paths; chứa size/SHA/verify code và second-copy check. |
| raw_backup_manifest.json | Tar metadata/hash đã đo ở Part 2; không remeasure AoI hoặc xác nhận identity dataset 427 MiB. |
| final_review_reading_note.md | Tóm tắt từ full snapshot theo digest; không là bản gốc hoặc primary-paper verification. |

Raw, full bundles, full review và private feedback không được copy vào repo này. Manifest nguyên bản đầy đủ vẫn local-only; public summaries không có cùng hash với manifest nguyên bản và không giả chúng là bản nguyên vẹn. Second bundle copies ở filesystem khác cùng máy, chưa off-site. Full review chưa public và primary papers chưa đọc lại là giới hạn khoa học đã ghi trong inventory.

## DL-010 — kiểm hữu hạn cho closeout Phase 0

[verify_dl010.py](verify_dl010.py), tác giả Doan Van Tai, chạy bằng thư viện chuẩn:

```bash
python3 notes/verification/verify_dl010.py
```

[Kết quả đã chạy](dl010_results.json): 5.832 cặp action kiểm bảo toàn (2.048 cặp không idle, mỗi cặp kiểm 16 cách gán action cho bốn ô), 72 trường hợp state/action kiểm Jensen bằng liệt kê Markov và số hữu tỉ, 0 vi phạm. Hai ví dụ contract cho cost 37/37 và 23/17. Lưới conservation: backlog mỗi queue 0/2/10, capacity 2/3, managed load 0/2, arrivals mỗi queue/slot 0/1/4, H=2. Lưới Jensen: cùng backlog, capacity 3, managed load 2, modes 0/4, ma trận chuyển ((3/4,1/4),(1/2,1/2)), H=3; trạng thái ban đầu đã biết. Switching cost bằng 0, slot bằng 1.

Đây là đối chiếu hữu hạn cho EV-32/33; không thay chứng minh đại số tổng quát, bài tính tay của tác giả, kiểm leakage của pipeline triển khai hoặc người đọc độc lập V10. Các lần Monte Carlo/script tạm được kể trong review không được ghi thành số chạy của repo.

## L1.2 — hai phần lesson hàng đợi (09/10/2026)

[Experiment card trước khi chạy](../lessons/L1.2_experiment_card.md) · [Báo cáo và bảng đo](l1_2/report.md) · [JSON](l1_2/results.json) · [CSV toàn lưới](l1_2/grid_results.csv).

Chạy từ gốc repo sau khi cài môi trường dev:

```bash
.venv/bin/python -m experiments.lessons.run_l1_2
# Giữ lần chạy hiện tại, lưu lần mới sang thư mục khác:
.venv/bin/python -m experiments.lessons.run_l1_2 --output-dir /tmp/l1_2-rerun
```

Runner chạy 11 test lesson và toàn suite, liệt kê 5.832 cấu hình với 2.048 cấu hình không idle,
so cost/idle từng action với implementation DL-010, lưu 46 dòng bảng từng slot và hình minh họa,
rồi chạy bốn mutant trong subprocess riêng. Các log B1–B4 cố ý có test thất bại;
baseline/full suite phải xanh. Kết quả đã chạy: 11/11 lesson, 22/22 toàn repo;
0 vi phạm đẳng thức, 0 sai khác đối chiếu, mutant bị 5/3/8/5 test bắt.

Golden trong `tests/golden_phase1.py` được ghi từ đáp án của tài liệu do người dùng gửi,
không là bài tính tay của tác giả. Đối chiếu hai implementation chưa đủ để tuyên bố kiểm chéo
độc lập. G1 và các gate V3/V10/V11 chưa đổi; chưa thay verification plant Phase 3 hay validation mạng.

## L1.3 — expected cost, oracle, regret (21/10/2026)

[Experiment card](../lessons/L1.3_experiment_card.md) · [Báo cáo](l1_3/report.md) · [Cấu hình](l1_3/config.json) · [JSON](l1_3/results.json) · [CSV J và oracle](l1_3/state_costs.csv).

```bash
.venv/bin/python -m experiments.lessons.run_l1_3
.venv/bin/python -m experiments.lessons.run_l1_3 --output-dir /tmp/l1_3-rerun
```

Runner dùng plant L1.2, liệt kê cây bằng Fraction, sinh D12 từ y=(2,0), tau=1,
prior_on=1/2 độc lập với observation; H=2,p=s=1/2,c=3,u=2,b_A=1,b_B on/off=5/0,c_sw=0,dt=1.
Không RNG/seed hoặc Monte Carlo. H là lựa chọn thiết kế, không thuộc law.

Kết quả: **9/9 L1.3**, **20/20 hai lesson**, **3/3 kiểm biên/nhiều bước**, **34/34 toàn repo PASS**.
Oracle L=25/4, luôn Stay L=59/8,R=9/8; luôn Switch L=57/8,R=7/8 packet·slot.
Tất cả bốn state có Δ khác 0; không state nào thuộc vùng bảo toàn. `future_branches.csv`
lưu 8 nhánh, `slot_tables.csv` có 64 dòng, `episode_paths.csv` lưu trace pre-t0.
`old_example_paths.csv` ghi audit EV-22 theo cấu hình trích trong tài liệu L1.3,
không giả đã kiểm bản Master Plan đầy đủ.

M1–M5 chạy ở subprocess riêng với 8 test đầu và 9 test cuối. Số test đỏ lần lượt
**1/3/2/1/0** trước, **1/4/2/1/1** sau test phá đối xứng. Log/JUnit thật và patch
của mỗi mutant được lưu cùng thư mục; các FAIL này là có chủ đích.
`preflight.txt/xml` giữ lỗi dự đoán bổ sung H=3 ban đầu (22 PASS,1 FAIL): Stay tail
on/off phải là 8=6+2, không phải 7. Golden đã sửa theo dẫn giải từng queue;
plant và đáp án của tài liệu giữ nguyên. Các log baseline cuối đều PASS.

Đáp án tài liệu ghi vào golden ngày 21/10/2026, chưa là record bài giấy của tác giả.
Đây là finite verification E0/E1; chưa là validation mạng, novelty, kết quả của L1.4
hoặc bản exact solver Phase 3. G1, V3/V10/V11 và HOLD Phase 4 giữ nguyên.

## L1.4 — sổ sách 2×2, contrasts và pattern (21/10/2026)

[Experiment card](../lessons/L1.4_experiment_card.md) · [Báo cáo](l1_4/report.md) · [Cấu hình](l1_4/config.json) · [JSON](l1_4/results.json) · [CSV từng ô](l1_4/canonical_cells.csv).

```bash
.venv/bin/python -m experiments.lessons.run_l1_4
.venv/bin/python -m experiments.lessons.run_l1_4 --output-dir /tmp/l1_4-rerun
```

Dùng J/episode từ L1.3 và gap dự đoán cho sẵn trong L1.4; chưa suy ra belief/model L1.6.
Sáu hàm của `experiments/lessons/l1_4_factorial.py` giữ nhãn ô (s,m)=00,10,01,11,
hoà chọn Stay và chỉ dùng J thật sau quyết định. Kết quả đã chạy: **12/12 L1.4**,
**32/32 ba lesson**, **2/2 kiểm bổ sung**, **48/48 toàn repo PASS**.

L=(59/8,25/4,57/8,25/4), R=(9/8,0,7/8,0) theo thứ tự 00,10,01,11.
G_S=9/8,G_M=1/4,G_SM=9/8,Γ=−1/4,G_S|M1=7/8,G_M|S1=0 packet·slot.
Gamma episode từ −3 tới +2; model repair hại 1/2 tổng xác suất D. Pattern (0,0,1)
và (1,0,0) mỗi loại có xác suất 1/2; chỉ dấu trung bình chưa đủ giải thích interaction.

Vét cạn 1.156 cấu hình lỗi cộng bước 1/2 và 9.604 cấu hình bước 1/6 đều có 0 vi phạm
(a),(b),(e), chỉ có hệ số gamma/margin −1,0,1. `all_patterns.csv` kiểm 16 trường hợp
cho đủ 8 pattern ở Δ=±2, chạm thêm hệ số 2. Δ=0 được kiểm riêng, không chia margin 0.
Quét lỗi, tie diagnostic, mixture và partial-repair EV-26 có CSV riêng.

N1–N5 có số test đỏ trước golden bất đối xứng là **7/3/2/0/2**, sau là **7/3/2/1/2**.
N4 đổi nhãn S/M lọt 11 test đầu, bị test thứ 12 bắt. N1 còn được thử riêng trên toàn
pattern và bị bắt khi hệ số 2 đảo thành −2. Mutant FAIL là có chủ đích, source baseline
không bị sửa; log và JUnit lưu theo tên `N*_initial`, `N*_final`, `N1_all_patterns`.

Lần runner đầu dừng sau 48/48 test PASS do nhãn hệ số float khác nhãn Fraction.
Đã sửa phép chia sang Fraction, giữ record ở `development_issue.json`; lần cuối hoàn tất
mọi bước. `run_output.txt` lưu stdout/stderr toàn runner; `full_suite.txt` lưu test repo.

Quy tắc “Γ dương phải báo phân bố pattern” và giới hạn cộng tính được bổ sung trong
[claim boundary](../01_claim_boundary_v0.md); không thay contract đã đóng băng.
Không RNG/seed/CI lấy mẫu; đây là exact E0/E1 trên cấu hình khai báo, chưa là evidence mạng,
novelty hoặc bài tự tính giấy của tác giả. G1,V3/V10/V11 và HOLD Phase 4 giữ nguyên.

## L1.5 — F5, I_Δ và checker độc lập (21/10/2026)

[Experiment card](../lessons/L1.5_experiment_card.md) · [Spec làm việc](../lessons/L1.5_identity_diagnostic_spec.md) · [Báo cáo](l1_5/report.md) · [Config](l1_5/config.json) · [Results](l1_5/results.json).

```bash
.venv/bin/python -m experiments.lessons.run_l1_5
.venv/bin/python -m experiments.lessons.run_l1_5 --output-dir /tmp/l1_5-rerun
```

Kết quả đã chạy: **11/11 L1.5**, **43/43 bốn lesson**, **2/2 kiểm giới hạn** và **61/61 toàn repo PASS**.
F5 dùng logic độc lập với choose L1.4, khớp regret trực tiếp trên 16 cặp chuẩn và 81 cặp
Δ,Δ_hat có zero trên cả hai trục. Hai bounds nền kiểm trên 24 cặp thỏa điều kiện margin
và 324 cấu hình cost error, 0 vi phạm. Mean I theo chính belief bằng 0 trên **12.288 cấu hình**.

I_Δ=(1/2,−1/2,0,0), mean=0,E|I|=1/4; nhóm mode thật on/off có mean=±1/4 và không áp
guard theo y. Ô 00/01 cùng consistency=1/2, regret=9/8 và 7/8. Belief chuẩn và gaps M0
vẫn là đầu vào cho sẵn; chưa xác nhận posterior S0 end-to-end.

Năm mutant P1–P5 có số test đỏ cuối **2/2/6/2/6**. Dựng lại checker dùng chung helper ở
file riêng cho số test đỏ **2/2/6/1/6**: test any-belief bỏ sót P4; checker độc lập dùng sum
có trọng số bắt được nó. Lỗi tie Switch cài vào choose L1.4 trước import L1.5 làm 2 test
điểm hoà/lưới F5 đỏ. FAIL mutant là có chủ đích, source baseline giữ nguyên.

`canonical_states.csv` lưu I/error/gamma; `canonical_regrets.csv` lưu 16 cặp F5/direct;
`f5_grid.csv`, `belief_grid.csv`, `cost_error_bounds.csv` lưu toàn bộ các lưới. Bảng
`belief_diagnostics.csv` cho mean=1/8 khi reweight D lệch có thể phát hiện, và mean=0
ở một D khác belief nhưng cùng E[e_M]. Dùng hai belief khác giữa cell00/cell01 cho mean=7/8.
Mean-zero chỉ là điều kiện cần dưới giả định, chưa đủ chứng nhận belief; PASS của test
mismatch nghĩa là đã xác nhận guard mean-zero bị vi phạm đúng như dự kiến.

`run_output.txt` lưu toàn runner; `full_suite.txt` và các file XML lưu pytest thật;
`P*_coupled`/`P*_independent` và `cross_choose` lưu mutation replay. Hình ở
`identity_diagnostics.png`. Chưa fit H0/H1 hoặc chấm held-out; không chọn δ/quantile
chính thức sau khi nhìn kết quả. Spec ghi yêu cầu cho A05 và việc mang sang L1.8.
Không có seed/Monte Carlo/CI lấy mẫu; G1,V3/V10/V11 và HOLD Phase 4 giữ nguyên.

## L1.6 A–D — belief/M0/2×2 end-to-end (22/10/2026)

[Card](../lessons/L1.6_experiment_card.md) · [Spec](../lessons/L1.6_belief_model_spec.md) · [Báo cáo](../../results/lessons/l1_6/report.md) · [Config](../../results/lessons/l1_6/config.json) · [Results](../../results/lessons/l1_6/results.json).

```bash
.venv/bin/python -m experiments.lessons.run_l1_6
.venv/bin/python -m experiments.lessons.run_l1_6 --output-dir /tmp/l1_6-rerun
```

Output mới ở `results/lessons/l1_6/`, ngoài src/experiments. Mutation dùng subprocess,
không copy repo. Source `experiments/lessons/l1_6_belief.py` và evaluator reference
`l1_6_reference.py` dùng chung plant; reference không gọi S0 belief/mode_paths.

**16/16 lesson,59/59 năm lesson,3/3 reference/schema và80/80 toàn repo PASS.**
864 matched cases thoả posterior/Bayes/mean I=0; 6.696 state/action cases thoả Jensen
và idle identity; 576 wrong-prior cases có đúng5 GM âm. Toàn bộ lưới đều lưu CSV.
History filtering có evidence/path records, gồm impossible history bị từ chối và tau3/nonzero-off.

Canonical S0M0 predicts6,75/7, S0M1 predicts7,375/7,125. Bảng L/R/contrasts tái lập L1.4–L1.5;
GS=9/8,GM=1/4,Gamma=−1/4. Ô backlog hiện tại cost7: GS tách theo thứ tự thành3/8 freshness
+3/4 mode visibility. Không coi phần thấy mode là practical telemetry/net gain.
Các variants/B1 sensitivities lưu đầy đủ, không suy GS đơn điệu từ conditional rows.

Q1–Q5 bị 2/3/3/2/1 test function bắt; tính pytest parametrized cases là2/3/3/4/2.
Không test nào trong 5 test chuẩn bắt chúng. Q6 bỏ off-rate lọt16 test gốc, bị test bổ sung bắt.
Các FAIL mutant là có chủ đích. Logs/JUnit: lesson,lessons,reference,full_suite,Q1…Q5,Q6_core,Q6_extra;
`run_output.txt` ghi toàn runner, `belief_pipeline.png` dựng từ số liệu.

Các giả định §7(c) là điều kiện đủ, không phải iff; mean I=0 chưa chứng nhận belief.
Prior1/4 “B rỗng” là conditional initialization minh hoạ, chưa chạy warm-up/stationary.
Đã ghi exposure; chưa đọc P11 gốc, fit H0/H1 hoặc chấm held-out. Spec/schema/prior/D/B1/M_K
khóa tại L1.8; timescale vật lý/forward solver Phase3 chưa làm. Golden chưa thay bài giấy;
G1,V3/V10/V11 và HOLD Phase4 giữ nguyên.

## L1.7 — CRN, seed streams, exposure và leak (22/10/2026)

[Card](../lessons/L1.7_experiment_card.md) · [Spec và mock tham khảo](../lessons/L1.7_stream_exposure_spec.md) · [Index tái chạy](l1_7/README.md) · [Report](../../results/lessons/l1_7/report.md).

```bash
.venv/bin/python -m experiments.lessons.run_l1_7
.venv/bin/python notes/verification/verify_l1_7_artifacts.py
```

**13/13** test L1.7,**72/72** sáu lesson,**4/4** bổ sung,**97/97** toàn repo PASS.
N2000,XB=(2,2,off),H6,p=s1/2: primitive meanΔ9.236±0.243796SE,var118.872740;
naive extra1 mean8.745±0.420489SE,var353.621786. Exact variances117.496094,
358.152344 và independent323.248047 (independent chỉ exact,không MC).
Primitive background mismatch0/2000,residual0/2000; naive mismatch1942/2000,
residual nonzero1914/2000. Residual0 chưa đủ chứng nhận CRN; có counterexample/test riêng.

H3,K1: oracle cost7.836±0.116965SE,leak6.5725±0.089445SE,honest8.22±0.089265SE
packet·slot; exact7.75/6.5/8.125. Honest vẫn thắng495/2000 episode; H2 blind spot
leak bằng oracle1200/1200. Sáu lỗi mutant bị bắt; R7 bỏ chiaK equivalent nên qua.
Audit process mới replay11332 CSV rows bằng plant,kiểm source/manifest/JUnit đều PASS.

Output tại `results/lessons/l1_7/`; root demo và exposure ghi trước chạy tại
[seed registry](../seed_registry.md) và [exposure](../00_exposure_register.md).
Đã pin NumPy2.5.3/record PCG64; root lấy từ tài liệu,không tự nhận entropy mới.
Mock là tham khảo có tài liệu,chưa là bài kín sách/V10. Không khóa contract-v1,
không mở root discovery/calibration/confirmation; G1,V3/V10/V11,HOLD Phase4 giữ nguyên.

## L1.8 Part A — physical seconds → slots (22/10/2026)

[Card trước chạy](../lessons/L1.8A_experiment_card.md) · [Spec](../lessons/L1.8A_slot_model_spec.md) · [Index](l1_8_a/README.md) · [Report](../../results/lessons/l1_8_a/report.md).

```bash
.venv/bin/python -m experiments.lessons.run_l1_8_a
.venv/bin/python notes/verification/verify_l1_8_a_artifacts.py
```

4/4core,10/10bổ sung,111/111 toàn repo PASS;96 fluid-boundary và900round-trip
cases không vi phạm. Neo a:dt.12ms,c10,age42slot=5.04ms(+.8%),H50.
Neo b:dt12ms,c10,age17slot=.204s(+2%),H50,drainpre.6s,post1.2s nếurho_post.9,
h/Tpost.5. T_mode b=.1s minh hoạ;anchor a chưa cóT_mode/rho_post.
R2 correlation qua204ms=.016907466 tại12/6/3ms;R1=.009415233/.012954208/.014883122.
D13 cho queue drain2→0 trong1s là0/.5/.75/.875 so fluidarea1 khi dt1/.5/.25/.125s.
Interior-crossing correction so với boundary telescoping là dương (ví dụ+1/4),tổng
error drain vẫn âm. Không thay D13 thành fluid area.

Output tạiresults/lessons/l1_8_a;khôngRNG/seed,không nghiên cứu mạng/held-out.
PartBcontrast acceptance,PartCgrid,PartDdecisions,PartEfreeze chưa làm.
Không tái lập con số43% của nguồn khi thiếu full configuration. G1,V3/V10/V11 vàHOLDPhase4 giữ nguyên.

[Audit artifact trong process mới](../../results/lessons/l1_8_a/independent_artifact_audit.json) dùng Decimal exp 60 chữ số và nguyên hàm positive-part để đối chiếu CSV; PASS, không thay review khoa học độc lập.

## L1.8 Part B — refinement bằng finite-law DP (22/10/2026)

[Card](../lessons/L1.8B_experiment_card.md) · [Working protocol](../lessons/L1.8B_refinement_protocol.md) · [Report](../../results/lessons/l1_8_b/report.md) · [Index](l1_8_b/README.md).

```bash
.venv/bin/python -m experiments.lessons.run_l1_8_b
.venv/bin/python notes/verification/verify_l1_8_b_artifacts.py
```

**13/13 Part B, 124/124 toàn repo PASS**. DP không Monte Carlo, gộp integer backlog
units1/m; tám levels m1…128 có4/6/14/30/62/126/254/510 states. GS từ0.9296875 xuống
0.307151637, GM0, Gamma/m2=0.078002930 vàm128=0.017151712. Richardson cuối cho
GS≈0.302699661/Gamma≈0.017362905, chỉ là estimates, chưa true continuum reference.
Cref tạm5.933106738,tol1%; original coarse-report chọnm8 cóerror proxy1.220%,
finer-report hoặchalf-tol chọnm16 còn0.616%. Recordrho mọi metric,không tự khóaorder band.

Forward scoring độc lập tái sinhD vàchấm6policies khớp backward trong3.6e-15.
Audit1006state rows/4024F5 checks/78triplets,hashes vàJUnit PASS; zeroaction0,
meanI≈0,R110,không precision action mismatch ở cảprimary vàdiagnostic cells.

Có2rounding discrepancies trong nguồn (Gamma/m4, Lstar/m32). Bảng tách B6 khớp
hybrid midpointM1→endpointM0,không là fixed-model State-only path. Fixed-M0 mode
share ởm128=17.811%;không claim11% từhybrid cho State-only. Hai fixed-M0 components
chưa cófirst-order ratio ổn định ởtriplet cuối. XemCSV/script vàlog lầnđầu dừng ởaudit
nguồn;baseline tests cuối đềuPASS. GiữG1,V3/V10/V11,HOLDPhase4; chưaPartsC–E/contractv1.


L1.8 CDE: [index](l1_8_cde/README.md), [report](../../results/lessons/l1_8_cde/report.md), [artifact auditor](verify_l1_8_cde_artifacts.py). Đọc rõ5 consistency PASS+1source PARTIAL và A01/human gates pending; không grid contrast hoặc held-out outcome.

B1 v1.1 (23/10/2026): [index](v1_1_b1/README.md), [báo cáo](../../results/lessons/l1_8_v1_1_b1/report.md), [điều kiện DRAFT](../design/design_conditions_v1_1.md). Baseline146→154/154 PASS; coverage thiếu SD2/WD2 của nguồn được phát hiện và sửa bằng verification cases bổ sung; first_run FAIL được giữ. HOLD A01/A04 grid v1; chưa chọn/chạy grid v1.1 hoặc p_switch, chưa tạo tag mới.
