# V7-1 — gap-scale rule (post-hoc)

Người phụ trách: **Doan Van Tai**.

Verdict card: **DOES_NOT_HOLD**. Tiêu chí là AUC(P2)>AUC(P1) ở cả hai dataset; CI là mô tả, không thay tiêu chí.

| Dataset | Cells / Y=1 | AUC P1 (95% CI) | AUC P2 (95% CI) | AUC P3 (95% CI) | P2−P1 (95% CI) |
|---|---:|---:|---:|---:|---:|
| CTMC | 3255 / 2551 | 0.910904480 [0.889499430, 0.931042112] | 0.818012544 [0.779853069, 0.853988587] | 0.945018219 [0.929901842, 0.958691536] | -0.092891936 [-0.126808995, -0.063025067] |
| GEANT | 612 / 359 | 0.824518040 [0.765131278, 0.888765316] | 0.667213494 [0.482293019, 0.862514555] | 0.745262972 [0.643493255, 0.862762014] | -0.157304546 [-0.292401306, -0.006002858] |

Nguồn mọi AUC/CI: `cells.csv` (P1/P2/P3/Y); `summary.json.datasets`. Bootstrap paired theo regime, 2.000 draws, seed 20261118; hai seed GÉANT được lấy cùng nhau. Không bootstrap các cell như trial độc lập.

## Extraction, arrays và đơn vị

- CTMC: `results/letter/w1b/raw/*.json`, 93 regimes × 5 ages × 7 saved horizons = 3.255 cells, level `true_s`. Dùng `ctmc.m0_gap(..., h=inf)` cho `gap_A`, `gap_B`, chưa có h·s; hai finite-horizon certified shifts triệt tiêu trong tổng network gap. `pi_A`, `pi_B` là stationary Stay laws. `old_A_*`, `old_B_*` là `exp(Q_Stay*tau)` nhân gap, full old (backlog,mode), dùng `posterior_full` ở các chênh tuổi tăng dần. Joint stationary law của hai queue là tích hai pi; conditional expectation được lấy trước absolute value. M̂ xét **mọi** truncated states. Q90 của |gap_A+gap_B| dùng mass fresh 1/2, mỗi stale age 1/10. Units gap=packet·s, s=packet (backlog-cost rate), h/T_int/h*=s.
- GÉANT: kiểm đủ 340 NPZ + metadata ở `results/letter/e4/raw/` và `e4b/raw/`, seeds 3000001/5000001. NPZ chỉ có `V[instance,action,h]` là plant MC cost, `decisions[instance,pipeline,side,tau,h]`, `tie_flags` và grids/IDs; **không có per-instance M0 fluid costs/gaps**. Không thay `V` vào Δ̂. Tái tạo `instances`, posterior K=128 theo đúng E4 per-instance seeds, gọi `twin_costs` và mean cost như E4. `fresh_gap[n,h]=fresh_cost[:,Switch,:]-fresh_cost[:,Stay,:]`; `stale_gap[n,tau,h]=mean_posterior_cost_Switch-mean_posterior_cost_Stay`. Lưu dưới `extracted/GEANT_*.npz`. M̂=max |fresh_gap[:,-1]|; Q90 pool fresh 3 lần và 3 stale ages một lần (equal sides/ages), N=500/seed/regime. Dùng largest saved horizon h=30T_int theo card fallback, không tuyên bố đã saturation. Training s=`r_a[1].mean-r_a[0].mean` (level i), T_int/dt từ `results/ext_validity/ev_te/train/*.json`. Units gap=Mb·s, s=Mb, time=s theo simulator fast rate 1/s; không phải đo calibration thực tế.
- `extraction_checks.json`: mọi r/T_int/variance/s/F_new/F_old tính lại ở CTMC phải khớp saved với relative error≤1e−9 (zero đòi đúng zero). GÉANT đối chiếu bitwise M0 và Hybrid-i decisions + tie flags ở mọi age/horizon, cả hai phía; nguồn NPZ SHA được kiểm trước khi đọc. Gap scales là đại lượng mới nên không có saved gap scalar để đối chiếu trực tiếp; không tuyên bố scalar-gap replay khi raw không chứa nó.
- Quantile là inverse empirical/weighted CDF (`inverted_cdf`), dùng thống nhất hai dataset; không nội suy probability giữa atom. Scales và per-regime h* ở `regime_scales.csv`, mỗi số có source column; mỗi cell có source + source_row.

## Forecasts và h*

- CTMC: forecast AUC(P3) nằm giữa P1/P2: **False**. Precision P2≥1 = 2047/2315 = 0.884233261; false positives=268.
- CTMC: h*=Q90/|s| ∈ [3.21259198, 720.494799] s, tương đương [0.0385157558, 3.30413166] T_int. Nguồn: toàn bộ rows cùng dataset trong `regime_scales.csv`.
- GEANT: forecast AUC(P3) nằm giữa P1/P2: **True**. Precision P2≥1 = 347/546 = 0.635531136; false positives=199.
- GEANT: h*=Q90/|s| ∈ [0.0506572859, 44.9030596] s, tương đương [0.0408155351, 2.93284794] T_int. Nguồn: toàn bộ rows cùng dataset trong `regime_scales.csv`.
- Forecast precision≥0,9 trên GÉANT: **False**.

Nguồn forecast và per-seed counts/AUC: `summary.json.forecast_*`, `summary.json.geant_by_seed` (cùng cell table, không thí nghiệm mới).

## Regime-level Spearman

Onset là saved h đầu tiên mà mọi age có Y=1 ở h đó và mọi h sau. Mỗi GÉANT seed báo riêng để không coi hai seed của cùng regime là hai regime độc lập. Không có onset được ghi right-censored, không điền horizon kế tiếp.

| Dataset:seed | Evaluable / regimes | Right-censored | Left at first h | rho(onset,T_int) | rho(onset,h*) |
|---|---:|---:|---:|---:|---:|
| CTMC:none | 93/93 | 0 | 26 | 0.7194124320974268 | 0.3699486349878446 |
| GEANT:3000001 | 17/17 | 0 | 3 | 0.6519607843137255 | 0.7034313725490197 |
| GEANT:5000001 | 15/17 | 2 | 3 | 0.5249999999999999 | 0.5857142857142856 |

Nguồn: `regime_onsets.csv`; không có p-value/population claim từ panel này.

## Phân tích nguyên nhân và giới hạn

Cả ba predictor đều tuyến tính theo h trong mỗi regime: chênh AUC chỉ do thứ tự giữa regimes, không do thêm thông tin truth theo horizon. Dùng gap/s để dự báo regret/C_ref còn thiếu độ lớn denominator C_ref, information loss của stale state và sai số rate/truncated/finite-sample. Một gap thường gặp nhỏ không chứng minh regret chuẩn hóa nhỏ; M̂ từ đuôi mọi truncated state còn có thể rất lớn dù stationary mass ở đuôi nhỏ.
`summary.json.datasets.*.failed_Y_by_regime` giữ đủ các regime gây failure; không loại near-empty regimes hay tune quantile/cutoff để cứu card. Kiểm tra cùng saved dữ liệu bằng P3 là alternative đã khai trong card, không thêm predictor sau outcome. `subgroups.csv` báo từng CTMC family và từng GÉANT seed, kể cả nhóm kết quả không thuận. Không khởi động simulation mới để cải thiện verdict.

Inclusion rule: Table II giữ theo T_int; phải nói rõ gap/s không cải thiện dự báo trên cả hai dataset được xét. Không sửa paper trong brief này.

## Compute và kiểm chứng

Compute (source `summary.json.compute`): `{"workers": 16, "compute_location": "gcp", "reused_pilot_artifacts": ["CTMC_Za7p5_u3-2_lA31-4_x1-3_k2", "GEANT_e4_G2_r90_b6_s1_01"], "new_extractions": 431, "total_extractions": 433, "new_worker_cpu_s": 3002.752686881, "extraction_cpu_s_including_reused_pilot": 3219.413075463, "extraction_wall_sum_s_including_reused_pilot": 3219.4752023889996, "gcp_main_cpu_s": 1.5904994909999997, "gcp_child_cpu_s": 3016.64878, "gcp_elapsed_wall_s": 198.23586642499998, "worker_max_peak_rss_kib": 138080, "parent_peak_rss_kib": 138080, "memory_scope": "maximum single-worker RSS, not simultaneous total VM memory", "environment": {"python": "3.14.5 (main, Jun  2 2026, 22:25:17) [Clang 22.1.3 ]", "numpy": "2.5.3", "scipy": "1.18.1", "variables": {"NPY_DISABLE_CPU_FEATURES": "AVX512F AVX512CD AVX512VL AVX512BW AVX512DQ AVX512VNNI AVX512_SKX AVX512_CLX AVX512_CNL AVX512_ICL AVX512_SPR", "OPENBLAS_CORETYPE": "Haswell", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}}, "raw_commit_before_scoring": "536dc4863", "local_score_cpu_s": 8.01195616, "local_score_wall_s": 8.016063014998508, "local_score_peak_rss_kib": 170548}`.
Pilot gồm regime CTMC lớn nhất và E4/E4b chunk có saved CPU lớn nhất; `pilot.json` ghi projection trước full extraction. Pilot được reuse nguyên artifact. `input_manifest.json` ghi SHA256 code/card/brief và mọi input đã đọc; xác minh lại sau run. Independent rescore ở `experiments/letter/v7_1_rescore.py`, không import scorer, đọc per-cell table và phải khớp mọi AUC≤1e−12; kết quả riêng `rescore.json`.

## Deviations

- M0 fluid gaps are absent from E4/E4b raw; the unchanged pilot code reconstructs the original predictor inputs.
- A new wrapper separates parallel GCP extraction from local scoring; original source files and card remain unchanged.
- The two verified pilot extractions are reused, as planned in the pilot handoff; 431 extractions are new.

Thực hiện brief GCP tại HEAD: extraction detached, tối đa 16 workers; tải về và đối chiếu SHA256 hai phía; commit và push bảng trước scoring local. Không thay trạng thái/cấu hình VM, card, code pilot hoặc paper; không chạm V7-2/V7-3. Log/checksum/receipt ở thư mục này.
