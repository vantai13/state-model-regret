# JAN19 — Alipourfard et al.: Janus, lập kế hoạch thay đổi mạng DC theo rủi ro

- Người phụ trách: **Doan Van Tai** · 20/11/2026. Note do AI (Claude) soạn.
- Tác giả duyệt ngày 20/11, issue 1, đề xuất số 3.
- PDF do Codex tải (trang tác giả, minlanyu.seas.harvard.edu).
- Mức đọc AI: AI-T (Codex đọc, Claude kiểm trích dẫn). Tác giả tự đọc: chưa có xác nhận.

O. Alipourfard, J. Gao, J. Koenig, C. Harshaw, A. Vahdat, M. Yu. *Risk Based Planning of Network Changes in Evolving Data Centers*. Proc. ACM
SOSP 2019, tr. 414–429. [DOI 10.1145/3341301.3359664](https://doi.org/10.1145/3341301.3359664). Metadata đối chiếu Crossref ngày 20/11.

**Phiên bản.**
- Bản tác giả (`sosp19.pdf`).
- Lưu tại `~/papers/state-model-regret/current/JAN19_Janus_SOSP19.pdf`, sha256 xem catalog.

**Đọc targeted:** §1, §3.3, §4, §5.1.

**Quan sát (trích vị trí)**
- **§3.3 ("Estimating cost with Monte Carlo simulations"):** "losses using flow-level Monte-Carlo simulations"; "We use the current TM to
  represent what happens in the next planning interval and use the past TMs to predict the TMs for the remainder of the change. Previous work
  [44] … find that the current TM is a good estimation of the future (e.g., the next step of the plan)".
- **§4:** "Janus uses the current TM as a prediction of the traffic for the upcoming subplan and the 10 previously observed TMs as a prediction of
  traffic for the rest of the plan."
- **§5.1:** đánh giá với subplan "one timeslot (5 minutes)".
- Mô hình là max-min bandwidth flow-level, không có thời gian chờ hàng đợi dừng (theo Codex, `codex_search.md` D.2).

**Suy luận của AI (chưa kiểm bởi tác giả)**
- Đây là planner kiểu what-if, đánh giá cấu hình được giữ trong subplan kế tiếp bằng TM hiện tại (giả định persistence) và mô hình không có
  hàng đợi. Nó gần lớp "twin dùng rate snapshot".
- Hold của mỗi subplan ngắn (5 phút); toàn bộ thay đổi kéo dài hơn.
- Prototype đánh giá bằng trace, chưa xác nhận triển khai production.

**Dùng trong letter (v8.6):** `\cite[Secs.~3.3 and~4]{Alipourfard:SOSP:2019}`. Hai agent kiểm.
