# Claim boundary v1.3 — sau L3R.6 (cards v1 FROZEN)

Người phụ trách: **Doan Van Tai** · 29/10/2026 · DL-073–074.
File này không thuộc lock receipt contract v1.3; hash của nó ghi trong
[receipt card](phases/PHASE_3R_hypothesis_cards.lock.json). Khung trống trước đây giữ ở commit
`2f41957`. Cards: [PHASE_3R_hypothesis_cards.md](phases/PHASE_3R_hypothesis_cards.md). AI soạn,
tác giả duyệt lựa chọn; chưa có evidence CF, G1 không đổi.

| Slot | Card | Vùng (chỉ tọa độ) | Có thể bác bỏ bằng | Identity/prior | Câu không được nói |
|---|---|---|---|---|---|
| Primary1 | Hyp-MV: ḠM/C̄ref≥1% ở đa số Ω_MV⁺, không ở Ω_MV⁻ | Ω⁺ λB=8, λA∈[7;7,5], u∈[1;1,5], κ∈[0,1;0,3], h∈[12;16]; Ω⁻ chỉ lật κ∈[1;3] (ngoại suy) | R⁺ ở Ω_MV⁺ → FALSIFY; Y⁻ → WEAKEN-W1 | Không dùng ḠM≥0, ḠM≤σ̄; P11/P12/AIS22/P13 khác ở E/M/R | “Model quan trọng hơn state” nói chung; “telemetry”; prevalence |
| Primary2 | Hyp-SH: ḠS/C̄ref≤−1% ở đa số Ω_SH⁺, không ở Ω_SH⁻ | Ω⁺ λB∈[6;7], λA∈[7;8], u∈[1;1,5], κ∈[0,1;0,3], h∈[8;16]; Ω⁻ chỉ lật κ∈[1;3] (ngoại suy) | R⁺ ở Ω_SH⁺ → FALSIFY; không có WEAKEN theo dấu | Không dùng “Γ̄>0 trong harm” (S12); K-RM1 đã biết harm có thể xảy ra | “Telemetry tươi có hại”; harm do backlog tươi trước D22 |
| Secondary | **Không cấp** (phương án D) | — | — | Γ̄≥−min(ḠS,ḠM): discovery 3/162 cấu hình có thông tin | “Hai repair bổ trợ” hoặc “không substitution” như quy luật |

Hai primary dùng Bonferroni (α=1/40 mỗi card); trong card Ω⁺ AND Ω⁻ không chia α. “Đa số”
nghĩa là tỉ lệ theo measure đã khóa trong card (λ/u đều, κ/h log-đều), cận Clopper–Pearson.

Scope không được bỏ: P1/plant fixed, a/μ=.6, c_sw=0, ideal backlog + hidden-mode oracle, endpoint
objective; realism HOLD_UNSOURCED (mọi vùng UNSOURCED); εR là quy ước, chưa SESOI vận hành.
“Interact” chỉ mô tả. “Differ” chỉ là đặt hai verdict cạnh nhau trên cùng thước, không phải phép
so sánh MV với SH đã chấm. Không carry PC cũ hay verdict A04/A05-T như confirmation cho v1.3.
Card chưa là evidence; CF chưa sinh; numerics v1.3.1, D22 audit, P0-V10/L8, Gate3R còn trước Phase4.
