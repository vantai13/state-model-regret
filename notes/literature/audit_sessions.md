# L2.8 — bốn thẻ audit có giới hạn

Người phụ trách: **Doan Van Tai** ·26/10/2026 · AI-assisted/exposed.
Mục tiêu: kiểm prior có cùng estimand/mechanism/regime; không chứng minh novelty.
Đây là A1–A4 **literature**, khác A01/A04/A05 experiments của dự án.

| Thẻ | Claim / câu hỏi chặn | Hai query dự kiến, chưa coi đã chạy | Paper neo / citation | Giữ nếu / giới hạn |
|---|---|---|---|---|
| A1 | PC3/PC4: routing/NDT đã so state-info gain dưới hai response models và interaction chưa? | `routing state information model approximation interaction`; `network digital twin state fidelity model fidelity decision regret` | P04, forward tối đa20records | Có decision/action cost và tách intervention; prediction-only thì context. Networking trước, chưa thực hiện trong Part1 |
| A2 | PC3: freshness value dưới model mismatch khác known-law ra sao? | `age of information model mismatch value of information`; `fresh state information approximate model control performance` | S11, forward tối đa20records | Tách thông tin/model và downstream cost; không đánh đồng AoI với decision value. Chưa thực hiện trong Part1 |
| A3 | PC5/PC3: model adequacy theo decision/regret có phụ thuộc information structure? | `decision focused model partial observability model sufficiency`; `approximate value equivalence information structure decision regret` | P12/R43, forward tối đa20records | Kiểm norm/quantifiers/state representation, không chỉ trùng từ equivalence. Chưa thực hiện trong Part1 |
| A4 | PC3/PC4: deterministic re-solving có thể làm hại, stochastic formulation nào không hại và dưới điều kiện gì? | `certainty equivalence value of information negative value reoptimization`; `deterministic linear programming resolving revenue management information` | R02 Cooper2002, forward tối đa20records | Giữ E/M overlap; không coi multi-step resource re-solving bằng D20, stochastic approximation bằng exact M1. Part1 chạy metadata/abstract screening; full đọc Part2 |

Mỗi session tối đa2query variants×20records và1forward pass×20records,
ngân sách30phút thực chạy/phiên,90phút targeted/source nếu được yêu cầu.
Ngân sách là cap, không guarantee đủ coverage. Chỉ gọi stopping rule đạt khi
2variants liên tiếp **mỗi query đã sàng20** và không có candidate mới; ít hơn20
hoặc provider errors thì ghi không đạt, dừng theo budget/scope. Forward failure
không là “0citing papers”; ghi những records thực trả và tool/source/filter.

Tier1 có thể đổi judgment claim → cần primary reading trước L2.9;
Tier2 gần estimand/mechanism nhưng khác regime → ghi chỗ unclear;
Tier3 chỉ context → log, không thêm reading list. Tối đa3Tier1 ưu tiên cho đợt
này: R01/R02/R04 tác giả chỉ định; nguồn mới phát hiện chỉ đề xuất tối đa3,
chờ duyệt trước download/note. Không tự đổi PC/Gate/null hoặc chạy Phase3.

## Execution Part2 —26/10/2026

[Ledger](../../results/lessons/l2_8/part2/search_calls.json): A1 44,A2 45,A3 60,
A4variant2repeat20screening events. Dự đoán AI/exposed trước phiên ở
[reading card](../../results/lessons/l2_8/part2/reading_card.md).
A3 có WM26/Tier1framing thay dự đoán0Tier1. A1 NDT26/A2 AIS22 Tier2 được duyệt.
Không gán toàncandidate counts khi raw rank-level không được giữ sau resume.
A2forwardS2 vẫn429, A3q1Scholar vẫntimeout; provider fallbacks đã ghi riêng.
Không đạt2×20 zero-new rule; dừng bounded scope/budget, không saturation.
[Four conclusions, primary reading, HOLD](literature_audit_part2.md).
