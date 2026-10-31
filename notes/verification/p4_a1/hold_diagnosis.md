# Chẩn đoán HOLD L4.3/L4.4 trước amendment A1 — 31/10/2026

Người phụ trách: **Doan Van Tai**. Provenance: AI soạn từ artifact đã commit, theo yêu cầu triển khai; không phải tác giả tự viết hoặc human review.

## Fact

Nguồn: `results/lessons/p4_a1/diagnosis/diagnosis.json` và `diagnosis.log`, 0 engine call.
1298 calibration rows: same-route violations 0/0; cross-route 236/279; độ âm lớn nhất 0.1107764%Cref.
118 main rows: raw-invalid28; G_SM25/G_S_M1 28. Sanity cũ fail17/33SH,0/16MV trùng calibration.
X2000 có saved decimal costs giống CAL_CORNER_001; chưa kiểm original in-memory binary bits.
XM2X000 có Cref-dt0.310539%>.25%; mức K đạt, trục dt chưa đạt. Calibration max0.0725669%.

## Inference — AI theo ủy quyền, không tác giả tự viết

Trên cùng các nút và trọng số không âm, a*d >= min(d,0) đúng từng nút, nên same-route controller bound kiểm được mà không cần certificate cho quadrature tổng.
OLD và CURRENT dùng quadrature riêng; arithmetic errors không bao tổng sai lệch tích phân. Vì vậy so cross-route bằng arithmetic errors chưa đủ cơ sở để phân biệt integration mismatch với bug.
Dữ liệu ủng hộ tách controller invariants khỏi readiness; nó chưa loại trừ bug trong hai đường tích phân. XM2X000 chứng minh một failure R1 theo dt ở một tọa độ, chưa chứng minh global kappa cutoff.
Đổi sàn L11 sang L01 không luôn chặt hơn: X2000 có L01<L11. Amendment thay phạm vi bảo đảm và phải khai rõ; không sửa tolerance để đạt PASS.

## Không được nói

Không gọi các báo động là đã chứng minh false positive, không nhận root cause đã giải xong, engine tuyệt đối đúng, hypothesis đúng hoặc realism/novelty. Refinement differences không là certified total error bounds.

## Hệ quả

Chuẩn bị L44_A1; SV combined native+baseline với đối chứng được khóa; SUB probe theo quyết định riêng. Không sàng hộp hoặc gọi CF. Cap NOT_READY>0 đổi selection sang READY subset và phải ghi phạm vi mới. P0-V10/L8/Understanding vẫn OPEN.
