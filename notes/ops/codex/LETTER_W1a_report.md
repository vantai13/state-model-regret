Đã hoàn tất W1a trên **61 regime**, seed **1000001**, **N=500, K=128**, đủ lưới τ/h. Không commit hoặc SSH; **28.829 file được bảo vệ giữ nguyên SHA256**.

Tại **h=30·T_int**, bảng dưới ghi **exact tie / zero-zero (%)**. Relative tie 1e−9 trùng exact tie trên toàn bộ lưới.

| Pipeline | Abilene, 32 regime | GÉANT confirmatory, 17 regime |
|---|---:|---:|
| M0_new | 51,362 / 51,362 | 48,012 / 47,047 |
| M0_old | 1,633 / 1,633 | 4,106 / 4,103 |
| P_old | 51,417 / 51,417 | 47,753 / 46,703 |
| CE_old | 2,072 / 2,072 | 12,526 / 12,447 |

Kết quả P1–P6:

- **P1 — HELD:** 28/32 regime đạt, yêu cầu ≥24.
- **P2 — DID_NOT_HOLD:** 0/17 đạt; kết quả này giữ ở mọi h đã kiểm.
- **P3 — phụ thuộc cách gộp:** pooled **1,633% <5%**, nên HELD; nhưng **54/768 cells ≥5%**, nên DID_NOT_HOLD nếu yêu cầu từng cell.
- **P4 — DID_NOT_HOLD theo nghĩa fresh/stale luôn trùng action:** 0/33. V̂ saturation và quyết định bất biến theo h của từng policy đều **PASS 33/33**, sai khác V̂ bằng **0**.
- **P5 — HELD trên numerical grid:** 33/33 regime.
- **P6 — DID_NOT_HOLD:** 0/33; bound nằm trong **380,387–1.618,461 T_int**, vượt 30.

**bar_h/T_int = 16,803–18,162**. Đây là kiểm tra trên finite grid và truncated state spaces, chưa chứng minh mọi h hoặc infinite-buffer lemma.

Saved CTMC tables có **5.768 rows**. Sign agreement là **4.646/5.144 = 90,319%**; 498 mismatch đều do s=0 và sai số floating point của s_mm1, không có hai dấu nonzero trái nhau. Với h/T_int≥15, median regret M0_new/old là **6,5483 / 2,5500 % C_ref**; hybrid_new/old là **3,37e−12 / 3,55e−11 % C_ref**.

Đã chạy lệnh yêu cầu:

```bash
python3 -m pytest -q tests/test_letter_w1a.py tests/test_ev_te.py --basetemp=/tmp/lw1a_pt -o cache_dir=/tmp/lw1a_cache
```

**35 tests PASS trong 3,42 giây**. Recount **5.856 cells: 0 mismatch**; lock EV-TE PASS. Tổng timed analysis CPU: **3.167,246 giây**; wall topology main **746,365 giây**, chưa gồm toàn bộ startup/import, hash/report và pytest.

File đã tạo và kết quả:

- Source: [ties_topology.py](/home/vantai/state-model-regret/experiments/letter/ties_topology.py), [lemma_check.py](/home/vantai/state-model-regret/experiments/letter/lemma_check.py), [ctmc_saved_tables.py](/home/vantai/state-model-regret/experiments/letter/ctmc_saved_tables.py), [w1a_report.py](/home/vantai/state-model-regret/experiments/letter/w1a_report.py), cùng `__init__.py` và [test mới](/home/vantai/state-model-regret/tests/test_letter_w1a.py).
- [Báo cáo đầy đủ, bảng và commands](/home/vantai/state-model-regret/results/letter/w1a/README.md).
- [Topology CSV](/home/vantai/state-model-regret/results/letter/w1a/topology_ties.csv), [lemma JSON](/home/vantai/state-model-regret/results/letter/w1a/lemma_checks.json), [CTMC tables JSON](/home/vantai/state-model-regret/results/letter/w1a/ctmc_saved_tables.json).
- [Test log](/home/vantai/state-model-regret/results/letter/w1a/pytest.log), [verification](/home/vantai/state-model-regret/results/letter/w1a/verification.json), [CPU](/home/vantai/state-model-regret/results/letter/w1a/cpu_times.json).

Không tạo biểu đồ; card và cấu hình gốc giữ nguyên. Các điểm mơ hồ của P3/P4 được ghi rõ, chưa suy ra causal explanation cho topology harm.