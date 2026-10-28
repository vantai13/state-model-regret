# Progress log — các trạng thái lịch sử

Người phụ trách: **Doan Van Tai** · chuyển từ README ngày 27/10/2026 (L3.1 Part 3).
Nguồn: README tại commit `af734a7`. Toàn bộ phần cũ được giữ, chỉ điều chỉnh link
cho vị trí mới. Các trạng thái HOLD/GO và số tests bên dưới là **lịch sử tại thời
điểm ghi**, có đoạn mới hơn thay thế đoạn cũ; không dùng làm trạng thái hôm nay.
[Bản hiện hành](../README.md) · [DL-044](02_decision_log.md#dl-044--mở-phase-3-điều-kiện-còn-mở-và-bản-hiện-hành-2026-10-27).
`00_history.md` giữ nguyên vì là lịch sử các thế hệ nghiên cứu.

## L3R.2 — T07 và golden reference (28/10/2026, DL-065)

Đọc đủ 3 phần lesson; T07 đủ 8 mục, 18 sanity rows, proofs và toys, soạn theo ủy quyền.
Commit315d203 trước run/audit. 16 golden PASS (0.47s), 439 full PASS (61.95s), 500 joint laws
seed20261028/0 vi phạm; 5/5 mutant KILLED. Sửa điều kiện invariance, chiều suy Γ/harm,
finite-support smoothness, bound Γ và optional cb0; không đổi contract v1.2/pilot.
Chưa audit engine population; không CF/R09/R10 outcome; Understanding/P0-V10/L8/T05 OPEN,
G1 giữ nguyên, Phase4 HOLD. [Report](../results/lessons/l3r_2/report.md),
[T07](theory/T07_population_estimand.md), [completion](phases/L3R_2_completion.json).
Tiếp theo L3R.3; T07 reference có sẵn không phải xác nhận tác giả tự viết.

## L3R.1 — re-entry hoàn tất kỹ thuật (28/10/2026, DL-064)

Đã đọc bundle, xóa ZIP theo yêu cầu; pilot tag a7435e9, branch không merge/xóa.
Khai trước c8c165e và tag đều trên remote trước một lần đếm. 13 tests riêng/423full PASS,
3/3mutant KILLED. Đếm216ID/210cấu hình,234ID gồmrobust; harm80/216 hoặc78/210.
E1–E7/overlap45ID/23ô/mappingeta/dt/D22 được ghi; SUMMARY/raw giữ nguyên.
Sai lệch trình tự tag và lỗi EOF so preview đã công bố trong report; không rerun hoặc đổi dữ liệu.
L3R.1 không chứng minh engine đúng/hypothesis; Understanding OPEN, học L3R.2 được;
P0-V10/L8/T05 và thực thiPhase4 HOLD giữ nguyên. [Report](../results/lessons/l3r_1/report.md),
[record](phases/PHASE_3R_discovery_record.md).

## L3.8 — Gate A REFORMULATE, DL-061 (28/10/2026)

Đọc đủ hai phần lesson, đối chiếu nguồn/freeze/output, chạy lại391tests PASS.
Đã soạn bảng11validity checks, bảng quy trình,5outcomes, gate note/closeout/handoff;
không đổi RQ/contract/metric/threshold, không run engine/outcome mới. Sửa diễn giải
ngoại lệ EΔ=0 trong phát biểu lật⇔GM>0; T01 không suyΓvô nghĩa hoặc bắt buộc đổi thiết kế.
Tác giả chọn REFORMULATE thay khuyến nghị NARROW trước đó của AI. Hai mục closeout
viết ngôi “tôi” theo yêu cầu ủy quyền mới, không phải author-understanding attestation.
DL-061 chốt một nhãn/claim và ghi exception ownership. Đã chuẩn bị contract/briefv1.3
DRAFT, chưa khóa/rerun. P0-V10/L8/ownership OPEN; thực thiPhase4 HOLD tới người đọc
và contract mới, học tiếpđược. Closeout commit trước annotated tag theo lesson.
[Gate](phases/PHASE_3_gate.md) · [Closeout](phases/PHASE_3_closeout.md) ·
[Phần tác giả](lessons/L3.8_author_handoff.md) · [Report](../results/lessons/l3_8/report.md).

## L3.7 — A05-T hoàn tất, nhắc lại trạng thái mới hơn L3.6 bên dưới

DL-059–060, run đã commit e719157 và report ec022d1:10ôR mởmộtlần,
20BOUNDED/10pairsPASS;PC4nộisuyWEAKEN,ngoạisuyFALSIFY,K5bácR04,C1đứng4ô.
R09/R10niêmphong;10ôđãmởkhôngcòncleantestchohypothesismới.
[Report](../results/lessons/l3_7/report.md). Các dòng “chưa A05-T” dưới đây là lịch sử.

## L3.6 / A05-F — đã đóng băng (28/10/2026,DL-057–058)

Tác giả chọn D25(ii),thiết kếA vàủyquyềnchi tiết. Author51c926f→prereg57d84c6
→theta6aa696a→prediction3c75aec→freeze5f20103.369testsPASS;80LOSO/2fullfits,
164starts đều thànhcông. H0/H1cùng12coeff/2candidates/rho0;H1summaryMSELOSO
thấp hơn21.13%,chỉdiscovery. Dprimary.59124pp,weak.21230pp,extra.47495pp;
margin.25pp. GiữR09/R10chưamở;actualplanned10ô theo luật trướcprediction.
K5m=1nguyênvăn;C1equivalence≤.005khóa sauA04,báoriêng. FeaturesRchỉbậc0–2,
khôngD/cost/gap/Cref/outcomes. Chưa A05-T/irreversibledecision;human/Phase4giữmở.
[Report](../results/lessons/l3_6/freeze_report.md) · [Freeze](lessons/A05_F_preregistration.md).

## L3.6 — chuẩn bị, chưa freeze (28/10/2026)

Đã đọc đủ baattachment, thêm append-only headroom vào noteA04/boundary, tự kiểm
38ô/20lát và base rates. Gaussian/identity/pairedintervalMAE có10test mới,
358fullPASS/60s. ToyMC2×2triệu mẫu đạt;100.000toyD không vi phạm trên allowance
float,rawexcessmax6.66e−16 được ghi.147A04hashes và nguồnengine/card giữnguyên.
**Chờ tác giả quyết D25/lambdaA và phạm vi H0/H1/C1**; chưaprereg/theta/predictions
hoặcfreeze. Khôngfit/targetfeatures/D/cost/gap held-out;khôngA05-T.
[Report](../results/lessons/l3_6/report.md) · [Lựa chọn](lessons/L3.6_decisions_pending.md).

## L3.5 / A04 — run27/10, tổng kết28/10/2026 (DL-055–056)

Prereg56c4141,receipt0eb42f2,score checkpoint7005a3b trước discovery.38main+8ô kiểm/
đầu dò ×ref1/ref2=92BOUNDED;46pairs đạt;60zeroD19+6zeroWD;khôngHOLD/cờdt.
348tests PASS;hai ô review bằng phiênAI riêng khớp,không human/GVHD review.
P2:2/4 nên không đứng;P3:0/2 không đứng;P5:K4/4,Q2witness nên đứng;P6:0/2 không đứng.
5phát biểu đã xét,1candidateC1 post-discovery;0/3miền cheap kill. K5carry m=1 giữ nguyên.
Không thay card/lưới/engine/dt;khôngD/cost/contrast held-out mới. Đã ghi exposure public
held-out design metadata do đọc bảng cũ;không dùng làmfeature. Literature20records,
1proposal mới chưa tải/đọc full text;khôngnovelty. L3.6 mở,khôngA05freeze/Phase4.
[Note](lessons/L3.5_A04_note.md) · [Report](../results/lessons/l3_5/report.md).

## Sau A01 / DL-054 — 27/10/2026

Theo yêu cầu trực tiếp của tác giả, điều kiện gửi memo trước A04 chuyển sang
**WAIVED_BY_AUTHOR**. Memo chưa gửi, không ghi GVHD thật đã phản hồi. Review mô
phỏng được lưu nguyên nguồn với phạm vi remotef72306f; intake đối chiếu A01 local.
Có thể triển khai L3.5; còn prereg/exposure/runner/tests trước run38ô. Không A04/
held-out outcome mới; L8/P0-V10/T05 author-writing/Phase4 HOLD giữ nguyên.
[Gate](phases/A04_execution_gate.json) · [preflight](lessons/L3.5_preflight.md).

## L3.4 / A01 — 27/10/2026

Prereg/receipt trước outcome; giữ run01 FAIL N01 và run02 INTERRUPTED. Sửa symbolic
idle/mean-path certificates và O(n²) conversions; không đổi contract/card/ngưỡng.
Run03 PASS:9p_sw bitwise,18C1–C3 identities,C4toy PASS,60C5+6WD exact zeros;
15/15BOUNDED,12/12pairsPASS, dt cuối **1/240s/ref2** sau đủref1–16. 336tests,
11mutantsPASS. CSV replay cùng2; outcome calibration đã exposed, không held-out.
A04/V9 vẫn chờ; chưa chấm card/H1/null hoặc đóng author Understanding/L8/P0-V10.
[Report](../results/lessons/l3_4/report.md) · [selection](../results/A01/20261027_03/selection.json).

## L3.3 / A03 — 27/10/2026

Card4forecast không cơ chế/14sanity/1luật K5, tác giả chọn hai mức K5 và author-attested
hai read-back;324tests PASS,11/11mutant KILLED,4000ledger0vi phạm. Commit card riêng,
receipt/tag theo sau; không A01/gridoutcomes/Dmới ngoài regression cũ. [Report](../results/lessons/l3_3/report.md).

## L3.2 — 27/10/2026

Engine exact thực nghiệm: 72 tests mới/300 toàn repo PASS; 11/11 mutant bị bắt;
golden canonical/E2/E5/E7/L1.5/L1.8B đã kiểm. 32 D-only migration cases khớp,
không grid outcomes. T05 tác giả OPEN, chưa promote vào src; L3.3 chưa commit,
V9/A04 và P0-V10/Phase4 giữ nguyên. [Report](../results/lessons/l3_2/report.md).

---

# State × Model — giá trị cải thiện quyết định routing

Tác giả: **Doan Van Tai**.

**Mỗi lần tìm hoặc kiểm paper:** mở [quy tắc + checklist 7 bước](../notes/literature/search_protocol.md).
**Hỏi → Tìm → Kiểm → Duyệt → Đọc → Ghi → Dừng**; [log các lượt thực chạy](../notes/literature/search_log.md).

**Trạng thái 23/10/2026: Phase 1 đóng — GO có điều kiện sang Phase 3.** Contract khóa tại tag **`contract-v1.2`**. [Lưới v1.2](../notes/design/grid_v1_2.md) ACCEPTED: 38 ô chính được neo theo ranh giới quyết định (oracle chọn Switch khoảng 30% hoặc 70%), 12 ô held-out, 6 ô kiểm âm, 2 đầu dò; mọi ô ổn định tới dt/4 và trong budget. Calibration A01: M01, M09, M22. Sáu kiểm nhất quán PASS, **193/193 tests PASS**. Chưa tính contrast hay regret ở ô nào. [Closeout](../notes/phases/PHASE_1_closeout.md) · [contract v1.2](../notes/01_definitions_v1_2.md) · [claim boundary](../notes/01_claim_boundary_v1_2.md) · [DL-038, DL-039](../notes/02_decision_log.md) · [thử nghiệm thiết kế](../notes/explore/reformulate_grid_report.md).

Điều kiện còn mở: HOLD Phase 4 tới khi có người đọc độc lập (P0-V10); heads-up và memo GVHD **chưa gửi** (V9), nên gửi trước A04; lý do và câu chữ v1.2 do AI soạn, tác giả chưa tự viết lại. V1/V8/P0-V3/P0-V11 author-attested. G1 giữ nguyên. Các đoạn dưới là lịch sử, gồm trạng thái HOLD trước đó của lưới v1.1 (B4 rejected).

**L2.1–L2.3, cập nhật 24/10/2026:** đã lưu bộ literature Part A, proof T03 v2,
code tái lập và toàn bộ output toy. **21.952 toy**, I1–I6 không vi phạm;
**17/17** kiểm P11 và **202/202** tests toàn repo PASS.
[Báo cáo, checklist, commands và output](../results/lessons/part_a/report.md) ·
[Literature index](../notes/literature/README.md) ·
[Prior boundary](../notes/literature/prior_boundary.md).
Formal Part A **HOLD**: forecasts AI-assisted đã exposed trước commit,
L-self/proof kín sách/đọc lại và review người thật chưa có record; B82/MAB11 còn
hạn chế full-text. Đây là verification toy, chưa chạy contrast lưới Phase3,
chưa freeze L3.3, không nâng G1 hoặc mở HOLD Phase4.

**Paper đang dùng:** [Excel và tiến độ đọc](../papers/paper_comparison.xlsx)
· [Thư viện và hướng dẫn](../papers/README.md). PDF lưu cục bộ, không đưa vào Git.

**Phase 2 — Gate L: GO có điều kiện (26/10/2026, [DL-043](../notes/02_decision_log.md), tag `phase-2-closeout`).**
Main RQ **KEEP**; PC1 DROP (framing), PC2/PC5/PC6 NARROW, PC3 KEEP câu chữ, PC4 HOLD (A05).
Tác giả author-attested đã tự đọc 7 nguồn quyết định nhãn, tự dẫn T03, xác nhận nhãn. Điều kiện:
một người đọc thật (L8); tác giả tự viết hai mục đầu [closeout](../notes/phases/PHASE_2_closeout.md).
**Phase 3 mở:** commit L3.3 trước A01; memo GVHD trước A04; HOLD Phase 4 tới P0-V10.

**Bản chính thức + hỗ trợ tự đọc (26/10 tối):** S11 journal TIT2026 khớp số mục; file R01 là
TR 2006 (cần bản Springer) và R34 là bản CDC 1992 2 trang (cần TAC 1995). Có
[gói tự đọc](../notes/literature/author_reading_pack.md) và [ví dụ tính tay T03](../notes/theory/T03_worked_example.md);
L-self/T03/tự chấm vẫn chờ tác giả. [Report](../results/lessons/l2_9/journal_check/report.md).

**Đợt duyệt 26/10:** bạn duyệt và tải 9 PDF; đọc targeted IA26, DTS25, CEN26, CEH23
(AI-T/AI-F, chưa L-self) → Excel 23 nguồn. Các điều kiện "nhãn sẽ đổi nếu" của PC2/PC3/PC5/PC6
đã kiểm: **không nhãn tạm nào đổi**; thêm H1-Q04. [Report](../results/lessons/l2_8/approved_batch/report.md).

**WM26 — tác giả đọc bản giải thích AI (26/10):** ghi nhận **L-2nd, author-attested**,
chưa phải L-self; AI kiểm bản giải thích trên PDF (khớp, 2 ghi chú nhỏ) và đính chính lỗi
"§9"→**§8** của chính AI. [Kiểm](../results/lessons/l2_9/wm26_author_reading/check.md) ·
[record](../notes/literature/author_reading_record.md). Gate L vẫn HOLD.

**L2.9 Part2,26/10/2026 (AI theo ủy quyền tác giả):** nhãn tạm Main RQ **KEEP**; PC1 DROP,
PC2/PC5/PC6 NARROW, PC3 KEEP câu chữ (framing NARROW), PC4 HOLD; **Gate L = HOLD**
([DL-042](../notes/02_decision_log.md)) vì L-self 0/19, T03 chưa tự dẫn, chưa có người đọc thật.
[Related work](../notes/literature/related_work_skeleton.md) · [closeout (HOLD, chưa tag)](../notes/phases/PHASE_2_closeout.md)
· [report](../results/lessons/l2_9/part2/report.md). Không phần nào ghi là tác giả tự làm.

**L2.9 Part1,26/10/2026:** [hồ sơ 8 cột PC1–PC6/Main RQ](../notes/literature/prior_boundary.md)
với **cột nhãn để trống cho tác giả**, trạng thái Gate L = **HOLD** (L1/L2/L6/L8 thiếu),
[mẫu ghi L-self](../notes/literature/author_reading_record.md) chưa điền, WM26 F.1 đọc lại
(AI-T: không thấy nhánh chỉ dùng thông tin hiện tại). [Report](../results/lessons/l2_9/part1/report.md).

**L2.8 follow-up,26/10/2026:** P02 nay đọc được từ bản VoR bạn tải → AI-T §1–5/Bảng 2:
bias một đại lượng mỗi lần, quét 1-D theo prediction/update horizon, không joint bias.
Phiên tìm mới lưu raw HTTP + sha256 từng call: 157 record, không Tier1, 4 T2, chưa đạt
luật dừng. Sàng abstract 6 đề xuất cũ + R06; 3 đề xuất mới chờ duyệt. Không L2.9/Gate.
[Report/commands](../results/lessons/l2_8/followup/report.md) · [note P02](../notes/literature/papers/P02.md).

**L2.8 Part2,26/10/2026:** [Primary reading/crosswalk](../notes/literature/literature_audit_part2.md),
[report/commands](../results/lessons/l2_8/part2/report.md). R01/R02/R04 và3nguồn mới
NDT26/WM26/AIS22 được duyệt đã AI-T. WM26 có2×2repair; R04 cho sufficient
diagnostic, chưa H1. Cooper Example1 tính lại revenue14.586589→14.079588,
loss0.507000; V1 GS=−1/4. Excel19nguồn, giữ13notes/progress. A1–A3/A4repeat
169screen events nhưng chỉcall-level checkpoints, thiếu raw từng rank;
không saturation hoặc formal Gate/L2.9/Phase3. Các mục dưới là trạng thái lúc lưu.

**L2.8 Part1,26/10/2026:** [4audit cards](../notes/literature/audit_sessions.md) và
[A4 screening/report](../notes/literature/literature_audit_part1.md) đã lưu.
Google Scholar20+15records; forwardR02 thêm20records,3Tier2proposals chờ duyệt.
Official abstracts R01/R02/R04 AI-A; archiveAI-T được giữ riêng. A1–A3/primary
Part2/L2.9 còn mở; chưa đạt stopping rule hoặc novelty clearance. Excel giữ13nguồn.

**L2.7 Part B,26/10/2026:** [VE/OεRE và bài tập](../notes/literature/model_equivalence.md),
[terms](../notes/literature/terms.md), [P12](../notes/literature/papers/P12.md), PC5/K-M6–7 và
[L3.3/A05 queue](../notes/lessons/L3.3_equivalence_queue.md) đã lưu. **27checks PASS**,
625exact two-state cases; V1 model-gain/Cref0% dưới S0,20% dưới S1.
Luật κ≥2,A/Bq90,h8 có4main+R03/R04 theo metadata; **chưa chọn K5, chưa test held-out**.
[Report/commands/output](../results/lessons/l2_7/part_b/report.md). PartB hoàn tất kỹ thuật;
toàn L2.7 còn P02 full text/Understanding/L-self/Gate. Contract/grid/PC không đổi.

**L2.7 Part A,26/10/2026:** [fidelity/oracle/factorial và bài tập](../notes/literature/model_fidelity_methods.md),
[MT1–MT8](../notes/phases/PHASE_4_methodology_threats.md), K-M1–5 và Excel12nguồn đã lưu.
**14checks exact PASS**, thêm256factorial+256oracle cases; RP/WS=3,5/2,5,
future EVPI1; V1Γ=1/4. P03=R51/P07 AI-T, **P02 chỉ abstract: full text BLOCKED**.
[Report/commands/output và việc còn mở](../results/lessons/l2_7/part_a/report.md).
Part A còn dependency P02; PartB/P12, L-self/Gate/A4/A05/L2.8–2.9 chưa đóng.

**L2.6 Part B, 26/10/2026:** [P13 journal](../notes/literature/papers/P13.md),
[horizon/transient/crosswalk](../notes/literature/horizon_transient.md), K-F/K-H,
H1-Q02 và T-H1 đã lưu. **122checks PASS**: fluid25 tại h10/100, q0gấp2 cho100;
abstract no-queue Γ=1/5 hoặc−1/2, không chứng minh mechanism của grid.
[Report/commands/output](../results/lessons/l2_6/part_b/report.md).
Cả2parts hoàn tất kỹ thuật; formal Understanding/L-self/Gate/A4/L2.9 còn mở.

**L2.6 Part A, 26/10/2026:** đã lưu [AoI, K3, mode/variance và decision value](../notes/literature/freshness_decision_value.md),
[note S11](../notes/literature/papers/S11.md) với journal identity **TIT2026** đúng,
[heuristic queue H1](../notes/literature/h1_candidates.md) chưa khóa.
**293checks PASS**,125binary cases; bài tập đổi gap cho value1/4packet·s.
[Report/commands/output](../results/lessons/l2_6/part_a/report.md).
Record lúc lưu chỉ PartA; PartB nay có ở trên. Tác giả L-self và formal Gate còn
mở. Không chạy lưới/Phase3.

**L2.5 Part2, 26/10/2026:** đã kiểm [hai cơ chế, V1 và bài tập hi={2,5}](../notes/literature/information_harm.md),
[M00](../notes/literature/papers/M00.md)/[P01 screen](../notes/literature/papers/P01.md),
K-S1…8 và hàng đợi A4; **44checks PASS**. V1 GS=−1/4,Γ=1/4;
bài tập cả4L=5/4 và contrasts=0 dù M0 vẫn bias Stay1/2.
[Báo cáo, commands, CSV và giới hạn](../results/lessons/l2_5/part2/report.md).
AI-T, chưa L-self/Gate hoặc Phase3; không đổi G1/contract/HOLD Phase4.

**L2.5 Part1, 26/10/2026:** đã lưu [note/bảng dịch stale state và đính chính lesson](../notes/literature/state_staleness.md),
[P04 journal15trang](../notes/literature/papers/P04.md), code/CSV minh họa và log.
22kiểm PASS: cùng10yêu cầu, blocked T1/T5/T10/round-robin =0/1/4/1;
T6=0 cho thấy toy hữu hạn không đơn điệu theo T. Đây không là replication P04
hoặc lưới Phase3. Trạng thái lúc lưu Part1: Part2 và L-self chưa thực hiện;
Part2 đã được bổ sung ở trên, L-self/Gate còn mở.

**L2.4 Part2–3, 25/10/2026:** đã lưu [bản đồ NDT, pipeline, metric và giới hạn claim](../notes/literature/ndt_landscape.md),
notes NDT1/P05/P10 và snowball thật (15 references,100 citing titles;3 đề xuất chưa duyệt).
Kiểm625 tổ hợp cost/tie PASS; đây là ví dụ minh họa, chưa chạy lưới Phase3.
Mức đọc là AI-only; Gate/L-self của tác giả chưa được xác nhận.

Các record bên dưới là lịch sử của Phase0/L1.2–L1.8 và mốc2. [Mốc2](../notes/design/decisions_v1_1_m2.md) đã chốt trước candidate calculations; [report mốc2](../notes/verification/v1_1_m2/README.md) ghi2/10 certificates của prototype cũ, đã được PhầnA thay thế. Lưới v1 cũ có13ô Stay áp đảo, cả3calibration bị invalid, vẫn HOLD A01/A04; tag v1 và output lịch sử giữ nguyên. Các lựa chọn §11 đã adopted theoủy quyền, không còn chờ từng quyết định kỹ thuật. Contract/claim boundary v1.1 vẫn là **draft cập nhật**, vì B4 không đạt.

Main RQ (nguyên văn Final Review cập nhật 06/10/2026):
> For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?

Record lịch sử 22/10/2026: Phase 1 từng ghi hoàn tất kỹ thuật có điều kiện tại [snapshot contract-v1](https://github.com/vantai13/state-model-regret/blob/6bb631f9181cc06bfade9d71e54ad57ca3bbb284/notes/phases/PHASE_1_closeout.md). Contract/grid v1 lưu tại [definitions v1](../notes/01_definitions_v1.md), [brief v1](../notes/00_research_brief_v1.md), [grid/protocol](../notes/design/grid_v1.md). Record này đã bị trạng thái HOLD ở đầu README thay thế. **G1/candidate gap** giữ nguyên; **HOLD Phase4 tới khi P0-V10 đạt**. P0-V3/V11, human feedback và final grid Δt A01 còn pending. V0 giữ làm snapshot lịch sử.
L0.1: **SCIENTIFIC/UNDERSTANDING PASS — PRACTICAL PENDING**; heads-up chưa gửi.
L0.2: đã thêm [RQ card v0](../notes/lessons/L0.2_rq_card.md) ngày 08/10/2026; phần diễn giải chờ tác giả xác nhận, read-back chưa làm; V3/V11 còn mở và được mang sang theo phương án B.
Contract v0: [D1–D25, quyền thông tin, estimand, repairs, scope và năm sửa đổi DL-010](../notes/01_definitions.md), bản kỹ thuật đóng băng tại **`contract-v0`**. Các nhãn DRAFT/OPEN giữ bên trong snapshot; tự kiểm chưa hoàn thành. Quyết định phase tại **`phase-0-closeout`**.
[T00 — timescale sanity](../notes/theory/T00_timescale_sanity.md): đã cập nhật phương án A, giữ cả neo (a) ms/datacenter và (b) polling/edge; trục tổng tuổi/delay 5 ms–30 s. **10 test timescale đạt**, ma trận 40 ô khớp; AoI prototype chỉ đối chiếu. Đây là kiểm fluid có điều kiện; chưa chứng minh practical gain.
[L0.5 — phân loại legacy](../legacy/INDEX.md): đã bổ sung 21 dòng phân loại và 10 giả định không mang sang; bài tác giả tự kiểm 5 dòng còn chờ. Khung package `smr` đã cài editable và **11 test đạt** (10 timescale + 1 smoke).
File 8: đã thêm khung [L0.3 — objects](../notes/lessons/L0.3_objects.md), [L0.4 — estimand](../notes/lessons/L0.4_estimand.md), [L0.5 — legacy](../notes/lessons/L0.5_legacy.md), [L0.6 — scope](../notes/lessons/L0.6_scope.md), [L0.7 — review](../notes/lessons/L0.7_review.md). MẪU và bài chưa làm được ghi riêng; chưa có đủ understanding artifacts hoặc record người đọc độc lập. V3/V10/V11 còn mở; File 9 đã đóng theo B và ghi rõ điều kiện/mốc xử lý.
[Ownership Review — phần đã chọn và việc chưa hoàn thành](../notes/PHASE_0_ownership_review.md): đã nêu chọn B2 và domain hai neo; self-explanation, tính tay, review và liên hệ GVHD còn Pending; formal closeout đã ghi B có điều kiện.
Review chuyển phase 08/10 ([DL-010](../notes/02_decision_log.md#dl-010), review kỹ thuật tự động): **GO WITH CAUTION**; năm sửa đổi đã áp, bảo toàn/Jensen được tái lập bằng [script hữu hạn](../notes/verification/verify_dl010.py). [Closeout §6](../notes/phases/PHASE_0_closeout.md) ghi B, **V3/V10/V11 còn mở**; không phải GVHD duyệt.
[Inventory](../notes/00_evidence_inventory.md) · [Exposure](../notes/00_exposure_register.md) · [Claim boundary](../notes/01_claim_boundary_v0.md).
[History](../notes/00_history.md) · [Archive index](../legacy/INDEX.md) · [Closeout](../notes/lessons/L0.1_CLOSEOUT.md).
[Kết quả và nguồn kiểm chứng](../notes/verification/2026-10-07_report.md) · [Cách tái kiểm](../notes/verification/README.md).
L1.2 (09/10/2026): đã thực thi hai phần lesson hàng đợi; **11/11 test lesson, 22/22 test toàn repo đạt**. Vét cạn **5.832 cấu hình**, **2.048** không idle, **0 vi phạm**; bốn mutant bị 5/3/8/5 test phát hiện. [Experiment card](../notes/lessons/L1.2_experiment_card.md) · [Báo cáo, bảng từng slot và kết quả đo](../notes/verification/l1_2/report.md). Đây là verification toy plant; golden lấy từ tài liệu được cung cấp, V3/V10/V11 và G1 giữ nguyên.
L1.3 (21/10/2026): **9/9 test theo tài liệu, 20/20 test hai lesson, 3/3 kiểm bổ sung và 34/34 toàn repo đạt**. Sinh đúng bốn state, mỗi state 1/4; oracle L=6,25, luôn Stay R=1,125, luôn Switch R=0,875 packet·slot. Cả năm mutant bị bắt; M5 lọt 8 test đầu và bị test bất đối xứng chặn. EV-22 được ghi nhãn ví dụ sổ sách theo audit cấu hình trích. [Experiment card](../notes/lessons/L1.3_experiment_card.md) · [Báo cáo, số liệu, log và biểu đồ](../notes/verification/l1_3/report.md). Golden bổ sung H=3 có một lỗi dự đoán đã sửa và giữ log preflight; G1/V3/V10/V11 chưa đổi.
L1.4 (21/10/2026): **12/12 test lesson, 32/32 test ba lesson và 48/48 toàn repo đạt**. Lưới 1.156 và 9.604 cấu hình có 0 vi phạm ba tính chất; kiểm thêm đủ 8 pattern. G_S=1,125,G_M=0,25,Γ=−0,25 packet·slot; model repair làm hại 1/2 tổng xác suất episode dù gain trung bình dương. Năm mutant bị bắt; lỗi đổi nhãn S/M lọt 11 test đầu và bị golden bất đối xứng chặn. [Experiment card](../notes/lessons/L1.4_experiment_card.md) · [Báo cáo, CSV, log, biểu đồ](../notes/verification/l1_4/report.md). Dự đoán của bốn ô cho sẵn; chưa implement belief/model L1.6, G1 và các gate giữ nguyên.
L1.5 (21/10/2026): **11/11 test lesson, 43/43 bốn lesson và 61/61 toàn repo đạt**. F5 khớp 16 cặp chuẩn và 81 cặp lưới; 12.288 cấu hình belief có 0 vi phạm mean-zero. I_Δ=(1/2,−1/2,0,0), mean=0 nhưng E|I_Δ|=1/4. Năm mutant bị bắt; checker độc lập phát hiện P4 bỏ trọng số mà checker dùng chung helper bỏ sót ở test mọi belief. Thêm phản ví dụ cho thấy mean-zero chưa chứng nhận belief đúng. [Card](../notes/lessons/L1.5_experiment_card.md) · [Spec làm việc cho contract-v1](../notes/lessons/L1.5_identity_diagnostic_spec.md) · [Báo cáo/CSV/log/hình](../notes/verification/l1_5/report.md). Chưa fit H0/H1, kiểm held-out hoặc xác nhận posterior S0; G1 và các gate giữ nguyên.
Understanding/judgment được tác giả xác nhận ngày 07/10/2026; chưa phải GVHD phê duyệt hướng mới.

L1.6 A–D (22/10/2026): **16/16 test lesson, 59/59 năm lesson, 3/3 kiểm bổ sung và 80/80 toàn repo đạt**. Belief/M0 sinh từ history và tái lập bảng L1.4–L1.5; 864 matched-prior cases có 0 vi phạm, 576 wrong-prior cases có đúng 5 G_M âm. 6.696 cặp state/action thoả Jensen và idle identity. GS=1,125 tách theo thứ tự thành freshness0,375 + mode visibility0,75; chưa là practical telemetry gain. [Card](../notes/lessons/L1.6_experiment_card.md) · [Spec S0/M0](../notes/lessons/L1.6_belief_model_spec.md) · [Báo cáo/CSV/log/hình](../results/lessons/l1_6/report.md). Sáu mutant bị bắt; output ngoài src/experiments, không copy repo. G1/V3/V10/V11 và HOLD Phase 4 giữ nguyên.

Cài môi trường và chạy kiểm thử (Python >= 3.10):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
```

L1.7 (22/10/2026): **13/13 test lesson,72/72 sáu lesson,4/4 bổ sung,97/97 toàn repo PASS**. N2000,XB,H6: CRN sample variance118.873 so với naive extra-draw353.622; exact117.496/358.152/independent323.248. H3: oracle/leak/honest cost7.836/6.5725/8.22 packet·slot; honest vẫn thắng24.75% episode, không tự là dấu leak. Sáu mutant lỗi bị bắt; R7 equivalent về action. Audit replay11332 CSV rows PASS. [Card](../notes/lessons/L1.7_experiment_card.md) · [Spec/mock tham khảo](../notes/lessons/L1.7_stream_exposure_spec.md) · [Seed](../notes/seed_registry.md) · [Report/CSV/log/hình](../results/lessons/l1_7/report.md) · [Index và audit](../notes/verification/l1_7/README.md). Residual0 chưa đủ CRN; demo không là Phase4/E01 hoặc held-out. G1,V3/V10/V11 và HOLD Phase4 giữ nguyên.

L1.8 **Part A** (22/10/2026): **4/4 test core, 10/10 bổ sung, 111/111 toàn repo PASS**. Hai thẻ đổi đơn vị giữ Δt ứng viên (a) 0,12 ms, (b) 12 ms; tuổi làm tròn thành 42 và 17 slot. R2 giữ correlation qua 204 ms = 0,016907466 tại slot 12/6/3 ms; R1 thay đổi. 96 kiểm fluid boundary và 900 round trips có 0 vi phạm; đã làm rõ dấu crossing correction bằng phản ví dụ exact. [Card](../notes/lessons/L1.8A_experiment_card.md) · [Spec](../notes/lessons/L1.8A_slot_model_spec.md) · [Report/CSV/log/hình](../results/lessons/l1_8_a/report.md) · [Index và audit](../notes/verification/l1_8_a/README.md). Trạng thái tại lần chạy A: chưa thực hiện Parts B–E, chưa chốt Δt hoặc contract v1; xem record CDE mới ở cuối README. Chưa xác nhận kết quả không phụ thuộc slot hay validation mạng. G1, V3/V10/V11 và HOLD Phase 4 giữ nguyên.

L1.8 **Part B** (22/10/2026): **13/13 test mới, 124/124 toàn repo PASS**. Toy p=s=5/8 được chạy ở tám mức Δt…Δt/128 bằng DP gộp state, không Monte Carlo. GS từ 0,9296875 xuống 0,307151637; GM=0; Richardson cuối GS≈0,302699661, Γ≈0,017362905 (ước lượng có điều kiện). Forward scorer khớp backward DP trong 3,6×10⁻¹⁵. Đã phát hiện hai sai khác làm tròn và vấn đề đổi model ở phép tách B6: fixed-M0 mode share tại Δt/128 là 17,81%, không lấy ≈11% của đường hybrid làm kết quả State-only. [Card](../notes/lessons/L1.8B_experiment_card.md) · [Protocol](../notes/lessons/L1.8B_refinement_protocol.md) · [Report/CSV/log/hình](../results/lessons/l1_8_b/report.md) · [Index/audit](../notes/verification/l1_8_b/README.md). Trạng thái tại lần chạy B: chưa khóa contract v1 hoặc Parts C–E; record CDE mới bổ sung bên dưới; Δt vật lý cuối vẫn chưa được chứng nhận; G1, V3/V10/V11 và HOLD Phase 4 giữ nguyên.

L1.8 **Parts C–E** (22/10/2026): đã chọn profile stable OFF.2μ/ON1.4μ, conditional stationary prior vô hạn, lưới24main+2negative+2stress, calibration3 và reserve16 chỉ tọa độ. Ngưỡng chính1%/equivalence.5%/numerical budget.25%, Cref=Lstar cùng ô/cùng dt. Contract v1 giữ25term; brief/card/decision log/closeout và exception V11 có record. [Report và số đo thực](../results/lessons/l1_8_cde/report.md) · [22 tests mới](../tests/test_l1_8_contract.py) · [11 thẻ+6b](../notes/lessons/L1.8D_decision_cards.md) · [Index/audit/git receipt](../notes/verification/l1_8_cde/README.md). Chỉ screen/budget/timescales trên lưới mới; chưa chạy contrast hoặc margin, chưa sinh reserve. A01 final dt/full-grid computational feasibility và human feedback vẫn pending; không xem freeze là hypothesis/network validation.

Kết quả CDE thực chạy: **146/146 tests PASS**,5.832 idle pairs không mismatch; backward/forward132 giá trị sai số tối đa7.11e-15. Main s_bt0,hai controls≈1; M20/M22/M24 báo alarm conservative budget, chưa chứng nhận full-grid feasibility. Artifact auditor dựng lại28D/6.776state rows PASS.
