# DTS25 — đồng bộ NDT theo where/when/what (bài ý tưởng)

Người phụ trách: **Doan Van Tai** · 26/10/2026 · tác giả duyệt đọc; mức **AI-F** (đọc hết 2 trang), chưa L-self.

Zhiheng Yang; Francisco Vogt; Adam Belloum; Christian Rothenberg; Paola Grosso; Chrysa
Papagianni. *Adaptive Digital Twin Synchronization: A Mechanism for Where, When, and What to
Measure.* CoNEXT'25 Student Workshop, 2 trang, [DOI 10.1145/3769700.3771695](https://doi.org/10.1145/3769700.3771695).
PDF tác giả tải (`RC3.C29 (1).pdf`): `~/papers/state-model-regret/current/DTS25.pdf`, sha256 `c069d65b…7c84`.

**Câu hỏi đọc (PC2/PC6):** NDT đã đo giá trị của đồng bộ telemetry theo chất lượng quyết định chưa?

## Fact

| Nội dung | Vị trí |
|---|---|
| Đề xuất Neural Measurement Field λθ(e,t,f,p\|z_c): một hàm cường độ chung cho where/when/what, học online để tối đa "decision fidelity per unit cost" dưới ngân sách | Abstract, §1 tr1, §2 tr2 |
| Proxy đồng bộ là "uncertainty or decision impact"; encoder gồm staleness/drift | §1 tr1, §2 tr1–2 |
| **Chưa có thí nghiệm**: "Planned Validation… We will evaluate"; "the description remains conceptual" | §3–§4 tr2 |

## Inference

Bài xác nhận cộng đồng NDT đã **đặt vấn đề** chọn telemetry theo giá trị quyết định (framing
PC2/PC6), nhưng không có số đo, không có oracle/regret, không có trục model. Không đổi nhãn;
thuộc bối cảnh cho đoạn 1 của related work.
