# E4b — rescore độc lập

Người phụ trách: Doan Van Tai. Triển khai AI-assisted từ brief đã commit.

**MATCH**. Brief `c7d26083a5a7aa315d6944d03ef112cecda81777`; HEAD khi chấm `ba7a258a0305c8d1d7bbbbb0e0a1a3594147a93f`.
Seed 5000001; pilot=false; onset theta=0.5. 17 regimes × 10 chunks × 50 = 8.500 instances; 500 ID duy nhất/regime.
VM SHA: 340/340; JSON→NPZ: 170/170; lock: 30/30.
Integrity PASS: 4508 checks, 0 lỗi; 384/384 inputs/source giữ SHA.

| Test | Rescore độc lập | Locked | Verdict độc lập / locked |
|---|---:|---:|---|
| E4-1 | 97/102 (95.098039%) | 97/102 | PASS / PASS |
| E4-2 | 90/102 (88.235294%) | 90/102 | FAIL / FAIL |
| E4-3 | 14/17 (82.352941%) | 14/17 | FAIL / FAIL |
| E4-4 | 81/102 (79.411765%) | 81/102 | FAIL / FAIL |
| X1 | fast 9/9; slow miss 8/8 | fast 9/9; slow miss 8/8 | HOLDS / HOLDS |
| X2 | 81/84 (96.428571%) | 81/84 (96.428571%) | HOLDS / HOLDS |
| X3 | rule2 0/102; median G_S -62.587723867%C_ref | rule2 0/102; median G_S -62.587723867%C_ref | HOLDS / HOLDS |

E4-1: |G_S|≤0,25%C_ref, share≥90%; E4-2: both regrets≤0,5%C_ref, share≥90%; E4-4: cùng regret rule, share≥80%. E4-3 training agreement≥90%.
E4-5/E4-6: DESCRIPTIVE ở cả hai scorer. X1 fast≥8/9 và slow miss≥6/8; X2≥90%; X3 rule2≤10% và signed median G_S≤−25%C_ref.

| Bảng | Rows | Fields | Mismatches |
|---|---:|---:|---:|
| cells.csv | 6120 | 140760 | 0 |
| reductions.csv | 1224 | 15912 | 0 |
| regimes.csv | 17 | 119 | 0 |
| merge.json.regimes | 17 | 119 | 0 |

So sánh từng field: rtol=1e-12, atol=1e-9 theo math.isclose (max hai tolerance); kiểm riêng ô trống, nhãn, boolean. Cost/SE: Mb·time; pct: %C_ref; sai khác pct: percentage points.

| Bảng | Field | Max abs diff | Mismatches |
|---|---|---:|---:|
| cells.csv | C_ref | 2.32830643654e-09 | 0 |
| cells.csv | E_stay | 9.31322574615e-10 | 0 |
| cells.csv | G_S | 1.16415321827e-10 | 0 |
| cells.csv | G_S_pct | 6.54836185277e-11 | 0 |
| cells.csv | G_S_se | 0 | 0 |
| cells.csv | G_S_se_pct | 5.45696821064e-12 | 0 |
| cells.csv | L_fresh | 9.31322574615e-10 | 0 |
| cells.csv | L_fresh_se | 0 | 0 |
| cells.csv | L_stale | 9.31322574615e-10 | 0 |
| cells.csv | L_stale_se | 0 | 0 |
| cells.csv | N | 0 | 0 |
| cells.csv | h | 0 | 0 |
| cells.csv | h_mult | 0 | 0 |
| cells.csv | pipeline | 0 | 0 |
| cells.csv | regime | 0 | 0 |
| cells.csv | regret_fresh_pct | 3.78349795938e-10 | 0 |
| cells.csv | regret_fresh_se_pct | 1.1823431123e-11 | 0 |
| cells.csv | regret_stale_pct | 3.78349795938e-10 | 0 |
| cells.csv | regret_stale_se_pct | 1.1823431123e-11 | 0 |
| cells.csv | tau | 0 | 0 |
| cells.csv | tau_mult | 0 | 0 |
| cells.csv | tie_fresh | 0 | 0 |
| cells.csv | tie_stale | 0 | 0 |
| reductions.csv | M0_loss | 9.31322574615e-10 | 0 |
| reductions.csv | denominator_positive | 0 | 0 |
| reductions.csv | h_mult | 0 | 0 |
| reductions.csv | hybrid_loss | 2.32830643654e-10 | 0 |
| reductions.csv | hybrid_reduction | 9.31322574615e-10 | 0 |
| reductions.csv | level | 0 | 0 |
| reductions.csv | reduction_fraction | 3.35287353437e-14 | 0 |
| reductions.csv | regime | 0 | 0 |
| reductions.csv | reversed_minus_hybrid | 9.31322574615e-10 | 0 |
| reductions.csv | side | 0 | 0 |
| reductions.csv | tau_mult | 0 | 0 |
| reductions.csv | tie_loss | 9.31322574615e-10 | 0 |
| reductions.csv | tie_reduction | 4.65661287308e-10 | 0 |
| regimes.csv | CPU | 0 | 0 |
| regimes.csv | N | 0 | 0 |
| regimes.csv | chunks | 0 | 0 |
| regimes.csv | complete | 0 | 0 |
| regimes.csv | pilot | 0 | 0 |
| regimes.csv | regime | 0 | 0 |
| regimes.csv | seed | 0 | 0 |
| merge.json.regimes | CPU | 0 | 0 |
| merge.json.regimes | N | 0 | 0 |
| merge.json.regimes | chunks | 0 | 0 |
| merge.json.regimes | complete | 0 | 0 |
| merge.json.regimes | pilot | 0 | 0 |
| merge.json.regimes | regime | 0 | 0 |
| merge.json.regimes | seed | 0 | 0 |

Phân tích mô tả saved data, không đổi verdict/threshold:

| Test | h/T_int=15 | h/T_int=30 |
|---|---:|---:|
| E4-1 | 46/51 | 51/51 |
| E4-2 | 45/51 | 45/51 |
| E4-4 | 39/51 | 42/51 |

| Pipeline (102 units) | Median signed G_S %C_ref | Median abs G_S %C_ref | Median regret fresh %C_ref | Median regret stale %C_ref | Rule2 |
|---|---:|---:|---:|---:|---:|
| M0 | -55.917244 | 64.555183 | 58.074045 | 12.098536 | 0/102 |
| M0-tie-i | -13.333858 | 32.165570 | 20.714106 | 12.098536 | 0/102 |
| Hybrid-i | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 90/102 |
| Hybrid-ii | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 81/102 |

Training ordering khác tại: G2_r80_b3_s1, G2_r80_b6_s0, G3_r80_b3_s1.
Giữ 684 regret âm, min -1.44007082427%C_ref; reduction mẫu số âm 256, mẫu số 0 226.

E4-1 trượt 5 units; phân bố theo h/regime và từng unit nằm trong JSON.
Hybrid-i có 9 units đạt |G_S|≤0,25% nhưng trượt rule 2: chênh lệch fresh/stale nhỏ không đảm bảo regret mỗi phía nhỏ.
Trong 21 units trượt Hybrid-ii, 18 thuộc các regime training ordering khác, 3 thuộc ordering đúng. Đây là phân rã mô tả, chưa chứng minh cơ chế hoặc instance noise.
Forecast E4-1 holds được giữ; forecast E4-2 holds không đứng; E4-3 FAIL đã biết trước truth; E4-4 forecast chỉ ghi borderline. X1/X2/X3 holds đều đứng.
Không fit/tune hoặc chạy thêm truth để cải thiện verdict; nhiệm vụ này chỉ kiểm chứng lại raw đã lưu.

- G_S = mean(V_stale - V_fresh); dấu âm nghĩa là fresh telemetry gây hại. Dấu khớp locked CSV.
- C_ref là mean chi phí action M1_new/fresh đã lưu; M1_new/stale không available. Giữ regret âm, không clip.
- Rule 2 dùng max(regret_fresh_pct, regret_stale_pct) <= 0.5, không dùng absolute regret hoặc SE allowance.
- SE = sample sd(ddof=1)/sqrt(500); regret và G_S dùng chênh lệch ghép cặp trên cùng instance.
- reduction_fraction = tie_reduction/hybrid_reduction nếu mẫu số khác 0, kể cả âm; denominator_positive là cờ riêng.
- Tau/h thực lấy từ NPZ (làm tròn theo dt); eligibility dùng h_mult. Onset theta 0.5 chỉ descriptive.
- E4b dùng 102 units ở h/T_int=15,30; không mang 153 units/h=7 của E4 sang verdict. E4-3 chỉ training seed 1.
- X1 dùng S8 đã định từ E4, không chọn lại theo E4b. X2 chỉ lấy 14 training argmin agreements; X3 dùng median G_S có dấu.
- 102 units dùng chung instances giữa ages/horizons, không phải independent trials; không tạo population CI.
- Rescore xác nhận arithmetic của saved decisions/costs và verdict, không xác nhận estimator/simulator là exact ground truth.
- training_checks.json giữ metadata source lịch sử, có hai SHA khác source lock hiện hành; byte copy E4 và lock E4b được kiểm riêng.
- score.json giữ note template 'No card: no E4 pass/fail verdicts.' dù card SHA hợp lệ/descriptive_only=false; đây là note không phù hợp lượt có card.

Metadata source lịch sử của training (không sửa):

```json
[
  {
    "path": "experiments/letter/e4_geant.py",
    "training_source_sha256": "5265c306660bbcb40bb8c884df5d324c46acffb8b3250ba246a57ae64831437e",
    "current_locked_sha256": "53035c71881180a973518c33aea3f8386e5588f75869e1681c695e90b6852b21"
  },
  {
    "path": "tests/test_letter_e4.py",
    "training_source_sha256": "2a6a3e410a3e5fc8f3b090e63f68fedf069fcfe1cc5e5af75d3a10670892758b",
    "current_locked_sha256": "9554e77a3c73e4f5750c5dc9108ca1b4159a3b2c53441946d6aad3a1f2ef110a"
  }
]
```

Tổng mismatches: 0.

Lệnh thực thi:

```bash
source .venv/bin/activate && source experiments/explore_ctmc/env.sh
PYTHONDONTWRITEBYTECODE=1 python -m experiments.letter.e4b_rescore --self-test
PYTHONDONTWRITEBYTECODE=1 python -m experiments.letter.e4b_rescore
```

Source mới: `experiments/letter/e4b_rescore.py`. Outputs mới: `results/letter/e4b/rescore_independent.json` và `.md`.
Không tạo CSV/log/biểu đồ/config mới; JSON lưu metrics/checks/SHA/sai khác. Không commit, SSH, truth run hoặc sửa file hiện có.
