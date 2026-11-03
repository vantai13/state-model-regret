# L7.1 — CTMC MMPP/M/1 (ctmc-v1): nhật ký và tổng kết

Doan Van Tai — **AI (Claude) thiết kế, chạy và soạn theo ủy quyền** ("thực hiện theo hướng dẫn và bạn tự chạy đi",
03/11/2026). Exploration trên nhánh `explore/ctmc-phase7`, không phải author-self, không phải confirmation của
contract v1.3, không phải claim novelty. Tác giả không ghi dự đoán riêng ở mục 9 lesson.

## Nhật ký theo stage

- **A setup.** Worktree ngoài repo `/home/vantai/smr-ctmc`, nhánh `explore/ctmc-phase7`. Hai máy (local 10 lõi AMD,
  GCP 8 vCPU Xeon), cùng Python/numpy/scipy/g++ ([env.json](env.json)). Lesson ghi gcp1 + gcp2; chỉ có một VM.
- **B evaluator + control.** [SPEC.md](../../experiments/explore_ctmc/SPEC.md) viết trước code; 17 test
  ([tests/test_explore_ctmc.py](../../tests/test_explore_ctmc.py)). π của chain cắt khớp nghiệm matrix-geometric của
  queue vô hạn ≤ 1e−11. V3 Monte Carlo đầu-cuối (10⁵ episode, CRN) đạt ở cả 3 regime, |z| ≤ 1,7; G_S và S lệch
  10–32 SE khỏi 0, M lệch 4–11 SE; G_M gần 0 ở horizon ngắn nên V3 yếu với G_M.
  - **V7 attempt01 trượt:** hai máy lệch ở bit cuối vì numpy/OpenBLAS chọn kernel SIMD khác nhau (AVX-512 chỉ có trên
    GCP). Sửa: `env.sh` chung, `det_expm1`. Kết quả attempt01 giữ ở `controls/attempt01/`.
  - **Phát hiện khi tìm lỗi V7:** ở horizon ngắn, gap của M0 triệt tiêu chính xác khi cả hai queue không chạm 0
    (−u·h²/2 + u·h²/2); dấu đang do làm tròn quyết định, khối lượng tới 0,89. Sửa thành luật hòa chính xác (Stay),
    như certified tie của contract. Đây là bug thật của evaluator, bắt được trước khi tính truth trong miền khoa học.
  - Control chạy lại toàn bộ sau sửa (attempt03); lượt dừng giữa chừng ghi ở `controls/attempt02_killed/`.
- **Exposure trước khóa.** Lệnh đo thời gian in truth của 3 regime (T1–T3, liệt kê trong
  [PREDICTIONS_bridge.md](PREDICTIONS_bridge.md)); chúng bị loại khỏi mọi tập chấm.
- **C khóa dự đoán.** [PREDICTIONS_bridge.md](PREDICTIONS_bridge.md) + check_bridge.py,
  [PREDICTIONS_asymptote.md](PREDICTIONS_asymptote.md) + check_asymptote.py + số đóng băng; sha256 trong
  [locks.json](locks.json).
