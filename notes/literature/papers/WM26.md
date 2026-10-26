# WM26 — bảng 2×2 repair trong latent world models

Người phụ trách: **Doan Van Tai** ·26/10/2026 · tác giả duyệt; **AI-T**, chưa L-self.

Rui Min; Xianyao Li; Fang Xu; Eric Jing Du (arXiv metadata: Jing Du).
*When Low Prediction Error Misleads Planning: Diagnosing Representation,
Dynamics, and Decision Failures in Latent World Models*.
[arxiv2610.05550v1](https://arxiv.org/abs/2610.05550v1),04/10/2026,40pages,
**preprint under review**, chưa xác nhận peer-reviewed publication.
PDF: `~/papers/state-model-regret/current/WM26.pdf`.

**Prior mạnh cho framing PC3/PC4:** §4–5/PDF4–5 và F.1/Eq10/Table10/PDF22
có bốn endpoint sets **P,C,S,E**: predicted; sửa center; sửa responses; sửa cả hai.
Đo physical ranking/elite error trên cùng physical starts/candidate pools. Vì vậy
“bảng2×2 sửa hai nguồn lỗi và so repair priority” đã có prior cụ thể.

**Khác contract:** center là trung bình **qua các candidate actions**, không
hidden current state D20 hay trung bình future disturbance của D21. C/S dùng
realized future endpoints: C nhập true pool mean, S nhập từng centered response;
**khác information budgets** (F.1/PDF22). E vẫn qua learned representation/goal
metric, **không phải true-performance upper bound** (F.1/PDF23), khác oracle D15.
Dreamer E còn dùng observations tương lai để posterior-update (§7.2/PDF7).

**Paper báo cáo:** §7.1/Table1–2/PDF6 và F.2/PDF25:14/16cells center-dominant MSE,
6cells response repair tốt hơn trên cả hai decision criteria, nominal family-wise
intervals; không16independent replications. Không lấy con số này làm frequency
cho queue hoặc so trực tiếp với GS. F.1/PDF22–23 báo C−P,S−P,C−S;
**chưa xác nhận cùng D19Γ** từ các phần targeted; bốn giá trị cho phép contrast
đại số nhưng không cùng estimand/interventions.

Targeted PDF1,3–8,22–23,25,28; Table10 được nhìn trực tiếp. Không full40pages,
không chạy code/closed-loop experiments; incremental closed-loop gains vẫn
unconfirmed trong phần bài đọc. **Tier1 cho framing**, không tự đổi nhãn PC.
