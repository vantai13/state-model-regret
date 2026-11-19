# R2-O1 — kiểm phạm vi mệnh đề (P)

Người phụ trách: **Doan Van Tai**. Exploration kiểm mệnh đề; không phải kết quả paper, không đổi verdict đã khóa.

**STOP_BUDGET sau 1 pilot; không hoàn tất panel 12 regime.** Dừng theo đúng brief: sau khi giảm lưới h đến `{1}`, dự phóng vẫn vượt 2 CPU-h. Không chạy thêm truth, không tự bỏ P_dis hoặc lấy subset để nhận full PASS.

Đã chọn đủ 12 regime theo thứ tự id và rounded linspace, 6 s<0 từ 42 và 6 s>0 từ 51. Predictions/threshold/w*/slope của cả 12 đã lưu trước truth. Pilot `Za3_u1_lA7_x-1_k1-20`: `(lamA,lamB,u,kappa,alpha)=(7,6,1,1/20,3)`, c=0, mu=10, tau=T_int=4.63063430308 s; N_A=167, N_B=106. Lưới pilot `h/T_int=(1, 3, 10, 30, 100, 300)`: 36 twin-h cells, 7 T0 replay rows. Không seed: deterministic finite CTMC.

## D1–D6: đúng/sai và phạm vi thực sự đã kiểm

| Dự đoán | Trạng thái | Bằng chứng/giới hạn |
|---|---|---|
| D1 | CHƯA ĐÁNH GIÁ ĐƯỢC | 0 ô đủ h>M_hat/abs(s_hat); không nhận PASS rỗng. Ngưỡng của cả 12 regime đều ngoài lưới gốc. |
| D2 | ĐÚNG TRÊN PILOT: 12/12 | T1/T2, 6 h; dùng P_dis lower bound và tolerance arithmetic 1e−9 C_ref. Có 8/12 thỏa ngay không tolerance; không khẳng định toàn panel. |
| D3 | CHƯA ĐÁNH GIÁ ĐƯỢC | 0 ô trên ngưỡng cho cả plug-in và 3tau; T3 vẫn được chạy đủ 6 mức h của pilot. |
| D4 | PHÙ HỢP HỮU HẠN TRÊN 1 PILOT | T0 slope dự đoán -0.222286063158; G_S/h ở 300 T_int = -0.221041531245 packet. Chưa chứng minh giới hạn bằng chạy hữu hạn. |
| D5 | PHÙ HỢP HỮU HẠN TRÊN 1 PILOT | T4 w*=.25: P_dis=0.249999995205, dự đoán .25. Slope dự đoán -0.213020924373; đo -0.212475967529. 3 regime T4 hợp lệ khác chưa chạy, gồm 2 constant-sign. |
| D6 | MỘT PHẦN | Dự đoán trước truth 2 regime slope âm; quan sát harm tăng ở 1 pilot, regime còn lại NOT_RUN. Không ghi 2/2 PASS. |

D4/D5 dùng chữ ‘phù hợp hữu hạn’: brief không cho tolerance hội tụ hoặc tốc độ ‘gần tuyến tính’. Không tự đặt ngưỡng chấm sau khi thấy dữ liệu.

## Kết quả đo trực tiếp

| Twin ở h/T_int=300 | G_S (packet·s) | 100 G_S/C_ref (%) | P_dis |
|---|---:|---:|---:|
| T0 | -307.068749096 | -4.59590825139 | 0.260905512211 |
| T1 | 2.27373675443e-12 | 3.40310941506e-14 | 2.22044604925e-16 |
| T2 | 2.27373675443e-12 | 3.40310941506e-14 | 2.22044604925e-16 |
| T3_plugin | 2.27373675443e-12 | 3.40310941506e-14 | 2.22044604925e-16 |
| T3_3tau | 2.27373675443e-12 | 3.40310941506e-14 | 2.22044604925e-16 |
| T4 | -295.169551146 | -4.41781255718 | 0.249999995205 |

C_ref ở mức cuối = 6681.35072111 packet·s. T0 baseline và T4 đều có harm (G_S<0); T1/T2/T3 chỉ gần 0 theo số học, không khẳng định tất cả state đã coincidence dưới ngưỡng bảo đảm.

| Twin | h/T_int | G_S packet·s | G_S %C_ref | slope dự đoán | G_S/h đo | sai số slope tương đối | secant từ mức trước | P_dis |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| T0 | 1 | -0.105119891769 | -0.430320990176 | -0.222286063158 | -0.0227009702967 | 89.7874973% | n/a | 0.260910628063 |
| T0 | 3 | -1.53724850898 | -2.20840901008 | -0.222286063158 | -0.11065787884 | 50.218256% | -0.154636333111 | 0.260905553122 |
| T0 | 10 | -8.56628379761 | -3.79905697025 | -0.222286063158 | -0.184991585104 | 16.7776952% | -0.216848887788 | 0.260905512211 |
| T0 | 30 | -29.1508724475 | -4.34622770367 | -0.222286063158 | -0.209840744194 | 5.59878509% | -0.222265323739 | 0.260905512211 |
| T0 | 100 | -101.203655265 | -4.54025708469 | -0.222286063158 | -0.218552467418 | 1.67963555% | -0.222286063086 | 0.260905512211 |
| T0 | 300 | -307.068749096 | -4.59590825139 | -0.222286063158 | -0.221041531245 | 0.559878517% | -0.222286063158 | 0.260905512211 |
| T4 | 1 | -0.139054813786 | -0.56923769755 | -0.213020924373 | -0.0300293231305 | 85.9031111% | n/a | 0.179037138837 |
| T4 | 3 | -1.54679866772 | -2.22212875447 | -0.213020924373 | -0.111345341083 | 47.7303268% | -0.152003350059 | 0.216175434509 |
| T4 | 10 | -8.5147244571 | -3.77619094379 | -0.213020924373 | -0.183878144975 | 13.6807121% | -0.214963632358 | 0.241264101922 |
| T4 | 30 | -28.6701274521 | -4.2745513852 | -0.213020924373 | -0.206380131214 | 3.11743702% | -0.217631124333 | 0.24913802731 |
| T4 | 100 | -97.8804997128 | -4.39117175275 | -0.213020924373 | -0.211376008785 | 0.772184983% | -0.213517099173 | 0.24999248601 |
| T4 | 300 | -295.169551146 | -4.41781255718 | -0.213020924373 | -0.212475967529 | 0.255823152% | -0.213025946902 | 0.249999995205 |

T0 |G_S| tăng từ 0.105119892 lên 307.068749 packet·s; T4 từ 0.139054814 lên 295.169551 packet·s. Slope là G_S/h (packet), không phải %C_ref/h. Chuẩn hóa bởi C_ref tăng theo h có thể cho %C_ref hội tụ trong khi harm tuyệt đối tăng tuyến tính.

## CPU, pilot và lý do dừng

Prediction preparation 24.375981474 CPU-s; pilot 16.797530356 CPU-s: truth 16.151048653, posterior 0.323963005, joint 0.262530023. Tổng scientific đo được 41.173511830 CPU-s (0.011437087 CPU-h). Đây là thời gian thực đo, khác các dự phóng dưới đây.

| Lưới dự phóng | CPU-s | CPU-h |
|---|---:|---:|
| [1, 3, 10, 30, 100, 300] | 73330.816980909 | 20.369671384 |
| [1, 3, 10, 30, 100] | 65277.821191845 | 18.132728109 |
| [1, 3, 10, 30] | 62472.863216929 | 17.353573116 |
| [1, 3, 10] | 62472.337943018 | 17.353427206 |
| [1, 3] | 62472.337943018 | 17.353427206 |
| [1] | 62472.337943018 | 17.353427206 |

Dự phóng dùng saved prepare timings của từng regime cho V và work proxy (n_A²+n_B²)tau cho joint semigroups, calibration từ 1 pilot nhẹ, cộng 25% reserve và 180 CPU-s. Chi phí joint không mất đi khi chỉ giảm số h; kernel được tái dùng cho các twin/h trong mỗi regime. Joint term còn lại dự phóng 46960.870912 CPU-s. Đây là ước lượng phụ thuộc implementation/proxy, không lower bound về độ khó, không time guarantee và không bằng chứng không thể giải bằng thuật toán rẻ hơn. Một pilot nhẹ có hạn chế; chưa đo case nặng vì luật dừng đã áp dụng.

## Danh sách trước truth và coverage

| Regime | s thật | w* T4 | slope T4 dự đoán | threshold T1/T_int | threshold T2/T_int | h_bar/T_int | status |
|---|---:|---:|---:|---:|---:|---:|---|
| A_u1-2_lA9_x-1_k1-2 | -12.6670091227 | SKIP | n/a | 485.296243 | 922.087791 | 18.0337424 | NOT_RUN_BUDGET |
| A_u1-2_lA9_x1-2_k1-2 | 31.6668354062 | SKIP | n/a | 517.490366 | 983.236935 | 18.0113012 | NOT_RUN_BUDGET |
| A_u1_lA7_x-1-2_k2 | -2.4230609223 | 0.125 | -0.605765230574 | 917.669192 | 4244.99414 | 16.8027836 | NOT_RUN_BUDGET |
| A_u1_lA7_x1_k1-20 | 3.63333470531 | 0.0625 | 0 | 468.185661 | 510.322564 | 18.0413651 | NOT_RUN_BUDGET |
| Za3_u1-2_lA9_x-1_k1-20 | -6.81666675312 | SKIP | n/a | 473.652782 | 484.309976 | 17.9854927 | NOT_RUN_BUDGET |
| Za3_u1-2_lA9_x1-2_k2 | 31.6684821225 | SKIP | n/a | 516.691614 | 981.770349 | 17.9877308 | NOT_RUN_BUDGET |
| Za3_u1_lA7_x-1_k1-20 | -0.852083697492 | 0.25 | -0.213020924373 | 589.547704 | 602.812785 | 18.0401851 | PILOT_COMPLETE |
| Za3_u2_lA13-2_x1-2_k1-2 | 14.9338400857 | SKIP | n/a | 419.8549 | 514.339705 | 18.0225523 | NOT_RUN_BUDGET |
| Za7p5_u1-2_lA17-2_x-2_k1-2 | -5.61546640188 | 0.0625 | -0 | 462.780235 | 1113.74008 | 18.0284563 | NOT_RUN_BUDGET |
| Za7p5_u1_lA8_x1-2_k1-20 | 9.50520935676 | SKIP | n/a | 510.438878 | 582.219408 | 18.0323471 | NOT_RUN_BUDGET |
| Za7p5_u3-2_lA31-4_x-1-6_k2 | -19.1447638489 | SKIP | n/a | 985.009114 | 6527.68854 | 17.8661932 | NOT_RUN_BUDGET |
| Za7p5_u3-2_lA31-4_x1-6_k2 | 40.4916014735 | SKIP | n/a | 790.282655 | 5236.3326 | 17.9327157 | NOT_RUN_BUDGET |

T4: 4 regime hợp lệ, 8 SKIP vì không có w trong tập quy định cho max load < 0.95 mu. Trong 4 regime có 2 mixed-sign và 2 constant-sign strict; không có mode slope bằng 0. Hai slope âm được dự báo trước là -0.605765230574 và -0.213020924373 packet; chỉ slope sau đã có finite-h truth mới. s_hat của T4 là hàm state: CSV ghi min/max, bốn giá trị và posterior ở predictions; không gán scalar threshold M_hat/abs(s_hat) cho T4 mixed-sign.

## Kiểm tra, ngoại lệ và flag

- T0 tái lập G_S tại đủ 7 h đã lưu của pilot: 7/7 PASS, max relative error 4.62292334527e-15 ≤1e−9. 11 regime khác chưa tái lập.
- Independent saved-data audit: 232/232 PASS; không import scorer/engine, không gọi lại V. Kiểm normalization, ngưỡng, slope, Frechet bounds, replay và D2. Không nhận đây là một engine độc lập hay độc lập tính lại real-regime P_dis.
- 8 tests mới PASS: 2D-CDF so với enumerate 4D nhỏ, actual P_dis khác |DeltaF|, wrong-kernel cost semantics, strict cutoff/tie, inequality, nowcast selection, full semigroup marginals, selection 12 regime. Các tests không chứng minh đầy đủ mọi implementation lỗi đều bị loại.
- 0 flag arithmetic mới trên 36 cells. Max stationary residual 1.22124532709e-15. P_dis joint marginal errors và omission ở pilot.log; không suppress negative G_S vì đó là harm được định nghĩa.
- P_dis là số đo deterministic kèm [lower,upper]: bỏ terminal stationary mass ≤1e−10 mỗi path, giữ full Q và mọi old-state row, không renormalize. Khoảng chỉ bao omission, không phải interval-arithmetic certificate cho scipy. Khi marginal bounds đủ hẹp (width≤1e−9), dùng enclosure trực tiếp; không nhận P_dis chính xác bằng 0 khi chỉ nhỏ hơn độ phân giải.
- Chi phí T3 luôn dùng posterior thật exp(Q0*tau); plugin/3tau chỉ đổi kernel chọn action. Tie dùng strict <0 → Stay; không epsilon.
- Rows replay không thuộc lưới h yêu cầu chỉ ghi T0 G_S; P_dis để trống, flag REPLAY_ONLY_NO_PDIS. Không giả 0. Tất cả 36 cells đúng lưới của pilot có P_dis và enclosure.
- Không CI population: đây là finite deterministic CTMC; các h/twin trong cùng regime phụ thuộc nhau. Không suy thực tế/infinite-buffer từ một pilot cắt cụt.

## Phạm vi mệnh đề (P) — không gọi là định lý

1. **Lập luận đủ của (P) đúng cho probability kernel**: nếu |b|≤M thì |E_K b|≤M; h|s_hat|>M ép D_tilde và mọi posterior average cùng dấu. Khi đó hai action trùng nhau ở mọi state, G_S=0. K phải normalized, nonnegative; ‘mọi kernel’ không bao arbitrary linear/signed operator. Bất đẳng thức |G_S|≤P_dis max|V1−V0+c| xuất phát trực tiếp từ cost difference theo disagreement.
2. **Có stationary term không tự đủ cho O(1)**. T4 pilot có term h*s_nc(x), bounded fluid remainder, mixed-sign state slopes và posterior slope negative ở mọi old mode. Pretruth F_new_inf=.75, F_old_inf=1 nên hệ số s*.25 khác 0. P_dis tiến gần .25 và G_S/h tiến gần -0.213020924373 trên lưới thực chạy: counterexample hữu hạn có cơ chế tiệm cận được chỉ rõ cho cách nói quá rộng ‘twin có stationary cost thì O(1)’. Không nhận phép chạy hữu hạn tự nó chứng minh giới hạn. Regime dự báo còn lại chưa có truth.
3. **s_hat=0 không bảo đảm O(1)**: T0 là bounded fluid twin nhưng pretruth s*DeltaF_inf=-0.222286063158 và harm tuyệt đối tăng rõ. Đây là đối chứng bỏ stationary term. Tuy nhiên s_hat khác 0 không phải điều kiện cần cho mọi twin có G_S=O(1): một twin luôn chọn cùng action đã có G_S=0.
4. **Hằng số độc lập state chỉ là điều kiện đủ mạnh**. Nếu s_hat(x) cùng dấu và inf_x|s_hat(x)|=eta>0 thì cutoff h>M/eta cũng cho coincidence. Trên finite support, strict common sign cho eta>0. Sign đổi tự nó cũng chưa bảo đảm slope harm khác 0: còn cần DeltaF_inf khác 0 và s khác 0. Hai constant-sign T4 cases chưa chạy nên không ghi numeric PASS cho nhánh này.
5. **Uniform boundedness b không cần thiết để O(1)**. Trên finite support, b(h,x)=sqrt(h)u(x) là unbounded nhưng o(h), nên common nonzero slope vẫn thắng cuối cùng. Ngược lại, cho phép b=O(h) tùy state có thể tạo mixed-sign effective slope như T4; không thể bỏ toàn bộ kiểm soát relative growth của remainder. Đây là phân tích đại số phạm vi, không một experiment phụ hay giả định mới của letter.
6. **Correct stationary-rate sign không cần cho G_S=0**: hai pipeline có thể cùng chọn action sai và có regret O(h). Nó cần khi yêu cầu long-run action đúng, không cần cho coincidence. Ở 12 regime đã chọn s_MM1 cùng dấu s; panel này không phải phép kiểm wrong-sign rate.
7. **Uniform cutoff và G_S=O(1) khác nhau**: disagreement không cần triệt tiêu để expected G_S bounded. Plug-in stale có cùng switch share với fresh dưới stationary X,Y nên DeltaF=0; finite-state gain–bias cho phần còn lại O(1). Hoặc P_dis=O(1/h) cũng là điều kiện đủ khi max true gap=O(h). Vì vậy một giả định thất bại không đồng nghĩa O(1) thất bại.
8. **M_hat phải thực sự bound remainder**. Prop.2 của letter dùng h>max(h_bar,M_hat/abs(s_hat)), D1 của brief chỉ ghi threshold sau. Ở 12 case này h_bar≈16.8–18.04 T_int thấp hơn mọi threshold, nên không đổi eligibility. Với fluid model cụ thể, từng path gap có dấu cố định và bounded bởi saturated path gap; empty low-mode cho gap 0, nên max network gap saturation bound mọi h. Không suy saturation M_hat là sup cho một twin tổng quát khác.
9. **Giới hạn môi trường**: finite irreducible CTMC/bounded f cho bounded bias và exponentially decaying remainder; đây là lý do true gap có hệ số stationary độc lập initial state. Không suy cùng kết luận cho infinite support hoặc real traces. Phần đại số cutoff của (P) chỉ cần bounded remainder và probability kernel, không cần CTMC.

## Kết luận và phần chưa xác nhận

Đã có kiểm tra hữu hạn rõ về failure mode của state-dependent rate: trên 1 pilot, T4 không loại harm tăng theo horizon, còn T1/T2/T3 gần 0. D2 đúng với tolerance arithmetic trên 12 ô của pilot; T0 tái lập 7/7. D1/D3 chưa có ô trên cutoff và toàn bộ panel chưa chạy. Không đưa dữ liệu này vào paper, không gọi là định lý, không đổi verdict cũ. Không tự chạy thêm theo thẻ hiện tại sau budget stop. Muốn đủ 12 regime cần một lựa chọn kỹ thuật/ngân sách riêng cho joint P_dis; đây chỉ là hướng tiếp theo, chưa triển khai.

## File, commands và provenance

Nguồn mới: `experiments/letter/r2_o1_check.py`; tests mới: `tests/test_r2_o1_check.py`. Không sửa source đã có, không commit/SSH, không sửa state-model-regret-papers/, không ghi vào job p2_tier2.

Commands đã chạy, sau khi source `.venv/bin/activate` và `experiments/explore_ctmc/env.sh`, đặt `PYTHONDONTWRITEBYTECODE=1`:

```text
python3 -m pytest -q -p no:cacheprovider --basetemp results/letter/r2_o1/pytest_tmp tests/test_r2_o1_check.py
python3 -m experiments.letter.r2_o1_check prepare
python3 -m experiments.letter.r2_o1_check pilot
python3 results/letter/r2_o1/analyze_saved.py
```

Không chạy `run` sau STOP_BUDGET. Logs: `tests_pre.log`, `prepare.log`, `pilot.log`, `analysis.log`; command CPU/wall ở `*.time.json`. Raw duy nhất ở `raw/Za3_u1_lA7_x-1_k1-20.json`; số liệu ở `rows.csv`, `summary.json`, `audit.json`, `reproduction.json`; design/predictions ở `predictions_before.json`, resource decision ở `pilot.json`. Không tạo biểu đồ, PDF hay paper artifact.

Brief SHA256 `ad2e2ecbba725ac7cb9fcc4e97ce951ea2d542360c10d82da3515a140040ab7b`; predictions SHA256 `2da6b5f17f19a4a4502098d92c7dd6a14e67ce93b3f650ef957112ccf8adf9cb`; raw SHA256 `c22d5383de13491b7c91cabf6ded7f8e059f8b94183bb848544d5134ccba4fcf`. Source/input hashes khớp audit. Predictions trước finite-h truth, không sửa sau pilot; phạm vi diễn giải/independent audit là post-hoc, không blind forecast mới.

AI (Codex) triển khai, chạy, audit theo brief của Claude và ủy quyền tác giả; không human independent review, không author-self proof. Không literature lookup mới. research-workflow yêu cầu PRINCIPLES.md nhưng file không có trong skill root đã chỉ định; không tạo thay và không dùng để chặn scope được user ủy quyền. Bộ nhớ letter-current-state không có trong local memory roots/tools hiện có; brief và source local được dùng làm context, không tự sửa paper.
