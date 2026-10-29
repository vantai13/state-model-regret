# Lesson 3R.7 — giải thích bằng ngôn ngữ đơn giản

Người phụ trách: **Doan Van Tai**.

Bài này chuẩn bị một phép kiểm chứng mới cho hai dự đoán đã viết ở bài trước:
thông tin về mô hình giúp quyết định trong miền nào, và thông tin trạng thái
có thể làm quyết định tệ hơn trong miền nào. Bài 7 chưa phải lần chạy confirmation
để kết luận hai dự đoán đó đúng hay sai; lần chạy ấy thuộc Phase 4.

Ba sản phẩm cần có là: số tình huống sẽ kiểm tra; danh sách tình huống được sinh
một lần và khóa trước khi thấy kết quả; cách chạy và chấm đã được kiểm tra.
Giống chuẩn bị một kỳ thi: chọn đủ câu hỏi, niêm phong đề và kiểm tra thang điểm
trước ngày thi. Test phần mềm qua không có nghĩa dự đoán nghiên cứu đã đúng.

Trước khi chốt số tình huống, cần đo thời gian cho một tình huống và kiểm tra
độ chính xác của phép tính. Hệ thống tính cũ chưa chứng minh được hai điều này
cho toàn bộ phạm vi mới. Công việc kéo dài chủ yếu ở phần bổ sung và kiểm lại
hệ thống tính này, không chỉ ở việc tạo danh sách của bài 7.

`HOLD` nghĩa là một điều kiện chưa đủ để đi tiếp. Cụ thể ở đây: chưa khóa được
mức tính số sau kiểm tra độ chính xác, nên chưa được chốt số mẫu, cấp seed và
sinh danh sách confirmation. HOLD không tự có nghĩa máy yếu, cũng không có
nghĩa giả thuyết nghiên cứu bị bác bỏ.

Một ca đang kiểm được tính ở ba mức: mức chính; mức ít điểm đại diện hơn; mức
bước thời gian lớn hơn. Nếu kết quả thay đổi quá ngưỡng đã khóa, phải ghi chưa
đủ chính xác. Không được nới ngưỡng hoặc bỏ ca khó để có PASS.

Ở đợt full02, ca hoàn tất lâu nhất mất 254,67 giây thời gian thực và dùng tối đa
khoảng165 MiB RAM. Ca dừng vì sai số xác suất dùng khoảng134 MiB, không chạm giới
hạnCPU/RAM. Vì thế lỗi dừng đó nằm ở phép tính/chứng nhận sai số; tăng RAM không
tự sửa được. Những lần giới hạnCPU trước đó là các lần chạy khác, vẫn giữ lịch sử.

Một kết quả tốt của bài 7 là có thiết kế khóa đầy đủ và biết rõ độ chính xác,
chi phí và giới hạn của phép thử. Kết quả nghiên cứu sau này có thể ủng hộ hoặc
bác dự đoán; cả hai đều có giá trị nếu phép thử hợp lệ. Điều tệ là báo hoàn tất
khi chưa kiểm đủ, giấu ca thất bại hoặc sửa tiêu chuẩn sau khi thấy kết quả.

Trạng thái chạy thực tế và log cập nhật nằm trong
`results/lessons/l3r_7/full_numerics/`; raw full02 nằm trong
`results/R3R_population_numerics/20261029_02/`. Các con số trên là snapshot full02,
không thay cho kết quả cuối của đợt full03 đang kiểm lại.
