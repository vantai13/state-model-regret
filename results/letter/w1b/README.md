| prediction | outcome |
| --- | --- |
| P7 | HELD |
| P8 | HELD |
| P9 | HELD |
| P10 | NOT_EVALUABLE |
| P11 | NOT_HELD_FINITE_PANEL |
| P12 | HELD |

| owner | regimes | raw_regimes | E3_rows | hybrid_rows | CPU_s | wall_s | pilot_projected_wall_h | scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Doan Van Tai | 93 | 93 | 3255 | 32550 | 20715.8 | 7812 | 1.01288 | all_on_disk |

| family | eligible | age_harm | fraction | confounded_median | age_median |
| --- | --- | --- | --- | --- | --- |
| ALL | 217 | 194 | 0.894009 | -2.32107 | -4.87367 |
| asym | 78 | 72 | 0.923077 | -2.5634 | -5.48474 |
| zf_a3_asym | 82 | 78 | 0.95122 | -3.65995 | -5.34239 |
| zf_a7p5_asym | 57 | 44 | 0.77193 | -1.53062 | -3.90907 |

| population | n | median_ratio | confounded_median | age_median |
| --- | --- | --- | --- | --- |
| all_nonzero | 644 | 0.963718 | -0.795197 | -0.749034 |
| confounded_negative | 491 | 0.964439 | -1.47701 | -1.3459 |
| confounded_below_minus_0.1 | 462 | 0.963682 | -1.63081 | -1.45689 |

| level | n | both_pass | fraction | new_pass | old_pass | max_new | max_old |
| --- | --- | --- | --- | --- | --- | --- | --- |
| true_s | 1335 | 1310 | 0.981273 | 1335 | 1310 | 0.0265675 | 0.353606 |
| true_s_eps_-0.5 | 1335 | 1306 | 0.978277 | 1335 | 1306 | 0.0422379 | 0.353801 |
| true_s_eps_-0.25 | 1335 | 1310 | 0.981273 | 1335 | 1310 | 0.00356819 | 0.353421 |
| true_s_eps_-0.1 | 1335 | 1310 | 0.981273 | 1335 | 1310 | 0.0160224 | 0.35353 |
| true_s_eps_+0.1 | 1335 | 1308 | 0.979775 | 1335 | 1308 | 0.0419894 | 0.353689 |
| true_s_eps_+0.25 | 1335 | 1306 | 0.978277 | 1335 | 1306 | 0.0634708 | 0.35383 |
| true_s_eps_+0.5 | 1335 | 1302 | 0.975281 | 1335 | 1302 | 0.0990075 | 0.354014 |

| valid_regimes | invalid_regimes | correct_sign | sign_fraction | sign_correct_rows | equal_regret_rows | max_regret_difference_pp | fallback_sign_correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 93 | 0 | N/A | 0 | 0 | N/A | 93 |

| level | h_Tint | n | median_new | median_old | p95_new | p95_old | max_abs_GS | median_share_new | median_share_old |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| true_s | <1 | 995 | 0.381087 | 0.720321 | 3.03329 | 5.27296 | 9.02538 | 0.172354 | 0.0694104 |
| true_s | 1–<4 | 925 | 0.0119748 | 0.0140573 | 0.472462 | 1.60046 | 3.88253 | 0.0951687 | 0.0617837 |
| true_s | 4–<7 | 80 | 8.69491e-05 | 0.000183681 | 0.0265675 | 0.128104 | 0.327039 | 0.52056 | 0.517455 |
| true_s | >=7 | 1255 | 1.03653e-07 | 4.45339e-07 | 0.00347975 | 0.0175854 | 0.207975 | 0.0184149 | 0.0092896 |
| mm1 | <1 | 995 | 0.191648 | 0.608311 | 1.74588 | 5.03506 | 9.36202 | 0.288496 | 0.175917 |
| mm1 | 1–<4 | 925 | 0.0119573 | 0.0289644 | 0.431005 | 1.55253 | 9.81983 | 0.217136 | 0.146639 |
| mm1 | 4–<7 | 80 | 0.000796056 | 0.000291083 | 0.0984315 | 0.134736 | 0.345302 | 0.543685 | 0.538492 |
| mm1 | >=7 | 1255 | 2.95879e-06 | 1.95134e-06 | 0.122531 | 0.0747694 | 0.926037 | 0.0582504 | 0.0313698 |
| mmpp_est | <1 | 995 | 0.191648 | 0.608311 | 1.74588 | 5.03506 | 9.36202 | 0.288496 | 0.175917 |
| mmpp_est | 1–<4 | 925 | 0.0119573 | 0.0289644 | 0.431005 | 1.55253 | 9.81983 | 0.217136 | 0.146639 |
| mmpp_est | 4–<7 | 80 | 0.000796056 | 0.000291083 | 0.0984315 | 0.134736 | 0.345302 | 0.543685 | 0.538492 |
| mmpp_est | >=7 | 1255 | 2.95879e-06 | 1.95134e-06 | 0.122531 | 0.0747694 | 0.926037 | 0.0582504 | 0.0313698 |
| true_s_eps_-0.5 | <1 | 995 | 0.134891 | 0.571475 | 1.23253 | 5.0006 | 10.3798 | 0.291283 | 0.156681 |
| true_s_eps_-0.5 | 1–<4 | 925 | 0.00129064 | 0.0135705 | 0.110891 | 1.43643 | 4.798 | 0.169936 | 0.124349 |
| true_s_eps_-0.5 | 4–<7 | 80 | 0.000636762 | 0.000292218 | 0.0422379 | 0.131438 | 0.33994 | 0.546575 | 0.540236 |
| true_s_eps_-0.5 | >=7 | 1255 | 4.73019e-05 | 2.09423e-06 | 0.0223782 | 0.0268479 | 0.201318 | 0.0535196 | 0.0299272 |
| true_s_eps_-0.25 | <1 | 995 | 0.250108 | 0.643228 | 2.72159 | 5.09573 | 9.7223 | 0.212278 | 0.0981495 |
| true_s_eps_-0.25 | 1–<4 | 925 | 0.00705761 | 0.0137063 | 0.291546 | 1.57151 | 4.37412 | 0.123314 | 0.0852692 |
| true_s_eps_-0.25 | 4–<7 | 80 | 6.59814e-07 | 0.000171375 | 0.00356819 | 0.127055 | 0.34988 | 0.529163 | 0.525733 |
| true_s_eps_-0.25 | >=7 | 1255 | 4.74004e-07 | 7.64868e-07 | 0.000562706 | 0.0155497 | 0.222631 | 0.029011 | 0.015776 |
| true_s_eps_-0.1 | <1 | 995 | 0.316072 | 0.696401 | 2.72159 | 5.14651 | 9.31026 | 0.187027 | 0.0783639 |
| true_s_eps_-0.1 | 1–<4 | 925 | 0.0111188 | 0.0140573 | 0.404205 | 1.5936 | 4.07619 | 0.103222 | 0.0696709 |
| true_s_eps_-0.1 | 4–<7 | 80 | 4.64412e-05 | 0.000178712 | 0.0160224 | 0.12754 | 0.338014 | 0.523583 | 0.519757 |
| true_s_eps_-0.1 | >=7 | 1255 | 4.51243e-09 | 3.78101e-07 | 0.00116839 | 0.0161259 | 0.216416 | 0.0224846 | 0.0113935 |
| true_s_eps_+0.1 | <1 | 995 | 0.407958 | 0.725514 | 3.05232 | 5.50609 | 8.74627 | 0.15937 | 0.0593505 |
| true_s_eps_+0.1 | 1–<4 | 925 | 0.0130535 | 0.014128 | 0.539799 | 1.64106 | 3.68884 | 0.0847416 | 0.0555276 |
| true_s_eps_+0.1 | 4–<7 | 80 | 0.000116049 | 0.000188179 | 0.0419894 | 0.128732 | 0.3117 | 0.517479 | 0.515106 |
| true_s_eps_+0.1 | >=7 | 1255 | 3.01934e-07 | 5.72321e-07 | 0.00562584 | 0.0179606 | 0.197181 | 0.0150199 | 0.00778143 |
| true_s_eps_+0.25 | <1 | 995 | 0.438437 | 0.734571 | 3.05232 | 5.72581 | 8.30729 | 0.132761 | 0.0480088 |
| true_s_eps_+0.25 | 1–<4 | 925 | 0.0136104 | 0.0142372 | 0.616653 | 1.65942 | 3.4154 | 0.0777532 | 0.0475815 |
| true_s_eps_+0.25 | 4–<7 | 80 | 0.000146062 | 0.000193794 | 0.0634708 | 0.129602 | 0.29036 | 0.514271 | 0.512482 |
| true_s_eps_+0.25 | >=7 | 1255 | 5.20111e-07 | 6.55392e-07 | 0.00872789 | 0.0190436 | 0.183383 | 0.0118321 | 0.00594433 |
| true_s_eps_+0.5 | <1 | 995 | 0.525363 | 0.734571 | 3.4433 | 6.22402 | 7.50758 | 0.10376 | 0.0324039 |
| true_s_eps_+0.5 | 1–<4 | 925 | 0.0140213 | 0.0144021 | 0.752658 | 1.7929 | 2.99745 | 0.0625239 | 0.0378297 |
| true_s_eps_+0.5 | 4–<7 | 80 | 0.000178837 | 0.000198355 | 0.0990075 | 0.136544 | 0.255007 | 0.510421 | 0.509192 |
| true_s_eps_+0.5 | >=7 | 1255 | 7.19859e-07 | 7.53872e-07 | 0.0129737 | 0.0206193 | 0.160013 | 0.00787886 | 0.0038836 |
| sign_flipped | <1 | 995 | 4.09061 | 5.95074 | 37.9715 | 38.133 | 10.235 | 0.866677 | 0.980615 |
| sign_flipped | 1–<4 | 925 | 14.9687 | 17.1067 | 105.628 | 105.628 | 13.2263 | 0.92255 | 0.978017 |
| sign_flipped | 4–<7 | 80 | 18.5545 | 20.0529 | 128.446 | 128.446 | 3.97633 | 0.524912 | 0.524755 |
| sign_flipped | >=7 | 1255 | 22.1741 | 22.4977 | 135.946 | 135.946 | 2.04976 | 0.994162 | 0.998493 |

| h_Tint | n | max_abs_GS | median_regret_new | median_regret_old | median_cost_ratio_new | median_cost_ratio_old |
| --- | --- | --- | --- | --- | --- | --- |
| <1 | 995 | 10.235 | 4.09061 | 5.95074 | 0.160042 | 0.222779 |
| 1–<4 | 925 | 13.2263 | 14.9687 | 17.1067 | 0.544139 | 0.595877 |
| 4–<7 | 80 | 3.97633 | 18.5545 | 20.0529 | 0.844996 | 0.85804 |
| >=7 | 1255 | 2.04976 | 22.1741 | 22.4977 | 0.944435 | 0.947708 |

| level | n | new_worse | old_worse | either_worse | max_new_increase_pp | max_old_increase_pp |
| --- | --- | --- | --- | --- | --- | --- |
| true_s | 995 | 515 | 469 | 581 | 6.27035 | 6.84605 |
| mm1 | 995 | 380 | 408 | 479 | 6.27035 | 6.41847 |
| mmpp_est | 995 | 380 | 408 | 479 | 6.27035 | 6.41847 |
| true_s_eps_-0.5 | 995 | 365 | 384 | 461 | 4.95947 | 6.83624 |
| true_s_eps_-0.25 | 995 | 445 | 437 | 520 | 4.95947 | 6.84561 |
| true_s_eps_-0.1 | 995 | 460 | 457 | 542 | 6.27035 | 6.84595 |
| true_s_eps_+0.1 | 995 | 535 | 478 | 598 | 6.27035 | 6.8461 |
| true_s_eps_+0.25 | 995 | 570 | 488 | 619 | 6.27035 | 6.84613 |
| true_s_eps_+0.5 | 995 | 585 | 493 | 631 | 6.27035 | 6.84616 |
| sign_flipped | 995 | 995 | 926 | 995 | 37.5175 | 69.7432 |

Đây là exploration CTMC cắt hữu hạn với μ=10, a theo từng case, seed 20261116 + index, 5 ages và h grid giữ nguyên; ba file chứa 93 regimes, không phải 99. Mọi regret/G_S trong bảng là % C_ref; cost ratio là excess cost/(h|s|), CPU là tổng process time. Các bin dùng h/T_int thật, không làm tròn; P9 yêu cầu cả fresh và stale đạt riêng ở từng mức i/iv. P8 dùng tỷ số literal khi baseline khác 0 và kèm hai harm subsets; P7 ghép saved baseline τ=1 s với age-only τ=T_int. P7/P8 chỉ trên 92 regimes có baseline: case cuối có baseline UNRESOLVED vì CPU cap cũ, không điền 0 hoặc chạy lại baseline. Estimator ii INVALID ở 93/93 regimes; các dòng mmpp_est khi INVALID dùng iii và không chứng minh P10. API gốc từ chối α̂ ngoài namespace cố định; chi tiết lỗi domain/API nằm trong raw và analysis.json. P10 “matches” và P11 “≈” thiếu tolerance: phép so bằng số dùng 1e−9 pp; P11 NOT_HELD_FINITE_PANEL chỉ bác cách đọc đồng nhất ở mọi h, không bác giới hạn h→∞ (s≠0, finite state: −s làm cả hai chọn action sai, G_S→0, excess cost/(h|s|)→1). Tại τ=0 mọi pipeline trùng nhau; control τ→0⁺ không đạt trên exact M0 ties, lưu boundary_check.json, không thêm epsilon. Fresh so với baseline sai khác tuyệt đối tối đa 5.88625e-09; không có validity flags. Pilot và raw được lưu trước diễn giải; không commit theo brief. Run khởi đầu dừng trước computation vì forkserver bị sandbox chặn, run_fork.log dùng fork/pipes. Sau 92 raw, đã dừng case cuối trước lỗi đọc baseline thiếu; recovery chỉ tính case chưa có raw, dùng cùng Chain.V/age calls trong các tasks độc lập, không đổi numerical evaluator. CPU báo ở bảng là các evaluations hoàn tất; CPU phần bị dừng không có số đo và không được coi là 0. interruption.json, io_recovery_plan.json và recovery.log giữ lịch sử. Đây là mô tả panel hữu hạn, không population CI hoặc novelty claim.
