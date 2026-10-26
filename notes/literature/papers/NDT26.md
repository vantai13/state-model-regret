# NDT26 — gate theo fidelity trong Open RAN

Người phụ trách: **Doan Van Tai** ·26/10/2026 · tác giả duyệt đọc; **AI-T**, chưa L-self.

Akram Almohammedi; Mohammed Balfaqih; Sam Darshi; Rami Langar; Wael Jaafar.
*Twin-Fidelity-Aware Resolution of Direct xApp Conflicts in Open RAN*.
[arxiv2607.22857v1](https://arxiv.org/abs/2607.22857v1),24/07/2026,15pages.
**Preprint**, submitted IEEE TNSM; chưa xác nhận acceptance. Khác P10/OpenTwin.
PDF: `~/papers/state-model-regret/current/NDT26.pdf`.

- **PC3/PC5:** §III-B/C–V, PDF5–8/Eq1–12/Algorithm1: chọn1trong21power blends
  giữa ES/CTO xApps bằng twin-predicted throughput−energy cost; theo dõi absolute
  utility error của **action đã chạy**, EWMA vượt threshold thì dùng best past
  observed action. Fidelity-aware NDT gating và utility regret đã có trực tiếp
  trong networking; không nhận chúng như ý mới của repo.
- **Thông tin:** controller không biết full live utility landscape hoặc optimum;
  evaluator dùng chúng tính regret (§IV-B/PDF6). Gate dùng ε trước action, cập nhật
  sau feedback (§V/Algorithm1). On-policy error chưa chứng nhận ranking mọi action.
- **Thiết kế:** §IV-B/Eq6/PDF6,§VI-B/PDF9 gây mismatch bằng offset neighbor power
  d; live/twin cùng simulator, d0 khớp. Không phải D21 sửa mean-future expectation.
  Những phần đọc không có independent D20 hidden-state reveal × D21 repair.
- **Giới hạn:** §IV-D/PDF7 cần calibrated warm-up, slowly varying optimum, đủ
  query budget. §VI-D/PDF9 chọn τ trên **all evaluation runs**: không mượn làm
  evidence held-out predictive validity cho PC4. §VI-E/PDF9 có20seeds/95%CI;
  **chưa chạy** MATLAB hoặc kiểm toàn results.

AI-T PDF1,5–9; nhìn Algorithm1/TableII. Tier2 gần NDT, không clearance PC3/PC5.
