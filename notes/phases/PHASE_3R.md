# Addendum triển khai — L3R.8 và đóng Phase 3R, 30/10/2026

**DL-097–102: Gate 3R = NARROW.** Phase 4 kiểm Hyp-MV/Hyp-SH (card v2) trên 270 CF ở mức mô hình.
D22 dời Phase 5 (`contract-v1.3-amend1`); realism UNSOURCED là outcome; audit L3R.3 đóng có phạm vi card v2;
L8 dời Phase 8. **P0-V10 OPEN** trước lần gọi CF; Phase 4 Bước 0 là nối runner (tái lập đúng dry-run B).
Tác giả xác nhận ngoài vở phần tự đọc/viết; nhãn AI chọn theo ủy quyền. G1. [Gate note](PHASE_3R_gate_note.md),
[closeout](PHASE_3R_closeout.md). Phần bên dưới giữ nguyên byte.

---

# Addendum triển khai — L3R.7 đóng gọn, 30/10/2026

**DL-095–096:** đóng L3R.7 bằng card v2. Card v2 khác v1 đúng bước làm tròn λA/λB/u = 1/100, do luật khai trước chọn;
card v1 giữ nguyên byte. Numerics v1.3.1-lean chọn (640, 4) trên 118 ca calibration, 0 UNRESOLVED.
n 60/BND 15 theo DL-077; root đã commit trước khi rút; 270 regime CF chỉ tham số, sinh một lần; dry-run B thông.
Chưa có outcome CF. Còn mở: D22, P0-V10/L8, realism HOLD_UNSOURCED, Gate 3R; Phase4 HOLD, G1.
[Report](../../results/lessons/l3r_7/lean_close/report.md). Phần bên dưới giữ nguyên byte.

---

# Addendum triển khai — L3R.7, 29/10/2026

**Cập nhật DL-078–079:** đã thực thi gate numerics,không còn chỉarithmetic.
Prereg0efddcc trước9jobs;3/3legacyanchorskhớp,stationary3/6complete,3/6CPUlimit.
595full/8numerics testsPASS;396.116CPU-s,2.21GiBmaxRSSmẫu.312globalcalibration
jobs dừng trước activation theo prereg. Numericsv1.3.1HOLD_FEASIBILITY_STAGE0;
chưa fullκ3h16costs/r/p95/D22/dry-runB. n/root/CF giữnull/0,Phase4HOLD/G1.
[Report numerics](../../results/lessons/l3r_7/numerics_report.md),
[CSV](../../results/R3R_numerics/20261029_01/metrics.csv).

Snapshot chuẩn bị trước calibration:

Phần chuẩn bị hoàn tất; **toàn bộ sampling gate chưa hoàn tất**. DL-075 sửa checker
receipt thiếu manifest mà không sửa card/receipt; DL-076 ghi design/power/sampler/
collision inventory/runner guard.587full/38targetedPASS;10kdraws test-only;
308inventoryrecords/245reservedv1.3keys;88unpairedpilotrows→UNRESOLVED đúng.
Không confirmationroot/CF/engine mới. DL-077: tác giả duyệt luật n,ủyquyền chọnB;
B48CPU-giờ,profile1worker trước rồi2/tốiđa4 theoRAM,1BLASthread/worker; n chưa chốt.
K*/dt*/route/tail/timing/r→numericsv1.3.1; coverage phải cóκ3,h16 vàinteriorrate1/1000.
Audited backend và dry-runB DEFERRED; D22/human/Gate3R còn mở. Phase4HOLD,G1 giữ.
[Thiết kế](../design/confirmation_v1_3.md),[report](../../results/lessons/l3r_7/report.md),
[completion](L3R_7_completion.json). Không đổi luật/card/tag cũ hoặc claim boundary.

# Addendum triển khai — L3R.6, 29/10/2026

Người phụ trách: **Doan Van Tai** · DL-073–074. Cards v1 **FROZEN** ở `1414d92`, receipt
[PHASE_3R_hypothesis_cards.lock.json](PHASE_3R_hypothesis_cards.lock.json) verify PASS. Tác giả chọn
phương án D (Part1 §11): Hyp-MV, Hyp-SH primary; không secondary; Γ̄ diagnostic vì Γ̄≥−min(ḠS,ḠM)
(discovery 3/162 cấu hình có thông tin, 70/73 cấu hình ḠS≥0 tự đạt). Ω⁺ MV+A/SH+A, Ω⁻ chỉ lật κ∈[1;3]
(ngoại suy), BND mô tả; measure khóa trong card; R4 bốn góc. 13 luật tóm tắt + 1 khai không nhìn dữ
liệu đều trong [forking log](PHASE_3R_forking_paths.md). 9/9 checks, 17 targeted/549 full PASS.
Đính chính lesson: Part3 §16(b) 20/30→U⁻→W2; Part1 §9.2 cận −min(ḠS,ḠM); Part2 h=2 là 0/30.
Không CF/engine/MC/seed; R09/R10 ngoài mọi vùng; R11 trong MV+A. L3R.7 học được; frame phải gọi
verify_cards trước; n/seed sau numerics v1.3.1 (phủ κ=3,h=16). AI soạn, tác giả duyệt; phép7 bằng
lời tác giả, Understanding/P0-V10/L8/T05 OPEN; audit L3R.3 HOLD, realism HOLD_UNSOURCED, G1, Phase4 HOLD.
[Report](../../results/lessons/l3r_6/report.md), [completion](L3R_6_completion.json).

---

# Addendum triển khai — L3R.5, 29/10/2026

Người phụ trách: **Doan Van Tai** · DL-071–072. Contractv1.3 **LOCKED_WITH_DEFERRED**,
annotatedtagcontract-v1.3→3d2359b;21input hashes tronglockreceipt. Tác giả chọn
P1stationary,RoE/C̄ref,εR1%/εE.5%,stakesdescriptive,c_sw0primary,camkếtD22,tagA.
532full/41targetedtestsPASS;234metadatarecords hợp lệ,216ID→210scientifickeys;
thiếuc_sw→162,thêmK/ref→228. KhôngCF/outcomesmới/MC/simulation/papersearch.
Khóa luậtR1–R8,u_max10%,2bướcescalationchung; levels/S1route/quadrature-tail
DEFERRED→numericsfreezev1.3.1trướcL3R.7sampling;D22implementation/audittrướcPhase4;
H0/H1fitbudget→Phase5. Không suy refinementdelta làerrorbound hoặc levelsfree
không thểảnhhưởngverdict. δindexedslottedfamily giữobjectivev1.2,khôngcontinuouslimit.
S1invariance cầnπ/J/policycốđịnh; không mặcđịnhkhiκđổi. Validitykhácframe.
[Contract](../01_definitions_v1_3.md),[brief](../00_research_brief_v1_3.md),
[report](../../results/lessons/l3r_5/report.md),[completion](L3R_5_completion.json).
L3R.6đạtđiềukiệncontract;cardchecksriêngchưalàm. AuditL3R.3HOLD,realism
HOLD_UNSOURCED,G1,Phase4HOLD;Understanding/P0-V10/L8/T05OPEN. Không sửa byte
contract/draft/briefv1.2 hoặc draftDL061;phần plan và addenda cũ bên dưới giữ nguyên.

---

# Addendum triển khai — L3R.4, 29/10/2026

Người phụ trách: **Doan Van Tai** · DL-069–070. Screen đã chạy, **realism HOLD_UNSOURCED**
ở cả MV/SH và hai bối cảnh DL-008. Không phải OUT hoặc empirical validation.
Generic preregcbed2bc,18/18checks/24replicatesPASS;24targeted/491fulltestsPASS.
Envelope6bef959 trước bảng216, exportfix830a187 giữ nguyên luật; labels1164500
trước saved-overlay.216ID/210cấu hình,432feature/1296label rows,toànUNSOURCED.
MV20/20distinct,SH80/78,giao14/14;f1.5/2/3 không exercise numeric robustness.
Ba nguồn mới được duyệt rồi đọc targeted; Excel26giữ23oldrecords, không L-self.
Sửa thứ tựA1→nguồn/envelope/commit→A2/labels→overlay; φ=u/(c−λB) khácη=u/2;
a/c=.6 và nền hai mức cố định; delayvirtualtimeaverage,buffer-tail≠drop;
stationary-postload≠transient;modecorr≠backlogcorr;actuation không suy dấuGS.
[Report](../../results/lessons/l3r_4/report.md),[worksheet](../realism/worksheet_v1.md),
[completion](L3R_4_completion.json). Scope chỉproposal choL3R.5,CFframe chưa chọn.
L3R.3HOLD/numericsNOT_FROZEN,contractv1.3DRAFT,G1/Phase4HOLD;
Understanding/P0-V10/L8/T05OPEN. Phần plannguồn và các addenda cũ giữ nguyên byte.

---

# Addendum triển khai — L3R.3, 29/10/2026

Người phụ trách: **Doan Van Tai** · DL-066–068. Audit đã chạy, **gate HOLD**;
evidence kỹ thuật PASS có giới hạn. 467fulltests/19oldtests/12mutants/19repro đạt,
C1 80/80,C2 80/80 sau arithmetic check,C3node8/8,max|z|2.313697.
Giữ original UNRESOLVED/FAIL/partial; K320/MCprecision extension ghi sau quan sát,
trước lần bổ sung. K160 costκ3 chưa đủ.25ppC; numericsv1.3/read-back vẫnOPEN.
KEEP lõi/snapshot và thêmtest/API ởexperiments; khôngpromotesrc hoặcmergepilot.
Không enginebug mới đượcxácnhận trongscope, khôngrerun216ID/pilotv2.
L1.5 có reportP4 checkerchung bỏsóttest; không chép nhận định thiếuevidence củalesson.
[Report](../../results/lessons/l3r_3/report.md),[code map](../verification/l3r_3/code_map.md),
[completion](L3R_3_completion.json). L3R.4 học tiếpđược; L3R.5 không tựfreezenumerics;
P0-V10/L8/T05/UnderstandingOPEN,G1/Phase4HOLD. Phần plannguồn bên dưới giữ nguyên byte.

---

# Addendum triển khai v1.2 — L3R.2, 28/10/2026

Người phụ trách/người soạn: **Doan Van Tai** · DL-065. [T07](../theory/T07_population_estimand.md)
soạn theo ủy quyền đã commit315d203 trước audit; Understanding/self-read-back vẫn OPEN.
16golden/439fulltests PASS,500laws seed20261028 không vi phạm,5/5mutantKILLED.
[Report](../../results/lessons/l3r_2/report.md), [completion](L3R_2_completion.json).
S1 bất biến chỉ khi marginalX/J/policy cố định; target stationary/periodic là giả định
chưa adopt. LargeΓ⇒harm là discovery, không phải chiều đảo của identity harm⇒Γ>0.
Chặn Γ[−σ̄,σ̄] mạnh hơn chặn lỏng trong nguồn; finite population không bảo đảm smooth.
Không kế thừa εR1% tự động; law/normalization/primary/η/numerics giữOPEN choL3R.5.
Không audit engine ởL3R.2, không CF/R09/R10 outcome; G1/Phase4HOLD giữ nguyên.
Tiếp theoL3R.3; không promote engine từ bảnT07 ủy quyền hoặc đóng ownership.
Phần nguồn plan bên dưới vẫn nguyên byte; addendum hiện tại ưu tiên về trạng thái.

---

# Addendum triển khai v1.1 — L3R.1, 28/10/2026

Người phụ trách: **Doan Van Tai** · DL-064. Phần dưới giữ nguyên nguồn plan v1.0 được cung cấp,
bao gồm attribution; addendum này ưu tiên khi trạng thái repo khác bản nguồn.

- V9 đã waive theo DL-054; P0-V10/L8/T05/Understanding vẫn OPEN. Không hỏi lại lựa chọn đã có.
- v1.3 đã có definitions/brief DRAFT theo DL-061, chưa contract/tag chính thức.
- Pilot là discovery tại a7435e9; không merge/xóa branch. Số/errata của các bản review
  chỉ là đầu vào đối chiếu cho tới khi script chạy tại máy này theo DL-064.
- Sẽ báo cả ID và cấu hình phân biệt; không áp câu “không trùng v1.2” như một giả định
  mặc định. Giữ mọi overlap phát hiện được, R09/R10 chỉ đọc tham số public.
- Phải tách nhãn eta=u/2 của pilot khỏi u/(capacity−lambdaB); dt/K của pilot không tự
  trở thành mức số v1.3. D22, chỉ báo và rubric chỉ báo phần thực có/thiếu, không suy diễn.
- Kết quả L3R.1 đã kiểm local:216ID/210cấu hình,6cặp trùng;45ID chạm23ôv1.2;
  điều kiện “không trùng” của plan không thỏa. E1–E7, dt1/120/K40, thiếuD22 và
  giới hạn nhãneta/rubric ghi trong discovery record, không sửa sourcepilot.
- Trên9cấu hình có refinement, max0,193329ppC̄; không suy cả210cấu hình đều đạt.
- Local423tests/13recounttests/3mutantsPASS là kiểm hiện tại; các số reviewer báo
  trong nguồn gốc bên dưới không được chép thành phép kiểm local khác.
- Hồ sơ L3R.1 sau run: [discovery record](PHASE_3R_discovery_record.md),
  [prereg](../../experiments/R3R_01_recount/prereg.json),
  [báo cáo thực thi](../../results/lessons/l3r_1/report.md).

---

# PHASE 3R — Reformulation v1.3: kiểm lại pilot, sàng lọc tính khả thi thực tế, và đóng băng một phép confirmation có thể sai

| Mục | Giá trị |
|---|---|
| Phiên bản | **v1.0 · 28/10/2026** |
| Vai trò | Lesson plan + research guide + execution protocol cho Phase 3R. Theo MASTER PLAN XIX.5, file này thắng phần tóm tắt trong MASTER PLAN |
| Căn cứ có thẩm quyền cao hơn file này | Final Review 05–06/10 (Main RQ); decision log, đặc biệt DL đóng Phase 3 với REFORMULATE và DL ghi outcome Step 1; contract v1.2 (cho tới khi v1.3 có tag); Phase 3 closeout. Nếu file này mâu thuẫn với chúng thì chúng thắng; sửa file này và ghi changelog |
| Đã đọc để soạn | MASTER PLAN v1.0 (06/10); Final Review (05–06/10); PHASE_3.md v2.0 (26/10); POST_PHASE3_CONTEXT.md; yêu cầu cấu trúc phase file (bản đã dùng cho PHASE_0) |
| Chưa xem | Repo (main @ `66f167d`, branch `explore/v13-population` @ `a7435e9`), code engine population, `results/explore_v13/SUMMARY.md`, raw results, file closeout/gate note Phase 3, file prereg/outcome Step 1, file contract v1.2, decision log. **Mọi con số của pilot trong file này lấy từ POST_PHASE3_CONTEXT; tôi chưa kiểm độc lập.** Mọi đường dẫn file mới trong file này là **đề xuất**; kiểm tên thật trong repo |
| Đã kiểm trong phiên soạn | Tính lại bằng script riêng (không dùng code của repo): toy "sửa state làm tệ hơn" và toy ba snapshot (bằng phân số); các identity và bất đẳng thức population trên 4.000 plant rời rạc ngẫu nhiên (0 vi phạm); các con số realism của mô hình fluid ON/OFF (công thức, đối chiếu với mô phỏng); bất biến khi đổi thang đơn vị và thang thời gian; bảng Clopper–Pearson và xác suất PASS; khoảng tin cậy Spearman; mức thổi phồng khi chọn chỉ báo tốt nhất trong 5 |
| Provenance | Claude (AI) soạn theo yêu cầu của tác giả. Tác giả đọc, sửa và chịu trách nhiệm trước khi dùng làm căn cứ. Số **minh họa** luôn được ghi là minh họa, không phải kết quả |

### Đọc file này thế nào

1. Đọc §0–§7 một lần để thấy toàn cảnh: đang ở đâu, phase này hỏi gì, tạo ra gì, theo thứ tự nào.
2. **Hai track**, giống PHASE_3. Track học (đọc, tự dẫn công thức, tính toy, viết nháp) **không bao giờ bị gate chặn**. Track thực thi (chạy code trên dữ liệu, khóa contract, sinh mẫu, đóng băng prereg) có thứ tự bắt buộc vì lý do **khoa học**, không vì thủ tục.
3. **Luật vàng của Phase 3R:** không tính bất kỳ *outcome* nào ($J$, $\Delta$, $\bar L_{sm}$, contrast, regret, tương quan giữa predictor và outcome) trên các regime dùng cho confirmation. Việc "chạy đúng một lần" thuộc Phase 4.
4. Khi kẹt ở một khái niệm: quay về ví dụ hai state hoặc ba snapshot của lesson đó và tính tay. Đừng đọc thêm tài liệu khó hơn trước khi ví dụ nhỏ đã rõ.
5. Cuối phase: §16–§21 (gate, validity/outcome, quyết định, closeout). Phần "sau Phase 3R" nằm ở §22.

---

## 0. Where I am now

### 0.1 Trạng thái ngày 28/10/2026

Trong cột "Nguồn", **CTX §n** là mục n của POST_PHASE3_CONTEXT.md (không phải mục của file này).

| Mục | Trạng thái | Nguồn |
|---|---|---|
| Phase 3 | Đóng với Gate A = **REFORMULATE** (`47f8e06`; trạng thái sau tag ở `1f620ec`). Lý do: với một snapshot cố định mỗi ô và hai action, giá trị của model repair gần như chỉ là "quyết định có lật hay không" (knife-edge), nên khó trả lời RQ ở mức operating regime. Engine **không** sai; thiết kế quá thô cho câu hỏi | CTX §4–5 |
| Step 1 (kiểm cơ chế "ba chế độ sai của M0") | Prereg `81b1c3f`, outcome `66f167d`, chạy một lần trên 38 ô A04 (đã là discovery). P(a) PASS (gần như kết quả cấu trúc); P(b) FAIL; P(c) FAIL. Theo bảng quyết định khóa trước: **fallback** — không xây v1.3 quanh fluid one-sided classifier hay boundary-error lens | CTX §7–8 |
| Population pilot | Branch `explore/v13-population` @ `a7435e9`, ghi rõ **EXPLORATION ONLY**, chưa merge (cố ý). 216 regime mới: Stage 1 = 60; Stage 2 = 108, **chọn sau khi đã thấy Stage 1**; Stage 3 = 48, có switching cost. Toàn bộ là **discovery thích nghi** | CTX §10–12 |
| Tín hiệu discovery (chưa phải evidence) | (1) Model repair có giá trị lớn ở vùng B ít headroom (λB = 8 trên capacity 10), κ ≈ 0,1–0,3, h = 8–16 s, một số λA ≈ 7–7,5. Mạnh nhất: regime X2065, $\bar G_M/\bar C_{\text{ref}}\approx$ 13,41%, khoảng 42% "stakes", P(flip) ≈ 0,47. (2) Sửa state làm tệ hơn khi vẫn dùng M0: $\bar G_S\le-1\%\,\bar C_{\text{ref}}$ ở 80/216 regime (79/168 nếu chỉ tính Stage 1+2 với c_sw = 0); tệ nhất ≈ −21,57%. (3) $\bar\Gamma$ gần như luôn ≥ 0 khi c_sw = 0. (4) Một chỉ báo chỉ dùng M0 (độ biến thiên khuyến nghị của M0 theo snapshot) xếp hạng giá trị model repair với Spearman ≈ +0,75 — **chọn hậu nghiệm trong 5 chỉ báo** | CTX §13–16 |
| Kiểm số pilot đã làm | So với engine Phase 3 ở 8 cặp snapshot: khớp. 19 brute-force ledger test. "GM identity gap" ≈ 0. Làm mịn K 40 → 80 và dt 1/120 → 1/240 s trên **9 regime được chọn**: chênh lệch tối đa ≈ 0,193 điểm phần trăm (pp) | CTX §11, §17 |
| Errata đã biết | **(E1)** 80/216, không phải 79/216; 79/168 cho Stage 1+2. **(E2)** chênh lệch làm mịn tối đa ≈ 0,193 pp → viết "≤ khoảng 0,20 pp", không phải "≤ 0,15 pp". **(E3)** Không được nói "switching cost không đổi bức tranh": Stage 3 không ghép cặp với Stage 2, và max $\bar G_M$ ở Stage 3 chỉ ≈ 0,65% so với 13,41% | CTX §34 |
| Exposure | 38 ô A04 + 10 ô R đã mở = discovery. **R09/R10 vẫn niêm phong.** 216 regime pilot = discovery | CTX §7, §12, §20 |
| main | `66f167d` | CTX §33 |
| Contract | v1.2 LOCKED cho estimand một snapshot. **v1.3 chưa tồn tại** | PHASE_3 v2.0; CTX §22 |
| Gap | G-level G1 (candidate gap), stability *fragile*. Discovery không nâng G-level (MASTER PLAN I.5) | MASTER PLAN I.5 |
| Điều kiện mang từ Phase 1–3 | P0-V10 (người đọc độc lập contract), L8 (người đọc prior boundary), V9 (heads-up GVHD), các mục closeout tác giả tự viết (Phase 1, 2, 3). **Trạng thái của chúng sau Phase 3 không có trong tài liệu tôi được xem → bạn xác nhận ở L3R.1** | PHASE_3 v2.0 §5.2 |
| MASTER PLAN | v1.0 (06/10): §0 còn ghi "Phase 0"; Part VI Phase 4 là "controlled core (Monte Carlo + discovery)" — lỗi thời so với hướng v1.3. Patch đề xuất ở Phụ lục D | MASTER PLAN |

### 0.2 Những gì bạn chưa biết hoặc chưa khóa

Nói đơn giản: pilot cho bạn một **tấm bản đồ phác**, vẽ bằng một **chiếc máy đo mới**. Bạn chưa biết ba điều: máy đo có chuẩn không; vùng đất trên bản đồ có tồn tại ngoài đời không; và nếu đi tới một chỗ *chưa từng đến* trong cùng vùng thì có thấy lại cảnh đó không. Cụ thể:

1. **Engine population có tính đúng không.** Các kiểm đã làm là cần nhưng chưa đủ cho confirmation. Chưa có phương pháp độc lập ở mức population (ví dụ Monte Carlo viết từ định nghĩa, không đọc code engine). Chưa kiểm "trung bình của mọi belief sau quan sát phải bằng prior". Chưa có mutation test cho tầng population. Làm mịn số mới chạy trên 9 regime chọn tay. Engine nằm trên branch chưa review.
2. **Estimand v1.3 chính xác là gì.** Chưa khóa: chuẩn hóa (% $\bar C_{\text{ref}}$ hay % "stakes" — pilot báo cả hai, và định nghĩa "stakes" cần đọc lại trong code), K và dt cuối, cái gì là primary outcome, luật hòa ở mức population.
3. **Phần nào của tín hiệu chỉ là identity.** Ví dụ: hễ $\bar G_S<0$ thì $\bar\Gamma>0$ là **bắt buộc về đại số** (L3R.2). Câu "penalty biến mất khi dùng M1" cũng là identity, vì S1M1 chính là oracle. Không thể "xác nhận" một điều không thể sai.
4. **Các con số có khả thi ngoài đời không.** κ = 0,1–0,3 với tuổi telemetry 1 s nghĩa là mode của traffic nền đổi mỗi 0,1–0,3 s. B dùng trung bình 80% capacity nhưng nhảy giữa 140% và 20% capacity. Horizon 8–16 s. Chưa có nguồn nào cho biết tổ hợp này có gặp ở mạng thật không, và ở loại mạng nào.
5. **Điều gì đã biết trong prior.** "Thông tin tốt hơn có thể làm hại một chính sách xấp xỉ" đã nằm trong danh sách đã biết của Phase 2 (K-RM1…K-RM3). Claim về state harm chỉ có thể mới ở **điều kiện và độ lớn** trong routing làm đổi tải.
6. **Thiết kế confirmation.** Chưa có khung lấy mẫu, cỡ mẫu, luật chấm, vùng đối chứng "có thể thất bại", hay scorer đã kiểm.

### 0.3 Phase 3R có còn hợp lý không? — audit trước khi viết chi tiết

POST_PHASE3_CONTEXT §21–22 và §35 đã đề xuất một Phase 3R gồm: đóng băng discovery → contract v1.3 → hai primary hypothesis + một secondary → sinh mẫu mới → prereg. Tôi kiểm đề xuất đó theo năm câu hỏi.

**(i) Phase 3R có đúng là bước tiếp theo không?** Có, vì ba lý do. Estimand đã đổi (một snapshot → phân phối snapshot), nên theo MASTER PLAN XIX.5 phải khóa lại contract và đi lại chuỗi Problem → … → Contribution. Tín hiệu hiện có là discovery thích nghi, chưa được viết thành prediction có thể sai. Và engine population chưa đạt chuẩn verification mà engine Phase 3 đã đạt. Đi thẳng vào confirmation lúc này là đo bằng một chiếc thước chưa kiểm, cho một câu hỏi chưa viết xong.

**(ii) Prerequisite nào chưa đạt?** Không có gì chặn việc *học* Phase 3R. Các điều kiện mang sang (P0-V10, L8, V9, mục tự viết) có trạng thái chưa rõ → xác nhận ở L3R.1. P0-V10 là điều kiện bạn tự đặt cho *thực thi Phase 4*; nó vẫn áp dụng cho confirmation v1.3, trừ khi bạn ghi một DL đổi điều kiện.

**(iii) Lesson nào nên chuyển vào hoặc ra?**
- *Vào:* (a) **audit engine** (L3R.3), trả lời đúng câu bạn hỏi "chạy có đúng không"; phần Monte Carlo kiểm chéo lấy từ vai trò E01 của Phase 4 cũ, nhưng ở đây chỉ dùng để **verification**, không để discovery. (b) **Realism screen** (L3R.4): MASTER PLAN đặt realism ở Phase 8, nhưng một sàng lọc thô ở mức bậc độ lớn, có nguồn, làm *bây giờ* thì rất rẻ và có thể NARROW hoặc kill trước khi đầu tư vào confirmation và mechanism (nguyên tắc #2 của MASTER PLAN: giảm uncertainty theo thứ tự rẻ nhất). (c) **Lọc identity và prior** cho từng hypothesis (trong L3R.6).
- *Ra:* intervention kiểm cơ chế, so sánh threshold null với dynamics (RQ2), feasible repair, packet simulator/testbed. Chúng thuộc các phase sau (§22).
- *Không làm lại:* literature survey. Phase 2 đã xong; Phase 3R chỉ đọc lại có mục tiêu.

**(iv) Cái gì trong plan hoặc đề xuất cũ đang dựa trên trạng thái lỗi thời?**
- Phase 4 của MASTER PLAN ("controlled core: Monte Carlo + discovery + baseline") không còn đúng. Discovery đã được làm bằng engine exact population. Phase 4 mới là **confirmation chạy đúng một lần**.
- Câu hypothesis "penalty giảm mạnh hoặc biến mất khi dùng M1" (POST_PHASE3_CONTEXT §24) chứa một identity → phải viết lại.
- Cụm từ "fresh telemetry / fresh state có hại": theo contract v1.2, S1 là state thật tại $t_0$ **gồm cả mode** của traffic nền — một quyền oracle, vì không telemetry nào đo được mode. Đó nhiều hơn "telemetry tươi hơn". Câu chữ phải sửa (L3R.2, Khái niệm 6).

**(v) Scientific blocker nào phải đưa vào ngay?**
1. **Identity coupling.** $\bar G_S<0\Rightarrow\bar\Gamma>0$, và khi đó $\bar G_{M\mid S_1}\ge\lvert\bar G_S\rvert+\bar G_M$. Vì vậy hypothesis về model value phải dùng $\bar G_M$ (dưới state cũ), để không bị hypothesis về state harm kéo theo.
2. **Ngưỡng có trước dữ liệu.** ε_R = 1% đã khóa *trước* pilot → giữ. Đổi ngưỡng sau khi thấy 13% là chọn ngưỡng theo outcome.
3. **Realism.** Nếu vùng tín hiệu nằm ngoài mọi bối cảnh mạng thật, phải biết *bây giờ*, không phải sau ba phase.
4. **Một primary normalization.** Hai thước (% $\bar C_{\text{ref}}$ và % stakes) trả lời hai câu hỏi khác nhau.
5. **Vùng đối chứng phải có thể thất bại.** Không lấy một vùng mà mọi contrast bằng 0 một cách tầm thường.

**Bảng sửa đổi so với đề xuất trong POST_PHASE3_CONTEXT**

| # | Đề xuất / plan cũ | Vấn đề | Sửa trong file này | Vì sao |
|---|---|---|---|---|
| 1 | Phase 3R = freeze → contract → hypotheses → prereg | Chưa có bước verification engine ở mức confirmation | Thêm L3R.3: Monte Carlo độc lập viết từ định nghĩa, kiểm posterior → prior, mutation test, tái lập từ checkout sạch, chính sách số cho từng regime | Bạn hỏi đúng câu "chạy có đúng không"; pilot mới có kiểm điểm (spot-check) |
| 2 | Realism để Phase 8 | Có thể phát hiện quá muộn rằng vùng tín hiệu không có thật | Thêm L3R.4: realism screen ở mức thiết kế, không chạm outcome | Kill/narrow rẻ nhất phải làm trước confirmation |
| 3 | Hyp 2: "S1M0 tệ hơn S0M0, penalty biến mất dưới M1" | Vế sau là identity | Hyp-SH chỉ nói về dấu và độ lớn của $\bar G_S$; các hệ quả identity khai báo riêng | Không "xác nhận" điều không thể sai |
| 4 | Complementarity là một finding riêng | Trong vùng harm, $\bar\Gamma>0$ là bắt buộc | Complementarity chỉ là một prediction riêng *ngoài* vùng harm (nếu muốn) | Không đếm một kết quả hai lần |
| 5 | Hyp 1 "model repair có giá trị" (không nói contrast nào) | Nếu dùng $\bar G_{M\mid S_1}$ thì bị Hyp-SH kéo theo | Hyp-MV dùng $\bar G_M$ (state cũ) | Hai primary độc lập về logic |
| 6 | "fresh telemetry có hại" | S1 gồm mode (quyền oracle) | Viết "state repair (backlog + mode tại $t_0$)"; tách $\bar F/\bar V$ theo D22 báo làm diagnostic | Không nói quá điều đã đo |
| 7 | SESOI chưa nói rõ | Dễ chọn lại sau khi thấy 13% | Giữ ε_R = 1% $\bar C_{\text{ref}}$ (độ nhạy 0,5% và 2%), ε_E = 0,5% | Ngưỡng có trước dữ liệu |
| 8 | "% of Cref" và "% of stakes" cùng tồn tại | Hai thước, hai câu hỏi | Một primary (đề xuất $\bar C_{\text{ref}}$), một secondary (stakes, định nghĩa tường minh) | Một câu hỏi, một thước |
| 9 | Regime confirmation "mới hoàn toàn" | Chưa nói cách sinh | Rút ngẫu nhiên trong vùng định nghĩa bằng luật, seed khóa trước, chỉ sinh tham số | Không chọn tay, không jitter quanh đỉnh |
| 10 | Làm mịn trên 9 regime | Regime confirmation có thể nằm ở vùng số khó hơn | Kiểm cặp mức số cho **mọi** regime + luật leo thang | Không để artefact số thành effect |
| 11 | Switching cost | Stage 3 không ghép cặp với Stage 2 | Primary c_sw = 0; switching cost thành phép can thiệp ghép cặp ở Phase 5 (hoặc secondary mô tả ở Phase 4) | Không claim robustness chưa kiểm |
| 12 | Predictor M0-only | Spearman phụ thuộc quần thể regime; có thể chỉ phản ánh hình học quyết định | Khóa nguyên công thức; báo theo từng stratum; so với một predictor ngây thơ chỉ dùng tọa độ thiết kế | Biết predictor thêm được gì thật |
| 13 | Gate của Phase 3R chưa rõ | — | Gate 3R đóng vai trò Gate B của MASTER PLAN (đóng băng trước khi chạm dữ liệu xác nhận) | Nối với hệ gate cũ |
| 14 | Phase 4–10 của MASTER PLAN | Lỗi thời | Roadmap mới ở §22; patch MASTER PLAN ở Phụ lục D | Hoàn thiện phần sau Phase 3R |
| 15 | Branch exploration | — | Không merge; gắn tag; engine vào main qua review + test + provenance | Tách discovery khỏi code dùng cho confirmation |

### 0.4 Ký hiệu dễ nhầm (bổ sung cho bảng §0.4 của PHASE_3)

| Ký hiệu | Nghĩa trong file này | Dễ nhầm với | Cách viết |
|---|---|---|---|
| $G$ và $\bar G$ | $G$: contrast cho **một** snapshot (Phase 3). $\bar G$: trung bình theo phân phối snapshot (v1.3) | — | Population luôn có gạch ngang |
| $\bar C_{\text{ref}}$ | $\bar L_{11}$: cost kỳ vọng của oracle trên cả regime | $C_{\text{ref}}$ của một ô Phase 3 | "$\bar C_{\text{ref}}$" |
| $\bar\sigma$ (stakes) | Đề xuất: $\mathbb E_\pi\lvert\Delta(x)\rvert$. Định nghĩa của pilot cần đọc lại | σ là độ lệch chuẩn | "stakes $\bar\sigma$" |
| X#### | Regime discovery của pilot (ví dụ X2065) | — | "regime X2065" |
| CF-### | Regime confirmation (sinh ở L3R.7) | Control C1–C6 của A01; $C_{\text{ref}}$ | "regime CF-017" |
| Ω_MV+, Ω_MV−, Ω_SH+, Ω_SH−, Ω_BND | Vùng tọa độ của hypothesis | Ô held-out R01–R12; regret $R_{sm}$ | Luôn có Ω |
| Hyp-MV, Hyp-SH, Hyp-MI | Hypothesis model value / state harm / chỉ báo M0 | HC1, HM1, HP1 (MASTER PLAN); $H_0/H_1$ (threshold null vs dynamics); $H$ (số slot) | Luôn có "Hyp-" |
| P(a), P(b), P(c) | Prediction của Step 1 | Ô P01, P02; paper [P01]… | "Step 1 P(b)" |
| K | Số nút quadrature cho phân phối snapshot | Tập ô K2…K6; kill criteria K1…K14; danh sách K-RM… | "K (quadrature)" |
| pp | Điểm phần trăm (percentage point) | % tương đối | "0,193 pp" |
| Stage 1/2/3 | Ba đợt quét của pilot | Phase | "Stage 2" |

### 0.5 Hai track, luật provenance, kỷ luật exposure

- **Track học** không bao giờ bị gate chặn. **Track thực thi** có thứ tự (§7).
- **Exposure.** Được làm trong Phase 3R: sinh *tham số* regime; tính đại lượng *thiết kế* (utilization, κ, h/τ, phân phối dừng phục vụ realism); chạy mọi thứ trên regime discovery và toy. **Không** được làm: tính bất kỳ outcome nào trên regime confirmation.
- **Provenance** (giữ luật của PHASE_3 v2.0, L3.1). Validity của một prereg phụ thuộc *thời điểm commit*; ownership phụ thuộc *người viết*. POST_PHASE3_CONTEXT, review hậu nghiệm và SUMMARY của pilot có thể do AI soạn → ghi đúng nhãn. Một hypothesis card do AI soạn, commit trước khi có dữ liệu, vẫn là prereg hợp lệ; nhưng repo không được ghi "tác giả dự đoán" khi bạn chưa tự giải thích lại được nó.

---

## 1. Phase question

**Câu hỏi chính của Phase 3R:**

> Trước khi chạy confirmation đúng một lần: (a) pilot population có được tính đúng như định nghĩa không; (b) luật chơi v1.3 đo chính xác điều gì, và phần nào chỉ là identity; (c) các vùng discovery có nằm trong dải tham số gặp được ở ít nhất một bối cảnh mạng thật không; và (d) các claim còn lại đã được viết thành prediction có thể sai, không trùng prior, với một thiết kế confirmation đủ khả năng phân biệt chưa?

| ID | Câu hỏi | Lesson trả lời | Câu trả lời trông như thế nào |
|---|---|---|---|
| Q3R.1 | Engine population có tính đúng estimand đã định nghĩa không, và đúng tới mức nào về số? | L3R.2, L3R.3 | Báo cáo audit: từng kiểm PASS/FAIL. Nếu có bug: bug gì, đổi con số pilot ra sao |
| Q3R.2 | Estimand v1.3 chính xác là gì; contrast nào là identity, contrast nào có thể sai? | L3R.2, L3R.5 | Note T07 + contract v1.3 có tag + danh sách identity |
| Q3R.3 | Tổ hợp tham số của vùng discovery có gặp ở mạng thật không, ở bối cảnh nào? | L3R.4 | Realism envelope v1 có nguồn; bảng IN/EDGE/OUT cho 216 regime |
| Q3R.4 | Sau khi trừ identity và điều đã biết, claim nào còn đứng, và viết chúng thành prediction có thể sai thế nào? | L3R.6 | 1–2 primary + tối đa 1 secondary hypothesis card, **hoặc** lý do ghi rõ vì sao không còn claim nào |
| Q3R.5 | Thiết kế confirmation có phân biệt được PASS với FALSIFY không, và chạy được trong ngân sách không? | L3R.7, L3R.8 | Prereg + danh sách regime + scorer đã test + bảng khả năng phân biệt; Gate 3R |

---

## 2. Why this phase exists

**Vấn đề.** Pilot cho tín hiệu lớn: model value tới 13,41% $\bar C_{\text{ref}}$, state harm tới −21,57%. Một con số lớn là lý do để **nghi ngờ** trước khi là lý do để vui. Có ba lời giải thích cạnh tranh cho một con số lớn:

1. hiện tượng thật của mô hình;
2. bug hoặc artefact số;
3. tham số không gặp ngoài đời.

Ngoài ra, cách tìm ra con số (chọn Stage 2 theo Stage 1; chọn chỉ báo tốt nhất trong 5) làm nó **lạc quan** ngay cả khi hiện tượng là thật. Phase 3R loại trừ (2), đo (3), và viết (1) thành một câu có thể sai trên dữ liệu chưa từng thấy.

**Vì sao nó nằm ở đây.** Không thể prereg khi chưa biết estimand (contract). Không nên prereg khi chưa biết engine đúng (audit). Không nên đầu tư confirmation cho một vùng không có thật (realism). Và phải prereg **trước** khi có dữ liệu mới, vì đó là toàn bộ ý nghĩa của confirmation.

**Nếu bỏ qua Phase 3R và chạy confirmation ngay, chuyện gì có thể sai:**

1. **Bug thành phát hiện.** Ví dụ: quadrature bỏ sót khối xác suất tại backlog = 0 → $p(y)$ sai → belief của S0 sai → $\bar G_S$ có thể đổi dấu. Confirmation khi đó "xác nhận" chính bug đó, vì cùng engine.
2. **Hypothesis vẽ theo đỉnh discovery.** Confirmation thất bại vì regression to the mean, hoặc "thành công" vì vùng đối chứng tầm thường.
3. **Identity được báo như phát hiện** (complementarity trong vùng harm).
4. **Điều đã biết được claim như mới** ("thông tin có thể hại chính sách xấp xỉ").
5. **Realism lộ ra sau ba phase.** Cả chuỗi phải NARROW muộn, với chi phí lớn hơn nhiều.
6. **Ngưỡng hoặc luật chấm được chọn sau khi thấy outcome.** Mọi verdict mất giá trị.

---

## 3. What this phase does NOT do

- **Không** chạy confirmation; không tính outcome trên regime CF.
- **Không** quét thêm regime discovery để "tìm vùng đẹp". Ngoại lệ duy nhất: nếu audit tìm ra bug, chạy lại **đúng** 216 regime cũ bằng engine đã sửa ("pilot v2"). Đó vẫn là discovery.
- **Không** thử thêm chỉ báo, không thử biến thể của chỉ báo M0.
- **Không** intervention kiểm cơ chế, không so threshold null với dynamics (RQ2) → Phase 5.
- **Không** packet simulator, ns-3, Mininet → Phase 6. Monte Carlo ở L3R.3 chỉ để verification.
- **Không** feasible repair, không chi phí telemetry thật, không baseline vận hành → Phase 7.
- **Không** claim novelty, **không** nâng G-level.
- **Không** dùng 38 ô A04, 10 ô R đã mở, hay R09/R10 cho bất cứ phép xác nhận nào.
- **Không** merge branch exploration như thiết kế cuối.
- **Không** đổi Main RQ; không đổi ε_R hay ε_E sau khi thấy pilot.
- **Không** claim "switching cost không đổi bức tranh".
- **Không** yêu cầu tác giả gửi, báo cáo hay chép bất kỳ trao đổi riêng nào.

> **Phase 3R kết thúc khi:** Gate 3R có một nhãn trong decision log, dựa trên: engine population đã qua audit (hoặc lý do HOLD ghi rõ); contract v1.3 có tag; realism envelope v1 có nguồn và bảng phân loại vùng discovery; hypothesis cards, thiết kế confirmation và scorer đã đóng băng với hash — **và chưa có bất kỳ outcome nào của regime confirmation được tính.**

---

## 4. Connection to Main RQ

> *For load-changing routing actions, how do improvements in current-state information and action-response model fidelity differ and interact in their effect on expected decision regret?*

Main RQ **KEEP**, giữ nguyên câu chữ. Cách diễn đạt trong POST_PHASE3_CONTEXT §2 ("trong các operating regime khác nhau, decision value của hai repair thay đổi thế nào, và khi nào giá trị của repair này phụ thuộc repair kia") là một cách *đọc* RQ, không phải RQ mới. Estimand population thật ra **gần chữ "expected decision regret" hơn** estimand một-snapshot: nó lấy kỳ vọng theo mọi snapshot mà controller có thể gặp trong một regime.

### 4.1 Vị trí trong research flow

```text
Trạng thái 28/10/2026
  main @66f167d: Phase 3 đóng (REFORMULATE) · Step 1: P(a) PASS, P(b) FAIL, P(c) FAIL
  explore/v13-population @a7435e9: pilot 216 regime (DISCOVERY, chưa merge)
        │
        ▼
PHASE 3R — không có outcome confirmation nào
  L3R.1 Re-entry: đóng băng discovery · errata · exposure
  L3R.2 Hiểu estimand population (identity nào, cái gì có thể sai)
     ├──► L3R.3 Audit engine (verification)          ─┐  làm song song
     └──► L3R.4 Realism screen (chỉ mức thiết kế)    ─┤
                                                      ▼
  L3R.5 Contract v1.3 LOCK (tag contract-v1.3)
  L3R.6 Hypothesis cards (+ lọc identity, lọc prior)
  L3R.7 Thiết kế confirmation (mẫu mới, luật chấm, scorer, dry-run)
  L3R.8 Freeze + người đọc + Gate 3R + closeout
        │  Gate 3R  (≈ Gate B của MASTER PLAN)
        ▼
PHASE 4 — Confirmation v1.3: chạy đúng một lần, chấm tự động        (Gate C)
        ▼
PHASE 5 Mechanism (intervention, RQ2)                                (Gate D)
PHASE 6 Independent validation (packet DES / finite buffer / …)      (Gate E)
PHASE 7 Practical relevance (feasible repair, chi phí, timing, RQ3)  (Gate F)
PHASE 8 Synthesis + final novelty audit                              (Gate G)
PHASE 9 Paper
```

### 4.2 Output của Phase 3R đi đâu, và nếu sai thì hỏng ở đâu

| Output Phase 3R | Phase dùng nó | Nếu output này sai thì |
|---|---|---|
| Discovery record + errata | L3R.6 (viết hypothesis), §22 | Hypothesis viết từ con số lệch raw |
| T07 (định nghĩa + identity) | L3R.3, L3R.6, Phase 4 | Identity bị báo như phát hiện; audit không có đáp án |
| Engine population đã audit | Phase 4 (chạy CF), Phase 5 (intervention) | Confirmation "xác nhận" bug |
| Realism envelope v1 | L3R.5 (scope), L3R.7 (frame), Phase 6–7 | Claim đúng trong mô hình nhưng ở vùng không ai gặp |
| Contract v1.3 | Mọi phase sau | Đổi luật sau khi thấy dữ liệu |
| Hypothesis cards | Phase 4 (chấm), Phase 5 (cơ chế để can thiệp) | Prediction không thể sai, hoặc trùng prior |
| Thiết kế CF + scorer + prereg | Phase 4 | Verdict mơ hồ, mẫu thiên lệch, thiết kế không phân biệt được |

### 4.3 Phase 3R đóng góp phần nào cho RQ

| Sub-RQ | Phase 3R đóng góp | Không đóng góp |
|---|---|---|
| **RQ1** characterization | Định nghĩa estimand population; viết claim theo vùng (Hyp-MV, Hyp-SH) thành dạng kiểm được | Chưa có evidence; Phase 4 mới kiểm |
| **RQ2** mechanism/falsification | Ghi rõ phần nào là identity; khóa chỉ báo M0-only (một predictor kiểu "hình học quyết định") để Phase 5 dùng làm đối chứng | Chưa so null với dynamics; chưa intervention |
| **RQ3** practical relevance | Realism screen ở mức bậc độ lớn; giữ ε_R làm ngưỡng thực dụng | Chưa feasible repair, chưa chi phí thật |

**Chuỗi nghiên cứu sau Phase 3R:** Problem (giữ) → Gap (G1; candidate gap được thu hẹp thành "điều kiện theo regime của giá trị hai repair ở mức population trong finite-load rerouting") → RQ (KEEP) → **Hypothesis** (Hyp-MV, Hyp-SH, Hyp-MI — tạo ở Phase 3R) → **Method** (engine exact population — audit ở Phase 3R) → Experiment (CF, Phase 4) → Evidence (tầng E1, trong mô hình đã khai báo) → Contribution (chưa có).

---

## 5. Prerequisites

### 5.1 Artifact phải có

| Artifact | Ở đâu | Dùng ở | Trạng thái (theo context) |
|---|---|---|---|
| Phase 3 closeout + gate note | main | L3R.1 | Có — đọc lại |
| Step 1 prereg & outcome | `81b1c3f`, `66f167d` | L3R.1, L3R.6 | Có |
| Branch pilot | `explore/v13-population` @ `a7435e9` | L3R.1, L3R.3 | Có, chưa merge |
| `results/explore_v13/SUMMARY.md` + raw | branch | L3R.1 | Có; 3 errata |
| Engine Phase 3 + golden (theo PHASE_3 v2.0: `src/smr/cells.py`, `src/smr/factorial.py` — kiểm tên thật) | main | L3R.3 | Có |
| Contract v1.2 (D1–D25) | main | L3R.2, L3R.5 | LOCKED |
| Đầu ra Phase 2: `already_implied.md`, `prior_boundary.md`, các danh sách đã biết (K-RM…), `terms.md` | main | L3R.6 | Có |
| Exposure register, decision log, seed registry | main | Mọi lesson | Có |

### 5.2 Điều kiện mang sang: chặn bước thực thi nào, không chặn gì

| Điều kiện | Nguồn | Chặn bước thực thi nào | Không chặn | Lựa chọn hợp lệ | Làm ở |
|---|---|---|---|---|---|
| Không tính outcome trên regime CF | Khoa học | Luôn áp dụng | — | — | Toàn phase |
| Tag branch + exposure entry trước mọi phân tích mới trên dữ liệu pilot | Khoa học | L3R.3, L3R.4 Part D, L3R.6 | Học | — | L3R.1 |
| Audit PASS trước khi khóa numerics trong contract | Khoa học (ER5) | L3R.5 mục numerics; L3R.7 dry-run | Học, viết contract nháp | — | L3R.3 |
| Envelope + luật phân loại commit trước khi phân loại | Khoa học (chống "motivated realism") | L3R.4 Part D | — | — | L3R.4 |
| Contract v1.3 có tag trước hypothesis cards | Khoa học | L3R.6 | Nháp hypothesis | — | L3R.5 |
| Prereg + hash trước Phase 4 | Khoa học | Phase 4 | — | — | L3R.8 |
| MASTER PLAN X.3 #2: tự dẫn công thức trước khi đưa code vào `src/smr/` | Điều kiện GVHD đặt 25/09 | Đưa engine population vào `src/smr/` | Code ở `experiments/` có nhãn | T07 tác giả viết; hoặc author-attested; hoặc DL đổi điều kiện | L3R.2, L3R.3 |
| P0-V10: người đọc độc lập contract | Tác giả, closeout Phase 1 | Thực thi Phase 4 | Toàn bộ Phase 3R | Buổi đọc contract v1.3 (L3R.8); hoặc DL đổi điều kiện | L3R.8 |
| V9: heads-up GVHD | Tác giả | Do bạn đặt | — | Gửi / ghi DL sửa / giữ nguyên | L3R.1 |
| Closeout tự viết (Phase 1–3) | Luật ownership | Không chặn thực thi | — | Làm, hoặc ghi "còn mở" | L3R.1 |

### 5.3 Math prerequisites

Phase 3R dùng xác suất rời rạc, đại số, và một ít thống kê cho tỉ lệ và tương quan. Không cần lý thuyết nâng cao.

| Mức | Chủ đề | Dùng ở | Ôn tới đâu thì đủ |
|---|---|---|---|
| **Must know** | Xác suất có điều kiện; Bayes rời rạc | L3R.2, L3R.3 | Tính tay posterior hai state từ một observation |
| | Luật kỳ vọng toàn phần $\mathbb E[\mathbb E[X\mid Y]]=\mathbb E[X]$ | L3R.2, L3R.3 | Giải thích vì sao trung bình của mọi posterior bằng prior |
| | Argmin; regret ≤ $\lvert\Delta\rvert$ theo từng state | L3R.2 | Chứng minh $\bar G_M\le\bar\sigma$ trong 3 dòng |
| | Đại số bảng 2×2 (đã học ở Phase 3) | L3R.2, L3R.6 | Từ bốn $\bar L$ tính được sáu contrast |
| | Tỉ số không thứ nguyên, đổi đơn vị | L3R.4 | Giải thích vì sao capacity = 10 chỉ là đơn vị |
| | Hàm mũ, đuôi dạng $e^{-\theta x}$ | L3R.4 | Đọc "mỗi khi tăng 1/θ, xác suất giảm e lần" |
| | Monte Carlo: SE = s/√N; common random numbers (CRN); z-score | L3R.3 | Tính N cần để SE nhỏ hơn một ngưỡng |
| | Tỉ lệ nhị thức; cận tin cậy một phía (Clopper–Pearson) | L3R.6, L3R.7 | Đọc bảng cận và bảng xác suất PASS |
| | Spearman rank correlation | L3R.6, L3R.7 | Tính tay trên 5 cặp số |
| **Nice to know** | Quadrature (tích phân xấp xỉ bằng tổng có trọng số); atom | L3R.3 | Biết vì sao "atom" phải là một nút riêng |
| | Fisher z cho khoảng tin cậy của tương quan | L3R.6 | Đọc bảng khoảng |
| | Bonferroni / Holm | L3R.7 | Vì sao hai primary dùng cận 97,5% |
| | Fluid queue hai trạng thái; telegraph process | L3R.4 | Chỉ ý tưởng, không cần dẫn |
| **Not needed yet** | Bootstrap phức tạp, Bayesian hierarchical model, causal inference hình thức, Lévy queue, POMDP, GNN/RL, ns-3 | — | — |

### 5.4 Literature trong Phase 3R: chỉ đọc lại có mục tiêu

Phase 3R **không** mở survey mới. Mọi phiên tìm nguồn mới theo `AGENTS.md` của repo: Hỏi → Tìm → Kiểm → Duyệt → Đọc → Ghi → Dừng; tối đa 3 nguồn mới mỗi lượt; tác giả duyệt trước khi tải PDF hay tạo note.

| Nguồn | Vì sao đọc (trong Phase 3R) | Phần nào | Câu hỏi phải trả lời | Ghi lại gì | Ảnh hưởng tới RQ/claim | Khi nào |
|---|---|---|---|---|---|---|
| Note Phase 2: `already_implied.md`, danh sách K-RM1…K-RM3, `prior_boundary.md` | Lọc prior cho Hyp-SH | Các dòng về "thông tin thêm làm hại chính sách xấp xỉ" | Điều gì đã có tên, dưới giả định nào? | Một câu "Hyp-SH khác ở trục E/M/R nào" | Câu chữ Hyp-SH; không claim "info có thể hại" là mới | L3R.6 Part C |
| [P11] Strong–Oakley (EVMI) | Lọc prior cho Hyp-MV | Formulation, §2.4 | "Giá trị của cải thiện model, lấy trung bình theo state" có đúng là EVMI không? | Khác biệt cụ thể (thông tin cũ; action đổi tải; cost cumulative) | Không claim khái niệm "value of model improvement" là mới | L3R.6 Part C |
| [P12] + mục OεRE trong `terms.md` | Nhánh equivalence nếu Hyp-MV FAIL ở một vùng | Definition 1, §3.1 | Câu "M0 đủ tốt ở vùng X" khác value equivalence ở đâu? | Hai khác biệt | Câu chữ của vùng đối chứng | L3R.6 |
| [P13] + note T-H1 (`horizon_transient.md`) | Hyp-MV có "horizon đủ dài" | Theorem 1; §6 | Objective cumulative (D13) khác time-average thế nào khi h dài? | Một câu diễn giải | Không nói "long-run loss" | L3R.6 |
| Nguồn realism (danh sách ứng viên ở L3R.4 Part B) | Dải tham số thực tế | Theo từng đại lượng | Theo bảng ở L3R.4 | Worksheet (Phụ lục C) | Scope và cờ assumption | L3R.4 |

### 5.5 Công cụ và ngân sách

- Môi trường Python của repo; tái lập được từ checkout sạch.
- Engine exact không cần RNG. Monte Carlo ở L3R.3 cần RNG: mọi seed ghi vào seed registry.
- **Ngân sách tính toán cho confirmation chưa biết**: thời gian chạy một regime đo ở L3R.3 Part D; cỡ mẫu chọn ở L3R.7 Part B dựa trên số đó.

---

## 6. Phase outputs

Mỗi output tồn tại vì nó giảm một rủi ro nghiên cứu cụ thể. Đường dẫn là đề xuất.

| Output | Nơi lưu (đề xuất) | Rủi ro được giảm | Lesson |
|---|---|---|---|
| Discovery record + errata + tag branch + dòng exposure | `notes/phases/PHASE_3R_discovery_record.md`; tag `explore-v13-pilot`; exposure register | Trộn discovery với evidence; số trôi khỏi raw | L3R.1 |
| DL "mở Phase 3R" | Decision log | Điều kiện bị quên hoặc bị áp đặt | L3R.1 |
| T07 + sanity list v1.3 + golden toy | `notes/theory/T07_population_estimand.md`; `tests/` | Identity bị coi là finding; audit không có đáp án | L3R.2 |
| Báo cáo audit + engine population trong main + Monte Carlo độc lập | `notes/phases/PHASE_3R_engine_audit.md`; `src/smr/population.py`; `experiments/R3R_03_mc/` | Bug thành phát hiện (ER5) | L3R.3 |
| Realism envelope v1 + bảng đại lượng suy ra cho 216 regime | `notes/design/realism_envelope_v1.md`; `results/R3R_04/` | Effect chỉ có ở vùng không có thật (SR5, SR6) | L3R.4 |
| Contract v1.3 + brief/claim boundary cập nhật + schema regime + tag | `notes/01_definitions_v1_3.md`; tag `contract-v1.3` | Đổi luật sau khi thấy dữ liệu | L3R.5 |
| Hypothesis cards + forking-paths log | `notes/phases/PHASE_3R_hypothesis_cards.md` | SR2, kill-K8, claim trùng prior | L3R.6 |
| Thiết kế confirmation: frame, strata, danh sách regime (chỉ tham số), scorer + test, dry-run | `notes/design/confirmation_v1_3.md`; `experiments/CF_v13/` | Pseudo-replication; thiết kế không phân biệt được; luật chấm mơ hồ | L3R.7 |
| Prereg có hash, record người đọc, gate note, closeout, patch MASTER PLAN, tag | `experiments/CF_v13/prereg.md`; `notes/phases/` | Trôi sang Phase 4 theo quán tính | L3R.8 |

---

## 7. Lesson map

| Lesson | Một mục tiêu | Tầng evidence | Phụ thuộc (track thực thi) | Ước lượng |
|---|---|---|---|---|
| **L3R.1** Re-entry | Đóng băng discovery; errata; exposure; trạng thái điều kiện | — | — | 0,5–1 ngày |
| **L3R.2** Estimand population | Hiểu và viết định nghĩa; biết cái gì là identity | E0 | — | 1–2 ngày |
| **L3R.3** Audit engine | Chứng minh engine tính đúng (hoặc tìm bug) | E1 verification | Tag + exposure (L3R.1); T07 | 4–7 ngày |
| **L3R.4** Realism screen | Biết các tỉ số có gặp ngoài đời không | Thiết kế + literature | Tag + exposure (L3R.1) | 3–5 ngày (+ thời gian đọc) |
| **L3R.5** Contract v1.3 | Khóa luật chơi mới | — | L3R.2, L3R.3, L3R.4 | 1–2 ngày |
| **L3R.6** Hypothesis cards | Viết prediction có thể sai | E0 + bảng discovery | Contract có tag | 2–3 ngày |
| **L3R.7** Thiết kế confirmation | Mẫu mới, luật chấm, scorer, dry-run | — | L3R.6 | 3–5 ngày |
| **L3R.8** Freeze + Gate 3R | Đóng băng, người đọc, gate, closeout | — | Tất cả | 1–2 ngày (+ chờ người đọc) |

Tổng ước lượng: khoảng 3–5 tuần làm việc, L3R.3 và L3R.4 chạy song song. Đây là ước lượng công sức, không phải hạn chót. **Gate thắng lịch.** Nếu Phase 3R vượt khoảng 6 tuần, dừng lại và tự hỏi: mình có đang phình quy trình không (ER1)?

**Ràng buộc thứ tự commit (track thực thi).** Lịch sử git là bằng chứng rằng bạn không nhìn trước. Các ràng buộc sau phải đọc được từ `git log`:

1. Tag branch pilot + dòng exposure có trước mọi phân tích mới trên dữ liệu pilot.
2. T07 (định nghĩa) có trước kết luận của audit.
3. Dung sai của phép kiểm Monte Carlo được viết trước khi chạy Monte Carlo.
4. Envelope (dải + luật phân loại) commit trước khi phân loại vùng discovery.
5. Audit PASS có trước phần numerics của contract; tag `contract-v1.3` có trước hypothesis cards.
6. Frame + seed + strata + cỡ mẫu commit trước khi sinh danh sách regime; danh sách sinh **một lần**.
7. Prereg + scorer + hash commit trước Phase 4.
8. Không có outcome CF nào xuất hiện trong git trước bước 7.

---

## 8. Lesson 3R.1 — Re-entry: đóng băng discovery, sửa errata, ghi exposure

#### Mục tiêu
Sau lesson này tôi kể lại được, không nhìn tài liệu, đường đi từ Phase 3 tới pilot; phân loại được mỗi phát biểu của pilot thành identity / discovery / hypothesis / evidence; đã tự đối chiếu ba errata với raw file; và mọi dữ liệu đã nhìn đều có dòng exposure.

#### Tại sao lesson này cần?
- **Lesson → RQ.** v1.3 sẽ được xây trên tín hiệu discovery. Nếu ranh giới giữa "đã thấy" và "sẽ kiểm" mờ, toàn bộ confirmation mất giá trị.
- **Rủi ro "số trôi".** Summary của pilot đã lệch raw ở hai chỗ (E1, E2). Nếu viết hypothesis từ summary, hypothesis lệch theo.
- **Rủi ro garden of forking paths.** Stage 2 được chọn sau khi thấy Stage 1; chỉ báo M0 được chọn trong 5. Phải ghi lại để mọi bước sau biết con số nào lạc quan.
- **Rủi ro ER3.** POST_PHASE3_CONTEXT, review hậu nghiệm và SUMMARY có thể do AI soạn. Bạn cần tự đối chiếu với raw, không chỉ tin bản tóm tắt.

#### Lý thuyết cần hiểu

**Khái niệm 1 — Bốn trạng thái của một phát biểu.**
- *Trực giác.* Một tin đồn → một nghi vấn có thể kiểm → một giả thuyết viết ra giấy → một điều đã kiểm.
- *Ví dụ nhỏ.*
  - "$\bar G_{S\mid M_1}\ge0$ ở mọi regime" → **identity**: không thể sai, vì ô S1M1 là oracle.
  - "80/216 regime có $\bar G_S\le-1\%$" → **discovery**: đã thấy, trên mẫu chọn thích nghi.
  - "Trong vùng Ω_SH+ định nghĩa bằng luật, đa số regime mới có $\bar G_S\le-\varepsilon_R$" → **hypothesis**.
  - Câu trên đứng được trên regime CF chưa từng thấy → **evidence** (trong mô hình đã khai báo).
- *Định nghĩa chính xác.* Identity đúng theo định nghĩa hoặc đại số. Discovery là pattern quan sát trên chính dữ liệu dùng để tìm ra nó. Hypothesis có miền, đại lượng, hướng, quan sát bác bỏ, và được viết trước dữ liệu kiểm. Evidence là kết quả của một phép kiểm đã đăng ký trên dữ liệu chưa dùng.
- *Liên hệ nghiên cứu.* L3R.6 sẽ đưa mỗi tín hiệu đi đúng qua bốn trạng thái này.

**Khái niệm 2 — Tần suất trong mẫu thích nghi không phải prevalence.**
- *Trực giác.* Bạn câu được cá ở một chỗ, rồi quay lại thả câu dày đặc quanh đúng chỗ đó. Tỉ lệ câu được lần sau cao hơn tỉ lệ cá trong cả hồ.
- *Ví dụ nhỏ (số đếm từ context; tôi tính lại tỉ lệ).*

  | Tập | Regime có $\bar G_S\le-1\%$ | Tỉ lệ |
  |---|---:|---:|
  | Stage 1 (chưa thích nghi) | 6/60 | 10,0% |
  | Stage 2 (chọn sau khi thấy Stage 1) | 73/108 | 67,6% |
  | Stage 1+2 | 79/168 | 47,0% |
  | Cả ba stage | 80/216 | 37,0% |
  | Stage 3 riêng (có switching cost) | 1/48 | 2,1% |

  Con số "chung" thay đổi theo cách bạn gộp, tức là theo **thiết kế lấy mẫu**, không theo bản chất của mạng.
- *Định nghĩa chính xác.* Prevalence cần một phân phối lấy mẫu đại diện cho phân phối regime ngoài đời. Pilot không có điều đó, và Phase 3R cũng không cố có.
- *Liên hệ nghiên cứu.* Mọi claim về sau phải có dạng "trong vùng Ω…, …", không bao giờ có dạng "x% mạng…".

**Khái niệm 3 — Exposure: dữ liệu đã nhìn không bao giờ sạch lại.**
- *Trực giác.* Đề thi đã xem không dùng để thi lại được.
- *Ví dụ nhỏ.* Regime X2065 đã được nhìn. Một regime "gần như X2065" (mỗi tọa độ lệch vài phần trăm) không phải dữ liệu mới theo nghĩa khoa học: nó gần như chắc chắn cho kết quả tương tự, nên không kiểm được gì.
- *Định nghĩa chính xác.* Exposure register ghi: tập dữ liệu nào, ai nhìn, nhìn ở mức nào (tham số / đại lượng thiết kế / outcome), khi nào.
- *Liên hệ nghiên cứu.* L3R.7 dùng register để đảm bảo regime CF không trùng hoặc dính sát discovery.

**Khái niệm 4 — Raw thắng summary.**
- *Trực giác.* Bản tóm tắt là bản chép tay của bản gốc; khi hai bản khác nhau, bản gốc đúng.
- *Ví dụ nhỏ.* Ba errata E1–E3 ở §0.1.
- *Định nghĩa chính xác.* Summary phải sinh bằng script từ raw. Khi phát hiện lệch, ghi errata gồm giá trị cũ, giá trị đúng và cách kiểm; không sửa thầm lặng.
- *Liên hệ nghiên cứu.* L3R.3 tái lập raw từ checkout sạch; L3R.1 đối chiếu summary với raw.

#### Toán cần biết
Chỉ tỉ lệ. Không có công thức mới.

#### Variables / notation

| Ký hiệu | Nghĩa | Đơn vị | Ai biết | Khi nào biết | Vì sao tách riêng |
|---|---|---|---|---|---|
| Stage ∈ {1, 2, 3} | Đợt quét của pilot | — | tác giả | lúc quét | Biết đợt nào chọn thích nghi |
| X#### | ID regime discovery | — | tác giả | lúc quét | Kiểm trùng với CF ở L3R.7 |
| Mức exposure | {tham số, thiết kế, outcome} | — | tác giả | lúc ghi | Phân biệt cái gì đã "lộ" tới đâu |
| Pilot v1 / v2 | Bản pilot gốc / bản chạy lại sau khi sửa bug (nếu có) | — | tác giả | L3R.3 | Không trộn số của hai engine |

#### Ví dụ nhỏ
Route A/B: bạn xem kết quả của 60 cặp đường A/B (Stage 1) và thấy 6 cặp "sửa state làm tệ hơn". Bạn chủ động chọn 108 cặp đường giống 6 cặp đó hơn (Stage 2), và thấy 73 cặp như vậy. Câu đúng là "ở những cặp đường giống loại đó, hiện tượng hay xuất hiện"; câu sai là "37% đường có hiện tượng này".

#### Việc tôi phải tự làm vs AI có thể hỗ trợ

| Tôi phải tự làm | AI có thể hỗ trợ |
|---|---|
| Viết timeline 10 dòng từ trí nhớ; phân loại 12 phát biểu | So với §0.1, chỉ chỗ thiếu |
| Đọc kết quả script đếm lại và quyết định errata | Viết script đếm lại từ raw |
| Quyết định cách xử lý V9, người đọc, các mục tự viết | Liệt kê hệ quả của từng lựa chọn |
| Chấp nhận hoặc sửa luật provenance | Kiểm luật có mâu thuẫn với DL trước không |

#### Hands-on task

**Part A — Tái dựng (1–2 giờ)**

- **Bước 1 — Timeline 10 dòng, không nhìn tài liệu.**
  - *Vì sao:* đo khoảng cách giữa điều repo ghi và điều bạn thật sự nhớ.
  - *Làm:* viết ra giấy: Phase 3 → Gate A → Step 1 (P(a)/P(b)/P(c)) → pilot Stage 1/2/3 → hôm nay.
  - *Kiểm:* so với §0.1; đánh dấu dòng sai/thiếu.
  - *Ý nghĩa:* các dòng sai là chỗ phải đọc lại trước L3R.2.
- **Bước 2 — Phân loại 12 phát biểu vào bốn trạng thái.**
  - *Vì sao:* đây là kỹ năng cốt lõi của cả phase.
  - *Làm:* với mỗi câu, ghi: identity / discovery / hypothesis / evidence / "phát biểu quá rộng".
    1. $\bar G_M\ge0$ ở mọi regime.
    2. X2065 có $\bar G_M\approx$ 13,41% $\bar C_{\text{ref}}$.
    3. 80/216 regime có harm.
    4. $\bar\Gamma\ge0$ ở gần như mọi regime với c_sw = 0.
    5. Chỉ báo M0 có Spearman ≈ 0,75 với $\bar G_M$.
    6. Blind cells không chạm biên rỗng (Step 1 P(a)).
    7. "Margin tương đối nhỏ + méo không đối xứng gây đảo thứ hạng."
    8. Chênh lệch làm mịn ≤ khoảng 0,20 pp.
    9. "Switching cost không đổi bức tranh."
    10. "Fresh telemetry có hại."
    11. $\bar G_S<0\Rightarrow\bar\Gamma>0$.
    12. "Model repair có giá trị khi B ít headroom, traffic đổi nhanh, horizon dài."
  - *Kiểm:* so với đáp án dưới (mở sau khi tự làm).
  - *Ý nghĩa:* bạn biết câu nào có thể đưa vào hypothesis, câu nào không.

<details>
<summary>Đáp án gợi ý Bước 2 (mở sau khi tự làm)</summary>

(1) Identity (vì S0M1 tối ưu Bayes dưới luật thật cho cùng snapshot — L3R.2). (2) Discovery, và là cực trị trong 216. (3) Discovery thích nghi. (4) Discovery, nhưng ở mọi regime có harm thì nó bị identity (11) kéo theo. (5) Discovery, chọn hậu nghiệm trong 5. (6) Kết quả cấu trúc đã kiểm (Step 1 PASS), gần như identity của plant. (7) Candidate hậu nghiệm trên 2 ô; chưa đủ để thành hypothesis chính. (8) Verification điểm trên 9 regime; không bảo đảm cho regime khác. (9) Phát biểu sai (errata E3). (10) Phát biểu quá rộng: S1 gồm mode, plant lý tưởng. (11) Identity. (12) Candidate → sẽ thành Hyp-MV.

</details>

**Part B — Errata và đóng băng**

- **Bước 3 — Tự kiểm ba errata từ raw.**
  - *Vì sao:* errata trong context do người/AI khác kiểm; bạn cần tự thấy.
  - *Làm:* script đọc raw của pilot (qua `git worktree` hoặc `git show` tại `a7435e9`), đếm theo stage.
  - *Kiểm:* ra 6/73/1, 80/216, 79/168; max chênh làm mịn ≈ 0,193 pp; max $\bar G_M$ Stage 3 ≈ 0,65%.
  - *Ý nghĩa:* con số bạn dùng ở L3R.6 khớp raw.
- **Bước 4 — Gắn tag cho branch pilot.**
  - *Vì sao:* provenance — "discovery v13" phải có địa chỉ không đổi.
  - *Làm:* annotated tag `explore-v13-pilot` tại `a7435e9`. Không merge, không xóa branch.
  - *Kiểm:* `git ls-remote --tags` thấy tag.
  - *Ý nghĩa:* mọi tham chiếu về sau trỏ vào một commit cố định.
- **Bước 5 — Discovery record trong main.**
  - *Vì sao:* main cần biết pilot tồn tại mà không chứa code/kết quả chưa review.
  - *Làm:* `notes/phases/PHASE_3R_discovery_record.md` gồm: tóm tắt sinh từ raw; errata; tag; danh sách 216 regime (ID + tham số, **không** kèm outcome trong bảng này) để L3R.7 kiểm trùng; ghi rõ Stage 2 thích nghi và chỉ báo chọn trong 5.
  - *Kiểm:* mọi số trong file có nguồn là script.
  - *Ý nghĩa:* một nơi duy nhất để nói "chúng ta đã thấy gì".
- **Bước 6 — Dòng exposure.**
  - *Làm:* "pilot v13 (`a7435e9`): 216 regime, outcome đã nhìn; Stage 2 thích nghi; chỉ báo M0 chọn trong 5; A04 38 ô + 10 ô R vẫn là discovery; R09/R10 niêm phong."

**Part C — Điều kiện mở**

- **Bước 7 — DL "mở Phase 3R".**
  - *Vì sao:* một quyết định thật, một DL (chống ER1).
  - *Làm:* ghi trạng thái P0-V10, L8, V9, các closeout tự viết (đạt / còn mở / đổi bằng DL); quyết định "không merge branch"; chấp nhận hoặc sửa luật provenance (§0.5).
  - *Kiểm:* DL có đủ bốn mục Decision / Why / Alternatives / Consequence.

#### Nếu có code
**Code này tồn tại để kiểm:** "các con số trong summary có khớp raw không?"
- File: `experiments/R3R_01_recount/recount.py` (đề xuất).
- Input: thư mục raw của pilot tại `a7435e9`.
- Output: bảng đếm theo stage (harm ≤ −1% $\bar C_{\text{ref}}$; max $\bar G_M$; max chênh làm mịn).
- Invariant: 60 + 108 + 48 = 216 ID không trùng nhau; không regime pilot nào trùng tham số regime (λA, λB, κ, η, h) của 38 ô A04 hay 12 ô R.
- Test: một CSV giả 5 dòng với đáp án biết trước.

#### Verification
Số đếm khớp; tag tồn tại; dòng exposure và DL tồn tại; bảng phân loại 12 câu khớp đáp án hoặc khác có lý do ghi lại.

#### Output
Discovery record (có errata), tag `explore-v13-pilot`, dòng exposure, DL "mở Phase 3R".

#### Interpretation
"Tôi biết chính xác mình đã thấy gì, và các con số tôi sẽ dùng để viết hypothesis khớp với raw."

#### What it does NOT prove
Không chứng minh pilot tính đúng (đó là L3R.3). Không biến discovery thành evidence. Không nói gì về realism.

#### Beginner traps
- Sửa summary thầm lặng thay vì ghi errata.
- Merge branch "cho tiện", hoặc xóa branch "cho gọn".
- Coi 80/216 là "37% mạng có hiện tượng này".
- Đọc summary thay vì raw.
- Quên Stage 3 có thiết kế khác (switching cost) khi gộp số.

#### Self-check
1. Vì sao 80/216 không nói gì về tần suất harm trong mạng thật?
2. Trong 12 phát biểu, câu nào là identity?
3. Vì sao không merge branch exploration?
4. Câu "fresh telemetry có hại" sai ở đâu về câu chữ?
5. Nếu raw cho 81/216 thay vì 80/216, bạn ghi gì, ở đâu?

#### Gate của lesson
*Thông tin trạng thái.* **Track học:** không chặn gì. **Track thực thi:** L3R.3 và L3R.4 Part D chỉ bắt đầu sau khi có tag và dòng exposure.

---

## 9. Lesson 3R.2 — Estimand population: từ một snapshot sang phân phối snapshot

#### Mục tiêu
Sau lesson này tôi tự viết được định nghĩa của $\bar L_{sm}$ và sáu contrast population; giải thích vì sao estimand này trơn hơn estimand một-snapshot; và chỉ ra chính xác contrast nào không thể âm, contrast nào có thể âm, hệ quả nào giữa chúng là bắt buộc.

#### Tại sao lesson này cần?
- **Lesson → RQ.** RQ hỏi "*expected* decision regret". Estimand population lấy kỳ vọng theo mọi snapshot mà controller có thể gặp, nên khớp chữ "expected" hơn thiết kế một-snapshot.
- **Lesson → các lesson sau.** Audit (L3R.3) cần công thức chính xác làm đáp án. Hypothesis (L3R.6) cần biết câu nào *có thể* sai.
- **Rủi ro.** SR2 (obviousness): báo một identity như phát hiện. Nói quá ("fresh telemetry") khi S1 thật ra gồm cả mode.

#### Lý thuyết cần hiểu

**Khái niệm 1 — Một snapshot so với phân phối snapshot.**
- *Trực giác.* Chấm một bác sĩ bằng một bệnh nhân, so với chấm bằng tất cả bệnh nhân mà bác sĩ đó sẽ gặp.
- *Ví dụ nhỏ (tính bằng phân số).* Một regime có ba snapshot có thể xảy ra:

  | Snapshot | $p(y)$ | $\mathbb E[\Delta\mid y]$ | $\mathbb E[\widehat\Delta_{M_0}\mid y]$ | $a_{00}$ | $a_{01}$ | $G_M(y)$ |
  |---|---:|---:|---:|---|---|---:|
  | $y_1$ | 0,5 | −1,5 | −0,6 | Switch | Switch | 0 |
  | $y_2$ | 0,3 | −0,8 | +0,3 | Stay | Switch | 0,8 |
  | $y_3$ | 0,2 | +0,9 | +1,2 | Stay | Stay | 0 |

  $\bar G_M=0{,}3\times0{,}8=0{,}24$. Thiết kế một-snapshot (Phase 3) cố định một $y$, nên cho 0 hoặc 0,8 tùy snapshot được chọn: đó là "knife-edge". Population cho 0,24, và con số này thay đổi dần khi regime thay đổi.
- *Định nghĩa chính xác.*
  - **Regime:** một bộ tham số plant cố định (λA, λB, κ, η, h, cùng các hằng số tuổi τ, capacity c, biên độ ON/OFF a).
  - **Observation:** $Y=(y_A,y_B)$ là backlog quan sát tại $t_0-\tau$; $p(y)$ là phân phối dừng của backlog trước quyết định (routing đang ở Stay).
  - **Belief của S0:** $D(x\mid y)$, posterior Bayes của state tại $t_0$ dưới luật thật (như v1.2).
  - Với mỗi $y$: $L_{sm}(y)=\mathbb E_{x\sim D(\cdot\mid y)}\big[J(a_{sm};x)\big]$, trong đó $a_{0m}=a_{0m}(y)$ (một action cho cả snapshot) và $a_{1m}=a_{1m}(x)$ (theo từng state).
  - **Estimand:** $\bar L_{sm}=\mathbb E_{Y\sim p}\big[L_{sm}(Y)\big]$. Sáu contrast giữ đúng công thức của Phase 3, chỉ thêm gạch ngang: $\bar G_S=\bar L_{00}-\bar L_{10}$, $\bar G_M=\bar L_{00}-\bar L_{01}$, $\bar G_{SM}=\bar L_{00}-\bar L_{11}$, $\bar\Gamma=\bar G_{SM}-\bar G_S-\bar G_M$, $\bar G_{S\mid M_1}=\bar L_{01}-\bar L_{11}$, $\bar G_{M\mid S_1}=\bar L_{10}-\bar L_{11}$.
  - Bổ đề T01 vẫn đúng **cho từng $y$**: $G_M(y)=\lvert\mathbb E[\Delta\mid y]\rvert\cdot\mathbf 1[a_{00}(y)\ne a_{01}(y)]$. Population là trung bình của các "bậc thang" này, nên trơn.
- *Chú ý:* "population" **không** có nghĩa controller được xem nhiều snapshot. Mỗi episode controller vẫn chỉ thấy một snapshot. Population là cách *người đánh giá* lấy trung bình.
- *Liên hệ nghiên cứu.* Đây là estimand chính của contract v1.3.

**Khái niệm 2 — Luật kỳ vọng toàn phần: hai ô S1 không phụ thuộc snapshot.**
- *Trực giác.* Nếu controller thấy state thật, ảnh chụp cũ không còn tác dụng. Trung bình theo ảnh chụp, rồi theo state-cho-trước-ảnh, bằng trung bình theo state.
- *Ví dụ nhỏ.* Hai snapshot "thấp" và "cao", mỗi cái xác suất 0,5. $D(x_1\mid\text{thấp})=0{,}8$, $D(x_1\mid\text{cao})=0{,}2$. Khi đó $0{,}5\times0{,}8+0{,}5\times0{,}2=0{,}5=\pi(x_1)$.
- *Định nghĩa chính xác.* Vì quá trình trước quyết định là dừng và routing không đổi trong $[t_0-\tau,t_0]$:
  $$\sum_y p(y)\,D(x\mid y)=\pi(x),$$
  với $\pi$ là phân phối dừng của state tại $t_0$. Do đó $\bar L_{10}=\mathbb E_\pi\big[J(a_{10}(x);x)\big]$ và $\bar L_{11}=\mathbb E_\pi\big[\min_aJ(a;x)\big]$: không phụ thuộc $\tau$, $p(y)$ hay quadrature của $y$.
- *Liên hệ nghiên cứu.* (a) Đây là một bất biến audit rất mạnh (L3R.3). (b) Chỉ hai ô S0 "cảm nhận" được tuổi telemetry. Mọi thay đổi của $\bar G_{M\mid S_1}$ theo κ đến từ động học (T_mode) và phân phối state, không đến từ observation.

**Khái niệm 3 — Contrast nào là identity.**
- *Trực giác.* Ô 11 là oracle (biết state thật và luật thật), nên không ô nào tốt hơn nó. Ô 01 là "người ra quyết định Bayes tốt nhất khi chỉ có snapshot", nên không thua ô 00 có cùng thông tin.
- *Ví dụ nhỏ.* Toy ở Khái niệm 4.
- *Định nghĩa chính xác* (mỗi dòng có một lý do ngắn):
  1. $\bar G_{SM}\ge0$, $\bar G_{S\mid M_1}\ge0$, $\bar G_{M\mid S_1}\ge0$: ô 11 là oracle theo từng $x$.
  2. $\bar G_M\ge0$: với mỗi $y$, $a_{01}(y)$ tối ưu Bayes dưới luật thật cho belief $D(\cdot\mid y)$. **Lưu ý:** identity này dựa vào việc S0 là posterior Bayes *chính xác*. Nếu sau này bạn thử một estimator khác (ví dụ lọc bằng M0), $\bar G_M$ có thể âm.
  3. $\bar\Gamma=\bar G_{S\mid M_1}-\bar G_S=\bar G_{M\mid S_1}-\bar G_M$ (đại số).
  4. **Hệ quả:** nếu $\bar G_S<0$ thì $\bar\Gamma\ge-\bar G_S>0$, và $\bar G_{M\mid S_1}\ge\lvert\bar G_S\rvert+\bar G_M$.
  5. **Chặn bởi stakes** $\bar\sigma=\mathbb E_\pi\lvert\Delta(x)\rvert$: $\bar G_M,\ \bar G_{S\mid M_1},\ \bar G_{M\mid S_1},\ \bar G_{SM}\in[0,\bar\sigma]$; $\lvert\bar G_S\rvert\le\bar\sigma$; $\bar\Gamma\in[-\bar\sigma,2\bar\sigma]$.

  **Chỉ $\bar G_S$ và $\bar\Gamma$ có thể âm.** Tôi đã kiểm các quan hệ 1–5 trên 4.000 plant rời rạc ngẫu nhiên: 0 vi phạm. Đó là kiểm số, không thay chứng minh của bạn.
- *Liên hệ nghiên cứu.* Hyp-SH chỉ có thể nói về $\bar G_S$. "Penalty biến mất dưới M1" là identity 1. "Complementarity" trong vùng harm là hệ quả 4.

**Khái niệm 4 — Vì sao sửa state có thể làm tệ hơn (toy hai state).**
- *Trực giác.* Snapshot cũ làm controller "nhòe mắt": nó lấy trung bình lỗi của M0 qua nhiều state. Nếu M0 sai nhiều ở state này và ít ở state kia, trung bình có thể triệt tiêu và cho quyết định đúng. Khi thấy rõ state, controller hành động *đúng theo* lỗi của M0 ở từng state.
- *Ví dụ nhỏ (tính bằng phân số).* Hai state hiện tại $x_1,x_2$, mỗi state xác suất 1/2. Snapshot cũ không phân biệt được hai state, nên belief của S0 là (1/2, 1/2). $J(\text{Stay})=10$ ở cả hai; $\Delta=+1$ ở cả hai, tức Stay luôn đúng. M0 dự đoán $\widehat\Delta_{M_0}(x_1)=-2$ (tưởng Switch tốt hơn) và $\widehat\Delta_{M_0}(x_2)=+3$.

  | Ô | Quyết định | Cost kỳ vọng |
  |---|---|---:|
  | 00 (snapshot cũ, M0) | $\mathbb E\widehat\Delta_{M_0}=+0{,}5$ → Stay ở mọi state | 10 |
  | 01 (snapshot cũ, M1) | $\mathbb E\Delta=+1$ → Stay | 10 |
  | 10 (state thật, M0) | Switch ở $x_1$, Stay ở $x_2$ | 10,5 |
  | 11 (oracle) | Stay | 10 |

  Kết quả: $\bar G_S=-0{,}5$; $\bar G_M=0$; $\bar G_{SM}=0$; $\bar\Gamma=+0{,}5$; $\bar G_{S\mid M_1}=0$; $\bar G_{M\mid S_1}=0{,}5$. Stakes $\bar\sigma=1$, nên $\bar G_S=-50\%$ stakes.

  Bằng lời Route A/B: ở $x_1$, M0 hiểu sai hậu quả của việc dồn tải sang B; ở $x_2$, M0 hiểu đúng. Ví dụ **không** nói M0 sai vì lý do vật lý nào; nó chỉ cho thấy cấu trúc toán học.
- *Định nghĩa chính xác.* Đây là hiện tượng "thông tin tốt hơn làm hại một chính sách cố định xấp xỉ" (compensating errors). Nó **không mâu thuẫn** với "thông tin miễn phí không làm hại người ra quyết định tối ưu", vì S1M0 không tối ưu. Hiện tượng này đã nằm trong danh sách đã biết của Phase 2 (K-RM1…K-RM3).
- *Liên hệ nghiên cứu.* Hyp-SH chỉ có thể mới ở chỗ: **ở đâu, bao nhiêu** trong routing đổi tải.

**Khái niệm 5 — Chuẩn hóa: % $\bar C_{\text{ref}}$ hay % stakes.**
- *Trực giác.* "Mất 13 đồng" nghe lớn hay nhỏ tùy bạn so với tổng hóa đơn (1.000 đồng) hay với số tiền đang đặt cược vào quyết định (30 đồng).
- *Ví dụ nhỏ.* $\bar C_{\text{ref}}=1000$ packet·s, $\bar\sigma=30$, $\bar G_M=13$ → 1,3% $\bar C_{\text{ref}}$ nhưng 43,3% stakes.
- *Định nghĩa chính xác.* % $\bar C_{\text{ref}}$ trả lời: "phần này chiếm bao nhiêu trong tổng chi phí hàng đợi của hệ?". % stakes trả lời: "repair lấy lại được bao nhiêu phần của những gì quyết định này có thể thay đổi?". Contrast không âm luôn ≤ 100% stakes (identity 5). Ngưỡng ε_R = 1% đã được khóa theo $C_{\text{ref}}$ (v1.2, D23).
- *Liên hệ nghiên cứu.* L3R.5 chọn một primary. Đề xuất: primary % $\bar C_{\text{ref}}$ (kế thừa ε_R đã khóa trước pilot); secondary % stakes. Pilot báo "42% of stakes" cho X2065 — định nghĩa "stakes" trong code pilot cần đọc ở L3R.3.

**Khái niệm 6 — S1 gồm những gì: "state repair" khác "telemetry tươi".**
- *Trực giác.* Telemetry cho bạn backlog. Mode của traffic nền (đang ON hay OFF) không đo trực tiếp được.
- *Ví dụ nhỏ.* Một controller có backlog hiện tại (tuổi 0) nhưng không biết mode vẫn phải đoán mode từ backlog.
- *Định nghĩa chính xác* (theo contract v1.2; L3R.3 kiểm pilot có dùng đúng như vậy không). S1 = $(q_A,m_A,q_B,m_B)$ thật tại $t_0$, tức gồm **quyền oracle về mode**. Pipeline D22 (backlog hiện tại, mode ẩn, M0 cố định) cho phép tách $\bar G_S=\bar F+\bar V$, với $\bar F=\bar L_{00}-\bar L_{\text{cb}0}$ là phần "backlog mới hơn", và $\bar V=\bar L_{\text{cb}0}-\bar L_{10}$ là phần "thấy mode".
- *Liên hệ nghiên cứu.* Câu "telemetry tươi có hại" chỉ được nói nếu $\bar F<0$. Nếu harm nằm ở $\bar V$, câu đúng là "biết mode mà dùng M0 thì có hại". $\bar F/\bar V$ được báo làm diagnostic ở confirmation (L3R.5 quyết).

#### Toán cần biết
*Cần ôn trước:* Bayes rời rạc; luật kỳ vọng toàn phần; regret ≤ $\lvert\Delta\rvert$ theo từng state. Sau đó:
- **Quadrature.** $\int g(y)\,p(y)\,dy\approx\sum_k w_k\,g(y_k)$. Khi phân phối có **atom** (một khối xác suất dồn tại một điểm, ở đây là backlog = 0), atom phải là một nút riêng với trọng số bằng khối đó. Nếu không, một phần xác suất bị bỏ hoặc bị làm nhòe.
- **Chứng minh $\bar G_M\le\bar\sigma$ trong ba dòng:** với mỗi $y$, $L_{00}(y)-L_{01}(y)=\lvert\mathbb E[\Delta\mid y]\rvert\cdot\mathbf 1[\text{lật}]\le\mathbb E\big[\lvert\Delta\rvert\mid y\big]$; lấy trung bình theo $p(y)$ và dùng Khái niệm 2.

#### Variables / notation

| Ký hiệu | Nghĩa | Đơn vị | Ai biết | Khi nào biết | Vì sao tách riêng |
|---|---|---|---|---|---|
| $\tau$ | Tuổi observation (1 s ở pilot) | s | mọi bên | trước | Neo thời gian |
| $Y=(y_A,y_B)$ | Backlog quan sát tại $t_0-\tau$ | traffic unit | S0 | $t_0$ | Observation ≠ state |
| $p(y)$ | Phân phối dừng của backlog trước quyết định | — | evaluator | thiết kế | Trọng số population |
| $x=(q_A,m_A,q_B,m_B)$ | State thật tại $t_0$ | — | S1, oracle, evaluator | $t_0$ | Gồm mode |
| $\pi(x)$ | Phân phối dừng của state | — | evaluator | thiết kế | $\sum_y p(y)D(x\mid y)=\pi(x)$ |
| $D(x\mid y)$ | Belief của S0 (Bayes, luật thật) | — | S0 | $t_0$ | Estimator cố định khi đổi model |
| $L_{sm}(y)$ | Cost kỳ vọng của ô $sm$ cho snapshot $y$ | packet·s | evaluator | sau tính | Tầng một-snapshot |
| $\bar L_{sm}$ | Trung bình theo $p(y)$ | packet·s | evaluator | sau tính | Estimand v1.3 |
| $\bar G_\bullet$, $\bar\Gamma$ | Sáu contrast population | packet·s | evaluator | sau tính | — |
| $\bar C_{\text{ref}}=\bar L_{11}$ | Cost của oracle | packet·s | evaluator | sau tính | Primary normalization (đề xuất) |
| $\bar\sigma$ | Stakes $=\mathbb E_\pi\lvert\Delta\rvert$ | packet·s | evaluator | sau tính | Secondary normalization |
| $\bar F,\bar V$ | Tách D22 | packet·s | evaluator | sau tính | Câu chữ của claim |
| K | Số nút quadrature cho $y$ | — | engine | trước | Chính sách số |
| P(flip) | $P_Y\big(a_{00}(Y)\ne a_{01}(Y)\big)$ — kiểm định nghĩa của pilot | — | evaluator | sau tính | Diagnostic |

#### Ví dụ nhỏ
Ba ví dụ ở trên: toy ba snapshot (Khái niệm 1), toy hai state (Khái niệm 4), ví dụ chuẩn hóa (Khái niệm 5). Hãy tính lại cả ba trên giấy **trước** khi đọc code.

#### Việc tôi phải tự làm vs AI có thể hỗ trợ

| Tôi phải tự làm | AI có thể hỗ trợ |
|---|---|
| Dẫn trên giấy: định nghĩa, posterior → prior, identity 1–5 | Kiểm từng bước đại số |
| Tính tay ba toy | Viết toy thành golden test bằng phân số |
| Viết T07 bằng lời mình (understanding artifact) | Đối chiếu T07 với contract v1.2, chỉ chỗ lệch nghĩa. **Không** viết thay |

#### Hands-on task

**Part A — Giấy bút**
- **Bước 1 — Viết định nghĩa.**
  - *Vì sao:* audit và contract cần đúng công thức này.
  - *Làm:* viết $L_{sm}(y)$, $\bar L_{sm}$, sáu contrast, nói rõ ô nào dùng $a(y)$, ô nào dùng $a(x)$.
  - *Kiểm:* áp vào toy ba snapshot ra $\bar G_M=0{,}24$.
- **Bước 2 — Chứng minh posterior → prior.**
  - *Làm:* hai dòng từ tính dừng và việc routing không đổi trong $[t_0-\tau,t_0]$.
  - *Kiểm:* chỉ ra giả định nào dùng.
  - *Ý nghĩa:* đây là bất biến audit số 1.
- **Bước 3 — Chứng minh identity 1–3.**
- **Bước 4 — Chứng minh hệ quả 4 và chặn 5.**
  - *Ý nghĩa:* bạn sẽ không bao giờ báo "complementarity trong vùng harm" như phát hiện.

**Part B — Toy**
- **Bước 5 — Tính tay ba toy.**
- **Bước 6 — Biến chúng thành golden test** (phân số, không float). L3R.3 dùng các test này.

**Part C — Ghi lại**
- **Bước 7 — Viết `notes/theory/T07_population_estimand.md`** (nhãn: tác giả viết). Gồm: định nghĩa; **sanity list v1.3** (ít nhất 10 dòng, mỗi dòng có lý do); **danh sách "có thể sai"** (ngắn: dấu và độ lớn của $\bar G_S$; dấu của $\bar\Gamma$ ngoài vùng harm; độ lớn của các contrast không âm; $\bar F/\bar V$).

#### Nếu có code
**Code này tồn tại để kiểm:** "công thức trong T07 có cho đúng đáp án trên toy không?" — và để L3R.3 có đáp án exact.
- File: `tests/test_population_toys.py` (đề xuất).
- Input: định nghĩa ba toy.
- Output: assert bằng phân số cho sáu contrast.
- Invariant: identity 1–5.
- Test: chính file này.

#### Verification
Chứng minh đọc lại được; toy khớp tay; read-back với một người: "vì sao trong vùng harm, $\bar\Gamma>0$ là bắt buộc?"

#### Output
T07, sanity list v1.3, golden toy.

#### Interpretation
Bạn biết câu nào có thể sai, câu nào không.

#### What it does NOT prove
Không chứng minh engine pilot implement đúng T07. Không chứng minh harm tồn tại trong plant. Không nói gì về realism.

#### Beginner traps
- Coi $\bar\Gamma>0$ là phát hiện riêng trong vùng harm.
- Gọi S1 là "telemetry tươi".
- Trộn % $\bar C_{\text{ref}}$ và % stakes trong cùng một câu.
- Quên atom tại backlog = 0.
- Nghĩ "population" nghĩa là controller được xem nhiều snapshot.

#### Self-check
1. Vì sao $\bar L_{10}$ và $\bar L_{11}$ không phụ thuộc $\tau$?
2. Chứng minh trong một dòng: $\bar G_S<0\Rightarrow\bar\Gamma>0$.
3. Trong toy hai state, vì sao ô 00 đúng mà ô 10 sai?
4. Identity $\bar G_M\ge0$ dựa vào giả định nào về S0?
5. Một regime có $\bar G_M=13\%\,\bar C_{\text{ref}}$ và $\bar\sigma=30\%\,\bar C_{\text{ref}}$: model repair lấy lại bao nhiêu phần stakes?

#### Gate của lesson
*Thông tin trạng thái.* **Track học:** không chặn gì. **Track thực thi:** T07 là đáp án của audit (L3R.3 Part B) và là nền của contract (L3R.5).

---

## 10. Lesson 3R.3 — Audit engine: pilot có được tính đúng không?

#### Mục tiêu
Sau lesson này tôi có **bằng chứng verification**, không phải niềm tin, rằng engine population tính đúng estimand T07: trên toy, trên regime discovery, và khớp một phương pháp độc lập. Hoặc tôi tìm ra bug, biết bug đó đổi con số pilot thế nào, và đã chạy lại discovery đúng cách.

#### Tại sao lesson này cần?
- **Đây là câu bạn hỏi:** "không biết chạy có đúng hay sai sót không".
- **Lesson → RQ.** Estimand v1.3 chỉ có nghĩa nếu được tính đúng. Confirmation dùng *cùng engine*, nên một bug sẽ được "xác nhận" chứ không bị phát hiện.
- **Rủi ro.** ER5 (bug ở oracle hoặc sổ sách); bug chung giữa code và checker (Phase 3 đã gặp ở L1.5: checker dùng chung helper nên bỏ sót lỗi); artefact rời rạc hóa; code migrate từ branch chưa review.

**Pilot đã kiểm gì, còn thiếu gì**

| Kiểm | Pilot đã có? | Bắt được loại lỗi nào | Còn thiếu |
|---|---|---|---|
| So với engine Phase 3 ở 8 cặp snapshot | Có | Sai ở tầng một-snapshot | Không kiểm tầng trung bình theo $p(y)$ |
| 19 brute-force ledger test | Có | Sổ sách bảng 2×2 | Chưa rõ có phủ toy harm, atom tại 0 không |
| "GM identity gap" ≈ 0 | Có | Bổ đề T01 theo từng $y$ | — |
| Làm mịn K và dt | 9 regime chọn tay | Sai số rời rạc ở 9 regime đó | Regime CF có thể nằm ở vùng số khó hơn |
| Monte Carlo độc lập viết từ định nghĩa | Chưa | Lỗi $p(y)$, belief, phép trung bình | — |
| Posterior → prior | Chưa | Belief sai (ví dụ mode tại $t_0-\tau$ coi như độc lập với $y$) | — |
| Mutation test cho tầng population | Chưa rõ | Test "lúc nào cũng xanh" | — |
| Tái lập từ checkout sạch | Chưa rõ | Phụ thuộc môi trường, file tạm | — |
| Tác giả đọc và giải thích được code | Chưa rõ | Hiểu sai định nghĩa (D10, D22…) | — |

#### Lý thuyết cần hiểu

**Khái niệm 1 — Verification khác validation (nhắc lại MASTER PLAN III.2).**
- *Trực giác.* Verification: "tôi có làm đúng bài toán tôi viết ra không?". Validation: "bài toán tôi viết ra có giống thế giới thật không?".
- *Ví dụ nhỏ.* Monte Carlo khớp engine → code đúng **mô hình**. Điều đó không nói gì về việc mạng thật có hành xử như mô hình không.
- *Định nghĩa.* Lesson này chỉ làm verification. Validation là việc của Phase 6.
- *Liên hệ.* Kết luận của lesson này luôn có đuôi "…trong mô hình đã khai báo".

**Khái niệm 2 — Phép kiểm độc lập và "bug nhất quán".**
- *Trực giác.* Tự chấm bài mình bằng đáp án chép từ chính bài mình thì luôn được 10 điểm.
- *Ví dụ nhỏ.* Nếu Monte Carlo gọi lại hàm `belief()` của engine để sinh state, mọi lỗi trong `belief()` xuất hiện ở cả hai bên và triệt tiêu khi so.
- *Định nghĩa chính xác.* Ba mức độc lập: (i) thuật toán khác, chung code; (ii) code khác, chung *đặc tả*; (iii) người khác, chung đặc tả. Mục tiêu tối thiểu: (ii). Monte Carlo được viết từ T07 và contract, **không mở code engine**.
- *Liên hệ.* Part C.

**Khái niệm 3 — Monte Carlo với CRN và dung sai viết trước.**
- *Trực giác.* Ước lượng bằng rút thăm: càng nhiều thăm thì sai số càng nhỏ. Dùng cùng một bộ thăm cho cả bốn pipeline để so cho công bằng (common random numbers, CRN).
- *Ví dụ nhỏ (MASTER PLAN IX.5).* Hai cost có độ lệch chuẩn 5, tương quan 0,9: độ lệch chuẩn của hiệu ≈ 2,24, thay vì ≈ 7,07 nếu độc lập.
- *Định nghĩa chính xác.* $\widehat{\bar L}_{sm}=\frac1N\sum_{n=1}^NC\big(a_{sm},w_n\big)$, với $(y_n,x_n,w_n)$ rút từ plant; SE = $s/\sqrt N$. Hai số "khớp" nếu $\lvert z\rvert=\lvert\text{engine}-\text{MC}\rvert/\text{SE}\le3$.
  - Khi so nhiều lần, thỉnh thoảng sẽ có $\lvert z\rvert>3$ chỉ do may rủi: mỗi phép so có xác suất khoảng 0,27%; với 40 phép so, xác suất có ít nhất một báo động giả khoảng 10%.
  - **Luật viết trước:** $\lvert z\rvert>3$ → chạy lại với N gấp 4 và seed mới; vẫn $>3$ → điều tra như bug.
- *Liên hệ.* Part C.

**Khái niệm 4 — Posterior → prior như một "định luật bảo toàn" của estimator.**
- *Trực giác.* Trung bình của mọi niềm tin *sau* quan sát phải bằng niềm tin *trước* quan sát. Nếu không, estimator đang "tạo ra" hoặc "làm mất" xác suất.
- *Ví dụ nhỏ.* Một lỗi điển hình: engine coi mode tại $t_0-\tau$ là độc lập với backlog quan sát (dùng xác suất 1/2 cho mỗi mode bất kể $y$). Thật ra backlog B lớn gợi ý B vừa ở mode ON. Với lỗi này, trung bình của các belief theo $p(y)$ lệch khỏi $\pi$ → bị bắt.
- *Định nghĩa chính xác.* Kiểm $\max_x\big\lvert\sum_yp(y)D(x\mid y)-\pi(x)\big\rvert\le$ dung sai quadrature (viết trước).
- *Liên hệ.* Part B, Bước 3.

**Khái niệm 5 — Mutation test.**
- *Trực giác.* Cố tình cài lỗi để xem bộ test có kêu không. Một bộ test không bắt được lỗi nào thì chưa kiểm gì.
- *Định nghĩa.* Mỗi mutant trong danh sách (Part B, Bước 4) phải làm ít nhất một test FAIL.
- *Liên hệ.* Phase 3 đã dùng cách này; ở đây áp cho tầng population.

**Khái niệm 6 — Chính sách số cho từng regime.**
- *Trực giác.* Thước có vạch. Mỗi lần đo, xem hai mức vạch có đồng ý với nhau không.
- *Định nghĩa chính xác.* Chọn (K*, dt*). Với **mỗi** regime, tính thêm một mức thô hơn (ví dụ K*/2 với cùng dt*, và 2·dt* với cùng K*). Yêu cầu mọi contrast chênh ≤ 0,25 pp $\bar C_{\text{ref}}$ (= ε_E/2, kế thừa D1 và D24). Không đạt → leo thang một bậc (2K*, dt*/2). Vẫn không đạt → "chưa phân giải số": không được đếm là PASS hay FALSIFY.
- *Liên hệ.* Đi vào contract v1.3 (L3R.5) và Phase 4.

**Khái niệm 7 — Atom tại backlog = 0 (cụ thể cho plant này).**
- *Trực giác.* Hàng đợi hay rỗng. "Rỗng" là một khối xác suất riêng, không phải một điểm trên đường cong mật độ.
- *Ví dụ nhỏ (mô hình fluid liên tục; tôi tính và kiểm bằng mô phỏng).* Nền B ON/OFF với tốc độ 14 và 2 (trung bình λB = 8, biên độ a = 6), capacity c = 10. Xác suất hàng đợi không rỗng là $P(Q>0)=\frac{a}{c-\lambda+a}=\frac68=0{,}75$, nên **khối tại 0 là 0,25**. Nếu quadrature chỉ đặt nút trên phần mật độ liên tục, 25% xác suất bị bỏ hoặc bị làm nhòe.
- *Định nghĩa chính xác.* Kiểm $p(y_B=0)$ của engine so với công thức. Plant slotted sẽ lệch nhẹ: đặt dung sai trước (ví dụ 0,01) và kiểm rằng độ lệch giảm khi dt giảm. Với A, dùng λ = λA + u (managed traffic đang ở A trước quyết định).
- *Liên hệ.* Part B, Bước 3.

#### Toán cần biết
*Cần ôn trước:* SE = s/√N; xác suất báo động giả khi so nhiều lần: $1-(1-p)^m$; quadrature với atom. Cỡ mẫu Monte Carlo: muốn SE ≤ e khi độ lệch chuẩn của contrast theo episode là s thì $N\approx(s/e)^2$. Ví dụ minh họa: s = 20% $\bar C_{\text{ref}}$, e = 0,1% $\bar C_{\text{ref}}$ → N ≈ 40.000 episode. Ước lượng s bằng một lần chạy thử nhỏ.

#### Variables / notation

| Ký hiệu | Nghĩa | Đơn vị | Ai biết | Khi nào biết | Vì sao tách riêng |
|---|---|---|---|---|---|
| N | Số episode Monte Carlo mỗi regime | — | tác giả | trước khi chạy MC | Quyết định SE |
| s, SE | Độ lệch chuẩn theo episode; sai số chuẩn | packet·s | MC | sau chạy thử | Dung sai |
| z | (engine − MC)/SE | — | MC | sau chạy | Luật khớp |
| (K*, dt*) | Mức số cuối | —, s | contract v1.3 | sau audit | Chính sách số |
| tol_num | 0,25 pp $\bar C_{\text{ref}}$ | pp | contract | trước | Kế thừa D1/D24 |
| tol_quad | Dung sai posterior → prior | xác suất | tác giả | trước khi kiểm | Bất biến estimator |
| t_reg | Thời gian chạy một regime | s | engine | Part D | Ngân sách confirmation |

#### Ví dụ nhỏ
Route A/B (số giả định): engine nói "chuyển sang B trung bình tốn thêm 2 packet·s so với ở lại A" cho một regime. Monte Carlo chạy 40.000 lần cùng regime, mỗi lần rút một snapshot, state thật và một tương lai; dùng *cùng* tương lai cho cả bốn pipeline; tính cost thật. Nếu MC cho 2,03 ± 0,02, hai bên khớp. Nếu MC cho 2,40 ± 0,02, có gì đó sai: ở engine, ở MC, hoặc ở đặc tả mà một bên hiểu khác.

#### Việc tôi phải tự làm vs AI có thể hỗ trợ

| Tôi phải tự làm | AI có thể hỗ trợ |
|---|---|
| Đọc từng hàm engine và ánh xạ vào T07; trả lời 11 câu hỏi (a)–(k) | Vẽ sơ đồ gọi hàm; chỉ nơi dùng D10, D22 |
| Viết trước kết quả mong đợi của mỗi test và dung sai MC | Viết test, mutant, và Monte Carlo **từ đặc tả** (chỉ đưa AI T07 + contract, **không** đưa code engine) |
| Quyết định khi lệch: bug hay dung sai | Đề xuất giả thuyết debug |
| Quyết định KEEP hay REBUILD engine | Soạn PR, provenance, checklist review |

#### Hands-on task

**Part A — Đọc và ánh xạ (1–2 ngày)**

- **Bước 1 — Bảng ánh xạ T07 → code.**
  - *Vì sao:* nếu không chỉ ra được dòng code nào tính công thức nào, bạn không biết engine tính gì.
  - *Làm:* mỗi công thức trong T07 một dòng: file, hàm, dòng. Rồi trả lời từ code 11 câu:
    - (a) $p(y)$ lấy từ đâu; atom tại 0 được xử lý thế nào?
    - (b) Belief $D(x\mid y)$ có dùng *joint* (backlog, mode) tại $t_0-\tau$ không; có đẩy chuỗi mode qua $\tau$ không?
    - (c) S0 lọc bằng luật thật (như v1.2) không?
    - (d) M0 lấy trung bình cost theo belief (D10) hay rollout từ mean-state?
    - (e) S1 có gồm mode không?
    - (f) Luật hòa là gì?
    - (g) $\bar C_{\text{ref}}$ có tính ở cùng (K, dt) với contrast không?
    - (h) "Stakes" định nghĩa thế nào?
    - (i) "P(flip)" định nghĩa thế nào?
    - (j) Chỉ báo M0-only tính bằng công thức chính xác nào? (sẽ khóa ở L3R.6)
    - (k) Ở Stage 3, $c_{\text{sw}}$ có đơn vị gì và được cộng vào đâu?
  - *Kiểm:* mỗi câu có trích dẫn file:dòng.
  - *Ý nghĩa:* mỗi câu trả lời "khác T07" là một bug **hoặc** một định nghĩa phải quyết ở v1.3.
- **Bước 2 — Danh sách lệch.** Ghi mọi chỗ code khác T07 hoặc contract v1.2, phân loại: bug / lựa chọn định nghĩa / chưa rõ.

**Part B — Test (viết đáp án trước khi chạy)**

- **Bước 3 — Test đúng/sai có đáp án biết trước.**
  - Golden toy (L3R.2) bằng phân số.
  - Identity 1–5 trên plant nhỏ ngẫu nhiên.
  - Posterior → prior trên toy và trên 6–10 regime discovery.
  - Atom tại 0 so với công thức (Khái niệm 7).
  - 8 cặp snapshot với engine Phase 3 (giữ).
  - **Zero-action** ($u=0$): mọi contrast bằng 0 **chính xác**.
  - **Regime không chạm biên rỗng** (conservation): $\Delta\equiv0$ → mọi contrast bằng 0 chính xác.
- **Bước 4 — Mutation.** Mỗi mutant phải làm ít nhất một test FAIL:
  1. Đổi nhãn S0/S1 trong pipeline M0.
  2. S0 nhận state thật.
  3. M0 rollout từ mean-state thay vì trung bình cost theo belief.
  4. Mode tại $t_0-\tau$ coi như độc lập với $y$.
  5. Không đẩy belief qua $\tau$ (coi $y$ là state hiện tại).
  6. Bỏ atom tại 0 trong $p(y)$.
  7. Luật hòa đổi thành Switch.
  8. $\bar C_{\text{ref}}$ tính ở mức dt khác.
  9. Pipeline D22 thấy mode.
  10. Trọng số $p(y)$ không chuẩn hóa (tổng ≠ 1).
- **Bước 5 — Tái lập từ checkout sạch.**
  - *Vì sao:* kết quả không được phụ thuộc file tạm hay môi trường máy bạn.
  - *Làm:* clone mới, môi trường mới; chạy lại 9 regime robustness và X2065.
  - *Kiểm:* số trùng raw (sai khác bằng 0 trong làm tròn, hoặc giải thích được từng chỗ).

**Part C — Monte Carlo độc lập (từ đặc tả)**

- **Bước 6 — Viết MC từ T07 + contract, không mở code engine.**
  - *Thiết kế:* mô phỏng plant tới trạng thái dừng (burn-in dài); ghi $y$ tại $t_0-\tau$ và $x$ tại $t_0$; hỏi engine (như một hộp đen) bốn quyết định $a_{00}(y), a_{01}(y), a_{10}(x), a_{11}(x)$; mô phỏng **một** tương lai $w$ chung cho cả bốn quyết định (CRN); tính cost thực hiện.
  - *Phép kiểm này kiểm gì:* phân phối $p(y)$, belief dùng trong phép đánh giá, việc tích phân cost kỳ vọng, phép trung bình, và chuẩn hóa. Nó **không** kiểm bản thân việc $a_{00}(y)$ có đúng là quyết định "S0 + M0 theo D10" — phần đó do Part A, toy và mutant kiểm.
- **Bước 7 — Chọn regime kiểm:** 3 toy + 6–10 regime discovery (X2065; một regime harm mạnh; một regime gần 0; một regime Stage 3; một regime κ lớn…). **Chỉ discovery.**
- **Bước 8 — Viết dung sai trước:** $\lvert z\rvert\le3$, luật chạy lại; chọn N cho SE ≤ 0,1 pp $\bar C_{\text{ref}}$ trên contrast.
- **Bước 9 — Kiểm ở mức $J$:** chọn 5–10 state $x$, so $J(a;x)$ của engine với MC thuần (không dùng engine). Bước này kiểm phần "luật thật" (M1).
- **Bước 10 — Ghi seed vào seed registry.**

**Part D — Chính sách số và ngân sách**

- **Bước 11 — Đề xuất (K*, dt*), cặp kiểm từng regime, luật leo thang.** Đo thời gian chạy một regime ở (K*, dt*) và ở mức kiểm → con số t_reg cho L3R.7.

**Part E — Migration**

- **Bước 12 — KEEP hay REBUILD.**
  - KEEP: đưa code engine vào main qua review + provenance (branch, commit, file gốc) + test.
  - REBUILD: viết lại sạch theo T07, dùng engine pilot làm đối chiếu.
  - Tiêu chí: Part A tìm thấy bao nhiêu chỗ lệch định nghĩa; bạn giải thích được từng hàm không (điều kiện X.3 #2).
- **Bước 13 — DL "engine population v1: đã kiểm …; chưa kiểm …"** và báo cáo audit.

> **Nếu tìm ra bug — quy trình bắt buộc**
> 1. Không sửa rồi chỉ chạy lại các regime "đẹp". Chạy lại **toàn bộ** 216 regime bằng engine đã sửa ("pilot v2"). Đó vẫn là discovery.
> 2. Ghi exposure: pilot v2 đã nhìn.
> 3. Viết lại discovery record: tín hiệu nào còn, tín hiệu nào mất, số đổi bao nhiêu.
> 4. L3R.6 viết hypothesis từ pilot v2.
> 5. Nếu tín hiệu chính biến mất → Gate 3R có thể là PIVOT (§18). Đó là một kết quả, không phải thất bại của bạn.

#### Nếu có code
**Code này tồn tại để kiểm:** "Engine có tính đúng estimand T07 không?" (Q3R.1)

| File (đề xuất) | Hàm | Input | Output | Invariant (vi phạm thì raise) |
|---|---|---|---|---|
| `src/smr/population.py` (migrate hoặc rebuild) | `observation_law(regime, K)` | regime, K | Nút $y$ và trọng số (có atom) | Tổng trọng số = 1; atom khớp kiểm tra |
| | `belief(regime, y)` | regime, $y$ | $D(x\mid y)$ | $\sum_yp(y)D(x\mid y)=\pi(x)$ trong tol_quad |
| | `decisions(regime, y, x)` | | $a_{00},a_{01},a_{10},a_{11}$ | $a_{11}=\arg\min_aJ$; $a_{01}$ tối ưu Bayes |
| | `evaluate_regime(regime, K, dt)` | | $\bar L_{sm}$; sáu contrast; $\bar C_{\text{ref}}$; $\bar\sigma$; P(flip); khối hòa; $\bar F,\bar V$; $e_{\text{num}}$ | Identity 1–5 |
| `experiments/R3R_03_mc/mc_population.py` | `sample_episode`, `estimate` | regime, hàm quyết định (hộp đen), N, seed | $\widehat{\bar L}_{sm}$ + SE | Zero-action → contrast 0; CRN dùng chung $w$ |

**Tests:** golden toy; identity trên plant ngẫu nhiên; posterior → prior; atom; zero-action; conservation; 8 cặp snapshot; 10 mutant; tái lập checkout sạch; MC khớp.

#### Verification
Mọi test xanh; mọi mutant bị bắt; MC khớp ($\lvert z\rvert\le3$ sau luật chạy lại) ở mọi regime kiểm; tái lập từ checkout sạch khớp raw; bạn giải thích được từng hàm (read-back).

#### Output
Báo cáo audit; engine trong main (hoặc kế hoạch rebuild); Monte Carlo + test; (K*, dt*) đề xuất; t_reg; DL.

#### Interpretation
"Trong phạm vi các kiểm này, engine tính đúng mô hình; tín hiệu pilot (nếu tái lập được) không phải lỗi code."

#### What it does NOT prove
- Không chứng minh tín hiệu là của mạng thật, hay plant đúng.
- Không chứng minh regime CF sẽ không có vấn đề số — vì thế mới có kiểm từng regime.
- MC khớp không chứng minh **định nghĩa** đúng ý RQ; đó là việc của contract.

#### Beginner traps
- Viết MC bằng cách đọc code engine (bug nhất quán).
- Chọn dung sai sau khi thấy z.
- Chạy MC trên regime CF "cho chắc" — đó là exposure.
- Sửa bug rồi chạy lại chọn lọc.
- Chấp nhận "gần 0" ở zero-action: ở đó phải bằng 0 chính xác.
- Coi "19 test xanh" là đủ.

#### Self-check
1. Vì sao MC phải được viết mà không đọc code engine?
2. Mutant "mode tại $t_0-\tau$ độc lập với $y$" bị kiểm nào bắt, vì sao?
3. Với 40 phép so ở ngưỡng 3 SE, vì sao một $\lvert z\rvert=3{,}2$ chưa đủ để kết luận bug?
4. Vì sao làm mịn trên 9 regime chọn tay chưa đủ cho confirmation?
5. Nếu sửa một bug làm harm giảm một nửa, bạn làm gì với 216 regime?

#### Gate của lesson
*Thông tin trạng thái.* **Track học:** không chặn gì. **Track thực thi:** phần numerics của contract v1.3 (L3R.5) chỉ khóa khi audit PASS. Nếu FAIL → HOLD tới khi sửa xong và chạy lại discovery.

---

## 11. Lesson 3R.4 — Realism screen: các con số có khả thi ngoài đời không?

#### Mục tiêu
Sau lesson này tôi biểu diễn được mỗi regime bằng vài tỉ số không thứ nguyên; suy ra từ chúng các đại lượng quan sát được ngoài đời (mức dùng link, độ biến động theo cửa sổ thời gian, delay hàng đợi, tần suất đổi mode, thời gian vật lý); có một **realism envelope v1** với nguồn cho từng dải; và biết vùng discovery nằm IN / EDGE / OUT ở bối cảnh nào — tất cả ở mức thiết kế, không chạm outcome.

#### Tại sao lesson này cần?
- **Đây là câu bạn hỏi:** con số phải phù hợp thực tế, không phải số không khả thi ngoài đời.
- **Lesson → RQ3** (practical relevance) và các rủi ro SR5 (toy realism), SR6 (timescale).
- **Vì sao bây giờ.** MASTER PLAN đặt realism ở Phase 8. Nhưng một sàng lọc thô, có nguồn, chỉ dùng tham số thiết kế thì rất rẻ, và có thể NARROW sớm trước khi đầu tư vào confirmation và mechanism.
- **Rủi ro riêng của lesson này: "motivated realism"** — định nghĩa "thực tế" sao cho vùng tín hiệu của mình trông thực tế.

#### Lý thuyết cần hiểu

**Khái niệm 1 — Đơn vị và tỉ số: "capacity = 10" không phải vấn đề realism.**
- *Trực giác.* Bản đồ tỉ lệ 1:1.000 hay 1:1.000.000 vẽ cùng một con đường. Cái quan trọng là hình dạng, không phải con số trên thước.
- *Ví dụ nhỏ (tôi kiểm bằng mô phỏng plant fluid slotted).* Nhân mọi tốc độ và backlog với 1000 → cost nhân đúng 1000. Co mọi thời gian (τ, T_mode, h, dt) còn 1/100 → backlog co còn 1/100, cost co còn 1/10.000. Sau khi chia cho $\bar C_{\text{ref}}$, contrast **không đổi**.
- *Định nghĩa chính xác.* Với điều kiện plant là fluid (trong mỗi mode, tốc độ đến cố định — kiểm lại trong contract v1.2), kết quả chuẩn hóa chỉ phụ thuộc các tỉ số:
  - $\rho_A=(\lambda_A+u)/c$ (A trước quyết định), $\rho_B=\lambda_B/c$, $\rho_B'=(\lambda_B+u)/c$ (B sau Switch);
  - $a/c$ (biên độ ON/OFF so với capacity);
  - $\eta=u/(c-\lambda_B)$;
  - $\kappa=T_{\text{mode}}/\tau$ và $h/\tau$.

  Một mốc thời gian (ví dụ τ = 1 s) chỉ dùng để **dịch** sang thời gian vật lý khi so với thế giới thật.
- *Hệ quả quan trọng.* "τ = 1 s, T_mode = 0,1 s, h = 8 s" và "τ = 10 ms, T_mode = 1 ms, h = 80 ms" là **cùng một regime** về toán. Câu hỏi realism đúng là: **có bối cảnh mạng thật nào có đồng thời các tỉ số này không?**
- *Cảnh báo.* Nếu plant có nhiễu Poisson bên trong mỗi mode (đếm packet rời rạc), bất biến theo đơn vị traffic không còn đúng. Kiểm định nghĩa plant.
- *Liên hệ.* Part A.

**Khái niệm 2 — Đại lượng quan sát được suy ra (implied observables).**
- *Trực giác.* Không ai đo "κ" ngoài đời. Người ta đo mức dùng link, độ biến động của traffic theo cửa sổ 10 ms / 100 ms / 1 s, delay hàng đợi, tuổi telemetry. Phải dịch mô hình sang những thứ đó thì mới so được.
- *Ví dụ nhỏ (tôi tính bằng công thức và đối chiếu mô phỏng; mô hình fluid liên tục; nền B trước quyết định với λB = 8, a = 6, c = 10; mốc τ = 1 s).* Nói bằng lời: **B dùng trung bình 80% capacity, nhưng cứ mỗi T_mode giây lại nhảy giữa 140% và 20% capacity.**

  | Đại lượng | κ = 0,1 (T_mode = 0,1 s) | κ = 0,3 (T_mode = 0,3 s) |
  |---|---:|---:|
  | Mức dùng trung bình của B | 80% | 80% |
  | Độ biến động (CV) của tốc độ nền B theo cửa sổ 10 ms | 0,73 | 0,74 |
  | … theo cửa sổ 100 ms | 0,56 | 0,67 |
  | … theo cửa sổ 1 s | 0,23 | 0,38 |
  | P(hàng đợi B không rỗng) | 0,75 | 0,75 |
  | Delay hàng đợi trung bình ở B | 60 ms | 180 ms |
  | P(delay > 100 ms) | 0,21 | 0,49 |
  | P(delay > 250 ms) | 0,033 | 0,26 |
  | P(delay > 500 ms) | 0,0014 | 0,093 |
  | Số lần đổi mode trong h = 8 s | ≈ 80 | ≈ 27 |

  Với mốc τ = 10 ms, mọi thời gian chia cho 100: delay trung bình 0,6 ms và 1,8 ms; T_mode 1 ms và 3 ms; h = 80 ms.
- *Định nghĩa chính xác (công thức sàng lọc; không cần dẫn, chỉ cần hiểu từng phần).*
  - **Độ biến động theo cửa sổ $w$:** $\text{CV}_w=\dfrac{a}{\lambda}\sqrt{f(2w/T)}$, với $f(z)=\dfrac{2(z-1+e^{-z})}{z^2}$. Cửa sổ rất ngắn so với T → $f\to1$: thấy nguyên biên độ. Cửa sổ rất dài → $f\approx T/w$: luật số lớn làm mượt.
  - **Hàng đợi fluid hai trạng thái đối xứng** (khi $\lambda<c$ và $\lambda-a<c<\lambda+a$): $P(Q>0)=\dfrac{a}{c-\lambda+a}$; $P(Q>x)=P(Q>0)\,e^{-\theta x}$ với $\theta=\dfrac{2(c-\lambda)}{T\,\big(a^2-(c-\lambda)^2\big)}$. Đọc: mỗi khi backlog tăng thêm $1/\theta$, xác suất giảm e lần.
  - **Delay trung bình** $=\dfrac{a\,T\,\big(a-(c-\lambda)\big)}{2c\,(c-\lambda)}$, tức $\dfrac{\text{delay}}{\tau}=\kappa\cdot\dfrac{a\big(a-(c-\lambda)\big)}{2c\,(c-\lambda)}$. Với a = 6, c − λ = 2: delay/τ = 0,6·κ.

  Đây là **xấp xỉ liên tục để sàng lọc**. Giá trị chính xác lấy từ phân phối dừng của engine (đại lượng thiết kế, không phải outcome).
- *Liên hệ.* Part A tính các đại lượng này cho cả 216 regime.

**Khái niệm 3 — Bối cảnh (context) và envelope.**
- *Trực giác.* Cùng một tổ hợp tỉ số có thể hợp lý ở một loại mạng mà vô lý ở loại khác. Ví dụ, một link backbone mang hàng nghìn flow có lẽ mượt hơn ở thang 100 ms so với một link biên hay ToR chỉ có vài flow lớn — đây là **trực giác luật số lớn, cần nguồn để xác nhận**.
- *Ví dụ nhỏ.* Với mốc τ = 10 ms, delay trung bình 0,6–1,8 ms nghe giống switch datacenter. Nhưng khi đó T_mode chỉ 1–3 ms, và action phải có hiệu lực nhanh hơn thế — câu hỏi realism chuyển sang độ trễ cài rule.
- *Định nghĩa chính xác.* Envelope = với mỗi bối cảnh (ví dụ: datacenter fabric; enterprise/campus; WAN/ISP; edge hoặc 5G transport), một dải cho mỗi đại lượng: tuổi telemetry τ; thang thời gian của biến động traffic; mức dùng link; độ biến động theo cửa sổ; buffer tính theo thời gian; độ trễ actuation; thời gian giữ quyết định h. Mỗi dải có nguồn, mục, mức đọc và độ tin cậy. **Luật phân loại viết trước**, ví dụ: IN = mọi đại lượng nằm trong dải của ít nhất một bối cảnh; EDGE = lệch tối đa một hệ số 2 ở không quá 2 đại lượng (bạn chọn); OUT = còn lại.
- *Liên hệ.* Part B–D.

**Khái niệm 4 — Ba giả định của plant mà realism soi trực tiếp.**
- **Buffer vô hạn.** Nếu xác suất delay vượt kích thước buffer (tính theo thời gian) của bối cảnh không nhỏ, plant đang bỏ qua drop — và giả định có thể sai **đúng ở vùng tín hiệu**. Ví dụ ở bảng trên: với κ = 0,3 và mốc 1 s, khoảng 9% thời gian B có delay > 0,5 s.
- **Action có hiệu lực ngay.** So độ trễ actuation với T_mode.
- **S1 biết mode.** Không telemetry nào đo "mode" → quyền oracle.
- *Liên hệ.* Ba cờ này đi vào assumptions của contract (L3R.5) và quyết định phép validation nào làm trước ở Phase 6.

**Khái niệm 5 — Motivated realism và cách chống.**
- *Trực giác.* Thợ may đo một người mẫu rồi tuyên bố "cỡ áo này vừa với mọi người".
- *Ví dụ nhỏ.* Sau khi biết vùng tín hiệu cần T_mode ≈ 0,1–0,3τ, bạn chọn đúng bối cảnh "khớp" và lặng lẽ bỏ qua các bối cảnh còn lại.
- *Định nghĩa (luật).* Dải lấy từ nguồn **trước** khi phân loại; luật phân loại commit trước; báo kết quả cho **mọi** bối cảnh đã chọn; ghi rõ nếu vùng tín hiệu OUT ở đa số bối cảnh; người đọc độc lập soi riêng phần này.
- *Liên hệ.* L3R.8.

#### Toán cần biết
Tỉ số và đổi đơn vị; hàm mũ; đọc một công thức qua hai trường hợp cực đoan (cửa sổ rất ngắn / rất dài; T → 0 thì delay → 0 vì traffic đổi quá nhanh để hàng đợi kịp đầy); tư duy bậc độ lớn.

#### Variables / notation

| Ký hiệu | Nghĩa | Đơn vị | Ai biết | Khi nào biết | Vì sao tách riêng |
|---|---|---|---|---|---|
| c | Capacity | traffic unit/s | thiết kế | trước | Đơn vị, không phải realism |
| λA, λB, u, a | Tải nền, managed traffic, biên độ ON/OFF | traffic unit/s | thiết kế | trước | Chuyển thành tỉ số |
| ρA, ρB, ρB′, a/c, η | Tỉ số tải | — | thiết kế | trước | Đại lượng realism thật sự |
| τ, T_mode, h | Tuổi telemetry, thời gian một mode, horizon | s | thiết kế | trước | Chỉ tỉ số κ, h/τ quan trọng |
| CV_w | Độ biến động tốc độ theo cửa sổ w | — | tính từ thiết kế | Part A | So với đo đạc thật |
| P(Q>0), θ, delay | Thống kê hàng đợi dừng | —, 1/unit, s | tính từ thiết kế | Part A | So với buffer thật |
| δ_act | Độ trễ actuation (ngoài plant) | s | nguồn | Part B | Cờ "action ngay" |
| bối cảnh | DC / WAN / enterprise / edge… | — | tác giả | Part B | Một regime có thể IN ở bối cảnh này, OUT ở bối cảnh khác |

#### Ví dụ nhỏ
Route A/B: "Path B chạy trung bình 80% capacity, nhưng cứ khoảng 0,1 s lại nhảy giữa 140% và 20%; telemetry trễ 1 s; controller giữ quyết định 8 s." Câu hỏi realism là: **có mạng thật nào trông như vậy không?** Với mốc 10 ms thay vì 1 s, câu hỏi trở thành: "có datacenter nào telemetry trễ 10 ms, traffic đổi mode mỗi 1 ms, controller giữ quyết định 80 ms, và cài rule nhanh hơn 1 ms không?"

#### Việc tôi phải tự làm vs AI có thể hỗ trợ

| Tôi phải tự làm | AI có thể hỗ trợ |
|---|---|
| Chọn bối cảnh và viết lý do trước | Liệt kê các bối cảnh phổ biến |
| Đọc nguồn (theo `AGENTS.md`), ghi dải, mục, mức đọc | Đề xuất nguồn ứng viên; kiểm nguồn tồn tại |
| Viết luật phân loại; phân loại; viết kết luận | Viết script tính đại lượng suy ra; kiểm công thức bằng mô phỏng |
| Quyết định realism (a/b/c ở Bước 7) | Đóng vai reviewer soi "motivated realism" |

#### Hands-on task

**Part A — Bảng tỉ số (chỉ mức thiết kế)**
- **Bước 1 — Script `implied.py`.**
  - *Vì sao:* biến 216 regime thành ngôn ngữ của thế giới thật.
  - *Làm:* với mỗi regime discovery, tính các tỉ số và đại lượng suy ra (công thức Khái niệm 2). Với 3 regime, lấy giá trị chính xác từ phân phối dừng của engine (atom, delay trung bình, đuôi) để đối chiếu công thức. **Không gọi hàm nào tính $J$, $\Delta$ hay quyết định.**
  - *Kiểm:* bất biến thang; khớp mô phỏng nền telegraph và hàng đợi (như tôi đã làm cho hai giá trị κ).
  - *Ý nghĩa:* bạn có một bảng "regime này trông thế nào ngoài đời".

**Part B — Nguồn** (theo `AGENTS.md`: Hỏi → Tìm → Kiểm → Duyệt → Đọc → Ghi → Dừng; tối đa 3 nguồn mới mỗi lượt; bạn duyệt trước khi tải PDF hay tạo note)
- **Bước 2 — Chọn 2–3 bối cảnh** (đề xuất: datacenter fabric, WAN/ISP, edge/enterprise). Viết lý do chọn **trước** khi đọc.
- **Bước 3 — Điền worksheet** (Phụ lục C) cho từng đại lượng × bối cảnh.

**Nguồn ứng viên** (tên, năm, venue ở bảng này là **từ trí nhớ của tôi, chưa kiểm trong phiên soạn**. Kiểm tồn tại và đúng bản trước khi đọc; không trích con số nào khi chưa đọc mục tương ứng):

| Đại lượng | Nguồn ứng viên | Câu hỏi phải trả lời |
|---|---|---|
| Tuổi telemetry τ | Đo AoI trên testbed dt4n của chính project (MASTER PLAN ghi trung bình ≈ 0,36 s, p95 ≈ 0,6 s — testbed, không phải production); tài liệu streaming telemetry của vendor (gNMI/OpenConfig, sFlow); Rasley et al., "Planck", SIGCOMM 2014 | Tuổi telemetry điển hình (trung bình, p95) ở từng bối cảnh? |
| Biến động traffic theo thang thời gian | Benson, Akella, Maltz, IMC 2010; Kandula et al., IMC 2009; Roy et al., SIGCOMM 2015; Zhang et al. (microburst), IMC 2017; trace công khai (MAWI, CAIDA) nếu muốn tự đo | CV của tốc độ theo cửa sổ 10 ms / 100 ms / 1 s trên loại link nào? Dao động cỡ ±60% capacity có gặp không, ở thang nào? |
| Mức dùng link | Jain et al., B4, SIGCOMM 2013; Hong et al., SWAN, SIGCOMM 2013; Benson et al. 2010 | Link "nóng" chạy ở mức nào, kéo dài bao lâu? |
| Buffer theo thời gian | Appenzeller, Keslassy, McKeown, "Sizing router buffers", SIGCOMM 2004; Alizadeh et al., DCTCP, SIGCOMM 2010 | Buffer tính bằng ms ở từng bối cảnh? |
| Độ trễ actuation | He et al., control plane latency, SOSR 2015; Kuźniar et al., SDN flow tables, PAM 2015 | Cài hoặc đổi một rule mất bao lâu, phân phối thế nào? |
| Thời gian giữ quyết định h | Al-Fares et al., Hedera, NSDI 2010; Benson et al., MicroTE, CoNEXT 2011; chu kỳ TE trong B4/SWAN; CONGA (S03, thang flowlet) | Controller giữ một quyết định reroute bao lâu? |

**Part C — Envelope**
- **Bước 4 — Viết `realism_envelope_v1.md`** gồm dải + nguồn + luật IN/EDGE/OUT. **Commit trước khi phân loại.**

**Part D — Phân loại**
- **Bước 5 — Phân loại 216 regime.** Đánh dấu vùng tín hiệu theo discovery record (được phép: chỉ đọc lại discovery).
- **Bước 6 — Note "điều tôi thấy / điều nó KHÔNG có nghĩa".**
- **Bước 7 — Quyết định realism** (ghi DL):
  - (a) vùng tín hiệu IN ở ít nhất một bối cảnh → giữ, claim mang câu bối cảnh;
  - (b) chỉ EDGE → giữ, gắn cờ, đưa assumption rủi ro nhất vào Phase 6;
  - (c) OUT ở mọi bối cảnh → **realism blocker** → Gate 3R xét NARROW / REFORMULATE / PIVOT (§18).

**Part E — Đưa vào contract**
- **Bước 8 —** frame lấy mẫu cho CF = (vùng hypothesis) ∩ (envelope IN hoặc EDGE), **hoặc** toàn vùng nhưng báo riêng theo realism; cờ assumption: buffer, actuation, mode oracle.

#### Nếu có code
**Code này tồn tại để kiểm:** "regime này, dịch sang đại lượng đo được, trông như thế nào?" (Q3R.3)
- File: `experiments/R3R_04_realism/implied.py` (đề xuất).
- Input: tham số regime, mốc thời gian, bối cảnh.
- Output: bảng tỉ số + đại lượng suy ra; cờ IN/EDGE/OUT.
- Invariant: không import module tính outcome (một test kiểm điều này); bất biến thang (nhân traffic, co thời gian).
- Test: khớp mô phỏng telegraph (CV_w) và hàng đợi (P(Q>0), delay) trên 2–3 trường hợp.

#### Verification
Công thức khớp mô phỏng; mỗi dải có nguồn + mục + mức đọc; `git log` cho thấy envelope commit trước phân loại; người đọc soi phần "motivated realism".

#### Output
Envelope v1; bảng đại lượng suy ra cho 216 regime; DL realism.

#### Interpretation
"Vùng tín hiệu nằm IN / EDGE / OUT ở bối cảnh nào." Mọi claim sau này phải mang theo câu bối cảnh tương ứng.

#### What it does NOT prove
- Không chứng minh plant đúng động học (Phase 6), hay repair khả thi (Phase 7).
- Envelope không đầy đủ; IN **không** có nghĩa là đã validate.

#### Beginner traps
- Nghĩ "capacity = 10" là phi thực tế.
- Chọn bối cảnh sau khi đã phân loại.
- Dùng một nguồn cho mọi bối cảnh.
- Trộn giá trị trung bình với giá trị đỉnh.
- Quên giả định buffer vô hạn.
- Coi IN là validation.
- Lấy số từ abstract mà không đọc mục tương ứng.

#### Self-check
1. Vì sao "capacity = 10" không phải vấn đề realism?
2. Hai regime (τ = 1 s, T_mode = 0,1 s, h = 8 s) và (τ = 10 ms, T_mode = 1 ms, h = 80 ms) khác nhau gì về kết quả chuẩn hóa?
3. Từ bảng ví dụ: vì sao κ = 0,3 làm giả định buffer vô hạn đáng ngờ hơn κ = 0,1?
4. Luật nào chống "motivated realism"?
5. Nếu vùng tín hiệu OUT ở mọi bối cảnh, những lựa chọn hợp lệ là gì?

#### Gate của lesson
*Thông tin trạng thái.* **Track học:** không chặn gì. **Track thực thi:** contract (L3R.5) dùng envelope cho scope; frame CF (L3R.7) dùng envelope.

---

## 12. Lesson 3R.5 — Contract v1.3: khóa luật chơi mới

#### Mục tiêu
Sau lesson này tôi có contract v1.3 LOCKED (tag `contract-v1.3`): mọi term mới có định nghĩa vận hành; ghi rõ cái gì kế thừa từ v1.2 và cái gì đổi; có chính sách số, scope, assumptions và stop rules; và chuỗi Problem → … → Contribution vẫn nối được.

#### Tại sao lesson này cần?
- **Lesson → RQ.** MASTER PLAN XIX.5: khi estimand đổi, phải (1) ghi DL, (2) cập nhật contract và brief, (3) đi lại chuỗi Problem → … → Contribution và đánh dấu mắt xích nào hết hiệu lực. Confirmation cần luật chơi được khóa **trước**.
- **Rủi ro.** Đổi định nghĩa sau khi thấy dữ liệu; chọn ngưỡng theo outcome; để một term mơ hồ ("fresh state", "stakes") rồi diễn giải theo hướng có lợi.

#### Lý thuyết cần hiểu

**Khái niệm 1 — Kế thừa và thay đổi.**
- *Trực giác.* Sửa luật chơi giữa mùa giải: chỉ đổi đúng điều cần đổi, và nói rõ đã đổi gì.
- *Ví dụ / định nghĩa chính xác:*

  | Thành phần | v1.2 | v1.3 (đề xuất) |
  |---|---|---|
  | Plant | Hai path rời; ON/OFF đối xứng; fluid; buffer vô hạn; action có hiệu lực ngay | Giữ nguyên; thêm cờ realism từ L3R.4 |
  | Observation | Một snapshot cố định mỗi ô (theo quantile) | $Y\sim p(y)$ dừng |
  | Regime | Ô lưới; λA neo theo $p_{\text{sw}}$ | Bộ tỉ số tự do; **không neo** (neo dùng dấu của oracle — một thiết kế phụ thuộc outcome, không cần ở mức population) |
  | S0 | Posterior Bayes một observation, luật thật | Giữ |
  | S1 | State thật gồm mode | Giữ; thêm pipeline D22 làm diagnostic |
  | M0 / M1 | D10 / D21 | Giữ |
  | Estimand | $L_{sm}$, $G$ của một ô | $\bar L_{sm}$, $\bar G$ |
  | Chuẩn hóa | $C_{\text{ref}}=L_*$ | Primary $\bar C_{\text{ref}}=\bar L_{11}$; secondary stakes $\bar\sigma$ |
  | ε_R, ε_E | 1% (độ nhạy 0,5% và 2%); 0,5% | Giữ |
  | Numerics | dt cuối chọn ở A01 | (K*, dt*) + kiểm cặp mức cho từng regime |
  | c_sw | 0 (diagnostic) | 0 cho primary |
  | Luật hòa | Stay | Stay; báo khối hòa |
- *Liên hệ.* Part A.

**Khái niệm 2 — Ngưỡng kế thừa.**
- *Trực giác.* Đặt vạch đích sau khi đã thấy ai về nhất thì cuộc đua mất nghĩa.
- *Ví dụ nhỏ.* Nếu bây giờ đổi ε_R thành 5% "vì effect lớn", một regime có 4% bị gọi là "không có effect". Bạn đã chọn ngưỡng khi biết cái gì sẽ qua.
- *Định nghĩa chính xác.* Giữ ε_R = 1% $\bar C_{\text{ref}}$ và tập độ nhạy {0,5%; 1%; 2%} đã khóa ở v1.2. Nếu muốn đổi, lý do phải đến từ **ngoài dữ liệu** (nhu cầu vận hành, chi phí repair) và được ghi DL trước. Muốn nói về độ lớn mạnh hơn ε_R, chỉ dùng các mức đã có trong tập độ nhạy (ví dụ 2%).
- *Liên hệ.* L3R.6 dùng ε_R làm tiêu chí theo từng regime.

**Khái niệm 3 — Primary, secondary, diagnostic.**
- *Trực giác.* Không phải mọi con số bạn báo đều là một phép thử.
- *Định nghĩa.* **Primary:** có verdict, nằm trong họ kiểm soát đa so sánh (Hyp-MV, Hyp-SH). **Secondary:** có verdict riêng, không ảnh hưởng primary (Hyp-MI). **Diagnostic:** chỉ báo cáo, không chấm ($\bar G_{M\mid S_1}$, $\bar\Gamma$, $\bar G_{S\mid M_1}$, $\bar G_{SM}$, P(flip), $\bar F/\bar V$, khối hòa, $\bar R_{00}/\bar C_{\text{ref}}$).
- *Liên hệ.* Số primary nhỏ → ít báo động giả (MASTER PLAN IX.6g).

**Khái niệm 4 — Numerics và stop rules là một phần của luật chơi.**
- *Trực giác.* Một trận đấu cần luật cho trường hợp mất điện, không chỉ luật ghi bàn.
- *Ví dụ.* Nếu 20% regime trong một stratum "chưa phân giải số", bạn không được tự chọn coi chúng là đạt hay không đạt **sau** khi thấy kết quả.
- *Định nghĩa.* Contract ghi: (K*, dt*); cặp kiểm từng regime; dung sai 0,25 pp; luật leo thang; ngưỡng tỉ lệ "chưa phân giải" tối đa $u_{\max}$ cho mỗi stratum chấm; control phải bằng 0 chính xác; anchor phải trùng số pilot.
- *Liên hệ.* L3R.7 dùng nguyên văn.

**Khái niệm 5 — Scope và assumptions.**
- *Định nghĩa.* Giữ bảng AS1–AS9 của MASTER PLAN II.10 và thêm: (AS10) quá trình trước quyết định là dừng; (AS11) S0 là posterior Bayes chính xác dưới luật thật; (AS12) S1 có quyền oracle về mode; (AS13) c_sw = 0 trong primary; (AS14) τ cố định = 1 s làm mốc (không mất tổng quát nếu plant fluid, L3R.4). Mỗi assumption có cột "nếu sai thì sao" và "kiểm ở phase nào" — kèm cờ realism từ L3R.4 (buffer, actuation, mode oracle).

#### Toán cần biết
Không có công thức mới. Ôn lại T07.

#### Variables / notation
Toàn bộ term của contract v1.3, mỗi term theo mẫu Phụ lục A (định nghĩa vận hành / đo bằng gì / đơn vị / ai biết / khi nào biết / không nhầm với / trạng thái).

#### Ví dụ nhỏ
Một mục đã điền:

> **Regime** — *Định nghĩa vận hành:* bộ (ρA, ρB, η, κ, h/τ, a/c) cùng mốc τ = 1 s, c = 10 và các hằng số plant của v1.2. *Đo bằng gì:* tham số thiết kế, không tính từ outcome. *Đơn vị:* không thứ nguyên (h/τ, κ) hoặc theo mốc. *Ai biết:* mọi bên. *Khi nào biết:* trước khi chạy. *Không nhầm với:* ô lưới v1.2 (có quantile observation cố định và λA neo). *Trạng thái:* LOCKED (DL-xxx).

#### Việc tôi phải tự làm vs AI có thể hỗ trợ

| Tôi phải tự làm | AI có thể hỗ trợ |
|---|---|
| Quyết định từng mục OPEN, viết lý do và phương án đã cân nhắc | Liệt kê hệ quả của từng phương án |
| Viết (hoặc duyệt từng dòng) contract v1.3 | Soạn nháp, diff với v1.2, kiểm nhất quán với T07 |
| Đi lại chuỗi Problem → … → Contribution | Đóng vai reviewer: "term nào còn mơ hồ?" |

#### Hands-on task

**Part A — Checklist khóa (mỗi mục: lựa chọn + lý do + phương án khác + DL)**

| # | Mục | Đề xuất | Phương án khác và hệ quả |
|---|---|---|---|
| 1 | Main RQ | KEEP nguyên văn + một câu "đọc theo population" | Đổi câu chữ → phải đi lại toàn chuỗi |
| 2 | Regime | Bộ tỉ số + mốc τ = 1 s; không neo λA | Neo λA như v1.2 → thiết kế phụ thuộc dấu của oracle |
| 3 | Observation | $y=(y_A,y_B)$ backlog tại $t_0-\tau$; mode không quan sát | Quan sát cả mode → đổi nghĩa của S0 và của harm |
| 4 | $p(y)$ | Phân phối dừng trước quyết định (Stay); quadrature K*, atom tại 0 là nút riêng | — |
| 5 | S0 | Posterior Bayes chính xác, luật thật (kế thừa) | Lọc bằng M0 → identity $\bar G_M\ge0$ có thể không còn; để làm robustness ở Phase 5 |
| 6 | S1 | (q, m) thật tại $t_0$; pipeline D22 cho $\bar F/\bar V$ (diagnostic) | Chỉ backlog tươi → đổi estimand chính; pilot chưa đo |
| 7 | M0 / M1 | Kế thừa D10 / D21 | — |
| 8 | Estimand | $\bar L_{sm}$ + sáu contrast; primary $\bar G_M$ (Hyp-MV), $\bar G_S$ (Hyp-SH); secondary Hyp-MI; còn lại diagnostic | Thêm primary → tăng đa so sánh |
| 9 | Chuẩn hóa | Primary % $\bar C_{\text{ref}}$; secondary % stakes $\bar\sigma=\mathbb E_\pi\lvert\Delta\rvert$ (đối chiếu định nghĩa của pilot) | Primary % stakes → phải chọn ngưỡng mới cho thước mới |
| 10 | SESOI | ε_R = 1% (0,5% và 2%); ε_E = 0,5% | Đổi → cần lý do ngoài dữ liệu + DL trước |
| 11 | Numerics | (K*, dt*) từ L3R.3; cặp kiểm; 0,25 pp; leo thang; "chưa phân giải" | — |
| 12 | c_sw | 0 cho primary | Thêm c_sw > 0 → secondary ghép cặp, đặt bằng lý do vật lý (Phase 4) hoặc can thiệp ở Phase 5 |
| 13 | Luật hòa | Stay; báo khối $Y$ có $\lvert\mathbb E[\Delta\mid y]\rvert$ dưới ngưỡng số | — |
| 14 | Information rights | Bảng S0/S1/M0/M1/oracle/evaluator (kế thừa) + "evaluator lấy trung bình theo $p(y)$" | — |
| 15 | Scope & assumptions | AS1–AS14 + cờ realism | — |
| 16 | Exposure | Liệt kê tập discovery; R09/R10 niêm phong; tập CF sinh ở L3R.7 | — |
| 17 | Stop rules | Control sai → dừng run; tỉ lệ "chưa phân giải" > $u_{\max}$ → INCONCLUSIVE cho stratum đó; chính sách deviation (L3R.7) | — |

**Part B — Viết**
- **Bước 1 — `notes/01_definitions_v1_3.md`** (template Phụ lục A) + một bảng diff với v1.2.
- **Bước 2 — Cập nhật brief** (≤ 2 trang) và tạo chỗ cho claim boundary v1.3 (điền ở L3R.6).

**Part C — Đi lại chuỗi nghiên cứu**
- **Bước 3 — Bảng mắt xích:**

  | Mắt xích | v1.2 | v1.3 | Còn hiệu lực? |
  |---|---|---|---|
  | Problem | Routing đổi tải; hai loại repair | Giữ | Có |
  | Gap | Candidate gap ở mức một snapshot | Candidate gap ở mức regime, population | Thu hẹp; cần claim boundary mới |
  | RQ | Main RQ | Main RQ | Có |
  | Hypothesis | PC1–PC6 (card Phase 3) | Hyp-MV, Hyp-SH, Hyp-MI | PC cũ đã đóng; không mang sang |
  | Method | Engine exact một-snapshot | Engine exact population | Mới; cần audit (L3R.3) |
  | Experiment | A04, A05-T | CF (Phase 4) | Mới |
  | Evidence | E1 một-snapshot | E1 population (sau Phase 4) | Chưa có |
  | Contribution | — | — | Chưa có |

**Part D — Khóa**
- **Bước 4 — Tag `contract-v1.3`; DL** ghi: vì sao đổi estimand (evidence: Gate A REFORMULATE + pilot), phương án đã cân nhắc, hệ quả.

#### Nếu có code
**Code này tồn tại để kiểm:** "engine, sampler và scorer có đọc **cùng một** định nghĩa regime không?"
- File: `notes/design/regime_schema_v1_3.json` (JSON schema, đề xuất).
- Input: một regime. Output: hợp lệ / không hợp lệ.
- Invariant: mọi trường bắt buộc có mặt; dải hợp lệ (ví dụ ρ < 1 trước quyết định).
- Test: 216 regime discovery đều hợp lệ; một regime cố tình sai bị từ chối.

#### Verification
Mọi term có định nghĩa không phụ thuộc outcome; danh sách identity khớp T07; một lần đọc to từ đầu đến cuối không gặp term chưa định nghĩa; (nếu có) người đọc độc lập.

#### Output
Contract v1.3, DL, brief cập nhật, schema regime, tag `contract-v1.3`.

#### Interpretation
Luật đã khóa. Từ đây, mọi thay đổi đều phải lộ ra trong git và trong decision log.

#### What it does NOT prove
Không chứng minh novelty, không chứng minh hypothesis, không chứng minh realism.

#### Beginner traps
- Định nghĩa term sao cho pilot "đẹp".
- Đổi ε_R "vì effect lớn".
- Để "fresh state" hay "stakes" không định nghĩa.
- Trộn hai chuẩn hóa.
- Quên luật số và stop rules.
- Viết contract *sau* hypothesis cards để hypothesis dễ qua.

#### Self-check
1. Vì sao v1.3 không neo λA như v1.2?
2. Vì sao giữ ε_R = 1% dù effect pilot tới 13%?
3. Phân biệt primary, secondary, diagnostic bằng một ví dụ của project.
4. Identity $\bar G_M\ge0$ phụ thuộc vào lựa chọn nào trong checklist?
5. Mắt xích nào của chuỗi nghiên cứu đã đổi, mắt xích nào giữ?

#### Gate của lesson
*Thông tin trạng thái.* **Track học:** không chặn gì. **Track thực thi:** hypothesis cards (L3R.6) và thiết kế CF (L3R.7) chỉ khóa sau tag `contract-v1.3`.

---

## 13. Lesson 3R.6 — Hypothesis cards: biến discovery thành prediction có thể sai

#### Mục tiêu
Sau lesson này tôi có 1–2 primary hypothesis (Hyp-MV, Hyp-SH) và tối đa 1 secondary (Hyp-MI). Mỗi card có: vùng định nghĩa bằng luật tọa độ, vùng đối chứng có thể thất bại, đại lượng, tiêu chí theo regime và tiêu chí gộp, cơ chế ứng viên, quan sát bác bỏ, kiểm identity, kiểm prior, và các hệ quả chung đã khai báo.

#### Tại sao lesson này cần?
- **Lesson → RQ1** (characterization ở mức population) và chuẩn bị cho RQ2.
- **Rủi ro.** SR2 (obviousness); kill-K8 (chỉ tái hiện identity hay prior); claim trùng điều đã biết (K-RM); vùng vẽ sát đỉnh discovery nên thất bại vì regression to the mean.

#### Lý thuyết cần hiểu

**Khái niệm 1 — Từ pattern discovery thành claim theo vùng.**
- *Trực giác.* "Chỗ này có cá" (đã thấy) → "ở mọi khúc sông sâu và chảy chậm, đa số lần thả câu sẽ được cá" (có thể sai ở một khúc sông mới).
- *Ví dụ hình thức (số giả định, không phải đề xuất).* Ω_MV+ = {ρB ∈ [0,80; 0,90], κ ∈ [0,1; 0,3], h/τ ∈ [8; 16], …}. Dự đoán: tỉ lệ regime CF trong Ω_MV+ có $\bar G_M/\bar C_{\text{ref}}\ge\varepsilon_R$ có cận dưới 97,5% lớn hơn 0,5.
- *Định nghĩa chính xác.* Claim theo vùng = vùng (luật trên tọa độ thiết kế) + đại lượng + tiêu chí theo regime + tiêu chí gộp trên vùng + cơ chế ứng viên + quan sát bác bỏ.
- *Liên hệ.* Part D–E.

**Khái niệm 2 — Vẽ vùng mà không overfit.**
- *Trực giác.* Đường biên vẽ quá sát các điểm đã thấy sẽ sai ở điểm mới.
- *Ví dụ nhỏ.* "λB ≥ 7,93" (tối ưu theo dữ liệu discovery) so với "ρB ≥ 0,8" (số tròn của lưới thiết kế).
- *Định nghĩa chính xác.* Tối đa 3 tọa độ "chủ động"; các tọa độ còn lại có dải; ngưỡng đặt ở số tròn hoặc giá trị của lưới thiết kế; **mỗi luật đã thử được ghi vào forking-paths log**, kể cả luật bị bỏ.
- *Liên hệ.* Part D.

**Khái niệm 3 — Regression to the mean và chọn cực trị.**
- *Trực giác.* Người cao nhất lớp không cho bạn biết chiều cao trung bình của lớp.
- *Ví dụ nhỏ.* X2065 là regime mạnh nhất trong 216; một regime mới trong cùng vùng nhiều khả năng yếu hơn. Với chỉ báo: tôi mô phỏng 5 chỉ báo cùng có Spearman thật 0,6 với outcome trên 168 regime; chỉ báo "tốt nhất trong 5" có Spearman trung bình khoảng 0,65, tức thổi phồng khoảng 0,05. Mức thổi phồng thật trong pilot chưa biết; có thể nhỏ hơn nếu 5 chỉ báo tương quan với nhau.
- *Định nghĩa chính xác.* Ngưỡng lấy từ **ý nghĩa** (ε_R; "đa số regime"), không từ độ lớn discovery. Kỳ vọng effect ở confirmation nhỏ hơn ở discovery.
- *Liên hệ.* Part E.

**Khái niệm 4 — Lọc identity và khai báo hệ quả chung.**
- *Trực giác.* Đừng đặt cược vào điều chắc chắn xảy ra.
- *Ví dụ.* "Trong vùng harm, $\bar\Gamma>0$" — chắc chắn (L3R.2, hệ quả 4).
- *Định nghĩa chính xác.* Mỗi câu được gắn nhãn: identity / hệ quả của hypothesis khác / có thể sai độc lập. Hệ quả cần khai báo: Hyp-SH đúng ở regime $r$ ⇒ $\bar\Gamma_r>0$ và $\bar G_{M\mid S_1,r}\ge\lvert\bar G_{S,r}\rvert$. Vì vậy Hyp-MV dùng $\bar G_M$, **không** dùng $\bar G_{M\mid S_1}$.
- *Liên hệ.* Part B.

**Khái niệm 5 — Lọc prior.**
- *Trực giác.* Không gọi bánh xe là phát minh.
- *Ví dụ.* "Thông tin thêm có thể làm hại chính sách xấp xỉ" → K-RM (Phase 2).
- *Định nghĩa chính xác.* Mỗi card có dòng "đã biết gần nhất" và "khác ở trục nào": E (estimand), M (phép can thiệp), R (regime) — cách ghi của Phase 2.
- *Liên hệ.* Part C.

**Khái niệm 6 — Vùng đối chứng phải có thể thất bại.**
- *Trực giác.* Một bài kiểm mà ai cũng qua thì không kiểm gì.
- *Ví dụ nhỏ.* Ω_MV− = "ρB ≤ 0,3" → gần như không có gì để quyết định, nên $\bar G_M\approx0$ một cách tầm thường. Tốt hơn: giữ nguyên các tọa độ khác như Ω_MV+, chỉ "lật" một nhân tố (ví dụ ρB ≤ 0,6, tức B có nhiều headroom), với tải A đủ cao để quyết định vẫn có stakes.
- *Định nghĩa chính xác.* Tính "quyết định có stakes" phải được bảo đảm bằng **tọa độ thiết kế**, không bằng stakes tính trên regime CF (đó là outcome).
- *Liên hệ.* L3R.7.

**Khái niệm 7 — Chỉ báo M0-only: khóa nguyên văn, hiểu nó đo gì.**
- *Trực giác.* Chỉ báo đo "M0 lưỡng lự tới đâu giữa Stay và Switch khi snapshot thay đổi". Model repair chỉ có giá trị khi M0 và M1 bất đồng; M0 càng lưỡng lự càng dễ bất đồng. Vì vậy mối liên hệ có thể phần lớn là **hình học quyết định** (giống threshold null của RQ2), không nhất thiết là động học hàng đợi.
- *Ví dụ.* Spearman là tính chất của bộ ba (predictor, outcome, **quần thể regime**). Một mẫu trộn hai stratum khác xa nhau theo thiết kế có thể cho Spearman cao chỉ vì predictor "nhận ra" stratum.
- *Định nghĩa chính xác.* Khóa đúng công thức (chép hàm từ code pilot kèm hash). Tiêu chí: Spearman trên một mẫu CF đã định nghĩa trước. Báo kèm Spearman trong từng stratum và Spearman của một predictor ngây thơ chỉ dùng tọa độ thiết kế (ví dụ ρB).
- *Liên hệ.* Hyp-MI (secondary); RQ2 sau này (§22).

#### Toán cần biết
*Cần ôn trước:* tỉ lệ nhị thức; cận tin cậy một phía; Spearman.

**Cận dưới một phía Clopper–Pearson** (tôi tính bằng scipy):

| Quan sát | Cận dưới 95% | Cận dưới 97,5% |
|---|---:|---:|
| 14/20 | 0,49 | 0,46 |
| 16/20 | 0,60 | 0,56 |
| 21/30 | 0,53 | 0,51 |
| 24/30 | 0,64 | 0,61 |
| 28/40 | 0,56 | 0,53 |
| 32/40 | 0,67 | 0,64 |
| 30/30 | 0,90 | 0,88 |

Đọc: thấy 21/30 regime đạt chỉ cho phép nói "tỉ lệ thật lớn hơn khoảng 0,51" ở mức 97,5%.

**Khoảng tin cậy ≈ 95% của Spearman** (Fisher z với SE ≈ $\sqrt{1{,}06/(n-3)}$; kiểm bằng mô phỏng ở n = 40, ρ = 0,75: [0,54; 0,87]):

| Spearman quan sát | n = 30 | n = 40 | n = 60 | n = 100 |
|---|---|---|---|---|
| 0,50 | [0,16; 0,73] | [0,21; 0,71] | [0,27; 0,67] | [0,33; 0,64] |
| 0,75 | [0,53; 0,88] | [0,57; 0,86] | [0,61; 0,85] | [0,65; 0,83] |

**Bonferroni:** hai primary, mỗi cái kiểm một phía ở mức 2,5% → dùng cận 97,5%.

#### Variables / notation

| Ký hiệu | Nghĩa | Ai đặt | Khi nào | Vì sao tách riêng |
|---|---|---|---|---|
| Ω_MV+, Ω_MV− | Vùng dự đoán dương / đối chứng của Hyp-MV | tác giả | trước khi sinh mẫu | Miền của claim |
| Ω_SH+, Ω_SH− | Như trên cho Hyp-SH | tác giả | như trên | — |
| Ω_BND | Dải quanh biên của luật vùng | tác giả | như trên | Kiểm biên, chỉ mô tả |
| $\pi_0$ | Ngưỡng tỉ lệ (đề xuất 0,5 = "đa số") | tác giả | trước | Tiêu chí gộp |
| $r_0$ | Ngưỡng Spearman của Hyp-MI | tác giả | trước | Tiêu chí secondary |
| $I_{M_0}$ | Chỉ báo M0-only (công thức của pilot, khóa nguyên văn) | — | khóa ở đây | Không được thử biến thể |

#### Ví dụ nhỏ
Một card hình thức đã điền (**mọi con số là minh họa, không phải đề xuất**):

```text
Hyp-MV — Model repair có giá trị khi B ít headroom, traffic đổi nhanh, horizon dài
Nguồn discovery: Stage 2, pilot v1 (hoặc v2 nếu sửa bug)
Câu một dòng: Khi B gần bão hòa và traffic nền đổi nhanh so với tuổi telemetry,
  sửa model (mean → luật ngẫu nhiên đúng) giảm regret kỳ vọng ít nhất ε_R
  ở đa số regime, kể cả khi state vẫn cũ.
Vùng: Ω_MV+ = { ρB ∈ [0,80; 0,90]; κ ∈ [0,1; 0,3]; h/τ ∈ [8; 16]; η ∈ […]; ρA ∈ […] }
Đối chứng: Ω_MV− = như Ω_MV+ nhưng ρB ∈ [0,50; 0,60]  (chỉ lật headroom của B)
  Vì sao có thể thất bại: tải A vẫn cao nên quyết định vẫn có stakes;
  nếu M0 vẫn sai nhiều ở đây, Ω_MV− sẽ không đạt.
Đại lượng: Ḡ_M / C̄ref · tiêu chí theo regime: ≥ ε_R (1%)
Tiêu chí gộp: Ω_MV+: cận dưới 97,5% của tỉ lệ > 0,5 · Ω_MV−: cận trên 97,5% < 0,5
Độ lớn (mô tả, không chấm): median, quantile 10/90 của Ḡ_M/C̄ref và của % stakes
Cơ chế ứng viên: M0 thay luật ON/OFF bằng tốc độ trung bình nên bỏ qua phần
  Jensen ở biên rỗng; khi B gần bão hòa, phần bỏ qua sau Switch lớn và
  horizon dài cộng dồn nó (candidate từ POST_PHASE3_CONTEXT §13 — chưa kiểm)
Dự đoán phụ về cơ chế (mô tả, không ảnh hưởng verdict): trong Ω_MV+,
  bias của M0 nghiêng về Switch (E[Δ̂_M0 − Δ] < 0)
Bác bỏ nếu: Ω_MV+ có cận trên 97,5% < 0,5
Identity liên quan: Ḡ_M ≥ 0 và Ḡ_M ≤ σ̄ (không phải prediction)
Đã biết gần nhất: [P11] EVMI; [P13] transient/horizon; Jensen ở biên rỗng (Phase 3)
  · khác ở: E (regret population với observation cũ), R (finite-load rerouting)
Realism: Ω_MV+ IN/EDGE/OUT ở bối cảnh […] (L3R.4)
Provenance: tác giả viết / AI soạn, tác giả duyệt (ngày)
Loại: PRIMARY
```

#### Việc tôi phải tự làm vs AI có thể hỗ trợ

| Tôi phải tự làm | AI có thể hỗ trợ |
|---|---|
| Chọn vùng (từ bảng discovery), viết cơ chế, viết điều kiện bác bỏ | Tóm tắt discovery theo từng luật vùng (được phép: đó là discovery) |
| Quyết định primary/secondary | Kiểm identity và hệ quả chung giữa các card |
| Viết dòng "đã biết gần nhất / khác ở đâu" | Tính bảng Clopper–Pearson, Spearman; đóng vai reviewer |

#### Hands-on task

**Part A — Kiểm kê tín hiệu.** Từ discovery record (pilot v1 hoặc v2): liệt kê mọi tín hiệu kèm stage và mức thích nghi.

**Part B — Lọc identity.** Gắn nhãn identity / hệ quả / có thể sai cho từng câu ứng viên (dùng sanity list v1.3 từ T07).

**Part C — Lọc prior.** Với mỗi câu còn lại: dòng đã biết gần nhất, khác ở E/M/R; nếu không khác ở trục nào → bỏ (kill-K14, §22).

**Part D — Vẽ vùng.**
- *Vì sao:* claim phải có miền viết bằng luật.
- *Làm:* chạy bảng discovery theo vài luật ứng viên; mỗi lần chạy append một dòng vào forking-paths log.
- *Kiểm:* luật cuối có ≤ 3 tọa độ chủ động, ngưỡng tròn, vùng đối chứng "lật đúng một nhân tố".
- *Ý nghĩa:* biên vùng có lý do, không phải đường cong ôm sát dữ liệu.

**Part E — Viết card** theo template (ví dụ trên). Mỗi card qua **7 kiểm:**
1. Có thể sai (có một kết quả tưởng tượng được làm nó FALSIFY).
2. Không phải identity.
3. Hệ quả chung đã khai báo.
4. Đã lọc prior.
5. Vùng định nghĩa chỉ bằng tọa độ thiết kế.
6. Vùng đối chứng có thể thất bại.
7. Có cơ chế ứng viên viết bằng lời của bạn.

**Part F — Primary / secondary + đa so sánh.** Tối đa 2 primary (Bonferroni, cận 97,5%), tối đa 1 secondary. Ghi quyết định.

#### Nếu có code
**Code này tồn tại để kiểm:** "trong dữ liệu discovery, luật vùng này tóm tắt pattern ra sao?" — chỉ để vẽ vùng, **không** phải evidence.
- File: `experiments/R3R_06_regions/discovery_tables.py` (đề xuất).
- Input: discovery (pilot v1/v2) + một luật vùng.
- Output: số regime trong vùng; tỉ lệ vượt ngưỡng; một dòng mới trong forking-paths log.
- Invariant: chỉ đọc dữ liệu discovery; không đọc gì liên quan CF.
- Test: luật rỗng → 0 regime; luật bao tất cả → 216.

#### Verification
Mỗi card qua 7 kiểm; forking-paths log đầy đủ; read-back: bạn giải thích được mỗi card cho một người trong 2 phút.

#### Output
`notes/phases/PHASE_3R_hypothesis_cards.md` (hash ở L3R.8); forking-paths log; claim boundary v1.3 (cập nhật dòng "đã biết / khác ở đâu").

#### Interpretation
Bạn có câu hỏi sẵn sàng để kiểm.

#### What it does NOT prove
Không nói gì về việc hypothesis đúng hay sai.

#### Beginner traps
- Vẽ vùng ôm quanh X2065.
- Đặt ngưỡng bằng độ lớn discovery ("vì X2065 có 13%").
- Đưa identity vào card.
- Viết "fresh telemetry có hại".
- Viết 6 hypothesis "cho chắc".
- Thử thêm biến thể của chỉ báo M0.

#### Self-check
1. Vì sao Hyp-MV dùng $\bar G_M$ mà không dùng $\bar G_{M\mid S_1}$?
2. Một vùng đối chứng tầm thường trông như thế nào, và vì sao nó vô dụng?
3. Thấy 21/30 regime đạt thì được nói gì ở mức 97,5%?
4. Vì sao Spearman 0,75 của pilot không phải kỳ vọng cho confirmation?
5. Dòng "đã biết gần nhất" của Hyp-SH là gì, và Hyp-SH khác nó ở trục nào?

#### Gate của lesson
*Thông tin trạng thái.* **Track học:** không chặn gì. **Track thực thi:** L3R.7 cần card đã qua 7 kiểm.

---

## 14. Lesson 3R.7 — Thiết kế confirmation: mẫu regime mới, luật chấm, khả năng phân biệt, dry-run

#### Mục tiêu
Sau lesson này tôi có một thiết kế confirmation chạy được đúng một lần: khung lấy mẫu và seed đã khóa; danh sách regime CF (chỉ tham số); cỡ mẫu có lý do; control và anchor; luật hợp lệ số; luật chấm bốn verdict; xử lý đa so sánh; scorer đã test bằng bảng giả; và dry-run trên dữ liệu discovery.

#### Tại sao lesson này cần?
- **Lesson → Q3R.5.**
- **Rủi ro.** Pseudo-replication (mẫu "mới" thật ra dính sát discovery); thiết kế quá yếu (INCONCLUSIVE do thiết kế); thiết kế tầm thường (PASS do thiết kế); luật chấm mơ hồ để rồi diễn giải sau khi thấy outcome; hết ngân sách giữa chừng (và bị cám dỗ nhìn kết quả từng phần).

#### Lý thuyết cần hiểu

**Khái niệm 1 — Khung lấy mẫu và rút thăm với seed khóa trước.**
- *Trực giác.* Rút thăm thay vì chọn tay; công bố cách rút **trước** khi rút.
- *Ví dụ nhỏ.* Trong Ω_MV+ có ρB ∈ [0,80; 0,90], κ ∈ [0,1; 0,3], h/τ ∈ [8; 16]: rút đều ρB; rút log-đều κ và h/τ (vì chúng là thang tỉ lệ: từ 0,1 lên 0,2 "xa" bằng từ 0,15 lên 0,3).
- *Định nghĩa chính xác.* Frame = tích các dải (contract + vùng + envelope). Trong mỗi stratum, rút ngẫu nhiên độc lập. Seed và phiên bản code sampler được commit trước. Danh sách sinh **một lần**. Nếu phải sinh lại vì bug sampler → ghi lý do và giữ danh sách cũ trong log.
- *Liên hệ.* Part A, Part E.

**Khái niệm 2 — Strata, control và anchor.**

| Stratum | Mục đích | Chấm? |
|---|---|---|
| Ω_MV+ | Kiểm Hyp-MV | Primary |
| Ω_MV− | Đối chứng Hyp-MV (lật một nhân tố) | Primary (cùng Hyp-MV) |
| Ω_SH+ (nếu khác Ω_MV+) | Kiểm Hyp-SH | Primary |
| Ω_SH− | Đối chứng Hyp-SH | Primary hoặc mô tả (bạn quyết trước) |
| Ω_BND | Quanh biên của luật vùng | Mô tả, không chấm |
| Control | Zero-action ($u=0$); regime conservation (không chạm biên rỗng) | Validity: phải bằng 0 **chính xác** |
| Anchor | 2–3 regime discovery chạy lại | Validity: phải trùng số pilot (v1 hoặc v2) |

Nếu Ω_SH+ trùng Ω_MV+, một stratum phục vụ cả hai primary (tiết kiệm tính toán; hai verdict tương quan với nhau là chuyện bình thường, Bonferroni vẫn đúng).

**Khái niệm 3 — Cỡ mẫu: độ chính xác và khả năng phân biệt.**
- *Trực giác.* Tung đồng xu 5 lần không phân biệt được đồng xu lệch 60/40 với đồng xu cân.
- *Ví dụ nhỏ (tôi tính bằng scipy).* Tiêu chí "cận dưới 97,5% của tỉ lệ > 0,5":

  | n mỗi stratum | Cần ≥ k regime đạt | P(PASS) nếu tỉ lệ thật = 0,5 | 0,6 | 0,7 | 0,8 | 0,9 |
  |---:|---:|---:|---:|---:|---:|---:|
  | 20 | 15 (75%) | 0,021 | 0,13 | 0,42 | 0,80 | 0,99 |
  | 30 | 21 (70%) | 0,021 | 0,18 | 0,59 | 0,94 | 1,00 |
  | 40 | 27 (68%) | 0,019 | 0,21 | 0,70 | 0,98 | 1,00 |
  | 60 | 39 (65%) | 0,014 | 0,26 | 0,84 | 1,00 | 1,00 |

  Cột "0,5" là xác suất PASS khi hiện tượng thật ra chỉ "hòa" — luôn nhỏ (khoảng 2%), đúng như thiết kế muốn. Nếu tỉ lệ thật chỉ là 0,7, n = 20 cho PASS chưa tới một nửa số lần: dù hiện tượng có thật, kết quả nhiều khả năng là WEAKEN.

  Vùng đối chứng, tiêu chí "cận trên 97,5% < 0,5": 4/20 → 0,44 (đạt); 6/20 → 0,54 (không đạt); 6/30 → 0,39; 8/30 → 0,46; 8/40 → 0,36.
- *Định nghĩa chính xác.* Chọn n theo hai thứ: (i) tỉ lệ thật **tối thiểu** mà bạn muốn có ít nhất 80% cơ hội PASS — chọn từ ý nghĩa, không từ đỉnh discovery; (ii) ngân sách thời gian (t_reg từ L3R.3 Part D).
- *Liên hệ.* Part B.

**Khái niệm 4 — Luật chấm bốn verdict.**

*Bước 0 — validity (áp cho mọi hypothesis):* control bằng 0 chính xác; anchor trùng số; tỉ lệ regime "chưa phân giải số" ≤ $u_{\max}$ (ví dụ 10%) trong mỗi stratum được chấm. Không đạt → **INCONCLUSIVE**, không phải FALSIFY.

*Hyp-MV (template):*
- **PASS:** Ω_MV+: cận dưới 97,5% của tỉ lệ ($\bar G_M/\bar C_{\text{ref}}\ge\varepsilon_R$) > 0,5 **và** Ω_MV−: cận trên 97,5% < 0,5.
- **FALSIFY:** Ω_MV+: cận trên 97,5% < 0,5 (đa số regime trong vùng dự đoán dương *không* có effect).
- **WEAKEN:** không PASS, không FALSIFY, nhưng ước lượng điểm đúng hướng. Ví dụ: Ω_MV+ đạt nhưng Ω_MV− cũng có effect (effect không đặc thù vùng); hoặc tỉ lệ điểm > 0,5 nhưng cận dưới chưa qua.
- **INCONCLUSIVE:** Bước 0 không đạt.

*Hyp-SH (template):* như trên với tiêu chí theo regime $\bar G_S/\bar C_{\text{ref}}\le-\varepsilon_R$. Thêm một trường hợp **WEAKEN** riêng: harm có dấu âm ở đa số regime nhưng phần lớn nằm giữa −ε_R và 0 ("có harm nhưng dưới ngưỡng thực dụng").

*Hyp-MI (secondary, template):* PASS nếu Spearman($I_{M_0}$, $\bar G_M/\bar C_{\text{ref}}$) trên mẫu gộp đã định nghĩa trước ≥ $r_0$ **và** cận dưới 95% > 0. Báo kèm Spearman của predictor ngây thơ (ví dụ ρB) trên cùng mẫu; nếu predictor ngây thơ ≥ $I_{M_0}$ → **WEAKEN** ("chỉ báo không thêm gì ngoài tọa độ thiết kế").

*Regime "chưa phân giải số":* loại khỏi mẫu số, báo riêng, và chạy phân tích độ nhạy (coi tất cả là đạt / tất cả là không đạt). Nếu verdict đổi theo phân tích độ nhạy → hạ một bậc (PASS → WEAKEN).

**Khái niệm 5 — Dry-run và diễn tập.**
- *Trực giác.* Diễn tập chữa cháy trước khi có cháy thật.
- *Ví dụ.* Scorer nhận các bảng **giả** được dựng để rơi đúng vào từng verdict. Dry-run trên dữ liệu discovery (pilot v1/v2) gần như chắc chắn ra PASS vì vùng được vẽ từ chính dữ liệu đó → **không phải evidence**, chỉ kiểm đường ống.
- *Định nghĩa chính xác.* Scorer là hàm thuần: (bảng outcome, `prereg.json`) → verdict; không đọc gì khác; kiểm hash của `prereg.json` trước khi chạy.
- *Liên hệ.* Part D, Part F.

**Khái niệm 6 — Chính sách sai lệch (deviation) khi đã bắt đầu Phase 4.**
- **Được:** sửa bug validity (ghi log) rồi chạy lại **toàn bộ** CF với **cùng** phân tích.
- **Không được:** đổi ngưỡng, vùng, mẫu, metric; bỏ regime sau khi thấy outcome; dừng sớm khi "thấy đủ".

#### Toán cần biết
Nhị thức; Clopper–Pearson; xác suất PASS (power); Bonferroni; rút đều và rút log-đều.

#### Variables / notation

| Ký hiệu | Nghĩa | Ai đặt | Khi nào | Vì sao tách riêng |
|---|---|---|---|---|
| $n_s$ | Số regime mỗi stratum | tác giả | Part B | Độ chính xác |
| seed | Seed của sampler | tác giả | trước khi sinh | Tái lập, chống chọn tay |
| frame | Tích các dải được phép | contract + card + envelope | trước | Miền của mẫu |
| $u_{\max}$ | Tỉ lệ "chưa phân giải số" tối đa | contract | trước | Stop rule |
| verdict | PASS / WEAKEN / FALSIFY / INCONCLUSIVE | scorer | Phase 4 | Không để lúc chấm có quyền chọn |
| CF-### | ID regime confirmation | sampler | Part E | Không trùng X#### |

#### Ví dụ nhỏ
Route A/B: bạn muốn biết "ở các cặp đường mà B gần đầy và traffic đổi nhanh, model tốt hơn có thường giúp không". Bạn rút thăm 30 cặp đường mới trong vùng đó, và 30 cặp trong vùng đối chứng (B rộng rãi hơn, mọi thứ khác giống). Trước khi xem kết quả, bạn viết: "nếu ít nhất 21/30 ở vùng thứ nhất giúp ≥ 1%, và không quá vài cặp ở vùng thứ hai, thì PASS".

#### Việc tôi phải tự làm vs AI có thể hỗ trợ

| Tôi phải tự làm | AI có thể hỗ trợ |
|---|---|
| Chọn strata, n, $\pi_0$, $r_0$, $u_{\max}$, rút đều hay log-đều | Viết sampler, scorer, test; tính bảng power |
| Duyệt kết quả scorer trên bảng giả | Dựng bảng giả phủ mọi nhánh verdict |
| Viết đoạn "vì sao mỗi hypothesis có thể thất bại" | Ước lượng thời gian chạy từ t_reg |

#### Hands-on task

**Part A — Frame và strata.** Từ contract + card + envelope: viết frame; định nghĩa từng stratum; quyết định rút đều hay log-đều cho mỗi tọa độ.

**Part B — Cỡ mẫu và ngân sách.** Dùng bảng power + t_reg → chọn $n_s$. Ghi: "với $n_s$ = …, nếu tỉ lệ thật ≥ … thì xác suất PASS ≥ 80%".

**Part C — Control và anchor.** Chọn 2–3 regime control (zero-action, conservation) và 2–3 anchor từ discovery.

**Part D — Luật chấm → `prereg.json` → scorer + test.**
- *Vì sao:* luật chấm phải là code, không phải lời.
- *Làm:* chuyển Khái niệm 4 thành `prereg.json` (ngưỡng, strata, α, $u_{\max}$, $r_0$); viết `score.py`; dựng bảng giả cho **mọi** nhánh verdict.
- *Kiểm:* mỗi nhánh có ít nhất một test; scorer từ chối nếu hash `prereg.json` không khớp.

**Part E — Sinh danh sách CF (chỉ tham số) một lần.**
- *Làm:* `sample.py` với seed đã commit → `regimes_cf.json`; hash.
- *Kiểm:* không regime nào trùng discovery (216), A04 hay ô R; báo khoảng cách nhỏ nhất tới discovery (tính trên tọa độ chuẩn hóa về [0, 1] theo frame); khai báo trước một phân tích độ nhạy *mô tả* loại các CF quá gần discovery.
- *Ý nghĩa:* mẫu mới thật sự, và mọi người kiểm lại được.

**Part F — Dry-run trên discovery.** Chạy scorer trên pilot v1/v2. Ghi rõ: "kiểm đường ống, không phải evidence".

**Part G — Kiểm khả năng phân biệt.** Với mỗi hypothesis, viết một đoạn: "kết quả nào trên CF sẽ làm nó FALSIFY, và vì sao kết quả đó *có thể* xảy ra". Nếu không viết được → card chưa đủ tốt, quay lại L3R.6.

#### Nếu có code
**Code này tồn tại để kiểm:** "các prediction đã khóa có đứng trên regime mới không?" — được viết **bây giờ** nhưng chỉ chạy ở Phase 4.

| File (đề xuất) | Vai trò | Invariant |
|---|---|---|
| `experiments/CF_v13/sample.py` | Frame → `regimes_cf.json` | Tất định theo seed; mọi regime nằm trong frame và hợp lệ theo schema |
| `experiments/CF_v13/score.py` | Hàm thuần: outcome + `prereg.json` → verdict | Chỉ đọc hai input này; kiểm hash |
| `experiments/CF_v13/run.py` | Phase 4: chạy engine trên CF | Từ chối chạy nếu thiếu cờ `--confirmation-run` hoặc hash prereg không khớp; không có tham số nào đổi luật |
| `experiments/CF_v13/prereg.md`, `prereg.json` | Prereg người đọc / máy đọc | Hai file khớp nhau (test) |
| `experiments/CF_v13/tests/` | Test sampler + scorer | Mọi nhánh verdict được phủ |

#### Verification
Mọi nhánh verdict có test; danh sách regime tái lập được từ seed; hash khớp; dry-run chạy hết đường ống; (nếu có) người đọc đọc thiết kế.

#### Output
`notes/design/confirmation_v1_3.md`; `regimes_cf.json` (chỉ tham số, có hash); scorer + test; bảng power; ước lượng thời gian chạy.

#### Interpretation
Bạn biết **trước** điều gì sẽ là PASS, WEAKEN, FALSIFY hay INCONCLUSIVE.

#### What it does NOT prove
Không chứng minh hypothesis đúng; không nói gì ngoài frame đã khai báo.

#### Beginner traps
- Tính outcome trên CF "chỉ để đo thời gian chạy".
- Rút lại seed cho tới khi mẫu "trông đẹp".
- Loại regime sau khi thấy outcome.
- Đặt ngưỡng sau dry-run.
- n quá nhỏ (INCONCLUSIVE/WEAKEN do thiết kế).
- Vùng đối chứng tầm thường.

#### Self-check
1. Vì sao rút log-đều cho κ và h/τ?
2. Với n = 20 và tỉ lệ thật 0,7, xác suất PASS khoảng bao nhiêu? Bạn rút ra gì?
3. Vì sao dry-run trên discovery ra PASS không phải là evidence?
4. Khi một control không bằng 0, verdict là gì, và vì sao không phải FALSIFY?
5. Sau khi Phase 4 bắt đầu, bạn được và không được thay đổi những gì?

#### Gate của lesson
*Thông tin trạng thái.* **Track học:** không chặn gì. **Track thực thi:** L3R.8 cần danh sách CF có hash, scorer có test phủ mọi nhánh, dry-run đã chạy, và đoạn "khả năng phân biệt" cho mỗi hypothesis.

---

## 15. Lesson 3R.8 — Freeze, người đọc độc lập, Gate 3R và closeout

#### Mục tiêu
Sau lesson này prereg v1.3 (cards + thiết kế + scorer + danh sách regime) đã commit với hash; một người đọc thật (nếu bạn chọn) đã đọc; Gate 3R có nhãn trong decision log; closeout đã viết với hai mục đầu do tôi tự viết; MASTER PLAN được vá; và có tag `phase-3R-closeout`.

#### Tại sao lesson này cần?
- Đây là bước cuối trước một hành động **không đảo ngược**: sau khi chạy, tập CF trở thành dữ liệu đã thấy.
- **Rủi ro.** ER3: chuỗi từ review hậu nghiệm tới pilot có nhiều phần do AI soạn, nên dễ sai cùng hướng. ER1: phình quy trình. ER7: áp lực lịch khiến bỏ qua gate.

#### Lý thuyết cần hiểu
- **Đóng băng = thứ tự commit + hash.** *Trực giác:* phong bì niêm phong trước trận đấu. *Định nghĩa:* mọi file prereg có hash ghi trong DL; `git log` cho thấy chúng có trước mọi outcome CF.
- **Người đọc thật khác review của AI.** *Ví dụ (DL-026, Phase 3):* lưới v1 có 13/28 ô mà Stay áp đảo theo cấu trúc; lỗi lọt qua chính quy trình đã tạo ra nó. *Định nghĩa:* người có quyền nói "không" đọc và phản hồi được ghi (vai trò, ngày, đọc gì, đã sửa gì). Review do AI viết không tính cho P0-V10.
- **Validity tách khỏi outcome ở gate.** Phase 3R chưa có outcome khoa học mới; "outcome" của phase là: engine đúng hay có bug, realism IN/EDGE/OUT, còn bao nhiêu claim sau khi lọc.
- **Bước không đảo ngược.** Sau Phase 4, mọi giả thuyết mới cần một mẫu mới.

#### Toán cần biết
Không có.

#### Variables / notation
Không có biến mới.

#### Ví dụ nhỏ
"Audit PASS; realism: Ω_MV+ IN ở bối cảnh edge/enterprise, OUT ở WAN; Hyp-SH bị lọc vì không khác K-RM ở trục nào → chỉ còn Hyp-MV (primary) và Hyp-MI (secondary)" → nhãn hợp lý là **NARROW** (một primary, bối cảnh giới hạn), rồi sang Phase 4.

#### Việc tôi phải tự làm vs AI có thể hỗ trợ

| Tôi phải tự làm | AI có thể hỗ trợ |
|---|---|
| Chọn nhãn Gate 3R; viết lý do; viết hai mục đầu closeout | Kiểm mỗi claim trong gate note có link tới evidence |
| Quyết định có mời người đọc không, mời ai | Soạn gói đọc và danh sách câu hỏi |
| Quyết định trình bày cho ai, hay không trình bày | Soạn khung một trang nếu bạn cần |

#### Hands-on task
- **Bước 1 — Lắp prereg** (Phụ lục B); mỗi mục trỏ tới file nguồn.
- **Bước 2 — Bảng hash:** hypothesis cards, `prereg.json`, `regimes_cf.json`, `score.py`, commit engine, tag `contract-v1.3`.
- **Bước 3 — (Nếu bạn chọn) buổi đọc.** Đưa người đọc: contract v1.3, cards, realism envelope, thiết kế CF. Hỏi sáu câu:
  1. Có câu nào trong cards không thể sai không?
  2. Vùng đối chứng có thật sự có thể thất bại không?
  3. Envelope realism có dấu hiệu được "may đo" cho vùng tín hiệu không?
  4. Có lý do nào để nghi ngờ engine mà audit chưa kiểm?
  5. Câu chữ nào nói quá (ví dụ "fresh telemetry")?
  6. Nếu là reviewer, bạn hỏi gì đầu tiên?
- **Bước 4 — Sửa theo phản hồi trước commit cuối;** ghi diff.
- **Bước 5 — Điền bảng validity, điều kiện quy trình, outcome** (§17).
- **Bước 6 — Chọn nhãn Gate 3R** (§18); gắn đúng **một** claim.
- **Bước 7 — DL + gate note** (≤ 2 trang).
- **Bước 8 — Closeout** (template §21); hai mục đầu do bạn tự viết.
- **Bước 9 — Vá MASTER PLAN** theo Phụ lục D → v1.1.
- **Bước 10 — Tag annotated `phase-3R-closeout`** (không dùng `-f`).

#### Nếu có code
Không có code mới.

#### Verification
`git log` đúng thứ tự (§7); mọi hash khớp; record người đọc (nếu có); mọi claim trong gate note có link tới evidence.

#### Output
Prereg có hash, DL, gate note, closeout, MASTER PLAN v1.1, tag.

#### Interpretation
Nhãn Gate 3R nói Phase 4 được làm gì, với claim nào, trong miền nào.

#### What it does NOT prove
GO không có nghĩa hypothesis đúng. NARROW hay PIVOT không có nghĩa thất bại.

#### Beginner traps
- Chọn GO vì muốn "chạy cho xong".
- Để lịch quyết định thay gate.
- Sửa prereg sau khi đã commit mà không ghi diff.
- Trộn điều kiện quy trình vào bảng validity.

#### Self-check
1. Ba file nào phải có hash trước Phase 4, vì sao?
2. Vì sao review của AI không tính cho P0-V10?
3. Nếu người đọc chỉ ra một vùng đối chứng tầm thường, bạn làm gì trước khi commit?

#### Gate của lesson
*Thông tin trạng thái.* Nhãn đã ghi; closeout đã viết; trạng thái Phase 4 ghi tường minh.

---

## 16. Phase Gate (Gate 3R)

**Gate 3R (sang Phase 4 — confirmation)** đóng vai trò **Gate B** của MASTER PLAN: engine đã verify; hypothesis và phân tích đã đóng băng **trước** khi chạm dữ liệu xác nhận; khả năng phân biệt đã được lập luận; realism đã được sàng lọc.

**Không cần positive.** Gate 3R có thể kết thúc bằng "sau khi lọc identity, prior và realism, không còn claim nào đáng kiểm" — đó là một kết quả có căn cứ (§18), không phải thất bại.

| Kiểm | Lesson | Đạt khi |
|---|---|---|
| Discovery đóng băng | L3R.1 | Tag `explore-v13-pilot`; discovery record; errata tự đối chiếu raw; dòng exposure |
| Estimand hiểu và viết ra | L3R.2 | T07 do tác giả viết (hoặc author-attested); sanity list v1.3; golden toy |
| Engine | L3R.3 | Mọi test xanh; mọi mutant bị bắt; MC độc lập khớp; tái lập từ checkout sạch; (K*, dt*) và t_reg |
| Realism | L3R.4 | Envelope có nguồn, commit trước phân loại; quyết định (a)/(b)/(c) có DL |
| Contract | L3R.5 | Tag `contract-v1.3`; chuỗi nghiên cứu đã đi lại |
| Hypotheses | L3R.6 | Mỗi card qua 7 kiểm; forking-paths log |
| Thiết kế | L3R.7 | Frame, seed, strata, $n_s$; `regimes_cf.json` có hash; scorer phủ mọi nhánh; dry-run; đoạn "khả năng phân biệt" |
| Freeze | L3R.8 | Prereg có hash; `git log` đúng thứ tự §7 |

---

## 17. Validity vs Outcome

### 17.1 Validity — những điều phải đúng để Phase 3R đáng tin

| ID | Điều kiện | Kiểm bằng |
|---|---|---|
| V3R-1 | Discovery đóng băng: tag, exposure, errata tự đối chiếu với raw | Tag, register, script đếm lại |
| V3R-2 | Engine verified: golden toy, identity 1–5, posterior → prior, atom tại 0, zero-action và conservation bằng 0 chính xác, mutant bị bắt, tái lập sạch, MC độc lập khớp | Báo cáo audit |
| V3R-3 | Có chính sách số cho **mọi** regime (cặp kiểm, leo thang, "chưa phân giải") | Contract v1.3 |
| V3R-4 | Contract nhất quán: term vận hành, không term nào định nghĩa bằng outcome; identity list khớp T07; chuỗi nghiên cứu đã đi lại | Contract, DL |
| V3R-5 | Realism envelope: mỗi dải có nguồn/mục/mức đọc; commit trước phân loại; báo **mọi** bối cảnh đã chọn | Envelope, `git log` |
| V3R-6 | Hypothesis card qua 7 kiểm (có thể sai, không identity, hệ quả chung khai báo, lọc prior, vùng chỉ dùng tọa độ thiết kế, đối chứng có thể thất bại, có cơ chế) | Cards |
| V3R-7 | Thiết kế: rút ngẫu nhiên với seed khóa; **không outcome CF nào được tính**; strata có stakes theo tọa độ thiết kế; bảng power; control/anchor; scorer thuần và có test; dry-run đã chạy | Thiết kế CF, test |
| V3R-8 | Thứ tự commit đọc được từ `git log` (§7) | `git log` |
| V3R-9 | Exposure register cập nhật (pilot v1/v2, seed MC, danh sách CF chỉ tham số) | Register |
| V3R-10 | Mỗi artifact có đúng một nhãn provenance | Đầu mỗi file |

### 17.2 Điều kiện quy trình (do tác giả đặt) — báo riêng, không trộn vào validity

| Điều kiện | Nguồn | Ảnh hưởng | Trạng thái lúc Gate 3R |
|---|---|---|---|
| P0-V10 người đọc độc lập contract | Closeout Phase 1 | Mở thực thi Phase 4 | ⟨đạt / đổi bằng DL / còn mở⟩ |
| V9 heads-up GVHD | Closeout Phase 1 | Do bạn đặt | ⟨…⟩ |
| L8 người đọc prior boundary | DL-043 | Gate L tối đa "GO có điều kiện" | ⟨…⟩ |
| Closeout tự viết (Phase 1, 2, 3, 3R) | Luật ownership | Được nói "tôi bảo vệ được thiết kế" | ⟨…⟩ |
| MASTER PLAN X.3 #2 | Điều kiện GVHD 25/09 | Engine nằm ở `src/smr/` hay `experiments/` | ⟨…⟩ |

### 17.3 Outcome — những gì Phase 3R có thể cho thấy (không cần "positive")

| Outcome | Cho thấy gì | Vì sao vẫn có giá trị nếu "âm" |
|---|---|---|
| O1 Engine | Đúng, hoặc có bug (đã sửa, pilot v2) | Tìm bug **trước** confirmation là thành công lớn nhất của phase |
| O2 Realism | Vùng tín hiệu IN / EDGE / OUT theo bối cảnh | OUT tiết kiệm nhiều tháng làm việc trên một vùng không có thật |
| O3 Lọc identity/prior | Số claim còn lại (0–3) | 0 claim → PIVOT có căn cứ, không phải đoán |
| O4 Thiết kế | Có phân biệt được trong ngân sách không | Nếu không → NARROW scope trước khi tốn công chạy |
| O5 Tín hiệu sau audit | Giữ / đổi / mất | Tín hiệu mất sau khi sửa bug là kết quả hợp lệ |

**Không bao giờ** đặt "hypothesis phải đúng" hay "tín hiệu phải còn" làm điều kiện validity.

---

## 18. GO / HOLD / NARROW / REFORMULATE / PIVOT / DROP

| Nhãn | Điều kiện | Ví dụ trong Phase 3R | Hành động |
|---|---|---|---|
| **GO** | Mọi V3R đạt; ≥ 1 primary qua 7 kiểm; thiết kế phân biệt được trong ngân sách; vùng primary IN hoặc EDGE ở ≥ 1 bối cảnh | Hyp-MV và Hyp-SH qua; Ω+ IN ở bối cảnh edge/enterprise | Sang Phase 4 khi P0-V10 đạt (hoặc điều kiện được đổi bằng DL) |
| **HOLD** | Thiếu một artifact validity; outcome chưa được diễn giải | MC chưa chạy; contract chưa tag; scorer chưa phủ nhánh; audit tìm ra bug và đang chạy lại pilot v2 | Hoàn tất đúng điều kiện đó rồi đánh giá lại |
| **NARROW** | Chỉ một phần còn đứng | Chỉ còn một primary; realism IN chỉ ở một bối cảnh hoặc một phần vùng; vùng OUT ở mọi bối cảnh nhưng bạn chọn giữ claim ở mức "trong mô hình" (từ bỏ claim RQ3) | Thu hẹp claim và miền; ghi DL; Phase 4 chỉ kiểm phần còn lại |
| **REFORMULATE** | Estimand hoặc contract không khớp câu hỏi | Audit cho thấy S và M không tách được ở mức population; $\bar C_{\text{ref}}$ gần 0 ở vùng quan trọng nên % vô nghĩa; định nghĩa S1 hoặc stakes của pilot khác contract đến mức đổi ý nghĩa tín hiệu | Contract v1.3.x hoặc v1.4 + DL; đi lại chuỗi Problem → … → Contribution |
| **PIVOT** | Câu hỏi khoa học cần đổi contribution theo evidence | Sau khi sửa bug, tín hiệu biến mất; hoặc vùng tín hiệu OUT ở mọi bối cảnh và bạn không muốn claim mức mô hình → chuyển sang "trong vùng thực tế, M0 đủ tốt và state repair an toàn" (equivalence) | Viết lại claim boundary; tối đa một vòng discovery mới có giới hạn (reformulation budget, §22.2) |
| **DROP** | Chỉ khi có evidence chết người | Engine không verify được bằng bất kỳ phương pháp độc lập nào, kể cả sau khi sửa; một prior có cùng E, M, R (kill-K1) | Bỏ candidate claim; giữ negative result |

**Nhớ:** "không còn tín hiệu lớn" không phải lý do DROP. "M0 đủ tốt ở vùng thực tế" là một câu trả lời hợp lệ cho chữ "differ" của RQ. Thứ bị kill là **claim không có evidence**, không phải mọi kết quả trái kỳ vọng.

---

## 19. Beginner traps (cấp phase)

1. **Coi pilot là evidence** ("đã thấy 13% rồi mà").
2. **Tin con số vì nó lớn.** Số lớn cần kiểm *nhiều hơn*, không ít hơn.
3. **Kiểm engine bằng chính engine** (Monte Carlo chép logic từ code).
4. **Sửa bug rồi chỉ chạy lại các regime "đẹp".**
5. **Gọi S1 là "telemetry tươi".** S1 gồm cả mode — một quyền oracle.
6. **Báo complementarity trong vùng harm như một phát hiện.** Nó là hệ quả bắt buộc.
7. **Đổi ε_R sau khi thấy 13%.**
8. **"Motivated realism":** chọn bối cảnh sau khi biết vùng tín hiệu nằm đâu.
9. **Vẽ vùng ôm đỉnh discovery; jitter quanh X2065.**
10. **Vùng đối chứng tầm thường** (không có gì để quyết định nên chắc chắn đạt).
11. **Thử thêm chỉ báo** hoặc biến thể của chỉ báo M0.
12. **Tính outcome trên CF "chỉ để thử".**
13. **Merge branch exploration** như thiết kế cuối.
14. **Phình quy trình.** Phase 3R là phase *chuẩn bị*; một DL cho một quyết định thật; gate note ≤ 2 trang; time-box khoảng 6 tuần (ER1).

---

## 20. Phase-level self-check và learning outcomes

### 20.1 Self-check (trả lời không nhìn tài liệu)
1. Ba lời giải thích cạnh tranh cho một con số pilot lớn là gì, và lesson nào xử lý từng cái?
2. Vì sao "80/216" không phải prevalence?
3. Viết định nghĩa $\bar L_{sm}$. Vì sao $\bar L_{10}$ và $\bar L_{11}$ không phụ thuộc τ?
4. Contrast nào có thể âm? Chứng minh $\bar G_S<0\Rightarrow\bar\Gamma>0$.
5. Monte Carlo của audit kiểm gì, và **không** kiểm gì?
6. Vì sao "capacity = 10" không phải vấn đề realism, còn "nhảy giữa 140% và 20% capacity mỗi 0,1 s" thì có thể là?
7. Vì sao giữ ε_R = 1% dù effect pilot tới 13%?
8. Vì sao Hyp-MV dùng $\bar G_M$ mà không dùng $\bar G_{M\mid S_1}$?
9. Với n = 30, cần bao nhiêu regime đạt để cận dưới 97,5% của tỉ lệ vượt 0,5?
10. Nếu Phase 4 FALSIFY cả hai primary, bạn được làm gì và không được làm gì?

Không trả lời được câu nào thì quay lại lesson tương ứng trước khi đóng phase.

### 20.2 Sau Phase 3R tôi phải tự giải thích được
- Vì sao pilot là discovery chứ không phải evidence, và tần suất trong pilot không phải prevalence.
- Estimand population bằng lời mình; vì sao nó trơn hơn estimand một-snapshot và gần chữ "expected" của RQ hơn.
- State repair (backlog + mode) khác "telemetry tươi" ở đâu.
- Vì sao sửa state có thể làm tệ hơn khi dùng M0 (compensating errors), và vì sao điều đó đã có trong prior.
- Contrast nào là identity; vì sao complementarity trong vùng harm là bắt buộc.
- Verification khác validation; vì sao phép kiểm độc lập phải được viết từ đặc tả.
- Realism nằm ở **tỉ số**, không ở đơn vị; vì sao cùng một regime có thể thực tế ở bối cảnh này mà không ở bối cảnh kia.
- Vì sao ngưỡng phải có trước dữ liệu.
- Một prediction theo vùng gồm những phần nào; một vùng đối chứng tốt trông thế nào.
- PASS / WEAKEN / FALSIFY / INCONCLUSIVE nghĩa là gì; vì sao "chưa phân giải số" không phải FALSIFY.
- Vì sao thực thi Phase 4 chưa mở cho tới khi Gate 3R có nhãn (và P0-V10, theo luật bạn tự đặt).

---

## 21. Phase closeout template

```markdown
# Phase 3R Closeout

> Ngày · Người phụ trách · Contract v1.3 · Tag `phase-3R-closeout`
> Provenance: ai viết phần nào (tác giả viết / author-attested / AI soạn, tác giả duyệt / AI theo ủy quyền)

## What I understood
⟨Tác giả tự viết: 5–10 câu, không nhìn tài liệu. Không ủy quyền được.⟩

## What changed in my mental model
⟨Tác giả tự viết: trước Phase 3R tôi nghĩ… ; bây giờ tôi nghĩ… ; vì evidence…⟩

## Decisions made
| DL | Quyết định | Evidence |
|---|---|---|

## Evidence created
⟨Verification engine population (tầng E1 verification, trong mô hình đã khai báo); realism screen
(mức thiết kế + nguồn); không có evidence khoa học mới nào về các hypothesis.⟩

## Assumptions still open
⟨AS1–AS14; cờ realism (buffer vô hạn, action ngay, quyền oracle về mode); S0 là posterior Bayes chính xác;
c_sw = 0; quá trình trước quyết định dừng; D13 không tính chi phí sau h.⟩

## Risks still open
| Risk | Lộ ra ở |
|---|---|

## What I am allowed to claim
⟨"Engine population tính đúng estimand v1.3 trong phạm vi các kiểm …";
"pilot cho tín hiệu discovery … ở các vùng …, phân loại realism … ở bối cảnh …";
"các prediction sau đã được đóng băng trước dữ liệu: … (hash …)".⟩

## What I am NOT allowed to claim
⟨Bất kỳ hypothesis nào đúng; tần suất trong mạng thật; "fresh telemetry có hại"; complementarity như phát hiện riêng;
robustness với switching cost; novelty; G2; khuyến nghị vận hành; "tác giả dự đoán" cho phần do AI soạn.⟩

## Gate decision
| Validity (V3R-1…V3R-10) | Trạng thái |
|---|---|

| Điều kiện quy trình (P0-V10, V9, L8, closeout tự viết, X.3 #2) | Trạng thái |
|---|---|

**Nhãn:** GO / HOLD / NARROW / REFORMULATE / PIVOT / DROP · **Claim gắn với nhãn:** … · **Trạng thái P0-V10:** …

## Next phase
⟨Phase 4 bắt đầu bằng …, với điều kiện …; hoặc việc phải làm nếu HOLD / NARROW / REFORMULATE / PIVOT.⟩
```

---

## 22. What comes next — roadmap sau Phase 3R

Theo progressive elaboration (MASTER PLAN XIX.5): Phase 4 được mô tả ở mức vừa vì nó là bước kế tiếp; Phase 5–9 chỉ ở mức mục tiêu và gate. Mỗi phase có file `notes/phases/PHASE_X.md` riêng khi tới.

### 22.1 Bản đồ phase mới so với MASTER PLAN v1.0

| MASTER PLAN v1.0 | Roadmap v1.3 | Ghi chú |
|---|---|---|
| Phase 3 — analytical pre-spike (Gate A) | Phase 3 (đã đóng: REFORMULATE) + **Phase 3R** (Gate 3R ≈ Gate B) | Gate A đã có nhãn |
| Phase 4 — controlled core (Monte Carlo + discovery + baseline) | Phần lớn đã làm bằng pilot exact. Monte Carlo chuyển thành **verification** ở L3R.3. Baseline vận hành chuyển sang Phase 7 | Không còn là một phase riêng |
| Phase 5 — confirmation (RQ1), Gate C | **Phase 4 — confirmation v1.3**, Gate C | Chạy đúng một lần |
| Phase 6 — mechanism (RQ2), Gate D | **Phase 5 — mechanism**, Gate D | Intervention + null discrimination |
| Phase 7 — independent validation, Gate E | **Phase 6 — independent validation**, Gate E | Chọn theo assumption rủi ro nhất |
| Phase 8 — practical relevance (RQ3), Gate F | **Phase 7 — practical relevance**, Gate F | Feasible repair, chi phí, timing |
| Phase 9 — synthesis, Gate G | **Phase 8 — synthesis + final novelty audit**, Gate G | — |
| Phase 10 — paper | **Phase 9 — paper** | — |

### 22.2 Phase 4 — Confirmation v1.3 (mức vừa)

- **Câu hỏi.** Các prediction đã đóng băng (Hyp-MV, Hyp-SH, Hyp-MI) có đứng trên các regime CF chưa từng thấy không?
- **Input từ Phase 3R.** Engine (commit), contract v1.3, hypothesis cards, `prereg.json`, `regimes_cf.json`, scorer.
- **Các bước.**
  1. Kiểm điều kiện: hash khớp; engine commit đúng; P0-V10 theo luật bạn đặt.
  2. Chạy **control và anchor trước**. Sai → dừng, sửa, ghi deviation, rồi chạy lại toàn bộ với cùng phân tích.
  3. Chạy mọi regime CF ở (K*, dt*) + mức kiểm; leo thang theo luật.
  4. Scorer chấm tự động.
  5. Báo cáo theo bốn nhãn Fact / Claim / Evidence / Inference; độ lớn mô tả; diagnostic ($\bar F/\bar V$, P(flip), $\bar\Gamma$, $\bar G_{M\mid S_1}$); câu bối cảnh realism bắt buộc.
  6. Exposure: tập CF trở thành dữ liệu đã thấy.
  7. Gate C.
- **Gate C.** PASS ở ≥ 1 primary và realism IN → **ứng viên** G2 (MASTER PLAN I.5 còn yêu cầu kiểm timescale/cost sơ bộ). Mọi nhãn ghi DL.
- **Nếu kết quả không như mong đợi:**

  | Kết quả | Nhãn gợi ý | Hướng |
  |---|---|---|
  | Hyp-MV FAIL, Hyp-SH PASS | NARROW | "Dùng sai thông tin dưới mean model" ở vùng đã kiểm; nhớ ranh giới K-RM: chỉ mới ở điều kiện và độ lớn |
  | Hyp-SH FAIL, Hyp-MV PASS | NARROW | "Điều kiện để mean model không đủ cho quyết định" |
  | Hyp-MI FAIL | — | Bỏ chỉ báo; primary không bị ảnh hưởng |
  | Cả hai primary FAIL | NARROW hoặc PIVOT | Câu chuyện âm hoặc equivalence |
  | INCONCLUSIVE | HOLD | Sửa validity, chạy lại **cùng** phân tích (deviation log) |
- **Reformulation budget.** Sau Phase 4, tối đa **một** vòng discovery → confirmation nữa, và chỉ khi phân tích thất bại chỉ ra một lý do cụ thể, phát biểu được trước. Nếu không → viết kết quả âm hoặc equivalence. Ghi DL. Đây là cách cụ thể hóa câu "không reformulate vô hạn để tìm positive result".
- **Ước lượng.** Khoảng 1–2 tuần, phụ thuộc t_reg × số regime.

### 22.3 Phase 5 — Mechanism (RQ2)

- **Câu hỏi.** Vì sao pattern xảy ra? Cơ chế ứng viên có dự báo đúng hướng khi chủ động thay **một** nhân tố không?
- **Nội dung.** Can thiệp ghép cặp một nhân tố (headroom của B, κ, h, η, $c_{\text{sw}}$ — đây là nơi kiểm switching cost một cách có kiểm soát). Knockout (ví dụ: bỏ biến động của A; thay luật ON/OFF bằng một luật mượt hơn có cùng trung bình). Robustness của estimator (S0 lọc bằng M0 — kiểm bẫy "estimator–model coupling"). RQ2: threshold null (dùng $I_{M_0}$ như một predictor hình học) so với một predictor động học, trên regime held-out, cùng quyền thông tin và cùng ngân sách fit.
- **Gate D.** Chỉ claim mechanism khi có null discrimination held-out **và** knockout đúng dự đoán.

### 22.4 Phase 6 — Independent validation

- **Chọn theo assumption rủi ro nhất** mà realism screen đã gắn cờ: finite buffer + drop (nếu P(delay > buffer) đáng kể ở vùng tín hiệu); packet-level DES với arrival Poisson trong mỗi mode (phá bất biến thang của plant fluid); actuation delay; luật traffic khác (nhiều mức, đuôi nặng); shared bottleneck chỉ khi claim cần.
- **Thành công** = prediction định tính đã đóng băng còn đứng (hướng, vùng), không phải khớp từng con số.
- **Gate E** (→ ứng viên G4).

### 22.5 Phase 7 — Practical relevance (RQ3)

- Feasible state repair (refresh có delay $d$ và chi phí telemetry; chỉ phần backlog $\bar F$, không có quyền oracle về mode); feasible model repair (model burst-aware hiệu chỉnh từ dữ liệu hữu hạn); baseline mạnh (age-aware, hysteresis); realism envelope v2 dùng dữ liệu đo (trace công khai, AoI trên testbed); emulation chỉ khi một claim về timing cần nó.
- **Gate F.** Claim vận hành chỉ khi net gain vượt ε_R sau chi phí.

### 22.6 Phase 8 — Synthesis và Phase 9 — Paper

- **Phase 8:** claim–evidence matrix (MASTER PLAN A.10); threats to validity; final novelty audit; người đọc độc lập; **Gate G**.
- **Phase 9:** viết theo loại contribution mà evidence hỗ trợ (MASTER PLAN I.7, XVII).

### 22.7 Kill criteria bổ sung

| # | Trigger | Dừng điều gì | Hành động hợp lý | Phát hiện ở |
|---|---|---|---|---|
| K12 | Vùng hypothesis OUT ở mọi bối cảnh realism đã chọn | Claim vận hành; mọi câu "trong mạng thực" | NARROW thành kết quả mức mô hình, hoặc PIVOT sang equivalence trong vùng thực tế | 3R, 7 |
| K13 | Engine không verify được bằng phương pháp độc lập, kể cả sau khi sửa | Mọi claim định lượng dựa trên engine | HOLD; nếu không khắc phục được → DROP estimand đó | 3R |
| K14 | Mọi effect còn lại chỉ là identity, hoặc trùng K-RM/EVMI ở cả ba trục E, M, R | Novelty claim | NARROW về characterization có điều kiện, hoặc dừng | 3R, 8 |

### 22.8 Bước tiếp theo có giá trị nhất ngay bây giờ

- **Mục tiêu hiện tại:** biết pilot có được tính đúng không, trước khi xây bất cứ thứ gì lên nó.
- **Nút thắt lớn nhất:** trong các tài liệu tôi được xem, chưa có bản đối chiếu nào giữa code engine population và định nghĩa (T07 / contract v1.2).
- **Bước nhỏ nhất có ích:** gắn tag `explore-v13-pilot` (khoảng 10 phút), rồi trả lời 11 câu hỏi (a)–(k) của L3R.3 Bước 1 bằng cách đọc code engine và trích file:dòng. Không cần chạy gì mới; mỗi câu trả lời "khác định nghĩa" cho bạn biết ngay pilot có thể sai ở đâu. Song song, ở track học: L3R.2 Part A — chứng minh $\bar G_S<0\Rightarrow\bar\Gamma>0$ trên giấy.

---

## Phụ lục A — Khung contract v1.3

```markdown
# Definitions v1.3 (contract) — LOCKED <ngày> · tag contract-v1.3
> Provenance: …

## 0. Main RQ (nguyên văn) + một câu "đọc theo population"
## 1. Thay đổi so với v1.2 (bảng diff)
## 2. Plant (kế thừa D-terms; cờ realism từ L3R.4)
## 3. Regime (tọa độ không thứ nguyên, dải, mốc thời gian)
## 4. Observation và p(y) (atom tại 0; quadrature K*)
## 5. State pipelines: S0 (Bayes, luật thật) · S1 (gồm mode) · pipeline D22
## 6. Models: M0 (D10) · M1 (D21)
## 7. Estimand: L̄_sm, sáu contrast; danh sách identity (từ T07)
## 8. Chuẩn hóa: C̄ref = L̄11 (primary) · stakes σ̄ (secondary, định nghĩa tường minh)
## 9. Outcomes: primary / secondary / diagnostic
## 10. SESOI: ε_R, ε_E, tập độ nhạy
## 11. Numerics: (K*, dt*), cặp kiểm từng regime, dung sai 0,25 pp, leo thang, "chưa phân giải"
## 12. Information rights
## 13. Scope / out-of-scope
## 14. Assumptions AS1–AS14 (nếu sai thì sao · kiểm ở phase nào)
## 15. Exposure và các tập niêm phong
## 16. Stop rules
## 17. Mục DEFERRED (nếu có) + lesson sẽ quyết
```

Mẫu cho mỗi term (giữ MASTER PLAN A.4): định nghĩa vận hành · đo bằng gì / tính thế nào · đơn vị · ai biết · khi nào biết · không nhầm với · trạng thái (LOCKED / DEFERRED, DL-xxx).

## Phụ lục B — Khung prereg confirmation v1.3

```text
ID: CF-v1.3 · ngày · contract-v1.3 · commit engine · provenance
Câu hỏi nghiên cứu (một câu)
Hypotheses: Hyp-MV, Hyp-SH (primary) · Hyp-MI (secondary) — trỏ tới cards (hash)
Identity và hệ quả chung đã khai báo (không chấm)
Frame; strata; phân phối rút (đều / log-đều); seed; n_s; lý do chọn n (bảng power)
Danh sách regime: regimes_cf.json (hash) · khoảng cách nhỏ nhất tới discovery · phân tích độ nhạy mô tả
Control và anchor: danh sách + kết quả bắt buộc
Numerics: (K*, dt*); cặp kiểm; dung sai 0,25 pp; leo thang; u_max
Luật chấm: tiêu chí theo regime; tiêu chí gộp; α (Bonferroni);
  PASS / WEAKEN / FALSIFY / INCONCLUSIVE cho từng hypothesis
Xử lý "chưa phân giải số" + phân tích độ nhạy
Diagnostic sẽ báo (không chấm)
Realism: bối cảnh + câu bối cảnh bắt buộc trong báo cáo
Chính sách deviation
Exposure: những gì đã thấy khi viết file này
Hash: cards · prereg.json · regimes_cf.json · score.py · commit engine
```

## Phụ lục C — Worksheet realism

| Đại lượng | Bối cảnh | Dải | Nguồn (tác giả, năm, venue) | Mục / bảng | Mức đọc (full / targeted / abstract-only) | Độ tin cậy | Ghi chú |
|---|---|---|---|---|---|---|---|
| Tuổi telemetry τ | | | | | | | |
| Thang thời gian biến động traffic | | | | | | | |
| CV theo cửa sổ 10 ms / 100 ms / 1 s | | | | | | | |
| Mức dùng link (trung bình, đỉnh) | | | | | | | |
| Buffer tính theo thời gian | | | | | | | |
| Độ trễ actuation δ_act | | | | | | | |
| Thời gian giữ quyết định h | | | | | | | |

```text
Luật phân loại (commit TRƯỚC khi phân loại):
IN   = …
EDGE = …
OUT  = …
Commit: <hash>
```

## Phụ lục D — Patch đề xuất cho MASTER PLAN (→ v1.1)

- **§0:** Phase hiện tại = Phase 3R; lesson hiện tại; blocker = audit engine + realism; next step = §22.8.
- **Part I.1:** thêm "Thế hệ 3b (26–28/10/2026): Phase 3 đóng với REFORMULATE → Step 1 (P(a) PASS, P(b) và P(c) FAIL) → population pilot (discovery, chưa merge)".
- **Part I.5:** G-level giữ G1; ghi "pilot không nâng G-level".
- **Part IV:** thay bảng phase theo §22.1.
- **Part VI:** chèn Phase 3R (trỏ tới file này); Phase 4 = confirmation v1.3; đánh số lại Phase 5–9.
- **Part XIII:** Gate 3R ≈ Gate B; Gate C sau Phase 4; D, E, F, G dịch theo §22.1.
- **Part XV:** thêm K12–K14.
- **Phụ lục C (changelog):** dòng v1.1.

---

## Changelog của file này

| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| v1.0 | 28/10/2026 | Bản đầu. Dựng từ POST_PHASE3_CONTEXT, PHASE_3 v2.0, MASTER PLAN v1.0 và Final Review. So với đề xuất Phase 3R trong POST_PHASE3_CONTEXT: thêm audit engine (L3R.3) và realism screen (L3R.4); lọc identity (complementarity trong vùng harm; "penalty biến mất dưới M1"); Hyp-MV dùng $\bar G_M$; tách "state repair" khỏi "telemetry tươi"; giữ ε_R; rút mẫu ngẫu nhiên với seed khóa trước; chính sách số cho mọi regime; reformulation budget; roadmap Phase 4–9; patch MASTER PLAN |

