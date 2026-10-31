# SUB_PROBE — Probe phân giải số ở κ/τ = 1/20 (chỉ khi tác giả chọn phương án B)

Người phụ trách: **Doan Van Tai**. Provenance: AI (Claude) soạn; **tác giả quyết** trong `author_choices.json`.

- Câu hỏi: ở κ/τ = 1/20, làm mịn dt (ref 8) có đưa C̄ref về đạt R1 không, và tốn bao nhiêu CPU? Đây là việc
  "numerics coverage cho frame mới" của L4.7, kéo lên sớm vì bộ lọc khả thi của L4.5 cần nó.
- Vì sao ref chứ không K: ở XM2X000 trục K đã hội tụ (chênh C̄ref 0,002%); toàn bộ lỗi nằm ở trục dt (0,31%).
  Thang R3 của card v2 tăng K trước, nên bước đầu không cứu được một điểm bị giới hạn bởi dt.
- Không chứng minh: bất cứ điều gì về hiệu ứng SUB; mọi điểm κ = 1/20 khác ngoài các điểm probe.
- Kết quả của probe chỉ được dùng qua `region_decision_rule` đã khóa trước khi chạy.
