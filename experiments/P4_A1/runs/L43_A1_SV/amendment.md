# L4.3-A1 (SV) — Audit vùng A bằng đúng thước của scorer, kèm baseline, sau HOLD tại XM2X000

Người phụ trách: **Doan Van Tai**. Provenance: AI (Claude) soạn; **tác giả quyết** trong `author_choices.json`.

## Vì sao sửa (độc lập với kết quả)

1. HOLD gốc ở XM2X000 (vùng AB, κ/τ = 1/20): chênh C̄ref theo dt 0,31% > 0,25% trong khi sáu contrast đổi
   ≤ 0,046851 pp theo đầy đủ R1 (riêng ratio-only tối đa 0,044061 pp). Calibration đóng băng (κ ≥ 1/10) có chênh C̄ref theo dt tối đa 0,073%; hai điểm vùng A
   đã chạy chỉ 0,004% và 0,001%. Một failure ở κ=1/20 chưa chứng minh failure hoặc readiness trên toàn vùng κ/τ≥1/5.
   → **Stop rule tách theo vùng ứng viên**: run này chỉ chứa hỗ trợ của SV; vùng AB (SUB) chờ quyết định riêng.
2. Validator gốc đòi raw `arithmetic_pass`, raw `validity_errors = []` và S07/S08 ở 10⁻⁹ pp trên cả contrast
   khác tuyến — chặt hơn scorer của confirmation (`frame_v2.adapter_result`: R1 + độ rộng ≤ 1/4000 + lean TOL_NUM).
   Trên 1298 row calibration, khác tuyến âm nhẹ 236/279 lần dù numerics đóng băng chấp nhận chúng.
   → **Validator = thước của scorer**; raw flag chỉ báo cáo. Nhãn, d, R6 giữ đúng logic L4.3 (`audit_compare`).
3. Luật sàng L4.5 đã khóa (624a9be) đòi, cho từng ứng viên, nhãn native **và** baseline + ρ policy trước khi
   đếm hộp; SV là thiết kế hai vùng nên cần nhãn native của **vùng đối chứng**, vốn không nằm trong scope L4.3.
   → Một run gộp (native + margin trên cùng lời gọi engine) cho SV+ và SV−.

## Đổi gì / không đổi

- Đổi: phạm vi (chỉ SV+ = vùng A của L4.3 trừ điểm niêm phong, SV− do tác giả chọn); validator; stop rule
  BUG vs NOT_READY (như L4.4-A1); cờ pilot/native > 0,25 pp thành phát hiện, dừng khi vượt cap × N.
- Không đổi: engine, ba mức, R1, ngưỡng ±1%, R6, TOL_NUM, lưới ρ, luật budget, mọi file L4.3 cũ (khóa hash).
- Không làm: vẽ hộp, tính p̂, chọn card, đụng CF/R09/R10.

## Kết quả nào bác bỏ giả định của amendment

Vi phạm cùng tuyến (BUG) bất kỳ; hoặc NOT_READY ở vùng A vượt cap — khi đó giả định "vùng A nằm trong
coverage của (640, 4)" sai và phải xử lý numerics trước khi dùng nhãn.
