# L4.5 — Nháp claim boundary theo nhánh, chưa adopt contract v1.4

Người phụ trách: **Doan Van Tai** · 30/10/2026.
Provenance: AI soạn; **DRAFT_CONDITIONAL_NOT_CARD_DECISION**.
Không sửa contract/cardv2 hoặc claim boundaryv1.3 frozen. Chưa có outcomeCF.

## Baseline đã khóa trước confirmation — cập nhật 31/10/2026

A3/B1: MV rho=1/20 ở cả ba mức, median recovery0,862967–0,867986. Nếu card MV
PASS ở Phase5, câu claim bắt buộc ghi **“so với controller mean-field không
margin”**; margin đơn giản đã lấy lại khoảng86% model gain trên discovery.
SH rho=0, median abs(GSθ)/Cref4,679597–4,701969%,deltaL10=0: không thu hẹp
theo lưới baseline đã thử. SV rho=1/100 trên448READY, baseline không thu hẹp
theo luật SV đã khóa (DL110). Những câu này không phải verdictCF.

SUB được tác giả chọn chạy một hộp native+baseline. Áp nguyên readingMV+A:
nếu medianR_M>=1/2 thì câu SUB phải kèm **“so với controller không margin”**;
không đổi Gamma, metric hoặc card verdict vì điều này. Chỉ ghi kết quả sau run.

Không giả định recovery đơn điệu theo rho. rho=5% đã là witness đủ để thu hẹp
MV trong lưới đã thử; không cần mở rộng lưới hoặc A4. Ba numerical levels có thể
cùng bias; STABLE không là convergence/certificate từng point.

| Nhánh tương lai | Câu có thể viết nếu phép kiểm tương ứng PASS | Giới hạn |
|---|---|---|
| 0card mới | Regime map là discovery thích nghi do AI thiết kế/chạy; không có confirmation cho SV/SUB. NếuF1PASS chỉ nói về MV/SH đúng vùng/metric đã khóa | Không claim state value dương/substitution đã xác nhận; không suy0card từ thiếu dữliệu |
| ChỉSV | TrongΩSV⁺, đa số regime cóGS/Cref≥1%, với contrast vùngΩSV⁻ theo card tương lai nếu đạt | Không tự suyGM nhỏ hoặc double dissociation đầyđủ; thêm prior/ baseline wording đãkhóa |
| ChỉSUB | TrongΩSUB⁺, đa số regime cóΓ/Cref≤−1%, ởmức môhình, nếucardPASS | GS,GM≥1% trên những regimeMEETS làidentity, khôngfinding thứhai; kèm baseline đúngcandidate |
| SVvàSUB | Hai câuSV/SUB riêng nếu từngcardPASS, báo cảverdict củaF1/F2 | Không cheFALSIFY/INCONCLUSIVE; FWER liênfamily cóunionbound khác.05 |

Không nói genericfreshnessvalue/2×2repair làmới, khôngprevalence/realism hoặc
operational recommendation. “Không thấy trong targetednotes” không phải novelty.
F1cònchưa chạy; mọi câu trên làđiềukiện, không kết luận thực nghiệm hômnay.

NếuSVcầnclaim “GM tươngđương0” hoặcMVcần “GS khôngcógiátrị”, phải preregister
tiêu chí/measure/error/multiplicity phùhợp trướcCF; khônglénthêm điều kiện vào
hai card gốc để đủdouble dissociation. Không có quyết định thêmconjunction tạiđây.

BaselineSV/SUB cần support/rho policy riêng trước khi áp DL-104-style wording;
hai MVpointsL4.4 không được chuyển thành kết quảbaseline cho vùngA/AB.
P0-V10/Understanding/L8/G1 vàHOLD L4.3/L4.4 giữtrạngthái hiệncó.
