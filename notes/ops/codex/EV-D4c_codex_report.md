Đã triển khai brief và Amendment, chỉ tạo ba file:

- [ev_d4c_panel.py](/home/vantai/state-model-regret/experiments/ext_validity/ev_d4c_panel.py): đủ các commands, selection C–L, scoring và kiểm lock.
- [ev_d4c_pipeline.sh](/home/vantai/state-model-regret/experiments/ext_validity/ev_d4c_pipeline.sh): hai stage train/test, retry và xử lý lỗi.
- [test_ev_d4c.py](/home/vantai/state-model-regret/tests/test_ev_d4c.py): tests nhanh và smoke test.

Đã chạy trong `.venv` cùng `env.sh`:

| Command | Kết quả |
|---|---:|
| `pytest -q tests/test_ev_d4c.py`¹ | **34 PASS — 2,73 s** |
| `pytest -q tests/test_ext_packet.py`¹ | **22 PASS — 7,61 s** |
| `bash -n experiments/ext_validity/ev_d4c_pipeline.sh` | **PASS** |

¹ Có thêm options tắt cache và lưu pytest artifacts trong `/tmp`. Lượt đầu có một FAIL do fixture biểu diễn biên 0,5 bằng số thực; đã sửa fixture, giữ nguyên ngưỡng scorer.

Smoke trên **SER_L, τ = 0,8 s**, `train_T=200 s`, `n_inst=16`, seed `15000`:

- `train` và `simulate` trả output hữu hạn, đủ **8 twins**.
- `T_int = 4,919184 s`; CPU lần lượt **0,038 s / 0,015 s**.
- Xác nhận `ts−tau` dùng tuổi **0,8 s**; `max(TAU, …)` chỉ đặt spacing.

Các lựa chọn khi CARD chưa nói rõ: nhánh H3 `L=WORKS` áp dụng “H=any”; T_int trong `describe` tổng hợp main train cases; increment ratio có mẫu số 0 ghi `null`; quy tắc `n<10` áp dụng cả D6.

Ước lượng tối đa **540 trains và 960 tests**. Theo mốc EV-D4b trong brief, riêng test khoảng **66 phút trên 32 vCPU**, nhân với tỷ lệ T_int trung bình mới/cũ, giả sử scaling lý tưởng. Chưa đo full probe train C/L nên chưa ước lượng tổng train.

Log và bằng chứng:

- [EV-D4c tests](/tmp/ev-d4c-final-tests.log), [packet tests](/tmp/ev-d4c-packet-tests.log)
- [JSON kiểm chứng, smoke metrics và SHA256](/tmp/ev-d4c-verification.json)

**7/7 file gốc được đối chiếu SHA256 giữ nguyên**, gồm CARD và `packet.py`. Chưa tạo CSV/JSON kết quả panel; chưa commit, SSH hoặc chạy full panel. Implementation đã kiểm chứng kỹ thuật; các hypothesis chưa được kiểm nghiệm.