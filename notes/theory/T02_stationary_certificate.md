# T02 — stationary solver: điều gì được chứng nhận

Người phụ trách: **Doan Van Tai** ·23/10/2026. Hai mode đối xứng, increments nguyên coprime a0<0<a1, a0+a1<0, positive transition probabilities. Input s có interval radius cho R2 exp; không giả Fraction(float) là physical law chính xác.

Chọn t>0 và v_m>0. Với tilted matrix K_mn=exp(t*a_m)P_mn, tính bằng Decimal upper arithmetic một λ≥max_m(Kv)_m/v_m<1. Phản xạ tại0 cho EV_next≤λEV+vmax, V=exp(tq)v_m. Iteration từ0 và Fatou cho stationary moment≤vmax/(1−λ), nên tail P(q>K)≤C exp(−tK), C=vmax/[vmin(1−λ)]. Không suy tail chỉ từ mass trên một chain bị cap.

Solver tạo chain hữu hạn q≤K với cap chỉ để tính số. Gọi μ là invariant law chain này, π true law, ν là π collapse tail lênK giữ mode. One-step stationarity residual của ν dưới capped chain có TV≤ε_tail. Với atom(0,off), bất kỳ supersolution h_i≥1+Σ_j Q_ij h_j, h_atom0, cho max expected return time≤T=maxh. Poisson/return-time representation có span≤2T, nên một approximate invariant law với residual TV≤r cách μ không quá2Tr. Suy ra bound bảo thủ cho true law và output: **(1+2T)ε_tail+2Tr**, cộng conversion/normalization roundoff.

Code tìm h bằng sparse solve rồi kiểm **Bellman inequality bằng directed Decimal arithmetic**; không coi float solve là certificate tự thân. Invariant occupation dùng regenerative atom và iterative refinement; residual bounds bao gồm interval s và rounding guard. Output float-conversion errors được cộng vào bound. K vượt50.000, T vượt precision envelope, negative mass hoặc bound không đạt đều HOLD/error; không normalize finite cap rồi gọi đó là infinite posterior.

Đây là prototype certified theo assumptions/precision envelope đã ghi. Closed-form −2/+1 được đối chiếu bằng Decimal70digits, không lấy sai số của closed-form float làm ground truth chính xác. Generic −5/+3 và R2 probability interval cũng có tests. Tail-bound nhỏ không tự bảo đảm conditional posterior tốt: conditioning tại event xác suấtp khuếch đại error, cần báo bound kiểu2ε/(p−ε) khi p>ε. Quantile phải kiểm CDF interval tách khỏi α; nếu không, giữ interval quantile thay vì chứng nhận một index. Những điều kiện posterior/quantile này còn phải đạt trước B2/B3 thật.
