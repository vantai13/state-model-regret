# AIS22 — model/state đủ cho quyết định dưới partial observations

Người phụ trách: **Doan Van Tai** ·26/10/2026 · tác giả duyệt; **AI-T**, chưa L-self.

Jayakumar Subramanian; Amit Sinha; Raihan Seraj; Aditya Mahajan.
*Approximate Information State for Approximate Planning and Reinforcement
Learning in Partially Observed Systems*. [JMLR23(12):1–83,2022](https://www.jmlr.org/papers/v23/20-1165.html).
Journal peer-reviewed, bản JMLR83pages; PDF: `~/papers/state-model-regret/current/AIS22.pdf`.

**PC5:** §2.3 Def3/Theorem5/PDF6–8: history compression đủ nếu giữ expected
reward và luật next compressed state; khi đó giữ DP/action values. Không cần
predict mọi observation nếu phần đó không phục vụ control (example/PDF7).

**Approximation:** §3.2 Def7/PDF15: uniform reward error≤εt, transition IPM
error≤δt trên histories/actions. Theorem9/Eq14–17/PDF16–18 cho
αt=εt+ρF(Vhat[t+1])δt+α[t+1], α[T+1]=0; value approximation≤αt,
loss của greedy approximate-DP policy≤**2αt**. Đã nhìn công thức/absolute bars
trong PDF, đọc proof backward induction; không lấy average training error thay
uniform assumptions. Bounded/finite-value và finite IPM functional cần kiểm
khi áp sang system khác; model finite spaces trong §2.1/PDF4.

**So repo:** prior cụ thể về joint compressed state/approximate reward-transition
model adequacy, không nhận “model đủ dưới partial information” là mới. Đây không
phải independent D20 reveal × D21 mean-future repair hoặc normalized GM/Cref
uniform trong K5. Muốn chuyển bound phải chứng nhận ε,δ,ρ và embedding;
chưa thực hiện việc này. Tier2 cho PC5, không xác nhận PC5 đúng.

Targeted PDF4,6–8,14–18; không full83pages, infinite-horizon/learning/experiments
và appendices chưa đọc. Không chạy paper code; L-self/Gate còn mở.
