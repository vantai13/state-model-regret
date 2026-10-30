# Contract v1.3 — amendment 1 (D22 deadline) · tag `contract-v1.3-amend1`

Người phụ trách: **Doan Van Tai** · 30/10/2026 · DL-097. AI (Claude) soạn theo ủy quyền "đóng lesson cho tôi";
khuyến nghị lấy từ lesson L3R.8 §4.1. Tag `contract-v1.3` và 21 file của nó **giữ nguyên byte**. Đây là toàn bộ thay đổi.

| Mục | contract-v1.3 | amend1 |
|---|---|---|
| §7 bảng, dòng 6b D22, cột DEFERRED/closure | "Engine path và audit trước Phase 4" | "Engine path và audit **trước Phase 5** (mechanism)" |
| §7 câu "Phase 4 HOLD tới …" | "… numerical audit/closure, D22 audit, P0-V10/người đọc thật và mọi Gate3R đạt" | "… numerical audit/closure, P0-V10/người đọc thật và mọi Gate3R đạt"; D22 không còn là điều kiện vào Phase 4 |

Giữ nguyên: định nghĩa D22 (§3), giới hạn claim ("SH trước D22 chỉ nói state = backlog + mode oracle"; F̄<0 chỉ
câu hẹp; không gán cb0 = 0). Phase 4 báo F̄/V̄ = null, đúng như card v2 dòng 191 đã cho phép.

Vì sao: F̄/V̄ không vào verdict nào; D22 là phép tách cơ chế mà Phase 5 cần. Hai văn bản trước đây mâu thuẫn
(contract: trước Phase 4; card v2: null nếu chưa có). Amendment này chọn cách card đã cho phép. D22 tính sau trên
regime CF là phân tích cơ chế/discovery, không phải confirmation, nên không cần "lần chạy duy nhất".

Không đổi: card v1/v2, numerics v1.3.1-lean, n, root, danh sách CF, ngưỡng, verdict.
