# Diff contract v1.2 → v1.3

Người phụ trách: **Doan Van Tai** · 29/10/2026 · DL-071.
v1.2 vẫn mô tả kết quả cũ. Bảng này không sửa prereg/outcomes Phase 3.

| Nguồn v1.2 | v1.3 | Vì sao / giới hạn |
|---|---|---|
| D1 dt rule; A01 chọn final dt | R1–R8 khóa; global K*/dt* DEFERRED | L3R.3 HOLD; tag không chứng nhận mức số |
| D2 fixed horizons của grid | h là tham số regime; frame chọn sau | Không đổi h giữa action/pipeline/refinement; không silent ceil |
| D3 paths/capacity | Giữ μ10, hai path rời | Không thêm shared bottleneck |
| D4 λB8, λA neo p_sw | λA/λB tự do theo design; ratesλ±6 | Không tính J/Δ để neo CF; giữ R2/biên độ |
| D5 u=2η, c_sw0 | Lưu u,φ dẫn xuất; primary c_sw0 | Cost >0 vẫn phải có trong scientific identity |
| D6–D7 slotted recurrence/full state | Giữ; viết estimand indexed by dt | dt đổi law/cost; chưa adopt continuous limit |
| D8 một quantile y cố định | Y theo P1 stationary, age1, không mode | Controller vẫn chỉ thấy một Y mỗi episode |
| D9 true shared posterior | Giữ, suy từ cùng P(Y,X) | Không lọc bằng M0 rồi nhận GM≥0 |
| D10–D11 mean rollout/true model/no future | Giữ | M0 không rollout từ mean-state; oracle không hindsight |
| D12 conditional stationary at y* | Full stationary joint P1 | Recovery y* condition cả joint và marginal X |
| D13–D17 cost/J/oracle/tie/gap | Giữ ở registered dt; c_sw add once nếu scenario | Exact tie khác uncertified tiny interval |
| D18–D19 cost/regret/six contrasts | Population expectation; cùng đại số | S01–S18/T07, identity không thành finding |
| D20 full state repair | Giữ backlog+mode oracle | Không gọi S1 là feasible telemetry |
| D21 model repair | Giữ stochastic representation, θ đúng | Không parameter/structure repair |
| D22 current backlog diagnostic | Cam kết; definition LOCKED, physical path/audit DEFERRED | Toy/reference không chứng nhận production path |
| D23–D24 Cref mỗi ô,1%/.5% | RoE Ḡ/C̄ref,1%/.5%; stakes descriptive | Giữ con số, ghi ý nghĩa đã đổi; không SLA; không OR |
| D25 A05 H0/H1/R held-out | RQ2 H0/H1→Phase5; CF mới→L3R.7/Phase4 | R đã mở là discovery; R09/R10 niêm phong |
| Ownership/human reader | Giữ OPEN | Tác giả chọn khoa học không phải tự read-back/human review |

Những chỗ chỉnh lý luận từ lesson: không coi refinement gap là cận total error
hoặc bảo đảm chọn mức không đổi verdict; invariance S1 cần fixedπ/J/policy,
không mặc định theoκ; population hữu hạn không bảo đảm smooth. Validity chỉ
đòi stability trước action; overload sau Switch trong finiteh không tự vô nghĩa.
JSON schema chỉ cấu trúc; semantic cross-field checks là lớp riêng.
