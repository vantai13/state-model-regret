# EV-TE Arm R v2 — descriptive replay

Person responsible: **Doan Van Tai**.

Local execution, one serial worker, one BLAS thread. This directory contains the new Arm R outputs.

## Parser and observed coverage

An omitted OD is set to 0 Mb/s in a retained bin. A file with any node lacking source entries or destination entries is a missing bin. Explicit zero-valued entries count as present. Absent files are also missing; windows crossing missing bins are excluded.

| Count | Value |
|---|---:|
| TM files | 48,096 |
| Absent OD entries actually filled with zero in retained bins | 196,870 |
| Absent OD entries in all structurally parsed files, including discarded outage bins | 332,697 |
| Node-outage bins | 6,412 |
| Absent-file bins | 7,776 |
| Other malformed files | 0 |
| Valid bins | 41,684 |
| All missing bins | 14,188 |

Grid: 2004-03-01T00:00:00 through 2004-09-10T23:55:00, inclusive, at 5-minute spacing (55,872 bins). Missing-file counts refer to this observed calendar span.

Train: first two calendar months, **2004-03-01 <= timestamp < 2004-05-01T00:00:00**, 3,742/17,568 valid bins. Test: 37,942/38,304 valid bins. All mean TMs, alpha, bottlenecks, managed ODs, relaxation parameters and OLS coefficients use retained training bins. The existing active-support reduction uses observed train-plus-test loads; it was kept as before.

## Training quantities

| rho | alpha | e* | Managed OD1 | Managed {OD1, OD2} | T_int (min) | Censored |
|---:|---:|---|---|---|---:|---|
| 0.8 | 6.245521698222 | ATLAng_IPLSng:ATLAng>IPLSng | LOSAng_CHINng | LOSAng_CHINng, WASHng_IPLSng | 283.733817565 | False |
| 0.9 | 7.026211910500 | ATLAng_IPLSng:ATLAng>IPLSng | LOSAng_CHINng | LOSAng_CHINng, WASHng_IPLSng | 438.891423818 | False |

T_int uses the longest uninterrupted training segment: 2004-03-06T11:10:00 <= timestamp < 2004-03-14T00:00:00, 2,170 bins (10,850 minutes). No gaps were interpolated. Both managed sets have the same reported T_int at each rho.

## Descriptive paired differences

P uses the observed stale state in the relaxation-mean twin. N applies the training-only OLS nowcast to the stale state first. Both fresh pipelines use the same observed fresh state. G_S = mean(cost_old - cost_fresh), and E_stay is the observed mean all-Stay cost. Rates are Mb/min, queues Mb, and costs Mb·min.

Each value below is **100 G_S / E_stay ± 100 SE(G_S) / E_stay**, in percent. The mean uses all retained evaluation instances; SE is the sample standard deviation of daily paired means divided by sqrt(number of days), with E_stay held fixed, matching the existing summary rule. This is an SE, not a confidence interval. The retained five-minute windows overlap.

Every cell has n = 37,717 instances from 132 days. R1 = {OD1}; R4 = {OD1, OD2}. Full precision, unnormalized G_S, SE and E_stay are in [summary_cells.csv](summary_cells.csv).

| rho | Set | tau (min) | h (min) | h/T_int | P: G_S (% E_stay) ± SE | N: G_S (% E_stay) ± SE | n |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0.8 | R1 | 5 | 5 | 0.017622 | 0.000355 ± 0.000061 | 0.000038 ± 0.000051 | 37,717 |
| 0.8 | R1 | 5 | 10 | 0.035244 | 0.000603 ± 0.000107 | -0.000009 ± 0.000104 | 37,717 |
| 0.8 | R1 | 5 | 15 | 0.052866 | 0.000802 ± 0.000146 | -0.000134 ± 0.000165 | 37,717 |
| 0.8 | R1 | 5 | 30 | 0.105733 | 0.001315 ± 0.000246 | -0.000828 ± 0.000397 | 37,717 |
| 0.8 | R1 | 5 | 60 | 0.211466 | 0.002145 ± 0.000419 | -0.003493 ± 0.001180 | 37,717 |
| 0.8 | R1 | 10 | 5 | 0.017622 | 0.000694 ± 0.000121 | -0.000099 ± 0.000053 | 37,717 |
| 0.8 | R1 | 10 | 10 | 0.035244 | 0.001237 ± 0.000225 | -0.000311 ± 0.000109 | 37,717 |
| 0.8 | R1 | 10 | 15 | 0.052866 | 0.001700 ± 0.000317 | -0.000645 ± 0.000177 | 37,717 |
| 0.8 | R1 | 10 | 30 | 0.105733 | 0.002838 ± 0.000551 | -0.002175 ± 0.000473 | 37,717 |
| 0.8 | R1 | 10 | 60 | 0.211466 | 0.004535 ± 0.000911 | -0.007023 ± 0.001490 | 37,717 |
| 0.8 | R4 | 5 | 5 | 0.017622 | 0.000375 ± 0.000063 | 0.000060 ± 0.000052 | 37,717 |
| 0.8 | R4 | 5 | 10 | 0.035244 | 0.000630 ± 0.000110 | 0.000028 ± 0.000106 | 37,717 |
| 0.8 | R4 | 5 | 15 | 0.052866 | 0.000835 ± 0.000150 | -0.000076 ± 0.000167 | 37,717 |
| 0.8 | R4 | 5 | 30 | 0.105733 | 0.001356 ± 0.000252 | -0.000709 ± 0.000399 | 37,717 |
| 0.8 | R4 | 5 | 60 | 0.211466 | 0.002180 ± 0.000424 | -0.003178 ± 0.001186 | 37,717 |
| 0.8 | R4 | 10 | 5 | 0.017622 | 0.000735 ± 0.000125 | 0.000080 ± 0.000080 | 37,717 |
| 0.8 | R4 | 10 | 10 | 0.035244 | 0.001297 ± 0.000232 | 0.000051 ± 0.000166 | 37,717 |
| 0.8 | R4 | 10 | 15 | 0.052866 | 0.001777 ± 0.000327 | -0.000084 ± 0.000264 | 37,717 |
| 0.8 | R4 | 10 | 30 | 0.105733 | 0.002943 ± 0.000567 | -0.000959 ± 0.000657 | 37,717 |
| 0.8 | R4 | 10 | 60 | 0.211466 | 0.004656 ± 0.000930 | -0.004284 ± 0.001861 | 37,717 |
| 0.9 | R1 | 5 | 5 | 0.011392 | 0.000222 ± 0.000041 | 0.000068 ± 0.000037 | 37,717 |
| 0.9 | R1 | 5 | 10 | 0.022785 | 0.000363 ± 0.000071 | 0.000065 ± 0.000072 | 37,717 |
| 0.9 | R1 | 5 | 15 | 0.034177 | 0.000478 ± 0.000096 | 0.000030 ± 0.000111 | 37,717 |
| 0.9 | R1 | 5 | 30 | 0.068354 | 0.000772 ± 0.000162 | -0.000216 ± 0.000246 | 37,717 |
| 0.9 | R1 | 5 | 60 | 0.136708 | 0.001253 ± 0.000277 | -0.001314 ± 0.000671 | 37,717 |
| 0.9 | R1 | 10 | 5 | 0.011392 | 0.000427 ± 0.000083 | -0.000008 ± 0.000042 | 37,717 |
| 0.9 | R1 | 10 | 10 | 0.022785 | 0.000744 ± 0.000152 | -0.000092 ± 0.000085 | 37,717 |
| 0.9 | R1 | 10 | 15 | 0.034177 | 0.001011 ± 0.000212 | -0.000235 ± 0.000130 | 37,717 |
| 0.9 | R1 | 10 | 30 | 0.068354 | 0.001676 ± 0.000369 | -0.000920 ± 0.000307 | 37,717 |
| 0.9 | R1 | 10 | 60 | 0.136708 | 0.002695 ± 0.000615 | -0.003169 ± 0.000897 | 37,717 |
| 0.9 | R4 | 5 | 5 | 0.011392 | 0.000241 ± 0.000043 | 0.000082 ± 0.000037 | 37,717 |
| 0.9 | R4 | 5 | 10 | 0.022785 | 0.000386 ± 0.000073 | 0.000086 ± 0.000073 | 37,717 |
| 0.9 | R4 | 5 | 15 | 0.034177 | 0.000503 ± 0.000099 | 0.000058 ± 0.000112 | 37,717 |
| 0.9 | R4 | 5 | 30 | 0.068354 | 0.000809 ± 0.000165 | -0.000153 ± 0.000248 | 37,717 |
| 0.9 | R4 | 5 | 60 | 0.136708 | 0.001293 ± 0.000280 | -0.001206 ± 0.000673 | 37,717 |
| 0.9 | R4 | 10 | 5 | 0.011392 | 0.000467 ± 0.000086 | 0.000017 ± 0.000042 | 37,717 |
| 0.9 | R4 | 10 | 10 | 0.022785 | 0.000797 ± 0.000156 | -0.000055 ± 0.000085 | 37,717 |
| 0.9 | R4 | 10 | 15 | 0.034177 | 0.001074 ± 0.000217 | -0.000180 ± 0.000129 | 37,717 |
| 0.9 | R4 | 10 | 30 | 0.068354 | 0.001766 ± 0.000378 | -0.000811 ± 0.000304 | 37,717 |
| 0.9 | R4 | 10 | 60 | 0.136708 | 0.002805 ± 0.000627 | -0.002939 ± 0.000895 | 37,717 |

All-Stay baseline E_stay (Mb·min), identical for R1 and R4 at the same rho:

| rho | h=5 min | h=10 min | h=15 min | h=30 min | h=60 min |
|---:|---:|---:|---:|---:|---:|
| 0.8 | 1.836213256e+09 | 3.673042795e+09 | 5.510486449e+09 | 1.102647777e+10 | 2.207429695e+10 |
| 0.9 | 2.396729712e+09 | 4.794318332e+09 | 7.192763337e+09 | 1.439320999e+10 | 2.881635517e+10 |

## Fraction of time backlogged under Stay

The time fraction is the time with any positive link backlog divided by retained valid-bin time, integrated within each constant-load five-minute bin. The second fraction samples total backlog at bin ends. Queues restart at zero after gaps; missing time is excluded from both denominators. These are all-Stay replay occupancies, not the occupancy of a switched policy. R1 and R4 have identical all-Stay occupancy at each rho. Evaluated-start bins are the bins at the retained decision timestamps, not the union of their future windows.

| rho | Period | Valid bins | Observed min | Backlogged min | Time backlogged (%) | Positive end-bin samples (%) |
|---:|---|---:|---:|---:|---:|---:|
| 0.8 | train | 3,742 | 18,710 | 6,257.872343 | 33.446672 | 33.110636 |
| 0.8 | test | 37,942 | 189,710 | 92,081.804087 | 48.538192 | 48.384376 |
| 0.8 | evaluated_windows | 37,717 | 188,585 | 91,563.563220 | 48.552941 | 48.399926 |
| 0.9 | train | 3,742 | 18,710 | 12,400.527470 | 66.277539 | 66.007483 |
| 0.9 | test | 37,942 | 189,710 | 104,685.565003 | 55.181891 | 55.036635 |
| 0.9 | evaluated_windows | 37,717 | 188,585 | 104,033.996623 | 55.165573 | 55.020283 |

## Interpretation scope

These values describe an offline, five-minute, piecewise-constant fluid replay of the retained Abilene traffic matrices with the stated routing, training-period scaling and nowcast fits. Positive G_S means that the fresh pipeline had lower mean replay cost; negative G_S means that it had higher mean replay cost. The reported SE describes variation in daily paired means under the existing summary rule. Missing-bin windows are excluded, carry-in queues after gaps are unknown, and the valid training coverage is limited to the bins listed above. This is descriptive Arm R evidence outside the Arm S lock; it is not an Arm S hypothesis test, a measurement of production queues, or evidence for causal, stationary long-horizon or generalization claims.

## Commands and verification

Executed with:

```bash
source .venv/bin/activate
source experiments/explore_ctmc/env.sh
python3 -m pytest -q tests/test_ev_te.py tests/test_ext_packet.py tests/test_ev_d4c.py --basetemp=/tmp/evte_r2_pt -o cache_dir=/tmp/evte_r2_cache > results/ext_validity/ev_te/arm_r_v2/tests.log 2>&1
python3 -m experiments.ext_validity.ev_te_trace train > results/ext_validity/ev_te/arm_r_v2/train.log 2>&1
python3 -m experiments.ext_validity.ev_te_trace run > results/ext_validity/ev_te/arm_r_v2/run.log 2>&1
python3 -m experiments.ext_validity.ev_te_trace summary > results/ext_validity/ev_te/arm_r_v2/summary.log 2>&1
python3 -m experiments.ext_validity.ev_te verify-lock > results/ext_validity/ev_te/arm_r_v2/verify_lock.log 2>&1
```

Tests: **85 passed in 9.70s**. Only Arm R tests were added. The existing Arm R runner is serial and has no --workers option, so execution used one worker. Train, run and summary each exited 0. run.log and summary.log are empty because those commands print no status text; their JSON/CSV/raw outputs were checked directly.

Independent NumPy/raw checks reproduced all 80 summary cells, the CSV serialization, the common P/N fresh costs and every eligible timestamp. SHA256 checks matched 73 protected files before/after, including all 70 locked files plus lock.json and the historical arm_r/train.json and arm_r_train.log. verify-lock also matched external data. See [verification.json](verification.json), [protected_before.json](protected_before.json), [protected_after.json](protected_after.json) and [verify_lock.log](verify_lock.log). No commit or SSH was performed.

Artifacts: [train.json](train.json), [train.log](train.log), [run.json](run.json), [run.log](run.log), [summary.json](summary.json), [summary_cells.csv](summary_cells.csv), [summary.log](summary.log), [tests.log](tests.log), [raw/](raw/). Source changes: experiments/ext_validity/ev_te_trace.py and tests/test_ev_te.py. No chart was created.
