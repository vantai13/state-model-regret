# L2.7 Part A — thẻ đọc trước lookup

Người phụ trách: **Doan Van Tai** · 26/10/2026. Theo attachment hiện tại.

- Scope: Part A P03/P07/P02; P12/OεRE thuộc Part B, chưa triển khai.
- Câu hỏi PC2/PC3/PC4/PC5: decision fidelity/regret đã có gì, comparator biết gì, controlled2×2 xác định interaction hơn một OAT anchor ra sao? Không đổi RQ/PC/null/metric.
- Ba nguồn có tên được tác giả yêu cầu, không phải đề xuất chưa duyệt: P03 DT² (R51 đã có; ưu tiên PMLR306/amad26a, đối chiếu arxiv2606.25923); P07 DOTE (USENIX NSDI23); P02 DOI10.1016/j.trc.2023.104174 (TU Delft).
- P03 đọc formulation/theorem quantifier/experimental evaluation/limitations; P02 đọc setup/tuning/reference/bias sweeps/discussion; P07 kiểm selected formulation/comparator. Ghi T nếu đã đọc sections, không ghi A sai mức.
- Kiểm library/local PDFs trước; R51=P03 chỉ một work, không thêm duplicate catalog row. Không mở lại18 nguồn archive hoặc tự tải snowball.
- Kiểm riêng: L là expected cost, R mới là regret; OAT từ một anchor thiếu corner khác với cấm mọi sensitivity study đo interaction; P02 có cross sweeps nào; P04/P02 chưa có Γ đúng D19 nên không tự gán dấu prior.
- Kiểm đúng MC expectation khác hindsight; finite policy-class oracle khác global optimum. Regret = sign mistake × gap magnitude, không chỉ sign.
- Tính oracle/RP/WS/EVPI example và exercise; V1 OAT/nonadditivity, conditional/simple effects và averaged main effects; không outcomes grid/held-out hoặc paper simulations.
- Output: notes3sources, K-M1…5, MT1…8 queue cho Phase4 (HOLD), sửa metric#5 landscape bằng evidence P03. MT5 chỉ đưa vào queue A05, không chọn null bây giờ.
- PDF ngoài Git; lưu version/§/trang/hash, AI level riêng human level. Dừng khi đủ formulation/comparator/claim, không algorithms/proofs toàn bài; tối đa90phút không tiến triển/nguồn.
