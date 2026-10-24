# Sáu candidate claims và kết quả bác bỏ

Người phụ trách: **Doan Van Tai** · 24/10/2026. AI hỗ trợ; exposed trước commit.
PC1–PC6 tương ứng C1–C6 của lesson plan; không trùng C1–C10 của boundary v0.
PC1 được bổ sung ánh xạ VSS từ L2.2, không gọi phần bổ sung là dự đoán trước đọc.

| ID | Claim có phạm vi | Loại | Khi nào không đứng? |
|---|---|---|---|
| PC1 | Dưới G1–G5 của T03, GSgivenM1 bằng EVPPI(x\|y), GMgivenS1 bằng trung bình VSS(x) | Identity/framing | Có lỗi trong phép dẫn hoặc cách ánh xạ dưới cùng giả định; không phải hypothesis cần experiment bác bỏ |
| PC2 | Trong K2=M09–M12, (GS−GM)/Cref≥.01 ở từng ô | Characterization | Có ít nhất một ô không đạt hướng/ngưỡng sau tính sai số; chưa chạy |
| PC3 | Trong K3={M19,M21}, Γ/Cref>.005 ở từng ô; khả năng giải thích/dự đoán ngoài discovery phải kiểm riêng với null | Interaction candidate | Prediction K3 sai ở bất kỳ ô nào; nếu chỉ đạt K3 thì vẫn chưa chứng minh mechanism, cần kiểm PC4 |
| PC4 | Queue-dynamics explanation dự đoán tốt hơn threshold null với cùng thông tin và budget | Mechanism/null | Null tương đương hoặc tốt hơn theo metric/biên/split được khóa tại A05; các lựa chọn này còn deferred theo D25 |
| PC5 | Trong K5=M19–M22, GM/Cref≤.005 ở mọi ô; trong Q5=M01–M04 có ít nhất một ô GM/Cref≥.01 | Equivalence boundary | Có ô K5 vượt biên hoặc không ô Q5 nào đạt relevance; numeric error phải tính trước khi gán nhãn |
| PC6 | Trong K6={M17,M18}, fixed-M0 D22 split F=L00−Lcb0, V=Lcb0−L10 có V>0 và V>F | Conditional characterization | Có ô không đạt một trong hai bất đẳng thức; không diễn giải V thành lợi ích chỉ refresh backlog |

Các K là nháp exploratory do AI chọn trong hội thoại, chưa phải L3.3 preregistration.
Cref=Lstar cùng ô và dt; Cref=0 giữ absolute output và loại nhãn relative có lý do
theo D23. K2/K3/K5/K6 chỉ main cells; không đọc outcomes hoặc tái dùng held-out.
Không thay cell nếu dự đoán sai. Không suy hiệu ứng riêng kappa/quantile/eta vì
lambdaA thay cùng lát (so ở cùng độ khó). PC4 chờ A05, không tự chọn null dễ thắng.

Kiểm kết quả trên lưới chưa chạy. Tất cả toy L2.2/L2.3 chỉ kiểm toán học và code.
