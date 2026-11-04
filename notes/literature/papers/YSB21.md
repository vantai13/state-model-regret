# YSB21 — Yates et al.: Age of Information, giới thiệu và survey

Người phụ trách: **Doan Van Tai** · 04/11/2026. Note do AI (Claude) soạn.
Tác giả tự tải (thư mục Downloads, 07:06–07:08 ngày 04/11) sau danh sách L7.3-R2 đợt 3. Mức đọc: AI-T.
Tác giả tự đọc: chưa có xác nhận.

Yates, Sun, Brown, Kaul, Modiano, Ulukus. *Age of Information: An Introduction and Survey*. IEEE JSAC 39(5) (2021),
tr. 1183–1210. [DOI 10.1109/JSAC.2021.3065072](https://doi.org/10.1109/JSAC.2021.3065072). Bản arXiv 2007.08564v1 đã có sẵn
trong Zotero của tác giả.

**Phiên bản.** VoR, 28 trang, khớp tr. 1183–1210. Footer có dòng IEEE Xplore "Authorized licensed use limited to ...
Downloaded on May 28,2021". Lưu tại `~/papers/state-model-regret/l73/YSB21/YSB21_AoI_survey_JSAC21.pdf`, sha256
`1169d4f1c266…`. Đọc targeted: §II/PDF2–3, §III-A–B/PDF6–7 (render tr. 1189). Không đọc §IV trở đi.

**Câu hỏi.** Có nguồn primary cho phần "P/2 + L" trong công thức τ_eff ≈ P/2 + L + W/2 của T00 không?

**Quan sát (trích vị trí)**
- **Định nghĩa (§II/PDF2–3).** Age Δ(t) tăng với tốc độ 1 cho tới khi có update mới, tạo dạng răng cưa. AoI là trung
  bình theo thời gian của Δ(t) (eq. 1).
- **Hàng đợi một nguồn (§III-A/tr. 1189, eq. 21).** Với update định kỳ (rate λ, tức chu kỳ P = 1/λ), service memoryless
  1/μ và preemption: Δ_D/M/1* = (1/μ)(1 + 1/(2ρ)) = E[S] + P/2.
- **Các trường hợp khác (§III-A/PDF6–7).** M/M/1 FCFS có Δ = (1/μ)(1 + 1/ρ + ρ²/(1 − ρ)) (eq. 17), tối ưu ở ρ* ≈ 0,53.
  Ở tải thấp, mọi hàng đợi trong Fig. 5 có tuổi xấp xỉ (1 + 1/ρ)/μ.
- **Zero-wait (§III-B/tr. 1189, eq. 22–23).** Cận dưới Δ* ≥ 3E[S]/2.

**Suy luận của AI (chưa kiểm bởi tác giả)**
- Phần P/2 + L của τ_eff trong T00 có cơ sở primary: eq. 21 cho đúng E[trễ] + P/2 với update định kỳ.
- Phần W/2 (cửa sổ trung bình) **không** có trong phần đã đọc. Đó là quy ước của T00 cho ước lượng gom trung bình, vẫn là
  AI-tính.
- Nếu cập nhật xếp hàng FCFS ở tải cao, tuổi lớn hơn P/2 + L nhiều (eq. 17), nên τ_eff là cận dưới.

PC liên quan: realism (định nghĩa τ). Không đổi nhãn PC.
