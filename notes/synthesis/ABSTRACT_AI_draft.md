# A2 (L7.4) — abstract nháp ≤ 200 từ

Doan Van Tai — **AI (Claude) viết theo ủy quyền** ("đóng vai trò là tôi", 04/11/2026). Mentor ghi A2 là việc tác giả
viết **bằng lời của mình**. Bản này **không phải** abstract của tác giả; nó chỉ là khung để tác giả viết lại. Không dùng
nguyên văn trong paper khi tác giả chưa tự viết.

Viết bằng tiếng Anh (ngôn ngữ dự kiến của paper). Mỗi câu phát hiện có nhãn claim ([CLAIMS_EVIDENCE](CLAIMS_EVIDENCE.md)).
Không có câu nào về τ, vì quét τ chưa có truth.

---

**Fresh telemetry or a better model? When a horizon-blind network twin should not be refreshed**

A network digital twin that steers load must trade investment in fresher telemetry against investment in a more faithful
model. We study this trade-off for a single steering decision held over a horizon h, comparing a mean-value twin with
the true model on stale and fresh state in exactly solvable two-path Markov-modulated queues. We find three regularities.
First, the value of fresh state for the mean-value twin follows a zero-fit first-order law, h·s·ΔF plus a state-weighted
bias, accurate to 0.1 percentage points from about 4–7 integral times of the backlog [C1]. Second, beyond about seven
integral times a stationary rule that ignores state is within 0.1% of the optimum [C2], while fresh state harms the
horizon-blind twin in most regimes outside a narrow band [C3]; the harm persists when fresh telemetry carries only
backlog [C4]. Third, the backlog's integral time, rather than the burst time constant, orders convergence [C6]. Within
the model, refreshing a horizon-blind twin can therefore hurt; fresh state pays only at horizons short against the
integral time.

---

**Đếm từ:** khoảng 180.

**Chú thích để tác giả viết lại:**
- "zero-fit" cần giải thích một lần: chỉ dùng twin và đại lượng dừng, không fit truth.
- Câu kết có điều kiện "within the model" là bắt buộc (THREATS K2, K4, E1–E5).
- Không viết "first" hay "novel". Kiểm novelty mới ở mức đã sàng ([L7_4_novelty_check](../literature/L7_4_novelty_check.md)).
- Cơ chế "planner ngầm" (C5) **chưa** vào abstract, vì nó vẫn là giả thuyết.
