# CEN26 — CENTILE: telemetry model được chấm bằng quyết định

Người phụ trách: **Doan Van Tai** · 26/10/2026 · tác giả duyệt đọc; mức **AI-T**, chưa L-self.

Zifan Zhang; Zhichao Hou; Tingxiang Ji; Yuchen Liu. *CENTILE: A Telemetry Foundation Model
Evaluated by the Decisions It Drives.* [arXiv 2608.01725v1](https://arxiv.org/abs/2608.01725v1),
03/08/2026, 11 trang, **preprint**. PDF: `~/papers/state-model-regret/current/CEN26.pdf`, sha256 `17f962ee…b5c267a`.

**Câu hỏi đọc (PC5):** trong networking, model dự đoán tương đương theo sai số có cho quyết
định tương đương không, và đánh giá dùng comparator nào?

## Fact

| Nội dung | Vị trí |
|---|---|
| Point-forecast error "saturates near last-value baselines… can stay flat while the decisions it feeds diverge" — câu này bài **trích từ nguồn [6]**, không phải kết quả riêng | §I tr1 |
| Lý do quantile hiệu chỉnh giúp quyết định (Assumption 1, hợp đồng quantile) | §III-D tr5 |
| Replay backfilling: 5 nguồn walltime (user limit, History q90, Tsafrir last-2, GBM quantile, CENTILE); **true runtime chỉ là reference**; MASE=1 tương ứng dự báo last-value | §IV-A tr6, Table III tr7 |
| CESNET provisioning: tỉ lệ vi phạm 20,5% → 9,0% | §IV-D tr8, Table VI |

## Inference

Thêm một ví dụ networking của "đánh giá model bằng quyết định" (K-M1/K-M2, NDT26). Comparator
là replay với runtime thật (hindsight), khác oracle D15; không có 2×2 state × model; "last-value"
là baseline dự báo, không phải can thiệp D20. Không đổi nhãn PC5.
