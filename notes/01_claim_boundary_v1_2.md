# Claim boundary v1.2

Người phụ trách: **Doan Van Tai** · 23/10/2026. Bổ sung cho [boundary v0](01_claim_boundary_v0.md) và thay [bản nháp v1.1](01_claim_boundary_v1_1_draft.md). Đi cùng [contract v1.2](01_definitions_v1_2.md) và [lưới v1.2](design/grid_v1_2.md).

> **Provenance.** Do AI soạn theo yêu cầu thực hiện của tác giả; tác giả chưa tự viết lại (PHASE_1 §5.4, luật 5).

## Được claim (có điều kiện, trong mô hình lý tưởng đã khai báo)

| Claim | Bằng chứng |
|---|---|
| Trong plant của contract, hai action chỉ khác cost qua capacity bỏ phí; vùng bảo toàn cho mọi contrast bằng 0 (E0, đã biết) | L1.2, ĐK1, ô N03/N04/P01 |
| Với một observation mỗi ô và belief đúng: $G_M=\lvert E\Delta\rvert\cdot\mathbf 1[a_{00}\ne a_{01}]$, $G_{S\mid M_1}=\min(E\Delta^+,E\Delta^-)$ (E0) | T01 |
| $G_{S\mid M_1}$ có dạng EVPPI có điều kiện theo observation (đối chiếu toán học, không phải khái niệm mới) | T03 |
| Trong plant này, ranh giới quyết định của oracle dịch theo quantile backlog B và $\kappa$; một tải A chung không đặt được mọi ô vào vùng có quyết định thật | Thử nghiệm REFORMULATE (DISCOVERY, chỉ $p_{\text{sw}}$) |
| Horizon ngắn (2 s) với mode kéo dài làm quyết định bị khóa bởi cấu trúc (conservation hoặc WD) | Nhãn ĐK1 của đầu dò P01, P02 |

## Chưa được claim

- Bất kỳ giá trị nào của $G_S$, $G_M$, $\Gamma$ hay regret: **chưa tính** ở ô nào.
- Hiệu ứng riêng của $\kappa$, quantile B hay $\eta$: các lát ở **cùng độ khó**, không cùng tải, và $\lambda_A$ đồng biến với điều kiện.
- Kết luận cho vùng A nặng hơn B: $\psi$ của lưới nằm trong $[-0{,}2;+0{,}05]$, gần như một phía.
- Tần suất các hiệu ứng trong mạng thật: lưới chọn có chủ đích gần ranh giới quyết định.
- Claim về horizon ngắn ở $\kappa\ge1$.
- Bất kỳ kết luận mạng thật, novelty hay khuyến nghị vận hành. Gap vẫn ở **G1**.

## Ghi chú diễn giải

- $p_{\text{sw}}$ trong $[0{,}1;0{,}9]$ giới hạn trên giá trị state, nhưng không bảo đảm gain vượt $\varepsilon_R$. Gain nhỏ ở Phase 3 là một kết quả hợp lệ.
- $p_{\text{sw}}$ trong dải chưa đủ để có bài toán quyết định: phải kèm nhãn ĐK1 `candidate`. Ô WD có thể có $p_{\text{sw}}$ trong dải chỉ vì hòa.
- Ô oracle-hằng (WD) vẫn có thể có $G_M>0$; giữ chúng cho nhánh model.
- State repair gồm thấy cả hai mode; phần "thấy mode" không phải lợi ích của refresh telemetry backlog (D22).
- Exposure: $p_{\text{sw}}$, nhãn và budget của thử nghiệm đã công khai trên GitHub; contrast chưa ai thấy.

## Bổ sung Part A — 24/10/2026

AI triển khai theo yêu cầu tác giả; [T03 v2](theory/T03_primary_reading_start.md)
và [prior boundary](literature/prior_boundary.md) là reference, không L-self.

- GSgivenM1 bằng EVPPI(x|y) dưới G1–G4; GMgivenS1 bằng E_D[VSS(x)] theo
  định nghĩa conditional mean-future problem dưới G2–G5. Nonnegativity và
  Gamma difference-of-gains không là contribution.
- P11 §2.4 Eq2.7–2.8 đã so input/discrepancy information. Không gọi D21 là
  EVMI hoặc model fidelity gồm parameter/structure repair.
- Chỉnh phạm vi C7 v0: fixed-M0 oracle-state gain không luôn bound feasible
  state-repair gain. Riêng M1 tối ưu true cost với matched belief và cùng info,
  GM/GMgivenS1 vẫn bound model repairs cùng info tương ứng. R00 là cận chung,
  không phải cận duy nhất. Đây là E0/proof, toy chỉ verification.
- p_sw band/candidate chưa chứng nhận hai dấu strict của true gap; không kết
  luận GSgivenM1>0 từ nhãn thiết kế đơn độc. D22 fixed-M0 không tự là EVPPI.
- Số 21.952 toy và 17 kiểm P11 không phải output lưới v1.2, network evidence
  hoặc novelty. Predictions là AI-assisted exposed; formal Gate còn HOLD.

## T-H1 — giới hạn diễn giải do horizon hữu hạn, 26/10/2026

AI soạn theo yêu cầu L2.6 Part B; đây là **interpretation threat**, không đổi
objective, contract, thresholds hoặc estimand.

D13 **đã tính** endpoint occupancy, bao gồm Δt·(qA,H+qB,H) và các packet còn
tồn trong horizon. Nó không có một terminal surcharge bổ sung hoặc cost sau h.
Regret/contrasts chỉ định giá window [t0,t0+h]; action để lại backlog có thể
có hậu quả ngoài window chưa được tính. Không diễn giải kết quả như long-run
network loss hoặc total cost cho tới khi mọi packet được phục vụ xong.

P13 journal [§6/tr289](https://ir.cwi.nl/pub/25530/25530.pdf) bàn end-of-period
effect như một explanation có thể; arxivv1 đặt đoạn đó ở §5.3. Không dùng việc
source nói tới congestion còn lại để khẳng định D13 bỏ toàn bộ backlog qH.
Chưa có terminal-cost sensitivity experiment và không tự thêm vào protocol.

Các giới hạn literature đi kèm: P13 Theorem1 cần Lévy/moment/stability conditions;
Prop5 nói normalized cost với continuous capacity choice. S1 quadratic-loss
illustration còn cần smooth density và small constant gap bias, không có từ
riêng p_sw band/finite posterior. Không nhận “initial state matters”, average
so cumulative, VOI≥0 hoặc Γ bookkeeping là contribution. Mọi hypothesis về
mode/F/V/Γ của grid vẫn chờ chạy đúng protocol và audit L2.8/L2.9.

[Note P13](literature/papers/P13.md) · [phép tính/crosswalk](literature/horizon_transient.md)
· [DL-041](02_decision_log.md#dl-041--l26-part-b-prior-và-interpretation-threat-2026-10-26).

## Ranh giới với prior (Phase 2) — 26/10/2026

AI (Claude) soạn theo ủy quyền của Doan Van Tai ("đóng vai tác giả"), tổng hợp các dòng
K đã có trong [prior_boundary](literature/prior_boundary.md); không thêm nội dung mới,
không đổi contract/metric/thresholds. Mức đọc nguồn: AI-T/AI-A; **L-self 0/19**.

### Không được claim là mới

| Không được claim là mới | Dòng K / nguồn |
|---|---|
| G_{S\|M1}=EVPPI, G_{M\|S1}=E[VSS], dấu ≥0; Γ dạng bookkeeping; tách giá trị thông tin đầu vào với giá trị học discrepancy | PC1, T03 v2, K-S8, SOB14, B82, P11 |
| State cũ có thể làm routing kém; tác hại phụ thuộc age so với timescale; age khác error | K-S1, K-S2, K-S6 |
| Dồn tải theo tin cũ (nhiều quyết định hoặc một dispatcher lặp); chọn ngẫu nhiên ít ứng viên phá đồng bộ | K-S3, K-S4 |
| Lợi ích thông tin queue phụ thuộc load/policy/baseline; độ mịn cost tương tác định tính với update policy | K-S7, K-S5 |
| Đo độ tươi theo cost quyết định; tuổi khác sai lệch; cost phẳng theo sampling budget | K-S9…K-S11, K-F1…K-F3 |
| Trạng thái ban đầu quan trọng với cost cộng dồn; trung bình khác cộng dồn; bỏ cost sau horizon có hệ quả | K-H1…K-H4, T-H1 |
| Fidelity mô phỏng khác chất lượng quyết định; chấm twin bằng decision regret | K-M1, K-M2, NDT26 |
| Tối ưu trực tiếp objective TE; sensitivity theo từng nguồn lỗi và theo horizon/update | K-M3, K-M4, K-M5, P02 |
| Model chỉ cần đủ cho quyết định, kể cả dưới partial observation; dung sai approximate VE | K-M6, K-M7, AIS22 |
| Thông tin mới có thể làm hại một chính sách xấp xỉ; điều kiện đủ để không hại | K-RM1…K-RM3 |
| Bảng 2×2 sửa hai nguồn lỗi; so thứ tự ưu tiên repair | WM26 F.1 |
| NDT what-if đánh giá action; gate theo fidelity; resync/recalibrate | NDT1, P05, NDT26, P10 |

### Được claim (tạm, nhãn AI chấm theo ủy quyền; chưa Gate L)

| Claim | Nhãn tạm | Dạng được claim |
|---|---|---|
| PC1 | DROP như contribution | Chỉ dùng làm framing/ánh xạ có giả định |
| PC2 | NARROW | Đặc trưng theo ô của (GS−GM)/Cref ở K2 dưới D20/D21, oracle không biết w, plant queue làm đổi tải; không claim câu hỏi "repair nào đáng hơn" |
| PC3 | KEEP câu chữ, framing NARROW | Γ/Cref>.005 ở từng ô K3 theo D19; không claim thông tin làm hại, 2×2 repair hay fidelity≠quyết định là mới; khác WM26 ở lượng thông tin của repair |
| PC4 | HOLD | Chưa claim; chờ A05 khóa H1/null |
| PC5 | NARROW | Vị trí ranh giới OεRE dưới S0 trên tọa độ queue (K5/Q5), luật K chưa chọn |
| PC6 | NARROW | Tách backlog/mode ẩn dưới fixed-M0 ở K6; không claim giá trị độ tươi theo quyết định |
| Main RQ | KEEP | Chưa xác nhận prior trùng cả E, M, R từ các nguồn đã đọc |

Không có claim nào ở đây là kết quả lưới (chưa tính contrast/regret ở ô nào). G1 giữ nguyên.
[DL-042](02_decision_log.md#dl-042--gate-l-phase-2-nhãn-main-rq-và-trạng-thái-gate-2026-10-26) ·
[related work](literature/related_work_skeleton.md).

### Bổ sung danh sách không được claim là mới — đợt đọc 26/10/2026

| Không được claim là mới | Nguồn |
|---|---|
| Định giá thông tin theo khả năng dự đoán quyết định; ngưỡng đóng giữa thông tin mới-cục bộ và đầy đủ-trễ | IA26 §1, §3.4 (môi trường ngoại sinh) |
| Chọn telemetry NDT theo giá trị quyết định (ở mức đề xuất) | DTS25 |
| Đánh giá telemetry model bằng replay quyết định | CEN26 §IV |
| Heuristic certainty equivalence gần tối ưu, cận ∝ √var hoặc var (dưới động học affine, reward trơn) | CEH23 §6.1 |

Nhãn tạm PC1–PC6 và Main RQ không đổi ([chi tiết](literature/prior_boundary.md)). Mức đọc AI-T/AI-F.

### Gate L — 26/10/2026 (DL-043)

Tác giả xác nhận nhãn (author-attested) → các nhãn ở bảng "Được claim (tạm)" trên nay là **nhãn
chính thức Phase 2**, Gate L **GO có điều kiện** (thiếu người đọc thật L8). Danh sách "không được
claim là mới" giữ nguyên và áp cho prediction card L3.3. G1 giữ nguyên; chưa có claim kết quả lưới.


### Kết quả card A04 — run27/10, tổng kết28/10/2026 (DL-056)

Đây là **kết quả trên danh sách khóa**, không sửa nhãn prior của Phase2,
không sửa claims.md/card hoặc nhận contribution/novelty mới.

| Claim | Kết quả được phép báo | Giới hạn |
|---|---|---|
| PC2/P2 | Không đứng tại K2;M09/M10 bác ngưỡng1%,M11/M12 đạt | Không đổi ALL thành majority |
| PC3/P3 | Không đứng tại K3;Γ củaM19/M21 dưới.5% | Γ dương không đủ dự đoán strict>.5%;không cơ chế |
| PC5/P5 | K5đạt4/4≤.5%;Q5cóM01/M03≥1%;P5đứng | Chỉ các ô này,D/plant/dt;K5carry m=1 nguyên văn,chưa ngoài mẫu |
| PC6/P6 | Không đứng;V vàV−F âm ởM17/M18 | V không là giá trị refreshbacklog riêng |
| PC4 | VẫnHOLD;H0/H1/fit/split/metric chưa khóa | C1hậu discovery không xác nhận queue mechanism |

Không claim chưa phân giải/excluded ở card;không route/mechanism preregister.
Candidate C1:κ=1,h8 có16/16ôGMnominal0;interpolationR05–R08 chỉ đề cử A05-F,
chưa predictionfrozen. Năm phát biểu đã xét có cả phản ví dụ,không giấu mẫu số.
Ba miềncheap kill không đạt ALL,khôngNARROW theo cheap kill. Không thay RQ/G1.

Kết quả định giá cửa sổ[t0,t0+h],khônglong-run loss. Cùngđộkhó nhưngkhácλA;
D-specific/near-boundary/ψrange/h2κ.3/floor/ĐK1 giữ nguyên. Held-outcost/contrast
chưa mở;publicdesignmetadataexposure được ghi riêng. Humanreading/Phase4giữmở.
[Note](lessons/L3.5_A04_note.md) · [scores](../results/A04/20261027_01/card_scores.csv) ·
[candidate và prior screen](../results/lessons/l3_5/patterns.md).


### Diễn giải sau A04 từ L3.6 — append-only, không đổi điểm chấm

Tại baseline đã đo của M19–M22, upperR00/Cref nằm trong khoảng
0,1096014850%–0,1643461187%, đều dướiεE=0,5%. DoGM≤R00, vếK củaP5
đứng đã được headroom chặn; không lấy nó làm bằng chứng riêng M0 đủ tốt về
mô hình/vật lý. ThayM0 có thể đổi baseline/R00, nên không suy “bất kểM0”.
M19/M21 cóGS=0, nênΓ=GS_M1≤R00, giải thích P3 không thể đạt ngưỡng0,5%
ở baseline này. Không đổi miền hoặc forecast đã khóa; không sửa scores.

EΔhat=0 trong raw của bốn ô cho a00=Stay theo tie rule; kỳ vọng0 không tự
chứng minh từngstatehatgap0 hoặc không cóidle. Các luận điểm vật lý mạnh hơn
chưa kiểm. C1 nếu đăng ký equivalence≤0,5% phải dùng base36/38; base34/38 chỉ
cho nominalzero. Không dùng heuristic độc lập như xác suất thật.
[Addendum và số đo](lessons/L3.5_A04_note.md) ·
[audit](../results/lessons/l3_6/preflight/a04_audit.json).

### Kết quả A05-T — held-out một lần, 28/10/2026 (DL-060)

Áp dụng cho 10 ô R01–R08, R11, R12 ở dt 1/240 s, trong mô hình đã khai báo:

- **PC4:** nội suy **WEAKEN**: H1 gần sự thật hơn H0 nhưng dưới margin đã khóa
  (d = 0,247 < 0,25 điểm % C_ref); ngoại suy h = 12 s **FALSIFY** (d = −0,142). Không được
  claim "động học queue thêm sức dự báo" hay "H1 chính xác". PC4 không đạt SUPPORT.
- **K5:** luật tọa độ κ ≥ 2, A/B q90, h = 8 s **bị bác ở R04** (G_M/C_ref = 0,528%). Chỉ còn
  claim mức danh sách M19–M22 (A04), có headroom chặn.
- **C1:** G_M/C_ref ≤ 0,5% đứng ở R05–R08. Luật post-discovery, base rate cao; không claim
  cho vùng tọa độ liên tục.
- **Chưa kiểm:** trục h = 4 s (R09/R10 niêm phong). Không network evidence, không cơ chế, không G2.
