# A05-T — mở held-out đúng một lần (L3.7)

Người phụ trách: **Doan Van Tai**. Code do AI (Claude) viết theo ủy quyền trực tiếp
của tác giả cho L3.7; không phải bằng chứng tác giả tự viết hoặc đã đọc từng dòng.

| File | Vai trò |
|---|---|
| `gate.py` | Cửa một chiều: dòng quyết định đã commit cùng DL và exposure, danh sách ô đúng 10, thư mục output trống |
| `run.py` | Runner duy nhất. Không có CLI cho ô, dt, margin, metric hay mô hình |
| `invariants.py` | Bất biến tầng 1 (bug) và chẩn đoán khai trước (`DIAGNOSTIC_NOT_VERDICT`) |
| `rescore.py` | Chấm lại độc lập từ `grading_input.json`, không import scorer đã khóa |
| `decision.json` | Bản ghi quyết định không đảo ngược, kèm SHA nguồn đã đăng ký |

Thứ tự trong `run.py`:
1. `verify_frozen()`;
2. quyết định đã commit;
3. kiểm ID;
4. output trống;
5. manifest;
6. kiểm p_sw công khai ở ref 1 và 2 (lệch thì dừng trước cost);
7. engine dt 1/120 và 1/240;
8. validity và bất biến (fail thì dừng, không chấm);
9. `score_test.score`;
10. chẩn đoán.

R09/R10 không bao giờ tới engine.

Chạy: `.venv/bin/python -u -m experiments.A05_test.run --workers 6`, đúng một lần.
Kiểm lại: `.venv/bin/python -m experiments.A05_test.rescore results/A05_test/<run_id>`.
Sửa một bug validity sau khi đã chạy cần DL mới và bản ghi quyết định mới; gate không có công tắc chạy lại.
