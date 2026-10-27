# Hướng dẫn làm việc trong repo

Người phụ trách mặc định: **Doan Van Tai**. Báo cáo bằng tiếng Việt; giữ nguyên
attribution đã tồn tại. Không thay RQ, contract, giả định hoặc tiêu chí thí nghiệm
chỉ vì một nguồn literature hay hướng dẫn của AI đề xuất.

## Mỗi lần tìm, lấy, đọc, kiểm tra hoặc trích paper

1. Đọc [quy tắc và checklist](notes/literature/search_protocol.md) trước khi
   thao tác; áp dụng cả khi chỉ tra một bài đã biết tên/DOI.
2. Kiểm thư viện và log hiện có trước; ưu tiên NDT/networking. Viết câu hỏi,
   PC liên quan và lý do nguồn có thể ảnh hưởng claim. Không mở rộng ngoài ngành
   chỉ vì trùng thuật ngữ.
3. Phân biệt `lookup`, `keyword`, `backward`, `forward`, `author/venue` trong
   [search log](notes/literature/search_log.md). Chỉ ghi thao tác và số đếm thật;
   lookup không phải bằng chứng đã khảo sát lĩnh vực.
4. Mỗi đợt AI đề xuất tối đa 3 nguồn mới, có lý do giữ và PC liên quan. Chờ tác giả
   duyệt trước khi tải PDF hoặc tạo note nội dung mới. Yêu cầu trực tiếp tải/đọc
   một nguồn cụ thể đã là ủy quyền; không hỏi lại. Tra metadata, sàng ứng viên và
   ghi log được làm trước bước duyệt.
5. Kiểm DOI/arXiv/URL ở nguồn chính thức, phiên bản và trạng thái xuất bản.
   PDF lưu ngoài Git tại `~/papers/state-model-regret/`; không dùng thư viện lậu,
   không tự gửi email xin bài.
6. Ghi riêng mức đọc AI và tác giả; trích đúng §/trang/phương trình cho claim
   nội dung. Thiếu bằng chứng thì ghi chưa xác nhận. Không tự kết luận novelty
   hoặc đổi nhãn PC/Gate từ một kết quả tìm kiếm.
7. Cuối phiên ghi query, công cụ, bộ lọc, số thực sàng, số giữ không trùng, lý do,
   lỗi/hạn chế và lý do dừng; báo trực tiếp kết quả cùng đường dẫn đã lưu.

Nhắc nhanh: **Hỏi → Tìm → Kiểm → Duyệt → Đọc → Ghi → Dừng**.

## Thư viện sau dọn ngày 24/10/2026

Bảng hiện dùng: `papers/paper_comparison.xlsx`; dữ liệu: `papers/data/catalog.json`.
`papers/archive/` là snapshot lịch sử; không tự đưa 21 bài hoặc 4 nhóm đọc cũ
trở lại danh sách bắt buộc. Lưu tạm không đồng nghĩa nguồn đã bị bác bỏ.
Note/proof Part A và kết quả thí nghiệm vẫn là evidence, phải giữ nguyên.

Cập nhật25/10/2026: NDT1/P05/P10 được tác giả yêu cầu trong L2.4 và nằm đầu
catalog; R32/R34/R51 là tham khảo cũ. NMRG/P08/S07 ở landscape để tra bổ sung.
Ba đề xuất snowball chưa duyệt chỉ ở log, không tự tải hoặc thêm vào danh sách.

Cập nhật26/10/2026: L2.5 Part1/Part2 đã hoàn tất kỹ thuật, P04 khác R04;
toy admission/bốn server/V1 không phải replication paper hoặc lưới v1.2.
L2.6 Part A có S11 ở đầu Excel, journal identity TIT2026 đã kiểm nhưng bản đọc
là arxivv3. K3/heuristic H1 chỉ là AI-assisted evidence/queue, không khóa H1.
L2.6 Part B/P13 nay có artifact kỹ thuật, journal CWI36trang; Eq2.7 định nghĩa
ΩT, Prop4–5/tr282 và terminal discussion §6/tr289 khác arxivv1 numbering.
T-H1: D13 đã chứa dt·qH, chỉ không có terminal surcharge/cost sau h; không đổi
metric. H1-Q02 và Q-L27-01 chỉ là queue, tác giả L-self/Gate/A4/L2.9 còn mở;
không tự đổi nhãn PC, khóa H1 hoặc chạy Phase3.

Cập nhật L2.7 PartA,26/10/2026: P03=R51 dùng chung một record, P03/P07 AI-T;
P02 mới official abstract AI-A, full text timeout/403/OA fallback thất bại.
Không ghi P02 đã T hoặc L2.7 PartA hoàn tất toàn bộ. Excel12nguồn;10tiến độ
tác giả và9notes khác giữ nguyên, R51 AI note nâng mức có snapshot. K-M1…5/
MT1…8 chỉ evidence/queue; K-M5 và MT2/6/7 còn primary P02 dependency. Không gán
dấu Γ cho P02/P04 hoặc nhận factorial/decision regret là mới. MT5 chờ A05,
PartB/P12/OεRE/L-self/Gate/A4/L2.8–2.9 còn mở; không tự chọn null hoặc chạy Phase3.

Cập nhật L2.7 PartB,26/10/2026: P12 primary NeurIPS AI-T; R43 lượt này AI-A,
archived AI-T24/10 có provenance riêng. OεRE đã có trong terms dưới dạng draft,
không contract-adopted; numeric/CI label helpers chỉ teaching/reporting proposal.
K5/S0 forecast giữ nguyên; rule κ≥2/q90/q90/h8 chỉ candidate L3.3, chưa chọn;
held-out chỉ đọc tọa độ/design labels, không outcomes/p_sw/λA. Excel13nguồn,
chỉ thêm P12, giữ12notes/progress cũ. PartB technical PASS không đóng toàn L2.7:
P02 PartA vẫn full-text BLOCKED, L-self/Understanding/Gate/A4/A05/L2.8–2.9 còn mở.

L2.8 Part1/26/10:4session cards, A4 bounded rerun có20+15GoogleScholar records,
20forwardR02 (same first page gọi2lần, chỉ đếm20). R01/R02/R04 official
abstracts AI-A lượt này; R01/R04 archiveAI-T giữ riêng.3Tier2proposals chỉ ởlog,
chờ duyệt PDF/note; Excel13nguồn/PC/contract giữ nguyên. A1–A3/primaryPart2/
L2.9 và affected prior-clearance judgment HOLD; chưa đạt2×20 hoặc fullL2.8 PASS.

L2.8 Part2/26/10: R01/R02/R04 current primary AI-T; R02 CiteSeerX PDF lấy được
sau VPN retry, publisher vẫn403; R04 SC+Π-accuracy⇒SI, chỉ one-shot diagnostic,
chưa khóa H1. K-RM1/2/3 tránh đè K-S9/10 freshness. NDT26/WM26/AIS22 tác giả
“Duyệt cả3”, targetedAI-T; WM26 cóP/C/S/E2×2repair và true-future oracles,
không nhận generic2×2/harm/fidelity≠decision quality là mới. Excel19, giữ13notes/
progress cũ. A1 44/A2 45/A3 60/A4repeat20screen events; raw rank payload trước
resume không lưu được, chỉcheckpoint ledger, không full search reproducibility.
A3q1Scholar vẫntimeout/S11S2citations429 cảretry; fallbacks ghi riêng, không
saturation. PC3formalL2.9/PC4A05/H1/null/L-self/Gate vẫn HOLD, không Phase3.

L2.8 follow-up/26/10: P02 có VoR tác giả tải (CC BY, ngoài Git) → AI-T §1–5/Bảng2;
bias OAT theo đại lượng, sweep1-D horizon/update, không joint bias; MT2/6/7,K-M4/5 có
addendum, không gán Γ. Phiên tìm mới lưu raw HTTP+sha256: 157 record, 0Tier1/4T2,
2×20 chưa đạt; P07 forward không chạy được. 6 đề xuất cũ+R06 sàng abstract; 3 đề xuất
mới (2609.06351, 10.1145/3769700.3771695, 2608.01725) chờ duyệt. Excel19 giữ progress;
audit L2.8Part2 cũ FAIL có chủ đích ở assert P02 row. Không L2.9/Gate/L-self/Phase3.

L2.9 Part1/26/10: prior_boundary có hồ sơ 8 cột PC1–PC6/MainRQ, **cột nhãn để trống
cho tác giả**; Gate L=HOLD. author_reading_record.md là mẫu L-self chưa điền: AI chỉ chép
nguyên văn xác nhận của tác giả (cơ chế DL-032), không suy từ "Duyệt"/tải PDF/note AI.
Nhãn tạm của mentor lưu riêng results/lessons/l2_9/part1/reviewer_view_AI_open_after_grading.md,
không đưa vào dossier/DL. WM26 đọc lại AI-T: không thấy nhánh chỉ thông tin hiện tại.
Không DL Gate L, không related work/closeout (Part2), không Phase3.

L2.9 Part2/26/10 (AI theo ủy quyền "đóng vai tác giả"): nhãn tạm MainRQ KEEP; PC1 DROP,
PC2/5/6 NARROW, PC3 KEEP câu chữ/framing NARROW, PC4 HOLD; DL-042 Gate L **HOLD**
(L2 0/19, L3 AI, L8 ❌); related_work_skeleton, claim boundary Phase2, EV-37…45,
exposure Phase2, PHASE_2_closeout (2 mục tác giả vẫn trống, **chưa tag**). Không ghi
AI-work là tác giả làm; L-self/T03 kín sách/L8 chỉ tác giả/người thật tạo được.
Không commit L3.3 trước nhãn do tác giả xác nhận + L-self WM26; không Phase3 runs.

WM26/26/10: tác giả gửi bản giải thích AI đã đọc → ghi **L-2nd author-attested**, không
L-self (chưa tự mở §4.1/§5/F.1 và tự viết). PDF Downloads trùng sha94201c59 thư viện.
AI kiểm bản giải thích khớp PDF; đính chính record AI cũ: "diagnostic tools" là WM26 **§8**
PDF9 (không §9). Excel "Mức tôi đã đọc" giữ nguyên; Gate L vẫn HOLD.

Đợt duyệt/26/10: tác giả duyệt và tải 9 PDF; IA26/DTS25/CEN26/CEH23 đọc targeted (AI-T,
DTS25 AI-F), Excel23, author levels vẫn "Chưa có xác nhận". Nhãn tạm không đổi; H1-Q04 thêm
vào queue. Tác giả yêu cầu không ghi AI: repo vẫn ghi mức đọc thật (AI-T ≠ L-self) vì Gate L
dựa vào cột đó; L-self chỉ ghi khi tác giả tự đọc và nhắn lời mình.

Bản chính thức/26/10 tối: S11 journal khớp số mục; R01 eCommons = TR2006 (cần Springer
10.1007/s10479-009-0603-7); R34 nhận bản CDC1992 2tr (cần TAC 10.1109/9.402238). Có
author_reading_pack + T03_worked_example (EVPPI 1/9, E[VSS] 2/9) để tác giả tự làm; tác giả
yêu cầu AI đóng vai tự đọc/tự dẫn/tự chấm — không ghi được thành L-self/L3; nhãn tạm giữ.

Gate L/26/10 (DL-043): **GO có điều kiện**, tag phase-2-closeout. Tác giả author-attested
(ngoài vở, DL-032) đã tự đọc WM26/R02/R04/P11/P02/S11/P12, tự dẫn T03, xác nhận nhãn; Excel 6
nguồn = "Mục liên quan". Còn: L8 người đọc thật; hai mục đầu closeout. Phase 3 mở: L3.3 commit
trước A01; A05 khóa trước held-out; memo GVHD trước A04; HOLD Phase4 tới P0-V10.

L3.1 Part3/27/10 (DL-044): có PHASE_3 (bản triển khai từ lesson, không phải plan v2.0
đầy đủ), current pointers/index và progress log. V9 giữ điều kiện(c): chưa gửi, A04 chờ;
P0-V10 đọc v1.2/brief/claims hiện hành, L8 OPEN; hai nghĩa V9 tách riêng. Tự viết vẫn OPEN.
cells.py rebuild4hàm từ experiments, nguồn giữ byte;38main constructors và24D comparisons
khớp,228testsPASS. Chỉ kiểm D, không engineL3.2/outcomes/held-outD; L3.3 chưa khóa.
Không nhận Understanding/ownership PASS hoặc người đọc đã xem; HOLD Phase4 giữ nguyên.

L3.2 Parts1–4/27/10 (DL-045–046): engine mới ở experiments/A00_engine, KHÔNG src
vì T05 tác giả/attestation chưa có. 72tests mới/300full PASS,11/11mutant KILLED;
canonical/E2/E5/E7/L1.5/L1.8B tái lập; bounds tách oracle/M0/D22 và impact.
E3/E6 là arrival-law toys, không D7 H=1 known-mode; pseudocode idle/guard đã sửa.
Adapter58metadata,32D-only comparisons8IDs×A/B×ref1/2 khớp,không heldoutD/gridoutcomes.
Src/kernel/contract/PC/threshold giữ; EVPI_w/flip2D để sau; L3.3 chưa commit,
T05/ownership/P0-V10/L8 OPEN, V9 chưa gửi/A04 chờ, Phase4 HOLD.

L3.3/A03/27/10 (DL-047–049): tác giả chọn K5 cả danh sách+luậtκ≥2/q90/q90/h8,
attest tự hoàn thành already_implied kín sách + engine/T05 read-back ngoài repo (nguyên văn lưu).
Card notes/phases/PHASE_3_prediction_card.md có14sanity/4forecast không cơ chế/1luật K5;
giữ byte claims.md; P1sanity/P4A05-F, optionalP2/P3rules chưaadopt, P6không OOS.
324fulltests/29card+guard PASS,11/11mutant KILLED,4000ledger0vi phạm/0mismatch.
Signed ratio dùng4corners, Cref0excluded,dt/HOLDunknown,Kleene từngvế. Guard kiểm card+
lockSHA/2commit/tag,không cho DRAFT; card fullSHA thay đổi thì dừng, không amend/force.
K5carry mọi rule chưa refute kể cả unknown, nguyênvăn sangA05-F,m=1; H1/null/split chưa khóa.
Không grid outcomes/Dmới (regressionD-only/screenM31cũ ghi riêng),không A01/A04/A05/src promotion.
T05chưa văn bản tác giả; P0-V10/L8/V9 và Phase4HOLD giữ; không nhận author-owned mechanism/novelty.

L3.4/A01,27/10: prereg81233ef trước outcomes; cardA03 byte nguyên. Run01 C5N01 FAIL
(modeltie−1.35525e−20), sửa always-empty/mean-no-idle certificates, không epsilon.
Run02 controlsPASS, interruptedref8 vì O(n²)conversion; hoist và6independent processes.
Run03 code60a1032 PASS: p_sw9/9bitwise, C1–C6 PASS (60C5zero+6WDzero),15/15BOUNDED,
12/12pairsPASS; **DL-053 dt cuối1/240s/ref2**, cả3calibrationpick2 sau đủref1–16.
336tests/11mutantsPASS; CSVreplay2; giữ failed/partial artifacts. Calibration mọi mức
đã exposed, không chấm card/H1/null hoặc D/outcomes held-out mới. A04 vẫn chờV9
chưa gửi; A04 cần kiểmpair1/120→1/240 từng ô. T05author-writing/L8/P0-V10/Phase4
không tự đóng. Report results/lessons/l3_4/report.md, data results/A01/20261027_03/.

DL-054/27-10: tác giả yêu cầu bỏ chặn để triển khaiL3.5. **P1-V9=WAIVED_BY_AUTHOR**,
miễn điều kiện gửi memo trướcA04; supersede điều kiện(c) DL-044 cho bước tiếp.
Memo chưa gửi, không GVHD_APPROVED/human review; giữ nguồn mock review nguyên byte
ở notes/reviews/2026-10-27_pre_A04/. Không đổi attribution thành GVHD thật.
Rủi ro tính lại/redesign sau outcome được ghi DL-054, không sửa card/thước cũ.
A04 chưa chạy; còn prereg/exposure/runner/toy checks, dt1/240+pair1/120→1/240.
Gate record notes/phases/A04_execution_gate.json, notes/lessons/L3.5_preflight.md.
A05-F/held-out,L8/P0-V10,T05author-writing/Phase4HOLD giữ. Review nhìn remotef72306f
nên324tests/20ktoy chỉ reviewer-reported; localA01 guards/51hash kiểm lại.
Ref4/FV/flipmass/cheapkill proposals chưa tựadopt; không áp kill cho identityT01.
