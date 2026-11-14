# Thẻ: c_sw > 0 ở vùng harm — dự đoán zero-fit (khóa và commit trước truth)

Doan Van Tai — **AI (Claude) soạn và khóa theo ủy quyền** ("tự thiết kế và kiểm tra thí nghiệm giúp tôi… bằng chứng
thật mạnh", 14/11/2026). Không phải dự đoán do tác giả viết, không mentor review. Thiết kế:
[DESIGN_CSW_HARM.md](DESIGN_CSW_HARM.md).

## 1. Dự đoán

Dự đoán là **720 con số** z_pred1(regime, c, h) trong [predictions_csw_harm.csv](predictions_csw_harm.csv).
- Chúng do `ctmc.evaluate_m0` tính, chỉ từ M0 và phân phối dừng, trước mọi truth của panel này.
- Sha256 nằm trong [lock_csw_harm.json](lock_csw_harm.json). Bản khóa được commit Git trước khi chạy truth.
- Test `test_predictions_reproduce_bitwise` tính lại được đúng từng bit.

Tóm tắt những gì luật dự đoán (đếm từ file, không có truth):

| Đại lượng (h ≥ 3 T_int, c > 0, 450 ô) | Luật nói |
|---|---|
| Ô mà c đổi harm ≥ 0,25 pp (tập S2) | 288; harm **giảm** ở 169, **tăng** ở 119 |
| Ô đổi dấu so với c = 0 (tập S3) | **0**, nên S3 sẽ NOT_EVALUABLE |
| Ô có harm ở c = 0 (≤ −0,25 pp) | 67 (regime, h), thuộc 24 regime |
| Trong đó harm mất ở c = 1/4 / 1/2 / 1 / 2 / 4 | 4 / 5 / 5 / 4 / 9 trên 67 |
| Trung vị z ở các ô đó, c = 0 → c = 4 | −4,10 → −2,96 %Cref |

Như vậy luật nói ngược với K7 nghĩa đen: ở vùng harm, switching cost **không** xóa harm. Có chỗ nó còn làm harm tăng.

## 2. Chấm (như design §4; dung sai thừa kế)

- **S1:** |G_S − z_pred1| ≤ 0,1 pp ở ≥ 90% của 450 ô.
- **S2:** trên 288 ô, trung vị sai số của luật ≤ 0,5 × trung vị sai số của null thực nghiệm G_S(0, h), **và** luật gần hơn ở ≥ 80% ô. Hướng thay đổi (tăng/giảm harm) chỉ báo mô tả.
- **S3:** NOT_EVALUABLE (0 ô). Theo luật cài sẵn, không thêm c.
- **K7:** mô tả, so tỷ lệ harm mất theo truth và theo luật.
- **Control:**
  - ≥ 90% của 180 job COMPLETED;
  - F_old/F_new ở h = ∞ và z_∞ khớp ≤ 1e−9;
  - tỷ lệ Switch M0 ở từng h khớp ≤ 1e−9;
  - MC 6 ô: |z| ≤ 3,5.

  Một control fail thì mọi verdict INCONCLUSIVE.
- Một run, không chạy lại, không đổi ngưỡng.

## 3. Những gì đã thấy trước khóa (không có truth nào)

- Panel đầu (seed 20261117) bị bỏ vì trùng chuỗi Sobol với các panel trước.
- File dự đoán đầu bị bỏ vì lọc h ≥ 3 T_int bằng số thực bỏ sót các h làm tròn. Nay lọc theo bội của h.
- Cả hai bản bỏ được giữ (`discarded_*`).
- Chỉ đã nhìn các số đếm zero-fit ở mục 1.

## 4. Cách đọc

Như design §5.
- **S1 và S2 PASS:** cơ chế "gộp quyết định + bias" dự đoán đúng, trước truth, một can thiệp mới ở vùng harm, và thắng một baseline được dùng truth.
- **K7:** câu thay thế được đề xuất cho tác giả, kèm số.
