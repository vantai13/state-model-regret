# E4 — rescore độc lập

Người phụ trách: Doan Van Tai. Triển khai AI-assisted từ brief; không import scorer/simulator.

**Kết quả đối chiếu: MATCH**. Brief `4b6ad702`, HEAD `48b4ce01ca81f709631e53782237496cfb5eb8fb`.

VM manifest: 340/340 SHA256; JSON→NPZ: 170/170; lock: 27/27.
17 regimes × 10 chunks × 50 = 8.500 instances; mỗi regime 500 ID duy nhất. Seed 3000001, pilot=false, onset_theta=0.5.
Kiểm integrity: 4287 checks, 0 lỗi; 374/374 file input/source giữ nguyên SHA trong lượt rescore.

| Test | Rescore độc lập | Locked | Ngưỡng share | Verdict độc lập / locked |
|---|---:|---:|---:|---|
| E4-1 | 134/153 (87.581699%) | 134/153 | 90% | FAIL / FAIL |
| E4-2 | 130/153 (84.967320%) | 130/153 | 90% | FAIL / FAIL |
| E4-3 | 14/17 (82.352941%) | 14/17 | 90% | FAIL / FAIL |
| E4-4 | 111/153 (72.549020%) | 111/153 | 80% | FAIL / FAIL |

E4-1: Hybrid-i |G_S|≤0,25%C_ref; E4-2: Hybrid-i regret≤0,5%C_ref ở cả hai phía; E4-4: Hybrid-ii cùng điều kiện regret. E4-3: agreement best action trên training.

| Bảng | Số dòng đối chiếu | Số fields | Sai khác |
|---|---:|---:|---|
| cells.csv | 6120 | 140760 | 0 (MATCH) |
| reductions.csv | 1224 | 15912 | 0 (MATCH) |
| regimes.csv | 17 | 119 | 0 (MATCH) |

So sánh từng field: rtol=1e-12, atol=1e-9 (math.isclose; max hai tolerance). Ô trống và fields phân loại kiểm riêng.

Cost/SE ở đơn vị Mb·time; fields pct ở %C_ref (sai khác là percentage points).

| Bảng | Field | Max abs difference | Max relative difference | Mismatch |
|---|---|---:|---:|---:|
| cells.csv | C_ref | 6.51925802231e-09 | 1.97457184372e-15 | 0 |
| cells.csv | E_stay | 9.31322574615e-10 | 2.18163992277e-16 | 0 |
| cells.csv | G_S | 4.65661287308e-10 | 1.99467877209e-14 | 0 |
| cells.csv | G_S_pct | 8.73114913702e-11 | 1.9567768143e-14 | 0 |
| cells.csv | G_S_se | 0 | 0 | 0 |
| cells.csv | G_S_se_pct | 7.27595761418e-12 | 2.08518606492e-15 | 0 |
| cells.csv | L_fresh | 9.31322574615e-10 | 5.36906635614e-16 | 0 |
| cells.csv | L_fresh_se | 0 | 0 | 0 |
| cells.csv | L_stale | 9.31322574615e-10 | 4.305140879e-16 | 0 |
| cells.csv | L_stale_se | 0 | 0 | 0 |
| cells.csv | N | 0 | 0 | 0 |
| cells.csv | h | 0 | 0 | 0 |
| cells.csv | h_mult | 0 | 0 | 0 |
| cells.csv | pipeline | 0 | 0 | 0 |
| cells.csv | regime | 0 | 0 | 0 |
| cells.csv | regret_fresh_pct | 4.07453626394e-10 | 2.0548002602e-15 | 0 |
| cells.csv | regret_fresh_se_pct | 7.27595761418e-12 | 2.08518606492e-15 | 0 |
| cells.csv | regret_stale_pct | 4.07453626394e-10 | 2.17482059736e-15 | 0 |
| cells.csv | regret_stale_se_pct | 6.36646291241e-12 | 2.00614130628e-15 | 0 |
| cells.csv | tau | 0 | 0 | 0 |
| cells.csv | tau_mult | 0 | 0 | 0 |
| cells.csv | tie_fresh | 0 | 0 | 0 |
| cells.csv | tie_stale | 0 | 0 | 0 |
| reductions.csv | M0_loss | 9.31322574615e-10 | 5.36906635614e-16 | 0 |
| reductions.csv | denominator_positive | 0 | 0 | 0 |
| reductions.csv | h_mult | 0 | 0 | 0 |
| reductions.csv | hybrid_loss | 9.31322574615e-10 | 3.13117101532e-16 | 0 |
| reductions.csv | hybrid_reduction | 1.39698386192e-09 | 2.63333545649e-12 | 0 |
| reductions.csv | level | 0 | 0 | 0 |
| reductions.csv | reduction_fraction | 5.39845945724e-15 | 6.59222341427e-14 | 0 |
| reductions.csv | regime | 0 | 0 | 0 |
| reductions.csv | reversed_minus_hybrid | 9.31322574615e-10 | 5.44223594072e-14 | 0 |
| reductions.csv | side | 0 | 0 | 0 |
| reductions.csv | tau_mult | 0 | 0 | 0 |
| reductions.csv | tie_loss | 9.31322574615e-10 | 5.36906635614e-16 | 0 |
| reductions.csv | tie_reduction | 1.86264514923e-09 | 6.58306242262e-14 | 0 |
| regimes.csv | CPU | 0 | 0 | 0 |
| regimes.csv | N | 0 | 0 | 0 |
| regimes.csv | chunks | 0 | 0 | 0 |
| regimes.csv | complete | 0 | 0 | 0 |
| regimes.csv | pilot | 0 | 0 | 0 |
| regimes.csv | regime | 0 | 0 | 0 |
| regimes.csv | seed | 0 | 0 | 0 |

Tie shares tính trực tiếp từ raw tie_flags, đối chiếu cả từng cell và pooled theo pipeline/side.

| Pipeline | Side | Ties / denominator | Raw share | Locked share |
|---|---|---:|---:|---:|
| Hybrid-i | fresh | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-i | stale | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-ii | fresh | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-ii | stale | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-noise_m25 | fresh | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-noise_m25 | stale | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-noise_m50 | fresh | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-noise_m50 | stale | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-noise_p25 | fresh | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-noise_p25 | stale | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-noise_p50 | fresh | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-noise_p50 | stale | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-reversed | fresh | 0/153000 | 0.000000% | 0.000000% |
| Hybrid-reversed | stale | 0/153000 | 0.000000% | 0.000000% |
| M0 | fresh | 72687/153000 | 47.507843% | 47.507843% |
| M0 | stale | 4602/153000 | 3.007843% | 3.007843% |
| M0-tie-i | fresh | 72687/153000 | 47.507843% | 47.507843% |
| M0-tie-i | stale | 4602/153000 | 3.007843% | 3.007843% |
| M0-tie-ii | fresh | 72687/153000 | 47.507843% | 47.507843% |
| M0-tie-ii | stale | 4602/153000 | 3.007843% | 3.007843% |
| M0-tie-iii | fresh | 72687/153000 | 47.507843% | 47.507843% |
| M0-tie-iii | stale | 4602/153000 | 3.007843% | 3.007843% |
| M0-tie-rand | fresh | 72687/153000 | 47.507843% | 47.507843% |
| M0-tie-rand | stale | 4602/153000 | 3.007843% | 3.007843% |
| M1_new | fresh | 504/153000 | 0.329412% | 0.329412% |
| M1_new | stale | 0/0 | N/A | N/A |
| Onset-hybrid-i | fresh | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-i | stale | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-ii | fresh | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-ii | stale | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-noise_m25 | fresh | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-noise_m25 | stale | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-noise_m50 | fresh | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-noise_m50 | stale | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-noise_p25 | fresh | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-noise_p25 | stale | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-noise_p50 | fresh | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-noise_p50 | stale | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-reversed | fresh | 0/153000 | 0.000000% | 0.000000% |
| Onset-hybrid-reversed | stale | 0/153000 | 0.000000% | 0.000000% |

Phân tích mô tả trên saved data; không đổi threshold, không truth run mới.

| Test | h/T_int=7 | h/T_int=15 | h/T_int=30 |
|---|---:|---:|---:|
| E4-1 | 32/51 | 51/51 | 51/51 |
| E4-2 | 28/51 | 51/51 | 51/51 |
| E4-4 | 28/51 | 41/51 | 42/51 |

| Pipeline (153 units) | Median abs(G_S) %C_ref | Median regret fresh %C_ref | Median regret stale %C_ref | abs(G_S)≤0,25 | Both regrets≤0,5 |
|---|---:|---:|---:|---:|---:|
| M0 | 63.649188 | 52.985959 | 13.977190 | 0/153 | 0/153 |
| M0-tie-i | 32.633621 | 17.448649 | 13.977190 | 0/153 | 0/153 |
| Hybrid-i | 0.000000 | 0.000000 | 0.000000 | 134/153 | 130/153 |
| Hybrid-ii | 0.000000 | 0.000000 | 0.000000 | 130/153 | 111/153 |

E4-3: best action (ii) khác (i) tại `G2_r80_b3_s1`, `G2_r80_b6_s0`, `G3_r80_b3_s1`.
Regret âm: 1187 cell-side values; nhỏ nhất -0.955381034663%C_ref; giữ nguyên dấu.

- Tên manifest trong brief là e4_raw_sha256.txt; artifact VM đã commit thực tế là raw_sha256_vm.txt (340 mục).
- G_S = mean(V_stale - V_fresh): âm nghĩa là telemetry fresh gây hại; quy ước khớp cells.csv, không đảo dấu.
- reduction_fraction = tie_reduction/hybrid_reduction khi mẫu số khác 0, kể cả âm; denominator_positive là cờ riêng. Có 264 dòng mẫu số âm, 204 dòng mẫu số 0. Tỷ số với mẫu số âm không diễn giải là phần lợi ích thu được. Bản check-only đầu của rescore bỏ trống 264 tỷ số mẫu số âm; đã sửa giả định này và thêm analytic test, không sửa locked CSV.
- SE dùng sample sd(ddof=1)/sqrt(500); SE của G_S và regret dùng chênh lệch ghép cặp trên cùng instance/CRN, không cộng SE hai phía.
- Giữ nguyên regret âm do M1_new dùng rollout quyết định độc lập; không clip về 0. M1_new không có stale: các ô trống được giữ là null.
- Dùng tau/h thực trong NPZ (đã làm tròn theo dt), và h_mult cho eligibility của card.
- onset_theta=0.5 chỉ descriptive theo addendum trước truth; không dùng các pipeline Onset trong E4-1..E4-4.
- 153 units dùng chung instances giữa age/horizon: đây là tỷ lệ trong panel, không phải 153 independent trials hoặc population CI.
- E4-3 là training-only đã biết trước truth. Rescore kiểm arithmetic của saved costs/decisions; không xác nhận simulator hoặc rollout estimator là ground truth chính xác.
- score.json có note chung 'No card: no E4 pass/fail verdicts.'; đây là mô tả trường hợp không có card, không phản ánh lượt này (card SHA hợp lệ, descriptive_only=false).

Lệnh đã dùng:

```bash
source .venv/bin/activate && source experiments/explore_ctmc/env.sh
PYTHONDONTWRITEBYTECODE=1 python experiments/letter/e4_rescore.py --self-test
PYTHONDONTWRITEBYTECODE=1 python experiments/letter/e4_rescore.py
```

Source: `experiments/letter/e4_rescore.py`. Outputs: `results/letter/e4/rescore_independent.json` và `.md`.
Không tạo CSV/log/biểu đồ/config mới; stdout hiển thị tóm tắt, JSON lưu số liệu, SHA và toàn bộ sai khác. Không commit, SSH hoặc sửa artifact cũ.
