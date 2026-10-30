# L4.4 — Đặc tả baseline để tác giả duyệt trước khi chạy

Người ký duyệt đặc tả: **Doan Van Tai** · 30/10/2026.
Provenance: **AI soạn, tác giả duyệt gói nguyên văn trong chat**.
Trạng thái: **ADOPTED_BY_AUTHOR_CHOICE** cho quyết định #1 DL-103.
Còn phải commit source/prereg trước plant run; không xác nhận author ownership.

Đã thấy: hai input L4.4; output L4.1–L4.3, gồm ba điểm native benchmark và
HOLD tại κ=.05. Chưa tính baseline trên bất kỳ điểm plant nào. Input đã cho
đáp án toys/synthetic tests; chúng không phải dự đoán độc lập của tác giả.

## 1. Claim và giải thích thay thế

| Claim | Giải thích thay thế | Baseline đề xuất |
|---|---|---|
| MV | Chỉ cần margin thay vì sửa model | Bθ trên S0M0; recovery R_M |
| SH | Tác hại chỉ vì M0 đổi đường với lợi dự báo nhỏ | Cùng θ trên S0M0/S1M0; GSθ và ΔL10 |
| Mọi claim | Controller có tốt hơn luôn Stay không? | Stay từ base; headroom và chênh với bốn ô |
| SV/SUB | Chưa chọn card, audit vùng A/AB còn HOLD | DEFERRED tới L4.3 được xử lý/L4.5; không chạy |

Giữ margin và Stay. Age-aware đã có ở S0 posterior Bayes theo T07 §2; không
implement estimator khác. Last-observation/current-metric/steady-state để Phase 8
vì khác câu hỏi/quyền thông tin hoặc không thêm bảo vệ cho claim hiện tại.

## 2. Controller và lưới đề xuất

`Switch iff forecast_M0 < -θ`, tie Stay, cùng hai action/objective/horizon,
c_sw=0. **θ chỉ đổi action, không cộng vào cost thật.**

`θ(c,ρ) = ρ · E[J_Stay(c)] = ρ · h · E[Q_A+Q_B]`.
Không dùng Cref/oracle để cấp thông tin cho controller; evaluator chỉ dùng Cref
để mô tả/tune offline như quy định bên dưới. S0 đã giả định biết luật plant.

Lưới ρ = **{0, 1/200, 1/100, 1/50, 1/20}** = {0; 0.5%; 1%; 2%; 5%}.
Lưới nhỏ có 0, cho thấy cả lợi/hại của margin, không thử thêm sau kết quả.

## 3. Luật chọn đề xuất: phương án (c), riêng từng vùng

- MV: tối thiểu hóa trung bình `(L00θ−L11)/Cref` trên mọi tọa độ discovery
  phân biệt trong Ω_MV⁺. SH: cùng công thức nhưng controller mục tiêu là L10θ.
- Mỗi tọa độ age1 phân biệt một phiếu; không lọc theo lớp/pilot effect hoặc chỉ
  chọn điểm có lợi. Hai vùng không chồng nhau; không để vùng đông điểm lấn vùng kia.
- Dùng row chính K640/ref4. Tính argmin bằng Fraction từ chuỗi số đã lưu; hòa
  đúng giá trị thì chọn ρ nhỏ hơn. Không thêm epsilon sau kết quả.
- Cùng ρ* và θ cho cả ô 00/10 của một regime khi tính GSθ. ρ* giữ cố định theo
  vùng ở Phase 5; θ còn phụ thuộc Stay của regime theo luật đã viết.
- Báo thêm ρ_best(c) và envelope theo controller mục tiêu của vùng. Đây là
  lựa chọn dùng evaluator cho từng điểm, chỉ là mô tả cận trên trên lưới.
- Báo độ nhạy argmin giữa ba mức và khoảng cách best/runner-up. Discovery là
  mẫu thích nghi, không ước tần suất population hoặc gắn p-value.

Lựa chọn (c) làm baseline mạnh ở từng claim. Chuẩn hóa khi tune tránh regime
có chi phí lớn áp đảo; normalization chỉ trong evaluator, không trong θ.

## 4. Luật đọc đề xuất — áp lại trên mô tả CF, không đổi verdict v2

- **MV:** nếu median R_M(ρ*) ≥ **1/2**, câu claim phải ghi “so với controller
  mean-field không margin; margin đơn giản lấy lại phần lớn lợi ích model trên
  các điểm đã kiểm”. R_M chỉ định nghĩa khi GM>0; báo số undefined/không phân
  giải mẫu số, không ép 0 hoặc bỏ âm. Nếu không đạt, chỉ nói lưới margin đã thử
  chưa lấy lại ít nhất một nửa theo luật này, không suy mọi baseline đều thua.
- **SH:** nếu median `abs(GSθ)/Cref` < **1/200** (=0.5%) **và** median
  `ΔL10 = L10θ−L10` < **0** (cost unit), thu hẹp thành “tác hại với controller
  không margin”. Báo kèm ΔL10/Cref, nhưng điều kiện median dùng đúng ΔL10 raw.
- Nếu margin không cải thiện controller mục tiêu (ΔL10≥0), không dùng việc
  GSθ nhỏ để kết luận mốc yếu; toy T-A là phản ví dụ. ΔL10=0 không đạt điều kiện
  cải thiện nghiêm ngặt. Không đánh đồng mô tả discovery với câu claim CF.
- Không thêm card baseline hoặc đổi metric/verdict card v2. Sau discovery,
  DL ghi lại đúng luật đã duyệt và ρ*; không đổi ngưỡng theo bảng kết quả.

## 5. Tập điểm và guard

`cases.json`: **18 Ω_MV⁺ + 72 Ω_SH⁺ = 90 tọa độ/90 aliases**, đọc từ CSV L4.1
có hash, amp6/c_sw0, age quy chính xác về1. Giữ mọi lớp, kể cả C/D/A trong hộp.
Không chọn hộp mới, không điểm mới hoặc A/AB ngoài hai vùng trên. Card v2 bounds
giữ nguyên. CF-v2 270 keys chỉ đọc để từ chối; R09/R10 bị chặn bằng exact6key.
Mỗi điểm còn phải đạt R1, không suy PASS chỉ vì thuộc frame calibration.

## 6. Numerics, sanity và resource — đề xuất trước outcomes

Physical code frozen không sửa. Hàm margin mới dùng lại mảng thật của side();
wrapper thu mảng trong đúng một lần evaluate gốc tại mỗi mức rồi tính margin.
Ba mức **(640,4),(320,4),(640,2)**, thread1, tối đa2workers; kết quả write-once.
Cache riêng, không ghi đè cache native của L4.3. Source/freeze/spec phải kiểm
trước engine import; resume kiểm receipt/spec/ID/params. Không CF evaluation.

- θ0: loss/error/ambiguity và ô00/10 trùng bit với pair_loss/evaluate gốc.
- θ đủ lớn: gap0, đúng base; u0: mọi ô bằng nhau (synthetic và mảng plant có
  exact zero-action certificate). Oracle bound phải đạt trong arithmetic errors.
- Bao lỗi base/margin scale trong ambiguity: θ_error=ρ·base_error, thêm roundoff
  khi ρ>0. θ0 giữ đúng đường tính gốc. Không gọi measured refinement là error bound.
- Native four-cell readiness dùng **lean frozen level_ready** (R1 đủ Cref/sáu
  contrast, arithmetic width ≤1/4000, lean consistency); lưu cả raw flags và
  phân biệt với strict raw-validity audit L4.3. Không tự sửa adapter/threshold.
- Baseline mới phải kiểm oracle bound, arithmetic width và cùng mức refinement
  ≤1/400 Cref cho L00θ, L10θ, GSθ và ΔL10 ở mỗi ρ; Stay/Cref cũng báo refinement.
  Đây là kiểm readiness mô tả mới, không đổi contract card.
- Sai sanity/numerics/source/guard ⇒ dừng schedule, giữ outputs, không tune/freeze
  ρ* từ subset chưa đủ. Không tự nâng K/ref hoặc nới dung sai sau HOLD.
- Benchmark cố định bốn tọa độ: first/last theo sorted physical key ở mỗi vùng.
  Chỉ nếu cả4PASS mới chốt budget:1.5×max bundle CPU mỗi vùng×N, cap8CPUh;
  budget commit trước full. Benchmark đã chạy được tính trong ngân sách full.
  Cap mỗi case1800CPU-s/2400wall-s/AS3GiB; full tối đa2workers.
- Trước plant cần spec/author choice/source manifests commit; synthetic sanity
  được phép với spec DRAFT đã commit, không sinh hoặc mở physical outcomes.

## 7. Dự đoán trước plant run — AI soạn thay theo ủy quyền trực tiếp

Tác giả yêu cầu nguyên văn: “bạn hãy đống vai trò là tôi và ghi cho tôi, đây là
mệnh lệnh”. Yêu cầu này thay việc tự viết được lesson khuyến nghị; không hỏi lại.
Hai câu dưới là forecast AI theo ủy quyền, không tác giả tự dự đoán độc lập.

**MV:** “Tôi dự đoán margin được chọn theo luật sẽ lấy lại ít nhất một nửa giá trị
model ở trung vị Ω_MV⁺, tức median R_M(ρ*) ≥ 1/2, vì lỗi clipping của M0 có thể
làm các lần Switch với lợi dự báo nhỏ trở thành các lần đổi sai.”

**SH:** “Tôi dự đoán tại ρ=1%, margin xóa ít hơn một nửa tác hại của state ở
trung vị Ω_SH⁺, vì margin nhỏ có thể không chặn được các dự báo lợi sai lớn;
ở ρ* được tối ưu, tôi dự đoán median |GSθ|/Cref vẫn ≥0.5%.”

Chấm forecast SH1 bằng median mức giảm harm theo điểm ở những điểm GS0<0:
`1 − max(0,−GSρ=1%)/abs(GS0)`; giữ cả số âm nếu hại tăng. Báo N, không dùng
như prevalence. Chấm toàn scope chỉ khi hoàn tất; partial thì NOT_EVALUABLE.
Không nâng Understanding/ownership từ hai câu này.

## 8. Trạng thái ký

Tác giả chọn nguyên văn **“Chọn gói đặc tả đã soạn (khuyến nghị)”** trước plant
run. Đây là author choice/approval trong chat, không chữ ký điện tử hoặc xác
nhận tự viết/tự hiểu. Forecast được AI soạn sau ủy quyền riêng, trước outcomes.
Xem `author_choices.json`. Không đổi bốn ô/card/contract hoặc gỡ HOLD L4.3.
