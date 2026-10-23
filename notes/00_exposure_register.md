# Exposure register — khóa phạm vi đã biết ngày 07/10/2026

Tác giả xác nhận: confirmation không chỉ cần seed mới; workload/configuration/parameter regime dùng test prediction cũng không được là chính regime đã được chọn sau khi nhìn pattern. Đổi seed đơn độc không xóa selection theo regime. Không tuyên bố sổ này đầy đủ với mọi máy/sandbox.

| Seed / configuration | Đã dùng cho gì; trạng thái | Nguồn immutable / kiểm |
|---|---|---|
| **9101–9110**, PSA POS_probeB, H=0,5 s, a=0,05 s, C=10 Mb/s, K=83, G_all, luật Ī>0; prior B=0,80 hoặc 0,70; A T_tel=0,5 s/B=30 s | n02 factorial S/M/P; n02b inst/win/noisy; đã chạy/xem pilot, không cấp lại làm held-out RQ mới. S=staleness, M=measurement, P=parameter; không hiểu S/M là State/Model repairs. | [S13/S16–S19](verification/source_checks.json); n02 JSON seeds khớp 9101–9110; n02b CSV cũng khớp. |
| **99001–99002 / 99101–99102**, smoke info-arrangement | Nguồn sandbox nói đã dùng; output bị xóa mà chưa đọc. Không suy ra đã xem outcome; vẫn đánh dấu đã chạy và không cấp làm fresh. Chưa có output để tái kiểm độc lập. | [S08/S09](verification/source_checks.json). |
| **20001–20020**, confirm/frontier/explore anchor | Registry ngày 01/10 ghi đã dùng/đã xem; thắng dòng “20000–29999 chưa dùng” trong F6 ngày 30/09. | [S01/S08](verification/source_checks.json). |
| 30001–30020; 60001–63020; 70001–70008/71001–71008; 72001–72020/73001–73020 | Các dải confirm/map/explore lịch sử, có nhiều dải con; không mặc định fresh. | [Registry toàn bộ](https://github.com/vantai13/dt4n-decision-risk-project/blob/e669f5c8053a81d6de192de9f9d0d6304ee67802/notes/seed_registry.md). |
| 80001–80020/81001–81020; 86001–86020/87001–87020; 86001–86020/89001–89020 | GO/rollout, calibration dùng lại; trạng thái FIX/SYM/FF theo registry, không nâng validity thành viewed outcome. | S08. |
| 92001–92020/93001–93020; 94001–94020/95001–95020 | GO-check đã xem sandbox và tái lập local; không còn là xác nhận mù. | S06/S08/S21. |
| 9001–10000; 11001–11932, các dải con F2–F8 | Registry bao rộng, không có nghĩa mọi seed đã dùng; 9101–9110 nằm trong dải bao nhưng **chưa có dòng sử dụng n02 cụ thể**. Sổ này bổ sung mục đích/config, không khẳng định registry không bao phủ các số đó. | S08/S16–S18. |
| 90001–90020/91001–91060, rollout v6/R3_outage | Registry tại snapshot ghi “để dành, chưa mở”; chưa kiểm exposure ở nơi khác hoặc sau snapshot, không tự cấp lại. | S08/S22. |

## Quy tắc cho L1.7–L1.8

Thiết kế confirmation sau khi khóa sổ; tránh cả seed lẫn cấu hình exploratory đã ảnh hưởng hypothesis, chốt calibration/held-out workload trước test. Muốn dùng lại một mục phải gọi rõ replication/sensitivity, không gọi fresh confirmation. RNG phụ `[seed,424242]` không tự tạo test set độc lập.

## Bổ sung exposure Phase 1 — 21/10/2026

Các cấu hình dưới đây đã được dùng để học, kiểm code hoặc đọc outcome trong L1.2–L1.5.
Không có RNG/seed mới. Không gọi việc dùng lại chúng là held-out confirmation của A05.

| Configuration / phép kiểm | Exposure và phạm vi | Artifact |
|---|---|---|
| Ví dụ chuẩn H=2,c_A=c_B=3,u=2,b_A=1,B on/off=5/0,p=s=1/2,y=(2,0),tau=1,prior_on=1/2 | Đã xem J, oracle, gaps bốn ô, gains/gamma/I và patterns; thuộc worked example, không là workload held-out chưa thấy | [L1.3](verification/l1_3/report.md), [L1.4](verification/l1_4/report.md), [L1.5](verification/l1_5/report.md) |
| Lưới L1.2 5.832 cấu hình; L1.4 1.156 cấu hình bước 1/2 và 9.604 cấu hình bước 1/6 | Vét cạn verification, đã xem số đếm và invariants; không tự là target của RQ2 được chấm mù | [L1.2](verification/l1_2/report.md), [L1.4](verification/l1_4/report.md) |
| L1.5 lưới F5 81 cặp, belief 12.288 cấu hình; reweight D=(3/8,1/8,3/8,1/8) và (1/4,1/4,3/8,1/8) | Phép kiểm/negative controls được chọn có chủ đích để kiểm sức phát hiện và blind spot; không phải discovery hoặc confirmation về mạng | [Card L1.5](lessons/L1.5_experiment_card.md), [results.json](verification/l1_5/results.json) |

Chưa chọn/fit H0,H1 hoặc chia workload held-out; record này không tự gán toàn bộ các
regime chưa chạy thành đã exposed. Khi lập A05, phải đối chiếu cả các giá trị tham số
đã dùng ở lesson/sensitivity và outcome đã nhìn, không chỉ seed.

## Bổ sung exposure L1.6 A–D — 22/10/2026

| Configuration / phép kiểm | Exposure | Artifact |
|---|---|---|
| rate_on={3,4,5,6}, (p,s)={(1/2,1/2),(3/4,3/4),(3/4,1/2)}, yA={0,2,4}, yB={0,1,2,3}, u={1,2}, c3,bA1,rate_off0,H2,tau1 | Đã xem 864 matched prior1/4,1/2,3/4 và 576 wrong prior_S0=1/2; biết 5 negative GM. Không cấp lại làm fresh held-out | [L1.6](../results/lessons/l1_6/report.md), [config](../results/lessons/l1_6/config.json) |
| p=s=11/20 hoặc3/4; prior1/2 hoặc1/4; history (2,0)→(2,2), (2,0)→(2,0); observation tuổi2 | Đã xem posterior/evidence/gains theo persistence/cách condition D. Prior1/4 là biến thể khai báo, không là warm-up đã chạy | [Variants](../results/lessons/l1_6/persistence_variants.csv), [posterior](../results/lessons/l1_6/posterior_states.csv) |
| Tau3,H3,rate_on4,rate_off1,p3/4,s1/2,prior1/4,history (2,0)→(2,1)→(2,0) | Đã xem reference posterior/evidence1/16/conditional M0 và mutant bỏ off-rate | [Card](lessons/L1.6_experiment_card.md), [Results](../results/lessons/l1_6/results.json) |

Đây là verification và toy discovery, không có seed/RNG mới, chưa fit H0/H1 hoặc chấm
held-out. B1 sensitivities, state-mean shortcut, iid Jensen và ô backlog hiện tại cũng đã
được xem; dùng lại phải gọi replication/sensitivity đúng phạm vi.

## Giới hạn

Sandbox khác, Colab và máy ngoài phiên này chưa kiểm được. Không có outcome của smoke đã xóa để đo mức exposure mạnh hơn lời nguồn. Không chạy thêm simulation hoặc mở seed để dành trong L0.1 này.

## Bổ sung exposure L1.7 — ghi trước chạy ngày 22/10/2026

| Seed / regime | Đã thấy gì từ tài liệu; kế hoạch dùng | Artifact |
|---|---|---|
| Demo root144558766427411771296652109119745142241,episode0–1999; theta chuẩn,H6,x=(2,2,off) | Đã đọc Δ145/16,variances và MC của nguồn; sẽ kiểm CRN/offset bằng root đã cung cấp. Teaching/verification, không confirmation | [Seed register](seed_registry.md), [card](lessons/L1.7_experiment_card.md) |
| Theta chuẩn,H2 bốn state; H3,x=(2,2,off); H6,x=(2,2,on/off),(6,6,on),(10,10,on) | Đã xem J/Δ/covariance/gain hoặc cost của oracle/leak/honest từ lesson. H3 exact7.75/6.5/8.125 | [Report lần chạy](../results/lessons/l1_7/report.md) |
| H3/4/6,p=s=1/2 hoặc3/4,states(2,2,·),(2,0,·),(6,6,·),(10,10,·) | Phạm vi regime được lesson nhắc; không khẳng định đã chạy mọi Cartesian combination. Những outcome đã đọc không là fresh | Hai tài liệu người dùng cung cấp; hashes trong config L1.7 |
| p3/4,s1/2,H4,x=(2,2,on),(2,0,off) | Sampler verification; nguồn không in J, nhưng runner lần này sẽ lưu/in mean và exact J để kiểm; các outcome đó được đánh dấu đã xem khi chạy | [Sampler CSV](../results/lessons/l1_7/sampler_checks.csv) |
| Tape H6,extra1; H4 hai background khác nhau có weighted arrivals bằng nhau | Golden/negative control có chủ đích; không là quan sát thực nghiệm mạng | [Exact paths](../results/lessons/l1_7/exact_paths.csv), [diagnostics](../results/lessons/l1_7/diagnostics.json) |

Các root discovery/calibration/confirmation chưa cấp và không được mở trong L1.7.
Lưới chỉ kiểm invariants của L1.2/L1.4 được ghi verification, không suy đã đọc
outcome từng regime. Nguồn cũ/L0.5 không được coi là đã rerun bởi demo hiện tại.

## Bổ sung exposure L1.8 Part A — 22/10/2026

| Regime / phép kiểm | Outcome đã xem | Artifact |
|---|---|---|
| Anchor a:1Gb/s,1500byte,qB100,rho_pre.8,age+act5ms,h6ms,dt.12/.06/.03ms | Conversion/rounding/ratios,không có full ON/OFF law hoặccontrast;T_mode/rho_post chưa khai báo | [Thẻ](../results/lessons/l1_8_a/anchor_cards.csv),[refinements](../results/lessons/l1_8_a/anchor_refinements.csv) |
| Anchor b:10Mb/s,1500byte,qB100,rho_pre.8,age+act.2s,h.6s,dt12/6/3ms,T_mode.1s;rho_post.9 minh hoạ | R1/R2 probabilities,correlation qua.204s,run duration,semigroup,rounding,pre/post drain;không J/GS/GM/Gamma cho anchor | [R1/R2](../results/lessons/l1_8_a/persistence_comparison.csv),[report](../results/lessons/l1_8_a/report.md) |
| q0{0,1,2,5},arrival rate{0,1,3,5},service{1,3},dt{1,1/2,1/4};drain/rise với h1s,dt1/2/4/8 nghịch đảo | Đã xem96 endpoint/cost/crossing checks và8 cost convergence rows;deterministic verification | [Boundary grid](../results/lessons/l1_8_a/boundary_grid.csv),[E1](../results/lessons/l1_8_a/fluid_convergence.csv) |
| Canonical xd all-off,H2,dt1;q=(10−2t)+,h10/20;R1fixedleave.1,dt10/5ms | Branch gapD13−4/fluid−3;cumulative25/timeavg2.5,1.25;effective holding times khi giữ leave cố định | [Canonical branch](../results/lessons/l1_8_a/canonical_all_off.csv),[results](../results/lessons/l1_8_a/results.json) |

Không seed mới;deterministic/reference verification,không confirmation. Đã đọc con số
GS.930→.534 vàGamma+.078 trong tài liệu nhưng thiếu full configuration nên chưa tái lập;
regime p=s5/8 được nhắc đó không được gọi là unseen sau khi đã đọc outcome.
Không tự mởD-grid PartC hoặcchọnT_mode theo gain.
Artifact/hash của các lesson cũ giữ nguyên như snapshot lúc chạy. Sổ exposure tiếp tục
được bổ sung;hash input-document trong config cũ phải đối chiếu đúng snapshot nguồn,
không diễn giải việc sổ tăng dòng thành thay đổi số đo cũ.

## Bổ sung exposure L1.8 Part B — 22/10/2026

| Regime / kiểm | Outcome đã xem | Artifact |
|---|---|---|
| Toy y=(2,0) tại−1,initialmode stationary1/2 độc lập y;rates c3/3,A1,u2,B5/0,h2,coarsep=s5/8,lambda1/4;R2,m1/2/4/8/16/32/64/128 | Đã đọc bảng nguồn trước chạy; đã xem đủL/J/gaps/actions/contrasts,mode/freshness splits,rho/Richardson ở8levels. Không cònunseen;không chuyển thànhconfirmation bằngseed mới | [Levels](../results/lessons/l1_8_b/level_metrics.csv),[state cells](../results/lessons/l1_8_b/state_cells.csv),[report](../results/lessons/l1_8_b/report.md) |
| Cùngtoy,u0 tại8levels;float64/longdouble;finite paths m1/2/4 vàforward scoring mọi level | Verification/negative control,khôngpruning/RNG/seed. Tolerance1% củaCref tạmLstar(m128),không phảiSESOI hoặcCref đã khóa | [Config](../results/lessons/l1_8_b/config.json),[rules](../results/lessons/l1_8_b/rule_comparison.csv),[controls](../results/lessons/l1_8_b/zero_action_controls.csv) |
| M0 fixed split,M1 fixed split,hybrid midpointM1 endpointM0 | Đã xem khác biệt định nghĩa phép tách;sourceB6 số làmtròn khớphybrid. Khôngchọn lạiprimary split để khớpnguồn | [Source split comparison](../results/lessons/l1_8_b/source_split_comparison.csv) |

Không mở thêmcell/levelTmode dài10× củaself-check,không chạy hai physical anchors với
law chưa khai báo. Khôngseed mới,khôngheldout hoặcfitH0/H1. Cácsai khác bảngnguồn
vàlogaudit lỗi lầnđầu được giữ để kiểm;khôngnới threshold hoặcẩn điểm khôngthuận lợi.


## L1.8 Parts C–E — 22/10/2026, khai báo trước outcome

Profile do tác giả chọn: μ10,A5,B OFF2/ON14, symmetric R2; stationary conditional B, A controlled; observation backlog/noise0/hiddenmode; candidate dt1/120s. Lưới [manifest](design/grid_v1.json): M01–M24, N01–N02, S01–S02; calibration M01/M02/M10. Chỉ được xem s_bt, time ratios và budget, không tính J/gap/margin/contrast trên những ô này trước contract-v1. Full diagnostics và scale copies được lưu ở report CDE; không chuyển screen thành evidence effect.

Reserve z.6/2/5 × κ.6/2 × η.5/.9 (12) và extrapolation z30 cùng κ/η (4): chỉ khai báo tọa độ, **không sinh D/screen/outcomes**. Chưa allocate bất kỳ discovery/calibration/confirmation root nào. Cần audit exposure bên ngoài repository trước A05/confirmation; tọa độ đơn lẻ xuất hiện trước không đồng nghĩa mọi combination còn fresh.

J goldens và B16 backward/forward cùng correlated-additivity checks trong CDE là verification trên teaching regimes đã exposed; canonical I/threshold examples cũng không confirmation. Budget-only diagnostics là exposure thiết kế, không outcome gain. Commit grid trước chạy chẩn đoán đầy đủ; tag trước mọi Phase3 contrast. Không mở Phase3 trong task CDE này.

## Post-hoc review lưới v1 và B1 của v1.1 — 22/10/2026 (DL-026–028)

Ghi bởi Claude (AI) theo yêu cầu của tác giả. Không có RNG/seed mới trong repo.

| Regime / phép kiểm | Exposure | Artifact |
|---|---|---|
| Mock review (AI, ngoài repo): dấu của C(Switch)−C(Stay) trên 200 path ngẫu nhiên cho mỗi ô M01–M12, S01 | Chỉ dấu trên các ô có contrast bằng 0 theo cấu trúc; không có J/gap/contrast; seed của review không được ghi lại | Review của tác giả, DL-026 |
| Phân loại ĐK1 cho 28 ô v1 (q_A(t0), lượng đến A, hai path cực trị trên support D đã có) | Chỉ tham số và support D đã exposed ở CDE; kết quả: 13 SD-cell, 2 conservation-cell, 13 candidate | [Test](../tests/test_dominance_v1_1.py) |
| Lưới vét cạn 9.216 state nhỏ (H 2–3, c 2–3, u 1–2, rate (0,3)/(1,5), keep 1/4 hoặc 3/4, q 0/1/4) và ví dụ luật hoà (A bão hoà, B OFF1/ON5, c3, H3) | Verification định lý ĐK1, không phải workload của RQ; đã xem J của một state ví dụ | Cùng test |
| Lưới v1.1 | **Chưa sinh.** Chưa chạy ĐK1 hoặc ĐK2 trên bất kỳ ô ứng viên nào. Reserve v1.1 chỉ được chạy ĐK1, không $p_{\text{sw}}$ | [Điều kiện](design/design_conditions_v1_1.md) |

Reserve v1: 6/12 ô held-out (z=0,6 và z=2, η=0,5) thuộc vùng Stay áp đảo; không dùng reserve v1 làm held-out của v1.1 mà không audit lại.

### Tích hợp và chạy kiểm B1 thực tế — 23/10/2026

Người thực hiện: **Doan Van Tai**. Các dòng nguồn22/10 ở trên là provenance của patch/mock review, không phải ngày hoặc bằng chứng đã chạy trong phiên tích hợp. Random200paths/ô ngoài repo chưa tái lập; nguồn không cung cấp seed/log, chỉ ghi exposure được báo. Những kiểm vô hạn/mean rollout thực chạy tại [report B1](../results/lessons/l1_8_v1_1_b1/report.md) dùng vét cạn, không RNG/seed mới.

Chỉ phân loại tham số và support D v1 đã lưu, không tính J/gap/margin/contrast cho28 ô v1. Reserve v1 chỉ kiểm điều kiện SD2 từ tham số A để đối chiếu6/12 held-out, không sinh D hoặc chấm action. Toy9.216state và ví dụ WD/tie có cost được tính làm verification, không là grid v1.1 hoặc confirmation. Ba mutant chạy trong memory, không đổi source thật.

Coverage audit phát hiện9.216 ca nguồn chưa bao giờ kích hoạt SD2/WD2; lần runner đầu FAIL assertion coverage dù test suite PASS. Thêm3.456 ca với nền OFF0/ON1 trên cả hai queue và H1/2/3, tổng12.672state-parameter cases/116.352cặp path; giữ số liệu này là verification exposure, không đưa vào confirmation hoặc chọn grid v1.1.

**v1.1: chưa chọn số/lưới, chưa ĐK1/ĐK2 trên candidate, chưa sinh reserve, chưa allocate root, chưa A01.** Khoảng p_sw và bảy lựa chọn §11 là DRAFT; Δt/phương pháp xác nhận dấu R2 chưa khóa. Phải commit protocol trước B3; không gọi B1 DRAFT là preregistration hoàn tất.


## Review N1–N6 và quyết định mốc2 — 23/10/2026

Người thực hiện: **Doan Van Tai**. Hai nguồn mới là mock reviews, không independent validation. Mock dominance review cũ nay cung cấp `random.seed(1)`,200paths/cell; script được nêu là dominance_check.py nhưng chưa cung cấp byte. Ghi seed/exposure được báo, không cấp lại root1 như fresh confirmation và không tuyên bố đã replay.

Scripts reviewer nêu recheck_b1.py(4000randomplants),float_ties2.py(truth300/M020000),idleidentity recheck(truth300/M0468), các bảng quantile/feasibility chưa có source/log để tái lập đúng. Phiên này sẽ tạo kiểm deterministic riêng, báo counts riêng, không nhận105/114/183/6549 là số đo local. Canonical N2 đã exposed; prototypes/toy của N1/N2/stationary là verification, không grid candidate.

Mốc2 ghi đủ lựa chọn/phương pháp trước tính candidate. Không J/gap/contrast/reserve p_sw hoặc Phase3 run trên v1/v1.1. Không RNG/root mới; historical frozen outputs giữ hash, active closeout đổi trạng thái có version/git history.

## Kết quả exposure mốc 2 — 23/10/2026

Người phụ trách: **Doan Van Tai**. Quyết định đã commit `27eeed4` trước tính tham số. Không tạo RNG/seed mới, không mở held-out hoặc reserve outcomes.

| Phạm vi đã xem | Outcome / evidence | Artifact |
|---|---|---|
| Verification N1: 300 truth +468 M0 structural ties, H12 | Subtraction sai95/182; idle identity sai0/0. Fixtures deterministic local, không tái lập nguyên scripts reviewer chưa có | `results/lessons/v1_1_m2/structural_ties.csv` |
| N2 canonical đã exposed và1.875 rational two-state cases | GM1/4, GSgivenM1 7/8, model bias1/2;0 violations, không candidate grid | `results/lessons/v1_1_m2/N2_lemma.json` |
| Stationary references: −2/+1 tại s=.5/.75/.9 và R2(dt1/120,T.3); generic−5/+3,s.75 | 5 laws có tail/law certificates;3 closed forms đối chiếu Decimal70 | `stationary_certificates.csv`, `stationary_reference_masses.npz` trong cùng output dir |
| Parameter map: λA6.5/7.5/8.5 ×κ.3/1/3,η.5; center λA7.5,κ1,η.9 | Rates, stability, quantile/budget:2 certified,8 HOLD_CAP. Không future J, p_switch, margin hoặc contrasts của candidate | `results/lessons/v1_1_m2/feasibility_parameters.csv` |
| Hai mutant subtraction, subprocess riêng | Mỗi mutant1 test FAIL có chủ đích; production không sửa | `results/lessons/v1_1_m2/audit/` |
| Primary reading Phase2a | Strong/Oakley/Brennan2014: full publisher Method/Eqs1–4; Birge1982 và Escudero2007: indexed primary abstracts, full text fetch bị chặn, chưa đọc full. Mapping là suy luận, novelty chưa kết luận | `notes/theory/T03_primary_reading_start.md` |

Không có human artifact, email đã gửi hoặc tagv1.1 mới. Heads-up lưu nháp nội bộ theo yêu cầu tác giả. Giới hạn cap là kết quả phải giữ, không loại ô để làm đẹp lưới.
