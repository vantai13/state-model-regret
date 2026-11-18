# V7-3: held daytime reroute trên ma trận GÉANT thật, giờ hành chính nghẽn — báo cáo kết quả (Claude, 18/11/2026)

Người phụ trách **Doan Van Tai**.
- **Phân công:** card và phân tích do Claude viết theo ủy quyền của tác giả. Code, chấm điểm và rescore là của Codex.
- **Review:** chưa có mentor review hoặc dự báo của tác giả.
- **Trạng thái:** run một lần theo card là **INCOMPLETE**. Kết quả dưới đây là **phân tích sửa đổi DEVIATION 01**, không phải bản confirmatory gốc.

## Mốc commit
| Bước | Commit |
|---|---|
| Training nghẽn ρ=0,9 | 3b28b2c21 |
| Card + params + brief | 0f8ec8229 |
| Pilot | 61670742d |
| Code test-phase | d1bd41892 |
| Lock (28 input) | eba210194 |
| DEVIATION 01, trước khi đọc bất kỳ kết quả nào | a32137acd |
| Raw (147 records, sha ac182a3b…, khớp VM/laptop), trước khi chấm | 316a553ad |
| Chấm và rescore độc lập MATCH | 2e0fc828a |

## Chuyện gì đã xảy ra
- **Tiến độ run:** run trên n2-standard-32 (30 worker) xong 147/150 bản ghi trong 2 h 52 min.
- **Ba bản ghi còn lại** đều là ngày 2005-06-27:
  - tổng demand đạt 1 551 525 Mbit/s, gấp **19,64 lần** mức cao nhất của train;
  - ngày test cao thứ hai chỉ gấp 1,23 lần;
  - 51–52 link bị kích hoạt, so với 5–6 link ở các ngày quá tải bình thường;
  - ước tính khoảng 40 giờ cho mỗi bản ghi, vượt cap 6 giờ.
- **Quyết định của tác giả:** dừng run, ghi INCOMPLETE, rồi loại ngày bất thường bằng luật chỉ dựa trên input. Luật là tổng demand vượt 2 lần max của train; mọi ngưỡng trong khoảng 1,23–19,64 lần đều cho cùng kết quả.
- **Chi phí:** 44,3 CPU-h của records, wall 3,23 h.

## Kết quả kiểm định (DAY1/DAY2, tầng S, case evaluable, h ∈ {2,4,6} h)
| Kiểm định | Verdict | Số đếm | Ghi chú độ mạnh |
|---|---|---|---|
| H1: luật dấu của M0 | PASS | 20/22 case resolved | Độ phân giải thấp: 42/76 case nằm trong 2 se, 12 case F_EQUAL. Theo từng h: cả ba h đều NE vì < 20 case |
| H2: hybrid giữ regret ≤ 0,5% | PASS | 76/76 | Regret lớn nhất của hybrid là 0,0316% C_ref |
| H3: hybrid tốt hơn M0 ở chỗ M0 sai | PASS | 16/16 | 16 case chỉ đến từ **2 ngày** (2005-08-10, 08-11) × 2 regime, không độc lập |

Các case dùng chung ngày và instance, nên số đếm là mẫu số chứ không phải số phép thử độc lập.

## Dự báo của Claude (không phải kiểm định)
| | Dự báo | Kết quả |
|---|---|---|
| F1 | ≥ 60% ngày là tầng S | **Không đứng**: 29/50 (58%), 29/49 sau khi loại ngày |
| F2 | M0 fresh tệ hơn ở ≥ 60% case lúc 6 h | **Không đứng**: 12/32 |
| F3 | trung vị regret hai phía của M0 lúc 6 h ≥ 5% | **Không đứng**: 0% |
| F4 | hybrid và luật tĩnh trùng ≥ 99% quyết định | Đứng: 42 336/42 336 |
| F5 | tầng O: mọi pipeline ≤ 0,5% ở ≥ 80% case | Đứng tổng thể. M0 338/408 ≤ 0,5%, hybrid và luật tĩnh 408/408. M0 riêng ở 6 h: 86/110 (không đứng) |
| F6 | DAY3: trung vị \|G_S\| ≤ 0,5% | Đứng: 0% |
| F7 | tỷ lệ tie fresh ≥ 50%; harm còn lại khi phá tie ngẫu nhiên | Đứng: 86,4%; 84/84 |

## Phân tích (result-analysis)
1. **Harm xuất hiện theo đợt, không phổ biến.**
   - Trên 8 ngày S tính được của mỗi regime, M0 sai rõ chỉ ở 2 ngày liên tiếp (10–11/8). Regret trung vị 25,8% C_ref, cao nhất 53,1%; quy ra delay hàng đợi trung bình 5,4 ms, cao nhất 23,3 ms.
   - Các ngày khác: M0 vẫn giữ regret hai phía ≤ 0,5% (60/76 case confirmatory). M0 fresh hòa (tie) ở 87,5% quyết định, với trung vị tính theo case. Chưa tách xem regret nhỏ vì chi phí của hai action gần nhau hay vì tie rơi vào action đúng.
   - Dự báo F2/F3 sai vì Claude đã ngoại suy từ training (dấu ŝ 26/26) sang tần suất harm. Dấu của s đúng không có nghĩa là harm thường xuyên: harm chỉ xảy ra khi M0 chọn sai và chênh lệch chi phí đáng kể.
2. **Hiệu chỉnh chưa bao giờ làm tệ hơn.**
   - Hybrid với ŝ gộp từ tháng 5–6 trùng với luật tĩnh ở mọi quyết định (F4).
   - Trên test mùa hè, hybrid giữ regret ≤ 0,5% ở 76/76 case confirmatory. Ở tầng O (mô tả), M0 vượt 0,5% ở 70/408 case, hybrid 0/408.
   - Vì vậy kết quả cho thấy **dấu tốc độ dài hạn chuyển được qua các tuần**. Nó không kiểm được khả năng hybrid cân bằng Δ̂ và hŝ: với ŝ cỡ 10⁵ Mbit, hybrid luôn chọn Switch.
3. **Giữ quyết định thật sự là giữ lâu.** T_int của ngày test có trung vị 232 s (90–536 s; 72/76 case resolved), nên 6 giờ tương đương khoảng 90 lần T_int.
4. **Tầng S ít case tính được: 150/546.** Mùa hè tải thấp nên nhiều ngày không có hàng đợi. Đây là giới hạn về phạm vi và nhất quán với kết quả ban đêm và ban ngày đủ dung lượng: hiệu ứng cần mạng nghẽn.
5. **Giả định tổng hợp vẫn còn:**
   - capacity đồng đều đặt theo ρ=0,9 trên train;
   - buffer vô hạn;
   - điều biến OD nhanh (β=0,3).

   Ngày quá tải tạo backlog lớn không thực tế; vì vậy tầng O chỉ để mô tả.

## Cải tiến (bước mới, không thay verdict)
- Card về sau cho dữ liệu trace phải có **luật kiểm tra input** (spike so với train) và **pilot trên ngày input nặng nhất**.
- Muốn kiểm vai trò Δ̂ của hybrid thì cần một kịch bản có ŝ nhỏ so với Δ̂, ví dụ ŝ chỉ lấy từ tầng S: −320 Mbit. Phân tích độ nhạy 2 (Hybrid_S) đã có trong `score_dev1/cases.csv`; chưa đọc ở báo cáo này.

## Đưa vào paper (theo quy tắc đã khóa trong card)
Mục V của bản V7-3 thêm một đoạn gồm:
- cách chia train/test;
- ngày bị loại do lỗi đo;
- H1–H3 kèm mẫu số;
- harm của M0 tính bằng % và ms;
- hybrid và luật tĩnh trùng nhau;
- biến thể tie;
- DAY3 làm đối chứng;
- một câu về provisioned/night không có hàng đợi;
- một câu về tầng O.

Viết theo đúng mức của bằng chứng: harm theo đợt ở một số ngày nghẽn. Dòng ledger do Codex thêm, phần chữ do Argon viết.
