# LETTER-TRUNC-N2 — kết quả phase 1

Người phụ trách: **Doan Van Tai**. Nhánh `letter`; brief khớp byte với HEAD trước triển khai và ở kiểm tra cuối.

Đã tạo `experiments/letter/trunc_n2.py`, `experiments/letter/trunc_n2_gcp.sh`, `tests/test_letter_trunc_n2.py` và outputs dưới `results/letter/trunc_n2/`. Không sửa file có sẵn trước nhiệm vụ, không commit/SSH/network; không chạm paper workspace song song.

Runner dùng một process pool, ưu tiên regime theo W1b CPU giảm dần, rồi các chain-V jobs → prepare → năm age jobs. Dùng nguyên saved case, levels, tau/order/labels và horizons; giữ `disagree=False`. Wrapper vá và khôi phục `choose_N` cùng identity aliases trong các module của code path. Guard kiểm N của từng chain ở từng age.

Comparator phân loại rõ percentage-pp / relative / discrete, xuất tên field và arg-max; không bỏ qua missing/extra, unknown numeric field gây lỗi. Tie masses/shares là continuous; flags, decisions, counts và stationary decisions là discrete. Relative denominator là trị tuyệt đối baseline, không epsilon floor; zero reference thay đổi được ghi `infinity`. Ngưỡng card giữ nguyên.

Kiểm chứng: `python3 -m pytest -q tests/test_letter_trunc_n2.py` → **21 PASS, 0 FAIL, 3.55 s**; `bash -n experiments/letter/trunc_n2_gcp.sh` PASS; `sha256sum --check --strict results/letter/trunc_n2/manifest.sha256` → **5/5 OK**. Pytest cache bị tắt và temporary files nằm trong output được phép.

1×N: **5,830 numeric leaves** khớp W1b, **max relative difference = 0**, threshold `1e-12`; N cũng được kiểm; không thiếu/thừa field và discrete values khớp. CPU/wall/time/SHA operational không phải scientific numeric leaves. Lượt pytest cuối đọc lại artifact 1N và kiểm SHA, không chạy lại truth.

Pilot timing: `python3 -m experiments.letter.trunc_n2 pilot --n-scale 2 --workers 4`; một regime `Za7p5_u1-2_lA17-2_x-2_k1-20`, năm saved ages × bảy horizons; 1N trong integration test dùng cùng bốn workers. Không chấm hoặc báo khác biệt khoa học 2N–1N.

| Component | 1N CPU-s | 2N CPU-s | Ratio 2N/1N |
|---|---:|---:|---:|
| Chain V | 11.672873 | 15.651865 | 1.340875 |
| Prepare, chưa gồm V | 0.140286 | 0.159793 | 1.139053 |
| Tổng năm ages | 2.791477 | 4.472037 | 1.602032 |

1N: 14.604637 task CPU-s / 5.099869 regime wall-s; 2N: 20.283694 task CPU-s / 7.299375 regime wall-s. Task CPU loại IPC; run_summary lưu thêm worker-process CPU và coordinator CPU. RSS đo được: 1N max-worker HWM 78,760 KiB; 2N 64,192 KiB. Parent pytest và CLI có baseline RSS khác nhau; không diễn giải hai số RSS này như memory scaling.

Dự phóng từ saved W1b 11071.664483 CPU-s: toàn bộ 27 regime ở 2N **16155.311154 CPU-s** (4.4876 CPU-h). Heaviest `Za7p5_u3-2_lA31-4_x1-3_k2` có critical path **3585.360991 s** (59.7560 phút), giả sử các chain-V và age jobs chạy song song. Đề xuất n2-standard-32: **32 workers**, cap **10800 s (3 h)**; script chưa chạy.

Peak RSS ước lượng cho heaviest 2N: **304.354 MiB/process**. Mô hình linear từ 4728 tới 101424 tổng chain states: base + (pilot_peak − base) × heavy_states/pilot_states. Không phải aggregate RSS đo trên heaviest. Sáu bản sao theo mô hình này (coordinator + tối đa năm age workers) khoảng 1.783 GiB, chỉ là envelope ước lượng, chưa gồm IPC/allocator khác.

Hạn chế dự phóng: chỉ một pilot nhẹ trên máy local, không có CI hay bảo đảm cho GCP. Chỉ heaviest W1b có saved per-chain V CPU; 26 regime serial phải tách saved prepare bằng tỷ phần V đo ở 1N pilot. Estimator overhead cũ bị loại vì dùng fixed levels. Không chạy thêm regime nặng để cải thiện ước lượng.

Hai lỗi kỹ thuật ban đầu được giữ nguyên evidence: (1) pytest temporary parent chưa tồn tại, đã tạo; (2) adapter V truyền rational string vào float, dừng trước evaluation/reproduction comparison. Đã giữ source/manifest/run_start/run_summary ở `pilot/failed_before_evaluation_01/`, sửa adapter mới sang Fraction đúng đường serial, rồi kiểm số học 1N PASS. Không thay tolerance, card, W1b hay evaluator.

Kiểm cuối: **128/128 protected files** giữ SHA, `git diff --stat` và staged diff đều rỗng, HEAD không đổi, không có new file ngoài allowlist (hai thư mục pytest có sẵn được giữ).

Artifacts chính:
- Source/tests: ba file mới nêu đầu báo cáo.
- Hashes: `manifest.sha256`, `initial_state.json`, `verification.json`.
- Test log cuối: `pytest_verified.log`; lịch sử lỗi: `pilot_unit_tests.log`, `pytest.log`.
- 1N check: `pilot/n1_Za7p5_u1-2_lA17-2_x-2_k1-20/code_path_check.json`.
- Raw và receipts: `pilot/n1_Za7p5_u1-2_lA17-2_x-2_k1-20/` và `pilot/n2_Za7p5_u1-2_lA17-2_x-2_k1-20/` (mỗi nơi có `raw/<id>.json`, `run_start.json`, `run_summary.json`).
- Timing log: `pilot/n2.log`; metrics/dự phóng: `pilot/projection.json`; bảng từng age: `pilot/timing_report.md`.

Chưa chạy full 27-regime 2N, chưa có full-run `raw/`, `compare.json`, `compare.md` hay `gcp_run.log`; comparator JSON/Markdown chỉ được test bằng synthetic fixtures. Chưa kết luận truncation PASS/FAIL. Không tạo CSV hoặc biểu đồ.
