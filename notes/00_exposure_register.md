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

## Phần A — B3 initial screen,23/10/2026

Doan Van Tai. Candidate commit571d4cf, engine commitc7ddef3;44 sign-only evaluations,22 main ×dt1/120,1/240. Không reserve p_sw, không lưu W/Δ/margin/Lstar. Bảng p_sw interval đầy đủ:

| Ô | Refinement | p_low | p_high | Class |
|---|---|---|---|---|
| M01 | 1 | 0.46525490370630207 | 0.4652549037063193 | in |
| M01 | 2 | 0.4643657987317197 | 0.46436579873175254 | in |
| M02 | 1 | 0.05809277987174269 | 0.05809277987176088 | out |
| M02 | 2 | 0.05778643356993665 | 0.057786433569971415 | out |
| M03 | 1 | 0.6364783708182058 | 0.6364783708182389 | in |
| M03 | 2 | 0.6360621308916001 | 0.6360621308916647 | in |
| M04 | 1 | 0.0 | 1.804011558512889e-14 | out |
| M04 | 2 | 0.0 | 3.5272424914621265e-14 | out |
| M05 | 1 | 0.8208694669025174 | 0.8208694669025955 | in |
| M05 | 2 | 0.8209545820196784 | 0.8209545820198332 | in |
| M06 | 1 | 0.0 | 4.3597796556704023e-14 | out |
| M06 | 2 | 0.0 | 8.638778685779016e-14 | out |
| M07 | 1 | 0.8460140352173076 | 0.8460140352173184 | in |
| M07 | 2 | 0.8465051680766155 | 0.8465051680766355 | in |
| M08 | 1 | 0.562527124004479 | 0.5625271240044906 | in |
| M08 | 2 | 0.5624683300736651 | 0.5624683300736869 | in |
| M09 | 1 | 0.9999999999999892 | 1.0 | out |
| M09 | 2 | 0.9999999999999793 | 1.0 | out |
| M10 | 1 | 0.6232373313156218 | 0.6232373313156464 | in |
| M10 | 2 | 0.6234179794554571 | 0.6234179794555044 | in |
| M11 | 1 | 0.9999999999999738 | 1.0 | out |
| M11 | 2 | 0.9999999999999486 | 1.0 | out |
| M12 | 1 | 0.7036477092198449 | 0.7036477092199062 | in |
| M12 | 2 | 0.7040829049884901 | 0.7040829049886111 | in |
| M13 | 1 | 0.9999999999999705 | 1.0 | out |
| M13 | 2 | 0.9999999999999418 | 1.0 | out |
| M14 | 1 | 0.9999999999999701 | 1.0 | out |
| M14 | 2 | 0.9999999999999409 | 1.0 | out |
| M15 | 1 | 0.9999999999999182 | 1.0 | out |
| M15 | 2 | 0.9999999999998371 | 1.0 | out |
| M16 | 1 | 0.9999999999999166 | 1.0 | out |
| M16 | 2 | 0.9999999999998341 | 1.0 | out |
| M17 | 1 | 0.9999999999997685 | 1.0 | out |
| M17 | 2 | 0.9999999999995379 | 1.0 | out |
| M18 | 1 | 0.9999999999997641 | 1.0 | out |
| M18 | 2 | 0.9999999999995288 | 1.0 | out |
| M19 | 1 | 0.562118136683926 | 0.5621181366839362 | in |
| M19 | 2 | 0.562226214202635 | 0.5622262142026538 | in |
| M20 | 1 | 0.9999999999999892 | 1.0 | out |
| M20 | 2 | 0.9999999999999793 | 1.0 | out |
| M21 | 1 | 0.9629231475585321 | 0.9629231475585537 | out |
| M21 | 2 | 0.9630757181878092 | 0.9630757181878505 | out |
| M22 | 1 | 0.999999999999711 | 1.0 | out |
| M22 | 2 | 0.9999999999994229 | 1.0 | out |

8/22 in ở cả2levels, chưa đạt15/22. Unresolved mass0 trên44rows; giữ toàn bộ out. Không RNG/seed mới. Results: results/lessons/v1_1_a4/.

## Phần A — B3 sau đúng một redesign,23/10/2026

Doan Van Tai. Redesign prereg19d03cc, candidate3fe81d2; λA7/7.2/8.1, center7.2.44 sign-only evaluations, không reserve hoặc margin/Lstar.

| Ô | Refinement | p_low | p_high | Class |
|---|---|---|---|---|
| M01 | 1 | 0.6379402437413106 | 0.6379402437413162 | in |
| M01 | 2 | 0.6377206612205755 | 0.6377206612205848 | in |
| M02 | 1 | 0.22803166256473717 | 0.22803166256474355 | in |
| M02 | 2 | 0.22795851775089693 | 0.22795851775090809 | in |
| M03 | 1 | 0.8447972941356348 | 0.8447972941356434 | in |
| M03 | 2 | 0.8455524400339849 | 0.8455524400340004 | in |
| M04 | 1 | 0.17005600259320816 | 0.17005600259321982 | in |
| M04 | 2 | 0.16968919006734756 | 0.16968919006736927 | in |
| M05 | 1 | 0.9999999999999911 | 1.0 | out |
| M05 | 2 | 0.9999999999999831 | 1.0 | out |
| M06 | 1 | 0.12837369605096044 | 0.1283736960509872 | in |
| M06 | 2 | 0.1287980098588167 | 0.12879800985886866 | in |
| M07 | 1 | 0.7150936680479748 | 0.7150936680479941 | in |
| M07 | 2 | 0.715245090865843 | 0.7152450908658798 | in |
| M08 | 1 | 0.3395673012371496 | 0.3395673012371698 | in |
| M08 | 2 | 0.33902334152732383 | 0.33902334152736247 | in |
| M09 | 1 | 0.9083417271342186 | 0.9083417271342585 | out |
| M09 | 2 | 0.9087116413600541 | 0.9087116413601325 | out |
| M10 | 1 | 0.29323877221659694 | 0.2932387722166399 | in |
| M10 | 2 | 0.2929612215690838 | 0.2929612215691684 | in |
| M11 | 1 | 0.9999999999999503 | 1.0 | out |
| M11 | 2 | 0.9999999999999012 | 1.0 | out |
| M12 | 1 | 0.22918800415948473 | 0.2291880041595933 | in |
| M12 | 2 | 0.22911318338460923 | 0.22911318338482478 | in |
| M13 | 1 | 0.9991045381906865 | 0.9991045381907464 | out |
| M13 | 2 | 0.999105564848101 | 0.9991055648482193 | out |
| M14 | 1 | 0.9716771161970548 | 0.9716771161971158 | out |
| M14 | 2 | 0.9718181003678029 | 0.971818100367923 | out |
| M15 | 1 | 0.9999999999999235 | 1.0 | out |
| M15 | 2 | 0.9999999999998479 | 1.0 | out |
| M16 | 1 | 0.9999999999999221 | 1.0 | out |
| M16 | 2 | 0.9999999999998449 | 1.0 | out |
| M17 | 1 | 0.9999999999997907 | 1.0 | out |
| M17 | 2 | 0.9999999999995822 | 1.0 | out |
| M18 | 1 | 0.9999999999997862 | 1.0 | out |
| M18 | 2 | 0.9999999999995732 | 1.0 | out |
| M19 | 1 | 0.44842825717304974 | 0.44842825717306695 | in |
| M19 | 2 | 0.4478161804904561 | 0.4478161804904888 | in |
| M20 | 1 | 0.9460964426722879 | 0.9460964426723278 | out |
| M20 | 2 | 0.9461433773060919 | 0.9461433773061703 | out |
| M21 | 1 | 0.8371370776064071 | 0.8371370776064471 | in |
| M21 | 2 | 0.8366947320289214 | 0.8366947320289998 | in |
| M22 | 1 | 0.9999999999999779 | 1.0 | out |
| M22 | 2 | 0.9999999999999567 | 1.0 | out |

11/22 in, yêu cầu15/22; unresolved mass0 ở44rows. Đã hết một lượt redesign; giữ đủ22main, B4 không chấp nhận, không chuyển calibration/freeze. Results: results/lessons/v1_1_a4_redesign/.

## Phần A — verification bổ sung sau screen,23/10/2026

Doan Van Tai. Chỉ mở toy conservation q10000/10001,H300,incs−3/+2 và keep3/4,97/100 để kiểm mutant cost-subtraction. Test dyadic đầu không bắt được mutant, record PASS giữ nguyên; thêm keep97/100 làm mutant FAIL, source kernel không đổi. Không mở candidate margin/Lstar. Full177tests PASS sau bổ sung. D/dominance audit136rows và136legacyB comparisons chỉ dùng support/parameters đã exposed, không future J. Plot chỉ dùng p_sw đã exposed và stationary error bounds. FinalB4 giữ rejected11/22, không lọc ô để nhận lưới. No RNG/seed, no extra screen/heldout hoặc contrast. Human gates author-attested bằng phản hồi trực tiếp, không tạo human artifact. Heads-up chưa gửi.

## Thử nghiệm REFORMULATE lưới (DISCOVERY), 23/10/2026 — đã công khai

Doan Van Tai. Nhánh `explore/reformulate-grid` (commit `db955de` → `ee349a4`), push công khai lên GitHub ngày 23/10, merge vào `main` tại `87dcd53`. Kế hoạch và báo cáo: `notes/explore/`.

| Đã xem | Phạm vi |
|---|---|
| Khoảng $p_{\text{sw}}$ ở dt và dt/2 | 480 cặp (lát, $\lambda_A$): $\kappa\in\{0{,}3;1;3\}$, B q50/q90, A q90 (A q50 ở $\kappa$ 1), $\eta\in\{0{,}5;0{,}75\}$, horizon $r_h=1$, 2 s, 8 s; thang $\lambda_A$ từ 6, bước 0,25 |
| Khoảng $p_{\text{sw}}$ ở dt/4 | 48 ô được neo của P4 |
| Nhãn ĐK1 | 48 ô neo của P4 và 5 đầu dò cấu trúc |
| Budget, $y_A$, $y_B$, $H$, sai số law | mọi dòng trên |
| Tính lại để kiểm script | M01, M02, M04 của v1.1 (đã xem từ trước, khớp tuyệt đối) |

**Chưa xem:** $J$, $L_*$, $C_{\text{ref}}$, margin, belief, pipeline, contrast, regret. **Chưa tính:** mọi tọa độ held-out của protocol v1.2 ($\kappa$ 0,6 và 2; B q75; $\eta$ 0,625; $h$ 4 và 12 s). Không RNG, không seed.

## Lưới v1.2 — chạy chính thức, 23/10/2026

Doan Van Tai. Protocol commit `d696eef` trước khi chạy; kết quả `results/lessons/v1_2/`, [grid](design/grid_v1_2.md).

| Đã xem | Phạm vi | Mới? |
|---|---|---|
| Khoảng $p_{\text{sw}}$ ở dt, dt/2 cho thang của 20 lát chính; dt/4 và nhãn của 38 ô chính | Tái lập tuyệt đối thử nghiệm | Không |
| Khoảng $p_{\text{sw}}$ ở dt, dt/2 cho thang của 6 lát held-out H01–H06 (65 điểm thang) | $\kappa$ 0,6 và 2, B q75, $\eta$ 0,625, $h$ 4 và 12 s | **Có** |
| $p_{\text{sw}}$ ở dt/4 và nhãn ĐK1 của 12 ô held-out R01–R12 | | **Có** |
| Nhãn và $p_{\text{sw}}$ của N01–N04, W01, S01 và đầu dò P01, P02 | Định nghĩa v1.1 / ô đã có trong thử nghiệm | Không đáng kể |

**Chưa xem:** $J$, $L_*$, margin, contrast, regret ở bất kỳ ô nào. Held-out chưa dùng cho discovery hay calibration.

## Exposure L2.1–L2.3 — 24/10/2026

Người phụ trách: **Doan Van Tai**; AI-assisted. Trước các commit lưu artifact,
claims, forecasts và nguồn L2.2/L2.3 đã xuất hiện trong hội thoại. Bootstrap
`5ab4750` và proof `3870931` là receipts sau exposure, không prereading evidence.

| Configuration / nội dung | Trạng thái đã biết | Artifact |
|---|---|---|
| PC1–PC6; K2/K3/K5/K6 và Q5 | AI chọn theo ủy quyền, đã exposed; không blind calibration của tác giả | literature/prior_predictions.md, claims.md |
| 21.952 toy một slot, pairs0..7, C3/U2/prior1/2 | Golden V1/V2/V4, mutant counts đã lộ trong lesson; lượt lưu là replication | results/lessons/l2_2/cases.csv và voi_mapping.json |
| P11 toy4priors; V1 bounds; V2 discrepancy disclosure | Đã xem true costs, VOI/regret và corrections; không fresh confirmation | results/lessons/l2_3/p11_toy.json |
| SOB14/P11 primary notes; B82/MAB11/E07/SOC12 | AI đọc theo mức note; không L-self hoặc nhận xét independent human | literature/README.md và papers/ |

Không RNG mới, không dùng held-out grid để chọn forecasts, chưa chạy outcomes
Phase3. Việc ghi source ở đây không nâng G1 hoặc chứng nhận prediction mù.

## L2.7 Part B —26/10/2026, AI-assisted/exposed

Người phụ trách: **Doan Van Tai**. P12 Definition1/§3.1 được AI đọc targeted
trong official NeurIPS PDF; R43 official abstract và archived AI-T24/10 note
đã được mở để kiểm provenance. Không là L-self hoặc prereading prediction.
OεRE draft, K5/PC5 wording và ba candidate K rules đã lộ qua lesson/hội thoại.
Không gọi bất kỳ lựa chọn tương lai nào dựa trên chúng là blind forecast mới.

Đã xem lại V1 frozen và chạy625abstract two-state problems để kiểm gap bounds;
chỉ đọc tọa độ/design labels của38main+12held-out+8controls/probes để kiểm
membership. Không đọc/tính J,Lstar,margin,regret hoặc contrasts của held-out;
không đưa p_sw/λA riêng vào features. K5 cũ giữ nguyên, chưa chọn rule mới;
R03/R04 membership là metadata, không là confirmation.
[Artifact/source/hash](../results/lessons/l2_7/part_b/source_access.json),
[queue](lessons/L3.3_equivalence_queue.md). Contract/thresholds/D25/G1 giữ nguyên.

## L2.8 Part2 —26/10/2026

Doan Van Tai phụ trách; AI đã exposed archived R01/R04/toy và lesson. Forecast
A1–A3 lưu reading_card trước queries, không blind forecast tác giả. R02 mới primary
đọc sau CiteSeerXretry; NDT26/WM26/AIS22 được tác giả duyệt trước PDF/note.
WM26 có2×2repair là exposure phải giữ khi viết A05/L2.9. Diagnostic R04 dùng true
costs; chưa chọn H1/null/threshold, không chạy grid/held-out. [Report](../results/lessons/l2_8/part2/report.md).

## L2.8 follow-up —26/10/2026

AI đọc P02 VoR (Bảng 2 số trung bình delay/xe được chép vào note), abstract R06 và
9 bài đề xuất; các nội dung này nay exposed trước khi tác giả đọc. Không có outcome
lưới/held-out nào được xem. PHASE_2 v2.0 (bản trong Downloads của tác giả, sha256
`e09c4989…a6c647`) được AI đọc §5.4, §13–§17 để đối chiếu vai trò nguồn; không thực hiện L2.9.

## L2.9 Part 1 —26/10/2026

Lesson L2.9 Part 1 của mentor (AI) chứa nhãn tạm reviewer cho PC1–PC6/Main RQ trong
khối thu gọn; nội dung lưu ở `results/lessons/l2_9/part1/reviewer_view_AI_open_after_grading.md`
để giữ provenance. Hồ sơ trong prior_boundary không chép các nhãn đó. Tác giả có thể
đã thấy khối này trước khi chấm: ghi lại khi chấm nếu đã mở (K3, PHASE_2 §14).

## Phase 2 — tổng hợp exposure trước Phase 3 (L2.9 Part 2, 26/10/2026)

AI soạn theo ủy quyền của Doan Van Tai. Phase 3 cần biết những gì đã lộ:

- **Forecast nhãn PC** đã lộ trước khi lưu (DL-040); nhãn tạm L2.9 do AI chấm **sau khi
  thấy** nhãn tạm của mentor; không có dự đoán mù của tác giả cho Phase 2.
- **Luật K5 ứng viên** (list/κ3, κ≥2, q90/h8…) đã lộ **chỉ ở mức tọa độ** (L3.3 queue);
  chưa chọn luật, chưa có outcome.
- **H1-Q01…Q03** đã lộ (heuristic, chưa khóa H1/null; H1-Q01 không phải F của D22).
- **R02 Example1** (loss 0.507) và **chẩn đoán một bước dịch từ R04** đã lộ, chạy trên toy V1
  (GS=−1/4), không phải ô lưới.
- **P02 Bảng 2** và kết quả WM26 (F.1) đã được AI đọc và chép vào note.
- **Held-out R01–R12:** p_sw, λA, nhãn và budget đã lộ từ lúc khóa lưới (DL-039, không phải
  Phase 2) và bị D25 cấm làm input; trong Phase 2 chỉ đọc **tọa độ và nhãn thiết kế**.
  **Chưa ai thấy J, margin, contrast hay regret của bất kỳ ô nào (main hay held-out)**:
  held-out vẫn **sạch về outcome**.

## Đợt đọc được duyệt — 26/10/2026

IA26, DTS25, CEN26, CEH23 được đọc thay tác giả (AI-T/AI-F); H1-Q04 (độ phi tuyến của động
học kỳ vọng ↔ khoảng cách CE) thêm vào hàng đợi H1, chưa khóa. Không có outcome lưới hay
held-out nào được xem; held-out vẫn sạch về outcome.

Bổ sung 26/10 (tối): R34 bản CDC 1992 (JSEQ, trễ k) và ví dụ tính tay T03 đã được AI đọc/dựng;
không có outcome lưới hay held-out nào được xem.

## Gate L GO có điều kiện — 26/10/2026 (DL-043)

Tác giả đã thấy nhãn tạm (AI) và khối reviewer của mentor trước khi xác nhận nhãn; không có dự
đoán mù của tác giả cho Phase 2. Trước Phase 3: chưa ai thấy J, margin, contrast hay regret của
bất kỳ ô nào; held-out sạch về outcome. Prediction card L3.3 phải viết trước A01.


## L3.1 Part 3 — 27/10/2026

Doan Van Tai phụ trách; AI đọc lesson và repo để ghi DL-044, làm con trỏ hiện hành,
reader packet và rebuild cell/D. Bản lesson chứa giải thích và gợi ý tự kiểm đã lộ;
không phải tác giả tự trả lời kín sách. Không ghi author attestation mới.

Chỉ dựng lại 38 **main** constructors và D tách A/B cho M01/M09/M22 cùng control N01,
ref 1/2/4, để đối chiếu implementation gốc. Đây là kiểm numerical migration;
không tính action costs, margins, predictions, regret hoặc contrasts trên lưới.
Full regression có tests đọc metadata và p_sw thiết kế đã công khai, bao gồm metadata
held-out, và tái tính screen M31 cũ. Không dựng D/không chạy outcome held-out mới.
A01/A04/A05-F/A05-T chưa chạy. L3.3 chưa khóa; K5/null/H1 không được chọn.
[Config và nguồn](../results/lessons/l3_1/part3/config.json) ·
[report](../results/lessons/l3_1/part3/report.md).

## L3.2 Parts 1–4 — 27/10/2026

Doan Van Tai phụ trách; AI đọc bốn lesson và triển khai engine ở experiments/A00_engine.
E1/E2/E3/E5/E6/E7/golden Phase1 và cơ chế Jensen đã exposed trong lesson trước khi lưu
expected_before_code; không là blind prediction hoặc tác giả tự trả lời kín sách.
T05 do AI hỗ trợ có phần tác giả còn trống, không có author attestation mới.

J/gap/contrast mới chỉ tính trên synthetic toys: canonical, E2/E5/E7, các plant ngẫu nhiên,
teaching cell L1.8B. E3/E6 được ghi là arrival-law toys ngoài D7; không đổi mode timing D7.
Không chạy engine J/gap/contrast trên bất kỳ ô M/R/N/P/W/S nào của grid v1.2.
Migration Part4 §11 chạy **D-only** trên M01/M09/M22/N01/N02/N03/N04/W01, hai queue,
ref1/2 (32 trường hợp khác nhau; cả test và replay); so unit/mass/support/error với queue_D
gốc. Adapter đọc metadata cả58 records; không dùng p_sw/λA riêng held-out làm features.
Không dựng D held-out. Full regression còn rerun D-only L3.1 và screen M31 đã exposed.
Vì thế không nhận toàn phiên là “không dựng D grid”; ngoại lệ D-only được DL-045 ghi trước.

Mutation chạy trong temporary copy, chỉ toy/D-only và git fixture, không thay source gốc.
L3.3 chưa commit; không khóa K5/H1/null/split, không A01/A04/A05, không thay nhãn PC/G1.
[Config/seeds](../results/lessons/l3_2/config.json) · [report](../results/lessons/l3_2/report.md).


## L3.3 / A03 — 27/10/2026

Doan Van Tai phụ trách. Tác giả chọn hai mức K5 và trực tiếp xác nhận đã tự hoàn thành
read-back already_implied kín sách + engine/T05 ngoài repo (author-attested, DL-048;
[nguyên văn](../results/lessons/l3_3/author_attestation.json)). Không có transcript/mới,
không ghi phần AI hỗ trợ thành tác giả viết. Reviewer là AI tự kiểm cùng phiên, không độc lập.

| Artifact | Commit / content / tag | Exposure tại lúc viết |
|---|---|---|
| A03 card | commit `b05ed70bd4e93544bccefc975cdc452ad40d1380` · sha256 `14021a83c6d45a3fbeba6b7cbe27e9c8c0e572734557af1598cf79b819f34639` · tag `a03-card-v1` | AI-assisted forecasts đã exposed24/10; không J, độ lớn gap, margin, contrast hoặc regret grid trong record hiện có. Dấu gap đã exposed qua screen thiết kế; không nhận “chưa thấy gap” phủ nhận sign exposure. |

Chỉ toy outcomes (E8,16 mode-persistence rows,4000 synthetic ledgers và các witness/countermodel),
metadata whitelist50 main/held-out records. Không đọc actual p_sw/lambdaA held-out làm features,
không dựng D mới hoặc gọi engine trên grid trong phần L3.3. Full regression vẫn rerun D-only
và design screen M31 cũ; không gọi toàn phiên là “chỉ toy”. Giữ nguyên claims.md từng byte.
P2/P3/P5/P6 là forecast không cơ chế; PC1 sanity, PC4 deferred. Mở rộng K5 có quyết định
trước outcome; optionalP2/P3 chưa adopt. Không chọn H1/null/K5 theo kết quả. Không A01/A04/A05.
[Card](phases/PHASE_3_prediction_card.md) · [receipt](phases/PHASE_3_prediction_card.lock.json).

## L3.4 / A01 — 27/10/2026, DL-050–053

Doan Van Tai phụ trách, AI triển khai theo lesson. Không author-attestation mới
cho tự kiểm L3.4 hoặc tác giả tự viết predictions WD. A03 card/receipt/tag đã khóa
trước mọi cost run A01; prereg81233ef trước run01 và source receipts sau các fixes.

- Run01 `20261027_01`: Part0 M01/M09/M22 ref1/2/4 chỉ public p_sw; PartA baseline
  ledgers/control variants ba calibration ref1/2 (gồm EΔ,Δhat expectations, L/G,
  D22/V), N01/ref1; STOP C5 FAIL, chưa PartB. N01 diagnosis chỉ ô đã fail.
- Run02 `20261027_02`: Part0/A đủ các biến thể C1/C2/C3, N01–N04/W01/S01/P01/P02
  ref1/2; PartB M01/ref1/2/4 hoàn tất, ref8 đã tính nội bộ tới precision trước
  interrupt, **không complete output**. Giữ console/partial JSON; không nhận run02 PASS toàn A01.
- Run03 `20261027_03`: tính mới toàn Part0/A, PartB **M01/M09/M22 × ref1,2,4,8,16**,
  L/contrasts/gap expectations/quantiles/e_num/actions/certificates đã exposed.
  C1 dựng lại D khi u=0; C2/C3 lộ contrasts thật. Controls/probes mọi ledger
  ref1/2 nay exposed. 15cell-level/12pairs PASS, dt cuối1/240s chọn theo prereg,
  không chọn theo card. Không chấm forecasts hoặc thay card bằng kết quả calibration.

Ba calibration vẫn được chấm ở A04 theo đúng card tại dt cuối; ngoài card chỉ
là discovery, không confirmation. Toàn bộ contrast/diagnostics của chúng đã thấy;
không giả còn blind. 35main còn lại chưa được A01 tính costs. Full regression vẫn
rerun D-only và design screen M31 vốn đã public. Không D/outcomes held-out mới.
A04/A05-F/A05-T chưa thực hiện; không chọn H1/null theo A01. V9 chưa gửi/A04 chờ,
L8/P0-V10/T05 author-writing không tự đóng. [Report](../results/lessons/l3_4/report.md),
[manifest](../results/A01/20261027_03/manifest.json),
[failed run](../results/A01/20261027_01/run_status.json),
[interrupted run](../results/A01/20261027_02/run_status.json).

## Tiếp nhận review trước A04 / DL-054 — 27/10/2026

Tác giả cung cấp bản AI mock review chỉ truy cập remotef72306f; bản gốc/provenance
ở `notes/reviews/2026-10-27_pre_A04/`. Đã đọc các gợi ý phân lớp a00=a01, ref4,
F/V dt diagnostics, flip mass, miền cheap-kill và các alternative explanations.
Đây là exposure về luật đọc/giả thuyết và đề xuất trước A04, sau khi đã thấy
calibration A01. Không coi chúng là cơ chế blind hoặc yêu cầu đã adopt.

Đã kiểm lại nguồn A01 local/card/hash/51artifacts và nhận xét đại số trên ledger
toy; không chạy D/cost/contrast mới trên main/held-out. Không replay20.000toy
reviewer báo;336tests/11mutants là evidence cũ của A01. Không chấm card A04.

DL-054 ghi waiver của tác giả cho điều kiện chờ memo trước A04. Memo chưa gửi,
không có phản hồi GVHD thật/human validation mới. Human-reading/Phase4 giữ nguyên.

## DỰ THẢO exposure A04 — CHƯA CHẠY

Phạm vi dự kiến:38main và controls theo prereg sẽ được chốt; không R01–R12.
M01/M09/M22 mọi ref1–16 đã exposed trong A01;35main khác chưa có A01 outcomes.
Primary dt dự kiến1/240s, kiểm pair1/120→1/240 từng ô; các diagnostics bổ sung
phải được chốt trước computation liên quan. Không gọi phần discovery là held-out
confirmation. Trước run cần thêm prereg commit/source/config/hash và run-id thực;
sau run mới ghi các outcomes thực tế đã thấy, kể cả FAIL/HOLD. Không điền trước
kết quả cho38ô hoặc ngầm nhận draft này là đã chạy A04.

## L3.5 prereg — trước outcomes A04, 27/10/2026

Hai phần lesson đã đọc đầy đủ; code/tests dùng dữ liệu synthetic. Prereg và
exposure chính ở `experiments/A04_discovery/prereg.md` / `exposure_plan.md`.
Chọn trước ba miền cheap kill core/spoke_A50/spoke_h2, không thay card.
A01 calibration/control exposure giữ như lịch sử. Trong phiên chuẩn bị đã mở
toàn bộ `grid_v1_2.md`; bảng public held-out gồm lambdaA/p_sw thiết kế đã hiện
trên tool output. Không dùng chúng làm features H0/H1; không phát sinh D, J,
regret/contrast held-out. Không ghi blanket “chưa thấy metadata held-out”.
Full regression tái kiểm D-only/screen đã public; chưa outcome A04 mới.
Run dự kiến `20261027_01`: 38main+8controls/probes, ref1/ref2; validity trước,
score commit trước discovery. Timestamps và SHA thực sẽ nằm trong manifest.

## A04 thực chạy và discovery — run27/10, tổng kết28/10/2026

Doan Van Tai phụ trách. Prereg56c4141/receipt0eb42f2; run20261027_01 bắt đầu
2026-10-27T16:17:22.192539+00:00, kết thúc2026-10-27T16:17:53.051031+00:00.92lượt đủ38main+8controls/probes×ref1/ref2.
Đã đọc validity trước;score commit7005a3b trước mở cells.csv/discovery. Raw/intervals/
D22/R04/quantile và sáu contrast của mọi ô này đã được tính,xem và báo. Không
chọn lọc ô thuận lợi,không overwrite hoặc đổi thresholds để cứu P2/P3/P6.

Từ sau checkpoint: phân tích bảng,hìnhH1–H3,ba miềncheap kill,5phát biểu ghi đầy
đủ trong patterns.md/190rows;giữ1candidateC1 hậu discovery. Không forecast mới
được chấm cùng A03. Tọa độ R03–R08 được đối chiếu eligibility/carry;khôngD/outcome.
Public held-out λA/p_sw cũ đã hiện ở bước đọcgrid.md như mục prereg ghi,không
nhận chưa thấymetadata và không dùng chúng làmfeaturesH0/H1. Held-out J/gap magnitude/
regret/contrast vẫn chưa tính/xem;không mởA05-T.

Phiên reviewAI riêng chỉ xem card+bốnraw củaM09/M17 ởhai dt,không nhãn grader
trước khi tính;2/2khớp. Không human/GVHDreview hoặc readback author-attested mới.
Đã dùng skillpaper-research,sàng20title/snippet/2keywordqueries sau outcomes,
lookupprimary2nguồn:arXivabstracts,crossrefmetadata;khôngPDF/fulltext/newpaper-note.
1proposal chờduyệt;catalog/author progress không đổi. Tìm kiếm này là post-discovery.

[Note A04](lessons/L3.5_A04_note.md) · [manifest](../results/A04/20261027_01/manifest.json) ·
[scores](../results/A04/20261027_01/card_scores.json) · [pattern log](../results/lessons/l3_5/patterns.md).


## L3.6 chuẩn bị — trước quyết định D25/prereg,28/10/2026

Doan Van Tai phụ trách. Đọc/archive review và Parts1–3 L3.6. Review tựbáo348tests/
74s không được chép thànhlocal evidence. Đã audit lại A04/currentguards,38ô/20lát,
headroom vàbase rates,tái dựngidentity;không tínhD/outcome gridmới. GaussianMC
4triệu mẫu và100.000toyD chỉ dữ liệu giả;seeds/tham số/log lưu riêngpreflight.
358tests/60s là local runmới;regression tái kiểm D-only/screen đãexposed trướcđó.

Đã đọc tọa độ/nhãnheld-out ngay trong lesson được cung cấp;chưa tải recordgrid
held-out mới vào feature module,chưaD/cost/gap/contrast held-out. Khôngp_sw/λA
held-out mới được tính;exposurepublicmetadata cũ vẫn giữ. Đã hỏi tác giả hai
quyết định D25/phạm vi;chưa có câu trả lời,không giảđã chọn. A05-F chưa freeze.
[Report](../results/lessons/l3_6/report.md) · [audit](../results/lessons/l3_6/preflight/a04_audit.json).


## L3.6 sau tác giả chọn DL-057 — trước fit/predictions (28/10/2026)

Tác giả chọn D25(ii) và thiết kếA đầy đủ, giao chốt chi tiết trong prereg.
Đã commit author decision51c926f trước prereg. H0/H1 cùng12hệ số,2candidate,
2start;rho0;LOSO20lát;metricchínhMAEđều GS/GM/Gamma,margin.25điểm%Cref.
Các công thức/numerical gates/conditional opening đã viết trước khi tạo θ/dựbáo.
Unit tests feature chỉ sanitize38main;không load held-out record vào features.
369fulltestsPASS/60.31s,21targetedtestsPASS;không fit thực38ô trướcpreregcommit.
Nguồn A01/A04/cardgiữnguyên. KhôngD/cost/gap/contrast held-out mới.


## A05-F — dự báo đã khóa, chưa outcomes (28/10/2026)

Prereg 57d84c66fc2cfca6de6fbbda662918959cd99fc5,theta 6aa696a958ec0ee09242812c94762a0f42927f89,predictions 3c75aecd720ef688923d818bc41f3db4a82742ec.
Fit38ô đãexposedA04,80LOSO+2fullfits,164solverstarts;thetađãcommit trước
featureR. Đã đọc/tính/xem sanitizedmetadata vàfeaturesbậc0–2của cả12R lúc
2026-10-28T00:50:16.694515+00:00,gồmλAđượcphéptheoDL-057;khôngp_swactual,cost,gap hoặcCrefR.
Khôngbậc3/Dheld-out. Không gọi bước này là hoàn toànchưađụngmetadataheld-out.

ĐãxemdựbáoGaussian của12R vàD3nhóm saukhicodemodel/config/preregđãcommit.
Không thaychoice/model/threshold/metric/split sau đó. Dweak=.2123<margin.25 nên
R09/R10không cần mở;outcomeIDsplanned10củaunionnhánhđãkhóa. ChưarunA05-T,
chưaJ/Delta/bias/margin/headroom/regret/contrast thật củaR,khôngfitbằngtest.
K5m=1nguyênvăn;C1postdiscovery riêng;khônggộptỷlệthànhcông.

[Predictions](../experiments/A05_freeze/predictions_heldout.json) ·
[Discrimination](../experiments/A05_freeze/discrimination.json) ·
[Features](../experiments/A05_freeze/features_heldout.json).

## A05-T — quyết định mở, ghi trước run (28/10/2026, DL-059)

`A05-T_OPENING_DECLARED` · 2026-10-28T08:31:52+07:00. Các ô **R01–R08, R11, R12** được
mở cho A05-T, đúng một lần, sau commit này. Lúc commit: chưa có D, J, gap, contrast,
regret hay C_ref của bất kỳ ô R nào; không có `results/A05_test/`. **R09/R10 giữ niêm
phong**: không D, không outcome. Sau run, 10 ô đã mở trở thành dữ liệu đã thấy; giả
thuyết mới nảy ra từ chúng cần dữ liệu khác (Phase 5). AI theo ủy quyền, không human review.

## A05-T — sau run (28/10/2026, DL-060)

Run `results/A05_test/20261028_01`, một lần, exit 0. Đã tính và xem: D, cost, gap, contrast,
regret, C_ref, R00, diagnostics của **R01–R08, R11, R12** ở ref 1 và 2. Mười ô này nay là dữ
liệu đã thấy, không còn dùng được để kiểm giả thuyết mới. **R09/R10 vẫn niêm phong**: không D,
không cost, không outcome. Chuỗi "R10" trong output là khóa regret R10, không phải ô.
Đọc verdict sau khi chấm bằng scorer đã khóa; không đổi model, metric, dt hay danh sách ô.

## Review A05-T và L3.8 — sau dữ liệu, 28/10/2026

Đã đọc hai lesson L3.8, source/provenance, status, verdict và report đã có. Phiên review
trước đã chấm lại dữ liệu A05-T đã lưu; artifacts ở `results/reviews/l3_7_20261028/`.
L3.8 kiểm hash/chronology, full-suite regression391tests và rescore saved data; không
gọi runner A05-T, không tính D/cost/outcome grid mới, không mở R09/R10. Regression
có các toy/design checks đã exposed trước; không nhận hoàn toàn chưa thực thi phép tính.

Mọi đề xuất Gate/diễn giải mới trong phiên này đều **sau dữ liệu**. Khuyến nghị NARROW
của AI không được adopt: tác giả chọn REFORMULATE ở DL-061 và ủy quyền viết ngôi “tôi”. Không bổ sung
hồi tố kỳ vọng trước A05-T, không nhận người thật/GVHD đã đọc hoặc Understanding PASS.
Các source/card/threshold cũ giữ nguyên; 10 ô đã mở không còn là test sạch cho claim mới.
Contract/briefv1.3 chỉ là proposal nhiều observations chưa khóa; không mở R09/R10 hoặc
tính outcome mới để chọn law/weights. Hai đoạn ngôi “tôi” là bản sau dữ liệu theo
ủy quyền, không thành kỳ vọng trước run/tự viết/author-attested Understanding.

## v1.3 bước 1 — khai trước run (28/10/2026, DL-062)

`V13_STEP1_DISCOVERY_DECLARED` · 2026-10-28T18:24:00+07:00. Sau commit này sẽ tính lại bảng D và các thành phần
gap theo từng state (δ, δ̂, e_M, khối lượng fluid chạm rỗng, cửa sổ gần biên) của **38 ô main ở
ref 2**. Các ô này đã lộ ở mức tổng hợp từ A04; chi tiết theo state là exposure mới, cùng ô, nhãn
DISCOVERY. Không ô R nào được tính lại; R09/R10 vẫn niêm phong. AI theo ủy quyền, không human review.

## v1.3 bước 1 — sau run (28/10/2026, DL-063)

Run `results/V13_step1/20261028_01`. Đã tính và xem theo từng state, ở mức tổng hợp mỗi ô: khối
lượng fluid chạm rỗng, thành phần gap trung bình mỗi phía, G_M|S1 tính lại, lens biên của **38 ô main**.
Không ô R nào được tính lại; R09/R10 niêm phong. Kết quả là DISCOVERY trên dữ liệu đã lộ.


## Phase 3R / L3R.1 — khai trước đếm lại pilot (2026-10-28, DL-064)

`R3R1_RECOUNT_DECLARED` · 2026-10-28T21:35:45.066305+07:00. Người phụ trách: **Doan Van Tai**.

Đã lộ trước khai này: pilot ở a7435e9 và các bảng/errata trong lesson Part1, ZIP và
preview report được cung cấp. Theo nguồn, Stage2 thích nghi sau Stage1, chỉ báo M0
chọn hậu nghiệm trong5; lần reviewer tính bảng Part1 và recount trước đây là
**reviewer-reported**, không chép thành lần chạy local hoặc tác giả tự đọc raw.
Trong phiên trước đã đọc plan/SUMMARY/report Step1; phiên này đọc đầy đủ script,
preview và hướng dẫn ZIP. Chưa tính lại raw tại máy này trước khai báo này.

Sau commit này và tag remote: chạy script một lần từ tag, chỉ git-show 5 CSV,
SUMMARY và grid v1.2 (chỉ tham số, kể cả R09/R10). Các kiểm thêm trùng cấu hình,
trùng tọa độ, thang pctS, ghép Stage3 và bảng Part1/rubric đã khai trước ở prereg.json.
Các bảng vẫn là DISCOVERY/verification dữ liệu lưu; không gọi engine, không D/J/contrast
mới của main/R/CF. Tham số R đã public trước đây không đồng nghĩa mở outcome niêm phong.

Số210 cấu hình,45 trùng tọa độ… trong preview hiện là số nguồn báo, chưa là kết quả
local; sẽ đối chiếu và ghi sau run, giữ cả sai lệch nếu có. Không khẳng định đã tự
làm bài kín sách/đọc từngCSV chỉ vì yêu cầu triển khai theo ủy quyền.


## Phase 3R / L3R.1 — sau đếm lại (2026-10-28, DL-064)

Ghi lúc 2026-10-28T21:50:17.714926+07:00. Run `results/R3R_01_recount/20261028_01`, đúng một invocation
local, subprocess exit0. Đã xem bảng30ôSUMMARY theo stage; E1–E7;6cặp trùng;45ID
trùng tọa độ23ôv1.2; ghép Stage3, mappingeta, thangpctC/pctS, bảngPart1 theoID và
cấu hình, rubric diagnostic. Tất cả thuộc phạm vi đã khai, vẫn là DISCOVERY.
Không engine/new regime/CF outcome; grid R09/R10 chỉ tham số public. D22 và chỉ báo
M0 chưa có phép tính/tái lập mới. Script/source raw/README SUMMARY ở tag không thay.

Tag được tạo trước commit khai trước do bước kiểm định dạng chặn commit ban đầu;
cả tag và khai trước đã push trước đếm. Output khớp ZIP ngoàiRev; controller kiểm
bản paste dừng vì thiếuEOF newline rồi phục hồi metadata, không rerun hoặc đổi3file
máy sinh. Hai khác biệt đã công bố ở [report](../results/lessons/l3r_1/report.md).
[Discovery record](phases/PHASE_3R_discovery_record.md) ghi số local đã xác nhận.

Người phụ trách: Doan Van Tai; tổng hợp theo ủy quyền, không xác nhận tác giả tự làm
kín sách/đọc hết raw hoặc human review mới. Understanding/P0-V10/L8/T05 giữOPEN;
V9 giữWAIVED_BY_AUTHOR, thực thiPhase4 HOLD. Không nângG1 hoặc gọi210cấu hình là mẫuIID.


## Phase 3R / L3R.2 — theory và golden reference (2026-10-28, DL-065)

Ghi lúc 2026-10-28T22:59:28.587036+07:00. Người phụ trách: **Doan Van Tai**. Đã đọc ba phần lesson được cung cấp,
T01, contractv1.2, draftv1.3 và plan§9. Đã biết các discovery pilot/Step1/L3R.1 trước
định nghĩa này; mọi lựa chọn v1.3 tiếp theo là sau pilot, không gọi là pre-pilot.
Không mở code engine population để viết golden. Chỉ toy hữu hạn được cung cấp và
8 kiểm bổ sung (500 laws seed20261028, cùng tập được dùng lại cho bound), không
new-regime outcome, R09/R10 hoặc CF. Không khảo sát literature mới.
T07 soạn theo ủy quyền, self-read-back chưa có xác nhận; Understanding OPEN.


## Phase 3R / L3R.2 — sau golden run (2026-10-28, DL-065)

Ghi lúc 2026-10-28T23:02:37.144963+07:00. T07 source315d203 trước run. Đã tính các toy hữu hạn: GM=.24,
harm GS=−.5/Γ=.5; biến thể GS=.5/Γ=−.5; D22 mode/backlog/triệt tiêu và hai ratio 1%/5%.
16 golden/439 full tests PASS; 500 joint laws seed20261028/0 vi phạm; 5/5 mutant KILLED.
Cùng 500 laws được replay, không cộng số plant theo số lần gọi. Không mở code engine
population, không tính outcomes pilot/regime mới/CF/R09/R10. Full suite gồm regression
engine v1.2 cũ trên toy, không phải population audit. Đối chiếu aggregate L3R.1 đã lưu
cho số 79/162 Stage1+2, không đếm lại raw. Không khảo sát literature.
Kết quả là reference verification, không hypothesis confirmation; law/primary/εR
v1.3 vẫn OPEN và sẽ là lựa chọn sau pilot. [Report](../results/lessons/l3r_2/report.md).
Người phụ trách Doan Van Tai; Understanding/P0-V10/L8/T05 OPEN, Phase4 HOLD, G1 giữ nguyên.


## Phase3R / L3R.3 — khai trước audit (DL-066)

2026-10-28T23:15:51.002242+07:00. Đã đọc đủ4lesson,codepilotpopulation/19tests,queue_D/law_for,physical/ledger
v1.2vàcut_value; chưa chạy engine mới. Snapshotpilot a7435e9,8regimes
X2065, X2029, X2041, X1001, X3001, X1008, X2012, X1009. T1–T7/12mutants/MC/refinement/repro khai trongprereg.
Dải318300000–318399999 chỉaudit; C3pilotN2048,chọnNtheoluật trướcfinalrun.
Phiên MC độc lập không được xemengine; tác giả không được ghi đã tự viết/read-back.
R09/R10/CF không mở; v1.3law/numericschỉproposal.


## Phase3R / L3R.3 — sau audit (2026-10-29, DL-068)

Ghi 2026-10-29T07:24:06.679220+07:00. Đã tính J/gap/loss/contrasts mới trong8regimes discovery đã khai:
X2065,X2029,X2041,X1001,X3001,X1008,X2012,X1009; đã nhìn T2/T3/T6,ref/K levels,
MC C1–C3. Tái lập18robustness IDs(cùng9tọa độ)+X2065 từtag,không CF/R09/R10.
K320 và X2065precision extension được khai sau quan sát, trước lần bổ sung; originals
UNRESOLVED/failed/partial giữ nguyên. Dảiseed318300000–318399999 chỉverification;
[used seeds](../results/lessons/l3r_3/used_seeds.json) ghi roots thực trongreceipts,
không nhận toàn bộdảiđãrút hoặc nhân sốepisode vì replay. Full467tests+19oldtoy,
12mutants,19repro PASS; đây làverification trongplant, không hypothesis confirmation.
T07/code map soạn theoủyquyền; không human read-back mới. AuditHOLD, G1/Phase4HOLD,
v1.3DRAFT,Understanding/P0-V10/L8/T05OPEN. [Report](../results/lessons/l3r_3/report.md).


L3R.3bổ sung: đã chạy X2065ref2,K80 theo one-step escalation khai gốc; maxdelta so
K40=.050360895ppC, không signflip. Đây cùngregime discovery đã lộ, khôngCF mới.
Sau interruption đã giữ12jobrepro trước và hoàn tất7job còn lại từ freshclone/venv
khác cùngsource/deps;19lầnchạy trên9tọa độ,57.808pairs khớp. Không rerunengine để
sửa schema-checker; archivedStage2 thiếuc_sw chỉ kiểm metadata0 vớispec.


## Phase3R / L3R.4 — trước bảng216, DL-069 (29/10/2026)

Đã đọc đủ3lesson(848lines), T00/DL008/protocol, metadata9Crossrefrecords/0DBLP,
nguồn mới3được duyệt rồi targeted-primary-read. Không tác giả L-self. A1generic
3singlequeues λ8/T.1,λ8/T.3,λ9.5/T.1;24seeds generic đã khai,18comparisons;
không newregime gain. Chuẩn bị stationary-only X2041/X2012/X1009,Apre/Bpre,ref1/2.
Envelope/luật phải commit trước216design translations và labels; labels checkpoint
phải commit trước saved-discovery overlay. CF/R09/R10 không mở.


## Phase3R / L3R.4 — sau screen, DL-070 (2026-10-29T08:12:02.140485+07:00)

Đã dịch tham số216ID(210distinct),hai anchor minh họa10ms/100ms,432feature rows;
1296labels(context×f),không1296designs. Envelope6bef959 trước run;exportfix830a187
giữrules;labels1164500 trước overlay. Đã đọc lại saved rawstage1–3 từpilot taga7435e9
choMV20/SH80/giao14,không outcome mới. Stationary-onlyX2041/X2012/X1009,Apre/Bpre,
ref1/2:atom/mean/tail,khôngJ/gap/action/regret/newcontrast. Full491tests gồm regression
toy cũ;khôngrunA05-T hoặcCF/R09/R10. Reviewer riêngchỉenvelope/worksheet/rules/labels/receipt.
Ba nguồn mới approvedAI-T,khôngauthor-selfread. Buffer/d_act thựcchưađủnguồn;range
misalignment ghiworksheet. MV/SH đềuHOLD_UNSOURCED;G1,Phase4HOLD giữ.


## Phase3R / L3R.5 — contract/schema only (2026-10-29T09:17:41.162857+07:00, DL-071–072)

Đọc4lesson vàlocalcontract/T07/DL/auditstatus. Tácgiả đã chọnP1,metric/ngưỡng,
D22commitment,tagA trướcadoption. Chỉ đọc5design specs.json từpilot taga7435e9,
234metadatarecords;khôngđọcmớipilotoutcomeCSVđểchọnthước hoặcđếmPASSphươngán.
3D22toyexactreplay vàRoE/P2a/numerical-ruletoy;đơnvịtoycost,khôngnetworkmeasurements.
41targeted/532fulltestsPASS,gồmregressiongoldencũ,khôngnewresearchregimeoutcomes.
Tagcontract-v1.3→3d2359b;CFgenerated0,newMC/simulation0,newseeds0.
R09/R10khôngmở,khôngpilotmerge/srcpromotion,khôngpapersearch/download/note mới.
D22physicalpath/numlevelsDEFERRED,auditL3R.3HOLD,realismHOLD_UNSOURCED;
G1,Understanding/P0-V10/L8/T05OPEN,Phase4HOLD.


## Phase3R / L3R.6 — trước bảng discovery vẽ vùng (2026-10-29)

Người phụ trách: **Doan Van Tai**; triển khai theo yêu cầu L3R.6. Đã đọc lesson Part2/Part3
(Part1 bị cắt từ §9.2). Lesson đã cho xem4bảng discovery pilot (mục0 forking log). Công cụ
`experiments/R3R_06_cards/` commit trước: luật vùng chỉ đọc DesignView, mọi tóm tắt outcome tự
ghi `results/lessons/l3r_6/forking_paths.jsonl`. Sẽ đọc lại saved raw stage1–2 (c_sw0,162cấu hình)
tại taga7435e9 để tái lập bảng lesson và đếm12luật ứng viên đã khóa trong code. Không engine,
không regime mới, không CF/R09/R10 outcome; tọa độ R09/R10 chỉ dùng kiểm luật có chạm hay không.
