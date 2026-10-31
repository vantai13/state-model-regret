# State × Model — giá trị cải thiện quyết định routing

Tác giả: **Doan Van Tai**.

**Hiện tại — L4.8 scope: use case/domain đã ghi; empirical realism cònUNRESOLVED (DL-120).**

Chọn narrativeDC-inspiredone-shotaggregatesteering trong frozenplant;không
nhậnproductioncontroller. Reread3nguồncũ,15targetedPDFpages,0newpaper/PDF.
597designkeys được kiểm schema/quyđổi units,khôngsimulation. Anchor10Gb/s,
tau10mschỉminhhọa:managed1–1.75Gb/s,h10–160ms,mộtmodelbacklogunit=1.25MB
fluidwork. Khôngbiếnscalingthànhempiricalvalidation hoặcgánIN/OUTkhi thiếu
jointmeasurement.12new/942fulltestsPASS. SUB/CFpark,D22nativeDEFERRED,G1giữ.

[Report/trạng thái thật](results/lessons/l4_8_v2/report.md) ·
[Declared domain](notes/realism/declared_domain_l4_8.json) ·
[Source review](notes/realism/L4_8_source_review.md) ·
[CSV/JSON](results/lessons/l4_8_v2/projection/summary.json).
Khôngcófulllesson4.8mới;đây làscope roadmap,khôngtựđóngGate4. L4.9chỉđược
chuẩnbịpredictioncóđiềukiệntrênmodel;empiricalclaimscònthiếuevidence.

**Snapshot L4.7 (v2): P-clip đã chứng minh/kiểm native; predictor có giới hạn (DL-119).**

34tests mới/930fulltestsPASS. NgoàiClip24/24statechecks cód=dh;96per-action
JensenchecksPASS. Diagnostic50discoverykeys hoàn tất trong34.53CPU-s,không
tạo nativekernels/fullregimerun mới. P_clip=.996476–1; S_clip/sigma=1cả50điểm
và làidentity của primaryc_sw0/totalbacklog, không phải predictor mới. Rawrank
correlations chỉdescriptive, chưaheld-out. Giữ8rawflags, G1/UnderstandingOPEN;
SUB/CF vẫnpark, nativeD22DEFERRED. Tiếp theo **L4.8realism**.

[ProofT08](notes/theory/T08_clipping_anchor.md) ·
[Report](results/lessons/l4_7_v2/report.md) ·
[CSV/summary](results/lessons/l4_7_v2/analysis/summary.json) ·
[Plot](results/lessons/l4_7_v2/analysis/predictors.png).

**Snapshot L4.6 (v2): đã tách nguồn và vẽ3hình trên discovery (DL-118).**

1.136pilot rows→1.118unique;597native keys(497SV+90MV/SH+10SUB đã park).
Trên449SV+, medianGS|M1=1,169907%Cref, medianGS=.969564%; AB pilot có
GS|M1q10–q90=.026992–2.583081%, không đồng nhất. Giữ mọi raw flags/negative
estimates; không chứng nhận numerics đã giải quyết. D22 native cònDEFERRED:
hướng dẫn trộnP(mode|Q) bỏY khác contract(Y,Q), đã kiểm bằng stationary toy.
Không engine/CF/R09/R10 outcomes mới; SUB/CF-v2 vẫnpark, G1/UnderstandingOPEN.

[Báo cáo/số đo](results/lessons/l4_6_v2/report.md) ·
[CSV](results/lessons/l4_6_v2/analysis/rows.csv) ·
[P1](results/lessons/l4_6_v2/analysis/P1.png) ·
[P2](results/lessons/l4_6_v2/analysis/P2.png) ·
[P3](results/lessons/l4_6_v2/analysis/P3.png).
Tiếp theo **L4.7 clipping**; không coi plots là evidence cơ chế hoặc realism.

**Snapshot L4.5 (v2): đổi loại evidence, SUB và CF-v2 đã park (DL-117).**

Chọn **0 card mới trong hướng hiện tại** vì chuyển sang tách nguồn, mechanism
và held-out điều kiện; đây không phải kết luận SUB FAIL. Giữ SV FAIL_SCREEN,
baseline A3 (MV rho5%/narrow; SH rho0/not-narrow) và mọi artifact lịch sử.
SUB giữ10/76keys đã hoàn tất làm discovery; tiến trình cũ đã kết thúc khi đang
STOP, không chạy66keys còn lại.270CF-v2 vẫn chỉ là tham số, chưa có outcomes;
gói đó được park để xem lại riêng như kiểm phụ. Contract/card/engine frozen giữ
nguyên byte. Không có thí nghiệm hoặc evidence mới từ lesson này, G1 giữ nguyên.

[Phase4 v2 — bản triển khai tối thiểu](notes/phases/PHASE_4_v2.md) ·
[DL-117](notes/02_decision_log.md#dl-117--l45-v2-đổi-loại-evidence-park-sub-và-gói-cf-v2-31102026) ·
[Parking](results/lessons/l4_5_v2/parking.json) ·
[Báo cáo/kiểm chứng](results/lessons/l4_5_v2/report.md).
Tiếp theo: **L4.6 tách nguồn trên dữ liệu đã có**, chưa chạy trong lesson này.

**Snapshot trước DL-117 — các trạng thái bên dưới được giữ nguyên lịch sử.**

**Hiện tại — L4.5 Part B: SV FAIL_SCREEN; SUB tạm dừng theo yêu cầu.**

SV đã sàng đúng một hộp trên support A1: plus 216 MEETS/224 FAILS/9 UNRESOLVED
(449 keys), minus 0 MEETS/48 FAILS. p_cond=49,09%, r_plus=2,00%; sau haircut
p_plan=39,09%, planning power≈0,0000257: **FAIL_SCREEN**, không thử hộp khác.

SUB đã khóa một hộp 76 keys và dùng nguyên runner A1. Hiện **10/76 keys hoàn
tất (10 PASS), 2 đang tính dở, 64 chưa bắt đầu**; job đã SIGSTOP, không chạy
thêm CPU. SUB chưa có full summary, rho*, manifest hoặc screen. **Số card chưa
quyết định**, không suy 0 card từ việc tạm dừng. Chỉ resume khi tác giả yêu cầu.

880 full tests PASS; 17 screening tests PASS cả trước và sau SV screen.
[Report](results/lessons/l4_5/part_b/report.md) ·
[SV result](results/lessons/l4_5/box_trials/SV/trial_01.result.json) ·
[SUB checkpoint](results/lessons/l4_5/part_b/SUB_checkpoint.json) ·
[Pause/resume](results/lessons/l4_5/part_b/pause.json).

**Snapshot A3/B1, 31/10/2026: MV và SH đều STABLE; kết thúc nhánh numerical.**

Đã chạy đủ 90 keys × 3 levels và một control, giữ cả 36 điểm SH NOT_READY.
Cả ba mức chọn MV ρ*=5% với narrow=True (median R_M 0,86297–0,86799),
SH ρ*=0 với narrow=False (median |GSθ|/Cref 4,67960–4,70197%; ΔL10=0).
879 full tests PASS; replay 12/12 và đối chiếu Fraction độc lập PASS; 0 BUG.
Tổng 1.934,611542 evaluation CPU-s. Dùng nguyên runner A1 và luật DL104.

STABLE chỉ là robustness ở ba mức đã kiểm, không phải numerics từng point đã
solved. Không A4 hoặc refinement thêm để cứu kết quả. Chuyển sang L4.5 Part B
với evidence còn sống và rho policy đã chốt; SV/SUB giữ nguyên, G1.
[Report](results/lessons/p4_a3/report.md) ·
[JSON](results/lessons/l4_4/a3/summary/b1_summary.json) ·
[CSV](results/lessons/l4_4/a3/summary/level_summary.csv) ·
[Rho policy](experiments/P4_A1/runs/L44_A3/rho_freeze.json).

**Snapshot P4-A2, 31/10/2026: probe hoàn tất, nhánh B1; F1 baseline vẫn HOLD.**

Đã chạy đủ 8 điểm × 7 levels và một control u=0: 57 evaluation calls,
1.280,950894 CPU-s, dưới cap 3 CPU giờ. Control PASS, 24/24 row tái lập A1 khớp,
0 BUG/mismatch; audit độc lập PASS. Có 2/8 điểm từng READY, với số READY theo
ba bậc là **0 → 2 → 0**. Hai điểm P44_006/P44_007 lại fail ở bậc cuối.
Theo ngưỡng khóa trước run, áp **B1_CLAIM_LEVEL_ROBUSTNESS**; chưa chạy A3,
chưa chọn ρ* hoặc tính regional medians. 870 full tests PASS (86,83 s).

A3 cần prereg riêng và full 90 điểm, so ρ*/luật đọc giữa ba mức theo B1.
SV/SUB giữ nguyên; G1, L4.5 Part B, Gate 4, P0-V10/L8/Understanding còn mở.
[Báo cáo A2](results/lessons/p4_a2/report.md) ·
[Decision](results/lessons/l4_4/a2_probe/decision.json) ·
[CSV 8 điểm](results/lessons/p4_a2/point_summary.csv) ·
[Verification](results/lessons/p4_a2/verification.json) ·
[Completion](notes/phases/P4_A2_completion.json).

**Snapshot P4-A1, 31/10/2026: đã chạy engine thật; F1 baseline vẫn HOLD.**

842 full tests PASS (88,76 s), 3 controls PASS; rescore, export và 6 bộ receipt khớp.
L44 full dừng đúng cap ở 16/90 điểm (8 PASS, 8 NOT_READY); tổng 19 điểm đã quan sát
kể cả benchmark, 71 NOT_RUN, chưa chọn ρ*.
SV hoàn tất 497/497 điểm: 496 PASS, 1 NOT_READY. Trên 448 điểm SV+ READY, ρ*=1%;
median GS/Cref tăng từ 0,971841% lên 1,021545%, median ΔL00 dương: baseline không
thu hẹp SV theo luật đã khóa. SUB probe có 4/5 điểm native-ready; max bundle
164,405 CPU-s: chỉ đề xuất giữ κ≥0,05 để kiểm coverage tiếp.

Quyết định/dự đoán do AI soạn theo ủy quyền, không phải tác giả tự viết.
Không có CF/sealed outcomes hoặc box counts mới; L4.5 Part B, combined SUB,
readiness receipts và Gate 4 còn mở. G1 giữ nguyên.
[Báo cáo](results/lessons/p4_a1/report.md) · [CSV](results/lessons/p4_a1/measured_runs.csv) ·
[Verification](results/lessons/p4_a1/verification.json) · [Completion](notes/phases/P4_A1_completion.json).

**Snapshot L4.5, chốt 31/10/2026: Part A/rules đã khóa; Part B bị chặn.**
Tác giả giữ SV/SUB có điều kiện, duyệt luật robust/haircut.10/power≥.5/U≤5%,
tối đa3hộp/candidate (DL-105, lock624a9be). 16tests mới và813fulltests PASS82.29s;
14/14dòng power thiết kế khớp lesson, n60 cần≥39MEETS ởΩ⁺/≤21ởΩ⁻.
Chưa có hộp thực/p-hat mới, chưa chọn0/1/2card. Native/baseline L4.3–L4.4 còn
HOLD; không pilot proxy/CF/cardv3. Power là hypothetical, G1/cardv2 giữ nguyên.
[Báo cáo và số liệu](results/lessons/l4_5/report.md) ·
[Part A](notes/phases/PartA_candidate_filters.md) ·
[Luật sàng](experiments/P4_05_candidates/screening_rules.md) ·
[Completion](notes/phases/L4_5_completion.json).

**Snapshot L4.4, 30/10/2026: baseline chạy tới sanity HOLD.**
Tác giả duyệt margin+Stay/lướiρ/per-region selection và luật đọc trước plant;
forecast AI soạn theo ủy quyền. 18 targeted tests/200synthetic trials và797fulltests
PASS83.17s; u0 control thật PASS. Benchmark2MV PASS/1SH HOLD tạiP44_000/X2000:
ô00 gốc thấp hơn oracle0.000126276packet·s, vượt tổng arithmetic errors0.000099074.
Không full90/ρ*freeze; ledger2PASS/1HOLD/87NOT_RUN. L4.3 HOLD giữ nguyên;
G1, cardv2/verdict không đổi, khôngCF/newsealedoutcomes.
[Báo cáo/số đo](results/lessons/l4_4/report.md) ·
[Spec đã duyệt](experiments/P4_04_baseline/spec.md) ·
[Completion](notes/phases/L4_4_completion.json).

**Snapshot L4.3, 30/10/2026: HOLD theo điều kiện dừng đã đăng ký.**
Part A 14/14 replay và 126/126 trường khớp bit; 779 full tests PASS (100.17 s).
Native benchmark chạy 3/4 điểm, đủ 9 level rows: 2 PASS, 1 HOLD tại XM2X000
vì Cref lệch theo dt **0.310539% > 0.25%**. XM2S110 có point estimate A→D,
nhưng R6 còn UNRESOLVED. XA097 trùng physical key R10 được chặn trước native.
Giữ toàn scope 666 tọa độ/684 aliases; full audit, MC, CF và ca benchmark thứ tư
chưa chạy. G1, chưa dùng nhãn cho L4.5 hoặc đóng Understanding/P0-V10/L8.
[Báo cáo và số đo](results/lessons/l4_3/report.md) ·
[Pilot/native CSV](results/lessons/l4_3/report_data/pilot_native_metrics.csv) ·
[Completion](notes/phases/L4_3_completion.json).

**Snapshot L4.2, 30/10/2026:** hoàn tất phần kỹ thuật đọc map: 8/8 golden checks,
2/2 implementation mutants KILLED, 26 test mới và 757 full tests PASS (85.29 s),
10/10 numeric checks. 18/18 age pairs cùng lớp (max 0.200989 pp); AB không đồng nhất,
δ không phải luật tất định. T07 P4 là khung trống cho tác giả tự viết;
Understanding/P0-V10/L8 OPEN, G1. Chưa chạy native audit, CF hoặc bài optional A-by-δ.
[Report/log/metrics](results/lessons/l4_2/report.md) ·
[Reading note](notes/verification/l4_2/reading_note.md) ·
[Author template](notes/theory/T07_P4_author_addendum.md).

**Snapshot L4.1, 30/10/2026 (DL-103):** đã lập record regime map và exposure/forking#0;
tác giả chọn **v1.2: Phase4(hợp nhất discovery),5(confirmation),6(mechanism)**.
Recount1430→1376,54duplicate khớp;10/10checks,21test mới và731fulltests PASS.
Đây là discovery, G1; E11/E12 chưa audit native, mục tác giả tự viết/Understanding
và P0-V10/L8 còn OPEN. Chưa có outcome CF mới hoặc baseline/card mới.
[Report/số đo/log](results/lessons/l4_1/report.md) ·
[Record](notes/phases/PHASE_4_regime_map_discovery_record.md) ·
[DL-103/ánh xạ phase](notes/phases/PHASE_4_entry_decision.md).
Các mục dưới là snapshot lịch sử, dùng nghĩa phase cũ trừ khi có ghi ánh xạ.

**L3R.7 — tạm dừng theo yêu cầu tác giả, 30/10/2026 (DL-094):** native05 đã
kết thúc **HOLD**:286receiptsCOMPLETED,2lỗi JSONserialize ởCAL_CORNER_049/050,
6972.840511CPU-s,peak183.691MiB. Local701testsPASS/GCPpreflight693PASS;
2410exportfiles khớpSHA,3948same-levelcomparisons khớp trong arithmeticenclosures.
Không còn researchworker; temporarySSHrule đãxóa,VMvẫnRUNNING. **Lesson7 chưa
hoàn tất**, chưa v1.3.1/n/root/CF;Phase4HOLD. Các snapshot dưới đây là lịch sử.
[Báo cáo tạm dừng](results/lessons/l3r_7/pause_report_20261030.md) ·
[Metrics](results/lessons/l3r_7/full_numerics/native05/report/metrics.csv) ·
[Prereg](experiments/R3R_11_native_population/prereg.json).

**L3R.7 — bản đồng bộ ngày 30/10/2026:** đã lưu mã, thiết kế, prereg và các
kết quả hiện có. Lần kiểm hash này xác nhận contract21/card10/numerical-source108
khớp; không chạy lại thí nghiệm. Preflight GCP gần nhất ghi **672 tests PASS**.
Trạng thái đợt full03 hiện **chưa xác minh được vì SSH timeout**; tiến trình thu
kết quả local không còn chạy. Snapshot cuối23:50:47 ngày29/10 ghi120lượt hoàn tất,
3ca còn chạy ở vòng đầu; chưa có export cuối của03 trong repo.
**Chưa khóa v1.3.1/n/seed/CF; Lesson7 chưa hoàn tất, Phase4 HOLD.**
[Trạng thái lần push](results/lessons/l3r_7/full_numerics/push_snapshot_20261030.json) ·
[Giải thích bài7](notes/lessons/L3R.7_explained_vi.md) ·
[Báo cáo đợt02](results/lessons/l3r_7/full_numerics/report02/report.md).

**L3R.7 — đã chạy hai probe lớn trên GCP** (29/10/2026, DL-084–085):
633/633 tests PASS trên local và 633/633 PASS riêng trên GCP. Balanced candidate:
medium local **19,926 s** (baseline806,568s, quantiles khớp); hai marginal degree12000
trên GCP **902,514 s / 329,654 s**, peakRSS **137,9 / 108,9 MiB**, law error bounds
**1,408e-32 / 2,453e-33**. Phiên bản balanced hoàn tất3/3probe đã đăng ký.
Giữ failed candidate02 và baselinev2 B bị ngắt/thiếu finalreceipt; không tô thànhPASS.
29file export khớp SHA256; ruleSSH tạm đã xóa, VM vẫn RUNNING do tác giả bật.
**Candidate chưa adopted; numerics v1.3.1/fullaccuracy/D22 còn HOLD. Chưa n/root/CF.**
[Kết quả candidate](results/lessons/l3r_7/extended_capacity/candidate_report.md) ·
[CSV](results/lessons/l3r_7/extended_capacity/candidate_metrics.csv) ·
[Baseline và lần gián đoạn](results/lessons/l3r_7/extended_capacity/report.md).

**Snapshot numerics v1 — kết quả HOLD** (29/10/2026, DL-078–079):
prereg `0efddcc` trước run; **595/595 full tests,8/8 numerics tests PASS**.
Replay **3/3 anchor khớp**, stationary **3/6 hoàn tất,3/6 UNRESOLVED do CPU ceiling**.
Hai probe degree12000 dừng ở numpy_roots, khoảng2.21GiBRSS; degree1200 dừng ở
mpmath LU437×437. Tổng396.116CPU-s;312globaljobs chưa mở theo stop rule.
**Chưa khóa v1.3.1, chưa cấp n/root/CF; Phase4 HOLD/G1.**
[Báo cáo numerics](results/lessons/l3r_7/numerics_report.md) ·
[Số đo CSV](results/R3R_numerics/20261029_01/metrics.csv).

**Snapshot L3R.7 trước calibration — phần chuẩn bị hoàn tất, chưa sinh confirmation**
(29/10/2026, DL-075–076): **587/587 full tests,38/38 targeted PASS**; sửa checker
receipt thiếu manifest, giữ nguyên10file cardv1 và21file contract. Sampler dùng
seed thử,10.000draws; inventory308records/245reservedv1.3keys; power36scenarios;
runner từ chối đúng, engine0/CF0/rootconfirmation0. **DL-077: luật n đã duyệt,
B48CPU-giờ theoủyquyền,2worker banđầu/tốiđa4,1luồngBLAS mỗiworker**;
numericsv1.3.1 và audited backend/dry-runB còn DEFERRED. **Sampling/Phase4 HOLD**,G1.
[Thiết kế](notes/design/confirmation_v1_3.md) · [Report](results/lessons/l3r_7/report.md) ·
[Completion](notes/phases/L3R_7_completion.json).

**Phase 3R — L3R.6 đã đóng băng hypothesis cards v1** (29/10/2026, DL-073–074):
freeze commit **1414d92**, [receipt](notes/phases/PHASE_3R_hypothesis_cards.lock.json) verify PASS.
Tác giả chọn **phương án D**: Hyp-MV (ḠM/C̄ref≥1%) và Hyp-SH (ḠS/C̄ref≤−1%) primary, không secondary;
Γ̄ chỉ diagnostic vì Γ̄≥−min(ḠS,ḠM) (discovery: 3/162 cấu hình có thông tin). Ω⁻ hai card chỉ lật
κ∈[1;3] (ngoại suy). π₀=½, CP 97,5%, Bonferroni, R4 bốn góc, R5 u_max10%; measure khóa trong card.
**9/9 phép kiểm, 17/17 targeted, 549/549 full tests PASS.** AI soạn, tác giả duyệt; phép7 bằng lời
tác giả và Understanding OPEN. Không CF/engine/seed; R09/R10 ngoài mọi vùng. CF sampling chờ numerics
v1.3.1; **Phase4 HOLD**, G1. [Cards](notes/phases/PHASE_3R_hypothesis_cards.md) ·
[Forking log](notes/phases/PHASE_3R_forking_paths.md) · [Claim boundary](notes/01_claim_boundary_v1_3.md) ·
[Report](results/lessons/l3r_6/report.md) · [Completion](notes/phases/L3R_6_completion.json).

**Phase 3R — L3R.5 đã khóa contract v1.3 với mục DEFERRED** (29/10/2026, DL-071–072):
Tag **contract-v1.3 → 3d2359b**,21frozen inputs khớp receipt;
**532/532 full tests,41/41 targeted tests PASS**. P1/RoE/εR1%/εE.5%/c_sw0primary
được tác giả chọn; stakes chỉ mô tả, không dùng OR. Schema giữ210scientific keys
trên216ID; quênc_sw→162,đưaK/ref→228 trên234metadata records.
D22 đã cam kết/khóa định nghĩa; enginepath/auditDEFERRED. Numerical rules LOCKED,
K*/dt*/quadrature-tail/S1routeDEFERRED→v1.3.1 trướcCFsampling. RealismHOLD_UNSOURCED,
auditL3R.3HOLD; **Phase4HOLD**,G1,Understanding/P0-V10/L8/T05OPEN.
Đã đạt điều kiện contract choL3R.6; chưa tạo hypothesis card hoặcCF.
[Contract](notes/01_definitions_v1_3.md) · [Brief](notes/00_research_brief_v1_3.md) ·
[Lock receipt](notes/phases/contract_v1_3.lock.json) · [Report](results/lessons/l3r_5/report.md) ·
[Completion](notes/phases/L3R_5_completion.json).

**Phase 3R — L3R.4 đã chạy screen; realism HOLD_UNSOURCED** (29/10/2026, DL-069–070):
**491/491 full tests,24/24 targeted tests,18/18 generic MC comparisons PASS**.
Nguồn mới3được duyệt/đọc targeted; Excel26nguồn,23record/progress cũ giữ nguyên.
Envelope commit6bef959, export fix830a187 không đổi luật; labels1164500 trước overlay.
**216ID/210cấu hình đều UNSOURCED ở cả DC và edge**, kể cả f1.5/2/3.
MV20ID,SH80ID(78distinct),giao14ID từ discovery cũ; cả MV/SH nhánh(d) HOLD.
Không đủ nguồn tương thích chưa có nghĩa OUT/phi thực tế; chưa empirical validation.
[Report](results/lessons/l3r_4/report.md) · [Nhãn](results/lessons/l3r_4/screen/labels.csv) ·
[Worksheet](notes/realism/worksheet_v1.md) · [Review giới hạn input](results/lessons/l3r_4/blind_review.md) ·
[Completion](notes/phases/L3R_4_completion.json).
L3R.5 học/soạn được; L3R.3 auditHOLD/numericsNOT_FROZEN giữ; contractv1.3DRAFT,
Understanding/P0-V10/L8/T05OPEN, **Phase4 thực thi HOLD**,G1.

**Phase 3R — L3R.3 đã chạy audit; gate HOLD** (29/10/2026, DL-068):
**467/467 tests**, 19 tests gốc riêng, **12/12 mutants**, **19/19 clean reproductions** đạt.
MC: C1 **80/80**, C2 **80/80 sau kiểm arithmetic**, C3 node **8/8**, max|z| **2,313697**.
Giữ UNRESOLVED ở các mức số khai gốc; X2065 qua kiểm sau tăng K80/ref2 (0,050361ppC).
19 lần tái lập thuộc 9 tọa độ vật lý; kiểm bổ sung được ghi riêng. KEEP lõi/snapshot với
lớp test/API trong experiments. Numerics v1.3 và read-back tác giả chưa khóa/hoàn tất.
[Report](results/lessons/l3r_3/report.md) · [CSV/metric](results/lessons/l3r_3/summary.csv) ·
[Code map](notes/verification/l3r_3/code_map.md) · [Completion](notes/phases/L3R_3_completion.json).
L3R.4 học tiếp được; **Phase4 thực thi HOLD**, contract v1.3 vẫn DRAFT.

**Phase 3R — L3R.2 hoàn tất kỹ thuật** (28/10/2026, DL-065):
[T07 estimand/proofs](notes/theory/T07_population_estimand.md) đã commit trước audit;
**16/16 golden, 439/439 full tests PASS; 500 joint laws/0 vi phạm; 5/5 mutant KILLED**.
[Report/số đo](results/lessons/l3r_2/report.md) · [JSON exact](results/lessons/l3r_2/toys/metrics.json) ·
[Completion](notes/phases/L3R_2_completion.json). T07 soạn theo ủy quyền;
Understanding/ownership OPEN. Tiếp theo **L3R.3 audit engine**; chưa engine verification,
Contract v1.3 vẫn DRAFT, Phase 4 thực thi HOLD.

**Phase 3R — L3R.1 hoàn tất kỹ thuật** (28/10/2026, DL-064):
pilot được đóng băng tại tag `explore-v13-pilot` → `a7435e9`, không merge branch.
Đếm một lần từ raw: **216 ID/210 cấu hình phân biệt; harm80/216 hoặc78/210**;
423 tests toàn repo PASS,3/3mutant bị bắt. SUMMARY nguồn giữ nguyên, E1–E7 ghi riêng.
[Discovery record](notes/phases/PHASE_3R_discovery_record.md) ·
[Report/log](results/lessons/l3r_1/report.md) · [Số liệu](results/R3R_01_recount/20261028_01/recount.json) ·
[Completion](notes/phases/L3R_1_completion.json). Trạng thái sau L3R.1: tiếp theo L3R.2;
engine audit/realism chưa làm, Understanding và điều kiện Phase4 vẫn OPEN/HOLD.

**L3.8 — Gate A: REFORMULATE** (DL-061, 28/10/2026):
391/391 tests toàn repo vừa kiểm lại PASS; validity/evidence và điều kiện quy trình
được tách riêng. Tác giả chọn chuẩn bị thiết kế mới; hai mục closeout được viết ngôi
“tôi” theo ủy quyền trực tiếp, **Understanding/ownership vẫn OPEN**.
[Gate note](notes/phases/PHASE_3_gate.md) · [Closeout](notes/phases/PHASE_3_closeout.md) ·
[Record tác giả](notes/phases/PHASE_3_author_decision.json) ·
[Audit L3.8](results/lessons/l3_8/report.md). Bước tiếp: hoàn thiện
[contract v1.3 DRAFT](notes/01_definitions_v1_3_draft.md) và [brief DRAFT](notes/00_research_brief_v1_3_draft.md).
**Thực thi Phase 4 HOLD tới P0-V10 và contract mới được khóa**; học tiếp được.

**L3.6/A05-F đã đóng băng** (DL-057–058): D25(ii), shared Gaussian H0/H1,
12 hệ số/model, 2 candidates/bên, LOSO 20 lát. **369 tests PASS**; θ, features,
predictions và luật chấm đã commit đúng thứ tự, source/SHA guard PASS.

H1 có LOSO summary MSE thấp hơn H0 **21,13%** trên discovery; chưa là kết quả test.
D của nhóm nội suy chính **0,59124 điểm %Cref**, ngoại suy **0,47495**, đều vượt
margin0,25. Nhóm yếu R09/R10 chỉ **0,21230** nên giữ chưa mở theo luật đã khóa.
Universe12 ô; A05-T mở **R01–R08,R11/R12**, R09/R10 niêm phong.

**L3.7/A05-T đã chạy đúng một lần** (DL-059–060, 28/10/2026): validity 20/20, p_sw 20/20,
chấm lại độc lập khớp. **PC4 nội suy WEAKEN** (d = 0,247 < m = 0,25 điểm % C_ref;
MAE0 0,690, MAE1 0,443); ngoại suy h12 **FALSIFY** (d = −0,142); **K5 bị bác ở R04**
(G_M/C_ref 0,528%); **C1 đứng** ở R05–R08 (khóa sau discovery/trước test; n=4, base rate cao). Không SUPPORT,
không cơ chế. Gate A được tác giả chọn REFORMULATE ở L3.8. [Report L3.7](results/lessons/l3_7/report.md) ·
[verdict](results/A05_test/20261028_01/verdict.json).

[Report L3.6](results/lessons/l3_6/freeze_report.md) · [Audit](results/lessons/l3_6/freeze_verification.json) ·
[Prereg](experiments/A05_freeze/prereg.md) · [Freeze](notes/lessons/A05_F_preregistration.md) ·
[Biểu đồ](results/lessons/l3_6/freeze_diagnostics.png) · [Completion](notes/phases/A05_F_completion.json).

**Trạng thái 28/10/2026:** Phase 2 GO có điều kiện (DL-043); Phase 3 đã hoàn tất
kỹ thuật tới **L3.7/A05-T**, L3.8 chốt REFORMULATE. Contract `contract-v1.2` và prediction card `a03-card-v1`
giữ nguyên. **A04: 92/92 cell-level BOUNDED, 46/46 cặp dt đạt**, không HOLD/cờ dt;
348 tests PASS. Primary dt=1/240 s theo DL-053, pair1/120→1/240 cho từng ô.

**Card: P5 đứng; P2, P3, P6 không đứng.** K5 đạt4/4; Q5 có2/4 witness. Chấm và
commit `7005a3b` trước discovery, kiểm tay độc lập hai ô khớp. Không xác nhận cơ chế.
Đã xét5 phát biểu, giữ1 candidate C1 sau discovery; cả3 miền không bị cheap kill.
K5 đã carry nguyên văn m=1 vào **A05-F**, C1 khóa sau A04; kết quả held-out ở khối L3.7 phía trên.

[Note A04](notes/lessons/L3.5_A04_note.md) · [report đầy đủ](results/lessons/l3_5/report.md) ·
[kiểm chứng](results/lessons/l3_5/verification.json) · [38 ô cuối](results/A04/20261027_01/main_final.csv) ·
[card scores](results/A04/20261027_01/card_scores.csv).
[A01](results/lessons/l3_4/report.md) vẫn PASS: dt1/240, giữ các failed/partial artifacts;
11/11 mutants là kiểm lịch sử A01, không chạy lại trong A04.
[Card](notes/phases/PHASE_3_prediction_card.md) · [L3.3](results/lessons/l3_3/report.md) ·
[L3.2](results/lessons/l3_2/report.md). Engine vẫn ở experiments, chưa promote.

```text
Bản hiện hành thiết kế population (29/10/2026):
  Contract:       notes/01_definitions_v1_3.md (tag contract-v1.3, có DEFERRED)
  Brief / Claims: notes/00_research_brief_v1_3.md · notes/01_claim_boundary_v1_3.md (điền theo cards L3R.6)
  Cards v1.3:     notes/phases/PHASE_3R_hypothesis_cards.md (+ .lock.json; FROZEN 1414d92)
  Receipt:        notes/phases/contract_v1_3.lock.json
  Kết quả cũ:     notes/01_definitions_v1_2.md · notes/design/grid_v1_2.json · notes/design/v1_2_protocol.md
  Phase:          notes/phases/PHASE_3R.md (L3R.6 cards frozen; numerics/realism HOLD)
  Gate / Closeout: notes/phases/PHASE_3_gate.md · PHASE_3_closeout.md (REFORMULATE, ownership OPEN)
  Draft lịch sử:  notes/01_definitions_v1_3_draft.md (DL-061, đã supersede cho thiết kế mới)
  Log:            notes/02_decision_log.md · notes/00_exposure_register.md
  Experiments:    notes/03_experiment_index.md (A01 | A04 | A05-F | A05-T)
  D v1.2:         src/smr/cells.py (nguồn experiments giữ nguyên)
  Engine L3.2:    experiments/A00_engine/ (read-back author-attested, chưa promote)
  Prediction:     notes/phases/PHASE_3_prediction_card.md (a03-card-v1)
  A05-F freeze:   notes/lessons/A05_F_preregistration.md · experiments/A05_freeze/
  KHÔNG hiện hành: definitions v0/v1/v1.1; src/smr/design.py (plant L1.8C)
```

[Contract v1.3](notes/01_definitions_v1_3.md) · [brief v1.3](notes/00_research_brief_v1_3.md) ·
[claim boundary v1.3](notes/01_claim_boundary_v1_3.md) · [Phase 3 cũ và phân loại artifact](notes/phases/PHASE_3.md) ·
[experiment index](notes/03_experiment_index.md) · [progress log lịch sử](notes/00_progress_log.md).
[Contract v1.2](notes/01_definitions_v1_2.md) vẫn đi cùng kết quả cũ;
claim boundary v1.2 có addendum Phase2/A04, D1–D25 và lưới giữ nguyên.

**Điều kiện:** A03/A01 prereg đã khóa trước run; A04 dùng dt1/240 và kiểm cặp1/120→1/240 từng ô.
**V9 đã được tác giả miễn làm điều kiện tiên quyết theo DL-054 (`WAIVED_BY_AUTHOR`)**;
memo chưa gửi, chưa có phản hồi GVHD thật. Prereg/exposure, runner/tests và A04 đã hoàn tất.
[Completion A04](notes/phases/A04_completion.json) ghi trạng thái sau run; gate record là snapshot trước run.
[Gate record](notes/phases/A04_execution_gate.json) · [preflight L3.5](notes/lessons/L3.5_preflight.md).
A05-F đã khóa; A05-T đã chạy một lần sau quyết định DL-059. **HOLD Phase 4 tới P0-V10**. Người đọc P0-V10/L8 và các mục
tác giả tự viết còn mở. [Gói cho người đọc](notes/meetings/phase2_reader_packet.md).
Không dùng nháp heads-up 23/10 nguyên trạng (đã lỗi thời). Main RQ/contract/G1 giữ nguyên.

Main RQ:
> For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

**Mỗi lần tìm hoặc kiểm paper:** đọc [quy tắc + checklist](notes/literature/search_protocol.md).
[Search log](notes/literature/search_log.md) · [Excel tiến độ đọc](papers/paper_comparison.xlsx) ·
[thư viện](papers/README.md). PDF lưu ngoài Git.

Cài môi trường và chạy kiểm thử (Python >= 3.10):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
```
