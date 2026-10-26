# CEH23 — cận hiệu năng của heuristic certainty equivalence

Người phụ trách: **Doan Van Tai** · 26/10/2026 · tác giả duyệt đọc; mức **AI-T**, chưa L-self.

Chen Yan; Alexandre Reiffers-Masson. *Certainty Equivalence Control-Based Heuristics in
Multi-Stage Convex Stochastic Optimization Problems.* [arXiv 2308.13166v1](https://arxiv.org/abs/2308.13166v1),
25/08/2023, 69 trang, "Submitted to Operations Research"; Crossref top-3 chưa thấy bản xuất bản
(lượt 26/10). PDF: `~/papers/state-model-regret/current/CEH23.pdf`, sha256 `c2fa2be7…39493e5`.

**Câu hỏi đọc (PC5, PC3):** có cận tổng quát cho khoảng cách giữa chính sách CE (thay bất định
tương lai bằng giá trị danh nghĩa, nghĩa của M0) và chính sách tối ưu không, dưới giả định nào?

## Fact

| Nội dung | Vị trí |
|---|---|
| Mỗi bước: biết **đầy đủ state hiện tại** X(t), quan sát W(t) rồi mới chọn U(t) | §2 tr5 |
| Giả định: reward lõm C³; ràng buộc lồi C²; W i.i.d. bị chặn; **động học affine trong kỳ vọng** E[X(t+1)\|·]=ϕ affine | §2 tr6, Assumptions 1–8, Eq2–3 |
| CEC relaxation thay bất định bằng giá trị danh nghĩa; update policy re-solve mỗi bước | Abstract; §5.1 tr17, Eq20 |
| Định lý 1: V_opt−V_update ≤ P·C₁+(1−P)V̄, C₁=O(√var[W]+√var[E]) (Lipschitz) | §6.1 tr21–22 |
| Định lý 2: C₂=O(var[W]+var[E]) (C²-smoothness); P→1 khi phương sai→0 | §6.1 tr22 |
| Re-solving nhiều hơn "not always beneficial", trích Cooper (2002) = R02, Secomandi (2008) = R04 | §8 tr29 |
| Ví dụ network utility maximization | §3.1 tr9; §7 tr25 |

## Inference — ánh xạ sang repo

- CE ở đây đúng **nghĩa #3** (biến ngẫu nhiên tương lai → giá trị danh nghĩa), cùng nghĩa M0;
  với state đầy đủ, khoảng cách V_opt−V_update gần **G_{M|S1}** của repo.
- Plant của repo **vi phạm Assumption 5**: q⁺=max(0, q+a−c) không affine trong kỳ vọng; khoảng
  cách M0/M1 của repo sinh ra chính từ phi tuyến ở biên rỗng (EV-33, Jensen). Cận ∝ variance
  của bài không áp trực tiếp; bài cũng không cho vị trí ranh giới theo tọa độ queue.
- Thêm vào "không được claim là mới": heuristic CE gần tối ưu khi phương sai nhỏ, có cận
  tường minh dưới giả định trơn/affine. PC5 vẫn chỉ đứng ở dạng hẹp (vị trí ranh giới trong
  plant phi tuyến). Gợi ý cơ chế cho hàng đợi H1 (H1-Q04), chưa khóa.

Đọc targeted: abstract, §1 đầu, §2, §5.1, §6.1–6.3, §8. Chưa đọc chứng minh (EC.2) và §3.2–3.3, §7 chi tiết.
