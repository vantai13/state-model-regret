# L4.4-A1 — Sửa đặc tả sanity sau HOLD tại X2000 (design revision, không nới ngưỡng)

Người phụ trách: **Doan Van Tai**. Provenance: AI (Claude) soạn; **tác giả quyết** trong `author_choices.json`.
Trạng thái thật nằm trong file đó, không nằm ở đây.

## Vì sao sửa (nêu được mà không cần nhắc tới R_M, Ḡ_S^θ hay verdict nào)

1. Engine tính ô 00/01 trên lưới snapshot cũ + posterior, ô 10/11 trên lưới state hiện tại
   (`population.side`: hai lời gọi `quadrature.build`). Sai lệch giữa hai lưới **không** nằm trong
   `cost_error` (row tự ghi `quadrature_error = ... not a certified total error interval`).
2. Sanity gốc so L̄00^θ (lưới cũ) với L̄11 (lưới hiện tại) bằng sai số số học → so khác tuyến bằng
   ngân sách sai. DL-095 đã thay đúng loại kiểm này bằng TOL_NUM × C̄ref cho numerics đóng băng.
3. Bằng chứng read-only (`results/lessons/p4_a1/diagnosis/diagnosis.json`, Bước 0): row X2000 trùng bit
   ca calibration `CAL_CORNER_001` mà numerics đóng băng đã chấp nhận; trên 1298 row calibration
   (118 ca × 11 mức) bất đẳng thức **cùng tuyến** vi phạm 0 lần, **khác tuyến** 236/279 lần (≤ 0,111% C̄ref);
   luật gốc sẽ fail ở 17/33 điểm SH có row trùng tọa độ → HOLD là chắc chắn, không phụ thuộc kết quả khoa học.

## Đổi gì

| Trước (spec L4.4 §6) | Sau (A1) | Loại |
|---|---|---|
| Oracle bound L̄^θ + e ≥ L̄11 − e11 cho cả ô 00 và 10, kiểm TRƯỚC bit θ0 | Bit θ0 kiểm đầu tiên; L̄00^θ ≥ L̄01 và L̄10^θ ≥ L̄11 (cùng tuyến, sai số số học), mọi ρ | BUG → dừng |
| — | Ô gốc của engine: L̄00 ≥ L̄01, L̄10 ≥ L̄11 cùng tuyến | BUG → dừng |
| Mọi lỗi (sanity hay số) → HOLD toàn bộ | Lỗi số (lean `level_ready`, baseline R1/độ rộng) → điểm NOT_READY, ghi lại; dừng khi số NOT_READY > cap × N của vùng | NOT_READY |
| Raw `arithmetic_pass`/`validity_errors` | Chỉ báo cáo; khác tuyến đã do lean consistency (TOL_NUM) chấm | báo cáo |

Phân rã: L̄00^θ − L̄11 = (L̄00^θ − L̄01) + Ḡ_S|M1. Phần đầu là bất biến cùng tuyến;
phần sau là so hai quadrature, chấm theo lean TOL_NUM đã khóa. Đây là thay phạm vi bảo đảm, không phải
phép kiểm mới luôn chặt hơn: tại X2000, L01=L00<L11 nên sàn số mới thấp hơn sàn cũ. Chưa xác nhận
nguyên nhân gốc của sai lệch tích phân hoặc loại trừ mọi bug trong engine.

## Không đổi

Lưới ρ, công thức argmin và tie rule theo vùng, luật đọc DL-104, 90 điểm đăng ký, luật benchmark
(đầu/cuối mỗi vùng, cùng 4 điểm cũ), luật budget, engine/card/CF/numerics. Nếu cap NOT_READY>0 được
duyệt, lựa chọn và mô tả áp dụng trên tập READY: đó là đổi phạm vi so với yêu cầu đầy đủ scope của
DL-104, phải báo N/N_ready và mọi điểm loại riêng. Không suy kết quả tập READY sang toàn vùng.
Hồ sơ HOLD cũ giữ nguyên byte (prereg A1 khóa hash của chúng).

## Kết quả nào bác bỏ chẩn đoán

Bất kỳ vi phạm **cùng tuyến** nào ở bất kỳ điểm/mức/ρ nào → chẩn đoán sai, đó là bug → dừng, điều tra.
