# Sáu contrast — phần đã có cơ sở và phần còn phải tìm

Người phụ trách: **Doan Van Tai** · 24/10/2026 · AI đề xuất; source notes AI-only.
Điều kiện G1–G5 và proof ở [T03 v2](../theory/T03_primary_reading_start.md).

| Contrast | Khái niệm/identity | Điều kiện | Nguồn, mức đọc | Trạng thái |
|---|---|---|---|---|
| GSgivenM1 | EVPPI của current state conditional on y | G1–G4, đúng argmin và khả tích | SOB14 Method Eq4, AI T; T01/T03 | Có tên; ≥0 là hệ quả; >0 cần hai dấu gap strict có mass |
| GMgivenS1 | E_D[VSS(x)] theo conditional mean-future problem | G2–G5, cùng cost/action set | T03 proof; B82 abstract A, không mượn bounds | Có tên theo định nghĩa; original full reading chưa đủ |
| GM | Gain khi giữ belief state, thay mean rollout theo state bằng đúng expectation | G1/G3/G4 bảo đảm không âm | D10/D19; T01/T03, E0 | Không tự global VSS hoặc EVMI; tên literature còn phải tìm ở L2.8 |
| GS | Giá trị sửa state với fixed approximate M0 | D20/D21, cùng D | T03/V1; exact toy E1 | Có thể âm; không áp VOI≥0 của Bayes đúng-model |
| GSM=R00 | Headroom so với ô00 | Ô11 đúng oracle, cùng D/objective/actions | D15/D18/D19 | Bookkeeping, cận chung; chưa là practical feasible gain |
| Gamma | GSgivenM1−GS = GMgivenS1−GM | D19 | Đại số; exact toy verification | Hai dấu không tự là mechanism; related conditional VOI cần L2.8 |

P11 §2.4 Eq2.7: EVPI(delta) là VOI theo belief, diễn giải upper bound cho EVMI;
GM và GMgivenS1 không tự là đại lượng đó. “Input information so với model
improvement” không được claim mới. Đúng theta không loại hidden x ở S0.

Các bounds cần phân biệt: fixed-M0 oracle-state gain không luôn là cận cho
feasible state repair. Với fixed information/matched belief, M1 tối ưu expected
true cost, nên GM (hoặc GMgivenS1) là cận model repair cùng thông tin. R00 là cận
chung từ ô00, không phải cận duy nhất. Không mở rộng sang model/belief sai.

Không dùng p_sw band/candidate để chứng nhận strict gain; không gọi toy là
Phase3 discovery; không gọi EVIU đã kiểm original source. L2.8 chưa chạy.

## Framing đã có trong nguồn networking — 25/10/2026, AI targeted

- [NDT1 §II-B/IV-B](papers/NDT1.md): dùng twin đánh giá cấu hình cho routing optimizer.
- [P05 §III-A/V](papers/P05.md): what-if cho action/rerouting đổi tải đã có; workflow passive.
- [P10 §III/V–VI](papers/P10.md): online calibration, drift-triggered resync và gate trước action đã có.
- [P08 §2–3](https://arxiv.org/abs/2312.03374v1): parameter identification, device modeling,
  status update là ba vấn đề riêng; AI đọc PDF3–5. Không nhận taxonomy này là mới.

Đây là giới hạn wording/framing từ các mục đã đọc, không phải proof rằng prior đã
trả lời đúng Γ hay controlled2×2 D20/D21. Xem [landscape](ndt_landscape.md);
nhãn PC và formal Gate không đổi.

## Trục state networking — P04, 26/10/2026, AI targeted

Năm điểm phải đặt sau prior, không tự nhận là ý mới:

1. Routing failure tại nguồn khác setup failure có signaling/reservation overhead (§II-C, tr164–165).
2. Periodic staleness có thể gây flapping/tăng blocking; có thể thua load-independent routing trong một số traffic/topology, không phải mọi mạng (§III-A/IV-A, tr166–167,171).
3. Tác động phụ thuộc holding times, burstiness, bandwidth và topology (§III, tr168–170).
4. Trigger có thể đổi failure mix mà tổng blocking thay đổi ít trong các cấu hình đã xét; hold-down lớn vẫn có hại (§III-B, tr168–170).
5. Lợi ích cost granularity phụ thuộc update policy (§V-A, tr172–173, Fig8); không chứng nhận Γ của D19.

[Note primary P04](papers/P04.md) · [đối chiếu và giới hạn](state_staleness.md).
Đây là giới hạn wording; chưa thay quyết định PC3 hay null/H1 của A05.

## L2.5 Part2 — 26/10/2026

[K-S1…8](prior_boundary.md#trục-state--l25-part2-26102026) gom prior có điều kiện.
M00 §3.4/§4 cho policy×delay/randomness, không chứng minh “thêm thông tin tối ưu
làm hại”. P01 Def2/§2.5 dùng cumulative regret so OWR genie, không D18.
R04 re-solving là prior cụ thể chờ A4; đã có archived AI-T provenance, chưa clearance.
Không nhận fixed-M0 negative GS hay Γ>0 như discovery từ toy. Γ=GSgivenM1−GS
làm dấu Γ>0 tự theo khi GS<0 và true-model info gain không âm; cần kiểm action
flips/model bias độc lập trước diễn giải mechanism. Tác giả L-self vẫn pending.

## L2.6 Part A — 26/10/2026

Đo freshness bằng downstream action/control cost đã có ở S11 §III và R32
abstract; AoII còn kết hợp time/error (§II/Eq3–9), AY19 dùng quadratic-error
uncertainty reduction (§2.4), không đồng nhất tất cả với Shannon bit hay D18.
S11 §VII-D/Theorem9/Cor2 cho plateau theo allowed sampling budget, statement
đã đọc targeted, proof chưa kiểm. [K-S9…11](prior_boundary.md#freshness-và-decision-value--l26-part-a-26102026).
Không gọi freshness-aware decision value là contribution. Không từ các phần
đã đọc hoặc hai query screening suy ra GS/Γ với approximate response model mới.
