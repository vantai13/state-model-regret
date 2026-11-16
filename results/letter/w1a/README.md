# LETTER-W1a — kết quả local

Người phụ trách: **Doan Van Tai**. Card nguồn: `results/letter/CARD_W1.md` (giữ nguyên).
Đây là audit và numerical checks; không phải author-self work hoặc mathematical proof.
Không commit và không SSH theo brief; raw được ghi trước khi tổng hợp. Quy tắc commit raw
trong card không được thực hiện vì brief lần này yêu cầu **Do not commit**.

## Phạm vi và định nghĩa

- Đủ 61 regime EV-TE: Abilene 32, GÉANT 29 (17 confirmatory + 12 descriptive D1).
- Test seed 1000001, N=500, K=128; đầy đủ 4 tuổi × 6 horizon × 4 pipelines.
- Pilot 3 instance/regime, nhưng dựng toàn bộ 500 states hai lần: 61/61 SHA khớp
  bitwise; N=500 khớp shape truth lưu sẵn. Dùng nguyên `ev_te.instances` và seed streams
  trong `run_one`, giữ posterior riêng từng instance. Argmin instance đầu khớp
  `choose_twins` 61/61. Truth không lưu states nên không có state-by-state đối chiếu
  trực tiếp với artifact cũ; không tái chạy truth rollouts.
- Tie chính: **mọi action có cùng predicted cost**. Relative tie dùng
  max(cost)−min(cost) ≤ 1e−9 max(abs(cost)), không absolute floor.
  Zero-zero: mọi cost bằng đúng 0. Bốn-action có thể có nhiều minimizing actions
  dù mọi cost không bằng nhau: cột `minimum_exact_share` và raw counters giữ riêng.
- Bảng topology ở h=30 T_int gộp đều regime × tuổi × instance. M0_new lặp lại qua
  các tuổi; không coi đây là các quan sát độc lập, không lập population CI.
- Pilot dự phóng 3072.045 CPU-s,
  6.400 phút/8 workers (<2 giờ): chạy **full grid**.
  Run dùng 6 workers; các công việc CTMC/test còn lại không làm vượt 8 workers.

## Topology — h=30 T_int, tỷ lệ %

| Nhóm | Pipeline | Exact all-action | Relative 1e-9 | Zero-zero | Tie tại minimum |
| --- | --- | --- | --- | --- | --- |
| Abilene_all_32 | M0_new | 51.362 | 51.362 | 51.362 | 51.600 |
| Abilene_all_32 | M0_old | 1.633 | 1.633 | 1.633 | 1.731 |
| Abilene_all_32 | P_old | 51.417 | 51.417 | 51.417 | 51.705 |
| Abilene_all_32 | CE_old | 2.072 | 2.072 | 2.072 | 2.072 |
| GEANT_confirmatory_17 | M0_new | 48.012 | 48.012 | 47.047 | 48.012 |
| GEANT_confirmatory_17 | M0_old | 4.106 | 4.106 | 4.103 | 4.106 |
| GEANT_confirmatory_17 | P_old | 47.753 | 47.753 | 46.703 | 47.753 |
| GEANT_confirmatory_17 | CE_old | 12.526 | 12.526 | 12.447 | 12.526 |
| GEANT_descriptive_12 | M0_new | 0.000 | 0.000 | 0.000 | 36.150 |
| GEANT_descriptive_12 | M0_old | 0.000 | 0.000 | 0.000 | 6.583 |
| GEANT_descriptive_12 | P_old | 0.000 | 0.000 | 0.000 | 35.900 |
| GEANT_descriptive_12 | CE_old | 0.000 | 0.000 | 0.000 | 12.371 |
| GEANT_all_29 | M0_new | 28.145 | 28.145 | 27.579 | 43.103 |
| GEANT_all_29 | M0_old | 2.407 | 2.407 | 2.405 | 5.131 |
| GEANT_all_29 | P_old | 27.993 | 27.993 | 27.378 | 42.848 |
| GEANT_all_29 | CE_old | 7.343 | 7.343 | 7.297 | 12.462 |

Per-(regime,τ,h,pipeline) ở `topology_ties.csv`; predicted cost vectors ở `topology/*.npz`.
Full audit có 5856 cells; recount độc lập từ NPZ: PASS,
0 mismatch; 0 nonfinite,
0 predicted values âm.

## P1–P6 — chấm cơ học

| Prediction | Kết quả | Số đếm |
| --- | --- | --- |
| P1 | HELD | 28/32 |
| P2 | DID_NOT_HOLD | 0/17 |
| P3 | DID_NOT_HOLD | 714/768 |
| P4 | DID_NOT_HOLD | 0/33 |
| P5 | HELD | 33/33 |
| P6 | DID_NOT_HOLD | 0/33 |

- P1: ≥30% exact all-action tie ở ít nhất 24/32 regime Abilene, h=30 T_int.
- P2: <10% exact tie ở ít nhất 13/17 GÉANT confirmatory. Card không ghi h:
  bảng chính áp dụng h=30 T_int; số đếm từng h ở `verification.json`.
- P3: card không chỉ định h, tuổi hoặc cách gộp. Cách đọc không điều kiện yêu cầu
  mọi cell Abilene M0_old <5%: 714/768 đạt;
  pooled mọi h/tuổi = 1.632812%, pooled h30 = 1.632812%,
  max cell = 27.200%. Kết quả theo pooled mọi h là
  HELD, theo pooled h30 là HELD.
- P4: literal “fresh và stale trùng action” **DID_NOT_HOLD**, 0/33.
  V̂ saturation **PASS 33/33**, sai khác tuyệt đối 0 bitwise; horizon-invariance
  riêng của fresh và stale **PASS 33/33**. Cách đọc invariance của P4 là HELD;
  không tự sửa câu trong card. Counterexamples cụ thể ở `lemma/*.json`.
- P5: true-s hybrid **PASS 33/33** trên bốn điểm grid
  > M_hat/|s|; kiểm toàn bộ finite states và posterior means bằng extrema.
- P6: bound ≤30 T_int ở 0/33; cần ít nhất 80%.

## Lemma — toàn bộ 33 asym regimes

bar_h/T_int = [16.802784, 18.162188];
(M_hat/|s|)/T_int = [380.387124, 1618.461186].
M_hat lấy max |gap tổng hai path| trên **toàn bộ support đã truncate** và posterior
means tại bar_h; giữ cả các states ở tail rất nhỏ, không thay bằng quantile hay
stationary-average bound. Fresh/stale là ctmc-v1, stale backlog-only ở τ=1,
khác thiết kế age-only của topology/W1b.

`m0_vhat(return_T=True)` được kiểm ở bar_h, nextafter(bar_h,+∞),
1.25bar_h, 2bar_h, 4bar_h; thêm các h=.25/.5/.75bar_h cho những states đã drain.
`m0_gap` và posterior nguyên bản được dùng kiểm decisions; quyết định từ shifted
và unshifted plateau không mismatch trên grid. `evaluate(arrays=True)` được replay
với h=1/100 để lấy/check inputs; không tính true V ở các bound h rất lớn.
Numerical grid và finite N không chứng minh mọi real h hoặc infinite-buffer lemma.
Kết quả từng regime: `lemma_checks.csv`, `lemma_checks.json`.

## CTMC saved-data — read only

Đọc 5191 JSON: 5144 COMPLETED,
47 UNRESOLVED (giữ danh sách lý do), 5768 horizon rows,
5768 physical keys không trùng. Không bỏ raw flags.
Bins dùng `h_Tint` đã lưu, không làm tròn theo nominal grid. Regret/G_S có đơn vị
**% C_ref**. `tie_mass.c10` là near-tie mass với tolerance
1e−12(h*r_stay+1), không phải exact tie definition của topology.

| h/T_int | Rows | Median tie mass | q90 tie mass | Share G_S<−0.1 (%) |
| --- | --- | --- | --- | --- |
| <1 | 3135 | 0.0483717 | 0.588708 | 24.242 |
| 1-4 | 938 | 0.0160319 | 0.04392 | 67.377 |
| 4-7 | 301 | 0.0166914 | 0.0428038 | 72.425 |
| 7-15 | 950 | 0.0130344 | 0.0344807 | 77.789 |
| >=15 | 444 | 0.0160847 | 0.044017 | 76.351 |

Median regret (% C_ref); cột new/old được tách riêng:

| h/T_int | M0_new | M0_old | hybrid_new | hybrid_old | hybrid_mm1_new | hybrid_mm1_old | static |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <1 | 0.0921571 | 0.147155 | 0.121166 | 0.17375 | 0.0766804 | 0.142131 | 0.264318 |
| 1-4 | 2.80711 | 1.0006 | 0.00251348 | 0.019687 | 0.00212931 | 0.0251655 | 0.0526754 |
| 4-7 | 4.53245 | 1.2417 | 8.21021e-07 | 6.36022e-05 | 3.13056e-06 | 0.000259378 | 9.29543e-05 |
| 7-15 | 5.3466 | 2.69715 | 7.42202e-06 | 2.36672e-05 | 5.45991e-05 | 0.000243594 | 5.71418e-05 |
| >=15 | 6.5483 | 2.54999 | 3.37201e-12 | 3.5549e-11 | 1.60193e-08 | 2.96084e-07 | 7.99481e-11 |

Sign agreement theo case: 4646/5144 =
90.318818%. Có 498 case
true s=0 nhưng s_mm1≠0 theo floating point; **0 case có hai dấu nonzero trái nhau**.
Không gọi mọi mismatch này là đảo dấu có ý nghĩa khoa học; không dùng epsilon
để đổi số đếm. Đối chiếu công thức M/M/1 bằng Fraction cho cả 498 case mismatch
cho slope đúng bằng 0; max |s_mm1| float là 3.55271368e-15.
Regret hybrid_mm1 trong các row mismatch được báo đầy đủ:

| h/T_int | Mismatch rows | Opposite nonzero | Median mm1_new regret | Median mm1_old regret |
| --- | --- | --- | --- | --- |
| <1 | 311 | 0 | 0.00810481 | 0.150663 |
| 1-4 | 87 | 0 | 2.34637e-05 | 0.142663 |
| 4-7 | 32 | 0 | 9.0781e-07 | 0.0549867 |
| 7-15 | 31 | 0 | 6.01959e-06 | 0.0192837 |
| >=15 | 37 | 0 | 2.63996e-06 | 0.015659 |

Bảng theo từng design source (tie mass là share, cột harm là share):

| Source | h/T_int | N | Median tie | q90 tie | Share harm |
| --- | --- | --- | --- | --- | --- |
| runs/asym | <1 | 71 | 0.0197167 | 0.0627785 | 0.478873 |
| runs/asym | 1-4 | 62 | 0.0219217 | 0.0435207 | 0.806452 |
| runs/asym | 4-7 | 8 | 0.0239306 | 0.0326159 | 0.875 |
| runs/asym | 7-15 | 45 | 0.0251578 | 0.0472987 | 0.866667 |
| runs/asym | >=15 | 45 | 0.0301434 | 0.0472987 | 0.866667 |
| runs/bridge | <1 | 1183 | 0.463958 | 0.662536 | 0.0566357 |
| runs/bridge | 1-4 | 17 | 0.0452117 | 0.0777667 | 0.235294 |
| runs/bridge | 4-7 | 0 | — | — | — |
| runs/bridge | 7-15 | 0 | — | — | — |
| runs/bridge | >=15 | 0 | — | — | — |
| runs/csw | <1 | 22 | 0.0109171 | 0.0399942 | 0 |
| runs/csw | 1-4 | 28 | 0.0109171 | 0.0352798 | 0 |
| runs/csw | 4-7 | 8 | 0.0127885 | 0.0367454 | 0 |
| runs/csw | 7-15 | 14 | 0.0109171 | 0.0386996 | 0 |
| runs/csw | >=15 | 12 | 0.0109171 | 0.0346975 | 0 |
| runs/pslice | <1 | 48 | 0.0786405 | 0.476396 | 0.145833 |
| runs/pslice | 1-4 | 22 | 0.0308003 | 0.0481296 | 0.454545 |
| runs/pslice | 4-7 | 5 | 0.0381525 | 0.0481296 | 0.6 |
| runs/pslice | 7-15 | 3 | 0.0481296 | 0.0481296 | 0.666667 |
| runs/pslice | >=15 | 0 | — | — | — |
| runs/wide | <1 | 1040 | 0.0246844 | 0.30347 | 0.361538 |
| runs/wide | 1-4 | 410 | 0.0169794 | 0.0466077 | 0.72439 |
| runs/wide | 4-7 | 166 | 0.0184274 | 0.0462903 | 0.759036 |
| runs/wide | 7-15 | 222 | 0.0171706 | 0.0458878 | 0.720721 |
| runs/wide | >=15 | 198 | 0.0164172 | 0.0493999 | 0.787879 |
| runs/xslice | <1 | 37 | 0.0204594 | 0.0270253 | 0.72973 |
| runs/xslice | 1-4 | 40 | 0.0307521 | 0.0498878 | 0.45 |
| runs/xslice | 4-7 | 12 | 0.0345318 | 0.0488288 | 0.666667 |
| runs/xslice | 7-15 | 7 | 0.0448285 | 0.0557081 | 0.428571 |
| runs/xslice | >=15 | 0 | — | — | — |
| runs_l72/zf_a3_asym | <1 | 66 | 0.0169221 | 0.0558439 | 0.484848 |
| runs_l72/zf_a3_asym | 1-4 | 62 | 0.0157299 | 0.039595 | 0.790323 |
| runs_l72/zf_a3_asym | 4-7 | 5 | 0.0140848 | 0.0164932 | 1 |
| runs_l72/zf_a3_asym | 7-15 | 46 | 0.0204028 | 0.041319 | 0.847826 |
| runs_l72/zf_a3_asym | >=15 | 52 | 0.0235213 | 0.0422333 | 0.826923 |
| runs_l72/zf_a3_sobol | <1 | 305 | 0.0199153 | 0.283558 | 0.360656 |
| runs_l72/zf_a3_sobol | 1-4 | 120 | 0.0157633 | 0.0503733 | 0.716667 |
| runs_l72/zf_a3_sobol | 4-7 | 49 | 0.0164279 | 0.0418892 | 0.734694 |
| runs_l72/zf_a3_sobol | 7-15 | 65 | 0.0111234 | 0.0370771 | 0.784615 |
| runs_l72/zf_a3_sobol | >=15 | 61 | 0.0150772 | 0.0466203 | 0.704918 |
| runs_l72/zf_a3_xs | <1 | 0 | — | — | — |
| runs_l72/zf_a3_xs | 1-4 | 0 | — | — | — |
| runs_l72/zf_a3_xs | 4-7 | 0 | — | — | — |
| runs_l72/zf_a3_xs | 7-15 | 274 | 0.0149358 | 0.0277153 | 0.821168 |
| runs_l72/zf_a3_xs | >=15 | 0 | — | — | — |
| runs_l72/zf_a7p5_asym | <1 | 58 | 0.0121619 | 0.0305501 | 0.293103 |
| runs_l72/zf_a7p5_asym | 1-4 | 60 | 0.010784 | 0.0162562 | 0.8 |
| runs_l72/zf_a7p5_asym | 4-7 | 3 | 0.0113629 | 0.0119784 | 1 |
| runs_l72/zf_a7p5_asym | 7-15 | 32 | 0.0117476 | 0.0161529 | 0.90625 |
| runs_l72/zf_a7p5_asym | >=15 | 29 | 0.0113629 | 0.0214166 | 0.965517 |
| runs_l72/zf_a7p5_sobol | <1 | 305 | 0.0106779 | 0.29197 | 0.295082 |
| runs_l72/zf_a7p5_sobol | 1-4 | 117 | 0.0090495 | 0.0249669 | 0.598291 |
| runs_l72/zf_a7p5_sobol | 4-7 | 45 | 0.00813287 | 0.0235635 | 0.666667 |
| runs_l72/zf_a7p5_sobol | 7-15 | 61 | 0.00928263 | 0.0234583 | 0.721311 |
| runs_l72/zf_a7p5_sobol | >=15 | 47 | 0.00902246 | 0.0285959 | 0.638298 |
| runs_l72/zf_a7p5_xs | <1 | 0 | — | — | — |
| runs_l72/zf_a7p5_xs | 1-4 | 0 | — | — | — |
| runs_l72/zf_a7p5_xs | 4-7 | 0 | — | — | — |
| runs_l72/zf_a7p5_xs | 7-15 | 181 | 0.00893898 | 0.0141948 | 0.812155 |
| runs_l72/zf_a7p5_xs | >=15 | 0 | — | — | — |

Median regret theo design source (% C_ref):

| Source | h/T_int | M0_new | M0_old | hybrid_new | hybrid_old | hybrid_mm1_new | hybrid_mm1_old | static |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| runs/asym | <1 | 0.51919 | 0.513066 | 0.304905 | 0.499271 | 0.138802 | 0.3118 | 0.663983 |
| runs/asym | 1-4 | 3.64443 | 2.18077 | 0.00870291 | 0.0103995 | 0.00889042 | 0.0520992 | 0.0136521 |
| runs/asym | 4-7 | 4.16347 | 3.12008 | 0.000396623 | 0.000738939 | 0.000796056 | 0.000980105 | 0.000936689 |
| runs/asym | 7-15 | 5.52283 | 3.40631 | 3.21585e-06 | 6.68174e-06 | 0.000192935 | 0.000665031 | 8.97137e-06 |
| runs/asym | >=15 | 6.47373 | 4.00995 | 8.17844e-12 | 3.07981e-11 | 3.81017e-07 | 1.68731e-06 | 3.57658e-11 |
| runs/bridge | <1 | 0.0464775 | 0.039402 | 0.0813626 | 0.0867403 | 0.0583385 | 0.0803002 | 0.113343 |
| runs/bridge | 1-4 | 0.0842341 | 0.387732 | 0.0604587 | 0.364403 | 0.0231505 | 0.307274 | 0.872463 |
| runs/bridge | 4-7 | — | — | — | — | — | — | — |
| runs/bridge | 7-15 | — | — | — | — | — | — | — |
| runs/bridge | >=15 | — | — | — | — | — | — | — |
| runs/csw | <1 | 0.0501655 | 0.91339 | 0.181351 | 0.849974 | 0.0985263 | 0.83726 | 5.32085 |
| runs/csw | 1-4 | 0.258075 | 0.869393 | 0.16186 | 0.532779 | 0.0278035 | 0.464172 | 4.7283 |
| runs/csw | 4-7 | 0.381249 | 0.760246 | 0.0575288 | 0.224153 | 0.00803586 | 0.219569 | 1.77959 |
| runs/csw | 7-15 | 1.05275 | 1.22599 | 0.0147687 | 0.07366 | 0.0265067 | 0.0881714 | 0.462215 |
| runs/csw | >=15 | 2.03215 | 2.21719 | 0.00101181 | 0.00805438 | 0.0190215 | 0.0272997 | 0.0620194 |
| runs/pslice | <1 | 0.0933247 | 0.415878 | 0.333906 | 0.601958 | 0.211846 | 0.527002 | 0.753901 |
| runs/pslice | 1-4 | 0.787557 | 0.8031 | 0.113148 | 0.24695 | 0.0135698 | 0.1681 | 0.384702 |
| runs/pslice | 4-7 | 1.74017 | 1.42635 | 0.0124893 | 0.021671 | 0.0176406 | 0.023765 | 0.036008 |
| runs/pslice | 7-15 | 2.75824 | 1.70622 | 0.000593466 | 0.00123571 | 0.0137015 | 0.00968682 | 0.00223298 |
| runs/pslice | >=15 | — | — | — | — | — | — | — |
| runs/wide | <1 | 0.144723 | 0.257054 | 0.135617 | 0.224924 | 0.0821453 | 0.198007 | 0.320863 |
| runs/wide | 1-4 | 3.86284 | 0.819308 | 0.00017385 | 0.00465869 | 0.000377978 | 0.0118628 | 0.00615015 |
| runs/wide | 4-7 | 6.09996 | 1.2918 | 5.96252e-08 | 4.03464e-06 | 2.55401e-06 | 7.58231e-05 | 5.71528e-06 |
| runs/wide | 7-15 | 6.98925 | 2.05099 | 1.70724e-09 | 4.39136e-08 | 1.11531e-07 | 1.69507e-05 | 6.25377e-08 |
| runs/wide | >=15 | 7.43714 | 1.71181 | 1.58734e-13 | 1.08052e-11 | 4.70654e-10 | 8.01909e-09 | 2.4507e-11 |
| runs/xslice | <1 | 2.47307 | 1.32636 | 0.532304 | 0.838174 | 0.33086 | 0.68961 | 1.2951 |
| runs/xslice | 1-4 | 1.57274 | 1.36198 | 0.117855 | 0.283788 | 0.0245892 | 0.173523 | 0.731894 |
| runs/xslice | 4-7 | 3.02504 | 1.37673 | 0.00894783 | 0.0244451 | 0.00858472 | 0.0743305 | 0.0827074 |
| runs/xslice | 7-15 | 1.48113 | 1.5256 | 0.00223273 | 0.036743 | 0.0252462 | 0.0899025 | 0.171088 |
| runs/xslice | >=15 | — | — | — | — | — | — | — |
| runs_l72/zf_a3_asym | <1 | 0.498879 | 0.622985 | 0.313816 | 0.619867 | 0.255632 | 0.552644 | 0.691226 |
| runs_l72/zf_a3_asym | 1-4 | 3.63134 | 1.68491 | 0.00763157 | 0.00836247 | 0.00392423 | 0.0072473 | 0.00937901 |
| runs_l72/zf_a3_asym | 4-7 | 4.73936 | 2.55268 | 2.97631e-08 | 3.25457e-08 | 3.67305e-09 | 1.10724e-08 | 4.41109e-08 |
| runs_l72/zf_a3_asym | 7-15 | 5.51582 | 2.80816 | 9.04709e-07 | 1.869e-06 | 7.9379e-07 | 1.01192e-05 | 2.12601e-06 |
| runs_l72/zf_a3_asym | >=15 | 6.46906 | 3.52894 | 4.19211e-12 | 1.98362e-11 | 3.7619e-09 | 1.40855e-09 | 2.40723e-11 |
| runs_l72/zf_a3_sobol | <1 | 0.136655 | 0.245715 | 0.125282 | 0.226419 | 0.113701 | 0.208692 | 0.277525 |
| runs_l72/zf_a3_sobol | 1-4 | 3.1132 | 0.586548 | 0.000283073 | 0.00559563 | 0.000211367 | 0.00498508 | 0.00932253 |
| runs_l72/zf_a3_sobol | 4-7 | 4.92127 | 0.532177 | 3.75581e-10 | 2.99359e-07 | 3.8949e-09 | 2.60339e-06 | 3.20417e-07 |
| runs_l72/zf_a3_sobol | 7-15 | 7.64915 | 1.31577 | 1.96417e-10 | 4.10933e-10 | 4.53248e-11 | 6.28379e-10 | 5.33293e-10 |
| runs_l72/zf_a3_sobol | >=15 | 7.37672 | 1.1306 | 2.14692e-15 | 1.87845e-13 | 1.14383e-14 | 1.35629e-11 | 3.44871e-14 |
| runs_l72/zf_a3_xs | <1 | — | — | — | — | — | — | — |
| runs_l72/zf_a3_xs | 1-4 | — | — | — | — | — | — | — |
| runs_l72/zf_a3_xs | 4-7 | — | — | — | — | — | — | — |
| runs_l72/zf_a3_xs | 7-15 | 4.25555 | 2.81678 | 0.000109252 | 0.00024272 | 6.25215e-05 | 0.000247155 | 0.000475408 |
| runs_l72/zf_a3_xs | >=15 | — | — | — | — | — | — | — |
| runs_l72/zf_a7p5_asym | <1 | 0.422715 | 0.480011 | 0.59381 | 0.745719 | 0.195588 | 0.26369 | 1.53608 |
| runs_l72/zf_a7p5_asym | 1-4 | 2.58555 | 1.79428 | 0.02433 | 0.027331 | 0.0225846 | 0.0583055 | 0.0389097 |
| runs_l72/zf_a7p5_asym | 4-7 | 3.85026 | 3.64145 | 0.00968638 | 0.0116879 | 0.042694 | 0.043465 | 0.0625247 |
| runs_l72/zf_a7p5_asym | 7-15 | 4.86028 | 4.30572 | 1.19836e-06 | 1.54512e-06 | 0.000447354 | 0.000561906 | 3.35105e-06 |
| runs_l72/zf_a7p5_asym | >=15 | 5.7429 | 4.80322 | 2.56742e-12 | 5.88173e-12 | 2.95879e-06 | 4.43718e-06 | 1.64502e-11 |
| runs_l72/zf_a7p5_sobol | <1 | 0.116286 | 0.150663 | 0.0969003 | 0.134125 | 0.0457212 | 0.0997365 | 0.820366 |
| runs_l72/zf_a7p5_sobol | 1-4 | 2.31841 | 1.20209 | 4.18422e-06 | 0.0123817 | 3.48596e-05 | 0.0123165 | 0.163695 |
| runs_l72/zf_a7p5_sobol | 4-7 | 3.75987 | 1.37428 | 2.17615e-07 | 0.000353109 | 3.27032e-07 | 0.00318011 | 0.000910494 |
| runs_l72/zf_a7p5_sobol | 7-15 | 4.96301 | 2.1952 | 1.14757e-07 | 7.70639e-07 | 1.15645e-06 | 0.000169008 | 3.94469e-06 |
| runs_l72/zf_a7p5_sobol | >=15 | 4.49066 | 2.28832 | 6.64952e-10 | 7.71066e-07 | 8.04966e-08 | 0.000169897 | 4.86254e-06 |
| runs_l72/zf_a7p5_xs | <1 | — | — | — | — | — | — | — |
| runs_l72/zf_a7p5_xs | 1-4 | — | — | — | — | — | — | — |
| runs_l72/zf_a7p5_xs | 4-7 | — | — | — | — | — | — | — |
| runs_l72/zf_a7p5_xs | 7-15 | 4.78372 | 4.30383 | 3.96345e-05 | 6.12005e-05 | 0.00155082 | 0.00312542 | 0.000218671 |
| runs_l72/zf_a7p5_xs | >=15 | — | — | — | — | — | — | — |

CSV/JSON đầy đủ: `ctmc_saved_tables.csv/json`, `ctmc_saved_pooled.csv`,
`ctmc_sign_by_source.csv`, `ctmc_sign_mismatch_rows.csv`, `ctmc_saved_rows.csv`.
Input hashes: `ctmc_saved_input_hashes.json`.

## Kiểm tra, CPU và file

Command thực tế (sau khi source `.venv/bin/activate`, `experiments/explore_ctmc/env.sh`
và đặt `PYTHONDONTWRITEBYTECODE=1`):

```bash
python3 -m experiments.letter.ties_topology pilot --workers 8
python3 -m experiments.letter.ties_topology run --workers 6
python3 -m experiments.letter.lemma_check
python3 -m experiments.letter.ctmc_saved_tables
python3 -m pytest -q tests/test_letter_w1a.py tests/test_ev_te.py --basetemp=/tmp/lw1a_pt -o cache_dir=/tmp/lw1a_cache
python3 -m experiments.letter.w1a_report
```

Test **PASS**, stdout: `35 passed in 3.42s`. Log: `pytest.log`, process resources: `pytest_resources.txt`.
Analysis CPU được đo: pilot 44.257 s,
topology main 3062.258 s,
lemma 59.075 s, saved tables 1.657 s;
tổng 3167.246 s. Đây là tổng các timed analysis intervals,
chưa gồm toàn bộ interpreter startup/imports, hash/report và pytest; không phải
end-to-end CPU billing. Wall main 746.365 s.
Chi tiết: `cpu_times.json`, các log `topology_pilot.log`, `topology_run.log`,
`lemma_check.log`, `ctmc_saved_tables.log`.

28829 file đã có trong hai cây results được bảo vệ và các
source/card chính: SHA256 giữ nguyên, `verification.json` PASS. Mã mới nằm ở
`experiments/letter/` (ba module được yêu cầu, module tạo report, `__init__.py`),
test ở `tests/test_letter_w1a.py`. Không đụng `e3_*.py`. Không tạo biểu đồ ở W1a.

## Plain facts

Đợt này đã dựng lại 30.500 decision instances đúng seed test và ghi predicted
cost vectors cho đủ lưới của 61 regime; mọi counter được recount từ raw vectors.
Trong 33 CTMC asym regimes, cost M0 bão hòa và mỗi policy giữ nguyên theo horizon
trên grid đã kiểm, nhưng fresh/stale có counterexample chọn khác action. Hybrid
dùng true s trùng action trên grid vượt bound; bound toàn support đều lớn hơn
30 T_int. Saved-data tables có 5.768 rows; strict sign mismatches đều thuộc
s=0/s_mm1≠0, không có hai dấu nonzero trái nhau. Các dữ kiện này không xác nhận
causal explanation của topology harm, mathematical theorem, novelty hoặc realism.
